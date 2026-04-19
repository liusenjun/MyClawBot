import urllib.request, json, base64

req = urllib.request.Request(
    'https://api.github.com/repos/venetanji/ltx2-comfy-v915/contents/workflows/ltx2-singlepass-T2V.json',
    headers={'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
wf = json.loads(base64.b64decode(data['content']).decode('utf-8'))
nodes = wf.get('nodes', [])

for n in nodes:
    t = n.get('type', '')
    wv = n.get('widgets_values', [])
    if wv and t in ['LoraLoaderModelOnly', 'UnetLoaderGGUF', 'EmptyLTXVLatentVideo',
                    'LTXVEmptyLatentAudio', 'CFGGuider', 'LTXVScheduler', 'RandomNoise',
                    'CreateVideo', 'KSamplerSelect', 'DualCLIPLoader']:
        print(f'Node {n["id"]} {t}: widgets_values = {wv}')
