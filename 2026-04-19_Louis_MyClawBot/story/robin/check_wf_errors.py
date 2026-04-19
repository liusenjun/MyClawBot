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
        st = e.get('status', {})
        outs = e.get('outputs', {})
        print(f'=== {label} ===')
        print(f'  status: {st.get("status_str")} completed: {st.get("completed")}')
        print(f'  error: {st.get("error_message","")}')
        print(f'  outputs: {bool(outs)} n={len(outs)}')
        print(f'  status keys: {list(st.keys())}')
        # Check for errors in the prompt itself
        if 'prompt' in e:
            print(f'  prompt present')
    except Exception as ex:
        print(f'{label}: err={ex}')
