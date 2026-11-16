// D13-s1, round 11 -- D13.M1 (first-pass yield, rounds per merge) and D13.M2 (verdict coverage by class).
//
// METRIC (M1): over the merged PRs whose merge commit is first-parent in <since>..<base> (enumerated
//   from /commits/<sha>/pulls through policy_lint.mjs:enumerateMerges + resolvePrFromCommit), a verdict
//   is an issue comment or PR review whose trimmed first line parses under web-fix-wave.js's VERDICT_RE,
//   as policy_lint.mjs:statsHistogram walks them (both endpoints, time-ordered). Yield = share of
//   verdict-carrying PRs whose first verdict is `merge`; rounds = parsable verdicts per verdict-carrying
//   PR (mean, max). Every count is the production statsHistogram's, driven per window and per PR.
// METRIC (M2): merged PRs carrying no parsable verdict, by (title type as policy_lint.mjs:prClass reads
//   it, PR author), each row with the in-tree rule that exempts it or "none".
// COUNT KEYS: a verdict is keyed by (PR, verdict word, 40-hex head). A relay duplicate is a second
//   comment carrying the same `bus-nonce:` line as an earlier one on the same PR. A bus verdict is a
//   commit with subject `verdict: #<pr> Fix review: ...` reachable from origin's review/<pr>,
//   verdict/<pr>, archive/review/<pr> or archive/verdict/<pr> refs and not from <base> (the population
//   tools/audit/seat/review_strength.py reads); it is "bus-only" when no comment/review verdict on that PR
//   names the same (word, head).
//
// RUN (from the export root):
//   PYTHONPATH=tests/hastub node dev/audit/rounds/round11/D13/s1/yield_rounds.mjs \
//       [--since v7.1.10] [--base 92d38ecb640bd462f2e19c0814d0f0b7df1ee692] [--perturb <name>]
//   needs GITHUB_TOKEN (or the session proxy) for api.github.com and `git ls-remote origin`; the window
//   read is cached under os.tmpdir() (window_fetch.mjs; $D13S1_CACHE overrides; delete to re-fetch).
// PERTURBATIONS (in memory, never on a live PR):
//   --perturb reshape    one verdict comment re-shaped out of the grammar (`Fix review: PASS -- merge`)
//                        on the lowest-numbered PR carrying exactly one verdict: verdict_prs -1, M2's
//                        no-verdict count +1 in that PR's class (the brief's M2 perturbation).
//   --perturb dedup      drop a comment whose bus-nonce repeats an earlier one on its PR (one relayed
//                        verdict read once): instrument_repeat_rounds 9 -> 0, comment_verdicts 420 -> 411.
//   --perturb dedup,bus-union  both (the bus population read once): verdicts 453 over 208 PRs.
//   --perturb bus-union  feed statsHistogram the bus-only verdicts as comments at their author time:
//                        verdict_prs 206 -> 208, verdicts 420 -> 462, one_round_yield down.
// EXPECTED at baseline 92d38ecb, window v7.1.10..92d38ecb (exact; counts, no timing):
//   merges=234 api_failures=0 comment_verdicts=420 verdict_prs=206 first_verdict_yield=0.583
//   one_round_yield=0.476 rounds_mean=2.039 rounds_max=10 relay_duplicates=9 bus_only_verdicts=42
// MACHINE: box B8 (Linux, node v22.23.4), baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
// THREAD PIN: a Node harness, no BLAS; the env pin below is copied for the contract, and thread_factor
//   is printed as process CPU over the main thread's CPU (Node runs this on one JS thread).
for (const k of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) process.env[k] ??= '1'

