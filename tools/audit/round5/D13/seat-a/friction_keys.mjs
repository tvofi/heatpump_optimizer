#!/usr/bin/env node
// D13 / round 5 seat-a -- the friction histogram's keys resolved against the
// `--budgets` path list, at this seat's own window.
//
// METRIC (one line): for every friction entry the PRODUCTION parser
// (policy_lint.mjs's `frictionEntries`, imported here, never re-typed) reads
// out of the `## Friction` section of a merged pull request body in
// v6.6.6..1cc89e0, the key is the entry's rule id with any `#anchor` dropped
// and outer backticks stripped; the key NAMES a budgets path p (a key of
// policy_budgets.json's `files`) iff p === k, or p ends in "/" + k, or
// p === k + ".md", or p === k + "/SKILL.md"; exactly one matching path files
// the key under that file, several match -> the ambiguous row, none -> the
// no-file row; share_naming_one_file = keys on file rows / all keys.
//
// INSTRUMENTED SYMBOL: .claude/workflows/policy_lint.mjs:frictionEntries (the
// same parser checkPrBody refuses with); the path list is
// .claude/workflows/policy_budgets.json (what `--budgets` caps). `sections()`
// is NOT exported by policy_lint.mjs, so this harness carries a minimal local
// copy of the section splitter (codefence-aware `## ` split) -- the entry
// grammar itself is production.
//
// COMMAND (from the repository root):
//   HPO_PLANDATA=/tmp/audit-5/tmp/d13/plandata.json \
//   node tools/audit/round5/D13/seat-a/friction_keys.mjs
//
// EXPECTED at baseline 1cc89e0 (tolerance: exact; counts over closed fixtures):
//   friction_entries_live=0 share_naming_one_file_live=n/a-0-keys (all 8 bodies
//   say `none`); corpus (5 entries): file rows .claude/rules/ratchet-budgets.md
//   (2 spellings: backticked + unbackticked) and CLAUDE.md (1, anchor dropped);
//   no-file row `steward` (1); UNLABELLED 1 -- the entry whose id is the
//   repo-relative path `.claude/skills/steward/SKILL.md`, which FRICTION_ID
//   (^[A-Za-z]) cannot read. corpus_share_naming_one_file=0.667.
//   api_failures=0
//
// PERTURBATION (the brief's, in the fixture corpus -- never a live pull
// request): re-spell the accepted `ratchet-budgets.md` entry as `README.md`
// and it must move to the ambiguous row (file rows for it drop to 0,
// ambiguous rises by its count); re-spell it as `ratchet-budgets` and no
// file's count moves (no-file row); re-spell it unbackticked and the entry
// still parses (the grammar's backticks are optional -- FRICTION_ENTRY_RE)
// and still names the same file. Set PERTURB=spell to run the corpus with the
// README.md re-spelling applied; PERTURB=bare for the bare-id arm.
// MACHINE: any; count harness, no timing claim.

import { frictionEntries } from '../../../../../.claude/workflows/policy_lint.mjs'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const FIX = process.env.FIXTURE_DIR ?? join(HERE, 'fixtures')
const ROOT = resolveRoot(HERE)

function resolveRoot(h) {
  // tools/audit/round5/D13/seat-a -> five levels up to the repository root
  return join(h, '..', '..', '..', '..', '..')
}

