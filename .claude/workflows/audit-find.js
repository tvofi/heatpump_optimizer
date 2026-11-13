// The finder pass of the per-dimension audit: one seat per scope of
// dev/audit/config/scopes.json against a pinned baseline, then intake into the
// register. Sign-off happens between workflows, so this one stops after intake;
// verification, the judge's dedup and the timing re-takes (its batch re-runner)
// are /audit-verify's. What stays here of the old quiet window is D3's: its
// brief makes a mutant a finding only once a full gate confirms it.
//
//   /audit-find with args {round: 10, baseline: "<sha>", repo: "<abs path of a checkout>",
//                         rotation: <the parsed dev/audit/config/rotation.json at repo's HEAD>,
//                         scopes: <the parsed dev/audit/config/scopes.json at repo's HEAD>,
//                         box: "B4"      -- optional: run only that container's seats
//                         debug_bundle: "<abs path>", debug_export: "<abs path>"
//                                        -- optional, out of tree: D15's diagnostics
//                                           download and its export.py document
//                         from: "intake" -- optional: gather every box's reports, leads, intake}
//
// One cloud container is one box (dev/audit/README.md). A round split across
// containers runs `box` once per box, each pushing its evidence to
// handoff/audit-r<round>-find-<box>, then `from: "intake"` once, after the last
// box. With neither, every box runs here one after another, then intake.
//
// No timestamps here on purpose: Date.now() throws inside a workflow so a
// relaunch replays the same agent() calls; the register writer stamps dates.
export const meta = {
  name: 'audit-find',
  description: 'One finder seat per scope of dev/audit/config/scopes.json against a pinned baseline, per container, then leads and intake into the register',
  phases: ['Prepare the baseline', 'Finders', 'Leads', 'Quiet window', 'Intake'],
}

const round = args?.round
const baseline = args?.baseline
const repo = args?.repo
const rotation = args?.rotation
const scopes = args?.scopes
const box = args?.box
const from = args?.from
const defer = Array.isArray(args?.defer) ? args.defer : []
const judgeFlags = typeof args?.judge_flags === 'string' ? args.judge_flags : ''
const debugBundle = typeof args?.debug_bundle === 'string' ? args.debug_bundle : ''
const debugExport = typeof args?.debug_export === 'string' ? args.debug_export : ''
if ([debugBundle, debugExport].some((x) => x && !x.startsWith('/'))) throw new Error('args.debug_bundle and args.debug_export are absolute paths outside every tree (dev/governance/dimensions/D15.md, Privacy)')
if (!Number.isInteger(round) || !baseline || !repo) throw new Error('args.round (integer), args.baseline (sha) and args.repo (absolute path of a checkout) are required')
// The ledger and the scopes are passed, not read: this runtime has no
// filesystem. The prepare agent below compares both against the committed
// files, as web-fix-wave.js's Reconcile does its roster, so a seat cannot
// dispatch from a ledger or a scope table in its head.
if (!rotation || typeof rotation !== 'object') throw new Error('args.rotation is required: the parsed dev/audit/config/rotation.json, the coverage ledger this pass records into')
if (!scopes || typeof scopes !== 'object') throw new Error('args.scopes is required: the parsed dev/audit/config/scopes.json, the seats this pass dispatches')
if (from !== undefined && from !== 'intake') throw new Error(`args.from is "intake" or absent, not ${JSON.stringify(from)}`)
if (from && box) throw new Error('args.box and args.from are exclusive: a box runs finders, intake gathers every box')

const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17']
// D11 audits the process itself, so it needs `.git` and the API: a worktree, not
// an export. D13 reads the same sources and needs the same (dev/governance/dimensions/
// D13.md), so it is isolated too. DIMS and ISOLATED are the schedule: EVERY brief
// under dev/governance/dimensions/D<N>.md belongs in DIMS. They stopped at D12 through
// round 7 (R7-INSTR-01, #1477), and the omission was silent; the check in
// tools/policy/check-wave-script.mjs derives both from the briefs directory
// and refuses the next one.
// D14 is isolated because it mutates production to prove each detector moves
// (dev/governance/dimensions/D14.md), and runs its detectors against pre-fix commits.
// An isolated seat gets its OWN worktree: seats of one dimension that share a
// box would otherwise mutate one tree under each other.
// D15 is isolated because its perturbations edit production (dev/governance/dimensions/D15.md).
const ISOLATED = new Set(['D0', 'D3', 'D9', 'D11', 'D13', 'D14', 'D15'])
// WHICH FINDERS MAY READ GITHUB, narrower than ISOLATED on purpose: D0, D3 and D9
// are isolated to MUTATE production, not to read the API, and the wall COMMON.md
// draws (a finder's verdicts are its population, never its evidence) is what this
// grants an exception to. D13 is here because its brief's six required outputs
// read `main`'s history and the API -- round 7's own D13 was first dispatched
// with GitHub out of scope and returned one of the six (dev/programme/register/audit-2026-09.md,
// R7-INSTR-01). A dim in here must also be in ISOLATED: the history it reads
// comes from a worktree with `.git`, which is what ISOLATED buys.
const API_DIMS = new Set(['D11', 'D13'])
// D14 is the one finder whose METHOD is earlier findings (dev/governance/dimensions/D14.md):
// it reads dev/audit/config/bugclasses.json and, in its worktree's .git, the history of
// the instances listed there (pre-fix commits). No GitHub: that stays API_DIMS'.
const LEDGER_DIMS = new Set(['D14'])
// D15 debugs the owner's own install from its diagnostics download, which no
// tree carries: the path reaches its seats only through args.debug_bundle.
const BUNDLE_DIMS = new Set(['D15'])

