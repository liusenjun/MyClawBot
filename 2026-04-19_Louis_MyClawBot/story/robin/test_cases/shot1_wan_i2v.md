# Shot 1 — 测试用例

**项目：** 人类刹车计划 · 第一幕「深水埗暗线」  
**镜头：** Shot 1 (00:00–00:20) · 全景固定 · 室外茶餐厅街景  
**模型：** Wan 2.2 Image-to-Video (`WanFirstLastFrameToVideo`)  
**生成日期：** 2026-04-17

---

## 输入

| 项目 | 内容 |
|------|------|
| **输入图片** | `gemini_shot/shot1.png` |
| **剧本描述** | 深水埗深夜街景，霓虹闪烁，茶餐厅暖灯 |
| **景别** | 全景（Wide / Full View） |
| **运镜** | 固定机位（Fixed Static Camera） |

---

## Prompts

### Positive
```
香港深水埗深夜街景，霓虹招牌红蓝闪烁，雨雾弥漫，地面湿滑泛着冷冽反光，
街角茶餐厅门面，暖黄灯光从窗户透出，复古花砖地面，港风霓虹灯牌，
湿润柏油路面倒映霓虹光，
全景画面，固定机位，摄影机静止不动，
cinematic film still photography, sharp focus, anamorphic bokeh, Hong Kong night market, 24fps
```

### Negative
```
blurry, low quality, watermark, distorted, still frame, flickering, noisy, grainy, washed out, cartoon, anime, day time, bright, crowd, camera shake, pan, tilt, zoom
```

---

## 技术参数

| 参数 | 值 |
|------|-----|
| 分辨率 | 1024 × 576（16:9） |
| 帧数 | 201 帧 |
| 时长 | ~8.4 秒（@24fps） |
| VAE | `wan_2.1_vae.safetensors` |
| CLIP | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` |
| 输出格式 | video/h264-mp4 |

---

## Workflow 节点链

```
LoadImage (shot1.png)
    ↓
CLIPLoader (umt5_xxl_fp8_e4m3fn_scaled) → CLIPTextEncode(positive)
                                                    ↓
CLIPTextEncode(negative) ← CLIPLoader
    ↓
WanFirstLastFrameToVideo(start_image=LoadImage, positive, negative, vae, length=201, width=1024, height=576)
    ↓
VAEDecode(samples)
    ↓
VHS_VideoCombine(frame_rate=24, format=video/h264-mp4)
    ↓
SaveVideo(filename_prefix="shot1_test")
```

---

## 生成结果

| 文件名 | 时长 | 帧数 | 分辨率 | 文件大小 | 备注 |
|--------|------|------|--------|----------|------|
| `shot1_test_00001.mp4` | — | — | — | — | 待生成 |

---

## 其他模型测试记录

> 补充其他模型跑过此镜头的效果
