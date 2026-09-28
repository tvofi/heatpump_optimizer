// Adversarial verification of one round's findings: ONE verifier per dimension
// (given only the findings and their harnesses; it re-runs and attacks the
// finder's harness AND measures each finding with one it writes itself), then
// one common judge who re-measures every finding, then issues and the register.
// With one vote nothing is killed at panel: every finding reaches the judge
// (round 8, the owner's panel shape; rounds 1-7 ran three verifiers per panel
// and killed by majority refute).
// args.from selects where the pass starts: "panels" (default) runs all four
// phases; "judge" skips the verifier phase and hands the judge every reported
// finding directly, unvoted -- for a relaunch once the verifiers already ran
// elsewhere, or when a verifier pass is known unnecessary.
//
//   /audit-verify with args {round: 2, repo: "<abs path>", branch: "claude/audit-r2-register", from: "panels"}
export const meta = {
  name: 'audit-verify',
  description: 'One verifier per dimension, no panel kill, one judge re-measuring every finding, issues',
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
  `In ${repo}, check out ${branch}. Read the Round ${round} findings register in docs/audit-2026-09.md and every tools/audit/round${round}/D*/REPORT.md. Return JSON {findings: [{id, dimension, step, severity, title, claim, report_path, harness_paths: [..], attached_refutation: string|null}]} for every finding with status reported; step is the brief's method step the finder's report names for it (D<k>.M<n>), null if it names none. Do not include corroborations of open issues.`,
  { label: 'read', schema: { type: 'object', required: ['findings'] } },
)
if (!reg) throw new Error('register read failed (agent returned null); relaunch')

let tally = {}
if (from === 'panels') {
  const byDim = {}
  for (const f of reg.findings) (byDim[f.dimension] ??= []).push(f)
  const dims = Object.keys(byDim).sort()

  const verifier = (dim) => agent(
    `You are the one verifier for dimension ${dim} of audit round ${round}. Work in a fresh worktree: from ${repo} run git worktree add ../audit-r${round}-verify-${dim} ${branch}. Read tools/audit/briefs/verifier.md and tools/audit/README.md there and follow them. Do not read the register's verdict columns or GitHub.
Findings to verify (each has its report and harnesses under tools/audit/round${round}/${dim}/): ${JSON.stringify(byDim[dim].map((f) => ({ id: f.id, title: f.title, claim: f.claim, harness_paths: f.harness_paths, attached_refutation: f.attached_refutation })))}.
You carry both halves of the contract for every finding: re-run the finder's harness and attack the method, AND measure it with a harness you write yourself beside the finder's, printing your own RESULT lines.
Timing and memory numbers taken while other agents run are provisional: cite only counts, bytes and ratios for those, and mark a timing-based refute as unresolved.
Write your report to tools/audit/round${round}/${dim}/verify.md and return JSON {votes: [{id, vote: "verify"|"weaken"|"refute"|"unresolved", severity, value, metric_definition, method, attacks}]}.`,
    { label: `${dim}/verify`, schema: { type: 'object', required: ['votes'] } },
  )

  phase('Panels')
  const seats = await pipeline(dims, (dim) => verifier(dim))
  // A null verifier is re-run once; still null, its findings reach the judge unvoted.
  for (let i = 0; i < dims.length; i++) if (!seats[i]) seats[i] = await verifier(dims[i])
  for (const [i, dim] of dims.entries()) {
    for (const f of byDim[dim]) {
      const vote = seats[i]?.votes?.find((v) => v.id === f.id) ?? null
      tally[f.id] = { vote: vote?.vote ?? 'unvoted', detail: vote }
    }
  }
  log(`verifiers done: ${dims.length} dimension(s), ${Object.keys(tally).length} finding(s), all to the judge (one vote kills nothing)`)
} else {
  log(`args.from is "judge": verifier phase skipped, ${reg.findings.length} finding(s) go to the judge unvoted`)
}

