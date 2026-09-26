// The finder pass of the per-dimension audit: one seat per scope of
// tools/audit/scopes.json against a pinned baseline, then intake into the
// register. Sign-off happens between workflows, so this one stops after intake;
// verification, the judge's dedup and the timing re-takes (its batch re-runner)
// are /audit-verify's. What stays here of the old quiet window is D3's: its
// brief makes a mutant a finding only once a full gate confirms it.
//
//   /audit-find with args {round: 9, baseline: "<sha>", repo: "<abs path of a checkout>",
//                         rotation: <the parsed tools/audit/rotation.json at repo's HEAD>,
//                         scopes: <the parsed tools/audit/scopes.json at repo's HEAD>,
//                         box: "B4"      -- optional: run only that container's seats
//                         from: "intake" -- optional: gather every box's reports, leads, intake}
//
// One cloud container is one box (tools/audit/README.md). A round split across
// containers runs `box` once per box, each pushing its evidence to
// handoff/audit-r<round>-find-<box>, then `from: "intake"` once, after the last
// box. With neither, every box runs here one after another, then intake.
//
// No timestamps here on purpose: Date.now() throws inside a workflow so a
// relaunch replays the same agent() calls; the register writer stamps dates.
export const meta = {
  name: 'audit-find',
  description: 'One finder seat per scope of tools/audit/scopes.json against a pinned baseline, per container, then leads and intake into the register',
  phases: ['Prepare the baseline', 'Finders', 'Leads', 'Quiet window', 'Intake'],
}

const round = args?.round
const baseline = args?.baseline
const repo = args?.repo
const rotation = args?.rotation
const scopes = args?.scopes
const box = args?.box
const from = args?.from
if (!Number.isInteger(round) || !baseline || !repo) throw new Error('args.round (integer), args.baseline (sha) and args.repo (absolute path of a checkout) are required')
// The ledger and the scopes are passed, not read: this runtime has no
// filesystem. The prepare agent below compares both against the committed
// files, as web-fix-wave.js's Reconcile does its roster, so a seat cannot
// dispatch from a ledger or a scope table in its head.
if (!rotation || typeof rotation !== 'object') throw new Error('args.rotation is required: the parsed tools/audit/rotation.json, the coverage ledger this pass records into')
if (!scopes || typeof scopes !== 'object') throw new Error('args.scopes is required: the parsed tools/audit/scopes.json, the seats this pass dispatches')
if (from !== undefined && from !== 'intake') throw new Error(`args.from is "intake" or absent, not ${JSON.stringify(from)}`)
if (from && box) throw new Error('args.box and args.from are exclusive: a box runs finders, intake gathers every box')

const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14']
// D11 audits the process itself, so it needs `.git` and the API: a worktree, not
// an export. D13 reads the same sources and needs the same (tools/audit/briefs/
// D13.md), so it is isolated too. DIMS and ISOLATED are the schedule: EVERY brief
// under tools/audit/briefs/D<N>.md belongs in DIMS. They stopped at D12 through
// round 7 (R7-INSTR-01, #1477), and the omission was silent; the check in
// .claude/workflows/check-wave-script.mjs derives both from the briefs directory
// and refuses the next one.
// D14 is isolated because it mutates production to prove each detector moves
// (tools/audit/briefs/D14.md), and runs its detectors against pre-fix commits.
// An isolated seat gets its OWN worktree: seats of one dimension that share a
// box would otherwise mutate one tree under each other.
const ISOLATED = new Set(['D0', 'D3', 'D9', 'D11', 'D13', 'D14'])
// WHICH FINDERS MAY READ GITHUB, narrower than ISOLATED on purpose: D0, D3 and D9
// are isolated to MUTATE production, not to read the API, and the wall COMMON.md
// draws (a finder's verdicts are its population, never its evidence) is what this
// grants an exception to. D13 is here because its brief's six required outputs
// read `main`'s history and the API -- round 7's own D13 was first dispatched
// with GitHub out of scope and returned one of the six (docs/audit-2026-09.md,
// R7-INSTR-01). A dim in here must also be in ISOLATED: the history it reads
// comes from a worktree with `.git`, which is what ISOLATED buys.
const API_DIMS = new Set(['D11', 'D13'])
// D14 is the one finder whose METHOD is earlier findings (tools/audit/briefs/D14.md):
// it reads tools/audit/bugclasses.json and, in its worktree's .git, the history of
// the instances listed there (pre-fix commits). No GitHub: that stays API_DIMS'.
const LEDGER_DIMS = new Set(['D14'])

