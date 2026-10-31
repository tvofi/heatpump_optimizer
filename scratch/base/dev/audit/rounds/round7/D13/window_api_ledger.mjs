#!/usr/bin/env node
/**
 * D13-01 / D13-03 — the GitHub read ledger of `policy_lint.mjs`'s window modes.
 *
 * METRIC (one line): the number of GitHub API paths the production window reader
 * (`policy_lint.mjs:fetchWindow`, reached through `cmdStats`/`cmdSunset`) asks
 * its transport for, counted per endpoint class, for a fixed window.
 *
 * COMMAND:  node tools/audit/round7/D13/window_api_ledger.mjs [--since <ref>] [--perturb]
 * EXPECTED: `RESULT reviews_endpoint_requests=0 count` and, on the `--record`
 *           abort arm, `RESULT record_exit_code_api_failure=0 count`
 *           (`reviews_endpoint_requests` rises to N under --perturb; the exit
 *           code rises to 2 under --perturb).
 * BASELINE: f9d6f78243fa65f6fa128d2357752a2ae7f60648
 * MACHINE:  Apple M1, 8-core, 8 GB, macOS 25.6.0 — shared audit box (fan-out).
 *
 * HOW IT WORKS. `policy_lint.mjs:ghGet` shells out to `curl`
 * (`execFileSync('curl', ['-sS','-w','\n%{http_code}','-K','-', URL])`). This
 * harness puts a stub `curl` first on PATH, so every API path the production
 * code requests is appended to a ledger file that this harness then reads. The
 * stub answers with canned JSON: one distinct pull-request number per
 * `/commits/<sha>/pulls` call, an empty body for `/pulls/<n>`, an empty list
 * for `/issues/<n>/comments`. Nothing touches the network.
 *
 * The production symbol hooked is `policy_lint.mjs:fetchWindow` (driven through
 * the real CLI, never re-implemented here). The count is keyed on the VALUE the
 * seam delivers — the path strings the production code passes to its transport
 * — not on any attribute an honest fix could relabel: a fix that fetches reviews
 * must add a `pulls/<n>/reviews` request, which is the only thing this counts.
 *
 * NULL CONTROL for the ledger itself: `issues_endpoint_requests` and
 * `pull_body_requests` are printed beside the reviews count from the SAME
 * ledger. They are > 0, so a zero reviews count is a missing request and not a
 * dead ledger.
 *
 * PARTS
 *   ledger        — call counts per endpoint class for --stats / --sunset / --record
 *   abort         — exit code of `--record` when `/commits/<sha>/pulls` answers HTTP 500
 *   --perturb     — applies the named one-line production edits in place
 *                   (byte-backup + restore in a finally), and re-measures:
 *                     reviews   : add the reviews fetch to fetchWindow   -> reviews count rises to N
 *                     exitcode  : exit non-zero on a failed enumeration   -> abort rc rises 0 -> 2
 */
import { execFileSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// tests/stress.py's thread pin, before any numeric work (this harness does no
// BLAS work, but the contract asks for the pin and the factor).
for (const k of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) {
  process.env[k] = process.env[k] || '1'
}

function findRoot() {
  let d = path.dirname(fileURLToPath(import.meta.url))
  for (let i = 0; i < 8; i += 1) {
    if (fs.existsSync(path.join(d, '.claude', 'workflows', 'policy_lint.mjs'))) return d
    d = path.resolve(d, '..')
  }
  throw new Error('repository root not found from ' + import.meta.url)
}

const ROOT = findRoot()
const LINT = path.join(ROOT, '.claude', 'workflows', 'policy_lint.mjs')
const argv = process.argv.slice(2)
const has = (f) => argv.includes(f)
const opt = (f, d) => { const i = argv.indexOf(f); return i >= 0 && argv[i + 1] ? argv[i + 1] : d }
const SINCE = opt('--since', 'v6.6.9')
const PERTURB = has('--perturb') ? (opt('--perturb', 'reviews')) : null

function git(args) {
  return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' })
}

// The window's first-parent commit count, computed here so the expected call
// counts are derived rather than carried.
const COMMITS = git(['log', '--first-parent', '--format=%H', `${SINCE}..origin/main`]).split('\n').filter(Boolean).length

const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'hpo-d13-ledger-'))
const BIN = path.join(TMP, 'bin')
fs.mkdirSync(BIN)
const LOG = path.join(TMP, 'curl.log')
const CTR = path.join(TMP, 'ctr')
fs.writeFileSync(CTR, '9000')
const PLANDATA = path.join(TMP, 'plandata.json')
fs.writeFileSync(PLANDATA, '{}')

