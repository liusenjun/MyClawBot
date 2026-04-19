import urllib.request, json

HOST = 'http://127.0.0.1:8188'
with urllib.request.urlopen(HOST + '/object_info', timeout=10) as r:
    info = json.loads(r.read())

hunyuan_nodes = [(k, v) for k, v in info.items() if 'hunyuan' in k.lower() or 'Hunyuan' in k]
print('Hunyuan nodes:')
for name, data in sorted(hunyuan_nodes):
    inputs = data.get('input', {}).get('required', {}) or data.get('input', {}).get('optional', {})
    input_names = list(inputs.keys()) if inputs else []
    print(f'  {name}: {input_names[:8]}')
