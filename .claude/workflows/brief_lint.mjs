// Citation linter for .claude/workflows/wave-*-groups.json (issue #411).
//
// WHY THIS EXISTS. A brief is dense with measurements stated as literals --
// line numbers, harness paths, symbol names, budget figures -- and nothing
// checks that any of them still resolves. `.claude/` is on tests/closure.py's
// INERT list, so CI structurally cannot see this directory; this script runs
// by hand and is driven into CI by its own never-scoped job (tests.yml's
// `briefs`, shaped like `browser`'s), the same precedent as
// check-wave-script.mjs and tests/card_browser.mjs.
//
// Four citation classes, each cheap and offline (git objects already on
// disk; no network):
//   1. file paths        -- exist in the tree, or are cited with a tag ref
//                            that actually carries them (`git cat-file -e
//                            <ref>:<path>`, never a fetch).
//   2. path:line          -- the range resolves, and text the brief
//                            attributes to it (a quoted phrase, a curated
//                            code keyword, or a code-shaped identifier pulled
//                            from the words around the citation) is found
//                            there, in its enclosing def/class chain, or --
//                            failing that -- reported at wherever else in the
//                            file it now lives.
//   3. named symbols       -- exist somewhere in the tracked tree, or at a
//                            cited tag.
//   4. structure_budgets.json metrics -- must exist; a literal value quoted
//                            for one is ALWAYS an error (issue #411, class 4:
//                            "not merely stale"), because the fixer is
//                            supposed to re-measure at their own merge base.
// Plus: every `after:` edge names a group in the same file, and every group
// carries the fields a cold pickup needs -- a lintable `brief` and a `resume`
// (#582). Those are checked for presence and type only; see `checkShape`.
//
// A brief whose `resume.stage` is "done" describes finished, merged work: no
// fixer will read it again, so it is not linted -- checking it would only
// report citations that rotted after they stopped mattering.
//
// A citation this script cannot resolve reliably (no anchor text extracted,
// ambiguous shorthand, no tag object present locally) is a WARNING, not a
// failure -- a linter that cries wolf gets bypassed. Run:
//   node .claude/workflows/brief_lint.mjs [files...]
//
// The no-arg (CI) path also runs three acceptances, because every rule here is
// otherwise deletable in silence -- this job reports what the rules FOUND, and
// finding nothing is what a clean tree and a gutted linter both look like.
// fixtures/wave-1b-931dffe.json pins lintBrief, fixtures/shape-defects.json
// pins checkShape, and a probe pins the driver guard. Each states the errors it
// must still produce; see REQUIRED_931DFFE.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'

const HERE = path.dirname(fileURLToPath(import.meta.url))
export const ROOT = path.resolve(HERE, '..', '..')

const CODE_EXTS = ['py', 'mjs', 'js', 'json', 'yaml', 'yml', 'md', 'sh', 'txt', 'patch', 'out']
export const EXT_RE = CODE_EXTS.join('|')
const EXT_SET = new Set(CODE_EXTS)

// ---------------------------------------------------------------------------
// git plumbing -- every call reads objects already on disk; nothing fetches.

export function git(args, opts = {}) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], ...opts })
  } catch (e) {
    if (opts.allowFail) return null
    throw e
  }
}

function basenameMap(files) {
  const byBase = new Map()
  for (const f of files) {
    const b = path.posix.basename(f)
    if (!byBase.has(b)) byBase.set(b, [])
    byBase.get(b).push(f)
  }
  return byBase
}

let _trackedFiles = null
export function trackedFiles() {
  if (_trackedFiles) return _trackedFiles
  const out = git(['ls-files'])
  const list = out.split('\n').filter(Boolean)
  _trackedFiles = { set: new Set(list), byBase: basenameMap(list), list }
  return _trackedFiles
}

const _refResolveCache = new Map()
export function refResolves(ref) {
  if (_refResolveCache.has(ref)) return _refResolveCache.get(ref)
  const out = git(['rev-parse', '--verify', '--quiet', `${ref}^{commit}`], { allowFail: true })
  const ok = !!(out && out.trim())
  _refResolveCache.set(ref, ok)
  return ok
}

const _refFilesCache = new Map()
function refFiles(ref) {
  if (_refFilesCache.has(ref)) return _refFilesCache.get(ref)
  if (!refResolves(ref)) {
    _refFilesCache.set(ref, null)
    return null
  }
  const out = git(['ls-tree', '-r', '--name-only', ref], { allowFail: true })
  const list = out ? out.split('\n').filter(Boolean) : []
  const result = { set: new Set(list), byBase: basenameMap(list) }
  _refFilesCache.set(ref, result)
  return result
}

// Resolve a token against a file listing (either the working tree's or a
// tag's). Exact path wins; otherwise any file sharing the basename -- a bare
// filename in prose ("model_sanity.py") does not commit to a directory, so
// ambiguity between two same-named files is not grounds to call it unresolved.
function lookupPath(listing, token) {
  if (listing.set.has(token)) return token
  const base = path.posix.basename(token)
  const cands = listing.byBase.get(base)
  return cands && cands.length ? cands[0] : null
}

