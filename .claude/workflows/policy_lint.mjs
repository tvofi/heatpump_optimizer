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
// Six check classes over the corpus as it stands, each cheap and offline:
//   citations   paths, path:line and named symbols in policy prose resolve
//   counts      a literal count in policy prose matches its derivation
//   no-gh       no `gh <verb>` outside the MCP mapping table
//   budgets     one-sided size caps: a policy file may shrink, never grow
//   index       CLAUDE.md names every policy file, and every file it names exists
//   duplicates  no 12-word run shared between two policy files
//
// ...and three that measure the LOOP around it -- whether the process that
// maintains the corpus is still running. These read merged history, so none of
// them runs on a pull request (see the `record` job in governance.yml):
//   record      every merged pull request has a disposition somewhere  (refuses)
//   stats       verdict and friction histograms, and what they would open
//   sunset      rules that have outlived the reason they were written
//
// Every class is otherwise deletable in silence, so the no-arg (CI) path also
// runs an acceptance over fixtures/policy-rot/ and fixtures/policy-loop/, which
// states the errors each class must still produce and the healthy input each
// must stay silent on. A run that finds nothing and a gutted linter look
// identical without it.
//
//   node .claude/workflows/policy_lint.mjs            # lint + acceptance (CI)
//   node .claude/workflows/policy_lint.mjs --list     # every check + fixture
//   node .claude/workflows/policy_lint.mjs --budgets  # sizes vs caps
//   node .claude/workflows/policy_lint.mjs --hooks [settings.json]  # wired and self-testing
//   node .claude/workflows/policy_lint.mjs --report   # enforcement summary
//   node .claude/workflows/policy_lint.mjs <files...> # lint just these
//   node .claude/workflows/policy_lint.mjs --record-known-bad   # reseed the ratchet
//   node .claude/workflows/policy_lint.mjs --pr-body <file> --head <sha> [--title t] [--red names]
//   node .claude/workflows/policy_lint.mjs --record --since <ref>   # dispositions
//   node .claude/workflows/policy_lint.mjs --stats  --since <ref>   # histograms
//   node .claude/workflows/policy_lint.mjs --sunset --since <ref>   # dead rules
//
// `--record` and `--record-known-bad` are two different things and the names sit
// one hyphen apart: the first REFUSES a merge with no disposition, the second
// reseeds the known-bad ledger. Argument matching below is exact-string, never
// prefix, so neither can be reached by mistyping the other.

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

function git(args, { allowFail = false, env } = {}) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, ...(env ? { env } : {}) })
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
  // The live instruments' own README, which `tools/audit/README.md` names. It
  // arrived with the archive pass and the widened basename resolution reported
  // it immediately: a seat-facing document outside every cap is the corpus
  // escape this check exists for, whether or not anyone meant it as one.
  /^tools\/audit\/harnesses\/README\.md$/,
  /^tests\/README\.md$/,
  /^docs\/HANDOVER\.md$/,
  /^\.claude\/workflows\/web-fragments\.md$/,
  // A skill is seat-facing text loaded by the harness at the moment a pull
  // request event arrives, which makes it policy with an unusually short path
  // to acting on it. It is linted like the rest.
  /^\.claude\/skills\/[a-z0-9-]+\/SKILL\.md$/,
  // The template states the contract `checkPrBody` enforces, so a seat follows
  // it and CI grades against it. It was given a cap while it was outside this
  // list, which compared it against nothing: measured at 539 lines with the cap
  // recorded at 38, the run was still `TOTAL: 0`. A cap on an unmeasured file
  // is the whole escape `checkOrphanCaps` now refuses, and the fix for THIS
  // file is to measure it rather than to drop its cap.
  /^\.github\/PULL_REQUEST_TEMPLATE\.md$/,
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
const CORPUS_CHECK_NAMES = ['checkIndex', 'checkDuplicates', 'checkBudgets', 'coverageOverTree', 'namedDocsOverTree', 'orphanCapsOverTree', 'checkProvenance']

// WHAT THIS PIN DOES NOT COVER, stated rather than implied. It compares the
// wired list against the names above, so it catches a registered check that is
// mis-wired -- removed, duplicated, replaced by a no-op or by an unwrapped
// call. It CANNOT catch a check function that was never registered at all:
// adding `checkNamedDocs` and forgetting both lists left every pin green, which
// is how this comment came to exist. Detecting that needs a registry the
// checks declare themselves into, and until one exists this is the floor.
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

// Deliberately outside the corpus, each for a stated reason. CLAUDE.md's own
// scope rule -- "it does not govern README.md or the rest of docs/" -- puts the
// first two beyond it; the last two are programme records a seat reads as data
// rather than as policy. Adding to this list is a visible edit in the diff a
// reviewer reads, which is the same bar as raising a cap.
const CORPUS_EXCLUDED = new Set([
  'README.md',                        // user-facing
  'RELEASE_NOTES.md',                 // user-facing
  'docs/audit-2026-09.md',            // evidence register
  'docs/plan-2026-09-open-issues.md', // plan of record
  'DISCLAIMER.md',                    // user-facing, same ground as README.md
  'docs/backlog.md',                  // superseded record, kept for history
  // The architecture decision records. An ADR states a decision ALREADY TAKEN
  // and the measurement behind it; it binds no seat and no seat is sent to one
  // to learn what it must do. The corpus machinery is built for text that binds
  // someone: `checkIndex` refuses a policy file `CLAUDE.md` does not name,
  // because "the index is the only way a seat finds a policy file" -- and
  // naming them all here would push the ALWAYS-LOADED set, the one number this
  // audit exists to drive down, past its cap to carry documents nobody must
  // read. Measured before choosing, and RE-MEASURED here because the first
  // reading was taken against five decisions and this list now names six:
  // bringing `docs/decisions/` under POLICY_GLOBS reports 24 errors across 41
  // policy files -- 7 [budgets], 6 [index], 6 [duplicates], 5 [citations] --
  // where the first reading said 14. The shape is what decided it and the shape
  // is unchanged: every ADR wants a cap and an index line it should not have.
  // The five [citations] are named one by one rather than summarised, because
  // the first version of this sentence said they were all 0003's and three of
  // them are: `docs/Zednotes.md`, `NOT_A_DOCUMENT` and `NEVER_NOT_A_DOCUMENT`,
  // correct BECAUSE 0003 describes an experiment over files and symbols that do
  // not exist. The fourth is 0005 citing `docs/plan-2026-09-governance-audit.md`
  // and is a TRUE positive: that plan is archived on a branch and is not in this
  // tree. The fifth is 0006 citing `POLICY_GLOBS`, which exists a few lines
  // above here -- unresolvable because `SYMBOL_GREP_EXCLUDE` is [':!.claude'],
  // excluding this whole directory on purpose so that a roster cannot satisfy
  // its own citation. So three of the five are a check applied to the wrong kind
  // of text, one is the check working, and one is a known exclusion meeting a
  // document that cites into it. The count grows with the directory, which is
  // the other half of the argument: measuring ADRs makes the corpus pay per
  // decision.
  //
  // THE RESIDUAL RISK, stated rather than left to be found: prose moved from a
  // capped file into an ADR leaves the corpus and buys headroom in every cap at
  // once, and nothing detects it. Only a reviewer reading the diff does. These
  // are named ONE BY ONE and not by prefix, deliberately -- a `.md` is never
  // excused by location here, so the NEXT ADR costs a line in this list, which
  // is the same bar as raising a cap and is the point. It has already been paid
  // once: this comment said "a sixth" while it was written against five, and
  // 0006 landed on `main` before the branch did. A count in a comment goes
  // stale on the next merge; the list is the count.
  'docs/decisions/0001-session-policy-merge-grant.md',
  'docs/decisions/0002-self-witnessed-proxy-assertion.md',
  'docs/decisions/0003-enumerate-what-you-may-ignore.md',
  'docs/decisions/0004-an-assertion-can-be-correct-and-never-run.md',
  'docs/decisions/0005-no-codeowners-while-one-identity-authors-and-approves.md',
  'docs/decisions/0006-policy-merge-grant-regranted-to-the-local-session.md',
])

// Widening the scan past `.md` brought in every `.txt` a policy file cites, and
// in this tree every one of them is DATA rather than a document: the two claim
// files, `tests/requirements-ci.txt`, and the round-2 and wave-5 evidence dumps.
// A directory rule rather than seven more names, because the property is where
// the repository keeps data, and a name list would go stale on the next fixture.
//
// MARKDOWN IS NEVER EXCUSED BY LOCATION. The first version of this list applied
// to every extension, and that REOPENED the escape it was written beside: the
// #615 round-two review moved ten lines of CLAUDE.md plus 4756 bytes of new
// prose into `tests/POLICY-NOTES.md`, named it from CLAUDE.md, and measured
// `rc=0` with 138 tokens freed in each of the five caps and a two-file diff.
// The prefixes exist for `.txt` and its neighbours, which this repository keeps
// under `tests/` and the evidence directories as data; a `.md` is a document
// wherever it sits, so it is never excused here. Measured cost of the narrowing:
// none -- the healthy tree stays at TOTAL 0 with every fixture pin intact.
const CORPUS_EXCLUDED_PREFIX = [
  'tests/',                            // suite data: fixtures, claim files, requirements
  'tools/audit/w5-g5-195-coverage/',   // wave-5 evidence, kept until that wave closes
]

// A SECOND, DIFFERENT KIND OF EXCLUSION, and it must not be folded into the
// first. CORPUS_EXCLUDED_PREFIX says "this directory holds data, so a
// location-dependent extension is data here" -- and round three established
// that a DOCUMENT is never excused by location, so that list deliberately does
// not apply to one. Generated output is the other case: `.cursor/rules/*.mdc`
// is produced from `.claude/rules/` by rules_sync.mjs and byte-compared by
// `--check`, so it cannot carry a word its source does not have, and its source
// IS measured. Excluding it is not a hole; measuring it would double-count the
// corpus. This applies whatever the extension, which is exactly why it is
// separate -- writing `.cursor/rules/` into the list above would have silently
// re-excused a document by location.
const GENERATED_PREFIX = ['.cursor/rules/']

// AN ALLOWLIST OF DOCUMENT EXTENSIONS CANNOT BE COMPLETE, and three review
// rounds proved it one extension at a time: `.MD` and `.txt`, then `.rst`, then
// `.mdx/.adoc/.org/.text/.mdown/.mkd/.rest/.asciidoc`, then `.mdc` -- which is
// NINE real files in this tree. Each round closed the named ones and shipped a
// body claiming the rest were covered. The list that must be complete is
// therefore the other one.
//
// INVERTED. Any tracked path a policy file names is a document unless its
// extension says otherwise. `NOT_A_DOCUMENT` is bounded by what this repository
// actually contains -- `git ls-files | sed 's/.*\.//' | sort -u` -- so it is
// checkable, and an extension nobody thought of now defaults to REPORTED rather
// than to silent. The acceptance drives that default with an invented extension.
//
// Measured on the healthy tree: the inverted form reports 14 paths, TEN already
// in CORPUS_EXCLUDED or under CORPUS_EXCLUDED_PREFIX, and the other four are
// `.cursor/rules/*.mdc` -- generated by rules_sync.mjs and byte-compared by
// `--check`, so they cannot carry prose their source does not have. One prefix
// entry below, and the whole inversion costs nothing.
const NOT_A_DOCUMENT = new Set([
  'donotdelete',
  'gitattributes',
  'gitignore',
  'js',
  'json',
  'log',
  'mjs',
  'png',
  'py',
  'sh',
  'svg',
  'tsv',
  'yaml',
  'yml',
])

// THE BLOCKLIST NEEDS A FLOOR AS WELL AS A CEILING. `deadWeight` in the
// acceptance bounds NOT_A_DOCUMENT from ABOVE -- no entry the tree does not
// have -- and the round-six review measured what that leaves open: adding
// `txt`, or `mdc`, to the set above reopened rounds three and five at rc=0 with
// all 45 pins green, because an extension the tree DOES have passes the only
// assertion guarding the list. So the extensions this branch has already
// established are documents are named once, and the acceptance refuses their
// appearance in the blocklist.
//
// THIS LIST DOES NOT HAVE TO BE COMPLETE, which is the whole reason it is not
// the allowlist rounds one to five kept failing to finish one extension at a
// time. An extension in NEITHER list still defaults to DOCUMENT -- the
// inversion is untouched. This floor only refuses writing a KNOWN document
// extension into the blocklist, so it can never be the thing that has to be
// exhaustive. Its members are exactly the extensions the earlier rounds closed:
// `.MD` and `.txt`, then `.rst`, then the eight-format widening, then `.mdc`.
const NEVER_NOT_A_DOCUMENT = [
  'md', 'mdc', 'markdown', 'mdown', 'mkd', 'txt', 'text',
  'rst', 'rest', 'mdx', 'adoc', 'asciidoc', 'org',
]

