#!/usr/bin/env python3
"""
Secret Scanner for bot-memory-update

Scans files for sensitive data (API keys, tokens, passwords, private keys)
BEFORE they are uploaded to a public repository.

Usage:
    python scan_secrets.py <path_to_scan> [--fix]
    
    --fix  : Redact found secrets (creates .redacted files, does NOT modify originals)
"""

import os
import re
import json
import argparse
import sys
from pathlib import Path
from typing import NamedTuple

# Try to enable ANSI colors on Windows
try:
    import fcntl, termios
except ImportError:
    pass
else:
    pass

try:
    if sys.platform == 'win32':
        os.system('')  # Enable ANSI on Windows Console
except:
    pass

class SecretMatch(NamedTuple):
    file: str
    line_number: int
    line_content: str
    pattern_name: str
    redacted_content: str

# High-confidence patterns: anything that looks like an actual key/token
HIGH_CONFIDENCE_PATTERNS = [
    # GitHub tokens
    (r'ghp_[a-zA-Z0-9]{36}',           'GitHub Personal Access Token (classic)'),
    (r'github_pat_[a-zA-Z0-9_]{22,}',  'GitHub Fine-grained PAT'),
    (r'gho_[a-zA-Z0-9]{36}',           'GitHub OAuth Token'),
    (r'ghu_[a-zA-Z0-9]{36}',           'GitHub User Access Token'),
    (r'ghs_[a-zA-Z0-9]{36}',           'GitHub Server Access Token'),
    
    # HuggingFace
    (r'hf_[a-zA-Z0-9]{34,}',           'HuggingFace Token'),
    (r' hf_[a-zA-Z0-9]{20,}',          'HuggingFace Token (with space prefix)'),
    
    # OpenAI / Anthropic / Google
    (r'sk-[a-zA-Z0-9]{20,}',           'OpenAI API Key'),
    (r'sk-ant-[a-zA-Z0-9]{48}',        'Anthropic API Key'),
    (r'AIza[a-zA-Z0-9_-]{35}',         'Google API Key'),
    
    # AWS
    (r'AKIA[A-Z0-9]{16}',              'AWS Access Key ID'),
    (r'ASIA[A-Z0-9]{16}',               'AWS Session Token'),
    
    # Database / generic
    (r'postgres(ql)?://[^\s:]+:[^\s@]+@', 'Database Connection String (with password)'),
    (r'mongodb\+srv://[^\s:]+:[^\s@]+@',  'MongoDB Connection String (with password)'),
    (r'redis://[^\s:]+:[^\s@]+@',          'Redis Connection String (with password)'),
    
    # Private keys
    (r'-----BEGIN (RSA |EC |OPENSSH |DSA |PGP |PRIVATE KEY)-----', 'Private Key Header'),
    (r'-----BEGIN OPENPGP PRIVATE KEY BLOCK-----',                  'PGP Private Key'),
    
    # Misc services
    (r'sl?sk_[a-zA-Z0-9]{20,}',        'Slack Token'),
    (r'[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_-]{25,}', 'Discord Bot/User Token'),
    (r'[A-Za-z0-9]{40}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_-]{27,}', 'Discord Token'),
    (r'xox[baprs]-[a-zA-Z0-9]{10,}',   'Discord/Slack Token'),
    (r'telegram[_-]?bot[a-zA-Z0-9_:+/-]{10,}', 'Telegram Bot Token'),
    (r'meow_[a-zA-Z0-9]{20,}',         'Cloudflare API Token'),
    (r'Bearer [a-zA-Z0-9_.-]{20,}',    'Bearer Token (HTTP Auth)'),
    (r'Authorization:\s*[a-zA-Z0-9_.-]{20,}', 'Authorization Header'),
]

# Medium-confidence patterns: things that might be real but could be placeholders
MEDIUM_CONFIDENCE_PATTERNS = [
    (r'["\']?(api[_-]?key|apikey|secret|token|password|passwd|pwd|private[_-]?key)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_.-]{20,}["\']',
     'Named Secret (api_key / secret / token field)'),
    (r'(GH_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|HF_TOKEN|AWS_SECRET|STRIPE_SECRET)[_0-9]*\s*=\s*["\'][a-zA-Z0-9_.-]{20,}["\']',
     'Environment Variable containing Secret'),
]

ALL_PATTERNS = [(p, n, 'HIGH') for p, n in HIGH_CONFIDENCE_PATTERNS] + \
               [(p, n, 'MED') for p, n in MEDIUM_CONFIDENCE_PATTERNS]

# File extensions to scan (text-based files)
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.mjs', '.cjs', '.sh', '.bash', '.ps1',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
    '.md', '.txt', '.env', '.gitignore', '.npmrc', '.pypirc',
    '.html', '.css', '.xml', '.sql', '.go', '.rs', '.rb', '.java',
    '.kt', '.swift', '.php', '.pl', '.r', '.lua', '.nix',
}

# Directories to always skip
SKIP_DIRS = {
    '.git', '__pycache__', '.venv', 'venv', 'node_modules',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', 'out',
    '.tox', '.eggs', '*.egg-info', '.sass-cache', '.next',
    '.nuxt', '.cache', '.temp', 'tmp', 'temp',
}

# Files to always skip (binary or generated)
SKIP_FILES = {
    '.gitignore',  # .gitignore often contains fake/example patterns
    'scan_secrets.py',  # Scanner's own code contains pattern strings that look like secrets
    'SKILL.md',  # SKILL.md documents secret patterns as examples, not real secrets
}