// A token whose basename does not resolve anywhere, but IS a substring of
// some tracked file's basename, is probably brief shorthand ("card.js" for
// ".../heatpump-optimizer-card.js") rather than a rotted citation -- warn,
// don't fail, since this cannot be resolved reliably.
function shorthandCandidates(token) {
  const stem = path.posix.basename(token).replace(/\.[^.]+$/, '')
  if (stem.length < 3) return []
  const { list } = trackedFiles()
  const low = stem.toLowerCase()
  return list.filter((f) => path.posix.basename(f).toLowerCase().includes(low)).slice(0, 5)
}

export function resolvePathToken(token) {
  return lookupPath(trackedFiles(), token)
}

const _tagFileCache = new Map()
// null = ref not resolvable locally (can't verify, no network attempted).
function pathExistsAtRef(ref, token) {
  const key = `${ref}:${token}`
  if (_tagFileCache.has(key)) return _tagFileCache.get(key)
  const listing = refFiles(ref)
  const result = listing === null ? null : !!lookupPath(listing, token)
  _tagFileCache.set(key, result)
  return result
}

function symbolInRefTree(ref, symbol) {
  if (!refResolves(ref)) return null
  const out = git(['grep', '-I', '-l', '-w', '-F', symbol, ref], { allowFail: true })
  return !!(out && out.trim())
}

// One directory is excluded from "does this symbol exist anywhere":
//   .claude/            -- every wave-*-groups.json brief IS the text this
//                          script is scanning, so a symbol it names would
//                          otherwise "exist" by matching its own citation.
//
// `tools/audit/round2` was the second entry, for the same reason in a different
// shape -- write-once evidence, prose ABOUT a finding rather than resolvable
// current state, so a symbol mentioned only there would have passed the check
// on the strength of the report describing the rot. That tree is archived and
// no tracked file starts with the prefix any more, so the entry stopped
// excluding anything and was deleted. IT WAS NOT NOTICED BY ANYTHING: the list
// had no assertion, which is precisely the hole `policy_lint`'s
// `CORPUS_EXCLUDED` assertion was written to close two rounds earlier -- an
// exclusion that names nothing is a destination waiting to be used, because a
// file written at that path later is excluded with no diff to this file for a
// reviewer to see. `assertGrepExcludeBounded` below now bounds this list the
// same way, in BOTH directions.
const SYMBOL_GREP_EXCLUDE = [':!.claude']

// The entries this list cannot lose without the check going quietly vacuous.
// A ceiling alone is half the answer: deleting `.claude` would make every
// symbol cited by a roster "exist" by matching its own citation, and nothing
// downstream would report a thing.
const SYMBOL_GREP_EXCLUDE_FLOOR = [':!.claude']

export function symbolInTree(symbol) {
  const out = git(['grep', '-I', '-l', '-w', '-F', symbol, '--', '.', ...SYMBOL_GREP_EXCLUDE], { allowFail: true })
  return !!(out && out.trim())
}

const _fileLinesCache = new Map()
export function fileLines(relPath) {
  if (_fileLinesCache.has(relPath)) return _fileLinesCache.get(relPath)
  let lines = null
  try {
    lines = fs.readFileSync(path.join(ROOT, relPath), 'utf8').split('\n')
  } catch {
    lines = null
  }
  _fileLinesCache.set(relPath, lines)
  return lines
}

// ---------------------------------------------------------------------------
// tag-like reference extraction: 7-40 hex chars with at least one a-f letter
// (so a plain decimal count, e.g. a line number, never matches), or the
// literal evidence-tag name. Checked per BRIEF, not per-citation proximity:
// briefs are short paragraphs, and issue #411 licenses "cited together with"
// at that grain.

const SHA_RE = /\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f][0-9a-f]*\b)[0-9a-f]{7,40}\b/g
const TAG_NAME_RE = /\baudit-round2-evidence\b/g

export function tagRefsIn(text) {
  const refs = new Set()
  for (const m of text.matchAll(SHA_RE)) refs.add(m[0])
  for (const m of text.matchAll(TAG_NAME_RE)) refs.add(m[0])
  return [...refs]
}

// Resolve a path/symbol against every tag ref cited in the brief.
//   'ok'    -- at least one cited ref carries it: tag-scoped, accepted.
//   'error' -- at least one cited ref resolves locally but does NOT carry it,
//              and none that resolves does.
//   'warn'  -- every cited ref is unresolvable locally (nothing to check
//              without a fetch this script will not perform).
//   'none'  -- no ref was cited at all.
export function checkAgainstTags(refs, checkFn) {
  if (refs.length === 0) return { status: 'none' }
  let sawResolvable = false
  for (const ref of refs) {
    const r = checkFn(ref)
    if (r === true) return { status: 'ok', ref }
    if (r === false) sawResolvable = true
  }
  return sawResolvable ? { status: 'error' } : { status: 'warn' }
}

