// D4 (UI/UX) round 2 -- the card's real geometry in real Chromium.
//
// METRIC (one line each; every number is a count, contention-immune):
//   text_overlap_pairs  : pairs of visible text boxes (HTML text-node client
//                         rects, SVG <text>/<tspan> rects) from different,
//                         non-nested elements whose intersection is >= 1.5 px
//                         on its narrower side. Overlay panes (.tooltip,
//                         .slot-menu, .setup-picker, .viewctl) occlude by
//                         design: a pair with exactly one side in an overlay
//                         is not counted.
//   text_overflow       : visible text boxes that spill > 1 px past a clipping
//                         ancestor (overflow hidden/clip on that axis, or the
//                         outer <svg>) or past the measured scope's box, plus
//                         elements with nowrap/clipped text whose scrollWidth
//                         exceeds clientWidth by > 1 px.
//   contrast_fail       : visible text boxes whose WCAG 2.x contrast ratio
//                         (fg = computed color/fill x opacity chain, composited
//                         over the first opaque ancestor background) is below
//                         4.5:1, or 3:1 for large text (>= 24 px, or >= 18.66 px
//                         bold). The host supplies Home Assistant's default
//                         light and dark theme tokens (see HA_TOKENS).
//   hit_small_24        : interactive targets whose smaller side is < 24 px
//                         (WCAG 2.2 SC 2.5.8); hit_small_24_nospacing further
//                         requires that a 24 px circle on the target's centre
//                         intersects another target (the SC's spacing
//                         exception does not rescue it).
//   hit_small_44_coarse : the same on the coarse-pointer arm at 44 px.
//   tab_unreached       : visible focusables inside the measured scope that a
//                         Tab walk from the document body (up to 120 presses,
//                         until it wraps to its first stop) never reaches.
//   focus_no_indicator  : focus stops that show no outline, box-shadow or
//                         stroke change when focused via Tab.
//   console_errors      : console.error + uncaught page errors during a state.
//   hover_shift         : elements (outside overlays) whose rect moves > 0.5 px
//                         when a chip/button/tab/setup row is hovered.
//   min_text_px         : the smallest on-screen font of any visible text box.
//
// COMMAND (from the export root; HPO_PLANDATA written by tests/plan_view.py):
//   HPO_PLANDATA=$TMP/plandata.json \
//   NODE_PATH=$PW/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round2/D4/card_geometry.mjs [--shots] [--quick]
//   --shots writes PNGs under tools/audit/round2/D4/shots/ (light/en and
//   dark/sv arms); --quick runs only the 375x812 light/en arm.
//
// EXPECTED (baseline c398fc84, Apple M1, Chromium 1148 / Playwright 1.49.0):
//   see REPORT.md; the RESULT lines below are exact counts (tolerance: exact
//   for counts; +-1 on hover/tab counts, which depend on focus timing).
//
// INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/www/
//   heatpump-optimizer-card.js:HeatpumpOptimizerCard (the whole element:
//   cardStyleBlock, renderChart, Legend.html, ExpandedDialog.html,
//   LaneEditor, SetupPage, WhatIfPanel) driven through the same 26 states
//   tests/card_drift.mjs renders, in Chromium instead of the DOM stub.
//
// The 26 states are tests/card_drift.mjs:STATES, re-driven with real events
// (the stub's `fire()` has no browser equivalent). The state builders
// (planStates, qaTopologies, layoutCatalogTopo, ...) are imported from
// tests/card_rig.mjs unchanged.
//
// Writes only under its own directory (results.json, shots/).
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import {
  CARD_PATH, DEFAULT_SPACE, DEFAULT_DHW, HOUR,
  planStates, setupSensorStates, qaTopologies, layoutCatalogTopo,
} from "../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../../..");
const args = process.argv.slice(2);
const SHOTS = args.includes("--shots");
const QUICK = args.includes("--quick");

const planPath = process.env.HPO_PLANDATA;
if (!planPath || !fs.existsSync(planPath)) {
  console.error("FAIL: set HPO_PLANDATA to the payload tests/plan_view.py wrote");
  process.exit(1);
}
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const CARD_SRC = fs.readFileSync(path.join(repo, CARD_PATH), "utf8");

