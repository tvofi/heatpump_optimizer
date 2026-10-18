// ARCH2-s5 (round 10, D7): the card pages tests/card_drift.mjs does not render.
//
//     HPO_PLANDATA=<temp>/plandata.json node dev/audit/rounds/round10/D7/arch2-s5/card_pages_drift.mjs [REF]
//
// card_drift.mjs renders 40 states, none of them the Health page, the Savings
// receipt/replay, the Advisor inbox (ranked rows, waiting/error rows, restart
// rows, the feedback row) or the deep links those pages fire (Assign into the
// Setup picker, Open settings). This harness renders exactly those, for the
// REF's card and the working tree's card, in the same process, through
// tests/card_rig.mjs, against the same plan payload and the same frozen clock,
// and compares every state byte for byte -- card_drift's method, its rig, on
// the pages it leaves out. A deep-link state records the markup after the
// press plus the picker state and the router calls (pushState path and the
// location-changed event), so a refactor of the link that lands somewhere
// else, or with focus handled differently, moves a state.
//
// Fixtures are card.mjs's own (the Advisor inbox, Health and receipt blocks),
// copied as data. Output: one line per state, then
//   RESULT states=<n> identical=<k> moved=<m>
// Exit 1 when any state moved. Perturbation: any one-line change to what these
// pages print (e.g. `fmtMinutes` returning "min" without the space) moves the
// Health states and the exit goes to 1.
import fs from "fs";
import path from "path";
import { execFileSync } from "child_process";
import { fileURLToPath } from "url";
import {
  CARD_PATH, DEFAULT_SPACE, DEFAULT_DHW, HOUR,
  makeCardContext, loadCard, collect, frozenDateClass, planStates,
} from "../../../../../../tests/card_rig.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../../../../..");
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !fs.existsSync(planPath)) {
  console.error("HPO_PLANDATA must name the payload tests/plan_view.py wrote");
  process.exit(2);
}
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const ref = process.argv[2] || "origin/main";
const baseSrc = execFileSync("git", ["show", `${ref}:${CARD_PATH}`], { cwd: repo, encoding: "utf8" });
const treeSrc = fs.readFileSync(path.join(repo, CARD_PATH), "utf8");

const PFX = "sensor.heat_pump_optimizer";
const BIN = "binary_sensor.heat_pump_optimizer_input_problem";

function side(src, label) {
  const rig = makeCardContext();
  const Card = loadCard(rig.ctx, src);
  const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
  rig.ctx.Date = frozenDateClass(Date, FROZEN);
  const router = [];
  rig.ctx.history = { pushState: (_s, _t, p) => router.push(`push ${p}`) };
  rig.ctx.dispatchEvent = (ev) => router.push(`event ${ev.type}`);
  return { ...rig, Card, FROZEN, label, router };
}

const iso = (ms) => new Date(ms).toISOString();
const topoSlots = (slots) => ({
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: false, volume_l: 500 }, edges: [], slots,
});

function inboxStates() {
  const s = planStates(plan);
  s[DEFAULT_SPACE].attributes.setup_topology = topoSlots([{ key: "lower_floor_temp_entity",
    label: "Lower floor temperature", place: "lower_zone", entity: null, domains: ["sensor"] }]);
  s[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: [
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", priced: true, spread_c: 0.42 },
    { key: "buffer_tank_temp_entity", label: "Buffer tank", priced: false, reason: "no_clamped_parameter" }] };
  s[`${PFX}_sensor_gap_advisor`] = { state: "40", last_updated: "t1", attributes: {
    top_slot: "lower_floor_temp_entity",
    gaps: [{ key: "lower_floor_temp_entity", label: "Lower floor temperature", empty: true, sek_per_month: 40 }] } };
  s[`${PFX}_dhw_setpoint_advisor`] = { state: "48", last_updated: "t1", attributes: {
    current_setpoint: 55, recommended_setpoint: 48, covers_heaviest_window: true,
    candidates: [[48, 9.0], [50, 9.4], [52, 9.9], [54, 10.5], [56, 11.2], [58, 12.0], [60, 12.9]]
      .map(([setpoint, cost_per_day]) => ({ setpoint, cost_per_day, meets_heaviest_window: true })) } };
  s[`${PFX}_optimization_score`] = { state: "80", last_updated: "t1", attributes: { price_tiles: {
    target_minus_1: { overrides: { target_temp: 20 }, monthly_cost_delta: -90 },
    target_plus_1: { overrides: { target_temp: 22 }, monthly_cost_delta: 95 } } } };
  s[`${PFX}_valve_target_recommendation`] = { state: "21.5", last_updated: "t1", attributes: {
    reason: "cheap hours", configured_target: 21, mixing_valve_mode: "manual", price_ratio: 0.7 } };
  return s;
}

