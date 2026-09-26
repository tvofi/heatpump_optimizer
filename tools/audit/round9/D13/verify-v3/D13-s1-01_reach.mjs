#!/usr/bin/env node
// D13 / round 9 / verifier V3 (reach and class) -- D13-s1-01.
//
// METRIC: over v6.6.0..1936d5ca, through the PRODUCTION CLI of
//   .claude/workflows/policy_lint.mjs in its two other window consumers the
//   finder's harness does not drive (--record, and the population --stats
//   shares with it), with a stub `curl` that answers /commits/<sha>/pulls from
//   the finder's live-API snapshot (tools/audit/round9/D13/s1/window.json.gz):
//   RESULT record_enumerated   = N of `TOTAL: e error(s) over N merged pull request(s)`
//   RESULT record_errors       = e (merges with no disposition)
//   RESULT dropped_prs         = subject-numbered merges whose snapshot row is []
//   RESULT dropped_with_delivery_row = of those, how many have docs/delivery/<N>.md
//   RESULT dropped_undispositioned   = record errors that appear ONLY in the
//                                      restore arm (merges --record hides)
//   RESULT unchecked_marker    = 1 if the as-is arm prints UNCHECKED / enum skip
//   Arms: as-is (stub replays []), restore (stub answers the subject's #N).
// COMMAND (repository root): HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v3/D13-s1-01_reach.mjs
//   It makes its own `git clone --shared` under $TMPDIR with origin/main pinned
//   to the baseline (origin/main in the shared checkout has moved on) and an
//   origin URL naming the GitHub slug; no network is used.
// PERTURBATION: the restore arm is the perturbation; record_enumerated must
//   rise by dropped_prs' distinct count.
// EXPECTED at 1936d5ca: see the verifier report; exact (closed snapshot).
// BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: any (offline).
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import zlib from 'node:zlib'
import { execFileSync } from 'node:child_process'

const BASE = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
const ROOT = process.cwd()
const R = (k, v) => console.log(`RESULT ${k}=${v}`)
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(ROOT, 'tools/audit/round9/D13/s1/window.json.gz'))).toString())
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd13v3-'))
const clone = path.join(tmp, 'repo')
const g = (args, cwd = clone) => execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
g(['clone', '-q', '--shared', '--no-checkout', ROOT, clone], ROOT)
g(['checkout', '-q', '--detach', g(['rev-parse', 'HEAD'], ROOT).trim()])
g(['update-ref', 'refs/remotes/origin/main', BASE])
g(['remote', 'set-url', 'origin', 'https://github.com/tvofi/heatpump_optimizer.git'])

const subjNum = (s) => (/^Merge pull request #(\d+)/.exec(s) || [])[1]
const dropped = snap.commits.filter((c) => c.pulls && !c.pulls.length && subjNum(c.subject)).map((c) => subjNum(c.subject))
const maps = {}
for (const arm of ['asis', 'restore']) {
  const m = {}
  for (const c of snap.commits) {
    if (c.pulls && c.pulls.length) m[c.sha] = [{ number: c.pulls[0].number }]
    else if (arm === 'restore' && subjNum(c.subject)) m[c.sha] = [{ number: Number(subjNum(c.subject)) }]
    else m[c.sha] = []
  }
  maps[arm] = path.join(tmp, `${arm}.json`)
  fs.writeFileSync(maps[arm], JSON.stringify(m))
}
const bin = path.join(tmp, 'bin')
fs.mkdirSync(bin)
fs.writeFileSync(path.join(bin, 'curl'), `#!/usr/bin/env node
const m = JSON.parse(require('fs').readFileSync(process.env.D13V3_MAP, 'utf8'))
const u = new URL(process.argv[process.argv.length - 1])
const k = /\\/commits\\/([0-9a-f]{40})\\/pulls$/.exec(u.pathname)
if (k && k[1] in m) { process.stdout.write(JSON.stringify(m[k[1]]) + '\\n200'); process.exit(0) }
process.stdout.write('{"message":"Not Found"}\\n404')
`)
fs.chmodSync(path.join(bin, 'curl'), 0o755)

const run = (arm) => {
  let t
  try {
    t = execFileSync('node', ['.claude/workflows/policy_lint.mjs', '--record', '--since', 'v6.6.0'], {
      cwd: clone, encoding: 'utf8', maxBuffer: 64 << 20,
      env: { ...process.env, PATH: `${bin}:${process.env.PATH}`, GITHUB_TOKEN: 'stub', D13V3_MAP: maps[arm] },
    })
  } catch (e) { t = String(e.stdout ?? '') + String(e.stderr ?? '') }
  const tot = /TOTAL: (\d+) error\(s\) over (\d+) merged pull request/.exec(t) || []
  const errs = new Set([...t.matchAll(/no disposition[^#]*#(\d+)/g)].map((x) => x[1]))
  return { t, errors: Number(tot[1]), n: Number(tot[2]), errs, marker: /UNCHECKED|merge-enumeration/.test(t) ? 1 : 0, enumLine: (/^RECORD_ENUM:.*$/m.exec(t) || [''])[0] }
}
const a = run('asis')
const b = run('restore')
const hidden = [...b.errs].filter((n) => !a.errs.has(n))
console.log(`asis ${a.enumLine}; restore ${b.enumLine}`)
R('record_enumerated_asis', a.n)
R('record_enumerated_restore', b.n)
R('record_errors_asis', a.errors)
R('record_errors_restore', b.errors)
R('unchecked_marker_asis', a.marker)
R('dropped_prs', new Set(dropped).size)
R('dropped_with_delivery_row', [...new Set(dropped)].filter((n) => fs.existsSync(path.join(ROOT, 'docs/delivery', `${n}.md`))).length)
R('dropped_undispositioned', hidden.length)
console.log(`hidden_undispositioned: ${hidden.join(' ')}`)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('swapins', 0)
fs.rmSync(tmp, { recursive: true, force: true })
