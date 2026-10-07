// D14-s2 / class P8 -- the card's money surfaces name one currency per screen?
//
// Metric (one line): distinct currency tokens the card renders across its
//   un-converted money surfaces (headline savings, savings table heads, what-if
//   delta, price axis unit) for ONE install; 1 = the screen agrees with itself.
// Count key: the token each RENDERED surface prints (read from the card's own
//   output / its own deltaHtml() and priceUnit()), never the config that fed it.
// Command:
//   HPO_PLANDATA=<tmp>/plan.json /opt/node22/bin/node tools/audit/round9/D14/s2/p8_card.mjs [--card <file>] [--arm <name>]
//   (tools/audit/round9/D14/s2/p8_currency.py runs plan_view.py into a private
//    HPO_PLANDATA and drives every arm; run that, not this, by hand.)
// Expected: arm card_cfg_EUR -> distinct=2 (SEK, EUR), exact; arm no_cfg (null
//   control) -> distinct=1; perturbation (drop `this.config.currency ||` from
//   PlanSource.currency()) -> distinct=1.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B8
//   (4 cores, 15 GB, Linux 6.18), node v22.22.2.
// Instrumented symbols: www/heatpump-optimizer-card.js PlanSource.currency(),
//   savingsUnit(), ManualPlan.deltaHtml(), PlanSource.priceUnit().
import fs from "fs";
import path from "path";
import { makeCardContext, loadCard, planStates, collect, DEFAULT_SPACE, DEFAULT_DHW, frozenDateClass } from "../../../../../tests/card_rig.mjs";

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const cardFile = opt("--card", "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const arm = opt("--arm", "card_cfg_EUR");
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !fs.existsSync(planPath)) { console.error("HPO_PLANDATA must name plan_view.py's payload"); process.exit(2); }
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
let src = fs.readFileSync(cardFile, "utf8");

// The perturbation, applied in memory to the source string only.
if (arm === "perturb_drop_cfg_lead") {
  const before = src;
  src = src.replace(/return \(\s*this\.config\.currency \|\|/, "return (");
  if (src === before) { console.error("perturbation did not apply"); process.exit(3); }
}

const { ctx } = makeCardContext();
const HOUR = 3600000;
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
ctx.Date = frozenDateClass(Date, FROZEN);
const Card = loadCard(ctx, src);

// One install as production publishes it: the coordinator's currency (SEK) on
// every money sensor and on the plan sensor's `currency` attribute.
const INSTALL = "SEK";
const st = planStates(plan);
st[DEFAULT_SPACE].attributes.currency = INSTALL;
st[DEFAULT_DHW].attributes.currency = INSTALL;
st[DEFAULT_SPACE].attributes.day_start_hour = 7;
st[DEFAULT_SPACE].attributes.day_end_hour = 22;
st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
const months = [{ month: "2026-01", baseline_sek: 1200.5, actual_sek: 900.25, savings_sek: 300.25, savings_pct: 25 }];
st["sensor.heat_pump_optimizer_monthly_savings"] = { state: "300.25", attributes: { unit_of_measurement: INSTALL, savings_months: months } };
st["sensor.heat_pump_optimizer_predicted_savings"] = { state: "300.25", attributes: { unit_of_measurement: INSTALL } };
st["sensor.heat_pump_optimizer_savings_percentage"] = { state: "25", attributes: {} };

const cfg = { show_stats: true, what_if: true };
if (arm !== "no_cfg") cfg.currency = "EUR";
const card = new Card();
card.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
const hass = { states: st, config: { currency: INSTALL }, callService: async () => ({ response: {} }) };
card.hass = hass;
if (card.connectedCallback) card.connectedCallback();
card.hass = hass;

const TOK = /\b([A-Z]{3}|kr)\b/;
const surfaces = {};
// Headline savings figure.
card._sig = null; card._render();
const headline = [...card.shadowRoot.querySelectorAll(".hl-stat")].map((e) => e.textContent.replace(/\s+/g, " ").trim()).find((t) => /saving/i.test(t)) || "";
surfaces.headline_savings = (headline.match(/\d[\d.,]*\s+([A-Za-z]{2,5})\b/) || [])[1] || "";
// Price axis unit, the string the chart draws.
surfaces.price_axis = ((card.plan && card.plan.priceUnit && card.plan.priceUnit()) || "").split("/")[0];
const drawn = collect(card.shadowRoot).join("\n");
surfaces.price_axis_drawn = (drawn.match(/([A-Z]{3})\/kWh/) || [])[1] || "";
// What-if delta.
try {
  card._onCardClick && card._onCardClick({});
  const html = card.manual.deltaHtml();
  surfaces.whatif_delta = (html.match(/-?\d+\.\d\d&nbsp;([A-Za-z]{2,5})/) || [])[1] || "";
} catch (e) { surfaces.whatif_delta = ""; surfaces.whatif_error = String(e); }
// Savings table heads.
try {
  card.dialog.open(); card.dialog.page = "savings"; card._sig = null; card._render();
  const heads = [...card.shadowRoot.querySelectorAll(".savings-table thead th")].map((th) => th.textContent.trim()).map((t) => (t.match(/\(([^)]+)\)/) || [])[1] || "").filter(Boolean);
  surfaces.savings_table = [...new Set(heads)].join(",");
} catch (e) { surfaces.savings_table = ""; }

const tokens = new Set(Object.entries(surfaces).filter(([k, v]) => !k.endsWith("_error") && v).flatMap(([, v]) => v.split(",")).filter((v) => TOK.test(v)));
console.log(`SURFACES ${JSON.stringify(surfaces)}`);
console.log(`RESULT card_distinct_currency_tokens[${arm}]=${tokens.size} count`);
console.log(`RESULT card_tokens[${arm}]=${[...tokens].sort().join("|")}`);
const off = Object.entries(surfaces).filter(([k, v]) => v && !k.endsWith("_error") && v.split(",").some((t) => t !== INSTALL)).map(([k]) => k);
console.log(`RESULT card_surfaces_not_install_currency[${arm}]=${off.length} count (${off.join(",")})`);
