import fs from "fs";
import vm from "vm";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";

// Plan payload written by tests/plan_view.py earlier in the run. The path is
// argv[2], or HPO_PLANDATA, or a default derived from this checkout's tests/
// directory — the same derivation plan_view.py uses — so this test cannot
// quietly pass against a stale file another checkout left in /tmp. The old
// fixed /tmp/plandata.json is only accepted as a last resort, loudly.
const testsDir = path.dirname(fileURLToPath(import.meta.url));
const defaultPath = path.join(
  "/tmp",
  `plandata-${crypto.createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`
);
let planPath = process.argv[2] || process.env.HPO_PLANDATA || defaultPath;
if (!fs.existsSync(planPath)) {
  const legacy = "/tmp/plandata.json";
  if (planPath === defaultPath && fs.existsSync(legacy)) {
    console.warn(
      `WARNING: ${planPath} not found (run tests/plan_view.py first); ` +
      `falling back to ${legacy}, which may be stale or from another checkout`
    );
    planPath = legacy;
  } else {
    console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py first`);
    process.exit(1);
  }
}
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));

// Minimal DOM stub sufficient for the card's inline-SVG rendering.
//
// `innerHTML` is parsed rather than merely stored. The card queries its own
// output for controls it then wires up — the legend chips, the expand button,
// the what-if slider — so a stub that keeps the markup as an opaque string
// silently skips every one of those paths and reports a pass. The parser only
// needs tag names, classes, other attributes and text, which is all the card
// selects on.
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
      if (trimmed.trim() && stack.length) {
        stack[stack.length - 1]._text += trimmed;
      }
      continue;
    }
    if (m[0][1] === "/") {
      // Closing tag. Tolerate mismatches rather than throwing: the point is to
      // find elements, not to validate markup.
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
  get textContent(){
    return this._text + this.children.map((c) => c.textContent).join("");
  }
  set className(v){
    this.classList._s = new Set(String(v).split(/\s+/).filter(Boolean));
  }
  get className(){ return [...this.classList._s].join(" "); }
  appendChild(c){ this.children.push(c); c.parentNode = this; return c; }
  removeChild(c){
    this.children=this.children.filter(x=>x!==c);
    if (c) c.parentNode = null;
  }
  setAttribute(k,v){ this[k]=v; }
  getAttribute(k){ return this[k]; }
  addEventListener(t,f){ (this._listeners[t] ||= []).push(f); }
  removeEventListener(){}
  // No bubbling: the card and its editor only ever listen on the element the
  // event is dispatched on, so a local delivery is faithful enough.
  dispatchEvent(ev){ ev.target = ev.target || this;
    (this._listeners[ev.type]||[]).slice().forEach((f)=>f(ev)); return true; }
  querySelector(sel){ return this._find(sel); }
  querySelectorAll(sel){ const out=[]; this._findAll(sel,out); return out; }
  _find(sel){ const a=[]; this._findAll(sel,a); return a[0]||null; }
  _findAll(sel,out){
    // Descendant selectors: the card scopes its chart lookups with
    // ".chartwrap svg", because the header's expand icon is an <svg> too.
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
  // Focus is tracked, not simulated: the card restores focus after
  // render-destroying keyboard actions, and the assertion is simply "who
  // received the last .focus() call".
  focus(){ document.activeElement = this; }
  // ...and gives it up again. The card takes focus off a setup row that a
  // pointer gesture left holding it (item F), which is only observable if
  // the stub models letting go as well as taking hold.
  blur(){ if (document.activeElement === this) document.activeElement = document.body; }
}
// Selector support: a tag name, a class, an attribute, or a tag+attribute
// pair, which covers everything the card actually queries for.
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

const document = {
  createElement:(t)=>new Node(t),
  createElementNS:(ns,t)=>new Node(t),
  head:new Node("head"), body:new Node("body"),
  activeElement:null,
  // Real registries, same pattern as window's below: the slot menu parks an
  // Escape listener on the document while it is open, so a mouse-opened menu
  // (focus still on the chart) can be dismissed from the keyboard.
  addEventListener(t,f){ (docListeners[t]=docListeners[t]||[]).push(f); },
  removeEventListener(t,f){ const a=docListeners[t]||[]; const i=a.indexOf(f); if(i>=0)a.splice(i,1); },
};
document.activeElement = document.body;
const store={};
const ctx = {
  HTMLElement, document, console,
  window:{ customCards:[], localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
           // Real registries: the drag and pan gestures park their move/up
           // handlers on window so they survive mid-gesture re-renders, and a
           // no-op here would make those paths untestable.
           addEventListener(t,f){ (winListeners[t]=winListeners[t]||[]).push(f); },
           removeEventListener(t,f){ const a=winListeners[t]||[]; const i=a.indexOf(f); if(i>=0)a.splice(i,1); },
           matchMedia:(q)=>({matches:
             (q === "(pointer: coarse)" && coarseTouch.on) ||
             (q === "(prefers-reduced-motion: reduce)" && reducedMotion.on),
             addEventListener(){}}) },
  localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
  customElements:{ _d:{}, define(n,c){ this._d[n]=c; }, get(n){ return this._d[n]; } },
  ResizeObserver: class { observe(){} unobserve(){} disconnect(){} },
  requestAnimationFrame:(f)=>f(),
  setTimeout, clearTimeout,
  // Deterministic intervals: the edge auto-pan runs on one, and a test that
  // slept for real time would be both slow and flaky.
  setInterval:(f)=>{ intervals.set(++intervalId, f); return intervalId; },
  clearInterval:(id)=>{ intervals.delete(id); },
};
const winListeners = {};
const docListeners = {};
const fireDocument = (t, ev) => (docListeners[t]||[]).slice().forEach((f)=>f(ev));
const coarseTouch = { on: false };
const reducedMotion = { on: false };
// The editor dispatches config-changed as a CustomEvent; the stub only needs
// the shape the listeners read.
ctx.CustomEvent = class {
  constructor(type, opts = {}) {
    this.type = type; this.detail = opts.detail;
    this.bubbles = !!opts.bubbles; this.composed = !!opts.composed;
  }
};
const fireWindow = (t, ev) => (winListeners[t]||[]).slice().forEach((f)=>f(ev));
const intervals = new Map(); let intervalId = 0;
const tickIntervals = () => { for (const f of [...intervals.values()]) f(); };
ctx.globalThis = ctx; ctx.self = ctx; ctx.window.document = document;
vm.createContext(ctx);
const cardSrc = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8");
vm.runInContext(cardSrc, ctx);

const names = Object.keys(ctx.customElements._d);
console.log("defined elements:", names.join(", "));
console.log("customCards:", JSON.stringify(ctx.window.customCards));

const Card = ctx.customElements.get("heatpump-optimizer-card");
if (!Card) { console.error("FAIL: card not registered"); process.exit(1); }

const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";

// The irradiance sensor publishes its own {t, ghi} horizon. Its timestamps are
// already interval starts, so the card must plot them as-is.
const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));

const mkStates = (spaceId, dhwId, withMarker) => ({
  [SOLAR_ID]: { state:"120", attributes:{
    forecast: solarForecast, source:"open_meteo", friendly_name:"Solar Irradiance",
    ...(withMarker ? { plan_kind: "solar" } : {}) } },
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
function check(name, cond, detail) {
  console.log((cond ? "  ok  " : "  FAIL") + "  " + name);
  if (!cond) {
    if (detail) console.log("        " + detail);
    fails++;
  }
}

// --- Scenario 1: stock install, real (device-prefixed) entity ids ----------
const card = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
const dump = collect(card.shadowRoot).join("\n");

check("renders an <svg>", /<svg/.test(dump));
check("draws polyline/path data", /(<polyline|<path)/.test(dump));
check("draws heating bars", /<rect/.test(dump));
check("legend has all seven series", ["Electricity price","DHW heating","Space heating","Outdoor temperature","DHW tank temperature","House temperature","Solar irradiance"].every(l=>dump.includes(l)));
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


// --- Scenario 9: solar irradiance series (item 2) --------------------------
//
// The value of this check is that it exercises *discovery*: hardcoding
// `sensor.heat_pump_optimizer_solar_irradiance` is exactly the mistake that
// caused the v2.6.1 bug where the card never found its plan sensors, so the
// series has to be found by its `plan_kind` marker on a renamed entity too.
const solarCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
const solarDump = collect(solarCard.shadowRoot).join("\n");
check("solar series has data", solarCard._series.find(s => s.key === "solar").hasData);
check("solar gets its own W/m2 axis", /W\/m/.test(solarDump));
check("the solar axis does not share the power scale",
  solarCard._plot.axes.solar !== null && solarCard._plot.axes.solar !== solarCard._plot.axes.power);

// Turning the series off must give the plot its width back rather than
// permanently reserving room for an axis most users will not show.
const plotRWithSolar = solarCard._plot.plotR;
solarCard._onLegendClick({ currentTarget: { getAttribute: k => k === "data-key" ? "solar" : null } });
check("hiding solar returns the reserved axis width", solarCard._plot.plotR > plotRWithSolar);

const renamedSolar = build({
  ...mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
  "sensor.my_sun": { state:"90", attributes:{ forecast: solarForecast, plan_kind:"solar" } },
});
delete renamedSolar._hass.states[SOLAR_ID];
renamedSolar._resolvedCache = null;
check("discovers a renamed solar sensor by plan_kind",
  renamedSolar._resolveEntity("solar") === "sensor.my_sun");

// A missing solar sensor must not break the rest of the card.
const noSolar = build((() => { const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true); delete st[SOLAR_ID]; return st; })());
const noSolarDump = collect(noSolar.shadowRoot).join("\n");
check("a missing solar sensor degrades cleanly",
  /<svg/.test(noSolarDump) && !/No plan data available yet/.test(noSolarDump));

// --- Scenario 10: legend legibility in the popup (item 1) ------------------
//
// The legend is plain HTML, so it cannot literally be low resolution. What it
// was, was sized in em against the card's font, which does not grow with the
// dialog. The fix is a rule that scales it, so assert the rule exists and that
// it targets the dialog specifically.
const legendCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
legendCard._onCardClick({});
const legendDump = collect(legendCard.shadowRoot).join("\n");
check("the popup scales the legend up",
  /dialog\.expanded \.legend\s*\{[^}]*font-size/.test(legendDump));
check("the popup scales the legend chips and dots",
  /dialog\.expanded \.chip\s*\{[^}]*font-size/.test(legendDump) &&
  /dialog\.expanded \.chip \.dot\s*\{[^}]*width/.test(legendDump));

// SVG text is sized in viewBox units, so the same nominal size across a much
// larger chart reads as cramped. The expanded chart must use a larger one.
const expSvgs = legendDump.split("<svg").slice(1);
const maxFont = (s) => Math.max(0, ...[...s.matchAll(/font-size="(\d+)"/g)].map(m => Number(m[1])));
check("the popup chart uses a larger in-viewBox font",
  maxFont(expSvgs[expSvgs.length - 1]) > maxFont(expSvgs[0]));

// --- Scenario 11: plan reason codes (item 16) ------------------------------
//
// Without these an unexpected slot is indistinguishable from a bug, which is
// what makes bug reports weak and the optimizer hard to trust.
const reasonCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
const withReason = reasonCard._reasonHtml([
  { reason: "cheap_price" }, { reason: "cheap_price" }, { reason: "dhw_window" },
]);
check("reason codes render as readable text",
  /Cheapest hours/.test(withReason) && /Hot water needed now/.test(withReason));
check("a repeated reason is not repeated in the tooltip",
  (withReason.match(/Cheapest hours/g) || []).length === 1);
check("idle steps produce no explanation",
  reasonCard._reasonHtml([{ reason: "idle" }, {}]) === "");
check("an unknown reason code still shows something",
  /brand_new_code/.test(reasonCard._reasonHtml([{ reason: "brand_new_code" }])));

// --- Scenario 12: estimated prices are marked (item 7) ---------------------
//
// A plan that looks identical whether or not it rests on published prices
// cannot be audited, so the guessed stretch has to be visible.
const halfKnown = (() => {
  const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  const fc = plan.space_plan.forecast.map((p, i) => ({ ...p, price_known: i < 40 }));
  st[DEFAULT_SPACE].attributes.forecast = fc;
  return st;
})();
const markedCard = build(halfKnown);
const markedDump = collect(markedCard.shadowRoot).join("\n");
check("the estimated stretch of the horizon is shaded",
  /class="estimated"/.test(markedDump) && /estimated prices/.test(markedDump));
check("the tooltip says a price is estimated",
  /estimated, not published/.test(markedCard._reasonHtml([{ priceKnown: false }])));
check("a fully published horizon is not shaded",
  !/class="estimated"/.test(collect(build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)).shadowRoot).join("\n")));

// --- Scenario 13: what-if simulator ---------------------------------------
// The panel is on by default: editing a draft costs nothing, and only the
// Simulate and Save buttons reach Home Assistant. It can still be turned off.
const onCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
onCard._onCardClick({});
check("the schedule editor is available without extra configuration",
  /class="whatif"/.test(collect(onCard.shadowRoot).join("\n")));
check("and it is reachable in the expanded view specifically",
  /class="whatif"/.test(collect(onCard.shadowRoot).join("\n")) && onCard._expanded === true);

const offCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { what_if: false });
offCard._onCardClick({});
check("what_if: false still hides the panel",
  !/class="whatif"/.test(collect(offCard.shadowRoot).join("\n")));

let called = null;
const simResult = {
  monthly_cost_delta: -42.5,
  min_room_temperature: 19.4,
  baseline_min_room_temperature: 20.1,
  min_dhw_temperature: 46.0,
  baseline_min_dhw_temperature: 45.8,
  compressor_starts: 4,
  rate_limited: false,
};
const mkHass = (states, respond) => ({
  states,
  callService: async (domain, service, data) => {
    called = { domain, service, data };
    return respond ? respond() : { response: { results: { abc: simResult } } };
  },
});

// The plan sensors advertise the schedule the plan was made against, which is
// what the editor pre-fills from.
const slotStates = (() => {
  const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7;
  st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
  return st;
})();

const whatIf = build(slotStates, { what_if: true });
whatIf._hass = mkHass(whatIf._hass.states);
whatIf._onCardClick({});
const whatIfDump = collect(whatIf.shadowRoot).join("\n");
check("the what-if panel appears when enabled",
  /class="whatif"/.test(whatIfDump) && /class="wi-temp"/.test(whatIfDump));
check("the panel offers heating hour editors",
  /class="wi-day-start"/.test(whatIfDump) && /class="wi-day-end"/.test(whatIfDump));
check("the panel offers hot water window editors",
  /class="wi-win-start"/.test(whatIfDump) && /class="wi-add"/.test(whatIfDump));
check("it distinguishes simulating from saving",
  /Simulating changes\s+nothing/.test(whatIfDump) &&
  /saving replaces your configured schedule/.test(whatIfDump));

// Item 22. The comfort slider used to sit alone in the scheduling section with
// no context, which is what made it read as a stray control. It now shares a
// "Temperatures" section with the hot water minimum.
check("the temperature sliders have a section of their own",
  /Temperatures/.test(whatIfDump) && /class="wi-dhw-min"/.test(whatIfDump));
check("each slider has its own readout",
  /wi-comfort-value/.test(whatIfDump) && /wi-dhw-value/.test(whatIfDump));

// The two sliders deliberately share one debounce timer: independent timers
// racing on one service call is how the delta ends up pricing the *previous*
// drag rather than the current one.
{
  const comfortBefore = whatIf._whatIfDraft().comfort;
  const timerBefore = whatIf._whatIfTimer;
  whatIf._onWhatIfInput({
    stopPropagation(){},
    target:{ value:"42", classList:{ contains:(c)=>c === "wi-dhw-min" } },
  });
  check("the hot water slider writes its own draft field, not the comfort one",
    whatIf._whatIfDraft().dhwMin === 42 &&
    whatIf._whatIfDraft().comfort === comfortBefore);
  check("moving either slider uses the one shared debounce",
    whatIf._whatIfTimer !== timerBefore && whatIf._whatIfTimer !== null);
  check("the hot water readout follows its own slider",
    /42/.test(whatIf.shadowRoot.querySelector(".wi-dhw-value").textContent) &&
    !/42/.test(whatIf.shadowRoot.querySelector(".wi-comfort-value").textContent));
  // Leave no armed timer behind: it would fire mid-await further down and
  // overwrite `called` with a simulate the next assertion never asked for.
  clearTimeout(whatIf._whatIfTimer);
  whatIf._whatIfTimer = null;
  whatIf._whatIfDraft().dhwMin = 45;
}

// The ceiling is published by the integration rather than recomputed here, so
// the card and the backend validator cannot drift apart. A stored minimum that
// the setpoint no longer allows is lowered *and* said out loud -- silently
// reducing someone's hot water is exactly the kind of quiet correction that
// gets reported as a bug months later.
{
  const clampStates = (() => {
    const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    st[DEFAULT_SPACE].attributes.dhw_setpoint = 52;
    st[DEFAULT_SPACE].attributes.dhw_min_temperature_max = 47;
    st[DEFAULT_SPACE].attributes.dhw_min_temperature = 50;
    return st;
  })();
  const clamped = build(clampStates, { what_if: true });
  clamped._hass = mkHass(clamped._hass.states);
  clamped._onCardClick({});
  const dump = collect(clamped.shadowRoot).join("\n");
  check("a stored minimum above the ceiling is clamped to it",
    clamped._whatIfDraft().dhwMin === 47,
    `got ${clamped._whatIfDraft().dhwMin}`);
  check("and the clamp is visible rather than silent",
    /wi-warn/.test(dump) && /50/.test(dump));
  check("the slider's maximum comes from the published ceiling",
    /class="wi-dhw-min"[^>]*max="47"/.test(dump) ||
    /max="47"[^>]*class="wi-dhw-min"/.test(dump));
  check("the deadband is described from the setpoint actually in force",
    /52/.test(dump) && /5\s*&nbsp;°C band/.test(dump));
}

// Before the first plan arrives there is no setpoint to clamp against. The
// attribute is published as null in that case, and `Number(null)` is 0 -- a
// finite value that would sail through a naive isFinite guard and cap the
// slider at nothing.
{
  const blankStates = (() => {
    const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    st[DEFAULT_SPACE].attributes.dhw_min_temperature_max = null;
    st[DEFAULT_SPACE].attributes.comfort_temp_day = null;
    return st;
  })();
  const blank = build(blankStates, { what_if: true });
  blank._hass = mkHass(blank._hass.states);
  check("a null ceiling falls back instead of collapsing to zero",
    blank._dhwMinCeiling() === 45, `got ${blank._dhwMinCeiling()}`);
  check("a null comfort target falls back instead of reading as 0 °C",
    blank._whatIfDraft().comfort === 21,
    `got ${blank._whatIfDraft().comfort}`);
}

// The comfort target must come from our own plan, not from whatever climate
// entity happens to be enumerated first. A frost-protection valve, an air
// conditioner or a towel rail would otherwise pin the slider to its setpoint,
// which is where the mystery "5" came from.
const strayStates = (() => {
  const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  st[DEFAULT_SPACE].attributes.comfort_temp_day = 19.5;
  st["climate.frost_protection_valve"] = {
    state: "heat",
    attributes: { temperature: 5 },
  };
  return st;
})();
const strayCard = build(strayStates, { what_if: true });
strayCard._hass = mkHass(strayCard._hass.states);
check("the comfort target comes from the plan, not a stray thermostat",
  strayCard._whatIfDraft().comfort === 19.5,
  `got ${strayCard._whatIfDraft().comfort}`);

// Pre-filling from the live plan matters: an editor that starts from defaults
// would silently propose changes the user never asked for.
check("the heating hours are pre-filled from the plan",
  /value="07:00"/.test(whatIfDump) && /value="22:00"/.test(whatIfDump));
check("the hot water windows are pre-filled from the plan",
  whatIf._whatIfDraft().dhwWindows.length === 2 &&
  whatIf._whatIfDraft().dhwWindows[0].start === "06:00" &&
  whatIf._whatIfDraft().dhwWindows[1].end === "22:00");

// Temperature: debounced, then reported.
whatIf._onWhatIfInput({ stopPropagation(){}, target:{ value:"19.5" } });
check("dragging does not call the service immediately", called === null);
check("the label follows the slider straight away",
  /19\.5/.test(whatIf.shadowRoot.querySelector(".wi-value").textContent));

await whatIf._runWhatIf();
check("the simulator calls the right service",
  called && called.domain === "heatpump_optimizer" && called.service === "simulate_plan");
check("the simulator sends the dragged temperature",
  called && called.data.target_temp === 19.5);
check("the simulator sends the heating hours",
  called && called.data.day_start_hour === 7 && called.data.day_end_hour === 22);
check("the simulator sends the hot water windows",
  called && called.data.dhw_windows === "06:00-08:30, 17:00-22:00");

const resultText = whatIf.shadowRoot.querySelector(".wi-result").textContent;
check("a cheaper answer is reported as a monthly saving",
  /43 less per month/.test(resultText));
// Reporting only the saving would invite the obvious mistake: a plan is always
// cheaper if it is allowed to be colder.
check("the comfort consequence is reported alongside the money",
  /Coldest the house gets: 19\.4/.test(resultText) && /-0\.7/.test(resultText));
check("the hot water consequence is reported too",
  /Lowest tank temperature: 46\.0/.test(resultText));

// --- Scenario 14: editing the slots ---------------------------------------
const editor = build(slotStates, { what_if: true });
editor._hass = mkHass(editor._hass.states);
editor._onCardClick({});

// Editing a time field updates the draft without triggering a solve: a
// half-typed time should not cost a multi-second optimization.
const root = editor.shadowRoot;
root.querySelector(".wi-day-start").value = "05:00";
called = null;
editor._onSlotEdit({ stopPropagation(){} });
check("editing an hour does not simulate on its own", called === null);
check("editing an hour updates the draft", editor._whatIfDraft().dayStart === 5);

editor._onAddWindow({ stopPropagation(){} });
check("a window can be added", editor._whatIfDraft().dhwWindows.length === 3);
check("the added window is rendered",
  (collect(editor.shadowRoot).join("\n").match(/class="wi-window"/g) || []).length === 3);

editor._onRemoveWindow({
  stopPropagation(){},
  currentTarget: { getAttribute: (k) => (k === "data-index" ? "0" : null) },
});
const remaining = editor._whatIfDraft().dhwWindows;
check("a window can be removed", remaining.length === 2);
check("the right window was removed", remaining[0].start === "17:00");

await editor._onApplySlots({ stopPropagation(){} });
check("applying sends the edited hours",
  called && called.data.day_start_hour === 5);
check("applying sends the edited windows",
  called && called.data.dhw_windows === "17:00-22:00, 06:00-08:00",
  );

// Removing every window is a legitimate thing to price ("what if I stopped
// guaranteeing hot water at fixed times?"), so it must be sent as an explicit
// empty schedule rather than omitted. Driven through the UI, because the
// editors are the source of truth on apply.
while (editor._whatIfDraft().dhwWindows.length) {
  editor._onRemoveWindow({
    stopPropagation(){},
    currentTarget: { getAttribute: (k) => (k === "data-index" ? "0" : null) },
  });
}
check("all windows can be removed",
  !/class="wi-window"/.test(collect(editor.shadowRoot).join("\n")));
called = null;
await editor._onApplySlots({ stopPropagation(){} });
check("an empty schedule is sent explicitly, not omitted",
  called && called.data.dhw_windows === "" && "dhw_windows" in called.data);

// A malformed time must be caught before a solve is spent on it.
editor._whatIfDraft().dhwWindows = [{ start: "notatime", end: "08:00" }];
called = null;
await editor._runWhatIf();
check("an invalid window is rejected without calling the service",
  called === null &&
  /not a valid time/.test(editor.shadowRoot.querySelector(".wi-result").textContent));

// Reset must restore the plan's own schedule, not a hardcoded default.
editor._onResetWhatIf({ stopPropagation(){} });
check("reset restores the live schedule",
  editor._whatIfDraft().dayStart === 7 &&
  editor._whatIfDraft().dhwWindows.length === 2);

// Controls must not reach the card's expand handler underneath.
// Without this, a click anywhere in the panel reaches the card handler and
// collapses the dialog the panel lives in.
for (const [name, handler] of [
  ["add", editor._onAddWindow],
  ["reset", editor._onResetWhatIf],
  ["apply", editor._onApplySlots],
  ["edit", editor._onSlotEdit],
]) {
  let stopCount = 0;
  handler.call(editor, { stopPropagation: () => { stopCount++; } });
  check(`the ${name} control stops propagating to the card`, stopCount > 0);
}

// An error from the service must be shown, not swallowed.
editor._hass = mkHass(editor._hass.states, () => ({
  response: { results: { abc: { error: "invalid_windows: bad" } } },
}));
await editor._runWhatIf();
check("a rejected simulation reports why",
  /invalid_windows: bad/.test(editor.shadowRoot.querySelector(".wi-result").textContent));

editor._hass = { states: editor._hass.states, callService: async () => { throw new Error("boom"); } };
await editor._runWhatIf();
check("a failed simulation is reported, not swallowed",
  /Could not simulate: boom/.test(editor.shadowRoot.querySelector(".wi-result").textContent));

// ---------------------------------------------------------------------------
// Saving the edited schedule
// ---------------------------------------------------------------------------
// Simulating is reversible; saving rewrites the schedule the house runs on, so
// it takes two deliberate presses and must not fire on the first one.
const saver = build(slotStates, { what_if: true });
saver._openExpanded();
saver._hass = mkHass(saver._hass.states, () => ({}));
called = null;

const saveRoot = saver.shadowRoot;
check("the expanded card offers a save button",
  !!saveRoot.querySelector(".wi-save"));

await saver._onSaveSchedule({ stopPropagation: () => {} });
check("the first press does not call the service", called === null);
check("the first press asks for confirmation",
  /Confirm/i.test(saveRoot.querySelector(".wi-save").textContent));
check("the first press says what saving will do",
  /replaces your configured/i.test(saveRoot.querySelector(".wi-result").textContent));

await saver._onSaveSchedule({ stopPropagation: () => {} });
check("the second press calls apply_schedule",
  called && called.domain === "heatpump_optimizer" && called.service === "apply_schedule");
check("it sends the whole schedule, not a fragment",
  called && ["day_start_hour", "day_end_hour", "dhw_windows", "comfort_temp_day",
             "dhw_min_temperature"]
    .every((k) => called.data[k] !== undefined));
check("the button returns to its resting label",
  !/Confirm/i.test(saveRoot.querySelector(".wi-save").textContent));

// An edit between the two presses invalidates the confirmation: the user would
// otherwise confirm one schedule and save a different one.
const armed = build(slotStates, { what_if: true });
armed._openExpanded();
armed._hass = mkHass(armed._hass.states, () => ({}));
called = null;
await armed._onSaveSchedule({ stopPropagation: () => {} });
check("the confirmation is armed", armed._pendingSave === true);
armed.shadowRoot.querySelector(".wi-day-start").value = "04:00";
armed._onSlotEdit({ stopPropagation: () => {} });
check("editing a slot disarms the confirmation", armed._pendingSave === false);
await armed._onSaveSchedule({ stopPropagation: () => {} });
check("so the next press only re-arms, it does not save", called === null);

// Pressing save twice with no edit in between must still save: `_onSaveSchedule`
// runs `_onSlotEdit` itself, and an unchanged draft is not an edit.
called = null;
await armed._onSaveSchedule({ stopPropagation: () => {} });
check("an unchanged draft still confirms on the second press",
  called && called.service === "apply_schedule");

// Nonsense must be caught here rather than written to the configuration, where
// it would fail on every subsequent load.
const bad = build(slotStates, { what_if: true });
bad._openExpanded();
bad._hass = mkHass(bad._hass.states, () => ({}));
called = null;
bad.shadowRoot.querySelector(".wi-day-start").value = "07:00";
bad.shadowRoot.querySelector(".wi-day-end").value = "07:00";
await bad._onSaveSchedule({ stopPropagation: () => {} });
check("an empty comfort period is refused before it is saved",
  called === null && /no comfort period/i.test(bad.shadowRoot.querySelector(".wi-result").textContent));

const boom = build(slotStates, { what_if: true });
boom._openExpanded();
boom._hass = { states: boom._hass.states, callService: async () => { throw new Error("nope"); } };
await boom._onSaveSchedule({ stopPropagation: () => {} });
await boom._onSaveSchedule({ stopPropagation: () => {} });
check("a failed save is reported, not swallowed",
  /Could not save: nope/.test(boom.shadowRoot.querySelector(".wi-result").textContent));
check("and the button is usable again afterwards",
  boom.shadowRoot.querySelector(".wi-save").disabled === false);

// ---------------------------------------------------------------------------
// Chart text sizing
// ---------------------------------------------------------------------------
// Chart text is sized in viewBox units, and the whole chart geometry -- margins,
// tick spacing, legend rows -- is authored in those same units against a font of
// roughly that size. Sizing the font independently of the geometry is what made
// labels overlap, so the sizes are pinned here as part of the layout.
const svgFont = (expanded) => {
  const c = build(slotStates, {});
  if (expanded) c._openExpanded();
  const dump = collect(c.shadowRoot).join("\n");
  const wrap = expanded
    ? dump.slice(dump.indexOf('chartwrap big'))
    : dump.slice(0, dump.indexOf('chartwrap big') === -1 ? dump.length : dump.indexOf('chartwrap big'));
  const m = wrap.match(/font-size="([\d.]+)"/);
  return m ? Number(m[1]) : null;
};

// The real constraint is that labels must not run into each other. Label
// density used to be a fixed choice -- every hour when expanded -- which is
// comfortable over 12 hours and unreadable over 48, where labels sit 15 units
// apart and are 40 units wide. Measure the rendered labels instead of trusting
// the setting.
const timeLabels = (svg) => {
  const out = [];
  const re = /<text x="([-\d.]+)"[^>]*font-size="([\d.]+)"[^>]*text-anchor="middle"[^>]*>(\d{1,2}[:.]\d{2}[^<]*)<\/text>/g;
  let m;
  while ((m = re.exec(svg))) out.push({ x: Number(m[1]), size: Number(m[2]), text: m[3] });
  return out.sort((a, b) => a.x - b.x);
};

const collisions = (labels) => {
  const bad = [];
  for (let i = 1; i < labels.length; i++) {
    const prev = labels[i - 1];
    const cur = labels[i];
    // Centred labels, so each occupies half its width either side of x.
    const halfPrev = (prev.text.length * prev.size * 0.55) / 2;
    const halfCur = (cur.text.length * cur.size * 0.55) / 2;
    const gap = cur.x - prev.x - halfPrev - halfCur;
    if (gap < 0) bad.push(`${prev.text}/${cur.text} overlap by ${(-gap).toFixed(1)}u`);
  }
  return bad;
};

for (const expanded of [false, true]) {
  const c = build(slotStates, {});
  if (expanded) c._openExpanded();
  const dump = collect(c.shadowRoot).join("\n");
  // The shadow root holds the inline chart and, once opened, the expanded one
  // too. Compare labels within a single chart, or every label pairs with its
  // twin in the other chart at the same coordinate.
  const cut = dump.indexOf("chartwrap big");
  const scoped = expanded ? dump.slice(cut) : dump.slice(0, cut === -1 ? dump.length : cut);
  const labels = timeLabels(scoped);
  const where = expanded ? "expanded" : "inline";
  check(`the ${where} chart labels its time axis`, labels.length > 1,
    `found ${labels.length} time labels`);
  const bad = collisions(labels);
  check(`the ${where} time axis labels do not overlap`, bad.length === 0,
    bad.join("; "));
}

// The value-axis titles have the same problem as the time labels, in the one
// place the chart puts two axes on one side. The gap between the price axis and
// the solar axis is a fixed 46 viewBox units and does not grow with the font, so
// at the expanded size "SEK/kWh" is wider than the space it has and used to run
// straight through "W/m2".
const axisTitles = (svg) => {
  const out = [];
  const re =
    /<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)"[^>]*>([^<]*)<\/text>/g;
  let m;
  while ((m = re.exec(svg))) {
    const [, x, y, size, anchor, text] = m;
    if (!/^(kW|°C|SEK\/kWh|W\/m²)$/.test(text)) continue;
    const w = text.length * Number(size) * 0.55;
    const left = anchor === "end" ? Number(x) - w : Number(x);
    out.push({ text, anchor, x: Number(x), y: Number(y), left, right: left + w });
  }
  return out.sort((a, b) => a.left - b.left);
};

// `_hidden` is persisted in localStorage, which the stub shares across every
// build in this file. Force the series on: with solar hidden there is no second
// right-hand axis and this stops testing the case it exists for.
const withAllSeries = (config) => {
  const c = build(slotStates, config || {});
  c._hidden = {};
  c._sig = null;
  return c;
};

for (const expanded of [false, true]) {
  const c = withAllSeries();
  if (expanded) c._openExpanded();
  else c._render();
  const dump = collect(c.shadowRoot).join("\n");
  const cut = dump.indexOf("chartwrap big");
  const scoped = expanded ? dump.slice(cut) : dump.slice(0, cut === -1 ? dump.length : cut);
  const titles = axisTitles(scoped);
  const where = expanded ? "expanded" : "inline";
  check(`the ${where} chart titles its value axes`, titles.length >= 3,
    `found ${titles.map((t) => t.text).join(", ")}`);
  check(`the ${where} chart really is showing both right-hand axes`,
    titles.some((t) => t.text === "W/m²") && titles.some((t) => t.text === "SEK/kWh"),
    "otherwise this is not testing the crowded case at all");
  const bad = [];
  for (let i = 1; i < titles.length; i++) {
    if (Math.abs(titles[i].y - titles[i - 1].y) > 1) continue;
    const gap = titles[i].left - titles[i - 1].right;
    if (gap < 0)
      bad.push(`${titles[i - 1].text}/${titles[i].text} overlap by ${(-gap).toFixed(1)}u`);
  }
  check(`the ${where} value axis titles do not overlap`, bad.length === 0, bad.join("; "));
}

// The flip is conditional, not unconditional: with no solar series there is no
// second right-hand axis, so the price title must stay where it always sat.
{
  const expandedTitles = (card) => {
    const dump = collect(card.shadowRoot).join("\n");
    return axisTitles(dump.slice(dump.indexOf("chartwrap big")));
  };

  const withSolar = withAllSeries();
  withSolar._openExpanded();
  const a = expandedTitles(withSolar);
  const priceWith = a.find((t) => t.text === "SEK/kWh");

  const noSolar = withAllSeries();
  noSolar._hidden = { solar: true };
  noSolar._sig = null;
  noSolar._openExpanded();
  const b = expandedTitles(noSolar);
  const priceWithout = b.find((t) => t.text === "SEK/kWh");

  check("the price title is pushed aside when the solar axis crowds it",
    priceWith && priceWith.anchor === "end",
    priceWith && `anchor ${priceWith.anchor}`);
  check("and left exactly where it was when nothing crowds it",
    priceWithout && priceWithout.anchor === "start",
    priceWithout && `anchor ${priceWithout.anchor}`);
  check("the solar title itself never moves",
    !b.some((t) => t.text === "W/m²") &&
      a.some((t) => t.text === "W/m²" && t.anchor === "start"));
}

// Density must follow the space available, not a hardcoded interval, so the
// same code stays readable at any horizon.
check("label density is derived, not hardcoded",
  !/expanded \? 1 : 3/.test(cardSrc),
  "the time axis still picks a fixed label interval");

const inlineFont = svgFont(false);
check("chart text is sized in the units its layout was authored in",
  inlineFont !== null && inlineFont <= 12,
  `got ${inlineFont} units; the 92-unit left margin and 34-unit bottom margin ` +
  `are sized for about 10, so a larger font collides with its neighbours`);

// The chart is stretched from a fixed viewBox, so a given size in those units
// already renders larger in a wider container. That is the scaling; it does not
// need help from a larger unit count.
check("the chart scales by being stretched, not by inflating its font",
  /preserveAspectRatio="none"/.test(collect(build(slotStates, {}).shadowRoot).join("\n")));

// The chrome around the chart is plain HTML and cannot scale by itself, so the
// dialog font is set from the measured width. Clamped at both ends.
const fontCard = build(slotStates, {});
fontCard._openExpanded();
const dlgOf = (w) => {
  const d = fontCard.shadowRoot.querySelector("dialog");
  d.getBoundingClientRect = () => ({ width: w });
  if (!d.style) d.style = {};
  fontCard._dialogFontPx = 0;
  fontCard._scaleDialogFont();
  return fontCard._dialogFontPx;
};
check("a wide dialog gets larger chrome than a narrow one",
  dlgOf(1800) > dlgOf(700));
check("a phone-width dialog stays legible", dlgOf(320) >= 12 - 1e-9);
check("a very wide dialog does not turn the legend into a headline",
  dlgOf(4000) <= 21 + 1e-9);
check("an unmeasured dialog is left alone rather than sized from zero",
  dlgOf(0) === 0);


// ---------------------------------------------------------------------------
// The slot model itself
// ---------------------------------------------------------------------------
// The editing rules are pure functions on plain arrays, exposed as a static so
// they can be exercised without a pointer, a chart or a clock.
{
  const S = Card.slots;
  const t0 = Date.parse("2026-08-22T00:00:00Z");
  const STEP = 15 * 60000;
  const H = (h) => t0 + h * 3600000;
  const bounds = [t0, H(24)];

  const fc = [];
  for (let i = 0; i < 96; i++) {
    fc.push({
      t: new Date(t0 + i * STEP).toISOString(),
      dhw_power: (i >= 8 && i < 12) || (i >= 40 && i < 44) ? 2 : 0,
      price: 1,
    });
  }
  const runs = S.runsFrom(fc, "dhw_power", 0.05, STEP);
  check("consecutive running steps collapse into one slot",
    runs.length === 2 && runs[0].start === H(2) && runs[0].end === H(3),
    JSON.stringify(runs));

  let r = S.move(runs, 0, 3600000, STEP, bounds);
  check("a slot moves without changing length",
    r[0].start === H(3) && r[0].end === H(4), JSON.stringify(r[0]));
  r = S.move(runs, 0, 1000 * 3600000, STEP, bounds);
  check("a slot pushed past the horizon stops there, unstretched",
    r[r.length - 1].end - r[r.length - 1].start === 3600000, JSON.stringify(r));
  r = S.move(runs, 0, 9 * 3600000, STEP, bounds);
  check("dragging a slot onto another merges them", r.length === 1, JSON.stringify(r));

  r = S.resize(runs, 0, "end", 3600000, STEP, bounds);
  check("resizing the end leaves the start alone",
    r[0].start === H(2) && r[0].end === H(4), JSON.stringify(r[0]));
  r = S.resize(runs, 0, "start", -3600000, STEP, bounds);
  check("resizing the start leaves the end alone",
    r[0].start === H(1) && r[0].end === H(3), JSON.stringify(r[0]));
  r = S.resize(runs, 0, "end", -99 * 3600000, STEP, bounds);
  check("a slot never collapses below one timestep",
    r[0].end - r[0].start === STEP, JSON.stringify(r[0]));
  r = S.resize(runs, 0, "start", -99 * 3600000, STEP, bounds);
  check("resizing cannot reach back before the editable range",
    r[0].start >= t0, JSON.stringify(r[0]));

  r = S.add(runs, H(20), STEP, bounds);
  check("a slot can be added in free space", r.length === 3, JSON.stringify(r));
  // Adding next to an existing slot must not swallow it: the new slot stops at
  // its neighbour, and the two then merge into one continuous block.
  r = S.add(runs, H(9), STEP, bounds, 4 * 3600000);
  const added = r.find((x) => x.start === H(9));
  check("a slot added beside another merges rather than swallowing it",
    r.length === 2 && added && added.end === H(11), JSON.stringify(r));
  r = S.add(runs, H(24), STEP, bounds);
  const last = r[r.length - 1];
  check("adding at the far edge still gives a usable slot",
    r.length === 3 && last.end === H(24) && last.end - last.start === STEP,
    JSON.stringify(last));

  check("a slot can be removed", S.remove(runs, 0).length === 1);
  check("a time resolves to the slot covering it",
    S.indexAt(runs, H(2) + 60000) === 0 && S.indexAt(runs, H(5)) === -1);

  const power = S.typicalPower(fc, "dhw_power");
  check("typical power is the mean of the running steps", power === 2, String(power));
  check("cost is power x time x price",
    Math.abs(S.cost(runs, fc, power, STEP) - 4) < 1e-9);
}

// ---------------------------------------------------------------------------
// Direct manipulation of today's slots
// ---------------------------------------------------------------------------
// The slots are edited by dragging them on the chart, so the interesting logic
// is geometric: a pointer position has to become a time, and a drag has to
// become a new arrangement. The stub reports the svg as 900px wide against a
// 900-unit viewBox, so a client x and a viewBox x coincide here; the card is
// still asked for the geometry it recorded rather than told what it should be.
const HOUR = 3600000;

// The captured plan is dated to the day it was recorded, so the clock has to
// be moved to the plan rather than the plan to the clock. Re-dating the plan
// against the real clock made these checks depend on what time of day the
// suite happened to run: the edit floor is "now", so the set of slots still in
// the future changed from one run to the next. Freeze time six hours into the
// captured day instead, which always leaves both a locked past and an
// editable future.
const RealDate = Date;
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
class FrozenDate extends RealDate {
  constructor(...a) { super(...(a.length ? a : [FROZEN])); }
  static now() { return FROZEN; }
}
ctx.Date = FrozenDate;

const drag = build(slotStates, { what_if: true });
drag._hass = mkHass(drag._hass.states);
drag._onCardClick({});

const laneDump = collect(drag.shadowRoot).join("\n");
check("the chart grows editable lanes", /class="lane"/.test(laneDump));
check("both channels get a lane",
  /data-channel="dhw"/.test(laneDump) && /data-channel="space"/.test(laneDump));
check("the plan is drawn as draggable slots", /class="slot"/.test(laneDump));
check("slots carry resize handles", /class="slot-handle"/.test(laneDump));

const svgOf = (card) => card.shadowRoot.querySelector(".chartwrap svg");
const fire = (el, type, ev) => (el._listeners[type] || []).forEach((f) => f(ev));

const geom = drag._geom;
check("the card records the geometry a pointer needs",
  !!geom && Number.isFinite(geom.plotL) && geom.plotW > 0);

const xOf = (t) =>
  geom.plotL + ((t - geom.windowStart) / (geom.windowEnd - geom.windowStart)) * geom.plotW;

// Round-tripping a time through the geometry is the whole basis of dragging.
const probe = geom.windowStart + 5 * HOUR;
check("a screen position maps back to the time under it",
  Math.abs(drag._timeAtClientX(svgOf(drag), xOf(probe)) - probe) < 60000);

const evAt = (t, target) => ({
  clientX: xOf(t), clientY: 0, target,
  stopPropagation() {}, preventDefault() {},
});

// A slot that is entirely in the past cannot be rescheduled, so pick one that
// the editor will actually let us move.
const editable = () => {
  const runs = drag._draftRuns().dhw;
  const [lo] = drag._editBounds();
  const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
  return { runs, i };
};

{
  const { runs, i } = editable();
  check("there is a future hot water slot to edit", i >= 0);
  if (i >= 0) {
    const before = { ...runs[i] };
    const [lo0] = drag._editBounds();
    const pastBefore = JSON.stringify(runs.filter((r) => r.end <= lo0));
    const svg = svgOf(drag);
    const target = { dataset: { channel: "dhw", index: String(i) } };
    fire(svg, "pointerdown", evAt(before.start + 60000, target));
    fire(svg, "pointermove", evAt(before.start + 60000 + HOUR, target));
    const moved = drag._draftRuns().dhw[i];
    check("dragging a slot moves it",
      moved && moved.start === before.start + HOUR,
      `${before.start} -> ${moved && moved.start}`);
    check("and keeps its length",
      moved && moved.end - moved.start === before.end - before.start);
    // Making room for an edit must not rewrite what already happened: the
    // editable range starts at the present, and clamping every slot into it
    // would haul this morning's runs forward and merge them together.
    const history = drag._draftRuns().dhw.filter((r) => r.end <= lo0);
    check("editing leaves slots that have already run untouched",
      JSON.stringify(history) === pastBefore,
      `${pastBefore} -> ${JSON.stringify(history)}`);
    fire(svg, "pointerup", {});
  }
}

{
  // Re-seed from the plan so the resize starts from a known arrangement.
  drag._resetRuns();
  drag._render();
  const { runs, i } = editable();
  if (i >= 0) {
    const before = { ...runs[i] };
    const svg = svgOf(drag);
    const target = { dataset: { channel: "dhw", index: String(i), edge: "end" } };
    fire(svg, "pointerdown", evAt(before.end, target));
    fire(svg, "pointermove", evAt(before.end + HOUR, target));
    const sized = drag._draftRuns().dhw[i];
    check("dragging an edge resizes the slot",
      sized && sized.end === before.end + HOUR && sized.start === before.start,
      JSON.stringify(sized));
    fire(svg, "pointerup", {});
  }
}

// Editing must never rewrite history.
{
  drag._resetRuns();
  const [lo] = drag._editBounds();
  const past = drag._draftRuns().dhw.findIndex((r) => r.end <= lo);
  if (past >= 0) {
    const before = JSON.stringify(drag._draftRuns().dhw[past]);
    const svg = svgOf(drag);
    const target = { dataset: { channel: "dhw", index: String(past) } };
    fire(svg, "pointerdown", evAt(lo - HOUR, target));
    fire(svg, "pointermove", evAt(lo, target));
    check("a slot that has already happened cannot be dragged",
      JSON.stringify(drag._draftRuns().dhw[past]) === before);
    fire(svg, "pointerup", {});
  } else {
    check("a slot that has already happened cannot be dragged", true);
  }
}

// Right-click: add where there is nothing, remove where there is something.
{
  drag._resetRuns();
  drag._render();
  const svg = svgOf(drag);
  const runs = drag._draftRuns().space;
  const [lo, hi] = drag._editBounds();
  // A time inside the editable range that no slot covers, and that is clear of
  // its neighbours: a slot added flush against another correctly merges with
  // it, which is a different behaviour and is covered by the model checks.
  let gap = null;
  for (let t = lo + HOUR; t < hi - HOUR; t += 15 * 60000) {
    if ([-HOUR, 0, HOUR].every((d) => slotFree(runs, t + d))) { gap = t; break; }
  }
  function slotFree(list, t) { return !list.some((r) => t >= r.start && t < r.end); }

  check("there is a free stretch to add into", gap !== null);
  if (gap !== null) {
    fire(svg, "contextmenu", evAt(gap, { dataset: { channel: "space" } }));
    const menu = drag.shadowRoot.querySelector(".slot-menu");
    check("right-clicking an empty lane offers to add a slot",
      !!menu && /Add a heating slot here/.test(collect(menu).join("")));
    if (menu) {
      const n = drag._draftRuns().space.length;
      fire(menu, "click", { target: { dataset: { act: "add" } }, stopPropagation() {} });
      check("choosing add creates a slot",
        drag._draftRuns().space.length === n + 1,
        JSON.stringify(drag._draftRuns().space));
      check("and the menu closes", !drag.shadowRoot.querySelector(".slot-menu"));
    }
  }
}

{
  drag._resetRuns();
  drag._render();
  const svg = svgOf(drag);
  const { runs, i } = (() => {
    const list = drag._draftRuns().space;
    const [lo] = drag._editBounds();
    return { runs: list, i: list.findIndex((r) => r.end > lo) };
  })();
  if (i >= 0) {
    fire(svg, "contextmenu",
      evAt(runs[i].start + 60000, { dataset: { channel: "space" } }));
    const menu = drag.shadowRoot.querySelector(".slot-menu");
    check("right-clicking a slot offers to remove it",
      !!menu && /Remove this heating slot/.test(collect(menu).join("")));
    if (menu) {
      const n = drag._draftRuns().space.length;
      fire(menu, "click", { target: { dataset: { act: "remove" } }, stopPropagation() {} });
      check("choosing remove deletes it", drag._draftRuns().space.length === n - 1);
    }
  }
}

// The price delta is the point of the exercise: it has to move, and in the
// right direction, when the arrangement changes.
{
  drag._resetRuns();
  const base = drag._costDelta();
  check("an untouched arrangement costs the same as the plan",
    Math.abs(base.delta) < 1e-9, JSON.stringify(base));

  const runs = drag._draftRuns().dhw;
  const [lo] = drag._editBounds();
  const i = runs.findIndex((r) => r.end > lo);
  if (i >= 0) {
    drag._commitRuns("dhw", SlotModelOf(drag).remove(runs, i));
    const less = drag._costDelta();
    check("removing a slot is reported as cheaper", less.delta < 0,
      JSON.stringify(less));
  }
  function SlotModelOf(card) { return card.constructor.slots; }
}

// Applying pins the arrangement through the service the backend exposes.
{
  drag._resetRuns();
  drag._render();
  called = null;
  drag._applyManualPlan();
  check("applying calls the manual plan service",
    called && called.domain === "heatpump_optimizer" &&
    called.service === "apply_manual_plan",
    JSON.stringify(called && { d: called.domain, s: called.service }));
  const sent = (called && called.data) || {};
  check("it sends both channels",
    Array.isArray(sent.dhw_slots) && Array.isArray(sent.space_slots));
  const [lo] = drag._editBounds();
  const allFuture = [...(sent.dhw_slots || []), ...(sent.space_slots || [])]
    .every((s) => Date.parse(s.end) > lo && Date.parse(s.start) >= lo);
  check("it never tries to reschedule the past", allFuture,
    JSON.stringify(sent.dhw_slots || []));
  const iso = (sent.dhw_slots || [])[0];
  check("slots are sent as ISO timestamps",
    !iso || (!Number.isNaN(Date.parse(iso.start)) && /T/.test(iso.start)),
    JSON.stringify(iso));
}

// Prices are shown in the user's currency, not the author's.
{
  const saved = drag._hass;
  drag._hass = { ...saved, config: { currency: "EUR" } };
  check("Home Assistant's configured currency is used",
    /EUR/.test(drag._deltaHtml()), drag._deltaHtml());
  drag._config = { ...drag._config, currency: "NOK" };
  check("an explicit card setting still wins",
    /NOK/.test(drag._deltaHtml()), drag._deltaHtml());
  drag._config = { ...drag._config, currency: undefined };
  drag._hass = saved;
  check("with neither, it falls back rather than showing nothing",
    /SEK/.test(drag._deltaHtml()), drag._deltaHtml());
}

// Every reason the optimizer can emit needs a human label, or the tooltip
// falls back to showing a raw identifier.
check("the hand-scheduled reason has a label",
  /You scheduled this/.test(cardSrc) && /manual_plan:/.test(cardSrc));

// The plan is re-optimised every few minutes. The draft has to follow it,
// except where the user has said otherwise by editing.
{
  const fresh = build(slotStates, { what_if: true });
  fresh._hass = mkHass(slotStates);
  fresh._onCardClick({});
  const seeded = JSON.stringify(fresh._draftRuns().dhw);

  // A refresh carrying a different plan must be picked up.
  const moved = JSON.parse(JSON.stringify(slotStates));
  const fc = moved[DEFAULT_DHW].attributes.forecast;
  fc.forEach((f) => { f.dhw_power = 0; });
  for (let i = 60; i < 66; i++) fc[i].dhw_power = 3;
  fresh.hass = { ...mkHass(moved), states: moved };
  const followed = JSON.stringify(fresh._draftRuns().dhw);
  check("an untouched draft follows a newly published plan",
    followed !== seeded, followed);

  // But an edit in progress must not be thrown away by a refresh landing
  // mid-drag: that would discard work the user can see themselves doing.
  const edited = fresh._draftRuns().dhw;
  const [lo] = fresh._editBounds();
  const i = edited.findIndex((r) => r.end > lo && r.start >= lo);
  if (i >= 0) {
    fresh._commitRuns("dhw", Card.slots.move(
      edited, i, HOUR, 15 * 60000, fresh._editBounds()
    ));
    const mine = JSON.stringify(fresh._draftRuns().dhw);
    const again = JSON.parse(JSON.stringify(moved));
    again[DEFAULT_DHW].attributes.forecast[70].dhw_power = 2;
    fresh.hass = { ...mkHass(again), states: again };
    check("but edits in progress survive a refresh",
      JSON.stringify(fresh._draftRuns().dhw) === mine);
  }
}

// A channel with no plan data means "we do not know", which is not the same as
// "the user wants it off": sending [] would switch hot water off until midnight.
{
  const partial = JSON.parse(JSON.stringify(slotStates));
  partial[DEFAULT_DHW].attributes.forecast = [];
  const c = build(partial, { what_if: true });
  c._hass = mkHass(partial);
  c._onCardClick({});
  called = null;
  c._applyManualPlan();
  check("a channel with no plan data is left automatic",
    called && called.data && !("dhw_slots" in called.data),
    JSON.stringify(called && called.data));
  check("while the channel that does have a plan is still pinned",
    called && Array.isArray(called.data.space_slots));

  const blank = JSON.parse(JSON.stringify(slotStates));
  blank[DEFAULT_DHW].attributes.forecast = [];
  blank[DEFAULT_SPACE].attributes.forecast = [];
  const empty = build(blank, { what_if: true });
  empty._hass = mkHass(blank);
  empty._onCardClick({});
  called = null;
  empty._applyManualPlan();
  check("with no plan at all, nothing is pinned", called === null);
}

// An override now lasts a fixed window from the moment it is applied, so the
// chart must not let a slot be dragged past that: a slot shown as pinned that
// quietly does nothing would be worse than not offering the gesture at all.
//
// This used to recompute midnight by hand and assert the ceiling was below it,
// which said nothing once the rule changed. The ceiling is now clock-independent
// -- it is measured from `now` -- so it can be asserted directly.
{
  const [, hi] = drag._editBounds();
  const WINDOW_H = 20;
  const applyEnd = FROZEN + WINDOW_H * HOUR;
  check("editing stops at the window the card would actually send",
    hi <= applyEnd + 1000,
    `${new Date(hi).toISOString()} vs ${new Date(applyEnd).toISOString()}`);

  // The ceiling has to come from the integration, not from a literal in the
  // card, or the chart and the service's expiry default could drift apart and
  // the chart would show slots as pinned past the point the backend frees them.
  check("the window is read from the plan, not hardcoded in the card",
    /manual_plan_window_hours/.test(cardSrc),
    "the card should read the published window");

  // Deliberately not the active override's expiry. One applied 15 hours ago has
  // 5 left, but the user editing now is composing a new plan that will last the
  // full window from this moment -- deriving the ceiling from the old expiry
  // would shrink the editable window through the day.
  {
    // An override applied 15 hours ago, with 5 left to run.
    const stale = build((() => {
      const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
      const info = {
        active: true,
        expires_at: new Date(FROZEN + 5 * HOUR).toISOString(),
        space_slots: [], dhw_slots: [], released_space: [], released_dhw: [],
      };
      st[DEFAULT_SPACE].attributes.manual_override = info;
      st[DEFAULT_DHW].attributes.manual_override = info;
      return st;
    })(), { what_if: true });
    stale._openExpanded();
    const [, staleHi] = stale._editBounds();
    check("the ceiling ignores the expiry already in force",
      staleHi > FROZEN + 5 * HOUR,
      `ceiling ${new Date(staleHi).toISOString()} would shrink to the old expiry`);
  }

  // Dragging hard to the right must stop there rather than run past it.
  drag._resetRuns();
  const runs = drag._draftRuns().dhw;
  const [lo] = drag._editBounds();
  const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
  if (i >= 0) {
    const pushed = Card.slots.move(
      runs, i, 72 * HOUR, 15 * 60000, drag._editBounds()
    );
    check("a slot cannot be dragged past the expiry",
      pushed.every((r) => r.end <= hi), JSON.stringify(pushed));
  }

  // And nothing sent to the backend may reach past it either, since the
  // backend frees every step at or beyond the expiry.
  drag._resetRuns();
  called = null;
  drag._applyManualPlan();
  const sent = [
    ...((called && called.data && called.data.dhw_slots) || []),
    ...((called && called.data && called.data.space_slots) || []),
  ];
  check("there are slots to send in the first place", sent.length > 0);
  check("no slot is sent past the expiry",
    sent.every((sl) => Date.parse(sl.end) <= hi),
    JSON.stringify(sent.filter((sl) => Date.parse(sl.end) > hi)));
}

// An override is a state the user is in, not just an action they took, so the
// card has to show it -- including when the optimizer overruled part of it.
{
  check("with no override there is nothing to go back from",
    !drag.shadowRoot.querySelector(".wi-auto"));
  check("and no override banner", !drag.shadowRoot.querySelector(".wi-override"));

  const withOverride = (info) => {
    const states = JSON.parse(JSON.stringify(slotStates));
    for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) {
      states[id].attributes.manual_override = info;
    }
    const c = build(states, { what_if: true });
    c._hass = mkHass(states);
    c._onCardClick({});
    return c;
  };

  const pinned = withOverride({
    active: true,
    expires_at: new Date(FROZEN + 6 * HOUR).toISOString(),
    space_slots: [], dhw_slots: [], released_space: [], released_dhw: [],
  });
  const banner = pinned.shadowRoot.querySelector(".wi-override");
  check("an active override is announced", !!banner);
  check("and says how long it lasts",
    !!banner && /pinned until \d/i.test(banner.textContent),
    banner && banner.textContent);
  check("and offers a way back to automatic",
    !!pinned.shadowRoot.querySelector(".wi-auto"));

  // The optimizer releases pins that would breach a safety limit. Staying
  // quiet about that would leave the user believing a plan that is not running.
  const released = withOverride({
    active: true,
    expires_at: new Date(FROZEN + 6 * HOUR).toISOString(),
    space_slots: [], dhw_slots: [],
    released_space: [{ start: "x", end: "y" }],
    released_dhw: [],
  });
  const note = released.shadowRoot.querySelector(".wi-override");
  check("a pin released for safety is reported, not hidden",
    !!note && /released to protect/i.test(note.textContent),
    note && note.textContent);
}

{
  called = null;
  drag._clearManualPlan();
  check("going back to automatic clears the override",
    called && called.service === "clear_manual_plan");
}

// ---------------------------------------------------------------------------
// Touch can edit too (field report: on a phone, existing slots could not be
// modified or removed at all — the menu lived behind right-click, which iOS
// Safari never synthesises, and the resize handles were ~7 px wide).
// ---------------------------------------------------------------------------
{
  drag._resetRuns();
  drag._view = null;
  drag._render();
  const svg = svgOf(drag);
  const { runs, i } = editable();
  check("(setup) a future slot exists to tap", i >= 0);
  if (i >= 0) {
    // Tap ON a slot: down + up with no movement opens the menu with Remove.
    const target = { dataset: { channel: "dhw", index: String(i) } };
    fire(svg, "pointerdown", evAt(runs[i].start + 60000, target));
    fire(svg, "pointerup", {});
    let menu = drag.shadowRoot.querySelector(".slot-menu");
    check("tapping a slot opens the slot menu (no right-click needed)",
      !!menu && /Remove this hot water slot/.test(collect(menu).join("")),
      menu ? collect(menu).join("") : "no menu");
    if (menu) {
      const n = drag._draftRuns().dhw.length;
      fire(menu, "click", { target: { dataset: { act: "remove" } }, stopPropagation() {} });
      check("and Remove removes it", drag._draftRuns().dhw.length === n - 1);
    }

    // Tap on an EMPTY editable stretch: the add menu, from a bare press.
    drag._resetRuns();
    drag._render();
    const [lo2, hi2] = drag._editBounds();
    const space = drag._draftRuns().space;
    let gap2 = null;
    for (let t = lo2 + HOUR; t < hi2 - HOUR; t += 15 * 60000) {
      if (!space.some((r) => t >= r.start - HOUR && t < r.end + HOUR)) { gap2 = t; break; }
    }
    check("(setup) an empty stretch exists", gap2 !== null);
    if (gap2 !== null) {
      fire(svgOf(drag), "pointerdown", evAt(gap2, { dataset: { channel: "space" } }));
      fire(svgOf(drag), "pointerup", {});
      menu = drag.shadowRoot.querySelector(".slot-menu");
      check("tapping an empty lane offers to add a slot",
        !!menu && /Add a heating slot here/.test(collect(menu).join("")));
      if (menu) fire(menu, "click", { target: { dataset: {} }, stopPropagation() {} });
      drag._closeSlotMenu();
    }

    // A DRAG must not open the menu on release.
    drag._resetRuns();
    drag._render();
    const e2 = editable();
    if (e2.i >= 0) {
      const t2 = { dataset: { channel: "dhw", index: String(e2.i) } };
      fire(svgOf(drag), "pointerdown", evAt(e2.runs[e2.i].start + 60000, t2));
      fire(svgOf(drag), "pointermove", evAt(e2.runs[e2.i].start + 60000 + HOUR, t2));
      fire(svgOf(drag), "pointerup", {});
      check("a real drag does not open the menu on release",
        !drag.shadowRoot.querySelector(".slot-menu"));
    }
  }

  // Coarse pointers get finger-sized resize handles; fine pointers keep the
  // slim ones the mouse tests above rely on.
  drag._resetRuns();
  coarseTouch.on = true;
  drag._render();
  const dumpCoarse = collect(drag.shadowRoot).join("\n");
  coarseTouch.on = false;
  drag._render();
  const dumpFine = collect(drag.shadowRoot).join("\n");
  const widthOf = (dump) => {
    const m = dump.match(/class="slot-handle"[^>]*width="([0-9.]+)"/);
    return m ? Number(m[1]) : null;
  };
  check("touch widens the grab handles", widthOf(dumpCoarse) === 16,
    `coarse width ${widthOf(dumpCoarse)}`);
  check("mouse keeps the slim handles", widthOf(dumpFine) === 6,
    `fine width ${widthOf(dumpFine)}`);
}

// ---------------------------------------------------------------------------
// Zoom-limited editing: the ceiling names its cause, and dragging pans it
// away (user report on v4.0.0: "slots can only be edited until midnight" —
// a forgotten zoom had clamped the edit ceiling to the visible window).
// ---------------------------------------------------------------------------
{
  drag._resetRuns();
  drag._view = null;
  drag._render();
  const dump0 = collect(drag.shadowRoot).join("\n");
  check("an unzoomed card shows no view-limit hint", !/class="wi-viewlimit"/.test(dump0));
  check("and no lane chevron", !/class="lane-more"/.test(dump0));

  drag._zoomView(0.25);
  const parts = drag._editCeilingParts();
  check("zoomed: the visible edge is the binding edit limit",
    drag._editCeiling() === drag._geom.windowEnd &&
      parts.visibleEnd < Math.min(parts.applyEnd, parts.planEnd),
    JSON.stringify({ceiling: drag._editCeiling(), parts}));
  const dump1 = collect(drag.shadowRoot).join("\n");
  check("the lanes flag the zoom with a chevron", /class="lane-more"/.test(dump1));
  check("the what-if panel says the zoom is the limit", /class="wi-viewlimit"/.test(dump1));

  // Auto-pan: grab a slot, park the pointer at the plot's right edge, and let
  // the interval carry the view forward.
  const zoomGeom = drag._geom;
  const zx = (t) =>
    zoomGeom.plotL +
    ((t - zoomGeom.windowStart) / (zoomGeom.windowEnd - zoomGeom.windowStart)) *
      zoomGeom.plotW;
  const zRuns = drag._draftRuns().dhw;
  const [zlo] = drag._editBounds();
  const zi = zRuns.findIndex((r) => r.end > zlo && r.start >= zlo && r.start < zoomGeom.windowEnd);
  check("there is a visible slot to drag against the edge", zi >= 0);
  if (zi >= 0) {
    const startView = drag._viewCurrent().start;
    const target = { dataset: { channel: "dhw", index: String(zi) } };
    fire(svgOf(drag), "pointerdown", {
      clientX: zx(zRuns[zi].start + 60000), clientY: 0, target,
      stopPropagation() {}, preventDefault() {},
    });
    fireWindow("pointermove", { clientX: 897, clientY: 0, target: {} });
    tickIntervals();
    tickIntervals();
    tickIntervals();
    check("holding the drag at the edge pans the view forward",
      drag._viewCurrent().start > startView,
      `${startView} -> ${drag._viewCurrent().start}`);
    fireWindow("pointerup", {});
    check("releasing the drag stops the auto-pan", !drag._dragPan);
  }

  // Closing the dialog ends the session, and the view with it: one
  // accidental pinch used to cap editing for days on a wall-mounted
  // dashboard, because the view re-anchored to "now" and never expired.
  drag._zoomView(0.25);
  check("(setup) the view is narrowed again", !!drag._view);
  drag._onDialogClose();
  check("closing the dialog discards the pan/zoom view", drag._view === null);
  // Reopen directly: the drag above armed the one-shot click suppression,
  // which would silently spend a simulated card click.
  drag._openExpanded();
  // Narrow again: the reset-button checks below need a zoomed card.
  drag._zoomView(0.25);

  // The hint's button is the escape hatch: one press, whole plan back.
  drag._render();
  const resetBtn = drag.shadowRoot.querySelector(".wi-viewreset");
  check("the hint carries a reset button", !!resetBtn);
  if (resetBtn) {
    fire(resetBtn, "click", { stopPropagation() {} });
    check("pressing it clears the zoom", drag._view === null);
    const dump2 = collect(drag.shadowRoot).join("\n");
    check("and the hint disappears with it", !/class="wi-viewlimit"/.test(dump2));
  }
}

// ---------------------------------------------------------------------------
// Nothing painted over the lanes may eat pointer events (field report,
// Safari: hover, drags and right-click add all dead wherever a filled
// series body covered the lane strip — the series are painted after the
// lanes, and SVG fills capture events by default). The stub fires events
// with pre-built targets and does no real hit-testing, so this is pinned
// at the markup level: every chart-body overlay must declare itself inert.
// ---------------------------------------------------------------------------
{
  const dump = collect(drag.shadowRoot).join("\n");
  const seriesTags = dump.match(/<path class="series"[^>]*>/g) || [];
  check("the chart draws series paths at all", seriesTags.length > 0);
  check("every series path is pointer-inert",
    seriesTags.every((t) => t.includes('pointer-events="none"')),
    seriesTags.find((t) => !t.includes('pointer-events="none"')));
  for (const frag of [
    '<rect class="estimated" pointer-events="none"',
    '<line class="crosshair" pointer-events="none"',
  ]) {
    check(`source keeps ${frag.slice(1, 30)}… inert`, cardSrc.includes(frag));
  }
}

// ---------------------------------------------------------------------------
// Item 23: pan and zoom the plan window
// ---------------------------------------------------------------------------
{
  const zoom = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { what_if: true });
  zoom._hass = mkHass(zoom._hass.states);

  const windowOf = (card) => {
    const b = card._buildSeries();
    return { start: b.windowStart, end: b.windowEnd, span: b.windowEnd - b.windowStart };
  };

  const base = windowOf(zoom);
  check("an untouched card renders the default window",
    zoom._view === null && base.span > 0);

  // Zooming has to hold the pointed-at time still. Zooming about the centre
  // walks whatever the user is looking at off the edge, so repeated zooming
  // feels like it is fighting back.
  const anchor = base.start + base.span / 4;
  zoom._zoomView(1 / 4, anchor);
  const zoomed = windowOf(zoom);
  check("zooming in narrows the window", zoomed.span < base.span,
    `${zoomed.span} vs ${base.span}`);
  check("the anchored time stays inside the new window",
    anchor >= zoomed.start - 1 && anchor <= zoomed.end + 1,
    `anchor ${anchor} not within ${zoomed.start}..${zoomed.end}`);
  check("zooming never starts before the default window does",
    zoomed.start >= base.start - 1, `${zoomed.start} < ${base.start}`);

  // Forward-only: there is no recorded history to scroll back into, so the
  // window must not be draggable to before the start of the plan.
  zoom._panView(-base.span * 10);
  check("panning backwards stops at the start of the plan",
    windowOf(zoom).start >= base.start - 1);

  zoom._panView(base.span * 10);
  const far = windowOf(zoom);
  check("panning forwards stops at the end of the plan",
    far.end <= base.end + 1, `${far.end} > ${base.end}`);
  check("and panning never changes the span it is panning",
    Math.abs(far.span - zoomed.span) < 2, `${far.span} vs ${zoomed.span}`);

  // Zooming out is bounded by the plan, not by the configured plot width: past
  // the optimizer's horizon there is empty chart, not more plan.
  zoom._zoomView(1000, null);
  const out = windowOf(zoom);
  check("zooming out stops at the extent of the plan",
    out.span <= base.span + 1, `${out.span} > ${base.span}`);

  zoom._resetView();
  const back = windowOf(zoom);
  check("reset restores the default window exactly",
    zoom._view === null &&
    back.start === base.start && back.end === base.end);

  // The controls are the only route for touch and keyboard users; a gesture
  // nobody can perform is not an affordance.
  const dump = collect(zoom.shadowRoot).join("\n");
  check("the chart offers zoom controls",
    /class="vc-in"/.test(dump) && /class="vc-out"/.test(dump) &&
    /class="vc-reset"/.test(dump));
  check("reset is disabled while the view is already the default",
    /vc-reset[^>]*disabled/.test(dump));
}

// A drag that starts on a lane belongs to the slot editor. If panning stole it
// the slots would stop being draggable, which is the entire point of the lanes.
{
  const guard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { what_if: true });
  guard._hass = mkHass(guard._hass.states);
  guard._buildSeries();
  const before = guard._view;
  guard._onPanDown({
    stopPropagation(){}, clientX: 400,
    target: { dataset: { channel: "space" } },
    currentTarget: { getBoundingClientRect: () => ({ width: 900, left: 0 }) },
  });
  check("a pointerdown on a lane does not start a pan",
    guard._pan === null && guard._view === before);

  // A pan finishes with a click on the chart, and a click on the chart opens
  // the expanded view. Without suppression, every drag would pop the dialog.
  const svgRect = { getBoundingClientRect: () => ({ width: 900, left: 0 }) };
  guard._onPanDown({
    stopPropagation(){}, preventDefault(){}, clientX: 400,
    target: { dataset: {} }, currentTarget: svgRect,
  });
  check("a pointerdown on the background does start a pan", guard._pan !== null);
  const pan = guard._pan;
  pan.move({ clientX: 340 });
  pan.up();
  check("a drag suppresses the click that ends it", guard._suppressClick === true);
  guard._expanded = false;
  guard._onCardClick({});
  check("so the drag does not open the expanded view", guard._expanded === false);
  check("and the suppression is spent, not sticky", guard._suppressClick === false);
  guard._onCardClick({});
  check("a real click still opens the expanded view", guard._expanded === true);

  // A click with no movement is not a pan and must stay a click.
  const still = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { what_if: true });
  still._hass = mkHass(still._hass.states);
  still._buildSeries();
  still._onPanDown({
    stopPropagation(){}, preventDefault(){}, clientX: 400,
    target: { dataset: {} }, currentTarget: svgRect,
  });
  if (still._pan) still._pan.up();
  check("a click that never moved is not treated as a pan",
    still._suppressClick === false);
}

{
  // The browser synthesises a click after a slot drag's pointerup —
  // preventDefault on pointerdown suppresses compatibility mouse events but
  // not click — and on the INLINE chart that click bubbles to ha-card.
  // Without suppression, every drag ended by popping the expanded dialog open.
  const inline = build(slotStates, { what_if: true });
  inline._hass = mkHass(inline._hass.states);
  inline._buildSeries();
  const g = inline._geom;
  const svg = svgOf(inline);
  const runs = inline._draftRuns().dhw;
  const [lo] = inline._editBounds();
  const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
  check("the inline chart has an editable slot to drag", i >= 0 && !!g && !!svg);
  if (i >= 0) {
    const at = (t) => ({
      clientX:
        g.plotL +
        ((t - g.windowStart) / (g.windowEnd - g.windowStart)) * g.plotW,
      clientY: 0,
      target: { dataset: { channel: "dhw", index: String(i) } },
      stopPropagation() {},
      preventDefault() {},
    });
    fire(svg, "pointerdown", at(runs[i].start + 60000));
    fire(svg, "pointermove", at(runs[i].start + 60000 + HOUR));
    fire(svg, "pointerup", {});
    check("a slot drag suppresses the click that ends it",
      inline._suppressClick === true);
    inline._onCardClick({});
    check("so the drag does not open the expanded view",
      inline._expanded === false);
    inline._onCardClick({});
    check("a real click after the drag still opens it",
      inline._expanded === true);
  }
}

{
  // A re-render replaces the <dialog> element wholesale, so the font memo has
  // to be forgotten or _scaleDialogFont skips the write and the fresh
  // dialog's chrome collapses back to card size mid-session.
  const refont = build(slotStates, {});
  refont._openExpanded();
  // Measured at the stub's constant width, as a real browser would measure a
  // constant viewport: a changed width would re-trigger the write and mask
  // exactly the bug this guards against.
  const size = (card) => {
    const d = card.shadowRoot.querySelector("dialog");
    if (!d.style) d.style = {};
    card._scaleDialogFont();
    return d.style.fontSize;
  };
  const first = size(refont);
  check("the expanded dialog chrome is sized on open", !!first);
  refont._sig = null;
  refont._render();
  const second = size(refont);
  check("a re-render while the dialog is open re-applies its font",
    second === first, `first ${first}, after re-render ${second}`);
}

// --- Scenario: the setup page (item 33) ------------------------------------
{
  const TEMP = ["sensor", "number", "input_number"];
  const topo = {
    two_zone: true, dhw: true, valve_mode: "manual",
    buffer: { volume_l: 750, is_store: true, max_temp: 70 },
    wood: { present: true, volume_l: 500 },
    // v3.16.0: the coordinator publishes the active layout's drawn edges and
    // the card draws those, rather than hardcoding pipes that can drift from
    // the physics. This is what `describe_setup` sends for a single-tank
    // house with a throttling valve, two zones and a wood furnace.
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
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  states[DEFAULT_SPACE].attributes.setup_topology = topo;
  states["sensor.livingroom"] = {
    state: "21.3", attributes: { unit_of_measurement: "°C" } };
  states["sensor.tank"] = {
    state: "47.5", attributes: { unit_of_measurement: "°C" } };
  states["sensor.outside"] = { state: "unavailable", attributes: {} };
  const su = build(states);
  su._onCardClick({});
  const planPage = collect(su.shadowRoot).join("\n");
  check("the dialog offers plan and setup tabs",
    /dlg-tab[^>]*data-page="plan"/.test(planPage) &&
    /dlg-tab[^>]*data-page="setup"/.test(planPage));

  su._dialogPage = "setup";
  su._render();
  const setupPage = collect(su.shadowRoot).join("\n");
  check("the setup page draws the system", /setup-svg/.test(setupPage) &&
    /Buffer tank \(750 L\)/.test(setupPage) && /Wood furnace tank/.test(setupPage));
  check("live values are read straight from hass states",
    /21\.3 °C/.test(setupPage) && /47\.5 °C/.test(setupPage));
  check("an unavailable sensor says so instead of a stale number",
    /unavailable/.test(setupPage));
  // Labels longer than the row are trimmed with an ellipsis, so match the
  // prefix rather than the full name.
  check("empty slots are drawn empty, not omitted",
    /not configured/.test(setupPage) && /Lower floor te/.test(setupPage));
  // Issue #40: the drawn hydronics must match the model. The model computes
  // one t_mix and feeds both circuits from it in parallel, so with a valve
  // BOTH floor boxes hang off the mixing valve; the old drawing ran the
  // slab straight from the tank, which is a different (unmodelled) system.
  const edges = (html) =>
    (html.match(/data-edge="([^"]+)"/g) || []).map((m) => m.slice(11, -1));
  const drawn = edges(setupPage);
  check("with a valve, one shared flow feeds both floors",
    drawn.includes("mixing_valve>upper_zone") &&
    drawn.includes("mixing_valve>lower_zone") &&
    drawn.includes("buffer_tank>mixing_valve") &&
    !drawn.includes("buffer_tank>lower_zone"),
    `edges drawn: ${drawn.join(", ")}`);
  // v4.0.0 (#40 feedback, item 3): the wood chain is tank to tank; the
  // wood-side blending valve is no longer a box of its own.
  check("and the wood chain is drawn tank to tank from the published edges",
    drawn.includes("wood_tank>buffer_tank") &&
    !/Wood mixing valve/.test(setupPage),
    `edges drawn: ${drawn.join(", ")}`);
  // #40 feedback, item 2: the DHW tank used to float unconnected.
  check("the heat pump visibly feeds the hot water tank",
    drawn.includes("heat_pump>dhw_tank"),
    `edges drawn: ${drawn.join(", ")}`);
  // v4.3.0: each place is drawn as the equipment it is. The silhouette rides
  // its own contour path so the rect can stay the invisible geometry carrier
  // every older assertion (and the drag editor) reads.
  check("every place wears its own silhouette",
    ["heat_pump", "wood_tank", "buffer_tank", "dhw_tank", "mixing_valve",
      "upper_zone", "lower_zone", "outdoor"].every((p) =>
      new RegExp(`class="setup-contour kind-${p}"`).test(setupPage)),
    "a place without a contour is a box that lost its shape");
  check("no box goes without a contour",
    (setupPage.match(/class="setup-contour/g) || []).length >=
      (su._layoutBoxes || []).length,
    `${(setupPage.match(/class="setup-contour/g) || []).length} contours for `
    + `${(su._layoutBoxes || []).length} boxes`);
  check("the carrier rect is invisible, not gone",
    /\.setup-box \{ fill: none; stroke: none; \}/.test(cardSrc),
    "the rect is geometry for the tests and the editor; the contours are "
    + "the paint");
  // Outside air is unbounded: its contour is an open tray baseline, no Z,
  // while a tank's silhouette closes.
  {
    const outdoorG = setupPage.split("<g>")
      .find((g) => g.includes("kind-outdoor")) || "";
    const contourD = (seg, place) => {
      const m = new RegExp(
        `class="setup-contour kind-${place}"\\s+d="([^"]*)"`).exec(seg);
      return m ? m[1] : "";
    };
    check("outside air is drawn open, tanks are drawn closed",
      contourD(outdoorG, "outdoor") !== "" &&
      !/Z/.test(contourD(outdoorG, "outdoor")) &&
      /Z/.test(contourD(setupPage, "wood_tank")),
      "walls around the outdoors would claim a container that place is not");
  }
  // Endpoint dots and flow chevrons are ornament: none of them may carry
  // `data-edge`, or every scrape of the drawn topology inflates. Scoped to
  // the diagram's own svg -- the plan lanes elsewhere in the shadow root
  // legitimately use data-edge for their drag handles.
  {
    const svgOnly =
      (setupPage.match(/<svg class="setup-svg[\s\S]*?<\/svg>/) || [""])[0];
    check("pipe decorations never carry data-edge",
      (svgOnly.match(/data-edge=/g) || []).length === topo.edges.length &&
      (svgOnly.match(/<path class="setup-pipe/g) || []).length ===
        topo.edges.length,
      `${(svgOnly.match(/data-edge=/g) || []).length} data-edge and `
      + `${(svgOnly.match(/<path class="setup-pipe/g) || []).length} pipes `
      + `for ${topo.edges.length} edges`);
  }
  // Designer QA pass (v4.3.x): the silhouettes keep their ink apart.
  {
    const svgOnly =
      (setupPage.match(/<svg class="setup-svg[\s\S]*?<\/svg>/) || [""])[0];
    // The house ridge is a shallow r=30 knuckle. An `A 4 4` arc over the
    // 8-unit chord was a full semicircle whose apex sat above the bounding
    // box -- a pimple on every roof.
    const houseG = svgOnly.split("<g>")
      .find((g) => g.includes("kind-upper_zone")) || "";
    check("the house ridge arc is shallow and stays inside the box",
      /A 30 30 0 0 1/.test(houseG) && !/A 4 4 /.test(houseG),
      "chord 8 at r=4 renders a semicircle bulging above the roofline");
    // The same-column pipe into the mixing valve drops its flow chevron:
    // the apex would land on the valve's bowtie accent and merge ink. Every
    // other pipe keeps its chevron, so the count is exactly edges - 1.
    const pipeSegs = svgOnly.split('<path class="setup-pipe');
    const valveSeg = pipeSegs.find((s) =>
      s.includes('data-edge="buffer_tank>mixing_valve"')) || "";
    check("the pipe into the mixing valve carries no flow chevron",
      valveSeg !== "" && !/class="setup-flow"/.test(valveSeg) &&
      (svgOnly.match(/class="setup-flow"/g) || []).length ===
        topo.edges.length - 1,
      `${(svgOnly.match(/class="setup-flow"/g) || []).length} chevrons for `
      + `${topo.edges.length} edges`);
    // A row-less box (h = 32) draws no header divider -- it would separate
    // the title from nothing and graze the valve's bowtie -- while a box
    // with rows keeps it.
    const valveBoxG = svgOnly.split("<g>")
      .find((g) => g.includes("Mixing valve")) || "";
    const bufBoxG = svgOnly.split("<g>")
      .find((g) => g.includes("Buffer tank (750 L)")) || "";
    check("a row-less box draws no header divider",
      valveBoxG !== "" && !/setup-accent divider/.test(valveBoxG) &&
      /setup-accent divider/.test(bufBoxG),
      "a divider over an empty band underlines nothing");
  }
  {
    // A coordinator from before v4.0.0 still publishes the wood-valve hop
    // and a slot placed on it. The pipes anchor where the slot went — the
    // wood tank — so a stale payload degrades to the new drawing instead of
    // dropping its wood chain or losing the outlet sensor.
    const stale = JSON.parse(JSON.stringify(topo));
    stale.edges = [
      ["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"],
      ["mixing_valve", "upper_zone"],
      ["mixing_valve", "lower_zone"],
      ["wood_tank", "wood_valve"],
      ["wood_valve", "buffer_tank"],
    ];
    stale.slots = topo.slots.concat([
      { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
        place: "wood_valve", entity: null, domains: TEMP }]);
    const stStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    stStates[DEFAULT_SPACE].attributes.setup_topology = stale;
    const st = build(stStates);
    st._onCardClick({});
    st._dialogPage = "setup";
    st._render();
    const stPage = collect(st.shadowRoot).join("\n");
    const woodGroup = stPage.split("<g>")
      .find((g) => g.includes("Wood furnace tank")) || "";
    check("a stale wood-valve payload re-homes its slot onto the wood tank",
      !/Wood mixing valve/.test(stPage) &&
      /data-key="valve_outlet_temp_entity"/.test(woodGroup) &&
      edges(stPage).includes("wood_valve>buffer_tank"),
      "the removed box must not take the outlet sensor down with it");
  }
  {
    // An older coordinator publishes no `edges` at all. The card must fall
    // back to the drawing it has always made rather than showing a system
    // with no plumbing in it.
    const legacyTopo = JSON.parse(JSON.stringify(topo));
    delete legacyTopo.edges;
    const lgStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    lgStates[DEFAULT_SPACE].attributes.setup_topology = legacyTopo;
    const lg = build(lgStates);
    lg._onCardClick({});
    lg._dialogPage = "setup";
    lg._render();
    const lgDrawn = edges(collect(lg.shadowRoot).join("\n"));
    check("a coordinator that publishes no edges still gets the old drawing",
      ["hp-buffer", "buffer-valve", "valve-upper", "valve-lower",
        "wood-buffer", "hp-dhw"].every((e) =>
        lgDrawn.includes(e)) && !lgDrawn.some((e) => e.includes(">")),
      `edges drawn: ${lgDrawn.join(", ")}`);
  }
  // The caption is wrapped across rows (SVG text does not wrap itself), so
  // match its fragments rather than the whole sentence.
  check("the wood box admits the single-tank abstraction",
    /modelled as heat into the/.test(setupPage) &&
    /heat-pump tank/.test(setupPage));
  {
    // Issue #40, stage 5: with the two-tank model active the drawing is of
    // the real plumbing, not of the abstraction. One physical 4-way valve
    // that both stores feed and both floors are served from -- so no wood
    // valve, no wood tank pouring into the heat-pump tank, and no caption
    // claiming the wood heat is folded in, because it no longer is.
    const twoTank = JSON.parse(JSON.stringify(topo));
    twoTank.two_tank_modelled = true;
    twoTank.layout = "two_tank_4way";
    twoTank.valve_mode = "manual";
    // What `describe_setup` composes for `two_tank_4way`: both stores into
    // the one 4-way valve, and no wood chain at all.
    twoTank.edges = [
      ["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"],
      ["wood_tank", "mixing_valve"],
      ["mixing_valve", "upper_zone"],
      ["mixing_valve", "lower_zone"],
      ["heat_pump", "dhw_tank"],
    ];
    twoTank.slots.push(
      { key: "mixing_valve_target_entity", label: "Valve target",
        place: "mixing_valve", entity: null, domains: TEMP },
      // describe_setup moves this slot onto the mixing valve in the
      // two-tank layout: one device, one place.
      { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
        place: "mixing_valve", entity: null, domains: TEMP });
    const ttStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    ttStates[DEFAULT_SPACE].attributes.setup_topology = twoTank;
    const tt = build(ttStates);
    tt._onCardClick({});
    tt._dialogPage = "setup";
    tt._render();
    const ttPage = collect(tt.shadowRoot).join("\n");
    const ttDrawn = edges(ttPage);
    check("the two-tank drawing runs both stores into one 4-way valve",
      ["heat_pump>buffer_tank", "wood_tank>mixing_valve",
        "buffer_tank>mixing_valve", "mixing_valve>upper_zone",
        "mixing_valve>lower_zone"].every((e) => ttDrawn.includes(e)) &&
      !ttDrawn.includes("wood_valve>buffer_tank") &&
      !ttDrawn.includes("wood_tank>wood_valve") &&
      !ttDrawn.includes("buffer_tank>lower_zone"),
      `edges drawn: ${ttDrawn.join(", ")}`);
    check("and names the tanks by what fills them",
      /4-way mixing valve \(manual\)/.test(ttPage) &&
      /Heat pump tank \(750 L\)/.test(ttPage) &&
      !/Buffer tank \(750 L\)/.test(ttPage) &&
      !/Wood mixing valve/.test(ttPage),
      "with two modelled stores 'buffer tank' no longer says which one");
    check("and drops the single-tank caption, which is no longer true",
      !/modelled as heat into the/.test(ttPage),
      "the box is the physics now, so the abstraction note would lie");
    // Each box is its own <g>, so ask which box the row landed in rather
    // than whether the page mentions it anywhere.
    const valveGroup = ttPage.split("<g>")
      .find((g) => g.includes("4-way mixing valve (manual)")) || "";
    check("the valve outlet probe is drawn on the one valve that has it",
      /data-key="valve_outlet_temp_entity"/.test(valveGroup) &&
      /data-key="mixing_valve_target_entity"/.test(valveGroup),
      "the slot moved to the mixing valve place; drawing it anywhere else "
      + "would put a sensor on a device this system does not have");
    // The coil is off in this topo, so neither the pipe nor the caption may
    // appear. A drawing that shows plumbing the model does not run is the
    // failure this whole diagram exists to prevent.
    check("no coil in the drawing when the topology does not have one",
      !ttDrawn.includes("wood_tank>dhw_tank") &&
      !/refilled through/.test(ttPage),
      `edges drawn: ${ttDrawn.join(", ")}`);

    // v3.15.1: the same two-tank system, plus the DHW tank's cold-water inlet
    // running through a coil in the wood tank. That is a second, separate
    // path out of the wood tank -- mains water on its way in, not heating
    // water on its way to the house -- so it is its own pipe, and every pipe
    // the two-tank drawing already had survives.
    const coil = JSON.parse(JSON.stringify(twoTank));
    coil.dhw_wood_coil = true;
    coil.edges = twoTank.edges.concat([["wood_tank", "dhw_tank"]]);
    coil.slots.push(
      { key: "dhw_temp_entity", label: "Hot water temperature",
        place: "dhw_tank", entity: null, domains: TEMP });
    const coStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    coStates[DEFAULT_SPACE].attributes.setup_topology = coil;
    const co = build(coStates);
    co._onCardClick({});
    co._dialogPage = "setup";
    co._render();
    const coPage = collect(co.shadowRoot).join("\n");
    const coDrawn = edges(coPage);
    check("the coil is drawn as its own pipe, wood tank to hot water tank",
      coDrawn.includes("wood_tank>dhw_tank") &&
      ["heat_pump>buffer_tank", "wood_tank>mixing_valve",
        "buffer_tank>mixing_valve", "mixing_valve>upper_zone",
        "mixing_valve>lower_zone"].every((e) => coDrawn.includes(e)),
      `edges drawn: ${coDrawn.join(", ")}`);
    check("and the electric pipe survives beside the coil (#40 item 2)",
      coDrawn.includes("heat_pump>dhw_tank"),
      "with the coil, the only pipe shown used to be the wood one — "
      + "implying a tank with no electric heat source at all");
    // 33 characters, which fits the box on a single row (wrapExtra breaks
    // above 34 -- the original wording wrapped with "coil" alone on row two).
    const dhwGroup = coPage.split("<g>")
      .find((g) => g.includes("Hot water tank")) || "";
    check("and the hot water box says where its refill water comes from",
      /refilled through a wood tank coil/.test(dhwGroup),
      "the caption belongs on the tank being preheated, not loose on the page");
    // v4.3.0: the coil is also drawn -- a helix on the wood tank's wall --
    // and only when the connection exists. The plain two-tank drawing above
    // has no coil, so it must have no helix either.
    check("the coil is drawn as a helix on the wood tank",
      /class="setup-coil"/.test(coPage) && !/class="setup-coil"/.test(ttPage),
      "the helix exists exactly when the wood>DHW connection does");
    {
      const wb = (co._layoutBoxes || []).find((b) => b.place === "wood_tank");
      const coilPipe = new RegExp(
        `data-edge="wood_tank>dhw_tank"\\s+d="M ${wb.x + wb.w + 13} ` +
        `${wb.y + 23}`);
      check("and the coil pipe departs from the helix, not the box wall",
        coilPipe.test(coPage),
        "a pipe from the box midpoint would leave the helix as ornament");
    }
  }
  {
    const noValve = JSON.parse(JSON.stringify(topo));
    noValve.valve_mode = "none";
    noValve.edges = [
      ["heat_pump", "buffer_tank"],
      ["buffer_tank", "upper_zone"],
      ["buffer_tank", "lower_zone"],
      ["wood_tank", "buffer_tank"],
      ["heat_pump", "dhw_tank"],
    ];
    const nvStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    nvStates[DEFAULT_SPACE].attributes.setup_topology = noValve;
    const nv = build(nvStates);
    nv._onCardClick({});
    nv._dialogPage = "setup";
    nv._render();
    const nvDrawn = edges(collect(nv.shadowRoot).join("\n"));
    check("without a valve the tank feeds both floors directly",
      nvDrawn.includes("buffer_tank>upper_zone") &&
      nvDrawn.includes("buffer_tank>lower_zone") &&
      !nvDrawn.some((e) => e.startsWith("mixing_valve>")),
      `edges drawn: ${nvDrawn.join(", ")}`);
  }
  // The hidden page must be genuinely unrendered, not display:none --
  // getBoundingClientRect on a hidden chart returns zeroes and
  // _timeAtClientX would compute garbage drag times rather than fail.
  check("the plan chart is genuinely unrendered on the setup page",
    !/chartwrap big/.test(setupPage) && !/class="whatif"/.test(setupPage));

  // A plan refresh must not yank the user off the page they are reading.
  su._sig = null;
  su._maybeRender(true);
  const afterRefresh = collect(su.shadowRoot).join("\n");
  check("the current page survives a plan refresh",
    su._dialogPage === "setup" && /setup-svg/.test(afterRefresh));

  su._dialogPage = "plan";
  su._render();
  const backToPlan = collect(su.shadowRoot).join("\n");
  check("switching back restores the chart and the what-if panel",
    /chartwrap big/.test(backToPlan) && !/class="setup-svg"/.test(backToPlan));

  // --- click-to-assign (item 32's second stage) ---------------------------
  su._dialogPage = "setup";
  su._render();
  const clickable = collect(su.shadowRoot).join("\n");
  check("every slot is a click target, not just the configured ones",
    (clickable.match(/class="setup-hit"/g) || []).length === topo.slots.length,
    `${(clickable.match(/class="setup-hit"/g) || []).length} hit targets for `
    + `${topo.slots.length} slots -- an empty slot is the one you most need `
    + `to click`);

  su._pickerKey = "lower_floor_temp_entity";
  su._render();
  const picking = collect(su.shadowRoot).join("\n");
  check("clicking a slot opens a picker for it",
    /class="setup-picker"/.test(picking) && /Lower floor temperature/.test(picking));
  check("the picker offers entities of the domains the slot accepts",
    /sensor\.livingroom/.test(picking) && /sensor\.tank/.test(picking));
  check("and offers clearing the slot",
    /\(not configured\)/.test(picking));
  // The service validates domains too, but a picker that offers what the
  // service will refuse turns a wrong click into an error message instead of
  // an impossibility.
  su._pickerKey = "heat_pump_switch_entity";
  su._render();
  const switchPick = collect(su.shadowRoot).join("\n");
  check("a switch slot does not offer temperature sensors",
    !/sensor\.livingroom/.test(switchPick),
    "the picker is filtered by the same domain list the service enforces");

  su._pickerKey = "lower_floor_temp_entity";
  su._render();
  const calls = [];
  su._hass.callService = async (domain, service, data) => {
    calls.push([domain, service, data]);
  };
  const saveBtn = su.shadowRoot.querySelector(".sp-save");
  const select = su.shadowRoot.querySelector(".sp-select");
  if (select) select.value = "sensor.tank";
  if (saveBtn) await Promise.all(
    (saveBtn._listeners.click || []).map((f) => f({ stopPropagation() {} })));
  check("assigning calls the validated service, not a config write",
    calls.length === 1 && calls[0][0] === "heatpump_optimizer"
    && calls[0][1] === "assign_entity",
    JSON.stringify(calls));
  check("and sends the slot key and the chosen entity",
    calls.length === 1 && calls[0][2].key === "lower_floor_temp_entity"
    && calls[0][2].entity_id === "sensor.tank",
    JSON.stringify(calls[0] && calls[0][2]));
  check("the picker closes once the assignment is away",
    su._pickerKey === null);

  // A failed call must say so rather than looking like it worked.
  su._pickerKey = "lower_floor_temp_entity";
  su._render();
  su._hass.callService = async () => {
    throw new Error("Entity does not exist");
  };
  const saveBtn2 = su.shadowRoot.querySelector(".sp-save");
  if (saveBtn2) await Promise.all(
    (saveBtn2._listeners.click || []).map((f) => f({ stopPropagation() {} })));
  check("a rejected assignment is reported, not swallowed",
    /Could not assign/.test(su._setupNote || ""),
    `note was ${JSON.stringify(su._setupNote)}`);
  check("and the picker stays open so the choice can be corrected",
    su._pickerKey === "lower_floor_temp_entity");
}

// --- Scenario: the layout editor (v3.16.0, issue #40) ----------------------
//
// The editor's whole promise is that a drawing cannot claim physics the model
// does not run: every edit is matched against the catalog the coordinator
// published for THIS configuration, and only a key -- never a free-form graph
// -- is ever saved. These checks are about that promise, not about pixels.
{
  const TEMP = ["sensor", "number", "input_number"];
  // A two-zone house with a throttling valve and no wood tank: exactly the
  // configuration where `valve_upper_direct_slab` and `single_tank_valve` are
  // both storable, so an edit can legitimately move between them.
  const EDGES = {
    no_valve: [["heat_pump", "buffer_tank"], ["buffer_tank", "upper_zone"],
      ["buffer_tank", "lower_zone"]],
    single_tank_valve: [["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"], ["mixing_valve", "upper_zone"],
      ["mixing_valve", "lower_zone"]],
    two_tank_4way: [["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"], ["wood_tank", "mixing_valve"],
      ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"]],
    valve_upper_direct_slab: [["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"], ["mixing_valve", "upper_zone"],
      ["buffer_tank", "lower_zone"]],
    slab_shunt: [["heat_pump", "buffer_tank"],
      ["buffer_tank", "mixing_valve"], ["mixing_valve", "upper_zone"],
      ["buffer_tank", "slab_shunt"], ["slab_shunt", "lower_zone"]],
  };
  // `valid` is what `topology_layout_valid` answers for a throttling valve,
  // two zones and no wood-tank probe.
  const CATALOG = [
    { key: "no_valve", label: "No mixing valve", description: "",
      requirement: "no throttling mixing valve configured",
      selectable: true, valid: false, edges: EDGES.no_valve },
    { key: "single_tank_valve", label: "One tank behind a valve",
      description: "", requirement: "a throttling mixing valve",
      selectable: true, valid: true, edges: EDGES.single_tank_valve },
    { key: "two_tank_4way", label: "Two tanks, one 4-way valve",
      description: "",
      requirement: "a throttling valve, two zones and a wood-tank top probe",
      selectable: true, valid: false, edges: EDGES.two_tank_4way },
    { key: "valve_upper_direct_slab",
      label: "Valve on the radiators, slab fed direct", description: "",
      requirement: "a throttling valve, two zones, and no wood-tank probe",
      selectable: true, valid: true, edges: EDGES.valve_upper_direct_slab },
    { key: "slab_shunt", label: "Separate slab shunt", description: "",
      requirement: "not selectable: no model variant exists yet",
      selectable: false, valid: false, edges: EDGES.slab_shunt },
  ];
  const mkTopo = (over) => ({
    two_zone: true, dhw: false, valve_mode: "manual",
    layout: "valve_upper_direct_slab", two_tank_modelled: false,
    buffer: { volume_l: 500, is_store: true, max_temp: 65 },
    wood: { present: false, volume_l: 0 },
    edges: EDGES.valve_upper_direct_slab.map((e) => [e[0], e[1]]),
    catalog: CATALOG, positions: {},
    slots: [
      { key: "indoor_temp_entity", label: "Indoor temperature",
        place: "upper_zone", entity: "sensor.livingroom", domains: TEMP },
      { key: "lower_floor_temp_entity", label: "Lower floor temperature",
        place: "lower_zone", entity: null, domains: TEMP },
      { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
        place: "buffer_tank", entity: "sensor.tank", domains: TEMP },
      { key: "mixing_valve_target_entity", label: "Valve target",
        place: "mixing_valve", entity: null, domains: TEMP },
      { key: "outdoor_temp_entity", label: "Outdoor temperature",
        place: "outdoor", entity: "sensor.outside", domains: TEMP },
      { key: "heat_pump_switch_entity", label: "Heat pump switch",
        place: "heat_pump", entity: null,
        domains: ["switch", "input_boolean", "climate"] },
    ],
    ...(over || {}),
  });
  const mkEditor = (over) => {
    const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    states[DEFAULT_SPACE].attributes.setup_topology = mkTopo(over);
    states["sensor.livingroom"] = {
      state: "21.3", attributes: { unit_of_measurement: "°C" } };
    states["sensor.tank"] = {
      state: "47.5", attributes: { unit_of_measurement: "°C" } };
    states["sensor.outside"] = { state: "3.0", attributes: {} };
    const c = build(states);
    c._onCardClick({});
    c._dialogPage = "setup";
    c._render();
    return c;
  };
  // The diagram as it stands now. An edit refreshes the canvas in place, so
  // the shadow root's own innerHTML is a snapshot from before it -- reading
  // the whole dump would happily assert against the drawing being replaced.
  const pageHtml = (card) => {
    const canvas = card.shadowRoot.querySelector(".setup-canvas");
    return (canvas && canvas.innerHTML) || collect(card.shadowRoot).join("\n");
  };
  const edgesOf = (card) =>
    (pageHtml(card).match(/data-edge="([^"]+)"/g) || [])
      .map((m) => m.slice(11, -1));
  const clickOn = (el) => (el._listeners.click || [])
    .map((f) => f({ stopPropagation() {}, preventDefault() {} }));
  // The DOM stub measures every element 900 px wide and the diagram's viewBox
  // is 720 units, so a viewBox unit is 1.25 px. Aiming at real box geometry
  // (from `_layoutBoxes`) rather than at guessed coordinates is what makes
  // these drags mean anything.
  const pxOf = (u) => (u * 900) / 720;
  const boxAt = (card, place) =>
    (card._layoutBoxes || []).find((b) => b.place === place);
  const centre = (card, place) => {
    const b = boxAt(card, place);
    return { x: b.x + b.w / 2, y: b.y + b.h / 2 };
  };
  const ev = (pt, target) => ({
    clientX: pxOf(pt.x), clientY: pxOf(pt.y), target: target || {},
    stopPropagation() {}, preventDefault() {},
  });
  // Drag from one box's port and drop on another, the way a pointer does it.
  const connect = (card, from, to) => {
    const src = centre(card, from);
    const dst = centre(card, to);
    card._onLayoutDown(ev(src, { dataset: { place: from, port: "right" } }));
    card._onLayoutMove(ev({ x: (src.x + dst.x) / 2, y: (src.y + dst.y) / 2 }));
    card._onLayoutUp(ev(dst));
  };

  {
    const c = mkEditor();
    const dump0 = collect(c.shadowRoot).join("\n");
    check("the setup page offers an Edit layout toggle",
      /class="layout-edit-toggle[^"]*"/.test(dump0) &&
      !/class="layout-port"/.test(dump0),
      "and draws no drag handles until it is pressed");
    const toggle = c.shadowRoot.querySelector(".layout-edit-toggle");
    clickOn(toggle);
    const dump = pageHtml(c);
    check("the editor draws a port on every box edge",
      (dump.match(/class="layout-port"/g) || []).length ===
        (c._layoutBoxes || []).length * 4,
      `${(dump.match(/class="layout-port"/g) || []).length} ports for `
      + `${(c._layoutBoxes || []).length} boxes`);
    // v4.3.0: the pipe ornament (endpoint dots, flow chevrons) is styled
    // away while editing -- it would sit right on the widened pipes that
    // are the editor's click targets. The stub computes no styles, so what
    // can be pinned is that the rule exists and is scoped as designed.
    check("pipe ornament is suppressed while the layout is being edited",
      /\.setup-svg\.editing \.setup-pipe-dot/.test(cardSrc) &&
      /\.setup-svg\.editing \.setup-flow \{ display: none; \}/.test(cardSrc),
      "dots and chevrons under the pointer would cover the editor's "
      + "click targets");
    const save = c.shadowRoot.querySelector(".layout-save");
    check("Save is offered but disabled until something is drawn",
      !!save && !!save.disabled,
      "an untouched editor would otherwise offer to write what is already "
      + "configured");
    check("and the editor says which layout is on screen",
      /Valve on the radiators, slab fed direct/
        .test(collect(c.shadowRoot).join("\n")),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
    // Editing takes the diagram over; a picker opening on top of a drag is
    // the interaction that made the whole page feel broken.
    const hit = c.shadowRoot.querySelector(".setup-hit");
    if (hit) (hit._listeners.click || []).forEach((f) =>
      f({ stopPropagation() {}, currentTarget: hit }));
    check("click-to-assign is off while the layout is being edited",
      !c._pickerKey);
  }

  {
    // The edit this feature exists for: the slab is not fed straight from the
    // tank after all, it hangs off the valve like the radiators. That is
    // exactly `single_tank_valve`, and the editor has to recognise it.
    const c = mkEditor();
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    c._onLayoutClick({ target: { dataset: { edge: "buffer_tank>lower_zone" } },
      stopPropagation() {} });
    check("clicking a pipe while editing removes it",
      !edgesOf(c).includes("buffer_tank>lower_zone"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
    check("and a drawing that is no layout is rejected, with a reason",
      !c._layoutEdit.match &&
      /No supported layout matches/.test(c._layoutEdit.verdict) &&
      /Lower floor/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
    connect(c, "mixing_valve", "lower_zone");
    check("dragging a port onto another box proposes that connection",
      edgesOf(c).includes("mixing_valve>lower_zone"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
    check("the finished drawing snaps to the layout it equals",
      !!c._layoutEdit.match &&
      c._layoutEdit.match.key === "single_tank_valve",
      `matched ${JSON.stringify(c._layoutEdit.match)}`);
    const dump = pageHtml(c);
    check("a matched layout is highlighted and Save is enabled",
      /setup-pipe layout-match/.test(dump) &&
      !c.shadowRoot.querySelector(".layout-save").disabled &&
      /One tank behind a valve/.test(c._layoutEdit.verdict));

    // (4) Only the key travels. A free-form graph is never stored, which is
    // what keeps the model from being asked to run physics nobody wrote.
    const calls = [];
    c._hass.callService = async (domain, service, data) => {
      calls.push([domain, service, data]);
    };
    await Promise.all(clickOn(c.shadowRoot.querySelector(".layout-save")));
    check("saving calls apply_topology with the matched key and positions",
      calls.length === 1 && calls[0][0] === "heatpump_optimizer" &&
      calls[0][1] === "apply_topology" &&
      calls[0][2].layout === "single_tank_valve" &&
      calls[0][2].positions && typeof calls[0][2].positions === "object" &&
      !("edges" in calls[0][2]),
      JSON.stringify(calls));
    check("and the editor closes once the write is away",
      c._layoutEdit === null && /Saved/.test(c._setupNote || ""),
      `note was ${JSON.stringify(c._setupNote)}`);
  }

  {
    // A rejected write keeps the drawing: it is the user's work, and losing
    // it is not a way to say no.
    const c = mkEditor();
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    c._onLayoutClick({ target: { dataset: { edge: "buffer_tank>lower_zone" } },
      stopPropagation() {} });
    connect(c, "mixing_valve", "lower_zone");
    c._hass.callService = async () => {
      throw new Error("that layout needs a wood-tank top probe");
    };
    await Promise.all(clickOn(c.shadowRoot.querySelector(".layout-save")));
    check("a rejected layout write is reported, not swallowed",
      /Could not save the layout/.test(c._setupNote || "") &&
      /wood-tank top probe/.test(c._setupNote || ""),
      `note was ${JSON.stringify(c._setupNote)}`);
    check("and the editor stays open with the drawing intact",
      c._layoutEditing() &&
      c._layoutEdit.edges.some((e) => e[1] === "lower_zone" &&
        e[0] === "mixing_valve"));
  }

  {
    // (3) An edit that is no layout at all: drawn, but drawn as rejected.
    const c = mkEditor();
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    connect(c, "heat_pump", "upper_zone");
    const dump = pageHtml(c);
    check("an unsupported drawing names the nearest layout and what differs",
      !c._layoutEdit.match &&
      /No supported layout matches/.test(c._layoutEdit.verdict) &&
      /Closest: Valve on the radiators, slab fed direct/
        .test(c._layoutEdit.verdict) &&
      /Heat pump → Upper floor/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
    check("the offending pipe is drawn as rejected, and Save stays disabled",
      /setup-pipe invalid" data-edge="heat_pump>upper_zone"/.test(dump) &&
      !!c.shadowRoot.querySelector(".layout-save").disabled,
      `edges drawn: ${edgesOf(c).join(", ")}`);
    const verdictEl = c.shadowRoot.querySelector(".layout-verdict");
    check("and the page says so, not just the console",
      !!verdictEl && /No supported layout matches/.test(verdictEl.textContent));

    // A drawing that IS a known layout this configuration cannot run gets the
    // requirement instead: nothing is mis-drawn, the house is just not that.
    c._layoutEdit.edges = EDGES.two_tank_4way.map((e) => [e[0], e[1]]);
    c._layoutEvaluate();
    check("a layout the configuration cannot run explains what it needs",
      !c._layoutEdit.match &&
      /Two tanks, one 4-way valve/.test(c._layoutEdit.verdict) &&
      /wood-tank top probe/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
    c._layoutEdit.edges = EDGES.slab_shunt.map((e) => [e[0], e[1]]);
    c._layoutEvaluate();
    check("and a known-but-unmodelled layout says it is not selectable",
      !c._layoutEdit.match &&
      /Separate slab shunt/.test(c._layoutEdit.verdict) &&
      /no model variant exists yet/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
  }

  {
    // #40 feedback, item 5: a catalog from before the `requirement` field
    // existed must not render "needs undefined" — the message shown at the
    // exact moment the user needs to know what to configure.
    const bare = CATALOG.map((e) => {
      const copy = { ...e };
      delete copy.requirement;
      return copy;
    });
    const c = mkEditor({ catalog: bare });
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    c._layoutEdit.edges = EDGES.two_tank_4way.map((e) => [e[0], e[1]]);
    c._layoutEvaluate();
    check("a catalog without requirement text degrades, never 'undefined'",
      !c._layoutEdit.match &&
      /Two tanks, one 4-way valve/.test(c._layoutEdit.verdict) &&
      !/undefined/.test(c._layoutEdit.verdict) &&
      /cannot store/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
    c._layoutEdit.edges = EDGES.slab_shunt.map((e) => [e[0], e[1]]);
    c._layoutEvaluate();
    check("and the unmodelled layout degrades the same way",
      !/undefined/.test(c._layoutEdit.verdict) &&
      /not modelled yet/.test(c._layoutEdit.verdict),
      `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
  }

  {
    // (5) The recorded trap: `_maybeRender` rebuilds the shadow root on the
    // coordinator's schedule, and an editor living in local state would be
    // wiped out mid-drawing every few minutes.
    const c = mkEditor();
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    c._onLayoutClick({ target: { dataset: { edge: "buffer_tank>lower_zone" } },
      stopPropagation() {} });
    connect(c, "mixing_valve", "lower_zone");
    c._sig = null;
    c._maybeRender(true);
    const dump = pageHtml(c);
    check("the layout editor survives a plan refresh",
      c._layoutEditing() && /class="layout-port"/.test(dump) &&
      edgesOf(c).includes("mixing_valve>lower_zone") &&
      !edgesOf(c).includes("buffer_tank>lower_zone"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
    check("and so does the match it had made",
      !!c._layoutEdit.match &&
      c._layoutEdit.match.key === "single_tank_valve" &&
      !c.shadowRoot.querySelector(".layout-save").disabled);
    // Cancel discards: nothing was written, so the working set must not
    // outlive the editor.
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    check("closing the editor discards the drawing",
      c._layoutEdit === null &&
      edgesOf(c).includes("buffer_tank>lower_zone"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
  }

  {
    // (6) Cosmetic positions come from the coordinator and move a box; the
    // drawing grows to fit rather than clipping it.
    const plain = mkEditor();
    const plainBox = boxAt(plain, "heat_pump");
    const moved = mkEditor({ positions: { heat_pump: [430, 360] } });
    const movedBox = boxAt(moved, "heat_pump");
    check("a published position moves the box it names",
      movedBox.x === 430 && movedBox.y === 360 &&
      (plainBox.x !== 430 || plainBox.y !== 360),
      `default ${plainBox.x},${plainBox.y} -> ${movedBox.x},${movedBox.y}`);
    const dump = pageHtml(moved);
    check("and the drawing is written at that position",
      /<rect class="setup-box" x="430" y="360"/.test(dump));
    const height = (html) => {
      const m = /viewBox="0 0 720 (\d+)"/.exec(html);
      return m ? Number(m[1]) : 0;
    };
    check("the diagram grows so the moved box is not clipped",
      height(dump) >= 360 + movedBox.h,
      `viewBox height ${height(dump)} for a box ending at `
      + `${360 + movedBox.h}`);
    // Out of the viewBox is out of reach: a position that would park a box
    // off the page is clamped back onto it.
    const wild = mkEditor({ positions: { heat_pump: [9999, -50] } });
    const wildBox = boxAt(wild, "heat_pump");
    check("an impossible position is clamped onto the drawing",
      wildBox.x === 720 - wildBox.w && wildBox.y === 0,
      `clamped to ${wildBox.x},${wildBox.y}`);

    // Dragging a box records a position and nothing else: a box that moved
    // must not change which layout the drawing is.
    const c = mkEditor();
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    const before = c._layoutEdit.edges.map((e) => `${e[0]}>${e[1]}`).join();
    const from = centre(c, "buffer_tank");
    c._onLayoutDown(ev(from, { dataset: {} }));
    c._onLayoutMove(ev({ x: from.x + 30, y: from.y + 40 }));
    c._onLayoutUp(ev({ x: from.x + 30, y: from.y + 40 }));
    const at = c._layoutEdit.positions.buffer_tank;
    check("dragging a box records its position and leaves the pipes alone",
      Array.isArray(at) && at.length === 2 &&
      c._layoutEdit.edges.map((e) => `${e[0]}>${e[1]}`).join() === before,
      `position ${JSON.stringify(at)}`);
    check("and a moved box is still the layout it was, now saveable",
      !!c._layoutEdit.match &&
      c._layoutEdit.match.key === "valve_upper_direct_slab" &&
      !c.shadowRoot.querySelector(".layout-save").disabled);
    // The click a drag owes is swallowed by whatever it ended over -- a slot
    // row stops it before the diagram sees it -- so the next gesture must
    // clear the debt rather than spend it on the user's next real click.
    c._onLayoutDown(ev({ x: 4, y: 4 }, { dataset: {} }));
    c._onLayoutClick({
      target: { dataset: { edge: "buffer_tank>lower_zone" } },
      stopPropagation() {} });
    check("a click after a drag is not silently eaten",
      !edgesOf(c).includes("buffer_tank>lower_zone"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
  }

  {
    // v4.3.0: the coil helix follows the drawing while the editor is open.
    // The wood>DHW pipe is what claims a coil, so removing it must take the
    // helix off the tank live, and re-drawing it must bring it back --
    // otherwise the editor shows a heat exchanger the drawing just deleted.
    const c = mkEditor({
      dhw: true, dhw_wood_coil: true,
      wood: { present: true, volume_l: 300 },
      edges: EDGES.valve_upper_direct_slab
        .concat([["wood_tank", "dhw_tank"]]).map((e) => [e[0], e[1]]),
    });
    check("the coil helix hangs on the wood tank",
      /class="setup-coil"/.test(pageHtml(c)),
      "the drawn wood>DHW edge is the coil's existence condition");
    clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
    c._layoutRemoveEdge("wood_tank>dhw_tank");
    check("removing the wood>DHW pipe removes the helix with it",
      !/class="setup-coil"/.test(pageHtml(c)),
      `edges drawn: ${edgesOf(c).join(", ")}`);
    connect(c, "wood_tank", "dhw_tank");
    check("and drawing the pipe again brings the helix back",
      /class="setup-coil"/.test(pageHtml(c)) &&
      edgesOf(c).includes("wood_tank>dhw_tank"),
      `edges drawn: ${edgesOf(c).join(", ")}`);
  }

  // --- Undo: back to the layout in force, without leaving the editor ------
  //
  // The owner's ask: a rearrangement that turned out wrong should be
  // undoable in place. Cancel already throws the drawing away, but it closes
  // the editor too, so starting over meant reopening it. Undo restores the
  // layout the editor opened on -- pipes AND box positions -- and stays.
  {
    const undoBtn = (card) => card.shadowRoot.querySelector(".layout-undo");
    // A native <button> is activated by Enter and Space by the browser
    // itself, which synthesises a click on it; a <div role="button"> is not.
    // So the keyboard question is answered by what the control IS, plus the
    // click path actually running -- which is what those keys deliver.
    const pressKey = (el, key) => {
      if (!el || el.tagName !== "BUTTON" || el.disabled) return [];
      if (key !== "Enter" && key !== " ") return [];
      return clickOn(el);
    };
    const posOf = (card) => JSON.stringify(card._layoutEdit.positions);
    const edgeNames = (card) =>
      card._layoutEdit.edges.map((e) => `${e[0]}>${e[1]}`).join();
    const PUBLISHED = EDGES.valve_upper_direct_slab
      .map((e) => `${e[0]}>${e[1]}`).join();

    {
      const c = mkEditor();
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      check("Undo is offered but disabled on a freshly opened editor",
        !!undoBtn(c) && !!undoBtn(c).disabled,
        "an untouched drawing already IS the layout in use, so there is "
        + "nothing to take back");
      check("and it says what it does, for a screen reader and on hover",
        /class="layout-undo"[\s\S]*?aria-label="[^"]*layout in use/
          .test(collect(c.shadowRoot).join("\n")) &&
        /class="layout-undo"[\s\S]*?title="[^"]*layout in use/
          .test(collect(c.shadowRoot).join("\n")));
      check("the Undo label goes through the translation layer, both ways",
        /"setup\.undo_layout": "Undo"/.test(cardSrc) &&
        /"setup\.undo_layout": "Ångra"/.test(cardSrc) &&
        (cardSrc.match(/"setup\.undo_layout_aria":/g) || []).length === 2,
        "a hard-coded English string is a string the Swedish card keeps");

      // One drag and one new pipe: both halves of the working set moved.
      const from = centre(c, "buffer_tank");
      c._onLayoutDown(ev(from, { dataset: {} }));
      c._onLayoutMove(ev({ x: from.x + 30, y: from.y + 40 }));
      c._onLayoutUp(ev({ x: from.x + 30, y: from.y + 40 }));
      connect(c, "heat_pump", "upper_zone");
      check("Undo lights up as soon as something is changed",
        !undoBtn(c).disabled && c._layoutEdit.dirty &&
        posOf(c) !== "{}" && edgeNames(c) !== PUBLISHED,
        `edges ${edgeNames(c)}, positions ${posOf(c)}`);

      clickOn(undoBtn(c));
      check("Undo restores the pipes and the box positions it opened with",
        edgeNames(c) === PUBLISHED && posOf(c) === "{}",
        `edges ${edgeNames(c)}, positions ${posOf(c)}`);
      check("and re-derives the verdict for the restored drawing",
        !!c._layoutEdit.match &&
        c._layoutEdit.match.key === "valve_upper_direct_slab" &&
        /Valve on the radiators, slab fed direct/
          .test(c._layoutEdit.verdict) &&
        /Valve on the radiators, slab fed direct/.test(
          (c.shadowRoot.querySelector(".layout-verdict") || {}).textContent
          || ""),
        `verdict was ${JSON.stringify(c._layoutEdit.verdict)}`);
      check("the editor stays open, unlike Cancel",
        c._layoutEditing() && /class="layout-port"/.test(pageHtml(c)),
        "Undo is the way to start over without reopening the editor");
      check("and Undo goes dark again, with nothing left to take back",
        !c._layoutEdit.dirty && !!undoBtn(c).disabled &&
        !!c.shadowRoot.querySelector(".layout-save").disabled,
        "an editor back at its starting point has nothing to save either");
      check("no drag survives the restore",
        c._layoutEdit.drag === null && !c._layoutEdit.suppressClick,
        "a pointerup still owed would land an edge against a drawing that "
        + "no longer exists");

      // The baseline is a deep copy, so touching the working set cannot
      // reach into the layout Undo owes on the NEXT press.
      c._layoutEdit.positions.buffer_tank = [1, 2];
      c._layoutEdit.edges.push(["heat_pump", "upper_zone"]);
      check("the baseline is a copy the working set cannot corrupt",
        JSON.stringify(c._layoutEdit.baseline.positions) === "{}" &&
        c._layoutEdit.baseline.edges.map((e) => `${e[0]}>${e[1]}`).join()
          === PUBLISHED,
        JSON.stringify(c._layoutEdit.baseline));
    }

    {
      // Only a drag: the positions half must come back on its own, and it
      // has to come back to the PUBLISHED position, not to the origin.
      const c = mkEditor({ positions: { heat_pump: [430, 360] } });
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      const from = centre(c, "heat_pump");
      c._onLayoutDown(ev(from, { dataset: {} }));
      c._onLayoutMove(ev({ x: from.x + 40, y: from.y + 20 }));
      c._onLayoutUp(ev({ x: from.x + 40, y: from.y + 20 }));
      const moved = JSON.stringify(c._layoutEdit.positions.heat_pump);
      clickOn(undoBtn(c));
      check("Undo after a drag alone puts the box back where it was",
        JSON.stringify(c._layoutEdit.positions.heat_pump) === "[430,360]" &&
        moved !== "[430,360]" && boxAt(c, "heat_pump").x === 430 &&
        boxAt(c, "heat_pump").y === 360,
        `moved to ${moved}, restored to `
        + JSON.stringify(c._layoutEdit.positions.heat_pump));
      check("and the pipes it never touched are still the published ones",
        edgeNames(c) === PUBLISHED, `edges ${edgeNames(c)}`);
    }

    {
      // Only an edge change: the pipes half must come back on its own.
      const c = mkEditor();
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      c._onLayoutClick({
        target: { dataset: { edge: "buffer_tank>lower_zone" } },
        stopPropagation() {} });
      connect(c, "mixing_valve", "lower_zone");
      check("a rearranged drawing is a different layout before Undo",
        c._layoutEdit.match.key === "single_tank_valve");
      clickOn(undoBtn(c));
      check("Undo after pipe edits alone restores the published pipe set",
        edgeNames(c) === PUBLISHED &&
        edgesOf(c).includes("buffer_tank>lower_zone") &&
        !edgesOf(c).includes("mixing_valve>lower_zone"),
        `edges drawn: ${edgesOf(c).join(", ")}`);

      // Nothing stale left behind: the editor still works exactly as it did
      // before the Undo, all the way through a real write.
      c._onLayoutClick({
        target: { dataset: { edge: "buffer_tank>lower_zone" } },
        stopPropagation() {} });
      connect(c, "mixing_valve", "lower_zone");
      const calls = [];
      c._hass.callService = async (domain, service, data) => {
        calls.push([domain, service, data]);
      };
      await Promise.all(clickOn(c.shadowRoot.querySelector(".layout-save")));
      check("Save still works normally after an Undo",
        calls.length === 1 && calls[0][1] === "apply_topology" &&
        calls[0][2].layout === "single_tank_valve" && c._layoutEdit === null,
        JSON.stringify(calls));
    }

    {
      // Keyboard parity with the buttons beside it.
      const c = mkEditor();
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      check("a disabled Undo does nothing on Enter",
        pressKey(undoBtn(c), "Enter").length === 0 &&
        undoBtn(c).tagName === "BUTTON" &&
        undoBtn(c).getAttribute("type") === "button" &&
        !/class="layout-undo"[^>]*tabindex/.test(collect(c.shadowRoot).join("")),
        "a real button is in the tab order and activated by the browser; "
        + "nothing here may take it back out");
      connect(c, "heat_pump", "upper_zone");
      pressKey(undoBtn(c), "Enter");
      check("Enter on Undo restores the layout, from the keyboard alone",
        edgeNames(c) === PUBLISHED && c._layoutEditing());
      connect(c, "heat_pump", "upper_zone");
      pressKey(undoBtn(c), " ");
      check("and so does Space",
        edgeNames(c) === PUBLISHED && c._layoutEditing());
      check("the bar's buttons ring themselves with :focus-visible, no more",
        /\.layout-bar button:focus-visible \{\s*outline: 2px solid/
          .test(cardSrc),
        "the shared rule covers Undo; an SVG-style outline is what clipped "
        + "the setup rows' ring");
    }

    {
      // The path Undo must NOT have changed: Cancel still closes, and still
      // leaves the published layout on screen.
      const c = mkEditor();
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      connect(c, "heat_pump", "upper_zone");
      clickOn(undoBtn(c));
      clickOn(c.shadowRoot.querySelector(".layout-edit-toggle"));
      check("Cancel still closes the editor, Undo or no Undo",
        c._layoutEdit === null && !c._layoutEditing() &&
        !/class="layout-port"/.test(pageHtml(c)) &&
        edgesOf(c).includes("buffer_tank>lower_zone"),
        `edges drawn: ${edgesOf(c).join(", ")}`);
    }
  }
}

// --- Scenario: phone-width usability (#40 feedback, item 1) -----------------
//
// Style rules, asserted on the source: the DOM stub computes no layout, so
// what CAN be pinned is that the rules exist and are scoped as designed.
{
  check("only the chart claims raw touch input",
    /\.chartwrap svg \{ touch-action: none; \}/.test(cardSrc) &&
    !/^\s*svg \{[^}]*touch-action/m.test(cardSrc),
    "a blanket svg { touch-action: none } swallowed touch on the setup "
    + "diagram, which on a phone fills the dialog — the page could not be "
    + "scrolled at all");
  check("the editor still claims the diagram while a drag must move a box",
    /\.setup-svg\.editing \{ touch-action: none; \}/.test(cardSrc));
  const phone = (cardSrc.match(/@media \(max-width: 600px\) \{[\s\S]*?\n {8}\}/g) || [])
    .join("\n");
  check("the dialog header may wrap at phone width, keeping the tabs reachable",
    /\.dlg-head \{ flex-wrap: wrap/.test(phone),
    "without wrapping, the title pushes the Plan/Setup tabs out of the "
    + "header on narrow screens");
  check("the setup diagram scrolls sideways at phone width instead of shrinking",
    /\.setup-canvas \{ overflow-x: auto/.test(phone) &&
    /\.setup-canvas svg \{ min-width/.test(phone),
    "slot rows scaled to a 380px dialog are too small to read or tap");
}

// --- Scenario: shared-step honesty (T3b, user report on v3.16.0) -----------
// The optimizer plans space + hot water in the same quarter hour as a
// time-share (their sum stays under nameplate). Two full-height bars with
// nothing said implied double-booking; the chart must mark shared spans
// and say what they are.
{
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  const spFc = clone(plan.space_plan.forecast);
  const dwFc = clone(plan.dhw_plan.forecast);
  // Doctor three consecutive steps into a guaranteed overlap — placed
  // deep enough into the horizon to sit inside the default view window,
  // which clips the first hours.
  for (const i of [40, 41, 42]) {
    if (spFc[i]) spFc[i].space_power = 2.0;
    if (dwFc[i]) dwFc[i].dhw_power = 3.0;
  }
  states[DEFAULT_SPACE].attributes.forecast = spFc;
  states[DEFAULT_DHW].attributes.forecast = dwFc;
  const sh = build(states);
  const shDump = collect(sh.shadowRoot).join("\n");
  check("shared quarter hours are marked with a hatched band",
    /shared-band/.test(shDump) && /hpoShared/.test(shDump));
  check("the band explains itself: time-sharing, not double-booking",
    /alternates circuits/.test(shDump) && /not double-booking/.test(shDump));

  // Control: with hot water flat off there is nothing to mark.
  const off = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  const dwOff = clone(plan.dhw_plan.forecast);
  for (const p of dwOff) p.dhw_power = 0.0;
  off[DEFAULT_DHW].attributes.forecast = dwOff;
  const shOff = build(off);
  check("no overlap, no band",
    !/shared-band/.test(collect(shOff.shadowRoot).join("\n")));

  // Hiding one channel hides its half of the story: no orphan bands.
  const hid = build(states);
  hid._hidden = { dhw_slots: true };
  hid._render();
  check("a hidden channel takes its shared bands with it",
    !/shared-band/.test(collect(hid.shadowRoot).join("\n")));

  // The hover tooltip's shared line, driven directly: each series snaps to
  // its own nearest point, so the guard must demand the SAME timestamp —
  // otherwise a stale sensor whose horizon ends early pairs points hours
  // apart and the tooltip claims a sharing the band refuses to draw.
  const T0 = 1700000000000;
  const row = (field, value, t) => ({ field, value, t });
  const shared = sh._sharedTooltipHtml([
    row("space_power", 1.2, T0), row("dhw_power", 4.8, T0),
  ]);
  check("the tooltip explains a genuinely shared step, with the sum",
    /Shared step/.test(shared) && /alternates/.test(shared) && /6/.test(shared));
  check("nearest points from different timestamps are never called shared",
    sh._sharedTooltipHtml([
      row("space_power", 1.2, T0), row("dhw_power", 4.8, T0 + 3600000),
    ]) === "");
  check("one idle channel means no shared line",
    sh._sharedTooltipHtml([
      row("space_power", 1.2, T0), row("dhw_power", 0.0, T0),
    ]) === "" && sh._sharedTooltipHtml([row("space_power", 1.2, T0)]) === "");
}

// --- Scenario: the Outside box and the plan's real irradiance (T3b) --------
// With no radiation sensor configured the plan still runs on Open-Meteo or
// weather-derived irradiance every cycle; the setup diagram used to call
// that "not configured".
{
  const TEMP = ["sensor", "number", "input_number"];
  const mkTopo = () => ({
    two_zone: false, dhw: false, valve_mode: "none",
    buffer: { volume_l: 200, is_store: false, max_temp: 60 },
    wood: { present: false },
    edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "upper_zone"]],
    slots: [
      { key: "solar_radiation_entity", label: "Solar radiation",
        place: "outdoor", entity: null, domains: TEMP },
      { key: "outdoor_temp_entity", label: "Outdoor temperature",
        place: "outdoor", entity: null, domains: TEMP },
    ],
  });
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  states[DEFAULT_SPACE].attributes.setup_topology = mkTopo();
  const su = build(states);
  su._onCardClick({});
  su._dialogPage = "setup";
  su._render();
  const page = collect(su.shadowRoot).join("\n");
  check("an unconfigured solar slot shows the irradiance the plan uses",
    /120 W\/m² · Open-Meteo/.test(page));
  check("only the genuinely absent slot reads as not configured",
    (page.match(/not configured/g) || []).length === 1,
    "the solar row has a fallback; the outdoor temperature row does not");

  // Without any irradiance source the old answer is the right one.
  const bare = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  delete bare[SOLAR_ID];
  bare[DEFAULT_SPACE].attributes.setup_topology = mkTopo();
  const suBare = build(bare);
  suBare._onCardClick({});
  suBare._dialogPage = "setup";
  suBare._render();
  check("no source at all still says not configured",
    !/W\/m² ·/.test(collect(suBare.shadowRoot).join("\n")));
}

// --- Scenario: slot values follow the user's unit system (T3b) -------------
// A natively-°F probe read raw showed °F on a metric install while every
// other HA surface converts. The card must prefer the frontend's own
// formatter and keep the raw concatenation only as a fallback.
{
  const TEMP = ["sensor", "number", "input_number"];
  const topo = {
    two_zone: false, dhw: false, valve_mode: "none",
    buffer: { volume_l: 200, is_store: false, max_temp: 60 },
    wood: { present: true, volume_l: 500 },
    edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "upper_zone"],
      ["wood_tank", "buffer_tank"]],
    slots: [
      { key: "wood_tank_top_entity", label: "Wood tank top",
        place: "wood_tank", entity: "sensor.wood_top", domains: TEMP },
    ],
  };
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  states[DEFAULT_SPACE].attributes.setup_topology = topo;
  states["sensor.wood_top"] = {
    state: "140.0", attributes: { unit_of_measurement: "°F" } };

  const fmt = build(states);
  fmt.hass = { states, formatEntityState: (st) =>
    st === states["sensor.wood_top"] ? "60.0 °C" : `${st.state}` };
  fmt._onCardClick({});
  fmt._dialogPage = "setup";
  fmt._render();
  const fmtPage = collect(fmt.shadowRoot).join("\n");
  check("the frontend's formatter wins: the probe reads in the user's units",
    /60\.0 °C/.test(fmtPage) && !/140\.0 °F/.test(fmtPage));

  const raw = build(states);
  raw._onCardClick({});
  raw._dialogPage = "setup";
  raw._render();
  check("an older frontend without the formatter still gets the raw value",
    /140\.0 °F/.test(collect(raw.shadowRoot).join("\n")));
}

// --- Scenario: the card speaks Swedish (v4.2.0 i18n + currency) -------------
//
// The language rides on `hass.language` and is applied in the hass setter, so
// no card-level configuration exists (or is needed). English remains the
// default and the fallback: every earlier scenario in this file asserts the
// English literals, which is itself the regression test for the "en" table.
{
  const svStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  const sv = new Card();
  sv.setConfig({ type: "custom:heatpump-optimizer-card" });
  sv.hass = { states: svStates, language: "sv-SE" };
  const svDump = collect(sv.shadowRoot).join("\n");
  check("hass.language sv-SE renders the legend in Swedish",
    ["Elpris", "Varmvattenberedning", "Uppvärmning", "Utetemperatur",
     "Innetemperatur", "Solinstrålning"].every((l) => svDump.includes(l)),
    svDump.match(/class="legend"[\s\S]{0,400}/)?.[0]);
  check("the default title localizes too (it is not baked in at setConfig)",
    /Värmepumpsplan/.test(svDump) && !/Heat pump plan/.test(svDump));
  check("reason codes explain themselves in Swedish",
    /Billigaste timmarna/.test(sv._reasonHtml([{ reason: "cheap_price" }])) &&
    /Varmvatten behövs nu/.test(sv._reasonHtml([{ reason: "dhw_window" }])));
  check("wire contracts stay untranslated under sv",
    /data-key="price"/.test(svDump) && /data-key="dhw_slots"/.test(svDump));

  sv._onCardClick({});
  const svExpanded = collect(sv.shadowRoot).join("\n");
  check("the expanded dialog is Swedish: tabs, slot actions, schedule editor",
    /Anläggning/.test(svExpanded) &&
    /Tillämpa denna plan/.test(svExpanded) &&
    /Spara som mitt schema/.test(svExpanded) &&
    /Varmvattenfönster/.test(svExpanded));
  check("the slot menu strings are whole Swedish sentences",
    /värmepass/.test(
      (() => { // exercise the L() path the menu uses
        sv._closeExpanded();
        return ctxL(sv, "menu.add_slot_space");
      })()
    ));

  // A language without a dictionary falls back to English wholesale.
  const de = new Card();
  de.setConfig({ type: "custom:heatpump-optimizer-card" });
  de.hass = { states: mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    language: "de-DE" };
  const deDump = collect(de.shadowRoot).join("\n");
  check("an unknown language falls back to English",
    deDump.includes("Electricity price") &&
    deDump.includes("Heat pump plan") &&
    !/Elpris/.test(deDump));

  // Currency: published by the plan sensor as `currency`, shown on the price
  // axis and in the legend chip; absent, the SEK fallback holds.
  const eurStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  eurStates[DEFAULT_SPACE].attributes.currency = "EUR";
  const eur = build(eurStates);
  const eurDump = collect(eur.shadowRoot).join("\n");
  check("a currency published on the plan sensor reaches the price axis",
    /EUR\/kWh/.test(eurDump) && !/SEK\/kWh/.test(eurDump));
  const sekDump =
    collect(build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)).shadowRoot)
      .join("\n");
  check("no published currency still falls back to SEK",
    /SEK\/kWh/.test(sekDump));
  // hass's global currency fills in when the sensor publishes none.
  const nok = new Card();
  nok.setConfig({ type: "custom:heatpump-optimizer-card" });
  nok.hass = { states: mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    config: { currency: "NOK" } };
  check("hass.config.currency fills in when the sensor publishes none",
    /NOK\/kWh/.test(collect(nok.shadowRoot).join("\n")));

  // Leave the module back in English for anything that runs after this block.
  build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
}

// The slot-menu helper above: reach the same lookup the menu uses without
// standing up a pointer gesture. `_openSlotMenu` needs real chart geometry;
// what the i18n scenario cares about is only that the per-channel sentence
// exists in the active language.
function ctxL(card, key) {
  card._closeSlotMenu();
  // The card file keeps L private; the menu markup is the observable. Build
  // it via a minimal fake wrapper.
  const host = new (Object.getPrototypeOf(card.shadowRoot).constructor)("div");
  host.classList.add("chartwrap");
  card.shadowRoot.appendChild(host);
  card._geom = null;
  try {
    card._openSlotMenu("space", Date.now(), 0, 0, host);
    const menu = card._slotMenu;
    return menu ? menu.innerHTML : "";
  } finally {
    card._closeSlotMenu();
  }
}

// --- Scenario: the visual config editor (v4.2.0) ----------------------------
//
// The editor is a plain element wrapping ha-form: the schema, the effective
// values and the config-changed contract are the card's own code and are
// exercised here; ha-form itself is Home Assistant's and is only stood up as
// a stub node the editor sets properties on.
{
  const Editor = ctx.customElements.get("heatpump-optimizer-card-editor");
  check("an editor element is registered", !!Editor);

  const el = Card.getConfigElement();
  check("getConfigElement returns the editor element",
    !!el && el.tagName === "HEATPUMP-OPTIMIZER-CARD-EDITOR");

  const stub = Card.getStubConfig();
  let stubErr = null;
  try { new Card().setConfig(stub); } catch (e) { stubErr = e; }
  check("getStubConfig passes setConfig", stubErr === null,
    stubErr && stubErr.message);

  check("the card advertises itself with a preview",
    ctx.window.customCards.some((c) =>
      c.type === "heatpump-optimizer-card" && c.preview === true));

  const ed = new Editor();
  ed.hass = { states: {}, language: "en" };
  ed.setConfig(stub);
  const form = ed.querySelector("ha-form");
  check("the editor builds an ha-form with a schema",
    !!form && Array.isArray(form.schema));
  const names = form ? form.schema.map((s) => s.name) : [];
  check("the schema covers the card's config keys",
    ["title", "space_entity", "dhw_entity", "solar_entity", "hours",
     "what_if", "show_stats", "currency", "series"]
      .every((k) => names.includes(k)),
    `schema names: ${names.join(", ")}`);
  const spaceRow = form && form.schema.find((s) => s.name === "space_entity");
  check("entity pickers are filtered to this integration's sensors",
    !!spaceRow && spaceRow.selector.entity.integration === "heatpump_optimizer"
    && spaceRow.selector.entity.domain === "sensor");
  check("the form shows effective values, defaults filled in",
    form && form.data.hours === 24 && form.data.what_if === true &&
    form.data.show_stats === true && form.data.series.price === true);
  check("labels come from the dictionary, not raw key names",
    form && form.computeLabel({ name: "hours" }) === "Hours to show" &&
    form.computeLabel({ name: "price" }) === "Electricity price");

  // A user edit flows out as config-changed, and the emitted config both
  // passes setConfig and stays free of keys that restate defaults.
  let fired = null;
  ed.addEventListener("config-changed", (ev) => { fired = ev.detail.config; });
  form.dispatchEvent(new ctx.CustomEvent("value-changed", { detail: { value: {
    ...form.data, hours: 48, show_stats: false, title: "",
    series: { ...form.data.series, solar: false },
  } } }));
  check("editing fires config-changed with the new values",
    !!fired && fired.hours === 48 && fired.show_stats === false &&
    fired.type === "custom:heatpump-optimizer-card");
  check("an emptied field falls back to the default rather than storing ''",
    fired && !("title" in fired));
  // The form pre-fills every default, so its emitted value carries them all;
  // the stored config must not. Only the two keys the user changed (hours,
  // show_stats) and the non-default series choice may appear.
  check("untouched defaults do not appear in the emitted config",
    fired && !("space_entity" in fired) && !("dhw_entity" in fired) &&
    !("solar_entity" in fired) && !("what_if" in fired),
    fired && JSON.stringify(fired));
  check("only non-default series choices are stored",
    fired && fired.series && fired.series.solar === false &&
    !("price" in fired.series));
  // A value edited back to its default drops out of the config again.
  let firedBack = null;
  ed.addEventListener("config-changed", (ev) => { firedBack = ev.detail.config; });
  form.dispatchEvent(new ctx.CustomEvent("value-changed", { detail: { value: {
    ...form.data, hours: 24, show_stats: false,
  } } }));
  check("a field edited back to its default is dropped, not stored",
    !!firedBack && !("hours" in firedBack) && firedBack.show_stats === false,
    firedBack && JSON.stringify(firedBack));

  // An explicit `title: ""` is a real choice (it renders no header text):
  // it must survive an unrelated edit, while a title that was never
  // configured must not materialize as "".
  const edTitled = new Editor();
  edTitled.hass = { states: {}, language: "en" };
  edTitled.setConfig({ type: "custom:heatpump-optimizer-card", title: "" });
  const formTitled = edTitled.querySelector("ha-form");
  let firedTitled = null;
  edTitled.addEventListener("config-changed",
    (ev) => { firedTitled = ev.detail.config; });
  formTitled.dispatchEvent(new ctx.CustomEvent("value-changed",
    { detail: { value: { ...formTitled.data, hours: 48 } } }));
  check("an existing title: \"\" survives an unrelated edit",
    !!firedTitled && firedTitled.title === "" && firedTitled.hours === 48,
    firedTitled && JSON.stringify(firedTitled));
  let firedErr = null;
  try { new Card().setConfig(fired); } catch (e) { firedErr = e; }
  check("the emitted config passes setConfig", firedErr === null,
    firedErr && firedErr.message);
}

// --- Scenario: the headline stats row (v4.2.0) ------------------------------
{
  const statStates = () => ({
    "sensor.heat_pump_optimizer_predicted_savings": {
      state: "12.34", attributes: { unit_of_measurement: "SEK" } },
    "sensor.heat_pump_optimizer_savings_percentage": {
      state: "8.2", attributes: {} },
    "sensor.heat_pump_optimizer_optimization_score": {
      state: "82", attributes: { envelope: 90, machine: 75 } },
    "sensor.heat_pump_optimizer_plan_narrative": {
      state: "cheap_price", attributes: {
        lines: ["Most heating is placed in the cheapest hours."],
        language: "en" } },
  });
  const full = { ...mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), ...statStates() };
  const hl = build(full);
  const hlDump = collect(hl.shadowRoot).join("\n");
  check("headline shows the projected savings in the sensor's unit",
    /class="headline"/.test(hlDump) && /Projected savings/.test(hlDump) &&
    /12\.34 SEK \(8%\)/.test(hlDump),
    hlDump.match(/class="headline"[\s\S]{0,300}/)?.[0]);

  // The savings sensor declares the unit its value is denominated in; a
  // card-level `currency:` must not relabel it (nothing converts here).
  const relabeled = build(full, { currency: "EUR" });
  check("a config currency does not relabel the sensor's own unit",
    /12\.34 SEK/.test(collect(relabeled.shadowRoot).join("\n")));
  const noUnit = { ...full,
    "sensor.heat_pump_optimizer_predicted_savings": {
      state: "12.34", attributes: {} } };
  check("a savings sensor without a unit falls back to the resolved currency",
    /12\.34 EUR/.test(
      collect(build(noUnit, { currency: "EUR" }).shadowRoot).join("\n")));

  // Percent spacing is orthographic, so it rides the language: sv keeps the
  // space before %, en drops it.
  const svHl = new Card();
  svHl.setConfig({ type: "custom:heatpump-optimizer-card" });
  svHl.hass = { states: full, language: "sv-SE" };
  check("Swedish spaces the percent; English does not",
    /\(8 %\)/.test(collect(svHl.shadowRoot).join("\n")));
  build(full); // leave the module back in English

  // Discovery is scoped to the plan sensors' device (shared entity-id
  // prefix): a foreign integration's sensor that shares the suffix — and
  // sorts first — must not capture the headline.
  const foreign = { ...full,
    "sensor.aaa_other_vendor_predicted_savings": {
      state: "99.99", attributes: { unit_of_measurement: "EUR" } } };
  const scopedDump = collect(build(foreign).shadowRoot).join("\n");
  check("headline binds to the plan sensors' device, not a foreign twin",
    /12\.34 SEK/.test(scopedDump) && !/99\.99/.test(scopedDump));

  // A backend that starts publishing the stat sensors later must still be
  // found: the miss is cached, but keyed to the number of sensor ids.
  const lateCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  check("(setup) no headline before the backend publishes",
    !/class="headline"/.test(collect(lateCard.shadowRoot).join("\n")));
  lateCard.hass = { states:
    { ...mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), ...statStates() } };
  check("a late-arriving backend still surfaces the headline",
    /class="headline"/.test(collect(lateCard.shadowRoot).join("\n")));
  check("headline shows the optimization score",
    /Optimization score/.test(hlDump) && /82\/100/.test(hlDump));
  check("headline shows the narrative's first line",
    hlDump.includes("Most heating is placed in the cheapest hours."));

  // The row must track its own sensors: a new savings value re-renders even
  // though no plan data changed (the headline is part of _signature).
  const next = { ...full,
    "sensor.heat_pump_optimizer_predicted_savings": {
      state: "20.00", attributes: { unit_of_measurement: "SEK" } } };
  hl.hass = { states: next };
  check("a savings update re-renders the headline",
    /20\.00 SEK/.test(collect(hl.shadowRoot).join("\n")));

  // No stat sensors: no row, no empty chrome.
  const bare = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  check("no headline chrome when the sensors are absent",
    !/class="headline"/.test(collect(bare.shadowRoot).join("\n")));

  // Sensors present but unavailable and with no lines: still nothing.
  const unavail = { ...mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    "sensor.heat_pump_optimizer_predicted_savings": {
      state: "unavailable", attributes: {} },
    "sensor.heat_pump_optimizer_optimization_score": {
      state: "unknown", attributes: {} },
    "sensor.heat_pump_optimizer_plan_narrative": {
      state: "idle", attributes: { lines: [] } } };
  check("unavailable sensors render no row either",
    !/class="headline"/.test(collect(build(unavail)).join("\n") ||
      collect(build(unavail).shadowRoot).join("\n")));

  // The config toggle removes the row even with data to show.
  const off = build(full, { show_stats: false });
  check("show_stats: false removes the row",
    !/class="headline"/.test(collect(off.shadowRoot).join("\n")));
  let err = null;
  try { new Card().setConfig({ show_stats: "yes" }); } catch (e) { err = e; }
  check("a non-boolean show_stats is rejected",
    !!err && /show_stats/.test(err.message));
}

// --- Scenario: reduced motion is honored (v4.2.0) ---------------------------
{
  reducedMotion.on = false;
  const animated = collect(build(
    mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)).shadowRoot).join("\n");
  check("the zoom controls fade by default",
    /transition: opacity 120ms/.test(animated));
  reducedMotion.on = true;
  const calm = collect(build(
    mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)).shadowRoot).join("\n");
  check("prefers-reduced-motion drops the fade",
    !/transition: opacity 120ms/.test(calm));
  reducedMotion.on = false;
}

// --- Scenario: localStorage keys carry the card's identity (v4.2.0) ---------
//
// Two cards can plot the same entities — different titles, different horizons
// — and a series hidden on one must not vanish from the other.
{
  const a = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    { title: "Upstairs" });
  const b = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    { title: "Downstairs", hours: 48 });
  check("cards with different config identities get different keys",
    a._storageKey(a._config) !== b._storageKey(b._config) &&
    a._storageKey(a._config).includes("Upstairs") &&
    a._storageKey(a._config).includes(DEFAULT_SPACE));
  a._onLegendClick({ stopPropagation(){}, currentTarget: {
    getAttribute: (k) => (k === "data-key" ? "outdoor" : null) } });
  const bReloaded = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true),
    { title: "Downstairs", hours: 48 });
  check("a toggle on one card does not leak into the other",
    a._hidden.outdoor === true && !bReloaded._hidden.outdoor);

  // A pre-v4.2.0 key (no identity suffix) still loads, so an upgrade keeps
  // the user's saved toggles; writes then move to the new key.
  const legacySpace = "sensor.legacy_space_heating_plan";
  const legacyDhw = "sensor.legacy_dhw_heating_plan";
  store[`heatpump-optimizer-card:${legacySpace}:${legacyDhw}`] =
    JSON.stringify({ price: true });
  const legacy = build(mkStates(legacySpace, legacyDhw, true),
    { space_entity: legacySpace, dhw_entity: legacyDhw });
  check("a legacy storage key is still honoured after the upgrade",
    legacy._hidden.price === true);
}

// --- Scenario: keyboard access to the plan slots (v4.2.0) -------------------
{
  const kb = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  const kbDump = collect(kb.shadowRoot).join("\n");
  check("editable slots are focusable buttons with a spoken label",
    /<rect class="slot" [^>]*tabindex="0"/.test(kbDump) &&
    /<rect class="slot" [^>]*role="button"/.test(kbDump) &&
    /Press Enter for actions/.test(kbDump));
  check("the lanes are focusable add targets",
    /<rect class="lane" [^>]*tabindex="0"/.test(kbDump) &&
    /Press Enter to add a slot/.test(kbDump));
  check("an svg with focusable children is not role=img",
    /<svg viewBox="0 0 900[^>]*role="group"/.test(kbDump));

  const svg = kb._chartSvgs(kb.shadowRoot)[0];
  const slot = svg.querySelector(".slot");
  check("there is a slot to drive", !!slot && slot.dataset.index !== undefined);
  const keydown = (target, key) => svg._listeners.keydown.forEach((f) =>
    f({ key, target, preventDefault(){}, stopPropagation(){} }));

  const kdBase = (docListeners.keydown || []).length;
  keydown(slot, "Enter");
  check("Enter on a slot opens the slot menu",
    !!kb._slotMenu && /slot/.test(kb._slotMenu.innerHTML));
  check("an open menu parks an Escape listener on the document",
    (docListeners.keydown || []).length === kdBase + 1);
  check("a keyboard-opened menu takes focus onto its button",
    document.activeElement &&
    document.activeElement.tagName === "BUTTON");
  kb._slotMenu._listeners.keydown.forEach((f) =>
    f({ key: "Escape", stopPropagation(){} }));
  check("Escape dismisses the menu", kb._slotMenu === null);
  check("and hands focus back to the slot it came from",
    document.activeElement === kb._chartSvgs(kb.shadowRoot)[0]
      .querySelector(".slot") ||
    (document.activeElement &&
      document.activeElement.classList.contains &&
      document.activeElement.classList.contains("slot")));
  check("closing the menu releases its document Escape listener",
    (docListeners.keydown || []).length === kdBase);

  const channel = slot.dataset.channel;
  const before = (kb._draftRuns()[channel] || []).length;
  keydown(slot, "Delete");
  const after = (kb._draftRuns()[channel] || []).length;
  check("Delete removes the focused slot", before > 0 && after === before - 1);
  // The render that removed the slot destroyed the element holding focus;
  // the card must not let it fall to document.body. The slot is gone, so
  // its lane (or, failing that, the chart svg) is the logical successor.
  const active = document.activeElement;
  check("after Delete, focus lands on the lane or the chart, not the body",
    !!active && active !== document.body &&
    ((active.classList.contains("lane") &&
      active.dataset.channel === channel) ||
     active.tagName === "SVG"),
    active && `${active.tagName} class=${active.className}`);

  // A MOUSE-opened menu leaves focus on the chart, so the menu element
  // itself never sees the keydown: Escape is caught at the document while
  // the menu is open.
  const freshSvg = kb._chartSvgs(kb.shadowRoot)[0];
  const freshSlot = freshSvg.querySelector(".slot");
  const freshRuns = kb._draftRuns()[freshSlot.dataset.channel] || [];
  const freshRun = freshRuns[Number(freshSlot.dataset.index)];
  kb._openSlotMenu(freshSlot.dataset.channel,
    (freshRun.start + freshRun.end) / 2, 120, 300, freshSvg);
  check("a mouse-opened menu does not steal focus",
    !!kb._slotMenu && document.activeElement !== kb._slotMenu &&
    (document.activeElement === null ||
      document.activeElement.tagName !== "BUTTON"));
  fireDocument("keydown",
    { key: "Escape", stopPropagation(){}, preventDefault(){} });
  check("Escape closes a mouse-opened menu via the document listener",
    kb._slotMenu === null);
  check("the document Escape listener is removed with the menu",
    (docListeners.keydown || []).length === kdBase);

  const lane = kb._chartSvgs(kb.shadowRoot)[0].querySelector(".lane");
  const laneChannel = lane.dataset.channel;
  const laneBefore = (kb._draftRuns()[laneChannel] || []).length;
  kb._chartSvgs(kb.shadowRoot)[0]._listeners.keydown.forEach((f) =>
    f({ key: "Enter", target: lane, preventDefault(){}, stopPropagation(){} }));
  check("Enter on a lane offers the menu there too", !!kb._slotMenu);
  // Acting on the menu re-renders; focus must follow to the fresh lane.
  kb._slotMenu._listeners.click.forEach((f) => f({
    target: kb._slotMenu.querySelector("button"), stopPropagation(){} }));
  const laneActive = document.activeElement;
  check("a menu action returns focus to the lane in the fresh DOM",
    !!laneActive && laneActive !== document.body &&
    ((laneActive.classList.contains("lane") &&
      laneActive.dataset.channel === laneChannel) ||
     laneActive.tagName === "SVG"),
    laneActive && `${laneActive.tagName} class=${laneActive.className}`);
}

// --- Scenario: keyboard access to the setup page (v4.2.0) -------------------
{
  const TEMP = ["sensor", "number", "input_number"];
  const topo = {
    two_zone: false, dhw: false, valve_mode: "none",
    buffer: { volume_l: 500, is_store: true, max_temp: 70 },
    wood: { present: false },
    edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "upper_zone"]],
    slots: [
      { key: "indoor_temp_entity", label: "Indoor temperature",
        place: "upper_zone", entity: "sensor.livingroom", domains: TEMP },
    ],
  };
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  states[DEFAULT_SPACE].attributes.setup_topology = topo;
  states["sensor.livingroom"] = {
    state: "21.0", attributes: { unit_of_measurement: "°C" } };
  const su = build(states);
  su._onCardClick({});
  su._dialogPage = "setup";
  su._render();
  const page = collect(su.shadowRoot).join("\n");
  check("setup rows are focusable buttons",
    /setup-hit[^>]*[\s\S]{0,120}?tabindex="0"/.test(page) &&
    /setup-hit[\s\S]{0,200}?role="button"/.test(page));
  check("the setup diagram is a group, not a flattened image",
    /setup-svg[\s\S]{0,200}?role="group"/.test(page));

  const hit = su.shadowRoot.querySelector(".setup-hit");
  hit._listeners.keydown.forEach((f) => f({ key: "Enter",
    currentTarget: hit, preventDefault(){}, stopPropagation(){} }));
  const picker = su.shadowRoot.querySelector(".setup-picker");
  check("Enter on a setup row opens the entity picker", !!picker);
  picker._listeners.keydown.forEach((f) =>
    f({ key: "Escape", stopPropagation(){} }));
  check("Escape closes the picker without assigning",
    !su.shadowRoot.querySelector(".setup-picker") && su._pickerKey === null);
  // The close re-rendered the page, destroying the focused select; focus
  // must come back to the row the picker was opened from, re-located by
  // its data-key in the fresh DOM.
  check("Escape returns focus to the setup row it came from",
    !!document.activeElement &&
    document.activeElement.classList.contains("setup-hit") &&
    document.activeElement.dataset.key === "indoor_temp_entity",
    document.activeElement &&
      `${document.activeElement.tagName} class=${document.activeElement.className}`);
}

// --- Shared rig for the v5.1.4 setup-page scenarios (items A-F) -------------
// One topology with every box kind the reports touch: an open outdoor node,
// the heat-pump cabinet, a wood tank, a valve, two zones. Built here rather
// than reusing the layout editor's rig above, which is scoped to its own
// block and carries a catalog these scenarios have no use for.
const SETUP_TEMP = ["sensor", "number", "input_number"];
const setupTopo = (over) => ({
  two_zone: true, dhw: false, valve_mode: "manual",
  layout: "valve_upper_direct_slab", two_tank_modelled: false,
  buffer: { volume_l: 500, is_store: true, max_temp: 65 },
  wood: { present: true, volume_l: 750 },
  edges: [
    ["heat_pump", "buffer_tank"],
    ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"],
    ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"],
  ],
  positions: {},
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature",
      place: "upper_zone", entity: "sensor.livingroom", domains: SETUP_TEMP },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature",
      place: "lower_zone", entity: null, domains: SETUP_TEMP },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
      place: "buffer_tank", entity: "sensor.tank", domains: SETUP_TEMP },
    { key: "wood_tank_top_entity", label: "Wood tank top",
      place: "wood_tank", entity: null, domains: SETUP_TEMP },
    { key: "mixing_valve_target_entity", label: "Valve target",
      place: "mixing_valve", entity: null, domains: SETUP_TEMP },
    { key: "outdoor_temp_entity", label: "Outdoor temperature",
      place: "outdoor", entity: "sensor.outside", domains: SETUP_TEMP },
    { key: "heat_pump_switch_entity", label: "Heat pump switch",
      place: "heat_pump", entity: null,
      domains: ["switch", "input_boolean", "climate"] },
  ],
  ...(over || {}),
});
function mkSetup(over, extraStates) {
  const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  states[DEFAULT_SPACE].attributes.setup_topology = setupTopo(over);
  states["sensor.livingroom"] = {
    state: "21.3", attributes: { unit_of_measurement: "°C",
      friendly_name: "Living room" } };
  states["sensor.tank"] = {
    state: "47.5", attributes: { unit_of_measurement: "°C",
      friendly_name: "Buffer tank" } };
  states["sensor.outside"] = {
    state: "3.0", attributes: { unit_of_measurement: "°C",
      friendly_name: "Outside" } };
  Object.assign(states, extraStates || {});
  const c = build(states);
  c._onCardClick({});
  c._dialogPage = "setup";
  c._render();
  return c;
}
const setupPage = (over, extraStates) =>
  collect(mkSetup(over, extraStates).shadowRoot).join("\n");
const setupBox = (card, place) =>
  (card._layoutBoxes || []).find((b) => b.place === place);

// --- Scenario: the heat pump lost its louvres (item A, v5.1.4) --------------
// Two horizontal strokes used to sit in the cabinet's bottom-left band as
// vents. From a step back they read as two stray lines in the corner of a
// box rather than as louvres, so they were removed. Everything else the
// silhouette is built from -- contour, fan shroud, blades, hub, header
// divider -- stays, and this pins that the removal took the ink and nothing
// around it.
{
  const X = 16, Y = 79, W = 200, H = 49;
  const acc = vm
    .runInContext(`NODE_SHAPES.hp.accents(${X}, ${Y}, ${W}, ${H})`, ctx)
    .filter(Boolean);
  check("the heat pump draws four accents, not six",
    acc.length === 4, `${acc.length} accents: ${JSON.stringify(acc)}`);
  const ds = acc.map((a) => a.d || "").join(" ");
  check("the fan shroud, its blades, the hub and the divider all survive",
    /A 8 8 0 1 1/.test(ds) &&
    (ds.match(/A 5 5 0 0 1/g) || []).length === 3 &&
    acc.some((a) => (a.cls || "").includes("hub") && a.r === 1.6) &&
    acc.some((a) => (a.cls || "").includes("divider")),
    ds);
  // The louvres lived at y+h-7 and y+h-4.5, i.e. the band within 10 units of
  // the cabinet floor. Numeric, not textual: any ink that lands there again
  // fails this whether or not it is spelled the way the old pair was. `d`
  // is read as "M/L x y" pairs, which is every point the accents place.
  const floorBand = [];
  for (const a of acc) {
    for (const m of String(a.d || "").matchAll(/[ML] (-?[\d.]+) (-?[\d.]+)/g)) {
      if (Number(m[2]) > Y + H - 10) floorBand.push(m[0]);
    }
    if (a.cy !== undefined && a.cy > Y + H - 10) floorBand.push(`circle@${a.cy}`);
  }
  check("nothing is drawn in the cabinet's floor band any more",
    floorBand.length === 0,
    `ink below y=${Y + H - 10}: ${floorBand.join(", ")}`);
  // ...and the same holds once the box is actually drawn: the louvres would
  // have rendered as `M 30 121 H 56 M 30 123.5 H 56` on this box.
  const page = setupPage();
  check("the drawn heat pump has no louvre strokes",
    !/M 30 121 H 56/.test(page) && !/M 30 123\.5 H 56/.test(page) &&
    !/H 56 M 30/.test(page));
  check("but it does still have its fan",
    /M 190 92 A 8 8 0 1 1 206 92/.test(page));
}

// --- Scenario: the flow chevrons lie along their pipes (item B, v5.1.4) -----
// `pipeDeco` used to draw an axis-aligned glyph in both branches: a
// horizontal chevron for every cross-column pipe whatever its slope. Those
// pipes are cubics whose ends usually differ in height, so on most of them
// the arrow sat across the pipe at very nearly a right angle -- which is
// what the reporter saw. The glyph is now built from the curve's own unit
// tangent at its midpoint.
//
// Nothing below repeats the card's formula. The tangent is measured off the
// ACTUAL drawn path by central difference, so a chevron that agreed with a
// wrong derivation would still fail here.
{
  // Every pipe in the card's drawing, paired with the chevron on it.
  //
  // One asymmetry to respect: a cross-column pipe's cubic is written from
  // source to target, so the path runs with the water. A same-column pipe
  // is always written top to bottom whichever way the water goes, so its
  // flow direction has to come from the edge's own place names.
  const pipesOf = (card, html) => {
    const page = html || collect(card.shadowRoot).join("\n");
    const boxes = card._layoutBoxes || [];
    const boxOf = (place) => boxes.find((b) => b.place === place);
    const re = new RegExp(
      '<path class="setup-pipe([^"]*)" data-edge="([^"]+)"\\s+' +
      'd="M\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(C|L)([^"]*)"\\s*/>' +
      '\\s*(?:<circle[^>]*/>\\s*<circle[^>]*/>)?' +
      '\\s*(?:<path class="setup-flow" d="M (-?[\\d.]+) (-?[\\d.]+) ' +
      'L (-?[\\d.]+) (-?[\\d.]+) L (-?[\\d.]+) (-?[\\d.]+)"\\s*/>)?',
      "g");
    const out = [];
    let m;
    while ((m = re.exec(page)) !== null) {
      const n = (v) => Number(v);
      const rest = (m[6].match(/-?[\d.]+/g) || []).map(Number);
      const cubic = m[5] === "C";
      const p0 = [n(m[3]), n(m[4])];
      const p1 = cubic ? [rest[0], rest[1]] : null;
      const p2 = cubic ? [rest[2], rest[3]] : null;
      const p3 = cubic ? [rest[4], rest[5]] : [rest[0], rest[1]];
      const [srcPlace, dstPlace] = m[2].split(">");
      const src = boxOf(srcPlace);
      const dst = boxOf(dstPlace);
      // True when the path was written against the water: only ever the
      // same-column case, and only when the source box is the lower one.
      const flipped = !cubic && !!src && !!dst && src.y > dst.y;
      out.push({
        edge: m[2], cls: m[1], cubic, p0, p1, p2, p3, flipped,
        chevron: m[8] === undefined ? null : {
          tail1: [n(m[7]), n(m[8])],
          apex: [n(m[9]), n(m[10])],
          tail2: [n(m[11]), n(m[12])],
        },
      });
    }
    return out;
  };
  // The drawn path at t (t running along the PATH), and its tangent there by
  // central difference -- the curve's real direction, not a restatement of
  // the card's algebra.
  const at = (p, t) => {
    if (!p.cubic) {
      return [p.p0[0] + (p.p3[0] - p.p0[0]) * t,
        p.p0[1] + (p.p3[1] - p.p0[1]) * t];
    }
    const u = 1 - t;
    return [0, 1].map((i) =>
      u * u * u * p.p0[i] + 3 * u * u * t * p.p1[i] +
      3 * u * t * t * p.p2[i] + t * t * t * p.p3[i]);
  };
  // The direction the WATER moves at the pipe's midpoint.
  const flowAtMid = (p) => {
    const h = 1e-6;
    const a = at(p, 0.5 - h);
    const b = at(p, 0.5 + h);
    const sign = p.flipped ? -1 : 1;
    return [sign * (b[0] - a[0]) / (2 * h), sign * (b[1] - a[1]) / (2 * h)];
  };
  // How well the chevron's axis agrees with the flow there: +1 is "points
  // exactly down the pipe", 0 "crosses it at a right angle", -1 "points
  // back up it". This is the number the bug got wrong.
  const report = (p) => {
    const mid = at(p, 0.5);
    const d = [p.chevron.apex[0] - mid[0], p.chevron.apex[1] - mid[1]];
    const T = flowAtMid(p);
    const dn = Math.hypot(d[0], d[1]);
    const tn = Math.hypot(T[0], T[1]);
    return {
      mid, d, dn, T,
      cos: (d[0] * T[0] + d[1] * T[1]) / (dn * tn),
      // The chord midpoint, which is where the glyph is anchored. For this
      // cubic the two coincide exactly -- the two 40-unit handles cancel --
      // and that is worth pinning, because the anchoring assumes it.
      chord: [(p.p0[0] + p.p3[0]) / 2, (p.p0[1] + p.p3[1]) / 2],
    };
  };
  const near = (a, b, eps) => Math.abs(a - b) <= (eps === undefined ? 1e-6 : eps);
  const byEdge = (list, e) => list.find((p) => p.edge === e);

  // The five orientations, each on a real pipe of a real drawing. Downhill,
  // uphill and flat come from the default rig; a near-horizontal pipe is
  // made by parking two boxes almost level; the two vertical directions
  // need a same-column edge that is not the one into the mixing valve
  // (which drops its chevron on purpose -- see (3)).
  const rig = mkSetup();
  const cross = pipesOf(rig);
  const upCard = mkSetup({
    edges: [["wood_tank", "heat_pump"], ["heat_pump", "buffer_tank"]] });
  const downCard = mkSetup({
    edges: [["heat_pump", "wood_tank"], ["heat_pump", "buffer_tank"]] });
  const tiltCard = mkSetup({
    edges: [["heat_pump", "buffer_tank"]],
    positions: { heat_pump: [16, 120], buffer_tank: [260, 113] } });

  const cases = [
    ["downhill cross-column", byEdge(cross, "mixing_valve>lower_zone")],
    ["uphill cross-column", byEdge(cross, "wood_tank>buffer_tank")],
    ["flat cross-column", byEdge(cross, "mixing_valve>upper_zone")],
    ["near-horizontal cross-column",
      byEdge(pipesOf(tiltCard), "heat_pump>buffer_tank")],
    ["vertical, water flowing down",
      byEdge(pipesOf(downCard), "heat_pump>wood_tank")],
    ["vertical, water flowing up",
      byEdge(pipesOf(upCard), "wood_tank>heat_pump")],
  ];
  // The set is only worth anything if the orientations really differ, so
  // state each one's slope and insist the family covers the ground.
  const slopes = [];
  for (const [name, p] of cases) {
    if (!p || !p.chevron) {
      check(`${name}: the pipe is drawn with a chevron`, false,
        p ? "pipe drawn without one" : "pipe not found");
      continue;
    }
    const r = report(p);
    const dy = r.T[1] / Math.hypot(r.T[0], r.T[1]);
    slopes.push({ name, dy });
    check(`${name}: the chevron points down the pipe, not across it`,
      near(r.cos, 1, 1e-6) && near(r.dn, 2, 1e-3),
      `flow direction (${r.T.map((v) => v.toFixed(2))}), ` +
      `cos=${r.cos.toFixed(9)}, |apex-mid|=${r.dn.toFixed(4)}`);
    check(`${name}: it is anchored on the pipe's own midpoint`,
      near(r.mid[0], r.chord[0], 1e-6) && near(r.mid[1], r.chord[1], 1e-6),
      `curve mid ${r.mid} vs chord mid ${r.chord}`);
    // The tails straddle the axis 3 units back and 3 to each side, so the
    // glyph is the same arrowhead as before -- just rotated into frame.
    const tm = [(p.chevron.tail1[0] + p.chevron.tail2[0]) / 2,
      (p.chevron.tail1[1] + p.chevron.tail2[1]) / 2];
    const span = Math.hypot(p.chevron.tail1[0] - p.chevron.tail2[0],
      p.chevron.tail1[1] - p.chevron.tail2[1]);
    const reach = Math.hypot(tm[0] - p.chevron.apex[0],
      tm[1] - p.chevron.apex[1]);
    check(`${name}: the arrowhead keeps its 5-long, 6-wide proportions`,
      near(reach, 5, 1e-3) && near(span, 6, 1e-3),
      `apex-to-tailmid ${reach.toFixed(4)}, span ${span.toFixed(4)}`);
    // ...and it is a chevron, not a spike: the two tails are on opposite
    // sides of the axis.
    const nrm = [-r.T[1], r.T[0]];
    const side = (pt) => (pt[0] - r.mid[0]) * nrm[0] + (pt[1] - r.mid[1]) * nrm[1];
    check(`${name}: its two tails sit on opposite sides of the axis`,
      side(p.chevron.tail1) * side(p.chevron.tail2) < 0,
      `${side(p.chevron.tail1).toFixed(3)} and ` +
      `${side(p.chevron.tail2).toFixed(3)}`);
  }
  // Genuinely different orientations, not one orientation spelled six ways.
  // `dy` here is the flow direction's vertical component once normalised:
  // +1 straight down, -1 straight up, 0 dead level.
  const vy = slopes.map((x) => x.dy);
  const seen = (lo, hi) => vy.some((v) => v > lo && v < hi);
  check("the six cases really are six different slopes",
    slopes.length === 6 &&
    vy.some((v) => near(v, 1, 1e-9)) &&   // straight down
    vy.some((v) => near(v, -1, 1e-9)) &&  // straight up
    vy.some((v) => near(v, 0, 1e-9)) &&   // dead level
    seen(0.02, 0.5) &&                  // barely tilted
    seen(0.5, 0.999) &&                 // steeply down, but not vertical
    seen(-0.999, -0.5) &&               // steeply up, but not vertical
    new Set(vy.map((v) => v.toFixed(4))).size === 6,
    slopes.map((x) => `${x.name}=${x.dy.toFixed(4)}`).join("; "));

  // (2) The bug itself. A horizontal glyph on a sloped pipe puts the apex on
  //     the midpoint's own horizontal, and on the steepest pipe of the
  //     drawing that is nearly 90 degrees away from the pipe.
  const steep = byEdge(cross, "wood_tank>buffer_tank");
  const steepR = report(steep);
  const degrees = Math.acos(Math.max(-1, Math.min(1, steepR.cos))) * 180 / Math.PI;
  // 0.05 degrees, not zero: the card rounds the glyph's coordinates to
  // three decimals, which at a radius of 2 units is worth about 0.014
  // degrees of slack. The bug being excluded is 87 degrees wide.
  check("a steep pipe's chevron is no longer drawn horizontally",
    !near(steepR.d[1], 0, 1e-3) && degrees < 0.05,
    `dy=${(steep.p3[1] - steep.p0[1]).toFixed(1)}: apex is ` +
    `${steepR.d[1].toFixed(3)} off the midpoint's horizontal and ` +
    `${degrees.toFixed(6)} degrees off the tangent`);
  // The old code wrote `M mx-3s my-3 L mx+2s my L mx-3s my+3`, apex on the
  // midpoint's own y. Nowhere in the drawing now.
  const axisAligned = cross.filter((p) =>
    p.chevron && p.cubic &&
    Math.abs(p.p3[1] - p.p0[1]) > 1 &&
    near(p.chevron.apex[1], (p.p0[1] + p.p3[1]) / 2, 1e-3));
  check("no sloped pipe carries an axis-aligned chevron any more",
    axisAligned.length === 0, axisAligned.map((p) => p.edge).join(", "));

  // (3) The two suppressions the fix had to preserve.
  const intoValve = byEdge(cross, "buffer_tank>mixing_valve");
  check("a same-column pipe into the mixing valve still keeps its chevron off",
    !!intoValve && intoValve.chevron === null &&
    intoValve.p0[0] === intoValve.p3[0],
    intoValve ? JSON.stringify(intoValve.chevron) : "pipe not found");
  // An invalid pipe is drawn to be rejected, and an arrow on it would
  // endorse a connection the model refuses.
  const ed = mkSetup();
  ed._layoutEdit = { active: true,
    edges: setupTopo().edges.map((e) => e.slice()),
    positions: {}, invalid: ["heat_pump>buffer_tank"], match: null,
    drag: null, verdict: null };
  ed._refreshLayout();
  const canvas = ed.shadowRoot.querySelector(".setup-canvas");
  const edited = pipesOf(ed, (canvas && canvas.innerHTML) || "");
  const bad = edited.filter((p) => / invalid/.test(p.cls));
  check("an invalid pipe still carries dots but no chevron",
    bad.length === 1 && bad[0].edge === "heat_pump>buffer_tank" &&
    bad[0].chevron === null &&
    edited.some((p) => p.edge === "mixing_valve>lower_zone" && p.chevron),
    `${bad.length} invalid pipes; chevrons ` +
    bad.map((p) => JSON.stringify(p.chevron)).join(","));

  // (4) Direction, stated the plain way: the apex is on the downstream side.
  for (const [name, p] of cases) {
    if (!p || !p.chevron) continue;
    const mid = at(p, 0.5);
    const far = p.flipped ? p.p0 : p.p3;
    const toEnd = [far[0] - mid[0], far[1] - mid[1]];
    const d = [p.chevron.apex[0] - mid[0], p.chevron.apex[1] - mid[1]];
    check(`${name}: the apex is on the downstream side of the midpoint`,
      d[0] * toEnd[0] + d[1] * toEnd[1] > 0,
      `apex offset ${d.map((v) => v.toFixed(3))} vs travel ` +
      `${toEnd.map((v) => v.toFixed(3))}`);
  }
}

// --- Scenario: the boxes have room to breathe (item C, v5.1.4) -------------
// Titles and slot rows started at x+10 and right-anchored values ended at
// x+190, against contour walls at x+2 and x+w-2: eight viewBox units of
// air, which at desktop width reads as text pressed against the wall it is
// inside. `SETUP_PAD` is now 16, so the margin is 14 units on both sides.
//
// The point of the change is that NOTHING ELSE moved. Box width, the three
// column abscissae, the viewBox and the row arithmetic that sets `b.h` are
// all as shipped, which is why the drawing's only literal geometry pin
// (`<rect class="setup-box" x="430" y="360"`, the moved-box test above)
// still reads true and did not have to be rewritten.
{
  const card = mkSetup();
  const page = collect(card.shadowRoot).join("\n");
  const boxes = card._layoutBoxes || [];
  const PAD = 16;
  const COLW = 200;

  // (1) Nothing that was pinned moved.
  check("the columns, the box width and the viewBox are untouched",
    boxes.every((b) => b.w === COLW) &&
    boxes.every((b) => [16, 260, 504].includes(b.x)) &&
    /viewBox="0 0 720 \d+"/.test(page),
    `widths ${[...new Set(boxes.map((b) => b.w))]}, ` +
    `columns ${[...new Set(boxes.map((b) => b.x))].sort((a, c) => a - c)}, ` +
    `viewBox ${(/viewBox="([^"]*)"/.exec(page) || [])[1]}`);
  // b.h = 24 + (rows + caption lines) * 17 + 8, exactly as before: the line
  // count drives the height, and neither the padding nor the caption
  // wrapping that follows from it may change how many lines there are.
  // Counted off the drawing, so a caption that started wrapping differently
  // would show up here as a height that no longer matches its own content.
  const topo = setupTopo();
  const groups = page.split('<rect class="setup-box"').slice(1);
  const perBox = groups.map((g) => {
    const m = /^[^>]*x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"\s*height="([\d.]+)"/
      .exec(g);
    return {
      x: m && Number(m[1]), y: m && Number(m[2]),
      w: m && Number(m[3]), h: m && Number(m[4]),
      lines: (g.match(/<text class="setup-slot/g) || []).length,
    };
  });
  const heightWrong = perBox.filter((b) => b.h !== 24 + b.lines * 17 + 8);
  check("the row arithmetic that sets each box height is unchanged",
    perBox.length === boxes.length && heightWrong.length === 0,
    `${perBox.length} boxes; ` + perBox.map((b) =>
      `${b.x},${b.y} h=${b.h} lines=${b.lines}`).join("; "));
  check("the carrier rects are still written at the column abscissae",
    /<rect class="setup-box" x="16" y="16" width="200"/.test(page),
    (/<rect class="setup-box"[^>]*>/.exec(page) || [])[0]);

  // (2) The padding itself, measured against the contour walls the boxes
  //     are actually painted with (x+2 and x+w-2).
  const titles = [...page.matchAll(/<text class="setup-title" x="([\d.]+)"/g)]
    .map((m) => Number(m[1]));
  const labels = [...page.matchAll(/<text class="setup-slot[^"]*" x="([\d.]+)"/g)]
    .map((m) => Number(m[1]));
  const values = [...page.matchAll(
    /<tspan class="setup-value" x="([\d.]+)"/g)].map((m) => Number(m[1]));
  const cols = [...new Set(boxes.map((b) => b.x))].sort((a, b) => a - b);
  const leftGaps = [...new Set([...titles, ...labels])]
    .map((x) => x - (cols.reduce((best, c) => (x - c >= 0 && x - c < x - best
      ? c : best), -1e9) + 2));
  const rightGaps = [...new Set(values)].map((x) => {
    const c = cols.reduce((best, cc) => (x - cc >= 0 && x - cc < x - best
      ? cc : best), -1e9);
    return c + COLW - 2 - x;
  });
  check("every title and every row label clears the left wall by 14 units",
    titles.length > 0 && labels.length > 0 &&
    leftGaps.every((g) => g === 14),
    `text at x ${[...new Set([...titles, ...labels])].sort((a, b) => a - b)}, ` +
    `gaps ${[...new Set(leftGaps)]}`);
  check("every right-anchored value clears the right wall by 14 units",
    values.length > 0 && rightGaps.every((g) => g === 14),
    `values anchored at ${[...new Set(values)].sort((a, b) => a - b)}, ` +
    `gaps ${[...new Set(rightGaps)]}`);
  // Both are a real widening, not a shuffle: main put text 8 units off the
  // wall on both sides.
  check("that is a widening on both sides, not a shift",
    leftGaps.every((g) => g > 8) && rightGaps.every((g) => g > 8) &&
    leftGaps.every((g) => g <= 16) && rightGaps.every((g) => g <= 16));
  // The rule under a title starts where the title starts, or it reads as a
  // second, contradictory margin.
  const dividers = [...page.matchAll(
    /<path class="setup-accent divider" d="M ([\d.]+) [\d.]+ L ([\d.]+)/g)];
  check("the header rules start on the title's own left margin",
    dividers.length > 0 &&
    dividers.every((m) => cols.includes(Number(m[1]) - PAD)),
    dividers.map((m) => `${m[1]}->${m[2]}`).join(", "));

  // (3) The hit targets still cover the rows they belong to. A row that
  //     stops responding to the pointer is a worse regression than cramped
  //     text, so this is checked per row rather than in aggregate.
  const pairs = [...page.matchAll(new RegExp(
    '<text class="setup-slot[^"]*" x="([\\d.]+)" y="([\\d.]+)">\\s*' +
    '<tspan>([^<]*)</tspan>\\s*<tspan class="setup-value" x="([\\d.]+)"\\s*' +
    'text-anchor="end">([^<]*)</tspan></text>\\s*' +
    '<rect class="setup-hit" data-key="([^"]+)"[^>]*?' +
    'x="([\\d.]+)" y="([\\d.]+)" width="([\\d.]+)"\\s*height="([\\d.]+)"',
    "g"))].map((m) => ({
      labelX: Number(m[1]), baseline: Number(m[2]), label: m[3],
      valueX: Number(m[4]), value: m[5], key: m[6],
      x: Number(m[7]), y: Number(m[8]), w: Number(m[9]), h: Number(m[10]),
    }));
  check("every slot row is matched with its own hit rect",
    pairs.length === topo.slots.length,
    `${pairs.length} of ${topo.slots.length}`);
  // 12px text: the cap line sits about 8.7 units above the baseline and the
  // descenders about 2.6 below, so a rect that spans that band covers every
  // glyph in the row as well as the gap between label and value.
  const uncovered = pairs.filter((r) =>
    !(r.x <= r.labelX && r.x + r.w >= r.valueX &&
      r.y <= r.baseline - 9 && r.y + r.h >= r.baseline + 3));
  check("and every hit rect covers its row's text from label to value",
    uncovered.length === 0,
    uncovered.map((r) =>
      `${r.key}: rect x${r.x}..${r.x + r.w} y${r.y}..${r.y + r.h} ` +
      `vs text x${r.labelX}..${r.valueX} baseline ${r.baseline}`).join("; "));
  // The rects are inset inside their box and off their neighbours, so the
  // focus ring drawn on them (item F) has all four sides on screen.
  const boxOf = (r) => boxes.find((b) => b.x + 4 === r.x);
  check("the hit rects sit inside the box, clear of the contour",
    pairs.every((r) => {
      const b = boxOf(r);
      return b && r.x > b.x + 2 && r.x + r.w < b.x + COLW - 2;
    }),
    pairs.map((r) => `${r.key} x${r.x}+${r.w}`).join("; "));
  const sameBox = {};
  for (const r of pairs) (sameBox[r.x] ||= []).push(r);
  const touching = [];
  for (const list of Object.values(sameBox)) {
    const sorted = list.slice().sort((a, b) => a.y - b.y);
    for (let i = 1; i < sorted.length; i++) {
      const gap = sorted[i].y - (sorted[i - 1].y + sorted[i - 1].h);
      if (gap < 1) touching.push(`${sorted[i - 1].key}/${sorted[i].key}=${gap}`);
    }
  }
  check("and neighbouring rows do not touch, so neither do their rings",
    touching.length === 0, touching.join(", "));

  // (4) The outdoor node is explicitly out of scope: the owner has seen the
  //     open composition -- no walls, a tray baseline the rows hang over, a
  //     cloud in the header's right corner -- and wants it as shipped. These
  //     are the two paths origin/main draws for it at column 0, verbatim.
  //     Only the text inside moved, and only by the padding above.
  const cloudInk = [...page.matchAll(
    /<path class="setup-contour[^"]*"\s+d="([^"]*)"/g)]
    .map((m) => m[1].replace(/\s+/g, " ").trim());
  check("the outdoor node's tray and cloud are exactly as shipped",
    cloudInk.includes("M 18 57 A 6 6 0 0 0 24 63 H 208 A 6 6 0 0 0 214 57") &&
    cloudInk.includes("M 170 35 A 5.5 5.5 0 0 1 173 25.5 A 7 7 0 0 1 186 " +
      "22.5 A 6 6 0 0 1 197 25 A 6 6 0 0 1 203 35 Z"),
    cloudInk.slice(0, 3).join(" | "));
  // ...and it is still an OPEN composition: no header rule, no side walls,
  // no closing Z on the tray.
  const outdoorBox = boxes.find((b) => b.place === "outdoor");
  const outdoorGroup = page.slice(
    page.indexOf("kind-outdoor"),
    page.indexOf("<g", page.indexOf("kind-outdoor")));
  check("the outdoor node still has no walls and no header rule",
    !!outdoorBox && outdoorBox.x === 16 && outdoorBox.y === 16 &&
    !/setup-accent divider/.test(outdoorGroup) &&
    !/\bZ"/.test((/kind-outdoor"\s+d="([^"]*)"/.exec(page) || ["", ""])[1]),
    outdoorGroup.slice(0, 160).replace(/\s+/g, " "));
}

// --- Scenario: the solar row's label and value never collide (item D) -------
// With no radiation probe the plan still has irradiance -- from Open-Meteo
// or from the weather forecast -- and the row says so: "123 W/m² ·
// Open-Meteo", right-anchored in the same 200-unit row as its label. The
// old rule sized the label by COUNTING CHARACTERS of the value ("longer
// than 10 characters, allow the label 15"), which prices an "i" and a "W"
// alike and never looked at the value's rendered width at all. On the
// reporter's install the two strings ran through each other.
//
// Both strings are measured now. The value is priced first, the label gets
// what is left, and only the LABEL is ever ellipsized -- when the label
// would be squeezed below legibility the VALUE gives up its provenance tag
// instead, never a digit of the reading.
{
  const INNER = vm.runInContext("SETUP_COL_W - 2 * SETUP_PAD", ctx);
  const GAP = vm.runInContext("SETUP_ROW_GAP", ctx);
  const MINLABEL = vm.runInContext("SETUP_MIN_LABEL_W", ctx);
  const w = (s, bold) =>
    vm.runInContext(`setupTextW(${JSON.stringify(s)}, 12, ${!!bold})`, ctx);
  const fit = (label, alts) => vm.runInContext(
    `fitSlotRow(${JSON.stringify(label)}, ${JSON.stringify(alts)}, ` +
    `${INNER}, 12)`, ctx);
  // Every spelling of the fallback the card can actually produce, at both
  // ends of the reading's length, in both languages, plus the ordinary
  // rows it shares the drawing with.
  const cases = [
    ["Solar radiation", ["1000 W/m² · Open-Meteo", "1000 W/m²"]],
    ["Solar radiation", ["123 W/m² · Open-Meteo", "123 W/m²"]],
    ["Solar radiation", ["0 W/m² · Open-Meteo", "0 W/m²"]],
    ["Solar radiation", ["123 W/m² · weather forecast", "123 W/m²"]],
    ["Solar radiation", ["1000 W/m² · weather forecast", "1000 W/m²"]],
    ["Solinstrålning", ["1000 W/m² · väderprognos", "1000 W/m²"]],
    ["Solinstrålning", ["1000 W/m² · Open-Meteo", "1000 W/m²"]],
    ["Solar radiation", ["(not configured)"]],
    ["Outdoor temperature", ["unavailable"]],
    ["Lower floor temperature", ["21.3 °C"]],
    ["Buffer tank temperature", ["47.5 °C"]],
    ["Valve target", ["1000 W/m² · Open-Meteo", "1000 W/m²"]],
    ["Hot water temperature",
      ["a sensor whose state is a whole sentence about the weather"]],
  ];
  const collisions = [];
  const cutReadings = [];
  const rows = [];
  for (const [label, alts] of cases) {
    const f = fit(label, alts);
    const lw = w(f.label, false);
    const vw = w(f.value, true);
    rows.push(`${JSON.stringify(label)} + ${JSON.stringify(alts[0])} -> ` +
      `${lw.toFixed(1)}+${vw.toFixed(1)}=${(lw + vw).toFixed(1)}/${INNER}`);
    if (lw + vw + GAP > INNER + 1e-9) {
      collisions.push(`${label} | ${f.label} + ${f.value} = ` +
        `${(lw + vw).toFixed(2)} > ${INNER - GAP}`);
    }
    // The reading itself is never cut. Whatever spelling the row settles
    // on must still open with the same number the longest one did.
    const num = /^[\d.]+/.exec(alts[0]);
    if (num && !f.value.startsWith(num[0])) {
      cutReadings.push(`${alts[0]} -> ${f.value}`);
    }
  }
  check("no slot row's label and value can overlap, at any real length",
    collisions.length === 0, collisions.join("; ") || rows.join("\n    "));
  check("and the reading itself is never what gets cut",
    cutReadings.length === 0, cutReadings.join("; "));

  // The specific report: the longest fallback the card can write, beside
  // the label it shares its row with.
  const worst = fit("Solar radiation",
    ["1000 W/m² · weather forecast", "1000 W/m²"]);
  const worstL = w(worst.label, false);
  const worstV = w(worst.value, true);
  check("the longest real solar value leaves the label whole and legible",
    worst.label === "Solar radiation" && worstL >= MINLABEL &&
    worst.value === "1000 W/m²" && worst.shortened === true &&
    worstL + worstV + GAP <= INNER,
    `label ${JSON.stringify(worst.label)} (${worstL.toFixed(2)}u, minimum ` +
    `${MINLABEL}) + value ${JSON.stringify(worst.value)} ` +
    `(${worstV.toFixed(2)}u) = ${(worstL + worstV).toFixed(2)}u of ` +
    `${INNER}, ${(INNER - worstL - worstV).toFixed(2)}u to spare`);
  // ...and the tag it dropped is still reachable, so nothing is lost.
  check("the dropped provenance tag is kept for the tooltip",
    worst.full === "1000 W/m² · weather forecast", worst.full);

  // The old rule, priced with the same metrics, on the same strings: this
  // is the collision the owner reported, in viewBox units. The old row was
  // 180 units wide (x+10 to x+190).
  const oldRow = (label, value) => {
    const room = value.length > 10 ? 15 : 19;
    const lab = label.length > room ? label.slice(0, room - 1) + "…" : label;
    return w(lab, false) + w(value, true) - 180;
  };
  const oldOverlaps = [
    ["Solar radiation", "1000 W/m² · Open-Meteo"],
    ["Solar radiation", "123 W/m² · Open-Meteo"],
    ["Solar radiation", "1000 W/m² · weather forecast"],
    ["Solinstrålning", "1000 W/m² · väderprognos"],
  ].map(([l, v]) => `${JSON.stringify(v)} overran by ` +
    `${oldRow(l, v).toFixed(2)}u`);
  check("the rule this replaced really did overlap on these very strings",
    oldRow("Solar radiation", "1000 W/m² · Open-Meteo") > 40 &&
    oldRow("Solar radiation", "123 W/m² · Open-Meteo") > 30 &&
    oldRow("Solar radiation", "1000 W/m² · weather forecast") > 60 &&
    oldRow("Solinstrålning", "1000 W/m² · väderprognos") > 40,
    oldOverlaps.join("; "));

  // A short label keeps a long value whole: the label only ever asks for
  // the room it actually needs, so the tag is not dropped out of habit.
  // (At 138.65u the tag is a near thing -- "Sun" reserves 21.6u and the row
  // has 138.4u to give -- which is exactly why this is measured and not
  // counted.)
  const roomy = fit("Sun", ["0 W/m² · Open-Meteo", "0 W/m²"]);
  check("a short label lets the value keep its source tag",
    roomy.label === "Sun" && roomy.value === "0 W/m² · Open-Meteo" &&
    roomy.shortened === false &&
    w(roomy.label, false) + w(roomy.value, true) + GAP <= INNER,
    `${JSON.stringify(roomy.label)} + ${JSON.stringify(roomy.value)} = ` +
    `${(w(roomy.label, false) + w(roomy.value, true)).toFixed(2)}u`);
  // The invariant behind that: a shorter label never costs the value room.
  const alts = ["123 W/m² · Open-Meteo", "123 W/m²"];
  const short = fit("Sun", alts);
  const long = fit("Solar radiation", alts);
  check("a shorter label never buys the value less room",
    w(short.value, true) >= w(long.value, true),
    `"Sun" keeps ${JSON.stringify(short.value)}, ` +
    `"Solar radiation" keeps ${JSON.stringify(long.value)}`);
  // An ellipsis is only ever spent when it buys something, and it never
  // leaves a dangling separator behind it.
  check("a label that fits is left exactly alone",
    fit("Valve target", ["21.3 °C"]).label === "Valve target" &&
    !/[\s·-]…$/.test(fit("Lower floor temperature", ["21.3 °C"]).label),
    fit("Lower floor temperature", ["21.3 °C"]).label);

  // ...and the whole thing again on the real drawing, which is where the
  // report came from: a solar slot with no probe, falling back to
  // Open-Meteo, rendered beside its label.
  const solarTopo = setupTopo();
  solarTopo.slots = solarTopo.slots.concat([{
    key: "solar_radiation_entity", label: "Solar radiation",
    place: "outdoor", entity: null, domains: SETUP_TEMP }]);
  // The harness already publishes an Open-Meteo irradiance sensor; drive it
  // to the widest reading the fallback can ever print.
  const solarStates = {};
  solarStates[SOLAR_ID] = {
    state: "1000",
    attributes: { forecast: solarForecast, source: "open_meteo",
      friendly_name: "Solar Irradiance", plan_kind: "solar",
      unit_of_measurement: "W/m²" },
  };
  const page = setupPage(solarTopo, solarStates);
  const row = new RegExp(
    '<text class="setup-slot[^"]*" x="([\\d.]+)" y="[\\d.]+">\\s*' +
    '<tspan>([^<]*)</tspan>\\s*<tspan class="setup-value" x="([\\d.]+)"\\s*' +
    'text-anchor="end">([^<]*)</tspan></text>\\s*' +
    '<rect class="setup-hit" data-key="solar_radiation_entity"[^>]*' +
    'aria-label="([^"]*)"').exec(page);
  check("the drawing really does fall back to Open-Meteo for irradiance",
    !!row && /W\/m²/.test(row[4]), row ? row[4] : "no solar row drawn");
  if (row) {
    const labelX = Number(row[1]);
    const valueEnd = Number(row[3]);
    const lw = w(row[2], false);
    const vw = w(row[4], true);
    check("on the page, the solar label ends before its value begins",
      labelX + lw <= valueEnd - vw,
      `label ${JSON.stringify(row[2])} runs x${labelX}..` +
      `${(labelX + lw).toFixed(2)}; value ${JSON.stringify(row[4])} runs ` +
      `x${(valueEnd - vw).toFixed(2)}..${valueEnd}; ` +
      `${(valueEnd - vw - labelX - lw).toFixed(2)}u between them`);
    check("the label is the whole label, not a truncation",
      row[2] === "Solar radiation", row[2]);
    // Nothing is lost by shortening: the row's accessible name and tooltip
    // still carry the reading with its provenance.
    check("and the row still says where the number came from, out loud",
      /1000 W\/m² · Open-Meteo/.test(row[5]) && row[4] === "1000 W/m²",
      `drawn ${JSON.stringify(row[4])}, spoken ${JSON.stringify(row[5])}`);
  }
}

// --- Scenario: the entity picker stops destroying assignments (item E) ------
// Three faults, and the first two combined into a data-loss bug rather than
// an inconvenience:
//
//  - The slot's own entity was offered only if it happened to fall inside
//    the candidate list. When it did not, the `<select>` fell back to
//    "(not configured)" -- so a configured slot was SHOWN as empty, and
//    pressing Assign wrote that emptiness and reloaded the integration.
//  - PICKER_MAX_OPTIONS truncated the alphabetical candidate list, so on a
//    large install the user's own probe was simply not in the list, with no
//    way to reach it. That is the case above, on every install big enough.
//  - Options were friendly names only. The reporter's two wood-tank probes
//    are both called "Vedpanna temperatur"; one of them is silently
//    `..._2`. A list of identical labels is a list nobody can choose from.
{
  const MAX = vm.runInContext("PICKER_MAX_OPTIONS", ctx);
  // Parse a rendered picker into something to assert against.
  const pickerOf = (card) => {
    const page = collect(card.shadowRoot).join("\n");
    const html = (/<div class="setup-picker">[\s\S]*?<\/div>\s*$/m
      .exec(page) || [page])[0];
    const options = [...page.matchAll(
      /<option value="([^"]*)"( selected)?>([^<]*)<\/option>/g)]
      .map((m) => ({ value: m[1], selected: !!m[2], text: m[3] }));
    const note = (/<div class="sp-note">([^<]*)<\/div>/.exec(page) || [])[1];
    return { html, options, note,
      selected: options.filter((o) => o.selected) };
  };
  const openPicker = (card, key, viaKeyboard) => {
    const hit = card.shadowRoot.querySelectorAll(".setup-hit")
      .find((h) => h.dataset.key === key);
    if (!hit) return null;
    if (viaKeyboard) {
      (hit._listeners.keydown || []).forEach((f) => f({ key: "Enter",
        currentTarget: hit, preventDefault() {}, stopPropagation() {} }));
    } else {
      (hit._listeners.click || []).forEach((f) => f({ currentTarget: hit,
        preventDefault() {}, stopPropagation() {} }));
    }
    return card.shadowRoot.querySelector(".setup-picker");
  };
  const clickBtn = async (card, sel) => {
    const b = card.shadowRoot.querySelector(sel);
    if (!b) return;
    await Promise.all((b._listeners.click || [])
      .map((f) => f({ stopPropagation() {}, preventDefault() {} })));
  };
  const typeFilter = (card, text) => {
    const box = card.shadowRoot.querySelector(".sp-filter");
    box.value = text;
    (box._listeners.input || []).forEach((f) =>
      f({ currentTarget: box, target: box }));
  };
  const chooseInSelect = (card, value) => {
    const sel = card.shadowRoot.querySelector(".sp-select");
    sel.value = value;
    (sel._listeners.change || []).forEach((f) =>
      f({ currentTarget: sel, target: sel }));
  };

  // A big install: 400 sensors whose names give nothing away, plus the two
  // wood-tank probes the report is actually about -- identical friendly
  // names, distinguishable only by their ids.
  const bigStates = {};
  for (let i = 0; i < 400; i++) {
    bigStates[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = {
      state: "20.0",
      attributes: { unit_of_measurement: "°C",
        friendly_name: `Probe ${String(i).padStart(3, "0")}` },
    };
  }
  bigStates["sensor.vedpanna_temperatur_temperature"] = {
    state: "71.2", attributes: { unit_of_measurement: "°C",
      friendly_name: "Vedpanna temperatur" } };
  bigStates["sensor.vedpanna_temperatur_temperature_2"] = {
    state: "48.9", attributes: { unit_of_measurement: "°C",
      friendly_name: "Vedpanna temperatur" } };

  // (a) A slot that HAS an entity shows it, and shows it selected -- even
  //     when the install is far too big for it to survive the render cap.
  const assignedTopo = setupTopo();
  assignedTopo.slots = assignedTopo.slots.map((s) =>
    s.key === "wood_tank_top_entity"
      ? { ...s, entity: "sensor.vedpanna_temperatur_temperature_2" }
      : s);
  const big = mkSetup(assignedTopo, bigStates);
  openPicker(big, "wood_tank_top_entity");
  const p1 = pickerOf(big);
  const mine = p1.options.find((o) =>
    o.value === "sensor.vedpanna_temperatur_temperature_2");
  check("a slot's own entity is offered even on an install past the cap",
    !!mine, `${p1.options.length} options rendered, cap ${MAX}`);
  check("and it is the option the picker comes up on",
    !!mine && mine.selected && p1.selected.length === 1 &&
    p1.selected[0].value === "sensor.vedpanna_temperatur_temperature_2",
    `selected: ${JSON.stringify(p1.selected)}`);
  check("so the placeholder is NOT what a configured slot shows",
    !p1.options.some((o) => o.value === "" && o.selected),
    JSON.stringify(p1.options.filter((o) => o.value === "")));
  // The bug's payload: pressing Assign on an untouched picker must not
  // write a clearance. It writes the entity that is already there, if it
  // writes anything at all.
  const calls = [];
  big._hass.callService = async (d, s2, data) => { calls.push([d, s2, data]); };
  await clickBtn(big, ".sp-save");
  check("Assign on an untouched configured slot never clears it",
    calls.length === 1 &&
    calls[0][2].entity_id === "sensor.vedpanna_temperatur_temperature_2",
    JSON.stringify(calls));

  // ...and every option carries its entity id, because the two probes this
  // report is about are indistinguishable without it.
  const twins = p1.options.filter((o) => /vedpanna/.test(o.value));
  check("every option shows its entity id next to the friendly name",
    p1.options.filter((o) => o.value).every((o) => o.text.includes(o.value)),
    p1.options.filter((o) => o.value && !o.text.includes(o.value))
      .slice(0, 3).map((o) => `${o.value} -> ${o.text}`).join("; "));
  check("so the two identically-named wood-tank probes are tellable apart",
    twins.length === 2 && twins[0].text !== twins[1].text &&
    twins.every((o) => /Vedpanna temperatur/.test(o.text)),
    twins.map((o) => o.text).join(" | "));

  // (b) Filtering. The cap is a RENDER bound applied after the filter, so
  //     anything on the install is reachable by typing, and the footnote
  //     says so while the list is standing on more than it shows.
  const fresh = mkSetup(setupTopo(), bigStates);
  openPicker(fresh, "wood_tank_top_entity");
  const p2 = pickerOf(fresh);
  const listed = p2.options.filter((o) => o.value).length;
  check("a big install's list is capped rather than built in full",
    listed === MAX, `${listed} options for 400+ candidates, cap ${MAX}`);
  check("and the footnote says what it is standing on",
    /showing 200 of 40\d/i.test(p2.note || "") ||
    /200 of 40\d/.test(p2.note || ""),
    p2.note);
  // The probe the reporter could not reach: past the cap alphabetically,
  // and found by typing part of its name.
  const reachable = (q) => {
    typeFilter(fresh, q);
    const opts = [...fresh.shadowRoot.querySelector(".sp-select").innerHTML
      .matchAll(/<option value="([^"]*)"/g)].map((m) => m[1]);
    return opts;
  };
  const byName = reachable("vedpanna");
  check("typing part of a friendly name reaches an entity past the cap",
    byName.includes("sensor.vedpanna_temperatur_temperature") &&
    byName.includes("sensor.vedpanna_temperatur_temperature_2"),
    `${byName.length} options: ${byName.slice(0, 4).join(", ")}`);
  const byId = reachable("TEMPERATURE_2");
  check("and typing part of an entity id does too, case-insensitively",
    byId.includes("sensor.vedpanna_temperatur_temperature_2"),
    `${byId.length} options: ${byId.slice(0, 4).join(", ")}`);
  const deep = reachable("probe 387");
  check("an entity 387 places down the alphabet is one search away",
    deep.includes("sensor.zz_probe_387"),
    `${deep.length} options: ${deep.slice(0, 4).join(", ")}`);
  // A filter that matches nothing says so rather than showing an empty box.
  typeFilter(fresh, "no such sensor anywhere");
  const emptyNote = fresh.shadowRoot.querySelector(".sp-note");
  check("a filter that matches nothing says so",
    /nothing matches/i.test(emptyNote.textContent || ""),
    emptyNote.textContent);
  // Narrowing below the cap drops the truncation notice.
  typeFilter(fresh, "vedpanna");
  check("and once the list fits, the footnote stops warning about the cap",
    !/\bof 40\d/.test(
      fresh.shadowRoot.querySelector(".sp-note").textContent || ""),
    fresh.shadowRoot.querySelector(".sp-note").textContent);

  // (c) A clearing Assign is confirmed, the way the what-if save is.
  const clearing = mkSetup(assignedTopo, bigStates);
  const clearCalls = [];
  clearing._hass.callService = async (d, s2, data) => {
    clearCalls.push([d, s2, data]);
  };
  openPicker(clearing, "wood_tank_top_entity");
  chooseInSelect(clearing, "");
  await clickBtn(clearing, ".sp-save");
  const saveBtn = clearing.shadowRoot.querySelector(".sp-save");
  check("choosing (not configured) does not clear the slot on one click",
    clearCalls.length === 0 && clearing._pendingClear === true,
    JSON.stringify(clearCalls));
  check("the button says what the second click will do",
    /confirm/i.test(saveBtn.textContent || "") &&
    saveBtn.classList.contains("confirm"),
    `${JSON.stringify(saveBtn.textContent)} ` +
    `class=${saveBtn.className}`);
  check("and the warning names the entity that would be lost",
    /vedpanna_temperatur_temperature_2/.test(clearing._setupNote || ""),
    clearing._setupNote);
  await clickBtn(clearing, ".sp-save");
  check("a second, deliberate click does clear it",
    clearCalls.length === 1 && clearCalls[0][1] === "assign_entity" &&
    clearCalls[0][2].entity_id === "" &&
    clearCalls[0][2].key === "wood_tank_top_entity",
    JSON.stringify(clearCalls));
  // Clearing a slot that was already empty is not destructive and is not
  // made to feel like it.
  const emptySlot = mkSetup(setupTopo(), bigStates);
  const emptyCalls = [];
  emptySlot._hass.callService = async (d, s2, data) => {
    emptyCalls.push([d, s2, data]);
  };
  openPicker(emptySlot, "wood_tank_top_entity");
  chooseInSelect(emptySlot, "");
  await clickBtn(emptySlot, ".sp-save");
  check("an empty slot does not demand confirmation to stay empty",
    emptyCalls.length === 1 && emptyCalls[0][2].entity_id === "",
    JSON.stringify(emptyCalls));
  // Changing your mind disarms it, so the armed state cannot be inherited
  // by a different answer.
  const rearm = mkSetup(assignedTopo, bigStates);
  rearm._hass.callService = async () => {};
  openPicker(rearm, "wood_tank_top_entity");
  chooseInSelect(rearm, "");
  await clickBtn(rearm, ".sp-save");
  chooseInSelect(rearm, "sensor.vedpanna_temperatur_temperature");
  check("picking something else disarms the clear",
    rearm._pendingClear === false &&
    !rearm.shadowRoot.querySelector(".sp-save").classList.contains("confirm"),
    `pendingClear=${rearm._pendingClear}`);
  // Leaving the picker drops the arming with it.
  const leave = mkSetup(assignedTopo, bigStates);
  leave._hass.callService = async () => {};
  openPicker(leave, "wood_tank_top_entity");
  chooseInSelect(leave, "");
  await clickBtn(leave, ".sp-save");
  await clickBtn(leave, ".sp-cancel");
  check("and cancelling out of the picker disarms it too",
    leave._pendingClear === false && leave._pickerKey === null &&
    leave._pickerFilter === "" && leave._pickerChoice === null,
    `pendingClear=${leave._pendingClear} key=${leave._pickerKey} ` +
    `filter=${JSON.stringify(leave._pickerFilter)}`);

  // Keyboard access has to survive all of that.
  const kb = mkSetup(assignedTopo, bigStates);
  check("Enter on a row still opens the picker",
    !!openPicker(kb, "wood_tank_top_entity", true));
  const kbPicker = kb.shadowRoot.querySelector(".setup-picker");
  (kbPicker._listeners.keydown || []).forEach((f) =>
    f({ key: "Escape", stopPropagation() {} }));
  check("Escape still closes it without assigning",
    !kb.shadowRoot.querySelector(".setup-picker") && kb._pickerKey === null);
  check("and still hands focus back to the row it came from",
    !!document.activeElement &&
    document.activeElement.classList.contains("setup-hit") &&
    document.activeElement.dataset.key === "wood_tank_top_entity",
    document.activeElement && document.activeElement.className);
  // The filter is a labelled control, not an unexplained box.
  const kb2 = mkSetup(assignedTopo, bigStates);
  openPicker(kb2, "wood_tank_top_entity", true);
  const filterBox = kb2.shadowRoot.querySelector(".sp-filter");
  check("the filter box says out loud what it filters",
    !!filterBox && /wood tank top/i.test(filterBox["aria-label"] || "") &&
    !!filterBox.placeholder,
    filterBox && `${filterBox["aria-label"]} / ${filterBox.placeholder}`);
}

// --- Scenario: no focus ring is left behind by a mouse (item F) -------------
// Click a sensor field, click Cancel, click elsewhere: "a thin blue line
// remains at the left and above the sensor field". The rows have been
// focusable buttons since v4.2.0, and Cancel handed focus back to the row
// whether or not the person wanted it there -- so a mouse user was left
// holding focus on a field they had just backed out of, ringed by an
// `outline` that the row's own geometry clipped down to two edges.
//
// Fixed by keeping the ring (keyboard users need it) and fixing everything
// around it: focus goes back to the row only when the keyboard sent it
// there, any pointer gesture off a row drops it, and the ring is stroked
// onto the rect -- part of the drawing, so nothing can clip it -- inside a
// rect inset far enough for all four sides to show.
{
  const hitFor = (card, key) => card.shadowRoot.querySelectorAll(".setup-hit")
    .find((h) => h.dataset.key === key);
  const openBy = (card, key, viaKeyboard) => {
    const hit = hitFor(card, key);
    // A real pointer press focuses what it presses; the keyboard path
    // arrives on an already-focused row.
    hit.focus();
    if (viaKeyboard) {
      (hit._listeners.keydown || []).forEach((f) => f({ key: "Enter",
        currentTarget: hit, preventDefault() {}, stopPropagation() {} }));
    } else {
      (hit._listeners.click || []).forEach((f) => f({ currentTarget: hit,
        preventDefault() {}, stopPropagation() {} }));
    }
  };
  const cancel = (card) => {
    const b = card.shadowRoot.querySelector(".sp-cancel");
    (b._listeners.click || []).forEach((f) =>
      f({ stopPropagation() {}, preventDefault() {} }));
  };
  const focusedRow = () => {
    const a = document.activeElement;
    return a && a.classList && a.classList.contains("setup-hit")
      ? a.dataset.key : null;
  };
  // A pointer press somewhere in the dialog that is not a row. The card
  // parks the listener on the dialog, which is the root `_attachSetupEvents`
  // is handed.
  const clickElsewhere = (card, target) => {
    const dlg = card.shadowRoot.querySelector("dialog");
    ((dlg && dlg._listeners.pointerdown) || []).forEach((f) =>
      f({ target: target || new Node("div") }));
  };

  // The reported sequence, with a mouse throughout.
  const mouse = mkSetup();
  openBy(mouse, "indoor_temp_entity", false);
  check("a mouse click on a row opens the picker",
    !!mouse.shadowRoot.querySelector(".setup-picker"));
  cancel(mouse);
  check("Cancel does not hand the row back to a mouse user",
    focusedRow() === null,
    `focus is on ${focusedRow() || (document.activeElement || {}).tagName}`);
  // Put focus back on the row by hand first, so this is a real test of the
  // click and not of the line above it.
  hitFor(mouse, "indoor_temp_entity").focus();
  clickElsewhere(mouse);
  check("and clicking elsewhere afterwards leaves no row focused",
    focusedRow() === null, `focus is on ${focusedRow()}`);
  // The listener that does it is parked once per render, not once per
  // render since the dialog opened.
  const before = mouse.shadowRoot.querySelector("dialog")
    ._listeners.pointerdown.length;
  mouse._sig = null;
  mouse._maybeRender(true);
  const after = mouse.shadowRoot.querySelector("dialog")
    ._listeners.pointerdown.length;
  check("and re-rendering does not stack another copy of it",
    after === before, `${before} listeners before a re-render, ${after} after`);

  // The keyboard path is the one the ring exists for, and it is unchanged.
  const keys = mkSetup();
  openBy(keys, "indoor_temp_entity", true);
  check("Enter on a row opens the picker",
    !!keys.shadowRoot.querySelector(".setup-picker"));
  cancel(keys);
  check("Cancel does return the row to a keyboard user",
    focusedRow() === "indoor_temp_entity",
    `focus is on ${focusedRow()}`);
  // ...and Escape, the other way out, still does the same.
  const esc = mkSetup();
  openBy(esc, "buffer_tank_temp_entity", true);
  const pk = esc.shadowRoot.querySelector(".setup-picker");
  (pk._listeners.keydown || []).forEach((f) =>
    f({ key: "Escape", stopPropagation() {} }));
  check("Escape returns it too",
    focusedRow() === "buffer_tank_temp_entity", `focus is on ${focusedRow()}`);
  // A row a keyboard user is deliberately sitting on is not stolen from
  // them by an unrelated pointer gesture on that same row.
  const kept = mkSetup();
  hitFor(kept, "indoor_temp_entity").focus();
  clickElsewhere(kept, hitFor(kept, "indoor_temp_entity"));
  check("a pointer press on the row itself does not drop its focus",
    focusedRow() === "indoor_temp_entity", `focus is on ${focusedRow()}`);
  clickElsewhere(kept);
  check("but a pointer press anywhere else does",
    focusedRow() === null, `focus is on ${focusedRow()}`);

  // The ring itself: kept, and kept visible.
  check("the ring is still there for keyboard users",
    /\.setup-hit:focus-visible \{/.test(cardSrc),
    "no :focus-visible rule for setup rows");
  check("it is not painted with an outline that geometry can clip",
    /\.setup-hit:focus-visible \{[^}]*outline:\s*none/.test(cardSrc) &&
    /\.setup-hit:focus-visible \{[^}]*stroke:/.test(cardSrc) &&
    /\.setup-hit:focus-visible \{[^}]*stroke-width:\s*2/.test(cardSrc),
    (/\.setup-hit:focus-visible \{[^}]*\}/.exec(cardSrc) || [])[0]);
  check("and it is :focus-visible, so a mouse click cannot leave one",
    !/\.setup-hit:focus(?![-\w])/.test(cardSrc),
    "a bare :focus rule on .setup-hit would ring mouse clicks too");
  // Hover and focus-visible have equal specificity, so a hover rule using
  // element opacity would fade the ring on the row under the pointer.
  check("hovering a focused row does not fade its ring",
    /\.setup-hit:hover \{[^}]*fill-opacity/.test(cardSrc) &&
    !/\.setup-hit:hover \{[^}]*[^-]opacity:\s*0\.12/.test(cardSrc),
    (/\.setup-hit:hover \{[^}]*\}/.exec(cardSrc) || [])[0]);
  // Nobody's outline was hidden wholesale to make the report go away.
  check("no blanket outline suppression was added",
    !/outline:\s*none[^;]*;\s*\}\s*\/\* *hide/i.test(cardSrc) &&
    /\.slot:focus-visible, \.lane:focus-visible \{[\s\S]{0,80}outline: 2px solid/
      .test(cardSrc),
    "the other focusable SVG parts keep their outlines");

  // Geometry: at stroke-width 2 centred on the path the ring reaches one
  // unit outside the rect, and must still clear the contour and the rows
  // above and below -- otherwise it is clipped again, differently.
  const geoCard = mkSetup();
  const page = collect(geoCard.shadowRoot).join("\n");
  const rects = [...page.matchAll(
    /<rect class="setup-hit" data-key="([^"]+)"[^>]*?x="([\d.]+)" y="([\d.]+)"\s*width="([\d.]+)"\s*height="([\d.]+)"/g)]
    .map((m) => ({ key: m[1], x: +m[2], y: +m[3], w: +m[4], h: +m[5] }));
  const boxes = geoCard._layoutBoxes || [];
  const clipped = [];
  for (const r of rects) {
    const b = boxes.find((bb) => r.x > bb.x && r.x < bb.x + bb.w &&
      r.y > bb.y && r.y < bb.y + bb.h);
    if (!b) { clipped.push(`${r.key}: no box`); continue; }
    // 1 unit of ring on every side, against the contour at x+2 / x+w-2 and
    // the box's own top and bottom.
    if (r.x - 1 < b.x + 2) clipped.push(`${r.key}: left ${r.x - 1} < ${b.x + 2}`);
    if (r.x + r.w + 1 > b.x + b.w - 2) {
      clipped.push(`${r.key}: right ${r.x + r.w + 1} > ${b.x + b.w - 2}`);
    }
    if (r.y - 1 < b.y) clipped.push(`${r.key}: top ${r.y - 1} < ${b.y}`);
    if (r.y + r.h + 1 > b.y + b.h) {
      clipped.push(`${r.key}: bottom ${r.y + r.h + 1} > ${b.y + b.h}`);
    }
  }
  check("the ring has room for all four of its sides inside the box",
    clipped.length === 0, clipped.join("; "));
  // Two rings on adjacent rows must not merge into one smear.
  const merged = [];
  const byCol = {};
  for (const r of rects) (byCol[r.x] ||= []).push(r);
  for (const list of Object.values(byCol)) {
    const sorted = list.slice().sort((a, b) => a.y - b.y);
    for (let i = 1; i < sorted.length; i++) {
      const gap = sorted[i].y - (sorted[i - 1].y + sorted[i - 1].h) - 2;
      if (gap < 0) merged.push(`${sorted[i - 1].key}/${sorted[i].key} ${gap}`);
    }
  }
  check("and two neighbouring rings never touch each other",
    merged.length === 0, merged.join(", "));
}


// --- Scenario: tooltip prose wraps, and the box stays on the chart ---------
//
// `.tooltip` sets `white-space: nowrap`, which is right for the value rows
// ("House temperature: 22 °C" must not break) and wrong for everything else
// in the box. `.tt-shared` carried a `max-width: 180px` that could never take
// effect, because nowrap was never overridden on it: the ~110-character
// shared-step sentence rendered as one unbroken line roughly 500 px wide and
// spilled straight out of the box. `.tt-reason` is prose too and had no width
// bound at all.
//
// STRUCTURAL PIN, not a rendered-overflow test. This DOM stub has no layout
// engine: there is no box model, no text measurement and no `offsetWidth`, so
// nothing here can observe an overflow. What it can pin is the rule that
// prevents one — every prose block inside the tooltip declares
// `white-space: normal` and a `max-width`, and none is left inheriting nowrap.
// A future prose block added without those two declarations is caught; a
// declared max-width that is simply too narrow for its content is NOT, and
// neither is a real overflow arising from anything other than these rules.
{
  const styleOf = (cls) => {
    const re = new RegExp(
      "\\.tooltip \\." + cls + "\\s*\\{([\\s\\S]*?)\\}", "m"
    );
    const m = cardSrc.match(re);
    return m ? m[1] : null;
  };
  // Every block the tooltip builder emits, and whether it is prose.
  const PROSE = ["tt-shared", "tt-reason"];
  const VALUES = ["tt-row", "tt-time"];

  check("the tooltip itself still keeps short value rows on one line",
    /\.tooltip \{[\s\S]*?white-space:\s*nowrap[\s\S]*?\}/.test(cardSrc));
  for (const cls of PROSE) {
    const css = styleOf(cls);
    check(`${cls} declares a style block at all`, css !== null);
    check(`${cls} wraps instead of inheriting nowrap`,
      css !== null && /white-space:\s*normal/.test(css), css);
    check(`${cls} bounds its own width`,
      css !== null && /max-width:\s*\d/.test(css), css);
  }
  for (const cls of VALUES) {
    const css = styleOf(cls);
    check(`${cls} is left on one line, which is what nowrap is for`,
      css === null || !/white-space:\s*normal/.test(css), css);
  }
  // Every class the tooltip HTML emits must be one of the two lists above, so
  // a new prose block cannot be added without deciding which it is.
  const emitted = new Set(
    [...cardSrc.matchAll(/<div class="(tt-[\w-]+)"/g)].map((m) => m[1])
  );
  check("every tooltip block is classified as prose or as a value row",
    [...emitted].every((c) => PROSE.includes(c) || VALUES.includes(c)),
    [...emitted].join(", "));

  // The competing hypothesis, and a real second defect: placement clamped
  // only the LEFT edge (`Math.max(0, place)`) and flipped the box left of the
  // pointer past 60 % of the width assuming a 160 px box. A wider box near the
  // right-hand edge ran off the chart whether or not its text wrapped.
  const posCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  const rect = { width: 900, left: 0, top: 0 };
  // The stub has no layout, so `offsetWidth` is supplied by hand: this is the
  // one number the placement needs and the only thing standing in for layout.
  const TT_W = 420;
  const ttNode = posCard.shadowRoot.querySelector(".tooltip");
  ttNode.offsetWidth = TT_W;
  const place = (clientX) => {
    posCard._onPointerMove({
      clientX,
      currentTarget: { getBoundingClientRect: () => rect },
    });
    return parseFloat(ttNode.style.left);
  };
  // Inside the plot area: the pointer handler ignores anything outside it, so
  // these have to be plot coordinates, not card ones.
  const atRightEdge = place(830);
  check("the tooltip never starts past the chart's right edge",
    atRightEdge + TT_W <= rect.width,
    `left ${atRightEdge} + ${TT_W} > ${rect.width}`);
  check("and never starts left of the chart", place(95) >= 0,
    `left ${place(95)}`);
  check("a pointer in the middle still places it beside the crosshair",
    place(300) > 0 && place(300) + TT_W <= rect.width, `left ${place(300)}`);
}

// --- Scenario: the zone traces are named, in one legend entry ------------
//
// The house-temperature series draws `room` solid and `upper`/`lower` dashed
// in one colour. Until v5.1.7 all three shared one legend chip and one label,
// and the tooltip reported `s.lines.find(l => l.primary)` — the ROOM value —
// for whichever line the pointer was over. A two-zone house whose downstairs
// trace sat at 28 °C therefore hovered as 21 °C, which is how a display defect
// reads as the optimizer overheating the house.
//
// v5.1.7 named every trace in both places at once, which put three chips in
// the legend under one colour. They all carry the series' data-key — the only
// granularity the visibility model has — so clicking any of them toggled all
// three lines together, and the owner reported three legend entries that
// resolve to one line. The naming belongs in the tooltip, which points at the
// trace under the pointer; the legend gets one entry per series.
{
  const twoZone = (opts) => {
    const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    // Same timestamps, three genuinely different temperatures.
    st[DEFAULT_SPACE].attributes.forecast =
      plan.space_plan.forecast.map((p) => ({
        ...p,
        // Whole degrees apart: the chart formats anything at or above 10
        // with `toFixed(0)`, so smaller gaps would render identically and the
        // "own value" check below would pass on a coincidence.
        room: 22.0,
        upper: 20.0,
        lower: 28.0,
      }));
    if (opts && opts.topology) {
      st[DEFAULT_SPACE].attributes.setup_topology = {
        slots: [
          { key: "indoor_temp_entity", entity: "sensor.indoor" },
          { key: "lower_floor_temp_entity", entity: opts.lowerEntity || null },
        ],
      };
    }
    return st;
  };

  // Just the chips: the legend div ends at the first </div>, and nothing
  // inside a chip is one. Slicing rather than regex-matching keeps unrelated
  // markup (which may legitimately contain the word "modelled") out of the
  // labelling assertions below.
  const legendOf = (dump) => {
    const i = dump.indexOf('<div class="legend">');
    if (i < 0) return "";
    const end = dump.indexOf("</div>", i);
    return dump.slice(i, end < 0 ? undefined : end);
  };
  /** The `title` of one series' legend chip: what the chip claims beyond
   * its visible name. One chip per series, so one title per key. */
  const titleOf = (lg, key) => {
    const m = lg.match(new RegExp(`data-key="${key}" title="([^"]*)"`));
    return m ? m[1] : "";
  };
  const chipsFor = (lg, key) =>
    (lg.match(new RegExp(`<button[^>]*data-key="${key}"`, "g")) || []).length;
  const zc = build(twoZone());
  const zdump = collect(zc.shadowRoot).join("\n");
  const zlegend = legendOf(zdump);

  // The regression the owner reported. Three lines are drawn — the count
  // below proves the drop rule kept all three — and the legend still gets
  // exactly one entry for them, because one chip is all the visibility model
  // can act on.
  const zlines = zc._series.find((s) => s.key === "house_temp").lines;
  check("a two-zone house draws all three house-temperature traces",
    zlines.length === 3 &&
    zlines.map((l) => l.field).join(",") === "room,upper,lower",
    JSON.stringify(zlines.map((l) => l.field)));
  check("a multi-line series gets one legend entry, not one per line",
    chipsFor(zlegend, "house_temp") === 1, zlegend);
  check("and the zone names are not chips of their own",
    !/>\s*Upper floor/.test(zlegend) && !/>\s*Lower floor/.test(zlegend),
    zlegend);
  // Every other series keeps exactly one chip too, so the count above is not
  // passing because the legend lost entries wholesale.
  check("the legend still carries one chip per series",
    (zlegend.match(/<button[^>]*data-key=/g) || []).length === 7, zlegend);
  check("the one chip still says what else rides on its line",
    /also drawn: Upper floor, Lower floor/.test(zlegend), zlegend);

  // Hover: three rows, each with its own name and its OWN value. This is
  // where the disambiguation lives now, and it is the half of v5.1.7 the
  // owner did not ask to lose.
  const hovered = (card) => {
    card._onPointerMove({
      clientX: 450,
      currentTarget: {
        getBoundingClientRect: () => ({ width: 900, left: 0, top: 0 }),
      },
    });
    const tt = card.shadowRoot.querySelector(".tooltip");
    return tt ? tt.innerHTML : "";
  };
  const tip = hovered(zc);
  check("the tooltip names all three house-temperature traces",
    /House temperature/.test(tip) && /Upper floor/.test(tip) &&
    /Lower floor/.test(tip), tip);
  check("and reports each trace's own value, not the room's three times",
    /House temperature: 22 °C/.test(tip) &&
    /Upper floor: 20 °C/.test(tip) &&
    /Lower floor: 28 °C/.test(tip), tip);
  // One row per rendered line, with no two rows sharing a label: a tooltip
  // that lost a row, or repeated one, is the pre-v5.1.7 defect coming back.
  const ttRows = (tt) =>
    (tt.match(/<div class="tt-row">.*?<\/div>/g) || []).map((r) =>
      parseHtml(r, (t) => new Node(t))[0].textContent.split(":")[0].trim()
    );
  const zoneRows = ttRows(tip).filter((l) => /floor|House temperature/i.test(l));
  check("the tooltip carries one row per drawn trace, all distinctly labelled",
    zoneRows.length === 3 && new Set(zoneRows).size === 3, zoneRows.join(" | "));
  check("a dashed trace gets a dashed swatch in the tooltip, not a solid dot",
    /repeating-linear-gradient/.test(tip), tip);

  // A single-zone house publishes upper == lower == room (the one-zone
  // dynamics assign both from the room temperature every step). Naming those
  // copies would put three identical rows in the tooltip for a house with one
  // zone, so an exact duplicate is dropped instead.
  const oneZone = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  const olegend = legendOf(collect(oneZone.shadowRoot).join("\n"));
  check("a single-zone house still gets one house-temperature chip",
    chipsFor(olegend, "house_temp") === 1 && !/Upper floor/.test(olegend),
    olegend);
  check("and the duplicate traces are dropped rather than drawn",
    oneZone._series.find((s) => s.key === "house_temp").lines.length === 1);
  // Scoped to the house chip's own title, not the whole legend: v5.2.0
  // gives the tank series extra traces of its own on this same fixture, and
  // "does the legend contain the words 'also drawn' anywhere" stopped being
  // a question about the house the moment a second series could answer it.
  check("so its chip claims no extra traces",
    !/also drawn/.test(titleOf(olegend, "house_temp")),
    titleOf(olegend, "house_temp"));
  const otip = ttRows(hovered(oneZone)).filter((l) =>
    /floor|House temperature/i.test(l));
  check("and its tooltip carries the one house row",
    otip.length === 1 && otip[0] === "House temperature", otip.join(" | "));

  // Modelled vs measured. With no lower-floor thermometer the trace is the
  // model running open-loop, and the tooltip has to say so.
  const modelled = build(twoZone({ topology: true }));
  const mtip = hovered(modelled);
  check("an unmeasured lower zone is labelled as modelled in the tooltip",
    /Lower floor \(modelled\): 28 °C/.test(mtip), mtip);
  const measured = build(twoZone({ topology: true, lowerEntity: "sensor.down" }));
  const stip = hovered(measured);
  check("a lower zone with its own thermometer is not",
    /Lower floor: 28 °C/.test(stip) && !/modelled/.test(stip), stip);
  check("no topology published means no claim either way",
    !/modelled/.test(tip), tip);
  // The distinction reaches the legend too, without costing a second chip.
  check("the chip's title carries the modelled wording as well",
    /also drawn: Upper floor, Lower floor \(modelled\)/.test(
      legendOf(collect(modelled.shadowRoot).join("\n"))),
    legendOf(collect(modelled.shadowRoot).join("\n")));

  // Swedish, like every other user-visible string on this card.
  const svZone = new Card();
  svZone.setConfig({ type: "custom:heatpump-optimizer-card" });
  svZone.hass = { states: twoZone({ topology: true }), language: "sv-SE" };
  const svTip = hovered(svZone);
  check("the zone traces are named in Swedish too",
    /Övre plan/.test(svTip) && /Nedre plan \(modellerad\)/.test(svTip), svTip);
  const svLegend = legendOf(collect(svZone.shadowRoot).join("\n"));
  check("and the Swedish legend says one thing, in Swedish",
    chipsFor(svLegend, "house_temp") === 1 &&
    /ritas också: Övre plan, Nedre plan \(modellerad\)/.test(svLegend),
    svLegend);
}

// --- Scenario: the hot-water expected-error band (v5.2.0) ------------------
//
// `dhw_temp_lo` / `dhw_temp_hi` bracket the tank curve with the model's own
// expected error. It rides v5.1.7's multi-trace machinery -- the same `extra`
// array, the same dashed stroke, the same one-chip-toggles-the-series rule,
// the same duplicate-drop -- and differs in exactly one deliberate way: the
// pair is ONE envelope, so it collapses to a single named ± row and a single
// chip instead of two of each.
{
  const mkCard = (mut, lang) => {
    const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    if (mut) {
      states[DEFAULT_DHW].attributes.forecast = plan.dhw_plan.forecast.map(mut);
    }
    const c = new Card();
    c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states, ...(lang ? { language: lang } : {}) };
    // Legend toggles persist to the shared localStorage stub and earlier
    // scenarios switch series off; these assertions are about the band.
    c._hidden = {};
    c.hass = { states, ...(lang ? { language: lang } : {}) };
    return { card: c, dump: collect(c.shadowRoot).join("\n") };
  };
  const dhwPaths = (dump) =>
    [...dump.matchAll(/<path class="series" data-key="dhw_temp"[^>]*>/g)]
      .map((m) => m[0]);
  const dashed = (paths) =>
    paths.filter((x) => /stroke-dasharray="3 3"/.test(x));
  const ptsOf = (c, field) => {
    const s = c._series.find((x) => x.key === "dhw_temp");
    return s.lines.filter((l) => l.field === field).flatMap((l) => l.points);
  };
  const hover = (c) => {
    c._onPointerMove({
      clientX: 400,
      currentTarget: { getBoundingClientRect: () => ({ width: 900, left: 0 }) },
    });
    const tt = c.shadowRoot.querySelector(".tooltip");
    return (tt && tt._html) || "";
  };
  const legendOnly = (dump) => {
    const i = dump.indexOf('<div class="legend">');
    if (i < 0) return "";
    const end = dump.indexOf("</div>", i);
    return dump.slice(i, end < 0 ? undefined : end);
  };

  const banded = plan.dhw_plan.forecast.filter(
    (p) => p.dhw_temp_lo !== null && p.dhw_temp_lo !== undefined
  );
  check("the plan fixture actually carries a hot-water band to draw",
    banded.length > 0 && banded.every(
      (p) => p.dhw_temp_lo <= p.dhw_temp && p.dhw_temp <= p.dhw_temp_hi),
    `${banded.length} banded steps of ${plan.dhw_plan.forecast.length}`);

  const on = mkCard(null);
  const onPaths = dhwPaths(on.dump);
  check("the tank curve draws with its two dashed band edges",
    onPaths.length === 3 && dashed(onPaths).length === 2,
    `${onPaths.length} dhw_temp paths, ${dashed(onPaths).length} dashed`);
  // Matching the room's dashes visually is the whole request: the chart must
  // have ONE vocabulary for "this line is a companion, not a plan". The
  // default fixture publishes upper == lower == room, which v5.1.7 rightly
  // drops as duplicates, so the comparison needs a genuinely two-zone card.
  const twoZoneEl = (() => {
    const states = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
    states[DEFAULT_SPACE].attributes.forecast =
      plan.space_plan.forecast.map((p, i) => ({
        ...p, upper: p.room + 1.5, lower: p.room - 1.5 + (i % 3) * 0.1,
      }));
    const c = new Card();
    c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states };
    c._hidden = {};
    c.hass = { states };
    return c;
  })();
  const twoZoneCard = collect(twoZoneEl.shadowRoot).join("\n");
  const roomDashed = [...twoZoneCard.matchAll(
    /<path class="series" data-key="house_temp"[^>]*>/g)]
    .map((m) => m[0]).filter((x) => /stroke-dasharray/.test(x));
  const dashAttrs = (x) =>
    (String(x).match(/stroke-dasharray="[^"]*" stroke-opacity="[^"]*"/) || [""])[0];
  check("the band's dashes match the room extras' pattern and opacity exactly",
    roomDashed.length === 2 &&
    dashAttrs(dashed(onPaths)[0]) === dashAttrs(roomDashed[0]) &&
    dashAttrs(dashed(onPaths)[0]) ===
      'stroke-dasharray="3 3" stroke-opacity="0.7"',
    `band ${dashAttrs(dashed(onPaths)[0])} vs `
    + `room[${roomDashed.length}] ${dashAttrs(roomDashed[0])}`);
  check("and the band is drawn in the tank series' own colour",
    dashed(onPaths).every((x) => /stroke="#c264d0"/.test(x)),
    dashed(onPaths).join("\n"));
  check("the band brackets the curve it belongs to at every plotted step",
    (() => {
      const lo = ptsOf(on.card, "dhw_temp_lo");
      const hi = ptsOf(on.card, "dhw_temp_hi");
      const mid = new Map(ptsOf(on.card, "dhw_temp").map((q) => [q.t, q.v]));
      const hiAt = new Map(hi.map((q) => [q.t, q.v]));
      return lo.length > 0 && lo.every(
        (q) => q.v <= mid.get(q.t) && mid.get(q.t) <= hiAt.get(q.t));
    })());

  // A fresh install: null at every step, and the card must draw no band at
  // all rather than a zero-width one lying on the curve.
  const off = mkCard((p) => ({ ...p, dhw_temp_lo: null, dhw_temp_hi: null }));
  const offPaths = dhwPaths(off.dump);
  check("null band values draw nothing -- only the tank curve remains",
    offPaths.length === 1 && dashed(offPaths).length === 0,
    `${offPaths.length} dhw_temp paths`);
  check("and the tank curve keeps exactly the data it had with the band",
    JSON.stringify(ptsOf(off.card, "dhw_temp").map((q) => [q.t, q.v])) ===
    JSON.stringify(ptsOf(on.card, "dhw_temp").map((q) => [q.t, q.v])));

  // v5.1.7's duplicate rule, which the band inherits: a record that has
  // scored pairs but never been wrong answers sigma 0, so both edges land
  // exactly on the curve. That is a zero-width envelope and must not draw.
  const flat = mkCard((p) => ({
    ...p, dhw_temp_lo: p.dhw_temp, dhw_temp_hi: p.dhw_temp,
  }));
  const flatPaths = dhwPaths(flat.dump);
  check("a zero-width band is dropped by the same rule that drops a copied "
    + "zone, not drawn on top of the curve",
    flatPaths.length === 1 && dashed(flatPaths).length === 0,
    `${flatPaths.length} dhw_temp paths`);
  check("and it contributes no tooltip row either",
    !/expected error/.test(hover(flat.card)), hover(flat.card));

  // A hole in the middle must BREAK each dashed edge, not bridge it, and not
  // plot the null as a zero -- a zero would drag the shared temperature axis
  // down and flatten every other curve sharing it.
  const gapFrom = 30, gapTo = 40;
  const gapNulled = new Set(
    plan.dhw_plan.forecast.slice(gapFrom, gapTo).map((p) => Date.parse(p.t)));
  const gapped = mkCard((p, i) =>
    i >= gapFrom && i < gapTo
      ? { ...p, dhw_temp_lo: null, dhw_temp_hi: null }
      : p);
  const gapPaths = dhwPaths(gapped.dump);
  check("a null in the middle breaks each band edge into two paths",
    gapPaths.length === 5 && dashed(gapPaths).length === 4,
    `${gapPaths.length} dhw_temp paths, ${dashed(gapPaths).length} dashed`);
  const gapPts = ptsOf(gapped.card, "dhw_temp_lo");
  check("and no null is plotted -- not as a zero, not as anything",
    gapPts.length > 0 && gapPts.every((q) => !gapNulled.has(q.t)),
    `${gapPts.filter((q) => gapNulled.has(q.t)).length} nulled steps plotted`);
  check("every step that DID have a value is still drawn",
    (() => {
      const kept = new Set(gapPts.map((q) => q.t));
      return ptsOf(on.card, "dhw_temp_lo")
        .filter((q) => !gapNulled.has(q.t))
        .every((q) => kept.has(q.t));
    })());
  check("the hole is a real break: the two segments do not share a step",
    (() => {
      const segs = gapped.card._series
        .find((x) => x.key === "dhw_temp")
        .lines.filter((l) => l.field === "dhw_temp_lo");
      if (segs.length !== 2) return false;
      const endA = segs[0].points[segs[0].points.length - 1].t;
      const startB = segs[1].points[0].t;
      return endA < startB && [...gapNulled].some(
        (t) => t > endA && t < startB);
    })());
  // A segmented field is still ONE trace to the reader: v5.1.7 names every
  // trace in the legend and the tooltip, and naming each fragment would say
  // the same thing three times.
  const chipCount = (dump, key) =>
    (legendOnly(dump).match(
      new RegExp(`data-key="${key}"`, "g")) || []).length;
  const legendTitle = (dump, key) => {
    const m = legendOnly(dump).match(
      new RegExp(`data-key="${key}" title="([^"]*)"`));
    return m ? m[1] : "";
  };
  check("a broken band is still named once and reported once, not once per "
    + "segment",
    chipCount(gapped.dump, "dhw_temp") === 1 &&
    (legendTitle(gapped.dump, "dhw_temp")
      .match(/Hot water, expected error/g) || []).length === 1 &&
    (hover(gapped.card).match(/expected error/g) || []).length === 1,
    legendTitle(gapped.dump, "dhw_temp"));

  // --- what the dashed lines SAY -----------------------------------------
  const ttEn = hover(on.card);
  check("the tooltip names the band as the model's expected error, with a ±",
    /Hot water, expected error: ±[\d.]+ °C/.test(ttEn), ttEn);
  check("the solid tank row still reads as an absolute temperature",
    /DHW tank temperature: [\d.-]+ °C/.test(ttEn), ttEn);
  check("the band is ONE row, not two absolute temperatures nobody asked for",
    (ttEn.match(/expected error/g) || []).length === 1 &&
    !/dhw_temp_lo|dhw_temp_hi/.test(ttEn), ttEn);
  const ttOff = hover(off.card);
  check("with no band there is no expected-error row to mislead anyone",
    !/expected error/.test(ttOff) && /DHW tank temperature:/.test(ttOff), ttOff);

  // The legend chip carries the explanation, which is where a reader puzzled
  // by a dashed line actually looks.
  const legEn = legendOnly(on.dump);
  check("the legend says what the tank's dashed pair is",
    /data-key="dhw_temp" title="[^"]*expected error[^"]*widens further ahead/
      .test(legEn),
    (legEn.match(/data-key="dhw_temp" title="[^"]*"/g) || []).join("\n"));
  // v5.1.9: ONE chip per series, extras named inside its title. The band
  // gets no chip of its own and must not: the chip toggles the series, and
  // there is no such thing as hiding one edge of it.
  check("and it is the tank's own single chip that says so, not a second one",
    chipCount(on.dump, "dhw_temp") === 1 &&
    /also drawn: Hot water, expected error\./.test(
      legendTitle(on.dump, "dhw_temp")),
    legendTitle(on.dump, "dhw_temp"));
  // The sentence belongs on hover; stretched across the legend row it would
  // push every other chip off the card.
  check("the explanation rides in the chip's title, not its visible text",
    />DHW tank temperature\s*<\/button>/.test(legEn) &&
    !/>[^<]*widens further ahead[^<]*<\/button>/.test(legEn), legEn);
  // The band is named ONCE in that title, not once per edge -- which is the
  // whole point of enumerating traces through `_extraFields`: a legend
  // rewritten to stop repeating a name must not start repeating this one.
  // Counted on the band's NAME, not on the words "expected error": the
  // explanatory sentence that follows legitimately contains them again.
  check("and it names the pair once, not once per edge",
    (legendTitle(on.dump, "dhw_temp")
      .match(/Hot water, expected error/g) || []).length === 1 &&
    !/DHW tank temperature.*also drawn.*DHW tank temperature/.test(
      legendTitle(on.dump, "dhw_temp")),
    legendTitle(on.dump, "dhw_temp"));

  // A band is a PAIR or it is nothing. Either edge can go missing on its own
  // -- a key absent from the payload, an edge published null the whole way
  // across, or an edge dropped by v5.1.7's duplicate rule -- and before this
  // was enforced the card drew ONE dashed line hugging the curve, still
  // offered the "expected error" legend chip, and reported nothing in the
  // tooltip. Three parts of the card disagreeing about whether a band exists.
  for (const [how, mut] of [
    ["the high edge absent",
      (p) => { const q = { ...p }; delete q.dhw_temp_hi; return q; }],
    ["the low edge absent",
      (p) => { const q = { ...p }; delete q.dhw_temp_lo; return q; }],
    ["the high edge null throughout", (p) => ({ ...p, dhw_temp_hi: null })],
    ["the low edge null throughout", (p) => ({ ...p, dhw_temp_lo: null })],
  ]) {
    const half = mkCard(mut);
    const paths = dhwPaths(half.dump);
    check(`with ${how} the card draws no band at all, not half of one`,
      paths.length === 1 && dashed(paths).length === 0,
      `${paths.length} dhw_temp paths, ${dashed(paths).length} dashed`);
    check(`and offers no expected-error chip for a band it is not drawing`,
      !/expected error/.test(legendOnly(half.dump)),
      legendOnly(half.dump));
    check(`and the tank curve itself is untouched`,
      ptsOf(half.card, "dhw_temp").length ===
      ptsOf(on.card, "dhw_temp").length);
  }

  // --- the legend toggle --------------------------------------------------
  const chipFor = (c, key) =>
    [...c.shadowRoot.querySelectorAll(".chip")]
      .find((el) => el.getAttribute("data-key") === key);
  // `_onLegendClick` reads `currentTarget`, which the stub's dispatch does
  // not set, so the handler is called directly with the chip as its target.
  const clickChip = (c, key) => {
    const el = chipFor(c, key);
    for (const f of el._listeners.click || []) {
      f({ currentTarget: el, stopPropagation() {}, preventDefault() {} });
    }
    return collect(c.shadowRoot).join("\n");
  };
  const toggled = mkCard(null);
  const hiddenDump = clickChip(toggled.card, "dhw_temp");
  check("turning the tank series off takes its band with it",
    dhwPaths(hiddenDump).length === 0,
    `${dhwPaths(hiddenDump).length} dhw_temp paths after the toggle`);
  // Compared against the SAME card before the toggle, not against the
  // two-zone card above: the point is that hiding one series leaves the
  // other exactly as it was.
  const housePaths = (dump) =>
    [...dump.matchAll(/<path class="series" data-key="house_temp"[^>]*>/g)]
      .map((m) => m[0]);
  // Trace count and dash treatment, not path geometry: hiding a series frees
  // the shared temperature axis to rescale, so the remaining curve's
  // coordinates legitimately move. What must not change is how many traces
  // the room series has and which of them are dashed.
  const dashCount = (paths) =>
    paths.filter((x) => /stroke-dasharray/.test(x)).length;
  check("while the room's own traces are untouched -- one chip, one series",
    housePaths(hiddenDump).length === housePaths(on.dump).length &&
    dashCount(housePaths(hiddenDump)) === dashCount(housePaths(on.dump)),
    `${housePaths(hiddenDump).length}/${dashCount(housePaths(hiddenDump))} vs `
    + `${housePaths(on.dump).length}/${dashCount(housePaths(on.dump))}`);
  check("and the chip count is unchanged: the room keeps its own chips",
    chipCount(hiddenDump, "house_temp") === chipCount(on.dump, "house_temp"),
    `${chipCount(hiddenDump, "house_temp")} vs `
    + `${chipCount(on.dump, "house_temp")}`);
  const backDump = clickChip(toggled.card, "dhw_temp");
  check("and turning it back on restores the curve and both band edges",
    dhwPaths(backDump).length === 3 && dashed(dhwPaths(backDump)).length === 2,
    `${dhwPaths(backDump).length} paths, `
    + `${dashed(dhwPaths(backDump)).length} dashed`);
  const hoverHidden = (() => {
    clickChip(toggled.card, "dhw_temp");
    const tt = hover(toggled.card);
    clickChip(toggled.card, "dhw_temp");
    return tt;
  })();
  check("a hidden tank series contributes no band row to the tooltip either",
    !/expected error/.test(hoverHidden) &&
    !/DHW tank temperature:/.test(hoverHidden), hoverHidden);

  // --- naming the band WITHOUT a chip of its own --------------------------
  //
  // This branch draws one chip per named trace. A sibling change replaces
  // that with one chip per SERIES, naming the rest of its traces inside that
  // chip's `title`. The band must not assume either shape: what it owes any
  // such consumer is that "how many traces are there, and what is each
  // called" has a right answer, which is `_extraFields` + `_lineLabel`.
  // Asserted against those two directly, because the markup this branch
  // happens to render cannot show it.
  //
  // Both failure modes here are silent and would ship: iterating `lines`
  // instead of `_extraFields` names a band twice and a gapped trace once per
  // fragment, and without `extraLabels` an edge falls back to the series
  // label and calls itself "DHW tank temperature" -- a second, wrong
  // absolute temperature in a legend built to remove duplicates.
  {
    const traces = (c, key) => {
      const s = c._series.find((x) => x.key === key);
      return c._extraFields(s).map((line) => c._lineLabel(s, line));
    };
    check("the band is ONE named trace, however many paths draw it",
      JSON.stringify(traces(on.card, "dhw_temp")) ===
        JSON.stringify(["Hot water, expected error"]),
      JSON.stringify(traces(on.card, "dhw_temp")));
    check("and it stays one when a hole splits both edges in two",
      JSON.stringify(traces(gapped.card, "dhw_temp")) ===
        JSON.stringify(["Hot water, expected error"]),
      JSON.stringify(traces(gapped.card, "dhw_temp")));
    check("neither edge ever answers to the tank curve's own name",
      !traces(on.card, "dhw_temp").includes("DHW tank temperature"),
      JSON.stringify(traces(on.card, "dhw_temp")));
    // The collapse is the BAND's, not every extra's: two floors are two
    // real temperatures and must keep two names.
    check("while the room's two floors stay two separately named traces",
      JSON.stringify(traces(twoZoneEl, "house_temp")) ===
        JSON.stringify(["Upper floor", "Lower floor"]),
      JSON.stringify(traces(twoZoneEl, "house_temp")));
    check("and a series with no band is unaffected by any of it",
      traces(on.card, "house_temp").length === 0,
      JSON.stringify(traces(on.card, "house_temp")));
    check("the explanation is fetched per trace too, so a one-chip legend "
      + "can reach it",
      (() => {
        const s = on.card._series.find((x) => x.key === "dhw_temp");
        const zs = twoZoneEl._series.find((x) => x.key === "house_temp");
        return /widens further ahead/.test(
          on.card._lineNote(s, on.card._extraFields(s)[0])) &&
          twoZoneEl._lineNote(zs, twoZoneEl._extraFields(zs)[0]) === "";
      })());
  }

  // Swedish: both dictionaries carry the new keys, or the band is explained
  // to half the users only.
  const sv = mkCard(null, "sv-SE");
  const svTt = hover(sv.card);
  check("the band is named in Swedish too",
    /Varmvatten, förväntat fel: ±[\d.]+ °C/.test(svTt), svTt);
  check("the Swedish legend explains the dashed pair",
    /förväntade fel/.test(legendOnly(sv.dump)), legendOnly(sv.dump));
  check("and no English band string leaks into the Swedish render",
    !/expected error/.test(svTt) && !/expected error/.test(legendOnly(sv.dump)),
    svTt);
}


// ===========================================================================
// Card setup and what-if surfaces (a2)
// ===========================================================================

// --- Scenario: hot water guaranteed until midnight -------------------------
// `dhw_schedule.format_windows` renders a window that runs to the end of the
// day as "20:00-24:00" ON PURPOSE, and `parse_windows` reads it straight back
// to the same window. The card's `hourOf` has no 24:00 — nor should it, since
// it also parses `<input type="time">` values and there is no 24:00 in one.
//
// The two paths differ, and only one of them was broken:
//
//   * The SAVE path and the Apply button both call `_onSlotEdit` first, which
//     re-reads the window rows out of the DOM, where the browser has already
//     turned an unrepresentable 24:00 into something a time input can hold.
//   * The slider path does NOT. `_onWhatIfInput` writes one number into the
//     memoised draft and schedules `_runWhatIf`, which validates that draft —
//     the one seeded straight from the sensor's published "20:00-24:00".
//
// So a household whose hot water is guaranteed until midnight could not price
// a single change: every simulate was refused by the card itself, with a
// message blaming the schedule the integration had just published.
{
  const calls = [];
  const st = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7;
  st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "20:00-24:00";
  const mid = build(st, { what_if: true });
  mid._hass = {
    states: st,
    callService: async (domain, service, data) => {
      calls.push({ domain, service, data });
      return { response: { results: { abc: simResult } } };
    },
  };
  mid._onCardClick({});

  const seeded = mid._whatIfDraft().dhwWindows;
  check("the editor seeds one window from the published schedule",
    seeded.length === 1 && seeded[0].start === "20:00",
    JSON.stringify(seeded));

  // The slider path: nothing re-reads the DOM, so what is validated is the
  // seeded draft itself.
  mid._onWhatIfInput({
    stopPropagation() {},
    target: { value: "21.5", classList: { contains: () => false } },
  });
  clearTimeout(mid._whatIfTimer);
  mid._whatIfTimer = null;
  await mid._runWhatIf();
  const sims = calls.filter((c) => c.service === "simulate_plan");
  check("a 20:00-24:00 household reaches simulate_plan",
    sims.length === 1,
    `${calls.length} service call(s): ${JSON.stringify(calls.map((c) => c.service))}`);
  check("and the panel does not call the house's own schedule invalid",
    !/not a valid time/.test(
      mid.shadowRoot.querySelector(".wi-result").textContent || ""),
    mid.shadowRoot.querySelector(".wi-result").textContent);
  // What it prices has to still be the window the house runs. "20:00-00:00"
  // is the same window to `parse_windows`; anything else is a different
  // schedule wearing the same label.
  check("and the window it prices is still the one the house runs",
    sims.length === 1 && sims[0].data.dhw_windows === "20:00-00:00",
    sims.length === 1 ? JSON.stringify(sims[0].data.dhw_windows) : "no call");

  // A window that is genuinely not a time still stops the run — and now says
  // WHICH one, because a household with four windows given "one of them is
  // wrong" has to check all four by hand.
  mid._whatIfDraft().dhwWindows = [
    { start: "06:00", end: "08:00" },
    { start: "17:00", end: "25:70" },
  ];
  const beforeBad = calls.length;
  await mid._runWhatIf();
  check("a genuinely malformed window still stops the run",
    calls.length === beforeBad,
    JSON.stringify(calls.slice(beforeBad).map((c) => c.service)));
  check("and the error names the window that is wrong",
    /17:00-25:70/.test(
      mid.shadowRoot.querySelector(".wi-result").textContent || ""),
    mid.shadowRoot.querySelector(".wi-result").textContent);
  check("without naming the windows that are fine",
    !/06:00-08:00/.test(
      mid.shadowRoot.querySelector(".wi-result").textContent || ""),
    mid.shadowRoot.querySelector(".wi-result").textContent);
}

// --- Scenario: the slot menu's document listener is not for keeps ----------
// The menu parks an Escape handler on the DOCUMENT, because a mouse-opened
// menu leaves focus on the chart and the menu element never sees the key.
// Two paths dropped the menu without dropping the listener:
//
//   * `_render` replaces the whole shadow root — on the coordinator's
//     schedule, not the user's — so the menu element is destroyed under the
//     open menu on the next plan refresh.
//   * `disconnectedCallback` never called `_closeSlotMenu` at all, so a card
//     scrolled off a dashboard left its listener behind for the lifetime of
//     the page: one per card visit.
{
  const kb = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
  const count = () => (docListeners.keydown || []).length;
  const base = count();
  const openMenu = (card) => {
    const svg = card._chartSvgs(card.shadowRoot)[0];
    const slot = svg.querySelector(".slot");
    const runs = card._draftRuns()[slot.dataset.channel] || [];
    const run = runs[Number(slot.dataset.index)];
    card._openSlotMenu(slot.dataset.channel,
      (run.start + run.end) / 2, 120, 300, svg);
  };

  check("no card leaves a document keydown listener behind at rest",
    base === 0, `${base} listener(s) already parked`);
  openMenu(kb);
  check("an open slot menu parks exactly one document keydown listener",
    !!kb._slotMenu && count() === base + 1, `${count()} listener(s)`);

  // A plan refresh. The menu's markup goes with the shadow root either way;
  // the question is whether its listener does.
  kb._render();
  check("a re-render takes the menu's document listener with the menu",
    count() === base, `${count()} listener(s), expected ${base}`);
  check("and leaves no menu state behind on the card",
    kb._slotMenu === null && kb._menuEscape === null,
    `slotMenu=${kb._slotMenu} escape=${kb._menuEscape}`);

  // Repeated refreshes with a menu open each time must not accumulate.
  for (let i = 0; i < 5; i++) { openMenu(kb); kb._render(); }
  check("five open-and-refresh cycles leak nothing",
    count() === base, `${count()} listener(s), expected ${base}`);

  // Teardown: the card is removed from the dashboard with its menu open.
  openMenu(kb);
  check("the menu is open before the card goes away",
    count() === base + 1, `${count()} listener(s)`);
  kb.disconnectedCallback();
  check("disconnecting the card releases the document listener too",
    count() === base, `${count()} listener(s), expected ${base}`);
  check("and the whole page is back to no parked keydown listeners",
    count() === 0, `${count()} listener(s)`);
}

// --- Scenario: the Setup tab before the first solve ------------------------
// `sensor.py` publishes `setup_topology` with no plan at all, and says why in
// as many words: "Configuration-derived, so it exists before the first plan
// does; the card's setup page should not need a solve to draw." The card
// gated the expand affordance AND the dialog on plan data, so the one page
// that could have told a user which sensor is missing was reachable only
// after a solve that the missing sensor was preventing.
{
  const preStates = {};
  preStates[DEFAULT_SPACE] = {
    state: "unknown",
    attributes: {
      plan_kind: "space",
      friendly_name: "Space Heating Plan",
      manual_plan_window_hours: 6,
      setup_topology: setupTopo(),
      currency: "SEK",
    },
  };
  preStates[DEFAULT_DHW] = {
    state: "unknown",
    attributes: { plan_kind: "dhw", friendly_name: "DHW Heating Plan",
      currency: "SEK" },
  };
  preStates["sensor.livingroom"] = { state: "21.3",
    attributes: { unit_of_measurement: "°C", friendly_name: "Living room" } };
  const pre = build(preStates);
  const preDump = collect(pre.shadowRoot).join("\n");
  check("with no plan the card still says there is no plan",
    /no plan data/i.test(preDump), preDump.slice(0, 200));
  check("but it still offers a way in to the setup page",
    /class="expand"/.test(preDump),
    "no expand affordance rendered");

  pre._onExpandClick({ stopPropagation() {} });
  const openDump = collect(pre.shadowRoot).join("\n");
  check("expanding before the first solve opens the dialog",
    pre._expanded === true && /<dialog/.test(openDump),
    `expanded=${pre._expanded}`);
  check("and it lands on the setup page rather than an empty plan",
    pre._dialogPage === "setup" && /class="setup-page"/.test(openDump),
    `page=${pre._dialogPage}`);
  check("the diagram is drawn from the published topology",
    /class="setup-hit"/.test(openDump) && /Indoor temperature/.test(openDump),
    "no clickable slots rendered");
  check("so an unassigned sensor can be assigned without a plan first",
    pre.shadowRoot.querySelectorAll(".setup-hit")
      .some((h) => h.dataset.key === "lower_floor_temp_entity"),
    pre.shadowRoot.querySelectorAll(".setup-hit")
      .map((h) => h.dataset.key).join(", "));
  // The Plan tab is still there and still honest about having nothing.
  const planTab = pre.shadowRoot.querySelectorAll(".dlg-tab")
    .find((t) => t.dataset.page === "plan");
  check("the Plan tab is still offered", !!planTab);
  ((planTab && planTab._listeners.click) || []).forEach((f) =>
    f({ currentTarget: planTab, stopPropagation() {} }));
  // Scoped to the DIALOG's own body: the card underneath says "no plan data"
  // too, so a match anywhere in the shadow root would pass against a dialog
  // page that drew nothing at all.
  const dlgBody = pre.shadowRoot.querySelector("dialog .dlg-body");
  check("and switching to it explains the absence rather than drawing nothing",
    pre._dialogPage === "plan" && !!dlgBody &&
    /no plan data/i.test(dlgBody.textContent || ""),
    `page=${pre._dialogPage} body=${JSON.stringify(
      (dlgBody && dlgBody.textContent) || null)}`);

  // An install with genuinely nothing published has nothing to expand to:
  // no plan, and no topology either. That empty state stays as it was.
  const nothing = build({});
  check("an install with nothing published still offers no expansion",
    !/class="expand"/.test(collect(nothing.shadowRoot).join("\n")) &&
    !/<ha-card class="clickable"/.test(collect(nothing.shadowRoot).join("\n")));
}

// --- Scenario: what a slot is asking for comes from the slot ---------------
// The picker ranks a matching device_class to the top, which is what makes a
// temperature slot usable on an install with hundreds of sensors. That
// expectation used to live in a hardcoded map inside the card, keyed by slot
// id — a second copy of something `topology._SLOTS` already describes, and
// one that no test touched. It is published on the slot now, beside the
// domains it sits with in the same table.
{
  const bigStates = {};
  for (let i = 0; i < 250; i++) {
    bigStates[`sensor.aaa_meter_${String(i).padStart(3, "0")}`] = {
      state: "3.2",
      attributes: { device_class: "power", unit_of_measurement: "kW",
        friendly_name: `Meter ${String(i).padStart(3, "0")}` },
    };
  }
  bigStates["sensor.zzz_wood_probe"] = {
    state: "71.2",
    attributes: { device_class: "temperature", unit_of_measurement: "°C",
      friendly_name: "Wood probe" },
  };
  const topo = setupTopo();
  topo.slots = topo.slots.map((s) =>
    s.key === "wood_tank_top_entity"
      ? { ...s, device_class: "temperature" }
      : s);
  const card = mkSetup(topo, bigStates);
  const hit = card.shadowRoot.querySelectorAll(".setup-hit")
    .find((h) => h.dataset.key === "wood_tank_top_entity");
  (hit._listeners.click || []).forEach((f) =>
    f({ currentTarget: hit, preventDefault() {}, stopPropagation() {} }));
  const pickerHtml = collect(card.shadowRoot).join("\n");
  const opts = [...pickerHtml.matchAll(/<option value="([^"]*)"/g)]
    .map((m) => m[1]).filter(Boolean);
  check("a slot that wants a temperature ranks one above 250 power meters",
    opts[0] === "sensor.zzz_wood_probe",
    `first five: ${opts.slice(0, 5).join(", ")}`);
  // Ranking, not filtering. A house full of sensors carrying no device
  // class at all is normal, and a picker that hid them would hide the very
  // probe the user is trying to assign.
  check("and hides none of the ones it did not ask for",
    opts.some((id) => /aaa_meter/.test(id)) &&
    opts.length === vm.runInContext("PICKER_MAX_OPTIONS", ctx),
    `${opts.length} options, ${opts.filter((id) => /aaa_meter/.test(id)).length} of them power meters`);
}

// --- Scenario: the assignment the picker could not see ---------------------
// The picker prepends the slot's own entity as the SELECTED option, outside
// the text filter and outside the 200-option cap, because an option that is
// absent reads as "(not configured)" and Assign writes that absence back as a
// clearance. That production line has been there since v5.1.4 — and until now
// nothing reached it. The scenario above assigns
// `sensor.vedpanna_temperatur_temperature_2`, which sorts BEFORE 400
// `sensor.zz_probe_*` and therefore lands inside the cap on its own merits;
// replacing `if (chosen && !listed.has(chosen))` with `if (false)` left the
// whole suite green. Three ordinary ways an assignment falls outside the list
// the picker would otherwise build, and the write that used to follow.
{
  const MAX = vm.runInContext("PICKER_MAX_OPTIONS", ctx);
  const bigStates = {};
  for (let i = 0; i < 400; i++) {
    bigStates[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = {
      state: "20.0",
      attributes: { unit_of_measurement: "°C",
        friendly_name: `Probe ${String(i).padStart(3, "0")}` },
    };
  }
  const assignedTo = (id) => {
    const t = setupTopo();
    t.slots = t.slots.map((s) =>
      s.key === "wood_tank_top_entity" ? { ...s, entity: id } : s);
    return t;
  };
  const openAndRead = (card, filter) => {
    const hit = card.shadowRoot.querySelectorAll(".setup-hit")
      .find((h) => h.dataset.key === "wood_tank_top_entity");
    (hit._listeners.click || []).forEach((f) =>
      f({ currentTarget: hit, preventDefault() {}, stopPropagation() {} }));
    if (filter !== undefined) {
      const box = card.shadowRoot.querySelector(".sp-filter");
      box.value = filter;
      (box._listeners.input || []).forEach((f) =>
        f({ currentTarget: box, target: box }));
    }
    const page = collect(card.shadowRoot).join("\n");
    return [...page.matchAll(
      /<option value="([^"]*)"( selected)?>([^<]*)<\/option>/g)]
      .map((mm) => ({ value: mm[1], selected: !!mm[2], text: mm[3] }));
  };

  // (a) Past the cap on its own merits: 400 candidates, and the assigned one
  //     is the last of them alphabetically. The cap is a RENDER bound, so the
  //     answer is 200 listed candidates PLUS the one that is already
  //     configured — not 200 that happen to exclude it.
  const past = mkSetup(assignedTo("sensor.zz_probe_399"), bigStates);
  const pastOpts = openAndRead(past);
  const pastMine = pastOpts.find((o) => o.value === "sensor.zz_probe_399");
  check("an assignment 200 places past the cap is still offered",
    !!pastMine && pastOpts.filter((o) => o.value).length === MAX + 1,
    `${pastOpts.filter((o) => o.value).length} options for 400 candidates, ` +
    `cap ${MAX}`);
  check("and it is the one and only option the picker comes up on",
    !!pastMine && pastMine.selected &&
    pastOpts.filter((o) => o.selected).length === 1,
    JSON.stringify(pastOpts.filter((o) => o.selected)));

  // (b) A filter the assignment does not match. Narrowing the list to look
  //     for something else must not quietly deselect what is configured.
  const filtered = mkSetup(assignedTo("sensor.zz_probe_399"), bigStates);
  const fOpts = openAndRead(filtered, "probe 012");
  check("a filter that excludes the assignment does not drop it",
    fOpts.some((o) => o.value === "sensor.zz_probe_399" && o.selected),
    fOpts.map((o) => o.value).join(", ").slice(0, 120));

  // (c) The strongest form: the assignment is in no list the picker builds,
  //     because the entity is not in `states` at all — renamed, removed, or
  //     an integration that has not come up yet. Ranking and filtering can
  //     never reach it; only the prepend can.
  const gone = mkSetup(assignedTo("sensor.renamed_away"), bigStates);
  const goneOpts = openAndRead(gone);
  const ghost = goneOpts.find((o) => o.value === "sensor.renamed_away");
  check("an assignment that is not a candidate at all is still shown",
    !!ghost && ghost.selected,
    JSON.stringify(goneOpts.slice(0, 3)));
  check("and it is labelled with its raw id, and said to be unavailable",
    !!ghost && ghost.text.includes("sensor.renamed_away") &&
    /not available/i.test(ghost.text),
    ghost && ghost.text);
  // The payload. This is the write that used to arrive as a clearance.
  const calls = [];
  gone._hass.callService = async (d, s2, data) => { calls.push([d, s2, data]); };
  const saveBtn = gone.shadowRoot.querySelector(".sp-save");
  await Promise.all((saveBtn._listeners.click || [])
    .map((f) => f({ stopPropagation() {}, preventDefault() {} })));
  check("and Assign on an untouched picker writes it back, not a clearance",
    calls.length === 1 && calls[0][2].entity_id === "sensor.renamed_away",
    JSON.stringify(calls));
}


console.log(fails ? `\n${fails} CARD CHECK(S) FAILED` : "\nALL CARD CHECKS PASSED");
process.exit(fails?1:0);
