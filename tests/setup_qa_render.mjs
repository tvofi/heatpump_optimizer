// Visual-QA renderer: builds the card with the same DOM stub as card.mjs,
// renders the setup page for three topologies, and saves each page's
// setup <svg> as a self-contained .svg file (card CSS inlined, HA vars
// resolved to their light-mode fallbacks) for designer review.
import fs from "fs";
import vm from "vm";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";

// Same plan-payload resolution as tests/card.mjs: argv, HPO_PLANDATA, then a
// default derived from this checkout's tests/ directory (what plan_view.py
// writes), so the render never silently uses another checkout's stale file.
const _testsDir = path.dirname(fileURLToPath(import.meta.url));
const _defaultPlan = path.join(
  "/tmp",
  `plandata-${crypto.createHash("sha256").update(_testsDir).digest("hex").slice(0, 12)}.json`
);
const _planPath = process.argv[2] || process.env.HPO_PLANDATA || _defaultPlan;
const plan = JSON.parse(fs.readFileSync(_planPath, "utf8"));

// --- DOM stub, verbatim from tests/card.mjs ---------------------------------
const VOID_TAGS = new Set(["br","hr","img","input","meta","link","source","path","rect","line","circle","use"]);

function parseHtml(html, mk) {
  const root = [];
  const stack = [];
  const push = (node) => {
    if (stack.length) stack[stack.length - 1].appendChild(node);
    else root.push(node);
  };
  const re = /<\/?([a-zA-Z][\w-]*)((?:\s+[^>]*?)?)(\/?)>|([^<]+)/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const [, tag, attrsRaw, selfClose, text] = m;
    if (text !== undefined) {
      const trimmed = text.replace(/\s+/g, " ");
      if (trimmed.trim() && stack.length) stack[stack.length - 1]._text += trimmed;
      continue;
    }
    if (m[0][1] === "/") {
      for (let i = stack.length - 1; i >= 0; i--) {
        if (stack[i].tagName === tag.toUpperCase()) { stack.length = i; break; }
      }
      continue;
    }
    const node = mk(tag);
    for (const a of attrsRaw.matchAll(/([\w:-]+)\s*=\s*"([^"]*)"/g)) {
      const [, name, value] = a;
      if (name === "class") value.split(/\s+/).filter(Boolean).forEach((c) => node.classList.add(c));
      else if (name.startsWith("data-")) node.dataset[name.slice(5).replace(/-(\w)/g, (x, c) => c.toUpperCase())] = value;
      node.setAttribute(name, value);
    }
    push(node);
    if (!selfClose && !VOID_TAGS.has(tag.toLowerCase())) stack.push(node);
  }
  return root;
}

