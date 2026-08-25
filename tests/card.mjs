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
  appendChild(c){ this.children.push(c); c.parentNode = this; return c; }
  removeChild(c){
    this.children=this.children.filter(x=>x!==c);
    if (c) c.parentNode = null;
  }
  setAttribute(k,v){ this[k]=v; }
  getAttribute(k){ return this[k]; }
  addEventListener(t,f){ (this._listeners[t] ||= []).push(f); }
  removeEventListener(){}
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
           addEventListener(){}, removeEventListener(){},
           matchMedia:()=>({matches:false,addEventListener(){}}) },
  localStorage:{ getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v);}, removeItem:k=>{delete store[k];} },
  customElements:{ _d:{}, define(n,c){ this._d[n]=c; }, get(n){ return this._d[n]; } },
  ResizeObserver: class { observe(){} unobserve(){} disconnect(){} },
  requestAnimationFrame:(f)=>f(),
  setTimeout, clearTimeout,
};
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
      ["wood_tank", "wood_valve"],
      ["wood_valve", "buffer_tank"],
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
  check("and the wood chain is drawn from the published edges",
    drawn.includes("wood_tank>wood_valve") &&
    drawn.includes("wood_valve>buffer_tank"),
    `edges drawn: ${drawn.join(", ")}`);
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
        "wood-woodvalve", "woodvalve-buffer"].every((e) =>
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
    // 33 characters, which fits the box on a single row (wrapExtra breaks
    // above 34 -- the original wording wrapped with "coil" alone on row two).
    const dhwGroup = coPage.split("<g>")
      .find((g) => g.includes("Hot water tank")) || "";
    check("and the hot water box says where its refill water comes from",
      /refilled through a wood tank coil/.test(dhwGroup),
      "the caption belongs on the tank being preheated, not loose on the page");
  }
  {
    const noValve = JSON.parse(JSON.stringify(topo));
    noValve.valve_mode = "none";
    noValve.edges = [
      ["heat_pump", "buffer_tank"],
      ["buffer_tank", "upper_zone"],
      ["buffer_tank", "lower_zone"],
      ["wood_tank", "wood_valve"],
      ["wood_valve", "buffer_tank"],
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
}

console.log(fails ? `\n${fails} CARD CHECK(S) FAILED` : "\nALL CARD CHECKS PASSED");
process.exit(fails?1:0);
