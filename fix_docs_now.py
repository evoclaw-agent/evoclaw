import re

with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"Current docs.html: {len(c.splitlines())} lines")

# ── 1. Fix scrollToSection ──
old = re.search(r'function scrollToSection\([^)]*\)\s*\{[^}]+\}', c)
if old:
    print(f"Found: {old.group()[:60]}")

c = re.sub(
    r'function scrollToSection\([^)]*\)\s*\{[^}]+\}',
    "function scrollToSection(id,el){var t=document.getElementById(id);if(t){t.scrollIntoView({behavior:'smooth',block:'start'});}document.querySelectorAll('.sb-link').forEach(function(b){b.classList.remove('active');});var btn=el;while(btn&&btn.tagName!=='BUTTON'){btn=btn.parentElement;}if(btn){btn.classList.add('active');}}",
    c
)
print("✅ scrollToSection fixed")

# ── 2. Fix all onclick to pass this ──
c = re.sub(
    r"onclick=['\"]scrollToSection\('([^']+)'[^)]*\)['\"]",
    r"onclick=\"scrollToSection('\1',this)\"",
    c
)
print("✅ onclick updated")

# ── 3. Ensure nav has all links ──
idx = c.find('<ul class="nav-links">')
end = c.find('</ul>', idx) + 5
nav_block = c[idx:end]

new_nav = '''<ul class="nav-links">
      <li><a href="index.html">HOME</a></li>
      <li><a href="demo.html">LIVE DEMO</a></li>
      <li><a href="docs.html" class="active">DOCS</a></li>
      <li><a href="index.html#get-started">GET STARTED</a></li>
      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>
      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>
    </ul>'''

c = c[:idx] + new_nav + c[end:]
print("✅ Nav links fixed")

# ── 4. Fix mobile menu ──
mob_start = c.find('<div class="mobile-menu"')
mob_end = c.find('</div>', mob_start) + 6
if mob_start > 0:
    new_mob = '''<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-close" id="mobileClose" aria-label="Close">✕</button>
  <a href="index.html">HOME</a>
  <a href="demo.html">LIVE DEMO</a>
  <a href="docs.html" class="active">DOCS</a>
  <a href="index.html#get-started">GET STARTED</a>
  <a href="ask.html" class="green">ASK EVOCLAW</a>
  <a href="playground.html" class="green">PLAYGROUND</a>
  <a href="https://github.com/evoclaw-agent/evoclaw" target="_blank" class="mobile-github-btn">GITHUB →</a>
</div>'''
    c = c[:mob_start] + new_mob + c[mob_end:]
    print("✅ Mobile menu fixed")

# ── 5. Add sidebar CSS ──
c = re.sub(r'<style id="sidebar-fix">.*?</style>\s*', '', c, flags=re.DOTALL)
sidebar_css = '''<style id="sidebar-fix">
.sidebar{display:block!important;visibility:visible!important;}
.docs-layout{display:grid!important;grid-template-columns:240px 1fr!important;}
@media(max-width:860px){
  .docs-layout{grid-template-columns:1fr!important;}
  .sidebar{position:relative!important;height:auto!important;max-height:300px!important;overflow-y:auto!important;border-right:none!important;border-bottom:1px solid var(--border)!important;}
}
</style>'''
c = c.replace('</head>', sidebar_css + '\n</head>')
print("✅ Sidebar CSS added")

# ── Verify ──
print(f"\nVerify:")
print(f"  PLAYGROUND in nav: {'PLAYGROUND' in c[c.find('<ul class=\"nav-links\">'):c.find('</ul>',c.find('<ul class=\"nav-links\">'))]}")
print(f"  event.target: {'event.target' in c}")
print(f"  onclick this: {\",this)\" in c}")
print(f"  sidebar-fix: {'sidebar-fix' in c}")
print(f"  lines: {len(c.splitlines())}")

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("\n✅ docs.html saved!")
print("git add -f docs.html && git commit -m 'fix: docs sidebar + nav' && git push origin main")
