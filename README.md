<div align="center">

<img src="https://evoclaw.tech/assets/logo.png" width="120" alt="EvoClaw Logo" />

# EvoClaw

**Self-evolving AI agent wrapper — learns from every conversation, automatically.**

[![PyPI](https://img.shields.io/pypi/v/evoclaw?color=00ff87&labelColor=0c1020&label=pypi)](https://pypi.org/project/evoclaw/)
[![Python](https://img.shields.io/badge/python-3.9+-00c4ff?labelColor=0c1020)](https://pypi.org/project/evoclaw/)
[![License: MIT](https://img.shields.io/badge/license-MIT-00ff87?labelColor=0c1020)](LICENSE)
[![Website](https://img.shields.io/badge/website-evoclaw.tech-00ff87?labelColor=0c1020)](https://evoclaw.tech)

[Website](https://evoclaw.tech) · [Docs](https://evoclaw.tech/docs) · [Install Guide](https://evoclaw.tech/install) · [Live Demo](https://evoclaw.tech/demo) · [PyPI](https://pypi.org/project/evoclaw/)

</div>

---

## What is EvoClaw?

EvoClaw wraps your model behind an OpenAI-compatible API proxy, intercepts every conversation turn, scores it with a reward model, injects relevant skills into the system prompt, and trains via cloud LoRA on Tinker — all automatically, with zero downtime.

> Just talk to your agent. It evolves while you chat.

**No GPU. No data team. No setup headache.**

---

## ✨ Key Features

- **🎯 Real Usage Training** — Learns from live conversations, not synthetic datasets
- **💉 Skill Injection** — Injects relevant skills into the system prompt at every turn
- **🧬 Skill Evolution** — Auto-generates new skills from failure trajectories
- **☁️ No GPU Required** — Training offloads to [Tinker](https://www.thinkingmachines.ai/tinker/) cloud
- **⚡ Fully Async** — Serving, scoring, and training run as decoupled coroutines
- **🔀 Two Learning Modes** — RL (GRPO) + On-Policy Distillation (OPD)
- **📦 pip installable** — `pip install evoclaw` and you're ready

---

## 🚀 Quick Start

### Install

```bash
pip install evoclaw
```

### Configure

```bash
evoclaw init
```

Select your model (Kimi-K2.5 recommended) and enter your Tinker API key when prompted.

### Start

```bash
evoclaw start
```

You'll see:

```
🦎 EvoClaw v0.2.1 starting...
   → Model:       moonshotai/Kimi-K2.5
   → Proxy port:  30000
   → Tinker URL:  http://localhost:8080
   → Skills:      enabled (18 loaded)
   → Evolution:   enabled
   → Ready. Start chatting — your agent will begin evolving!
```

Point your OpenClaw config to `http://localhost:30000/v1` and start chatting. EvoClaw handles the rest.

---

## ⚙️ Configuration

All settings are passed as a single `EvoClawConfig` instance:

```python
from evoclaw import EvoClawConfig, EvoClawProxy

config = EvoClawConfig(
    model_name="moonshotai/Kimi-K2.5",
    loss_fn="importance_sampling",  # or "ppo", "cispo"
    use_prm=True,
    use_skills=True,
    enable_skill_evolution=True,
    batch_size=32,
    lora_rank=32,
)
```

| Field | Default | Description |
|---|---|---|
| `model_name` | `"moonshotai/Kimi-K2.5"` | Base model for training |
| `lora_rank` | `32` | LoRA rank. Higher = more capacity |
| `batch_size` | `32` | Turns before each training step |
| `loss_fn` | `"importance_sampling"` | RL loss: `importance_sampling` / `ppo` / `cispo` |
| `use_prm` | `True` | Enable PRM reward scoring per turn |
| `use_skills` | `False` | Inject skills into system prompt |
| `enable_skill_evolution` | `False` | Auto-generate skills from failures |
| `proxy_port` | `30000` | Proxy listen port |
| `tinker_api_key` | `None` | Tinker API key (or set `TINKER_API_KEY` env var) |

Full config reference → [evoclaw.tech/docs#config-ref](https://evoclaw.tech/docs#config-ref)

---

## 🧠 How It Works

```
User → OpenClaw → EvoClaw Proxy (port 30000)
                        ↓
              [1] Intercept conversation turn
                        ↓
              [2] Score with PRM (0.0 – 1.0)
                        ↓
              [3] Inject relevant skills into prompt
                        ↓
              [4] Buffer turn (async, non-blocking)
                        ↓
              [5] Every N turns → send batch to Tinker
                        ↓
              [6] LoRA training on Tinker cloud
                        ↓
              [7] Hot-swap weights → agent upgraded
                        ↓
                    (repeat forever)
```

---

## 🤖 Supported Models

| Model | Size | Notes |
|---|---|---|
| `moonshotai/Kimi-K2.5` | ~200B MoE | Best quality. Recommended for production. |
| `Qwen/Qwen3-4B` | 4B | Lightweight. Fast iteration, lower cost. |
| `meta-llama/Llama-3.1-8B` | 8B | Balanced speed and quality. |
| Any OpenAI-compatible | — | Set `model_name` to any Tinker-supported identifier. |

---

## 🔄 Learning Modes

### Mode 1: Reinforcement Learning (GRPO)

Uses Group Relative Policy Optimization. Best when you have clear task completion signals.

```python
config = EvoClawConfig(
    loss_fn="importance_sampling",  # or "ppo", "cispo"
    use_prm=True,
)
```

### Mode 2: On-Policy Distillation (OPD)

Leverages richer natural-language supervision from a teacher model. Faster convergence, denser signal.

```python
config = EvoClawConfig(
    loss_fn="importance_sampling",
    use_prm=True,
    prm_model="gpt-4o",
    prm_url="https://api.openai.com/v1",
)
```

---

## 💪 Skills

Skills are short Markdown instructions injected into the system prompt at each turn. The default skill bank ships with 18 skills across 5 categories: `coding`, `security`, `agentic`, `writing`, `research`.

**Enable skill injection:**
```python
config = EvoClawConfig(use_skills=True)
```

**Enable auto skill evolution from failures:**
```python
config = EvoClawConfig(
    use_skills=True,
    enable_skill_evolution=True,
    azure_openai_deployment="gpt-4o",
    azure_openai_endpoint="https://YOUR-RESOURCE.openai.azure.com/",
)
```

**Add custom skills** in `memory_data/conversation/conversation_skills.json`:
```json
{
  "id": "skill_019",
  "category": "coding",
  "title": "Always write type hints in Python",
  "content": "When writing Python functions, always include type hints...",
  "tags": ["python", "typing"],
  "enabled": true
}
```

---

## 🖥️ Production Deployment

```bash
# /etc/systemd/system/evoclaw.service
[Unit]
Description=EvoClaw Self-Evolving Agent
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/evoclaw
Environment="TINKER_API_KEY=your_key_here"
ExecStart=/usr/bin/evoclaw start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable evoclaw
sudo systemctl start evoclaw
```

---

## 📊 EvoClaw vs MetaClaw

| Feature | MetaClaw | EvoClaw |
|---|---|---|
| `pip install` | ❌ | ✅ |
| Website + Docs | ❌ | ✅ [evoclaw.tech](https://evoclaw.tech) |
| Interactive Playground | ❌ | ✅ |
| Multi-provider API | ❌ Azure only | ✅ Groq, OpenAI, Anthropic, + |
| Skill injection | ✅ | ✅ |
| Skill evolution | ✅ | ✅ |
| Tinker LoRA training | ✅ Kimi-K2.5 | ✅ Kimi-K2.5 + more |
| CLI (`evoclaw init/start`) | ❌ | ✅ |

---

## 🙏 Acknowledgements

EvoClaw builds on top of:

- [OpenClaw](https://openclaw.ai) — core agent framework
- [Tinker](https://www.thinkingmachines.ai/tinker/) — cloud LoRA training
- [MetaClaw](https://github.com/aiming-lab/MetaClaw) — original inspiration
- [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) — skill bank foundation

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**[⭐ Star this repo](https://github.com/evoclaw-agent/evoclaw)** if EvoClaw helps your agent evolve!

[evoclaw.tech](https://evoclaw.tech) · [Docs](https://evoclaw.tech/docs) · [PyPI](https://pypi.org/project/evoclaw/)

</div>
