// api/stats.js — Returns live stats from Redis for homepage counter

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");

  const REDIS_URL = process.env.UPSTASH_REDIS_REST_URL;
  const REDIS_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN;

  let skillsTotal = 0;
  let conversationsTotal = 0;

  if (REDIS_URL && REDIS_TOKEN) {
    try {
      const [skillsRes, countRes] = await Promise.all([
        fetch(`${REDIS_URL}/get/evoclaw:skills`, { headers: { Authorization: `Bearer ${REDIS_TOKEN}` } }),
        fetch(`${REDIS_URL}/get/evoclaw:conversation_count`, { headers: { Authorization: `Bearer ${REDIS_TOKEN}` } }),
      ]);
      const skillsData = await skillsRes.json();
      const countData = await countRes.json();

      if (skillsData.result) {
        const skills = JSON.parse(skillsData.result);
        skillsTotal = skills.length;
      }
      if (countData.result) {
        conversationsTotal = parseInt(countData.result) || 0;
      }
    } catch (e) {}
  }

  return res.status(200).json({
    skills_total: skillsTotal,
    conversations_total: conversationsTotal,
  });
}
