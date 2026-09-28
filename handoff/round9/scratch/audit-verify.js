// Adversarial verification of one round's findings, round 9's shape
// (/mnt/project-files/audit-r9/PLAN.md sections 5-8, carried into policy by #1627):
//
//   Panels   three verifiers per dimension, each owning one lens
//            (tools/audit/briefs/verifier.md), pipelined per dimension: a
//            dimension's triple starts as soon as it is dispatched, never
//            waiting on another dimension. Two `refute` votes, each carrying
//            an executed number, kill a finding at panel; one sends it to the
//            judge `disputed`. A refute with no number is `unresolved`, as a
//            timing-only refute is by verifier.md step 5. A dimension with more
//            findings than SHARD_SIZE gets another triple, split at a finder-
//            seat boundary so no triple verifies across a scope boundary.
//   Judge    one common judge (tools/audit/briefs/judge.md): dedup across all
//            dimensions first, then the scripted re-runs --
//            tools/audit/judge_batch.py, serially under the gate lease, on
//            `args.runners` quiet boxes (runners measure, never decide) --
//            then a verdict and a class for every survivor.
//   Sweep    one seat per class with a surviving finding (D14.md method steps
//            3-4): its enumerator, controls, and the count of confirmed
//            instances. RCA is owed at three instances of a class this round
//            (judged plus swept), or at any instance of a barriered class
//            (defect-root-cause.md).
//   Issues   the register, rotation.json's yield, one issue DRAFT per class and
//            the draft roster `.claude/workflows/wave-r<N>-groups.json`. Filing
//            is the Mac seat's as tvofi (decision 0011): only `args.file: true`
//            lets the writer run `gh`.
//
// args.from: "panels" (default) runs every phase; "judge" skips the panels and
// hands every reported finding to the judge unvoted (a relaunch after the
// verifiers ran elsewhere).
//
//   /audit-verify with args {round: 9, repo: "<abs path>", branch: "claude/audit-r9-register", runners: 1}
//
// .claude/workflows/check-wave-script.mjs ('the round-9 verification pass')
// evaluates the PANEL block alone and drives this body with agent() stubbed
// per label; keep the labels. `wave-script` grades with the base's copy of that
// checker (decision 0013), so a change to this shape lands there first.
export const meta = {
  name: 'audit-verify',
  description: 'Three lens verifiers per dimension with majority kill, one judge (dedup, scripted re-runs, classes), class sweep, issue drafts',
  phases: ['Read the register', 'Panels', 'Judge', 'Class sweep', 'Issues and register'],
}

const round = args?.round ?? 9
const repo = args?.repo
const branch = args?.branch ?? `claude/audit-r${round}-register`
const from = args?.from ?? 'panels'
const runners = Math.max(1, Number(args?.runners ?? 1))
const fileIssues = args?.file === true
if (!repo) throw new Error('args.repo is required')
if (from !== 'panels' && from !== 'judge') throw new Error('args.from must be "panels" or "judge"')

// PLAN section 5: "start at 15".
const SHARD_SIZE = Number(args?.shard_size ?? 15)
const LENSES = [
  { k: 1, name: 'reproduce', steps: '1 and 3', owns: "re-run the finder's harness exactly as its header says; run its perturbation (the finding is void if the number does not move in the stated direction); run the null control; leave-one-out on any aggregate" },
  { k: 2, name: 'independent', steps: '2 and 4', owns: "measure every finding with a harness and metric definition you write yourself, beside the finder's; for a test-gap claim, the single-line PRODUCTION mutation the suite misses and the file it lives in" },
  { k: 3, name: 'reach and class', steps: '3 (reachability, severity)', owns: "whether the path is reachable in real Home Assistant and not only through tests/hastub (tests/ha_contract.py records which stub symbols diverge); severity by consequence; run the finding's seam_rule and say whether it enumerates the phenomenon's seams or only the demonstrated one; confirm or correct class_guess against tools/audit/bugclasses.json" },
]

