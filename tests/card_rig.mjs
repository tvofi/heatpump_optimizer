// The shared rig for the Node card harnesses: tests/card.mjs,
// tests/setup_qa_render.mjs and tests/card_drift.mjs.
//
// Issue #101 taught the lesson once: the renderer carried a verbatim copy of
// an EARLIER revision of card.mjs's DOM stub and drifted with every
// extension. tests/dom_stub.mjs fixed that for the stub itself; this module
// does the same for the rest of what a harness needs to run the card in
// Node -- the vm context with its window/document/localStorage/timer shims,
// the plan-sensor states built from plan_view.py's payload, the three
// setup-page topologies designers review, and the frozen clock. One copy,
// three importers, so the markup gate and the test cannot disagree about
// what the card was given.
//
// Not a test. Excluded from the "every script is wired" accounting in
// tests/run.sh and from tests/closure.py's roster, like dom_stub.mjs.
import vm from "vm";
import { makeDomStub } from "./dom_stub.mjs";

export const CARD_PATH =
  "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
export const CARD_TAG = "heatpump-optimizer-card";
export const EDITOR_TAG = "heatpump-optimizer-card-editor";
export const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
// The plan sensors use has_entity_name, so a default install prefixes the
// device name. These are the ids a real Home Assistant actually creates.
export const DEFAULT_SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
export const DEFAULT_DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";
export const HOUR = 3600000;

/** The vm context the card runs in, plus the handles a harness drives it by.
 *
 * `innerHTML` is parsed rather than merely stored (see dom_stub.mjs): the
 * card queries its own output for the controls it then wires up, so a stub
 * that kept the markup as an opaque string would skip every one of those
 * paths and report a pass.
 *
 * The listener registries on `window` and `document` are real: the drag and
 * pan gestures park their move/up handlers on window so they survive a
 * mid-gesture re-render, and the slot menu parks an Escape listener on the
 * document. Intervals are deterministic (`tickIntervals()` fires them) so
 * the edge auto-pan can be driven without sleeping.
 *
 * `coarseTouch` / `reducedMotion` are the two media queries the card asks
 * about; flip `.on` before a render to answer them.
 */
export function makeCardContext(opts = {}) {
  const domRef = { document: null };
  const { VOID_TAGS, parseHtml, Node, matches, HTMLElement } = makeDomStub(domRef);
  const docListeners = {};
  const winListeners = {};
  const document = {
    createElement: (t) => new Node(t),
    createElementNS: (ns, t) => new Node(t),
    head: new Node("head"),
    body: new Node("body"),
    activeElement: null,
    addEventListener(t, f) { (docListeners[t] = docListeners[t] || []).push(f); },
    removeEventListener(t, f) {
      const a = docListeners[t] || []; const i = a.indexOf(f); if (i >= 0) a.splice(i, 1);
    },
  };
  document.activeElement = document.body;
  // The stub's focus/blur track the active element on THIS document; the
  // ref was empty while the document was being built (its head and body
  // are stub Nodes, so the classes had to exist first).
  domRef.document = document;
  const store = opts.store || {};
  const coarseTouch = opts.coarseTouch || { on: false };
  const reducedMotion = opts.reducedMotion || { on: false };
  const intervals = new Map();
  let intervalId = 0;
  const localStorage = {
    getItem: (k) => store[k] ?? null,
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
  };
  const ctx = {
    HTMLElement, document, console,
    window: {
      customCards: [],
      localStorage,
      addEventListener(t, f) { (winListeners[t] = winListeners[t] || []).push(f); },
      removeEventListener(t, f) {
        const a = winListeners[t] || []; const i = a.indexOf(f); if (i >= 0) a.splice(i, 1);
      },
      matchMedia: (q) => ({
        matches:
          (q === "(pointer: coarse)" && coarseTouch.on) ||
          (q === "(prefers-reduced-motion: reduce)" && reducedMotion.on),
        addEventListener() {},
      }),
    },
    localStorage,
    customElements: { _d: {}, define(n, c) { this._d[n] = c; }, get(n) { return this._d[n]; } },
    ResizeObserver: class { observe() {} unobserve() {} disconnect() {} },
    requestAnimationFrame: (f) => f(),
    setTimeout, clearTimeout,
    setInterval: (f) => { intervals.set(++intervalId, f); return intervalId; },
    clearInterval: (id) => { intervals.delete(id); },
  };
  // The editor dispatches config-changed as a CustomEvent; the stub only
  // needs the shape the listeners read.
  ctx.CustomEvent = class {
    constructor(type, o = {}) {
      this.type = type; this.detail = o.detail;
      this.bubbles = !!o.bubbles; this.composed = !!o.composed;
    }
  };
  ctx.globalThis = ctx; ctx.self = ctx; ctx.window.document = document;
  vm.createContext(ctx);
  const fireWindow = (t, ev) => (winListeners[t] || []).slice().forEach((f) => f(ev));
  const fireDocument = (t, ev) => (docListeners[t] || []).slice().forEach((f) => f(ev));
  const tickIntervals = () => { for (const f of [...intervals.values()]) f(); };
  return {
    ctx, document, store, winListeners, docListeners, intervals,
    fireWindow, fireDocument, tickIntervals, coarseTouch, reducedMotion,
    VOID_TAGS, parseHtml, Node, matches, HTMLElement,
  };
}

