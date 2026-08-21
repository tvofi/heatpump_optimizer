import fs from "fs";
import vm from "vm";

const plan = JSON.parse(fs.readFileSync("/tmp/plandata.json","utf8"));

// Minimal DOM stub sufficient for the card's inline-SVG rendering.
class Node {
  constructor(tag){ this.tagName=(tag||"").toUpperCase(); this.children=[]; this.style={};
    this._html=""; this._listeners={}; this.dataset={}; this.classList={
      _s:new Set(), add(...c){c.forEach(x=>this._s.add(x));},
      remove(...c){c.forEach(x=>this._s.delete(x));},
      toggle(c,f){ f===undefined? (this._s.has(c)?this._s.delete(c):this._s.add(c)) : (f?this._s.add(c):this._s.delete(c)); },
      contains(c){return this._s.has(c);} };
  }
  set innerHTML(v){ this._html=String(v); }
  get innerHTML(){ return this._html; }
  appendChild(c){ this.children.push(c); return c; }
  removeChild(c){ this.children=this.children.filter(x=>x!==c); }
  setAttribute(k,v){ this[k]=v; }
  getAttribute(k){ return this[k]; }
  addEventListener(t,f){ (this._listeners[t] ||= []).push(f); }
  removeEventListener(){}
  querySelector(sel){ return this._find(sel); }
  querySelectorAll(sel){ const out=[]; this._findAll(sel,out); return out; }
  _find(sel){ const a=[]; this._findAll(sel,a); return a[0]||null; }
  _findAll(sel,out){
    for(const c of this.children){
      const cls = sel.startsWith(".") ? sel.slice(1) : null;
      if(cls ? c.classList.contains(cls) : c.tagName===sel.toUpperCase()) out.push(c);
      c._findAll(sel,out);
    }
  }
  attachShadow(){ this.shadowRoot=new Node("shadow-root"); return this.shadowRoot; }
  getBoundingClientRect(){ return {width:900,height:400,left:0,top:0}; }
}
class HTMLElement extends Node { constructor(){ super("div"); } }

const document = {
  createElement:(t)=>new Node(t),
  createElementNS:(ns,t)=>new Node(t),
  head:new Node("head"), body:new Node("body"),
};
const store={};
const ctx = {
  HTMLElement, document, console,
  window:{ customCards:[], localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
           addEventListener(){}, matchMedia:()=>({matches:false,addEventListener(){}}) },
  localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
  customElements:{ _d:{}, define(n,c){ this._d[n]=c; }, get(n){ return this._d[n]; } },
  ResizeObserver: class { observe(){} unobserve(){} disconnect(){} },
  requestAnimationFrame:(f)=>f(),
  setTimeout, clearTimeout,
};
ctx.globalThis = ctx; ctx.self = ctx; ctx.window.document = document;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8"), ctx);

const names = Object.keys(ctx.customElements._d);
console.log("defined elements:", names.join(", "));
console.log("customCards:", JSON.stringify(ctx.window.customCards));

const Card = ctx.customElements.get("heatpump-optimizer-card");
if (!Card) { console.error("FAIL: card not registered"); process.exit(1); }

const mkStates = (spaceId, dhwId, withMarker) => ({
  [spaceId]: { state:"3 slots planned", attributes:{
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now, friendly_name:"Space Heating Plan",
    ...(withMarker ? { plan_kind: "space" } : {}) } },
  [dhwId]: { state:"4 slots planned", attributes:{
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now, friendly_name:"DHW Heating Plan",
    ...(withMarker ? { plan_kind: "dhw" } : {}) } },
});

// The plan sensors use has_entity_name, so a default install prefixes the
// device name. These are the ids a real Home Assistant actually creates.
const DEFAULT_SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
const DEFAULT_DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";

function collect(n, out=[]) { if(n._html) out.push(n._html); n.children.forEach(c=>collect(c,out)); return out; }

function build(states, config) {
  const card = new Card();
  card.setConfig({ type:"custom:heatpump-optimizer-card", ...(config||{}) });
  card.hass = { states };
  if (card.connectedCallback) card.connectedCallback();
  card.hass = { states };
  return card;
}

let fails = 0;
function check(name, cond) { console.log((cond?"  ok  ":"  FAIL") + "  " + name); if(!cond) fails++; }

// --- Scenario 1: stock install, real (device-prefixed) entity ids ----------
const card = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
const dump = collect(card.shadowRoot).join("\n");

check("renders an <svg>", /<svg/.test(dump));
check("draws polyline/path data", /(<polyline|<path)/.test(dump));
check("draws heating bars", /<rect/.test(dump));
check("legend has all six series", ["Electricity price","DHW heating","Space heating","Outdoor temperature","DHW tank temperature","House temperature"].every(l=>dump.includes(l)));
check("shows a cost or energy summary", /kWh|SEK/.test(dump));
check("default entity ids match a real install", !/No plan data available yet/.test(dump));

