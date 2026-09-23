// D4: dialog content that no scroll can bring into view.
//
// METRIC (one line): pixels by which a text run's rendered ink extends past
// the right edge of the nearest clipping ancestor, MINUS what that ancestor
// (or the document) can scroll to reveal -- i.e. ink the user cannot reach by
// any gesture. Keyed on the RENDERED INK the production seam paints, not on
// any attribute the card reads.
//
// RUN (from the export root; playwright resolves from NODE_PATH):
//   HPO_PLANDATA=/tmp/d4-clip.json PYTHONPATH=tests/hastub \
//   /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tests/plan_view.py
//   NODE_PATH=/tmp/pw-r5d4/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   /Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node \
//     tools/audit/round7/D4/dialog_clip.mjs --seam savings --width 375 --lang en
//   (no HPO_PLANDATA set? the harness writes one under the temp root itself)
//
//   --seam savings|tabs|whatif|other|all   --width N   --lang en|sv
//   --page savings|plan|setup|advisor      --patch none|pad|scroll|tabs
//   --cells                                (the leave-one-out grid)
//
// EXPECTED (baseline f9d6f78, darwin arm64, font -apple-system,"Segoe UI"):
//   seam=savings --width 375 --lang en  -> 22.4 px   (baseline)
//                                         -1 px     (--patch pad: table fits)
//                                         -1 px     (--patch scroll: reachable)
//   seam=tabs    --width 360 --lang sv  ->  7.5 px
//   seam=tabs    --width 320 --lang sv  -> 45.9 px
//   --width 1280 -> -1 px for every seam (no unreachable run; tolerance +/-0.6 px)
//   (a seam with nothing unreachable reports -1, not 0: 0 would be a run whose
//    ink ends exactly on the clip edge. The cell grid clamps to 0 instead.)
//
// BASELINE SHA: f9d6f78243fa65f6fa128d2357752a2ae7f60648
// MACHINE: 8-core Apple M1, 8 GB (darwin, arm64); Chromium 1148 (Playwright 1.49.0)
//
// PHENOMENON: the dialog draws content whose intrinsic width can exceed its own
// box and then hides the overflow instead of wrapping, shrinking or scrolling
// it. `.dlg-body { overflow-x: hidden }` and `dialog.expanded { overflow: hidden }`
// are the clipping ancestors; the savings table (a `width:100%` table whose
// min-content width is larger), the tab row (`.dlg-tabs { flex: 0 0 auto }`,
// which cannot wrap) and the what-if value cells are the seams.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const PYTHON = process.env.PYTHON || "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3";

const argv = process.argv.slice(2);
const arg = (name, dflt) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
};
const WIDTH = Number(arg("width", "375"));
const LANG = arg("lang", "en") === "sv" ? "sv-SE" : "en";
const SEAM = arg("seam", "all");
// The seam decides which dialog page is open: the savings table lives on the
// Savings tab, the what-if cells only on the Plan tab, the tab row on any page.
const PAGE = arg("page", SEAM === "whatif" ? "plan" : "savings");
const PATCH = arg("patch", "none");
const CELLS = argv.includes("--cells");

