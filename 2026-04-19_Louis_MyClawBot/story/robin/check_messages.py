import json, urllib.request
HOST = 'http://127.0.0.1:8188'
for label, pid in [
    ('WAN22',   'ac7621fb-7828-4f33-bff4-8509362f35e5'),
    ('HUNYUAN', '2445bf1f-f128-48c5-afb7-a393ea44943d'),
]:
    try:
        with urllib.request.urlopen(f'{HOST}/history/{pid}', timeout=10) as r:
            h = json.loads(r.read())
        e = h.get(pid, {})
        msgs = e.get('status', {}).get('messages', [])
        print(f'=== {label} ({len(msgs)} messages) ===')
        for m in msgs:
            print(f'  {m}')
    except Exception as ex:
        print(f'{label}: err={ex}')
