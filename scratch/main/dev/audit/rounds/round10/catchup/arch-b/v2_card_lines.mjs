// Catch-up verifier arch-b, V2 for ARCH2-s5 C1-C4: the card's repeated rules counted by LINE, with
// order-free patterns, independently of card_shapes.mjs's exact-spelling regexes.
//
//     node dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs CARD.js [CARD.js ...]
//
// Metric per file (comments stripped, then per line):
//   dead_entity_lines  lines naming both "unavailable" and "unknown" (any order, any operator)
//   isfinite_lines     lines calling Number.isFinite( with a `typeof` on the same line
//   nullish3_lines     lines with === null, === undefined and === "" all present
//   char_width_lines   lines using CHAR_WIDTH_EM
//   no_plan_lines      lines naming errors.no_plan_data
//   picker_lines       lines assigning pickerFocus to something other than false
// Null control: run it on the same file twice -- identical counts. Perturbation: paste one extra
// inline guard line and dead_entity_lines rises by 1. Expected at 9061fbd3d: see votes.json.
// Counts only; writes nothing.
import fs from "fs";
const pats = {
  dead_entity_lines: (l) => l.includes('"unavailable"') && l.includes('"unknown"'),
  isfinite_lines: (l) => l.includes("Number.isFinite(") && l.includes("typeof"),
  nullish3_lines: (l) => l.includes("=== null") && l.includes("=== undefined") && l.includes('=== ""'),
  char_width_lines: (l) => l.includes("CHAR_WIDTH_EM") && !/const CHAR_WIDTH_EM/.test(l),
  no_plan_lines: (l) => l.includes("errors.no_plan_data"),
  picker_lines: (l) => /pickerFocus\s*=\s*(?!false|=)/.test(l),
};
for (const f of process.argv.slice(2)) {
  const code = fs.readFileSync(f, "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:"'`\\])\/\/.*$/gm, "$1");
  const lines = code.split("\n");
  const out = Object.entries(pats).map(([k, p]) => [k, lines.filter(p).length]);
  const tot = out.reduce((a, [, n]) => a + n, 0);
  console.log(`RESULT ${f.split("/").pop()} ${out.map(([k, n]) => `${k}=${n}`).join(" ")} total=${tot}`);
}
