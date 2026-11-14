// R10-USER-TEXT-VERIFY-CARD: enumerates every user-visible string of the
// dashboard card, the enumerator the round-10 card user-text record
// (dev/audit/rounds/round10/user-text-card.md) is built on.
//
//    node dev/audit/harnesses/r10_card_user_text.mjs [card.js] [--tsv]
//
// Run from a worktree root; the card path defaults to that tree's card, so the
// same file measures a base, a head or a scratch copy (the null control plants
// a key and an unkeyed literal in a copy and passes its path).
//
// Two sources, because the card has two ways of putting text on screen:
//   table     every key of `STRINGS.en` (the card's language table; `L(key)`
//             is the only reader), with its `sv` and `de` texts, and whether
//             a reader reaches it: the key quoted outside the table, or a
//             `L(\`prefix_${...}\`)` template whose literal prefix it starts
//             with, or the same prefix as a concatenation's head (`reached`),
//             else `unreached`;
//   literal   text outside the table that reaches the DOM unkeyed: a template
//             or string literal's `>text<` run, a `title=`, `aria-label=`,
//             `placeholder=` or `alt=` attribute value, and a `textContent` /
//             `innerText` assignment of a quoted literal; text with no letter,
//             a `${...}` hole alone, an entity (`&nbsp;`), and comment lines
//             are skipped.
// Output: one summary line per source (`table N`, `literal N`), then with
// `--tsv` one row per string: source, key or line, en, sv, de, reach.
// Counts and texts only; no timing, no network.

import fs from "fs";
import path from "path";

const args = process.argv.slice(2);
const tsv = args.includes("--tsv");
const cardArg = args.find((a) => !a.startsWith("--"));
const cardPath = cardArg || path.join(process.cwd(), "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const src = fs.readFileSync(cardPath, "utf8");
const lines = src.split("\n");

// The table: from `const STRINGS = {` to the first line that is exactly `};`.
const start = lines.findIndex((l) => /^const STRINGS = \{/.test(l));
if (start < 0) throw new Error("no `const STRINGS = {` in " + cardPath);
let end = start;
while (end < lines.length && lines[end] !== "};") end++;
if (end >= lines.length) throw new Error("STRINGS block has no closing `};`");
const STRINGS = new Function(lines.slice(start, end + 1).join("\n").replace(/^const STRINGS = /, "return "))();
if (!STRINGS.en || Object.keys(STRINGS.en).length === 0) throw new Error("STRINGS.en is empty");

const outside = lines.filter((_, i) => i < start || i > end).join("\n");
// A key built at run time: a template literal or a concatenation whose literal
// head is a key prefix (`\`health.p_${...}\``, `"health.input_" + id`).
const dynPrefixes = [
  ...[...outside.matchAll(/`([a-z]+\.[a-z0-9_]*)\$\{/g)].map((m) => m[1]),
  ...[...outside.matchAll(/["']([a-z]+\.[a-z0-9_]*)["']\s*\+/g)].map((m) => m[1]),
];
const reach = (key) =>
  outside.includes(`"${key}"`) || outside.includes(`'${key}'`) || outside.includes(`\`${key}\``) ||
  dynPrefixes.some((p) => p && key.startsWith(p))
    ? "reached"
    : "unreached";

const rows = [];
for (const key of Object.keys(STRINGS.en)) {
  rows.push(["table", key, STRINGS.en[key], (STRINGS.sv || {})[key] ?? "", (STRINGS.de || {})[key] ?? "", reach(key)]);
}

// Unkeyed literals outside the table.
const hasLetter = (s) => /[A-Za-zÅÄÖåäöÜüß]/.test(s);
const visible = (s) => {
  const t = s.replace(/\$\{[^}]*\}/g, "").replace(/&[a-z#0-9]+;/gi, "").trim();
  return t.length > 0 && hasLetter(t);
};
const literalRows = [];
lines.forEach((line, i) => {
  if (i >= start && i <= end) return;
  const t = line.trim();
  if (t.startsWith("//") || t.startsWith("*") || t.startsWith("/*")) return;
  const seen = new Set();
  const add = (text, how) => {
    const k = how + "\u0000" + text;
    if (seen.has(k) || !visible(text)) return;
    seen.add(k);
    literalRows.push(["literal", `L${i + 1}:${how}`, text.trim(), "", "", "unkeyed"]);
  };
  if (/[`"']/.test(line)) {
    for (const m of line.matchAll(/>([^<>`"']*)</g)) {
      // A `>` that is a comparison or an arrow, not a tag end, is skipped:
      // the run must sit between a tag end and a tag start.
      const before = line.slice(0, m.index + 1);
      if (/(=>|>=|\s>\s?)$/.test(before.slice(-3)) && !/["a-z0-9/]>$/i.test(before.slice(-2))) continue;
      add(m[1], "text");
    }
  }
  for (const m of line.matchAll(/\b(title|aria-label|placeholder|alt)="([^"$]*)"/g)) add(m[2], m[1]);
  for (const m of line.matchAll(/\.(textContent|innerText)\s*=\s*(["'])((?:(?!\2).)*)\2/g)) add(m[3], m[1]);
});
rows.push(...literalRows);

const tableN = rows.filter((r) => r[0] === "table").length;
const unreached = rows.filter((r) => r[5] === "unreached").length;
console.log(`table ${tableN} (unreached ${unreached})`);
console.log(`literal ${literalRows.length}`);
if (tsv) {
  const cell = (s) => String(s).replace(/[\t\n]/g, " ");
  for (const r of rows) console.log(r.map(cell).join("\t"));
}
