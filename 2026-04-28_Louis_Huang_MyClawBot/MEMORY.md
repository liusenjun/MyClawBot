# MEMORY.md — Long-term Memory

---

## 关于 Louis

- **称呼**：Louis
- **显示名**：Louis_Huang
- **GitHub**: liusenjun
- **Discord**: louis_hls
- **Discord ID**: 1480802010637795460
- **时区**：Asia/Shanghai (GMT+8)

---

## 部署环境

- **当前状态（2026-04-27）：** 部署在 Louis 的 Windows 电脑的 WSL2（Linux 子系统）下
- **WSL 挂载点：** Windows C: 盘 → `/mnt/c/`
- **路径对应示例：** `C:\Users\louis\...` = `/mnt/c/Users/louis/...`
- **OpenClaw 版本：** 2026.4.24
- **模型：** MiniMax-M2.7-highspeed（已切换高速版）

---

## 重要项目

### 人类刹车计划 — AI Video
- 仓库：https://github.com/liusenjun/human-brake-ai-video
- AI 短片（1分钟），风格参考《宝可梦礼宾部》
- 核心角色：小熊虫（3D 羊毛毡风格）
- 工具链：Gemini（剧本）、nano banana 2.0（角色设计）

**当前状态（2026-04-24）：**
- ✅ 第一阶段流程已告一段落
- ✅ 成品视频已完成（Final Output.mp4，154.8 MB）
- ✅ GitHub repo 搭建完成，队友已开始上传素材
- ⚠️ 成品视频因商业项目无法公开，README 标注为"Coming soon"
- ⚠️ 计划上传 B站 作为视频托管，链接嵌入 README（待 Louis 上传后更新）
- Wan 2.2 I2V ✅ 可用（已下载专用模型）
- LTX 2.3 I2V ❌ 文字编码器全损坏，qBittorrent 文件损坏

**GitHub 仓库内容（2026-04-24）：**
- `docs/`：Act 1 workflow 截图 × 3、Discord 协作截图 × 1
- `assets/`：角色三视图 × 5、摩托车 asset、海报占位符
- `huangyishu/`：Act 2-3 分镜图（已上传）
- `jing/`：Act 2-3 分镜图（已上传）
- `voice/`：4个音轨文件（Durian Drop、Neon Apex Run、Neon Pursuit、Untitled）
- `workflows/`：HunyuanVideo 1.5 I2V workflow
- `script/`：剧本

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

---

## 2026-04-24 项目阶段完成

### 重要里程碑
- **成品视频完成**：`Final Output.mp4`（154.8 MB）存放于 Louis 本地
- **GitHub repo 公开**：https://github.com/liusenjun/human-brake-ai-video
- **README 最终状态**：
  - Demo video 标注为"temporarily unavailable — commercial project"
  - 海报（poster）作为公开参考
  - B站视频链接待上传后嵌入

### 队友贡献已收录
- 黄奕舒：Act 2-3 分镜图已上传到 `huangyishu/`
- 辛怡静：Act 2-3 分镜图 + voice 音轨已上传
- 工作流：HunyuanVideo 1.5 I2V workflow 已收录

### 下次继续
- B站视频上传后，更新 README 中的视频链接
- 等朱智立上传 Act 4 素材
- 项目后续阶段（配音、剪辑）时间待定
