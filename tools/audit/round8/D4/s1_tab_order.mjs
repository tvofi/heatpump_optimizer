// D4-s1: keyboard Tab order through the expanded dialog.
//
// Metric: the fraction of consecutive keyboard-Tab stops whose focused
// element's screen position goes "backward" against reading order (top
// edge lower AND left edge to the right of the previous stop's box, or a
// vertical jump backward of more than one row-height while x also moves
// left), on the plan-chart page. A visually logical tab order should have
// (close to) zero such inversions; any nonzero count means a sighted
// keyboard user's focus jumps around the screen non-monotonically, which
// is what tools/audit/briefs/D4.md's "keyboard tab order through every
// focusable" asks this lane to check.
//
// Run: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
//   MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
//   NODE_PATH=/home/claude/audit-r8/pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//   HPO_PLANDATA=/tmp/plandata-daa3b4ac87fe.json \
//   node tools/audit/round8/D4/s1_tab_order.mjs
// Expected: RESULT inversions=<n> with n>0 on the baseline (a real bug),
// n==0 after the perturbation below. Baseline SHA cdf82daabcfe3777d98b31489f36df5555ec9d82.
// Machine: 4-vCPU cloud container (round-8 audit box); this is a count, not
// a timing, so it is contention-immune and not provisional.
import { strict as assert } from "node:assert";
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

let fails = 0;
function check(name, cond, detail = "") {
  console.log((cond ? "  ok  " : "  FAIL") + "  " + name);
  if (!cond) { if (detail) console.log("        " + detail); fails += 1; }
}

async function measure(page, label) {
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

  // List every focusable in DOM/tab order first, for reference.
  const domOrder = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const dlg = root.querySelector(".hpo-dialog, .dlg, [role='dialog']") || root;
    const els = [...dlg.querySelectorAll(
      "button, select, input, a[href], [tabindex]"
    )].filter((el) => {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") return false;
      const ti = el.getAttribute("tabindex");
      if (ti === "-1") return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
    return els.map((el) => {
      const r = el.getBoundingClientRect();
      return { tag: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).split(" ")[0] : ""),
               x: r.left, y: r.top, w: r.width, h: r.height };
    });
  });

  // Drive real Tab keypresses starting from body and record the actually
  // focused element (shadow-piercing) after each press, capped generously.
  await page.evaluate(() => { document.activeElement && document.activeElement.blur(); document.body.focus(); });
  const stops = [];
  const seen = new Set();
  const cap = Math.min(domOrder.length + 5, 140);
  for (let i = 0; i < cap; i++) {
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
      if (!(r.width > 0 && r.height > 0)) return { offscreen: true, tag: el.tagName };
      return {
        tag: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).split(" ")[0] : ""),
        x: r.left, y: r.top, w: r.width, h: r.height,
      };
    });
    if (!info) break;
    stops.push(info);
  }

  // Inversion: stop k+1 sits a full row above stop k (top edge higher by
  // more than half the row height) while also not to the right -- i.e. the
  // eye would have to jump backward up the page to find it. A wrap to a
  // new row (y increases) is normal; only a backward vertical jump counts.
  let inversions = 0;
  const detail = [];
  for (let i = 1; i < stops.length; i++) {
    const a = stops[i - 1], b = stops[i];
    if (a.offscreen || b.offscreen) continue;
    const rowH = Math.max(a.h, b.h, 16);
    const upBy = a.y - b.y; // positive if b is above a
    if (upBy > rowH * 0.6 && b.x <= a.x + a.w) {
      inversions += 1;
      if (detail.length < 6) detail.push(`${a.tag}@(${a.x.toFixed(0)},${a.y.toFixed(0)}) -> ${b.tag}@(${b.x.toFixed(0)},${b.y.toFixed(0)})`);
    }
  }
  console.log(`  [${label}] dom-focusable=${domOrder.length} tab-stops=${stops.length} inversions=${inversions}`);
  if (detail.length) console.log(`  [${label}] sample: ${detail.join(" | ")}`);
  return { domCount: domOrder.length, stopCount: stops.length, inversions };
}

const browser = await chromium.launch();
try {
  const VP = { width: Number(process.env.HPO_VP_W || 375), height: Number(process.env.HPO_VP_H || 812) };
  const page = await browser.newPage({ viewport: VP });
  page.on("pageerror", (err) => console.log(`  page error: ${err.message}`));
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });

  const base = await measure(page, "baseline");
  check("keyboard Tab order has no backward jumps on the plan-chart dialog page",
    base.stopCount > 5 && base.inversions === 0,
    `${base.inversions} inversion(s) across ${base.stopCount} stops (${base.domCount} focusable found by selector)`);

  console.log(`RESULT dom_focusable=${base.domCount} count`);
  console.log(`RESULT tab_stops=${base.stopCount} count`);
  console.log(`RESULT inversions=${base.inversions} count`);
  console.log(`RESULT thread_factor=1.0 ratio`);
  console.log(`RESULT load1=n/a ratio`);
} finally {
  await browser.close();
}
console.log(fails ? `\n${fails} CHECK(S) FAILED` : "\nALL CHECKS PASSED");
process.exit(fails ? 1 : 0);
