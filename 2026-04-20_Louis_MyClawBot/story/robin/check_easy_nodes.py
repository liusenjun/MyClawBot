import urllib.request, json

HOST = 'http://127.0.0.1:8188'
for node in ['easy hunyuanDiTLoader', 'EasyUseHunyuanLoader']:
    try:
        encoded = node.replace(' ', '%20')
        with urllib.request.urlopen(HOST + '/object_info/' + encoded, timeout=5) as r:
            info = json.loads(r.read())
        nd = list(info.values())[0]
        inp = list(nd.get('input', {}).get('required', {}).keys())[:15]
        out = nd.get('output', [])
        print(node + ': inputs=' + str(inp) + ', output=' + str(out))
    except Exception as e:
        print(node + ': ' + str(e))
