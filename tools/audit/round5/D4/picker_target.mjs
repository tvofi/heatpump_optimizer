// D4 round 5 -- the entity picker's text and filter controls against WCAG 2.2
// SC 2.5.8's 24 CSS px target minimum.
//
// METRIC (one line): the number of HTML form controls inside the setup
// dialog's entity picker (input/select/textarea/button) whose smaller
// rendered side, in CSS px, is below 24 -- measured with
// getBoundingClientRect in a real Chromium at 375, 768 and 1280 CSS px wide.
// SVG-drawn targets (rect.setup-hit) are excluded here: they are the subject
// of setup_row_target.mjs, and mixing them would hide this one behind theirs.
//
// COMMAND (from the repository root):
//   NODE_PATH=$PWD/.scratch-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=$PWD/.plandata.json \
//   node tools/audit/round5/D4/picker_target.mjs
// (HPO_PLANDATA comes from `HPO_PLANDATA=... PYTHONPATH=tests/hastub python3
//  tests/plan_view.py`.)
//
// EXPECTED: baseline >= 1 control under the floor, all of them the picker's
// own text field(s) at 23.19 px; after the perturbation 0. Tolerance: the
// pixel figures are exact to 0.01 px (no timing, no load sensitivity).
//
// BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
// MACHINE: 8-core Apple M1, 8 GB, macOS (Darwin 25.6.0); Chromium via
// Playwright 1.49.0.
//
// The instrumented symbol is heatpump-optimizer-card.js's `htmlTargetFloor`
// template literal: the every-pointer 24 px floor, which the card's own
// comment says "is owed to every pointer, not only to touch". Its selector
// list floors `.sp-actions button` -- the picker's own Save and Cancel --
// but not `.sp-filter`/`.sp-select`, the field and list that sit directly
// above them in the same component. The perturbation is the one-line
// production edit of adding them to that list.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");

const CARD_REL = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
const CARD_SRC = path.join(repo, CARD_REL);
const FLOOR_PX = 24;
const ANCHOR = ".expand, .close, .viewctl button, .chip, .dlg-tab,";

const baselineSrc = readFileSync(CARD_SRC, "utf8");
if (baselineSrc.split(ANCHOR).length - 1 !== 1) {
  throw new Error("anchor for the htmlTargetFloor edit is not unique");
}
// The perturbation: add the picker's own controls to the every-pointer floor.
const perturbedSrc = baselineSrc.replace(
  ANCHOR,
  `${ANCHOR}\n        .sp-filter, .sp-select,`
);

// Payload (private to this harness's temp dir).
const tmp = mkdtempSync(path.join(os.tmpdir(), "d4-picker-"));
const payload = process.env.HPO_PLANDATA;
if (!payload) throw new Error("set HPO_PLANDATA (tests/plan_view.py writes it)");
const plan = JSON.parse(readFileSync(payload, "utf8"));
writeFileSync(path.join(tmp, "plandata.json"), JSON.stringify(plan));

const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
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
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: ["sensor"] },
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

