import json

with open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json', encoding='utf-8') as f:
    sb = json.load(f)

shots = sb.get('shots', [])
print(f'Total shots: {len(shots)}')
for s in shots:
    if s.get('shot_index') == 4 or s.get('shot_number') == 4:
        print('\nShot 4 found:')
        print('prompt:', s.get('prompt', 'N/A')[:300])
        print('scene:', s.get('scene', 'N/A'))
        print('shot_type:', s.get('shot_type', 'N/A'))
        print('emotion_tone:', s.get('emotion_tone', 'N/A'))
        break
else:
    print('Shot with index/number 4 not found')
    if shots:
        print('First shot index:', shots[0].get('shot_index'))
        print('All shot indices:', [s.get('shot_index') for s in shots])
