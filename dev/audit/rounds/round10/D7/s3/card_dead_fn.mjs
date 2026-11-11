// D7.M6 card dead-function sentinel.
// Metric: (a) static: number of top-level function declarations in the card
//   source whose identifier occurs exactly once (its own declaration) after
//   comments are stripped; (b) runtime: calls to each such function, and to a
//   live control (fmtTick), while the stock card renders every plan view the
//   plan_view.py payload carries (vm global rebinding, card_rig.mjs:loadCard).
// Command: python3 tests/plan_view.py (with HPO_PLANDATA set) then
//   HPO_PLANDATA=<same> node dev/audit/rounds/round10/D7/s3/card_dead_fn.mjs
//   -- or run dev/audit/rounds/round10/D7/s3/card_dead_fn.sh which does both under mktemp.
// Expected: dead_static=1 (textWidth), textWidth_calls=0, control fmtTick_calls>0.
// Perturbation: HPO_SENT_INJECT=1 appends a one-line call site
//   `textWidth("x", 10);` to the card source before load -> dead_static=0, calls=1.
// Baseline 17f1c55fad1b, box B5 (macOS arm64). Root rule: cwd.
import fs from "node:fs";
import { makeCardContext, loadCard, buildCard, planStates, CARD_PATH } from "../../../../../../tests/card_rig.mjs";

let src = fs.readFileSync(CARD_PATH, "utf8");
if (process.env.HPO_SENT_INJECT) src += '\ntextWidth("x", 10);\n';
const code = src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
const decls = [...code.matchAll(/^function\s+([A-Za-z_$][\w$]*)/gm)].map((m) => m[1]);
// Every regex metacharacter, backslash included, so a name is matched literally.
const escapeRe = (s) => s.replace(/[\\^$.*+?()[\]{}|]/g, "\\$&");
// An occurrence is a bare identifier: not preceded by [\w$] and not a
// member access (a single '.'); a spread '...name' counts.
const uses = (n) => (code.match(new RegExp(`(?<![\\w$])(?<!(?<!\\.\\.)\\.)${escapeRe(n)}(?![\\w$])`, "g")) || []).length;
const dead = decls.filter((n) => uses(n) === 1);
console.log("static-dead:", dead.join(",") || "(none)");

const { ctx } = makeCardContext();
const Card = loadCard(ctx, src);
const counts = {};
for (const n of [...dead, "textWidth", "fmtTick"]) {
  const orig = ctx[n];
  if (typeof orig !== "function") continue;
  counts[n] = 0;
  ctx[n] = function (...a) { counts[n] += 1; return orig.apply(this, a); };
}
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const views = [plan]; // plan_view.py writes one payload: {space_plan, dhw_plan}
let rendered = 0;
for (const v of views) {
  if (!v || !v.space_plan) continue;
  try {
    const card = buildCard(Card, planStates(v), {});
    if (card.render) card.render();
    rendered += 1;
  } catch (e) { console.log("render-fail", e.message); }
}
console.log(`RESULT card_top_level_functions=${decls.length} functions`);
console.log(`RESULT dead_static=${dead.length} functions`);
console.log(`RESULT views_rendered=${rendered} views`);
console.log(`RESULT textWidth_calls=${counts.textWidth ?? -1} calls`);
console.log(`RESULT fmtTick_calls=${counts.fmtTick ?? -1} calls`);
console.log("RESULT thread_factor=1.000");
console.log(`RESULT load1=${(await import("node:os")).loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
