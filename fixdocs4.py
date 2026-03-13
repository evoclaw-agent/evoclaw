with open('docs.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for line in lines:
    # Fix escaped quotes in onclick attributes
    if 'onclick=' in line and ('navTo' in line or 'scrollTo' in line):
        line = line.replace('\\"navTo(', '"navTo(')
        line = line.replace('\\"scrollTo(', '"navTo(')
        line = line.replace(',this)\\"', ',this)"')
        line = line.replace("onclick=\"scrollTo('", "onclick=\"navTo('")
        # Ensure ,this is present
        import re
        line = re.sub(r'onclick="navTo\(\'([^\']+)\'\)"', r"onclick=\"navTo('\1',this)\"", line)
        # Remove any double backslash issues
        line = line.replace('\\\\"', '\\"')
    out.append(line)

c = ''.join(out)

# Also fix nav to include PLAYGROUND
nav_start = c.find('<ul class="nav-links">')
nav_end = c.find('</ul>', nav_start) + 5
current_nav = c[nav_start:nav_end]
if 'PLAYGROUND' not in current_nav:
    new_nav = """<ul class="nav-links">
      <li><a href="index.html">HOME</a></li>
      <li><a href="demo.html">LIVE DEMO</a></li>
      <li><a href="docs.html" class="active">DOCS</a></li>
      <li><a href="index.html#get-started">GET STARTED</a></li>
      <li><a href="ask.html" style="color:var(--green)">ASK EVOCLAW</a></li>
      <li><a href="playground.html" style="color:var(--green)">PLAYGROUND</a></li>
    </ul>"""
    c = c[:nav_start] + new_nav + c[nav_end:]
    print("Nav: PLAYGROUND added")
else:
    print("Nav: PLAYGROUND already present")

# Check results
import re
bad = re.findall(r'onclick=\\"', c)
good = re.findall(r'onclick="navTo', c)
print("Bad escaped onclick:", len(bad))
print("Good onclick navTo:", len(good))
print("PLAYGROUND in nav:", 'PLAYGROUND' in c)

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("SAVED")
