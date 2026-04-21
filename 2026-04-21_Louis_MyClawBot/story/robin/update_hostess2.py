import json
FN = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json'
d = json.load(open(FN, encoding='utf-8'))
for shot in d['shots']:
    if shot['shot_index'] == 2:
        shot['ref_images'] = ['refs/hostess_three_views.png']
        shot['ref_images_logic'] = 'Hostess three-view sheet: middle-aged woman in crisp uniform, warm smile, bright welcoming gestures'
for key in list(d.get('character_tracking', {}).keys()):
    if key in ['领位员']:
        ct = d['character_tracking'][key]
        ct['name'] = 'Hostess阿姨'
        ct['shots'] = [2]
        ct['last_frame'] = 'Standing at Teahouse entrance, one hand on door frame, the other beckoning, bright smile in warm amber light'
with open(FN, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\diag_out.txt','w').write('OK')
