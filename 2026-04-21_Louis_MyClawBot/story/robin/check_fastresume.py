import re

for fname in ['7043633976cc98ccd355e660528042f14525e49f.fastresume', 'b871c46af02e622d4d25d0e26c3496e19c3e64b6.fastresume']:
    path = rf'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\{fname}'
    try:
        f = open(path, 'rb')
        data = f.read()
        f.close()
        text = data.decode('latin-1', errors='replace')
        print(f'=== {fname[:16]}... ===')
        for key in ['num_complete', 'num_incomplete', 'seeding_time', 'paused', 'stopped', 'save_path']:
            idx = text.find(key)
            if idx >= 0:
                snippet = text[idx:idx+80].replace('\n', ' ')[:80]
                print(f'  {key}: {snippet}')
        print()
    except Exception as e:
        print(f'{fname}: {e}')
