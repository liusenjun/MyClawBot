import struct, json, os

for fname in ['flux2-vae.safetensors', 'LTX2_video_vae_bf16.safetensors', 'LTX2_audio_vae_bf16_test.safetensors']:
    path = r'C:\Users\user.V915-31\Documents\ComfyUI\models\vae\{}'.format(fname)
    if not os.path.exists(path):
        print('{}: FILE NOT FOUND'.format(fname))
        continue
    size = os.path.getsize(path)
    try:
        with open(path, 'rb') as f:
            header_size_bytes = f.read(8)
            if len(header_size_bytes) < 8:
                print('{}: File too small ({} bytes)'.format(fname, size))
                continue
            header_size = struct.unpack('<Q', header_size_bytes)[0]
            if header_size > 1000000:
                print('{}: SUSPICIOUS header size {}'.format(fname, header_size))
                continue
            header = json.loads(f.read(header_size))
        gb = size / (1024*1024*1024)
        print('{}: {:.2f} GB | {} tensors'.format(fname, gb, len(header)))
    except Exception as e:
        print('{}: ERROR - {}'.format(fname, e))
