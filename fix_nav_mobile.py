import re

# ════════════════════════════════════════
# HELPER: inject/replace mobile nav block
# ════════════════════════════════════════
def fix_nav(html, active_page):
    """Fix nav links to always include all items + fix mobile menu"""

    # Build correct nav-links based on active page
    nav_items = [
        ('index.html', 'HOME', '', False),
        ('demo.html', 'LIVE DEMO', '', False),
        ('docs.html', 'DOCS', '', False),
        ('index.html#get-started', 'GET STARTED', '', False),
        ('ask.html', 'ASK EVOCLAW', 'color:var(--green)', False),
        ('playground.html', 'PLAYGROUND', 'color:var(--green)', False),
    ]

    # Build <ul> with correct active class
    items_html = '\n'
    for href, label, style, _ in nav_items:
        active = ' class="active"' if (
            (active_page == 'home' and href == 'index.html') or
            (active_page == 'demo' and href == 'demo.html') or
            (active_page == 'docs' and href == 'docs.html') or
            (active_page == 'ask' and href == 'ask.html') or
            (active_page == 'playground' and href == 'playground.html')
        ) else ''
        style_attr = f' style="{style}"' if style else ''
        items_html += f'      <li><a href="{href}"{style_attr}{active}>{label}</a></li>\n'
    items_html += '    '

    new_ul = f'<ul class="nav-links">{items_html}</ul>'

    # Replace existing nav-links ul
    idx = html.find('<ul class="nav-links">')
    if idx >= 0:
        end = html.find('</ul>', idx) + 5
        html = html[:idx] + new_ul + html[end:]

    # Fix mobile menu items too
    mobile_items = ''
    for href, label, style, _ in nav_items:
        cls = ' class="green"' if 'green' in style else ''
        mobile_items += f'  <a href="{href}"{cls}>{label}</a>\n'

    # Replace mobile menu links (between mobile-menu-title and mobile-github-btn)
    idx2 = html.find('<span class="mobile-menu-title">')
    if idx2 >= 0:
        title_end = html.find('</span>', idx2) + 7
        github_btn = html.find('<a href="https://github.com', title_end)
        if github_btn > 0:
            html = html[:title_end] + '\n' + mobile_items + '  ' + html[github_btn:]

    return html


# ════════════════════════════════════════
# FIX index.html
# ════════════════════════════════════════
with open('index.html', 'r', encoding='utf-8') as f:
    index = f.read()

index = fix_nav(index, 'home')

# Fix proxy flow mobile: make nodes wrap properly
# Replace the pf-node row div to add flex-wrap
index = re.sub(
    r'(<div style="display:flex;align-items:center;justify-content:center;gap:0;)(overflow-x:auto;)',
    r'\1flex-wrap:wrap;\2',
    index
)

# Add/replace mobile CSS for proxy flow
mobile_proxy_css = """<style>
@media(max-width:700px){
  #proxyFlow>div:first-child{flex-wrap:wrap!important;gap:6px!important;}
  .pf-node{min-width:72px!important;padding:10px 8px!important;font-size:.7rem;}
  .pf-node-main{min-width:100px!important;}
  .pf-arrow{padding:0 2px!important;font-size:1rem!important;}
  #proxyFlow [style*="grid-template-columns:repeat(4"]{grid-template-columns:repeat(2,1fr)!important;}
}
</style>"""

if 'pf-node{min-width:72px' not in index:
    index = index.replace('</head>', mobile_proxy_css + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index)
print(f"✅ index.html: {len(index.splitlines())} lines | ASK: {'ASK EVOCLAW' in index} | PLAYGROUND: {'PLAYGROUND' in index}")


# ════════════════════════════════════════
# FIX demo.html
# ════════════════════════════════════════
with open('demo.html', 'r', encoding='utf-8') as f:
    demo = f.read()

demo = fix_nav(demo, 'demo')

with open('demo.html', 'w', encoding='utf-8') as f:
    f.write(demo)
print(f"✅ demo.html: {len(demo.splitlines())} lines | ASK: {'ASK EVOCLAW' in demo} | PLAYGROUND: {'PLAYGROUND' in demo}")


# ════════════════════════════════════════
# FIX playground.html
# ════════════════════════════════════════
with open('playground.html', 'r', encoding='utf-8') as f:
    pg = f.read()

pg = fix_nav(pg, 'playground')

# Mobile fix for proxy dashboard 2-col grid
pg_mobile = """<style>
@media(max-width:700px){
  div[style*="grid-template-columns:1fr 300px"]{grid-template-columns:1fr!important;}
  #pgTerminal{min-height:140px!important;font-size:.68rem!important;}
}
</style>"""
if 'grid-template-columns:1fr!important' not in pg:
    pg = pg.replace('</head>', pg_mobile + '\n</head>')

with open('playground.html', 'w', encoding='utf-8') as f:
    f.write(pg)
print(f"✅ playground.html: {len(pg.splitlines())} lines | ASK: {'ASK EVOCLAW' in pg} | PLAYGROUND: {'PLAYGROUND' in pg}")


# ════════════════════════════════════════
# FIX docs.html + ask.html (nav sync)
# ════════════════════════════════════════
for fname, active in [('docs.html','docs'), ('ask.html','ask')]:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            h = f.read()
        h = fix_nav(h, active)
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(h)
        print(f"✅ {fname}: nav synced | PLAYGROUND: {'PLAYGROUND' in h}")
    except FileNotFoundError:
        print(f"⚠ {fname} not found, skipping")

print("\n=== ALL DONE ===")
