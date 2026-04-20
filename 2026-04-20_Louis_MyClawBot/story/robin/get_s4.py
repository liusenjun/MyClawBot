import json, sys
sys.stdout = open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\diag_out.txt', 'w', encoding='utf-8')
d = json.load(open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json', encoding='utf-8'))
s4 = [s for s in d['shots'] if s['shot_index']==4][0]
print('Shot 4 prompt:', s4['prompt'])
print('Scene:', s4['scene'])
print('Time:', s4['time'])