import fs from 'node:fs'
import os from 'node:os'
import { execFileSync } from 'node:child_process'
import { statsHistogram, statsRoundsLine, statsCoverageClassLine } from '../../../../../../tools/policy/policy_lint.mjs'
import { loadWindow, git } from './window_fetch.mjs'

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d }
const SINCE = arg('--since', 'v7.1.10')
const BASE = arg('--base', '92d38ecb640bd462f2e19c0814d0f0b7df1ee692')
const PERTURB = new Set((arg('--perturb', '') || '').split(',').filter(Boolean))
const R = (k, v, u = 'count') => console.log(`RESULT ${k}=${v} ${u}`)
const cpu0 = process.cpuUsage()

const w = loadWindow(SINCE, BASE)
console.log(`window ${SINCE}..${w.base} cache ${w.cacheFile} (${w.fromCache ? 'read from cache' : 'fetched'}, ${w.fetched_at})`)
const prs = w.prs
// The enumerator of both steps' universe: one merged PR per line (`--list`), then exit.
if (process.argv.includes('--list')) { for (const { pr } of prs) console.log(`#${pr}`); process.exit(0) }
const fetched = new Map(Object.entries(w.fetched).map(([k, v]) => [k, structuredClone(v)]))

// ---- the verdict bus: review_strength.py's population -------------------------------------------
function busVerdicts() {
  const want = new Set(prs.map((p) => p.pr))
  const ls = execFileSync('git', ['ls-remote', 'origin', 'refs/heads/review/*', 'refs/heads/verdict/*', 'refs/tags/archive/review/*', 'refs/tags/archive/verdict/*'], { encoding: 'utf8', maxBuffer: 64 << 20 })
  const tips = []
  for (const line of ls.split('\n')) {
    const [sha, ref] = line.split('\t')
    const m = /\/(?:review|verdict)\/(\d+)$/.exec(ref ?? '')
    if (m && want.has(m[1])) tips.push(sha)
  }
  const missing = tips.filter((s) => { try { git(['cat-file', '-e', `${s}^{commit}`]); return false } catch { return true } })
  for (let i = 0; i < missing.length; i += 100) {
    try { execFileSync('git', ['fetch', '-q', '--no-tags', '--no-write-fetch-head', 'origin', ...missing.slice(i, i + 100)]) } catch { /* counted below */ }
  }
  const log = tips.length ? execFileSync('git', ['log', '--format=%x1e%aI%x1f%s', ...tips, '--not', w.base], { encoding: 'utf8', maxBuffer: 64 << 20 }) : ''
  const bus = new Map()
  for (const rec of log.split('\x1e')) {
    const [at, subj] = rec.trim().split('\x1f')
    const m = /^verdict: #(\d+) (Fix review: (merge|blocked) ([0-9a-f]{40}).*)$/.exec(subj ?? '')
    if (!m || !want.has(m[1])) continue
    const key = `${m[1]}|${m[3]}|${m[4]}`
    const prev = bus.get(key)
    if (!prev || prev.at > at) bus.set(key, { pr: m[1], word: m[3], head: m[4], line: m[2], at: new Date(at).toISOString() })
  }
  return { bus: [...bus.values()], tips: tips.length, unfetched: missing.length && tips.filter((s) => { try { git(['cat-file', '-e', `${s}^{commit}`]); return false } catch { return true } }).length }
}

const HEAD_RE = /^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})/
const NONCE_RE = /^bus-nonce:\s*([0-9a-f]+)/m
function commentKeys(f) {
  const s = new Set()
  for (const c of [...f.comments, ...f.reviews]) { const m = HEAD_RE.exec(String(c.body ?? '').trim()); if (m) s.add(`${m[1]}|${m[2]}`) }
  return s
}

