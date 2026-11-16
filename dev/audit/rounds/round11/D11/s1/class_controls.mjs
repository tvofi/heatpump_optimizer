#!/usr/bin/env node
// D11-s1 round 11: does every policy_lint.mjs check class have the control
// D11.md M1 names for it -- an arm of policy_lint_mutants.mjs -- and does the
// real acceptance refuse each class's emptied entry point?
//
// Metric (one line): of the per-file check functions lintFile() calls
// (checkCitations, checkNoGh -- the `citations` and `no-gh` classes of CHECKS),
// how many are absent from the mutants lane's two enumerations
// (CORPUS_CHECK_NAMES, LOOP_CHECK_NAMES); and, per class, whether
// assertAcceptance(derivations()) goes red with that function emptied.
// Count key: membership of the production export, and the production
// acceptance's return code on a mutant module.
//
// Run (from the export root):
//   node dev/audit/rounds/round11/D11/s1/class_controls.mjs
//   node dev/audit/rounds/round11/D11/s1/class_controls.mjs --perturb
// --perturb: the one-line edit adding checkCitations and checkNoGh to
// LOOP_CHECK_NAMES (as `{ name, file: 'policy_lint.mjs', kind: 'return' }`),
// applied to the imported list in memory; unlaned goes to 0 (down).
// Expected: RESULT unlaned=2 exact; RESULT acceptance_refuses_emptied=<n of 2>.
// Null control: the unmutated module's acceptance returns 0.
// Mutant modules are written beside policy_lint.mjs (it resolves its imports and
// ROOT relative to itself, as policy_lint_mutants.mjs's own are) and deleted in finally.
// Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
// Instrumented symbol: tools/policy/policy_lint.mjs:assertAcceptance,
// LOOP_CHECK_NAMES, CORPUS_CHECK_NAMES, checkCitations, checkNoGh.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

for (const v of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) process.env[v] ??= '1'
const ROOT = process.cwd()
const TMP = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd11s1-cc-'))
process.env.HPO_PLANDATA = path.join(TMP, 'pd')
const PERTURB = process.argv.includes('--perturb')
const DIR = path.join(ROOT, 'tools/policy')
const ENTRY = path.join(DIR, 'policy_lint.mjs')
const PER_FILE = ['checkCitations', 'checkNoGh']

const base = await import(pathToFileURL(ENTRY).href)
const loop = PERTURB
  ? [...base.LOOP_CHECK_NAMES, ...PER_FILE.map((name) => ({ name, file: 'policy_lint.mjs', kind: 'return' }))]
  : base.LOOP_CHECK_NAMES
const laned = new Set([...base.CORPUS_CHECK_NAMES, ...loop.map((e) => e.name)])
const unlaned = PER_FILE.filter((n) => !laned.has(n))

async function acceptance(url) {
  const real = console.log
  const said = []
  console.log = (...a) => said.push(a.join(' '))
  try {
    const m = await import(url)
    return { rc: m.assertAcceptance(m.derivations()), said }
  } finally { console.log = real }
}

const nul = await acceptance(pathToFileURL(ENTRY).href + '?null')
console.log(`null control: unmutated acceptance rc=${nul.rc}`)
const src = fs.readFileSync(ENTRY, 'utf8')
let refused = 0
for (const name of PER_FILE) {
  const re = new RegExp(`^(function ${name}\\([^)]*\\) \\{)$`, 'm')
  if (!re.test(src)) { console.log(`MUTATION DID NOT APPLY for ${name}`); process.exit(2) }
  const file = path.join(DIR, `.policy_lint.d11s1-${name}.mjs`)
  fs.writeFileSync(file, src.replace(re, '$1\n  return [] // MUTANT d11s1'))
  try {
    const r = await acceptance(pathToFileURL(file).href)
    const why = r.said.find((s) => /FIXTURE (VACUOUS|OVER-FIRES)/.test(s)) || ''
    if (r.rc) refused++
    console.log(`${name} emptied: acceptance rc=${r.rc}${r.rc ? `  (${why.trim().slice(0, 140)})` : '  <- SURVIVES'}  laned=${laned.has(name)}`)
  } finally { fs.rmSync(file, { force: true }) }
}
console.log(`RESULT per_file_classes=${PER_FILE.length} classes`)
console.log(`RESULT unlaned=${unlaned.length} classes`)
console.log(`RESULT acceptance_refuses_emptied=${refused} classes`)
console.log(`RESULT null_rc=${nul.rc} rc`)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let sw = 'n/a'
try { sw = fs.readFileSync('/proc/vmstat', 'utf8').split('\n').find((l) => l.startsWith('pswpin')).split(' ')[1] } catch {}
console.log(`RESULT swapins=${sw}`)
fs.rmSync(TMP, { recursive: true, force: true })
process.exit(0)
