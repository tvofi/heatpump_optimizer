// field_coverage.mjs -- every field a governance check's input carries is either
// READ by that check or IGNORED with a reason (round-9 class I3 barrier,
// prototype from the root-cause seat; handoff/r9-rca-i3).
//
// THE SHAPE IT REFUSES. A governance check is demonstrated failing on the defect
// that motivated it, and so reads the fields that defect varied. The fields the
// policy asserts but no defect has varied yet are read by nothing, and the next
// audit round finds one: `--hooks` read the script and never the matcher
// (D11-s2-02), the per-file cap read lines and never bytes (D11-s2-01), the only
// reader of the live ruleset carried rule TYPES and never a rule's parameters,
// so `dismiss_stale_reviews_on_push` changed under decision 0008 step 3(d)
// unseen (D11-s1-01). Each fix added the one field its finding named.
//
// THE BOUNDED DIRECTION (decision 0003). The list of fields a check must read
// cannot be completed; the list of fields it may IGNORE can, because the fields
// are derived from the artifact itself. So: every leaf of the input is perturbed
// to a value that violates the property, and the real check is run on it. A
// leaf whose perturbation leaves the check green is BLIND unless IGNORE names it
// with a reason; an IGNORE entry that matches no leaf is DEAD. A field the
// artifact gains later (GitHub adds a ruleset parameter, settings.json gains a
// key) is enumerated on the next run without anyone listing it.
//
// NOT GREEN BY SKIPPING. The unperturbed input must be green (else nothing is
// measured); a check that skips, errors or exits outside {0,1} on a perturbation
// is a refusal, never a detection; a registration that enumerates zero leaves is
// a refusal.
//
//   node .claude/workflows/field_coverage.mjs [--only hooks|ruleset|budgets]
//        [--ruleset-json FILE]   # the live ruleset object; without it `gh api`
//
// exit 0: no BLIND, no DEAD, no refusal. exit 1 otherwise. exit 2: usage.

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { execFileSync, spawn } from 'node:child_process'
import * as counts from './counts.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
const SENTINEL = '__field_coverage__'

// ---- generic ---------------------------------------------------------------

function leaves(v, p = []) {
  if (Array.isArray(v)) return v.length ? v.flatMap((x, i) => leaves(x, [...p, i])) : [p]
  if (v && typeof v === 'object') {
    const ks = Object.keys(v)
    return ks.length ? ks.flatMap((k) => leaves(v[k], [...p, k])) : [p]
  }
  return [p]
}
const show = (p) => p.map((k) => (typeof k === 'number' ? `[${k}]` : `.${k}`)).join('').replace(/^\./, '')
const pattern = (p) => show(p).replace(/\[\d+\]/g, '[*]')

function get(o, p) { return p.reduce((x, k) => x[k], o) }
// A value that breaks the property the field carries, chosen by type: a flipped
// boolean, a different number, a string no tool/context/path is called, an
// empty collection given a member (an empty `exclude` that gains one excludes).
function perturbed(obj, p) {
  const o = structuredClone(obj)
  const v = get(o, p)
  const set = (x) => { if (!p.length) return x; get(o, p.slice(0, -1))[p.at(-1)] = x; return o }
  if (typeof v === 'boolean') return set(!v)
  if (typeof v === 'number') return set(v + 1)
  if (typeof v === 'string') return set(SENTINEL)
  if (v === null) return set(SENTINEL)
  if (Array.isArray(v)) return set([SENTINEL])
  return set({ [SENTINEL]: SENTINEL })
}

// An IGNORE key without `*` names a field and everything under it.
function matches(glob, pat) {
  if (!glob.includes('*')) return pat === glob || pat.startsWith(glob + '.') || pat.startsWith(glob + '[')
  const re = new RegExp('^' + glob.replace(/\[\*\]/g, '\u0001').replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*\*/g, '\u0000').replace(/\*/g, '[^.\\[]*').replace(/\u0000/g, '.*').replace(/\u0001/g, '\\[\\*\\]') + '$')
  return re.test(pat)
}

function run(cmd, args, opts = {}) {
  return new Promise((resolve) => {
    const c = spawn(cmd, args, { cwd: ROOT, ...opts })
    let out = ''
    c.stdout.on('data', (d) => { out += d })
    c.stderr.on('data', (d) => { out += d })
    c.on('close', (code) => resolve({ code, out }))
  })
}

