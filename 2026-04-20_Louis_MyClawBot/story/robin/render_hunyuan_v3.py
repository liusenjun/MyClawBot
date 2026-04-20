"""
HunyuanVideo T2V - 最简版（去掉 negative 避免 CLIP 不兼容问题）
"""
import sys, io, json, time, urllib.request
from pathlib import Path
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\user\V915-31\Documents\ComfyUI\output"

MODEL = "hunyuan_video_t2v_720p_bf16.safetensors"
VAE = "hunyuan_video_vae_bf16.safetensors"

PROMPT = (
    "A woman in black leather boots walks through a crowded Teahouse with predatory precision, "
    "low angle tracking shot from behind, warm amber lamplight, wet floor reflecting light, "
    "shallow depth of field, soft bokeh background of chattering diners, "
    "her silver-dyed hair wet and sticking to her face"
)

def build_hunyuan_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=42, steps=8, cfg=7.0):
    g = WorkflowGraph()

    # CLIP - 用 DualCLIPLoader（hunyuan_video type）
    dual_clip = g.node("DualCLIPLoader",
        clip_name1="llava_llama3_fp8_scaled.safetensors",
        clip_name2="umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        type="hunyuan_video",
    )

    vae = g.node("VAELoader", vae_name=VAE)
    unet = g.node("UNETLoader", unet_name=MODEL, weight_dtype="default")

    # Positive conditioning - Hunyuan 专用节点
    cond_pos = g.node("CLIPTextEncodeHunyuanDiT", clip=dual_clip,
        bert=prompt_pos, mt5xl=prompt_pos)

    # 隐空间
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)

    # Denoise（不接 negative conditioning）
    after_denoise = g.node(
        "KSamplerAdvanced",
        model=unet, positive=cond_pos, negative=None, latent_image=latent,
        add_noise="enable", noise_seed=seed, steps=steps, cfg=cfg,
        sampler_name="euler", scheduler="normal",
        start_at_step=0, end_at_step=steps, return_with_leftover_noise="disable",
    )

    # 解码 + 保存
    video = g.node("DecodeAndSaveVideo",
        video_latent=after_denoise,
        fps=24.0,
        filename_prefix="hunyuan_v3",
        format="auto",
        codec="auto",
        video_vae=vae,
        tiling="disabled",
    )

    return g.to_dict()


def submit_and_wait(workflow, timeout=1800):
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{HOST}/prompt", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"prompt_id: {prompt_id}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{HOST}/history/{prompt_id}", timeout=15) as resp:
            hist = json.loads(resp.read())
        entry = hist.get(prompt_id, {})
        outputs = entry.get("outputs", {})
        status = (entry.get("status") or {}).get("status_str") or (entry.get("status") or {}).get("status", "")
        print(f"[{status}]")
        if outputs:
            for node_output in outputs.values():
                for key, val in node_output.items():
                    if isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict) and "filename" in item:
                                print(f"  -> {item['filename']}")
            return outputs
        if status in ("error", "completed") and not outputs:
            break
        time.sleep(15)
    raise TimeoutError(f"Timed out after {timeout}s")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    steps = 8
    cfg = 7.0
    print(f"Building HunyuanVideo workflow (v3 - no negative)...")
    print(f"  Prompt: {PROMPT[:80]}...")
    print(f"  Resolution: 1280x720, Frames: 121, Steps: {steps}, CFG: {cfg}, Seed: {seed}")
    print()

    workflow = build_hunyuan_t2v(PROMPT, seed=seed)
    print("Submitting to ComfyUI...")
    outputs = submit_and_wait(workflow, timeout=1800)
    print(f"\nDone! Output: {OUTPUT_DIR}")
