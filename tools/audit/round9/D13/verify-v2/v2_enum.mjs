#!/usr/bin/env node
// D13 round 9, verifier V2 (independent), finding D13-s1-01.
// METRIC (V2's own): the set of PR numbers the PRODUCTION enumerator
//   policy_lint.mjs:enumerateMerges delivers in API mode over the recorded
//   /commits/<sha>/pulls rows (window.json.gz, finder's snapshot), against the
//   set of N in first-parent subjects `Merge pull request #N` of
//   v6.6.0..1936d5ca (git, explicit SHA -- not origin/main, which moves).
//   enumerateMerges is not exported: its source text is cut from the file and
//   evaluated, so the production body is what runs (a one-line edit to it moves
//   the number). Key: PR-number set, never totals.
//   RESULT dropped = |subject set - API set|; dropped_two_parent = those whose
//   commit has 2 parents in git (a real merge, not a stamp); skipped_total =
//   first-parent commits the enumerator skipped (stamps + dropped).
//   Silence: RESULT silent_skip_lines = number of lines in policy_lint.mjs's
//   cmdStats/enumerateMerges/fetchPullsBySha source that could print a skipped
//   commit (grep for console.log inside those three functions) -- 0 = silent.
// NULL CONTROL: RESULT subject_mode_count = the same production function in
//   subject mode (pullsBySha=null) -- its end-anchored (#N) regex matches none
//   of this repository's merge subjects, so it is not a fallback that recovers
//   the 52; and RESULT api_with_subject_fill = API map plus the subject's N for
//   empty rows -> equals the subject set when the gap is exactly the empty rows.
// PERTURBATION: V2_PERTURB=body -- the production source's `continue` on an
//   unmapped sha is replaced by a subject fallback in memory: dropped -> 0.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v2/v2_enum.mjs
// EXPECTED: dropped=52 +-0 (count; contention-immune). BASELINE SHA
//   1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: cloud box G1-V2, 4 vCPU
//   Linux, node 22, CPython 3.14.0rc2 (not used). No numpy: thread pin moot,
//   thread_factor printed as 1 (single-threaded node, count metric).
process.env.OMP_NUM_THREADS ??= '1'; process.env.OPENBLAS_NUM_THREADS ??= '1'
import fs from 'node:fs'
import os from 'node:os'
import zlib from 'node:zlib'
import { execFileSync } from 'node:child_process'
const R = (k, v, u = '') => console.log(`RESULT ${k}=${v}${u ? ' ' + u : ''}`)
const BASE = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
const src = fs.readFileSync('.claude/workflows/policy_lint.mjs', 'utf8')
const cut = (name) => {
  const i = src.indexOf(`function ${name}(`)
  let depth = 0, j = src.indexOf('{', i)
  for (let k = j; k < src.length; k++) { if (src[k] === '{') depth++; else if (src[k] === '}' && --depth === 0) return src.slice(i, k + 1) }
}
const reLine = src.split('\n').find((l) => l.startsWith('const MERGE_SUBJECT_RE'))
let body = cut('enumerateMerges')
if (process.env.V2_PERTURB === 'body') {
  const before = body
  body = body.replace("if (raw == null || raw === '') continue", "if (raw == null || raw === '') { const mm = /^Merge pull request #(\\d+)/.exec(subject); if (!mm) continue; pr = mm[1] } else")
  if (before === body) throw new Error('perturbation did not apply')
}
const enumerateMerges = new Function(`${reLine}\n${body}\nreturn enumerateMerges`)()
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const git = (...a) => execFileSync('git', a, { encoding: 'utf8' })
const fp = git('log', '--first-parent', '--format=%H%x09%P%x09%s', `v6.6.0..${BASE}`).split('\n').filter(Boolean)
  .map((l) => { const [sha, par, subject] = l.split('\t'); return { sha, parents: par.split(' ').length, subject } })
const bySha = new Map(snap.commits.map((c) => [c.sha, c]))
const missing = fp.filter((c) => !bySha.has(c.sha)).length
const map = new Map()
for (const c of fp) { const rows = bySha.get(c.sha)?.pulls ?? []; if (rows.length) map.set(c.sha, rows[0].number) }
const api = enumerateMerges(fp.map(({ sha, subject }) => ({ sha, subject })), map)
const apiSet = new Set(api.prs.map((p) => p.pr))
const subj = new Map()
for (const c of fp) { const m = /^Merge pull request #(\d+)/.exec(c.subject); if (m) subj.set(m[1], c) }
const dropped = [...subj.keys()].filter((n) => !apiSet.has(n)).map(Number).sort((a, b) => a - b)
const extra = [...apiSet].filter((n) => !subj.has(n))
const subjMode = enumerateMerges(fp.map(({ sha, subject }) => ({ sha, subject })), null)
const fill = new Map(map)
for (const c of fp) if (!fill.has(c.sha)) { const m = /^Merge pull request #(\d+)/.exec(c.subject); if (m) fill.set(c.sha, Number(m[1])) }
const filled = enumerateMerges(fp.map(({ sha, subject }) => ({ sha, subject })), fill)
let silent = 0
for (const f of ['enumerateMerges', 'fetchPullsBySha', 'mergedPRsFromWindow']) silent += (cut(f).match(/console\.log/g) || []).length
R('first_parent_commits', fp.length)
R('snapshot_missing_commits', missing)
R('subject_merges', subj.size)
R('api_enumerated', apiSet.size)
R('dropped', dropped.length, `PRs #${dropped[0]}..#${dropped[dropped.length - 1]}`)
R('dropped_two_parent', dropped.filter((n) => subj.get(String(n)).parents === 2).length)
R('api_only_not_subject', extra.length)
R('skipped_total', fp.length - api.prs.length)
R('silent_skip_lines', silent)
R('subject_mode_count', subjMode.prs.length)
R('api_with_subject_fill', filled.prs.length)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1)
R('swapins', (fs.readFileSync('/proc/vmstat', 'utf8').match(/^pswpin (\d+)/m) || [])[1] ?? 'na')
