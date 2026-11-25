#!/usr/bin/env node
// D13-s2, step D13.M6 -- the friction histogram's keys.
//
// Metric: over every `## Friction` entry policy_lint.mjs:frictionEntries accepts (id != null)
//   in the bodies of the merged pull requests first-parent in the window, the rule id k
//   (backticks stripped, `#` anchor dropped) names each `--budgets` path p with
//   p in {k, k.md, k/SKILL.md} or p ending in /k, /k.md, /k/SKILL.md (D13.md M6's rule):
//   one path -> that file; several -> an ambiguous row keyed by k; none -> no file.
//   Reported: the share of accepted entries naming one file, and per file each spelling's
//   count; beside it, the key production gives the same entry (frictionKey, through
//   `policy_lint.mjs --normalize-friction-keys`) and the files whose friction the two
//   disagree on. Key: the entry (pull request, line), never the PR title.
// Instrumented symbols: tools/policy/policy_lint.mjs:frictionEntries (what an entry is),
//   :frictionKey (via --normalize-friction-keys), :statsHistogram (the histogram, checked
//   equal to this harness's per-entry keys), :sizes/:policyFiles (the --budgets paths).
// Command (offline, from the export root):
//   HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node dev/audit/rounds/round11/D13/s2/friction_keys.mjs \
//     [--window dev/audit/rounds/round11/D13/s2/window.json] [--perturb readme|bare|unticked] [--list]
// Perturbations (fixture-only, D13.md): the first accepted entry naming
//   .claude/rules/ratchet-budgets.md is re-spelled in its body: `readme` -> README.md, which
//   moves one entry from that file to the ambiguous row (one_file down 1, ambiguous up 1);
//   `bare` -> ratchet-budgets (that file's count unchanged, its spelling row moves);
//   `unticked` -> the backticks removed (no file's count moves).
// Expected (baseline 92d38ecb, window v7.1.0..92d38ecb, window.json): exact counts.
// Machine: box B8 (shared). No timing is measured.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { frictionEntries, statsHistogram, policyFiles, sizes } from '../../../../../../tools/policy/policy_lint.mjs'

const argv = process.argv.slice(2)
const opt = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d)
const HERE = path.dirname(new URL(import.meta.url).pathname)
const snap = JSON.parse(fs.readFileSync(opt('--window', path.join(HERE, 'window.json')), 'utf8'))
const PERTURB = opt('--perturb', null)
const UNLABELLED = '(unlabelled friction bullet)'

// The `## Friction` section, split the way policy_lint.mjs:sections splits a body
// (a fenced block is opaque; a `## ` heading opens a section). Checked below: every
// PR's keys from this split must equal statsHistogram's own friction cells.
function frictionSection(body) {
  let cur = null, inFence = false
  const out = new Map()
  for (const line of String(body ?? '').split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    const m = inFence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) { cur = m[1]; out.set(cur, []); continue }
    if (cur) out.get(cur).push(line)
  }
  return (out.get('Friction') ?? []).join('\n').trim()
}

const budgetPaths = sizes(policyFiles()).map((r) => r.file)
const merges = snap.merges.map((m) => ({ ...m, pr: String(m.pr) }))

