HOTFIX (R10 batch 246, P744), repair round after "Fix review: blocked b63d67cc". Main CI is Linux-only, so a Darwin-only self-test regression (PR 3475: `mutant_run.py` listing /proc) was found only when an opener failed. This adds a `darwin-selftest` beat row: Darwin hosts only, one run per new origin/main tip, heavy-slot lease, a detached worktree the row owns, `prepr.sh --self-test` plus each wired seat self-test, one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green. No workflow file touched (owner ruling 2026-11-12: macOS checks are local seats or beat rows). It detects after merge and does not prevent; a pre-merge arm is round 11.

Repair round: the four survivors the reviewer found are now killed by named cases and in-file mutants; the row checks `slot-take`'s exit code (reviewer finding); the Mac run and wall time stay owed to a Darwin seat (O-item below).

Closes: none (no issue; triage P744).

## Head

8a05961bfc00cd8a0c849fa4f42f975494c34560

## Mutation proof

Ten mutants in `beat_jobs_selftest.py` MUTANTS, each killed by the case named in its entry (the self-test prints `ok mutant <name> killed by: <case>` for each). The first five are unchanged: `darwin_gate_dropped`, `darwin_first_fail_is_last_line`, `darwin_tip_not_skipped`, `darwin_red_dropped`, `darwin_lease_not_released`. New this round:
- `darwin_cwd_repo` (self-tests run in `ctx.repo`) by "every self-test runs in the worktree, never the orchestrator's own checkout" (Fake now records each call's cwd and env).
- `darwin_keep_state_dir` (the `HPO_STATE_DIR` strip dropped) by "the self-tests' env never carries this digest's HPO_STATE_DIR".
- `darwin_wired_filter_dropped` (`and p in wired` dropped) by "the wired filter drops a self-test no workflow runs", on a temp tree with two self-testing scripts of which one workflow run line names one.
- `darwin_remember_on_wt_fail` (tip remembered after a failed worktree add) by "a failed worktree add is UNREADABLE, releases the slot, and the tip is retried".
- `darwin_slot_take_ignored` (slot-take rc ignored) by "a slot-take that fails is UNREADABLE and runs nothing".

## Null control

The new check passes at the Head and fails under each reviewer survivor: the reviewer's own `ev/my_mutants.py` (from `probe/revt-r10-hotfix-macos-selftest-lane-930d29b9`) was re-run against the Head with `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants`, one mutant at a time on a restored file. Results: cwd_repo rc=1, keep_state_dir rc=1, wired_filter_dropped rc=1, remember_on_wt_fail rc=1 (the four former survivors, each now failing named cases); no_detach rc=1, no_final_remove rc=1, no_remember rc=1 (killed as before); no_prepr rc=1 and no_take rc=1 (killed by a StopIteration crash in the order case, as the reviewer saw; no_take's pattern was adapted to the now rc-checked call `rc, _, err = ctx.run([*gate, "slot-take"`, since the original line no longer exists). Null for the wired-filter case: the same temp tree's `self_testing` lists both scripts, so only the filter separates them. Null for the cwd case: the non-mutant run's every self-test cwd equals the worktree path and differs from `ctx.repo`.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` at the Head: final line `227 checks, 0 failed`; all ten darwin mutants killed.
- NOT MEASURED, carried to the orchestrator as O-item: this seat is Linux, where the Darwin-only /proc read is green, so neither the red-then-green demonstration nor the Mac wall time can be produced here. A local macOS seat must run, from a checkout whose `origin/main` is 19baca76 (red expected, naming `tools/audit/seat/mutant_run.py`) and again at a main with the `mutant_run.py` Darwin hotfix (nothing expected): `rm -f $STATE/darwin-selftest.json; time python3 -I tools/audit/seat/beat_jobs.py --run darwin-selftest` (or the beatd row run for `darwin-selftest`), then `cat` the digest's `jobs/darwin-selftest`. Record both outputs and the `time` real figure. Carry: O1.
- Linux self-test wall time at the Head is not claimed; the review measured 50 s for the prior head.
- Round-end measures (detection lag, refused opens per Darwin red) are owed at round end. Carry: O1.
- Reviewer findings dispositioned: three survivors fixed (above); slot-take rc fixed; the 3600 s self-test timeout note is moot (the runner's timeout is the `subprocess.run` bound in `Ctx`, unchanged here).

## Red checks

none

## Forward-carry

none

## Friction

none
