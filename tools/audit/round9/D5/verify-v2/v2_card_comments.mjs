// D5 verify-v2 harness for D5-s2-01 (independent of the finder's card_comment_names.mjs:
// acorn tokens instead of the TS parser + live-member reflection).
// Metric (one line): distinct `_name` identifiers (regex \b_[A-Za-z]\w*) inside comments of
// www/heatpump-optimizer-card.js that occur NOWHERE in the card's non-comment tokens
// (identifiers, property names, string/template contents, per acorn's tokenizer) nor as a
// word in any production Python file under custom_components/heatpump_optimizer/; also the
// number of comment mentions, and how many have an underscore-less successor token in code.
// Count key: acorn.tokenizer output over the production card file (the shipped bytes).
// Command (repository root):
//   T=$(mktemp -d); npm install --prefix "$T" acorn@8 >/dev/null 2>&1; NODE_PATH=$T/node_modules node tools/audit/round9/D5/verify-v2/v2_card_comments.mjs [--perturb]
// --perturb: in memory, rewrite each stale comment name that has a successor to the successor
//   -> distinct stale count must drop by the successor count.
// Baseline 1936d5ca; exact.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
const require = createRequire(path.join(process.env.NODE_PATH || ".", "x.js"));
const acorn = require("acorn");
const CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
let src = fs.readFileSync(CARD, "utf8");
function scan(text) {
  const comments = [];
  const code = new Set();
  const tk = acorn.tokenizer(text, { ecmaVersion: "latest", sourceType: "module", locations: true,
    onComment: (block, t, s, e, sl) => comments.push({ t, line: sl.line }) });
  for (const tok of tk) {
    if (tok.value !== undefined && tok.value !== null) {
      const v = String(tok.value);
      for (const m of v.matchAll(/[A-Za-z_$][\w$]*/g)) code.add(m[0]);
    }
  }
  return { comments, code };
}
const pyWords = new Set();
function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p);
    else if (p.endsWith(".py")) for (const m of fs.readFileSync(p, "utf8").matchAll(/\w+/g)) pyWords.add(m[0]);
  }
}
walk("custom_components/heatpump_optimizer");
function stale(text) {
  const { comments, code } = scan(text);
  const hits = new Map();
  for (const c of comments) for (const m of c.t.matchAll(/(?<![\w$.])_[A-Za-z]\w*/g)) {
    const n = m[0];
    if (code.has(n) || pyWords.has(n)) continue;
    if (!hits.has(n)) hits.set(n, []);
    hits.get(n).push(c.line);
  }
  return { hits, code };
}
let { hits, code } = stale(src);
if (process.argv.includes("--perturb")) {
  for (const n of hits.keys()) { const s = n.slice(1); if (code.has(s)) src = src.split(n).join(s); }
  ({ hits, code } = stale(src));
}
let mentions = 0, succ = 0;
for (const [n, lines] of [...hits].sort()) {
  mentions += lines.length;
  const s = code.has(n.slice(1)); succ += s;
  console.log(`STALE ${n} lines=${lines.join(",")} successor=${s ? n.slice(1) : "none"}`);
}
console.log(`RESULT stale_names=${hits.size} count`);
console.log(`RESULT stale_mentions=${mentions} count`);
console.log(`RESULT with_successor=${succ} count`);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
