// R10-BRIEFS-FOLD: does every block class web-fix-wave.js teaches land in a
// bucket of D13's blocks_friction.mjs and on a side of D14's N-gate-yield
// enumerator, rather than in their fallbacks?
//
//   node dev/audit/harnesses/r10_briefs_fold_placement.mjs
//
// Both scripts read a window.json fetched from GitHub; this one writes a
// synthetic window with one blocked verdict each of root-cause-detectable,
// root-cause-unrecorded (#2275's split), root-cause-unanswered and harness,
// and runs both scripts on it from the tree root. Metric, one line per arm:
//   RESULT arm=friction  <each block_bucket line>   -- placed: record-and-body=3
//                                                      (the fallback files the two
//                                                      new words under orchestration)
//   RESULT arm=enumerate seams=3 instances=0          -- the three record words
//   RESULT arm=<script>-unplaced rc=2                 -- a copy whose taught list gains
//                                                      `zz-new` is refused: the
//                                                      precondition's positive control
import { execFileSync, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const work = fs.mkdtempSync(path.join(os.tmpdir(), "briefs-fold-"));
const sha = "a".repeat(40);
const verdict = (word, at) => ({ body: `Fix review: blocked ${sha} ${word}: probe`, created_at: at });
const window = { since: "x", until: "y", merges: [], api_failures: [], prs: { 1: { body: "", reviews: [],
  comments: ["root-cause-detectable", "root-cause-unrecorded", "harness", "root-cause-unanswered"].map((w, i) => verdict(w, String(i))) } } };
const win = path.join(work, "window.json");
fs.writeFileSync(win, JSON.stringify(window));
const scripts = {
  friction: "dev/audit/rounds/round10/D13/s2/blocks_friction.mjs",
  enumerate: "dev/audit/rounds/round10/D14/sweep-N-gate-yield/enumerate.mjs",
};
const env = { ...process.env, HPO_PLANDATA: work };
const run = (file) => spawnSync("node", [file, win], { cwd: root, env, encoding: "utf8" });

const friction = run(path.join(root, scripts.friction)).stdout.split("\n").filter((l) => l.startsWith("RESULT block_bucket"));
console.log(`RESULT arm=friction ${friction.map((l) => l.replace(/^RESULT block_bucket\[(.+)\]=(\d+) count$/, "$1=$2")).join(" ")}`);
const enumerate = execFileSync("node", [path.join(root, scripts.enumerate), win], { cwd: root, env, encoding: "utf8" });
console.log(`RESULT arm=enumerate ${enumerate.trim().split("\n").at(-1).replace(/^RESULT /, "")}`);
for (const [arm, file] of Object.entries(scripts)) {
  const copy = path.join(work, `${arm}.mjs`);
  const text = fs.readFileSync(path.join(root, file), "utf8");
  const planted = text.replace("taught = L.blockClasses()", "taught = [...L.blockClasses(), 'zz-new']");
  if (planted === text) throw new Error(`${file}: the taught-list read moved; this harness no longer plants`);
  fs.writeFileSync(copy, planted);
  console.log(`RESULT arm=${arm}-unplaced rc=${run(copy).status}`);
}
fs.rmSync(work, { recursive: true, force: true });
