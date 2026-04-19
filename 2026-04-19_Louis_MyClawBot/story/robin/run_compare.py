"""
Shot 4 三模型对比 v2 - 修复版
同时提交三个任务，然后等所有结果
"""
import sys, io, json, time, urllib.request, urllib.error, threading

LOG = open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\run_compare.log', 'w', encoding='utf-8', buffering=1)
def log(msg):
    print(msg, flush=True)
    LOG.write(msg + '\n'); LOG.flush()

sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph
import ltx23

HOST = "http://127.0.0.1:8188"
TIMEOUT = 1200

PROMPT = (
    "Robin moves through the cramped Teahouse with predatory precision — "
    "each footfall deliberate, weight rolling heel-to-toe to silence on the oil-wet floor, "
    "her black leather boots catching warm amber lamplight as they navigate past puddles "
    "and the shuffling feet of passing servers. Camera: extremely low angle tracking shot "
    "from directly behind, lens nearly grazing the wet tiles, 24mm wide angle to exaggerate "
    "speed and the proximity of the floor. Lighting: warm amber from overhead Teahouse lamps "
    "cuts through cool blue-tinged wet light seeping from the open door, shallow depth of field "
    "compressing the crowded background of chattering diners into soft bokeh. Audio: "
    "the amplified wet squelch of boots on tile, distant clinking porcelain, muffled Cantonese "
    "chatter, her own controlled shallow breathing audible above the ambient noise. "
    "Her breathing: measured, deliberate — the rhythm of someone who knows exactly where "
    "everyone in the room is without looking. Position: she occupies the wet third of frame, "
    "passing a serving cart on her left."
)
SEED = 42

# ── Wan 2.2 ──────────────────────────────────
def build_wan22(prompt_pos, width=1280, height=720, num_frames=121, seed=None, steps=8):
    CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
    VAE  = "wan_2.1_vae.safetensors"
    HIGH = "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
    LOW  = "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
    LORA_H = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
    LORA_L = "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
    NEG = "blurry, low quality, watermark, distorted, still frame, static, flickering"
    if seed is None: seed = int(time.time()*1000) % (2**32)
    g = WorkflowGraph()
    clip   = g.node("CLIPLoader", clip_name=CLIP, type="wan", device="default")
    vae    = g.node("VAELoader", vae_name=VAE)
    unet_h = g.node("UNETLoader", unet_name=HIGH, weight_dtype="default")
    unet_l = g.node("UNETLoader", unet_name=LOW,  weight_dtype="default")
    model_h = g.node("LoraLoaderModelOnly", model=unet_h, lora_name=LORA_H, strength_model=1.0)
    model_l = g.node("LoraLoaderModelOnly", model=unet_l, lora_name=LORA_L,  strength_model=1.0)
    model_h = g.node("ModelSamplingSD3", model=model_h, shift=5.0)
    model_l = g.node("ModelSamplingSD3", model=model_l, shift=5.0)
    cond_p  = g.node("CLIPTextEncode", text=prompt_pos, clip=clip)
    cond_n  = g.node("CLIPTextEncode", text=NEG, clip=clip)
    latent  = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)
    after_h = g.node("KSamplerAdvanced", model=model_h, positive=cond_p, negative=cond_n, latent_image=latent,
                     add_noise="enable", noise_seed=seed, steps=steps, cfg=1.0,
                     sampler_name="euler", scheduler="simple", start_at_step=0, end_at_step=4,
                     return_with_leftover_noise="enable")
    after_l = g.node("KSamplerAdvanced", model=model_l, positive=cond_p, negative=cond_n, latent_image=after_h,
                     add_noise="disable", noise_seed=seed, steps=steps, cfg=1.0,
                     sampler_name="euler", scheduler="simple", start_at_step=4, end_at_step=steps,
                     return_with_leftover_noise="disable")
    decoded = g.node("VAEDecode", samples=after_l, vae=vae)
    video   = g.node("CreateVideo", images=decoded, fps=24)
    g.node("SaveVideo", video=video, filename_prefix="cmp2_wan22", format="mp4", codec="auto")
    return g.to_dict()

# ── HunyuanVideo (FIXED: DualCLIPLoader returns tuple) ──────────────
def build_hunyuan(prompt_pos, width=1280, height=720, num_frames=121, seed=None, steps=8, cfg=7.0):
    MODEL = "hunyuan_video_t2v_720p_bf16.safetensors"
    VAE   = "hunyuan_video_vae_bf16.safetensors"
    NEG   = "blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render"
    if seed is None: seed = int(time.time()*1000) % (2**32)
    g = WorkflowGraph()
    # FIX: DualCLIPLoader returns tuple -> use clip[0] for CLIPTextEncodeHunyuanDiT
    clip_raw = g.node("DualCLIPLoader", clip_name1="llava_llama3_fp8_scaled.safetensors",
                      clip_name2="umt5_xxl_fp8_e4m3fn_scaled.safetensors", type="hunyuan_video")
    vae    = g.node("VAELoader", vae_name=VAE)
    unet   = g.node("UNETLoader", unet_name=MODEL, weight_dtype="default")
    cond_p = g.node("CLIPTextEncodeHunyuanDiT", clip=clip_raw[0], bert=prompt_pos, mt5xl=prompt_pos)
    cond_n = g.node("CLIPTextEncode", text=NEG, clip=clip_raw[0])
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)
    denoised = g.node("KSamplerAdvanced", model=unet, positive=cond_p, negative=cond_n, latent_image=latent,
                       add_noise="enable", noise_seed=seed, steps=steps, cfg=cfg,
                       sampler_name="euler", scheduler="normal",
                       start_at_step=0, end_at_step=steps, return_with_leftover_noise="disable")
    g.node("DecodeAndSaveVideo", video_latent=denoised, fps=24.0,
           filename_prefix="cmp2_hunyuan", format="auto", codec="auto",
           video_vae=vae, tiling="disabled")
    return g.to_dict()

