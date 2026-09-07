// Policy-document linter: the refusal for the governance corpus.
//
// WHY THIS EXISTS. `brief_lint.mjs` checks citations in wave rosters and
// deliberately does not read `docs/plan-*.md`, `docs/HANDOVER.md` or
// `tools/audit/briefs/` (.cursor/rules/brief-citations.mdc). So the four
// citation classes are enforced downward onto rosters and practised by
// nothing that governs a seat. The 2026-09 governance audit measured the
// consequence: dead symbols inside dispatch instructions, counts that drifted
// only ever upward, one `gh` invocation per contract in an environment with
// no `gh`, and an always-loaded file that grew from 134 to 464 lines with no
// commit ever making it shorter.
//
// This script is that refusal. It reuses brief_lint's resolvers by import --
// one implementation of "does this path/symbol/metric resolve", not two --
// and adds the checks a prose policy file needs and a JSON roster does not.
//
// Six check classes, each cheap and offline:
//   citations   paths, path:line and named symbols in policy prose resolve
//   counts      a literal count in policy prose matches its derivation
//   no-gh       no `gh <verb>` outside the MCP mapping table
//   budgets     one-sided size caps: a policy file may shrink, never grow
//   index       CLAUDE.md names every policy file, and every file it names exists
//   duplicates  no 12-word run shared between two policy files
//
// Every class is otherwise deletable in silence, so the no-arg (CI) path also
// runs an acceptance over fixtures/policy-rot/, which states the errors each
// class must still produce. A run that finds nothing and a gutted linter look
// identical without it.
//
//   node .claude/workflows/policy_lint.mjs            # lint + acceptance (CI)
//   node .claude/workflows/policy_lint.mjs --list     # every check + fixture
//   node .claude/workflows/policy_lint.mjs --budgets  # sizes vs caps
//   node .claude/workflows/policy_lint.mjs --report   # enforcement summary
//   node .claude/workflows/policy_lint.mjs <files...> # lint just these
//   node .claude/workflows/policy_lint.mjs --record-known-bad   # reseed the ratchet
//   node .claude/workflows/policy_lint.mjs --pr-body <file> --head <sha> [--title t] [--red names]

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'
import {
  trackedFiles,
  resolvePathToken,
  symbolInTree,
  budgets,
  resolveMetricName,
  liveVersion,
  tagRefsIn,
  fileLines,
  symbolCandidates,
  PATH_TOKEN_RE,
  PATHLINE_RE,
  METRIC_LITERAL_RE,
  NEGATION_RE,
} from './brief_lint.mjs'

// brief_lint's CODE_EXTS has no `mdc`, because a wave roster never cites one.
// Half this corpus's citations are `.cursor/rules/*.mdc`, so they are matched
// here rather than by widening a regex the roster linter depends on.
const MDC_PATH_RE = /(?<![\w./-])\.?(?:[A-Za-z0-9_][A-Za-z0-9_.-]*\/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\.mdc\b/g
// ...and the same for `file.mdc:120`, which PATHLINE_RE cannot see for the same
// reason. Named groups match brief_lint's, so one loop handles both.
const MDC_PATHLINE_RE =
  /(?<![\w./-])(?<pth>\.?(?:[A-Za-z0-9_][A-Za-z0-9_.-]*\/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\.mdc):(?<start>\d+)(?:[-\u2013](?<end>\d+))?\+?/g

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')

function git(args, { allowFail = false } = {}) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
  } catch (e) {
    if (allowFail) return ''
    throw e
  }
}

// symbolInTree greps the whole tracked tree, and the policy file being linted
// is tracked, so a symbol invented in that file resolved against itself. That
// inverted the check on 24 of 28 files: brief_lint is immune only because its
// rosters live under the `.claude/` prefix it already excludes.
// Excluding only the file under test was not enough: a symbol invented in two
// policy files resolved against the other one, so a pair of briefs could keep
// each other's dead citation alive indefinitely. A policy file's symbol has to
// resolve against production, tests or tooling -- prose citing prose is the
// thing this check exists to catch.
// The MCP mapping table in `web-fragments.md` is the registry of tools that
// live OUTSIDE this repository, which is why the symbol pass already skips that
// file entirely. A contract instructing one of those tools cites a real thing
// that no tree grep can find, so the table is consulted as an allowlist.
//
// Deliberately an allowlist and not a directory exemption: `.claude/workflows/`
// also holds the wave scripts, whose prompt strings are brief PROSE citing
// production symbols. Widening the grep to that directory made five genuinely
// dead citations resolve against prose that merely mentions them -- the same
// prose-citing-prose trap the `.cursor/` exclusion exists for.
let _mcpTools = null
function isMcpTool(symbol) {
  if (!_mcpTools) {
    const raw = read('.claude/workflows/web-fragments.md') ?? ''
    const block = /const GH = `([\s\S]*?)`/.exec(raw)
    _mcpTools = new Set(
      block ? [...block[1].matchAll(/\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b/g)].map((m) => m[1]) : []
    )
  }
  return _mcpTools.has(symbol)
}

// The budget file's own keys are the second allowlist. A rule that governs the
// caps has to name them, and they live under `.claude/`, which the grep below
// excludes wholesale for a reason the comment above states. Sourced FROM the
// file rather than hand-listed, so it cannot drift: a key that is renamed stops
// being citable in the same commit that renames it.
//
// Extending the grep to `.claude/workflows/*.mjs` instead was measured and
// refused -- `SCREAMING_SNAKE` and `min_ink_gap`, two of the five dead
// citations the wholesale exclusion keeps dead, resolve against COMMENTS in
// `brief_lint.mjs` that name them precisely to say they are not pinned. The
// known-bad ledger reported both as `entry no longer fires`. An extension is
// prose or code by what it holds, not by its name.
let _budgetKeys = null
function isBudgetKey(symbol) {
  if (!_budgetKeys) {
    _budgetKeys = new Set()
    try {
      const b = JSON.parse(read(BUDGET_FILE) ?? '{}')
      for (const k of Object.keys(b)) _budgetKeys.add(k)
      for (const k of Object.keys(b.roles ?? {})) _budgetKeys.add(k)
      for (const spec of Object.values(b.roles ?? {})) for (const k of Object.keys(spec)) _budgetKeys.add(k)
    } catch {}
  }
  return _budgetKeys.has(symbol)
}

let _policySpec = null
function symbolElsewhere(symbol, exceptRel) {
  if (isMcpTool(symbol)) return true
  if (isBudgetKey(symbol)) return true
  if (!_policySpec) _policySpec = policyFiles().map((f) => `:!${f}`)
  const spec = _policySpec.includes(`:!${exceptRel}`) ? _policySpec : [..._policySpec, `:!${exceptRel}`]
  const out = git(
    ['grep', '-I', '-l', '-w', '-F', symbol, '--', '.', ':!.claude', ':!.cursor', ':!tools/audit/round2', ...spec],
    { allowFail: true }
  )
  return !!(out && out.trim())
}

// A path or symbol cited alongside a tag SHA is checked AT that tag, which is
// what brief_lint's rule 1 does. The first draft skipped the whole FILE when
// any hex token appeared anywhere in it, so one tag citation in a header
// disabled every path and symbol check below it -- on six files, three of them
// role contracts. The skip is now per token and has to resolve at the ref.
const _refListing = new Map()
function refListing(ref) {
  if (_refListing.has(ref)) return _refListing.get(ref)
  const out = git(['ls-tree', '-r', '--name-only', ref], { allowFail: true })
  const list = out ? out.split('\n').filter(Boolean) : null
  _refListing.set(ref, list)
  return list
}

function pathAtRef(ref, token) {
  const list = refListing(ref)
  if (!list) return false
  if (list.includes(token)) return true
  const base = path.posix.basename(token)
  return list.some((f) => path.posix.basename(f) === base)
}

function symbolAtRef(ref, symbol) {
  const out = git(['grep', '-I', '-l', '-w', '-F', symbol, ref], { allowFail: true })
  return !!(out && out.trim())
}

// resolvePathToken resolves a bare basename against ANY tracked file sharing it,
// which is right for "does this path exist" and wrong for "is line N inside it":
// a citation like `README.md:400` would be measured against whichever same-named
// file the listing happened to yield. A line range is only checked where the
// basename is unambiguous.
let _byBase = null
function candidatesFor(token) {
  if (!_byBase) {
    _byBase = new Map()
    for (const f of git(['ls-files']).split('\n').filter(Boolean)) {
      const b = path.posix.basename(f)
      if (!_byBase.has(b)) _byBase.set(b, [])
      _byBase.get(b).push(f)
    }
  }
  const exact = _byBase.get(path.posix.basename(token)) ?? []
  if (exact.includes(token)) return [token]
  return exact
}