/** Run the card's source in a context and return the registered element. */
export function loadCard(ctx, src) {
  vm.runInContext(src, ctx);
  const Card = ctx.customElements.get(CARD_TAG);
  if (!Card) throw new Error(`${CARD_TAG} did not register itself`);
  return Card;
}

/** Every innerHTML the tree was given, top down. A node assigned innerHTML
 * keeps the string; its parsed children are what the card then queries. An
 * in-place refresh (the lanes during a drag, the setup canvas during a
 * layout edit, the picker's list while typing) lands on a CHILD's string,
 * which is why this walks every node rather than reading the root. */
export function collect(n, out = []) {
  if (n._html) out.push(n._html);
  n.children.forEach((c) => collect(c, out));
  return out;
}

/** A Date whose clock stands still at `at`, for a context whose card must
 * see one fixed "now". Installed as `ctx.Date`; the card resolves `Date` from
 * its global at call time, so a replacement after load is what it sees. */
export function frozenDateClass(RealDate, at) {
  return class FrozenDate extends RealDate {
    constructor(...a) { super(...(a.length ? a : [at])); }
    static now() { return at; }
  };
}

/** The irradiance sensor publishes its own {t, ghi} horizon. Its timestamps
 * are already interval starts, so the card must plot them as-is. */
export function solarForecastFor(plan) {
  return plan.space_plan.forecast.map((p, i) => ({
    t: p.t,
    ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
  }));
}

/** The three sensors a stock install publishes, from plan_view.py's payload.
 * `marker` adds the `plan_kind` attribute the card discovers entities by. */
export function planStates(plan, { spaceId = DEFAULT_SPACE, dhwId = DEFAULT_DHW, marker = true } = {}) {
  const tag = (kind) => (marker ? { plan_kind: kind } : {});
  return {
    [SOLAR_ID]: { state: "120", attributes: {
      forecast: solarForecastFor(plan), source: "open_meteo",
      friendly_name: "Solar Irradiance", ...tag("solar") } },
    [spaceId]: { state: "3 slots planned", attributes: {
      forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
      total_energy_kwh: plan.space_plan.total_energy_kwh,
      total_cost: plan.space_plan.total_cost,
      active_now: plan.space_plan.active_now,
      friendly_name: "Space Heating Plan", ...tag("space") } },
    [dhwId]: { state: "4 slots planned", attributes: {
      forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
      total_energy_kwh: plan.dhw_plan.total_energy_kwh,
      total_cost: plan.dhw_plan.total_cost,
      active_now: plan.dhw_plan.active_now,
      friendly_name: "DHW Heating Plan", ...tag("dhw") } },
  };
}

/** The live readings the setup page draws into its boxes. */
export function setupSensorStates() {
  return {
    "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
    "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
    "sensor.outside": { state: "unavailable", attributes: {} },
  };
}

/** A card the way Lovelace builds one: config, then hass, then connected,
 * then hass again (the frontend sets hass on every state change). */
export function buildCard(Card, states, config, hassExtra) {
  const card = new Card();
  card.setConfig({ type: `custom:${CARD_TAG}`, ...(config || {}) });
  const hass = { states, ...(hassExtra || {}) };
  card.hass = hass;
  if (card.connectedCallback) card.connectedCallback();
  card.hass = hass;
  return card;
}

const TEMP_DOMAINS = ["sensor", "number", "input_number"];

/** The setup page's diagram payload for the three houses designers review:
 * a two-zone, two-tank house with a throttling valve and a wood furnace, as
 * `describe_setup` publishes it -- single buffer, two tanks on a 4-way
 * valve, and the wood tank pre-heating hot water through a coil. */
export function qaTopologies() {
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
      place: "mixing_valve", entity: null, domains: TEMP_DOMAINS },
    { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
      place: "mixing_valve", entity: null, domains: TEMP_DOMAINS },
  ]);
  const coil = JSON.parse(JSON.stringify(twoTank));
  coil.dhw_wood_coil = true;
  coil.edges = twoTank.edges.concat([["wood_tank", "dhw_tank"]]);
  coil.slots.push({ key: "dhw_temp_entity", label: "Hot water temperature",
    place: "dhw_tank", entity: null, domains: TEMP_DOMAINS });
  return { base, twoTank, coil };
}

