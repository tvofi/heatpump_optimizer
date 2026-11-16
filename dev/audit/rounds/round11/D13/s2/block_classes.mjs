#!/usr/bin/env node
// D13-s2, step D13.M3 -- block classes, three ways.
//
// Metric: over the merged pull requests first-parent in the window, every `blocked`
//   verdict (an issue comment OR a pull-request review whose trimmed first line parses
//   under web-fix-wave.js's VERDICT_RE) counted (a) by the class word statsHistogram keys
//   it on (VERDICT_CLASSES word, `other` for a bare/classless verdict, an untaught word on
//   its own row), (b) by bucket, (c) the same population as policy_lint.mjs's own window
//   read (`fetchWindow`, driven through a stub `curl` that serves the snapshot with
//   GitHub's paging) delivers it. Key: the verdict comment/review id, never a title.
// Bucketing (this harness's, D13.M3 asks for it to be stated here):
//   engineering        mutation-vacuous harness null-control class-open
//                      product-tradeoff-regression metric-gamed architecture-unsound
//   record-and-body    claims version carry-missing root-cause-unanswered
//                      root-cause-detectable root-cause-unrecorded
//   orchestration      head-moved preflight-mismatch conflict
//   unrouted           other (bare `blocked <sha>`, `blocked <sha>: why`, or the word `other`)
//   untaught words     each its own row; bucketed by UNTAUGHT_BUCKET below, stated per word
// Instrumented symbols: tools/policy/policy_lint.mjs:statsHistogram (classification),
//   :fetchWindow (the window read), :waveVerdictRe / :blockClasses (the grammar).
// Command (offline, from the export root):
//   HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node dev/audit/rounds/round11/D13/s2/block_classes.mjs \
//     [--window dev/audit/rounds/round11/D13/s2/window.json] [--perturb reshape-one|teach-ci-red] [--no-window-read] [--list]
// Perturbations (fixture-only, D13.md): --perturb reshape-one re-shapes the window's first
//   blocked verdict out of the grammar (`Fix review: BLOCKED ...`): blocked_verdicts moves
//   down by exactly 1 and outside_grammar up by 1. --perturb teach-ci-red adds `ci-red` to
//   VERDICT_CLASSES in memory: untaught_blocked falls by exactly class_ci-red (63 -> down).
//   --no-window-read skips arm (c) (about 1700 stub-curl calls, minutes).
// Expected (baseline 92d38ecb, window v7.1.0..92d38ecb, snapshot window.json): the RESULT
//   lines are exact counts over the committed snapshot (tolerance: exact).
// Machine: box B8 (shared). No timing is measured.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { statsHistogram, fetchWindow, blockClasses, waveVerdictRe } from '../../../../../../tools/policy/policy_lint.mjs'

const argv = process.argv.slice(2)
const opt = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d)
const HERE = path.dirname(new URL(import.meta.url).pathname)
const WIN = opt('--window', path.join(HERE, 'window.json'))
const PERTURB = opt('--perturb', null)
const snap = JSON.parse(fs.readFileSync(WIN, 'utf8'))

