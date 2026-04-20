import json, sys
d=json.load(open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json',encoding='utf-8'))
print('Total:', len(d['shots']))
for s in d['shots']:
    idx = s['shot_index']
    scene = s['scene']
    time = s['time']
    sys.stdout.write(f'{idx} {scene} {time}\n')
