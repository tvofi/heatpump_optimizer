HOTFIX (R10 batch 246, P744), repair round after "Fix review: blocked 8a05961b" (probe/revt-r10-hotfix-macos-selftest-lane-dfbc393a). Main CI is Linux-only, so a Darwin-only self-test regression (PR 3475: `mutant_run.py` listing /proc) was found only when an opener failed. This adds a `darwin-selftest` beat row: Darwin hosts only, one cycle per new origin/main tip, heavy-slot lease per pass, a detached worktree the row owns, `prepr.sh --self-test` plus each wired seat self-test, one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green. No workflow file touched (owner ruling 2026-11-12: macOS checks are local seats or beat rows). It detects after merge and does not prevent; a pre-merge arm is round 11.

This round was run on the Mac, so both blocked items are measured below. Those measurements exposed two lane defects in this group's own seam, and both are fixed in this head:
- One whole run took 80 to 109 min, which is past the row's beatd `timeout_s` of 3600. beatd would kill every pass, and because the tip was never remembered, the row would take the heavy slot again every 900 s. A run is now a resumable cycle. Each pass starts no self-test past `DARWIN_PASS_BUDGET_S` (900 s), remembers what ran and gives the slot back. The next pass resumes the same tip, and a finished cycle writes its RED lines once.
- `python3 -I` drops the script's directory from sys.path (Python 3.11+, `-I` implies `-P`). That made `queue_pre_flight.py` read as a false Darwin red (`ModuleNotFoundError: No module named 'merge_train'`). The row now runs a `.py` self-test with CI's plain `python3`.

Closes: none (no issue; triage P744).

## Head

5c7b8a82c53d2259296dd43da81212f85e69eaed

## Re-cut

Round 4 follows the round-3 verdict `blocked a55158085ed8cd6517113af8b77af07492a6634e mutation-vacuous: red_carried_to_next_cycle, no_per_run_remember survive`. Relative to the reviewed head this repair changes only `tools/audit/seat/beat_jobs_selftest.py`: two cases and two MUTANTS rows, production code unchanged. It also merges origin/main c987209c, which carries the weekend-clock fix.
- `darwin-selftest: a new cycle starts with an empty red list after a cycle that had REDs`: cycle 1 on tip A ends with one RED, cycle 2 on tip B runs green, and the digest must be empty.
- `darwin-selftest: a pass killed partway keeps the runs it finished`: the second self-test run raises, and the remembered state must hold `done == [prepr.sh]`, `complete` false and the cycle's tip.

## Mutation proof

Seventeen mutants in `beat_jobs_selftest.py` MUTANTS. Each one is killed by the case named in its entry, and the self-test prints `ok mutant <name> killed by: <case>` for each. The command is `python3 -I tools/audit/seat/beat_jobs.py --self-test` at the Head, and its final line is `beat_jobs self-test: 242 checks, 0 failed`.
- The ten from earlier rounds: `darwin_gate_dropped`, `darwin_first_fail_is_last_line`, `darwin_tip_not_skipped`, `darwin_red_dropped`, `darwin_cwd_repo`, `darwin_keep_state_dir`, `darwin_wired_filter_dropped`, `darwin_remember_on_wt_fail`, `darwin_slot_take_ignored` and `darwin_lease_not_released`. The sites of `darwin_tip_not_skipped` and `darwin_red_dropped` were re-anchored to the restructured lines. They mutate the same predicates.
- New this round:
  - `darwin_budget_ignored` drops the pass-budget check. Killed by "a pass starts no self-test past DARWIN_PASS_BUDGET_S; the next pass resumes the same tip".
  - `darwin_cycle_follows_main` makes every pass restart at the newest tip. Killed by the same case.
  - `darwin_done_rerun` makes an already-run self-test run again. Killed by the same case.
  - `darwin_red_each_pass` writes the RED lines at every pass. Killed by "a cycle's RED lines are written once, when it completes".
  - `darwin_py_isolated` puts `-I` back. Killed by "a .py self-test runs as CI's plain python3, never -I (which drops the script dir)".
