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
import { fileURLToPath, pathToFileURL } from 'node:url'

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
    agentImpl: REVIEW('Fix review: merge aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa') })
  t('a well-formed merge verdict merges', out.results[0].merged === true, J(out.results[0]))
})
await block('group 10', async () => {
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: blocked aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa mutation-vacuous: the proof names no failing check') })
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
    agentImpl: REVIEW('Fix review: blocked aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa root-cause-unanswered: the branch turned typing red and the body does not say why') })
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
  // #1239 (D13-02), measured at the round-5 baseline: 16 of 30 blocked
  // verdicts fell outside this grammar -- 7 bare (no class word), 9 with a
  // class word the vocabulary never taught -- and every one of them took the
  // unparseable path, which drops the head SHA the reviewer measured and
  // leaves the wave no route but "blocked, no reason". The grammar below now
  // reads both shapes: the class words stay the taught list for ROUTING, but
  // a verdict that names a full head SHA is never discarded unreadable --
  // the head is the one thing a later round cannot re-derive. (This group's
  // old fixture used `h1` as its SHA, so the abbreviated-SHA refusal fired
  // before the class arm and the pin exercised no vocabulary at all.)
  const sha = 'a'.repeat(40)
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW(`Fix review: blocked ${sha} not-a-real-class: invented`, 'blocked') })
  const r = out.results[0]
  t('a blocked verdict with an untaught class word parses and routes to other',
    r.merged === false && r.class === 'other',
    J(r))
  t('and the untaught word survives in the why rather than vanishing into "unparseable"',
    /^not-a-real-class:/.test(r.why ?? '') && !/unparseable/.test(r.why ?? ''), J(r.why).slice(0, 90))
  t('an untaught class word is repaired once, exactly like a taught one -- the repair round is the proof the verdict ROUTED (unparseable verdicts skip it)',
    calls.filter((c) => c.startsWith('repair')).length === 1 && calls.some((c) => c.startsWith('re-review')), J(calls))
})
await block('group 13b -- bare blocked verdicts (#1239: the 7 bare of 16)', async () => {
  const sha = 'b'.repeat(40)
  const { out, calls } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW(`Fix review: blocked ${sha}`, 'blocked') })
  const r = out.results[0]
  t('a bare blocked verdict (no class) parses and routes to other',
    r.merged === false && r.class === 'other' && !/unparseable/.test(r.why ?? ''), J(r))
  t('a bare blocked verdict is repaired once, not discarded as unreadable',
    calls.filter((c) => c.startsWith('repair')).length === 1, J(calls))
})
await block('group 13c -- the reason line without a class word (#1239: parse the reason line)', async () => {
  const sha = 'c'.repeat(40)
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW(`Fix review: blocked ${sha}: the mutation proof names no failing check`, 'blocked') })
  const r = out.results[0]
  t('`blocked <sha>: <why>` parses with the reason kept as the why',
    r.merged === false && r.class === 'other' && /mutation proof/.test(r.why ?? '') && !/unparseable/.test(r.why ?? ''), J(r))
})
await block('group 13d -- what still refuses', async () => {
  // The loosening is total about CLASS WORDS and never about the head: the
  // SHA stays the full 40 hex the merge gate compares against (#1106), and a
  // first line that is neither merge nor blocked -- the `PASS — merge` shape
  // the D13 brief names -- stays unreadable rather than guessed at.
  const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW(`Fix review: blocked ${'a'.repeat(39)}: reason without a full sha`, 'blocked') })
  t('a blocked verdict with a 39-hex SHA is still refused (#1106)',
    /unparseable/.test(out.results[0].why ?? ''), J(out.results[0].why).slice(0, 80))
  const { out: out2 } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: REVIEW('Fix review: PASS — merge deadbeef', 'merge') })
  t('a `PASS — merge` line stays outside the grammar entirely',
    /unparseable/.test(out2.results[0].why ?? ''), J(out2.results[0].why).slice(0, 80))
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
  // DERIVE the regex from web-fix-wave.js's own source rather than rebuilding a
  // second copy by hand. A hand-rebuilt copy is exactly the shape #592 and the
  // root-cause catalogue both name: a check that supplies the value it is
  // meant to be verifying. Concretely, this file used to hardcode `(\S+)` for
  // the SHA capture groups here while production tightened to `[0-9a-f]{40}`
  // -- the two silently diverged, and the 'deadbeef' null control below stayed
  // green throughout, proving nothing about VERDICT_RE. `run()` above already
  // executes the wave script's body via `new Function`, so the literal is
  // extracted from `src` (the same string that already feeds VERDICT_CLASSES)
  // and evaluated with those classes, instead of retyped.
  const reLiteral = src.match(/const VERDICT_RE = new RegExp\(\n([\s\S]*?)\n\)/)
  t('VERDICT_RE\'s literal is extracted from the wave script\'s own source', !!reLiteral, 'could not locate the VERDICT_RE definition')
  const re = new Function('VERDICT_CLASSES', `return new RegExp(${reLiteral[1]})`)(classes)
  const briefsDir = path.join(here, '..', '..', 'tools', 'audit', 'briefs')
  const briefs = fs.readdirSync(briefsDir).filter((f) => f.endsWith('.md')).sort().map((f) => [f, fs.readFileSync(path.join(briefsDir, f), 'utf8')])
  t('the briefs directory is readable and non-empty', briefs.length > 0, `found ${briefs.length}`)
  // A brief is hard-wrapped, so an example can span a newline; `VERDICT_RE`'s `.+`
  // cannot. Extract across the wrap and collapse the whitespace, or a correct
  // example fails for the width of its column -- a check refusing the thing it
  // exists to accept, which is worse than one that misses.
  const examples = briefs.flatMap(([f, text]) => [...text.matchAll(/`((?:blocked|merge) [^`]+)`/g)].map((m) => [f, m[1].replace(/\s+/g, ' ').trim()]))
  t('the briefs carry at least three verdict examples (floor, not a count)', examples.length >= 3, `found ${examples.length}`)
  // The briefs write `<sha>` as a human placeholder -- a reviewer substitutes
  // the real head SHA, never types the literal angle brackets. The grammar
  // check is about the CLASS and shape a brief spells out, not about `<sha>`
  // being 40 hex itself, so a stand-in SHA is substituted before parsing.
  const SHA_STAND_IN = 'a'.repeat(40)
  for (const [f, ex] of examples) t(`${f} example parses: ${ex.slice(0, 60)}`, re.test('Fix review: ' + ex.replace(/<sha>/g, SHA_STAND_IN)), 'rejected by VERDICT_RE')
  const colonForm = briefs.filter(([, text]) => /`blocked:/.test(text)).map(([f]) => f)
  t('no brief spells a verdict in the form the parser rejects (`blocked:`)', colonForm.length === 0, `found in ${colonForm.join(', ')}`)
  t('the spelling the contract used for a session is refused (negative control)',
    !re.test('Fix review: blocked: finding not carried to <stage>'), 'the old form parses, so this pin cannot fail')
  t('a bare merge verdict with the full 40-hex SHA parses (null control)', re.test(`Fix review: merge ${SHA_STAND_IN}`), 'rejected')
  t('an abbreviated SHA is refused, not merely a \\S+ null control (#1106)', !re.test('Fix review: merge 995b48e'), 'an abbreviated SHA parsed clean, which is the #1106 defect')
})

