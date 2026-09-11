// D4 round 3 -- real-browser geometry sweep of every card state.
//
// METRIC (one line): for each (card state x viewport x theme), the number of
// on-screen defects Chromium's layout engine reports -- HTML text boxes whose
// content is clipped (scrollWidth > clientWidth on an overflow-hidden box),
// SVG <text> EM boxes that overlap another <text> em box in both axes (a lead,
// not ink -- see the note beside that RESULT),
// descendants painted outside the <ha-card> box, focusable controls whose
// smaller side is under 24 px, text/background pairs under WCAG AA 4.5:1, and
// uncaught page errors.
//
// COMMAND (from the export root, one line):
//   HPO_PLANDATA=$TMPDIR/plandata-d4.json NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round3/D4/card_states_geometry.mjs
//
// The plan payload must exist first:
//   HPO_PLANDATA=$TMPDIR/plandata-d4.json PYTHONPATH=tests/hastub python3 tests/plan_view.py
//
// EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1 (8-core Apple
// M1, Chromium 1148 via Playwright 1.49.0, Node v20.10.0):
//   RESULT states_rendered=33 (exact) -- `node tests/card_drift.mjs --list`
//        enumerates 34; `editor_schema` is a JSON dump with no rendered tree
//        and is the one this sweep does not drive.
//   RESULT cells=396 (exact; 33 states x 3 viewports x 2 themes x 2 pointers)
//   RESULT clipped_text_cells=0 (exact)
//   RESULT clipped_overflow_cells=0 (exact)
//   RESULT doc_hscroll_cells=0 (exact)
//   RESULT page_error_cells=0 (exact)
//   RESULT render_failures=0 (exact)
//   RESULT low_contrast_sites=1 (exact) -- the `.chip.nodata` legend button
//   RESULT low_contrast_cells=24 (exact)
//   RESULT small_target_cells_coarse=24 (exact)
//   RESULT small_target_cells_fine=198 (exact)
//   RESULT scrollable_overflow_cells=24 (exact) -- the setup diagram on a
//        phone, which `@media (max-width:600px)` deliberately makes scroll.
//   RESULT svg_text_embox_overlap_cells=372 -- a LEAD, not ink; see the note
//        beside that line and section C of card_ux_defects.mjs.
// Every number here is a COUNT of pixels or elements, so it is contention
// immune; no wall or CPU time is taken.
//
// `--json <path>` dumps the full per-cell record. `--state <name>` restricts
// the sweep. `--shots <dir>` writes a PNG per failing cell.
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const CARD_SRC = path.join(
  repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

const testsDir = path.join(repo, "tests");
const defaultPlan = path.join(
  "/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`);
const planPath = process.env.HPO_PLANDATA || defaultPlan;
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py with HPO_PLANDATA set`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

const argv = process.argv.slice(2);
const argOf = (flag) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : null;
};
const onlyState = argOf("--state");
const jsonOut = argOf("--json");
const shotDir = argOf("--shots");
if (shotDir) mkdirSync(shotDir, { recursive: true });

// Home Assistant's own default theme tokens (the same two sets
// tests/card_browser.mjs resolves the card's colours against).
const HA_LIGHT = `
  --primary-text-color:#212121; --secondary-text-color:#727272;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#fff; --divider-color:rgba(0,0,0,.12);
  --primary-background-color:#fafafa; --secondary-background-color:#e5e5e5;
  --disabled-text-color:#bdbdbd; --error-color:#db4437; --warning-color:#ffa600;
  --success-color:#43a047; --info-color:#039be5;
`;
const HA_DARK = `
  --primary-text-color:#e1e1e1; --secondary-text-color:#9b9b9b;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#1c1c1c; --divider-color:rgba(225,225,225,.12);
  --primary-background-color:#111111; --secondary-background-color:#202020;
  --disabled-text-color:#6f6f6f; --error-color:#db4437; --warning-color:#ffa600;
  --success-color:#43a047; --info-color:#039be5;
`;

// Viewport, and the host width Home Assistant's masonry view gives a card
// there: one full-bleed column on a phone, one on a tablet, a 492 px
// masonry column on a desktop (HA's own --masonry-view-card-width).
const VIEWPORTS = [
  { name: "phone", w: 375, h: 812, host: 359 },
  { name: "tablet", w: 768, h: 1024, host: 736 },
  { name: "desktop", w: 1280, h: 800, host: 492 },
];

// The page-side driver: one function per state in tests/card_drift.mjs's
// STATES, minus `editor_schema` (a JSON dump, no geometry). Ported to real
// DOM events; the card's own public seams (`dialog`, `manual`, `lanes`,
// `whatIf`, `view`, `layoutEditor`) are driven exactly as card_drift does.
const DRIVER = `
window.__HPO = (() => {
  const HOUR = 3600000;
  const SOLAR = "sensor.heat_pump_optimizer_solar_irradiance";
  const SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
  const DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";
  let PLAN = null;
  const solarForecastFor = (p) => p.space_plan.forecast.map((q, i) => ({
    t: q.t, ghi: Math.max(0, 400 * Math.sin((i / p.space_plan.forecast.length) * Math.PI)),
  }));
  const planStates = () => ({
    [SOLAR]: { state: "120", attributes: {
      forecast: solarForecastFor(PLAN), source: "open_meteo",
      friendly_name: "Solar Irradiance", plan_kind: "solar" } },
    [SPACE]: { state: "3 slots planned", attributes: {
      forecast: PLAN.space_plan.forecast, slots: PLAN.space_plan.slots,
      total_energy_kwh: PLAN.space_plan.total_energy_kwh,
      total_cost: PLAN.space_plan.total_cost,
      active_now: PLAN.space_plan.active_now,
      friendly_name: "Space Heating Plan", plan_kind: "space" } },
    [DHW]: { state: "4 slots planned", attributes: {
      forecast: PLAN.dhw_plan.forecast, slots: PLAN.dhw_plan.slots,
      total_energy_kwh: PLAN.dhw_plan.total_energy_kwh,
      total_cost: PLAN.dhw_plan.total_cost,
      active_now: PLAN.dhw_plan.active_now,
      friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  });
  const setupSensorStates = () => ({
    "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "\\u00b0C" } },
    "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "\\u00b0C" } },
    "sensor.outside": { state: "unavailable", attributes: {} },
  });
  const TEMP_DOMAINS = ["sensor", "number", "input_number"];
  const qaTopologies = () => {
    const base = {
      two_zone: true, dhw: true, valve_mode: "manual",
      buffer: { volume_l: 750, is_store: true, max_temp: 70 },
      wood: { present: true, volume_l: 500 },
      edges: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
        ["mixing_valve","upper_zone"],["mixing_valve","lower_zone"],
        ["wood_tank","buffer_tank"],["heat_pump","dhw_tank"]],
      slots: [
        { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone",
          entity: "sensor.livingroom", domains: TEMP_DOMAINS },
        { key: "lower_floor_temp_entity", label: "Lower floor temperature",
          place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
        { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
          place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
        { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank",
          entity: null, domains: TEMP_DOMAINS },
        { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor",
          entity: "sensor.outside", domains: TEMP_DOMAINS },
        { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump",
          entity: null, domains: ["switch","input_boolean","climate"] },
      ],
    };
    const twoTank = JSON.parse(JSON.stringify(base));
    twoTank.two_tank_modelled = true;
    twoTank.layout = "two_tank_4way";
    twoTank.edges = [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
      ["wood_tank","mixing_valve"],["mixing_valve","upper_zone"],
      ["mixing_valve","lower_zone"],["heat_pump","dhw_tank"]];
    twoTank.slots = base.slots.concat([
      { key: "mixing_valve_target_entity", label: "Valve target", place: "mixing_valve",
        entity: null, domains: TEMP_DOMAINS },
      { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
        place: "mixing_valve", entity: null, domains: TEMP_DOMAINS },
    ]);
    const coil = JSON.parse(JSON.stringify(twoTank));
    coil.dhw_wood_coil = true;
    coil.edges = twoTank.edges.concat([["wood_tank","dhw_tank"]]);
    coil.slots.push({ key: "dhw_temp_entity", label: "Hot water temperature",
      place: "dhw_tank", entity: null, domains: TEMP_DOMAINS });
    return { base, twoTank, coil };
  };
  const layoutCatalogTopo = () => {
    const EDGES = {
      no_valve: [["heat_pump","buffer_tank"],["buffer_tank","upper_zone"],["buffer_tank","lower_zone"]],
      single_tank_valve: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
        ["mixing_valve","upper_zone"],["mixing_valve","lower_zone"]],
      two_tank_4way: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
        ["wood_tank","mixing_valve"],["mixing_valve","upper_zone"],["mixing_valve","lower_zone"]],
      valve_upper_direct_slab: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
        ["mixing_valve","upper_zone"],["buffer_tank","lower_zone"]],
      slab_shunt: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],
        ["mixing_valve","upper_zone"],["buffer_tank","slab_shunt"],["slab_shunt","lower_zone"]],
    };
    const catalog = [
      { key:"no_valve", label:"No mixing valve", description:"",
        requirement:"no throttling mixing valve configured", selectable:true, valid:false, edges:EDGES.no_valve },
      { key:"single_tank_valve", label:"One tank behind a valve", description:"",
        requirement:"a throttling mixing valve", selectable:true, valid:true, edges:EDGES.single_tank_valve },
      { key:"two_tank_4way", label:"Two tanks, one 4-way valve", description:"",
        requirement:"a throttling valve, two zones and a wood-tank top probe",
        selectable:true, valid:false, edges:EDGES.two_tank_4way },
      { key:"valve_upper_direct_slab", label:"Valve on the radiators, slab fed direct",
        description:"", requirement:"a throttling valve, two zones, and no wood-tank probe",
        selectable:true, valid:true, edges:EDGES.valve_upper_direct_slab },
      { key:"slab_shunt", label:"Separate slab shunt", description:"",
        requirement:"not selectable: no model variant exists yet",
        selectable:false, valid:false, edges:EDGES.slab_shunt },
    ];
    return {
      two_zone:true, dhw:false, valve_mode:"manual", layout:"valve_upper_direct_slab",
      two_tank_modelled:false, buffer:{volume_l:500,is_store:true,max_temp:65},
      wood:{present:false,volume_l:0},
      edges: EDGES.valve_upper_direct_slab.map((e)=>[e[0],e[1]]),
      catalog, positions:{},
      slots: [
        { key:"indoor_temp_entity", label:"Indoor temperature", place:"upper_zone",
          entity:"sensor.livingroom", domains:TEMP_DOMAINS },
        { key:"lower_floor_temp_entity", label:"Lower floor temperature", place:"lower_zone",
          entity:null, domains:TEMP_DOMAINS },
        { key:"buffer_tank_temp_entity", label:"Buffer tank temperature", place:"buffer_tank",
          entity:"sensor.tank", domains:TEMP_DOMAINS },
        { key:"mixing_valve_target_entity", label:"Valve target", place:"mixing_valve",
          entity:null, domains:TEMP_DOMAINS },
        { key:"outdoor_temp_entity", label:"Outdoor temperature", place:"outdoor",
          entity:"sensor.outside", domains:TEMP_DOMAINS },
        { key:"heat_pump_switch_entity", label:"Heat pump switch", place:"heat_pump",
          entity:null, domains:["switch","input_boolean","climate"] },
      ],
    };
  };
  const statStates = () => ({
    "sensor.heat_pump_optimizer_predicted_savings": { state:"12.34", attributes:{unit_of_measurement:"SEK"} },
    "sensor.heat_pump_optimizer_savings_percentage": { state:"8.2", attributes:{} },
    "sensor.heat_pump_optimizer_optimization_score": { state:"82", attributes:{envelope:90,machine:75} },
    "sensor.heat_pump_optimizer_plan_narrative": { state:"cheap_price", attributes:{
      lines:["Most heating is placed in the cheapest hours."], language:"en" } },
  });
  const scheduleStates = () => {
    const st = planStates();
    st[SPACE].attributes.day_start_hour = 7;
    st[SPACE].attributes.day_end_hour = 22;
    st[DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
    return st;
  };
  const sharedStepStates = () => {
    const st = planStates();
    const sp = st[SPACE].attributes.forecast;
    const heating = new Set(sp.filter((p)=>Number(p.space_power)>0.05).map((p)=>p.t));
    st[DHW].attributes.forecast = st[DHW].attributes.forecast.map(
      (p)=> heating.has(p.t) ? {...p, dhw_power:1.5} : p);
    return st;
  };
  const woodFuelStates = (fuel) => {
    const st = planStates();
    st[SPACE].attributes.wood_fuel = fuel;
    return st;
  };
  const awayPlanStates = ({sw=false, returnIso=null, resolved=false}={}) => {
    const st = planStates();
    st["switch.heat_pump_optimizer_away"] = { state: sw?"on":"off", attributes:{} };
    st["datetime.heat_pump_optimizer_away_return"] = { state: returnIso||"unknown", attributes:{} };
    st["binary_sensor.heat_pump_optimizer_away_mode"] = {
      state: resolved?"on":"off", attributes:{ source: (resolved && !sw) ? "person.alice" : "none" } };
    return st;
  };
  const setupStates = (topo, extra) => {
    const st = { ...planStates(), ...setupSensorStates(), ...(extra||{}) };
    st[SPACE].attributes.setup_topology = topo;
    return st;
  };
  const bigStates = () => {
    const st = {};
    for (let i=0;i<400;i++) {
      st["sensor.zz_probe_"+String(i).padStart(3,"0")] = { state:"20.0",
        attributes:{ unit_of_measurement:"\\u00b0C", friendly_name:"Probe "+String(i).padStart(3,"0") } };
    }
    st["sensor.vedpanna_temperatur_temperature"] = { state:"71.2",
      attributes:{ unit_of_measurement:"\\u00b0C", friendly_name:"Vedpanna temperatur" } };
    st["sensor.vedpanna_temperatur_temperature_2"] = { state:"48.9",
      attributes:{ unit_of_measurement:"\\u00b0C", friendly_name:"Vedpanna temperatur" } };
    return st;
  };

  // --- mounting -----------------------------------------------------------
  // Lovelace's own order: setConfig and hass BEFORE the element is placed, so
  // the first paint has no width (the order tests/card_browser.mjs proved
  // matters). One fresh element per cell; no state carries into the next.
  let CARD = null;
  const mount = async (states, config, hassExtra, hostW, themeCss) => {
    document.head.querySelectorAll("style.hpo-d4").forEach((n)=>n.remove());
    document.body.innerHTML = "";
    const style = document.createElement("style");
    style.className = "hpo-d4";
    style.textContent =
      'body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif;' +
      'background:var(--primary-background-color,#fafafa)}' +
      'heatpump-optimizer-card{display:block;width:' + hostW + 'px;' + themeCss + '}';
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig(Object.assign({type:"custom:heatpump-optimizer-card"}, config||{}));
    card.hass = Object.assign({states: states}, hassExtra||{});
    document.body.appendChild(card);
    CARD = card;
    window.__card = card;
    await new Promise((r)=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    await new Promise((r)=>setTimeout(r, 60));
    return card;
  };
  const settle = async () => {
    await new Promise((r)=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    await new Promise((r)=>setTimeout(r, 60));
  };
  const q = (sel) => CARD.shadowRoot.querySelector(sel);
  const qa = (sel) => [...CARD.shadowRoot.querySelectorAll(sel)];
  const svgOf = () => q(".chartwrap svg");
  const clickEl = (el) => { if (el) el.dispatchEvent(new MouseEvent("click", {bubbles:true, composed:true})); };
  const openDialog = () => CARD._onCardClick({});
  const xOf = (geom, t) =>
    geom.plotL + ((t - geom.windowStart)/(geom.windowEnd - geom.windowStart))*geom.plotW;

  const STATES = {
    no_plan: async (o) => { await mount({}, null, null, o.host, o.theme); },
    no_plan_expanded: async (o) => { await mount({}, null, null, o.host, o.theme); CARD.dialog.open(); await settle(); },
    plan_inline: async (o) => { await mount(planStates(), null, null, o.host, o.theme); },
    plan_inline_sv: async (o) => { await mount(planStates(), null, {language:"sv-SE"}, o.host, o.theme); },
    plan_short_window: async (o) => { await mount(planStates(), {hours:6}, null, o.host, o.theme); },
    custom_title_currency: async (o) => {
      await mount(planStates(), {title:"V\\u00e4rme", currency:"EUR", hours:48}, null, o.host, o.theme); },
    hidden_series: async (o) => {
      await mount(planStates(), {series:{outdoor:false, solar:false}}, null, o.host, o.theme);
      clickEl(q(".chip[data-key='price']")); await settle(); },
    score_open: async (o) => {
      await mount(Object.assign({}, planStates(), statStates()), null, null, o.host, o.theme);
      clickEl(q('[data-stat="score"]')); await settle(); },
    expanded_plan: async (o) => { await mount(planStates(), null, null, o.host, o.theme); openDialog(); await settle(); },
    what_if_off: async (o) => { await mount(planStates(), {what_if:false}, null, o.host, o.theme); openDialog(); await settle(); },
    expanded_zoomed: async (o) => {
      await mount(planStates(), null, null, o.host, o.theme); openDialog(); await settle();
      CARD.view.zoom(0.25); await settle(); },
    draft_dirty_menu_open: async (o) => {
      await mount(planStates(), {what_if:true}, null, o.host, o.theme); openDialog(); await settle();
      const geom = CARD._geom; const runs = CARD.manual.draft().dhw; const lo = CARD.manual.bounds()[0];
      const i = runs.findIndex((r)=>r.end>lo && r.start>=lo); const svg = svgOf();
      if (i>=0 && svg && geom) {
        const before = Object.assign({}, runs[i]);
        const target = { dataset:{channel:"dhw", index:String(i)} };
        const ev = (t)=>({clientX:xOf(geom,t), clientY:0, target, stopPropagation(){}, preventDefault(){}});
        svg.dispatchEvent(Object.assign(new MouseEvent("pointerdown",{bubbles:true}), {}));
        CARD.lanes.onDown ? CARD.lanes.onDown(ev(before.start+60000)) : null;
        CARD.lanes.onMove ? CARD.lanes.onMove(ev(before.start+60000+HOUR)) : null;
        CARD.lanes.onUp ? CARD.lanes.onUp({}) : null;
        CARD.lanes.openMenu("space", geom.windowStart+2*HOUR, 120, 40, svg, false);
      }
      await settle(); },
    draft_mid_drag: async (o) => {
      await mount(planStates(), {what_if:true}, null, o.host, o.theme); openDialog(); await settle();
      const geom = CARD._geom; const runs = CARD.manual.draft().dhw; const lo = CARD.manual.bounds()[0];
      const i = runs.findIndex((r)=>r.end>lo && r.start>=lo);
      if (i>=0 && geom) {
        const target = { dataset:{channel:"dhw", index:String(i)} };
        const ev = (t)=>({clientX:xOf(geom,t), clientY:0, target, stopPropagation(){}, preventDefault(){}});
        CARD.lanes.onDown(ev(runs[i].start+60000));
        CARD.lanes.onMove(ev(runs[i].start+60000+HOUR));
      }
      await settle(); },
    whatif_edited: async (o) => {
      await mount(scheduleStates(), {what_if:true}, null, o.host, o.theme);
      CARD._hass = { states: CARD._hass.states, callService: async ()=>({response:{results:{}}}) };
      openDialog(); await settle();
      CARD.whatIf.onInput({ stopPropagation(){}, preventDefault(){},
        target:{ value:"42", classList:{contains:(x)=>x==="wi-dhw-min"} } });
      clearTimeout(CARD.whatIf.timer); CARD.whatIf.timer = null;
      CARD.whatIf.onAddWindow({ stopPropagation(){}, preventDefault(){} });
      await settle(); },
    whatif_weekly: async (o) => {
      const st = planStates();
      st[DHW].attributes.dhw_windows = "06:00-08:30";
      st[DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
      await mount(st, {what_if:true}, null, o.host, o.theme); openDialog(); await settle(); },
    override_active: async (o) => {
      const st = planStates();
      const info = { active:true, expires_at:new Date(Date.now()+5*HOUR).toISOString(),
        space_slots:[], dhw_slots:[], released_space:[], released_dhw:[] };
      st[SPACE].attributes.manual_override = info;
      st[DHW].attributes.manual_override = info;
      await mount(st, {what_if:true}, null, o.host, o.theme); CARD.dialog.open(); await settle(); },
    shared_steps: async (o) => { await mount(sharedStepStates(), null, null, o.host, o.theme); openDialog(); await settle(); },
    shared_steps_hover: async (o) => {
      await mount(sharedStepStates(), null, null, o.host, o.theme); openDialog(); await settle();
      const svg = svgOf(); const plot = CARD._plot;
      const sp = sharedStepStates()[SPACE].attributes.forecast;
      const first = sp.find((p)=>Number(p.space_power)>0.05 && Date.parse(p.t)>=plot.windowStart);
      const t = first ? Date.parse(first.t) : plot.windowStart + 5*HOUR;
      CARD._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(t) }); await settle(); },
    tooltip_hover: async (o) => {
      await mount(planStates(), null, null, o.host, o.theme); openDialog(); await settle();
      const svg = svgOf(); const plot = CARD._plot;
      CARD._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(plot.windowStart + 5*HOUR) });
      await settle(); },
    coarse_pointer: async (o) => { await mount(planStates(), null, null, o.host, o.theme); openDialog(); await settle(); },
    reduced_motion: async (o) => { await mount(planStates(), null, null, o.host, o.theme); },
    setup_single_buffer: async (o) => {
      await mount(setupStates(qaTopologies().base), null, null, o.host, o.theme);
      openDialog(); CARD.dialog.page = "setup"; CARD._render(); await settle(); },
    setup_two_tank: async (o) => {
      await mount(setupStates(qaTopologies().twoTank), null, null, o.host, o.theme);
      openDialog(); CARD.dialog.page = "setup"; CARD._render(); await settle(); },
    setup_coil: async (o) => {
      await mount(setupStates(qaTopologies().coil), null, null, o.host, o.theme);
      openDialog(); CARD.dialog.page = "setup"; CARD._render(); await settle(); },
    layout_editing_dragged: async (o) => {
      await mount(setupStates(layoutCatalogTopo()), null, null, o.host, o.theme);
      openDialog(); CARD.dialog.page = "setup"; CARD._render(); await settle();
      clickEl(q(".layout-edit-toggle")); await settle();
      const L = CARD.layoutEditor; const box = (L.boxes||[]).find((b)=>b.place==="buffer_tank");
      if (box) {
        const svg = q("svg.setup-svg"); const r = svg.getBoundingClientRect();
        const vb = (svg.getAttribute("viewBox")||"0 0 720 420").split(/\\s+/);
        const k = r.width / (Number(vb[2])||720);
        const pt = (x,y)=>({clientX:r.left+x*k, clientY:r.top+y*k, target:{dataset:{}},
          stopPropagation(){}, preventDefault(){}});
        const fx = box.x+box.w/2, fy = box.y+box.h/2;
        L.onDown(pt(fx,fy)); L.onMove(pt(fx+20,fy+15)); L.onUp(pt(fx+40,fy+30));
      }
      await settle(); },
    layout_editing_tidy: async (o) => {
      await STATES.layout_editing_dragged(o);
      clickEl(q(".layout-tidy")); await settle(); },
    picker_open_filtered: async (o) => {
      await mount(setupStates(qaTopologies().base, bigStates()), null, null, o.host, o.theme);
      openDialog(); CARD.dialog.page = "setup"; CARD._render(); await settle();
      const hit = qa(".setup-hit").find((h)=>h.dataset.key==="wood_tank_top_entity");
      if (hit) hit.dispatchEvent(new MouseEvent("click",{bubbles:true,composed:true}));
      await settle();
      const box = q(".sp-filter");
      if (box) { box.value = "vedpanna"; box.dispatchEvent(new Event("input",{bubbles:true})); }
      await settle(); },
    wood_alert: async (o) => {
      await mount(woodFuelStates({cheaper:true, show_whatif:true, ready:true, slots:[]}),
        null, null, o.host, o.theme); },
    wood_lane: async (o) => {
      const t0 = PLAN.space_plan.forecast[0].t;
      const t1 = PLAN.space_plan.forecast[Math.min(4, PLAN.space_plan.forecast.length-1)].t;
      await mount(woodFuelStates({cheaper:false, show_whatif:true, ready:true,
        slots:[{start:t0, end:t1, source:"detected"}]}), null, null, o.host, o.theme); },
    wood_whatif: async (o) => {
      await mount(woodFuelStates({cheaper:false, show_whatif:true, ready:true, slots:[]}),
        {what_if:true}, null, o.host, o.theme); openDialog(); await settle(); },
    away_toggle: async (o) => { await mount(awayPlanStates(), null, null, o.host, o.theme); openDialog(); await settle(); },
    away_return: async (o) => { await mount(awayPlanStates({sw:true}), null, null, o.host, o.theme); openDialog(); await settle(); },
    away_status: async (o) => { await mount(awayPlanStates({resolved:true}), null, null, o.host, o.theme); openDialog(); await settle(); },
  };

  // --- measurement --------------------------------------------------------
  const hex = (h) => { const n = parseInt(h.slice(1),16); return [(n>>16)&255,(n>>8)&255,n&255]; };
  const parseCol = (s) => {
    if (!s || s === "transparent" || s === "none") return null;
    let m = s.match(/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?/);
    if (m) { const a = m[4]===undefined?1:Number(m[4]); return a===0?null:[+m[1],+m[2],+m[3],a]; }
    if (s.startsWith("#")) { const c = hex(s.length===4?"#"+s[1]+s[1]+s[2]+s[2]+s[3]+s[3]:s); return [c[0],c[1],c[2],1]; }
    return null;
  };
  const lum = (c) => { const f=(v)=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);};
    return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]); };
  const ratio = (a,b) => { const la=lum(a), lb=lum(b); return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05); };
  const over = (fg,bg,a) => [0,1,2].map((i)=>Math.round(a*fg[i]+(1-a)*bg[i]));
  const bgOf = (el) => {
    for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode().host) || null) {
      if (n.nodeType !== 1) break;
      const c = parseCol(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0.5) return [c[0],c[1],c[2]];
    }
    const host = window.__card;
    const tok = parseCol(getComputedStyle(host).getPropertyValue("--card-background-color").trim());
    return tok ? [tok[0],tok[1],tok[2]] : [255,255,255];
  };
  const visible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || Number(cs.opacity) === 0) return false;
    return el.getClientRects().length > 0;
  };
  const walkAll = (root, out) => {
    for (const el of root.querySelectorAll("*")) {
      out.push(el);
      if (el.shadowRoot) walkAll(el.shadowRoot, out);
    }
    return out;
  };
  const ownText = (el) => {
    let s = "";
    for (const n of el.childNodes) if (n.nodeType === 3) s += n.nodeValue;
    return s.trim();
  };
  const path = (el) => {
    const bits = [];
    for (let n = el; n && n.nodeType === 1 && bits.length < 4; n = n.parentElement) {
      bits.unshift(n.tagName.toLowerCase() +
        (n.getAttribute && n.getAttribute("class") ? "." + String(n.getAttribute("class")).trim().split(/\\s+/).join(".") : ""));
    }
    return bits.join(">");
  };

  const measure = () => {
    const card = window.__card;
    const root = card.shadowRoot;
    if (!root) return { error: "no shadow root" };
    const boxEl = root.querySelector("ha-card") || card;
    const cb = boxEl.getBoundingClientRect();
    // <defs> content is never painted; a <pattern>'s tiles routinely sit
    // outside the element that references them, which is not overflow.
    const inDefs = (el) => !!(el.closest && el.closest("defs"));
    const els = walkAll(root, []).filter((el) => !inDefs(el));

    // 1. HTML text clipped by its own box.
    const clipped = [];
    for (const el of els) {
      if (el.namespaceURI && el.namespaceURI.indexOf("svg") >= 0) continue;
      if (!visible(el)) continue;
      const t = ownText(el);
      if (!t) continue;
      const cs = getComputedStyle(el);
      const hidesX = cs.overflowX === "hidden" || cs.overflowX === "clip";
      const hidesY = cs.overflowY === "hidden" || cs.overflowY === "clip";
      const dx = el.scrollWidth - el.clientWidth;
      const dy = el.scrollHeight - el.clientHeight;
      if ((hidesX && dx > 1) || (hidesY && dy > 1)) {
        clipped.push({ sel: path(el), text: t.slice(0, 40), dx, dy,
          ellipsis: cs.textOverflow === "ellipsis" });
      }
    }

    // 2. SVG <text> ink boxes overlapping another <text> ink box.
    const texts = els.filter((el) => el.tagName === "text" && (el.textContent||"").trim() && visible(el));
    const boxes = texts.map((el) => {
      const b = el.getBoundingClientRect();
      return { el, x1:b.left, x2:b.right, y1:b.top, y2:b.bottom,
               t:(el.textContent||"").trim().slice(0,24), cls: el.getAttribute("class")||"" };
    }).filter((b) => b.x2 > b.x1 && b.y2 > b.y1);
    const overlaps = [];
    for (let i=0;i<boxes.length;i++) for (let j=i+1;j<boxes.length;j++) {
      const a=boxes[i], b=boxes[j];
      if (a.el.parentElement === b.el.parentElement && a.el.parentElement &&
          a.el.parentElement.tagName === "text") continue;
      const ox = Math.min(a.x2,b.x2) - Math.max(a.x1,b.x1);
      const oy = Math.min(a.y2,b.y2) - Math.max(a.y1,b.y1);
      if (ox > 0.5 && oy > 0.5) overlaps.push({ a:a.t, b:b.t, ax:a.cls, bx:b.cls,
        ox:+ox.toFixed(2), oy:+oy.toFixed(2) });
    }

    // 3. Horizontal overflow, split by whether a user can reach it. The
    //    clipping ancestor is the first one whose overflow-x is hidden or
    //    clip; an auto/scroll ancestor first means the same pixels are
    //    reachable by scrolling, which is a layout choice and not a defect.
    let clip = 0, clipWho = "", scrollable = 0, scrollWho = "";
    const containerOf = (el) => {
      for (let n = el.parentElement; n; n = n.parentElement) {
        const ox = getComputedStyle(n).overflowX;
        if (ox === "hidden" || ox === "clip") return { n, kind: "clip" };
        if (ox === "auto" || ox === "scroll") return { n, kind: "scroll" };
      }
      return null;
    };
    for (const el of els) {
      if (!visible(el)) continue;
      const b = el.getBoundingClientRect();
      if (b.width === 0 && b.height === 0) continue;
      const c = containerOf(el);
      if (!c) continue;
      const nb = c.n.getBoundingClientRect();
      const out = Math.max(nb.left - b.left, b.right - nb.right, 0);
      if (out <= 1) continue;
      if (c.kind === "clip") { if (out > clip) { clip = out; clipWho = path(el) + " |in| " + path(c.n); } }
      else if (out > scrollable) { scrollable = out; scrollWho = path(el) + " |in| " + path(c.n); }
    }
    const spill = clip; const spillWho = clipWho;

    // 4. Focusable / clickable controls under 24 px on their smaller side.
    const tsel = ["button","[tabindex]","[role='button']","input","select","textarea",
      "a[href]",".chip",".dlg-tab"].join(",");
    const small = [];
    const targets = [];
    for (const el of els) {
      if (!el.matches || !el.matches(tsel)) continue;
      if (!visible(el) || el.disabled) continue;
      if (el.getAttribute("tabindex") === "-1") continue;
      const b = el.getBoundingClientRect();
      if (b.width === 0 || b.height === 0) continue;
      targets.push(1);
      const m = Math.min(b.width, b.height);
      if (m < 24 - 0.05) small.push({ sel: path(el), w:+b.width.toFixed(1), h:+b.height.toFixed(1) });
    }

    // 5. WCAG AA on every visible text run (HTML own-text and SVG <text>).
    const inactive = (el) => {
      for (let n = el; n; n = n.parentElement) {
        if (n.disabled === true) return true;
        if (n.getAttribute && n.getAttribute("aria-disabled") === "true") return true;
      }
      return false;
    };
    const lowContrast = [];
    for (const el of els) {
      if (!visible(el)) continue;
      // WCAG 1.4.3 exempts text in an INACTIVE user interface component.
      if (inactive(el)) continue;
      const isSvgText = el.tagName === "text";
      const t = isSvgText ? (el.textContent||"").trim() : ownText(el);
      if (!t) continue;
      const cs = getComputedStyle(el);
      const raw = isSvgText ? (cs.fill && cs.fill !== "none" ? cs.fill : el.getAttribute("fill")) : cs.color;
      const fgc = parseCol(raw);
      if (!fgc) continue;
      const op = Number(cs.opacity);
      const bg = bgOf(el);
      const fg = over([fgc[0],fgc[1],fgc[2]], bg, (Number.isFinite(op)?op:1) * fgc[3]);
      const r = ratio(fg, bg);
      const px = parseFloat(cs.fontSize) || 0;
      // SVG font-size is in user units; convert with the svg's own scale.
      let screenPx = px;
      if (isSvgText) {
        const svg = el.ownerSVGElement;
        if (svg) {
          const rr = svg.getBoundingClientRect();
          const vb = (svg.getAttribute("viewBox")||"").split(/\\s+/);
          const w = Number(vb[2]);
          if (w && rr.width) screenPx = px * (rr.width / w);
        }
      }
      const bold = Number(cs.fontWeight) >= 700;
      const floor = (screenPx >= 24 || (bold && screenPx >= 18.66)) ? 3 : 4.5;
      if (r < floor - 0.005) lowContrast.push({ sel: path(el), text: t.slice(0,28),
        ratio:+r.toFixed(2), floor, px:+screenPx.toFixed(2) });
    }

    return {
      cardW: +cb.width.toFixed(1), cardH: +cb.height.toFixed(1),
      clipped, overlaps, spill:+spill.toFixed(2), spillWho,
      scrollable:+scrollable.toFixed(2), scrollWho,
      docScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      smallTargets: small, nTargets: targets.length,
      lowContrast,
    };
  };

  return {
    setPlan: (p) => { PLAN = p; },
    names: () => Object.keys(STATES),
    run: async (name, opts) => { await STATES[name](opts); return measure(); },
  };
})();
`;

const HA_CARD_DEF = `
if (!customElements.get("ha-card")) {
  customElements.define("ha-card", class extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host{background:var(--ha-card-background,var(--card-background-color,#fff));" +
        "box-sizing:border-box;border-radius:12px;border-width:1px;" +
        "border-style:solid;border-color:var(--divider-color,#e0e0e0);" +
        "color:var(--primary-text-color);" +
        "display:block;position:relative;}</style><slot></slot>";
    }
  });
}
`;

const POINTERS = ["coarse", "fine"];

const browser = await chromium.launch();
const records = [];
let pageErrors = 0;
try {
 for (const pointer of POINTERS) {
  for (const vp of VIEWPORTS) {
    for (const [themeName, themeCss] of [["light", HA_LIGHT], ["dark", HA_DARK]]) {
      const page = await browser.newPage({ viewport: { width: vp.w, height: vp.h } });
      const errs = [];
      page.on("pageerror", (e) => { errs.push(String(e.message).slice(0, 160)); });
      page.on("console", (m) => {
        if (m.type() === "error") errs.push("console: " + m.text().slice(0, 160));
      });
      await page.goto("about:blank");
      if (pointer === "coarse") {
        // Headless Chromium reports pointer:fine. Playwright 1.49 has no
        // emulateMedia({pointer}); CDP is the equivalent, and the matchMedia
        // stub covers the card's own JS `_coarsePointer()` reads, which CDP
        // emulation does not re-evaluate inside a shadow root.
        const cdp = await page.context().newCDPSession(page);
        await cdp.send("Emulation.setEmulatedMedia", {
          features: [{ name: "pointer", value: "coarse" },
                     { name: "any-pointer", value: "coarse" },
                     { name: "hover", value: "none" }],
        });
        await page.evaluate(() => {
          const orig = window.matchMedia.bind(window);
          window.matchMedia = (q) => {
            if (q === "(pointer: coarse)" || q === "(hover: none)") {
              return { matches: true, media: q, onchange: null,
                addEventListener() {}, removeEventListener() {},
                addListener() {}, removeListener() {}, dispatchEvent() { return true; } };
            }
            return orig(q);
          };
        });
      }
      await page.addScriptTag({ path: CARD_SRC });
      await page.evaluate(HA_CARD_DEF);
      await page.evaluate(DRIVER);
      await page.evaluate((p) => window.__HPO.setPlan(p), plan);
      const names = await page.evaluate(() => window.__HPO.names());
      for (const name of names) {
        if (onlyState && name !== onlyState) continue;
        errs.length = 0;
        let m;
        try {
          m = await page.evaluate(
            ([n, o]) => window.__HPO.run(n, o),
            [name, { host: vp.host, theme: themeCss }]);
        } catch (e) {
          m = { error: String(e.message).slice(0, 200) };
        }
        m.state = name;
        m.viewport = vp.name;
        m.theme = themeName;
        m.pointer = pointer;
        m.hostW = vp.host;
        m.errors = [...new Set(errs)];
        pageErrors += m.errors.length;
        records.push(m);
        if (shotDir && ((m.clipped || []).length || (m.overlaps || []).length ||
            m.spill > 1 || (m.smallTargets || []).length || (m.lowContrast || []).length)) {
          try {
            await page.screenshot({
              path: path.join(shotDir, `${name}-${vp.name}-${themeName}-${pointer}.png`),
              fullPage: true,
            });
          } catch { /* a state that failed to render has nothing to shoot */ }
        }
      }
      await page.close();
    }
  }
 }
} finally {
  await browser.close();
}

const nStates = new Set(records.map((r) => r.state)).size;
const cells = records.length;
const cnt = (f) => records.filter(f).length;
console.log("");
console.log(`RESULT states_rendered=${nStates} count`);
console.log(`RESULT cells=${cells} count`);
console.log(`RESULT clipped_text_cells=${cnt((r) => (r.clipped || []).length > 0)} count`);
// NOT an ink metric: getBoundingClientRect on an SVG <text> returns the
// font's em box (ascent+descent), not the glyph outline, so an em-box
// overlap is a LEAD and must be confirmed by rasterising. At this baseline
// tools/audit/round3/D4/card_ux_defects.mjs section C rasterises the pairs
// this counter reports and finds ZERO real ink collisions.
console.log(`RESULT svg_text_embox_overlap_cells=${cnt((r) => (r.overlaps || []).length > 0)} count`);
console.log(`RESULT clipped_overflow_cells=${cnt((r) => (r.spill || 0) > 1)} count`);
console.log(`RESULT scrollable_overflow_cells=${cnt((r) => (r.scrollable || 0) > 1)} count`);
console.log(`RESULT small_target_cells_coarse=${cnt((r) => r.pointer === "coarse" && (r.smallTargets || []).length > 0)} count`);
console.log(`RESULT small_target_cells_fine=${cnt((r) => r.pointer === "fine" && (r.smallTargets || []).length > 0)} count`);
console.log(`RESULT low_contrast_cells=${cnt((r) => (r.lowContrast || []).length > 0)} count`);
console.log(`RESULT low_contrast_sites=${new Set(records.flatMap((r) => (r.lowContrast || []).map((x) => x.sel))).size} count`);
console.log(`RESULT doc_hscroll_cells=${cnt((r) => (r.docScroll || 0) > 0)} count`);
console.log(`RESULT page_error_cells=${cnt((r) => (r.errors || []).length > 0)} count`);
console.log(`RESULT render_failures=${cnt((r) => r.error)} count`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${(await import("node:os")).loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);

if (jsonOut) {
  writeFileSync(jsonOut, JSON.stringify(records, null, 1));
  console.log(`wrote ${records.length} cell records -> ${jsonOut}`);
}
