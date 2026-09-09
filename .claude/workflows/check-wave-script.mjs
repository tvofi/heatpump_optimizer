// Control-flow check for web-fix-wave.js.
//
// WHY THIS EXISTS. A resumability audit found that everything protecting the
// CODE in this repository is enforced -- CI, closure.py, the orphan check, the
// ratchet, the claim files, stamp.py's refusals -- while everything protecting
// the RESUME is merely remembered, because tests/closure.py lists `.claude/` as
// INERT and closure.py's merge check actively FAILS if an INERT file appears in
// a recorded closure. The gate contains a check that keeps this directory
// unchecked. So this runs by hand, and by hand is better than not at all:
//
//     node .claude/workflows/check-wave-script.mjs
//
// It stubs agent()/log()/phase()/parallel() and drives the real script body, so
// it exercises the branching rather than a copy of it. Run it after ANY edit to
// web-fix-wave.js -- the Reconcile gate and the resume stages are the machinery
// a wave resume rests on, and both shipped once without ever having been run.
//
// It is now wired into CI as the `wave-script` job in .github/workflows/
// governance.yml, on the tests/card_browser.mjs precedent: INERT, driven by a
// never-scoped job. It was the last file in that position running by hand only.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const src = fs.readFileSync(path.join(here, 'web-fix-wave.js'), 'utf8')
// Drop the `export const meta = {...}` literal: it is ESM syntax, and the rest
// of the file is an async function body by construction.
const i = src.indexOf('export const meta')
const body = src.slice(0, i) + src.slice(src.indexOf('\n}\n', i) + 3)

async function run({ groups, groupsFile, reconResult, agentImpl }) {
  const calls = []
  const agent = async (prompt, opts) => {
    calls.push(opts?.label ?? '?')
    if (opts?.label?.startsWith('reconcile')) return reconResult
    return agentImpl ? agentImpl(prompt, opts) : null
  }
  const fn = new Function('agent', 'log', 'phase', 'parallel', 'args',
    `return (async () => { ${body} })()`)
  const out = await fn(agent, () => {}, () => {},
    (thunks) => Promise.all(thunks.map((t) => t().catch(() => null))),
    { groups, groupsFile, repo: '/repo', fork: 'deadbeef', session: 'claude-web' })
  return { out, calls }
}

const G = (group, resume) => ({ group, issues: [1], brief: 'b', resume })
const OK = { provenance_ok: true, groups: [{ group: 'g', matches: true, observed: 'x' }], mismatches: [], summary: 'ok' }
let pass = 0, fail = 0
// JSON.stringify(undefined) is undefined, not a string, so `.slice` on it
// throws and kills the run at whichever assertion happened to be first -- and a
// harness that stops reporting halfway is worse than one that reports a FAIL.
// This is exactly how the control run for the verdict grammar died.
const J = (x) => JSON.stringify(x ?? null) ?? 'undefined'
const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }
// A block that throws reports as a failure, never as a truncated run. Every
// grouped assertion below runs inside it: without that the first unexpected
// throw ends the process and the remaining assertions are silently unreported,
// which is indistinguishable from their having passed.
const block = async (label, fn) => {
  try { await fn() } catch (e) { fail++; console.log(`  FAIL ${label} threw: ${e.message.slice(0, 120)}`) }
}
const throws = async (n, re, opts) => {
  try { await run(opts); t(n, false, 'did not throw') }
  catch (e) { t(n, re.test(e.message), e.message.slice(0, 90)) }
}

console.log('-- Provenance and the fail-closed Reconcile gate')
await throws('a wave refuses to run without a committed roster', /groupsFile is required/,
  { groups: [G('A')], reconResult: OK })
await throws('a roster that disagrees with origin stops the wave', /no longer matches origin/,
  { groups: [G('A')], groupsFile: 'r.json', reconResult: { provenance_ok: true, groups: [{ group: 'A', matches: false, observed: 'no PR' }], mismatches: ['A'], summary: 's' } })
await throws('a roster that is not the committed file stops the wave', /do not match the committed roster/,
  { groups: [G('A')], groupsFile: 'r.json', reconResult: { provenance_ok: false, groups: [], mismatches: [], summary: 'differs' } })
await throws('a reconciler that returns nothing stops the wave', /unverified roster/,
  { groups: [G('A')], groupsFile: 'r.json', reconResult: null })

