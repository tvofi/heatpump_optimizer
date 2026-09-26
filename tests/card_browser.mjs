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
//
// B12 (#558): this lane also takes the README hero. CI never writes the
// committed PNG (Chromium raster is not bit-stable across machines).
// Regenerate after a card change that should move the picture:
//
//   HPO_HERO_OUT=docs/img/card-plan-chart.png node tests/card_browser.mjs
import { strict as assert } from "node:assert";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

// createRequire, not a static import: the lane must resolve playwright
// from wherever the CI job or developer put it (a bare `import` would
// demand node_modules inside the repository, which this repo does not
// have and should not grow for one lane).
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
import {
  DEFAULT_SPACE, DEFAULT_DHW, HOUR, planStates, setupSensorStates, qaTopologies, withActuals, layoutCatalogTopo,
} from "./card_rig.mjs";


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
const SPACE_ID = "sensor.heat_pump_optimizer_plan_space_heating";
const DHW_ID = "sensor.heat_pump_optimizer_plan_dhw_heating";

let fails = 0;
function check(name, cond, detail = "") {
  console.log((cond ? "  ok  " : "  FAIL") + "  " + name);
  if (!cond) { if (detail) console.log("        " + detail); fails += 1; }
}

// ---- P9 class barrier ------------------------------------------------------
// P9 class barrier (prototype): the rendered-property rules over a state grid.
//
// Every earlier P9 witness in tests/card_browser.mjs is keyed to the instance
// that produced it: a REQUIRED list of four contrast selectors, a unit regex
// that omits SEK/kWh, one hover row. Round 9 found five more instances at
// selectors and states none of them named. This block asserts the PROPERTY
// over every rendered node instead, in every cell of a grid, and a REACH rule
// that fails when the card styles a colour no cell renders -- so a new status
// class cannot ship unmeasured by being absent from the grid.
//
// Prototype carried from the round-9 P9 RCA seat (handoff/r9-rca-p9) for F6.3.
// HA's default theme tokens, including the status colours the card reads.
const THEMES = {
  light: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#212121;--secondary-text-color:#727272;
    --text-primary-color:#ffffff;--disabled-text-color:#bdbdbd;--primary-background-color:#fafafa;--secondary-background-color:#e5e5e5;
    --card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
  dark: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;
    --text-primary-color:#ffffff;--disabled-text-color:#6f6f6f;--primary-background-color:#111111;--secondary-background-color:#282828;
    --card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
};
const VIEWPORTS = [[375, 812], [768, 1024], [1280, 800]];

