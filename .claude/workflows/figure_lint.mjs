#!/usr/bin/env node
// Can the commands in `## Figures` be run at all?
//
// WHAT THIS IS FOR. Since #676 a body must carry `## Figures`, one line per
// figure with the command that printed it, and since #724 that command is
// MANDATORY where the corpus is out of the tree and its window still open --
// the literal belongs only there, beside the command. Nothing executed or
// examined the command. The section was a paste, and a paste is what the
// figure rules were written against.
//
// The defect that motivated this is on #715, round seven: an enumerator that
// passed `--arg n "$n"` to `gh api`, which has no `--arg` flag. It errored
// client-side before any request was made, printed `0` for every possible
// state of the world, and satisfied the rule in appearance exactly as well as
// a command that can run. A fix reviewer found it by running it. Nothing in
// the tree would have.
//
// WHAT THIS DELIBERATELY DOES NOT DO: it does not execute one character of the
// body. #679 proposed re-executing allowlisted commands and comparing the
// printed value to the stated one. That is refused, and the reasons are
// recorded here so the next seat has to answer them rather than rediscover
// them. TWO OF THEM ARE LOAD-BEARING, one is load-bearing for one arm, and the
// fourth is a COST rather than a reason: a first draft of this file argued the
// refusal on two quantities that do not measure out, and a refusal argued on a
// false quantity is one a later seat overturns for the wrong reason.
//
// The counting rule for 1 and 2, since the corpus is out of the tree and its
// window is open, so no literal is carried here. A RECOGNISED COMMAND is one
// simple-command segment inside an open pull request's `## Figures` section,
// extracted by this file's own `figuresSection`, `candidates` and `segments`,
// whose first word after `VAR=` assignments and shell keywords is one of
// PROGRAMS or a literal script path -- the checker's own recogniser, not a
// second one written for the count. TEMPLATED means the segment carries a
// `<placeholder>` or a `$NAME` the body binds elsewhere. The enumerator is
// `.claude/workflows/figure_census.mjs`, which imports that recogniser from
// here; the corpus it counts includes the body of the pull request that added
// this file, so the figure moves when that body is edited. Run the enumerator,
// do not carry its number.
//
//   1. NOT load-bearing, and it is recorded as a cost. Some figure commands are
//      templates (`<sha>`, `$D`), so a job could not spawn them as written --
//      but measured over the recognised commands they are a small minority, and
//      restricted to #679's actual target, the in-tree instruments, a smaller
//      one still: the large majority of instrument figures are literally
//      spawnable. Re-execution would have to skip the templated ones. That is a
//      design cost, not a veto, and this reason cannot carry the refusal.
//   2. Load-bearing, RESTATED. The claim that most figures are over the GitHub
//      API is false -- `gh` is about a fifth of recognised commands and in-tree
//      instruments are the largest class. What survives is the part that does
//      the work: the API arm is not empty, and every command in it reads a
//      value that is time-varying by construction -- an open-pull-request
//      count, a check-run listing at a live head. Comparing one of those to a
//      stated literal reddens an honest body, and one reddening is enough for
//      the check to be routed around. The share never was the argument.
//   3. Load-bearing for the `git` arm and every merge-base figure.
//      `pr-contract` runs `actions/checkout@v4` with no `fetch-depth`, so it
//      has depth 1 and no `origin/main` ref, and every
//      `git merge-base origin/main HEAD` figure would print a wrong value or
//      none.
//   4. Load-bearing, and decisive on its own. Even spawned as argv rather than
//      through a shell, an allowlist of the tree's own instruments still hands
//      the body `python3 tests/structure.py --record`, which rewrites the
//      ratchet's budget table. The allowlist bounds the program, not what the
//      program does.
//
// So the claim here is narrower and it is stated as such: a figure's command is
// checked for being WELL-FORMED AND RESOLVABLE, never for being right. That is
// what the #715 defect needed -- `gh api` has no `--arg` -- and nothing more.
//
// THE ONLY BODY-DERIVED DATA THAT REACHES A CHILD PROCESS is a subcommand word
// matching /^[a-z][a-z0-9-]*$/, passed as argv to `gh <word...> --help`, with
// no shell. `gh --help` reads no network and needs no authentication. The word
// is argv, but the word also SELECTS WHICH PROGRAM `gh` RUNS, which is a weaker
// boundary than "we only pass a subcommand" -- see the alias note at `ghEnv`
// below for the route that gave, its measurement, and why it is closed here
// rather than disclosed.
//
// PER-LINE, NOT PER-BODY. A command this cannot analyse is reported
// `unverified` with the reason, and is not an error: a seat can see which of
// its figures were examined and which were only stated. The three refusals are
//   - a `gh` long flag the installed `gh` does not accept for that subcommand;
//   - a `gh` subcommand that does not exist;
//   - a script path named as the argument of node/python3/bash that is not in
//     the tree at this head.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
const GH = process.env.FIGURE_LINT_GH || 'gh'