console.log('-- Resume stages')
await block('group 1', async () => {
  const { out, calls } = await run({ groups: [G('A', { stage: 'done', merged_pr: 383, merge_sha: 'b0703f7' })], groupsFile: 'r.json', reconResult: OK })
  t('stage done reports merged and spends no agent', out.results[0].merged === true && out.results[0].pr === 383 && calls.filter((c) => !c.startsWith('reconcile')).length === 0, J(calls))
})
await block('group 2', async () => {
  const { calls } = await run({
    groups: [G('A', { stage: 'merge', pr: 385, head_sha: 'bf9bda6' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('merge') ? { merged: true, sha: 'm1' } : o.label.startsWith('main after') ? { green: true } : null })
  t('stage merge skips fixer AND reviewer', !calls.some((c) => c.startsWith('fix ') || c.startsWith('review ')) && calls.some((c) => c.startsWith('merge ')), J(calls))
})
await block('group 3', async () => {
  const { calls } = await run({
    groups: [G('A', { stage: 'review', pr: 384, head_sha: 'f1063e2' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('review') ? { verdict: 'blocked', comment: 'Fix review: blocked a227743 harness: measured with the fixer\'s harness' } : null })
  t('stage review skips the fixer only', !calls.some((c) => c.startsWith('fix ')) && calls.some((c) => c.startsWith('review ')), J(calls))
})
await block('group 4', async () => {
  const { out, calls } = await run({
    groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('fix') ? { pr: 'I ran out of budget', head_sha: 'abc' } : null })
  t('a fixer that returns prose in `pr` is refused, after one retry',
    out.results[0].pr === null && calls.filter((c) => c.startsWith('fix ')).length === 2, J(calls))
})

console.log('-- The stage vocabulary the rosters actually use')
await block('group 5', async () => {
  // The defect this pins: the script and the committed rosters had drifted into
  // two vocabularies sharing one word, so 29 of 84 groups reached the
  // fresh-fixer branch. This asserts every stage a roster carries is one the
  // script recognises -- measured from the rosters, never from a list here,
  // because a list here would drift the same way.
  const known = [...src.matchAll(/const KNOWN_STAGES = \[([^\]]*)\]/g)]
    .flatMap((m) => [...m[1].matchAll(/'([a-z-]+)'/g)].map((x) => x[1]))
  // AND THE POPULATION IS AN OPERAND TOO. `known.length > 0` guarded the list
  // read out of the script and left the side the ENVIRONMENT decides unguarded:
  // the rosters are discovered by scanning this directory, so "every stage is
  // recognised" is vacuously true over zero files and prints the identical
  // verdict. Measured on this branch, which is what makes it live rather than
  // theoretical -- the archive deletes three of the seven rosters:
  //
  //   7 roster(s), 84 group(s)   (main)     ok  26 passed
  //   4 roster(s), 59 group(s)   (here)     ok  26 passed
  //   0 roster(s),  0 group(s)   (probe)    ok  26 passed
  //
  // A 30% drop in what a check covers must not be invisible in its own output,
  // so the counts are PRINTED as well as asserted: a floor catches the empty
  // case, and the numbers let a reader see a shrinking one.
  const rosters = fs.readdirSync(here).filter((f) => /^wave-.*-groups\.json$/.test(f))
  const used = new Map()
  let groupsSeen = 0
  for (const f of rosters) {
    for (const g of JSON.parse(fs.readFileSync(path.join(here, f), 'utf8')).groups ?? []) {
      groupsSeen += 1
      const st = g.resume?.stage
      if (st) used.set(st, (used.get(st) ?? 0) + 1)
    }
  }
  const unknown = [...used.keys()].filter((st) => !known.includes(st))
  const atRisk = unknown.reduce((n, st) => n + used.get(st), 0)
  // `t` prints its detail only on FAILURE, so asserting the floor is not the
  // same as disclosing the population -- the first draft of this fix claimed
  // both and delivered one. The count goes to stdout unconditionally.
  console.log(`  scope  ${rosters.length} roster(s), ${groupsSeen} group(s), ${used.size} distinct stage(s)`)
  t('every resume.stage in every committed roster is one the wave script branches on',
    known.length > 0 && rosters.length > 0 && groupsSeen > 0 && unknown.length === 0,
    `rosters=${rosters.length} groups=${groupsSeen} known=[${known}] used=[${[...used.keys()]}] unknown=[${unknown}] at-risk=${atRisk}`)
})
await block('group 6', async () => {
  const { out, calls } = await run({ groups: [G('A', { stage: 'in-review', open_pr: 573, head_sha: 'a227743' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('review') ? { verdict: 'blocked', comment: 'Fix review: blocked a227743 harness: measured with the fixer\'s harness' } : null })
  t("stage in-review is the review stage, and reads the roster's own open_pr key",
    !calls.some((c) => c.startsWith('fix ')) && calls.some((c) => c.startsWith('review ')) &&
      out.results[0]?.pr === 573, J(calls) + ' pr=' + J(out.results[0]?.pr))
})
await block('group 7', async () => {
  const { out, calls } = await run({ groups: [G('A', { stage: 'pending' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('fix') ? { pr: 1, head_sha: 'h' } : o.label.startsWith('review') ? { verdict: 'merge', comment: 'Fix review: merge h' } : o.label.startsWith('merge') ? { merged: true, sha: 'm' } : { green: true } })
  t('stage pending starts a fixer, deliberately rather than by falling through',
    calls.some((c) => c.startsWith('fix ')), J(calls))
})
await block('group 8', async () => {
  const { out, calls } = await run({ groups: [G('A', { stage: 'blocked', note: '#457 stays open' })], groupsFile: 'r.json', reconResult: OK })
  t('stage blocked spends no agent and is recorded for the orchestrator',
    out.results[0].skipped === 'blocked' && !calls.some((c) => c.startsWith('fix ')), J(calls))
})
await throws('an unrecognised stage refuses instead of starting a fresh fixer', /is not one of/,
  { groups: [G('A', { stage: 'halfway' })], groupsFile: 'r.json', reconResult: OK })


console.log('-- The verdict grammar, and the seats it dispatches')
// The reviewer's verdict was a free-text sentence and every non-merge outcome
// collapsed to one undifferentiated "not merged". A class is what lets a script
// route a blocked verdict instead of only a reader.
const REVIEW = (comment, verdict) => async (p, o) =>
  o.label.startsWith('fix') || o.label.startsWith('repair') ? { pr: 7, head_sha: 'h1' }
    : o.label.startsWith('review') || o.label.startsWith('re-review') ? { verdict: verdict ?? (/blocked/.test(comment) ? 'blocked' : 'merge'), comment }
    : o.label.startsWith('merge') ? { merged: true, sha: 'm' }
    : o.label.startsWith('root-cause') ? { cause: 'c', state: 'the process did not exist', countermeasure: null, comment: 'Root cause: c' }
    : { green: true }
await block('group 9', async () => {
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: merge h1') })
  t('a well-formed merge verdict merges', out.results[0].merged === true, J(out.results[0]))
})
await block('group 10', async () => {
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: blocked h1 mutation-vacuous: the proof names no failing check') })
  const r = out.results[0]
  t('a blocked verdict carries its class through to the result',
    r.merged === false && r.class === 'mutation-vacuous', J(r))
  t('a blocked verdict leaves a roster patch the orchestrator can apply',
    r.rosterPatch?.stage === 'blocked' && r.rosterPatch?.pr === 7 && r.rosterPatch?.class === 'mutation-vacuous', J(r.rosterPatch))
  t('a blocked verdict is repaired once, then re-reviewed',
    calls.filter((c) => c.startsWith('repair')).length === 1 && calls.some((c) => c.startsWith('re-review')), J(calls))
})
await block('group 11', async () => {
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: blocked h1 root-cause-unanswered: the branch turned typing red and the body does not say why') })
  t('a root-cause-unanswered verdict dispatches the root-cause seat, not another repair',
    calls.some((c) => c.startsWith('root-cause')) && !calls.some((c) => c.startsWith('repair')), J(calls))
  t('the root-cause seat returns beside the fix, and the group stays unmerged',
    out.results[0].merged === false && out.results[0].rootCause?.state === 'the process did not exist', J(out.results[0]?.rootCause))
})
await block('group 12', async () => {
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: nonsense', 'merge') })
  const r = out.results[0]
  t('an unreadable verdict never merges, whatever the schema field says',
    r.merged === false && /unparseable/.test(r.why ?? ''), J(r.why).slice(0, 80))
  t('an unreadable verdict is not retried as a repair request',
    !calls.some((c) => c.startsWith('repair')), J(calls))
})
await block('group 13', async () => {
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: blocked h1 not-a-real-class: invented', 'blocked') })
  t('a class outside the vocabulary is unreadable rather than silently accepted',
    /unparseable/.test(out.results[0].why ?? ''), J(out.results[0].why).slice(0, 80))
})

console.log('-- Regressions a review found, pinned so they cannot come back')
// A null agent return is documented runtime behaviour (a skipped agent, a
// terminal API error). The merge base guarded it; the verdict refactor dropped
// the guard, and parallel() swallowed the TypeError into "group threw" -- so the
// group lost its PR number and a live wave would have reported nothing useful.
await block('null reviewer', async () => {
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => (o.label.startsWith('fix') ? { pr: 7, head_sha: 'h1' } : null) })
  const r = out.results[0]
  t('a reviewer that returns nothing does not crash the group',
    r.merged === false && r.pr === 7, J(r))
  t('...and it is recorded as blocked, not as a thrown group',
    r.verdict === 'blocked' && !/threw/.test(r.reason ?? ''), J(r.verdict) + ' ' + J(r.reason))
})
// The schema field and the comment's first line are two statements of one
// thing. Nothing compared them, so a reviewer could return blocked in the field
// and "Fix review: merge" in the comment, and the group merged.
await block('verdict disagrees with itself', async () => {
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('fix') ? { pr: 7, head_sha: 'h1' }
      : o.label.startsWith('review') ? { verdict: 'blocked', comment: 'Fix review: merge h1' }
      : o.label.startsWith('merge') ? { merged: true, sha: 'm' } : { green: true } })
  t('a verdict whose field and comment disagree never merges',
    out.results[0].merged === false, J(out.results[0]))
})
// THE CONTRACT'S OWN EXAMPLES MUST PARSE UNDER THE SCRIPT'S OWN GRAMMAR.
// fix-review.md tells a reviewer what to write; VERDICT_RE above decides what
// the wave script will act on. For a whole session the contract said
// `blocked: finding not carried to <stage>` -- no SHA, no class -- which the
// regex rejects, so every reviewer following it to the letter wrote a verdict
// that read as no verdict at all. Nothing compared the two. This does, by
// extracting every backticked example that begins `blocked ` or `merge ` from
// every brief and running it through the grammar rebuilt from `src` -- the
// same source of truth the histogram uses -- rather than a copy kept here.
// The floor is the null control: an extraction that finds nothing must not
// pass, or deleting the examples would green this. And the old form is looked
// for by its own shape, `blocked:` -- the extractor above skips it, which is
// how two briefs kept it for a round after the contract was corrected.
await block('the contract\'s verdict examples parse under the script\'s own grammar', async () => {
  const cls = [...src.matchAll(/const VERDICT_CLASSES = \[([^\]]*)\]/g)]
  t('VERDICT_CLASSES is defined exactly once in the wave script', cls.length === 1, `found ${cls.length}`)
  const classes = [...(cls[0]?.[1] ?? '').matchAll(/'([a-z-]+)'/g)].map((m) => m[1])
  const re = new RegExp(`^Fix review:\\s+(?:(merge)\\s+(\\S+)|(blocked)\\s+(\\S+)\\s+(${classes.join('|')}):\\s*(.+))$`)
  const briefsDir = path.join(here, '..', '..', 'tools', 'audit', 'briefs')
  const briefs = fs.readdirSync(briefsDir).filter((f) => f.endsWith('.md')).sort().map((f) => [f, fs.readFileSync(path.join(briefsDir, f), 'utf8')])
  t('the briefs directory is readable and non-empty', briefs.length > 0, `found ${briefs.length}`)
  // A brief is hard-wrapped, so an example can span a newline; `VERDICT_RE`'s `.+`
  // cannot. Extract across the wrap and collapse the whitespace, or a correct
  // example fails for the width of its column -- a check refusing the thing it
  // exists to accept, which is worse than one that misses.
  const examples = briefs.flatMap(([f, text]) => [...text.matchAll(/`((?:blocked|merge) [^`]+)`/g)].map((m) => [f, m[1].replace(/\s+/g, ' ').trim()]))
  t('the briefs carry at least three verdict examples (floor, not a count)', examples.length >= 3, `found ${examples.length}`)
  for (const [f, ex] of examples) t(`${f} example parses: ${ex.slice(0, 60)}`, re.test('Fix review: ' + ex), 'rejected by VERDICT_RE')
  const colonForm = briefs.filter(([, text]) => /`blocked:/.test(text)).map(([f]) => f)
  t('no brief spells a verdict in the form the parser rejects (`blocked:`)', colonForm.length === 0, `found in ${colonForm.join(', ')}`)
  t('the spelling the contract used for a session is refused (negative control)',
    !re.test('Fix review: blocked: finding not carried to <stage>'), 'the old form parses, so this pin cannot fail')
  t('a bare merge verdict with a SHA parses (null control)', re.test('Fix review: merge deadbeef'), 'rejected')
})

// The guard above is only worth having if it is actually called.
await block('the harness guard is wired', async () => {
  const before = fail
  // The FAIL line this prints is the point: it is what a real throw would look
  // like, and it is discounted below so the total stays honest.
  await block('(probe, expected)', async () => { throw new Error('deliberate') })
  t('a throwing block is reported as a failure rather than ending the run',
    fail === before + 1, `fail ${before} -> ${fail}`)
  fail -= 1   // discount the deliberate probe
})

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
