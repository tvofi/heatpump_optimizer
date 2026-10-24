// D13-s2 harness: D13.M3 (block classes, three ways) and D13.M6 (friction keys).
// Run (export root): HPO_PLANDATA=$(mktemp -d) node dev/audit/rounds/round10/D13/s2/blocks_friction.mjs <window.json> [--perturb=verdict|budgets-readme|unbacktick]
// window.json comes from fetch_window.py (GitHub API; recorded under exposure).
// Hooks: tools/policy/policy_lint.mjs statsHistogram (frictionKey, verdict histogram),
//        waveVerdictRe + blockClasses (web-fix-wave.js VERDICT_RE / VERDICT_CLASSES).
// M3 metric: every first-line `Fix review: blocked <40hex> ...` verdict (issue comment OR review,
//   ordered by time) parsed by the wave's VERDICT_RE; class = taught word, else its own row
//   (`untaught:<word>`), bare -> `other`. Bucketing (mine): engineering = mutation-vacuous, harness,
//   null-control, product-tradeoff-regression, metric-gamed, architecture-unsound, class-open;
//   record-and-body = claims, version, carry-missing, preflight-mismatch, root-cause-unanswered;
//   orchestration = head-moved, conflict, other, untaught:*. Also: statsHistogram's verdict rows.
// M6 metric: per friction entry (statsHistogram's frictionKey output keyed by entry), the brief's
//   rule: id k (# dropped, backticks stripped) names each policy_budgets.json `files` path p with
//   p==k or p endswith '/'+k, '/'+k+'.md', '/'+k+'/SKILL.md' (or equal to those). One path = one
//   file; >1 = ambiguous; 0 = none. Key of the count: the entry's id as frictionEntries parsed it.
import fs from 'node:fs'
import path from 'node:path'
const ROOT = process.cwd()
const L = await import(path.join(ROOT, 'tools/policy/policy_lint.mjs'))
const [file, ...flags] = process.argv.slice(2)
const perturb = (flags.find((f) => f.startsWith('--perturb=')) ?? '').slice(10)
const W = JSON.parse(fs.readFileSync(file, 'utf8'))
const nums = Object.keys(W.prs).map(Number)
if (perturb === 'verdict') {
  // re-shape the first blocked verdict out of the grammar (abbreviate its SHA)
  outer: for (const n of nums) for (const k of ['comments', 'reviews']) for (const c of W.prs[n][k]) {
    if (/^Fix review:\s+blocked\s+[0-9a-f]{40}/.test(String(c.body ?? '').trim())) { c.body = String(c.body).trim().replace(/([0-9a-f]{12})[0-9a-f]{28}/, '$1'); break outer }
  }
}
const budgets = JSON.parse(fs.readFileSync(path.join(ROOT, 'dev/governance/config/policy_budgets.json'), 'utf8'))
const files = Object.keys(budgets.files)
const re = L.waveVerdictRe(), taught = L.blockClasses()
const B = { engineering: ['mutation-vacuous', 'harness', 'null-control', 'product-tradeoff-regression', 'metric-gamed', 'architecture-unsound', 'class-open'],
  'record-and-body': ['claims', 'version', 'carry-missing', 'preflight-mismatch', 'root-cause-unanswered'],
  orchestration: ['head-moved', 'conflict', 'other'] }