function read(rel) {
  try {
    return fs.readFileSync(path.join(ROOT, rel), 'utf8')
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// The policy set. Everything CLAUDE.md's "Where the policy is" section binds a
// seat to, plus the two READMEs a seat is sent to read. Kept as globs resolved
// against the tracked tree so a new brief joins without editing this list.

const POLICY_GLOBS = [
  /^CLAUDE\.md$/,
  // `.cursor/rules/*.mdc` is NOT here: it is generated from `.claude/rules/`
  // by rules_sync.mjs, whose --check byte-compares it. Linting a generated copy
  // reports every finding twice, doubles every ledger entry, and -- since the
  // bodies are identical by construction -- makes `duplicates` refuse all five.
  // The source is linted; the output is compared.
  /^\.claude\/rules\/[a-z0-9-]+\.md$/,
  /^tools\/audit\/briefs\/[A-Za-z0-9_.-]+\.md$/,
  /^tools\/audit\/README\.md$/,
  /^tests\/README\.md$/,
  /^docs\/HANDOVER\.md$/,
  /^\.claude\/workflows\/web-fragments\.md$/,
  // A skill is seat-facing text loaded by the harness at the moment a pull
  // request event arrives, which makes it policy with an unusually short path
  // to acting on it. It is linted like the rest.
  /^\.claude\/skills\/[a-z0-9-]+\/SKILL\.md$/,
]

// Always loaded by a tool, so their size is charged to every session.
//
// `CLAUDE.md` always. A `.claude/rules/*.md` only when it has NO `paths:` key:
// the harness loads an unscoped rule at session start and a scoped one when the
// seat reads a file matching one of its globs. Charging a scoped rule to every
// session would overstate the floor and make the cap refuse the very scoping
// that lowers it.
const RULE_FILE = /^\.claude\/rules\/[a-z0-9-]+\.md$/
function isAlwaysLoaded(rel) {
  if (rel === 'CLAUDE.md') return true
  if (!RULE_FILE.test(rel)) return false
  const raw = read(rel)
  if (raw == null) return false
  const fm = /^---\n([\s\S]*?)\n---/.exec(raw)
  return !(fm && /^paths:/m.test(fm[1]))
}

// Every tracked file under a policy DIRECTORY has to be matched by a glob
// above. A one-character gap is enough to lose one silently: the `.mdc` pattern
// allowed no digits while the `.claude/rules/` pattern beside it did, so a rule
// file with a digit in its name would have left the corpus entirely and the run
// would still have printed `TOTAL: 0`. This is the same argument
// closure.orphan_files() makes about the gate -- a file that is neither matched
// nor deliberately excluded is an oversight, not a pass.
const POLICY_DIRS = [/^\.cursor\/rules\//, /^\.claude\/rules\//, /^\.claude\/skills\//, /^tools\/audit\/briefs\//]
// The one deliberate exclusion: write-once evidence committed under briefs/.
const POLICY_DIR_EXCLUDE = [
  /^tools\/audit\/briefs\/.*\.(json|txt|png|svg)$/,
  // Generated from `.claude/rules/` and byte-compared by `rules_sync --check`,
  // which is a stronger guarantee than linting it a second time would give.
  /^\.cursor\/rules\/[a-z0-9-]+\.mdc$/,
]

// `files` is injectable for ONE reason: the acceptance. This check runs over
// the tracked tree, where a healthy corpus produces nothing, so a fixture
// directory cannot make it fire and the whole check was deletable in silence --
// `--self-test` 11/11 and `FIXTURE ok` both stayed green with the call site
// removed. Passing a synthetic file list is what lets the pin invoke the real
// function instead of re-testing its regexes, which is a different change.
function uncoveredPolicyFiles(files = null) {
  const list = files ?? trackedFiles().list
  return list
    .filter((f) => POLICY_DIRS.some((re) => re.test(f)))
    .filter((f) => !POLICY_GLOBS.some((re) => re.test(f)))
    .filter((f) => !POLICY_DIR_EXCLUDE.some((re) => re.test(f)))
    .sort()
}

// The corpus-level checks, as a LIST rather than four calls inline, so the
// acceptance can assert what is in it. `checkCoverage` was pinned by the
// acceptance calling it directly, which left it deletable from the pipeline
// with every pin green.
//
// The list pins MEMBERSHIP AND IDENTITY, and that is all it pins. It does not
// pin that the loop over it runs: truncating `main`'s own `for` line disables a
// check with the list intact, and no assertion inside a program can pin its own
// last call site. One unpinned hop, named here rather than claimed away.
//
// Membership alone was not enough either. `length === 4` is arity, and three
// different edits keep the arity while disabling the check: a no-op arrow, a
// duplicated entry, and -- the one that needs no malice -- replacing the
// wrapper below with `checkCoverage` itself. That last is a ONE-TOKEN cleanup
// an earlier version of this comment openly invited, and it silently voids the
// check, because the loop passes the POLICY FILE list and every policy file is
// covered by definition. Hence the name, and hence asserting names.
const CORPUS_CHECK_NAMES = ['checkIndex', 'checkDuplicates', 'checkBudgets', 'coverageOverTree']
const CORPUS_CHECKS = []

// Named, not an arrow, so removing the wrapper is a rename the acceptance sees.
// It discards the loop's argument deliberately: the loop passes the POLICY FILE
// list, and coverage's whole subject is a file that list does not contain.
//
// A name pin is not a behaviour pin. Asserting only the name left two silent
// mutations -- a body of `return []`, and one forwarding the loop's argument as
// `checkCoverage(files)` -- each of which keeps every pin green and stops the
// check firing. `coverageFileSource` exists so the acceptance can drive this
// wrapper for real: it returns null in production, which `checkCoverage` reads
// as "the tracked tree", and the acceptance swaps it for a synthetic list. Both
// mutations then fail, because `return []` reports nothing and a forwarded
// `files` is undefined here and falls back to the tree.
let coverageFileSource = () => null

function coverageOverTree() {
  return checkCoverage(coverageFileSource())
}

function checkCoverage(files = null) {
  return uncoveredPolicyFiles(files).map((f) => ({
    severity: 'error',
    check: 'coverage',
    where: f,
    message: `sits in a policy directory and matches no POLICY_GLOBS pattern, so no check in this file has ever read it. Widen the glob, or exclude it deliberately.`,
  }))
}

function policyFiles() {
  const { list } = trackedFiles()
  return list.filter((f) => POLICY_GLOBS.some((re) => re.test(f))).sort()
}

// ---------------------------------------------------------------------------
// Derivations. Every count a policy file is allowed to state is computed here
// from the artefact itself, never carried. CLAUDE.md's own rule: "derive the
// count, do not carry one".

function jsonKeys(rel, key) {
  const raw = read(rel)
  if (!raw) return null
  const d = JSON.parse(raw)
  return key ? Object.keys(d[key]).length : Object.keys(d).length
}

function countMatches(rel, re) {
  const raw = read(rel)
  if (!raw) return null
  return (raw.match(re) || []).length
}

function derivations() {
  const d = {}
  const b = read('tests/structure_budgets.json')
  if (b) d.budgets = Object.keys(JSON.parse(b)).filter((k) => k !== 'recorded_at').length
  d.scripts = jsonKeys('tests/closures.json', 'closures')
  d.rules = git(['ls-files', '.cursor/rules/*.mdc']).trim().split('\n').filter(Boolean).length
  d.briefs = git(['ls-files', 'tools/audit/briefs/D*.md']).trim().split('\n').filter(Boolean).length
  d.jobs = countMatches('.github/workflows/tests.yml', /^ {2}[a-z0-9-]+:$/gm)
  const card = read('tests/card_drift.mjs')
  if (card) {
    const m = card.match(/const STATES = \[[\s\S]*?\n\]/)
    d.states = m ? (m[0].match(/\bname:/g) || []).length : null
  }
  d.services = countMatches('custom_components/heatpump_optimizer/services.yaml', /^[a-z_]+:/gm)
  d.modules = git(['ls-files', 'custom_components/heatpump_optimizer/']).trim().split('\n').filter((f) => f.endsWith('.py')).length
  d.goldens = git(['ls-files', 'tests/golden/*.json']).trim().split('\n').filter(Boolean).length
  return d
}

// Number words the corpus actually uses, so "fourteen of sixteen" is checked.
const WORDS = {
  two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
  eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16,
  seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20, 'twenty-one': 21,
  'twenty-two': 22, 'twenty-three': 23, 'twenty-four': 24,
}
const NUM = `(\\d+|${Object.keys(WORDS).join('|')})`
function toNum(tok) {
  return /^\d+$/.test(tok) ? Number(tok) : WORDS[tok.toLowerCase()]
}

// Each rule: a regex whose first group is the stated count, and the derivation
// key it must equal. Deliberately narrow -- a rule that over-fires gets the
// linter bypassed, which is the failure mode this whole script exists to stop.
const COUNT_RULES = [
  { key: 'budgets', re: new RegExp(`${NUM}\\s+(?:budgets|metrics)\\b`, 'gi'), what: 'metrics in tests/structure_budgets.json' },
  { key: 'scripts', re: new RegExp(`(?:of|all)\\s+${NUM}\\s+scripts?\\b`, 'gi'), what: 'selectable scripts in tests/closures.json' },
  { key: 'rules', re: new RegExp(`${NUM}\\s+(?:\`?alwaysApply\`?\\s+)?policies\\b`, 'gi'), what: '.cursor/rules/*.mdc files' },
  { key: 'states', re: new RegExp(`(?:STATES\\s*\\(${NUM}\\)|card's\\s+${NUM}\\s+states)\\b`, 'gi'), what: 'entries in card_drift.mjs STATES' },
  { key: 'services', re: new RegExp(`${NUM}\\s+services\\b`, 'gi'), what: 'keys in services.yaml' },
  { key: 'modules', re: new RegExp(`${NUM}\\s+modules\\b`, 'gi'), what: 'modules in custom_components/heatpump_optimizer/' },
  { key: 'goldens', re: new RegExp(`${NUM}\\s+GOLDEN\\s+SCENARIOS\\b|${NUM}\\s+golden\\s+fixtures\\b`, 'g'), what: 'fixtures in tests/golden/' },
  { key: 'briefs', re: new RegExp(`${NUM}\\s+dimension\\s+briefs\\b`, 'gi'), what: 'tools/audit/briefs/D*.md' },
]

// A count inside a quotation, an example, or a passage the file itself marks
// as history is a record of what was once measured, not a live claim.
const HISTORY_LINE = /^\s*(?:>|\|?\s*BORN:|EXAMPLE|#{1,6}\s|.*\b(?:once|used to|at the time|was then|historical|superseded)\b)/i

function checkCounts(rel, text, derived) {
  const out = []
  const lines = text.split('\n')
  lines.forEach((line, i) => {
    if (HISTORY_LINE.test(line)) return
    for (const rule of COUNT_RULES) {
      const want = derived[rule.key]
      if (want == null) continue
      rule.re.lastIndex = 0
      let m
      while ((m = rule.re.exec(line))) {
        const tok = m[1] || m[2]
        if (!tok) continue
        const got = toNum(tok)
        if (got == null || got === want) continue
        out.push({
          severity: 'error',
          check: 'counts',
          where: `${rel}:${i + 1}`,
          message: `states ${tok} for ${rule.what}; derived ${want}. Derive the count, do not carry one.`,
        })
      }
    }
  })
  return out
}

// ---------------------------------------------------------------------------
// no-gh. The seats run in a container with no `gh` binary; web-fragments.md
// carries the MCP mapping and is the one place the string may appear.

const GH_RE = /\bgh\s+(pr|issue|run|api|release|secret|workflow)\b/g
const GH_ALLOWED = /^\.claude\/workflows\/web-fragments\.md$/

function checkNoGh(rel, text) {
  if (GH_ALLOWED.test(rel)) return []
  const out = []
  text.split('\n').forEach((line, i) => {
    GH_RE.lastIndex = 0
    let m
    while ((m = GH_RE.exec(line))) {
      out.push({
        severity: 'error',
        check: 'no-gh',
        where: `${rel}:${i + 1}`,
        message: `names \`gh ${m[1]}\`; no gh binary exists in the seat environment. Use the MCP mapping in .claude/workflows/web-fragments.md.`,
      })
    }
  })
  return out
}

// ---------------------------------------------------------------------------
// citations. Paths, path:line and named symbols, resolved with brief_lint's
// own resolvers so there is one implementation of "does this resolve".

const CODEFENCE = /^\s*(?:```|~~~)/
// A markdown indented code block. Every fenced-or-indented block in this corpus
// is a command, and a command's arguments are not citations: fixer.md's own
// `cat "$D/scope.txt"` is a shell variable, not a path that should resolve.
const INDENTED_CODE = /^ {4,}\S/

function checkCitations(rel, text) {
  const out = []
  const lines = text.split('\n')
  const refs = tagRefsIn(text)
  const atSomeRef = (fn) => refs.some((r) => fn(r))
  const prose = []
  let inFence = false
  lines.forEach((line, i) => {
    if (CODEFENCE.test(line)) {
      inFence = !inFence
      return
    }
    if (inFence || INDENTED_CODE.test(line)) return
    prose.push(line)
    const where = `${rel}:${i + 1}`

    // path:line and path:start-end. A line number is the citation form most
    // likely to rot without the path rotting: brief-citations.mdc's own GOOD
    // example had drifted 1,577 lines by the time this audit measured it.
    const pathLineSpans = []
    const pathLines = []
    for (const re of [PATHLINE_RE, MDC_PATHLINE_RE]) {
      re.lastIndex = 0
      let hit
      while ((hit = re.exec(line))) {
        pathLineSpans.push([hit.index, hit.index + hit[0].length])
        pathLines.push(hit)
      }
    }
    for (const pl of pathLines) {
      const tok = pl.groups.pth
      if (NEGATION_RE.test(line.slice(0, pl.index))) continue
      const resolved = resolvePathToken(tok)
      if (!resolved) {
        if (atSomeRef((r) => pathAtRef(r, tok))) continue
        out.push({
          severity: 'error',
          check: 'citations',
          where,
          message: `path \`${tok}\`: not in the tree, and no tag SHA is cited alongside it`,
        })
        continue
      }
      // A bare basename can name several files (`README.md` names four here),
      // and resolvePathToken hands back whichever the listing yielded. Measuring
      // the line number against that one is arbitrary: it invents a failure when
      // the cited file is the longer sibling. So the citation is out of range
      // only when it is out of range for EVERY candidate -- which keeps the
      // check on ambiguous names instead of dropping it.
      const cands = candidatesFor(tok)
      const lengths = cands
        .map((c) => fileLines(c))
        .filter(Boolean)
        .map((b) => Math.max(1, b.length - (b[b.length - 1] === '' ? 1 : 0)))
      if (!lengths.length) continue
      const last = Math.max(...lengths)
      const want = Number(pl.groups.end || pl.groups.start)
      if (want > last) {
        out.push({
          severity: 'error',
          check: 'citations',
          where,
          message: `line citation \`${tok}:${pl.groups.start}${pl.groups.end ? '-' + pl.groups.end : ''}\` runs past ${cands.length > 1 ? `every file named ${path.posix.basename(tok)}, the longest of which has` : `${resolved}, which has`} ${last} lines. Cite a quoted phrase or a symbol; a line number rots on the next edit.`,
        })
      }
    }
    const inPathLine = (idx) => pathLineSpans.some(([a, b]) => idx >= a && idx < b)

    // Plain path tokens, plus `.mdc` -- brief_lint's extension list has no
    // `mdc` because a wave roster never cites one, and half of THIS corpus's
    // citations are `.cursor/rules/*.mdc`.
    for (const re of [PATH_TOKEN_RE, MDC_PATH_RE]) {
      re.lastIndex = 0
      let m
      while ((m = re.exec(line))) {
        const tok = m[0]
        if (inPathLine(m.index)) continue
        if (NEGATION_RE.test(line.slice(0, m.index))) continue
        if (tok === path.posix.basename(rel) || tok === rel) continue
        // `mock.patch`, `foo.out`: a bare word.word with an ambiguous extension
        // is a dotted symbol (module.attr), which the symbol pass already covers.
        if (!tok.includes('/') && /\.(patch|out|txt)$/.test(tok)) continue
        // A glob (`wave-*-groups.json`) leaves a fragment after the star. The
        // pattern is the citation; the fragment never resolves and never should.
        if (/[*?][A-Za-z0-9_.-]{0,12}$/.test(line.slice(0, m.index))) continue
        if (resolvePathToken(tok)) continue
        if (atSomeRef((r) => pathAtRef(r, tok))) continue
        out.push({
          severity: 'error',
          check: 'citations',
          where,
          message: `path \`${tok}\`: not in the tree, and no tag SHA is cited alongside it`,
        })
      }
    }

    METRIC_LITERAL_RE.lastIndex = 0
    const isExample = /\b(?:always an error|# ?BAD|EXAMPLE BAD)\b/i.test(line)
    let m
    while ((m = METRIC_LITERAL_RE.exec(line))) {
      if (!resolveMetricName(m[1])) continue
      if (isExample) continue
      out.push({
        severity: 'error',
        check: 'citations',
        where,
        message: `metric literal \`${m[0].trim()}\`: a budget value is always re-measured at the seat's merge base, never quoted`,
      })
    }
  })

  // The MCP mapping table names tools that live outside this repository; that
  // is its whole job, so the symbol pass would report every row.
  if (GH_ALLOWED.test(rel)) return out

  // Named symbols: backticked identifiers that look like code. Reported once
  // per file per symbol, because a contract repeats its own nouns.
  const seen = new Set()
  // Prose only. Reading the whole file meant a shell variable inside a fenced
  // command was a "symbol", while the path pass in the same function skipped
  // exactly those lines -- two passes over one file disagreeing about what
  // counts as text.
  const backticked = prose.join('\n').match(/`[^`\n]{2,60}`/g) || []
  for (const b of backticked) {
    const inner = b.slice(1, -1)
    if (/[\s/]/.test(inner)) continue
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(inner)) continue
    if (!symbolCandidates(inner).length) continue
    if (seen.has(inner)) continue
    seen.add(inner)
    // symbolInTree greps the whole tracked tree, and the file being linted IS
    // tracked, so a symbol invented in a policy file resolved against its own
    // citation. brief_lint is immune only because rosters live under the
    // `.claude/` prefix its exclude list already carries.
    if (symbolElsewhere(inner, rel)) continue
    if (atSomeRef((r) => symbolAtRef(r, inner))) continue
    out.push({
      severity: 'error',
      check: 'citations',
      where: rel,
      message: `symbol \`${inner}\`: not found in the tracked tree, and no tag SHA is cited in this file`,
    })
  }
  return out
}

