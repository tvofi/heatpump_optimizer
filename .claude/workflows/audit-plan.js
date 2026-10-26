// P3 of every audit round (decision 0015), between `audit-verify` and the fix
// wave: one architect/planner seat, then one architecture-plan reviewer.
//
//   Input    `audit-verify`'s class-grouped draft roster, the verified register
//            and issue drafts, the D7 brief, bugclasses, and the fork's own
//            measurements. The draft roster is an input and is never
//            dispatched as it stands (`architect-planner.md`, Inputs).
//   Plan     `architect-planner.md` steps 1-9: the component view and quality
//            scenarios at the fork, every verified finding triaged once
//            (keep/merge/defer/refuse), groups by owning seam, ADRs, the moves
//            to the programme target with a predicted dS per metric, each
//            move's fitness functions, the roster and the risks.
//   Review   `plan-review.md` attacks the plan at its handoff SHA; only
//            `Plan review: approve` sends it to the owner. Two revise rounds at
//            most, then the owner receives the open points, never a third.
//   Hand off dev/audit/rounds/round<N>/PLAN/ (PLAN.md, PLAN.json, ADRs) and the
//            roster `.claude/workflows/wave-r<N>-groups.json` on ref `plan/r<N>`.
//            P4 executes that plan and records deviations against it
//            (`orchestrator.md` section 2b).
//
//   /audit-plan with args {round: 11, repo: "<abs path>", fork: "<sha>", branch: "<register branch>"}
//
// args.draft overrides the draft roster path; args.target_ds overrides the
// programme target the plan is projected against. The workflow pushes the plan
// ref and never a pull request: opening one is the orchestrator's (decision
// 0011). Its plan is machine-read by tools/audit/seat/plan_audit.py, whose
// `ledger` reconciles each group's `## Architecture score` block against
// PLAN.json's moves at the stamp.
export const meta = {
  name: 'audit-plan',
  description: 'P3: the architect/planner seat and the plan reviewer between audit-verify and the fix wave; the roster draft, ADRs and move plan on plan/r<N>',
  phases: ['Read the draft', 'Plan the architecture', 'Publish the plan', 'Plan review', 'Record the verdict'],
}

const round = args?.round ?? 11
const repo = args?.repo
const branch = args?.branch ?? `claude/audit-r${round}-register`
const fork = args?.fork
const draft = args?.draft ?? `.claude/workflows/wave-r${round}-groups.json`
const targetDs = Number(args?.target_ds ?? 22.7)
const planDir = `dev/audit/rounds/round${round}/PLAN`
const planRef = `plan/r${round}`
const worktree = `../audit-r${round}-plan`
if (!repo) throw new Error('args.repo is required')
if (!fork || !/^[0-9a-f]{7,40}$/.test(String(fork))) throw new Error('args.fork is required: the round\'s fork SHA')

// A workflow script imports nothing, so a collection read off a reply is
// parsed when it came back as JSON text and refused when it is not the
// collection named -- never read as empty (R10-TICK (e,h), audit-verify.js).
const replyField = (v, kind, what) => {
  let x = v
  if (typeof x === 'string') {
    try { x = JSON.parse(x) } catch { throw new Error(`${what}: the reply is text that does not parse as JSON (cut off?)`) }
  }
  const got = x === null ? 'null' : Array.isArray(x) ? 'array' : typeof x
  if (got !== kind) throw new Error(`${what}: the reply is ${got === 'undefined' ? 'missing' : `a ${got}`}, not an ${kind}`)
  return x
}

