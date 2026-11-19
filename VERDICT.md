Fix review: merge 8ad37dc99944f5e0db46d6f04562a65ff2bbe916

bus-nonce: 60c1c9d0d54319a3a7a612d878a69e90

Round: delta review (fix-review.md step 12) over the reviewed head 9371c9e6a3a76f37fe522501881285df1df89099, the newest posted verdict (blocked). It is the PR's fourth review dispatch and its second blocked-or-later round, so no re-cut is owed. The confirmed merge verdict at 731ceaa3d3505006973cef6b213a84cda4569acc (verdict/3608 tip 66c065707c80) cannot post because its head's gate concluded red (card C8). This review re-issues that verdict at the live head, which is green.

RESULT prior-finding: resolved. dev/programme/delivery/3451.md, 3521.md and 3593.md each hold one line and are byte-equal to origin/main, so the PR's three-dot diff no longer touches them (evidence/prior-finding.txt).
RESULT delta 9371c9e6..731ceaa3: one commit. It deletes the second (unioned) line from each of those three row files and changes nothing else.
RESULT delta 731ceaa3..8ad37dc9 (the main merge): git merge-tree --write-tree 731ceaa3 fd847a55 gives tree 812e4564bf, which is exactly the head's tree. So the merge is git's automatic one with no hand resolution. The branch's own patch against main is identical before and after the merge (the diff from merge base to head, index lines aside). review_carry.py 731ceaa3 8ad37dc9 answers CARRY (evidence/merge-resolution.txt, evidence/review-carry-731ceaa3.txt).
RESULT conflict: git merge-tree --write-tree origin/main(1723f9fdc9) 8ad37dc9 exits 0.
RESULT live checks: merge_train.py classify --pr 3608 at 8ad37dc9 reads GREEN with no required context pending or red (evidence/classify-head.txt). tests / nightly-status is red and is not a required context.
RESULT version: VERSION, the manifest and the RELEASE_NOTES.md heading are absent from the three-dot diff.
RESULT scope: the three-dot diff contains only records: dev/audit/rounds/round10/CLOSEOUT-REPORT.md, dev/programme/HANDOVER.md, delivery rows 3590 and 3608, and dev/programme/rosters/wave-r10-groups.json. It changes no production, test, instrument or policy path, so steps 1-4, 6, 9, 14 and 16 have nothing to measure (no mutation target, finder's harness, claim file or actuator write). Nothing in the delta widens the review.
Note: body: the Delivery rows paragraph says nothing is added for #3590, but the three-dot diff rewrites dev/programme/delivery/3590.md from main's malformed open row to merged `ee9e233`. The new row is one line and correct.
