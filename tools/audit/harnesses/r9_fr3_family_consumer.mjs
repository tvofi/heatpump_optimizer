// R9-FR-3 (#1825) consumer instrument: the friction filer's parser over the
// family-folded stats output.
//
// WHAT IT PINS. policy_lint.mjs --stats gained additive family rows (CENSUS
// kind `verdict family`, key `<name> (family)`) and family would-open lines.
// `friction_issues.mjs` reads that output and its input contract must not
// change shape: the census summary must still equal the rows parsed, and the
// would-open line must still parse to a key, kind, count and threshold. This
// harness drives the REAL parseHistogram over a family-shaped histogram and
// asserts both, offline -- the live `--dry-run` half reads the repository, so
// the offline parse is the reproducible half.
//
// The entry-strip: friction_issues.mjs runs `run(argv)` unconditionally on
// import (no import.meta guard), so importing it as a module executes the
// filer. The copy below deletes only that one dispatch line; parseHistogram
// and every other export are byte-identical to the tree's file, read live at
// each run -- a parser change is measured, never a copy frozen here.
//
//    node tools/audit/harnesses/r9_fr3_family_consumer.mjs
//
// exit 0: the consumer parses the family output unchanged; exit 1: it does not.

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..')
const src = fs.readFileSync(path.join(ROOT, '.claude/workflows/friction_issues.mjs'), 'utf8')
const entry = 'run(argv)'
if (!src.includes(entry)) {
  console.error('consumer harness: friction_issues.mjs no longer dispatches via run(argv); re-point the strip')
  process.exit(1)
}
const tmp = path.join(os.tmpdir(), `r9fr3-consumer-${process.pid}.mjs`)
fs.writeFileSync(tmp, src.replace(entry, '// entry stripped for the offline consumer probe'))

// The exact shapes the family fold prints: additive CENSUS rows of kind
// `verdict family` and `friction family` (the environment siblings live in the
// friction-id histogram, not the verdict histogram), the summary count
// including them, and one would-open line per kind keyed `<name> (family)`.
// The verdict counts are the measured since-v6.7.14 window's (4 distinct PRs /
// 5 entries); the id counts are the since-v6.7.13 window's shape (environment
// 4, seat-environment 1) shrunk to a minimal 3-PR composition, so the text is
// a record, not a guess.
const text = [
  'STATS: 26 merged pull request(s) in v6.7.14..origin/main; verdict grammar ["blocked","merge"] over block classes ["mutation-vacuous"] read from .claude/workflows/web-fix-wave.js',
  'CENSUS\tverdict class\t2\t2\tmutation',
  'CENSUS\tverdict class\t1\t2\tmutation-survivor',
  'CENSUS\tverdict class\t1\t1\tmutation-vacuous',
  'CENSUS\tverdict family\t4\t5\tmutation (family)',
  'CENSUS\tfriction rule id\t2\t2\tenvironment',
  'CENSUS\tfriction rule id\t1\t1\tseat-environment',
  'CENSUS\tfriction family\t3\t3\tenvironment (family)',
  'CENSUS: 7 key(s)',
  '',
  'threshold: 3 or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.',
  '(window)',
  '  INFO    [stats] (window): would open "[policy] recurring friction: mutation (family)" -- verdict family at 4 in this window, threshold 3. The family folds the sibling keys the exact ids split across (FRICTION_FAMILIES), counted as DISTINCT pull requests across them (5 entries in all); it fires once, whatever its members do alone. Not opened here: a seat measures and files, a report does not.',
  '  INFO    [stats] (window): would open "[policy] recurring friction: environment (family)" -- friction family at 3 in this window, threshold 3. The family folds the sibling keys the exact ids split across (FRICTION_FAMILIES), counted as DISTINCT pull requests across them (3 entries in all); it fires once, whatever its members do alone. Not opened here: a seat measures and files, a report does not.',
  '',
  'WOULD OPEN: 2 issue(s)',
].join('\n')

let fail = 0
const st = (ok, label) => {
  console.log(`${ok ? 'ok' : 'FAIL'}  ${label}`)
  if (!ok) fail = 1
}
try {
  const { parseHistogram } = await import(pathToFileURL(tmp))
  const p = parseHistogram(text)
  st(p.ok === true, `parseHistogram accepts the family-shaped output (why: ${JSON.stringify(p.why)})`)
  st(p.census.size === 7, `census rows parsed = declared 7 (got ${p.census.size}); the summary-count invariant friction_issues refuses on still holds`)
  const row = p.census.get('mutation (family)')
  st(row && row.kind === 'verdict family' && row.prs === 4 && row.entries === 5, `verdict family census row readable for the close path (got ${JSON.stringify(row)})`)
  const idRow = p.census.get('environment (family)')
  st(idRow && idRow.kind === 'friction family' && idRow.prs === 3 && idRow.entries === 3, `friction family census row readable for the close path (got ${JSON.stringify(idRow)})`)
  st(p.entries.length === 2 &&
    p.entries[0].key === 'mutation (family)' && p.entries[0].kind === 'verdict family' && p.entries[0].count === 4 && p.entries[0].threshold === 3 &&
    p.entries[1].key === 'environment (family)' && p.entries[1].kind === 'friction family' && p.entries[1].count === 3 && p.entries[1].threshold === 3,
  `both family would-open lines parse to key/kind/count/threshold (got ${JSON.stringify(p.entries)})`)

  // The detector's own control: the same output with the summary line NOT
  // counting the family rows -- the exact producer regression this harness
  // exists to catch -- must refuse, not pass. A control that passed would make
  // the ok lines above a shape check over a fixture, not a detector.
  const broken = text.replace('CENSUS: 7 key(s)', 'CENSUS: 5 key(s)')
  const q = parseHistogram(broken)
  st(q.ok === false && /declares 5 key\(s\) and 7 row\(s\) parsed/.test(q.why), `a producer that prints the family row without counting it refuses (why: ${JSON.stringify(q.why)})`)
} finally {
  fs.rmSync(tmp, { force: true })
}
process.exit(fail)
