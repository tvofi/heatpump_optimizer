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


console.log('-- The referent a keyed stage must carry, not only the stage word')
// THE DEFECT THIS PINS. The vocabulary check above asserts that every stage a
// roster carries is a word this script branches on. It says nothing about the
// KEY that branch then reads. At origin/main 8b2a2e9 the UX roster carried
// fourteen groups at `in-review` holding only `stage` and `note`, and the
// review path reads `g.resume.pr ?? g.resume.open_pr` -- so a wave over that
// roster dispatches fourteen adversarial reviewers at PR `undefined`, from a
// worktree detached at head `undefined`. Nine more sat at `done` with no
// `merged_pr`/`merge_sha`, which the done path returns as a merge whose number
// and SHA are both undefined. The vocabulary check printed 37 passed, 0 failed
// throughout, because every one of those stage words was in KNOWN_STAGES.
//
// THE RULE, READ OFF web-fix-wave.js RATHER THAN INVENTED HERE -- and, since
// the #691 review, EXECUTED rather than only written down. A stage requires a
// key exactly where that script dereferences `g.resume.<key>` IN THAT STAGE'S
// OWN BRANCH, with no `??` fallback closing the chain, AND the value is a
// POINTER: a commit, a pull request or a head. Keys sharing one `??` chain are
// alternatives; separate chains are separate requirements -- which is why
// review asks for `pr` OR `open_pr`, the two spellings the committed rosters
// use, and ALSO for `head_sha`.
//
// THE POINTER CLAUSE IS THE #691 REVIEW'S FIRST RESIDUAL, CLOSED HERE. The
// earlier wording ended at "hands the value to an agent or reports it as fact",
// which also covers `what` and `missing` -- the fix branch's RESUMED prompt
// dereferences both bare and interpolates both into a prompt an agent is handed
// -- while STAGE_REFERENT.fix required neither. Rule and map could be read
// apart. The wording is tightened rather than the map widened, and the
// discriminant is the script's own: `pushed_sha` names a git object the RESUMED
// prompt tells a resuming fixer to re-attach to, and it is the one `fix` key
// the Reconcile prompt checks against origin (`resume.stage is 'fix' but the
// branch tip differs from resume.pushed_sha`). `what` and `missing` name no
// object and origin holds no fact to reconcile them against; an absent one
// degrades a sentence. Requiring them would make this check the author of a
// prose convention rather than the reader of the script's -- the same failure
// the stale-key guard below exists to prevent.
//
// AND THE TWO CANNOT DRIFT APART AGAIN, because the rule is now a predicate:
// deriveReferents() re-derives the whole map -- rows, alternatives and the
// blocked exemption -- from the branch source, and STAGE_REFERENT is asserted
// equal to it. Edit the map without the script, or the script without the map,
// and this goes red.
//
// `blocked` is EXEMPT, and the exemption is now DERIVED rather than asserted:
// its branch reads `g.resume.pr ?? g.resume.open_pr ?? null` and
// `g.resume.head_sha ?? null`, every chain closed by a fallback, so the rule
// yields an empty row for it and the script itself declares those keys
// optional. It spends no agent and dispatches nobody; requiring them would fail
// the one committed blocked group, whose roster is not defective. `pending` and
// a missing stage normalise to null, match no branch and read no key at all.
const STAGE_REFERENT = {
  review: [['pr', 'open_pr'], ['head_sha']],
  merge: [['pr'], ['head_sha']],
  done: [['merged_pr'], ['merge_sha']],
  fix: [['pushed_sha']],
}
const STAGE_NO_REFERENT = ['blocked']
// ONE predicate, two callers: the roster scan below and the synthetic controls
// beside it. A control that re-implements the rule tests the copy.
const referentGaps = (resume, normalise) => {
  const need = STAGE_REFERENT[normalise(resume?.stage)]
  if (!need) return []
  return need.filter((alts) => !alts.some((k) => resume[k] !== undefined && resume[k] !== null))
}

