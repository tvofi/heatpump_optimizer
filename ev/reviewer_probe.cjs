const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const U = 'http://127.0.0.1:8765/index.html';
  for (const width of [360, 1440]) {
    const p = await (await b.newContext({ viewport: { width, height: 800 } })).newPage(); await p.goto(U); await p.waitForTimeout(400);
    const small = await p.evaluate(() => [...document.querySelectorAll('a,button,label,input,summary,[tabindex]')].filter(e => e.getClientRects().length).map(e => { const r = e.getBoundingClientRect(); return [e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).replace(/ /g, '.') : ''), (e.textContent.trim() || e.getAttribute('aria-label') || '').slice(0, 28), Math.round(r.width), Math.round(r.height)]; }).filter(x => x[3] < 40 || x[2] < 40));
    console.log(`RESULT targets<40 at ${width}px: ${small.length}`); for (const s of small) console.log('   ', JSON.stringify(s));
    const seen = []; let noring = [];
    for (let i = 0; i < 120; i++) { await p.keyboard.press('Tab'); const f = await p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const c = getComputedStyle(e); const lab = e.closest('label'); const lc = lab ? getComputedStyle(lab) : null; return { k: e.tagName.toLowerCase() + '#' + e.id + '.' + String(e.className) + '|' + (e.textContent.trim() || e.getAttribute('aria-label') || '').slice(0, 24), ring: (c.outlineStyle !== 'none' && parseFloat(c.outlineWidth) > 0) || (lc && lc.outlineStyle !== 'none' && parseFloat(lc.outlineWidth) > 0) || c.boxShadow !== 'none' }; }); if (!f) break; if (seen.includes(f.k)) break; seen.push(f.k); if (!f.ring) noring.push(f.k); }
    const total = await p.evaluate(() => [...document.querySelectorAll('a[href],button,input,[tabindex]:not([tabindex="-1"])')].length);
    console.log(`RESULT tab stops at ${width}px: ${seen.length} reached; focusable elements in the DOM ${total}; without visible ring ${noring.length} ${JSON.stringify(noring.slice(0, 8))}`);
    await p.context().close();
  }
  { const ctx = await b.newContext({ viewport: { width: 1440, height: 800 } }); const p = await ctx.newPage(); const msgs = [];
    p.on('console', m => msgs.push(m.text())); p.on('pageerror', e => msgs.push(e.message));
    const st = () => p.evaluate(() => { const pr = document.querySelector('.progress'); const c = getComputedStyle(pr); const r = pr.getBoundingClientRect(); return { display: c.display, w: Math.round(r.width), h: Math.round(r.height), transform: c.transform, opacity: c.opacity, anim: c.animationName, tl: c.animationTimeline }; });
    await p.goto(U); await p.evaluate(() => scrollTo(0, 2000)); await p.waitForTimeout(300); console.log('RESULT progress, engine with scroll timelines:', JSON.stringify(await st()));
    await p.route('**/index.html', async r => { const resp = await r.fetch(); let t = await resp.text(); const n = t.split('@supports (animation-timeline: scroll())').length - 1; t = t.replace('@supports (animation-timeline: scroll())', '@supports (animation-timeline: nonesuch-value())'); console.log('   replaced', n); r.fulfill({ response: resp, body: t }); });
    await p.goto(U); await p.evaluate(() => scrollTo(0, 2000)); await p.waitForTimeout(300); console.log('RESULT progress, @supports for scroll timelines false:', JSON.stringify(await st()), 'console', msgs.length); await ctx.close(); }
  { const ctx = await b.newContext({ viewport: { width: 1440, height: 800 } }); const p = await ctx.newPage(); await p.goto(U);
    const r = await p.evaluate(() => { document.querySelectorAll('style,link[rel=stylesheet]').forEach(e => e.remove()); document.querySelectorAll('[style]').forEach(e => e.removeAttribute('style')); const ids = ['top', 'main', 'how', 'card', 'features', 'works-with', 'install', 'limits', 'ai', 'docs']; const ys = ids.map(i => [i, Math.round(document.getElementById(i).getBoundingClientRect().top + scrollY)]); const hs = [...document.querySelectorAll('h1,h2,h3')].map(h => [h.tagName, h.textContent.trim().slice(0, 40), Math.round(h.getBoundingClientRect().top + scrollY), h.getClientRects().length]); return { ys, hs }; });
    console.log('RESULT styles off, anchor tops:', JSON.stringify(r.ys)); let mono = true; for (let i = 1; i < r.hs.length; i++) if (r.hs[i][2] < r.hs[i - 1][2]) mono = false; console.log('RESULT styles off, headings top to bottom in document order:', mono, 'count', r.hs.length); await ctx.close(); }
  await b.close();
})();
