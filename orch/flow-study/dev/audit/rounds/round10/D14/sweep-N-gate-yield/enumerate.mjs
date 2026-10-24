// Class N-gate-yield enumerator (D14 method step 3).
// Seam = every non-engineering block class (governance/record/orchestration, taught or
// untaught) that blocked at least one fix-review verdict in the window. A seam is an
// INSTANCE when its count exceeds the largest engineering block class: the gate's cost
// then dominates review yield (D13-s2-01's property).
// Run (export root): node dev/audit/rounds/round10/D14/sweep-N-gate-yield/enumerate.mjs <window.json> [--fixture=clean|reintro]
//   --fixture=clean   strips every blocked verdict (null control: expect seams=0 instances=0)
//   --fixture=reintro clean, then re-inserts ONE root-cause-unanswered verdict line (perturbation: instances 0->1)
import fs from 'node:fs'
import path from 'node:path'
const L = await import(path.join(process.cwd(), 'tools/policy/policy_lint.mjs'))
const [file, ...flags] = process.argv.slice(2)
const fx = (flags.find((f) => f.startsWith('--fixture=')) ?? '').slice(10)
const W = JSON.parse(fs.readFileSync(file, 'utf8'))
const nums = Object.keys(W.prs).map(Number)
const isBlocked = (b) => /^Fix review:\s*blocked/i.test(String(b ?? '').trim())
if (fx === 'clean' || fx === 'reintro') for (const n of nums) for (const k of ['comments', 'reviews']) W.prs[n][k] = W.prs[n][k].filter((c) => !isBlocked(c.body))
if (fx === 'reintro') W.prs[nums[0]].comments.push({ body: `Fix review: blocked ${'a'.repeat(40)} root-cause-unanswered: reintroduced`, created_at: '9999' })
const ENG = new Set(['mutation-vacuous', 'harness', 'null-control', 'product-tradeoff-regression', 'metric-gamed', 'architecture-unsound', 'class-open',
  // untaught words naming a defect in the fixed code
  'untaught:defect', 'untaught:mutation-unpinned', 'untaught:vacuous', 'untaught:null-control-unpinned', 'untaught:closures-under-approximated',
  'untaught:over-fire', 'untaught:d-unbounded', 'untaught:skip-abusable', 'untaught:skip-dead', 'untaught:guard', 'untaught:docs-code-mismatch',
  'untaught:resolution-docstring-corruption'])
const re = L.waveVerdictRe(), taught = L.blockClasses()
const cls = new Map()
for (const n of nums) for (const k of ['comments', 'reviews']) for (const c of W.prs[n][k]) {
  const first = String(c.body ?? '').trim().split('\n')[0]
  if (!isBlocked(first)) continue
  const m = re.exec(first); if (!m || !m[3]) continue
  const w = m[5] ? (taught.includes(m[5]) ? m[5] : `untaught:${m[5]}`) : 'other'
  cls.set(w, (cls.get(w) ?? 0) + 1)
}
const engMax = Math.max(0, ...[...cls].filter(([w]) => ENG.has(w)).map(([, v]) => v))
const seams = [...cls].filter(([w]) => !ENG.has(w)).sort((a, b) => b[1] - a[1])
let inst = 0
for (const [w, v] of seams) { const i = v > engMax; inst += i; console.log(`SEAM ${w} count=${v} engineering_max=${engMax} ${i ? 'INSTANCE' : 'below'}`) }
console.log(`RESULT seams=${seams.length} instances=${inst} engineering_max=${engMax}`)
