// Derived counts, shared by the two linters that check a stated figure against
// the artefact that answers it (issue #581).
//
// WHY ITS OWN FILE. policy_lint.mjs already imports resolvers from
// brief_lint.mjs, so brief_lint cannot import back from policy_lint without a
// cycle -- and in a cycle the importer evaluates against bindings that are
// still in their temporal dead zone, so `COUNT_RULES.filter(...)` at module
// scope throws. A third module both import is the shape that has no cycle to
// get wrong. It deliberately depends on neither linter: the six lines of `read`
// and `git` below are its own so that the dependency arrow never turns around.
//
// One enumeration, two callers, each with its own genre guard. COUNT_RULES is
// calibrated for POLICY prose; brief_lint takes a measured subset of it,
// because a roster brief uses some of the same words for a subset rather than
// for the tree -- see BRIEF_COUNT_KEYS there for the measurement.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')

function read(rel) {
  try {
    return fs.readFileSync(path.join(ROOT, rel), 'utf8')
  } catch {
    return null
  }
}

function git(args) {
  return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
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

export function derivations() {
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
  const pb = read('.claude/workflows/policy_budgets.json')
  d.caps = pb ? JSON.parse(pb).files : null
  return d
}

// Number words the corpus actually uses, so "fourteen of sixteen" is checked.
export const WORDS = {
  two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
  eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16,
  seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20, 'twenty-one': 21,
  'twenty-two': 22, 'twenty-three': 23, 'twenty-four': 24,
}
const NUM = `(\\d+|${Object.keys(WORDS).join('|')})`
export function toNum(tok) {
  return /^\d+$/.test(tok) ? Number(tok) : WORDS[tok.toLowerCase()]
}

// A cap stated in prose beside the name of the file it caps. Resolved, never
// guessed, which is the property that keeps every rule here at zero false
// positives: the file must name a key of policy_budgets.json by unique suffix,
// the number must sit against the word `cap` or carry a line unit, and an
// issue number is never read as one: wherever the number follows the cap word
// or the glue, the engine arrives at the `#` and the digit class fails there,
// and the one number-first form, "N-line cap", carries its own `#` lookbehind.
// An earlier draft guarded every position with a lookbehind; once the glue
// below became required it decided nothing in the number-after positions, its
// mutation arm went green, and it was removed there rather than kept as
// protection that protects nothing. "from X to Y" is the arrow written in
// prose, so `to` is accepted as an arrow and the claim is Y; a draft that read
// X reported a true raise as stale, which review round 3 found. Three shapes,
// because the file name can sit before the cap, after it, or between the cap
// and its number.
//
// Built from the one class that blocked every review round of #675, in the
// exact shapes those rounds found: "raised the cap for docs/HANDOVER.md: 273 ->
// 376", "375 lines exceeds its cap of 273", "against a cap of 257" -- and in the
// second of those it is the "cap of 273" that is read, never the "375 lines": a
// number followed by "lines" is the file's length, and a draft that read it as
// the cap reported a true sentence as stale, which review round 2 found. The
// number-first form that survives is "406-line cap", where the number IS the
// cap. Measured
// before it was wired: over the corpus, both disposition documents and all 59
// roster briefs at 0b66857 it reports nothing, because the one cap the tree
// states -- fixer.md's, in a plan row -- is correct; with that cap moved to 999
// in the caps map the row is reported, and nothing else is. Every
// number it reads sits against a cap word or against required glue after the
// file name -- never merely NEAR the name, which is how an earlier draft of the
// third shape read a date and a line count as caps. A "273 -> 384" with no cap
// word beside it is not caught, and is not meant to be: that is the shape
// writing-for-agents.md forbids outright. Limits: one line at a time, so a cap
// and its file name split across a wrap are not read, which the HISTORY guard
// shares; and a figure the corpus writes as a bare number beside a file name is
// #581's territory, refused there on a measurement.
const CAP_PATH = String.raw`\`?([A-Za-z0-9_./-]+\.md)\`?`
const CAP_NUM = String.raw`(?<![\w.])(\d{2,5})(?![\w%]|\.\d)`
const CAP_WORD = String.raw`\bcap(?:ped|s)?\b`
const CAP_AT = `(?:${CAP_WORD}(?:\\s*[:=]|\\s+(?:of|at|is|was|to|from))?\\s*\\(?(?:\\*\\*)?${CAP_NUM}\\)?(?:\\s*(?:->|→|to)\\s*${CAP_NUM})?|(?<!#)${CAP_NUM}[-\\s]line\\s+cap\\b)`
const CAP_RES = [
  new RegExp(`${CAP_PATH}[^\\n]{0,80}?${CAP_AT}`, 'g'),
  new RegExp(`${CAP_AT}[^\\n]{0,80}?${CAP_PATH}`, 'g'),
  new RegExp(`${CAP_WORD}[^\\n]{0,40}?${CAP_PATH}\\s*(?:[:=]|->|→|\\b(?:at|of|to|is|was)\\b)\\s*(?:\\*\\*)?${CAP_NUM}(?:\\s*(?:->|→|to)\\s*${CAP_NUM})?`, 'g'),
]
// The last number is the claim: in "273 -> 376" the cap being asserted is 376.
function parseCap(m, caps) {
  const groups = m.slice(1).filter((x) => x !== undefined)
  const p = groups.find((x) => /\.md$/.test(x))
  const nums = groups.filter((x) => /^\d+$/.test(x))
  if (!p || !nums.length) return null
  const cand = Object.keys(caps).filter((k) => k === p || k.endsWith('/' + p))
  if (cand.length !== 1) return null
  return { tok: nums[nums.length - 1], want: caps[cand[0]], what: `the cap on ${cand[0]} in .claude/workflows/policy_budgets.json` }
}

// Each rule: a regex whose first group is the stated count, and the derivation
// key it must equal. A rule may instead carry `res` (several regexes) and a
// `parse(match, derivation)` that resolves the claim itself, returning null
// where the sentence resolves to nothing. Deliberately narrow -- a rule that over-fires gets the
// linter bypassed, which is the failure mode this whole script exists to stop.
export const COUNT_RULES = [
  { key: 'budgets', re: new RegExp(`${NUM}\\s+(?:budgets|metrics)\\b`, 'gi'), what: 'metrics in tests/structure_budgets.json' },
  { key: 'scripts', re: new RegExp(`(?:of|all)\\s+${NUM}\\s+scripts?\\b`, 'gi'), what: 'selectable scripts in tests/closures.json' },
  { key: 'rules', re: new RegExp(`${NUM}\\s+(?:\`?alwaysApply\`?\\s+)?policies\\b`, 'gi'), what: '.cursor/rules/*.mdc files' },
  { key: 'states', re: new RegExp(`(?:STATES\\s*\\(${NUM}\\)|card's\\s+${NUM}\\s+states)\\b`, 'gi'), what: 'entries in card_drift.mjs STATES' },
  { key: 'services', re: new RegExp(`${NUM}\\s+services\\b`, 'gi'), what: 'keys in services.yaml' },
  { key: 'modules', re: new RegExp(`${NUM}\\s+modules\\b`, 'gi'), what: 'modules in custom_components/heatpump_optimizer/' },
  { key: 'goldens', re: new RegExp(`${NUM}\\s+GOLDEN\\s+SCENARIOS\\b|${NUM}\\s+golden\\s+fixtures\\b`, 'g'), what: 'fixtures in tests/golden/' },
  { key: 'briefs', re: new RegExp(`${NUM}\\s+dimension\\s+briefs\\b`, 'gi'), what: 'tools/audit/briefs/D*.md' },
  { key: 'caps', res: CAP_RES, parse: parseCap, what: 'a cap in .claude/workflows/policy_budgets.json' },
]

// A count inside a quotation, an example, or a passage the file itself marks
// as history is a record of what was once measured, not a live claim.
export const HISTORY_LINE = /^\s*(?:>|\|?\s*BORN:|EXAMPLE|#{1,6}\s|.*\b(?:once|used to|at the time|was then|historical|superseded)\b)/i

// ---------------------------------------------------------------------------
// The live required-context set (#957). Three assertion sites -- a governance.yml
// comment, the plan's CLOSED block, a decision-record status note -- each stated
// a required-context count the live ruleset no longer returned, and nothing in
// the tree could notice: the counts above derive from TREE artifacts, and the
// ruleset lives on the other side of an API call. This instrument derives the
// live set instead and polices two things against it: the corpus's literals
// (a stated count must equal the live count) and a recorded-shape FIXTURE (the
// committed list must equal the live list, name by name, so the next ruleset
// change reddens the tree within one push).
//
// THE DERIVATION READS BOTH SURFACES, never the branch endpoint alone: the
// D11 brief's warning is that `rules/branches/main` is not bypass-aware -- it
// merges the applicable view but says nothing about who the rule does not bind.
// The ruleset OBJECT is the authoritative definition. The two are required to
// AGREE on the context list; a disagreement is a topology this instrument
// refuses to interpret, and it skips (loudly) rather than guessing which view
// is the truth. Two `gh api` calls, memoized per process: about a second. What
// it RETURNS carries the ruleset's shape beside the contexts -- each rule's
// type, each bypass actor's mode -- because a rule or a bypass entry that
// changes without moving a context is still a change to what the merge boundary
// does (#1192).
//
// WHY A FETCH FAILURE IS A SKIP AND NOT A RED. `policy-docs` -- the job this
// runs in -- is itself a required context, so an unreachable or rate-limited
// API reddening this class would block every merge in the repository on a
// transient outage nobody's change caused. The failure mode is recorded here
// so the next reader does not "fix" it into fail-closed: unreachable means
// UNCHECKED, and the skip line says so, which is the difference between an
// open defect and a closed one. The acceptance pins the skip both ways: a
// null fetch produces no finding AND the line that says why.

let _liveRequiredContexts
let _liveRequiredContextsWhy = 'not asked yet'
export function liveRequiredContextsWhy() {
  return _liveRequiredContextsWhy
}

// WHERE TO ASK is the fixture's `branch_endpoint`, never the clone's own
// remote: the environment matrix builds synthetic clones whose origin is a
// LOCAL PATH, and a fork's origin names a different repository than the one
// the corpus's claims are about. The recorded shape names the repository the
// assertions cite; the ANSWER still comes from the API, never from the
// fixture -- recording where to ask is not recording what it said.
export function liveRequiredContexts() {
  if (_liveRequiredContexts !== undefined) return _liveRequiredContexts
  _liveRequiredContexts = null
  try {
    const fixture = JSON.parse(read('.claude/workflows/fixtures/required-contexts.json'))
    const base = (fixture && fixture.branch_endpoint || '').replace(/\/rules\/branches\/main$/, '')
    if (!/^repos\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(base)) {
      _liveRequiredContextsWhy = 'the recorded shape names no branch_endpoint to ask'
      return null
    }
    // Surface 1: the merged branch view.
    const branch = JSON.parse(execFileSync('gh', ['api', `${base}/rules/branches/main`], { encoding: 'utf8' }))
    const ids = new Set()
    const viaBranch = new Set()
    for (const r of branch) {
      if (r.type !== 'required_status_checks') continue
      if (r.ruleset_id != null) ids.add(r.ruleset_id)
      for (const c of (r.parameters && r.parameters.required_status_checks) || []) viaBranch.add(c.context)
    }
    // Surface 2: each contributing ruleset object, read itself. The CONTEXTS
    // are what the drift comparison reads, but the reader carries the ruleset's
    // SHAPE too -- every rule's type, every bypass actor's mode -- because a
    // reader that returned the context list alone gave BYTE-IDENTICAL output for
    // two rulesets differing in a `pull_request` rule and a bypass actor
    // (#1192, D11-02): a change to the ruleset the merge boundary runs was
    // invisible to the tree's only reader of it. The shape is what makes the
    // next such change visible, whether or not anything compares it yet.
    const viaRulesets = new Set()
    const shapes = []
    for (const id of ids) {
      const rs = JSON.parse(execFileSync('gh', ['api', `${base}/rulesets/${id}`], { encoding: 'utf8' }))
      shapes.push({ id, rules: (rs.rules || []).map((r) => r.type),
                    bypass: (rs.bypass_actors || []).map((a) => a.bypass_mode) })
      for (const rule of rs.rules || []) {
        if (rule.type !== 'required_status_checks') continue
        for (const c of (rule.parameters && rule.parameters.required_status_checks) || []) viaRulesets.add(c.context)
      }
    }
    const a = [...viaBranch].sort()
    const b = [...viaRulesets].sort()
    if (a.join('\n') !== b.join('\n')) {
      _liveRequiredContextsWhy = 'the branch endpoint and the ruleset objects disagree on the context list'
      return null
    }
    _liveRequiredContextsWhy = ''
    return { contexts: a, count: a.length, rulesets: [...ids].sort((x, y) => x - y), shapes }
  } catch (e) {
    _liveRequiredContextsWhy = `the fixture or the API failed: ${String((e && e.status) || (e && e.message) || e).split('\n')[0].slice(0, 100)}`
    return null
  }
}

// The literal shapes the assertion sites use. Deliberately narrower than "N
// required checks": "#656 read BLOCKED on two required checks still running"
// counts CHECKS AT A MOMENT, not the set's size, and would be a false refusal.
// "16-of-16 required checks" (a dated row) is not matched by any shape here --
// the number sits behind "of-", and no shape admits it.
export const REQUIRED_CONTEXT_RES = [
  new RegExp(`${NUM}\\s+required\\s+status\\s+checks\\b`, 'gi'),
  new RegExp(`${NUM}\\s+required\\s+contexts\\b`, 'gi'),
  new RegExp(`${NUM}-context\\s+required\\s+set\\b`, 'gi'),
]

// History guard for the SITE scan -- deliberately not counts.mjs's
// HISTORY_LINE: a decision record's status note is a blockquote (`>`) and is
// exactly the live claim this class exists to read. What IS history here is
// the plan's per-merge record furniture: Delivery-status TABLE rows (`| ...`)
// and per-PR rows (`- [#NNN] ...`), each dated by construction.
export const REQUIRED_CONTEXT_HISTORY = /^\s*(?:\||-\s*\[#\d+\])/

export function checkRequiredContexts(rel, text, live) {
  if (text == null || live == null) return []
  const out = []
  text.split('\n').forEach((line, i) => {
    if (REQUIRED_CONTEXT_HISTORY.test(line)) return
    for (const re of REQUIRED_CONTEXT_RES) {
      re.lastIndex = 0
      let m
      while ((m = re.exec(line))) {
        const got = toNum(m[1])
        if (got == null || got === live.count) continue
        out.push({
          severity: 'error',
          check: 'required-contexts',
          where: `${rel}:${i + 1}`,
          message: `states ${m[1]} for the required-context set; the live ruleset returns ${live.count}. State the rule, never a count -- "the required checks its endpoint returns" needs no number and cannot go stale.`,
        })
      }
    }
  })
  return out
}

// The recorded-shape fixture against the live list, name by name: a COUNT
// alone would pass a ruleset change that swapped one context for another, and
// the two reds below are what make the next ruleset change visible within one
// push. Red here means re-record the fixture BY HAND from the API (both
// surfaces, as above) and re-read every assertion site against the new list.
export function requiredContextsDrift(fixtureRel, fixture, live) {
  if (fixture == null || live == null) return []
  const out = []
  const recorded = new Set(fixture.contexts || [])
  for (const c of live.contexts) {
    if (recorded.has(c)) continue
    out.push({
      severity: 'error',
      check: 'required-contexts',
      where: fixtureRel,
      message: `the live required-context set has \`${c}\`, which the recorded shape lacks. The ruleset changed: re-record ${fixtureRel} from the API and re-read every assertion site against the new list.`,
    })
  }
  for (const c of recorded) {
    if (live.contexts.includes(c)) continue
    out.push({
      severity: 'error',
      check: 'required-contexts',
      where: fixtureRel,
      message: `\`${c}\` is recorded as a required context but the live set no longer returns it. The ruleset changed: re-record ${fixtureRel} and re-read every assertion site against the new list.`,
    })
  }
  return out
}

export function checkCounts(rel, text, derived) {
  const out = []
  const lines = text.split('\n')
  lines.forEach((line, i) => {
    if (HISTORY_LINE.test(line)) return
    for (const rule of COUNT_RULES) {
      const derivation = derived[rule.key]
      if (derivation == null) continue
      for (const re of rule.res ?? [rule.re]) {
        re.lastIndex = 0
        let m
        while ((m = re.exec(line))) {
          const r = rule.parse ? rule.parse(m, derivation) : { tok: m[1] || m[2], want: derivation, what: rule.what }
          if (!r || !r.tok) continue
          const got = toNum(r.tok)
          if (got == null || got === r.want) continue
          out.push({
            severity: 'error',
            check: 'counts',
            where: `${rel}:${i + 1}`,
            message: `states ${r.tok} for ${r.what}; derived ${r.want}. Derive the count, do not carry one.`,
          })
        }
      }
    }
  })
  return out
}
