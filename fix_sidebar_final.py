import re

with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"docs.html: {len(c.splitlines())} lines")

# Fix 1: Remove old wrong sidebar fix (targets .docs-sidebar which doesn't exist)
c = re.sub(r'<style id="sidebar-fix">.*?</style>\s*', '', c, flags=re.DOTALL)

# Fix 2: Fix scrollToSection function - robust version
c = re.sub(
    r'function scrollToSection\([^)]*\)\s*\{[^}]*\}',
    '''function scrollToSection(id, el){
    var target = document.getElementById(id);
    if(target){ target.scrollIntoView({behavior:'smooth', block:'start'}); }
    document.querySelectorAll('.sb-link').forEach(function(b){ b.classList.remove('active'); });
    var btn = el;
    while(btn && btn.tagName !== 'BUTTON'){ btn = btn.parentElement; }
    if(btn){ btn.classList.add('active'); }
  }''',
    c
)
print("✅ scrollToSection fixed")

# Fix 3: Update onclick to pass this
c = re.sub(
    r"onclick=\"scrollToSection\('([^']+)'(?:,\s*this)?\)\"",
    r"onclick=\"scrollToSection('\1', this)\"",
    c
)
print("✅ onclick updated")

# Fix 4: Add strong CSS to keep sidebar always visible
sidebar_css = """<style id="sidebar-fix">
/* ── SIDEBAR ALWAYS VISIBLE ── */
.sidebar {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}
.docs-layout {
  display: grid !important;
  grid-template-columns: 240px 1fr !important;
}
@media (max-width: 860px) {
  .docs-layout {
    grid-template-columns: 1fr !important;
  }
  .sidebar {
    position: relative !important;
    height: auto !important;
    max-height: 300px !important;
    border-right: none !important;
    border-bottom: 1px solid var(--border) !important;
  }
}
</style>"""

c = c.replace('</head>', sidebar_css + '\n</head>')
print("✅ Sidebar CSS added (correct class .sidebar)")

# Verify
print(f"\nVerification:")
print(f"  scrollToSection(id, el): {'scrollToSection(id, el)' in c}")
print(f"  event.target: {'event.target' in c}")
print(f"  onclick this: {\"scrollToSection('intro', this)\" in c}")
print(f"  .sidebar fix: {'sidebar-fix' in c}")

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Force a byte change so git detects it
print(f"\n✅ docs.html saved: {len(c.splitlines())} lines")