// THE INHERITED `gh` CONFIG IS NOT TRUSTED, and this is the one place the
// "argv, no shell" boundary was weaker than it read. `gh` expands its own
// SHELL aliases and `--help` does not short-circuit them: with
// `aliases: {w: '!<shell>'}` in the config it reads, `gh w --help` runs the
// shell. So a subcommand word taken from a body selected which PROGRAM `gh`
// ran, not merely which subcommand -- unreachable on `pr-contract`, whose
// runner config is fresh and which a pull-request author cannot write, and
// reachable through `tools/audit/prepr.sh` on a seat's own machine, where the
// seat's config applies. It is closed rather than disclosed, because closing it
// costs one empty directory: every spawn below runs under a config directory
// this file creates, so no alias exists for the child on any machine. A real
// subcommand cannot be shadowed by an alias in the first place, so nothing that
// resolved before stops resolving; what changes is that a word that is NOT a
// subcommand can no longer select anything. The same isolation makes the
// derived inventory independent of the seat's config in the other direction
// too: `co: pr checkout` in a local config would otherwise resolve here and not
// on the runner.
let ghHome = null
function ghEnv() {
  if (!ghHome) {
    ghHome = fs.mkdtempSync(path.join(os.tmpdir(), 'figure-lint-gh-'))
    process.on('exit', () => { try { fs.rmSync(ghHome, { recursive: true, force: true }) } catch {} })
  }
  return { ...process.env, GH_CONFIG_DIR: ghHome }
}

// `gh <sub> --help` is a process each. A body naming many distinct subcommands
// would otherwise spawn one per subcommand with no ceiling, on a check that
// runs on every pull-request event. Past the budget the gh arm reports
// unverified rather than refusing: a command this check ran out of budget to
// examine is one it did not examine, which is what `unverified` means.
const ghBudget = () => Number(process.env.FIGURE_LINT_GH_BUDGET || 40)
let ghSpawns = 0

// --- reading the section -----------------------------------------------------

// `## Figures` runs to the next `## ` that is not inside a fence. The fence
// state matters: a body quoting a heading inside a ``` block would otherwise
// end the section early and this would silently examine nothing.
export function figuresSection(body) {
  const lines = body.split('\n')
  let inFence = false
  let start = -1
  const out = []
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    if (!inFence && /^##\s+/.test(line)) {
      if (start >= 0) break
      if (/^##\s+Figures\s*$/.test(line)) start = i
      continue
    }
    if (start >= 0) out.push(line)
  }
  return start < 0 ? null : out.join('\n')
}

// --- finding the candidate commands -----------------------------------------

// Two passes, both conservative, and the conservatism is the whole
// false-positive control: only a segment whose program is one of these is
// analysed at all, and a backticked span that yields no such segment is dropped
// rather than reported. Prose in backticks -- `--budgets`, `MODE: SCOPED`,
// `coordinator_loc`, `success` -- is what this corpus is made of, and a check
// that reads any of it as a command starts refusing bodies that are correct.
const PROGRAMS = new Set(['gh', 'git', 'node', 'python3', 'python', 'bash', 'sh'])
const SCRIPTISH = /^\.{0,2}\/?[\w.@-]+(\/[\w.@-]+)+\.(sh|py|mjs|js)$/

