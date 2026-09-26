#!/usr/bin/env node
// D13 / round 9 / seat s1 -- D13.M1 (first-pass yield, rounds per merge),
// D13.M2 (verdict coverage by class), D13.M3 (block classes, three ways).
//
// METRICS (one line each):
//   M1 yield_first_verdict = share of window merges with >=1 verdict whose
//      FIRST verdict (issue comment or PR review, first line matching the
//      brief's ^Fix review:\s*(merge|blocked), time-ordered) is `merge`;
//      rounds = verdicts per merge carrying one (mean, max).
//   M1' the same through the PRODUCTION reader: policy_lint.mjs:statsHistogram
//      (the wave's VERDICT_RE, both endpoints), its rounds/coverage lines.
//   M2 no_verdict[class] = window merges with no parsable verdict, by class of
//      title prefix + author (rule below).
//   M3 blocked[class] = blocked verdicts by VERDICT_CLASSES word (web-fix-wave.js,
//      read through policy_lint.mjs:blockClasses), then by bucket (below).
// POPULATION: first-parent commits of v6.6.0..1936d5ca whose /commits/<sha>/pulls
//   answers a PR (the API mode of policy_lint.mjs:enumerateMerges, driven here
//   on the snapshot's map). Count key: the PR NUMBER set, never a total.
// M2 CLASS RULE (mine, stated): author `hpo-author[bot]`-like App or human, title
//   prefix before the first ':' or '(' lower-cased:
//     bot cycle  = author login ends in [bot] and is not hpo-author, OR title starts `ci:`
//     record/chore = prefix in {record, chore, docs, stamp, plan, handover} or title
//                    starts `record` / contains `delivery row`
//     fix/feature = prefix in {fix, feat, feature, perf, refactor, test, tests}
//                   or `Fix` / `Feat` capitalised
//     untitled   = title is a merge subject (`Merge ...`/`Absorb ...`), no prefix to read
//     other lane = everything else (policy, tooling, audit, ...)
//   Exemption column: a rule citation is printed only where a tree file exempts
//   the class; none does today (grep in the harness: EXEMPT_RULES is empty).
// M3 BUCKETS (mine, stated):
//     engineering = mutation-vacuous harness null-control class-open
//                   product-tradeoff-regression preflight-mismatch
//     record-and-body = claims version carry-missing root-cause-unanswered
//     orchestration = head-moved conflict
//     other = `other` and a bare `blocked <sha>`; an untaught word keeps its own
//     class row and is bucketed by the taught class it restates (SYN below)
//   body-answer = root-cause-unanswered + red-check (a red check the body does not
//     answer); RESULT m3_body_answer_blocks vs m3_max_engineering_class.
// M1b REVERIFY: every parsable verdict after a `merge` verdict that names a
//   different head (production statsHistogram's `reverify` part, re-walked here
//   to keep each round's verdict word); per round, the first-parent commits
//   prev_head..head (git): only merges (of main) / only `ci:` bot commits /
//   branch content. RESULT reverify_blocked = such rounds whose verdict is
//   `blocked` -- what the re-verification caught.
//   Perturbations: D13_PERTURB=block_one_reverify turns ONE reverify round's
//   verdict into `blocked <same head> harness: x` -> reverify_blocked 0 -> 1;
//   D13_PERTURB=rca_to_harness re-words ONE root-cause-unanswered verdict as
//   `harness:` -> m3_body_answer_blocks -1, m3_bucket_engineering +1.
//
// COMMAND (repository root):
//   HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/s1/yield_rounds.mjs
//   Perturbation (M2): D13_PERTURB=reshape_one  -- re-shapes ONE verdict comment
//   (the first merge's first verdict) out of the grammar in memory: production
//   coverage must fall by exactly one.
// EXPECTED at 1936d5ca (exact; counts over a closed, snapshotted window): see
//   REPORT.md; tolerance exact. MACHINE: any (network-free; reads window.json.gz).
// BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
import fs from 'node:fs'
import zlib from 'node:zlib'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as PL from '../../../../../../.claude/workflows/policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(HERE, 'window.json.gz'))).toString())
const R = (k, v, u = '') => console.log(`RESULT ${k}=${v}${u ? ' ' + u : ''}`)
const PERTURB = process.env.D13_PERTURB || ''