function gridStates(plan) {
  const scheduleStates = () => {
    const st = planStates(plan);
    st[DEFAULT_SPACE].attributes.day_start_hour = 7;
    st[DEFAULT_SPACE].attributes.day_end_hour = 22;
    st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
    return st;
  };
  const setupStates = (topo, extra) => {
    const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
    st[DEFAULT_SPACE].attributes.setup_topology = topo;
    return st;
  };
  // Two sensors sharing a friendly name: the picker must tell them apart.
  const twins = () => {
    const st = {};
    for (let i = 0; i < 40; i++) {
      st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = { state: "20.0",
        attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` } };
    }
    for (const [id, v] of [["sensor.vedpanna_temperatur_temperature", "71.2"], ["sensor.vedpanna_temperatur_temperature_2", "48.9"]]) {
      st[id] = { state: v, attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
    }
    return st;
  };
  const clamped = () => {
    const st = scheduleStates();
    for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) {
      st[id].attributes.dhw_min_temperature = 55; st[id].attributes.dhw_min_temperature_max = 60;
    }
    return st;
  };
  const wi = { what_if: true };
  const statStates = () => ({
    "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
    "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
    "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
    "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
      lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
  });
  const shared = () => {
    const st = planStates(plan);
    const heating = new Set(st[DEFAULT_SPACE].attributes.forecast.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
    st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) => heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
    return st;
  };
  const wood = (fuel) => { const st = planStates(plan); st[DEFAULT_SPACE].attributes.wood_fuel = fuel; return st; };
  const away = ({ sw = false, resolved = false } = {}) => {
    const st = planStates(plan);
    st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
    st["datetime.heat_pump_optimizer_away_return"] = { state: "unknown", attributes: {} };
    st["binary_sensor.heat_pump_optimizer_away_mode"] = { state: resolved ? "on" : "off",
      attributes: { source: resolved && !sw ? "person.alice" : "none" } };
    return st;
  };
  const override = () => {
    const st = planStates(plan);
    const at = Date.parse(plan.dhw_plan.forecast[0].t) + 11 * HOUR;
    const info = { active: true, expires_at: new Date(at).toISOString(), space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
    st[DEFAULT_SPACE].attributes.manual_override = info; st[DEFAULT_DHW].attributes.manual_override = info;
    return st;
  };
  const advisor = () => {
    const st = setupStates(qaTopologies().base);
    st[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: [
      { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13, parameters: ["buffer_cooling_rate"], priced: true },
      { key: "dhw_temp_entity", label: "Hot water temperature", priced: false, reason: "no_clamped_parameter" },
    ] };
    return st;
  };
  const S = (name, o) => ({ name, config: {}, steps: [], service: false, ...o });
  return [
    S("live_default", { states: withActuals(planStates(plan)) }),
    S("live_default_expanded", { states: withActuals(planStates(plan)), steps: [["cardClick"]] }),
    S("draft_menu_open", { states: planStates(plan), config: wi, steps: [["cardClick"], ["dragDhw"], ["menuAt", "space", 0.1]] }),
    S("menu_right_edge", { states: planStates(plan), config: wi, steps: [["cardClick"], ["menuAt", "space", 0.97]] }),
    S("menu_right_edge_dhw", { states: planStates(plan), config: wi, steps: [["cardClick"], ["menuAt", "dhw", 0.97]] }),
    S("pin_ok", { states: planStates(plan), config: wi, service: "ok", steps: [["cardClick"], ["dragDhw"], ["clickSel", ".wi-pin"]] }),
    S("pin_fail", { states: planStates(plan), config: wi, service: "fail", steps: [["cardClick"], ["dragDhw"], ["clickSel", ".wi-pin"]] }),
    S("save_confirm", { states: scheduleStates(), config: wi, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"]] }),
    S("save_ok", { states: scheduleStates(), config: wi, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
    S("save_fail", { states: scheduleStates(), config: wi, service: "fail", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
    S("dhw_clamped", { states: clamped(), config: wi, steps: [["cardClick"], ["lowerCeiling", 50]] }),
    S("no_plan", { states: {} }),
    S("no_plan_expanded", { states: {}, steps: [["open"]] }),
    S("score_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "score"]] }),
    S("savings_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "savings"]] }),
    S("hidden_series", { states: planStates(plan), config: { series: { outdoor: false, solar: false } }, steps: [["chip", "price"]] }),
    S("tooltip_hover", { states: planStates(plan), steps: [["cardClick"], ["hover", 5]] }),
    S("override_active", { states: override(), config: wi, steps: [["open"]] }),
    S("wood_alert", { states: wood({ cheaper: true, show_whatif: true, ready: true, slots: [] }) }),
    S("wood_lane", { states: wood({ cheaper: false, show_whatif: true, ready: true, slots: [{ start: plan.space_plan.forecast[0].t,
      end: plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t, source: "detected" }] }) }),
    S("away_return", { states: away({ sw: true }), steps: [["cardClick"]] }),
    S("away_status", { states: away({ resolved: true }), steps: [["cardClick"]] }),
    S("setup_two_tank", { states: setupStates(qaTopologies().twoTank), steps: [["cardClick"], ["page", "setup"]] }),
    S("advisor_page", { states: advisor(), steps: [["cardClick"], ["page", "advisor"]] }),
    S("savings_page", { states: { ...planStates(plan), "sensor.heat_pump_optimizer_plan_monthly_savings": { state: "8.1",
      attributes: { unit_of_measurement: "SEK", savings_months: [
        { month: "2026-01", baseline_sek: 900, actual_sek: 820, savings_sek: 80, savings_pct: 8.9, estimated: true },
        { month: "2025-12", baseline_sek: 700, actual_sek: 712, savings_sek: -12, savings_pct: -1.7 }] } } },
      steps: [["cardClick"], ["page", "savings"]] }),
    S("estimated_price_hover", { states: (() => { const st = planStates(plan);
      for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) st[id].attributes.forecast = st[id].attributes.forecast.map((p) => ({ ...p, price_known: false }));
      return st; })(), steps: [["cardClick"], ["hover", 3]] }),
    S("shared_steps_hover", { states: shared(), steps: [["cardClick"], ["hoverShared"]] }),
    S("view_limit", { states: planStates(plan), config: wi, steps: [["cardClick"], ["zoom", 0.25]] }),
    S("layout_editing", { states: setupStates(layoutCatalogTopo()), steps: [["cardClick"], ["page", "setup"], ["clickSel", ".layout-edit-toggle"]] }),
    S("setup_clear_armed", { states: setupStates(qaTopologies().base), steps: [["cardClick"], ["page", "setup"], ["armClear"]] }),
    S("picker_twins", { states: setupStates(qaTopologies().base, twins()), steps: [["cardClick"], ["page", "setup"], ["picker", "vedpanna"]] }),
  ];
}

// ---- the in-page instrument (serialised into the page) ---------------------
function instrument() {
  const H = {};
  window.__p9 = H;
  const parseColor = (s) => {
    if (!s || s === "none" || s === "transparent") return null;
    let m = s.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)$/);
    if (m) return [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : +m[4])];
    m = s.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)$/);
    if (m) return [m[1] * 255, m[2] * 255, m[3] * 255, m[4] === undefined ? 1 : +m[4]];
    return undefined;
  };
  const over = (top, a, bottom) => [0, 1, 2].map((i) => top[i] * a + bottom[i] * (1 - a));
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const effOpacity = (el) => { let o = 1; for (let n = el; n; n = parentOf(n)) o *= parseFloat(getComputedStyle(n).opacity || "1"); return o; };
  const visible = (el) => {
    if (!el.getClientRects || !el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility !== "visible" || cs.display === "none") return false;
    if (el.closest && el.closest("defs, pattern, clipPath, mask, marker, symbol, title")) return false;
    return effOpacity(el) > 0.02;
  };
  const desc = (el) => {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    return (el.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "")).slice(0, 60);
  };
  const card = () => document.querySelector("heatpump-optimizer-card");
  const root = () => card().shadowRoot;
  const scope = () => { const d = root().querySelector("dialog[open]"); return d && d.matches(":modal") ? d : root(); };
  const allEls = () => [...scope().querySelectorAll("*")];

  const textRuns = () => {
    const runs = [];
    for (const el of allEls()) {
      const isSvg = el instanceof SVGElement;
      if (isSvg && el.tagName.toLowerCase() !== "text") continue;
      if (!isSvg && ["STYLE", "SCRIPT", "TITLE", "OPTION"].includes(el.tagName)) continue;
      if (!visible(el)) continue;
      let txt, rect;
      if (isSvg) {
        txt = (el.textContent || "").replace(/\s+/g, " ").trim();
        rect = el.getBoundingClientRect();
      } else {
        const rs = [];
        txt = "";
        for (const tn of el.childNodes) {
          if (tn.nodeType !== 3 || !tn.textContent.trim()) continue;
          txt += tn.textContent;
          const r = document.createRange(); r.selectNodeContents(tn); rs.push(...r.getClientRects());
        }
        txt = txt.replace(/\s+/g, " ").trim();
        if (!rs.length) continue;
        const l = Math.min(...rs.map((r) => r.left)), t = Math.min(...rs.map((r) => r.top));
        const r = Math.max(...rs.map((r) => r.right)), b = Math.max(...rs.map((r) => r.bottom));
        rect = { left: l, top: t, right: r, bottom: b, width: r - l, height: b - t };
      }
      if (!txt || rect.width < 0.5 || rect.height < 0.5) continue;
      runs.push({ el, txt, rect, isSvg });
    }
    return runs;
  };
  // Ink a clipping ancestor hides and cannot scroll to.
  const unreachable = (run) => {
    let worst = 0;
    for (const axis of ["x", "y"]) {
      for (let n = parentOf(run.el); n && n !== document.documentElement; n = parentOf(n)) {
        const cs = getComputedStyle(n);
        const o = axis === "x" ? cs.overflowX : cs.overflowY;
        if (o === "visible") continue;
        const r = n.getBoundingClientRect();
        const scroll = o === "auto" || o === "scroll";
        const [a0, a1, c0, c1, eA, eB] = axis === "x"
          ? [run.rect.left, run.rect.right, r.left, r.right, scroll ? n.scrollLeft : 0, scroll ? n.scrollWidth - n.clientWidth - n.scrollLeft : 0]
          : [run.rect.top, run.rect.bottom, r.top, r.bottom, scroll ? n.scrollTop : 0, scroll ? n.scrollHeight - n.clientHeight - n.scrollTop : 0];
        worst = Math.max(worst, (c0 - eA) - a0, a1 - (c1 + eB));
        break;
      }
    }
    return worst;
  };
  const inShape = (sh, x, y) => {
    try { const m = sh.getScreenCTM(); if (m && sh.isPointInFill) return sh.isPointInFill(new DOMPoint(x, y).matrixTransform(m.inverse())); } catch (e) { /* fall through */ }
    const r = sh.getBoundingClientRect(); return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  };
  const bgAt = (el, x, y) => {
    const chain = []; for (let n = el; n; n = parentOf(n)) chain.push(n); chain.reverse();
    let bg = [255, 255, 255];
    for (const n of chain) {
      if (n instanceof SVGElement) continue;
      const c = parseColor(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0) bg = over(c, c[3] * effOpacity(n), bg);
    }
    let svg = el instanceof SVGElement ? el.ownerSVGElement : null;
    while (svg && svg.ownerSVGElement) svg = svg.ownerSVGElement;
    if (svg) {
      for (const sh of svg.querySelectorAll("rect, path, circle, ellipse, polygon")) {
        if ((sh.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) === 0 || !visible(sh)) continue;
        const cs = getComputedStyle(sh);
        const c = parseColor(cs.fill);
        const a = parseFloat(cs.fillOpacity || "1") * effOpacity(sh);
        if (!c || a <= 0.01 || !inShape(sh, x, y)) continue;
        bg = over(c, c[3] * a, bg);
      }
    }
    return bg;
  };
  const contrastOf = (run) => {
    const cs = getComputedStyle(run.el);
    const fg = parseColor(run.isSvg ? cs.fill : cs.color);
    if (fg === null) return null;
    if (fg === undefined) return { unknown: true };
    const a = fg[3] * (run.isSvg ? parseFloat(cs.fillOpacity || "1") : 1) * effOpacity(run.el);
    const bg = bgAt(run.el, (run.rect.left + run.rect.right) / 2, (run.rect.top + run.rect.bottom) / 2);
    let px = parseFloat(cs.fontSize);
    if (run.isSvg) { const m = run.el.getScreenCTM(); if (m) px *= Math.hypot(m.a, m.b); }
    const large = px >= 24 || (parseInt(cs.fontWeight, 10) >= 700 && px >= 18.66);
    return { ratio: ratio(over(fg, a, bg), bg), need: large ? 3 : 4.5 };
  };
  const INTERACTIVE = "button, a[href], input:not([type=hidden]), select, textarea, summary, [role=button], [role=tab], [role=option], [role=menuitem], [tabindex]";
  const targets = () => allEls().filter((el) => {
    if (el.tagName === "HA-CARD" || el.tagName === "DIALOG" || !visible(el) || el.disabled) return false;
    if (getComputedStyle(el).pointerEvents === "none") return false;
    if (el.matches(INTERACTIVE) && !(el.getAttribute("tabindex") === "-1" && !el.matches("[role]"))) return true;
    if (getComputedStyle(el).cursor !== "pointer") return false;
    const p = parentOf(el); return !p || getComputedStyle(p).cursor !== "pointer";
  }).map((el) => { const r = el.getBoundingClientRect(); return { el, r, cx: (r.left + r.right) / 2, cy: (r.top + r.bottom) / 2 }; })
    .filter((t) => t.r.width >= 0.5 && t.r.height >= 0.5);

  H.measure = (coarse) => {
    const out = { runs: 0, contrast: [], unknownColour: 0, overflow: [], boxPairs: [], small: [], popups: [], options: [] };
    const runs = textRuns();
    out.runs = runs.length;
    runs.forEach((r, i) => r.el.setAttribute("data-p9run", String(i)));
    for (const run of runs) {
      const u = unreachable(run);
      if (u > 0.5) out.overflow.push(`${desc(run.el)} "${run.txt.slice(0, 30)}" ${u.toFixed(1)}px`);
      if (run.el.closest("[disabled], [aria-disabled='true']")) continue;
      const c = contrastOf(run);
      if (c && c.unknown) out.unknownColour += 1;
      else if (c && c.ratio + 1e-6 < c.need) out.contrast.push(`${desc(run.el)} "${run.txt.slice(0, 30)}" ${c.ratio.toFixed(2)}:1<${c.need}`);
    }
    // Candidate collisions: two text runs whose boxes intersect. Boxes are
    // line boxes; whether the GLYPHS touch is decided on pixels by the host.
    for (let i = 0; i < runs.length; i++) for (let j = i + 1; j < runs.length; j++) {
      const a = runs[i], b = runs[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      if (a.el.closest(".tooltip, .slot-menu, .setup-picker") || b.el.closest(".tooltip, .slot-menu, .setup-picker")) continue;
      const ix = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
      const iy = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
      if (ix <= 0.5 || iy <= 0.5) continue;
      if (a.txt === b.txt && Math.abs(a.rect.left - b.rect.left) < 0.6 && Math.abs(a.rect.top - b.rect.top) < 0.6) continue;
      const u = { x: Math.min(a.rect.left, b.rect.left) - 1, y: Math.min(a.rect.top, b.rect.top) - 1 };
      out.boxPairs.push({ a: i, b: j, at: `${desc(a.el)} "${a.txt.slice(0, 20)}"`, bt: `${desc(b.el)} "${b.txt.slice(0, 20)}"`,
        clip: { x: u.x, y: u.y, width: Math.max(a.rect.right, b.rect.right) + 1 - u.x, height: Math.max(a.rect.bottom, b.rect.bottom) + 1 - u.y } });
    }
    const ts = targets(), floor = coarse ? 44 : 24;
    for (const t of ts) {
      if (Math.min(t.r.width, t.r.height) >= floor - 0.05) continue;
      // WCAG 2.5.8's spacing exception: a 24 px circle on the centre clears every other target.
      const clash = ts.some((u) => u !== t && !u.el.contains(t.el) && !t.el.contains(u.el) &&
        (Math.min(u.r.width, u.r.height) < 23.95 ? Math.hypot(u.cx - t.cx, u.cy - t.cy) - 12
          : Math.hypot(Math.max(u.r.left - t.cx, 0, t.cx - u.r.right), Math.max(u.r.top - t.cy, 0, t.cy - u.r.bottom))) < 12);
      // A slot the card could not grow because its neighbours abut it on both
      // sides is the lane's accepted "boxed in" case (card_browser.mjs), not a defect.
      const abuts = (side) => ts.some((u) => u !== t && Math.min(u.r.bottom, t.r.bottom) - Math.max(u.r.top, t.r.top) > 1 &&
        (side < 0 ? Math.abs(u.r.right - t.r.left) < 1 : Math.abs(u.r.left - t.r.right) < 1));
      if (clash && !(abuts(-1) && abuts(1))) out.small.push(`${desc(t.el)} ${t.r.width.toFixed(1)}x${t.r.height.toFixed(1)}`);
    }
    // Every pop-up sits inside the viewport and inside the chart it belongs to.
    for (const p of scope().querySelectorAll(".tooltip, .slot-menu")) {
      if (!visible(p)) continue;
      const r = p.getBoundingClientRect(), host = p.closest(".chartwrap"), hr = host && host.getBoundingClientRect();
      const out1 = Math.max(0, -r.left, r.right - innerWidth, -r.top, r.bottom - innerHeight, hr ? hr.left - r.left : 0, hr ? r.right - hr.right : 0);
      if (out1 > 0.5) out.popups.push(`${desc(p)} ${out1.toFixed(1)}px outside`);
    }
    // A listbox option shows only the prefix that fits; two options whose shown text is equal are one option to a reader.
    const cv = document.createElement("canvas").getContext("2d");
    for (const sel of scope().querySelectorAll("select")) {
      if (!visible(sel)) continue;
      const shown = [...sel.options].map((o) => {
        const cs = getComputedStyle(o);
        if (o.scrollWidth <= o.clientWidth + 1) return o.text;
        cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const avail = o.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        let lo = 0, hi = o.text.length;
        while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (cv.measureText(o.text.slice(0, mid)).width <= avail) lo = mid; else hi = mid - 1; }
        return o.text.slice(0, lo);
      });
      const full = [...sel.options].map((o) => o.text);
      for (let i = 0; i < shown.length; i++) for (let j = i + 1; j < shown.length; j++) {
        if (full[i] !== full[j] && shown[i] === shown[j]) out.options.push(`${desc(sel)} "${shown[i]}"`);
        else if (full[i] === full[j]) out.options.push(`${desc(sel)} twice "${full[i]}"`);
      }
    }
    return out;
  };
  // REACH: every card rule that sets a colour, with its selector reduced to
  // what querySelectorAll can test, and whether a visible element matches it now.
  H.colourRules = () => {
    const sheets = [...root().querySelectorAll("style")].map((s) => s.sheet).filter(Boolean)
      .concat(root().adoptedStyleSheets || []);
    const out = {};
    const walk = (rules, media) => {
      for (const r of rules) {
        if (r.cssRules && !(r instanceof CSSStyleRule)) { walk(r.cssRules, r.conditionText || r.media && r.media.mediaText || media); continue; }
        if (!(r instanceof CSSStyleRule)) continue;
        const st = r.style;
        if (!["color", "background-color", "background", "fill"].some((p) => st.getPropertyValue(p) && !/^(inherit|currentcolor|transparent|none|initial|unset)$/i.test(st.getPropertyValue(p).trim()))) continue;
        for (const sel of r.selectorText.split(",")) {
          if (/::?(before|after|backdrop|placeholder|selection|-webkit-)/.test(sel)) continue;
          const base = sel.replace(/:(hover|focus-visible|focus-within|focus|active|visited|host)(\([^)]*\))?/g, "").trim();
          if (!base) continue;
          const key = media ? `@${media} ${sel.trim()}` : sel.trim();
          let hit = false;
          try { hit = [...root().querySelectorAll(base)].some(visible); } catch (e) { hit = false; }
          out[key] = hit;
        }
      }
    };
    for (const s of sheets) walk(s.cssRules, "");
    return out;
  };
  // Pixel ink of one text run: everything else hidden, the run forced black on white.
  H.inkMode = (i) => {
    let st = root().querySelector("style#p9ink");
    if (!st) { st = document.createElement("style"); st.id = "p9ink"; root().appendChild(st); }
    st.textContent = i === null ? "" :
      `*{visibility:hidden!important;background:transparent!important;border-color:transparent!important;box-shadow:none!important;outline:none!important}
       dialog::backdrop{background:transparent!important}
       [data-p9run="${i}"]{visibility:visible!important;color:#000!important;fill:#000!important;stroke:none!important;opacity:1!important}`;
    document.documentElement.style.background = i === null ? "" : "#fff";
  };
  H.inkShared = async (a, b) => {
    const load = (u) => new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = no; im.src = u; });
    const px = (im) => { const c = document.createElement("canvas"); c.width = im.width; c.height = im.height; const x = c.getContext("2d"); x.drawImage(im, 0, 0); return x.getImageData(0, 0, im.width, im.height).data; };
    const da = px(await load(a)), db = px(await load(b));
    let n = 0;
    for (let q = 0; q < da.length; q += 4) if (da[q] + da[q + 1] + da[q + 2] < 384 && db[q] + db[q + 1] + db[q + 2] < 384) n++;
    return n;
  };

  // ---- drivers -----------------------------------------------------------
  const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const click = (el) => el && el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true, cancelable: true }));
  const charts = () => [...root().querySelectorAll(".chartwrap svg")];
  const svgPx = (svg, vbX) => { const r = svg.getBoundingClientRect(); return r.left + (vbX / svg.viewBox.baseVal.width) * r.width; };
  const pe = (type, x, y, target) => (target || window).dispatchEvent(new PointerEvent(type, { bubbles: true, composed: true,
    cancelable: true, clientX: x, clientY: y, pointerId: 1, isPrimary: true, button: 0, buttons: type === "pointerup" ? 0 : 1 }));
  // Returns the steps whose target was not found: a driver that silently
  // missed would measure a state the grid claims and never reached.
  H.drive = async (steps) => {
    const c = card(), missed = [];
    let hover = null;
    for (const [op, a1, a2] of steps) {
      if (op === "cardClick") c._onCardClick({});
      else if (op === "open") c.dialog.open();
      else if (op === "stat") { const el = root().querySelector(`[data-stat='${a1}']`); if (el) click(el); else missed.push(`${op} ${a1}`); }
      else if (op === "chip") { const el = root().querySelector(`.chip[data-key='${a1}']`); if (el) el.click(); else missed.push(`${op} ${a1}`); }
      else if (op === "hover") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1], plot = c._plot;
        if (!svg || !plot) { missed.push(op); continue; }
        const r = svg.getBoundingClientRect();
        hover = { x: svgPx(svg, plot.scaleX(plot.windowStart + a1 * 3600000)), y: r.top + r.height * 0.45 };
      }
      else if (op === "zoom") c.view.zoom(a1);
      else if (op === "hoverShared") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1], plot = c._plot;
        const sp = c.hass.states["sensor.heat_pump_optimizer_plan_space_heating"].attributes.forecast;
        const dh = new Set(c.hass.states["sensor.heat_pump_optimizer_plan_dhw_heating"].attributes.forecast.filter((p) => Number(p.dhw_power) > 0.05).map((p) => p.t));
        const f = sp.find((p) => Number(p.space_power) > 0.05 && dh.has(p.t) && Date.parse(p.t) >= Date.now());
        if (!svg || !plot || !f) { missed.push(op); continue; }
        const r = svg.getBoundingClientRect();
        hover = { x: svgPx(svg, plot.scaleX(Date.parse(f.t) + 900000)), y: r.top + r.height * 0.45 };
      } else if (op === "armClear") {
        const hit = [...root().querySelectorAll(".setup-hit")].find((h) => h.dataset.key === "indoor_temp_entity");
        if (!hit) { missed.push(op); continue; }
        click(hit); await frame();
        const sel = root().querySelector(".setup-picker select");
        const save = root().querySelector(".sp-save");
        if (!sel || !save || ![...sel.options].some((o) => o.value === "")) { missed.push(`${op} picker`); continue; }
        sel.value = ""; sel.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
        save.click(); await frame();
        if (!save.classList.contains("confirm")) missed.push(`${op} not armed`);
      }
      else if (op === "page") { c.dialog.page = a1; c._render(); }
      else if (op === "clickSel") { const el = root().querySelector(a1); if (el) el.click(); else missed.push(`${op} ${a1}`); await sleep(60); }
      else if (op === "lowerCeiling") {
        const st = JSON.parse(JSON.stringify(c.hass.states));
        for (const e of Object.values(st)) if (e.attributes && "dhw_min_temperature_max" in e.attributes) e.attributes.dhw_min_temperature_max = a1;
        c.hass = { ...c.hass, states: st };
      } else if (op === "dragDhw") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1];
        const runs = c.manual.draft().dhw, [lo] = c.manual.bounds();
        const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
        const hit = svg && [...svg.querySelectorAll("[data-channel='dhw'][data-index]")].find((e) => e.dataset.index === String(i) && !e.dataset.edge);
        if (!hit) { missed.push(op); continue; }
        const g = c.geomAt(svgs.length - 1);
        const xOf = (t) => svgPx(svg, g.plotL + ((t - g.windowStart) / (g.windowEnd - g.windowStart)) * g.plotW);
        const hr = hit.getBoundingClientRect(), y = (hr.top + hr.bottom) / 2;
        const x0 = xOf(runs[i].start + 60000), x1 = xOf(runs[i].start + 60000 + 3600000);
        pe("pointerdown", x0, y, hit); pe("pointermove", x1, y, window); pe("pointerup", x1, y, window);
      } else if (op === "menuAt") {
        const svgs = charts(), svg = svgs[svgs.length - 1], g = c.geomAt(svgs.length - 1);
        const t = g.windowStart + a2 * (g.windowEnd - g.windowStart);
        const x = svgPx(svg, g.plotL + a2 * g.plotW);
        const lane = svg.querySelector(`rect.lane[data-channel='${a1}']`) || svg.querySelector(`[data-channel='${a1}']`);
        if (!lane) { missed.push(`${op} ${a1}`); continue; }
        const lr = lane.getBoundingClientRect();
        c.lanes.openMenu(a1, t, x, (lr.top + lr.bottom) / 2, svg, false);
      } else if (op === "picker") {
        const hit = [...root().querySelectorAll(".setup-hit")].find((h) => h.dataset.key === "wood_tank_top_entity");
        if (!hit) { missed.push(op); continue; }
        click(hit); await frame();
        const box = root().querySelector(".sp-filter");
        if (!box) { missed.push(`${op} filter`); continue; }
        box.value = a1; box.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
      } else missed.push(`unknown ${op}`);
      await frame();
    }
    await sleep(120); await frame();
    return { missed, hover };
  };
}

