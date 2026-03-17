#!/usr/bin/env python3
# add_skills_api.py
# Jalankan di VPS: cd ~/evoclaw/repo && python3 add_skills_api.py

import os, re

PROXY_PATH = os.path.expanduser("~/evoclaw/repo/evoclaw/proxy.py")

# ── Code yang ditambahkan ke proxy.py ──
SKILLS_API_CODE = '''

# ═══════════════════════════════════════════════
# EVOCLAW SKILL API — added by add_skills_api.py
# ═══════════════════════════════════════════════

import glob as _glob
import hashlib as _hashlib

def _get_skills_dir():
    """Return skills directory, create if not exists"""
    import pathlib
    d = pathlib.Path.home() / ".evoclaw" / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _load_all_skills():
    """Load all skills from local skill bank"""
    skills = []
    skill_dir = _get_skills_dir()

    # Load dari JSON files kalau ada
    for f in skill_dir.glob("*.json"):
        try:
            skill = json.loads(f.read_text())
            skills.append(skill)
        except Exception:
            pass

    # Kalau kosong, load dari config evoclaw
    if not skills:
        try:
            config_path = pathlib.Path.home() / ".evoclaw" / "skills.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                skills = data if isinstance(data, list) else data.get("skills", [])
        except Exception:
            pass

    # Kalau masih kosong, scan dari skill_bank di memory
    if not skills:
        try:
            # Try get from evoclaw agent skill bank
            import subprocess
            result = subprocess.run(
                ["evoclaw", "skills", "--json"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout:
                skills = json.loads(result.stdout)
        except Exception:
            pass

    return skills

@app.get("/api/skills")
async def get_skills():
    """
    GET /api/skills
    Returns all skills in the local skill bank
    Called by EvoClaw Marketplace dashboard
    """
    try:
        skills = _load_all_skills()

        # Normalize format
        normalized = []
        for i, s in enumerate(skills):
            normalized.append({
                "id": s.get("id", f"skill-{i}"),
                "name": s.get("name", s.get("skill_name", f"skill-{i}")),
                "category": s.get("category", s.get("type", "general")),
                "content": s.get("content", s.get("instruction", s.get("text", ""))),
                "prm_score": round(float(s.get("prm_score", s.get("score", s.get("reward", 0.75)))), 3),
                "uses": int(s.get("uses", s.get("usage_count", s.get("use_count", 0)))),
                "conversations": int(s.get("conversations", s.get("conv_count", 0))),
                "status": s.get("status", "private"),
                "created_at": s.get("created_at", s.get("created", "")),
                "updated_at": s.get("updated_at", s.get("updated", "")),
            })

        # Sort by PRM score descending
        normalized.sort(key=lambda x: -x["prm_score"])

        return {
            "status": "ok",
            "agent_id": _hashlib.md5(os.uname().nodename.encode()).hexdigest()[:12],
            "total": len(normalized),
            "skills": normalized
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "total": 0,
            "skills": []
        }


@app.post("/api/skills/inject")
async def inject_skill(request: Request):
    """
    POST /api/skills/inject
    Hot-inject a new skill without restarting the agent
    Body: {"name": "...", "content": "...", "category": "..."}
    """
    try:
        body = await request.json()

        if not body.get("name") or not body.get("content"):
            return {"status": "error", "error": "name and content required"}

        import pathlib, time
        skill_id = f"skill-{int(time.time())}"
        skill = {
            "id": skill_id,
            "name": body["name"],
            "category": body.get("category", "general"),
            "content": body["content"],
            "prm_score": float(body.get("prm_score", 0.75)),
            "uses": 0,
            "conversations": 0,
            "status": "private",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Save to disk
        skill_dir = _get_skills_dir()
        skill_path = skill_dir / f"{skill_id}.json"
        skill_path.write_text(json.dumps(skill, indent=2))

        return {
            "status": "injected",
            "skill_id": skill_id,
            "active": True,
            "message": f"Skill '{skill['name']}' injected successfully"
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.delete("/api/skills/{skill_id}")
async def delete_skill(skill_id: str):
    """
    DELETE /api/skills/{skill_id}
    Remove a skill from the local bank
    """
    try:
        import pathlib
        skill_path = _get_skills_dir() / f"{skill_id}.json"
        if skill_path.exists():
            skill_path.unlink()
            return {"status": "deleted", "skill_id": skill_id}
        else:
            return {"status": "error", "error": "Skill not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/skills/{skill_id}/status")
async def update_skill_status(skill_id: str, request: Request):
    """
    POST /api/skills/{skill_id}/status
    Update skill status: private / listed
    Body: {"status": "listed", "price": 0}
    """
    try:
        import pathlib
        body = await request.json()
        skill_path = _get_skills_dir() / f"{skill_id}.json"

        if not skill_path.exists():
            return {"status": "error", "error": "Skill not found"}

        skill = json.loads(skill_path.read_text())
        skill["status"] = body.get("status", "private")
        skill["price"] = body.get("price", 0)
        skill_path.write_text(json.dumps(skill, indent=2))

        return {"status": "updated", "skill_id": skill_id}

    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/agent/status")
async def agent_status():
    """
    GET /api/agent/status
    Returns agent health and basic stats
    Used by dashboard to show AGENT ONLINE indicator
    """
    try:
        skills = _load_all_skills()
        avg_score = 0
        if skills:
            scores = [float(s.get("prm_score", s.get("score", 0))) for s in skills]
            avg_score = round(sum(scores) / len(scores), 3)

        return {
            "status": "online",
            "version": "0.2.1",
            "skill_count": len(skills),
            "avg_prm_score": avg_score,
            "listed_skills": len([s for s in skills if s.get("status") == "listed"]),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ═══════════════════════════════════════════════
# END SKILL API
# ═══════════════════════════════════════════════
'''

