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
export const DEFAULT_SPACE = "sensor.heat_pump_optimizer_plan_space_heating";
export const DEFAULT_DHW = "sensor.heat_pump_optimizer_plan_dhw_heating";
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

// --- The history API stub ---------------------------------------------------
// The plan-history pan (the owner's pan-back request) reads Home Assistant's
// recorder through `hass.callApi("GET", "history/period/...")`. The rig has
// no hass.connection, so this builds the callApi a Lovelace hass carries,
// answering from a compact fixture: HA's shape is one array per entity, in
// filter_entity_id order, of {state, last_updated, attributes?}. The stub
// PARSES the path the card built -- start out of the path, end_time and
// filter_entity_id out of the query, minimal_response/no_attributes honored
// -- so a test that fetches the wrong ids, the wrong window or a needlessly
// fat response fails rather than passes vacuously.
//
// A fixture row may carry its own `stamp` (a full HA-shaped last_updated,
// microseconds and local offset included -- see haStamp); without one the
// millisecond Z form is served. `opts.inclusiveEnd` serves the state at
// exactly `end_time` too, which is what a recorder that treats end_time as
// inclusive does: the same state then arrives in two neighbouring chunks,
// the boundary join the card has to survive.
//
// Two more of HA's own semantics are served, because the card got both
// wrong while a kinder stub stayed green (bug 7; homeassistant/components/
// history/__init__.py and recorder/history/, the /history/period view):
//   - an entity with ZERO rows in the window is FILTERED OUT of the answer
//     ("Filter out the empty lists if some states had 0 results"), so the
//     answer is not positional; the first row of every list carries its
//     `entity_id` even under minimal_response, and that is the key;
//   - `significant_changes_only` defaults to "1", under which a sensor's
//     row is served only where its STATE changed (last_changed ==
//     last_updated): an attribute-only update (power_kw moving under an
//     unchanged mode) is dropped unless the query sends
//     `significant_changes_only=0`. The first row in the window is served.
//
// opts.fail throws on every call (the network/refusal arm).
export function historyApi(entries, opts = {}) {
  const api = {
    calls: [],
    async callApi(method, path) {
      api.calls.push(`${method} ${path}`);
      if (opts.fail) throw new Error("history unreachable");
      const m = /^history\/period\/([^?]+)\?(.*)$/.exec(String(path || ""));
      if (!m || method !== "GET") {
        throw new Error(`unexpected callApi: ${method} ${path}`);
      }
      const start = Date.parse(decodeURIComponent(m[1]));
      const q = new URLSearchParams(m[2]);
      const end = Date.parse(q.get("end_time"));
      const ids = (q.get("filter_entity_id") || "").split(",").filter(Boolean);
      const lean = q.has("no_attributes");
      const significantOnly = q.get("significant_changes_only") !== "0";
      return ids.map((id) => {
        let prev = null;
        return (entries[id] || [])
          .filter((s) => {
            const t = s.t;
            return t >= start && (t < end || (opts.inclusiveEnd && t === end));
          })
          .filter((s, i) => {
            // A fixture row that repeats its predecessor's state is an
            // attribute-only update when it CARRIES attributes; a bare
            // repeat (the grid fixture's own sample) is served as written,
            // since the recorder would not have written it at all.
            const keep = !significantOnly || i === 0 || !s.attributes ||
              String(s.state) !== prev;
            prev = String(s.state);
            return keep;
          })
          .map((s, i) => ({
            ...(i === 0 || !lean ? { entity_id: id } : {}),
            state: String(s.state),
            last_updated: s.stamp || new Date(s.t).toISOString(),
            ...(lean ? {} : { attributes: s.attributes || {} }),
          }));
      }).filter((rows) => rows.length);
    },
  };
  return api;
}

