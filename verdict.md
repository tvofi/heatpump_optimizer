Fix review: blocked 8a05961bfc00cd8a0c849fa4f42f975494c34560 harness: design-trace-missing red-then-green demonstration at 19baca76 and Mac wall time still NOT MEASURED with no tvofi waiver

bus-nonce: dfbc393aa30b0bf422ae6aa68595b523

## Block

- design-trace-missing (fix-review.md step 9; defect-root-cause.md "A detector must be shown to detect"). This is the prior verdict's first block item (probe/revt-r10-hotfix-macos-selftest-lane-930d29b9), and it is not resolved. The brief names two on-device items. The first is a red-then-green demonstration: RED naming mutant_run.py at main 19baca76, then nothing once the mutant_run.py Darwin hotfix is on main. The second is the wall time of one run on the Mac. The body's Figures still mark both NOT MEASURED and hand them to the orchestrator as O1. That is a carry past the merge. The prior verdict said these runs go in the report, and no tvofi waiver is cited. A Darwin host has to run the body's own command, `time python3 -I tools/audit/seat/beat_jobs.py --run darwin-selftest` at both mains. Once both outputs and the real time are recorded in the body, the work can be handed off again. If tvofi waives the items, the body must cite that waiver instead. With either of those, and the code unchanged, this delta is mergeable: every other prior finding is resolved (see Evidence).

## Findings

- The round-end measures (detection lag, refused opens per Darwin red) are owed at round end, as the body says. Carry: O1

## Evidence

- Later round, so this is a delta review (fix-review.md, tvofi 2026-11-09). The delta is `git diff b63d67cc 8a05961b`. It touches only tools/audit/seat/beat_jobs.py (+8/-1) and beat_jobs_selftest.py (+44/-1). It changes no production code, so the review does not widen. The measured head is 8a05961bfc00cd8a0c849fa4f42f975494c34560 (ev/HEAD.txt). It matches the body's ## Head.
- No pull request exists yet, so there is no review packet and no CI to read. Red checks: none apply. The owed-reds set is in ev/owed-reds.txt.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test` at the head gives rc=0 and prints `227 checks, 0 failed`, as the body claims, in 36 s wall on Linux. All 10 darwin_* in-file mutants print `killed by` their named case (ev/selftest.txt).
- Prior findings, re-run with the prior reviewer's mutants (ev/my_mutants.py). no_take was adapted to the rc-checked slot-take line. One new mutant, slot_rc_ignored, was added. Each one ran with `--self-test --no-mutants` on a restored file, and every one gives rc=1 (ev/mutants.txt, ev/mutant-*.tail.txt):
  - cwd_repo is now killed: "every self-test runs in the worktree…" FAILs. Resolved.
  - keep_state_dir is now killed: "the self-tests' env never carries…HPO_STATE_DIR" FAILs. Resolved.
  - wired_filter_dropped is now killed: "the wired filter drops a self-test no workflow runs" FAILs. The case includes a null showing that self_testing lists both stubs. Resolved.
  - remember_on_wt_fail is now killed: "a failed worktree add is UNREADABLE, releases the slot, and the tip is retried" FAILs. Resolved.
  - The slot-take rc is now checked. My mutant slot_rc_ignored is killed by "a slot-take that fails is UNREADABLE and runs nothing". Resolved.
  - These are still killed: no_remember, no_final_remove, no_detach, no_prepr and no_take.
- The prior timeout note is accepted as moot, as the body explains. Not re-measured.
- The worktree was clean after the mutant runs (ev/wt-status-after.txt is empty).
- Merge with main: `git merge-tree --write-tree origin/main 8a05961b` exits 0 with tree 30a73264, so it merges cleanly (ev/merge-tree.txt).
- fix-review.md is unchanged between the merge base and origin/main. Other role files changed on main, and this review used main's rendered role pack.
- Figures I could not re-derive: the Mac wall time and the red/green runs at 19baca76. Both need a Darwin host, and this seat runs Linux. They are the block above.
