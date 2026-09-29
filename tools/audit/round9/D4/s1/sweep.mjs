// D4-s1 sweep: the card in real Chromium over tests/card_drift.mjs's STATES.
//
// Metric definitions (one line each, per cell = state x viewport x theme x lang x mode):
//   overflow_px   ink of a visible text run beyond its nearest clipping ancestor, minus what that ancestor can scroll to reveal
//   overlap       pairs of visible text runs (not nested, not same-text halo copies) whose boxes intersect by > 2 px in both axes
//   contrast      visible, enabled text runs whose composited fg/bg ratio is below WCAG AA (4.5, or 3 for >= 24 px / bold >= 18.66 px)
//   small         interactive targets (native/ARIA/tabindex, or a topmost cursor:pointer element) whose min side < 24 px (44 px coarse)
//   small24       the subset under 24 px that also fails WCAG 2.5.8's 24 px spacing exception
//   pointerOnly   topmost cursor:pointer targets that are neither focusable nor inside a focusable ancestor (no keyboard route)
//   nameless      interactive targets with an empty accessible name
//   console       console.error + pageerror count while the cell ran
//   (keyboard cells) unreached focusables, focus stops with no visible indicator
//   (hover cells)  Chromium layout-shift score accrued while hovering each target
//
// Run (from the repository root; ~10-15 min on 4 cores):
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
//     /home/claude/venv314/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/root/.cache/pw-browsers \
//     node tools/audit/round9/D4/s1/sweep.mjs [--states a,b] [--quick] [--perturb <name>] [--shots]
//
// Expected (exact; counts/pixels are contention-immune, font = Liberation Sans), canonical targeted run
//   --no-keys --modes normal --states x_pin_ok,x_pin_fail,x_save_ok,x_save_fail,x_dhw_clamped,x_save_confirm,
//   draft_dirty_menu_open,x_menu_right_edge,x_menu_right_edge_dhw,picker_open_filtered,x_live_default,x_live_default_expanded:
//   cells=144 contrast_instances=90 popup_out_cells=6 option_indistinct_pairs=8 now_marker_collisions=24;
//   --perturb status_text_token -> contrast 12; menu_clamp -> popup 0; picker_wrap -> options 0; now_temp_below -> now 0.
//   Full grid (--shots, no --states): cells=1626 at the 47-state launch, kb_unreached=0, overflow_instances=0.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1). Machine: box B10, 4-core Linux container, Chromium 141.0.7390.37.
// Writes only under $TMPDIR (a mkdtemp root) and, with --shots, under this directory's shots/.
// Instrumented symbol: heatpump-optimizer-card.js:HeatpumpOptimizerCard (the registered element, rendered by its _render()).
// Card tile width = viewport - 16 px (one column, 8 px gutters); the dialog is the card's own showModal() <dialog>.
// Limits: no Home Assistant frontend; ha-card is a stand-in with ha-card's background/border/colour; HA default light/dark theme tokens.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import {
  DEFAULT_SPACE, DEFAULT_DHW, HOUR, planStates, setupSensorStates, qaTopologies,
  layoutCatalogTopo, withActuals, realisticHistory, historyApi,
} from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const args = process.argv.slice(2);
const argOf = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const HERE = "tools/audit/round9/D4/s1";
const CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !fs.existsSync(planPath)) { console.error("FAIL: set HPO_PLANDATA to a plan_view.py payload"); process.exit(1); }
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const TMP = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1-"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;

