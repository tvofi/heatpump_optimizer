// The finder pass of the per-dimension audit: one fresh-eyes auditor per
// dimension against a pinned baseline, a quiet-window re-measurement, then
// dedup into the register. Sign-off happens between workflows, so this one
// stops after dedup; verification is /audit-verify.
//
//   /audit-find with args {round: 9, baseline: "<sha>", repo: "<abs path of a checkout>",
//                         rotation: <the parsed tools/audit/rotation.json at repo's HEAD>}
//
// No timestamps here on purpose: Date.now() throws inside a workflow so a
// relaunch replays the same agent() calls; the register writer stamps dates.
export const meta = {
  name: 'audit-find',
  description: 'One fresh-eyes auditor per dimension against a pinned baseline, quiet-window re-measurement, dedup into the register',
  phases: ['Prepare the baseline', 'Finders', 'Quiet window', 'Dedup'],
}

const round = args?.round
const baseline = args?.baseline
const repo = args?.repo
const rotation = args?.rotation
if (!Number.isInteger(round) || !baseline || !repo) throw new Error('args.round (integer), args.baseline (sha) and args.repo (absolute path of a checkout) are required')
// The ledger is passed, not read: this runtime has no filesystem. The prepare
// agent below compares it against the committed file, as web-fix-wave.js's
// Reconcile does its roster, so a seat cannot dispatch from a ledger in its head.
if (!rotation || typeof rotation !== 'object') throw new Error('args.rotation is required: the parsed tools/audit/rotation.json, the coverage ledger the dispatch rule reads')

const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14']
// Compute-heavy finders share a box with everyone else; at most three of them
// run together and the Chromium one never beside them (tools/audit/README.md).
const WAVES = [['D0', 'D2', 'D3', 'D1', 'D5', 'D6', 'D7', 'D10', 'D11', 'D12', 'D13', 'D14'], ['D9', 'D4', 'D8']]
// D11 audits the process itself, so it needs `.git` and the API: a worktree, not
// an export. D13 reads the same sources and needs the same (tools/audit/briefs/
// D13.md), so it is isolated too. These two lists -- DIMS and ISOLATED, with
// WAVES partitioning the first -- are the schedule: EVERY brief under
// tools/audit/briefs/D<N>.md belongs in DIMS, and every DIMS entry in exactly one
// wave. They stopped at D12 through round 7 (R7-INSTR-01, #1477), so a round
// driven by this workflow dispatched thirteen dimensions and could not register
// a D13 at all -- the dedup prompt's count and path list both come from DIMS, and
// the missing-dimension log iterates it -- and the omission was silent. The
// check in .claude/workflows/check-wave-script.mjs now derives all three from the
// briefs directory and refuses the next one.
// D14 is isolated because it mutates production to prove each detector moves
// (tools/audit/briefs/D14.md), and runs its detectors against pre-fix commits.
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

