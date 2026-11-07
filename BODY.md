R10-HOTFIX-SELFTEST-TIMEOUT. `governance / instrument-self-tests` ran its steps in line under `timeout-minutes: 30` and spent most of its wall time in five self-tests: prepr.sh's, beatd.py's, and pr_args.sh's alone and again through open_pr.sh and update_pr.sh, which each run it (open_pr.sh's `--self-test` arm, update_pr.sh's). Only prepr.sh's of the five keeps a core busy; the other four wait. They now start detached in the job's first step, each to its own log and exit-status file, and five steps at the end of the job, under their old names, print each log, fail on its status and grep the same tally lines. The job now lasts as long as the longer of its in-line steps and the detached work, instead of the sum of both. The timeout stays 30: no raise.

The three pr_args.sh callers run one after another in a single detached chain, and prepr.sh's self-test runs at `nice -n 10`. With all five at once, pr_args.sh's `mut:unlock` arm failed once in nine observations: it checks for a lock holder inside the 0.2 s poll the holder takes to notice that its parent has gone, and CPU contention shortens that window. Chained, they keep the order they had in line (figures).

Alternatives, and why each lost:
- **Matrix shards** of the job would rename its check runs to `governance / instrument-self-tests (<shard>)`. That name is read in tools/pr/ci_predict.py's `JOB` table and by tools/audit/round4/D11/governance_cost.py's `bare()`, and each shard repeats checkout. Separate jobs fail tests/entities.py's census, which ties governance.yml job ids to governance_cost.py's `GOV`, until a file outside this group names them.
- **Dropping the standalone pr_args.sh step** would remove a step, which the null control forbids, and would leave pr_args.sh's tally to two callers outside this file.
- **Cutting prepr.sh's own cost** was not needed for the headroom. It is about 400 CPU-s of work, and the detached run already removes it from the critical path.

`bg_wait` fails a test whose launcher exited with no status, instead of waiting out the timeout. The launcher writes each status through a temporary file and `mv`, so a reader never sees a partial status.

Repair round 2 (review blocked d6482b704, mutation-vacuous). Mutant X8, `return 0` after `bg_wait`'s `sleep 5`, survived every arm, because each arm's command had finished or been killed before its `bg_wait` ran. The prepr waiter step is `bg_wait prepr` with no tally grep, so under X8 it would pass while prepr.sh's self-test was still running, or after a late failure. The harness now has a still-running arm: a slow command that exits 5, waited on with no grep as the prepr step is, with a slow pass as its null control. X8 is in the harness's mutant list. The workflow is unchanged in this round: the arm needed no change to it.

## Head

Measured at 6301ec8864e229b27c9d65964ef65bb2d8b5e201: the reviewed head d6482b704bb11831c12001ffc0b0210a47c35483, merged with origin/main 28d46c4918285d36c409c1fb2f72eb77e04e569e (origin/main had not moved at handoff, so the one prepr.sh run stands), plus the harness commit 6301ec8864e229b27c9d65964ef65bb2d8b5e201. The new head changes only dev/audit/harnesses/r10_selftest_timeout.py against d6482b704, apart from main's own commits. Every gate figure below is re-taken there.

## Mutation proof

`python3 dev/audit/harnesses/r10_selftest_timeout.py` reads the `bg_run`/`bg_pid`/`bg_start`/`bg_wait` library out of the launcher step as committed and drives it over planted commands. At the new head:
- M0, the library as committed: all 10 arms PASS, the new `refuse slow bad` and `control slow ok` included.
- M1, `bg_wait` returning 0 in place of the recorded status: KILLED by `refuse slow bad`, `refuse chained bad` and `refuse bad`.
- M2, `bg_wait` returning 0 for a launcher gone with no status: KILLED by `refuse chain killed` and `refuse killed`.
- X8, `bg_wait` returning 0 after its first poll finds the command still running: KILLED by `refuse slow bad`.
- `RESULT survivors=0`, rc 0.

Failing first: with X8 in the mutant list but before the arm, the same command printed `X8 SURVIVED`, `RESULT survivors=1`, rc 1. That is the reviewer's finding, reproduced.

A missing tally is refused by the grep each waiter step keeps (arm `refuse notally`).

## Null control

- Each refusal arm has its passing control in the same run (`control ok`, `control tally`, `control chained tally`, `control slow ok`). A library that refused everything fails them. `control slow ok` is waited on while still running, so it also exercises the still-running poll.
- Every one of the job's steps still runs and still greps its `checks, 0 failed` line. The five waiter steps keep the five step names, and their grep lines are byte-identical to the base's.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `118 self-testing, 118 wired, 0 unwired`, so the move dropped no self-test's run line.
- The base workflow replays the same steps in line, which is the before figure.

## Figures