// The panel rules, between the markers: .claude/workflows/check-wave-script.mjs
// evaluates this block alone, so it may use nothing outside itself.
// PANEL:BEGIN
// A finder seat: the finding's `scope` (finding.schema.json), else the id's
// D<k>-s<n> prefix.
const seatOf = (f) => f.scope ?? String(f.id).replace(/-\d+$/, '')

// Seats in order, packed into shards of at most `size` findings; a seat is
// never split, so a single seat over the size is a shard of its own.
function shardsFor(findings, size) {
  if (findings.length <= size) return [findings]
  const bySeat = {}
  for (const f of findings) (bySeat[seatOf(f)] ??= []).push(f)
  const shards = []
  let cur = []
  for (const seat of Object.keys(bySeat).sort()) {
    if (cur.length && cur.length + bySeat[seat].length > size) { shards.push(cur); cur = [] }
    cur.push(...bySeat[seat])
  }
  if (cur.length) shards.push(cur)
  return shards
}

// verifier.md: a refute counts only with an executed number; without one it is
// `unresolved`, exactly as a refute resting on timing alone is.
const hasNumber = (v) => v?.value !== undefined && v?.value !== null && String(v.value).trim() !== ''
const normalise = (v) => (v?.vote === 'refute' && !hasNumber(v) ? { ...v, vote: 'unresolved', note: 'refute without an executed number' } : v)

function panelOf(votes) {
  const cast = votes.filter(Boolean).map(normalise)
  const refutes = cast.filter((v) => v.vote === 'refute').length
  if (refutes >= 2) return 'killed'
  if (refutes === 1) return 'disputed'
  return cast.length === 3 && cast.every((v) => v.vote === 'verify') ? 'unanimous' : 'split'
}

// defect-root-cause.md, "Except an audit class".
const rcaOwed = (n, barriered) => n >= 3 || (barriered && n >= 1)
// PANEL:END

phase('Read the register')
const reg = await agent(
  `In ${repo}, check out ${branch}. Read the Round ${round} findings register in docs/audit-2026-09.md and every tools/audit/round${round}/D*/ report (REPORT*.md and report*.json). Return JSON {findings: [{id, dimension, scope, step, severity, title, claim, class_guess, report_path, harness_paths: [..], attached_refutation: string|null}]} for every finding with status reported; scope is the finder seat id (D<k>-s<n>), step the brief's method step the report names (D<k>.M<n>, null if none), class_guess the report's ledger id or "new". Do not include corroborations of open issues.`,
  { label: 'read', schema: { type: 'object', required: ['findings'] } },
)
if (!reg) throw new Error('register read failed (agent returned null); relaunch')

