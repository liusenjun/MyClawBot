import json, os

FN = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json'
OUT = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\diag_out.txt'
d=json.load(open(FN,encoding='utf-8'))
shots = d['shots']

# Find the two GRAB-U shots
grab_shots = [(i,s) for i,s in enumerate(shots) if 'snatches the USB' in s.get('prompt','')]
print('Grab-U shots found at indices:', [str(i)+'(shot#'+str(s['shot_index'])+')' for i,s in grab_shots])

# Remove the LAST one (keep the first)
if len(grab_shots) >= 2:
    dup_pos = grab_shots[-1][0]
    print('Removing duplicate at list position', dup_pos)
    shots.pop(dup_pos)

# Re-index
for i, s in enumerate(shots):
    s['shot_index'] = i + 1

print('After fix: total shots =', len(shots))

# Now run the fixes from fix_final.py (without inserting again)
import re

def clean_english(text):
    if not text: return text
    t = text
    t = re.sub(r'rain-slicked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-streaked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-soaked', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-swept', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-washed', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'rain-whipped', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'braindrops?', 'water drops', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy-', 'wet-', t, flags=re.IGNORECASE)
    t = re.sub(r'rainy', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\brain\b', 'wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRain\b', 'Wet', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRaining\b', 'Wetting', t, flags=re.IGNORECASE)
    t = re.sub(r'rain on', 'condensation on', t, flags=re.IGNORECASE)
    t = re.sub(r'rain light', 'wet light', t, flags=re.IGNORECASE)
    return t

def clean_chinese(text):
    if not text: return text
    t = text
    t = t.replace('雨雾', '雾气')
    t = t.replace('雨声', '凝结声')
    t = t.replace('雨滴', '水滴')
    t = t.replace('雨水无声滑落', '水汽无声滑落')
    t = t.replace('雨水在车轮下飞溅', '水洼中的积水在车轮下飞溅')
    t = t.replace('雨水顺着玻璃流淌', '水汽凝结流淌')
    return t

# FIX Shot 6 — Uncle Fat Mandarin dialogue
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
s6['audio_cue'] = "肥叔普通话：东西全部都在这里面了。这个刹车要是踩下去，整个香港会有场好戏。+ 瓷器轻碰声"
s6['emotion_tone'] = "日常感，暗流涌动"
print("Shot 6 dialogue fixed")

# Apply cleaning to all shots
for s in shots:
    for field in ['prompt','audio_cue','transition_hint','camera_move','emotion_tone','ref_images_logic']:
        if isinstance(s.get(field), str):
            s[field] = clean_english(clean_chinese(s[field]))
    if 'position' in s:
        for k,v in s['position'].items():
            if isinstance(v,str):
                s['position'][k] = clean_english(clean_chinese(v))
            elif isinstance(v,list):
                s['position'][k] = [clean_english(clean_chinese(x)) if isinstance(x,str) else x for x in v]

# Restore 暴风雨 metaphor
for s in shots:
    if s.get('emotion_tone') == '暴风湿气前的平静':
        s['emotion_tone'] = '暴风雨前的平静'

# Fix shot 10 window
s10 = next((s for s in shots if s['shot_index']==10), None)
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

# Fix shot 15 (glass crash)
s15 = next((s for s in shots if s['shot_index']==15), None)
if s15:
    s15['prompt'] = s15['prompt'].replace(
        'as they fall around her like frozen rain.',
        'as they scatter outward in slow arcs.'
    )

# Fix shot 18
s18 = next((s for s in shots if s['shot_index']==18), None)
if s18:
    s18['prompt'] = s18['prompt'].replace(
        'Her silver-dyed hair whips in the wind, soaking wet and plastered to the sides of her face.',
        'Her silver-dyed hair clings to her forehead, plastered to the sides of her face with sweat and condensation.'
    )

# Clean scenes
for scene in d.get('scenes', []):
    for k,v in scene.items():
        if isinstance(v,str):
            scene[k] = clean_english(clean_chinese(v))

# Clean character_tracking
for ck,cd in d.get('character_tracking',{}).items():
    for k,v in cd.items():
        if isinstance(v,str):
            cd[k] = clean_english(clean_chinese(v))

# Write
with open(FN,'w',encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# Print summary
lines = ['After fix: total shots = ' + str(len(shots))]
for s in shots:
    lines.append(str(s['shot_index']).rjust(2) + ' ' + s['scene'] + ' | ' + s['time'])
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print('Saved. Summary written.')
