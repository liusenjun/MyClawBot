import urllib.request, json

HOST = 'http://127.0.0.1:8188'

# Check ComfyUI queue
with urllib.request.urlopen(HOST + '/queue', timeout=5) as r:
    q = json.loads(r.read())
print('Queue running:', q.get('queue_running', []))
print('Queue pending:', q.get('queue_pending', []))

# Also check qBittorrent
QB_HOST = 'http://127.0.0.1:8080'
try:
    req = urllib.request.Request(QB_HOST + '/api/v2/torrents/info', method='GET')
    with urllib.request.urlopen(req, timeout=5) as resp:
        torrents = json.loads(resp.read())
    for t in torrents:
        name = t.get('name', '')
        state = t.get('state', '')
        prog = t.get('progress', 0) * 100
        seeds = t.get('num_seeds', 0)
        print('Torrent: ' + name + ' - ' + state + ' - ' + str(round(prog, 1)) + '% - seeds: ' + str(seeds))
except Exception as e:
    print('qBittorrent: ' + str(e))