const bucketOf = (c) => Object.entries(B).find(([, v]) => v.includes(c))?.[0] ?? 'orchestration'
const cls = new Map(), bk = new Map(), outside = []
let blocked = 0
const bump = (m, k) => m.set(k, (m.get(k) ?? 0) + 1)
for (const n of nums) {
  const f = W.prs[n]
  const rows = [...f.comments.map((c) => ({ b: c.body, at: c.created_at })), ...f.reviews.map((c) => ({ b: c.body, at: c.submitted_at }))].sort((a, b) => String(a.at).localeCompare(String(b.at)))
  for (const r of rows) {
    const first = String(r.b ?? '').trim().split('\n')[0]
    if (!/^Fix review:\s*blocked/i.test(first)) continue
    const m = re.exec(first)
    if (!m || !m[3]) { outside.push(`#${n}: ${first.slice(0, 60)}`); continue }
    blocked += 1
    const c = m[5] ? (taught.includes(m[5]) ? m[5] : `untaught:${m[5]}`) : 'other'
    bump(cls, c); bump(bk, bucketOf(c))
  }
}
// production histogram on the same payload
const prs = nums.map((pr) => ({ pr }))
const fetched = new Map(nums.map((n) => [n, { body: W.prs[n].body, comments: W.prs[n].comments, reviews: W.prs[n].reviews }]))
// M6: entries, per production key and per brief rule
const one = new Map(), amb = [], none = new Map()
let entries = 0, oneN = 0, ambN = 0, noneN = 0, prodFile = 0, disagree = []
const fileSet = new Set(files)
for (const n of nums) {
  let body = W.prs[n].body
  if (perturb === 'budgets-readme') body = body.replace(/ratchet-budgets\.md/, 'README.md')
  if (perturb === 'unbacktick') body = body.replace(/`ratchet-budgets\.md`/, 'ratchet-budgets')
  fetched.get(n).body = body
  const sec = (body.split(/^## Friction\s*$/m)[1] ?? '').split(/^## /m)[0]
  const one1 = new Map([[n, { body: `## Friction\n${sec}`, comments: [], reviews: [] }]])
  // production key per entry, via statsHistogram on a single-PR payload per entry line set
  const h = L.statsHistogram([{ pr: n }], one1, taught)
  for (const [key, cell] of h.friction) {
    const cnt = cell.entries ?? 1
    entries += cnt
    const k = key.replace(/^`+|`+$/g, '').replace(/#.*$/, '')
    const hits = files.filter((p) => [k, k + '.md', k + '/SKILL.md'].some((s) => p === s || p.endsWith('/' + s)))
    if (fileSet.has(key)) prodFile += cnt
    if (hits.length === 1) { oneN += cnt; const m = one.get(hits[0]) ?? new Map(); m.set(key, (m.get(key) ?? 0) + cnt); one.set(hits[0], m); if (!fileSet.has(key)) disagree.push(`#${n} ${key}->${hits[0]}`) }
    else if (hits.length > 1) { ambN += cnt; amb.push(`#${n} ${key}(${hits.length})`) }
    else { noneN += cnt; bump(none, key) }
  }
}
const H = L.statsHistogram(prs, fetched, taught)
console.log(`WINDOW ${W.since}..${W.until} merges=${W.merges.length} prs=${nums.length} api_failures=${W.api_failures.length}`)
console.log(`RESULT blocked_verdicts=${blocked} count`)
for (const [k, v] of [...cls].sort((a, b) => b[1] - a[1])) console.log(`RESULT block_class[${k}]=${v} count`)
for (const [k, v] of bk) console.log(`RESULT block_bucket[${k}]=${v} count`)
console.log(`RESULT blocked_outside_grammar=${outside.length} count`); for (const o of outside) console.log(`  OUTSIDE ${o}`)
for (const [k, v] of H.verdicts) console.log(`  PROD verdict_row[${k}] prs=${v.prs.size} entries=${v.entries}`)
console.log(`RESULT prod_unclassified=${H.unclassified.length} count`)
console.log(`RESULT friction_entries=${entries} count`)
console.log(`RESULT friction_one_file=${oneN} count`)
console.log(`RESULT friction_ambiguous=${ambN} count`)
console.log(`RESULT friction_no_file=${noneN} count`)
console.log(`RESULT friction_one_file_share=${entries ? (oneN / entries).toFixed(3) : 'n/a'} ratio`)
console.log(`RESULT friction_prod_key_is_budget_file=${prodFile} count`)
console.log(`RESULT friction_rule_file_but_prod_verbatim=${disagree.length} count`)
for (const d of disagree) console.log(`  DISAGREE ${d}`)
for (const [p, m] of one) console.log(`  FILE ${p} ${[...m].map(([s, c]) => `${s}=${c}`).join(' ')}`)
for (const a of amb) console.log(`  AMBIG ${a}`)
for (const [k, v] of none) console.log(`  NONE ${k}=${v}`)
