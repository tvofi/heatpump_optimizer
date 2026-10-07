#!/usr/bin/env node
/**
 * D13-02 — `statsHistogram`'s verdict grammar against the wave's own `VERDICT_RE`.
 *
 * METRIC (one line): over a fixed battery of `Fix review:` first lines, the
 * number of lines the production histogram counts as a verdict CLASS
 * (`policy_lint.mjs:statsHistogram`) but the production grammar
 * (`web-fix-wave.js:VERDICT_RE`) refuses to parse.
 *
 * COMMAND:  node tools/audit/round7/D13/verdict_grammar.mjs [--since <ref>]
 *           node tools/audit/round7/D13/verdict_grammar.mjs --perturb
 * EXPECTED: `RESULT shapes_counted_by_histogram_but_refused_by_wave=7 count`
 *           (5 under --perturb). The two control rows below must hold in both:
 *           the in-grammar merge and blocked shapes are counted by BOTH.
 * BASELINE: f9d6f78243fa65f6fa128d2357752a2ae7f60648
 * MACHINE:  Apple M1, 8-core, 8 GB, macOS 25.6.0 — shared audit box (fan-out).
 *
 * HOW IT WORKS. The two production symbols are both driven, never
 * re-implemented:
 *   - `statsHistogram` is imported from `policy_lint.mjs` and called with one
 *     fixture comment per shape; the word it lands in (and whether it fell into
 *     `unclassified`) is read from its return value.
 *   - `web-fix-wave.js:VERDICT_RE` is built by evaluating the expression the
 *     file itself writes (`const VERDICT_RE = new RegExp(...)`), the same
 *     read-the-literal-from-the-file technique `verdictClasses`/`blockClasses`
 *     already use for the two halves of this grammar.
 *   The histogram's `classes` input is taken from the production CLI's own
 *   header line (`STATS: ... verdict grammar [...]`) rather than typed here.
 *
 * The count is keyed on the VALUE the histogram delivers: for each shape the
 * harness records which verdict cell (or `unclassified`) `statsHistogram`
 * returned for that shape's first line. A fix that makes the histogram classify
 * exactly the wave's grammar moves shapes off the divergence row by name.
 *
 * NULL CONTROL: two shapes are IN both grammars (a 40-hex merge, a 40-hex
 * blocked with a class). They must be counted by both, so a divergence count is
 * not simply "everything refuses everything".
 */
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

for (const k of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) {
  process.env[k] = process.env[k] || '1'
}

function findRoot() {
  let d = path.dirname(fileURLToPath(import.meta.url))
  for (let i = 0; i < 8; i += 1) {
    if (fs.existsSync(path.join(d, '.claude', 'workflows', 'policy_lint.mjs'))) return d
    d = path.resolve(d, '..')
  }
  throw new Error('repository root not found')
}
const ROOT = findRoot()
const LINT = path.join(ROOT, '.claude', 'workflows', 'policy_lint.mjs')
const WAVE = path.join(ROOT, '.claude', 'workflows', 'web-fix-wave.js')
const argv = process.argv.slice(2)
const PERTURB = argv.includes('--perturb')
const SINCE = (() => { const i = argv.indexOf('--since'); return i >= 0 && argv[i + 1] ? argv[i + 1] : 'v6.6.9' })()

const SHA40 = '0123456789abcdef0123456789abcdef01234567'
const SHA12 = '0123456789ab'

// ---- the battery. [label, first line, in_wave_grammar_expected]
const BATTERY = [
  ['merge-full-sha', `Fix review: merge ${SHA40}`, true],
  ['blocked-full-sha-class', `Fix review: blocked ${SHA40} mutation-vacuous: the mutant survived`, true],
  ['merge-no-sha', 'Fix review: merge', false],
  ['merge-short-sha', `Fix review: merge ${SHA12}`, false],
  ['merge-uppercase-word', `Fix review: MERGE ${SHA40}`, false],
  ['merge-uppercase-no-sha', 'Fix review: MERGE', false],
  ['merge-no-space', `Fix review:merge ${SHA40}`, false],
  ['merge-trailing-text', `Fix review: merge ${SHA40} please land it`, false],
  ['blocked-no-sha', 'Fix review: blocked', false],
  ['blocked-short-sha', `Fix review: blocked ${SHA12}`, false],
  ['pass-merge-hybrid', `Fix review: PASS — merge ${SHA40}`, false],
  ['blocked-uppercase-word', `Fix review: BLOCKED ${SHA40} mutation-vacuous: the mutant survived`, false],
]

// ---- production inputs
const classes = (() => {
  const env = { ...process.env }
  delete env.GITHUB_TOKEN
  delete env.GH_TOKEN
  const r = spawnSync(process.execPath, [LINT, '--stats', '--since', SINCE], { cwd: ROOT, env, encoding: 'utf8' })
  const m = (r.stdout || '').match(/verdict grammar (\[[^\]]*\])/)
  if (!m) throw new Error('could not read the verdict grammar from the production header line')
  return JSON.parse(m[1])
})()

const waveRe = (() => {
  const text = fs.readFileSync(WAVE, 'utf8')
  const key = 'const VERDICT_RE = '
  const start = text.indexOf(key) + key.length
  const end = text.indexOf('\n)', start) + 2
  if (start < key.length || end < 2) throw new Error('could not extract VERDICT_RE from web-fix-wave.js')
  // eslint-disable-next-line no-eval
  return eval(text.slice(start, end))
})()

