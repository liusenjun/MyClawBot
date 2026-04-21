"""
Shot 4 - Wan 2.2 简化 prompt 版
对比用：去掉所有电影/音频描述，只保留视觉主体+动作+氛围
"""
import sys, io, json, time, urllib.request
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\user\V915-31\Documents\ComfyUI\output"

# 简化版 prompt - 只保留视觉描述
PROMPT = (
    "A woman in black leather boots walks through a crowded Teahouse with predatory precision, "
    "warm amber lamplight, wet floor reflecting light, her silver hair wet and sticking to her face, "
    "shallow depth of field, soft bokeh background of chattering diners"
)

# 模型
VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
NEGATIVE = "blurry, low quality, watermark, distorted, still frame"


def build_wan22_t2v(prompt_pos: str, width=1280, height=720, num_frames=121, seed=None, steps=8):
    g = WorkflowGraph()

    clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
    vae = g.node("VAELoader", vae_name=VAE)
    unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
    unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")

    model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
    model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)

    model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
    model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)

    cond_pos = g.node("CLIPTextEncode", text=prompt_pos, clip=clip)
    cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)

    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)

    if seed is None:
        seed = int(time.time() * 1000) % (2**32)

    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_h,
        positive=cond_pos,
        negative=cond_neg,
        latent_image=latent,
        add_noise="enable",
        noise_seed=seed,
        steps=steps,
        cfg=1.0,
        sampler_name="euler",
        scheduler="simple",
        start_at_step=0,
        end_at_step=2,
        return_with_leftover_noise="enable",
    )

    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_l,
        positive=cond_pos,
        negative=cond_neg,
        latent_image=after_denoise,
        add_noise="disable",
        noise_seed=seed,
        steps=steps,
        cfg=1.0,
        sampler_name="euler",
        scheduler="simple",
        start_at_step=2,
        end_at_step=steps,
        return_with_leftover_noise="disable",
    )

    decoded = g.node("VAEDecode", samples=after_denoise, vae=vae)
    g.node("CreateVideo", images=decoded, fps=24, filename_prefix="cmp4_wan22_simple")

    return g.to_dict()


def submit_and_wait(workflow, timeout=1200):
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
        status = (entry.get("status") or {}).get("status_str", "")
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
    print(f"Building Wan 2.2 workflow (simplified prompt)...")
    print(f"  Prompt: {PROMPT[:80]}...")
    print()

    workflow = build_wan22_t2v(PROMPT, seed=seed)
    print("Submitting to ComfyUI...")
    try:
        outputs = submit_and_wait(workflow, timeout=1200)
        print(f"\nDone!")
    except TimeoutError as e:
        print(e)
