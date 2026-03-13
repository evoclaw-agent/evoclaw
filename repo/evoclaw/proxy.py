"""
EvoClaw Proxy
OpenAI-compatible HTTP proxy that wraps any LLM API.
- Intercepts every conversation
- Injects skills into system prompt
- Scores responses via PRM (async, non-blocking)
- Triggers skill evolution on failures
- Feeds training samples to Tinker
"""
import asyncio, json, os, time
from typing import Optional

try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import StreamingResponse, JSONResponse
    import httpx
    import uvicorn
except ImportError:
    raise ImportError("pip install fastapi uvicorn httpx")

from .config import EvoClawConfig
from .skills import SkillBank
from .scorer import PRMScorer
from .evolver import SkillEvolver
from .trainer import EvoClawTrainer, TrainingSample


class EvoClawProxy:
    def __init__(self, config: Optional[EvoClawConfig] = None):
        self.config = config or EvoClawConfig.load()
        self.skill_bank = SkillBank(self.config)
        self.scorer = PRMScorer(self.config) if self.config.use_prm else None
        self.evolver = SkillEvolver(self.config) if self.config.enable_skill_evolution else None
        self.trainer = EvoClawTrainer(self.config) if self.config.enable_tinker_training else None
        self.app = self._build_app()
        self._conversations = 0
        self._skills_injected = 0

    def _build_app(self) -> FastAPI:
        app = FastAPI(title="EvoClaw Proxy", version="0.2.0")

        @app.post("/v1/chat/completions")
        async def chat_completions(request: Request):
            return await self._handle_chat(request)

        @app.get("/v1/models")
        async def list_models():
            return JSONResponse({
                "object": "list",
                "data": [{"id": self.config.target_model, "object": "model"}]
            })

        @app.get("/health")
        async def health():
            return {
                "status": "ok",
                "conversations": self._conversations,
                "skills": self.skill_bank.stats(),
                "trainer": self.trainer.get_status() if self.trainer else None,
            }

        @app.get("/logo.png")
        async def serve_logo():
            import pathlib
            from fastapi.responses import FileResponse, Response
            candidates = [
                pathlib.Path(__file__).parent.parent.parent / "website" / "assets" / "logo.png",
                pathlib.Path(__file__).parent.parent / "assets" / "logo.png",
                pathlib.Path("assets/logo.png"),
                pathlib.Path("../assets/logo.png"),
                pathlib.Path("../../website/assets/logo.png"),
            ]
            for p in candidates:
                if p.exists():
                    return FileResponse(str(p), media_type="image/png")
            return Response(status_code=404)

        @app.get("/")
        async def root():
            from fastapi.responses import HTMLResponse
            stats = self.skill_bank.stats()
            trainer_status = self.trainer.get_status() if self.trainer else None
            tinker_ok = trainer_status and trainer_status.get("tinker_connected")
            cats_html = "".join(
                f'<div class="stat"><span class="stat-label">{cat}</span>'
                f'<span class="stat-value">{count} skills</span></div>'
                for cat, count in stats["categories"].items()
            )
            html = f"""<!DOCTYPE html>
<html><head><title>EvoClaw Proxy</title><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0a0a;color:#e0e0e0;font-family:'Courier New',monospace;display:flex;align-items:center;justify-content:center;min-height:100vh}}
.container{{max-width:600px;width:100%;padding:40px 20px}}
.logo{{font-size:48px;margin-bottom:8px}}
h1{{font-size:28px;color:#00ff88;margin-bottom:4px}}
.sub{{color:#888;margin-bottom:32px;font-size:14px}}
.card{{background:#111;border:1px solid #222;border-radius:12px;padding:24px;margin-bottom:16px}}
.card h2{{font-size:12px;color:#555;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px}}
.stat{{display:flex;justify-content:space-between;margin-bottom:12px}}
.stat-label{{color:#888;font-size:14px}}
.stat-value{{color:#00ff88;font-weight:bold;font-size:14px}}
.stat-value.warn{{color:#ffaa00}}
.endpoint{{background:#0d1117;border:1px solid #333;border-radius:8px;padding:16px;margin-top:8px;font-size:13px;color:#79c0ff;line-height:1.8}}
.dot{{width:8px;height:8px;border-radius:50%;background:#00ff88;display:inline-block;margin-right:6px;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
footer{{text-align:center;color:#444;font-size:12px;margin-top:24px}}
footer a{{color:#555;text-decoration:none}}
</style></head>
<body><div class="container">
  <img src="/logo.png" alt="EvoClaw" style="width:72px;height:72px;object-fit:contain;margin-bottom:8px;" onerror="this.style.display='none';document.getElementById('emoji-logo').style.display='block'">
  <div id="emoji-logo" style="font-size:48px;margin-bottom:8px;display:none">🦎</div>
  <h1>EvoClaw Proxy</h1>
  <p class="sub"><span class="dot"></span>Running &nbsp;·&nbsp; v0.2.0</p>

  <div class="card">
    <h2>Status</h2>
    <div class="stat"><span class="stat-label">Proxy</span><span class="stat-value">● Online :8080</span></div>
    <div class="stat"><span class="stat-label">Conversations</span><span class="stat-value">{self._conversations}</span></div>
    <div class="stat"><span class="stat-label">Total Skills</span><span class="stat-value">{stats["total_skills"]}</span></div>
    <div class="stat"><span class="stat-label">Skills Injected</span><span class="stat-value">{stats["total_injected"]}</span></div>
    <div class="stat"><span class="stat-label">Tinker LoRA</span>
      <span class="stat-value {'stat-value' if tinker_ok else 'stat-value warn'}">{"● Connected" if tinker_ok else "⚠ Skill-only mode"}</span>
    </div>
  </div>

  <div class="card">
    <h2>Skill Categories</h2>
    {cats_html}
  </div>

  <div class="card">
    <h2>Quick Start</h2>
    <div class="endpoint">
      from openai import OpenAI<br>
      client = OpenAI(<br>
      &nbsp;&nbsp;base_url="http://localhost:8080/v1",<br>
      &nbsp;&nbsp;api_key="any-string"<br>
      )<br>
      <span style="color:#8b949e"># Just chat — agent learns automatically</span>
    </div>
  </div>

  <footer>
    <a href="https://evoclaw.tech">evoclaw.tech</a> &nbsp;·&nbsp;
    <a href="/health">/health</a> &nbsp;·&nbsp;
    <a href="/v1/models">/v1/models</a>
  </footer>
</div></body></html>"""
            return HTMLResponse(html)

        return app

    async def _handle_chat(self, request: Request) -> Response:
        body = await request.json()
        messages = body.get("messages", [])

        # ── 1. Inject skills into system prompt ────────────────────────────
        user_query = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_query = m.get("content", "")
                break

        skill_injection = ""
        if self.config.use_skills and self.skill_bank:
            skill_injection = self.skill_bank.format_for_injection(user_query)
            if skill_injection:
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += f"\n\n{skill_injection}"
                else:
                    messages.insert(0, {"role": "system", "content": skill_injection})
                self._skills_injected += 1

        body["messages"] = messages
        body["model"] = body.get("model", self.config.target_model)

        # ── 2. Forward to upstream API ──────────────────────────────────────
        upstream_url = f"{self.config.target_api_url}/chat/completions"
        api_key = os.environ.get("GROQ_API_KEY", "")
        if self.config.prm_provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY", "")
        elif self.config.prm_provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        self._conversations += 1
        start = time.time()

        async with httpx.AsyncClient(timeout=60) as client:
            upstream_response = await client.post(
                upstream_url,
                json=body,
                headers=headers,
            )

        elapsed = time.time() - start

        # ── 3. Parse response ───────────────────────────────────────────────
        if upstream_response.status_code != 200:
            return Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                media_type="application/json",
            )

        response_data = upstream_response.json()
        assistant_msg = ""
        try:
            assistant_msg = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            pass

        # ── 4. Score & learn in background (non-blocking) ──────────────────
        if user_query and assistant_msg and self.scorer:
            asyncio.create_task(
                self._learn_from_turn(user_query, assistant_msg, skill_injection)
            )

        # ── 5. Add metadata headers ────────────────────────────────────────
        response = JSONResponse(response_data)
        response.headers["X-EvoClaw-Skills-Injected"] = str(bool(skill_injection))
        response.headers["X-EvoClaw-Conversations"] = str(self._conversations)
        response.headers["X-EvoClaw-Total-Skills"] = str(self.skill_bank.stats()["total_skills"])
        response.headers["X-EvoClaw-Latency"] = f"{elapsed:.3f}s"
        return response

    async def _learn_from_turn(
        self,
        user_msg: str,
        assistant_msg: str,
        skill_injection: str,
    ):
        """Background task: score → evolve → train."""
        try:
            # Score
            result = await self.scorer.score_async(user_msg, assistant_msg)
            print(
                f"📊 PRM score={result.score:.2f} | "
                f"conv={self._conversations} | "
                f"skills={self.skill_bank.stats()['total_skills']}"
            )

            # Add skill if high quality
            if result.skill_extracted:
                added = self.skill_bank.add_skill(
                    text=result.skill_extracted,
                    category=result.skill_category,
                    score=result.score,
                    source="learned",
                )
                if added:
                    print(f"🧠 New skill [{result.skill_category}]: {result.skill_extracted[:60]}...")

            # Evolve skill if failure
            if result.is_failure and self.evolver:
                existing = self.skill_bank.get_top_skills()
                evolved = await self.evolver.evolve_async(
                    user_msg=user_msg,
                    assistant_msg=assistant_msg,
                    score=result.score,
                    reasoning=result.reasoning,
                    existing_skills=existing,
                )
                if evolved:
                    self.skill_bank.add_skill(
                        text=evolved.text,
                        category=evolved.category,
                        score=0.7,
                        source="evolved",
                    )

            # Feed to Tinker trainer
            if self.trainer:
                sample = TrainingSample(
                    user_msg=user_msg,
                    assistant_msg=assistant_msg,
                    reward=result.score,
                    skill_injected=skill_injection,
                )
                self.trainer.add_sample(sample)

        except Exception as e:
            print(f"⚠️  Learn-from-turn error: {e}")

    def run(self):
        """Start the proxy server."""
        print(f"""
╔══════════════════════════════════════════╗
║  🦎 EvoClaw Proxy v0.2.0                ║
║  → Listening on http://localhost:{self.config.proxy_port}  ║
║  → Model: {self.config.target_model[:30]:<30} ║
║  → Skills: {self.skill_bank.stats()['total_skills']} loaded                    ║
║  → Tinker: {'✅ connected' if self.trainer and self.trainer.get_status()['tinker_connected'] else '⚠️  skill-only mode'}             ║
╚══════════════════════════════════════════╝

Point your OpenAI client here:
  base_url = "http://localhost:{self.config.proxy_port}/v1"
  api_key   = "any-string"  # Not checked by proxy
""")
        uvicorn.run(self.app, host="0.0.0.0", port=self.config.proxy_port, log_level="warning")
