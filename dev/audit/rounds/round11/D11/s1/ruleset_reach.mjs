#!/usr/bin/env node
// D11-s1 round 11: which of main's and the tags' live rulesets the tree's only
// ruleset drift detector can see.
//
// Metric (one line): of the repository's active rulesets (the API snapshot in
// api/), how many can change -- a bypass actor added with mode `always` -- while
// the production detector (counts.mjs liveRequiredContexts + requiredContextsDrift,
// the `required-contexts` class policy_lint.mjs runs on every governance job)
// reports 0 findings. Count key: the detector's finding count per perturbed
// ruleset, a ruleset counted when that count is 0.
//
// Run (from the export root):
//   node dev/audit/rounds/round11/D11/s1/ruleset_reach.mjs
//   node dev/audit/rounds/round11/D11/s1/ruleset_reach.mjs --perturb
// --perturb is the one-line production edit, made on a temp copy of counts.mjs:
// liveRequiredContexts collects the ruleset id of EVERY branch rule instead of
// `continue`-ing past all but required_status_checks -- with the fix's data half,
// the temp fixture recording 22628467 (ids and object) as the snapshot has it.
// A ruleset is UNMONITORED when its change adds no finding over the null arm. Expected:
//   baseline  RESULT unmonitored=2 (22628467 main-protect, 23937752 release-tags-protect), exact
//   perturbed RESULT unmonitored=1 (23937752 only: a tag ruleset is on no branch rules), down
// Null control: the unperturbed snapshot gives 0 findings, and the same bypass
// added to 23698884 (the ruleset the detector reads) gives >= 1 -- the detector
// is alive, it is the reach that is short.
// The `gh` the detector shells out to is a shim serving api/*.json, so no live
// API call is made and the live ruleset is never touched (D11.md step 4).
// Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; snapshot taken 2026-11-16
// with `gh api repos/tvofi/heatpump_optimizer/rulesets/<id>` and
// `.../rules/branches/main`; machine: box B6 (linux, 4 cpu).
// Instrumented symbol: tools/policy/counts.mjs:liveRequiredContexts (and
// requiredContextsDrift on its output, against the committed fixture).
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

for (const v of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) process.env[v] ??= '1'
const ROOT = process.cwd()
const HERE = path.join(ROOT, 'dev/audit/rounds/round11/D11/s1')
const TMP = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd11s1-rs-'))
process.env.HPO_PLANDATA = path.join(TMP, 'pd')
const PERTURB = process.argv.includes('--perturb')
const cpu0 = process.cpuUsage()

const REPO = 'repos/tvofi/heatpump_optimizer'
const snap = (f) => JSON.parse(fs.readFileSync(path.join(HERE, 'api', f), 'utf8'))
const IDS = [22628467, 23698884, 23937752]
const BYPASS = { actor_id: 424242, actor_type: 'Integration', bypass_mode: 'always' }

// The tree the detector runs from: the real one, or a temp copy with the edit.
let countsPath = path.join(ROOT, 'tools/policy/counts.mjs')
if (PERTURB) {
  const root2 = path.join(TMP, 'tree')
  for (const rel of ['tools/policy/counts.mjs', 'tools/policy/fixtures/required-contexts.json', 'tests/layout.json']) {
    fs.mkdirSync(path.dirname(path.join(root2, rel)), { recursive: true })
    fs.copyFileSync(path.join(ROOT, rel), path.join(root2, rel))
  }
  const p = path.join(root2, 'tools/policy/counts.mjs')
  const src = fs.readFileSync(p, 'utf8')
  const old = "      if (r.type !== 'required_status_checks') continue\n      if (r.ruleset_id != null) ids.add(r.ruleset_id)"
  if (!src.includes(old)) { console.log('PERTURBATION DID NOT APPLY'); process.exit(2) }
  fs.writeFileSync(p, src.replace(old, "      if (r.ruleset_id != null) ids.add(r.ruleset_id)\n      if (r.type !== 'required_status_checks') continue"))
  countsPath = p
  // The fix's data half: the fixture records the newly read ruleset as it stands.
  const fx = path.join(root2, 'tools/policy/fixtures/required-contexts.json')
  const rec = JSON.parse(fs.readFileSync(fx, 'utf8'))
  rec.rulesets = [22628467, 23698884]
  rec.ruleset_objects = { ...rec.ruleset_objects, 22628467: snap('ruleset-22628467.json') }
  fs.writeFileSync(fx, JSON.stringify(rec))
}

// The `gh` shim: serves the snapshot, with one ruleset's bypass list grown.
function shim(perturbedId) {
  const dir = fs.mkdtempSync(path.join(TMP, 'gh-'))
  const files = { [`${REPO}/rules/branches/main`]: snap('rules-branches-main.json') }
  for (const id of IDS) {
    const rs = snap(`ruleset-${id}.json`)
    if (id === perturbedId) rs.bypass_actors = [...(rs.bypass_actors || []), BYPASS]
    files[`${REPO}/rulesets/${id}`] = rs
  }
  fs.writeFileSync(path.join(dir, 'served.json'), JSON.stringify(files))
  fs.writeFileSync(path.join(dir, 'gh'), `#!/usr/bin/env node
const f = require(${JSON.stringify(path.join(dir, 'served.json'))});
const a = process.argv.slice(2);
if (a[0] !== 'api' || !(a[1] in f)) { process.stderr.write('shim: unserved ' + a.join(' ') + '\\n'); process.exit(1) }
process.stdout.write(JSON.stringify(f[a[1]]));
`, { mode: 0o755 })
  return dir
}

const fixture = JSON.parse(fs.readFileSync(PERTURB ? path.join(TMP, 'tree/tools/policy/fixtures/required-contexts.json') : path.join(ROOT, 'tools/policy/fixtures/required-contexts.json'), 'utf8'))
const PATH0 = process.env.PATH
let n = 0
async function findings(perturbedId) {
  process.env.PATH = `${shim(perturbedId)}:${PATH0}`
  const m = await import(`${pathToFileURL(countsPath).href}?arm=${n++}`)   // fresh memo per arm
  const live = m.liveRequiredContexts()
  process.env.PATH = PATH0
  if (live == null) return { count: NaN, why: 'reader returned null' }
  return { count: m.requiredContextsDrift('required-contexts.json', fixture, live).length, read: live.rulesets }
}

const nullArm = await findings(null)
console.log(`null arm (snapshot as read): ${nullArm.count} finding(s), rulesets read ${JSON.stringify(nullArm.read)}`)
let unmonitored = 0
for (const id of IDS) {
  const r = await findings(id)
  const blind = !(r.count - nullArm.count > 0)        // keyed on the change the perturbation makes, over the null arm
  if (blind) unmonitored++
  console.log(`ruleset ${id} gains an 'always' bypass actor: ${r.count} finding(s), delta ${r.count - nullArm.count}${blind ? '  <- UNMONITORED' : ''}`)
}
console.log(`RESULT rulesets=${IDS.length} rulesets`)
console.log(`RESULT unmonitored=${unmonitored} rulesets`)
console.log(`RESULT null_findings=${nullArm.count} findings`)
const u = process.cpuUsage(cpu0)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let sw = 'n/a'
try { sw = fs.readFileSync('/proc/vmstat', 'utf8').split('\n').find((l) => l.startsWith('pswpin')).split(' ')[1] } catch {}
console.log(`RESULT swapins=${sw}`)
void u
fs.rmSync(TMP, { recursive: true, force: true })
