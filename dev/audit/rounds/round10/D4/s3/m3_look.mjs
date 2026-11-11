// D4-s3 (round 10, D4.M3 professional look) -- two measurements in real Chromium.
//
// A. empty_state_chips: in the no-plan state (hass.states = {}), the number of
//    visible, focusable legend chips the inline card renders. Key: chips in the
//    card's shadow root matched by `.legend .chip` with a client rect; the dialog
//    path suppresses its legend when !anyData, the inline path does not.
//    Production symbol: heatpump-optimizer-card.js HeatPumpOptimizerCard._render
//    (`const legend = savingsTile ? "" : this.legend.html(...)`).
//    Perturbation --perturb=legend: that line gains `|| !anyData`; expect 0 (down from 8).
// B. chart_text_px / title_px: in the expanded dialog's plan page, the rendered size
//    of the chart's axis tick text (fontSize x getScreenCTM().a, i.e. what the
//    production font-size in viewBox units paints) divided by the dialog title's
//    px, per viewport width 1280/1920/2560 (height 900). Also the setup page's
//    diagram text. Key: rendered px of production <text> nodes.
//    Production symbols: chartFontUnits / FONT_EXPANDED (chart), the setup svg.
//    Perturbation --perturb=font: the expanded chart font gets a 13 px ceiling
//    (`const font = Math.min(chartFontUnits(...), 13*VIEW_W/drawnWidth)`); expect
//    the chart ratio to fall below 1 at every width.
//
// Run from the export root:
//   PYTHONPATH=tests/hastub python3 tests/plan_view.py   (with HPO_PLANDATA set)
//   HPO_PLANDATA=$TMPDIR/d4s3-plandata.json NODE_PATH=<pw>/node_modules \
//     HPO_CHROMIUM=<chromium binary, optional> node dev/audit/rounds/round10/D4/s3/m3_look.mjs [--perturb=legend|font]
// Expected (baseline 17f1c55fad1b, macOS arm64 B10, Chromium 131 / playwright 1.56.1):
//   empty_state_chips=8, empty_state_focusable_chips=8, control dialog_empty_chips=0 (exact);
//   plan_svg_text_over_title 1280=1.104, 1920=1.112, 2560=1.112; setup 1.190/1.198/1.198 (±0.02)
//   (the dialog caps its own width at ~1663 px, so 1920 and 2560 coincide)
// Counts and ratios: contention-immune.
import { createRequire } from "node:module"; import { readFileSync } from "node:fs"; import os from "node:os";
import { planStates, setupSensorStates, qaTopologies, DEFAULT_SPACE, HOUR } from "../../../../../../tests/card_rig.mjs";
const require = createRequire(import.meta.url); const { chromium } = require("playwright");
const perturb = (process.argv.find((a) => a.startsWith("--perturb=")) || "").split("=")[1] || "";
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
let SRC = readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
const swap = (a, b) => { if (!SRC.includes(a)) { console.error("perturbation anchor missing: " + a); process.exit(2); } SRC = SRC.replace(a, b); };
if (perturb === "legend") swap('const legend = savingsTile ? "" : this.legend.html(', 'const legend = savingsTile || !anyData ? "" : this.legend.html(');
if (perturb === "font") swap("const font = chartFontUnits(drawnWidth, expanded ? FONT_EXPANDED : FONT_BASE);",
  "const font = Math.min(chartFontUnits(drawnWidth, expanded ? FONT_EXPANDED : FONT_BASE), drawnWidth ? 13 * VIEW_W / drawnWidth : Infinity);");
