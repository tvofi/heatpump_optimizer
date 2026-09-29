// D5-s2 harness (D5.M4, comments in code): card comments that name a private
// member the card does not have.
//
// Metric: distinct `_name` identifiers cited in backticks (`_x`, `_x()`,
//   `this._x`) inside comments of the card that resolve to NOTHING: no live
//   binding in the loaded card (top-level binding, or own/prototype/static
//   member of any class the card defines), no token of the card's code with
//   comments stripped, and no token of the backend (.py/.json/.yaml).
// Count key: the identifier a comment names, resolved against the LIVE card
//   the production file defines when run in tests/card_rig.mjs's vm context
//   (loadCard -> customElements "heatpump-optimizer-card"), not against any
//   attribute of the comment itself.
// Command (from the export root):
//   HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node tools/audit/round9/D5/s2/card_comment_names.mjs
//   add --perturb to apply the one-line-per-comment fix in memory (each
//   stale `_name` rewritten to the name the code now carries, where one
//   exists) before measuring; the count must go DOWN (12 -> 5).
// Expected: RESULT card_stale_private_names=12 names (exact),
//   card_stale_private_mentions=17 (exact); with --perturb 5 / 6.
// Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1).
// Machine: box B2 cloud container (Linux, 4 CPU), node v22.22.2.
// Control arm: the same rule over the production Python comments
//   (`_name` in backticks vs the backend's own tokens) prints
//   RESULT py_stale_private_names -- the rule itself is not noisy.
import fs from "fs";
import os from "os";
import path from "path";
import vm from "vm";
import { createRequire } from "module";
import { makeCardContext, loadCard, CARD_PATH } from "../../../../../tests/card_rig.mjs";

const t0 = process.cpuUsage();
const PERTURB = process.argv.includes("--perturb");
if (!process.env.HPO_PLANDATA) {
  process.env.HPO_PLANDATA = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d5s2-"));
}

// Successors the code carries today, for the --perturb arm only (the fix a
// comment edit would make). Names with no successor stay stale.
const SUCCESSOR = {
  _extraFields: "extraFields",
  _fieldPoints: "fieldPoints",
  _lineLabel: "lineLabel",
  _resolveEntity: "resolveEntity",
  _seriesUnit: "seriesUnit",
  _laneGroupInner: "laneGroupInner",
  _onSlotEdit: "onSlotEdit",
};

let src = fs.readFileSync(CARD_PATH, "utf8");

