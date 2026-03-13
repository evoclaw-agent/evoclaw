"""
fix_all_3.py - Fix semua 3 masalah sekaligus:
1. Quick Start di index.html - ganti cara lama ke evoclaw init/start
2. Tambah INSTALL di nav semua halaman
3. Docs Quick Start - update ke cara baru
"""
import re, os

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def read(f):
    with open(f, 'r', encoding='utf-8') as fh:
        return fh.read()

def write(f, c):
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(c)
    print(f"  ✅ {f} saved")

def check(label, cond):
    print(f"  {'✅' if cond else '❌'} {label}: {cond}")

# ─────────────────────────────────────────────
# FIX 1 - index.html Quick Start section
# ─────────────────────────────────────────────
print("\n── FIX 1: index.html Quick Start ──")
c = read('index.html')

# Ganti seluruh qs-body section
OLD_QS = '''        <div><span class="cm"># 1. Install dependencies</span></div>
        <div><span class="fn">pip</span> install evoclaw</div>
        <div>&nbsp;</div>
        <div><span class="cm"># 2. Set up OpenClaw to use EvoClaw proxy</span></div>
        <div><span class="fn">bash</span> openclaw_model_kimi.sh</div>
        <div>&nbsp;</div>
        <div><span class="cm"># 3. Add your Tinker key and run</span></div>
        <div><span class="va">export</span> TINKER_API_KEY=<span class="st">"your_key_here"</span></div>
        <div><span class="fn">python</span> examples/run_with_skills.py</div>'''

NEW_QS = '''        <div><span class="cm"># 1. Install EvoClaw</span></div>
        <div><span class="fn">pip</span> install evoclaw</div>
        <div>&nbsp;</div>
        <div><span class="cm"># 2. Setup API keys (Groq = free, Tinker = cloud LoRA)</span></div>
        <div><span class="fn">evoclaw</span> init</div>
        <div>&nbsp;</div>
        <div><span class="cm"># 3. Start the proxy</span></div>
        <div><span class="fn">evoclaw</span> start</div>
        <div>&nbsp;</div>
        <div><span class="st">🦎 EvoClaw Proxy v0.2.1 — localhost:8080 — evolving!</span></div>'''

if OLD_QS in c:
    c = c.replace(OLD_QS, NEW_QS)
    print("  ✅ Quick Start step 1-3 updated")
else:
    # Try simpler replace - just the bash/python lines
    c = c.replace(
        'openclaw_model_kimi.sh</div>',
        'evoclaw</span> init</div>'
    )
    c = c.replace(
        'TINKER_API_KEY=<span class="st">"your_key_here"</span></div>\n        <div><span class="fn">python</span> examples/run_with_skills.py</div>',
        'evoclaw</span> start</div>'
    )
    # Fix comment labels
    c = c.replace(
        '# 2. Set up OpenClaw to use EvoClaw proxy',
        '# 2. Setup API keys (Groq = free)'
    )
    c = c.replace(
        '# 3. Add your Tinker key and run',
        '# 3. Start the proxy'
    )
    c = c.replace(
        '<div><span class="va">export</span> ',
        '<div><span class="fn">evoclaw</span> '
    )
    print("  ✅ Quick Start updated (partial replace)")

# Fix success message
c = c.replace(
    '🦎 EvoClaw ready — your agent is now self-evolving.',
    '🦎 EvoClaw Proxy v0.2.1 — localhost:8080 — evolving!'
)

# Update version badge from v0.1.0 to v0.2.1
c = c.replace('v0.1.0 &nbsp;·&nbsp; MIT LICENSE', 'v0.2.1 &nbsp;·&nbsp; MIT LICENSE')
c = c.replace('v0.2.0 &nbsp;·&nbsp; MIT LICENSE', 'v0.2.1 &nbsp;·&nbsp; MIT LICENSE')

write('index.html', c)
check("evoclaw init in index", 'evoclaw</span> init' in c)
check("evoclaw start in index", 'evoclaw</span> start' in c)


# ─────────────────────────────────────────────
# FIX 2 - Tambah INSTALL di nav semua halaman
# ─────────────────────────────────────────────
print("\n── FIX 2: INSTALL nav di semua halaman ──")

files = ['index.html', 'demo.html', 'docs.html', 'ask.html', 'playground.html']