// ---------------------------------------------------------------------------
// budgets. One-sided caps: a policy file may shrink freely, never grow past
// its cap. Deliberately NOT the two-sided ratchet tests/structure.py uses --
// an "improved and not yet recorded" refusal on prose would punish deletion,
// which is the behaviour this audit wants.

const BUDGET_FILE = '.claude/workflows/policy_budgets.json'

function policyBudgets() {
  const raw = read(BUDGET_FILE)
  return raw ? JSON.parse(raw) : null
}

function countLines(raw) {
  if (raw === '') return 0
  const n = (raw.match(/\n/g) || []).length
  return raw.endsWith('\n') ? n : n + 1
}

function sizes(files) {
  const rows = []
  for (const f of files) {
    const raw = read(f)
    if (raw == null) continue
    // `split('\n').length` counts the empty string after a file's final
    // newline, so every cap read one line higher than `wc -l` on the same file.
    // A seat that cuts until `wc -l` matches its cap was still refused, and the
    // error named a number no local command produced -- reported on #612 by a
    // reviewer who noticed the control print 320 where `wc -l` said 319. Count
    // what `wc -l` counts: newline-terminated lines, plus a trailing partial.
    rows.push({ file: f, lines: countLines(raw), bytes: Buffer.byteLength(raw), always: isAlwaysLoaded(f) })
  }
  return rows
}

