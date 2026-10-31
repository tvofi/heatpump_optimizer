Fix review: merge 4522a316c00e4c3394a8f22cad446d9543979e42

bus-nonce: 52f1c57719bb7a725059e65554e2621b

## Verdict

Round 4, delta b63829d1..head only. The authored delta a44b8c7af is one line of tools/audit/seat/instruments/cancel_superseded.py.md (1 insertion, 1 deletion); the rest of b63829d1..4522a316c00e4c3394a8f22cad446d9543979e42 is two merges of main (3010, 3012 and later main). The instrument code is unchanged.

## Findings

- `ci_predict.wiring_preds` keeps only UNWIRED lines, so a MISMATCH, UNINDEXED, DUPLICATE or MISSING line from `selftest_wiring.py --check` printed "no instrument red predicted" in prepr. Reproduced in the PR body's account; not this PR's to fix. Carry: R10-FLY-CIPREDICT-GAPS
- Part 2 of this group (CI-priority tier module, its config file, merge-train pause/resume) is owed in a follow-up PR; the tier-module disposition stands. Carry: R10-FLY-CANCEL-SWEEP

## Evidence

- Merge with origin/main: `git merge-tree --write-tree origin/main 4522a316c00e4c3394a8f22cad446d9543979e42` is clean (origin/main has moved to 5d4e0bcfb since the head's last main merge).
- `selftest_wiring.py --check` at the head: 103 self-testing, 103 wired, 0 unwired, 0 index gap(s). With cancel_superseded.py.md reverted to b63829d1: `MISMATCH ... the index line's name is not the one its entry opens with`, 1 index gap(s). Restored, tree clean. (ev/wiring_head.txt, ev/wiring_reverted.txt)
- `python3 -I tools/pr/cancel_superseded.py --self-test`: 44 checks, 0 failed at the head (matches the body).
- CI on this head: merge_train.py classify exits 0 GREEN. `governance / instrument-self-tests` completed success (it was the round-3 red). The remaining required jobs were green or skipped; pr-contract was the last to finish.
- `## Red checks` in the body names the red as this diff's own, corrects the round-3 claim, names the cheaper detector (selftest_wiring --check), the process state (detector ran, filter narrower than the check) and the countermeasure routed as its own group. That answers the root-cause trigger.
- Code owner: tools/pr/cancel_superseded.py is code-owned, so tvofi's approving review is required at merge. Flagged, not a block.
- review_packet render: no refusals, no advisories; figure_lint 3 resolved, 0 not verified.
