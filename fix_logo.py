with open('install.html', 'r', encoding='utf-8') as f:
    c = f.read()

logo_img = '<img src="assets/logo.png" style="width:16px;height:16px;object-fit:contain;vertical-align:middle;margin-right:4px;">'

# Replace semua 🦎 di dalam qs-body / code blocks dengan logo
# Tapi jangan ganti yang di luar code block (judul dll)
c = c.replace('🦎 EvoClaw Proxy v0.2.1', logo_img + ' EvoClaw Proxy v0.2.1')
c = c.replace('🦎 EvoClaw learns in the background', logo_img + ' EvoClaw learns in the background')

with open('install.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
count = c.count('assets/logo.png')
print(f'logo.png occurrences: {count}')
print('Done!')
