import json

with open(r"C:\Users\user.V915-31\Documents\comfyui-git\blueprints\Text to Video (Wan 2.2).json", encoding="utf-8") as f:
    bp = json.load(f)

# Get all unique node types used
nodes = bp.get("nodes", [])
print(f"Total nodes: {len(nodes)}")
types = set()
for n in nodes:
    types.add(n.get("type"))
print("Unique types:")
for t in sorted(types):
    print(f"  {t}")

print()

# Print first 5 nodes in detail
for n in nodes[:5]:
    print(f"\nNode {n['id']}: type={n.get('type')}")
    print(f"  inputs: {json.dumps(n.get('inputs', {}), indent=2)[:500]}")
    print(f"  outputs: {n.get('outputs', [])}")
