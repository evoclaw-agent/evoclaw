"""
evoclaw/skill_autotag.py
────────────────────────
Skill Auto-Tag: automatically categorizes and tags every skill in the
skill bank using an LLM. No manual labeling required.

Usage:
    from evoclaw.skill_autotag import SkillAutoTagger

    tagger = SkillAutoTagger(api_key="your_openai_key")
    tagger.tag_all("memory_data/conversation/conversation_skills.json")
"""

import json
import os
from pathlib import Path
from typing import Optional
import httpx

# ── Domain taxonomy ──────────────────────────────────────────────────────────
DOMAINS = [
    "crypto",        # DeFi, trading, Web3, blockchain
    "coding",        # software engineering, debugging, code review
    "research",      # data analysis, literature review, RAG
    "agentic",       # multi-step planning, tool use, orchestration
    "security",      # red teaming, vulnerability analysis, CTF
    "communication", # writing, summarization, customer support
    "general",       # everything else
]

SYSTEM_PROMPT = f"""You are a skill taxonomy expert for AI agents.
Given a skill description, return ONLY a JSON object with these fields:
- "domain": one of {DOMAINS}
- "tags": list of 2-4 short keyword tags (lowercase, no spaces, use hyphens)
- "complexity": "basic" | "intermediate" | "advanced"
- "use_case": one sentence describing when to use this skill

Return ONLY valid JSON, no markdown, no explanation."""


class SkillAutoTagger:
    """
    Automatically tags skills in a skill bank JSON file using an LLM.

    Args:
        api_key:    OpenAI-compatible API key
        base_url:   API base URL (default: OpenAI)
        model:      Model to use for tagging (default: gpt-4o-mini, cheap + fast)
        overwrite:  If False, skip skills that already have tags
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        overwrite: bool = False,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.overwrite = overwrite

        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key= or set OPENAI_API_KEY env var."
            )

    def _tag_skill(self, skill_text: str) -> dict:
        """Call LLM to tag a single skill."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Skill:\n{skill_text}"},
            ],
            "max_tokens": 200,
            "temperature": 0.1,
        }
        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)

    def tag_all(self, skills_path: str) -> dict:
        """
        Tag all skills in a skill bank JSON file.

        The file format expected:
        {
          "category_name": ["skill text 1", "skill text 2", ...],
          ...
        }

        Returns the updated skill bank dict.
        """
        path = Path(skills_path)
        if not path.exists():
            raise FileNotFoundError(f"Skills file not found: {skills_path}")

        with open(path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)

        # Build tagged output structure
        tagged: dict = {}
        total = sum(len(v) for v in skills_data.values() if isinstance(v, list))
        done = 0

        for category, skills in skills_data.items():
            if not isinstance(skills, list):
                tagged[category] = skills
                continue

            tagged[category] = []
            for skill in skills:
                # If skill is already a dict with tags and not overwriting, keep it
                if isinstance(skill, dict) and "tags" in skill and not self.overwrite:
                    tagged[category].append(skill)
                    done += 1
                    continue

                skill_text = skill if isinstance(skill, str) else skill.get("text", "")
                print(f"  [{done+1}/{total}] Tagging: {skill_text[:60]}...")

                try:
                    meta = self._tag_skill(skill_text)
                    tagged[category].append({
                        "text": skill_text,
                        "domain": meta.get("domain", "general"),
                        "tags": meta.get("tags", []),
                        "complexity": meta.get("complexity", "basic"),
                        "use_case": meta.get("use_case", ""),
                    })
                except Exception as e:
                    print(f"    ⚠ Tag failed ({e}), keeping raw skill.")
                    tagged[category].append({"text": skill_text, "domain": "general", "tags": []})

                done += 1

        # Save back to file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tagged, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Tagged {done} skills → saved to {path}")
        return tagged

    def search(self, skills_path: str, domain: str = None, tag: str = None) -> list:
        """
        Search tagged skills by domain or tag.

        Example:
            tagger.search("skills.json", domain="crypto")
            tagger.search("skills.json", tag="defi")
        """
        with open(skills_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)

        results = []
        for category, skills in skills_data.items():
            if not isinstance(skills, list):
                continue
            for skill in skills:
                if not isinstance(skill, dict):
                    continue
                if domain and skill.get("domain") != domain:
                    continue
                if tag and tag not in skill.get("tags", []):
                    continue
                results.append({**skill, "category": category})

        return results


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EvoClaw Skill Auto-Tagger")
    parser.add_argument("skills_file", help="Path to conversation_skills.json")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model to use")
    parser.add_argument("--overwrite", action="store_true", help="Re-tag existing skills")
    parser.add_argument("--search-domain", help="Search skills by domain after tagging")
    args = parser.parse_args()

    tagger = SkillAutoTagger(model=args.model, overwrite=args.overwrite)
    tagger.tag_all(args.skills_file)

    if args.search_domain:
        results = tagger.search(args.skills_file, domain=args.search_domain)
        print(f"\n🔍 Skills in domain '{args.search_domain}':")
        for r in results:
            print(f"  • [{r['complexity']}] {r['text'][:80]}")
            print(f"    tags: {r['tags']}")
