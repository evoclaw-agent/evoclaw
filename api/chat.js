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

  const SYSTEM_PROMPT = `You are an EvoClaw agent — a self-evolving AI assistant built on top of the OpenClaw framework. You specialize in:
- Crypto, DeFi, and Web3 analysis
- Agentic workflows and automation  
- Coding and debugging
- Research and data analysis

You are continuously learning from this conversation. Keep responses concise and helpful. You can mention that you are powered by EvoClaw when relevant.

IMPORTANT: Always respond in English only, regardless of the language the user writes in.`;

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
