// R10-POLICY-LINT-STATS (#2220, #2221): the `--stats` rows the three D13
// findings measured, printed by the PRODUCTION symbols over a recorded window,
// so a later seat re-derives them offline at any tree.
//
// INPUT. A window file in `dev/audit/rounds/round10/D13/s2/fetch_window.py`'s
// shape (`prs[<n>] = {title, body, comments, reviews}`), fetched once:
//    python3 dev/audit/rounds/round10/D13/s2/fetch_window.py v6.7.16 17f1c55fad1b <out.json>
//    node dev/audit/harnesses/r10_stats_window.mjs <out.json>
// Run from the repository root: the tree's `tools/policy/policy_lint.mjs` is
// the one imported, so the same file measures a base and a head.
//
// WHAT IT PRINTS. `statsHistogram` over the window, then:
//   verdict_head_moved  entries in the verdict table's `head-moved` row (D13-s2-02);
//   blocked_head_moved  first-line `Fix review: blocked <sha> head-moved:` verdicts,
//                       counted here by the wave's own VERDICT_RE -- the row must equal it;
//   rework_entries      the rework row (REWORK_KEY), absent before #2221;
//   reverify_entries    the STATS ROUNDS re-verification part -- the rework row must equal it;
//   verdict_total / parsable_total  the verdict table's entries against the parsable
//                       verdicts the walk saw -- equal when the rows partition them;
// and the production STATS COVERAGE and STATS COVERAGE BY CLASS lines (D13-s1-01;
// the second is absent before #2220 and prints `(absent)`).
// Counts only; no timing, no network.

import fs from 'node:fs'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const file = process.argv[2]
if (!file) {
  console.error('usage: node dev/audit/harnesses/r10_stats_window.mjs <window.json>')
  process.exit(2)
}
const PL = await import(pathToFileURL(path.resolve('tools/policy/policy_lint.mjs')).href)
const W = JSON.parse(fs.readFileSync(file, 'utf8'))
const nums = Object.keys(W.prs)
const prs = nums.map((pr) => ({ pr }))
const fetched = new Map(nums.map((n) => [n, { ...W.prs[n] }]))
const H = PL.statsHistogram(prs, fetched, ['blocked', 'merge'])

const re = PL.waveVerdictRe()
let blockedHm = 0
let parsable = 0
for (const n of nums) {
  for (const c of [...(W.prs[n].comments ?? []), ...(W.prs[n].reviews ?? [])]) {
    const m = re.exec(String(c.body ?? '').trim().split('\n')[0])
    if (!m) continue
    parsable += 1
    if (m[3] && m[5] && m[5].toLowerCase() === 'head-moved') blockedHm += 1
  }
}
let verdictTotal = 0
for (const cell of H.verdicts.values()) verdictTotal += cell.entries
const rework = H.rework?.get(PL.REWORK_KEY)

console.log(`WINDOW ${W.since}..${W.until} prs=${nums.length}`)
console.log(`RESULT verdict_head_moved=${H.verdicts.get(PL.REWORK_CLASS)?.entries ?? 0} count`)
console.log(`RESULT blocked_head_moved=${blockedHm} count`)
console.log(`RESULT rework_entries=${rework ? rework.entries : 'absent'} count`)
console.log(`RESULT reverify_entries=${H.rounds.reverify.entries} count`)
console.log(`RESULT verdict_total=${verdictTotal} count`)
console.log(`RESULT parsable_total=${parsable} count`)
console.log(PL.statsCoverageLine(H.coverage))
console.log(PL.statsCoverageClassLine ? PL.statsCoverageClassLine(H.coverage) : 'STATS COVERAGE BY CLASS: (absent)')