// DISPATCH:BEGIN -- check-wave-script.mjs evaluates this block on its own, so it
// uses nothing from outside it.
//
// How often a dimension runs: `1` every round, `2` on even rounds. A round in
// EVERY_DIM_ROUNDS runs all of them: round 9 widens coverage on the owner's ask
// (the round-9 plan, section 2 default 1), round 10 by the owner's override of
// 2026-10-14. D11 and D13 run every round from round 11 (tvofi 2026-11-13: a
// dimension that sits out a round examines none of its universe in it).
const CADENCE = { D0: 1, D1: 1, D2: 1, D3: 1, D4: 1, D7: 1, D8: 1, D9: 1, D10: 1, D11: 1, D12: 1, D13: 1, D14: 1, D15: 1, D16: 1, D17: 1, D5: 2, D6: 2 }
const EVERY_DIM_ROUNDS = new Set([9, 10])
const activeIn = (r, dim) => !!CADENCE[dim] && (EVERY_DIM_ROUNDS.has(r) || r % CADENCE[dim] === 0)
// The seats of a dimension, from dev/audit/config/scopes.json and nothing else: one
// per key of its `seats`, in the file's order, id `<dim>-<key>`. A seat's steps
// are every step its blocks name, in the dimension's step order, and every one
// is its deep focus: the scopes are disjoint within a dimension
// (tools/audit/check_scopes.py), so no step is a spot check on a cell another
// seat owns. Deterministic by construction -- no randomness, no clock -- so a
// relaunch replays the same seats.
const seatsFromScopes = (table, dim) => {
  const d = table?.[dim]
  if (!d || !d.seats || !Object.keys(d.seats).length) throw new Error(`scopes.json has no seats for ${dim}`)
  return Object.entries(d.seats).map(([key, blocks]) => {
    if (!/^s\d+$/.test(key) || !Array.isArray(blocks) || !blocks.length) throw new Error(`scopes.json ${dim}.seats.${key} is not a seat (s<n> with at least one block)`)
    const named = new Set(blocks.flatMap((b) => b.steps ?? []))
    return { id: `${dim}-${key}`, dim, key, steps: (d.steps ?? []).filter((m) => named.has(m)), blocks }
  })
}
// Where each seat runs: one box per cloud container (the round-9 plan, section
// 4.3). At most three compute-heavy finders share a box, and a Chromium finder
// sits alone (dev/audit/README.md, "Resource rules on the audit box"): D4-s1
// drives the card and D4-s3 renders it for the visual and accessibility pass.
// The leads seat runs after the fan-out, on the box named by LEADS_BOX.
const BOXES = {
  B1: { heavy: ['D0-s1', 'D3-s1', 'D9-s1'], light: ['D5-s1', 'D6-s1', 'D10-s1'] },
  B2: { heavy: ['D0-s2', 'D3-s2', 'D9-s2'], light: ['D5-s2', 'D6-s2', 'D10-s2'] },
  B3: { heavy: ['D0-s3', 'D3-s3', 'D9-s3'], light: ['D5-s3', 'D6-s3', 'D10-s3'] },
  B4: { heavy: ['D2-s1', 'D12-s1', 'D1-s1'], light: ['D1-s2', 'D1-s3', 'D8-s1', 'D17-s1'] },
  B5: { heavy: ['D2-s2', 'D12-s2', 'D7-s2'], light: ['D7-s1', 'D7-s3', 'D8-s2', 'D17-s2'] },
  B6: { heavy: ['D2-s3', 'D12-s3', 'D16-s1'], light: ['D8-s3', 'D4-s2', 'D11-s1'] },
  B7: { heavy: ['D14-s1', 'D14-s2', 'D14-s3'], light: ['D11-s2', 'D11-s3'] },
  B8: { heavy: ['D15-s2', 'D15-s3', 'D16-s2'], light: ['D13-s1', 'D13-s2', 'D13-s3', 'D15-s1', 'D17-s3'] },
  B9: { heavy: [], light: ['D4-s1'] },
  B10: { heavy: [], light: ['D4-s3'] },
}
const CHROMIUM = new Set(['D4-s1', 'D4-s3'])
const LEADS_BOX = 'B8'
// One predicate for the driver's own refusal and the check's controls: every
// dispatched seat in exactly one box, no box naming a seat the scopes do not
// have, at most three heavy per box, a Chromium seat alone.
const boxGaps = (boxes, seatIds) => {
  const gaps = []
  if (!Object.keys(boxes ?? {}).length || !seatIds?.length) return ['no boxes or no seats (an empty extraction is a gap, never an exemption)']
  const placed = Object.entries(boxes).flatMap(([b, x]) => [...(x.heavy ?? []), ...(x.light ?? [])].map((s) => [b, s]))
  for (const s of seatIds) {
    const n = placed.filter(([, p]) => p === s).length
    if (n !== 1) gaps.push(`${s} is in ${n} box(es), not exactly one`)
  }
  for (const [b, s] of placed) if (!seatIds.includes(s)) gaps.push(`${b} names ${s}, which the scopes do not dispatch`)
  for (const [b, x] of Object.entries(boxes)) {
    if ((x.heavy ?? []).length > 3) gaps.push(`${b} runs ${(x.heavy ?? []).length} compute-heavy seats, more than three`)
    const all = [...(x.heavy ?? []), ...(x.light ?? [])]
    if (all.some((s) => CHROMIUM.has(s)) && all.length > 1) gaps.push(`${b} puts the Chromium seat beside ${all.length - 1} other(s)`)
  }
  return gaps
}
// THE DENOMINATOR (COMMON.md; tvofi 2026-11-13: "always check everything in
// their dimension, not only small samples"). What a dimension did not reach in
// its latest earlier round is the first work of this one: a not_reached item of
// a counted step, a step an older round recorded only as a depth word below
// `deep`, and every `unfinished` entry. `age` is the run of consecutive rounds
// an item has gone unreached, so a rotation's bound can be held.
const carryOf = (ledger, r, dim) => {
  const rounds = ledger?.[dim]?.rounds ?? {}
  const earlier = Object.keys(rounds).map(Number).filter((n) => Number.isInteger(n) && n < r).sort((a, b) => b - a)
  if (!earlier.length) return []
  const left = (n, m) => { const c = rounds[n]?.coverage?.[m]; return c && typeof c === 'object' ? (c.not_reached ?? []) : [] }
  const e = rounds[earlier[0]]
  const out = []
  for (const [m, c] of Object.entries(e.coverage ?? {})) {
    if (typeof c === 'string') { if (c !== 'deep') out.push({ step: m, item: `the whole step: round ${earlier[0]} recorded it "${c}" with no denominator`, age: 1 }) }
    else for (const item of c?.not_reached ?? []) out.push({ step: m, item, age: earlier.findIndex((n) => !left(n, m).includes(item)) < 0 ? earlier.length : earlier.findIndex((n) => !left(n, m).includes(item)) })
  }
  for (const u of e.unfinished ?? []) out.push({ step: String(u.step).replace(`${dim}.`, ''), item: `unfinished: ${u.what}`, age: 1 })
  return out
}
// A seat's share of it, numbered C1.. so the report answers by id, and marked
// overdue where the step is a declared rotation (rotation.json's `rotate`:
// step -> {enumerator, bound}) whose bound the item's age has reached.
const seatCarry = (ledger, r, seat) => carryOf(ledger, r, seat.dim).filter((c) => seat.steps.includes(c.step))
  .map((c, i) => ({ id: `C${i + 1}`, ...c, overdue: c.age >= ((ledger?.[seat.dim]?.rotate?.[c.step]?.bound ?? Infinity) - 1) }))
// Why a seat's report is refused: a step it owns with no denominator row, a row
// whose counts do not close, a handed-over item unanswered, an overdue item
// left unreached. An empty list is the only pass.
const denominatorGaps = (seat, rep, carry) => {
  const gaps = []
  const rows = Array.isArray(rep?.coverage) ? rep.coverage : []
  const answered = {}
  for (const m of seat.steps) {
    const mine = rows.filter((c) => c?.step === `${seat.dim}.${m}` || c?.step === m)
    if (mine.length !== 1) { gaps.push(`${m} has ${mine.length} coverage row(s), not exactly one`); continue }
    const c = mine[0]
    if (typeof c.enumerator !== 'string' || !c.enumerator.trim()) gaps.push(`${m} names no enumerator`)
    if (!Number.isInteger(c.universe) || c.universe < 0 || !Number.isInteger(c.examined) || c.examined < 0 || c.examined > c.universe) { gaps.push(`${m} universe=${JSON.stringify(c.universe)} examined=${JSON.stringify(c.examined)} are not counts with examined <= universe`); continue }
    if (!Array.isArray(c.not_reached)) gaps.push(`${m} carries no not_reached list`)
    else if ((c.examined < c.universe) !== (c.not_reached.length > 0)) gaps.push(`${m} examined ${c.examined} of ${c.universe} but lists ${c.not_reached.length} not reached`)
    for (const x of Array.isArray(c.redispatched) ? c.redispatched : []) answered[x?.item] = x?.state
  }
  for (const c of carry) {
    if (!['examined', 'not_reached'].includes(answered[c.id])) gaps.push(`${c.id} (${c.step}), handed over from the round before, is not answered under redispatched`)
    else if (c.overdue && answered[c.id] !== 'examined') gaps.push(`${c.id} (${c.step}) is overdue under its rotation's bound and was not examined`)
  }
  return gaps
}
// DISPATCH:END

