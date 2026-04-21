import os

save_path = r"C:\Users\user.V915-31\Documents\ComfyUI\models"
torrent_files = [
    "text_encoders/gemma_3_12B_it_fp8_e4m3fn.safetensors",
    "diffusion_models/ltx-2-19b-distilled_Q4_K_M.gguf",
    "latent_upscale_models/ltx-2-spatial-upscaler-x2-1.0.safetensors",
    "loras/ltx-2-19b-distilled-lora-384.safetensors",
    "loras/ltx-2-19b-ic-lora-detailer.safetensors",
    "loras/ltx-2-19b-lora-camera-control-dolly-in.safetensors",
    "loras/ltx-2-19b-lora-camera-control-dolly-left.safetensors",
    "loras/ltx-2-19b-lora-camera-control-dolly-right.safetensors",
    "loras/ltx-2-19b-lora-camera-control-jib-down.safetensors",
    "loras/ltx-2-19b-lora-camera-control-jib-up.safetensors",
    "loras/ltx-2-19b-lora-camera-control-static.safetensors",
    "diffusion_models/flux-2-klein-4b-fp8.safetensors",
    "text_encoders/ltx-2-19b-embeddings_connector_distill_bf16.safetensors",
    "text_encoders/qwen_3_4b.safetensors",
    "vae/flux2-vae.safetensors",
    "vae/LTX2_audio_vae_bf16.safetensors",
    "vae/LTX2_video_vae_bf16.safetensors",
]

expected_sizes = {
    "text_encoders/gemma_3_12B_it_fp8_e4m3fn.safetensors": 12.65,
    "diffusion_models/ltx-2-19b-distilled_Q4_K_M.gguf": 1.00,
    "latent_upscale_models/ltx-2-spatial-upscaler-x2-1.0.safetensors": 7.67,
    "loras/ltx-2-19b-distilled-lora-384.safetensors": 2.62,
    "loras/ltx-2-19b-ic-lora-detailer.safetensors": 0.33,
    "loras/ltx-2-19b-lora-camera-control-dolly-in.safetensors": 0.33,
    "loras/ltx-2-19b-lora-camera-control-dolly-left.safetensors": 0.33,
    "loras/ltx-2-19b-lora-camera-control-dolly-right.safetensors": 2.21,
    "loras/ltx-2-19b-lora-camera-control-jib-down.safetensors": 2.21,
    "loras/ltx-2-19b-lora-camera-control-jib-up.safetensors": 2.21,
    "loras/ltx-2-19b-lora-camera-control-static.safetensors": 4.07,
    "diffusion_models/flux-2-klein-4b-fp8.safetensors": 2.86,
    "text_encoders/ltx-2-19b-embeddings_connector_distill_bf16.safetensors": 8.04,
    "text_encoders/qwen_3_4b.safetensors": 0.34,
    "vae/flux2-vae.safetensors": 0.22,
    "vae/LTX2_audio_vae_bf16.safetensors": 2.45,
    "vae/LTX2_video_vae_bf16.safetensors": 1.56,
}

for f in torrent_files:
    full_path = os.path.join(save_path, f.replace('/', os.sep))
    if os.path.exists(full_path):
        size_gb = os.path.getsize(full_path) / 1e9
        expected = expected_sizes.get(f, 0)
        status = "OK" if abs(size_gb - expected) < 0.1 else f"MISMATCH (expected {expected})"
        print(f"  {f}: {size_gb:.2f} GB - {status}")
    else:
        print(f"  {f}: MISSING")
