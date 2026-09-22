#!/usr/bin/env node
/*
D13 round 6 -- required output 6: the friction histogram's keys, and which of
them name a file.

METRIC (one line each; every count derived at this harness's own window):

  entries_total          every Friction entry in the window's merged bodies:
                         frictionEntries(<body's Friction section>).length, the
                         production entry reader itself (imported, not copied).
  unlabelled_entries     entries whose id is null -- no backticked rule id.
  key_resolved_to_one    entries whose normalized key names EXACTLY ONE file of
                         the policy-file list `--budgets` reports.
  key_ambiguous          entries whose key names SEVERAL (e.g. README.md).
  key_unresolved         entries whose key names none -- the verbatim row.
  share_naming_one_file  key_resolved_to_one / entries_total.
  per file               the DISTINCT raw spellings that resolved to it, with
                         each spelling's entry count.

RESOLUTION RULE, which is the one the brief states: a key `k` (its `#anchor`
dropped) names each policy file `p` where p === k, or p ends in '/' + k, or
p === k + '.md', or p === k + '/SKILL.md'. One match is that file; several is an
ambiguous row; none is the verbatim row.

INSTRUMENTS DRIVEN (nothing is transcribed):
  policy_lint.mjs:frictionEntries   imported and called (the entry reader).
  policy_lint.mjs:frictionKey       driven through its own CLI,
                                    `--normalize-friction-keys`, ids on stdin.
  policy_lint.mjs:cmdBudgets        driven through `--budgets` for the file list.
A NULL CONTROL validates the one thing this harness does copy -- the `sections`
split it needs to find the Friction section: the per-key histogram it produces
must equal `policy_lint.mjs:statsHistogram`'s CENSUS lines from
`--stats --since v6.6.0` (22 keys, of which 20 label friction). If those differ,
the copy is wrong and the numbers below are not evidence.

COMMAND (from the repository root; needs GITHUB_TOKEN for the CLI children):
  GITHUB_TOKEN=$(gh auth token) node tools/audit/round6/D13/friction_keys.mjs

EXPECTED at baseline e336cc2c (tolerance: exact; counts, not timings):
  see RESULT lines; api_failures must be 0.

PERTURBATION. D13_SPELL=<spelling> re-spells the FIRST entry whose id is
`ratchet-budgets.md` -- an entry that resolved to .claude/rules/ratchet-budgets.md
-- and re-runs the whole pipeline, printing `DELTA key` lines:
  D13_SPELL=README.md   the entry moves to the ambiguous row (several matches);
                        that file's count falls by 1.
  D13_SPELL=ratchet-budgets   resolves to the SAME file: no file's count moves.
  D13_SPELL=@@none@@    drops the backticks (id becomes null): the entry moves
                        to the unlabelled row, so that file's count falls.
  D13_SPELL=@@absent@@  inserts an id naming no policy file at all.

MACHINE: any; reads the GitHub API and shells out to node. Counts, not timings.
*/

import { execFileSync } from 'node:child_process'
import { readFileSync, existsSync } from 'node:fs'
import path from 'node:path'
import os from 'node:os'
import { frictionEntries } from '../../../../.claude/workflows/policy_lint.mjs'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../../..')
const CACHE = process.env.D13_CACHE || path.join(os.homedir(), '.cache/hpo-d13-round6')
const REPO = process.env.D13_REPO || 'tvofi/heatpump_optimizer'
const SINCE = process.env.D13_SINCE || 'v6.6.0'
const WAVE_FILES = '.claude/workflows/policy_lint.mjs'
let API_FAILURES = 0

const key = (p) => p.replaceAll('/', '_').replaceAll('?', '~').replaceAll('&', '~').replaceAll('=', '-')

