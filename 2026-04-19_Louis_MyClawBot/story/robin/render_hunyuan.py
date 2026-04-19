"""
HunyuanVideo T2V 渲染脚本 - 正确版（DualCLIPLoader）
用法: python render_hunyuan.py "<prompt>" <seed>
"""
import sys, io, json, time
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph
import urllib.request

COMFYUI_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\user\V915-31\Documents\ComfyUI\output"

MODEL = "hunyuan_video_t2v_720p_bf16.safetensors"
VAE = "hunyuan_video_vae_bf16.safetensors"
NEGATIVE = "blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render"


def build_hunyuan_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=None, steps=8, cfg=7.0):
    """HunyuanVideo T2V - 5秒 1280x720"""
    if seed is None:
        seed = int(time.time() * 1000) % (2**32)

    g = WorkflowGraph()

    # DualCLIPLoader - 加载两个 CLIP：llava（图像+文本）和 umt5（文本编码）
    # type='hunyuan_video' 让它输出支持 bert + mt5xl 双 tokenizer
    clip = g.node("DualCLIPLoader",
        clip_name1="llava_llama3_fp8_scaled.safetensors",
        clip_name2="umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        type="hunyuan_video",
    )

    vae = g.node("VAELoader", vae_name=VAE)
    unet = g.node("UNETLoader", unet_name=MODEL, weight_dtype="default")

    # Hunyuan 专用 encoder（需要 bert + mt5xl 双输入）
    cond_pos = g.node("CLIPTextEncodeHunyuanDiT", clip=clip,
        bert=prompt_pos, mt5xl=prompt_pos)

    # 负 prompt 用标准 CLIPTextEncode
    cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)

    # 隐空间
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)

    # Denoise
    after_denoise = g.node(
        "KSamplerAdvanced",
        model=unet, positive=cond_pos, negative=cond_neg, latent_image=latent,
        add_noise="enable", noise_seed=seed, steps=steps, cfg=cfg,
        sampler_name="euler", scheduler="normal",
        start_at_step=0, end_at_step=steps, return_with_leftover_noise="disable",
    )

    # 解码 + 保存
    video = g.node("DecodeAndSaveVideo",
        video_latent=after_denoise,
        fps=24.0,
        filename_prefix="hunyuan_test",
        format="auto",
        codec="auto",
        video_vae=vae,
        tiling="disabled",
    )

    return g.to_dict()


def submit_and_wait(workflow, prefix="hunyuan_test", timeout=1800):
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
        time.sleep(15)

    raise TimeoutError(f"Timed out after {timeout}s")


if __name__ == "__main__":
    from pathlib import Path
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    prompt_text = sys.argv[1] if len(sys.argv) > 1 else "A woman walks through rain-slicked Hong Kong street at night, neon lights reflecting off wet pavement, cinematic"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Building HunyuanVideo workflow...")
    print(f"  Resolution: 1280x720")
    print(f"  Frames: 121 (~5s @ 24fps)")
    print(f"  Steps: 8, CFG: 7.0")
    print()
    workflow = build_hunyuan_t2v(prompt_text, seed=seed)

    print("Submitting to ComfyUI...")
    outputs = submit_and_wait(workflow, timeout=1800)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\nDone! Output: {OUTPUT_DIR}")