// A backtick span may WRAP: this corpus wraps prose at eighty columns and a
// command inside single backticks spans two lines as often as not. Collapsing
// the newline is what stops the second half being read as a separate command.
function backtickSpans(text) {
  const out = []
  const re = /(`{1,3})([^`][\s\S]*?)\1/g
  let m
  while ((m = re.exec(text))) out.push(m[2].replace(/\s*\n\s*/g, ' ').trim())
  return out
}

// Fenced blocks and four-space indented blocks. A trailing `\` continues onto
// the next line, which is how every multi-line pipeline in this corpus is
// written.
function blockLines(text) {
  const out = []
  let inFence = false
  let buf = []
  const flush = () => { if (buf.length) { out.push(buf.join(' ')); buf = [] } }
  for (const raw of text.split('\n')) {
    if (/^\s*(```|~~~)/.test(raw)) { flush(); inFence = !inFence; continue }
    const indented = /^ {4,}\S/.test(raw)
    if (!inFence && !indented) { flush(); continue }
    const line = raw.trim()
    if (!line) { flush(); continue }
    if (line.endsWith('\\')) { buf.push(line.slice(0, -1).trim()); continue }
    buf.push(line)
    flush()
  }
  flush()
  return out
}

// A candidate carries WHERE it came from. A fenced or indented block inside
// `## Figures` is a command by construction, so it is reported even when this
// cannot analyse it. A backticked span is usually prose -- `--budgets`,
// `MODE: SCOPED`, `success` -- so it is reported only when some segment of it
// names a program this knows. Without that split the report is either blind to
// an unanalysable block or full of metric names.
export function candidates(section) {
  const seen = new Set()
  const out = []
  for (const [src, list] of [['block', blockLines(section)], ['span', backtickSpans(section)]]) {
    for (const c of list) {
      if (!c || seen.has(c)) continue
      seen.add(c)
      out.push({ cmd: c, src })
    }
  }
  return out
}

// --- lexing ------------------------------------------------------------------

// A shell-shaped lexer that EXPANDS NOTHING. Quotes and backslashes group; `$(`
// and a backtick group opaquely so a substitution never splits a token. The
// output is words plus, per word, whether it was quoted -- a quoted `--x` is
// data, not a flag.
export function lex(cmd) {
  const words = []
  let cur = ''
  let quoted = false
  let started = false
  const push = () => { if (started) words.push({ text: cur, quoted }); cur = ''; quoted = false; started = false }
  for (let i = 0; i < cmd.length; i++) {
    const ch = cmd[i]
    if (ch === '\\' && i + 1 < cmd.length) { started = true; cur += cmd[++i]; continue }
    if (ch === "'" || ch === '"') {
      const end = cmd.indexOf(ch, i + 1)
      started = true; quoted = true
      if (end < 0) { cur += cmd.slice(i + 1); break }
      cur += cmd.slice(i + 1, end); i = end; continue
    }
    if (ch === '$' && cmd[i + 1] === '(') {
      let depth = 1; let j = i + 2
      while (j < cmd.length && depth) { if (cmd[j] === '(') depth++; else if (cmd[j] === ')') depth--; j++ }
      started = true; cur += cmd.slice(i, j); i = j - 1; continue
    }
    if (/\s/.test(ch)) { push(); continue }
    started = true
    cur += ch
  }
  push()
  return words
}

// Split a pipeline into simple commands on unquoted `|`, `&&`, `||`, `;`.
export function segments(cmd) {
  const words = lex(cmd)
  const out = []
  let cur = []
  for (const w of words) {
    if (!w.quoted && (w.text === '|' || w.text === '&&' || w.text === '||' || w.text === ';')) { out.push(cur); cur = []; continue }
    // `a;b` and `a|b` written without spaces still separate.
    if (!w.quoted && /^[^|;&]+[|;]$/.test(w.text)) { cur.push({ ...w, text: w.text.slice(0, -1) }); out.push(cur); cur = []; continue }
    cur.push(w)
  }
  out.push(cur)
  return out.filter((s) => s.length)
}

// `VAR=value cmd ...` -- the assignments are not the program.
// `VAR=value cmd ...` -- the assignments are not the program. Nor are the shell
// keywords that open a loop or a conditional: the #715 defect was written as
// `for n in ...; do gh api ...; done`, and a check that only ever reads the
// first word of a segment does not see the `gh` inside it.
const KEYWORDS = new Set(['do', 'then', 'else', 'elif', 'done', 'fi', 'esac', '{', '(', '!', 'time'])
const stripAssignments = (words) => {
  let i = 0
  for (;;) {
    if (i < words.length && !words[i].quoted && /^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i].text)) { i++; continue }
    if (i < words.length && !words[i].quoted && KEYWORDS.has(words[i].text)) { i++; continue }
    break
  }
  return words.slice(i)
}

// --- gh flag inventory, DERIVED not carried ----------------------------------

const helpCache = new Map()
let ghState = null

function ghAvailable() {
  if (ghState !== null) return ghState
  try {
    const v = execFileSync(GH, ['--version'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 20000, env: ghEnv() })
    ghState = { ok: true, version: v.split('\n')[0].trim() }
  } catch (e) {
    ghState = { ok: false, why: String(e && e.message || e).split('\n')[0] }
  }
  return ghState
}

// `gh <sub...> --help` prints `FLAGS` and `INHERITED FLAGS` blocks; every long
// flag is `--name`. Parsing the help text is what makes this inventory the
// installed gh's own answer rather than a list in this file that would rot.
function ghFlags(sub) {
  const key = sub.join(' ')
  if (helpCache.has(key)) return helpCache.get(key)
  if (ghSpawns >= ghBudget()) return 'budget'
  let res = null
  try {
    ghSpawns++
    const txt = execFileSync(GH, [...sub, '--help'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 20000, env: ghEnv() })
    const flags = new Set(['--help'])
    let inFlags = false
    for (const line of txt.split('\n')) {
      if (/^[A-Z][A-Z ]*$/.test(line.trim())) { inFlags = /FLAGS$/.test(line.trim()); continue }
      if (!inFlags) continue
      const m = /^\s+(?:-\w,\s+)?(--[a-z][a-z0-9-]*)/.exec(line)
      if (m) flags.add(m[1])
    }
    res = flags.size > 1 ? flags : null
  } catch { res = null }
  helpCache.set(key, res)
  return res
}

// --- git command inventory, DERIVED not carried -------------------------------

// `git --list-cmds` is git's own answer to "what commands do you have". Flags
// are NOT checked for git: `git log --help` opens a man page rather than
// printing a parseable FLAGS block, and a hand-written flag list here would rot
// into the false refusals this whole check exists not to produce. So a git
// figure is checked for its SUBCOMMAND resolving and reported unverified for
// everything else, which is what the per-line report is for.
let gitCmds = null
function gitCommands() {
  if (gitCmds !== null) return gitCmds
  try {
    const txt = execFileSync('git', ['--list-cmds=main,others,alias,nohelpers'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 20000 })
    const set = new Set(txt.split('\n').map((x) => x.trim()).filter(Boolean))
    gitCmds = set.size ? set : false
  } catch { gitCmds = false }
  return gitCmds
}

function analyseGit(words, cmd, out) {
  const sub = words.slice(1).find((w) => !w.quoted && /^[a-z][a-z0-9-]*$/.test(w.text))
  if (!sub) { out.push({ kind: 'unverified', cmd, why: '`git` with no subcommand word to resolve' }); return }
  const cmds = gitCommands()
  if (!cmds) {
    out.push({ kind: 'error', cmd, why: '`git --list-cmds` did not answer, so this command was checked against nothing. A check that cannot reach its inventory must say so rather than pass.' })
    return
  }
  if (!cmds.has(sub.text)) {
    out.push({ kind: 'error', cmd, why: `\`git ${sub.text}\` is not a git command here. A figure whose command does not resolve prints nothing, for every state of the world.` })
    return
  }
  out.push({ kind: 'unverified', cmd, why: `\`git ${sub.text}\` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals` })
}

// --- resolving a path at this head -------------------------------------------

let atRev = null
export const setRev = (rev) => { atRev = rev }

function inTree(rel) {
  if (atRev) {
    try {
      execFileSync('git', ['cat-file', '-e', `${atRev}:${rel}`], { cwd: ROOT, stdio: 'ignore', timeout: 20000 })
      return true
    } catch { return false }
  }
  return fs.existsSync(path.join(ROOT, rel))
}

// --- the analysis ------------------------------------------------------------

const INLINE_CODE_FLAGS = new Set(['-c', '-e', '-m', '--eval', '--command'])

function analyseGh(words, cmd, out) {
  const sub = []
  for (let i = 1; i < words.length && sub.length < 3; i++) {
    const w = words[i]
    if (w.quoted || !/^[a-z][a-z0-9-]*$/.test(w.text)) break
    sub.push(w.text)
  }
  if (!sub.length) { out.push({ kind: 'unverified', cmd, why: '`gh` with no subcommand word to resolve' }); return }
  const gh = ghAvailable()
  if (!gh.ok) {
    out.push({ kind: 'error', cmd,
      why: `\`gh\` is not runnable here (${gh.why}), so this command's flags were not checked against anything. A check that cannot reach its inventory must say so rather than pass.` })
    return
  }
  let flags = null
  let used = null
  for (let n = sub.length; n >= 1 && !flags; n--) {
    const got = ghFlags(sub.slice(0, n))
    if (got === 'budget') {
      out.push({ kind: 'unverified', cmd,
        why: `the \`gh --help\` spawn budget of ${ghBudget()} was reached, so this command's flags were not checked. Raise \`FIGURE_LINT_GH_BUDGET\` to examine it.` })
      return
    }
    flags = got
    if (flags) used = sub.slice(0, n)
  }
  if (!flags) {
    out.push({ kind: 'error', cmd,
      why: `\`gh ${sub.join(' ')}\` is not a subcommand the installed gh knows (${gh.version} here). A figure whose command does not resolve prints nothing, for every state of the world. If this is a program's OUTPUT rather than a command -- \`gh version 2.98.0\` is what \`gh --version\` prints -- state the command instead: \`## Figures\` asks for what produced the figure, not what it printed.` })
    return
  }
  let afterDashDash = false
  const bad = []
  for (const w of words.slice(1 + used.length)) {
    if (w.quoted) continue
    if (w.text === '--') { afterDashDash = true; continue }
    if (afterDashDash) continue
    const m = /^(--[a-z][a-z0-9-]*)(=.*)?$/.exec(w.text)
    if (m && !flags.has(m[1])) bad.push(m[1])
  }
  if (bad.length) {
    out.push({ kind: 'error', cmd,
      why: `\`gh ${used.join(' ')}\` has no ${bad.map((b) => `\`${b}\``).join(', ')} flag (${gh.version} accepts ${[...flags].sort().join(' ')}). It is refused client-side, prints nothing, and states the same figure whatever the world holds.` })
    return
  }
  out.push({ kind: 'ok', cmd, what: `gh ${used.join(' ')}: every long flag accepted` })
}

function analyseScript(words, cmd, out, program, argIndex) {
  if (words.slice(1).some((w) => !w.quoted && INLINE_CODE_FLAGS.has(w.text))) {
    out.push({ kind: 'unverified', cmd, why: `${program} runs an inline script rather than a file` })
    return
  }
  const arg = words[argIndex]
  if (!arg) { out.push({ kind: 'unverified', cmd, why: `${program} with no script argument` }); return }
  const raw = arg.text.replace(/^\.\//, '')
  if (/[$*?<>{}]/.test(raw)) { out.push({ kind: 'unverified', cmd, why: `the path \`${arg.text}\` is a template or an expansion, not a literal` }); return }
  if (!SCRIPTISH.test(arg.text)) { out.push({ kind: 'unverified', cmd, why: `\`${arg.text}\` does not look like a path in this tree` }); return }
  // A path is resolved against the repository root and must stay inside it.
  // Without this the two modes disagree and the WORKTREE mode -- the one
  // `pr-contract` runs, since it passes no `--at` -- is the one that is wrong:
  // `path.join(ROOT, '../../x/y.sh')` escapes the repository, and a file that
  // exists out there was reported `is in the tree at this head`. That is a
  // false ACCEPT, so it is the direction that costs the check its meaning. It
  // is reported unverified rather than refused because an absolute path outside
  // the repository is a figure this check cannot resolve, not one it has shown
  // to be wrong.
  const abs = path.resolve(ROOT, raw)
  if (abs !== ROOT && !abs.startsWith(ROOT + path.sep)) {
    out.push({ kind: 'unverified', cmd,
      why: `\`${arg.text}\` resolves outside this repository, so whether it is in the tree at this head is not a question this check can answer` })
    return
  }
  const rel = path.relative(ROOT, abs)
  if (inTree(rel)) { out.push({ kind: 'ok', cmd, what: `\`${rel}\` is in the tree at this head` }); return }
  out.push({ kind: 'error', cmd,
    why: `\`${rel}\` is not in the tree at this head. A figure whose instrument is not there cannot be re-run by whoever reads this body next.` })
}

