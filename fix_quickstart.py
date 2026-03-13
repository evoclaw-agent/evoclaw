with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix line 1176 - replace old pip install with new
old = 'pip</span> install fastapi uvicorn httpx openai transformers tinker tinker-cookbook'
new = 'pip</span> install evoclaw'

if old in c:
    c = c.replace(old, new)
    # Also fix the comment above it
    c = c.replace('# 1. Install dependencies', '# 1. Install EvoClaw')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - pip install evoclaw updated')
else:
    print('NOT FOUND')
    # Show what is there
    idx = c.find('fastapi')
    if idx > 0:
        print('Found fastapi at:', idx)
        print(repr(c[idx-50:idx+100]))

# Also fix the backtick-n issue in navbar
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

if '`n' in c:
    c = c.replace('</li>`n      <li>', '</li>\n      <li>')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - backtick-n fixed in navbar')
else:
    print('No backtick-n found (already clean)')

# Verify
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()
print('pip install evoclaw:', 'pip install evoclaw' in c)
print('install.html in nav:', 'install.html' in c)
print('backtick-n remaining:', '`n' in c)
