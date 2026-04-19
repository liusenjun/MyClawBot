"""
Shot 4 三模型对比: Wan2.2 vs LTX2.3 vs HunyuanVideo
"""
import sys, io, json, time, urllib.request, urllib.error, threading

LOG = open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\compare3.log', 'w', encoding='utf-8', buffering=1)
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
    g.node("SaveVideo", video=video, filename_prefix="cmp_wan22", format="mp4", codec="auto")
    return g.to_dict()

# ── LTX 2.3 ──────────────────────────────────
def build_ltx(prompt, seconds=5, fps=24, seed=None):
    return ltx23.ltx23_text_to_video(prompt, seconds=seconds, fps=fps,
                                      filename_prefix="cmp_ltx", seed=seed, include_audio=False)

# ── HunyuanVideo ──────────────────────────────
def build_hunyuan(prompt_pos, width=1280, height=720, num_frames=121, seed=None, steps=8, cfg=7.0):
    MODEL = "hunyuan_video_t2v_720p_bf16.safetensors"
    VAE   = "hunyuan_video_vae_bf16.safetensors"
    NEG   = "blurry, low quality, watermark, distorted, still frame, static, flickering, cartoon, anime, 3d render"
    if seed is None: seed = int(time.time()*1000) % (2**32)
    g = WorkflowGraph()
    clip  = g.node("DualCLIPLoader", clip_name1="llava_llama3_fp8_scaled.safetensors",
                   clip_name2="umt5_xxl_fp8_e4m3fn_scaled.safetensors", type="hunyuan_video")
    vae   = g.node("VAELoader", vae_name=VAE)
    unet  = g.node("UNETLoader", unet_name=MODEL, weight_dtype="default")
    cond_p = g.node("CLIPTextEncodeHunyuanDiT", clip=clip, bert=prompt_pos, mt5xl=prompt_pos)
    cond_n = g.node("CLIPTextEncode", text=NEG, clip=clip)
    latent = g.node("EmptyHunyuanLatentVideo", width=width, height=height, length=num_frames, batch_size=1)
    denoised = g.node("KSamplerAdvanced", model=unet, positive=cond_p, negative=cond_n, latent_image=latent,
                       add_noise="enable", noise_seed=seed, steps=steps, cfg=cfg,
                       sampler_name="euler", scheduler="normal",
                       start_at_step=0, end_at_step=steps, return_with_leftover_noise="disable")
    g.node("DecodeAndSaveVideo", video_latent=denoised, fps=24.0,
           filename_prefix="cmp_hunyuan", format="auto", codec="auto",
           video_vae=vae, tiling="disabled")
    return g.to_dict()

# ── ComfyUI helpers ───────────────────────────
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
            status  = (entry.get("status") or {}).get("status_str", "unknown")
            log(f"[{label}] {status}")
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

# ── Main ──────────────────────────────────────
log("=== Building workflows ===")
wan_wf = build_wan22(PROMPT, seed=SEED)
log(f"WAN22 nodes: {len(wan_wf.get('nodes', {}))}")
ltx_wf = build_ltx(PROMPT, seconds=5, seed=SEED)
log(f"LTX nodes: {len(ltx_wf.get('nodes', {}))}")
hun_wf = build_hunyuan(PROMPT, seed=SEED)
log(f"HUNYUAN nodes: {len(hun_wf.get('nodes', {}))}")

log("=== Submitting all three ===")
results = {}
lock = threading.Lock()

def worker(label, wf):
    pid = submit(wf)
    log(f"[{label}] prompt_id={pid}")
    status = wait(label, pid)
    with lock:
        results[label] = status
    log(f"[{label}] DONE: {status}")

threads = [
    threading.Thread(target=worker, args=("WAN22",   wan_wf)),
    threading.Thread(target=worker, args=("LTX",     ltx_wf)),
    threading.Thread(target=worker, args=("HUNYUAN", hun_wf)),
]
for t in threads: t.start()
for t in threads: t.join()

log("\n========== RESULTS ==========")
for k, v in results.items():
    log(f"  {k}: {v}")
log("==============================")
LOG.close()
