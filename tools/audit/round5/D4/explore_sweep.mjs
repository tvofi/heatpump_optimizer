// EXPLORER (D4 round 5): mount the card in real Chromium across states,
// viewports, themes and languages; report SVG text collisions, HTML text
// overflow, out-of-box text, and console errors. Throwaway: the finding
// harnesses are the ones under tools/audit/round5/D4/.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../.."); // export root

const planPath = process.env.HPO_PLANDATA;
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_space_heating_plan";
const DHW_ID = "sensor.heat_pump_optimizer_dhw_heating_plan";

const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));

const setupTopology = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [
    ["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"],
  ],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.livingroom", domains: ["sensor","number","input_number"] },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone", entity: null, domains: ["sensor","number","input_number"] },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank", entity: "sensor.tank", domains: ["sensor","number","input_number"] },
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: ["sensor","number","input_number"] },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor", entity: "sensor.outside", domains: ["sensor","number","input_number"] },
    { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump", entity: null, domains: ["switch","input_boolean","climate"] },
    { key: "solar_radiation_entity", label: "Solar radiation", place: "outdoor", entity: null, domains: ["sensor"] },
  ],
};

const baseStates = () => ({
  [SOLAR_ID]: { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", friendly_name: "Solar Irradiance", plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: {
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now, friendly_name: "Space Heating Plan", plan_kind: "space",
    setup_topology: setupTopology,
    solar_radiation_entity: "sensor.solar_rad", weather_entity: "weather.home",
    dhw_windows: "06:00-08:30, 17:00-22:00",
    day_start_hour: 7, day_end_hour: 22 } },
  [DHW_ID]: { state: "4 slots planned", attributes: {
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now, friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
});

const SCENARIOS = {
  plan:            { cfg: {}, drive: "" },
  plan_whatif:     { cfg: { what_if: true }, drive: "" },
  expanded:        { cfg: {}, drive: "window.__card._onCardClick({});" },
  expanded_whatif: { cfg: { what_if: true }, drive: "window.__card._onCardClick({});" },
  setup:           { cfg: {}, drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render();" },
  no_plan:         { cfg: {}, drive: "", empty: true },
};

const THEMES = {
  light: "--primary-text-color:#212121;--secondary-text-color:#727272;--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#fff;--divider-color:rgba(0,0,0,.12);",
  dark:  "--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);",
};
const VIEWPORTS = { phone: { width: 375, height: 812 }, tablet: { width: 768, height: 1024 }, desktop: { width: 1280, height: 800 } };

const COLLECT = () => {
  const root = window.__card.shadowRoot;
  const out = { svgOverlaps: [], htmlOverflow: [], outOfBox: [] };
  for (const svg of root.querySelectorAll("svg")) {
    const texts = [...svg.querySelectorAll("text")].filter((t) => (t.textContent || "").trim().length);
    const boxes = texts.map((t) => {
      let b; try { b = t.getBBox(); } catch (e) { b = { x: 0, y: 0, width: 0, height: 0 }; }
      return { t, x: b.x, y: b.y, w: b.width, h: b.height, s: (t.textContent || "").trim() };
    });
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.t.parentNode === b.t.parentNode && a.t.nextElementSibling === b.t) continue;
        const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
        const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (ox > 1.5 && oy > 1.5) {
          out.svgOverlaps.push({ a: a.s.slice(0, 28), b: b.s.slice(0, 28), ox: +ox.toFixed(2), oy: +oy.toFixed(2) });
        }
      }
    }
    const vb = (svg.getAttribute("viewBox") || "").split(/\s+/).map(Number);
    if (vb.length === 4) {
      for (const bx of boxes) {
        if (bx.x < vb[0] - 1 || bx.x + bx.w > vb[0] + vb[2] + 1) {
          out.outOfBox.push({ s: bx.s.slice(0, 28), x: +bx.x.toFixed(1), r: +(bx.x + bx.w).toFixed(1), vbw: vb[2] });
        }
      }
    }
  }
  for (const el of root.querySelectorAll("*")) {
    const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!hasText) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    if (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0) {
      out.htmlOverflow.push({ cls: String(el.getAttribute("class")), tag: el.tagName, sw: el.scrollWidth, cw: el.clientWidth, ovx: cs.overflowX, s: (el.textContent || "").trim().slice(0, 40) });
    }
  }
  return out;
};

const browser = await chromium.launch();
const results = [];
try {
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    for (const [thName, theme] of Object.entries(THEMES)) {
      for (const lang of ["en", "sv-SE"]) {
        for (const [scName, sc] of Object.entries(SCENARIOS)) {
          const page = await browser.newPage({ viewport: vp });
          const errs = [];
          page.on("pageerror", (e) => errs.push(e.message));
          page.on("console", (m) => { if (m.type() === "error") errs.push("console: " + m.text()); });
          await page.goto("about:blank");
          await page.addScriptTag({ path: CARD_SRC });
          await page.evaluate(async ([st, themeCss, cfg, drive, empty, lang]) => {
            if (!customElements.get("ha-card")) {
              customElements.define("ha-card", class extends HTMLElement {
                constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML =
                  "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>"; }
              });
            }
            document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
            document.body.innerHTML = "";
            const style = document.createElement("style");
            style.className = "hpo-test";
            style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:100%;${themeCss}}`;
            document.head.appendChild(style);
            const card = document.createElement("heatpump-optimizer-card");
            card.setConfig(Object.assign({ type: "custom:heatpump-optimizer-card" }, cfg));
            card.hass = { states: empty ? {} : st, language: lang };
            document.body.appendChild(card);
            window.__card = card;
            await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
            await new Promise((r) => setTimeout(r, 60));
            if (drive) eval(drive);
            await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
            await new Promise((r) => setTimeout(r, 60));
          }, [baseStates(), theme, sc.cfg, sc.drive, !!sc.empty, lang]);
          let res = null;
          try { res = await page.evaluate(COLLECT); } catch (e) { res = { err: String(e) }; }
          results.push({ vp: vpName, theme: thName, lang, sc: scName, errs, res });
          await page.close();
        }
      }
    }
  }
} finally { await browser.close(); }

for (const r of results) {
  const o = r.res.svgOverlaps.length, h = r.res.htmlOverflow.length, b = r.res.outOfBox.length, e = r.errs.length;
  if (o || h || b || e) {
    console.log(`--- ${r.sc} ${r.vp} ${r.theme} ${r.lang}: overlaps=${o} htmlOverflow=${h} outOfBox=${b} errors=${e}`);
    for (const x of r.res.svgOverlaps.slice(0, 5)) console.log(`    OV "${x.a}" ~ "${x.b}" ox=${x.ox} oy=${x.oy}`);
    for (const x of r.res.htmlOverflow.slice(0, 5)) console.log(`    HO .${x.cls} sw=${x.sw} cw=${x.cw} ovx=${x.ovx} "${x.s}"`);
    for (const x of r.res.outOfBox.slice(0, 5)) console.log(`    OB "${x.s}" x=${x.x} r=${x.r} vbw=${x.vbw}`);
    for (const x of r.errs.slice(0, 5)) console.log(`    ER ${x}`);
  }
}
console.log(`scenarios run: ${results.length}`);
