import re

PAGES = ['index.html', 'demo.html', 'docs.html', 'playground.html', 'ask.html']

# ── Global mobile CSS to inject ──
GLOBAL_MOBILE_CSS = '''<style id="global-mobile">
/* ══ GLOBAL OVERFLOW FIX ══ */
*, *::before, *::after { box-sizing: border-box; }
html, body {
  overflow-x: hidden !important;
  max-width: 100vw !important;
  width: 100% !important;
}

/* ══ MOBILE NAV ══ */
@media (max-width: 900px) {
  .nav-inner {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 0 16px !important;
    width: 100% !important;
  }
  .nav-links { display: none !important; }
  .nav-cta   { display: none !important; }
  .hamburger {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    gap: 5px !important;
    cursor: pointer !important;
    padding: 8px !important;
    background: none !important;
    border: none !important;
    margin-left: auto !important;
    flex-shrink: 0 !important;
  }
  .hamburger span {
    display: block !important;
    width: 22px !important;
    height: 2px !important;
    background: #00ff88 !important;
    border-radius: 2px !important;
    transition: all .3s !important;
  }
  .hamburger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg) !important; }
  .hamburger.open span:nth-child(2) { opacity: 0 !important; }
  .hamburger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg) !important; }
}
@media (min-width: 901px) {
  .hamburger { display: none !important; }
  .nav-links  { display: flex !important; }
}

/* ══ MOBILE SLIDE MENU ══ */
.mobile-menu {
  position: fixed !important;
  top: 0 !important; right: -100% !important;
  width: 260px !important; height: 100vh !important;
  background: #0a0f0a !important;
  border-left: 1px solid var(--border) !important;
  z-index: 9999 !important;
  padding: 20px 16px 20px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 0 !important;
  transition: right .3s cubic-bezier(.4,0,.2,1) !important;
  overflow-y: auto !important;
}
.mobile-menu.open { right: 0 !important; }
.mobile-overlay {
  position: fixed !important;
  inset: 0 !important;
  background: rgba(0,0,0,.65) !important;
  z-index: 9998 !important;
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity .3s !important;
}
.mobile-overlay.open { opacity: 1 !important; pointer-events: all !important; }
.mobile-close {
  align-self: flex-end !important;
  background: none !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  width: 30px !important; height: 30px !important;
  border-radius: 50% !important;
  cursor: pointer !important;
  font-size: .9rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin-bottom: 16px !important;
  flex-shrink: 0 !important;
}
.mobile-close:hover { border-color: var(--green) !important; color: var(--green) !important; }
.mobile-menu-title { display: none !important; }
.mobile-menu a {
  font-family: var(--mono) !important;
  font-size: .82rem !important;
  letter-spacing: .08em !important;
  color: var(--muted) !important;
  padding: 11px 6px !important;
  border-bottom: 1px solid rgba(255,255,255,.06) !important;
  text-decoration: none !important;
  transition: color .2s !important;
  display: block !important;
}
.mobile-menu a:hover { color: #fff !important; }
.mobile-menu a.green { color: var(--green) !important; }
.mobile-menu a.active { color: #fff !important; font-weight: 600 !important; }
.mobile-github-btn {
  margin-top: 12px !important;
  background: var(--green) !important;
  color: #000 !important;
  font-weight: 700 !important;
  text-align: center !important;
  border-radius: 6px !important;
  border: none !important;
  padding: 12px !important;
}

/* ══ CONTENT OVERFLOW FIXES ══ */
@media (max-width: 768px) {
  /* Container */
  .container { padding-left: 16px !important; padding-right: 16px !important; max-width: 100% !important; }

  /* Hero */
  .hero-wrap, .hero-content { overflow: hidden !important; }
  .hero-stats {
    grid-template-columns: repeat(3, 1fr) !important;
    font-size: .8rem !important;
  }
  .hero-stats .hs:nth-child(4),
  .hero-stats .hs:nth-child(5) { display: none !important; }

  /* Sections with 2-col grid → 1 col */
  [style*="grid-template-columns:1fr 1fr"],
  [style*="grid-template-columns: 1fr 1fr"] {
    grid-template-columns: 1fr !important;
    gap: 32px !important;
  }
  [style*="grid-template-columns:1fr 320px"],
  [style*="grid-template-columns:1fr 300px"],
  [style*="grid-template-columns: 1fr 320px"],
  [style*="grid-template-columns: 1fr 300px"] {
    grid-template-columns: 1fr !important;
  }

  /* Mini demo / terminal - prevent overflow */
  .mini-demo, .md-body { max-width: 100% !important; overflow-x: hidden !important; }
  .md-line { word-break: break-word !important; white-space: normal !important; }

  /* Features grid */
  .features-grid { grid-template-columns: 1fr !important; }

  /* Code blocks */
  pre, code, .iflow-code {
    word-break: break-all !important;
    white-space: pre-wrap !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
  }

  /* Proxy flow */
  #proxyFlow > div:first-child {
    flex-wrap: wrap !important;
    gap: 8px !important;
    justify-content: center !important;
    overflow: hidden !important;
  }
  .pf-node { min-width: 70px !important; padding: 10px 8px !important; }
  .pf-node-main { min-width: 100px !important; }
  .pf-arrow { display: none !important; }

  /* Proxy stats grid */
  #proxyFlow [style*="grid-template-columns:repeat(4"] {
    grid-template-columns: repeat(2, 1fr) !important;
  }

  /* Intercept flow */
  .iflow-stage { flex-direction: column !important; padding: 16px !important; }
  .iflow-stage .iflow-status { align-self: flex-start !important; }

  /* Playground terminal */
  #pgTerminal { min-height: 140px !important; font-size: .68rem !important; }

  /* HOW IT WORKS 2-col section */
  .section [style*="display:grid"] { grid-template-columns: 1fr !important; }

  /* Hide right panel of HOW IT WORKS on mobile to prevent overflow */
  .mini-demo { max-width: 100% !important; width: 100% !important; overflow: hidden !important; }

  /* Buttons */
  .hero-actions { flex-direction: column !important; align-items: stretch !important; }
  .hero-actions a { text-align: center !important; }

  /* Section titles */
  .section-title { font-size: clamp(1.4rem, 5vw, 2rem) !important; }

  /* Tables / long content */
  table { display: block !important; overflow-x: auto !important; }
}
</style>'''