function cached(apiPath) {
  const f = path.join(CACHE, key(apiPath) + '.json')
  if (existsSync(f) && readFileSync(f, 'utf8').length) return JSON.parse(readFileSync(f, 'utf8'))
  try {
    const out = execFileSync('gh', ['api', apiPath], { encoding: 'utf8', maxBuffer: 1 << 28 })
    return JSON.parse(out)
  } catch (e) {
    API_FAILURES++
    return null
  }
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8', cwd: ROOT })
}

function result(name, value, unit = '') {
  console.log(`RESULT ${name}=${value} ${unit}`.trimEnd())
}

// A copy of policy_lint.mjs:sections' split rule -- the only thing copied, and
// the null control below is what validates it.
function sections(body) {
  const out = new Map()
  let cur = null
  let inFence = false
  for (const line of String(body || '').split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    const m = inFence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) { cur = m[1]; out.set(cur, []); continue }
    if (cur) out.get(cur).push(line)
  }
  for (const [k, v] of out) out.set(k, v.join('\n').trim())
  return out
}

function cli(args, stdin) {
  return execFileSync('node', [path.join(ROOT, WAVE_FILES), ...args], {
    encoding: 'utf8',
    cwd: ROOT,
    input: stdin,
    env: { ...process.env, GITHUB_TOKEN: process.env.GITHUB_TOKEN || execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim() },
    maxBuffer: 1 << 28,
  })
}

function policyFiles() {
  const txt = cli(['--budgets'])
  const out = []
  let header = true
  for (const line of txt.split('\n')) {
    if (header) { if (/\bcap\b/.test(line) && /\blines\b/.test(line)) header = false; continue }
    if (!line.trim()) break
    const f = line.trim().split(/\s+/)[0]
    if (f) out.push(f)   // includes the slash-less CLAUDE.md and AGENTS.md
  }
  return out
}

function matches(k, files) {
  const bare = k.split('#')[0]
  return files.filter((p) => p === bare || p.endsWith('/' + bare) || p === bare + '.md' || p === bare + '/SKILL.md')
}

