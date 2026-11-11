Fix review: merge aa70efdd076bd5d6468060ca20638675c2fb9dd6

bus-nonce: 7055a1b1179464bd9228f498c313c70b
pending-ci: the relay has not yet applied aa70efdd to PR #3404 (live head d7347d0c), so no check run exists at this head; the required checks are owed there

## Round

This is round 4 of this group (R10-ARBITER-OFF-RESTORE). It is a delta review from the round-3 verdict `probe/rev-3404-091e3d43` (`Fix review: merge d7347d0c...`, findings none). Under fix-review.md step 12 I reviewed `git diff d7347d0c aa70efdd` with the finder's harness. I did not redo the earlier review of unchanged code. There was no review packet and no CI at this head to wait on.

## Evidence

- Head. The body at `handoff-body/r10-arbiter-off-restore` (466d56a90a79) names `aa70efdd076bd5d6468060ca20638675c2fb9dd6` under `## Head`. That is the head I measured from a detached worktree (`ev/HEAD.txt`).
- Contract. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current (`ev/roles-current.txt`).
- The delta is exactly a clean merge of main (`ev/delta.txt`).
  - `git merge-tree --write-tree d7347d0c a7887485` produces tree `2576d2ee`, with `LEDGER-MERGE: resolved tests/closures.json`.
  - `git diff 2576d2ee aa70efdd` is empty. So the head equals the automatic merge of the reviewed head with main `a7887485`. The merge reverted nothing and carries no hand resolution.
  - `BLOCKED.md` was added at `dacdacbf` and removed at `aa70efdd`, so it nets to zero.
- Production under `custom_components/`.
  - The branch's own changed lines are identical before the merge (`cbd23f1c8..d7347d0c`) and after it (`a7887485..aa70efdd`): `SAME-CHANGED-LINES`.
  - The only main-side change to `pump_arbiter.py` in the merge is two comment lines from #3466 (the vendor name removed at `FEEDBACK_START_HOLD` and in `_clamp_cut`'s docstring). That is no functional risk to reviewed code, so the review is not widened.
- Mutation proof with the finder's harness. I ran `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` at aa70efdd (`ev/mutants-harness-aa70efdd.txt`).
  - Result: `SURVIVED NULL` on both blocks, 37 `KILLED` (M01 to M20, M21 to M32, M34 to M38), rc 0.
  - This matches the body's `## Mutation proof`.
- Pins. The dispatch said this delta pins 7 new sites. I measured that it does not.
  - `git diff --name-status d7347d0c aa70efdd -- tests/mutation_ledger` shows only five `diagnostics.py` pins deleted, and those are main's own deletions (`cbd23f1c8..a7887485`, the same five).
  - The branch's own ledger files are unchanged from the head I reviewed in round 3.
  - The body agrees: "no pin was written by hand". So there was no new pin to verify with `--pin-killed`, and I ran no `mutation_table.py`.
- CI prediction. I ran `python3 tools/pr/ci_predict.py --base origin/main` at the head (`ev/ci_predict.txt`).
  - It printed `no closures, fast, governance or instrument red predicted against a7887485deb7`, rc 0.
  - It lists the same six unpinned sites with the same line numbers as the body's `## Unpinned sites` (`:1013`, `:1038`, `:1041` x2, `:1063`, `:1586`).
  - Round 3 re-ran those sites' kills (U1, U2, S1 to S5) on unchanged production.
- Merge with main.
  - `git merge-tree --write-tree origin/main aa70efdd` exits 0 against origin/main `6cc15e9b` (`ev/merge-tree.txt`), so there is no conflict.
  - The head lacks #3474. A `governance / instrument-self-tests` red there is main's old red: it is not in `merge_train.py owed-reds` (`ev/owed-reds.txt`) and blocks nothing.
- Untouched files. `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are identical to origin/main. Both claim files are byte-identical to the merge base (`ev/version.txt`).
- Carry check. `review_carry.py d7347d0c aa70efdd` prints `FRESH-REVIEW`, rc 1 (`ev/review-carry.txt`).
  - The cause is history, not content. `7ea3053f` merges the stale step chain `handoff-wip` (`97a33f7d` and its `wip: step` ancestors) into the branch. Their tree contributions net to nothing (proof above).
  - So the delta was reviewed by hand, as recorded here.
- Red checks. No check run exists at aa70efdd. The PR's live head is still d7347d0c, so no red at this head is owed an answer yet.
- Figures I could not re-derive at this head:
  - The body's quoted round-3 gate, score and `prepr.sh` figures. Those are the round-3 head's, which round 3 checked.
- Body inaccuracy (not a block). `## Head` says production "is unchanged from the round-3 head `4a5abf4a` except the merged main".
  - `4a5abf4a` is round 3's dispatch head. `git diff 4a5abf4a d7347d0c -- custom_components` is round 3's own fix (`pump_arbiter.py`, `store.py`, 22+/9-), which round 3 reviewed.
  - Measured against the reviewed head `d7347d0c`, the statement holds.

## Findings

- The six unpinned sites the body lists under `## Unpinned sites` (`pump_arbiter.py:1013`, `:1038`, `:1041` CMP_BOUND*2 and RETURN_DEL, `:1063`, `:1586`) are still unpinned at aa70efdd. They are shown killed by spec mutants (round 3), and pinning them is left to `mutation-autofix` on the PR head. Carry: dismissed: mutation-autofix writes the pins once the relay applies the head (ci-autofix.md); each site's kill is already shown, so it is not a survivor
