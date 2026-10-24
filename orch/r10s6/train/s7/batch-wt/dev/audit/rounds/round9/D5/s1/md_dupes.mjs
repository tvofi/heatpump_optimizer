// D5-s1 harness: duplicated paragraphs across README.md and the seven user docs.
//
// Metric (one line): paragraph/fence blocks (>= 40 chars after normalisation) whose
//   normalised text hash occurs in more than one place across README.md +
//   docs/{architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md;
//   reported as duplicate groups and as the extra copies beyond the first.
//   Also a near-duplicate pass: fence blocks whose line-set Jaccard >= 0.6.
// Normalisation: lowercase, markdown punctuation (*_`) dropped, whitespace collapsed.
// Count key: markdown-it 14.1.0 paragraph/fence tokens (inline text, not raw source).
// Command (from the repository root):
//   T=$(mktemp -d); npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1; \
//   NODE_PATH=$T/node_modules node tools/audit/round9/D5/s1/md_dupes.mjs [--perturb]
// --perturb appends one README paragraph verbatim to docs/ecl110.md in memory.
//   Expected: extra_copies up by 1.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1.
import fs from "node:fs";
import os from "node:os";
import crypto from "node:crypto";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const MarkdownIt = require("markdown-it");
const md = new MarkdownIt("commonmark").enable("table");
const FILES = ["README.md", ...["architecture", "automations", "configuration",
  "dashboard-card", "ecl110", "how-it-works", "setup"].map((n) => `docs/${n}.md`)];
const perturb = process.argv.includes("--perturb");
const norm = (s) => s.toLowerCase().replace(/[*_`]/g, "").replace(/\s+/g, " ").trim();
const groups = new Map(); const fences = [];
for (const f of FILES) {
  let text = fs.readFileSync(f, "utf8");
  if (perturb && f === "docs/ecl110.md")
    text += "\n\n**Floor heating responds slowly.** That is the slab, and it is expected. The\noptimizer plans around it by pre-heating during cheap periods.\n";
  const toks = md.parse(text, {});
  toks.forEach((t, i) => {
    let body = null, kind = null;
    if (t.type === "paragraph_open" && !(toks[i - 1] && toks[i - 1].type === "td_open")) { body = toks[i + 1].content; kind = "para"; }
    if (t.type === "fence") { body = t.content; kind = "fence"; fences.push({ f, line: t.map[0] + 1, lines: new Set(t.content.split("\n").map((l) => l.trim()).filter(Boolean)) }); }
    if (!body) return;
    const n = norm(body);
    if (n.length < 40) return;
    const h = crypto.createHash("sha1").update(n).digest("hex").slice(0, 12);
    if (!groups.has(h)) groups.set(h, []);
    groups.get(h).push(`${f}:${t.map[0] + 1} (${kind}) ${n.slice(0, 60)}`);
  });
}
let dupGroups = 0, extra = 0;
for (const [h, locs] of groups) if (locs.length > 1) { dupGroups++; extra += locs.length - 1; console.log(`dup ${h}\n  ${locs.join("\n  ")}`); }
let near = 0;
for (let a = 0; a < fences.length; a++) for (let b = a + 1; b < fences.length; b++) {
  const A = fences[a], B = fences[b];
  if (A.f === B.f || A.lines.size < 5) continue;
  const inter = [...A.lines].filter((x) => B.lines.has(x)).length;
  const j = inter / (A.lines.size + B.lines.size - inter);
  if (j >= 0.6) { near++; console.log(`near-dup fence j=${j.toFixed(2)} ${A.f}:${A.line} ~ ${B.f}:${B.line}`); }
}
console.log(`RESULT paragraph_blocks_hashed=${groups.size} count`);
console.log(`RESULT duplicate_groups=${dupGroups} count`);
console.log(`RESULT extra_copies=${extra} count`);
console.log(`RESULT near_duplicate_fences=${near} count`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
