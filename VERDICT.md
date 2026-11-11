Fix review: merge 0ceea2fd3f843a29b155631bd4d2c52a4af654ef

bus-nonce: 0c5a1c1c26df916112522ef81aefdfe6

Round 1 (handoff review, no pull request yet). Head measured: 0ceea2fd3f843a29b155631bd4d2c52a4af654ef; origin/main is 0a2139b1 and `git merge-tree --write-tree origin/main <head>` exits 0 (clean tree 903d2390).

## Evidence

- No review packet and no CI exist before the PR opens; nothing waited on. `merge_train.py owed-reds` prints tests / mutation, tests / typing, validate / validate-hacs; the body's "Red checks: none" is vacuous pre-PR and unanswerable now.
- RESULT head: `roster_edit --self-test` = 280 checks, 0 failed (ev/head-selftest.txt). Base (merge base ee64358b): 277 checks, 0 failed, so the 3 added checks are the only delta (ev/base-selftest.txt).
- RESULT mutation (my own run): replaced `if len(exact) == 1:` with `if False:` in `_carry_index`: 280 checks, 2 failed: "drop-carry --match equal to a carry inside a sibling is that carry" and "drop-carry --match unique substring still resolves" (ev/mutant.txt). The first reproduces the base behaviour (ambiguous refusal), so it is the null control; restored, 0 failed. No survivor.
- Null arms confirmed in the diff: a match equal to no carry that hits two ("zeta") still refuses as ambiguous; a unique substring still resolves. Two identical duplicate carries give len(exact)==2, so they fall through to the ambiguous refusal (unchanged).
- Diff is one file, tools/audit/seat/roster_edit.py (+21/-2); no VERSION, manifest, release-notes, golden, claim file, budget or closures change (ev/files.txt), so steps 4, 5 and 14 have nothing to move.
- Body figures re-derived: 280/0 at head. The `prepr.sh` rc=0 and `MODE: SCOPED` lines I did not re-run (heavy gate); not re-derived.
- Class rule: the finding names one seam (`_carry_index`, shared by drop-carry and mark-carry); a one-seam class. mark-carry has no direct exact-match check, but it calls the same helper that the mutant above breaks.
- Forward-carry: body says none; the change narrows no later stage. Out-of-scope items (filtering marked carries, `replay_unsafe`) are briefed out and not claimed fixed.
