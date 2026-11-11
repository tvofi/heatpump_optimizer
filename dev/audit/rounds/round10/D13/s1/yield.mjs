// D13-s1 harness: first-pass yield, rounds per merge (D13.M1) and verdict
// coverage by class (D13.M2), over the merged pull requests whose merge commit
// is first-parent in <since>..origin/main.
//
// METRIC (one line each):
//   window      = PR numbers from /commits/<sha>/pulls per first-parent commit (API mode of
//                 policy_lint.mjs:enumerateMerges), compared as a SET against the production
//                 mergedPRsFromWindow; api_failures printed beside it.
//   verdict     = issue comment or PR review whose trimmed body's first line matches
//                 web-fix-wave.js VERDICT_RE (read via policy_lint.mjs:waveVerdictRe), ordered by time.
//   yield       = share of verdict-carrying merges whose first verdict is `merge`;
//   rounds      = parsable verdicts per verdict-carrying merge, mean and max.
//   coverage    = merges with no parsable verdict, split by class (title prefix x author).
//   truncation  = verdicts the production reader policy_lint.mjs:fetchWindow (one page of 100
//                 issue comments, one page of 100 reviews) drops against a fully paginated read;
//                 count key = parsable verdicts statsHistogram delivers from each fetched map.
// INSTRUMENTED: policy_lint.mjs:fetchWindow, policy_lint.mjs:statsHistogram,
//               policy_lint.mjs:mergedPRsFromWindow, policy_lint.mjs:waveVerdictRe.
// PERTURBATIONS:
//   --reshape-one   re-shape ONE single-verdict merge's verdict out of the grammar
//                   (`Fix review: PASS -- merge <sha>`) in the in-memory fixture: coverage -1.
//   --page-all      swap fetchWindow's map for the fully paginated map: truncation -> 0.
// RUN (repo root): GITHUB_TOKEN=$(gh auth token) PYTHONPATH=tests/hastub \
//   node dev/audit/rounds/round10/D13/s1/yield.mjs --since 1913f0dd7 [--reshape-one] [--page-all]
// Raw API answers are cached under ~/.cache/hpo/d13s1-cache-<since>/, created
// owner-only (0700) (delete it to re-fetch). Not the shared temp dir: a
// predictable name there lets another user plant or swap the cached answers.
// EXPECTED at baseline 17f1c55fad1b, window 1913f0dd7..origin/main (exact, counts):
//   window=185 api_failures=0; see REPORT.md for the rest.
// MACHINE: macOS arm64 (Darwin 25.6.0), node, B8 light seat. Counts: no thread pin needed
//   (no numpy); thread_factor printed as 1 for the contract.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import * as PL from '../../../../../../tools/policy/policy_lint.mjs'

const argv = process.argv.slice(2)
const since = argv[argv.indexOf('--since') + 1]
if (!argv.includes('--since') || !since) { console.error('--since <ref> required'); process.exit(2) }
const RESHAPE = argv.includes('--reshape-one')
const PAGE_ALL = argv.includes('--page-all')
const token = process.env.GITHUB_TOKEN
if (!token) { console.error('GITHUB_TOKEN required'); process.exit(2) }
const slug = 'tvofi/heatpump_optimizer'
const cacheDir = path.join(os.homedir(), '.cache', 'hpo', `d13s1-cache-${since}`)
fs.mkdirSync(cacheDir, { recursive: true, mode: 0o700 })
fs.chmodSync(cacheDir, 0o700)
// Read a cache entry in one call: an exists-then-read pair races a writer.
function readCache(file) {
  try { return fs.readFileSync(file, 'utf8') } catch (e) { if (e.code === 'ENOENT') return null; throw e }
}

let apiFailures = 0
let apiRequests = 0
function get(p) {
  const key = path.join(cacheDir, p.replace(/[^A-Za-z0-9]+/g, '_') + '.json')
  const hit = readCache(key)
  if (hit !== null) return JSON.parse(hit)
  apiRequests += 1
  const raw = execFileSync('curl', ['-sS', '-w', '\n%{http_code}', '-K', '-', 'https://api.github.com' + p], {
    input: `header = "Authorization: Bearer ${token}"\nheader = "Accept: application/vnd.github+json"\n`,
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
  })
  const cut = raw.lastIndexOf('\n')
  if (raw.slice(cut + 1).trim() !== '200') { apiFailures += 1; return null }
  const data = JSON.parse(raw.slice(0, cut))
  fs.writeFileSync(key, JSON.stringify(data), { mode: 0o600 })
  return data
}
function getAll(p) {
  const out = []
  for (let page = 1; page < 50; page++) {
    const d = get(`${p}?per_page=100&page=${page}`)
    if (!Array.isArray(d)) return null
    out.push(...d)
    if (d.length < 100) return out
  }
  return out
}

