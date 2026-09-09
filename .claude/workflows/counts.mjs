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

// Each rule: a regex whose first group is the stated count, and the derivation
// key it must equal. Deliberately narrow -- a rule that over-fires gets the
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
