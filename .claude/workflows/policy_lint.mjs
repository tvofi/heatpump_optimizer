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
//   ... | node .claude/workflows/policy_lint.mjs --corpus-filter  # keep the policy paths
//   node .claude/workflows/policy_lint.mjs <files...> # lint just these
//   node .claude/workflows/policy_lint.mjs --record-known-bad   # reseed the ratchet
//   node .claude/workflows/policy_lint.mjs --pr-body <file> --head <sha> [--title t] [--red names] [--paths-file f] [--author login]
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
import { checkCounts, derivations, liveRequiredContexts, liveRequiredContextsWhy, checkRequiredContexts, requiredContextsDrift } from './counts.mjs'
import { inspectRender } from './render_md.mjs'

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

function git(args, { allowFail = false, env, quiet = false } = {}) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, ...(env ? { env } : {}),
      ...(quiet ? { stdio: ['ignore', 'pipe', 'pipe'] } : {}) })
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
    _mcpTools = new Set()
    for (const block of raw.matchAll(/const GH(?:_[A-Z]+)? = `([\s\S]*?)`/g)) {
      for (const m of block[1].matchAll(/\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b/g)) {
        _mcpTools.add(m[1])
      }
    }
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
  // The harness-neutral entry point: ZCode and Codex auto-load a root
  // AGENTS.md where Claude Code loads CLAUDE.md. It defers to CLAUDE.md and
  // states no policy of its own, but it is seat-facing text a harness loads
  // before anything else, so it is measured and capped like the rest of the
  // corpus rather than sitting outside every cap as a door prose can leave
  // through. Widening this list is the owner's decision; this entry was made
  // by the owner's instruction in the pull request that added it.
  /^AGENTS\.md$/,
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
const CORPUS_CHECK_NAMES = ['checkIndex', 'checkDuplicates', 'checkBudgets', 'coverageOverTree', 'namedDocsOverTree', 'citationPresenceOverTree', 'orphanCapsOverTree', 'requiredContextsOverTree', 'checkProvenance', 'rowFreezeOverPlan', 'ruleBindingOverTree']

// THE RECORD MODE'S CHECKS, enumerated HERE beside the corpus list rather than
// in the mutation lane, for the reason the corpus list gives about itself: a
// second copy is the same defect one level up, and a regex over this file's
// source re-derives the enumeration from spelling.
//
// `cmdRecordDispositions` prints four lines -- `RECORD:`, `TABLES:`, `CAPS:`
// and `RENDER:` -- and each is driven inside `assertAcceptance` against a
// fixture under fixtures/policy-loop/, so a check emptied outright is already
// refused THERE. That is not the question this list is for. The corpus lane's
// whole argument is that an acceptance cannot derive its own drive loop, and
// the argument does not weaken one mode over: nothing established that the
// drive which is supposed to catch an emptied `checkTableSplit` is the drive
// that runs. #683. `checkRender` is the fourth (#682).
//
// An entry carries its FILE and its mutation KIND, because two of the five are
// not functions in this module:
//
//   - `checkCounts` and the regex list its `caps` rule scans both live in
//     counts.mjs, so mutating them means mutating that file and pointing this
//     one's import at the copy.
//   - `CAP_RES` is not a function at all, and emptying it is a DIFFERENT
//     mutation from emptying the check: `checkCounts` still runs, still walks
//     COUNT_RULES, and the `caps` rule simply scans every line with no regex.
//     Silent, and on a corpus that states no cap it is indistinguishable from
//     a correct run -- which is the shape decisions/0002 is about.
//
// WHAT THIS DOES NOT COVER, on the same terms as the corpus list above: it is a
// list, not a registry, so a check the record mode grows and nobody adds here
// is mutated by nothing and this file cannot tell. The converse IS covered, and
// by the lane rather than by an assertion here: an entry the record mode has
// stopped driving survives its own emptying and is reported `ACCEPTED`.
const LOOP_CHECK_NAMES = [
  { name: 'checkRecord', file: 'policy_lint.mjs', kind: 'return' },
  { name: 'checkTableSplit', file: 'policy_lint.mjs', kind: 'return' },
  { name: 'checkRender', file: 'policy_lint.mjs', kind: 'return' },
  // The fifth loop output: the conditional fetch-failure skip line, printed by
  // both `--record` and `--stats` (enumSkipLine). It produces no findings, so
  // the acceptance drives its SHAPE directly -- the one output whose deletion
  // leaves every count green and only the marker's own pin red.
  { name: 'enumSkipLine', file: 'policy_lint.mjs', kind: 'return' },
  // The sixth: the window guard's OTHER half (badRefLine), printed by every
  // mode that takes `--since`. Same reason as the fifth -- it produces no
  // findings, so the acceptance drives its shape directly -- and a different
  // arm: `enumSkipLine` covers a fetch that died, this one a ref that never
  // resolved, which reaches an empty window one step earlier and with no
  // marker of its own until this existed.
  { name: 'badRefLine', file: 'policy_lint.mjs', kind: 'return' },
  { name: 'checkCounts', file: 'counts.mjs', kind: 'return' },
  { name: 'CAP_RES', file: 'counts.mjs', kind: 'array' },
  // The pr-body contract and the one friction grammar it shares with `--stats`.
  // Neither is a record-mode check; both are driven inside the same acceptance
  // and were in the position the corpus checks were in before this lane
  // existed -- an emptied `checkPrBody` was refused by eight fixture pins and
  // nothing asked whether the drive that holds those pins is the drive that
  // runs. Emptying `frictionEntries` leaves the contract accepting every
  // `## Friction` section and the histogram keying nothing, which is the
  // silent shape the shared parser replaced.
  { name: 'checkPrBody', file: 'policy_lint.mjs', kind: 'return' },
  { name: 'frictionEntries', file: 'policy_lint.mjs', kind: 'return' },
  // The histogram's KEYING, which is a second silent shape beside the grammar's:
  // `frictionEntries` decides what an entry IS, `frictionKey` decides which key
  // it counts under, and an emptied keyer leaves every entry parsed, every
  // count printed, and every rule filed under whichever spelling a seat typed.
  // That is the defect this entry arrived with, and it was invisible to the
  // whole acceptance until the keying window pinned it.
  { name: 'frictionKey', file: 'policy_lint.mjs', kind: 'return' },
  // The seventh: `--sunset`'s marker census (sunsetMarkerLine), printed by the
  // third loop mode. Same shape as the fifth and sixth -- no findings, so the
  // acceptance drives its SHAPE and both ends of it -- and the reason it exists
  // is that this class's zero was the one print in the corpus that a reader
  // could not tell from a measurement (#1469, D11-03).
  { name: 'sunsetMarkerLine', file: 'policy_lint.mjs', kind: 'return' },
]

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
  // The living handover left POLICY_GLOBS by the owner's decision of 2026-09-16
  // (#201 comment 5702401684): it carries state, not rules, changes with nearly
  // every record PR, and so owes no `## Approval` and no code-owner review. Its
  // cap went with it. The residual risk is ADRs' below: prose moved into it
  // leaves the corpus, and only a reviewer reading the diff sees that.
  'docs/HANDOVER.md',
  // The architecture decision records. An ADR states a decision ALREADY TAKEN
  // and the measurement behind it; it binds no seat and no seat is sent to one
  // to learn what it must do. The corpus machinery is built for text that binds
  // someone: `checkIndex` refuses a policy file `CLAUDE.md` does not name,
  // because "the index is the only way a seat finds a policy file" -- and
  // naming them all here would push the ALWAYS-LOADED set, the one number this
  // audit exists to drive down, past its cap to carry documents nobody must
  // read. Measured before choosing, and stated as a SHAPE rather than a count,
  // because the count is a function of how many decisions exist and this comment
  // has already carried three stale readings -- 14, then 24, then 24 again after
  // the list grew. Bringing `docs/decisions/` under POLICY_GLOBS reports, for
  // every decision, one [budgets] error (no cap) and one [index] error (CLAUDE.md
  // does not name it), plus [duplicates] between records that share a paragraph
  // and [citations] below. The total therefore grows with the directory, which is
  // itself half the argument. Re-derive it rather than reading it here: put the
  // glob back, delete the exclusion entries, and run the linter.
  // The five [citations] are named one by one rather than summarised, because
  // the first version of this sentence said they were all 0003's and three of
  // them are: `docs/Zednotes.md`, `NOT_A_DOCUMENT` and `NEVER_NOT_A_DOCUMENT`,
  // correct BECAUSE 0003 describes an experiment over files and symbols that do
  // not exist. The fourth is 0005 citing `docs/plan-2026-09-governance-audit.md`
  // and is a TRUE positive: that plan is archived on a branch and is not in this
  // tree. The fifth is 0006 citing `POLICY_GLOBS`, which exists a few lines
  // above here. `git grep -w POLICY_GLOBS` finds three tracked files, and
  // `symbolElsewhere` below excludes all three by three different clauses of
  // its own inline list: this file by `:!.claude`, ADR 0002 by `...spec` (a
  // policy file cannot satisfy a citation, and once ADRs are policy files --
  // the state being measured -- 0002 is one), and 0006 itself by `exceptRel`.
  // Two are independently sufficient: dropping `:!.claude` removes this error,
  // and so does un-excluding 0002. Neither total is written here -- the previous
  // two versions of this sentence carried one, both went stale, and the second
  // went stale in the same commit that removed the count from the sentence above
  // it. Named this precisely because the
  // sentence has been wrong twice, once as "all five are 0003's" and once as
  // `SYMBOL_GREP_EXCLUDE`, which this file imports and never calls on this
  // path. So three of the five are a check applied to the wrong kind of text,
  // one is the check working, and one is three exclusions meeting a document
  // that cites into all of them. The count grows with the directory, which is
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
  'docs/decisions/0007-after-this-session-owner-approval-per-pull-request.md',
  'docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md',
  // The W4D-G9 decision record (#954): agent identities for author and
  // approver, no separate human approval, the approver created before the
  // rule. Named one by one per the rule above, under the 2026-09-14 session
  // grant (#201 comment 5670246622), which covers the policy change. An
  // uncited ADR needs no line -- measured again on this branch: the file
  // added and cited by nothing keeps TOTAL at 0 -- but the line is owed the
  // moment a capped file names it, and the first will be the handover
  // recording that merge, so it is paid here rather than left to redden the
  // record seat that writes it.
  'docs/decisions/0009-agent-identities-for-author-and-approver.md',
  // The merge-method record (#1041): `main` takes a pull request as a merge
  // commit, the owner's ruling of 2026-09-16. Named one by one per the rule
  // above, and owed rather than optional -- `tools/audit/briefs/orchestrator.md`
  // cites it and is capped, so `checkNamedDocs` reports it without this line.
  // THAT SENTENCE SAID THREE FILES until PR #1117's review measured it: it named
  // `.claude/workflows/web-fragments.md` and `tools/audit/briefs/fixer.md` too,
  // and neither cites the record any more. The count rotted from three to one
  // with nothing watching -- which is this entry's own thesis, arriving as a
  // wrong sentence in the comment that states it. A prose count of citers is a
  // measurement and decays; only the ONE the check below carries is maintained,
  // and it is carried for the message rather than as the key. That is the whole enforcement a decision citation has here: the cited
  // path must resolve (`checkCitations`) and must be classified (this list).
  // The citation being REMOVED again is the third direction, and it was a clean
  // zero until `checkCitationPresence` below: this entry is listed there, so
  // dropping the last policy-file citation of it now refuses.
  'docs/decisions/0010-merge-commits-on-main.md',
  // The author-identity record (#201 comment 5744682317): pull requests are
  // authored by the `hpo-author` App, seats are LOCAL-ONLY, the retired
  // account never writes again. Named one by one per the rule above, and owed
  // rather than optional: `tools/audit/briefs/fixer.md` and
  // `tools/audit/briefs/fix-review.md` cite it and are capped.
  'docs/decisions/0011-app-authored-identity.md',
  // The process-diet record (round-8 convergence programme, item F6): the
  // process moratorium until 2026-10-31, the D11/D13-every-third-round and
  // D5/D6-alternate-rounds cadence, the one-enforcement-point rule, and
  // D14's stop rule. Named one by one per the rule above. Cited by nothing
  // in the capped corpus as of this pull request -- TOTAL stays at 0 for
  // this entry -- so no capped file's `checkNamedDocs` count depends on it
  // yet; the line is paid here anyway, per this list's own rule that the
  // next ADR costs a line regardless of citation.
  'docs/decisions/0012-process-diet-and-round-cadence.md',
  // Round-evidence exclusions (finder reports and round baselines) are DATA,
  // not source: they live in .claude/workflows/corpus_excluded.json and are
  // merged into this set below. They are not here because the `policy-docs`
  // job's restore step (#1403) rewrites this file from the base commit before
  // grading, so a round could not ship its evidence and its exclusions in the
  // same branch -- the catch-22 the data file exists to break.
])

// The round-evidence part of the exclusion set is read from a DATA file rather
// than written into the Set above, so a round can ship its evidence files and
// their exclusions in the same branch: the `policy-docs` job's restore step
// (#1403) rewrites `.claude/workflows/*.mjs` from the base commit before
// grading, which would erase a round block written here, while a `.json` data
// file is outside that pathspec. This is the shape the #1403 fix's own comment
// names for `policy_budgets.json`, `policy_known_bad.json` and
// `cfr_exclusions.json`: a grader's criteria are data, and a fixture's expected
// outcome has to be the data under test.
//
// Fail-closed by construction, so no separate pin is needed for the read: a
// missing or unparseable file, or a non-array `excluded`, merges nothing, and
// the cited-but-unexcluded evidence files then re-arm `named-docs` on the
// production run -- which is the same refusal that would have fired on the
// branch that added them, one restore step later. The `deadExcluded` pin below
// still holds every merged entry to a tracked file, so a vacuous entry in the
// data file is refused exactly as a vacuous entry in the Set was.
const CORPUS_EXCLUDED_DATA = '.claude/workflows/corpus_excluded.json'
for (const rel of roundEvidenceExclusions()) CORPUS_EXCLUDED.add(rel)

function roundEvidenceExclusions() {
  const raw = read(CORPUS_EXCLUDED_DATA)
  if (raw == null) return []
  let parsed
  try {
    parsed = JSON.parse(raw)
  } catch {
    return []
  }
  const entries = parsed?.excluded
  return Array.isArray(entries) ? entries.filter((e) => typeof e === 'string') : []
}

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

// ---------------------------------------------------------------------------
// citation-presence. THE OTHER DIRECTION OF A CITATION, and until this check it
// was a measured clean zero. `checkCitations` above asks whether a citation
// RESOLVES; `checkNamedDocs` asks whether a cited document is CLASSIFIED. Both
// read the citation that is in front of them, so both are silent about a
// citation that is no longer there. #1058 drove all four arms and published the
// table: with the ADR removed and the citation left, rc is non-zero; with the
// `CORPUS_EXCLUDED` line removed, rc is non-zero; with THE CITATION REMOVED and
// the ADR left, `TOTAL: 0 error(s)`. The comment on the 0010 entry above said so
// at the site -- "Nothing detects the citation being REMOVED again" -- and #1079
// counted the sentence three times before it was closed here.
//
// WHAT IS PINNED, and it is deliberately not "every citation in the corpus".
// A citation deleted along with the sentence that carried it is ordinary
// editing, and a check that refused it would refuse every deletion pass this
// corpus runs -- the caps exist to make seats delete. What is pinned is the
// much smaller set of citations that BOUGHT something: an entry in
// CORPUS_EXCLUDED under the rule the 0010 comment states, "the line is owed the
// moment a capped file names it". That exclusion is EARNED by the citation, and
// when the last citation goes the earning goes with it, leaving an unearned
// exclusion -- which the `deadExcluded` pin already calls "a destination waiting
// to be used", the same defect one axis over. So the declaration is the pin, and
// an ADR that nobody cites needs no line here, exactly as it needs none there.
//
// ANY POLICY FILE SATISFIES IT, not the recorded one. The recorded citer is
// carried for the MESSAGE only: a citation moved from one policy file to
// another is a legitimate edit with the same content, and keying on the
// recorded file would report it as rot. Driven both ways in `assertAcceptance`,
// because a check keyed on the recorded citer passes every arm that does not
// move one.
const EXCLUDED_BECAUSE_CITED = new Map([
  // #1041's merge-method record. Its CORPUS_EXCLUDED line was paid because
  // `tools/audit/briefs/orchestrator.md` cites it; that is the citation whose
  // disappearance nothing saw.
  ['docs/decisions/0010-merge-commits-on-main.md', 'tools/audit/briefs/orchestrator.md'],
])

// Injectable for the reason `uncoveredPolicyFiles` states about itself: this
// check's property is FALSE on a healthy tree, so the tree gives it no witness
// and it would be deletable in silence. Pairs rather than a file list, so an
// arm can move a citation from one policy file to another without writing to
// the working tree.
let citationPresenceSource = () => undefined

function corpusCitationTexts() {
  return policyFiles().map((f) => [f, read(f) ?? ''])
}

function citationPresenceOverTree() {
  return checkCitationPresence(citationPresenceSource())
}

