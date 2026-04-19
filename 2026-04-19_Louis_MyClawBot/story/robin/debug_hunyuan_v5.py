import sys, io, json, urllib.request, traceback
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"

PROMPT = "A woman in black leather boots walks through a crowded Teahouse with predatory precision, low angle tracking shot from behind, warm amber lamplight, wet floor reflecting light, shallow depth of field, soft bokeh background of chattering diners, her silver-dyed hair wet and sticking to her face"

def build_hunyuan_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=42, steps=8, cfg=7.0):
    g = WorkflowGraph()
    loader = g.node("easy hunyuanDiTLoader",
        ckpt_name="hunyuan_video_t2v_720p_bf16.safetensors",
        vae_name="Baked VAE",
        lora_name="None",
        lora_model_strength=1.0,
        lora_clip_strength=1.0,
        resolution="1280 x 720",
        empty_latent_width=width,
        empty_latent_height=height,
        positive=prompt_pos,
        negative="blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render",
        batch_size=1,
    )
    sampled = g.node("KSampler",
        model=loader[1],
        seed=seed,
        steps=steps,
        cfg=cfg,
        sampler_name="euler",
        scheduler="normal",
        positive=loader[4],
        negative=loader[5],
        latent_image=loader[6],
        denoise=1.0,
    )
    decoded = g.node("VAEDecode", samples=sampled, vae=loader[2])
    g.node("SaveImage", images=decoded, filename_prefix="hunyuan_v5")
    return g.to_dict()

try:
    workflow = build_hunyuan_t2v(PROMPT, seed=42)
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(HOST + "/prompt", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print("prompt_id:", result.get("prompt_id"))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print("HTTP", e.code)
    try:
        err = json.loads(body)
        print(json.dumps(err, indent=2, ensure_ascii=False)[:1000])
    except:
        print(body[:500])
except Exception as e:
    traceback.print_exc()
