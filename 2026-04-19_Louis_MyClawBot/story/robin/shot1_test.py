#!/usr/bin/env python3
"""Shot 1 - Wan 2.2 I2V Test"""
import sys, json, urllib.request, time
sys.path.insert(0, r'C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts')

from core import WorkflowGraph, upload_image, _submit_and_wait
from pathlib import Path

COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = Path(r'C:\Users\user.V915-31\Documents\ComfyUI\output')
IMAGE_PATH = r'C:\Users\user.V915-31\.openclaw\workspace\ref_shot1.png'

PROMPT = (
    "香港深水埗深夜街景，霓虹招牌红蓝闪烁，雨雾弥漫，地面湿滑泛着冷冽反光，"
    "街角茶餐厅门面，暖黄灯光从窗户透出，复古花砖地面，港风霓虹灯牌，"
    "湿润柏油路面倒映霓虹光，"
    "全景画面，固定机位，摄影机静止不动，"
    "cinematic film still photography, sharp focus, anamorphic bokeh, Hong Kong night market, 24fps"
)
NEGATIVE = (
    "blurry, low quality, watermark, distorted, still frame, flickering, noisy, grainy, "
    "washed out, cartoon, anime, day time, bright, crowd, camera shake, pan, tilt, zoom"
)

print(f"Uploading image: {IMAGE_PATH}")
server_img = upload_image(IMAGE_PATH)
print(f"Uploaded as: {server_img}")

VAE = "wan_2.1_vae.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"

g = WorkflowGraph()
clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
vae = g.node("VAELoader", vae_name=VAE)
cond_pos = g.node("CLIPTextEncode", text=PROMPT, clip=clip)
cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)
img_node = g.node("LoadImage", image=server_img)

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

decoded = g.node("VAEDecode", samples=wan_out[2], vae=vae)

g.node("VHS_VideoCombine",
    images=decoded,
    frame_rate=24,
    loop_count=0,
    filename_prefix="shot1_test",
    format="video/h264-mp4",
    pingpong=False,
    save_output=True,
)

wf = g.to_dict()
print(f"Submitting {len(wf)} nodes...")
prompt_id = _submit_and_wait(wf, OUTPUT_DIR, timeout=900)
print(f"Done! Prompt ID: {prompt_id}")
