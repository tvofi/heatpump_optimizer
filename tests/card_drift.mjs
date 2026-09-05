// The dashboard card's markup gate.
//
//     node tests/card_drift.mjs [ref]          # default: $GOLDEN_REF, else origin/main
//     node tests/card_drift.mjs --list         # the states it renders
//
// tests/card.mjs asserts what the card's markup CONTAINS; tests/card_browser.mjs
// measures what Chromium lays out. Neither says the markup is the SAME as it
// was, and "no behaviour change" is exactly the claim every refactor of the
// card makes. This script checks that claim the way tests/env_drift.py checks
// the solver's: the working tree's card and the comparison ref's card are
// run through the same states, in the same process, against the same plan
// payload and the same frozen clock, and every state's rendered tree must
// come out byte for byte identical. A state that differs must be claimed in
// tests/golden/card_claimed_drift.txt, with a reason, by the release that
// moves it -- unclaimed drift fails, and so does a claim nothing matched.
//
// Differential rather than golden-based on purpose. A committed rendering
// would move with Node's ICU (the AM/PM space in `toLocaleTimeString`), the
// machine's time zone, and every optimizer change that reshapes the payload
// plan_view.py writes. Two cards rendered side by side in one process share
// all of those, so what remains is the change's own footprint.
//
// The comparison ref's card is read with `git show`; the card is one file, so
// no worktree is needed. Both sides run in their own vm context from the
// shared rig (tests/card_rig.mjs), each with its own module state, its own
// localStorage, and its own frozen Date at the same instant.
import fs from "fs";
import os from "os";
import path from "path";
import crypto from "crypto";
import { execFileSync } from "child_process";
import { fileURLToPath } from "url";
import {
  CARD_PATH, EDITOR_TAG, DEFAULT_SPACE, DEFAULT_DHW, HOUR,
  CLAIM_FILE, parseClaims, claimVersionError,
  makeCardContext, loadCard, collect, frozenDateClass, buildCard,
  planStates, setupSensorStates, qaTopologies, layoutCatalogTopo,
} from "./card_rig.mjs";

const testsDir = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(testsDir, "..");
const args = process.argv.slice(2);

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

// --- the states ------------------------------------------------------------
// Each drives one card into one situation and returns the rendered tree. The
// names are what tests/golden/card_claimed_drift.txt refers to.
const noop = { stopPropagation() {}, preventDefault() {} };
const svgOf = (card) => card.shadowRoot.querySelector(".chartwrap svg");
const fire = (el, type, ev) => (el._listeners[type] || []).forEach((f) => f(ev));
const xOf = (geom, t) =>
  geom.plotL + ((t - geom.windowStart) / (geom.windowEnd - geom.windowStart)) * geom.plotW;
const evAt = (geom, t, target) =>
  ({ clientX: xOf(geom, t), clientY: 0, target, ...noop });
// The diagram's viewBox is 720 units and the stub measures every element
// 900 px wide, so a viewBox unit is 1.25 px.
const pxOf = (u) => (u * 900) / 720;
const layoutEv = (pt, target) =>
  ({ clientX: pxOf(pt.x), clientY: pxOf(pt.y), target: target || {}, ...noop });