phase('Read the draft')
const draftRead = await agent(
  `In ${repo}, work in a fresh worktree off ${branch}: git worktree add --force ${worktree} ${branch} (if it already exists, reuse it and reset it to origin/${branch}). Read dev/governance/roles/architect-planner.md, dev/governance/roles/plan-review.md, dev/audit/README.md and the D7 brief dev/governance/dimensions/D7.md there.
Read the class-grouped draft roster ${draft} and the verified register (dev/audit/rounds/round${round}/JUDGE.json and ISSUES.json, or the register section dev/programme/register/). This draft roster is P2's output and is NOT the round's roster: it is your input.
Measure the fork ${fork} once into the plan's evidence: run
  python3 tools/audit/seat/plan_audit.py snapshot --ref ${fork} --instrument ${fork} --out ${planDir}/holdouts/fork.json
(it takes minutes; run it detached with tools/audit/seat/daemonize.py and wait on its exit, then read the file). It records the fork's score vector and gate-only tripwires, structure budgets, behaviour inventory, mutation kill rate and change coupling -- the holdouts the plan must not regress.
Return JSON {draft_path, groups: [{group, issues, fixes, findings, severity, files, after, architect_note}], findings: [{id, dimension, severity, title, class, seam}], holdouts_path}. Refuse, by returning an empty groups array, if the draft roster is absent or carries no group: audit-verify must run first.`,
  { label: 'plan/read', schema: { type: 'object', required: ['groups', 'findings'], properties: { groups: { type: 'array', items: { type: 'object' } }, findings: { type: 'array', items: { type: 'object' } }, holdouts_path: { type: 'string' } } } },
)
if (!draftRead) throw new Error('the draft read failed (agent returned null); relaunch')
const groups = replyField(draftRead.groups, 'array', 'plan/read: groups')
const findings = replyField(draftRead.findings, 'array', 'plan/read: findings')
for (const g of groups) if (!g || typeof g.group !== 'string' || !g.group) throw new Error('plan/read: a draft group has no `group` id')
if (!groups.length) throw new Error(`the draft roster ${draft} is empty or absent: audit-verify's "Issues and register" phase writes it, and P3 does not invent one`)
log(`draft roster: ${groups.length} class group(s), ${findings.length} verified finding(s), fork holdouts ${draftRead.holdouts_path ?? '(unreported)'}`)

phase('Plan the architecture')
const architecture = await agent(
  `You are the architect/planner of audit round ${round}, in ${worktree} (from ${repo}). Read dev/governance/roles/architect-planner.md and follow it in full; this call is steps 1-4 (component view at the fork ${fork}, quality scenarios, triage, groups by owning seam), the next call is steps 5-9.
The draft roster (P2's, never dispatched): ${JSON.stringify(groups)}. The verified findings: ${JSON.stringify(findings)}. The fork's measurements, including the score vector the target is read against: ${planDir}/holdouts/fork.json.
Triage EVERY verified finding exactly once as keep, merge (same root at one seam, name the canonical id), defer (to which round and why) or refuse (back to the judge, with the reason). Group by owning seam, not by file or class: each group carries its findings, size, seam, hot files and an architect note, and its edges come from the prerequisite graph, never file order.
Write ${planDir}/COMPONENTS.md and ${planDir}/SCENARIOS.md. Return JSON {components: [name], scenarios: [{quality, scenario, sensitivity, tradeoff}], triage: [{id, verdict, into, round, reason}]}. Every finding id above must appear exactly once.`,
  { label: 'plan/architect', phase: 'Plan the architecture', schema: { type: 'object', required: ['components', 'scenarios', 'triage'], properties: { components: { type: 'array', items: { type: 'object' } }, scenarios: { type: 'array', items: { type: 'object' } }, triage: { type: 'array', items: { type: 'object', required: ['id', 'verdict'] } } } } },
)
if (!architecture) throw new Error('the architect failed (agent returned null); relaunch')
const triage = replyField(architecture.triage, 'array', 'plan/architect: triage')
const triaged = new Set(triage.map((t) => t.id))
const dropped = findings.map((f) => f.id).filter((id) => !triaged.has(id))
if (dropped.length) throw new Error(`the triage dropped ${dropped.length} verified finding(s) (${dropped.slice(0, 8).join(', ')}); every finding appears once, as keep, merge, defer or refuse`)

