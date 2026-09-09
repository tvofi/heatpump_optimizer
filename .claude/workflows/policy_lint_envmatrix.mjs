
// Declared-environment matrix for the governance lanes.
//
// The class it detects: an assertion whose reachability depends on an
// environment fact, where the run does not disclose that it did not run.
// Each row DECLARES what the shape must produce; a row whose run does not
// produce it fails. A shape that could not be built fails too -- a matrix that
// silently ran three of four rows is the defect it was written for.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

const SRC = process.argv[2]
const WORK = process.argv[3]
const SHA = process.argv[4] || 'HEAD'

const sh = (cmd, args, opts = {}) => {
  try {
    return { rc: 0, out: execFileSync(cmd, args, { encoding: 'utf8', stdio: ['ignore','pipe','pipe'], ...opts }) }
  } catch (e) { return { rc: e.status ?? 1, out: (e.stdout || '') + (e.stderr || '') } }
}
const git = (dir, args) => sh('git', ['-C', dir, ...args])

// What this run actually built, recorded HERE rather than read off the disk
// afterwards. `fs.existsSync(WORK/<name>/.git)` was the earlier test, and it
// answers a question about the filesystem, not about this run: delete a shape's
// `build(...)` call and its directory from the PREVIOUS run still satisfies it,
// so the matrix reports five shapes while running four.
const BUILT = new Set()

function build(name, mutate) {
  const dir = path.join(WORK, name)
  // And a work directory that already holds this shape is refused rather than
  // reused, because reuse is what makes the stale directory available at all.
  if (fs.existsSync(dir)) {
    return { dir, error: `work directory already holds ${name}: pass a fresh --work dir. Reusing one lets a deleted shape pass on the previous run's clone.` }
  }
  BUILT.add(name)
  const c = sh('git', ['clone', '-q', '--no-checkout', SRC, dir])
  if (c.rc) return { dir, error: `clone failed: ${c.out.slice(0,200)}` }
  const co = git(dir, ['checkout', '-q', '--detach', SHA])
  if (co.rc) return { dir, error: `checkout ${SHA} failed: ${co.out.slice(0,200)}` }
  const m = mutate(dir)
  if (m) return { dir, error: m }
  return { dir }
}

// WHICH main. `refs/heads/main` is the wrong first choice and the prototype
// used it: this repository's clones carry a LOCAL main that goes stale the
// moment a merge lands upstream -- measured at d7dc142 while origin/main was
// already 6b71e85, one merge ahead -- and a CI checkout is detached with no
// local branch at all, where it does not exist. Both failures are silent in
// opposite directions: a stale ref measures the wrong tree, a missing one
// makes `build` fail and the matrix refuse. Prefer the remote, fall back to
// the local, and say which was used -- a matrix whose baseline is unstated is
// the class this file exists to catch.
const MAIN_REFS = ['refs/remotes/origin/main', 'refs/heads/main']
let mainTip = '', mainRef = ''
for (const ref of MAIN_REFS) {
  const r = git(SRC, ['rev-parse', '--verify', '--quiet', ref])
  if (r.rc === 0 && r.out.trim()) { mainTip = r.out.trim(); mainRef = ref; break }
}

const pinsOf = (out) => {
  const m = out.match(/FIXTURE ok: \d+ error\(s\) hold (\d+) pins/)
  return m ? Number(m[1]) : null
}

// A FAIL that says nothing about why is the instrument's own defect: CI's first
// run of this matrix failed `shallow / policy_lint rc=0` with `rc=1 ` and a blank
// detail, because this slot quoted only a FIXTURE VACUOUS line and the run had
// produced none. So: the vacuous line if there is one; otherwise every ERROR,
// fatal and skip line; otherwise the last three lines of whatever it printed.
const why = (out) => {
  const vac = out.match(/^FIXTURE VACUOUS.*$/m)
  if (vac) return vac[0].slice(0, 160)
  const bad = out.split('\n').filter((l) => /ERROR|fatal:|^\s*skip\s|Error:|TypeError|ReferenceError/.test(l))
  if (bad.length) return bad.slice(-3).join(' | ').slice(0, 240)
  return out.trim().split('\n').slice(-3).join(' | ').slice(0, 240)
}
const rows = []
const add = (name, ok, detail) => rows.push({ name, ok, detail })

