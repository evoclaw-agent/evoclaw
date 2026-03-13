import re

with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

print("BEFORE:")
print("  scrollTo function:", 'function scrollTo' in c)
print("  navTo function:", 'function navTo' in c)
print("  onclick sample:", c[c.find('onclick='):c.find('onclick=')+40])

# Step 1: rename function definition
c = c.replace('function scrollTo(id)', 'function navTo(id, el)')
c = c.replace('function scrollTo(id,el)', 'function navTo(id, el)')

# Step 2: fix function body - replace event.target with el-based logic
c = re.sub(
    r"document\.querySelectorAll\('\.sb-link'\)\.forEach\(b=>b\.classList\.remove\('active'\)\);\s*event\.target\.classList\.add\('active'\);",
    "document.querySelectorAll('.sb-link').forEach(function(b){b.classList.remove('active');});var btn=el;while(btn&&btn.tagName!=='BUTTON'){btn=btn.parentElement;}if(btn){btn.classList.add('active');}",
    c
)

# Step 3: replace ALL onclick="scrollTo('xxx')" with onclick="navTo('xxx',this)"
c = re.sub(r"onclick=\"scrollTo\('([^']+)'\)\"", r"onclick=\"navTo('\1',this)\"", c)
c = re.sub(r"onclick=\"scrollTo\('([^']+)',this\)\"", r"onclick=\"navTo('\1',this)\"", c)
c = re.sub(r"onclick=\"navTo\('([^']+)'\)\"", r"onclick=\"navTo('\1',this)\"", c)

# Step 4: also fix inline href onclick links
c = re.sub(r"onclick=\"scrollTo\('([^']+)',this\)\"", r"onclick=\"navTo('\1',this)\"", c)

print("\nAFTER:")
print("  scrollTo function:", 'function scrollTo' in c)
print("  navTo function:", 'function navTo' in c)
print("  onclick navTo count:", c.count("onclick=\"navTo("))
print("  onclick scrollTo count:", c.count("onclick=\"scrollTo("))
print("  onclick sample:", c[c.find('onclick='):c.find('onclick=')+45])

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("\nSAVED OK - now run:")
print("git add -f docs.html && git commit -m fix && git push origin main")
