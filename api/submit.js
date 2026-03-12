// api/submit.js — Vercel Serverless Function
// Receives form data → sends email via Resend API
// Deploy to Vercel, set RESEND_API_KEY in environment variables

export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // CORS headers (allow your domain)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  const {
    firstName,
    lastName,
    email,
    github,
    model,
    useCase,
    about
  } = req.body;

  // Basic validation
  if (!email || !email.includes('@')) {
    return res.status(400).json({ error: 'Valid email is required' });
  }

  const RESEND_API_KEY = process.env.RESEND_API_KEY;
  const TO_EMAIL = process.env.TO_EMAIL; // Your inbox email

  if (!RESEND_API_KEY) {
    return res.status(500).json({ error: 'Server configuration error' });
  }

  // ── Email 1: Notify YOU (the owner) about new signup ──
  const ownerEmailHTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body { font-family: 'Courier New', monospace; background: #05070f; color: #dde6f5; margin: 0; padding: 0; }
    .wrap { max-width: 600px; margin: 0 auto; padding: 40px 32px; }
    .header { border-bottom: 1px solid #1a2438; padding-bottom: 24px; margin-bottom: 32px; }
    .logo { font-size: 18px; font-weight: 700; letter-spacing: .1em; }
    .logo span { color: #00ff87; }
    .badge { display: inline-block; background: rgba(0,255,135,.1); border: 1px solid rgba(0,255,135,.2); color: #00ff87; font-size: 11px; padding: 4px 12px; border-radius: 4px; margin-top: 8px; letter-spacing: .1em; }
    .field { margin-bottom: 16px; }
    .label { font-size: 11px; letter-spacing: .15em; color: #2e4060; margin-bottom: 4px; }
    .value { font-size: 14px; color: #dde6f5; background: #0c1020; border: 1px solid #1a2438; border-radius: 4px; padding: 10px 14px; }
    .value.highlight { border-color: rgba(0,255,135,.2); color: #00ff87; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a2438; font-size: 11px; color: #2e4060; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="logo">🦎 <span>EVO</span>CLAW</div>
      <div class="badge">NEW SIGNUP</div>
    </div>

    <div class="field">
      <div class="label">NAME</div>
      <div class="value">${firstName} ${lastName}</div>
    </div>

    <div class="field">
      <div class="label">EMAIL</div>
      <div class="value highlight">${email}</div>
    </div>

    ${github ? `<div class="field">
      <div class="label">GITHUB</div>
      <div class="value"><a href="https://github.com/${github}" style="color:#00c4ff;">github.com/${github}</a></div>
    </div>` : ''}

    <div class="field">
      <div class="label">BASE MODEL</div>
      <div class="value">${model || 'Not specified'}</div>
    </div>

    <div class="field">
      <div class="label">USE CASE</div>
      <div class="value">${useCase || 'Not specified'}</div>
    </div>

    ${about ? `<div class="field">
      <div class="label">ABOUT PROJECT</div>
      <div class="value">${about}</div>
    </div>` : ''}

    <div class="footer">
      Submitted via EvoClaw website · ${new Date().toUTCString()}
    </div>
  </div>
</body>
</html>`;

  // ── Email 2: Welcome email TO the user ──
  const userEmailHTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body { font-family: -apple-system, sans-serif; background: #05070f; color: #dde6f5; margin: 0; padding: 0; }
    .wrap { max-width: 600px; margin: 0 auto; padding: 48px 32px; }
    .header { text-align: center; margin-bottom: 40px; }
    .logo { font-family: 'Courier New', monospace; font-size: 20px; font-weight: 700; letter-spacing: .12em; }
    .logo span { color: #00ff87; }
    h1 { font-size: 26px; font-weight: 300; line-height: 1.3; margin: 24px 0 12px; }
    h1 b { font-weight: 700; }
    p { font-size: 15px; color: #5e7494; line-height: 1.8; margin-bottom: 16px; }
    .card { background: #0c1020; border: 1px solid #1a2438; border-radius: 6px; padding: 24px; margin: 28px 0; }
    .card-title { font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: .16em; color: #2e4060; margin-bottom: 16px; }
    .step { display: flex; gap: 14px; margin-bottom: 16px; align-items: flex-start; }
    .step-n { width: 24px; height: 24px; border-radius: 50%; background: #00ff87; color: #000; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-family: 'Courier New', monospace; }
    .step-text { font-size: 14px; color: #dde6f5; line-height: 1.6; }
    .step-text code { font-family: 'Courier New', monospace; background: rgba(0,255,135,.08); color: #00ff87; padding: 1px 6px; border-radius: 3px; font-size: 12px; }
    .code-block { background: #020408; border: 1px solid #1a2438; border-radius: 6px; padding: 18px; font-family: 'Courier New', monospace; font-size: 12px; line-height: 2; color: #5e7494; margin: 16px 0; overflow-x: auto; }
    .code-block .g { color: #00ff87; }
    .code-block .b { color: #00c4ff; }
    .code-block .o { color: #ff8c42; }
    .btn { display: inline-block; background: #00ff87; color: #000; font-family: 'Courier New', monospace; font-size: 13px; font-weight: 700; letter-spacing: .08em; padding: 12px 28px; border-radius: 4px; text-decoration: none; margin-top: 8px; }
    .footer { margin-top: 48px; padding-top: 20px; border-top: 1px solid #1a2438; text-align: center; font-size: 12px; color: #2e4060; font-family: 'Courier New', monospace; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="logo">🦎 <span>EVO</span>CLAW</div>
      <h1>You're in, ${firstName}.<br/><b>Let's get you set up.</b></h1>
      <p>Here's everything you need to get EvoClaw running with <strong style="color:#dde6f5;">${model || 'your chosen model'}</strong> in under 5 minutes.</p>
    </div>

    <div class="card">
      <div class="card-title">QUICK START — 3 COMMANDS</div>
      <div class="code-block">
        <div><span style="color:#2e4060;"># 1. Install dependencies</span></div>
        <div><span class="b">pip</span> install fastapi uvicorn httpx openai transformers tinker tinker-cookbook</div>
        <div>&nbsp;</div>
        <div><span style="color:#2e4060;"># 2. Start OpenClaw proxy</span></div>
        <div><span class="b">bash</span> openclaw_model_kimi.sh</div>
        <div>&nbsp;</div>
        <div><span style="color:#2e4060;"># 3. Set API key and run</span></div>
        <div><span class="o">export</span> TINKER_API_KEY=<span class="g">"your_key_here"</span></div>
        <div><span class="b">python</span> examples/run_with_skills.py</div>
        <div>&nbsp;</div>
        <div><span class="g">🦎 EvoClaw running — your agent is now self-evolving.</span></div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">NEXT STEPS</div>
      <div class="step">
        <div class="step-n">1</div>
        <div class="step-text">Get your Tinker API key at <a href="https://www.thinkingmachines.ai/tinker/" style="color:#00c4ff;">thinkingmachines.ai/tinker</a> — it's free to start.</div>
      </div>
      <div class="step">
        <div class="step-n">2</div>
        <div class="step-text">Clone the repo: <code>git clone https://github.com/YOUR_USERNAME/EvoClaw</code></div>
      </div>
      <div class="step">
        <div class="step-n">3</div>
        <div class="step-text">Open <code>evoclaw/config.py</code> and set your model, reward threshold, and skill bank path.</div>
      </div>
      <div class="step">
        <div class="step-n">4</div>
        <div class="step-text">Run <code>python examples/run_with_skills.py</code> and start chatting — your agent begins evolving immediately.</div>
      </div>
    </div>

    <div style="text-align:center;margin-top:32px;">
      <a href="https://YOUR_USERNAME.github.io/EvoClaw/docs.html" class="btn">Read Full Documentation →</a>
    </div>

    <div class="footer">
      <p>EvoClaw · MIT Licensed · Open Source<br/>
      You received this because you signed up at evoclaw website.<br/>
      <a href="#" style="color:#2e4060;">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>`;

  try {
    // Send notification to owner
    const ownerRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'EvoClaw <onboarding@resend.dev>',
        to: [TO_EMAIL],
        subject: `🦎 New EvoClaw signup — ${firstName} ${lastName} (${model || 'model TBD'})`,
        html: ownerEmailHTML,
      }),
    });

    // Send welcome email to user
    const userRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'EvoClaw <onboarding@resend.dev>',
        to: [email],
        subject: `🦎 You're in, ${firstName} — EvoClaw setup guide inside`,
        html: userEmailHTML,
      }),
    });

    if (!ownerRes.ok || !userRes.ok) {
      const err = await userRes.text();
      throw new Error(`Resend error: ${err}`);
    }

    return res.status(200).json({ success: true });

  } catch (err) {
    console.error('Email error:', err);
    return res.status(500).json({ error: 'Failed to send email. Please try again.' });
  }
}
