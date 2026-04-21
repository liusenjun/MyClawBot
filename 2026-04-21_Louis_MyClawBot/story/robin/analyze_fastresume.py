import re

path = r'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\b871c46af02e622d4d25d0e26c3496e19c3e64b6.fastresume'
f = open(path, 'rb')
data = f.read()
f.close()

# Parse bencode manually - find interesting fields
text = data.decode('latin-1', errors='replace')

# Look for save_path, file paths, completed pieces, etc.
print('=== save_path ===')
idx = text.find('save_path')
if idx >= 0:
    print(text[idx:idx+100])

print('=== file sizes in torrent ===')
# Files have format: 'X:pathlen:path' followed eventually by 'X:lengthiSIZEe'
# Find all length entries
lengths = re.findall(r'6:lengthi(\d+)e', text)
total = sum(int(l) for l in lengths)
print(f'Number of files: {len(lengths)}, Total: {total/1e9:.1f} GB')
for l in lengths[:5]:
    print(f'  {int(l)/1e9:.2f} GB')

print('=== has pieces data ===')
if 'pieces' in text:
    pieces_idx = text.find('pieces')
    # pieces are binary, just check it exists
    print('Pieces data present')
    # Find how many pieces
    pieces_data = data[pieces_idx+6:pieces_idx+10]
    print(f'First 4 bytes after "pieces": {pieces_data[:4].hex()}')