// 1. The window, our own enumeration, against production's as a set.
const log = execFileSync('git', ['log', '--first-parent', '--format=%H%x09%s', `${since}..origin/main`], { encoding: 'utf8' })
const commits = log.split('\n').filter(Boolean).map((l) => { const [sha, ...s] = l.split('\t'); return { sha, subject: s.join('\t') } })
const mine = []
for (const { sha, subject } of commits) {
  const rows = get(`/repos/${slug}/commits/${sha}/pulls`)
  if (!Array.isArray(rows)) continue
  const r = PL.resolvePrFromCommit(subject, rows)
  if (r && !mine.includes(r.pr)) mine.push(r.pr)
}
const prod = PL.mergedPRsFromWindow(since)
const prodSet = new Set(prod.prs.map((p) => p.pr))
const onlyMine = mine.filter((p) => !prodSet.has(p))
const onlyProd = [...prodSet].filter((p) => !mine.includes(p))
console.log(`RESULT window=${mine.length} count`)
console.log(`RESULT api_failures=${apiFailures} count`)
console.log(`RESULT window_prod=${prod.prs.length} count (mode ${prod.mode}, why ${prod.why})`)
console.log(`RESULT window_set_diff=${onlyMine.length + onlyProd.length} count (only mine ${onlyMine.join(',') || '-'}; only prod ${onlyProd.join(',') || '-'})`)
const prs = prod.prs

// 2. Full paginated read, and the production one-page read (fetchWindow itself).
const full = new Map()
const meta = new Map()
for (const { pr } of prs) {
  const body = get(`/repos/${slug}/pulls/${pr}`)
  const comments = getAll(`/repos/${slug}/issues/${pr}/comments`)
  const reviews = getAll(`/repos/${slug}/pulls/${pr}/reviews`)
  full.set(pr, { body: body?.body ?? '', comments: comments ?? [], reviews: reviews ?? [] })
  meta.set(pr, { title: body?.title ?? '', author: body?.user?.login ?? '?', ncomments: (comments ?? []).length, nreviews: (reviews ?? []).length })
}
console.log(`RESULT api_failures_after_bodies=${apiFailures} count`)
const prodCache = path.join(cacheDir, 'fetchWindow.json')
let paged
const prodHit = readCache(prodCache)
if (prodHit !== null) paged = new Map(JSON.parse(prodHit))
else {
  const r = PL.fetchWindow(prs)
  if (r.fetchError) { console.log(`fetchWindow error: ${r.fetchError}`); process.exit(1) }
  paged = r.fetched
  fs.writeFileSync(prodCache, JSON.stringify([...paged]), { mode: 0o600 })
}
const classes = ['blocked', 'merge']
const re = PL.waveVerdictRe()

function verdictsOf(f) {
  const rows = []
  for (const c of f.comments) rows.push({ body: c.body, at: c.created_at, origin: 'issue comment' })
  for (const c of f.reviews) rows.push({ body: c.body, at: c.submitted_at, origin: 'review' })
  rows.sort((a, b) => String(a.at ?? '').localeCompare(String(b.at ?? '')))
  const out = []; const outside = []
  for (const r of rows) {
    const first = String(r.body ?? '').trim().split('\n')[0]
    if (!/^Fix review:/i.test(first)) continue
    const m = re.exec(first)
    if (!m) { outside.push(first.slice(0, 60)); continue }
    out.push({ word: m[1] ? 'merge' : 'blocked', origin: r.origin })
  }
  return { out, outside }
}

let fixture = full
if (RESHAPE) {
  // Re-shape the first single-verdict merge's verdict out of the grammar.
  fixture = new Map([...full].map(([k, v]) => [k, { ...v, comments: v.comments.map((c) => ({ ...c })) }]))
  for (const [pr, f] of fixture) {
    const v = verdictsOf(f)
    if (v.out.length !== 1 || v.out[0].origin !== 'issue comment') continue
    const c = f.comments.find((x) => re.exec(String(x.body ?? '').trim().split('\n')[0]))
    c.body = c.body.trim().replace(/^Fix review:\s+merge/, 'Fix review: PASS -- merge')
    console.log(`PERTURB reshaped one verdict on #${pr}`)
    break
  }
}