// ---- shape 1: a pull request (HEAD is not origin/main) --------------------
const pr = build('pr', (d) => {
  if (!mainTip) return 'no refs/heads/main in the source repo'
  const r = git(d, ['update-ref', 'refs/remotes/origin/main', mainTip])
  return r.rc ? 'update-ref failed' : null
})
let basePins = null
if (pr.error) add('pr / built', false, pr.error)
else {
  const r = sh('node', ['.claude/workflows/policy_lint.mjs'], { cwd: pr.dir })
  basePins = pinsOf(r.out)
  add('pr / policy_lint rc=0 and every pin earned', r.rc === 0 && basePins !== null,
      `rc=${r.rc} pins=${basePins}`)
  add('pr / nothing skipped in a full clone', !/^\s*skip\s/m.test(r.out),
      (r.out.match(/^\s*skip.*$/m) || ['none'])[0].trim())
  const m = sh('node', ['.claude/workflows/policy_lint_mutants.mjs'], { cwd: pr.dir })
  add('pr / every corpus and record-mode check measured and pinned',
      m.rc === 0 && !/^\s*(SKIP|ACCEPTED|CRASH)\s/m.test(m.out), `rc=${m.rc}`)
}

// ---- shape 2: the push to main (HEAD IS origin/main) ----------------------
// governance.yml runs on `push: branches: [main]`. Instances 1 and 2.
const pm = build('push-main', (d) => {
  const h = git(d, ['rev-parse', 'HEAD']).out.trim()
  const r = git(d, ['update-ref', 'refs/remotes/origin/main', h])
  return r.rc ? 'update-ref failed' : null
})
if (pm.error) add('push-main / built', false, pm.error)
else {
  const r = sh('node', ['.claude/workflows/policy_lint.mjs'], { cwd: pm.dir })
  const p = pinsOf(r.out)
  add('push-main / policy_lint rc=0', r.rc === 0, `rc=${r.rc}`)
  add('push-main / the same pins are earned as on a pull request',
      p !== null && p === basePins, `pins=${p} vs pr=${basePins}`)
  const m = sh('node', ['.claude/workflows/policy_lint_mutants.mjs'], { cwd: pm.dir })
  add('push-main / every corpus and record-mode check still measured and pinned',
      m.rc === 0 && !/^\s*(SKIP|ACCEPTED|CRASH)\s/m.test(m.out),
      `rc=${m.rc} ${(m.out.match(/^\s*(SKIP|ACCEPTED|CRASH).*$/m) || [''])[0].trim()}`)
}

// ---- shape 3: a clone with no origin/main --------------------------------
const nr = build('no-remote', (d) => {
  git(d, ['remote', 'remove', 'origin'])
  git(d, ['update-ref', '-d', 'refs/remotes/origin/main'])
  return git(d, ['rev-parse', '--verify', '--quiet', 'origin/main']).out.trim() ? 'origin/main still resolves' : null
})
if (nr.error) add('no-remote / built', false, nr.error)
else {
  const r = sh('node', ['.claude/workflows/policy_lint.mjs'], { cwd: nr.dir })
  const p = pinsOf(r.out)
  add('no-remote / policy_lint rc=0', r.rc === 0, `rc=${r.rc}`)
  add('no-remote / the skipped drive is said out loud',
      /skip\s+checkProvenance-pin/.test(r.out), 'no `skip checkProvenance-pin` line')
  add('no-remote / a skipped drive does not claim its pins',
      p !== null && basePins !== null && p < basePins, `pins=${p} vs pr=${basePins}`)
  const m = sh('node', ['.claude/workflows/policy_lint_mutants.mjs'], { cwd: nr.dir })
  add('no-remote / the lane reports NOT MEASURED rather than failing',
      m.rc === 0 && /^\s*SKIP\s/m.test(m.out), `rc=${m.rc}`)
}

// ---- shape 4: a shallow clone that HAS origin/main -----------------------
// The arm added at 99dd454 exists for this shape; the assertion beside it
// cannot run in it. Instance 5.
const shl = build('shallow', (d) => {
  if (!mainTip) return 'no refs/heads/main in the source repo'
  git(d, ['update-ref', 'refs/remotes/origin/main', mainTip])
  const par = git(d, ['rev-parse', 'HEAD~1']).out.trim()
  if (!par) return 'no parent commit to graft at'
  fs.writeFileSync(path.join(d, '.git', 'shallow'), par + '\n')
  return git(d, ['rev-parse', '--is-shallow-repository']).out.trim() === 'true' ? null : 'clone did not become shallow'
})
if (shl.error) add('shallow / built', false, shl.error)
else {
  const r = sh('node', ['.claude/workflows/policy_lint.mjs'], { cwd: shl.dir })
  const p = pinsOf(r.out)
  add('shallow / policy_lint rc=0', r.rc === 0, `rc=${r.rc} ${why(r.out)}`)
  // The property, not one spelling of it: an arm this shape cannot drive is
  // said out loud AND is not counted. Declaring the skip line's exact text
  // would test the fix rather than the property.
  add('shallow / an undrivable arm is said out loud and not claimed',
      p !== null && basePins !== null && p < basePins && /^\s*skip\s/m.test(r.out),
      `pins=${p} vs pr=${basePins}; skip line ${/^\s*skip\s/m.test(r.out) ? 'present' : 'absent'}`)
}

