# MEMORY.md — Long-term Memory

---

## 关于 Louis

- **称呼**：Louis
- **GitHub**: liusenjun
- **Discord**: louis_hls
- **时区**：Asia/Shanghai (GMT+8)

---

## 重要项目

### 人类刹车计划 — AI Video
- 仓库：https://github.com/liusenjun/human-brake-ai-video
- AI 短片（1分钟），风格参考《宝可梦礼宾部》
- 核心角色：小熊虫（3D 羊毛毡风格）
- 工具链：Gemini（剧本）、nano banana 2.0（角色设计）

**当前状态（2026-04-24）：**
- Wan 2.2 I2V ✅ 可用（已下载专用模型）
- LTX 2.3 I2V ❌ 文字编码器全损坏，qBittorrent 文件损坏
- venetanji torrent 下载受阻（models 132.85 GB，文件损坏不匹配）

**GitHub 协作模式（2026-04-23 更新）：**
- 仓库开放给队友为 **collaborator（Write 权限）**，无需 Fork 直接上传
- CONTRIBUTING.md 已改为纯浏览器操作流程（无 Git 命令）
- 公共文件夹结构：`script/`、`workflows/`、`audio/`、`voice/`、`assets/`、`docs/`
- 队友各自文件夹：`louis/`、`huangyishu/`、`jing/`、`leozhu/`

---

## 已安装/配置好的工具

- **SenseVoice** — 阿里 FunAudioLLM 语音转文字，本地运行
  - 模型路径：`C:\Users\user.V915-31\.cache\modelscope\hub\models\iic\SenseVoiceSmall`
  - 加载方式：`model=本地路径, device='cpu', disable_update=True`
  - ffmpeg 路径：`C:\Users\user.V915-31\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin`
- **yt-dlp** — 视频/音频下载（pip install yt-dlp）
- **ffmpeg** — winget 安装，用于音频解码
- **skill-vetter** — Skill 安全审查插件，每次安装 Skill 前必须审查（位于 workspace/skills/skill-vetter/）
- **bot-memory-update** — 记忆同步到 GitHub 的 skill（位于 workspace/skills/bot-memory-update/）
- **Git** — v2.53.0，已安装（2026-03-26）
- **GitHub CLI (gh)** — v2.88.1，已安装，已认证（GH_TOKEN env var）

### OpenClaw 配置记录
- Discord channel 已加 `"healthMonitor": {"enabled": false}` — 防止 stale-socket 导致 Gateway 崩溃
- 注意：双 node 进程会冲突，重启前需先杀掉旧进程

---

## 约定 & 规则

- 安装任何 Skill 之前，必须先用 skill-vetter 审查
- 下载大文件时：中断超过1小时或多次失败，切换备选方案并通知用户
- workspace 完整备份用 bot-memory-update skill，推送到 https://github.com/liusenjun/MyClawBot
- **GitHub 推送必须由 Louis 明确触发 skill 或授权后操作，不得擅自 push**

---

## Louis 的偏好/习惯

- 喜欢简洁的结构，不喜欢冗长
- 不喜欢废话，对话直接高效
- 语音输入用中文，清晰有条理
- Discord 是主要沟通渠道

---

## ComfyUI Video Gen 工具

- ComfyUI 端口：8188
- ComfyUI 源码：`C:\Users\user.V915-31\Documents\comfyui-git\`
- 模型路径：`C:\Users\user.V915-31\Documents\ComfyUI\models\`
- 输出路径：`C:\Users\user.V915-31\Documents\ComfyUI\output\`
- comfyui skill 脚本：`C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts\`

**三模型状态（2026-04-21）：**

| 模型 | 状态 | 说明 |
|------|------|------|
| Wan 2.2 | ✅ 可用 | I2V 专用模型已下载（wan2.2_ti2v_5B_fp16 + wan2.2_vae） |
| HunyuanVideo | ⚠️ T2V only | 只有 T2V 模型，无 I2V 专用模型 |
| LTX 2.3 | ❌ 损坏 | 文字编码器全部故障 |

**Wan 2.2 I2V 正确节点链：**
- `WanFirstLastFrameToVideo`（不是 WanImageToVideo）
- CLIPLoader + VAELoader + KSampler + VAEDecode + CreateVideo

**LTX 2.3 文字编码器状态：**
- Gemma `gemma_3_12B_it_fp8_e4m3fn.safetensors` — corrupted sparse file
- UMT5 `umt5_xxl_fp8_e4m3fn_scaled.safetensors` — meta tensor error
- Qwen 3B `qwen_3_4b.safetensors` — wrong tokenizer

---

## venetanji/ltx2-comfy-v915 分析

- Repo：`C:\Users\user.V915-31\Documents\ltx2-comfy-v915\`
- GGUF I2V workflow：`workflows/gguf_i2v.json`
- 关键依赖（全部在 torrent 里，不在 HuggingFace）：
  - `ltx-2.3-22b-dev-Q4_K_M.gguf` (13.34 GB)
  - `gemma_3_12B_it_fp4_mixed.safetensors` (8.80 GB)
  - `ltx-2.3-22b-dev_video_vae.safetensors` (2.28 GB)
  - `ltx-2.3_text_projection_bf16.safetensors` (2.15 GB)

**models torrent（132.85 GB）状态：**
- 全部 26 个文件都在，但大部分大小不匹配（qBittorrent fastresume 损坏）
- 唯一正确的 3 个文件：ltx-2-19b-distilled_Q4_K_M.gguf、ltx-2.3-22b-distilled-lora-384、ltx-2-19b-ic-lora-detailer
- qBittorrent WebUI 完全无法启动（Windows 版 5.1.4 兼容问题，端口 8080 不监听）

---

## 2026-04-23 项目进展

### Repo 大重构完成
- 仓库名从 `1min-AI-video---BearBug` 改为公开展示名 `human-brake-ai-video`
- 完全重组文件夹结构：per-member 文件夹 + 共享文件夹
- 黄奕舒 + 辛怡静的素材包已分析：HunyuanVideo 1.5 I2V workflow、SD v1.5 reference images、Suno music（3 tracks）、56 video clips、2 段完成视频
- 已上传：角色三视图 × 5、摩托车 asset、Act 1 workflow 截图 × 3、Discord 协作截图 × 1

### README 重写完成
- About：3段式简介（项目介绍 → 故事梗概 → 协作模式）
- Story Structure：4 Acts 表格
- Team：4人 + AI Agent
- How We Work：Pipeline → Division of Labour → Per-act breakdown
- AI Collaboration：OpenClaw 小志担任技术搭档

### CONTRIBUTING.md 简化
- 移除 Fork + PR 流程
- 改为直接上传：注册 → 接受邀请 → 进仓库 → 进自己文件夹 → 上传 → Commit done
- 队友不需要安装任何软件或输入命令，纯浏览器操作

---

## 心得记录

- B站字幕：原字幕接口返回404时，可用 yt-dlp 下载音频 + SenseVoice 转写作为备选方案
- yt-dlp 下载 B站音频：yt-dlp -f "30280" --audio-format wav -o "output.wav" "视频URL"
- qBittorrent fastresume 缓存损坏会导致文件大小不匹配但无法自动修复
- ComfyUI object_info API：`http://localhost:8188/object_info/{NodeType}`
- ComfyUI models API：`http://localhost:8188/api/models/{category}`

---

_Last updated: 2026-04-24_