MOBILE_SCRIPT = '''<script id="mobile-nav-js">
(function(){
  var btn = document.getElementById('hamburger');
  var menu = document.getElementById('mobileMenu');
  var overlay = document.getElementById('mobileOverlay');
  var closeBtn = document.getElementById('mobileClose');
  if (!btn || !menu) return;
  function openMenu() {
    menu.classList.add('open');
    if(overlay) overlay.classList.add('open');
    btn.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    menu.classList.remove('open');
    if(overlay) overlay.classList.remove('open');
    btn.classList.remove('open');
    document.body.style.overflow = '';
  }
  btn.addEventListener('click', function() {
    menu.classList.contains('open') ? closeMenu() : openMenu();
  });
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  if (overlay) overlay.addEventListener('click', closeMenu);
  menu.querySelectorAll('a').forEach(function(a) {
    a.addEventListener('click', closeMenu);
  });
})();
</script>'''

NAV_ITEMS = [
    ('index.html',            'HOME',        ''),
    ('demo.html',             'LIVE DEMO',   ''),
    ('docs.html',             'DOCS',        ''),
    ('index.html#get-started','GET STARTED', ''),
    ('ask.html',              'ASK EVOCLAW', 'green'),
    ('playground.html',       'PLAYGROUND',  'green'),
]

def build_mobile_menu(active):
    links = ''
    for href, label, cls in NAV_ITEMS:
        is_active = (
            (active=='home'       and href=='index.html') or
            (active=='demo'       and href=='demo.html') or
            (active=='docs'       and href=='docs.html') or
            (active=='ask'        and href=='ask.html') or
            (active=='playground' and href=='playground.html')
        )
        classes = []
        if cls: classes.append(cls)
        if is_active: classes.append('active')
        cls_attr = f' class="{" ".join(classes)}"' if classes else ''
        links += f'\n  <a href="{href}"{cls_attr}>{label}</a>'
    return f'''<div class="mobile-overlay" id="mobileOverlay"></div>
<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-close" id="mobileClose" aria-label="Close">✕</button>{links}
  <a href="https://github.com/evoclaw-agent/evoclaw" target="_blank" class="mobile-github-btn">GITHUB →</a>
</div>'''

ACTIVE_MAP = {
    'index.html': 'home', 'demo.html': 'demo', 'docs.html': 'docs',
    'playground.html': 'playground', 'ask.html': 'ask'
}

for fname in PAGES:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print(f'⚠ {fname} not found')
        continue

    active = ACTIVE_MAP.get(fname, 'home')

    # 1. Fix viewport
    html = re.sub(r'<meta name="viewport"[^>]+>', '', html)
    html = html.replace('<head>', '<head>\n<meta name="viewport" content="width=device-width, initial-scale=1.0">')

    # 2. Remove old mobile style/script injections
    html = re.sub(r'<style id="mobile-nav-fix">.*?</style>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<style id="global-mobile">.*?</style>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<script id="mobile-nav-script">.*?</script>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<script id="mobile-nav-js">.*?</script>\s*', '', html, flags=re.DOTALL)

    # 3. Remove duplicate mobile CSS blocks
    html = re.sub(r'<style>\s*@media\s*\(max-width:\s*768px\)\s*\{\s*#proxyFlow.*?</style>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<style>\s*@media\s*\(max-width:\s*700px\)\s*\{.*?</style>\s*', '', html, flags=re.DOTALL)

    # 4. Inject global mobile CSS before </head>
    html = html.replace('</head>', GLOBAL_MOBILE_CSS + '\n</head>')

    # 5. Ensure hamburger in nav
    if 'id="hamburger"' not in html:
        html = html.replace(
            '</div>\n</nav>',
            '    <button class="hamburger" id="hamburger" aria-label="Menu"><span></span><span></span><span></span></button>\n  </div>\n</nav>'
        )

    # 6. Replace mobile overlay+menu
    start = html.find('<div class="mobile-overlay"')
    if start >= 0:
        # Find end of mobile-menu div
        menu_start = html.find('<div class="mobile-menu"', start)
        menu_end = html.find('</div>', menu_start) + 6
        html = html[:start] + build_mobile_menu(active) + html[menu_end:]
    else:
        # Insert after </nav>
        nav_end = html.find('</nav>') + 6
        html = html[:nav_end] + '\n' + build_mobile_menu(active) + html[nav_end:]

    # 7. Remove old hamburger script and add new
    html = re.sub(
        r'<script>\s*\(function\(\)\{\s*var btn\s*=\s*document\.getElementById\(\'hamburger\'\).*?\}\)\(\);\s*</script>',
        '', html, flags=re.DOTALL
    )
    html = html.replace('</body>', MOBILE_SCRIPT + '\n</body>')

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ {fname}: {len(html.splitlines())} lines | menu:{("mobileMenu" in html)} | hamburger:{("hamburger" in html)}')

print('\n=== DONE ===')
print('git add -f index.html demo.html docs.html playground.html ask.html')
