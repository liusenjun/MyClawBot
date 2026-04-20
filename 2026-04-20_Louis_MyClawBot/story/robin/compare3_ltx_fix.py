"""
Fixed LTX 2.3 builder - uses correct clip_name2 from available models
"""
import sys, io, json, time, urllib.request, urllib.error, threading, os

LOG = open(r'C:\Users\user.V915-31\.openclaw\workspace\story\robin\compare3_ltx.log', 'w', encoding='utf-8', buffering=1)
def log(msg):
    print(msg, flush=True)
    LOG.write(msg + '\n'); LOG.flush()

sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")
from core import WorkflowGraph

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

# Available models (confirmed via object_info):
# clip_name1: gemma_3_12B_it_fp8_e4m3fn, llava_llama3_fp8_scaled, ltx-2-19b-embeddings_connector_distill_bf16, qwen_3_4b, umt5_xxl_fp8_e4m3fn_scaled
# clip_name2: gemma_3_12B_it_fp8_e4m3fn, llava_llama3_fp8_scaled, ltx-2-19b-embeddings_connector_distill_bf16, qwen_3_4b, umt5_xxl_fp8_e4m3fn_scaled

def build_ltx_fixed(prompt, seconds=5, fps=24, seed=None):
    if seed is None:
        seed = int(time.time() * 1000) % (2**31)
    g = WorkflowGraph()
    # Use gemma for both clips (LTX2.3 default text encoder)
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
    # Load UNet GGUF
    unet = g.node("UnetLoaderGGUF", unet_name="ltx-2-19b-distilled_Q4_K_M.gguf")
    model = g.node("LTXVChunkFeedForward", model=unet[0], chunks=4, dim_threshold=4096)
    # LoRA
    model = g.node("LoraLoaderModelOnly", model=model[0],
                   lora_name="ltx-2-19b-distilled-lora-384.safetensors",
                   strength_model=0.6)
    # Conditioning
    pos = g.node("CLIPTextEncode", text=prompt, clip=clip)
    neg = g.node("CLIPTextEncode",
                 text="blurry, low quality, watermark, distorted, still frame",
                 clip=clip)
    cond = g.node("LTXVConditioning", positive=pos[0], negative=neg[0], frame_rate=float(fps))
    # Latent
    raw_length = seconds * fps
    length = ((raw_length // 8) * 8) + 1
    latent = g.node("EmptyLTXVLatentVideo",
                     width=768, height=512, length=length, batch_size=1)
    # Sample
    sampler = g.node("KSamplerSelect", sampler_name="euler_ancestral")
    schedule = g.node("LTXVScheduler", steps=8, max_shift=2.05, base_shift=0.95,
                       stretch=True, terminal=0.1, latent=latent)
    noise = g.node("RandomNoise", noise_seed=seed)
    guider = g.node("CFGGuider", model=model[0], positive=cond[0], negative=cond[1], cfg=1.0)
    out = g.node("SamplerCustomAdvanced", noise=noise[0], guider=guider[0],
                 sampler=sampler[0], sigmas=schedule[0], latent_image=latent)
    # Decode
    images = g.node("LTXVSpatioTemporalTiledVAEDecode", vae=video_vae[0], latents=out[0],
                    spatial_tiles=4, spatial_overlap=1,
                    temporal_tile_length=16, temporal_overlap=1,
                    last_frame_fix=False, working_device="auto", working_dtype="auto")
    # Save
    video = g.node("CreateVideo", images=images[0], fps=float(fps))
    g.node("SaveVideo", video=video[0], filename_prefix="cmp_ltx", format="auto", codec="auto")
    return g.to_dict()

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
            log(f"[{label}] {st}")
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

# Wait for current queue to drain first
log("=== Waiting for current queue to clear ===")
while True:
    with urllib.request.urlopen(f"{HOST}/queue", timeout=10) as r:
        q = json.loads(r.read())
    running = q.get('queue_running', [])
    pending = q.get('queue_pending', [])
    log(f"  running={len(running)} pending={len(pending)}")
    if not running and not pending:
        log("Queue empty!")
        break
    time.sleep(15)

log("\n=== Building & submitting fixed LTX ===")
wf = build_ltx_fixed(PROMPT, seconds=5, seed=SEED)
log(f"LTX nodes: {len(wf)}")
pid = submit(wf)
log(f"LTX prompt_id={pid}")
status = wait("LTX", pid)
log(f"\nLTX result: {status}")
LOG.close()