const ACTIVE = DIMS.filter((d) => activeIn(round, d))
for (const d of ACTIVE) if (!rotation[d]) throw new Error(`args.rotation has no entry for ${d}; dev/audit/config/rotation.json must carry every dimension`)
const SEATS = ACTIVE.flatMap((d) => seatsFromScopes(scopes, d))
const seatById = Object.fromEntries(SEATS.map((s) => [s.id, s]))
const CARRY = Object.fromEntries(SEATS.map((s) => [s.id, seatCarry(rotation, round, s)]))
// Only the active dimensions' seats are placed, so a round that runs a subset
// checks the boxes against that subset.
const activeBoxes = Object.fromEntries(Object.entries(BOXES).map(([b, x]) => [b, { heavy: x.heavy.filter((s) => ACTIVE.includes(s.split('-')[0])), light: x.light.filter((s) => ACTIVE.includes(s.split('-')[0])) }]))
const placement = boxGaps(activeBoxes, SEATS.map((s) => s.id))
if (placement.length) throw new Error(`the boxes and args.scopes disagree: ${placement.join('; ')}`)
if (box !== undefined && !BOXES[box]) throw new Error(`args.box ${JSON.stringify(box)} is not one of ${Object.keys(BOXES).join(', ')}`)
const boxOf = (id) => Object.keys(BOXES).find((b) => BOXES[b].heavy.includes(id) || BOXES[b].light.includes(id))
const boxSeats = (b) => [...activeBoxes[b].heavy, ...activeBoxes[b].light].map((id) => seatById[id])
const RUN_BOXES = from ? [] : (box ? [box] : Object.keys(BOXES))
const RUN = RUN_BOXES.flatMap(boxSeats)
// A round's evidence lives under dev/audit/rounds/ (R9-RO-8): where
// tools/audit/fold_ledger.py reads JUDGE.json and the sweeps, and where
// prepare_baseline.sh writes BASELINE.md. tools/audit/round<N>/ is the old home.
const ROUND_DIR = `dev/audit/rounds/round${round}`
// What Prepare copies from the checkout over the baseline's own copy, so a
// baseline older than a brief edit still hands every seat the current text.
const CURRENT = ['tools/audit/', 'dev/governance/roles/', 'dev/governance/dimensions/', 'dev/audit/README.md', 'dev/audit/config/']
const seatDir = (s) => `${ROUND_DIR}/${s.dim}/${s.key}`
const isolatedHere = RUN.filter((s) => ISOLATED.has(s.dim))

