# Fixer — prepr's `closures` step is CI's job, not every handoff's

Role: **fixer**, one change. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first:
failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim,
`GATE_SCOPE=auto`, `tests/structure.py` before the push, and the handoff freezes the branch.
Read `CLAUDE.md` rule 1 and `dev/governance/rules/gate-scoping.md` — this touches the gate.
**LOCAL seat only — no cloud.**

## The ask (tvofi, 2026-10-20)

Asked whether prepr's `closures` step is needed at all when CI runs `closures` as a required context, the owner
replied: **"yes, do that"** — make it default-skip off Linux, keep CI's gate plus `closures-autofix` as the owner,
and leave an opt-in for a lane that specifically needs a first-green head.

## The measurement this rests on (re-take it, do not quote mine)

- Across every prepr log on this box: **108 `ok`, 0 `FAIL`, 12 skip** for the `closures` step. It has never
  refused here.
- It is the dominant cost of a handoff. The replay-lane run's own plan
  (`derive.out`, 2026-10-20): `lane 1 (599.0s recorded): tests/features.py, tests/dst_checks.py`,
  `lane 2 (324.8s recorded): tests/entities.py`, `lane 3 (1.4s): tests/debug_collect.py` — ~925 s of recorded work,
  ~10 min critical path idle, and **24 min measured** on a box at load 77 with six preprs.
- The only thing the local run buys is avoiding a round trip: `closures-autofix` pushes the recording as a
  `GITHUB_TOKEN` bot commit, and a bot head has no `pull_request` run, so the required contexts never report,
  the train routes it serial as `bot-head`, and it needs a recarry.

## The change

In `tools/pr/prepr.sh`'s `closures_line`, the `scoped` arm records locally on any platform. Make that decision
platform-dependent:

- **Off Linux (Darwin and anything else): default to leaving the scoped recordings to CI** — print a `skip` line
  naming (a) that CI's `closures` context and `closures-autofix` own it, and (b) the opt-in below. Do not record.
- **On Linux: unchanged.** Every current decision stands.
- **The opt-in**: an environment variable that forces the local recording off Linux too, for a lane that
  specifically needs a first-green head. Name it in the printed skip line and in the rule.
- `full` and `skip` cases are already skips and must not change. The `left to CI:` reporting must stay truthful —
  a diff whose scoped recordings are all left to CI still says so, and the run still owes no recorder interpreter
  in that case (that is the existing `recorder_python` ordering; keep it).

The step's printed wording is what a later seat reads to decide whether to force a head through. It must say what
happened and how to override, not merely `skip`.

## Policy it must carry

If `dev/governance/rules/gate-scoping.md` (or any rule, brief or `orchestrator.md` section) names this step as
something a handoff always runs, update it in the same pull request — `finding-propagation.md` binds the producing
pull request. The owner rules the policy half under mandate 6175172275; say so in `## Approval` with the quote
above. Under 0012's moratorium this is an edit to an existing rule, never a new file.

## Controls

- **Failing test first**: the step's own `--self-test` (`prepr.sh --self-test`) must redden on a mutant that
  removes the platform guard before the fix, and pass after. Show the failing arm's line and its rc.
- **Mutation**: delete the off-Linux predicate → the off-Linux arm must fail its named check. Delete the opt-in
  override → the force arm must fail. A mutant that crashes instead of reddening is not a proof.
- **Null control**: with the opt-in set, and on the Linux arm, the step must still record and still refuse a
  closure that the recording does not cover — drive it with a stubbed `PREPR_RECORD` (the self-test already has
  one) so it runs offline. State both rcs.
- **The regression that matters**: a diff whose `closure.py affected` case is `full` or `skip` must behave
  byte-identically to today. Show both lines from your run.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/prepr-closures` (absolute). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/prepr-closures/wt -B handoff/r10-prepr-closures origin/main`.
`export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH` (the seat venv; never an ambient python3).
The box is loaded (8 cores, load 70+): state load1 beside every wall-clock figure, prefer counts, and run anything
long detached via `tools/audit/seat/daemonize.py --log`.
`tools/pr/prepr.sh` is **not** code-owned; the rule change is policy and I approve it under the mandate. Push code
to `handoff/r10-prepr-closures` and body to `handoff-body/r10-prepr-closures`; no host path (#2310).
Report under 200 words: what you changed, each control's rc, what you could not establish.
