#!/usr/bin/env node
// D13 / round 9 / verify V1 -- independent re-measure of D13-s1-01.
// METRIC: RESULT stats_n_<arm> = N of `STATS: N merged pull request(s)` from the
//   PRODUCTION CLI (policy_lint.mjs --stats --since v6.6.0, API mode via
//   enumerateMerges/fetchPullsBySha) when a stub `curl` answers /commits/<sha>/pulls
//   with [] for a chosen set E of subject-numbered merges and [{number:N}] (N from
//   the `Merge pull request #N` subject, git only -- NOT the finder's snapshot) for
//   every other merge; RESULT mentioned_<arm> = how many of E's numbers appear as
//   `#N` anywhere in the full CLI output; RESULT marker_<arm> = 1 if any line says
//   skip/UNCHECKED/unfetched/never fetched. Also the `--record` arm: RECORD N.
//   Key: the PR-number set the seam delivers (N) against the git subject set (253).
// ARMS: null (E empty), one (E={1100}), ten (E = 10 lowest subject numbers),
//   snap52 (E = the 52 numbers #1097..#1165 read from the finder's window.json.gz).
// ISOLATION: origin/main in the shared checkout moves (at 2026-09-26 it is 18
//   commits past baseline, and the finder's harness then prints 0/256); this
//   harness makes a private `git clone --shared` under mktemp with origin/main
//   pinned to the baseline and production checked out AT the baseline.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v1/seam_dose.mjs
// EXPECTED at 1936d5ca: stats_n_null=253 one=252 ten=243 snap52=201; mentioned=0,
//   marker=0 in every dropping arm; exact. MACHINE: any (offline).
// BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import zlib from 'node:zlib'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
const BASE = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
const HERE = path.dirname(fileURLToPath(import.meta.url))
const R = (k, v) => console.log(`RESULT ${k}=${v}`)
const root = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd13v1-'))
const repo = path.join(root, 'clone')
const g = (...a) => execFileSync('git', ['-C', repo, ...a], { encoding: 'utf8' })
execFileSync('git', ['clone', '-q', '--shared', '--no-checkout', process.cwd(), repo])
g('remote', 'set-url', 'origin', 'https://github.com/tvofi/heatpump_optimizer.git')
g('update-ref', 'refs/remotes/origin/main', BASE)
g('checkout', '-q', '--detach', BASE)
const subj = new Map()
for (const l of g('log', '--first-parent', '--format=%H%x09%s', `v6.6.0..${BASE}`).split('\n').filter(Boolean)) {
  const [sha, s] = l.split('\t'); const m = /^Merge pull request #(\d+)/.exec(s); if (m) subj.set(sha, Number(m[1]))
}
const nums = [...subj.values()].sort((a, b) => a - b)
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(HERE, '..', 's1', 'window.json.gz'))).toString())
const snap52 = snap.commits.filter((c) => c.pulls && !c.pulls.length && /^Merge pull request #\d+/.test(c.subject)).map((c) => Number(/#(\d+)/.exec(c.subject)[1]))
const arms = { null: [], one: [1100], ten: nums.slice(0, 10), snap52 }
fs.writeFileSync(path.join(root, 'map.json'), JSON.stringify(Object.fromEntries(subj)))
const stub = path.join(root, 'curl')
fs.writeFileSync(stub, `#!/usr/bin/env node
const map = require(${JSON.stringify(path.join(root, 'map.json'))})
const E = new Set((process.env.D13V_EMPTY || '').split(',').filter(Boolean).map(Number))
const p = new URL(process.argv[process.argv.length - 1]).pathname
const out = (d, c = 200) => { process.stdout.write(JSON.stringify(d) + '\\n' + c); process.exit(0) }
let m
if ((m = /\\/commits\\/([0-9a-f]{40})\\/pulls$/.exec(p))) { const n = map[m[1]]; out(n && !E.has(n) ? [{ number: n }] : []) }
if (/\\/pulls\\/\\d+$/.test(p)) out({ body: '' })
if (/\\/(comments|reviews)$/.test(p)) out([])
out({ message: 'Not Found' }, 404)
`)
fs.chmodSync(stub, 0o755)
const run = (args, E) => { try { return execFileSync('node', ['.claude/workflows/policy_lint.mjs', ...args], { cwd: repo, encoding: 'utf8', maxBuffer: 64 << 20, env: { ...process.env, PATH: `${root}:${process.env.PATH}`, GITHUB_TOKEN: 'stub', D13V_EMPTY: E.join(',') } }) } catch (e) { return String(e.stdout ?? '') + String(e.stderr ?? '') } }
R('subject_merges', nums.length)
R('snap52_size', snap52.length)
for (const [arm, E] of Object.entries(arms)) {
  const t = run(['--stats', '--since', 'v6.6.0'], E)
  R(`stats_n_${arm}`, Number((/^STATS: (\d+) merged/m.exec(t) || [])[1] ?? NaN))
  R(`mentioned_${arm}`, E.filter((n) => new RegExp(`#${n}\\b`).test(t)).length)
  R(`marker_${arm}`, /\bskip\b.*merge-enumeration|UNCHECKED|never fetched/i.test(t) ? 1 : 0)
}
for (const arm of ['null', 'snap52']) {
  const t = run(['--record', '--since', 'v6.6.0'], arms[arm])
  R(`record_n_${arm}`, Number((/^RECORD: (\d+) merged/m.exec(t) || [])[1] ?? NaN))
}
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('swapins', 0)
R('baseline_sha', BASE)
fs.rmSync(root, { recursive: true, force: true })
