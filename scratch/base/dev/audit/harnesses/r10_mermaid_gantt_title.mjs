// R10-PLAN-ARTIFACT: does mermaid 11.4.1's gantt grammar read plan_table.py's
// gantt as written -- in particular the `;` in its title line?
//
//   npm install --prefix <DIR> mermaid@11.4.1 jsdom@24.1.3
//   node dev/audit/harnesses/r10_mermaid_gantt_title.mjs <DIR>
//
// The gantt is plan_table.gantt() over plan_table's own fixture roster, taken
// from the tree. The lexer rule at issue is `title\s[^\n]+` (a title runs to
// the line's end), where `dateFormat\s[^#\n;]+` stops at `;`. Metric, one line
// per arm: `RESULT arm=<name> parsed=<bool> title=<json>`.
//   tree     plan_table's gantt; expected parsed=true, the title whole.
//   null     the same gantt with `; x` appended to its dateFormat line, a
//            directive whose rule excludes `;`; expected parsed=false, so the
//            parser is shown able to refuse a `;` where the grammar has none.
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const dir = process.argv[2];
if (!dir) {
  console.error("usage: r10_mermaid_gantt_title.mjs <dir holding node_modules/mermaid>");
  process.exit(2);
}
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const { JSDOM } = await import(path.join(dir, "node_modules/jsdom/lib/api.js"));
const dom = new JSDOM("<!doctype html><html><body></body></html>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
const chunks = path.join(dir, "node_modules/mermaid/dist/chunks/mermaid.core");
const { readdirSync } = await import("node:fs");
const file = readdirSync(chunks).find((f) => /^ganttDiagram-.*\.mjs$/.test(f));
const { diagram } = await import(path.join(chunks, file));

const block = execFileSync("python3", ["-I", "-c",
  "import sys; sys.path.insert(0, 'tools/audit/seat'); import plan_table; " +
  "print(plan_table.gantt(plan_table._fixture_roster()))"], { cwd: root, encoding: "utf8" });
const tree = block.replace(/^```mermaid\n/, "").replace(/\n```\s*$/, "");

function parse(arm, src) {
  diagram.db.clear();
  diagram.parser.parser.yy = diagram.db;
  let ok = true;
  try { diagram.parser.parse(src); } catch { ok = false; }
  console.log(`RESULT arm=${arm} parsed=${ok} title=${JSON.stringify(ok ? diagram.db.getDiagramTitle() : null)}`);
  return ok;
}
const a = parse("tree", tree);
const b = parse("null", tree.replace(/(dateFormat [^\n]*)/, "$1; x"));
process.exit(a && !b ? 0 : 1);
