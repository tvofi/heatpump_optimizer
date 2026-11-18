Fix review: merge 731ceaa3d3505006973cef6b213a84cda4569acc

bus-nonce: f90bf2e49cc8a9b00eb086344e41b88f
pending-ci: gate

## Scope
Later round (round 2) over reviewed head 9371c9e6a3a76f37fe522501881285df1df89099; packet scope `delta`. The delta is one commit (731ceaa3d, "Restore main's one-line delivery rows 3451, 3521, 3593"), three deletions under dev/programme/delivery/. It touches no production code (custom_components/), so the review stays at the delta.

## Previous verdict
The previous block (merge-resolution: 3451.md, 3521.md and 3593.md held two lines each) is resolved. At this head each of the three files is byte-identical to origin/main (9fe63d00b5), is one line, and has dropped out of the PR's three-dot diff.

## Evidence
- RESULT: delta: `git diff 9371c9e6..731ceaa3` deletes the duplicated line from each of the three row files and changes nothing else (ev/delta-check.txt).
- RESULT: PR diff at head, three-dot: CLOSEOUT-REPORT.md, HANDOVER.md, delivery/3590.md, delivery/3608.md, rosters/wave-r10-groups.json. 3590.md and 3608.md are one line each.
- RESULT: `git merge-tree --write-tree origin/main 731ceaa3d3` exits 0 (tree a807c9382a), so there is no conflict with main.
- RESULT: review_carry.py 9371c9e6 -> 731ceaa3 prints FRESH-REVIEW. That is expected: the previous verdict was a block, so no merge verdict carries forward.
- RESULT: review packet carry_audit has 0 findings; figure_lint has 3 resolved, 1 not verified (the `git diff --stat` flags, which the instrument does not check), 0 refused.
- CI: `merge_train.py classify` was polled every ~60 s from 15:21 to 15:51 UTC and printed `WAIT 731ceaa3d3505006973cef6b213a84cda4569acc pending: gate red: none` every time, so no red was seen (ev/classify.log). This head is returned with `pending-ci: gate`.

## Notes
Note: figure: the body's `git diff --stat origin/main...HEAD printed 8 files` is 5 at this head (three-dot vs merge-base 5825e1346c), and the Summary's five delivery rows (#3451, #3521, #3593, #3606, #3607) are no longer in the PR's diff, because main already carries them; only #3590 and #3608 change. The body is stale, the content is correct.

## Findings
none
