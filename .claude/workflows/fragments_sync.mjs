#!/usr/bin/env node
// Are the five web-*.js copies of the shared prompt block still the canonical text?
//
// WHY BY HAND AT ALL. A workflow script here is evaluated as a function body
// handed `args`/`agent()`/`phase()`, with a top-level `return`, so a static
// `import` is not legal syntax in one. The five `web-*.js` scripts therefore
// each carry their own copy of the block in `web-fragments.md`, and that file
// says in as many words: "Keep the copies in sync by hand." Nothing checked it.
//
// The block is not decoration. It tells a seat that `/tmp/hpo-gate.lock` exists
// because `tests/stress.py` measures the machine while it solves, and what to do
// when the lock is held -- the subject of a 113-minute incident. A copy that
// drifts hands one seat a different rule from its neighbours, silently.
//
// WHAT IT COMPARES. Every top-level `const NAME` declaration inside the fenced
// block in `web-fragments.md` is canonical. Each `web-*.js` that declares the
// same name must carry byte-identical text. A script may omit a fragment it does
// not use; it may not carry a different one.
//
// A declaration runs from its `const NAME` line to the line before the next
// top-level `const` or comment banner, which is the convention both files
// already follow. Where that boundary cannot be found, this refuses rather than
// comparing a truncated fragment: a comparison of the wrong text is not a pass.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
const CANON = '.claude/workflows/web-fragments.md'
const COPIES = /^web-.*\.js$/

const read = (rel) => {
  try { return fs.readFileSync(path.join(ROOT, rel), 'utf8') } catch { return null }
}

const DECL = /^const ([A-Za-z_][A-Za-z0-9_]*)\b/
// A banner ends a declaration as surely as the next one does. Without this the
// last fragment in a file swallows every comment beneath it and reports drift
// against text nobody wrote.
const ENDS = (line) => DECL.test(line) || /^\/\/ ---/.test(line) || /^```/.test(line)

// Returns a Map name -> exact text, and the list of names in order. Splitting is
// shared by both sides on purpose: a canonical parsed one way and a copy parsed
// another would compare two different things and call the difference drift.
function declarations(lines) {
  const out = new Map()
  let name = null
  let buf = []
  const flush = () => { if (name) out.set(name, buf.join('\n').replace(/\s+$/, '')) }
  for (const line of lines) {
    const m = DECL.exec(line)
    if (m) { flush(); name = m[1]; buf = [line]; continue }
    if (name && ENDS(line)) { flush(); name = null; buf = []; continue }
    if (name) buf.push(line)
  }
  flush()
  return out
}

function canonical() {
  const raw = read(CANON)
  if (raw == null) return { error: `${CANON} is not in the tree` }
  const m = /\n```js\n([\s\S]*?)\n```\n/.exec(raw)
  if (!m) return { error: `${CANON} has no \`\`\`js block, so there is no canonical text to compare against` }
  const decls = declarations(m[1].split('\n'))
  if (!decls.size) return { error: `${CANON}'s js block declares no top-level const, so this check would compare nothing` }
  return { decls }
}

function findings(canonDecls, files) {
  const out = []
  for (const rel of files) {
    const raw = read(rel)
    if (raw == null) continue
    const decls = declarations(raw.split('\n'))
    for (const [name, want] of canonDecls) {
      if (!decls.has(name)) continue
      const got = decls.get(name)
      if (got === want) continue
      const w = want.split('\n')
      const g = got.split('\n')
      const at = w.findIndex((l, i) => l !== g[i])
      out.push({
        file: rel,
        name,
        detail: w.length !== g.length && at === -1
          ? `${g.length} lines against the canonical ${w.length}`
          : `first differs at line ${at + 1} of the fragment:\n      canonical: ${JSON.stringify((w[at] ?? '').trim().slice(0, 90))}\n      copy:      ${JSON.stringify((g[at] ?? '').trim().slice(0, 90))}`,
      })
    }
  }
  return out
}

const copyFiles = () =>
  fs.readdirSync(path.join(ROOT, '.claude', 'workflows'))
    .filter((f) => COPIES.test(f))
    .sort()
    .map((f) => `.claude/workflows/${f}`)

// A check that cannot be shown failing does not merge. The canonical text is
// perturbed in memory -- one character in one fragment -- and every script that
// carries that fragment must be reported. Perturbing the CANONICAL rather than a
// copy is deliberate: it is the direction the tree actually drifted (all five
// copies agreed with each other and disagreed with the file calling itself
// canonical), and it exercises the comparison for every copy at once.
function selfTest(canonDecls, files) {
  let pass = 0
  let fail = 0
  const ok = (cond, what) => { if (cond) { pass += 1; console.log(`  ok   ${what}`) } else { fail += 1; console.log(`  FAIL ${what}`) } }

  ok(findings(canonDecls, files).length === 0, 'the tree as committed reports no drift (null control)')

  const name = [...canonDecls.keys()].find((n) => files.some((f) => declarations((read(f) || '').split('\n')).has(n)))
  ok(!!name, 'at least one canonical fragment is carried by a script, so there is something to compare')
  if (name) {
    const carriers = files.filter((f) => declarations((read(f) || '').split('\n')).has(name))
    const bent = new Map(canonDecls)
    bent.set(name, canonDecls.get(name).replace(/^const /, 'const  '))
    const hits = findings(bent, files)
    ok(hits.length === carriers.length,
      `one character changed in \`${name}\` is reported for all ${carriers.length} script(s) carrying it (got ${hits.length})`)
    ok(hits.every((h) => h.name === name), 'and for no other fragment')
  }

  // The parser is the half that can silently measure nothing. A canonical block
  // whose declarations cannot be found is not a clean tree.
  ok(declarations(['const A = `x`', 'more', 'const B = 1']).size === 2, 'two declarations split into two')
  ok(declarations(['const A = `x`', 'more', '// ---- banner', 'trailing']).get('A') === 'const A = `x`\nmore',
    'a comment banner ends a declaration rather than being absorbed into it')
  ok(declarations([]).size === 0, 'an empty file declares nothing rather than throwing')

  console.log(`\n${pass} passed, ${fail} failed`)
  return fail ? 2 : 0
}

const { decls, error } = canonical()
if (error) {
  console.log(`FRAGMENTS: ${error}`)
  process.exit(1)
}
const files = copyFiles()
if (process.argv.includes('--self-test')) process.exit(selfTest(decls, files))

const hits = findings(decls, files)
for (const h of hits) console.log(`  DRIFT   ${h.file}: \`${h.name}\` ${h.detail}`)
if (hits.length) {
  console.log(`\nFRAGMENTS: ${hits.length} copy(ies) differ from ${CANON}. That file is the canonical text; change it there and copy it out, never the other way, or the next script to be edited reinstates the drift.`)
  process.exit(1)
}
console.log(`FRAGMENTS ok: ${decls.size} canonical fragment(s) [${[...decls.keys()].join(', ')}] match every copy across ${files.length} script(s)`)