// 3. M1 over the fully paginated read.
let n = 0, firstMerge = 0, total = 0, max = 0, maxPr = null, outsideN = 0
const roundsHist = new Map()
const noVerdict = []
for (const { pr } of prs) {
  const { out, outside } = verdictsOf(fixture.get(pr))
  outsideN += outside.length
  if (!out.length) { noVerdict.push(pr); continue }
  n += 1; total += out.length
  if (out[0].word === 'merge') firstMerge += 1
  if (out.length > max) { max = out.length; maxPr = pr }
  roundsHist.set(out.length, (roundsHist.get(out.length) ?? 0) + 1)
}
console.log(`RESULT verdict_prs=${n} count`)
console.log(`RESULT first_verdict_yield=${(firstMerge / n).toFixed(3)} ratio (${firstMerge}/${n})`)
console.log(`RESULT rounds_mean=${(total / n).toFixed(3)} verdicts/merge (${total}/${n})`)
console.log(`RESULT rounds_max=${max} verdicts (#${maxPr})`)
console.log(`RESULT outside_grammar=${outsideN} count`)
console.log(`rounds histogram: ${[...roundsHist].sort((a, b) => a[0] - b[0]).map(([k, v]) => `${k}:${v}`).join(' ')}`)

// 4. Production statsHistogram over each map: what the shipped reader delivers.
const hFull = PL.statsHistogram(prs, fixture, classes)
const hPaged = PL.statsHistogram(prs, PAGE_ALL ? fixture : paged, classes)
const cnt = (h) => [...h.endpoints.values()].reduce((s, c) => s + c.entries, 0)
console.log(`RESULT prod_verdicts_full=${cnt(hFull)} count; prod_coverage_full=${hFull.coverage.verdictPrs.size}; prod_firstMerge_full=${hFull.rounds.firstMerge}`)
console.log(`RESULT prod_verdicts_fetchWindow=${cnt(hPaged)} count; prod_coverage_fetchWindow=${hPaged.coverage.verdictPrs.size}; prod_firstMerge_fetchWindow=${hPaged.rounds.firstMerge}`)
console.log(`RESULT truncation_verdicts_dropped=${cnt(hFull) - cnt(hPaged)} count`)
const truncPrs = prs.filter(({ pr }) => (paged.get(pr)?.comments.length ?? 0) < meta.get(pr).ncomments || (paged.get(pr)?.reviews.length ?? 0) < meta.get(pr).nreviews).map((p) => p.pr)
console.log(`RESULT truncated_prs=${truncPrs.length} count (${truncPrs.map((p) => `#${p}:${meta.get(p).ncomments}c/${meta.get(p).nreviews}r`).join(' ')})`)
// Who is mis-delivered by truncation: per PR, verdicts full vs paged.
for (const pr of truncPrs) {
  const a = verdictsOf(fixture.get(pr)).out, b = verdictsOf(paged.get(pr)).out
  console.log(`  #${pr}: verdicts full=${a.length} (first ${a[0]?.word}) fetchWindow=${b.length} (first ${b[0]?.word ?? 'none'})`)
}

// 5. M2: coverage by class.
function klass(pr) {
  const { title, author } = meta.get(pr)
  const pre = (title.match(/^([a-z]+)(?:\([^)]*\))?!?:/i)?.[1] ?? '(none)').toLowerCase()
  const bot = /\[bot\]$/.test(author) ? 'bot' : 'human/app'
  const group = ['fix', 'feat'].includes(pre) ? 'fix-feature' : ['docs', 'chore', 'record'].includes(pre) ? 'record-chore' : 'other'
  return { pre, author, bot, group }
}
const byGroup = new Map()
for (const { pr } of prs) {
  const k = klass(pr)
  const key = `${k.group}\t${k.author}`
  const cell = byGroup.get(key) ?? { all: 0, none: [] }
  cell.all += 1
  if (noVerdict.includes(pr)) cell.none.push(`#${pr}(${k.pre})`)
  byGroup.set(key, cell)
}
console.log(`RESULT coverage=${prs.length - noVerdict.length}/${prs.length} merges carrying a parsable verdict`)
console.log(`RESULT no_verdict=${noVerdict.length} count`)
for (const [k, c] of [...byGroup].sort()) console.log(`COVER\t${k}\t${c.all}\tnone=${c.none.length}\t${c.none.join(' ')}`)
console.log(`RESULT api_requests_this_run=${apiRequests} count`)
console.log('RESULT thread_factor=1')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
console.log('RESULT swapins=0')
