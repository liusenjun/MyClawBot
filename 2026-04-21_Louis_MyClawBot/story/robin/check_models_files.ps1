# Check which models torrent files are on disk and their sizes
$savePath = "C:\Users\user.V915-31\Documents\ComfyUI"
$torrentFiles = @(
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
    "vae/LTX2_video_vae_bf16.safetensors"
)

foreach ($f in $torrentFiles) {
    $fullPath = Join-Path $savePath $f
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        $sizeGB = [math]::Round($size/1GB, 3)
        Write-Host "$($f): $sizeGB GB"
    } else {
        Write-Host "$($f): MISSING"
    }
}
