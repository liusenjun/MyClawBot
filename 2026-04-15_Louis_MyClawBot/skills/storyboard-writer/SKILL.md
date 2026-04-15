---
name: storyboard-writer
description: "将剧本/叙事概念转化为专业的分镜头剧本（Storyboard）。融合 ViMax 多智能体视频生成框架的核心理念：场景切分、角色一致性追踪、多机位设计、参考图智能选择、叙事节奏控制。适用场景：规划多镜头视频序列、将叙事概念转化为拍摄就绪的分镜头列表、为每个镜头生成可供 Wan 2.2 / HunyuanVideo / LTX-2.3 等模型使用的渲染 Prompt。模型由调用者根据项目需求自行选择。使用时机：创建新项目、规划视频序列、编写或优化 storyboard.json。"
---

# Storyboard Writer

将剧本或叙事概念转化为专业的分镜头剧本，融合 ViMax 框架的核心产品理念：场景智能切分、角色一致性追踪、多机位设计、参考图智能选择与叙事节奏控制。

---

## ViMax 核心理念（融入本 Skill）

ViMax 是一个多智能体视频生成框架，它的核心理念：

| ViMax 模块 | 功能 | 我们在 storyboard 中的对应 |
|------------|------|---------------------------|
| 智能剧本解析 | RAG 分析长文本，自动切分场景边界 | scene_analysis → scene_breakdown |
| 表现力分镜设计 | 电影语言生成镜头级分镜 | shot_index + camera_move + camera_detail |
| 多机位拍摄模拟 | 同一场景多角度拍摄 | multi_angle_shots（同一 scene 的多个 shot） |
| 智能参考图选择 | 选前一镜头的末帧作为当前镜头的首帧参考 | ref_images: last_frame_reference |
| 一致性校验 | VLM 评估生成质量 | quality_checklist（人工/VLM） |
| 高效并行生成 | 同机位连续镜头并行渲染 | batch_rendering（按机位分组） |
| 叙事节奏控制 | 根据场景类型调整镜头时长和节奏 | emotion_tone + duration |

---

## 核心原则

**Prompt 必须写成单一流畅段落**，不能是列表或碎片化描述。

---

## 模型选择（由调用者决定）

| 模型 | 适用场景 | 推荐参数 |
|------|----------|----------|
| Wan 2.2 | 通用场景，性价比高 | 1280×720, 8步, 121帧(~5秒) |
| HunyuanVideo | 电影感强，清晰度高 | 1280×720, T2V（需安装专用节点） |
| LTX-2.3 | 快速渲染 | 768×512, 4-6步 |

**调用者选择模型后，在 storyboard.json 的 `model` 字段注明。**

---

## Step 1: 场景分析与切分（Scene Analysis）

收到剧本后，首先进行场景切分：

### 场景边界识别规则

1. **地点变化** = 新场景（茶餐厅内 → 街道 → 车内）
2. **时间跳转** = 新场景（白天 → 深夜）
3. **主要动作/情节段** = 一个场景单元
4. **情绪基调变化** = 子场景切分依据

### 场景信息提取

对每个场景提取：
```
scene_name: "深水埗茶餐厅"
location: "香港深水埗"
time_of_day: "深夜"
lighting: "暖黄室内灯 + 冷蓝霓虹"
atmosphere: "烟火气但暗流涌动"
characters_present: ["罗宾", "肥叔"]
key_props: ["U盘", "菠萝包", "冻奶茶"]
```

---

## Step 2: 镜头设计（Shot Design）

### 镜头类型分类（ViMax 借鉴）

| 类型 | 用途 | 特征 |
|------|------|------|
| **Establishing Shot** | 建立场景 | 远景/全景，交代地点、时间、氛围 |
| **Action Shot** | 主体动作 | 跟拍/手持，强调真实感 |
| **Reaction Shot** | 角色反应 | 近景/特写，捕捉表情 |
| **Insert Shot** | 物件特写 | 特写，强调关键道具 |
| **Cutaway** | 转移视线 | 空镜/环境镜头，调节节奏 |
| **POV Shot** | 主观镜头 | 让观众代入角色视角 |
| **Master Shot** | 完整记录 | 长镜头记录整个场景 |

