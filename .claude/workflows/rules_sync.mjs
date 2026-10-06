// Generate `.claude/rules/*.md` and `.cursor/rules/*.mdc` from
// `dev/governance/rules/*.md` (tvofi's D1, R9-RO-5).
//
// The canonical rule text lives under dev/governance/rules/. Claude Code loads
// `.claude/rules/*.md` and Cursor loads `.cursor/rules/*.mdc`, so both are
// generated and `--check` refuses drift in either. policy_lint treats the
// generated `.claude` copy as it treats `.cursor`: the source is what is
// measured, and an edit at the generated path is this script's refusal.
//
//   node .claude/workflows/rules_sync.mjs           # regenerate
//   node .claude/workflows/rules_sync.mjs --check   # refuse if out of date
//
// The `.claude` copy is the source bytes. The `.cursor` copy is the same body
// with Cursor's frontmatter. Only the frontmatter differs there, because the
// two loaders spell the same idea differently. Cursor has no lazy tier, so
// every generated rule keeps `alwaysApply: true` and carries the paths as its
// `globs`.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseRuleFrontmatter } from './policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
// The source directory, not `at()`: a generated file still sits at the old
// path, and locate prefers a file that is already there, which would make
// this script read its own output.
const SRC = path.join(ROOT, 'dev', 'governance', 'rules')
const CLAUDE_OUT = path.join(ROOT, '.claude', 'rules')
const CURSOR_OUT = path.join(ROOT, '.cursor', 'rules')

function parse(text, rel) {
  return parseRuleFrontmatter(text, rel)
}

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
    .map((f) => ({ stem: f.replace(/\.md$/, ''), rel: `dev/governance/rules/${f}` }))
}

function main() {
  const check = process.argv.includes('--check')
  let drift = 0
  let wrote = 0
  const expectedMd = new Set()
  const expectedMdc = new Set()

  for (const { stem, rel } of sources()) {
    const raw = fs.readFileSync(path.join(ROOT, rel), 'utf8')
    const claudeRel = `.claude/rules/${stem}.md`
    const cursorRel = `.cursor/rules/${stem}.mdc`
    expectedMd.add(`${stem}.md`)
    expectedMdc.add(`${stem}.mdc`)
    const wantCursor = render(parse(raw, rel))
    for (const [outRel, want] of [[claudeRel, raw], [cursorRel, wantCursor]]) {
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
  }

  // A generated file with no source is a hand-written rule that survived, or
  // a rule whose source was deleted without its output.
  if (fs.existsSync(CLAUDE_OUT)) {
    for (const f of fs.readdirSync(CLAUDE_OUT).filter((x) => x.endsWith('.md')).sort()) {
      if (expectedMd.has(f)) continue
      console.log(`ORPHAN .claude/rules/${f}: no dev/governance/rules/ source generates it`)
      drift++
    }
  }
  if (fs.existsSync(CURSOR_OUT)) {
    for (const f of fs.readdirSync(CURSOR_OUT).filter((x) => x.endsWith('.mdc')).sort()) {
      if (expectedMdc.has(f)) continue
      console.log(`ORPHAN .cursor/rules/${f}: no dev/governance/rules/ source generates it`)
      drift++
    }
  }

  if (check) {
    console.log(drift ? `\nRULES-SYNC: ${drift} file(s) out of date. Run without --check.` : '\nRULES-SYNC ok: every generated rule is the generated form of its source')
    process.exit(drift ? 1 : 0)
  }
  console.log(`\nRULES-SYNC: ${wrote} file(s) written, ${sources().length} source(s)`)
}

export { parse, render, sources }

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
