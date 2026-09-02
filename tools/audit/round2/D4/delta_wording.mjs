// D4 (UI/UX) round 2 -- the what-if delta sentence for each of its three verdicts.
//
// METRIC: ungrammatical_en = how many of the three verdicts (cheaper, dearer,
//   the same) produce an English `stats.delta_detail` sentence containing
//   "the same than"; the Swedish template is checked the same way for
//   "oförändrad än" (its "jämfört med" phrasing fits all three).
// COMMAND (from the export root): node tools/audit/round2/D4/delta_wording.mjs
// EXPECTED (baseline c398fc84): ungrammatical_en = 1, ungrammatical_sv = 0.
// INSTRUMENTED SYMBOL: heatpump-optimizer-card.js:L / STRINGS
//   ("stats.delta_detail", "stats.the_same"), the same composition
//   WhatIfPanel's delta row performs, read through tests/card_rig.mjs's vm.
// PERTURBATION: change the English template to "{verdict} compared with the
//   saved plan" (or give stats.the_same its own template) -> 0.
import fs from "node:fs";
import os from "node:os";
import vm from "node:vm";
import { CARD_PATH, makeCardContext, loadCard } from "../../../../tests/card_rig.mjs";

const rig = makeCardContext();
loadCard(rig.ctx, fs.readFileSync(CARD_PATH, "utf8"));
const counts = {};
for (const lang of ["en", "sv"]) {
  vm.runInContext(`setLanguage(${JSON.stringify(lang)})`, rig.ctx);
  let bad = 0;
  for (const verdict of ["stats.cheaper", "stats.dearer", "stats.the_same"]) {
    const s = vm.runInContext(
      `L("stats.delta_detail", { verdict: L(${JSON.stringify(verdict)}), planned: "31.97", edited: "31.97", currency: "SEK" })`,
      rig.ctx);
    const wrong = lang === "en" ? /\bthe same than\b/.test(s) : /oförändrad än/.test(s);
    if (wrong) bad++;
    console.log(`${lang} ${verdict.padEnd(16)} ${wrong ? "WRONG " : "ok    "} ${s}`);
  }
  counts[lang] = bad;
}
console.log(`RESULT ungrammatical_en=${counts.en} count`);
console.log(`RESULT ungrammatical_sv=${counts.sv} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