function checkBudgets(files) {
  const b = policyBudgets()
  if (!b) return []
  const out = []
  const rows = sizes(files)
  for (const r of rows) {
    const cap = b.files[r.file]
    if (cap == null) {
      out.push({
        severity: 'error',
        check: 'budgets',
        where: r.file,
        message: `no line cap recorded in ${BUDGET_FILE}. A new policy file is classified deliberately or not at all.`,
      })
      continue
    }
    if (r.lines > cap) {
      out.push({
        severity: 'error',
        check: 'budgets',
        where: r.file,
        message: `${r.lines} lines exceeds its cap of ${cap}. Cut, or state the case for a higher cap in the pull request body.`,
      })
    }
  }
  const alwaysTokens = rows.filter((r) => r.always).reduce((n, r) => n + Math.round(r.bytes / 4), 0)
  if (b.always_loaded_tokens != null && alwaysTokens > b.always_loaded_tokens) {
    out.push({
      severity: 'error',
      check: 'budgets',
      where: '(always-loaded set)',
      message: `about ${alwaysTokens} tokens exceeds the cap of ${b.always_loaded_tokens}. Every seat pays this before its first productive read.`,
    })
  }

  // The floor is not the cost. `always_loaded_tokens` measures a session that
  // opens nothing, so moving prose out of `CLAUDE.md` into a `paths:`-scoped
  // rule lowers it without deleting a line -- measured across the index split,
  // the floor fell 6800 -> 3198 while the corpus moved 57398 -> 57325, a 53%
  // drop against 0.13% of actual deletion. Recording that drop as the ratchet
  // would hand a later pull request headroom nobody earned, and would price a
  // scoped rule at zero however far it grew. Two more one-sided caps close it:
  // the corpus, which a move does not change, and the per-role load, which is
  // what a seat that opens a file actually pays.
  const corpusTokens = rows.reduce((n, r) => n + Math.round(r.bytes / 4), 0)
  if (b.corpus_tokens != null && corpusTokens > b.corpus_tokens) {
    out.push({
      severity: 'error',
      check: 'budgets',
      where: '(whole corpus)',
      message: `about ${corpusTokens} tokens exceeds the cap of ${b.corpus_tokens}. Moving prose between policy files does not change this number, which is why it is here: cut it, or raise the cap in the diff a reviewer reads.`,
    })
  }

  for (const [role, spec] of Object.entries(b.roles || {})) {
    const t = roleTokens(rows, spec.opens)
    if (spec.cap != null && t > spec.cap) {
      out.push({
        severity: 'error',
        check: 'budgets',
        where: `(role ${role})`,
        message: `about ${t} tokens exceeds the cap of ${spec.cap}. This is what the seat loads once it opens ${spec.opens.join(', ')} -- the floor in always_loaded_tokens is what it pays before that.`,
      })
    }
  }
  return out
}

// A rule's `paths:` globs decide when the harness loads it, so a role's real
// load is the floor plus every rule whose globs match a file that role opens.
// `opens` is a representative file per surface, not an exhaustive list: the cap
// is a ratchet on a fixed sample, and changing the sample is a visible edit to
// the budget file rather than a silent re-measurement.
function globToRe(g) {
  const re = g
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*\*\//g, '\u0000')
    .replace(/\*\*/g, '\u0000')
    .replace(/\*/g, '[^/]*')
    .replace(/\?/g, '[^/]')
    .replace(/\u0000/g, '.*')
  return new RegExp('^' + re + '$')
}

function rulePaths(rel) {
  const raw = read(rel)
  if (raw == null) return null
  const fm = /^---\n([\s\S]*?)\n---/.exec(raw)
  if (!fm) return null
  // The frontmatter capture stops BEFORE the closing `\n---`, so the last
  // `paths:` entry has no trailing newline. A block pattern that requires one
  // per line therefore drops it, and a rule with a single path matched zero
  // lines and read as unscoped -- silently, because the run still printed a
  // number. Restore the newline before matching.
  const fmBody = fm[1] + '\n'
  const block = /^paths:\n((?:[ \t]*-[ \t]*.*\n)+)/m.exec(fmBody)
  if (!block) return null
  return [...block[1].matchAll(/-\s*"([^"]+)"/g)].map((m) => m[1])
}

function roleTokens(rows, opens) {
  let total = 0
  for (const r of rows) {
    if (r.always) { total += Math.round(r.bytes / 4); continue }
    if (!RULE_FILE.test(r.file)) continue
    const globs = rulePaths(r.file)
    if (!globs) continue
    if (globs.some((g) => opens.some((o) => globToRe(g).test(o)))) total += Math.round(r.bytes / 4)
  }
  return total
}

// ---------------------------------------------------------------------------
// index. CLAUDE.md is the only auto-loaded file, so it is the index. Checked
// in BOTH directions: every policy file it names exists, and every policy file
// in the tree is named. The audit found a role-contract row pointing at a file
// that had never existed, and a first draft naming 8 of 24 policy documents.

