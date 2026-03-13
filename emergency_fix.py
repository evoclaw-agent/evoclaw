with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"Lines: {len(c.splitlines())}")

# Check for broken closing tags
print(f"Has </html>: {'</html>' in c}")
print(f"Has html> (broken): {c.strip().endswith('html>')}")
print(f"Last 100 chars: {repr(c[-100:])}")

# Fix 1: Remove any stray "html>" text that appears as visible content
# This happens when </html> got split or duplicated
import re

# Remove any bare "html>" that appears outside of tags (as text content)
# Common cause: the regex replaced inside a tag and left a fragment
c_fixed = re.sub(r'\nhtml>\s*$', '\n</html>', c.rstrip())

# Ensure file ends with </html>
if not c_fixed.rstrip().endswith('</html>'):
    # Find last </body> and add </html> after it
    last_body = c_fixed.rfind('</body>')
    if last_body > 0:
        c_fixed = c_fixed[:last_body + 7] + '\n</html>'
    else:
        c_fixed = c_fixed.rstrip() + '\n</body>\n</html>'

# Fix 2: Remove duplicate/extra blank sections at bottom
# Find if there are empty <section> or <div> blocks at the end before footer
# Check for empty areas - multiple consecutive blank lines
c_fixed = re.sub(r'\n{4,}', '\n\n', c_fixed)

# Fix 3: Make sure hero section has content (check if hero is empty)
hero_idx = c_fixed.find('class="hero"')
if hero_idx < 0:
    hero_idx = c_fixed.find('id="hero"')
print(f"\nHero section found: {hero_idx > 0}")

# Check what's in hero
if hero_idx > 0:
    hero_end = c_fixed.find('</section>', hero_idx)
    hero_content = c_fixed[hero_idx:hero_end if hero_end > 0 else hero_idx+500]
    print(f"Hero content length: {len(hero_content)}")
    print(f"Hero preview: {hero_content[:200]}")

print(f"\nFixed last 200 chars: {repr(c_fixed[-200:])}")
print(f"Fixed lines: {len(c_fixed.splitlines())}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c_fixed)

print("\n✅ index.html closing tags fixed")
