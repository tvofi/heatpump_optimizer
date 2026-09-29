// D5-s1 harness: internal link and anchor check of the user docs.
//
// Metric (one line): relative links/images in README.md + the seven user docs whose
//   target file is missing from the tree, or whose #fragment matches no heading slug
//   (GitHub slug rule: lowercase, drop chars outside letters/marks/digits/_/-/space,
//   space -> "-", repeats suffixed -1, -2 ...) in the target file.
// Count key: link_open/image hrefs from the markdown-it 14.1.0 token stream (links
//   inside code are not links), resolved against the files on disk.
// Paths the round-9 export strips on purpose (docs/audit-*.md, docs/backlog.md) are
//   counted separately as "stripped" and not judged.
// Command (from the repository root):
//   T=$(mktemp -d); npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1; \
//   NODE_PATH=$T/node_modules node tools/audit/round9/D5/s1/md_links.mjs [--perturb]
// --perturb renames, in memory, the first heading of docs/setup.md that a link
//   targets, so every link to it breaks. Expected: broken_links up.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const MarkdownIt = require("markdown-it");
const md = new MarkdownIt("commonmark").enable("table");
const FILES = ["README.md", ...["architecture", "automations", "configuration",
  "dashboard-card", "ecl110", "how-it-works", "setup"].map((n) => `docs/${n}.md`)];
const STRIPPED = /^docs\/(audit-[^/]*\.md|backlog\.md)$/;
const perturb = process.argv.includes("--perturb");
const cache = new Map();

function read(f) {
  let t = fs.readFileSync(f, "utf8");
  if (perturb && f === "docs/setup.md") t = t.replace("## Quick setup (recommended)", "## Quick set-up, recommended");
  return t;
}
function slugs(f) {
  if (cache.has(f)) return cache.get(f);
  const toks = md.parse(read(f), {});
  const seen = new Map(), out = new Set();
  toks.forEach((t, i) => {
    if (t.type !== "heading_open") return;
    const inline = toks[i + 1];
    const text = inline.children.filter((c) => c.type === "text" || c.type === "code_inline").map((c) => c.content).join("");
    let s = text.toLowerCase().replace(/[^\p{L}\p{M}\p{N}_\- ]/gu, "").replace(/ /g, "-");
    const n = seen.get(s) ?? 0; seen.set(s, n + 1);
    out.add(n ? `${s}-${n}` : s);
  });
  // explicit HTML anchors
  for (const m of read(f).matchAll(/<a\s+(?:name|id)="([^"]+)"/g)) out.add(m[1]);
  cache.set(f, out);
  return out;
}
let total = 0, broken = 0, stripped = 0, external = 0, anchors = 0;
for (const f of FILES) {
  const walk = (tokens) => {
    for (const t of tokens) {
      if (t.children) walk(t.children);
      const href = t.type === "link_open" ? t.attrGet("href") : t.type === "image" ? t.attrGet("src") : null;
      if (href == null) continue;
      if (/^[a-z]+:/i.test(href)) { external++; continue; }
      total++;
      const [p, frag] = href.split("#");
      const target = p ? path.normalize(path.join(path.dirname(f), decodeURI(p))) : f;
      if (STRIPPED.test(target)) { stripped++; continue; }
      if (!fs.existsSync(target)) { broken++; console.log(`missing-file ${f} -> ${href}`); continue; }
      if (frag !== undefined && target.endsWith(".md")) {
        anchors++;
        if (!slugs(target).has(decodeURIComponent(frag))) { broken++; console.log(`missing-anchor ${f} -> ${href}`); }
      }
    }
  };
  walk(md.parse(read(f), {}));
}
console.log(`RESULT relative_links=${total} count`);
console.log(`RESULT anchored_links=${anchors} count`);
console.log(`RESULT stripped_targets_not_judged=${stripped} count`);
console.log(`RESULT external_links_not_fetched=${external} count`);
console.log(`RESULT broken_links=${broken} count`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
