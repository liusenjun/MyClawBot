import re

# Read the torrent file
torrent_path = r'C:\Users\user.V915-31\AppData\Local\qBittorrent\BT_backup\b871c46af02e622d4d25d0e26c3496e19c3e64b6.torrent'
f = open(torrent_path, 'rb')
data = f.read()
f.close()

# The torrent file is bencoded. Let's find the announce URL and add more trackers.
text = data.decode('latin-1', errors='replace')

# Find announce
idx = text.find("announce")
if idx >= 0:
    end = text.find("e", idx)
    announce = text[idx+8:end]
    print(f"Current announce: {announce}")

# Find announce-list (if exists)
idx2 = text.find("announce-list")
if idx2 >= 0:
    print("Has announce-list!")
    print(text[idx2:idx2+200])
else:
    print("No announce-list")

# Let's also look for the info section to verify this is the right torrent
idx3 = text.find("4:pathl")
print(f"\nFirst file path at: {idx3}")
print(text[idx3:idx3+100])