// ROTATION:BEGIN -- check-wave-script.mjs evaluates this block on its own, so it
// uses nothing from outside it. Seats per dimension, and how often it runs:
// `every: 2` runs on even rounds, `every: 3` on rounds divisible by three.
const SEATS = {
  D0: { seats: 2, every: 1 }, D1: { seats: 2, every: 1 }, D2: { seats: 2, every: 1 },
  D7: { seats: 2, every: 1 }, D9: { seats: 2, every: 1 }, D12: { seats: 2, every: 1 },
  D3: { seats: 1, every: 1 }, D4: { seats: 1, every: 1 }, D8: { seats: 1, every: 1 },
  D10: { seats: 1, every: 1 }, D14: { seats: 1, every: 1 },
  D5: { seats: 1, every: 2 }, D6: { seats: 1, every: 2 },
  D11: { seats: 1, every: 3 }, D13: { seats: 1, every: 3 },
}
const activeIn = (r, dim) => !!SEATS[dim] && r % SEATS[dim].every === 0
// The dispatch rule. Deterministic by construction -- no randomness, no clock --
// so a relaunch replays the same seats. A step's priority is the rounds since it
// was last covered `deep`, +2 if the last round named it `unfinished`, +1 if the
// last round's yield there was at least one; ties go to the lower step number. A
// step `deep` in each of the last two recorded rounds with zero yield in both is
// spot-only this round. The S highest become one deep focus per seat; every other
// step is a spot check for the seat carrying the fewest steps (lowest seat first).
const planSeats = (ledger, dim, seats, r) => {
  const entry = ledger?.[dim]
  if (!entry || !Array.isArray(entry.steps) || !entry.steps.length) throw new Error(`rotation ledger has no steps for ${dim}`)
  const past = Object.keys(entry.rounds ?? {}).map(Number).filter((n) => Number.isInteger(n) && n < r).sort((a, b) => b - a)
  const at = (n) => entry.rounds[String(n)] ?? {}
  const last = past.length ? at(past[0]) : {}
  const depth = (n, s) => at(n).coverage?.[s] ?? 'none'
  const yieldAt = (n, s) => Number(at(n).yield?.[s] ?? 0)
  const unfinished = new Set((last.unfinished ?? []).map((u) => (typeof u === 'string' ? u : u?.step)))
  const priority = (s) => {
    const lastDeep = past.find((n) => depth(n, s) === 'deep')
    return (lastDeep === undefined ? r : r - lastDeep) + (unfinished.has(s) ? 2 : 0) + (past.length && yieldAt(past[0], s) >= 1 ? 1 : 0)
  }
  const resting = (s) => past.length >= 2 && past.slice(0, 2).every((n) => depth(n, s) === 'deep' && yieldAt(n, s) === 0)
  const order = entry.steps.map((s, i) => ({ s, i, p: priority(s), rest: resting(s) }))
    .sort((a, b) => (a.rest - b.rest) || (b.p - a.p) || (a.i - b.i))
  const plan = Array.from({ length: seats }, (_, k) => ({ seat: k + 1, deep: [], spot: [] }))
  order.forEach(({ s, rest }, n) => {
    if (n < seats && !rest) { plan[n].deep.push(s); return }
    const light = plan.reduce((a, b) => (b.deep.length + b.spot.length < a.deep.length + a.spot.length ? b : a))
    light.spot.push(s)
  })
  return plan
}
// ROTATION:END

const ACTIVE = DIMS.filter((d) => activeIn(round, d))
for (const d of ACTIVE) if (!rotation[d]) throw new Error(`args.rotation has no entry for ${d}; tools/audit/rotation.json must carry every dimension`)
const SEAT_PLAN = Object.fromEntries(ACTIVE.map((d) => [d, planSeats(rotation, d, SEATS[d].seats, round)]))
const seatList = (dims) => dims.flatMap((d) => SEAT_PLAN[d].map((p) => ({ dim: d, ...p, of: SEAT_PLAN[d].length })))
const seatId = (s) => (s.of > 1 ? `${s.dim}-s${s.seat}` : s.dim)
const seatDir = (s) => `tools/audit/round${round}/${s.dim}${s.of > 1 ? `/s${s.seat}` : ''}`

