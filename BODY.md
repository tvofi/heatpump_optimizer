Part 1 of 3 of R11-CLOSEOUT-CLEANUP: the closeout instrument derives the round's own closeout group from the roster's round, refuses a missing `--orch-root`, and `prune_refs.tip_ages` reads ages per sha when a batch fails (Carry 2 and Carry 3; the brief's SELF_GROUP ask). Carries 0, 1 and 4 are proposal-triage or re-measure items: dispositions under Forward-carry.

## Head

c64b6c335ca8cb33647b606a0feb7bef3fb7b555, on origin/main ac9045c223721608e684c8a2213831aa34c1fa4f (`date -u` 2026-11-28).

## Mutation proof

- `tip_ages` fallback (`if read(batch) and len(batch) > 1:` replaced by `if False:`): `python3 tools/audit/seat/prune_refs.py --self-test` fails "tip_ages: a batch with one missing sha still reads the others" and the null-control arm; restored, passes.
- `--orch-root` refusal (`if not a.orch_root:` replaced by `if False:`): `python3 tools/audit/seat/closeout.py --self-test` exits 1; restored, exits 0.

## Null control

- A batch with every sha present reads the same ages as before (self-test arm "null control: a batch with every sha present reads the same ages").
- A run naming `--orch-root` passes that refusal (arm "null control: a run naming the root passes that refusal"); a round-10 roster still derives `R10-CLOSEOUT-CLEANUP`, and a round-11 roster blocks on a not-done `R10-CLOSEOUT-CLEANUP` while exempting `R11-CLOSEOUT-CLEANUP`.

## Figures

- `python3 tools/audit/seat/closeout.py --self-test`: 46 checks, 0 failed.
- `grep -rln "orch-root\|orch_root" tools/ .claude dev/governance`: lists only tools/audit/seat/closeout.py, so it is the one script taking the argument.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, the two changed files.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

- Carry 2 (tip_ages per-sha read) and Carry 3 (`--orch-root` refusal) are built in this pull request, above; no forward carry. Carry: dismissed: built in this pull request
- Carry 0 and Carry 1 (merge-time undefined-name detector, `merge_train.py` merge step candidate site): a round-end proposal, not built here. Carry: R11-CLOSEOUT-CLEANUP
- Carry 4, re-measured at ac9045c223 by reading `tools/audit/seat/`: merge_pr.sh deferral read is answered (classify rc 3 is WAIT); TRAIN-ADD-START-TEXT (train.sh header and the started-train sentence) open; TRAIN-SKIP-RELEASES-WORKTREE (`Train.skip` never calls `release_worktrees`) open; TRAIN-WAIT-UNSTALE (`unstale` only on the land path, not `wait_ci`) open; skipped-entry re-admission in `already_held` open; rejoin-without-recarry answered for PREFLIGHT_PARK, open for other skip classes; stale gate red from an older run's check open. Builds are instrument work for a later part. Carry: R11-CLOSEOUT-CLEANUP

## Friction

none