// The finding's form, read off dev/audit/config/finding.schema.json and nothing
// else (R10-TICK g, i): this runtime has no filesystem, so the block below is
// WRITTEN by `python3 tools/audit/fold_ledger.py sync`, which fold runs after it
// edits the schema's class enum. CLASS_GUESS is intake's class check, the
// third reader of that enum; FINDING_REPORT is the whole schema with its $refs
// inlined, handed to every finder as its return schema, so an enum or a type
// intake validates refuses the reply at return instead of the finding at
// intake (round 10 rejected 35 of 44 box findings on form, NORMALISE.md).
// agreement.mjs's finding-class-id and finder-report-form pairs refuse a block
// that parts from the schema. Never edit it by hand.
// FINDING-SCHEMA:BEGIN -- generated by tools/audit/fold_ledger.py sync
const CLASS_GUESS = /^((I1|I2|I3|I4|I5|N-approval-rebuy|N-body-lint-bounce|N-confounded-learner|N-dispatch-overreach|N-finally-return|N-future-clamp|N-future-instant|N-gate-yield|N-leaf-imports-solver|N-livehead-operator-cancel|N-log-flood|N-move-stale-path|N-name-sort|N-no-expiry|N-order-coupling|N-orphaned-handoff|N-p2b-assembly-reader|N-period-rollover|N-postreview-merge-red|N-provisional-gate-red-read-final|N-reap-lock|N-registry-leak|N-relay-handoff-starvation|N-restart|N-restore-race|N-shared-config|N-silent-stop|N-silent-zero|N-solve-recompute|N-staleness|N-stamp-claim-conflict|N-step-grid|N-structure-blind|N-train-only-predicate|N-unmetered-reference|N-vocabulary-drift|P1|P10|P11|P2|P3|P4|P5|P6|P7|P8|P9|R10-SELFTEST-RED-INTRODUCED|R10-TOPIC-FAMILY|R9-ROW-STALE|new))$/
const FINDING_REPORT = {"title": "Audit finder report", "type": "object", "required": ["dimension", "baseline_sha", "coverage", "unfinished", "findings", "non_findings", "harnesses", "leads"], "properties": {"dimension": {"type": "string", "pattern": "^D(1[0-7]|[0-9])$"}, "baseline_sha": {"type": "string", "minLength": 7}, "exposure": {"type": "string", "description": "Sources the finder had to read that carry earlier audit findings (D5/D6), or GitHub's own records (D11); empty otherwise"}, "coverage": {"type": "array", "description": "The denominator, one row per method step of the brief this seat owns (D<k>.M<n>; COMMON.md, 'The denominator'): what the step ranges over, how much of it this seat examined, and what it did not reach. dev/audit/config/rotation.json records it and the next round's dispatch opens with not_reached", "items": {"type": "object", "required": ["step", "enumerator", "universe", "examined", "not_reached", "redispatched", "evidence"], "properties": {"step": {"type": "string", "pattern": "^D(1[0-7]|[0-9])\\.M[0-9]+$"}, "enumerator": {"type": "string", "minLength": 1, "description": "The command that, run alone from the export root, prints this step's universe one item per line; where the step has no item list, the command printing the population it read"}, "universe": {"type": "integer", "minimum": 0, "description": "Lines the enumerator printed at the baseline"}, "examined": {"type": "integer", "minimum": 0, "description": "Items of it this seat ran the step's method on; never more than universe"}, "not_reached": {"type": "array", "maxItems": 200, "items": {"type": "string", "minLength": 1}, "description": "Every item not examined, by the enumerator's own name for it, or by the enumerator's groups (a file, a class, a grid plane) where the items outnumber the cap; empty exactly when examined equals universe"}, "redispatched": {"type": "array", "description": "Each item the task handed over from the round before (its C<n> id), and whether it was examined this time", "items": {"type": "object", "required": ["item", "state"], "properties": {"item": {"type": "string", "pattern": "^C[0-9]+$"}, "state": {"enum": ["examined", "not_reached"]}}}}, "evidence": {"type": "string"}}}}, "unfinished": {"type": "array", "description": "Steps this seat could not finish, and what is left; the next round's dispatch hands each back as first work", "items": {"type": "object", "required": ["step", "what"], "properties": {"step": {"type": "string", "pattern": "^D(1[0-7]|[0-9])\\.M[0-9]+$"}, "what": {"type": "string"}}}}, "findings": {"type": "array", "items": {"type": "object", "required": ["id", "scope", "step", "title", "severity", "claim", "evidence", "instrumented_symbol", "perturbation", "metric_definition", "phenomenon_property", "seam_rule", "stop_rule_class", "class_guess", "files", "proposed_fix_scope"], "properties": {"id": {"type": "string", "pattern": "^D(1[0-7]|[0-9])(-s[0-9]+)?-[0-9]{2}$", "description": "D<k>-<nn>, or D<k>-s<seat>-<nn> when a round runs more than one finder seat per dimension"}, "scope": {"type": "string", "pattern": "^D(1[0-7]|[0-9])-s[0-9]+$", "description": "The finder seat whose cells the finding measures, a seat of dev/audit/config/scopes.json; the finding's id starts with it"}, "step": {"type": "string", "pattern": "^D(1[0-7]|[0-9])\\.M[0-9]+$", "description": "The brief's method step the finding came from"}, "title": {"type": "string", "maxLength": 120}, "severity": {"enum": ["critical", "high", "medium", "low"]}, "claim": {"type": "string", "description": "One sentence, falsifiable"}, "mechanism": {"type": "string"}, "evidence": {"type": "object", "required": ["command", "harness_path", "value", "unit", "baseline_sha", "machine", "cpu_or_wall", "contention_note", "tolerance", "load1", "thread_factor"], "properties": {"command": {"type": "string"}, "harness_path": {"type": "string", "pattern": "^(?:tools/audit/round|dev/audit/rounds/round)[0-9]+/D(1[0-7]|[0-9])/"}, "value": {"type": ["number", "string"]}, "unit": {"type": "string"}, "baseline_sha": {"type": "string"}, "machine": {"type": "string"}, "cpu_or_wall": {"enum": ["cpu", "wall", "count", "bytes", "ratio", "n/a"]}, "contention_note": {"type": "string", "description": "What else was running; 'quiet' only for a quiet-window re-take"}, "tolerance": {"type": "string", "description": "e.g. '±3 %' or 'exact'"}, "load1": {"type": "number"}, "thread_factor": {"type": "number"}}}, "instrumented_symbol": {"type": "string", "description": "module:symbol the harness hooks"}, "perturbation": {"type": "object", "required": ["change", "expected_direction"], "properties": {"change": {"type": "string"}, "expected_direction": {"enum": ["up", "down", "to_zero", "sign_flip"]}, "observed_value": {"type": ["number", "string"]}}}, "metric_definition": {"type": "string", "maxLength": 200}, "phenomenon_property": {"type": "string", "description": "The phenomenon stated as a property; the fixer is held to it, not the block's text (fixer.md step 8)"}, "seam_rule": {"type": "string", "description": "The command that enumerates the class's seams, in the same form as harness_path"}, "null_control": {"type": "object", "properties": {"command": {"type": "string"}, "value": {"type": ["number", "string"]}, "note": {"type": "string"}}}, "leave_one_out": {"type": "object", "properties": {"cells": {"type": "integer", "minimum": 5}, "min": {"type": "number"}, "max": {"type": "number"}, "drop_most_favourable": {"type": "number"}}}, "reproduction_steps": {"type": "array", "items": {"type": "string"}}, "proposed_fix_scope": {"type": "string"}, "files": {"type": "array", "items": {"type": "string"}}, "expected_golden_drift": {"type": "array", "items": {"type": "string"}}, "stop_rule_class": {"enum": ["bug", "hygiene"]}, "class_guess": {"enum": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "I1", "I2", "I3", "I4", "I5", "N-future-instant", "P11", "N-restart", "N-solve-recompute", "N-structure-blind", "N-name-sort", "N-shared-config", "N-approval-rebuy", "N-finally-return", "N-step-grid", "N-reap-lock", "N-staleness", "N-silent-zero", "N-orphaned-handoff", "N-postreview-merge-red", "R9-ROW-STALE", "N-registry-leak", "N-future-clamp", "N-no-expiry", "N-log-flood", "N-gate-yield", "N-move-stale-path", "N-period-rollover", "N-confounded-learner", "N-leaf-imports-solver", "N-order-coupling", "N-restore-race", "N-silent-stop", "N-body-lint-bounce", "N-train-only-predicate", "N-p2b-assembly-reader", "N-vocabulary-drift", "N-unmetered-reference", "N-livehead-operator-cancel", "N-dispatch-overreach", "R10-TOPIC-FAMILY", "N-relay-handoff-starvation", "N-stamp-claim-conflict", "R10-SELFTEST-RED-INTRODUCED", "N-provisional-gate-red-read-final", "new"], "description": "The finder's guess at the bug class: an id in dev/audit/config/bugclasses.json, or new. The verifier's V3 lens confirms or corrects it; the judge assigns the class. The enum is exactly that file's ids plus new (check-wave-script.mjs holds the two equal), so a class the judge adds lands in both in one pull request"}}, "allOf": [{"if": {"properties": {"evidence": {"properties": {"cpu_or_wall": {"enum": ["cpu", "wall"]}}}}}, "then": {"required": ["null_control"]}}]}}, "non_findings": {"type": "array", "description": "What was checked and held, each with the executed number that showed it", "items": {"type": "object", "required": ["claim", "command", "value"], "properties": {"claim": {"type": "string"}, "command": {"type": "string"}, "value": {"type": "string"}}}}, "harnesses": {"type": "array", "items": {"type": "string", "pattern": "^(?:tools/audit/round|dev/audit/rounds/round)[0-9]+/D(1[0-7]|[0-9])/"}}, "leads": {"type": "array", "description": "What this seat noticed outside its cells (COMMON.md, the scope wall): not a finding and no harness. The driver routes each to the leads seat, which converts one only with an executed number", "items": {"type": "object", "required": ["owner_seat", "file", "symbol", "what"], "properties": {"owner_seat": {"type": "string", "pattern": "^(D(1[0-7]|[0-9])-s[0-9]+|unknown)$", "description": "The seat whose cells hold it (check_scopes.py --seat lists a seat's cells), or unknown"}, "file": {"type": "string"}, "symbol": {"type": "string"}, "what": {"type": "string"}}}}}}
// FINDING-SCHEMA:END
// The driver's own addition: where the seat wrote its REPORT.md.
const reportSchema = { ...FINDING_REPORT, required: [...FINDING_REPORT.required, 'report_path'], properties: { ...FINDING_REPORT.properties, report_path: { type: 'string' } } }