// Toggling a series off must change the rendered output.
const before = dump;
card._onLegendClick({ currentTarget: { getAttribute: (k) => (k === "data-key" ? "dhw_temp" : null) } });
const after = collect(card.shadowRoot).join("\n");
check("toggling a series changes the chart", after !== before);
check("toggle persisted to localStorage", Object.keys(store).length > 0);

// --- Scenario 2: user renamed the entities; discovery via plan_kind --------
const renamed = build(mkStates("sensor.my_heat_plan", "sensor.my_water_plan", true));
const renamedDump = collect(renamed.shadowRoot).join("\n");
check("discovers renamed entities by plan_kind", !/No plan data available yet/.test(renamedDump) && /<svg/.test(renamedDump));

// --- Scenario 3: older integration without plan_kind; suffix fallback ------
const legacy = build(mkStates("sensor.space_heating_plan", "sensor.dhw_heating_plan", false));
const legacyDump = collect(legacy.shadowRoot).join("\n");
check("falls back to name-suffix discovery", !/No plan data available yet/.test(legacyDump) && /<svg/.test(legacyDump));

// --- Scenario 4: nothing published; message must be actionable -------------
const empty = build({});
const emptyDump = collect(empty.shadowRoot).join("\n");
check("reports missing entities clearly", /no entity found/.test(emptyDump) && /Developer Tools/.test(emptyDump));

// --- Scenario 5: explicit config overrides discovery -----------------------
const explicit = build(
  { ...mkStates("sensor.a_plan", "sensor.b_plan", true), ...mkStates(DEFAULT_SPACE, DEFAULT_DHW, true) },
  { space_entity: "sensor.a_plan", dhw_entity: "sensor.b_plan" }
);
check("explicit config is honoured", explicit._resolveEntity("space") === "sensor.a_plan");

// --- Scenario 6: click to expand ------------------------------------------
const exp = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
const collapsed = collect(exp.shadowRoot).join("\n");
check("collapsed card offers an expand affordance",
  /class="expand"/.test(collapsed) && /ha-card class="clickable"/.test(collapsed));
check("no dialog is rendered until asked for", !/<dialog/.test(collapsed));

exp._onCardClick({});
const opened = collect(exp.shadowRoot).join("\n");
check("clicking the card opens a dialog", exp._expanded && /<dialog/.test(opened));
check("the dialog uses showModal-capable markup", /dialog class="expanded"/.test(opened));
check("the dialog carries its own chart", (opened.match(/<svg/g) || []).length >
  (collapsed.match(/<svg/g) || []).length);
// data-key also appears on series paths, so count the legend containers.
check("the dialog carries its own legend and close button",
  /class="close"/.test(opened) && (opened.match(/class="legend"/g) || []).length === 2);

// The enlarged chart has room for an hourly time axis rather than every third
// hour, so it must not be a pixel-identical copy of the inline one.
const svgs = opened.split("<svg").slice(1);
const labelCount = (s) => (s.match(/text-anchor="middle"/g) || []).length;
check("the enlarged chart labels more of the time axis",
  labelCount(svgs[svgs.length - 1]) > labelCount(svgs[0]));

// --- Scenario 7: toggles must not open the popup ---------------------------
const tog = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
let stopped = false;
tog._onLegendClick({
  stopPropagation: () => { stopped = true; },
  currentTarget: { getAttribute: (k) => (k === "data-key" ? "price" : null) },
});
check("a legend click stops propagating to the card", stopped);
check("a legend click does not expand the card", tog._expanded === false);

// Toggling while expanded must keep the popup open, not dismiss it.
tog._onCardClick({});
tog._onLegendClick({
  stopPropagation: () => {},
  currentTarget: { getAttribute: (k) => (k === "data-key" ? "price" : null) },
});
check("toggling inside the popup keeps it open",
  tog._expanded && /<dialog/.test(collect(tog.shadowRoot).join("\n")));

tog._closeExpanded();
check("closing removes the dialog",
  !tog._expanded && !/<dialog/.test(collect(tog.shadowRoot).join("\n")));

// --- Scenario 8: nothing to show, nothing to expand ------------------------
const emptyExp = build({});
const emptyExpDump = collect(emptyExp.shadowRoot).join("\n");
// "clickable" also occurs in the stylesheet, so check the element's attribute.
check("the empty state is not clickable",
  !/class="expand"/.test(emptyExpDump) && !/<ha-card class="clickable"/.test(emptyExpDump));

console.log(fails ? `\n${fails} CARD CHECK(S) FAILED` : "\nALL CARD CHECKS PASSED");
process.exit(fails?1:0);