const PATH_RE = /[A-Za-z0-9_./-]+\.[A-Za-z0-9]+\b/g

// A DESTINATION WITH NO EXTENSION. Round four and round five both stated this as
// a limit and I twice guessed its cost wrong -- "every backticked word in the
// corpus" was the guess; the measurement is ONE. The tree has exactly three
// extensionless tracked files, and the corpus cites exactly one of them:
//
//   extensionless tracked files          LICENSE, NOTICE, VERSION
//   cited by a policy file               VERSION, from brief-citations.md
//
// So the route closes for three names, bounded by the tree the same way
// NOT_A_DOCUMENT is, and the same dead-weight assertion covers both. A bare word
// only reaches this at all if it IS a tracked file, so ordinary prose cannot
// trip it: `docs` and `tests` are directories and fail the tracked lookup.
const BARE_RE = /(?<![A-Za-z0-9_./-])[A-Za-z0-9_/-]{2,}(?![A-Za-z0-9_./-])/g
const NOT_A_DOCUMENT_NAME = new Set(['LICENSE', 'NOTICE', 'VERSION'])

// A `.txt` in THIS tree is data -- the two claim files, `requirements-ci`, the
// round-2 and wave-5 dumps -- while `.txt` is a document format elsewhere. That
// is the one extension whose answer depends on WHERE it sits, which is why the
// exclusion is a directory prefix rather than another extension list, and why
// `.txt` is the only extension this predicate treats as location-dependent.
const ALWAYS_A_DOCUMENT = /\.(?!txt$)[A-Za-z0-9]+$/i

const corpusExcluded = (rel) =>
  CORPUS_EXCLUDED.has(rel) ||
  GENERATED_PREFIX.some((p) => rel.startsWith(p)) ||
  (!ALWAYS_A_DOCUMENT.test(rel) && CORPUS_EXCLUDED_PREFIX.some((p) => rel.startsWith(p)))

// THE ESCAPE THIS CLOSES. `corpus_tokens` sums the CAPPED files, so prose moved
// into a file that has no cap leaves the corpus and buys headroom in every cap
// at once -- measured: 40 lines of CLAUDE.md into a new `docs/POLICY-NOTES.md`
// freed 644 tokens across all four with zero deletion, and `coverage` misses it
// because `docs/` is not a policy directory. `.claude/rules/ratchet-budgets.md`
// asserts "only a deletion lowers it", and without this that sentence is false.
//
// The move has to stay REACHABLE to be worth making, so the corpus must name
// its destination. Any `.md` the corpus names, that is tracked and has no cap
// and is not excluded above, is that hole.
// Extracted so the acceptance can drive the SCAN, which is the half that had no
// witness: reverting `path.posix.normalize` here left every pin green while
// `./docs/NOTES.md` went unreported. `matchAll` builds its own regex from this
// one, so the shared `g` flag carries no `lastIndex` between calls -- driven in
// the acceptance rather than trusted, because a stateful global regex would
// silently skip every file after the first.
function namedDocMatches(text) {
  return [...text.matchAll(PATH_RE)]
    .map((m) => path.posix.normalize(m[0]))
    .filter((rel) => !NOT_A_DOCUMENT.has(rel.split('.').pop().toLowerCase()))
}

// The bare pass is a SEPARATE function with a separate contract, and keeping
// them apart is not tidiness. `namedDocMatches` returns candidates that are
// documents by extension, and the acceptance drives it with synthetic paths that
// are not tracked -- so it cannot filter on the tree. A bare token cannot be
// judged that way: every word in every policy file matches, and only
// `tracked.has` in the caller separates `VERSION` from `and`. Folding the two
// made `namedDocMatches` return ["see", "and", "and"], which its own over-fire
// assertion refused -- the assertion doing exactly what it was written for.
// CASE-FOLDED, and it has to be, because `resolveCited` folds. With the filter
// case-sensitive and the resolution not, the ordinary English words " version "
// and " notice' " in `brief-citations.md` prose resolved to the tracked files
// `VERSION` and `NOTICE` and were reported as uncapped documents -- two findings
// on a healthy tree, caught by the null control in the run that introduced them.
// The three files are data whatever case a sentence spells them in.
const notADocumentName = (n) => NOT_A_DOCUMENT_NAME.has(n.split('/').pop().toUpperCase())

function bareNameCandidates(text) {
  return [...text.matchAll(BARE_RE)].map((m) => m[0]).filter((n) => !notADocumentName(n))
}

// A CITATION BY BASENAME IS A CITATION, and reading it as anything else was the
// last way out of the corpus. `tracked.has` compares WHOLE PATHS, so
// `POLICY-NOTES.md` -- prose moved into `docs/POLICY-NOTES.md` and cited the way
// `CLAUDE.md` cites all thirty documents it indexes, the way this branch's own
// `brief-citations.md` calls a resolvable citation -- matched no tracked path
// and was dropped BEFORE any exclusion ran. Measured by the round-six review:
// the same prose reported rc=0 cited as `POLICY-NOTES.md` and rc=1 cited as
// `docs/POLICY-NOTES.md`, with 77 tokens leaving each of the five caps in
// silence. The extension axis was closed while this one stood open.
//
// CASE-INSENSITIVELY, for the same reason round four put `/i` on the extension
// test and round seven's review measured the half that was left: `namedDocMatches`
// lowercases an extension before judging it, so `POLICY-NOTES.MD` survives the
// scan -- and then resolved case-SENSITIVELY against `git ls-files` it matched
// nothing and was dropped. Measured: `docs/POLICY-NOTES.md` cited as
// `POLICY-NOTES.md` reported rc=1 and the same file cited as `POLICY-NOTES.MD`
// reported rc=0 with TOTAL 0. Folding decides which files COLLIDE; what a
// collision then resolves to is `resolveCited`'s business, and it resolves to
// all of them.
function lowerBaseMap(listing) {
  if (!listing._byBaseLower) {
    const m = new Map()
    for (const f of listing.set) {
      const b = path.posix.basename(f).toLowerCase()
      if (!m.has(b)) m.set(b, [])
      m.get(b).push(f)
    }
    listing._byBaseLower = m
  }
  return listing._byBaseLower
}

// AN AMBIGUOUS BASENAME RESOLVES TO ALL OF THEM, NOT TO NOTHING, and resolving
// it to nothing was a ONE-FILE escape rather than the two-file one the #615 body
// claimed. The second file never had to be planted: it is the policy file
// itself. Measured on that branch's head -- a new tracked `docs/X.md`, cited
// from `CLAUDE.md` by basename:
//
//   docs/COMMON.md        cited as `COMMON.md`        0 findings   ESCAPED
//   docs/fixer.md         cited as `fixer.md`         0            ESCAPED
//   docs/gate-scoping.md  cited as `gate-scoping.md`  0            ESCAPED
//   docs/Zednotes.md      cited as `Zednotes.md`      1            reported
//
// Any destination named after a capped policy file left every cap in silence.
//
// WHY IT COSTS NOTHING HERE AND NOT BEFORE. Driven this way on the base tree it
// reported seventeen extra findings, all `tools/audit/round2/**`: sixteen
// through the generic names `REPORT.md` and `BASELINE.md`, and a seventeenth --
// `round2/JUDGE.md` -- through `judge.md` and the case fold. Both counts are
// measured on `e4a388a`, the tree whose body wrote sixteen: an EXACT-CASE
// resolve-to-all reports 16 there, the FOLDED one 17, and the one finding
// between them is `round2/JUDGE.md`. So sixteen is the count from before the
// fold -- which `e4a388a` itself carries -- and not a number #616 moved. Those
// were never false positives -- they were frozen evidence documents that
// genuinely had no cap and no exclusion, and the honest fix was to classify
// them, which this commit does by deleting the tree. So the check is widened in
// the same change that removes its cost, and the caller's own filter does the
// rest: a candidate that is capped AND measured, or excluded, is dropped, so an
// ambiguous basename reports only the destination that is neither.
// ONE LOOKUP, NOT TWO. #616 gave the exact-case map precedence so a UNIQUE
// exact match would win over a folded collision; resolving an ambiguous
// basename to ALL of its candidates makes that precedence dead, because the
// folded map is a superset of the exact one and the caller filters both the
// same way. Driven: with the exact branch emptied, every pin stayed green and
// the tree stayed at TOTAL 0 -- a branch with no witness left, which inside a
// check reads exactly like a property. Removed rather than pinned.
function resolveCited(token, listing) {
  if (listing.set.has(token)) return [token]
  return lowerBaseMap(listing).get(path.posix.basename(token).toLowerCase()) || []
}

// The SCAN AND ITS RESOLUTION, extracted so the acceptance can drive them with
// a SYNTHETIC listing. That seam is not tidiness either: with the resolution
// inlined in `unmeasuredNamedDocs`, the bare pass could be deleted at its call
// site with every pin still green, because the three extensionless tracked
// files are exactly `VERSION`, `LICENSE` and `NOTICE` and all three are data --
// so the bare route has NO true positive on a healthy tree and therefore no
// witness there. A synthetic listing supplies the one the tree cannot.
function citedTrackedPaths(text, listing) {
  const l = listing || trackedFiles()
  const out = []
  for (const m of [...namedDocMatches(text), ...bareNameCandidates(text)]) {
    for (const rel of resolveCited(m, l)) if (!out.includes(rel)) out.push(rel)
  }
  return out
}

function unmeasuredNamedDocs(budget) {
  const b = budget !== undefined ? budget : policyBudgets()
  if (!b) return []
  const capped = new Set(Object.keys(b.files || {}))
  // A cap is not enough, and reading it as enough was the escape: a cap on a
  // file outside POLICY_GLOBS is compared against nothing. Both, so the budget
  // still drives the check -- which is where its witness comes from -- while a
  // capped-but-unmeasured destination stays a finding.
  const measured = new Set(policyFiles())
  const listing = trackedFiles()
  const out = new Map()
  for (const src of policyFiles()) {
    const raw = read(src)
    if (raw == null) continue
    // Case-insensitive, and past `.md`. The scan saw only lowercase `.md`, so
    // `docs/NOTES.MD` and `docs/NOTES.txt` each carried the same prose out of
    // the corpus in silence -- measured by the #615 review at about 1189
    // tokens through either. Prose extensions only: a destination that is not
    // a document is not this check's subject, and widening it to every
    // tracked extension would report data files a brief legitimately cites.
    // `namedDocMatches` normalised its matches and `resolveCited` resolves them
    // against `git ls-files`, which is normalised too -- a RAW `./docs/NOTES.md`
    // failed the tracked lookup and went unreported everywhere.
    for (const rel of citedTrackedPaths(raw, listing)) {
      if ((capped.has(rel) && measured.has(rel)) || corpusExcluded(rel)) continue
      if (!out.has(rel)) out.set(rel, src)
    }
  }
  return [...out].map(([rel, src]) => ({ rel, src }))
}

// A named doc with no cap is its OWN check, not another arm of `coverage`:
// `coverage` is driven by an injected file list in the acceptance, and folding a
// second property into it made that probe measure both and fail on the wrong one.
// One function, one property.
// Wired through a NAMED wrapper that ignores the loop's argument, exactly as
// `coverageOverTree` is. Wiring `checkNamedDocs` directly made `CORPUS_CHECKS`'
// `fn(all)` pass the FILE LIST as the budget: `b.files` was undefined, every
// named document read as uncapped, and the production run reported ten. That is
// attack G from #614 -- a wrapper forwarding the loop's argument -- reproduced
// in the same file hours after it was fixed, which is the clearest evidence I
// have for the root-cause seat's thesis: the model that writes the assertion
// also writes the proof, so the proof inherits the model's blind spot.
let namedDocsBudgetSource = () => undefined

function namedDocsOverTree() {
  return checkNamedDocs(namedDocsBudgetSource())
}

function checkNamedDocs(budget) {
  return unmeasuredNamedDocs(budget).map(({ rel, src }) => ({
    severity: 'error',
    check: 'named-docs',
    where: rel,
    message: `is named by ${src} but has no cap in ${BUDGET_FILE}, so prose moved into it leaves the corpus and buys headroom in every cap at once. Bring it under a POLICY_GLOBS pattern so a cap on it is actually compared, or add it to CORPUS_EXCLUDED with a reason. A cap alone does not do it: a cap on a file no glob matches is refused by checkOrphanCaps precisely because it measures nothing.`,
  }))
}

