// The real-browser layout lane (issue #96).
//
// card.mjs proves the card builds the right DOM against a hand-written
// stub whose getBoundingClientRect is a constant 900x400 -- so it cannot
// see anything about position, size or visibility. Three layout defects
// reached a user that way: the zoom-limited editing trap (v4.0.5),
// tooltip text overflowing its box (two causes: inherited nowrap plus a
// left-edge-only clamp), and legend chips 0.33px apart that read as one
// chip hiding three traces.
//
// This lane runs the real card in real Chromium and asserts geometry:
// boxes at coordinates, overlaps, contained edges, scroll vs client
// width. It consumes the same plan payload card.mjs does (run
// tests/plan_view.py first; this file resolves the same default).
//
// Own CI job, not a run.sh lane: it needs a browser the other lanes do
// not install, and it is excluded from the closures roster in
// tests/closure.py's NOT_A_TEST for exactly that reason -- the closures
// job would have to install Chromium to record it, which buys nothing:
// its dependency closure is the card source, the payload and itself.
import { strict as assert } from "node:assert";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

// createRequire, not a static import: the lane must resolve playwright
// from wherever the CI job or developer put it (a bare `import` would
// demand node_modules inside the repository, which this repo does not
// have and should not grow for one lane).
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.join(__dirname, "..");

