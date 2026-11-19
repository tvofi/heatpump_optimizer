// D4.M1 harness (round 11, seat D4-s1): the dashboard card in real Chromium over
// every item enumerate_m1.mjs prints (card_drift state x language), each at
// 375x812, 768x1024, 1280x800 x {light,dark} x {reduce,no-preference} x {fine,coarse}.
//
// Metric definitions (one per RESULT family):
//   contrast   = text runs (HTML text node owners + SVG <text>) whose composited
//                colour is below WCAG AA (4.5:1, 3:1 large) against what is under it,
//                measured by tests/card_browser.mjs:instrument() (__p9.measure).
//   overflow   = text runs clipped >0.5 px by an ancestor that cannot scroll to them.
//   overlap    = text-run pairs whose boxes intersect AND share >0 ink pixels.
//   small      = interactive targets under 24 px (44 px when the context is coarse)
//                that fail WCAG 2.5.8's spacing exception (__p9.measure's rule).
//   strict_small = the same targets against D4-criteria F1 as written (no exception).
//   tab_unreached = tabbable elements (tabIndex>=0, visible, not disabled/inert) in
//                the card's active scope that a Tab sweep never focuses.
//   focus_no_indicator = elements the Tab sweep focuses whose computed outline,
//                box-shadow, background, border, colour, fill and stroke (own and
//                parent) are all identical focused and unfocused.
//   focus_invisible = Tab stops on an element with no client rect / hidden.
//   hover_shift_targets = interactive targets whose hover (pointer moved from rest onto
//                its centre) moves or resizes any element in the active scope by
//                >0.5 px (border-box diff; pointer-following pop-ups and elements
//                appearing/vanishing excluded). hover_shift_sum = the PerformanceObserver
//                'layout-shift' value over the same hovers (reported, not keyed).
//   console_errors = console 'error' messages + uncaught page errors per render.
//   tab_backward = consecutive Tab steps whose next stop lies wholly above the previous one,
//                or on its row and wholly to its left, by scroll-independent layout positions
//                taken before the sweep (TABONLY=1 runs the keyboard sweep alone).
// Count keys: the value the production card delivers (computed style / geometry /
// focus of the card's own rendered nodes), never a fixture attribute.
//
// Run (from the export root; PW = a playwright package dir from tests/pwlane's lock,
// PLAYWRIGHT_BROWSERS_PATH = that lock's Chromium, here rev 1254 / 158.0.8127.18):
//   HPO_PLANDATA=$(mktemp -d)/plan.json PYTHONPATH=tests/hastub python3 tests/plan_view.py
//   PW=$HOME/pwlane/node_modules/playwright PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers-lock \
//     HPO_PLANDATA=<that plan.json> node dev/audit/rounds/round11/D4/s1/m1_browser.mjs
// Filters (comma lists): STATES=, LANGS=, VPS=375,768,1280, THEMES=light,dark,
//   MOTION=reduce,no-preference, POINTER=fine,coarse, WORKERS=3, OUT=<dir> (default mktemp).
//   PROBE='<expr of c, the card element>' records an in-page value per render (witness re-runs).
//   SHOT_TAG=<regex on the render tag> writes a viewport PNG witness into ./screens.
//   LIGHT=1 stops after the drive + dlgBody record (probe/witness runs); RESUME=1 appends to OUT.
//   SHOTS=1 writes JPEG screenshots into ./screens next to this file (en/light/reduce/fine).
// Perturbation: HPO_PERTURB='[["from","to"], ...]' rewrites the card source in memory
//   (each `from` must occur exactly once) before it is injected -- a one-line production edit.
// Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B9, Chromium 158.0.8127.18):
//   see REPORT.md for each RESULT's value; counts are exact (+-0), times provisional.
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_SPACE, DEFAULT_DHW, HOUR, planStates, setupSensorStates, qaTopologies, layoutCatalogTopo,
  withActuals, historyApi, realisticHistory, EDITOR_TAG,
} from "../../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, "../../../../../..");
const t0wall = Date.now();
const cpu0 = process.cpuUsage();

