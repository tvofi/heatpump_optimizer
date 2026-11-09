Fix review: merge 0c27d79e0e1c082dd8045b93b05e7f84b68da7ae

bus-nonce: 52c82b6ab658be0daa72b85c7b0b29f0

Round 1. Head reviewed: 0c27d79e0e1c082dd8045b93b05e7f84b68da7ae (still the PR head at 05:30Z per get).

## Findings

- Follow-up: the settle gap (code run green, gate-sweep not yet re-run) is shown only by a synthetic scene that reads WAIT at this head and RED at origin/main, per the body; the RCA's carry to the orchestrator and the #3290 fixer is prose in the record, not a routed item. Carry: dismissed: already written in the record's Forward-carry section with owners (#3290 fixer, orchestrator); this PR changes no train code.
- Follow-up: the six readers of a `gate` conclusion outside `classify`'s family still read a deferral as final (body Figures, grep-based enumeration, not re-derived by me). Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- Follow-up: `orchestrator_tick.py` still describes the superseded 720 s wait. Carry: dismissed: orchestrator-owned text outside this RCA diff, recorded in the record's Forward-carry.
- Residual: the body's red-check answer for `governance / instrument-self-tests` leaves the flake unreproduced with no null control; its carry already stands. Carry: R10-SUITE-HOST-DETERMINISM

## Evidence

- Scope: 6 files, all RCA/record material (bugclasses.json entry, RCA doc, harness .py/.json fixture, delivery row, one closures.json line registering the harness). No production code, VERSION, manifest or RELEASE_NOTES change (ev/version-diff-lines.txt: 0).
- Mutation proof (step 1) re-run: replay at head RESULT replay defects=0 settle_gap=0 null_bad=0 scenes=7 (ev/replay_head.txt); with merge_train.py line 487 `deferred = {GATE} if busy else set()` replaced by `deferred = set()`: RESULT replay defects=3 settle_gap=1 null_bad=0 scenes=7 (ev/replay_mutant.txt); restored (worktree clean). Matches the body. Null controls (code-run-red, all-green, red non-gate) read RED/GREEN/RED at head. I did not re-run the origin/main-side defects=3 figure separately beyond the mutant equivalence.
- Merge: git merge-tree --write-tree origin/main head: rc 0, LEDGER-MERGE: resolved dev/audit/config/bugclasses.json (ev/merge-tree.txt).
- CI at this head (get_check_runs, run 42554656207 and 42554903108): gate success, tests/fast, mutation, closures, coverage, typing, pr-contract, instrument-self-tests, budget-raise-gate, arch-score all success; no required check red at this head. The red checks the body answers (fast at 330159042, instrument-self-tests, pr-contract) are earlier heads' and answered in the body. `merge_train.py classify` returned rc 2 (REFUSE ci: the check runs could not be read) in this seat (no readable GitHub token); the verdict rests on the MCP check-run listing instead. A governance / delivery-status failure appears only on an earlier run (42554575887); at this head's run it is skipped, and it grades main.
- carry_audit at head per packet: 0 finding items; figure_lint: 2 resolved, 0 not verified, 0 refused. Census figure (deferral_fails=14) not re-run by me.
- Not re-derived: the 32 of 56 SKIPs quoted from #3290, the eight-reader enumeration, and the flake reproduction counts; the body itself discloses these as not measured or not in tree.
- Heavy runs (mutation, gate) cited from CI, not re-run.
