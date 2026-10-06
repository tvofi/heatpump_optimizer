#!/usr/bin/env node
// What is the `## Figures` corpus actually made of?
//
// WHY THIS EXISTS. `figure_lint.mjs`'s header refuses #679's re-execution and
// two of its four reasons are quantities over the open pull requests -- a
// corpus that is OUT OF THE TREE with an OPEN WINDOW, which #724 says may not
// be quoted as a literal in the tree at all. The instrument is then the
// ENUMERATOR: the command that, run alone, prints the number. This is it. A
// first draft of that header carried two quantities instead, and a fix review
// measured both out: `most figures are over the GitHub API` was false, and
// `the corpus is not executable as written` described a small minority.
//
// THE COUNTING RULE, which is the whole point of the file. A RECOGNISED COMMAND
// is one simple-command segment inside an open pull request's `## Figures`
// section, extracted by `figure_lint.mjs`'s own `figuresSection`, `candidates`
// and `segments`, whose first word after `VAR=` assignments and shell keywords
// names a program that checker knows or is a literal script path. The recogniser
// is imported rather than reimplemented: a census counted by a second reader of
// the same text measures the difference between the two readers as well as the
// corpus, and #373 is where three agents counting "the same" census got 59, 50
// and 124/147/50.
//
// A command is TEMPLATED when it carries a `<placeholder>` or a `$NAME` the body
// binds somewhere else, which is the class a job could not spawn as written. A
// `$(...)` substitution is reported separately: a shell runs it as written, so
// it is not templated, but an ALLOWLIST SPAWNING ARGV expands none of it, so
// under #679's own execution model it is as unspawnable as a placeholder. Both
// counts are printed rather than one, because which is right depends on the
// execution model being argued about.
//
// THE POPULATION MOVES WHILE YOU READ IT. Pull requests open and merge; this
// pull request's own body is in the corpus, so editing it moves the count. Run
// this, do not carry what it printed.
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { figuresSection, candidates, segments } from './figure_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const GH = process.env.FIGURE_LINT_GH || 'gh'
const PROGRAMS = new Set(['gh', 'git', 'node', 'python3', 'python', 'bash', 'sh'])
const SCRIPTISH = /^\.{0,2}\/?[\w.@-]+(\/[\w.@-]+)+\.(sh|py|mjs|js)$/
const KEYWORDS = new Set(['do', 'then', 'else', 'elif', 'done', 'fi', 'esac', '{', '(', '!', 'time'])
const INLINE = new Set(['-c', '-e', '-m', '--eval', '--command'])

const stripAssignments = (words) => {
  let i = 0
  for (;;) {
    if (i < words.length && !words[i].quoted && /^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i].text)) { i++; continue }
    if (i < words.length && !words[i].quoted && KEYWORDS.has(words[i].text)) { i++; continue }
    break
  }
  return words.slice(i)
}

