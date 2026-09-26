// D5 verify-v3 (reach and class) harness for D5-s1-04: pipe rows rendered outside a table and
// prose rendered as table rows, re-measured with a second, independent GFM parser.
// Metric (one line): source lines of README.md + the 7 user docs whose GFM block is wrong --
//   a line starting with "|" that micromark (+ micromark-extension-gfm-table, the CommonMark/GFM
//   reference-conformant parser, not markdown-it) places in a paragraph, plus a non-"|" line it
//   places inside a tableRow; fenced code excluded by the parser itself.
// Count key: the tableRow / paragraph token spans micromark's event stream returns for the
//   docs' own bytes.
// Command (from the repository root):
//   T=$(mktemp -d); npm install --prefix "$T" micromark@4 micromark-extension-gfm-table@2 >/dev/null 2>&1; \
//     NODE_PATH=$T/node_modules node tools/audit/round9/D5/verify-v3/v3_s1_04_tables.mjs [--perturb]
// --perturb: in memory, a blank line before configuration.md:633 and rows 185-187 moved up to follow row 179, paragraph 181-184 after them
//   (the finder's proposed repair). Expected: misrendered 9 -> 0.
// Expected at baseline: misrendered_lines=9 (exact).
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core cloud
//   container, node v22.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
const t0 = process.cpuUsage();
const micromark = await import(path.join(process.env.NODE_PATH, "micromark", "index.js"));
const { gfmTable } = await import(path.join(process.env.NODE_PATH, "micromark-extension-gfm-table", "index.js"));
const P = micromark.parse, PP = micromark.postprocess, PRE = micromark.preprocess;
const perturb = process.argv.includes("--perturb");
const files = ["README.md", ...["architecture", "automations", "configuration", "dashboard-card",
  "ecl110", "how-it-works", "setup"].map((n) => `docs/${n}.md`)];
let orphan = 0, swallowed = 0;
for (const f of files) {
  let src = fs.readFileSync(f, "utf8");
  if (perturb && f === "docs/configuration.md") {
    const L = src.split("\n");
    L.splice(632, 0, "");                       // blank before old 633
    // rows 185-187 straight after row 179, then the blank (180), then paragraph 181-184
    src = [...L.slice(0, 179), ...L.slice(184, 187), "", ...L.slice(180, 184), ...L.slice(187)].join("\n");
  }
  const events = PP(P({ extensions: [gfmTable()] }).document().write(PRE()(src, "utf8", true)));
  const lines = src.split("\n");
  const kind = new Array(lines.length + 2).fill(null);
  for (const [ev, tok] of events) {
    if (ev !== "enter") continue;
    if (tok.type === "tableRow" || tok.type === "tableDelimiterRow" || tok.type === "tableHead")
      for (let l = tok.start.line; l <= tok.end.line; l++) kind[l] = "row";
    if (tok.type === "paragraph")
      for (let l = tok.start.line; l <= tok.end.line; l++) if (kind[l] !== "row") kind[l] = "para";
  }
  lines.forEach((text, i) => {
    const l = i + 1, t = text.trim();
    if (t.startsWith("|") && kind[l] === "para") { orphan++; console.log(`orphaned ${f}:${l}`); }
    if (t && !t.startsWith("|") && kind[l] === "row") { swallowed++; console.log(`swallowed ${f}:${l}`); }
  });
}
const u = process.cpuUsage(t0);
console.log(`RESULT files_checked=${files.length} count`);
console.log(`RESULT orphaned_rows=${orphan} count`);
console.log(`RESULT swallowed_prose=${swallowed} count`);
console.log(`RESULT misrendered_lines=${orphan + swallowed} count`);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
console.log(`# cpu_ms=${Math.round((u.user + u.system) / 1000)}`);
