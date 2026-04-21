import json, os, re

BASE = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin'
FN = os.path.join(BASE, 'storyboard_v2.json')

with open(FN, 'r', encoding='utf-8') as f:
    data = json.load(f)

shots = data['shots']

def remove_rain(text):
    if not text:
        return text
    t = text
    # English patterns (order matters: specific compound words first)
    t = t.replace('rain-slicked', 'wet')
    t = t.replace('rain-streaked', 'wet')
    t = t.replace('rain-soaked', 'wet')
    t = t.replace('rain-swept', 'wet')
    t = t.replace('rain-washed', 'wet')
    t = t.replace('Rain-slicked', 'Wet')
    t = t.replace('Rain-streaked', 'Wet')
    t = t.replace('Rain-soaked', 'Wet')
    t = t.replace('rain slicked', 'wet')
    t = t.replace('rain streaked', 'wet')
    t = t.replace('rain slick', 'wet')
    t = t.replace('rain slick', 'wet')
    t = t.replace('rain wet', 'wet')
    t = t.replace('rain-', '')
    t = t.replace('Rain-', '')
    t = t.replace('the rain', 'the wet')
    t = t.replace('The rain', 'The wet')
    t = re.sub(r'\braining\b', 'wetting', t, flags=re.IGNORECASE)
    t = re.sub(r'\brainy\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brains\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\braindrops\b', 'drops', t, flags=re.IGNORECASE)
    t = re.sub(r'\braindrops?\b', 'water drops', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain ?like\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bthe rain-\b', 'the ', t, flags=re.IGNORECASE)
    # Chinese patterns
    t = t.replace('雨雾', '雾气')
    t = t.replace('雨声', '水汽凝结声')
    t = t.replace('雨水', '湿气')
    t = t.replace('雨夜', '湿夜')
    t = t.replace('雨天', '潮湿天气')
    t = t.replace('雨滴', '水滴')
    t = t.replace('雨顺着玻璃流淌', '水汽凝结流淌')
    t = t.replace('雨水无声滑落', '水汽无声滑落')
    t = t.replace('雨水在', '水汽在')
    t = t.replace('雨水在车轮下飞溅', '水洼中的积水在车轮下飞溅')
    t = t.replace('雨水在', '湿')
    t = t.replace('雨', '湿气')  # catch-all remaining
    # Fix double replacements
    t = t.replace('wet气', 'wet')
    t = t.replace('湿气气', '湿气')
    return t

# ─── FIX 1: Shot 6 — add Uncle Fat Mandarin dialogue ───
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
s6['ref_images_logic'] = "角色三视图，确保 Robin 外观一致性"

# ─── FIX 2: Insert new shot 14 — Robin grabs U盘 quickly ───
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

# Renumber existing shots 14-18 → 15-19
for s in shots:
    if s['shot_index'] >= 14:
        s['shot_index'] += 1

# Insert new shot at index 13 (0-based = before current shot 14, now shot 15)
shots.insert(13, new_shot)

# Re-index
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

# ─── FIX 3: Remove rain from all fields ───
for shot in shots:
    for field in ['prompt', 'audio_cue', 'transition_hint', 'camera_move',
                  'emotion_tone', 'ref_images_logic']:
        if field in shot and isinstance(shot[field], str) and shot[field]:
            shot[field] = remove_rain(shot[field])
    # position fields
    if 'position' in shot:
        for k, v in shot['position'].items():
            if isinstance(v, str) and v:
                shot['position'][k] = remove_rain(v)
            elif isinstance(v, list):
                shot['position'][k] = [remove_rain(x) if isinstance(x, str) else x for x in v]

# scene/atmosphere
for scene in data.get('scenes', []):
    for k, v in scene.items():
        if isinstance(v, str):
            scene[k] = remove_rain(v)

# character tracking
for char_key, char_data in data.get('character_tracking', {}).items():
    for k, v in char_data.items():
        if isinstance(v, str):
            char_data[k] = remove_rain(v)

# ─── FIX 4: Restore shot 10 specifically (window close-up, remove rain mentions) ───
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

# ─── FIX 5: Update shot 15 (old shot 14, now the glass crash) — remove "glass rain" ───
s15 = next((s for s in shots if s['shot_index'] == 15), None)
if s15:
    s15['prompt'] = s15['prompt'].replace(
        'Glass fragments catching the dual-color light — warm amber from the Teahouse behind her, '
        'cold blue from the street lamps ahead — as they fall around her like frozen rain.',
        'Glass fragments catch the dual-color light — warm amber from the Teahouse behind her, '
        'cold blue from the street lamps ahead — as they scatter outward in slow arcs.'
    )
    s15['transition_hint'] = s15.get('transition_hint', '').replace('cut to 爆发', 'cut to 仰视中景')
    if s15.get('audio_cue'):
        s15['audio_cue'] = remove_rain(s15['audio_cue'])

# ─── FIX 6: Shot 18 — remove wet wind whipping ───
s18 = next((s for s in shots if s['shot_index'] == 18), None)
if s18:
    s18['prompt'] = s18['prompt'].replace(
        'Her silver-dyed hair whips in the wind, soaking wet and plastered to the sides of her face.',
        'Her silver-dyed hair clings to her forehead, wet with sweat and condensation, plastered to the sides of her face.'
    ).replace(
        'black leather jacket spread behind her like wings.',
        'black leather jacket spread behind her.'
    )
    if s18.get('audio_cue'):
        s18['audio_cue'] = remove_rain(s18['audio_cue'])

with open(FN, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Saved OK')
print('Total shots:', len(shots))