/** A HA-shaped last_updated: microseconds, and the local UTC offset the
 * instance actually writes (`+01:00` before a spring-forward transition,
 * `+02:00` after it). Round-trips through Date.parse to the same instant,
 * so a fixture built with it exercises the parser against the real string
 * shape rather than the millisecond-Z form the stub would otherwise
 * invent. */
export function haStamp(ms, offsetHours = 1) {
  const p = (n, w = 2) => String(n).padStart(w, "0");
  const dd = new Date(ms + offsetHours * 3600000);
  const sign = offsetHours < 0 ? "-" : "+";
  return (
    `${dd.getUTCFullYear()}-${p(dd.getUTCMonth() + 1)}-${p(dd.getUTCDate())}` +
    `T${p(dd.getUTCHours())}:${p(dd.getUTCMinutes())}:${p(dd.getUTCSeconds())}` +
    `.${p(dd.getUTCMilliseconds(), 3)}456` +
    `${sign}${p(Math.abs(offsetHours))}:00`
  );
}

// The optimizer's own actual-carrying sensors, at the ids a default install
// (device prefix `heat_pump_optimizer`) really creates. The card must derive
// these from the resolved plan sensor, the way it derives its stat entities.
export const HISTORY_IDS = {
  indoor: "sensor.heat_pump_optimizer_indoor_temperature_optimizer",
  outdoor: "sensor.heat_pump_optimizer_outdoor_temperature_optimizer",
  price: "sensor.heat_pump_optimizer_cost_current_electricity_price",
  solar: SOLAR_ID,
  action: "sensor.heat_pump_optimizer_heat_pump_action",
};

/** Deterministic recorded actuals for the 48 h ending at `endMs`.
 *
 * The integration's default optimization interval is 30 minutes
 * (const.py DEFAULT_OPTIMIZATION_INTERVAL), so that is the cadence the
 * recorder sees; values are sines so every series is non-degenerate and
 * unlike its neighbours. One indoor sample mid-window is "unavailable", the
 * honest hole, and the action alternates off/pre_heat/comfort with the
 * power the coordinator publishes alongside each mode.
 */
export function historyFixture(endMs, { stepMs = 30 * 60000, spanMs = 48 * HOUR } = {}) {
  const entries = {
    [HISTORY_IDS.indoor]: [],
    [HISTORY_IDS.outdoor]: [],
    [HISTORY_IDS.price]: [],
    [HISTORY_IDS.solar]: [],
    [HISTORY_IDS.action]: [],
  };
  const n = Math.floor(spanMs / stepMs);
  for (let i = n; i >= 1; i--) {
    const t = endMs - i * stepMs;
    const k = i / n;
    const hourOfDay = (t / HOUR) % 24;
    entries[HISTORY_IDS.indoor].push({
      t, state: (21 + 0.9 * Math.sin(k * Math.PI * 3)).toFixed(1) });
    entries[HISTORY_IDS.outdoor].push({
      t, state: (2.5 + 4 * Math.sin(k * Math.PI * 2)).toFixed(1) });
    entries[HISTORY_IDS.price].push({
      t, state: (0.42 + 0.31 * Math.sin(k * Math.PI * 5)).toFixed(4) });
    entries[HISTORY_IDS.solar].push({
      t, state: Math.max(0, Math.round(320 * Math.sin((hourOfDay - 6) / 12 * Math.PI))).toString() });
    const mode = i % 3 === 0 ? "off" : i % 3 === 1 ? "pre_heat" : "comfort";
    const kw = mode === "off" ? 0 : mode === "pre_heat" ? 4.1 : 2.3;
    entries[HISTORY_IDS.action].push({
      t, state: mode, attributes: { power_kw: kw, heat_pump_on: mode !== "off" } });
  }
  // One unavailable stretch, not a zero reading: the trace must break.
  const mid = entries[HISTORY_IDS.indoor][Math.floor(entries[HISTORY_IDS.indoor].length / 2)];
  mid.state = "unavailable";
  return entries;
}