// R10-TICK (e, h), one class: a script that trusts a large agent reply. Each
// collection read off a reply passes here: JSON text (a reply the agent
// serialised, round 10's register read) is parsed, and anything that is not
// the collection named, a cut-off text among them, is refused with the reply
// it came from -- never read as empty. The other half of the class is size:
// no one reply carries a round (the gather below is per box).
const replyField = (v, kind, what) => {
  let x = v
  if (typeof x === 'string') {
    try { x = JSON.parse(x) } catch { throw new Error(`${what}: the reply is text that does not parse as JSON (cut off?)`) }
  }
  const got = x === null ? 'null' : Array.isArray(x) ? 'array' : typeof x
  if (got !== kind) throw new Error(`${what}: the reply is ${got === 'undefined' ? 'missing' : `a${got === 'array' || got === 'object' ? 'n' : ''} ${got}`}, not an ${kind}`)
  return x
}

phase('Prepare the baseline')
const prep = await agent(
  `Prepare the round ${round} audit baseline from the repository at ${repo} (do not modify that checkout)${box ? ` for box ${box} (this container)` : ''}.
1. Export baseline ${baseline} with \`git archive\` into a sibling directory named audit-r${round}-baseline. Keep RELEASE_NOTES.md (tests/entities.py and tests/closure.py read it unguarded). Copy ${CURRENT.join(', ')} from ${repo} into the export (the instruments, the contracts and briefs, the harness contract, the schema, scopes and ledgers) so the finders have the current briefs even if the baseline predates them, then run \`bash tools/audit/prepare_baseline.sh --strip <export> ${round}\` from ${repo} so the finder wall (the findings registers and the backlog, wherever they live) and every earlier round's evidence the gate does not read are removed from the export (the wall and the strip are that script's own, never a second list). Create ${ROUND_DIR}/ in the export. Then, for the upgrade arms (D1.md step 7, D16.md step 2), give the export each earlier release's own package: for the last v* tag of every major version before the baseline and the three latest v* tags before it (\`git -C ${repo} tag --list 'v*' --sort=v:refname\`, keeping the ancestors of ${baseline}), run \`git -C ${repo} archive <tag> custom_components/heatpump_optimizer | tar -x -C <export>/old-releases/<tag>\`, and list the tags in ${ROUND_DIR}/BASELINE.md.
2. For each of ${isolatedHere.map((s) => s.id).join(', ') || '(no isolated seat here)'} run \`git worktree add ../audit-r${round}-<seat id> ${baseline}\` from ${repo}; copy the same paths in the same way and strip it the same way.
3. Warm the shared drift cache once: from ${repo}, run \`DRIFT_WARM_CACHE=1 PYTHONPATH=tests/hastub python3 tests/env_drift.py --all ${baseline}\` (the cache is warmed by a run with that variable set; \`--cache-key [ref] [--all]\` only prints the key, and there is no warm mode behind it).
4. Record the absolute paths, the python interpreter to use (a venv with the pinned numpy/scipy/orjson of tests/requirements-ci.txt), node, and the Chromium path (under $PLAYWRIGHT_BROWSERS_PATH if set, else ~/.cache/pw-browsers) in ${ROUND_DIR}/BASELINE.md inside the export.
5. Read dev/audit/config/rotation.json in ${repo}. rotation_ok is true only if it parses and its per-dimension {steps, rounds, rotate (where the dimension has one)} are exactly these (compare parsed JSON): ${JSON.stringify(Object.fromEntries(DIMS.map((d) => [d, { steps: rotation[d]?.steps ?? null, rounds: rotation[d]?.rounds ?? null, ...(rotation[d]?.rotate ? { rotate: rotation[d].rotate } : {}) }])))}; otherwise false, with the difference in rotation_note.
6. Read dev/audit/config/scopes.json in ${repo}. scopes_ok is true only if it parses to exactly this object (compare parsed JSON, not bytes): ${JSON.stringify(scopes)}; otherwise false, with the difference in scopes_note.
7. From ${repo}, run \`python3 tools/audit/check_scopes.py --repo ${repo} --ref ${baseline}\` and return its exit status as scopes_rc (an integer, read from the shell, never inferred from the text) and its complete output as scopes_out.
Return JSON {exportDir, worktrees: {<seat id>: <absolute path>} for the seats of step 2, python, node, rotation_ok, rotation_note, scopes_ok, scopes_note, scopes_rc, scopes_out}.`,
  { label: 'prepare', schema: { type: 'object', required: ['exportDir', 'worktrees', 'python', 'rotation_ok', 'scopes_ok', 'scopes_rc', 'scopes_out'], properties: { exportDir: { type: 'string' }, worktrees: { type: 'object' }, python: { type: 'string' }, node: { type: 'string' }, rotation_ok: { type: 'boolean' }, rotation_note: { type: 'string' }, scopes_ok: { type: 'boolean' }, scopes_note: { type: 'string' }, scopes_rc: { type: 'integer' }, scopes_out: { type: 'string' } } } },
)

if (!prep) throw new Error('baseline preparation failed (agent returned null); relaunch')
if (!prep.rotation_ok) throw new Error(`args.rotation is not the committed dev/audit/config/rotation.json: ${prep.rotation_note ?? 'no note'}`)
if (!prep.scopes_ok) throw new Error(`args.scopes is not the committed dev/audit/config/scopes.json: ${prep.scopes_note ?? 'no note'}`)
// The scopes are proved disjoint and complete AT THE BASELINE, or no seat runs:
// a production file added since the scopes were written lands in a `rest`
// scope, and one that breaks disjointness is a scope edit before the round.
if (prep.scopes_rc !== 0) throw new Error(`check_scopes.py --ref ${baseline} exited ${JSON.stringify(prep.scopes_rc)}, not 0; fix dev/audit/config/scopes.json before the round:\n${prep.scopes_out ?? ''}`)
log(`round ${round}${box ? ` box ${box}` : ''}: ${ACTIVE.length} dimension(s), ${RUN.length} finder seat(s) here of ${SEATS.length}: ${RUN.map((s) => `${s.id} [${s.steps.join('+')}]`).join(', ') || '(intake only)'}`)

