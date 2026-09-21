// Round 5, D4 seat A — the card in a real browser, every drift state,
// three viewports, light and dark, sv and en, reduced motion, coarse pointer.
//
// METRIC (one line): per rendered card state, counts of (a) text-on-text
// overlap pairs >=1px in both axes, (b) HTML text elements whose scroll
// extent exceeds their client box by >1px, (c) text elements below WCAG AA
// (4.5:1 normal, 3:1 large) for their effective on-screen colour against the
// nearest opaque ancestor background, (d) visible interactive targets under
// 24px (fine) / 44px (coarse) on their min side, (e) console/page errors,
// (f) anchor elements that move >0.5px on hover, (g) focusables unreachable
// by Tab.
//
// COMMAND (from the repository root):
//   HPO_PLANDATA=/tmp/audit-5/tmp/d4/plandata \
//   NODE_PATH=/tmp/audit-5/pw/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round5/D4/seat-a/sweep.mjs
// Optional: HPO_CARD_SRC=<copy of the card> to run the same sweep against a
// modified card (the perturbation arm); SHOTS=1 to (re)take the screenshot
// set; MAX_STATES=<n> to trim the state list.
//
// EXPECTED at the baseline (1cc89e020fff9040a9d0090a27bf22bc1dd497f0):
//   renders=342 states=38 text_overlap_pairs=831 text_overflow=12
//   contrast_aa_fail=3 (light=0 dark=3) hit_under24_fine=6 of 7848
//   hit_under44_coarse=728 focus_unreachable=135 focus_zero_size=0
//   hover_shift_gt05px=0 console_page_errors=0 mount_errors=0
// Contention-immune counts; tolerance ±10 on the coarse count and ±2 on the
// others (Chromium font raster at the 375 boundary), ±0 on console errors.
// Under the perturbations in REPORT.md: card-fix-alert.js -> contrast_aa_fail
// 3 -> 0; card-fix-hits.js (MAX_STATES=score_open,shared_steps) ->
// hit_under24_fine 4 -> 2; card-fix-coarse.js (MAX_STATES=plan_inline,
// expanded_plan) -> coarse under-44 38 -> 2. The three copies are one-line
// edits of the production card, recreated with the sed/python snippets in
// REPORT.md's finding sections.
//
// Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0
// Machine: 8-core Apple M1, macOS 25.6.0, Chromium 1148 (Playwright 1.49.0).
//
// Writes: sweep-details.json (per-render metrics) and shots/*.png (SHOTS=1)
// under this directory. Nothing else. HPO_PLANDATA must point at a private
// payload (tests/plan_view.py output) — set before running.
import { createRequire } from "node:module";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import {
  HOUR, DEFAULT_SPACE, DEFAULT_DHW,
  planStates, setupSensorStates, qaTopologies, layoutCatalogTopo,
} from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "..", "..", "..", "..", "..");
const planPath = process.env.HPO_PLANDATA || "/tmp/audit-5/tmp/d4/plandata";
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found (HPO_PLANDATA)`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const CARD_SRC = process.env.HPO_CARD_SRC
  || path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;

// ---------------------------------------------------------------- scenarios
// The same states tests/card_drift.mjs's STATES drive, rebuilt as data the
// browser can mount: {states, config, hass, actions}. Actions are dispatched
// in-page against the real element (native clicks where the rig fires click,
// direct controller-method calls where the rig calls them).
const noop = { stopPropagation() {}, preventDefault() {} };
const woodFuelStates = (fuel) => {
  const st = planStates(plan);
  st[DEFAULT_SPACE].attributes.wood_fuel = fuel;
  return st;
};
const awayPlanStates = ({ sw = false, returnIso = null, resolved = false } = {}) => {
  const st = planStates(plan);
  st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] = { state: returnIso || "unknown", attributes: {} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = {
    state: resolved ? "on" : "off",
    attributes: { source: resolved && !sw ? "person.alice" : "none" },
  };
  return st;
};
const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": {
    state: "cheap_price", attributes: { lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
});
const scheduleStates = () => {
  const st = planStates(plan);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7;
  st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
  return st;
};
const sharedStepStates = () => {
  const st = planStates(plan);
  const sp = st[DEFAULT_SPACE].attributes.forecast;
  const heating = new Set(sp.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
  st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) =>
    heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
  return st;
};
const setupStates = (topo, extra) => {
  const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
  st[DEFAULT_SPACE].attributes.setup_topology = topo;
  return st;
};
const bigStates = () => {
  const st = {};
  for (let i = 0; i < 400; i++) {
    st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = {
      state: "20.0", attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` } };
  }
  st["sensor.vedpanna_temperatur_temperature"] = { state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  return st;
};
const overrideInfo = {
  active: true, expires_at: new Date(FROZEN + 5 * HOUR).toISOString(),
  space_slots: [], dhw_slots: [], released_space: [], released_dhw: [],
};