// A cap recorded for a file no glob matches is compared against nothing, and
// its bytes are outside `corpus_tokens`. That made "give it a cap" -- the
// remedy `checkNamedDocs` used to print -- a way OUT of the corpus rather than
// into it: measured on this branch, 40 lines moved from CLAUDE.md into a named,
// capped, tracked file bought 483 tokens of headroom in all five caps with zero
// deletion, and 1189 tokens of new prose written into it afterwards raised
// `corpus_tokens` by nothing. The branch had already used the door itself, on
// `.github/PULL_REQUEST_TEMPLATE.md`, whose recorded cap of 38 sat unenforced
// while the file measured 539 lines in the reviewer's probe.
//
// Found by the fix review of #615, not by this file's own acceptance: the
// escape ran through a remedy the check recommends, which no mutation of the
// check can reach.
const FIXTURE_CAP_PREFIX = '.claude/workflows/fixtures/'

let orphanCapBudgetSource = () => undefined

function orphanCapsOverTree() {
  return checkOrphanCaps(orphanCapBudgetSource())
}

function checkOrphanCaps(budget) {
  const b = budget !== undefined ? budget : policyBudgets()
  if (!b || !b.files) return []
  // Against the TREE's policy files, never against a caller's list: the
  // acceptance drives `checkBudgets` with the rot fixtures, and comparing the
  // recorded caps against that list would report all 33 real files as orphans.
  const measured = new Set(policyFiles())
  return Object.keys(b.files)
    // A rot fixture is an input to the acceptance and never a member of the
    // corpus; `budgets.md` is capped at 1 so the fixture drive can produce an
    // "exceeds its cap" finding at all. Exempting the directory is what keeps
    // this check from refusing the harness that pins it.
    .filter((k) => !measured.has(k) && !k.startsWith(FIXTURE_CAP_PREFIX))
    .map((k) => ({
      severity: 'error',
      check: 'budgets',
      where: k,
      message: `has a cap in ${BUDGET_FILE} but is matched by no POLICY_GLOBS pattern, so the cap is compared against nothing and the file's bytes are outside corpus_tokens. Add a glob, or delete the cap -- a cap that measures nothing reads exactly like one that holds.`,
    }))
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

// `budget` is injectable for ONE reason: the acceptance. Every comparison below
// is against the recorded caps, and on a healthy corpus every comparison is
// FALSE -- so none of them has a witness, and each was independently deletable
// in silence: `if (b.corpus_tokens != null && corpusTokens > b.corpus_tokens)`
// -> `if (false)` left TOTAL 0, FIXTURE ok and exit 0, as did the same edit to
// the floor and the per-role loop. A rot fixture cannot reach them either,
// because the caps are recorded per real file. Driving the real function with a
// deliberately impossible budget is what gives each comparison a witness.
function checkBudgets(files, budget) {
  const b = budget !== undefined ? budget : policyBudgets()
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
// THE LOOP MODES. Everything above measures the corpus as it stands. These
// three measure whether the process around it is still turning: dispositions
// recorded, friction counted, rules retired. All three read merged history,
// which is why the `record` job in .github/workflows/governance.yml runs on
// push and schedule and never on `pull_request` -- a pull request's merge
// commit does not exist yet, so `<ref>..origin/main` measured from one describes
// a history the branch is not in.

// A squash merge's subject ends `(#N)`. tools/release/stamp.py has a PR_RE for
// the same job -- `\(#(\d+)\)`, unanchored -- and it is deliberately NOT reused
// here. Measured over v6.3.18..origin/main, it collects two numbers from two of
// the fifteen subjects, e.g.
//
//     tests(#303): the pinned stub-free typing ruler, and guard 4 ... (#596)
//
// where 303 is the issue the change is for and 596 is the pull request. That
// over-collection is harmless where stamp.py uses it (release notes keyed by a
// superset of numbers still name every merged PR, which is all rule 4 asks) and
// wrong here, where every number extracted is then asserted to carry a
// disposition: it would demand a plan row for an issue that was merely cited in
// a Conventional-Commit scope. Anchored to end of subject instead.
const MERGE_SUBJECT_RE = /\(#(\d+)\)\s*$/

// Where a disposition may live. CLAUDE.md's programme-tracking section names
// exactly these two: the Delivery-status table in the plan of record, and the
// living handover. #201 is deliberately NOT one of them -- it is the volatile
// half of the split, free to post at any moment and not in the tree, so a check
// that accepted it would be satisfiable by something no later seat can read
// from a checkout.
const DISPOSITION_FILES = ['docs/plan-2026-09-open-issues.md', 'docs/HANDOVER.md']

function mainRef() {
  const ok = git(['rev-parse', '--verify', '--quiet', 'origin/main'], { allowFail: true }).trim()
  return ok ? 'origin/main' : 'HEAD'
}

function mergedSubjects(since) {
  const out = git(['log', '--format=%s', `${since}..${mainRef()}`], { allowFail: true })
  return out ? out.split('\n').filter(Boolean) : []
}

function mergedPRs(subjects) {
  const seen = new Set()
  const rows = []
  for (const s of subjects) {
    const m = s.match(MERGE_SUBJECT_RE)
    if (!m || seen.has(m[1])) continue
    seen.add(m[1])
    rows.push({ pr: m[1], subject: s })
  }
  return rows
}

// --record. Pure over its two inputs so the acceptance can hand it a fixture
// history and a fixture disposition text without a git repository or a network.
//
// The message puts the class first and the pull-request number PAST the
// 60-character truncation keyOf applies. That is deliberate: every
// undispositioned merge then collapses into ONE ledger entry carrying a count,
// which is the behaviour keyOf's own comment describes and wants. A per-PR key
// would mean a new ledger entry for every merge that lands undispositioned and a
// stale one for every merge that ages out of the `--since` window, so the ledger
// would churn on the calendar rather than on the defect.
function checkRecord(prs, dispositionText) {
  const out = []
  for (const { pr, subject } of prs) {
    if (new RegExp(`#${pr}(?![0-9])`).test(dispositionText)) continue
    out.push({
      severity: 'error',
      check: 'record',
      where: DISPOSITION_FILES[0],
      message: `no disposition in the plan of record or the living handover for merged pull request #${pr} (${subject.slice(0, 90)}). A merge nobody recorded is a merge no later seat can resume from.`,
    })
  }
  return out
}

// --stats. The verdict vocabulary is READ from the wave script rather than
// re-listed here, so the histogram cannot classify against a grammar the
// reviewers were never given. It cannot be imported: web-fix-wave.js is a
// workflow script whose top level destructures `args` and throws without them,
// so `import` would execute it. The string literals in the prompt that tells a
// reviewer what to write are the source of truth, and they are extracted.
const WAVE_SCRIPT = '.claude/workflows/web-fix-wave.js'
const VERDICT_LITERAL_RE = /"Fix review:\s+([a-z]+)/g

// The one verdict class that means the process WORKED, read from the same file:
// mergePrompt requires `the newest "Fix review:" comment says merge` before a
// merge agent will merge, so that word is the terminal-success class by
// definition rather than by anyone's opinion here. It is excluded from the
// would-open list because friction is REWORK: measured on this repository's own
// window, ten successful merges over fifteen pull requests cleared the threshold
// of three and would have opened an issue titled "recurring friction: merge" --
// an issue saying the process working is a problem. The histogram still prints
// it; only the issue proposal is withheld. If the extraction fails the exclusion
// is dropped rather than guessed, so the mode over-reports instead of hiding a
// class it could not name.
const PASSING_VERDICT_RE = /"Fix review:"\s+comment says\s+([a-z]+)/

function passingVerdict(text = read(WAVE_SCRIPT)) {
  const m = text == null ? null : text.match(PASSING_VERDICT_RE)
  return m ? m[1] : null
}

function verdictClasses(text = read(WAVE_SCRIPT)) {
  if (text == null) return null
  const set = new Set()
  VERDICT_LITERAL_RE.lastIndex = 0
  let m
  while ((m = VERDICT_LITERAL_RE.exec(text))) set.add(m[1])
  return set.size ? [...set].sort() : null
}

// A `## Friction` section names, per bullet, the rule id that cost the seat
// time. A bullet with no backticked id is counted under a single bucket rather
// than dropped: an unparsed bullet is friction that happened, and silently
// discarding it biases the histogram toward "no friction".
const FRICTION_UNLABELLED = '(unlabelled friction bullet)'

function frictionIds(body) {
  const ids = []
  let inSection = false
  for (const line of String(body ?? '').split('\n')) {
    if (/^##\s/.test(line)) {
      inSection = /^##\s+Friction\b/i.test(line)
      continue
    }
    if (!inSection || !/^\s*[-*]\s/.test(line)) continue
    const m = line.match(/`([^`\n]{2,80})`/)
    ids.push(m ? m[1] : FRICTION_UNLABELLED)
  }
  return ids
}

// The plan's threshold: three or more of one key inside the window opens a
// `[policy] recurring friction:` issue. This mode PRINTS what it would open and
// opens nothing -- CLAUDE.md's "fix it; if you cannot, verify it independently;
// only then file it" makes filing the last resort of a seat that has measured,
// not something a cron job does on a count.
const FRICTION_THRESHOLD = 3

function statsHistogram(prs, fetched, classes) {
  const verdicts = new Map()
  const friction = new Map()
  const unclassified = []
  const re = new RegExp(`^Fix review:\\s*(${classes.join('|')})\\b`, 'i')
  for (const { pr } of prs) {
    const f = fetched.get(pr)
    if (!f) continue
    for (const c of f.comments ?? []) {
      const first = String(c.body ?? '').split('\n')[0].trim()
      if (!/^Fix review:/i.test(first)) continue
      const m = first.match(re)
      if (!m) {
        // A verdict that says "Fix review:" and then something the wave script
        // never taught a reviewer to say. Reported rather than bucketed: it is
        // the grammar drifting, and a histogram that quietly absorbs it would
        // hide exactly that.
        unclassified.push(`#${pr}: ${first.slice(0, 70)}`)
        continue
      }
      const k = m[1].toLowerCase()
      verdicts.set(k, (verdicts.get(k) ?? 0) + 1)
    }
    for (const id of frictionIds(f.body)) friction.set(id, (friction.get(id) ?? 0) + 1)
  }
  return { verdicts, friction, unclassified }
}

// Findings are severity `info`: the acceptance counts every finding by class, so
// these are pinned like any other check, while main() only ever exits non-zero
// on `error`. That is how a reporting mode is made undeletable without being
// made able to fail a job.
function statsFindings({ prs, fetched, fetchError, classes, passing = passingVerdict() }) {
  if (fetchError) {
    return [{
      severity: 'info',
      check: 'stats',
      where: '(github api)',
      message: `could not fetch pull-request bodies and comments: ${fetchError}. Printing no histogram rather than a histogram of zeroes -- a zero meaning "no data" and a zero meaning "no friction" are opposite claims, and only one of them is a reason to relax.`,
    }]
  }
  const { verdicts, friction, unclassified } = statsHistogram(prs, fetched, classes)
  const out = []
  for (const [kind, hist] of [['verdict class', verdicts], ['friction rule id', friction]]) {
    for (const [k, n] of [...hist.entries()].sort((a, b) => b[1] - a[1])) {
      if (n < FRICTION_THRESHOLD) continue
      if (kind === 'verdict class' && passing && k === passing) {
        out.push({
          severity: 'info',
          check: 'stats',
          where: '(window)',
          message: `not opened: verdict class "${k}" at ${n} is the passing verdict ${WAVE_SCRIPT} requires before a merge, so it counts rework nowhere. Friction is rework.`,
        })
        continue
      }
      out.push({
        severity: 'info',
        check: 'stats',
        where: '(window)',
        message: `would open "[policy] recurring friction: ${k}" -- ${kind} at ${n} in this window, threshold ${FRICTION_THRESHOLD}. Not opened here: a seat measures and files, a report does not.`,
      })
    }
  }
  for (const u of unclassified) {
    out.push({
      severity: 'info',
      check: 'stats',
      where: '(window)',
      message: `verdict comment outside the grammar in ${WAVE_SCRIPT} (${classes.join(', ')}): ${u}`,
    })
  }
  return out
}

// --sunset. Three ways a rule outlives its reason, and one guard that is more
// important than any of them.
const REFUSED_BY_RE = /REFUSED BY\s+`?([A-Za-z0-9_./-]+)`?/g
const SUNSET_MARKER_RE = /SUNSET:\s*(\d{4}-\d{2}-\d{2})/g
const HONOUR_RE = /HONOUR:\s*`?([A-Za-z0-9_.:#-]+)`?/g
// A detector is a script something can run. A rule that names one is not prose.
const DETECTOR_TOKEN_RE = /(?<![\w./-])((?:tests|tools|\.claude|\.github)\/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh|yml))\b/g

function detectorExists(token, rel) {
  if (resolvePathToken(token)) return true
  return !token.includes('/') && symbolElsewhere(token, rel)
}

