#!/usr/bin/env node
// Can a corpus check be emptied without the acceptance noticing?
//
// WHY THIS EXISTS. Three checks in `policy_lint.mjs` shipped measuring nothing,
// in three separate pull requests, each with an acceptance the author believed
// pinned it: `checkCoverage` (a probe that tested the GLOBS instead of the
// function), the four budget cap comparisons (a healthy corpus exceeds no cap,
// so every comparison was false and none had a witness), and `checkNamedDocs`
// (same shape, one round later). The named cause is SELF-WITNESSED PROXY
// ASSERTION: when a property is false on a healthy tree it has no natural
// witness, so the author writes down a MODEL of the check and pins the model.
// The model and the check come from the same head, so the pin confirms rather
// than tests. Every one of the three was found by an adversarial reader asking
// "what happens if I empty this", never by the harness.
//
// This lane asks that question mechanically, for every corpus check, with no
// model in between: it empties one check's return, runs the REAL acceptance,
// and demands a refusal. A check whose acceptance survives its own removal is
// reported by name, which is the finding the three defects each were.
//
// WHAT IT DOES NOT COVER, stated rather than implied. Its granularity is the
// wired entry point. Emptying `coverageOverTree` subsumes emptying
// `checkCoverage`, because the wrapper returns what the implementation returns
// -- so delegation is covered -- but a comparison INSIDE a check is not: the
// budget defect was three of four `if` arms with no witness while the fourth
// fired, and the whole function still returned findings. Sub-function
// comparisons need their own driven witness, which is what the `capClasses`
// loop in `assertAcceptance` is. This lane cannot derive that loop and does not
// claim to. It covers exactly the class where all three defects were REACHED:
// a wired check that reports nothing.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

// The enumeration comes from production. Copying it here, or re-deriving it
// with a regex over the source, would be the same defect one level up -- a lane
// that measures the checks it happens to know about and prints a confident
// count for the rest. A check added to `CORPUS_CHECK_NAMES` is mutated by this
// lane on the pull request that adds it, with no edit here.
import { CORPUS_CHECK_NAMES } from './policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const TARGET = path.join(HERE, 'policy_lint.mjs')
const MUTANT_RE = /^\.policy_lint\.mutant-.*\.mjs$/

// A mutant must live beside its original: `policy_lint.mjs` resolves
// `fixtures/policy-rot/` from its own directory, so a copy written anywhere
// else reports "fixtures are missing" and goes red for a reason that has
// nothing to do with the mutation. Red for the wrong reason is not a pin.
function sweep() {
  for (const f of fs.readdirSync(HERE)) {
    if (MUTANT_RE.test(f)) fs.rmSync(path.join(HERE, f), { force: true })
  }
}

// Silence the acceptance's own output and keep it, so a mutant that IS refused
// can be reported with the line that refused it. A lane that printed five
// copies of the whole acceptance would be unreadable, and one that printed only
// pass/fail would hide a mutant refused by an unrelated pin.
async function runAcceptance(modUrl) {
  const said = []
  const real = console.log
  console.log = (...a) => said.push(a.join(' '))
  try {
    const mod = await import(modUrl)
    const rc = mod.assertAcceptance(mod.derivations())
    return { rc, said }
  } finally {
    console.log = real
  }
}

function firstRefusal(said) {
  const line = said.find((s) => /FIXTURE (VACUOUS|OVER-FIRES)/.test(s))
  return line ? line.trim().replace(/\s+/g, ' ').slice(0, 160) : '(refused with no FIXTURE line)'
}

async function main() {
  sweep()
  const src = fs.readFileSync(TARGET, 'utf8')
  const rows = []

  // NULL CONTROL first. Every mutant below is expected to fail; that expectation
  // is worth nothing unless the unmutated module passes. A tree where the
  // acceptance is already red makes every mutant "detected" for free, which is
  // precisely the vacuous shape this lane exists to refuse -- so it is checked
  // here rather than assumed from the fact that CI ran the linter separately.
  const control = await runAcceptance(pathToFileURL(TARGET).href + '?control')
  if (control.rc !== 0) {
    console.log('MUTANTS: null control FAILED -- the unmutated acceptance returned ' +
      `${control.rc}, so no mutant below proves anything. First refusal: ${firstRefusal(control.said)}`)
    return 1
  }

  for (const name of CORPUS_CHECK_NAMES) {
    // The anchor is asserted, not assumed. "I could not find it" and "it is
    // pinned" are opposite results, and a lane that reports the first as the
    // second is the defect it was written for. A check rewritten as
    // `const checkDuplicates = (files) => {` reaches CRASH here, measured; a
    // signature merely broken across lines still mutates correctly, because
    // a JS character class matches newlines and the argument capture spans
    // them.
    const all = src.match(new RegExp(`^function ${name}\\(`, 'gm')) || []
    if (all.length !== 1) {
      rows.push({ name, verdict: 'CRASH', why: `the anchor \`function ${name}(\` matched ${all.length} time(s) in policy_lint.mjs, expected exactly 1; nothing was mutated` })
      continue
    }
    const mutated = src.replace(
      new RegExp(`^function ${name}\\(([^)]*)\\) \\{$`, 'm'),
      (_m, args) => `function ${name}(${args}) {\n  return [] // MUTANT`,
    )
    if (mutated === src) {
      rows.push({ name, verdict: 'CRASH', why: `\`function ${name}(...)\` is not a single-line signature ending in \`{\`, so the empty-return edit did not apply` })
      continue
    }
    const file = path.join(HERE, `.policy_lint.mutant-${name}.mjs`)
    fs.writeFileSync(file, mutated)
    try {
      const { rc, said } = await runAcceptance(pathToFileURL(file).href)
      if (rc !== 0) rows.push({ name, verdict: 'PIN', why: firstRefusal(said) })
      else rows.push({ name, verdict: 'ACCEPTED', why: 'the acceptance returned 0 with this check reporting nothing at all' })
    } catch (e) {
      // A throw is not a pin. The claim is "the acceptance refuses this
      // mutation", and an exception says the harness fell over -- which may
      // equally be a bug in this lane. Reported as its own verdict so the two
      // are never counted together.
      rows.push({ name, verdict: 'CRASH', why: `the acceptance threw: ${String(e && e.message || e).split('\n')[0].slice(0, 140)}` })
    } finally {
      fs.rmSync(file, { force: true })
    }
  }

  // The enumeration is printed, never a count. "5 of 5 pinned" is the shape
  // that let a check go missing from two lists at once; a reader who can see
  // the names can tell that the one they are looking for is absent.
  for (const r of rows) console.log(`  ${r.verdict.padEnd(8)} ${r.name.padEnd(20)} ${r.why}`)
  const bad = rows.filter((r) => r.verdict !== 'PIN')
  if (!bad.length) {
    console.log(`\nMUTANTS ok: every corpus check in CORPUS_CHECK_NAMES turns the acceptance red when its return is emptied [${rows.map((r) => r.name).join(', ')}]`)
    return 0
  }
  for (const r of bad) {
    if (r.verdict === 'ACCEPTED') {
      console.log(`\nMUTANTS: \`${r.name}\` is DELETABLE IN SILENCE. Emptying its return changed no output the acceptance reads, so nothing in this repository would notice the check no longer measuring anything. It needs a witness driven against a state where its property is TRUE -- the property is false on a healthy corpus, which is why it has none.`)
    } else {
      console.log(`\nMUTANTS: \`${r.name}\` could not be measured -- ${r.why}. An unmeasured check is not a passing one.`)
    }
  }
  return 1
}

process.exit(await main())