function checkCitationPresence(pairs) {
  const entries = pairs !== undefined ? pairs : corpusCitationTexts()
  const listing = trackedFiles()
  const cited = new Set()
  for (const [, raw] of entries) {
    for (const rel of citedTrackedPaths(raw, listing)) cited.add(rel)
  }
  const out = []
  // THE REMEDY IS DERIVED, NOT WRITTEN DOWN, because its last clause depends on
  // how many entries are left. "Delete both lines" is the whole remedy while a
  // second entry survives; on the LAST entry the same two deletions leave a
  // wired check over an empty map, which `policy_lint_mutants.mjs` refuses as
  // DELETABLE IN SILENCE -- `governance.yml`'s mutation step, red, for a seat
  // that followed the message literally. So the message carries the rest of the
  // withdrawal exactly when it is owed, and `assertAcceptance` refuses the
  // half-done state as well, so neither a seat that skips the message nor one
  // that skips the acceptance lands a vacuous check.
  const lastOne = EXCLUDED_BECAUSE_CITED.size === 1
  const retire = lastOne
    ? ` This is the LAST entry, so those two deletions RETIRE THE CLASS and are not the whole remedy: in the same commit also remove \`citationPresenceOverTree\` from \`CORPUS_CHECK_NAMES\` and from the \`CORPUS_CHECKS\` push, and the \`citation-presence\` rows from \`CHECKS\` and from \`NEVER_SUPPRESSED\`. A wired check over an empty map measures nothing, and \`policy_lint_mutants.mjs\` refuses it.`
    : ''
  for (const [rel, recorded] of EXCLUDED_BECAUSE_CITED) {
    if (cited.has(rel)) continue
    out.push({
      severity: 'error',
      check: 'citation-presence',
      where: rel,
      message: `no policy file cites it any more. Its CORPUS_EXCLUDED line in policy_lint.mjs was earned by the citation in ${recorded}, and an excluded document nobody cites is a destination waiting to be used -- prose moved into it leaves the corpus and buys headroom in every cap at once, with no diff to policy_lint.mjs for a reviewer to see. Restore the citation, or delete BOTH this entry and the exclusion line in the same commit.${retire} Any policy file satisfies this check, so a citation moved to another one is not a failure; ${recorded} is named here because it is where the line was paid, not because the check reads it.`,
    })
  }
  return out
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

// The live required-context set (#957), in the counts class: the derivation is
// an API away rather than a tree artifact, so it is fetched here (memoized in
// counts.mjs) and two things are policed against it -- the corpus's literals
// and the recorded-shape fixture. See counts.mjs for why a fetch failure is a
// printed skip and never a finding, and why the derivation reads the branch
// endpoint AND the ruleset objects.
//
// THE SITE LIST is the files that assert the merge boundary's state: the
// workflow comments, the plan of record, the decision records, the handover.
// It is a list and not a registry -- a file nobody lists here is unmeasured by
// this check, the same residual the corpus list above carries, and for the
// same reason: nothing inside a program can pin its own coverage.
const REQUIRED_CONTEXT_FIXTURE = '.claude/workflows/fixtures/required-contexts.json'
const REQUIRED_CONTEXT_SITE = /^(?:\.github\/workflows\/[A-Za-z0-9_.-]+\.yml|docs\/plan-[A-Za-z0-9-]+\.md|docs\/decisions\/[0-9]{4}-[A-Za-z0-9-]+\.md|docs\/HANDOVER\.md)$/

let requiredContextsSource = null
let requiredContextsFixtureSource = null
let requiredContextsSitesSource = null

function requiredContextsOverTree() {
  // The fixture FIRST, unconditionally: a missing or unparseable baseline is a
  // tree defect regardless of whether the API answered, and ordering the fetch
  // first would hide it behind the skip whenever both fail at once.
  const fixtureRaw = requiredContextsFixtureSource ? requiredContextsFixtureSource() : read(REQUIRED_CONTEXT_FIXTURE)
  if (fixtureRaw == null) {
    return [{
      severity: 'error',
      check: 'required-contexts',
      where: REQUIRED_CONTEXT_FIXTURE,
      message: 'is missing. The recorded shape of the required-context set is this check\'s baseline; deleting it deletes the comparison, and a check whose baseline vanished reading exactly like one that passed is the shape this refuses.',
    }]
  }
  let fixture = null
  try {
    fixture = JSON.parse(fixtureRaw)
  } catch {
    return [{
      severity: 'error',
      check: 'required-contexts',
      where: REQUIRED_CONTEXT_FIXTURE,
      message: 'does not parse. The recorded shape of the required-context set is this check\'s baseline; re-record it from the API (branch endpoint and ruleset objects, agreeing).',
    }]
  }
  const live = requiredContextsSource ? requiredContextsSource() : liveRequiredContexts()
  if (live == null) {
    // `policy-docs` is itself a required context: an unreachable or
    // rate-limited API must not block every merge. UNCHECKED, said out loud --
    // a check that skips without saying so reads exactly like one that passed.
    console.log(`  skip     required-contexts     the GitHub API is unreachable (${liveRequiredContextsWhy()}); the live required-context set is UNCHECKED this run, not confirmed`)
    return []
  }
  const sites = requiredContextsSitesSource ? requiredContextsSitesSource() : trackedFiles().list.filter((f) => REQUIRED_CONTEXT_SITE.test(f)).sort()
  return [
    ...requiredContextsDrift(REQUIRED_CONTEXT_FIXTURE, fixture, live),
    ...sites.flatMap((rel) => checkRequiredContexts(rel, read(rel), live)),
  ]
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
// RULE BINDING. Which paths load which rule, derived from the tree.
//
// WHY THIS EXISTS. `.claude/rules/*.md` reaches a seat only when the harness
// loads it, and the harness loads it when the seat reads a file matching one of
// its `paths:` globs -- CLAUDE.md, "The project policies, loaded when they
// bind". Nothing measured that. Four `## Friction` entries across #1058, #1061
// and #1062 made one complaint in different words, and #1062's names it
// outright: "no instrument answers `is rule X loaded on path Y`". The binding
// model itself was already load-bearing before this check -- `roleTokens`
// charges a role for exactly the rules whose globs match what it opens -- so
// the model was being trusted for a budget while never being audited.
//
// It reuses `rulePaths` and `globToRe` rather than parsing frontmatter again:
// a second implementation of the binding would measure a binding nothing loads.
//
// WHAT IT CANNOT ANSWER, stated rather than implied. It measures BINDING and
// nothing else. It does not measure whether a rule's sentences are unique
// (`checkDuplicates` is the only instrument on that, over 12-grams), whether a
// bound rule is read, obeyed, or even relevant to the file that loads it, or
// whether the RIGHT rule binds a path -- only that at least one does. The gap
// that remains after this check is a capped file bound by some rule while the
// rule that governs its subject is not among them; deciding that needs a
// rule-to-subject mapping no artifact in this tree carries, and inventing one
// here would be a hand-kept list, which is the shape this check exists to
// replace. Named so the next seat does not read a green run as more than it is.
//
// OVER-BREADTH IS REPORTED AND NOT REFUSED. `--rule-binding` prints each rule's
// share of the tracked tree, because a glob that loads on nearly every change
// spends a seat's context on every change. No cap is applied: the honest
// threshold between "governs a large surface" and "over-broad" is a judgement,
// and a number chosen here would be one seat's opinion enforced on every later
// one. A report a seat reads is what that is worth; a gate check is not.
let ruleBindingSource = () => null

function ruleBindingOverTree() {
  return checkRuleBinding(ruleBindingSource())
}

// The model, so the acceptance can drive the check against a synthetic tree
// without touching the real one. `null` -- and anything else `??` discards --
// means the tracked tree, on the same terms as `coverageFileSource`.
function liveRuleBinding() {
  const corpus = policyFiles()
  return {
    tracked: trackedFiles().list,
    corpus,
    rules: corpus.filter((f) => RULE_FILE.test(f)).map((f) => ({ file: f, globs: rulePaths(f) })),
  }
}

function checkRuleBinding(model = null) {
  const { tracked, corpus, rules } = model ?? liveRuleBinding()
  const findings = []
  const bound = new Map(corpus.map((f) => [f, []]))
  for (const rule of rules) {
    // `rulePaths` returns null for BOTH a missing frontmatter block and a
    // frontmatter with no `paths:` key, and the two are one defect here: either
    // way the harness has no path on which to load the rule, so it is loaded in
    // every session instead and charged to `always_loaded_tokens`. An unscoped
    // rule is not refused because it is large; it is refused because the
    // question this check answers has no answer for it.
    if (!rule.globs || !rule.globs.length) {
      findings.push({
        severity: 'error',
        check: 'rule-binding',
        where: rule.file,
        message: `declares no \`paths:\` globs, so no path loads it: the harness charges it to every session instead, which is what \`always_loaded_tokens\` caps. Give it the paths it governs, or move the prose into CLAUDE.md, which is the artifact that is meant to be always loaded.`,
      })
      continue
    }
    for (const g of rule.globs) {
      const re = globToRe(g)
      if (tracked.some((f) => re.test(f))) continue
      findings.push({
        severity: 'error',
        check: 'rule-binding',
        where: rule.file,
        message: `has \`paths:\` glob "${g}", which matches no tracked file, so that entry loads the rule for nobody. Either the path was renamed or deleted under it, or the glob never matched; point it at what it governs, or delete it.`,
      })
    }
    for (const f of corpus) {
      if (rule.globs.some((g) => globToRe(g).test(f))) bound.get(f).push(rule.file)
    }
  }
  // The corpus, not the tree: these are the files that already have a cap and a
  // seat-facing purpose, so a capped policy file no rule binds is a file whose
  // editor is told nothing at the moment they edit it. Against the whole tree
  // this would report nine hundred source files and mean nothing.
  for (const [f, rs] of bound) {
    if (rs.length) continue
    findings.push({
      severity: 'error',
      check: 'rule-binding',
      where: f,
      message: `is a measured policy file that no \`.claude/rules/*.md\` binds: editing it loads no project rule, so the caps and conventions that govern it reach the seat only if it opens CLAUDE.md's index by hand. Add it to the \`paths:\` of the rule that governs it.`,
    })
  }
  return findings
}

// The report half. The checks above refuse three shapes; this prints the whole
// matrix, which is the thing #1062 asked for and which no failure can be
// written for: "which paths load rule X" has an answer on a healthy tree too.
function cmdRuleBinding() {
  const { tracked, corpus, rules } = liveRuleBinding()
  console.log(`rule bindings, derived from \`git ls-files\` (${tracked.length} tracked file(s), ${corpus.length} in the measured policy corpus)\n`)
  for (const rule of rules.slice().sort((a, b) => a.file.localeCompare(b.file))) {
    const globs = rule.globs ?? []
    const all = new Set()
    console.log(rule.file.replace(/^\.claude\/rules\//, ''))
    if (!globs.length) console.log('    (no paths: globs -- loaded in every session)')
    for (const g of globs) {
      const re = globToRe(g)
      const hits = tracked.filter((f) => re.test(f))
      hits.forEach((f) => all.add(f))
      console.log(`    ${g.padEnd(42)} ${String(hits.length).padStart(4)} tracked${hits.length <= 3 && hits.length ? `  ${hits.join(', ')}` : ''}`)
    }
    const inCorpus = corpus.filter((f) => all.has(f))
    console.log(`    => ${all.size} tracked file(s), ${(100 * all.size / tracked.length).toFixed(1)}% of the tree; ${inCorpus.length} of them policy`)
  }
  console.log('\npolicy corpus file -> the rules a seat loads when it edits that file\n')
  for (const f of corpus) {
    const rs = rules.filter((r) => (r.globs ?? []).some((g) => globToRe(g).test(f))).map((r) => path.posix.basename(r.file))
    console.log(`  ${rs.length ? ' ' : '!'} ${f.padEnd(44)} ${rs.join(', ') || '(none)'}`)
  }
  console.log('\nThis measures BINDING only: that a rule is loaded on a path, never that its sentences are unique, that it is read, or that the rule which governs a file\'s subject is among the ones bound to it. The share column is reported and not capped; no threshold is applied.')
}


// ---------------------------------------------------------------------------
// no-gh. The seats run in a container with no `gh` binary; web-fragments.md
// carries the MCP mapping and is the one place the string may appear.

const GH_RE = /\bgh\s+(pr|issue|run|api|release|secret|workflow)\b/g
const GH_ALLOWED = /^\.claude\/workflows\/web-fragments\.md$/

// AND ONE COMMAND IS REFUSED EVERYWHERE, the mapping table included, because it
// answers a different question from the one it is offered for. `gh pr checks`
// prints the LATEST run per check, so a check that failed and then succeeded
// reads as never-red -- #625 merged with a `pr-contract` failure at its head and
// a body saying `## Red checks: none`, and the body was not lying about what its
// author saw. A seat writing that section must read
// `/repos/<owner>/<repo>/commits/<sha>/check-runs`, which returns every run.
// The mapping table is not exempt: it is where a seat with no `gh` binary looks
// up what to run, so an exemption there is the hole rather than an escape from
// it.
const GH_LOSSY = /\bgh\s+pr\s+checks\b/g

function checkNoGh(rel, text) {
  const out = []
  text.split('\n').forEach((line, i) => {
    GH_LOSSY.lastIndex = 0
    if (GH_LOSSY.test(line)) {
      out.push({
        severity: 'error',
        check: 'no-gh',
        where: `${rel}:${i + 1}`,
        message: 'names `gh pr checks`, which prints only the LATEST run per check, so a check that failed and then succeeded reads as never-red. Read /repos/<owner>/<repo>/commits/<sha>/check-runs, which returns every run.',
      })
    }
  })
  if (GH_ALLOWED.test(rel)) return out
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
// The working band, and why only the five aggregates get one. A cap re-recorded
// to the measured value every time leaves zero headroom, so the NEXT pull
// request is refused by whatever it adds -- and the refusal is not about that
// pull request's prose, it is about the previous seat's arithmetic. Measured on
// this corpus: twenty consecutive commits at exactly zero corpus headroom, and
// zero headroom refused no accretion over that window. What it did produce is a
// confiscation edit -- a one-line change to `corpus_tokens` with no corpus file
// in the commit at all -- and a two-branch collision where main and a branch
// re-record the same line over different bases, neither number is right after
// the merge and the deltas do not add (#1122).
//
// So the five aggregate caps are compared against `cap + band`. The recorded
// cap stays the honest LAST MEASUREMENT, which is what makes a re-record
// meaningful; the band is the room a seat works in without touching it. The
// ratchet still bites, one band later, and that is the property the null
// control pins: a brief-sized addition is still refused.
//
// The per-file caps deliberately get NO band. They are a per-document ratchet a
// seat pays one document at a time, the payment is small and local, and a band
// there would buy silent growth in every one of 39 files at once.
//
// Absent or unparseable, the band is 0 and every comparison is what it was.
function bandOf(b) {
  const n = Number(b && b._band)
  return Number.isFinite(n) && n > 0 ? n : 0
}

function checkBudgets(files, budget) {
  const b = budget !== undefined ? budget : policyBudgets()
  if (!b) return []
  const out = []
  const band = bandOf(b)
  const ceiling = (cap) => cap + band
  // What the seat is told it exceeded: the ceiling it actually hit, and the two
  // numbers it is made of, so nobody reads a stale-looking cap as the refusal.
  const capPhrase = (cap) => (band ? `${ceiling(cap)} (the recorded ${cap} plus the working band of ${band})` : `${cap}`)
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
  if (b.always_loaded_tokens != null && alwaysTokens > ceiling(b.always_loaded_tokens)) {
    out.push({
      severity: 'error',
      check: 'budgets',
      where: '(always-loaded set)',
      message: `about ${alwaysTokens} tokens exceeds the cap of ${capPhrase(b.always_loaded_tokens)}. Every seat pays this before its first productive read.`,
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
  if (b.corpus_tokens != null && corpusTokens > ceiling(b.corpus_tokens)) {
    out.push({
      severity: 'error',
      check: 'budgets',
      where: '(whole corpus)',
      message: `about ${corpusTokens} tokens exceeds the cap of ${capPhrase(b.corpus_tokens)}. Moving prose between policy files does not change this number, which is why it is here: cut it, or raise the cap in the diff a reviewer reads.`,
    })
  }

  for (const [role, spec] of Object.entries(b.roles || {})) {
    const t = roleTokens(rows, spec.opens)
    if (spec.cap != null && t > ceiling(spec.cap)) {
      out.push({
        severity: 'error',
        check: 'budgets',
        where: `(role ${role})`,
        message: `about ${t} tokens exceeds the cap of ${capPhrase(spec.cap)}. This is what the seat loads once it opens ${spec.opens.join(', ')} -- the floor in always_loaded_tokens is what it pays before that.`,
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

// A squash merge's subject ends `(#N)`. `main` no longer produces one -- it
// takes a pull request as a merge commit, subject `Merge pull request #N from
// <branch>`, per docs/decisions/0010-merge-commits-on-main.md -- so this
// pattern's zero over a live window means COULD NOT ENUMERATE, not no merges.
// tools/release/stamp.py has a PR_RE for
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

// AND ONE FILE PER PULL REQUEST, `docs/delivery/<N>.md` -- the owner's choice on
// #201 (comment 5704121269) of the countermeasure costed in 5704098870. Every
// branch appended its row at the same seam of one table, so each merge left
// every open branch DIRTY: 31 row-only conflicts over 40 merges. A file per
// number shares no seam with any other. A file speaks for <N> only through a
// line anchoring <N> itself (`rowAnchor`), so a misnamed file dispositions nobody.
const ROW_DIR = 'docs/delivery'
// The listing is swappable, as `rowFreezeSource` is, so the acceptance drives
// `rowFiles` and `recordRegionOverTree` themselves: emptying either, or dropping
// `rowFiles()` from the region, refuses every row file and survived #1081's review.
let rowFileSource = () => {
  try { return fs.readdirSync(path.join(ROOT, ROW_DIR)).map((n) => [n, () => read(`${ROW_DIR}/${n}`) ?? '']) } catch { return [] }
}
function rowFiles() {
  return Object.fromEntries(rowFileSource().flatMap(([n, text]) => (/^\d+\.md$/.test(n) ? [[n.slice(0, -3), text()]] : [])))
}
function recordRegionOverTree() {
  return recordRegion(read(DISPOSITION_FILES[0]) ?? '', read(DISPOSITION_FILES[1]) ?? '', rowFiles())
}

// The table stops growing. What it held when the files began stays a valid
// disposition, as do the rows four open branches (#1068 two, #1073, #1074,
// #1077) had already written; past these counts a new row is refused before it
// merges and belongs in a file. One-sided, like a budget: moving rows out is free.
const ROW_FREEZE = { rows: 41, anchors: 354 }
// A corpus check, so it runs pre-merge on every pull request and the mutation
// lane empties it; the source is swapped by the acceptance, as coverage's is.
let rowFreezeSource = () => read(DISPOSITION_FILES[0]) ?? ''
function rowFreezeOverPlan() {
  return checkRowFreeze(rowFreezeSource())
}
function checkRowFreeze(planText, freeze = ROW_FREEZE) {
  let inside = false
  let table = 0 // 0 before the section's first table, 1 inside it, 2 after
  const n = { rows: 0, anchors: 0 }
  for (const line of planText.split('\n')) {
    const h2 = /^##\s+(.*?)\s*$/.exec(line)
    if (h2) { inside = h2[1] === RECORD_SECTION; continue }
    if (!inside) continue
    if (table < 2 && line.startsWith('|')) { table = 1; if (!/^\|[\s|:-]+\|\s*$/.test(line)) n.rows++ }
    else if (table === 1) table = 2
    if (rowAnchor(line)) n.anchors++
  }
  return Object.keys(freeze).filter((k) => n[k] > freeze[k]).map((k) => ({
    severity: 'error',
    check: 'row-freeze',
    where: DISPOSITION_FILES[0],
    message: `\`## ${RECORD_SECTION}\` holds ${n[k]} ${k === 'rows' ? 'rows in its first table' : 'anchored pull-request rows'}, over the ${freeze[k]} frozen when rows moved to one file per pull request. Write the row as ${ROW_DIR}/<N>.md, anchored \`- [#N](.../pull/N)\`, and take it out of the table: a row at the table's end conflicts with every other open branch.`,
  }))
}

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

// First-parent commits in the record window. `--first-parent` is load-bearing
// on a history that is not squash-only: a merge commit's second parent is
// another pull request's branch, and asking the API for that SHA would
// double-count. It WAS the same set either way while `main` was squash-only;
// it is not since 2026-09-14 (docs/decisions/0010-merge-commits-on-main.md),
// so this flag is now load-bearing in fact and not only in principle.
function firstParentCommits(since) {
  const out = git(
    ['log', '--first-parent', '--format=%H%x09%s', `${since}..${mainRef()}`],
    { allowFail: true },
  )
  if (!out) return []
  const rows = []
  for (const line of out.split('\n')) {
    if (!line) continue
    const tab = line.indexOf('\t')
    if (tab < 0) continue
    rows.push({ sha: line.slice(0, tab), subject: line.slice(tab + 1) })
  }
  return rows
}

// THE ENUMERATOR. Pure over its two inputs so the acceptance can drive the
// two shapes #677 named — a suffix-less subject, and a suffix that names an
// issue — without a network. `pullsBySha` present is API mode: the number
// comes from the commit-to-PR map, and a commit with no entry is a stamp
// (or any other first-parent that is not a pull request) and is skipped.
// `pullsBySha` null is the offline fallback: the trailing `(#N)` of the
// subject, the function `mergedPRs` already is. The two modes must print
// different words. A reader who cannot tell them apart is the same defect
// as `MODE: SCOPED` against `MODE: FULL`.
function enumerateMerges(commits, pullsBySha) {
  const mode = pullsBySha ? 'api' : 'subject'
  const seen = new Set()
  const prs = []
  for (const { sha, subject } of commits) {
    let pr = null
    if (pullsBySha) {
      const raw = pullsBySha.get(sha)
      if (raw == null || raw === '') continue
      pr = String(raw)
    } else {
      const m = String(subject).match(MERGE_SUBJECT_RE)
      if (!m) continue
      pr = m[1]
    }
    if (seen.has(pr)) continue
    seen.add(pr)
    prs.push({ pr, subject, sha })
  }
  return { mode, prs }
}

function fetchPullsBySha(commits) {
  const slug = repoSlug()
  if (!slug) return { ok: false, why: 'no github remote on origin' }
  const map = new Map()
  for (const { sha } of commits) {
    const res = ghGet(`/repos/${slug}/commits/${sha}/pulls`)
    if (!res.ok) return { ok: false, why: res.why }
    const rows = Array.isArray(res.data) ? res.data : []
    if (rows.length) map.set(sha, rows[0].number)
  }
  return { ok: true, map }
}

function mergedPRsFromWindow(since) {
  const commits = firstParentCommits(since)
  const fetched = fetchPullsBySha(commits)
  if (fetched.ok) return { ...enumerateMerges(commits, fetched.map), why: null }
  return { ...enumerateMerges(commits, null), why: fetched.why }
}

// THE LOUD HALF OF THE ENUMERATION GUARD (#957's dead-fetch discipline; the
// in-file precedent is `required-contexts`' skip line). `mergedPRsFromWindow`
// falls back to subject mode when `/commits/<sha>/pulls` will not answer, and
// on this repository's merge commits the fallback's end-anchored `(#N)` matches
// NOTHING -- every subject is `Merge pull request #N from ...`, which ends in a
// branch name. The fallback's zero therefore means "no data", not "no merges":
// measured at fdd30fa over v6.5.0..origin/main, 12 merged pull requests all
// printed as `STATS: 0 merged pull request(s)` with no fetch-failure marker,
// and friction_issues.mjs -- which refuses a histogram whose WINDOW fetch
// failed but had no marker for an enumeration that never produced a window --
// filed nothing, green (#1043 review, comment 5673472536, residual 2).
//
// rc=0 STAYS acceptable on this path -- the stats step is deliberately
// `|| true`, and this skip is a fetch failure rather than a measured clean
// window, so reddening it would block on a transient API outage -- so the line
// is the whole guard: unmissable, `UNCHECKED this run, not confirmed`, the same
// words the required-contexts skip uses. Pure over its `why` so the acceptance
// drives it offline, and listed in LOOP_CHECK_NAMES so emptying it is a
// mutation the mutants lane refuses rather than a silent string change.
export function enumSkipLine(why) {
  return `  skip     merge-enumeration     the commit-to-PR map could not be fetched (${why}); the window's merged pull requests are UNCHECKED this run, not confirmed empty -- the subject fallback's zero over merge-commit subjects means "no data", not "no merges"`
}

// The record's SEARCH REGION, and the reason it is not the whole file.
//
// `#<pr>` tested against the whole plan plus the handover is satisfied by
// any mention at all: a carried finding that says "found by #639's first
// review" dispositions #639, and a standing rule that names a pull request as
// an example dispositions it too. The check could not tell its subject from its
// prose, so it passed on text written before the merge it was accepting.
//
// The anchor is the SECTION, not the line and not the link. A row format was
// the obvious fix and is the wrong one: it would refuse the dispositions
// this repository actually writes inside Delivery-status TABLE CELLS, and pin a
// shape the next lane must copy rather than a property it must satisfy.
// Measured before choosing, and the count moves with the window
// rather than being carried: at `e4f34c7` all 42 merged pull requests in the
// window were linked from `## Delivery status` and from nowhere else, and EVERY
// ONE still is at every head this has been re-derived at. The size of the window
// is deliberately not restated: it grows with every merge on `main`, and three
// copies of it went stale inside this one branch before the number was dropped.
// What is stable is the property, not the count.
//
// AND THE HANDOVER IS NOT DEMOTED, which has a consequence worth stating rather
// than leaving to be discovered: it contributes ALL of itself, so a pull request
// named anywhere in it -- a trap citation, a correction -- is dispositioned by
// that mention. At `cc2efc9` #621 was, and would be again. That is the price of
// `DISPOSITION_FILES` naming both files and the error message promising both;
// narrowing the handover too is a policy change about what that document is
// for, and belongs to the owner rather than to a linter.
//
// The plan contributes that one section; the handover contributes all of
// itself, because the handover IS the record and has no other job. If the
// section is missing the region is empty, and that is reported as its own
// failure rather than as one error per merge in the window -- a renamed heading is a different
// defect from an unrecorded merge and reads nothing like it.
const RECORD_SECTION = 'Delivery status'

function recordRegion(planText, handoverText, files = {}) {
  const out = []
  let inside = false
  for (const line of planText.split('\n')) {
    const h2 = /^##\s+(.*?)\s*$/.exec(line)
    if (h2) inside = h2[1] === RECORD_SECTION
    else if (inside) out.push(line)
  }
  const rows = Object.entries(files).flatMap(([n, text]) => text.split('\n').filter((l) => rowAnchor(l) === n))
  return { region: [...out, ...rows].join('\n') + '\n' + handoverText, sectionFound: out.length > 0 }
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
//
// A DISPOSITION IS NOT A MENTION, and the region alone could not tell them apart
// (#752). `#N` tested against the whole region is satisfied by a sentence inside
// somebody else's row, including one that says in terms it is NOT dispositioning
// that number: on `main` the single occurrence of #741 was "#741 stays #745's",
// written inside #748's row, and `record` reported zero without a disposition
// while #741 had no row at all. The control that showed the check was not simply
// inert: at the same head it correctly reported #749, which no text mentioned.
//
// So one shape is subtracted and one only: a line that ANCHORS a pull request --
// `- [#M](.../pull/M)`, the governance-queue row format -- speaks for #M, and a
// different number named inside it is that row's prose. Everything else in the
// region still counts, which is the whole reason the predicate is this narrow
// rather than a row anchor.
//
// WHY NOT A ROW ANCHOR, which is the obvious shape and was measured before being
// rejected rather than argued away. Swept over every first-parent head on `main`
// in v6.3.16..origin/main, rebuilding each head's window the way governance.yml
// does and enumerating through the API: `^- [#N]` newly refuses eleven pull
// requests, ten of them legitimate dispositions written as table cells, as rows
// anchored to an ISSUE number, or in the handover's prose; extending the anchor
// to table rows newly refuses five, four of them legitimate. The predicate below
// newly refuses exactly one, #741, which is the gap. The counts are the sweep's
// and move with the window; the harness is in the pull request that added this.
// All three shapes the sweep cleared are pinned in `assertAcceptance`.
//
// THE COST, stated rather than left to be discovered. This cannot tell "this
// dispositions #746", written inside #748's row, from "#741 stays #745's"
// written in the same place. It refuses both, so a merge dispositioned ONLY from
// inside another pull request's row is now reported -- and the remedy is the row
// the rule asks for in the first place, which the error message already names.
// Over the swept range that cost nothing: every pull request dispositioned
// inside another's row also had a row of its own. Re-run the sweep rather than
// trusting that sentence at a later head.
//
// THE ANCHOR MUST NAME ITS OWN PULL REQUEST. `[#M](...)` with a link that does
// not resolve to `/pull/M` is not read as a row: the plan writes rows anchored to
// ISSUE numbers whose cells disposition the pull request that closed them, and
// suppressing those is the four-false-refusal arm above.
const ROW_ANCHOR_RE = /^\s*[-*]\s+\[#(\d+)\]\((?:[^()\s]*\/pull\/)(\d+)\)/

// The pull request a line SPEAKS FOR, or null when it speaks for nobody and
// every number on it is therefore a disposition, as before.
function rowAnchor(line) {
  const m = ROW_ANCHOR_RE.exec(line)
  return m && m[1] === m[2] ? m[1] : null
}

// AND THE SAME HOLE IN THE OTHER ROW FORMAT. The list-anchor above subtracts
// `- [#M](.../pull/M)`, and the Delivery-status rows this repository actually
// writes are TABLE rows -- `| ... | **in review -- PR [#M](.../pull/M) ...** |`
// -- which that regex cannot match, because it is anchored at the start of the
// line and a table row starts with a pipe. So the same defect survived in the
// format carrying most of the record: measured on `main` at 434cd5f, #1065's
// only occurrence anywhere in the region at the time was a sentence inside the
// plan's table row for #1074, and `--record` reported it dispositioned. Same
// class as #752, one row format over.
//
// WHY THIS IS NOT THE REJECTED "EXTEND THE ANCHOR TO TABLE ROWS". That option
// read a table row's FIRST cell as its anchor and refused every other number in
// it, which the #752 sweep measured as five new refusals, four legitimate: the
// plan's rows are anchored to an ISSUE number and disposition the pull request
// that closed it in a later cell, and the wave rows disposition from a cell with
// no anchor at all. The rule below reads the row's PULL-REQUEST LINKS instead,
// all of them, and a row that links none speaks for nobody -- so both of those
// shapes are untouched, and they are the two null controls in `assertAcceptance`
// directly beneath the arm that fires.
//
// A ROW MAY SPEAK FOR SEVERAL, which is the difference from the list form and is
// deliberate. A status cell naming two pull requests is one row dispositioning
// both, and the set is every link on the line whose anchor text and target
// agree -- the same identity test as above, for the same reason: `[#M](.../pull/N)`
// with M and N different is ambiguous, so it makes the row speak for neither and
// the row falls back to dispositioning everything on it.
//
// THE COST, on the same terms #752 stated its own. A row that links pull request
// M and dispositions N in prose now refuses N, and cannot tell that from a row
// that merely mentions N. The remedy is the one the error message already names
// and the one #1081 landed the mechanism for: `docs/delivery/N.md`, N's own row.
// Re-measured over `v6.5.0..origin/main` in the pull request that added this;
// the sweep and its result are in that body, and the figure moves with the
// window, so re-run it rather than quoting it.
const TABLE_PULL_LINK_RE = /\[#(\d+)\]\((?:[^()\s]*\/pull\/)(\d+)\)/g

// The set of pull requests a line speaks for, or null when it speaks for nobody.
function speaksFor(line) {
  const anchored = rowAnchor(line)
  if (anchored) return new Set([anchored])
  if (!/^\s*\|/.test(line)) return null
  const set = new Set()
  for (const m of line.matchAll(TABLE_PULL_LINK_RE)) if (m[1] === m[2]) set.add(m[1])
  return set.size ? set : null
}

function checkRecord(prs, dispositionText) {
  const out = []
  const lines = String(dispositionText ?? '').split('\n')
  for (const { pr, subject } of prs) {
    const re = new RegExp(`#${pr}(?![0-9])`)
    if (lines.some((l) => re.test(l) && (speaksFor(l)?.has(pr) ?? true))) continue
    out.push({
      severity: 'error',
      check: 'record',
      where: DISPOSITION_FILES[0],
      message: `no disposition in the plan of record or the living handover for merged pull request #${pr} (${subject.slice(0, 90)}). Write its row as ${ROW_DIR}/${pr}.md. A merge nobody recorded is a merge no later seat can resume from.`,
    })
  }
  return out
}

// ---------------------------------------------------------------------------
// table. A blank line between two rows of one markdown table ends the table
// there, and every row after it renders as literal text -- pipes and all --
// while the source still looks like a table to whoever is editing it. Found
// when a row of the plan's Delivery-status table was left FIVE cells wide in a
// three-column table and the reviewer went looking for why nobody had noticed:
// the row was not in a table at all. Measured through GitHub's own /markdown
// endpoint at 7d8d271, the section rendered as one table of 11 rows plus 104
// literal pipe characters loose in paragraphs; with the blank line removed it
// renders as one table of 37 rows and no loose pipes.
//
// This runs in the RECORD mode rather than over the corpus because the two
// documents it reads are the record's own, and `docs/` is not a policy
// directory -- no corpus check has ever opened either of them.
//
// The one legitimate shape it must not refuse is two tables in a row, where the
// blank line is the separator between them. That is told apart by looking one
// line further: a new table's header is followed by a delimiter row, and a
// continuation row is not.
function checkTableSplit(rel, text) {
  const out = []
  const lines = text.split('\n')
  const isRow = (l) => typeof l === 'string' && l.startsWith('|')
  const isDelim = (l) => typeof l === 'string' && /^\|[\s|:-]+\|\s*$/.test(l)
  for (let i = 1; i < lines.length - 1; i++) {
    if (lines[i].trim() !== '') continue
    if (!isRow(lines[i - 1]) || !isRow(lines[i + 1])) continue
    if (isDelim(lines[i + 2])) continue // a new table starts here, not a split
    out.push({
      severity: 'error',
      check: 'table',
      where: `${rel}:${i + 1}`,
      message:
        'a blank line sits between two rows of one table, which ends the table here. Every row below renders as literal text with its pipes visible, while the source still reads as a table. Delete the blank line, or give the second half its own header and delimiter row.',
    })
  }
  return out
}

// --record, fourth output. The two disposition documents are read as source
// by every other class; this walks the rendered token stream and compares
// structure back to the source. markdown-it lives in render_md.mjs so this
// file's signature stays the single-line form the mutation lane rewrites.
function checkRender(rel, text) {
  return inspectRender(text).findings.map((f) => ({
    severity: 'error',
    check: 'render',
    where: `${rel}:${f.line}`,
    message: f.message,
  }))
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

// THE OTHER HALF OF THE SAME GRAMMAR (#1240, D13-03). `verdictClasses` reads
// the verdict WORDS the reviewer prompt teaches (`merge`, `blocked`); the wave
// script also teaches eleven BLOCK CLASSES -- VERDICT_CLASSES -- that say WHY
// a review blocked, and the histogram used to print only the two words as
// "the verdict grammar" while keying every blocked verdict on the one word
// `blocked`: 0 block-class rows over 30 blocked verdicts at the round-5
// baseline, an instrument that could not compute the block-class metric the
// D13 brief asks for. Read from the same single source as the words, with the
// same fail-loud posture: unreadable yields null and the caller withholds
// rather than classifying against a list typed here.
const BLOCK_CLASS_LITERAL_RE = /const VERDICT_CLASSES = \[([^\]]*)\]/g
export function blockClasses(text = read(WAVE_SCRIPT)) {
  if (text == null) return null
  BLOCK_CLASS_LITERAL_RE.lastIndex = 0
  const m = BLOCK_CLASS_LITERAL_RE.exec(text)
  if (!m) return null
  const words = [...m[1].matchAll(/'([a-z][a-z0-9-]*)'/g)].map((x) => x[1])
  return words.length ? words : null
}

// THE MATCHER IS THE WAVE'S OWN GRAMMAR, NOT A SECOND ONE (#1472, D13-02). The
// histogram built its matcher from the two words above -- `^Fix review:\s*
// (blocked|merge)\b`, case-insensitive -- while the header line asserted it had
// read the grammar "from .claude/workflows/web-fix-wave.js". It had read half of
// it, and the halves diverged on four axes, every one one-directional: no space
// after the colon, case, an abbreviated head, and no head at all. The wave
// refuses all four (`\s+`, no `i`, `[0-9a-f]{40}`, and a SHA required on both
// arms); the histogram counted them, and the merge arm took a SHA-less line
// while the blocked arm in the same function sent its own to `unclassified`.
// That asymmetry is also what a rework round is measured against -- a verdict
// naming no head is no evidence of a moved one -- so the looser grammar did not
// merely over-count, it moved the rework figure. The reader now classifies with
// the wave's `VERDICT_RE` itself, read out of that file the way `verdictClasses`
// reads the words, so a line the wave throws on lands in `unclassified` where
// the drift shows; the extraction technique is `check-wave-script.mjs`'s, which
// builds the same regex from the same literal to check the reviewer contracts'
// own examples. Unreadable yields null and the caller withholds, as with the
// words and the block classes.
const VERDICT_RE_LITERAL_RE = /const VERDICT_RE = new RegExp\(\n([\s\S]*?)\n\)/

export function waveVerdictRe(text = read(WAVE_SCRIPT)) {
  if (text == null) return null
  const m = VERDICT_RE_LITERAL_RE.exec(text)
  if (!m) return null
  try {
    // eslint-disable-next-line no-new-func -- the literal is the wave script's
    // own, from this repository, and building it is how check-wave-script.mjs
    // reads the same grammar.
    return new Function('VERDICT_CLASSES', `return new RegExp(${m[1]})`)(blockClasses(text) ?? [])
  } catch {
    return null
  }
}

// A `## Friction` section names, per entry, the rule id that cost the seat
// time. The key is the `<rule_id>` of the template's grammar, read by the SAME
// parser `checkPrBody` refuses with (`frictionEntries`), so a body the contract
// accepted is a body this histogram can classify. It was not: this read the
// first backticked span of 2-80 characters on a LIST-MARKED line and called
// any other marked line unlabelled, while the contract read `<rule_id>:
// <class>: <evidence>`, marker optional, backticks tolerated. Over the 156
// pull requests merged in v6.4.0..cb30d98 the contract had passed 54 entries;
// this saw the 21 that carried a marker and none of the 33 that did not,
// keyed 6 of the 21 on their rule id, 7 on a fragment (a command quoted in
// the evidence, or the entry's own prefix cut at an inner backtick), and
// bucketed 8 as unlabelled because the whole entry sat inside one backtick
// pair longer than 80 characters or wrapped onto a second line. The one key
// the cron then filed on was that bucket. An entry that parses under no
// grammar is still counted under one bucket rather than dropped: an unparsed
// entry is friction that happened, and discarding it biases the histogram
// toward "no friction". Merged bodies are never re-checked by the contract,
// so this bucket is where a body that predates a refusal, or was edited after
// it ran, still shows.
const FRICTION_UNLABELLED = '(unlabelled friction bullet)'

// KEY NORMALIZATION. The id is whatever a seat typed, and the histogram used to
// key on it verbatim, so one rule reached the filer as several keys and several
// rules reached it as none. Measured at 598ad6d over `--since v6.5.1`:
// `gate-scoping` 5 and `gate-scoping.md` 3 filed #1095 and #1093 for one rule
// file; `finding-propagation` 4 and `finding-propagation.md` 3 did the same;
// and `defect-root-cause` 1 + `defect-root-cause.md` 2, and `steward` 2 +
// `steward-S10` 1, each summed to the threshold while neither half reached it,
// so two rules with recurring friction surfaced nowhere at all.
//
// THE RULE, in one sentence: the key is the POLICY FILE the entry names, when
// it names one, and the id verbatim when it does not. So the key is always a
// path `git ls-files` confirms, which is what a disposer opens, and the
// normalization is never a guess -- an id that resolves to nothing is left
// exactly as typed rather than folded into something that looks close.
//
// Three steps, each with the thing it must NOT do:
//   1. A `#fragment` names a section of a document, not a second document, so
//      it is dropped: `CLAUDE.md#budgets` and `CLAUDE.md#rule-4` are CLAUDE.md.
//   2. The id, then the id without a trailing `.md`, is looked up.
//   3. Failing both, the longest `-`-delimited PREFIX that resolves is used --
//      `steward-S10` and `fixer-step-5` are the steward skill and the fixer
//      contract, because a suffix that is not itself a policy file is a section
//      pointer. `fixer-dispatch` goes the same way, which the triage counted
//      separately: a seat writing it named the fixer contract, the issue a
//      disposer would open is that contract, and there is no evidence in the
//      tree for any other reading. The rule is self-repairing -- add
//      `.claude/rules/fixer-dispatch.md` and step 2 resolves it to itself.
//      Prefixes are tried LONGEST FIRST and only against files that exist, so
//      `defect-root-cause` resolves at step 2 and never walks down to
//      `root-cause`, which is a different policy file; the two stay two keys.
//
// An id claimed by more than one policy file resolves to NONE of them. `README`
// is claimed by three, and merging three documents under one key is exactly the
// silent merge this rule exists to refuse, so ambiguity is left unresolved and
// the id stays verbatim.
const BRIEF_FILE = /^tools\/audit\/briefs\//
let POLICY_KEY_INDEX = null
function policyKeyIndex(files = null) {
  const claims = new Map()
  const claim = (cand, p) => {
    if (!cand) return
    if (!claims.has(cand)) claims.set(cand, new Set())
    claims.get(cand).add(p)
  }
  for (const p of files ?? policyFiles()) {
    claim(p, p)
    const skill = /^\.claude\/skills\/([^/]+)\/SKILL\.md$/.exec(p)
    if (skill) {
      // A skill is named by its DIRECTORY; every skill's basename is
      // `SKILL.md`, so claiming that would make one ambiguous candidate and
      // resolve nothing.
      claim(skill[1], p)
      continue
    }
    const base = p.slice(p.lastIndexOf('/') + 1)
    claim(base, p)
    // A ROLE CONTRACT'S BARE NAME IS NOT CLAIMED, and this is the same
    // ambiguity guard as the `README` one below, not an exception to it.
    // `tools/audit/briefs/*.md` are what CLAUDE.md calls "Role contracts --
    // open the one you are", so `orchestrator` names a SEAT as readily as that
    // seat's contract, and a seat also writes the dispatch briefs it hands out.
    // Measured over `v6.5.1..origin/main` at c71c53c: the bare key
    // `orchestrator` held 4 entries across 2 pull requests and every one of
    // them records friction with a DISPATCH brief -- "the dispatch brief named
    // the lease tool tools/audit/gate_lock.py", "the plan's G3 test cannot pass
    // on the stock house", "the plan's G4 brief gives the derate range as
    // 0.3-1.0", "the brief said the claim files stay untouched" -- while the
    // separate key `orchestrator.md`, 2 entries across 2 pull requests, names
    // the contract by section ("in section 13, rule 4 means stamp.py's notes
    // rule"). Resolving the first onto the second files the contract for
    // something it does not govern. `fixer-dispatch` measured the same way:
    // both its entries are about a dispatch. The template offers one field,
    // `<rule_id>`, and there is no field for a brief, which is why the two
    // subjects arrive under one shape.
    //
    // So a briefs document resolves only from an id that names it as a FILE --
    // `orchestrator.md`, or its repo-relative path -- and a bare or
    // suffix-qualified role name stays verbatim. It costs `fixer-step-5`, which
    // did name the contract; that is the price of a rule with no list in it,
    // and a verbatim key blames nobody.
    //
    // `.claude/rules/` and `.claude/skills/` are NOT carved out, and the same
    // measurement is why: there is no "gate-scoping seat", and all three
    // `steward` entries in that window name S9 and S10, sections of the skill
    // document itself.
    if (!BRIEF_FILE.test(p)) claim(base.replace(/\.md$/, ''), p)
  }
  const index = new Map()
  for (const [cand, set] of claims) if (set.size === 1) index.set(cand, [...set][0])
  return index
}

function frictionKey(id) {
  if (id === FRICTION_UNLABELLED) return id
  const raw = String(id ?? '').trim()
  const bare = raw.replace(/^`+|`+$/g, '').replace(/#.*$/, '')
  if (!bare) return raw
  POLICY_KEY_INDEX ??= policyKeyIndex()
  if (POLICY_KEY_INDEX.has(bare)) return POLICY_KEY_INDEX.get(bare)
  const noExt = bare.replace(/\.md$/, '')
  if (POLICY_KEY_INDEX.has(noExt)) return POLICY_KEY_INDEX.get(noExt)
  const parts = noExt.split('-')
  for (let n = parts.length - 1; n >= 1; n -= 1) {
    const stem = parts.slice(0, n).join('-')
    if (POLICY_KEY_INDEX.has(stem)) return POLICY_KEY_INDEX.get(stem)
  }
  return bare
}

function frictionIds(body) {
  const section = sections(String(body ?? '')).get('Friction') ?? ''
  return frictionEntries(section).map((e) => frictionKey(e.id ?? FRICTION_UNLABELLED))
}

// The plan's threshold: three or more of one key inside the window opens a
// `[policy] recurring friction:` issue. This mode PRINTS what it would open and
// opens nothing -- CLAUDE.md's "fix it; if you cannot, verify it independently;
// only then file it" makes filing the last resort of a seat that has measured,
// not something a cron job does on a count.
const FRICTION_THRESHOLD = 3

// THE THRESHOLD'S UNIT IS THE PULL REQUEST, not the entry. "Recurring" is a
// claim about recurrence, and a key written three times inside one body has
// happened once: it is one seat, one session, one occasion. Measured at 598ad6d
// over `--since v6.5.1`, `orchestrator` reached 4 entries from 2 pull requests,
// 3 of them in a single body, and that is what filed #1094; `gate-scoping` over
// the same window reached its count from 4 separate pull requests and fires
// under either rule. Both counts are kept and both are printed -- the entry
// count is still the volume of friction -- but only the distinct-PR count is
// compared against the threshold.
const bump = (hist, key, pr) => {
  if (!hist.has(key)) hist.set(key, { entries: 0, prs: new Set() })
  const cell = hist.get(key)
  cell.entries += 1
  cell.prs.add(pr)
}

// THE SAME KEYING, ONE GRAMMAR (#1240, D13-03; #1304; #1472, D13-02). The
// blocked arm used to key every blocked verdict on the word `blocked` -- one
// constant key, because the grammar read was only the two verdict words. It keys
// the CLASS WORD the wave's own parser captures now: a taught word as itself, an
// untaught word as its own row, never folded into `other`, because a class the
// grammar does not have is the drift signal, not noise -- and a bare
// `blocked <sha>` routes to `other`, where web-fix-wave.js routes it (#1239).
// The continuation after the head was this file's own reconstruction of the
// wave's until #1472: it once matched a class word with no colon (which
// VERDICT_RE REFUSES, #1304) and it required a SHA on the blocked arm alone
// while the merge arm took a SHA-less line. Both are gone with
// BLOCKED_SHAPE_RE -- one matcher, the wave's, so a line the wave refuses is
// reported outside the grammar on EITHER arm rather than blessed as a row here.
// The merge arm stays keyed on the word alone: the passing verdict is not rework
// IN ITS OWN ROW however it is spelled, so that arm only withholds, and the
// rework that row cannot see is keyed separately below.
//
// THE REWORK THE PASSING VERDICT HIDES (#1405, D13-01). `merge` is the verdict
// the wave requires before it merges, so the exclusion above prints it and
// counts rework nowhere -- and the rework this programme pays takes exactly
// that shape. A head that moves under a review is re-verified and re-merged,
// spelled `merge <new head>`; `fix-review.md` step 12 leaves re-measuring to
// the reviewer, so the `blocked <sha> head-moved` that class exists for was
// never written. Measured over v6.6.0..e336cc2c, all 11 rework rounds named a
// moved head and `head-moved` held 0 verdicts. So a second-or-later parseable
// verdict naming a head other than the pull request's FIRST parseable verdict's
// is a re-verification of a moved head, and is keyed on the class the wave
// defines for it -- in a row of its own, beside the passing row that cannot show
// it, because that row is where the verdict landed and a histogram that emptied
// it would be reading the grammar rather than counting it. So the rows stop
// partitioning the window's verdicts: the same round is one `merge` entry AND
// one `head-moved` entry, and the second is the one that says a head moved.
// Every parseable verdict names a full head -- the wave's grammar requires one
// on both arms -- so there is no missing side to infer from: a `Fix review:`
// line with no head is outside the grammar and reaches the rework arm never.
// The key is the wave's own word -- a class the wave stops teaching is a key
// nothing routes on, which the extraction check in tests/entities.py refuses by
// name.
export const REWORK_CLASS = 'head-moved'

// WHICH ENDPOINT A VERDICT ARRIVED ON (#1471, D13-01). A verdict is an issue
// comment or a pull-request review, and `fetchWindow` asked only for
// `/issues/<n>/comments` -- so a review-posted verdict was not merely
// unweighted, the pull request read as one that carried none. Both endpoints are
// fetched now, and every verdict carries the one it came from, so the census
// line beside the coverage line can say which endpoint a window's verdicts
// arrived on rather than leaving a zero to be read as "none were written".
const VERDICT_ENDPOINTS = [
  { origin: 'issue comment', field: 'comments', at: 'created_at', path: '/issues/<n>/comments' },
  { origin: 'review', field: 'reviews', at: 'submitted_at', path: '/pulls/<n>/reviews' },
]

// The verdict walk, over both endpoints, in the order the two were WRITTEN: the
// bodies carry no shared sequence number, so the timestamps are the only
// ordering the API gives (comments oldest-first, reviews by `submitted_at`; both
// ISO-8601, so a string compare is the compare). A payload with no timestamps --
// both loop fixtures, and the round-6 window fixture -- keeps the order it was
// written in, which is `Array.prototype.sort`'s stability on equal keys.
function verdictWalk(f) {
  const rows = []
  for (const { origin, field, at } of VERDICT_ENDPOINTS) {
    for (const c of f[field] ?? []) rows.push({ body: c.body, at: c[at], origin })
  }
  return rows.sort((a, b) => String(a.at ?? '').localeCompare(String(b.at ?? '')))
}

export function statsHistogram(prs, fetched, classes) {
  const verdicts = new Map()
  const friction = new Map()
  const unclassified = []
  const endpoints = new Map()
  const re = waveVerdictRe()
  for (const { pr } of prs) {
    const f = fetched.get(pr)
    if (!f) continue
    // The head each parseable verdict names, in the order the verdicts were
    // written. The rework arm after the walk compares against the first of
    // these. (`classes` stays in this signature because every caller passes the
    // words the reviewer prompt teaches and `statsFindings` keys its arms on
    // them; the matcher below no longer needs them, because the grammar it reads
    // carries both words itself.)
    const heads = []
    for (const { body, origin } of verdictWalk(f)) {
      // THE EXTRACTION IS THE WAVE'S OWN, not only the matcher (#1480 review,
      // class-open). `web-fix-wave.js`'s `parseVerdict` does
      // `String(...).trim().split('\n')[0]` -- TRIM THE BODY, then take its
      // first line -- and this read did the opposite: take the first line, then
      // trim it. The two differ for exactly two shapes of body, and each moves
      // a verdict in the direction the other one does not: a body whose verdict
      // line ends in whitespace has its trailing space REMOVED here and KEPT
      // there, so a line the wave throws on counted as a verdict; and a body
      // opening with a blank line has `''` as its first line here, which fails
      // the `Fix review:` gate below and was neither counted nor reported,
      // while the wave reads the verdict on the second line. The `## Figures`
      // harness could not see either: it enumerates `Fix review:` FIRST LINES,
      // where the two extractions coincide by construction. Trim first, as the
      // wave does, and both directions close.
      const first = String(body ?? '').trim().split('\n')[0]
      if (!/^Fix review:/i.test(first)) continue
      const m = re == null ? null : re.exec(first)
      if (!m) {
        // A verdict that says "Fix review:" and then something the wave script
        // refuses to parse. Reported rather than bucketed, with the endpoint it
        // arrived on: it is the grammar drifting, and a histogram that quietly
        // absorbed it would hide exactly that.
        unclassified.push(`#${pr} (${origin}): ${first.slice(0, 70)}`)
        continue
      }
      const word = m[1] ? m[1] : m[5] ? m[5].toLowerCase() : 'other'
      // The head the wave's grammar captured: arm 2 for `merge`, arm 4 for
      // `blocked`, both required to be 40 hex by that grammar.
      heads.push((m[1] ? m[2] : m[4]).toLowerCase())
      bump(verdicts, word, pr)
      bump(endpoints, origin, pr)
    }
    // THE REWORK ARM (#1405, D13-01): a later verdict naming a head the first
    // one did not is a re-verification of a moved head, keyed as the class the
    // wave defines for it (see REWORK_CLASS above). A bump BESIDE the row the
    // verdict already landed in, never instead of it, so every figure this table
    // printed before the change it still prints. One bump per round, so the
    // cell's distinct-PR count and its entry count are the two figures the
    // finder measured -- 7 merges and 11 rounds over the round-6 window.
    for (const h of heads.slice(1)) if (h !== heads[0]) bump(verdicts, REWORK_CLASS, pr)
    for (const id of frictionIds(f.body)) bump(friction, id, pr)
  }
  // THE HISTOGRAM'S COVERAGE (#1406, D13-02). The verdict table's population is
  // the pull requests that CARRIED a parsable verdict -- `verdicts`' cells --
  // and `--stats` printed that population's size as the window's, because the
  // only count it printed was the merge total. A merge carrying none (an
  // automation-authored merge with no `Fix review:` comment is the common case;
  // one whose body or comments could not be fetched is the same gap with a
  // different cause) then left the denominator silently. Both counts are
  // derived from the SAME walk that built the table rather than by re-scanning
  // `prs`, so the line cannot disagree with the rows above it. The window is
  // `prs.length` -- the merges the window contains -- not the cells' union.
  const verdictPrs = new Set()
  for (const cell of verdicts.values()) for (const p of cell.prs) verdictPrs.add(p)
  const all = prs.map(({ pr }) => pr)
  const noVerdict = all.filter((pr) => !verdictPrs.has(pr))
  const unfetched = all.filter((pr) => !fetched.has(pr))
  return {
    verdicts,
    friction,
    unclassified,
    endpoints,
    coverage: { window: prs.length, verdictPrs, noVerdict, unfetched },
  }
}

// WHICH ENDPOINT THE WINDOW'S VERDICTS ARRIVED ON (#1471, D13-01), printed
// beside the coverage line. The population it counts is the walk's own -- the
// parseable verdicts `endpoints` was bumped with inside the same loop that
// builds the table -- so it cannot disagree with the rows above it, and a
// refused line stays visible with its endpoint in the `outside the grammar`
// report rather than being folded in here. Both endpoints are named with the
// path the reader asks for, because the finding is that one of them was never
// asked for: a census whose reviews row is zero over a reader that does ask
// means "none were posted", which is a fact about the window.
export function statsEndpointLine(endpoints) {
  const rows = VERDICT_ENDPOINTS.map(({ origin, path }) => {
    const cell = endpoints.get(origin)
    return `${path} (${origin}): ${cell ? cell.entries : 0}`
  })
  return `STATS ENDPOINTS: parsable verdict(s) by the endpoint they arrived on -- ${rows.join('; ')}. Both endpoints are read, so a verdict posted as a review is counted rather than read as a merge that carried none.`
}

// The line `--stats` prints beside `STATS:` so the window's merge count and the
// histogram's own verdict population are readable side by side (#1406, D13-02).
// Pure over `statsHistogram`'s `coverage` -- the counts the table above it used,
// not a second count taken here -- so the acceptance drives it offline and it
// cannot drift from the rules that produced the table. BOTH numbers print: the
// finding is that a window holding merges the histogram could not classify read
// as a smaller denominator, and one count alone cannot show the gap. The pull
// request list is capped so a large window grows the line by a constant.
const COVERAGE_LIST_CAP = 10
export function statsCoverageLine({ window: total, verdictPrs, noVerdict, unfetched }) {
  const seen = verdictPrs.size
  const missing = noVerdict.length
  const shown = noVerdict.slice(0, COVERAGE_LIST_CAP).map((p) => `#${p}`).join(' ')
  const more = missing > COVERAGE_LIST_CAP ? ` +${missing - COVERAGE_LIST_CAP} more` : ''
  const gap = missing ? `; ${missing} carried none${shown ? ` (${shown}${more})` : ''}` : ''
  const unf = unfetched.length ? `, ${unfetched.length} of them never fetched` : ''
  return `STATS COVERAGE: ${seen} of ${total} merged pull request(s) in the window carried a parsable verdict${gap}${unf}; the histogram's verdict denominator is ${seen}, not the window's merge count`
}

// Findings are severity `info`: the acceptance counts every finding by class, so
// these are pinned like any other check, while main() only ever exits non-zero
// on `error`. That is how a reporting mode is made undeletable without being
// made able to fail a job.
export function statsFindings({ prs, fetched, fetchError, classes, blocks = blockClasses(), passing = passingVerdict() }) {
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
  // THE VERDICT ARM IS A TAUTOLOGY ONLY WHEN THE GRAMMAR COLLAPSES TO ONE
  // NON-PASSING KEY (#1041, and #1240's correction). The words the reviewer
  // prompt teaches are two (`merge`, `merge` withheld as passing), but the
  // blocked arm keys on the BLOCK CLASSES the wave script teaches, so the arm
  // informs whenever those classes read. The exclusion survives for the one
  // degraded case that recreates the old shape: VERDICT_CLASSES unreadable,
  // every blocked verdict falling back to `other`, one key, a constant over
  // any active window. The histogram still PRINTS the class and its count
  // either way; only the issue proposal is withheld.
  const nonPassing = [...new Set([
    ...classes.filter((c) => !(passing && c === passing)),
    ...(blocks ?? []),
  ])]
  const verdictArmInforms = nonPassing.length > 1
  for (const [kind, hist] of [['verdict class', verdicts], ['friction rule id', friction]]) {
    for (const [k, cell] of [...hist.entries()].sort((a, b) => b[1].prs.size - a[1].prs.size)) {
      const n = cell.prs.size
      if (n < FRICTION_THRESHOLD) continue
      if (kind === 'verdict class' && passing && k === passing) {
        out.push({
          severity: 'info',
          check: 'stats',
          where: '(window)',
          message: `not opened: verdict class "${k}" at ${n} pull request(s) is the passing verdict ${WAVE_SCRIPT} requires before a merge, so this row counts rework nowhere -- the rework a merge verdict spells is keyed under the wave's "${REWORK_CLASS}", a later verdict naming a moved head. Friction is rework.`,
        })
        continue
      }
      if (kind === 'verdict class' && !verdictArmInforms) {
        out.push({
          severity: 'info',
          check: 'stats',
          where: '(window)',
          message: `not opened: verdict class "${k}" at ${n} pull request(s) is the only non-passing key the grammar can yield -- verdict words ${JSON.stringify(classes)} read from ${WAVE_SCRIPT}, and its block-class half (VERDICT_CLASSES) ${blocks == null ? 'is unreadable, so every blocked verdict collapses onto one key' : `yields only ${JSON.stringify(blocks)}`} -- so any active window clears the threshold. A constant is not a measurement; it is printed and proposes nothing. A readable VERDICT_CLASSES with more than one word makes this arm informative again.`,
        })
        continue
      }
      out.push({
        severity: 'info',
        check: 'stats',
        where: '(window)',
        message: `would open "[policy] recurring friction: ${k}" -- ${kind} at ${n} in this window, threshold ${FRICTION_THRESHOLD}. Counted as DISTINCT pull requests (${cell.entries} entr${cell.entries === 1 ? 'y' : 'ies'} in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.`,
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

// THE MARKER CENSUS (#1469, D11-03), printed beside the corpus count. All three
// arms of this class fire on a MARKER a rule declares for itself -- `REFUSED BY
// <detector>`, `SUNSET: <date>`, `HONOUR: <id>` -- so the class can name a rule
// that has outlived its reason, and it names none where no rule declares one. No
// policy file in this corpus carries any of the three, and `proposed (0) held
// (0)` on its own then prints in the shape of a measurement over a swept corpus:
// a reader cannot tell "no rule has expired" from "this class has nothing to
// read". This line states what the zero is a zero OF and moves the moment a
// marker lands, which is what makes it a census rather than a caption. The count
// is taken over the same rows `checkSunset` walks, with the same three regexes,
// so the two cannot disagree about what a marker is.
const SUNSET_MARKERS = [
  ['REFUSED BY', REFUSED_BY_RE],
  ['SUNSET:', SUNSET_MARKER_RE],
  ['HONOUR:', HONOUR_RE],
]

export function sunsetMarkerLine(rows) {
  let declared = 0
  const counts = SUNSET_MARKERS.map(([name, re]) => {
    let n = 0
    for (const { text } of rows) {
      // matchAll clones the regex WITH its lastIndex, so it must be reset here:
      // these three are shared with `checkSunset` and are left mid-walk there.
      re.lastIndex = 0
      n += [...String(text ?? '').matchAll(re)].length
    }
    declared += n
    return `${name} ${n}`
  })
  const reading = declared
    ? `${declared} marker(s) declared, so this class has a population in these files`
    : 'no marker is declared in these files, so the (0) counts below are the PARTICIPATION zero -- this class has nothing to read here, which is not the same as a corpus swept clean'
  return `SUNSET MARKERS: ${rows.length} policy file(s) scanned; ${counts.join(', ')} -- ${reading}`
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
        // Through the same normalization the histogram keys with: the friction
        // map is now keyed on the policy FILE an entry names, so an honour rule
        // written as a bare rule id would otherwise miss its own friction and
        // be proposed for sunset while the window was recording it.
        if (friction.has(id) || friction.has(frictionKey(id))) continue
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

// The credential is a PARAMETER rather than a second read of `GITHUB_TOKEN`,
// because the red-history walk below reads through `ghCredential()` and a gate
// that predicts one credential while the fetch uses another refuses a read it
// had already announced as available. Defaulted, so every caller that predates
// the parameter keeps exactly today's source and today's message.
function ghGet(pathname, token = process.env.GITHUB_TOKEN) {
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
//
// BOTH ENDPOINTS A VERDICT CAN ARRIVE ON (#1471, D13-01). The reviewer contract
// defines a verdict as a comment OR a review, and this read asked for the pull
// request and its issue comments only -- so a verdict posted as a review was
// invisible rather than unweighted, and `statsCoverageLine` reported that merge
// as one that carried none. `/pulls/<n>/reviews` is fetched here, and the two
// lists reach the walk as one stream. The cost is one request per pull request
// per window, counted by endpoint class in the D13 harness that drove this read.
//
// EXPORTED for one reason, the same one `statsCoverageLine` carries: the read is
// the half no assertion over `statsHistogram` can reach, so a check drives this
// with a stub `curl` first on PATH and reads the ledger it leaves -- which is
// how the finding measured it.
export function fetchWindow(prs) {
  const slug = repoSlug()
  if (!slug) return { fetched: new Map(), fetchError: 'no github remote on origin' }
  const fetched = new Map()
  for (const { pr } of prs) {
    const body = ghGet(`/repos/${slug}/pulls/${pr}`)
    if (!body.ok) return { fetched: new Map(), fetchError: body.why }
    const comments = ghGet(`/repos/${slug}/issues/${pr}/comments?per_page=100`)
    if (!comments.ok) return { fetched: new Map(), fetchError: comments.why }
    const reviews = ghGet(`/repos/${slug}/pulls/${pr}/reviews?per_page=100`)
    if (!reviews.ok) return { fetched: new Map(), fetchError: reviews.why }
    fetched.set(pr, {
      body: body.data?.body ?? '',
      comments: Array.isArray(comments.data) ? comments.data : [],
      reviews: Array.isArray(reviews.data) ? reviews.data : [],
    })
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
// `citation-presence` joins them on the same ground one axis over: recording
// "this exclusion lost the citation that earned it" as a known defect leaves the
// unearned exclusion standing, which is the destination the check exists to close.
const NEVER_SUPPRESSED = new Set(['budgets', 'coverage', 'provenance', 'named-docs', 'citation-presence'])

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

// `--list`'s registry. `cmdList` iterates THIS array, a different registry from
// `CORPUS_CHECK_NAMES` above: the names there decide what RUNS over the corpus,
// the entries here decide what a seat asking `--list` can DISCOVER. The two
// drifted once -- `orphan-caps`, `row-freeze` and `rule-binding` ran on every
// pull request while `--list` never named them (#1137) -- so each entry that
// lists a wired check carries `fn`, the production function it stands for, and
// `assertAcceptance` holds both directions of that correspondence.
//
// WHY `fn` IS CARRIED RATHER THAN DERIVED. The two names do not follow from each
// other's spelling in general -- `coverageOverTree` reports as `coverage`,
// `orphanCapsOverTree` as `orphan-caps` -- and a regex over this source that
// re-derives one from the other is the defect the corpus list's own comment
// names. `fn` is the correspondence stated where it is read. An entry with no
// `fn` is a check outside the corpus sweep: the `lintFile` pass (`citations`,
// `counts`, `no-gh`), the body contract (`pr-body`), or a loop-mode output.
const CHECKS = [
  { name: 'citations', what: 'paths, path:line and symbols in policy prose resolve', fixture: 'fixtures/policy-rot/citations.md' },
  { name: 'counts', what: 'a literal count matches its derivation', fixture: 'fixtures/policy-rot/counts.md' },
  { name: 'no-gh', what: 'no `gh <verb>` outside the MCP mapping table', fixture: 'fixtures/policy-rot/no-gh.md' },
  { name: 'budgets', fn: 'checkBudgets', what: 'a policy file may shrink, never grow past its cap', fixture: 'fixtures/policy-rot/budgets.md' },
  { name: 'orphan-caps', fn: 'orphanCapsOverTree', what: 'a recorded cap whose file no policy glob matches', fixture: '(driven in assertAcceptance)' },
  { name: 'index', fn: 'checkIndex', what: 'CLAUDE.md names every policy file, and every file it names exists', fixture: 'fixtures/policy-rot/index.md' },
  { name: 'duplicates', fn: 'checkDuplicates', what: 'no 12-word run shared between two policy files', fixture: 'fixtures/policy-rot/dup-a.md' },
  { name: 'pr-body', what: 'a body carries its evidence sections, at the head CI ran', fixture: 'fixtures/policy-rot/prepr/' },
  { name: 'named-docs', fn: 'namedDocsOverTree', what: 'a document the corpus names but no cap measures', fixture: '(driven in assertAcceptance)' },
  { name: 'citation-presence', fn: 'citationPresenceOverTree', what: 'a citation that earned a CORPUS_EXCLUDED line is still there', fixture: '(driven in assertAcceptance)' },
  { name: 'coverage', fn: 'coverageOverTree', what: 'every file in a policy directory is matched by a glob', fixture: '(a probe file, see assertAcceptance)' },
  { name: 'provenance', fn: 'checkProvenance', what: "the known-bad ledger's recorded_at resolves from origin/main", fixture: '(driven in assertAcceptance)' },
  { name: 'required-contexts', fn: 'requiredContextsOverTree', what: 'the corpus\'s required-context literals and recorded shape match the live ruleset', fixture: '(driven in assertAcceptance; live state, never fixtures, in production)' },
  { name: 'row-freeze', fn: 'rowFreezeOverPlan', what: 'the plan\'s delivery table stays within its frozen row and anchor counts', fixture: '(driven in assertAcceptance)' },
  { name: 'rule-binding', fn: 'ruleBindingOverTree', what: 'every `paths:` glob matches a tracked file, and every capped policy file is bound by a rule', fixture: '(driven in assertAcceptance)' },
  { name: 'record', what: 'every merged pull request has a disposition (refuses)', fixture: 'fixtures/policy-loop/merged-subjects.txt' },
  { name: 'render', what: 'disposition documents render with the same structure as their source', fixture: 'fixtures/policy-loop/render-cells-rotten.md' },
  { name: 'stats', what: 'verdict and friction histograms, and what they would open', fixture: 'fixtures/policy-loop/pr-payloads.json + friction-keys.json' },
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
  counts: { count: 13, must: ['for the cap on'] },  // two literal counts, one stated cap per regex shape, one per glue word, the number-first form, and one in the loop fixture
  table: { count: 1, must: ['ends the table here'] },
  render: {
    count: 4,
    must: [
      'different cell count from its header',
      'pipe-block(s) with a delimiter',
      'renders as ordinal',
      'does not resolve to a pull request or issue',
    ],
  },
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
    count: 8,
    must: [
      'section. Every one is content',   // a heading that is missing outright
      'no `## Figures` section',         // the figures section specifically, pinned by name
      'is empty. Write the evidence',    // a heading with nothing under it
      'does not name',                   // the body's head is not the head CI ran
      'is not in the tree. A carry',     // a forward-carry destination that is gone
      'does not parse',                  // an unreadable friction line
      'does not parse: "- a second bullet',  // a bullet after a labelled entry opens an entry; it is not folded
      'does not parse: "`budgets`: `annoying`',  // a class outside the five is refused, not read as an id
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
    count: 19,
    must: [
      // The rule id at threshold, keyed on the FILE the entry names: the
      // fixture writes it `CLAUDE.md#budgets`, and a fragment names a section
      // of a document rather than a second document.
      'would open "[policy] recurring friction: CLAUDE.md" --',
      'is the passing verdict',                                       // the class that is not rework
      'outside the grammar in .claude/workflows/web-fix-wave.js',     // the grammar drifting
      'could not fetch pull-request bodies and comments',             // the opposite-claims guard
      // #1240 (D13-03): the verdict arm keys blocked verdicts by the FULL
      // grammar -- the block classes VERDICT_CLASSES teaches -- instead of one
      // constant `blocked` key (the tautology exclusion now fires only when
      // VERDICT_CLASSES is unreadable, and that degraded arm is driven in
      // tests/entities.py). The three witnesses live in
      // fixtures/policy-loop/friction-keys.json, one per pull request: a
      // TAUGHT class word keys itself, an UNtaught word is its own row
      // (never folded into `other`), and a bare `blocked <sha>` routes to
      // `other`. The sha-less `blocked —` lines in both fixtures are the
      // outside-grammar rows above.
      'would open "[policy] recurring friction: null-control"',
      'would open "[policy] recurring friction: harness-typo"',
      'would open "[policy] recurring friction: other"',
      // fixtures/policy-loop/friction-keys.json. Three spellings of one rule
      // over three pull requests collapse to one key at 3 distinct PRs...
      'would open "[policy] recurring friction: .claude/rules/gate-scoping.md"',
      // ...a section-qualified spelling goes with its stem...
      'would open "[policy] recurring friction: .claude/skills/steward/SKILL.md"',
      // ...and the null control on that suffix rule: two ids that each resolve
      // in their own right stay two keys, at 3 apiece rather than one at 6.
      'would open "[policy] recurring friction: .claude/rules/defect-root-cause.md"',
      'would open "[policy] recurring friction: tools/audit/briefs/root-cause.md"',
      // ...and the role-name carve-out, both directions. A BARE role name is
      // the seat, not the seat's contract -- it files under its own text...
      'would open "[policy] recurring friction: orchestrator"',
      'would open "[policy] recurring friction: fixer-dispatch"',
    ],
    // The fixture puts the passing class OVER the threshold on purpose, so the
    // first of these is a pin and not a vacuous one: without the exclusion the
    // same window produces that line. The rest are the three ways the keying
    // was wrong -- a verdict key that could only ever be `blocked`, a rule
    // filed twice under two spellings, and a key that recurs in one body and
    // nowhere else.
    mustNot: [
      'would open "[policy] recurring friction: merge"',
      'would open "[policy] recurring friction: blocked"',
      'would open "[policy] recurring friction: gate-scoping.md"',
      'would open "[policy] recurring friction: steward-S10"',
      'would open "[policy] recurring friction: CLAUDE.md#budgets"',
      'would open "[policy] recurring friction: claim-files"',
      'would open "[policy] recurring friction: .claude/rules/claim-files.md"',
      // ...and the contract is never filed for a dispatch's friction. The
      // fixture puts three bare `orchestrator` entries on three pull requests
      // beside ONE `orchestrator.md`, so without the carve-out this line is
      // exactly what the same window produces, at 4.
      'would open "[policy] recurring friction: tools/audit/briefs/orchestrator.md"',
      'would open "[policy] recurring friction: tools/audit/briefs/fixer.md"',
    ],
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

CORPUS_CHECKS.push(checkIndex, checkDuplicates, checkBudgets, coverageOverTree, namedDocsOverTree, citationPresenceOverTree, orphanCapsOverTree, requiredContextsOverTree, checkProvenance, rowFreezeOverPlan, ruleBindingOverTree)

// SILENT ON A HEALTHY INPUT. A count-and-substring pin proves a check can still
// refuse; it cannot prove the check is not refusing everything. Each loop mode
// is therefore also run against a fixture that is healthy in exactly the way the
// rot fixture is rotten, and must produce nothing.
const REQUIRED_SILENT = ['record', 'stats', 'sunset', 'table', 'caps', 'render']

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
    if (f === 'needs-approval.md') continue
    const errs = checkPrBody(rel, { head: ZERO, red: f === 'unnamed-red.md' ? ['fast (3.14)'] : [] })
    if (f === 'good.md' && errs.length) {
      console.log(`\nFIXTURE VACUOUS: the pr-body null control ${rel} produced ${errs.length} error(s); it must produce none`)
      return 1
    }
    found.push(...errs)
  }

  // The author check (decision 0011): a body authored as tvofi — or any
  // identity other than the hpo-author App — is refused; the App and an absent
  // author are the null controls that must stay silent. One arm alone would
  // pin a check that always fires or never does.
  {
    const rel = path.relative(ROOT, path.join(prepr, 'good.md'))
    const wrong = checkPrBody(rel, { head: ZERO, author: 'tvofi' })
    const right = checkPrBody(rel, { head: ZERO, author: 'app/hpo-author' })
    const rightBot = checkPrBody(rel, { head: ZERO, author: 'hpo-author[bot]' })
    const absent = checkPrBody(rel, { head: ZERO })
    if (!wrong.some((e) => /hpo-author App/.test(e.message))) {
      console.log('\nFIXTURE VACUOUS: the author check did not fire on a tvofi-authored body')
      return 1
    }
    if (right.length || rightBot.length || absent.length) {
      console.log('\nFIXTURE VACUOUS: the author check fired on the App (either form) or on an absent author (the null controls)')
      return 1
    }
  }

  // `## Approval` is keyed on the DIFF, so one fixture is driven twice and the
  // pair is the check: the same body with a policy path in the diff must be
  // refused, and with a non-policy path must be silent. One arm alone would pin
  // a check that always fires or never does.
  const needsApproval = path.join(prepr, 'needs-approval.md')
  if (!fs.existsSync(needsApproval)) {
    console.log('\nFIXTURE VACUOUS: fixtures/policy-rot/prepr/needs-approval.md is missing; the diff-keyed approval gate is deletable in silence')
    return 1
  }
  {
    const rel = path.relative(ROOT, needsApproval)
    const onPolicy = checkPrBody(rel, { head: ZERO, paths: ['CLAUDE.md'] })
    const offPolicy = checkPrBody(rel, { head: ZERO, paths: ['README.md'] })
    if (!onPolicy.some((e) => /Approval/.test(e.message))) {
      console.log('\nFIXTURE VACUOUS: the approval gate did not fire on a diff touching CLAUDE.md')
      return 1
    }
    if (offPolicy.length) {
      console.log(`\nFIXTURE VACUOUS: the approval gate fired on a diff touching no policy path (${offPolicy.length} error(s)); it would refuse every pull request`)
      return 1
    }
    found.push(...onPolicy)

    // The refusals are the headline property, so they are pinned rather than
    // trusted: an unreadable list and an empty one must each produce an error,
    // and a real list must produce none. Without these three, deleting either
    // refusal leaves this acceptance green and the empty case fail-open.
    const missing = pathsFromFile(path.join(prepr, 'no-such-list.txt'))
    const empty = pathsFromFile(path.join(prepr, 'paths-empty.txt'))
    const real = pathsFromFile(path.join(prepr, 'paths-real.txt'))
    if (!missing.error || !/unreadable/.test(missing.error)) {
      console.log('\nFIXTURE VACUOUS: an unreadable --paths-file did not refuse; the approval gate would read a failed derivation as an empty diff')
      return 1
    }
    if (!empty.error || !/is empty/.test(empty.error)) {
      console.log('\nFIXTURE VACUOUS: an empty --paths-file did not refuse; a pull request changes at least one file')
      return 1
    }
    if (real.error || !real.paths.includes('CLAUDE.md')) {
      console.log(`\nFIXTURE VACUOUS: a real --paths-file did not read back (${real.error ?? real.paths.join(',')}); a refusal that fires on everything pins nothing`)
      return 1
    }
  }

  // The wiring is the half a fixture cannot reach, and round two measured the
  // cost of leaving it unpinned: dropping `--paths-file` from governance.yml
  // restores R3-D11-03 exactly, and dropping `--no-renames` reopens the rename
  // hole, and BOTH leave every instrument in this repository green. So the
  // step's own text is read here. This asserts the flags are passed, not that
  // GitHub runs the job -- no check in a repository can assert the second.
  const WORKFLOW = '.github/workflows/governance.yml'
  const wf = read(WORKFLOW)
  if (wf == null) {
    console.log(`\nFIXTURE VACUOUS: ${WORKFLOW} is unreadable, so the approval gate's wiring is unpinned`)
    return 1
  }
  // On the INVOCATIONS, not on any occurrence, and this is the third attempt.
  // The first asserted `wf.includes(flag)` and passed while the flag survived
  // only in a comment eight lines above the command. The second selected lines
  // matching a regex that CONTAINED the flag, so the flag text surviving in a
  // trailing shell comment or in the step's `name:` defeated it -- a reviewer
  // drove both. Selecting by what a line mentions cannot work when the needle
  // is what is being looked for, so this cuts the step's `run:` block by
  // indentation first and strips comments second.
  //
  // IT IS STILL NOT SOUND, and saying so is the point. No ratio is stated here
  // and that is deliberate: the set of carriers is open, every review round has
  // added one, and a fraction over a set anyone can extend is not a coverage
  // figure. What it refuses, stated as shapes: either flag deleted, or left
  // behind in a trailing comment, or left in the step's `name:`.
  //
  // What defeats it is one class -- a command that MENTIONS the flag without
  // passing it. A `:` no-op, an echo, a printf, a heredoc and a plain shell
  // assignment are all that shape, and so is a decoy `run: |` block anywhere in
  // the file. The decoy is the worst of them, because it means the subject is
  // "some block mentions this text": with one in place, the path-derivation
  // step or the body-check step can be deleted outright and this stays green.
  // Pointing --paths-file at a path nothing writes passes too, because a
  // filename is not a file.
  //
  // The class is exact: a command that MENTIONS the flag without passing it
  // defeats any text match, so anyone wanting soundness must parse the YAML and
  // read the argv of the invocation. String-matching moves the carrier, it does
  // not close it. What is pinned here is the rot seen in the wild twice -- the
  // flag deleted, and the flag left behind in a comment.
  const runBlocks = []
  {
    const lines = wf.split('\n')
    for (let i = 0; i < lines.length; i++) {
      const m = /^(\s*)run:\s*\|?\s*$/.exec(lines[i])
      if (!m) continue
      const indent = m[1].length
      const body = []
      for (let j = i + 1; j < lines.length; j++) {
        const l = lines[j]
        if (l.trim() && (l.length - l.trimStart().length) <= indent) break
        body.push(l.replace(/#.*$/, ''))
      }
      runBlocks.push(body.join('\n'))
    }
  }
  const bodyCheck = runBlocks.filter((b) => /policy_lint\.mjs/.test(b) && /--pr-body/.test(b)).join('\n')
  const pathsDerive = runBlocks.filter((b) => /git diff/.test(b) && /--name-only/.test(b)).join('\n')
  for (const [where, hay, flag, why] of [
    ['the body-check invocation', bodyCheck, '--paths-file', 'the approval gate would fall back to the title alone, which is R3-D11-03 restored'],
    ['the path derivation', pathsDerive, '--no-renames', 'a rename is reported by its destination only, so moving a policy file out of the glob set would not fire the gate'],
  ]) {
    if (!hay.includes(flag)) {
      console.log(`\nFIXTURE VACUOUS: ${WORKFLOW} no longer passes ${flag} in ${where}; ${why}`)
      return 1
    }
  }

  // The template and the parser's required set drift apart the moment either is
  // edited alone, and the seat that pays is one following a template that no
  // longer satisfies the job. Linting the template as if it were a body ties
  // them together: a heading the parser requires and the template omits fails
  // here, on the pull request that removed it.
  //
  // AND IT REFUSES, rather than reporting into `found` (#1195, D11-05). The arm
  // used to push its findings and continue: the template failed `--pr-body`
  // while the acceptance -- the `policy-docs` context that runs it -- exited 0,
  // so a violation of the contract the template states was reported into green.
  // `return 1` is the wiring every sibling FIXTURE VACUOUS arm above already
  // uses, and it is what turns the arm's finding into the acceptance's refusal.
  //
  // THE PATH IS OVERRIDABLE BY `POLICY_LINT_TEMPLATE`, for the one drive this
  // arm cannot get on a healthy tree: the template holds, the refusal below
  // never fires, and the wiring has no witness. `tests/entities.py` points it at
  // a body that drops a required heading and reads the acceptance's exit status;
  // the same run with the real template is its null control. The path is
  // resolved from this module's root, so the override is a clone-relative path.
  const TEMPLATE = process.env.POLICY_LINT_TEMPLATE || '.github/PULL_REQUEST_TEMPLATE.md'
  if (read(TEMPLATE) != null) {
    const errs = checkPrBody(TEMPLATE)
    if (errs.length) {
      console.log(`\nFIXTURE VACUOUS: ${TEMPLATE} does not satisfy the contract it exists to state`)
      return 1
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
  found.push(...checkTableSplit('fixtures/policy-loop/dispositions-rotten.md', loop.dispositionsRotten))
  // The cap rule alone: handing checkCounts a derivations object with only
  // `caps` runs only that rule, the same way brief_lint withholds `modules`.
  found.push(...checkCounts('fixtures/policy-loop/dispositions-rotten.md', loop.dispositionsRotten, { caps: derived.caps }))
  // One rotten fixture per render shape (#682). A single combined file would
  // let three of the four comparisons be deleted as long as one still fired.
  const RENDER_SHAPES = ['cells', 'tables', 'lists', 'links']
  const renderSilent = []
  for (const shape of RENDER_SHAPES) {
    const rotRel = `fixtures/policy-loop/render-${shape}-rotten.md`
    const okRel = `fixtures/policy-loop/render-${shape}-healthy.md`
    const rot = read(`.claude/workflows/${rotRel}`)
    const ok = read(`.claude/workflows/${okRel}`)
    if (rot == null || ok == null) {
      console.log(`\nFIXTURE VACUOUS: render fixture for ${shape} is missing; that comparison is deletable in silence`)
      return 1
    }
    found.push(...checkRender(rotRel, rot))
    renderSilent.push(...checkRender(okRel, ok))
  }


  found.push(...statsFindings({ prs: loop.prs, fetched: loop.fetched, fetchError: null, classes: loop.classes }))
  found.push(...statsFindings({ prs: loop.prs, fetched: new Map(), fetchError: 'fixture: the API was not reachable', classes: loop.classes }))
  // The keying window: normalization, distinct-PR recurrence, and the verdict
  // arm's tautology, each with its null control inside the fixture.
  found.push(...statsFindings({ prs: loop.keysPrs, fetched: loop.keysFetched, fetchError: null, classes: loop.classes }))
  found.push(...checkSunset(loop.sunsetRot, { friction: loop.friction, fires: loop.fires, today: loop.today }))
  found.push(...checkSunset(loop.sunsetRot, { friction: null, fires: loop.fires, today: loop.today }))

  // Silent on a healthy input. Reported as its own failure line rather than
  // folded into the counts: a check that fires on everything satisfies every
  // count and every substring, and is exactly as useless as one that fires on
  // nothing.
  const silent = {
    record: checkRecord(loop.prs, loop.dispositionsHealthy),
    table: checkTableSplit('fixtures/policy-loop/dispositions-healthy.md', loop.dispositionsHealthy),
    caps: checkCounts('fixtures/policy-loop/dispositions-healthy.md', loop.dispositionsHealthy, { caps: derived.caps }),
    render: [
      ...checkRender('fixtures/policy-loop/dispositions-healthy.md', loop.dispositionsHealthy),
      ...renderSilent,
    ],
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

  // The enumeration guard's loud half, pinned on SHAPE because it produces no
  // findings for any count above to see. The subject fallback is a SILENT zero
  // on merge-commit subjects (#1043 review, residual 2), and this line is the
  // only thing standing between that zero and a green that measured nothing --
  // so the pin asserts the three properties the discipline owes: the `skip`
  // lead, the `UNCHECKED this run, not confirmed` claim, and that the `why`
  // actually reached the line. Emptying enumSkipLine (the LOOP_CHECK_NAMES
  // mutation) fails here.
  pins += 1
  const enumSkip = enumSkipLine('fixture: GITHUB_TOKEN is not set')
  if (!/^\s*skip\s+merge-enumeration\b/.test(enumSkip) || !enumSkip.includes('UNCHECKED this run, not confirmed') || !enumSkip.includes('fixture: GITHUB_TOKEN is not set')) {
    console.log('\nFIXTURE VACUOUS: the merge-enumeration fetch-failure marker lost its skip/UNCHECKED shape; a dead fetch would then keep rc=0 with `0 merged pull request(s)` reading as a measured window rather than an unchecked one')
    rc = 1
  }

  // The window guard's OTHER half, pinned on SHAPE for the same reason: it
  // produces no findings either. The three properties this one owes are the
  // `refuse` lead, the `could not be DERIVED` claim that separates it from an
  // empty window, and that BOTH the ref and the range reached the line -- a
  // marker that names neither cannot be acted on by the seat reading it.
  pins += 1
  const badRef = badRefLine('6.5.0', '--record', '6.5.0..origin/main')
  if (!/^\s*refuse\s+since-ref\b/.test(badRef) || !badRef.includes('could not be DERIVED') || !badRef.includes('6.5.0') || !badRef.includes('6.5.0..origin/main')) {
    console.log('\nFIXTURE VACUOUS: the since-ref marker lost its refuse/DERIVED shape; an unresolvable --since would then print `0 merged pull request(s)` at rc=0, which is what `--since $(cat VERSION)` did at d1a531b while `--since v$(cat VERSION)` reported 16')
    rc = 1
  }

  // ITS NULL CONTROL, and the half the shape pin cannot reach: a marker with a
  // perfect shape is worthless if the predicate that reaches it fires on
  // everything, or on nothing. `HEAD` resolves in any checkout this acceptance
  // can run in at all; the second name cannot resolve anywhere, and is not a
  // path in the tree either, so `^{commit}` is the only thing being asked.
  // Both directions, because a guard asserted in one direction is the
  // over-firing shape this file keeps refusing elsewhere.
  pins += 2
  if (!resolvesToCommit('HEAD')) {
    console.log('\nFIXTURE VACUOUS: the since-ref predicate refuses HEAD, so it would refuse every window and the guard is an outage rather than a check')
    rc = 1
  }
  if (resolvesToCommit('no-such-ref-6f2a1c9e-policy-lint-acceptance')) {
    console.log('\nFIXTURE VACUOUS: the since-ref predicate accepts a name that resolves to nothing, so an unresolvable --since reaches the enumerator and the marker above is unreachable')
    rc = 1
  }

  // The sunset class's marker census, pinned on SHAPE and at BOTH ENDS (#1469,
  // D11-03). It produces no findings -- it is the line that says what the
  // `proposed (0) held (0)` beneath it is a zero of -- so the counts above cannot
  // see it. One end is the corpus as it stands: no marker, and the line must SAY
  // so, because a bare zero beside a class that fires on markers reads as a
  // swept corpus. The other end is a row that carries a marker: the counts must
  // move, or the line is a caption rather than a census and the first assertion
  // is satisfied by any constant string. Emptying `sunsetMarkerLine` (the
  // LOOP_CHECK_NAMES mutation) fails both.
  pins += 2
  const noMarkers = sunsetMarkerLine([{ file: 'fixture.md', text: '# a rule, with no marker of its own\n' }])
  const oneMarker = sunsetMarkerLine([{ file: 'fixture.md', text: '- (expiry) SUNSET: 2020-01-01\n' }])
  if (!/^SUNSET MARKERS: 1 policy file\(s\) scanned; /.test(noMarkers)
      || !noMarkers.includes('REFUSED BY 0') || !noMarkers.includes('SUNSET: 0') || !noMarkers.includes('HONOUR: 0')
      || !noMarkers.includes('PARTICIPATION zero')) {
    console.log('\nFIXTURE VACUOUS: the sunset marker census does not name the corpus\'s marker population, so `proposed (0) held (0)` prints with nothing to say whether a rule has outlived its reason or no rule carries a marker at all')
    rc = 1
  }
  if (!oneMarker.includes('SUNSET: 1') || !oneMarker.includes('has a population')) {
    console.log('\nFIXTURE VACUOUS: the sunset marker census reports the same reading over a corpus carrying a marker as over one carrying none, so it is a constant and not a count of the rows `checkSunset` walks')
    rc = 1
  }

  // THE RED HISTORY (#1144), driven with fixture runs so it runs with no
  // network, no git history and no token -- a pin that needed any of those
  // would be skipped on the machine where it matters. The property under pin is
  // the one the issue is about: a red at an EARLIER commit that the tip has
  // since cleared still owes an answer, so the loop over the commits must read
  // every entry and not only the last. Its null control is the same fixture
  // with every conclusion green, which must produce no name at all: a
  // derivation that fired on everything would satisfy the first assertion.
  pins += 3
  const CLEARED = {
    c1: [
      { name: 'fast (3.14)', status: 'completed', conclusion: 'failure' },
      { name: 'typing', status: 'completed', conclusion: 'failure' },
      { name: 'pr-contract', status: 'completed', conclusion: 'failure' },
      { name: 'mutation', status: 'completed', conclusion: 'skipped' },
      { name: 'nightly-status', status: 'in_progress' },
      { name: 'fast (3.14)', status: 'completed', conclusion: 'failure' },
    ],
    c2: [
      { name: 'fast (3.14)', status: 'completed', conclusion: 'success' },
      { name: 'typing', status: 'completed', conclusion: 'success' },
    ],
  }
  const redUnion = redsOverCommits(['c1', 'c2'], (sha) => ({ ok: true, runs: CLEARED[sha] }))
  if (!redUnion.ok || redUnion.reds.join(',') !== 'fast (3.14),typing') {
    console.log(`\nFIXTURE VACUOUS: the red history over a pull request's commits is ${redUnion.ok ? JSON.stringify(redUnion.reds) : `not ok (${redUnion.why})`}, not ["fast (3.14)","typing"]; a red a later commit cleared must still be on it, this job's own runs and every non-\`failure\` conclusion must not, and a name earned twice is owed once`)
    rc = 1
  }
  const redClean = redsOverCommits(['c1', 'c2'], (sha) =>
    ({ ok: true, runs: CLEARED[sha].map((r) => ({ ...r, conclusion: 'success' })) }))
  if (!redClean.ok || redClean.reds.length) {
    console.log('\nFIXTURE VACUOUS: the red history names a check over a range that failed nothing, so the derivation is not reading the run objects it is handed')
    rc = 1
  }
  // The enforcement, driven on the DERIVED names rather than on a hand-written
  // list: `unnamed-red.md`'s `## Red checks` says `none`, so the red a later
  // commit cleared has to reach the same refusal the head's own red does.
  const clearedRefusals = checkPrBody(path.relative(ROOT, path.join(prepr, 'unnamed-red.md')), { head: ZERO, red: redUnion.reds })
  if (clearedRefusals.length !== 2) {
    console.log(`\nFIXTURE VACUOUS: a body whose \`## Red checks\` does not name the two earlier-head reds produced ${clearedRefusals.length} error(s), not 2; the derived names have to reach the refusal the --red path already drives`)
    rc = 1
  }
  // Both markers on SHAPE, for the reason `enumSkipLine`'s pin above gives: they
  // carry no finding, so no count can see them. The skip line is the only thing
  // between an unread history and a green that measured nothing, and the record
  // line is the only trace an already-cleared red leaves.
  pins += 2
  const redSkip = redHistorySkipLine('fixture: neither GITHUB_TOKEN nor GH_TOKEN is set')
  if (!/^\s*skip\s+red-history\b/.test(redSkip) ||
      !redSkip.includes('UNCHECKED this run, not confirmed clean') ||
      !redSkip.includes('fixture: neither GITHUB_TOKEN nor GH_TOKEN is set')) {
    console.log('\nFIXTURE VACUOUS: the red-history skip marker lost its skip/UNCHECKED shape; an unread history would then read as a clean one, which is the fail-open #1144 is about')
    rc = 1
  }
  const redRec = redHistoryRecordLine(3, ['typing'])
  if (!/^\s*record\s+red-history\b/.test(redRec) || !redRec.includes('3 commit') || !redRec.includes('typing')) {
    console.log('\nFIXTURE VACUOUS: the red-history record marker does not name what was read, so a head that went red and then green leaves no trace -- which is the whole point of recording it')
    rc = 1
  }


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
  // AND THE REGION THE RECORD READS, which had no pin at all: `recordRegion`
  // could be emptied to `return { region: everything, sectionFound: out.length > 0 }` and
  // every count above would still hold, because the fixtures hand `checkRecord`
  // its text directly. Assertions on synthetic input rather than on the
  // live plan, so a section renamed in the tree cannot make them pass:
  // a mention inside the section counts, the same mention outside it does not,
  // and a plan with no such heading reports the absence rather than an empty
  // region. The third is the one that keeps this fail-closed: an empty region
  // would otherwise read as "every merge undispositioned", which is a true
  // statement about the wrong thing.
  pins += 14
  const regIn = recordRegion(`## ${RECORD_SECTION}\n- [#9101](x/pull/9101) merged\n`, '')
  const regOut = recordRegion(`## Carried findings\n- found by #9101 in passing\n`, '')
  const regNone = recordRegion('# plan\nno second-level heading at all\n', '')
  // The fourth fixture is TWO sections, and it is the one the first three could
  // not stand in for: each of those is single-section, so a region that OPENS
  // correctly and never CLOSES satisfies all three. One token does that --
  // `if (h2) inside = …` becoming `if (h2 && …) inside = true` -- and the
  // acceptance stayed green under it, with the whole plan back in the region.
  // Found by #658's round 1, on the pin rather than on the code.
  const regBoth = recordRegion(
    `## ${RECORD_SECTION}\n- [#9101](x/pull/9101) merged\n\n## Carried findings\n- found by #9102 in passing\n`, '')
  const regFail = []
  if (checkRecord([{ pr: '9101', subject: 's' }], regIn.region).length !== 0) regFail.push('a disposition INSIDE the section did not count')
  if (checkRecord([{ pr: '9101', subject: 's' }], regOut.region).length !== 1) regFail.push('a mention OUTSIDE the section counted as a disposition')
  if (regNone.sectionFound) regFail.push('a plan with no section heading reported one')
  if (checkRecord([{ pr: '9102', subject: 's' }], regBoth.region).length !== 1) regFail.push('the region did not CLOSE at the next section heading')
  if (checkRecord([{ pr: '9101', subject: 's' }], regBoth.region).length !== 0) regFail.push('the region did not cover its own section when another follows')
  // AND THE HANDOVER HALF, which the assertions above did not reach: dropping
  // `handoverText` from the returned region passed every one of them and left
  // the live `--record` at 0 undispositioned, so the design property this
  // change states -- the handover contributes ALL of itself, which is why it is
  // not demoted -- was unpinned prose. #658's round 2 drove ten mutations and
  // this is the one that survived and mattered.
  // TWO lines, because one holds only "the handover contributes something":
  // `handoverText.split('\n')[0]` passed a one-line fixture. #658's round 4
  // drove the strengthened form with a null control and it costs no pin.
  const regHand = recordRegion('## other\n', 'a first line\n- [#9103](x/pull/9103) merged in the handover\n')
  if (checkRecord([{ pr: '9103', subject: 's' }], regHand.region).length !== 0) regFail.push('a disposition in the handover did not count')
  // AND A THIRD-LEVEL HEADING MUST NOT CLOSE THE REGION. Widening the match to
  // `^#{1,3}` is a plausible edit and survived every assertion above it, while
  // taking most of the window undispositioned: the plan keeps a
  // `### Governance queue` subsection INSIDE `## Delivery status`, and this
  // pull request writes its own row into it. Reported by #658's round 3 as the
  // one survivor of ten that a reader might actually write.
  const regSub = recordRegion(
    `## ${RECORD_SECTION}\n### a subsection\n- [#9104](x/pull/9104) merged\n`, '')
  if (checkRecord([{ pr: '9104', subject: 's' }], regSub.region).length !== 0) regFail.push('a third-level heading inside the section closed the region')
  // AND A MENTION INSIDE ANOTHER PULL REQUEST'S OWN ROW IS NOT A DISPOSITION
  // (#752). The region test was `#N` anywhere in the text, so a row that
  // DISCLAIMS responsibility for a number discharged the obligation for it: on
  // `main` the only occurrence of #741 was the sentence "#741 stays #745's",
  // written inside #748's row, and `record` reported 0 without a disposition.
  // The first arm is that live shape. The second is its null control on the same
  // line -- the row's own number is still dispositioned by the row it anchors,
  // which is what stops the fix from refusing the format it is defending.
  const regMention = recordRegion(
    `## ${RECORD_SECTION}\n- [#9105](x/pull/9105) merged. This dispositions #9105. #9106 stays #9107's.\n`, '')
  if (checkRecord([{ pr: '9106', subject: 's' }], regMention.region).length !== 1) regFail.push('a mention inside another pull request\'s anchored row counted as a disposition')
  if (checkRecord([{ pr: '9105', subject: 's' }], regMention.region).length !== 0) regFail.push('an anchored row stopped dispositioning its own pull request')
  // AND THE THREE SHAPES THE NARROWING MUST NOT REFUSE, each measured over the
  // window before the predicate was chosen and each the reason a plainer
  // predicate was rejected. A row anchor (`^- [#N]`) refuses all three; an
  // anchor extended to table rows refuses the last two.
  //   - a Delivery-status TABLE CELL, which is how the wave rows disposition;
  //   - a table row anchored to an ISSUE number, which is how the nightly rows
  //     disposition the pull request that closed them;
  //   - the handover's own format, a prose bullet that anchors nothing.
  const regCell = recordRegion(
    `## ${RECORD_SECTION}\n| item | state |\n|---|---|\n| linter | landed as #9108 |\n`, '')
  if (checkRecord([{ pr: '9108', subject: 's' }], regCell.region).length !== 0) regFail.push('a disposition written in a table cell was refused')
  const regIssueRow = recordRegion(
    `## ${RECORD_SECTION}\n| **#9109** the nightly probe | **CLOSED by [#9110](x/pull/9110), merged \`abc1234\`** |\n`, '')
  if (checkRecord([{ pr: '9110', subject: 's' }], regIssueRow.region).length !== 0) regFail.push('a disposition inside a row anchored to an ISSUE number was refused')
  const regHandProse = recordRegion('## other\n', '- **A seam move was sequenced to S12, S12 halted (#9111)** (owner)\n')
  if (checkRecord([{ pr: '9111', subject: 's' }], regHandProse.region).length !== 0) regFail.push("the handover's own prose-bullet disposition was refused")
  // AND THE SAME SUBTRACTION IN THE TABLE ROW, the format the Delivery-status
  // table is made of and the one the list anchor above cannot reach. Five arms,
  // because the three null controls are what separate this from the row anchor
  // #752 measured and rejected: a row anchored to an ISSUE number, and a cell
  // that links nothing, both still disposition everything on them -- those are
  // `regIssueRow` and `regCell` above, which run against this predicate too --
  // while a row that links its own pull request speaks for that one and its
  // prose stops dispositioning others.
  pins += 5
  const regTableRow = recordRegion(
    `## ${RECORD_SECTION}\n| a policy change | **in review -- PR [#9130](x/pull/9130)**, and #9131 landed the mechanism |\n`, '')
  if (checkRecord([{ pr: '9131', subject: 's' }], regTableRow.region).length !== 1) regFail.push("a mention inside another pull request's anchored TABLE row counted as a disposition")
  if (checkRecord([{ pr: '9130', subject: 's' }], regTableRow.region).length !== 0) regFail.push('an anchored table row stopped dispositioning its own pull request')
  // A row speaks for EVERY pull request it links, not only the first. Reading
  // one link per row is the plausible narrowing and has no witness above: it
  // would refuse the second of two pull requests a single status cell records.
  const regTwoLinks = recordRegion(
    `## ${RECORD_SECTION}\n| a split | landed as [#9132](x/pull/9132) and [#9133](x/pull/9133) |\n`, '')
  if (checkRecord([{ pr: '9132', subject: 's' }, { pr: '9133', subject: 's' }], regTwoLinks.region).length !== 0) regFail.push('a table row linking two pull requests dispositioned only one of them')
  // AND THE IDENTITY TEST, in the table form too: an anchor text and a link
  // naming different pull requests is ambiguous, so the row speaks for neither
  // and suppresses nothing -- the arm that favours accepting honest work.
  const regTableCross = recordRegion(
    `## ${RECORD_SECTION}\n| a row | [#9134](x/pull/9135) disagree, and #9136 landed here |\n`, '')
  if (checkRecord([{ pr: '9136', subject: 's' }], regTableCross.region).length !== 0) regFail.push('a table row whose anchor text and link name different pull requests suppressed a mention')
  // And the LIST form is still reached: a table-only predicate would pass every
  // arm above while re-opening #752 itself. `regMention` covers that, and this
  // states it rather than leaving it to be re-derived.
  if (speaksFor('- [#9137](x/pull/9137) merged') === null) regFail.push('the list anchor stopped speaking for its own pull request')
  // AND THE ANCHOR MUST NAME ITS OWN PULL REQUEST. Dropping that identity test
  // is a one-token cleanup with no witness above it: a row whose anchor text and
  // link disagree would then speak for the text, and suppress every other number
  // on the line. Ambiguous rows speak for nobody, which is the arm that favours
  // accepting a disposition over refusing honest work.
  const regCrossLink = recordRegion(
    `## ${RECORD_SECTION}\n- [#9112](x/pull/9113) the anchor text and the link disagree. #9114 landed here.\n`, '')
  if (checkRecord([{ pr: '9114', subject: 's' }], regCrossLink.region).length !== 0) regFail.push('a row whose anchor text and link name different pull requests suppressed a mention')
  // AND THE ROW FILES. A file dispositions its own number and nothing else: a
  // misnamed file, or another number in its prose, is refused; and files alone
  // never stand in for a missing section. Then the freeze, both counts, at the
  // cap and one over, with a second table and a later section as null controls.
  pins += 12
  const rowIn = recordRegion('## other\n', '', { 9115: '- [#9115](x/pull/9115) merged\n' })
  const rowBad = recordRegion(`## ${RECORD_SECTION}\n`, '', { 9116: '- [#9117](x/pull/9117) misnamed. #9118 too.\n' })
  if (checkRecord([{ pr: '9115', subject: 's' }], rowIn.region).length !== 0) regFail.push('a row file did not disposition its own pull request')
  if (checkRecord([{ pr: '9116', subject: 's' }, { pr: '9117', subject: 's' }, { pr: '9118', subject: 's' }], rowBad.region).length !== 3) regFail.push('a misnamed row file, or a number in its prose, counted as a disposition')
  if (rowIn.sectionFound) regFail.push('row files stood in for a missing section')
  const frz = (rows, anchors) => `## ${RECORD_SECTION}\n| a |\n|---|\n${'| r |\n'.repeat(rows)}\n| b |\n|---|\n| other table |\n${'- [#9120](x/pull/9120) r\n'.repeat(anchors)}## later\n| r |\n- [#9121](x/pull/9121) r\n`
  const cap = { rows: 3, anchors: 2 }
  if (checkRowFreeze(frz(2, 2), cap).length !== 0) regFail.push('a table AT its freeze was refused, or a second table or a later section was counted')
  if (checkRowFreeze(frz(3, 2), cap).length !== 1) regFail.push('a first table one row over its freeze was not refused')
  if (checkRowFreeze(frz(2, 3), cap).length !== 1) regFail.push('one anchored row over the freeze was not refused')
  if (checkRowFreeze(frz(3, 3), cap).length !== 2) regFail.push('the two freeze counts are not independent')
  if (checkRowFreeze(`# plan\n${'| r |\n'.repeat(50)}`, cap).length !== 0) regFail.push('rows outside the section were counted')
  if (checkRowFreeze(`## ${RECORD_SECTION}\n- [#9122](x/issues/9122) an issue's row\n- [#9123](x/pull/9124) r\n`, { anchors: 0 }).length !== 0) regFail.push('the freeze counted an issue-anchored or cross-linked item as a pull-request row')
  const liveSource = rowFreezeSource
  rowFreezeSource = () => frz(ROW_FREEZE.rows, 0)
  if (rowFreezeOverPlan().length !== 1) regFail.push('the wired freeze check does not read its source, or reads it against no freeze')
  rowFreezeSource = liveSource
  const liveRows = rowFileSource
  rowFileSource = () => [['9125.md', () => '- [#9125](x/pull/9125) r\n'], ['9126.txt', () => '- [#9126](x/pull/9126) r\n']]
  if (checkRecord([{ pr: '9125', subject: 's' }, { pr: '9126', subject: 's' }], recordRegionOverTree().region).length !== 1) regFail.push('the wired record region does not read the row files')
  rowFileSource = liveRows
  // AND `--record` REFUSES TO RUN WITH NO TOKEN. Driven as a SUBPROCESS, which
  // is not ceremony: `requireToken` ends in `process.exit`, so an in-process
  // assertion would take this acceptance down with it, and the property being
  // pinned is the WIRING -- that `cmdRecordDispositions` reaches the guard
  // before it reaches the enumeration. A pure helper asserted directly would
  // stay green with the call deleted, which is the exact shape that left this
  // mode passing on a window it never read.
  //
  // THE WINDOW IS EMPTY BY CONSTRUCTION, and the earlier `--since HEAD` was
  // not. That version asserted a property of the CLONE rather than of the
  // guard: `HEAD..origin/main` is empty only where `origin/main` is reachable
  // from `HEAD`, which is true on a `pull_request` checkout (the branch merged
  // into main) and false on a branch head and in a grafted or shallow clone.
  // `policy_lint_envmatrix.mjs`'s `shallow` shape is exactly that: measured
  // there, the window was the whole history, the run enumerated 611 merges over
  // the network and exited 1, and this arm reported FIXTURE VACUOUS at a head
  // whose merge base was green -- the instrument that exists to catch an
  // environment-dependent assertion caught this one.
  //
  // `mainRef()..mainRef()` is empty in EVERY clone, shallow, grafted or full,
  // because `git log X..X` is empty for any X that resolves -- and `mainRef()`
  // is the same function the window itself uses, so the two cannot drift apart.
  // `firstParentCommits` returns [], `fetchPullsBySha` iterates an empty list
  // and issues no request, and the null control reaches `TOTAL: 0` without a
  // socket. The refusing arm never gets that far. So both arms are offline on a
  // CI runner, on a seat with no network, and under every shape in the matrix.
  //
  // The null control is the whole point of the pair: a guard that exited 2
  // whenever `--record` ran at all would satisfy the first arm alone.
  pins += 3
  const emptyWindow = mainRef()
  const recRun = (env) => {
    try {
      return { code: 0, out: execFileSync(process.execPath, [path.join(HERE, 'policy_lint.mjs'), '--record', '--since', emptyWindow], { cwd: ROOT, encoding: 'utf8', env, stdio: ['pipe', 'pipe', 'pipe'] }) }
    } catch (e) {
      return { code: e.status === undefined ? 1 : e.status, out: `${e.stdout || ''}${e.stderr || ''}` }
    }
  }
  const envNoTok = { ...process.env }
  delete envNoTok.GITHUB_TOKEN
  const noTok = recRun(envNoTok)
  const withTok = recRun({ ...process.env, GITHUB_TOKEN: 'acceptance-fixture-not-a-credential' })
  if (noTok.code !== 2) regFail.push(`--record with no GITHUB_TOKEN exited ${noTok.code}, not 2: an unenumerated window reported as a measured one`)
  if (!/needs GITHUB_TOKEN/.test(noTok.out)) regFail.push('--record with no GITHUB_TOKEN did not say which variable it needs')
  if (withTok.code !== 0 || /needs GITHUB_TOKEN/.test(withTok.out)) regFail.push(`--record with a token set exited ${withTok.code} and must reach its verdict unchanged (null control)`)
  if (regFail.length) {
    console.log(`\nFIXTURE VACUOUS: recordRegion ${JSON.stringify(regFail)}. The record's region is what makes a mention a disposition; unpinned, it can be widened back to the whole file with every other count unchanged.`)
    return 1
  }

  // #677. The enumerator is the API's pull-request number, not the subject's
  // trailing `(#N)`. Two shapes, both silent in the shipped regex: a
  // suffix-less subject, and a suffix that names an issue. The subject-mode
  // fallback must still exhibit both defects and must still say it is the
  // fallback — that is how a reader tells the two modes apart.
  pins += 8
  const enumFail = []
  const enumCommits = [
    { sha: 'a'.repeat(40), subject: 'typing: snapshots.py annotations' },
    { sha: 'b'.repeat(40), subject: 'feat: something (#587)' },
    { sha: 'c'.repeat(40), subject: 'v6.3.19: stamp Seven leftover product features' },
    { sha: 'd'.repeat(40), subject: 'fix: the shipped catalog said eleven (#710)' },
  ]
  const enumApi = new Map([
    [enumCommits[0].sha, 656],
    [enumCommits[1].sha, 655],
    [enumCommits[3].sha, 710],
  ])
  const apiEnum = enumerateMerges(enumCommits, enumApi)
  if (apiEnum.mode !== 'api') enumFail.push('api mode not reported')
  if (!apiEnum.prs.some((p) => p.pr === '656')) enumFail.push('suffix-less subject invisible under api')
  if (apiEnum.prs.some((p) => p.pr === '587')) enumFail.push('issue suffix collected under api')
  if (!apiEnum.prs.some((p) => p.pr === '655')) enumFail.push('real PR for the issue-suffix subject missing under api')
  if (apiEnum.prs.some((p) => p.sha === enumCommits[2].sha)) enumFail.push('a stamp collected under api')
  if (!apiEnum.prs.some((p) => p.pr === '710')) enumFail.push('healthy suffix dropped under api')
  const subEnum = enumerateMerges(enumCommits, null)
  if (subEnum.mode !== 'subject') enumFail.push('subject mode not reported')
  if (subEnum.prs.some((p) => p.pr === '656')) enumFail.push('suffix-less collected under subject fallback')
  if (!subEnum.prs.some((p) => p.pr === '587')) enumFail.push('issue-suffix phantom not produced by subject fallback')
  if (subEnum.prs.some((p) => p.pr === '655')) enumFail.push('subject fallback invented the API number')
  if (enumFail.length) {
    console.log(`\nFIXTURE VACUOUS: enumerateMerges ${JSON.stringify(enumFail)}. The record's window is the API's pull-request set; unpinned, a suffix-less squash is invisible and a title ending in an issue number is demanded.`)
    return 1
  }

  pins += 1
  const wiredNames = CORPUS_CHECKS.map((f) => f.name || '(anonymous)').join(',')
  if (wiredNames !== CORPUS_CHECK_NAMES.join(',')) {
    console.log(`\nFIXTURE VACUOUS: CORPUS_CHECKS is wired as [${wiredNames}], expected [${CORPUS_CHECK_NAMES.join(',')}]. A check missing from the list never runs; one replaced by a no-op, a duplicate or an unwrapped \`checkCoverage\` runs and measures nothing. The count is derived from this list rather than carried, so adding a fifth check names it here once.`)
    return 1
  }

  // `--list` DISCOVERABILITY. The pin above holds what RUNS to
  // `CORPUS_CHECK_NAMES`; it says nothing about `CHECKS`, the separate registry
  // `cmdList` prints, so a check wired into the sweep but absent from `CHECKS`
  // runs on every pull request and is invisible to a seat asking `--list` which
  // checks exist -- exactly what happened to `orphan-caps`, `row-freeze` and
  // `rule-binding` (#1137). The entry's own `fn` carries the correspondence (see
  // `CHECKS`), and BOTH directions are held: a wired name no entry lists is a
  // check that runs undiscoverably, and an entry naming a function that is not
  // wired advertises a check that no longer runs. Duplicates are reported too,
  // because two entries for one function is a listing that over-reports just as
  // the missing three under-reported.
  pins += 1
  const listedFns = CHECKS.filter((c) => c.fn).map((c) => c.fn)
  const unlisted = CORPUS_CHECK_NAMES.filter((n) => !listedFns.includes(n))
  const unknown = listedFns.filter((n) => !CORPUS_CHECK_NAMES.includes(n))
  const dupes = listedFns.filter((n, i) => listedFns.indexOf(n) !== i)
  if (unlisted.length || unknown.length || dupes.length) {
    console.log(`\nFIXTURE VACUOUS: --list and the corpus sweep disagree. Wired but with no CHECKS entry: [${unlisted.join(', ')}] -- such a check runs on every pull request and no \`--list\` reader learns it exists. Listed but not wired: [${unknown.join(', ')}] -- such an entry advertises a check that no longer runs. Listed twice: [${dupes.join(', ')}]. Each entry that lists a wired check carries \`fn\`, and every name in CORPUS_CHECK_NAMES must appear on exactly one.`)
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

  // RULE BINDING, driven on the same terms and for the same reason. Each of its
  // three refusals is FALSE on a healthy tree, so none has a natural witness --
  // exactly the shape that shipped three checks measuring nothing, named in
  // policy_lint_mutants.mjs. The production default is pinned BEFORE the swap:
  // `() => []` there would make `checkRuleBinding` destructure an array, read
  // `tracked`, `corpus` and `rules` as undefined and throw rather than measure,
  // and `() => ({ tracked: [], corpus: [], rules: [] })` would scan an empty
  // tree silently, which is the coverage defect one file over.
  pins += 1
  const LIVE_BINDING = Symbol('live-rule-binding')
  if ((ruleBindingSource() ?? LIVE_BINDING) !== LIVE_BINDING) {
    console.log(`\nFIXTURE VACUOUS: ruleBindingSource's production default returned ${JSON.stringify(ruleBindingSource())}, which \`??\` does not discard. Only a nullish default makes checkRuleBinding read the tracked tree; any other model is measured instead, and an empty one measures nothing.`)
    return 1
  }
  // Through the WRAPPER, so what is wired is what is pinned.
  const driveBinding = (model) => {
    const prev = ruleBindingSource
    ruleBindingSource = () => model
    try { return ruleBindingOverTree() } finally { ruleBindingSource = prev }
  }
  const bindingClean = {
    tracked: ['CLAUDE.md', 'tools/audit/briefs/fixer.md', '.claude/rules/a-rule.md', 'src/app.py'],
    corpus: ['CLAUDE.md', 'tools/audit/briefs/fixer.md', '.claude/rules/a-rule.md'],
    rules: [{ file: '.claude/rules/a-rule.md', globs: ['CLAUDE.md', 'tools/audit/briefs/**', '.claude/rules/**'] }],
  }
  const bindingArms = [
    ['unscoped', { ...bindingClean, rules: [{ file: '.claude/rules/a-rule.md', globs: null }] }, 'declares no'],
    ['dead glob', { ...bindingClean, rules: [{ file: '.claude/rules/a-rule.md', globs: [...bindingClean.rules[0].globs, 'docs/gone/**'] }] }, 'matches no tracked file'],
    ['unbound corpus file', { ...bindingClean, rules: [{ file: '.claude/rules/a-rule.md', globs: ['.claude/rules/**'] }] }, 'no `.claude/rules/*.md` binds'],
  ]
  pins += bindingArms.length + 1
  for (const [name, model, needle] of bindingArms) {
    const hits = driveBinding(model)
    if (hits.some((f) => f.check === 'rule-binding' && f.message.includes(needle))) continue
    console.log(`\nFIXTURE VACUOUS: the rule-binding '${name}' arm produced ${JSON.stringify(hits.map((f) => f.message.slice(0, 60)))} against a model built to trip it. A refusal with no witness is deletable in silence.`)
    return 1
  }
  const bindingClear = driveBinding(bindingClean)
  if (bindingClear.length) {
    console.log(`\nFIXTURE OVER-FIRES: rule-binding produced ${bindingClear.length} finding(s) against a model where every glob matches, every corpus file is bound and no rule is unscoped, e.g. ${JSON.stringify(bindingClear[0].message.slice(0, 120))}`)
    return 1
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

  // The working band. Three properties, none of which has a witness on a
  // healthy corpus: it applies to the five aggregates, it does NOT apply to the
  // per-file caps, and the ratchet still bites one band later. Deleting
  // `_band`'s effect, or leaking it to the file comparison, are both plausible
  // one-token edits and each passes every pin above.
  //
  // The boundary is what pins the arithmetic. At cap = measured - band the
  // aggregates are exactly at their ceiling and the strict `>` must stay
  // silent, while the SAME caps refuse every file, which is the leak test. One
  // token lower and all three aggregates must fire -- `cap * 2`, `cap + 1e9`
  // and a band applied unconditionally all stay silent there.
  const BAND_PROBE = 500
  const banded = (delta) => ({ ...scaled(delta), _band: BAND_PROBE })
  pins += 3
  const atCeiling = checkBudgets(policyFiles(), banded(-BAND_PROBE))
  const ceilingClasses = new Set(atCeiling.map(classOf))
  for (const cls of ['floor', 'corpus', 'role']) {
    if (!ceilingClasses.has(cls)) continue
    console.log(`\nFIXTURE OVER-FIRES: the '${cls}' comparison fired with the cap one band below the measured value, so _band is not being added to it. A band nothing honours is a band that silently is not there.`)
    return 1
  }
  if (!ceilingClasses.has('file')) {
    console.log(`\nFIXTURE VACUOUS: the per-file comparison stayed silent with every file cap ${BAND_PROBE} below its measured size, so _band is leaking into the per-file caps. Those are a per-document ratchet and are compared exactly; a band there buys silent growth in every capped file at once.`)
    return 1
  }
  const pastBand = new Set(checkBudgets(policyFiles(), banded(-BAND_PROBE - 1)).map(classOf))
  for (const cls of ['floor', 'corpus', 'role']) {
    if (pastBand.has(cls)) continue
    console.log(`\nFIXTURE VACUOUS: the '${cls}' comparison stayed silent one token past its cap plus _band, so the band does not end. The band is working room, not an exemption -- the ratchet has to bite one band later.`)
    return 1
  }
  // And the default. Every budget injected above omits `_band`, so the whole
  // acceptance would still pass if an absent band read as some non-zero number.
  pins += 1
  if (bandOf({}) !== 0 || bandOf({ _band: 'wide' }) !== 0 || bandOf({ _band: -1 }) !== 0) {
    console.log(`\nFIXTURE VACUOUS: an absent, unparseable or negative _band does not read as 0, so a budget file that never opted in would be compared against a ceiling nobody recorded.`)
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

  // Required contexts (#957). On a healthy tree the live set EQUALS the recorded
  // shape and the corpus states no literal, so every property here is false and
  // witnessless -- the exact shape all three deletable checks at the top of
  // policy_lint_mutants.mjs had. Driven, through the wired wrapper with swapped
  // sources, and BOTH ways where the sign matters. The drives are synthetic on
  // purpose: the acceptance runs offline (the mutants lane imports it per
  // mutant), so the live API can be one of its inputs only by injection.
  //
  // The null arm is the FAILURE-MODE CONTROL the class owes for asserting live
  // state: a fetch that cannot look must produce no finding AND the line that
  // says so -- a skip without its line reads exactly like a pass, and a red on
  // an outage would block every merge through `policy-docs` itself.
  const driveRC = (source, fixtureText, sites) => {
    const prevS = requiredContextsSource
    const prevF = requiredContextsFixtureSource
    const prevSites = requiredContextsSitesSource
    const said = []
    const real = console.log
    console.log = (...a) => said.push(a.join(' '))
    try {
      // A VALUE, wrapped here -- `null` means "the fetch returned nothing",
      // which the wrapper must be able to hand the check without falling back
      // to the production fetch the way its own null default does.
      requiredContextsSource = () => source
      requiredContextsFixtureSource = fixtureText === undefined ? null : () => fixtureText
      requiredContextsSitesSource = sites === undefined ? null : () => sites
      return { found: requiredContextsOverTree(), said }
    } finally {
      requiredContextsSource = prevS
      requiredContextsFixtureSource = prevF
      requiredContextsSitesSource = prevSites
      console.log = real
    }
  }
  if (requiredContextsSource !== null || requiredContextsFixtureSource !== null || requiredContextsSitesSource !== null) {
    console.log('\nFIXTURE VACUOUS: a required-contexts source is not back at its production default; the wired check would read an injected state, not the tree and the API')
    return 1
  }
  const RC_THREE = { contexts: ['policy-docs', 'probe-a', 'probe-b'], count: 3, rulesets: [1] }
  const rcFixture = (contexts, rulesets = [1]) => JSON.stringify({ contexts, rulesets })
  const rcRot = '.claude/workflows/fixtures/policy-rot/required-contexts.md'
  const rcRotText = read(rcRot)
  if (rcRotText == null) {
    console.log(`\nFIXTURE VACUOUS: ${rcRot} is missing; the literal shapes of the required-contexts check are deletable in silence`)
    return 1
  }
  // One pin per literal SHAPE (three regexes, one finding each from the rot
  // fixture's three unguarded lines), plus the message substring that says
  // what the literal was checked against.
  pins += 4
  const lit = driveRC(RC_THREE, rcFixture(RC_THREE.contexts), [rcRot])
  if (lit.found.length !== 3 || !lit.found.every((f) => f.check === 'required-contexts')) {
    console.log(`\nFIXTURE VACUOUS: the required-contexts literal scan produced ${lit.found.length} finding(s) on the rot fixture, 3 required (one per literal shape). A deleted regex in REQUIRED_CONTEXT_RES survives here in silence.`)
    return 1
  }
  if (!lit.found.some((f) => f.message.includes('the live ruleset returns 3'))) {
    console.log('\nFIXTURE VACUOUS: no required-contexts finding names the live count it checked against, so a comparison against a constant would pass this pin')
    return 1
  }
  // The history guard: the rot fixture's two guarded lines carry the same
  // stale literal (a table row and a per-PR row) and must produce nothing --
  // over-firing on dated records is what would get this class bypassed.
  const litLines = lit.found.map((f) => rcRotText.split('\n')[Number(f.where.split(':')[1]) - 1] || '')
  if (litLines.some((l) => /^\s*(?:\||-\s*\[#\d+\])/.test(l))) {
    console.log('\nFIXTURE OVER-FIRES: a required-contexts finding landed on a table or per-PR row, which is a dated record, not a live claim')
    return 1
  }
  // Drift, both directions: the next ruleset change reddens within one push,
  // NAME by name -- a count alone would pass a swap.
  pins += 2
  const grew = driveRC({ ...RC_THREE, contexts: [...RC_THREE.contexts, 'probe-new'], count: 4 }, rcFixture(RC_THREE.contexts), [])
  if (grew.found.length !== 1 || !grew.found[0].message.includes('which the recorded shape lacks') || !grew.found[0].message.includes('probe-new')) {
    console.log('\nFIXTURE VACUOUS: a context the live set gained over the recorded shape was not reported by name; the next ruleset change would not redden the tree')
    return 1
  }
  const shrank = driveRC({ contexts: RC_THREE.contexts.slice(0, 2), count: 2, rulesets: [1] }, rcFixture(RC_THREE.contexts), [])
  if (shrank.found.length !== 1 || !shrank.found[0].message.includes('no longer returns it') || !shrank.found[0].message.includes('probe-b')) {
    console.log('\nFIXTURE VACUOUS: a context the live set dropped was not reported by name; a retired required context would read as still recorded')
    return 1
  }
  // Drift by RULESET ID, both directions (#1300). The context names above are
  // only half the boundary: a ruleset change that moves WHICH ruleset supplies
  // the required contexts, leaving the names byte-identical, read as 0 findings
  // against a fixture that recorded a different ruleset -- which the committed
  // fixture did (`main-protect` 22628467 against a boundary drawing the checks
  // from `main-protect-checks` 23698884), leaving the check blind to the exact
  // drift the fixture exists to expose. Each arm is 1 finding, not 2: the
  // contexts agree, only the id moved.
  pins += 3
  const idGrew = driveRC({ ...RC_THREE, rulesets: [1, 2] }, rcFixture(RC_THREE.contexts, [1]), [])
  if (idGrew.found.length !== 1 || !idGrew.found[0].message.includes('ruleset `2`')) {
    console.log('\nFIXTURE VACUOUS: a ruleset the live boundary gained as a source of the required contexts was not reported by id; a boundary whose checks moved to a new ruleset would read as unchanged')
    return 1
  }
  const idShrank = driveRC({ ...RC_THREE, rulesets: [1] }, rcFixture(RC_THREE.contexts, [1, 2]), [])
  if (idShrank.found.length !== 1 || !idShrank.found[0].message.includes('`2` is recorded in `rulesets`')) {
    console.log('\nFIXTURE VACUOUS: a recorded ruleset id the live boundary no longer draws the contexts from was not reported; a retired ruleset would read as still recorded')
    return 1
  }
  // An ABSENT record fires too. Skipping it would reinstate the same blindness
  // by deletion: drop the `rulesets` key and a ruleset move is invisible again.
  const idAbsent = driveRC(RC_THREE, JSON.stringify({ contexts: RC_THREE.contexts }), [])
  if (idAbsent.found.length !== 1 || !idAbsent.found[0].message.includes('ruleset `1`')) {
    console.log('\nFIXTURE VACUOUS: a fixture naming no rulesets did not fire; deleting the key would make a ruleset move invisible again')
    return 1
  }
  // Silent on equality (over-fire control) and SKIPPING on a dead fetch, line
  // included -- the recorded failure mode, pinned so it cannot become a red.
  pins += 3
  const equal = driveRC(RC_THREE, rcFixture(RC_THREE.contexts), [])
  if (equal.found.length) {
    console.log(`\nFIXTURE OVER-FIRES: the required-contexts check reported ${equal.found.length} finding(s) with the live set equal to the recorded shape, e.g. ${JSON.stringify(equal.found[0].message.slice(0, 120))}`)
    return 1
  }
  const dead = driveRC(null, rcFixture(RC_THREE.contexts), [rcRot])
  if (dead.found.length) {
    console.log(`\nFIXTURE OVER-FIRES: an unreachable API produced ${dead.found.length} required-contexts finding(s); policy-docs is itself a required context, and a transient outage must not block every merge`)
    return 1
  }
  if (!dead.said.some((l) => l.includes('skip') && l.includes('required-contexts') && l.includes('UNCHECKED'))) {
    console.log('\nFIXTURE VACUOUS: a dead fetch skipped without saying so in its own words; a skip that is not said reads exactly like a pass')
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
  // citation-presence. Its property -- "an exclusion earned by a citation has
  // lost that citation" -- is FALSE on a healthy tree by construction, the same
  // shape as named-docs above and the same shape as the three checks #1058's
  // mutation lane was written for, so it has no witness on the tree and would be
  // deletable in silence. The arms are the four of #1058's own citation table,
  // re-pointed at this check, plus a scope arm and a retirement arm.
  const cpKeys = [...EXCLUDED_BECAUSE_CITED.keys()]
  const cpWired = CORPUS_CHECK_NAMES.includes('citationPresenceOverTree')
  // THE LAST WITHDRAWAL RETIRES THE CLASS, and this arm is what makes the error
  // message's own remedy land green on BOTH lanes. `EXCLUDED_BECAUSE_CITED`
  // empty means no exclusion is earned by a citation any more, so a still-wired
  // check runs over no entries and measures nothing: `policy_lint_mutants.mjs`
  // empties its return, finds every arm below passing over an empty key list,
  // and reports `citationPresenceOverTree` DELETABLE IN SILENCE -- rc=1 on
  // `governance.yml`'s mutation step, for a seat that did exactly what the
  // message told it to do. So the half-done state is refused HERE, naming the
  // rest of the withdrawal, and the arms are skipped once the check is unwired.
  if (!cpKeys.length) {
    if (cpWired) {
      console.log(`\nFIXTURE VACUOUS: EXCLUDED_BECAUSE_CITED is empty while citationPresenceOverTree is still wired into CORPUS_CHECK_NAMES, so the check runs over no entries and measures nothing -- policy_lint_mutants.mjs calls that DELETABLE IN SILENCE and turns governance.yml red. Withdrawing the LAST entry retires the class: also remove citationPresenceOverTree from CORPUS_CHECK_NAMES and from the CORPUS_CHECKS push, and the 'citation-presence' rows from CHECKS and from NEVER_SUPPRESSED.`)
      return 1
    }
    // Retired, and said out loud rather than passed over: an unmeasured check is
    // not a passing one, and this line is the only trace that the class was ever
    // here. NOT counted in `pins` -- a skipped drive that still added its pins
    // would report the same total as a driven one.
    console.log(`\n  skip citationPresence-pin -- EXCLUDED_BECAUSE_CITED is empty and citationPresenceOverTree is unwired, so the class is retired and there is nothing to drive.`)
  } else {
  pins += 6
  const driveCP = (pairs) => {
    const prev = citationPresenceSource
    citationPresenceSource = () => pairs
    try { return citationPresenceOverTree() } finally { citationPresenceSource = prev }
  }
  if (citationPresenceSource() !== undefined) {
    console.log(`\nFIXTURE VACUOUS: citationPresenceSource's production default is not undefined, so the wired check reads a corpus nobody assembled.`)
    return 1
  }
  // THE PRODUCTION SCOPE, which no other arm reaches. Every arm below injects
  // its pairs through `citationPresenceSource`, so `corpusCitationTexts()` --
  // the one line that makes this "no POLICY FILE cites it" rather than "no file
  // cites it" -- is exercised by nothing but this comparison. Repointed at a
  // single non-policy file that happens to cite the same document (the plan of
  // record cites 0010), every arm below still passed and both lanes stayed
  // green: a tree where the citation had left the corpus entirely and survived
  // only in an unmeasured document would have been accepted.
  const cpScope = corpusCitationTexts().map(([f]) => f)
  const cpCorpus = policyFiles()
  if (cpScope.length !== cpCorpus.length || cpScope.some((f, i) => f !== cpCorpus[i])) {
    console.log(`\nFIXTURE VACUOUS: corpusCitationTexts() reads ${cpScope.length} file(s) where policyFiles() names ${cpCorpus.length}; first divergence ${JSON.stringify(cpScope.find((f, i) => f !== cpCorpus[i]) ?? '(length only)')}. The check's claim is that no POLICY file cites the document, so it must read the policy corpus and nothing else -- a wider source accepts a citation that has left the corpus, a narrower one reports a citation that has not.`)
    return 1
  }
  const cpLive = corpusCitationTexts()
  // ARM 0, the null control: the live corpus reports nothing. An arm that
  // reported here would make every other arm meaningless. Its message names BOTH
  // readings, because on a genuinely rotted tree this arm and a true production
  // finding are the same event: the check is only wrong here if the document it
  // names IS still cited by a policy file.
  const cpNull = driveCP(cpLive)
  if (cpNull.length) {
    console.log(`\nFIXTURE OVER-FIRES, or the corpus is genuinely rotted -- the two are distinguishable and this arm cannot tell them apart: checkCitationPresence reported ${JSON.stringify(cpNull.map((f) => f.where))} on the live corpus. Grep the corpus for that path first. If no policy file cites it, the CHECK IS RIGHT and the corpus is wrong: restore the citation or withdraw the pin as the reported error says, and this arm goes quiet. Only if a policy file does still cite it is this a defect in checkCitationPresence.`)
    return 1
  }
  // ARM B of #1058: the citation removed, the document left, the sentence that
  // carried it still in place. This is the arm that measured `TOTAL: 0`.
  const elide = (t) => cpKeys.reduce((acc, k) => acc.split(k).join(`${k}.NOT-CITED`), t)
  const cpElided = driveCP(cpLive.map(([f, t]) => [f, elide(t)]))
  if (cpElided.length !== cpKeys.length) {
    console.log(`\nFIXTURE VACUOUS: checkCitationPresence reported ${cpElided.length} of ${cpKeys.length} earned exclusions with every citation of them elided from the corpus. That is arm B of #1058's citation table -- the citation removed and the document left -- and it measured TOTAL 0 before this check existed.`)
    return 1
  }
  // The MOVE, which is the over-fire this check would otherwise have. A
  // citation relocated from the recorded citer to any other policy file is a
  // legitimate edit; only a check keyed on the recorded file reports it.
  const movedTo = cpLive.findIndex(([f]) => ![...EXCLUDED_BECAUSE_CITED.values()].includes(f))
  if (movedTo < 0) {
    console.log(`\nFIXTURE VACUOUS: the corpus has no policy file that is not a recorded citer, so the move arm cannot be built.`)
    return 1
  }
  const carried = cpKeys.map((k) => `see \`${k}\``).join(' and ')
  const cpMoved = driveCP(cpLive.map(([f, t], i) => [f, i === movedTo ? `${elide(t)}\n${carried}\n` : elide(t)]))
  if (cpMoved.length) {
    console.log(`\nFIXTURE OVER-FIRES: checkCitationPresence reported ${JSON.stringify(cpMoved.map((f) => f.where))} when the citation had moved to ${cpLive[movedTo][0]}, another policy file. The recorded citer is carried for the message; keying the check on it turns a legitimate move into rot.`)
    return 1
  }
  // The declaration is bounded by the list it earns. An entry naming a file
  // that is not excluded pins a citation that bought nothing, and an entry the
  // tree does not have pins a citation to a path that cannot be cited -- both
  // are dead weight the `deadExcluded` pin below would not see, because they
  // are in a different list.
  const cpStray = cpKeys.filter((k) => !CORPUS_EXCLUDED.has(k) || !trackedFiles().set.has(k))
  if (cpStray.length) {
    console.log(`\nFIXTURE VACUOUS: EXCLUDED_BECAUSE_CITED lists ${JSON.stringify(cpStray)}, which CORPUS_EXCLUDED does not carry or the tree does not have. The entry exists to pin the citation that EARNED an exclusion; without one there is nothing earned to lose.`)
    return 1
  }
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
    // The keying window. Its pull-request numbers are NOT in
    // merged-subjects.txt, on purpose: that list is also `record`'s
    // undispositioned-merge witness, so numbers added there would move
    // checkRecord's rot count and need matching rows in dispositions-healthy.md
    // to keep its silent arm silent. statsFindings is pure over injected
    // inputs, so this window is handed to it directly.
    const keys = JSON.parse(read(`${dir}/friction-keys.json`))
    const keysFetched = new Map()
    for (const [k, v] of Object.entries(keys)) {
      if (k.startsWith('_')) continue
      keysFetched.set(k, v)
    }
    const keysPrs = (keys._window ?? []).map((pr) => ({ pr }))
    if (!keysPrs.length) return null
    return {
      prs,
      healthyPrs: prs.filter((p) => healthy.has(p.pr)),
      fetched,
      keysPrs,
      keysFetched,
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

const REQUIRED_H2 = ['Head', 'Mutation proof', 'Null control', 'Figures', 'Red checks', 'Forward-carry', 'Friction']
const POLICY_H2 = ['Approval']
const FRICTION_EVENTS = ['unclear', 'contradiction', 'unenforced', 'stale', 'cost']
// A body writing `none` in backticks means the same thing as one writing none,
// and refusing the first would teach seats to write the second while meaning
// neither. Leading list markers and emphasis are stripped for the same reason.
const STRIP = "[-*\\s`_\"']*"
// A section IS `none` only when the `none`/`n/a` is the WHOLE section. The
// `[^\n]*$` tail is load-bearing: without it `^` matched at the start of the
// string and the pattern had no end anchor, so a section that opened with
// `None` on its first line and then carried real entries matched anyway --
// `frictionEntries` returned `[]` and every entry below the declaration was
// dropped, and a malformed entry there was accepted rather than refused
// (#1139). A `none`/`n/a` line that is not the whole section is a DECLARATION,
// not an entry; `frictionEntries` drops it so the entries below it are read.
// Callers pass trimmed text (`frictionEntries`, the `Forward-carry` read), so
// the tail cannot be a bare newline.
const isNone = (text) => new RegExp(`^${STRIP}(none|n/a)\\b[^\\n]*$`, 'i').test(text)
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

// THE ONE FRICTION GRAMMAR. `.github/PULL_REQUEST_TEMPLATE.md` prescribes
// `none`, or one line per event: `<rule_id>: <unclear|contradiction|unenforced|
// stale|cost>: <evidence>`. `checkPrBody` refuses against this and the `--stats`
// histogram keys against it, through this one function, because two readings
// of the same section disagreed in silence (the measurement is at
// `frictionIds`).
//
// Tokenising: an entry OPENS on a list marker, on an `id: event:` shape, or on
// a near-miss `word:` shape; any other line CONTINUES the entry above it. The
// continuation rule is load-bearing -- this corpus wraps at eighty columns, so
// evidence longer than a few words spans lines, and treating each physical
// line as an entry refused the first well-formed body this check ever saw.
// The near-miss rule refuses `index: Cost:` and `index: unenforced but no
// second colon` instead of folding them into the entry above, where a
// malformed second entry cost nothing. The list-marker rule is the newest: a
// line that starts with `- ` or `* ` is a second event by the template's own
// words, whatever follows the marker, and before it existed an unlabelled
// bullet after a labelled entry folded into that entry's evidence -- accepted
// by the contract, counted as unlabelled by the histogram, visible to nobody.
//
// The id charset admits `#`, `/` and a LEADING `.`, so `CLAUDE.md#budgets` and
// a repo-relative path (`.claude/skills/steward/SKILL.md`) parse as ids: the
// template constrains the class, not the id, and the class is the half that
// carries meaning. The leading dot is #1305: a path is the most explicit
// spelling of the file it names, and a grammar that could not start on `.`
// dropped it into the unlabelled bucket, where it named no budget file at all.
// Backticks around the id and the class are tolerated because every other
// policy file writes an identifier that way.
// A section that is `none` has no entries; that is the contract's accept path
// and the histogram's zero, and it is decided here so neither caller can read
// `none` as one unparseable entry.
const FRICTION_ID = '[A-Za-z.][A-Za-z0-9_.#/-]*'
const FRICTION_ENTRY_RE = new RegExp(`^[-*]?\\s*\`?(${FRICTION_ID})\`?\\s*:\\s*\`?([a-z-]+)\`?\\s*:\\s*(.+)$`)
const FRICTION_OPENS_RE = new RegExp(`^[-*]?\\s*\`?${FRICTION_ID}\`?\\s*:\\s*\`?[a-z-]+\`?\\s*:`)
const FRICTION_NEAR_MISS_RE = new RegExp(`^[-*]?\\s*\`?${FRICTION_ID}\`?\\s*:`)
const FRICTION_BULLET_RE = /^[-*]\s/

// A TRAILER LINE IS NOT FRICTION (#1238, D13-01). The lines a tool or an
// assistant appends to a body -- the Claude Code attribution, a
// `Co-Authored-By:` git trailer, GitHub's `Closes #N`-family keyword lines --
// OPEN entries under the rules above (a list-marked bullet; a `word:`
// near-miss) while naming no rule and no event, so at the round-5 baseline 13
// of 54 merged bodies fed the unlabelled bucket 13 entries of boilerplate no
// seat wrote, 11 of them the attribution alone, and that bucket was the
// histogram's TOP ROW -- the row `friction_issues.mjs` would have filed
// "[policy] recurring friction: (unlabelled friction bullet)" on. Dropped
// here, like a `none` declaration, rather than refused: the seat did not
// write the line (a tool pasted it), and refusing would charge every body a
// repair round for a paste. The drop is keyed on the LINE'S OWN SHAPE, a
// closed list: an attribution line, the one git co-author trailer token, and
// the closing/linking keywords GitHub itself defines, each before an issue
// number. None of the shapes is `<rule_id>: <event>: <evidence>`, so the drop
// cannot swallow a well-formed entry; the null control in tests/entities.py
// drives the same words mid-evidence, where no line-anchored shape matches,
// and the entry survives.
const FRICTION_TRAILER_RE =
  /^[-*]?\s*(?:(?:🤖\s*)?generated with\b|co-authored-by:\s|(?:closes?|closed|fixes?|fixed|resolves?|resolved|reverts?|refs|part of|supersedes)\s+#\d+\b)/i

function frictionEntries(text) {
  const section = String(text ?? '').trim()
  if (!section || isNone(section)) return []
  const lines = []
  for (const raw of section.split('\n').map((l) => l.trim()).filter(Boolean)) {
    // A `none`/`n/a` line that is not the whole section is a DECLARATION, not
    // an entry -- the section below it carries the content. The whole-section
    // case returned above, so reaching here means entries follow; reading the
    // declaration as one unparseable entry would refuse a body whose entries
    // are well-formed, and dropping the section instead lost them (#1139).
    if (isNone(raw)) continue
    if (FRICTION_TRAILER_RE.test(raw)) continue
    const opens = FRICTION_BULLET_RE.test(raw) || FRICTION_OPENS_RE.test(raw) || FRICTION_NEAR_MISS_RE.test(raw)
    if (opens || !lines.length) lines.push(raw)
    else lines[lines.length - 1] += ' ' + raw
  }
  return lines.map((line) => {
    const m = FRICTION_ENTRY_RE.exec(line)
    if (!m || !FRICTION_EVENTS.includes(m[2])) return { line, id: null, event: null, evidence: null }
    return { line, id: m[1], event: m[2], evidence: m[3] }
  })
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

// Reading the path list is separated from using it so the REFUSALS can be
// pinned. They are the fix's headline property -- a list that cannot be derived
// must not read as "touches no policy file" -- and round one found them
// unpinned: deleting the empty-list refusal left the acceptance green and turned
// the empty case fail-open, which is the defect this keying exists to close.
function pathsFromFile(pathsFile) {
  let raw
  try {
    raw = fs.readFileSync(pathsFile, 'utf8')
  } catch {
    return { error: `--paths-file ${pathsFile}: unreadable. The approval gate reads the diff; a list that cannot be read is not an empty diff.` }
  }
  const paths = raw.split('\n').map((x) => x.trim()).filter(Boolean)
  if (!paths.length) {
    return { error: `--paths-file ${pathsFile} is empty. A pull request changes at least one file; an empty list means the derivation failed.` }
  }
  return { paths }
}

// `## Approval` is keyed on the DIFF, not on the title. It was keyed on
// `/^policy:/` against `github.event.pull_request.title` -- a string written by
// the same seat the section exists to constrain, so a one-word title change
// switched the requirement off. R3-D11-03 measured the hole rather than arguing
// it: one body, one head, only --title changed, exit 1 against exit 0.
// The title arm is KEPT as well: a seat that calls its change policy is taken at
// its word even when the diff touches no globbed path. Widening POLICY_GLOBS --
// which does not contain this file, nor .github/workflows/ -- is a policy
// question and the owner's, and is named in the body rather than taken here.
// AN AUTOFIX COMMIT MOVES THE HEAD WITHOUT MOVING THE EVIDENCE. `closures-autofix`
// and `claims-autofix` (tests.yml) push onto a pull request after its body was
// written, so `## Head` names the seat's commit while CI runs on the bot's, and
// the body had to be edited and the run waited out again (#1107, run
// 35220336323 at b1afbcf). A chain of such commits directly on top of a commit
// the section names is accepted when EVERY commit in it has:
//   - author and committer both the bot identity the jobs configure;
//   - a whole message that is exactly one of the two autofix messages;
//   - exactly one parent;
//   - a diff against that parent that only MODIFIES the files that message's
//     job stages -- and, for the claims job, which only empties lists, adds no
//     line.
// The identity is git metadata anyone can write, and GitHub offers nothing
// better here: the bot's pushes are unsigned (`verification.reason` is
// `unsigned` on both #1107 commits) and a push with the PAT is attributed to
// the PAT's owner, a seat (run 35220336323's actor). So the other three carry
// the weight. A forged closures commit is a GATE_FILES change, so the `closures`
// job re-derives every closure at that head and refuses an under-scoped one; a
// forged claims commit can only delete claims, which `fast`'s golden drift check
// then refuses if a fixture really drifts. Accepting the head asserts nothing
// about either file -- every other required context still runs at the real head.
//
// The constants are held here rather than read from tests.yml because this
// runs in the pull request's own checkout: a branch that edited the workflow
// would widen what it is excused for. tests/entities.py pins their agreement.
const AUTOFIX_BOT_COMMITS = {
  name: 'github-actions[bot]',
  email: '41898282+github-actions[bot]@users.noreply.github.com',
  messages: {
    'ci: re-record closures': { paths: ['tests/closures.json'], mayAdd: true },
    'ci: drop inherited claims': {
      paths: ['tests/golden/claimed_drift.txt', 'tests/golden/card_claimed_drift.txt'], mayAdd: false },
  },
}

// One commit's answer: `{ parent, message }` when it is an autofix commit, or
// `{ why }` naming the first condition it fails. Fail-closed: a commit this
// clone cannot read is refused, never assumed.
function autofixCommit(sha) {
  const bot = `${AUTOFIX_BOT_COMMITS.name} <${AUTOFIX_BOT_COMMITS.email}>`
  const short = sha.slice(0, 7)
  if (!/^[0-9a-f]{40}$/.test(sha)) return { why: `${short} is not a full commit SHA` }
  const meta = git(['show', '-s', '--format=%an <%ae>%x00%cn <%ce>%x00%P%x00%B', sha], { allowFail: true, quiet: true })
  if (!meta) return { why: `${short} is not a commit in this clone` }
  const [author, committer, parents, raw] = meta.split('\0')
  if (author !== bot || committer !== bot) return { why: `${short} is not authored and committed as ${bot}` }
  const message = raw.trim()
  if (!Object.hasOwn(AUTOFIX_BOT_COMMITS.messages, message)) return { why: `${short}'s message is not an autofix message` }
  const rule = AUTOFIX_BOT_COMMITS.messages[message]
  const ps = parents.trim().split(/\s+/).filter(Boolean)
  if (ps.length !== 1) return { why: `${short} has ${ps.length} parents` }
  const status = git(['diff', '--no-renames', '--name-status', ps[0], sha], { allowFail: true, quiet: true })
    .split('\n').filter(Boolean).map((l) => l.split('\t'))
  const numstat = git(['diff', '--no-renames', '--numstat', ps[0], sha], { allowFail: true, quiet: true })
    .split('\n').filter(Boolean).map((l) => l.split('\t'))
  if (!status.length) return { why: `${short} changes no file` }
  const outside = status.map(([, p]) => p).filter((p) => !rule.paths.includes(p))
  if (outside.length) return { why: `${short} changes ${outside.join(', ')}, outside what "${message}" stages` }
  if (status.some(([s]) => s !== 'M')) return { why: `${short} does not only modify its files` }
  if (!rule.mayAdd && numstat.some(([added]) => added !== '0')) return { why: `${short} adds lines, and "${message}" only removes them` }
  return { parent: ps[0], message }
}

// Walks down from the head while each commit is an autofix commit, stopping at
// the first parent `names` accepts. `{ base, accepted }` or `{ why }`.
function autofixChain(head, names) {
  const accepted = []
  for (let sha = head; ;) {
    const c = autofixCommit(sha)
    if (c.why) return { why: c.why }
    accepted.unshift({ sha, message: c.message })
    if (names(c.parent)) return { base: c.parent, accepted }
    sha = c.parent
  }
}

// ---------------------------------------------------------------------------
// THE `## Red checks` OBLIGATION IS OVER EVERY HEAD, NOT ONLY THIS ONE (#1144).
//
// `fix-review.md` step 11 reads a red on ANY head as an answer the body owes.
// The CI wiring that supplies `red` -- `.github/workflows/governance.yml`,
// "List the red checks at this head" -- queries `commits/${PR_HEAD}/check-runs`,
// so a check that failed at an earlier head and was cleared by a later push
// leaves NO check-run record against the current head at all: the red is gone
// before this check ever sees it, and a body that never named it passes. The
// instrument was head-only while the rule was not.
//
// This derivation reads the commits BETWEEN the merge base with `origin/main`
// and the head this run is at, instead. Those are the branch's own commits, and
// each push moves the head to one of them, so the red a later push cleared is
// still in the range after it has gone green. Commits `main` absorbed by a merge
// are NOT in it: merging moves the merge base to `main`'s tip. The list comes
// from the clone (`rev-list`), not from the API, which is what keeps it cheap
// and what keeps a red that `main` itself carried out of this pull request's
// obligation -- the `nightly-status` precedent in `fix-review.md` step 11.
//
// It needs the API -- a check run is not in the git clone -- and therefore a
// credential. Where the history cannot be read the check says which heads went
// UNCHECKED rather than reading the absence as a clean one, which is the
// fail-open this file refuses everywhere else; where it could be read and the
// read failed, the run is REFUSED, on `--paths-file`'s own argument.
//
// `checkPrBody` itself does not change: `red` is still a list of names, and the
// refusal it drives is the one #956 wired.
const PR_CONTRACT_CHECK = 'pr-contract'
const RED_HISTORY_PAGE = 100
const RED_HISTORY_MAX_PAGES = 10

// Pure over run objects, so the acceptance drives it with no network and no
// token. RED is the corpus's own predicate -- conclusion `failure` on a
// COMPLETED run -- so skipped, cancelled, timed-out, neutral and still-running
// are not red, while a run that failed and then succeeded at the SAME commit
// still is. This job's own runs are excluded by the check-run NAME and nothing
// else, which is #956's argument: an id-keyed exclusion lets this job's prior
// red back in and deadlocks the body.
function failingCheckNames(runs) {
  const names = new Set()
  for (const run of Array.isArray(runs) ? runs : []) {
    if (run?.status !== 'completed' || run?.conclusion !== 'failure') continue
    if (run?.name === PR_CONTRACT_CHECK) continue
    if (typeof run?.name === 'string' && run.name.trim()) names.add(run.name)
  }
  return [...names].sort()
}

// The union over the commits, with the per-commit read injected so this is a
// pure function of its inputs -- the acceptance drives it with fixture runs.
// THE LOOP IS THE FIX, and the mutation proof is against it: it reads EVERY
// commit. A loop over the tip alone (`.slice(-1)`), which is what a head-only
// derivation amounts to, drops exactly the red this exists to keep. A read that
// fails is returned as a failure rather than skipped: a commit whose runs could
// not be read is an unmeasured commit, and a union over the measured ones alone
// would report a clean history it did not establish.
function redsOverCommits(commits, fetchRuns) {
  const reds = new Set()
  for (const sha of commits) {
    const got = fetchRuns(sha)
    if (!got.ok) return { ok: false, why: `check-runs at ${String(sha).slice(0, 7)}: ${got.why}` }
    for (const name of failingCheckNames(got.runs)) reds.add(name)
  }
  return { ok: true, reds: [...reds].sort(), commits: commits.length }
}

// The credential. `ghGet` reads `GITHUB_TOKEN` by default, and a seat's own runs
// hold `GH_TOKEN` (fixer.md takes it from `~/.zcode/identity-author.token`) --
// `gh` reads the same two. This helper is what the red-history walk passes to
// `ghGet` explicitly, so the gate and the fetch agree on one credential and a
// seat's own push gate can read the history it is about to be judged on. Neither
// variable is a licence to print one: the value goes into curl's `-K -` config
// on stdin, exactly as `ghGet` sends it.
function ghCredential() {
  return process.env.GITHUB_TOKEN || process.env.GH_TOKEN || ''
}

// One bounded page-walk over a listing endpoint. These are read on a seat's
// push gate, so an unbounded walk against an endpoint that always returns a
// full page would hang it. `pick` unwraps the two shapes in play: a bare array,
// and `/commits/<sha>/check-runs`'s `{check_runs: []}`.
function ghGetList(pathname, pick = (d) => (Array.isArray(d) ? d : []), token) {
  const out = []
  for (let page = 1; page <= RED_HISTORY_MAX_PAGES; page++) {
    const got = ghGet(`${pathname}${pathname.includes('?') ? '&' : '?'}per_page=${RED_HISTORY_PAGE}&page=${page}`, token)
    if (!got.ok) return { ok: false, why: got.why }
    const arr = pick(got.data)
    out.push(...arr)
    if (arr.length < RED_HISTORY_PAGE) return { ok: true, data: out }
  }
  return { ok: false, why: `more than ${RED_HISTORY_PAGE * RED_HISTORY_MAX_PAGES} entries at ${pathname}` }
}

const RED_HISTORY_PICK_RUNS = (d) =>
  Array.isArray(d?.check_runs) ? d.check_runs : Array.isArray(d) ? d : []

// `{ok: true, data}` with the reds, or `{ok: true, none: <why>}` when there is
// no history to read (not a failure -- a first push has no earlier head), or
// `{ok: false, why}` when the read failed and the run must be refused.
function redHistoryForHead(head, slug) {
  const base = git(['merge-base', 'origin/main', head], { allowFail: true }).trim()
  if (!/^[0-9a-f]{40}$/.test(base)) {
    return { ok: true, none: `origin/main and ${head.slice(0, 7)} share no merge base in this clone` }
  }
  const listed = git(['rev-list', `${base}..${head}`], { allowFail: true }).trim()
  const shas = listed ? listed.split('\n').map((s) => s.trim()).filter(Boolean) : []
  if (!shas.length) return { ok: true, none: `no commit sits between origin/main and ${head.slice(0, 7)}` }
  // ONE PROBE before the walk, and it is the line that separates an outage from
  // an unpushed commit: a repository resource that will not answer means no
  // later 404 can be read as "this commit has no runs".
  const token = ghCredential()
  const probe = ghGet(`/repos/${slug}`, token)
  if (!probe.ok) return { ok: false, why: probe.why }
  const union = redsOverCommits(shas, (sha) => {
    const got = ghGetList(`/repos/${slug}/commits/${sha}/check-runs`, RED_HISTORY_PICK_RUNS, token)
    if (got.ok) return { ok: true, runs: got.data }
    // 404/422 on a commit the clone has but GitHub does not: it is not pushed
    // yet, so it has no runs. That is a skip, not a failure -- a seat's push
    // gate runs BEFORE its push, and its own new head is exactly this case.
    if (/\b(404|422)\b/.test(got.why || '')) return { ok: true, runs: [] }
    return { ok: false, why: got.why }
  })
  if (!union.ok) return { ok: false, why: union.why }
  return { ok: true, commits: union.commits, reds: union.reds }
}

// The two lines this derivation prints, pinned on SHAPE in the acceptance for
// `enumSkipLine`'s reason: they carry no finding, so no count above can see
// them. The skip line's job is to make an unread history UNCHECKED rather than
// clean -- the exact fail-open #1144 is about -- and the record line names what
// was read, so a head that went red and then green is still on the record after
// the red is gone.
function redHistoryRecordLine(commits, reds) {
  return `  record   red-history           ${commits} commit(s) between origin/main and this head, every failure conclusion across them: ${reds.length ? reds.join(', ') : 'none'}`
}

function redHistorySkipLine(why) {
  return `  skip     red-history           ${why}; every head before the one this ran on is UNCHECKED this run, not confirmed clean -- a red a later push cleared would not be named here`
}

function checkPrBody(bodyPath, { head = '', title = '', red = [], paths = [], notes = [], author = null } = {}) {
  const out = []
  // The REST `/pulls/{n}` `.user.login` reports the App as `hpo-author[bot]`
  // while the GraphQL `author.login` reports `app/hpo-author`; accept both.
  if (author != null && author !== 'app/hpo-author' && author !== 'hpo-author[bot]') {
    out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
      message: `the pull request author is \`${author}\`; a pull request is authored by the hpo-author App (decision 0011) — re-open it via tools/audit/app_push.sh, never push.sh` })
  }
  let body
  try {
    body = fs.readFileSync(bodyPath, 'utf8')
  } catch {
    return [{ severity: 'error', check: 'pr-body', where: bodyPath, message: 'unreadable' }]
  }
  const secs = sections(body)
  const byTitle = /^policy:/.test(title.trim())
  const policyPaths = paths.filter((f) => POLICY_GLOBS.some((re) => re.test(f)))
  const isPolicy = byTitle || policyPaths.length > 0
  const why = policyPaths.length
    ? `this diff touches ${policyPaths.length === 1 ? '' : `${policyPaths.length} policy files, including `}\`${policyPaths[0]}\``
    : 'the title declares this a policy change'
  const want = [...REQUIRED_H2, ...(isPolicy ? POLICY_H2 : [])]

  for (const h of want) {
    if (!secs.has(h)) {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: POLICY_H2.includes(h)
          ? `no \`## ${h}\` section, and ${why}. The owner approves a policy change before it merges; the section is where that is recorded.`
          : `no \`## ${h}\` section. Every one is content or an explicit "n/a: <reason>"; a missing heading is neither.` })
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
  // an older head is the shape fix-review.md calls `head-moved` -- except where
  // everything between the two is the autofix jobs' own repair (`autofixChain`).
  const headSec = secs.get('Head') ?? ''
  const names = (sha) => headSec.includes(sha) || headSec.includes(sha.slice(0, 7))
  if (head && headSec && !names(head)) {
    const chain = autofixChain(head, names)
    if (chain.base) {
      notes.push(`HEAD: \`## Head\` names ${chain.base.slice(0, 7)}; accepted autofix commit(s) on top of it: ${
        chain.accepted.map((c) => `${c.sha.slice(0, 7)} (${c.message})`).join(', ')}`)
    } else {
      out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
        message: `\`## Head\` does not name ${head.slice(0, 7)}, which is the head this ran on. Evidence measured at another head describes another tree. Nor is it an autofix repair on a head the section names: ${chain.why}.` })
    }
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

  // Friction is the input to the policy-evolution loop. An entry the grammar
  // does not parse is a signal the histogram can only bucket, never classify,
  // so it is refused here, where the seat that wrote it can still fix it --
  // and by the same parser the histogram keys with (`frictionEntries`), so the
  // contract cannot accept what the histogram cannot read. Free prose after a
  // parsed entry is its wrapped evidence and passes; a first line of free
  // prose, a bullet that names no rule and no class, and a near-miss are each
  // an entry that does not parse. Merged bodies are never re-read: this runs
  // on `pull_request` events only.
  for (const e of frictionEntries(secs.get('Friction'))) {
    if (e.id) continue
    out.push({ severity: 'error', check: 'pr-body', where: bodyPath,
      message: `\`## Friction\` line does not parse: ${JSON.stringify(e.line.slice(0, 50))}. Write \`none\`, or \`<rule_id>: <${FRICTION_EVENTS.join('|')}>: <evidence>\`.` })
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
  // The pull request must be authored by the hpo-author App (decision 0011);
  // a PR authored as tvofi or any other identity is refused, fail-closed,
  // because an author cannot approve their own code-owned PR.
  const author = val('--author')
  // `--red` may be REPEATED, once per name. A LONE `--red` value is still
  // split on commas -- the form `prepr.sh --self-test` drives -- but each
  // value of a repeated `--red` is ONE name, verbatim: CI's pr-contract job
  // passes one flag per check-run name it derived (#956), and the comma form
  // cannot carry a name that itself contains a comma (a matrix job named over
  // two dimensions splits into fragments neither the refusal nor
  // `## Red checks` can match). Duplicated names collapse: a head that failed
  // a check twice, or a caller passing both forms, asks the question once.
  const redVals = args.flatMap((a, i) => (a === '--red' && i + 1 < args.length ? [args[i + 1]] : []))
  const red = [...new Set(
    (redVals.length > 1 ? redVals : (redVals[0] ?? '').split(','))
      .map((x) => x.trim())
      .filter(Boolean))]
  // The changed paths decide whether `## Approval` is owed, so a path list that
  // could not be derived must REFUSE rather than pass: an empty list reads as
  // "touches no policy file", which is the fail-open this check exists to close.
  const pathsFile = val('--paths-file')
  let paths = []
  if (pathsFile != null) {
    const got = pathsFromFile(pathsFile)
    if (got.error) {
      console.log(`  ERROR   [pr-body] ${got.error}`)
      return 1
    }
    paths = got.paths
  }
  // THE `## Red checks` OBLIGATION IS OVER EVERY HEAD (#1144). CI derives `red`
  // from `commits/$PR_HEAD/check-runs`, so a red a later push cleared has no
  // check-run record at the head this runs on and silently drops out of the
  // list. The derivation below is that predicate widened to the branch's own
  // commits, so a cleared red is RECORDED (the `record` line) and then enforced
  // by the loop in `checkPrBody`, instead of vanishing.
  const notes = []
  const head = (val('--head') ?? '').trim()
  let redAll = red
  if (!/^[0-9a-f]{40}$/i.test(head) || /^0{40}$/.test(head)) {
    notes.push(redHistorySkipLine('`--head` is not a commit sha, so this run is not at a head the red history can be read for'))
  } else if (!ghCredential()) {
    notes.push(redHistorySkipLine('neither GITHUB_TOKEN nor GH_TOKEN is set, so no check run could be read'))
  } else if (!repoSlug()) {
    notes.push(redHistorySkipLine('origin is not a GitHub remote'))
  } else {
    const hist = redHistoryForHead(head, repoSlug())
    if (!hist.ok) {
      console.log(`  ERROR   [pr-body] the red history could not be derived: ${hist.why}`)
      return 1
    }
    if (hist.none) notes.push(redHistorySkipLine(hist.none))
    else {
      notes.push(redHistoryRecordLine(hist.commits, hist.reds))
      redAll = [...new Set([...red, ...hist.reds])]
    }
  }
  const findings = checkPrBody(bodyPath, { head, title: val('--title') ?? '', red: redAll, paths, notes, author })
  for (const n of notes) console.log(n)
  printFindings(findings)
  console.log(`\nPR-BODY: ${findings.length} error(s) in ${bodyPath}`)
  return findings.length ? 1 : 0
}

function cmdList() {
  console.log('policy_lint checks:\n')
  for (const c of CHECKS) console.log(`  ${c.name.padEnd(12)} ${c.what}\n${' '.repeat(16)}fixture: ${c.fixture}`)
}

// Reads one path per line on stdin and prints back the subset POLICY_GLOBS
// matches. `tools/audit/preflight.sh` is the consumer: it needs to know whether
// a path `git diff` named is policy, and CLAUDE.md's "a fourth definition of
// what is policy is its own defect" makes copying the globs into a shell regex
// the wrong answer.
//
// WHY A FILTER RATHER THAN A LIST. `policyFiles()` resolves the globs against
// the TRACKED tree, so a policy file that exists on origin/main and not in this
// checkout -- which is exactly the shape of a corpus that has fallen behind --
// is absent from it, and a consumer intersecting with that list would go quiet
// on the case it most needs to see. A filter is a pure function of the path.
//
// ALWAYS READS STDIN, never a filename. A mode that reads stdin only sometimes
// blocks when it is handed a filename instead, the process is killed, and the
// kill reports success: that is how three merge bodies were once "verified"
// clean against preflight.sh (#605). One input channel, no branch to get wrong.
function cmdCorpusFilter() {
  let raw = ''
  try {
    raw = fs.readFileSync(0, 'utf8')
  } catch {
    raw = ''
  }
  for (const line of raw.split('\n')) {
    const f = line.trim()
    if (f && POLICY_GLOBS.some((re) => re.test(f))) console.log(f)
  }
}

// Reads one friction rule id per line on stdin and prints `<raw>\t<key>`, one
// row per input line, in order. Same channel and same argument as
// `--corpus-filter` above: friction_issues.mjs needs to know which key an
// ALREADY-FILED issue's title normalizes to before it can say that key is below
// threshold, and a second copy of the normalization there would be a second
// definition of what one rule is. A blank line is skipped; every other line
// answers, so a consumer can check the row count against what it sent and
// refuse a partial answer rather than read a short list as "no match".
function cmdNormalizeKeys() {
  let raw = ''
  try {
    raw = fs.readFileSync(0, 'utf8')
  } catch {
    raw = ''
  }
  for (const line of raw.split('\n')) {
    const id = line.trim()
    if (!id) continue
    console.log(`${id}\t${frictionKey(id)}`)
  }
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
  // The band is printed on every aggregate row, not once in a footer. A seat
  // reads one line to decide whether it is refused, and a cap that now sits
  // below the measurement is only honest beside the ceiling it is half of.
  const band = bandOf(b)
  const agg = (cap) => (cap == null ? 'cap -' : band ? `cap ${cap} +band ${band} = ${cap + band}` : `cap ${cap}`)
  console.log(`\nalways-loaded: ~${alwaysTokens} tokens, ${agg(b ? b.always_loaded_tokens : null)}`)
  // The floor alone reads as the corpus cost; printing the three together is
  // what stops a re-record of one being mistaken for an improvement in all.
  const corpusTokens = rows.reduce((n, r) => n + Math.round(r.bytes / 4), 0)
  console.log(`corpus:        ~${corpusTokens} tokens, ${agg(b ? b.corpus_tokens : null)}`)
  for (const [role, spec] of Object.entries((b && b.roles) || {})) {
    console.log(`role ${role.padEnd(9)} ~${roleTokens(rows, spec.opens)} tokens, ${agg(spec.cap)}`)
  }
  if (band) console.log(`\nThe working band applies to the five aggregate caps only; every per-file cap above is compared exactly. Re-record an aggregate down when it falls more than ${band} below its cap, and on any reclassification.`)
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

// THE OTHER HALF OF THE WINDOW GUARD, and the sibling of `enumSkipLine` above.
// That marker covers a dead FETCH -- git listed the window's commits and the
// commit-to-PR map would not answer. This one covers a bad REF, which is the
// arm BEFORE it: `git log <ref>..origin/main` is fatal, `firstParentCommits`
// returns [], `fetchPullsBySha` over zero commits succeeds trivially, and the
// enumeration reports `api` mode with an empty window and no marker of any
// kind. The bad-ref arm is marker-less by construction, which is why it needed
// its own.
//
// Measured at d1a531b: `--since 6.5.0` (the contents of VERSION -- the release
// TAG is `v6.5.0`, so the composition the dispatch briefs prescribe names no
// revision) printed `RECORD: 0 merged pull request(s)` and `TOTAL: 0 error(s)`
// at rc=0, byte-identical in shape to `--since origin/main`, a ref that DOES
// resolve over a genuinely empty window. Two opposite claims, one output.
//
// Pure over its three arguments so the acceptance drives it without a
// repository, and listed in LOOP_CHECK_NAMES so emptying it is a mutation the
// mutants lane refuses rather than a silent string change.
export function badRefLine(ref, mode, range) {
  return `  refuse   since-ref             ${mode} was given --since ${ref}, which names no revision here, so \`git log ${range}\` is fatal and the window could not be DERIVED; measuring nothing rather than printing a zero -- a zero over a window that was never derived and a zero over a window derived and found empty are opposite claims, and only one of them is a reason to stop looking`
}

// `^{commit}` rather than a bare `--verify`: it peels an annotated tag to the
// commit `git log` will actually walk, and refuses a name that resolves to a
// tree or a blob -- which `git log <ref>..` would also reject. What this asks
// is exactly what the range needs, not a weaker proxy for it.
function resolvesToCommit(ref) {
  return !!git(['rev-parse', '--verify', '--quiet', `${ref}^{commit}`], { allowFail: true }).trim()
}

// A window that was not given and a window that cannot be derived are the same
// CALLER error -- "there is no window to measure" -- so they share this seat and
// they share rc=2. Deliberately not rc=1 on `--record`, whose rc IS its error
// count: a bad ref found no undispositioned merge, and returning 1 would report
// a corpus defect that nothing measured. Deliberately not rc=0 with a marker
// either, which is #957's discipline for an UNREACHABLE API -- a transient,
// external condition on a required context, where reddening would gate every
// pull request on GitHub's availability. A bad ref is none of that: it is
// deterministic, local, reproducible, and fixed by typing a different argument.
// Nothing has to recover for the next run to succeed, so the outage precedent
// does not transfer and the `requireSince` precedent -- caller error, exit 2 --
// does.
function requireSince(since, mode) {
  if (since) {
    if (resolvesToCommit(since)) return since
    console.log(badRefLine(since, mode, `${since}..${mainRef()}`))
    process.exit(2)
  }
  console.log(`${mode} needs a window: pass --since <ref>. It measures pull requests merged in <ref>..origin/main, and without a ref there is no window to measure.`)
  process.exit(2)
}

// AN UNSET TOKEN IS A CALLER ERROR, NOT AN OUTAGE, and the two are the same
// `{ok:false}` to `ghGet` while being opposite things to whoever reads the run.
//
// `--record` reads the window's merges through `/commits/<sha>/pulls`. With no
// token `ghGet` refuses before it calls `curl`, `mergedPRsFromWindow` falls
// back to subject mode, and the fallback's end-anchored `(#N)` matches none of
// this repository's merge subjects -- so the mode prints `RECORD: 0 merged pull
// request(s)`, `TOTAL: 0 error(s)` and exits 0. That is the whole check
// reporting a clean window it never looked at. `enumSkipLine` says UNCHECKED
// out loud beside it, and a loud line is what a human reads; rc=0 is what the
// job's `continue-on-error` step, the run summary's verdict and any `&&` after
// it read, and all three read it as "no undispositioned merge".
//
// WHY THIS DOES NOT REOPEN #957. That discipline keeps rc=0 for an UNREACHABLE
// API -- transient, external, nothing the caller can do -- because reddening a
// required context on GitHub's availability gates every pull request on an
// outage. An unset token is none of those: deterministic, local, reproducible,
// and fixed by setting one variable. It is exactly the class `requireSince`
// already exits 2 on, and it takes the same rc for the same reason -- the
// caller was misconfigured, so the mode measured nothing and says so, rather
// than reporting an error count nothing produced (rc=1) or a clean window
// nothing read (rc=0). An HTTP failure, a rate limit, a 403 on a token that IS
// set: unchanged, still the skip line and still rc=0.
//
// SCOPED TO `--record` AND NOTHING ELSE, because it is the mode whose zero is a
// verdict. `--stats` is run `|| true` by design and `--record-known-bad` with a
// window writes a ledger a reviewer reads in the diff; widening this to either
// is a separate change with its own callers to check.
//
// THE CALLERS. The rule, so a reader re-derives the set rather than trusting a
// number that ages: every tracked file that invokes this script with `--record`
// as an argument -- `git grep -n -- '--record' -- .github .claude tools tests
// docs`, minus the hits that are this file's own usage banner or prose about
// the mode, and minus `--record-known-bad`, a different mode this guard does
// not touch. Run at the head of the pull request that added the guard, that
// rule names two invokers, and an earlier draft of this comment claimed one:
//
//   `.github/workflows/governance.yml`, the `Every merged pull request has a
//   disposition` step. It sets `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`, so
//   it takes the authenticated path and is unaffected.
//
//   `.claude/workflows/policy_lint_envmatrix.mjs`, twice: the `since-ref` bad-ref
//   row and that row's own null control. Both now pass a fixture token in the
//   child's env, so the matrix stays drivable by a seat with no token -- which
//   it had stopped being, and which is how the false enumeration was found.
//
// Neither is a cron. A future caller that cannot hold a token belongs in that
// list with its arm, not in a widened guard.
function requireToken(mode) {
  if (process.env.GITHUB_TOKEN) return
  console.log(`${mode} needs GITHUB_TOKEN. It enumerates the window's merged pull requests through the GitHub API, and unauthenticated it enumerates nothing -- which this mode would otherwise print as a window with no undispositioned merge in it. Set GITHUB_TOKEN and re-run; an API that is reachable but failing still reports and exits 0, because that is an outage rather than a misconfiguration.`)
  process.exit(2)
}

function cmdRecordDispositions(since) {
  requireToken('--record')
  const enumerated = mergedPRsFromWindow(since)
  const prs = enumerated.prs
  console.log(`RECORD_ENUM: ${enumerated.mode}${enumerated.why ? ` (${enumerated.why})` : ''}`)
  // The enumeration guard's loud half (#957 discipline -- see enumSkipLine).
  // RECORD_ENUM alone states the MODE, not the confidence: a reader who stops
  // at `TOTAL: 0 error(s)` sees a measured window, and the fallback's zero over
  // merge commits measured nothing. The skip line says UNCHECKED out loud; the
  // verdict lines below keep their semantics, so what a seat reads beside them
  // is the marker, not a silent green.
  if (enumerated.why) console.log(enumSkipLine(enumerated.why))
  const { region, sectionFound } = recordRegionOverTree()
  const all = sectionFound
    ? checkRecord(prs, region)
    : [{ severity: 'error', check: 'record', where: DISPOSITION_FILES[0],
         message: `no \`## ${RECORD_SECTION}\` section, so the record has no region to read and every merge in the window would report as undispositioned. Restore the heading, or change RECORD_SECTION with it.` }]
  const applied = applyKnownBad(all, RECORD_KEY)
  // Counted and printed apart from the record findings: `all.length` is the
  // undispositioned-merge count and folding a different class into it would
  // make that sentence false.
  const split = DISPOSITION_FILES.flatMap((rel) => {
    const t = read(rel)
    return t ? checkTableSplit(rel, t) : []
  })
  // Only the cap rule runs here. The other eight were driven over these two
  // documents before this was wired and reported four figures, every one a
  // quotation of history inside a disposition row -- the genre these files are
  // made of. The cap rule reported one, and it was true.
  const caps = DISPOSITION_FILES.flatMap((rel) => {
    const t = read(rel)
    return t ? checkCounts(rel, t, { caps: derivations().caps }) : []
  })
  const rendered = DISPOSITION_FILES.flatMap((rel) => {
    const t = read(rel)
    return t ? checkRender(rel, t) : []
  })
  const rCounts = DISPOSITION_FILES.reduce((acc, rel) => {
    const t = read(rel)
    if (!t) return acc
    const s = inspectRender(t)
    acc.tables += s.tables
    acc.rows += s.rows
    acc.lists += s.lists
    acc.items += s.items
    return acc
  }, { tables: 0, rows: 0, lists: 0, items: 0 })
  console.log(`RECORD: ${prs.length} merged pull request(s) in ${since}..${mainRef()}; ${all.length} without a disposition in ${DISPOSITION_FILES.join(', ')} or ${ROW_DIR}/`)
  console.log(`TABLES: ${split.length} split table(s) across ${DISPOSITION_FILES.length} disposition document(s)`)
  console.log(`CAPS: ${caps.length} stated cap(s) disagreeing with policy_budgets.json across ${DISPOSITION_FILES.length} disposition document(s)`)
  console.log(`RENDER: ${rCounts.tables} table(s), ${rCounts.rows} row(s), ${rCounts.lists} list(s), ${rCounts.items} item(s) across ${DISPOSITION_FILES.length} disposition document(s)`)
  printFindings([...applied.live, ...split, ...caps, ...rendered])
  console.log(`\nKNOWN-BAD: ${applied.suppressed} of ${applied.total} recorded record-class defect(s) still present, in ${applied.occurrences} recorded occurrence(s)`)
  const errors = [...applied.live, ...split, ...caps, ...rendered].filter((f) => f.severity === 'error').length
  console.log(`\nTOTAL: ${errors} error(s) over ${prs.length} merged pull request(s)`)
  process.exit(errors > 0 ? 1 : 0)
}

function cmdStats(since) {
  const enumerated = mergedPRsFromWindow(since)
  const prs = enumerated.prs
  const classes = verdictClasses()
  // BOTH HALVES OF THE GRAMMAR, or nothing: the words the reviewer prompt
  // teaches and the parser the wave acts on (#1472, D13-02). With the parser
  // unreadable every `Fix review:` line would land outside the grammar and this
  // mode would print a histogram of zeroes -- the opposite-claims shape the
  // fetch guard below exists to refuse -- so it withholds, as it does for the
  // words.
  if (!classes || !waveVerdictRe()) {
    console.log(`STATS: could not read the verdict grammar from ${WAVE_SCRIPT}; classifying nothing rather than against a list typed here.`)
    process.exit(0)
  }
  const blocks = blockClasses()
  // The enumeration guard: the loud half first (enumSkipLine), then the failure
  // rides the SAME fetchError channel a window-fetch failure rides, so
  // statsFindings prints its opposite-claims finding ("Printing no histogram
  // rather than a histogram of zeroes") and carries the `could not fetch
  // pull-request bodies and comments` phrase friction_issues.mjs refuses on --
  // the filer, unchanged, then refuses a marked output instead of filing
  // nothing in silence. fetchWindow is skipped entirely: a histogram over a
  // window that could not be enumerated is a partial-window claim, the exact
  // shape fetchWindow's own any-failure abort exists to prevent.
  if (enumerated.why) console.log(enumSkipLine(enumerated.why))
  const { fetched, fetchError } = enumerated.why
    ? { fetched: new Map(), fetchError: enumerated.why }
    : fetchWindow(prs)
  console.log(`STATS: ${prs.length} merged pull request(s) in ${since}..${mainRef()}; verdict grammar ${JSON.stringify(classes)}${blocks ? ` over block classes ${JSON.stringify(blocks)}` : ' (VERDICT_CLASSES unreadable)'} read from ${WAVE_SCRIPT}`)
  if (!fetchError) {
    const { verdicts, friction, coverage, endpoints } = statsHistogram(prs, fetched, classes)
    // The coverage line, under `STATS:` and above the tables it describes
    // (#1406, D13-02): the verdict table's denominator is the pull requests
    // that carried a verdict, and until this line existed the mode printed only
    // the window's merge count -- so a merge with no verdict read as one more
    // row of a full window rather than as a gap in the table's population.
    console.log(statsCoverageLine(coverage))
    // ...and the endpoint census beside it (#1471, D13-01): the coverage line
    // says how many merges carried a verdict, this one says which of the two
    // endpoints they arrived on, so a reviews row at zero is read as "none were
    // posted" over a reader that does ask for them.
    console.log(statsEndpointLine(endpoints))
    // Both counts in the table, threshold on the left one, because a reader who
    // sees only "4" cannot tell 4 occasions from one body written four times.
    for (const [label, hist] of [['verdict class', verdicts], ['friction rule id', friction]]) {
      console.log(`\n${label} (PRs / entries):`)
      const rows = [...hist.entries()].sort((a, b) => b[1].prs.size - a[1].prs.size || b[1].entries - a[1].entries)
      if (!rows.length) console.log('  (none in this window)')
      for (const [k, cell] of rows) {
        const n = cell.prs.size
        console.log(`  ${String(n).padStart(4)} / ${String(cell.entries).padEnd(4)}  ${k}${n >= FRICTION_THRESHOLD ? '   <- at or over threshold' : ''}`)
      }
      // The machine-readable census, tab-separated with the key LAST because
      // one key -- the unlabelled bucket -- carries spaces. friction_issues.mjs
      // reads it to re-measure the keys of issues it already filed: the
      // would-open lines alone name only the keys still over the threshold, and
      // a close path needs the count of the ones that are not.
      for (const [k, cell] of rows) console.log(`CENSUS\t${label}\t${cell.prs.size}\t${cell.entries}\t${k}`)
    }
    console.log(`\nCENSUS: ${verdicts.size + friction.size} key(s)`)
  }
  const found = statsFindings({ prs, fetched, fetchError, classes, blocks })
  console.log(`\nthreshold: ${FRICTION_THRESHOLD} or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.`)
  printFindings(found)
  console.log(`\nWOULD OPEN: ${found.filter((f) => f.message.startsWith('would open')).length} issue(s)`)
  process.exit(0)
}

function cmdSunset(since) {
  // #1050's residual 1, taken here rather than left: this line dropped
  // `.why` on the floor, so `--sunset` was the one loop mode that stayed silent
  // on a dead fetch while its two siblings printed the marker. #1050 classed it
  // informational-lane-only and that was defensible then. It stopped being
  // defensible in THIS pull request, which makes `--sunset` refuse a bad ref
  // loudly through `requireSince`: a mode that shouts about an underivable
  // window and says nothing about an unenumerable one teaches the reader that
  // silence here means measured. The marker is `enumSkipLine` unchanged -- the
  // same words on the same lane, not a second vocabulary.
  const enumerated = mergedPRsFromWindow(since)
  const prs = enumerated.prs
  if (enumerated.why) console.log(enumSkipLine(enumerated.why))
  const classes = verdictClasses()
  const { fetched, fetchError } = fetchWindow(prs)
  const friction = fetchError || !classes ? null : statsHistogram(prs, fetched, classes).friction
  const fires = detectorFires(friction)
  const rows = policyFiles().map((f) => ({ file: f, text: read(f) }))
  const found = checkSunset(rows, { friction, fires, today: new Date() })
  console.log(`SUNSET: ${rows.length} policy file(s) over ${since}..${mainRef()}${fetchError ? `; no friction data (${fetchError}), so honour rules are not evaluated` : ''}`)
  // What the zeroes below are a zero OF (#1469, D11-03): the class reads markers
  // a rule declares for itself, so it says which of them the corpus carries
  // before it prints the counts that would otherwise read as a swept clean.
  console.log(sunsetMarkerLine(rows))
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
  if (argv[0] === '--corpus-filter') return cmdCorpusFilter(), process.exit(0)
  if (argv[0] === '--normalize-friction-keys') return cmdNormalizeKeys(), process.exit(0)
  if (argv[0] === '--rule-binding') return cmdRuleBinding(), process.exit(0)

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
    // Through `requireSince` like the three loop modes, not around it: this is
    // the fourth consumer of a caller-supplied ref, and a reseed that re-measured
    // the record class over a window it could not derive would write `0` into
    // the known-bad file as a MEASUREMENT. `requireSince` only refuses a ref
    // that was given, so the no-window reseed below is unaffected.
    if (since) findings.push(...checkRecord(mergedPRsFromWindow(requireSince(since, '--record-known-bad')).prs, recordRegionOverTree().region))
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

// Exported for `policy_lint_mutants.mjs`, which empties one check at a time and
// demands this acceptance go red. The mutation lane must learn WHICH checks
// exist from production rather than from a list of its own: a second copy of
// either enumeration is the same defect one level up, and a regex over this
// file's source would re-derive it from spelling. `CORPUS_CHECK_NAMES` and
// `LOOP_CHECK_NAMES` are the two enumerations -- the corpus checks and the
// record mode's -- `assertAcceptance` is the thing under test, and
// `derivations` is its only argument.
export { CORPUS_CHECK_NAMES, LOOP_CHECK_NAMES, assertAcceptance, derivations, frictionEntries, AUTOFIX_BOT_COMMITS }

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
