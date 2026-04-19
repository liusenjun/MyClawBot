import re

path = r'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\b871c46af02e622d4d25d0e26c3496e19c3e64b6.fastresume'
f = open(path, 'rb')
data = f.read()
f.close()
text = data.decode('latin-1', errors='replace')
idx = text.find('save_path')
if idx >= 0:
    snippet = text[idx:idx+60].replace('\n', ' ')
    print('save_path:', snippet)