const MEASURE = (floor) => {
  const root = window.__card.shadowRoot;
  const SEL = "button, input, select, textarea";
  const out = [];
  const seen = new Set();
  for (const el of root.querySelectorAll(SEL)) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || el.disabled) continue;
    if (el.getClientRects().length === 0) continue;
    const b = el.getBoundingClientRect();
    if (b.width <= 0 || b.height <= 0) continue;
    const cls = String(el.getAttribute("class") || "");
    const key = `${el.tagName}.${cls}@${Math.round(b.left)},${Math.round(b.top)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const min = Math.min(b.width, b.height);
    out.push({ tag: el.tagName, cls, w: +b.width.toFixed(2), h: +b.height.toFixed(2),
      min: +min.toFixed(2), under: min < floor - 0.05 });
  }
  const picker = root.querySelector(".setup-picker");
  const filt = root.querySelector("input.sp-filter");
  const sel = root.querySelector("select.sp-select");
  return {
    n: out.length,
    under: out.filter((c) => c.under),
    filterH: filt ? +filt.getBoundingClientRect().height.toFixed(2) : null,
    selectH: sel ? +sel.getBoundingClientRect().height.toFixed(2) : null,
    saveH: picker ? +picker.querySelector(".sp-save").getBoundingClientRect().height.toFixed(2) : null,
    picker: !!picker,
  };
};

const BROWSER = await chromium.launch();
async function run(src, width) {
  const ctx = await BROWSER.newContext({ viewport: { width, height: 900 } });
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.addScriptTag({ content: src });
  await page.evaluate(async ([st]) => {
    if (!customElements.get("ha-card")) {
      customElements.define("ha-card", class extends HTMLElement {
        constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{background:var(--card-background-color,white);display:block}</style><slot></slot>"; }
      });
    }
    const style = document.createElement("style");
    style.textContent = ":root{" + "--primary-text-color:#212121;--secondary-text-color:#727272;--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#fff;--divider-color:rgba(0,0,0,.12)}";
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: "en" };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => setTimeout(r, 120));
    // Open the setup page, then open the picker on the one unassigned slot.
    card._onCardClick({});
    card.dialog.page = "setup";
    card._render();
    await new Promise((r) => setTimeout(r, 120));
    const hit = [...card.shadowRoot.querySelectorAll(".setup-hit")]
      .find((x) => x.dataset.key === "wood_tank_top_entity");
    if (hit) hit.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    card._render();
    await new Promise((r) => setTimeout(r, 150));
  }, [states]);
  const m = await page.evaluate(`(${MEASURE.toString()})(${FLOOR_PX})`);
  await ctx.close();
  return m;
}

const WIDTHS = [375, 768, 1280];
const base = {}, pert = {};
for (const w of WIDTHS) base[w] = await run(baselineSrc, w);
for (const w of WIDTHS) pert[w] = await run(perturbedSrc, w);
await BROWSER.close();

for (const w of WIDTHS) {
  const m = base[w];
  if (!m.picker) throw new Error(`picker did not open at width ${w}`);
  console.log(`baseline ${w}: controls=${m.n} under=${m.under.length}/${m.n} ` +
    `filterH=${m.filterH} selectH=${m.selectH} saveH=${m.saveH}`);
  for (const u of m.under) console.log(`    under: ${u.tag}.${u.cls} ${u.w}x${u.h} min=${u.min}`);
}

const underBase = WIDTHS.reduce((a, w) => a + base[w].under.length, 0);
const underPert = WIDTHS.reduce((a, w) => a + pert[w].under.length, 0);
console.log("");
console.log(`RESULT picker_under_floor_baseline=${underBase} count`);
console.log(`RESULT picker_under_floor_perturbed=${underPert} count`);
for (const w of WIDTHS) {
  console.log(`RESULT sp_filter_height_${w}_baseline=${base[w].filterH} px`);
  console.log(`RESULT sp_filter_height_${w}_perturbed=${pert[w].filterH} px`);
}
console.log(`RESULT sp_select_height_baseline=${base[375].selectH} px`);
console.log(`RESULT sp_save_height_control=${base[375].saveH} px`);

let load1 = 0;
try { load1 = +os.loadavg()[0].toFixed(2); } catch { /* no loadavg here */ }
// Swapins: macOS counts them in `vm_stat`'s "Swapins" line; -1 when the
// platform reports nothing (the field is quoted, not gated).
let swapins = -1;
try {
  const m = execSync("vm_stat", { encoding: "utf8" }).match(/Swapins:\s+(\d+)/);
  if (m) swapins = Number.parseInt(m[1], 10);
} catch { swapins = -1; }
console.log("RESULT thread_factor=1.000 ratio   # Chromium geometry only; no BLAS in this process");
console.log(`RESULT load1=${load1} load`);
console.log(`RESULT swapins=${swapins} count`);

const ok = underBase >= 1 && underPert === 0 &&
  base[375].filterH < FLOOR_PX && pert[375].filterH >= FLOOR_PX;
console.log(ok ? "SELF-CHECK ok" : "SELF-CHECK FAIL");
if (!ok) process.exitCode = 1;
