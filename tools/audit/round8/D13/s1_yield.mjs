#!/usr/bin/env node
// D13 / round 8 / seat s1 -- required outputs 1, 2, 3 and 6 of the D13 brief.
//
// METRICS (one line each):
//   first_pass_yield   share of window merges carrying >=1 verdict whose FIRST verdict (by time,
//                      both endpoints) is `merge`; a verdict is a first line matching
//                      ^Fix review:\s*(merge|blocked) (the brief's population regex).
//   rounds_mean/max    verdicts per merge over merges carrying >=1 verdict.
//   no_verdict         window merges with no `Fix review:` first line on either endpoint, split
//                      by class (title prefix and author, CLASS_RULES below).
//   blocked_by_class   every blocked verdict keyed by web-fix-wave.js's own parseVerdict route
//                      (VERDICT_RE + VERDICT_CLASSES, evaluated from that file's source), then by
//                      BUCKETS below; a class word outside VERDICT_CLASSES is its own row.
//   friction_keys      each `## Friction` entry's rule id (policy_lint.mjs:frictionEntries), `#`
//                      anchor dropped, resolved under the D13 brief's rule against the `--budgets`
//                      path list: one path = that file, several = `ambiguous`, none = `unresolved`.
//                      Compared entry-for-entry with production's key (statsHistogram's friction map).
//   The count key is the value production delivers: the verdict first line as the wave's
//   parseVerdict extracts it (trim, then first line), and the friction id as frictionEntries parses it.
//
// PRODUCTION SYMBOLS DRIVEN: .claude/workflows/web-fix-wave.js:VERDICT_RE / VERDICT_CLASSES /
//   parseVerdict (evaluated from the file's source); .claude/workflows/policy_lint.mjs:statsHistogram,
//   waveVerdictRe, blockClasses, frictionEntries (imported).
//
// COMMAND (tree root; needs the window JSON from s1_window.py):
//   HPO_PLANDATA=/home/claude/audit-r8/tmp/D13-s1/plandata TMPDIR=/home/claude/audit-r8/tmp/D13-s1 \
//   node tools/audit/round8/D13/s1_yield.mjs [--window <json>] [--reshape <pr>] [--respell '<pr>|<from>|<to>'] [--unbacktick <pr>:<id>]
//
// PERTURBATIONS (fixture-side, never live): --reshape <pr> rewrites that PR's every verdict first line
//   out of the grammar (`Fix review:` -> `Fix-review:`); verdict_prs falls by exactly 1 and no_verdict
//   rises by 1. --respell '1358|- ratchet-budgets.md:|- README.md:' re-spells one entry: its file row falls by
//   one, `ambiguous` rises by one. Production-side: delete a word from VERDICT_CLASSES in
//   web-fix-wave.js and that class's blocked rows move to `other`.
//
// EXPECTED at baseline cdf82da, window c310541..cdf82da: see REPORT-s1.md (exact; closed window).
// MACHINE: any; counts only, no timing claim, so no load1/thread_factor applies.
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..')
const PL = await import(path.join(ROOT, '.claude/workflows/policy_lint.mjs'))

const argv = process.argv.slice(2)
const opt = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null }
const WINDOW = opt('--window') ?? path.join(process.env.D13S1_TMP ?? '/home/claude/audit-r8/tmp/D13-s1', 'window.json')
const win = JSON.parse(fs.readFileSync(WINDOW, 'utf8'))
const R = (k, v, u = '') => console.log(`RESULT ${k}=${typeof v === 'object' ? JSON.stringify(v) : v}${u ? ' ' + u : ''}`)

// ---- the wave's own parseVerdict, from its source (check-wave-script.mjs's technique) -------------
const waveText = fs.readFileSync(path.join(ROOT, '.claude/workflows/web-fix-wave.js'), 'utf8')
const reKey = 'const VERDICT_RE = '
const clsKey = 'const VERDICT_CLASSES = '
const reStart = waveText.indexOf(reKey) + reKey.length
const reEnd = waveText.indexOf('\n)\n', reStart) + 2
const clsStart = waveText.indexOf(clsKey) + clsKey.length
const clsEnd = waveText.indexOf('\n]\n', clsStart) + 2
// eslint-disable-next-line no-eval
const VERDICT_CLASSES = eval(waveText.slice(clsStart, clsEnd))
// eslint-disable-next-line no-eval
const VERDICT_RE = eval(waveText.slice(reStart, reEnd))
const fnStart = waveText.indexOf('function parseVerdict(')
const fnEnd = waveText.indexOf('\n}\n', fnStart) + 2
const parseVerdict = new Function('VERDICT_RE', 'VERDICT_CLASSES', waveText.slice(fnStart, fnEnd) + '\nreturn parseVerdict')(VERDICT_RE, VERDICT_CLASSES)

