import urllib.request, json

HOST = 'http://127.0.0.1:8188'

# Try different endpoints
for ep in ['/object_info/hunyuan', '/object_info/HunyuanDiTLoader', '/object_info/CLIPTextEncodeHunyuanDiT']:
    try:
        with urllib.request.urlopen(HOST + ep, timeout=10) as r:
            info = json.loads(r.read())
        name = list(info.keys())[0]
        inp = info[name].get('input', {}).get('required', {})
        out = info[name].get('output', [])
        print(f"\n{ep} -> {name}")
        print(f"  inputs: {list(inp.keys())}")
        print(f"  output: {out}")
    except Exception as e:
        print(f"{ep}: {e}")