await block('group 14 -- the two readers of a blocked verdict deliver one class', async () => {
  // #1475 (D13-05). A blocked verdict is read by TWO programs: `policy_lint.mjs`'s
  // `statsHistogram`, which keys its class table on the word it finds, and this
  // script's `parseVerdict`, which ROUTES the word (a taught one as itself, an
  // untaught one to `other`). The reviewer prompt teaches ONE vocabulary
  // (`${VERDICT_CLASSES.join(', ')}` in web-fix-wave.js) and `policy_lint.mjs`
  // extracts the same literal, so a class the window's reviewer wrote must be a
  // class both readers deliver -- or they disagree about one verdict, which is
  // what happened at round 7's #1429: `product-tradeoff-regression` was keyed by
  // the histogram and routed to `other` by the wave, 1 of the window's 2 blocked
  // verdicts and 100% of its engineering blocks. Both readers are DRIVEN below.
  const { statsHistogram } = await import(pathToFileURL(path.join(here, 'policy_lint.mjs')).href)
  const words = [...src.matchAll(/const VERDICT_CLASSES = \[([^\]]*)\]/g)]
    .flatMap((m) => [...m[1].matchAll(/'([a-z][a-z0-9-]*)'/g)].map((x) => x[1]))
  t('the class vocabulary is extracted from the wave script', words.length >= 10, `found ${words.length}`)
  // The round-7 window's `blocked` first lines, verbatim (yield_rounds.py prints
  // them from /issues/<n>/comments over the round's window; the audit's own
  // harness drives both readers over them at tools/audit/round7/D13/
  // class_vocabulary.mjs). #1418 is the taught control.
  const WINDOW = [
    ['1418', 'root-cause-unanswered'],
    ['1429', 'product-tradeoff-regression'],
  ].map(([pr, word]) => [pr, word, `Fix review: blocked ${'a'.repeat(40)} ${word}: the reviewer's own words`])
  // The histogram's cell key, through its OWN argument shape: the CLI passes the
  // verdict words plus the classes, one fixture comment per verdict line.
  const histKey = (line) => [...statsHistogram(
    [{ pr: 7002 }],
    new Map([[7002, { body: '', comments: [{ body: line }] }]]),
    [...new Set(['merge', 'blocked', ...words])],
  ).verdicts.keys()].join('+') || null
  const rows = []
  for (const [pr, expected, line] of WINDOW) {
    const { out } = await run({ groups: [G('A')], groupsFile: 'r.json', reconResult: OK, agentImpl: REVIEW(line) })
    const route = out.results[0]?.class ?? null
    const key = histKey(line)
    rows.push({ pr, expected, key, route, disagree: key !== route, taught: words.includes(expected) })
  }
  for (const r of rows) console.log(`  class  #${r.pr} expected=${r.expected} taught=${r.taught ? 1 : 0} histogram_key=${r.key} wave_route=${r.route} disagree=${r.disagree ? 1 : 0}`)
  const bad = rows.filter((r) => r.disagree)
  t("every class the window's blocked verdicts name is keyed by the histogram AND routed by the wave",
    rows.length === WINDOW.length && bad.length === 0,
    `disagreeing: ${bad.map((r) => `#${r.pr} key=${r.key} route=${r.route}`).join(', ') || '(none)'}`)
  // THE ARM THAT SAYS THE COMPARISON CAN FAIL. Every row above is now a taught
  // word, so agreement is what the check prints whether or not it is comparing
  // anything. An invented word is NOT taught, so the histogram keys it raw while
  // the wave routes `other` (#1240's deliberate drift signal) -- if this arm
  // agreed too, the comparison would be reading one reader twice.
  const invented = `Fix review: blocked ${'b'.repeat(40)} not-a-real-class: invented`
  t('the comparison fires: an untaught class word is keyed raw and routed to `other` (positive control)',
    !words.includes('not-a-real-class') && histKey(invented) === 'not-a-real-class',
    `histogram_key=${histKey(invented)} with ${words.length} taught word(s)`)
  // ...and the taught control row, which is the whole reason a disagreement here
  // is a finding about the untutored word rather than about the readers.
  t('a taught class agrees in the same run (null control)',
    rows.filter((r) => r.taught && !r.disagree).length === rows.filter((r) => r.taught).length
      && rows.some((r) => r.taught),
    J(rows))
})

