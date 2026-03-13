"""
EvoClaw Skill Evolver
When the agent fails (PRM score < threshold), analyze the failure and
auto-generate a new skill to prevent the same mistake.
Uses Groq (free) instead of Azure OpenAI (expensive like MetaClaw).
"""
import os, json, re
from typing import Optional
from dataclasses import dataclass

try:
    from groq import Groq, AsyncGroq
except ImportError:
    raise ImportError("pip install groq")


@dataclass
class EvolvedSkill:
    text: str
    category: str
    reasoning: str
    triggered_by: str  # Summary of the failure that triggered evolution


EVOLUTION_PROMPT = """You are an AI meta-learning system. An AI agent just failed at a task.
Analyze the failure and generate a SKILL — a short instruction that would prevent this failure.

FAILED CONVERSATION:
User: {user_msg}
Agent: {assistant_msg}

FAILURE REASON (PRM score: {score:.2f}):
{reasoning}

EXISTING SKILLS (don't duplicate):
{existing_skills}

Generate ONE new skill in JSON:
{{
  "skill": "A clear, actionable 1-2 sentence instruction the agent should follow",
  "category": "coding|security|agentic|crypto|defi|general",
  "reasoning": "Why this skill prevents the failure"
}}

The skill must be:
- Actionable (starts with a verb: "Always", "Never", "When", "Before", "After")
- General enough to apply beyond this specific case
- Different from existing skills"""


class SkillEvolver:
    def __init__(self, config):
        self.config = config
        self._api_key = os.environ.get("GROQ_API_KEY", "")
        if not self._api_key:
            raise ValueError("GROQ_API_KEY not set.")
        self.client = Groq(api_key=self._api_key)
        self.async_client = AsyncGroq(api_key=self._api_key)
        self._evolution_count = 0

    def evolve(
        self,
        user_msg: str,
        assistant_msg: str,
        score: float,
        reasoning: str,
        existing_skills: list[str],
    ) -> Optional[EvolvedSkill]:
        """Analyze failure and generate a new skill synchronously."""
        existing_summary = "\n".join(f"- {s[:80]}" for s in existing_skills[:10])
        prompt = EVOLUTION_PROMPT.format(
            user_msg=user_msg[:1000],
            assistant_msg=assistant_msg[:1000],
            score=score,
            reasoning=reasoning[:500],
            existing_skills=existing_summary or "None yet",
        )
        try:
            response = self.client.chat.completions.create(
                model=self.config.evolution_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
            data = json.loads(raw)

            skill_text = data.get("skill", "").strip()
            if not skill_text or len(skill_text) < 20:
                return None

            self._evolution_count += 1
            print(f"🧬 Skill evolved [{data.get('category', 'general')}]: {skill_text[:60]}...")

            return EvolvedSkill(
                text=skill_text,
                category=data.get("category", "general"),
                reasoning=data.get("reasoning", ""),
                triggered_by=f"score={score:.2f}: {reasoning[:100]}",
            )
        except Exception as e:
            print(f"⚠️  Skill evolution error: {e}")
            return None

    async def evolve_async(
        self,
        user_msg: str,
        assistant_msg: str,
        score: float,
        reasoning: str,
        existing_skills: list[str],
    ) -> Optional[EvolvedSkill]:
        """Async version for non-blocking operation in proxy."""
        existing_summary = "\n".join(f"- {s[:80]}" for s in existing_skills[:10])
        prompt = EVOLUTION_PROMPT.format(
            user_msg=user_msg[:1000],
            assistant_msg=assistant_msg[:1000],
            score=score,
            reasoning=reasoning[:500],
            existing_skills=existing_summary or "None yet",
        )
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.evolution_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
            data = json.loads(raw)

            skill_text = data.get("skill", "").strip()
            if not skill_text or len(skill_text) < 20:
                return None

            self._evolution_count += 1
            return EvolvedSkill(
                text=skill_text,
                category=data.get("category", "general"),
                reasoning=data.get("reasoning", ""),
                triggered_by=f"score={score:.2f}: {reasoning[:100]}",
            )
        except Exception as e:
            print(f"⚠️  Skill evolution async error: {e}")
            return None

    @property
    def evolution_count(self) -> int:
        return self._evolution_count
