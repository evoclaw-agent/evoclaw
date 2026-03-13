demo_add = """
<div style="background:var(--bg);border-top:1px solid var(--border);padding:80px 0;">
  <div class="container">
    <div style="text-align:center;margin-bottom:48px;">
      <span class="label">PROXY INTERCEPT FLOW</span>
      <h2 style="font-size:clamp(1.6rem,3vw,2.2rem);font-weight:300;letter-spacing:-.03em;margin-top:12px;">What happens <b>inside EvoClaw</b></h2>
      <p style="color:var(--muted);max-width:500px;margin:12px auto 0;font-size:.9rem;line-height:1.85;">Every request goes through 4 stages in under 15ms overhead.</p>
    </div>
    <div style="max-width:780px;margin:0 auto;display:flex;flex-direction:column;gap:0;">
      <div class="iflow-stage" id="ifs1"><div class="iflow-num">01</div><div class="iflow-body"><div class="iflow-title">INTERCEPT</div><div class="iflow-desc">EvoClaw listens on localhost:8080 — drop-in for any OpenAI-compatible endpoint. Your app doesn't change.</div><div class="iflow-code">POST http://localhost:8080/v1/chat/completions</div></div><div class="iflow-status" id="ifs1s">WAITING</div></div>
      <div style="width:2px;height:24px;background:var(--border);margin:0 auto;" id="ifc1"></div>
      <div class="iflow-stage" id="ifs2"><div class="iflow-num">02</div><div class="iflow-body"><div class="iflow-title">SCORE (PRM)</div><div class="iflow-desc">Conversation scored by Process Reward Model via Groq. High scores trigger skill evolution.</div><div class="iflow-code" id="ifc2code">prm_score = scorer.score(messages)  # 0.84</div></div><div class="iflow-status" id="ifs2s">WAITING</div></div>
      <div style="width:2px;height:24px;background:var(--border);margin:0 auto;" id="ifc2"></div>
      <div class="iflow-stage" id="ifs3"><div class="iflow-num">03</div><div class="iflow-body"><div class="iflow-title">INJECT SKILLS</div><div class="iflow-desc">Relevant skills from SkillBank injected into system prompt automatically.</div><div class="iflow-code" id="ifc3code">skills = skill_bank.get_relevant(messages)</div></div><div class="iflow-status" id="ifs3s">WAITING</div></div>
      <div style="width:2px;height:24px;background:var(--border);margin:0 auto;" id="ifc4"></div>
      <div class="iflow-stage" id="ifs4"><div class="iflow-num">04</div><div class="iflow-body"><div class="iflow-title">FORWARD + LEARN</div><div class="iflow-desc">Enriched request forwarded to model. Response stored for Tinker LoRA training.</div><div class="iflow-code">return response  # transparent to caller</div></div><div class="iflow-status" id="ifs4s">WAITING</div></div>
    </div>
    <div style="text-align:center;margin-top:40px;">
      <button onclick="runInterceptDemo()" id="interceptBtn" style="background:var(--green);color:#000;font-family:var(--mono);font-size:.75rem;letter-spacing:.12em;font-weight:700;padding:12px 32px;border-radius:6px;border:none;cursor:pointer;">&#9654; RUN INTERCEPT DEMO</button>
      <div style="margin-top:16px;font-family:var(--mono);font-size:.72rem;color:var(--dim)" id="interceptTimer">OVERHEAD: -</div>
    </div>
  </div>
</div>
<style>
.iflow-stage{display:flex;align-items:flex-start;gap:20px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:24px;transition:all .3s;}
.iflow-stage.active{border-color:var(--green);background:rgba(0,255,136,.04);}
.iflow-stage.done{border-color:rgba(0,255,136,.3);}
.iflow-num{font-family:var(--mono);font-size:1.4rem;font-weight:700;color:var(--border);flex-shrink:0;transition:color .3s;}
.iflow-stage.active .iflow-num,.iflow-stage.done .iflow-num{color:var(--green);}
.iflow-title{font-family:var(--mono);font-size:.65rem;letter-spacing:.14em;color:var(--green);margin-bottom:6px;}
.iflow-desc{font-size:.85rem;color:var(--muted);line-height:1.75;margin-bottom:10px;}
.iflow-code{background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:8px 12px;font-family:var(--mono);font-size:.72rem;color:var(--text);}
.iflow-status{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--dim);flex-shrink:0;transition:color .3s;}
.iflow-stage.active .iflow-status{color:var(--green);}
.iflow-stage.done .iflow-status{color:rgba(0,255,136,.5);}
</style>
<script>
function runInterceptDemo(){
  var btn=document.getElementById('interceptBtn');
  btn.disabled=true; btn.textContent='RUNNING...';
  var prm=(0.72+Math.random()*.23).toFixed(2);
  [1,2,3,4].forEach(function(n){
    document.getElementById('ifs'+n).classList.remove('active','done');
    document.getElementById('ifs'+n+'s').textContent='WAITING';
    var c=document.getElementById('ifc'+n); if(c) c.style.background='var(--border)';
  });
  function act(n,txt,delay){
    setTimeout(function(){ document.getElementById('ifs'+n).classList.add('active'); document.getElementById('ifs'+n+'s').textContent=txt; },delay);
    setTimeout(function(){ document.getElementById('ifs'+n).classList.remove('active'); document.getElementById('ifs'+n).classList.add('done'); document.getElementById('ifs'+n+'s').textContent='DONE'; var c=document.getElementById('ifc'+n); if(c)c.style.background='var(--green)'; },delay+700);
  }
  act(1,'INTERCEPTING...',0);
  setTimeout(function(){ document.getElementById('ifc2code').textContent='prm_score = scorer.score(messages)  # '+prm; },800);
  act(2,'SCORING...',800);
  setTimeout(function(){ document.getElementById('ifc3code').textContent='skills = skill_bank.get_relevant()  # [crypto-security, defi-expert]'; },1600);
  act(3,'INJECTING...',1600);
  act(4,'FORWARDING...',2400);
  setTimeout(function(){
    var oh=Math.floor(8+Math.random()*10);
    document.getElementById('interceptTimer').textContent='OVERHEAD: '+oh+'ms  |  PRM: '+prm+'  |  SKILLS: crypto-security, defi-expert';
    btn.disabled=false; btn.textContent='&#9654; RUN AGAIN';
  },3300);
}
</script>
"""

with open('demo.html', 'r', encoding='utf-8') as f:
    c = f.read()

if 'iflow-stage' in c:
    print('Already has iflow-stage, skipping')
else:
    c = c.replace('<footer class="footer">', demo_add + '\n<footer class="footer">')
    with open('demo.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - demo.html lines:', len(c.splitlines()))
    print('iflow-stage:', 'iflow-stage' in c)
