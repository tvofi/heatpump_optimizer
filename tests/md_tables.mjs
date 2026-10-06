// Round 9 F8.2 add-on (from the F8.1 review; class N-markdown, #1674): a
// permanent CI gate for the D5-s1 finder's GFM-table-integrity harness
// (tools/audit/round9/D5/s1/md_tables.mjs, evidence commit 79aa98ec).
//
// Metric (one line, unchanged from the finder): source lines in README.md +
// docs/{architecture,automations,configuration,dashboard-card,ecl110,
// how-it-works,setup}.md that render in the wrong block -- (a) prose lines
// (not starting with "|") rendered as table rows ("swallowed"), plus (b)
// pipe-table rows rendered as paragraph text with raw pipes ("orphaned")
// because no header/delimiter row governs them.
// Count key: the markdown-it token stream (tr_open / paragraph map), i.e.
// what the renderer delivers, never the raw source shape alone -- the same
// distinction render_md.mjs (#682) draws for the other reader docs.
//
// Unlike the finder's copy under tools/audit/round9/ (evidence-only, not in
// main's tree, and needing a throwaway `npm install markdown-it@14.1.0`),
// this gate reaches the SAME vendored 14.1.0 build already checked in for
// render_md.mjs, so it runs offline in the scoped gate and in CI with no
// network step:
//   node tests/md_tables.mjs
// `--self-test` runs the null control only (see below) and exits without
// touching the real docs.
//
// Expected clean: misrendered_lines=0 (swallowed=0, orphaned=0). D5-s1-04
// (baseline 1936d5ca) measured misrendered_lines=9 in docs/configuration.md
// alone (the anti-legionella rows at :181-187, orphaned; the fuel-price
// prose at :633-638, swallowed); F8.1 (#1696) fixed those two, and the sweep
// (S6, 6b65c9c4a8) found no other instance across the other 7 files.
import fs from 'node:fs'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const MarkdownIt = require(fs.existsSync(new URL('../.claude/workflows/vendor/markdown-it.min.js', import.meta.url))
  ? '../.claude/workflows/vendor/markdown-it.min.js'
  : '../tools/policy/vendor/markdown-it.min.js')
const md = new MarkdownIt('commonmark').enable('table')

const FILES = [
  'README.md',
  ...['architecture', 'automations', 'configuration', 'dashboard-card',
    'ecl110', 'how-it-works', 'setup'].map((n) => `docs/${n}.md`),
]

export function analyse(text) {
  const lines = text.split('\n')
  const toks = md.parse(text, {})
  const inTable = new Set()
  const inCode = new Set()
  const swallowed = []
  const orphaned = []
  for (const t of toks) {
    if (t.type === 'table_open') {
      for (let i = t.map[0]; i < t.map[1]; i++) inTable.add(i)
    }
    if ((t.type === 'fence' || t.type === 'code_block' || t.type === 'html_block') && t.map) {
      for (let i = t.map[0]; i < t.map[1]; i++) inCode.add(i)
    }
    if (t.type === 'tr_open' && t.map && !lines[t.map[0]].trim().startsWith('|')) {
      swallowed.push(t.map[0])
    }
  }
  lines.forEach((l, i) => {
    if (l.trim().startsWith('|') && !inTable.has(i) && !inCode.has(i)) orphaned.push(i)
  })
  return { lines, swallowed, orphaned }
}

function report(files) {
  let sw = 0
  let orph = 0
  for (const [name, text] of files) {
    const { lines, swallowed, orphaned } = analyse(text)
    for (const i of swallowed) console.log(`swallowed ${name}:${i + 1}: ${lines[i].slice(0, 70)}`)
    for (const i of orphaned) console.log(`orphaned  ${name}:${i + 1}: ${lines[i].slice(0, 70)}`)
    sw += swallowed.length
    orph += orphaned.length
  }
  console.log(`RESULT doc_files_checked=${files.length} count`)
  console.log(`RESULT doc_swallowed_prose_lines=${sw} count`)
  console.log(`RESULT doc_orphaned_table_rows=${orph} count`)
  console.log(`RESULT doc_misrendered_lines=${sw + orph} count`)
  return sw + orph
}

// Null control: the exact anti-legionella (orphaned) and fuel-price
// (swallowed) shapes D5-s1-04 measured at baseline 1936d5ca, reintroduced
// as a synthetic document -- proof the gate fires on the shape it exists to
// catch, not only that the current docs happen to be clean.
const SELF_TEST_BAD = [
  '# Configuration',
  '',
  '| Day | Legionella cycle |',
  '|---|---|',
  '| Monday | 60 °C for 1 h |',
  '',
  'A short paragraph that separates the two tables in the source.',
  '| Tuesday | Skipped |',
  '| Wednesday | Skipped |',
  '',
  '## Fuel price',
  '',
  '| Field | Default |',
  '|---|---|',
  '| Price per litre | 12 SEK |',
  'A prose sentence glued directly under the table with no blank line, so',
  'the renderer reads it as another row instead of a paragraph.',
  '',
].join('\n')

function selfTest() {
  const { swallowed, orphaned } = analyse(SELF_TEST_BAD)
  const ok = swallowed.length >= 1 && orphaned.length >= 1
  console.log(`RESULT self_test_swallowed=${swallowed.length} count`)
  console.log(`RESULT self_test_orphaned=${orphaned.length} count`)
  console.log(`RESULT self_test_fires=${ok}`)
  if (!ok) {
    console.error('md_tables self-test FAILED: the gate does not fire on its own reintroduced misrender')
    return 1
  }
  return 0
}

function main() {
  const selfTestOnly = process.argv.includes('--self-test')
  const selfTestRc = selfTest()
  if (selfTestOnly) return selfTestRc
  const files = FILES.map((f) => [f, fs.readFileSync(f, 'utf8')])
  const misrendered = report(files)
  if (selfTestRc !== 0) return selfTestRc
  if (misrendered !== 0) {
    console.error(`md_tables: ${misrendered} misrendered line(s); see swallowed/orphaned lines above`)
    return 1
  }
  return 0
}

process.exit(main())
