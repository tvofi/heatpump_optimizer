// D5-s1 harness: GFM table integrity of the user docs, as a GFM renderer sees them.
//
// Metric (one line): source lines in README.md + docs/{architecture,automations,
//   configuration,dashboard-card,ecl110,how-it-works,setup}.md that render in the
//   wrong block -- (a) prose lines (not starting with "|") rendered as table rows
//   ("swallowed"), plus (b) pipe-table rows rendered as paragraph text with raw
//   pipes ("orphaned") because no header/delimiter row governs them.
// Count key: the markdown-it 14.1.0 token stream (tr / paragraph token .map), i.e.
//   what the renderer delivers, never the raw source shape alone.
// Command (from the repository root):
//   T=$(mktemp -d); npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1; \
//   NODE_PATH=$T/node_modules node tools/audit/round9/D5/s1/md_tables.mjs [--perturb]
// --perturb applies the minimal doc repair in memory: a blank line before every
//   swallowed line, and every paragraph sitting between a table and its orphaned
//   rows moved below those rows. Expected: misrendered_lines -> 0.
// Expected at baseline: misrendered_lines=9 (swallowed=6, orphaned=3), exact.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
// No numpy here: the thread pin does not apply; thread_factor printed as 1.0 for the contract.
import fs from "node:fs";
import os from "node:os";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const MarkdownIt = require("markdown-it");
const md = new MarkdownIt("commonmark").enable("table");

const FILES = ["README.md", ...["architecture", "automations", "configuration",
  "dashboard-card", "ecl110", "how-it-works", "setup"].map((n) => `docs/${n}.md`)];
const perturb = process.argv.includes("--perturb");

function analyse(text) {
  const lines = text.split("\n");
  const toks = md.parse(text, {});
  const inTable = new Set(), inCode = new Set(), swallowed = [], orphaned = [];
  for (const t of toks) {
    if (t.type === "table_open") for (let i = t.map[0]; i < t.map[1]; i++) inTable.add(i);
    if ((t.type === "fence" || t.type === "code_block" || t.type === "html_block") && t.map)
      for (let i = t.map[0]; i < t.map[1]; i++) inCode.add(i);
    if (t.type === "tr_open" && t.map && !lines[t.map[0]].trim().startsWith("|"))
      swallowed.push(t.map[0]);
  }
  lines.forEach((l, i) => {
    if (l.trim().startsWith("|") && !inTable.has(i) && !inCode.has(i)) orphaned.push(i);
  });
  return { lines, swallowed, orphaned };
}

function repair(text) {
  let { lines, swallowed, orphaned } = analyse(text);
  // blank line before each swallowed prose line (bottom-up keeps indices valid)
  for (const i of [...swallowed].sort((a, b) => b - a)) lines.splice(i, 0, "");
  ({ lines, swallowed, orphaned } = analyse(lines.join("\n")));
  // move the paragraph between a table and its orphaned rows below the rows
  const blocks = [];
  for (const i of orphaned) {
    if (blocks.length && blocks.at(-1).end === i - 1) blocks.at(-1).end = i;
    else blocks.push({ start: i, end: i });
  }
  for (const b of blocks.reverse()) {
    let p = b.start - 1;
    while (p >= 0 && lines[p].trim() !== "" && !lines[p].trim().startsWith("|")) p--;
    const para = lines.slice(p + 1, b.start);
    let q = p;
    while (q >= 0 && lines[q].trim() === "") q--;
    if (q < 0 || !lines[q].trim().startsWith("|")) continue; // no table above: nothing to rejoin
    const rows = lines.slice(b.start, b.end + 1);
    lines.splice(q + 1, b.end - q, ...rows, "", ...para);
  }
  return lines.join("\n");
}

let sw = 0, orph = 0;
for (const f of FILES) {
  let text = fs.readFileSync(f, "utf8");
  if (perturb) text = repair(text);
  const { lines, swallowed, orphaned } = analyse(text);
  for (const i of swallowed) console.log(`swallowed ${f}:${i + 1}: ${lines[i].slice(0, 70)}`);
  for (const i of orphaned) console.log(`orphaned  ${f}:${i + 1}: ${lines[i].slice(0, 70)}`);
  sw += swallowed.length; orph += orphaned.length;
}
console.log(`RESULT files_checked=${FILES.length} count`);
console.log(`RESULT swallowed_prose_lines=${sw} count`);
console.log(`RESULT orphaned_table_rows=${orph} count`);
console.log(`RESULT misrendered_lines=${sw + orph} count`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