// ---- perturbations (in memory, on the fixture) ---------------------------------------------------
const prs = win.prs
const reshape = opt('--reshape')
if (reshape) {
  for (const p of prs.filter((x) => String(x.pr) === reshape)) {
    for (const c of [...p.comments, ...p.reviews]) {
      if (c.body && /^Fix review:/.test(String(c.body).trim())) c.body = String(c.body).trim().replace(/^Fix review:/, 'Fix-review:')
    }
  }
}
const respell = opt('--respell')
if (respell) {
  const [n, from, to] = respell.split('|')
  const p = prs.find((x) => String(x.pr) === n)
  const i = p.body.indexOf(from)
  if (i < 0) throw new Error(`--respell: ${from} not in #${n}'s body`)
  p.body = p.body.slice(0, i) + to + p.body.slice(i + from.length)
}
const pinHead = opt('--pin-head')
if (pinHead) { // rewrite every verdict SHA of that PR to its first verdict's SHA: no head moved
  const p = prs.find((x) => String(x.pr) === pinHead)
  const vs = p.comments.filter((c) => /^Fix review:/.test(String(c.body ?? '').trim())).sort((a, b) => a.created_at.localeCompare(b.created_at))
  const h0 = /[0-9a-f]{40}/.exec(vs[0].body)[0]
  for (const c of vs) c.body = String(c.body).replace(/[0-9a-f]{40}/, h0)
}
const unbacktick = opt('--unbacktick')
if (unbacktick) {
  const [n, id] = unbacktick.split(':')
  const p = prs.find((x) => String(x.pr) === n)
  if (!p.body.includes('`' + id + '`')) throw new Error(`--unbacktick: \`${id}\` not in #${n}'s body`)
  p.body = p.body.replace('`' + id + '`', id)
}

// ---- 1. verdict walk -----------------------------------------------------------------------------
const POP_RE = /^Fix review:\s*(merge|blocked)/
const walk = (p) => [
  ...p.comments.map((c) => ({ body: c.body, at: c.created_at, origin: 'issue comment', user: c.user })),
  ...p.reviews.map((c) => ({ body: c.body, at: c.submitted_at, origin: 'review', user: c.user })),
].sort((a, b) => String(a.at ?? '').localeCompare(String(b.at ?? '')))