// DISPATCH:BEGIN -- check-wave-script.mjs evaluates this block on its own, so it
// uses nothing from outside it.
//
// How often a dimension runs: `2` on even rounds, `3` on rounds divisible by
// three. A round in EVERY_DIM_ROUNDS runs all of them: round 9 widens coverage
// on the owner's ask (the round-9 plan, section 2 default 1), and the cadence is
// otherwise left alone.
const CADENCE = { D0: 1, D1: 1, D2: 1, D3: 1, D4: 1, D7: 1, D8: 1, D9: 1, D10: 1, D12: 1, D14: 1, D5: 2, D6: 2, D11: 3, D13: 3 }
const EVERY_DIM_ROUNDS = new Set([9])
const activeIn = (r, dim) => !!CADENCE[dim] && (EVERY_DIM_ROUNDS.has(r) || r % CADENCE[dim] === 0)
// The seats of a dimension, from tools/audit/scopes.json and nothing else: one
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
// 4.3). At most three compute-heavy finders share a box, and the Chromium
// finder sits alone (tools/audit/README.md, "Resource rules on the audit box");
// the leads seat runs after the fan-out, on the box named by LEADS_BOX.
const BOXES = {
  B1: { heavy: ['D0-s1', 'D3-s1'], light: ['D5-s1', 'D6-s1', 'D10-s1'] },
  B2: { heavy: ['D0-s2', 'D3-s2'], light: ['D5-s2', 'D6-s2', 'D10-s2'] },
  B3: { heavy: ['D0-s3', 'D3-s3'], light: ['D11-s1', 'D11-s2', 'D13-s1'] },
  B4: { heavy: ['D9-s1', 'D2-s1'], light: ['D1-s1', 'D1-s2', 'D8-s3'] },
  B5: { heavy: ['D9-s2', 'D2-s2'], light: ['D1-s3', 'D1-s5', 'D7-s3'] },
  B6: { heavy: ['D2-s4', 'D12-s1', 'D1-s4'], light: ['D7-s1', 'D8-s1'] },
  B7: { heavy: ['D12-s2', 'D12-s3', 'D7-s2'], light: ['D2-s3', 'D8-s2'] },
  B8: { heavy: ['D14-s1', 'D14-s2', 'D14-s3'], light: [] },
  B9: { heavy: ['D14-s4', 'D14-s5'], light: ['D4-s2'] },
  B10: { heavy: [], light: ['D4-s1'] },
}
const CHROMIUM = new Set(['D4-s1'])
const LEADS_BOX = 'B10'
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
// DISPATCH:END

const ACTIVE = DIMS.filter((d) => activeIn(round, d))
for (const d of ACTIVE) if (!rotation[d]) throw new Error(`args.rotation has no entry for ${d}; tools/audit/rotation.json must carry every dimension`)
const SEATS = ACTIVE.flatMap((d) => seatsFromScopes(scopes, d))
const seatById = Object.fromEntries(SEATS.map((s) => [s.id, s]))
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
const seatDir = (s) => `tools/audit/round${round}/${s.dim}/${s.key}`
const isolatedHere = RUN.filter((s) => ISOLATED.has(s.dim))

