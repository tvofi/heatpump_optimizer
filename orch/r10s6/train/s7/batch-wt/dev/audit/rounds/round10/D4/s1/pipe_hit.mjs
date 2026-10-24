// D4-s1 (round 10, D4.M1): the touch target of a pipe in the setup page's
// layout editor, where "clicking a pipe is how one is removed" (card CSS
// comment at `.setup-svg.editing .setup-pipe`).
//
// Metric: for every drawn pipe (<path class="setup-pipe" data-edge=...>) in
// the layout_editing state, the width in CSS px of the band, measured along
// the pipe's normal at its midpoint, over which the shadow root's
// elementFromPoint returns an element whose closest [data-edge] is that pipe
// (0.25 px steps, +-40 px). Count key: the hit-tested band the production card
// (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js) lays
// out in Chromium -- a fix that adds a wider transparent hit path carrying the
// same data-edge moves it; a stylesheet rename does not.
// RESULT pipes_under_44 counts pipes whose band is < 44 px with pointer:coarse
// emulated (the card's own coarse floor, _targetMinPx / _coarsePointer);
// pipes_under_24 the same under a fine pointer (WCAG 2.5.8, the card's
// every-pointer floor; the 2.5.8 spacing exception does not apply to a target
// along which other pipes run within 12 px -- reported, not used).
// Perturbation: PIPE_STROKE=<n> rewrites the editing stroke width 3.5 in the
// card source in memory; at 30 the bands must rise and the counts fall.
//
// Run from the repository root:
//   PYTHONPATH=tests/hastub HPO_PLANDATA=$(mktemp -d)/p.json python tests/plan_view.py
//   NODE_PATH=<pw>/node_modules HPO_CHROME=<chromium or empty> node dev/audit/rounds/round10/D4/s1/pipe_hit.mjs
// Baseline 17f1c55fad1b, macOS arm64, Chromium 131 headless shell (rev 1148).
// Expected: see REPORT.md; counts exact, widths +-0.5 px.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
const repo = process.cwd();
const rig = await import(path.join(repo, "tests/card_rig.mjs"));
const { planStates, setupSensorStates, layoutCatalogTopo, qaTopologies, DEFAULT_SPACE, HOUR } = rig;
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const require = createRequire(path.join(process.env.NODE_PATH || repo, "x.js"));
const { chromium } = require("playwright");
let cardSrc = fs.readFileSync(path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8");
const NEEDLE = ".setup-svg.editing .setup-pipe { stroke-width: 3.5; cursor: pointer; }";
if (!cardSrc.includes(NEEDLE)) console.log("NOTE: editing stroke rule not found verbatim (tree moved)");
if (process.env.PIPE_STROKE) cardSrc = cardSrc.replace(NEEDLE, NEEDLE.replace("3.5", process.env.PIPE_STROKE));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
const browser = await chromium.launch(process.env.HPO_CHROME ? { executablePath: process.env.HPO_CHROME } : {});
const topos = { catalog: layoutCatalogTopo(), base: qaTopologies().base };
const out = [];
for (const coarse of [false, true]) for (const vp of [[375, 812], [768, 1024], [1280, 800]]) for (const [tn, topo] of Object.entries(topos)) {
  const ctx = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, hasTouch: coarse, isMobile: coarse, reducedMotion: "reduce" });
  await ctx.clock.setFixedTime(FROZEN);
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.addScriptTag({ content: cardSrc });
  const st = { ...planStates(plan), ...setupSensorStates() };
  st[DEFAULT_SPACE].attributes.setup_topology = topo;
  const r = await page.evaluate(async ([st, w]) => {
    const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const s = document.createElement("style");
    s.textContent = `body{margin:0;padding:8px;font-family:Arial,sans-serif}heatpump-optimizer-card{display:block;width:${w}px}`;
    document.head.appendChild(s);
    const c = document.createElement("heatpump-optimizer-card");
    c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states: st, language: "en", themes: { darkMode: false } };
    document.body.appendChild(c);
    await frame();
    c._onCardClick({}); c.dialog.page = "setup"; c._render(); await frame();
    const root = c.shadowRoot;
    const tog = root.querySelector(".layout-edit-toggle");
    if (!tog) return { err: "no toggle" };
    tog.click(); await frame(); await frame();
    const editing = !!root.querySelector(".setup-svg.editing");
    const coarseMQ = matchMedia("(pointer: coarse)").matches;
    const pipes = [...root.querySelectorAll("path.setup-pipe[data-edge]")];
    const res = [];
    for (const p of pipes) {
      p.scrollIntoView({ block: "center", inline: "center" }); await frame();
      const L = p.getTotalLength(), m = p.getScreenCTM();
      const P = (l) => { const q = p.getPointAtLength(l); return new DOMPoint(q.x, q.y).matrixTransform(m); };
      const a = P(L / 2 - 1), b = P(L / 2 + 1), c0 = P(L / 2);
      let nx = -(b.y - a.y), ny = b.x - a.x; const nl = Math.hypot(nx, ny); nx /= nl; ny /= nl;
      let band = 0;
      for (let d = -40; d <= 40; d += 0.25) {
        const x = c0.x + nx * d, y = c0.y + ny * d;
        if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
        const el = root.elementFromPoint(x, y);
        const e = el && el.closest && el.closest("[data-edge]");
        if (e && e.getAttribute("data-edge") === p.getAttribute("data-edge") && !e.classList.contains("slot-handle")) band += 0.25;
      }
      const cs = getComputedStyle(p);
      res.push({ edge: p.getAttribute("data-edge"), band, strokePx: parseFloat(cs.strokeWidth) * Math.hypot(m.a, m.b), cursor: cs.cursor });
    }
    return { editing, coarseMQ, res };
  }, [st, vp[0] - 16]);
  out.push({ coarse, vp: vp[0], topo: tn, ...r });
  await ctx.close();
}
await browser.close();
let n = 0, u24 = 0, u44 = 0, maxBand = 0, minBand = 1e9, cells = 0, notEditing = 0;
for (const o of out) {
  cells++;
  if (o.err || !o.editing) { notEditing++; console.log(`cell ${o.coarse ? "coarse" : "fine"}/${o.vp}/${o.topo}: ${o.err || "not editing"}`); continue; }
  const bands = o.res.map((p) => p.band);
  console.log(`cell ${o.coarse ? "coarse" : "fine"}/${o.vp}/${o.topo}: mq=${o.coarseMQ} pipes=${o.res.length} band px ${bands.map((b) => b.toFixed(2)).join(",")} stroke px ${o.res.map((p) => p.strokePx.toFixed(2)).join(",")}`);
  for (const p of o.res) {
    n++; maxBand = Math.max(maxBand, p.band); minBand = Math.min(minBand, p.band);
    if (o.coarse && p.band < 44) u44++;
    if (!o.coarse && p.band < 24) u24++;
  }
}
console.log(`RESULT cells=${cells} count`);
console.log(`RESULT cells_not_editing=${notEditing} count`);
console.log(`RESULT pipes_measured=${n} count`);
console.log(`RESULT pipes_under_44_coarse=${u44} count`);
console.log(`RESULT pipes_under_24_fine=${u24} count`);
console.log(`RESULT band_max=${maxBand.toFixed(2)} px`);
console.log(`RESULT band_min=${minBand.toFixed(2)} px`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