console.log('-- The round driver: the schedule every dimension brief must be in')
// R7-INSTR-01 (#1477). `.claude/workflows/audit-find.js` is the committed
// workflow that runs a round, and its `DIMS` stopped at D12 through round 7 while
// `tools/audit/briefs/D13.md` had been in the tree since round 6: the brief
// existed, the schedule did not name it, and nothing said so -- the dedup
// prompt's `/reports/` count and path list are both built from DIMS, and the
// missing-dimension log iterates it, so a dimension absent from the list is
// absent from the round's record too. Round 7's prep dispatched D13 by hand.
// `WAVES` must partition DIMS (a dimension in no wave never runs), and
// `ISOLATED` with `API_DIMS` decides the worktree a finder gets and whether it
// may read GitHub -- both narrower lists a new dimension joins deliberately.
// `tools/audit/prepare_baseline.sh` carries the same worktree set in a
// shell file and says in its own comment that a seat editing one edits both, so// the agreement is asserted rather than remembered. It belongs HERE because
// `.claude/` is INERT in tests/closure.py and the gate structurally cannot
// select any of this; the `wave-script` job is never scoped.
await block('the round driver', async () => {
  const rd = fs.readFileSync(path.join(here, 'audit-find.js'), 'utf8')
  const dimsIn = (text) => [...text.matchAll(/'([A-Z]\d+)'/g)].map((m) => m[1])
  const grab = (re) => { const m = re.exec(rd); return m ? dimsIn(m[1]) : [] }
  // `WAVES` is a list of lists; brace counting rather than a line-anchored match,
  // so re-wrapping the literal does not silently yield an empty schedule -- an
  // empty extraction that reported "no gap" would be this check's own defect.
  const waveList = (() => {
    const key = 'const WAVES = ['
    const start = rd.indexOf(key)
    if (start < 0) return []
    const from = start + key.length - 1
    let depth = 0, end = -1
    for (let i = from; i < rd.length; i += 1) {
      if (rd[i] === '[') depth += 1
      else if (rd[i] === ']') { depth -= 1; if (depth === 0) { end = i; break } }
    }
    if (end < 0) return []
    return [...rd.slice(from, end + 1).matchAll(/\[([^\]]*)\]/g)].map((m) => dimsIn(m[1]))
  })()
  const shell = fs.readFileSync(
    path.join(here, '..', '..', 'tools', 'audit', 'prepare_baseline.sh'), 'utf8')
  const S = {
    dims: grab(/const DIMS = \[([^\]]*)\]/),
    waves: waveList,
    isolated: grab(/const ISOLATED = new Set\(\[([^\]]*)\]/),
    api: grab(/const API_DIMS = new Set\(\[([^\]]*)\]/),
    baseline: ((/^ISOLATED_DIMS="([^"]*)"/m.exec(shell) ?? [, ''])[1]).split(/\s+/).filter(Boolean),
    briefs: fs.readdirSync(path.join(here, '..', '..', 'tools', 'audit', 'briefs'))
      .filter((f) => /^D\d+\.md$/.test(f)).map((f) => f.slice(0, -3)).sort(),
  }
  // One predicate, two callers: the tree below and the synthetic controls after
  // it. A control that re-implements the rule tests the copy.
  const scheduleGaps = (s) => {
    const gaps = []
    for (const k of ['dims', 'waves', 'isolated', 'api', 'baseline']) {
      if (!s[k]?.length) gaps.push(`${k} not found (an empty extraction is a gap, never an exemption)`)
    }
    if (gaps.length) return gaps
    for (const d of s.briefs) if (!s.dims.includes(d)) gaps.push(`briefs/${d}.md has no DIMS entry`)
    for (const d of s.dims) if (!s.briefs.includes(d)) gaps.push(`DIMS names ${d}, which has no brief`)
    for (const d of s.dims) if (s.dims.indexOf(d) !== s.dims.lastIndexOf(d)) gaps.push(`DIMS names ${d} twice`)
    const inWaves = (d) => s.waves.filter((w) => w.includes(d)).length
    for (const d of s.dims) if (inWaves(d) !== 1) gaps.push(`${d} runs in ${inWaves(d)} wave(s), not exactly one`)
    for (const w of s.waves.flat()) if (!s.dims.includes(w)) gaps.push(`a wave runs ${w}, which DIMS does not name`)
    for (const d of s.isolated) if (!s.dims.includes(d)) gaps.push(`ISOLATED names ${d}, which DIMS does not`)
    for (const d of s.api) if (!s.isolated.includes(d)) gaps.push(`API_DIMS names ${d}, which ISOLATED does not (its history needs a worktree with .git)`)
    const base = [...s.baseline].sort().join(','), iso = [...s.isolated].sort().join(',')
    if (base !== iso) gaps.push(`prepare_baseline.sh ISOLATED_DIMS [${base}] != audit-find.js ISOLATED [${iso}]`)
    return gaps
  }
  const real = scheduleGaps(S)
  console.log(`  scope  ${S.dims.length} dimension(s), ${S.waves.length} wave(s), ${S.isolated.length} isolated, ${S.api.length} API-reading, ${S.briefs.length} brief(s)`)
  t("every dimension brief is in the round driver's DIMS, and its waves and worktree lists agree",
    S.briefs.length >= 14 && real.length === 0, `gaps: ${real.join('; ')}`)
  t('the check fires: a DIMS list that stops short of a brief is refused (positive control)',
    scheduleGaps({ ...S, dims: S.dims.filter((d) => d !== 'D13') }).length > 0,
    'a schedule missing a dimension brief passed, so this check cannot see R7-INSTR-01')
  t('the check fires: a wave list that does not partition DIMS is refused (positive control)',
    scheduleGaps({ ...S, waves: [(S.waves[0] ?? []).filter((d) => d !== 'D13'), S.waves[1] ?? []] }).length > 0,
    'a wave list that runs no D13 passed')
  t('the check fires: the two worktree lists drifting apart is refused (positive control)',
    scheduleGaps({ ...S, baseline: S.baseline.filter((d) => d !== 'D13') }).length > 0,
    'audit-find.js and prepare_baseline.sh may disagree, which its own comment forbids')
  t('and an empty extraction is refused rather than reported clean (null control)',
    scheduleGaps({ dims: [], waves: [], isolated: [], api: [], baseline: [], briefs: [] }).length > 0,
    'a schedule read out of nothing reported no gap')
})

