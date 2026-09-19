// D4 round 5 -- the setup diagram's click-to-assign rows against WCAG 2.2
// SC 2.5.8's 24 CSS px target minimum under a FINE pointer.
//
// METRIC (one line): the count of `rect.setup-hit` elements in the setup page
// whose rendered height, in CSS px, is below 24 (fine pointer) or below 44
// (coarse pointer) -- measured with getBoundingClientRect in a real Chromium
// at 375, 768 and 1280 CSS px wide, plus the smallest such height.
//
// COMMAND (from the repository root):
//   NODE_PATH=$PWD/.scratch-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=$PWD/.plandata.json \
//   node tools/audit/round5/D4/setup_row_target.mjs
// (HPO_PLANDATA comes from `HPO_PLANDATA=... PYTHONPATH=tests/hastub python3
//  tests/plan_view.py`.)
//
// EXPECTED: baseline, fine pointer, 375 + 768 -> 10 under (all five rows at
// 11.67 px and 14.57 px); at 1280 -> 0 (24.80 px). Coarse pointer -> 0 under
// the 44 px bar at every width (88.99 px and up): the coarse branch works.
// After the perturbation -> 0 at every width and pointer. Tolerance: exact to
// 0.01 px (no timing, no load sensitivity).
//
// BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
// MACHINE: 8-core Apple M1, 8 GB, macOS (Darwin 25.6.0); Chromium via
// Playwright 1.49.0.
//
// The instrumented symbol is heatpump-optimizer-card.js:setupSvgHtml -- the
// line that picks a row's hit height:
//
//   const hitH = _coarsePointer()
//     ? Math.max(hitBase, _targetMinPx() * (SETUP_W / 280))
//     : hitBase;
//
// The every-pointer floor the card documents 700 lines away ("SC 2.5.8's
// 24 px target minimum is owed to every pointer, not only to touch") is
// applied only on the coarse branch here, so under a mouse the height is a
// bare `rowH - 2` = 15 viewBox units, and a viewBox unit is not a pixel: at
// the 560 px minimum the setup canvas renders at (its CSS `min-width`), 15
// units come out 11.67 px. The perturbation un-gates that floor so it
// applies to every pointer, which is the one-line edit a reviewer would
// reach for.
//
// The perturbation is deliberately the NAIVE fix, and the harness measures
// its side effect too: the coarse branch's `SETUP_W / 280` factor assumes the
// diagram renders 280 px wide, but the shipped CSS renders it 560-1190 px, so
// un-gating multiplies 44.5 units by 2.571 and lands 89-189 px tall -- rows
// that swallow their neighbours. Both numbers are reported; only the
// under-floor count is the expected-direction claim.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");

const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const FINE_FLOOR = 24, COARSE_FLOOR = 44;
const ANCHOR = `const hitH = _coarsePointer()
        ? Math.max(hitBase, _targetMinPx() * (SETUP_W / 280))
        : hitBase;`;
const baselineSrc = readFileSync(CARD_SRC, "utf8");
if (baselineSrc.split(ANCHOR).length - 1 !== 1) {
  throw new Error("anchor for the hitH edit is not unique");
}
const perturbedSrc = baselineSrc.replace(
  ANCHOR,
  "const hitH = Math.max(hitBase, _targetMinPx() * (SETUP_W / 280));"
);

const payload = process.env.HPO_PLANDATA;
if (!payload) throw new Error("set HPO_PLANDATA (tests/plan_view.py writes it)");
const plan = JSON.parse(readFileSync(payload, "utf8"));
const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));
const topo = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"]],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.livingroom", domains: ["sensor"] },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank", entity: "sensor.tank", domains: ["sensor"] },
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: ["sensor"] },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor", entity: "sensor.outside", domains: ["sensor"] },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone", entity: null, domains: ["sensor"] },
  ],
};
const states = {
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo, day_start_hour: 7, day_end_hour: 22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: {} },
  "sensor.tank": { state: "47.5", attributes: {} },
  "sensor.outside": { state: "unavailable", attributes: {} },
};

const MEASURE = (fineFloor, coarseFloor) => {
  const root = window.__card.shadowRoot;
  const pts = [...root.querySelectorAll("rect.setup-hit")].map((r) => {
    const b = r.getBoundingClientRect();
    return { key: r.dataset.key, x: +b.left.toFixed(1), top: +b.top.toFixed(2), h: +b.height.toFixed(2) };
  });
  // Worst same-column overlap between adjacent rows: the amount by which a
  // row's box reaches into the next row's nominal pitch.
  let worstOverlap = 0;
  const cols = new Map();
  for (const p of pts) { if (!cols.has(p.x)) cols.set(p.x, []); cols.get(p.x).push(p); }
  for (const rows of cols.values()) {
    rows.sort((a, b) => a.top - b.top);
    for (let i = 1; i < rows.length; i++) {
      worstOverlap = Math.max(worstOverlap, (rows[i - 1].top + rows[i - 1].h) - rows[i].top);
    }
  }
  return {
    n: pts.length,
    minH: pts.length ? +Math.min(...pts.map((p) => p.h)).toFixed(2) : null,
    maxH: pts.length ? +Math.max(...pts.map((p) => p.h)).toFixed(2) : null,
    underFine: pts.filter((p) => p.h < fineFloor - 0.05).length,
    underCoarse: pts.filter((p) => p.h < coarseFloor - 0.05).length,
    worstOverlap: +worstOverlap.toFixed(2),
  };
};

