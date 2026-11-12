const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [name, port] of [['base 6cc15e9b8f53', 8766], ['head 1a35b70dbf2c', 8765]]) for (const width of [360, 390, 768, 1440]) { const p = await (await b.newContext({ viewport: { width, height: 800 } })).newPage(); await p.goto(`http://127.0.0.1:${port}/index.html`); await p.waitForTimeout(300);
    const r = await p.evaluate(() => { const m = s => [...document.querySelectorAll(s)].filter(e => e.getClientRects().length).map(e => [(e.textContent.trim() || '').slice(0, 22), Math.round(e.getBoundingClientRect().height)]); return { nav: m('header nav a, header .nav a, nav a'), next: m('a.next'), brand: m('a.brand'), bmc: m('a.bmc') }; });
    console.log(`RESULT ${name} ${width}px: nav ${JSON.stringify(r.nav)} next ${JSON.stringify(r.next)} brand ${JSON.stringify(r.brand)} bmc ${JSON.stringify(r.bmc)}`); await p.context().close(); }
  await b.close(); })();