const tally = {}
const killed = []
let toJudge = reg.findings.map((f) => ({ ...f, panel: 'unvoted', votes: [] }))
if (from === 'panels') {
  const byDim = {}
  for (const f of reg.findings) (byDim[f.dimension] ??= []).push(f)
  const units = []
  for (const dim of Object.keys(byDim).sort()) {
    const shards = shardsFor(byDim[dim], SHARD_SIZE)
    shards.forEach((findings, i) => units.push({ dim, tag: shards.length > 1 ? `${dim}#${i + 1}` : dim, findings }))
    if (shards.length > 1) log(`${dim}: ${byDim[dim].length} findings > ${SHARD_SIZE}, ${shards.length} triples split by finder seat`)
  }

  const verifier = (u, lens) => agent(
    `You are verifier V${lens.k} (${lens.name}) of dimension ${u.dim} in audit round ${round}; two other verifiers vote on the same findings from other containers -- do not coordinate numbers with them. Work in a fresh worktree: from ${repo} run git worktree add ../audit-r${round}-verify-${u.tag.replace('#', '-')}-v${lens.k} ${branch}. Read tools/audit/briefs/verifier.md and tools/audit/README.md there and follow them. Do not read the register's verdict columns, GitHub, or another verifier's report.
Every finding below gets your vote, refute-first, with an executed number (verifier.md steps 1-5 all apply). Your lens, run in full on every finding (verifier.md steps ${lens.steps}): ${lens.owns}.
Two refutes, each with an executed number, kill a finding at panel; a refute without one counts as unresolved, and so does a refute resting on a timing mismatch alone. Timing and memory numbers taken while other seats run are provisional: quote load1 and thread_factor beside them.
Findings (reports and harnesses under tools/audit/round${round}/${u.dim}/): ${JSON.stringify(u.findings.map((f) => ({ id: f.id, scope: seatOf(f), title: f.title, claim: f.claim, class_guess: f.class_guess, harness_paths: f.harness_paths, attached_refutation: f.attached_refutation })))}.
Write your report to tools/audit/round${round}/${u.dim}/verify-v${lens.k}${u.tag === u.dim ? '' : '-' + u.tag.split('#')[1]}.md and return JSON {votes: [{id, vote: "verify"|"weaken"|"refute"|"unresolved", severity, value, metric_definition, method, attacks, class, seam_rule_enumerates}]}; class and seam_rule_enumerates are V3's, null for the others.`,
    { label: `${u.tag}/v${lens.k}`, phase: 'Panels', schema: { type: 'object', required: ['votes'] } },
  )
  // A null verifier is re-run once; still null, its votes are missing and the
  // panel for its findings can at most be `split` or `disputed`, never killed by it.
  const triple = (u) => parallel(LENSES.map((lens) => async () => (await verifier(u, lens)) ?? (await verifier(u, lens))))

  phase('Panels')
  const panels = await pipeline(units, (u) => triple(u))
  toJudge = []
  units.forEach((u, i) => {
    const seats = panels[i] ?? []
    for (const f of u.findings) {
      const votes = LENSES.map((lens, j) => {
        const v = seats[j]?.votes?.find((x) => x.id === f.id)
        return v ? { lens: lens.name, ...normalise(v) } : null
      })
      const panel = panelOf(votes)
      tally[f.id] = { panel, votes: votes.map((v) => v?.vote ?? 'unvoted') }
      if (panel === 'killed') killed.push(f.id)
      else toJudge.push({ ...f, panel, votes: votes.filter(Boolean) })
    }
  })
  killed.sort()
  log(`panels done: ${units.length} triple(s), ${killed.length} killed at panel, ${toJudge.length} to the judge (${toJudge.filter((f) => f.panel === 'disputed').length} disputed)`)
} else {
  log(`args.from is "judge": panels skipped, ${toJudge.length} finding(s) go to the judge unvoted`)
}

phase('Judge')
const lease = `python3 tests/gate_lock.py take --label judge-r${round}; renew between commands; release at the end -- never mkdir`
const dedup = await agent(
  `You are the one common judge of audit round ${round}. Work alone on the quiet box in a fresh worktree: from ${repo}, git worktree add ../audit-r${round}-judge ${branch}. Read tools/audit/briefs/judge.md and follow it. Any measurement you take holds the gate lease: ${lease}.
This call is judge.md's first step only: DEDUP, across all dimensions, before any verdict. Cluster the findings below by instrumented symbol, files, phenomenon_property and class_guess (read each finding's full record from its report). In each cluster pick the canonical finding and merge another into it only where the canonical finding's perturbation moves the other's harness too -- quote that number; no number, no merge. Merged findings keep their ids ("merged into <id>").
Then write tools/audit/round${round}/JUDGE-INPUT.json: a JSON list of every canonical finding's full record in tools/audit/finding.schema.json's shape, which tools/audit/judge_batch.py reads. Where a harness header has no JUDGE-RUN / JUDGE-PERTURB / JUDGE-NULL / JUDGE-METRIC line (judge_batch.py's docstring gives the form), add a "judge_batch" object with the commands you derive from the header's prose, so the scripted re-run covers it; a perturbation you cannot express as a command is left out and re-run by hand.
Findings, each with its panel (unanimous, split, disputed, or unvoted) and votes:
<<FINDINGS>>${JSON.stringify(toJudge)}<</FINDINGS>>
Return JSON {canonical: [id], merged: [{id, into, number}], input_path}.`,
  { label: 'judge/dedup', schema: { type: 'object', required: ['canonical', 'merged', 'input_path'] } },
)
if (!dedup) throw new Error('judge dedup failed (agent returned null); relaunch to re-run it')