/** Let the card's fetch/render microtask chain run to rest. */
export const flushHistory = async () => {
  for (let i = 0; i < 8; i++) await Promise.resolve();
};

/** Recorder-realistic history: what /api/history/period actually returns.
 *
 * The synthetic `historyFixture` above writes a row on a fixed grid for
 * every entity, and that regularity is exactly what it should NOT be
 * trusted for: two owner-reported defects survived it. The recorder writes
 * a state only when state OR attributes CHANGE, so this builder emits --
 *
 *   - temperatures at IRREGULAR gaps (4..11 minutes while the house is
 *     being heated, then a multi-hour stable stretch overnight that writes
 *     nothing -- the sparse-then-dense spacing that makes a uniform
 *     Catmull-Rom curve run backward in x, the reported time loop);
 *   - the price only when it steps, roughly hourly with jitter;
 *   - the action entity as the recorder really sees it: with
 *     `power: true`, one row per ATTRIBUTE change with the state often
 *     UNCHANGED (power_kw republished every cycle); with `power: false`
 *     -- an install with no power attribute at all -- rows only at mode
 *     changes, sparse, which is the null control for slots-from-state;
 *   - every stamp in HA's own shape (see `haStamp`), crossing a
 *     spring-forward transition mid-window (+01:00 -> +02:00).
 */
const MODE_CYCLE = ["off", "eco", "hot_water", "pre_heat", "normal"];
const MODE_KW = { eco: 1.4, hot_water: 2.8, pre_heat: 3.4, normal: 2.4 };
export function realisticHistory(endMs, { power = true, spanMs = 48 * HOUR } = {}) {
  const entries = {
    [HISTORY_IDS.indoor]: [],
    [HISTORY_IDS.outdoor]: [],
    [HISTORY_IDS.price]: [],
    [HISTORY_IDS.solar]: [],
    [HISTORY_IDS.action]: [],
  };
  let t = endMs - spanMs;
  let phase = 0;
  let room = 20.6, out = 1.8, price = 0.31, mode = "off";
  while (t < endMs) {
    const offset = t < endMs - 24 * HOUR ? 1 : 2; // spring-forward mid-window
    const stamp = haStamp(t, offset);
    const hourOfDay = (t / HOUR) % 24;
    room += Math.sin(phase / 9) * 0.14;
    out += Math.cos(phase / 7) * 0.35;
    // A stable house stops writing: the temperatures record only during
    // the first hour of every six, and hold silent for the five after --
    // a 5-hour gap beside 4-minute ones is the spacing that made the old
    // uniform-tangent curve run backward in x, and a fixed-grid fixture
    // can never produce it.
    const recording = (t % (6 * HOUR)) < 1 * HOUR;
    if (recording) {
      entries[HISTORY_IDS.indoor].push({ t, stamp, state: room.toFixed(1) });
      entries[HISTORY_IDS.outdoor].push({ t, stamp, state: out.toFixed(1) });
    }
    if (phase % 2 === 0) {
      price = Math.max(0.05, price + Math.sin(phase / 5) * 0.07);
      entries[HISTORY_IDS.price].push({ t, stamp, state: price.toFixed(4) });
    }
    entries[HISTORY_IDS.solar].push({
      t, stamp,
      state: String(Math.max(0, Math.round(300 * Math.sin((hourOfDay - 6) / 12 * Math.PI)))),
    });
    if (phase % 17 === 0) {
      // The optimizer's own ladder (optimizer.py's mode ladder), hot_water
      // among it: a step heating only the tank.
      mode = MODE_CYCLE[(MODE_CYCLE.indexOf(mode) + 1) % MODE_CYCLE.length];
    }
    if (power) {
      // Attribute-only updates: state unchanged, power_kw republished --
      // and MOVING, as the commanded draw does from one solve to the next.
      const kw = mode === "off" ? 0 : MODE_KW[mode] + 0.1 * (phase % 4);
      entries[HISTORY_IDS.action].push({
        t, stamp, state: mode,
        attributes: { power_kw: kw, heat_pump_on: mode !== "off" } });
    } else if (phase % 17 === 0) {
      // No power attribute on this install: rows exist only where the
      // MODE changed, which is all the state-first series may depend on.
      entries[HISTORY_IDS.action].push({ t, stamp, state: mode });
    }
    t += (4 + ((phase * 7) % 8)) * 60000;
    phase += 1;
  }
  for (const rows of Object.values(entries)) rows.sort((a, b) => a.t - b.t);
  return entries;
}