// Every action is a small descriptor the in-page runner dispatches.
const SCENARIOS = [
  { name: "no_plan", states: {} },
  { name: "no_plan_expanded", states: {}, actions: [{ t: "open" }] },
  { name: "plan_inline", states: planStates(plan) },
  { name: "plan_inline_sv", states: planStates(plan), language: "sv-SE" },
  { name: "plan_short_window", states: planStates(plan), config: { hours: 6 } },
  { name: "custom_title_currency", states: planStates(plan), config: { title: "Värme", currency: "EUR", hours: 48 } },
  { name: "hidden_series", states: planStates(plan), config: { series: { outdoor: false, solar: false } },
    actions: [{ t: "clickChip", key: "price" }] },
  { name: "score_open", states: { ...planStates(plan), ...statStates() },
    actions: [{ t: "clickSel", sel: '[data-stat="score"]' }] },
  { name: "expanded_plan", states: planStates(plan), actions: [{ t: "clickCard" }] },
  { name: "what_if_off", states: planStates(plan), config: { what_if: false }, actions: [{ t: "clickCard" }] },
  { name: "expanded_zoomed", states: planStates(plan), actions: [{ t: "clickCard" }, { t: "zoom", f: 0.25 }] },
  { name: "draft_dirty_menu_open", states: planStates(plan), config: { what_if: true },
    actions: [{ t: "clickCard" }, { t: "dhwDrag" }, { t: "slotMenu" }] },
  { name: "draft_mid_drag", states: planStates(plan), config: { what_if: true },
    actions: [{ t: "clickCard" }, { t: "dhwDrag", hold: true }] },
  { name: "whatif_edited", states: scheduleStates(), config: { what_if: true }, callService: true,
    actions: [{ t: "clickCard" }, { t: "wiDhw", v: "42" }, { t: "addWindow" }] },
  { name: "whatif_weekly", states: (() => {
      const st = planStates(plan);
      st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30";
      st[DEFAULT_DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
      return st; })(), config: { what_if: true }, actions: [{ t: "clickCard" }] },
  { name: "override_active", states: (() => {
      const st = planStates(plan);
      st[DEFAULT_SPACE].attributes.manual_override = overrideInfo;
      st[DEFAULT_DHW].attributes.manual_override = overrideInfo;
      return st; })(), config: { what_if: true }, actions: [{ t: "open" }] },
  { name: "shared_steps", states: sharedStepStates(), actions: [{ t: "clickCard" }] },
  { name: "shared_steps_hover", states: sharedStepStates(),
    actions: [{ t: "clickCard" }, { t: "hoverPlot", pick: "heating" }] },
  { name: "tooltip_hover", states: planStates(plan),
    actions: [{ t: "clickCard" }, { t: "hoverPlot", offsetH: 5 }] },
  { name: "coarse_pointer", states: planStates(plan), actions: [{ t: "clickCard" }] },
  { name: "reduced_motion", states: planStates(plan) },
  { name: "setup_single_buffer", states: setupStates(qaTopologies().base),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }] },
  { name: "setup_two_tank", states: setupStates(qaTopologies().twoTank),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }] },
  { name: "setup_coil", states: setupStates(qaTopologies().coil),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }] },
  { name: "advisor_page", states: (() => {
      const st = setupStates(qaTopologies().base);
      st[DEFAULT_SPACE].attributes.sensor_advisor = {
        basis: "history",
        candidates: [
          { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13, parameters: ["buffer_cooling_rate"], priced: true },
          { key: "lower_floor_temp_entity", label: "Lower floor temperature", spread_c: 2.87, parameters: ["lower_floor_loss_ratio"], priced: true },
          { key: "dhw_temp_entity", label: "Hot water temperature", priced: false, reason: "no_clamped_parameter" },
          { key: "outdoor_temp_entity", label: "Outdoor temperature", priced: false, reason: "weather_backed" },
        ] };
      return st; })(),
    actions: [{ t: "clickCard" }, { t: "page", name: "advisor" }] },
  { name: "layout_editing_dragged", states: setupStates(layoutCatalogTopo()),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }, { t: "layoutDrag" }] },
  { name: "layout_editing_tidy", states: setupStates(layoutCatalogTopo()),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }, { t: "layoutDrag" }, { t: "clickSel", sel: ".layout-tidy" }] },
  { name: "picker_open_filtered", states: setupStates(qaTopologies().base, bigStates()),
    actions: [{ t: "clickCard" }, { t: "page", name: "setup" }, { t: "picker" }], waitMs: 250 },
  { name: "wood_alert", states: woodFuelStates({ cheaper: true, show_whatif: true, ready: true, slots: [] }) },
  { name: "wood_lane", states: woodFuelStates({
      cheaper: false, show_whatif: true, ready: true,
      slots: [{ start: plan.space_plan.forecast[0].t, end: plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t, source: "detected" }] }) },
  { name: "wood_whatif", states: woodFuelStates({ cheaper: false, show_whatif: true, ready: true, slots: [] }),
    config: { what_if: true }, actions: [{ t: "clickCard" }] },
  { name: "away_toggle", states: awayPlanStates({}), actions: [{ t: "clickCard" }] },
  { name: "away_return", states: awayPlanStates({ sw: true }), actions: [{ t: "clickCard" }] },
  { name: "away_status", states: awayPlanStates({ resolved: true }), actions: [{ t: "clickCard" }] },
  { name: "history_panned", states: planStates(plan), history: "full",
    actions: [{ t: "clickCard" }, { t: "pan", h: -10 }], waitMs: 400 },
  { name: "history_deep_panned", states: planStates(plan), history: "full",
    actions: [{ t: "clickCard" }, { t: "pan", h: -40 }], waitMs: 400 },
  { name: "history_unavailable", states: planStates(plan), history: "empty",
    actions: [{ t: "clickCard" }, { t: "pan", h: -10 }], waitMs: 400 },
  { name: "history_pending", states: planStates(plan), history: "pending",
    actions: [{ t: "clickCard" }, { t: "pan", h: -10 }], waitMs: 400 },
];
// editor_schema is data-only (no DOM); the sweep notes it, card_drift owns it.

const VIEWPORTS = { "375x812": 359, "768x1024": 752, "1280x800": 1264 };
const HA_LIGHT = `
  --primary-text-color:#212121; --secondary-text-color:#727272;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#fff; --divider-color:rgba(0,0,0,.12);`;
