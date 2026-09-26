#!/usr/bin/env node
// D13 / round 9 / verifier V3 (reach and class) -- D13-s1-02 (and the base rate
// D13-s1-03 leans on).
//
// METRIC (mine): a "reverify round" = a `Fix review: (merge|blocked) <40-hex>`
//   line (any line of an issue comment or review in the finder's live-API
//   snapshot, backticks stripped, time-ordered, an exact repeat of the previous
//   (word, head) dropped) whose previous verdict on the same PR was `merge` on a
//   DIFFERENT head. For each, the branch's own change is compared at both heads:
//   git diff merge-base(H, M^1)..H, M = the PR's first-parent
//   merge commit on main (a merged head is an ancestor of main itself, so the
//   base must be main just before the merge), as a `git patch-id --stable`.
//   RESULT reverify_rounds, reverify_blocked,
//   RESULT reverify_patch_identical = rounds whose branch patch-id did not change
//          (the proposed diff-equivalence check would have carried the verdict),
//   RESULT move_<git class>_<patch class> = cross-tab of the finder's move class
//          (first-parent prev..head all merges / all `ci:` / else content)
//          against the patch-id comparison,
//   RESULT reverify_heads_unresolved = heads git cannot resolve here,
//   RESULT first_verdicts, first_verdict_blocked = base rate of a block on a
//          PR's first verdict (what a round catches when it can catch),
//   RESULT p_zero_of_content = P(0 blocks | base rate) over the rounds whose
//          patch DID change (binomial), the chance 0 catches is luck.
// COMMAND (repository root): node tools/audit/round9/D13/verify-v3/D13-s1-02_diffeq.mjs
// VARIANT: D13V3_U0=1 -- the diffs are taken with -U0 (no context lines), so a
//   merge of main that only moves context around the branch's hunks keeps the id.
// VARIANT: D13V3_EXCL=1 -- the three bot/merge-driver-managed files (both claim
//   files, tests/closures.json) are left out of both diffs.
// PERTURBATION: D13V3_PERTURB=flip -- one patch-identical round's verdict word
//   read as `blocked` in memory: reverify_blocked 0 -> 1.
// BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: any (offline).
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import zlib from 'node:zlib'
import { execFileSync } from 'node:child_process'

const BASE = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
const R = (k, v) => console.log(`RESULT ${k}=${v}`)
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const git = (args, input) => {
  try { return execFileSync('git', args, { encoding: 'utf8', input, maxBuffer: 256 << 20, stdio: ['pipe', 'pipe', 'ignore'] }) } catch { return null }
}
const VR = /^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})\b/
const mergeOf = new Map()
for (const c of snap.commits) if (c.pulls && c.pulls.length && !mergeOf.has(String(c.pulls[0].number))) mergeOf.set(String(c.pulls[0].number), c.sha)
const pop = new Set(mergeOf.keys())
const pidCache = new Map()
const U = process.env.D13V3_U0 ? ['-U0'] : []
const X = process.env.D13V3_EXCL ? ['--', '.', ':!tests/golden/claimed_drift.txt', ':!tests/golden/card_claimed_drift.txt', ':!tests/closures.json'] : []
const patchId = (h, mainBefore) => {
  const key = h + mainBefore
  if (pidCache.has(key)) return pidCache.get(key)
  let v = null
  if (git(['cat-file', '-e', `${h}^{commit}`]) != null) {
    const mb = (git(['merge-base', h, mainBefore]) || '').trim()
    const d = mb ? git(['diff', '--no-color', '--full-index', ...U, `${mb}..${h}`, ...X]) : null
    v = d == null ? null : d === '' ? 'EMPTY' : (git(['patch-id', '--stable'], d) || '').split(' ')[0]
  }
  pidCache.set(key, v)
  return v
}
const rounds = []
let first = 0, firstBlocked = 0
for (const n of pop) {
  const p = snap.prs[n]
  if (!p) continue
  const vs = []
  for (const c of [...(p.comments || []), ...(p.reviews || [])]) {
    for (const raw of String(c.body || '').split('\n')) {
      const m = VR.exec(raw.replace(/`/g, '').trim())
      if (m) vs.push({ at: c.at, word: m[1], head: m[2] })
    }
  }
  vs.sort((a, b) => (a.at < b.at ? -1 : a.at > b.at ? 1 : 0))
  const dd = vs.filter((v, i) => i === 0 || v.word !== vs[i - 1].word || v.head !== vs[i - 1].head)
  if (dd.length) { first++; if (dd[0].word === 'blocked') firstBlocked++ }
  for (let i = 1; i < dd.length; i++) {
    if (dd[i - 1].word === 'merge' && dd[i].head !== dd[i - 1].head) rounds.push({ pr: n, prev: dd[i - 1].head, ...dd[i] })
  }
}
let emptyDiff = 0, ident = 0, unresolved = 0, blocked = 0, content = 0, flipped = false
for (const r of rounds) {
  const mb4 = `${mergeOf.get(r.pr)}^1`
  const a = patchId(r.prev, mb4), b = patchId(r.head, mb4)
  if (a === 'EMPTY' || b === 'EMPTY') emptyDiff++
  if (a == null || b == null) { unresolved++; r.cls = 'unresolved' } else if (a === b) { ident++; r.cls = 'identical' } else { content++; r.cls = 'changed' }
  if (process.env.D13V3_PERTURB === 'flip' && !flipped && r.cls === 'identical') { r.word = 'blocked'; flipped = true }
  if (r.word === 'blocked') blocked++
}
const cross = {}
for (const r of rounds) {
  const log = (git(['log', '--first-parent', '--format=%P%x09%s', `${r.prev}..${r.head}`]) || '').split('\n').filter(Boolean)
  const mv = log.every((l) => l.split('\t')[0].includes(' ')) ? 'merges-only' : log.every((l) => /^ci:/.test(l.split('\t')[1])) ? 'ci-only' : 'content'
  const k = `${mv}/${r.cls}`
  cross[k] = (cross[k] || 0) + 1
  console.log(`round #${r.pr} ${r.prev.slice(0, 8)}->${r.head.slice(0, 8)} ${r.word} ${mv} ${r.cls}`)
}
for (const [k, v] of Object.entries(cross).sort()) R(`move_${k.replace('/', '_')}`, v)
const q = first ? firstBlocked / first : 0
R('reverify_rounds', rounds.length)
R('reverify_blocked', blocked)
R('reverify_patch_identical', ident)
R('reverify_patch_changed', content)
R('reverify_heads_unresolved', unresolved)
R('reverify_empty_branch_diff', emptyDiff)
R('first_verdicts', first)
R('first_verdict_blocked', firstBlocked)
R('p_zero_of_content', Math.pow(1 - q, content).toFixed(3))
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('swapins', 0)