const statStates = () => ({
  "sensor.heat_pump_optimizer_predicted_savings": {
    state: "12.34", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_savings_percentage": {
    state: "8.2", attributes: {} },
  "sensor.heat_pump_optimizer_optimization_score": {
    state: "82", attributes: { envelope: 90, machine: 75 } },
  "sensor.heat_pump_optimizer_plan_narrative": {
    state: "cheap_price", attributes: {
      lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
});

const scheduleStates = (plan) => {
  const st = planStates(plan);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7;
  st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
  return st;
};

const sharedStepStates = (plan) => {
  const st = planStates(plan);
  const sp = st[DEFAULT_SPACE].attributes.forecast;
  const heating = new Set(sp.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
  st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) =>
    heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
  return st;
};

const setupStates = (plan, topo, extra) => {
  const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
  st[DEFAULT_SPACE].attributes.setup_topology = topo;
  return st;
};


// The two sides of a comparison need not speak the same dialect: the
// baseline is the comparison ref's card, which may predate the decomposition
// (#136), and the tree's card has no `_` seams once PR 9 landed. Every
// driver goes through these, which take whichever the card offers.
const api = {
  open: (c) => (c.dialog ? c.dialog.open() : c._openExpanded()),
  setPage: (c, page) => {
    if (c.dialog) c.dialog.page = page;
    else c._dialogPage = page;
  },
  draft: (c) => (c.manual ? c.manual.draft() : c._draftRuns()),
  bounds: (c) => (c.manual ? c.manual.bounds() : c._editBounds()),
  zoom: (c, f) => (c.view ? c.view.zoom(f) : c._zoomView(f)),
  openMenu: (c, ...a) => (c.lanes ? c.lanes.openMenu(...a) : c._openSlotMenu(...a)),
  whatIfInput: (c, ev) => (c.whatIf ? c.whatIf.onInput(ev) : c._onWhatIfInput(ev)),
  addWindow: (c, ev) => (c.whatIf ? c.whatIf.onAddWindow(ev) : c._onAddWindow(ev)),
  disarmWhatIf: (c) => {
    if (c.whatIf) { clearTimeout(c.whatIf.timer); c.whatIf.timer = null; }
    else { clearTimeout(c._whatIfTimer); c._whatIfTimer = null; }
  },
  // The layout editor has had three homes: `_onLayout*` before the
  // decomposition, `layout` after it, and `layoutEditor` since v5.4.20 --
  // `layout` had to go because Lovelace assigns `card.layout` itself and
  // silently replaced ours. This gate renders BOTH trees with the harness
  // from HEAD, so every name a comparison ref might still use has to be
  // tried here. Miss one and the drag is a no-op on that side, which shows
  // up as drift in the editor's buttons rather than as the failure it is.
  layoutOf: (c) => c.layoutEditor || c.layout || null,
  boxes: (c) => (api.layoutOf(c) ? api.layoutOf(c).boxes : c._layoutBoxes) || [],
  layoutDown: (c, ev) => {
    const l = api.layoutOf(c);
    return l ? l.onDown(ev) : c._onLayoutDown(ev);
  },
  layoutMove: (c, ev) => {
    const l = api.layoutOf(c);
    return l ? l.onMove(ev) : c._onLayoutMove(ev);
  },
  layoutUp: (c, ev) => {
    const l = api.layoutOf(c);
    return l ? l.onUp(ev) : c._onLayoutUp(ev);
  },
};

const setupPage = (side, topo, extra) => {
  const c = buildCard(side.Card, setupStates(side.plan, topo, extra));
  c._onCardClick({});
  api.setPage(c, "setup");
  c._render();
  return c;
};

// A big install: 400 sensors whose names give nothing away, plus two probes
// with identical friendly names, so the picker's cap and filter both show.
const bigStates = () => {
  const st = {};
  for (let i = 0; i < 400; i++) {
    st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = {
      state: "20.0",
      attributes: { unit_of_measurement: "°C",
        friendly_name: `Probe ${String(i).padStart(3, "0")}` },
    };
  }
  st["sensor.vedpanna_temperatur_temperature"] = {
    state: "71.2", attributes: { unit_of_measurement: "°C",
      friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = {
    state: "48.9", attributes: { unit_of_measurement: "°C",
      friendly_name: "Vedpanna temperatur" } };
  return st;
};

const STATES = [
  { name: "no_plan",
    drive: (s) => buildCard(s.Card, {}) },
  { name: "no_plan_expanded",
    drive: (s) => { const c = buildCard(s.Card, {}); api.open(c); return c; } },
  { name: "plan_inline",
    drive: (s) => buildCard(s.Card, planStates(s.plan)) },
  { name: "plan_inline_sv",
    drive: (s) => buildCard(s.Card, planStates(s.plan), {}, { language: "sv-SE" }) },
  { name: "plan_short_window",
    drive: (s) => buildCard(s.Card, planStates(s.plan), { hours: 6 }) },
  { name: "custom_title_currency",
    drive: (s) => buildCard(s.Card, planStates(s.plan),
      { title: "Värme", currency: "EUR", hours: 48 }) },
  { name: "hidden_series",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan), { series: { outdoor: false, solar: false } });
      const chip = c.shadowRoot.querySelectorAll(".chip")
        .find((el) => el.getAttribute("data-key") === "price");
      if (chip) fire(chip, "click", { currentTarget: chip, ...noop });
      return c;
    } },
  { name: "score_open",
    drive: (s) => {
      const c = buildCard(s.Card, { ...planStates(s.plan), ...statStates() });
      const stat = c.shadowRoot.querySelector('[data-stat="score"]');
      if (stat) fire(stat, "click", { ...noop });
      return c;
    } },
  { name: "expanded_plan",
    drive: (s) => { const c = buildCard(s.Card, planStates(s.plan)); c._onCardClick({}); return c; } },
  { name: "what_if_off",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan), { what_if: false });
      c._onCardClick({});
      return c;
    } },
  { name: "expanded_zoomed",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan));
      c._onCardClick({});
      api.zoom(c, 0.25);
      return c;
    } },
  { name: "draft_dirty_menu_open",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan), { what_if: true });
      c._onCardClick({});
      const geom = c._geom;
      const runs = api.draft(c).dhw;
      const [lo] = api.bounds(c);
      const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
      const svg = svgOf(c);
      if (i >= 0) {
        const before = { ...runs[i] };
        const target = { dataset: { channel: "dhw", index: String(i) } };
        fire(svg, "pointerdown", evAt(geom, before.start + 60000, target));
        fire(svg, "pointermove", evAt(geom, before.start + 60000 + HOUR, target));
        fire(svg, "pointerup", {});
      }
      api.openMenu(c, "space", geom.windowStart + 2 * HOUR, 120, 40, svg, false);
      return c;
    } },
  // A drag in flight: the lanes redrawn in place, before the pointer is
  // released and a full render draws everything afresh. The one moment the
  // inline copy's lanes are not drawn by the chart itself (#138).
  { name: "draft_mid_drag",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan), { what_if: true });
      c._onCardClick({});
      const geom = c._geom;
      const runs = api.draft(c).dhw;
      const [lo] = api.bounds(c);
      const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
      if (i >= 0) {
        const target = { dataset: { channel: "dhw", index: String(i) } };
        fire(svgOf(c), "pointerdown", evAt(geom, runs[i].start + 60000, target));
        fire(svgOf(c), "pointermove", evAt(geom, runs[i].start + 60000 + HOUR, target));
      }
      return c;
    } },
  { name: "whatif_edited",
    drive: (s) => {
      const c = buildCard(s.Card, scheduleStates(s.plan), { what_if: true });
      c._hass = { states: c._hass.states, callService: async () => ({ response: { results: {} } }) };
      c._onCardClick({});
      api.whatIfInput(c, {
        ...noop,
        target: { value: "42", classList: { contains: (x) => x === "wi-dhw-min" } },
      });
      // The slider armed a simulate; nothing here should reach a service.
      api.disarmWhatIf(c);
      api.addWindow(c, { ...noop });
      return c;
    } },
  { name: "whatif_weekly",
    drive: (s) => {
      const st = planStates(s.plan);
      st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30";
      st[DEFAULT_DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
      const c = buildCard(s.Card, st, { what_if: true });
      c._onCardClick({});
      return c;
    } },
  { name: "override_active",
    drive: (s) => {
      const st = planStates(s.plan);
      const info = {
        active: true,
        expires_at: new Date(s.FROZEN + 5 * HOUR).toISOString(),
        space_slots: [], dhw_slots: [], released_space: [], released_dhw: [],
      };
      st[DEFAULT_SPACE].attributes.manual_override = info;
      st[DEFAULT_DHW].attributes.manual_override = info;
      const c = buildCard(s.Card, st, { what_if: true });
      api.open(c);
      return c;
    } },
  // The shared-step band and its tooltip sentence need both circuits planned
  // in the same quarter hour, which the recorded plan may not contain: force
  // hot water onto the heating steps so the <pattern> and the sentence render.
  { name: "shared_steps",
    drive: (s) => {
      const c = buildCard(s.Card, sharedStepStates(s.plan));
      c._onCardClick({});
      return c;
    } },
  { name: "shared_steps_hover",
    drive: (s) => {
      const c = buildCard(s.Card, sharedStepStates(s.plan));
      c._onCardClick({});
      const svg = svgOf(c);
      const plot = c._plot;
      const sp = sharedStepStates(s.plan)[DEFAULT_SPACE].attributes.forecast;
      const first = sp.find((p) => Number(p.space_power) > 0.05 && Date.parse(p.t) >= plot.windowStart);
      const t = first ? Date.parse(first.t) : plot.windowStart + 5 * HOUR;
      c._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(t) });
      return c;
    } },
  { name: "tooltip_hover",
    drive: (s) => {
      const c = buildCard(s.Card, planStates(s.plan));
      c._onCardClick({});
      const svg = svgOf(c);
      const plot = c._plot;
      c._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(plot.windowStart + 5 * HOUR) });
      return c;
    } },
  { name: "coarse_pointer",
    drive: (s) => {
      s.coarseTouch.on = true;
      const c = buildCard(s.Card, planStates(s.plan));
      c._onCardClick({});
      return c;
    } },
  { name: "reduced_motion",
    drive: (s) => {
      s.reducedMotion.on = true;
      return buildCard(s.Card, planStates(s.plan));
    } },
  { name: "setup_single_buffer",
    drive: (s) => setupPage(s, qaTopologies().base) },
  { name: "setup_two_tank",
    drive: (s) => setupPage(s, qaTopologies().twoTank) },
  { name: "setup_coil",
    drive: (s) => setupPage(s, qaTopologies().coil) },
  { name: "layout_editing_dragged",
    drive: (s) => {
      const c = setupPage(s, layoutCatalogTopo());
      const toggle = c.shadowRoot.querySelector(".layout-edit-toggle");
      if (toggle) fire(toggle, "click", { ...noop });
      const box = api.boxes(c).find((b) => b.place === "buffer_tank");
      if (box) {
        const from = { x: box.x + box.w / 2, y: box.y + box.h / 2 };
        const to = { x: from.x + 40, y: from.y + 30 };
        api.layoutDown(c, layoutEv(from, { dataset: {} }));
        api.layoutMove(c, layoutEv({ x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 }));
        api.layoutUp(c, layoutEv(to));
      }
      return c;
    } },
  { name: "layout_editing_tidy",
    drive: (s) => {
      const c = setupPage(s, layoutCatalogTopo());
      const toggle = c.shadowRoot.querySelector(".layout-edit-toggle");
      if (toggle) fire(toggle, "click", { ...noop });
      const box = api.boxes(c).find((b) => b.place === "buffer_tank");
      if (box) {
        const from = { x: box.x + box.w / 2, y: box.y + box.h / 2 };
        const to = { x: from.x + 40, y: from.y + 30 };
        api.layoutDown(c, layoutEv(from, { dataset: {} }));
        api.layoutMove(c, layoutEv({ x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 }));
        api.layoutUp(c, layoutEv(to));
      }
      const tidy = c.shadowRoot.querySelector(".layout-tidy");
      if (tidy) fire(tidy, "click", { ...noop });
      return c;
    } },
  { name: "picker_open_filtered",
    drive: (s) => {
      const c = setupPage(s, qaTopologies().base, bigStates());
      const hit = c.shadowRoot.querySelectorAll(".setup-hit")
        .find((h) => h.dataset.key === "wood_tank_top_entity");
      if (hit) fire(hit, "click", { currentTarget: hit, ...noop });
      const box = c.shadowRoot.querySelector(".sp-filter");
      if (box) {
        box.value = "vedpanna";
        fire(box, "input", { currentTarget: box, target: box });
      }
      return c;
    } },
  { name: "editor_schema",
    drive: (s) => {
      const Editor = s.ctx.customElements.get(EDITOR_TAG);
      const e = new Editor();
      e.setConfig({ type: "custom:heatpump-optimizer-card", hours: 12, series: { solar: false } });
      e.hass = { states: {}, language: "en" };
      return { text: JSON.stringify({ schema: e._schema(), data: e._data() }, null, 1) };
    } },
];

