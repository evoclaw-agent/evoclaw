import re

PAGES = {
    'index.html':      'home',
    'demo.html':       'demo',
    'docs.html':       'docs',
    'playground.html': 'playground',
    'ask.html':        'ask',
}

# ── Nav items ──
NAV_ITEMS = [
    ('index.html',           'HOME',         ''),
    ('demo.html',            'LIVE DEMO',    ''),
    ('docs.html',            'DOCS',         ''),
    ('index.html#get-started','GET STARTED', ''),
    ('ask.html',             'ASK EVOCLAW',  'color:var(--green)'),
    ('playground.html',      'PLAYGROUND',   'color:var(--green)'),
]

# ── Mobile CSS + hamburger script to inject ──
MOBILE_CSS = '''
<style id="mobile-nav-fix">
/* ── Mobile nav ── */
@media (max-width: 900px) {
  .hamburger { display:flex !important; }
  .nav-links  { display:none !important; }
  .nav-cta    { display:none !important; }
}
@media (min-width: 901px) {
  .hamburger   { display:none !important; }
  .nav-links   { display:flex !important; }
  .mobile-menu { display:none !important; }
}
/* Hamburger icon */
.hamburger {
  flex-direction:column; justify-content:center;
  gap:5px; cursor:pointer; padding:8px;
  background:none; border:none; z-index:1001;
  flex-shrink:0; margin-left:auto;
}
.hamburger span {
  display:block; width:22px; height:2px;
  background:#00ff88; border-radius:2px; transition:all .3s;
}
.hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.hamburger.open span:nth-child(2){opacity:0; transform:scaleX(0);}
.hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
/* Mobile slide-in menu */
.mobile-menu {
  position:fixed; top:0; right:-100%; width:260px; height:100vh;
  background:#0a0f0a; border-left:1px solid var(--border);
  z-index:1100; padding:24px 20px;
  display:flex; flex-direction:column; gap:4px;
  transition:right .3s cubic-bezier(.4,0,.2,1);
}
.mobile-menu.open { right:0; }
.mobile-overlay {
  position:fixed; inset:0; background:rgba(0,0,0,.6);
  z-index:1099; opacity:0; pointer-events:none;
  transition:opacity .3s;
}
.mobile-overlay.open { opacity:1; pointer-events:all; }
.mobile-close {
  align-self:flex-end; background:none; border:1px solid var(--border);
  color:var(--text); width:32px; height:32px; border-radius:50%;
  cursor:pointer; font-size:1rem; display:flex;
  align-items:center; justify-content:center; margin-bottom:12px;
  flex-shrink:0;
}
.mobile-close:hover { border-color:var(--green); color:var(--green); }
.mobile-menu-title {
  font-family:var(--mono); font-size:.6rem; letter-spacing:.15em;
  color:var(--dim); padding:0 4px; margin-bottom:8px;
}
.mobile-menu a {
  font-family:var(--mono); font-size:.78rem; letter-spacing:.1em;
  color:var(--muted); padding:12px 8px;
  border-bottom:1px solid var(--border); text-decoration:none;
  transition:color .2s;
}
.mobile-menu a:hover, .mobile-menu a.active { color:var(--text); }
.mobile-menu a.green { color:var(--green); }
.mobile-menu a.active { color:#fff; }
.mobile-github-btn {
  margin-top:auto; background:var(--green); color:#000 !important;
  font-weight:700; text-align:center; border-radius:6px;
  border:none !important; padding:12px !important;
}
/* Viewport fix - prevent zoom */
</style>'''

MOBILE_SCRIPT = '''
<script id="mobile-nav-script">
(function(){
  var btn=document.getElementById('hamburger');
  var menu=document.getElementById('mobileMenu');
  var overlay=document.getElementById('mobileOverlay');
  var closeBtn=document.getElementById('mobileClose');
  if(!btn||!menu) return;
  function openMenu(){ menu.classList.add('open'); overlay.classList.add('open'); btn.classList.add('open'); document.body.style.overflow='hidden'; }
  function closeMenu(){ menu.classList.remove('open'); overlay.classList.remove('open'); btn.classList.remove('open'); document.body.style.overflow=''; }
  btn.addEventListener('click', function(){ menu.classList.contains('open')?closeMenu():openMenu(); });
  if(closeBtn) closeBtn.addEventListener('click', closeMenu);
  overlay.addEventListener('click', closeMenu);
  menu.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', closeMenu); });
})();
</script>'''