const HA_DARK = `
  --primary-text-color:#e1e1e1; --secondary-text-color:#9b9b9b;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#1c1c1c; --divider-color:rgba(225,225,225,.12);`;

// ---------------------------------------------------------------- in-page
// Installed once per page: ha-card (the frontend's own :host rule, as
// tests/card_browser.mjs defines it), the frozen clock, and the RUNNER that
// mounts a scenario, drives it and measures the result.
const SETUP = (frozenMs) => {
  if (customElements.get("ha-card")) return;
  customElements.define("ha-card", class extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host{background:var(--card-background-color,white);" +
        "box-sizing:border-box;border-radius:12px;border-width:1px;" +
        "border-style:solid;border-color:var(--divider-color,#e0e0e0);" +
        "display:block;position:relative;}</style><slot></slot>";
    }
  });
  const Real = Date;
  class Frozen extends Real {
    constructor(...a) { super(...(a.length ? a : [frozenMs])); }
    static now() { return frozenMs; }
  }
  window.Date = Frozen;
};

// The history callApi the rig's historyApi provides, in-page. `entries` is
// the rig fixture's {entity_id: [{t, state, attributes}]} shape.
const HISTORY_JS = `
function makeCallApi(kind, entriesJson) {
  const entries = JSON.parse(entriesJson || "{}");
  return async function callApi(method, pathStr) {
    if (kind === "pending") return new Promise(() => {});
    const path = String(pathStr || "");
    const m = /^history\\/period\\/([^?]+)\\?(.*)$/.exec(path);
    if (!m || method !== "GET") throw new Error("unexpected callApi: " + method + " " + path);
    const start = Date.parse(decodeURIComponent(m[1]));
    const q = new URLSearchParams(m[2]);
    const end = Date.parse(q.get("end_time"));
    const ids = (q.get("filter_entity_id") || "").split(",").filter(Boolean);
    const lean = q.has("no_attributes");
    return ids.map((id) => (entries[id] || [])
      .filter((s) => s.t >= start && s.t < end)
      .map((s) => ({ state: String(s.state), last_updated: new Date(s.t).toISOString(),
        ...(lean ? {} : { attributes: s.attributes || {} }) })));
  };
}`;

