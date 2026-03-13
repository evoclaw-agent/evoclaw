with open('docs.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find and replace the entire <script> block
script_start = c.rfind('<script>')
script_end = c.rfind('</script>') + 9

new_script = """<script>
  function navTo(id, clicked){
    var t = document.getElementById(id);
    if(t){ t.scrollIntoView({behavior:'smooth', block:'start'}); }
    document.querySelectorAll('.sb-link').forEach(function(b){ b.classList.remove('active'); });
    var btn = clicked;
    while(btn && btn.tagName !== 'BUTTON'){ btn = btn.parentElement; }
    if(btn){ btn.classList.add('active'); }
  }

  function copyCode(btn){
    var code = btn.closest('.code-block').querySelector('pre').innerText;
    navigator.clipboard.writeText(code).then(function(){
      btn.textContent = 'COPIED'; setTimeout(function(){ btn.textContent = 'COPY'; }, 2000);
    });
  }

  window.addEventListener('scroll', function(){
    document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 10);
  });

  var sections = ['intro','install','quickstart','prerequisites','overview','proxy','buffer','prm','trainer','skills-intro','skill-injection','skill-evolution','custom-skills','config-ref','learning-modes','models','deploy','troubleshoot','faq','changelog'];
  var links = document.querySelectorAll('.sb-link');

  var sObs = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        var id = e.target.id;
        links.forEach(function(l){ l.classList.remove('active'); });
        var match = Array.from(links).find(function(l){
          return l.getAttribute('onclick') && l.getAttribute('onclick').indexOf("'"+id+"'") > -1;
        });
        if(match) match.classList.add('active');
      }
    });
  }, {rootMargin: '-20% 0px -70% 0px'});

  sections.forEach(function(id){ var el = document.getElementById(id); if(el) sObs.observe(el); });
</script>"""

c = c[:script_start] + new_script + c[script_end:]

print("navTo defined:", 'function navTo' in c)
print("scrollTo defined:", 'function scrollTo(' in c)
print("el already declared issue fixed: no more const el in navTo")

with open('docs.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("SAVED")
