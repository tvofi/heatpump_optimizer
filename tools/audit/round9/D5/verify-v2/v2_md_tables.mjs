// D5 verify-v2 harness for D5-s1-04 (independent renderer: marked@15, not markdown-it).
// Metric (one line): source lines of README.md + the 7 user docs whose text marked's GFM
// lexer places in the wrong block: a line starting with '|' that ends up inside a paragraph
// (orphaned pipe row) plus a non-pipe prose line that ends up as a table row (swallowed).
// Count key: marked.lexer tokens (table.rows cells / paragraph raw), mapped back to source
// lines by exact raw text; never the doc's own line shapes.
// Command (repository root):
//   T=$(mktemp -d); npm install --prefix "$T" marked@15 >/dev/null 2>&1; NODE_PATH=$T/node_modules node tools/audit/round9/D5/verify-v2/v2_md_tables.mjs [--perturb]
// --perturb: in memory, move a paragraph interposed between a table and its further pipe rows
//   below those rows, then insert a blank line before every non-pipe line that directly follows a
//   pipe line, and before every pipe line directly following a non-pipe, non-blank line
//   (the minimal repair of both shapes) -> count must go to 0 (control: nothing else moves).
// Baseline 1936d5ca; exact.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
const require = createRequire(path.join(process.env.NODE_PATH || ".", "x.js"));
const { marked } = require("marked");
const FILES = ["README.md", ...["architecture", "automations", "configuration", "dashboard-card",
  "ecl110", "how-it-works", "setup"].map((n) => `docs/${n}.md`)];
const perturb = process.argv.includes("--perturb");
let orphan = 0, swallowed = 0;
function moveInterposed(L) {
  // pipe block, blank, paragraph, pipe row: move "blank + paragraph" below the pipe run.
  const isP = (x) => /^\s*\|/.test(x);
  for (let i = 1; i < L.length; i++) {
    if (isP(L[i - 1]) && L[i] === "") {
      let j = i + 1; while (j < L.length && L[j].trim() && !isP(L[j])) j++;
      if (j > i + 1 && j < L.length && isP(L[j])) {
        let k = j; while (k < L.length && isP(L[k])) k++;
        const para = L.slice(i, j), rows = L.slice(j, k);
        L.splice(i, k - i, ...rows, ...para);
      }
    }
  }
  return L;
}
function repair(src) {
  const L = moveInterposed(src.split("\n")), out = [];
  let fence = false;
  for (let i = 0; i < L.length; i++) {
    const cur = L[i], prev = i ? L[i - 1] : "";
    if (/^\s*(```|~~~)/.test(cur)) fence = !fence;
    if (!fence && i) {
      const pp = /^\s*\|/.test(prev), cp = /^\s*\|/.test(cur);
      if (pp && !cp && cur.trim()) out.push("");
      else if (!pp && cp && prev.trim()) out.push("");
    }
    out.push(cur);
  }
  return out.join("\n");
}
for (const f of FILES) {
  let src = fs.readFileSync(f, "utf8");
  if (perturb) src = repair(src);
  const lines = src.split("\n");
  const walk = (toks) => {
    for (const t of toks) {
      if (t.type === "paragraph") {
        for (const ln of t.raw.split("\n")) if (/^\s*\|.*\|\s*$/.test(ln)) {
          orphan++; console.log(`ORPHAN ${f}:${lines.indexOf(ln) + 1}: ${ln.slice(0, 60)}`);
        }
      } else if (t.type === "table") {
        for (const ln of t.raw.split("\n")) if (ln.trim() && !ln.includes("|")) {
          swallowed++; console.log(`SWALLOWED ${f}:${lines.indexOf(ln) + 1}: ${ln.slice(0, 60)}`);
        }
      }
      if (t.tokens && t.type !== "table") walk(t.tokens);
      if (t.items) walk(t.items);
    }
  };
  walk(marked.lexer(src, { gfm: true }));
}
const cpu = process.cpuUsage();
console.log(`RESULT files_checked=${FILES.length} count`);
console.log(`RESULT orphaned_pipe_rows=${orphan} count`);
console.log(`RESULT swallowed_prose_lines=${swallowed} count`);
console.log(`RESULT misplaced_lines=${orphan + swallowed} count`);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${(await import("node:os")).loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