const lead = { type: 'object', required: ['owner_seat', 'file', 'symbol', 'what'], properties: { owner_seat: { type: 'string' }, file: { type: 'string' }, symbol: { type: 'string' }, what: { type: 'string' } } }
const reportSchema = {
  type: 'object',
  required: ['dimension', 'baseline_sha', 'report_path', 'coverage', 'unfinished', 'findings', 'non_findings', 'harnesses', 'leads'],
  properties: {
    dimension: { type: 'string' },
    baseline_sha: { type: 'string' },
    report_path: { type: 'string' },
    exposure: { type: 'string' },
    // What this seat covered, per step id (`D2.M3`), and what it left undone:
    // tools/audit/rotation.json records both per round.
    coverage: { type: 'array', items: { type: 'object', required: ['step', 'depth', 'evidence'], properties: { step: { type: 'string' }, depth: { enum: ['deep', 'spot', 'none'] }, evidence: { type: 'string' } } } },
    unfinished: { type: 'array', items: { type: 'object', required: ['step', 'what'], properties: { step: { type: 'string' }, what: { type: 'string' } } } },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'scope', 'step', 'title', 'severity', 'claim', 'evidence', 'instrumented_symbol', 'perturbation', 'metric_definition', 'phenomenon_property', 'seam_rule', 'stop_rule_class', 'class_guess', 'files', 'proposed_fix_scope'],
        properties: {
          id: { type: 'string' }, scope: { type: 'string' }, step: { type: 'string' }, title: { type: 'string' }, severity: { type: 'string' }, claim: { type: 'string' },
          evidence: { type: 'object', required: ['command', 'harness_path', 'value', 'unit', 'baseline_sha', 'machine', 'cpu_or_wall', 'contention_note', 'tolerance', 'load1', 'thread_factor'] },
          files: { type: 'array', items: { type: 'string' } },
          proposed_fix_scope: { type: 'string' },
          instrumented_symbol: { type: 'string' },
          perturbation: { type: 'object', required: ['change', 'expected_direction'] },
          metric_definition: { type: 'string' },
          phenomenon_property: { type: 'string' },
          seam_rule: { type: 'string' },
          stop_rule_class: { type: 'string' },
          class_guess: { type: 'string' },
          provisional: { type: 'boolean' },
        },
      },
    },
    non_findings: { type: 'array', items: { type: 'object', required: ['claim', 'command', 'value'] } },
    harnesses: { type: 'array', items: { type: 'string' } },
    leads: { type: 'array', items: lead },
  },
}

phase('Prepare the baseline')
const prep = await agent(
  `Prepare the round ${round} audit baseline from the repository at ${repo} (do not modify that checkout)${box ? ` for box ${box} (this container)` : ''}.
1. Export baseline ${baseline} with \`git archive\` into a sibling directory named audit-r${round}-baseline, then delete from the export: docs/audit-*.md, docs/backlog.md. Keep RELEASE_NOTES.md (tests/entities.py and tests/closure.py read it unguarded). Copy tools/audit/ from ${repo} into the export (briefs, README, schema, scopes) so the finders have the current briefs even if the baseline predates them. Create tools/audit/round${round}/ in the export.
2. For each of ${isolatedHere.map((s) => s.id).join(', ') || '(no isolated seat here)'} run \`git worktree add ../audit-r${round}-<seat id> ${baseline}\` from ${repo}; copy tools/audit/ in the same way.
3. Warm the shared drift cache once: from ${repo}, run \`python tests/env_drift.py --cache-key ${baseline} --all\` and, if the cache misses, capture the baseline with \`--capture\` as tests/README.md describes so later runs hit.
4. Record the absolute paths, the python interpreter to use (a venv with the pinned numpy/scipy/orjson of tests/requirements-ci.txt), node, and the Chromium path under ~/.cache/pw-browsers in tools/audit/round${round}/BASELINE.md inside the export.
5. Read tools/audit/rotation.json in ${repo}. rotation_ok is true only if it parses and its per-dimension step lists are exactly these: ${JSON.stringify(Object.fromEntries(DIMS.map((d) => [d, rotation[d]?.steps ?? null])))}, and its rounds maps equal the ones passed to this run; otherwise false, with the difference in rotation_note.
6. Read tools/audit/scopes.json in ${repo}. scopes_ok is true only if it parses to exactly this object (compare parsed JSON, not bytes): ${JSON.stringify(scopes)}; otherwise false, with the difference in scopes_note.
7. From ${repo}, run \`python3 tools/audit/check_scopes.py --repo ${repo} --ref ${baseline}\` and return its exit status as scopes_rc (an integer, read from the shell, never inferred from the text) and its complete output as scopes_out.
Return JSON {exportDir, worktrees: {<seat id>: <absolute path>} for the seats of step 2, python, node, rotation_ok, rotation_note, scopes_ok, scopes_note, scopes_rc, scopes_out}.`,
  { label: 'prepare', schema: { type: 'object', required: ['exportDir', 'worktrees', 'python', 'rotation_ok', 'scopes_ok', 'scopes_rc', 'scopes_out'], properties: { exportDir: { type: 'string' }, worktrees: { type: 'object' }, python: { type: 'string' }, node: { type: 'string' }, rotation_ok: { type: 'boolean' }, rotation_note: { type: 'string' }, scopes_ok: { type: 'boolean' }, scopes_note: { type: 'string' }, scopes_rc: { type: 'integer' }, scopes_out: { type: 'string' } } } },
)