export function analyse(cmd) {
  const out = []
  for (const seg of segments(cmd)) {
    const words = stripAssignments(seg)
    if (!words.length) continue
    const p = words[0]
    if (p.quoted) continue
    if (p.text === 'gh') { analyseGh(words, cmd, out); continue }
    if (p.text === 'git') { analyseGit(words, cmd, out); continue }
    if (PROGRAMS.has(p.text)) {
      let i = 1
      while (i < words.length && /^-/.test(words[i].text) && !words[i].quoted) i++
      analyseScript(words, cmd, out, p.text, i)
      continue
    }
    if (SCRIPTISH.test(p.text)) { analyseScript([{ text: 'run', quoted: false }, p], cmd, out, p.text, 1); continue }
  }
  return out
}

export function lint(body) {
  const section = figuresSection(body)
  if (section === null) return { section: false, results: [], examined: 0 }
  const results = []
  for (const { cmd, src } of candidates(section)) {
    const hits = analyse(cmd)
    if (hits.length) { results.push(...hits); continue }
    if (src === 'block') results.push({ kind: 'unverified', cmd, why: 'no segment of this names a program this check knows' })
  }
  return { section: true, results, examined: results.length }
}

// --- self-test ---------------------------------------------------------------
// A check that cannot be shown failing does not merge, and one that cannot be
// shown STAYING SILENT on a healthy input pins nothing either: a check that
// refused every command would satisfy the rot fixtures exactly as well.
function selfTest() {
  let pass = 0
  let fail = 0
  const ok = (cond, what) => { if (cond) { pass++; console.log(`  ok   ${what}`) } else { fail++; console.log(`  FAIL ${what}`) } }
  const dir = path.join(HERE, 'fixtures', 'figures')
  if (!fs.existsSync(dir)) {
    console.log(`\nFIXTURE VACUOUS: ${path.relative(ROOT, dir)}/ is missing; every assertion below runs over nothing`)
    return 2
  }
  const fx = (n) => fs.readFileSync(path.join(dir, n), 'utf8')
  const errs = (n) => lint(fx(n)).results.filter((r) => r.kind === 'error')

  // THE POSITIVE ARM: the #715 defect, the command as the review quoted it.
  const arg = errs('gh-arg.md')
  ok(arg.length === 1, `the #715 enumerator's \`--arg\` is refused (got ${arg.length} error(s))`)
  ok(arg.length === 1 && /--arg/.test(arg[0].why), 'and the refusal names the flag, not merely the line')

  const sub = errs('gh-subcommand.md')
  ok(sub.length === 1, `a \`gh\` subcommand that does not exist is refused (got ${sub.length})`)
  // Pinned on the MESSAGE, because the fixture's flags would be refused by the
  // flag arm too: a count alone passes while the subcommand arm is dead.
  ok(sub.length === 1 && /is not a subcommand/.test(sub[0].why), 'and by the subcommand arm, not the flag arm')
  ok(errs('missing-script.md').length === 1, 'a script path that is not in the tree is refused')

  // THE NULL CONTROL. Every command here is one this repository's own bodies
  // wrote and a seat really ran.
  const good = errs('good.md')
  ok(good.length === 0, `a body whose figure commands all resolve is silent (null control; got ${good.length})`)
  const g = lint(fx('good.md'))
  ok(g.results.some((r) => r.kind === 'ok'), 'and it did not go silent by examining nothing')

  // Prose in backticks is the false-positive surface. `--budgets` and
  // `MODE: SCOPED` are figures this corpus writes constantly.
  const prose = lint(fx('prose-only.md'))
  ok(prose.results.length === 0, `backticked prose is not read as a command (got ${prose.results.length})`)

  // A command it cannot analyse is a REPORT, never a refusal -- the half that
  // decides whether seats route around this.
  const unk = lint(fx('unverifiable.md'))
  ok(unk.results.length > 0 && unk.results.every((r) => r.kind === 'unverified'),
    'a placeholder or an unknown program is reported unverified, not refused')

  ok(lint('## Head\n\nabc\n').section === false, 'a body with no `## Figures` section is not this check\'s refusal')

  // The parser is the half that can silently measure nothing.
  ok(segments('a | b && c ; d').length === 4, 'a pipeline splits into its simple commands')
  ok(segments("gh api --jq '.[] | .id'").length === 1, 'a pipe inside quotes does not split')
  ok(lex('gh api "/x/y" --jq \'.a\'')[2].quoted === true, 'a quoted word is marked quoted')
  ok(lex('a $(b | c) d').length === 3, 'a command substitution stays one word')
  ok(figuresSection('## Figures\n\n```\n## Head\n```\nx\n\n## Red checks\ny') !== null &&
     /x/.test(figuresSection('## Figures\n\n```\n## Head\n```\nx\n\n## Red checks\ny')) &&
     !/y/.test(figuresSection('## Figures\n\n```\n## Head\n```\nx\n\n## Red checks\ny')),
     'a heading inside a fence does not end the section early')

  // The inventory itself. If `gh` is not runnable the gh arm is dead code, and
  // a dead arm is the shape that makes a green run mean nothing here.
  const gh = ghAvailable()
  ok(gh.ok, `\`gh\` is runnable, so the flag inventory is real${gh.ok ? ` (${gh.version})` : ` -- ${gh.why}`}`)
  if (gh.ok) {
    const f = ghFlags(['api'])
    ok(!!f && f.has('--jq') && f.has('--paginate') && !f.has('--arg'),
      'the derived `gh api` inventory has --jq and --paginate and no --arg')
  }

  // THE CONFUSED-DEPUTY ARM, both ways round. A shell alias in the config `gh`
  // reads turns `gh <word> --help` into a shell command, so the word chose the
  // PROGRAM. The first assertion is the null control and it must FIRE: it
  // spawns the same word with the malicious config visible, and if the sentinel
  // does not appear the alias was never armed and the second assertion below
  // proves nothing. The second is the containment: the same word through this
  // file, which supplies its own config directory.
  if (gh.ok) {
    const cfg = fs.mkdtempSync(path.join(os.tmpdir(), 'figure-lint-alias-'))
    const sentinel = path.join(cfg, 'ran')
    fs.writeFileSync(path.join(cfg, 'config.yml'),
      `version: 1\naliases:\n    figlintprobe: '!touch ${sentinel}; echo ran'\n`)
    const saved = process.env.GH_CONFIG_DIR
    try {
      execFileSync(GH, ['figlintprobe', '--help'],
        { stdio: 'ignore', timeout: 20000, env: { ...process.env, GH_CONFIG_DIR: cfg } })
    } catch { /* the alias's own exit status is not what is measured */ }
    ok(fs.existsSync(sentinel), 'a `gh` shell alias really does run under `--help` (null control; without this the containment assertion is vacuous)')
    fs.rmSync(sentinel, { force: true })
    process.env.GH_CONFIG_DIR = cfg
    const deputy = analyse('gh figlintprobe --help')
    if (saved === undefined) delete process.env.GH_CONFIG_DIR; else process.env.GH_CONFIG_DIR = saved
    ok(!fs.existsSync(sentinel) && deputy.length === 1 && deputy[0].kind === 'error',
      'and this check does not expand it: the word resolves to nothing and the alias does not run')
    fs.rmSync(cfg, { recursive: true, force: true })
  }

  // A path that leaves the repository. `pr-contract` passes no `--at`, so the
  // worktree arm is the one it runs, and `path.join(ROOT, '../x/y.sh')` used to
  // find a real file out there and report it in the tree -- a false ACCEPT.
  const out = fs.mkdtempSync(path.join(path.dirname(ROOT), 'figure-lint-outside-'))
  try {
    fs.writeFileSync(path.join(out, 'probe.sh'), '#!/bin/sh\n')
    const esc = path.relative(ROOT, path.join(out, 'probe.sh'))
    const r = analyse(`bash ${esc}`)
    ok(r.length === 1 && r[0].kind === 'unverified' && /outside this repository/.test(r[0].why),
      'an existing file reached by `..` from outside the repository is not reported in the tree')
  } finally { fs.rmSync(out, { recursive: true, force: true }) }
  const inside = analyse('bash tools/audit/prepr.sh')
  ok(inside.length === 1 && inside[0].kind === 'ok',
    'and a path that stays inside it still resolves (null control; the verdict above is the containment arm, not the path shape)')

  // The spawn ceiling. Without it a body naming many subcommands spawns one
  // `gh --help` per subcommand with no bound, on a per-event check.
  if (gh.ok) {
    const savedBudget = process.env.FIGURE_LINT_GH_BUDGET
    process.env.FIGURE_LINT_GH_BUDGET = '0'
    const capped = analyse('gh label list --limit 5')
    if (savedBudget === undefined) delete process.env.FIGURE_LINT_GH_BUDGET; else process.env.FIGURE_LINT_GH_BUDGET = savedBudget
    ok(capped.length === 1 && capped[0].kind === 'unverified' && /spawn budget/.test(capped[0].why),
      'past the `gh --help` spawn budget a command is unverified, not refused and not silently accepted')
  }

  console.log(`\n${pass} passed, ${fail} failed`)
  return fail ? 2 : 0
}

