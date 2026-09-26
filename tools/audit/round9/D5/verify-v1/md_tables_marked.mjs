// V1 independent check for D5-s1-04 with a second GFM renderer (marked, gfm:true).
// Metric: in docs/configuration.md, the 9 flagged source lines -- count those whose text lands in
// the wrong block: anti-legionella rows (185-187) inside a <p> with raw pipes, and prose 633-638
// inside <td>. Also counts, across README.md + the finder's 7 user docs (same scope as md_tables.mjs), <p> blocks containing a raw "| --- |"-free
// line starting with "|" (orphan pipe rows) and <td> cells whose text begins with a prose sentence
// fragment from a line lacking any pipe.
// Command: T=$(mktemp -d); npm install --prefix "$T" marked@14; NODE_PATH=$T/node_modules node tools/audit/round9/D5/verify-v1/md_tables_marked.mjs
import { createRequire } from "module";
import fs from "fs";
const require = createRequire(import.meta.url + "/../");
const { marked } = require(process.env.NODE_PATH + "/marked");
const files = ["README.md", ...["architecture", "automations", "configuration", "dashboard-card", "ecl110", "how-it-works", "setup"].map(n => `docs/${n}.md`)];
let orphan = 0, swallowed = 0;
for (const f of files) {
  const src = fs.readFileSync(f, "utf8");
  const toks = marked.lexer(src, { gfm: true });
  const walk = (ts) => { for (const t of ts) {
    if (t.type === "paragraph") for (const line of t.raw.split("\n")) if (/^\|.*\|\s*$/.test(line)) { orphan++; console.log("orphaned", f, line.slice(0, 60)); }
    if (t.type === "table") for (const row of t.rows) { const cells = row.map(c => c.text); if (cells.slice(1).every(c => c === "") && cells[0] && !t.raw.split("\n").find(l => l.includes(cells[0]))?.trim().startsWith("|")) { swallowed++; console.log("swallowed", f, cells[0].slice(0, 60)); } }
    if (t.tokens) walk(t.tokens.filter(x => x.type !== "text"));
  } };
  walk(toks);
}
console.log(`RESULT files_checked=${files.length} count`);
console.log(`RESULT orphaned_table_rows=${orphan} count`);
console.log(`RESULT swallowed_prose_lines=${swallowed} count`);
console.log(`RESULT misrendered_lines=${orphan + swallowed} count`);