### 景别规范（具体化）

| 景别 | 英文 | 用途 |
|------|------|------|
| 极远景 | Extreme Wide | 建立城市/建筑全貌 |
| 远景 | Wide / Full | 角色全身，交代与环境关系 |
| 中远景 | Medium Wide | 膝盖以上，叙事性场景 |
| 中景 | Medium | 腰部以上，对话/反应 |
| 近景 | Close-up | 胸部以上，强调表情 |
| 特写 | Close-up | 脸部/物件，强调细节 |
| 极特写 | Extreme Close-up | 眼睛/手指/关键道具 |

### 相机运动规范

| 运动 | 描述 | 适用场景 |
|------|------|----------|
| Static | 固定机位 | 静态对话、物件特写 |
| Dolly Forward | 推进 | 从远景到近景的情绪推进 |
| Dolly Back / Pull-back | 后拉 | 从特写拉开到全景，揭示环境 |
| Tracking Shot | 跟拍 | 跟随角色行走/奔跑 |
| Pan Left/Right | 摇镜 | 横向扫视环境 |
| Tilt Up/Down | 俯仰 | 从脚到头或相反 |
| Crane Up/Down | 升降 | 从低到高或相反，大范围运动 |
| POV | 主观镜头 | 角色视角 |

### 焦距参考

| 焦距 | 视野 | 适用场景 |
|------|------|----------|
| 16-24mm | 超广角 | 建筑/狭小空间/夸张透视 |
| 35-50mm | 标准 | 日常叙事/对话 |
| 85mm | 人像 | 表情特写/浅景深 |
| 135mm+ | 长焦 | 远距离跟拍/压缩感 |

---

## Step 3: Shot Duration 参考

| 镜头类型 | 时长 | 示例 |
|----------|------|------|
| 快速动作 | 2–4s | 枪击、撞碎玻璃、起步 |
| 行走/对话 | 5–7s | 跟拍行走、对坐交谈 |
| 建立/情感 | 7–10s | 空镜、情绪特写、转场奔跑 |
| 超长运动 | 10s+ | 追车、追逐戏 |

**ViMax 叙事节奏原则：**
- 紧张场景 → 短镜头，快节奏切换
- 情感场景 → 长镜头，慢节奏
- 转场场景 → 中等长度，留出呼吸空间

---

## Step 4: Prompt 写作规范

每段 Prompt 必须同时覆盖以下维度（顺序不固定，但每项都要有）：

### 1. 场景主体
- 谁/什么在画面中心
- 在做什么、什么状态
- 用现在时、Cinematic 风格

### 2. 相机 + 景别
- 具体景别：extreme wide shot / wide shot / medium / close-up / extreme close-up
- 具体机位：overhead / low angle / high angle / POV / over-the-shoulder
- 具体运动：static / slow dolly forward / tracking shot / pan left / tilt up / crane up
- 具体焦距：24mm wide angle / 50mm natural / 85mm portrait / 135mm telephoto

### 3. 光线 + 色彩
- 光源方向：rim light from left / backlit / soft front fill
- 色温：warm tungsten / cool blue / golden hour / neon magenta
- 氛围：light fog / rain mist / dust particles / shallow depth of field

### 4. 音效暗示（画内音）
- 环境音：muffled city traffic / distant thunder / clinking porcelain
- 情绪音：slow piano motif building / bass rumble / high-pitched tension tone
- 描述方式：Audio: ...（句末或句首都可以）

### 5. 角色动作细节
- 不能只写"罗宾走着"
- 要写：步伐节奏、手的位置、眼神方向、呼吸状态
- 体现角色情绪（恐惧、警觉、冷漠、平静）

