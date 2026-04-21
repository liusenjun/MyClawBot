import re

path = r'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\7043633976cc98ccd355e660528042f14525e49f.fastresume'
f = open(path, 'rb')
data = f.read()
f.close()

# Bencode format: find all 'files' entries
# Each file has: 'length' and 'path'
text = data.decode('latin-1', errors='replace')

# Find file entries with their priorities
# Files with priority 0 are "do not download"
# Priority 1 = low, 6 = normal, 7 = high
import sys

# Look for file priorities
prio_matches = re.findall(r'file_prio\x69(\d+)e', text)
print(f'File priorities found: {len(prio_matches)}')

# Look for 'skipped' or 'paused' states
if 'skipped' in text.lower():
    print('Has skipped files!')
if 'do_not_download' in text:
    print('Has do_not_download!')

# Look for the files section
files_idx = text.find('files')
if files_idx >= 0:
    print('Files section at:', files_idx)
    print(text[files_idx:files_idx+500])
