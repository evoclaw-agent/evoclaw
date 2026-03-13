"""
EvoClaw Config
All settings in one place. Compatible with MetaClaw config naming.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
import json, os

CONFIG_PATH = os.path.expanduser("~/.evoclaw/config.json")

@dataclass
class EvoClawConfig:
    # ── Model ───────────────────────────────────────────────────────────────
    model_name: str = "Qwen/Qwen3-4B"           # Tinker base model
    lora_rank: int = 32                           # LoRA rank (MetaClaw default: 32)
    lora_alpha: float = 64.0                      # LoRA alpha

    # ── Training ────────────────────────────────────────────────────────────
    batch_size: int = 32                          # Samples before each train step
    max_steps: int = 1000                         # Total training steps
    learning_rate: float = 1e-4                   # Adam LR
    loss_fn: Literal[
        "cross_entropy",
        "importance_sampling",
        "grpo",
        "cispo"
    ] = "importance_sampling"                     # Loss function

    # ── PRM (Process Reward Model) ───────────────────────────────────────────
    use_prm: bool = True                          # Enable PRM scoring
    prm_threshold: float = 0.65                   # Min score to learn from
    prm_provider: Literal[
        "groq", "openai", "anthropic"
    ] = "groq"                                    # Judge provider (MetaClaw uses Azure OpenAI)
    prm_model: str = "llama-3.3-70b-versatile"   # Judge model on Groq (FREE)

    # ── Skills ──────────────────────────────────────────────────────────────
    use_skills: bool = True                       # Enable skill injection
    skills_top_k: int = 5                         # How many skills to inject
    skills_path: str = os.path.expanduser(
        "~/.evoclaw/skills.json"
    )

    # ── Skill Evolution ──────────────────────────────────────────────────────
    enable_skill_evolution: bool = True           # Auto-generate skills from failures
    evolution_model: str = "llama-3.3-70b-versatile"   # Groq model for evolution
    evolution_threshold: float = 0.35             # Score below this → trigger evolution

    # ── Tinker ──────────────────────────────────────────────────────────────
    tinker_model_tag: str = "evoclaw-agent"       # Name for saved Tinker weights
    tinker_save_every: int = 100                  # Save weights every N steps
    enable_tinker_training: bool = True           # Set False for skill-only mode

    # ── Proxy ───────────────────────────────────────────────────────────────
    proxy_port: int = 8080                        # Local proxy port
    target_api_url: str = "https://api.groq.com/openai/v1"  # Upstream API
    target_model: str = "llama-3.3-70b-versatile"           # Model to use upstream

    # ── Memory / Redis ───────────────────────────────────────────────────────
    redis_url: Optional[str] = None               # Optional Upstash Redis URL
    redis_token: Optional[str] = None            # Optional Upstash token

    # ── Discord Bot ─────────────────────────────────────────────────────────
    discord_token: Optional[str] = None
    discord_prefix: str = "!"

    # ── Skill packs ─────────────────────────────────────────────────────────
    skill_packs: list = field(default_factory=lambda: ["general", "coding"])

    # ────────────────────────────────────────────────────────────────────────

    def save(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(asdict(self), f, indent=2)
        print(f"✅ Config saved to {CONFIG_PATH}")

    @classmethod
    def load(cls) -> "EvoClawConfig":
        if not os.path.exists(CONFIG_PATH):
            return cls()
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