const BUCKET = {
  engineering: ['mutation-vacuous', 'harness', 'null-control', 'class-open', 'product-tradeoff-regression', 'metric-gamed', 'architecture-unsound'],
  'record-and-body': ['claims', 'version', 'carry-missing', 'root-cause-unanswered', 'root-cause-detectable', 'root-cause-unrecorded'],
  orchestration: ['head-moved', 'preflight-mismatch', 'conflict'],
  unrouted: ['other'],
}
// Untaught class words met in the window, bucketed by what the reasons beside them name
// (read in the window's verdicts; one bucket per word, the judgement stated here).
const UNTAUGHT_BUCKET = Object.fromEntries([
  ['engineering', ['mutation-survivor', 'mutation-survivors', 'defect', 'claim-refuted', 'regression', 'tests-gap',
    'harness-vacuous', 'regression-unmeasured', 'trace-gap', 'null-control-leak', 'equivalence-refuted', 'mutant-committed',
    'pin-missing', 'reference-basis-unbumped', 'selftest-scope-ungated', 'under-scoped', 'dropped-entries',
    'census-misclassified', 'introduced-red', 'self-test-red', 'sufficiency', 'caused-by-unwritable', 'caused-by-overbroad',
    'doc-claim-false', 'claim-false', 'prior-findings-open', 'flaky-harness', 'config-attack', 'robustness',
    'mutant-survives', 'countermeasure-unsound', 'instrument-broken', 'selftest-red', 'over-fire', 'unpinned-site',
    'suite-red', 'mutation-unpinned', 'claim-stronger-than-check', 'scope-rule-widened', 'resolution-ungated-step',
    'own-row-not-generated', 'requirement-unmet', 'ratchet-grown', 'settle-unjudged', 'swap-void-undone', 'wait-cycle']],
  ['record-and-body', ['body-stale', 'figure-wrong', 'figures-uncited', 'figure-mislabelled', 'body', 'body-not-applied',
    'evidence-cut', 'evidence-comment', 'comment-evidence', 'carry-dismissal-unsupported', 'owner-words', 'policy-unapproved',
    'findings-unresolved', 'red-unanswered', 'red-checks', 'carry-unmet', 'carry-unanswered', 'body-carry-missing',
    'carry-over-wide', 'citation-false', 'citation-wrong', 'figure-false', 'owner-stale', 'owner-ruling-contradicted',
    'raise-unjustified', 'stale-reference', 'rule-conflict', 'rule-lost']],
  ['orchestration', ['ci-red', 'gate-red', 'ci-cancelled', 'ci-pending', 'merge-conflict', 'main-conflict', 'scope-overlap',
    'part-topic-collision', 'stale-base', 'ci-incomplete', 'ci-unsettled', 'ci-deferral-red', 'ci-red-cancelled',
    'pr-contract-red', 'pr-closed', 'merge-semantics', 'semantic-conflict', 'scope-incomplete', 'beyond-card']],
].flatMap(([b, ws]) => ws.map((w) => [w, b])))
const bucketOf = (w) => Object.entries(BUCKET).find(([, ws]) => ws.includes(w))?.[0] ?? UNTAUGHT_BUCKET[w] ?? 'untaught (unbucketed)'

// --perturb teach-ci-red: the wave's VERDICT_CLASSES literal, edited IN MEMORY to carry
// `ci-red`, read through the production extractor; untaught_blocked must fall by ci-red's count.
const waveText = fs.readFileSync('.claude/workflows/web-fix-wave.js', 'utf8')
const classes = PERTURB === 'teach-ci-red'
  ? blockClasses(waveText.replace("const VERDICT_CLASSES = [", "const VERDICT_CLASSES = [ 'ci-red',"))
  : blockClasses()
// bus.sh's own vocabulary: the dispatch path's MECHANICAL_CLASSES (fixer.md "Never for a
// mechanical-only gap"), read from its source.
const busMech = (/^MECHANICAL_CLASSES=" ([^"]*) "/m.exec(fs.readFileSync('tools/audit/seat/bus.sh', 'utf8'))?.[1] ?? '').split(/\s+/).filter(Boolean)
const re = waveVerdictRe()
if (!classes || !re) throw new Error('could not read the wave grammar')

// The snapshot as fetchWindow's map shape. A comment body is stored whole only when
// its first line is a `Fix review:` line; any other comment carries its first line,
// which is all the walk reads of it.
const merges = snap.merges.map((m) => ({ ...m, pr: String(m.pr) }))
if (PERTURB === 'reshape-one') {
  outer: for (const m of merges) {
    for (const c of [...m.comments, ...m.reviews]) {
      const first = String(c.body ?? c.first ?? '').trim().split('\n')[0]
      const v = re.exec(first)
      if (v && v[3]) {
        c.body = String(c.body ?? c.first).replace(/^(\s*)Fix review:\s+blocked/, '$1Fix review: BLOCKED')
        console.log(`PERTURB reshaped #${m.pr} ${c.id}`)
        break outer
      }
    }
  }
}
const toFetched = (m, cap = Infinity) => ({
  body: m.body,
  title: m.title,
  comments: m.comments.slice(0, cap).map((c) => ({ body: c.body ?? c.first, created_at: c.created_at, id: c.id })),
  reviews: m.reviews.slice(0, cap).map((r) => ({ body: r.body ?? r.first, submitted_at: r.submitted_at, id: r.id })),
})
const prs = merges.map((m) => ({ pr: m.pr, sha: m.sha, subject: m.subject }))
const full = new Map(merges.map((m) => [m.pr, toFetched(m)]))

