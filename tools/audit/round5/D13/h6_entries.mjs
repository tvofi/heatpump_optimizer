// The production friction-entry parser, driven from the file that owns it.
//
// WHY AN IMPORT HERE AND AN EVAL IN h1_grammar.mjs. `.claude/workflows/
// policy_lint.mjs` guards its `main()` on `process.argv[1]` and exports
// `frictionEntries`, so importing it is safe and the function this harness
// counts on IS the production one. `web-fix-wave.js` has no such guard, which
// is why the grammar is extracted there and imported here.
//
// The section split (a `## ` heading, code fences skipped) is NOT exported by
// policy_lint.mjs, so it is ported in `h6_friction.py` and the port is checked
// against the production CLI's own histogram, which prints the same keys: a
// port that missed a section would show up as a key count that disagrees with
// `node .claude/workflows/policy_lint.mjs --stats --since <ref>`.
//
// USAGE (from the repository root):
//   node h6_entries.mjs <partials.json> <out.json>
// <partials.json> is a JSON array of `## Friction` SECTION texts. Prints, to
// <out.json>, one array of production entries per input section:
// {line, id, event, evidence} exactly as `frictionEntries` returns them.

import fs from 'node:fs'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const ROOT = process.env.D13_ROOT || process.cwd()
const mod = await import(
  pathToFileURL(path.join(ROOT, '.claude', 'workflows', 'policy_lint.mjs')).href
)
if (typeof mod.frictionEntries !== 'function') {
  throw new Error(
    'policy_lint.mjs does not export frictionEntries: the harness would ' +
    'otherwise parse the entries with a copy of the grammar and report a ' +
    'count keyed on its own rewrite rather than on the production parser.'
  )
}
const sections = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))
const out = sections.map((s) => mod.frictionEntries(s))
fs.writeFileSync(process.argv[3], JSON.stringify(out))
const total = out.reduce((a, e) => a + e.length, 0)
process.stdout.write(`frictionEntries (production): ${sections.length} section(s), ${total} entry(ies)\n`)