const workdir = (s) => (ISOLATED.has(s.dim) ? prep.worktrees[s.id] : prep.exportDir)
const finder = (seat) => { const dim = seat.dim; const b = boxOf(seat.id); return agent(
  `You are finder seat ${seat.id} of audit round ${round}, dimension ${dim}, on box ${b} (${BOXES[b].heavy.includes(seat.id) ? 'a compute-heavy seat: at most three share this box' : 'a light seat'}${CHROMIUM.has(seat.id) ? '; the Chromium seat, alone on its box' : ''}). Work only in ${workdir(seat)} (an export/worktree of baseline ${baseline}; ${LEDGER_DIMS.has(dim) ? 'your brief is the exception to the earlier-findings wall: read dev/audit/config/bugclasses.json and the git history of the instances it lists (their pre-fix commits, from this worktree\'s .git), and record what you read under exposure' : 'the earlier-round files left in it are the ones the gate reads, not a record for you, and you must not go looking for earlier findings'}; ${API_DIMS.has(dim) ? 'your brief is the one exception to the GitHub wall -- read the history and the API it names, and record what you read under exposure' : 'do not run gh'}). Use the interpreter ${prep.python} with PYTHONPATH=tests/hastub from that directory's root.${BUNDLE_DIMS.has(dim) ? ` ${debugBundle ? `The real bundle is ${debugBundle}${debugExport ? ` and its export.py document ${debugExport}` : ' (no export.py document was named, so the timeline replay is unfinished)'}: read them in place, never copy either into a tree.` : 'No real bundle was named: rehearse on the synthetic week and report every step unfinished, with no finding.'}` : ''}
Read dev/governance/roles/COMMON.md, then dev/governance/dimensions/${dim}.md, then dev/audit/README.md, and follow them exactly. The brief's numbered method steps are ${dim}.M1, ${dim}.M2, ... in order.
YOUR CELLS. Your scope is ${seat.id} in dev/audit/config/scopes.json: ${JSON.stringify(seat.blocks)}. List them resolved with \`python3 ${repo}/tools/audit/check_scopes.py --repo ${repo} --ref ${baseline} --seat ${seat.id}\` (one line per step set, axis value set and file). Every step you own is a deep focus: ${seat.steps.map((m) => `${dim}.${m}`).join(', ')}. Measure only these cells, and ALL of them: a step ranges over everything its enumerator prints, not over a sample. ${CARRY[seat.id].length ? `FIRST WORK, before anything else -- what the round before left not reached in your steps: ${JSON.stringify(CARRY[seat.id].map((c) => ({ id: c.id, step: `${dim}.${c.step}`, item: c.item, ...(c.overdue ? { overdue: true } : {}) })))}. Answer each by its id under its step's redispatched, examined or not_reached; an item marked overdue has reached its rotation's bound and a report leaving it not_reached is refused.` : 'The round before handed your steps nothing not reached.'} Outside your cells, do not measure and write no harness: record a lead {owner_seat, file, symbol, what} in your report's leads, owner_seat being the seat whose cells hold it (\`--seat\` lists any seat's) or "unknown". Leads go to the leads seat after the fan-out.
Write your harnesses under ${seatDir(seat)}/ and your report to ${seatDir(seat)}/REPORT.md. Every finding needs an executed number from a committed harness that hooks a named production symbol and moves under a named perturbation; a finding without those cannot be returned. Mark any wall/CPU/RSS number provisional: true -- the judge's batch re-runner re-takes it on a quiet container.
Return the JSON report described by dev/audit/config/finding.schema.json (fields: dimension, baseline_sha, report_path, exposure, coverage, unfinished, findings, non_findings, harnesses, leads). Number your findings ${seat.id}-01, -02, ... (finding.schema.json's id pattern); every finding carries scope "${seat.id}" and class_guess (an id in dev/audit/config/bugclasses.json, or "new"); coverage carries exactly one row per step of yours -- its enumerator (the command that prints the step's universe), universe (the lines it printed), examined, not_reached (every item not examined, by name; empty only when examined equals universe), redispatched and evidence -- and a report whose rows are missing or do not close is refused and the seat re-run; unfinished names each step you could not finish and what is left; every finding names its step.`,
  { label: seat.id, schema: reportSchema },
) }

const reports = {}
if (!from) {
  phase('Finders')
  // Boxes one after another, the seats of a box together: in a round split
  // across containers RUN_BOXES is this container's one box.
  for (const b of RUN_BOXES) {
    const seats = boxSeats(b)
    if (!seats.length) continue
    const results = await pipeline(seats, finder)
    seats.forEach((s, i) => { reports[s.id] = results[i] })
  }
  // A failed agent resolves to null, and so does one whose denominator does
  // not close. Retry once; a seat still missing is reported as "not reported",
  // never as "no findings".
  for (const s of RUN) {
    const gaps = reports[s.id] ? denominatorGaps(s, reports[s.id], CARRY[s.id]) : []
    if (gaps.length) { log(`${s.id}: report refused, re-running the seat: ${gaps.join('; ')}`); reports[s.id] = null }
  }
  for (const s of RUN) if (!reports[s.id]) reports[s.id] = await finder(s)
}

if (box) {
  const mine = RUN.map((s) => s.id)
  const missingHere = mine.filter((id) => !reports[id])
  if (missingHere.length) log(`box ${box}: seats not reported after one retry: ${missingHere.join(', ')}`)
  const collect = await agent(
    `You are the collector of box ${box}, audit round ${round}. In ${repo}, create branch handoff/audit-r${round}-find-${box} from origin/main (never check it out in a shared checkout; use a worktree), copy into it ${RUN.map((s) => `${seatDir(s)}/`).join(', ')} from ${prep.exportDir} and from the seat worktrees ${JSON.stringify(prep.worktrees)}, and write ${ROUND_DIR}/reports-${box}.json with exactly this object (two-space indent, trailing newline): ${JSON.stringify({ box, missing: missingHere, reports: Object.fromEntries(mine.filter((id) => reports[id]).map((id) => [id, reports[id]])) })}. Commit and push the branch (git push -u origin HEAD:handoff/audit-r${round}-find-${box}). Return JSON {branch, commit}.`,
    { label: `collect-${box}`, schema: { type: 'object', required: ['branch', 'commit'], properties: { branch: { type: 'string' }, commit: { type: 'string' } } } },
  )
  return { box, missing: missingHere, collect, reports }
}

if (from) {
  // One gatherer per box, in parallel (R10-TICK e): round 10's one gatherer
  // returned all 45 reports in one reply, which was cut off, and intake read
  // every seat as missing. Each reply now carries one box's reports. A seat
  // a box reports that BOXES places elsewhere (a seat re-run on another
  // container) is taken and logged; where two boxes report one seat, the box
  // BOXES places it on wins. The label stays `gather` on every box: the
  // base's check-wave-script.mjs keys its stub on it (decision 0013).
  const gatherBox = async (b) => {
    const got = await agent(
      `You are the gatherer of box ${b}, audit round ${round}. From ${repo}, fetch branch handoff/audit-r${round}-find-${b} and read ${ROUND_DIR}/reports-${b}.json from it. Return JSON {reports: {<seat id>: <report>}, absent_boxes: []} with each report exactly as the file holds it, or {reports: {}, absent_boxes: ["${b}"]} when the branch or the file is missing.`,
      { label: 'gather', schema: { type: 'object', required: ['reports', 'absent_boxes'], properties: { reports: { type: 'object' }, absent_boxes: { type: 'array', items: { type: 'string' } } } } },
    )
    if (!got) return { b, error: 'the gatherer returned null' }
    try {
      return { b, reports: replyField(got.reports, 'object', `box ${b} gather: reports`), absent: replyField(got.absent_boxes, 'array', `box ${b} gather: absent_boxes`).includes(b) }
    } catch (e) { return { b, error: e.message } }
  }
  const gathered = await pipeline(Object.keys(BOXES).filter((b) => boxSeats(b).length), gatherBox)
  for (const g of gathered) {
    if (g.error) { log(`box ${g.b}: ${g.error}; its seats stay missing (relaunch with from: "intake")`); continue }
    if (g.absent) log(`box ${g.b} has no evidence branch`)
    for (const [id, rep] of Object.entries(g.reports)) {
      if (!seatById[id]) { log(`box ${g.b}'s reply names ${id}, which this round dispatches no seat as; ignored`); continue }
      if (boxOf(id) === g.b) reports[id] = rep
      else if (!reports[id]) { log(`box ${g.b} reports ${id}, which BOXES places on ${boxOf(id)}`); reports[id] = rep }
    }
  }
}

