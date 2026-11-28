Part 1 of 3 of R11-CLOSEOUT-CLEANUP: the closeout instrument derives the round's own closeout group from the roster's round, refuses a missing `--orch-root`, and `prune_refs.tip_ages` reads ages per sha when a batch fails (Carry 2 and Carry 3; the brief's SELF_GROUP ask). Carries 0, 1 and 4 are proposal-triage or re-measure items: dispositions under Forward-carry.

Round 2 repairs the round-1 block (verdict/3942 at 72f9171a74, `mutation-vacuous`): the delta adds self-test checks only; no production line changed (`git diff 9ea84ecc HEAD -- tools/audit/seat/closeout.py tools/audit/seat/prune_refs.py` touches only `self_test()` in each).

## Head

76ecf989699c6b1ec0c9350a6d71e36a4f21af0d, on origin/main a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43 (`date -u` 2026-11-28 16:50 UTC). `git merge-tree --write-tree origin/main HEAD` exits 0.

## Mutation proof

The reviewer's three mutants, applied verbatim to the new head, each run against its file's `--self-test`:

- ctx-const (`self.self_group = self_group_for(str(a.roster_file))` -> `self.self_group = "R10-CLOSEOUT-CLEANUP"`, `Ctx.__init__`): rc=1 KILLED, failing "a round-11 dry run with only its own closeout group open does not refuse" and "null control: the same round-11 dry run names R10-CLOSEOUT-CLEANUP open".
- run-uses-const (`roster_blockers(c.roster, c.self_group)` -> `roster_blockers(c.roster, "R10-CLOSEOUT-CLEANUP")`, `run()`): rc=1 KILLED, failing the same two checks.
- tip-no-len (`if read(batch) and len(batch) > 1:` -> `if read(batch):`, `tip_ages`): rc=1 KILLED, failing "tip_ages: a lone missing sha costs one git call, never a re-read of itself". The mutant is equivalent in result (the reviewer's note); the check pins the cost instead: a failed one-sha batch is not read a second time.
- Round-1 mutants, unchanged: `tip_ages` fallback (`if False:`) and `--orch-root` refusal (`if False:`) still kill; the verdict's six other kills rest on production lines this delta does not touch, and the delta only adds checks.

## Null control

- At 9ea84ecc (the base of this delta) the same three mutants read SURVIVED, rc=0 (verdict/3942 `evidence/mutants.txt`); at this head, unmutated, `closeout.py --self-test` prints 48 checks, 0 failed and `prune_refs.py --self-test` prints SELF-TEST PASS (84 checks).
- The round-11 `run()` arm has its own null control: the same roster with `R10-CLOSEOUT-CLEANUP` not-started prints `would REFUSE` whose blocker list is exactly `R10-CLOSEOUT-CLEANUP`.
- The `tip_ages` call-count check has its own: a failed two-sha batch costs 1 + 2 calls and still reads the held sha.
- A batch with every sha present reads the same ages as before; a run naming `--orch-root` passes that refusal.

## Figures

- `python3 tools/audit/seat/closeout.py --self-test`: 48 checks, 0 failed (46 at 9ea84ecc, plus the two round-11 `run()` arms).
- `python3 tools/audit/seat/prune_refs.py --self-test`: SELF-TEST PASS (84 checks) (82 at 9ea84ecc, plus the two call-count arms).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 34 scoped out.` The changed tools are run by the governance `instrument-self-tests` job, not by a closure script (round 1 wrote "the two changed files"; corrected).
- `grep -rln "orch-root\|orch_root" tools/ .claude dev/governance`: lists only tools/audit/seat/closeout.py.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Unpinned sites

`mutant_run.py --diff <merge-base>...HEAD --in-place --max-mutants 40` under `MUTANT_CMD` (both self-tests) prints 15 survivors, every one inside a `self_test()` body:

- tools/audit/seat/closeout.py:502 CONST_SWAP: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:505 CALL_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:644 CONST_SWAP: equivalent: in `self_test()`, `rsplit(": ", 2)[-1]` returns the same last field as maxsplit 1
- tools/audit/seat/closeout.py:480 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:485 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:489 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:491 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:497 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:502 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:636 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:637 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:639 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:642 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:653 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof
- tools/audit/seat/closeout.py:664 STMT_DEL: a self-test line in `self_test()`, not production: the mutant deletes or weakens one of the self-test's own checks; the production mutants those checks pin are killed under ## Mutation proof

## Red checks

none

## Forward-carry

- Carry 2 (tip_ages per-sha read) and Carry 3 (`--orch-root` refusal) are built in this pull request, above; no forward carry. Carry: dismissed: built in this pull request
- Carry 0 and Carry 1 (merge-time undefined-name detector, `merge_train.py` merge step candidate site): a round-end proposal, not built here. Carry: R11-CLOSEOUT-CLEANUP
- Carry 4, re-measured at ac9045c223 by reading `tools/audit/seat/`: merge_pr.sh deferral read is answered (classify rc 3 is WAIT); TRAIN-ADD-START-TEXT (train.sh header and the started-train sentence) open; TRAIN-SKIP-RELEASES-WORKTREE (`Train.skip` never calls `release_worktrees`) open; TRAIN-WAIT-UNSTALE (`unstale` only on the land path, not `wait_ci`) open; skipped-entry re-admission in `already_held` open; rejoin-without-recarry answered for PREFLIGHT_PARK, open for other skip classes; stale gate red from an older run's check open. Builds are instrument work for a later part. Carry: R11-CLOSEOUT-CLEANUP
- Round-1 reviewer follow-up: `dev/programme/HANDOVER.md`'s closeout dry-run enumerator omits `--orch-root`, which this head requires; outside this repair's three-site brief. Carry: R11-CLOSEOUT-CLEANUP

## Friction

none