function checkIndex(files, indexRel = 'CLAUDE.md') {
  const text = read(indexRel)
  if (text == null) return []
  const out = []
  const named = new Set()
  for (const re of [PATH_TOKEN_RE, MDC_PATH_RE]) {
    re.lastIndex = 0
    let m
    while ((m = re.exec(text))) {
      named.add(m[0])
      // ...and its basename. PATH_TOKEN_RE cannot begin with a dot, so a path
      // the index writes as `.claude/skills/steward/SKILL.md` is captured with
      // the leading dot shorn off and matches neither the full path nor the
      // bare-filename pattern below. The index would then report a file it
      // plainly names as unnamed. Recording the basename is right on its own
      // terms as well: naming `a/b.md` is naming `b.md`.
      named.add(path.posix.basename(m[0]))
    }
  }
  // Also catch bare brief names in the role-contract tables ("fixer.md").
  for (const b of text.match(/`[A-Za-z0-9_.-]+\.(?:md|mdc)`/g) || []) named.add(b.slice(1, -1))

  for (const tok of named) {
    if (!/\.(md|mdc)$/.test(tok)) continue
    if (resolvePathToken(tok)) continue
    out.push({
      severity: 'error',
      check: 'index',
      where: indexRel,
      message: `names \`${tok}\`, which is not in the tree. A seat sent to a file that does not exist cannot comply.`,
    })
  }
  for (const f of files) {
    if (f === indexRel) continue
    const base = path.posix.basename(f)
    if (named.has(f) || named.has(base)) continue
    out.push({
      severity: 'error',
      check: 'index',
      where: indexRel,
      message: `does not name \`${f}\`. The index is the only way a seat finds a policy file; an unnamed one binds nobody.`,
    })
  }
  return out
}

// ---------------------------------------------------------------------------
// duplicates. A 12-word run shared by two policy files is one obligation
// stated twice; the audit measured 263 obligations with two or more copies and
// eight that had drifted into disagreeing. Quotations are exempt.

const SHINGLE = 12

