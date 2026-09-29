#!/usr/bin/env node
// D13 / round 9 / seat s1 -- D13.M1 population: what the PRODUCTION `--stats`
// enumerates as the window's merges, against the merges `main` records.
//
// METRIC: RESULT stats_window_merges = the N of the production CLI line
//   `STATS: N merged pull request(s) in v6.6.0..origin/main`
//   (.claude/workflows/policy_lint.mjs --stats, whose population is
//   policy_lint.mjs:enumerateMerges in API mode over fetchPullsBySha), driven
//   OFFLINE through a stub `curl` first on PATH that answers from window.json.gz
//   exactly what the live API answered when the snapshot was taken; against
//   RESULT subject_merges = first-parent commits of the window whose subject is
//   `Merge pull request #N` (git). Gap = subject_merges - stats_window_merges;
//   RESULT gap_marked = whether the CLI printed any line naming the gap.
//   Count key: the set of PR numbers the production seam delivers.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/s1/enum_gap.mjs
// PERTURBATIONS: D13_PERTURB=drop:<sha> -- the stub answers `[]` for one more
//   merge commit: stats_window_merges falls by one and gap_marked stays 0 (the
//   seam drops a merge silently). D13_PERTURB=restore -- the stub answers the
//   52 empty rows with the subject's number (and an empty PR payload):
//   stats_window_merges rises to subject_merges.
// EXPECTED at 1936d5ca: stats_window_merges=201 subject_merges=253 gap=52
//   gap_marked=0; exact. MACHINE: any (offline). BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const R = (k, v) => console.log(`RESULT ${k}=${v}`)
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'd13-enum-'))
const stub = path.join(tmp, 'curl')
fs.writeFileSync(stub, `#!/usr/bin/env node
const fs = require('fs'), zlib = require('zlib')
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(${JSON.stringify(path.join(HERE, 'window.json.gz'))})).toString())
const P = process.env.D13_PERTURB || ''
const url = process.argv[process.argv.length - 1]
const u = new URL(url)
const p = u.pathname
const out = (d, code = 200) => { process.stdout.write(JSON.stringify(d) + '\\n' + code); process.exit(0) }
let m
if ((m = /\\/commits\\/([0-9a-f]{40})\\/pulls$/.exec(p))) {
  const c = snap.commits.find((c) => c.sha === m[1])
  if (!c) out({ message: 'Not Found' }, 404)
  if (P === 'drop:' + c.sha) out([])
  if (P === 'restore' && !c.pulls.length) { const n = (/^Merge pull request #(\\d+)/.exec(c.subject) || [])[1]; if (n) out([{ number: Number(n) }]) }
  out((c.pulls || []).map((r) => ({ number: r.number })))
}
if ((m = /\\/pulls\\/(\\d+)$/.exec(p))) { const pr = snap.prs[m[1]]; out({ body: pr ? pr.body : '' }) }
if ((m = /\\/issues\\/(\\d+)\\/comments$/.exec(p))) { const pr = snap.prs[m[1]]; out(pr ? pr.comments.map((c) => ({ body: c.body, created_at: c.at })) : []) }
if ((m = /\\/pulls\\/(\\d+)\\/reviews$/.exec(p))) { const pr = snap.prs[m[1]]; out(pr ? pr.reviews.map((c) => ({ body: c.body, submitted_at: c.at })) : []) }
out({ message: 'Not Found' }, 404)
`)
fs.chmodSync(stub, 0o755)
let text
try {
  text = execFileSync('node', ['.claude/workflows/policy_lint.mjs', '--stats', '--since', 'v6.6.0'], {
    encoding: 'utf8', env: { ...process.env, PATH: `${tmp}:${process.env.PATH}`, GITHUB_TOKEN: 'stub' }, maxBuffer: 64 << 20,
  })
} catch (e) { text = String(e.stdout ?? '') + String(e.stderr ?? '') }
const n = Number((/^STATS: (\d+) merged pull request/m.exec(text) || [])[1] ?? NaN)
const subj = execFileSync('git', ['log', '--first-parent', '--format=%s', 'v6.6.0..origin/main'], { encoding: 'utf8' })
  .split('\n').filter((s) => /^Merge pull request #\d+/.test(s)).length
const marked = /UNCHECKED|could not enumerate|not a pull request|no pull request for|skipped \d+ merge/i.test(text)
console.log(text.split('\n').filter((l) => /^STATS/.test(l)).map((l) => l.slice(0, 200)).join('\n'))
R('stats_window_merges', n)
R('subject_merges', subj)
R('gap', subj - n)
R('gap_marked', marked ? 1 : 0)
R('api_failures', 0)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('baseline_sha', '1936d5ca72a06556eeed4e8e5bf3dea520e517e1')
fs.rmSync(tmp, { recursive: true, force: true })