// ---- the card source, perturbed in memory --------------------------------------
let cardSrc = readFileSync(path.join(REPO, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8");
const perturb = process.env.HPO_PERTURB ? JSON.parse(process.env.HPO_PERTURB) : [];
for (const [from, to] of perturb) {
  const n = cardSrc.split(from).length - 1;
  if (n !== 1) { console.error(`HPO_PERTURB: "${from.slice(0, 60)}" occurs ${n} times, need 1`); process.exit(2); }
  cardSrc = cardSrc.replace(from, to);
}
console.log(`perturbations applied: ${perturb.length}`);

// ---- the committed lane instrument, by text (card_browser.mjs runs at import) ---
const laneSrc = readFileSync(path.join(REPO, "tests/card_browser.mjs"), "utf8");
const iStart = laneSrc.indexOf("function instrument() {");
const iEnd = laneSrc.indexOf("\n}\n", iStart);
if (iStart < 0 || iEnd < 0) { console.error("instrument() not found in tests/card_browser.mjs"); process.exit(2); }
const instrumentSrc = laneSrc.slice(iStart, iEnd + 2);
const thStart = laneSrc.indexOf("const THEMES = {");
const thEnd = laneSrc.indexOf("\n};", thStart);
const THEMES = new Function(`${laneSrc.slice(thStart, thEnd + 3)} return THEMES;`)();

// ---- the plan payload ---------------------------------------------------------
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !existsSync(planPath)) { console.error("set HPO_PLANDATA to a plan_view.py payload"); process.exit(2); }
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;

// ---- the states: tests/card_drift.mjs's STATES, rebuilt for a real DOM ---------
const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
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
  const heating = new Set(st[DEFAULT_SPACE].attributes.forecast.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
  st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) => heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
  return st;
};
const setupStates = (topo, extra) => {
  const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
  st[DEFAULT_SPACE].attributes.setup_topology = topo;
  return st;
};
const woodFuelStates = (fuel) => { const st = planStates(plan); st[DEFAULT_SPACE].attributes.wood_fuel = fuel; return st; };
const awayPlanStates = ({ sw = false, resolved = false } = {}) => {
  const st = planStates(plan);
  st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] = { state: "unknown", attributes: {} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = { state: resolved ? "on" : "off",
    attributes: { source: resolved && !sw ? "person.alice" : "none" } };
  return st;
};
const bigStates = () => {
  const st = {};
  for (let i = 0; i < 400; i++) {
    st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = { state: "20.0",
      attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` } };
  }
  st["sensor.vedpanna_temperatur_temperature"] = { state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  return st;
};
const advisorStates = (cands) => {
  const st = setupStates(qaTopologies().base);
  st[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: cands };
  return st;
};
const savingsAttr = {
  state: "100.00",
  attributes: {
    unit_of_measurement: "SEK",
    savings_months: [
      { month: "2026-01", baseline_sek: 800, actual_sek: 652, savings_sek: 148, savings_pct: 18.5, estimated: false },
      { month: "2026-02", baseline_sek: 800, actual_sek: 700, savings_sek: 100, savings_pct: 12, estimated: true },
    ],
    receipts: [{
      month: "2026-01",
      lines: { spot: { kwh: 1238, sek: 498 }, grid_fee: { kwh: 1238, sek: 74 }, capacity: { kwh: 0, sek: 40 },
        space: { kwh: 900, sek: 360 }, savings_baseline: { kwh: 1300, sek: 646 } },
      basis: ["spot", "grid_fee", "capacity"], total_sek: 612, capacity_peak_kw: 5.8, compressor_starts: 212,
      reasons: { scheduled: { kwh: 200, sek: 96 }, cheap_price: { kwh: 900, sek: 312 } },
    }],
    plan_replay: {
      day: "2026-02-14", start: "2026-02-14T00:05:00+01:00", step_minutes: 15,
      room: Array.from({ length: 97 }, (_, i) => 21 - 0.01 * i),
      cost: Array.from({ length: 97 }, (_, i) => 0.5 * i),
      measured: { t: [6, 12, 24], room: [20.7, 20.4, 20.0], cost: [13, 25, 50] },
    },
  },
};
const wi = { what_if: true };
const page = (p) => [["cardClick"], ["page", p]];
const S = (name, o) => ({ name, config: {}, steps: [], service: false, ...o });
const t0 = plan.space_plan.forecast[0].t;
const t1 = plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t;
const STATES = [
  S("no_plan", { states: {} }),
  S("no_plan_expanded", { states: {}, steps: [["open"]] }),
  S("plan_inline", { states: planStates(plan) }),
  S("plan_inline_sv", { states: planStates(plan), lang: "sv-SE" }),
  S("plan_short_window", { states: planStates(plan), config: { hours: 6 } }),
  S("custom_title_currency", { states: planStates(plan), config: { title: "Värme", currency: "EUR", hours: 48 } }),
  S("hidden_series", { states: planStates(plan), config: { series: { outdoor: false, solar: false } },
    steps: [["open"], ["chip", "price"], ["x:close"]] }),
  S("score_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "score"]] }),
  S("expanded_plan", { states: planStates(plan), steps: [["cardClick"]] }),
  S("what_if_off", { states: planStates(plan), config: { what_if: false }, steps: [["cardClick"]] }),
  S("expanded_zoomed", { states: planStates(plan), steps: [["cardClick"], ["zoom", 0.25]] }),
  S("draft_dirty_menu_open", { states: planStates(plan), config: wi, steps: [["cardClick"], ["x:scrollChart"], ["dragDhw"], ["x:menuAtHours", "space", 2]] }),
  S("draft_mid_drag", { states: planStates(plan), config: wi, steps: [["cardClick"], ["x:dragDhwHold"]] }),
  S("whatif_edited", { states: scheduleStates(), config: wi, service: "empty", steps: [["cardClick"], ["x:whatifEdit"]] }),
  S("whatif_weekly", { states: (() => { const st = planStates(plan);
    st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30";
    st[DEFAULT_DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30"; return st; })(),
  config: wi, steps: [["cardClick"]] }),
  S("override_active", { states: (() => { const st = planStates(plan);
    const info = { active: true, expires_at: new Date(FROZEN + 5 * HOUR).toISOString(), space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
    st[DEFAULT_SPACE].attributes.manual_override = info; st[DEFAULT_DHW].attributes.manual_override = info; return st; })(),
  config: wi, steps: [["open"]] }),
  S("shared_steps", { states: sharedStepStates(), steps: [["cardClick"]] }),
  S("shared_steps_hover", { states: sharedStepStates(), steps: [["cardClick"], ["x:scrollChart"], ["hoverShared"]] }),
  S("tooltip_hover", { states: planStates(plan), steps: [["cardClick"], ["x:scrollChart"], ["hover", 5]] }),
  S("coarse_pointer", { states: planStates(plan), steps: [["cardClick"]], forcePointer: "coarse" }),
  S("reduced_motion", { states: planStates(plan), forceMotion: "reduce" }),
  S("setup_single_buffer", { states: setupStates(qaTopologies().base), steps: page("setup") }),
  S("setup_two_tank", { states: setupStates(qaTopologies().twoTank), steps: page("setup") }),
  S("setup_coil", { states: setupStates(qaTopologies().coil), steps: page("setup") }),
  S("advisor_page", { states: advisorStates([
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13, parameters: ["buffer_cooling_rate"], priced: true },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", spread_c: 2.87, parameters: ["lower_floor_loss_ratio"], priced: true },
    { key: "dhw_temp_entity", label: "Hot water temperature", priced: false, reason: "no_clamped_parameter" },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", priced: false, reason: "weather_backed" },
  ]), steps: page("advisor") }),
  S("savings_page", { states: { ...planStates(plan), "sensor.heat_pump_optimizer_monthly_savings": savingsAttr }, steps: page("savings") }),
  S("savings_empty", { states: planStates(plan), steps: page("savings") }),
  S("health_page", { states: setupStates(qaTopologies().base), steps: page("health") }),
  S("setup_not_published", { states: planStates(plan), steps: page("setup") }),
  S("advisor_empty", { states: advisorStates([]), steps: page("advisor") }),
  S("layout_editing_dragged", { states: setupStates(layoutCatalogTopo()), steps: [...page("setup"), ["clickSel", ".layout-edit-toggle"], ["x:layoutDrag"]] }),
  S("layout_editing_tidy", { states: setupStates(layoutCatalogTopo()), steps: [...page("setup"), ["clickSel", ".layout-edit-toggle"], ["x:layoutDrag"], ["clickSel", ".layout-tidy"]] }),
  S("picker_open_filtered", { states: setupStates(qaTopologies().base, bigStates()), steps: [...page("setup"), ["picker", "vedpanna"]] }),
  S("wood_alert", { states: woodFuelStates({ cheaper: true, show_whatif: true, ready: true, slots: [] }) }),
  S("wood_lane", { states: woodFuelStates({ cheaper: false, show_whatif: true, ready: true, slots: [{ start: t0, end: t1, source: "detected" }] }) }),
  S("wood_whatif", { states: woodFuelStates({ cheaper: false, show_whatif: true, ready: true, slots: [] }), config: wi, steps: [["cardClick"]] }),
  S("away_toggle", { states: awayPlanStates(), steps: [["cardClick"]] }),
  S("away_return", { states: awayPlanStates({ sw: true }), steps: [["cardClick"]] }),
  S("away_status", { states: awayPlanStates({ resolved: true }), steps: [["cardClick"]] }),
  S("editor_schema", { states: {}, editor: true }),
  S("history_panned", { states: withActuals(planStates(plan)), history: realisticHistory(FROZEN), steps: [["cardClick"], ["x:panBy", -10]] }),
  S("history_deep_panned", { states: withActuals(planStates(plan)), history: realisticHistory(FROZEN), steps: [["cardClick"], ["x:panBy", -40]] }),
  S("history_no_power", { states: withActuals(planStates(plan)), history: realisticHistory(FROZEN, { power: false }), steps: [["cardClick"], ["x:panBy", -20]] }),
  S("history_unavailable", { states: withActuals(planStates(plan)), history: {}, steps: [["cardClick"], ["x:panBy", -10]] }),
  S("history_pending", { states: withActuals(planStates(plan)), history: "never", steps: [["cardClick"], ["x:panBy", -10]] }),
];

// ---- the seat's in-page kit: drivers card_drift needs and __p9 lacks, plus the
// tab, focus-indicator and hover-shift sweeps --------------------------------------
function seatKit() {
  const K = {};
  window.__s1 = K;
  const card = () => document.querySelector("heatpump-optimizer-card");
  const root = () => card().shadowRoot;
  const scope = () => { const d = root().querySelector("dialog[open]"); return d && d.matches(":modal") ? d : root(); };
  const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const desc = (el) => {
    if (!el || !el.tagName) return String(el && el.nodeName);
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    const extra = el.dataset && (el.dataset.key || el.dataset.page || el.dataset.stat || el.dataset.channel) ? `[${el.dataset.key || el.dataset.page || el.dataset.stat || el.dataset.channel}]` : "";
    return (el.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "") + extra).slice(0, 70);
  };
  K.desc = desc;
  const pe = (type, x, y, target) => (target || window).dispatchEvent(new PointerEvent(type, { bubbles: true, composed: true,
    cancelable: true, clientX: x, clientY: y, pointerId: 1, isPrimary: true, button: 0, buttons: type === "pointerup" ? 0 : 1 }));
  const charts = () => [...root().querySelectorAll(".chartwrap svg")];
  const svgPx = (svg, vbX) => { const r = svg.getBoundingClientRect(); return r.left + (vbX / svg.viewBox.baseVal.width) * r.width; };
  K.drive = async (op, a1, a2) => {
    const c = card();
    if (op === "close") { c.dialog.close(); }
    else if (op === "scrollChart") {
      // A reader hovers or taps a chart they can see: bring the last chart into view
      // first, so a pointer step never lands below the fold (where nothing is hovered).
      const svgs = charts(), svg = svgs[svgs.length - 1];
      if (!svg) return "scrollChart";
      svg.scrollIntoView({ block: "center", inline: "nearest" });
    }
    else if (op === "menuAtHours") {
      await frame();
      const svgs = charts(), svg = svgs[svgs.length - 1], g = c.geomAt(svgs.length - 1);
      const t = g.windowStart + a2 * 3600000;
      const x = svgPx(svg, g.plotL + ((t - g.windowStart) / (g.windowEnd - g.windowStart)) * g.plotW);
      const lane = svg.querySelector(`rect.lane[data-channel='${a1}']`) || svg.querySelector(`[data-channel='${a1}']`);
      if (!lane) return `menuAtHours ${a1}`;
      const lr = lane.getBoundingClientRect();
      c.lanes.openMenu(a1, t, x, (lr.top + lr.bottom) / 2, svg, false);
    } else if (op === "dragDhwHold") {
      await frame();
      const svgs = charts(), svg = svgs[svgs.length - 1];
      const runs = c.manual.draft().dhw, [lo] = c.manual.bounds();
      const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
      const hit = svg && [...svg.querySelectorAll("[data-channel='dhw'][data-index]")].find((e) => e.dataset.index === String(i) && !e.dataset.edge);
      if (!hit) return "dragDhwHold";
      const g = c.geomAt(svgs.length - 1);
      const xOf = (t) => svgPx(svg, g.plotL + ((t - g.windowStart) / (g.windowEnd - g.windowStart)) * g.plotW);
      const hr = hit.getBoundingClientRect(), y = (hr.top + hr.bottom) / 2;
      pe("pointerdown", xOf(runs[i].start + 60000), y, hit); pe("pointermove", xOf(runs[i].start + 60000 + 3600000), y, window);
    } else if (op === "whatifEdit") {
      const inp = root().querySelector(".wi-dhw-min");
      if (!inp) return "whatifEdit input";
      inp.value = "42";
      c.whatIf.onInput({ target: inp, stopPropagation() {}, preventDefault() {} });
      clearTimeout(c.whatIf.timer); c.whatIf.timer = null;
      c.whatIf.onAddWindow({ stopPropagation() {}, preventDefault() {} });
    } else if (op === "layoutDrag") {
      await frame();
      const L = c.layoutEditor, svg = root().querySelector(".setup-svg");
      const box = L && (L.boxes || []).find((b) => b.place === "buffer_tank");
      if (!box || !svg) return "layoutDrag";
      const r = svg.getBoundingClientRect(), k = r.width / svg.viewBox.baseVal.width;
      const at = (p) => ({ clientX: r.left + p.x * k, clientY: r.top + p.y * k, target: { dataset: {} }, stopPropagation() {}, preventDefault() {} });
      const from = { x: box.x + box.w / 2, y: box.y + box.h / 2 }, to = { x: from.x + 40, y: from.y + 30 };
      L.onDown(at(from)); L.onMove(at({ x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 })); L.onUp(at(to));
    } else if (op === "panBy") { c.view.panBy(a1 * 3600000); await sleep(250); }
    else return `unknown ${op}`;
    await frame();
    return null;
  };

  // Tabbable elements in the active scope, crossing nested shadow roots.
  const deepAll = (r) => { const out = []; const walk = (n) => { for (const el of n.querySelectorAll("*")) { out.push(el); if (el.shadowRoot) walk(el.shadowRoot); } }; walk(r); return out; };
  const shown = (el) => {
    if (!el.getClientRects().length) return false;
    for (let n = el; n; n = parentOf(n)) { const cs = getComputedStyle(n); if (cs.visibility === "hidden" || cs.display === "none") return false; }
    return true;
  };
  K.tabbables = () => deepAll(scope()).filter((el) => el.tabIndex >= 0 && !el.disabled && !el.closest("[inert]") && shown(el) &&
    (el.matches("a[href], button, input:not([type=hidden]), select, textarea, summary, iframe, [contenteditable]") || el.hasAttribute("tabindex")));
  const STYLE_KEYS = ["outlineStyle", "outlineWidth", "outlineColor", "boxShadow", "backgroundColor", "borderTopColor", "borderBottomColor",
    "color", "fill", "stroke", "strokeWidth", "textDecorationLine", "opacity", "filter"];
  const snap = (el) => {
    const parts = [];
    for (const n of [el, parentOf(el)]) {
      if (!n || !n.tagName) continue;
      const cs = getComputedStyle(n);
      parts.push(STYLE_KEYS.map((k) => cs[k]).join("|"));
    }
    return parts.join("#");
  };
  K.deepActive = () => { let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement; return a; };
  K.tabPrep = () => {
    const ts = K.tabbables();
    ts.forEach((el, i) => el.setAttribute("data-s1tab", String(i)));
    K._rest = ts.map((el) => snap(el));
    // Scroll-independent layout position of every tabbable, taken before any focus
    // scrolls anything: its box plus the scroll offsets of every scrolling ancestor.
    K._pos = ts.map((el) => {
      const r = el.getBoundingClientRect(); let sx = scrollX, sy = scrollY;
      for (let n = parentOf(el); n && n.tagName; n = parentOf(n)) { sx += n.scrollLeft || 0; sy += n.scrollTop || 0; }
      return [+(r.left + sx).toFixed(1), +(r.top + sy).toFixed(1), +(r.right + sx).toFixed(1), +(r.bottom + sy).toFixed(1)];
    });
    K._seq = [];
    // A modal dialog keeps the focus the card gave it on opening (that stop is
    // recorded as the first); otherwise the sweep starts on a button before the card.
    const dlg = root().querySelector("dialog[open]");
    const modal = !!(dlg && dlg.matches(":modal"));
    const pre = document.getElementById("s1pre");
    if (!modal && pre) pre.focus();
    // Rest snapshots were taken with the opening focus in place: re-take that one blurred.
    const a = K.deepActive();
    if (modal && a && a.hasAttribute && a.hasAttribute("data-s1tab")) {
      a.blur(); K._rest[+a.getAttribute("data-s1tab")] = snap(a); a.focus({ focusVisible: true });
    }
    return ts.length;
  };
  K.tabStep = () => {
    const a = K.deepActive();
    if (!a || a === document.body) return { where: "body" };
    if (a.id === "s1pre" || a.id === "s1post") return { where: a.id };
    const r = a.getBoundingClientRect(), cs = getComputedStyle(a);
    // A straight pipe path is 0 px tall and still drawn: invisible means no box on both axes.
    const inv = !a.getClientRects().length || cs.visibility !== "visible" || (r.width < 1 && r.height < 1);
    const idx = a.getAttribute("data-s1tab");
    const now = snap(a);
    const rest = idx === null ? null : K._rest[+idx];
    return { where: "card", idx, d: desc(a), inv, ind: rest === null ? null : now !== rest, top: +r.top.toFixed(1), left: +r.left.toFixed(1), bottom: +r.bottom.toFixed(1), right: +r.right.toFixed(1), sy: scrollY, dlgTop: (() => { const d = root().querySelector("dialog[open]"); return d ? d.scrollTop : 0; })() };
  };
  // Hover: every interactive target in the active scope, layout-shift entries
  // collected per target by a PerformanceObserver.
  const INTERACTIVE = "button, a[href], input:not([type=hidden]), select, textarea, summary, [role=button], [role=tab], [role=option], [role=menuitem], [tabindex]";
  K.hoverTargets = () => {
    const els = deepAll(scope()).filter((el) => {
      if (el.tagName === "HA-CARD" || el.tagName === "DIALOG" || !shown(el) || el.disabled) return false;
      const cs = getComputedStyle(el);
      if (cs.pointerEvents === "none") return false;
      if (el.matches(INTERACTIVE)) return true;
      if (cs.cursor !== "pointer") return false;
      const p = parentOf(el); return !p || getComputedStyle(p).cursor !== "pointer";
    });
    els.forEach((el, i) => el.setAttribute("data-s1hov", String(i)));
    return els.length;
  };
  // D4-criteria F1 as written (no spacing exception): every hover target's box.
  K.targetSizes = (floor) => deepAll(scope()).filter((el) => el.hasAttribute("data-s1hov")).map((el) => {
    const r = el.getBoundingClientRect(); return { d: desc(el), w: +r.width.toFixed(1), h: +r.height.toFixed(1) };
  }).filter((t) => Math.min(t.w, t.h) < floor - 0.05);
  K.hoverPoint = (i) => {
    const el = deepAll(scope()).find((e) => e.getAttribute("data-s1hov") === String(i));
    if (!el) return null;
    let r = el.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) { el.scrollIntoView({ block: "center", inline: "nearest" }); r = el.getBoundingClientRect(); }
    const x = Math.min(Math.max((r.left + r.right) / 2, 1), innerWidth - 1), y = Math.min(Math.max((r.top + r.bottom) / 2, 1), innerHeight - 1);
    return { x, y, d: desc(el) };
  };
  K.shifts = [];
  try {
    new PerformanceObserver((l) => { for (const e of l.getEntries()) K.shifts.push({ v: e.value, src: (e.sources || []).map((s) => s.node ? desc(s.node.nodeType === 1 ? s.node : s.node.parentElement) : "?").slice(0, 3) }); })
      .observe({ type: "layout-shift", buffered: true });
  } catch (e) { K.noObserver = String(e); }
  K.takeShifts = () => { const s = K.shifts; K.shifts = []; return s; };
  // Rect-diff: every element in the active scope, its border box before and after a
  // hover. Pop-ups that exist to follow the pointer (tooltip, slot menu, crosshair)
  // and elements that appear or vanish (zero box on one side) are not shifts.
  const FOLLOW = ".tooltip, .slot-menu, .crosshair, .tt-row, .tt-time";
  K.rects = () => {
    const els = deepAll(scope());
    K._els = els;
    K._prev = els.map((el) => { const r = el.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; });
    return els.length;
  };
  K.moved = () => {
    const out = [];
    let max = 0;
    K._els.forEach((el, i) => {
      if (!el.isConnected || el.closest(FOLLOW)) return;
      const p = K._prev[i], r = el.getBoundingClientRect();
      if (p[2] * p[3] === 0 || r.width * r.height === 0) return;
      const d = Math.max(Math.abs(p[0] - r.left), Math.abs(p[1] - r.top), Math.abs(p[2] - r.width), Math.abs(p[3] - r.height));
      if (d > 0.5) { out.push(desc(el)); max = Math.max(max, d); }
    });
    return { n: out.length, max: +max.toFixed(2), els: [...new Set(out)].slice(0, 5) };
  };
  K.frame = frame;
}

// ---- host side ------------------------------------------------------------------
const csv = (v, d) => (v ? v.split(",").filter(Boolean) : d);
const VPS = { 375: [375, 812], 768: [768, 1024], 1280: [1280, 800] };
const LANG_TAG = { en: "en", de: "de-DE", sv: "sv-SE" };
const want = {
  states: csv(process.env.STATES, STATES.map((s) => s.name)),
  langs: csv(process.env.LANGS, ["de", "en", "sv"]),
  vps: csv(process.env.VPS, ["375", "768", "1280"]),
  themes: csv(process.env.THEMES, ["light", "dark"]),
  motion: csv(process.env.MOTION, ["reduce", "no-preference"]),
  pointer: csv(process.env.POINTER, ["fine", "coarse"]),
};
const OUT = process.env.OUT || mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1-"));
mkdirSync(OUT, { recursive: true });
const SHOTS = process.env.SHOTS === "1";
const SHOT_DIR = path.join(HERE, "screens");
if (SHOTS) mkdirSync(SHOT_DIR, { recursive: true });
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style id="theme"></style></head><body><button id="s1pre">before</button><div id="slot"></div><button id="s1post">after</button></body></html>`;
const historyApiSrc = historyApi.toString();

const cells = [];
for (const vp of want.vps) for (const theme of want.themes) for (const motion of want.motion) for (const pointer of want.pointer) cells.push({ vp, theme, motion, pointer });
const states = STATES.filter((s) => want.states.includes(s.name));

async function renderOne(ctx, cell, st, lang) {
  const tag = `${st.name}/${lang}/${cell.vp}/${cell.theme}/${cell.motion}/${cell.pointer}`;
  const rec = { tag, state: st.name, lang, ...cell, errors: [], missed: [] };
  const pg = await ctx.newPage();
  pg.on("console", (m) => { if (m.type() === "error") rec.errors.push(`console: ${m.text().slice(0, 200)}`); });
  pg.on("pageerror", (e) => rec.errors.push(`pageerror: ${String(e.message || e).slice(0, 200)}`));
  const tStart = Date.now();
  try {
    await pg.goto("http://hpo.test/");
    await pg.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await pg.addScriptTag({ content: cardSrc });
    await pg.addScriptTag({ content: `(${instrumentSrc})();` });
    await pg.addScriptTag({ content: `(${seatKit.toString()})();` });
    const coarse = (st.forcePointer || cell.pointer) === "coarse";
    const reduce = (st.forceMotion || cell.motion) === "reduce";
    await pg.evaluate(([themeCss, w, cfg, states2, langTag, svc, dark, hist, histSrc, editor, editorTag, reduceForced, coarseForced]) => {
      document.getElementById("theme").textContent =
        `html{${themeCss};background:var(--primary-background-color)}` +
        `body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
        `heatpump-optimizer-card, ${editorTag}{display:block;width:${w}px}`;
      // A state that pins a media answer (card_drift's coarse_pointer / reduced_motion)
      // pins it here too, whatever the cell's context says.
      if (reduceForced || coarseForced) {
        const orig = window.matchMedia.bind(window);
        window.matchMedia = (q) => {
          if ((reduceForced && q === "(prefers-reduced-motion: reduce)") || (coarseForced && q === "(pointer: coarse)")) {
            return { matches: true, media: q, onchange: null, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return true; } };
          }
          return orig(q);
        };
      }
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
      const hass = { states: states2, language: langTag, themes: { darkMode: dark } };
      if (svc === "empty") hass.callService = async () => ({ response: { results: {} } });
      if (hist === "never") hass.callApi = () => new Promise(() => {});
      else if (hist) { const mk = new Function(`return (${histSrc})`)(); hass.callApi = mk(hist).callApi; }
      const slot = document.getElementById("slot");
      if (editor) {
        const e = document.createElement(editorTag);
        e.setConfig({ type: "custom:heatpump-optimizer-card", hours: 12, series: { solar: false } });
        e.hass = hass;
        slot.appendChild(e);
        return;
      }
      const c = document.createElement("heatpump-optimizer-card");
      c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
      c.hass = hass;
      slot.appendChild(c);
      c.hass = hass;
    }, [THEMES[cell.theme], VPS[cell.vp][0] - 16, st.config, st.states, st.lang || LANG_TAG[lang], st.service, cell.theme === "dark",
      st.history === undefined ? null : st.history, historyApiSrc, !!st.editor, EDITOR_TAG, st.forceMotion === "reduce" && cell.motion !== "reduce", st.forcePointer === "coarse" && cell.pointer !== "coarse"]);
    await pg.waitForTimeout(reduce ? 60 : 400);
    if (st.editor) {
      rec.editor = await pg.evaluate((t) => { const e = document.querySelector(t); const r = e.getBoundingClientRect();
        return { children: e.shadowRoot ? e.shadowRoot.childElementCount : e.childElementCount, h: r.height, text: (e.shadowRoot || e).textContent.trim().slice(0, 80),
          undefinedTags: [...(e.shadowRoot || e).querySelectorAll("*")].filter((n) => n.tagName.includes("-") && !customElements.get(n.tagName.toLowerCase())).map((n) => n.tagName.toLowerCase()) }; }, EDITOR_TAG);
      rec.ms = Date.now() - tStart;
      await pg.close();
      return rec;
    }
    // Steps: runs of __p9 ops go through the lane's own driver, x: ops through the seat kit.
    let hover = null;
    const steps = st.steps.slice();
    while (steps.length) {
      if (steps[0][0].startsWith("x:")) {
        const [op, a1, a2] = steps.shift();
        const miss = await pg.evaluate(([o, x, y]) => window.__s1.drive(o, x, y), [op.slice(2), a1, a2]);
        if (miss) rec.missed.push(miss);
      } else {
        const run = [];
        while (steps.length && !steps[0][0].startsWith("x:")) run.push(steps.shift());
        const r = await pg.evaluate((s) => window.__p9.drive(s), run);
        rec.missed.push(...r.missed);
        if (r.hover) hover = r.hover;
      }
    }
    if (hover) { await pg.mouse.move(hover.x, hover.y); await pg.waitForTimeout(120); }
    if (!reduce) await pg.waitForTimeout(400);
    // PROBE: an in-page expression (a function of the card element) recorded per render,
    // for a witness re-run; never used by the counted checks.
    if (process.env.PROBE) rec.probe = await pg.evaluate((src) => { try { return new Function("c", `return (${src})`)(document.querySelector("heatpump-optimizer-card")); } catch (e) { return "probe threw: " + e.message; } }, process.env.PROBE);
    // The open dialog's scrolling body: how much of it a reader sees at once.
    rec.dlgBody = await pg.evaluate(() => {
      const r = document.querySelector("heatpump-optimizer-card").shadowRoot, d = r.querySelector("dialog[open]");
      const b = d && d.querySelector(".dlg-body");
      if (!b) return null;
      const db = d.getBoundingClientRect(), bb = b.getBoundingClientRect();
      return { client: b.clientHeight, scroll: b.scrollHeight, dlg: Math.round(db.height), head: Math.round(bb.top - db.top) };
    });
    if (process.env.LIGHT === "1") { rec.ms = Date.now() - tStart; await pg.close(); return rec; }
    const TABONLY = process.env.TABONLY === "1";
    // 1. geometry, contrast, targets, pop-ups (the lane's measure) + ink on candidate pairs.
    // TABONLY=1 (tab-order re-runs) skips 1 and 2 and runs the keyboard sweep alone.
    if (!TABONLY) {
    const m = await pg.evaluate((co) => window.__p9.measure(co), coarse);
    rec.runs = m.runs; rec.contrast = m.contrast; rec.overflow = m.overflow; rec.small = m.small; rec.popups = m.popups; rec.options = m.options;
    rec.unknownColour = m.unknownColour; rec.overlap = []; rec.inkFail = [];
    for (const p of m.boxPairs) {
      const { clip, why } = await pg.evaluate((q) => window.__p9.reveal(q), p);
      if (!clip) { rec.inkFail.push(`${p.at} x ${p.bt}: ${why}`); continue; }
      const shots = [];
      for (const i of [p.a, p.b]) {
        await pg.evaluate((k) => window.__p9.inkMode(k), i);
        shots.push("data:image/png;base64," + (await pg.screenshot({ clip })).toString("base64"));
      }
      await pg.evaluate(() => window.__p9.inkMode(null));
      const shared = await pg.evaluate(([a, b]) => window.__p9.inkShared(a, b), shots);
      if (shared > 0) rec.overlap.push(`${p.at} x ${p.bt} ${shared}px`);
    }
    if (process.env.SHOT_TAG && new RegExp(process.env.SHOT_TAG).test(tag)) {
      mkdirSync(SHOT_DIR, { recursive: true });
      await pg.screenshot({ path: path.join(SHOT_DIR, `witness_${tag.replace(/[^a-z0-9]+/gi, "_")}.png`) });
    }
    if (SHOTS && lang === "en" && cell.theme === "light" && cell.motion === "reduce" && cell.pointer === "fine") {
      await pg.screenshot({ path: path.join(SHOT_DIR, `${st.name}_${cell.vp}.jpg`), type: "jpeg", quality: 55, fullPage: true });
    }
    // 2. hover layout shift over every interactive target.
    rec.settleShift = (await pg.evaluate(() => window.__s1.takeShifts())).reduce((a, s) => a + s.v, 0);
    const nh = await pg.evaluate(() => window.__s1.hoverTargets());
    rec.hoverTargets = nh; rec.hoverShift = []; let hsum = 0;
    rec.strictSmall = (await pg.evaluate((f) => window.__s1.targetSizes(f), coarse ? 44 : 24)).map((t) => `${t.d} ${t.w}x${t.h}`);
    for (let i = 0; i < nh; i++) {
      const pt = await pg.evaluate((k) => window.__s1.hoverPoint(k), i);
      if (!pt) continue;
      // From rest: the pointer leaves the card first, so a tooltip that follows the
      // pointer from the previous target is not read as this target's shift.
      await pg.mouse.move(0, 0);
      await pg.evaluate(() => window.__s1.frame());
      if (!reduce) await pg.waitForTimeout(200);
      await pg.evaluate(() => window.__s1.takeShifts());
      await pg.evaluate(() => window.__s1.rects());
      await pg.mouse.move(pt.x, pt.y);
      await pg.evaluate(() => window.__s1.frame());
      if (!reduce) await pg.waitForTimeout(200);
      await pg.evaluate(() => window.__s1.frame());
      const sh = await pg.evaluate(() => window.__s1.takeShifts());
      const mv = await pg.evaluate(() => window.__s1.moved());
      const v = sh.reduce((a, s) => a + s.v, 0);
      if (v > 0 || mv.n > 0) { hsum += v; rec.hoverShift.push({ target: pt.d, v: +v.toFixed(5), moved: mv.n, max: mv.max, src: [...new Set([...sh.flatMap((s) => s.src), ...mv.els])].slice(0, 5) }); }
    }
    rec.hoverShiftSum = +hsum.toFixed(5);
    }
    await pg.mouse.move(0, 0);
    // 3. keyboard: Tab through every focusable.
    const nt = await pg.evaluate(() => window.__s1.tabPrep());
    rec.tabbable = nt; const seen = new Set(); const seq = [];
    rec.noIndicator = []; rec.invisibleFocus = [];
    let outside = 0;
    for (let k = -1; k < nt * 2 + 6; k++) {
      if (k >= 0) await pg.keyboard.press("Tab");
      const s = await pg.evaluate(() => window.__s1.tabStep());
      if (s.where !== "card") { if (seq.length && ++outside >= 2) break; continue; }
      outside = 0;
      const key = s.idx === null ? `x:${s.d}` : s.idx;
      // A time/date input takes Tab between its own fields: same element, keep going.
      if (seq.length && key === (seq[seq.length - 1].idx === null ? `x:${seq[seq.length - 1].d}` : seq[seq.length - 1].idx)) continue;
      if (seen.has(key)) break;
      seen.add(key); seq.push(s);
      if (s.ind === false) rec.noIndicator.push(s.d);
      if (s.inv) rec.invisibleFocus.push(s.d);
    }
    rec.tabReached = seq.filter((s) => s.idx !== null).length;
    rec.tabExtra = seq.filter((s) => s.idx === null).map((s) => s.d);
    rec.tabUnreached = await pg.evaluate((got) => [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("[data-s1tab]")]
      .filter((e) => !got.includes(e.getAttribute("data-s1tab"))).map((e) => window.__s1.desc(e)), seq.map((s) => s.idx));
    rec.tabSeq = seq.map((s) => s.d);
    // Document-space boxes of each stop (viewport box + the scroll that focusing caused).
    rec.tabBoxes = seq.map((s) => [s.left, s.top + s.sy + s.dlgTop, s.right, s.bottom + s.sy + s.dlgTop]);
    // Visual order: each consecutive pair of stops, by the pre-focus layout positions.
    // Backward = the next stop lies wholly above the previous one (its bottom above the
    // previous top), or on the same row (vertical overlap) and wholly to its left.
    // The last-to-first wrap of a modal dialog's focus cycle is not counted.
    const pos = await pg.evaluate(() => window.__s1._pos);
    rec.tabBackward = [];
    for (let i = 1; i < seq.length; i++) {
      if (seq[i].idx === null || seq[i - 1].idx === null) continue;
      const p = pos[+seq[i - 1].idx], q = pos[+seq[i].idx];
      const above = q[3] < p[1] - 0.5;
      const sameRowLeft = !(q[3] < p[1] || q[1] > p[3]) && q[2] < p[0] - 0.5;
      const wrap = i === seq.length - 1 && false;
      if ((above || sameRowLeft) && !wrap) rec.tabBackward.push(`${seq[i - 1].d} -> ${seq[i].d} [${p.join(",")}] -> [${q.join(",")}]`);
    }
  } catch (e) {
    rec.threw = String((e && e.message) || e).slice(0, 300);
  }
  rec.ms = Date.now() - tStart;
  await pg.close();
  return rec;
}

const browser = await chromium.launch();
const jobs = [];
for (const cell of cells) for (const st of states) for (const lang of want.langs) jobs.push({ cell, st, lang });
const WORKERS = Number(process.env.WORKERS || 3);
const outFile = path.join(OUT, "renders.jsonl");
// RESUME=1 keeps the renders already in OUT/renders.jsonl and runs only the missing tags.
const done = new Set();
if (process.env.RESUME === "1" && existsSync(outFile)) {
  for (const l of readFileSync(outFile, "utf8").split("\n")) if (l.trim()) done.add(JSON.parse(l).tag);
} else writeFileSync(outFile, "");
const tagOf = (j) => `${j.st.name}/${j.lang}/${j.cell.vp}/${j.cell.theme}/${j.cell.motion}/${j.cell.pointer}`;
if (done.size) { const before = jobs.length; for (let i = jobs.length - 1; i >= 0; i--) if (done.has(tagOf(jobs[i]))) jobs.splice(i, 1); console.log(`resume: ${before - jobs.length} renders kept, ${jobs.length} to run`); }
const recs = [];
let next = 0;
const ctxs = new Map();
async function ctxFor(cell) {
  const k = JSON.stringify(cell);
  if (!ctxs.has(k)) {
    ctxs.set(k, (async () => {
      const ctx = await browser.newContext({ viewport: { width: VPS[cell.vp][0], height: VPS[cell.vp][1] }, deviceScaleFactor: 1,
        colorScheme: cell.theme, reducedMotion: cell.motion, hasTouch: cell.pointer === "coarse" });
      await ctx.clock.setFixedTime(FROZEN);
      await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: PAGE }));
      return ctx;
    })());
  }
  return ctxs.get(k);
}
// Check the media each context really answers (coarse via hasTouch, motion via reducedMotion).
{
  const probe = {};
  for (const cell of cells) {
    const ctx = await ctxFor(cell); const p = await ctx.newPage(); await p.goto("http://hpo.test/");
    probe[`${cell.pointer}/${cell.motion}`] = await p.evaluate(() => [matchMedia("(pointer: coarse)").matches, matchMedia("(prefers-reduced-motion: reduce)").matches]);
    await p.close();
  }
  console.log("media probe", JSON.stringify(probe));
}
async function worker() {
  while (next < jobs.length) {
    const j = jobs[next++];
    const ctx = await ctxFor(j.cell);
    const r = await renderOne(ctx, j.cell, j.st, j.lang);
    recs.push(r);
    writeFileSync(outFile, JSON.stringify(r) + "\n", { flag: "a" });
    if (recs.length % 100 === 0) console.log(`progress ${recs.length}/${jobs.length}`);
  }
}
await Promise.all(Array.from({ length: WORKERS }, worker));
await browser.close();

// ---- summary (over every render in OUT, resumed ones included) -------------------
recs.length = 0;
for (const l of readFileSync(outFile, "utf8").split("\n")) if (l.trim()) recs.push(JSON.parse(l));
const items = new Set(recs.map((r) => `${r.state}\t${r.lang}`));
const sum = (f) => recs.reduce((a, r) => a + (f(r) || 0), 0);
console.log(`chromium ${browser.version ? "" : ""}renders written to ${outFile}`);
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", recs.length, "renders");
R("items", items.size, "state x language items");
R("threw", sum((r) => r.threw ? 1 : 0), "renders");
R("missed_steps", sum((r) => r.missed.length), "steps");
R("contrast", sum((r) => (r.contrast || []).length), "text runs");
R("overflow", sum((r) => (r.overflow || []).length), "text runs");
R("overlap", sum((r) => (r.overlap || []).length), "run pairs");
R("small", sum((r) => (r.small || []).length), "targets");
R("popups", sum((r) => (r.popups || []).length), "pop-ups");
R("options", sum((r) => (r.options || []).length), "options");
R("console_errors", sum((r) => r.errors.length), "messages");
R("strict_small", sum((r) => (r.strictSmall || []).length), "targets under 24 px (44 coarse), no spacing exception (D4-criteria F1)");
R("tab_unreached", sum((r) => (r.tabUnreached || []).length), "elements");
R("focus_no_indicator", sum((r) => (r.noIndicator || []).length), "tab stops");
R("focus_invisible", sum((r) => (r.invisibleFocus || []).length), "tab stops");
R("tab_backward", sum((r) => (r.tabBackward || []).length), "consecutive Tab steps against visual order (pre-focus layout positions)");
R("hover_shift_renders", sum((r) => ((r.hoverShift || []).length ? 1 : 0)), "renders");
R("hover_shift_targets", sum((r) => (r.hoverShift || []).filter((h) => h.moved > 0).length), "hovered targets that moved other elements >0.5 px");
R("hover_shift_sum", sum((r) => r.hoverShiftSum).toFixed(4), "CLS");
const cpu = process.cpuUsage(cpu0);
R("wall", ((Date.now() - t0wall) / 1000).toFixed(1), "s provisional");
R("thread_factor", "n/a (node + chromium processes; no BLAS)");
R("load1", os.loadavg()[0].toFixed(2));
R("host_cpu", ((cpu.user + cpu.system) / 1e6).toFixed(1), "s provisional");
let swapins = "n/a";
try { const vm = readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m); if (vm) swapins = vm[1]; } catch (e) { /* none */ }
R("swapins", swapins);