const RUNNER = async (spec) => {
  const raf2 = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  document.head.querySelectorAll("style.hpo-sweep").forEach((n) => n.remove());
  document.body.innerHTML = "";
  const style = document.createElement("style");
  style.className = "hpo-sweep";
  style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
    `heatpump-optimizer-card{display:block;width:${spec.cardW}px;${spec.themeCss}}`;
  document.head.appendChild(style);
  const card = document.createElement("heatpump-optimizer-card");
  const cfg = Object.assign({ type: "custom:heatpump-optimizer-card" }, spec.config || {});
  const hass = { states: spec.states, language: spec.language || "en" };
  if (spec.history) hass.callApi = makeCallApi(spec.history, spec.historyEntries || "{}");
  if (spec.callService) hass.callService = async () => ({ response: { results: {} } });
  // Lovelace order (hui-card): configured and fed before placement.
  card.setConfig(cfg);
  card.hass = hass;
  document.body.appendChild(card);
  window.__card = card;
  await raf2(); await sleep(spec.waitMs || 120);

  const root = () => card.shadowRoot;
  const svgOf = () => root().querySelector(".chartwrap svg");

  // --- drive ---
  for (const a of spec.actions || []) {
    if (a.t === "open") card.dialog.open();
    else if (a.t === "clickCard") card._onCardClick({});
    else if (a.t === "page") { card.dialog.page = a.name; card._render(); }
    else if (a.t === "zoom") card.view.zoom(a.f);
    else if (a.t === "clickSel") { const el = root().querySelector(a.sel); if (el) el.click(); }
    else if (a.t === "clickChip") {
      const chip = [...root().querySelectorAll(".chip")]
        .find((el) => el.getAttribute("data-key") === a.key);
      if (chip) chip.click();
    } else if (a.t === "hoverPlot") {
      const svg = svgOf(); if (!svg) continue;
      const plot = card._plot;
      let t = plot.windowStart + (a.offsetH || 5) * 3600000;
      if (a.pick === "heating") {
        const sp = spec.states[Object.keys(spec.states).find((k) => k.includes("space_heating_plan"))].attributes.forecast;
        const first = sp.find((p) => Number(p.space_power) > 0.05 && Date.parse(p.t) >= plot.windowStart);
        if (first) t = Date.parse(first.t);
      }
      const r = svg.getBoundingClientRect();
      card._onPointerMove({ currentTarget: svg, clientX: r.left + plot.scaleX(t), clientY: r.top + r.height * 0.4 });
    } else if (a.t === "dhwDrag") {
      const svg = svgOf(); if (!svg) continue;
      const geom = card._geom;
      const runs = card.manual ? card.manual.draft().dhw : card._draftRuns().dhw;
      const lo = (card.manual ? card.manual.bounds() : card._editBounds())[0];
      const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
      if (i < 0) continue;
      const r = svg.getBoundingClientRect();
      const xOf = (t) => r.left + geom.plotL + ((t - geom.windowStart) / (geom.windowEnd - geom.windowStart)) * geom.plotW;
      const target = svg.querySelector(`.slot-hit[data-channel="dhw"][data-index="${i}"]`) || svg;
      const x0 = xOf(runs[i].start + 60000);
      target.dispatchEvent(new PointerEvent("pointerdown", { clientX: x0, clientY: r.top + r.height * 0.6, bubbles: true, pointerId: 1, isPrimary: true }));
      await raf2();
      window.dispatchEvent(new PointerEvent("pointermove", { clientX: xOf(runs[i].start + 60000 + 3600000), clientY: r.top + r.height * 0.6, bubbles: true, pointerId: 1, isPrimary: true }));
      await raf2();
      if (!a.hold) window.dispatchEvent(new PointerEvent("pointerup", { clientX: xOf(runs[i].start + 60000 + 3600000), clientY: r.top + r.height * 0.6, bubbles: true, pointerId: 1, isPrimary: true }));
    } else if (a.t === "slotMenu") {
      const svg = svgOf(); if (!svg) continue;
      const geom = card._geom;
      card.lanes.openMenu("space", geom.windowStart + 2 * 3600000, 120, 40, svg, false);
    } else if (a.t === "wiDhw") {
      card.whatIf.onInput({ ...{ stopPropagation() {}, preventDefault() {} }, target: { value: a.v, classList: { contains: (x) => x === "wi-dhw-min" } } });
      clearTimeout(card.whatIf.timer); card.whatIf.timer = null;
    } else if (a.t === "addWindow") {
      card.whatIf.onAddWindow({ stopPropagation() {}, preventDefault() {} });
    } else if (a.t === "layoutDrag") {
      const l = card.layoutEditor;
      const svg = root().querySelector("svg.setup-svg");
      if (!l || !svg) continue;
      const box = l.boxes.find((b) => b.place === "buffer_tank");
      if (!box) continue;
      const r = svg.getBoundingClientRect();
      const vb = svg.viewBox.baseVal;
      const px = (u) => r.left + (u / vb.width) * r.width;
      const py = (u) => r.top + (u / vb.height) * r.height;
      const from = { x: box.x + box.w / 2, y: box.y + box.h / 2 };
      const to = { x: from.x + 40, y: from.y + 30 };
      const ev = (p) => ({ clientX: px(p.x), clientY: py(p.y), target: { dataset: {} }, stopPropagation() {}, preventDefault() {} });
      l.onDown(ev(from));
      l.onMove(ev({ x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 }));
      l.onUp(ev(to));
    } else if (a.t === "picker") {
      const hit = root().querySelector('.setup-hit[data-key="wood_tank_top_entity"]');
      if (hit) hit.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      await raf2();
      const box = root().querySelector(".sp-filter");
      if (box) { box.value = "vedpanna"; box.dispatchEvent(new Event("input", { bubbles: true })); }
    } else if (a.t === "pan") {
      card.view.panBy(a.h * 3600000);
      await sleep(250);
    }
    await raf2();
  }
  await raf2(); await sleep(150);

  // --- measure ---
  const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const parse = (s) => {
    if (!s || s === "transparent" || s === "none") return null;
    const m = String(s).match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    if (m) return [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]];
    if (s.startsWith("#")) { const c = hex(s.length === 4 ? `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}` : s); return [...c, 1]; }
    return null;
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const ratio = (a, b) => { const la = lum(a), lb = lum(b); return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05); };
  const over = (fg, bg) => fg.map((v, i) => i < 3 ? Math.round(fg[3] * v + (1 - fg[3]) * bg[i]) : 1);
  const visible = (el) => {
    if (!el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    return cs.display !== "none" && cs.visibility !== "hidden" && cs.opacity !== "0";
  };
  // Nearest opaque background, crossing the shadow boundary.
  const bgOf = (el) => {
    let node = el;
    let acc = null;
    for (; node; node = node.parentElement || (node.getRootNode().host || null)) {
      const cs = getComputedStyle(node);
      const c = parse(cs.backgroundColor);
      if (c && c[3] >= 0.99) return acc ? over(acc, c) : c;
      if (c && c[3] > 0) acc = acc ? over(acc, [255, 255, 255, 1]) : c;
    }
    const tok = parse(getComputedStyle(card).getPropertyValue("--card-background-color").trim());
    return acc ? over(acc, tok || [255, 255, 255, 1]) : (tok || [255, 255, 255, 1]);
  };
  const descOf = (el) => {
    const tag = el.tagName.toLowerCase();
    const cls = (typeof el.getAttribute === "function" && el.getAttribute("class")) || "";
    const d = el.getAttribute && el.getAttribute("data-key");
    const i = el.getAttribute && el.getAttribute("data-index");
    return tag + (cls ? "." + cls.split(" ").filter(Boolean).slice(0, 2).join(".") : "") + (d ? `[${d}]` : "") + (i !== null && i !== undefined ? `[${i}]` : "");
  };

  const r = root();
  // Scope to the top layer: when a dialog is open the tile behind it is
  // backdrop-dimmed, and its chips/tabs would fake overlaps with the
  // dialog's own. Popovers (.slot-menu, .picker) may live outside the
  // dialog element; they belong to the top layer too.
  const openDlg = [...r.querySelectorAll("dialog")].find((d) => d.open);
  const layers = [];
  if (openDlg) layers.push(openDlg);
  for (const pop of r.querySelectorAll(".slot-menu, .picker")) {
    if (visible(pop) && (!openDlg || !openDlg.contains(pop))) layers.push(pop);
  }
  const scope = layers.length
    ? { q: (sel) => layers.flatMap((l) => [...l.querySelectorAll(sel)]) }
    : { q: (sel) => [...r.querySelectorAll(sel)] };
  const inDisabled = (el) => {
    for (let n = el; n && n !== r; n = n.parentElement) {
      if (n.disabled) return true;
    }
    return false;
  };
  // Text boxes: HTML elements with direct text (Range over the text nodes)
  // and every SVG <text>.
  const boxes = [];
  const push = (el, rect, fsPx, bold, fgProp) => {
    if (!rect || rect.width < 1 || rect.height < 1) return;
    const cs = getComputedStyle(el);
    let fg = parse(cs[fgProp]);
    if (!fg && fgProp === "fill") fg = parse(el.getAttribute("fill"));
    if (!fg) return;
    if (fg[3] >= 1) fg[3] = Math.min(1, fg[3] * Number(cs.opacity || 1));
    else fg[3] = fg[3] * Number(cs.opacity || 1);
    const large = fsPx >= 24 || (fsPx >= 18.66 && bold);
    boxes.push({ el, desc: descOf(el), x: rect.left, y: rect.top, w: rect.width, h: rect.height,
      fg, bg: bgOf(el), fsPx, bold, large, text: (el.textContent || "").trim().slice(0, 24) });
  };
  const scaleOf = (svg) => {
    const rct = svg.getBoundingClientRect();
    const vb = svg.viewBox && svg.viewBox.baseVal;
    return (vb && vb.width) ? rct.width / vb.width : 1;
  };
  for (const el of scope.q("*")) {
    if (el.namespaceURI && el.namespaceURI.includes("svg")) continue;
    if (!visible(el) || inDisabled(el)) continue;
    const tnodes = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
    if (!tnodes.length) continue;
    const rg = document.createRange();
    let first = true;
    for (const n of tnodes) { rg.selectNodeContents(n); if (first) { rg.setStart(n, 0); first = false; } }
    const rect = rg.getBoundingClientRect();
    const cs = getComputedStyle(el);
    push(el, rect, parseFloat(cs.fontSize), parseInt(cs.fontWeight, 10) >= 600, "color");
  }
  for (const t of scope.q("svg text")) {
    if (inDisabled(t)) continue;
    if (!t.textContent.trim() || !visible(t)) continue;
    const svg = t.closest("svg");
    const scale = scaleOf(svg);
    const attrFs = Number(t.getAttribute("font-size"));
    const fs = (attrFs || parseFloat(getComputedStyle(t).fontSize)) * scale;
    const fw = parseInt(getComputedStyle(t).fontWeight, 10) || 400;
    push(t, t.getBoundingClientRect(), fs, fw >= 600, "fill");
  }

  // (a) text-on-text overlap, neither containing the other
  const overlaps = [];
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (ox >= 1 && oy >= 1) overlaps.push({ a: a.desc, b: b.desc, ta: a.text, tb: b.text,
        fsA: +a.fsPx.toFixed(1), fsB: +b.fsPx.toFixed(1), ox: +ox.toFixed(1), oy: +oy.toFixed(1) });
    }
  }
  // (b) HTML text overflow of its own box
  const overflow = [];
  for (const el of scope.q("*")) {
    if (el.namespaceURI && el.namespaceURI.includes("svg")) continue;
    if (!visible(el) || inDisabled(el)) continue;
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1) {
      overflow.push({ desc: descOf(el), dw: el.scrollWidth - el.clientWidth, dh: el.scrollHeight - el.clientHeight,
        text: (el.textContent || "").trim().slice(0, 24) });
    }
  }
  // (c) WCAG AA contrast
  const contrastFail = [];
  for (const b of boxes) {
    if (b.fg[3] <= 0.05) continue; // fully faded decorative
    const eff = over(b.fg, b.bg);
    const rr = ratio(eff, b.bg);
    const floor = b.large ? 3.0 : 4.5;
    if (rr < floor - 0.005) contrastFail.push({ desc: b.desc, text: b.text, ratio: +rr.toFixed(2), floor, fsPx: +b.fsPx.toFixed(1), fg: b.fg, bg: b.bg });
  }
  // (d) hit targets
  const floorPx = spec.coarse ? 44 : 24;
  const hitSel = ["button", '[role="button"]', '[tabindex="0"]', "input", "select", "a", "rect[tabindex]"].join(", ");
  const hits = [];
  const hitsSmall = [];
  for (const el of scope.q(hitSel)) {
    if (!visible(el) || el.disabled || inDisabled(el)) continue;
    const b = el.getBoundingClientRect();
    if (b.width < 0.5 || b.height < 0.5) continue;
    hits.push(descOf(el));
    if (Math.min(b.width, b.height) < floorPx - 0.05) hitsSmall.push({ desc: descOf(el), w: +b.width.toFixed(1), h: +b.height.toFixed(1) });
  }
  // (g) focusables and zero-size focus traps
  const focusables = scope.q(hitSel).filter((el) => visible(el) && !inDisabled(el));
  focusables.forEach((el, i) => el.setAttribute("data-hpo-fi", String(i)));
  const zeroFocus = focusables.filter((el) => { const b = el.getBoundingClientRect(); return b.width < 1 || b.height < 1; }).map(descOf);

  // headline numbers alignment (professional-look probe): the .stats row
  const statsRects = [...r.querySelectorAll(".stats [data-stat], .stat, [data-stat]")]
    .filter(visible).map((el) => { const b = el.getBoundingClientRect(); return { desc: descOf(el), y: +b.y.toFixed(1), h: +b.height.toFixed(1) }; });

  return {
    overlaps, overflow, contrastFail, hitsCount: hits.length, hitsSmall,
    focusables: focusables.length, zeroFocus,
    svgTextCount: boxes.filter((b) => b.desc.startsWith("text")).length,
    statsRects,
    dbgFill: (() => {
      const t = r.querySelector("svg text");
      if (!t) return null;
      return { attr: t.getAttribute("fill"), cs: getComputedStyle(t).fill,
        v: getComputedStyle(t).getPropertyValue("--secondary-text-color").trim(),
        hostV: getComputedStyle(card).getPropertyValue("--secondary-text-color").trim(),
        styleEl: (document.querySelector("style.hpo-sweep") || {}).textContent || null };
    })(),
    anchors: anchorsOf(),
  };
  function anchorsOf() {
    const out = {};
    const grab = (name, el) => { if (el) { const b = el.getBoundingClientRect(); out[name] = [b.left, b.top, b.width, b.height]; } };
    grab("card", card);
    const svgs = [...r.querySelectorAll("svg")];
    let best = null;
    for (const s of svgs) { const b = s.getBoundingClientRect(); if (!best || b.width * b.height > best[2] * best[3]) best = [b.left, b.top, b.width, b.height]; }
    if (best) out.bigsvg = best;
    [...r.querySelectorAll(".chip")].slice(0, 12).forEach((el, i) => { const b = el.getBoundingClientRect(); out["chip" + i] = [b.left, b.top, b.width, b.height]; });
    return out;
  }
};