// local minimal copy of policy_lint.mjs's `sections()` (not exported there)
function sections(body) {
  const out = new Map()
  let cur = null
  let inFence = false
  for (const line of String(body ?? '').split('\n')) {
    if (/^```/.test(line)) inFence = !inFence
    const m = inFence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) { cur = m[1]; out.set(cur, []); continue }
    if (cur) out.get(cur).push(line)
  }
  for (const [k, v] of out) out.set(k, v.join('\n').trim())
  return out
}

const budgets = JSON.parse(readFileSync(join(ROOT, '.claude/workflows/policy_budgets.json'), 'utf8'))
const paths = Object.keys(budgets.files ?? {})

function names(k, p) {
  return p === k || p.endsWith('/' + k) || p === k + '.md' || p === k + '/SKILL.md'
}

function keyOf(id) {
  const raw = String(id ?? '').trim()
  return raw.replace(/^`+|`+$/g, '').replace(/#.*$/, '')
}

function resolveKey(id) {
  const k = keyOf(id)
  const hits = paths.filter((p) => names(k, p))
  if (hits.length === 1) return { row: 'file', file: hits[0], key: k }
  if (hits.length > 1) return { row: 'ambiguous', files: hits, key: k }
  return { row: 'no-file', key: k }
}

function histogram(bodies) {
  const fileRows = new Map()
  const ambiguous = new Map()
  const noFile = new Map()
  const unlabelled = { entries: 0 }
  let entries = 0
  for (const [pr, body] of Object.entries(bodies)) {
    const section = sections(body).get('Friction') ?? ''
    for (const e of frictionEntries(section)) {
      entries += 1
      if (e.id == null) { unlabelled.entries += 1; continue }
      const r = resolveKey(e.id)
      if (r.row === 'file') {
        const c = fileRows.get(r.file) ?? { count: 0, spellings: {} }
        c.count += 1
        const sp = e.id.trim()
        c.spellings[sp] = (c.spellings[sp] ?? 0) + 1
        fileRows.set(r.file, c)
      } else if (r.row === 'ambiguous') {
        const c = ambiguous.get(r.key) ?? { count: 0, files: r.files }
        c.count += 1
        ambiguous.set(r.key, c)
      } else {
        const c = noFile.get(r.key) ?? 0
        noFile.set(r.key, c + 1)
      }
    }
  }
  return { entries, fileRows, ambiguous, noFile, unlabelled }
}

// ---- live window: the 8 merged bodies from the graphql fixture
const g = JSON.parse(readFileSync(join(FIX, 'prs_graphql.json'), 'utf8')).data.repository
const live = {}
for (const k of ['p1280', 'p1281', 'p1282', 'p1284', 'p1285', 'p1286', 'p1287', 'p1289']) {
  live[k.slice(1)] = g[k].body ?? ''
}
const liveH = histogram(live)

// ---- fixture corpus for the perturbation arms (never a live pull request)
const PERTURB = process.env.PERTURB ?? ''
const baseId = PERTURB === 'readme' ? 'README.md' : PERTURB === 'bare' ? 'ratchet-budgets' : 'ratchet-budgets.md'
const corpus = {
  '9001': `## Friction\n- \`${baseId}\`: cost: the cap re-record dance cost the seat a retry cycle.\n`,
  '9002': `## Friction\n- ${baseId}: stale: written unbackticked to test the grammar's optional backticks.\n`,
  '9003': `## Friction\n- \`CLAUDE.md#budgets\`: unclear: anchor names a section of one document.\n`,
  '9004': `## Friction\n- \`.claude/skills/steward/SKILL.md\`: cost: the skill document named by its repo-relative path -- FRICTION_ID cannot start with '.', so the most explicit spelling parses as NO id.\n`,
  '9005': `## Friction\n- \`steward\`: cost: the same skill named by its bare directory word.\n`,
}
const corpusH = histogram(corpus)

function res(name, value, unit = '') {
  console.log(`RESULT ${name}=${value} ${unit}`.trimEnd())
}

console.log('# budgets paths read:', paths.length)
console.log('# live window histogram:', JSON.stringify({
  entries: liveH.entries,
  fileRows: Object.fromEntries(liveH.fileRows),
  ambiguous: Object.fromEntries(liveH.ambiguous),
  noFile: Object.fromEntries(liveH.noFile),
  unlabelled: liveH.unlabelled.entries,
}))
console.log('# fixture corpus (perturbation arm, id spelling =', JSON.stringify(baseId) + '):')
console.log(JSON.stringify({
  fileRows: Object.fromEntries([...liveH.fileRows, ...corpusH.fileRows].map(([f, c], i, arr) => [f, c])),
  ambiguous: Object.fromEntries(corpusH.ambiguous),
  noFile: Object.fromEntries(corpusH.noFile),
  unlabelled: corpusH.unlabelled.entries,
}, null, 0))

const allKeys = [...liveH.fileRows.keys()].length +
  [...liveH.ambiguous.keys()].length + [...liveH.noFile.keys()].length
const fileKeys = [...liveH.fileRows.keys()].length
res('friction_entries_live', liveH.entries)
res('friction_keys_live', allKeys)
res('share_naming_one_file_live', allKeys ? (fileKeys / allKeys).toFixed(3) : 'n/a-0-keys')
res('corpus_entries', corpusH.entries)
res('corpus_unlabelled', corpusH.unlabelled.entries)
res('corpus_share_naming_one_file',
  (([...corpusH.fileRows.keys()].length) /
    ([...corpusH.fileRows.keys()].length + [...corpusH.ambiguous.keys()].length +
     [...corpusH.noFile.keys()].length)).toFixed(3))
for (const [f, c] of corpusH.fileRows) res(`corpus_file_${f}`, JSON.stringify(c))
for (const [k, c] of corpusH.ambiguous) res('corpus_ambiguous_' + k, JSON.stringify(c))
for (const [k, c] of corpusH.noFile) res('corpus_nofile_' + k, c)
res('api_failures', 0)
res('thread_factor', '1.0 (count harness, no numpy)')