// ---- shape 5: the population a check measures can go to zero -------------
// check-wave-script.mjs scans a DIRECTORY for rosters. Instance 4.
const noRost = build('no-rosters', (d) => {
  const wf = path.join(d, '.claude', 'workflows')
  const gone = fs.readdirSync(wf).filter((f) => /^wave-.*-groups\.json$/.test(f))
  if (!gone.length) return 'no rosters to remove'
  for (const f of gone) fs.rmSync(path.join(wf, f))
  return null
})
if (noRost.error) add('no-rosters / built', false, noRost.error)
else {
  const r = sh('node', ['.claude/workflows/check-wave-script.mjs'], { cwd: noRost.dir })
  add('no-rosters / a roster scan over zero rosters does not report ok',
      r.rc !== 0, `rc=${r.rc}; ${(r.out.match(/^\d+ passed.*$/m)||[''])[0]}`)
}

// ---- report --------------------------------------------------------------
//
// THE ROW ROSTER, named one by one. A count is satisfied by a duplicate and by
// a swap -- #614's round 3 measured exactly that on another check -- so the
// thirteen outcomes this matrix declares are listed, and a run whose row set is
// not this set fails whichever way it differs. Deleting an `add(...)` call
// leaves its name here with nothing to satisfy it, which is the point: the
// roster cannot be maintained by the same edit that removes the row.
const DECLARED_ROWS = [
  'pr / policy_lint rc=0 and every pin earned',
  'pr / nothing skipped in a full clone',
  'pr / every corpus and record-mode check measured and pinned',
  'push-main / policy_lint rc=0',
  'push-main / the same pins are earned as on a pull request',
  'push-main / every corpus and record-mode check still measured and pinned',
  'no-remote / policy_lint rc=0',
  'no-remote / the skipped drive is said out loud',
  'no-remote / a skipped drive does not claim its pins',
  'no-remote / the lane reports NOT MEASURED rather than failing',
  'shallow / policy_lint rc=0',
  'shallow / an undrivable arm is said out loud and not claimed',
  'no-rosters / a roster scan over zero rosters does not report ok',
]
const EXPECTED_SHAPES = 5
const built = ['pr','push-main','no-remote','shallow','no-rosters'].filter((n) => BUILT.has(n))
console.log(`  baseline ${mainRef || '(no main ref found)'} = ${mainTip.slice(0, 7) || '-'}`)
for (const r of rows) console.log(`  ${(r.ok ? 'ok' : 'FAIL').padEnd(5)} ${r.name}${r.ok ? '' : `  --  ${r.detail}`}`)
const bad = rows.filter((r) => !r.ok)
const seen = new Set(rows.map((r) => r.name))
const missing = DECLARED_ROWS.filter((n) => !seen.has(n))
// A SET loses duplicates, so a row added twice satisfies both lists below while
// the run reports fourteen outcomes against a thirteen-name roster -- the one
// case a plain count would have caught, missed by the check whose comment says a
// count is satisfied by a duplicate. #659's round 1 drove it. The length check
// is what makes the pair complete: names for a swap, count for a duplicate.
const dupes = rows.length !== new Set(rows.map((r) => r.name)).size
// A `<shape> / built` row is only added when a shape failed to build, so it is
// a permitted extra: it already fails on its own and saying it twice hides the
// cause behind a roster complaint.
const unexpected = [...seen].filter((n) => !DECLARED_ROWS.includes(n) && !n.endsWith('/ built'))
if (missing.length || unexpected.length || dupes) {
  console.log(`\nMATRIX ROSTER: ${missing.length} declared row(s) never ran ${JSON.stringify(missing)}; ${unexpected.length} row(s) ran that are not declared ${JSON.stringify(unexpected)}; ${rows.length} row(s) ran against ${DECLARED_ROWS.length} declared${dupes ? ' -- a NAME APPEARS TWICE, which a set-difference cannot see' : ''}. Names catch a swap and the count catches a duplicate; neither alone is the roster.`)
  process.exit(1)
}
if (built.length !== EXPECTED_SHAPES) {
  console.log(`\nMATRIX VACUOUS: built ${built.length} of ${EXPECTED_SHAPES} shapes [${built.join(', ')}]; a matrix that ran a subset certifies nothing`)
  process.exit(1)
}
console.log(`\n${rows.length - bad.length} declared outcome(s) held, ${bad.length} did not, across ${built.length} environment shape(s)`)
process.exit(bad.length ? 1 : 0)
