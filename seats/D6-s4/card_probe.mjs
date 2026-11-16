#!/usr/bin/env node
// D6-s4: the card facts ledger.py checks card text against, read from the running card.
// Prints one line "JSON <object>": per language/key the `{name}` tokens production `L` leaves
// unsubstituted (vars = en's placeholders), the stale-pill constants, and the verdict of
// production `setConfig` on `hours` at 0.9, 1, 168 and 169 (true = accepted).
// Run: node dev/audit/rounds/round11/D6/s4/card_probe.mjs   (from the repository root)
// Expected at baseline 92d38ecb: unresolved {"sv/status.stale_title": ["{minuter}"]},
// hours {"0.9":false,"1":true,"168":true,"169":false}, stale {intervals:3,floor:90,default:30}.
import fs from "fs";
import os from "os";
import path from "path";
import vm from "vm";
import { makeCardContext, loadCard, CARD_PATH } from "../../../../../../tests/card_rig.mjs";

process.env.HPO_PLANDATA = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d6s4p-"));
const log = console.log; console.log = () => {};
const { ctx } = makeCardContext();
const Card = loadCard(ctx, fs.readFileSync(CARD_PATH, "utf8"));
const run = (code) => vm.runInContext(code, ctx);
const STRINGS = run("STRINGS");
const CALLSITE_EXTRA = { "stats.delta_detail_same": ["verdict"] };
const names = (s) => [...new Set((s.match(/\{(\w+)\}/g) || []).map((t) => t.slice(1, -1)))];
const unresolved = {};
for (const lang of Object.keys(STRINGS)) {
  run(`setLanguage(${JSON.stringify(lang)})`);
  for (const key of Object.keys(STRINGS[lang])) {
    const vars = Object.fromEntries([...names(STRINGS.en[key] || ""), ...(CALLSITE_EXTRA[key] || [])].map((v) => [v, "X"]));
    const left = ctx.L(key, vars).match(/\{\w+\}/g);
    if (left) unresolved[`${lang}/${key}`] = left;
  }
}
run('setLanguage("en")');
const hours = {};
for (const h of [0.9, 1, 168, 169]) {
  try { new Card().setConfig({ type: "custom:heatpump-optimizer-card", hours: h }); hours[h] = true; }
  catch { hours[h] = false; }
}
const stale = run("({intervals: PLAN_STALE_INTERVALS, floor: PLAN_STALE_FLOOR_MIN, default: DEFAULT_SOLVE_INTERVAL_MIN})");
console.log = log;
console.log("JSON " + JSON.stringify({ strings: STRINGS, unresolved, hours, stale }));
