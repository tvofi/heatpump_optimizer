// Generate `.cursor/rules/*.mdc` from `.claude/rules/*.md`.
//
// WHY THIS EXISTS. The five project policies were reachable by a Claude Code
// seat only if it chose to open `.cursor/rules/` and read them -- the harness
// loads `CLAUDE.md` and nothing else, and `.mdc` is a Cursor format Claude Code
// ignores entirely. So five `alwaysApply` policies applied to nobody in this
// environment. `.claude/rules/*.md` IS loaded: a rule with no `paths` key at
// session start, and a `paths`-scoped rule when the seat reads a file matching
// one of its globs.
//
// That leaves two copies of one policy, which is the corpus's largest measured
// defect class. So one is canonical and the other is generated: `.claude/rules/`
// is the source, `.cursor/rules/` is output, and `--check` refuses any drift
// between them.
//
//   node .claude/workflows/rules_sync.mjs           # regenerate
//   node .claude/workflows/rules_sync.mjs --check   # refuse if out of date
//
// The bodies are byte-identical by construction; only the frontmatter differs,
// because the two loaders spell the same idea differently. Cursor has no lazy
// tier, so every generated rule keeps `alwaysApply: true` and carries the paths
// as its `globs` -- a Cursor seat therefore sees strictly more than a Claude
// Code seat, which is the safe direction for a rule.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseRuleFrontmatter } from './policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
const SRC = path.join(ROOT, '.claude', 'rules')
const OUT = path.join(ROOT, '.cursor', 'rules')

// D11-s1-71: this used to run its own `/^\s*-\s*"([^"]+)"\s*$/gm` over the
// whole frontmatter block, which disagreed with `policy_lint.mjs`'s reader on
// two of six shapes the sweep drove -- a trailing comment on a path line (the
// line-end anchor rejected it) and a list item under a key other than `paths:`
// (the whole-block scan collected it as if it were one). Import the one
// reader both files now use rather than keep a second copy of it.
function parse(text, rel) {
  return parseRuleFrontmatter(text, rel)
}

// The generated form. `globs` is comma-joined without spaces, which is how the
// hand-written files spelled it and what Cursor parses.
function render({ description, paths, body }) {
  const head = ['---', `description: ${description}`]
  if (paths.length) head.push(`globs: ${paths.join(',')}`)
  head.push('alwaysApply: true', '---', '')
  return head.join('\n') + body
}

function sources() {
  if (!fs.existsSync(SRC)) return []
  return fs
    .readdirSync(SRC)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => ({ stem: f.replace(/\.md$/, ''), rel: `.claude/rules/${f}` }))
}

// I4 carry-in (RCA, 2026-09-26): this ran unconditionally at module scope, so
// merely IMPORTING this file for its parser (as F11.4's agreement lane, and
// this PR's own `parse`, need to) wrote `.cursor/rules/*.mdc` as a side
// effect of being read. Guarded behind `main()` like `policy_lint.mjs` is, so
// a seat can import `parse`/`render`/`sources` without triggering a write.
function main() {
  const check = process.argv.includes('--check')
  let drift = 0
  let wrote = 0
  const expected = new Set()

  for (const { stem, rel } of sources()) {
    const want = render(parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'), rel))
    const outRel = `.cursor/rules/${stem}.mdc`
    expected.add(`${stem}.mdc`)
    const outAbs = path.join(ROOT, outRel)
    const have = fs.existsSync(outAbs) ? fs.readFileSync(outAbs, 'utf8') : null
    if (have === want) continue
    if (check) {
      console.log(`DRIFT ${outRel}: ${have === null ? 'missing' : 'differs from'} the generated form of ${rel}`)
      drift++
    } else {
      fs.mkdirSync(path.dirname(outAbs), { recursive: true })
      fs.writeFileSync(outAbs, want)
      console.log(`wrote ${outRel}`)
      wrote++
    }
  }

  // A `.mdc` with no source is a hand-written rule that survived the conversion,
  // or a rule whose source was deleted without its output. Either way a seat is
  // reading something nothing generates, which is the state this script exists to
  // end.
  if (fs.existsSync(OUT)) {
    for (const f of fs.readdirSync(OUT).filter((x) => x.endsWith('.mdc')).sort()) {
      if (expected.has(f)) continue
      console.log(`ORPHAN .cursor/rules/${f}: no .claude/rules/ source generates it`)
      drift++
    }
  }

  if (check) {
    console.log(drift ? `\nRULES-SYNC: ${drift} file(s) out of date. Run without --check.` : '\nRULES-SYNC ok: every .cursor rule is the generated form of its source')
    process.exit(drift ? 1 : 0)
  }
  console.log(`\nRULES-SYNC: ${wrote} file(s) written, ${sources().length} source(s)`)
}

export { parse, render, sources }

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