if (args.includes("--list")) {
  for (const st of STATES) console.log(st.name);
  process.exit(0);
}

// --- serialisation ---------------------------------------------------------
// The stub's innerHTML getter returns the string that was set and never
// re-serialises, so a `setAttribute`, `textContent` or `.disabled` written
// after the parse is invisible in `_html`. Walk the tree for those, and take
// every node's `_html` along the way (see `collect` in the rig for why the
// nested ones matter).
const NODE_INTERNALS = new Set([
  "tagName", "children", "style", "_html", "_text", "_listeners", "dataset",
  "classList", "parentNode", "shadowRoot",
]);
function serialize(node, depth, out) {
  const pad = "  ".repeat(depth);
  const attrs = Object.keys(node)
    .filter((k) => !NODE_INTERNALS.has(k) && typeof node[k] !== "function")
    .sort()
    .map((k) => `${k}=${JSON.stringify(node[k])}`);
  const classes = [...node.classList._s];
  // `class` above is the parsed attribute; the live classList can differ
  // from it once the card toggles classes, so both are recorded.
  if (classes.length) attrs.push(`classes=${JSON.stringify(classes)}`);
  const ds = Object.keys(node.dataset).sort().map((k) => `${k}:${JSON.stringify(node.dataset[k])}`);
  if (ds.length) attrs.push(`dataset={${ds.join(",")}}`);
  const style = Object.keys(node.style).sort().map((k) => `${k}:${JSON.stringify(node.style[k])}`);
  if (style.length) attrs.push(`style={${style.join(",")}}`);
  out.push(`${pad}<${node.tagName}${attrs.length ? " " + attrs.join(" ") : ""}>`);
  if (node._text) out.push(`${pad}  text=${JSON.stringify(node._text)}`);
  if (node._html) out.push(`${pad}  html=${JSON.stringify(node._html)}`);
  for (const c of node.children) serialize(c, depth + 1, out);
  return out;
}
const dumpOf = (result) => {
  if (result && typeof result.text === "string") return result.text;
  return serialize(result.shadowRoot, 0, []).join("\n") + "\n";
};