def patch_proxy():
    if not os.path.exists(PROXY_PATH):
        print(f"❌ proxy.py not found at {PROXY_PATH}")
        print("   Coba cari manual: find ~ -name proxy.py 2>/dev/null")
        return False

    with open(PROXY_PATH, 'r') as f:
        content = f.read()

    # Cek sudah di-patch sebelumnya
    if "EVOCLAW SKILL API" in content:
        print("ℹ️  proxy.py already patched! Skip.")
        return True

    # Cek ada 'from fastapi import' atau 'import fastapi'
    if 'fastapi' not in content.lower():
        print("⚠️  FastAPI not found in proxy.py — might use different framework")
        print("   Patch tetap dicoba...")

    # Tambah 'from fastapi import Request' kalau belum ada
    if 'from fastapi import' in content and 'Request' not in content:
        content = content.replace(
            'from fastapi import',
            'from fastapi import Request,'
        )
    elif 'Request' not in content and 'fastapi' in content:
        content = content.replace(
            'from fastapi import FastAPI',
            'from fastapi import FastAPI, Request'
        )

    # Tambahkan skill API code di akhir file
    content = content.rstrip() + "\n" + SKILLS_API_CODE

    # Backup dulu
    backup_path = PROXY_PATH + ".backup"
    with open(backup_path, 'w') as f:
        f.write(open(PROXY_PATH).read())
    print(f"✅ Backup saved: {backup_path}")

    # Write patched file
    with open(PROXY_PATH, 'w') as f:
        f.write(content)

    print(f"✅ proxy.py patched successfully!")
    print(f"   Added endpoints:")
    print(f"   GET    /api/skills")
    print(f"   POST   /api/skills/inject")
    print(f"   DELETE /api/skills/{{skill_id}}")
    print(f"   POST   /api/skills/{{skill_id}}/status")
    print(f"   GET    /api/agent/status")
    return True


if __name__ == "__main__":
    import pathlib
    print("=" * 50)
    print("  EvoClaw Skill API Patch")
    print("=" * 50)

    success = patch_proxy()

    if success:
        print("""
Next steps:

1. Restart proxy:
   screen -X -S evoclaw-proxy quit
   screen -dmS evoclaw-proxy bash -c "cd ~/evoclaw/repo && python3 -m evoclaw.proxy"

2. Test endpoints:
   curl http://localhost:8080/api/skills
   curl http://localhost:8080/api/agent/status

3. Kalau ada error, restore backup:
   cp ~/evoclaw/repo/evoclaw/proxy.py.backup ~/evoclaw/repo/evoclaw/proxy.py
""")
