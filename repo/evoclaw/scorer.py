"""
EvoClaw PRM Scorer
Scores every conversation turn using Groq (free) instead of Azure OpenAI (expensive).
Returns a score 0.0–1.0 + extracted skill if score >= threshold.
"""
import os, json, re, asyncio
from typing import Optional
from dataclasses import dataclass

try:
    from groq import Groq, AsyncGroq
except ImportError:
    raise ImportError("pip install groq")


@dataclass
class ScoreResult:
    score: float                     # 0.0 – 1.0
    reasoning: str                   # Why this score
    skill_extracted: Optional[str]   # Skill text if score >= threshold
    skill_category: str              # coding / security / agentic / crypto / general
    is_failure: bool                 # True if score < evolution_threshold


SCORE_PROMPT = """You are an AI quality evaluator. Rate this conversation turn.

USER MESSAGE:
{user_msg}

ASSISTANT RESPONSE:
{assistant_msg}

Score the response from 0.0 to 1.0:
- 1.0 = Perfect: accurate, helpful, complete, safe
- 0.7 = Good: mostly correct, minor gaps
- 0.5 = Mediocre: partially helpful
- 0.3 = Poor: misleading or incomplete
- 0.0 = Bad: wrong, harmful, or irrelevant

If score >= 0.65, also extract the KEY SKILL demonstrated in 1-2 sentences.
Categorize as: coding / security / agentic / crypto / defi / general

Respond ONLY in JSON:
{{
  "score": 0.0,
  "reasoning": "...",
  "skill": "...",
  "category": "general"
}}"""


class PRMScorer:
    def __init__(self, config):
        self.config = config
        self._api_key = os.environ.get("GROQ_API_KEY", "")
        if not self._api_key:
            raise ValueError("GROQ_API_KEY not set. Run: evoclaw init")
        self.client = Groq(api_key=self._api_key)
        self.async_client = AsyncGroq(api_key=self._api_key)

    def score(self, user_msg: str, assistant_msg: str) -> ScoreResult:
        """Synchronous scoring."""
        prompt = SCORE_PROMPT.format(
            user_msg=user_msg[:2000],
            assistant_msg=assistant_msg[:2000]
        )
        try:
            response = self.client.chat.completions.create(
                model=self.config.prm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
            data = json.loads(raw)
        except Exception as e:
            print(f"⚠️  PRM scoring error: {e}")
            return ScoreResult(
                score=0.5, reasoning="Scoring failed", 
                skill_extracted=None, skill_category="general",
                is_failure=False
            )

        score = float(data.get("score", 0.5))
        skill = data.get("skill", "") if score >= self.config.prm_threshold else None
        category = data.get("category", "general")
        is_failure = score < self.config.evolution_threshold

        return ScoreResult(
            score=score,
            reasoning=data.get("reasoning", ""),
            skill_extracted=skill,
            skill_category=category,
            is_failure=is_failure,
        )

    async def score_async(self, user_msg: str, assistant_msg: str) -> ScoreResult:
        """Async scoring for non-blocking proxy operation."""
        prompt = SCORE_PROMPT.format(
            user_msg=user_msg[:2000],
            assistant_msg=assistant_msg[:2000]
        )
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.prm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
            data = json.loads(raw)
        except Exception as e:
            print(f"⚠️  PRM async scoring error: {e}")
            return ScoreResult(
                score=0.5, reasoning="Scoring failed",
                skill_extracted=None, skill_category="general",
                is_failure=False
            )

        score = float(data.get("score", 0.5))
        skill = data.get("skill", "") if score >= self.config.prm_threshold else None
        category = data.get("category", "general")

        return ScoreResult(
            score=score,
            reasoning=data.get("reasoning", ""),
            skill_extracted=skill,
            skill_category=category,
            is_failure=score < self.config.evolution_threshold,
        )