// ---- registrations ---------------------------------------------------------
//
// verdict(obj) -> 'red' | 'green' | 'skip:<why>' | 'error:<why>'

const HOOKS = {
  name: 'hooks',
  check: 'policy_lint.mjs --hooks',
  artifact: '.claude/settings.json',
  load: () => JSON.parse(fs.readFileSync(path.join(ROOT, '.claude/settings.json'), 'utf8')),
  ignore: {
    'permissions': 'tool permissions are not a hook; --hooks judges hooks and nothing else reads this key',
  },
  async verdict(obj) {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'fc-hooks-'))
    const f = path.join(tmp, 'settings.json')
    fs.writeFileSync(f, JSON.stringify(obj, null, 2))
    const { code, out } = await run('node', ['.claude/workflows/policy_lint.mjs', '--hooks', path.relative(ROOT, f)])
    fs.rmSync(tmp, { recursive: true, force: true })
    if (code === 0) return 'green'
    if (code === 1) return 'red'
    return `error:exit ${code}: ${out.trim().split('\n').pop()}`
  },
}

// The tree's only reader of the live ruleset is `counts.mjs:liveRequiredContexts`
// and the only comparison is `requiredContextsDrift`, run here unmodified in a
// fresh process (the reader memoizes) with `gh` answered from the object under
// test. The branch view is derived from that object, as GitHub derives it.
const GH_STUB = `#!/usr/bin/env node
const fs = require('fs')
const rs = JSON.parse(fs.readFileSync(process.env.FC_RULESET, 'utf8'))
const p = process.argv[3] || ''
if (/\\/rules\\/branches\\/main$/.test(p)) {
  process.stdout.write(JSON.stringify((rs.rules || []).map((r) => ({ ...r, ruleset_source_type: 'Repository', ruleset_source: rs.source, ruleset_id: rs.id }))))
} else if (/\\/rulesets\\/[^/]+$/.test(p)) {
  process.stdout.write(JSON.stringify(rs))
} else { process.stderr.write('gh stub: ' + p); process.exit(1) }
`
const RULESET_PROBE = `
import { liveRequiredContexts, liveRequiredContextsWhy, requiredContextsDrift } from ${JSON.stringify(pathToFileURL(path.join(HERE, 'counts.mjs')).href)}
import fs from 'node:fs'
const rel = '.claude/workflows/fixtures/required-contexts.json'
const fixture = JSON.parse(fs.readFileSync(process.env.FC_ROOT + '/' + rel, 'utf8'))
const live = liveRequiredContexts()
const drift = live == null ? [] : requiredContextsDrift(rel, fixture, live)
process.stdout.write(JSON.stringify({ live: live != null, why: liveRequiredContextsWhy(), drift: drift.length }))
`
let rulesetSource = null
const RULESET = {
  name: 'ruleset',
  check: 'counts.mjs liveRequiredContexts + requiredContextsDrift (policy-docs: required-contexts)',
  artifact: 'the live main-protect-checks ruleset object',
  load: () => {
    const raw = rulesetSource ? fs.readFileSync(rulesetSource, 'utf8')
      : execFileSync('gh', ['api', `repos/${ruleRepo()}/rulesets/${ruleId()}`], { encoding: 'utf8' })
    return JSON.parse(raw)
  },
  // What the comparison may ignore is the COMPARATOR's list, imported, never a
  // second copy (class I4). The fallback exists only because the base this
  // prototype runs on has no comparator for these fields at all.
  ignore: Object.fromEntries((counts.RULESET_VOLATILE || ['node_id', 'created_at', 'updated_at', '_links', 'current_user_can_bypass', 'source', 'source_type', 'name'])
    .map((k) => [k, 'GitHub rewrites it with no boundary change (RULESET_VOLATILE)'])),
  async verdict(obj) {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'fc-ruleset-'))
    fs.writeFileSync(path.join(tmp, 'ruleset.json'), JSON.stringify(obj))
    fs.writeFileSync(path.join(tmp, 'gh'), GH_STUB, { mode: 0o755 })
    fs.writeFileSync(path.join(tmp, 'probe.mjs'), RULESET_PROBE)
    const env = { ...process.env, PATH: `${tmp}:${process.env.PATH}`, FC_RULESET: path.join(tmp, 'ruleset.json'), FC_ROOT: ROOT }
    const { code, out } = await run('node', [path.join(tmp, 'probe.mjs')], { env })
    fs.rmSync(tmp, { recursive: true, force: true })
    if (code !== 0) return `error:probe exit ${code}: ${out.trim().split('\n').pop()}`
    const r = JSON.parse(out)
    if (!r.live) return `skip:${r.why}`
    return r.drift ? 'red' : 'green'
  },
}
function ruleFixture() { return JSON.parse(fs.readFileSync(path.join(ROOT, '.claude/workflows/fixtures/required-contexts.json'), 'utf8')) }
function ruleRepo() { return ruleFixture().branch_endpoint.replace(/^repos\//, '').replace(/\/rules\/branches\/main$/, '') }
function ruleId() { return ruleFixture().rulesets[0] }

// The per-file cap's input is the row `sizes()` measures for a capped file. The
// fields are that row's keys, read off the real function; each is perturbed by
// changing the FILE so that only that measurement moves.
let plMod = null
async function policyLint() {
  if (plMod) return plMod
  const src = fs.readFileSync(path.join(HERE, 'policy_lint.mjs'), 'utf8')
  // Prototype only: `checkBudgets` and `sizes` are not exported at this base.
  // The barrier pull request exports them; this does not edit policy_lint.mjs.
  const tmp = path.join(HERE, `.fc-policy-lint-${process.pid}.mjs`)
  fs.writeFileSync(tmp, src + '\nexport { checkBudgets as __fcCheckBudgets, sizes as __fcSizes, policyBudgets as __fcPolicyBudgets }\n')
  try { plMod = await import(pathToFileURL(tmp).href) } finally { fs.rmSync(tmp, { force: true }) }
  return plMod
}
const widen = (raw) => raw.split('\n').map((l) => (l ? l + ' ' + 'x'.repeat(60) : l)).join('\n')
// Past the recorded line cap: a field is read only if growth past its cap reddens.
const addLine = (raw, cap) => raw + 'x\n'.repeat(Math.max(1, cap - (raw.match(/\n/g) || []).length + 1))
const BUDGETS = {
  name: 'budgets',
  check: 'policy_lint.mjs checkBudgets, per-file arm',
  artifact: 'the sizes() row of every capped policy file',
  // Row keys and how the file is edited so that ONLY that key's value moves.
  edits: { lines: addLine, bytes: widen },
  ignore: {
    file: 'the row key itself, not a measurement',
    always: 'load class: the always_loaded_tokens aggregate reads it; a per-file cap is load-class-blind by design',
  },
}

async function budgetsRun(report) {
  const pl = await policyLint()
  const budget = pl.__fcPolicyBudgets()
  const BIG = 2 ** 52
  const files = Object.keys(budget.files).filter((f) => !f.startsWith('.claude/workflows/fixtures/'))
  const keys = Object.keys(pl.__fcSizes([files[0]])[0] || {})
  if (!keys.length || !files.length) { report.refused.push('budgets: enumerated no row keys or no capped file'); return }
  const tmpDir = fs.mkdtempSync(path.join(ROOT, '.fc-budgets-'))
  try {
    for (const key of keys) {
      if (key in BUDGETS.ignore) { report.ignored.push(`budgets ${key}: ${BUDGETS.ignore[key]}`); continue }
      const edit = BUDGETS.edits[key]
      if (!edit) { report.blind.push(`budgets row key \`${key}\`: no edit moves it and IGNORE does not name it`); continue }
      let blind = 0; let healthyRed = 0; let checked = 0
      for (const f of files) {
        const raw = fs.readFileSync(path.join(ROOT, f), 'utf8')
        const rel = path.relative(ROOT, path.join(tmpDir, f.replace(/\//g, '__')))
        // Budget object: the real one, the file's own cap under the temp name,
        // every aggregate out of reach, so only the per-file arm can answer.
        const b = { ...budget, files: { [rel]: budget.files[f] }, always_loaded_tokens: BIG, corpus_tokens: BIG,
          roles: Object.fromEntries(Object.entries(budget.roles || {}).map(([k, v]) => [k, { ...v, cap: BIG }])) }
        if (budget.files_tokens) b.files_tokens = { [rel]: budget.files_tokens[f] }
        fs.writeFileSync(path.join(ROOT, rel), raw)
        if (pl.__fcCheckBudgets([rel], b).some((x) => x.where === rel)) { healthyRed++; continue }
        const moved = edit(raw, budget.files[f])
        fs.writeFileSync(path.join(ROOT, rel), moved)
        const [r0] = pl.__fcSizes([f]); const [r1] = pl.__fcSizes([rel])
        // `bytes` must move alone (lines held); `lines` cannot move without
        // bytes, so for it only its own movement is required.
        const moved_ = keys.filter((k) => k !== 'file' && k !== 'always' && r0[k] !== r1[k])
        const ok = key === 'lines' ? moved_.includes('lines') : moved_.length === 1 && moved_[0] === key
        if (!ok) { report.refused.push(`budgets ${f}: the ${key} edit moved ${moved_.join(',') || 'nothing'}`); continue }
        checked++
        if (!pl.__fcCheckBudgets([rel], b).some((x) => x.where === rel)) blind++
      }
      report.runs += files.length
      if (healthyRed) report.refused.push(`budgets ${key}: ${healthyRed} capped file(s) already red unperturbed`)
      if (blind) report.blind.push(`budgets row key \`${key}\`: ${blind} of ${files.length} capped files grow in ${key} with the per-file check green`)
      else if (checked === files.length) report.read.push(`budgets ${key}: ${checked} of ${files.length} capped files reddened`)
      else report.refused.push(`budgets ${key}: only ${checked} of ${files.length} capped files could be measured`)
    }
  } finally { fs.rmSync(tmpDir, { recursive: true, force: true }) }
}

async function jsonRun(reg, report) {
  let base
  try { base = reg.load() } catch (e) { report.refused.push(`${reg.name}: cannot load ${reg.artifact}: ${String(e.message).split('\n')[0]}`); return }
  const v0 = await reg.verdict(base)
  if (v0 !== 'green') { report.refused.push(`${reg.name}: the unperturbed ${reg.artifact} is ${v0}, so nothing is measured`); return }
  const ls = leaves(base).filter((p) => p.length)
  if (!ls.length) { report.refused.push(`${reg.name}: enumerated zero fields`); return }
  const globs = Object.keys(reg.ignore)
  for (const g of globs) if (!ls.some((p) => matches(g, pattern(p)))) report.dead.push(`${reg.name}: IGNORE \`${g}\` matches no field of ${reg.artifact}`)
  const todo = ls.filter((p) => !globs.some((g) => matches(g, pattern(p))))
  report.ignored.push(...ls.filter((p) => globs.some((g) => matches(g, pattern(p)))).map((p) => `${reg.name} ${show(p)}`))
  const results = await Promise.all(todo.map(async (p) => [p, await reg.verdict(perturbed(base, p))]))
  report.runs += results.length + 1
  for (const [p, v] of results) {
    if (v === 'red') report.read.push(`${reg.name} ${show(p)}`)
    else if (v === 'green') report.blind.push(`${reg.name} \`${show(p)}\` = ${JSON.stringify(get(base, p))}: perturbed, ${reg.check} stays green`)
    else report.refused.push(`${reg.name} ${show(p)}: ${v} (a skip or an error is not a detection)`)
  }
}

async function main() {
  const argv = process.argv.slice(2)
  let only = null
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--only') only = argv[++i]
    else if (argv[i] === '--ruleset-json') rulesetSource = path.resolve(argv[++i])
    else { console.error(`usage: field_coverage.mjs [--only hooks|ruleset|budgets] [--ruleset-json FILE]`); process.exit(2) }
  }
  const t0 = Date.now()
  const report = { read: [], blind: [], dead: [], refused: [], ignored: [], runs: 0 }
  if (!only || only === 'hooks') await jsonRun(HOOKS, report)
  if (!only || only === 'ruleset') await jsonRun(RULESET, report)
  if (!only || only === 'budgets') await budgetsRun(report)
  for (const x of report.read) console.log(`  read     ${x}`)
  for (const x of report.ignored) console.log(`  ignored  ${x}`)
  for (const x of report.blind) console.log(`  BLIND    ${x}`)
  for (const x of report.dead) console.log(`  DEAD     ${x}`)
  for (const x of report.refused) console.log(`  REFUSED  ${x}`)
  const bad = report.blind.length + report.dead.length + report.refused.length
  console.log(`RESULT read=${report.read.length} ignored=${report.ignored.length} blind=${report.blind.length} dead=${report.dead.length} refused=${report.refused.length} runs=${report.runs} seconds=${((Date.now() - t0) / 1000).toFixed(1)}`)
  console.log(bad ? 'FIELD COVERAGE REFUSED: a field of a governance check\'s input is read by no check and ignored by no reason' : 'FIELD COVERAGE ok')
  process.exit(bad ? 1 : 0)
}

main()
