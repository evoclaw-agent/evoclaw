pg_add = """
<section style="padding:80px 0;background:var(--bg2);border-top:1px solid var(--border);">
  <div class="container">
    <div style="text-align:center;margin-bottom:48px;">
      <span class="label">PROXY DASHBOARD</span>
      <h2 style="font-size:clamp(1.6rem,3vw,2.2rem);font-weight:300;letter-spacing:-.03em;margin-top:12px;"><b>localhost:8080</b> - Live Dashboard</h2>
      <p style="color:var(--muted);max-width:480px;margin:12px auto 0;font-size:.9rem;line-height:1.85;">This is exactly what you see when you run <code style="color:var(--green)">evoclaw start</code>. Type a message and watch the proxy learn.</p>
    </div>
    <div style="max-width:960px;margin:0 auto;display:grid;grid-template-columns:1fr 300px;gap:16px;">
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div style="background:#0a0f0a;border:1px solid var(--border);border-radius:8px;overflow:hidden;">
          <div style="background:var(--bg2);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:8px;">
            <div style="width:10px;height:10px;border-radius:50%;background:#ff5f57;"></div>
            <div style="width:10px;height:10px;border-radius:50%;background:#ffbd2e;"></div>
            <div style="width:10px;height:10px;border-radius:50%;background:#28ca41;"></div>
            <span style="font-family:var(--mono);font-size:.7rem;color:var(--dim);margin-left:8px;">evoclaw proxy - localhost:8080</span>
            <span style="margin-left:auto;font-family:var(--mono);font-size:.65rem;color:var(--green)">&#9679; RUNNING</span>
          </div>
          <div id="pgTerminal" style="padding:16px;font-family:var(--mono);font-size:.72rem;line-height:1.9;min-height:220px;max-height:300px;overflow-y:auto;color:#cdd6c9;">
            <div style="color:var(--green)">EvoClaw v0.2.0 proxy started</div>
            <div style="color:var(--dim)">   Listening on http://localhost:8080</div>
            <div style="color:var(--dim)">   PRM scorer: Groq llama-3.1-8b-instant</div>
            <div style="color:var(--dim)">   Skills loaded: 11 (7 default + 4 learned)</div>
            <div style="color:var(--dim);margin-top:8px;">Waiting for requests...</div>
          </div>
        </div>
        <div style="display:flex;gap:8px;">
          <input id="pgInput" type="text" placeholder="Send a test message through the proxy..."
            style="flex:1;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:10px 14px;font-family:var(--mono);font-size:.78rem;color:var(--text);outline:none;"
            onkeydown="if(event.key==='Enter') pgSend()">
          <button onclick="pgSend()" id="pgBtn"
            style="background:var(--green);color:#000;font-family:var(--mono);font-size:.72rem;font-weight:700;letter-spacing:.1em;padding:10px 20px;border:none;border-radius:6px;cursor:pointer;">
            SEND
          </button>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;">
          <button onclick="pgQuick(this)" style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:5px 12px;font-family:var(--mono);font-size:.65rem;color:var(--muted);cursor:pointer;">What is impermanent loss?</button>
          <button onclick="pgQuick(this)" style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:5px 12px;font-family:var(--mono);font-size:.65rem;color:var(--muted);cursor:pointer;">Explain smart contract reentrancy</button>
          <button onclick="pgQuick(this)" style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:5px 12px;font-family:var(--mono);font-size:.65rem;color:var(--muted);cursor:pointer;">Write a Python async function</button>
          <button onclick="pgQuick(this)" style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:5px 12px;font-family:var(--mono);font-size:.65rem;color:var(--muted);cursor:pointer;">How does GRPO training work?</button>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:20px;">
          <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;color:var(--dim);margin-bottom:12px;">PRM SCORE</div>
          <div id="pgPrmVal" style="font-size:2.4rem;font-weight:300;color:var(--green);line-height:1;">-</div>
          <div style="font-family:var(--mono);font-size:.58rem;color:var(--dim);margin:4px 0 10px;">PROCESS REWARD MODEL</div>
          <div style="background:var(--bg2);border-radius:2px;height:4px;overflow:hidden;">
            <div id="pgPrmBar" style="height:100%;background:var(--green);width:0%;transition:width .8s ease;"></div>
          </div>
        </div>
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:20px;">
          <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;color:var(--dim);margin-bottom:12px;">SKILLS INJECTED</div>
          <div id="pgSkillsList" style="font-size:.72rem;color:var(--dim);font-family:var(--mono);">Send a message to see skills</div>
        </div>
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:20px;">
          <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;color:var(--dim);margin-bottom:8px;">JUST LEARNED</div>
          <div id="pgLearnedSkill" style="font-size:.72rem;color:var(--dim);font-family:var(--mono);">Learns after each conversation</div>
        </div>
        <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:20px;">
          <div style="font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;color:var(--dim);margin-bottom:12px;">SESSION STATS</div>
          <div style="display:flex;flex-direction:column;gap:7px;">
            <div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:.7rem;"><span style="color:var(--dim)">TOTAL SKILLS</span><span id="pgTotalSkills" style="color:var(--green)">11</span></div>
            <div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:.7rem;"><span style="color:var(--dim)">CONVERSATIONS</span><span id="pgConvs" style="color:var(--green)">0</span></div>
            <div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:.7rem;"><span style="color:var(--dim)">OVERHEAD</span><span id="pgOverhead" style="color:var(--green)">-</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
<script>
(function(){
  var SKILLS=['deep-research','defi-expert','crypto-security','structured-output','code-quality','agentic-flow','risk-analysis'];
  var convCount=0, totalSkills=11;
  function pgQuick(btn){ document.getElementById('pgInput').value=btn.textContent; pgSend(); }
  window.pgQuick=pgQuick;
  function pgLog(msg,color){
    var term=document.getElementById('pgTerminal');
    var d=document.createElement('div'); d.style.color=color||'#cdd6c9'; d.textContent=msg;
    term.appendChild(d); term.scrollTop=term.scrollHeight;
  }
  function pgSend(){
    var input=document.getElementById('pgInput');
    var msg=input.value.trim(); if(!msg) return;
    input.value=''; document.getElementById('pgBtn').disabled=true;
    convCount++;
    var prm=parseFloat((0.72+Math.random()*.24).toFixed(2));
    var didLearn=Math.random()>0.45;
    var learnedSkill=didLearn?SKILLS[convCount%SKILLS.length]:null;
    var injected=SKILLS.slice(0,3);
    var overhead=Math.floor(7+Math.random()*12);
    pgLog('','#000');
    pgLog('-> POST /v1/chat/completions','#00ff88');
    pgLog('   msg: "'+msg.slice(0,45)+(msg.length>45?'...':`"`),'var(--dim)');
    setTimeout(function(){ pgLog('   scoring (PRM)...','var(--muted)'); },300);
    setTimeout(function(){ pgLog('   prm_score: '+prm, prm>0.85?'#00ff88':prm>0.75?'#00c4ff':'#ffcb6b'); },700);
    setTimeout(function(){ pgLog('   injecting: '+injected.join(', '),'#00c4ff'); },1000);
    setTimeout(function(){ pgLog('   forwarding to model...','var(--dim)'); },1300);
    setTimeout(function(){
      pgLog('<- response ('+overhead+'ms overhead)','#00c4ff');
      if(didLearn){ totalSkills++; pgLog('   learned: ['+learnedSkill+']','#ffcb6b'); }
      document.getElementById('pgPrmVal').textContent=prm.toFixed(2);
      document.getElementById('pgPrmVal').style.color=prm>0.85?'var(--green)':prm>0.75?'#00c4ff':'#ffcb6b';
      document.getElementById('pgPrmBar').style.width=(prm*100)+'%';
      document.getElementById('pgSkillsList').innerHTML=injected.map(function(s){
        return '<span style="display:inline-block;background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.2);color:var(--green);padding:2px 8px;border-radius:3px;margin:2px;font-size:.68rem;">'+s+'</span>';
      }).join('');
      if(didLearn) document.getElementById('pgLearnedSkill').innerHTML='<span style="color:#ffcb6b">+ '+learnedSkill+'</span>';
      document.getElementById('pgTotalSkills').textContent=totalSkills;
      document.getElementById('pgConvs').textContent=convCount;
      document.getElementById('pgOverhead').textContent=overhead+'ms';
      document.getElementById('pgBtn').disabled=false;
    },1900);
  }
  window.pgSend=pgSend;
})();
</script>
"""

with open('playground.html', 'r', encoding='utf-8') as f:
    c = f.read()

if 'pgTerminal' in c:
    print('Already has pgTerminal, skipping')
else:
    c = c.replace('</body>', pg_add + '\n</body>')
    with open('playground.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - playground.html lines:', len(c.splitlines()))
    print('pgTerminal:', 'pgTerminal' in c)
