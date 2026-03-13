with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: Add ASK EVOCLAW + PLAYGROUND to nav if missing
if 'ASK EVOCLAW' not in c:
    old = '<li><a href="#get-started">GET STARTED</a></li>\n    </ul>'
    new = '<li><a href="#get-started">GET STARTED</a></li>\n      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>\n      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>\n    </ul>'
    if old in c:
        c = c.replace(old, new)
        print("✅ ASK EVOCLAW + PLAYGROUND added to nav")
    else:
        # Try finding nav-links end
        import re
        # Find the </ul> that closes nav-links
        idx = c.find('<ul class="nav-links">')
        if idx > 0:
            end = c.find('</ul>', idx)
            old2 = c[idx:end+5]
            new2 = old2.replace('</ul>', '      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>\n      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>\n    </ul>')
            c = c.replace(old2, new2)
            print("✅ ASK EVOCLAW + PLAYGROUND added (method 2)")
else:
    print("✅ ASK EVOCLAW already in nav")

# Fix 2: Replace emoji icons in proxy flow with EvoClaw logo img or text
c = c.replace('<div class="pf-icon">📱</div>', '<div class="pf-icon" style="font-size:.65rem;font-family:var(--mono);color:var(--green);letter-spacing:.05em;">APP</div>')
c = c.replace('<div class="pf-icon">🦎</div>', '<div class="pf-icon"><img src="assets/logo.png" style="width:32px;height:32px;object-fit:contain;" alt="EvoClaw"></div>')
c = c.replace('<div class="pf-icon">🤖</div>', '<div class="pf-icon" style="font-size:.65rem;font-family:var(--mono);color:var(--green);letter-spacing:.05em;">LLM</div>')
c = c.replace('<div class="pf-icon">✨</div>', '<div class="pf-icon" style="font-size:.65rem;font-family:var(--mono);color:var(--green);letter-spacing:.05em;">OUT</div>')
print("✅ Icons replaced with logo")

# Verify
print("\nVerification:")
print("  ASK EVOCLAW:", 'ASK EVOCLAW' in c)
print("  PLAYGROUND:", 'PLAYGROUND' in c)
print("  logo.png in flow:", 'assets/logo.png' in c)
print("  lines:", len(c.splitlines()))

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("\nDONE")
