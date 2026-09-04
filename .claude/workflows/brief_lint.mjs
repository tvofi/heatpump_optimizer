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
// Plus: every `after:` edge names a group in the same file.
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
// The no-arg (CI) path also lints fixtures/wave-1b-931dffe.json and REQUIRES
// the ten #411 acceptance errors. Deleting the lintBrief calls otherwise
// greens the job while catching nothing.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')

const CODE_EXTS = ['py', 'mjs', 'js', 'json', 'yaml', 'yml', 'md', 'sh', 'txt', 'patch', 'out']
const EXT_RE = CODE_EXTS.join('|')
const EXT_SET = new Set(CODE_EXTS)

// ---------------------------------------------------------------------------
// git plumbing -- every call reads objects already on disk; nothing fetches.

function git(args, opts = {}) {
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
function trackedFiles() {
  if (_trackedFiles) return _trackedFiles
  const out = git(['ls-files'])
  const list = out.split('\n').filter(Boolean)
  _trackedFiles = { set: new Set(list), byBase: basenameMap(list), list }
  return _trackedFiles
}

const _refResolveCache = new Map()
function refResolves(ref) {
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

function resolvePathToken(token) {
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

// Two directories are excluded from "does this symbol exist anywhere":
//   .claude/            -- every wave-*-groups.json brief IS the text this
//                          script is scanning, so a symbol it names would
//                          otherwise "exist" by matching its own citation.
//   tools/audit/round2/ -- write-once evidence FROM the tag, committed as
//                          prose about a finding, not resolvable current
//                          state (it is on INERT for exactly this reason).
//                          A symbol mentioned only there is the class-2
//                          "lives at the tag, not in the tree" case, and
//                          searching it would pass the check on the strength
//                          of the report describing the rot, not the rot
//                          being fixed.
const SYMBOL_GREP_EXCLUDE = [':!.claude', ':!tools/audit/round2']

function symbolInTree(symbol) {
  const out = git(['grep', '-I', '-l', '-w', '-F', symbol, '--', '.', ...SYMBOL_GREP_EXCLUDE], { allowFail: true })
  return !!(out && out.trim())
}

const _fileLinesCache = new Map()
function fileLines(relPath) {
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

function tagRefsIn(text) {
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
function checkAgainstTags(refs, checkFn) {
  if (refs.length === 0) return { status: 'none' }
  let sawResolvable = false
  for (const ref of refs) {
    const r = checkFn(ref)
    if (r === true) return { status: 'ok', ref }
    if (r === false) sawResolvable = true
  }
  return sawResolvable ? { status: 'error' } : { status: 'warn' }
}

function reportUnresolvedPath(add, kind, label, token, tagResult, refs) {
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

const SNAKE_RE = /\b_*[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g
const SCREAM_RE = /\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g
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

function symbolCandidates(text) {
  const out = new Set()
  for (const m of text.matchAll(SNAKE_RE)) out.add(m[0])
  for (const m of text.matchAll(SCREAM_RE)) out.add(m[0])
  return [...out]
}

function dottedCandidates(text) {
  const out = []
  for (const m of text.matchAll(DOTTED_RE)) {
    if (EXT_SET.has(m[2])) continue // "card_geometry.mjs" is a path, not module.symbol
    out.push({ module: m[1], symbol: m[2], full: m[0] })
  }
  return out
}

function quotedPhrases(text) {
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

function resolveModuleFile(moduleName) {
  const { byBase } = trackedFiles()
  for (const ext of ['py', 'mjs', 'js']) {
    const cands = byBase.get(`${moduleName}.${ext}`)
    if (cands && cands.length) return cands[0]
  }
  return null
}

// ---------------------------------------------------------------------------
// class 1 + 2 path tokens

const PATH_TOKEN_RE = new RegExp(
  `\\b(?:[A-Za-z0-9_][A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\\.(?:${EXT_RE})\\b`,
  'g'
)
const PATHLINE_RE = new RegExp(
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
const NEGATION_RE = /\b(?:do not go looking for|must not exist|should not exist|never existed|does not exist|whose source is (?:only )?in)\s*$/i

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

function checkPathLine(relPath, start, end, context, excludeStems, exact) {
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
function budgets() {
  if (_budgets) return _budgets
  _budgets = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests', 'structure_budgets.json'), 'utf8'))
  return _budgets
}

function resolveMetricName(word) {
  const b = budgets()
  if (word in b) return word
  const suffix = `_${word}`
  const hits = Object.keys(b).filter((k) => k.endsWith(suffix))
  if (hits.length === 0) return null
  hits.sort((a, c) => a.length - c.length) // shortest match wins a suffix tie
  return hits[0]
}

// `word NUMBER <comparator> NUMBER` -- the literal-figure shape #411 names.
const METRIC_LITERAL_RE = /\b([a-z][a-z_]{2,})\s+(\d+(?:\.\d+)?)\s*(<=|>=|==|<|>)\s*(\d+(?:\.\d+)?)\b/g

// ---------------------------------------------------------------------------
// class 3-narrow: VERSION drift. Checked against the live root VERSION file
// (not flagged unconditionally like a budget), because the brief is
// asserting the current release, not instructing a re-measurement.

let _liveVersion
function liveVersion() {
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
  const names = new Set(groups.map((g) => g.group))
  for (const g of groups) {
    for (const dep of g.after ?? []) {
      if (!names.has(dep)) {
        findings.push({ group: g.group, severity: 'error', kind: 'after', message: `after: '${dep}' names no group in this file` })
      }
    }
  }
}

// ---------------------------------------------------------------------------
// driver

function lintFile(file) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8'))
  const findings = []
  lintAfterEdges(data.groups, findings)
  for (const g of data.groups) {
    if (g.resume?.stage === 'done') continue // merged work; brief will not be read again
    lintBrief(g.group, g.brief, findings)
  }
  return findings
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

// #411 acceptance at 931dffe: the four half-II groups named in the issue,
// plus min_ink_gap (outside the freshness table). A gutted lintBrief makes
// this list miss and the no-arg path exit 1.
const REQUIRED_931DFFE = [
  { group: 'W1-G8', kind: 'metric', needle: 'coordinator_loc' },
  { group: 'W1-G8', kind: 'metric', needle: 'methods 255' },
  { group: 'W1-G8', kind: 'metric', needle: 'attrs 176' },
  { group: 'W1-G13', kind: 'path', needle: 'card_geometry.mjs' },
  { group: 'W1-G13', kind: 'symbol', needle: 'min_ink_gap' },
  { group: 'W1-G14', kind: 'path:line', needle: 'entities.py:6042-6062' },
  { group: 'W1-G14', kind: 'version', needle: '6.3.9' },
  { group: 'W1-G9', kind: 'path', needle: 'model_sanity.py' },
  { group: 'W1-G9', kind: 'path:line (anchored)', needle: 'wood_share:1152' },
  { group: 'W1-G9', kind: 'symbol', needle: 'wood_share_vec_parity' },
]

function assertAcceptanceFixture() {
  const fixture = path.join(HERE, 'fixtures', 'wave-1b-931dffe.json')
  const findings = lintFile(fixture)
  const errors = findings.filter((f) => f.severity === 'error')
  printReport(path.relative(ROOT, fixture), findings)
  const missing = REQUIRED_931DFFE.filter(
    (r) => !errors.some((e) => e.group === r.group && e.kind === r.kind && e.message.includes(r.needle))
  )
  if (missing.length) {
    console.log('\nFIXTURE VACUOUS: 931dffe acceptance pins missing:')
    for (const m of missing) console.log(`  [${m.group}] ${m.kind}: ${m.needle}`)
    return 1
  }
  console.log(`\nFIXTURE ok: ${errors.length} error(s) pin the 931dffe acceptance (${REQUIRED_931DFFE.length} required)`)
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
    const findings = lintFile(f)
    totalErrors += printReport(path.relative(ROOT, f), findings)
  }
  console.log(`\nTOTAL: ${totalErrors} error(s) across ${files.length} file(s)`)
  const fixtureRc = defaultRun ? assertAcceptanceFixture() : 0
  process.exit(totalErrors > 0 || fixtureRc ? 1 : 0)
}

main()
