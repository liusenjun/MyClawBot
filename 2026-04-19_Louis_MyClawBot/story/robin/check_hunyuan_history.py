import urllib.request, json

HOST = 'http://127.0.0.1:8188'
try:
    with urllib.request.urlopen(HOST + '/history?limit=10', timeout=5) as r:
        h = json.loads(r.read())
    print(f"Recent jobs: {len(h)}")
    for pid, data in sorted(h.items(), key=lambda x: x[1].get('status',{}).get('completed_at',0))[-5:]:
        st = data.get('status',{}).get('status_str','')
        ct = data.get('status',{}).get('completed_at','')
        print(f"\n{pid[:8]} - {st} (completed {ct})")
        p = data.get('prompt',{})
        for nid, n in p.items():
            inputs = n.get('inputs',{})
            if 'text' in inputs and isinstance(inputs['text'], str) and len(inputs['text']) > 20:
                print(f"  Node {nid} ({n.get('class_type','')}): {inputs['text'][:200]}")
except Exception as e:
    print(e)
