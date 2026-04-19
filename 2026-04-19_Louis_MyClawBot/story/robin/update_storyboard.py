import json, re, copy, sys, os

BASE = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin'
FN = os.path.join(BASE, 'storyboard_v2.json')

with open(FN, 'r', encoding='utf-8') as f:
    data = json.load(f)

shots = data['shots']

# ─────────────────────────────────────────────
# CHANGE 1: Shot 6 — 加上肥叔普通话台词
# Original dialogue (from orig storyboard.json shot 7):
#   肥叔：（普通话）"东西全部都在这里面了。这个刹车要是踩下去，整个香港看来会有场好戏要上演了。"
# Shot 6 existing prompt replaces "越肩" with dialogue included
# ─────────────────────────────────────────────
shot6 = next(s for s in shots if s['shot_index'] == 6)
shot6['prompt'] = (
    "Over-the-shoulder from directly behind Robin's right shoulder as she settles into a seat "
    "across from a round middle-aged man — Uncle Fat, his face slack and easy, one hand wrapped "
    "loosely around a cold milk tea, the other resting beside a pineapple bun with a thick slice "
    "of butter. He looks exactly like someone's retired uncle, harmless and unimpressed. "
    "Camera: over-the-shoulder medium shot, 50mm lens, slight telephoto compression to bring "
    "both faces into intimate proximity. The table between them holds the milk tea, the bun, "
    "and the heavy silence of something unsaid. Lighting: warm amber key light from above, "
    "soft and forgiving. Uncle Fat speaks in Mandarin, his voice easy and relaxed: "
    "'Everything is in here. Once this brake is pulled, it seems the whole of Hong Kong "
    "is going to put on quite a show.' "
    "His tone is casual, almost wistful. Robin's eyes track the U-shaped flash drive "
    "he slides across the table surface. Audio: the distant hum of the Teahouse, the slide "
    "of the USB on the table, Uncle Fat's Mandarin voice cutting through. "
    "Position: Robin occupies left third, Uncle Fat occupies right third, the U-drive in dead center."
)
shot6['audio_cue'] = "肥叔普通话「东西全部都在这里面了。这个刹车要是踩下去，整个香港会有场好戏。」+ 瓷器碰撞声"
shot6['emotion_tone'] = "日常感，暗流涌动"

# ─────────────────────────────────────────────
# CHANGE 2: Insert new shot 14 — Robin快速拿走U盘
# Existing shot 14 (撞玻璃) → renumber to 15
# Shots 15-18 → 16-19
# ─────────────────────────────────────────────

new_shot14 = {
    "shot_index": 14,
    "time": "01:09-01:12",
    "duration": 3,
    "scene": "突破",
    "shot_type": "insert",
    "prompt": (
        "Extreme close-up: Robin's hand darts forward and snatches the USB drive from the table "
        "with surgical speed — fingers closing around it, palm trapping it flat, a micro-motion "
        "taking less than a second. Her wrist snaps back, the drive now deep inside her fist. "
        "Camera: extreme close-up static shot, 135mm telephoto, framed tight on the hand and "
        "the U-drive throughout — the blur of her sleeve the only contextual information. "
        "The background remains a warm-amber wash of the Teahouse interior. "
        "Lighting: warm amber overhead, the drive catching a glint of metal light as it disappears "
        "into her grip. "
        "Audio: the sharp plastic click of fingers closing over the drive, a sound like a small "
        "lock clicking shut — followed by the immediate muffled roar of the panicked Teahouse behind her. "
        "Position: hand and U-drive occupy dead center of frame throughout."
    ),
    "camera_move": "特写锁定（手持U盘拿走）",
    "camera_detail": {
        "framing": "extreme close-up",
        "angle": "eye-level",
        "movement": "static",
        "focal_length": "135mm",
        "depth_of_field": "shallow"
    },
    "position": {
        "character_left": [],
        "character_center": ["罗宾（手）", "U盘"],
        "character_right": [],
        "props": ["U盘"],
        "foreground": "",
        "background": "茶餐厅内部虚化"
    },
    "characters": ["罗宾"],
    "ref_images": ["refs/robin_three_views.png"],
    "ref_images_logic": "角色三视图，确保 Robin 手部外观一致性（黑色皮衣袖口+银环）",
    "transition_hint": "cut to 动态追踪（撞玻璃）",
    "emotion_tone": "精准、冷静",
    "audio_cue": "手指合拢扣住U盘的清脆塑料声，背景混乱尖叫被压低",
    "narrative_function": "tension_release",
    "seed": 1246
}