const reportSchema = {
  type: 'object',
  required: ['dimension', 'baseline_sha', 'report_path', 'coverage', 'unfinished', 'findings', 'non_findings', 'harnesses'],
  properties: {
    dimension: { type: 'string' },
    baseline_sha: { type: 'string' },
    report_path: { type: 'string' },
    exposure: { type: 'string' },
    // What this seat covered, per step id (`D2.M3`), and what it left undone:
    // the next round's dispatch reads both from tools/audit/rotation.json.
    coverage: { type: 'array', items: { type: 'object', required: ['step', 'depth', 'evidence'], properties: { step: { type: 'string' }, depth: { enum: ['deep', 'spot', 'none'] }, evidence: { type: 'string' } } } },
    unfinished: { type: 'array', items: { type: 'object', required: ['step', 'what'], properties: { step: { type: 'string' }, what: { type: 'string' } } } },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'step', 'title', 'severity', 'claim', 'evidence', 'instrumented_symbol', 'perturbation', 'metric_definition', 'stop_rule_class', 'files', 'proposed_fix_scope'],
        properties: {
          id: { type: 'string' }, step: { type: 'string' }, title: { type: 'string' }, severity: { type: 'string' }, claim: { type: 'string' },
          evidence: { type: 'object', required: ['command', 'harness_path', 'value', 'unit', 'baseline_sha', 'machine', 'cpu_or_wall', 'contention_note', 'tolerance', 'load1', 'thread_factor'] },
          files: { type: 'array', items: { type: 'string' } },
          proposed_fix_scope: { type: 'string' },
          instrumented_symbol: { type: 'string' },
          perturbation: { type: 'object', required: ['change', 'expected_direction'] },
          metric_definition: { type: 'string' },
          stop_rule_class: { type: 'string' },
          provisional: { type: 'boolean' },
        },
      },
    },
    non_findings: { type: 'array', items: { type: 'object', required: ['claim', 'command', 'value'] } },
    harnesses: { type: 'array', items: { type: 'string' } },
  },
}

phase('Prepare the baseline')
const prep = await agent(
  `Prepare the round ${round} audit baseline from the repository at ${repo} (do not modify that checkout).
1. Export baseline ${baseline} with \`git archive\` into a sibling directory named audit-r${round}-baseline, then delete from the export: docs/audit-*.md, docs/backlog.md. Keep RELEASE_NOTES.md (tests/entities.py and tests/closure.py read it unguarded). Copy tools/audit/ from ${repo} into the export (briefs, README, schema) so the finders have the current briefs even if the baseline predates them. Create tools/audit/round${round}/ in the export.
2. For each of ${[...ISOLATED].filter((d) => ACTIVE.includes(d)).join(', ') || '(none this round)'} run \`git worktree add ../audit-r${round}-<dim> ${baseline}\` from ${repo}; copy tools/audit/ in the same way.
3. Warm the shared drift cache once: from ${repo}, PYTHONPATH=tests/hastub python tests/env_drift.py --all ${baseline} with GOLDEN_REF pointing at a different commit is not needed — instead run \`python tests/env_drift.py --cache-key ${baseline} --all\` and, if the cache misses, capture the baseline with \`--capture\` as tests/README.md describes so later runs hit.
4. Record the absolute paths, the python interpreter to use (a venv with numpy/scipy; ${repo}/../tvofi-claude/.venv/bin/python exists on the audit box), node, and the Chromium path under ~/.cache/pw-browsers in tools/audit/round${round}/BASELINE.md inside the export.
5. Read tools/audit/rotation.json in ${repo}. rotation_ok is true only if it parses and its per-dimension step lists are exactly these: ${JSON.stringify(Object.fromEntries(DIMS.map((d) => [d, rotation[d]?.steps ?? null])))}, and its rounds maps equal the ones passed to this run; otherwise false, with the difference in rotation_note.
Return JSON {exportDir, worktrees: {${[...ISOLATED].filter((d) => ACTIVE.includes(d)).join(', ')}}, python, node, rotation_ok, rotation_note}.`,
  { label: 'prepare', schema: { type: 'object', required: ['exportDir', 'worktrees', 'python', 'rotation_ok'], properties: { exportDir: { type: 'string' }, worktrees: { type: 'object' }, python: { type: 'string' }, node: { type: 'string' }, rotation_ok: { type: 'boolean' }, rotation_note: { type: 'string' } } } },
)

if (!prep) throw new Error('baseline preparation failed (agent returned null); relaunch')
if (!prep.rotation_ok) throw new Error(`args.rotation is not the committed tools/audit/rotation.json: ${prep.rotation_note ?? 'no note'}`)
log(`round ${round}: ${ACTIVE.length} dimension(s), ${seatList(ACTIVE).length} finder seat(s): ${seatList(ACTIVE).map((s) => `${seatId(s)} deep=${s.deep.join('+') || '-'}`).join(', ')}`)

