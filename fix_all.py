import re

# ── FIX 1: index.html - move proxy section higher (after hero, before features) ──
with open('index.html', 'r', encoding='utf-8') as f:
    index = f.read()

# Check where proxy section is now vs where hero ends
has_proxy = 'id="how-it-works"' in index
print(f"index.html - proxyFlow: {has_proxy}, lines: {len(index.splitlines())}")

# Move proxy section: extract it, then re-insert right after hero stats section
if has_proxy:
    # Extract the proxy section
    start = index.find('\n<!-- ── PROXY FLOW SECTION ── -->')
    if start < 0:
        start = index.find('<section id="how-it-works"')
    end = index.find('</section>', start) + len('</section>')
    
    # Also grab the <style> and <script> blocks that follow
    style_start = index.find('\n<style>\n.pf-node', end - 50)
    script_end = index.find('</script>\n', style_start) + len('</script>\n')
    
    if style_start > 0:
        proxy_block = index[start:script_end]
        rest = index[:start] + index[script_end:]
    else:
        proxy_block = index[start:end]
        rest = index[:start] + index[end:]
    
    # Find insertion point: right after hero section ends (look for first regular <section)
    # Insert after the stats row / hero wrap ends
    insert_after = '</section>\n\n<!-- ── DIVIDER'
    if insert_after not in rest:
        insert_after = '<!-- ── FEATURES'
    if insert_after not in rest:
        # Just insert before get-started
        insert_after = '<section class="section" id="get-started"'
        rest = rest.replace(insert_after, proxy_block + '\n\n' + insert_after)
    else:
        rest = rest.replace(insert_after, proxy_block + '\n\n' + insert_after, 1)
    
    index = rest
    print("✅ Proxy section repositioned")

# Add mobile CSS for proxy flow
mobile_css = '''
<style>
@media (max-width: 768px) {
  #proxyFlow > div:first-child {
    flex-wrap: wrap !important;
    gap: 8px !important;
    justify-content: center !important;
  }
  .pf-node { min-width: 80px !important; padding: 12px !important; }
  .pf-node-main { min-width: 110px !important; }
  .pf-arrow { display: none !important; }
  .pf-icon img { width: 24px !important; height: 24px !important; }
}
</style>'''

if 'pf-node { min-width: 80px' not in index:
    index = index.replace('</head>', mobile_css + '\n</head>')
    print("✅ Mobile CSS added for index.html")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index)
print(f"index.html saved: {len(index.splitlines())} lines")

# ── FIX 2: demo.html - add ASK EVOCLAW + PLAYGROUND to nav + mobile fix ──
with open('demo.html', 'r', encoding='utf-8') as f:
    demo = f.read()

print(f"\ndemo.html - ASK EVOCLAW: {'ASK EVOCLAW' in demo}, lines: {len(demo.splitlines())}")

if 'ASK EVOCLAW' not in demo:
    idx = demo.find('<ul class="nav-links">')
    if idx > 0:
        end_ul = demo.find('</ul>', idx)
        old_ul = demo[idx:end_ul+5]
        # Find GET STARTED line and add after it
        new_ul = old_ul.replace(
            '</ul>',
            '      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>\n      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>\n    </ul>'
        )
        demo = demo.replace(old_ul, new_ul)
        print("✅ ASK EVOCLAW + PLAYGROUND added to demo nav")

# Add mobile CSS for iflow
demo_mobile = '''
<style>
@media (max-width: 768px) {
  .iflow-stage { flex-direction: column; gap: 12px; padding: 16px; }
  .iflow-num { font-size: 1rem; }
  .iflow-code { font-size: .65rem; word-break: break-all; }
}
</style>'''

if 'iflow-stage { flex-direction' not in demo:
    demo = demo.replace('</head>', demo_mobile + '\n</head>')
    print("✅ Mobile CSS added for demo.html")

with open('demo.html', 'w', encoding='utf-8') as f:
    f.write(demo)
print(f"demo.html saved: {len(demo.splitlines())} lines")

# ── FIX 3: playground.html - add ASK EVOCLAW if missing + mobile fix ──
with open('playground.html', 'r', encoding='utf-8') as f:
    pg = f.read()

print(f"\nplayground.html - pgTerminal: {'pgTerminal' in pg}, lines: {len(pg.splitlines())}")

# Mobile fix for proxy dashboard grid
pg_mobile = '''
<style>
@media (max-width: 768px) {
  #pgTerminal { min-height: 160px !important; }
  div[style*="grid-template-columns:1fr 300px"] {
    grid-template-columns: 1fr !important;
  }
}
</style>'''

if 'grid-template-columns: 1fr !important' not in pg:
    pg = pg.replace('</head>', pg_mobile + '\n</head>')
    print("✅ Mobile CSS added for playground.html")

with open('playground.html', 'w', encoding='utf-8') as f:
    f.write(pg)
print(f"playground.html saved: {len(pg.splitlines())} lines")

print("\n=== ALL DONE ===")
print("Run: git add -f index.html demo.html playground.html")
