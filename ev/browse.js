const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const out = [];
  for (const scheme of ['light','dark']) for (const w of [360,390,768,1440]) {
    const ctx = await b.newContext({ viewport:{width:w,height:800}, colorScheme:scheme });
    const p = await ctx.newPage(); const msgs=[]; const reqs=new Set();
    p.on('console', m => msgs.push(m.type()+': '+m.text())); p.on('pageerror', e => msgs.push('pageerror: '+e.message));
    p.on('request', r => { const u=new URL(r.url()); reqs.add(u.host + (u.pathname.match(/\.(woff2?|png|svg|webp|jpg)$/)?' asset':' '+u.pathname)); });
    await p.goto('http://localhost:8765/index.html', {waitUntil:'networkidle'});
    await p.evaluate(async()=>{ for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,30));} scrollTo(0,0);});
    await p.waitForTimeout(300);
    const sw = await p.evaluate(()=>[document.documentElement.scrollWidth, innerWidth, getComputedStyle(document.body).backgroundColor]);
    out.push(`${scheme} ${w}px: scrollWidth ${sw[0]} innerWidth ${sw[1]} bg ${sw[2]} console ${msgs.length} ${JSON.stringify(msgs)} hosts ${JSON.stringify([...new Set([...reqs].map(r=>r.split(' ')[0]))])}`);
    if (w===1440 || w===390) {
      await p.screenshot({path:`/tmp/claude-0/rev/shot-${scheme}-${w}.png`, fullPage:false});
      const how = await p.$('#how'); await how.scrollIntoViewIfNeeded(); await p.evaluate(()=>document.getElementById('how').scrollIntoView());
      await p.waitForTimeout(800); await p.screenshot({path:`/tmp/claude-0/rev/shot-${scheme}-${w}-how.png`});
    }
    if (w===1440 && scheme==='light') {
      const seq=[];
      for (const n of [1,2,3,4,5,4,3,2,1]) {
        await p.evaluate(n=>{const el=document.querySelector(`[data-step="${n}"]`); const r=el.getBoundingClientRect(); scrollBy(0, r.top + r.height/2 - innerHeight/2);}, n);
        await p.waitForTimeout(500);
        seq.push(n+':'+await p.evaluate(()=>{const s=document.querySelector('svg[role="img"]'); let e=s; while(e && !(e.className && typeof e.className==='string' && /\bl[1-5]|layer|on/.test(e.className))) e=e.parentElement; return e? e.className : 'none';}));
      }
      out.push('story 1440 light: '+seq.join(' | '));
    }
    await ctx.close();
  }
  console.log(out.join('\n')); await b.close();
})();