// --list: the step's universe, one blocked verdict per line (the enumerator).
if (argv.includes('--list')) {
  for (const m of merges) {
    for (const [origin, xs] of [['issue-comment', m.comments], ['review', m.reviews]]) {
      for (const c of xs) {
        const v = re.exec(String(c.body ?? c.first ?? '').trim().split('\n')[0])
        if (v && v[3]) console.log(`#${m.pr} ${origin} ${c.id} ${v[5] ?? 'other'}`)
      }
    }
  }
  process.exit(0)
}
// (a) production's classification over every page.
const h = statsHistogram(prs, full, classes)
const rows = [...h.verdicts.entries()].filter(([w]) => w !== 'merge')
const blocked = rows.reduce((n, [, c]) => n + c.entries, 0)
console.log(`WINDOW ${snap.since}..${snap.head.slice(0, 12)} merges=${prs.length} api_failures=${snap.api_failures.length}`)
console.log('\n(a) blocked verdicts by class word (statsHistogram key)')
const byBucket = new Map()
for (const [w, c] of rows.sort((a, b) => b[1].entries - a[1].entries)) {
  const taught = classes.includes(w)
  const b = bucketOf(w)
  byBucket.set(b, (byBucket.get(b) ?? 0) + c.entries)
  console.log(`  ${w.padEnd(28)} ${String(c.entries).padStart(4)} verdicts ${String(c.prs.size).padStart(4)} PRs  ${taught ? 'taught' : 'UNTAUGHT (own row)'}  -> ${b}`)
  console.log(`RESULT class_${w}=${c.entries} verdicts`)
}
for (const w of classes) if (!h.verdicts.has(w)) console.log(`  ${w.padEnd(28)}    0`)
console.log('\n(b) by bucket')
for (const [b, n] of [...byBucket.entries()].sort((x, y) => y[1] - x[1])) {
  console.log(`  ${b.padEnd(24)} ${n}`)
  console.log(`RESULT bucket_${b.replace(/[^a-z]+/g, '_')}=${n} verdicts`)
}
console.log(`RESULT blocked_verdicts=${blocked} verdicts`)
const untaught = rows.filter(([w]) => !classes.includes(w))
const untaughtN = untaught.reduce((n, [, c]) => n + c.entries, 0)
const untaughtPrs = new Set(untaught.flatMap(([, c]) => [...c.prs]))
console.log(`RESULT untaught_blocked=${untaughtN} verdicts`)
console.log(`RESULT untaught_share=${(untaughtN / blocked).toFixed(3)} ratio`)
console.log(`RESULT untaught_words=${untaught.length} words`)
console.log(`RESULT untaught_prs=${untaughtPrs.size} pull_requests`)
const busOnly = busMech.filter((w) => !classes.includes(w))
const busHit = untaught.filter(([w]) => busMech.includes(w))
console.log(`  bus.sh MECHANICAL_CLASSES (${busMech.length}): ${busMech.join(' ')}`)
console.log(`  of them outside VERDICT_CLASSES (${busOnly.length}): ${busOnly.join(' ')}`)
console.log(`RESULT bus_mechanical_not_in_wave=${busOnly.length} words`)
console.log(`RESULT untaught_in_bus_vocabulary=${busHit.reduce((n, [, c]) => n + c.entries, 0)} verdicts (${busHit.map(([w, c]) => w + ':' + c.entries).join(' ')})`)
console.log(`RESULT class_other_routed=${(h.verdicts.get('other')?.entries ?? 0) + untaughtN} verdicts (parseVerdict routes an untaught word to \`other\`)`)
console.log(`RESULT merge_verdicts=${h.verdicts.get('merge')?.entries ?? 0} verdicts`)
console.log(`RESULT outside_grammar=${h.unclassified.length} lines`)
for (const u of h.unclassified) console.log(`  outside: ${u}`)

