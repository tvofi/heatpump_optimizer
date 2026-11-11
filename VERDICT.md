Fix review: merge 55da6b61abeef2000913e7a7847490505dd8bb82

bus-nonce: 4fdf90ddd683fa7951a400889764694e
pending-ci: gate

## Summary
Delta carry review. The branch's own content at 55da6b61abeef2000913e7a7847490505dd8bb82 equals what was reviewed at handoff 580f12908056021e9448d5f0520919044e6de41a (previous verdict: merge 580f1290). No real change; no code re-reviewed.

## Evidence
- Ranges compared three-dot: `6cc15e9b...55da6b61abeef2000913e7a7847490505dd8bb82` against `0a2139b1...580f1290`. Both are 17 files, 409 insertions, 28 deletions, identical name-status lists (ev/name-status-*.txt).
- Added and removed lines, file by file, are byte-identical (ev/changed-lines-diff.txt is empty). Whole-patch diff differs only in index hashes, hunk offsets, and one context line (ev/patch-diff.txt).
- Differences by cause: index hashes and hunk line offsets (const.py +4, others) come from main's merged commits shifting the base; the one text difference is a context line in const.py comment ("On the reporting install the two limits are smart-home interface inputs 10104" vs "On a Luxtronik ... Smart Home Interface inputs 10104"), which is main's own wording changed by a merged main commit and not a branch line.
- Delivery row: dev/programme/delivery/3469.md is already within the 17 files in both ranges and is unchanged between them. The remerge added delivery rows 3423..3474 and the v7.1.11 stamp, all main's, none in the branch diff.
- Main-merge resolution: remerge 5c728b210 and 55da6b61a are clean; `git diff 6cc15e9b 55da6b61abeef2000913e7a7847490505dd8bb82 --stat` is the same 17 files, so no resolution edit touches branch files. `git merge-tree --write-tree origin/main 55da6b61abeef2000913e7a7847490505dd8bb82` exits 0 (merges cleanly with origin/main 5cc6f6f2).
- CI at this head: `merge_train.py classify` printed `WAIT 55da6b61abeef2000913e7a7847490505dd8bb82 pending: gate red: none` on repeated runs (exit 3). No red. Returning with pending-ci per the brief.
- owed-reds was not printed to completion (not needed: no red).
- The review_carry FRESH-REVIEW answer is explained by the changed base (hunk offsets, index hashes, one main-side context line), not by branch content.
