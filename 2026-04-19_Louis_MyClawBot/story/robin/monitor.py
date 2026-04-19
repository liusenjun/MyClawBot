import json, urllib.request, time
HOST = 'http://127.0.0.1:8188'
targets = {
    'WAN22':   'c4a6014d-e4ff-4587-8528-24f43f8dff3f',
    'HUNYUAN': '63a5cdf8-77a3-4112-a94b-b255da170992',
    'LTX':     '17de78bc-70ff-4ed6-8d8f-b2728e751797'
}
done = set()
for i in range(30):
    for label, pid in targets.items():
        if label in done:
            continue
        try:
            with urllib.request.urlopen(f'{HOST}/history/{pid}', timeout=10) as r:
                h = json.loads(r.read())
            e = h.get(pid, {})
            st = (e.get('status') or {}).get('status_str', '')
            outs = e.get('outputs', {})
            if st == 'success' and outs:
                done.add(label)
                for nid, out in outs.items():
                    if isinstance(out, dict):
                        for k, v in out.items():
                            if isinstance(v, list):
                                for f in v:
                                    if isinstance(f, dict) and 'filename' in f:
                                        print(f'[{label}] DONE --> {f["filename"]}')
                            elif isinstance(v, dict) and 'filename' in v:
                                print(f'[{label}] DONE --> {v["filename"]}')
                if label not in done:
                    print(f'[{label}] success but no files')
                    done.add(label)
            elif st == 'error':
                done.add(label)
                print(f'[{label}] ERROR')
                msgs = e.get('status', {}).get('messages', [])
                for m in msgs:
                    if 'error' in str(m).lower():
                        print(f'  {str(m)[:150]}')
        except Exception as ex:
            print(f'[{label}] poll err: {ex}')
    if len(done) == len(targets):
        break
    print(f'[{i*20}s] done={len(done)}/{len(targets)}')
    time.sleep(20)
print('FINAL done:', done)
