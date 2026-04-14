import json, urllib.request, urllib.error

COMFYUI_HOST = "http://127.0.0.1:8188"

def post_json(path, data):
    req = urllib.request.Request(
        f"{COMFYUI_HOST}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise Exception(f"HTTP {e.code}: {body[:500]}")

# 测试 VAELoader
prompt = {
    "prompt": {
        "1": {
            "inputs": {"vae_name": "wan_2.1_vae.safetensors"},
            "class_type": "VAELoader"
        }
    }
}

print("Testing VAELoader...")
try:
    result = post_json("/api/prompt", prompt)
    print("OK:", result)
except Exception as e:
    print("Error:", e)
