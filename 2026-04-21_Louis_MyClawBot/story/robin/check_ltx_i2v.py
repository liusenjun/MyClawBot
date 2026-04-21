import json

with open(r"C:\Users\user.V915-31\Documents\ComfyUI\custom_nodes\ComfyUI-LTXVideo\example_workflows\2.3\LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json") as f:
    wf = json.load(f)

nodes = wf.get("nodes", [])
loader_types = ["Loader", "Load", "TextEncoder", "VAE", "Checkpoint", "Lora"]

for n in nodes:
    t = n.get("type", "")
    if any(x in t for x in loader_types):
        wv = n.get("widgets_values", [])
        print("Node", n["id"], t, ":", wv)