const perPr = []
const outsideGrammar = []
const fixReviewOther = []
const endpoint = { 'issue comment': 0, review: 0 }
for (const p of prs) {
  const vs = []
  for (const row of walk(p)) {
    const first = String(row.body ?? '').trim().split('\n')[0]
    if (!/^Fix review:/.test(first)) continue
    if (!POP_RE.test(first)) { fixReviewOther.push(`#${p.pr} (${row.origin}): ${first.slice(0, 80)}`); continue }
    const word = POP_RE.exec(first)[1]
    let parsed = null
    try { parsed = parseVerdict({ comment: first }) } catch { outsideGrammar.push(`#${p.pr} (${row.origin}): ${first.slice(0, 90)}`) }
    const m = VERDICT_RE.exec(first)
    vs.push({ word, parsed, raw_class: m && m[5] ? m[5] : null, origin: row.origin, at: row.at, first })
    endpoint[row.origin] += 1
  }
  perPr.push({ p, vs })
}
const withV = perPr.filter((x) => x.vs.length)
const firstMerge = withV.filter((x) => x.vs[0].word === 'merge')
const rounds = withV.map((x) => x.vs.length)
console.log(`window ${win.since}..${String(win.head).slice(0, 10)}: ${prs.length} merges (API mode, /commits/<sha>/pulls)`)
R('window_merges', prs.length)
R('verdict_prs', withV.length)
R('verdicts_total', rounds.reduce((a, b) => a + b, 0))
R('verdicts_by_endpoint', endpoint)
R('first_pass_yield', withV.length ? (firstMerge.length / withV.length).toFixed(3) : 'n/a')
R('first_pass_merges', firstMerge.length)
R('rounds_mean', withV.length ? (rounds.reduce((a, b) => a + b, 0) / withV.length).toFixed(2) : 'n/a', 'verdicts/merge')
R('rounds_max', Math.max(0, ...rounds))
R('rounds_hist', rounds.reduce((h, r) => ({ ...h, [r]: (h[r] ?? 0) + 1 }), {}))
R('verdicts_outside_grammar', outsideGrammar.length)
for (const l of outsideGrammar) console.log('  outside VERDICT_RE:', l)
R('fix_review_lines_not_merge_or_blocked', fixReviewOther.length)
for (const l of fixReviewOther) console.log('  not merge|blocked:', l)
// blocked-first merges in detail
for (const x of withV.filter((x) => x.vs[0].word !== 'merge')) {
  console.log(`  first verdict blocked: #${x.p.pr} ${x.vs.map((v) => v.word + (v.raw_class ? '/' + v.raw_class : '')).join(' -> ')}`)
}
// multi-round merges whose rounds are all merge (re-verification of a moved head)
const mergeOnlyRepeat = withV.filter((x) => x.vs.length > 1 && x.vs.every((v) => v.word === 'merge'))
R('multi_verdict_all_merge_prs', mergeOnlyRepeat.length)
// REWORK DECOMPOSITION: every verdict after a PR's first, keyed by what preceded it.
//   repair        the previous verdict was blocked (a repair round a block paid for)
//   reverify      the previous verdict was merge and this one names a different head (re-verification of a moved head)
//   duplicate     the previous verdict was merge at the same head
// and each keyed by its own outcome (merge / blocked).
const headOf = (v) => (/[0-9a-f]{40}/.exec(v.first) ?? [null])[0]
const rework = {}
const reverifyPrs = {}
for (const { p, vs } of withV) for (let i = 1; i < vs.length; i++) {
  const prev = vs[i - 1]
  const kind = prev.word === 'blocked' ? 'repair' : headOf(vs[i]) !== headOf(prev) ? 'reverify' : 'duplicate'
  const k = `${kind}->${vs[i].word}`
  rework[k] = (rework[k] ?? 0) + 1
  if (kind === 'reverify') reverifyPrs[p.pr] = (reverifyPrs[p.pr] ?? 0) + 1
}
R('extra_rounds', rounds.reduce((a, b) => a + b, 0) - withV.length)
R('extra_rounds_by_cause', rework)
R('reverify_rounds_by_pr', reverifyPrs)
const rv = Object.values(reverifyPrs)
if (rv.length >= 5) R('reverify_loo', { cells: rv.length, min: Math.min(...rv), max: Math.max(...rv), total: rv.reduce((a, b) => a + b, 0), drop_max_cell: rv.reduce((a, b) => a + b, 0) - Math.max(...rv) })
R('one_round_yield', withV.length ? (withV.filter((x) => x.vs.length === 1 && x.vs[0].word === 'merge').length / withV.length).toFixed(4) : 'n/a')
// null control: the block rate of FIRST rounds, and the catches it predicts for the reverify rounds
const firstBlocked = withV.filter((x) => x.vs[0].word === 'blocked').length
const nRev = Object.values(rework).length ? (rework['reverify->merge'] ?? 0) + (rework['reverify->blocked'] ?? 0) : 0
R('null_first_round_block_rate', (firstBlocked / withV.length).toFixed(4))
R('null_expected_blocks_in_reverify', (nRev * firstBlocked / withV.length).toFixed(2))

// production cross-check: statsHistogram over the same fetched map
const fetched = new Map(prs.map((p) => [String(p.pr), { body: p.body, comments: p.comments, reviews: p.reviews }]))
const hist = PL.statsHistogram(prs.map((p) => ({ pr: String(p.pr) })), fetched, PL.blockClasses())
R('prod_statsHistogram_verdict_prs', hist.coverage.verdictPrs.size)
R('prod_statsHistogram_unclassified', hist.unclassified.length)
R('prod_head_moved_entries', hist.verdicts.get(PL.REWORK_CLASS)?.entries ?? 0)

