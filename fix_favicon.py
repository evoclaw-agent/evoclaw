import re

PAGES = ['index.html', 'demo.html', 'docs.html', 'playground.html', 'ask.html']

for fname in PAGES:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            c = f.read()
    except FileNotFoundError:
        print(f'⚠ {fname} not found')
        continue

    original_lines = len(c.splitlines())

    # Remove ALL existing favicon/icon link tags (including base64 ones)
    c = re.sub(r'<link[^>]+rel=["\'](?:icon|shortcut icon|apple-touch-icon)[^>]+>\s*', '', c)

    # Inject correct favicon right after <head>
    correct_favicon = '<link rel="icon" type="image/png" href="assets/logo.png">\n  <link rel="apple-touch-icon" href="assets/logo.png">'
    c = c.replace('<head>\n', '<head>\n  ' + correct_favicon + '\n')

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(c)

    # Verify
    has_logo = 'assets/logo.png' in c
    has_base64 = 'data:image/png;base64' in c and 'rel="icon"' in c
    print(f'✅ {fname}: logo.png={has_logo} | base64_icon={has_base64} | lines={len(c.splitlines())}')

print('\n=== DONE ===')
print('git add -f index.html demo.html docs.html playground.html ask.html')