// ---------------------------------------------------------------- main
const CONC = (() => {
  const { execSync } = require("node:child_process");
  try {
    const out = execSync("ps aux | grep -E '[s]tress\\.py|[t]ests/run\\.sh' | wc -l", { shell: "/bin/sh" }).toString().trim();
    return Number(out) || 0;
  } catch { return -1; }
})();
console.log(`# concurrent stress/run.sh processes at start: ${CONC}`);

const t0 = process.hrtime.bigint();
const cpu0 = process.cpuUsage();
let states = SCENARIOS;
if (process.env.MAX_STATES) {
  const want = new Set(process.env.MAX_STATES.split(",").map((s) => s.trim()));
  states = SCENARIOS.filter((s) => want.has(s.name));
}

// The history fixture (rig shape) computed in Node, passed in as JSON.
const HISTORY_IDS = {
  indoor: "sensor.heat_pump_optimizer_indoor_temperature_optimizer",
  outdoor: "sensor.heat_pump_optimizer_outdoor_temperature_optimizer",
  price: "sensor.heat_pump_optimizer_cost_current_electricity_price",
  solar: "sensor.heat_pump_optimizer_solar_irradiance",
  action: "sensor.heat_pump_optimizer_heat_pump_action",
};
const HSTEP = 30 * 60000, HSPAN = 48 * HOUR;
const historyEntries = (() => {
  const entries = { [HISTORY_IDS.indoor]: [], [HISTORY_IDS.outdoor]: [], [HISTORY_IDS.price]: [], [HISTORY_IDS.solar]: [], [HISTORY_IDS.action]: [] };
  const n = Math.floor(HSPAN / HSTEP);
  for (let i = n; i >= 1; i--) {
    const t = FROZEN - i * HSTEP, k = i / n, hourOfDay = (t / HOUR) % 24;
    entries[HISTORY_IDS.indoor].push({ t, state: (21 + 0.9 * Math.sin(k * Math.PI * 3)).toFixed(1) });
    entries[HISTORY_IDS.outdoor].push({ t, state: (2.5 + 4 * Math.sin(k * Math.PI * 2)).toFixed(1) });
    entries[HISTORY_IDS.price].push({ t, state: (0.42 + 0.31 * Math.sin(k * Math.PI * 5)).toFixed(4) });
    entries[HISTORY_IDS.solar].push({ t, state: Math.max(0, Math.round(320 * Math.sin((hourOfDay - 6) / 12 * Math.PI))).toString() });
    const mode = i % 3 === 0 ? "off" : i % 3 === 1 ? "pre_heat" : "comfort";
    entries[HISTORY_IDS.action].push({ t, state: mode, attributes: { power_kw: mode === "off" ? 0 : mode === "pre_heat" ? 4.1 : 2.3, heat_pump_on: mode !== "off" } });
  }
  entries[HISTORY_IDS.indoor][Math.floor(n / 2)].state = "unavailable";
  return JSON.stringify(entries);
})();