const finder = (seat) => { const dim = seat.dim; return agent(
  `You are the ${dim} auditor of round ${round}${seat.of > 1 ? `, seat ${seat.seat} of ${seat.of}` : ''}. Work only in ${ISOLATED.has(dim) ? prep.worktrees[dim] : prep.exportDir} (an export/worktree of baseline ${baseline}; the earlier-round files left in it are the ones the gate reads, not a record for you, and you must not go looking for earlier findings; ${API_DIMS.has(dim) ? 'your brief is the one exception to the GitHub wall -- read the history and the API it names, and record what you read under exposure' : 'do not run gh'}). Use the interpreter ${prep.python} with PYTHONPATH=tests/hastub from that directory's root.
Read tools/audit/briefs/COMMON.md, then tools/audit/briefs/${dim}.md, then tools/audit/README.md, and follow them exactly. The brief's numbered method steps are ${dim}.M1, ${dim}.M2, ... in order. Your deep focus this round: ${seat.deep.map((m) => `${dim}.${m}`).join(', ') || '(none)'}; spot-check only: ${seat.spot.map((m) => `${dim}.${m}`).join(', ') || '(none)'}. Write your harnesses under ${seatDir(seat)}/ and your report to ${seatDir(seat)}/REPORT.md. Every finding needs an executed number from a committed harness that hooks a named production symbol and moves under a named perturbation; a finding without those cannot be returned. Mark any wall/CPU/RSS number provisional: true — it will be re-taken on a quiet box.
Return the JSON report described by tools/audit/finding.schema.json (fields: dimension, baseline_sha, report_path, exposure, coverage, unfinished, findings, non_findings, harnesses). Number your findings ${seatId(seat)}-01, -02, ... (finding.schema.json's id pattern); coverage names every step of yours with depth deep, spot or none and its evidence; unfinished names each step you could not finish and what is left; every finding names its step.`,
  { label: seatId(seat), schema: reportSchema },
) }

phase('Finders')
const reports = {}
for (const wave of WAVES) {
  const seats = seatList(wave.filter((d) => ACTIVE.includes(d)))
  if (!seats.length) continue
  const results = await pipeline(seats, finder)
  seats.forEach((s, i) => { reports[seatId(s)] = results[i] })
}
// A failed agent resolves to null. Retry once; a seat still missing is
// reported as "not reported", never as "no findings".
const ALL_SEATS = seatList(ACTIVE)
for (const s of ALL_SEATS) if (!reports[seatId(s)]) reports[seatId(s)] = await finder(s)
const missing = ALL_SEATS.map(seatId).filter((id) => !reports[id])
if (missing.length) log(`seats not reported after one retry: ${missing.join(', ')}`)
const REPORTED = ALL_SEATS.map(seatId).filter((id) => reports[id])
// This round's ledger entry, minus `yield`, which is the judge's count per step
// and is added after verification. The deepest depth any seat reports wins.
const RANK = { none: 0, spot: 1, deep: 2 }
const ledgerRound = Object.fromEntries(ACTIVE.map((d) => {
  const mine = ALL_SEATS.filter((s) => s.dim === d)
  const coverage = Object.fromEntries(rotation[d].steps.map((m) => {
    const seen = mine.flatMap((s) => (reports[seatId(s)]?.coverage ?? []).filter((c) => c.step === `${d}.${m}` || c.step === m).map((c) => c.depth))
    return [m, seen.reduce((a, b) => (RANK[b] > RANK[a] ? b : a), 'none')]
  }))
  const unfinished = mine.flatMap((s) => (reports[seatId(s)]?.unfinished ?? []).map((u) => ({ step: String(u.step).replace(`${d}.`, ''), what: u.what })))
  return [d, { seats: mine.map((s) => s.deep.concat(s.spot)), coverage, unfinished }]
}))

