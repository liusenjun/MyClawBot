import json, os

FN = r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\storyboard_v2.json'
d = json.load(open(FN, encoding='utf-8'))

# Update character_tracking for 领位员
if '领位员' in d.get('character_tracking', {}):
    d['character_tracking']['领位员']['name'] = '领位员阿姨'
    d['character_tracking']['领位员']['appearance'] = {
        'body': '中年女性，身材微胖，穿着整洁的餐厅制服',
        'expression': '笑容真诚热情，手势明亮有力',
        'gesture': '手势大而明亮，常用右手比划'
    }
    d['character_tracking']['领位员']['shots'] = [2]

# Update shot 2 — add hostess reference
for shot in d['shots']:
    if shot['shot_index'] == 2:
        shot['ref_images'] = ['refs/hostess_three_views.png']
        shot['ref_images_logic'] = '领位员三视图，确保中年女性制服形象一致性'
        shot['characters'] = ['领位员']
        print(f"Shot 2 ref_images updated: {shot['ref_images']}")
        print(f"Shot 2 characters: {shot['characters']}")

with open(FN, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('Saved')
