#!/usr/bin/env node
// Can a check be emptied without the acceptance noticing?
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
//
// TWO LANES, TWO ENUMERATIONS (#683). The paragraph above was written when the
// only enumeration was `CORPUS_CHECK_NAMES`. The RECORD mode has since grown
// four outputs of its own -- `RECORD:` (`checkRecord`), `TABLES:`
// (`checkTableSplit`), `CAPS:` (the `caps` rule of `checkCounts`, over both
// disposition documents) and `RENDER:` (`checkRender`) -- each driven by a fixture under
// fixtures/policy-loop/ inside the same acceptance. An emptied record check is
// therefore caught THERE; that is exactly the position the corpus checks were
// in before this lane existed, and it was not the question. The question is
// whether the drive that is supposed to catch it is the drive that runs, and no
// assertion inside the acceptance can answer that about itself. So
// `LOOP_CHECK_NAMES` is mutated the same way, from the same production export,
// with the same three verdicts and the same printed enumeration.
//
// The `caps` rule gets TWO ARMS, because the rule has two ways to go silent and
// they are not the same mutation. Emptying `checkCounts` stops all nine count
// rules at once; emptying `CAP_RES`, the regex list the `caps` rule scans,
// leaves `checkCounts` running, walking `COUNT_RULES` and reaching the `caps`
// rule -- which then scans every line with no regex and reports nothing. A
// check that still "runs" is the harder of the two to notice, which is why it
// is driven rather than argued about.
//
// ONE MORE ARM, ADDED WITH #1403 (D11-02). Every arm above -- and every drive
// inside `assertAcceptance` -- reads a RETURN VALUE in this process. The value
// the required `policy-docs` context reads is `process.exit`'s argument, one
// step further out, and no assertion in here can see it. The block below the
// null control drives the entry point as a PROCESS, at both ends, with NO
// environment override of its own: the defect it was written for was keyed on an
// override the drives themselves set, so a control carrying one would have had
// the same blind spot. Its own comment carries the rest.
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

// BOTH enumerations come from production. Copying either here, or re-deriving
// one with a regex over the source, would be the same defect one level up -- a
// lane that measures the checks it happens to know about and prints a confident
// count for the rest. A check added to `CORPUS_CHECK_NAMES` or to
// `LOOP_CHECK_NAMES` is mutated by this lane on the pull request that adds it,
// with no edit here.
import { CORPUS_CHECK_NAMES, LOOP_CHECK_NAMES } from './policy_lint.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
// `ROOT` belongs to the entry-point control below alone: it starts the entry as
// a child process, and that child must resolve its own fixtures from the
// repository the lane is measuring rather than from whatever cwd called the lane.
const ROOT = path.resolve(HERE, '..', '..')
const ENTRY = 'policy_lint.mjs'
const TARGET = path.join(HERE, ENTRY)
// Any `.<module>.mutant-<name>.mjs` beside the originals, not `policy_lint`
// alone: the record lane mutates counts.mjs too. `.gitignore` carries the same
// shape, and a mutant left behind by an aborted run is untracked in a directory
// the corpus reads, so the two must agree.
const MUTANT_RE = /^\.[A-Za-z0-9_]+\.mutant-[A-Za-z0-9_]+\.mjs$/
const mutantName = (file, name) => `.${file.replace(/\.mjs$/, '')}.mutant-${name}.mjs`

// A mutant must live beside its original: `policy_lint.mjs` resolves
// `fixtures/policy-rot/` from its own directory, so a copy written anywhere
// else reports "fixtures are missing" and goes red for a reason that has
// nothing to do with the mutation. Red for the wrong reason is not a pin. The
// same holds one module over: counts.mjs resolves the repository root from its
// own directory, so its mutant is written into this directory too.
function sweep() {
  for (const f of fs.readdirSync(HERE)) {
    if (MUTANT_RE.test(f)) fs.rmSync(path.join(HERE, f), { force: true })
  }
}

// ---------------------------------------------------------------------------
// The mutations. Each returns either `{ text }` or `{ error }`, never a
// silently unchanged source: a mutation that did not apply and one that applied
// and was caught are OPPOSITE results, and a lane that cannot tell them apart
// is the defect it was written for. Every arm below asserts its anchor rather
// than assuming it, and reports the count it actually saw.