# ── LTX 2.3 (FIXED models) ─────────────────────────────────────────
def build_ltx(prompt, seconds=5, fps=24, seed=None):
    if seed is None: seed = int(time.time() * 1000) % (2**31)
    g = WorkflowGraph()
    # Use gemma for both clips (confirmed available)
    clip = g.node("DualCLIPLoader",
                  clip_name1="gemma_3_12B_it_fp8_e4m3fn.safetensors",
                  clip_name2="gemma_3_12B_it_fp8_e4m3fn.safetensors",
                  type="ltxv")
    video_vae = g.node("VAELoaderKJ",
                        vae_name="LTX2_video_vae_bf16.safetensors",
                        device="main_device", weight_dtype="bf16")
    audio_vae = g.node("VAELoaderKJ",
                        vae_name="LTX2_audio_vae_bf16.safetensors",
                        device="main_device", weight_dtype="bf16")
    unet = g.node("UnetLoaderGGUF", unet_name="ltx-2-19b-distilled_Q4_K_M.gguf")
    model = g.node("LTXVChunkFeedForward", model=unet[0], chunks=4, dim_threshold=4096)
    model = g.node("LoraLoaderModelOnly", model=model[0],
                   lora_name="ltx-2-19b-distilled-lora-384.safetensors",
                   strength_model=0.6)
    pos = g.node("CLIPTextEncode", text=prompt, clip=clip)
    neg = g.node("CLIPTextEncode",
                 text="blurry, low quality, watermark, distorted, still frame",
                 clip=clip)
    cond = g.node("LTXVConditioning", positive=pos[0], negative=neg[0], frame_rate=float(fps))
    raw_length = seconds * fps
    length = ((raw_length // 8) * 8) + 1
    latent = g.node("EmptyLTXVLatentVideo",
                     width=768, height=512, length=length, batch_size=1)
    sampler = g.node("KSamplerSelect", sampler_name="euler_ancestral")
    schedule = g.node("LTXVScheduler", steps=8, max_shift=2.05, base_shift=0.95,
                       stretch=True, terminal=0.1, latent=latent)
    noise = g.node("RandomNoise", noise_seed=seed)
    guider = g.node("CFGGuider", model=model[0], positive=cond[0], negative=cond[1], cfg=1.0)
    out = g.node("SamplerCustomAdvanced", noise=noise[0], guider=guider[0],
                 sampler=sampler[0], sigmas=schedule[0], latent_image=latent)
    images = g.node("LTXVSpatioTemporalTiledVAEDecode", vae=video_vae[0], latents=out[0],
                    spatial_tiles=4, spatial_overlap=1,
                    temporal_tile_length=16, temporal_overlap=1,
                    last_frame_fix=False, working_device="auto", working_dtype="auto")
    video = g.node("CreateVideo", images=images[0], fps=float(fps))
    g.node("SaveVideo", video=video[0], filename_prefix="cmp2_ltx", format="auto", codec="auto")
    return g.to_dict()

# ── Helpers ────────────────────────────────────────────────────────
def submit(workflow):
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{HOST}/prompt", data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())["prompt_id"]
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:600]
        log(f"HTTP {e.code}: {body}")
        raise

def wait(label, prompt_id, timeout=TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{HOST}/history/{prompt_id}", timeout=15) as resp:
                hist = json.loads(resp.read())
            entry = hist.get(prompt_id, {})
            outputs = entry.get("outputs", {})
            st = (entry.get("status") or {}).get("status_str", "unknown")
            msgs = entry.get("status", {}).get("messages", [])
            log(f"[{label}] status={st}")
            for m in msgs:
                if 'error' in str(m).lower():
                    log(f"  MSG: {str(m)[:200]}")
            if outputs:
                for nid, out in outputs.items():
                    if isinstance(out, dict):
                        for k, v in out.items():
                            if isinstance(v, list):
                                for f in v:
                                    if isinstance(f, dict) and "filename" in f:
                                        log(f"[{label}] --> {f['filename']}")
                            elif isinstance(v, dict) and "filename" in v:
                                log(f"[{label}] --> {v['filename']}")
                return "SUCCESS"
        except Exception as ex:
            log(f"[{label}] poll err: {ex}")
        time.sleep(12)
    return "TIMEOUT"

# ── Build all three ────────────────────────────────────────────────
log("=== Building workflows ===")
wan_wf = build_wan22(PROMPT, seed=SEED)
ltx_wf = build_ltx(PROMPT, seconds=5, seed=SEED)
hun_wf = build_hunyuan(PROMPT, seed=SEED)
log(f"WAN22 nodes={len(wan_wf)} LTX nodes={len(ltx_wf)} HUNYUAN nodes={len(hun_wf)}")

# ── Submit all three simultaneously ────────────────────────────────
results = {}
lock = threading.Lock()

def worker(label, wf):
    pid = submit(wf)
    log(f"[{label}] submitted: {pid}")
    status = wait(label, pid)
    with lock:
        results[label] = (status, pid)
    log(f"[{label}] DONE: {status}")

threads = [
    threading.Thread(target=worker, args=("WAN22",   wan_wf)),
    threading.Thread(target=worker, args=("LTX",     ltx_wf)),
    threading.Thread(target=worker, args=("HUNYUAN", hun_wf)),
]
for t in threads: t.start()
for t in threads: t.join()

log("\n========== RESULTS ==========")
for k, (v, pid) in results.items():
    log(f"  {k}: {v} (prompt_id={pid})")
log("==============================")
LOG.close()
