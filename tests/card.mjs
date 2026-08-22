import fs from "fs";
import vm from "vm";

const plan = JSON.parse(fs.readFileSync("/tmp/plandata.json","utf8"));

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
      if (matches(c, sel)) out.push(c);
      c._findAll(sel,out);
    }
  }
  attachShadow(){ this.shadowRoot=new Node("shadow-root"); return this.shadowRoot; }
  getBoundingClientRect(){ return {width:900,height:400,left:0,top:0}; }
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
function check(name, cond) { console.log((cond?"  ok  ":"  FAIL") + "  " + name); if(!cond) fails++; }

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

// --- Scenario 13: what-if simulator (item 21) ------------------------------
const offCard = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true));
offCard._onCardClick({});
check("the what-if panel is off by default",
  !/class="whatif"/.test(collect(offCard.shadowRoot).join("\n")));

let called = null;
const whatIf = build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { what_if: true });
whatIf._hass = {
  states: whatIf._hass.states,
  callService: async (domain, service, data) => {
    called = { domain, service, data };
    return { response: { results: { abc: { monthly_cost_delta: -42.5, rate_limited: false } } } };
  },
};
whatIf._onCardClick({});
const whatIfDump = collect(whatIf.shadowRoot).join("\n");
check("the what-if panel appears when enabled",
  /class="whatif"/.test(whatIfDump) && /class="wi-temp"/.test(whatIfDump));

// A drag must not fire a solve per pixel, so input is debounced rather than
// dispatched immediately.
whatIf._onWhatIfInput({ stopPropagation(){}, target:{ value:"19.5" } });
check("dragging does not call the service immediately", called === null);
check("the label follows the slider straight away",
  /19\.5/.test(whatIf.shadowRoot.querySelector(".wi-value").textContent));

await whatIf._runWhatIf(19.5);
check("the simulator calls the right service",
  called && called.domain === "heatpump_optimizer" && called.service === "simulate_plan");
check("the simulator sends the dragged temperature",
  called && called.data.target_temp === 19.5);
const resultEl = whatIf.shadowRoot.querySelector(".wi-result");
check("a cheaper answer is reported as a monthly saving",
  /43 less per month/.test(resultEl.textContent) && resultEl.className.includes("cheaper"));

// An exploratory drag must never leave the card broken when the solve fails.
whatIf._hass = { states: whatIf._hass.states, callService: async () => { throw new Error("boom"); } };
await whatIf._runWhatIf(22);
check("a failed simulation is reported, not swallowed",
  /Could not simulate: boom/.test(whatIf.shadowRoot.querySelector(".wi-result").textContent));

console.log(fails ? `\n${fails} CARD CHECK(S) FAILED` : "\nALL CARD CHECKS PASSED");
process.exit(fails?1:0);