// Every report, a finder's reply or a box file's, has its collections checked
// before any is read; one that fails is a seat not reported, never a seat
// with no findings.
const REPORT_LISTS = ['coverage', 'unfinished', 'findings', 'non_findings', 'harnesses', 'leads']
for (const [id, rep] of Object.entries(reports)) {
  if (!rep) continue
  try {
    const r = replyField(rep, 'object', `${id}'s report`)
    reports[id] = { ...r, ...Object.fromEntries(REPORT_LISTS.map((k) => [k, replyField(r[k] ?? [], 'array', `${id}'s report: ${k}`)])) }
  } catch (e) { log(`${e.message}; ${id} is read as not reported`); delete reports[id] }
}

// The denominator is intake's first refusal (COMMON.md): a report that does not
// say what its steps range over, how much it examined and what it left is a
// seat not reported -- a falling count of findings is otherwise unreadable.
for (const s of SEATS) {
  if (!reports[s.id]) continue
  const gaps = denominatorGaps(s, reports[s.id], CARRY[s.id])
  if (gaps.length) { log(`${s.id}'s report carries no closed denominator and is read as not reported: ${gaps.join('; ')}`); delete reports[s.id] }
}
const missing = SEATS.map((s) => s.id).filter((id) => !reports[id] && !defer.includes(id))
if (defer.length) log(`deferred to the catch-up batch (tvofi 2026-09-26): ${defer.join(', ')}`)
if (missing.length) log(`seats not reported: ${missing.join(', ')}`)
const REPORTED = SEATS.map((s) => s.id).filter((id) => reports[id])

// Intake's mechanical half, computed here so it is the script's and not an
// agent's: a finding must carry its own seat as scope, an id under that seat,
// and a class_guess the schema admits. A failure is rejected at intake with the
// reason, never repaired.
const rejected = []
const accepted = []
for (const id of REPORTED) {
  for (const f of reports[id].findings ?? []) {
    const why = [
      f.scope !== id && `scope ${JSON.stringify(f.scope)} is not the seat that returned it (${id})`,
      !(typeof f.id === 'string' && f.id.startsWith(`${id}-`)) && `id ${JSON.stringify(f.id)} is not numbered under ${id}`,
      !CLASS_GUESS.test(String(f.class_guess ?? '')) && `class_guess ${JSON.stringify(f.class_guess)} is neither a ledger id nor "new"`,
    ].filter(Boolean)
    if (why.length) rejected.push({ id: f.id ?? `${id}-?`, seat: id, reason: why.join('; ') })
    else accepted.push({ ...f, seat: id })
  }
}

// The scope wall's other side (COMMON.md): every lead any seat raised goes to
// the one leads seat, grouped by the seat whose cells hold it. The plan's
// "route to the owner while it still runs" has no form here -- an agent takes
// no input once dispatched -- so every lead waits for the fan-out to finish.
const leads = REPORTED.flatMap((id) => (reports[id].leads ?? []).map((l) => ({ ...l, raised_by: id })))
phase('Leads')
let leadsSeat = null
if (leads.length) {
  const byOwner = leads.reduce((m, l) => ((m[l.owner_seat] ??= []).push(l), m), {})
  leadsSeat = await agent(
    `You are the leads seat of audit round ${round}, on box ${LEADS_BOX}. Read dev/governance/roles/COMMON.md and dev/audit/README.md, and follow them. Prepare your own export of baseline ${baseline} from ${repo} as a finder's is prepared (git archive; ${CURRENT.join(', ')} copied in from ${repo}; then \`bash tools/audit/prepare_baseline.sh --strip <export> ${round}\` from ${repo}, which applies the finder wall and the earlier-round strip), and work only there, with PYTHONPATH=tests/hastub. Do not run gh; do not look for earlier findings.
These are the leads the finder seats raised outside their own cells, grouped by the seat whose cells hold them: ${JSON.stringify(byOwner)}. Before measuring a lead, read its owner seat's REPORT.md (paths: ${JSON.stringify(Object.fromEntries(REPORTED.map((id) => [id, reports[id].report_path])))}${from ? `; these paths are inside each box's evidence branch, so fetch handoff/audit-r${round}-find-<box> for boxes ${Object.keys(BOXES).join(', ')} from ${repo}'s origin and read them there` : ''}): a lead the owner already measured, as a finding or a non-finding, is closed by that entry and not re-measured. Turn a lead into a finding ONLY with an executed number under COMMON.md -- harness, instrumented symbol, perturbation, metric definition, and the null control and leave-one-out where they apply. The finding is the owner's cells' finding: scope = the owner seat, id <owner seat>-51, -52, ..., harness under ${ROUND_DIR}/<owner dimension>/leads/. A lead with owner "unknown" is assigned an owner with \`python3 ${repo}/tools/audit/check_scopes.py --repo ${repo} --ref ${baseline} --seat <id>\` first.
Write your report to ${ROUND_DIR}/LEADS.md. Return JSON {report_path, findings (each as finding.schema.json's finding), non_findings, harnesses, converted: [{raised_by, file, symbol, finding_id}], closed: [{raised_by, file, symbol, why}]} -- every lead appears in exactly one of converted and closed.`,
    { label: 'leads', schema: { type: 'object', required: ['report_path', 'findings', 'non_findings', 'harnesses', 'converted', 'closed'], properties: { report_path: { type: 'string' }, findings: reportSchema.properties.findings, non_findings: reportSchema.properties.non_findings, harnesses: reportSchema.properties.harnesses, converted: { type: 'array', items: { type: 'object', required: ['raised_by', 'file', 'symbol', 'finding_id'] } }, closed: { type: 'array', items: { type: 'object', required: ['raised_by', 'file', 'symbol', 'why'] } } } } },
  )
  if (!leadsSeat) log('the leads seat returned null; its leads are registered unconverted')
  for (const f of leadsSeat?.findings ?? []) {
    const owner = f.scope
    if (!seatById[owner] || !(typeof f.id === 'string' && f.id.startsWith(`${owner}-`)) || !CLASS_GUESS.test(String(f.class_guess ?? ''))) rejected.push({ id: f.id ?? 'leads-?', seat: 'leads', reason: `a converted lead must carry an owner seat as scope, an id under it, and a class_guess; got scope ${JSON.stringify(f.scope)} id ${JSON.stringify(f.id)}` })
    else accepted.push({ ...f, seat: owner, from_lead: true })
  }
}

