"""
Debug: 完整 Wan 2.2 workflow
"""
import sys, io, json
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

VAE = "wan_2.1_vae.safetensors"
HIGH_UNET = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
LOW_UNET = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
LORA_HIGH = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
LORA_LOW = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"


def build_wan22_t2v():
    g = WorkflowGraph()

    clip = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
    vae = g.node("VAELoader", vae_name=VAE)
    unet_h = g.node("UNETLoader", unet_name=HIGH_UNET, weight_dtype="default")
    unet_l = g.node("UNETLoader", unet_name=LOW_UNET, weight_dtype="default")
    model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_HIGH, strength_model=1.0)
    model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_LOW, strength_model=1.0)
    model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
    model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)
    cond_pos = g.node("CLIPTextEncode", text="Hong Kong night street", clip=clip)
    cond_neg = g.node("CLIPTextEncode", text="blurry, low quality", clip=clip)
    latent = g.node("EmptyHunyuanLatentVideo", width=768, height=512, length=49, batch_size=1)

    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_h, positive=cond_pos, negative=cond_neg, latent_image=latent,
        add_noise="enable", noise_seed=1234, steps=4, cfg=1.0,
        sampler_name="euler", scheduler="simple",
        start_at_step=0, end_at_step=2, return_with_leftover_noise="enable",
    )

    after_denoise = g.node(
        "KSamplerAdvanced",
        model=model_l, positive=cond_pos, negative=cond_neg, latent_image=after_denoise,
        add_noise="disable", noise_seed=1234, steps=4, cfg=1.0,
        sampler_name="euler", scheduler="simple",
        start_at_step=2, end_at_step=4, return_with_leftover_noise="disable",
    )

    decoded = g.node("VAEDecode", samples=after_denoise, vae=vae)
    video = g.node("CreateVideo", images=decoded, fps=24)
    g.node("SaveVideo", video=video, filename_prefix="wan22_test", format="mp4", codec="auto")

    return g.to_dict()


if __name__ == "__main__":
    import urllib.request, urllib.error

    workflow = build_wan22_t2v()

    # Print full JSON for inspection
    print("Node count:", len(workflow))
    for nid, n in workflow.items():
        inputs = n.get("inputs", {})
        if isinstance(inputs, dict):
            for k, v in inputs.items():
                if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str):
                    inputs[k] = f"[link->{v[0]}]"
        print(f"  {nid}: {n['class_type']} -> {inputs}")

    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            print("\nOK! prompt_id:", result.get("prompt_id"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"\nHTTP {e.code}: {body[:800]}")