// Largest single engineering class against the record-and-body bucket (D13.md severity).
const engMax = Math.max(0, ...rows.filter(([w]) => bucketOf(w) === 'engineering').map(([, c]) => c.entries))
console.log(`RESULT engineering_max_class=${engMax} verdicts`)
console.log(`RESULT record_and_body_total=${byBucket.get('record-and-body') ?? 0} verdicts`)

// (c) the same window through fetchWindow itself: a stub `curl` on PATH answers each
// GitHub path from the snapshot with GitHub's own paging (per_page, page), so the read
// policy_lint's --stats makes is the read measured.
if (!argv.includes('--no-window-read')) {
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd13s2-'))
const db = path.join(tmp, 'db.json')
fs.writeFileSync(db, JSON.stringify(Object.fromEntries(merges.map((m) => [m.pr, toFetched(m)]))))
const stub = path.join(tmp, 'curl')
fs.writeFileSync(stub, `#!/usr/bin/env node
const fs=require('fs');const db=JSON.parse(fs.readFileSync(${JSON.stringify(db)},'utf8'))
const url=process.argv[process.argv.length-1];const u=new URL(url)
fs.readFileSync(0)
const per=+(u.searchParams.get('per_page')||30), page=+(u.searchParams.get('page')||1)
let m, out=null
if((m=/\\/pulls\\/(\\d+)$/.exec(u.pathname))) out={body:db[m[1]].body,title:db[m[1]].title}
else if((m=/\\/issues\\/(\\d+)\\/comments$/.exec(u.pathname))) out=db[m[1]].comments.slice((page-1)*per,page*per)
else if((m=/\\/pulls\\/(\\d+)\\/reviews$/.exec(u.pathname))) out=db[m[1]].reviews.slice((page-1)*per,page*per)
fs.appendFileSync(${JSON.stringify(path.join(tmp, 'ledger'))}, u.pathname+u.search+'\\n')
process.stdout.write(out==null?'{}\\n404':JSON.stringify(out)+'\\n200')
`)
fs.chmodSync(stub, 0o755)
process.env.PATH = `${tmp}:${process.env.PATH}`
process.env.GITHUB_TOKEN = 'stub'
const fw = fetchWindow(prs)
if (fw.fetchError) throw new Error(fw.fetchError)
const h2 = statsHistogram(prs, fw.fetched, classes)
const blocked2 = [...h2.verdicts.entries()].filter(([w]) => w !== 'merge').reduce((n, [, c]) => n + c.entries, 0)
const all2 = [...h2.verdicts.values()].reduce((n, c) => n + c.entries, 0)
const all1 = [...h.verdicts.values()].reduce((n, c) => n + c.entries, 0)
const over = merges.filter((m) => m.comments.length > 100 || m.reviews.length > 100)
console.log('\n(c) the same window as fetchWindow reads it (one page of 100 per endpoint)')
console.log(`  PRs with more than 100 comments or reviews: ${over.map((m) => `#${m.pr} (${m.comments.length}c/${m.reviews.length}r)`).join(', ') || 'none'}`)
console.log(`  calls: ${fs.readFileSync(path.join(tmp, 'ledger'), 'utf8').trim().split('\n').length}`)
console.log(`RESULT fetchwindow_blocked_verdicts=${blocked2} verdicts`)
console.log(`RESULT fetchwindow_lost_blocked=${blocked - blocked2} verdicts`)
console.log(`RESULT fetchwindow_lost_verdicts=${all1 - all2} verdicts`)
console.log(`RESULT prs_over_one_page=${over.length} pull_requests`)
const lostRows = []
for (const [w, c] of h.verdicts) {
  const d = c.entries - (h2.verdicts.get(w)?.entries ?? 0)
  if (d) lostRows.push(`${w}:${d}`)
}
console.log(`  lost by class: ${lostRows.join(' ') || 'none'}`)
fs.rmSync(tmp, { recursive: true, force: true })
}
console.log(`RESULT thread_factor=1.00`)
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let swapins = 0
try { swapins = +/pswpin (\d+)/.exec(fs.readFileSync('/proc/vmstat', 'utf8'))[1] } catch {}
console.log(`RESULT swapins=${swapins}`)