function main() {
  const files = policyFiles()
  result('policy_files', files.length)

  // ---- the window's merges, the API mode of policy_lint.mjs:enumerateMerges
  const commits = git('log', '--first-parent', '--format=%H%x09%s', `${SINCE}..HEAD`)
    .split('\n').filter(Boolean).map((l) => { const [sha, subj] = l.split('\t'); return { sha, subj } })
  const seen = new Set()
  const prs = []
  for (const c of commits) {
    const d = cached(`repos/${REPO}/commits/${c.sha}/pulls`)
    if (d === null) continue
    if (Array.isArray(d) && d.length) {
      const n = d[0].number
      if (!seen.has(n)) { seen.add(n); prs.push(n) }
    }
  }
  result('merges', prs.length)

  // ---- entries, straight out of the production reader
  const perPr = []
  for (const n of prs) {
    const meta = cached(`repos/${REPO}/pulls/${n}`)
    if (!meta) continue
    const sec = sections(meta.body).get('Friction')
    if (!sec) continue
    for (const e of frictionEntries(sec)) perPr.push({ pr: n, id: e.id, event: e.event })
  }
  // ---- PERTURBATION: re-spell the first entry that resolved to ratchet-budgets.md
  const spell = process.env.D13_SPELL
  if (spell) {
    const i = perPr.findIndex((e) => e.id === 'ratchet-budgets.md')
    if (i < 0) { console.log('D13_SPELL set but no `ratchet-budgets.md` entry found'); process.exit(1) }
    if (spell === '@@none@@') perPr[i].id = null
    else perPr[i].id = spell === '@@absent@@' ? 'no-such-file' : spell
    console.log(`PERTURBED entry at PR #${perPr[i].pr}`)
  }
  result('entries_total', perPr.length)
  result('unlabelled_entries', perPr.filter((e) => e.id === null).length)

  // ---- the production key normalizer, through its own CLI. It answers
  // `<raw>\t<key>` per input line, blank lines skipped, so the row count is
  // checked against what was sent rather than a short answer read as "no match".
  const ids = perPr.filter((e) => e.id !== null).map((e) => e.id)
  const rows = ids.length
    ? cli(['--normalize-friction-keys'], ids.join('\n') + '\n').split('\n').filter((l) => l.length)
    : []
  if (rows.length !== ids.length) {
    console.log(`MISMATCH: ${ids.length} ids in, ${rows.length} rows out`)
    process.exit(1)
  }
  let j = 0
  for (const e of perPr) if (e.id !== null) e.key = rows[j++].split('\t')[1]

  const byFile = new Map()      // file -> Map(spelling -> count)
  const ambiguous = new Map()   // key -> count
  const unresolved = new Map()
  let one = 0
  for (const e of perPr) {
    if (e.key === undefined) continue
    const m = matches(e.key, files)
    if (m.length === 1) {
      one++
      if (!byFile.has(m[0])) byFile.set(m[0], new Map())
      const sm = byFile.get(m[0])
      sm.set(e.id, (sm.get(e.id) || 0) + 1)
    } else if (m.length > 1) ambiguous.set(e.key, (ambiguous.get(e.key) || 0) + 1)
    else unresolved.set(e.key, (unresolved.get(e.key) || 0) + 1)
  }
  result('key_resolved_to_one', one)
  result('share_naming_one_file', (one / perPr.length).toFixed(3))
  result('key_ambiguous_entries', [...ambiguous.values()].reduce((a, b) => a + b, 0))
  result('key_unresolved_entries', [...unresolved.values()].reduce((a, b) => a + b, 0))
  result('distinct_files_named', byFile.size)

  console.log('\nper file (distinct spellings -> entries):')
  for (const f of [...byFile.keys()].sort()) {
    const sm = [...byFile.get(f).entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    console.log(`  ${f}  [${sm.reduce((a, b) => a + b[1], 0)}]  ` +
      sm.map(([s, c]) => `${JSON.stringify(s)}x${c}`).join(' '))
  }
  if (ambiguous.size) {
    console.log('\nambiguous rows (key names several files):')
    for (const [k, c] of [...ambiguous.entries()].sort((a, b) => b[1] - a[1]))
      console.log(`  ${k} x${c}  matches: ${matches(k, files).join(', ')}`)
  }
  if (unresolved.size) {
    console.log('\nverbatim rows (key names no file):')
    for (const [k, c] of [...unresolved.entries()].sort((a, b) => b[1] - a[1]))
      console.log(`  ${k} x${c}`)
  }

  // ---- null control: the copied section split must reproduce the CENSUS.
  // CENSUS rows are `<kind>\t<distinct PRs>\t<entries>\t<key>`; this harness
  // counts ENTRIES, so the entries column is the one compared.
  const hist = new Map()
  for (const e of perPr) { const k = e.key ?? '<unlabelled>'; hist.set(k, (hist.get(k) || 0) + 1) }
  const census = new Map()
  const stats = cli(['--stats', '--since', SINCE])
  for (const line of stats.split('\n')) {
    const m = /^CENSUS\tfriction rule id\t(\d+)\t(\d+)\t(.+)$/.exec(line)
    if (m) census.set(m[3].trim(), Number(m[2]))
  }
  const diffs = []
  for (const [k, c] of hist) if (k !== '<unlabelled>' && census.get(k) !== c) diffs.push(`${k}: mine=${c} census=${census.get(k)}`)
  for (const [k, c] of census) if (!hist.has(k)) diffs.push(`${k}: mine=absent census=${c}`)
  result('census_keys', census.size)
  result('histogram_keys', [...hist.keys()].filter((k) => k !== '<unlabelled>').length)
  result('census_null_control_diffs', diffs.length)
  for (const d of diffs) console.log(`  DIFF ${d}`)

  result('api_failures', API_FAILURES)
  result('cache_dir', CACHE)
}

main()