// --- the two sides ---------------------------------------------------------
function git(...a) {
  return execFileSync("git", a, { cwd: repo, encoding: "utf8" });
}
function rev(r) {
  try {
    return git("rev-parse", "--verify", "--quiet", `${r}^{commit}`).trim() || null;
  } catch (e) {
    return null;
  }
}
// `null` when the ref has no such file (a baseline older than the claim
// file, say); git's own complaint about that is expected and stays quiet.
function showAt(sha, file) {
  try {
    return execFileSync("git", ["show", `${sha}:${file}`],
      { cwd: repo, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
  } catch (e) {
    return null;
  }
}

const defaultPlan = path.join(
  "/tmp",
  `plandata-${crypto.createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`
);
const planPath = process.env.HPO_PLANDATA || defaultPlan;
if (!fs.existsSync(planPath)) {
  fail(`plan payload ${planPath} not found -- run tests/plan_view.py first`);
}
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));

const refName = args.find((a) => !a.startsWith("--")) || process.env.GOLDEN_REF || "origin/main";
const sha = rev(refName);
if (!sha) fail(`'${refName}' does not resolve to a commit here`);
const head = rev("HEAD");
const treeSrc = fs.readFileSync(path.join(repo, CARD_PATH), "utf8");
const baseSrc = showAt(sha, CARD_PATH);
if (baseSrc === null) fail(`${refName} (${sha.slice(0, 12)}) has no ${CARD_PATH}`);
// A ref that resolves to HEAD is env_drift.py's self-comparison trap: in CI
// it means a misresolved baseline, and a tree compared against itself is
// byte-identical by construction. It is also every developer's situation
// before the first commit on a branch -- and there the working tree's card
// genuinely differs from HEAD's, which is exactly the comparison they want.
// Refuse only the vacuous case: same commit AND the same card source.
if (sha === head && baseSrc === treeSrc) {
  console.error(
    `SELF-COMPARISON: '${refName}' resolves to ${head.slice(0, 12)}, which is HEAD,\n` +
    "and the working tree's card is that commit's card. Compared against itself\n" +
    "it is byte-identical by construction, so no drift can ever be reported.\n" +
    "Pass the ref this change forked from -- the merge-base for a PR, HEAD^1\n" +
    "for a push to main -- or set GOLDEN_REF."
  );
  process.exit(1);
}
if (sha === head) {
  console.log(`card_drift: ${refName} is HEAD; comparing the working tree's uncommitted card against it`);
}

