# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Skill 安装规则

**每次安装任何 Skill 之前，必须先用 skill-vetter 审查一遍！**

审查步骤：
1. 运行 skill-vetter 的 vetting protocol
2. 读取目标 Skill 的所有文件
3. 检查 RED FLAGS（见 skill-vetter/SKILL.md）
4. 生成 SKILL VETTING REPORT
5. 根据风险等级决定是否继续安装

**风险等级处理方式：**
- 🟢 LOW → 可直接安装
- 🟡 MEDIUM → 完整代码审查后安装
- 🔴 HIGH → 必须你确认才能装
- ⛔ EXTREME → 拒绝安装

---

Add whatever helps you do your job. This is your cheat sheet.
