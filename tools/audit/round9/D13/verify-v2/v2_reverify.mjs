#!/usr/bin/env node
// D13 round 9, verifier V2 (independent), finding D13-s1-02.
// METRIC (V2's own): over the finder's recorded verdict population
//   (window.json.gz, both endpoints), every verdict parsed by the PRODUCTION
//   parser policy_lint.mjs:waveVerdictRe that follows a `merge` verdict on the
//   same PR naming a DIFFERENT head (a re-verification round). Per round, the
//   branch's NET diff at each head -- `git diff $(git merge-base <head> <M>^1) <head>`,
//   M = the PR's merge commit, so <M>^1 is main just before the merge (a head is
//   an ancestor of 1936d5ca itself, so a merge base with the baseline is the head
//   and every diff would be empty) -- is keyed by `git patch-id --stable`: RESULT reverify_net_diff_equal =
//   rounds whose net diff is byte-equivalent at both heads (a move that changed
//   nothing the review read), reverify_net_diff_changed = the rest.
//   RESULT reverify_u0_plusminus_equal = the same with a context-free key
//   (git diff -U0, +/- lines and file headers only, sha1).
//   RESULT finder_no_content_rounds = rounds the finder's rule (first-parent
//   prev..head has only merges / only `ci:` commits) calls content-free, and
//   finder_no_content_rounds_u0_equal = how many of those keep the -U0 key.
//   RESULT reverify_blocked = rounds whose verdict is blocked; and, for the
//   rounds with a changed net diff, whether any LATER verdict on that PR was
//   blocked (RESULT changed_rounds_later_blocked) -- a miss the merge vote let through.
//   Key: the verdict word the production regex delivers.
// NULL CONTROL: RESULT repair_rounds / repair_blocked_or_merge -- verdicts after a
//   `blocked` verdict (where catches are expected to be 0 by construction? no:
//   repair rounds end in merge by construction); printed for scale only.
//   RESULT first_verdicts_blocked = PRs whose FIRST verdict was blocked: the
//   yield of a first review, the arm where the mechanism does catch.
// PERTURBATION: V2_PERTURB=flip -- the first re-verification round's verdict
//   text is rewritten to `Fix review: blocked <its head> harness: x` in memory
//   -> reverify_blocked 0 -> 1.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v2/v2_reverify.mjs
// EXPECTED: reverify_rounds=22, reverify_blocked=0 +-0 (counts). BASELINE SHA
//   1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: cloud box G1-V2, 4 vCPU
//   Linux, node 22, CPython 3.14.0rc2 (not used); no numpy, thread_factor 1.
process.env.OMP_NUM_THREADS ??= '1'; process.env.OPENBLAS_NUM_THREADS ??= '1'
import fs from 'node:fs'
import os from 'node:os'
import zlib from 'node:zlib'
import { execFileSync, execSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import * as PL from '../../../../../.claude/workflows/policy_lint.mjs'
const R = (k, v, u = '') => console.log(`RESULT ${k}=${v}${u ? ' ' + u : ''}`)
const BASE = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const VRE = PL.waveVerdictRe()
const git = (...a) => execFileSync('git', a, { encoding: 'utf8', maxBuffer: 1 << 28 }).trim()
const pid = (h, m1) => {
  const mb = git('merge-base', h, m1)
  const out = execSync(`git diff ${mb} ${h} | git patch-id --stable`, { encoding: 'utf8', maxBuffer: 1 << 28 }).trim()
  return out.split(' ')[0] || 'EMPTY'
}
// Second key, context-free: `git diff -U0` keeping only file headers and +/- lines
// (hunk headers dropped), so a merge of main that shifts line numbers or context
// but changes no line the branch changes keeps the same key.
const u0 = (h, m1) => {
  const mb = git('merge-base', h, m1)
  const d = execFileSync('git', ['diff', '-U0', mb, h], { encoding: 'utf8', maxBuffer: 1 << 28 })
  const keep = d.split('\n').filter((l) => l.startsWith('diff --git') || ((l.startsWith('+') || l.startsWith('-')) && !l.startsWith('+++') && !l.startsWith('---'))).join('\n')
  return keep ? createHash('sha1').update(keep).digest('hex') : 'EMPTY'
}
let flipped = false
const rv = { noContent: 0, noContentU0Equal: 0, u0equal: 0, n: 0, blocked: 0, equal: 0, changed: 0, laterBlocked: 0, missing: 0 }
const rows = []
let repair = 0, firstBlocked = 0, withV = 0
for (const [n, p] of Object.entries(snap.prs)) {
  const vs = [...(p.comments ?? []), ...(p.reviews ?? [])].sort((a, b) => String(a.at).localeCompare(String(b.at)))
    .map((c) => ({ c, m: VRE.exec(String(c.body ?? '').trim().split('\n')[0]) })).filter((x) => x.m)
  if (vs.length) { withV++; if (!vs[0].m[1]) firstBlocked++ }
  let prev = null
  for (let i = 0; i < vs.length; i++) {
    let { m } = vs[i]
    let head = (m[2] ?? m[4]).toLowerCase()
    if (prev && prev.pass && head !== prev.head && process.env.V2_PERTURB === 'flip' && !flipped) {
      m = VRE.exec(`Fix review: blocked ${head} harness: x`); flipped = true
    }
    const pass = Boolean(m[1])
    if (prev && !prev.pass) repair++
    if (prev && prev.pass && head !== prev.head) {
      rv.n++
      if (!pass) rv.blocked++
      let eq
      try { const m1 = git('rev-parse', `${p.merge_commit_sha}^1`); const a = pid(prev.head, m1), b = pid(head, m1); if (a === 'EMPTY' || b === 'EMPTY') throw new Error('empty'); eq = a === b; var eqU0 = u0(prev.head, m1) === u0(head, m1); if (eqU0) rv.u0equal++ } catch { rv.missing++; prev = { pass, head }; continue }
      if (eq) rv.equal++
      else {
        rv.changed++
        if (vs.slice(i + 1).some((x) => !x.m[1])) rv.laterBlocked++
      }
      const fpl = git('log', '--first-parent', '--format=%P%x09%s', `${prev.head}..${head}`).split('\n').filter(Boolean)
      const own = fpl.filter((l) => l.split('\t')[0].split(' ').length === 1 && !/^ci:/.test(l.split('\t')[1])).length
      const fcls = own ? 'content' : fpl.some((l) => l.split('\t')[0].split(' ').length > 1) ? 'merges-only' : 'ci-only'
      if (fcls !== 'content') { rv.noContent++; if (eqU0) rv.noContentU0Equal++ }
      rows.push(`[finder-class ${fcls}] #${n} ${prev.head.slice(0, 8)}->${head.slice(0, 8)} ${pass ? 'merge' : 'blocked'} net_diff_${eq ? 'equal' : 'changed'} u0_${eqU0 ? 'equal' : 'changed'}`)
    }
    prev = { pass, head }
  }
}
for (const r of rows) console.log('  ' + r)
R('reverify_rounds', rv.n)
R('reverify_blocked', rv.blocked)
R('reverify_net_diff_equal', rv.equal)
R('reverify_net_diff_changed', rv.changed)
R('reverify_u0_plusminus_equal', rv.u0equal)
R('finder_no_content_rounds', rv.noContent)
R('finder_no_content_rounds_u0_equal', rv.noContentU0Equal)
R('changed_rounds_later_blocked', rv.laterBlocked)
R('reverify_heads_missing', rv.missing)
R('repair_rounds', repair)
R('prs_with_verdict', withV)
R('first_verdicts_blocked', firstBlocked)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1)
R('swapins', (fs.readFileSync('/proc/vmstat', 'utf8').match(/^pswpin (\d+)/m) || [])[1] ?? 'na')
