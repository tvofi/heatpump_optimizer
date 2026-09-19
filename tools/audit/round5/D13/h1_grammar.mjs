// The production verdict grammar, extracted from the file that owns it.
//
// WHY EXTRACTION AND NOT AN IMPORT. `.claude/workflows/web-fix-wave.js` is a
// Workflow script: its module scope drives the whole fix wave (`for (const g
// of groups)` runs agents), so importing it would dispatch a wave rather than
// read a regex. No script on this project exports VERDICT_RE. So the grammar is
// taken FROM THE PRODUCTION FILE, at run time, by evaluating the two
// declarations that define it -- `VERDICT_CLASSES` and `VERDICT_RE` -- out of
// the source. The count this feeds is therefore keyed on the production
// grammar: edit VERDICT_RE and every number that depends on it moves, which is
// the perturbation `h1_verdicts.py --perturb grammar` runs.
//
// The first-line rule is `web-fix-wave.js:parseVerdict`'s own: the verdict is
// the FIRST LINE of the comment, trimmed, and nothing after a newline is read.
//
// USAGE (from the repository root):
//   node tools/audit/round5/D13/h1_grammar.mjs <lines.json>
// <lines.json> is a JSON array of first-line strings. Prints, to stdout, a JSON
// object {classes, source, parsed: [{raw, verdict, class} | null]}.

import fs from 'node:fs'
import path from 'node:path'

const ROOT = process.env.D13_ROOT ||
  path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', '..', '..')
const FILE = process.env.D13_GRAMMAR_FILE ||
  path.join(ROOT, '.claude', 'workflows', 'web-fix-wave.js')

function loadGrammar() {
  const src = fs.readFileSync(FILE, 'utf8')
  const cls = src.match(/const VERDICT_CLASSES = (\[[\s\S]*?\n\])/)
  const re = src.match(/const VERDICT_RE = new RegExp\(\s*(`[\s\S]*?`)\s*,?\s*\)/)
  if (!cls || !re) {
    throw new Error(
      'the verdict grammar could not be read out of web-fix-wave.js: ' +
      'VERDICT_CLASSES and VERDICT_RE must both be present and shaped as ' +
      '`const X = [...]` / `const VERDICT_RE = new RegExp(`...`)`. ' +
      'A parse that returned nothing would report every verdict as outside ' +
      'the grammar, which reads as a coverage collapse rather than as a ' +
      'harness that could not look.'
    )
  }
  // eslint-disable-next-line no-eval
  const VERDICT_CLASSES = eval(cls[1])
  // eslint-disable-next-line no-eval
  const source = eval(re[1])
  return { VERDICT_CLASSES, VERDICT_RE: new RegExp(source), source }
}

const { VERDICT_CLASSES, VERDICT_RE, source } = loadGrammar()
const lines = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))
const parsed = lines.map((raw) => {
  const m = VERDICT_RE.exec(String(raw).trim())
  if (!m) return null
  return m[1]
    ? { verdict: 'merge', head_sha: m[2], class: null, why: null }
    : { verdict: 'blocked', head_sha: m[4], class: m[5], why: m[6].trim() }
})
process.stdout.write(JSON.stringify({ classes: VERDICT_CLASSES, source, parsed }))