const moves = await agent(
  `You are the architect/planner of audit round ${round}, continuing in ${worktree} after your triage ${JSON.stringify(triage)}: architect-planner.md steps 5-9 (ADRs, the moves to the programme target, fitness functions, the roster, the risks).
Target: score.py --diff ${fork} <the round's stamp> reads dS >= ${targetDs} with the counters on, admissible end to end, at least three scored classes improving, and no metric supplying more than 40% of the dS. Plan findings first; where they fall short add refactor groups with no finding, each carrying its evidence and the scenario it serves. Every move names its metric(s), predicted dS per metric, its ADR and its fitness functions (structure budgets, gate-only tripwires, the behaviour inventory, mutation kill rate, change coupling, and any counter its metric can be gamed through). Never plan a move that deletes behaviour, renames or splits to dodge a counter, or edits the scorer.
EVERY group gets one move entry, including a finding group expected to be score-neutral ("metrics: {}, dS: 0"): the stamp's move ledger reconciles each merged PR's own Architecture score block against this plan, and a group with no entry reads as a dS no move explains.
Write the ADRs as ${planDir}/ADR-*.md (context, decision, alternatives, consequences, scenarios served) and ${planDir}/PLAN.md. Return JSON {groups: [{group, findings, size, seam, hot_files, after, architect_note}], moves: [{group, adr, metrics: {metric: predicted dS}, dS}], projected_dS, critical_chain: [group], depth, hours, risks: [{risk, check}]}.`,
  { label: 'plan/moves', phase: 'Plan the architecture', schema: { type: 'object', required: ['groups', 'moves', 'projected_dS'], properties: { groups: { type: 'array', items: { type: 'object', required: ['group'] } }, moves: { type: 'array', items: { type: 'object', required: ['group', 'metrics'] } }, projected_dS: { type: 'number' } } } },
)
if (!moves) throw new Error('the move plan failed (agent returned null); relaunch')
const planGroups = replyField(moves.groups, 'array', 'plan/moves: groups')
const planMoves = replyField(moves.moves, 'array', 'plan/moves: moves')
if (!planGroups.length) throw new Error('the plan returned no group; a round with verified findings cannot hand off an empty roster')
const planned = new Set(planMoves.map((m) => m.group))
const unplanned = planGroups.map((g) => g.group).filter((g) => !planned.has(g))
if (unplanned.length) throw new Error(`the plan leaves ${unplanned.length} group(s) with no move entry (${unplanned.slice(0, 8).join(', ')}); the move ledger reconciles every merged group, so a neutral group is "metrics: {}, dS: 0"`)
if (Number(moves.projected_dS) < targetDs) log(`PROJECTED SHORT: ${moves.projected_dS} < ${targetDs}; the plan must say so with its options, not shrink the target quietly`)
const planJson = {
  round, fork, target_dS: targetDs, draft,
  components: architecture.components, scenarios: architecture.scenarios, triage,
  groups: planGroups, moves: planMoves, projected_dS: moves.projected_dS,
  critical_chain: moves.critical_chain ?? [], depth: moves.depth ?? null, hours: moves.hours ?? null,
  risks: moves.risks ?? [], holdouts: draftRead.holdouts_path ?? null,
}
const writePlan = await agent(
  `In ${worktree}, write ${planDir}/PLAN.json with exactly this content (it is the plan the move ledger reads at the stamp):\n${JSON.stringify(planJson, null, 1)}\nAlso write the round's roster draft to ${draft} in the form audit-verify writes it (one entry per group, with its issues, findings, severity, files, after, size and architect note; resume.stage "planned", resume.branch "handoff/R${round}-<topic>" per group). Run node tools/policy/brief_lint.mjs and return its exit code and error lines, not the summary.`,
  { label: 'plan/write', phase: 'Plan the architecture', schema: { type: 'object', required: ['brief_lint_rc'], properties: { brief_lint_rc: { type: 'integer' } } } },
)
if (!writePlan) throw new Error('the plan write failed (agent returned null); relaunch')
if (writePlan.brief_lint_rc !== 0) throw new Error(`the roster draft fails brief_lint (rc=${writePlan.brief_lint_rc}); fix it before review`)