// ---- 2. coverage by class ------------------------------------------------------------------------
// CLASS RULES (mine): title prefix before the first ':' (or '(') and the author login.
//   bot cycles        author ends in [bot] AND is not hpo-author (the App that authors every lane)
//   record and chore  prefix in record|chore|docs|ci|audit|register|plan|handover|delivery, or title has 'record'
//   fix and feature   prefix in fix|feat|feature|perf|refactor|test|tests or `fix/` branch in the merge subject
//   other lanes       anything else
const REC = /^(record|chore|docs|ci|audit|register|plan|handover|delivery|policy|governance|carry|budget|structure|re-record|process|claims)\b/i
const FIX = /^(fix|feat|feature|perf|refactor|test|tests|card|ui|ux)\b/i
function classOf(p) {
  const t = String(p.title ?? '')
  const a = String(p.author ?? '')
  if (/\[bot\]$/.test(a) && a !== 'hpo-author[bot]') return 'bot cycles'
  if (REC.test(t) || /\brecord\b/i.test(t.split(':')[0])) return 'record and chore'
  if (FIX.test(t) || /from [^/]+\/fix\//.test(p.subject)) return 'fix and feature'
  return 'other lanes'
}
const cov = {}
for (const { p, vs } of perPr) {
  const c = classOf(p)
  cov[c] ??= { merges: 0, with_verdict: 0, no_verdict: 0, no_verdict_prs: [], authors: {} }
  cov[c].merges += 1
  if (vs.length) cov[c].with_verdict += 1
  else { cov[c].no_verdict += 1; cov[c].no_verdict_prs.push(p.pr) }
  cov[c].authors[p.author] = (cov[c].authors[p.author] ?? 0) + 1
}
R('no_verdict', perPr.filter((x) => !x.vs.length).length)
// APPROVAL PATH (the split that separates the no-verdict merges): owner-approved (an APPROVED review by the
// code owner `tvofi`, CLAUDE.md "only @tvofi reviews code-owned paths") against App-approved (`hpo-approver[bot]`).
const path_ = (p) => p.reviews.some((r) => r.user === 'tvofi' && r.state === 'APPROVED') ? 'owner-approved' : p.reviews.some((r) => r.user === 'hpo-approver[bot]' && r.state === 'APPROVED') ? 'app-approved' : 'no-approval'
const byPath = {}
for (const { p, vs } of perPr) {
  const k = path_(p); byPath[k] ??= { merges: 0, no_verdict: 0, prs: [] }
  byPath[k].merges += 1
  if (!vs.length) { byPath[k].no_verdict += 1; byPath[k].prs.push(p.pr) }
}
R('no_verdict_by_approval_path', byPath)
// merged head carrying no merge verdict AT that head (orchestrator.md s11)
const stale = perPr.filter(({ p, vs }) => vs.length && headOf([...vs].reverse().find((v) => v.word === 'merge') ?? { first: '' }) !== p.head_sha).map(({ p }) => p.pr)
R('merged_head_without_merge_verdict_at_it', stale.length)
console.log('  (verdicts exist, none names the merged head):', JSON.stringify(stale))
for (const [c, v] of Object.entries(cov)) {
  R(`coverage[${c.replace(/ /g, '_')}]`, `${v.with_verdict}/${v.merges}`)
  console.log(`  ${c}: no verdict ${v.no_verdict} ${JSON.stringify(v.no_verdict_prs)} authors ${JSON.stringify(v.authors)}`)
}
if (argv.includes('--titles')) for (const { p, vs } of perPr) console.log(`  #${p.pr} [${classOf(p)}] v=${vs.length} ${p.author} :: ${p.title}`)

// ---- 3. block classes, three ways ----------------------------------------------------------------
// BUCKETS (mine): engineering = a defect in the change or its evidence; record-and-body = the PR's
// written record (body, claims, carry, version, root-cause answer); orchestration = the process
// around the change (head moved, preflight, conflict). `other` (a bare or untaught block) stays its own.
const BUCKET = {
  'mutation-vacuous': 'engineering', harness: 'engineering', 'null-control': 'engineering',
  'class-open': 'engineering', 'product-tradeoff-regression': 'engineering',
  claims: 'record-and-body', version: 'record-and-body', 'carry-missing': 'record-and-body',
  'root-cause-unanswered': 'record-and-body',
  'head-moved': 'orchestration', 'preflight-mismatch': 'orchestration', conflict: 'orchestration',
  other: 'other',
}
const byClass = {}
const byRaw = {}
const byBucket = {}
let blockedTotal = 0
const blockedList = []
for (const { p, vs } of perPr) for (const v of vs) {
  if (v.word !== 'blocked') continue
  blockedTotal += 1
  const cls = v.parsed ? v.parsed.class : '(outside grammar)'
  byClass[cls] = (byClass[cls] ?? 0) + 1
  const raw = v.parsed ? (v.raw_class && !VERDICT_CLASSES.includes(v.raw_class) ? `untaught:${v.raw_class}` : (v.raw_class ?? '(bare)')) : '(outside grammar)'
  byRaw[raw] = (byRaw[raw] ?? 0) + 1
  const b = v.parsed ? BUCKET[cls] ?? 'other' : '(outside grammar)'
  byBucket[b] = (byBucket[b] ?? 0) + 1
  blockedList.push(`#${p.pr} ${raw} :: ${v.first.replace(/[0-9a-f]{40}/, '<sha>').slice(0, 150)}`)
}
R('blocked_total', blockedTotal)
R('blocked_by_class', byClass)
R('blocked_by_written_word', byRaw)
R('blocked_by_bucket', byBucket)
for (const l of blockedList) console.log('  blocked:', l)

// ---- 6. friction keys ----------------------------------------------------------------------------
const budgetsOut = execFileSync('node', [path.join(ROOT, '.claude/workflows/policy_lint.mjs'), '--budgets'], { cwd: ROOT, encoding: 'utf8' })
const PATHS = budgetsOut.split('\n').map((l) => l.split(/\s+/)[0]).filter((x) => /\.md$/.test(x))
function briefKey(id) {
  const k = String(id).trim().replace(/^`+|`+$/g, '').replace(/#.*$/, '')
  const hits = PATHS.filter((p) => [k, k + '.md', k + '/SKILL.md'].some((s) => p === s || p.endsWith('/' + s)))
  if (hits.length === 1) return hits[0]
  if (hits.length > 1) return 'ambiguous'
  return 'unresolved'
}
function sectionOf(body) { // policy_lint.mjs:sections, read-only copy of its ## split (fences respected)
  let cur = null; let fence = false; const out = new Map()
  for (const line of String(body ?? '').split('\n')) {
    if (/^\s*(?:```|~~~)/.test(line)) fence = !fence
    const m = fence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) { cur = m[1]; out.set(cur, []); continue }
    if (cur) out.get(cur).push(line)
  }
  return (out.get('Friction') ?? []).join('\n').trim()
}
const entries = []
for (const p of prs) for (const e of PL.frictionEntries(sectionOf(p.body))) entries.push({ pr: p.pr, id: e.id, key: e.id == null ? '(unparsed entry)' : briefKey(e.id) })
const prodTotal = [...hist.friction.values()].reduce((a, c) => a + c.entries, 0)
R('friction_entries', entries.length)
R('prod_statsHistogram_friction_entries', prodTotal)
const oneFile = entries.filter((e) => e.key !== 'ambiguous' && e.key !== 'unresolved' && e.key !== '(unparsed entry)')
R('friction_share_one_file', entries.length ? (oneFile.length / entries.length).toFixed(3) : 'n/a')
R('friction_one_file', oneFile.length)
R('friction_ambiguous', entries.filter((e) => e.key === 'ambiguous').length)
R('friction_unresolved', entries.filter((e) => e.key === 'unresolved').length)
R('friction_unparsed', entries.filter((e) => e.key === '(unparsed entry)').length)
const perFile = {}
for (const e of entries) {
  perFile[e.key] ??= {}
  const sp = String(e.id)
  perFile[e.key][sp] = (perFile[e.key][sp] ?? 0) + 1
}
for (const [k, v] of Object.entries(perFile).sort()) console.log(`  friction key ${k}: ${JSON.stringify(v)}`)
R('friction_per_file', perFile)
// production keys, for the entry-for-entry comparison
const prodKeys = {}
for (const [k, c] of hist.friction) prodKeys[k] = c.entries
R('prod_friction_keys', prodKeys)