- Round 4 adds `red_carried_to_next_cycle` (the new cycle's `red` seeded from the old one's, killed by the empty-red-list case) and `no_per_run_remember` (the per-run `ctx.remember` line deleted, killed by the killed-partway case). The self-test prints `ok mutant red_carried_to_next_cycle killed by: ...` and `ok mutant no_per_run_remember killed by: ...`. Both new cases pass on the unmutated code (242 checks, 0 failed).
- Failing test first: with the new cases added and the Head's production code still at 8a05961b, `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants` gave rc=1 and `139 checks, 5 failed`. The five failures were the pass-budget, written-once, per-pass-slot, budget-at-most-half-timeout_s and plain-python3 cases.

## Null control

- Pass budget: at 8a05961b the same fake run, three 600 s stubs plus prepr, ran every self-test in one pass, and the budget case FAILED, as above. At the Head, pass 1 runs exactly ceil(900/600) = 2 self-tests. Every later pass adds a worktree of the first tip, even after the fake origin/main moves. The cycle ends with each self-test run exactly once.
- `-I`, on this Mac at main 50373173 (output in <scratch>/qpf.txt, scratch):
  - `python3 -I tools/audit/seat/queue_pre_flight.py --self-test` gives rc=1 with `ModuleNotFoundError: No module named 'merge_train'`.
  - `python3 tools/audit/seat/queue_pre_flight.py --self-test` gives rc=0 with `queue_pre_flight self-test: 53 checks, 0 failed`.
  - Not re-measured: whether any other self-test that is green under `-I` changes without it. Dropping `-I` only adds the script's directory to sys.path.
- Reviewer survivors from earlier rounds: unchanged from the prior body. All are killed (probe/revt-r10-hotfix-macos-selftest-lane-dfbc393a Evidence).

## Figures

Machine class for every run below: Apple M1, 8 cores, 8 GiB, macOS 27.2, Python 3.14.7, /bin/bash 3.2.57. The box was not idle. Another seat's `prepr.sh --self-test` (pid 16778), two to three further `prepr.sh --self-test` processes and a `ci_predict.py --record-self-tests` ran during these runs, beside the merge train.

Each run uses row code 8a05961b, the blocked head, which carries the defect-detecting row unchanged. The row runs from a scratch clone at <scratch>/repo whose `refs/remotes/origin/main` is set to the tip under test. The body's former command, `beat_jobs.py --run darwin-selftest`, was wrong: the CLI takes the row as a positional. The command, from that clone, is:

    time python3 -I tools/audit/seat/beat_jobs.py darwin-selftest --state <scratch>/state-<red|green> --repo <scratch>/repo
    cat <scratch>/state-<red|green>/digest/jobs/darwin-selftest

**RED at main 19baca76181cb019d9b1cfd93ee6bc0a08e20047** (2026-11-13T22:57:53Z to 2026-11-14T00:18:24Z). Result: `real 80m30.649s`, rc=0, and the digest holds 13 lines:

    darwin-selftest: RED tools/pr/prepr.sh FAIL and the refusal quotes mutant_run's own reason (got 0, wanted 1)
    darwin-selftest: RED tools/audit/seat/bus.sh FAIL push-verdict refuses evidence names that differ only by case, naming both
    darwin-selftest: RED tools/audit/seat/cloud-setup.sh tools/audit/seat/cloud-setup.sh: line 124: vars[0]: unbound variable
    darwin-selftest: RED tools/audit/seat/gh_calls.py FAIL gh api dot segments resolving to #201 is refused
    darwin-selftest: RED tools/audit/seat/heartbeat.sh FAIL null control: the same host's message naming another path is pushed
    darwin-selftest: RED tools/audit/seat/hooks_setup.py FAIL beatd: run at the floor starts, and records its cwd, argv and HPO_* environment (null control for the refusal)
    darwin-selftest: RED tools/audit/seat/mutant_run.py FAIL spec: the NULL mutant reports SURVIVED and a pinned mutant KILLED
    darwin-selftest: RED tools/audit/seat/open_pr.sh FAIL   a runner without pr_exit_trap is refused
    darwin-selftest: RED tools/audit/seat/pr_args.sh FAIL   a runner without pr_exit_trap is refused
    darwin-selftest: RED tools/audit/seat/queue_pre_flight.py ModuleNotFoundError: No module named 'merge_train'
    darwin-selftest: RED tools/audit/seat/tick_loop.sh FAIL a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
    darwin-selftest: RED tools/audit/seat/train.sh train.sh: REFUSE: self-test: TERM to the train (pid 42762, launcher 42762) left 0 of 0 pids of its tree alive (pidfile removed, none)
    darwin-selftest: RED tools/audit/seat/update_pr.sh FAIL   a runner without pr_exit_trap is refused

