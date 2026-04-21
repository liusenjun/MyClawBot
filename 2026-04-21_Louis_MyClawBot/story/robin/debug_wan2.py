import sys, io, json, urllib.request
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"

PROMPT = (
    "A woman in black leather boots walks through a crowded Teahouse with predatory precision, "
    "warm amber lamplight, wet floor reflecting light, her silver hair wet and sticking to her face, "
    "shallow depth of field, soft bokeh background of chattering diners"
)

VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
NEGATIVE = "blurry, low quality, watermark, distorted, still frame"

g = WorkflowGraph()
clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
vae = g.node("VAELoader", vae_name=VAE)
unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")
model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)
model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)
cond_pos = g.node("CLIPTextEncode", text=PROMPT, clip=clip)
cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)
latent = g.node("EmptyHunyuanLatentVideo", width=1280, height=720, length=121, batch_size=1)
after_denoise = g.node("KSamplerAdvanced", model=model_h, positive=cond_pos, negative=cond_neg,
    latent_image=latent, add_noise="enable", noise_seed=42, steps=8, cfg=1.0,
    sampler_name="euler", scheduler="simple", start_at_step=0, end_at_step=2,
    return_with_leftover_noise="enable")
after_denoise = g.node("KSamplerAdvanced", model=model_l, positive=cond_pos, negative=cond_neg,
    latent_image=after_denoise, add_noise="disable", noise_seed=42, steps=8, cfg=1.0,
    sampler_name="euler", scheduler="simple", start_at_step=2, end_at_step=8,
    return_with_leftover_noise="disable")
decoded = g.node("VAEDecode", samples=after_denoise, vae=vae)
# Add SaveImage to ensure workflow has visible output
g.node("SaveImage", images=decoded, filename_prefix="cmp4_wan22_v2")

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
        print("ERROR:", json.dumps(err, indent=2, ensure_ascii=False)[:2000])
    except:
        print("HTTP", e.code, body[:800])
