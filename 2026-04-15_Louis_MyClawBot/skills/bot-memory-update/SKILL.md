---
name: bot-memory-update
description: Backup or sync OpenClaw workspace to GitHub for cross-machine continuity. Use when user asks to "backup workspace", "sync workspace to GitHub", "save workspace", "update memory", "sync memory", "push workspace to repo", "备份记忆", "同步记忆到 GitHub", "把工作区存到仓库", "把记忆更新进 GitHub", or similar phrases in any language. Creates a timestamped backup folder inside the existing repo (never replaces repo content). Requires GitHub CLI (gh) to be installed and authenticated. Reads username dynamically from USER.md for folder naming.
---

# Bot Memory Update

Sync OpenClaw workspace to a GitHub repository as a timestamped backup folder — like a system image backup. Each backup is a snapshot; no history is ever overwritten.

## Core Logic

```
IF repo does not exist:
    → Create new private repo (one-time)
    → Prepare first backup folder
    → Push as new repo

IF repo exists:
    → ALWAYS create a new dated folder (never overwrite existing backups)
    → Push to GitHub
    → Report result
```

**Key principle: Every backup is a new folder. Old backups are never modified or deleted.**

## Backup Structure

```
MyClawBot/
├── 2026-03-25_Louis_MyClawBot/   ← previous backup (kept intact)
├── 2026-03-26_Louis_MyClawBot/   ← new backup (added, not replacing)
└── ...
```

## Files to Backup

| Path | Purpose |
|------|---------|
| `MEMORY.md` | Long-term memory |
| `memory/YYYY-MM-DD.md` | Daily logs |
| `USER.md` | User information |
| `SOUL.md` | Soul/personality |
| `AGENTS.md` | Agent work rules |
| `TOOLS.md` | Tools configuration |
| `IDENTITY.md` | Identity settings |
| `HEARTBEAT.md` | Heartbeat tasks |
| `skills/` | **ALL** skills in this folder |
| `agents/` | Sub-agents (e.g. Elias 6092g) — identity, soul, rules |
| `memory/` | Daily logs (YYYY-MM-DD.md) |

**Important:** Upload entire `skills/` folder contents, not just specific skills.

## Workflow

### Step 1: Check gh Authentication

```bash
gh auth status
```

If not logged in → use `GH_TOKEN` env var or run `gh auth login`.

### Step 2: Get username from USER.md

```bash
# Read username from USER.md dynamically
```

### Step 3: Prepare Backup Folder Name

Format: `YYYY-MM-DD_[Username]_MyClawBot`

Example: `2026-03-26_Louis_MyClawBot`

### Step 4: Clone Existing Repo (preserves all history)

```bash
git clone https://github.com/<username>/<repo-name>.git /tmp/bot-repo
```

**Important:** Always clone first. Never `git init` in a backup folder — that creates a brand new repo and destroys remote history when pushed.

### Step 5: Copy Workspace Files into Backup Folder

```bash
# Create dated backup folder inside the cloned repo
mkdir -p /tmp/bot-repo/<YYYY-MM-DD>_Username_MyClawBot

# Copy all workspace files
cp MEMORY.md /tmp/bot-repo/<backup-folder>/
cp USER.md /tmp/bot-repo/<backup-folder>/
cp SOUL.md /tmp/bot-repo/<backup-folder>/
cp AGENTS.md /tmp/bot-repo/<backup-folder>/
cp TOOLS.md /tmp/bot-repo/<backup-folder>/
cp IDENTITY.md /tmp/bot-repo/<backup-folder>/
cp HEARTBEAT.md /tmp/bot-repo/<backup-folder>/
cp -r memory/ /tmp/bot-repo/<backup-folder>/
cp -r skills/ /tmp/bot-repo/<backup-folder>/
cp -r agents/ /tmp/bot-repo/<backup-folder>/
```

### Step 6: Commit and Push

```bash
cd /tmp/bot-repo
git add .
git commit -m "Backup <YYYY-MM-DD>"
git push
```

**No `--force`. No `git init`. Just add → commit → push to the existing repo.**

### Step 7: Cleanup

```bash
Remove-Item -Recurse -Force /tmp/bot-repo
```

### Step 8: Report Result

**发送消息给用户，包含以下信息：**
- ✅ Backup complete
- 📦 Files backed up: [count]
- 🔗 Repo URL: `https://github.com/<username>/<repo-name>`
- 📁 Backup folder: [folder name]

**重要：必须主动发送 Repo URL，让用户可以直接点击检查。**

---

## Folder Naming Convention

Format: `YYYY-MM-DD_[Username]_MyClawBot`

Examples:
- `2026-03-23_Louis_MyClawBot`
- `2026-03-26_Louis_MyClawBot`

---

## Error Handling

| Error | Solution |
|-------|----------|
| `gh: command not found` | Install GitHub CLI first |
| `gh auth not logged in` | Use `GH_TOKEN` env var or `gh auth login` |
| Repo not found | Create it with `gh repo create` first |
| Clone fails (empty repo) | Create initial backup without clone step |
| Push conflicts | Pull first (`git pull`), then push |

---

## Common Mistakes to Avoid

1. **Never `git init` in a backup folder** — this creates a new repo and destroys remote history when pushed with `--force`
2. **Never `git push --force`** — force push overwrites the entire remote repo
3. **Always clone the existing repo first** — work within the existing repo's git history
4. **Always create a new folder** — never modify existing backup folders

---

*This skill ensures your agent never loses memory between sessions or machines.* 🧠💾
