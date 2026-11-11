const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:900,height:800}})).newPage();
  await p.goto('http://localhost:8765/index.html',{waitUntil:'networkidle'});
  const r = await p.evaluate(()=>{const st=e=>{const c=getComputedStyle(e);return [c.fontFamily,c.fontWeight,c.fontSize,c.letterSpacing,c.textTransform,c.color,c.display].join(' / ')};
    const l=document.querySelector('legend .eyebrow'); const others=[...document.querySelectorAll('.eyebrow')].filter(e=>!e.closest('legend')).slice(0,2);
    return {legend:st(l), other:others.map(st), equal: others.length>0 && st(l).split(' / ').slice(0,6).join()==st(others[0]).split(' / ').slice(0,6).join()};});
  console.log(JSON.stringify(r,null,1));
  const fs=await p.$('fieldset'); await fs.scrollIntoViewIfNeeded(); await p.waitForTimeout(800); await fs.screenshot({path:'/tmp/claude-0/rev/shot-chooser-900.png'}); await b.close(); })();