if (PERTURB) {
  const RB = '.claude/rules/ratchet-budgets.md'
  const to = { readme: '`README.md`', bare: '`ratchet-budgets`', unticked: 'ratchet-budgets.md' }[PERTURB]
  let done = false
  for (const m of merges) {
    for (const e of frictionEntries(frictionSection(m.body))) {
      if (done || !e.id) continue
      const k = e.id.replace(/#.*$/, '')
      if (k === 'ratchet-budgets.md' || k === RB) {
        const line = e.line.replace(/`?[A-Za-z.][A-Za-z0-9_.#/-]*`?/, to)
        m.body = m.body.replace(e.line.slice(0, 40), line.slice(0, 40 + (line.length - e.line.length)))
        console.log(`PERTURB #${m.pr}: ${e.id} -> ${to}`)
        done = true
      }
    }
  }
  if (!done) throw new Error('no entry naming ratchet-budgets.md to perturb')
}

// Every accepted entry, and its production key.
const entries = []
let unparsed = 0
for (const m of merges) {
  for (const e of frictionEntries(frictionSection(m.body))) {
    if (!e.id) { unparsed += 1; continue }
    entries.push({ pr: m.pr, id: e.id })
  }
}
if (argv.includes('--list')) {
  for (const e of entries) console.log(`#${e.pr} ${e.id}`)
  process.exit(0)
}
const nk = spawnSync(process.execPath, [path.resolve(HERE, '../../../../../../tools/policy/policy_lint.mjs'), '--normalize-friction-keys'],
  { input: [...new Set(entries.map((e) => e.id))].join('\n') + '\n', encoding: 'utf8' })
const prodKey = new Map(nk.stdout.split('\n').filter(Boolean).map((l) => l.split('\t')))
for (const e of entries) e.prod = prodKey.get(e.id)

// Self-check against statsHistogram: same keys, same entry counts, per PR.
const h = statsHistogram(merges.map((m) => ({ pr: m.pr })), new Map(merges.map((m) => [m.pr, { body: m.body, title: m.title, comments: [], reviews: [] }])), [])
const mine = new Map()
for (const e of entries) mine.set(e.prod, (mine.get(e.prod) ?? 0) + 1)
if (unparsed) mine.set(UNLABELLED, unparsed)
let mismatch = 0
for (const [k, c] of h.friction) if ((mine.get(k) ?? 0) !== c.entries) mismatch += 1
for (const k of mine.keys()) if (!h.friction.has(k)) mismatch += 1
console.log(`SELFCHECK histogram keys equal to per-entry keys: ${mismatch === 0 ? 'yes' : `NO (${mismatch} keys differ)`}`)

// D13.M6's rule.
function named(id) {
  const k = String(id).replace(/^`+|`+$/g, '').replace(/#.*$/, '')
  if (!k) return []
  return budgetPaths.filter((p) => p === k || p === `${k}.md` || p === `${k}/SKILL.md` ||
    p.endsWith(`/${k}`) || p.endsWith(`/${k}.md`) || p.endsWith(`/${k}/SKILL.md`))
}
const perFile = new Map(), ambiguous = new Map(), none = new Map()
let one = 0
for (const e of entries) {
  const hits = named(e.id)
  e.rule = hits.length === 1 ? hits[0] : hits.length ? `AMBIGUOUS(${hits.length})` : null
  if (hits.length === 1) {
    one += 1
    const f = perFile.get(hits[0]) ?? { spellings: new Map(), prs: new Set(), n: 0 }
    f.spellings.set(e.id, (f.spellings.get(e.id) ?? 0) + 1)
    f.prs.add(e.pr)
    f.n += 1
    perFile.set(hits[0], f)
  } else {
    const t = hits.length ? ambiguous : none
    const r = t.get(e.id) ?? { n: 0, hits }
    r.n += 1
    t.set(e.id, r)
  }
}
console.log(`WINDOW ${snap.since}..${snap.head.slice(0, 12)} merges=${merges.length} budgets_paths=${budgetPaths.length}`)
console.log(`RESULT accepted_entries=${entries.length} entries`)
console.log(`RESULT unparsed_entries=${unparsed} entries`)
console.log(`RESULT one_file=${one} entries`)
console.log(`RESULT one_file_share=${(one / entries.length).toFixed(3)} ratio`)
console.log(`RESULT ambiguous=${[...ambiguous.values()].reduce((n, r) => n + r.n, 0)} entries`)
console.log(`RESULT no_file=${[...none.values()].reduce((n, r) => n + r.n, 0)} entries`)
console.log(`RESULT no_file_ids=${none.size} ids`)
console.log('\nper file: entries, distinct PRs, each spelling (count) -- and the production key(s) those entries got')
for (const [f, r] of [...perFile.entries()].sort((a, b) => b[1].n - a[1].n)) {
  const prodKeys = new Map()
  for (const e of entries) if (e.rule === f) prodKeys.set(e.prod, (prodKeys.get(e.prod) ?? 0) + 1)
  console.log(`  ${f}  ${r.n} entries ${r.prs.size} PRs`)
  console.log(`      spellings: ${[...r.spellings.entries()].sort((a, b) => b[1] - a[1]).map(([s, c]) => `${s} ${c}`).join(' | ')}`)
  console.log(`      production keys: ${[...prodKeys.entries()].map(([s, c]) => `${s} ${c}`).join(' | ')}`)
}
console.log('\nambiguous rows:')
for (const [k, r] of ambiguous) console.log(`  ${k} ${r.n}  -> ${r.hits.join(', ')}  (production key: ${prodKey.get(k)})`)
console.log('\nno-file rows (all, by count):')
for (const [k, r] of [...none.entries()].sort((a, b) => b[1].n - a[1].n)) console.log(`  ${k} ${r.n}  (production key: ${prodKey.get(k)})`)

// Where the two keyings disagree: an entry naming exactly one file by the rule whose
// production key is not that file.
const split = entries.filter((e) => e.rule && !e.rule.startsWith('AMBIGUOUS') && e.prod !== e.rule)
const extra = entries.filter((e) => !e.rule && budgetPaths.includes(e.prod))
console.log(`\nRESULT rule_file_prod_other=${split.length} entries (one file by the rule, another key in production)`)
const byFile = new Map()
for (const e of split) {
  const r = byFile.get(e.rule) ?? new Map()
  r.set(`${e.id} -> ${e.prod}`, (r.get(`${e.id} -> ${e.prod}`) ?? 0) + 1)
  byFile.set(e.rule, r)
}
for (const [f, r] of byFile) console.log(`  ${f}: ${[...r.entries()].map(([s, c]) => `${s} (${c})`).join(' ; ')}`)
console.log(`RESULT prod_file_rule_none=${extra.length} entries (no file by the rule, a --budgets file in production)`)
for (const e of extra.slice(0, 30)) console.log(`  #${e.pr} ${e.id} -> ${e.prod}`)

// The threshold consequence: FRICTION_THRESHOLD distinct PRs on one key opens an issue.
const T = 3
const under = []
for (const [f, r] of perFile) {
  if (r.prs.size < T) continue
  const best = Math.max(...[...h.friction.entries()].filter(([k]) => entries.some((e) => e.rule === f && e.prod === k)).map(([, c]) => c.prs.size), 0)
  if (best < T) under.push(`${f} (${r.prs.size} PRs by the rule, best production key ${best})`)
}
console.log(`RESULT files_at_threshold_split_below=${under.length} files`)
for (const u of under) console.log(`  ${u}`)
console.log(`RESULT thread_factor=1.00`)
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let swapins = 0
try { swapins = +/pswpin (\d+)/.exec(fs.readFileSync('/proc/vmstat', 'utf8'))[1] } catch {}
console.log(`RESULT swapins=${swapins}`)
