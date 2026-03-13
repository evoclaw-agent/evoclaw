with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"docs.html: {len(c.splitlines())} lines")

# Fix 1: scrollToSection uses global event.target (BROKEN)
# Replace with btn parameter version
old_fn = """function scrollToSection(id){
    const el=document.getElementById(id);
    if(el){ el.scrollIntoView({behavior:'smooth',block:'start'}); }
    document.querySelectorAll('.sb-link').forEach(b=>b.classList.remove('active'));
    event.target.classList.add('active');
  }"""

new_fn = """function scrollToSection(id, btn){
    const el=document.getElementById(id);
    if(el){ el.scrollIntoView({behavior:'smooth',block:'start'}); }
    document.querySelectorAll('.sb-link').forEach(b=>b.classList.remove('active'));
    // btn may be the span inside button - walk up to the button
    if(btn){
      var target = btn;
      while(target && target.tagName !== 'BUTTON') target = target.parentElement;
      if(target) target.classList.add('active');
    }
  }"""

if old_fn in c:
    c = c.replace(old_fn, new_fn)
    print("✅ scrollToSection function fixed (event.target → btn parameter)")
else:
    # Try partial match - just replace the function body
    import re
    c = re.sub(
        r'function scrollToSection\(id\)\{[^}]+event\.target\.classList\.add\(\'active\'\);\s*\}',
        new_fn.strip(),
        c
    )
    print("✅ scrollToSection fixed via regex")

# Fix 2: Update all onclick calls to pass 'this'
# onclick="scrollToSection('xxx')" → onclick="scrollToSection('xxx', this)"
import re
c = re.sub(
    r"onclick=\"scrollToSection\('([^']+)'\)\"",
    r"onclick=\"scrollToSection('\1', this)\"",
    c
)
print("✅ All onclick calls updated to pass 'this'")

# Fix 3: Make sure sidebar stays visible - remove any display:none on mobile for sidebar
# Add CSS to keep sidebar always visible on desktop
sidebar_fix = """
<style id="sidebar-fix">
/* Keep sidebar stable */
.docs-sidebar { display: block !important; visibility: visible !important; }
.sb-link { 
  display: flex !important; 
  align-items: center !important;
  width: 100% !important;
}
.sb-link:focus { outline: none !important; }
@media (max-width: 768px) {
  .docs-layout { 
    grid-template-columns: 1fr !important; 
  }
  .docs-sidebar { 
    position: relative !important;
    height: auto !important;
    border-right: none !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 16px !important;
    overflow: visible !important;
  }
}
</style>"""

if 'sidebar-fix' not in c:
    c = c.replace('</head>', sidebar_fix + '\n</head>')
    print("✅ Sidebar stability CSS added")

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f"\n✅ docs.html saved: {len(c.splitlines())} lines")
print("git add -f docs.html")
