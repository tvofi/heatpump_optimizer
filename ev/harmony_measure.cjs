// Reviewer's own driver over the harmony study's harness (6aea0d10 harness.html + states.js).
// usage: node harmony_measure.cjs <worktree>   (study harness copied into <worktree>/docs/design/harmony/harness/)
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const wt = path.resolve(process.argv[2]);
  const b = await chromium.launch();
  const out = [];
  for (const theme of ["light", "dark"]) for (const w of [375, 768, 1280]) for (const page of ["tile", "plan", "setup", "savings", "advisor", "health"]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
    const p = await ctx.newPage();
    const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
    await p.goto(`file://${wt}/docs/design/harmony/harness/harness.html?page=${page}&theme=${theme}`);
    await p.waitForTimeout(400);
    const r = await p.evaluate(() => {
      const host = document.querySelector("heatpump-optimizer-card");
      const sr = host.shadowRoot || host;
      const px = (e) => parseFloat(getComputedStyle(e).fontSize);
      const dlg = sr.querySelector("dialog.expanded[open]") || sr.querySelector("dialog[open]");
      const scope = dlg || sr;
      const all = [...scope.querySelectorAll("*")].filter((e) => !(e instanceof SVGElement));
      const html = all.filter((e) => [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) && e.getClientRects().length && e.getBoundingClientRect().width > 0 && getComputedStyle(e).visibility !== "hidden");
      const below = html.filter((e) => px(e) < 12 - 1e-6).map((e) => `${e.tagName.toLowerCase()}.${[...e.classList].join(".")}=${px(e).toFixed(2)}`);
      const role = (s) => { const v = [...scope.querySelectorAll(s)].map(px); return v.length ? `${Math.min(...v).toFixed(2)}-${Math.max(...v).toFixed(2)}(n${v.length})` : "none"; };
      return { base: (dlg ? px(dlg) : px(host)).toFixed(2), html: html.length, below12: below.length, below, wiHint: role(".whatif .wi-hint"), wiGroupTitle: role(".whatif .wi-group-title") };
    });
    out.push(`RESULT theme=${theme} w=${w} page=${page} base=${r.base} htmlText=${r.html} below12=${r.below12} wi-hint=${r.wiHint} wi-group-title=${r.wiGroupTitle} errors=${errs.length}${r.below12 ? " below=" + r.below.join(",") : ""}`);
    await ctx.close();
  }
  await b.close();
  console.log(out.join("\n"));
})();
