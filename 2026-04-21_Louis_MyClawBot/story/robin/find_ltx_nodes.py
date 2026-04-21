import json

path = r'C:\Users\user.V915-31\Documents\ComfyUI\custom_nodes\ComfyUI-LTXVideo\example_workflows\2.3\LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json'
with open(path) as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
for node in nodes:
    ct = node.get('type', '')
    if any(x in ct for x in ['VAE', 'Loader', 'Decode', 'Sampler']):
        print(f'Node {node.get("id")}: {ct}')
        print(f'  Inputs: {json.dumps(node.get("inputs", {}), ensure_ascii=False)[:500]}')
        print()
