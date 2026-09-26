#!/usr/bin/env node
// D13 / round 9 / verify V1 -- independent re-measure of D13-s1-02 and D13-s1-03.
// METRICS (my own reader; no policy_lint import):
//   02: a re-verify round = a verdict line `^Fix review:\s*(merge|blocked)\s+<hex7-40>`
//     (issue comments + reviews, time-ordered, per PR of the finder's snapshot whose
//     /commits/<sha>/pulls answered a row) whose predecessor verdict was `merge` on a
//     different head. RESULT rv_rounds, rv_blocked. Then DIFF-EQUIVALENCE, the
//     phenomenon property itself: base(H) = newest commit of the baseline's
//     first-parent line reachable from H; RESULT rv_diff_identical = rounds whose
//     `git diff base(prev) prev` and `git diff base(cur) cur` have the same
//     `git patch-id --stable`; rv_diff_changed = the rest.
//   03: blocked verdicts' class word (the token after `<head> ` up to ':'), counted
//     (a) raw, (b) synonym-merged on BOTH sides with the finder's own SYN map;
//     RESULT body_answer = root-cause-unanswered + red-check; max_eng_raw,
//     max_eng_merged; distinct PRs of body_answer; body_answer_in_1559_1563 (one
//     wave); leave-one-PR-out min of body_answer; body_answer minus that wave.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/verify-v1/rounds_indep.mjs
// EXPECTED at 1936d5ca: see verify-v1 report; exact. MACHINE: any (offline + git objects).
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
const git = (a, input) => execFileSync('git', a, { encoding: 'utf8', input, maxBuffer: 256 << 20 })
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(HERE, '..', 's1', 'window.json.gz'))).toString())
const prs = [...new Set(snap.commits.filter((c) => c.pulls && c.pulls.length).map((c) => String(c.pulls[0].number)))]
const VRE = /^Fix review:\s*(merge|blocked)\s+([0-9a-fA-F]{7,40})\b\s*(.*)$/
const verdicts = (pr) => {
  const p = snap.prs[pr]; if (!p) return []
  return [...(p.comments || []).map((c) => ({ b: c.body, at: c.at })), ...(p.reviews || []).map((c) => ({ b: c.body, at: c.at }))]
    .sort((a, b) => String(a.at).localeCompare(String(b.at)))
    .map((c) => VRE.exec(String(c.b ?? '').trim().split('\n')[0])).filter(Boolean)
    .map((m) => ({ word: m[1], head: m[2].toLowerCase(), rest: m[3] }))
}
const mainFP = new Set(git(['rev-list', '--first-parent', BASE]).split('\n').filter(Boolean))
const full = (h) => git(['rev-parse', h + '^{commit}']).trim()
const baseOf = (h) => { for (const c of git(['rev-list', '--topo-order', h]).split('\n')) if (mainFP.has(c)) return c; return null }
const pid = (a, b, u = '-U3') => { const d = git(['diff', u, a, b]); return d ? git(['patch-id', '--stable'], d).split(' ')[0] : 'EMPTY' }
let rv = 0, rvB = 0, same = 0, changed = 0, miss = 0, sameU0 = 0
const rows = []
for (const pr of prs) {
  const vs = verdicts(pr)
  for (let i = 1; i < vs.length; i++) {
    const a = vs[i - 1], b = vs[i]
    if (a.word !== 'merge' || b.head === a.head || b.head.startsWith(a.head) || a.head.startsWith(b.head)) continue
    rv++; if (b.word === 'blocked') rvB++
    try {
      const A = full(a.head), B = full(b.head)
      const eq = pid(baseOf(A), A) === pid(baseOf(B), B)
      eq ? same++ : changed++
      const eq0 = pid(baseOf(A), A, '-U0') === pid(baseOf(B), B, '-U0'); if (eq0) sameU0++
      rows.push(`#${pr} ${A.slice(0, 8)}->${B.slice(0, 8)} ${b.word} diff ${eq ? 'IDENTICAL' : 'changed'}`)
    } catch { miss++ }
  }
}
for (const r of rows) console.log('  rv ' + r)
R('window_prs', prs.length)
R('rv_rounds', rv); R('rv_blocked', rvB); R('rv_diff_identical', same); R('rv_diff_changed', changed); R('rv_missing', miss); R('rv_diff_identical_U0', sameU0)
// chance of 0 blocks in rv rounds at the window's first-verdict block rate (16/188)
R('p_zero_blocks_at_first_verdict_rate', Math.pow(1 - 16 / 188, rv).toFixed(3))
// ---- 03 ----
const SYN = { 'red-check': 'root-cause-unanswered', 'carry-incomplete': 'carry-missing', 'readme-numbering': 'claims', vacuous: 'mutation-vacuous', mutation: 'mutation-vacuous', 'wrong-input': 'product-tradeoff-regression', measurement: 'harness', dirty: 'conflict', 'closures-unrepaired': 'conflict' }
const ENG = ['mutation-vacuous', 'harness', 'null-control', 'class-open', 'product-tradeoff-regression', 'preflight-mismatch']
const blocks = []
for (const pr of prs) for (const v of verdicts(pr)) if (v.word === 'blocked') { const m = /^([a-z][a-z-]*):/.exec(v.rest.trim()); blocks.push({ pr: Number(pr), w: m ? m[1] : 'other' }) }
const cnt = (arr, f) => arr.reduce((m, x) => (m.set(f(x), (m.get(f(x)) || 0) + 1), m), new Map())
const raw = cnt(blocks, (x) => x.w), merged = cnt(blocks, (x) => SYN[x.w] ?? x.w)
console.log('  raw ' + JSON.stringify(Object.fromEntries(raw)))
console.log('  merged ' + JSON.stringify(Object.fromEntries(merged)))
const isBA = (x) => x.w === 'root-cause-unanswered' || x.w === 'red-check'
const BA = blocks.filter(isBA)
R('blocked_verdicts', blocks.length)
R('body_answer', BA.length)
R('body_answer_distinct_prs', new Set(BA.map((x) => x.pr)).size)
R('max_eng_raw', Math.max(0, ...[...raw].filter(([k]) => ENG.includes(SYN[k] ?? k)).map(([, v]) => v)))
R('max_eng_merged', Math.max(0, ...[...merged].filter(([k]) => ENG.includes(k)).map(([, v]) => v)))
R('eng_bucket', blocks.filter((x) => ENG.includes(SYN[x.w] ?? x.w)).length)
R('body_answer_in_1559_1563', BA.filter((x) => x.pr >= 1559 && x.pr <= 1563).length)
R('body_answer_outside_1559_1563', BA.filter((x) => x.pr < 1559 || x.pr > 1563).length)
const loo = [...new Set(BA.map((x) => x.pr))].map((p) => BA.filter((x) => x.pr !== p).length)
R('body_answer_loo_pr_min', Math.min(...loo))
const eng = (xs) => Math.max(0, ...[...cnt(xs.filter((x) => ENG.includes(SYN[x.w] ?? x.w)), (x) => SYN[x.w] ?? x.w).values()])
const nw = blocks.filter((x) => x.pr < 1559 || x.pr > 1563)
R('max_eng_merged_outside_1559_1563', eng(nw))
for (const x of BA) { const p = snap.prs[x.pr]; const c = (p.comments || []).find((c) => /^Fix review:\s*blocked/.test(String(c.body).trim()) && String(c.body).includes(x.w)); console.log(`  ba #${x.pr} ${x.w} at ${c ? c.at : '?'}`) }
R('load1', os.loadavg()[0].toFixed(2)); R('thread_factor', 1.0); R('swapins', 0); R('baseline_sha', BASE)
// ---- 03 attack: EVERY reason a blocked verdict gives, not only its first class word.
// A secondary reason is `; and <word>:` / `; also <word>:` / `and <word>:` in the first line.
// RESULT ba_sole = body-answer blocks carrying no second reason; ba_with_eng = those also
// naming an engineering reason; eng_any_max = largest engineering class (SYN-merged, plus
// `regression` -> product-tradeoff-regression) counting every mention.
{
  const SYN2 = { ...SYN, regression: 'product-tradeoff-regression' }
  const all = []
  for (const pr of prs) for (const v of verdicts(pr)) if (v.word === 'blocked') {
    const words = [...v.rest.matchAll(/(?:^|(?:;|--)\s*(?:and|also)?\s*|\band\s+|\balso\s+)([a-z][a-z-]+):/g)].map((m) => m[1])
    all.push({ pr: Number(pr), words })
  }
  const ba = all.filter((x) => x.words[0] === 'root-cause-unanswered' || x.words[0] === 'red-check')
  const engOf = (w) => ENG.includes(SYN2[w] ?? w)
  R('ba_sole', ba.filter((x) => !x.words.slice(1).some(engOf)).length)
  R('ba_with_eng', ba.filter((x) => x.words.slice(1).some(engOf)).length)
  const m = new Map(); for (const x of all) for (const w of new Set(x.words.filter(engOf).map((w) => SYN2[w] ?? w))) m.set(w, (m.get(w) || 0) + 1)
  console.log('  eng_any ' + JSON.stringify(Object.fromEntries(m)))
  R('eng_any_max', Math.max(0, ...m.values()))
  R('load1_end', os.loadavg()[0].toFixed(2))
}