// THE SECOND #691 RESIDUAL: the stale-key guard tested `resume.<key>` against
// the WHOLE script, so a row naming a key some OTHER branch reads passed --
// `merge: [['pr'], ['head_sha', 'merge_sha']]` was accepted because the done
// branch reads `merge_sha`. Both guards below are scoped to the branch instead,
// and a branch is a region of source rather than a whole file.
//
// The two shapes web-fix-wave.js tests a stage in: `if (stage === '<s>') { .. }`
// and RESUMED's `g.resume?.stage === 'fix' ? `..` : ''`. Brace counting is
// balanced across `${..}`, so the block form needs no template awareness; the
// ternary form is one template literal and is taken backtick to backtick. An
// unlocatable branch returns '' and is asserted against a floor below, because
// an empty region derives an empty row, which reads exactly like an exemption.
const branchSource = (stage) => {
  const out = []
  for (const m of src.matchAll(new RegExp(`===\\s*'${stage}'`, 'g'))) {
    let i = m.index + m[0].length
    while (i < src.length && /[\s)]/.test(src[i])) i += 1
    if (src[i] === '{') {
      let depth = 0, j = i
      for (; j < src.length; j += 1) {
        if (src[j] === '{') depth += 1
        else if (src[j] === '}' && (depth -= 1) === 0) break
      }
      out.push(src.slice(i, j + 1))
    } else if (src[i] === '?') {
      const a = src.indexOf('`', i), b = src.indexOf('`', a + 1)
      if (a > 0 && b > a) out.push(src.slice(a, b + 1))
    }
  }
  return out.join('\n')
}
// Every `g.resume.<key>` in a region, grouped into its `??` chain. A chain
// whose alternatives run out into anything that is not another resume key --
// `null`, `'no note'` -- is GUARDED: the script has spelled the key optional
// and asks the roster for nothing.
const DEREF = /g\.resume\??\.([A-Za-z_][A-Za-z0-9_]*)/g
const chainsIn = (text) => {
  const chains = []
  let i = 0
  for (;;) {
    DEREF.lastIndex = i
    const m = DEREF.exec(text)
    if (!m) return chains
    const keys = [m[1]]
    let j = m.index + m[0].length, guarded = false
    for (;;) {
      const link = /^\s*\?\?\s*/.exec(text.slice(j))
      if (!link) break
      const next = /^g\.resume\??\.([A-Za-z_][A-Za-z0-9_]*)/.exec(text.slice(j + link[0].length))
      if (!next) { guarded = true; break }
      keys.push(next[1])
      j += link[0].length + next[0].length
    }
    chains.push({ keys, guarded })
    i = j
  }
}
// THE POINTER CLAUSE, AS A PREDICATE, AND IT IS A NAME TEST -- said plainly
// because it is a design choice. web-fix-wave.js names every referent it reads
// `pr`, `open_pr`, `merged_pr`, `head_sha`, `merge_sha`, `pushed_sha`, so the
// shape is the script's own and not this file's invention. A pointer key named
// against that convention would be invisible to the test, which is why the
// leftovers are an assertion rather than a filter: a bare key that is neither
// pointer-shaped nor on NON_POINTER_KEYS fails, and the next author decides
// which it is instead of this check deciding by silence.
const POINTER_KEY = /(^|_)(pr|sha)$/
const NON_POINTER_KEYS = ['what', 'missing', 'note', 'stage']
const deriveReferents = (stage) => {
  const rows = [], mixed = [], unclassified = [], seen = new Set()
  for (const chain of chainsIn(branchSource(stage))) {
    if (chain.guarded) continue
    const ptr = chain.keys.filter((k) => POINTER_KEY.test(k))
    if (ptr.length && ptr.length !== chain.keys.length) { mixed.push(chain.keys.join(' / ')); continue }
    if (!ptr.length) { unclassified.push(...chain.keys.filter((k) => !NON_POINTER_KEYS.includes(k))); continue }
    const sig = ptr.join('|')
    if (!seen.has(sig)) { seen.add(sig); rows.push(ptr) }
  }
  return { rows, mixed, unclassified }
}
const canonical = (rows) => (rows ?? []).map((r) => [...r].sort().join('/')).sort().join(' + ') || '(exempt)'
await block('the referent a keyed stage must carry', async () => {
  const known = [...src.matchAll(/const KNOWN_STAGES = \[([^\]]*)\]/g)]
    .flatMap((m) => [...m[1].matchAll(/'([a-z-]+)'/g)].map((x) => x[1]))
  const aliasBody = /const STAGE_ALIASES = \{([^}]*)\}/.exec(src)?.[1] ?? ''
  const alias = new Map(
    [...aliasBody.matchAll(/'?([a-z-]+)'?:\s*(?:'([a-z-]+)'|(null))/g)].map((m) => [m[1], m[2] ?? null])
  )
  const normalise = (s) => (s == null ? null : alias.has(s) ? alias.get(s) : s)

  // The map must cover every stage the script branches on. A stage added to
  // web-fix-wave.js with no row here would be scanned for nothing and pass in
  // silence -- which is the exact shape of the defect above, one level up.
  const normalised = [...new Set(known.map(normalise).filter((s) => s !== null))]
  const unmapped = normalised.filter((s) => !(s in STAGE_REFERENT) && !STAGE_NO_REFERENT.includes(s))
  t('every stage the wave script branches on has a decided referent, or a recorded exemption',
    known.length > 0 && alias.size > 0 && unmapped.length === 0,
    `known=[${known}] normalised=[${normalised}] unmapped=[${unmapped}]`)

  // ...and the map must not require a key the script has stopped reading IN THE
  // BRANCH THAT REQUIRES IT. Testing against the whole file accepted a row
  // naming any key any branch reads, so a map rotting one row at a time --
  // `merge` extended with the done branch's `merge_sha` -- passed in silence.
  const region = Object.fromEntries(
    [...Object.keys(STAGE_REFERENT), ...STAGE_NO_REFERENT].map((s) => [s, branchSource(s)]))
  // The floor for the extractor itself: a branch this cannot locate yields no
  // source, no chains and an empty row, which is indistinguishable from a
  // stated exemption. Sizes are printed rather than only asserted, on the
  // precedent of the scan below -- a region that shrank to a fragment still
  // passes a non-empty test.
  const noRegion = Object.entries(region).filter(([, text]) => text.length === 0).map(([s]) => s)
  const derived = Object.fromEntries(Object.keys(region).map((s) => [s, deriveReferents(s)]))
  for (const [s, text] of Object.entries(region)) {
    console.log(`  rule   ${s.padEnd(8)} derived ${canonical(derived[s].rows).padEnd(28)} map ${canonical(STAGE_REFERENT[s])}   ${text.length} char(s) of branch source`)
  }
  t('every stage this map decides has a locatable branch in web-fix-wave.js',
    Object.keys(region).length > 0 && noRegion.length === 0, `no branch source found for: [${noRegion}]`)

  const stale = Object.entries(STAGE_REFERENT).flatMap(([s, rows]) =>
    [...new Set(rows.flat())]
      .filter((k) => !new RegExp(`resume\\??\\.${k}\\b`).test(region[s] ?? ''))
      .map((k) => `${s}: ${k}`))
  t('every key required here is one the branch that requires it actually reads',
    stale.length === 0, `not read in its own branch: [${stale.join(', ')}]`)

  // THE CONTROL THAT KEEPS THE RULE AND THE MAP FROM BEING READ APART. The
  // paragraph above states a rule; this re-derives the map from it and compares.
  // The map stays written out rather than replaced by the derivation, because a
  // reviewer reads the map and because the AND/OR structure is a decision worth
  // seeing -- but it is no longer allowed to say something the script does not.
  const drift = Object.keys(region)
    .map((s) => [s, canonical(derived[s].rows), canonical(STAGE_REFERENT[s])])
    .filter(([, rule, mapped]) => rule !== mapped)
    .map(([s, rule, mapped]) => `${s}: rule says ${rule}, map says ${mapped}`)
  t('the map is exactly what the rule derives from the branch source',
    Object.keys(region).length > 0 && drift.length === 0, drift.join('; '))

  // ...and no bare key in a keyed branch is left undecided by the pointer
  // clause, so a key the rule cannot classify halts instead of vanishing.
  const odd = Object.keys(region).flatMap((s) =>
    [...derived[s].mixed.map((c) => `${s}: pointer and prose in one chain (${c})`),
      ...derived[s].unclassified.map((k) => `${s}: ${k} is neither pointer-shaped nor a recorded non-pointer`)])
  t('every bare resume key in a decided branch is classified by the rule', odd.length === 0, odd.join('; '))

  // THE POPULATION IS AN OPERAND, on the precedent of the vocabulary check
  // above: "every keyed group carries its key" is vacuously true over zero
  // rosters, zero groups, or zero groups in a keyed stage, and prints the same
  // verdict. All three carry a floor, and all three are PRINTED -- a count that
  // fell from fourteen to thirteen reads exactly like one that was always
  // thirteen, so the misses are ENUMERATED rather than counted.
  const rosters = fs.readdirSync(here).filter((f) => /^wave-.*-groups\.json$/.test(f)).sort()
  const missing = []
  let groupsSeen = 0, keyed = 0
  for (const f of rosters) {
    for (const g of JSON.parse(fs.readFileSync(path.join(here, f), 'utf8')).groups ?? []) {
      groupsSeen += 1
      const st = normalise(g?.resume?.stage)
      if (!STAGE_REFERENT[st]) continue
      keyed += 1
      for (const alts of referentGaps(g.resume, normalise)) {
        missing.push(`${f} ${g.group ?? '(unnamed)'} at ${st}: none of ${alts.join(' / ')}`)
      }
    }
  }
  console.log(`  scope  ${rosters.length} roster(s), ${groupsSeen} group(s), ${keyed} in a stage that reads a key`)
  for (const m of missing) console.log(`  miss   ${m}`)
  t('every group in a stage the wave script reads a key for carries that key',
    rosters.length > 0 && groupsSeen > 0 && keyed > 0 && missing.length === 0,
    `rosters=${rosters.length} groups=${groupsSeen} keyed=${keyed} missing=${missing.length}`)

  // The scan is green on a repaired tree, and a scan that is green whatever it
  // reads is the failure mode this whole file exists for. Both arms of the
  // predicate are driven on synthetic groups, so the zero above is a
  // measurement rather than an absence.
  const gaps = (r) => referentGaps(r, normalise).length
  t('the defect fires: `in-review` carrying only stage and note is refused',
    gaps({ stage: 'in-review', note: 'In PR #567 with B2-B5. Decides B4-B7.' }) > 0,
    'the check cannot see the defect it was written for')
  t('the repair passes: `in-review` carrying open_pr and head_sha is accepted (null control)',
    gaps({ stage: 'in-review', open_pr: 573, head_sha: 'a227743' }) === 0, 'a healthy group is refused')
  t('`done` discriminates in both directions on merged_pr / merge_sha',
    gaps({ stage: 'done', note: 'Merged in PR #576.' }) > 0 &&
      gaps({ stage: 'done', merged_pr: 576, merge_sha: '5d73c38' }) === 0,
    'the done row does not separate a recorded merge from a remembered one')
  t('a stage the script reads no key for is not made to carry one (pending, blocked)',
    gaps({ stage: 'pending', note: 'Not started.' }) === 0 &&
      gaps({ stage: 'blocked', branch: 'b', note: 'n' }) === 0,
    'an unkeyed stage is being required to carry a referent')
  t('a null referent is a missing referent, not a present key',
    gaps({ stage: 'in-review', pr: null, open_pr: null, head_sha: null }) > 0,
    'an explicit null satisfies the check, which is how a roster patch writes one')
})

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