function normalise(line) {
  return line
    .replace(/`[^`]*`/g, ' ')
    .replace(/[^A-Za-z0-9 ]+/g, ' ')
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
}

function checkDuplicates(files) {
  const seen = new Map()
  const out = []
  for (const f of files) {
    const text = read(f)
    if (text == null) continue
    let inFence = false
    text.split('\n').forEach((line, i) => {
      if (CODEFENCE.test(line)) {
        inFence = !inFence
        return
      }
      if (inFence || /^\s*>/.test(line)) return
      const w = normalise(line)
      for (let k = 0; k + SHINGLE <= w.length; k++) {
        const key = w.slice(k, k + SHINGLE).join(' ')
        const prev = seen.get(key)
        if (prev && prev.file !== f) {
          out.push({
            severity: 'error',
            check: 'duplicates',
            where: `${f}:${i + 1}`,
            message: `repeats 12 words from ${prev.where}. State an obligation once and link to it; two copies drift apart.`,
          })
          return
        }
        if (!prev) seen.set(key, { file: f, where: `${f}:${i + 1}` })
      }
    })
  }
  return out
}

// ---------------------------------------------------------------------------
// The known-bad list. This linter lands on a corpus that already fails it, so
// today's failures are recorded once and suppressed. Two properties make that
// a ratchet rather than an amnesty: a finding NOT on the list is an error, so
// the corpus can never get worse; and an entry that no longer fires is an
// error too, so a fix must delete its entry and the list can only shrink.
// Growing it is possible only by editing this file in a diff a reviewer reads.

const KNOWN_BAD_FILE = '.claude/workflows/policy_known_bad.json'

function knownBad() {
  const raw = read(KNOWN_BAD_FILE)
  return raw ? JSON.parse(raw) : { entries: [] }
}

// The key deliberately drops line numbers, in `where` and inside the message.
// An entry keyed on one stops matching the moment a line is added above it,
// and the ratchet then reports the entry as fixed while the defect is still
// there -- the silent drain this list exists to prevent. The cost is that
// several occurrences of one defect class in one file collapse to a single
// entry, so the entry survives until the last is fixed. That errs toward
// keeping an entry too long, never toward dropping a live defect.
function keyOf(f) {
  const where = f.where.replace(/:\d+$/, '')
  const message = f.message.replace(/:\d+\b/g, ':N').slice(0, 60)
  return `${f.check}|${where}|${message}`
}

// Classes the ledger may never suppress. The list freezes defects the corpus
// already HAS, so they can be drained; these two are not that. A budget breach
// is something the change in front of you just did, and a policy file no check
// reads is not a state to record and live with. Recording either turns a
// refusal into a note, which is the failure the whole ratchet is against --
// measured: with both live, `--record-known-bad` then a re-run gave `TOTAL: 0`
// and exit 0.
const NEVER_SUPPRESSED = new Set(['budgets', 'coverage'])

function applyKnownBad(findings) {
  const kb = knownBad()
  // Entries are {key, count}. A bare string is read as one occurrence, so an
  // older file still parses rather than silently suppressing everything.
  const recorded = new Map()
  for (const e of kb.entries ?? []) {
    if (typeof e === 'string') recorded.set(e, 1)
    else recorded.set(e.key, e.count ?? 1)
  }

  const live = new Map()
  const out = []
  for (const f of findings) {
    if (NEVER_SUPPRESSED.has(f.check)) {
      out.push(f)
      continue
    }
    const k = keyOf(f)
    if (!live.has(k)) live.set(k, [])
    live.get(k).push(f)
  }

  let suppressed = 0
  let occurrences = 0
  for (const [k, group] of live) {
    if (!recorded.has(k)) {
      out.push(...group)
      continue
    }
    const want = recorded.get(k)
    const got = group.length
    if (got > want) {
      // THE POINT OF THE COUNT. Keys drop line numbers so an entry survives an
      // edit above it -- but that also made every occurrence of one class in one
      // file share an entry, so a NEW `gh pr` line in a file that already had one
      // landed on a suppressed key and passed. The corpus could get worse in
      // silence, which is the mirror of the defect the normalisation fixed.
      out.push({
        severity: 'error',
        check: 'known-bad',
        where: KNOWN_BAD_FILE,
        message: `${got} occurrence(s) of a recorded defect, ${want} recorded: ${k}. The list may only shrink; fix the new one.`,
      })
    } else if (got < want) {
      out.push({
        severity: 'error',
        check: 'known-bad',
        where: KNOWN_BAD_FILE,
        message: `${got} occurrence(s) left of ${want} recorded: ${k}. Re-record with --record-known-bad, or the headroom lets it come back unseen.`,
      })
    }
    occurrences += Math.min(got, want)
    suppressed++
  }
  for (const k of recorded.keys()) {
    if (live.has(k)) continue
    out.push({
      severity: 'error',
      check: 'known-bad',
      where: KNOWN_BAD_FILE,
      message: `entry no longer fires: ${k}. It was fixed, so delete the entry; the list may only shrink.`,
    })
  }
  return { live: out, suppressed, occurrences, total: recorded.size }
}

const CHECKS = [
  { name: 'citations', what: 'paths, path:line and symbols in policy prose resolve', fixture: 'fixtures/policy-rot/citations.md' },
  { name: 'counts', what: 'a literal count matches its derivation', fixture: 'fixtures/policy-rot/counts.md' },
  { name: 'no-gh', what: 'no `gh <verb>` outside the MCP mapping table', fixture: 'fixtures/policy-rot/no-gh.md' },
  { name: 'budgets', what: 'a policy file may shrink, never grow past its cap', fixture: 'fixtures/policy-rot/budgets.md' },
  { name: 'index', what: 'CLAUDE.md names every policy file, and every file it names exists', fixture: 'fixtures/policy-rot/index.md' },
  { name: 'duplicates', what: 'no 12-word run shared between two policy files', fixture: 'fixtures/policy-rot/dup-a.md' },
  { name: 'pr-body', what: 'a body carries its evidence sections, at the head CI ran', fixture: 'fixtures/policy-rot/prepr/' },
  { name: 'coverage', what: 'every file in a policy directory is matched by a glob', fixture: '(a probe file, see assertAcceptance)' },
]

function lintFile(rel, derived) {
  const text = read(rel)
  if (text == null) return [{ severity: 'error', check: 'citations', where: rel, message: 'unreadable' }]
  return [...checkCitations(rel, text), ...checkCounts(rel, text, derived), ...checkNoGh(rel, text)]
}

function lintFileGuarded(rel, derived) {
  try {
    return lintFile(rel, derived)
  } catch (e) {
    return [{ severity: 'error', check: '(driver)', where: rel, message: `linter threw: ${e.message}` }]
  }
}

function printFindings(findings) {
  const byFile = new Map()
  for (const f of findings) {
    const k = f.where.split(':')[0]
    if (!byFile.has(k)) byFile.set(k, [])
    byFile.get(k).push(f)
  }
  for (const [file, fs_] of [...byFile.entries()].sort()) {
    console.log(`\n${file}`)
    for (const f of fs_) console.log(`  ${f.severity.toUpperCase().padEnd(7)} [${f.check}] ${f.where}: ${f.message}`)
  }
}

// The acceptance. Each fixture states the errors its class must still produce;
// a class deleted in silence turns this red even on a clean tree.
// A count per CLASS is not enough, and the first version of this file proved it:
// `budgets: 2` was satisfied by two "no line cap recorded" errors alone, so the
// over-cap refusal -- the half that actually ratchets prose -- could be deleted
// with the acceptance still green. `citations: 3` was satisfied without any
// fixture citing an out-of-range line, so the whole path:line remediation was
// deletable too. Each entry may therefore also pin SUB-CLAIMS: a message
// substring that must appear at least once.
const REQUIRED_ROT = {
  citations: {
    count: 4,
    must: [
      'not in the tree',                 // a path that does not resolve
      'runs past',                       // path:line beyond the file's length
    ],
  },
  counts: { count: 2 },
  'no-gh': { count: 1 },
  duplicates: { count: 1 },
  budgets: {
    count: 2,
    must: [
      'no line cap recorded',            // an unclassified policy file
      'exceeds its cap',                 // the one-sided ratchet itself
    ],
  },
  'pr-body': {
    count: 6,
    must: [
      'section. Every one is content',   // a heading that is missing outright
      'is empty. Write the evidence',    // a heading with nothing under it
      'does not name',                   // the body's head is not the head CI ran
      'is not in the tree. A carry',     // a forward-carry destination that is gone
      'does not parse',                  // an unreadable friction line
      'is red and',                      // a red check the body never names
    ],
  },
  index: {
    count: 2,
    must: [
      'which is not in the tree',        // the index names a file that is gone
      'does not name',                   // a policy file the index omits
    ],
  },
}

CORPUS_CHECKS.push(checkIndex, checkDuplicates, checkBudgets, coverageOverTree)

function assertAcceptance(derived) {
  const dir = path.join(HERE, 'fixtures', 'policy-rot')
  if (!fs.existsSync(dir)) {
    console.log('\nFIXTURE VACUOUS: fixtures/policy-rot/ is missing; every check above is deletable in silence')
    return 1
  }
  const rels = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => path.relative(ROOT, path.join(dir, f)))
    .sort()
  let found = []
  for (const rel of rels) {
    const text = read(rel)
    found.push(...checkCitations(rel, text), ...checkCounts(rel, text, derived), ...checkNoGh(rel, text))
  }
  found.push(...checkDuplicates(rels))
  // budgets and index ran only over the real corpus, where a healthy tree
  // produces nothing -- so deleting either function looked identical to a
  // clean run. Both are pinned on fixtures instead: policy_budgets.json caps
  // fixtures/policy-rot/budgets.md at 1 line (over cap) while the other
  // fixtures have no cap at all (unclassified), and index.md names a file
  // that does not exist while omitting its neighbours.
  // pr-body: six rotten bodies under prepr/, and one healthy one that must stay
  // silent. Without the healthy fixture a check that refused EVERYTHING would
  // pin just as well as one that refuses the right things, which is the shape
  // this whole acceptance exists to rule out.
  const prepr = path.join(dir, 'prepr')
  if (!fs.existsSync(prepr)) {
    console.log('\nFIXTURE VACUOUS: fixtures/policy-rot/prepr/ is missing; the pr-body check is deletable in silence')
    return 1
  }
  const ZERO = '0000000000000000000000000000000000000000'
  for (const f of fs.readdirSync(prepr).filter((x) => x.endsWith('.md')).sort()) {
    const rel = path.relative(ROOT, path.join(prepr, f))
    const errs = checkPrBody(rel, { head: ZERO, red: f === 'unnamed-red.md' ? ['fast (3.14)'] : [] })
    if (f === 'good.md' && errs.length) {
      console.log(`\nFIXTURE VACUOUS: the pr-body null control ${rel} produced ${errs.length} error(s); it must produce none`)
      return 1
    }
    found.push(...errs)
  }

  // The template and the parser's required set drift apart the moment either is
  // edited alone, and the seat that pays is one following a template that no
  // longer satisfies the job. Linting the template as if it were a body ties
  // them together: a heading the parser requires and the template omits fails
  // here, on the pull request that removed it.
  const TEMPLATE = '.github/PULL_REQUEST_TEMPLATE.md'
  if (read(TEMPLATE) != null) {
    const errs = checkPrBody(TEMPLATE)
    if (errs.length) {
      console.log(`\nFIXTURE VACUOUS: ${TEMPLATE} does not satisfy the contract it exists to state`)
      found.push(...errs.map((e) => ({ ...e, check: '(template)' })))
    }
  }


  found.push(...checkBudgets(rels))
  const indexFixture = rels.find((r) => r.endsWith('/index.md'))
  if (!indexFixture) {
    console.log('\nFIXTURE VACUOUS: fixtures/policy-rot/index.md is missing, so the index check would fall back to the real CLAUDE.md and pin nothing')
    return 1
  }
  found.push(...checkIndex(rels.filter((r) => r !== indexFixture), indexFixture))
  const got = {}
  const msgs = {}
  for (const f of found) {
    got[f.check] = (got[f.check] || 0) + 1
    ;(msgs[f.check] ??= []).push(f.message)
  }
  let rc = 0
  let pins = 0

  // coverage: a probe rather than a committed fixture, because the check's whole
  // subject is a file the globs do not match -- committing one would make every
  // run report it.
  //
  // The probe used to write an UNTRACKED file, notice it was invisible to
  // `git ls-files`, and then test the POLICY_GLOBS regexes directly. That pinned
  // the patterns and not the check: deleting `checkCoverage` from the call site,
  // or emptying its return, left `--self-test` 11/11 and this line green. It was
  // the only entry in CHECKS with no class in REQUIRED_ROT, and `prepr.sh`'s own
  // standard -- a check that cannot be shown failing does not merge -- is what it
  // failed. Found by review, not by this harness.
  //
  // `checkCoverage` now takes an injectable file list, so the probe runs the real
  // function. BOTH directions, because one of them is what was missing: a file in
  // a policy directory that no glob matches must produce exactly one finding, and
  // an ordinary rule file must produce none.
  // The probe path must be genuinely uncovered. `zz-policy-lint-probe9.mdc` is
  // NOT: this commit widened `[a-z-]` to `[a-z0-9-]`, which is what makes the
  // digit case safe and the digit probe useless. A capital and an underscore
  // are outside the class in both directions, so this path stays uncovered
  // whichever way the glob is later widened for digits.
  const rotPath = '.cursor/rules/Probe_9.mdc'
  const okPath = '.cursor/rules/ci-autofix.mdc'
  pins += 1
  const wiredNames = CORPUS_CHECKS.map((f) => f.name || '(anonymous)').join(',')
  if (wiredNames !== CORPUS_CHECK_NAMES.join(',')) {
    console.log(`\nFIXTURE VACUOUS: CORPUS_CHECKS is wired as [${wiredNames}], expected [${CORPUS_CHECK_NAMES.join(',')}]. A check missing from the list never runs; one replaced by a no-op, a duplicate or an unwrapped \`checkCoverage\` runs and measures nothing. The count is derived from this list rather than carried, so adding a fifth check names it here once.`)
    return 1
  }
  // The harness below swaps `coverageFileSource`, so it cannot see that binding's
  // PRODUCTION default -- and that default is production code. `() => []` there
  // disables coverage completely and silently: `checkCoverage` coalesces on
  // `files ?? trackedFiles().list`, and an empty array is neither null nor
  // undefined, so the scan runs over nothing while every pin stays green. Pin
  // the default before swapping it. This is the line the review's attack J
  // named, and fixing a check by adding an untested line to production is the
  // shape it exists to refuse.
  pins += 1
  // The property is "coalesces away", not "is spelled null". `checkCoverage`
  // reads the tracked tree for anything `??` discards, so the test coalesces
  // against a sentinel rather than comparing to a literal. Asserting `!== null`
  // refused `() => {}` -- an arrow with an empty BLOCK body, the canonical
  // no-op idiom -- while its detection stayed correct: a false refusal on a
  // plausible edit, and the same substitution of spelling for property that the
  // friction parser made against backticked identifiers two rounds earlier.
  const TRACKED_TREE = Symbol('tracked-tree')
  if ((coverageFileSource() ?? TRACKED_TREE) !== TRACKED_TREE) {
    console.log(`\nFIXTURE VACUOUS: coverageFileSource's production default returned ${JSON.stringify(coverageFileSource())}, which \`??\` does not discard. Only a nullish default makes checkCoverage read the tracked tree; any other value is scanned instead, and an empty array scans nothing.`)
    return 1
  }

  // Driven through the WRAPPER, not through `checkCoverage` directly, so what
  // the wired function does is pinned and not merely what it is called.
  const drive = (files) => {
    const prev = coverageFileSource
    coverageFileSource = () => files
    try { return coverageOverTree() } finally { coverageFileSource = prev }
  }
  const covRot = drive([rotPath, okPath])
  const covOk = drive([okPath])
  pins += 2
  if (covRot.length !== 1 || covRot[0].where !== rotPath || covRot[0].check !== 'coverage') {
    console.log(`\nFIXTURE VACUOUS: checkCoverage did not report ${rotPath}; a rule file with a digit in its name would leave the corpus unread, in silence`)
    return 1
  }
  if (covOk.length) {
    console.log(`\nFIXTURE OVER-FIRES: checkCoverage reported ${covOk.length} finding(s) on a covered file, e.g. ${JSON.stringify(covOk[0].where)}`)
    return 1
  }

  for (const [cls, spec] of Object.entries(REQUIRED_ROT)) {
    const n = got[cls] || 0
    pins += 1 + (spec.must?.length ?? 0)
    if (n < spec.count) {
      console.log(`\nFIXTURE VACUOUS: check '${cls}' produced ${n} error(s) on the rot fixtures, ${spec.count} required`)
      rc = 1
    }
    for (const sub of spec.must ?? []) {
      if ((msgs[cls] ?? []).some((m) => m.includes(sub))) continue
      console.log(`\nFIXTURE VACUOUS: check '${cls}' produced no error saying ${JSON.stringify(sub)}; that sub-claim refuses nothing the fixtures can produce`)
      rc = 1
    }
  }
  // The rot fixtures cannot pin `rulePaths`, because a rule's `paths:` block
  // decides which fixtures exist rather than what they say. Pin it against the
  // real rules instead: the parsed list must have one entry per `- "..."` line
  // in the frontmatter. This is the check that would have caught the parser
  // dropping every list's LAST path -- and reading a single-path rule as
  // unscoped, so it was charged to every session's floor -- while still
  // printing a number for each role.
  for (const f of policyFiles().filter((x) => RULE_FILE.test(x))) {
    const raw = read(f)
    const fm = /^---\n([\s\S]*?)\n---/.exec(raw)
    if (!fm || !/^paths:/m.test(fm[1])) continue
    const want = (fm[1].match(/^[ \t]*-[ \t]*"/gm) || []).length
    const got = (rulePaths(f) || []).length
    if (got === want) continue
    console.log(`\nFIXTURE VACUOUS: rulePaths(${f}) parsed ${got} of ${want} declared path globs; a rule read as less scoped than it is lands in the always-loaded floor, and one read as more scoped is charged to no role at all`)
    rc = 1
  }
  if (!rc) console.log(`\nFIXTURE ok: ${found.length} error(s) hold ${pins} pins across ${Object.keys(REQUIRED_ROT).length} check classes on fixtures/policy-rot/`)
  return rc
}

function cmdRecord(findings) {
  const raw = read(KNOWN_BAD_FILE)
  const doc = raw ? JSON.parse(raw) : {}
  const before = new Map(
    (doc.entries ?? []).map((e) => (typeof e === 'string' ? [e, 1] : [e.key, e.count ?? 1]))
  )
  const counts = new Map()
  for (const f of findings) {
    if (NEVER_SUPPRESSED.has(f.check)) continue
    const k = keyOf(f)
    counts.set(k, (counts.get(k) ?? 0) + 1)
  }
  const after = [...counts.keys()].sort().map((key) => ({ key, count: counts.get(key) }))
  const added = after.filter((e) => !before.has(e.key))
  const dropped = [...before.keys()].filter((k) => !counts.has(k))
  const moved = after.filter((e) => before.has(e.key) && before.get(e.key) !== e.count)
  doc._comment =
    'Defects present when policy_lint landed, each with its recorded number of occurrences. A finding not listed here is an error; MORE occurrences of a listed one is an error; fewer is an error until re-recorded; an entry that no longer fires is an error. The list may only shrink. Regenerate with --record-known-bad; growing it is a deliberate edit a reviewer reads.'
  doc.recorded_at = git(['rev-parse', 'HEAD']).trim()
  doc.entries = after
  fs.writeFileSync(path.join(ROOT, KNOWN_BAD_FILE), JSON.stringify(doc, null, 2) + '\n')
  const total = [...counts.values()].reduce((a, b) => a + b, 0)
  console.log(`recorded ${after.length} entr(ies), ${total} occurrence(s), to ${KNOWN_BAD_FILE}: +${added.length} -${dropped.length} ~${moved.length}`)
  for (const e of added) console.log(`  + ${e.count}x ${e.key}`)
  for (const k of dropped) console.log(`  - ${k}`)
  for (const e of moved) console.log(`  ~ ${before.get(e.key)} -> ${e.count} ${e.key}`)
}

// ---------------------------------------------------------------------------
// pr-body. The evidence sections a pull request owes were honour-system, and on
// one day seven policy and gate pull requests merged with no independent verdict
// at their final head. Nothing at the merge boundary noticed, because the
// repository has no required check and no code-owner rule. This is the half of
// that gap a file in the repository can close: the body must SAY the things, in
// a shape a script reads, and CI re-executes the parts that are re-executable.
//
// It refuses an empty section rather than accepting silence, and accepts an
// explicit `n/a: <reason>` -- a reason a reviewer can disagree with beats a
// heading with nothing under it.

const REQUIRED_H2 = ['Head', 'Mutation proof', 'Null control', 'Red checks', 'Forward-carry', 'Friction']
const POLICY_H2 = ['Approval']
const FRICTION_EVENTS = ['unclear', 'contradiction', 'unenforced', 'stale', 'cost']
// A body writing `none` in backticks means the same thing as one writing none,
// and refusing the first would teach seats to write the second while meaning
// neither. Leading list markers and emphasis are stripped for the same reason.
const STRIP = "[-*\\s`_\"']*"
const isNone = (text) => new RegExp(`^${STRIP}(none|n/a)\\b`, 'i').test(text)
// `n/a` and `none` are not the same answer. `none` IS the content -- there were
// no red checks, nothing was carried. `n/a` says the section does not apply to
// this change, which is a judgement, and the whole point of the section is that
// a reviewer can disagree with it. A bare `n/a` gives them nothing to disagree
// with: six of them plus the right SHA satisfied the entire contract, exit 0.
const isBareNa = (text) => {
  const t = text.trim()
  if (!new RegExp(`^${STRIP}n/a\\b`, 'i').test(t)) return false
  const after = t.replace(new RegExp(`^${STRIP}n/a\\b`, 'i'), '').replace(/^[:\-\s]+/, '')
  return after.length < 3
}

function sections(body) {
  const out = new Map()
  let cur = null
  let inFence = false
  for (const line of body.split('\n')) {
    if (CODEFENCE.test(line)) inFence = !inFence
    const m = inFence ? null : /^##\s+(.+?)\s*$/.exec(line)
    if (m) {
      cur = m[1]
      out.set(cur, [])
      continue
    }
    if (cur) out.get(cur).push(line)
  }
  for (const [k, v] of out) out.set(k, v.join('\n').trim())
  return out
}

function checkPrBody(bodyPath, { head = '', title = '', red = [] } = {}) {
  const out = []
  let body
  try {
    body = fs.readFileSync(bodyPath, 'utf8')
  } catch {
    return [{ severity: 'error', check: 'pr-body', where: bodyPath, message: 'unreadable' }]
  }
  const secs = sections(body)
  const isPolicy = /^policy:/.test(title.trim())
  const want = [...REQUIRED_H2, ...(isPolicy ? POLICY_H2 : [])]

  for (const h of want) {
    if (!secs.has(h)) {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: `no \`## ${h}\` section. Every one is content or an explicit "n/a: <reason>"; a missing heading is neither.` })
      continue
    }
    if (!secs.get(h)) {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: `\`## ${h}\` is empty. Write the evidence, or "n/a: <reason>" a reviewer can disagree with.` })
      continue
    }
    if (isBareNa(secs.get(h))) {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: `\`## ${h}\` is a bare "n/a". Say why it does not apply: "n/a: <reason>". \`none\` is an answer; \`n/a\` alone is a heading with the work left out.` })
    }
  }

  // The head the body claims must be the head CI is running. A body describing
  // an older head is the shape fix-review.md calls `head-moved`.
  const headSec = secs.get('Head') ?? ''
  if (head && headSec && !headSec.includes(head) && !headSec.includes(head.slice(0, 7))) {
    out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
      message: `\`## Head\` does not name ${head.slice(0, 7)}, which is the head this ran on. Evidence measured at another head describes another tree.` })
  }

  // A carry destination that does not exist is a carry nobody receives, which is
  // the failure .cursor/rules/finding-propagation.mdc was written for.
  const carry = (secs.get('Forward-carry') ?? '').trim()
  if (carry && !isNone(carry)) {
    const toks = new Set()
    for (const re of [PATH_TOKEN_RE, MDC_PATH_RE]) {
      re.lastIndex = 0
      let m
      while ((m = re.exec(carry))) toks.add(m[0])
    }
    if (!toks.size) {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: '`## Forward-carry` names no destination file. Write `none`, or the path of the brief, contract or roster the finding lands in.' })
    }
    for (const tok of toks) {
      if (resolvePathToken(tok)) continue
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: `\`## Forward-carry\` names \`${tok}\`, which is not in the tree. A carry to a file that does not exist is not a carry.` })
    }
  }

  // Friction is the input to the policy-evolution loop. An unparseable line is a
  // signal nobody can count, so the histogram would silently under-report.
  const friction = (secs.get('Friction') ?? '').trim()
  if (friction && !isNone(friction)) {
    // An entry may WRAP. This corpus wraps its prose at eighty columns, so any
    // evidence sentence longer than a few words spans two lines -- and treating
    // each physical line as its own entry refused the continuation, which is
    // the second false refusal this parser produced on the first well-formed
    // body it ever saw. A line that starts a new `id: event:` opens an entry;
    // anything else continues the one above it. The first non-empty line must
    // still open an entry, so a block of free prose is refused exactly as before.
    const entryStart = /^[-*]?\s*`?[A-Za-z][A-Za-z0-9_.-]*`?\s*:\s*`?[a-z-]+`?\s*:/
    const entries = []
    for (const raw of friction.split('\n').map((l) => l.trim()).filter(Boolean)) {
      // A continuation is prose. A line shaped like `word: word:` is TRYING to
      // be an entry and failing -- `index: Cost:` (capitalised) and
      // `index: unenforced but no second colon` both folded silently into the
      // entry above, so a malformed second entry cost nothing and the histogram
      // under-reported exactly as an unparseable first entry would. Fold real
      // prose; refuse a near-miss.
      const nearMiss = /^[-*]?\s*`?[A-Za-z][A-Za-z0-9_.-]*`?\s*:/.test(raw)
      if (entryStart.test(raw) || !entries.length) entries.push(raw)
      else if (nearMiss) entries.push(raw)
      else entries[entries.length - 1] += ' ' + raw
    }
    for (const line of entries) {
      // Backticks around the id and the event are tolerated because every other
      // policy file in this repository writes an identifier that way, so a seat
      // reaching for `## Friction` writes `budgets`, not budgets. The first real
      // body this check ever saw was refused for exactly that, and the refusal
      // was the check's, not the body's: no fixture exercised a WELL-FORMED
      // friction line, so the accept path had never run. Tolerating the marks
      // removes a false refusal and no true one -- the event must still be in
      // the closed vocabulary below, which is the half that carries meaning.
      const m = /^[-*]?\s*`?([A-Za-z][A-Za-z0-9_.-]*)`?\s*:\s*`?([a-z-]+)`?\s*:\s*(.+)$/.exec(line)
      if (!m || !FRICTION_EVENTS.includes(m[2])) {
        out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
          message: `\`## Friction\` line does not parse: ${JSON.stringify(line.slice(0, 50))}. Write \`none\`, or \`<rule_id>: <${FRICTION_EVENTS.join('|')}>: <evidence>\`.` })
      }
    }
  }

  // A red check the body does not name is a red check nobody answered. The
  // ANALYSIS stays honour -- a script cannot judge whether an answer is good --
  // but naming it is mechanical, and naming it is what gets skipped.
  const redSec = (secs.get('Red checks') ?? '').trim()
  for (const name of red) {
    if (redSec.includes(name)) continue
    out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
      message: `check \`${name}\` is red and \`## Red checks\` does not name it. Name the failure and answer it: the cheaper detector and its standing cost, or the finding that none exists.` })
  }

  return out
}