phase('Judge')
const judge = await agent(
  `You are the judge of audit round ${round}. Work alone on the idle box: python3 tests/gate_lock.py take --label judge-r${round} first, renew between commands, release at the end -- never mkdir and a shell pid (#404: that lock carries no lease and no flock). Fresh worktree from ${repo}: git worktree add ../audit-r${round}-judge ${branch}. Read tools/audit/briefs/judge.md and follow it for every finding below. ${from === 'judge' ? `No verifier ran this pass (args.from: "judge"); findings, unvoted: ${JSON.stringify(reg.findings)}.` : `Every finding, each with its one verifier vote (nothing was killed at panel): ${JSON.stringify(reg.findings.map((f) => ({ ...f, verifier: tally[f.id] ?? { vote: 'unvoted', detail: null } })))}.`}
For every finding: re-run the harness, run the perturbation (void the harness if the number does not move), compare the finder's and the verifier's metric definitions, re-run leave-one-out and null controls, reject RESULTs at load1 > 1.5 or thread_factor > 1.05, assign stop_rule_class from the number.
Write tools/audit/round${round}/JUDGE.md and return JSON {verdicts: [{id, verdict: "verified"|"weakened"|"refuted"|"unreproduced", severity, value, stop_rule_class, note}]}.`,
  { label: 'judge', schema: { type: 'object', required: ['verdicts'] } },
)

if (!judge) throw new Error('judge failed (agent returned null); relaunch to re-run the judge')

// The rotation ledger's yield: judge-surviving findings per method step, per
// dimension, counted here from the verdicts rather than by an agent. It is what
// audit-find.js's dispatch rule reads as `yield` (tools/audit/rotation.json); a
// step absent from a dimension's map yielded zero. Like the coverage audit-find.js
// hands its dedup agent, it reaches the file through the register writer.
const SURVIVES = new Set(['verified', 'weakened'])
const verdictOf = Object.fromEntries((judge.verdicts ?? []).map((v) => [v.id, v.verdict]))
const rotationYield = {}
for (const f of [...reg.findings].sort((a, b) => String(a.id).localeCompare(String(b.id)))) {
  const y = (rotationYield[f.dimension] ??= {})
  const m = /^D\d+\.(M\d+)$/.exec(f.step ?? '')?.[1]
  if (m && SURVIVES.has(verdictOf[f.id])) y[m] = (y[m] ?? 0) + 1
  else if (!m) log(`${f.id} names no method step; it counts toward no step's yield`)
}
const sortedYield = Object.fromEntries(Object.keys(rotationYield).sort().map((d) => [d, rotationYield[d]]))

phase('Issues and register')
const writer = await agent(
  `Record the outcome of audit round ${round} verification. In ${repo} on ${branch}: update the Round ${round} register tables in docs/audit-2026-09.md with each verdict from ${JSON.stringify(judge.verdicts)} and the verifier's vote per finding ${JSON.stringify(Object.fromEntries(Object.entries(tally).map(([k, t]) => [k, t.vote])))}; add today's date to the section header; commit tools/audit/round${round}/ verifier and judge reports. In tools/audit/rotation.json set rounds["${round}"].yield for each dimension to exactly ${JSON.stringify(sortedYield)} (a dimension's map replaces its yield whole; keys sorted, two-space indent, trailing newline) and commit it.
Then open one GitHub issue per finding whose verdict is verified or weakened, using the template in the register's front matter (title "[R${round}-<id>] <claim>", labels audit, round-${round}, dim:<D>, sev:<severity>, plus regression where the register says so). Before each create, run gh issue list --search "\\"[R${round}-<id>]\\" in:title" and skip if it exists. The id namespace restarts every round, so a bare [<id>] search matches closed findings from earlier rounds and skips every issue. Refuted and unreproduced findings get no issue. Append the issue numbers to the register rows and to the round-${round} tracking issue's table (gh issue list --search "Audit — round ${round}" in:title). Commit and push the branch; open a PR titled "Audit round ${round}: register and harnesses" if none exists for it.
Return JSON {pr, issues: [{id, number}], skipped: [id]}.`,
  { label: 'register', schema: { type: 'object', required: ['issues'] } },
)
return { tally, verdicts: judge.verdicts, writer, rotation_yield: sortedYield }
