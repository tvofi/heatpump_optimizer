// field_coverage.mjs -- every field a governance check's input carries is either
// READ by that check or IGNORED with a reason (round-9 class I3 barrier, from the
// root-cause seat's prototype at handoff/r9-rca-i3 844d14b7).
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
// a refusal. ONE exception, the ruleset arm's LOAD: the live object comes from
// the API, `policy-docs` runs this and is itself a required context, and an
// outage must not block every merge -- so an unreachable API prints the same
// UNCHECKED skip `required-contexts` prints and refuses nothing. Once loaded,
// the ruleset arm refuses like the others.
//
// THE CHECK SET IS DERIVED, NOT REGISTERED (tvofi's card C10). The set is
// policy_lint.mjs's CHECKS table, the programs codeowners_gap.py reports
// PINNED, and stamp.py's rule 4. Each entry of it is in DECLARED, naming the arm
// that covers its input or saying why it has none; an entry DECLARED lacks is
// REFUSED as unregistered, and a DECLARED key the set no longer yields is DEAD.
// So a new check is refused until someone says what it reads.
//
//   node .claude/workflows/field_coverage.mjs [--only hooks|ruleset|budgets|registry]
//        [--ruleset-json FILE]   # the live ruleset object; without it `gh api`
//
// exit 0: no BLIND, no DEAD, no refusal. exit 1 otherwise. exit 2: usage.

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { execFileSync, spawn, spawnSync } from 'node:child_process'
import { RULESET_VOLATILE } from './counts.mjs'
import { checkBudgets, sizes, policyBudgets, CHECKS } from './policy_lint.mjs'

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
  skipOnLoad: true,
  load: () => {
    const raw = rulesetSource ? fs.readFileSync(rulesetSource, 'utf8')
      : execFileSync('gh', ['api', `repos/${ruleRepo()}/rulesets/${ruleId()}`], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] })
    return JSON.parse(raw)
  },
  // What the comparison may ignore is the COMPARATOR's list, imported, never a
  // second copy (class I4).
  ignore: Object.fromEntries(RULESET_VOLATILE.map((k) => [k, 'GitHub rewrites it with no boundary change (RULESET_VOLATILE)'])),
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
  const budget = policyBudgets()
  const BIG = 2 ** 52
  const files = Object.keys(budget.files).filter((f) => !f.startsWith('.claude/workflows/fixtures/'))
  const keys = Object.keys(sizes([files[0]])[0] || {})
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
        if (checkBudgets([rel], b).some((x) => x.where === rel)) { healthyRed++; continue }
        const moved = edit(raw, budget.files[f])
        fs.writeFileSync(path.join(ROOT, rel), moved)
        const [r0] = sizes([f]); const [r1] = sizes([rel])
        // `bytes` must move alone (lines held); `lines` cannot move without
        // bytes, so for it only its own movement is required.
        const moved_ = keys.filter((k) => k !== 'file' && k !== 'always' && r0[k] !== r1[k])
        const ok = key === 'lines' ? moved_.includes('lines') : moved_.length === 1 && moved_[0] === key
        if (!ok) { report.refused.push(`budgets ${f}: the ${key} edit moved ${moved_.join(',') || 'nothing'}`); continue }
        checked++
        if (!checkBudgets([rel], b).some((x) => x.where === rel)) blind++
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
  try { base = reg.load() } catch (e) {
    const why = String(e.message).split('\n')[0]
    if (reg.skipOnLoad) { console.log(`  skip     ${reg.name}: cannot load ${reg.artifact} (${why}); its field coverage is UNCHECKED this run, not confirmed`); return }
    report.refused.push(`${reg.name}: cannot load ${reg.artifact}: ${why}`); return
  }
  const v0 = await reg.verdict(base)
  if (v0 !== 'green') { report.refused.push(`${reg.name}: ${reg.artifact}, unperturbed, is already ${v0}, so nothing is measured`); return }
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

