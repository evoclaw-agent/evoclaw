"""
EvoClaw SkillBank
Stores, retrieves, and manages skills.
Skills are short Markdown instructions injected into every system prompt.
Optional Redis (Upstash) for shared/persistent storage across instances.
"""
import os, json, time
from typing import Optional
from difflib import SequenceMatcher


DEFAULT_SKILLS = {
    "general": [
        "Always verify your reasoning before responding. Break complex problems into steps.",
        "When uncertain, say so clearly. Prefer accuracy over speed.",
        "Structure long answers with clear sections. Use examples to illustrate abstract concepts.",
    ],
    "coding": [
        "Prefer readable, maintainable code over clever one-liners.",
        "Always handle edge cases: empty inputs, None values, and exceptions.",
        "Explain the 'why' behind code decisions, not just the 'what'.",
        "When debugging, isolate the problem systematically. Check assumptions first.",
    ],
    "security": [
        "Never trust user input. Validate and sanitize before processing.",
        "Use least-privilege principle: request only the permissions you need.",
        "Prefer established cryptographic libraries over custom implementations.",
    ],
    "crypto": [
        "Always verify smart contract addresses before signing transactions.",
        "Explain gas fees and slippage risks when discussing DeFi operations.",
        "Never share private keys or seed phrases. Use hardware wallets for large amounts.",
        "Check token contract audit status before recommending interactions.",
    ],
    "defi": [
        "Explain impermanent loss risk when discussing liquidity provision.",
        "Always check protocol TVL and audit history before recommending.",
        "Mention liquidation risks when discussing leveraged positions.",
    ],
    "agentic": [
        "Confirm destructive actions before executing. Ask 'are you sure?' for irreversible operations.",
        "Keep the user informed of multi-step progress. Log each completed action.",
        "If a task fails, explain why and suggest an alternative approach.",
    ],
}


class SkillBank:
    def __init__(self, config):
        self.config = config
        self.path = config.skills_path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._redis = None
        self._init_redis()
        self._data = self._load()

    def _init_redis(self):
        if self.config.redis_url and self.config.redis_token:
            try:
                import httpx
                self._redis = {
                    "url": self.config.redis_url,
                    "token": self.config.redis_token,
                }
            except ImportError:
                pass

    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        # Bootstrap with default skill packs
        data = {"skills": [], "stats": {"total": 0, "injected": 0}}
        for pack in self.config.skill_packs:
            if pack in DEFAULT_SKILLS:
                for skill_text in DEFAULT_SKILLS[pack]:
                    data["skills"].append({
                        "id": f"default_{pack}_{len(data['skills'])}",
                        "text": skill_text,
                        "category": pack,
                        "score": 0.8,
                        "uses": 0,
                        "created_at": time.time(),
                        "source": "default",
                    })
        data["stats"]["total"] = len(data["skills"])
        self._save(data)
        return data

    def _save(self, data=None):
        if data is None:
            data = self._data
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def add_skill(self, text: str, category: str, score: float, source: str = "learned"):
        """Add a new skill if it's not a duplicate."""
        if self._is_duplicate(text):
            return False
        skill = {
            "id": f"skill_{int(time.time()*1000)}",
            "text": text.strip(),
            "category": category,
            "score": score,
            "uses": 0,
            "created_at": time.time(),
            "source": source,
        }
        self._data["skills"].append(skill)
        self._data["stats"]["total"] = len(self._data["skills"])
        self._save()
        # Also push to Redis if available
        self._redis_push(skill)
        return True

    def _is_duplicate(self, text: str, threshold: float = 0.85) -> bool:
        for existing in self._data["skills"]:
            ratio = SequenceMatcher(None, text.lower(), existing["text"].lower()).ratio()
            if ratio > threshold:
                return True
        return False

    def get_top_skills(self, query: str = "", k: int = None) -> list[str]:
        """Return top-k most relevant skill texts for injection."""
        k = k or self.config.skills_top_k
        skills = self._data["skills"]
        if not skills:
            return []

        # Simple relevance: category match + score + recency
        scored = []
        query_lower = query.lower()
        for s in skills:
            relevance = s["score"]
            if s["category"] in query_lower or any(
                kw in query_lower for kw in s["text"].lower().split()[:5]
            ):
                relevance += 0.2
            scored.append((relevance, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [s["text"] for _, s in scored[:k]]

        # Track injection count
        self._data["stats"]["injected"] = self._data["stats"].get("injected", 0) + len(top)
        self._save()
        return top

    def get_all_categories(self) -> dict:
        cats = {}
        for s in self._data["skills"]:
            c = s["category"]
            cats[c] = cats.get(c, 0) + 1
        return cats

    def stats(self) -> dict:
        return {
            "total_skills": len(self._data["skills"]),
            "total_injected": self._data["stats"].get("injected", 0),
            "categories": self.get_all_categories(),
        }

    def _redis_push(self, skill: dict):
        if not self._redis:
            return
        try:
            import httpx
            key = f"evoclaw:skill:{skill['id']}"
            val = json.dumps(skill)
            httpx.post(
                f"{self._redis['url']}/set/{key}/{val}",
                headers={"Authorization": f"Bearer {self._redis['token']}"},
                timeout=3,
            )
        except Exception:
            pass  # Redis is optional

    def format_for_injection(self, query: str = "") -> str:
        """Format top skills as system prompt injection block."""
        skills = self.get_top_skills(query)
        if not skills:
            return ""
        lines = ["## Learned Skills (apply these proactively):"]
        for i, s in enumerate(skills, 1):
            lines.append(f"{i}. {s}")
        return "\n".join(lines)
