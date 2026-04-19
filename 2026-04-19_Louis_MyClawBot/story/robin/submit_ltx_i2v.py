"""
Submit ltx2-singlepass-I2V workflow to ComfyUI and check for errors.
"""
import json
import requests
import time

COMFY_URL = "http://127.0.0.1:8188"

# Load workflow
with open(r"C:\Users\user.V915-31\.openclaw\workspace\story\robin\ltx_i2v_workflow.json") as f:
    wf = json.load(f)

# Convert to flat prompt format
nodes = wf["nodes"]
links = wf.get("links", [])

# Build link map: link_id -> [source_node_id, source_output_idx]
link_map = {}
for link in links:
    if link:
        link_id, src_id, src_idx, tgt_id, tgt_idx, type_name = link
        link_map[link_id] = [src_id, src_idx]

prompt = {}
for n in nodes:
    nid = str(n["id"])
    inputs = {}
    for inp in n.get("inputs", []):
        if "link" in inp and inp["link"] is not None:
            link_id = inp["link"]
            if link_id in link_map:
                src_id, src_idx = link_map[link_id]
                inputs[inp["name"]] = [str(src_id), src_idx]
            else:
                inputs[inp["name"]] = None
        elif "widget" in inp:
            # use current value
            inputs[inp["name"]] = inp.get("link")  # will use widgets_values
        else:
            if inp["name"] in ["clip"] and inp.get("link") is None:
                continue
    
    widgets_values = n.get("widgets_values", [])
    prompt[nid] = {"inputs": inputs, "class_type": n["type"], "widgets_values": widgets_values}

