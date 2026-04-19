import json

with open(r"C:\Users\user.V915-31\Documents\comfyui-git\blueprints\Text to Video (Wan 2.2).json", encoding="utf-8") as f:
    bp = json.load(f)

print("Top-level keys:", list(bp.keys()))
nodes = bp.get("nodes", [])
print(f"nodes type: {type(nodes)}, count: {len(nodes)}")
if nodes:
    print("First node:", json.dumps(nodes[0], indent=2)[:500])