class Node {
  constructor(tag){ this.tagName=(tag||"").toUpperCase(); this.children=[]; this.style={};
    this._html=""; this._text=""; this._listeners={}; this.dataset={}; this.classList={
      _s:new Set(), add(...c){c.forEach(x=>this._s.add(x));},
      remove(...c){c.forEach(x=>this._s.delete(x));},
      toggle(c,f){ f===undefined? (this._s.has(c)?this._s.delete(c):this._s.add(c)) : (f?this._s.add(c):this._s.delete(c)); },
      contains(c){return this._s.has(c);} };
  }
  set innerHTML(v){
    this._html=String(v);
    this.children = [];
    for (const child of parseHtml(this._html, (t) => new Node(t))) this.appendChild(child);
  }
  get innerHTML(){ return this._html; }
  set textContent(v){ this._text = String(v); }
  get textContent(){ return this._text + this.children.map((c) => c.textContent).join(""); }
  set className(v){ this.classList._s = new Set(String(v).split(/\s+/).filter(Boolean)); }
  get className(){ return [...this.classList._s].join(" "); }
  appendChild(c){ this.children.push(c); c.parentNode = this; return c; }
  removeChild(c){ this.children=this.children.filter(x=>x!==c); if (c) c.parentNode = null; }
  setAttribute(k,v){ this[k]=v; }
  getAttribute(k){ return this[k]; }
  addEventListener(t,f){ (this._listeners[t] ||= []).push(f); }
  removeEventListener(){}
  dispatchEvent(ev){ ev.target = ev.target || this;
    (this._listeners[ev.type]||[]).slice().forEach((f)=>f(ev)); return true; }
  querySelector(sel){ return this._find(sel); }
  querySelectorAll(sel){ const out=[]; this._findAll(sel,out); return out; }
  _find(sel){ const a=[]; this._findAll(sel,a); return a[0]||null; }
  _findAll(sel,out){
    const sp = sel.indexOf(" ");
    if (sp > 0) {
      const head = sel.slice(0, sp).trim();
      const rest = sel.slice(sp + 1).trim();
      const hosts = [];
      this._findAll(head, hosts);
      for (const h of hosts) h._findAll(rest, out);
      return;
    }
    for(const c of this.children){
      if (matches(c, sel)) out.push(c);
      c._findAll(sel,out);
    }
  }
  attachShadow(){ this.shadowRoot=new Node("shadow-root"); return this.shadowRoot; }
  getBoundingClientRect(){ return {width:900,height:400,left:0,top:0}; }
  focus(){ document.activeElement = this; }
}
function matches(node, sel) {
  const attr = sel.match(/^([\w-]*)\[([\w-]+)(?:="([^"]*)")?\]$/);
  if (attr) {
    const [, tag, name, value] = attr;
    if (tag && node.tagName !== tag.toUpperCase()) return false;
    const actual = node.getAttribute(name);
    if (actual === undefined || actual === null) return false;
    return value === undefined || String(actual) === value;
  }
  if (sel.startsWith(".")) return node.classList.contains(sel.slice(1));
  return node.tagName === sel.toUpperCase();
}

class HTMLElement extends Node { constructor(){ super("div"); } }

const docListeners = {};
const document = {
  createElement:(t)=>new Node(t),
  createElementNS:(ns,t)=>new Node(t),
  head:new Node("head"), body:new Node("body"),
  activeElement:null,
  addEventListener(t,f){ (docListeners[t]=docListeners[t]||[]).push(f); },
  removeEventListener(t,f){ const a=docListeners[t]||[]; const i=a.indexOf(f); if(i>=0)a.splice(i,1); },
};
document.activeElement = document.body;
const store={};
const winListeners = {};
const intervals = new Map(); let intervalId = 0;
const ctx = {
  HTMLElement, document, console,
  window:{ customCards:[], localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
           addEventListener(t,f){ (winListeners[t]=winListeners[t]||[]).push(f); },
           removeEventListener(t,f){ const a=winListeners[t]||[]; const i=a.indexOf(f); if(i>=0)a.splice(i,1); },
           matchMedia:(q)=>({matches:false, addEventListener(){}}) },
  localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
  customElements:{ _d:{}, define(n,c){ this._d[n]=c; }, get(n){ return this._d[n]; } },
  ResizeObserver: class { observe(){} unobserve(){} disconnect(){} },
  requestAnimationFrame:(f)=>f(),
  setTimeout, clearTimeout,
  setInterval:(f)=>{ intervals.set(++intervalId, f); return intervalId; },
  clearInterval:(id)=>{ intervals.delete(id); },
};
ctx.CustomEvent = class {
  constructor(type, opts = {}) {
    this.type = type; this.detail = opts.detail;
    this.bubbles = !!opts.bubbles; this.composed = !!opts.composed;
  }
};
ctx.globalThis = ctx; ctx.self = ctx; ctx.window.document = document;
vm.createContext(ctx);
const cardSrc = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8");
vm.runInContext(cardSrc, ctx);
const Card = ctx.customElements.get("heatpump-optimizer-card");

const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const DEFAULT_SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
const DEFAULT_DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";
const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));
const mkStates = () => ({
  [SOLAR_ID]: { state:"120", attributes:{
    forecast: solarForecast, source:"open_meteo", friendly_name:"Solar Irradiance", plan_kind:"solar" } },
  [DEFAULT_SPACE]: { state:"3 slots planned", attributes:{
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now, friendly_name:"Space Heating Plan", plan_kind:"space" } },
  [DEFAULT_DHW]: { state:"4 slots planned", attributes:{
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now, friendly_name:"DHW Heating Plan", plan_kind:"dhw" } },
});
function collect(n, out=[]) { if(n._html) out.push(n._html); n.children.forEach(c=>collect(c,out)); return out; }

