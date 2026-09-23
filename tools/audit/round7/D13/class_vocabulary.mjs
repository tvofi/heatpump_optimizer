#!/usr/bin/env node
/**
 * D13-05 — a block class reviewers write, that `VERDICT_CLASSES` does not teach:
 * two readers of the same verdict, disagreeing about its class.
 *
 * METRIC (one line): over the round-7 window's real `blocked` verdict first
 * lines, the number for which `policy_lint.mjs:statsHistogram`'s cell key and
 * `web-fix-wave.js:parseVerdict`'s routed `class` are DIFFERENT strings --
 * i.e. the histogram reports a block class the wave does not have and the wave
 * routes a repair on a class the histogram does not print.
 *
 * COMMAND:  node tools/audit/round7/D13/class_vocabulary.mjs
 *           node tools/audit/round7/D13/class_vocabulary.mjs --perturb
 * EXPECTED: `RESULT blocked_verdicts_disagreeing_route=1 count` over the
 *           window's 2 blocked verdicts (0 under --perturb, which adds the word
 *           to `VERDICT_CLASSES`), and the control row -- the taught class --
 *           disagreeing in BOTH arms.
 * BASELINE: f9d6f78243fa65f6fa128d2357752a2ae7f60648
 * MACHINE:  Apple M1, 8-core, 8 GB, macOS 25.6.0 — shared audit box (fan-out).
 *
 * HOW IT WORKS. Both production readers are driven, not re-implemented:
 *   - `statsHistogram` is imported from `policy_lint.mjs` and called with one
 *     fixture comment per verdict line; the cell it lands in is its key.
 *   - `parseVerdict` is EXTRACTED from `web-fix-wave.js` as source and
 *     evaluated with that file's own `VERDICT_RE` and `VERDICT_CLASSES` bound
 *     (`web-fix-wave.js` runs a wave at import, so it cannot be imported; the
 *     slice is the function itself, not a paraphrase of its routing).
 *   - `VERDICT_CLASSES` and `VERDICT_RE` are read by evaluating the literals
 *     the file writes -- the technique `verdictClasses` / `blockClasses`
 *     already use for the same two halves of this grammar.
 *
 * THE FIXTURE IS THE WINDOW, NOT A BATTERY. The two lines are the round-7
 * window's `Fix review: blocked` first lines verbatim; `yield_rounds.py`
 * enumerates them from `/issues/<n>/comments` over `v6.6.9..f9d6f782` and
 * prints them under `== output 3: block classes ==`, so the population this
 * harness reasons over is re-derivable and the fixture is not a claim.
 *
 * NULL CONTROL: `root-cause-unanswered` is in `VERDICT_CLASSES`, so both
 * readers must agree on its line in BOTH arms -- a disagreement count of 1 is
 * then not "both readers disagree about everything".
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
const WORD = 'product-tradeoff-regression'

// The window's blocked verdicts, verbatim (yield_rounds.py prints these).
const BLOCKED = [
  ['1418', 'root-cause-unanswered',
    'Fix review: blocked 16491d4411b9fd1df80a88f7178198bf6a759509 root-cause-unanswered: fast (3.14) went red, unanswered'],
  ['1429', WORD,
    'Fix review: blocked 0e6de6f7f66741cadbb5b45266d38889f0bbc905 product-tradeoff-regression: blanket default-off'],
]

const waveText = fs.readFileSync(WAVE, 'utf8')

function extractRe() {
  const key = 'const VERDICT_RE = '
  const start = waveText.indexOf(key) + key.length
  const end = waveText.indexOf('\n)', start) + 2
  if (start < key.length || end < 2) throw new Error('could not extract VERDICT_RE')
  // eslint-disable-next-line no-eval
  return eval(waveText.slice(start, end))
}
function extractClasses() {
  const key = 'const VERDICT_CLASSES = ['
  const start = waveText.indexOf(key)
  if (start < 0) throw new Error('could not extract VERDICT_CLASSES')
  const end = waveText.indexOf('\n]', start) + 2
  // eslint-disable-next-line no-eval
  return eval(waveText.slice(start + 'const VERDICT_CLASSES = '.length, end))
}
function extractParseVerdict(re, classes) {
  const key = 'function parseVerdict(review) {'
  const start = waveText.indexOf(key)
  if (start < 0) throw new Error('could not extract parseVerdict')
  let depth = 0
  let end = -1
  for (let i = waveText.indexOf('{', start); i < waveText.length; i += 1) {
    if (waveText[i] === '{') depth += 1
    else if (waveText[i] === '}') { depth -= 1; if (depth === 0) { end = i + 1; break } }
  }
  if (end < 0) throw new Error('parseVerdict braces did not balance')
  // eslint-disable-next-line no-new-func
  return new Function('VERDICT_RE', 'VERDICT_CLASSES',
    `${waveText.slice(start, end)}\nreturn parseVerdict`)(re, classes)
}

const VERDICT_RE = extractRe()
const VERDICT_CLASSES = extractClasses()
const classes = [...new Set(['merge', 'blocked', ...VERDICT_CLASSES])]
const parseVerdict = extractParseVerdict(VERDICT_RE, VERDICT_CLASSES)

const { statsHistogram } = await import(pathToFileURL(LINT).href)

function histKey(line) {
  const prs = [{ pr: 7002 }]
  const fetched = new Map([[7002, { body: '', comments: [{ body: line }] }]])
  const h = statsHistogram(prs, fetched, classes)
  const words = [...h.verdicts.keys()]
  return { key: words.join('+') || null, unclassified: h.unclassified.length > 0 }
}

function rows() {
  return BLOCKED.map(([pr, expectedWord, line]) => {
    const h = histKey(line)
    let route = null
    let why = null
    try {
      const p = parseVerdict({ comment: line })
      route = p.class
      why = p.why
    } catch (e) {
      route = `THREW: ${String(e.message).slice(0, 60)}`
    }
    return { pr, expectedWord, line, hist: h, route, why,
             disagree: h.key !== route, taught: VERDICT_CLASSES.includes(expectedWord) }
  })
}

function report(rws, tag) {
  for (const r of rws) {
    console.log(`BLOCKED\t#${r.pr}\texpected=${r.expectedWord}\ttaught=${r.taught ? 1 : 0}`
      + `\thist_key=${r.hist.key ?? '-'}\twave_route=${r.route}\tdisagree=${r.disagree ? 1 : 0}`)
  }
  console.log(`RESULT blocked_verdicts_${tag}=${rws.length} count`)
  console.log(`RESULT blocked_verdicts_disagreeing_route_${tag}=${rws.filter((r) => r.disagree).length} count`)
  console.log(`RESULT blocked_verdicts_with_an_untaught_class_${tag}=${rws.filter((r) => !r.taught).length} count`)
  console.log(`RESULT control_taught_class_rows_${tag}=${rws.filter((r) => r.taught).length} count`)
  console.log(`RESULT control_taught_class_rows_agreeing_${tag}=${rws.filter((r) => r.taught && !r.disagree).length} count`)
  return rws.filter((r) => r.disagree).map((r) => `#${r.pr}`).join(',')
}

console.log(`HARNESS class_vocabulary — root=${ROOT} VERDICT_CLASSES=${JSON.stringify(VERDICT_CLASSES)}`)
const un = rows()
console.log(`# disagreeing rows (unperturbed): ${report(un, 'unperturbed')}`)

if (PERTURB && !argv.includes('--one-shot')) {
  // The one-line production edit: teach the wave the class the reviewer wrote.
  // Run in a FRESH child, because `parseVerdict` is already built in this
  // process and an edit here would leave the number unmoved.
  const before = fs.readFileSync(WAVE, 'utf8')
  const anchor = "'class-open', 'conflict', 'other',"
  if (!before.includes(anchor)) throw new Error(`anchor not found in web-fix-wave.js: ${anchor}`)
  fs.writeFileSync(WAVE, before.replace(anchor, `'preflight-mismatch', 'class-open', 'conflict', '${WORD}', 'other',`))
  let child = null
  try {
    child = spawnSync(process.execPath, [fileURLToPath(import.meta.url), '--one-shot'], { cwd: ROOT, encoding: 'utf8' })
  } finally {
    fs.writeFileSync(WAVE, before)
    if (fs.readFileSync(WAVE, 'utf8') !== before) throw new Error('FAILED to restore web-fix-wave.js')
  }
  if (!child || child.status !== 0) throw new Error(`perturbed child failed: ${child && child.stderr}`)
  for (const line of (child.stdout || '').split('\n')) {
    if (line.startsWith('BLOCKED\t')) console.log(`# perturbed ${line}`)
    const m = line.match(/^RESULT (\S+?)=(\S+) (\S+)$/)
    if (m) console.log(`RESULT ${m[1]}_PERTURBED=${m[2]} ${m[3]}`)
  }
  console.log(`RESULT wave_script_restored=${fs.readFileSync(WAVE, 'utf8') === before} bool`)
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
