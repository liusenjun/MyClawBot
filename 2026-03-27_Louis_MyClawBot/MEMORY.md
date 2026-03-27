# MEMORY.md — Long-term Memory

---

## 关于 Louis

- **称呼**：Louis
- **GitHub**: liusenjun
- **Discord**: louis_hls
- **时区**：Asia/Shanghai (GMT+8)

---

## 重要项目

### 1min AI Video — BearBug
- GitHub 仓库：https://github.com/liusenjun/1min-AI-video---BearBug
- AI 短片制作项目，展示制作思路
- 风格参考：《宝可梦礼宾部》
- 核心角色：小熊虫（3D 羊毛毡风格）
- 工具链：Gemini（剧本）、nano banana 2.0（角色设计）

---

## 已安装/配置好的工具

- **SenseVoice** — 阿里 FunAudioLLM 中文语音转文字（本地运行）
- **skill-vetter** — Skill 安全审查插件，每次安装 Skill 前必须审查（位于 workspace/skills/skill-vetter/）
- **bot-memory-update** — 记忆同步到 GitHub 的 skill（位于 workspace/skills/bot-memory-update/）
- **Git** — v2.53.0，已安装（2026-03-26）
- **GitHub CLI (gh)** — v2.88.1，已安装，已认证（GH_TOKEN env var）
- **GitHub 推送** — 必须由 Louis 明确触发 skill 或授权后操作，不得擅自 push

### OpenClaw 配置记录
- Discord channel 已加 `"healthMonitor": {"enabled": false}` — 防止 stale-socket 导致 Gateway 崩溃
- 注意：双 node 进程会冲突，重启前需先杀掉旧进程

---

## 约定 & 规则

- 安装任何 Skill 之前，必须先用 skill-vetter 审查
- 下载大文件时：中断超过1小时或多次失败，切换备选方案并通知用户
- workspace 完整备份用 bot-memory-update skill，推送到 https://github.com/liusenjun/MyClawBot

---

## Louis 的偏好/习惯

- 喜欢简洁的结构，不喜欢冗长
- 不喜欢废话，对话直接高效
- 语音输入用中文，清晰有条理
- Discord 是主要沟通渠道

---

## 心得记录

- GPT-5.4 确实存在（2026年发布），首个支持原生计算机操作的通用模型
- nano banana 2.0 是角色设计工具

---

_Last updated: 2026-03-26（下午）_