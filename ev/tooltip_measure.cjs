// Reviewer's own driver: hover the plan chart on the study harness, read the tooltip's computed font-size.
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const wt = path.resolve(process.argv[2]); const b = await chromium.launch(); const out = [];
  for (const w of [375, 768, 1280]) for (const page of ["tile", "plan"]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const p = await ctx.newPage();
    await p.goto(`file://${wt}/docs/design/harmony/harness/harness.html?page=${page}`); await p.waitForTimeout(400);
    const box = await p.evaluate((pg) => { const sr = document.querySelector("heatpump-optimizer-card").shadowRoot; const sc = pg === "tile" ? sr : sr.querySelector("dialog[open]"); const s = [...sc.querySelectorAll("svg")].sort((a, c) => c.getBoundingClientRect().width * c.getBoundingClientRect().height - a.getBoundingClientRect().width * a.getBoundingClientRect().height)[0]; const r = s.getBoundingClientRect(); return { x: r.left + r.width * 0.4, y: r.top + r.height * 0.5 }; }, page);
    await p.mouse.move(box.x, box.y); await p.mouse.move(box.x + 3, box.y); await p.waitForTimeout(300);
    const r = await p.evaluate((pg) => { const sr = document.querySelector("heatpump-optimizer-card").shadowRoot; const sc = pg === "tile" ? sr : sr.querySelector("dialog[open]"); const t = [...sc.querySelectorAll(".tooltip")].filter((e) => e.getBoundingClientRect().height > 0 && getComputedStyle(e).display !== "none" && getComputedStyle(e).visibility !== "hidden"); return t.map((e) => parseFloat(getComputedStyle(e).fontSize).toFixed(2) + "px h" + e.getBoundingClientRect().height.toFixed(0)).join(",") || "no visible tooltip"; }, page);
    out.push(`RESULT w=${w} page=${page} tooltip=${r}`); await ctx.close();
  }
  await b.close(); console.log(out.join("\n"));
})();
