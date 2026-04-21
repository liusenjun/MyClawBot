#!/usr/bin/env python3
"""Shot 1 - Wan 2.2 I2V with dual-pass KSamplerAdvanced (same as 32dc96eb)"""
import sys, json, urllib.request, time
sys.path.insert(0, r'C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts')

from core import WorkflowGraph, upload_image, _submit_and_wait
from pathlib import Path

COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = Path(r'C:\Users\user.V915-31\Documents\ComfyUI\output')
IMAGE_PATH = r'C:\Users\user.V915-31\.openclaw\workspace\ref_shot1.png'

# Prompts
PROMPT = (
    "深水埗深夜街景，霓虹招牌红蓝闪烁，雨雾弥漫，地面湿滑泛着冷冽反光，"
    "街角茶餐厅门面，暖黄灯光从窗户透出，复古花砖地面，港风霓虹灯牌，"
    "湿润柏油路面倒映霓虹光，"
    "全景画面，固定机位，摄影机静止不动，"
    "cinematic film still photography, sharp focus, anamorphic bokeh, Hong Kong night market, 24fps"
)
NEGATIVE = (
    "blurry, low quality, watermark, distorted, still frame, flickering, noisy, grainy, "
    "washed out, cartoon, anime, day time, bright, crowd"
)

# Model files
VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"

SEED = 42
STEPS = 4

print(f"Uploading image: {IMAGE_PATH}")
server_img = upload_image(IMAGE_PATH)
print(f"Uploaded as: {server_img}")

g = WorkflowGraph()

# Load models
clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
vae = g.node("VAELoader", vae_name=VAE)
unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")

# LoRA (lightx2v for motion)
model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)

# ModelSamplingSD3 (shift=5.0 for Wan 2.2)
model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)

# Conditioning
cond_pos = g.node("CLIPTextEncode", text=PROMPT, clip=clip)
cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)

# Load image
img_node = g.node("LoadImage", image=server_img)

# WanFirstLastFrameToVideo (I2V latent)
wan_out = g.node("WanFirstLastFrameToVideo",
    positive=cond_pos,
    negative=cond_neg,
    vae=vae,
    width=1024,
    height=576,
    length=201,
    batch_size=1,
    start_image=img_node[0],
)

# KSamplerAdvanced - high noise pass (step 0 -> 2)
after_h = g.node("KSamplerAdvanced",
    model=model_h,
    positive=cond_pos,
    negative=cond_neg,
    latent_image=wan_out[2],
    add_noise="enable",
    noise_seed=SEED,
    steps=STEPS,
    cfg=1.0,
    sampler_name="euler",
    scheduler="simple",
    start_at_step=0,
    end_at_step=2,
    return_with_leftover_noise="enable",
)

# KSamplerAdvanced - low noise pass (step 2 -> 4)
after_l = g.node("KSamplerAdvanced",
    model=model_l,
    positive=cond_pos,
    negative=cond_neg,
    latent_image=after_h,
    add_noise="disable",
    noise_seed=SEED,
    steps=STEPS,
    cfg=1.0,
    sampler_name="euler",
    scheduler="simple",
    start_at_step=2,
    end_at_step=STEPS,
    return_with_leftover_noise="disable",
)

# VAE decode
decoded = g.node("VAEDecode", samples=after_l, vae=vae)

# VHS_VideoCombine (same as 32dc96eb)
g.node("VHS_VideoCombine",
    images=decoded,
    frame_rate=24,
    loop_count=0,
    filename_prefix="shot1_v2",
    format="video/h264-mp4",
    pingpong=False,
    save_output=True,
)

wf = g.to_dict()
print(f"Submitting {len(wf)} nodes (dual-pass KSamplerAdvanced, same as 32dc96eb)...")
prompt_id = _submit_and_wait(wf, OUTPUT_DIR, timeout=900)
print(f"Done! Prompt ID: {prompt_id}")