export function reportUnresolvedPath(add, kind, label, token, tagResult, refs) {
  if (tagResult.status === 'warn') {
    add('warning', kind, `${label}: not in the tree; cited tag ref(s) [${refs.join(', ')}] not resolvable locally (no network attempted) -- accepting textual co-citation`)
  } else if (tagResult.status === 'error') {
    add('error', kind, `${label}: not in the tree, and not present at its cited tag ref(s) [${refs.join(', ')}]`)
  } else {
    const short = shorthandCandidates(token)
    if (short.length) {
      add('warning', kind, `${label}: not in the tree and no tag cited; could be shorthand for ${short.join(', ')} -- verify by hand`)
    } else {
      add('error', kind, `${label}: not in the tree, and no tag SHA is cited alongside it`)
    }
  }
}

// ---------------------------------------------------------------------------
// symbol-candidate extraction: code-shaped tokens only, so English prose
// cannot flood the symbol check. Snake_case (>=2 segments, leading
// underscores allowed -- most production helpers here are private),
// SCREAMING_SNAKE, dotted module.symbol, or a genuinely quoted phrase.

export const SNAKE_RE = /\b_*[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g
export const SCREAM_RE = /\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g
const DOTTED_RE = /\b([a-z][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b/g
// A single/double quote pair only counts as a quoted PHRASE when the opening
// mark is preceded by whitespace/bracket/punctuation (or string start) and
// the closing mark is followed by the same -- otherwise `scipy's` and
// `jac's f0` read as a spurious quotation spanning both possessives.
const QUOTED_RE = /(?:^|[\s([{:,\u2014-])['"]([^'"\n]{3,60})['"](?=[\s.,;:)\]}!?\u2014-]|$)/g

// Common code keywords that are legitimate anchors for a path:line citation
// ("the return around :1152") but too generic to run through the tree-wide
// named-symbol check.
const KEYWORD_ANCHORS = ['return', 'raise', 'assert', 'yield', 'except', 'elif', 'lambda', 'continue', 'break']

export function symbolCandidates(text) {
  const out = new Set()
  for (const m of text.matchAll(SNAKE_RE)) out.add(m[0])
  for (const m of text.matchAll(SCREAM_RE)) out.add(m[0])
  return [...out]
}

export function dottedCandidates(text) {
  const out = []
  for (const m of text.matchAll(DOTTED_RE)) {
    if (EXT_SET.has(m[2])) continue // "card_geometry.mjs" is a path, not module.symbol
    out.push({ module: m[1], symbol: m[2], full: m[0] })
  }
  return out
}

export function quotedPhrases(text) {
  const out = new Set()
  for (const m of text.matchAll(QUOTED_RE)) {
    const p = m[1].trim()
    if (/[a-zA-Z]/.test(p) && p.length >= 4) out.add(p)
  }
  return [...out]
}

function keywordsIn(text) {
  return KEYWORD_ANCHORS.filter((k) => new RegExp(`\\b${k}\\b`).test(text))
}

export function resolveModuleFile(moduleName) {
  const { byBase } = trackedFiles()
  for (const ext of ['py', 'mjs', 'js']) {
    const cands = byBase.get(`${moduleName}.${ext}`)
    if (cands && cands.length) return cands[0]
  }
  return null
}

// ---------------------------------------------------------------------------
// class 1 + 2 path tokens

export const PATH_TOKEN_RE = new RegExp(
  `\\b(?:[A-Za-z0-9_][A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\\.(?:${EXT_RE})\\b`,
  'g'
)
export const PATHLINE_RE = new RegExp(
  `(?<pth>(?:[A-Za-z0-9_][A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\\.(?:${EXT_RE}))` +
    `:(?<start>\\d+)(?:[-\u2013](?<end>\\d+))?\\+?`,
  'g'
)
// Bare `:N` (optionally a range) not already part of a path:line match -- the
// anchored form fixer.md's citation guidance prefers, back-referencing a
// module.symbol mentioned nearby in the same brief.
const BARE_LINE_RE = /(?<!\w)(?<!\.\w{1,4}):(?<start>\d+)(?:[-\u2013](?<end>\d+))?(?!\d)/g

// A brief that says "do not go looking for X" or "X does not exist" is
// documenting an ABSENCE on purpose (a fixer trap), not citing something it
// expects to resolve. Skip those rather than reporting the rot the brief
// already named.
export const NEGATION_RE = /\b(?:do not go looking for|must not exist|should not exist|never existed|does not exist|whose source is (?:only )?in)\s*$/i

const DEF_RE_PY = /^(\s*)(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)/
const DEF_RE_JS = /^(\s*)(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)/

function enclosingScopeChain(lines, zeroBasedLine, isJs) {
  const chain = []
  let indentLimit = Infinity
  const defRe = isJs ? DEF_RE_JS : DEF_RE_PY
  for (let i = Math.min(zeroBasedLine, lines.length - 1); i >= 0; i--) {
    const m = lines[i].match(defRe)
    if (m) {
      const indent = m[1].length
      if (indent < indentLimit) {
        chain.push(m[2])
        indentLimit = indent
        if (indent === 0) break
      }
    }
  }
  return chain
}

function windowText(lines, startLine, endLine, pad) {
  const s = Math.max(0, startLine - 1 - pad)
  const e = Math.min(lines.length, endLine + pad)
  return lines.slice(s, e).join('\n')
}

// The enclosing sentence/clause around a citation: bounded by `.` or `;`
// followed by whitespace (or the string's ends), capped at `radius` so one
// run-on paragraph cannot swallow an unrelated citation's anchor text. This
// is what keeps two citations in the same sentence -- a path:line and,
// thirty words later, an unrelated quoted phrase about a different file --
// from cross-contaminating each other's anchors.
function clauseWindow(text, idx, radius) {
  const isBoundary = (i) => /[.;]/.test(text[i]) && (i + 1 >= text.length || /\s/.test(text[i + 1]))
  let start = idx
  let end = idx
  while (start > 0 && !isBoundary(start - 1)) start--
  while (end < text.length && !isBoundary(end)) end++
  const s = Math.max(start, idx - radius)
  const e = Math.min(end + 1, idx + radius)
  return text.slice(s, e)
}

function anchorCandidatesFor(context, excludeStems) {
  const cands = new Set()
  for (const p of quotedPhrases(context)) cands.add(p)
  for (const k of keywordsIn(context)) cands.add(k)
  for (const s of symbolCandidates(context)) {
    if (!excludeStems.has(s)) cands.add(s)
  }
  return [...cands]
}

function findCandidateElsewhere(lines, candidate) {
  const idx = lines.findIndex((l) => l.includes(candidate))
  return idx === -1 ? null : idx + 1
}

export function checkPathLine(relPath, start, end, context, excludeStems, exact) {
  const lines = fileLines(relPath)
  if (!lines) return { ok: false, reason: `${relPath} could not be read` }
  if (start > lines.length) return { ok: false, reason: `line ${start} is past end of file (${lines.length} lines)` }
  const isJs = /\.(mjs|js)$/.test(relPath)
  const pad = exact ? 0 : 1 // an explicit range is checked as given; a single line gets +-1 for off-by-one
  const win = windowText(lines, start, end ?? start, pad)
  const candidates = anchorCandidatesFor(context, excludeStems)
  if (candidates.length === 0) {
    return { ok: true, warn: true, reason: 'no anchor text extracted near the citation; line range only' }
  }
  const chain = enclosingScopeChain(lines, start - 1, isJs)
  for (const c of candidates) {
    if (win.includes(c)) return { ok: true, matched: c }
    if (chain.includes(c)) return { ok: true, matched: c, via: 'enclosing scope' }
  }
  const bySpecificity = [...candidates].sort((a, b) => b.length - a.length)
  for (const c of bySpecificity) {
    const foundAt = findCandidateElsewhere(lines, c)
    if (foundAt) {
      return { ok: false, reason: `'${c}' not found near ${relPath}:${start}${end ? '-' + end : ''}; found at line ${foundAt} instead` }
    }
  }
  return { ok: false, reason: `none of [${bySpecificity.join(', ')}] found near ${relPath}:${start}${end ? '-' + end : ''}, or anywhere else in the file` }
}

// ---------------------------------------------------------------------------
// class 4: structure_budgets.json metrics

let _budgets = null
export function budgets() {
  if (_budgets) return _budgets
  _budgets = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests', 'structure_budgets.json'), 'utf8'))
  return _budgets
}

export function resolveMetricName(word) {
  const b = budgets()
  if (word in b) return word
  const suffix = `_${word}`
  const hits = Object.keys(b).filter((k) => k.endsWith(suffix))
  if (hits.length === 0) return null
  hits.sort((a, c) => a.length - c.length) // shortest match wins a suffix tie
  return hits[0]
}

// `word NUMBER <comparator> NUMBER` -- the literal-figure shape #411 names.
export const METRIC_LITERAL_RE = /\b([a-z][a-z_]{2,})\s+(\d+(?:\.\d+)?)\s*(<=|>=|==|<|>)\s*(\d+(?:\.\d+)?)\b/g

// ---------------------------------------------------------------------------
// class 3-narrow: VERSION drift. Checked against the live root VERSION file
// (not flagged unconditionally like a budget), because the brief is
// asserting the current release, not instructing a re-measurement.

let _liveVersion
export function liveVersion() {
  if (_liveVersion !== undefined) return _liveVersion
  try {
    _liveVersion = fs.readFileSync(path.join(ROOT, 'VERSION'), 'utf8').trim()
  } catch {
    _liveVersion = null
  }
  return _liveVersion
}

const VERSION_ARROW_RE = /\bVERSION\b[^.\n]{0,40}?(\d+\.\d+\.\d+)\s*->\s*(\d+\.\d+\.\d+)/g
const VERSION_DIRECT_RE = /\bVERSION\b(?:\s+is\s+|\s*==\s*|\s+)(\d+\.\d+\.\d+)\b/g

function versionLiteralsIn(text) {
  const claims = new Set()
  for (const m of text.matchAll(VERSION_ARROW_RE)) claims.add(m[2])
  for (const m of text.matchAll(VERSION_DIRECT_RE)) claims.add(m[1])
  return [...claims]
}

// ---------------------------------------------------------------------------
// per-brief lint

function lintBrief(groupName, brief, findings) {
  const add = (severity, kind, message) => findings.push({ group: groupName, severity, kind, message })
  const briefTagRefs = tagRefsIn(brief)

  const pathlineMatches = [...brief.matchAll(PATHLINE_RE)]
  const pathlineSpans = pathlineMatches.map((m) => [m.index, m.index + m[0].length])
  const insidePathline = (i) => pathlineSpans.some(([s, e]) => i >= s && i < e)

  // --- class 1: bare file paths (no line number) ------------------------
  const seenBarePaths = new Set()
  for (const m of brief.matchAll(PATH_TOKEN_RE)) {
    if (insidePathline(m.index)) continue // covered by class 2 below
    const token = m[0]
    if (seenBarePaths.has(token)) continue
    seenBarePaths.add(token)
    if (NEGATION_RE.test(brief.slice(Math.max(0, m.index - 60), m.index))) continue // brief asserts this does NOT exist
    if (resolvePathToken(token)) continue
    const tagResult = checkAgainstTags(briefTagRefs, (ref) => pathExistsAtRef(ref, token))
    if (tagResult.status === 'ok') continue
    reportUnresolvedPath(add, 'path', token, token, tagResult, briefTagRefs)
  }

  // --- class 2: path:line -------------------------------------------------
  for (const m of pathlineMatches) {
    const token = m.groups.pth
    const start = Number(m.groups.start)
    const end = m.groups.end ? Number(m.groups.end) : undefined
    const label = `${token}:${start}${end ? '-' + end : ''}`
    const resolved = resolvePathToken(token)
    if (!resolved) {
      const tagResult = checkAgainstTags(briefTagRefs, (ref) => pathExistsAtRef(ref, token))
      if (tagResult.status === 'ok') continue
      reportUnresolvedPath(add, 'path:line', label, token, tagResult, briefTagRefs)
      continue
    }
    const context = clauseWindow(brief, m.index, 220)
    const stems = new Set([token, path.posix.basename(token), path.posix.basename(token).replace(/\.[^.]+$/, '')])
    const r = checkPathLine(resolved, start, end, context, stems, end !== undefined)
    if (!r.ok) add('error', 'path:line', `${label}: ${r.reason}`)
    else if (r.warn) add('warning', 'path:line', `${label}: ${r.reason}`)
  }

  // --- class 2b: bare :line anchored forms -------------------------------
  for (const m of brief.matchAll(BARE_LINE_RE)) {
    if (insidePathline(m.index)) continue
    const start = Number(m.groups.start)
    const end = m.groups.end ? Number(m.groups.end) : undefined
    const before = brief.slice(Math.max(0, m.index - 150), m.index)
    const dotted = dottedCandidates(before).pop()
    if (!dotted) continue // no resolvable file context: leave to the symbol check
    const resolvedFile = resolveModuleFile(dotted.module)
    if (!resolvedFile) continue
    const label = `${dotted.full}:${start}${end ? '-' + end : ''}`
    // Tight, asymmetric window: the qualifying phrase for a bare back-
    // reference sits mostly BEFORE it ("the return around :1152"); a wide
    // symmetric window pulls in the NEXT clause's unrelated symbols.
    const context = brief.slice(Math.max(0, m.index - 70), Math.min(brief.length, m.index + 15))
    const stems = new Set([dotted.module, dotted.symbol, dotted.full])
    const r = checkPathLine(resolvedFile, start, end, context, stems, false)
    if (!r.ok) add('error', 'path:line (anchored)', `${label} (${resolvedFile}): ${r.reason}`)
    else if (r.warn) add('warning', 'path:line (anchored)', `${label}: ${r.reason}`)
  }

  // --- class 3: named symbols ---------------------------------------------
  const consumedStems = new Set()
  for (const m of pathlineMatches) consumedStems.add(path.posix.basename(m.groups.pth).replace(/\.[^.]+$/, ''))
  for (const m of brief.matchAll(PATH_TOKEN_RE)) consumedStems.add(path.posix.basename(m[0]).replace(/\.[^.]+$/, ''))

  for (const d of dottedCandidates(brief)) {
    const resolvedFile = resolveModuleFile(d.module)
    if (!resolvedFile) continue
    const lines = fileLines(resolvedFile)
    if (lines && lines.some((l) => l.includes(d.symbol))) continue
    if (symbolInTree(d.symbol)) continue
    const tagResult = checkAgainstTags(briefTagRefs, (ref) => symbolInRefTree(ref, d.symbol))
    if (tagResult.status === 'ok') continue
    if (tagResult.status === 'warn') {
      add('warning', 'symbol', `${d.full}: '${d.symbol}' not found in ${resolvedFile}; cited tag ref(s) not resolvable locally`)
    } else if (tagResult.status === 'error') {
      add('error', 'symbol', `${d.full}: '${d.symbol}' not found in ${resolvedFile}, and not present at its cited tag ref(s)`)
    } else {
      add('error', 'symbol', `${d.full}: '${d.symbol}' not found in ${resolvedFile}`)
    }
  }

  for (const s of symbolCandidates(brief)) {
    if (consumedStems.has(s)) continue
    if (resolveMetricName(s)) continue // valid bare metric mention; the literal-value case is handled below
    if (symbolInTree(s)) continue
    const tagResult = checkAgainstTags(briefTagRefs, (ref) => symbolInRefTree(ref, s))
    if (tagResult.status === 'ok') continue
    if (tagResult.status === 'warn') {
      add('warning', 'symbol', `'${s}': not found in the tracked tree; cited tag ref(s) not resolvable locally`)
    } else {
      // 'error' (a cited tag resolves locally but does not carry it) and
      // 'none' (no tag cited at all) both mean the same thing here: nothing
      // in this run can find the symbol anywhere it could legitimately live.
      add('error', 'symbol', `'${s}': not found in the tracked tree${tagResult.status === 'error' ? ', and not present at its cited tag ref(s)' : ' (no tag cited either)'}`)
    }
  }

  // --- class 4: structure_budgets.json metric literals --------------------
  for (const m of brief.matchAll(METRIC_LITERAL_RE)) {
    const metric = resolveMetricName(m[1])
    if (!metric) continue // not metric-shaped prose; already covered by the symbol check
    add('error', 'metric', `'${m[1]} ${m[2]} ${m[3]} ${m[4]}' cites a literal value for ${metric}; #411 rule 4: a fixer must re-measure at their own merge base, a literal is always an error`)
  }

  // --- class 3-narrow: VERSION literals ------------------------------------
  const lv = liveVersion()
  if (lv) {
    for (const claim of versionLiteralsIn(brief)) {
      if (claim !== lv) add('error', 'version', `VERSION ${claim} cited; live VERSION is ${lv}`)
    }
  }
}

function lintAfterEdges(groups, findings) {
  const names = new Set(groups.filter((g) => typeof g?.group === 'string').map((g) => g.group))
  for (const g of groups) {
    // `after` is iterated, so a string here would silently walk its characters.
    if (!Array.isArray(g?.after)) continue
    for (const dep of g.after) {
      if (!names.has(dep)) {
        findings.push({ group: g.group, severity: 'error', kind: 'after', message: `after: '${dep}' names no group in this file` })
      }
    }
  }
}

// ---------------------------------------------------------------------------
// roster shape (#582)
//
// A roster promises two things to a seat picking a lane up cold: a `brief` this
// script can check, and a `resume` saying where the lane restarts. Nothing
// checked either. A group missing `brief` threw a TypeError out of lintBrief --
// and because the no-arg run lints in sorted order with nothing catching, ONE
// malformed roster suppressed every later roster's findings and the fixture
// vacuity assertion with them. A group missing `resume` was accepted in
// silence, which is the deficit #582 names.
//
// These check PRESENCE AND TYPE, never truthfulness. Deliberately no vocabulary
// check on `stage`: only the exact string "done" skips a brief, so every
// misspelling already fails safe by linting MORE, and a `stage` that simply
// lies about a lane's state passes a vocabulary check anyway. A rule that
// catches only the safe direction would look like protection and add none.
//
// TWO THINGS THIS MUST NOT DO, both found by the acceptance fixture below when
// an earlier draft did them.
//   * It does not gate lintBrief. A group missing `resume` still has its
//     citations checked; the missing field is reported beside them. Letting a
//     shape failure silence the citation check is one check disabling another,
//     which is the defect class this repository keeps paying for -- the draft
//     that did it removed all nine of the fixture's acceptance pins and the
//     vacuity assertion is what caught it.
//   * It does not run on the fixture, which is a FROZEN SNAPSHOT of the roster
//     at 931dffe, when nine of its fifteen groups carried no `resume` at all.
//     Those absences are the historical record and are not defects to repair;
//     reporting them would invite a later seat to "fix" the fixture and destroy
//     what it pins.
const STAGE_SKIP = 'done'

// Reports shape defects. Purely additive: it never decides what gets linted.
function checkShape(groups, findings) {
  const bad = (group, message) => findings.push({ group, severity: 'error', kind: 'shape', message })
  if (groups.length === 0) {
    findings.push({ group: '(file)', severity: 'warning', kind: 'shape', message: 'roster has no groups, so it asserts nothing' })
  }
  const seen = new Set()
  groups.forEach((g, i) => {
    const named = g && typeof g.group === 'string' && g.group.trim()
    const label = named ? g.group : `(index ${i})`
    if (!g || typeof g !== 'object' || Array.isArray(g)) {
      bad(label, 'group entry is not an object')
      return
    }
    if (!named) {
      bad(label, '`group` is missing or is not a non-empty string')
    } else if (seen.has(g.group)) {
      bad(label, 'duplicate group id; an `after` edge and a resume both become ambiguous')
    } else {
      seen.add(g.group)
    }
    if (typeof g.brief !== 'string' || !g.brief.trim()) {
      bad(label, '`brief` is missing or is not a non-empty string, so no citation in it can be checked')
    }
    if (!g.resume || typeof g.resume !== 'object' || Array.isArray(g.resume)) {
      bad(label, '`resume` is missing or is not an object; the lane cannot be picked up cold without one')
    } else if (typeof g.resume.stage !== 'string' || !g.resume.stage.trim()) {
      bad(label, '`resume.stage` is missing or is not a non-empty string')
    }
    // lintAfterEdges skips a non-array `after` rather than walking its
    // characters, so without this a string here would pass in silence.
    if (g.after !== undefined && !Array.isArray(g.after)) {
      bad(label, '`after` is present but is not an array')
    }
  })
}

// ---------------------------------------------------------------------------
// driver

// `shape` is off for the acceptance fixture only -- see checkShape's note.
function lintFile(file, { shape = true } = {}) {
  const findings = []
  let data
  try {
    data = JSON.parse(fs.readFileSync(file, 'utf8'))
  } catch (e) {
    findings.push({ group: '(file)', severity: 'error', kind: 'shape', message: `could not be read as JSON: ${e.message}` })
    return findings
  }
  if (!data || typeof data !== 'object' || !Array.isArray(data.groups)) {
    findings.push({ group: '(file)', severity: 'error', kind: 'shape', message: '`groups` is missing or is not an array' })
    return findings
  }
  if (shape) checkShape(data.groups, findings)
  lintAfterEdges(data.groups, findings)
  for (const g of data.groups) {
    if (!g || typeof g !== 'object') continue
    if (g.resume?.stage === STAGE_SKIP) continue // merged work; brief will not be read again
    if (typeof g.brief !== 'string' || !g.brief.trim()) continue // absence already reported
    lintBrief(typeof g.group === 'string' ? g.group : '(unnamed)', g.brief, findings)
  }
  return findings
}

// Every lint of a roster goes through here. An unexpected throw becomes that
// roster's own error instead of aborting the run, which before #582 took every
// later roster's findings and the acceptances below down with it.
//
// `lint` is injected by assertDriverGuard and by nothing else. checkShape and
// lintFile's own field guards closed every throw a roster can now stage, so
// what is left for this to catch comes from underneath -- `git ls-files`
// refusing, tests/structure_budgets.json unparseable -- and no committed
// fixture can produce that. Measured at aea7f86: with nothing driving it,
// deleting this try/catch left the whole no-arg run byte-identical at rc=0.
function lintFileGuarded(file, opts, lint = lintFile) {
  try {
    return lint(file, opts)
  } catch (e) {
    return [{ group: '(file)', severity: 'error', kind: 'shape', message: `lint aborted: ${e.message}` }]
  }
}

function printReport(file, findings) {
  const errors = findings.filter((f) => f.severity === 'error')
  const warnings = findings.filter((f) => f.severity === 'warning')
  console.log(`\n== ${file} ==`)
  for (const f of findings) {
    console.log(`  ${f.severity.toUpperCase().padEnd(7)} [${f.group}] ${f.kind}: ${f.message}`)
  }
  console.log(`  -- ${errors.length} error(s), ${warnings.length} warning(s)`)
  return errors.length
}

// ---------------------------------------------------------------------------
// acceptances
//
// A frozen input, plus the errors it must still produce. A rule with no such
// list is deletable in silence, because this job's only signal is what the
// rules report and a deleted rule reports nothing.

// #411 acceptance at 931dffe: the four half-II groups named in the issue.
// min_ink_gap is not pinned: a later doc (#417 `.cursor/rules`) names it,
// so the symbol check goes quiet on a merge even though lintBrief is live.
// The nine below still go missing if lintBrief is deleted.
const REQUIRED_931DFFE = [
  { group: 'W1-G8', kind: 'metric', needle: 'coordinator_loc' },
  { group: 'W1-G8', kind: 'metric', needle: 'methods 255' },
  { group: 'W1-G8', kind: 'metric', needle: 'attrs 176' },
  { group: 'W1-G13', kind: 'path', needle: 'card_geometry.mjs' },
  { group: 'W1-G14', kind: 'path:line', needle: 'entities.py:6042-6062' },
  { group: 'W1-G14', kind: 'version', needle: '6.3.9' },
  { group: 'W1-G9', kind: 'path', needle: 'model_sanity.py' },
  { group: 'W1-G9', kind: 'path:line (anchored)', needle: 'wood_share:1152' },
  { group: 'W1-G9', kind: 'symbol', needle: 'wood_share_vec_parity' },
]

// checkShape acceptance: fixtures/shape-defects.json holds one group per rule,
// so a deleted rule surfaces as its own missing pin rather than as a count that
// moved. `no-resume` carries a rotted citation as well as its missing field,
// which pins the property the first draft of checkShape broke -- it reports
// beside lintBrief and never gates it. `edge-probe` pins lintAfterEdges still
// running alongside. The fixture is linted with shape ON; wave-1b-931dffe.json
// is the one linted with it off, for the reason checkShape's note gives.
const REQUIRED_SHAPE_DEFECTS = [
  { group: '(index 0)', kind: 'shape', needle: 'group entry is not an object' },
  { group: '(index 1)', kind: 'shape', needle: '`group` is missing or is not a non-empty string' },
  { group: 'no-brief', kind: 'shape', needle: '`brief` is missing or is not a non-empty string' },
  { group: 'no-resume', kind: 'shape', needle: '`resume` is missing or is not an object' },
  { group: 'no-resume', kind: 'path', needle: 'no_such_probe_file.py' },
  { group: 'no-stage', kind: 'shape', needle: '`resume.stage` is missing or is not a non-empty string' },
  { group: 'after-not-array', kind: 'shape', needle: '`after` is present but is not an array' },
  { group: 'twin', kind: 'shape', needle: 'duplicate group id' },
  { group: 'edge-probe', kind: 'after', needle: "'no-such-group' names no group in this file" },
]

function assertAcceptanceFixture(name, label, opts, required) {
  const fixture = path.join(HERE, 'fixtures', name)
  const findings = lintFileGuarded(fixture, opts)
  const errors = findings.filter((f) => f.severity === 'error')
  printReport(path.relative(ROOT, fixture), findings)
  const missing = required.filter(
    (r) => !errors.some((e) => e.group === r.group && e.kind === r.kind && e.message.includes(r.needle))
  )
  if (missing.length) {
    console.log(`\nFIXTURE VACUOUS: ${label} acceptance pins missing:`)
    for (const m of missing) console.log(`  [${m.group}] ${m.kind}: ${m.needle}`)
    return 1
  }
  console.log(`\nFIXTURE ok: ${errors.length} error(s) pin the ${label} acceptance (${required.length} required)`)
  return 0
}

// SYMBOL_GREP_EXCLUDE, bounded by the tree in both directions. The ceiling
// refuses an entry that names nothing, which is the dead weight the archive
// created and nothing caught. The floor refuses the deletion of an entry the
// check needs to mean anything, which is the failure the ceiling cannot see:
// an empty list passes every "names nothing" test there is.
function assertGrepExcludeBounded() {
  const tracked = git(['ls-files']).split('\n').filter(Boolean)
  const dead = SYMBOL_GREP_EXCLUDE.filter((e) => {
    const prefix = e.replace(/^:!/, '')
    return !tracked.some((f) => f === prefix || f.startsWith(prefix.endsWith('/') ? prefix : prefix + '/'))
  })
  if (dead.length) {
    console.log(`\nEXCLUDE VACUOUS: ${JSON.stringify(dead)} in SYMBOL_GREP_EXCLUDE match no tracked file. An exclusion that names nothing is a destination waiting to be used: a file written there later is invisible to symbolInTree with no diff to this file.`)
    return 1
  }
  const missing = SYMBOL_GREP_EXCLUDE_FLOOR.filter((e) => !SYMBOL_GREP_EXCLUDE.includes(e))
  if (missing.length) {
    console.log(`\nEXCLUDE VACUOUS: SYMBOL_GREP_EXCLUDE has lost ${JSON.stringify(missing)}. Without it a symbol resolves against the rosters that cite it, so the citation proves itself.`)
    return 1
  }
  console.log(`\nEXCLUDE ok: ${SYMBOL_GREP_EXCLUDE.length} symbol-search exclusion(s), each naming a prefix the tree has, none of the load-bearing ones dropped`)
  return 0
}

const GUARD_PROBE = 'driver-guard acceptance probe'

// Driver-guard acceptance. No committed roster can throw any more, so the only
// honest pin is to hand the guard a lint that does: what is being asserted is
// that one roster's failure comes back as that roster's error, leaving the
// loop and the fixtures above to finish.
function assertDriverGuard() {
  const thrower = () => {
    throw new TypeError(GUARD_PROBE)
  }
  let findings
  try {
    findings = lintFileGuarded('(driver-guard probe)', {}, thrower)
  } catch (e) {
    console.log(`\nGUARD VACUOUS: a throw escaped lintFileGuarded (${e.message}); one bad roster would abort the run`)
    return 1
  }
  if (!findings.some((f) => f.severity === 'error' && f.message.includes(GUARD_PROBE))) {
    console.log('\nGUARD VACUOUS: lintFileGuarded swallowed a throw instead of reporting it')
    return 1
  }
  console.log("\nGUARD ok: an unexpected throw is reported as that roster's own error")
  return 0
}

function main() {
  const args = process.argv.slice(2)
  const defaultRun = args.length === 0
  const files = defaultRun
    ? fs
        .readdirSync(path.join(ROOT, '.claude', 'workflows'))
        .filter((f) => /^wave-.*-groups\.json$/.test(f))
        .map((f) => path.join(ROOT, '.claude', 'workflows', f))
        .sort()
    : args

  let totalErrors = 0
  for (const f of files) {
    totalErrors += printReport(path.relative(ROOT, f), lintFileGuarded(f))
  }
  console.log(`\nTOTAL: ${totalErrors} error(s) across ${files.length} file(s)`)
  // Summed rather than short-circuited: a run that fails one acceptance still
  // reports the other two, so a report names every rule that stopped holding.
  let acceptanceRc = 0
  if (defaultRun) {
    acceptanceRc += assertAcceptanceFixture('wave-1b-931dffe.json', '931dffe', { shape: false }, REQUIRED_931DFFE)
    acceptanceRc += assertAcceptanceFixture('shape-defects.json', 'shape-defects', {}, REQUIRED_SHAPE_DEFECTS)
    acceptanceRc += assertDriverGuard()
    acceptanceRc += assertGrepExcludeBounded()
  }
  process.exit(totalErrors > 0 || acceptanceRc ? 1 : 0)
}

// Import-safe: the CLI path runs only when this file IS the entry point, so
// policy_lint.mjs can reuse the resolvers above without running the linter.
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main()
}