// Split comments from code with the TypeScript parser (the global install
// every audit box carries under /opt/node22/lib/node_modules): every comment
// range is the leading/trailing trivia of some token of the parsed tree, so
// strings, template literals and regex literals cannot desync the split.
const require = createRequire(import.meta.url);
function loadTs() {
  const tries = [process.env.TS_MODULE, "typescript", "/opt/node22/lib/node_modules/typescript"].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch {} }
  throw new Error("typescript not resolvable; set TS_MODULE to its path");
}
const ts = loadTs();
function splitComments(text) {
  const sf = ts.createSourceFile("card.js", text, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const seen = new Map();
  const add = (r) => { if (r) for (const c of r) seen.set(c.pos, c); };
  const visit = (node) => {
    add(ts.getLeadingCommentRanges(text, node.pos));
    add(ts.getTrailingCommentRanges(text, node.end));
    for (const ch of node.getChildren(sf)) visit(ch);
  };
  visit(sf);
  add(ts.getLeadingCommentRanges(text, sf.endOfFileToken.pos));
  const ranges = [...seen.values()].sort((a, b) => a.pos - b.pos);
  const comments = ranges.map((r) => ({
    line: sf.getLineAndCharacterOfPosition(r.pos).line + 1,
    text: text.slice(r.pos, r.end).replace(/^\/\/|^\/\*|\*\/$/g, ""),
  }));
  let code = ""; let at = 0;
  for (const r of ranges) { code += text.slice(at, r.pos) + " "; at = r.end; }
  code += text.slice(at);
  return { comments, code };
}

function tokens(s) { return new Set(s.match(/[A-Za-z_$][\w$]*/g) || []); }

// The backend's CODE: docstrings and '#' comments removed, so a name a
// Python comment cites cannot vouch for a name a card comment cites.
function pyCode(text) {
  return text
    .replace(/"""[\s\S]*?"""/g, " ").replace(/'''[\s\S]*?'''/g, " ")
    .split("\n").map((l) => { const h = l.indexOf("#"); return h >= 0 && !/["']/.test(l.slice(0, h)) ? l.slice(0, h) : l; }).join("\n");
}

function backendTokens() {
  const root = "custom_components/heatpump_optimizer";
  const out = new Set();
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) { if (e.name !== "www" && e.name !== "__pycache__") walk(p); }
      else if (/\.(json|yaml)$/.test(e.name)) for (const t of tokens(fs.readFileSync(p, "utf8"))) out.add(t);
      else if (e.name.endsWith(".py")) for (const t of tokens(pyCode(fs.readFileSync(p, "utf8")))) out.add(t);
    }
  };
  walk(root);
  return out;
}

function pyCommentTokens() {
  // Control arm: comment and docstring text of the production Python, and
  // its code tokens with comments stripped (a coarse split: '#' outside a
  // string is rare enough here to over-count code, never under-count).
  const root = "custom_components/heatpump_optimizer";
  const cited = [];
  const codeToks = new Set();
  for (const f of fs.readdirSync(root)) {
    if (!f.endsWith(".py")) continue;
    const lines = fs.readFileSync(path.join(root, f), "utf8").split("\n");
    for (const [k, l] of lines.entries()) {
      const h = l.indexOf("#");
      const codePart = h >= 0 && !/["']/.test(l.slice(0, h)) ? l.slice(0, h) : l;
      const comm = h >= 0 && !/["']/.test(l.slice(0, h)) ? l.slice(h) : "";
      for (const t of tokens(codePart.replace(/``?[^`]*``?/g, ""))) codeToks.add(t);
      for (const m of comm.matchAll(/`{1,2}(?:self\.)?(_[A-Za-z]\w*)(?:\(\))?`{1,2}/g)) cited.push({ f, line: k + 1, name: m[1] });
    }
  }
  return { cited, codeToks };
}

if (PERTURB) {
  // In-memory comment fix only: rewrite the stale name inside comments.
  const { comments } = splitComments(src);
  for (const c of comments) {
    let t = c.text;
    for (const [old, nu] of Object.entries(SUCCESSOR)) t = t.split("`" + old).join("`" + nu);
    if (t !== c.text) src = src.split(c.text).join(t);
  }
}

const { comments, code } = splitComments(src);
const codeToks = tokens(code);
const backToks = backendTokens();

// Live bindings: run the production card in the shared rig's context.
const rig = makeCardContext();
const Card = loadCard(rig.ctx, src);
const live = new Set();
const classNames = [...code.matchAll(/\bclass\s+([A-Za-z_$][\w$]*)/g)].map((m) => m[1]);
for (const cn of classNames) {
  const C = vm.runInContext(`typeof ${cn} === "function" ? ${cn} : null`, rig.ctx);
  if (!C) continue;
  for (let p = C.prototype; p && p !== Object.prototype; p = Object.getPrototypeOf(p)) {
    for (const k of Object.getOwnPropertyNames(p)) live.add(k);
  }
  for (const k of Object.getOwnPropertyNames(C)) live.add(k);
}
for (const k of Object.getOwnPropertyNames(Card.prototype)) live.add(k);
const isTopLevel = (name) => {
  try { return vm.runInContext(`typeof ${name} !== "undefined"`, rig.ctx); } catch { return false; }
};

const stale = new Map();
let mentions = 0;
for (const c of comments) {
  for (const m of c.text.matchAll(/`(?:this\.)?(_[A-Za-z][\w$]*)(?:\(\))?`/g)) {
    const name = m[1];
    if (live.has(name) || isTopLevel(name) || codeToks.has(name) || backToks.has(name)) continue;
    mentions++;
    if (!stale.has(name)) stale.set(name, []);
    stale.get(name).push(c.line);
  }
}
for (const [name, lines] of [...stale.entries()].sort()) {
  const succ = SUCCESSOR[name];
  const succLive = succ ? (isTopLevel(succ) || live.has(succ) || codeToks.has(succ)) : false;
  console.log(`STALE ${name} comment_lines=${lines.join(",")} successor=${succ && succLive ? succ : "none"}`);
}

// Control arm: the same rule on the Python side.
const py = pyCommentTokens();
const pyStale = new Set();
for (const c of py.cited) if (!py.codeToks.has(c.name) && !backToks.has(c.name) && !codeToks.has(c.name)) pyStale.add(`${c.f}:${c.line}:${c.name}`);
for (const s of [...pyStale].sort()) console.log(`PY_UNRESOLVED ${s}`);

console.log(`RESULT card_comment_blocks=${comments.length} blocks`);
console.log(`RESULT card_live_members=${live.size} names`);
console.log(`RESULT card_stale_private_names=${stale.size} names`);
console.log(`RESULT card_stale_private_mentions=${mentions} mentions`);
console.log(`RESULT py_stale_private_names=${pyStale.size} names`);
const cpu = process.cpuUsage(t0);
console.log(`RESULT thread_factor=1.00`); // single-threaded Node, no BLAS: the count is contention-immune
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
let swapins = "n/a";
try { swapins = (fs.readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m) || [])[1] || "n/a"; } catch {}
console.log(`RESULT swapins=${swapins}`);
console.log(`# cpu_ms=${((cpu.user + cpu.system) / 1000).toFixed(0)} perturb=${PERTURB}`);
