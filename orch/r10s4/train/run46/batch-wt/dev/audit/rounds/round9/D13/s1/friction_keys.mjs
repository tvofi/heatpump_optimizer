#!/usr/bin/env node
// D13 / round 9 / seat s1 -- D13.M6: the friction histogram's keys.
//
// METRIC: over every `## Friction` entry in the window's merged PR bodies
// (API-mode population, v6.6.0..1936d5ca), parsed by the PRODUCTION parser
// policy_lint.mjs:frictionEntries, the rule id k (`#` anchor dropped) names
// each `--budgets` path P with P == k, or P ends in `/`+k, or P is/ends in k+'.md'
// or k+'/SKILL.md'. One path -> that file; several -> the ambiguous row; none ->
// unresolved. RESULT share_one_file = entries naming exactly one file / entries
// with an id. Per file, each spelling's count. Then the PRODUCTION key
// (policy_lint.mjs:statsHistogram's friction map, i.e. frictionKey) is compared
// entry-for-entry with the brief's rule: RESULT key_disagreements.
// COMMAND: HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/s1/friction_keys.mjs
// PERTURBATION: D13_PERTURB=respell:<spelling> re-spells the FIRST entry keyed
//   on .claude/rules/ratchet-budgets.md (else the first one-file entry) in memory:
//   `README.md` moves it to the ambiguous row; `ratchet-budgets` keeps its file
//   count; an unbackticked spelling moves no file's count.
// EXPECTED at 1936d5ca: exact. MACHINE: any. BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
import fs from 'node:fs'
import zlib from 'node:zlib'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import * as PL from '../../../../../.claude/workflows/policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(HERE, 'window.json.gz'))).toString())
const R = (k, v, u = '') => console.log(`RESULT ${k}=${v}${u ? ' ' + u : ''}`)

const budgetOut = execFileSync('node', ['.claude/workflows/policy_lint.mjs', '--budgets'], { encoding: 'utf8' })
const PATHS = budgetOut.split('\n').slice(1).map((l) => l.split(/\s+/)[0]).filter((p) => p && /\.md$/.test(p))
R('budgets_paths', PATHS.length)

function names(k) {
  const bare = String(k).replace(/^`+|`+$/g, '').replace(/#.*$/, '')
  if (!bare) return []
  const forms = [bare, bare + '.md', bare + '/SKILL.md']
  return PATHS.filter((p) => forms.some((f) => p === f || p.endsWith('/' + f)))
}
// the production section reader is not exported; this is its rule (## heading
// outside code fences), re-stated, and the ENTRY parser is production's own.
function frictionSection(body) {
  let cur = null, fence = false
  const out = []
  for (const line of String(body).split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) fence = !fence
    const m = fence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) { cur = m[1]; continue }
    if (cur === 'Friction') out.push(line)
  }
  return out.join('\n').trim()
}

const seen = new Set(), merges = []
for (const c of snap.commits) {
  if (!c.pulls?.length) continue
  const pr = String(c.pulls[0].number)
  if (!seen.has(pr)) { seen.add(pr); merges.push({ pr }) }
}
const bodies = new Map(merges.map(({ pr }) => [pr, snap.prs[pr]?.body ?? '']))
const P = process.env.D13_PERTURB || ''

const entries = []
for (const { pr } of merges) {
  for (const e of PL.frictionEntries(frictionSection(bodies.get(pr)))) entries.push({ pr, ...e })
}
if (P.startsWith('respell:')) {
  const to = P.slice(8)
  const tgt = entries.find((e) => e.id && names(e.id).length === 1 && names(e.id)[0] === '.claude/rules/ratchet-budgets.md') ??
    entries.find((e) => e.id && names(e.id).length === 1)
  console.log(`perturbed #${tgt.pr}: ${tgt.id} -> ${to}`)
  // re-spell in the body, so the production parser re-reads it
  const body = bodies.get(tgt.pr)
  bodies.set(tgt.pr, body.replace(new RegExp('`?' + tgt.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '`?\\s*:\\s*`?' + tgt.event), to + ': ' + tgt.event))
  entries.length = 0
  for (const { pr } of merges) for (const e of PL.frictionEntries(frictionSection(bodies.get(pr)))) entries.push({ pr, ...e })
}
const withId = entries.filter((e) => e.id)
let one = 0, amb = 0, none = 0
const perFile = new Map()
const ambRows = new Map(), noneRows = new Map()
for (const e of withId) {
  const ns = names(e.id)
  if (ns.length === 1) {
    one += 1
    const m = perFile.get(ns[0]) ?? new Map()
    m.set(e.id, (m.get(e.id) ?? 0) + 1)
    perFile.set(ns[0], m)
  } else if (ns.length > 1) { amb += 1; ambRows.set(e.id, (ambRows.get(e.id) ?? 0) + 1) } else { none += 1; noneRows.set(e.id, (noneRows.get(e.id) ?? 0) + 1) }
}
R('friction_entries', entries.length)
R('entries_with_id', withId.length)
R('entries_unparsed', entries.length - withId.length)
R('one_file', one)
R('ambiguous', amb)
R('unresolved', none)
R('share_one_file', withId.length ? (one / withId.length).toFixed(3) : 'na')
for (const [f, m] of [...perFile].sort((a, b) => [...b[1].values()].reduce((x, y) => x + y) - [...a[1].values()].reduce((x, y) => x + y))) {
  console.log(`  file ${f}: ${JSON.stringify(Object.fromEntries(m))}`)
}
console.log(`  ambiguous: ${JSON.stringify(Object.fromEntries(ambRows))}`)
console.log(`  unresolved: ${JSON.stringify(Object.fromEntries(noneRows))}`)
const rmCount = [...(perFile.get('.claude/rules/ratchet-budgets.md') ?? new Map()).values()].reduce((x, y) => x + y, 0)
R('file_count_ratchet_budgets', rmCount)

// production keying, per entry (statsHistogram over one synthetic PR per entry)
let dis = 0
const disRows = new Map()
for (const e of withId) {
  const fake = `## Friction\n\n${e.line}\n`
  const H = PL.statsHistogram([{ pr: 'x' }], new Map([['x', { body: fake, comments: [], reviews: [] }]]), ['blocked', 'merge'])
  const prodKey = [...H.friction.keys()][0]
  const ns = names(e.id)
  const briefKey = ns.length === 1 ? ns[0] : ns.length > 1 ? '(ambiguous)' : '(unresolved)'
  const prodFile = PATHS.includes(prodKey) ? prodKey : '(verbatim)'
  const briefFile = ns.length === 1 ? ns[0] : '(verbatim)'
  if (prodFile !== briefFile) {
    dis += 1
    const k = `${e.id} -> brief ${briefKey} / prod ${prodKey}`
    disRows.set(k, (disRows.get(k) ?? 0) + 1)
  }
}
R('key_disagreements', dis)
for (const [k, v] of [...disRows].sort((a, b) => b[1] - a[1])) console.log(`  disagree x${v}: ${k}`)
R('api_failures', snap.api_failures)
R('load1', os.loadavg()[0].toFixed(2))
R('thread_factor', 1.0)
R('baseline_sha', '1936d5ca72a06556eeed4e8e5bf3dea520e517e1')