/** A topology WITH the layout catalog the coordinator publishes, so the
 * layout editor can be driven: a two-zone house with a throttling valve and
 * no wood tank, where `valve_upper_direct_slab` and `single_tank_valve` are
 * both storable and an edit can legitimately move between them. */
export function layoutCatalogTopo(over) {
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
  const catalog = [
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
  return {
    two_zone: true, dhw: false, valve_mode: "manual",
    layout: "valve_upper_direct_slab", two_tank_modelled: false,
    buffer: { volume_l: 500, is_store: true, max_temp: 65 },
    wood: { present: false, volume_l: 0 },
    edges: EDGES.valve_upper_direct_slab.map((e) => [e[0], e[1]]),
    catalog, positions: {},
    slots: [
      { key: "indoor_temp_entity", label: "Indoor temperature",
        place: "upper_zone", entity: "sensor.livingroom", domains: TEMP_DOMAINS },
      { key: "lower_floor_temp_entity", label: "Lower floor temperature",
        place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
      { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
        place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
      { key: "mixing_valve_target_entity", label: "Valve target",
        place: "mixing_valve", entity: null, domains: TEMP_DOMAINS },
      { key: "outdoor_temp_entity", label: "Outdoor temperature",
        place: "outdoor", entity: "sensor.outside", domains: TEMP_DOMAINS },
      { key: "heat_pump_switch_entity", label: "Heat pump switch",
        place: "heat_pump", entity: null,
        domains: ["switch", "input_boolean", "climate"] },
    ],
    ...(over || {}),
  };
}

// --- The markup gate's claim file ------------------------------------------
// tests/golden/card_claimed_drift.txt follows tests/golden/claimed_drift.txt
// to the letter, and tests/env_drift.py's `_claimed` is the reference for
// this parser: the stamp is a comment line that BEGINS with the marker and
// nothing else (`# claims-for: 6.2.7`), first one wins; a claim is any
// non-comment line, its trailing comment the reason. Merely mentioning the
// marker in prose declares nothing, and a claim line never declares either.
export const CLAIM_FILE = "tests/golden/card_claimed_drift.txt";
export const CLAIM_MARKER = "claims-for:";

export function parseClaims(text) {
  let declared = null;
  const claims = new Map();
  for (const line of String(text || "").split("\n")) {
    const hash = line.indexOf("#");
    const body = hash < 0 ? line : line.slice(0, hash);
    const comment = hash < 0 ? "" : line.slice(hash + 1);
    const name = body.trim();
    if (name) {
      claims.set(name, comment.trim() || "no reason given");
      continue;
    }
    const note = comment.trim();
    if (declared === null && note.startsWith(CLAIM_MARKER)) {
      const rest = note.slice(CLAIM_MARKER.length).trim().split(/\s+/);
      declared = rest[0] || "";
    }
  }
  return { declared, claims };
}

export const looksLikeVersion = (text) =>
  /^\d+\.\d+\.\d+$/.test(String(text || ""));

/** Why the claim file is not stamped for this tree -- null when it is. The
 * wording is env_drift.py's `claim_version_error`, so a developer meets one
 * message for both gates. */
export function claimVersionError(declared, version) {
  if (!version) {
    return `NO VERSION FILE: VERSION is missing or empty, so the claim file in ${CLAIM_FILE} cannot be checked against the release it belongs to. Restore VERSION.`;
  }
  if (!looksLikeVersion(version)) {
    return `MALFORMED VERSION: VERSION reads '${version}', which is not an X.Y.Z release number, so the '${CLAIM_MARKER}' stamp in ${CLAIM_FILE} cannot be tied to a release. Fix VERSION first.`;
  }
  if (declared === version) return null;
  let head;
  if (declared === null) {
    head = `UNSTAMPED CLAIM FILE: ${CLAIM_FILE} declares no release, and this tree is v${version}. Every claim file must carry a '# ${CLAIM_MARKER} ${version}' line of its own.`;
  } else if (!looksLikeVersion(declared)) {
    head = `MALFORMED CLAIM FILE: ${CLAIM_FILE} declares '${CLAIM_MARKER} ${declared}', which is not a version, and this tree is v${version}.`;
  } else {
    head = `STALE CLAIM FILE: ${CLAIM_FILE} declares claims for v${declared} but this tree is v${version}.`;
  }
  return `${head} A claim describes one release's diff and does not carry forward. Rewrite the file for this release -- bump the '${CLAIM_MARKER}' line and delete claims this release does not move (an empty list is the right answer for a release that moves nothing).`;
}
