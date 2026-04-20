import urllib.request, json, time

HOST = 'http://127.0.0.1:8188'
PROMPT_ID = '9ba67fcb-5fdb-4fec-87a7-b74c219b2028'

deadline = time.time() + 900
while time.time() < deadline:
    with urllib.request.urlopen(HOST + '/history/' + PROMPT_ID, timeout=15) as resp:
        hist = json.loads(resp.read())
    entry = hist.get(PROMPT_ID, {})
    outputs = entry.get('outputs', {})
    status = (entry.get('status') or {}).get('status_str', '?')
    print('[' + status + ']', end=' ')
    if outputs:
        for nid, out in outputs.items():
            for key, val in out.items():
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict) and 'filename' in item:
                            print(' -> ' + item['filename'])
        print('DONE!')
        break
    if status in ('error', 'completed') and not outputs:
        print('ERROR or completed with no outputs')
        break
    time.sleep(15)