// --- entry point -------------------------------------------------------------

// GUARDED, so `import`ing this file runs nothing. Without the guard the module
// body reached the usage line and called `process.exit(2)` on any importer, so
// every export above was unreachable to anything but this file -- including the
// enumerator that measures the corpus these refusals are argued from, which is
// how it was found.
function main(argv) {
  if (argv.includes('--self-test')) return selfTest()

  const val = (f) => { const i = argv.indexOf(f); return i >= 0 ? argv[i + 1] : null }
  const bodyPath = val('--pr-body')
  if (!bodyPath) {
    console.log('usage: figure_lint.mjs --pr-body <file> [--at <rev>] | --self-test')
    return 2
  }
  if (val('--at')) setRev(val('--at'))
  let body
  try { body = fs.readFileSync(bodyPath, 'utf8') } catch { console.log(`FIGURES: ${bodyPath} is unreadable`); return 1 }

  const { section, results } = lint(body)
  if (!section) {
    // `## Figures` being present at all is checkPrBody's refusal, pinned by its
    // own fixture. Refusing it here too would give one defect two red lines and
    // teach a seat that this check is about the heading.
    console.log('FIGURES: no `## Figures` section -- `policy_lint.mjs --pr-body` is the check that refuses that')
    return 0
  }
  const errors = results.filter((r) => r.kind === 'error')
  for (const r of results) {
    if (r.kind === 'ok') console.log(`  ok         ${r.cmd}\n             ${r.what}`)
    else if (r.kind === 'unverified') console.log(`  unverified ${r.cmd}\n             ${r.why}`)
    else console.log(`  REFUSED    ${r.cmd}\n             ${r.why}`)
  }
  const n = (k) => results.filter((r) => r.kind === k).length
  console.log(`\nFIGURES: ${n('ok')} resolved, ${n('unverified')} not verified, ${errors.length} refused`)
  if (!errors.length) return 0
  console.log('A figure whose command cannot run states the same number whatever the world holds. Repair the command, or state the figure without one and say what it rests on.')
  return 1
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exit(main(process.argv.slice(2)))
}