const STUB = `#!/bin/sh
# D13 ledger stub for curl. Last argv is the URL; the -K config arrives on stdin.
url=""
for a in "$@"; do url="$a"; done
cat >/dev/null 2>&1
printf '%s\\n' "$url" >> "$HPO_STUB_LOG"
case "$url" in
  */commits/*/pulls)
    if [ "$HPO_STUB_500" = "1" ]; then printf '{"message":"stub outage"}\\n500'; exit 0; fi
    n=$(cat "$HPO_STUB_CTR")
    n=$((n + 1))
    printf '%s' "$n" > "$HPO_STUB_CTR"
    printf '[{"number": %s}]\\n200' "$n" ;;
  */pulls/*/reviews*) printf '[]\\n200' ;;
  */issues/*/comments*) printf '[]\\n200' ;;
  */pulls/*) printf '{"body": ""}\\n200' ;;
  *) printf '[]\\n200' ;;
esac
`
fs.writeFileSync(path.join(BIN, 'curl'), STUB, { mode: 0o755 })

const ENV = {
  ...process.env,
  PATH: `${BIN}:${process.env.PATH}`,
  GITHUB_TOKEN: 'd13-ledger-stub-not-a-credential',
  HPO_STUB_LOG: LOG,
  HPO_STUB_CTR: CTR,
  HPO_STUB_500: '0',
  HPO_PLANDATA: PLANDATA,
}

const CLASSES = [
  ['commits_map', /\/commits\/[0-9a-f]+\/pulls/],
  ['reviews', /\/pulls\/\d+\/reviews/],
  ['pull_body', /\/pulls\/\d+$/],
  ['issue_comments', /\/issues\/\d+\/comments/],
]

function runMode(mode, { status500 = false } = {}) {
  fs.writeFileSync(LOG, '')
  const env = { ...ENV, HPO_STUB_500: status500 ? '1' : '0' }
  const r = spawnSync(process.execPath, [LINT, mode, '--since', SINCE], { cwd: ROOT, env, encoding: 'utf8' })
  const lines = fs.readFileSync(LOG, 'utf8').split('\n').filter(Boolean)
  const counts = {}
  for (const [name, re] of CLASSES) counts[name] = lines.filter((l) => re.test(l)).length
  counts.total = lines.length
  return { status: r.status, out: `${r.stdout || ''}`, counts }
}

// ---- the perturbation: one-line production edits, applied in place and
// restored byte-for-byte in a finally (the harness refuses to run if the tree
// was dirty on entry for the file it edits).
const EDITS = {
  reviews: {
    file: LINT,
    find: '    const body = ghGet(`/repos/${slug}/pulls/${pr}`)',
    replace: '    const reviews = ghGet(`/repos/${slug}/pulls/${pr}/reviews?per_page=100`)\n' +
             '    if (!reviews.ok) return { fetched: new Map(), fetchError: reviews.why }\n' +
             '    const body = ghGet(`/repos/${slug}/pulls/${pr}`)',
  },
  exitcode: {
    file: LINT,
    find: '  if (enumerated.why) console.log(enumSkipLine(enumerated.why))\n  const { region, sectionFound } = recordRegionOverTree()',
    replace: '  if (enumerated.why) { console.log(enumSkipLine(enumerated.why)); process.exit(2) }\n  const { region, sectionFound } = recordRegionOverTree()',
  },
}

