import json

path = r'C:\Users\user.V915-31\Documents\ComfyUI\custom_nodes\ComfyUI-LTXVideo\example_workflows\2.3\LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json'
with open(path) as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])

for node in nodes:
    if node.get('id') in ['3940', '4010']:
        print(f'Node {node.get("id")}: {node.get("type")}')
        print(f'  Properties: {json.dumps(node.get("properties", {}), ensure_ascii=False)}')
        print(f'  Outputs: {json.dumps(node.get("outputs", []), ensure_ascii=False)[:200]}')
        print()
