import json

with open(r'C:\Users\user\V915-31\Documents\comfyui-git\blueprints\Text to Video (Wan 2.2).json', encoding='utf-8') as f:
    blueprint = json.load(f)

nodes = blueprint['definitions']['subgraphs'][0]['nodes']

# Find the input node (PrimitiveNode with prompt text)
for nid, n in nodes.items():
    if n.get('type') == 'PrimitiveNode':
        print(f'Primitive Node {nid}: {n.get("widgets_values", [])}')
