import re

path = r'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\b871c46af02e622d4d25d0e26c3496e19c3e64b6.torrent'
f = open(path, 'rb')
data = f.read()
f.close()

text = data.decode('latin-1', errors='replace')

print('=== Announce ===')
idx = text.find('announce')
print(text[idx:idx+100])

print('=== Files ===')
# Find file entries: look for '4:pathl' (file path list)
file_pattern = r'4:pathl(.+?)6:lengthi(\d+)e'
matches = re.findall(file_pattern, text, re.DOTALL)
for m in matches[:30]:
    # Extract file name from path content
    name_match = re.search(r'(\d+):(.+?)(?=6:lengthi|$)', m[0], re.DOTALL)
    if name_match:
        name = name_match.group(2)[:60]
        size = int(m[1])
        print(f'  {size/1e9:8.2f} GB  {name}')
