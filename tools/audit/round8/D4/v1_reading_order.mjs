// D4-v1 verifier harness for D4-01 (independent metric, independent script).
//
// Metric: reading_order_violations = # of PAIRS (i, j) with i < j among the
// real-Chromium keyboard-Tab stops (in Tab order) such that stop j's top
// edge sits a full row-height or more ABOVE stop i's top edge (j.y < i.y -
// rowH), counted over ALL pairs, not only adjacent ones, and WITHOUT any
// x-position condition. This is a global "does the Tab sequence ever later
// visit something a sighted top-to-bottom reader already passed" check; the
// finder's `inversions` metric (s1_tab_order.mjs) instead counts only
// ADJACENT pairs and additionally requires the later stop not be to the
// right. Both measure the same underlying phenomenon (DOM/visual order
// mismatch in the expanded what-if dialog) from different angles.
//
// Run: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
//   MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
//   NODE_PATH=/home/claude/audit-r8/pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//   HPO_PLANDATA=<plan payload> HPO_VP_W=375 HPO_VP_H=812 \
//   node tools/audit/round8/D4/v1_reading_order.mjs
// Expected: RESULT reading_order_violations=<n> with n>0 on the baseline at
// all three required viewports (375x812, 768x1024, 1280x800), reproducing
// the finder's claim under an independently-authored metric. Baseline SHA
// cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud container
// (round-8 audit box); this is a count, not a timing, contention-immune.
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.join(__dirname, "..", "..", "..", "..");

const testsDir = path.join(repo, "tests");
const defaultPath = path.join(
  "/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`
);
let planPath = process.argv[2] || process.env.HPO_PLANDATA || defaultPath;
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found - run tests/plan_view.py first`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_plan_space_heating";
const DHW_ID = "sensor.heat_pump_optimizer_plan_dhw_heating";

const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));
const states = {
  [SOLAR_ID]: { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", friendly_name: "Solar Irradiance", plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: {
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now, friendly_name: "Space Heating Plan", plan_kind: "space" } },
  [DHW_ID]: { state: "4 slots planned", attributes: {
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now, friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
};

async function measure(page) {
  await page.evaluate(() => {
    if (customElements.get("ha-card")) return;
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:white;box-sizing:border-box;border-radius:12px;display:block;position:relative;}</style><slot></slot>";
      }
    });
  });
  await page.evaluate(async ([st]) => {
    document.body.innerHTML = "";
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
    card.hass = { states: st, language: "en" };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 60));
    card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 100));
  }, [states]);

  await page.evaluate(() => { document.activeElement && document.activeElement.blur(); document.body.focus(); });
  const stops = [];
  for (let i = 0; i < 140; i++) {
    await page.keyboard.press("Tab");
    const info = await page.evaluate(() => {
      function deepActive(root) {
        let el = root.activeElement;
        while (el && el.shadowRoot && el.shadowRoot.activeElement) el = el.shadowRoot.activeElement;
        return el;
      }
      const el = deepActive(document);
      if (!el || el === document.body) return null;
      const r = el.getBoundingClientRect();
      if (!(r.width > 0 && r.height > 0)) return null;
      return { tag: el.tagName.toLowerCase(), x: r.left, y: r.top, h: r.height };
    });
    if (!info) break;
    stops.push(info);
  }
  return stops;
}

const browser = await chromium.launch();
let violations = 0;
try {
  const VP = { width: Number(process.env.HPO_VP_W || 375), height: Number(process.env.HPO_VP_H || 812) };
  const page = await browser.newPage({ viewport: VP });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });

  const stops = await measure(page);
  const pairs = [];
  for (let i = 0; i < stops.length; i++) {
    for (let j = i + 1; j < stops.length; j++) {
      const rowH = Math.max(stops[i].h, stops[j].h, 16);
      if (stops[j].y < stops[i].y - rowH) {
        violations += 1;
        if (pairs.length < 6) pairs.push(`#${i}(${stops[i].tag}@y${stops[i].y.toFixed(0)}) -> #${j}(${stops[j].tag}@y${stops[j].y.toFixed(0)})`);
      }
    }
  }
  console.log(`tab-stops=${stops.length}`);
  if (pairs.length) console.log(`sample: ${pairs.join(" | ")}`);
  console.log(`RESULT reading_order_violations=${violations} count`);
  console.log(`RESULT tab_stops=${stops.length} count`);
  console.log(`RESULT thread_factor=1.0 ratio`);
  console.log(`RESULT load1=n/a ratio`);
} finally {
  await browser.close();
}
process.exit(0);