// ---- the derived check set (tvofi's card C10) ------------------------------
//
// Each key is an entry the set yields; its value names the arm that covers the
// check's input, or `none` with the reason it has no arm here. A reason that
// names a structured input is a residual on the record, not a claim of cover.
const ARMS = ['hooks', 'ruleset', 'budgets']
const PROSE = 'reads policy prose, not a structured input'
const DECLARED = {
  'check citations': { none: PROSE },
  'check counts': { none: PROSE },
  'check no-gh': { none: PROSE },
  'check budgets': { arm: 'budgets' },
  'check orphan-caps': { none: 'reads the key set of policy_budgets.json files{} against the tree, no field of an entry' },
  'check index': { none: PROSE },
  'check duplicates': { none: PROSE },
  'check pr-body': { none: 'reads a pull-request body, prose; its head field is pr-contract\'s (F11.2)' },
  'check named-docs': { none: PROSE },
  'check citation-presence': { none: PROSE },
  'check coverage': { none: 'reads the tracked file list against POLICY_GLOBS, not a structured input' },
  'check provenance': { none: 'reads recorded_at of policy_known_bad.json; residual, no arm here' },
  'check required-contexts': { arm: 'ruleset' },
  'check row-freeze': { none: 'reads the plan\'s delivery table, prose' },
  'check rule-binding': { none: 'reads rule frontmatter paths: against the tree; residual, no arm here' },
  'check record': { none: 'reads merge history, not a structured input' },
  'check render': { none: PROSE },
  'check stats': { none: 'a report; refuses nothing' },
  'check sunset': { none: PROSE },
  'pinned .claude/workflows/brief_lint.mjs': { none: 'reads the wave rosters and carries; residual, no arm here' },
  'pinned .claude/workflows/check-wave-script.mjs': { none: 'drives the wave script\'s branches, code not data' },
  'pinned .claude/workflows/counts.mjs': { arm: 'ruleset' },
  'pinned .claude/workflows/field_coverage.mjs': { none: 'this program; its input is DECLARED and the arms above' },
  'pinned .claude/workflows/figure_lint.mjs': { none: 'reads a body\'s figures, prose' },
  'pinned .claude/workflows/fragments_sync.mjs': { none: 'byte-compares fragments, no field to skip' },
  'pinned .claude/workflows/policy_lint.mjs': { arm: 'hooks' },
  'pinned .claude/workflows/policy_lint_envmatrix.mjs': { none: 'models clone shapes, code not data' },
  'pinned .claude/workflows/render_md.mjs': { none: PROSE },
  'pinned .claude/workflows/rules_sync.mjs': { none: 'byte-compares generated rules, no field to skip' },
  'pinned .claude/workflows/vendor/markdown-it.min.js': { none: 'a vendored parser, not a check' },
  'pinned tests/coverage_ratchet.py': { none: 'reads the coverage budget file; residual, no arm here' },
  'pinned tools/audit/preflight.sh': { none: 'runs other checks; no input of its own' },
  'pinned tools/audit/prepr.sh': { none: 'runs other checks over a body; no input of its own' },
  'pinned tools/audit/round6/D11/fix/codeowners_gap.py': { none: 'reads CODEOWNERS and workflows; residual (D11-s1-03), no arm here' },
  'stamp rule 4': { none: 'reads commit parents and subjects; residual (D11-s1-02), no arm here' },
}

function derivedSet(report) {
  const set = CHECKS.map((c) => `check ${c.name}`)
  const cg = spawnSync('python3', ['-I', 'tools/audit/round6/D11/fix/codeowners_gap.py'], { cwd: ROOT, encoding: 'utf8' })
  const pinned = [...new Set((cg.stdout || '').split('\n').map((l) => /^#\s+PINNED (\S+)$/.exec(l)).filter(Boolean).map((m) => m[1]))]
  if (cg.status !== 0 || !pinned.length) report.refused.push(`registry: codeowners_gap.py yielded no PINNED program (exit ${cg.status})`)
  set.push(...pinned.map((f) => `pinned ${f}`))
  const stamp = fs.readFileSync(path.join(ROOT, 'tools/release/stamp.py'), 'utf8')
  if (/^def rule4_problem\(/m.test(stamp)) set.push('stamp rule 4')
  else report.refused.push('registry: tools/release/stamp.py defines no rule4_problem, so rule 4 is not in the set')
  return set
}

function registryRun(report) {
  const set = derivedSet(report)
  for (const k of set) {
    const d = DECLARED[k]
    if (!d) report.refused.push(`registry: \`${k}\` is unregistered: DECLARED names neither an arm for its input nor none`)
    else if (d.arm && !ARMS.includes(d.arm)) report.refused.push(`registry: \`${k}\` names arm \`${d.arm}\`, which does not exist`)
    else if (d.arm) report.read.push(`registry ${k}: arm ${d.arm}`)
    else if (typeof d.none === 'string' && d.none.trim()) report.none.push(`${k}: ${d.none}`)
    else report.refused.push(`registry: \`${k}\` declares neither an arm nor a reason`)
  }
  for (const k of Object.keys(DECLARED)) if (!set.includes(k)) report.dead.push(`registry: DECLARED \`${k}\` is no longer in the derived set`)
}

async function main() {
  const argv = process.argv.slice(2)
  let only = null
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--only') only = argv[++i]
    else if (argv[i] === '--ruleset-json') rulesetSource = path.resolve(argv[++i])
    else { console.error(`usage: field_coverage.mjs [--only hooks|ruleset|budgets|registry] [--ruleset-json FILE]`); process.exit(2) }
  }
  if (only && !['hooks', 'ruleset', 'budgets', 'registry'].includes(only)) { console.error(`--only ${only}: no such arm`); process.exit(2) }
  const t0 = Date.now()
  const report = { read: [], blind: [], dead: [], refused: [], ignored: [], none: [], runs: 0 }
  if (!only || only === 'hooks') await jsonRun(HOOKS, report)
  if (!only || only === 'ruleset') await jsonRun(RULESET, report)
  if (!only || only === 'budgets') await budgetsRun(report)
  if (!only || only === 'registry') registryRun(report)
  for (const x of report.read) console.log(`  read     ${x}`)
  for (const x of report.ignored) console.log(`  ignored  ${x}`)
  for (const x of report.none) console.log(`  none     ${x}`)
  for (const x of report.blind) console.log(`  BLIND    ${x}`)
  for (const x of report.dead) console.log(`  DEAD     ${x}`)
  for (const x of report.refused) console.log(`  REFUSED  ${x}`)
  const bad = report.blind.length + report.dead.length + report.refused.length
  console.log(`RESULT read=${report.read.length} ignored=${report.ignored.length} declared_none=${report.none.length} blind=${report.blind.length} dead=${report.dead.length} refused=${report.refused.length} runs=${report.runs} seconds=${((Date.now() - t0) / 1000).toFixed(1)}`)
  console.log(bad ? 'FIELD COVERAGE REFUSED: a BLIND field, a DEAD entry or a REFUSED run above' : 'FIELD COVERAGE ok')
  process.exit(bad ? 1 : 0)
}

main()