const BROWSER = await chromium.launch();
async function run(src, width, coarse) {
  const ctx = await BROWSER.newContext({ viewport: { width, height: 900 } });
  const page = await ctx.newPage();
  await page.goto("about:blank");
  if (coarse) {
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "pointer", value: "coarse" }] });
  }
  await page.addScriptTag({ content: src });
  await page.evaluate(async ([st, coarseFlag]) => {
    if (coarseFlag) {
      const orig = window.matchMedia.bind(window);
      window.matchMedia = (q) => (q === "(pointer: coarse)"
        ? { matches: true, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }
        : orig(q));
    }
    if (!customElements.get("ha-card")) {
      customElements.define("ha-card", class extends HTMLElement {
        constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{background:var(--card-background-color,white);display:block}</style><slot></slot>"; }
      });
    }
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: "en" };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => setTimeout(r, 150));
    card._onCardClick({});
    card.dialog.page = "setup";
    card._render();
    await new Promise((r) => setTimeout(r, 150));
  }, [states, coarse]);
  const m = await page.evaluate(`(${MEASURE.toString()})(${FINE_FLOOR},${COARSE_FLOOR})`);
  await ctx.close();
  return m;
}

const WIDTHS = [375, 768, 1280];
const base = {}, pert = {};
for (const w of WIDTHS) {
  base[`${w}f`] = await run(baselineSrc, w, false);
  pert[`${w}f`] = await run(perturbedSrc, w, false);
  base[`${w}c`] = await run(baselineSrc, w, true);
}
await BROWSER.close();

for (const k of Object.keys(base)) {
  const m = base[k];
  console.log(`baseline ${k}: n=${m.n} minH=${m.minH} maxH=${m.maxH} under24=${m.underFine} under44=${m.underCoarse} worstOverlap=${m.worstOverlap}`);
}

const fineBase = WIDTHS.reduce((a, w) => a + base[`${w}f`].underFine, 0);
const finePert = WIDTHS.reduce((a, w) => a + pert[`${w}f`].underFine, 0);
const coarseBase = WIDTHS.reduce((a, w) => a + base[`${w}c`].underCoarse, 0);
console.log("");
console.log(`RESULT setup_row_under_24_fine_baseline=${fineBase} count`);
console.log(`RESULT setup_row_under_24_fine_perturbed=${finePert} count`);
console.log(`RESULT setup_row_under_44_coarse_baseline=${coarseBase} count`);
console.log(`RESULT setup_row_height_375_fine_baseline=${base["375f"].minH} px`);
console.log(`RESULT setup_row_height_375_fine_perturbed=${pert["375f"].minH} px`);
console.log(`RESULT setup_row_height_768_fine_baseline=${base["768f"].minH} px`);
console.log(`RESULT setup_row_height_1280_fine_baseline=${base["1280f"].minH} px`);
console.log(`RESULT setup_row_height_375_coarse_baseline=${base["375c"].minH} px`);
// The naive fix's side effect, reported so a reviewer sees it.
console.log(`RESULT setup_row_worst_overlap_375_fine_perturbed=${pert["375f"].worstOverlap} px`);
console.log(`RESULT setup_row_worst_overlap_375_coarse_baseline=${base["375c"].worstOverlap} px`);

let load1 = 0;
try { load1 = +os.loadavg()[0].toFixed(2); } catch { /* no loadavg here */ }
let swapins = -1;
try {
  const m = execSync("vm_stat", { encoding: "utf8" }).match(/Swapins:\s+(\d+)/);
  if (m) swapins = Number.parseInt(m[1], 10);
} catch { swapins = -1; }
console.log("RESULT thread_factor=1.000 ratio   # Chromium geometry only; no BLAS in this process");
console.log(`RESULT load1=${load1} load`);
console.log(`RESULT swapins=${swapins} count`);

const ok = fineBase === 10 && finePert === 0 && coarseBase === 0;
console.log(ok ? "SELF-CHECK ok" : `SELF-CHECK FAIL (fineBase=${fineBase} finePert=${finePert} coarseBase=${coarseBase})`);
if (!ok) process.exitCode = 1;