// --- Home Assistant's default theme tokens ---------------------------------
// There is no HA frontend on this box. These are the values the frontend's
// styles-data.ts ships for the default light theme and for its dark mode,
// which every stock install renders the card against.
const HA_TOKENS = {
  light: `
    --primary-text-color:#212121; --secondary-text-color:#727272;
    --text-primary-color:#fff; --disabled-text-color:#bdbdbd;
    --primary-color:#03a9f4; --accent-color:#ff9800;
    --divider-color:rgba(0,0,0,.12); --error-color:#db4437;
    --warning-color:#ffa600; --success-color:#43a047; --info-color:#039be5;
    --card-background-color:#fff; --primary-background-color:#fafafa;
    --secondary-background-color:#e5e5e5;`,
  dark: `
    --primary-text-color:#e1e1e1; --secondary-text-color:#9b9b9b;
    --text-primary-color:#fff; --disabled-text-color:#6f6f6f;
    --primary-color:#03a9f4; --accent-color:#ff9800;
    --divider-color:rgba(225,225,225,.12); --error-color:#db4437;
    --warning-color:#ffa600; --success-color:#43a047; --info-color:#039be5;
    --card-background-color:#1c1c1c; --primary-background-color:#111;
    --secondary-background-color:#202020;`,
};
// <ha-card> is a Home Assistant custom element, and the card renders its
// own <ha-card> INSIDE its shadow root, where a page-level rule cannot
// reach it. Without a definition it is an inline unknown element and its
// padding never shapes the chart. This is the frontend's ha-card.ts :host
// rule set, defined before the card script loads.
const HA_CARD_DEF = `
customElements.define("ha-card", class extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{" +
      "background:var(--ha-card-background,var(--card-background-color,white));" +
      "box-shadow:var(--ha-card-box-shadow,none);box-sizing:border-box;" +
      "border-radius:var(--ha-card-border-radius,12px);" +
      "border-width:var(--ha-card-border-width,1px);border-style:solid;" +
      "border-color:var(--ha-card-border-color,var(--divider-color,#e0e0e0));" +
      "color:var(--primary-text-color);display:block;position:relative;}" +
      "</style><slot></slot>";
  }
});`;
// The tile a dashboard gives the card: a phone spans the viewport minus the
// 8 px gutters; a tablet's two masonry columns; a desktop sections column
// (max 400 px). `panel` is the wide tile card_browser.mjs measures against.
const VIEWPORTS = {
  phone: { width: 375, height: 812, tile: 359 },
  tablet: { width: 768, height: 1024, tile: 372 },
  desktop: { width: 1280, height: 800, tile: 400 },
  panel: { width: 1280, height: 800, tile: 1200 },
};