// ---- perturbations ---------------------------------------------------------------------------
let reshaped = null
if (PERTURB.has('reshape')) {
  for (const { pr } of [...prs].sort((a, b) => Number(a.pr) - Number(b.pr))) {
    const f = fetched.get(pr)
    const vs = f.comments.filter((c) => HEAD_RE.test(String(c.body).trim()))
    if (vs.length === 1) { vs[0].body = String(vs[0].body).trim().replace(/^Fix review:\s+merge/, 'Fix review: PASS -- merge'); if (vs[0].body.includes('PASS')) { reshaped = pr; break } }
  }
  console.log(`perturb reshape: #${reshaped}'s only verdict re-shaped out of the grammar`)
}
if (PERTURB.has('dedup')) {
  let dropped = 0
  for (const f of fetched.values()) {
    const seen = new Set()
    f.comments = [...f.comments].sort((a, b) => String(a.created_at).localeCompare(String(b.created_at))).filter((c) => {
      const n = HEAD_RE.test(String(c.body).trim()) ? NONCE_RE.exec(String(c.body))?.[1] : null
      if (!n) return true
      if (seen.has(n)) { dropped++; return false }
      seen.add(n); return true
    })
  }
  console.log(`perturb dedup: ${dropped} relay duplicate comment(s) dropped`)
}
const B = busVerdicts()
if (PERTURB.has('bus-union')) {
  let added = 0
  for (const v of B.bus) {
    const f = fetched.get(v.pr)
    if (commentKeys(f).has(`${v.word}|${v.head}`)) continue
    f.comments.push({ body: v.line, created_at: v.at, user: '(bus)' }); added++
  }
  console.log(`perturb bus-union: ${added} bus-only verdict(s) fed to statsHistogram as comments`)
}

// ---- M1 through the production walk -----------------------------------------------------------
const words = ['blocked', 'merge']
const h = statsHistogram(prs, fetched, words)
const total = [...h.verdicts.values()].reduce((a, c) => a + c.entries, 0)
const perPr = prs.map(({ pr }) => [pr, [...statsHistogram([{ pr }], fetched, words).verdicts.values()].reduce((a, c) => a + c.entries, 0)]).filter(([, n]) => n > 0)
const n = h.coverage.verdictPrs.size
console.log(statsRoundsLine(h))
R('window_first_parent_commits', w.commits.length)
R('merges', prs.length)
R('api_failures', w.stats.api_failures.length)
R('gap_recovered_from_subject', w.stats.gap.length)
R('comment_verdicts', total)
R('review_endpoint_verdicts', h.endpoints.get('review')?.entries ?? 0)
R('outside_grammar', h.unclassified.length)
R('verdict_prs', n)
R('first_verdict_yield', (h.rounds.firstMerge / n).toFixed(3), 'ratio')
R('one_round_yield', (h.rounds.oneRound / n).toFixed(3), 'ratio')
R('rounds_mean', (total / n).toFixed(3), 'verdicts/merge')
R('rounds_max', Math.max(...perPr.map(([, k]) => k)), `verdicts (#${perPr.sort((a, b) => b[1] - a[1])[0][0]})`)
R('instrument_repeat_rounds', h.rounds.repeat.entries)
R('instrument_reverify_rounds', h.rounds.reverify.entries)
R('instrument_repair_rounds', h.rounds.repair.entries)

// relay duplicates: a later comment repeating an earlier comment's bus-nonce on the same PR
let dups = 0; const dupPrs = new Set()
for (const [pr, f] of fetched) {
  const seen = new Set()
  for (const c of [...f.comments].sort((a, b) => String(a.created_at).localeCompare(String(b.created_at)))) {
    if (!HEAD_RE.test(String(c.body).trim())) continue
    const nn = NONCE_RE.exec(String(c.body))?.[1]
    if (nn && seen.has(nn)) { dups++; dupPrs.add(pr) }
    if (nn) seen.add(nn)
  }
}
R('relay_duplicates', dups)
R('relay_duplicate_prs', dupPrs.size)

