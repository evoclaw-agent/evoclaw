import os

logo = '<img src="assets/logo.png" style="width:16px;height:16px;object-fit:contain;vertical-align:middle;margin-right:4px;">'

files = ['index.html', 'install.html', 'docs.html', 'demo.html', 'ask.html', 'playground.html']

for fname in files:
    if not os.path.exists(fname):
        print(f"  skip: {fname}")
        continue

    with open(fname, 'r', encoding='utf-8') as f:
        c = f.read()

    original = c

    # Replace all 🦎 emoji inside qs-body / code blocks with logo img
    # But keep 🦎 in the main nav logo area (it uses img tag already)
    c = c.replace('🦎 EvoClaw Proxy v0.2.1', logo + ' EvoClaw Proxy v0.2.1')
    c = c.replace('🦎 EvoClaw Proxy v0.2.0', logo + ' EvoClaw Proxy v0.2.0')
    c = c.replace('🦎 EvoClaw ready', logo + ' EvoClaw ready')
    c = c.replace('🦎 EvoClaw Setup', logo + ' EvoClaw Setup')
    c = c.replace('🦎 EvoClaw learns', logo + ' EvoClaw learns')
    c = c.replace('🦎 EvoClaw v0.2', logo + ' EvoClaw v0.2')
    c = c.replace('🦎 EvoClaw v0.1', logo + ' EvoClaw v0.1')

    if c != original:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  ✅ {fname} - emoji replaced")
    else:
        print(f"  ℹ️  {fname} - no emoji found (already clean)")

print("\nDone! Now push:")
print("git add -f index.html install.html docs.html demo.html ask.html playground.html")
print('git commit -m "fix: replace all lizard emojis with EvoClaw logo"')
print("git push origin main")
