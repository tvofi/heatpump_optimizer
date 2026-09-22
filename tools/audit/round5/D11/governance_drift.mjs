#!/usr/bin/env node
// METRIC (one line): the count of `required-contexts` findings the production
// drift check returns for the committed recorded shape against the live
// boundary derivation, plus the same count under three fixture perturbations;
// the harness exits 1 unless every arm reads its expected value, so a check
// that has gone blind reddens here.
//
// COMMAND (from the repository root):
//   node tools/audit/round5/D11/governance_drift.mjs
// EXPECTED at the fix head (129f96b3, 2026-09-22):
//   RESULT live_ruleset_ids=23698884          (the ruleset the checks come from)
//   RESULT recorded_ruleset_ids=23698884      (the fixture now names it)
//   RESULT drift_committed_fixture=0          (a healthy tree is silent)
//   RESULT control_context_swap=2             (>=2: the context check is alive)
//   RESULT control_ruleset_id_swap=2          (>=1: id drift is now detected)
//   RESULT perturb_ruleset_move_findings=2    (>=1: a ruleset move reddens)
// EXPECTED at the pre-fix tree (baseline 1cc89e0, or 129f96b3 with the fix's
// lines removed): live 23698884 against a fixture recording 22628467, and
//   RESULT drift_committed_fixture=0          (the defect: real drift reads 0)
//   RESULT control_context_swap=2             (the check is alive, not dead)
//   RESULT control_ruleset_id_swap=0          (0: no detector for id drift)
//   RESULT perturb_ruleset_move_findings=0    (0: a ruleset move is invisible)
//   -> exit 1, naming control_ruleset_id_swap and perturb_ruleset_move_findings
// TOLERANCE: exact (counts).
// ROOT RULE: resolves the tree under test from __file__, so it measures THIS
// checkout's committed content, not the cwd.
//
// OFFLINE BY CONSTRUCTION: every `gh api` the production derivation makes is
// answered by a stub `gh` executable that cats the frozen API snapshots in
// fixtures/api/ beside this file (see fixtures/api/PROVENANCE.md). The live
// ruleset is never contacted, so no arm can perturb it.
//
// Instrumented symbols:
//   .claude/workflows/counts.mjs:liveRequiredContexts   (the derivation)
//   .claude/workflows/counts.mjs:requiredContextsDrift  (the drift check)
//
// The metric's key is the value the seam DELIVERS: every count below is
// `requiredContextsDrift(...).length` over a live set the production
// derivation produced, never over a set hand-built here.

import fs from 'node:fs'
import path from 'node:path'
import os from 'node:os'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..', '..', '..')
const API = path.join(HERE, 'fixtures', 'api')
const FIXTURE_REL = '.claude/workflows/fixtures/required-contexts.json'

// A private temp root; created if the runner is somewhere else.
const TMPROOT = process.env.D11_TMPROOT || '/tmp/audit-5/tmp/d11-gov'
fs.mkdirSync(TMPROOT, { recursive: true })
process.env.HPO_PLANDATA = process.env.HPO_PLANDATA || path.join(TMPROOT, 'plandata.json')

// A stub `gh` that answers the two endpoints the derivation asks for out of
// apiDir. `rulesets/<id>` resolves `ruleset-<id>*.json`, so an arm can move the
// required checks to a ruleset id the fixture never recorded.
function writeStub(dir, apiDir) {
  fs.mkdirSync(path.join(dir, 'bin'), { recursive: true })
  const p = path.join(dir, 'bin', 'gh')
  fs.writeFileSync(p, `#!/bin/bash
args="$*"
case "$args" in
  *"/rules/branches/main"*) cat ${JSON.stringify(path.join(apiDir, 'rules-branches-main.json'))}; exit 0 ;;
esac
if [[ "$args" =~ /rulesets/([0-9]+) ]]; then
  id="\${BASH_REMATCH[1]}"
  for f in ${JSON.stringify(apiDir)}/ruleset-"$id"*.json; do
    [ -f "$f" ] && { cat "$f"; exit 0; }
  done
fi
echo "gh-stub: endpoint not snapshotted: $args" >&2; exit 4
`)
  fs.chmodSync(p, 0o755)
  return p
}

// Run the REAL counts.mjs derivation in a child process with the stub gh on
// PATH. counts.mjs memoizes the derivation per process, so each arm needs its
// own child rather than a reset.
function deriveWith(apiDir) {
  const t = fs.mkdtempSync(path.join(TMPROOT, 'h-'))
  const stub = writeStub(t, apiDir)
  const code = `
    process.env.PATH = ${JSON.stringify(path.dirname(stub))} + ':' + process.env.PATH
    import(${JSON.stringify(pathToFileURL(path.join(ROOT, '.claude/workflows/counts.mjs')).href)}).then(m => {
      console.log('JSON' + JSON.stringify(m.liveRequiredContexts()))
    }).catch(e => { console.error(e); process.exit(3) })
  `
  const stdout = execFileSync(process.execPath, ['-e', code], { encoding: 'utf8' })
  const line = stdout.split('\n').find((l) => l.startsWith('JSON'))
  if (!line) throw new Error('child produced no JSON line:\n' + stdout)
  return JSON.parse(line.slice(4))
}

