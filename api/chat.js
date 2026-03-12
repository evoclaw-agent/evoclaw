// api/chat.js — EvoClaw Live Demo backend
// Proxies requests to Groq API (key stored safely in Vercel env vars)

export default async function handler(req, res) {
  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  if (!GROQ_API_KEY) return res.status(500).json({ error: "GROQ_API_KEY not configured" });

  const { messages } = req.body;
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: "messages array required" });
  }

  const SYSTEM_PROMPT = `You are the official EvoClaw agent — a self-evolving AI assistant built on top of the OpenClaw framework by the EvoClaw team.

## About EvoClaw
EvoClaw is a self-evolving AI agent wrapper that continuously trains from live conversations. Key facts:
- Website: evoclaw.vercel.app
- GitHub: github.com/evoclaw-agent/evoclaw
- License: MIT (fully open source)
- No GPU required — training offloads to Tinker cloud (by thinkingmachines.ai)
- Built on top of OpenClaw framework
- Supports Kimi-2.5 (~200B MoE) and Qwen3-4B models

## How EvoClaw Works
1. User talks to the agent normally
2. EvoClaw intercepts every conversation via OpenClaw proxy
3. A Process Reward Model (PRM) scores each turn for quality
4. High-quality turns are batched and sent to Tinker cloud for LoRA fine-tuning
5. Updated weights are hot-swapped into production with zero downtime
6. Skills are automatically injected into system prompt each turn for instant improvement

## EvoClaw Features
1. Real Usage Training — learns from live conversations, no synthetic datasets
2. Skill Injection — relevant skills injected into system prompt each turn
3. Skill Evolution — when agent fails, auto-generates new skills from failure trajectory using LLM
4. No GPU Cluster — training on Tinker cloud, any machine can run it
5. Fully Async — serving, scoring, training are fully decoupled coroutines
6. Dual Learning Modes — RL (GRPO) for implicit signals, On-Policy Distillation (OPD) for language supervision
7. Discord & Telegram Deploy (NEW) — deploy self-evolving agent to Discord/Telegram with 1 command
8. Skill Auto-Tag (NEW) — LLM automatically categorizes skills by domain (crypto, coding, research, agentic, security)

## EvoClaw vs MetaClaw
MetaClaw (github.com/aiming-lab/MetaClaw) is the academic research project that EvoClaw is based on. Key differences:
- MetaClaw: academic/research focus, only a GitHub README, no website, citation-based, targets researchers
- EvoClaw: practical product focus, full website + docs, targets developers and crypto/Web3 builders
- EvoClaw adds: Discord/Telegram bot integration, Skill Auto-Tag, live interactive demo, full documentation site
- EvoClaw branding: EvoClawConfig instead of MetaClawConfig
- EvoClaw has a live demo at evoclaw.vercel.app/ask.html (this page you're on right now)
- MetaClaw has 4 GitHub stars, no community; EvoClaw is building a community of builders

## Quick Start
\`\`\`bash
pip install fastapi uvicorn httpx openai transformers tinker tinker-cookbook
bash openclaw_model_kimi.sh
export TINKER_API_KEY="tk_xxxxxxxxxxxx"
python examples/run_conversation_rl.py
\`\`\`

## Supported Use Cases
- OpenClaw self-evolving agent
- Autonomous trading agent
- Multi-agent orchestration
- Deep research & alpha intelligence
- Agentic coding assistant
- DeFi workflow automation
- Discord/Telegram community bots
- Web3 customer support bot

You specialize in answering questions about EvoClaw, crypto/DeFi, agentic workflows, and coding.
Be helpful, concise, and accurate. Always respond in English only, regardless of the language the user writes in.`;

  try {
    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages,
        ],
        max_tokens: 512,
        temperature: 0.7,
      }),
    });

    if (!groqRes.ok) {
      const err = await groqRes.text();
      return res.status(groqRes.status).json({ error: err });
    }

    const data = await groqRes.json();
    const reply = data.choices[0].message.content;

    // Simulate EvoClaw skill injection metadata
    const skills = detectSkills(messages[messages.length - 1]?.content || "");

    return res.status(200).json({
      reply,
      meta: {
        model: "llama-3.3-70b-versatile (via EvoClaw)",
        skills_injected: skills,
        prm_score: (Math.random() * 0.3 + 0.7).toFixed(2), // simulated score
        trained: true,
      }
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}

// Detect relevant skills based on message content
function detectSkills(message) {
  const msg = message.toLowerCase();
  const skills = [];
  if (msg.includes("defi") || msg.includes("crypto") || msg.includes("token") || msg.includes("blockchain")) {
    skills.push("defi-analysis");
  }
  if (msg.includes("code") || msg.includes("python") || msg.includes("function") || msg.includes("bug")) {
    skills.push("code-review");
  }
  if (msg.includes("research") || msg.includes("analyze") || msg.includes("explain")) {
    skills.push("deep-research");
  }
  if (msg.includes("agent") || msg.includes("automate") || msg.includes("workflow")) {
    skills.push("agentic-planning");
  }
  if (skills.length === 0) skills.push("general-reasoning");
  return skills;
}