// `frictionIds` null means the friction data could not be fetched. Every class
// that argues FROM ABSENCE is then withheld -- "no friction recorded" and "no
// friction measurable" are the same opposite-claims pair --record guards
// against, and proposing a sunset on the second would retire a live rule.
function checkSunset(rows, { friction, fires, today }) {
  const out = []
  const day = today.toISOString().slice(0, 10)
  for (const { file, text } of rows) {
    const lines = String(text ?? '').split('\n')
    lines.forEach((line, i) => {
      const where = `${file}:${i + 1}`

      // 1. Prose whose REFUSED BY names a detector that exists. The detector is
      //    the enforcement; the prose is a second copy of it, and two copies of
      //    one obligation drift apart -- the same argument the duplicates check
      //    makes within the corpus.
      REFUSED_BY_RE.lastIndex = 0
      let m
      while ((m = REFUSED_BY_RE.exec(line))) {
        if (!detectorExists(m[1], file)) continue
        out.push({
          severity: 'info', check: 'sunset', propose: true, where,
          message: `prose rule is REFUSED BY \`${m[1]}\`, which exists. Cut the prose and keep the detector; a rule enforced twice is a rule that will disagree with itself.`,
        })
      }

      // The detector guard, applied to the two classes below. A rule that names
      // a detector with no recorded fire is NOT proposed for sunset: a detector
      // that never fired may be working, and retiring it is how the defect it
      // was written for comes back with nothing left to catch it.
      DETECTOR_TOKEN_RE.lastIndex = 0
      const named = [...line.matchAll(DETECTOR_TOKEN_RE)].map((d) => d[1])
      const quiet = named.filter((d) => !fires.has(d))

      // 2. An explicit SUNSET: marker whose date has passed.
      SUNSET_MARKER_RE.lastIndex = 0
      while ((m = SUNSET_MARKER_RE.exec(line))) {
        if (m[1] >= day) continue
        if (quiet.length) {
          out.push({
            severity: 'info', check: 'sunset', propose: false, where,
            message: `held past its SUNSET: ${m[1]} marker: it names \`${quiet[0]}\`, a detector with zero recorded fires. A detector that never fired may be working, so it is not proposed for sunset on silence alone.`,
          })
          continue
        }
        out.push({
          severity: 'info', check: 'sunset', propose: true, where,
          message: `past its SUNSET: ${m[1]} marker (today ${day}). The rule named its own expiry; honour it or move the date deliberately.`,
        })
      }

      // 3. An honour rule -- one nothing mechanical checks -- with no friction
      //    and no incident reference over the window.
      HONOUR_RE.lastIndex = 0
      while ((m = HONOUR_RE.exec(line))) {
        const id = m[1]
        if (friction == null) {
          out.push({
            severity: 'info', check: 'sunset', propose: false, where,
            message: `honour rule \`${id}\` not evaluated: no friction data for this window, and absence of data is not absence of friction.`,
          })
          continue
        }
        if (friction.has(id)) continue
        if (/#\d+/.test(line)) continue
        if (quiet.length) {
          out.push({
            severity: 'info', check: 'sunset', propose: false, where,
            message: `held honour rule \`${id}\`: it names \`${quiet[0]}\`, a detector with zero recorded fires. A detector that never fired may be working.`,
          })
          continue
        }
        out.push({
          severity: 'info', check: 'sunset', propose: true, where,
          message: `honour rule \`${id}\` recorded no friction and cites no incident over this window. It costs every seat a read and refuses nothing measurable.`,
        })
      }
    })
  }
  return out
}

// ---------------------------------------------------------------------------
// The GitHub read. Nothing derived from a pull-request title, body or comment is
// ever interpolated into a command: every one of those is a JSON value parsed
// out of curl's stdout. The only interpolation into a URL is a pull-request
// number already matched as `\d+`, and execFileSync passes argv directly with no
// shell between it and curl. The token goes in on stdin as a curl -K config
// rather than in argv, where any process on the runner can read it.

function repoSlug() {
  const url = git(['remote', 'get-url', 'origin'], { allowFail: true }).trim()
  const m = url.match(/github\.com[:/]([^/\s]+)\/(.+?)(?:\.git)?$/)
  return m ? `${m[1]}/${m[2]}` : null
}

function ghGet(pathname) {
  const token = process.env.GITHUB_TOKEN
  if (!token) return { ok: false, why: 'GITHUB_TOKEN is not set' }
  let raw
  try {
    raw = execFileSync('curl', ['-sS', '-w', '\n%{http_code}', '-K', '-', 'https://api.github.com' + pathname], {
      input:
        `header = "Authorization: Bearer ${token}"\n` +
        'header = "Accept: application/vnd.github+json"\n' +
        'header = "X-GitHub-Api-Version: 2022-11-28"\n',
      encoding: 'utf8',
      maxBuffer: 32 * 1024 * 1024,
    })
  } catch (e) {
    return { ok: false, why: `curl failed (${String(e.message).slice(0, 120)})` }
  }
  const cut = raw.lastIndexOf('\n')
  const code = raw.slice(cut + 1).trim()
  if (code !== '200') return { ok: false, why: `HTTP ${code} from ${pathname}` }
  try {
    return { ok: true, data: JSON.parse(raw.slice(0, cut)) }
  } catch {
    return { ok: false, why: `unparseable JSON from ${pathname}` }
  }
}

// Returns {fetched, fetchError}. ANY failure aborts into fetchError rather than
// yielding a partial map: a histogram over the pull requests that happened to
// answer is a claim about the window that the window did not make.
function fetchWindow(prs) {
  const slug = repoSlug()
  if (!slug) return { fetched: new Map(), fetchError: 'no github remote on origin' }
  const fetched = new Map()
  for (const { pr } of prs) {
    const body = ghGet(`/repos/${slug}/pulls/${pr}`)
    if (!body.ok) return { fetched: new Map(), fetchError: body.why }
    const comments = ghGet(`/repos/${slug}/issues/${pr}/comments?per_page=100`)
    if (!comments.ok) return { fetched: new Map(), fetchError: comments.why }
    fetched.set(pr, { body: body.data?.body ?? '', comments: Array.isArray(comments.data) ? comments.data : [] })
  }
  return { fetched, fetchError: null }
}

// A detector "fires" if the ledger records a defect naming it, or the window's
// friction does. That is a deliberately generous reading: it errs toward keeping
// a rule, and the guard it feeds is one-sided by design.
function detectorFires(friction) {
  const fires = new Set()
  for (const e of knownBad().entries ?? []) {
    const key = typeof e === 'string' ? e : e.key
    DETECTOR_TOKEN_RE.lastIndex = 0
    for (const m of String(key).matchAll(DETECTOR_TOKEN_RE)) fires.add(m[1])
  }
  for (const id of friction?.keys() ?? []) {
    DETECTOR_TOKEN_RE.lastIndex = 0
    for (const m of String(id).matchAll(DETECTOR_TOKEN_RE)) fires.add(m[1])
  }
  return fires
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

// #361 fixed exactly this defect in `tests/structure.py`: a re-record only ever
// happens on a branch, and a branch commit is rewritten by the next amend and
// deleted by the squash that lands it, so a HEAD stamp names a commit no later
// reader can resolve. The countermeasure written for it -- an AST pin in
// `tests/features.py` -- was aimed at THAT FILE rather than at the property, so
// it did not travel, and this file reproduced the defect with the fix already in
// the tree. The committed value was `513a4c1`, a branch head that reached main
// in no form.
//
// The merge base is the fix in both files. It is on `origin/main` while the
// branch is open and stays on it after the squash, which is the whole property:
// a provenance SHA a reader can resolve.
function recordedAtSha() {
  return git(['merge-base', 'origin/main', 'HEAD'], { allowFail: true }).trim() || null
}

// Reachability from `origin/main`, not from HEAD. From HEAD is the assertion
// that cannot fail at the moment the defect is made: a HEAD stamp is trivially
// reachable from the HEAD that wrote it, and only stops resolving later, on
// somebody else's clone. From main it fails on the pull request that stamped it.
let provenanceShaSource = () => {
  const raw = read(KNOWN_BAD_FILE)
  return raw == null ? null : JSON.parse(raw).recorded_at
}

function checkProvenance() {
  const sha = provenanceShaSource()
  if (sha === null) return []
  const f = (message) => [{ severity: 'error', check: 'provenance', where: KNOWN_BAD_FILE, message }]
  if (!sha) return f('no `recorded_at`, so the ledger records no state it was measured against')
  // A clone with no `origin/main` cannot answer, and answering "unreachable"
  // there would refuse every pull request for the checkout's shape rather than
  // for the file's content. Said out loud rather than returning silently: a
  // check that skips without saying so reads exactly like one that passed.
  if (!git(['rev-parse', '--verify', '--quiet', 'origin/main'], { allowFail: true }).trim()) {
    console.log(`  skip     provenance             origin/main is not in this clone, so ${sha.slice(0, 7)} cannot be resolved`)
    return []
  }
  // EXIT 1 IS THE ANSWER; ANYTHING ELSE IS THE ABSENCE OF ONE. `--is-ancestor`
  // exits 1 for "no" and 128 when it cannot look -- an object the clone does
  // not have, which is what a shallow clone reports for a perfectly good SHA.
  // A bare catch read both as "no" and turned every shallow clone with an
  // origin/main ref into a false refusal.
  try {
    execFileSync('git', ['merge-base', '--is-ancestor', sha, 'origin/main'], { cwd: ROOT, stdio: 'ignore' })
    return []
  } catch (e) {
    // EXIT 1 IS THE ANSWER ONLY IN A CLONE THAT CAN WALK THE WHOLE GRAPH. The
    // env-matrix's first CI run found the case the arm below did not cover: a
    // clone holding every object but marked shallow at a commit AT OR ABOVE
    // origin/main, where the walk from origin/main stops at the boundary before
    // reaching a perfectly good SHA and answers 1 -- "no" -- rather than 128.
    // Where the boundary lands is the whole difference, not the git version: CI
    // checks out the pull request's merge commit, whose first parent IS
    // origin/main, so the matrix's HEAD~1 graft sits exactly there; a branch
    // tip's HEAD~1 sits above origin/main and the walk succeeds. One git, both
    // shapes, opposite answers -- reproduced on this box from a synthetic merge
    // commit. So shallowness is asked on BOTH error paths: a "no" git could not
    // have established is not a refusal, and rule 5 of decisions/0003 says to
    // say so rather than go silent or -- worse -- refuse.
    const shallowOnNo = e.status === 1 && git(['rev-parse', '--is-shallow-repository'], { allowFail: true }).trim() === 'true'
    if (shallowOnNo) {
      console.log(`  skip     provenance             this clone is shallow, so git's "not an ancestor" for ${sha.slice(0, 7)} may be the boundary, not the graph`)
      return []
    }
    if (e.status !== 1) {
      // EXIT 128 IS TWO ANSWERS, and the first version of this arm took both
      // for the same one. It means "this clone is shallow, so I cannot walk
      // that far" AND "no object with that name exists here" -- and the second
      // is a REFUSAL, not an absence of one: a ledger naming a SHA nothing ever
      // carried is precisely the defect this check is for. Measured by the #616
      // review: `recorded_at: deadbee` refused before that arm and skipped
      // after it. `--is-shallow-repository` is the one call that separates them,
      // and it is asked only on the error path, so it costs nothing on a healthy
      // run. Rule 5 of decisions/0003 says report rather than go silent; the
      // section under it says do not report a refusal you have not established.
      const shallow = git(['rev-parse', '--is-shallow-repository'], { allowFail: true }).trim() === 'true'
      if (!shallow) {
        return f(`\`recorded_at\` is ${sha.slice(0, 7)}, which no object in this clone carries at all. A ledger stamped from a branch head names a SHA the squash deletes; regenerate with --record-known-bad, which stamps the merge base`)
      }
      console.log(`  skip     provenance             this clone is shallow, so git cannot say whether ${sha.slice(0, 7)} is an ancestor of origin/main`)
      return []
    }
    return f(`\`recorded_at\` is ${sha.slice(0, 7)}, which is not reachable from origin/main. A branch head is rewritten by the next amend and deleted by the squash that lands it; regenerate with --record-known-bad, which stamps the merge base`)
  }
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
// `provenance` joins them for the same reason: a ledger whose own recorded_at
// resolves to nothing is not a defect to freeze and drain, and freezing it is
// self-referential -- the ledger would be recording that the ledger is wrong.
// The first `--record-known-bad` after this check landed did exactly that,
// entering the finding one run before the re-record fixed it.
// `named-docs` joins them for the reason `ratchet-budgets.md` gives about caps:
// an ESCAPE recordable as a known defect is not a closure. The ledger is the
// right instrument for a citation that has rotted; it is the wrong one for a
// document sitting outside every cap, because recording it makes the corpus
// smaller by agreement rather than by measurement.
const NEVER_SUPPRESSED = new Set(['budgets', 'coverage', 'provenance', 'named-docs'])

// RECORD_KEY marks the ledger entries belonging to the `record` class. They are
// scoped OUT of the default run and IN to `--record`, in both directions: a
// default run does not read merged history, so without the scope every record
// entry would report "no longer fires" on a corpus that is fine; and a --record
// run measures nothing else, so without it every other entry would.
const RECORD_KEY = (k) => k.startsWith('record|')

function applyKnownBad(findings, keyFilter = (k) => !RECORD_KEY(k)) {
  const kb = knownBad()
  // Entries are {key, count}. A bare string is read as one occurrence, so an
  // older file still parses rather than silently suppressing everything.
  const recorded = new Map()
  for (const e of kb.entries ?? []) {
    const key = typeof e === 'string' ? e : e.key
    if (!keyFilter(key)) continue
    recorded.set(key, typeof e === 'string' ? 1 : e.count ?? 1)
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
  { name: 'named-docs', what: 'a document the corpus names but no cap measures', fixture: '(driven in assertAcceptance)' },
  { name: 'coverage', what: 'every file in a policy directory is matched by a glob', fixture: '(a probe file, see assertAcceptance)' },
  { name: 'provenance', what: "the known-bad ledger's recorded_at resolves from origin/main", fixture: '(driven in assertAcceptance)' },
  { name: 'record', what: 'every merged pull request has a disposition (refuses)', fixture: 'fixtures/policy-loop/merged-subjects.txt' },
  { name: 'stats', what: 'verdict and friction histograms, and what they would open', fixture: 'fixtures/policy-loop/pr-payloads.json' },
  { name: 'sunset', what: 'rules that have outlived the reason they were written', fixture: 'fixtures/policy-loop/sunset-rules.md' },
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
  // The three loop modes. `mustNot` is here because `count` is a MINIMUM, and
  // the anchoring of MERGE_SUBJECT_RE is a claim about what must NOT be
  // collected: `count: 2` alone is satisfied by three findings, including the
  // one an unanchored regex would invent for the issue number in a commit
  // scope. Over-firing is the failure mode this whole mode has to avoid, so it
  // is pinned as a failure rather than left to a count that cannot see it.
  record: {
    count: 2,
    must: ['no disposition in the plan of record'],
    // The phrase the finding uses for the number it COLLECTED. Matching bare
    // "#8888" would be satisfied by the subject the message echoes back, which
    // is the rotten subject itself and proves nothing about the regex.
    mustNot: ['merged pull request #8888'],
  },
  stats: {
    count: 5,
    must: [
      'would open "[policy] recurring friction: CLAUDE.md#budgets"',  // a rule id at threshold
      'would open "[policy] recurring friction: blocked"',            // a verdict class at threshold
      'is the passing verdict',                                       // ...and the class that is not rework
      'outside the grammar in .claude/workflows/web-fix-wave.js',     // the grammar drifting
      'could not fetch pull-request bodies and comments',             // the opposite-claims guard
    ],
    // The fixture puts the passing class OVER the threshold on purpose, so this
    // is a pin and not a vacuous one: without the exclusion the same window
    // produces this line.
    mustNot: ['would open "[policy] recurring friction: merge"'],
  },
  sunset: {
    count: 5,
    must: [
      'REFUSED BY `tests/closure.py`, which exists',   // prose the detector already refuses
      'past its SUNSET: 2020-01-01 marker',            // an expiry the rule set itself
      'recorded no friction and cites no incident',    // an honour rule with nothing behind it
      'zero recorded fires',                           // THE GUARD: a quiet detector is held
      'absence of data is not absence of friction',    // no friction data withholds the class
    ],
  },
}

CORPUS_CHECKS.push(checkIndex, checkDuplicates, checkBudgets, coverageOverTree, namedDocsOverTree, orphanCapsOverTree, checkProvenance)

// SILENT ON A HEALTHY INPUT. A count-and-substring pin proves a check can still
// refuse; it cannot prove the check is not refusing everything. Each loop mode
// is therefore also run against a fixture that is healthy in exactly the way the
// rot fixture is rotten, and must produce nothing.
const REQUIRED_SILENT = ['record', 'stats', 'sunset']

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

  // The three loop modes, pinned on fixtures/policy-loop/. Their check functions
  // are pure over injected inputs precisely so this runs with no git history, no
  // network and no token: a pin that needed any of those would be skipped on the
  // machine where it matters and would pin nothing.
  const loop = loopFixtures()
  if (!loop) {
    console.log('\nFIXTURE VACUOUS: fixtures/policy-loop/ is missing or unreadable; record, stats and sunset are all deletable in silence')
    return 1
  }
  const rotten = checkRecord(loop.prs, loop.dispositionsRotten)
  found.push(...rotten)
  found.push(...statsFindings({ prs: loop.prs, fetched: loop.fetched, fetchError: null, classes: loop.classes }))
  found.push(...statsFindings({ prs: loop.prs, fetched: new Map(), fetchError: 'fixture: the API was not reachable', classes: loop.classes }))
  found.push(...checkSunset(loop.sunsetRot, { friction: loop.friction, fires: loop.fires, today: loop.today }))
  found.push(...checkSunset(loop.sunsetRot, { friction: null, fires: loop.fires, today: loop.today }))

  // Silent on a healthy input. Reported as its own failure line rather than
  // folded into the counts: a check that fires on everything satisfies every
  // count and every substring, and is exactly as useless as one that fires on
  // nothing.
  const silent = {
    record: checkRecord(loop.prs, loop.dispositionsHealthy),
    stats: statsFindings({ prs: loop.healthyPrs, fetched: loop.fetched, fetchError: null, classes: loop.classes }),
    sunset: checkSunset(loop.sunsetHealthy, { friction: loop.friction, fires: loop.fires, today: loop.today }),
  }

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
  // Every budget comparison, driven for real. On a healthy corpus each is FALSE
  // and therefore witnessless, which is how all four came to be independently
  // deletable in silence. An impossible budget gives each one a witness; a
  // generous one proves none of them fires on a corpus that is fine.
  const capClasses = ['file', 'floor', 'corpus', 'role']
  const tinyBudget = {
    files: Object.fromEntries(policyFiles().map((f) => [f, 0])),
    always_loaded_tokens: 0,
    corpus_tokens: 0,
    roles: { probe: { opens: ['CLAUDE.md'], cap: 0 } },
  }
  const hugeBudget = {
    files: Object.fromEntries(policyFiles().map((f) => [f, 1e9])),
    always_loaded_tokens: 1e9,
    corpus_tokens: 1e9,
    roles: { probe: { opens: ['CLAUDE.md'], cap: 1e9 } },
  }
  const classOf = (f) =>
    f.where === '(always-loaded set)' ? 'floor'
      : f.where === '(whole corpus)' ? 'corpus'
        : f.where.startsWith('(role ') ? 'role' : 'file'
  const tinyHits = new Set(checkBudgets(policyFiles(), tinyBudget).map(classOf))
  pins += capClasses.length + 1
  for (const cls of capClasses) {
    if (tinyHits.has(cls)) continue
    console.log(`\nFIXTURE VACUOUS: the '${cls}' budget comparison produced nothing against a zero budget, so deleting it would change no output. Every cap is false on a healthy corpus and therefore has no witness unless one is driven.`)
    return 1
  }
  const hugeHits = checkBudgets(policyFiles(), hugeBudget)
  if (hugeHits.length) {
    console.log(`\nFIXTURE OVER-FIRES: the budget check produced ${hugeHits.length} finding(s) against a budget nothing can exceed, e.g. ${JSON.stringify(hugeHits[0].message.slice(0, 120))}`)
    return 1
  }

  // The zero/huge pair pins that each comparison exists and has the right sign
  // AT THE EXTREMES. It does not pin that it compares against the RECORDED
  // number: the #615 review measured `> cap * 2` passing the whole acceptance
  // on three of the four classes, rc=0, no VACUOUS line. A scale factor is a
  // plausible edit and it silently triples the headroom.
  //
  // The boundary is what pins it, and the measured value comes from the check's
  // own output rather than from a second implementation of the measurement --
  // re-deriving it here would be the proxy substitution this acceptance keeps
  // producing. At cap = measured the strict `>` must stay silent; at
  // cap = measured - 1 it must fire. `> cap * 2` stays silent at both and is
  // caught by the second.
  const measuredFrom = (findings) => {
    const m = {}
    for (const f of findings) {
      const n = /^(?:about )?(\d+) (?:tokens|lines)\b/.exec(f.message)
      if (n) m[`${classOf(f)}|${f.where}`] = Number(n[1])
    }
    return m
  }
  const atMeasured = measuredFrom(checkBudgets(policyFiles(), tinyBudget))
  const scaled = (delta) => {
    const files = {}
    for (const f of policyFiles()) files[f] = (atMeasured[`file|${f}`] ?? 0) + delta
    return {
      files,
      always_loaded_tokens: (atMeasured['floor|(always-loaded set)'] ?? 0) + delta,
      corpus_tokens: (atMeasured['corpus|(whole corpus)'] ?? 0) + delta,
      roles: { probe: { opens: ['CLAUDE.md'], cap: (atMeasured['role|(role probe)'] ?? 0) + delta } },
    }
  }
  pins += capClasses.length + 1
  const exactHits = checkBudgets(policyFiles(), scaled(0))
  if (exactHits.length) {
    console.log(`\nFIXTURE OVER-FIRES: a cap set to exactly the measured value produced ${exactHits.length} finding(s); the comparison is not strict, e.g. ${JSON.stringify(exactHits[0].message.slice(0, 120))}`)
    return 1
  }
  const underHits = new Set(checkBudgets(policyFiles(), scaled(-1)).map(classOf))
  for (const cls of capClasses) {
    if (underHits.has(cls)) continue
    console.log(`\nFIXTURE VACUOUS: the '${cls}' comparison stayed silent against a cap one below the measured value, so it is not comparing against the recorded number. A constant factor or offset on that cap would pass every other pin here.`)
    return 1
  }

  // Orphan caps. A cap on a file no POLICY_GLOBS pattern matches is compared
  // against nothing, which made "give it a cap" a way out of the corpus. False
  // on a healthy tree like every other budget property, so it is driven.
  pins += 3
  const driveOC = (budget) => {
    const prev = orphanCapBudgetSource
    orphanCapBudgetSource = () => budget
    try { return orphanCapsOverTree() } finally { orphanCapBudgetSource = prev }
  }
  if (orphanCapBudgetSource() !== undefined) {
    console.log(`\nFIXTURE VACUOUS: orphanCapBudgetSource's production default is not undefined, so the wired check reads a budget nobody recorded.`)
    return 1
  }
  const ORPHAN = 'docs/a-file-no-glob-matches.md'
  const ocRot = driveOC({ files: { ...Object.fromEntries(policyFiles().map((f) => [f, 1])), [ORPHAN]: 1 } })
  if (ocRot.length !== 1 || ocRot[0].where !== ORPHAN) {
    console.log(`\nFIXTURE VACUOUS: checkOrphanCaps did not report ${ORPHAN} exactly once (got ${JSON.stringify(ocRot.map((f) => f.where))}); a cap that measures nothing would read exactly like one that holds.`)
    return 1
  }
  const ocOk = driveOC({ files: Object.fromEntries(policyFiles().map((f) => [f, 1])) })
  if (ocOk.length) {
    console.log(`\nFIXTURE OVER-FIRES: checkOrphanCaps reported ${ocOk.length} finding(s) with every cap on a measured file, e.g. ${JSON.stringify(ocOk[0].where)}`)
    return 1
  }

  // Provenance. Same shape as every other property here -- on a healthy tree the
  // recorded SHA IS reachable, so the comparison is false and has no witness.
  // Driven both ways: a commit main does not carry must be refused, and
  // origin/main itself must be silent.
  //
  // THE WITNESS IS UNREACHABLE BY CONSTRUCTION, NOT BY CIRCUMSTANCE, and the
  // first version got that wrong in the one run where it mattered. It used
  // `HEAD`, which is unreachable from main only while a branch is unmerged, and
  // skipped the assertion when the two were equal -- "a null control twice
  // over", said the comment, which is true and beside the point. `governance.yml`
  // ALSO runs on `push: branches: [main]`, where the pushed commit IS
  // origin/main: the guard went false, the witness never ran, and an emptied
  // `checkProvenance` passed. The mutation lane beside it then reports the check
  // as deletable and exits 1, so `policy-docs` would have gone red on main at
  // this pull request's own merge. The countermeasure caught the defect its own
  // commit introduced, which is the whole argument for the lane.
  //
  // `commit-tree` with no `-p` builds a real, parentless commit carrying main's
  // tree. It is a genuine object, so `--is-ancestor` gives a real answer rather
  // than the exit-128 it gives for a bad SHA -- which is the path this check now
  // treats as "no answer" -- and having no parents it can never be an ancestor
  // of anything. Identity is passed in the environment because CI checkouts
  // configure none, and `commit-tree` refuses without one.
  const driveProv = (sha) => {
    const prev = provenanceShaSource
    provenanceShaSource = () => sha
    try { return checkProvenance() } finally { provenanceShaSource = prev }
  }
  const mainSha = git(['rev-parse', 'origin/main'], { allowFail: true }).trim()
  const IDENT = {
    ...process.env,
    GIT_AUTHOR_NAME: 'policy_lint', GIT_AUTHOR_EMAIL: 'policy_lint@invalid',
    GIT_COMMITTER_NAME: 'policy_lint', GIT_COMMITTER_EMAIL: 'policy_lint@invalid',
  }
  const unreachable = mainSha
    ? git(['commit-tree', `${mainSha}^{tree}`, '-m', 'policy_lint provenance witness'], { allowFail: true, env: IDENT }).trim()
    : ''
  // A SHALLOW CLONE CANNOT DRIVE EITHER ARM. `checkProvenance` now treats a
  // "not an ancestor" from a shallow clone as the boundary rather than the
  // graph, so the parentless witness below would be skipped, not refused, and
  // the drive would read VACUOUS for a check that is behaving as designed. The
  // env-matrix's first CI run found the false refusal; its acceptance found the
  // fix that was too blunt. Asked once here, before any pin is promised.
  const shallowClone = git(['rev-parse', '--is-shallow-repository'], { allowFail: true }).trim() === 'true'
  if (!mainSha || !unreachable || shallowClone) {
    // Said out loud, and NOT counted. A skipped drive that still added its pins
    // would report a total the run did not earn.
    // KEYED ON THE CHECK'S OWN NAME, and that spelling is load-bearing:
    // `policy_lint_mutants.mjs` matches `skip <name>-pin` in this run's output
    // to tell "this check survived its own deletion" from "this clone could not
    // exercise it at all". Any other spelling would need a mapping table there,
    // and two hand-kept lists that must agree are the defect generator
    // decisions/0003 rule 4 is about.
    console.log(`  skip     checkProvenance-pin    ${shallowClone ? 'this clone is shallow, so a "no" from --is-ancestor may be the boundary rather than the graph' : mainSha ? 'git could not build a witness commit' : 'origin/main is not in this clone'}, so neither direction can be driven`)
  } else {
    pins += 3
    if (driveProv(unreachable).length !== 1) {
      console.log(`\nFIXTURE VACUOUS: checkProvenance did not refuse ${unreachable.slice(0, 7)}, a parentless commit that cannot be an ancestor of anything. A ledger stamped from HEAD names a SHA the squash deletes, which is #361 in a second file.`)
      return 1
    }
    // A SHA NO OBJECT CARRIES, which is a different question from an object
    // that exists and is not an ancestor -- and the answer git gives for it is
    // exit 128, the same one it gives a shallow clone. The #616 review measured
    // the cost of taking those for the same thing: `recorded_at: deadbee`
    // refused before that arm and skipped after it.
    //
    // WHETHER THIS ARM CAN RUN AT ALL IS AN ENVIRONMENT FACT, and the previous
    // version of this comment asserted the environment instead of asking it:
    // "This clone is not shallow, so here the refusal is the right answer."
    // Nothing measured that. In a `--depth 1` clone `checkProvenance` DECLINES
    // by design -- the arm directly above is what taught it to -- so demanding
    // a refusal here asserts the opposite of what the same commit added, and
    // the run printed `skip provenance ... this clone is shallow` two lines
    // before failing with `and this clone is not shallow`. rc=1 for both lanes
    // on any shallow seat; `governance.yml` uses fetch-depth: 0, so the
    // exposure was local, which is exactly where a seat runs `prepr.sh`.
    //
    // NOT keyed `skip <name>-pin`, deliberately. That spelling tells
    // `policy_lint_mutants.mjs` the check could not be driven AT ALL. This arm
    // is only reached in a clone that is not shallow -- the guard above the
    // witness drive skips both arms otherwise, under exactly that key -- so a
    // `shallowHere` true here would be a contradiction, kept as belt and
    // braces. Claiming less than the run earns is the same dishonesty as
    // claiming more.
    const shallowHere = git(['rev-parse', '--is-shallow-repository'], { allowFail: true }).trim() === 'true'
    if (shallowHere) {
      console.log(`  skip     provenance-deadbeef    this clone is shallow, so "no object carries this SHA" and "history this clone cannot walk" are the same exit 128; the witness arm above still drove the check`)
    } else {
    pins += 1
    if (driveProv('deadbeefdeadbeefdeadbeefdeadbeefdeadbeef').length !== 1) {
      console.log(`\nFIXTURE VACUOUS: checkProvenance did not refuse a SHA no object in this clone carries. git answers exit 128 for that AND for a shallow clone; reading both as "cannot look" loses the refusal a bogus stamp deserves, and this clone is measured non-shallow above.`)
      return 1
    }
    }
    if (driveProv(mainSha).length) {
      console.log(`\nFIXTURE OVER-FIRES: checkProvenance refused origin/main itself.`)
      return 1
    }
    if (driveProv(null).length) {
      console.log(`\nFIXTURE OVER-FIRES: checkProvenance reported on a tree with no ledger at all.`)
      return 1
    }
  }

  // named-docs, driven both ways. Its property -- "a document the corpus names
  // that no cap measures" -- is FALSE on a healthy tree by construction, so it
  // has no witness there and would be deletable in silence exactly as the caps
  // were. An empty budget makes every named doc uncapped; a budget capping the
  // whole corpus makes none.
  pins += 2
  const driveND = (budget) => {
    const prev = namedDocsBudgetSource
    namedDocsBudgetSource = () => budget
    try { return namedDocsOverTree() } finally { namedDocsBudgetSource = prev }
  }
  if (namedDocsBudgetSource() !== undefined) {
    console.log(`\nFIXTURE VACUOUS: namedDocsBudgetSource's production default is not undefined, so the wired check reads a budget nobody recorded.`)
    return 1
  }
  const ndBare = driveND({ files: {} })
  if (!ndBare.length) {
    console.log(`\nFIXTURE VACUOUS: checkNamedDocs reported nothing against an empty budget, where every document the corpus names is uncapped by definition. Prose moved into a named-but-uncapped file leaves the corpus and buys headroom in every cap at once.`)
    return 1
  }
  // The prefix list is a hole in the check it sits beside unless markdown is
  // exempt from it. Driven rather than argued, because the round-two review of
  // #615 measured the argued version letting 1342 tokens out through
  // `tests/POLICY-NOTES.md`. Both directions: a document under an excluded
  // prefix must still be a document, and a data file under one must still be
  // data -- an exemption that reported the .txt files back would be the
  // over-fire that made the prefixes necessary.
  pins += 2
  const UNDER_PREFIX = CORPUS_EXCLUDED_PREFIX[0]
  // Both spellings. The lowercase literal alone pinned the EXTENSION and not the
  // case-insensitivity the property rests on: dropping the `/i` flag left all
  // pins green and reopened the `.MD` route at 138 tokens per cap.
  if (corpusExcluded(`${UNDER_PREFIX}a-policy-note.md`) ||
      corpusExcluded(`${UNDER_PREFIX}A-POLICY-NOTE.MD`) ||
      corpusExcluded(`${UNDER_PREFIX}a-policy-note.rst`)) {
    console.log(`\nFIXTURE VACUOUS: a .md under the excluded prefix '${UNDER_PREFIX}' is treated as outside the corpus, so prose moved there leaves every cap at once. A directory says where data lives; it does not make a document into data.`)
    return 1
  }
  if (!corpusExcluded(`${UNDER_PREFIX}some-fixture.txt`)) {
    console.log(`\nFIXTURE OVER-FIRES: a .txt under the excluded prefix '${UNDER_PREFIX}' is reported, which is the data this repository keeps there and the reason the prefix list exists.`)
    return 1
  }

  // The SCAN, driven directly. Three properties, none of which the budget seam
  // can reach, and all three shipped unwitnessed at some point in this branch.
  pins += 3
  const scanned = namedDocMatches('see `./docs/a.md` and `docs/x/../b.rst` and `docs/c.mdx`')
  if (!scanned.includes('docs/a.md') || !scanned.includes('docs/b.rst')) {
    console.log(`\nFIXTURE VACUOUS: namedDocMatches did not normalise its matches (got ${JSON.stringify(scanned)}). trackedFiles() holds normalised git ls-files output, so a raw './docs/a.md' fails the tracked lookup and the destination goes unreported everywhere.`)
    return 1
  }
  // AN EXTENSION NOBODY HAS THOUGHT OF. This is the assertion the inversion
  // exists for: three rounds closed a named extension each and shipped a body
  // claiming the rest were covered. `.zqx` is not in any list, is not a real
  // format, and must still be seen -- because the scan no longer asks whether an
  // extension is a document, it asks whether it is code or data.
  if (!namedDocMatches('see `docs/invented.zqx`').includes('docs/invented.zqx')) {
    console.log(`\nFIXTURE VACUOUS: namedDocMatches did not see an extension absent from every list. The scan is an allowlist again, and an allowlist of document extensions cannot be complete -- .MD, .txt, .rst, .mdx and .mdc each escaped one at a time.`)
    return 1
  }
  // And the other direction: code and data must NOT be reported, or the check
  // fires on every `.py` a brief legitimately cites.
  const codeSeen = namedDocMatches('see `tests/entities.py` and `tests/closures.json` and `tests/run.sh`')
  if (codeSeen.length) {
    console.log(`\nFIXTURE OVER-FIRES: namedDocMatches returned ${JSON.stringify(codeSeen)} for code and data paths, which every brief cites by name.`)
    return 1
  }
  // The generated-output exclusion is not the location one, and folding them
  // together would re-excuse a document by location -- which was round three's
  // blocker. A `.mdc` under the generated prefix is excluded; a `.md` under a
  // DATA prefix is not.
  if (!corpusExcluded('.cursor/rules/gate-scoping.mdc') || corpusExcluded('tests/a-policy-note.md')) {
    console.log(`\nFIXTURE VACUOUS: the generated-output and data-directory exclusions have been folded together. Generated output is excluded whatever its extension; a document is never excused by location.`)
    return 1
  }
  // A shared /g regex carries `lastIndex` between calls when it is used with
  // `exec` or `test`. `matchAll` clones it, so it does not -- asserted rather
  // than trusted, because if it did every file after the first would be scanned
  // from an offset and the check would silently go quiet.
  if (JSON.stringify(namedDocMatches('`docs/c.mdx`')) !== JSON.stringify(namedDocMatches('`docs/c.mdx`'))) {
    console.log(`\nFIXTURE VACUOUS: DOCUMENT_RE is stateful across calls, so every file after the first is scanned from a stale lastIndex.`)
    return 1
  }
  // The bare pass, driven both ways. Its property is not the extension one:
  // every word matches, so what it must do is drop the three names the tree has
  // and keep everything else for the caller's tracked lookup to judge.
  pins += 2
  const threeNames = bareNameCandidates('the VERSION and the LICENSE and the NOTICE')
  if (['VERSION', 'LICENSE', 'NOTICE'].some((n) => threeNames.includes(n))) {
    console.log(`\nFIXTURE VACUOUS: bareNameCandidates returned an extensionless name the tree classifies as data. VERSION, LICENSE and NOTICE are the three extensionless tracked files and none is a document.`)
    return 1
  }
  if (!bareNameCandidates('see HANDOVER for the rest').includes('HANDOVER')) {
    console.log(`\nFIXTURE VACUOUS: bareNameCandidates dropped an ordinary bare name, so a destination with no extension is unreported -- the route round four and round five both stated as a limit and I twice costed wrong.`)
    return 1
  }
  // The three names must be exactly the tree's extensionless tracked files, or
  // this is an allowlist that goes stale the moment a fourth appears.
  const bareInTree = new Set(trackedFiles().list.filter((f) => !f.split('/').pop().includes('.')).map((f) => f.split('/').pop()))
  const strayNames = [...NOT_A_DOCUMENT_NAME].filter((n) => !bareInTree.has(n))
  if (strayNames.length) {
    console.log(`\nFIXTURE VACUOUS: NOT_A_DOCUMENT_NAME lists ${JSON.stringify(strayNames)}, which no tracked file has. Bounded by the tree, or it is an allowlist wearing a different name.`)
    return 1
  }

  // NOT_A_DOCUMENT is only bounded if it is checked against the tree it claims
  // to describe. Every extension present in the tracked tree must be either code
  // or data (in the set) or a document -- and a document that is neither capped
  // nor excluded is a finding, which the null control above already proves is
  // empty. So the assertion here is the one that can go stale: an extension in
  // NOT_A_DOCUMENT that no tracked file has is dead weight to be deleted, and an
  // extension in the tree that is a document is what the corpus must account for.
  const treeExts = new Set(trackedFiles().list
    .map((f) => (f.includes('.') ? f.split('.').pop().toLowerCase() : ''))
    .filter(Boolean))
  // AND THE TWO EXCLUSION LISTS, which had no such assertion at all. An entry
  // naming a file the tree no longer has is not merely untidy: it is a standing
  // hole, because a FUTURE file written at that exact path is excluded from the
  // corpus with no diff to this file for a reviewer to see. This branch is what
  // made the case live -- it deletes `tools/audit/round2/HARNESSES.md` and the
  // three round trees, so without the assertion four entries would have stayed
  // here naming nothing, and `round2/HARNESSES.md` would have become a
  // ready-made destination for prose leaving every cap at once.
  pins += 1
  const { set: liveTree, list: liveList } = trackedFiles()
  const deadExcluded = [
    ...[...CORPUS_EXCLUDED].filter((f) => !liveTree.has(f)),
    ...CORPUS_EXCLUDED_PREFIX.filter((p) => !liveList.some((f) => f.startsWith(p))),
  ]
  if (deadExcluded.length) {
    console.log(`\nFIXTURE VACUOUS: ${JSON.stringify(deadExcluded)} in CORPUS_EXCLUDED or CORPUS_EXCLUDED_PREFIX match no tracked file. An exclusion that names nothing is a destination waiting to be used: a file written there later leaves every cap with no diff to this file.`)
    return 1
  }

  const deadWeight = [...NOT_A_DOCUMENT].filter((e) => !treeExts.has(e))
  if (deadWeight.length) {
    console.log(`\nFIXTURE VACUOUS: NOT_A_DOCUMENT lists ${deadWeight.length} extensions no tracked file has (${deadWeight.slice(0, 6).join(', ')}...). A blocklist that is not bounded by the tree is an allowlist wearing a different name.`)
    return 1
  }
  // ... and the same list bounded from BELOW. Without this, `NOT_A_DOCUMENT`
  // gaining `txt` or `mdc` -- extensions the tree HAS, so `deadWeight` stays
  // silent -- reopens the route at rc=0 with every other pin green. Measured as
  // an accepted mutant by the round-six review, which is why it is a pin and
  // not a sentence.
  pins += 1
  const floorBreach = NEVER_NOT_A_DOCUMENT.filter((e) => NOT_A_DOCUMENT.has(e))
  if (floorBreach.length) {
    console.log(`\nFIXTURE VACUOUS: NOT_A_DOCUMENT contains ${JSON.stringify(floorBreach)}, which this corpus has already established are document formats. Blocklisting one carries every file with that extension out of every cap at once, and the dead-weight assertion above cannot see it because the tree HAS those extensions.`)
    return 1
  }

  // THE RESOLUTION AND THE BARE PASS, driven against a SYNTHETIC listing. Both
  // routes are invisible on a healthy tree -- the three extensionless tracked
  // files are all data, and every basename the corpus cites resolves to a file
  // that is capped or excluded -- so neither had a witness, and the round-six
  // review measured the consequence: the bare pass could be unwired at its call
  // site, and a basename citation carried prose out of all five caps at rc=0,
  // both with the acceptance unchanged.
  pins += 3
  const synth = { set: new Set(['docs/NOTES', 'docs/only-here.md', 'a/dup.md', 'b/dup.md']) }
  synth.byBase = new Map()
  for (const f of synth.set) {
    const b = f.split('/').pop()
    if (!synth.byBase.has(b)) synth.byBase.set(b, [])
    synth.byBase.get(b).push(f)
  }
  const cited = citedTrackedPaths('see `only-here.md` and `docs/NOTES` and `dup.md`', synth)
  if (!cited.includes('docs/only-here.md')) {
    console.log(`\nFIXTURE VACUOUS: a document cited by its UNIQUE basename did not resolve to its tracked path (got ${JSON.stringify(cited)}). CLAUDE.md cites all thirty documents it indexes that way, and brief-citations.md calls it a resolvable citation, so this is the spelling the escape uses.`)
    return 1
  }
  if (!cited.includes('docs/NOTES')) {
    console.log(`\nFIXTURE VACUOUS: an extensionless tracked document went unreported (got ${JSON.stringify(cited)}), so the bare pass is unwired at its call site. The tree's only extensionless files are LICENSE, NOTICE and VERSION -- all data -- so this route has no witness on a healthy tree and deleting it costs nothing that any other pin measures.`)
    return 1
  }
  if (!cited.includes('a/dup.md') || !cited.includes('b/dup.md')) {
    console.log(`\nFIXTURE VACUOUS: an AMBIGUOUS basename resolved to fewer than all its candidates (got ${JSON.stringify(cited)}). Resolving it to NOTHING was a one-file escape: the colliding second file is the policy file itself, so a destination named after one left every cap in silence. The caller drops a candidate that is capped and measured, so reporting all of them reports only the one that is neither.`)
    return 1
  }
  // A listing carrying a pair that collides only when FOLDED -- the shape
  // `judge.md` and `tools/audit/round2/JUDGE.md` had in the real tree until this
  // branch deleted the second. No `pins` here: this builds the fixture, and the
  // assertions that use it count themselves. The one that used to sit here
  // pinned exact-case precedence, which resolving to all candidates made dead
  // code; it went with the code, and the count went with it.
  const foldPair = { set: new Set(['a/case.md', 'b/CASE.md', 'docs/only-here.md', 'docs/NOTES']) }
  foldPair.byBase = new Map()
  for (const f of foldPair.set) {
    const b = f.split('/').pop()
    if (!foldPair.byBase.has(b)) foldPair.byBase.set(b, [])
    foldPair.byBase.get(b).push(f)
  }
  // BOTH ambiguity branches, because they are separate code paths and only the
  // exact one had a witness: a mutant restoring "resolve a folded collision to
  // nothing" left all 55 pins green. `CaSe.md` matches no tracked file exactly,
  // so it reaches the fold, where it matches two -- and must report both.
  pins += 1
  const foldAmbig = citedTrackedPaths('see `CaSe.md`', foldPair)
  if (!foldAmbig.includes('a/case.md') || !foldAmbig.includes('b/CASE.md')) {
    console.log(`\nFIXTURE VACUOUS: a basename ambiguous only AFTER folding resolved to fewer than all its candidates (got ${JSON.stringify(foldAmbig)}). That is the same one-file escape as the exact case, one spelling further out.`)
    return 1
  }

  // `named-docs` must not be suppressible by the ledger, and nothing said so
  // until a mutant took it off the list with every pin still green. An ESCAPE
  // recorded as a known defect is not a closure -- the reason `budgets` and
  // `coverage` are there. Asserted on the set rather than driven through
  // `applyKnownBad`, because a synthetic finding's key is absent from the real
  // ledger and would survive whatever the list said: the drive would be the
  // vacuous one, and this is the honest cheap pin.
  pins += 1
  if (!NEVER_SUPPRESSED.has('named-docs')) {
    console.log(`\nFIXTURE VACUOUS: named-docs is suppressible by policy_known_bad.json. A document sitting outside every cap would become a recorded defect, which makes the corpus smaller by agreement rather than by measurement.`)
    return 1
  }


  const citedCase = citedTrackedPaths('see `ONLY-HERE.md`', synth)
  if (!citedCase.includes('docs/only-here.md')) {
    console.log(`\nFIXTURE VACUOUS: a basename resolved case-SENSITIVELY (got ${JSON.stringify(citedCase)}). namedDocMatches lowercases an extension before judging it, so \`POLICY-NOTES.MD\` survives the scan and must survive the resolution too; case-sensitive, it was dropped and the file went unreported at rc=0.`)
    return 1
  }

  // THE PRODUCTION CALL SITE, not the seam. Every assertion above drives
  // `citedTrackedPaths` directly, and NONE of them says `unmeasuredNamedDocs`
  // calls it: the round-seven review measured the call site reverted to its
  // pre-r7 inline `listing.set.has(rel)` form with all 49 pins green and the
  // basename escape reopened at rc=0. That is round six's own block re-created
  // one level up by the fix for it, which is this branch's most repeated shape.
  //
  // Differential, and against the LIVE corpus rather than a fixture. The
  // negative control is the exact-path-only scan -- the mutant itself, written
  // out -- and the assertion is that production reports strictly more than it.
  // A fixture could not pin this: the caller reads `policyFiles()`, so only the
  // real corpus reaches it.
  pins += 1
  const live = trackedFiles()
  const exactOnly = new Set()
  for (const src of policyFiles()) {
    const raw = read(src)
    if (raw == null) continue
    for (const m of [...namedDocMatches(raw), ...bareNameCandidates(raw)]) if (live.set.has(m)) exactOnly.add(m)
  }
  const viaBasename = driveND({ files: {} }).map((f) => f.where).filter((w) => !exactOnly.has(w))
  if (!viaBasename.length) {
    console.log(`\nFIXTURE VACUOUS: with every document uncapped, unmeasuredNamedDocs reported nothing that the exact-path scan alone would not have reported. Either the caller no longer resolves basenames -- the escape, reopened -- or this corpus has stopped citing documents that way, in which case the assertion is measuring nothing and must be replaced rather than deleted.`)
    return 1
  }

  const ndFull = driveND({ files: Object.fromEntries(policyFiles().map((f) => [f, 1e9])) })
  const stray = ndFull.filter((f) => !corpusExcluded(f.where))
  if (stray.length && stray.length >= ndBare.length) {
    console.log(`\nFIXTURE OVER-FIRES: checkNamedDocs reported ${stray.length} finding(s) with the whole corpus capped, e.g. ${JSON.stringify(stray[0].where)}`)
    return 1
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
    for (const sub of spec.mustNot ?? []) {
      pins += 1
      if (!(msgs[cls] ?? []).some((m) => m.includes(sub))) continue
      console.log(`\nFIXTURE OVER-FIRES: check '${cls}' produced an error saying ${JSON.stringify(sub)}, which it must never collect`)
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
  for (const cls of REQUIRED_SILENT) {
    pins += 1
    const noisy = silent[cls] ?? []
    if (!noisy.length) continue
    console.log(`\nFIXTURE OVER-FIRES: check '${cls}' produced ${noisy.length} finding(s) on its HEALTHY fixture, e.g. ${JSON.stringify(noisy[0].message.slice(0, 120))}`)
    rc = 1
  }
  if (!rc) console.log(`\nFIXTURE ok: ${found.length} error(s) hold ${pins} pins across ${Object.keys(REQUIRED_ROT).length} check classes on fixtures/policy-rot/ and fixtures/policy-loop/`)
  return rc
}

// The loop fixtures, loaded once. Returns null rather than throwing so the
// acceptance reports a missing fixture directory as VACUOUS -- the same way it
// already reports a missing policy-rot/ -- instead of dying with a stack trace
// that reads like a bug in the linter.
function loopFixtures() {
  const dir = '.claude/workflows/fixtures/policy-loop'
  try {
    const subjects = read(`${dir}/merged-subjects.txt`).split('\n').filter(Boolean)
    const payloads = JSON.parse(read(`${dir}/pr-payloads.json`))
    const prs = mergedPRs(subjects)
    const fetched = new Map()
    for (const [k, v] of Object.entries(payloads)) {
      if (k.startsWith('_')) continue
      fetched.set(k, v)
    }
    const healthy = new Set(payloads._healthy ?? [])
    const classes = verdictClasses()
    if (!classes) return null
    return {
      prs,
      healthyPrs: prs.filter((p) => healthy.has(p.pr)),
      fetched,
      classes,
      dispositionsRotten: read(`${dir}/dispositions-rotten.md`),
      dispositionsHealthy: read(`${dir}/dispositions-healthy.md`),
      sunsetRot: [{ file: `${dir}/sunset-rules.md`, text: read(`${dir}/sunset-rules.md`) }],
      sunsetHealthy: [{ file: `${dir}/sunset-healthy.md`, text: read(`${dir}/sunset-healthy.md`) }],
      friction: statsHistogram(prs, fetched, classes).friction,
      // Empty on purpose: the guard being pinned is "a detector with zero
      // recorded fires is held", and a fixture that inherited the real ledger's
      // fires would pin it only for as long as that ledger stayed the same shape.
      fires: new Set(),
      // Fixed, so `SUNSET: 2020-01-01` is past on every machine and every day,
      // and `2099-01-01` is future. A `new Date()` here would make the
      // acceptance's verdict depend on the calendar.
      today: new Date('2026-09-07T00:00:00Z'),
    }
  } catch {
    return null
  }
}

// --record-known-bad. `measuredRecord` says whether this reseed actually read
// merged history (it did iff --since was passed). When it did not, every
// `record|` entry is CARRIED FORWARD untouched: a reseed that measured no
// history has no evidence those defects were fixed, and dropping them would let
// an undispositioned merge back in unseen -- the silent drain the whole ledger
// exists to prevent, arriving through the tool that maintains it.
function cmdRecord(findings, { measuredRecord = false } = {}) {
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
  if (!measuredRecord) {
    for (const [k, c] of before) if (RECORD_KEY(k) && !counts.has(k)) counts.set(k, c)
  }
  const after = [...counts.keys()].sort().map((key) => ({ key, count: counts.get(key) }))
  const added = after.filter((e) => !before.has(e.key))
  const dropped = [...before.keys()].filter((k) => !counts.has(k))
  const moved = after.filter((e) => before.has(e.key) && before.get(e.key) !== e.count)
  doc._comment =
    'Defects present when policy_lint landed, each with its recorded number of occurrences. A finding not listed here is an error; MORE occurrences of a listed one is an error; fewer is an error until re-recorded; an entry that no longer fires is an error. The list may only shrink. Regenerate with --record-known-bad; growing it is a deliberate edit a reviewer reads.'
  const at = recordedAtSha()
  if (!at) {
    console.log(`refusing to record: no merge base with origin/main, so ${KNOWN_BAD_FILE} would carry a provenance SHA nobody can resolve`)
    process.exit(2)
  }
  doc.recorded_at = at
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

// A HOOK THAT IS NOT WIRED, OR WIRED TO A FILE THAT IS NOT THERE, IS INDISTIN-
// GUISHABLE FROM ONE THAT WORKS. It fires silently, or not at all, and the seat
// it was written to catch never learns either way -- `defect-root-cause.md`
// records that this corpus already claimed a hook it had never built.
//
// TWO HALVES, and the first was missing when this sentence was first written.
// Iterating `.claude/settings.json` can only judge what is IN it: deleting an
// entry left this reporting `HOOKS ok: 2 wired hook(s)` and rc=0, and pointing
// `PreToolUse` at `session-start.sh` left it green at three. A check over a set
// the defect can shrink is a check over an empty set in the limit. So REQUIRED
// pins the roster by MEMBERSHIP -- event AND script, not a count, because a
// count is satisfied by a duplicate and by a swap (#614 round 3).
//
// The second half: for every `command` in the file, the script exists, and
// `--self-test` exits 0. The self-test is the substance --
// existence alone would have passed the first draft of `pre-edit.sh`, whose
// python read its own heredoc as the payload and fell open on every path it was
// written to refuse. Nine ALLOW controls passed. Only the refusals caught it.
function cmdHooks(settingsPath) {
  const rel = settingsPath || '.claude/settings.json'
  const abs = path.join(ROOT, rel)
  let parsed
  try {
    parsed = JSON.parse(fs.readFileSync(abs, 'utf8'))
  } catch (e) {
    console.log(`HOOKS: ${rel} does not parse: ${e.message}`)
    return 1
  }
  const rows = []
  for (const [event, groups] of Object.entries(parsed.hooks || {})) {
    for (const g of groups || []) {
      for (const h of g.hooks || []) {
        // The command is a shell line with $CLAUDE_PROJECT_DIR and quoting in
        // it. The SCRIPT is what this checks, so pull the one repository path
        // out of the line rather than trying to run the line.
        const m = String(h.command || '').match(/[.\w/-]*\.claude\/hooks\/[\w.-]+\.sh/)
        if (!m) { rows.push({ event, script: h.command || '(none)', verdict: 'UNREADABLE', why: 'no .claude/hooks/*.sh path in the command line' }); continue }
        const script = `.claude/hooks/${m[0].split('/').pop()}`
        if (!fs.existsSync(path.join(ROOT, script))) { rows.push({ event, script, verdict: 'MISSING', why: 'the command names a file that is not in the tree' }); continue }
        let out = ''
        let code = 0
        try {
          out = execFileSync('bash', [script, '--self-test'], { cwd: ROOT, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] })
        } catch (e) {
          code = e.status === undefined ? 1 : e.status
          out = `${e.stdout || ''}${e.stderr || ''}`
        }
        const tail = out.trim().split('\n').pop()
        rows.push({ event, script, verdict: code === 0 ? 'ok' : 'SELF-TEST FAILED', why: tail })
      }
    }
  }
  if (!rows.length) {
    console.log(`HOOKS: ${rel} wires no hooks at all. A settings file with an empty \`hooks\` key reads exactly like one that works.`)
    return 1
  }
  // Each hook stands in for a rule whose cheaper detector this corpus otherwise
  // pays CI or a release stamp for; losing one silently is losing that rule.
  const REQUIRED = [
    ['SessionStart', '.claude/hooks/session-start.sh'],
    ['PreToolUse', '.claude/hooks/pre-edit.sh'],
    ['Stop', '.claude/hooks/stop-selfcheck.sh'],
  ]
  const absent = REQUIRED.filter(([e, sc]) => !rows.some((r) => r.event === e && r.script === sc))
  for (const [e, sc] of absent) {
    rows.push({ event: e, script: sc, verdict: 'NOT WIRED', why: `${rel} wires no ${e} hook running this script, so the rule it stands in for is enforced nowhere before CI` })
  }
  for (const r of rows) console.log(`  ${r.verdict.padEnd(17)} ${r.event.padEnd(13)} ${r.script}  ${r.why}`)
  const bad = rows.filter((r) => r.verdict !== 'ok')
  console.log(bad.length
    ? `\nHOOKS REFUSED: ${bad.length} of ${rows.length} hook(s) checked is not wired, missing, unreadable, or fails its own --self-test`
    : `\nHOOKS ok: ${rows.length} wired hook(s) exist and pass their own --self-test`)
  return bad.length ? 1 : 0
}

// `--since <ref>` takes a value, so its value must not fall through to the
// positional list and be linted as a file path. Parsed explicitly rather than by
// filtering on a leading `--`.
function parseArgs(argv) {
  const flags = []
  const positional = []
  let since = null
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--since') {
      since = argv[++i] ?? null
      continue
    }
    if (a.startsWith('--since=')) {
      since = a.slice('--since='.length)
      continue
    }
    ;(a.startsWith('--') ? flags : positional).push(a)
  }
  return { flags, positional, since }
}

// ---------------------------------------------------------------------------
// The loop-mode drivers. Each prints and then exits: none of them lints the
// corpus, and none of them runs the acceptance, which belongs to the CI path.

function requireSince(since, mode) {
  if (since) return since
  console.log(`${mode} needs a window: pass --since <ref>. It measures pull requests merged in <ref>..origin/main, and without a ref there is no window to measure.`)
  process.exit(2)
}

function cmdRecordDispositions(since) {
  const prs = mergedPRs(mergedSubjects(since))
  const text = DISPOSITION_FILES.map((f) => read(f) ?? '').join('\n')
  const all = checkRecord(prs, text)
  const applied = applyKnownBad(all, RECORD_KEY)
  console.log(`RECORD: ${prs.length} merged pull request(s) in ${since}..${mainRef()}; ${all.length} without a disposition in ${DISPOSITION_FILES.join(' or ')}`)
  printFindings(applied.live)
  console.log(`\nKNOWN-BAD: ${applied.suppressed} of ${applied.total} recorded record-class defect(s) still present, in ${applied.occurrences} recorded occurrence(s)`)
  const errors = applied.live.filter((f) => f.severity === 'error').length
  console.log(`\nTOTAL: ${errors} error(s) over ${prs.length} merged pull request(s)`)
  process.exit(errors > 0 ? 1 : 0)
}

function cmdStats(since) {
  const prs = mergedPRs(mergedSubjects(since))
  const classes = verdictClasses()
  if (!classes) {
    console.log(`STATS: could not read the verdict grammar from ${WAVE_SCRIPT}; classifying nothing rather than against a list typed here.`)
    process.exit(0)
  }
  const { fetched, fetchError } = fetchWindow(prs)
  console.log(`STATS: ${prs.length} merged pull request(s) in ${since}..${mainRef()}; verdict grammar ${JSON.stringify(classes)} read from ${WAVE_SCRIPT}`)
  if (!fetchError) {
    const { verdicts, friction } = statsHistogram(prs, fetched, classes)
    for (const [label, hist] of [['verdict class', verdicts], ['friction rule id', friction]]) {
      console.log(`\n${label}:`)
      const rows = [...hist.entries()].sort((a, b) => b[1] - a[1])
      if (!rows.length) console.log('  (none in this window)')
      for (const [k, n] of rows) console.log(`  ${String(n).padStart(4)}  ${k}${n >= FRICTION_THRESHOLD ? '   <- at or over threshold' : ''}`)
    }
  }
  const found = statsFindings({ prs, fetched, fetchError, classes })
  console.log(`\nthreshold: ${FRICTION_THRESHOLD} or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.`)
  printFindings(found)
  console.log(`\nWOULD OPEN: ${found.filter((f) => f.message.startsWith('would open')).length} issue(s)`)
  process.exit(0)
}

function cmdSunset(since) {
  const prs = mergedPRs(mergedSubjects(since))
  const classes = verdictClasses()
  const { fetched, fetchError } = fetchWindow(prs)
  const friction = fetchError || !classes ? null : statsHistogram(prs, fetched, classes).friction
  const fires = detectorFires(friction)
  const rows = policyFiles().map((f) => ({ file: f, text: read(f) }))
  const found = checkSunset(rows, { friction, fires, today: new Date() })
  console.log(`SUNSET: ${rows.length} policy file(s) over ${since}..${mainRef()}${fetchError ? `; no friction data (${fetchError}), so honour rules are not evaluated` : ''}`)
  const propose = found.filter((f) => f.propose)
  const held = found.filter((f) => !f.propose)
  console.log(`\nproposed for sunset (${propose.length}) -- this mode changes nothing:`)
  if (!propose.length) console.log('  (none)')
  for (const f of propose) console.log(`  ${f.where}: ${f.message}`)
  console.log(`\nheld (${held.length}):`)
  if (!held.length) console.log('  (none)')
  for (const f of held) console.log(`  ${f.where}: ${f.message}`)
  process.exit(0)
}

function main() {
  const argv = process.argv.slice(2)
  const { flags, positional, since } = parseArgs(argv)
  const has = (f) => flags.includes(f)
  const derived = derivations()

  if (argv[0] === '--list') return cmdList(), process.exit(0)

  // Exact-string, and --record-known-bad is tested FIRST, so the reseed can
  // never be reached by a typo of --record or the other way round.
  if (has('--record-known-bad') && has('--record')) {
    console.log('--record and --record-known-bad are different modes: the first refuses an undispositioned merge, the second reseeds the ledger. Pass one.')
    process.exit(2)
  }
  if (has('--record')) return cmdRecordDispositions(requireSince(since, '--record'))
  if (has('--stats')) return cmdStats(requireSince(since, '--stats'))
  if (has('--sunset')) return cmdSunset(requireSince(since, '--sunset'))

  const all = policyFiles()
  const files = positional.length ? positional.map((a) => path.relative(ROOT, path.resolve(a))) : all
  const defaultRun = !positional.length

  if (has('--budgets')) return cmdBudgets(files), process.exit(0)
  // `--hooks` takes an OPTIONAL settings path, and `parseArgs` puts a bare value
  // in `positional` -- so the path arrives there, and its absence leaves
  // `cmdHooks` on its own default. Written in the loop branch's shape: that
  // branch renamed main's argument array to `argv` and reads flags through
  // `has()`, so the merge follows the rename rather than reviving `args`.
  if (has('--hooks')) process.exit(cmdHooks(positional[0]))
  if (has('--pr-body')) process.exit(cmdPrBody(argv))

  let findings = []
  for (const f of files) findings.push(...lintFileGuarded(f, derived))
  if (defaultRun) {
    for (const fn of CORPUS_CHECKS) findings.push(...fn(all))
  }

  if (has('--record-known-bad')) {
    // A reseed may also re-measure the record class, but only when it was given
    // a window: `--record-known-bad --since <ref>`.
    if (since) findings.push(...checkRecord(mergedPRs(mergedSubjects(since)), DISPOSITION_FILES.map((f) => read(f) ?? '').join('\n')))
    return cmdRecord(findings, { measuredRecord: !!since }), process.exit(0)
  }

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
  if (has('--report')) {
    const by = {}
    for (const f of findings) by[f.check] = (by[f.check] || 0) + 1
    console.log('\nby check:', JSON.stringify(by))
    console.log('derivations:', JSON.stringify(derived))
  }
  const rc = defaultRun ? assertAcceptance(derived) : 0
  process.exit(errors > 0 || rc ? 1 : 0)
}

// Exported for `policy_lint_mutants.mjs`, which empties one corpus check at a
// time and demands this acceptance go red. The mutation lane must learn WHICH
// checks exist from production rather than from a list of its own: a second
// copy of the enumeration is the same defect one level up, and a regex over
// this file's source would re-derive it from spelling. `CORPUS_CHECK_NAMES` is
// the one enumeration, `assertAcceptance` is the thing under test, and
// `derivations` is its only argument.
export { CORPUS_CHECK_NAMES, assertAcceptance, derivations }

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
