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
import { execFileSync } from 'node:child_process'

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

// Decision 0009 step 5 leaves the deploy key as main's only direct-push bypass,
// so a stamp `--push` with no `--push-key` beside it is refused at the push.
// Scanned: every tracked file under .claude/workflows/ and tools/, not only the
// fragments -- a retired script carried one. stamp.py and this file are skipped:
// their usage line and self-tests name `--push` alone. A `--push` is a stamp push
// when `stamp.py` precedes it by at most 400 characters with no sentence end
// between, and is keyed when `--push-key` follows within 40 characters.
const STAMP_EXEMPT = new Set(['tools/release/stamp.py', '.claude/workflows/fragments_sync.mjs'])
function keylessStampPushes(texts) {
  const out = []
  for (const [rel, raw] of texts) {
    if (STAMP_EXEMPT.has(rel)) continue
    for (const m of raw.matchAll(/--push(?![\w-])/g)) {
      const before = raw.slice(Math.max(0, m.index - 400), m.index)
      const at = before.lastIndexOf('stamp.py')
      if (at < 0 || /[.!?]\s/.test(before.slice(at + 8))) continue
      if (raw.slice(m.index + 6, m.index + 46).includes('--push-key')) continue
      out.push(`${rel}:${raw.slice(0, m.index).split('\n').length}`)
    }
  }
  return out
}
const trackedTexts = () =>
  execFileSync('git', ['ls-files', '-z', '.claude/workflows', 'tools'], { cwd: ROOT, encoding: 'utf8' })
    .split('\0').filter(Boolean).map((rel) => [rel, read(rel) ?? ''])

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

  ok(grantSplit(canonDecls).length === 0, 'GH_READ and GH_MERGE are split (null control)')
  const bentRead = new Map(canonDecls)
  bentRead.set('GH_READ', `${canonDecls.get('GH_READ') || ''}\nmerge_pull_request`)
  ok(grantSplit(bentRead).some((e) => /GH_READ holds/.test(e)),
    'putting merge_pull_request in GH_READ is reported')
  const bentMerge = new Map(canonDecls)
  bentMerge.set('GH_MERGE', `${canonDecls.get('GH_MERGE') || ''}\nissue_read`)
  ok(grantSplit(bentMerge).some((e) => /GH_MERGE holds/.test(e)),
    'putting issue_read in GH_MERGE is reported')
  const bentWrite = new Map(canonDecls)
  bentWrite.set('GH_WRITE', `${canonDecls.get('GH_WRITE') || ''}\nmerge_pull_request`)
  ok(grantSplit(bentWrite).some((e) => /GH_WRITE holds/.test(e)),
    'putting merge_pull_request in GH_WRITE is reported')

  const texts = trackedTexts()
  ok(keylessStampPushes(texts).length === 0, 'no tracked stamp --push lacks --push-key (null control)')
  for (const ex of STAMP_EXEMPT) {
    ok(keylessStampPushes(texts.filter(([r]) => r === ex).map(([, t]) => ['x', t])).length > 0,
      `${ex} would be reported unexempted, so its exemption is load-bearing`)
  }
  const bentStamp = [['a.js', 'run tools/release/stamp.py --bump patch, then the same command with --push. Done']]
  ok(keylessStampPushes(bentStamp).length === 1, 'a keyless stamp --push is reported')
  ok(keylessStampPushes([['a.js', 'Run python3\ntools/release/stamp.py --bump x --dry-run, then the\nsame command with --push. It']]).length === 1,
    'so is one wrapped across lines, as the fragments wrap it')
  ok(keylessStampPushes([['a.js', bentStamp[0][1].replace('--push.', '--push --push-key k.')]]).length === 0,
    'the same text with --push-key is not')
  ok(keylessStampPushes([['a.js', 'git push --push-option=ci.skip; git push --push']]).length === 0,
    'a --push with no stamp.py before it is not')
  ok(keylessStampPushes([['a.js', 'Run stamp.py. The keyless --push sites']]).length === 0,
    'nor one a sentence end separates from stamp.py')
  ok(keylessStampPushes([[STAMP_EXEMPT.values().next().value, bentStamp[0][1]]]).length === 0,
    'an exempt path is skipped')

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

function grantSplit(decls) {
  const read = decls.get('GH_READ') || ''
  const write = decls.get('GH_WRITE') || ''
  const merge = decls.get('GH_MERGE') || ''
  const errs = []
  if (!read) errs.push('GH_READ is missing')
  if (!write) errs.push('GH_WRITE is missing')
  if (!merge) errs.push('GH_MERGE is missing')
  if (read && /merge_pull_request/.test(read)) errs.push('GH_READ holds merge_pull_request')
  if (write && /merge_pull_request/.test(write)) errs.push('GH_WRITE holds merge_pull_request')
  if (write && /issue_read/.test(write)) errs.push('GH_WRITE holds issue_read')
  if (merge && /issue_read/.test(merge)) errs.push('GH_MERGE holds issue_read')
  return errs
}

const hits = findings(decls, files)
for (const h of hits) console.log(`  DRIFT   ${h.file}: \`${h.name}\` ${h.detail}`)
if (hits.length) {
  console.log(`\nFRAGMENTS: ${hits.length} copy(ies) differ from ${CANON}. That file is the canonical text; change it there and copy it out, never the other way, or the next script to be edited reinstates the drift.`)
  process.exit(1)
}
const split = grantSplit(decls)
for (const e of split) console.log(`  GRANT   ${e}`)
if (split.length) {
  console.log(`\nFRAGMENTS: write-grant split failed. issue_read and merge_pull_request must not share a grant.`)
  process.exit(1)
}
const keyless = keylessStampPushes(trackedTexts())
for (const k of keyless) console.log(`  KEYLESS ${k}: stamp.py --push without --push-key`)
if (keyless.length) {
  console.log(`\nFRAGMENTS: ${keyless.length} stamp push(es) without the deploy key. After decision 0009 step 5 main refuses them; pass --push-key ~/.zcode/stamp-deploy.key --known-hosts ~/.zcode/github_known_hosts, or stop before pushing where no key exists.`)
  process.exit(1)
}
console.log(`FRAGMENTS ok: ${decls.size} canonical fragment(s) [${[...decls.keys()].join(', ')}] match every copy across ${files.length} script(s)`)