// Population: enumerateMerges is not exported, so its API-mode rule is applied
// verbatim: first row's number per first-parent sha, sha with no row skipped,
// first occurrence of a number kept.
const seen = new Set()
const merges = []
let apiFailures = snap.api_failures
let multiRow = []
for (const c of snap.commits) {
  if (c.pulls == null) continue
  if (!c.pulls.length) continue
  if (c.pulls.length > 1) multiRow.push(c.sha.slice(0, 10))
  const pr = String(c.pulls[0].number)
  if (seen.has(pr)) continue
  seen.add(pr)
  merges.push({ pr, sha: c.sha, subject: c.subject })
}
// set check: every `Merge pull request #N` subject's N is in the API set
const subjNums = new Set(snap.commits.map((c) => (/^Merge pull request #(\d+)/.exec(c.subject) || [])[1]).filter(Boolean))
const onlySubj = [...subjNums].filter((n) => !seen.has(n))
const onlyApi = [...seen].filter((n) => !subjNums.has(n))

const fetched = new Map()
for (const { pr } of merges) {
  const p = snap.prs[pr]
  if (!p || p.comments == null || p.reviews == null) { apiFailures += p ? 0 : 1; continue }
  fetched.set(pr, {
    body: p.body,
    comments: p.comments.map((c) => ({ body: c.body, created_at: c.at, user: c.user })),
    reviews: p.reviews.map((c) => ({ body: c.body, submitted_at: c.at, user: c.user })),
  })
}
if (PERTURB === 'reshape_one') {
  // one verdict comment re-shaped out of the grammar
  for (const { pr } of merges) {
    const f = fetched.get(pr)
    const i = f?.comments.findIndex((c) => /^Fix review:\s+(merge|blocked)\s/.test(String(c.body).trim()))
    if (f && i >= 0) {
      const all = [...f.comments, ...f.reviews].filter((c) => /^Fix review:/.test(String(c.body).trim()))
      if (all.length === 1) { f.comments[i] = { ...f.comments[i], body: 'Fix review: PASS -- ' + f.comments[i].body.slice(12) }; console.log(`perturbed #${pr}`); break }
    }
  }
}
const VRE = PL.waveVerdictRe()
if (PERTURB === 'block_one_reverify' || PERTURB === 'rca_to_harness') {
  outer: for (const { pr } of merges) {
    const f = fetched.get(pr)
    if (!f) continue
    const cs = [...f.comments].sort((a, b) => String(a.created_at).localeCompare(String(b.created_at)))
    let prev = null
    for (const c of cs) {
      const m = VRE.exec(String(c.body).trim().split('\n')[0])
      if (!m) continue
      const head = m[2] ?? m[4]
      if (PERTURB === 'block_one_reverify' && prev && prev.pass && m[1] && head !== prev.head) {
        c.body = `Fix review: blocked ${head} harness: perturbed`; console.log(`perturbed #${pr}`); break outer
      }
      if (PERTURB === 'rca_to_harness' && m[5] === 'root-cause-unanswered') {
        c.body = c.body.replace('root-cause-unanswered:', 'harness:'); console.log(`perturbed #${pr}`); break outer
      }
      prev = { pass: Boolean(m[1]), head }
    }
  }
}

// ---- M1 by the brief's rule --------------------------------------------------
const BRIEF_RE = /^Fix review:\s*(merge|blocked)/
const walk = (f) => [
  ...f.comments.map((c) => ({ body: c.body, at: c.created_at, origin: 'comment', user: c.user })),
  ...f.reviews.map((c) => ({ body: c.body, at: c.submitted_at, origin: 'review', user: c.user })),
].sort((a, b) => String(a.at ?? '').localeCompare(String(b.at ?? '')))
let withV = 0, firstMerge = 0, total = 0, maxR = 0
const outside = []
const briefPerPr = new Map()
for (const { pr } of merges) {
  const f = fetched.get(pr)
  if (!f) continue
  const vs = []
  for (const c of walk(f)) {
    const first = String(c.body ?? '').trim().split('\n')[0]
    if (!/^Fix review:/i.test(first)) continue
    const m = BRIEF_RE.exec(first)
    if (!m) { outside.push(`#${pr} (${c.origin}): ${first.slice(0, 60)}`); continue }
    if (!PL.waveVerdictRe().exec(first)) outside.push(`#${pr} (${c.origin}, brief-parsable, wave-refused): ${first.slice(0, 60)}`)
    vs.push({ word: m[1], origin: c.origin, first })
  }
  briefPerPr.set(pr, vs)
  if (!vs.length) continue
  withV += 1
  total += vs.length
  maxR = Math.max(maxR, vs.length)
  if (vs[0].word === 'merge') firstMerge += 1
}
R('window_merges', merges.length)
R('first_parent_commits', snap.commits.length)
R('api_multi_row_commits', multiRow.length)
R('subject_only_numbers', onlySubj.length)
R('api_only_numbers', onlyApi.length)
R('brief_merges_with_verdict', withV)
R('brief_first_verdict_yield', withV ? (firstMerge / withV).toFixed(3) : 'na', `(${firstMerge}/${withV})`)
R('brief_rounds_mean', withV ? (total / withV).toFixed(3) : 'na', 'verdicts/merge')
R('brief_rounds_max', maxR)
R('verdict_lines_outside_or_wave_refused', outside.length)
for (const o of outside) console.log('  outside: ' + o)

// ---- M1' production reader --------------------------------------------------
const classes = ['blocked', 'merge']
const H = PL.statsHistogram(merges, fetched, classes)
console.log(PL.statsCoverageLine(H.coverage))
console.log(PL.statsRoundsLine(H))
console.log(PL.statsEndpointLine(H.endpoints))
R('prod_coverage_verdict_prs', H.coverage.verdictPrs.size)
R('prod_no_verdict', H.coverage.noVerdict.length)
R('prod_first_verdict_yield', (H.rounds.firstMerge / (H.coverage.verdictPrs.size || 1)).toFixed(3), `(${H.rounds.firstMerge}/${H.coverage.verdictPrs.size})`)
R('prod_one_round_yield', (H.rounds.oneRound / (H.coverage.verdictPrs.size || 1)).toFixed(3), `(${H.rounds.oneRound}/${H.coverage.verdictPrs.size})`)
R('prod_unclassified', H.unclassified.length)
for (const u of H.unclassified) console.log('  prod unclassified: ' + u)
for (const [k, cell] of H.endpoints) R(`prod_endpoint_${k.replace(/ /g, '_')}`, cell.entries)

// ---- M2 coverage by class ---------------------------------------------------
const EXEMPT_RULES = {} // no tree file exempts a class of merge from review today
function klass(p) {
  const t = String(p.title ?? '')
  const a = String(p.author ?? '')
  const pre = (/^([A-Za-z-]+)\s*[:(]/.exec(t) || [])[1]?.toLowerCase() ?? ''
  if ((a.endsWith('[bot]') && !/hpo-author/.test(a)) || /^ci:/i.test(t)) return 'bot cycle'
  if (/^(Merge|Absorb) /.test(t)) return 'untitled (merge subject)'
  if (['record', 'chore', 'docs', 'stamp', 'plan', 'handover', 'carry', 'claims', 'budget'].includes(pre) || /^(record|raise|disposition)\b/i.test(t) || /delivery row/i.test(t)) return 'record/chore'
  if (['fix', 'feat', 'feature', 'perf', 'refactor', 'test', 'tests'].includes(pre)) return 'fix/feature'
  return 'other lane'
}
const cov = new Map()
for (const { pr } of merges) {
  const p = snap.prs[pr]
  const k = klass(p)
  const a = String(p.author)
  if (!cov.has(k)) cov.set(k, { n: 0, none: 0, prs: [], authors: new Map() })
  const cell = cov.get(k)
  cell.n += 1
  if (!H.coverage.verdictPrs.has(pr)) { cell.none += 1; cell.prs.push(pr); cell.authors.set(a, (cell.authors.get(a) || 0) + 1) }
}
for (const [k, c] of [...cov].sort()) {
  const key = k.replace(/[ /]/g, '_')
  R(`m2_${key}_merges`, c.n)
  R(`m2_${key}_no_verdict`, c.none)
  console.log(`  m2 ${k}: ${c.none}/${c.n} no verdict; authors ${JSON.stringify(Object.fromEntries(c.authors))}; exempt by: ${EXEMPT_RULES[k] ?? '(no rule)'}; e.g. ${c.prs.slice(0, 12).map((x) => '#' + x).join(' ')}`)
}

// ---- M3 block classes -------------------------------------------------------
const taught = PL.blockClasses() ?? []
const BUCKET = {
  engineering: ['mutation-vacuous', 'harness', 'null-control', 'class-open', 'product-tradeoff-regression', 'preflight-mismatch'],
  'record-and-body': ['claims', 'version', 'carry-missing', 'root-cause-unanswered'],
  orchestration: ['head-moved', 'conflict'],
}
// An UNTAUGHT word keeps its own row (m3 class ... [UNTAUGHT]); for the BUCKET
// only, it is read by the taught class it restates (mine, stated):
const SYN = { 'red-check': 'root-cause-unanswered', 'carry-incomplete': 'carry-missing', 'readme-numbering': 'claims',
  vacuous: 'mutation-vacuous', mutation: 'mutation-vacuous', 'wrong-input': 'product-tradeoff-regression',
  measurement: 'harness', dirty: 'conflict', 'closures-unrepaired': 'conflict' }
const bucketOf0 = (w) => Object.entries(BUCKET).find(([, ws]) => ws.includes(w))?.[0] ?? (w === 'other' ? 'other' : taught.includes(w) ? 'unbucketed-taught' : 'untaught')
const bucketOf = (w) => bucketOf0(SYN[w] ?? w)
const re = PL.waveVerdictRe()
const byClass = new Map(), byBucket = new Map()
let blockedN = 0
for (const { pr } of merges) {
  const f = fetched.get(pr)
  if (!f) continue
  for (const c of walk(f)) {
    const first = String(c.body ?? '').trim().split('\n')[0]
    const m = re.exec(first)
    if (!m || !m[3]) continue
    blockedN += 1
    const w = m[5] ? m[5].toLowerCase() : 'other'
    const cls = m[5] ? w : 'other (bare)'
    byClass.set(cls, [...(byClass.get(cls) ?? []), pr])
    const b = bucketOf(w)
    byBucket.set(b, (byBucket.get(b) ?? 0) + 1)
  }
}
R('m3_blocked_verdicts', blockedN)
for (const [k, v] of [...byClass].sort((a, b) => b[1].length - a[1].length)) console.log(`  m3 class ${k}${taught.includes(k) || k.startsWith('other') ? '' : ' [UNTAUGHT]'}: ${v.length} (${v.map((x) => '#' + x).join(' ')})`)
for (const [k, v] of [...byBucket].sort()) R(`m3_bucket_${k}`, v)
const bodyAnswer = (byClass.get('root-cause-unanswered')?.length ?? 0) + (byClass.get('red-check')?.length ?? 0)
const engClasses = [...byClass].filter(([k]) => bucketOf(k.replace(' (bare)', '')) === 'engineering').map(([, v]) => v.length)
R('m3_body_answer_blocks', bodyAnswer)
R('m3_max_engineering_class', Math.max(0, ...engClasses))

// ---- M1b re-verification rounds ---------------------------------------------
import { execFileSync as X } from 'node:child_process'
const gitL = (...a) => X('git', a, { encoding: 'utf8' }).split('\n').filter(Boolean)
const rv = { n: 0, blocked: 0, mainOnly: 0, botOnly: 0, content: 0, missing: 0 }
for (const { pr } of merges) {
  const f = fetched.get(pr)
  if (!f) continue
  let prev = null
  for (const c of walk(f)) {
    const m = VRE.exec(String(c.body ?? '').trim().split('\n')[0])
    if (!m) continue
    const cur = { pass: Boolean(m[1]), head: (m[2] ?? m[4]).toLowerCase() }
    if (prev && prev.pass && cur.head !== prev.head) {
      rv.n += 1
      if (!cur.pass) rv.blocked += 1
      let fp
      try { fp = gitL('log', '--first-parent', '--format=%P%x09%s', `${prev.head}..${cur.head}`) } catch { rv.missing += 1; prev = cur; continue }
      const own = fp.filter((l) => l.split('\t')[0].split(' ').length === 1 && !/^ci:/.test(l.split('\t')[1]))
      const mg = fp.filter((l) => l.split('\t')[0].split(' ').length > 1)
      if (own.length) rv.content += 1
      else if (mg.length) rv.mainOnly += 1
      else rv.botOnly += 1
    }
    prev = cur
  }
}
R('reverify_rounds', rv.n)
R('reverify_blocked', rv.blocked)
R('reverify_moved_by_merges_only', rv.mainOnly)
R('reverify_moved_by_ci_bot_only', rv.botOnly)
R('reverify_moved_by_branch_content', rv.content)
R('reverify_heads_missing_locally', rv.missing)
R('prod_reverify_entries', H.rounds.reverify.entries)
R('prod_repair_entries', H.rounds.repair.entries)
R('prod_repeat_entries', H.rounds.repeat.entries)
R('api_failures', apiFailures)
R('load1', (await import('node:os')).loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('baseline_sha', '1936d5ca72a06556eeed4e8e5bf3dea520e517e1')