export function templated(text) {
  const noSubst = text.replace(/\$\([\s\S]*?\)/g, ' ')
  if (/\$\{?[A-Za-z_][A-Za-z0-9_]*\}?/.test(noSubst)) return 'bound-elsewhere'
  if (/<[A-Za-z_][\w .-]*>/.test(text)) return 'bound-elsewhere'
  if (/\$\(/.test(text)) return 'substitution'
  return null
}

// The class is the PROGRAM, because that is what #679's allowlist would bound.
// `instrument` is the class #679 actually targets: the tree's own scripts.
export function classify(words) {
  const p = words[0]
  if (p.quoted) return null
  if (p.text === 'gh' || p.text === 'git') return p.text
  if (PROGRAMS.has(p.text)) {
    if (words.slice(1).some((x) => !x.quoted && INLINE.has(x.text))) return 'inline-code'
    let i = 1
    while (i < words.length && /^-/.test(words[i].text) && !words[i].quoted) i++
    return words[i] && SCRIPTISH.test(words[i].text) ? 'instrument' : 'other-interpreter'
  }
  return SCRIPTISH.test(p.text) ? 'instrument' : null
}

export function census(bodies) {
  const rows = []
  const noSection = []
  for (const { name, body } of bodies) {
    const sec = figuresSection(body)
    if (sec === null) { noSection.push(name); continue }
    for (const { cmd } of candidates(sec)) {
      for (const seg of segments(cmd)) {
        const words = stripAssignments(seg)
        if (!words.length) continue
        const cls = classify(words)
        if (!cls) continue
        const text = words.map((w) => w.text).join(' ')
        rows.push({ name, cls, tmpl: templated(text), text })
      }
    }
  }
  return { rows, noSection }
}

const CLASSES = ['gh', 'git', 'instrument', 'inline-code', 'other-interpreter']

function report(bodies, refusals) {
  const { rows, noSection } = census(bodies)
  const n = (f) => rows.filter(f).length
  const bound = (r) => r.tmpl === 'bound-elsewhere'
  console.log(`bodies: ${bodies.length}, of which carrying no \`## Figures\`: ${noSection.length}${noSection.length ? ` (${noSection.join(', ')})` : ''}`)
  console.log(`recognised commands: ${rows.length}`)
  for (const c of CLASSES) {
    console.log(`  ${c.padEnd(17)} ${String(n((r) => r.cls === c)).padStart(4)}   templated ${n((r) => r.cls === c && bound(r))}   + substitution ${n((r) => r.cls === c && r.tmpl)}`)
  }
  console.log(`templated (a <placeholder> or a $NAME the body binds elsewhere): ${n(bound)}`)
  console.log(`the same, plus a $(...) an argv spawn would not expand:          ${n((r) => !!r.tmpl)}`)
  console.log(`API refusals during this run: ${refusals}`)
  return rows
}

// --- self-test ---------------------------------------------------------------
// The counting rule is what this file is FOR, so the rule is what is pinned:
// one fixture per class boundary, and the classification asserted rather than
// the total. A census whose only assertion is its own sum passes while every
// command lands in the wrong class.
function selfTest() {
  let pass = 0
  let fail = 0
  const ok = (cond, what) => { if (cond) { pass++; console.log(`  ok   ${what}`) } else { fail++; console.log(`  FAIL ${what}`) } }
  const dir = path.join(HERE, 'fixtures', 'figures')
  if (!fs.existsSync(dir)) {
    console.log(`\nFIXTURE VACUOUS: ${dir}/ is missing; every assertion below runs over nothing`)
    return 2
  }
  const of = (n) => census([{ name: n, body: fs.readFileSync(path.join(dir, n), 'utf8') }]).rows

  const arg = of('gh-arg.md')
  ok(arg.length === 1 && arg[0].cls === 'gh', `the #715 enumerator counts as one \`gh\` command (got ${arg.length})`)
  ok(arg.length === 1 && arg[0].tmpl === 'bound-elsewhere', 'and as templated, since `$n` is bound by the loop around it')

  // `good.md` is the mixed body, and it is asserted COMMAND BY COMMAND rather
  // than by a total: it holds instrument and `gh` commands, one of each
  // templated, and a total alone is satisfied by every one of them landing in
  // the wrong class.
  const good = of('good.md')
  const insts = good.filter((r) => r.cls === 'instrument')
  const ghs = good.filter((r) => r.cls === 'gh')
  ok(insts.length === 5 && ghs.length === 3, `a mixed body splits into its classes (got ${insts.length} instrument, ${ghs.length} gh)`)
  ok(insts.filter((r) => r.tmpl).length === 1 && ghs.filter((r) => r.tmpl).length === 1,
    'and one command in each class is templated -- `$D` in the scope selection, `<sha>` in the check-run listing')
  ok(insts.some((r) => r.tmpl === null) && ghs.some((r) => r.tmpl === null),
    'and the rest are not (null control: a rule that called everything templated would satisfy the assertion above)')
  ok(good.length > 0 && good.every((r) => CLASSES.includes(r.cls)), 'and every recognised command landed in a named class')

  // The false-positive surface, and the reason the recogniser is imported: a
  // census that reads `--budgets` or `MODE: SCOPED` as a command inflates every
  // share it prints.
  ok(of('prose-only.md').length === 0, `backticked prose is not counted as a command (got ${of('prose-only.md').length})`)

  ok(census([{ name: 'x', body: '## Head\n\nabc\n' }]).noSection.length === 1,
    'a body with no `## Figures` section is reported, not silently counted as empty')

  // `gh` against `git` is the boundary reason 2's share is measured across, and
  // no fixture holds a `git` figure -- collapsing the two classes passed every
  // assertion above. Pinned here on a body written for it.
  const two = census([{ name: 'x', body: '## Figures\n\n- `gh pr list --state open`\n- `git log --oneline -1`\n' }]).rows
  ok(two.length === 2 && two[0].cls === 'gh' && two[1].cls === 'git',
    `\`gh\` and \`git\` are counted apart (got ${two.map((r) => r.cls).join(', ') || 'nothing'})`)

  ok(templated('python3 tests/x.py --at <sha>') === 'bound-elsewhere', 'a `<placeholder>` is templated')
  ok(templated('python3 tests/x.py --workdir "$D"') === 'bound-elsewhere', 'a `$NAME` bound elsewhere is templated')
  ok(templated('git diff $(git merge-base origin/main HEAD)') === 'substitution',
    'a `$(...)` alone is counted separately: a shell runs it as written, an argv spawn does not')
  ok(templated('node .claude/workflows/policy_lint.mjs --budgets') === null,
    'and a command with neither is not templated (null control)')

  console.log(`\n${pass} passed, ${fail} failed`)
  return fail ? 2 : 0
}

// --- entry point -------------------------------------------------------------

function fromGitHub() {
  let refusals = 0
  const gh = (args) => {
    try { return execFileSync(GH, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 60000 }) } catch { refusals++; return null }
  }
  const list = gh(['pr', 'list', '--state', 'open', '--limit', '100', '--json', 'number', '-q', '.[].number'])
  if (list === null) { console.log('the open-pull-request listing was refused; no figure below would be over the population it names'); return { bodies: null, refusals } }
  const bodies = []
  for (const num of list.split('\n').map((x) => x.trim()).filter(Boolean)) {
    const body = gh(['pr', 'view', num, '--json', 'body', '-q', '.body'])
    if (body !== null) bodies.push({ name: `#${num}`, body })
  }
  return { bodies, refusals }
}

function main(argv) {
  if (argv.includes('--self-test')) return selfTest()
  const i = argv.indexOf('--bodies')
  if (i >= 0) {
    const dir = argv[i + 1]
    const files = fs.readdirSync(dir).filter((f) => f.endsWith('.md')).sort()
    report(files.map((f) => ({ name: f, body: fs.readFileSync(path.join(dir, f), 'utf8') })), 0)
    return 0
  }
  const { bodies, refusals } = fromGitHub()
  if (!bodies) return 1
  report(bodies, refusals)
  // A refusal count printed beside the figure, never a figure alone: a loop that
  // swallows API errors prints a smaller number and looks exactly like a smaller
  // corpus.
  return refusals ? 1 : 0
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exit(main(process.argv.slice(2)))
}
