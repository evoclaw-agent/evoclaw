import re

with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix nav - replace entire nav-links
old_nav_start = c.find('<ul class="nav-links">')
old_nav_end = c.find('</ul>', old_nav_start) + 5
new_nav = '<ul class="nav-links">\n      <li><a href="index.html">HOME</a></li>\n      <li><a href="demo.html">LIVE DEMO</a></li>\n      <li><a href="docs.html" class="active">DOCS</a></li>\n      <li><a href="index.html#get-started">GET STARTED</a></li>\n      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>\n      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>\n    </ul>'
c = c[:old_nav_start] + new_nav + c[old_nav_end:]

# 2. Rename function scrollTo → navTo
c = re.sub(r'function scrollTo\([^)]*\)', 'function navTo(id,el)', c)

# 3. Fix function body
c = re.sub(
    r"document\.querySelectorAll\('\.sb-link'\)\.forEach\([^)]+\)\.forEach\([^;]+\);\s*event\.target[^;]+;",
    "document.querySelectorAll('.sb-link').forEach(function(b){b.classList.remove('active');});var btn=el;while(btn&&btn.tagName!=='BUTTON'){btn=btn.parentElement;}if(btn){btn.classList.add('active');}",
    c
)
# Also try simpler replace
c = c.replace("event.target.classList.add('active');", "var btn=el;while(btn&&btn.tagName!=='BUTTON'){btn=btn.parentElement;}if(btn){btn.classList.add('active');}")
c = re.sub(r"document\.querySelectorAll\('\.sb-link'\)\.forEach\(b=>b\.classList\.remove\('active'\)\);", 
           "document.querySelectorAll('.sb-link').forEach(function(b){b.classList.remove('active');});", c)

# 4. Fix all onclick - scrollTo → navTo with ,this
c = re.sub(r"onclick=\"scrollTo\('([^']+)'(?:,this)?\)\"", r"onclick=\"navTo('\1',this)\"", c)
c = re.sub(r"onclick=\"navTo\('([^']+)'\)\"", r"onclick=\"navTo('\1',this)\"", c)

# 5. Fix IntersectionObserver to match navTo
c = c.replace(
    "const match=[...links].find(l=>l.getAttribute('onclick')?.includes(\"'\"+id+\"'\"));",
    "const match=[...links].find(l=>l.getAttribute('onclick')?.includes(\"'\"+id+\"'\"));"
)

print("PLAYGROUND in nav:", 'PLAYGROUND' in c[c.find('<ul class="nav-links">'):c.find('</ul>', c.find('<ul class="nav-links">'))])
print("function navTo:", 'function navTo' in c)
print("function scrollTo:", 'function scrollTo' in c)
print("event.target:", 'event.target' in c)
print("onclick navTo:", c.count('onclick="navTo('))
print("onclick scrollTo:", c.count('onclick="scrollTo('))

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("SAVED")
