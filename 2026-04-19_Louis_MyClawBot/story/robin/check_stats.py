import urllib.request, json

HOST = 'http://127.0.0.1:8188'
try:
    with urllib.request.urlopen(HOST + '/system_stats', timeout=5) as r:
        stats = json.loads(r.read())
    print('ComfyUI version:', stats.get('version', 'unknown'))
    print('VRAM:', stats.get('vram_used', '?'), '/', stats.get('vram_total', '?'))
    print('System:', stats.get('system', {}))
except Exception as e:
    print('system_stats error:', e)

# Check old successful hunyuan prompt id from run_compare2.log
old_pid = '63a5cdf8-77a3-4112-a94b-b255da170992'
try:
    with urllib.request.urlopen(HOST + '/history/' + old_pid, timeout=5) as r:
        h = json.loads(r.read())
    e = h.get(old_pid, {})
    st = (e.get('status') or {}).get('status_str', 'not found')
    print(f'\nOld hunyuan run ({old_pid[:8]}): {st}')
except Exception as e:
    print(f'\nOld hunyuan run: {e}')