# Fix missing required inputs with widget values
for nid, ndata in prompt.items():
    n_original = next(x for x in nodes if str(x["id"]) == nid)
    wv = ndata.get("widgets_values", [])
    inputs = ndata["inputs"]
    
    # Handle primitive nodes with widgets
    if n_original["type"] in ["PrimitiveNode", "PrimitiveInt", "PrimitiveFloat", "PrimitiveBoolean"]:
        wv_name = None
        for out in n_original.get("outputs", []):
            if "widget" in out:
                wv_name = out["widget"].get("name")
                break
        if wv and wv_name:
            inputs[wv_name] = wv[0]
    
    # Handle KSamplerSelect
    if n_original["type"] == "KSamplerSelect" and "SAMPLER" not in inputs:
        inputs["SAMPLER"] = wv[0] if wv else "euler_ancestral"
    
    # Handle RandomNoise  
    if n_original["type"] == "RandomNoise":
        if "noise" not in inputs or inputs["noise"] is None:
            seed = wv[0] if wv else 0
            inputs["noise"] = seed
    
    # Handle LoadImageOutput - this loads an image, skip for now
    if n_original["type"] == "LoadImageOutput":
        # Replace with empty image
        inputs["image"] = None
    
    # Handle VAELoaderKJ - widget values have the filename
    if n_original["type"] == "VAELoaderKJ":
        if wv:
            inputs["vae_name"] = wv[0]
    
    # Handle UnetLoaderGGUF
    if n_original["type"] == "UnetLoaderGGUF":
        if wv:
            inputs["model_path"] = wv[0]
    
    # Handle LoraLoaderModelOnly
    if n_original["type"] == "LoraLoaderModelOnly":
        if len(wv) >= 2:
            inputs["lora_name"] = wv[0]
            inputs["strength_model"] = wv[1]
        if "model" not in inputs or inputs["model"] is None:
            inputs["model"] = None
    
    # Handle DualCLIPLoader
    if n_original["type"] == "DualCLIPLoader":
        if wv:
            inputs["clip_model1"] = wv[0]
            inputs["clip_model2"] = wv[1]
    
    # Handle CLIPTextEncode
    if n_original["type"] == "CLIPTextEncode":
        if "clip" not in inputs or inputs["clip"] is None:
            inputs["text"] = wv[0] if wv else ""
    
    # Handle LTXVConditioning
    if n_original["type"] == "LTXVConditioning":
        if wv:
            inputs["frame_rate"] = wv[0]
    
    # Handle LTXVScheduler
    if n_original["type"] == "LTXVScheduler":
        if wv:
            inputs["steps"] = wv[0]
            inputs["cfg"] = wv[1]
            inputs["denoise"] = wv[2]
            inputs["scheduler"] = "normal"
    
    # Handle CM_FloatToInt
    if n_original["type"] == "CM_FloatToInt":
        if "a" in inputs and inputs["a"] is None:
            inputs["a"] = wv[0] if wv else 0
    
    # Handle SaveVideo - add filename
    if n_original["type"] == "SaveVideo":
        if wv:
            inputs["filename_prefix"] = wv[0]
    
    # Handle GetImageRangeFromBatch
    if n_original["type"] == "GetImageRangeFromBatch":
        if wv:
            inputs["start_index"] = wv[0]
            inputs["max_images"] = wv[1]
    
    # Handle LTXVEmptyLatentAudio
    if n_original["type"] == "LTXVEmptyLatentAudio":
        if wv:
            inputs["frames_number"] = wv[0]
            inputs["frame_rate"] = wv[1]
    
    # Handle EmptyLTXVLatentVideo
    if n_original["type"] == "EmptyLTXVLatentVideo":
        if wv:
            inputs["width"] = wv[0]
            inputs["height"] = wv[1]
            inputs["length"] = wv[2]
            inputs["batch_size"] = wv[3]
    
    # Handle CreateVideo
    if n_original["type"] == "CreateVideo":
        if wv:
            inputs["fps"] = wv[0]
    
    # Handle LTXVSpatioTemporalTiledVAEDecode
    if n_original["type"] == "LTXVSpatioTemporalTiledVAEDecode":
        if wv:
            inputs["tile_sample_min_height"] = wv[0]
            inputs["tile_sample_min_width"] = wv[1]
            inputs["tile_sample_min_t"] = wv[2]
            inputs["tile_sample_pad"] = wv[3]
            inputs["tile_sample_unequal_height"] = wv[4]
    
    # Handle PathchSageAttentionKJ
    if n_original["type"] == "PathchSageAttentionKJ":
        if wv:
            inputs["attention_type"] = wv[0]
            inputs["enable"] = wv[1]
    
    # Handle LTXVChunkFeedForward  
    if n_original["type"] == "LTXVChunkFeedForward":
        if wv:
            inputs["chunk_size"] = wv[0]
            inputs["chunk_nums"] = wv[1]

    ndata["inputs"] = inputs

# Remove None inputs
for nid, ndata in prompt.items():
    clean_inputs = {}
    for k, v in ndata["inputs"].items():
        if v is not None:
            clean_inputs[k] = v
    ndata["inputs"] = clean_inputs

# Submit
print("Submitting workflow...")
r = requests.post(f"{COMFY_URL}/prompt", json={"prompt": prompt}, timeout=30)
print("Status:", r.status_code)
if r.status_code != 200:
    print("Error:", r.text[:500])
else:
    data = r.json()
    print("Response:", json.dumps(data, indent=2)[:500])
    if "error" in data:
        print("ERROR:", data["error"])
    elif "prompt_id" in data:
        prompt_id = data["prompt_id"]
        print("Prompt ID:", prompt_id)
        
        # Wait and check history
        for i in range(10):
            time.sleep(3)
            hist_r = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
            if hist_r.status_code == 200:
                hist = hist_r.json()
                if prompt_id in hist:
                    status = hist[prompt_id]
                    print("Status:", status.get("status", {}).get("state", "unknown"))
                    if "error" in status:
                        print("ERROR:", json.dumps(status["error"], indent=2))
                    if "outputs" in status:
                        for node_id, output in status["outputs"].items():
                            if "errors" in output:
                                print(f"Node {node_id} errors:", output["errors"])
                    break
                else:
                    print("Not in history yet...")
            else:
                print("History request failed:", hist_r.status_code)