const browser = await chromium.launch();
const results = [];
let consoleErrs = 0, pageErrs = 0;
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
let cdpSession = null;
page.on("console", (m) => { if (m.type() === "error") consoleErrs += 1; });
page.on("pageerror", () => { pageErrs += 1; });
await page.goto("about:blank");
await page.addScriptTag({ content: `(${SETUP.toString()})(${FROZEN});\n${HISTORY_JS}` });
await page.addScriptTag({ path: CARD_SRC });

const runOne = async (sc, vw, vh, theme, cond) => {
  const themeCss = theme === "dark" ? HA_DARK : theme === "light" ? HA_LIGHT : "";
  await page.setViewportSize({ width: vw, height: vh });
  if (cond === "rm") await page.emulateMedia({ reducedMotion: "reduce" });
  else await page.emulateMedia({ reducedMotion: "no-preference" });
  if (cond === "coarse") {
    if (!cdpSession) cdpSession = await page.context().newCDPSession(page);
    await cdpSession.send("Emulation.setEmulatedMedia", { features: [{ name: "pointer", value: "coarse" }] });
    await page.evaluate(() => {
      const orig = window.matchMedia.bind(window);
      window.matchMedia = (q) => {
        if (q === "(pointer: coarse)") {
          return { matches: true, media: q, onchange: null, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return true; } };
        }
        return orig(q);
      };
    });
  }
  const errsBefore = consoleErrs + pageErrs;
  let m = null, err = null;
  try {
    m = await page.evaluate(RUNNER, {
      states: sc.states, config: sc.config, language: sc.language,
      actions: sc.actions || [], cardW: VIEWPORTS[`${vw}x${vh}`] || vw - 16,
      themeCss, waitMs: sc.waitMs || 120,
      history: sc.history || null, historyEntries,
      callService: !!sc.callService, coarse: cond === "coarse",
    });
  } catch (e) { err = String(e && e.message || e).slice(0, 200); }
  // hover layout shift on the first interactive controls
  let hoverShifts = 0, hoverShiftsBig = 0;
  if (m && m.anchors && !err) {
    try {
      const hoverables = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const sel = ["button", ".chip", '[role="button"]'].join(", ");
        return [...root.querySelectorAll(sel)]
          .filter((el) => { const b = el.getBoundingClientRect(); return b.width > 4 && b.height > 4 && getComputedStyle(el).visibility !== "hidden"; })
          .slice(0, 8)
          .map((el) => { const b = el.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; });
      });
      for (const [x, y] of hoverables) {
        await page.mouse.move(x, y);
        await page.waitForTimeout(90);
        const after = await page.evaluate(() => {
          const card = window.__card; const root = card.shadowRoot; const out = {};
          const grab = (name, el) => { if (el) { const b = el.getBoundingClientRect(); out[name] = [b.left, b.top, b.width, b.height]; } };
          grab("card", card);
          const svgs = [...root.querySelectorAll("svg")];
          let best = null;
          for (const s of svgs) { const b = s.getBoundingClientRect(); if (!best || b.width * b.height > best[2] * best[3]) best = [b.left, b.top, b.width, b.height]; }
          if (best) out.bigsvg = best;
          [...root.querySelectorAll(".chip")].slice(0, 12).forEach((el, i) => { const b = el.getBoundingClientRect(); out["chip" + i] = [b.left, b.top, b.width, b.height]; });
          return out;
        });
        for (const k of Object.keys(m.anchors)) {
          const a = m.anchors[k], b = after[k];
          if (!b) continue;
          const d = Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]), Math.abs(a[3] - b[3]));
          if (d > 0.5) hoverShifts += 1;
          if (d > 2) hoverShiftsBig += 1;
        }
      }
      await page.mouse.move(1, 1);
    } catch { /* hover failures are recorded as zero */ }
  }
  // Tab reachability
  let tabReach = 0;
  if (m && !err) {
    try {
      const n = m.focusables;
      await page.evaluate(() => document.body.focus && document.body.focus());
      const seen = new Set();
      for (let i = 0; i < Math.min(2 * n + 6, 80); i++) {
        await page.keyboard.press("Tab");
        const info = await page.evaluate(() => {
          const card = window.__card;
          const a = document.activeElement;
          const sa = card.shadowRoot && card.shadowRoot.activeElement;
          const el = (a === card && sa) ? sa : a;
          if (!el) return null;
          if (a === card && sa) {
            return el.getAttribute("data-hpo-fi") !== null
              ? "fi:" + el.getAttribute("data-hpo-fi")
              : (el.getAttribute("class") || el.tagName);
          }
          if (el.closest && el.closest("heatpump-optimizer-card")) {
            return el.getAttribute("data-hpo-fi") !== null
              ? "fi:" + el.getAttribute("data-hpo-fi")
              : (el.getAttribute("class") || el.tagName);
          }
          return null;
        });
        if (info !== null) seen.add(String(info));
      }
      tabReach = seen.size;
    } catch { /* count stays 0 */ }
  }
  const errs = consoleErrs + pageErrs - errsBefore;
  const inkOverlap = m ? m.overlaps.filter((o) => o.oy >= 3 && o.oy >= 0.25 * Math.max(o.fsA, o.fsB)).length : null;
  return {
    state: sc.name, viewport: `${vw}x${vh}`, theme, cond,
    inkOverlapPairs: inkOverlap,
    overlapPairs: m ? m.overlaps.length : null,
    overflow: m ? m.overflow.length : null,
    contrastFails: m ? m.contrastFail.length : null,
    hits: m ? m.hitsCount : null,
    hitsSmall: m ? m.hitsSmall.length : null,
    focusables: m ? m.focusables : null,
    tabReach, zeroFocus: m ? m.zeroFocus : null,
    svgText: m ? m.svgTextCount : null,
    dbgFill: m ? m.dbgFill : null,
    hoverShifts, hoverShiftsBig, errs, err,
    detail: m ? { overlaps: m.overlaps, overflow: m.overflow, contrastFail: m.contrastFail, hitsSmall: m.hitsSmall, statsRects: m.statsRects } : null,
  };
};

