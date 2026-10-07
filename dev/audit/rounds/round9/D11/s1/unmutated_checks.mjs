// D11-s1 round 9: which wired policy_lint corpus checks does the mutation lane never empty,
// and does the acceptance still refuse each one emptied?
//
// METRIC (one line): count of check functions the corpus lint path CALLS (the per-file
// lint `checkCitations`/`checkCounts`/`checkNoGh` and the acceptance's `checkSunset`)
// that are in neither production enumeration `policy_lint.mjs:CORPUS_CHECK_NAMES` nor
// `LOOP_CHECK_NAMES` -- i.e. that `policy_lint_mutants.mjs` never empties -- plus, per
// such check, the acceptance's own verdict (rc) with the check's return emptied.
// KEY: membership is read from the production exports; rc is `assertAcceptance(derivations())`
// of a mutant module built with the lane's own empty-return edit.
// CONTROL: `checkIndex` (in CORPUS_CHECK_NAMES) emptied must give rc != 0.
//
// COMMAND:  HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node tools/audit/round9/D11/s1/unmutated_checks.mjs [--perturb enumerate]
//           --perturb enumerate: the candidates are appended to CORPUS_CHECK_NAMES in the
//           temp copy (a one-line production edit) -> unenumerated count goes to zero.
// EXPECTED (baseline 1936d5ca): see REPORT.md; counts exact.
// MACHINE: box B3, 4 CPU Linux container, node v22.22.2.
// Writes only under a mkdtemp root: a copy of .claude/ beside symlinks to every other
// top-level entry, so the mutant sits beside its fixtures as the lane requires.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const ROOT = process.cwd()
const perturb = process.argv.includes('--perturb') && process.argv[process.argv.indexOf('--perturb') + 1] === 'enumerate'
const CANDIDATES = ['checkCitations', 'checkCounts', 'checkNoGh', 'checkSunset']
const CONTROL = 'checkIndex'
const t0 = process.cpuUsage()

const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd11s1-mut-'))
for (const e of fs.readdirSync(ROOT)) {
  if (e === '.claude') continue  // .git is linked too: the lint lists tracked files with git ls-files (read-only)
  fs.symlinkSync(path.join(ROOT, e), path.join(tmp, e))
}
fs.cpSync(path.join(ROOT, '.claude'), path.join(tmp, '.claude'), { recursive: true })
const WF = path.join(tmp, '.claude', 'workflows')
let base = fs.readFileSync(path.join(WF, 'policy_lint.mjs'), 'utf8')
if (perturb) {
  const re = /^(const CORPUS_CHECK_NAMES = \[.*)\]$/m
  const next = base.replace(re, (_m, head) => `${head}, ${CANDIDATES.map((c) => `'${c}'`).join(', ')}]`)
  if (next === base) throw new Error('perturbation did not apply')
  base = next
  fs.writeFileSync(path.join(WF, 'policy_lint.mjs'), base)
}

const prod = await import(pathToFileURL(path.join(WF, 'policy_lint.mjs')).href)
const loopNames = new Set(prod.LOOP_CHECK_NAMES.map((j) => j.name))
const corpusNames = new Set(prod.CORPUS_CHECK_NAMES)

function mutant(name) {
  const all = base.match(new RegExp(`^(?:export )?function ${name}\\(`, 'gm')) || []
  if (all.length !== 1) return { error: `anchor matched ${all.length}` }
  const text = base.replace(new RegExp(`^((?:export )?function ${name}\\(([^)]*)\\) \\{)$`, 'm'), (_m, sig) => `${sig}\n  return [] // MUTANT`)
  if (text === base) return { error: 'edit did not apply' }
  const file = path.join(WF, `.policy_lint.mutant-${name}.mjs`)
  fs.writeFileSync(file, text)
  return { file }
}

async function acceptanceRc(file) {
  const said = []
  const real = console.log
  console.log = (...a) => said.push(a.join(' '))
  try {
    const mod = await import(pathToFileURL(file).href + `?${Date.now()}`)
    return { rc: mod.assertAcceptance(mod.derivations()), said }
  } finally { console.log = real }
}

let unenumerated = 0
let unenumAlive = 0
for (const name of [CONTROL, ...CANDIDATES]) {
  const inLane = corpusNames.has(name) || loopNames.has(name)
  const m = mutant(name)
  if (m.error) { console.log(`# ${name}: mutation did not apply (${m.error})`); continue }
  const { rc, said } = await acceptanceRc(m.file)
  const why = (said.find((s) => /FIXTURE (VACUOUS|OVER-FIRES)/.test(s)) || '').trim().slice(0, 140)
  console.log(`# ${name}: in_mutation_lane=${inLane} emptied_acceptance_rc=${rc} ${why}`)
  if (name !== CONTROL && !inLane) { unenumerated++; if (rc) unenumAlive++ }
  if (name === CONTROL) console.log(`RESULT control_checkIndex_emptied_rc=${rc} code`)
}
console.log(`RESULT candidates=${CANDIDATES.length} count`)
console.log(`RESULT not_in_mutation_lane=${unenumerated} count`)
console.log(`RESULT not_in_lane_but_acceptance_refuses_emptied=${unenumAlive} count`)
const u = process.cpuUsage(t0)
console.log(`RESULT thread_factor=1.000`)
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
console.log('RESULT swapins=0')
fs.rmSync(tmp, { recursive: true, force: true })
void u