function cmdPrBody(args) {
  const val = (flag) => {
    const i = args.indexOf(flag)
    return i >= 0 ? args[i + 1] : null
  }
  const bodyPath = val('--pr-body')
  const red = (val('--red') ?? '').split(',').map((x) => x.trim()).filter(Boolean)
  const findings = checkPrBody(bodyPath, { head: val('--head') ?? '', title: val('--title') ?? '', red })
  printFindings(findings)
  console.log(`\nPR-BODY: ${findings.length} error(s) in ${bodyPath}`)
  return findings.length ? 1 : 0
}

function cmdList() {
  console.log('policy_lint checks:\n')
  for (const c of CHECKS) console.log(`  ${c.name.padEnd(12)} ${c.what}\n${' '.repeat(16)}fixture: ${c.fixture}`)
}

function cmdBudgets(files) {
  const b = policyBudgets()
  const rows = sizes(files)
  console.log('file'.padEnd(46), 'lines', 'cap', ' ~tokens', 'always')
  let alwaysTokens = 0
  for (const r of rows.sort((a, c) => c.lines - a.lines)) {
    const cap = b && b.files[r.file] != null ? String(b.files[r.file]) : '-'
    if (r.always) alwaysTokens += Math.round(r.bytes / 4)
    console.log(r.file.padEnd(46), String(r.lines).padStart(5), cap.padStart(4), String(Math.round(r.bytes / 4)).padStart(8), r.always ? '  yes' : '')
  }
  console.log(`\nalways-loaded: ~${alwaysTokens} tokens, cap ${b ? b.always_loaded_tokens : '-'}`)
  // The floor alone reads as the corpus cost; printing the three together is
  // what stops a re-record of one being mistaken for an improvement in all.
  const corpusTokens = rows.reduce((n, r) => n + Math.round(r.bytes / 4), 0)
  console.log(`corpus:        ~${corpusTokens} tokens, cap ${b ? b.corpus_tokens : '-'}`)
  for (const [role, spec] of Object.entries((b && b.roles) || {})) {
    console.log(`role ${role.padEnd(9)} ~${roleTokens(rows, spec.opens)} tokens, cap ${spec.cap}`)
  }
}