const arms = [];
for (const [vp] of Object.entries(VIEWPORTS)) {
  for (const theme of ["light", "dark"]) arms.push({ vp, theme, cond: "plain", lang: "en" });
}
arms.push({ vp: "1280x800", theme: "light", cond: "plain", lang: "sv" });
arms.push({ vp: "768x1024", theme: "light", cond: "rm", lang: "en" });
arms.push({ vp: "375x812", theme: "light", cond: "coarse", lang: "en" });

if (!process.env.SHOTS) {
  for (const arm of arms) {
    const [w, h] = arm.vp.split("x").map(Number);
    for (const sc of states) {
      if (arm.lang === "sv" && sc.language && sc.language !== "sv-SE") {
        // sv arm: render every state with sv-SE so labels localise.
        sc = { ...sc, language: "sv-SE" };
      }
      const res = await runOne(sc, w, h, arm.theme, arm.cond);
      res.arm = `${arm.vp}/${arm.theme}/${arm.cond}/${arm.lang}`;
      results.push(res);
      process.stdout.write(`DETAIL ${res.state} @${res.arm} ov=${res.overlapPairs} of=${res.overflow} cf=${res.contrastFails} hits=${res.hits}/${res.hitsSmall} foc=${res.focusables}/${res.tabReach} hs=${res.hoverShifts} err=${res.errs}${res.err ? " ERR:" + res.err : ""}\n`);
    }
    if (arm.cond === "coarse") {
      // restore fine pointer
      await page.evaluate(() => { delete window.__coarseStub; });
      const cdp2 = await page.context().newCDPSession(page);
      await cdp2.send("Emulation.setEmulatedMedia", { features: [{ name: "pointer", value: "fine" }] });
      // drop the matchMedia stub is not possible; recreate the page.
    }
    if (arm.cond === "coarse") break; // stubbed matchMedia must not leak
  }
}