def build_nav_html(active_page):
    items = ''
    for href, label, style in NAV_ITEMS:
        is_active = (
            (active_page=='home'       and href=='index.html') or
            (active_page=='demo'       and href=='demo.html') or
            (active_page=='docs'       and href=='docs.html') or
            (active_page=='ask'        and href=='ask.html') or
            (active_page=='playground' and href=='playground.html')
        )
        active_cls = ' class="active"' if is_active else ''
        style_attr = f' style="{style}"' if style else ''
        items += f'\n      <li><a href="{href}"{style_attr}{active_cls}>{label}</a></li>'
    return f'<ul class="nav-links">{items}\n    </ul>'

def build_mobile_menu_html(active_page):
    items = ''
    for href, label, style in NAV_ITEMS:
        is_active = (
            (active_page=='home'       and href=='index.html') or
            (active_page=='demo'       and href=='demo.html') or
            (active_page=='docs'       and href=='docs.html') or
            (active_page=='ask'        and href=='ask.html') or
            (active_page=='playground' and href=='playground.html')
        )
        cls_parts = []
        if 'green' in style: cls_parts.append('green')
        if is_active: cls_parts.append('active')
        cls = f' class="{" ".join(cls_parts)}"' if cls_parts else ''
        items += f'\n  <a href="{href}"{cls}>{label}</a>'
    return f'''<div class="mobile-overlay" id="mobileOverlay"></div>
<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-close" id="mobileClose" aria-label="Close">✕</button>
  <span class="mobile-menu-title">NAVIGATION</span>{items}
  <a href="https://github.com/evoclaw-agent/evoclaw" target="_blank" class="mobile-github-btn">GITHUB →</a>
</div>'''

def fix_page(filename, active_page):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print(f'⚠ {filename} not found')
        return

    # 1. Fix viewport meta
    if 'name="viewport"' in html:
        html = re.sub(
            r'<meta name="viewport"[^>]+>',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">',
            html
        )
    else:
        html = html.replace('</head>', '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">\n</head>')

    # 2. Remove old mobile-nav-fix style if exists
    html = re.sub(r'<style id="mobile-nav-fix">.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script id="mobile-nav-script">.*?</script>', '', html, flags=re.DOTALL)

    # 3. Inject mobile CSS before </head>
    html = html.replace('</head>', MOBILE_CSS + '\n</head>')

    # 4. Fix nav-links ul
    idx = html.find('<ul class="nav-links">')
    if idx >= 0:
        end = html.find('</ul>', idx) + 5
        html = html[:idx] + build_nav_html(active_page) + html[end:]

    # 5. Ensure hamburger button exists in nav
    if 'id="hamburger"' not in html:
        html = html.replace(
            '</div>\n</nav>',
            '    <button class="hamburger" id="hamburger" aria-label="Menu"><span></span><span></span><span></span></button>\n  </div>\n</nav>'
        )

    # 6. Replace old mobile overlay+menu block
    old_overlay = html.find('<div class="mobile-overlay"')
    old_menu_end = html.find('</div>', html.find('<div class="mobile-menu"'))
    if old_overlay > 0 and old_menu_end > 0:
        html = html[:old_overlay] + build_mobile_menu_html(active_page) + html[old_menu_end+6:]
    elif '</nav>' in html:
        # Insert after </nav>
        html = html.replace('</nav>\n', '</nav>\n' + build_mobile_menu_html(active_page) + '\n', 1)

    # 7. Remove old hamburger scripts (old inline ones) and add new one
    html = re.sub(r'<script>\s*\(function\(\)\{\s*var btn = document\.getElementById\(\'hamburger\'\).*?\}\)\(\);\s*</script>', '', html, flags=re.DOTALL)
    # Add before </body>
    html = html.replace('</body>', MOBILE_SCRIPT + '\n</body>')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    has_hamburger = 'id="hamburger"' in html
    has_mobile_menu = 'id="mobileMenu"' in html
    has_playground = 'PLAYGROUND' in html
    print(f'✅ {filename}: {len(html.splitlines())} lines | hamburger:{has_hamburger} | menu:{has_mobile_menu} | playground:{has_playground}')

for fname, active in PAGES.items():
    fix_page(fname, active)

print('\n=== ALL DONE ===')
print('git add -f index.html demo.html docs.html playground.html ask.html')