// Same plan-payload resolution as tests/card.mjs: argv, HPO_PLANDATA,
// then the per-checkout default plan_view.py writes.
const testsDir = __dirname;
const defaultPath = path.join(
  "/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`
);
let planPath = process.argv[2] || process.env.HPO_PLANDATA || defaultPath;
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py first`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_space_heating_plan";
const DHW_ID = "sensor.heat_pump_optimizer_dhw_heating_plan";

let fails = 0;
function check(name, cond, detail = "") {
  console.log((cond ? "  ok  " : "  FAIL") + "  " + name);
  if (!cond) { if (detail) console.log("        " + detail); fails += 1; }
}

const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));

// The setup page's diagram payload: what `describe_setup` publishes for a
// two-zone, two-tank house with a throttling valve and a wood furnace --
// the same shape tests/card.mjs builds, so the editor hits are the ones a
// fully-configured install offers.
const TEMP_DOMAINS = ["sensor", "number", "input_number"];
const setupTopology = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [
    ["heat_pump", "buffer_tank"],
    ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"],
    ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"],
    ["heat_pump", "dhw_tank"],
  ],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature",
      place: "upper_zone", entity: "sensor.livingroom", domains: TEMP_DOMAINS },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature",
      place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
      place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
    { key: "wood_tank_top_entity", label: "Wood tank top",
      place: "wood_tank", entity: null, domains: TEMP_DOMAINS },
    { key: "outdoor_temp_entity", label: "Outdoor temperature",
      place: "outdoor", entity: "sensor.outside", domains: TEMP_DOMAINS },
    { key: "heat_pump_switch_entity", label: "Heat pump switch",
      place: "heat_pump", entity: null,
      domains: ["switch", "input_boolean", "climate"] },
  ],
};
const states = {
  [SOLAR_ID]: { state: "120", attributes: {
    forecast: solarForecast, source: "open_meteo", friendly_name: "Solar Irradiance",
    plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: {
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh,
    total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now,
    friendly_name: "Space Heating Plan", plan_kind: "space",
    setup_topology: setupTopology } },
  [DHW_ID]: { state: "4 slots planned", attributes: {
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh,
    total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now,
    friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
};

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1024, height: 800 } });
  page.on("pageerror", (err) => {
    console.log(`  page error: ${err.message}`);
  });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });

  // The card, on a dashboard-sized tile: the host gets the panel width
  // Home Assistant would give it and a sane font, so every measurement
  // below is of the card as a user sees it, not of a collapsed div.
  await page.evaluate(([st]) => {
    const style = document.createElement("style");
    style.textContent = `
      body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif; }
      heatpump-optimizer-card { display: block; width: 900px; min-height: 400px; }
    `;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    document.body.appendChild(card);
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st };
    window.__card = card;
  }, [states]);
  await page.waitForTimeout(200);

  // --- 1. The card really rendered, with real geometry --------------------
  // The largest svg in the shadow root, not the first: the card also
  // draws small inline icons as svg, and an 18x18 icon would make every
  // measurement below nonsense.
  const cardBox = await page.evaluate(() => {
    const card = window.__card;
    const svgs = card.shadowRoot ? [...card.shadowRoot.querySelectorAll("svg")] : [];
    let best = null;
    for (const svg of svgs) {
      const b = svg.getBoundingClientRect();
      if (!best || b.width * b.height > best.w * best.h) {
        best = { w: b.width, h: b.height, left: b.left, top: b.top };
      }
    }
    return best ? { ...best, cardW: card.getBoundingClientRect().width } : null;
  });
  check("the card renders an svg with real size on a dashboard tile",
    cardBox !== null && cardBox.w > 600 && cardBox.h > 200,
    cardBox ? `${cardBox.w.toFixed(0)}x${cardBox.h.toFixed(0)} px` : "no svg");

  // --- 2. Legend chips: distinct, not stacked into one --------------------
  // The shipped defect: three chips 0.33px apart on a 65k axis read as
  // one chip and hid three traces at once. Chips must be pairwise
  // separated by a visible gap, and every chip label must fit its box.
  const chips = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    return [...root.querySelectorAll(".legend-chip, .chip")].map((el) => {
      const b = el.getBoundingClientRect();
      return { x: b.x, y: b.y, w: b.width, h: b.height,
               text: (el.textContent || "").trim(),
               overflow: el.scrollWidth > el.clientWidth + 1 };
    });
  });
  check("legend chips exist for the rendered traces", chips.length >= 2,
    `${chips.length} chip(s): ${chips.map((c) => c.text).join(" | ")}`);
  let overlapPairs = [];
  for (let i = 0; i < chips.length; i++) {
    for (let j = i + 1; j < chips.length; j++) {
      const a = chips[i], b = chips[j];
      const gapX = Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w));
      const gapY = Math.max(a.y - (b.y + b.h), b.y - (a.y + a.h));
      if (gapX < 2 && gapY < 2) overlapPairs.push(`${a.text}~${b.text} (${gapX.toFixed(2)}px apart)`);
    }
  }
  check("no two legend chips overlap or nearly touch", overlapPairs.length === 0,
    overlapPairs.slice(0, 4).join("; "));
  check("every legend chip's label fits inside it",
    chips.every((c) => !c.overflow && c.w > 4 && c.h > 8),
    chips.filter((c) => c.overflow).map((c) => c.text).join("; "));

  // --- 3. The tooltip: contained on BOTH edges, text inside its box ------
  // Hover across the whole chart width -- including the far left and far
  // right, where the two shipped causes lived: a clamp on the left edge
  // only, and inherited white-space:nowrap that made max-width inert
  // (scrollWidth > clientWidth). The exercised count guards against the
  // vacuous pass: a lane where no tooltip ever appeared must not report
  // "stays inside" about nothing.
  if (cardBox) {
    const contained = [];
    const overflows = [];
    let measured = 0;
    for (let frac of [0.02, 0.25, 0.5, 0.75, 0.98]) {
      const x = cardBox.left + cardBox.w * frac;
      const y = cardBox.top + cardBox.h * 0.35;
      await page.mouse.move(x, y);
      await page.waitForTimeout(120);
      const m = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const tt = root && root.querySelector(".tooltip");
        if (!tt || !tt.textContent.trim()) return null;
        const card = window.__card.getBoundingClientRect();
        const b = tt.getBoundingClientRect();
        return {
          left: b.left - card.left, right: card.right - b.right,
          top: b.top - card.top, bottom: card.bottom - b.bottom,
          textFits: tt.scrollWidth <= tt.clientWidth + 1,
          w: b.width, h: b.height,
        };
      });
      if (!m) continue;
      measured += 1;
      if (m.left < -0.5 || m.right < -0.5 || m.top < -0.5 || m.bottom < -0.5) {
        contained.push(`x=${frac}: edges L${m.left.toFixed(0)} R${m.right.toFixed(0)}`);
      }
      if (!m.textFits) overflows.push(`x=${frac}`);
    }
    check("hovering the chart actually shows tooltips (the lane is not vacuous)",
      measured >= 2, `${measured}/5 hover positions produced a tooltip`);
    check("the tooltip stays inside the card on both edges, everywhere hovered",
      measured >= 2 && contained.length === 0, contained.join("; "));
    check("and its text fits its box (no inherited-nowrap overflow)",
      measured >= 2 && overflows.length === 0, overflows.join("; "));
  }

  // --- 4. The setup editor: hit targets a pointer can actually hit -------
  // The zoom-limited editing trap (v4.0.5): at real rendered sizes the
  // draggable hit rects must be big enough to click, and inside the svg
  // they belong to.
  const setup = await page.evaluate(() => {
    const card = window.__card;
    // Open the dialog first, exactly as card.mjs does: the setup page
    // renders inside it, and setting _dialogPage alone leaves the dialog
    // closed and the svg absent.
    card._onCardClick({});
    card._dialogPage = "setup";
    card._render();
    const svg = card.shadowRoot && card.shadowRoot.querySelector("svg.setup-svg");
    if (!svg) return null;
    const sb = svg.getBoundingClientRect();
    const hits = [...svg.querySelectorAll("rect.setup-hit")].map((r) => {
      const b = r.getBoundingClientRect();
      return { w: b.width, h: b.height,
               inside: b.left >= sb.left - 0.5 && b.right <= sb.right + 0.5
                     && b.top >= sb.top - 0.5 && b.bottom <= sb.bottom + 0.5,
               key: r.getAttribute("data-key") || "" };
    });
    return { hits, svgW: sb.width, svgH: sb.height };
  });
  check("the setup page renders its svg", setup !== null && setup.svgW > 300,
    setup ? `${setup.svgW.toFixed(0)}x${setup.svgH.toFixed(0)} px` : "no setup svg");
  if (setup) {
    const tiny = setup.hits.filter((h) => h.w < 8 || h.h < 8);
    const outside = setup.hits.filter((h) => !h.inside);
    check("every setup hit target is at least 8x8 px at real size",
      setup.hits.length > 0 && tiny.length === 0,
      `${setup.hits.length} hit(s); tiny: ${tiny.map((h) => `${h.key}:${h.w.toFixed(1)}x${h.h.toFixed(1)}`).join(", ")}`);
    check("and every hit target sits inside the setup svg",
      outside.length === 0,
      outside.map((h) => h.key).join(", "));
  }
} finally {
  await browser.close();
}

console.log(fails ? `\n${fails} BROWSER CHECK(S) FAILED` : "\nALL BROWSER CHECKS PASSED");
process.exit(fails ? 1 : 0);