// The ruleset move: the branch view's required_status_checks rule moves to a
// ruleset id nobody recorded, its context list byte-identical. Built by
// rewriting ONE field of a copy of the snapshot.
function perturbedApiDir() {
  const t = fs.mkdtempSync(path.join(TMPROOT, 'p-'))
  const branch = JSON.parse(fs.readFileSync(path.join(API, 'rules-branches-main.json'), 'utf8'))
  const rs = JSON.parse(fs.readFileSync(path.join(API, 'ruleset-23698884.json'), 'utf8'))
  for (const r of branch) if (r.type === 'required_status_checks') r.ruleset_id = 99988877
  rs.id = 99988877
  fs.writeFileSync(path.join(t, 'rules-branches-main.json'), JSON.stringify(branch))
  fs.writeFileSync(path.join(t, 'ruleset-99988877.json'), JSON.stringify(rs))
  fs.copyFileSync(path.join(API, 'ruleset-22628467.json'), path.join(t, 'ruleset-22628467.json'))
  return t
}

const failures = []
const check = (name, got, ok, want) => {
  console.log(`RESULT ${name}=${got} count`)
  if (!ok) failures.push(`${name}=${got} (want ${want})`)
}

const counts = await import(pathToFileURL(path.join(ROOT, '.claude/workflows/counts.mjs')).href)
const fixtureText = fs.readFileSync(path.join(ROOT, FIXTURE_REL), 'utf8')
const fixture = JSON.parse(fixtureText)

const base = deriveWith(API)
if (base == null) {
  console.error('the production derivation returned null under the stub; check fixtures/api')
  process.exit(3)
}
const live = base

console.log(`RESULT live_ruleset_ids=${live.rulesets.join(',')} id`)
console.log(`RESULT recorded_ruleset_ids=${(fixture.rulesets || []).join(',')} id`)
console.log(`RESULT live_context_count=${live.count} count`)

// Arm 1 (equal): the committed record against the live boundary. 0 is correct
// on a healthy tree -- and was ALSO 0 on the baseline tree where the record's
// ruleset id was stale and wrong, which is the blindness the other arms expose.
const committed = counts.requiredContextsDrift(FIXTURE_REL, fixture, live)
check('drift_committed_fixture', committed.length, committed.length === 0, '0')

// Arm 2 (positive control, contexts): rename one recorded context -> >=2.
// One finding for the context the live set gained, one for the recorded name
// the live set no longer returns. Both directions fire.
const renamed = JSON.parse(JSON.stringify(fixture))
renamed.contexts[0] = 'probe-context-zzz'
const swap = counts.requiredContextsDrift(FIXTURE_REL, renamed, live)
check('control_context_swap', swap.length, swap.length >= 2, '>=2')

// Arm 3 (the gap): record a ruleset id that does not exist at all. Both
// directions fire -- the live id is unrecorded and the recorded id is not
// live -- so the count is 2 once the check reads ids, and 0 before.
const swapped = JSON.parse(JSON.stringify(fixture))
swapped.rulesets = [99999999]
const idSwap = counts.requiredContextsDrift(FIXTURE_REL, swapped, live)
check('control_ruleset_id_swap', idSwap.length, idSwap.length >= 1, '>=1')

// Arm 4 (perturbation): the ruleset move, end to end through the real
// derivation, the contexts untouched. >0 once ids are compared.
const p = deriveWith(perturbedApiDir())
if (p == null) {
  console.error('perturb arm failed to derive a live set')
  process.exit(3)
}
console.log(`RESULT perturb_live_ruleset_ids=${p.rulesets.join(',')} id`)
const move = counts.requiredContextsDrift(FIXTURE_REL, fixture, p)
check('perturb_ruleset_move_findings', move.length, move.length >= 1, '>=1')

// The finding the check would print, so the report is actionable.
if (move.length) {
  console.log(`RESULT drift_message_names_live_id=${Number(move.some((f) => f.message.includes('99988877')))} count`)
}

const la = os.loadavg()[0]
let swapins = 0
try {
  swapins = parseInt(execFileSync('bash', ['-c', 'vm_stat | grep "Pages swapped in" | tr -dc "0-9"'], { encoding: 'utf8' }).trim(), 10) || 0
} catch { swapins = -1 }
console.log('RESULT thread_factor=1.00')
console.log(`RESULT load1=${la.toFixed(2)}`)
console.log(`RESULT swapins=${swapins}`)

if (failures.length) {
  console.log(`\nGOVERNANCE DRIFT GAP: ${failures.join('; ')}`)
  console.log('A count of 0 where a move must show means the required-contexts drift check does not read that state.')
  process.exit(1)
}
console.log('\nok: the drift check reads the recorded ruleset id, the contexts, and a ruleset move')
