import json, urllib.request
HOST = 'http://127.0.0.1:8188'
for label, pid in [
    ('WAN22',   'ac7621fb-7828-4f33-bff4-8509362f35e5'),
    ('HUNYUAN', '2445bf1f-f128-48c5-afb7-a393ea44943d'),
    ('DONE',    'd82229a2-7e7d-462d-9f49-c97127bffc49'),
]:
    try:
        with urllib.request.urlopen(f'{HOST}/history/{pid}', timeout=10) as r:
            h = json.loads(r.read())
        e = h.get(pid, {})
        st = e.get('status', {})
        outs = e.get('outputs', {})
        print(f'{label}: status_str={st.get("status_str")} completed={st.get("completed")} error={st.get("error_message","")} outputs={bool(outs)} n={len(outs)}')
        for nid, out in outs.items():
            if isinstance(out, dict):
                for k, v in out.items():
                    if isinstance(v, list):
                        for f in v:
                            if isinstance(f, dict) and 'filename' in f:
                                print(f'  FILE: {f["filename"]}')
                    elif isinstance(v, dict) and 'filename' in v:
                        print(f'  FILE: {v["filename"]}')
    except Exception as ex:
        print(f'{label}: err={ex}')
