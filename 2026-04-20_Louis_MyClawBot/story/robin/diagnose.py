import json, os
FN = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json'
OUT = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\diag_out.txt'
d=json.load(open(FN,encoding='utf-8'))
lines = []
lines.append('Total shots: ' + str(len(d['shots'])))
for s in d['shots']:
    idx = s['shot_index']
    scene = s['scene']
    grab = 'snatches the USB' in s.get('prompt','')
    grab_str = ' [GRAB-U]' if grab else ''
    lines.append(str(idx).rjust(2) + ' ' + scene + grab_str)
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
