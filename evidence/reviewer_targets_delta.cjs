// Reviewer's instrument (mine, not the finder's): every displayed interactive element at more widths and
// more page states than the harness's floor check walks; prints those under 40 px and overlapping pairs.
const { chromium } = require('playwright');
const ORIGIN = process.argv[2], LABEL = process.argv[3];
(async () => { const b = await chromium.launch();
  for (const width of [320, 360, 390, 480, 600, 768, 900, 939, 940, 1024, 1440]) {
    const p = await (await b.newContext({ viewport: { width, height: 800 } })).newPage(); await p.goto(ORIGIN + '/index.html', { waitUntil: 'load' }); await p.waitForTimeout(400);
    const tabs = await p.locator('[role=tab]').count();
    const states = [['default', async () => {}]];
    for (const id of ['cp1', 'cp2', 'cp3', 'cp0']) states.push([id, async () => p.locator('#' + id).check({ force: true })]);
    for (let i = 0; i < tabs; i++) states.push(['tab' + i, async () => p.locator('[role=tab]').nth(i).click({ force: true })]);
    for (const [st, go] of states) { await go(); await p.waitForTimeout(150);
      const r = await p.evaluate(() => {
        const els = [...document.querySelectorAll('a[href], button, summary, select, textarea, input, label, [tabindex], [role=tab], [onclick]')].filter(e => e.getClientRects().length && !(e.tagName === 'INPUT' && e.closest('label')));
        const inText = e => [...e.parentElement.childNodes].some(n => n.nodeType === 3 && n.data.trim());
        const nm = e => (e.textContent.trim() || e.getAttribute('aria-label') || e.tagName).slice(0, 26);
        const rows = els.map(e => { const r = e.getBoundingClientRect(); return { e, n: nm(e), w: Math.round(r.width), h: Math.round(r.height), disp: getComputedStyle(e).display, inText: inText(e), r }; });
        const small = rows.filter(x => x.w < 40 || x.h < 40).map(x => `${x.n}|${x.w}x${x.h}|${x.disp}|${x.inText ? 'in-text' : 'STANDALONE'}`);
        const over = []; for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) { const a = rows[i], c = rows[j]; if (a.e.contains(c.e) || c.e.contains(a.e)) continue;
          const ox = Math.min(a.r.right, c.r.right) - Math.max(a.r.left, c.r.left), oy = Math.min(a.r.bottom, c.r.bottom) - Math.max(a.r.top, c.r.top); if (ox > 0.5 && oy > 0.5) over.push(`${a.n}~${c.n}:${Math.round(ox)}x${Math.round(oy)}`); }
        return { n: rows.length, small, over, sw: document.documentElement.scrollWidth, iw: innerWidth };
      });
      console.log(`RESULT ${LABEL} ${width}px ${st}: ${r.n} elements; under40 ${JSON.stringify(r.small)}; overlapping ${JSON.stringify(r.over)}; scrollWidth ${r.sw}/${r.iw}`); }
    await p.context().close(); }
  await b.close(); })();