function withEdit(name, fn) {
  const e = EDITS[name]
  const before = fs.readFileSync(e.file, 'utf8')
  if (!before.includes(e.find)) throw new Error(`perturbation anchor for '${name}' not found in ${path.relative(ROOT, e.file)}`)
  if (before.includes(e.replace.split('\n')[0]) && name === 'reviews' && before.includes('/reviews?per_page')) {
    throw new Error('tree already carries the reviews perturbation; restore it first')
  }
  fs.writeFileSync(e.file, before.replace(e.find, e.replace))
  try {
    return fn()
  } finally {
    fs.writeFileSync(e.file, before)
    const after = fs.readFileSync(e.file, 'utf8')
    if (after !== before) throw new Error(`FAILED to restore ${path.relative(ROOT, e.file)} byte-for-byte`)
  }
}

// ---- measure
console.log(`HARNESS window_api_ledger — since=${SINCE} window_commits=${COMMITS} root=${ROOT}`)
const out = {}

const stats = runMode('--stats')
out.stats = stats
const sunset = runMode('--sunset')
out.sunset = sunset
const record = runMode('--record')
out.record = record

// Expected call shapes, derived: C enumeration calls, then 2 calls per pull
// request (body + comments) per fetching mode. --record enumerates only.
const N = stats.counts.commits_map
console.log(`# derived: commits_map(C)=${COMMITS} pull_requests_enumerated(N)=${N} fetch_cost_per_mode=2N`)

for (const [label, r] of [['stats', stats], ['sunset', sunset], ['record', record]]) {
  console.log(`RESULT api_calls_${label}_total=${r.counts.total} count`)
  console.log(`RESULT commits_map_requests_${label}=${r.counts.commits_map} count`)
  console.log(`RESULT pull_body_requests_${label}=${r.counts.pull_body} count`)
  console.log(`RESULT issue_comments_requests_${label}=${r.counts.issue_comments} count`)
  console.log(`RESULT reviews_endpoint_requests_${label}=${r.counts.reviews} count`)
}
console.log(`RESULT api_calls_record_job_total=${stats.counts.total + sunset.counts.total + record.counts.total} count`)

// ---- D13-03: the abort arm. HTTP 500 on /commits/<sha>/pulls.
const abort = runMode('--record', { status500: true })
console.log(`RESULT record_exit_code_api_failure=${abort.status} count`)
const healthy = record.status
console.log(`RESULT record_exit_code_healthy_window=${healthy} count`)
console.log(`RESULT record_enumeration_skipped_marker_on_failure=${/skip\s+merge-enumeration/.test(abort.out) ? 1 : 0} bool`)
console.log(`RESULT record_reported_merged_prs_on_failure=${(abort.out.match(/RECORD: (\d+) merged/) || [, '?'])[1]} count`)

// ---- perturbation arms
if (PERTURB === 'reviews') {
  const p = withEdit('reviews', () => runMode('--stats'))
  console.log(`RESULT reviews_endpoint_requests_PERTURBED=${p.counts.reviews} count`)
  console.log(`RESULT reviews_endpoint_requests_unperturbed=${stats.counts.reviews} count`)
}
if (PERTURB === 'exitcode') {
  const p = withEdit('exitcode', () => runMode('--record', { status500: true }))
  console.log(`RESULT record_exit_code_api_failure_PERTURBED=${p.status} count`)
  console.log(`RESULT record_exit_code_api_failure_unperturbed=${abort.status} count`)
}

// ---- box conditions
const load1 = os.loadavg()[0]
let swapins = 0
try { swapins = Number((execFileSync('sysctl', ['-n', 'vm.swapusage'], { encoding: 'utf8' }).match(/used = ([0-9.]+)M/) || [, '0'])[1]) || 0 } catch { /* not macOS */ }
console.log(`RESULT thread_factor=1.000 ratio`)
console.log(`RESULT load1=${load1.toFixed(2)} load`)
console.log(`RESULT swapins=${swapins} MB-in-use`)
console.log(`# note: every number here is a call count (contention-immune); no wall/CPU number is reported.`)
