f = open('docs.html', 'r', encoding='utf-8')
c = f.read()
f.close()

old = "event.target.classList.add('active');"
new = "var btn=el;while(btn&&btn.tagName!=='BUTTON'){btn=btn.parentElement;}if(btn){btn.classList.add('active');}"

if old in c:
    c = c.replace(old, new)
    f2 = open('docs.html', 'w', encoding='utf-8')
    f2.write(c)
    f2.close()
    print('FIXED')
else:
    print('NOT FOUND - already fixed or different text')

print('event.target remaining:', 'event.target' in c)
