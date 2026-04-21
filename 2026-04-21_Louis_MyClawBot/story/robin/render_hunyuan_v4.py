"""
HunyuanVideo T2V - 使用 easy hunyuanDiTLoader 一站式节点
"""
import sys, io, json, time, urllib.request
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\user\V915-31\Documents\ComfyUI\output"

PROMPT = (
    "A woman in black leather boots walks through a crowded Teahouse with predatory precision, "
    "low angle tracking shot from behind, warm amber lamplight, wet floor reflecting light, "
    "shallow depth of field, soft bokeh background of chattering diners, "
    "her silver-dyed hair wet and sticking to her face"
)

def build_hunyuan_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=42, steps=8, cfg=7.0):
    g = WorkflowGraph()

    # easy hunyuanDiTLoader - 一站式加载（model + vae + lora + conditioning）
    ltx_loader = g.node("easy hunyuanDiTLoader",
        ckpt_name="hunyuan_video_t2v_720p_bf16.safetensors",
        vae_name="hunyuan_video_vae_bf16.safetensors",
        lora_name="",
        lora_model_strength=1.0,
        lora_clip_strength=1.0,
        resolution="720",
        empty_latent_width=width,
        empty_latent_height=height,
        positive=prompt_pos,
        negative="blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render",
        batch_size=1,
    )

    # 从一站式节点取出各部分
    pipe = ltx_loader        # PIPE_LINE output
    model = g.node("easy hunyuanDiTLoader",
        ckpt_name="hunyuan_video_t2v_720p_bf16.safetensors",
        vae_name="hunyuan_video_vae_bf16.safetensors",
        lora_name="",
        lora_model_strength=1.0,
        lora_clip_strength=1.0,
        resolution="720",
        empty_latent_width=width,
        empty_latent_height=height,
        positive=prompt_pos,
        negative="blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render",
        batch_size=1,
    )
    # 只需要 MODEL 和 VAE
    model_out = g.node("easy hunyuanDiTLoader",
        ckpt_name="hunyuan_video_t2v_720p_bf16.safetensors",
        vae_name="hunyuan_video_vae_bf16.safetensors",
        lora_name="",
        lora_model_strength=1.0,
        lora_clip_strength=1.0,
        resolution="720",
        empty_latent_width=width,
        empty_latent_height=height,
        positive=prompt_pos,
        negative="blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render",
        batch_size=1,
    )

    # 简化：直接用 easy 节点的 PIPE_LINE 输出采样
    # KSampler - 直接用 model 的 CONDITIONING
    sampler = g.node("KSampler",
        model=pipe,  # 需要 MODEL 类型
        positive=prompt_pos,  # 字符串直接作为 prompt
        negative="blurry, low quality",
        latent_image=pipe,    # 需要 LATENT 类型
        seed=seed,
        steps=steps,
        cfg=cfg,
        sampler_name="euler",
        scheduler="normal",
    )

    # VAEDecode + Save
    decoded = g.node("VAEDecode", samples=sampler, vae=pipe)
    g.node("SaveImage", images=decoded, filename_prefix="hunyuan_v4")

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

    seed = 42
    print(f"Building HunyuanVideo workflow (v4 - easy node)...")
    print(f"  Prompt: {PROMPT[:80]}...")
    print()

    workflow = build_hunyuan_t2v(PROMPT, seed=seed)
    print("Submitting to ComfyUI...")
    try:
        outputs = submit_and_wait(workflow, timeout=1800)
    except TimeoutError as e:
        print(e)
    print(f"\nDone! Output: {OUTPUT_DIR}")
