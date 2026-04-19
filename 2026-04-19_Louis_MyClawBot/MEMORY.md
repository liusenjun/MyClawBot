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
- 仓库：https://github.com/liusenjun/1min-AI-video---BearBug
- AI 短片（1分钟），风格参考《宝可梦礼宾部》
- 核心角色：小熊虫（3D 羊毛毡风格）
- 工具链：Gemini（剧本）、nano banana 2.0（角色设计）
- **当前状态**：Shot 4 视频生成中（Wan 2.2 vs HunyuanVideo vs LTX 2.3 三模型对比）
- Storyboard v2：19个镜头，英文 prompts，全8维度字段
- 参考图：`story/robin/refs/hostess_three_views.png`（Louis 提供）、`robin_three_views.png`、`motorcycle.png`

---

## 已安装/配置好的工具

- **SenseVoice** — 阿里 FunAudioLLM 语音转文字，本地运行
  - 模型路径：`C:\Users\user.V915-31\.cache\modelscope\hub\models\iic\SenseVoiceSmall`
  - 加载方式：`model=本地路径, device='cpu', disable_update=True`
  - ffmpeg 路径：`C:\Users\user.V915-31\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin`
  - **注意**：ffmpeg 刚装完 PATH 未刷新，加载模型时需手动设置 PATH 环境变量
- **yt-dlp** — 视频/音频下载（pip install yt-dlp）
- **ffmpeg** — winget 安装，用于音频解码
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

- B站字幕：原字幕接口返回404时，可用 yt-dlp 下载音频 + SenseVoice 转写作为备选方案
- yt-dlp 下载 B站音频：yt-dlp -f "30280" --audio-format wav -o "output.wav" "视频URL"

- GPT-5.4 确实存在（2026年发布），首个支持原生计算机操作的通用模型
- nano banana 2.0 是角色设计工具

### ComfyUI — Video Gen 工具
- ComfyUI 进程：PID 3248，端口 8188
- 模型路径：`C:\Users\user.V915-31\Documents\ComfyUI\models\`
- 输出路径：`C:\Users\user.V915-31\Documents\ComfyUI\output\`
- ComfyUI 源码：`C:\Users\user.V915-31\Documents\comfyui-git\`
- **OpenClaw comfyui skill 脚本路径**：`C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts\`

**三模型状态：**
| 模型 | 状态 | 说明 |
|------|------|------|
| Wan 2.2 | ✅ 正常 | `wan2.2_t2v_high/low_noise_14B_fp8_scaled.safetensors`，1280×720，121帧，8步 |
| HunyuanVideo | ✅ 可用 | `CLIPLoader(umt5_xxl, type='sd3')` + `CLIPTextEncode` 可替代 `CLIPTextEncodeHunyuanDiT` |
| LTX 2.3 | ❌ VAE损坏 | `LTX2_video_vae_bf16.safetensors` 全零文件，需重新下载 |

**Wan 2.2 验证参数**（1280×720，5秒，seed=42）：
- High-noise UNet（步0→4）→ Low-noise UNet（步4→8），Euler，CFG=1.0
- Negative: "blurry, low quality, watermark, distorted, still frame, static, flickering"

**HunyuanVideo 工作流**（替代方案）：
- `CLIPLoader(umt5_xxl, type='sd3')` → `CLIPTextEncode`（不能用 HunyuanDiT）
- `EmptyHunyuanLatentVideo` → `KSamplerAdvanced` → `VAEDecode` → `VHS_VideoCombine`
- 注意：`VAEDecode` 输出是 IMAGE，不能接 `SaveVideo`，必须用 `VHS_VideoCombine`

### 2026-04-11 更新
- **Elias 角色 Agent**：Louis 选了 6092g-Elias（38岁前皇家法师），成功 spawn，用 relay 方式通信
- **Discord pairing**：Louis 的 Discord 需要配对，用 `openclaw pairing approve discord 5U83Q3UZ` 解决
- **图片理解**：MiniMax API 不支持图片输入（Anthropic 兼容接口限制），需要问 MiniMax 客服
- **MiniMax Starter 套餐**：￥29/月，600次调用/5小时，支持图像理解和联网搜索 MCP，但 OpenClaw 未配置 MCP
- **额度注意**：5小时/月额度很少，注意不要过度使用

---

_Last updated: 2026-04-14_
