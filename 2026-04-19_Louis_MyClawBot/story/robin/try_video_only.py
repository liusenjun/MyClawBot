import sys, json, time, urllib.request, urllib.error
sys.path.insert(0, r'C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts')
from core import WorkflowGraph

HOST = 'http://127.0.0.1:8188'
PROMPT = 'Robin moves through the cramped Teahouse with predatory precision, low angle tracking shot'
SEED = 42

g = WorkflowGraph()
unet = g.node('UnetLoaderGGUF', unet_name='ltx-2-19b-distilled_Q4_K_M.gguf')
vae_v = g.node('VAELoaderKJ', vae_name='LTX2_video_vae_bf16.safetensors', device='main_device', weight_dtype='bf16')
clip = g.node('DualCLIPLoader', clip_name1='gemma_3_12B_it_fp8_e4m3fn.safetensors', clip_name2='ltx-2-19b-embeddings_connector_distill_bf16.safetensors', type='ltxv')
cond_p = g.node('CLIPTextEncode', text=PROMPT, clip=clip)
cond_n = g.node('CLIPTextEncode', text='blurry, low quality, cartoon, anime, watermark, distorted', clip=clip)
cond = g.node('LTXVConditioning', positive=cond_p, negative=cond_n, frame_rate=24.0)
guider = g.node('CFGGuider', model=unet, positive=cond, negative=cond, cfg=1.0)
sigmas = g.node('LTXVScheduler', steps=8, max_shift=2.05, base_shift=0.95, stretch=True, terminal=0.1)
noise = g.node('RandomNoise', noise_seed=SEED)
sampler_sel = g.node('KSamplerSelect', sampler_name='euler_ancestral')
# Video latent only - no audio
latent_v = g.node('EmptyLTXVLatentVideo', width=768, height=512, length=97, batch_size=1)
# Skip audio entirely - use video-only sampler
sampled = g.node('SamplerCustomAdvanced', noise=noise, guider=guider, sampler=sampler_sel, sigmas=sigmas, latent_image=latent_v)
decoded_v = g.node('LTXVSpatioTemporalTiledVAEDecode', vae=vae_v, latents=sampled, spatial_tiles=4, spatial_overlap=4, temporal_tile_length=16, temporal_overlap=4, last_frame_fix=False, working_device='auto', working_dtype='auto')
g.node('SaveImage', images=decoded_v, filename_prefix='ltx_v14')

wf = g.to_dict()
payload = json.dumps({'prompt': wf}).encode('utf-8')
req = urllib.request.Request(HOST + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        r = json.loads(resp.read())
    pid = r.get('prompt_id', '?')
    print(f'Submitted: {pid[:8]}')
    time.sleep(10)
    with urllib.request.urlopen(HOST + '/history/' + pid, timeout=10) as r2:
        h = json.loads(r2.read())
    e = h.get(pid, {})
    st = (e.get('status') or {}).get('status_str', '')
    print(f'Status after 10s: {st}')
    if st == 'error':
        for m in e.get('status',{}).get('messages',[]):
            if 'exception_message' in str(m): print(f'ERR: {str(m)[:300]}')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')[:600]
    print(f'HTTP {e.code}: {body}')