// bus-only verdicts
const busOnly = B.bus.filter((v) => !commentKeys(fetched.get(v.pr)).has(`${v.word}|${v.head}`))
R('bus_tips_read', B.tips)
R('bus_tips_unfetched', B.unfetched || 0)
R('bus_verdicts', B.bus.length)
R('bus_only_verdicts', busOnly.length)
R('bus_only_blocked', busOnly.filter((v) => v.word === 'blocked').length)
R('bus_only_prs', new Set(busOnly.map((v) => v.pr)).size)
const noComment = busOnly.filter((v) => !h.coverage.verdictPrs.has(v.pr)).map((v) => v.pr)
R('bus_verdict_prs_read_as_no_verdict', new Set(noComment).size, `(${[...new Set(noComment)].map((p) => '#' + p).join(' ') || 'none'})`)
for (const v of busOnly) console.log(`  bus-only #${v.pr} ${v.word} ${v.head.slice(0, 9)} ${v.at} ${v.line.slice(0, 80)}`)
// Each bus-only head is a real head of its PR: an ancestor of the merge commit's second parent.
let realHead = 0
for (const v of busOnly) {
  const mc = w.fetched[v.pr].merge_commit_sha
  try { execFileSync('git', ['merge-base', '--is-ancestor', v.head, `${mc}^2`]); realHead++ } catch {}
}
R('bus_only_heads_on_merged_branch', realHead)
// The null control for bus-union: the PRs carrying no bus-only verdict keep their verdict count.
const busOnlyPrs = new Set(busOnly.map((v) => v.pr))
R('prs_without_bus_only_verdicts', prs.filter(({ pr }) => !busOnlyPrs.has(pr)).length)
// fetchWindow reads ONE page of 100 per endpoint: the largest page a window PR needs.
R('max_comments_on_one_pr', Math.max(...prs.map(({ pr }) => w.fetched[pr].comments.length)))
R('max_reviews_on_one_pr', Math.max(...prs.map(({ pr }) => w.fetched[pr].reviews.length)))

// ---- M2: coverage by (title type, author), each with its exemption rule ----------------------------
const prClass = (f) => (f ? /^([a-z]+)(?:\([^)]*\))?!?:/i.exec(String(f.title ?? ''))?.[1].toLowerCase() ?? '(untyped)' : '(unfetched)')
const EXEMPT = {
  'record|hpo-author[bot]': '.github/workflows/nightly.yml record-autofix: "A record pull request the guard passes merges with no review seat" (tvofi, 2026-10-07)',
  'build|dependabot[bot]': '.github/workflows/dependabot-automerge.yml: a patch/minor bump is approved by the App and `gate` decides (tvofi, 2026-10-24)',
}
const cls = new Map()
for (const { pr } of prs) {
  const f = fetched.get(pr)
  const k = `${prClass(f)}|${f?.author ?? '?'}`
  if (!cls.has(k)) cls.set(k, { window: 0, none: [] })
  cls.get(k).window++
  if (!h.coverage.verdictPrs.has(pr)) cls.get(k).none.push(pr)
}
console.log(statsCoverageClassLine(h.coverage))
let unexempt = 0
for (const [k, c] of [...cls].sort((a, b) => b[1].none.length - a[1].none.length || a[0].localeCompare(b[0]))) {
  const rule = EXEMPT[k] ?? 'none'
  if (rule === 'none') unexempt += c.none.length
  console.log(`  M2 ${k.padEnd(32)} no-verdict ${c.none.length} of ${c.window}  rule: ${rule}${c.none.length ? `  [${c.none.map((p) => '#' + p).join(' ')}]` : ''}`)
}
R('no_verdict_prs', h.coverage.noVerdict.length)
R('no_verdict_unexempt', unexempt)

// ---- contract tail ----
const cpu = process.cpuUsage(cpu0)
const pcpu = (cpu.user + cpu.system) / 1e6
R('thread_factor', '1.00', `ratio (process_cpu ${pcpu.toFixed(2)} s on one JS thread; no BLAS)`)
R('load1', os.loadavg()[0].toFixed(2), 'load')
let swap = 'n/a'
try { swap = /pswpin (\d+)/.exec(fs.readFileSync('/proc/vmstat', 'utf8'))[1] } catch {}
R('swapins', swap)