The defect the row was written for is named: `RED tools/audit/seat/mutant_run.py`. `RED tools/pr/prepr.sh` is the same defect seen through prepr's own self-test, because it quotes mutant_run's reason.

**GREEN for that defect at main 50373173d486faf394b24637c177ab38b691b394**, which carries the mutant_run Darwin hotfix f3ccd1a5 ("mutant_run: wait for the self-test's zombie by polling the table, as macOS has no os.waitid"). The run went from 2026-11-14T00:18:49Z to 02:07:37Z. Result: `real 108m47.673s`, rc=0. The `mutant_run.py` and `prepr.sh` lines are gone, and so is `tick_loop.sh`. The digest holds the 10 lines below. The row is not silent, because main still carries other Darwin reds:

    darwin-selftest: RED tools/audit/seat/bus.sh FAIL push-verdict refuses evidence names that differ only by case, naming both
    darwin-selftest: RED tools/audit/seat/cloud-setup.sh tools/audit/seat/cloud-setup.sh: line 124: vars[0]: unbound variable
    darwin-selftest: RED tools/audit/seat/gh_calls.py FAIL gh api dot segments resolving to #201 is refused
    darwin-selftest: RED tools/audit/seat/heartbeat.sh FAIL null control: the same host's message naming another path is pushed
    darwin-selftest: RED tools/audit/seat/hooks_setup.py FAIL beatd: run at the floor starts, and records its cwd, argv and HPO_* environment (null control for the refusal)
    darwin-selftest: RED tools/audit/seat/open_pr.sh FAIL null control: open_pr with the code sha passes every check, and its failed push names its log
    darwin-selftest: RED tools/audit/seat/pr_args.sh FAIL null control: open_pr with the code sha passes every check, and its failed push names its log
    darwin-selftest: RED tools/audit/seat/queue_pre_flight.py ModuleNotFoundError: No module named 'merge_train'
    darwin-selftest: RED tools/audit/seat/train.sh train.sh: REFUSE: self-test: TERM to the train (pid 68229, launcher 68229) left 0 of 0 pids of its tree alive (pidfile removed, none)
    darwin-selftest: RED tools/audit/seat/update_pr.sh FAIL null control: open_pr with the code sha passes every check, and its failed push names its log

Classification of the 10 lines at 50373173:
- `queue_pre_flight.py` is the lane's own `-I` artifact, fixed in this head (Null control).
- These four were re-run directly on this Mac at 50373173 with CI's command, outside the row: no slot, no HPO_STATE_DIR, plain `python3`/`bash`. Each one reproduces:
  - `python3 tools/audit/seat/gh_calls.py --self-test` gives rc=1 and `221 checks, 1 failed`, with the same FAIL line.
  - `bash tools/audit/seat/heartbeat.sh --self-test` gives rc=1 and `8 checks, 1 failed`, same line.
  - `python3 tools/audit/seat/hooks_setup.py --self-test` gives rc=1 and `46 checks, 1 failed`, same line.
  - `bash tools/audit/seat/train.sh --self-test` gives rc=2 with the same REFUSE.
  They are real Darwin reds on main and not artifacts of the row.
- `cloud-setup.sh` is a real Darwin red. It calls `mapfile`, which /bin/bash 3.2 lacks, so `vars` stays unset under `set -u`. It is carried (Forward-carry).
- `bus.sh`, `open_pr.sh`, `pr_args.sh` and `update_pr.sh` were not re-run outside the row. They take 388 to 692 s each, and the box's heavy capacity was left to other seats. They are not classified, and they are carried with the four above (Forward-carry).