// ---- the host side -----------------------------------------------------------
async function p9Grid({ browser, check, plan, cardSrc, log = () => {} }) {
  const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
  const states = gridStates(plan);
  // Contrast varies with theme, geometry with width and language: 7 cells per
  // state cover both axes (375 px light/dark in English; 3 widths x 2
  // languages in light), where the full product is 12.
  const cells = [];
  for (const vp of VIEWPORTS) for (const lang of ["en", "sv-SE"]) cells.push({ vp, lang, theme: "light" });
  cells.push({ vp: VIEWPORTS[0], lang: "en", theme: "dark" });
  const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style id="theme"></style></head><body></body></html>`;
  const bad = { contrast: [], overflow: [], overlap: [], small: [], popups: [], options: [], missed: [], threw: [] };
  const reach = {};
  let measuredRuns = 0, candidates = 0, unknown = 0, n = 0;
  const t0 = Date.now();
  for (const cell of cells) {
    const ctx = await browser.newContext({ viewport: { width: cell.vp[0], height: cell.vp[1] }, deviceScaleFactor: 2,
      // Reduced motion: the card drops its transitions, so every cell measures
      // an end state -- a fade caught half-way would be a flake, not a finding.
      colorScheme: cell.theme, reducedMotion: "reduce" });
    await ctx.clock.setFixedTime(FROZEN);
    await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: PAGE }));
    const page = await ctx.newPage();
    for (const st of states) {
      const tag = `${st.name}/${cell.vp[0]}/${cell.theme}/${cell.lang}`;
      try {
        await page.goto("http://hpo.test/");
        await page.addScriptTag({ content: cardSrc });
        await page.addScriptTag({ content: `(${instrument.toString()})();` });
        await page.evaluate(([themeCss, w, cfg, states2, lang, svc]) => {
          document.getElementById("theme").textContent =
            `html{${themeCss};background:var(--primary-background-color)}` +
            `body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
            `heatpump-optimizer-card{display:block;width:${w}px}`;
          if (!customElements.get("ha-card")) {
            customElements.define("ha-card", class extends HTMLElement {
              constructor() {
                super();
                this.attachShadow({ mode: "open" }).innerHTML =
                  "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));" +
                  "color:var(--primary-text-color);box-sizing:border-box;border-radius:12px;" +
                  "border:1px solid var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";
              }
            });
          }
          const c = document.createElement("heatpump-optimizer-card");
          c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
          const hass = { states: states2, language: lang };
          if (svc === "fail") hass.callService = async () => { throw new Error("Service call failed"); };
          else if (svc) hass.callService = async () => ({ response: { results: {}, applied: { space: { expires_at: new Date(Date.now() + 5 * 3600000).toISOString() } } } });
          c.hass = hass;
          document.body.appendChild(c);
        }, [THEMES[cell.theme], cell.vp[0] - 16, st.config, st.states, cell.lang, st.service]);
        await page.waitForTimeout(60);
        const { missed, hover } = await page.evaluate((s) => window.__p9.drive(s), st.steps);
        if (hover) { await page.mouse.move(hover.x, hover.y); await page.waitForTimeout(120); }
        for (const m of missed) bad.missed.push(`${tag}: ${m}`);
        const m = await page.evaluate((co) => window.__p9.measure(co), false);
        n += 1; measuredRuns += m.runs; unknown += m.unknownColour; candidates += m.boxPairs.length;
        for (const k of ["contrast", "overflow", "small", "popups", "options"]) for (const x of m[k]) bad[k].push(`${tag}: ${x}`);
        for (const [k, v] of Object.entries(await page.evaluate(() => window.__p9.colourRules()))) reach[k] = reach[k] || v;
        for (const p of m.boxPairs) {
          const shots = [];
          for (const i of [p.a, p.b]) {
            await page.evaluate((k) => window.__p9.inkMode(k), i);
            shots.push("data:image/png;base64," + (await page.screenshot({ clip: p.clip })).toString("base64"));
          }
          await page.evaluate(() => window.__p9.inkMode(null));
          const shared = await page.evaluate(([a, b]) => window.__p9.inkShared(a, b), shots);
          if (shared > 0) bad.overlap.push(`${tag}: ${p.at} x ${p.bt} ${shared} px of shared ink`);
        }
      } catch (e) {
        bad.threw.push(`${tag}: ${String(e && e.message || e).slice(0, 160)}`);
      }
    }
    await ctx.close();
  }
  const unreached = Object.entries(reach).filter(([, v]) => !v).map(([k]) => k);
  const show = (xs) => `${xs.length}${xs.length ? ": " + [...new Set(xs.map((x) => x.replace(/^[^:]*: /, "")))].slice(0, 6).join(" | ") : ""}`;
  log(`P9 grid: ${n} cells, ${measuredRuns} text runs, ${candidates} box-intersecting pairs inked, ${Object.keys(reach).length} colour rules, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  check("P9 grid: every cell mounted and every driver step found its target (the grid measured what it names)",
    bad.threw.length === 0 && bad.missed.length === 0 && n === cells.length * states.length && measuredRuns > 0,
    `threw ${show(bad.threw)}; missed ${show(bad.missed)}; cells ${n}/${cells.length * states.length}`);
  check("P9 grid: every card rule that sets a colour is rendered in some cell (no unmeasured colour)",
    unreached.length === 0 && Object.keys(reach).length > 0, `${unreached.length} unreached: ${unreached.join(" | ")}`);
  check("P9 grid: every visible text run clears WCAG AA against what is under it", bad.contrast.length === 0 && unknown === 0,
    `${show(bad.contrast)}; unparsed colours ${unknown}`);
  check("P9 grid: no two text runs share ink", bad.overlap.length === 0, show(bad.overlap));
  check("P9 grid: no pop-up leaves the viewport or its chart", bad.popups.length === 0, show(bad.popups));
  check("P9 grid: every listbox option reads differently from its siblings as shown", bad.options.length === 0, show(bad.options));
  check("P9 grid: no text is clipped where its ancestor cannot scroll to it", bad.overflow.length === 0, show(bad.overflow));
  check("P9 grid: every target clears 24 px or the 2.5.8 spacing exception", bad.small.length === 0, show(bad.small));
  return { bad, unreached, n };
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

  // --- #936 (D4-03): the zoom pair clears SC 2.5.8 under a fine pointer ----
  // The shipped defect, measured by the audit in this same Chromium: the
  // HTML target floor lived only inside @media (pointer: coarse), so under
  // this page's own default fine pointer the zoom pair rendered at
  // 20.22x20.22 px with 22.22 px between centres -- under the 24 px minimum
  // and inside the spacing exception's 24 px circle at once, which is why
  // the exception rescued nothing. The floor is pointer-independent now
  // (card.mjs pins its emission); this lane is the one that can prove the
  // real rendered geometry, at both ends of the tile range the card ships
  // for. The buttons sit at opacity 0 until .chartwrap:hover, which hides
  // nothing here: opacity never removed hit-testing, and getBoundingClientRect
  // measures an invisible box as exactly as a visible one.
  const zoomAt = async (width) => page.evaluate(async (w) => {
    const card = window.__card;
    card.style.width = w;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    card._render();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    return [...card.shadowRoot.querySelectorAll(".viewctl button")].map((b) => {
      const r = b.getBoundingClientRect();
      return { cls: b.className, w: r.width, h: r.height,
               cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
    });
  }, width);
  for (const [label, width] of [["dashboard tile", "900px"], ["phone tile", "287px"]]) {
    const btns = await zoomAt(width);
    check(`the zoom controls render under a fine pointer (${label})`,
      btns.length >= 2, `${btns.length} button(s)`);
    if (btns.length) {
      const under = btns.filter((b) => Math.min(b.w, b.h) < 24 - 0.05);
      check(`every zoom button clears 24 px on both sides (${label})`,
        under.length === 0,
        under.map((b) => `${b.cls} ${b.w.toFixed(2)}x${b.h.toFixed(2)}`).join(", "));
      const tight = [];
      for (let i = 0; i < btns.length; i++) {
        for (let j = i + 1; j < btns.length; j++) {
          const d = Math.hypot(btns[i].cx - btns[j].cx, btns[i].cy - btns[j].cy);
          if (d < 24 - 0.05) tight.push(`${btns[i].cls}~${btns[j].cls} ${d.toFixed(2)}px`);
        }
      }
      check(`and the 24 px spacing circle fits between neighbours (${label})`,
        tight.length === 0, tight.join(", "));
    }
  }
  // Leave the card as the later sections found it.
  await zoomAt("900px");

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
    card.dialog.page = "setup";
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

  // --- D4-01: the compact chart's text at phone width ----------------------
  // The shipped defect, measured by the audit on a 287 px tile: axis text
  // at 3.19 px glyph height -- outlines gone. The card now floors the
  // rendered font (the viewBox-unit font grows as the tile narrows), and
  // the only honest place to prove it is a real layout engine: shrink the
  // host, re-render, and measure ON-SCREEN sizes. getComputedStyle is
  // useless here -- it reports the font-size attribute in user units,
  // with no viewBox scaling -- so the screen size is reconstructed from
  // the svg's own rect, the one transform that actually applies.
  const phoneFont = await page.evaluate(async () => {
    const card = window.__card;
    card.style.width = "287px";
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    card._render();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const root = card.shadowRoot;
    if (!root) return null;
    const chart = root.querySelector(".chartwrap svg");
    if (!chart) return null;
    const svgRect = chart.getBoundingClientRect();
    const scale = svgRect.width / 900;
    const labels = [...chart.querySelectorAll("text")]
      .filter((t) => (t.getAttribute("font-size") || "").length > 0);
    if (!labels.length) return null;
    const sizes = labels.map((t) => {
      const attr = Number(t.getAttribute("font-size"));
      const bbox = t.getBBox ? t.getBBox() : { height: 0 };
      return {
        screenFontPx: attr * scale,
        glyphScreenPx: bbox.height * scale,
        text: (t.textContent || "").trim().slice(0, 12),
      };
    });
    return {
      hostW: card.getBoundingClientRect().width,
      maxScreenFont: Math.max(...sizes.map((s) => s.screenFontPx)),
      maxGlyph: Math.max(...sizes.map((s) => s.glyphScreenPx)),
      n: sizes.length,
    };
  });
  check("a phone-width tile renders axis text at or above the 8 px floor",
    phoneFont !== null && phoneFont.maxScreenFont >= 8 - 0.05,
    phoneFont
      ? `host ${phoneFont.hostW.toFixed(0)} px, ${phoneFont.n} labels, ` +
        `largest on-screen font ${phoneFont.maxScreenFont.toFixed(2)} px, ` +
        `largest glyph box ${phoneFont.maxGlyph.toFixed(2)} px`
      : "no chart labels found");
  check("and the glyphs have real outlines again (height > 5 px)",
    phoneFont !== null && phoneFont.maxGlyph > 5,
    phoneFont ? `largest glyph ${phoneFont.maxGlyph.toFixed(2)} px on screen` : "none");

  // --- D4-01 / D4-02 / D4-04 (#256, #257, #259) ---------------------------
  // The audit's finding was not that the floor was wrong but that it never
  // applied: the card rendered at 3.70 px on a 359 px phone tile in the
  // order Lovelace mounts a card, and nothing re-rendered afterwards. The
  // checks above could not see it -- they call `card._render()` by hand
  // after resizing, and they read the LARGEST font in the chart. Everything
  // below mounts the card the way a dashboard does, touches nothing, and
  // reads the SMALLEST axis font, which is what the axis is actually drawn
  // at.
  //
  // A fresh page per scenario: a card that has already been laid out once
  // has a width, and the whole point of the Lovelace order is that the
  // first paint does not.
  const PHONE_TILE = 359;
  // <ha-card> is a Home Assistant element the card renders INSIDE its own
  // shadow root, where a page-level rule cannot reach it. Undefined, it is an
  // inline unknown element and its padding never shapes the chart -- which is
  // exactly the 26 px the shipped floor divided by the wrong width over
  // (#256). This is the frontend's own :host rule set.
  await page.evaluate(() => {
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
  });
  const mountScript = (order, tile, opts) => async ([st, ord, w, o]) => {
    document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
    document.body.innerHTML = "";
    const style = document.createElement("style");
    style.className = "hpo-test";
    style.textContent = `
      body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif; }
      heatpump-optimizer-card { display: block; width: ${w}px; }
    `;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    const cfg = Object.assign({ type: "custom:heatpump-optimizer-card" }, o || {});
    if (ord === "lovelace") {
      // What hui-card does: the element is configured and given its data
      // BEFORE it is placed, so its first paint has no width at all.
      card.setConfig(cfg);
      card.hass = { states: st };
      document.body.appendChild(card);
    } else {
      document.body.appendChild(card);
      card.setConfig(cfg);
      card.hass = { states: st };
    }
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 60));
  };
  const mount = async (order, tile, opts) =>
    page.evaluate(mountScript(order, tile, opts), [states, order, tile, opts || null]);

  // The on-screen size of the axis text: the font-size attribute is in
  // viewBox units, so only the svg's own rect turns it into pixels.
  const axisFont = () => page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const out = [];
    for (const svg of svgs) {
      const r = svg.getBoundingClientRect();
      if (!r.width) continue;
      const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
      const scale = r.width / (Number(vb[2]) || 900);
      // The axis and its annotations -- and, since #935 (R4-D4-01), the
      // lane strip's own labels: they used to be filtered out here because
      // they were drawn at 0.8x with no floor of their own, which put them
      // at 6.4 px wherever this floor bound. The card now floors them
      // through the same chartFontUnits pass (0.8 em base), so this check
      // reads them like every other chart text.
      const sizes = [...svg.querySelectorAll("text")]
        .filter((t) => (t.getAttribute("font-size") || "").length > 0)
        .filter((t) => (t.textContent || "").trim().length > 0)
        .map((t) => Number(t.getAttribute("font-size")) * scale);
      if (sizes.length) {
        out.push({ svgW: r.width, min: Math.min(...sizes), n: sizes.length });
      }
    }
    return out;
  });

  for (const order of ["lovelace", "attached"]) {
    await mount(order, PHONE_TILE);
    const f = await axisFont();
    check(`the ${order} mount order paints the axis at the 8 px floor on a phone tile`,
      f.length === 1 && f[0].min >= 8 - 0.05,
      f.length ? `svg ${f[0].svgW.toFixed(1)} px wide, smallest axis text ${f[0].min.toFixed(2)} px (${f[0].n} labels)`
               : "no chart text found");
  }

  // The ResizeObserver has to RE-RENDER, not just refresh a cached rect:
  // nothing else corrects the font, and the plan sensor that would is on a
  // 30-minute schedule by default.
  await mount("lovelace", PHONE_TILE);
  const resized = await page.evaluate(async () => {
    const card = window.__card;
    let renders = 0;
    const real = card._render.bind(card);
    card._render = (...a) => { renders += 1; return real(...a); };
    card.style.width = "300px";
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
    const svg = card.shadowRoot.querySelector(".chartwrap svg");
    const rect = svg.getBoundingClientRect();
    const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
    const scale = rect.width / (Number(vb[2]) || 900);
    const sizes = [...svg.querySelectorAll("text")]
      .filter((t) => (t.getAttribute("font-size") || "").length > 0)
      .filter((t) => (t.textContent || "").trim().length > 0)
      .map((t) => Number(t.getAttribute("font-size")) * scale);
    return { renders, svgW: rect.width, min: Math.min(...sizes) };
  });
  check("narrowing the tile re-renders the chart and holds the floor",
    resized.renders >= 1 && resized.min >= 8 - 0.05,
    `${resized.renders} render(s) on resize, svg ${resized.svgW.toFixed(1)} px, smallest axis text ${resized.min.toFixed(2)} px`);

  // The expanded dialog is not a wide chart just because it is a dialog: on
  // a phone it is 360 px across, and it had no floor at all.
  await page.setViewportSize({ width: 375, height: 812 });
  await mount("lovelace", PHONE_TILE, { what_if: true });
  await page.evaluate(async () => {
    window.__card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  });
  const dlgFont = await axisFont();
  check("the expanded dialog holds the 8 px floor on a phone too",
    dlgFont.length === 2 && dlgFont[1].min >= 8 - 0.05,
    dlgFont.length === 2
      ? `dialog svg ${dlgFont[1].svgW.toFixed(1)} px wide, smallest axis text ${dlgFont[1].min.toFixed(2)} px`
      : `${dlgFont.length} chart(s) measured`);

  // The editable slots are the ones still in the future, and the payload's
  // day is fixed while the wall clock is not: against the real clock every
  // slot is already locked, no `.slot-hit` is drawn at all, and a check on
  // slot targets measures an empty set. Freeze six hours into the captured
  // day, as tests/card.mjs does, which always leaves both a locked past and
  // an editable future.
  await page.evaluate(([frozen]) => {
    const Real = Date;
    class Frozen extends Real {
      constructor(...a) { super(...(a.length ? a : [frozen])); }
      static now() { return frozen; }
    }
    window.Date = Frozen;
  }, [Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000]);
  await mount("lovelace", PHONE_TILE, { what_if: true });
  await page.evaluate(async () => {
    window.__card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  });

  // D4-02: what a pointer or a Tab can land on, and how big it is. The
  // compact tile is a preview -- tapping it opens the dialog -- so it must
  // offer no lane or slot targets at all; the dialog's must clear 24 px.
  const targets = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const read = (svg) =>
      [...svg.querySelectorAll("rect")]
        .filter((r) => r.hasAttribute("tabindex") || r.getAttribute("role") === "button")
        .map((r) => {
          const b = r.getBoundingClientRect();
          return { cls: r.getAttribute("class"), w: b.width, h: b.height };
        });
    return { tile: read(svgs[0]), dialog: svgs[1] ? read(svgs[1]) : [] };
  });
  check("the compact tile offers no lane or slot target at all",
    targets.tile.length === 0,
    targets.tile.slice(0, 4).map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", "));
  const tooSmall = targets.dialog.filter((t) => Math.min(t.w, t.h) < 24 - 0.05);
  const dialogSlots = targets.dialog.filter((t) => /slot-hit/.test(t.cls || ""));
  check("the dialog really offers editable slot targets to measure",
    dialogSlots.length > 0,
    `${targets.dialog.length} target(s), ${dialogSlots.length} of them slots`);
  check("every lane and slot target in the dialog clears 24 px on both sides",
    targets.dialog.length > 0 && tooSmall.length === 0,
    `${targets.dialog.length} target(s); smallest ` +
    (targets.dialog.length
      ? targets.dialog
          .map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`)
          .sort()[0]
      : "none") +
    (tooSmall.length ? `; under: ${tooSmall.slice(0, 4).map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", ")}` : ""));

  // D4-02 (#262): HTML controls under a coarse pointer must also clear 24 px.
  // Isolated page so coarse media does not leak into later ink checks.
  const coarsePage = await browser.newPage({ viewport: { width: 1024, height: 800 } });
  coarsePage.on("pageerror", (err) => console.log(`  page error: ${err.message}`));
  await coarsePage.goto("about:blank");
  // Headless Chromium is pointer:fine, and nothing here makes it coarse for
  // CSS: Playwright 1.49's emulateMedia has no `pointer`, and CDP
  // Emulation.setEmulatedMedia leaves BOTH matchMedia("(pointer: coarse)")
  // false and an `@media (pointer: coarse)` block unmatched -- measured on a
  // minimal page in this job's own Chromium (R5-D4-03, #1320). What is coarse
  // on this page is the in-page matchMedia stub below, which is the card's
  // own predicate (_coarsePointer()). So the card's HTML floor keys on that
  // predicate rather than on a CSS media query, and this check measures the
  // floor the card actually applies under it.
  const coarseCdp = await coarsePage.context().newCDPSession(coarsePage);
  await coarseCdp.send("Emulation.setEmulatedMedia", {
    features: [{ name: "pointer", value: "coarse" }],
  });
  await coarsePage.addScriptTag({ path: CARD_SRC });
  await coarsePage.evaluate(() => {
    const orig = window.matchMedia.bind(window);
    window.matchMedia = (q) => {
      if (q === "(pointer: coarse)") {
        return {
          matches: true, media: q, onchange: null,
          addEventListener() {}, removeEventListener() {},
          addListener() {}, removeListener() {},
          dispatchEvent() { return true; },
        };
      }
      return orig(q);
    };
  });
  await coarsePage.evaluate(
    mountScript("lovelace", PHONE_TILE, { what_if: true }),
    [states, "lovelace", PHONE_TILE, { what_if: true }],
  );
  await coarsePage.evaluate(async () => {
    window.__card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  });
  const htmlTargets = await coarsePage.evaluate(() => {
    const root = window.__card.shadowRoot;
    const sel = [
      "button", ".chip", "input[type='range']", "input[type='time']",
      "select", ".dlg-tab",
    ].join(", ");
    return [...root.querySelectorAll(sel)]
      .filter((el) => {
        const st = getComputedStyle(el);
        return st.display !== "none" && st.visibility !== "hidden" && !el.disabled;
      })
      .map((el) => {
        const b = el.getBoundingClientRect();
        return {
          tag: el.className || el.tagName.toLowerCase(),
          w: b.width, h: b.height,
        };
      });
  });
  const htmlSmall = htmlTargets.filter((t) => Math.min(t.w, t.h) < 24 - 0.05);
  check("every HTML control in the dialog clears 24 px under a coarse pointer",
    htmlTargets.length > 0 && htmlSmall.length === 0,
    `${htmlTargets.length} control(s); smallest ` +
    (htmlTargets.length
      ? htmlTargets
          .map((t) => `${t.tag} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`)
          .sort((a, b) => Math.min(a.w, a.h) - Math.min(b.w, b.h))[0]
      : "none") +
    (htmlSmall.length
      ? `; under: ${htmlSmall.slice(0, 4).map((t) => `${t.tag} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", ")}`
      : ""));
  // R5-D4-03 (#1320): the 44 px touch floor is owed to the HTML surface too,
  // not only to the SVG-drawn lane/slot rects _targetMinPx() sizes. Under a
  // coarse pointer the card's HTML target floor is the same 44 px the drawn
  // geometry already gets, so no control a finger can land on lays out under
  // it. The survivors, if any, are the SVG lane rects this selector cannot
  // name -- those are _targetMinPx()'s own arm, checked above.
  const htmlSmall44 = htmlTargets.filter((t) => Math.min(t.w, t.h) < 44 - 0.05);
  check("every HTML control in the dialog clears 44 px under a coarse pointer",
    htmlTargets.length > 0 && htmlSmall44.length === 0,
    `${htmlTargets.length} control(s); ${htmlSmall44.length} under 44 px` +
    (htmlSmall44.length
      ? `: ${htmlSmall44.slice(0, 6).map((t) => `${t.tag} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", ")}`
      : ""));
  await coarsePage.close();

  // --- R7 D4-01 / D4-02 (#1454, #1455) ------------------------------------
  // The dialog painted content whose intrinsic width exceeded its own box and
  // then hid the overflow, so the ink could not be reached by any gesture:
  // the savings table's `%` column (a `width:100%` table whose min-content
  // width is wider than `.dlg-body`, right-aligned so the hidden strip is
  // exactly the digits) and the Swedish tab row (`Rådgivare`). card.mjs
  // cannot see either -- its stub's getBoundingClientRect is a constant --
  // and neither could the checks above, which read the chart. What is
  // measured here is the FINDER's metric, in the lane that runs on every
  // pull request: the pixels by which a text run's ink extends past the right
  // edge of the nearest clipping ancestor, MINUS what that ancestor (or the
  // document) can scroll to reveal. Anything positive is text a phone user
  // cannot reach at all.
  //
  // The grid is the three phone widths in both languages on both dialog
  // pages, plus 1280 px as the null control: a wide dialog has no
  // min-content overflow to hide, so a metric that read positive there would
  // be measuring something other than reachability.
  const clipPage = await browser.newPage({ viewport: { width: 375, height: 812 } });
  clipPage.on("pageerror", (err) => console.log(`  page error: ${err.message}`));
  await clipPage.goto("about:blank");
  await clipPage.addScriptTag({ path: CARD_SRC });
  // The savings page only draws a table when the savings sensor publishes
  // months, and this lane's fixture has none: without these the savings arms
  // measure an empty page and pass for the wrong reason. Twelve months of
  // realistic figures, because the table's width is data-driven.
  const clipStates = {
    ...states,
    "sensor.heat_pump_optimizer_monthly_savings": {
      state: "246.91",
      attributes: {
        unit_of_measurement: "SEK",
        savings_months: Array.from({ length: 12 }, (_, m) => ({
          month: `2026-${String(m + 1).padStart(2, "0")}`,
          baseline_sek: 1234.56 + m * 17,
          actual_sek: 987.65 + m * 9,
          savings_sek: 246.91 + m * 8,
          savings_pct: 20 + m,
          estimated: m % 4 === 3,
        })),
      },
    },
  };
  const unreachableInk = async (w, lang, dlgPage) => {
    await clipPage.setViewportSize({ width: w, height: 812 });
    return clipPage.evaluate(async ([st, w2, lang2, pg]) => {
      document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
      document.body.innerHTML = "";
      const style = document.createElement("style");
      style.className = "hpo-test";
      // The same font stack the other measurements here use: a table's
      // min-content width is font-dependent.
      style.textContent =
        `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
        `heatpump-optimizer-card{display:block;width:${w2}px}`;
      document.head.appendChild(style);
      const card = document.createElement("heatpump-optimizer-card");
      card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
      card.hass = { states: st, language: lang2 };
      document.body.appendChild(card);
      card._onCardClick({});
      card.dialog.page = pg;
      card._render();
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      await new Promise((r) => setTimeout(r, 140));
      // The dialog is the surface under test: the compact card behind it is
      // not what a phone user is reading here.
      const dlg = card.shadowRoot.querySelector("dialog.expanded");
      if (!dlg) return { over: -1, who: "no dialog", runs: 0 };
      // The reachable extra of a clipping ancestor: `hidden`/`clip` reaches
      // none of its overflow, `auto`/`scroll` reaches all of it -- which is
      // what the fix buys.
      const clipOf = (el) => {
        let n = el.parentElement;
        while (n) {
          const ox = getComputedStyle(n).overflowX;
          if (ox === "hidden" || ox === "clip") {
            return { rect: n.getBoundingClientRect(), extra: 0,
                     who: String(n.className || n.tagName) };
          }
          if (ox === "auto" || ox === "scroll") {
            const extra = Math.max(0, n.scrollWidth - n.clientWidth);
            if (extra > 0) {
              return { rect: n.getBoundingClientRect(), extra,
                       who: String(n.className || n.tagName) };
            }
          }
          n = n.parentElement;
        }
        const de = document.documentElement;
        return { rect: de.getBoundingClientRect(),
                 extra: Math.max(0, de.scrollWidth - de.clientWidth),
                 who: "document" };
      };
      let worst = null;
      let runs = 0;
      let tableRuns = 0;
      for (const el of dlg.querySelectorAll("*")) {
        if (!el.getClientRects().length) continue;
        const cs = getComputedStyle(el);
        if (cs.display === "none" || cs.visibility === "hidden") continue;
        const direct = [...el.childNodes].filter((x) => x.nodeType === 3)
          .map((x) => x.textContent).join("").trim();
        if (!direct) continue;
        const rg = document.createRange();
        rg.selectNodeContents(el);
        const ink = rg.getBoundingClientRect();
        if (ink.width < 1 || ink.height < 1) continue;
        runs += 1;
        if (el.closest(".savings-table")) tableRuns += 1;
        const c = clipOf(el);
        const over = +(ink.right - (c.rect.right + c.extra)).toFixed(1);
        if (over > 0.5 && (!worst || over > worst.over)) {
          worst = { over, clip: c.who, cls: String(el.className || el.tagName).slice(0, 24),
                    txt: direct.slice(0, 24) };
        }
      }
      return worst ? { ...worst, runs, tableRuns } : { over: -1, who: "none", runs, tableRuns };
    }, [clipStates, w, lang, dlgPage]);
  };

  const clipCells = [];
  for (const w of [375, 360, 320, 1280]) {
    for (const lang of ["en", "sv-SE"]) {
      for (const pg of ["savings", "plan"]) {
        clipCells.push({ w, lang, pg, ...(await unreachableInk(w, lang, pg)) });
      }
    }
  }
  const unreachable = clipCells.filter((c) => c.over > 0.5);
  check("no dialog text is painted outside a box a gesture can reach",
    unreachable.length === 0,
    unreachable.length
      ? unreachable.map((c) =>
          `${c.w}px ${c.lang}/${c.pg}: ${c.over}px "${c.txt}" clipped by ${c.clip}`).join("; ")
      : `${clipCells.length} cell(s) clean; worst ink reach ` +
        `${Math.max(...clipCells.map((c) => c.over)).toFixed(1)} px`);
  // The control on the metric itself: a walk that found no text run would
  // report no unreachable text for the wrong reason, and the savings arms
  // only measure the defect if the table actually rendered.
  check("and the walk really measured the dialog's text",
    clipCells.every((c) => c.runs > 0) &&
      clipCells.filter((c) => c.pg === "savings").every((c) => c.tableRuns > 0),
    `${Math.min(...clipCells.map((c) => c.runs))} text run(s) in the thinnest cell, ` +
    `${Math.min(...clipCells.filter((c) => c.pg === "savings").map((c) => c.tableRuns))} ` +
    `in the thinnest savings table`);
  await clipPage.close();

  // #258: axis unit labels must not ink-collide with their top tick once the
  // D4-01 font floor engages. Rasterize each text alone and pair units with
  // the top tick on the same axis (same x band); positive overlap in both
  // dimensions is a failure. deviceScaleFactor 4 matches the judge probe.
  const inkPage = await browser.newPage({
    viewport: { width: 500, height: 700 },
    deviceScaleFactor: 4,
  });
  inkPage.on("pageerror", (err) => console.log(`  page error: ${err.message}`));
  await inkPage.goto("about:blank");
  await inkPage.addScriptTag({ path: CARD_SRC });
  await inkPage.evaluate(() => {
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
  });
  await inkPage.evaluate(async ([st, w]) => {
    document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
    document.body.innerHTML = "";
    const style = document.createElement("style");
    style.className = "hpo-test";
    style.textContent =
      `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
      `heatpump-optimizer-card{display:block;width:${w}px;}`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
    card.hass = { states: st };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    card._onCardClick({});
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  }, [states, PHONE_TILE]);
  const inkStats = await inkPage.evaluate(async () => {
    const root = window.__card.shadowRoot;
    const svg = [...root.querySelectorAll(".chartwrap svg")].pop();
    if (!svg) return { pairs: -1, topRow: -1, detail: "no chart svg" };
    const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
    const W = Number(vb[2]) || 900;
    const H = Number(vb[3]) || 380;
    const unitPat = /^(°C|kW|kr\/kWh|öre\/kWh|W\/m²)$/;
    const tickPat = /^-?\d[\d.,]*$/;
    const texts = [...svg.querySelectorAll("text")]
      .filter((t) => (t.textContent || "").trim().length > 0);
    async function inkOf(el) {
      const mini = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      mini.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      mini.setAttribute("viewBox", `0 0 ${W} ${H}`);
      mini.setAttribute("width", String(W));
      mini.setAttribute("height", String(H));
      const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      bg.setAttribute("width", "100%");
      bg.setAttribute("height", "100%");
      bg.setAttribute("fill", "white");
      mini.appendChild(bg);
      mini.appendChild(el.cloneNode(true));
      const url = "data:image/svg+xml;charset=utf-8," +
        encodeURIComponent(new XMLSerializer().serializeToString(mini));
      const img = new Image();
      await new Promise((ok, no) => { img.onload = ok; img.onerror = no; img.src = url; });
      const canvas = document.createElement("canvas");
      canvas.width = W;
      canvas.height = H;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
      const { data } = ctx.getImageData(0, 0, W, H);
      let r0 = H, r1 = -1, c0 = W, c1 = -1;
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = (y * W + x) * 4;
          if (data[i + 3] > 8 && data[i] + data[i + 1] + data[i + 2] < 740) {
            r0 = Math.min(r0, y); r1 = Math.max(r1, y);
            c0 = Math.min(c0, x); c1 = Math.max(c1, x);
          }
        }
      }
      return r1 < 0 ? null : { rows: [r0, r1], cols: [c0, c1] };
    }
    const axisBand = (el) => Math.round(Number(el.getAttribute("x") || 0) / 40);
    const unitEls = texts.filter((t) => unitPat.test((t.textContent || "").trim()));
    let topRowUnits = 0;
    let pairs = 0;
    const detail = [];
    for (const u of unitEls) {
      const uInk = await inkOf(u);
      if (!uInk) continue;
      if (uInk.rows[0] <= 0) topRowUnits += 1;
      const band = axisBand(u);
      const ticks = texts.filter(
        (t) => tickPat.test((t.textContent || "").trim()) && axisBand(t) === band
      );
      if (!ticks.length) continue;
      const topTick = ticks.reduce(
        (a, b) => (Number(a.getAttribute("y")) < Number(b.getAttribute("y")) ? a : b)
      );
      const tInk = await inkOf(topTick);
      if (!tInk) continue;
      const vOv = Math.min(uInk.rows[1], tInk.rows[1]) - Math.max(uInk.rows[0], tInk.rows[0]) + 1;
      const hOv = Math.min(uInk.cols[1], tInk.cols[1]) - Math.max(uInk.cols[0], tInk.cols[0]) + 1;
      if (vOv > 0 && hOv > 0) {
        pairs += 1;
        detail.push(`${(u.textContent || "").trim()}/${(topTick.textContent || "").trim()} v${vOv} h${hOv}`);
      }
    }
    return { pairs, topRow: topRowUnits, detail: detail.join("; ") };
  });
  check("axis unit labels carry no ink on the svg's top row",
    inkStats.topRow === 0,
    `${inkStats.topRow} unit(s) with row-0 ink`);
  check("axis unit labels do not ink-collide with their top tick",
    inkStats.pairs === 0,
    `${inkStats.pairs} colliding pair(s)${inkStats.detail ? `: ${inkStats.detail}` : ""}`);
  await inkPage.close();

  // A target that falls short of the floor has to be BOXED IN, not merely
  // clipped on one side. The first review of this fix found every residual
  // target sitting next to 84-258 px of empty lane: the deficit was split in
  // half and each half clipped at its own constraint, so the half a
  // neighbour refused was thrown away instead of offered to the free side.
  // For each target this measures the span between the two things it may not
  // cross -- the nearest neighbouring INK on each side, else the plot edge --
  // and requires that a small target had nowhere to grow.
  const residual = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const svg = svgs[svgs.length - 1];
    if (!svg) return null;
    const r = svg.getBoundingClientRect();
    const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
    const perUnit = r.width / (Number(vb[2]) || 900);
    const num = (el, a) => Number(el.getAttribute(a));
    const inks = [...svg.querySelectorAll("rect.slot")].map((e) => ({
      x1: num(e, "x"), x2: num(e, "x") + num(e, "width"), y: num(e, "y"),
    }));
    const out = [];
    for (const hit of svg.querySelectorAll("rect.slot-hit")) {
      const b = hit.getBoundingClientRect();
      const hx1 = num(hit, "x"), hx2 = hx1 + num(hit, "width"), hy = num(hit, "y");
      const mine = inks.find((i) => i.y === hy && i.x1 >= hx1 - 0.01 && i.x2 <= hx2 + 0.01);
      let limitL = -Infinity, limitR = Infinity;
      let covers = 0;
      for (const ink of inks) {
        if (ink.y !== hy) continue;
        if (mine && ink.x1 === mine.x1 && ink.x2 === mine.x2) continue;
        // The invariant: a target may never cover another slot's ink.
        if (hx1 < ink.x2 - 0.01 && hx2 > ink.x1 + 0.01) covers += 1;
        if (mine && ink.x2 <= mine.x1) limitL = Math.max(limitL, ink.x2);
        if (mine && ink.x1 >= mine.x2) limitR = Math.min(limitR, ink.x1);
      }
      out.push({
        w: b.width, h: b.height, covers,
        // Room the target could occupy without covering anything, in px.
        available: mine
          ? (Math.min(limitR, Number(vb[2])) - Math.max(limitL, 0)) * perUnit
          : b.width,
      });
    }
    return out;
  });
  const covering = (residual || []).filter((t) => t.covers > 0);
  check("no slot target covers another slot's ink",
    residual !== null && covering.length === 0,
    `${covering.length} of ${(residual || []).length} target(s) overlap a neighbour's ink`);
  const roomLeft = (residual || []).filter(
    (t) => Math.min(t.w, t.h) < 24 - 0.05 && t.available > 24 + 1);
  check("a slot target under the floor is boxed in, not merely clipped on one side",
    residual !== null && roomLeft.length === 0,
    roomLeft.slice(0, 4).map((t) =>
      `target ${t.w.toFixed(1)} px with ${t.available.toFixed(1)} px available`).join("; ")
    || `${(residual || []).length} target(s), all at or above the floor`);

  // D4-04: the empty state, which is what the dashboard card picker previews
  // before anything is configured. Its entity ids used to paint up to 47 px
  // outside the card and give the document 40 px of horizontal scroll.
  await page.evaluate(async ([w]) => {
    document.body.innerHTML = "";
    document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
    const style = document.createElement("style");
    style.className = "hpo-test";
    style.textContent =
      `body { margin: 0; } heatpump-optimizer-card { display: block; width: ${w}px; }`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: {} };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, [PHONE_TILE]);
  const spill = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const box = root.querySelector("ha-card") || window.__card;
    const cb = box.getBoundingClientRect();
    let worst = 0, who = "";
    const walk = (node) => {
      for (const el of node.querySelectorAll("*")) {
        if (!el.getClientRects().length) continue;
        const b = el.getBoundingClientRect();
        const out = Math.max(cb.left - b.left, b.right - cb.right, 0);
        if (out > worst) { worst = out; who = el.tagName.toLowerCase(); }
      }
    };
    walk(root);
    return {
      worst, who,
      hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      text: (root.querySelector(".empty") || {}).textContent ? 1 : 0,
    };
  });
  check("the empty state's entity ids stay inside the card box on a phone tile",
    spill.text === 1 && spill.worst <= 1,
    `worst overflow ${spill.worst.toFixed(1)} px (${spill.who || "none"}), document h-scroll ${spill.hScroll} px`);
  check("and the empty state gives the document no horizontal scroll",
    spill.hScroll <= 0, `${spill.hScroll} px of h-scroll`);

  // D4-05 / D4-06: text contrast in real Chromium against HA's default light
  // theme and again with every HA token stripped (card fallbacks only).
  //
  // ---- Carried forward from #558 C1, for whoever extends this witness ----
  //
  // C1 fixed four GRAPHICAL objects and left this lane alone deliberately.
  // Three findings constrain the extension, each measured by resolving the
  // card's own tokens against HA's default themes (light #ffffff card /
  // dark #1c1c1c card) and compositing in sRGB; the control on each is the
  // perturbation named beside it.
  //
  // 1. NO FIXED COLOUR CLEARS 4.5:1 AGAINST BOTH #ffffff AND #1c1c1c. The
  //    constraints have no overlap: 4.5:1 on white needs relative luminance
  //    <= 0.1833, on #1c1c1c it needs >= 0.2273. So a dark-theme text lane
  //    cannot be satisfied by choosing a better constant ANYWHERE -- only by
  //    a theme token. Control: the same arithmetic at 3:1 does have an
  //    overlap (0.1348..0.3000), which is why the SERIES palette can be
  //    fixed constants and text cannot.
  //
  // 2. C4 retargeted the text sites C1 did not own. Re-derived at the
  //    merge base, not carried: ACCENT_READABLE had 7 non-definition
  //    references (#026aa8, 5.79:1 light / 2.95:1 dark); MUTED_READABLE
  //    had 2 (#666666, 5.74:1 / 2.97:1). Five CSS text colours plus the
  //    lane-more fill now use --primary-text-color. ACCENT_READABLE
  //    remains only on .wi-save's filled border/background (white on
  //    #026aa8). MUTED_READABLE is gone. Control: restore .chip.off to
  //    #666666 and the dark text check fails under 4.5:1.
  //
  // 3. THE FALLBACKS-ONLY LANE ALREADY FAILS 4.5:1 ON TEXT if extended past
  //    the four REQUIRED names. The failing set is a RULE, not a list: every
  //    <text> the chart emits whose fill is var(--secondary-text-color,#888).
  //    Re-derive it. At this head that rule returns the axis tick labels, the
  //    unit titles, the estimated-prices label AND the .lane-label runs --
  //    the last of which the three-instance list this line used to carry did
  //    not name. #888 on white is 3.54:1. With the token present it is 4.81:1
  //    light and 6.13:1 dark, so this is a FALLBACK defect, not a token one.
  //
  // And one thing this witness must NOT assert. Gridlines are deliberately
  // below 3:1 -- .grid is --secondary-text-color at opacity 0.3, which is
  // 1.472:1 light and 1.698:1 dark. WCAG 1.4.11 asks 3:1 of graphics
  // REQUIRED to understand content; the values are carried by the axis
  // labels, and a grid at 3:1 drowns the series it exists to help read.
  // Asserting 3:1 on .grid would red the lane for a measured design choice.
  // The hooks C1 left for this lane: .now, .now-label, .estimated-edge,
  // .grid.grid-v, .grid.grid-h, and .series[data-key]. That last selector is
  // deliberately NOT path-qualified: a one-point series draws a <circle
  // class="series">, so path.series[data-key] silently drops it.
  const HA_LIGHT = `
    --primary-text-color:#212121; --secondary-text-color:#727272;
    --text-primary-color:#fff; --primary-color:#03a9f4;
    --card-background-color:#fff; --divider-color:rgba(0,0,0,.12);
  `;
  // Same tokens tests/card.mjs C1 uses. A dark lane cannot be a second
  // constant: 4.5:1 on #ffffff and on #1c1c1c have no overlapping luminance.
  const HA_DARK = `
    --primary-text-color:#e1e1e1; --secondary-text-color:#9b9b9b;
    --text-primary-color:#fff; --primary-color:#03a9f4;
    --card-background-color:#1c1c1c; --divider-color:rgba(225,225,225,.12);
  `;
  const contrastOf = async (themeCss, dlgPage) => {
    await page.evaluate(async ([st, theme, tab]) => {
      document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
      document.body.innerHTML = "";
      const style = document.createElement("style");
      style.className = "hpo-test";
      style.textContent =
        `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
        `heatpump-optimizer-card{display:block;width:900px;${theme}}`;
      document.head.appendChild(style);
      const card = document.createElement("heatpump-optimizer-card");
      card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
      card.hass = { states: st, language: "en" };
      document.body.appendChild(card);
      window.__card = card;
      card._onCardClick({});
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      await new Promise((r) => setTimeout(r, 80));
      if (tab === "setup") {
        card.dialog.page = "setup";
        card._render();
      } else {
        const chip = card.shadowRoot.querySelector(".chip[data-key='price']");
        if (chip) chip.click();
      }
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    }, [states, themeCss, dlgPage]);
    return page.evaluate((tab) => {
      const hex = (h) => {
        const n = parseInt(h.slice(1), 16);
        return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
      };
      const parse = (s) => {
        if (!s || s === "transparent") return null;
        const m = s.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (m) return [+m[1], +m[2], +m[3]];
        if (s.startsWith("#")) return hex(s.length === 4
          ? `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}` : s);
        return null;
      };
      const lum = (c) => {
        const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
      };
      const ratio = (a, b) => {
        const la = lum(a), lb = lum(b);
        return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
      };
      const bgOf = (el) => {
        for (let n = el; n; n = n.parentElement || (n.getRootNode().host || null)) {
          const bg = parse(getComputedStyle(n).backgroundColor);
          if (bg) return bg;
        }
        return [255, 255, 255];
      };
      const root = window.__card.shadowRoot;
      const out = [];
      if (tab !== "setup") {
        const htmlSel = [
          [".whatif .wi-apply", "wi-apply"],
          [".whatif .wi-save", "wi-save"],
          [".chip.off", "chip-off"],
        ];
        for (const [sel, name] of htmlSel) {
          const el = root.querySelector(sel);
          if (!el) { out.push({ name, missing: true }); continue; }
          const fg = parse(getComputedStyle(el).color);
          const r = fg ? ratio(fg, bgOf(el)) : 0;
          out.push({ name, ratio: +r.toFixed(2), missing: false });
        }
      } else {
        const empty = root.querySelector("text.setup-slot.empty");
        if (empty) {
          const raw = empty.getAttribute("fill") || "";
          const fg = parse(raw.startsWith("#") ? raw : getComputedStyle(empty).fill);
          const rawBg = getComputedStyle(window.__card)
            .getPropertyValue("--card-background-color").trim();
          const cardBg = parse(rawBg) || [255, 255, 255];
          out.push({
            name: "setup-slot.empty",
            ratio: fg ? +ratio(fg, cardBg).toFixed(2) : 0,
            missing: false,
          });
        } else {
          out.push({ name: "setup-slot.empty", missing: true });
        }
      }
      return out;
    }, dlgPage);
  };
  const REQUIRED = ["wi-apply", "wi-save", "setup-slot.empty", "chip-off"];
  for (const [label, theme] of [
    ["HA light theme", HA_LIGHT],
    ["HA dark theme", HA_DARK],
    ["card fallbacks only", ""],
  ]) {
    const planRows = await contrastOf(theme, "plan");
    const setupRows = await contrastOf(theme, "setup");
    const rows = [...planRows, ...setupRows];
    const reqMissing = REQUIRED.filter((n) => rows.some((r) => r.name === n && r.missing));
    const bad = rows.filter((r) => REQUIRED.includes(r.name) && !r.missing && r.ratio < 4.5);
    check(`D4-05/D4-06 action and setup text clears 4.5:1 (${label})`,
      reqMissing.length === 0 && bad.length === 0,
      `${bad.map((r) => `${r.name} ${r.ratio}:1`).join("; ") || `${rows.length} site(s) measured`}` +
      (reqMissing.length ? `; missing: ${reqMissing.join(", ")}` : ""));
  }

  // C4: Chromium composites of the C1 hooks, light and dark. Gridlines are
  // perceptible only (1.3:1), never 3:1 — that would drown the series.
  const graphicStates = {
    ...states,
    [SPACE_ID]: {
      ...states[SPACE_ID],
      attributes: {
        ...states[SPACE_ID].attributes,
        forecast: plan.space_plan.forecast.map((p, i) => ({
          ...p,
          price_known: i < Math.floor(plan.space_plan.forecast.length / 2),
        })),
      },
    },
  };
  const graphicsOf = async (themeCss) => {
    await page.evaluate(async ([st, theme]) => {
      document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
      document.body.innerHTML = "";
      const style = document.createElement("style");
      style.className = "hpo-test";
      style.textContent =
        `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
        `heatpump-optimizer-card{display:block;width:900px;${theme}}`;
      document.head.appendChild(style);
      const card = document.createElement("heatpump-optimizer-card");
      card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
      card.hass = { states: st, language: "en" };
      document.body.appendChild(card);
      window.__card = card;
      card._onCardClick({});
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      await new Promise((r) => setTimeout(r, 80));
    }, [graphicStates, themeCss]);
    return page.evaluate(() => {
      const hex = (h) => {
        const n = parseInt(h.slice(1), 16);
        return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
      };
      const parse = (s) => {
        if (!s || s === "transparent" || s === "none") return null;
        const m = s.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (m) return [+m[1], +m[2], +m[3]];
        if (s.startsWith("#")) return hex(s.length === 4
          ? `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}` : s);
        return null;
      };
      const lum = (c) => {
        const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
      };
      const ratio = (a, b) => {
        const la = lum(a), lb = lum(b);
        return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
      };
      const over = (fg, bg, a) => fg.map((v, i) => Math.round(a * v + (1 - a) * bg[i]));
      const host = window.__card;
      const rawBg = getComputedStyle(host).getPropertyValue("--card-background-color").trim();
      const bg = parse(rawBg) || parse(getComputedStyle(host).backgroundColor) || [255, 255, 255];
      const root = host.shadowRoot;
      const against = (el, prop, floor) => {
        if (!el) return { missing: true, ratio: 0, floor };
        const cs = getComputedStyle(el);
        const color = parse(cs[prop]) || parse(el.getAttribute(prop));
        const op = Number(cs.opacity);
        if (!color || !Number.isFinite(op)) return { missing: true, ratio: 0, floor };
        const r = ratio(over(color, bg, op), bg);
        return { missing: false, ratio: +r.toFixed(3), floor, ok: r >= floor };
      };
      const series = [...root.querySelectorAll(".series[data-key]")];
      const seriesWorst = series.reduce((w, el) => {
        const cs = getComputedStyle(el);
        const prop = (cs.stroke && cs.stroke !== "none") ? "stroke" : "fill";
        const m = against(el, prop, 3);
        return (!m.missing && m.ratio < w.ratio) ? { ...m, n: (w.n || 0) + 1 } : { ...w, n: (w.n || 0) + 1 };
      }, { ratio: Infinity, missing: series.length === 0, floor: 3, n: 0 });
      return {
        now: against(root.querySelector("line.now"), "stroke", 3),
        nowLabel: against(root.querySelector("text.now-label"), "fill", 4.5),
        estimatedEdge: against(root.querySelector("line.estimated-edge"), "stroke", 3),
        gridV: against(root.querySelector("line.grid.grid-v"), "stroke", 1.3),
        gridH: against(root.querySelector("line.grid.grid-h"), "stroke", 1.3),
        series: { ...seriesWorst, missing: series.length === 0 },
      };
    });
  };
  for (const [label, theme] of [["HA light theme", HA_LIGHT], ["HA dark theme", HA_DARK]]) {
    const g = await graphicsOf(theme);
    check(`C4 now marker clears 3:1 (${label})`,
      !g.now.missing && g.now.ok, g.now.missing ? "missing .now" : `${g.now.ratio}:1`);
    check(`C4 now label clears 4.5:1 (${label})`,
      !g.nowLabel.missing && g.nowLabel.ok,
      g.nowLabel.missing ? "missing .now-label" : `${g.nowLabel.ratio}:1`);
    check(`C4 estimated-price edge clears 3:1 (${label})`,
      !g.estimatedEdge.missing && g.estimatedEdge.ok,
      g.estimatedEdge.missing ? "missing .estimated-edge" : `${g.estimatedEdge.ratio}:1`);
    check(`C4 vertical gridline is perceptible, not 3:1 (${label})`,
      !g.gridV.missing && g.gridV.ok && g.gridV.ratio < 3,
      g.gridV.missing ? "missing .grid.grid-v" : `${g.gridV.ratio}:1`);
    check(`C4 horizontal gridline is perceptible, not 3:1 (${label})`,
      !g.gridH.missing && g.gridH.ok && g.gridH.ratio < 3,
      g.gridH.missing ? "missing .grid.grid-h" : `${g.gridH.ratio}:1`);
    check(`C4 every .series[data-key] clears 3:1 (${label})`,
      !g.series.missing && g.series.ok,
      g.series.missing ? "no .series[data-key]" : `worst ${g.series.ratio}:1`);
  }

  // --- R8 D4-01 (#1522): keyboard reading order ---------------------------
  // The rules above each read a selector list, and a control no list names is
  // a control no rule measures. Tab reaches every control by construction, so
  // this arm walks real Tab presses through every view -- the tile and each
  // dialog page -- at the three required viewports, and refuses a step whose
  // target sits more than ROW_TOL of a row ABOVE the previous stop while not
  // starting to the right of that stop's right edge: a jump back up the
  // screen, rather than a wrap to the next row or a move to the top of the
  // next column. Positions are read after the walk, with every scroller
  // reset, so a focus that scrolled the body is not a jump. A positive
  // tabindex would satisfy the walk by overriding the DOM order a screen
  // reader still follows, so it is refused outright.
  const ROW_TOL = 0.6;
  const orderPage = await browser.newPage({ viewport: { width: 375, height: 812 } });
  orderPage.on("pageerror", (err) => console.log(`  page error: ${err.message}`));
  await orderPage.goto("about:blank");
  await orderPage.addScriptTag({ path: CARD_SRC });
  await orderPage.evaluate(([frozen]) => {
    const Real = Date;
    class Frozen extends Real {
      constructor(...a) { super(...(a.length ? a : [frozen])); }
      static now() { return frozen; }
    }
    window.Date = Frozen;
  }, [Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000]);
  const tabWalk = async () => {
    await orderPage.evaluate(() => {
      window.__stops = [];
      if (document.activeElement) document.activeElement.blur();
    });
    for (let i = 0; i < 200; i++) {
      await orderPage.keyboard.press("Tab");
      const more = await orderPage.evaluate(() => {
        let el = document.activeElement;
        while (el && el.shadowRoot && el.shadowRoot.activeElement) el = el.shadowRoot.activeElement;
        if (!el || el === document.body) return false;
        const s = window.__stops;
        if (s.length && s[0] === el) return false;
        // A time input takes one Tab per field: one control, one stop.
        if (s[s.length - 1] !== el) s.push(el);
        return true;
      });
      if (!more) break;
    }
    return orderPage.evaluate(() => {
      window.scrollTo(0, 0);
      const scrollers = (n) => {
        const out = [];
        for (; n; n = n.parentNode || n.host) {
          if (n.nodeType === 1 && (n.scrollTop || n.scrollLeft)) out.push(n);
        }
        return out;
      };
      for (const el of window.__stops) for (const n of scrollers(el)) { n.scrollTop = 0; n.scrollLeft = 0; }
      const root = window.__card ? window.__card.shadowRoot : document;
      return {
        positive: [...root.querySelectorAll("[tabindex]")].filter((e) => e.tabIndex > 0).length,
        stops: window.__stops.map((el) => {
          const r = el.getBoundingClientRect();
          const cls = el.getAttribute("class") || "";
          return { who: `${el.tagName.toLowerCase()}.${cls.split(" ")[0]}`,
                   x: r.left, y: r.top, w: r.width, h: r.height };
        }).filter((s) => s.w > 0 && s.h > 0),
      };
    });
  };
  const backward = (stops) => {
    const out = [];
    for (let i = 1; i < stops.length; i++) {
      const a = stops[i - 1], b = stops[i];
      const row = Math.max(a.h, b.h, 16);
      if (a.y - b.y > ROW_TOL * row && b.x <= a.x + a.w) {
        out.push(`${a.who}@(${a.x.toFixed(0)},${a.y.toFixed(0)}) -> ${b.who}@(${b.x.toFixed(0)},${b.y.toFixed(0)})`);
      }
    }
    return out;
  };
  // The positive control: a hand-built row whose DOM order runs against its
  // painted order, and its null twin -- the rule must fire on the first and
  // only the first, or it is measuring something other than reading order.
  const handBuilt = async (dir) => {
    await orderPage.evaluate((d) => {
      window.__card = null;
      document.body.innerHTML =
        `<div style="display:flex;flex-direction:${d};gap:12px;padding:12px">` +
        `<button>first</button><button>second</button><button>third</button></div>`;
    }, dir);
    return backward((await tabWalk()).stops);
  };
  const reversed = await handBuilt("column-reverse");
  const straight = await handBuilt("column");
  check("R8 D4-01 the reading-order rule fires on a hand-built out-of-order row",
    reversed.length === 2 && straight.length === 0,
    `reversed ${reversed.length}, straight ${straight.length} backward step(s)`);

  // Every view the card draws: the tile (and its score breakdown), and each
  // dialog page -- the plan page twice, the second with every optional
  // control the what-if panel and the zoom row can add, and the setup page
  // twice, the second with its entity picker open.
  const ORDER_VIEWS = [
    { name: "tile" }, { name: "tile_score", score: true },
    { name: "plan", page: "plan" }, { name: "plan_busy", page: "plan", busy: true },
    { name: "setup", page: "setup" },
    { name: "setup_picker", page: "setup", open: "dialog rect.setup-hit" },
    { name: "savings", page: "savings" },
    { name: "advisor", page: "advisor" },
  ];
  const orderCells = [];
  for (const [w, h] of [[375, 812], [768, 1024], [1280, 800]]) {
    await orderPage.setViewportSize({ width: w, height: h });
    for (const view of ORDER_VIEWS) {
      await orderPage.evaluate(async ([st0, w2, v]) => {
        const st = JSON.parse(JSON.stringify(st0));
        if (v.score) {
          // The headline stats, whose score pill is a control and opens a
          // breakdown panel.
          st["sensor.heat_pump_optimizer_predicted_savings"] = {
            state: "12.34", attributes: { unit_of_measurement: "SEK" } };
          st["sensor.heat_pump_optimizer_savings_percentage"] = { state: "8.2", attributes: {} };
          st["sensor.heat_pump_optimizer_optimization_score"] = {
            state: "82", attributes: { envelope: 90, machine: 75 } };
        }
        if (v.busy) {
          // Every optional what-if control drawn at once: DHW windows (a
          // select, two times and a remove each) and the override's
          // back-to-automatic button.
          st["sensor.heat_pump_optimizer_plan_dhw_heating"].attributes.dhw_windows_spec =
            "weekdays 06:00-08:30, weekend 08:00-09:30";
          st["sensor.heat_pump_optimizer_plan_space_heating"].attributes.manual_override = {
            active: true, expires_at: new Date(Date.now() + 5 * 3600e3).toISOString(),
            space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
        }
        document.body.innerHTML =
          `<style>body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}` +
          `heatpump-optimizer-card{display:block;width:${Math.min(w2 - 16, 500)}px;margin:8px}</style>`;
        const card = document.createElement("heatpump-optimizer-card");
        card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
        card.hass = { states: st, language: "en" };
        document.body.appendChild(card);
        window.__card = card;
        const settle = async () => {
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
          await new Promise((r) => setTimeout(r, 120));
        };
        if (v.score) {
          card._scoreOpen = true;
          card._render();
        }
        if (v.page) {
          card._onCardClick({});
          card.dialog.page = v.page;
          card._render();
        }
        await settle();
        // The setup picker, opened from the keyboard as a user would: focus
        // a diagram row, press Enter. It overlays the diagram.
        if (v.open) {
          const hit = card.shadowRoot.querySelector(v.open);
          hit.focus();
          hit.dispatchEvent(new KeyboardEvent("keydown",
            { key: "Enter", bubbles: true, composed: true }));
          await settle();
        }
        // Zoomed in, the view's reset button is enabled and joins the walk.
        if (v.busy) {
          card.shadowRoot.querySelector("dialog .vc-in").click();
          await settle();
        }
      }, [clipStates, w, view]);
      const walk = await tabWalk();
      orderCells.push({ w, h, view: view.name, n: walk.stops.length, positive: walk.positive,
                        back: backward(walk.stops) });
    }
  }
  await orderPage.close();
  console.log(`        tab stops: ${orderCells.map((c) => `${c.w} ${c.view}=${c.n}`).join(", ")}`);
  const jumps = orderCells.filter((c) => c.back.length);
  check("R8 D4-01 no Tab step jumps back up the screen, on any view at 375, 768 or 1280",
    jumps.length === 0,
    jumps.length
      ? jumps.map((c) => `${c.w}x${c.h} ${c.view}: ${c.back.join(" | ")}`).join("; ")
      : `${orderCells.length} cell(s), ${orderCells.reduce((s, c) => s + c.n, 0)} stop(s)`);
  check("R8 D4-01 and no control reorders Tab with a positive tabindex",
    orderCells.every((c) => c.positive === 0),
    orderCells.filter((c) => c.positive).map((c) => `${c.w} ${c.view}: ${c.positive}`).join(", "));
  // The walk's own control: a view that yielded a handful of stops would pass
  // the rule above for having nothing to order.
  check("R8 D4-01 and the walk reached the controls of every view",
    orderCells.every((c) => c.n >= 3) &&
      orderCells.filter((c) => c.view === "plan").every((c) => c.n >= 20),
    orderCells.map((c) => `${c.w} ${c.view}=${c.n}`).join(", "));

  // P9: the rendered-property rules over the state grid (see p9Grid above).
  await p9Grid({ browser, check, plan, cardSrc: readFileSync(CARD_SRC, "utf8"),
    log: (line) => console.log(`  ${line}`) });

  // B12: the README hero is a screenshot of this lane, not the card_rig
  // SVG B4 committed as an interim. Frozen at the payload's first sample
  // so the plot is the full horizon (same instant make_card_figures.mjs
  // uses). A committed PNG is not bit-stable across Chromium builds, so
  // CI never writes it; HPO_HERO_OUT is the generator. The check is that
  // this lane can take the picture: PNG magic, and a box the first
  // layout check already proved is a real tile.
  const heroAt = Date.parse(plan.space_plan.forecast[0].t);
  const heroPage = await browser.newPage({
    viewport: { width: 1024, height: 800 },
    deviceScaleFactor: 2,
  });
  try {
    await heroPage.goto("about:blank");
    await heroPage.addScriptTag({ path: CARD_SRC });
    await heroPage.evaluate(([st, theme, frozen]) => {
      const Real = Date;
      class Frozen extends Real {
        constructor(...a) { super(...(a.length ? a : [frozen])); }
        static now() { return frozen; }
      }
      window.Date = Frozen;
      const style = document.createElement("style");
      style.textContent =
        `body{margin:0;background:#fff;font-family:-apple-system,"Segoe UI",sans-serif}` +
        `.hero{padding:16px;background:#fff;display:inline-block}` +
        `heatpump-optimizer-card{display:block;width:900px;${theme}}`;
      document.head.appendChild(style);
      const wrap = document.createElement("div");
      wrap.className = "hero";
      const card = document.createElement("heatpump-optimizer-card");
      wrap.appendChild(card);
      document.body.appendChild(wrap);
      card.setConfig({ type: "custom:heatpump-optimizer-card" });
      card.hass = { states: st, language: "en" };
      window.__card = card;
    }, [states, HA_LIGHT, heroAt]);
    await heroPage.waitForTimeout(250);
    const heroBox = await heroPage.evaluate(() => {
      const card = window.__card;
      const svgs = card.shadowRoot ? [...card.shadowRoot.querySelectorAll("svg")] : [];
      let best = null;
      for (const svg of svgs) {
        const b = svg.getBoundingClientRect();
        if (!best || b.width * b.height > best.w * best.h) {
          best = { w: b.width, h: b.height };
        }
      }
      return best;
    });
    check("B12 hero card renders an svg with real size",
      heroBox !== null && heroBox.w > 600 && heroBox.h > 200,
      heroBox ? `${heroBox.w.toFixed(0)}x${heroBox.h.toFixed(0)} px` : "no svg");
    const shot = await heroPage.locator(".hero").screenshot({ type: "png" });
    check("B12 hero screenshot is a PNG of the dashboard tile",
      shot[0] === 0x89 && shot[1] === 0x50 && shot[2] === 0x4e && shot[3] === 0x47
        && shot.length > 20_000,
      `${shot.length} bytes`);
    const out = process.env.HPO_HERO_OUT;
    if (out) {
      writeFileSync(out, shot);
      console.log(`  wrote hero ${shot.length} bytes -> ${out}`);
    }
  } finally {
    await heroPage.close();
  }
} finally {
  await browser.close();
}

console.log(fails ? `\n${fails} BROWSER CHECK(S) FAILED` : "\nALL BROWSER CHECKS PASSED");
process.exit(fails ? 1 : 0);