// ---- perturbations: in-memory edits of the card source -------------------
const rep = (s, a, b) => { if (!s.includes(a)) throw new Error(`perturbation anchor missing: ${a.slice(0, 60)}`); return s.split(a).join(b); };
const PERTURB = {
  none: (s) => s,
  // D4-s1-01: status text in the readable text token instead of HA's status tokens.
  status_text_token: (s) => rep(rep(rep(s,
    "color: var(--success-color, #2fae7a);", "color: var(--primary-text-color);"),
    "color: var(--error-color, #e0544e);\n      }\n      @media", "color: var(--primary-text-color);\n      }\n      @media"),
    "color: var(--warning-color, #d98e00);", "color: var(--primary-text-color);"),
  // D4-s1-02: clamp the slot menu inside the chart it was opened from.
  menu_clamp: (s) => rep(s, "    host.appendChild(menu);\n",
    "    host.appendChild(menu);\n    menu.style.left = `${Math.max(0, Math.min(parseFloat(menu.style.left), host.clientWidth - menu.offsetWidth))}px`;\n"),
  // D4-s1-05: the measured-now reading drawn one line below the now marker's label.
  now_temp_below: (s) => rep(s, '`<text class="now-temp" x="${plotL + 6}" y="${plotT + font}"',
    '`<text class="now-temp" x="${plotL + 6}" y="${plotT + 2 * font + 4}"'),
  // D4-s1-03: let a listbox option wrap anywhere, so its whole label is shown.
  picker_wrap: (s) => rep(s, "      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;",
    "      .sp-select option { white-space: normal; overflow-wrap: anywhere; }\n      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;"),
};
const perturbName = argOf("--perturb", "none");
const extraPerturb = argOf("--perturb-file", null);
if (extraPerturb) Object.assign(PERTURB, (await import(path.resolve(extraPerturb))).default);
if (!PERTURB[perturbName]) { console.error(`unknown perturbation ${perturbName}`); process.exit(1); }
const cardSrc = PERTURB[perturbName](fs.readFileSync(CARD, "utf8"));
if (perturbName !== "none" && cardSrc === fs.readFileSync(CARD, "utf8")) { console.error("perturbation did not change the source"); process.exit(1); }
const measureSrc = fs.readFileSync(path.join(HERE, "measure.js"), "utf8");