**Wall time of one whole run, by this machine class under the load above:**
- RED: 4830.6 s. Slot wait inside it was not measured separately.
- GREEN: 6527.7 s. Of that, 779 s was slot wait (slot-take returned at 00:31:48Z, polled every 2 s on its pid) and 5749 s was self-tests after the slot.
- What the row runs is enumerated by `python3 -I -c 'import sys; from pathlib import Path; sys.path.insert(0,"tools/audit/seat"); import beat_jobs; print(len(beat_jobs.darwin_instruments(Path(sys.argv[1]))))' <tree>`, run from the Head on a `git archive` of each tip. It gives 80 at 19baca76 and 81 at 50373173, plus `prepr.sh --self-test`, so 81 and 82 runs.
- Per-run seconds come from sampling the row's child processes every 2 s. Each run counts from its start to the next run's start. 51 runs were seen; the rest finished within one sample. The sampled sum is 5746 s, against 5749 s measured.
- The largest runs: `prepr.sh` 1104, `pr_args.sh` 692, `open_pr.sh` 685, `update_pr.sh` 676, `beatd.py` 406, `bus.sh` 388, `merge_train.py` 381 and `cloud_relay.sh` 370. Every other run took under 200 s.
- No unloaded figure was taken: the train and openers run on this box all the time.

**Scope choice.** Even half the loaded figure, about 2900 s, would be past the 900 s interval, and close to the 3600 s timeout. So the row needed a scope that fits a pass, and raising `timeout_s` alone would not do. Two scopes were considered:
- Diff-scoped: only the self-tests the diff since the remembered tip can reach. Not taken. This defect class breaks that rule: `prepr.sh --self-test` went red from a change to `mutant_run.py`, a different file, and no measured closure maps seat self-tests to their inputs.
- A slower cadence alone: not taken. The pass would still outlive `timeout_s`.

Taken: a resumable cycle per tip, with a pass budget. The bound is 900 s plus the longest single run, measured 1104 s, so about 2004 s per pass. That is under the 3600 s `timeout_s`. A pass holds the heavy slot at most that long and then gives it back to other seats' prepr runs.

Null control for the bound: before this head, a pass was the whole run, 4830 to 6528 s, so beatd's timeout would have killed it.

Limits:
- A cycle finishes no sooner than the self-test time, measured 5749 s under load, plus the gaps between passes. Detection lag is therefore about one to two cycles while main moves.
- A self-test longer than about 2700 s, started late in a pass, can be killed with that pass once. It was not marked done, so the next pass starts with it, and there it has the whole 3600 s against `sh`'s 3000 s per-run bound.

Detection lag and refused opens per Darwin red stay owed at round end. Carry: O1

Machine-local logs (not in the tree) are kept in `<scratch>`, this seat's scratch directory under the orchestrator's state dir on the Mac (`$HPO_STATE_DIR/s14/seat/macos-lane`): `red.log`, `green.log`, `green.slot`, `green.samples`, `green.timing.txt`, `direct.txt`, `qpf.txt`, `failing-first.txt` and `selftest-head.txt`.

## Red checks

none

## Forward-carry

- `tools/audit/seat/cloud-setup.sh` self-test is red on Darwin. It uses `mapfile`, absent from bash 3.2, so it fails with `line 124: vars[0]: unbound variable`. The red is present at 19baca76 and at 50373173. Its seam is cloud-setup.sh and the seat environment. That seam's group, R10-SUITE-ENV-RESIDUE, is `carries-open`, so the carry audit refuses it as a destination (BAD-DEST at origin/handoff/audit-r10-roster de39b4bfe9). No live roster group lists cloud-setup.sh or a Darwin/bash 3.2 seam. The orchestrator routes it, either to a new hotfix group or by reopening that group. Carry: O1
- These Darwin reds at main 50373173 sit outside this group's seam, and the row will report them in the digest once it runs:
  - Reproduced outside the row: `gh_calls.py`, `heartbeat.sh`, `hooks_setup.py` and `train.sh`.
  - Not yet re-run outside it: `bus.sh`, `open_pr.sh`, `pr_args.sh` and `update_pr.sh`.
  The orchestrator routes each one to its owning group. Carry: O1

## Friction

none