# Renumber existing shots 14-18 → 15-19
for s in shots:
    if s['shot_index'] >= 14:
        s['shot_index'] += 1

# Insert new shot 14
# Find insertion point (after old shot 13, before old shot 14 which is now 15)
shots.insert(14 - 1, new_shot14)  # insert at index 13 (0-based), before what is now shot 15

# Re-assign correct indices after insertion
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

print(f"Total shots after insertion: {len(shots)}")

# ─────────────────────────────────────────────
# CHANGE 3: Remove ALL "rain" references
# Pattern: rain, rainy, rainy, rain-streaked, rain-soaked, rain-slicked, rain-slicked,
#          rain-licked, raindrop, rain-washed, rain-filled, rain-blurred, rain-XXX
# Also: 雨, 雨水, 雨声, 雨雾, 雨夜, 雨天, 雨滴
# ─────────────────────────────────────────────

RAIN_PATTERNS = [
    re.compile(r'\brain[-\s]?\w*', re.IGNORECASE),
    re.compile(r'\b雨天\b', re.IGNORECASE),
    re.compile(r'\b雨夜\b', re.IGNORECASE),
    re.compile(r'\b雨水\b', re.IGNORECASE),
    re.compile(r'\b雨声\b', re.IGNORECASE),
    re.compile(r'\b雨雾\b', re.IGNORECASE),
    re.compile(r'\b雨滴\b', re.IGNORECASE),
    re.compile(r'雨$', re.IGNORECASE),
    re.compile(r'雨顺着玻璃流淌', re.IGNORECASE),
]

REPLACE_WITH = {
    'rain-streaked': 'wet',
    'rain-slicked': 'wet',
    'rain-soaked': 'wet',
    'rain-slicked': 'wet',
    'rain-licked': 'wet',
    'rain-washed': 'wet',
    'rain-filled': 'wet',
    'rain-blurred': 'wet',
    'rain-swept': 'wet',
    'rain-whipped': 'wet',
    'rain-blanketed': 'wet',
    'rain-flecked': 'wet',
    'rain-drop': 'drop',
    'rain-streaked': 'wet',
    'rain and': '',
    'rain on': 'on',
    'rain in': 'in',
    'rain through': 'through',
    'rain of': 'of',
    'rain of': 'of',
    'rainy': 'wet',
    'rainfall': 'fall',
    'the rain-': 'the ',
    'The rain-': 'The ',
    'rainy night': 'wet night',
    'rainy night': 'wet night',
    '雨顺着玻璃流淌': '玻璃上的水汽凝结',
    '雨水': '湿气',
    '雨夜': '湿夜',
    '雨声': '水汽凝结声',
    '雨雾': '雾气',
    '雨滴': '水滴',
    '雨天': '潮湿天气',
    '雨$': '水汽',
}

def clean_rain(text):
    if not text:
        return text
    # Replace known patterns
    result = text
    # Generic rain-prefix and rain-suffix patterns
    result = re.sub(r'\brain[-\s]?streaked\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain[-\s]?slicked\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain[-\s]?swept\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain[-\s]?soaked\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain[-\s]?washed\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\bRain[-\s]?streaked\b', 'Wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\bRain[-\s]?slicked\b', 'Wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\bthe rain[-\s]?\w+\b', 'the wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\bthe rain\b', 'the wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain[-\s]?(?:drops?|dropping)\b', 'water drops', result, flags=re.IGNORECASE)
    result = re.sub(r'\brain\b', 'wet', result, flags=re.IGNORECASE)
    result = re.sub(r'\bRain\b', 'Wet', result, flags=re.IGNORECASE)
    result = re.sub(r'雨水', '湿气', result)
    result = re.sub(r'雨声', '水汽凝结声', result)
    result = re.sub(r'雨雾', '雾气', result)
    result = re.sub(r'雨夜', '湿夜', result)
    result = re.sub(r'雨天', '潮湿天气', result)
    result = re.sub(r'雨滴', '水滴', result)
    result = re.sub(r'雨水顺着玻璃流淌', '玻璃上的水汽凝结流淌', result)
    result = re.sub(r'雨水无声滑落', '水汽无声滑落', result)
    result = re.sub(r'雨水在车轮下飞溅', '水洼中的积水在车轮下飞溅', result)
    result = re.sub(r'\b雨\b', '水汽', result)
    return result

