# Shot 1 — 测试用例

**项目：** 人类刹车计划 · 第一幕「深水埗暗线」  
**镜头：** Shot 1 (00:00–00:08) · 全景固定 · 室外茶餐厅街景  
**模型：** Wan 2.2 Image-to-Video  
**更新日期：** 2026-04-21

---

## 输入

| 项目 | 内容 |
|------|------|
| **输入图片** | `C:\Users\user.V915-31\Documents\ComfyUI\input\SHOT\shot1.png` |
| **剧本描述** | 香港深水埗深夜街景，霓虹闪烁，茶餐厅暖灯 |
| **景别** | 全景（Wide / Full View） |
| **运镜** | 固定机位（Fixed Static Camera）|

---

## Positive Prompt

```
固定镜头，香港深水埗街道夜景。摄像机静止，街道上行人自然行走。

画面中心：恒香茶餐厅（黄色招牌，写着"since 1968"），暖黄色灯光从店内溢出。

周围：彩色繁体中文霓虹灯招牌（南昌大药房、老记烧腊、福华街鞋铺），红、蓝、绿光交织。

色调：冷暖对比，电影感，霓虹灯在潮湿街道上反射。

左侧：一名男子推着货物推车经过。右侧：停放的汽车。街上行人三三两两正常行走。

氛围：港式都市烟火气，怀旧，繁华热闹的夜晚街道。固定镜头，自然光线流动。
```

## Negative Prompt

```
blurry, low quality, watermark, distorted, still frame, static, flickering, noisy, grainy, washed out, cartoon, anime, day time, bright, crowd, camera shake, pan, tilt, zoom
```

---

## 关键参数

| 参数 | 值 |
|------|-----|
| 分辨率 | 1024 × 576（16:9） |
| 帧数 | 201 帧 |
| 时长 | 8秒 @ 24fps |
| VAE | `wan2.2_vae.safetensors` |
| I2V UNet | `wan2.2_ti2v_5B_fp16.safetensors` |
| CLIP | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` |
| 采样器 | Euler |
| 步数 | 25 |
| CFG | 1.0 |

---

## Workflow 节点链（ Wan22ImageToVideoLatent）

```
LoadImage(SHOT/shot1.png)
    ↓
CLIPLoader(umt5_xxl_fp8_e4m3fn_scaled.safetensors, type="wan")
    ↓
CLIPTextEncode(positive prompt) ──→ KSampler
                                       ↓
CLIPTextEncode(negative prompt) ──→ ModelSamplingSD3(shift=1.0)
                                       ↓
UNETLoader(wan2.2_ti2v_5B_fp16.safetensors)
    ↓
VAELoader(wan2.2_vae.safetensors)
    ↓
Wan22ImageToVideoLatent(width=1024, height=576, length=201)
    ↓
VAEDecode
    ↓
CreateVideo(fps=24)
    ↓
SaveVideo(filename_prefix="shot1_test", format="video/h264-mp4")
```

---

## 生成结果

| 文件名 | 状态 | 文件大小 | 日期 |
|--------|------|----------|------|
| `shot1_test_00001_.mp4` | 待生成 | — | 2026-04-21 |

---

## 历史记录

- **2026-04-17**：初次创建，使用 `WanFirstLastFrameToVideo` + T2V 模型（错误），视频几乎空白
- **2026-04-21**：更新为 `Wan22ImageToVideoLatent` + 正确的 I2V 模型（wan2.2_ti2v_5B_fp16）
