// computed font-size of every .tooltip in the open dialog (hidden or not), study harness, plan page
const { chromium } = require("playwright"); const path = require("path");
(async () => { const wt = path.resolve(process.argv[2]); const b = await chromium.launch();
  for (const w of [375, 768, 1280]) { const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const p = await ctx.newPage();
    await p.goto(`file://${wt}/docs/design/harmony/harness/harness.html?page=plan`); await p.waitForTimeout(400);
    const r = await p.evaluate(() => [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("dialog[open] .tooltip")].map((e) => parseFloat(getComputedStyle(e).fontSize).toFixed(2)).join(","));
    console.log(`RESULT w=${w} page=plan dialog-tooltip-font=${r || "none"}`); await ctx.close(); }
  await b.close(); })();