// --- The three topologies ---------------------------------------------------
const TEMP = ["sensor", "number", "input_number"];
const base = {
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
      place: "upper_zone", entity: "sensor.livingroom", domains: TEMP },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature",
      place: "lower_zone", entity: null, domains: TEMP },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
      place: "buffer_tank", entity: "sensor.tank", domains: TEMP },
    { key: "wood_tank_top_entity", label: "Wood tank top",
      place: "wood_tank", entity: null, domains: TEMP },
    { key: "outdoor_temp_entity", label: "Outdoor temperature",
      place: "outdoor", entity: "sensor.outside", domains: TEMP },
    { key: "heat_pump_switch_entity", label: "Heat pump switch",
      place: "heat_pump", entity: null,
      domains: ["switch", "input_boolean", "climate"] },
  ],
};
const twoTank = JSON.parse(JSON.stringify(base));
twoTank.two_tank_modelled = true;
twoTank.layout = "two_tank_4way";
twoTank.edges = [
  ["heat_pump", "buffer_tank"],
  ["buffer_tank", "mixing_valve"],
  ["wood_tank", "mixing_valve"],
  ["mixing_valve", "upper_zone"],
  ["mixing_valve", "lower_zone"],
  ["heat_pump", "dhw_tank"],
];
twoTank.slots = base.slots.concat([
  { key: "mixing_valve_target_entity", label: "Valve target",
    place: "mixing_valve", entity: null, domains: TEMP },
  { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
    place: "mixing_valve", entity: null, domains: TEMP },
]);
const coil = JSON.parse(JSON.stringify(twoTank));
coil.dhw_wood_coil = true;
coil.edges = twoTank.edges.concat([["wood_tank", "dhw_tank"]]);
coil.slots.push({ key: "dhw_temp_entity", label: "Hot water temperature",
  place: "dhw_tank", entity: null, domains: TEMP });

// --- Extract the setup CSS from the card source and resolve HA vars ---------
const styleBlock = (cardSrc.match(/\.setup-page[\s\S]*?\.setup-pipe\.invalid \{[\s\S]*?\}/) || [""])[0];
const layoutCss = styleBlock
  .replace(/var\(--primary-text-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--secondary-text-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--primary-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--error-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--card-background-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--divider-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--primary-text-color\)/g, "#212121")
  .replace(/var\(--secondary-text-color\)/g, "#757575");

const outDir = path.resolve(process.cwd(), "../setup-qa");
fs.mkdirSync(outDir, { recursive: true });

function renderTopo(name, topo) {
  const states = mkStates();
  states[DEFAULT_SPACE].attributes.setup_topology = topo;
  states["sensor.livingroom"] = { state: "21.3", attributes: { unit_of_measurement: "°C" } };
  states["sensor.tank"] = { state: "47.5", attributes: { unit_of_measurement: "°C" } };
  states["sensor.outside"] = { state: "unavailable", attributes: {} };
  const card = new Card();
  card.setConfig({ type: "custom:heatpump-optimizer-card" });
  card.hass = { states };
  if (card.connectedCallback) card.connectedCallback();
  card.hass = { states };
  card._onCardClick({});
  card._dialogPage = "setup";
  card._render();
  const page = collect(card.shadowRoot).join("\n");
  const svg = (page.match(/<svg class="setup-svg[\s\S]*?<\/svg>/) || [""])[0];
  if (!svg) { console.error(`FAIL: no setup svg for ${name}`); process.exit(1); }
  // Self-contained file: white ground + inlined card CSS with vars
  // resolved, spliced in right after the opening <svg ...> tag.
  const openEnd = svg.indexOf(">");
  const inject =
    `<style>svg { background: #fff; font-family: sans-serif; }\n${layoutCss}</style>` +
    `<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />`;
  const withStyle = openEnd < 0 ? svg : svg.slice(0, openEnd + 1) + inject + svg.slice(openEnd + 1);
  const file = path.join(outDir, `${name}.svg`);
  fs.writeFileSync(file, withStyle);
  console.log(`${name}: ${file}`);
  console.log(`  boxes: ${JSON.stringify(card._layoutBoxes)}`);
  return { svg, boxes: card._layoutBoxes };
}

renderTopo("coil", coil);
renderTopo("two-tank", twoTank);
renderTopo("single-buffer", base);
console.log("QA RENDERS WRITTEN");
