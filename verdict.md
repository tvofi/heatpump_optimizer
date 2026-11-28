Fix review: merge a7f972ae474f457c2f6f80a7c87cb2f37f9b853d

bus-nonce: 78e72cb4de8bba4fac8fbe9389bd56cc
pending-ci: gate

## Scope

This is a later round over the reviewed head 375a0057b65a828edfaf7ffa7484d137bcae28e4, which was blocked as `test-gap` (fix-review.md step 12). `review_carry.py 375a0057b6 a7f972ae47` prints `FRESH-REVIEW`. The review covers the delta and the previous block:
- `af730f110e` and `eef5468f03` change only `tests/features.py`, with 34 lines added. `git diff 375a0057b6 eef5468f03 -- custom_components` is empty. The two commits add check 2d, "through the planner", which is the planner-level check the previous verdict's `## Block` asked for.
- `f99b0ecd35` merges origin/main `98541868ad` (#3925, the two-zone presence gate), and `a7f972ae47` merges `f99b0ecd35`. For each merge, `git merge-tree --write-tree <parents>` gives the tree `2e79d94db3`, which is the commit's own tree. Both are automatic merges, and the ledger driver resolved `tests/structure_budgets.json` (`LEDGER-MERGE: resolved`, module_excess_loc 21647).
- #3925's production change is the zone-presence readers in `coordinator.py`, `services.py`, `thermal_model.py` and `payload.py`. None of that code is on the hot-water charge path this PR changes, so it puts no reviewed functionality at a non-obvious risk and the scope is not widened.

## Findings

- Note: body-stale: the PR body does not name the round's new planner-level check, or the P1/P1b kill that settles the previous `test-gap` block. Its `## Raise justification` names `af730f110e` and `eef5468f03` only for their line count. The commit message of `af730f110e` carries the account. Carry: dismissed: paperwork on this PR's own body, settled by this verdict's Evidence; nothing downstream reads it
- `tools/audit/seat/review_packet.py render --pr 3805 --head a7f972ae47... --reviewed-head 375a0057b6...` again wrote no packet: `review_packet: UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster: fatal: Not a valid object name b2ce461c`. The failure persists after fetching `handoff/audit-r11-roster`. `b2ce461c` is a body-item id in `dev/programme/rosters/wave-r11-groups.json`, not a commit, and the packet reads it as a SHA. The scope above was derived by hand. Carry: dismissed: an instrument defect outside this PR's diff, reported for the dispatcher; the review it blocked was done by hand

## Evidence

- RESULT head-reviewed=a7f972ae474f457c2f6f80a7c87cb2f37f9b853d (`ev/HEAD.txt`). The PR's `head.sha` reads the same, and so does the body's `## Head`.
- RESULT mutation proof of the previous block (`mutant_run.py --spec ev/spec.json --cmd 'bash ev/block.sh'`, copy-tree, Linux venv-ci, OPENBLAS_CORETYPE=Haswell; `ev/features_mut.log`). The NULL SURVIVED, so the group's features block passes unmutated at the head. `P1_planner_drops_running` was KILLED. `P1b_planner_running_true` was KILLED. Both survived at 375a0057b6. `NC1_refusal_call` was KILLED.
- The driver reached its background time limit before it ran `NC2_mask` and `NC3_drop_unstartable`. Both were KILLED at 375a0057b6 (previous verdict, `ev/features_mut_nc.log` on `probe/rev-3805-0bf2753a`). The delta writes no production line, so those kills stand unchanged.
- RESULT `git merge-tree --write-tree origin/main a7f972ae47` exits 0. origin/main is `98541868ad`, the head's own merged parent. No conflict.
- RESULT `python3 tests/structure.py` at the head: `ok module_excess_loc 21647 <= 21647`, `ok methods_over_200 6 <= 6`, `STRUCTURE RATCHET PASSED` (`ev/structure.log`).
- Main's budget at `98541868ad` reads module_excess_loc 21598 and methods_over_200 7. That re-derives the body's `21598 -> 21647`, +49 over main, for the raise that was already reviewed. The delta's own commits add no module line, and the head's 21647 is below 375a0057b6's 21649.
- RESULT `tests/comment_ratchet.py`: `long_units_base=2294 long_units_head=2294`, `comment_ratchet: OK` (`ev/comment_ratchet.log`). `eef5468f03`'s stated repair holds.
- RESULT the delta touches neither VERSION, nor manifest.json, nor the RELEASE_NOTES.md heading. It touches no claim file and no golden fixture, so no drift re-check is owed beyond the previous round's `NO UNCLAIMED DRIFT: 56`.
- CI: `merge_train.py classify a7f972ae474f457c2f6f80a7c87cb2f37f9b853d --pr 3805` printed `WAIT a7f972ae474f457c2f6f80a7c87cb2f37f9b853d pending: gate red: none` (rc 3) on every poll from 14:40 to 15:12 UTC (`ev/classify_poll.log`). There is no red, so no `## Red checks` answer is owed. The verdict carries `pending-ci: gate`.