count = 0
for shot in shots:
    for field in ['prompt', 'audio_cue', 'transition_hint', 'camera_move',
                  'emotion_tone', 'ref_images_logic']:
        if field in shot and shot[field]:
            before = shot[field]
            after = clean_rain(shot[field])
            if before != after:
                count += 1
                shot[field] = after
    # Also clean position fields
    for pos_field in ['foreground', 'background', 'character_left', 'character_right',
                       'character_center', 'props']:
        if pos_field in shot.get('position', {}):
            val = shot['position'][pos_field]
            if isinstance(val, list):
                shot['position'][pos_field] = [clean_rain(v) for v in val]
            elif isinstance(val, str):
                shot['position'][pos_field] = clean_rain(val)

print(f"Cleaned {count} field instances")

# Also clean scene/atmosphere descriptions
for scene in data.get('scenes', []):
    for key in scene:
        if isinstance(scene[key], str):
            scene[key] = clean_rain(scene[key])

# Fix shot 9 (window close-up): original Chinese had "雨水顺着玻璃流淌"
# Already cleaned above, but double check
# Also: the street outside is "wet" not "rainy"

# Fix character_tracking last_frame descriptions that mention rain
for char_key, char_data in data.get('character_tracking', {}).items():
    if 'last_frame' in char_data and char_data['last_frame']:
        char_data['last_frame'] = clean_rain(char_data['last_frame'])

# Remove rain from shot 10 prompt (the window shot — original says 雨水顺着玻璃流淌)
shot10 = next((s for s in shots if s['shot_index'] == 10), None)
if shot10:
    shot10['prompt'] = (
        "An extreme close-up of the rain-streaked plate glass window. "
        "Outside: the blue-black of a Sham Shui Po wet night street, a sodium vapor lamp "
        "casting orange pools on the wet asphalt. Inside: nothing visible, only the glass "
        "and its surface. Camera: static extreme close-up, 135mm telephoto, framing the "
        "window so the glass fills the entire frame — no context, no orientation, only surface. "
        "Water traces diagonal lines down the glass, each droplet catching a different color: "
        "the orange of the street lamp, the blue of the distant siren, the cold white of the "
        "overhead interior light. Lighting: cold blue-black dominates, with the orange sodium "
        "glow fracturing through the water streaks. Audio: the room has gone completely silent "
        "— no dialogue, no fans, no chopsticks. Only the faint hiss of condensation on glass "
        "and, from somewhere distant, the rising wail of a police siren. "
        "Position: window dominates entire frame."
    )
    shot10['audio_cue'] = "寂静 + 远处警笛渐近"

# Shot 1: clean "rain-mist" in foreground
shot1 = next((s for s in shots if s['shot_index'] == 1), None)
if shot1:
    shot1['position']['foreground'] = "湿气雾气"
    shot1['transition_hint'] = "cut to 侧拍领位员"

# Print updated shot 6 prompt to verify
s6 = next((s for s in shots if s['shot_index'] == 6), None)
print(f"\nShot 6 prompt (first 200 chars):\n{s6['prompt'][:200]}")

# Print new shot 14
s14 = next((s for s in shots if s['shot_index'] == 14), None)
print(f"\nNew shot 14 exists: {s14 is not None}, scene: {s14['scene'] if s14 else 'N/A'}")

# Verify total count
print(f"\nFinal shot count: {len(shots)}")
for s in shots:
    print(f"  shot {s['shot_index']}: {s['scene']} | {s['time']}")

with open(FN, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'\nSaved: {FN}')
