import json
d=json.load(open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json',encoding='utf-8'))
s2=[s for s in d['shots'] if s['shot_index']==2][0]
open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\diag_out.txt','w',encoding='utf-8').write(
    'ref_images: ' + str(s2['ref_images']) + '\nchars: ' + str(s2['characters'])
)