function restartStates() {
  const s = inboxStates();
  s[`${PFX}_model_restart_advisor`] = { state: "1.138", last_updated: "t1", attributes: {
    drift_alarm: true, current_scale: 0.673,
    refit: { scale: 1.138, band_percent: 10, pairs: 180, settled_days: 3.25, required_days: 3 },
    restore: { taken_at: "2026-03-01T03:00:00+00:00", scale: 1.0 } } };
  return s;
}

function waitingStates() {
  const s = inboxStates();
  s[`${PFX}_dhw_setpoint_advisor`] = { state: "unknown", attributes: { waiting_for: "first_dhw_cycle" } };
  s[`${PFX}_sensor_gap_advisor`] = { state: "unavailable", attributes: {} };
  s[`${PFX}_valve_target_recommendation`] = { state: "unknown", attributes: {} };
  return s;
}

function feedbackStates() {
  const s = inboxStates();
  delete s[`${PFX}_dhw_setpoint_advisor`];
  s[`${PFX}_sensor_gap_advisor`].state = "0";
  s[`${PFX}_sensor_gap_advisor`].attributes.feedback_gaps = [
    { class: "power", key: "heat_pump_power_entity" }, { class: "energy", key: "energy_entity" }];
  return s;
}

function healthStates(FROZEN, model) {
  const s = planStates(plan);
  s[DEFAULT_SPACE].attributes.setup_topology = topoSlots([
    { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.indoor", domains: ["sensor"] },
    { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump", entity: "switch.hp", domains: ["switch"] },
    { key: "heat_pump_power_entity", label: "Power meter", place: "heat_pump", entity: null, domains: ["sensor"] }]);
  s[BIN] = { state: "on", last_updated: "t1", attributes: {
    problems: [{ input: "outdoor_temp_entity", entity_id: "sensor.outdoor", problem: "stale", age_minutes: 130, max_age_minutes: 60 },
      { input: "dhw_temp_entity", entity_id: "sensor.tank", problem: "unavailable", age_minutes: null, max_age_minutes: null }],
    input_ages_minutes: { indoor_temp_entity: 3, outdoor_temp_entity: 130, dhw_temp_entity: 4, price_entity: 75 } } };
  s[`${PFX}_last_optimization`] = { state: iso(FROZEN - 12 * 60e3), last_changed: iso(FROZEN - 12 * 60e3), attributes: {} };
  s[`${PFX}_next_optimization`] = { state: iso(FROZEN + 18 * 60e3), last_changed: iso(FROZEN - 12 * 60e3), attributes: {} };
  s[`${PFX}_optimization_status`] = { state: "optimal", last_updated: "t1", attributes: {
    solve_time_ms: 1400, prices_available: 96, weather_forecast_available: 48 } };
  s[`${PFX}_plan_monthly_savings`] = { state: "unavailable", attributes: {} };
  s[`${PFX}_learning_observed_cop`] = { state: "unavailable", attributes: {} };
  s[`${PFX}_prediction_accuracy`] = { state: "0.3", last_updated: "t1", attributes: {} };
  s[`${PFX}_plan_optimization_score`] = { state: "unavailable", attributes: {} };
  if (model) {
    s[`${PFX}_learning_model_status`] = { state: "learned", last_updated: "t1", attributes: {
      heat_loss_w_per_k: 142.0, heat_loss: { scale: 1.08, samples: 21, learned: true },
      lower_floor: { ratio: 0.8, samples: 14, learned: true },
      solar_aperture: { scale: 1.15, samples: 6, needed: 30 },
      tank_cooling: { rate_c_per_h: 0.9, samples: 30, learned: true },
      cop: { scale: 0.97, samples: 12, alarm: false, watched_buckets: 2 },
      internal_gains_kw: Array.from({ length: 24 }, (_, h) => 0.2 + 0.02 * h) } };
  }
  return s;
}

function healthDegraded(FROZEN) {
  const s = healthStates(FROZEN, false);
  s[BIN] = { state: "unknown", attributes: {} };
  s[`${PFX}_learning_model_status`] = { state: "unavailable", attributes: {} };
  return s;
}

function savingsStates() {
  const s = planStates(plan);
  s[`${PFX}_monthly_savings`] = { state: "100.00", last_updated: "t1", attributes: {
    unit_of_measurement: "SEK",
    savings_months: [
      { month: "2026-01", baseline_sek: 800, actual_sek: 652, savings_sek: 148, savings_pct: 18.5, estimated: false },
      { month: "2026-02", baseline_sek: 800, actual_sek: 700, savings_sek: -10, savings_pct: null, estimated: true }],
    receipts: [{ month: "2026-01",
      lines: { spot: { kwh: 1238, sek: 498 }, grid_fee: { kwh: 1238, sek: 74 }, capacity: { kwh: 0, sek: 40 } },
      basis: ["spot", "grid_fee", "capacity"], total_sek: 612, capacity_peak_kw: 5.8, compressor_starts: 212,
      reasons: { scheduled: { kwh: 200, sek: 96 }, cheap_price: { kwh: 900, sek: 312 } } }],
    plan_replay: { day: "2026-02-14", start: "2026-02-14T00:05:00+01:00", step_minutes: 15,
      room: Array.from({ length: 97 }, (_, i) => 21 - 0.01 * i),
      cost: Array.from({ length: 97 }, (_, i) => 0.5 * i),
      measured: { t: [6, 12, 24], room: [20.7, 20.4, 20.0], cost: [13, 25, 50] } } } };
  return s;
}

function open(s, states, page, lang) {
  const c = new s.Card();
  c.setConfig({ type: "custom:heatpump-optimizer-card" });
  c.hass = { states, ...(lang ? { language: lang } : {}), callService: async () => {} };
  c._onCardClick({});
  c.dialog.page = page;
  c._render();
  return c;
}

async function press(c, sel, detail) {
  const el = c.shadowRoot.querySelector(sel);
  if (!el) return "missing";
  await Promise.all((el._listeners.click || []).map((f) => f({ stopPropagation() {}, preventDefault() {}, detail })));
  return "pressed";
}

const linkState = (s, c, pressed) => [
  `pressed=${pressed} page=${c.dialog.page} scroll=${c.dialog.scroll}`,
  `picker key=${c.setup.pickerKey} focus=${c.setup.pickerFocus} viaKeyboard=${c.setup.pickerViaKeyboard}`,
  `router ${s.router.join(" | ")}`,
  ...collect(c.shadowRoot),
].join("\n");

const STATES = [
  ["health_full", (s) => open(s, healthStates(s.FROZEN, true), "health")],
  ["health_full_sv", (s) => open(s, healthStates(s.FROZEN, true), "health", "sv")],
  ["health_degraded", (s) => open(s, healthDegraded(s.FROZEN), "health")],
  ["advisor_inbox", (s) => open(s, inboxStates(), "advisor")],
  ["advisor_restart", (s) => open(s, restartStates(), "advisor")],
  ["advisor_waiting", (s) => open(s, waitingStates(), "advisor")],
  ["advisor_feedback", (s) => open(s, feedbackStates(), "advisor")],
  ["savings_receipt", (s) => open(s, savingsStates(), "savings")],
  ["savings_receipt_sv", (s) => open(s, savingsStates(), "savings", "sv")],
  ["link_inbox_assign_mouse", async (s) => {
    const c = open(s, inboxStates(), "advisor");
    return linkState(s, c, await press(c, '.adv-act[data-act="assign"]', 1)); }],
  ["link_inbox_assign_keyboard", async (s) => {
    const c = open(s, inboxStates(), "advisor");
    return linkState(s, c, await press(c, '.adv-act[data-act="assign"]', 0)); }],
  ["link_ranking_row_keyboard", async (s) => {
    const c = open(s, inboxStates(), "advisor");
    return linkState(s, c, await press(c, ".adv-row", 0)); }],
  ["link_ranking_row_mouse", async (s) => {
    const c = open(s, inboxStates(), "advisor");
    return linkState(s, c, await press(c, ".adv-row", 1)); }],
  ["link_health_assign", async (s) => {
    const c = open(s, healthStates(s.FROZEN, true), "health");
    return linkState(s, c, await press(c, '.adv-act[data-act="assign"]', 1)); }],
  ["link_health_show_settings", async (s) => {
    const c = open(s, healthStates(s.FROZEN, true), "health");
    return linkState(s, c, await press(c, '.adv-act[data-act="settings"]', 1)); }],
  ["link_health_diagnostics", async (s) => {
    const c = open(s, healthStates(s.FROZEN, true), "health");
    return linkState(s, c, await press(c, '.adv-act[data-act="diagnostics"]', 1)); }],
  ["link_optin_settings", async (s) => {
    const c = open(s, inboxStates(), "advisor");
    return linkState(s, c, await press(c, '.adv-act[data-act="settings"]', 1)); }],
  ["link_setup_hit_keyboard", async (s) => {
    const st = inboxStates();
    const c = open(s, st, "setup");
    const hit = c.shadowRoot.querySelector(".setup-hit");
    if (!hit) return linkState(s, c, "missing");
    (hit._listeners.keydown || []).forEach((f) => f({ key: "Enter", currentTarget: hit,
      preventDefault() {}, stopPropagation() {} }));
    return linkState(s, c, "keyed"); }],
];

async function renderAll(sd) {
  const out = new Map();
  for (const [name, drive] of STATES) {
    sd.router.length = 0;
    let text;
    try {
      const r = await drive(sd);
      text = typeof r === "string" ? r : collect(r.shadowRoot).join("\n");
    } catch (e) {
      text = `THREW: ${e && e.stack ? e.stack : e}`;
    }
    out.set(name, text);
  }
  return out;
}

const tree = await renderAll(side(treeSrc, "tree"));
const base = await renderAll(side(baseSrc, ref));
// PEEK=name[,name] prints the head of those states (the tree's), so a reader
// can see a state holds what it claims rather than an empty page.
for (const name of (process.env.PEEK || "").split(",").filter(Boolean)) {
  const t = tree.get(name) || "";
  const marks = ["health-page", "advisor-page", "receipt-grid", "savings-table", "adv-inbox-row", "setup-picker"]
    .map((m) => `${m}:${(t.match(new RegExp(m, "g")) || []).length}`).join(" ");
  console.log(`PEEK ${name}\n${t.split("\n").slice(0, 3).join("\n")}\n  ${marks}`);
}
let moved = 0;
for (const [name] of STATES) {
  const same = tree.get(name) === base.get(name);
  if (!same) moved += 1;
  const threw = /^THREW/.test(tree.get(name)) ? " (tree threw)" : "";
  console.log(`  ${same ? "identical" : "MOVED    "}  ${name}  ${tree.get(name).length}B${threw}`);
  if (!same && process.env.SHOW_DIFF) {
    const a = base.get(name).split("\n"), b = tree.get(name).split("\n");
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      if (a[i] !== b[i]) { console.log(`    - ${a[i]}\n    + ${b[i]}`); break; }
    }
  }
}
console.log(`RESULT states=${STATES.length} identical=${STATES.length - moved} moved=${moved}`);
process.exit(moved ? 1 : 0);