phase('Quiet window')
const provisional = REPORTED.flatMap((id) => (reports[id]?.findings ?? []).filter((f) => f.provisional || ['cpu', 'wall'].includes(f.evidence?.cpu_or_wall)).map((f) => f.id))
const quiet = await agent(
  `You are the quiet-window measurer for round ${round}. Nothing else may run on the box: python3 tests/gate_lock.py take --label quiet-r${round} before starting, renew between commands, release at the end -- never mkdir and a shell pid (#404: that lock carries no lease and no flock). Work in ${prep.exportDir} (and ${prep.worktrees.D3 ?? '(no D3 worktree this round)'} for D3's mutants) with ${prep.python}, PYTHONPATH=tests/hastub, the five BLAS thread variables set to 1.
1. Re-execute every harness behind these provisional findings exactly as its header says: ${provisional.join(', ') || '(none)'}. Print load1 and swapins beside every RESULT; redo any RESULT taken at load1 > 1.5.
2. Read ${prep.worktrees.D3}/tools/audit/round${round}/D3/REPORT.md: for at most six prescreened mutants that survived the pre-screen, most consequential first, apply the mutant in that worktree and run \`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=${baseline} GATE_JOBS=1 ./tests/run.sh\` (the baseline ref must not equal HEAD — if the worktree is at the baseline, commit the mutant first so HEAD moves). Record survivor/killed with the killing check names; restore the tree after each.
3. Write tools/audit/round${round}/QUIET.md in the export with a table: finding id, harness, original value, quiet value, load1, thread_factor, verdict (reproduced within tolerance / not).
Return JSON {quiet_path, retaken: [{id, value, load1, thread_factor, reproduced}], d3_confirmed: [{mutant, survived, killed_by}]}.`,
  { label: 'quiet', schema: { type: 'object', required: ['quiet_path', 'retaken', 'd3_confirmed'] } },
)

phase('Dedup')
if (!quiet) log('quiet window agent returned null; provisional numbers stay provisional')
if (missing.length) {
  log(`dedup refused: ${missing.join(', ')} not reported`)
  return { missing, reports, quiet, rotation_round: ledgerRound }
}
if (!quiet) throw new Error('quiet window failed; relaunch to re-run it before dedup')
const dedup = await agent(
  `You are the dedup step of audit round ${round}. Read the ${REPORTED.length} reports at ${REPORTED.map((id) => reports[id].report_path).join(', ')} and ${quiet.quiet_path}, and the register docs/audit-2026-09.md in ${repo} (Round 1 section: its findings, verdicts, issue numbers). Validate every finding's JSON against tools/audit/finding.schema.json (pip install jsonschema into the venv if needed); a finding that fails validation is listed as "rejected at intake" with the reason.
Merge same-phenomenon findings into M-ids. Classify each finding: new; corroborates open issue #N (say which); regression of a released D-id (which release); matches a round-1 refuted finding (attach the refutation as one argument for the panel). Replace provisional numbers with the quiet ones; D3 findings are only the confirmed mutants.
Write the Round ${round} "Findings register" section of docs/audit-2026-09.md in ${repo} on a branch named claude/audit-r${round}-register (create it from origin/main; commit; do not push): the dimension status table, one table per dimension with id, severity, finding, status=reported, plus the dedup notes. Copy tools/audit/round${round}/ from the export and the worktrees into that branch and commit it too. In the same branch set tools/audit/rotation.json's rounds["${round}"] for each dimension to exactly ${JSON.stringify(ledgerRound)} (keys sorted, two-space indent, trailing newline) and commit it; the yield per step is added by the verification pass.
Return JSON {branch, findings: [{id, dimension, severity, classification, title}], rejected: [{id, reason}], corroborations: [{id, issue}]}.`,
  { label: 'dedup', schema: { type: 'object', required: ['branch', 'findings', 'rejected', 'corroborations'] } },
)
return { missing, dedup, quiet_path: quiet.quiet_path, rotation_round: ledgerRound }