phase('Publish the plan')
const publish = await agent(
  `In ${worktree}, commit ${planDir}/ and ${draft} with the subject "audit round ${round}: P3 plan" (no footer, no session link) and publish that commit as the constant ref ${planRef}: run tools/audit/seat/ref_privacy.py guard --ref ${planRef} first, then git push origin HEAD:refs/heads/${planRef} and read back origin's tip. A refused or failed push is returned, never forced. Do not open a pull request.
Return JSON {sha: <the published commit, 40 hex>, pushed: <bool>, readback: <string>, command: <the exact command line the orchestrator runs if pushed is false>}.`,
  { label: 'plan/publish', phase: 'Publish the plan', schema: { type: 'object', required: ['sha'], properties: { sha: { type: 'string' }, pushed: { type: 'boolean' }, readback: { type: 'string' }, command: { type: 'string' } } } },
)
if (!publish) throw new Error('the plan publish failed (agent returned null); relaunch')
if (!/^[0-9a-f]{40}$/.test(String(publish.sha))) throw new Error(`the plan publish returned ${JSON.stringify(publish.sha)}, not a 40-hex commit`)
let planSha = String(publish.sha)
log(`plan ${planRef} published at ${planSha}${publish.pushed === false ? ` (NOT PUSHED; the orchestrator runs: ${publish.command ?? '(no command returned)'})` : ''}`)

// The reviewer reviews the plan at its published SHA, and says which SHA it
// answered for: a verdict on a tree the ref no longer holds is not this plan's
// verdict (`plan-review.md`, "at that SHA").
phase('Plan review')
const reviewed = (v, sha, n) => {
  if (String(v.sha) !== sha) throw new Error(`plan/review-${n} answered for ${JSON.stringify(v.sha)}, the plan ref is at ${sha}; a review of another tree is not this plan's verdict`)
  return v
}
const review = (n, sha) => agent(
  `You are the architecture-plan reviewer of audit round ${round}, never the architect. In ${repo}, read the plan as published: git fetch origin ${planRef} then git worktree add --force ../audit-r${round}-review-${n} FETCH_HEAD (reuse and reset it if it exists). The plan is that tree -- ${planDir}/PLAN.json, PLAN.md and the ADRs -- at ${planRef} = ${sha}. Read dev/governance/roles/plan-review.md and attack the plan at that tree, one line per point:
1. recount the triage (every verified finding once, with a reason);
2. attack the three largest groups and the three on the critical chain (is the owning seam real in the code? is any edge a file order edge?);
3. re-derive each move's predicted dS from its prototype or prediction (a prediction resting on a renamed or split count, a deleted feature or a scorer change is metric-gamed);
4. check the target's conditions: admissible end to end, the spread rule, the holdouts named, fitness functions per move;
5. check the time: re-run the projection, the critical chain and the hot-file order;
6. check the ADRs against the scenarios.
Return JSON {verdict: "approve"|"revise", sha: "${sha}", points: [string]}.`,
  { label: `plan/review-${n}`, phase: 'Plan review', schema: { type: 'object', required: ['verdict', 'sha', 'points'], properties: { verdict: { type: 'string', enum: ['approve', 'revise'] }, sha: { type: 'string' }, points: { type: 'array', items: { type: 'string' } } } } },
)
let verdict = reviewed(await review(1, planSha), planSha, 1)
let revisions = 0
while (verdict.verdict === 'revise' && revisions < 2) {
  revisions += 1
  const revised = await agent(
    `You are the architect/planner of audit round ${round}, in ${worktree}. The plan reviewer returned revise at ${planSha} with these points: ${JSON.stringify(verdict.points)}. Address each one in ${planDir}/ (the ADRs and PLAN.md; update PLAN.json's moves and projected dS if a prediction changes), re-run the roster's brief_lint, then commit with the subject "audit round ${round}: P3 plan revision ${revisions}" and push it as the constant ref ${planRef} after tools/audit/seat/ref_privacy.py guard --ref ${planRef}, with git push origin HEAD:refs/heads/${planRef}; read back the ref's tip. Do not argue a point away without a measurement: the reviewer's next pass reads the plan, not your reply. Return JSON {sha: <the pushed commit, 40 hex>, addressed: [string]}.`,
    { label: `plan/revise-${revisions}`, phase: 'Plan review', schema: { type: 'object', required: ['sha', 'addressed'], properties: { sha: { type: 'string' }, addressed: { type: 'array', items: { type: 'string' } } } } },
  )
  if (!revised) throw new Error(`the revision ${revisions} failed (agent returned null); relaunch`)
  if (!/^[0-9a-f]{40}$/.test(String(revised.sha))) throw new Error(`revision ${revisions} returned ${JSON.stringify(revised.sha)}, not a 40-hex commit`)
  planSha = String(revised.sha)
  verdict = reviewed(await review(revisions + 1, planSha), planSha, revisions + 1)
}
const ownerDecision = verdict.verdict !== 'approve'
if (ownerDecision) log(`plan review did not approve after ${revisions} revision(s): the open points go to the owner, never to a third round: ${JSON.stringify(verdict.points)}`)

