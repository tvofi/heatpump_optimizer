Fix review: merge 1b44f40575abf76c4d55f16dd96cbbbbb2436ba7

bus-nonce: 00e6569209581bc10a1c92aa09e41849
pending-ci: gate (classify printed WAIT, pending, gate red: none)

Continuation of the finished review at 0cd785173433173b4f6e9d16a1b161bef464c516, which stands. The head moved only by one automatic merge of origin/main, so the review carries.

## Evidence

- Scope: the delta 0cd785173433..1b44f40575abf76c4d55f16dd96cbbbbb2436ba7 is one merge commit whose second parent 046736a49f8c is an ancestor of origin/main (ev/parents.txt). No fixer commit; `git log 0cd785173433..1b44f40575abf76c4d55f16dd96cbbbbb2436ba7 --not origin/main` lists only that merge.
- `review_carry.py 0cd785173433 1b44f40575abf76c4d55f16dd96cbbbbb2436ba7` prints CARRY (ev/review-carry.txt).
- Branch's own diff, merge-base 61afd4f2db10..0cd785173433 against merge-base 046736a49f8c..1b44f40575abf76c4d55f16dd96cbbbbb2436ba7: every added and removed line is identical, 16 files, 489 insertions and 7 deletions (ev/added-removed-old.txt, ev/added-removed-new.txt). Only main's own changes entered.
- The merge touched tests/closures.json by the ledger merge driver and no other resolution.
- `git merge-tree --write-tree origin/main 1b44f40575abf76c4d55f16dd96cbbbbb2436ba7` is clean (ev/merge-tree.txt); origin/main is 046736a49f8c, the head's second parent, so the head is not behind main.
- No production (custom_components/) file is in the delta, so nothing widens the review (fix-review.md step 12).
- CI: classify at this head printed `WAIT 1b44f40575abf76c4d55f16dd96cbbbbb2436ba7 pending: gate red: none` on both polls, about 100 s apart (ev/classify.txt); no red.

## Findings

none
