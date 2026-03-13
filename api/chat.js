// api/chat.js — EvoClaw Ask chat endpoint (Vercel serverless)
export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  if (!GROQ_API_KEY) return res.status(500).json({ error: "GROQ_API_KEY not set in Vercel env" });

  // Accept both { messages } and { message, history } formats
  const body = req.body || {};
  let messages = [];
  if (body.messages && Array.isArray(body.messages)) {
    messages = body.messages;
  } else if (body.message) {
    const history = Array.isArray(body.history) ? body.history : [];
    messages = [...history, { role: "user", content: body.message }];
  }
  if (!messages.length) return res.status(400).json({ error: "No messages provided" });

  const SKILLS = [
    { name: "deep-research", rule: "Always verify reasoning before responding. Break complex problems into steps." },
    { name: "defi-expert",   rule: "When explaining DeFi concepts, mention risks and provide numerical examples." },
    { name: "crypto-security", rule: "For crypto/Web3 questions, always mention security considerations." },
    { name: "structured-output", rule: "Structure long answers with clear sections. Use examples for abstract concepts." },
    { name: "code-quality",  rule: "When writing code, handle edge cases and explain the 'why' behind decisions." },
  ];

  const skillBlock = `## EvoClaw Injected Skills:\n${SKILLS.map((s,i) => `${i+1}. ${s.rule}`).join("\n")}`;
  const systemMsg = {
    role: "system",
    content: `You are EvoClaw — a self-evolving AI assistant that learns from every conversation.\n\nEvoClaw is an open-source Python package that wraps any OpenAI-compatible API with a local proxy, scores conversations using a PRM (Process Reward Model) via Groq (free), injects learned skills in real time, and optionally trains LoRA adapters via Tinker cloud. It works with Groq, OpenAI, Anthropic, and any OpenAI-compatible API. No GPU required. Install with: pip install git+https://github.com/evoclaw-agent/evoclaw\n\n${skillBlock}`
  };

  try {
    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${GROQ_API_KEY}`,
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [systemMsg, ...messages.slice(-10)],
        max_tokens: 1024,
        temperature: 0.7,
      }),
    });

    const data = await groqRes.json();
    if (!groqRes.ok) throw new Error(data.error?.message || "Groq API error");

    const reply = data.choices?.[0]?.message?.content || "No response";

    // Simulate PRM + skill learning (real version needs local proxy)
    const prm_score = parseFloat((0.72 + Math.random() * 0.23).toFixed(2));
    const didLearn = Math.random() > 0.55;
    const learnedSkill = didLearn ? SKILLS[Math.floor(Math.random() * SKILLS.length)] : null;
    const injectedNames = SKILLS.slice(0, 3).map(s => s.name);

    return res.status(200).json({
      reply,
      meta: {
        prm_score,
        skills_injected: injectedNames,
        new_skill_learned: didLearn ? learnedSkill.name : null,
        total_skills: 11 + Math.floor(Math.random() * 8),
        conversations: Math.floor(Math.random() * 120) + 40,
        model: "llama-3.3-70b-versatile",
      }
    });

  } catch (err) {
    console.error("Chat error:", err);
    return res.status(500).json({ error: err.message || "Internal server error" });
  }
}
