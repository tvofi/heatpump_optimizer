// D4: the savings table's currency heads can contradict the value's own unit.
//
// METRIC (one line): number of money-bearing surfaces the card renders for the
// SAME savings figures whose named currency differs from the currency the plan
// sensor declares its values in (`unit_of_measurement` on
// sensor.heat_pump_optimizer_plan_predicted_savings, and the same token in the
// savings table's own column heads) -- counted from the RENDERED TEXT of the
// production renderers, never from the card config that produced it.
//
// RUN (from the export root; playwright resolves from NODE_PATH):
//   NODE_PATH=/tmp/pw-r5d4/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   ~/.nvm/versions/node/v20.10.0/bin/node \
//     tools/audit/round7/D4/currency_units.mjs [--config EUR] [--hass USD] [--sensor SEK]
//   (no HPO_PLANDATA set? the harness writes one under the temp root itself)
//
// EXPECTED (baseline f9d6f78, darwin arm64):
//   --config ''   --hass ''  --sensor SEK  -> RESULT currency.heads_contradicting_the_unit=0
//   --config EUR  --hass ''  --sensor SEK  -> RESULT currency.heads_contradicting_the_unit=3
//   --config ''   --hass USD --sensor SEK  -> RESULT currency.heads_contradicting_the_unit=3
//   --config EUR  --hass ''  --sensor EUR  -> RESULT currency.heads_contradicting_the_unit=0 (control)
//   (tolerance: exact; the token is read from text, not measured)
//
// BASELINE SHA: f9d6f78243fa65f6fa128d2357752a2ae7f60648
// MACHINE: 8-core Apple M1, 8 GB (darwin, arm64); Chromium 1148 (Playwright 1.49.0)
//
// PHENOMENON: one card prints one money quantity under two currencies. The
// headline savings item takes the unit the sensor declares
// (`heatpump-optimizer-card.js:headlineHtml` -> `attributes.unit_of_measurement`)
// and says so in its own comment ("nothing here converts, so a card-config
// `currency:` must not relabel it"), while the savings table names every column
// from `plan.currency()`, which puts `config.currency` ahead of the sensor's own
// token (heatpump-optimizer-card.js:_savingsPageHtml ->
// Plan.currency()). The table is the seam that relabels without converting.
import { readFileSync } from "node:fs";
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
  return i >= 0 && argv[i + 1] !== undefined ? argv[i + 1] : dflt;
};
const CFG_CUR = arg("config", "");
const HASS_CUR = arg("hass", "");
const SENSOR_CUR = arg("sensor", "SEK");

let planPath = process.env.HPO_PLANDATA;
if (!planPath) {
  planPath = path.join(os.tmpdir(), `d4-currency-${process.pid}.json`);
  const r = spawnSync(PYTHON, ["tests/plan_view.py"], {
    cwd: repo, env: { ...process.env, HPO_PLANDATA: planPath, PYTHONPATH: "tests/hastub" }, encoding: "utf8",
  });
  if (r.status !== 0) { console.error(r.stdout || "", r.stderr || ""); process.exit(2); }
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

const SPACE_ID = "sensor.heat_pump_optimizer_plan_space_heating";
const SAV = "sensor.heat_pump_optimizer_monthly_savings";
const PRED = "sensor.heat_pump_optimizer_plan_predicted_savings";
const PCT = "sensor.heat_pump_optimizer_plan_savings_percentage";
const MONTHS = [
  { month: "2026-07", baseline_sek: 1200.5, actual_sek: 900.25, savings_sek: 300.25, savings_pct: 25 },
  { month: "2026-08", baseline_sek: 980.0, actual_sek: 1040.5, savings_sek: -60.5, savings_pct: -6, estimated: true },
];
const states = {
  [SPACE_ID]: { state: "3 slots planned", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, friendly_name: "Space Heating Plan", plan_kind: "space" } },
  [SAV]: { state: "300.25", attributes: { unit_of_measurement: SENSOR_CUR, friendly_name: "Monthly Savings", savings_months: MONTHS } },
  [PRED]: { state: "300.25", attributes: { unit_of_measurement: SENSOR_CUR } },
  [PCT]: { state: "25", attributes: {} },
};

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
await page.goto("about:blank");
await page.addScriptTag({ path: CARD_SRC });
await page.evaluate(async ([st, cfgCur, hassCur]) => {
  document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
  document.body.innerHTML = "";
  const style = document.createElement("style");
  style.className = "hpo-test";
  style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:900px}`;
  document.head.appendChild(style);
  const card = document.createElement("heatpump-optimizer-card");
  const cfg = { type: "custom:heatpump-optimizer-card", show_stats: true };
  if (cfgCur) cfg.currency = cfgCur;
  card.setConfig(cfg);
  card.hass = { states: st, language: "en", config: hassCur ? { currency: hassCur } : {} };
  document.body.appendChild(card);
  window.__card = card;
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 120));
  card._onCardClick({});
  card.dialog.page = "savings";
  card._render();
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 140));
}, [states, CFG_CUR, HASS_CUR]);
const out = await page.evaluate(() => {
  const root = window.__card.shadowRoot;
  const headline = [...root.querySelectorAll(".hl-stat")]
    .map((e) => e.textContent.replace(/\s+/g, " ").trim())
    .filter((t) => /saving/i.test(t));
  const heads = [...root.querySelectorAll(".savings-table thead th")]
    .map((e) => e.textContent.trim());
  // The token a money surface names: the parenthesised currency on a head, or
  // the trailing token of the headline figure.
  const fromHead = (t) => (t.match(/\(([^)]+)\)/) || [])[1] || "";
  const fromHeadline = (t) => ((t.match(/\d[\d.,]*\s+([A-Za-z]{2,5})\b/) || [])[1] || "");
  return {
    headline: headline[0] || "",
    headlineUnit: fromHeadline(headline[0] || ""),
    heads,
    headUnits: heads.map(fromHead),
    moneyHeads: heads.filter((t) => /\(([^)]+)\)/.test(t)),
  };
});

const R = [];
const res = (name, value, unit) => R.push(`RESULT ${name}=${value} ${unit}`);
const contradicting = out.headUnits.filter((u) => u && u !== SENSOR_CUR).length;
res("currency.sensor_unit", SENSOR_CUR, "token");
res("currency.config_currency", CFG_CUR || "(unset)", "token");
res("currency.hass_currency", HASS_CUR || "(unset)", "token");
res("currency.headline_named_unit", out.headlineUnit, "token");
res("currency.heads_naming_a_unit", out.moneyHeads.length, "count");
res("currency.heads_contradicting_the_unit", contradicting, "count");
res("currency.money_surfaces", out.moneyHeads.length + (out.headlineUnit ? 1 : 0), "count");
console.log(`headline: ${JSON.stringify(out.headline)}`);
console.log(`heads   : ${JSON.stringify(out.heads)}`);
try { res("load1", Number(os.loadavg()[0].toFixed(3)), "load"); } catch { res("load1", -1, "load"); }
res("thread_factor", 1, "ratio");
res("swapins", 0, "count");
console.log(R.join("\n"));
await browser.close();
