"""
Wan 2.2 T2V 渲染脚本 - 5秒 高清版
用法: python render_shot1.py "<prompt>" <seed>
"""
import sys, io, json, time
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph
import urllib.request, urllib.error

COMFYUI_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\user\V915-31\Documents\ComfyUI\output"

VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
NEGATIVE = "blurry, low quality, watermark, distorted, still frame, static, flickering"


def build_wan22_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=None, steps=8):
    """高质量 Wan 2.2 T2V - 5秒 1280x720"""
    if seed is None:
        seed = int(time.time() * 1000) % (2**32)

    g = WorkflowGraph()

    # 加载模型
    clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
    vae = g.node("VAELoader", vae_name=VAE)
    unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
    unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")

    # LoRA
    model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
    model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)

    # ModelSamplingSD3 (shift=5.0 for Wan 2.2)
    model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
    model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)

    # Conditioning
    cond_pos = g.node("CLIPTextEncode", text=prompt_pos, clip=clip)
    cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)

    # 隐空间 - 121帧 ≈ 5秒 @ 24fps
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)

    # High noise pass (step 0 -> 4)
    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_h, positive=cond_pos, negative=cond_neg, latent_image=latent,
        add_noise="enable", noise_seed=seed, steps=steps, cfg=1.0,
        sampler_name="euler", scheduler="simple",
        start_at_step=0, end_at_step=4, return_with_leftover_noise="enable",
    )

    # Low noise pass (step 4 -> steps)
    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_l, positive=cond_pos, negative=cond_neg, latent_image=after_denoise,
        add_noise="disable", noise_seed=seed, steps=steps, cfg=1.0,
        sampler_name="euler", scheduler="simple",
        start_at_step=4, end_at_step=steps, return_with_leftover_noise="disable",
    )

    # VAE 解码
    decoded = g.node("VAEDecode", samples=after_denoise, vae=vae)

    # 输出视频 - 24fps
    video = g.node("CreateVideo", images=decoded, fps=24)
    g.node("SaveVideo", video=video, filename_prefix="wan22_hq", format="mp4", codec="auto")

    return g.to_dict()


def submit_and_wait(workflow, prefix="wan22_hq", timeout=1200):
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_HOST}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"prompt_id: {prompt_id}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{COMFYUI_HOST}/history/{prompt_id}", timeout=15) as resp:
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
            print("Finished with status:", status)
            break
        time.sleep(10)

    raise TimeoutError(f"Timed out after {timeout}s")


if __name__ == "__main__":
    from pathlib import Path
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    prompt_text = sys.argv[1] if len(sys.argv) > 1 else "Hong Kong night street"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Building Wan 2.2 HQ workflow...")
    print(f"  Resolution: 1280x720")
    print(f"  Frames: 121 (~5s @ 24fps)")
    print(f"  Steps: 8")
    print()
    workflow = build_wan22_t2v(prompt_text, seed=seed)

    print("Submitting to ComfyUI...")
    outputs = submit_and_wait(workflow, timeout=1200)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\nDone! Output: {OUTPUT_DIR}")