const runnerRows = await parallel(Array.from({ length: runners }, (_, i) => () => agent(
  `You are a mechanical re-run runner for audit round ${round}'s judge: you measure, you do not decide. On a quiet box, fresh worktree from ${repo}: git worktree add ../audit-r${round}-runner-${i + 1} ${branch}. Run, from the worktree root:
python3 tools/audit/judge_batch.py --input ${dedup.input_path} --label judge-r${round}-runner${i + 1}${runners > 1 ? ` --shard ${i + 1}/${runners}` : ''} --out-json tools/audit/round${round}/judge-batch-${i + 1}.json --out-md tools/audit/round${round}/judge-batch-${i + 1}.md
It takes and releases the gate lease itself and runs every command serially. Read its exit code; do not edit a row. Return JSON {table, rows, rc}.`,
  { label: `judge/runner-${i + 1}`, schema: { type: 'object', required: ['table', 'rows'] } },
)))

const judge = await agent(
  `You are the judge of audit round ${round}, continuing in ../audit-r${round}-judge (from ${repo}) after your dedup (${JSON.stringify(dedup)}). Hold the gate lease for any measurement: ${lease}.
The scripted re-runs are in ${JSON.stringify(runnerRows.map((r) => r?.table ?? null))} (one row per canonical finding, with load1 and thread_factor; a null entry is a runner that died -- run judge_batch.py for its shard yourself). Read every row. Re-run by hand every finding whose row is disputed at panel, void, by-hand, not reproduced, flagged for a re-take (thread_factor > 1.05), or whose null control is by-hand. Then follow judge.md steps 1-7 for every canonical finding: compare the finder's and the verifiers' metric definitions, leave-one-out on aggregates, the null control on cost, gain and time claims, stop_rule_class from the number, and a class for every survivor: a tools/audit/bugclasses.json id, or a new one (P13..., I6...) with its mechanism in one line.
Write tools/audit/round${round}/JUDGE.md and JUDGE.json and return JSON {verdicts: [{id, verdict: "verified"|"weakened"|"refuted"|"unreproduced", severity, value, stop_rule_class, class, class_mechanism, note}]} for the canonical findings.`,
  { label: 'judge', schema: { type: 'object', required: ['verdicts'] } },
)
if (!judge) throw new Error('judge failed (agent returned null); relaunch to re-run the judge')

const verdicts = [...(judge.verdicts ?? []), ...(dedup.merged ?? []).map((m) => ({ id: m.id, verdict: 'merged', into: m.into, note: `merged into ${m.into}: ${m.number}` }))]

// The rotation ledger's yield: judge-surviving findings per method step, per
// dimension, counted here rather than by an agent; a merged finding counts once,
// under its canonical id. tools/audit/rotation.json keeps it beside the coverage,
// unfinished steps, findings per seat and leads that audit-find.js's intake
// records, so round 10 is judged against round 9 with numbers (PLAN section 10).
const SURVIVES = new Set(['verified', 'weakened'])
const verdictOf = Object.fromEntries(verdicts.map((v) => [v.id, v.verdict]))
const rotationYield = {}
for (const f of [...reg.findings].sort((a, b) => String(a.id).localeCompare(String(b.id)))) {
  const y = (rotationYield[f.dimension] ??= {})
  const m = /^D\d+\.(M\d+)$/.exec(f.step ?? '')?.[1]
  if (m && SURVIVES.has(verdictOf[f.id])) y[m] = (y[m] ?? 0) + 1
  else if (!m) log(`${f.id} names no method step; it counts toward no step's yield`)
}
const sortedYield = Object.fromEntries(Object.keys(rotationYield).sort().map((d) => [d, rotationYield[d]]))

