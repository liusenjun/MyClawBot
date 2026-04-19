import sys, json, urllib.request
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"

g = WorkflowGraph()

# CLIP
clip = g.node("DualCLIPLoader",
    clip_name1="llava_llama3_fp8_scaled.safetensors",
    clip_name2="umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    type="hunyuan_video",
)

# Text encoding
cond = g.node("CLIPTextEncodeHunyuanDiT",
    clip=clip,
    bert="A woman walks through a crowded Teahouse, warm amber lamplight, wet floor reflecting light",
    mt5xl="A woman walks through a crowded Teahouse, warm amber lamplight, wet floor reflecting light",
)

neg = g.node("CLIPTextEncode",
    clip=clip,
    text="blurry, low quality, watermark, distorted, still frame",
)

# Model + Sampler (use the known-working approach from render_hunyuan.py)
model = g.node("ModelSamplingDiscrete",
    model="hunyuan",  # won't work but let's see
    sampling="euler",
    sigma_shift=0.029,
)

# Empty latent
empty = g.node("EmptyHunyuanLatentVideo",
    width=1280,
    height=720,
    length=121,
    batch_size=1,
)

# KSampler
sampled = g.node("KSamplerAdvanced",
    model=model,
    seed=42,
    steps=8,
    cfg=7.0,
    sampler_name="euler",
    scheduler="normal",
    positive=cond,
    negative=neg,
    latent_image=empty,
    denoise=1.0,
)

# Decode
decoded = g.node("VAEDecode", samples=sampled, vae=clip)

# Save
g.node("SaveImage", images=decoded, filename_prefix="test_hunyuan")

wf = g.to_dict()
payload = json.dumps({"prompt": wf}).encode("utf-8")
req = urllib.request.Request(HOST + "/prompt", data=payload,
    headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print("SUCCESS! prompt_id:", result.get("prompt_id"))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    try:
        err = json.loads(body)
        print("ERROR:", json.dumps(err, indent=2, ensure_ascii=False)[:1000])
    except:
        print("HTTP", e.code, body[:400])