- CI before, main run 42297617709: job 1785 s; prepr 321, beatd 275, PR opener 199, PR argument builder 199, PR updater 198. Main run 42291959742: job 1759 s; 332, 274, 194, 194, 194. Seconds are completedAt minus startedAt: `gh run view 42297617709 --json jobs --jq '.jobs[]|select(.name=="governance / instrument-self-tests")|.steps[]|[.name,.startedAt,.completedAt]|@tsv'`.
- CI after, at d6482b704 (the workflow is unchanged since): code run 42334641003 attempt 1, `governance / instrument-self-tests` job 128289649754, 03:40:04Z to 03:50:35Z, so 631 s of the 1800 s timeout (65% headroom). That is completedAt minus startedAt of the job, from `actions get_workflow_job`. The PR updater waiter step waited 90 s on the chain, so the chain is the critical path there.
- The five self-tests one after another, locally: 475, 280, 223, 223, 224 s wall (sum 1424). All five at once: 478 s, every tally `0 failed`. Each was timed with bash `time` around its command, e.g. `time bash tools/pr/prepr.sh --self-test`.
- Job replay, base: `python3 dev/audit/harnesses/r10_selftest_timeout.py replay <(git show 41aa9050f:.github/workflows/governance.yml) all` gives `RESULT replay_seconds=1870 failed=0`. Job replay, head: the same with `.github/workflows/governance.yml` gives `replay_seconds=737`, `744` and `702`, `failed=0` each. Those were taken in round 1. Re-taken at the new head 6301ec886, the head replay gives `RESULT replay_seconds=702 failed=0`. The prepr, PR opener, PR argument builder and supervised beat waiter steps took 0.0 s each, and the PR updater waiter 55.0 s, so the pr_args chain is the critical path, as in CI.
- `mut:unlock` (pr_args.sh's check `mutant mut:unlock (its line deleted): the holder is still alive when the run returns`): with all five at once, 1 FAIL in 9 local observations. Chained, locally at the round-1 head, 9 of 9 PASS. Under real CI load, every CI run of d6482b704 that ran this job was read: there is exactly one, code run 42334641003. Its edit run 42334895114 skips the governance leg, and the earlier runs on this branch, 42334622520, 42334625513 and 42334640553, were at c8e3e7d0b and were cancelled as superseded. In that one run all three pr_args.sh waiter steps passed their `pr_args self-test: [1-9][0-9]* checks, 0 failed` grep. The update_pr.sh log tail reads `pr_args self-test: 174 checks, 0 failed`, so that is 3 of 3. Together that is 12 of 12 chained. Twelve passes bound the rate only to below about one in four (95%), so it is not a measured rate. It is carried below.
- Harness at the new head: `python3 dev/audit/harnesses/r10_selftest_timeout.py` gives `RESULT survivors=0`, rc 0, in 66 s wall (bash `time`).
- Scoped gate at the new head: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, and rc 0. Both scripts passed: tests/entities.py (420 s) and tests/harness_headers.py (122 s). So did run_always's env_drift `--claims-only`, `closure.py selftest` and `layout.py`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

The concluded reds of the previous head d6482b704, over every check-run page:
- `gate` in edit run 42334895114, attempt 1, job 128290201311 (failure at 03:41:45Z). The edit run's `Judge this head` step ran while the code run at the same head was still in flight, so it failed by deferral, not on a check. Attempt 2 (job 128299179386) concluded success at 04:20:49Z, once the code run had ended green. No code answer is owed.
- `governance / instrument-self-tests` cancelled at its 30-minute timeout, the stall this PR cures. The brief cites run 42332778588 (attempts 1 to 4) as this head's code run. It is not: `actions get_workflow_run 42332778588` names PR #3265, branch fix/r10-hotfix-plan-lanes, head c7c5cef52. That run is another pull request meeting the timeout this PR removes, and so it is this PR's motivation, not a red of its head. The head's own code run, 42334641003, concluded success, with the job at 631 s.

At the new head 6301ec8864e229b27c9d65964ef65bb2d8b5e201 no run has concluded at handoff. Its first `governance / instrument-self-tests` run is the probe for the harness change, which touches no workflow line.

## Forward-carry

- pr_args.sh's `mut:unlock` arm passes only while its checker runs `kill -0` within the lock holder's 0.2 s parent poll, so CPU load can turn it red. Measured: 1 in 9 with all five self-tests at once, and 12 of 12 chained (9 local, 3 in the one CI run of the head). That is not enough to bound a residual rate on main, where a red cancels a merge-train slot. The deterministic arm belongs to pr_args.sh, which this group does not own. Of the item's two routes I took the measurement, because it is the cheaper one this seat can take honestly. The other route, an append-carry landed on the roster, is closed to a fixer seat: `roster_edit.py append-carry` is a structural op refused outside `HPO_ROSTER_LANE=queue-runner` and written only by roster_queue.py, and this seat writes no branch but its return refs. The carry is routed here for the queue runner to land on R10-HANDOFF-PATH, whose resume names update_pr.sh, open_pr.sh and pr_args.sh as one owning seam. Carry text: make pr_args.sh's `mut:unlock` arm deterministic under CPU load (wait for the holder's exit or poll with a bound, not one `kill -0` inside the holder's 0.2 s parent poll); measured 1 FAIL in 9 with five self-tests concurrent, 12 of 12 chained. Carry: R10-HANDOFF-PATH

- Carry 1 (roster, orchestrator evidence 2026-11-07: #3262 and #3265 each cancelled at the 30-minute job timeout; the fixer re-measures the self-test wall time at its own base): re-measured at the new head 6301ec886, whose workflow is byte-identical to d6482b704's. The local job replay is 702 s, `failed=0`. The head's CI job, at the same workflow, was 631 s of 1800 s (Figures). #3262's and #3265's timeouts ran the base's in-line layout, which this PR replaces. Carry: dismissed: re-measured here, 702 s replay and 631 s CI under the 1800 s timeout

## Friction

- fixer.md-step-3: unenforced: a CI-time claim owes before and after on a probe run, but a fixer seat has no probe path. ci_probe.py takes only `ci-probe/*` refs, this seat may write no other branch, and `ci.yml` runs on no push but main's. The head's own code run 42334641003 is the probe, at 631 s. Carry: dismissed: the pull request's own first run is the probe
- brief-run-citation: stale: the brief named run 42332778588 as this head's code run, and it is PR #3265's (see Red checks). Carry: dismissed: corrected in this body
