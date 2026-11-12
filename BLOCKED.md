# BLOCKED: r10-process-slim-p2 merge repair 6 (PR #3451)

Question: The orchestrator's procedure was followed: merge the current origin/main, then run prepr.sh straight away with the worktree detached. The predicted red did not fire, but the second defect in the earlier BLOCKED.md did. origin/main moved during `ci predict`, and the self-test restart arm (`tools/audit/seat/tick_loop.sh`, the `checkout -q --detach origin/main` arm before `TICK-RESTART`) moved the detached worktree from this head to origin/main. Every later prepr step therefore ran at main, not at this head. prepr takes about 35 minutes, `ci predict` alone about 30, and main merged during that step in both runs. Should this seat (a) keep retrying merge-then-prepr until main stays still for one whole run, (b) hand off with this run on record, or (c) wait for R10-HOTFIX-TICK-SELFTEST-CHECKOUT to land? tick_loop.sh was not edited, per the ruling.

Code: f26a283927f9212ac4ff28f90c0b46a1a4c5e7f6 is the merge of origin/main 4596f721 into 8301a5f2. 8301a5f2 is the merge of origin/main fc2a7edc into dea9f4ca, and dea9f4ca is 1b45b89b with BLOCKED.md removed. Both merges were clean: `git merge-tree --write-tree` exits 0 and every file auto-merged. It is at handoff-wip/r10-process-slim-p2, with this file on top. The updated draft body is at handoff-wip/r10-process-slim-p2-body. Nothing is pushed to handoff/ or handoff-body/.

Answers to the previous BLOCKED.md:
- Ruling taken: tick_loop.sh is not edited.
- (1) The current origin/main was merged first. After the merge, `git rev-list --count HEAD..origin/main -- <path>` printed 0 for each of tools/audit/seat, tools/pr and tools/audit/carry_audit.py, both at 8301a5f2 (main fc2a7edc) and at f26a283 (main 4596f721).
- (2) prepr.sh ran detached, straight after the merge. Run 1 at 8301a5f2 hit the background time limit while in `ci predict`. By then main had moved once (4596f721, the v7.1.12 stamp), so the seat merged it, giving f26a283, and ran prepr again.
- (3) `git rev-parse HEAD`: before prepr, f26a283927f9212ac4ff28f90c0b46a1a4c5e7f6 (2026-11-12T10:50:28Z). After prepr, 6e100ef6980216a81eaa0438bdc215d62b19271f (2026-11-12T11:24:42Z). 6e100ef is origin/main itself (`Merge pull request #3479`), which main reached during the run through #3497 and #3479.
- (4) The predicted red (the tick-loop rows in `governance / instrument-self-tests`) did NOT fire. prepr printed `ok ci predict CI PREDICT: no closures, fast, governance or instrument red predicted against 4596f721f66d`. The HEAD move is the defect that fired.

Evidence:
- The worktree reflog shows a checkout by the restart arm during the `ci predict` step. No command of this seat moved HEAD:
  `6e100ef698 HEAD@{2026-11-12 11:20:50 +0000}: checkout: moving from f26a283927f9212ac4ff28f90c0b46a1a4c5e7f6 to origin/main`
- The steps after `ci predict` name main's head, not this one. They print `merged structure STRUCTURE RATCHET PASSED (tests/structure.py at 6e100ef69802, HEAD merged with origin/main)`, and then:
  `REFUSE pr-body ... ## Head does not name 6e100ef, which is the head this ran on.`
  `PRE-PR: 6e100ef6980216a81eaa0438bdc215d62b19271f 000000000000000000000000000001000 rc=1`
- Steps up to and including `ci predict` ran at f26a283 and all print ok or skip (`closures` skip: the diff cannot be scoped). `diff mutants` (skip: MUTANT_CMD unset) ran after the move, at 6e100ef.
- Control, the same arm at behind=0: the run at 8301a5f2 (main fc2a7edc, unmoved until the stamp) kept HEAD at 8301a5f2 through every step up to `ci predict`, as the reflog shows (no checkout entry between 10:15:41 and 10:50:20).
- The worktree is restored to f26a283 (`git checkout --detach f26a283`).
- Brief's closure run: `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` at f26a283 exits rc=0, with `tests/entities.py 566 files`, and HEAD is unmoved after the run. It changes one value in `tests/closures.json`: `recorded["tests/entities.py"].rc` goes from 1 to 0, and the closure's file list is unchanged. rc 1 is the value at origin/main, f26a2839, 9efb4daf and 4bc2f3bc, so it is inherited and not this branch's. It is committed as 5f95f406 on top of f26a283, below this file.
