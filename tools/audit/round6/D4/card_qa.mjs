// D4 round-6 card QA: the real card in real Chromium, across the state ×
// viewport × theme × language × pointer × motion matrix the D4 brief names.
//
//   NODE_PATH=<tmp>/node_modules PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers \
//     HPO_PLANDATA=<plan.json> node tools/audit/round6/D4/card_qa.mjs \
//       --outdir tools/audit/round6/D4/shots [--json out.json]
//
// Measures, per mounted state, from real layout (getBoundingClientRect /
// getComputedStyle), never from the markup:
//   R1 text overflow   elements whose scrollWidth exceeds clientWidth by >1 px
//   R2 text overlap    pairwise >1 px intersection of two leaf text boxes
//   R3 hit targets     controls under 24 px (fine) / 44 px (coarse) on a side
//   R4 contrast        visible text vs its composited background, WCAG AA
//   R5 h-scroll        document horizontal overflow, px
//   R6 console errors  pageerror + console.error count
//   R7 tab order       focusables in DOM order; keyboard reach
//
// Baseline SHA: e336cc2c530882a142ef298de6420706d96a6300 (v6.6.9).
// Instrumented symbols: custom_components/heatpump_optimizer/www/
//   heatpump-optimizer-card.js -- the card's own _render() output and its
//   _coarsePointer() predicate (the arm the 44 px floor keys on).
//
// Modes (all optional; the bare command above is the canonical run):
//   --selfcheck            plant four cases the four counters must fire on
//   --motion               one narrow strip twice, per reduced-motion arm
//   --focus                real Tab walk (fine/light/en cells only)
//   --hover                real page.hover, per selector, layout shift in px
//   --shots                screenshots into --outdir
//   --only a,b             restrict to named states
//   --perturb <css>        append one style to the card's shadow root after
//                          render: the declaration a fix would add.  The
//                          target-floor finding's perturbation, run as
//                            --only score_open \
//                            --perturb '.hl-stat.hl-score{min-height:44px;'\
//                            'min-width:44px;box-sizing:border-box}'
//                          moves under_floor_cells 12 -> 0.
//   --plan <plan.json>     plan payload (or HPO_PLANDATA); tests/plan_view.py
// Expected: overflow_cells=0 overlap_cells=0 under_floor_cells=12
//   contrast_cells=0 hscroll_cells=0 error_cells=0, cells=528.
import { createRequire } from "node:module";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

