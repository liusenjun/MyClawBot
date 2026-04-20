import json

# Check the latent upsample model path from the 2.3 workflow
path = r'C:\Users\user.V915-31\Documents\ComfyUI\custom_nodes\ComfyUI-LTXVideo\example_workflows\2.3\LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json'
with open(path) as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])

# Find latent upsample and other model nodes
for node in nodes:
    ct = node.get('type', '')
    if 'Latent' in ct or 'Upscale' in ct or 'Loader' in ct:
        print(f'Node {node.get("id")}: {ct}')
        print(f'  Properties: {json.dumps(node.get("properties", {}), ensure_ascii=False)}')
        print()
