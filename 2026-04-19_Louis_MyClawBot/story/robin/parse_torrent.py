import urllib.request
import bencodepy
import os

url = 'https://github.com/venetanji/ltx2-comfy-v915/raw/refs/heads/main/ltx23.torrent'
print(f"Downloading {url} ...")
torrent_data = urllib.request.urlopen(url, timeout=30).read()
print(f"Downloaded {len(torrent_data)} bytes")

t = bencodepy.decode(torrent_data)
info = t[b'info']
print('Name:', info[b'name'].decode() if b'name' in info else 'unknown')
print('Files:')
if b'files' in info:
    total = 0
    for f in info[b'files']:
        path_parts = f[b'path']
        if isinstance(path_parts[0], bytes):
            path = '/'.join([p.decode('utf-8', errors='replace') for p in path_parts])
        else:
            path = '/'.join(path_parts)
        size = f[b'length']
        total += size
        print(f'  {size/1024/1024/1024:.2f} GB  {path}')
    print(f'Total: {total/1024/1024/1024:.2f} GB')
else:
    size = info.get(b'length', 0)
    print(f'  {size/1024/1024/1024:.2f} GB  (single file)')
print()
announce = t.get(b'announce', b'none')
if isinstance(announce, bytes):
    announce = announce.decode('utf-8', errors='replace')
print('Main Tracker:', announce)
if b'announce-list' in t:
    print('All Trackers:')
    for tier in t[b'announce-list']:
        for tracker in tier:
            if isinstance(tracker, bytes):
                print(' ', tracker.decode('utf-8', errors='replace'))
