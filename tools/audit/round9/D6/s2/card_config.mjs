// D6-s2 harness: docs/dashboard-card.md "## Configuration options" claims against the card's setConfig.
//
// Metric: count of documented configuration claims (defaults of hours/what_if/show_stats/
// the three entity ids/series, the eight series keys, the 1..168 hours bound, refusal of
// non-string title / non-boolean toggles / unknown series keys, acceptance of an empty
// title) that disagree with what the real card element's setConfig accepts or fills in.
// Symbol: heatpump-optimizer-card.js parseConfig, via the registered element's setConfig
// and its read-only `config` getter. Key: what setConfig returns/throws.
//
// Command (from the export root):
//   HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D6/s2/card_config.mjs
// Perturbation: --perturb rewrites the card source in memory, `hours > 168` -> `hours > 200`
//   and `hours < 1` -> `hours < 0.5`; card_claims_false must go up by >= 2.
// Expected: see REPORT.md (exact).
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
// Root rule: paths relative to process.cwd().
import fs from "node:fs";
import path from "node:path";
import { makeCardContext, loadCard } from "../../../../../tests/card_rig.mjs";

const ROOT = process.cwd();
const t0 = process.cpuUsage();
const CARD = path.join(ROOT, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
let src = fs.readFileSync(CARD, "utf8");
if (process.argv.includes("--perturb")) {
  src = src.replace("hours < 1 || hours > 168", "hours < 0.5 || hours > 200");
}
const doc = fs.readFileSync(path.join(ROOT, "docs/dashboard-card.md"), "utf8").split("\n");
const lineOf = (re) => doc.findIndex((l) => re.test(l)) + 1;

const { ctx } = makeCardContext();
const Card = loadCard(ctx, src);
const results = [];
const claim = (re, what, ok, detail = "") =>
  results.push([`docs/dashboard-card.md:${lineOf(re)}`, what, !!ok, detail]);

const accept = (cfg) => {
  const c = new Card();
  try { c.setConfig(cfg); return { ok: true, cfg: c.config }; } catch (e) { return { ok: false, err: String(e.message || e) }; }
};

const base = { type: "custom:heatpump-optimizer-card" };
const d = accept(base);
claim(/^\| `hours`/, "hours defaults to 24", d.ok && d.cfg.hours === 24, JSON.stringify(d.cfg && d.cfg.hours));
claim(/^\| `what_if`/, "what_if defaults to true", d.ok && d.cfg.what_if === true, String(d.cfg && d.cfg.what_if));
claim(/^\| `show_stats`/, "show_stats defaults to true", d.ok && d.cfg.show_stats === true, String(d.cfg && d.cfg.show_stats));
claim(/^space_entity:/, "space_entity default is the plan_space_heating id",
  d.ok && d.cfg.space_entity === "sensor.heat_pump_optimizer_plan_space_heating", d.cfg && d.cfg.space_entity);
claim(/^dhw_entity:/, "dhw_entity default is the plan_dhw_heating id",
  d.ok && d.cfg.dhw_entity === "sensor.heat_pump_optimizer_plan_dhw_heating", d.cfg && d.cfg.dhw_entity);
claim(/^solar_entity:/, "solar_entity default is the solar_irradiance id",
  d.ok && d.cfg.solar_entity === "sensor.heat_pump_optimizer_solar_irradiance", d.cfg && d.cfg.solar_entity);
// series keys: the documented eight are accepted, an unknown one refused
const keysLine = doc.find((l) => l.startsWith("| `series`"));
const docKeys = [...keysLine.matchAll(/`(\w+)`/g)].map((m) => m[1]).filter((k) => k !== "series" && k !== "true");
const allOn = Object.fromEntries(docKeys.map((k) => [k, true]));
const s = accept({ ...base, series: allOn });
claim(/^\| `series`/, `the ${docKeys.length} documented series keys are accepted`, s.ok && docKeys.length === 8, s.err || docKeys.join(","));
// the card's own series roster: probe candidate names the chart could carry
const probe = ["price", "dhw_slots", "space_slots", "actioned", "outdoor", "dhw_temp", "house_temp", "solar",
  "upper", "lower", "room", "dhw_power", "space_power", "peak", "pv", "cost"];
const acceptedKeys = probe.filter((k) => accept({ ...base, series: { [k]: true } }).ok);
claim(/^\| `series`/, "no series key beyond the documented eight is accepted",
  acceptedKeys.length === docKeys.length && acceptedKeys.every((k) => docKeys.includes(k)), acceptedKeys.join(","));
claim(/an unknown\s*$|unknown series key/, "an unknown series key is refused", !accept({ ...base, series: { nope: true } }).ok);
// hours bound
for (const [h, want] of [[1, true], [168, true], [0.5, false], [0, false], [169, false], [200, false]]) {
  const r = accept({ ...base, hours: h });
  claim(/^\| `hours`/, `hours ${h} ${want ? "accepted" : "refused"}`, r.ok === want, r.err || "ok");
}
// types
claim(/^Invalid configuration/, "non-string title refused", !accept({ ...base, title: 5 }).ok);
claim(/^\| `title`/, "empty title accepted", accept({ ...base, title: "" }).ok);
claim(/^Invalid configuration/, "non-boolean what_if refused", !accept({ ...base, what_if: "yes" }).ok);
claim(/^Invalid configuration/, "non-boolean show_stats refused", !accept({ ...base, show_stats: 1 }).ok);
claim(/^Invalid configuration/, "non-boolean series visibility refused", !accept({ ...base, series: { price: "on" } }).ok);
claim(/^Invalid configuration/, "non-string entity id refused", !accept({ ...base, space_entity: 3 }).ok);

for (const [src_, what, ok, det] of results) {
  console.log(`${ok ? "true " : "FALSE"} ${src_.padEnd(28)} ${what} -- ${det}`);
}
console.log(`RESULT card_claims=${results.length} count`);
console.log(`RESULT card_claims_false=${results.filter((r) => !r[2]).length} count`);
const u = process.cpuUsage(t0);
console.log("RESULT thread_factor=1.000");
console.log(`RESULT load1=${(await import("node:os")).loadavg()[0].toFixed(2)}`);
let sw = "na";
try { sw = fs.readFileSync("/proc/vmstat", "utf8").split("\n").find((l) => l.startsWith("pswpin")).split(" ")[1]; } catch {}
console.log(`RESULT swapins=${sw}`);
void u;
