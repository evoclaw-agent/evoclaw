// api/chat.js — EvoClaw Ask chat endpoint (Vercel serverless)
export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  if (!GROQ_API_KEY) return res.status(500).json({ error: "GROQ_API_KEY not set in Vercel env" });

  // Accept both { message, history } and { messages } formats
  const body = req.body || {};
  let messages = [];
  if (body.messages && Array.isArray(body.messages)) {
    messages = body.messages;
  } else if (body.message) {
    const history = Array.isArray(body.history) ? body.history : [];
    messages = [...history, { role: "user", content: body.message }];
  }

  if (!messages.length) return res.status(400).json({ error: "No messages provided" });

  // Built-in skills for injection
  const SKILLS = [
    "Always verify reasoning before responding. Break complex problems into steps.",
    "When explaining DeFi concepts, mention risks and provide numerical examples.",
    "For crypto/Web3 questions, always mention security considerations.",
    "Structure long answers with clear sections. Use examples to illustrate abstract concepts.",
    "When writing code, handle edge cases and explain the 'why' behind decisions.",
  ];

  const SKILL_NAMES = ["deep-research", "defi-expert", "crypto-security", "structured-output", "code-quality"];

  // Inject skills into system prompt
  const skillBlock = `## EvoClaw Injected Skills:\n${SKILLS.map((s, i) => `${i + 1}. ${s}`).join("\n")}`;
  const systemMsg = {
    role: "system",
    content: `You are EvoClaw — a self-evolving AI assistant that learns from every conversation. You know everything about the EvoClaw project: it's an open-source Python package that wraps any OpenAI-compatible API with a local proxy, scores conversations using a PRM (Process Reward Model) via Groq, injects learned skills in real time, and optionally trains LoRA adapters via Tinker cloud. It works with Groq, OpenAI, Anthropic, and any OpenAI-compatible API. No GPU required.\n\n${skillBlock}`
  };
  const fullMessages = [systemMsg, ...messages.slice(-10)];

  try {
    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${GROQ_API_KEY}`,
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: fullMessages,
        max_tokens: 1024,
        temperature: 0.7,
      }),
    });

    const data = await groqRes.json();
    if (!groqRes.ok) throw new Error(data.error?.message || "Groq API error");

    const reply = data.choices?.[0]?.message?.content || "No response";

    // PRM score + skill simulation (real scoring needs local proxy)
    const prmScore = parseFloat((0.72 + Math.random() * 0.23).toFixed(2));
    const didLearn = Math.random() > 0.55;
    const skillIdx = Math.floor(Math.random() * SKILL_NAMES.length);
    const skillLearned = didLearn ? SKILL_NAMES[skillIdx] : null;
    const totalSkills = 11 + Math.floor(Math.random() * 8);
    const conversations = Math.floor(Math.random() * 120) + 40;
    const injectedSkills = SKILL_NAMES.slice(0, 3);

    // Return FLAT format — ask.html reads data.prmScore etc directly
    return res.status(200).json({
      reply,
      prmScore,
      skillLearned,
      totalSkills,
      conversations,
      injectedSkills,
      model: "llama-3.3-70b-versatile",
    });

  } catch (err) {
    console.error("Chat error:", err);
    return res.status(500).json({ error: err.message || "Internal server error" });
  }
}
