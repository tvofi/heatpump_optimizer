# Fix review — R10-REPLAY-LANE (series instrument and the loop-work note)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and
`dev/governance/roles/COMMON.md` first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2514** (`fix/r10-replay-lane`), head `f0b1844bad38247e0a08f575b0208e78e3ff6537` at dispatch.
**The head is moving**: the orchestrator is recarrying main and adding the delivery row now. Review the deliverable
at `f0b1844b` and, when the update lands (poll `gh pr view 2514 --json headRefOid`), re-run only what the delta
touches and measure at the final head. Hold the verdict: no `bus-nonce` exists yet; the orchestrator sends one
bound to the final head.

Work from a detached worktree at the head you measure, under
`/Users/timmalmstrom/hpo-seats/r10s3/r10-replay-lane-review/` (scratch and evidence there; absolute paths).
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. Long runs detached via
`tools/audit/seat/daemonize.py --log`; the gate lease is shared. The box is loaded: state load1 beside wall-clock
numbers and prefer counts.

## What this is

The nightly replay lane's series instrument is corrected so it reads two ruler eras rather than one mixed series
(the nightly ruler changed with #2339), the cross-runner comparison the group's carry asked for is recorded, and the
`loop_cpu_ratio` note's invariance claim — falsified by the 2026-10-20 nightly — is corrected. It deliberately
does **not** raise `COST_BUDGETS` (a rule-2 raise is the owner's) and does **not** add a real recorded day (needs
an export from the owner's box). Both are carried under `## Forward-carry` to #2272.

## What to verify, with your own harness

1. **The series derivation.** Re-derive the two-era spreads from the same rows the body names
   (`dev/audit/harnesses/r10_replay_loopnorm.py --series`), or your own read of the same nightly job logs. The body
   claims pre-era BLAS 0.2441-0.4050 (1.659x), post-era pure-Python 0.0868-0.1114 (1.283x, median 0.0877), and the
   same five post rows under the BLAS figure 0.2599-0.4190. Pick at least one row per era and confirm its numbers
   against the run/job the body cites. A number you cannot re-derive is not verified — say so.
2. **The mutation proof.** Run the harness self-test at the head; then apply the body's mutation
   (`loop_cpu_ms / row["ref_ms"]` → `loop_cpu_ms / row["loop_ref_ms"]` in the post-era branch) to a copy and show
   the self-test fails with the named line. If it passes, the proof is vacuous and the PR is blocked.
3. **The null control.** The interleaved per-SHA comparison (`c3530277` vs `0c298f6b`, six runs each, medians
   0.0711/0.0701) is the arm that separates runner sensitivity from loop work. Re-run it, or state precisely why
   you could not and what that costs the claim. A figure that did not move is the confirmable result.
4. **The red-check claim.** The body says the branch turns no check red and that the standing `slow`-job
   `loop_cpu_ratio` red belongs to main. Read the head's check-runs yourself; verify the diff does not touch
   `COST_BUDGETS` or `tests/replay.py`'s budget table, and that the cited run 39387919507/job 118512165515 is the
   main-side red it claims (commit at that job's head vs this branch).
5. **The owner boundary.** Confirm the diff touches no `.github/workflows/` file (the body's owner-review claim)
   and that the cap re-record is genuinely left unperformed — `COST_BUDGETS` byte-identical to the base.
6. **The carries.** `carry_audit.py check --body` prints 0 unrouted; #2272 exists and is live; the four carried
   items are real (no `hpo-replay/1` document in `tests/replay/`; the new-file classification; the #2271 credential
   refusal). Verify each destination rather than the claim.
7. **Structure and gate.** `tests/structure.py` passes; the scoped gate's mode line is as stated; note that
   `PREPR_SKIP_CLOSURES=1` means the closures re-recording is CI's — check the body says so and that the diff adds
   no read.

Post the verdict with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` once the nonce
arrives. No host path in the verdict (#2310) — write `~/…`. Report under 250 words: verdict line, each item
confirmed/not, what you could not establish.
