// ARCH2-s5 (round 10, D7): the card's repeated shapes, counted.
//
//     node dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs [CARD.js]
//
// tools/audit/archscore measures Python only (vector.py globs the package's
// *.py; the card is one 14.5k-line JS file), so a card change reads delta_S 0
// whatever it does. This is the card-side census the seat used instead. Each
// shape is one rule the card applies in more than one place; the count is the
// number of places that SPELL the rule inline (an owner's own definition is
// excluded by construction of each pattern), so a dedupe moves it to 0 or to
// the owner's single site. Plus the dead-code census: top-level functions and
// class methods whose name occurs once (the definition) outside comments,
// less the custom-element lifecycle hooks Home Assistant calls by name.
//
// Shapes (pattern, on the source with comments stripped):
//   live_guard        X.state === "unavailable" || X.state === "unknown"
//   state_sig         `${X.state}@${X.last_updated...`
//   null_number       X === null || X === undefined || X === ""
//   finite_inline     typeof X === "number" && Number.isFinite(X)
//   picker_open       pickerFocus = <anything but false>       (a picker visit opened)
//   char_width_inline <len> * CHAR_WIDTH_EM outside textWidth  (the label-width rule)
//   no_plan_state     L("errors.no_plan_data")                 (the no-plan empty state)
// RESULT lines: one per shape, total=<sum>, dead=<n>. Perturbation: any one of
// the shapes spelled once more anywhere moves its count and the total up by 1.
// Counts only.
import fs from "fs";

const file = process.argv[2] || "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
const src = fs.readFileSync(file, "utf8");
const code = src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:"'`\\])\/\/.*$/gm, "$1");

const SHAPES = {
  live_guard: /(\w+)\.state === "unavailable" \|\| \1\.state === "unknown"/g,
  state_sig: /\$\{(\w+)\.state\}@\$\{\1\.last_updated/g,
  null_number: /(\w+) === null \|\| \1 === undefined \|\| \1 === ""/g,
  finite_inline: /typeof (\w+(?:\.\w+)?) === "number" && Number\.isFinite\(\1\)/g,
  picker_open: /pickerFocus = (?!false)/g,
  char_width_inline: /(?:\.length|widest) \* CHAR_WIDTH_EM/g,
  no_plan_state: /L\("errors\.no_plan_data"\)/g,
};
let total = 0;
for (const [name, re] of Object.entries(SHAPES)) {
  const n = (code.match(re) || []).length;
  total += n;
  console.log(`RESULT ${name}=${n} count`);
}
console.log(`RESULT total=${total} count`);

const HOOKS = new Set(["getCardSize", "getStubConfig", "getConfigElement", "connectedCallback",
  "disconnectedCallback", "constructor", "render"]);
const defs = new Map();
for (const m of src.matchAll(/^(?:async )?function ([A-Za-z_$][\w$]*)|^const ([A-Za-z_$][\w$]*) =/gm)) {
  defs.set(m[1] || m[2], "top");
}
for (const m of src.matchAll(/^  (?:static |async |get |set )*([A-Za-z_$][\w$]*)\([^)]*\) \{$/gm)) {
  if (!defs.has(m[1])) defs.set(m[1], "method");
}
const dead = [];
for (const [n, kind] of defs) {
  if (HOOKS.has(n)) continue;
  const re = new RegExp(`(?<![\\w$])${n.replace(/\$/g, "\\$")}(?![\\w$])`, "g");
  if ((code.match(re) || []).length <= 1) dead.push(`${kind}:${n}`);
}
console.log(`  dead: ${dead.join(" ") || "-"}`);
console.log(`RESULT definitions=${defs.size} count`);
console.log(`RESULT dead=${dead.length} count`);
