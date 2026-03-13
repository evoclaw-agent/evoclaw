"""
EvoClaw — Self-evolving AI agents via LoRA
Just talk to your agent. It learns and evolves.

Works with: Groq, OpenAI, Anthropic, any OpenAI-compatible API
Training:   Tinker cloud LoRA (no GPU required)
"""
__version__ = "0.2.1"

from .config import EvoClawConfig
from .proxy import EvoClawProxy
from .skills import SkillBank
from .scorer import PRMScorer
from .evolver import SkillEvolver
from .trainer import EvoClawTrainer, TrainingSample

__all__ = [
    "EvoClawConfig",
    "EvoClawProxy",
    "SkillBank",
    "PRMScorer",
    "SkillEvolver",
    "EvoClawTrainer",
    "TrainingSample",
]
