import json, os, re

BASE = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin'
FN = os.path.join(BASE, 'storyboard_v2.json')

with open(FN, 'r', encoding='utf-8') as f:
    data = json.load(f)

shots = data['shots']
print('Before fix: total shots =', len(shots))

# ── Remove DUPLICATE new shot (both fix_storyboard.py and fix_storyboard2.py inserted one) ──
# Find shots with shot_index 14 that appear twice (the duplicate new shot)
# We want to KEEP the FIRST one (from fix_storyboard.py, already in file) and remove the second
indices_14 = [i for i, s in enumerate(shots) if s['shot_index'] == 14]
print('Shots with index 14:', indices_14)
if len(indices_14) >= 2:
    # Remove the LAST occurrence (the duplicate from fix_storyboard2.py)
    dup_idx = indices_14[-1]
    print('Removing duplicate at position', dup_idx)
    shots.pop(dup_idx)

# Re-index
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

print('After removing duplicate: total shots =', len(shots))

# ── FIX: 肥叔普通话台词 (Shot 6) ──
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
print("Shot 6 Uncle Fat dialogue updated")

# ── FIX: Insert NEW shot 14 between existing 13 and 15 (glass crash) ──
# Current shots: 13=Robin grabs U盘, 14=should be glass crash (was old 14), 15=should be old 15...
# We need to INSERT new shot 14, renumber existing 14→15, 15→16, etc.
new_shot_14 = {
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

# The fix_storyboard.py ALREADY inserted a new shot (now at position 13, shot_index=13)
# That one IS the Robin grabbing U盘 shot. So we should NOT insert again.
# But wait - we need to CHECK if a Robin-grabbing-U盘 shot already exists
grab_udos_shots = [s for s in shots if 'snatches the USB' in s.get('prompt','') or 'U盘' in str(s.get('position',{}))]
print('Existing grab-U盘 shots:', [s['shot_index'] for s in grab_udos_shots])

if not grab_udos_shots:
    # Insert at position 13 (0-based), will become shot_index=14
    for s in shots:
        if s['shot_index'] >= 14:
            s['shot_index'] += 1
    shots.insert(13, new_shot_14)
    print("Inserted new shot 14 (grab U盘)")
else:
    print("Grab-U盘 shot already exists at index", grab_udos_shots[0]['shot_index'], "- skipping insert")

# Re-index after any changes
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

print('Final shot count:', len(shots))

# ── FIX: Clean rain from all fields (English only, preserve Chinese metaphors) ──
def clean_english(text):
    if not text: return text
    t = text
    t = re.sub(r'rain-slicked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-streaked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-soaked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-swept', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-washed', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-whipped', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-battered', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'braindrops?', 'water drops', t, flags=re.IGNORECASE)
    t = re.sub(r'rainfall', 'fall', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy-', 'wet-', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRain\b', 'Wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRaining\b', 'Wetting', t, flags=re.IGNORECASE)
    t = re.sub(r'rain on', 'condensation on', t, flags=re.IGNORECASE)
    t = re.sub(r'rain light', 'wet light', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-night', 'wet-night', t, flags=re.IGNORECASE)
    t = re.sub(r'wet wet', 'wet', t, flags=re.IGNORECASE)
    return t

def clean_chinese(text):
    if not text: return text
    t = text
    # Preserve 暴风雨 as metaphor, only replace weather-descriptive 雨
    t = t.replace('雨雾', '雾气')
    t = t.replace('雨声', '凝结声')
    t = t.replace('雨滴', '水滴')
    t = t.replace('雨水无声滑落', '水汽无声滑落')
    t = t.replace('雨水在车轮下飞溅', '水洼中的积水在车轮下飞溅')
    t = t.replace('雨水顺着玻璃流淌', '水汽凝结流淌')
    # Don't replace 雨夜 / 雨水 wholesale — only explicit weather
    return t

# Check current emotion_tone values that might have 暴风湿气
for s in shots:
    for field in ['prompt', 'audio_cue', 'transition_hint', 'camera_move', 'emotion_tone', 'ref_images_logic']:
        v = s.get(field)
        if isinstance(v, str) and v:
            s[field] = clean_english(clean_chinese(v))
    if 'position' in s:
        for k, v in s['position'].items():
            if isinstance(v, str) and v:
                s['position'][k] = clean_english(clean_chinese(v))
            elif isinstance(v, list):
                s['position'][k] = [clean_english(clean_chinese(x)) if isinstance(x,str) else x for x in v]

# Fix 暴风湿气 → 暴风雨
for s in shots:
    if s.get('emotion_tone') == '暴风湿气前的平静':
        s['emotion_tone'] = '暴风雨前的平静'
    if s.get('emotion_tone') == '暴风湿气笼罩':
        s['emotion_tone'] = '暴风雨笼罩'

# ── FIX: Shot 10 (window) — ensure no rain references remain ──
s10 = next((s for s in shots if s['shot_index'] == 10), None)
if s10:
    s10['prompt'] = clean_english(clean_chinese(s10['prompt']))
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

# ── FIX: Shot 15 (glass crash) — fix any remaining rain ──
s15 = next((s for s in shots if s['shot_index'] == 15), None)
if s15:
    s15['prompt'] = clean_english(clean_chinese(s15['prompt']))
    s15['prompt'] = s15['prompt'].replace(
        'as they fall around her like frozen rain.',
        'as they scatter outward in slow arcs.'
    )

# ── FIX: Shot 18 ──
s18 = next((s for s in shots if s['shot_index'] == 18), None)
if s18:
    s18['prompt'] = clean_english(clean_chinese(s18['prompt']))
    s18['prompt'] = s18['prompt'].replace(
        'Her silver-dyed hair whips in the wind, soaking wet and plastered to the sides of her face.',
        'Her silver-dyed hair clings to her forehead, plastered to the sides of her face with sweat and condensation.'
    )

# ── Fix scenes ──
for scene in data.get('scenes', []):
    for k, v in scene.items():
        if isinstance(v, str):
            scene[k] = clean_english(clean_chinese(v))

# ── Fix character_tracking ──
for ck, cd in data.get('character_tracking', {}).items():
    for k, v in cd.items():
        if isinstance(v, str):
            cd[k] = clean_english(clean_chinese(v))

# ── Save ──
with open(FN, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Saved to', FN)
print()
for s in shots:
    print(f"  shot {s['shot_index']}: {s['scene']} | {s['time']} | seed={s['seed']}")