// Empty a check's RETURN. "I could not find it" and "it is pinned" are opposite
// results, and a lane that reports the first as the second is the defect it was
// written for. A check rewritten as `const checkDuplicates = (files) => {`
// reaches CRASH here, measured; a signature merely broken across lines still
// mutates correctly, because a JS character class matches newlines and the
// argument capture spans them. `export ` is optional because counts.mjs exports
// its check at the point of definition and policy_lint.mjs does not.
function mutateReturn(src, name, file) {
  const all = src.match(new RegExp(`^(?:export )?function ${name}\\(`, 'gm')) || []
  if (all.length !== 1) {
    return { error: `the anchor \`function ${name}(\` matched ${all.length} time(s) in ${file}, expected exactly 1; nothing was mutated` }
  }
  const text = src.replace(
    new RegExp(`^((?:export )?function ${name}\\(([^)]*)\\) \\{)$`, 'm'),
    (_m, sig) => `${sig}\n  return [] // MUTANT`,
  )
  if (text === src) {
    return { error: `\`function ${name}(...)\` in ${file} is not a single-line signature ending in \`{\`, so the empty-return edit did not apply` }
  }
  return { text }
}

// Empty a rule's REGEX LIST, which is a different mutation from emptying the
// check that walks it: the check still runs, the rule is still reached, and it
// scans every line against no pattern. The anchor is the array's opening line
// and the edit runs to the first line that is exactly `]`, so a list rewritten
// onto one line reaches CRASH rather than passing unmutated.
function mutateArray(src, name, file) {
  const all = src.match(new RegExp(`^const ${name} = \\[$`, 'gm')) || []
  if (all.length !== 1) {
    return { error: `the anchor \`const ${name} = [\` matched ${all.length} time(s) in ${file}, expected exactly 1; nothing was mutated` }
  }
  const text = src.replace(new RegExp(`^const ${name} = \\[\\n[\\s\\S]*?\\n\\]$`, 'm'), `const ${name} = [] // MUTANT`)
  if (text === src) {
    return { error: `\`const ${name} = [\` in ${file} is not a multi-line array literal closed by a line of \`]\`, so the empty-list edit did not apply` }
  }
  return { text }
}

