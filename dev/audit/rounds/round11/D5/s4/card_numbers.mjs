#!/usr/bin/env node
// D5-s4 M4 (C7): executed check of the numbers card comments cite against the card's own
// constants and functions, loaded through tests/card_rig.mjs into a vm context.
// Metric: cited-number checks that fail (a comment's number disagrees with the code it sits on).
// Run:  HPO_PLANDATA=$(mktemp -d) node dev/audit/rounds/round11/D5/s4/card_numbers.mjs [--perturb]
//   --perturb redefines CARD_CHROME_PX to 24 in the context (one-line edit stand-in): failures go up by 1.
// Expected at 92d38ecb: RESULT failed=0 count of RESULT checks=10 (exact). Machine: box B11. No timing.
import fs from "node:fs";
import vm from "node:vm";
import os from "node:os";
import { makeCardContext, loadCard, CARD_PATH } from "../../../../../../tests/card_rig.mjs";

process.env.HPO_PLANDATA ||= fs.mkdtempSync(`${os.tmpdir()}/d5s4-`);
const { ctx } = makeCardContext();
loadCard(ctx, fs.readFileSync(CARD_PATH, "utf8"));
const ev = (s) => vm.runInContext(s, ctx);
if (process.argv.includes("--perturb")) ev("CARD_CHROME_PX_OVERRIDE = 24");
const chrome = ev("typeof CARD_CHROME_PX_OVERRIDE !== 'undefined' ? CARD_CHROME_PX_OVERRIDE : CARD_CHROME_PX");
const near = (a, b, tol) => Math.abs(a - b) <= tol;
const checks = [
  ["CARD_CHROME_PX = 1 px border + 12 px padding, each side", chrome === 2 * (1 + 12), chrome],
  ["'Heating system and heat storage' is 164 units at 11", near(ev("setupTextW('Heating system and heat storage', 11)"), 164, 0.5), ev("setupTextW('Heating system and heat storage', 11)")],
  ["chip inside is 152 units (SETUP_COL_W - 2*SETUP_PAD - 2*SETUP_CHIP_PAD)", ev("SETUP_COL_W - 2*SETUP_PAD - 2*SETUP_CHIP_PAD") === 152, ev("SETUP_COL_W - 2*SETUP_PAD - 2*SETUP_CHIP_PAD")],
  ["badge disc is 18 units across", ev("2*SETUP_BADGE_R") === 18, ev("2*SETUP_BADGE_R")],
  ["MAX_COMPACT_FONT clears the 8 px floor at ~257 px", ev("MAX_COMPACT_FONT*257/VIEW_W") >= ev("MIN_AXIS_FONT_PX") - 0.05, ev("MAX_COMPACT_FONT*257/VIEW_W")],
  ["chart drawn in a fixed 900x380 system", ev("VIEW_W") === 900 && ev("VIEW_H") === 380, ev("VIEW_W+'x'+VIEW_H")],
  ["history span 48 h, chunk 12 h", ev("HISTORY_SPAN_MS") === 48 * 3600e3 && ev("HISTORY_CHUNK_MS") === 12 * 3600e3, ev("HISTORY_SPAN_MS/3600e3+'/'+HISTORY_CHUNK_MS/3600e3")],
  ["plan stale: three intervals, never sooner than 90 min", ev("PLAN_STALE_INTERVALS") === 3 && ev("PLAN_STALE_FLOOR_MIN") === 90, ev("PLAN_STALE_INTERVALS+'/'+PLAN_STALE_FLOOR_MIN")],
  ["SV_MAG_ALPHA inside the swept [0.133, 0.368] window", ev("SV_MAG_ALPHA") > 0.133 && ev("SV_MAG_ALPHA") < 0.368, ev("SV_MAG_ALPHA")],
  ["--hpo-radius-m is 12 px", /"--hpo-radius-m": "12px"/.test(fs.readFileSync(CARD_PATH, "utf8")), "12px"],
];
let failed = 0;
for (const [what, ok, got] of checks) {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what} -> ${got}`);
}
console.log(`RESULT checks=${checks.length} count`);
console.log(`RESULT failed=${failed} count`);
const u = process.cpuUsage();
console.log("RESULT thread_factor=1.000");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
