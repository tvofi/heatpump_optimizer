#!/usr/bin/env node
// D13 / round 9 / verifier V3 (reach and class) -- D13-s1-03.
//
// METRIC (mine): blocked verdicts in the finder's live-API snapshot
//   (tools/audit/round9/D13/s1/window.json.gz), population = PRs the API maps a
//   first-parent merge of v6.6.0..1936d5ca to; a verdict = any line of an issue
//   comment or review matching `Fix review: blocked <40-hex> <word>:` (backticks
//   stripped), an exact repeat (same PR, head, word) dropped. Counted two ways:
//   RESULT blocks_<word> (verdicts) and RESULT prs_<word> (distinct PRs), so a
//   class inflated by one PR blocked repeatedly shows. RESULT body_answer_prs =
//   distinct PRs blocked as root-cause-unanswered or red-check;
//   RESULT body_answer_head_red = of those verdicts, how many whose PR's
//   recorded head check-runs (runs_head) hold a `failure` conclusion (whether the
//   API data the proposed pre-review check would read shows the red check).
// COMMAND (repository root): node tools/audit/round9/D13/verify-v3/D13-s1-03_blocks.mjs
// PERTURBATION: D13V3_PERTURB=dup -- the first root-cause-unanswered verdict is
//   posted twice on a new head in memory: blocks_root-cause-unanswered +1,
//   prs_root-cause-unanswered unchanged.
// BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: any (offline).
import fs from 'node:fs'
import os from 'node:os'
import zlib from 'node:zlib'

const R = (k, v) => console.log(`RESULT ${k}=${v}`)
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const pop = new Set(snap.commits.filter((c) => c.pulls && c.pulls.length).map((c) => String(c.pulls[0].number)))
const BR = /^Fix review:\s+blocked\s+([0-9a-f]{40})(?:\s+([a-z][a-z0-9-]*)\s*:|\s*:|\s*$)(.*)$/
const rows = []
for (const n of pop) {
  const p = snap.prs[n]
  if (!p) continue
  const seen = new Set()
  for (const c of [...(p.comments || []), ...(p.reviews || [])]) {
    for (const raw of String(c.body || '').split('\n')) {
      const m = BR.exec(raw.replace(/`/g, '').trim())
      if (!m) continue
      const k = `${m[1]}|${m[2] || 'none'}`
      if (seen.has(k)) continue
      seen.add(k)
      rows.push({ pr: n, head: m[1], word: m[2] || 'none', rest: m[3].slice(0, 110), p })
    }
  }
}
if (process.env.D13V3_PERTURB === 'dup') {
  const r = rows.find((x) => x.word === 'root-cause-unanswered')
  if (r) rows.push({ ...r, head: 'f'.repeat(40) })
}
const by = {}
for (const r of rows) { (by[r.word] ??= { v: 0, prs: new Set() }).v++; by[r.word].prs.add(r.pr) }
for (const [w, x] of Object.entries(by).sort()) { R(`blocks_${w}`, x.v); R(`prs_${w}`, x.prs.size) }
const BODY = ['root-cause-unanswered', 'red-check']
const body = rows.filter((r) => BODY.includes(r.word))
for (const r of body) console.log(`body-answer #${r.pr} ${r.head.slice(0, 8)} ${r.word}: ${r.rest}`)
R('blocked_verdicts', rows.length)
R('body_answer_verdicts', body.length)
R('body_answer_prs', new Set(body.map((r) => r.pr)).size)
R('body_answer_head_red', body.filter((r) => (r.p.runs_head || []).some((x) => x.conclusion === 'failure')).length)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('swapins', 0)