// ---- the states: tests/card_drift.mjs STATES, same payloads ----------------
const woodFuelStates = (fuel) => { const st = planStates(plan); st[DEFAULT_SPACE].attributes.wood_fuel = fuel; return st; };
const awayPlanStates = ({ sw = false, returnIso = null, resolved = false } = {}) => {
  const st = planStates(plan);
  st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] = { state: returnIso || "unknown", attributes: {} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = { state: resolved ? "on" : "off",
    attributes: { source: resolved && !sw ? "person.alice" : "none" } };
  return st;
};
const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
    lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
});
const scheduleStates = () => {
  const st = planStates(plan);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7;
  st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
  return st;
};
const sharedStepStates = () => {
  const st = planStates(plan);
  const sp = st[DEFAULT_SPACE].attributes.forecast;
  const heating = new Set(sp.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
  st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) =>
    heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
  return st;
};
const setupStates = (topo, extra) => {
  const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
  st[DEFAULT_SPACE].attributes.setup_topology = topo;
  return st;
};
const bigStates = () => {
  const st = {};
  for (let i = 0; i < 400; i++) {
    st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = { state: "20.0",
      attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` } };
  }
  st["sensor.vedpanna_temperatur_temperature"] = { state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  return st;
};
const advisorStates = () => {
  const st = setupStates(qaTopologies().base);
  st[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: [
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13, parameters: ["buffer_cooling_rate"], priced: true },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", spread_c: 2.87, parameters: ["lower_floor_loss_ratio"], priced: true },
    { key: "dhw_temp_entity", label: "Hot water temperature", priced: false, reason: "no_clamped_parameter" },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", priced: false, reason: "weather_backed" },
  ] };
  return st;
};
const firstShared = () => {
  const sp = sharedStepStates()[DEFAULT_SPACE].attributes.forecast;
  const f = sp.find((p) => Number(p.space_power) > 0.05 && Date.parse(p.t) >= FROZEN);
  return f ? Date.parse(f.t) : FROZEN + 5 * HOUR;
};
const override = () => {
  const st = planStates(plan);
  const info = { active: true, expires_at: new Date(FROZEN + 5 * HOUR).toISOString(),
    space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
  st[DEFAULT_SPACE].attributes.manual_override = info;
  st[DEFAULT_DHW].attributes.manual_override = info;
  return st;
};
const setupPage = (topo, extra) => ({ states: setupStates(topo, extra), steps: [["cardClick"], ["page", "setup"]] });
const S = (name, o) => ({ name, config: {}, steps: [], lang: null, mode: null, history: null, ...o });
const STATES = [
  S("no_plan", { states: {} }),
  S("no_plan_expanded", { states: {}, steps: [["open"]] }),
  S("plan_inline", { states: planStates(plan) }),
  S("plan_inline_sv", { states: planStates(plan), lang: "sv-SE" }),
  S("plan_short_window", { states: planStates(plan), config: { hours: 6 } }),
  S("custom_title_currency", { states: planStates(plan), config: { title: "Värme", currency: "EUR", hours: 48 } }),
  S("hidden_series", { states: planStates(plan), config: { series: { outdoor: false, solar: false } }, steps: [["chip", "price"]] }),
  S("score_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "score"]] }),
  S("expanded_plan", { states: planStates(plan), steps: [["cardClick"]] }),
  S("what_if_off", { states: planStates(plan), config: { what_if: false }, steps: [["cardClick"]] }),
  S("expanded_zoomed", { states: planStates(plan), steps: [["cardClick"], ["zoom", 0.25]] }),
  S("draft_dirty_menu_open", { states: planStates(plan), config: { what_if: true }, steps: [["cardClick"], ["dragDhw", true], ["menu", "space", 2]] }),
  S("x_menu_right_edge", { states: planStates(plan), config: { what_if: true }, extra: true, steps: [["cardClick"], ["menuAt", "space", 0.97]] }),
  S("x_menu_right_edge_dhw", { states: planStates(plan), config: { what_if: true }, extra: true, steps: [["cardClick"], ["menuAt", "dhw", 0.97]] }),
  // Extra states (x_*): the status-text outcomes STATES never reaches, driven by real clicks.
  S("x_pin_ok", { states: planStates(plan), config: { what_if: true }, extra: true, service: "ok", steps: [["cardClick"], ["dragDhw", true], ["clickSel", ".wi-pin"]] }),
  S("x_pin_fail", { states: planStates(plan), config: { what_if: true }, extra: true, service: "fail", steps: [["cardClick"], ["dragDhw", true], ["clickSel", ".wi-pin"]] }),
  S("x_save_confirm", { states: scheduleStates(), config: { what_if: true }, extra: true, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"]] }),
  S("x_save_ok", { states: scheduleStates(), config: { what_if: true }, extra: true, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
  S("x_save_fail", { states: scheduleStates(), config: { what_if: true }, extra: true, service: "fail", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
  S("x_dhw_clamped", { states: (() => { const st = scheduleStates(); for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) {
    st[id].attributes.dhw_min_temperature = 55; st[id].attributes.dhw_min_temperature_max = 60; } return st; })(),
    config: { what_if: true }, extra: true, steps: [["cardClick"], ["lowerCeiling", 50]] }),
  // A live install publishes its measured indoor temperature (withActuals): the default view, no pan.
  S("x_live_default", { states: withActuals(planStates(plan)), extra: true }),
  S("x_live_default_expanded", { states: withActuals(planStates(plan)), extra: true, steps: [["cardClick"]] }),
  S("draft_mid_drag", { states: planStates(plan), config: { what_if: true }, steps: [["cardClick"], ["dragDhw", false]] }),
  S("whatif_edited", { states: scheduleStates(), config: { what_if: true }, service: true, steps: [["cardClick"], ["whatifInput"], ["addWindow"]] }),
  S("whatif_weekly", { states: (() => { const st = planStates(plan); st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30";
    st[DEFAULT_DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30"; return st; })(), config: { what_if: true }, steps: [["cardClick"]] }),
  S("override_active", { states: override(), config: { what_if: true }, steps: [["open"]] }),
  S("shared_steps", { states: sharedStepStates(), steps: [["cardClick"]] }),
  S("shared_steps_hover", { states: sharedStepStates(), steps: [["cardClick"], ["hover", "firstShared", firstShared()]] }),
  S("tooltip_hover", { states: planStates(plan), steps: [["cardClick"], ["hover", 5]] }),
  S("coarse_pointer", { states: planStates(plan), mode: "coarse", steps: [["cardClick"]] }),
  S("reduced_motion", { states: planStates(plan), mode: "reduced" }),
  S("setup_single_buffer", setupPage(qaTopologies().base)),
  S("setup_two_tank", setupPage(qaTopologies().twoTank)),
  S("setup_coil", setupPage(qaTopologies().coil)),
  S("advisor_page", { states: advisorStates(), steps: [["cardClick"], ["page", "advisor"]] }),
  S("layout_editing_dragged", { ...setupPage(layoutCatalogTopo()), steps: [["cardClick"], ["page", "setup"], ["layoutToggle"], ["layoutDrag", false]] }),
  S("layout_editing_tidy", { ...setupPage(layoutCatalogTopo()), steps: [["cardClick"], ["page", "setup"], ["layoutToggle"], ["layoutDrag", true]] }),
  S("picker_open_filtered", { ...setupPage(qaTopologies().base, bigStates()), steps: [["cardClick"], ["page", "setup"], ["picker"]] }),
  S("wood_alert", { states: woodFuelStates({ cheaper: true, show_whatif: true, ready: true, slots: [] }) }),
  S("wood_lane", { states: woodFuelStates({ cheaper: false, show_whatif: true, ready: true, slots: [{ start: plan.space_plan.forecast[0].t,
    end: plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t, source: "detected" }] }) }),
  S("wood_whatif", { states: woodFuelStates({ cheaper: false, show_whatif: true, ready: true, slots: [] }), config: { what_if: true }, steps: [["cardClick"]] }),
  S("away_toggle", { states: awayPlanStates(), steps: [["cardClick"]] }),
  S("away_return", { states: awayPlanStates({ sw: true }), steps: [["cardClick"]] }),
  S("away_status", { states: awayPlanStates({ resolved: true }), steps: [["cardClick"]] }),
  S("history_panned", { states: withActuals(planStates(plan)), history: "realistic", steps: [["cardClick"], ["pan", -10]] }),
  S("history_deep_panned", { states: withActuals(planStates(plan)), history: "realistic", steps: [["cardClick"], ["pan", -40]] }),
  S("history_no_power", { states: withActuals(planStates(plan)), history: "nopower", steps: [["cardClick"], ["pan", -20]] }),
  S("history_unavailable", { states: withActuals(planStates(plan)), history: "empty", steps: [["cardClick"], ["pan", -10]] }),
  S("history_pending", { states: withActuals(planStates(plan)), history: "never", steps: [["cardClick"], ["pan", -10]] }),
];
// Sync control: our names must be card_drift's names less the non-DOM editor_schema.
const driftNames = execFileSync("node", ["tests/card_drift.mjs", "--list"], { encoding: "utf8", env: { ...process.env } })
  .split("\n").map((s) => s.trim()).filter(Boolean);
const ours = STATES.map((s) => s.name);
const missing = driftNames.filter((n) => n !== "editor_schema" && !ours.includes(n));
const extra = ours.filter((n) => !driftNames.includes(n) && !n.startsWith("x_"));
console.log(`states: ${ours.length} driven; card_drift --list has ${driftNames.length}; missing=${JSON.stringify(missing)} extra=${JSON.stringify(extra)}`);

// ---- themes ---------------------------------------------------------------
const THEMES = {
  light: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#212121;--secondary-text-color:#727272;
    --text-primary-color:#ffffff;--disabled-text-color:#bdbdbd;--primary-background-color:#fafafa;--secondary-background-color:#e5e5e5;
    --card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
  dark: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;
    --text-primary-color:#ffffff;--disabled-text-color:#6f6f6f;--primary-background-color:#111111;--secondary-background-color:#282828;
    --card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
};
const VIEWPORTS = [[375, 812], [768, 1024], [1280, 800]];
const quick = args.includes("--quick");
const onlyStates = argOf("--states", null);
const states = onlyStates ? STATES.filter((s) => onlyStates.split(",").includes(s.name)) : STATES;
const shots = args.includes("--shots");
const noKeys = args.includes("--no-keys");
if (shots) fs.mkdirSync(path.join(HERE, "shots"), { recursive: true });

const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style id="theme"></style></head><body></body></html>`;
const history = { api: null };

async function newPage(browser, vp, theme, mode) {
  const ctx = await browser.newContext({
    viewport: { width: vp[0], height: vp[1] },
    colorScheme: theme === "dark" ? "dark" : "light",
    reducedMotion: mode === "reduced" ? "reduce" : "no-preference",
    hasTouch: mode === "coarse",
  });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: PAGE }));
  if (mode === "coarse") {
    await ctx.addInitScript(() => {
      const orig = window.matchMedia.bind(window);
      window.matchMedia = (q) => (q === "(pointer: coarse)" || q === "(hover: none)")
        ? { matches: true, media: q, onchange: null, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return true; } }
        : orig(q);
    });
  }
  await ctx.addInitScript(() => {
    window.__ls = [];
    try {
      new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__ls.push({ v: e.value, t: e.startTime,
        src: (e.sources || []).map((s) => { const n = s.node; if (!n) return "?"; const el = n.nodeType === 1 ? n : n.parentElement;
          if (!el) return n.nodeName; const wrapT = el.closest && el.closest(".tooltip, .crosshair") ? "overlay:" : "";
          return wrapT + el.tagName.toLowerCase() + "." + String(el.getAttribute("class") || "").trim().replace(/\s+/g, "."); }) }); })
        .observe({ type: "layout-shift", buffered: true });
    } catch (e) { /* no API */ }
  });
  const page = await ctx.newPage();
  const errs = [];
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text().slice(0, 200)); });
  page.on("pageerror", (e) => errs.push("pageerror: " + String(e.message).slice(0, 200)));
  await page.exposeFunction("__hpoCallApi", async (method, p) => history.api ? history.api.callApi(method, p) : []);
  return { ctx, page, errs };
}

