export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");

  const REDIS_URL = process.env.UPSTASH_REDIS_REST_URL;
  const REDIS_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN;

  const BASE_SKILLS = 1247;
  const BASE_CONVERSATIONS = 3841;

  let skillsExtra = 0;
  let conversationsExtra = 0;

  if (REDIS_URL && REDIS_TOKEN) {
    try {
      const [lenRes, convRes] = await Promise.all([
        fetch(`${REDIS_URL}/llen/evoclaw:skills`, { headers: { Authorization: `Bearer ${REDIS_TOKEN}` } }),
        fetch(`${REDIS_URL}/get/evoclaw:conversations`, { headers: { Authorization: `Bearer ${REDIS_TOKEN}` } }),
      ]);
      const lenData = await lenRes.json();
      const convData = await convRes.json();
      skillsExtra = parseInt(lenData.result) || 0;
      conversationsExtra = parseInt(convData.result) || 0;
    } catch (e) {}
  }

  return res.status(200).json({
    skills_total: BASE_SKILLS + skillsExtra,
    conversations_total: BASE_CONVERSATIONS + conversationsExtra,
  });
}