def redact_match(text: str, pattern: str) -> str:
    """Redact the matched secret portion with asterisks."""
    def replacer(m):
        secret = m.group(0)
        prefix_len = min(4, len(secret) // 4)
        suffix_len = min(4, len(secret) // 4)
        return secret[:prefix_len] + '*' * (len(secret) - prefix_len - suffix_len) + secret[-suffix_len:]
    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)


def should_scan_file(path: Path) -> bool:
    """Check if a file should be scanned."""
    name = path.name
    suffix = path.suffix.lower()
    
    # Skip skip dirs
    for parent in path.parts:
        if parent in SKIP_DIRS or any(parent.startswith(s.rstrip('*')) for s in SKIP_DIRS if s.endswith('*')):
            return False
    
    # Skip files in SKIP_FILES (but not .gitignore - we scan it for real tokens)
    if name in SKIP_FILES and name != '.gitignore':
        return False
    
    # Skip non-text files (binary)
    if suffix and suffix not in TEXT_EXTENSIONS:
        return False
    
    # Skip files > 10MB
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            return False
    except OSError:
        return False
    
    return True


def scan_file(path: Path) -> list[SecretMatch]:
    """Scan a single file for secrets. Returns list of matches."""
    matches = []
    
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line_no, line in enumerate(f, 1):
                # Skip obviously redacted lines
                if '***' in line or 'REDACTED' in line.upper():
                    continue
                
                for pattern, name, confidence in ALL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        redacted = redact_match(line.rstrip(), pattern)
                        matches.append(SecretMatch(
                            file=str(path),
                            line_number=line_no,
                            line_content=line.rstrip(),
                            pattern_name=name,
                            redacted_content=redacted,
                        ))
                        break  # Only report once per line per pattern group
    except (OSError, IOError):
        pass
    
    return matches


def scan_directory(root_path: str | Path) -> list[SecretMatch]:
    """Recursively scan a directory for secrets."""
    root = Path(root_path)
    all_matches = []
    
    for path in root.rglob('*'):
        if path.is_file() and should_scan_file(path):
            matches = scan_file(path)
            all_matches.extend(matches)
    
    return all_matches


def print_report(matches: list[SecretMatch], root_path: str | Path):
    """Print a human-readable report."""
    if not matches:
        print(f"\n[PASS] No secrets detected in {root_path}")
        return
    
    root = Path(root_path)
    
    # Group by file
    by_file: dict[str, list[SecretMatch]] = {}
    for m in matches:
        rel = str(Path(m.file).resolve().relative_to(root.resolve()))
        by_file.setdefault(rel, []).append(m)
    
    print(f"\n[!] WARNING: {len(matches)} secret(s) detected in {root_path}")
    print("=" * 80)
    print("Files containing secrets:")
    print()
    
    for file_rel, file_matches in sorted(by_file.items()):
        print(f"[FILE] {file_rel}")
        for m in file_matches:
            print(f"   Line {m.line_number} | {m.pattern_name}")
            print(f"   >> {m.redacted_content}")
            print()
    
    print("=" * 80)
    print(f"Total: {len(matches)} secret(s) across {len(by_file)} file(s)")
    print()
    print("REMEDIATION STEPS:")
    print("  1. Move secrets to environment variables (not in code)")
    print("  2. Use a secrets manager (e.g., .env files with .gitignore)")
    print("  3. Delete / rotate any tokens that were already committed")
    print("  4. Re-run this scan after cleaning up")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Scan workspace files for secrets before uploading to GitHub.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scan_secrets.py C:\\Users\\user\\.openclaw\\workspace
  python scan_secrets.py . --fix
        """
    )
    parser.add_argument('path', nargs='?', default='.', help='Path to scan (default: current directory)')
    parser.add_argument('--fix', action='store_true', help='Create redacted copies of files containing secrets')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output detected secrets (no warnings)')
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    
    matches = scan_directory(path)
    
    if args.json:
        output = {
            'path': str(path),
            'total_matches': len(matches),
            'files_with_secrets': len(set(m.file for m in matches)),
            'matches': [
                {
                    'file': m.file,
                    'line_number': m.line_number,
                    'pattern_name': m.pattern_name,
                    'redacted_content': m.redacted_content,
                }
                for m in matches
            ]
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    if args.quiet:
        for m in matches:
            print(f"{m.file}:{m.line_number} | {m.pattern_name}")
        return
    
    print_report(matches, path)
    
    if args.fix:
        print("Creating redacted copies...")
        root = path
        by_file: dict[str, list[SecretMatch]] = {}
        for m in matches:
            rel = str(Path(m.file).resolve().relative_to(root.resolve()))
            by_file.setdefault(rel, []).append(m)
        
        for file_rel, file_matches in sorted(by_file.items()):
            src = root / file_rel
            dst = root / f"{file_rel}.redacted"
            with open(src, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            for m in sorted(file_matches, key=lambda x: x.line_number, reverse=True):
                content_lines = content.split('\n')
                if m.line_number - 1 < len(content_lines):
                    content_lines[m.line_number - 1] = m.redacted_content
                    content = '\n'.join(content_lines)
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Created redacted: {file_rel}.redacted")
        
        print(f"\nOriginal files are UNCHANGED. Review the .redacted files and copy changes manually.")
    
    # Exit code: 0 = clean, 1 = secrets found
    sys.exit(1 if matches else 0)


if __name__ == '__main__':
    main()
