"""
Shot 4 三模型对比: LTX2.3 vs Wan 2.2 vs HunyuanVideo
同时提交，并行等待结果
"""
import sys, io, json, time, urllib.request, threading
sys.path.insert(0, r"C:\Users\user.V915-31\.openclaw\workspace\skills\comfyui\scripts")

from core import WorkflowGraph
from ltx23 import ltx23_text_to_video
import render_wan22, render_hunyuan

HOST = "http://127.0.0.1:8188"
TIMEOUT = 1200

# Shot 4 prompt
PROMPT_S4 = (
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

def submit(prompt, workflow_fn, label, extra={}, seed=None):
    print(f"\n=== Building {label} workflow ===")
    wf = workflow_fn(prompt, seed=seed, **extra)
    payload = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(
        f"{HOST}/prompt", data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"[{label}] prompt_id={prompt_id}")
    return label, prompt_id

def wait_for(label, prompt_id, timeout=TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{HOST}/history/{prompt_id}", timeout=15) as resp:
                hist = json.loads(resp.read())
            entry = hist.get(prompt_id, {})
            outputs = entry.get("outputs", {})
            status = (entry.get("status") or {}).get("status_str", "")
            print(f"[{label}] status={status}")
            if outputs:
                videos = []
                for node_id, out in outputs.items():
                    if isinstance(out, dict) and "videos" in out:
                        videos.extend(out["videos"])
                    if isinstance(out, dict) and out.get("class_type") in ("SaveVideo", "CreateVideo"):
                        videos.append(out)
                print(f"[{label}] DONE! outputs={list(outputs.keys())}")
                return label, "SUCCESS"
        except Exception as e:
            print(f"[{label}] poll error: {e}")
        time.sleep(10)
    return label, "TIMEOUT"

def run_wan22(prompt, seed=None):
    return render_wan22.build_wan22_t2v(prompt, width=1280, height=720, num_frames=121, seed=seed, steps=8)

def run_ltx(prompt, seed=None):
    return ltx23_text_to_video(prompt, seconds=5, fps=24, filename_prefix="cmp_ltx", seed=seed, include_audio=False)

def run_hunyuan(prompt, seed=None):
    return render_hunyuan.build_hunyuan_t2v(prompt, width=1280, height=720, num_frames=121, seed=seed, steps=8)

# Generate workflows
seed = 42
wan_wf = run_wan22(PROMPT_S4, seed=seed)
ltx_wf = run_ltx(PROMPT_S4, seed=seed)
hun_wf = run_hunyuan(PROMPT_S4, seed=seed)

print("=== Submitting all three simultaneously ===")

results = {}
def do(label, wf):
    payload = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{HOST}/prompt", data=payload,
                                  headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    pid = result["prompt_id"]
    print(f"[{label}] submitted: {pid}")
    label2, status = wait_for(label, pid)
    results[label2] = status

threads = [
    threading.Thread(target=do, args=("WAN22", wan_wf)),
    threading.Thread(target=do, args=("LTX", ltx_wf)),
    threading.Thread(target=do, args=("HUNYUAN", hun_wf)),
]
for t in threads: t.start()
for t in threads: t.join()

print("\n=== FINAL RESULTS ===")
for k, v in results.items():
    print(f"  {k}: {v}")