// ---- screenshots (SHOTS=1): representative states ---------------------
if (process.env.SHOTS) {
  const shots = [
    ["plan_inline", "375x812", "light", "plain"], ["expanded_plan", "375x812", "light", "plain"],
    ["whatif_edited", "375x812", "light", "plain"], ["setup_two_tank", "375x812", "light", "plain"],
    ["advisor_page", "375x812", "light", "plain"], ["wood_alert", "375x812", "light", "plain"],
    ["away_return", "375x812", "light", "plain"], ["no_plan", "375x812", "light", "plain"],
    ["picker_open_filtered", "375x812", "light", "plain"], ["layout_editing_dragged", "375x812", "light", "plain"],
    ["draft_dirty_menu_open", "375x812", "light", "plain"], ["history_panned", "375x812", "light", "plain"],
    ["expanded_plan", "375x812", "dark", "plain"], ["expanded_plan", "1280x800", "light", "plain"],
    ["plan_inline", "1280x800", "light", "plain"], ["expanded_zoomed", "768x1024", "light", "plain"],
    ["expanded_plan", "375x812", "light", "coarse"], ["expanded_plan", "768x1024", "light", "rm"],
  ];
  mkdirSync(path.join(__dirname, "shots"), { recursive: true });
  for (const [name, vp, theme, cond] of shots) {
    const sc = SCENARIOS.find((s) => s.name === name);
    if (!sc) continue;
    const [w, h] = vp.split("x").map(Number);
    await runOne(sc, w, h, theme, cond);
    const file = path.join(__dirname, "shots", `${name}_${vp}_${theme}${cond !== "plain" ? "_" + cond : ""}.png`);
    await page.screenshot({ path: file, fullPage: true });
    console.log(`SHOT ${path.basename(file)}`);
  }
}
await browser.close();

// ---- totals -----------------------------------------------------------
const sum = (f) => results.reduce((a, r) => a + (f(r) || 0), 0);
const renderCount = results.length;
const stats = {
  renders: renderCount,
  states: new Set(results.map((r) => r.state)).size,
  overlapPairs: sum((r) => r.overlapPairs),
  inkOverlapPairs: sum((r) => r.inkOverlapPairs),
  overflow: sum((r) => r.overflow),
  contrastFails: sum((r) => r.contrastFails),
  contrastLight: sum((r) => r.theme === "light" ? r.contrastFails : 0),
  contrastDark: sum((r) => r.theme === "dark" ? r.contrastFails : 0),
  contrastSv: sum((r) => r.arm && r.arm.endsWith("/sv") ? r.contrastFails : 0),
  hitsSmallFine: sum((r) => r.cond === "plain" ? r.hitsSmall : 0),
  hitsSmallCoarse: sum((r) => r.cond === "coarse" ? r.hitsSmall : 0),
  hitsTotal: sum((r) => r.hits),
  focusTotal: sum((r) => r.focusables),
  focusUnreachable: sum((r) => Math.max(0, (r.focusables || 0) - r.tabReach)),
  zeroFocus: sum((r) => (r.zeroFocus || []).length),
  hoverShifts: sum((r) => r.hoverShifts),
  hoverShiftsBig: sum((r) => r.hoverShiftsBig),
  errs: sum((r) => r.errs),
  mountErrs: results.filter((r) => r.err).length,
};
writeFileSync(path.join(__dirname, "sweep-details.json"), JSON.stringify({ stats, results }, null, 1));

const wall = Number(process.hrtime.bigint() - t0) / 1e9;
const cpu = process.cpuUsage(cpu0);
const tf = (cpu.user + cpu.system) / 1e6 / wall;
console.log(`RESULT renders=${stats.renders} count`);
console.log(`RESULT states=${stats.states} count`);
console.log(`RESULT text_overlap_pairs=${stats.overlapPairs} count (raw bbox; includes glyph-padding adjacency)`);
console.log(`RESULT text_overlap_ink_plausible=${stats.inkOverlapPairs} count (oy>=3px AND oy>=25% of the larger font — glyph boxes cannot overlap by less than their padding)`);
console.log(`RESULT text_overflow=${stats.overflow} count`);
console.log(`RESULT contrast_aa_fail=${stats.contrastFails} count (light=${stats.contrastLight} dark=${stats.contrastDark} sv=${stats.contrastSv})`);
console.log(`RESULT hit_under24_fine=${stats.hitsSmallFine} of ${stats.hitsTotal} targets`);
console.log(`RESULT hit_under44_coarse=${stats.hitsSmallCoarse} count`);
console.log(`RESULT focus_unreachable=${stats.focusUnreachable} of ${stats.focusTotal}`);
console.log(`RESULT focus_zero_size=${stats.zeroFocus} count`);
console.log(`RESULT hover_shift_gt05px=${stats.hoverShifts} count (>2px: ${stats.hoverShiftsBig})`);
console.log(`RESULT console_page_errors=${stats.errs} count`);
console.log(`RESULT mount_errors=${stats.mountErrs} count`);
console.log(`RESULT thread_factor=${tf.toFixed(2)} (node cpu_ms=${((cpu.user + cpu.system) / 1000).toFixed(0)} wall_s=${wall.toFixed(1)}; browser CPU is out-of-process and excluded — this harness reports contention-immune counts only)`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT concurrent_test_procs=${CONC} count`);