const argv = process.argv.slice(2);
const argOf = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const planPath = argOf("--plan", process.env.HPO_PLANDATA);
const outdir = argOf("--outdir", path.join(repo, "tools/audit/round6/D4/shots"));
const jsonOut = argOf("--json", null);
const only = argOf("--only", null);      // comma list of state names
const shot = argv.includes("--shots");
const hover = argv.includes("--hover");
// --probe=<css> prints, for one cell, each match's rect and its ancestor
// background/position chain; it exists to settle a single overlap by hand.
const probeSel = argOf("--probe", null);
const doFocus = argv.includes("--focus");
// --perturb <css> appends one style block to the card's own shadow root AFTER
// the state has rendered (so a re-render cannot wipe it), which is where the
// fix for the target-floor finding would land: the declarations the floor
// template's selector list applies to every other control on that surface.
// Run it with --only <state> so one cell is measured with and without.
const perturbCss = argOf("--perturb", null);
// hover-revealed chrome and the controls a pointer lands on; each is hovered
// on its own freshly-mounted card so one hover cannot mask another.
const HOVER_SEL = [".chartwrap", ".chip", ".hl-stat.hl-score", ".expand", ".setup-hit", ".vc-out"];
if (!planPath || !existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py first`);
  process.exit(1);
}
mkdirSync(outdir, { recursive: true });
const plan = JSON.parse(readFileSync(planPath, "utf8"));

// Instrument control: every measured quantity is given a planted case it must
// fire on, so a zero elsewhere is a fact about the card and not a dead probe.
async function selfcheck() {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 900, height: 700 } })).newPage();
  await p.goto("about:blank");
  await p.addScriptTag({ content: IN_PAGE });
  const r = await p.evaluate(() => {
    const host = document.createElement("div");
    document.body.appendChild(host);
    const sr = host.attachShadow({ mode: "open" });
    sr.innerHTML =
      '<style>.o{width:40px;height:14px;white-space:nowrap;overflow:hidden}' +
      '.big{font-size:40px;line-height:1;color:#000;position:absolute;left:10px;top:400px}' +
      '.sm{font-size:12px;color:#000;position:absolute;left:20px;top:410px}' +
      '.t{width:12px;height:12px}' +
      '.lowbg{color:#888;background:#999;position:absolute;left:500px;top:500px;font-size:20px}' +
      '</style>' +
      '<div class="o">an overflowing sentence that cannot fit in forty pixels</div>' +
      '<div class="big">AB</div><div class="sm">cd</div>' +
      '<button class="t">x</button>' +
      '<div class="lowbg">faint</div>';
    window.__card = host;
    const m = window.__hpoMeasure({ floor: 24 });
    return { overflow: m.overflow.length, overlap: m.overlaps.length,
      occl: m.occluded.length, under: m.under.length, contrast: m.contrastBad.length };
  });
  console.log("SELFCHECK " + JSON.stringify(r));
  const ok = r.overflow >= 1 && r.overlap >= 1 && r.under >= 1 && r.contrast >= 1;
  console.log(`RESULT selfcheck_control=${ok ? "fires" : "DEAD"} ` +
    `overflow=${r.overflow} overlap=${r.overlap} under=${r.under} contrast=${r.contrast}`);
  await b.close();
  process.exit(ok ? 0 : 2);
}

const SPACE = "sensor.heat_pump_optimizer_plan_space_heating";
const DHW = "sensor.heat_pump_optimizer_plan_dhw_heating";
const SOLAR = "sensor.heat_pump_optimizer_solar_irradiance";
const HOUR = 3600000;

// --- states, mirrored from tests/card_rig.mjs:planStates -------------------
const planStates = () => {
  const solar = plan.space_plan.forecast.map((p, i) => ({
    t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
  }));
  return {
    [SOLAR]: { state: "120", attributes: { forecast: solar, source: "open_meteo",
      friendly_name: "Solar Irradiance", plan_kind: "solar" } },
    [SPACE]: { state: "3 slots planned", attributes: {
      forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
      total_energy_kwh: plan.space_plan.total_energy_kwh,
      total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now,
      friendly_name: "Space Heating Plan", plan_kind: "space" } },
    [DHW]: { state: "4 slots planned", attributes: {
      forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
      total_energy_kwh: plan.dhw_plan.total_energy_kwh,
      total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now,
      friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  };
};

const TEMP_DOMAINS = ["sensor", "number", "input_number"];
function qaTopology() {
  return {
    two_zone: true, dhw: true, valve_mode: "manual",
    buffer: { volume_l: 750, is_store: true, max_temp: 70 },
    wood: { present: true, volume_l: 500 },
    edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
      ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
      ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"]],
    slots: [
      { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone",
        entity: "sensor.livingroom", domains: TEMP_DOMAINS },
      { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone",
        entity: null, domains: TEMP_DOMAINS },
      { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank",
        entity: "sensor.tank", domains: TEMP_DOMAINS },
      { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank",
        entity: null, domains: TEMP_DOMAINS },
      { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor",
        entity: "sensor.outside", domains: TEMP_DOMAINS },
      { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump",
        entity: null, domains: ["switch", "input_boolean", "climate"] },
    ],
  };
}
const setupSensors = () => ({
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
});

const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
    lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
});

const awayStates = ({ sw = false, resolved = false } = {}) => {
  const st = planStates();
  st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] = { state: "unknown", attributes: {} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = {
    state: resolved ? "on" : "off", attributes: { source: "none" } };
  return st;
};

const woodStates = (fuel) => {
  const st = planStates();
  st[SPACE].attributes.wood_fuel = fuel;
  return st;
};

// The matrix cells: name -> { states, config, drive }
const STATES = [
  { name: "plan", states: planStates },
  { name: "no_plan", states: () => ({}) },
  // The error arm of the D4 brief: the plan sensor exists but is not
  // available, and the arm where every plan sensor is missing entirely.
  { name: "plan_unavailable", states: () => { const s = planStates();
      for (const k of [SPACE, DHW, SOLAR]) { s[k] = { ...s[k], state: "unavailable" }; }
      return s; } },
  { name: "plan_missing", states: () => { const s = { ...planStates() };
      for (const k of [SPACE, DHW, SOLAR]) delete s[k];
      return s; } },
  { name: "expanded", states: planStates, drive: "card._onCardClick({});" },
  { name: "whatif", states: planStates, config: { what_if: true }, drive: "card._onCardClick({});" },
  { name: "setup", states: () => { const s = { ...planStates(), ...setupSensors() };
      s[SPACE].attributes.setup_topology = qaTopology(); return s; },
    drive: "card._onCardClick({}); card.dialog.page='setup'; card._render();" },
  { name: "advisor", states: () => { const s = { ...planStates(), ...setupSensors() };
      s[SPACE].attributes.setup_topology = qaTopology();
      s[SPACE].attributes.sensor_advisor = { basis: "history", candidates: [
        { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13,
          parameters: ["buffer_cooling_rate"], priced: true },
        { key: "dhw_temp_entity", label: "Hot water temperature", priced: false,
          reason: "no_clamped_parameter" } ] };
      return s; },
    drive: "card._onCardClick({}); card.dialog.page='advisor'; card._render();" },
  { name: "away", states: () => awayStates({ resolved: true }), drive: "card._onCardClick({});" },
  { name: "wood_alert", states: () => woodStates({ cheaper: true, show_whatif: true, ready: true, slots: [] }) },
  { name: "score_open", states: () => ({ ...planStates(), ...statStates() }),
    drive: "const s=card.shadowRoot.querySelector('[data-stat=\"score\"]'); if(s){s.click();}" },
  { name: "hidden_series", states: planStates,
    config: { series: { outdoor: false, solar: false } },
    drive: "const c=[...card.shadowRoot.querySelectorAll('.chip')].find(e=>e.getAttribute('data-key')==='price'); if(c){c.click();}" },
  { name: "custom_title", states: planStates, config: { title: "Värme", currency: "EUR", hours: 48 } },
  { name: "short_window", states: planStates, config: { hours: 6 } },
  { name: "long_title", states: planStates,
    config: { title: "Heat pump optimizer plan for the upstairs flat and the garage", hours: 48 } },
  { name: "override", states: () => { const s = planStates();
      const info = { active: true, expires_at: new Date(Date.parse(plan.space_plan.forecast[0].t) + 5 * HOUR).toISOString(),
        space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
      s[SPACE].attributes.manual_override = info; s[DHW].attributes.manual_override = info;
      return s; }, config: { what_if: true }, drive: "card._onCardClick({});" },
  { name: "away_return", states: () => awayStates({ sw: true }), drive: "card._onCardClick({});" },
  { name: "wood_lane", states: () => { const t0 = plan.space_plan.forecast[0].t;
      const t1 = plan.space_plan.forecast[4].t;
      return woodStates({ cheaper: false, show_whatif: true, ready: true,
        slots: [{ start: t0, end: t1, source: "detected" }] }); } },
  { name: "whatif_windows", states: () => { const s = planStates();
      s[DHW].attributes.dhw_windows = "06:00-08:30";
      s[DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
      return s; }, config: { what_if: true }, drive: "card._onCardClick({});" },
  { name: "picker_open", states: () => { const s = { ...planStates(), ...setupSensors() };
      s[SPACE].attributes.setup_topology = qaTopology();
      for (let i = 0; i < 400; i++) s["sensor.zz_probe_" + String(i).padStart(3, "0")] =
        { state: "20.0", attributes: { unit_of_measurement: "°C", friendly_name: "Probe " + String(i).padStart(3, "0") } };
      s["sensor.vedpanna_temperatur_temperature"] = { state: "71.2",
        attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
      return s; },
    drive: "card._onCardClick({}); card.dialog.page='setup'; card._render();" +
      "const h=[...card.shadowRoot.querySelectorAll('.setup-hit')].find(e=>e.dataset.key==='wood_tank_top_entity');" +
      "if(h){h.dispatchEvent(new MouseEvent('click',{bubbles:true}));} const b=card.shadowRoot.querySelector('.sp-filter');" +
      "if(b){b.value='vedpanna'; b.dispatchEvent(new Event('input',{bubbles:true}));}" },
  { name: "savings", states: planStates,
    drive: "card._onCardClick({}); card.dialog.page='savings'; card._render();" },
  { name: "layout_edit", states: () => { const s = { ...planStates(), ...setupSensors() };
      s[SPACE].attributes.setup_topology = qaTopology(); return s; },
    drive: "card._onCardClick({}); card.dialog.page='setup'; card._render();" +
      "const t=card.shadowRoot.querySelector('.layout-edit-toggle'); if(t){t.dispatchEvent(new MouseEvent('click',{bubbles:true}));}" },
];

const VIEWPORTS = [
  { name: "375x812", width: 375, height: 812 },
  { name: "768x1024", width: 768, height: 1024 },
  { name: "1280x800", width: 1280, height: 800 },
];
const HA_LIGHT = "--primary-text-color:#212121;--secondary-text-color:#727272;" +
  "--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#fff;" +
  "--secondary-background-color:#e5e5e5;--warning-color:#ffa726;--error-color:#db4437;" +
  "--divider-color:rgba(0,0,0,.12);";
const HA_DARK = "--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;" +
  "--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#1c1c1c;" +
  "--secondary-background-color:#2c2c2c;--warning-color:#ffa726;--error-color:#db4437;" +
  "--divider-color:rgba(225,225,225,.12);";

// --- the in-page measurement ------------------------------------------------
const IN_PAGE = `
window.__hpoMount = async (spec) => {
  document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
  document.body.innerHTML = "";
  const style = document.createElement("style");
  style.className = "hpo-test";
  style.textContent = 'body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}' +
    'heatpump-optimizer-card{display:block;width:100%;' + (spec.theme || "") + '}';
  document.head.appendChild(style);
  const card = document.createElement("heatpump-optimizer-card");
  card.setConfig(Object.assign({ type: "custom:heatpump-optimizer-card" }, spec.config || {}));
  const hass = Object.assign({ states: spec.states || {} }, spec.hass || {});
  card.hass = hass; document.body.appendChild(card); card.hass = hass;
  window.__card = card;
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 60));
  if (spec.drive) { new Function("card", spec.drive)(card); }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 60));
  // The perturbation lands last: a style appended to the card's own shadow
  // root, after every render the mount performs, so nothing overwrites it.
  if (spec.patchCss) {
    const ps = document.createElement("style");
    ps.className = "hpo-patch";
    ps.textContent = spec.patchCss;
    card.shadowRoot.appendChild(ps);
    await new Promise((r) => requestAnimationFrame(r));
  }
};

