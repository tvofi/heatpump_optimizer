// The finder pass of the eleven-dimension audit: one fresh-eyes auditor per
// dimension against a pinned baseline, a quiet-window re-measurement, then
// dedup into the register. Sign-off happens between workflows, so this one
// stops after dedup; verification is /audit-verify.
//
//   /audit-find with args {round: 2, baseline: "<sha>", repo: "<abs path of a checkout>"}
//
// No timestamps here on purpose: Date.now() throws inside a workflow so a
// relaunch replays the same agent() calls; the register writer stamps dates.
export const meta = {
  name: 'audit-find',
  description: 'Eleven fresh-eyes auditors against a pinned baseline, quiet-window re-measurement, dedup into the register',
  phases: ['Prepare the baseline', 'Finders', 'Quiet window', 'Dedup'],
}

const round = args?.round ?? 2
const baseline = args?.baseline
const repo = args?.repo
if (!baseline || !repo) throw new Error('args.baseline (sha) and args.repo (absolute path of a checkout) are required')

const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10']
// Compute-heavy finders share a box with everyone else; at most three of them
// run together and the Chromium one never beside them (tools/audit/README.md).
const WAVES = [['D0', 'D2', 'D3', 'D1', 'D5', 'D6', 'D7', 'D10'], ['D9', 'D4', 'D8']]
const ISOLATED = new Set(['D0', 'D3', 'D9'])

const reportSchema = {
  type: 'object',
  required: ['dimension', 'baseline_sha', 'report_path', 'findings', 'non_findings', 'harnesses'],
  properties: {
    dimension: { type: 'string' },
    baseline_sha: { type: 'string' },
    report_path: { type: 'string' },
    exposure: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'title', 'severity', 'claim', 'evidence', 'instrumented_symbol', 'perturbation', 'metric_definition', 'stop_rule_class', 'files', 'proposed_fix_scope'],
        properties: {
          id: { type: 'string' }, title: { type: 'string' }, severity: { type: 'string' }, claim: { type: 'string' },
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
1. Export baseline ${baseline} with \`git archive\` into a sibling directory named audit-r${round}-baseline, then delete from the export: docs/audit-*.md, docs/backlog.md, RELEASE_NOTES.md. Copy tools/audit/ from ${repo} into the export (briefs, README, schema) so the finders have the current briefs even if the baseline predates them. Create tools/audit/round${round}/ in the export.
2. For each of ${[...ISOLATED].join(', ')} run \`git worktree add ../audit-r${round}-<dim> ${baseline}\` from ${repo}; copy tools/audit/ in the same way.
3. Warm the shared drift cache once: from ${repo}, PYTHONPATH=tests/hastub python tests/env_drift.py --all ${baseline} with GOLDEN_REF pointing at a different commit is not needed — instead run \`python tests/env_drift.py --cache-key ${baseline} --all\` and, if the cache misses, capture the baseline with \`--capture\` as tests/README.md describes so later runs hit.
4. Record the absolute paths, the python interpreter to use (a venv with numpy/scipy; ${repo}/../tvofi-claude/.venv/bin/python exists on the audit box), node, and the Chromium path under ~/.cache/pw-browsers in tools/audit/round${round}/BASELINE.md inside the export.
Return JSON {exportDir, worktrees: {D0, D3, D9}, python, node}.`,
  { label: 'prepare', schema: { type: 'object', required: ['exportDir', 'worktrees', 'python'], properties: { exportDir: { type: 'string' }, worktrees: { type: 'object' }, python: { type: 'string' }, node: { type: 'string' } } } },
)

if (!prep) throw new Error('baseline preparation failed (agent returned null); relaunch')

const finder = (dim) => agent(
  `You are the ${dim} auditor of round ${round}. Work only in ${ISOLATED.has(dim) ? prep.worktrees[dim] : prep.exportDir} (an export/worktree of baseline ${baseline}; no earlier audit records are in it and you must not go looking for them; do not run gh). Use the interpreter ${prep.python} with PYTHONPATH=tests/hastub from that directory's root.
Read tools/audit/briefs/COMMON.md, then tools/audit/briefs/${dim}.md, then tools/audit/README.md, and follow them exactly. Write your harnesses under tools/audit/round${round}/${dim}/ and your report to tools/audit/round${round}/${dim}/REPORT.md. Every finding needs an executed number from a committed harness that hooks a named production symbol and moves under a named perturbation; a finding without those cannot be returned. Mark any wall/CPU/RSS number provisional: true — it will be re-taken on a quiet box.
Return the JSON report described by tools/audit/finding.schema.json (fields: dimension, baseline_sha, report_path, exposure, findings, non_findings, harnesses).`,
  { label: dim, schema: reportSchema },
)

phase('Finders')
const reports = {}
for (const wave of WAVES) {
  const results = await pipeline(wave, finder)
  wave.forEach((dim, i) => { reports[dim] = results[i] })
}
// A failed agent resolves to null. Retry once; a dimension still missing is
// reported as "not reported", never as "no findings".
for (const dim of DIMS) if (!reports[dim]) reports[dim] = await finder(dim)
const missing = DIMS.filter((d) => !reports[d])
if (missing.length) log(`dimensions not reported after one retry: ${missing.join(', ')}`)

phase('Quiet window')
const provisional = DIMS.flatMap((d) => (reports[d]?.findings ?? []).filter((f) => f.provisional || ['cpu', 'wall'].includes(f.evidence?.cpu_or_wall)).map((f) => f.id))
const quiet = await agent(
  `You are the quiet-window measurer for round ${round}. Nothing else may run on the box: take /tmp/hpo-gate.lock with mkdir before starting and remove it at the end. Work in ${prep.exportDir} (and ${prep.worktrees.D3} for D3's mutants) with ${prep.python}, PYTHONPATH=tests/hastub, the five BLAS thread variables set to 1.
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
  return { missing, reports, quiet }
}
if (!quiet) throw new Error('quiet window failed; relaunch to re-run it before dedup')
const dedup = await agent(
  `You are the dedup step of audit round ${round}. Read the eleven reports at ${DIMS.map((d) => reports[d].report_path).join(', ')} and ${quiet.quiet_path}, and the register docs/audit-2026-09.md in ${repo} (Round 1 section: its findings, verdicts, issue numbers). Validate every finding's JSON against tools/audit/finding.schema.json (pip install jsonschema into the venv if needed); a finding that fails validation is listed as "rejected at intake" with the reason.
Merge same-phenomenon findings into M-ids. Classify each finding: new; corroborates open issue #N (say which); regression of a released D-id (which release); matches a round-1 refuted finding (attach the refutation as one argument for the panel). Replace provisional numbers with the quiet ones; D3 findings are only the confirmed mutants.
Write the Round ${round} "Findings register" section of docs/audit-2026-09.md in ${repo} on a branch named claude/audit-r${round}-register (create it from origin/main; commit; do not push): the dimension status table, one table per dimension with id, severity, finding, status=reported, plus the dedup notes. Copy tools/audit/round${round}/ from the export and the worktrees into that branch and commit it too.
Return JSON {branch, findings: [{id, dimension, severity, classification, title}], rejected: [{id, reason}], corroborations: [{id, issue}]}.`,
  { label: 'dedup', schema: { type: 'object', required: ['branch', 'findings', 'rejected', 'corroborations'] } },
)
return { missing, dedup, quiet_path: quiet.quiet_path }
