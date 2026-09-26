#!/usr/bin/env node
// D13 round 9, verifier V2 (independent), finding D13-s1-03.
// METRIC (V2's own), over the finder's recorded verdicts (window.json.gz, both
//   endpoints), blocked verdicts parsed by the PRODUCTION policy_lint.mjs:waveVerdictRe:
//   every `<word>:` class token on the verdict's first line is read, not only
//   the first one the regex captures. RESULT body_answer_any = blocked verdicts
//   naming root-cause-unanswered or red-check anywhere; body_answer_only = those
//   naming NO other class (the rounds a pre-review body check could have
//   removed outright); eng_class_max = the largest per-class count of verdicts
//   naming an engineering class anywhere (finder's buckets: mutation-vacuous
//   harness null-control class-open product-tradeoff-regression
//   preflight-mismatch, plus the untaught vacuous/mutation/wrong-input/
//   measurement and `regression`); class-open counted where it follows `harness:`.
// SECOND ARM -- is the mechanical predicate already a pre-review check?
//   pr-contract.yml lists the head's failing check runs and hands them to
//   policy_lint.mjs --pr-body as --red (checkPrBody refuses an unnamed red).
//   From the recorded check runs at every PR's final head (runs_head):
//   RESULT lag_<check>_after_prcontract = heads where <check> COMPLETED after
//   the first pr-contract run at that head completed, of heads carrying both;
//   i.e. the existing check ran before the red it would have to name existed.
//   RESULT prcontract_reads_red = 1 if checkPrBody's red loop is present in the
//   tree (grep of the production source), 0 otherwise.
// NULL CONTROL: RESULT blocked_total must equal the finder's 21 (same population).
// PERTURBATION: V2_PERTURB=strip -- the first blocked verdict's `root-cause-unanswered`
//   token is removed in memory -> body_answer_any falls by 1.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v2/v2_blocks.mjs
// EXPECTED: blocked_total=21; body_answer_any=8 +-0 (counts; contention-immune).
// BASELINE SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: cloud box
//   G1-V2, 4 vCPU Linux, node 22, CPython 3.14.0rc2 (not used); thread_factor 1.
process.env.OMP_NUM_THREADS ??= '1'; process.env.OPENBLAS_NUM_THREADS ??= '1'
import fs from 'node:fs'
import os from 'node:os'
import zlib from 'node:zlib'
import * as PL from '../../../../../.claude/workflows/policy_lint.mjs'
const R = (k, v, u = '') => console.log(`RESULT ${k}=${v}${u ? ' ' + u : ''}`)
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const VRE = PL.waveVerdictRe()
const BODY = new Set(['root-cause-unanswered', 'red-check'])
const ENG = new Set(['mutation-vacuous', 'harness', 'null-control', 'class-open', 'product-tradeoff-regression', 'preflight-mismatch', 'vacuous', 'mutation', 'wrong-input', 'measurement', 'regression'])
let perturbed = false
const rows = [], engCount = new Map()
let total = 0, any = 0, only = 0, both = 0
for (const [n, p] of Object.entries(snap.prs)) {
  for (const c of [...(p.comments ?? []), ...(p.reviews ?? [])]) {
    let first = String(c.body ?? '').trim().split('\n')[0]
    const m = VRE.exec(first)
    if (!m || !m[3]) continue
    if (process.env.V2_PERTURB === 'strip' && !perturbed && first.includes('root-cause-unanswered')) { first = first.replaceAll('root-cause-unanswered:', ''); perturbed = true }
    total++
    const words = [...first.matchAll(/(?:^|[\s;(,])([a-z][a-z-]+):/g)].map((x) => x[1])
    if (/harness:\s*class-open/.test(first)) words.push('class-open')
    const ws = [...new Set(words)].filter((w) => w !== 'review')
    const b = ws.some((w) => BODY.has(w)), e = ws.filter((w) => ENG.has(w))
    for (const w of e) engCount.set(w, (engCount.get(w) ?? 0) + 1)
    if (b) { any++; if (e.length) both++; else only++ }
    rows.push(`#${n} [${ws.join(',')}]${b ? ' BODY' : ''}${e.length ? ' ENG' : ''}`)
  }
}
for (const r of rows) console.log('  ' + r)
R('blocked_total', total)
R('body_answer_any', any)
R('body_answer_only', only)
R('body_answer_with_engineering_class', both)
for (const [k, v] of [...engCount].sort((a, b) => b[1] - a[1])) R(`eng_${k}`, v)
R('eng_class_max', Math.max(0, ...engCount.values()))
R('verdicts_naming_any_engineering_class', rows.filter((r) => r.includes(' ENG')).length)
// second arm
const lag = new Map()
for (const p of Object.values(snap.prs)) {
  const runs = p.runs_head ?? []
  const pc = runs.filter((r) => r.name === 'pr-contract' && r.completed_at).map((r) => r.completed_at).sort()[0]
  if (!pc) continue
  for (const name of ['typing', 'fast (3.14)', 'mutation']) {
    const r = runs.filter((x) => x.name === name && x.status === 'completed' && x.conclusion !== 'skipped').map((x) => x.completed_at).sort().pop()
    if (!r) continue
    const cell = lag.get(name) ?? { after: 0, n: 0, minMin: Infinity }
    cell.n++
    const d = (Date.parse(r) - Date.parse(pc)) / 60000
    if (d > 0) cell.after++
    cell.minMin = Math.min(cell.minMin, d)
    lag.set(name, cell)
  }
}
for (const [k, v] of lag) R(`lag_${k.replace(/[ ().]/g, '')}_after_prcontract`, `${v.after}/${v.n}`, `(min lag ${v.minMin.toFixed(1)} min)`)
const src = fs.readFileSync('.claude/workflows/policy_lint.mjs', 'utf8')
R('prcontract_reads_red', /for \(const name of red\)/.test(src) && /--red/.test(fs.readFileSync('.github/workflows/pr-contract.yml', 'utf8')) ? 1 : 0)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1)
R('swapins', (fs.readFileSync('/proc/vmstat', 'utf8').match(/^pswpin (\d+)/m) || [])[1] ?? 'na')