// A mutant of a module policy_lint.mjs IMPORTS is only reached if policy_lint's
// own copy points at it. This rewrite is asserted for the same reason the
// anchors above are -- but note the failure is fail-CLOSED either way: a
// specifier that silently did not move leaves the mutant importing the
// unmutated module, the acceptance passes, and the row reads `ACCEPTED`, which
// fails the lane loudly. It never reads `PIN`.
function repoint(src, file, mutant) {
  const spec = `'./${file}'`
  const n = src.split(spec).length - 1
  if (n !== 1) {
    return { error: `the import specifier ${spec} appears ${n} time(s) in ${ENTRY}, expected exactly 1; the mutant would have imported the unmutated module` }
  }
  return { text: src.replace(spec, `'./${mutant}'`) }
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

// The two enumerations, flattened into one job list so both lanes get the same
// null control, the same skip handling, the same three verdicts and the same
// printed enumeration. The corpus entries carry no file or kind of their own:
// every one of them is a function in policy_lint.mjs, which is what makes that
// enumeration a bare list of names in production.
function jobs() {
  return [
    ...CORPUS_CHECK_NAMES.map((name) => ({ lane: 'corpus', name, file: ENTRY, kind: 'return' })),
    ...LOOP_CHECK_NAMES.map((e) => ({ lane: 'record', ...e })),
  ]
}

// ---------------------------------------------------------------------------
// THE ENTRY POINT'S EXIT STATUS IS ITSELF A CHECK, AND NO ARM ABOVE DROVE IT.
//
// Every arm above -- and every drive inside `assertAcceptance` -- reads a RETURN
// VALUE in this process. The value the required `policy-docs` context reads is
// `process.exit`'s argument, one step further out: `main()` could reach the right
// finding at the right severity and still exit 0, and nothing in here would
// notice. One line at the end of `main()` decides it, and before this arm
// nothing drove that line.
//
// SO THIS CONTROL STARTS A PROCESS, against the real entry point, and reads what
// a shell reads. It passes NO override of the run's own environment --
// `spawnSync` inherits this process's, untouched -- and that clause is the
// load-bearing one. The first version of the defect was keyed on an override the
// drives themselves set: `process.exit(process.env.POLICY_LINT_TEMPLATE ? ... :
// 0)` left the template arm in `tests/entities.py`, which passes that variable,
// seeing rc 1; left the default run, this lane and the corpus lint seeing 0; and
// survived all three. A control that passed an override of its own would have
// had the same blind spot, so it must not have one.
//
// BOTH ENDS, because a constant satisfies one: an unconditional `process.exit(0)`
// fails the red arm, an unconditional `process.exit(1)` the green arm, and only a
// status that tracks the findings passes both. The red arm is a fixture under
// `fixtures/policy-rot/`, whose refusal the run itself prints -- the redness is
// the linter's finding rather than this lane's belief about it -- and the green
// arm is the default run, the shape CI executes.
//
// WHAT IT CANNOT SEE, stated rather than implied. It drives the entry point of
// THIS checkout, so a branch that edits `policy_lint.mjs` and this lane together
// is invisible to it. `governance.yml` runs this lane on the branch's own copy
// deliberately -- its verdict is about the checkers, so a lane driven from the
// base would report on neither -- and restores the checker from the base commit
// for the steps that grade the corpus, which is where that residue is answered.
const RED_ARM = path.join(ROOT, '.claude', 'workflows', 'fixtures', 'policy-rot', 'citations.md')

function driveEntry(args) {
  const r = spawnSync(process.execPath, [TARGET, ...args], {
    cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
  })
  return { status: r.status, error: r.error, said: `${r.stdout || ''}\n${r.stderr || ''}` }
}

// `{ note }` when both ends hold, `{ fail }` when one does not -- so a control
// that was never run can never print as a control that passed.
function entryExitControl() {
  const red = driveEntry([RED_ARM])
  const redLine = (red.said.split('\n').find((l) => l.trim()) || '(no output)').trim().slice(0, 140)
  if (red.error) {
    return { fail: 'MUTANTS: the entry point could not be started ' +
      `(${red.error.message}), so its exit status was NOT measured. An unmeasured control is not a ` +
      'passing one.' }
  }
  if (red.status === 0) {
    return { fail: 'MUTANTS: the entry point exited 0 on an input its own output calls red. ' +
      `${ENTRY} ends in \`process.exit(errors > 0 || rc ? 1 : 0)\`, so an exit status that does not ` +
      'track its findings -- `process.exit(0)` on that line, or any other unconditional status -- is ' +
      'the required `policy-docs` context reporting green over a corpus the same run prints as red. ' +
      `It said: ${redLine}` }
  }
  const green = driveEntry([])
  if (green.error || green.status !== 0) {
    return { fail: 'MUTANTS: the entry point exited ' +
      `${green.error ? `with ${green.error.message}` : green.status} on the corpus as it stands. ` +
      'The null control above passed in-process, so this lane does not believe the tree is red; an ' +
      'entry that refuses a healthy corpus fails every arm below for free. First refusal: ' +
      firstRefusal(green.said.split('\n')) }
  }
  return { note: `the exit status tracks the findings both ways: ${red.status} on the red fixture, ` +
    "0 on the corpus as it stands, each driven as a process with this one's environment" }
}

async function main() {
  sweep()
  const srcs = new Map()
  const sourceOf = (file) => {
    if (!srcs.has(file)) srcs.set(file, fs.readFileSync(path.join(HERE, file), 'utf8'))
    return srcs.get(file)
  }
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

  // The entry point's exit status, driven before anything is mutated. An entry
  // that cannot refuse a red input makes every arm below unfalsifiable, which is
  // the null control's own argument one step further out; the block above
  // `main()` carries why it is a process and why it passes no override.
  const entry = entryExitControl()
  if (entry.fail) { console.log(entry.fail); return 1 }
  rows.push({ lane: 'entry', name: 'exit-status', verdict: 'DRIVEN', why: entry.note })

  // A CHECK THE CLONE CANNOT EXERCISE IS NOT A CHECK THAT SURVIVED ITS DELETION.
  // In a clone with no `origin/main` the acceptance says so out loud and skips
  // its provenance drive -- and this lane then emptied `checkProvenance`, saw
  // the acceptance still pass, and reported ACCEPTED ... DELETABLE IN SILENCE,
  // rc=1. That is a FALSE failure: nothing is deletable, the environment simply
  // cannot ask. It is the same confusion the check beside it was just fixed for,
  // one level up -- "no" and "I cannot look" are different answers.
  //
  // Read from the NULL CONTROL's own output rather than from a list here, and
  // keyed on the check's own name, so a check whose drive learns to skip needs
  // no edit in this file.
  const skipped = new Set(
    control.said.flatMap((l) => {
      const m = l.match(/^\s*skip\s+(\w+)-pin\b/)
      return m ? [m[1]] : []
    }),
  )

  for (const job of jobs()) {
    const { lane, name, file, kind } = job
    if (skipped.has(name)) {
      rows.push({ lane, name, verdict: 'SKIP', why: 'the acceptance could not drive this check in this clone, so emptying it proves nothing either way' })
      continue
    }
    const m = kind === 'array' ? mutateArray(sourceOf(file), name, file) : mutateReturn(sourceOf(file), name, file)
    if (m.error) {
      rows.push({ lane, name, verdict: 'CRASH', why: m.error })
      continue
    }
    // Written, then removed in the `finally`, one at a time -- so a run that
    // dies between two jobs leaves at most one mutant, and `sweep()` removes it
    // before the next run rather than importing it.
    const written = []
    try {
      const mutant = mutantName(file, name)
      fs.writeFileSync(path.join(HERE, mutant), m.text)
      written.push(mutant)
      let imported = mutant
      if (file !== ENTRY) {
        const rp = repoint(sourceOf(ENTRY), file, mutant)
        if (rp.error) {
          rows.push({ lane, name, verdict: 'CRASH', why: rp.error })
          continue
        }
        imported = mutantName(ENTRY, name)
        fs.writeFileSync(path.join(HERE, imported), rp.text)
        written.push(imported)
      }
      const { rc, said } = await runAcceptance(pathToFileURL(path.join(HERE, imported)).href)
      if (rc !== 0) rows.push({ lane, name, verdict: 'PIN', why: firstRefusal(said) })
      else rows.push({ lane, name, verdict: 'ACCEPTED', why: 'the acceptance returned 0 with this check reporting nothing at all' })
    } catch (e) {
      // A throw is not a pin. The claim is "the acceptance refuses this
      // mutation", and an exception says the harness fell over -- which may
      // equally be a bug in this lane. Reported as its own verdict so the two
      // are never counted together.
      rows.push({ lane, name, verdict: 'CRASH', why: `the acceptance threw: ${String(e && e.message || e).split('\n')[0].slice(0, 140)}` })
    } finally {
      for (const f of written) fs.rmSync(path.join(HERE, f), { force: true })
    }
  }

  // The enumeration is printed, never a count. "5 of 5 pinned" is the shape
  // that let a check go missing from two lists at once; a reader who can see
  // the names can tell that the one they are looking for is absent. The LANE is
  // printed beside each name for the same reason one level up: a run reporting
  // eleven pins says nothing about whether any of them was a record check, and
  // the record lane going missing is the failure this pull request exists to
  // make visible.
  for (const r of rows) console.log(`  ${r.verdict.padEnd(8)} ${r.lane.padEnd(6)} ${r.name.padEnd(20)} ${r.why}`)
  // SKIP DOES NOT FAIL, and that is the whole point of separating it from
  // ACCEPTED. The clone could not ask the question; the code is not implicated,
  // and failing here fails `prepr.sh` for a seat whose remote happens to be
  // absent -- which is how this was found, after `git remote remove` in one
  // worktree stripped it for every worktree sharing the .git. It is printed on
  // its own line so an unmeasured check is never mistaken for a measured one,
  // which is the same stance `checkProvenance` takes about its own skip.
  const skips = rows.filter((r) => r.verdict === 'SKIP')
  // `DRIVEN` joins `PIN` and `SKIP` as a verdict that is not a failure: it is the
  // entry-point control's, printed in the same enumeration so a reader sees it
  // ran. Named in the filter rather than left out of it, because a verdict
  // arriving through the two that used to be here is how a lane starts reporting
  // a control it no longer has.
  const bad = rows.filter((r) => !['PIN', 'SKIP', 'DRIVEN'].includes(r.verdict))
  for (const r of skips) {
    console.log(`\nMUTANTS: \`${r.name}\` was NOT measured -- ${r.why}. An unmeasured check is not a passing one; this run does not certify it either way.`)
  }
  if (!bad.length) {
    // BOTH enumerations on the one line, because `prepr.sh` reports this
    // script's last line and a summary naming one lane would read as a clean
    // run of both. "when it is emptied", not "when its return is emptied": one
    // of the record arms empties a regex list, and the check it belongs to
    // still runs.
    const named = (lane) => rows.filter((r) => r.lane === lane && r.verdict === 'PIN').map((r) => r.name).join(', ')
    console.log(`\nMUTANTS ok: every check this clone could drive turns the acceptance red when it is emptied -- corpus [${named('corpus')}]; record [${named('record')}]${skips.length ? `; ${skips.length} not measured here` : ''}`)
    return 0
  }
  for (const r of bad) {
    if (r.verdict === 'ACCEPTED') {
      console.log(`\nMUTANTS: \`${r.name}\` is DELETABLE IN SILENCE. Emptying it changed no output the acceptance reads, so nothing in this repository would notice the check no longer measuring anything. It needs a witness driven against a state where its property is TRUE -- the property is false on a healthy corpus, which is why it has none.`)
    } else {
      console.log(`\nMUTANTS: \`${r.name}\` could not be measured -- ${r.why}. An unmeasured check is not a passing one.`)
    }
  }
  return 1
}

process.exit(await main())
