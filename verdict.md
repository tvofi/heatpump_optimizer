Fix review: merge aa6148d4ff35c457e83310337760e075cb823a14

bus-nonce: fd1fe84d9f5bedb49732c49223b1c6ad

Round 3, a scoped re-check. Round 1 blocked d843403626ee923fe1fbde4428f3a0b2eb734b06 with carry-over-wide. Round 2 blocked 32d880b3dee4e525d16ec270af83d867f7006431 with root-cause-unrecorded: governance / instrument-self-tests. Both blocks are answered at this head.

## Findings

- The owner's approving review is still owed before the merge. The diff changes three code-owned policy files (orchestrator.md section 11, fix-review.md step 12, standing-dispatch.md Relay). The body's `## Approval` says so, and it raises two items for the owner's decision: the "or keep its patch (L6)" clause, and round-1 O3, which is that the `.md` context mask also covers instruction files. Carry: dismissed: owner decision, already raised in the body's ## Approval, and main-protect-checks' code-owner rule enforces it
- The runner-image `unrelated-sleep` defect in pr_args.sh's reap fixture is not this PR's code. Carry: dismissed: #3086 owns the fix, and the body names it under ## Red checks
- Round-1 P123 row-binding residual and the forged-bot-email residual: the body dismisses both, and earlier rounds upheld those dismissals. Nothing about them changes at this head. Carry: dismissed: unchanged since round 2, which upheld the dismissal

## Evidence

- Head measured: aa6148d4ff35c457e83310337760e075cb823a14 (ev/HEAD.txt). Re-read before returning, `refs/heads/fix/r10-fly-carry-doc-context` and `refs/pull/3077/head` are both still that SHA (ev/live-head.txt). Work was done from detached worktrees at the head. The merge base's roles diff against origin/main changes only fix-review.md step 12's carry sentence, with no effect on this re-check.
- Brief item 3, the delta since 32d880b3d. aa6148d4 is a single merge commit with parents 32d880b3d and origin/main 6421fe135. Its tree 82d5af601 equals `git merge-tree --write-tree 32d880b3d 6421fe135`. There are zero branch-authored commits in the range: `git log 32d880b3d..aa6148d4 --not origin/main` lists only that merge. `review_carry.py 32d880b3d aa6148d4` prints CARRY, and `app_approve.sh --carry` prints `CARRY: yes`. No authored file changes between the two heads. The three-dot patch has the same `git patch-id --stable` at both heads (824b9ec5), so the branch's patch is byte-unchanged (ev/head-delta.txt, ev/threedot-compare.txt).
- Brief item 3, the plants. I re-ran round 2's plants (ev/plants.sh, the finder's harness) at this head with the same four scripts: round 1, head, head+M1 and head+M8. The results are identical to round 2 (ev/plants-at-head.txt):
  - own-budget, own-claim, ci-bare-closures and merge-hand-budget: r1 yes, head NO, M1 yes.
  - bot-outside-paths: r1 yes, head NO, M1 yes, M8 yes.
  - All four nulls (own-empty, ci-bare-empty, bot-own-path, merge-auto): yes everywhere.
- Brief item 3, the eight body mutants (ev/mut.py, ev/runmut.sh). Each ran in its own detached worktree at this head, and each was restored and checked with `git diff --quiet`. All are killed, with the same counts as round 2: M1 14 failed, M2 2, M3 2, M4 1, M5 1, M6 27, M7 2, M8 2 (ev/mut-M*.log).
- Brief item 2, the self-tests at this head, on Linux under `env -u BASH_ENV` (ev/selftests.txt): app_approve 316/0, app_comment 67/0, app_push 204/0, review_carry 29/0, bus 110/0, merge_train 400/0. Every figure matches the body.
- Brief item 1, red checks. I read the full check-run set at this head in one page of 100. It has 81 runs, all completed, and none concluded `failure`; each is success or skipped. That includes `governance / instrument-self-tests` (job 124884885532, 12:46 to 13:13Z) and the latest `pr-contract / pr-contract` (job 124884341923, 14:58Z). So no red at this head needs an answer. The body names the three reds at 32d880b3d with cause, process state and the no-cheaper-detector finding, which answers round 2's block. The body predicted that instrument-self-tests would go red at aa6148d4. It labels that as a prediction, and the measurement says green.
- CI: `merge_train.py classify aa6148d4` exited 0, `GREEN ... pending: none red: none`, read twice (ev/classify.txt).
- Brief item 4: the body's `## Approval` still states that the owner's approving review is owed, and it still raises O3 and the L6 clause.
- Brief item 5: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 3077` printed `6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` (ev/carry-audit-pr.txt). The packet's head audit printed 4 routed and 0 bad.
- Gate (ev/gate.txt):
  - The delivery row dev/programme/delivery/3077.md is in the three-dot diff.
  - Both claim files are byte-identical to origin/main.
  - VERSION, the manifest and the notes heading are untouched.
  - `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
  - The scoped gate printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
  - `git merge-tree --write-tree origin/main aa6148d4` against origin/main e4c9e2016 exited 0, with tree 70238f9e5 and no conflict.
- Not re-run, by the contract: the gate, the mutation table and the archscore. I cite CI's green `gate`, `tests / mutation` and `arch-score` at this head.