console.log('-- The verification pass: one verifier per dimension, every finding to the judge')
// Round 8, the owner's panel shape. `audit-verify.js` dispatched three verifiers
// per panel of at most eight findings and dropped a majority-refuted finding
// from the judge's survivors. It now dispatches ONE verifier per dimension,
// however many findings that dimension has, and one judge whose prompt names
// every finding -- a refute is a vote the judge re-measures, never a kill.
// Driven, not grepped: the script body runs against stubbed agent()/pipeline().
await block('the verification pass', async () => {
  const vsrc = fs.readFileSync(path.join(here, 'audit-verify.js'), 'utf8')
  const vi = vsrc.indexOf('export const meta')
  const vbody = vsrc.slice(0, vi) + vsrc.slice(vsrc.indexOf('\n}\n', vi) + 3)
  const F = (id, dimension) => ({ id, dimension, severity: 'low', title: id, claim: id, report_path: 'r', harness_paths: [], attached_refutation: null })
  const findings = [...Array.from({ length: 9 }, (_, k) => F(`D1-${k}`, 'D1')), F('D3-01', 'D3')]
  const isVerifier = (label) => label.endsWith('/verify') || /^D\d+-\d+\/v\d$/.test(label)
  // Drives the real body. `nullDims` names dimensions whose verifier returns
  // null on every call; every other verifier refutes everything it is shown.
  const drive = async ({ from, nullDims = [] } = {}) => {
    const calls = []
    const agent = async (prompt, opts) => {
      const label = opts?.label ?? '?'
      calls.push({ label, prompt })
      if (label === 'read') return { findings }
      if (isVerifier(label)) {
        if (nullDims.some((d) => prompt.includes(`dimension ${d} `))) return null
        const ids = findings.filter((f) => prompt.includes(`"${f.id}"`)).map((f) => f.id)
        return { votes: ids.map((id) => ({ id, vote: 'refute' })) }
      }
      if (label === 'judge') return { verdicts: [] }
      return { issues: [] }
    }
    const pipeline = (items, fn) => Promise.all(items.map(fn))
    const fn = new Function('agent', 'log', 'phase', 'pipeline', 'args', `return (async () => { ${vbody} })()`)
    await fn(agent, () => {}, () => {}, pipeline, { round: 8, repo: '/repo', ...(from ? { from } : {}) })
    return calls
  }
  const verifiers = (cs) => cs.filter((c) => isVerifier(c.label))
  const judgeSees = (cs) => {
    const judges = cs.filter((c) => c.label === 'judge')
    return judges.length === 1 ? findings.filter((f) => judges[0].prompt.includes(`"${f.id}"`)).map((f) => f.id) : []
  }
  // One predicate, two callers: the driven run and the synthetic control.
  const shapeGaps = (cs) => {
    const gaps = []
    const vs = verifiers(cs)
    const dims = [...new Set(findings.map((f) => f.dimension))]
    if (vs.length !== dims.length) gaps.push(`${vs.length} verifier call(s) for ${dims.length} dimension(s)`)
    for (const d of dims) if (vs.filter((c) => c.prompt.includes(`dimension ${d} `)).length !== 1) gaps.push(`${d} has no single verifier`)
    const judges = cs.filter((c) => c.label === 'judge')
    if (judges.length !== 1) gaps.push(`${judges.length} judge call(s)`)
    const seen = judgeSees(cs)
    const missing = findings.filter((f) => !seen.includes(f.id))
    if (missing.length) gaps.push(`the judge never sees ${missing.map((f) => f.id).join(', ')}`)
    return gaps
  }
  const real = shapeGaps(await drive())
  t('one verifier per dimension (9 findings in one, 1 in another) and one judge shown every finding, all refuted',
    real.length === 0, real.join('; '))
  // The old shape: two panels for D1's nine findings, three seats each, and a
  // judge prompt that names no finding (every one killed by majority refute).
  const old = [{ label: 'read', prompt: '' },
    ...['D1-0', 'D1-1', 'D3-0'].flatMap((p) => [1, 2, 3].map((s) => ({ label: `${p}/v${s}`, prompt: `panel ${p} dimension ${p.slice(0, 2)} ` }))),
    { label: 'judge', prompt: 'Votes as counted: {}' }]
  t('the check fires: three seats per panel and a judge that sees only survivors is refused (positive control)',
    shapeGaps(old).length > 0, 'the round-7 shape passed')
  // A verifier that returns null twice: re-run exactly once, and its findings
  // still reach the judge, marked unvoted rather than dropped.
  const nul = await drive({ nullDims: ['D3'] })
  const d3calls = verifiers(nul).filter((c) => c.prompt.includes('dimension D3 ')).length
  const judgeNul = nul.find((c) => c.label === 'judge')?.prompt ?? ''
  t('a null verifier is re-run once, and its findings reach the judge unvoted',
    d3calls === 2 && /"id":"D3-01"[^}]*"verifier":\{"vote":"unvoted"/.test(judgeNul) && judgeSees(nul).length === findings.length,
    `D3 verifier calls ${d3calls}; judge sees ${judgeSees(nul).length} of ${findings.length}; D3-01 unvoted ${/"id":"D3-01"[^}]*"verifier":\{"vote":"unvoted"/.test(judgeNul)}`)
  // args.from "judge": no verifier runs, and the judge is handed every finding.
  const res = await drive({ from: 'judge' })
  t('from "judge" runs no verifier and hands the judge every registered finding',
    verifiers(res).length === 0 && judgeSees(res).length === findings.length,
    `verifier calls ${verifiers(res).length}; judge sees ${judgeSees(res).length} of ${findings.length}`)
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
