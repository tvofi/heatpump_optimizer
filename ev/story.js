const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({viewport:{width:1440,height:800}})).newPage();
  await p.goto('http://localhost:8765/index.html',{waitUntil:'networkidle'});
  const chain = () => p.evaluate(()=>{const s=document.querySelector('#how [role="img"]'); const o=[]; for(let e=s;e&&e!==document.body;e=e.parentElement) o.push(e.tagName+'.'+[...e.classList].join('.')); return o.join(' < ');});
  const seq=[];
  for (const n of [1,2,3,4,5,4,3,2,1]) {
    await p.evaluate(n=>{const el=document.querySelector(`[data-step="${n}"]`); const r=el.getBoundingClientRect(); scrollBy(0, r.top + r.height/2 - innerHeight/2);}, n);
    await p.waitForTimeout(600); seq.push(n+': '+await chain());
  }
  console.log(seq.join('\n')); await b.close(); })();