window.__hpoMeasure = (opts) => {
  const host = window.__card;
  const floor = opts.floor;
  const parse = (s) => {
    if (!s || s === "transparent" || s === "none") return null;
    let m = s.match(/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
    if (m) return [ +m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4] ];
    m = s.match(/^#([0-9a-f]{3,8})$/i);
    if (m) { let h = m[1];
      if (h.length === 3) h = h.split("").map(c=>c+c).join("");
      return [ parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16), 1 ]; }
    return null;
  };
  const lum = (c) => { const f = (v) => { v/=255; return v<=0.03928? v/12.92 : ((v+0.055)/1.055)**2.4; };
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]); };
  const ratio = (a, b) => { const la=lum(a), lb=lum(b); return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05); };
  const over = (fg, bg, a) => fg.map((v,i)=> i<3 ? Math.round(a*v + (1-a)*bg[i]) : 1);
  const nodes = [];
  const walk = (root) => {
    for (const el of root.querySelectorAll("*")) {
      nodes.push(el);
      if (el.shadowRoot) walk(el.shadowRoot);
    }
  };
  walk(host.shadowRoot);
  const vis = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return false;
    if (Number(cs.opacity) < 0.05) return false;
    const b = el.getBoundingClientRect();
    return b.width > 0 && b.height > 0;
  };
  // WCAG 1.4.3 exempts inactive components; the card marks them disabled.
  const inactive = (el) => {
    for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode().host) || null) {
      if (n.disabled === true || n.getAttribute && n.getAttribute("aria-disabled") === "true") return true;
    }
    return false;
  };
  const ownText = (el) => [...el.childNodes].some(
    (n) => n.nodeType === 3 && n.textContent.trim().length > 0);
  // background: composite the translucent layers down to the nearest opaque one
  const upOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const bgOf = (el) => {
    const stack = [];
    let i = null;
    for (let n = el; n; n = upOf(n)) {
      const b = parse(getComputedStyle(n).backgroundColor);
      if (!b || b[3] <= 0.001) continue;
      stack.push(b);
      if (b[3] >= 0.99) { i = stack.length - 1; break; }
    }
    if (i === null) return [255, 255, 255, 1];
    let acc = stack[i].slice(0, 3);
    for (let k = i - 1; k >= 0; k--) acc = over(stack[k], acc, stack[k][3]);
    return [acc[0], acc[1], acc[2], 1];
  };
  // A modal <dialog> is painted over the card by design, so its children share
  // no surface with the compact card behind it; overlap is scoped per surface.
  const surfaceOf = (el) => {
    for (let n = el; n; n = upOf(n)) if (n.tagName === "DIALOG") return n;
    return null;
  };

  // Does this element paint an opaque layer over whatever is behind it, up to
  // its own surface?  A dropdown panel that covers background text is not a
  // readability defect; two transparent texts sharing a rect are.
  const occludes = (el, surface) => {
    let a = 0;
    for (let n = el; n; n = upOf(n)) {
      if (n === surface) break;
      const b = parse(getComputedStyle(n).backgroundColor);
      if (b && b[3] > 0.001) { a = b[3] + a * (1 - b[3]); }
      if (a >= 0.99) return true;
    }
    return a >= 0.99;
  };

  const overflow = [];
  const texts = [];
  const targets = [];
  const focusables = [];
  const motion = [];
  const elOf = new Map();
  let ord = 0;
  for (const el of nodes) {
    ord += 1;
    if (!el.getBoundingClientRect) continue;
    const clsAttr0 = String(el.getAttribute("class") || "");
    // motion is collected before the visibility gate: a hover-revealed control
    // (opacity 0, .viewctl) is exactly what carries the card's transitions.
    {
      const cs3 = getComputedStyle(el);
      const dur = Math.max(...String(cs3.transitionDuration || "0s").split(",").map((s) => parseFloat(s) || 0),
        ...String(cs3.animationDuration || "0s").split(",").map((s) => parseFloat(s) || 0));
      const anim = cs3.animationName && cs3.animationName !== "none";
      if (dur > 0 && !(cs3.transitionProperty === "none" && !anim))
        motion.push({ tag: el.tagName.toLowerCase(), cls: clsAttr0.slice(0, 30), dur });
    }
    if (!vis(el)) continue;
    const b = el.getBoundingClientRect();
    const clsAttr = clsAttr0;
    const role = el.getAttribute("role") || "";
    const isSvgText = el.namespaceURI === "http://www.w3.org/2000/svg" && el.tagName.toLowerCase() === "text";
    if (isSvgText) {
      if (!(el.textContent || "").trim()) continue;
      const bb = el.getBBox ? el.getBBox() : null;
      const fill = getComputedStyle(el).fill || el.getAttribute("fill") || "";
      const fg = parse(fill);
      if (fg) { const bg = bgOf(el.parentElement || el); const op = Number(getComputedStyle(el).opacity);
        const r = ratio(over(fg, bg, Number.isFinite(op)? op : 1), bg);
        texts.push({ kind: "svgtext", text: (el.textContent||"").trim().slice(0,40),
          ratio: +r.toFixed(2), font: Number(getComputedStyle(el).fontSize) || 0,
          x: b.x, y: b.y, w: b.width, h: b.height }); }
      continue;
    }
    if (ownText(el) && el.tagName !== "OPTION") {
      const cs = getComputedStyle(el);
      const t = (el.textContent || "").trim();
      if (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0) {
        overflow.push({ text: t.slice(0, 40), cls: clsAttr || el.tagName.toLowerCase(),
          scrollW: el.scrollWidth, clientW: el.clientWidth });
      }
      const fg = parse(cs.color);
      if (fg && !inactive(el)) {
        const bg = bgOf(el);
        const op = Number(cs.opacity);
        const r = ratio(over(fg, bg, Number.isFinite(op)? op : 1), bg);
        const fs = parseFloat(cs.fontSize) || 0;
        const bold = (parseInt(cs.fontWeight) || 400) >= 700;
        const large = fs >= 24 || (fs >= 18.66 && bold);
        const rec = { kind: "html", text: t.slice(0, 40), ratio: +r.toFixed(2),
          font: fs, large, cls: clsAttr, ord,
          x: b.x, y: b.y, w: b.width, h: b.height };
        texts.push(rec); elOf.set(rec, el);
      }
    }
    // interactive targets: what a pointer or Tab can actually land on
    const roleInteractive = ["button", "switch", "checkbox", "link", "tab", "menuitem"].includes(role);
    const natFocus = ["BUTTON", "INPUT", "SELECT", "A"].includes(el.tagName);
    const interactive = (natFocus || roleInteractive || (el.tabIndex >= 0)) && !inactive(el);
    if (interactive) {
      targets.push({ tag: el.tagName.toLowerCase(), cls: clsAttr,
        role, tabindex: el.getAttribute("tabindex"),
        w: +b.width.toFixed(2), h: +b.height.toFixed(2),
        min: +Math.min(b.width, b.height).toFixed(2), text: (el.textContent||"").trim().slice(0,24) });
    }
    // keyboard reachability: anything that can take focus, in composed order
    const tabIdx = el.getAttribute && el.getAttribute("tabindex");
    const foci = el.tagName === "BUTTON" || el.tagName === "INPUT" || el.tagName === "SELECT" ||
      el.tagName === "A" || el.tagName === "DIALOG" || (el.hasAttribute && el.hasAttribute("tabindex"));
    if (foci && tabIdx !== "-1") {
      const cs2 = getComputedStyle(el);
      const hidden = cs2.display === "none" || cs2.visibility === "hidden";
      focusables.push({ tag: el.tagName.toLowerCase(), cls: String(el.className || "").slice(0,40),
        role: (el.getAttribute("role") || ""), tabindex: tabIdx === null ? "natural" : tabIdx,
        w: +b.width.toFixed(1), h: +b.height.toFixed(1), hidden, disabled: el.disabled === true,
        label: (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 28) });
    }
  }
  // overlaps between leaf text boxes (HTML only; nested pairs skipped, since a
  // parent's own text node shares a rect with every child it contains)
  const sec = [];
  const occl = [];
  for (const a of texts) { if (a.kind !== "html") continue;
    for (const b of texts) { if (b.kind !== "html") continue;
      if (a === b) continue;
      const ea = elOf.get(a), eb = elOf.get(b);
      if (ea && eb && (ea.contains(eb) || eb.contains(ea))) continue;
      if (surfaceOf(ea) !== surfaceOf(eb)) continue;
      if (a.x > b.x || (a.x === b.x && a.y >= b.y)) {
        const ox = Math.min(a.x+a.w, b.x+b.w) - Math.max(a.x, b.x);
        const oy = Math.min(a.y+a.h, b.y+b.h) - Math.max(a.y, b.y);
        if (ox > 1 && oy > 1) {
          // paint order is not DOM order once z-index enters: ask the browser
          // what is actually on top at the centroid of the intersection.
          const cx = (Math.max(a.x, b.x) + Math.min(a.x + a.w, b.x + b.w)) / 2;
          const cy = (Math.max(a.y, b.y) + Math.min(a.y + a.h, b.y + b.h)) / 2;
          const root = (ea && ea.getRootNode && ea.getRootNode()) || document;
          let topEl = null;
          try { topEl = root.elementFromPoint ? root.elementFromPoint(cx, cy) : null; } catch (e) { topEl = null; }
          if (topEl && topEl.nodeType !== 1) topEl = null;
          const topEl0 = topEl;
          const isA = topEl && ea && (ea === topEl || ea.contains(topEl));
          const isB = topEl && eb && (eb === topEl || eb.contains(topEl));
          const rec = { a: a.text, ac: a.cls, b: b.text, bc: b.cls, ox:+ox.toFixed(1), oy:+oy.toFixed(1) };
          if (topEl && !isA && !isB) {
            // a third element sits between them
            occl.push(Object.assign(rec, { top: String(topEl.getAttribute("class") || topEl.tagName).slice(0, 30),
              bot: "a/b both" }));
          } else {
            const cover = !topEl ? ((a.ord > b.ord) ? ea : eb) : (isA ? ea : eb);
            const covered = (cover === ea) ? eb : ea;
            (occludes(cover, surfaceOf(cover)) ? occl : sec).push(Object.assign(rec, {
              top: String(cover.getAttribute("class") || cover.tagName).slice(0, 30),
              bot: String(covered.getAttribute("class") || covered.tagName).slice(0, 30) }));
          }
        }
      } } }

  const doc = document.documentElement;
  const under = targets.filter((t) => t.min < floor - 0.05);
  const contrastBad = texts.filter((t) => t.ratio < (t.large ? 3 : 4.5) - 0.01);
  // a tab stop a keyboard user can reach but cannot see is a trap, not a stop
  const ghostStops = focusables.filter((f) => !f.disabled && (f.w === 0 || f.h === 0));
  // horizontal spill past the card's own box, on the card surface only (the
  // modal dialog is deliberately outside it)
  const hostBox = host.getBoundingClientRect();
  let spill = 0, spillWho = "";
  for (const el of nodes) {
    if (surfaceOf(el) !== null) continue;
    if (!vis(el)) continue;
    const b = el.getBoundingClientRect();
    const out = Math.max(hostBox.left - b.left, b.right - hostBox.right, 0);
    if (out > spill) { spill = out; spillWho = el.tagName.toLowerCase() + "." + String(el.getAttribute("class") || "").slice(0, 30); }
  }
  return {
    overflow, overlaps: sec.slice(0, 8), occluded: occl.slice(0, 8), textCount: texts.length,
    targets: targets.length, under,
    contrastBad: contrastBad.slice(0, 12), contrastCount: texts.length,
    hScroll: doc.scrollWidth - doc.clientWidth,
    hostH: host.getBoundingClientRect().height,
    spill: +spill.toFixed(1), spillWho,
    // The tab walk excludes disabled controls (the browser does too), so the
    // count printed beside it must: a disabled button listed as a stop made
    // the printed order one longer than the walk that follows it.
    tabStops: focusables.filter((f) => !f.disabled).length,
    focusStopsOrder: focusables.filter((f) => !f.disabled).map((f) => f.tag + "." + f.cls +
      (f.role ? "[role=" + f.role + "]" : "")),
    ghostStops, motion,
  };
};