const { statsHistogram } = await import(pathToFileURL(LINT).href)

// ---- drive both symbols over the battery
function histogramOf(line) {
  const prs = [{ pr: 7001 }]
  const fetched = new Map([[7001, { body: '', comments: [{ body: line }] }]])
  const h = statsHistogram(prs, fetched, classes)
  const words = [...h.verdicts.keys()]
  return { words, accepted: words.length > 0, unclassified: h.unclassified.length > 0 }
}

// ---- the one-line production edit under test: drop the case-insensitive flag
// from the histogram's regex, so the two grammars agree about case. The count
// must fall by exactly the shapes that differ ONLY in case.
function withFlagDropped(fn) {
  const before = fs.readFileSync(LINT, 'utf8')
  const lines = before.split('\n')
  const idx = lines.findIndex((l) => l.includes('const re = new RegExp(`^Fix review:'))
  if (idx < 0) throw new Error("the histogram's regex construction was not found; the anchor is stale")
  if (!/, 'i'\)\s*$/.test(lines[idx])) throw new Error(`anchor line does not end in ", 'i')": ${lines[idx]}`)
  lines[idx] = lines[idx].replace(/, 'i'\)\s*$/, ')')
  fs.writeFileSync(LINT, lines.join('\n'))
  try { return fn() } finally {
    fs.writeFileSync(LINT, before)
    if (fs.readFileSync(LINT, 'utf8') !== before) throw new Error('FAILED to restore policy_lint.mjs')
  }
}

function battery() {
  const rows = BATTERY.map(([label, line, expectedInWave]) => {
    const wave = waveRe.test(line)
    const h = histogramOf(line)
    return { label, wave, expectedInWave, hist: h, diverge: h.accepted && !wave }
  })
  return rows
}

console.log(`HARNESS verdict_grammar — root=${ROOT} classes=${JSON.stringify(classes)}`)

function report(rows, tag) {
  for (const r of rows) {
    console.log(`SHAPE\t${r.label}\twave_accepts=${r.wave ? 1 : 0}\thist_words=${r.hist.words.join('+') || '-'}\thist_unclassified=${r.hist.unclassified ? 1 : 0}\tdiverge=${r.diverge ? 1 : 0}`)
  }
  const diverge = rows.filter((r) => r.diverge)
  console.log(`RESULT shapes_${tag}_total=${rows.length} count`)
  console.log(`RESULT shapes_counted_by_histogram_but_refused_by_wave_${tag}=${diverge.length} count`)
  console.log(`RESULT control_shapes_in_both_grammars_${tag}=${rows.filter((r) => r.wave && r.hist.accepted).length} count`)
  console.log(`RESULT control_shapes_refused_by_both_${tag}=${rows.filter((r) => !r.wave && !r.hist.accepted).length} count`)
  // The internal asymmetry: the merge arm takes a sha-less line, the blocked
  // arm in the same function does not.
  const mergeNoSha = rows.find((r) => r.label === 'merge-no-sha')
  const blockedNoSha = rows.find((r) => r.label === 'blocked-no-sha')
  console.log(`RESULT hist_accepts_sha_less_merge_${tag}=${mergeNoSha.hist.accepted ? 1 : 0} bool`)
  console.log(`RESULT hist_accepts_sha_less_blocked_${tag}=${blockedNoSha.hist.accepted ? 1 : 0} bool`)
  return diverge.map((r) => r.label).join(',')
}

const un = battery()
console.log(`# divergent shapes (unperturbed): ${report(un, 'unperturbed')}`)

if (PERTURB && !argv.includes('--one-shot')) {
  // The perturbation must be measured by a process that LOADS the edited file:
  // `statsHistogram` is already in this module's import cache, so an edit here
  // would leave the number unmoved (measured: it did). A fresh child, spawned
  // while the edit is on disk, is the honest arm.
  let child = null
  withFlagDropped(() => {
    child = spawnSync(process.execPath, [fileURLToPath(import.meta.url), '--one-shot', '--since', SINCE], { cwd: ROOT, encoding: 'utf8' })
  })
  if (!child || child.status !== 0) throw new Error(`perturbed child failed: ${child && child.stderr}`)
  for (const line of (child.stdout || '').split('\n')) {
    if (line.startsWith('SHAPE\t')) console.log(`# perturbed ${line}`)
    const m = line.match(/^RESULT (\S+?)=(\S+) (\S+)$/)
    if (m) console.log(`RESULT ${m[1]}_PERTURBED=${m[2]} ${m[3]}`)
  }
}

const load1 = os.loadavg()[0]
let swapins = 0
try {
  const su = spawnSync('sysctl', ['-n', 'vm.swapusage'], { encoding: 'utf8' })
  swapins = Number(((su.stdout || '').match(/used = ([0-9.]+)M/) || [, '0'])[1]) || 0
} catch { /* not macOS */ }
console.log(`RESULT thread_factor=1.000 ratio`)
console.log(`RESULT load1=${load1.toFixed(2)} load`)
console.log(`RESULT swapins=${swapins} MB-in-use`)
console.log(`# note: every number here is a count (contention-immune); no wall/CPU number is reported.`)