/** The optimizer's own actual-carrying sensors as hass.states knows them.
 *
 * A real install has them beside the plan sensors -- they are this
 * integration's entities, enabled by default -- and the card's history
 * derivation checks presence before asking the recorder for an id, the
 * same guard the stat-entity derivation uses. Fixtures that only want the
 * plan sensors skip this; fixtures that drive the history pan need it.
 */
export function withActuals(states, { prefix = "heat_pump_optimizer" } = {}) {
  return {
    ...states,
    // The attributes below are the ones a real install publishes
    // (sensor.py's device_class/state_class/options declarations) and the
    // ones the card's suffix-scan fallback validates against: a foreign
    // sensor that merely shares a suffix is rejected by shape, not trusted.
    [`sensor.${prefix}_indoor_temperature_optimizer`]: {
      state: "21.1",
      attributes: { device_class: "temperature", unit_of_measurement: "°C" } },
    [`sensor.${prefix}_outdoor_temperature_optimizer`]: {
      state: "3.4",
      attributes: { device_class: "temperature", unit_of_measurement: "°C" } },
    [`sensor.${prefix}_cost_current_electricity_price`]: {
      state: "0.55",
      attributes: { unit_of_measurement: "SEK/kWh" } },
    [`sensor.${prefix}_heat_pump_action`]: {
      state: "comfort",
      attributes: {
        device_class: "enum",
        options: ["boost", "comfort", "eco", "hot_water", "idle", "normal",
          "off", "pre_heat", "system_identification", "unknown"],
        power_kw: 2.3 } },
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
//
// A state may carry more than one bare claim line (#1266, the card-file
// twin of #1255): the value is EVERY line's reason in file order, exactly
// as env_drift.py's `parse_claim_map` reads the solver file, so a map keyed
// on the name alone -- last line wins -- cannot hide a claim a branch added
// beside the baseline's own.
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
      const reason = comment.trim() || "no reason given";
      const reasons = claims.get(name);
      if (reasons) reasons.push(reason);
      else claims.set(name, [reason]);
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

/** Whether two parsed claim maps are the same names AND the same reason
 * LISTS, line count included -- env_drift.py's dict equality over
 * `parse_claim_map` output (#1255), ported to the card lane by #1266.
 * parseClaims once collapsed a state's lines to the last, so a fresh claim
 * added beside an inherited line parsed exactly equal to the baseline's
 * single entry and card_drift.mjs fired INHERITED CLAIMS where the Python
 * gate answered "not inherited" on the same file. The multi-value shape
 * closes that: an added line beside an inherited one is a rewrite, not an
 * inheritance; an exact copy still is one, and still gets emptied by
 * whichever autofix path applies. */
export function sameClaimMap(tree, base) {
  if (!tree || !base || tree.size !== base.size) return false;
  for (const [name, reasons] of tree) {
    const baseReasons = base.get(name);
    if (!baseReasons || baseReasons.length !== reasons.length
      || reasons.some((r, i) => baseReasons[i] !== r)) return false;
  }
  return true;
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

// --- Whose claim is it? ------------------------------------------------------
// A port of tests/env_drift.py's judgement, and deliberately the SAME answer
// on the same tree rather than a card-shaped approximation of it.
//
// The contradiction it resolves is env_drift.py's own, recorded at the
// `stale_is_ours` call site there: for a branch whose three-dot moves nothing
// a claim excuses, byte-identical claim files are red (INHERITED CLAIMS) and
// an emptied list deletes another lane's line at squash-merge (#569, #633).
// #658 gave env_drift.py `stale_claims_judged`; card_drift.mjs never received
// it, so on the tree that merged #735's six card claims the two instruments
// returned opposite verdicts -- `--claims-only` printed "claims hygiene: ok"
// while card_drift.mjs failed the same branch seven times.
//
// The predicate is the UNION over both claim files, exactly as
// `moves_claimable` is there, and not narrowed to the card. Narrowing it
// would re-open the disagreement in the other direction: env_drift.py runs
// `inherited_claims_error` against the CARD claim file too, gated on this
// same union, so a branch touching only integration Python or a capture
// source is judged for its card claims by that instrument. Two gates reading
// one file must not answer differently about it.
//
// The lists below mirror `justifies_solver_claim`, `justifies_card_claim` and
// `CAPTURE_SOURCES` in tests/env_drift.py. They are a second copy, kept
// because the alternative -- a node gate shelling out to Python -- would put
// env_drift.py and everything it imports into card_drift.mjs's closure.

/** tests/env_drift.py's CAPTURE_SOURCES: test files whose contents decide
 * what a capture PRODUCES. */
export const CAPTURE_SOURCES = [
  "tests/golden.py",
  "tests/profiles.py",
  "tests/harness.py",
];

/** Whether `p` can move a solver golden the solver claim file excuses. */
export function justifiesSolverClaim(p) {
  return (
    (p.startsWith("custom_components/heatpump_optimizer/") && p.endsWith(".py")) ||
    CAPTURE_SOURCES.includes(p)
  );
}

/** Whether `p` can move a card state the card claim file excuses. */
export function justifiesCardClaim(p) {
  return p === CARD_PATH;
}

/** Could this three-dot have moved anything a claim excuses? */
export function movesClaimable(changed) {
  return changed.some((p) => justifiesSolverClaim(p) || justifiesCardClaim(p));
}

/** Paths in `ref...HEAD` plus uncommitted work -- env_drift.py's
 * `three_dot_files`, same three commands in the same order.
 *
 * `runGit(...args)` returns stdout and THROWS when git exits non-zero; the
 * throw is the point. Reading stdout without the exit status returns an empty
 * list both for a failure and for a genuinely unchanged tree, and the caller
 * reads empty as "nothing claimable moved", which is the all-clear. */
export function threeDotFiles(runGit, ref) {
  const out = [];
  for (const args of [
    ["diff", "--name-only", `${ref}...HEAD`],
    ["diff", "--name-only", "HEAD"],
    ["ls-files", "--others", "--exclude-standard"],
  ]) {
    for (const line of String(runGit(...args)).split("\n")) {
      const p = line.trim();
      if (p) out.push(p);
    }
  }
  return [...new Set(out)].sort();
}

/** May THIS branch be failed for a claim it may not have written?
 *
 * env_drift.py's `stale_claims_judged`, including its fail-closed tail: an
 * unanswerable three-dot judges, because a gate that cannot read the diff
 * must not quietly stop failing.
 *
 * `justifies` asks the question PER FILE KIND (#747), never per branch:
 * pass `justifiesCardClaim` when the claim file at stake is the card's --
 * a solver diff can move a card STATE through the payload the card
 * renders, but the card claim LIST is not the solver branch's to rewrite,
 * exactly as env_drift.py's `claim_kinds` refuses on its side. The
 * default remains the shared any-claimable form so existing callers keep
 * their behavior. */
export function claimsAreThisBranchs(
  runGit, ref, justifies = (p) => justifiesSolverClaim(p) || justifiesCardClaim(p)
) {
  try {
    return threeDotFiles(runGit, ref).some(justifies);
  } catch (e) {
    return true;
  }
}