// This round's ledger entry, minus `yield`, which is the judge's count per step
// and is added after verification. Coverage is the denominator per step, summed
// over the seats that own it: a handed-over item answered not_reached stays in
// not_reached under its own words, so it is handed over again and ages.
// `returned` is findings accepted at intake per seat and `leads` the leads the
// dimension's seats raised and how many became findings: the round-9 plan,
// section 10, so round 10 is judged against round 9 with numbers.
const converted = leadsSeat?.converted ?? []
const ledgerRound = Object.fromEntries(ACTIVE.map((d) => {
  const mine = SEATS.filter((s) => s.dim === d)
  const coverage = Object.fromEntries(rotation[d].steps.map((m) => {
    const rows = mine.flatMap((s) => (reports[s.id]?.coverage ?? []).filter((c) => c.step === `${d}.${m}` || c.step === m).map((c) => ({ c, s })))
    const again = rows.flatMap(({ c, s }) => (c.redispatched ?? []).filter((x) => x.state === 'not_reached').map((x) => CARRY[s.id].find((k) => k.id === x.item)?.item).filter(Boolean))
    const not_reached = [...new Set([...rows.flatMap(({ c }) => c.not_reached ?? []), ...again])]
    return [m, { enumerator: [...new Set(rows.map(({ c }) => c.enumerator))].join(' ; '), universe: rows.reduce((n, { c }) => n + c.universe, 0), examined: rows.reduce((n, { c }) => n + c.examined, 0), not_reached }]
  }))
  const unfinished = mine.flatMap((s) => (reports[s.id]?.unfinished ?? []).map((u) => ({ step: String(u.step).replace(`${d}.`, ''), what: u.what })))
  const returned = Object.fromEntries(mine.map((s) => [s.key, accepted.filter((f) => f.seat === s.id && !f.from_lead).length]))
  const raised = leads.filter((l) => l.raised_by.startsWith(`${d}-`))
  return [d, { seats: mine.map((s) => s.steps), coverage, unfinished, returned, leads: { raised: raised.length, converted: converted.filter((c) => String(c.raised_by ?? '').startsWith(`${d}-`)).length } }]
}))

phase('Intake')
if (missing.length) {
  log(`intake refused: ${missing.join(', ')} not reported`)
  return { missing, reports, rejected, rotation_round: ledgerRound }
}
// D3's candidates become findings only through a full gate on a quiet box
// (dev/governance/dimensions/D3.md, step 3), so that confirmation runs here, once,
// after every box has reported. Wall/CPU re-takes are not this step's: the
// judge's batch re-runner re-takes every provisional number (/audit-verify).
phase('Quiet window')
const d3Seats = REPORTED.filter((id) => id.startsWith('D3-'))
let quiet = null
if (d3Seats.length) {
  quiet = await agent(
    `You are the D3 quiet-window confirmer of audit round ${round}. Nothing else may run on the box: python3 tests/gate_lock.py take --label quiet-r${round} before starting, renew between commands, release at the end -- never mkdir and a shell pid (#404: that lock carries no lease and no flock). Make your own worktree of baseline ${baseline} from ${repo} (git worktree add ../audit-r${round}-quiet ${baseline}); use the pinned venv, PYTHONPATH=tests/hastub, the five BLAS thread variables set to 1.
Read the prescreened mutants in the D3 seats' reports (${d3Seats.map((id) => reports[id].report_path).join(', ')}, ${from ? `on the handoff/audit-r${round}-find-<box> branches` : `under ${prep.exportDir} and the D3 seat worktrees`}). For every one that survived the pre-screen, most consequential first (name in QUIET.md, as not reached, each the window does not get to), apply the mutant in your worktree, commit it so HEAD moves off the baseline, and run \`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=${baseline} GATE_JOBS=1 ./tests/run.sh\`. Record survivor/killed with the killing check names; reset the worktree after each. Write ${ROUND_DIR}/QUIET.md with a table: mutant, finding id, survived, killed_by, load1.
Return JSON {quiet_path, d3_confirmed: [{mutant, finding_id, survived, killed_by}]}.`,
    { label: 'quiet', schema: { type: 'object', required: ['quiet_path', 'd3_confirmed'], properties: { quiet_path: { type: 'string' }, d3_confirmed: { type: 'array', items: { type: 'object' } } } } },
  )
  if (!quiet) throw new Error('the D3 quiet window failed (agent returned null); relaunch to re-run it before intake')
}

// Intake registers; it does not merge. Deduplication, within a dimension and
// across dimensions, is the judge's first step (dev/governance/roles/judge.md),
// which measures that two findings are one mechanism rather than reading it.
const provisional = accepted.filter((f) => f.provisional || ['cpu', 'wall'].includes(f.evidence?.cpu_or_wall)).map((f) => f.id)
const intake = await agent(
  `You are the intake step of audit round ${round}. You register findings; you do not merge, cluster or deduplicate them -- that is the judge's first step, measured there. Every finding below gets its own row.${defer.length ? ` This is BATCH 1 of round ${round}: seats ${defer.join(', ')} have not reported and are deferred to a catch-up batch by tvofi's decision of 2026-09-26; list them in the dimension status table as "deferred (catch-up)", and note that the catch-up batch adds their rows and updates their dimensions' rotation entries.` : ''}${judgeFlags ? ` Add a "Judge flags" subsection to the register section with exactly this text: ${JSON.stringify(judgeFlags)}.` : ''}
1. Validate every accepted finding's JSON against dev/audit/config/finding.schema.json in ${repo} (pip install jsonschema into a venv if needed); one that fails is moved to rejected-at-intake with the validator's message. Already rejected by the driver, with reasons: ${JSON.stringify(rejected)}.
2. Write the Round ${round} "Findings register" section of dev/programme/register/audit-2026-09.md in ${repo}, on a branch handoff/audit-r${round}-register created from origin/main in a worktree of your own: the dimension status table (seats reported, findings accepted, rejected at intake), one table per dimension with id, scope, step, severity, class_guess, title, status=reported, provisional (${JSON.stringify(provisional)} are provisional until the judge's batch re-run), a leads table (raised by, owner seat, file, symbol, converted to / closed because), and ${quiet ? `D3's confirmations from ${quiet.quiet_path}: ${JSON.stringify(quiet.d3_confirmed)} -- a D3 finding is registered only if its mutant survived the full gate, otherwise it is rejected at intake with the killing checks` : 'no D3 confirmations (no D3 seat reported)'}.
3. Copy ${ROUND_DIR}/ into that branch: from ${from ? `the handoff/audit-r${round}-find-<box> branches` : `${prep.exportDir} and the seat worktrees ${JSON.stringify(prep.worktrees)}`}, plus the leads seat's harnesses${quiet ? ` and ${quiet.quiet_path}` : ''}. Set dev/audit/config/rotation.json's rounds["${round}"] for each dimension to exactly ${JSON.stringify(ledgerRound)} (keys sorted, two-space indent, trailing newline); the yield per step is added by the verification pass. Commit and push (git push -u origin HEAD:handoff/audit-r${round}-register).
The accepted findings: ${JSON.stringify(accepted.map((f) => ({ id: f.id, seat: f.seat, scope: f.scope, step: f.step, severity: f.severity, class_guess: f.class_guess, title: f.title, from_lead: !!f.from_lead })))}; the reports: ${JSON.stringify(Object.fromEntries(REPORTED.map((id) => [id, reports[id].report_path])))}.
Return JSON {branch, registered: [ids], rejected: [{id, reason}]}.`,
  { label: 'intake', schema: { type: 'object', required: ['branch', 'registered', 'rejected'], properties: { branch: { type: 'string' }, registered: { type: 'array', items: { type: 'string' } }, rejected: { type: 'array', items: { type: 'object' } } } } },
)
return { missing, intake, rejected, leads: { raised: leads.length, converted: converted.length }, rotation_round: ledgerRound }
