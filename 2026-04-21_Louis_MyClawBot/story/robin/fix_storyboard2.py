import json, os, re

BASE = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin'
FN = os.path.join(BASE, 'storyboard_v2.json')

with open(FN, 'r', encoding='utf-8') as f:
    data = json.load(f)

shots = data['shots']

def clean_rain_english(text):
    """Remove/replace rain-related English words and phrases."""
    if not text:
        return text
    t = text
    # Compound adjectives first (before single-word replacements)
    t = re.sub(r'\brain-slicked\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-streaked\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-soaked\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-swept\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-washed\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-blanketed\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-flecked\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-whipped\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain-battered\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\braindrops?\b', 'water drops', t, flags=re.IGNORECASE)
    t = re.sub(r'\brainfall\b', 'fall', t, flags=re.IGNORECASE)
    # Single words
    t = re.sub(r'\bright\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRain\b', 'Wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRaining\b', 'Wetting', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRainy\b', 'Wet', t, flags=re.IGNORECASE)
    # Phrases
    t = re.sub(r'the rain-', 'the wet ', t, flags=re.IGNORECASE)
    t = re.sub(r'the rain', 'the wet', t, flags=re.IGNORECASE)
    t = re.sub(r'The rain', 'The wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain on metal', 'condensation on metal', t, flags=re.IGNORECASE)
    t = re.sub(r'rain through', 'wet through', t, flags=re.IGNORECASE)
    t = re.sub(r'rain in wind', 'wet in wind', t, flags=re.IGNORECASE)
    t = re.sub(r'rain light', 'wet light', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-whipped', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy night', 'wet night', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-soaked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy-', 'wet-', t, flags=re.IGNORECASE)
    t = re.sub(r'\bslicked\b', 'wet', t, flags=re.IGNORECASE)  # after rain-slicked dealt with
    # Fix double-wet artifacts
    t = re.sub(r'wet wet', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'Wet wet', 'Wet', t, flags=re.IGNORECASE)
    return t

def clean_rain_chinese(text):
    """Remove/replace rain-related Chinese phrases only. Preserve metaphors like 暴风雨."""
    if not text:
        return text
    t = text
    # Only replace explicit weather references, NOT metaphors
    t = t.replace('雨雾', '雾气')
    t = t.replace('雨声', '水汽凝结声')
    t = t.replace('雨水', '水汽凝结的水')
    t = t.replace('雨夜', '湿夜')
    t = t.replace('雨天', '潮湿天气')
    t = t.replace('雨滴', '水滴')
    t = t.replace('雨水顺着玻璃流淌', '水汽凝结流淌')
    t = t.replace('雨水无声滑落', '水汽无声滑落')
    t = t.replace('雨水在车轮下飞溅', '水洼中的积水在车轮下飞溅')
    t = t.replace('雨水在', '水汽在')
    # Fix artifacts from 雨水 replacement
    t = t.replace('水汽凝结的水气', '水汽凝结的水')
    t = t.replace('水汽凝结的水凝结', '水汽凝结的水')
    return t

def clean_field(text):
    """Clean English and Chinese rain references separately."""
    text = clean_rain_english(text)
    text = clean_rain_chinese(text)
    return text

# ─── FIX 1: Shot 6 — Uncle Fat dialogue in Mandarin ───
s6 = next(s for s in shots if s['shot_index'] == 6)
s6['prompt'] = (
    "Over-the-shoulder from directly behind Robin's right shoulder as she settles into a seat "
    "across from a round middle-aged man — Uncle Fat, his face slack and easy, one hand wrapped "
    "loosely around a cold milk tea, the other resting beside a pineapple bun with a thick slice "
    "of butter. He looks exactly like someone's retired uncle, harmless and unimpressed. "
    "Camera: over-the-shoulder medium shot, 50mm lens, slight telephoto compression to bring "
    "both faces into intimate proximity. The table between them holds the milk tea, the bun, "
    "and the heavy silence of something unsaid. Lighting: warm amber key light from above, "
    "soft and forgiving. Uncle Fat speaks in Mandarin, his voice easy and relaxed: "
    "'Everything is in here. Once this brake is pulled, the whole of Hong Kong is going to "
    "put on quite a show.' "
    "His tone is casual, almost wistful. Robin's eyes track the U-shaped flash drive "
    "he slides across the table surface. Audio: the distant hum of the Teahouse, the soft "
    "slide of the USB on the table, Uncle Fat's Mandarin voice cutting through. "
    "Position: Robin occupies left third, Uncle Fat occupies right third, the U-drive in dead center."
)
s6['audio_cue'] = "肥叔普通话「东西全部都在这里面了。这个刹车要是踩下去，整个香港会有场好戏。」+ 瓷器轻碰声"
s6['emotion_tone'] = "日常感，暗流涌动"

# ─── FIX 2: Insert new shot 14 — Robin grabs U盘 ───
new_shot = {
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
        "Audio: the sharp plastic click of fingers closing over the drive — a sound like a small "
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

for s in shots:
    if s['shot_index'] >= 14:
        s['shot_index'] += 1
shots.insert(13, new_shot)
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

# ─── FIX 3: Apply rain cleaning to all fields ───
for shot in shots:
    for field in ['prompt', 'audio_cue', 'transition_hint', 'camera_move',
                  'emotion_tone', 'ref_images_logic']:
        if field in shot and isinstance(shot[field], str) and shot[field]:
            shot[field] = clean_field(shot[field])
    if 'position' in shot:
        for k, v in shot['position'].items():
            if isinstance(v, str) and v:
                shot['position'][k] = clean_field(v)
            elif isinstance(v, list):
                shot['position'][k] = [clean_field(x) if isinstance(x, str) else x for x in v]

# scenes
for scene in data.get('scenes', []):
    for k, v in scene.items():
        if isinstance(v, str):
            scene[k] = clean_field(v)

# character_tracking
for char_key, char_data in data.get('character_tracking', {}).items():
    for k, v in char_data.items():
        if isinstance(v, str):
            char_data[k] = clean_field(v)

# Restore specific Chinese metaphors that got incorrectly changed
for shot in shots:
    if shot.get('emotion_tone') == '暴风湿气前的平静':
        shot['emotion_tone'] = '暴风雨前的平静'
    if shot.get('emotion_tone') == '暴风湿气笼罩':
        shot['emotion_tone'] = '暴风雨笼罩'

# ─── FIX 4: Fix specific shot 10 window description ───
s10 = next((s for s in shots if s['shot_index'] == 10), None)
if s10:
    s10['prompt'] = (
        "An extreme close-up of the wet plate glass window. "
        "Outside: the blue-black of a Sham Shui Po wet night street, a sodium vapor lamp "
        "casting orange pools on the wet asphalt. Inside: nothing visible, only the glass "
        "and its surface. Camera: static extreme close-up, 135mm telephoto, framing the window "
        "so the glass fills the entire frame — no context, no orientation, only surface. "
        "Water traces diagonal lines down the glass, each droplet catching a different color: "
        "the orange of the street lamp, the blue of the distant siren, the cold white of the "
        "overhead interior light. Lighting: cold blue-black dominates, with the orange sodium "
        "glow fracturing through the water streaks. Audio: the room has gone completely silent "
        "— no dialogue, no fans, no chopsticks. Only the faint hiss of condensation on glass "
        "and, from somewhere distant, the rising wail of a police siren. "
        "Position: window dominates entire frame."
    )

# ─── FIX 5: Shot 15 (glass crash) — remove "like frozen rain" ───
s15 = next((s for s in shots if s['shot_index'] == 15), None)
if s15:
    s15['prompt'] = s15['prompt'].replace(
        'as they fall around her like frozen rain.',
        'as they scatter outward in slow arcs.'
    )
    s15['transition_hint'] = 'cut to 仰视中景'

# ─── FIX 6: Shot 18 — fix hair description ───
s18 = next((s for s in shots if s['shot_index'] == 18), None)
if s18:
    s18['prompt'] = s18['prompt'].replace(
        'Her silver-dyed hair whips in the wind, soaking wet and plastered to the sides of her face.',
        'Her silver-dyed hair clings to her forehead, wet with sweat and condensation, plastered to the sides of her face.'
    )

with open(FN, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done. Total shots:', len(shots))