function main() {
  const args = process.argv.slice(2)
  const derived = derivations()

  if (args[0] === '--list') return cmdList(), process.exit(0)

  const all = policyFiles()
  const files = args.filter((a) => !a.startsWith('--')).length
    ? args.filter((a) => !a.startsWith('--')).map((a) => path.relative(ROOT, path.resolve(a)))
    : all
  const defaultRun = !args.filter((a) => !a.startsWith('--')).length

  if (args.includes('--budgets')) return cmdBudgets(files), process.exit(0)
  if (args.includes('--pr-body')) process.exit(cmdPrBody(args))

  let findings = []
  for (const f of files) findings.push(...lintFileGuarded(f, derived))
  if (defaultRun) {
    for (const fn of CORPUS_CHECKS) findings.push(...fn(all))
  }

  if (args.includes('--record-known-bad')) return cmdRecord(findings), process.exit(0)

  let suppressed = 0
  let occurrences = 0
  let known = 0
  if (defaultRun) {
    const applied = applyKnownBad(findings)
    findings = applied.live
    suppressed = applied.suppressed
    occurrences = applied.occurrences
    known = applied.total
  }
  printFindings(findings)
  const errors = findings.filter((f) => f.severity === 'error').length
  if (defaultRun) console.log(`\nKNOWN-BAD: ${suppressed} of ${known} recorded defect(s) still present, in ${occurrences} recorded occurrence(s)`)
  console.log(`\nTOTAL: ${errors} error(s) across ${files.length} policy file(s)`)
  if (args.includes('--report')) {
    const by = {}
    for (const f of findings) by[f.check] = (by[f.check] || 0) + 1
    console.log('\nby check:', JSON.stringify(by))
    console.log('derivations:', JSON.stringify(derived))
  }
  const rc = defaultRun ? assertAcceptance(derived) : 0
  process.exit(errors > 0 || rc ? 1 : 0)
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