const version = fs.readFileSync(path.join(repo, "VERSION"), "utf8").trim();
const claimPath = path.join(repo, CLAIM_FILE);
const treeClaims = parseClaims(fs.existsSync(claimPath) ? fs.readFileSync(claimPath, "utf8") : "");
const baseClaims = parseClaims(showAt(sha, CLAIM_FILE) || "");

let fails = 0;
const stampError = claimVersionError(treeClaims.declared, version);
if (stampError) {
  console.log(stampError);
  fails += 1;
}

// A claim list that is exactly the baseline's -- same names, same reasons --
// was written for the baseline's diff, not this one (env_drift.py's
// inherited-claims rule). An empty list claims nothing and is always fine.
const sameClaims =
  treeClaims.claims.size > 0 &&
  treeClaims.claims.size === baseClaims.claims.size &&
  [...treeClaims.claims].every(([k, v]) => baseClaims.claims.get(k) === v);
if (sameClaims) {
  console.log(
    `INHERITED CLAIMS: ${CLAIM_FILE} claims exactly what ${refName} already claims -- ` +
    `the same ${treeClaims.claims.size} state(s), with the same reasons: ` +
    `${[...treeClaims.claims.keys()].sort().join(", ")}. Rewrite the list for THIS diff.`
  );
  fails += 1;
}