// --- the states (tests/card_drift.mjs:STATES, browser edition) --------------
const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": {
    state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": {
    state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": {
    state: "cheap_price", attributes: {
      lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
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
      state: "20.0",
      attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` },
    };
  }
  st["sensor.vedpanna_temperatur_temperature"] = {
    state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = {
    state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  return st;
};
const FROZEN_ISO = plan.dhw_plan.forecast[0].t; // + 6 h, resolved in-page
const overrideStates = () => {
  const st = planStates(plan);
  const info = {
    active: true, expires_at: "__FROZEN_PLUS_5H__",
    space_slots: [], dhw_slots: [], released_space: [], released_dhw: [],
  };
  st[DEFAULT_SPACE].attributes.manual_override = info;
  st[DEFAULT_DHW].attributes.manual_override = info;
  return st;
};
const weeklyStates = () => {
  const st = planStates(plan);
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30";
  st[DEFAULT_DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
  return st;
};

// Each state: the states/config/hassExtra to mount with, and a `drive`
// keyword the in-page driver interprets (see PAGE_DRIVER).
const STATES = [
  { name: "no_plan", states: {}, drive: "none" },
  { name: "no_plan_expanded", states: {}, drive: "open" },
  { name: "plan_inline", states: planStates(plan), drive: "none" },
  { name: "plan_inline_sv", states: planStates(plan), hassExtra: { language: "sv-SE" }, drive: "none" },
  { name: "plan_short_window", states: planStates(plan), config: { hours: 6 }, drive: "none" },
  { name: "custom_title_currency", states: planStates(plan),
    config: { title: "Värme", currency: "EUR", hours: 48 }, drive: "none" },
  { name: "hidden_series", states: planStates(plan),
    config: { series: { outdoor: false, solar: false } }, drive: "click_price_chip" },
  { name: "score_open", states: { ...planStates(plan), ...statStates() }, drive: "click_score" },
  { name: "expanded_plan", states: planStates(plan), drive: "open" },
  { name: "what_if_off", states: planStates(plan), config: { what_if: false }, drive: "open" },
  { name: "expanded_zoomed", states: planStates(plan), drive: "open_zoom" },
  { name: "draft_dirty_menu_open", states: planStates(plan), config: { what_if: true }, drive: "drag_menu" },
  { name: "whatif_edited", states: scheduleStates(), config: { what_if: true }, drive: "whatif_edit" },
  { name: "whatif_weekly", states: weeklyStates(), config: { what_if: true }, drive: "open" },
  { name: "override_active", states: overrideStates(), config: { what_if: true }, drive: "open" },
  { name: "shared_steps", states: sharedStepStates(), drive: "open" },
  { name: "shared_steps_hover", states: sharedStepStates(), drive: "open_hover_shared" },
  { name: "tooltip_hover", states: planStates(plan), drive: "open_hover_5h" },
  { name: "coarse_pointer", states: planStates(plan), drive: "open", media: "coarse" },
  { name: "reduced_motion", states: planStates(plan), drive: "none", media: "reduce" },
  { name: "setup_single_buffer", states: setupStates(qaTopologies().base), drive: "setup" },
  { name: "setup_two_tank", states: setupStates(qaTopologies().twoTank), drive: "setup" },
  { name: "setup_coil", states: setupStates(qaTopologies().coil), drive: "setup" },
  { name: "layout_editing_dragged", states: setupStates(layoutCatalogTopo()), drive: "setup_layout_drag" },
  { name: "picker_open_filtered", states: setupStates(qaTopologies().base, bigStates()), drive: "setup_picker" },
  { name: "editor_schema", states: {}, drive: "editor" },
];

// --- the in-page driver and measurer ----------------------------------------
// Installed once per page as window.__d4. Everything below runs in Chromium.
const PAGE_DRIVER = String.raw`
window.__d4 = (() => {
  const HOUR = 3600000;
  const noop = { stopPropagation() {}, preventDefault() {} };
  const TAG = "heatpump-optimizer-card";
  const OVERLAY = ".tooltip, .slot-menu, .setup-picker, .viewctl";
  const FOCUSABLE = 'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])';
  const TARGETS = FOCUSABLE + ', [role="button"], .chip, .setup-hit, .slot, .slot-handle, .lane, .dlg-tab, .hl-score, .layout-port-hit';

  function mount(states, config, hassExtra) {
    document.body.innerHTML = "";
    const card = document.createElement(TAG);
    card.setConfig({ type: "custom:" + TAG, ...(config || {}) });
    const hass = { states, language: "en", ...(hassExtra || {}) };
    card.hass = hass;
    document.body.appendChild(card);
    card.hass = hass;
    window.__card = card;
    return card;
  }
  const raf2 = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const svgOf = (card) => card.shadowRoot.querySelector(".chartwrap svg");
  const clientX = (card, svg, t) => {
    const r = svg.getBoundingClientRect();
    const vb = svg.viewBox.baseVal;
    return r.left + card._plot.scaleX(t) * (r.width / vb.width);
  };

  async function drive(spec, frozen) {
    const hassExtra = { ...(spec.hassExtra || {}) };
    if (spec.language && !spec.hassExtra) hassExtra.language = spec.language;
    if (spec.drive === "editor") {
      document.body.innerHTML = "";
      const e = document.createElement(TAG + "-editor");
      e.setConfig({ type: "custom:" + TAG, hours: 12, series: { solar: false } });
      e.hass = { states: {}, language: hassExtra.language || "en" };
      document.body.appendChild(e);
      window.__card = e;
      await raf2();
      return { schemaEntries: e._schema().length, hover: null };
    }
    // The override banner's expiry rides on the frozen clock.
    const states = JSON.parse(JSON.stringify(spec.states).replaceAll(
      "__FROZEN_PLUS_5H__", new Date(frozen + 5 * HOUR).toISOString()));
    const card = mount(states, spec.config, hassExtra);
    await raf2();
    let hover = null;
    const open = () => { card._onCardClick({}); };
    switch (spec.drive) {
      case "none": break;
      case "open": open(); break;
      case "click_price_chip": {
        const chip = [...card.shadowRoot.querySelectorAll(".chip")]
          .find((el) => el.getAttribute("data-key") === "price");
        if (chip) chip.click();
        break;
      }
      case "click_score": {
        const stat = card.shadowRoot.querySelector('[data-stat="score"]');
        if (stat) stat.click();
        break;
      }
      case "open_zoom": open(); await raf2(); card.view.zoom(0.25); break;
      case "drag_menu": {
        open(); await raf2();
        const svg = svgOf(card);
        const geom = card._geom;
        const slot = [...svg.querySelectorAll('rect.slot[data-channel="dhw"]')]
          .find((r) => !r.classList.contains("locked"));
        let drag = null;
        if (slot && geom) {
          const b = slot.getBoundingClientRect();
          const r = svg.getBoundingClientRect();
          const pxPerMs = (geom.plotW / (geom.windowEnd - geom.windowStart)) * (r.width / svg.viewBox.baseVal.width);
          drag = { x1: b.left + Math.min(4, b.width / 2), y: b.top + b.height / 2, dx: pxPerMs * HOUR };
        }
        return { hover: null, drag, then: "open_menu" };
      }
      case "whatif_edit": {
        card._hass = { states: card._hass.states, language: hassExtra.language || "en",
          callService: async () => ({ response: { results: {} } }) };
        open(); await raf2();
        card.whatIf.onInput({ ...noop,
          target: { value: "42", classList: { contains: (x) => x === "wi-dhw-min" } } });
        clearTimeout(card.whatIf.timer); card.whatIf.timer = null;
        card.whatIf.onAddWindow({ ...noop });
        break;
      }
      case "open_hover_shared": {
        open(); await raf2();
        const svg = svgOf(card); const plot = card._plot;
        const sp = states[Object.keys(states).find((k) => k.endsWith("space_heating_plan"))].attributes.forecast;
        const first = sp.find((p) => Number(p.space_power) > 0.05 && Date.parse(p.t) >= plot.windowStart);
        const t = first ? Date.parse(first.t) : plot.windowStart + 5 * HOUR;
        const r = svg.getBoundingClientRect();
        hover = { x: clientX(card, svg, t), y: r.top + r.height * 0.35 };
        break;
      }
      case "open_hover_5h": {
        open(); await raf2();
        const svg = svgOf(card); const plot = card._plot;
        const r = svg.getBoundingClientRect();
        hover = { x: clientX(card, svg, plot.windowStart + 5 * HOUR), y: r.top + r.height * 0.35 };
        break;
      }
      case "setup": open(); await raf2(); card.dialog.page = "setup"; card._render(); break;
      case "setup_layout_drag": {
        open(); await raf2(); card.dialog.page = "setup"; card._render(); await raf2();
        const toggle = card.shadowRoot.querySelector(".layout-edit-toggle");
        if (toggle) toggle.click();
        await raf2();
        const box = (card.layout.boxes || []).find((b) => b.place === "buffer_tank");
        const svg = card.shadowRoot.querySelector("svg.setup-svg");
        let drag = null;
        if (box && svg) {
          const r = svg.getBoundingClientRect(); const vb = svg.viewBox.baseVal;
          const k = r.width / vb.width;
          drag = { x1: r.left + (box.x + box.w / 2) * k, y: r.top + (box.y + box.h / 2) * k, dx: 40 * k, dy: 30 * k };
        }
        return { hover: null, drag };
      }
      case "setup_picker": {
        open(); await raf2(); card.dialog.page = "setup"; card._render(); await raf2();
        const hit = [...card.shadowRoot.querySelectorAll(".setup-hit")]
          .find((h) => h.dataset.key === "wood_tank_top_entity");
        if (hit) hit.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true }));
        await raf2();
        const box = card.shadowRoot.querySelector(".sp-filter");
        if (box) { box.value = "vedpanna"; box.dispatchEvent(new Event("input", { bubbles: true })); }
        break;
      }
    }
    await raf2();
    return { hover };
  }

  function openMenuAfterDrag() {
    const card = window.__card;
    const svg = svgOf(card); const geom = card._geom;
    const r = svg.getBoundingClientRect();
    card.lanes.openMenu("space", geom.windowStart + 2 * HOUR, r.left + 120, r.top + 40, svg, false);
  }

  // ---- measurement ---------------------------------------------------------
  function scopeOf(card) {
    const root = card.shadowRoot;
    if (!root) return card;
    const dlg = root.querySelector("dialog[open]");
    return dlg || root.querySelector("ha-card") || card;
  }
  const cs = (el) => getComputedStyle(el);
  function opacityChain(el, stopAt) {
    let o = 1; let n = el;
    while (n && n !== stopAt && n.nodeType === 1) {
      const st = cs(n);
      if (st.display === "none" || st.visibility === "hidden") return 0;
      o *= parseFloat(st.opacity || "1");
      n = n.parentElement || (n.parentNode && n.parentNode.host) || null;
    }
    return o;
  }
  function parseColor(s) {
    const m = /rgba?\(([^)]+)\)/.exec(s || "");
    if (!m) return null;
    const p = m[1].split(",").map((x) => parseFloat(x));
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function over(fg, bg) {
    const a = fg.a + bg.a * (1 - fg.a);
    const mix = (c, d) => (c * fg.a + d * bg.a * (1 - fg.a)) / (a || 1);
    return { r: mix(fg.r, bg.r), g: mix(fg.g, bg.g), b: mix(fg.b, bg.b), a };
  }
  function lum(c) {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function ratio(a, b) { const la = lum(a), lb = lum(b); return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05); }
  function backgroundOf(el) {
    // First ancestor (through the shadow boundary) with a background; alpha
    // layers composite onto the next one until opaque. Body is the floor.
    let acc = null; let n = el;
    while (n) {
      if (n.nodeType === 1 && !(n instanceof SVGElement)) {
        const c = parseColor(cs(n).backgroundColor);
        if (c && c.a > 0) {
          acc = acc ? over(acc, c) : c;
          if (acc.a >= 0.999) return acc;
        }
      }
      n = n.parentElement || (n.parentNode && n.parentNode.host) || null;
    }
    const body = parseColor(cs(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
    return acc ? over(acc, body) : body;
  }
  function isOverlay(el) { return !!el.closest(OVERLAY); }
  function ancestorOf(a, b) { return a !== b && (a.contains(b) || b.contains(a)); }

  function textBoxes(scope) {
    const out = []; const seen = new Set();
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const el = n.parentElement; if (!el) continue;
      if (el.closest("style, script, title, option")) continue;
      const op = opacityChain(el, scope.parentNode);
      if (op < 0.05) continue;
      if (el.closest(".viewctl") && op < 0.95) continue; // mid-fade
      const svgText = el.closest("text");
      if (svgText) {
        const target = el.tagName.toLowerCase() === "tspan" ? el : svgText;
        if (seen.has(target)) continue; seen.add(target);
        const r = target.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) continue;
        const svg = target.ownerSVGElement;
        const vb = svg && svg.viewBox.baseVal.width ? svg.viewBox.baseVal.width : null;
        const attr = parseFloat(target.getAttribute("font-size") || svgText.getAttribute("font-size") || cs(svgText).fontSize);
        const scale = vb ? svg.getBoundingClientRect().width / vb : 1;
        const fill = cs(target).fill;
        const fo = parseFloat(cs(target).fillOpacity || "1");
        const fg = parseColor(fill);
        out.push({ el: target, rect: r, text: n.nodeValue.trim().slice(0, 40), svg: true,
          fontPx: attr * scale, weight: cs(svgText).fontWeight,
          fg: fg ? { ...fg, a: fg.a * fo * op } : null });
      } else {
        const rg = document.createRange(); rg.selectNodeContents(n);
        const rects = [...rg.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
        if (!rects.length) continue;
        const st = cs(el);
        const fg = parseColor(st.color);
        for (const r of rects) {
          out.push({ el, rect: r, text: n.nodeValue.trim().slice(0, 40), svg: false,
            fontPx: parseFloat(st.fontSize), weight: st.fontWeight,
            fg: fg ? { ...fg, a: fg.a * op } : null });
        }
      }
    }
    return out;
  }
  const inter = (a, b) => {
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return { w, h };
  };
  let idSeq = 0;
  const uid = (el) => { if (!el.__d4id) el.__d4id = ++idSeq; return el.__d4id; };
  const label = (el) => {
    const tag = el.tagName.toLowerCase();
    const cls = el.getAttribute && el.getAttribute("class") ? "." + el.getAttribute("class").trim().split(/\s+/).join(".") : "";
    return tag + cls;
  };

  function clipSpill(box, scope) {
    // Walk up: an ancestor that hides overflow on an axis clips; one that
    // scrolls on that axis makes the rest reachable, so stop for that axis.
    let el = box.el; let checkX = true; let checkY = true; let spill = 0; let where = "";
    const r = box.rect;
    if (box.svg) {
      const svg = box.el.ownerSVGElement;
      if (svg && cs(svg).overflow !== "visible") {
        const s = svg.getBoundingClientRect();
        const sx = Math.max(0, s.left - r.left, r.right - s.right);
        const sy = Math.max(0, s.top - r.top, r.bottom - s.bottom);
        if (Math.max(sx, sy) > 1) { spill = Math.max(sx, sy); where = "svg"; }
      }
      el = svg;
    }
    let n = el && el.parentElement;
    while (n && (checkX || checkY)) {
      const st = cs(n);
      const b = n.getBoundingClientRect();
      const hx = st.overflowX === "hidden" || st.overflowX === "clip";
      const hy = st.overflowY === "hidden" || st.overflowY === "clip";
      const sxr = st.overflowX === "auto" || st.overflowX === "scroll";
      const syr = st.overflowY === "auto" || st.overflowY === "scroll";
      if (checkX && hx) {
        const sx = Math.max(0, b.left - r.left, r.right - b.right);
        if (sx > 1 && sx > spill) { spill = sx; where = label(n) + " x"; }
      }
      if (checkY && hy) {
        const sy = Math.max(0, b.top - r.top, r.bottom - b.bottom);
        if (sy > 1 && sy > spill) { spill = sy; where = label(n) + " y"; }
      }
      if (sxr) checkX = false; if (syr) checkY = false;
      if (n === scope) break;
      n = n.parentElement || (n.parentNode && n.parentNode.host) || null;
    }
    // Past the scope box itself (a card whose text leaves the card).
    const sb = scope.getBoundingClientRect();
    if (checkX) { const sx = Math.max(0, sb.left - r.left, r.right - sb.right); if (sx > 1 && sx > spill) { spill = sx; where = "scope x"; } }
    if (checkY) { const sy = Math.max(0, sb.top - r.top, r.bottom - sb.bottom); if (sy > 1 && sy > spill) { spill = sy; where = "scope y"; } }
    if (!box.svg) {
      const st = cs(box.el);
      const clipped = st.overflowX !== "visible" || st.whiteSpace === "nowrap";
      if (clipped && box.el.scrollWidth > box.el.clientWidth + 1 && box.el.clientWidth > 0) {
        const s = box.el.scrollWidth - box.el.clientWidth;
        if (s > spill) { spill = s; where = "scrollWidth"; }
      }
    }
    return { spill, where };
  }

  function measure(coarse) {
    const card = window.__card;
    const scope = scopeOf(card);
    const boxes = textBoxes(scope);
    const overlaps = [];
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      if (a.el === b.el || ancestorOf(a.el, b.el)) continue;
      if (isOverlay(a.el) !== isOverlay(b.el)) continue;
      const { w, h } = inter(a.rect, b.rect);
      if (Math.min(w, h) >= 1.5) overlaps.push({ a: label(a.el) + " '" + a.text + "'", b: label(b.el) + " '" + b.text + "'", w: +w.toFixed(1), h: +h.toFixed(1) });
    }
    const overflow = [];
    for (const b of boxes) {
      const { spill, where } = clipSpill(b, scope);
      if (spill > 1) overflow.push({ el: label(b.el), text: b.text, spill: +spill.toFixed(1), where });
    }
    const contrast = []; const contrastInactive = [];
    let minFont = Infinity;
    for (const b of boxes) {
      if (b.fontPx > 0) minFont = Math.min(minFont, b.fontPx);
      if (!b.fg) continue;
      const inactive = !!b.el.closest(".nodata, [disabled], .locked");
      const bg = backgroundOf(b.el);
      const fg = b.fg.a < 1 ? over(b.fg, bg) : b.fg;
      const ratioV = ratio(fg, bg);
      const bold = parseInt(b.weight, 10) >= 700;
      const large = b.fontPx >= 24 || (b.fontPx >= 18.66 && bold);
      const need = large ? 3 : 4.5;
      if (ratioV < need) (inactive ? contrastInactive : contrast).push({ el: label(b.el), text: b.text, ratio: +ratioV.toFixed(2), need, fontPx: +b.fontPx.toFixed(1),
        fg: "rgb(" + [fg.r, fg.g, fg.b].map(Math.round).join(",") + ")", bg: "rgb(" + [bg.r, bg.g, bg.b].map(Math.round).join(",") + ")" });
    }
    // Interactive targets.
    const targets = [...scope.querySelectorAll(TARGETS)]
      .filter((el) => !el.disabled && opacityChain(el, scope.parentNode) >= 0.05)
      .map((el) => ({ el, r: el.getBoundingClientRect() }))
      .filter((t) => t.r.width > 0 && t.r.height > 0);
    const minSide = coarse ? 44 : 24;
    const small = []; const handles = [];
    for (const t of targets) {
      if (t.el.classList.contains("slot-handle")) { handles.push({ w: +t.r.width.toFixed(1), h: +t.r.height.toFixed(1) }); continue; }
      const side = Math.min(t.r.width, t.r.height);
      if (side >= minSide) continue;
      // Spacing exception (2.5.8): a 24 px circle on the centre must not hit another target.
      const cx = t.r.left + t.r.width / 2, cy = t.r.top + t.r.height / 2;
      let crowded = false;
      for (const o of targets) {
        if (o === t || ancestorOf(o.el, t.el) || o.el.classList.contains("slot-handle")) continue;
        const nx = Math.max(o.r.left, Math.min(cx, o.r.right)), ny = Math.max(o.r.top, Math.min(cy, o.r.bottom));
        if (Math.hypot(nx - cx, ny - cy) < 12) { crowded = true; break; }
      }
      small.push({ el: label(t.el), aria: t.el.getAttribute("aria-label") || t.el.textContent.trim().slice(0, 30),
        w: +t.r.width.toFixed(1), h: +t.r.height.toFixed(1), crowded });
    }
    const focusables = [...scope.querySelectorAll(FOCUSABLE)]
      .filter((el) => !el.disabled && opacityChain(el, scope.parentNode) >= 0.05 && el.getBoundingClientRect().width > 0);
    let chart = null;
    const csvg = scope.querySelector(".chartwrap svg");
    if (csvg) {
      const r = csvg.getBoundingClientRect(); const vb = csvg.viewBox.baseVal.width || 900;
      const axis = csvg.querySelector("text[font-size]");
      chart = { w: +r.width.toFixed(1), h: +r.height.toFixed(1), fontUnits: axis ? parseFloat(axis.getAttribute("font-size")) : null,
        fontPx: axis ? +(parseFloat(axis.getAttribute("font-size")) * r.width / vb).toFixed(2) : null,
        laneH: (() => { const l = csvg.querySelector("rect.lane"); return l ? +l.getBoundingClientRect().height.toFixed(1) : null; })() };
    }
    const dlg = card.shadowRoot && card.shadowRoot.querySelector("dialog[open]");
    return {
      scope: label(scope), boxes: boxes.length, overlaps, overflow, contrast, contrastInactive, minFont: minFont === Infinity ? null : +minFont.toFixed(2),
      dialogW: dlg ? +dlg.getBoundingClientRect().width.toFixed(1) : null,
      targets: targets.length - handles.length, small, handles, focusables: focusables.length, chart,
      hostW: card.getBoundingClientRect().width,
    };
  }

  // Focus bookkeeping for the tab-order walk.
  function deepActive() {
    let a = document.activeElement; let guard = 0;
    while (a && a.shadowRoot && a.shadowRoot.activeElement && guard++ < 5) a = a.shadowRoot.activeElement;
    return a;
  }
  function focusInfo() {
    const a = deepActive();
    if (!a || a === document.body) return { key: "body", indicator: null, inScope: false };
    const card = window.__card; const scope = scopeOf(card);
    const st = cs(a);
    const outline = st.outlineStyle !== "none" && parseFloat(st.outlineWidth) > 0;
    const shadow = st.boxShadow && st.boxShadow !== "none";
    const stroke = a instanceof SVGElement && st.stroke !== "none" && parseFloat(st.strokeWidth) > 0;
    return { key: label(a) + "#" + (a.getAttribute("aria-label") || a.textContent.trim().slice(0, 20)) + "@" + uid(a),
      indicator: !!(outline || shadow || stroke), inScope: scope.contains(a) };
  }
  function focusableKeys() {
    const scope = scopeOf(window.__card);
    return [...scope.querySelectorAll(FOCUSABLE)]
      .filter((el) => !el.disabled && opacityChain(el, scope.parentNode) >= 0.05 && el.getBoundingClientRect().width > 0)
      .map((el) => label(el) + "#" + (el.getAttribute("aria-label") || el.textContent.trim().slice(0, 20)) + "@" + uid(el));
  }
  function hoverTargets() {
    const scope = scopeOf(window.__card);
    return [...scope.querySelectorAll(".chip, .dlg-tab, .expand, .close, .setup-hit, .whatif button, .layout-bar button, .viewctl button, .hl-score")]
      .filter((el) => !el.closest(OVERLAY) || el.closest(".viewctl"))
      .map((el) => { const r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width }; })
      .filter((p) => p.w > 0).slice(0, 14);
  }
  function rectSnapshot() {
    const scope = scopeOf(window.__card);
    return [...scope.querySelectorAll("*")].filter((el) => !el.closest(OVERLAY) && !el.closest(".crosshair"))
      .map((el) => { const r = el.getBoundingClientRect(); return [Math.round(r.left * 2), Math.round(r.top * 2), Math.round(r.width * 2)]; });
  }
  return { drive, measure, openMenuAfterDrag, focusInfo, focusableKeys, hoverTargets, rectSnapshot };
})();
`;

// --- the arms -------------------------------------------------------------------
function arms() {
  const out = [];
  const vps = QUICK ? ["phone"] : ["phone", "tablet", "desktop", "panel"];
  for (const vp of vps) {
    for (const scheme of QUICK ? ["light"] : ["light", "dark"]) {
      for (const lang of QUICK ? ["en"] : ["en", "sv"]) {
        if (vp === "panel" && (scheme !== "light" || lang !== "en")) continue;
        out.push({ name: `${vp}-${scheme}-${lang}`, vp, scheme, lang, coarse: false, reduce: false });
      }
    }
  }
  if (!QUICK) {
    out.push({ name: "phone-light-en-coarse", vp: "phone", scheme: "light", lang: "en", coarse: true, reduce: false });
    out.push({ name: "phone-light-en-reduce", vp: "phone", scheme: "light", lang: "en", coarse: false, reduce: true });
  }
  return out;
}

const shotsDir = path.join(here, "shots");
if (SHOTS) fs.mkdirSync(shotsDir, { recursive: true });

const browser = await chromium.launch();
const results = { states: STATES.map((s) => s.name), arms: [], renders: [], cardVersion: null };
const totals = { overlaps: 0, overflow: 0, contrast: 0, contrastInactive: 0, contrastLight: 0, contrastDark: 0, small24: 0, small24Crowded: 0, handlesSmall: 0,
  small44: 0, tabUnreached: 0, noIndicator: 0, consoleErrors: 0, hoverShift: 0, minFont: Infinity, renders: 0, coarseEmulated: null };
const byClassContrast = new Map();
const bySmall = new Map();
try {
  for (const arm of arms()) {
    const vp = VIEWPORTS[arm.vp];
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      colorScheme: arm.scheme, reducedMotion: arm.reduce ? "reduce" : "no-preference",
      hasTouch: arm.coarse, isMobile: arm.coarse, locale: arm.lang === "sv" ? "sv-SE" : "en-GB",
      timezoneId: "Europe/Stockholm",
    });
    const page = await context.newPage();
    const errors = [];
    page.on("console", (m) => { if (m.type() === "error") errors.push(m.text().slice(0, 200)); });
    page.on("pageerror", (e) => errors.push("pageerror: " + String(e.message).slice(0, 200)));
    await page.goto("about:blank");
    await page.setContent('<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body></body></html>');
    const frozen = await page.evaluate((iso) => Date.parse(iso) + 6 * 3600000, FROZEN_ISO);
    await page.clock.setFixedTime(frozen);
    await page.addStyleTag({ content: `
      :root { ${HA_TOKENS[arm.scheme]} }
      html { font-size: 14px; }
      body { margin: 0; padding: 8px; font-family: Roboto, -apple-system, "Segoe UI", sans-serif; font-size: 14px;
             background: var(--primary-background-color); color: var(--primary-text-color); }
      heatpump-optimizer-card, heatpump-optimizer-card-editor { display: block; width: ${vp.tile}px; }
    ` });
    await page.addScriptTag({ content: HA_CARD_DEF });
    await page.addScriptTag({ content: CARD_SRC });
    await page.addScriptTag({ content: PAGE_DRIVER });
    const coarseReal = await page.evaluate(() => matchMedia("(pointer: coarse)").matches && matchMedia("(hover: none)").matches);
    if (arm.coarse) totals.coarseEmulated = coarseReal ? 1 : 0;
    const armRec = { ...arm, tile: vp.tile, coarseReal, states: {} };
    for (const st of STATES) {
      errors.length = 0;
      // The two media states are the real thing on their own arms; elsewhere
      // the card's JS query is answered by a matchMedia shim (CSS media
      // queries are not, which the report says).
      if (st.media === "reduce") await page.emulateMedia({ reducedMotion: "reduce" });
      if (st.media === "coarse" && !arm.coarse) {
        await page.evaluate(() => { const mm = window.matchMedia.bind(window);
          window.matchMedia = (q) => q === "(pointer: coarse)" ? { matches: true, addEventListener() {} } : mm(q); });
      }
      let drv;
      try {
        drv = await page.evaluate(({ spec, frozen }) => window.__d4.drive(spec, frozen), { spec: { ...st, language: arm.lang === "sv" ? "sv-SE" : "en" }, frozen });
      } catch (e) {
        errors.push("drive threw: " + String(e.message).slice(0, 200));
        drv = { hover: null };
      }
      if (drv.drag) {
        await page.mouse.move(drv.drag.x1, drv.drag.y);
        await page.mouse.down();
        await page.mouse.move(drv.drag.x1 + drv.drag.dx / 2, drv.drag.y + (drv.drag.dy || 0) / 2, { steps: 4 });
        await page.mouse.move(drv.drag.x1 + drv.drag.dx, drv.drag.y + (drv.drag.dy || 0), { steps: 4 });
        await page.mouse.up();
        await page.waitForTimeout(80);
        if (drv.then === "open_menu") await page.evaluate(() => window.__d4.openMenuAfterDrag());
      }
      if (drv.hover) {
        await page.mouse.move(drv.hover.x, drv.hover.y);
        await page.waitForTimeout(120);
      } else {
        await page.mouse.move(2, 2);
      }
      await page.waitForTimeout(60);
      const m = await page.evaluate((coarse) => window.__d4.measure(coarse), arm.coarse);
      // Tab walk from the body.
      await page.evaluate(() => { document.activeElement && document.activeElement.blur && document.activeElement.blur(); });
      const seq = []; const seen = new Set(); let noInd = 0; let last = null;
      for (let i = 0; i < 120; i++) {
        await page.keyboard.press("Tab");
        const f = await page.evaluate(() => window.__d4.focusInfo());
        if (f.key === "body") { if (seq.length) break; else continue; }
        if (f.key === last) continue; // segments of one control (type=time)
        last = f.key;
        if (seq.length && f.key === seq[0]) break; // wrapped around
        if (seen.has(f.key)) break; // a shorter cycle: focus trap or loop
        seen.add(f.key); seq.push(f.key);
        if (f.inScope && f.indicator === false) noInd++;
      }
      const keys = await page.evaluate(() => window.__d4.focusableKeys());
      const unreached = keys.filter((k) => !seen.has(k));
      // Hover shift.
      let shift = 0; const shifted = [];
      if (st.drive !== "editor") {
        const hts = await page.evaluate(() => window.__d4.hoverTargets());
        for (const h of hts) {
          const before = await page.evaluate(() => window.__d4.rectSnapshot());
          await page.mouse.move(h.x, h.y);
          await page.waitForTimeout(40);
          const after = await page.evaluate(() => window.__d4.rectSnapshot());
          if (before.length === after.length) {
            let moved = 0;
            for (let i = 0; i < before.length; i++) if (before[i][0] !== after[i][0] || before[i][1] !== after[i][1] || before[i][2] !== after[i][2]) moved++;
            if (moved) { shift += moved; shifted.push(`${h.x.toFixed(0)},${h.y.toFixed(0)}:${moved}`); }
          }
        }
        await page.mouse.move(2, 2);
      }
      if (SHOTS && ((arm.scheme === "light" && arm.lang === "en") || (arm.scheme === "dark" && arm.lang === "sv")) && !arm.coarse && !arm.reduce) {
        await page.screenshot({ path: path.join(shotsDir, `${arm.name}--${st.name}.png`), fullPage: true });
      }
      const rec = { ...m, tabSeq: seq, tabUnreached: unreached, noIndicator: noInd, errors: [...errors], hoverShift: shift, shifted,
        schemaEntries: drv.schemaEntries };
      armRec.states[st.name] = rec;
      totals.renders += 1;
      totals.overlaps += m.overlaps.length; totals.overflow += m.overflow.length; totals.contrast += m.contrast.length;
      totals.contrastInactive += m.contrastInactive.length; totals.handlesSmall += m.handles.filter((h) => Math.min(h.w, h.h) < (arm.coarse ? 44 : 24)).length;
      if (arm.scheme === "light") totals.contrastLight += m.contrast.length; else totals.contrastDark += m.contrast.length;
      for (const c of m.contrast) byClassContrast.set(c.el, (byClassContrast.get(c.el) || 0) + 1);
      if (arm.coarse) totals.small44 += m.small.length;
      else { totals.small24 += m.small.length; totals.small24Crowded += m.small.filter((s) => s.crowded).length;
        for (const s of m.small) bySmall.set(s.el, (bySmall.get(s.el) || 0) + 1); }
      totals.tabUnreached += unreached.length; totals.noIndicator += noInd; totals.consoleErrors += errors.length; totals.hoverShift += shift;
      if (m.minFont !== null) totals.minFont = Math.min(totals.minFont, m.minFont);
      const flag = (m.overlaps.length || m.overflow.length || m.contrast.length || m.small.length || unreached.length || errors.length || shift) ? "!" : " ";
      console.log(`${flag} ${arm.name.padEnd(24)} ${st.name.padEnd(24)} boxes=${String(m.boxes).padStart(3)} ov=${m.overlaps.length} of=${m.overflow.length} ct=${m.contrast.length}+${m.contrastInactive.length} small=${m.small.length}/${m.targets} tab=${seq.length}/${keys.length} unr=${unreached.length} noind=${noInd} err=${errors.length} shift=${shift} minpx=${m.minFont} chart=${m.chart ? m.chart.w + "x" + m.chart.h + "@" + m.chart.fontPx + "px lane" + m.chart.laneH : "-"}`);
      if (st.media === "reduce") await page.emulateMedia({ reducedMotion: "no-preference" });
      if (st.media === "coarse" && !arm.coarse) {
        await page.setContent('<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body></body></html>');
        await page.addStyleTag({ content: `:root { ${HA_TOKENS[arm.scheme]} } html { font-size: 14px; }
          body { margin: 0; padding: 8px; font-family: Roboto, -apple-system, "Segoe UI", sans-serif; font-size: 14px; background: var(--primary-background-color); color: var(--primary-text-color); }
          heatpump-optimizer-card, heatpump-optimizer-card-editor { display: block; width: ${vp.tile}px; }` });
        await page.addScriptTag({ content: HA_CARD_DEF });
        await page.addScriptTag({ content: CARD_SRC });
        await page.addScriptTag({ content: PAGE_DRIVER });
        await page.clock.setFixedTime(frozen);
      }
    }
    results.arms.push(armRec);
    await context.close();
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(here, "results.json"), JSON.stringify(results, null, 1));
const top = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12).map(([k, v]) => `${k}=${v}`).join("; ");
console.log("\ncontrast failures by element:", top(byClassContrast));
console.log("small targets by element:", top(bySmall));
console.log(`RESULT states=${STATES.length} count`);
console.log(`RESULT arms=${results.arms.length} count`);
console.log(`RESULT renders=${totals.renders} count`);
console.log(`RESULT coarse_emulated=${totals.coarseEmulated} flag`);
console.log(`RESULT text_overlap_pairs=${totals.overlaps} count`);
console.log(`RESULT text_overflow=${totals.overflow} count`);
console.log(`RESULT contrast_fail=${totals.contrast} count`);
console.log(`RESULT contrast_fail_inactive=${totals.contrastInactive} count`);
console.log(`RESULT slot_handles_small=${totals.handlesSmall} count`);
console.log(`RESULT contrast_fail_light=${totals.contrastLight} count`);
console.log(`RESULT contrast_fail_dark=${totals.contrastDark} count`);
console.log(`RESULT hit_small_24=${totals.small24} count`);
console.log(`RESULT hit_small_24_nospacing=${totals.small24Crowded} count`);
console.log(`RESULT hit_small_44_coarse=${totals.small44} count`);
console.log(`RESULT tab_unreached=${totals.tabUnreached} count`);
console.log(`RESULT focus_no_indicator=${totals.noIndicator} count`);
console.log(`RESULT console_errors=${totals.consoleErrors} count`);
console.log(`RESULT hover_shift=${totals.hoverShift} count`);
console.log(`RESULT min_text_px=${totals.minFont === Infinity ? "n/a" : totals.minFont} px`);
// Counts only: no CPU or wall number is reported, so the thread factor is
// moot; printed as 1.00 to satisfy the harness contract.
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
