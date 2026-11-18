// Verifier V2 for D4-s1-01/s3-01/s3-02. Own metrics:
// P: per pipe, isPointInStroke along the midpoint normal in user units, converted to CSS px (hit geometry, not elementFromPoint);
//    plus count of ANY element carrying the same data-edge (a wider hit path would exist).
// E: empty-state, two states: {} and "setup sensors only, no plan entities"; count tabbable elements inside .legend via Tab-key walk.
// F: expanded dialog: median rendered glyph-box height of plan-svg text vs title glyph-box height (rect heights), leave-max-out.
import fs from "node:fs"; import path from "node:path"; import os from "node:os"; import { createRequire } from "node:module";
const repo = process.cwd(); const rig = await import(path.join(repo, "tests/card_rig.mjs"));
const { planStates, setupSensorStates, qaTopologies, DEFAULT_SPACE, HOUR } = rig;
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const { chromium } = createRequire(path.join(process.env.NODE_PATH, "x.js"))("playwright");
const SRC = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
const b = await chromium.launch({ executablePath: process.env.HPO_CHROME });
async function mk(w, h, coarse, st) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, hasTouch: coarse, isMobile: coarse });
  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR);
  const page = await ctx.newPage(); await page.goto("about:blank"); await page.addScriptTag({ content: SRC });
  await page.evaluate(async ([st, w]) => { document.body.style.margin = "0";
    const c = document.createElement("heatpump-optimizer-card"); c.style.display = "block"; c.style.width = (w - 16) + "px";
    c.setConfig({ type: "custom:heatpump-optimizer-card" }); c.hass = { states: st, language: "en", themes: { darkMode: false } };
    document.body.appendChild(c); await new Promise((r) => setTimeout(r, 150)); }, [st, w]);
  return { ctx, page };
}
const ss = () => { const st = { ...planStates(plan), ...setupSensorStates() }; st[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base; return st; };
// P
let pn = 0, p24 = 0, p44 = 0, pmax = 0, extraHit = 0;
for (const coarse of [false, true]) for (const w of [375, 1280]) {
  const { ctx, page } = await mk(w, 900, coarse, ss());
  const r = await page.evaluate(async () => { const c = document.querySelector("heatpump-optimizer-card"); const W = () => new Promise((r) => setTimeout(r, 120));
    c._onCardClick({}); await W(); c.dialog.page = "setup"; c._render(); await W(); const root = c.shadowRoot;
    root.querySelector(".layout-edit-toggle").click(); await W();
    return [...root.querySelectorAll("path.setup-pipe[data-edge]")].map((p) => { const L = p.getTotalLength(); const m = p.getScreenCTM(); const s = Math.hypot(m.a, m.b);
      const a = p.getPointAtLength(L / 2 - 0.5), q = p.getPointAtLength(L / 2 + 0.5), o = p.getPointAtLength(L / 2);
      let nx = -(q.y - a.y), ny = q.x - a.x; const nl = Math.hypot(nx, ny); nx /= nl; ny /= nl; let n = 0; const st = 0.05;
      for (let d = -60; d <= 60; d += st) { const pt = p.ownerSVGElement.createSVGPoint(); pt.x = o.x + nx * d; pt.y = o.y + ny * d; if (p.isPointInStroke(pt)) n++; }
      return { px: n * st * s, same: root.querySelectorAll(`[data-edge="${p.getAttribute("data-edge")}"]`).length, pe: getComputedStyle(p).pointerEvents }; }); });
  for (const x of r) { pn++; pmax = Math.max(pmax, x.px); if (!coarse && x.px < 24) p24++; if (coarse && x.px < 44) p44++; if (x.same > 1) extraHit++; }
  console.log(`P ${coarse ? "coarse" : "fine"}/${w}: ${r.map((x) => x.px.toFixed(2) + "/" + x.same + "/" + x.pe).join(" ")}`);
  await ctx.close();
}
console.log(`IND pipes=${pn} fine_under24=${p24} coarse_under44=${p44} stroke_px_max=${pmax.toFixed(2)} pipes_with_extra_dataedge_elems=${extraHit}`);
// E
for (const [nm, st] of [["empty", {}], ["sensors_only", (() => { const s = setupSensorStates(); return s; })()]]) {
  const { ctx, page } = await mk(1280, 800, false, st);
  await page.locator("body").click({ position: { x: 2, y: 790 } });
  let inLegend = 0, total = 0; const seen = new Set();
  for (let i = 0; i < 40; i++) { await page.keyboard.press("Tab");
    const k = await page.evaluate(() => { const root = document.querySelector("heatpump-optimizer-card").shadowRoot; const a = root.activeElement; if (!a) return null; return { leg: !!a.closest(".legend"), id: a.outerHTML.slice(0, 80) }; });
    if (!k || seen.has(k.id)) break; seen.add(k.id); total++; if (k.leg) inLegend++; }
  const vis = await page.evaluate(() => { const r = document.querySelector("heatpump-optimizer-card").shadowRoot; return { chips: [...r.querySelectorAll(".legend .chip")].filter((c) => c.getBoundingClientRect().height > 0).length, empty: !!r.querySelector(".empty") }; });
  console.log(`IND E ${nm}: tab_stops_total=${total} tab_stops_in_legend=${inLegend} visible_chips=${vis.chips} empty_msg=${vis.empty}`);
  await ctx.close();
}
// F
for (const w of [1280, 1920]) {
  const { ctx, page } = await mk(w, 900, false, planStates(plan));
  const r = await page.evaluate(async () => { const c = document.querySelector("heatpump-optimizer-card"); c._onCardClick({}); await new Promise((r) => setTimeout(r, 200));
    const d = c.shadowRoot.querySelector("dialog[open]"); const t = d.querySelector(".title"); const th = t.getBoundingClientRect().height; const tfs = parseFloat(getComputedStyle(t).fontSize);
    const svg = d.querySelector("svg[preserveAspectRatio='none']");
    const hs = [...svg.querySelectorAll("text")].filter((x) => x.textContent.trim()).map((x) => x.getBoundingClientRect().height).sort((a, b) => a - b);
    return { th, tfs, n: hs.length, med: hs[hs.length >> 1], max: hs[hs.length - 1], second: hs[hs.length - 2], frac: hs.filter((h) => h > th).length }; });
  console.log(`IND F ${w}: title_rect_h=${r.th.toFixed(2)} title_fs=${r.tfs} svg_text n=${r.n} median_h=${r.med.toFixed(2)} max_h=${r.max.toFixed(2)} second_h=${r.second.toFixed(2)} median_over_title=${(r.med / r.th).toFixed(3)} n_taller_than_title=${r.frac}`);
  await ctx.close();
}
await b.close(); console.log(`load1=${os.loadavg()[0].toFixed(2)} thread_factor=1.0`);