phase('Class sweep')
const byClass = {}
for (const v of judge.verdicts ?? []) if (SURVIVES.has(v.verdict)) (byClass[v.class ?? 'unclassified'] ??= []).push(v)
const classIds = Object.keys(byClass).sort()
const sweeps = await pipeline(classIds, (cls) => agent(
  `You are the class-sweep seat for class ${cls} of audit round ${round} (PLAN phase D). Fresh worktree from ${repo}: git worktree add ../audit-r${round}-sweep-${cls} ${branch}. Read tools/audit/briefs/D14.md and run its method steps 3-4 for this class: an enumerator listing every seam of the class across the whole package (start from the findings' seam_rules), its positive control (it re-finds every finding below), its null control (zero on a clean fixture) and its perturbation (it moves under a one-line re-introduction); then disposition every seam it returns as instance (with a probe that fails on it), guarded (name the guard) or not applicable (the reason). Read the class's status in tools/audit/bugclasses.json.
Findings in the class: ${JSON.stringify(byClass[cls])}.
Write tools/audit/round${round}/sweep-${cls}.md and return JSON {class, instances, barriered, enumerator, instance_list: [{file, symbol, probe}]}; instances counts confirmed instances that are NOT among the findings above.`,
  { label: `sweep/${cls}`, phase: 'Class sweep', schema: { type: 'object', required: ['instances', 'barriered', 'enumerator'] } },
))
const classes = classIds.map((cls, i) => {
  const s = sweeps[i]
  const n = byClass[cls].length + Number(s?.instances ?? 0)
  return { class: cls, findings: byClass[cls].map((v) => v.id), sweep_instances: s?.instance_list ?? [], enumerator: s?.enumerator ?? null, swept: Boolean(s), n, rca: rcaOwed(n, Boolean(s?.barriered)) }
})
for (const c of classes) if (!c.swept) log(`class ${c.class}: the sweep seat returned nothing; its count is the judged findings alone and the issue must say the sweep is owed`)

phase('Issues and register')
const writer = await agent(
  `Record the outcome of audit round ${round} verification. In ${repo} on ${branch}: update the Round ${round} register tables in docs/audit-2026-09.md with each verdict from ${JSON.stringify(verdicts)} and each finding's panel ${JSON.stringify(tally)} (killed at panel: ${JSON.stringify(killed)}); add today's date to the section header; commit tools/audit/round${round}/ verifier, judge, judge-batch and sweep reports. In tools/audit/rotation.json set rounds["${round}"].yield for each dimension to exactly ${JSON.stringify(sortedYield)} (a dimension's map replaces its yield whole; keys sorted, two-space indent, trailing newline).
One issue per class, not per finding (PLAN section 8.1). Classes: ${JSON.stringify(classes)}. Write tools/audit/round${round}/ISSUES.json: per class {class, title: "[R${round}-<class>] <mechanism>", labels: ["audit", "round-${round}", "class:<class>", "sev:<highest severity in the class>"], body}, the body carrying the class mechanism, each finding (id, severity, harness, verdict), each sweep instance, the enumerator command, and "RCA: owed" when rca is true or "RCA: not triggered (N=<n>)". Write the draft roster .claude/workflows/wave-r${round}-groups.json: one group per class with its issue (null until filed), its file set from the sweep, after dependencies, and the RCA flag; run node .claude/workflows/brief_lint.mjs and read its exit code and error lines, not the summary.
${fileIssues ? `Filing is on (args.file): as tvofi, for each class run gh issue list --search "\\"[R${round}-<class>]\\" in:title" and skip one that exists, else create it; put the numbers in ISSUES.json, the register rows and the roster.` : 'Do not file issues, push, or open a pull request: filing and pushing are the Mac seat\'s (decision 0011). Commit on the branch and stop.'}
Return JSON {issues: [{class, number}], issues_path, roster, brief_lint_rc}.`,
  { label: 'register', schema: { type: 'object', required: ['issues'] } },
)
return { panel: { killed, tally }, dedup, verdicts, classes, writer, rotation_yield: sortedYield }
