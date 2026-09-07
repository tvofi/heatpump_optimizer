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
let _policySpec = null
function symbolElsewhere(symbol, exceptRel) {
  if (!_policySpec) _policySpec = policyFiles().map((f) => `:!${f}`)
  const spec = _policySpec.includes(`:!${exceptRel}`) ? _policySpec : [..._policySpec, `:!${exceptRel}`]
  const out = git(
    ['grep', '-I', '-l', '-w', '-F', symbol, '--', '.', ':!.claude', ':!tools/audit/round2', ...spec],
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
  /^\.cursor\/rules\/[a-z-]+\.mdc$/,
  /^\.claude\/rules\/[a-z0-9-]+\.md$/,
  /^tools\/audit\/briefs\/[A-Za-z0-9_.-]+\.md$/,
  /^tools\/audit\/README\.md$/,
  /^tests\/README\.md$/,
  /^docs\/HANDOVER\.md$/,
  /^\.claude\/workflows\/web-fragments\.md$/,
]

// Always loaded by a tool, so their size is charged to every session.
const ALWAYS_LOADED = /^(CLAUDE\.md|\.claude\/rules\/[a-z0-9-]+\.md)$/

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

function sizes(files) {
  const rows = []
  for (const f of files) {
    const raw = read(f)
    if (raw == null) continue
    rows.push({ file: f, lines: raw.split('\n').length, bytes: Buffer.byteLength(raw), always: ALWAYS_LOADED.test(f) })
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
  return out
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
    while ((m = re.exec(text))) named.add(m[0])
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
  for (const f of findings) {
    const k = keyOf(f)
    if (!live.has(k)) live.set(k, [])
    live.get(k).push(f)
  }

  const out = []
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
  index: {
    count: 2,
    must: [
      'which is not in the tree',        // the index names a file that is gone
      'does not name',                   // a policy file the index omits
    ],
  },
}

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

  let findings = []
  for (const f of files) findings.push(...lintFileGuarded(f, derived))
  if (defaultRun) {
    findings.push(...checkIndex(all), ...checkDuplicates(all), ...checkBudgets(all))
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
