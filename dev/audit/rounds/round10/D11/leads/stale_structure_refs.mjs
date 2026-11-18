// Leads seat (round 10), owner D11-s1, step D11.M1: stale structure-ratchet references that the
// policy count lint does not see.
//
// Metric (headline): lint_missed_stale_counts = statements, in the claims table below, that state a
//   count of tests/structure_budgets.json metrics different from counts.mjs:derivations().budgets AND
//   are not flagged by counts.mjs:checkCounts run over the same file text (the check policy_lint runs
//   over the corpus). Second metric: retired_key_claims = claims-table lines that present a metric
//   key as live (ratcheted / "the keys") while structure_budgets.json has no such key.
// Count key: checkCounts' returned errors for the file's line, and the key set of the budgets file
//   as derivations() reads it (metadata recorded_at excluded by derivations itself).
// Command (from the root of a git checkout of the baseline; derivations() runs git ls-files):
//   node dev/audit/rounds/round10/D11/leads/stale_structure_refs.mjs [--perturb]
// Expected at 17f1c55fad1b: lint_missed_stale_counts=1, retired_key_claims=3 (tolerance 0).
// Perturbation (--perturb): the stated-count sentence gets the noun the budgets rule keys on
//   ("measures all 24 metrics every run", in memory); checkCounts then flags it and
//   lint_missed_stale_counts falls to 0 -- the rule exists, but keys on an adjacent noun.
// Seam rule: grep -nE "cross_seam_edges|cut_\*|measures all [0-9]+" over dev/governance/**/*.md and
//   tests/structure.py, each hit classified into the table below.
// Machine: macOS arm64 (leads seat). Counts only, contention-immune.
import fs from 'node:fs'
import os from 'node:os'
import { derivations, checkCounts } from '../../../../../../tools/policy/counts.mjs'

const perturb = process.argv.includes('--perturb')
const derived = derivations()
const keys = new Set(Object.keys(JSON.parse(fs.readFileSync('tests/structure_budgets.json', 'utf8'))))
// [file, anchor text on the line, kind, claimed]
const CLAIMS = [
  ['dev/governance/dimensions/D7.md', 'measures all 24 every run', 'count', 24],
  ['dev/governance/dimensions/D7.md', 'the seam cut costs are the `cut_*`', 'key', 'cut_*'],
  ['dev/governance/dimensions/D7.md', 'keys and `cross_seam_edges`', 'key', 'cross_seam_edges'],
  ['tests/structure.py', 'built to price. cross_seam_edges, the ratio', 'key', 'cross_seam_edges'],
]
let missed = 0, retired = 0, held = 0
for (const [file, anchor, kind, claimed] of CLAIMS) {
  let text = fs.readFileSync(file, 'utf8')
  const lines = text.split('\n')
  const idx = lines.findIndex((l) => l.includes(anchor))
  if (idx < 0) { console.log(`anchor-gone ${file}: ${anchor}`); continue }
  if (kind === 'count') {
    if (perturb) text = text.replace('measures all 24 every run', 'measures all 24 metrics every run')
    const flagged = checkCounts(file, text, derived).some((e) => e.where === `${file}:${idx + 1}`)
    const stale = claimed !== derived.budgets
    console.log(`count ${file}:${idx + 1} states ${claimed}, derived ${derived.budgets}, stale=${stale}, checkCounts_flagged=${flagged}`)
    if (stale && !flagged) missed += 1
    if (!stale) held += 1
  } else {
    const live = claimed === 'cut_*' ? [...keys].some((k) => k.startsWith('cut_')) : keys.has(claimed)
    console.log(`key ${file}:${idx + 1} names ${claimed} as a live metric; in budgets: ${live}`)
    if (!live) retired += 1; else held += 1
  }
}
console.log(`RESULT derived_budget_metrics=${derived.budgets} count`)
console.log(`RESULT lint_missed_stale_counts=${missed} count`)
console.log(`RESULT retired_key_claims=${retired} count`)
console.log(`RESULT claims_that_hold=${held} count`)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
console.log('RESULT swapins=na')
