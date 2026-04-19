import re

f = open(r'C:\Users\user.V915-31\ltx23.torrent', 'rb')
data = f.read()
f.close()
text = data.decode('latin-1', errors='replace')

# Find all file entries: path string followed by length
# Pattern: (path_len):(path_content) ... 6:lengthi(NUMBER)e
# In bencode, files are stored as: '6:lengthi{N}e'
pattern = r'(\d+):pathl(.+?)6:lengthi(\d+)e'
matches = re.findall(pattern, text, re.DOTALL)

for path_len, path_content, size in matches:
    # Extract actual file path from path_content
    # Format: (name_len):(name)...
    name_pattern = r'(\d+):(.+?)(?=\d+:|$)'
    name_matches = re.findall(name_pattern, path_content, re.DOTALL)
    full_path = '/'.join([nm[1] for nm in name_matches])
    size_gb = int(size) / 1e9
    print(f'{full_path:<70} {size_gb:>8.2f} GB')
