import urllib.request, json

HOST = 'http://127.0.0.1:8188'
with urllib.request.urlopen(HOST + '/history/c1cef8b3-8691-4841-949d-1e407b8194fd', timeout=10) as r:
    hist = json.loads(r.read())
entry = hist.get('c1cef8b3-8691-4841-949d-1e407b8194fd', {})
prompt = entry.get('prompt', [])
print('Prompt type:', type(prompt))
if isinstance(prompt, list):
    print('Length:', len(prompt))
    if len(prompt) > 0:
        print('First item type:', type(prompt[0]))
        print('First item:', json.dumps(prompt[0], indent=2)[:500])