if (!prep) throw new Error('baseline preparation failed (agent returned null); relaunch')
if (!prep.rotation_ok) throw new Error(`args.rotation is not the committed tools/audit/rotation.json: ${prep.rotation_note ?? 'no note'}`)
if (!prep.scopes_ok) throw new Error(`args.scopes is not the committed tools/audit/scopes.json: ${prep.scopes_note ?? 'no note'}`)
// The scopes are proved disjoint and complete AT THE BASELINE, or no seat runs:
// a production file added since the scopes were written lands in a `rest`
// scope, and one that breaks disjointness is a scope edit before the round.
if (prep.scopes_rc !== 0) throw new Error(`check_scopes.py --ref ${baseline} exited ${JSON.stringify(prep.scopes_rc)}, not 0; fix tools/audit/scopes.json before the round:\n${prep.scopes_out ?? ''}`)
log(`round ${round}${box ? ` box ${box}` : ''}: ${ACTIVE.length} dimension(s), ${RUN.length} finder seat(s) here of ${SEATS.length}: ${RUN.map((s) => `${s.id} [${s.steps.join('+')}]`).join(', ') || '(intake only)'}`)

const workdir = (s) => (ISOLATED.has(s.dim) ? prep.worktrees[s.id] : prep.exportDir)
const finder = (seat) => { const dim = seat.dim; const b = boxOf(seat.id); return agent(
  `You are finder seat ${seat.id} of audit round ${round}, dimension ${dim}, on box ${b} (${BOXES[b].heavy.includes(seat.id) ? 'a compute-heavy seat: at most three share this box' : 'a light seat'}${CHROMIUM.has(seat.id) ? '; the Chromium seat, alone on its box' : ''}). Work only in ${workdir(seat)} (an export/worktree of baseline ${baseline}; ${LEDGER_DIMS.has(dim) ? 'your brief is the exception to the earlier-findings wall: read tools/audit/bugclasses.json and the git history of the instances it lists (their pre-fix commits, from this worktree\'s .git), and record what you read under exposure' : 'the earlier-round files left in it are the ones the gate reads, not a record for you, and you must not go looking for earlier findings'}; ${API_DIMS.has(dim) ? 'your brief is the one exception to the GitHub wall -- read the history and the API it names, and record what you read under exposure' : 'do not run gh'}). Use the interpreter ${prep.python} with PYTHONPATH=tests/hastub from that directory's root.
Read tools/audit/briefs/COMMON.md, then tools/audit/briefs/${dim}.md, then tools/audit/README.md, and follow them exactly. The brief's numbered method steps are ${dim}.M1, ${dim}.M2, ... in order.
YOUR CELLS. Your scope is ${seat.id} in tools/audit/scopes.json: ${JSON.stringify(seat.blocks)}. List them resolved with \`python3 ${repo}/tools/audit/check_scopes.py --repo ${repo} --ref ${baseline} --seat ${seat.id}\` (one line per step set, axis value set and file). Every step you own is a deep focus: ${seat.steps.map((m) => `${dim}.${m}`).join(', ')}. Measure only these cells. Outside them, do not measure and write no harness: record a lead {owner_seat, file, symbol, what} in your report's leads, owner_seat being the seat whose cells hold it (\`--seat\` lists any seat's) or "unknown". Leads go to the leads seat after the fan-out.
Write your harnesses under ${seatDir(seat)}/ and your report to ${seatDir(seat)}/REPORT.md. Every finding needs an executed number from a committed harness that hooks a named production symbol and moves under a named perturbation; a finding without those cannot be returned. Mark any wall/CPU/RSS number provisional: true -- the judge's batch re-runner re-takes it on a quiet container.
Return the JSON report described by tools/audit/finding.schema.json (fields: dimension, baseline_sha, report_path, exposure, coverage, unfinished, findings, non_findings, harnesses, leads). Number your findings ${seat.id}-01, -02, ... (finding.schema.json's id pattern); every finding carries scope "${seat.id}" and class_guess (an id in tools/audit/bugclasses.json, or "new"); coverage names every step of yours with depth deep, spot or none and its evidence; unfinished names each step you could not finish and what is left; every finding names its step.`,
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
  // A failed agent resolves to null. Retry once; a seat still missing is
  // reported as "not reported", never as "no findings".
  for (const s of RUN) if (!reports[s.id]) reports[s.id] = await finder(s)
}

if (box) {
  const mine = RUN.map((s) => s.id)
  const missingHere = mine.filter((id) => !reports[id])
  if (missingHere.length) log(`box ${box}: seats not reported after one retry: ${missingHere.join(', ')}`)
  const collect = await agent(
    `You are the collector of box ${box}, audit round ${round}. In ${repo}, create branch handoff/audit-r${round}-find-${box} from origin/main (never check it out in a shared checkout; use a worktree), copy into it ${RUN.map((s) => `${seatDir(s)}/`).join(', ')} from ${prep.exportDir} and from the seat worktrees ${JSON.stringify(prep.worktrees)}, and write tools/audit/round${round}/reports-${box}.json with exactly this object (two-space indent, trailing newline): ${JSON.stringify({ box, missing: missingHere, reports: Object.fromEntries(mine.filter((id) => reports[id]).map((id) => [id, reports[id]])) })}. Commit and push the branch (git push -u origin HEAD:handoff/audit-r${round}-find-${box}). Return JSON {branch, commit}.`,
    { label: `collect-${box}`, schema: { type: 'object', required: ['branch', 'commit'] } },
  )
  return { box, missing: missingHere, collect, reports }
}

if (from) {
  const gathered = await agent(
    `You are the gatherer of audit round ${round}. From ${repo}, fetch every branch handoff/audit-r${round}-find-<box> for boxes ${Object.keys(BOXES).join(', ')}, and read tools/audit/round${round}/reports-<box>.json from each. Return JSON {reports: {<seat id>: <report>}, absent_boxes: [<box whose branch or file is missing>]} with each report exactly as the file holds it.`,
    { label: 'gather', schema: { type: 'object', required: ['reports', 'absent_boxes'], properties: { reports: { type: 'object' }, absent_boxes: { type: 'array', items: { type: 'string' } } } } },
  )
  if (!gathered) throw new Error('gathering the boxes\' reports failed (agent returned null); relaunch with from: "intake"')
  for (const s of SEATS) if (gathered.reports?.[s.id]) reports[s.id] = gathered.reports[s.id]
  if (gathered.absent_boxes?.length) log(`boxes with no evidence branch: ${gathered.absent_boxes.join(', ')}`)
}

const missing = SEATS.map((s) => s.id).filter((id) => !reports[id])
if (missing.length) log(`seats not reported: ${missing.join(', ')}`)
const REPORTED = SEATS.map((s) => s.id).filter((id) => reports[id])

// Intake's mechanical half, computed here so it is the script's and not an
// agent's: a finding must carry its own seat as scope, an id under that seat,
// and a class_guess the schema admits. A failure is rejected at intake with the
// reason, never repaired.
const CLASS_GUESS = /^([PI][0-9]+|new)$/
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
    `You are the leads seat of audit round ${round}, on box ${LEADS_BOX}. Read tools/audit/briefs/COMMON.md and tools/audit/README.md, and follow them. Prepare your own export of baseline ${baseline} from ${repo} as a finder's is prepared (git archive; docs/audit-*.md and docs/backlog.md deleted; tools/audit/ copied in), and work only there, with PYTHONPATH=tests/hastub. Do not run gh; do not look for earlier findings.
These are the leads the finder seats raised outside their own cells, grouped by the seat whose cells hold them: ${JSON.stringify(byOwner)}. Before measuring a lead, read its owner seat's REPORT.md (paths: ${JSON.stringify(Object.fromEntries(REPORTED.map((id) => [id, reports[id].report_path])))}): a lead the owner already measured, as a finding or a non-finding, is closed by that entry and not re-measured. Turn a lead into a finding ONLY with an executed number under COMMON.md -- harness, instrumented symbol, perturbation, metric definition, and the null control and leave-one-out where they apply. The finding is the owner's cells' finding: scope = the owner seat, id <owner seat>-51, -52, ..., harness under tools/audit/round${round}/<owner dimension>/leads/. A lead with owner "unknown" is assigned an owner with \`python3 ${repo}/tools/audit/check_scopes.py --repo ${repo} --ref ${baseline} --seat <id>\` first.
Write your report to tools/audit/round${round}/LEADS.md. Return JSON {report_path, findings (each as finding.schema.json's finding), non_findings, harnesses, converted: [{raised_by, file, symbol, finding_id}], closed: [{raised_by, file, symbol, why}]} -- every lead appears in exactly one of converted and closed.`,
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
// and is added after verification. The deepest depth any seat reports wins.
// `returned` is findings accepted at intake per seat and `leads` the leads the
// dimension's seats raised and how many became findings: the round-9 plan,
// section 10, so round 10 is judged against round 9 with numbers.
const RANK = { none: 0, spot: 1, deep: 2 }
const converted = leadsSeat?.converted ?? []
const ledgerRound = Object.fromEntries(ACTIVE.map((d) => {
  const mine = SEATS.filter((s) => s.dim === d)
  const coverage = Object.fromEntries(rotation[d].steps.map((m) => {
    const seen = mine.flatMap((s) => (reports[s.id]?.coverage ?? []).filter((c) => c.step === `${d}.${m}` || c.step === m).map((c) => c.depth))
    return [m, seen.reduce((a, b) => (RANK[b] > RANK[a] ? b : a), 'none')]
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
// (tools/audit/briefs/D3.md, step 3), so that confirmation runs here, once,
// after every box has reported. Wall/CPU re-takes are not this step's: the
// judge's batch re-runner re-takes every provisional number (/audit-verify).
phase('Quiet window')
const d3Seats = REPORTED.filter((id) => id.startsWith('D3-'))
let quiet = null
if (d3Seats.length) {
  quiet = await agent(
    `You are the D3 quiet-window confirmer of audit round ${round}. Nothing else may run on the box: python3 tests/gate_lock.py take --label quiet-r${round} before starting, renew between commands, release at the end -- never mkdir and a shell pid (#404: that lock carries no lease and no flock). Make your own worktree of baseline ${baseline} from ${repo} (git worktree add ../audit-r${round}-quiet ${baseline}); use the pinned venv, PYTHONPATH=tests/hastub, the five BLAS thread variables set to 1.
Read the prescreened mutants in the D3 seats' reports (${d3Seats.map((id) => reports[id].report_path).join(', ')}, ${from ? `on the handoff/audit-r${round}-find-<box> branches` : `under ${prep.exportDir} and the D3 seat worktrees`}). For at most six that survived the pre-screen, most consequential first, apply the mutant in your worktree, commit it so HEAD moves off the baseline, and run \`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=${baseline} GATE_JOBS=1 ./tests/run.sh\`. Record survivor/killed with the killing check names; reset the worktree after each. Write tools/audit/round${round}/QUIET.md with a table: mutant, finding id, survived, killed_by, load1.
Return JSON {quiet_path, d3_confirmed: [{mutant, finding_id, survived, killed_by}]}.`,
    { label: 'quiet', schema: { type: 'object', required: ['quiet_path', 'd3_confirmed'] } },
  )
  if (!quiet) throw new Error('the D3 quiet window failed (agent returned null); relaunch to re-run it before intake')
}

// Intake registers; it does not merge. Deduplication, within a dimension and
// across dimensions, is the judge's first step (tools/audit/briefs/judge.md),
// which measures that two findings are one mechanism rather than reading it.
const provisional = accepted.filter((f) => f.provisional || ['cpu', 'wall'].includes(f.evidence?.cpu_or_wall)).map((f) => f.id)
const intake = await agent(
  `You are the intake step of audit round ${round}. You register findings; you do not merge, cluster or deduplicate them -- that is the judge's first step, measured there. Every finding below gets its own row.
1. Validate every accepted finding's JSON against tools/audit/finding.schema.json in ${repo} (pip install jsonschema into a venv if needed); one that fails is moved to rejected-at-intake with the validator's message. Already rejected by the driver, with reasons: ${JSON.stringify(rejected)}.
2. Write the Round ${round} "Findings register" section of docs/audit-2026-09.md in ${repo}, on a branch handoff/audit-r${round}-register created from origin/main in a worktree of your own: the dimension status table (seats reported, findings accepted, rejected at intake), one table per dimension with id, scope, step, severity, class_guess, title, status=reported, provisional (${JSON.stringify(provisional)} are provisional until the judge's batch re-run), a leads table (raised by, owner seat, file, symbol, converted to / closed because), and ${quiet ? `D3's confirmations from ${quiet.quiet_path}: ${JSON.stringify(quiet.d3_confirmed)} -- a D3 finding is registered only if its mutant survived the full gate, otherwise it is rejected at intake with the killing checks` : 'no D3 confirmations (no D3 seat reported)'}.
3. Copy tools/audit/round${round}/ into that branch: from ${from ? `the handoff/audit-r${round}-find-<box> branches` : `${prep.exportDir} and the seat worktrees ${JSON.stringify(prep.worktrees)}`}, plus the leads seat's harnesses${quiet ? ` and ${quiet.quiet_path}` : ''}. Set tools/audit/rotation.json's rounds["${round}"] for each dimension to exactly ${JSON.stringify(ledgerRound)} (keys sorted, two-space indent, trailing newline); the yield per step is added by the verification pass. Commit and push (git push -u origin HEAD:handoff/audit-r${round}-register).
The accepted findings: ${JSON.stringify(accepted.map((f) => ({ id: f.id, seat: f.seat, scope: f.scope, step: f.step, severity: f.severity, class_guess: f.class_guess, title: f.title, from_lead: !!f.from_lead })))}; the reports: ${JSON.stringify(Object.fromEntries(REPORTED.map((id) => [id, reports[id].report_path])))}.
Return JSON {branch, registered: [ids], rejected: [{id, reason}]}.`,
  { label: 'intake', schema: { type: 'object', required: ['branch', 'registered', 'rejected'] } },
)
return { missing, intake, rejected, leads: { raised: leads.length, converted: converted.length }, rotation_round: ledgerRound }
