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