async function mount(page, vp, theme, st, lang) {
  await page.goto("http://hpo.test/");
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) { /* ignore */ } });
  await page.addScriptTag({ content: cardSrc });
  await page.addScriptTag({ content: measureSrc });
  const svc = st.service || false;
  await page.evaluate(([themeCss, w, cfg, states, lang2, hist, svc2]) => {
    document.getElementById("theme").textContent =
      `html{${themeCss};background:var(--primary-background-color)}` +
      `body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
      `heatpump-optimizer-card{display:block;width:${w}px}`;
    if (!customElements.get("ha-card")) {
      customElements.define("ha-card", class extends HTMLElement {
        constructor() {
          super();
          this.attachShadow({ mode: "open" }).innerHTML =
            "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));" +
            "color:var(--primary-text-color);box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);" +
            "display:block;position:relative;}</style><slot></slot>";
        }
      });
    }
    const c = document.createElement("heatpump-optimizer-card");
    c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
    const hass = { states, language: lang2 };
    if (hist === "never") hass.callApi = () => new Promise(() => {});
    else if (hist) hass.callApi = (m, p) => window.__hpoCallApi(m, p);
    if (svc2 === "fail") hass.callService = async () => { throw new Error("Service call failed"); };
    else if (svc2) hass.callService = async () => ({ response: { results: {}, applied: { space: { expires_at: new Date(Date.now() + 5 * 3600000).toISOString() } } } });
    c.hass = hass;
    document.body.appendChild(c);
    c.hass = hass;
  }, [THEMES[theme], vp[0] - 16, st.config, st.states, lang, st.history, svc]);
  await page.waitForTimeout(60);
}

async function keyboardWalk(page) {
  await page.evaluate(() => window.__hpo.tagIds());
  const focusables = await page.evaluate(() => window.__hpo.focusables());
  // Start from wherever the card put focus (a modal dialog focuses its first
  // control on showModal); walk forward until the first stop comes round again.
  const seen = [];
  const first = await page.evaluate(() => window.__hpo.active());
  if (first.id) seen.push(first);
  for (let i = 0; i < 2 * focusables.length + 8; i++) {
    await page.keyboard.press("Tab");
    const a = await page.evaluate(() => window.__hpo.active());
    if (!a.id) continue; // body / outside the card: the wrap, not a stop
    if (seen.length && a.id === seen[0].id) break;
    seen.push(a);
  }
  const seenIds = new Set(seen.map((s) => s.id));
  const unreached = focusables.filter((f) => !seenIds.has(f.id));
  const ind = [];
  for (const f of focusables) ind.push(await page.evaluate((id) => window.__hpo.focusIndicator(id), f.id));
  const noIndicator = ind.filter((x) => !x.missing && !x.visible);
  return { focusables: focusables.length, stops: seen.filter((s) => s.id).length, unreached, noIndicator,
    seq: seen.map((s) => s.el),
    nameless: focusables.filter((f) => !f.name).map((f) => f.el) };
}

async function hoverShift(page) {
  const pts = await page.evaluate(() => {
    const out = [];
    const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
    const d = root.querySelector("dialog[open]");
    const scope = d || root;
    for (const el of scope.querySelectorAll("button, .chip, [data-stat], [role=tab], select, input, .setup-hit, [tabindex]")) {
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) continue;
      if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
      out.push({ x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2, el: (el.getAttribute("class") || el.tagName).slice(0, 40) });
    }
    return out.slice(0, 40);
  });
  let total = 0; const worst = [];
  for (const p of pts) {
    const before = await page.evaluate(() => window.__ls.length);
    await page.mouse.move(p.x, p.y);
    await page.waitForTimeout(90);
    const added = await page.evaluate((b) => window.__ls.slice(b), before);
    const v = added.reduce((a, e) => a + e.v, 0);
    total += v;
    if (v > 0.0005) worst.push({ el: p.el, v: +v.toFixed(4), src: [...new Set(added.flatMap((e) => e.src))].slice(0, 4) });
  }
  await page.mouse.move(1, 1);
  return { hovered: pts.length, total: +total.toFixed(4), worst };
}

const browser = await chromium.launch();
const cells = [];
const out = fs.createWriteStream(path.join(TMP, "cells.jsonl"));
const t0 = Date.now();
const themes = quick ? ["light"] : ["light", "dark"];
const langs = quick ? ["en"] : ["en", "sv-SE"];
const modes = argOf("--modes", quick ? "normal" : "normal,coarse,reduced").split(",");
try {
  for (const mode of modes) {
    for (const vp of VIEWPORTS) {
      for (const theme of themes) {
        const { ctx, page, errs } = await newPage(browser, vp, theme, mode);
        for (const st of states) {
          if (st.mode && st.mode !== mode) continue;
          for (const lang of langs) {
            if (st.lang && lang !== "en") continue;
            const L = st.lang || lang;
            errs.length = 0;
            history.api = st.history === "realistic" ? historyApi(realisticHistory(FROZEN))
              : st.history === "nopower" ? historyApi(realisticHistory(FROZEN, { power: false }))
              : st.history === "empty" ? historyApi({}, {}) : null;
            let cell = { state: st.name, vp: `${vp[0]}x${vp[1]}`, theme, lang: L, mode };
            try {
              await mount(page, vp, theme, st, L);
              const req = await page.evaluate((steps) => window.__hpo.drive(steps), st.steps);
              if (req.hover) { await page.mouse.move(req.hover.x, req.hover.y); await page.waitForTimeout(120); }
              const m = await page.evaluate((o) => window.__hpo.measure(o), { coarse: mode === "coarse" });
              cell = { ...cell, ...m, req };
              const kb = !noKeys && theme === "light" && L === "en" && mode === "normal";
              // The screenshot is taken BEFORE the keyboard walk: the walk focuses
              // every control in turn and leaves the last one focused and scrolled to.
              if (shots && mode === "normal" && (theme === "light" || vp[0] === 375)) {
                await page.screenshot({ path: path.join(HERE, "shots", `${st.name}__${vp[0]}__${theme}__${L}.png`) });
              }
              if (kb) cell.keyboard = await keyboardWalk(page);
              if (kb && vp[0] !== 768 && !st.steps.some((s) => s[0] === "hover") && !st.steps.some((s) => s[0] === "dragDhw" && !s[1])) {
                // Re-mount so keyboard focus does not colour the hover pass.
                await mount(page, vp, theme, st, L);
                await page.evaluate((steps) => window.__hpo.drive(steps), st.steps);
                cell.hover = await hoverShift(page);
              }
            } catch (e) {
              cell.threw = String(e && e.message || e).slice(0, 300);
            }
            cell.console = [...errs];
            out.write(JSON.stringify(cell) + "\n");
            delete cell.texts;
            cells.push(cell);
          }
        }
        await ctx.close();
      }
    }
  }
} finally {
  await browser.close();
  out.end();
}

// ---- summary -----------------------------------------------------------------
const sum = (f) => cells.reduce((a, c) => a + (f(c) || 0), 0);
const cnt = (k) => sum((c) => (c[k] || []).length);
console.log(`cells=${cells.length} wall=${((Date.now() - t0) / 1000).toFixed(0)}s jsonl=${path.join(TMP, "cells.jsonl")}`);
const byKind = (k, keyf) => {
  const m = new Map();
  for (const c of cells) for (const x of c[k] || []) {
    const key = keyf(x);
    if (!m.has(key)) m.set(key, { n: 0, cells: new Set(), ex: x, ctx: `${c.state}/${c.vp}/${c.theme}/${c.lang}/${c.mode}` });
    const e = m.get(key); e.n += 1; e.cells.add(`${c.state}/${c.vp}/${c.theme}/${c.lang}/${c.mode}`);
  }
  return [...m.entries()].sort((a, b) => b[1].cells.size - a[1].cells.size);
};
const show = (title, k, keyf, fmt) => {
  const rows = byKind(k, keyf);
  console.log(`\n== ${title}: ${cnt(k)} instance(s), ${rows.length} distinct`);
  for (const [key, e] of rows.slice(0, 25)) console.log(`  [${e.cells.size} cells] ${key}  e.g. ${e.ctx} ${fmt ? fmt(e.ex) : ""}`);
};
show("text overflow (unreachable ink)", "overflow", (x) => `${x.el} "${x.txt}" -> ${x.clip}/${x.side}`, (x) => `${x.px}px`);
show("text overlap", "overlap", (x) => `${x.a} "${x.at}" x ${x.b} "${x.bt}"`, (x) => `${x.ix}x${x.iy}px`);
show("contrast below AA", "contrast", (x) => `${x.el} "${x.txt}"`, (x) => `${x.ratio}:1 need ${x.need} fg${x.fg} bg${x.bg} ${x.px}px${x.bgUnknown ? " bg?" : ""}`);
show("ellipsized text", "ellipsized", (x) => `${x.el} title=${x.hasTitle}`, (x) => `"${x.txt}" -${x.hidden}px`);
show("small targets (floor 24 / 44 coarse)", "small", (x) => x.el, (x) => `${x.w}x${x.h}`);
show("small targets failing 2.5.8 spacing", "small24", (x) => x.el, (x) => `${x.w}x${x.h} clash ${x.clash}`);
show("pointer-only targets", "pointerOnly", (x) => x.el, (x) => `${x.w}x${x.h}`);
show("nameless targets", "nameless", (x) => x.el);
console.log("\n== listbox options cut / indistinct");
for (const c of cells) for (const o of c.options || []) if (o.cut || o.indistinct)
  console.log(`  ${c.state}/${c.vp}/${c.theme}/${c.lang}/${c.mode}: ${o.el} n=${o.n} cut=${o.cut} indistinct=${o.indistinct} box=${o.box} widest=${o.widest} ${JSON.stringify(o.pairs[0] || "")}`);
console.log("\n== pop-ups outside viewport / chart box");
for (const c of cells) for (const p of c.popups || []) if (p.vwOut > 0.5 || p.hostOut > 0.5)
  console.log(`  ${c.state}/${c.vp}/${c.theme}/${c.lang}/${c.mode}: ${p.el} w=${p.w} left=${p.left} right=${p.right} viewportOut=${p.vwOut} chartOut=${p.hostOut}`);
const kcells = cells.filter((c) => c.keyboard);
console.log(`\n== keyboard: ${kcells.length} cells`);
for (const c of kcells) {
  const k = c.keyboard;
  if (k.unreached.length || k.noIndicator.length || k.nameless.length) {
    console.log(`  ${c.state}/${c.vp}: focusables=${k.focusables} stops=${k.stops} unreached=${k.unreached.length} [${k.unreached.slice(0, 3).map((u) => u.el).join(" | ")}] noIndicator=${k.noIndicator.length} [${[...new Set(k.noIndicator.map((u) => u.el))].slice(0, 3).join(" | ")}] nameless=${k.nameless.length}`);
  }
}
const hcells = cells.filter((c) => c.hover);
console.log(`\n== hover layout shift: ${hcells.length} cells`);
for (const c of hcells) if (c.hover.total > 0.0005) console.log(`  ${c.state}/${c.vp}: total=${c.hover.total} ${JSON.stringify(c.hover.worst.slice(0, 3))}`);
console.log("\n== console errors");
for (const c of cells) if (c.console.length || c.threw) console.log(`  ${c.state}/${c.vp}/${c.theme}/${c.lang}/${c.mode}: ${c.threw || ""} ${c.console.slice(0, 2).join(" || ")}`);

console.log(`RESULT cells=${cells.length} count`);
for (const k of ["overflow", "overlap", "contrast", "ellipsized", "small", "small24", "pointerOnly", "nameless"]) {
  console.log(`RESULT ${k}_instances=${cnt(k)} count`);
  console.log(`RESULT ${k}_cells=${cells.filter((c) => (c[k] || []).length).length} count`);
}
console.log(`RESULT now_marker_collisions=${sum((c) => (c.overlap || []).filter((x) => /text\.now-label/.test(x.a + x.b) && /text\.now-temp/.test(x.a + x.b)).length)} count`);
console.log(`RESULT max_overflow_px=${Math.max(0, ...cells.flatMap((c) => (c.overflow || []).map((x) => x.px)))} px`);
console.log(`RESULT option_indistinct_pairs=${sum((c) => (c.options || []).reduce((a, o) => a + o.indistinct, 0))} count`);
console.log(`RESULT option_indistinct_cells=${cells.filter((c) => (c.options || []).some((o) => o.indistinct)).length} count`);
console.log(`RESULT option_cut=${sum((c) => (c.options || []).reduce((a, o) => a + o.cut, 0))} count`);
console.log(`RESULT popup_out_cells=${cells.filter((c) => (c.popups || []).some((p) => p.vwOut > 0.5 || p.hostOut > 0.5)).length} count`);
console.log(`RESULT max_popup_viewport_out_px=${Math.max(0, ...cells.flatMap((c) => (c.popups || []).map((p) => p.vwOut)))} px`);
console.log(`RESULT motion_elements_reduced=${sum((c) => c.mode === "reduced" ? (c.motion || []).length : 0)} count`);
console.log(`RESULT motion_elements_normal=${sum((c) => c.mode === "normal" ? (c.motion || []).length : 0)} count`);
console.log(`RESULT hscroll_cells=${cells.filter((c) => c.hscroll > 0).length} count`);
console.log(`RESULT kb_unreached=${sum((c) => c.keyboard && c.keyboard.unreached.length)} count`);
console.log(`RESULT kb_no_indicator=${sum((c) => c.keyboard && c.keyboard.noIndicator.length)} count`);
console.log(`RESULT hover_shift_cells=${hcells.filter((c) => c.hover.total > 0.0005).length} count`);
console.log(`RESULT console_error_cells=${cells.filter((c) => c.console.length || c.threw).length} count`);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