phase('Record the verdict')
const handoff = await agent(
  `Record the P3 verdict of audit round ${round} in ${worktree}. The reviewer's last verdict is ${JSON.stringify(verdict)} at ${planSha}${ownerDecision ? ' and it is NOT an approval: the owner decides with these open points, so say so in the file and the commit body' : ''}.
Write ${planDir}/REVIEW.md whose first line is exactly "Plan review: ${verdict.verdict} ${planSha}", followed by every point. Commit it with the subject "audit round ${round}: P3 plan verdict" (no footer, no session link) and push it as the constant ref ${planRef}: run tools/audit/seat/ref_privacy.py guard --ref ${planRef} first, then git push origin HEAD:refs/heads/${planRef} and read back the ref's tip. A refused or failed push is returned, never forced. Do not open a pull request.
Return JSON {ref: "${planRef}", sha: <the pushed verdict commit, 40 hex>, reviewed: "${planSha}", pushed: <bool>, readback: <string>, command: <the exact command line the orchestrator runs if pushed is false>}.`,
  { label: 'plan/verdict', phase: 'Record the verdict', schema: { type: 'object', required: ['ref', 'sha'], properties: { ref: { type: 'string' }, sha: { type: 'string' }, reviewed: { type: 'string' }, pushed: { type: 'boolean' }, readback: { type: 'string' }, command: { type: 'string' } } } },
)
if (!handoff) throw new Error('the plan verdict record failed (agent returned null); relaunch')
if (!/^[0-9a-f]{40}$/.test(String(handoff.sha))) throw new Error(`the verdict record returned ${JSON.stringify(handoff.sha)}, not a 40-hex commit`)
log(`plan ${planRef}: reviewed ${planSha}, verdict recorded at ${handoff.sha}${handoff.pushed === false ? ` (NOT PUSHED; orchestrator runs: ${handoff.command ?? '(no command returned)'})` : ''}`)

return {
  round, fork, draft, draft_groups: groups.length, findings: findings.length,
  triage, groups: planGroups, moves: planMoves, projected_dS: moves.projected_dS,
  target_ds: targetDs, target_met: Number(moves.projected_dS) >= targetDs,
  review: verdict, revisions, owner_decision: ownerDecision,
  plan: { ref: planRef, sha: handoff.sha, reviewed: planSha, pushed: handoff.pushed !== false, command: handoff.command ?? null },
  holdouts: draftRead.holdouts_path ?? null,
}
