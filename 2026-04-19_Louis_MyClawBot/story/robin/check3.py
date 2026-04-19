import json, urllib.request
HOST = 'http://127.0.0.1:8188'
targets = {
    'WAN22':   'c4a6014d-e4ff-4587-8528-24f43f8dff3f',
    'HUNYUAN': '63a5cdf8-77a3-4112-a94b-b255da170992',
    'LTX':     '17de78bc-70ff-4ed6-8d8f-b2728e751797'
}
for label, pid in targets.items():
    try:
        with urllib.request.urlopen(f'{HOST}/history/{pid}', timeout=10) as r:
            h = json.loads(r.read())
        e = h.get(pid, {})
        st = (e.get('status') or {}).get('status_str', '')
        outs = e.get('outputs', {})
        print(f'{label}: {st} outputs={bool(outs)} n={len(outs)}')
        if st == 'success' and outs:
            for nid, out in outs.items():
                if isinstance(out, dict):
                    for k, v in out.items():
                        if isinstance(v, list):
                            for f in v:
                                if isinstance(f, dict) and 'filename' in f:
                                    print(f'  FILE: {f["filename"]}')
                        elif isinstance(v, dict) and 'filename' in v:
                            print(f'  FILE: {v["filename"]}')
        elif st == 'error':
            msgs = e.get('status', {}).get('messages', [])
            for m in msgs:
                if 'error' in str(m).lower():
                    print(f'  ERR: {str(m)[:200]}')
    except Exception as ex:
        print(f'{label}: err={ex}')