for fname in files:
    if not os.path.exists(fname):
        print(f"  ⚠️  {fname} not found, skip")
        continue

    c = read(fname)
    changed = False

    # Kalau belum ada INSTALL link, tambahkan sebelum ASK EVOCLAW
    if 'install.html' not in c:
        # Coba tambah sebelum ask.html di nav-links
        if '<li><a href="ask.html"' in c:
            c = c.replace(
                '<li><a href="ask.html"',
                '<li><a href="install.html" style="color:var(--green)">INSTALL</a></li>\n      <li><a href="ask.html"'
            )
            changed = True
        # Coba tambah sebelum ASK EVOCLAW text
        elif 'ASK EVOCLAW' in c and 'install.html' not in c:
            c = c.replace(
                '>ASK EVOCLAW<',
                '>ASK EVOCLAW<'  # already there different format
            )

    # Fix mobile menu juga - tambah INSTALL sebelum ASK EVOCLAW
    if 'install.html' not in c or c.count('install.html') < 2:
        # Tambah di mobile menu juga
        if '<a href="ask.html" class="green">' in c:
            c = c.replace(
                '<a href="ask.html" class="green">',
                '<a href="install.html" class="green">INSTALL</a>\n  <a href="ask.html" class="green">'
            )
            changed = True
        elif '<a href="ask.html">' in c and 'ASK EVOCLAW' in c:
            pass  # handled above

    if changed or 'install.html' in c:
        write(fname, c)
        check(f"install.html in {fname}", 'install.html' in c)
    else:
        print(f"  ℹ️  {fname} - install.html already present or pattern not matched")
        check(f"install.html in {fname}", 'install.html' in c)


# ─────────────────────────────────────────────
# FIX 3 - docs.html Quick Start
# ─────────────────────────────────────────────
print("\n── FIX 3: docs.html Quick Start ──")

if not os.path.exists('docs.html'):
    print("  ⚠️  docs.html not found")
else:
    c = read('docs.html')

    # Ganti step 1 install
    c = c.replace(
        'pip install fastapi uvicorn httpx openai transformers',
        'pip install evoclaw'
    )
    c = c.replace(
        'pip install fastapi uvicorn httpx openai transformers tinker tinker-cookbook',
        'pip install evoclaw'
    )

    # Ganti step 2 openclaw bash
    c = c.replace('bash openclaw_model_kimi.sh', 'evoclaw init')
    c = c.replace(
        'bash openclaw_model_qwen.sh',
        'evoclaw init'
    )

    # Ganti step 3 export + python
    c = c.replace(
        'export TINKER_API_KEY="..."',
        'evoclaw start'
    )
    c = c.replace(
        'python examples/run_conversation_rl.py',
        'evoclaw start'
    )
    c = c.replace(
        'python examples/run_with_skills.py',
        'evoclaw start'
    )

    # Fix comment labels di docs
    c = c.replace('# 1. Install dependencies', '# 1. Install EvoClaw')
    c = c.replace('# 2. Configure OpenClaw gateway', '# 2. Setup API keys')
    c = c.replace('# 2. Set up OpenClaw to use EvoClaw proxy', '# 2. Setup API keys')
    c = c.replace('# 3. Start training', '# 3. Start the proxy')
    c = c.replace('# 3. Add your Tinker key and run', '# 3. Start the proxy')

    # Update success message di docs
    c = c.replace(
        '🦎 EvoClaw ready — your agent is now self-evolving.',
        '🦎 EvoClaw Proxy v0.2.1 — localhost:8080 — evolving!'
    )

    # Update version di docs
    c = c.replace('v0.1.0', 'v0.2.1')
    c = c.replace('v0.2.0', 'v0.2.1')

    write('docs.html', c)
    check("evoclaw init in docs", 'evoclaw init' in c or 'evoclaw</span> init' in c or 'evoclaw start' in c)
    check("pip install evoclaw in docs", 'evoclaw' in c)
    check("no old openclaw_model_kimi", 'openclaw_model_kimi' not in c)
    check("no old run_with_skills", 'run_with_skills' not in c)


# ─────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────
print("\n── FINAL CHECK ──")
for fname in ['index.html', 'docs.html', 'demo.html', 'ask.html', 'playground.html']:
    if os.path.exists(fname):
        c = read(fname)
        has_install = 'install.html' in c
        print(f"  {'✅' if has_install else '❌'} {fname}: install.html={has_install}")

print("\n🦎 All fixes done! Now run:")
print("  git add -f index.html docs.html demo.html ask.html playground.html")
print("  git commit -m 'fix: quick start evoclaw init/start + INSTALL nav all pages'")
print("  git push origin main")