function makeSide(src, label) {
  const rig = makeCardContext();
  let Card;
  try {
    Card = loadCard(rig.ctx, src);
  } catch (e) {
    fail(`${label} card failed to load: ${e && e.message}`);
  }
  const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
  rig.ctx.Date = frozenDateClass(Date, FROZEN);
  return { ...rig, Card, FROZEN, plan, label };
}

function resetSide(s) {
  for (const k of Object.keys(s.store)) delete s.store[k];
  for (const k of Object.keys(s.winListeners)) delete s.winListeners[k];
  for (const k of Object.keys(s.docListeners)) delete s.docListeners[k];
  s.intervals.clear();
  s.coarseTouch.on = false;
  s.reducedMotion.on = false;
  s.document.activeElement = s.document.body;
  // The shared-step pattern ids count up per render, process-wide.
  s.Card._sharedPatternSeq = 0;
}

function renderAll(side) {
  const out = new Map();
  for (const st of STATES) {
    resetSide(side);
    let text;
    try {
      text = dumpOf(st.drive(side));
    } catch (e) {
      text = `THREW: ${e && e.stack ? e.stack : e}\n`;
    }
    out.set(st.name, text);
  }
  return out;
}

const treeOut = renderAll(makeSide(treeSrc, "working tree"));
const baseOut = renderAll(makeSide(baseSrc, refName));

// --- compare -------------------------------------------------------------
function diffText(a, b, name) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "hpo-card-drift-"));
  const fa = path.join(dir, `${name}.${refName.replace(/[^\w.-]+/g, "_")}`);
  const fb = path.join(dir, `${name}.tree`);
  try {
    fs.writeFileSync(fa, a);
    fs.writeFileSync(fb, b);
    try {
      execFileSync("diff", ["-u", fa, fb], { encoding: "utf8" });
      return "";
    } catch (e) {
      const text = e.stdout || "";
      if (text) return text;
    }
    // No diff(1): the first differing line, with a little context.
    const la = a.split("\n"), lb = b.split("\n");
    let i = 0;
    while (i < la.length && i < lb.length && la[i] === lb[i]) i++;
    const ctx = (lines) => lines.slice(Math.max(0, i - 3), i + 4).join("\n");
    return `--- ${refName}\n${ctx(la)}\n+++ tree\n${ctx(lb)}\n`;
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

console.log(`card_drift: ${refName} = ${sha.slice(0, 12)}, tree = ${head.slice(0, 12)}, ${STATES.length} states`);
const moved = [];
const claimed = treeClaims.claims;
for (const st of STATES) {
  const a = baseOut.get(st.name), b = treeOut.get(st.name);
  if (a === b) {
    console.log(`  identical  ${st.name}`);
    continue;
  }
  moved.push(st.name);
  const reason = claimed.get(st.name);
  if (reason) {
    console.log(`  CLAIMED    ${st.name} -- ${reason}`);
  } else {
    console.log(`  DRIFT      ${st.name} (unclaimed)`);
    fails += 1;
  }
  const d = diffText(a, b, st.name).split("\n");
  const shown = d.slice(0, 120);
  console.log(shown.map((l) => `        ${l}`).join("\n"));
  if (d.length > shown.length) console.log(`        ... ${d.length - shown.length} more line(s)`);
}
const stale = [...claimed.keys()].filter((k) => !moved.includes(k));
for (const name of stale) {
  const known = STATES.some((s) => s.name === name);
  console.log(
    `  STALE CLAIM ${name} -- ${known ? "listed in " + CLAIM_FILE + " but this change does not move it" : "not a state this gate renders (see --list)"}`
  );
  fails += 1;
}

console.log();
if (fails) {
  console.log(
    `card_drift: ${fails} problem(s). Unclaimed drift is a behaviour change the\n` +
    `release has not owned up to; claim each moved state in ${CLAIM_FILE} with a\n` +
    "reason that describes THIS change, and delete claims that no longer move."
  );
  process.exit(1);
}
console.log(
  moved.length
    ? `card_drift: ${moved.length} state(s) moved and claimed, ${STATES.length - moved.length} identical`
    : `card_drift: identical in all ${STATES.length} states`
);
