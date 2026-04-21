import json

path = r'C:\Users\user.V915-31\Documents\ComfyUI\custom_nodes\ComfyUI-LTXVideo\example_workflows\2.3\LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json'
with open(path) as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
for node in nodes:
    if node.get('type') == 'CheckpointLoaderSimple':
        print('Full node:')
        print(json.dumps(node, ensure_ascii=False, indent=2)[:2000])
        break