// Hover layout shift.  Synthetic MouseEvents do NOT set the CSS :hover
// pseudo-class (measured: the control read 0/204 landed), so the runner
// drives a real hover with page.hover between the snapshot and the diff.
window.__hpoSnap = (sel) => {
  const host = window.__card;
  const m = new Map();
  const walk = (root, pre) => {
    let i = 0;
    for (const el of root.querySelectorAll("*")) {
      i += 1;
      const b = el.getBoundingClientRect();
      if (b.width > 0 && b.height > 0)
        m.set(pre + i + "." + el.tagName + "." + String(el.getAttribute("class") || ""), [b.x, b.y, b.width, b.height]);
      if (el.shadowRoot) walk(el.shadowRoot, pre + i + ":");
    }
  };
  walk(host.shadowRoot, "");
  window.__hpoSnapPrev = m;
  const vc = host.shadowRoot.querySelector(".viewctl");
  // the hover's own effect on the hovered element: a colour or background
  // change proves the pointer landed even where .viewctl plays no part.
  const t = sel ? host.shadowRoot.querySelector(sel) : null;
  window.__hpoTStyle = t ? getComputedStyle(t).cssText + getComputedStyle(t).backgroundColor +
    getComputedStyle(t).color + getComputedStyle(t).outlineColor : null;
  return { n: m.size, opB: vc ? Number(getComputedStyle(vc).opacity) : null };
};
window.__hpoDiff = (sel) => {
  const host = window.__card;
  const before = window.__hpoSnapPrev || new Map();
  const m = new Map();
  const walk = (root, pre) => {
    let i = 0;
    for (const el of root.querySelectorAll("*")) {
      i += 1;
      const b = el.getBoundingClientRect();
      if (b.width > 0 && b.height > 0)
        m.set(pre + i + "." + el.tagName + "." + String(el.getAttribute("class") || ""), [b.x, b.y, b.width, b.height]);
      if (el.shadowRoot) walk(el.shadowRoot, pre + i + ":");
    }
  };
  walk(host.shadowRoot, "");
  const moved = [];
  for (const [k, a] of before) {
    const b = m.get(k);
    if (!b) continue;
    const d = Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]), Math.abs(a[3] - b[3]));
    if (d > 0.5) moved.push({ k, d: +d.toFixed(1) });
  }
  moved.sort((x, y) => y.d - x.d);
  const vc = host.shadowRoot.querySelector(".viewctl");
  const t2 = sel ? host.shadowRoot.querySelector(sel) : null;
  const tChanged = t2 && window.__hpoTStyle !== null
    ? (getComputedStyle(t2).cssText + getComputedStyle(t2).backgroundColor +
       getComputedStyle(t2).color + getComputedStyle(t2).outlineColor) !== window.__hpoTStyle
    : null;
  return { max: moved.length ? moved[0].d : 0, moved: moved.slice(0, 6), tChanged,
    opA: vc ? Number(getComputedStyle(vc).opacity) : null };
};
// Keyboard focus walk: reaches by a REAL Tab keypress so :focus-visible
// matches; recorded by the runner.  WCAG 2.4.7.
// Keyboard focus walk helpers.  Focus must move by a REAL Tab keypress or
// :focus-visible never matches, so the runner drives the keys and the page
// only records.  WCAG 2.4.7 (focus visible).
window.__focusReset = () => {
  const host = window.__card;
  if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  const els = [...host.shadowRoot.querySelectorAll("button,[tabindex],input,select,a,summary")]
    .filter((e) => !e.disabled && e.getBoundingClientRect().width + e.getBoundingClientRect().height > 0);
  const st = (el) => { const cs = getComputedStyle(el);
    return [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow,
      cs.backgroundColor, cs.borderTopColor, cs.fill, cs.stroke, cs.strokeWidth,
      cs.textDecorationLine].join("|"); };
  window.__focusEls = els;
  window.__focusBefore = els.map(st);
  window.__focusOut = [];
  window.__focusPrev = null;
};
window.__focusTake = (i) => {
  const host = window.__card;
  let a = document.activeElement;
  while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
  const els = window.__focusEls;
  const idx = els.indexOf(a);
  const st = (el) => { const cs = getComputedStyle(el);
    return [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow,
      cs.backgroundColor, cs.borderTopColor, cs.fill, cs.stroke, cs.strokeWidth,
      cs.textDecorationLine].join("|"); };
  let rec;
  if (a === document.body || a === host) rec = { tag: "(host)", cls: "", reached: false };
  else {
    // a UA-internal segment of a composite control (a time input's hour field)
    // resolves to the same element as the control itself; keep it once.
    if (window.__focusPrev === a) return { tag: a.tagName.toLowerCase(), cls: "", reached: false, dup: true };
    window.__focusPrev = a;
    rec = { tag: a.tagName.toLowerCase(), cls: String(a.getAttribute("class") || "").slice(0, 30),
      label: (a.getAttribute("aria-label") || a.textContent || "").trim().slice(0, 22),
      reached: true,
      outline: getComputedStyle(a).outlineStyle !== "none" && parseFloat(getComputedStyle(a).outlineWidth) > 0,
      changed: idx >= 0 ? st(a) !== window.__focusBefore[idx] : null };
  }
  window.__focusOut.push(rec);
  return rec;
};
window.__focusDone = () => window.__focusOut;
`;

// --- run --------------------------------------------------------------------
if (argv.includes("--selfcheck")) await selfcheck();
// --motion runs one narrow strip twice, once per prefers-reduced-motion arm,
// so the motion count has a control arm it must move against.
const motionMode = argv.includes("--motion");
const VPS = motionMode ? VIEWPORTS.slice(0, 1) : VIEWPORTS;
const THEMES = motionMode ? [["light", HA_LIGHT]] : [["light", HA_LIGHT], ["dark", HA_DARK]];
const POINTERS = motionMode ? ["fine"] : ["fine", "coarse"];
const LANGS = motionMode ? ["en"] : ["en", "sv"];
const MOTIONS = motionMode ? ["no-preference", "reduce"] : ["no-preference"];
const results = [];
const errors = [];
const browser = await chromium.launch();
const want = (n) => !only || only.split(",").includes(n);
try {
  for (const vp of VPS) {
    for (const theme of THEMES) {
      for (const pointer of POINTERS) {
        for (const lang of LANGS) {
         for (const mo of MOTIONS) {
          const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
          const page = await ctx.newPage();
          const pageErrors = [];
          page.on("pageerror", (e) => pageErrors.push(String(e.message)));
          page.on("console", (m) => { if (m.type() === "error") pageErrors.push("console:" + m.text()); });
          await page.goto("about:blank");
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
          await page.addScriptTag({ content: IN_PAGE });
          await page.addScriptTag({ path: CARD_SRC });
          await page.evaluate(([ptr, mo]) => {
            const orig = window.matchMedia.bind(window);
            window.matchMedia = (q) => {
              if (q === "(pointer: coarse)") return { matches: ptr === "coarse", media: q,
                addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} };
              if (q === "(prefers-reduced-motion: reduce)") return { matches: mo === "reduce", media: q,
                addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} };
              return orig(q);
            };
          }, [pointer, mo]);
          const floor = pointer === "coarse" ? 44 : 24;
          for (const st of STATES) {
            if (!want(st.name)) continue;
            pageErrors.length = 0;
            const spec = { states: st.states(), config: st.config || null, drive: st.drive || null,
              theme: theme[1], hass: { language: lang === "sv" ? "sv-SE" : "en" } };
            if (perturbCss) spec.patchCss = perturbCss;
            await page.evaluate((s) => window.__hpoMount(s), spec);
            if (probeSel) {
              const p = await page.evaluate((q) => {
                const card = window.__card;
                const info = (el) => { const b = el.getBoundingClientRect(); const chain = [];
                  for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode().host) || null) {
                    chain.push(n.tagName + "." + String(n.getAttribute && n.getAttribute("class") || "").slice(0, 26) +
                      " bg=" + getComputedStyle(n).backgroundColor + " pos=" + getComputedStyle(n).position +
                      " z=" + getComputedStyle(n).zIndex);
                    if (n.tagName === "DIALOG") break; }
                  return { rect: [+b.x.toFixed(0), +b.y.toFixed(0), +b.width.toFixed(0), +b.height.toFixed(0)],
                    text: (el.textContent || "").trim().slice(0, 26), chain }; };
                return { order: [...card.shadowRoot.querySelectorAll(q)].map((e) => String(e.getAttribute("class"))),
                  els: [...card.shadowRoot.querySelectorAll(q)].map(info) };
              }, probeSel);
              console.log(`PROBE ${st.name}/${vp.name}/${theme[0]}/${pointer}/${lang}\n` + JSON.stringify(p, null, 1));
              await ctx.close();
              await browser.close();
              process.exit(0);
            }
            const m = await page.evaluate((o) => window.__hpoMeasure(o), { floor });
            if (hover && pointer === "fine") {
              const hs = [];
              for (const sel of HOVER_SEL) {
                await page.evaluate((s) => window.__hpoMount(s), spec);
                if (!(await page.$(sel))) continue;
                const pre = await page.evaluate((s) => window.__hpoSnap(s), sel);
                try { await page.hover(sel, { timeout: 4000 }); } catch (e) { continue; }
                await page.waitForTimeout(220);
                const post = await page.evaluate((s) => window.__hpoDiff(s), sel);
                hs.push({ sel, found: true, max: post.max, moved: post.moved,
                  ctrl: { opB: pre.opB, opA: post.opA, tChanged: post.tChanged } });
              }
              m.hover = hs;
              m.hoverMax = hs.reduce((n, h) => Math.max(n, h.max), 0);
            }
            const cell = { state: st.name, viewport: vp.name, theme: theme[0], pointer, lang,
              ...m, motion_arm: mo, errors: pageErrors.slice(0, 5) };
            if (doFocus && pointer === "fine" && theme[0] === "light" && lang === "en") {
              await page.evaluate(() => window.__focusReset());
              const n = await page.evaluate(() => (window.__focusEls || []).length);
              for (let i = 0; i < n; i++) { await page.keyboard.press("Tab");
                await page.evaluate((k) => window.__focusTake(k), i); }
              cell.focus = await page.evaluate(() => window.__focusDone());
            }
            results.push(cell);
            // Gallery: every state at both themes, all three viewports, fine
            // pointer, en (126 files).  The score pill is shot at every tier,
            // because it is the one control the floor measurement names.
            if (shot && lang === "en" && (pointer === "fine" || st.name === "score_open")) {
              const f = path.join(outdir,
                `${st.name}_${vp.name}_${theme[0]}_${pointer}.png`);
              await page.screenshot({ path: f, fullPage: true });
            }
          }
          await ctx.close();
         }
        }
      }
    }
  }
} finally {
  await browser.close();
}

// --- report -----------------------------------------------------------------
const sum = (k) => results.reduce((n, r) => n + (r[k] ? r[k].length : 0), 0);
console.log(`cells=${results.length}`);
console.log(`RESULT overflow_cells=${results.filter((r) => r.overflow.length).length} cells`);
console.log(`RESULT overlap_cells=${results.filter((r) => r.overlaps.length).length} cells`);
console.log(`RESULT under_floor_cells=${results.filter((r) => r.under.length).length} cells`);
console.log(`RESULT contrast_cells=${results.filter((r) => r.contrastBad.length).length} cells`);
console.log(`RESULT hscroll_cells=${results.filter((r) => r.hScroll > 0).length} cells`);
console.log(`RESULT error_cells=${results.filter((r) => r.errors.length).length} cells`);
console.log(`RESULT total_overflow=${sum("overflow")} total_overlap=${sum("overlaps")} ` +
  `total_under=${sum("under")} total_contrast=${sum("contrastBad")}`);

// distinct offender roll-ups
const roll = (pick, key) => {
  const m = new Map();
  for (const r of results) {
    for (const o of (pick(r) || [])) {
      const k = key(o);
      const e = m.get(k) || { k, n: 0, where: [] };
      e.n += 1;
      if (e.where.length < 3) e.where.push(`${r.state}/${r.viewport}/${r.theme}/${r.pointer}/${r.lang}`);
      m.set(k, e);
    }
  }
  return [...m.values()].sort((a, b) => b.n - a.n);
};
console.log("\n== overflow ==");
for (const e of roll((r) => r.overflow, (o) => `${o.cls}:${o.text}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
console.log("\n== under floor ==");
for (const e of roll((r) => r.under, (o) => `${o.tag}.${o.cls}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
console.log("\n== smallest targets ==");
{
  const all = [];
  for (const r of results) for (const t of r.under) all.push({ ...t, where: `${r.state}/${r.viewport}/${r.theme}/${r.pointer}/${r.lang}` });
  all.sort((a, b) => a.min - b.min);
  for (const t of all.slice(0, 12)) console.log(`  ${t.min}px ${t.tag}.${t.cls} "${t.text}" @ ${t.where}`);
}
console.log("\n== contrast ==");
for (const e of roll((r) => r.contrastBad, (o) => `${o.cls||o.kind}:${o.text}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
console.log("\n== overlap ==");
for (const e of roll((r) => r.overlaps, (o) => `${o.ac}:${o.a}|${o.bc}:${o.b}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
console.log("\n== occlusion (topmost element paints an opaque background) ==");
for (const e of roll((r) => r.occluded, (o) => `${o.top} OVER ${o.bot}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
if (hover) {
  console.log("\n== hover layout shift ==");
  let worst = 0, worstAt = "";
  const bySel = new Map();
  for (const r of results) {
    for (const h of (r.hover || [])) {
      const e = bySel.get(h.sel) || { sel: h.sel, max: 0, where: "" };
      if (h.max > e.max) { e.max = h.max; e.where = `${r.state}/${r.viewport}/${r.theme}/${r.pointer}/${r.lang}`; }
      bySel.set(h.sel, e);
      if (h.max > worst) { worst = h.max; worstAt = `${h.sel} @ ${r.state}/${r.viewport}/${r.theme}/${r.pointer}/${r.lang}`; }
    }
  }
  for (const e of [...bySel.values()].sort((a, b) => b.max - a.max))
    console.log(`  RESULT hover_shift ${e.sel} max=${e.max}px @ ${e.where}`);
  const ctrls = [];
  for (const r of results) for (const h of (r.hover || []))
    if (h.ctrl && h.ctrl.opA !== null) ctrls.push(h.ctrl);
  const reached = ctrls.filter((c) => c.opA > c.opB).length;
  const tchange = [];
  for (const r of results) for (const h of (r.hover || []))
    if (h.ctrl && h.ctrl.tChanged !== null) tchange.push(h.ctrl.tChanged);
  console.log(`  RESULT hover_shift_worst=${worst}px (${worstAt})`);
  console.log(`  RESULT hover_shift_cells=${results.filter((r) => r.hoverMax > 0.5).length} cells`);
  console.log(`  RESULT hover_ctrl_landed=${reached}/${ctrls.length} ` +
    `(.viewctl opacity rose on hover; applies only to .chartwrap)`);
  console.log(`  RESULT hover_ctrl_target_style_changed=` +
    `${tchange.filter(Boolean).length}/${tchange.length} (the hovered element's own computed style moved)`);
}
console.log("\n== errors ==");
for (const r of results) if (r.errors.length) console.log(`  ${r.state}/${r.viewport}/${r.theme}/${r.pointer}/${r.lang}: ${r.errors[0]}`);
console.log("\n== ghost tab stops ==");
for (const e of roll((r) => r.ghostStops, (o) => `${o.tag}.${o.cls}`)) console.log(`  ${e.n}x ${e.k} @ ${e.where[0]}`);
{
  const byArm = new Map();
  for (const r of results) {
    const k = r.motion_arm || "-";
    const e = byArm.get(k) || { n: 0, cells: 0, who: new Map() };
    e.n += r.motion ? r.motion.length : 0; e.cells += (r.motion || []).length ? 1 : 0;
    for (const m of (r.motion || [])) e.who.set(`${m.tag}.${m.cls}`, (e.who.get(`${m.tag}.${m.cls}`) || 0) + 1);
    byArm.set(k, e);
  }
  console.log("\n== motion (transition/animation duration > 0) by prefers-reduced-motion arm ==");
  for (const [k, e] of byArm)
    console.log(`  arm=${k}: cells_with_motion=${e.cells} elements=${e.n} ` +
      `${[...e.who.entries()].map(([w, c]) => w + " x" + c).join(", ")}`);
}
if (doFocus) {
  console.log("\n== keyboard focus (real Tab) ==");
  const seen = new Map();
  let stopsWithout = 0, stopsTotal = 0;
  for (const r of results) {
    if (!r.focus) continue;
    for (const f of r.focus) {
      if (!f.reached) continue;
      stopsTotal += 1;
      const visible = f.outline || f.changed === true;
      if (!visible) { stopsWithout += 1; seen.set(`${f.tag}.${f.cls}`,
        (seen.get(`${f.tag}.${f.cls}`) || { n: 0, where: `${r.state}/${r.viewport}` })); }
      const k = `${f.tag}.${f.cls}`;
      const e = seen.get(k) || { n: 0, where: `${r.state}/${r.viewport}`, no: 0, yes: 0 };
      if (visible) e.yes += 1; else e.no += 1;
      seen.set(k, e);
    }
  }
  for (const [k, e] of [...seen.entries()].sort((a, b) => (b[1].no || 0) - (a[1].no || 0)))
    console.log(`  ${e.no ? "NO-RING " : "        "}${k} visible=${e.yes} invisible=${e.no || 0} @ ${e.where}`);
  console.log(`  RESULT focus_stops=${stopsTotal} focus_stops_without_indicator=${stopsWithout}`);
}
console.log("\n== card-surface spill > 1px ==");
{
  const by = new Map();
  for (const r of results) {
    if (r.spill > 1) {
      const k = `${r.state}|${r.spillWho}`;
      const e = by.get(k) || { n: 0, worst: 0, where: [] };
      e.n++; e.worst = Math.max(e.worst, r.spill);
      if (e.where.length < 2) e.where.push(`${r.viewport}/${r.theme}/${r.pointer}/${r.lang}`);
      by.set(k, e);
    }
  }
  for (const [k, e] of [...by.entries()].sort((a, b) => b[1].worst - a[1].worst))
    console.log(`  ${e.n}x ${k} worst=${e.worst}px @ ${e.where[0]}`);
}
console.log("\n== tab stops (min, disabled excluded) ==");
const fc = results.filter((r) => r.state === "plan");
for (const r of fc.slice(0, 4)) console.log(`  ${r.state}/${r.viewport}/${r.pointer}/${r.lang}: ${r.tabStops} stops -> ${r.focusStopsOrder.join(" | ")}`);

if (jsonOut) writeFileSync(jsonOut, JSON.stringify(results, null, 1));
