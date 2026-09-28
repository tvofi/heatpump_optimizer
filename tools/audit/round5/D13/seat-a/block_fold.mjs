#!/usr/bin/env node
// D13 / round 5 seat-a -- the two verdict-class instruments disagree on the
// same blocked verdict: web-fix-wave.js's VERDICT_RE refuses a line that
// policy_lint.mjs --stats keys as class `other`.
//
// METRIC (one line): over the window's blocked verdicts (first lines matching
// ^Fix review:\s*blocked), folded_into_other = the count whose line does NOT
// match web-fix-wave.js's VERDICT_RE (the wave cannot act on it) but DOES
// match policy_lint.mjs's BLOCKED_SHAPE_RE with no class word captured (the
// --stats histogram keys it `other` instead of an outside-grammar row).
//
// INSTRUMENTED SYMBOLS, both extracted from the production files at run time
// (never re-typed from memory): .claude/workflows/web-fix-wave.js:VERDICT_RE
// (rebuilt from its template-literal source) and
// .claude/workflows/policy_lint.mjs:BLOCKED_SHAPE_RE (statsHistogram's
// keying arm).
//
// COMMAND (from the repository root):
//   HPO_PLANDATA=/tmp/audit-5/tmp/d13/plandata/pl.json \
//   node tools/audit/round5/D13/seat-a/block_fold.mjs
//
// EXPECTED at baseline 1cc89e0 (tolerance: exact):
//   blocked_verdicts=1 folded_into_other=1
//   (the #1287 post-merge block: untaught class word, parenthetical, no colon)
//
// PERTURBATION (fixture, direction): rewrite that verdict's first line with a
// colon after the class word (`... class-c-live-worktree-deleted: POST-MERGE
// ...`) via PERTURB=colon and folded_into_other must fall 1 -> 0: VERDICT_RE
// now parses it (untaught word, its own row per #1239) and BLOCKED_SHAPE_RE
// captures the word. PERTURB=nosha (drop the sha) and BOTH instruments refuse
// it (outside-grammar for both; folded stays 0).
// MACHINE: any; count harness, no timing claim.

import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const FIX = process.env.FIXTURE_DIR ?? join(HERE, 'fixtures')
const ROOT = join(HERE, '..', '..', '..', '..', '..')

// -- extract VERDICT_RE from web-fix-wave.js (template literals concatenated,
// then unescaped: the source's `\\s` is the runtime's `\s` -- template-literal
// semantics, without which the rebuilt pattern would demand a literal backslash)
const wave = readFileSync(join(ROOT, '.claude/workflows/web-fix-wave.js'), 'utf8')
const ctor = wave.match(/const VERDICT_RE = new RegExp\(\n([\s\S]*?)\n\)/)[1]
const verdictSrc = [...ctor.matchAll(/`([^`]*)`/g)].map((m) => m[1]).join('')
  .replaceAll('\\\\', '\\')
const VERDICT_RE = new RegExp(verdictSrc)
console.log('# VERDICT_RE rebuilt from web-fix-wave.js:', verdictSrc)

// -- extract BLOCKED_SHAPE_RE from policy_lint.mjs (regex literal + flags)
const lint = readFileSync(join(ROOT, '.claude/workflows/policy_lint.mjs'), 'utf8')
const bm = lint.match(/const BLOCKED_SHAPE_RE = (\/.*?\/)([a-z]*)\s*$/m)
const BLOCKED_SHAPE_RE = new RegExp(bm[1].slice(1, -1), bm[2])
console.log('# BLOCKED_SHAPE_RE rebuilt from policy_lint.mjs:',
  bm[1], bm[2])

// -- the window's blocked verdict first lines (from the graphql fixture)
const g = JSON.parse(readFileSync(join(FIX, 'prs_graphql.json'), 'utf8')).data.repository
const lines = []
for (const k of ['p1280', 'p1281', 'p1282', 'p1284', 'p1285', 'p1286', 'p1287', 'p1289']) {
  const p = g[k]
  for (const c of p.comments.nodes ?? []) {
    const first = String(c.body ?? '').split('\n')[0].trim()
    if (/^Fix review:\s*blocked/i.test(first)) lines.push([p.number, first])
  }
  for (const r of p.reviews.nodes ?? []) {
    const first = String(r.body ?? '').split('\n')[0].trim()
    if (/^Fix review:\s*blocked/i.test(first)) lines.push([p.number, first])
  }
}

let folded = 0
for (const [pr, raw] of lines) {
  let line = raw
  if (process.env.PERTURB === 'colon') {
    line = raw.replace(/(class-c-live-worktree-deleted) \(/, '$1: (')
  } else if (process.env.PERTURB === 'nosha') {
    line = line.replace(/[0-9a-f]{40} /, '')
  }
  const waveParses = VERDICT_RE.test(line)
  const statsKey = BLOCKED_SHAPE_RE.exec(line)
  const statsClass = statsKey ? (statsKey[2] ? statsKey[2].toLowerCase() : 'other') : null
  const isFolded = !waveParses && statsClass === 'other'
  if (isFolded) folded += 1
  console.log(`# PR ${pr}: wave=${waveParses ? 'parses' : 'REFUSES'} stats=${statsClass ?? 'unclassified'}`
    + `${isFolded ? '  <- folded into other' : ''}`)
  console.log(`#   line: ${line.slice(0, 100)}`)
}

const res = (n, v) => console.log(`RESULT ${n}=${v}`)
res('blocked_verdicts', lines.length)
res('folded_into_other', folded)
res('api_failures', 0)
res('thread_factor', '1.0 (count harness, no numpy)')
