with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"index.html: {len(c.splitlines())} lines")

# ── Find insertion point: before get-started section ──
INSERT_BEFORE = '<section class="section" id="get-started"'
if INSERT_BEFORE not in c:
    INSERT_BEFORE = '<footer class="footer">'

NEW_SECTIONS = '''
<!-- ── LEARNING MODES ── -->
<hr class="div"/>
<section class="section">
  <div class="container">
    <div class="section-divider reveal"><span>LEARNING MODES</span></div>
    <h2 class="section-title reveal">Two ways your agent <b>gets smarter.</b></h2>
    <p class="section-sub reveal">EvoClaw supports both lightweight signal learning and rich natural-language supervision — choose what fits your setup.</p>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px;" class="reveal">

      <!-- RL Mode -->
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:32px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:var(--green);"></div>
        <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.15em;color:var(--green);margin-bottom:12px;">MODE 01</div>
        <h3 style="font-size:1.2rem;font-weight:300;margin-bottom:12px;">Reinforcement Learning <b>(GRPO)</b></h3>
        <p style="color:var(--muted);font-size:.9rem;line-height:1.8;margin-bottom:20px;">Uses Group Relative Policy Optimization. The agent learns from implicit feedback — every scored conversation turn updates the policy automatically.</p>
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;font-family:var(--mono);font-size:.72rem;color:var(--text);line-height:1.9;">
          <span style="color:var(--dim)"># Lightweight — works with any signal</span><br>
          config = EvoClawConfig(<br>
          &nbsp;&nbsp;loss_fn=<span style="color:#ffcb6b">"importance_sampling"</span>,<br>
          &nbsp;&nbsp;use_prm=<span style="color:var(--green)">True</span>,<br>
          )
        </div>
        <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
          <span style="font-family:var(--mono);font-size:.62rem;background:rgba(0,255,136,.1);color:var(--green);padding:3px 10px;border-radius:20px;border:1px solid rgba(0,255,136,.2);">GRPO</span>
          <span style="font-family:var(--mono);font-size:.62rem;background:rgba(0,255,136,.1);color:var(--green);padding:3px 10px;border-radius:20px;border:1px solid rgba(0,255,136,.2);">PPO</span>
          <span style="font-family:var(--mono);font-size:.62rem;background:rgba(0,255,136,.1);color:var(--green);padding:3px 10px;border-radius:20px;border:1px solid rgba(0,255,136,.2);">CISPO</span>
        </div>
      </div>

      <!-- OPD Mode -->
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:32px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#00c4ff;"></div>
        <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.15em;color:#00c4ff;margin-bottom:12px;">MODE 02</div>
        <h3 style="font-size:1.2rem;font-weight:300;margin-bottom:12px;">On-Policy Distillation <b>(OPD)</b></h3>
        <p style="color:var(--muted);font-size:.9rem;line-height:1.8;margin-bottom:20px;">Leverages richer natural-language supervision from a teacher model. Best when you have access to a strong judge LLM for high-quality textual feedback.</p>
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;font-family:var(--mono);font-size:.72rem;color:var(--text);line-height:1.9;">
          <span style="color:var(--dim)"># High quality — needs judge model</span><br>
          config = EvoClawConfig(<br>
          &nbsp;&nbsp;use_prm=<span style="color:var(--green)">True</span>,<br>
          &nbsp;&nbsp;prm_model=<span style="color:#ffcb6b">"gpt-5.2"</span>,<br>
          )
        </div>
        <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
          <span style="font-family:var(--mono);font-size:.62rem;background:rgba(0,196,255,.1);color:#00c4ff;padding:3px 10px;border-radius:20px;border:1px solid rgba(0,196,255,.2);">TEACHER MODEL</span>
          <span style="font-family:var(--mono);font-size:.62rem;background:rgba(0,196,255,.1);color:#00c4ff;padding:3px 10px;border-radius:20px;border:1px solid rgba(0,196,255,.2);">RICH FEEDBACK</span>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- ── SUPPORTED MODELS ── -->
<hr class="div"/>
<section class="section section-alt">
  <div class="container">
    <div class="section-divider reveal"><span>SUPPORTED MODELS</span></div>
    <h2 class="section-title reveal">Works with the <b>models you already use.</b></h2>
    <p class="section-sub reveal">EvoClaw is model-agnostic. Use Kimi-2.5 for maximum quality, Qwen3-4B for lightweight deployment, or any Groq/OpenAI-compatible endpoint.</p>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:40px;" class="reveal">

      <div style="background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:24px;text-align:center;">
        <div style="font-size:2rem;margin-bottom:12px;">🌙</div>
        <div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.1em;color:var(--green);margin-bottom:8px;">RECOMMENDED</div>
        <div style="font-size:1rem;font-weight:600;margin-bottom:6px;">Kimi-2.5</div>
        <div style="font-family:var(--mono);font-size:.7rem;color:var(--dim);margin-bottom:12px;">~200B MoE</div>
        <p style="font-size:.82rem;color:var(--muted);line-height:1.7;">Best quality, long context, strong reasoning. Recommended for production.</p>
        <div style="margin-top:12px;font-family:var(--mono);font-size:.65rem;color:var(--dim);background:var(--bg2);border-radius:4px;padding:6px;">moonshotai/Kimi-2.5</div>
      </div>

      <div style="background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:24px;text-align:center;">
        <div style="font-size:2rem;margin-bottom:12px;">⚡</div>
        <div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.1em;color:#00c4ff;margin-bottom:8px;">LIGHTWEIGHT</div>
        <div style="font-size:1rem;font-weight:600;margin-bottom:6px;">Qwen3-4B</div>
        <div style="font-family:var(--mono);font-size:.7rem;color:var(--dim);margin-bottom:12px;">4B params</div>
        <p style="font-size:.82rem;color:var(--muted);line-height:1.7;">Fast iteration, lower API costs. Great for development and constrained budgets.</p>
        <div style="margin-top:12px;font-family:var(--mono);font-size:.65rem;color:var(--dim);background:var(--bg2);border-radius:4px;padding:6px;">Qwen/Qwen3-4B</div>
      </div>

      <div style="background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:24px;text-align:center;">
        <div style="font-size:2rem;margin-bottom:12px;">🔌</div>
        <div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.1em;color:#ffcb6b;margin-bottom:8px;">COMPATIBLE</div>
        <div style="font-size:1rem;font-weight:600;margin-bottom:6px;">Any API</div>
        <div style="font-family:var(--mono);font-size:.7rem;color:var(--dim);margin-bottom:12px;">OpenAI-compatible</div>
        <p style="font-size:.82rem;color:var(--muted);line-height:1.7;">Groq, OpenAI, Anthropic, or any Tinker-supported endpoint. Plug and play.</p>
        <div style="margin-top:12px;font-family:var(--mono);font-size:.65rem;color:var(--dim);background:var(--bg2);border-radius:4px;padding:6px;">llama · gpt · claude</div>
      </div>

    </div>
  </div>
</section>

<!-- ── CONFIG HIGHLIGHTS ── -->
<hr class="div"/>
<section class="section">
  <div class="container">
    <div class="section-divider reveal"><span>CONFIGURATION</span></div>
    <h2 class="section-title reveal">One config object. <b>Full control.</b></h2>
    <p class="section-sub reveal">All settings are passed as a single <code>EvoClawConfig</code> instance — no YAML files, no env sprawl.</p>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:40px;align-items:start;" class="reveal">

      <!-- Key params table -->
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
          <thead>
            <tr style="border-bottom:1px solid var(--border);">
              <th style="font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--dim);padding:8px 12px;text-align:left;">FIELD</th>
              <th style="font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--dim);padding:8px 12px;text-align:left;">DEFAULT</th>
              <th style="font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--dim);padding:8px 12px;text-align:left;">DESCRIPTION</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">loss_fn</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">"importance_sampling"</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">RL loss: importance_sampling / ppo / cispo</td></tr>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">use_prm</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">True</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">Enable PRM reward scoring per turn</td></tr>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">use_skills</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">False</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">Inject skills into system prompt</td></tr>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">batch_size</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">32</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">Turns before each training step</td></tr>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">lora_rank</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">32</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">LoRA rank. Higher = more capacity</td></tr>
            <tr style="border-bottom:1px solid var(--border);"><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">enable_skill_evolution</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">False</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">Auto-generate skills from failures</td></tr>
            <tr><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--green);">proxy_port</td><td style="padding:10px 12px;font-family:var(--mono);font-size:.72rem;color:var(--dim);">30000</td><td style="padding:10px 12px;color:var(--muted);font-size:.8rem;">Proxy listen port (default: 8080 in EvoClaw)</td></tr>
          </tbody>
        </table>
        <div style="margin-top:12px;">
          <a href="docs.html#config-ref" style="font-family:var(--mono);font-size:.72rem;color:var(--green);text-decoration:none;">VIEW FULL CONFIG REFERENCE →</a>
        </div>
      </div>

      <!-- Code example -->
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden;">
        <div style="background:var(--bg);border-bottom:1px solid var(--border);padding:10px 16px;font-family:var(--mono);font-size:.65rem;color:var(--dim);letter-spacing:.1em;">FULL EXAMPLE</div>
        <div style="padding:20px;font-family:var(--mono);font-size:.75rem;line-height:2;color:var(--text);">
          <span style="color:var(--dim)">from</span> evoclaw <span style="color:var(--dim)">import</span> EvoClawConfig<br>
          <br>
          config = EvoClawConfig(<br>
          &nbsp;&nbsp;model_name=<span style="color:#ffcb6b">"moonshotai/Kimi-2.5"</span>,<br>
          &nbsp;&nbsp;loss_fn=<span style="color:#ffcb6b">"importance_sampling"</span>,<br>
          &nbsp;&nbsp;use_prm=<span style="color:var(--green)">True</span>,<br>
          &nbsp;&nbsp;use_skills=<span style="color:var(--green)">True</span>,<br>
          &nbsp;&nbsp;enable_skill_evolution=<span style="color:var(--green)">True</span>,<br>
          &nbsp;&nbsp;batch_size=<span style="color:#c3e88d">32</span>,<br>
          &nbsp;&nbsp;lora_rank=<span style="color:#c3e88d">32</span>,<br>
          )<br>
          <br>
          <span style="color:var(--dim)"># That's it — start chatting</span><br>
          evoclaw start <span style="color:var(--dim)">--config</span> config
        </div>
      </div>

    </div>
  </div>
</section>

'''

if 'LEARNING MODES' not in c:
    c = c.replace(INSERT_BEFORE, NEW_SECTIONS + INSERT_BEFORE)
    print("✅ Learning Modes section added")
    print("✅ Supported Models section added")
    print("✅ Configuration highlights added")
else:
    print("⚠ Sections already exist")

# Also update hero badge version
c = c.replace('v0.1.0 &nbsp;·&nbsp;', 'v0.2.0 &nbsp;·&nbsp;')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f"\n✅ index.html saved: {len(c.splitlines())} lines")
print("\ngit add -f index.html")