### 6. 空间位置（ViMax 强调）
- 角色在场景中的位置（左/中/右）
- 与其他角色/道具的关系
- 前景/背景元素

### 7. 风格参考（可选）
- 参考图风格：in the photographic style of the provided ref image
- 影视风格：cinematic / documentary / noir / anime / realist
- 不要只写"电影感"，要写具体风格

### 8. 转场衔接
- 在 Prompt 末尾加一句说明与下一个镜头的衔接关系

---

## Prompt 示例

**原始版本（不够专业）：**
> 超低角度从后方跟随主角步伐，镜头几乎贴近湿漉漉的地面。黑色皮靴踩过油腻地砖，每一步都精准避开水洼和来往服务员的脚步。

**升级版本（符合规范）：**
> Robin, silver-dyed short hair hidden beneath a leather jacket collar, moves through the cramped Teahouse with predatory precision — each footfall deliberate, weight rolling heel-to-toe to silence on the oil-slicked floor. Camera: extremely low angle tracking shot from directly behind, lens nearly grazing the wet tiles, 24mm wide angle to exaggerate speed. Lighting: warm amber from overhead Teahouse lamps cuts through cool blue-tinged rain light outside, shallow depth of field compressing the crowded background into bokeh. Audio: distant clinking porcelain, muffled Cantonese chatter, the wet squelch of boots on tile amplified. Her breathing: controlled, shallow, the rhythm of someone who knows exactly where everyone in the room is. Position: she occupies the right third of frame, passing a serving cart on her left. Transition: cut to foreground obstruction as she passes a serving cart.

---

## Shot JSON Schema（增强版）

```json
{
  "shot_index": 1,
  "time": "00:00-00:05",
  "duration": 5,
  "scene": "场景名",
  "shot_type": "establishing/action/insert/reaction/cutaway/pov/master",
  "prompt": "（升级后的完整 Prompt）",
  "camera_move": "相机运动简述（用于快速浏览）",
  "camera_detail": {
    "framing": "extreme close-up / close-up / medium / wide / extreme wide",
    "angle": "eye-level / low angle / high angle / overhead / POV",
    "movement": "static / tracking / pan / tilt / dolly / crane / handheld",
    "focal_length": "24mm / 50mm / 85mm / 135mm",
    "depth_of_field": "shallow / deep / bokeh background"
  },
  "position": {
    "character_left": ["角色A"],
    "character_center": [],
    "character_right": ["角色B"],
    "props": ["U盘"],
    "foreground": "模糊的餐具散景",
    "background": "暖黄灯光的餐厅内部"
  },
  "characters": ["角色名"],
  "ref_images": ["refs/xxx.png"],
  "ref_images_logic": "角色三视图 / 氛围参考 / 末帧参考（last_frame_from_shot_N）",
  "transition_hint": "cut to 下一镜头描述",
  "emotion_tone": "紧张/平静/压迫/动作/悬疑/温情",
  "audio_cue": "音效描述（用于后期参考）",
  "narrative_function": "establishing / tension_build / climax / release / transition",
  "seed": 1234
}
```

**新增字段说明：**
- `shot_type`：镜头功能分类（建立/动作/插入/反应/转移/主观/主镜头）
- `position`：角色和道具在画面中的空间位置
- `ref_images_logic`：为什么选这张参考图（ViMax 的智能参考图选择理念）
- `narrative_function`：这个镜头在叙事中的功能（建立/张力构建/高潮/释放/转场）

---

## Step 5: 一致性追踪（Consistency Tracking）

### 角色外观追踪表

对每个角色维护：

```json
{
  "character_name": "罗宾",
  "appearance": {
    "hair": "银色挑染短发",
    "clothing": "黑色皮衣，银色金属扣",
    "expression": "冷冽警觉，眼神锐利"
  },
  "shots_appeared": [1, 3, 4, 6, 8, 13, 14, 15, 16, 17, 18],
  "last_shot": 18,
  "last_frame_description": "银发湿漉漉贴在脸上，黑色皮衣在雨中泛着微光"
}
```

