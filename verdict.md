Fix review: merge f5c4a8c75b4d796b3d0001e5a37ee08408cc590a

bus-nonce: 18f1de0a52245381d4ede41afb8094b5

## Round

This review covers PR #3050 (R10-CEILING-PROBE) after the round-3 block, the re-cut fixer.md owes from the fourth round. The body carries `## Re-cut`.

- Measured head: f5c4a8c75b4d796b3d0001e5a37ee08408cc590a. `refs/pull/3050/head` still read that SHA when I wrote this verdict (`ev/head_at_post.txt`).
- The head is an automatic merge of the fixer's handoff deceb3de7 into the previous head 2be13c572. Its tree is identical to deceb3de7 (`git diff deceb3de7 f5c4a8c` is empty), and `review_carry.py deceb3de7 f5c4a8c` prints `CARRY` (`ev/review_carry.txt`). The head did not move under the handoff.
- Merge base: d052f80f7, which is origin/main's tip, so the branch is 0 commits behind. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current.
- I judged from detached worktrees at the head, using the round-3 reviewer's finder harness from refs/heads/verdict/3050 (`evidence/null_rewrap_r3.diff` and `evidence/mut_median_p90.diff`, copied here to `ev/`), not the fixer's.

The re-cut (`git diff 2be13c572 e81bf9dbf`, `ev/recut_diff.txt`) touches three files, with 18 insertions and 9 deletions:
- In `coordinator.py`, the production change is byte-for-byte the round-3 null re-wrap.
- `tests/features.py` changes the `_P5_CONSULT` marker and adds one item-29 check.
- `tests/structure_budgets.json` is re-recorded.

## Round-3 block items, judged at this head

1. **metric-gamed (structure layout): settled.**
   - The arm call and the `hold_reason` call are laid out normally, exactly as in `ev/null_rewrap_r3.diff`.
   - e81bf9dbf re-recorded the budgets at 8054 / 17647, and its commit message gives the reason.
   - The ledger driver composed main's own -3 / -2 delta into the merge to give 8051 / 17645 (`ev/remerge_deceb3de7.txt`).
   - `python3 tests/structure.py` at the head passes with `max_class_loc=8051` and `class_excess_loc=17645`, both at zero headroom, so the recorded figures are the measured ones (`ev/structure_head.txt`).
   - Three-dot against main, `max_class_loc` goes 8056 → 8051 and `class_excess_loc` 17651 → 17645, and no key rises. This is not a raise.
   - The body's `-10` figures are gone; it now says -5 / -6.
2. **#1523 marker: settled.** `_P5_CONSULT` is now the call expression `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)` alone, which occurs exactly once in coordinator.py.
   - The whole `tests/features.py` passes in both layouts:
     - At the head: `ALL 4742 FEATURE CHECKS PASSED`, rc=0.
     - At the head with the re-wrap reverted to the old hugging layout: also `ALL 4742 FEATURE CHECKS PASSED`, rc=0.
     - The null-control row is `ok` in both (`ev/features_wt_summary.txt`, `ev/features_wt_hug_summary.txt`).
   - I also replaced that consult in the `hold_reason` call with `None` (`ev/mut_consult_none.diff`). The whole suite then reads `6 of 4742 FEATURE CHECKS FAILED`, including the #1523 class check and its null control (`ev/features_mut_consult_none_summary.txt`).
3. **Median against an upper quantile: settled.** The added check is `_cp_store([3.0]*9 + [4.0]*3).learned_max_kw(_CP_NOW) == 3.0`. With the round-3 p90 mutant planted:
   - The block reads `1 of 62 FEATURES BLOCK FAILED`, and the failing row is the new item-29 check (`ev/block_p90.out`).
   - The whole suite reads `1 of 4742 FEATURE CHECKS FAILED` (`ev/features_wt_p90_summary.txt`).
   - Unmutated, the block reads `ALL 62 FEATURES BLOCK PASSED` (`ev/block_head.out`).

The re-cut introduced nothing else. The merge resolution of deceb3de7 keeps both tail blocks in `tests/features.py`, and the two ledger files were resolved by the driver (`ev/remerge_deceb3de7.txt`).

## Findings

none

## Evidence

- RESULT head f5c4a8c75b4d796b3d0001e5a37ee08408cc590a (`ev/HEAD.txt`), merge base d052f80f7f81d42db5c57a55ebaef7056c7ce01a.
- RESULT structure: `STRUCTURE RATCHET PASSED`, with max_class_loc=8051 and class_excess_loc=17645 (`ev/structure_head.txt`).
- RESULT whole features at the head: 4742 of 4742 pass. Under the hugging layout: 4742 of 4742 pass. Under the p90 mutant: 1 of 4742 fails. Under consult→None: 6 of 4742 fail.
- RESULT finder harness `dev/audit/harnesses/ceiling_probe.py` (blob d1101c541b57). I copied it into a merge-base worktree because main does not have it (`ev/harness_wt.txt`, `ev/harness_wt_base.txt`). Readings, base → head:
  - duty: None → 'space'. The null arm reads 'idle' at both ends.
  - draw: flat at both ends, by design.
  - level: 35/35/35 → 55/38/25.
  - store: absent → learned top 3.0.
  - Every reading matches the body.
- RESULT `archscore --diff d052f80f7`: `dS +0.0006 IMPROVES` (`coord_footprint 2387 -> 2386`), which matches the body (`ev/archscore.txt`).
- RESULT scoped gate: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (`ev/closure_select.txt`).
- RESULT guard pins: `ALL 61 GUARD PIN CHECKS PASSED` (`ev/guard_pins.txt`).
- RESULT `env_drift.py --all d052f80f7`: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc=0 (`ev/env_drift_all.txt`). `tests/golden/claimed_drift.txt` carries the branch's own five `coord_*` claims, so it is deliberately not byte-identical to main. `claims-for: 7.1.0` equals `VERSION`. `git diff 2be13c572 HEAD -- tests/golden/` is empty. `card_claimed_drift.txt` is not in the three-dot diff.
- RESULT `VERSION`, the manifest and `RELEASE_NOTES.md` are not in the three-dot diff. `dev/programme/delivery/3050.md` is in it.
- RESULT `git merge-tree --write-tree origin/main f5c4a8c`: exit 0, clean (`ev/merge_tree.txt`).
- RESULT CI on this head, all 55 check runs on one page (`ev/checks.txt`): every run concluded success, skipped or neutral, and none is red. This includes:
  - `tests / fast (3.14)` 124920331713
  - `tests / mutation` 124920199562
  - `pr-contract / pr-contract` 124940588826
  - `gate` 124940794420
- RESULT `merge_train.py classify` exited 0 with `GREEN f5c4a8c75b4d796b3d0001e5a37ee08408cc590a pending: none red: none` (`ev/classify.out`, `ev/classify.log`).
- RESULT `## Red checks`: no check is red at this head, so none is owed. The two history reds the body names (mutation-autofix and fast at 08c2477f2) are answered there with a cheaper detector, and the green `pr-contract` run is the evidence for the range.
- RESULT body figures I did not re-derive here: the 79-site mutation inventory (76 killed by the block, plus two killed by the whole suite and one triaged as equivalent), and the step-8 enumeration grep counts. Round 2 verified both. No production operator changed after round 2 (the re-cut is layout only), and `tests / mutation` is green at this head.
- RESULT forward carries to R10-COP-GATE-D: `carry_audit` at the head reports 2 routed and 0 unrouted (review packet).
