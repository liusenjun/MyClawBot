"""
Wan 2.2 T2V via ComfyUI API - 使用 WorkflowGraph 格式
"""
import sys, time, json, io
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph, _submit_and_wait

# Fix stdout encoding for Chinese
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

OUTPUT_DIR = r"C:\Users\user.V915-31\Documents\ComfyUI\output"
INPUT_DIR = r"C:\Users\user.V915-31\Documents\ComfyUI\input\robin"

# 模型文件名
VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"

# 负向提示词
NEGATIVE = "blurry, low quality, watermark, distorted, still frame"


def build_wan22_t2v(prompt_pos: str, width=768, height=512, num_frames=49, seed=None, steps=4):
    g = WorkflowGraph()

    # 加载模型
    clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
    vae = g.node("VAELoader", vae_name=VAE)
    unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
    unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")

    # LoRA
    model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
    model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)

    # ModelSamplingSD3 (shift=5.0 for Wan)
    model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
    model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)

    # Conditioning
    cond_pos = g.node("CLIPTextEncode", text=prompt_pos, clip=clip)
    cond_neg = g.node("CLIPTextEncode", text=NEGATIVE, clip=clip)

    # 隐空间
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)

    if seed is None:
        seed = int(time.time() * 1000) % (2**32)

    # High noise pass (step 0 -> 2)
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

    # Low noise pass (step 2 -> steps)
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

    # VAE 解码
    decoded = g.node("VAEDecode", samples=after_denoise, vae=vae)

    # 输出视频
    g.node("CreateVideo", images=decoded, fps=24)

    return g.to_dict()


if __name__ == "__main__":
    from pathlib import Path

    prompt_text = sys.argv[1] if len(sys.argv) > 1 else "Hong Kong night street"
    prefix = sys.argv[2] if len(sys.argv) > 2 else "wan22_test"
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None

    print("Building workflow...")
    workflow = build_wan22_t2v(prompt_text, seed=seed)

    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Submitting to ComfyUI...")
    _submit_and_wait(workflow, output_path, timeout=600)
    print("Done!")
