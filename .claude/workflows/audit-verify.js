// Adversarial verification of one round's findings: three verifiers per
// panel (each given only the finding and its harness), majority-refute kills,
// then a judge who re-measures every survivor, then issues and the register.
// args.from selects where the pass starts: "panels" (default) runs all four
// phases; "judge" skips the panel phase and hands the judge every reported
// finding directly, unvoted — for a relaunch once panels already ran
// elsewhere, or when a panel pass is known unnecessary. Behaviour under the
// default "panels" is unchanged.
//
//   /audit-verify with args {round: 2, repo: "<abs path>", branch: "claude/audit-r2-register", from: "panels"}
export const meta = {
  name: 'audit-verify',
  description: 'Three-verifier panels per finding group, majority-refute kill rule, judge re-measurement, issues',
  phases: ['Read the register', 'Panels', 'Judge', 'Issues and register'],
}

const round = args?.round ?? 2
const repo = args?.repo
const branch = args?.branch ?? `claude/audit-r${round}-register`
const from = args?.from ?? 'panels'
if (!repo) throw new Error('args.repo is required')
if (from !== 'panels' && from !== 'judge') throw new Error('args.from must be "panels" or "judge"')

phase('Read the register')
const reg = await agent(
  `In ${repo}, check out ${branch}. Read the Round ${round} findings register in docs/audit-2026-09.md and every tools/audit/round${round}/D*/REPORT.md. Return JSON {findings: [{id, dimension, severity, title, claim, report_path, harness_paths: [..], attached_refutation: string|null}]} for every finding with status reported. Do not include corroborations of open issues.`,
  { label: 'read', schema: { type: 'object', required: ['findings'] } },
)
if (!reg) throw new Error('register read failed (agent returned null); relaunch')

let tally = {}
if (from === 'panels') {
  const byDim = {}
  for (const f of reg.findings) (byDim[f.dimension] ??= []).push(f)
  const panels = []
  for (const dim of Object.keys(byDim).sort()) {
    const list = byDim[dim]
    for (let i = 0; i < list.length; i += 8) panels.push({ dim, findings: list.slice(i, i + 8), index: i / 8 })
  }

  const verifier = (panel, seat) => agent(
    `You are verifier ${seat} of 3 on panel ${panel.dim}-${panel.index} of audit round ${round}. Work in a fresh worktree: from ${repo} run git worktree add ../audit-r${round}-verify-${panel.dim}-${panel.index}-${seat} ${branch}. Read tools/audit/briefs/verifier.md and tools/audit/README.md there and follow them. Do not read other verifiers' output, the register's verdict columns, or GitHub.
Findings to verify (each has its report and harnesses under tools/audit/round${round}/${panel.dim}/): ${JSON.stringify(panel.findings.map((f) => ({ id: f.id, title: f.title, claim: f.claim, harness_paths: f.harness_paths, attached_refutation: f.attached_refutation })))}.
${seat === 1 ? 'You are the seat that must measure with a harness you write yourself for every finding; write it beside the finder\'s and print your own RESULT lines.' : 'Re-run the finder\'s harness and attack the method; write your own harness where the finder\'s cannot be trusted.'}
Timing and memory numbers taken while other agents run are provisional: cite only counts, bytes and ratios for those, and mark a timing-based refute as unresolved.
Write your report to tools/audit/round${round}/${panel.dim}/verify-${panel.index}-${seat}.md and return JSON {votes: [{id, vote: "verify"|"weaken"|"refute"|"unresolved", severity, value, metric_definition, method, attacks}]}.`,
    { label: `${panel.dim}-${panel.index}/v${seat}`, schema: { type: 'object', required: ['votes'] } },
  )

  phase('Panels')
  const votes = {}
  for (const panel of panels) {
    let seats = await pipeline([1, 2, 3], (seat) => verifier(panel, seat))
    // A null verifier is re-run and never counted; three counted votes are the quorum.
    for (let s = 0; s < 3; s++) if (!seats[s]) seats[s] = await verifier(panel, s + 1)
    for (const f of panel.findings) {
      votes[f.id] = seats.filter(Boolean).flatMap((r) => r.votes.filter((v) => v.id === f.id))
    }
  }
  tally = Object.fromEntries(Object.entries(votes).map(([id, vs]) => {
    const refutes = vs.filter((v) => v.vote === 'refute').length
    const counted = vs.length
    return [id, { counted, refutes, killed: counted >= 3 && refutes * 2 > counted, votes: vs }]
  }))
  log(`panels done: ${Object.keys(tally).length} findings, ${Object.values(tally).filter((t) => t.killed).length} killed by majority refute`)
} else {
  log(`args.from is "judge": panel phase skipped, ${reg.findings.length} finding(s) go to the judge unvoted`)
}

phase('Judge')
const judge = await agent(
  `You are the judge of audit round ${round}. Work alone on the idle box: take /tmp/hpo-gate.lock with mkdir first and remove it at the end. Fresh worktree from ${repo}: git worktree add ../audit-r${round}-judge ${branch}. Read tools/audit/briefs/judge.md and follow it for every finding below. ${from === 'judge' ? `No verifier panel ran this pass (args.from: "judge"); findings, unvoted: ${JSON.stringify(reg.findings)}.` : `Votes as counted: ${JSON.stringify(tally)}.`}
For every survivor and every kill that rested on a number: re-run the harness, run the perturbation (void the harness if the number does not move), compare metric definitions across finder and verifiers, re-run leave-one-out and null controls, reject RESULTs at load1 > 1.5 or thread_factor > 1.05, assign stop_rule_class from the number.
Write tools/audit/round${round}/JUDGE.md and return JSON {verdicts: [{id, verdict: "verified"|"weakened"|"refuted"|"unreproduced", severity, value, stop_rule_class, note}]}.`,
  { label: 'judge', schema: { type: 'object', required: ['verdicts'] } },
)

if (!judge) throw new Error('judge failed (agent returned null); relaunch to re-run the judge')

phase('Issues and register')
const writer = await agent(
  `Record the outcome of audit round ${round} verification. In ${repo} on ${branch}: update the Round ${round} register tables in docs/audit-2026-09.md with each verdict from ${JSON.stringify(judge.verdicts)} and the vote counts ${JSON.stringify(Object.fromEntries(Object.entries(tally).map(([k, t]) => [k, `${t.counted - t.refutes}-${t.refutes}`])))}; add today's date to the section header; commit tools/audit/round${round}/ verifier and judge reports.
Then open one GitHub issue per finding whose verdict is verified or weakened, using the template in the register's front matter (title "[<id>] <claim>", labels audit, round-${round}, dim:<D>, sev:<severity>, plus regression where the register says so). Before each create, run gh issue list --search "\\"[<id>]\\" in:title" and skip if it exists. Refuted and unreproduced findings get no issue. Append the issue numbers to the register rows and to the round-${round} tracking issue's table (gh issue list --search "Audit — round ${round}" in:title). Commit and push the branch; open a PR titled "Audit round ${round}: register and harnesses" if none exists for it.
Return JSON {pr, issues: [{id, number}], skipped: [id]}.`,
  { label: 'register', schema: { type: 'object', required: ['issues'] } },
)
return { tally, verdicts: judge.verdicts, writer }
