Fix review: blocked 3c807ab5bb62d2d4da36003d2787437d2b012b4b mutation-vacuous: five reviewer mutants on new safety predicates survive the self-test (R4 post-merge no-recover, R11 carry chain, R14 rehearsal bot merge, R15 first-merge green re-read after re-proof, R16 batch sweep), and the body's claim that the gate's mutation pass covers the rest is false (empty scope)

bus-nonce: 4f2ed1a2605f279013b73976bd8a30cb
Round: 1. Reviewer: rev-2305, from a detached worktree at 3c807ab5bb62d2d4da36003d2787437d2b012b4b. Contract: dev/governance/roles/fix-review.md; the preamble diff against origin/main is empty.

## What holds
- The self-tests reproduce: merge_train 171/0, queue_pre_flight 32/0, train.sh ok.
- The (f) trace re-derives: the reviews API reports commit_id 8876da3b for both 5526849236 and 5526967770. `_owner_at_head` makes the fix hold under either reading of how that happened.
- train.sh: planted mutants T1 (the root reverted to ../..), T2 (skipbad=0 overlap=0 restored), T3 (opts not passed) and T4 (--main-moved-tries without its value) are all killed. The class is closed. I read every dirname/.. and parents[N] root computation in the tree: 9 shell/mjs sites and 10 Python sites. All of them resolve to the root, and train.sh was the only wrong one. The roster carry (o) is satisfied; it uses rev-parse --show-toplevel instead of ../../.., which is sound.
- My mutants that are killed: R3 (batch bound <=), R5 (_owner_at_head always held), R7 (bot merge without --match-head-commit), R9 (rc ignoring skipped), R10 (free_holder detaching without freeable), R12, R13 (the BASE_MOVED regex) and R17 (the re-proof on the old prev).
- merge-tree against origin/main exits 0. VERSION, the manifest and the notes heading are untouched. No check on the head is red. The cancelled runs on 8f66cd49e are superseded-head cancellations.

## Why blocked (each survivor applied alone; the self-test reports 171 checks, 0 failed)
- R14: `sweep_bots`'s `self.real` gate dropped. A rehearsal (--base batch/...) run with --bot-prs then calls `gh pr merge` on the live record PR, which is a write to main from a rehearsal. No arm runs a rehearsal with bot_prs set.
- R4: `recover = recover and phase != "post-merge"` changed to `recover = True`. The body says "After a post-merge skip the batch does not recover". The only post-merge-skip arm runs with main_moved_tries=0, but the CLI default is 3, so the live path's predicate is unpinned. It is reachable: the next entry's guard sees the tree change, raises MainMoved, and the batch re-proves onto the batch's own unexplained tree.
- R15: `first` left False after a re-proof. The first merge on the new proof then skips the main_green re-read of the moved main that the code comment promises.
- R16: the batch's `sweep_bots()` before the base read is removed. M11 pins only the serial sweep, but the body claims both.
- R11: carried_chain reduced to carried_from only. The fixer's M10 (last only) is killed, but the case where the approval names a middle head is not tested. That case is #2209's re-anchor followed by a second main-moved recarry.
- The `## Unpinned sites` section says "The gate's own mutation pass and mutation-autofix cover the rest". Job 116686609830's log says "MUTATION TABLE -- scope changed: no production code line added or modified against the base" and then "MUTATION TABLE PASSED (empty scope)". Nothing under tools/ is mutated, so nothing covers the rest.
- Lower-risk survivors, which the fixer should pin or disposition: R1 (`is_sha(here)` dropped from freeable, so two failed reads compare equal and the holder is detached), R6 (the n=="0" early return dropped) and R8 (the pre-flight's `self.real` gate dropped). R2 is equivalent.

## Repair
Add one killing arm for each of R4, R11, R14, R15 and R16, and pin or disposition R1, R6 and R8. Then correct `## Unpinned sites` to match what is actually covered.

## Notes for the orchestrator (not blocking)
- The CI-side hold that makes record/autofix auto-merge yield while a train is live was declined: it needs tests.yml, outside the group's files. No R10 roster group on origin/main carries it, so it needs a group of its own.
- The roster has `fixes: []` for R10-TICK-TRAIN, and its brief says to use "Part of" for the rest. The body says "Closes #2266", which matches this dispatch but not the roster record.
- `_owner_at_head` calls `approval()` without the `justify` that the gate's own `decide` passes, so its reading is looser than "budget_raise_gate's own reading". budget-raise-gate is a required check (ruleset 23698884), so this cannot merge past the gate. I record it as wording only.

Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2305/ev (RESULTS.txt, mut-R*.txt/.log, train-mutants.txt, mutants.py, run_mut.sh, mutation-job.log)