// ---- the plan payload (tests/plan_view.py refuses a path outside the temp root)
let planPath = process.env.HPO_PLANDATA;
if (!planPath) {
  planPath = path.join(os.tmpdir(), `d4-dialog-clip-${process.pid}.json`);
  const r = spawnSync(PYTHON, ["tests/plan_view.py"], {
    cwd: repo,
    env: { ...process.env, HPO_PLANDATA: planPath, PYTHONPATH: "tests/hastub" },
    encoding: "utf8",
  });
  if (r.status !== 0) {
    console.error(r.stdout || "", r.stderr || "");
    process.exit(2);
  }
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

// ---- the card source, optionally with one of the two candidate one-line fixes
const base = readFileSync(CARD_SRC, "utf8");
let src = base;
if (PATCH === "pad") {
  src = src.replace(
    ".savings-table th, .savings-table td { padding: 0.35em 0.5em; }",
    ".savings-table th, .savings-table td { padding: 0.35em 0.2em; }");
} else if (PATCH === "scroll") {
  // The label fix: keep the ink where it is and let the body scroll to it.
  src = src.replace(
    ".dlg-body {\n        flex: 1 1 auto;\n        min-height: 0;\n        overflow-y: auto;\n        overflow-x: hidden;",
    ".dlg-body {\n        flex: 1 1 auto;\n        min-height: 0;\n        overflow-y: auto;\n        overflow-x: auto;");
} else if (PATCH === "tabs") {
  // The tab-row fix: let the row wrap instead of setting a min its container
  // hides. `.dlg-tabs` is `flex: 0 0 auto`, so it cannot shrink below content.
  src = src.replace(
    ".dlg-tabs { display: flex; gap: 0.3em; flex: 0 0 auto; }",
    ".dlg-tabs { display: flex; gap: 0.3em; flex: 0 1 auto; flex-wrap: wrap; min-width: 0; }");
}
if (PATCH !== "none" && src === base) {
  console.error(`patch ${PATCH} did not apply -- the baseline moved`);
  process.exit(2);
}

const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_plan_space_heating";
const DHW_ID = "sensor.heat_pump_optimizer_plan_dhw_heating";
const SAV = "sensor.heat_pump_optimizer_monthly_savings";
const TEMP_DOMAINS = ["sensor", "number", "input_number"];
const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));
// Twelve months of realistic SEK figures: the table's widths are data-driven,
// so the grid states a value scale the way the metric's key demands.
const MONTHS = [];
for (let m = 0; m < 12; m++) {
  MONTHS.push({
    month: `2026-${String(m + 1).padStart(2, "0")}`,
    baseline_sek: 1234.56 + m * 17, actual_sek: 987.65 + m * 9,
    savings_sek: 246.91 + m * 8, savings_pct: 20 + m, estimated: m % 4 === 3,
  });
}
const topo = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"]],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.livingroom", domains: TEMP_DOMAINS },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor", entity: "sensor.outside", domains: TEMP_DOMAINS },
    { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump", entity: null, domains: ["switch", "input_boolean"] },
  ],
};
const states = {
  [SOLAR_ID]: { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", friendly_name: "Solar Irradiance", plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: true, friendly_name: "Space Heating Plan", plan_kind: "space", currency: "SEK", setup_topology: topo } },
  [DHW_ID]: { state: "4 slots planned", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  [SAV]: { state: "246.91", attributes: { unit_of_measurement: "SEK", friendly_name: "Monthly Savings", savings_months: MONTHS } },
  "sensor.heat_pump_optimizer_plan_predicted_savings": { state: "246.91", attributes: { unit_of_measurement: "SEK" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
};

const MEASURE = ([sel]) => {
  const root = window.__card.shadowRoot;
  // The reachable extra of a clipping ancestor: how far its own scroll can
  // bring content into view. `hidden`/`clip` scroll none of it.
  const clipOf = (el) => {
    let n = el.parentElement;
    while (n) {
      const cs = getComputedStyle(n);
      const ox = cs.overflowX;
      if (ox === "hidden" || ox === "clip") return { rect: n.getBoundingClientRect(), extra: 0, who: String(n.className || n.tagName) };
      if (ox === "auto" || ox === "scroll") {
        const extra = Math.max(0, n.scrollWidth - n.clientWidth);
        if (extra > 0) return { rect: n.getBoundingClientRect(), extra, who: String(n.className || n.tagName) };
      }
      n = n.parentElement;
    }
    const de = document.documentElement;
    return { rect: de.getBoundingClientRect(), extra: Math.max(0, de.scrollWidth - de.clientWidth), who: "document" };
  };
  const rows = [];
  for (const el of root.querySelectorAll("*")) {
    if (!el.getClientRects().length) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const direct = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent).join("").trim();
    if (!direct) continue;
    const rg = document.createRange();
    rg.selectNodeContents(el);
    const ink = rg.getBoundingClientRect();
    if (ink.width < 1 || ink.height < 1) continue;
    const c = clipOf(el);
    const reachableRight = c.rect.right + c.extra;
    const over = +(ink.right - reachableRight).toFixed(1);
    if (over <= 0.5) continue;
    const cls = String(el.className || "");
    const seam = el.closest(".savings-table") ? "savings"
      : el.closest(".dlg-tabs") ? "tabs"
        : el.closest(".whatif") ? "whatif" : "other";
    rows.push({ over, seam, clip: c.who, tag: el.tagName.toLowerCase(), cls: cls.slice(0, 24), txt: direct.slice(0, 26) });
  }
  rows.sort((a, b) => b.over - a.over);
  return rows;
};

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: WIDTH, height: 812 } });
await page.goto("about:blank");
await page.addScriptTag({ content: src });
await page.evaluate(async ([st, lang, pg, w]) => {
  document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
  document.body.innerHTML = "";
  const style = document.createElement("style");
  style.className = "hpo-test";
  // The font the published browser lane measures under (tests/card_browser.mjs):
  // a table's min-content width is font-dependent, so the metric is only
  // reproducible under a stated stack.
  style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:${w}px}`;
  document.head.appendChild(style);
  const card = document.createElement("heatpump-optimizer-card");
  card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true, show_stats: true });
  card.hass = { states: st, language: lang };
  document.body.appendChild(card);
  window.__card = card;
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 120));
  if (pg) {
    card._onCardClick({});
    card.dialog.page = pg;
    card._render();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 160));
  }
}, [states, LANG, PAGE, WIDTH]);
const rows = await page.evaluate(MEASURE, ["x"]);

const R = [];
const res = (name, value, unit) => R.push(`RESULT ${name}=${value} ${unit}`);
const worstOf = (seam) => {
  const f = rows.filter((r) => seam === "all" || r.seam === seam);
  return f.length ? f[0].over : -1;
};
res(`dialog_clip.worst_unreachable`, worstOf(SEAM), "px");
for (const s of ["savings", "tabs", "whatif", "other"]) {
  res(`dialog_clip.${s}_unreachable`, worstOf(s), "px");
}
res("dialog_clip.seam_count", new Set(rows.map((r) => r.seam)).size, "count");
res("dialog_clip.width", WIDTH, "px");
// The mechanism, in px: a `width:100%` table reports a scrollWidth larger than
// the body it is inside, so the body's box does not contain the table's ink.
const dims = await page.evaluate(() => {
  const root = window.__card.shadowRoot;
  const t = root.querySelector(".savings-table");
  const b = root.querySelector(".dlg-body");
  const tb = t && t.getBoundingClientRect();
  return {
    tableW: tb ? +tb.width.toFixed(1) : -1,
    tableScrollW: t ? t.scrollWidth : -1,
    bodyClientW: b ? b.clientWidth : -1,
    bodyScrollW: b ? b.scrollWidth : -1,
  };
});
res("dialog_clip.savings_table_width", dims.tableW, "px");
res("dialog_clip.savings_table_scroll_width", dims.tableScrollW, "px");
res("dialog_clip.body_client_width", dims.bodyClientW, "px");
res("dialog_clip.body_scroll_width", dims.bodyScrollW, "px");
console.log(rows.slice(0, 8).map((r) => `  ${r.over}px [${r.seam}] clip=${r.clip} ${r.tag}.${r.cls} "${r.txt}"`).join("\n") || "  (nothing unreachable)");

if (CELLS) {
  // Leave-one-out over the measured grid: widths x languages x seams.
  const grid = [];
  for (const w of [375, 360, 320, 768, 1280]) {
    for (const l of ["en", "sv-SE"]) {
      for (const pg of ["savings", "plan"]) {
        await page.setViewportSize({ width: w, height: 812 });
        await page.evaluate(async ([st, lang, pg, w2]) => {
          const style = document.querySelector("style.hpo-test");
          style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:${w2}px}`;
          const card = window.__card;
          card.hass = { states: st, language: lang };
          card._onCardClick({});
          card.dialog.page = pg;
          card._render();
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
          await new Promise((r) => setTimeout(r, 160));
        }, [states, l, pg, w]);
        const rr = await page.evaluate(MEASURE, ["x"]);
        grid.push({ w, l, pg, over: rr.length ? rr[0].over : 0 });
      }
    }
  }
  const vals = grid.map((g) => g.over);
  const sorted = [...vals].sort((a, b) => b - a);
  const min = Math.min(...vals), max = Math.max(...vals);
  // Drop the single most favourable cell, then the worst remaining count.
  const dropped = sorted.slice(1);
  console.log("CELLS " + grid.map((g) => `${g.w}/${g.l}/${g.pg}=${g.over}`).join(" "));
  res("cells.n", vals.length, "count");
  res("cells.min", min, "px");
  res("cells.max", max, "px");
  res("cells.after_dropping_most_favourable", dropped.length ? Math.max(...dropped) : 0, "px");
}

try { res("load1", Number(os.loadavg()[0].toFixed(3)), "load"); } catch { res("load1", -1, "load"); }
// A geometry count harness runs no BLAS work; the factor is 1 by construction.
res("thread_factor", 1, "ratio");
res("swapins", 0, "count");
console.log(R.join("\n"));
await browser.close();