const LIGHT = `--primary-color:#03a9f4;--primary-text-color:#212121;--secondary-text-color:#727272;--text-primary-color:#ffffff;--primary-background-color:#fafafa;--card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12);`;
const setupSt = () => { const st = { ...planStates(plan), ...setupSensorStates() }; st[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base; return st; };
const b = await chromium.launch({ executablePath: process.env.HPO_CHROMIUM || undefined });
async function mount(w, h, st, steps) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, reducedMotion: "reduce" });
  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR);
  const page = await ctx.newPage(); const errs = []; page.on("pageerror", (e) => errs.push(String(e)));
  await page.goto("about:blank"); await page.addScriptTag({ content: SRC });
  await page.evaluate(async ([css, st, steps]) => {
    const s = document.createElement("style"); s.textContent = css; document.head.appendChild(s);
    customElements.define("ha-card", class extends HTMLElement { constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{display:block;background:var(--card-background-color)}</style><slot></slot>"; } });
    const c = document.createElement("heatpump-optimizer-card"); c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states: st, language: "en", themes: { darkMode: false } }; document.body.appendChild(c);
    const wait = () => new Promise((r) => setTimeout(r, 120));
    await wait();
    for (const [op, a] of steps) { if (op === "cardClick") c._onCardClick({}); if (op === "page") { c.dialog.page = a; c._render(); } await wait(); }
    await wait();
  }, [`html{${LIGHT}} body{margin:0;padding:8px;font-family:Arial;background:var(--primary-background-color)} heatpump-optimizer-card{display:block;width:${Math.min(w - 16, 900)}px}`, st, steps]);
  return { ctx, page, errs };
}
// A
{
  const { ctx, page, errs } = await mount(1280, 800, {}, []);
  const r = await page.evaluate(() => {
    const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
    const chips = [...root.querySelectorAll(".legend .chip")].filter((c) => c.getClientRects().length && getComputedStyle(c).visibility === "visible");
    return { chips: chips.length, focusable: chips.filter((c) => c.tabIndex >= 0 && !c.disabled).length, empty: !!root.querySelector(".empty") };
  });
  console.log(`RESULT empty_state_chips=${r.chips} count`);
  console.log(`RESULT empty_state_focusable_chips=${r.focusable} count`);
  console.log(`RESULT empty_state_shown=${r.empty ? 1 : 0} bool`);
  if (errs.length) console.log("page errors: " + errs.join(" | "));
  // Control: the same empty state in the expanded dialog, whose legend is gated on anyData.
  const ctl = await page.evaluate(async () => { const c = document.querySelector("heatpump-optimizer-card"); c._onCardClick({});
    await new Promise((r) => setTimeout(r, 150)); const d = c.shadowRoot.querySelector("dialog[open]");
    return d ? [...d.querySelectorAll(".legend .chip")].filter((x) => x.getClientRects().length).length : -1; });
  console.log(`RESULT dialog_empty_chips=${ctl} count`);
  await page.screenshot({ path: `${os.tmpdir()}/d4s3-m3-empty-${perturb || "base"}.png` }); await ctx.close();
}
// B
for (const w of [1280, 1920, 2560]) {
  for (const [name, st, steps] of [["plan", planStates(plan), [["cardClick"]]], ["setup", setupSt(), [["cardClick"], ["page", "setup"]]]]) {
    const { ctx, page } = await mount(w, 900, st, steps);
    const r = await page.evaluate((name) => {
      const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
      const d = root.querySelector("dialog[open]"); if (!d) return null;
      const px = (el) => parseFloat(getComputedStyle(el).fontSize) * el.getScreenCTM().a;
      const title = d.querySelector(".title"); const tpx = title ? parseFloat(getComputedStyle(title).fontSize) : NaN;
      const svg = name === "plan" ? d.querySelector("svg[preserveAspectRatio='none']") : d.querySelector("svg.setup-svg");
      const texts = svg ? [...svg.querySelectorAll("text")].filter((t) => t.getClientRects().length && t.textContent.trim()) : [];
      const sizes = texts.map(px); const chip = d.querySelector(".chip");
      return { tpx, max: Math.max(...sizes), min: Math.min(...sizes), n: texts.length, chip: chip ? parseFloat(getComputedStyle(chip).fontSize) : null,
        dlgW: d.getBoundingClientRect().width };
    }, name);
    if (!r) { console.log(`RESULT ${name}_${w}_dialog_missing=1`); await ctx.close(); continue; }
    console.log(`# ${name} @${w}: dialog ${r.dlgW.toFixed(0)}px, title ${r.tpx.toFixed(2)}px, chip ${r.chip}px, svg text n=${r.n} min ${r.min.toFixed(2)} max ${r.max.toFixed(2)}px`);
    console.log(`RESULT ${name}_svg_text_max_px_${w}=${r.max.toFixed(2)} px`);
    console.log(`RESULT ${name}_svg_text_over_title_${w}=${(r.max / r.tpx).toFixed(3)} ratio`);
    await page.screenshot({ path: `${os.tmpdir()}/d4s3-m3-${name}-${w}-${perturb || "base"}.png` }); await ctx.close();
  }
}
await b.close();
const cpu = process.cpuUsage();
console.log(`RESULT thread_factor=1.00`); // no BLAS; counts and ratios only
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
console.log(`# perturb=${perturb || "none"} node_cpu_ms=${((cpu.user + cpu.system) / 1000).toFixed(0)}`);
