#!/usr/bin/env node
// D6-s4: card strings that render a literal, unsubstituted `{placeholder}`.
//
// Metric: per language dictionary of the card's STRINGS, the number of keys whose
// production `L(key, vars)` output still holds a `{name}` token when `vars` carries
// every placeholder the English source of that key names (the call sites' contract,
// en being the source text). Count key: the string L returns, never the dictionary
// text. Second RESULT: the production `statusPill(plan, now)` driven with a plan
// 200 min old under `setLanguage("sv")`; `stale_title_literal_tokens` counts `{name}`
// tokens in the pill's title (the tooltip the user reads).
//
// Run:    node dev/audit/rounds/round11/D6/s4/card_placeholders.mjs
//         node dev/audit/rounds/round11/D6/s4/card_placeholders.mjs --perturb
//           (in memory: STRINGS.sv["status.stale_title"] uses `{minutes}`, as en does;
//            unresolved_sv and stale_title_literal_tokens go to 0)
// Expected at baseline 92d38ecb: unresolved_en=0 (null control), unresolved_sv=1,
// unresolved_de=0, stale_title_literal_tokens=1 (exact; counts).
// Machine: B13 finder box (linux x86_64); counts are load-immune.
import fs from "fs";
import os from "os";
import path from "path";
import vm from "vm";
import { makeCardContext, loadCard, CARD_PATH } from "../../../../../../tests/card_rig.mjs";

process.env.HPO_PLANDATA = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d6s4-"));
const perturb = process.argv.includes("--perturb");
const t0 = process.cpuUsage();
const { ctx } = makeCardContext();
loadCard(ctx, fs.readFileSync(CARD_PATH, "utf8"));
const run = (code) => vm.runInContext(code, ctx);
const STRINGS = run("STRINGS");
if (perturb) STRINGS.sv["status.stale_title"] = STRINGS.sv["status.stale_title"].replace("{minuter}", "{minutes}");
// A call site that passes more than en's source names: deltaHtml() calls
// L(detailKey, { verdict, planned, edited, currency }) for both delta keys, so
// `{verdict}` in a translation of stats.delta_detail_same is substituted.
const CALLSITE_EXTRA = { "stats.delta_detail_same": ["verdict"] };
const names = (s) => [...new Set((s.match(/\{(\w+)\}/g) || []).map((t) => t.slice(1, -1)))];
const offenders = [];
for (const lang of Object.keys(STRINGS)) {
  run(`setLanguage(${JSON.stringify(lang)})`);
  let n = 0;
  for (const key of Object.keys(STRINGS[lang])) {
    const vars = Object.fromEntries([...names(STRINGS.en[key] || ""), ...(CALLSITE_EXTRA[key] || [])].map((v) => [v, "X"]));
    const out = ctx.L(key, vars);
    const left = out.match(/\{\w+\}/g);
    if (left) { n++; offenders.push(`${lang}\t${key}\t${left.join(",")}`); }
  }
  console.log(`RESULT unresolved_${lang}=${n} count`);
}
for (const o of offenders) console.log(`   offender ${o}`);
// The production call site: a stale plan under Swedish.
run('setLanguage("sv-SE")');
const now = Date.parse("2026-01-14T12:00:00Z");
const plan = {
  manualOverride: () => null,
  resolveEntity: (k) => `sensor.plan_${k}`,
  stateOf: () => ({ state: "heating", attributes: {} }),
  statEntity: (suffix) => suffix === "_last_optimization"
    ? { state: new Date(now - 200 * 60000).toISOString() } : null,
};
const pill = ctx.statusPill(plan, now);
const tokens = (pill && pill.title.match(/\{\w+\}/g)) || [];
console.log(`   pill key=${pill && pill.key} title=${pill && pill.title}`);
console.log(`RESULT stale_title_literal_tokens=${tokens.length} count`);
const u = process.cpuUsage(t0);
console.log("RESULT thread_factor=1.000");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
let sw = "na";
try { sw = fs.readFileSync("/proc/vmstat", "utf8").match(/pswpin (\d+)/)[1]; } catch {}
console.log(`RESULT swapins=${sw}`);
console.log(`RESULT cpu_ms=${((u.user + u.system) / 1000).toFixed(0)} ms`);
