---
name: bot-memory-update
description: Backup or sync OpenClaw workspace to GitHub for cross-machine continuity. Use when user asks to "backup workspace", "sync workspace to GitHub", "save workspace", "update memory", "sync memory", "push workspace to repo", "备份记忆", "同步记忆到 GitHub", "把工作区存到仓库", "把记忆更新进 GitHub", or similar phrases in any language. Handles updating an existing backup or creating a new backup folder. Requires GitHub CLI (gh) to be installed and authenticated. Reads username dynamically from USER.md for folder naming.
---

# Bot Memory Update

Sync OpenClaw workspace to a private GitHub repository for cross-machine continuity.

## Core Logic

```
IF repo does not exist:
    → Create new private repo (one-time)
    → Ask user to choose: Overwrite vs New folder

IF repo exists AND existing folders > 0:
    → IF user says "keep history" / "new folder" / "don't overwrite":
        → Create new dated folder
    → ELSE:
        → Auto Overwrite (no asking)

IF repo exists AND no existing folders:
    → Ask user to choose: Overwrite vs New folder

COMMIT:
    → Push files to GitHub
    → Share repo URL with user
```

## Decision Flow

```
┌─────────────────────────────────────┐
│  Check if repo exists on GitHub      │
└─────────────────┬───────────────────┘
                  │
       ┌──────────┴──────────┐
       ↓                      ↓
    Repo exists?          Repo not found
       │                      │
       ↓                      ↓
   Check existing        Create repo (one-time)
   folder count             ↓
       │                Ask mode
       ↓                (skip to push)
   Folders > 0?             ↓
   │                       Push
 ┌─┴──────────────────────┐  ↓
 ↓                         ↓
User says           Auto Overwrite
"keep history"?          (no ask)
 ↓                         ↓
Create new            Push to GitHub
folder                    ↓
 ↓                      Share URL ✅
Push
 ↓
Share URL ✅
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

**Important:** Upload entire `skills/` folder contents, not just specific skills. This ensures any newly installed skills are included in the backup.

## Workflow

### Step 1: Check GitHub CLI Status

```bash
gh auth status
```

If not logged in:
```bash
gh auth login --hostname github.com --git-protocol https
```

### Step 2: Check If Repo Exists

```bash
gh repo list <username> --json name --jq '.[].name'
```

If repo **does not exist** → Create it (Step 3)
If repo **exists** → Check existing folder name (Step 4)

### Step 3: Create Repo (One-time Only)

```bash
gh repo create <repo-name> --private --description "<description>"
```

Example:
```bash
gh repo create MyClawBot --private --description "OpenClaw workspace sync"
```

### Step 4: Check Existing Folders & Decide Mode

Check existing folders:
```bash
git ls-tree -r HEAD --name-only | grep -E '^[^/]+/$' | head -5
```

**Decision logic:**

```
IF existing folders > 0:
    → IF user says "don't overwrite", "keep history", "new folder":
        → Create new dated folder (v2, v3...)
        → Tell user: "Creating new backup, keeping history"
    → ELSE:
        → Auto Overwrite (replace oldest folder)
        → Tell user: "Auto-overwriting to keep repo clean"
    
IF no existing folders:
    → Ask user to choose mode (Overwrite vs New)
```

---

### Step 5: Prepare Backup Folder

**Overwrite mode:**
```bash
# Get current folder name, then rename to today's date
# e.g., "OldFolder" → "2026-03-23_Louis_MyClawBot"

rm -rf /tmp/bot-backup
mkdir -p /tmp/bot-backup/<NEW_FOLDER_NAME>
cd /tmp/bot-backup/<NEW_FOLDER_NAME>
```

**New folder mode (keep history):**
```bash
mkdir -p /tmp/bot-backup/<YYYY-MM-DD>_[Username]_MyClawBot
cd /tmp/bot-backup/<YYYY-MM-DD>_[Username]_MyClawBot
```

Note: Previous backup is kept intact as a separate folder.

### Step 6: Copy Workspace Files

**CRITICAL: Copy ALL files from workspace root to backup folder:**
- All .md files (MEMORY.md, USER.md, SOUL.md, AGENTS.md, TOOLS.md, IDENTITY.md, HEARTBEAT.md)
- The entire memory/ folder (all daily logs)
- The entire skills/ folder (all installed skills)

### Step 7: Push to GitHub

```bash
git init
git add .
git commit -m "Workspace backup $(date -u +'%Y-%m-%d')"
git branch -M main
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main --force
```

### Step 8: Share Result

Tell user:
- ✅ Backup complete
- 📦 Files backed up: [count]
- 🔗 Repo URL: [url]
- 📁 Folder: [folder name]

---

## Folder Naming Convention

Format: `YYYY-MM-DD_[Username]_MyClawBot`

Examples:
- `2026-03-23_Louis_MyClawBot`
- `2026-03-25_Louis_MyClawBot_v2`

---

## Error Handling

| Error | Solution |
|-------|----------|
| `gh: command not found` | Install GitHub CLI first |
| `gh auth not logged in` | Run `gh auth login` |
| Repo not found | Create it with `gh repo create` |
| Push rejected | Check if repo is empty, use `--force` |
| Large files | `.gitignore` large media files |

---

*This skill ensures your agent never loses memory between sessions or machines.* 🧠💾
