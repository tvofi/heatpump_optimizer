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
// Wiring it into CI is the honest follow-up: the precedent is tests/
// card_browser.mjs, which is INERT and driven by its own never-scoped `browser`
// job. A `roster` job in the same shape would make this enforced instead of
// remembered.

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
const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }
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
{
  const { out, calls } = await run({ groups: [G('A', { stage: 'done', merged_pr: 383, merge_sha: 'b0703f7' })], groupsFile: 'r.json', reconResult: OK })
  t('stage done reports merged and spends no agent', out.results[0].merged === true && out.results[0].pr === 383 && calls.filter((c) => !c.startsWith('reconcile')).length === 0, JSON.stringify(calls))
}
{
  const { calls } = await run({
    groups: [G('A', { stage: 'merge', pr: 385, head_sha: 'bf9bda6' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('merge') ? { merged: true, sha: 'm1' } : o.label.startsWith('main after') ? { green: true } : null })
  t('stage merge skips fixer AND reviewer', !calls.some((c) => c.startsWith('fix ') || c.startsWith('review ')) && calls.some((c) => c.startsWith('merge ')), JSON.stringify(calls))
}
{
  const { calls } = await run({
    groups: [G('A', { stage: 'review', pr: 384, head_sha: 'f1063e2' })], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('review') ? { verdict: 'blocked: x' } : null })
  t('stage review skips the fixer only', !calls.some((c) => c.startsWith('fix ')) && calls.some((c) => c.startsWith('review ')), JSON.stringify(calls))
}
{
  const { out, calls } = await run({
    groups: [G('A')], groupsFile: 'r.json', reconResult: OK,
    agentImpl: async (p, o) => o.label.startsWith('fix') ? { pr: 'I ran out of budget', head_sha: 'abc' } : null })
  t('a fixer that returns prose in `pr` is refused, after one retry',
    out.results[0].pr === null && calls.filter((c) => c.startsWith('fix ')).length === 2, JSON.stringify(calls))
}

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