### 参考图选择逻辑（ViMax 理念）

| 情况 | 选择策略 |
|------|----------|
| 同一 scene 内连续镜头 | 使用上一镜头的末帧作为首帧参考 |
| 角色特写 | 使用角色三视图 |
| 场景建立镜头 | 使用氛围参考图 |
| 物件特写 | 使用物件清晰图 |
| 跳跃剪辑后 | 重新使用角色三视图确认外观 |

---

## Step 6: 质量检查清单

写完每个 Prompt 后自检：
- [ ] 是单一段落，不是列表？
- [ ] 有具体景别（不只是"中景"）？
- [ ] 有具体焦距（50mm / 24mm / 85mm）？
- [ ] 有具体相机运动（不只是"跟拍"）？
- [ ] 有光源方向和色温？
- [ ] 有角色动作细节（不只是"走着"）？
- [ ] 有空间位置描述？
- [ ] 有音效暗示（Audio: ...）？
- [ ] 末尾有 transition_hint？
- [ ] 角色外观与之前镜头一致？
- [ ] 情绪基调与场景匹配？

---

## 工作流程

### Step 1: 读取剧本

从调用者提供的剧本（txt / md / json 格式）读取叙事内容。

### Step 2: 场景分析与切分

对剧本进行 scene_analysis，输出场景列表。

### Step 3: 生成 Shot 列表

对每个场景设计多个镜头，确定 shot_type、camera_detail、position。

### Step 4: 编写 Prompt

按本 skill 的 Prompt 写作规范逐个编写。

### Step 5: 建立一致性追踪

填写 character_tracking 表，标注 ref_images_logic。

### Step 6: 渲染测试

用指定模型渲染 1-2 个关键镜头，对比效果后调整 Prompt 写法。

### Step 7: 批量渲染

按顺序渲染所有镜头，使用 transition_hint 在后期软件中拼接。

---

## 参考图使用规范

| 用途 | 使用方式 |
|------|----------|
| 角色外貌参考 | 每个包含角色的镜头尽量使用角色三视图 |
| 场景氛围参考 | 空镜/建立镜头使用氛围图 |
| 物件特写参考 | 有特定道具（U盘/摩托车）时使用 |
| 末帧参考 | 同 scene 连续镜头用上一 shot 末帧 |

参考图路径：`story/项目名/refs/` 目录

---

## 与原版 storyworld-storyboard 的区别

| 项目 | storyworld-storyboard | storyboard-writer（我们） |
|------|----------------------|--------------------------|
| 场景切分 | 无 | Scene Analysis 模块（ViMax 理念） |
| 镜头类型分类 | 无 | shot_type 分类（8种） |
| 相机描述 | 简单描述 | camera_detail 详细参数（景别/机位/运动/焦距/景深） |
| 空间位置 | 无 | position 字段（角色左右/道具/前后景） |
| 参考图逻辑 | MCP 获取 | ref_images_logic（ViMax 理念） |
| 一致性追踪 | 无 | character_tracking 表 |
| 叙事功能 | 无 | narrative_function 字段 |
| Prompt 维度 | 7 项 | 8 项（新增空间位置） |
| 模型 | LTX-2.3（固定） | 调用者自选（Wan 2.2 / Hunyuan / LTX-2.3） |
| 镜头衔接 | last-frame i2v（链式渲染） | 后期软件拼接 + ref_images_logic |

---

## 快速开始

```bash
# 1. 提供剧本内容
# 2. 选择模型（Wan 2.2 / HunyuanVideo / LTX-2.3）
# 3. 执行 Scene Analysis（场景切分）
# 4. 设计 Shot 列表（每场景 3-8 个镜头）
# 5. 对照本 skill 的 Prompt 写作规范逐个编写
# 6. 渲染测试 shot 1
# 7. 效果满意后批量渲染
```
