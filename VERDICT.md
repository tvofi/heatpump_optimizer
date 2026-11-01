Fix review: merge 46c2ac3b4271c268014c13ac0334c56c33dde2d7

bus-nonce: 71417863adc4ed3ef2fc8408f9d9ba0f

Narrow resolution-delta re-check of the prior block (root-cause-unanswered, `governance / instrument-self-tests` at b8353012f530). Code findings of the earlier review stand; code was not re-reviewed.

## Findings

none

## Evidence

- Item 1, answer present: the body's `## Red checks` answers `governance / instrument-self-tests` at each head it was red at. e24686de4679 and 0c38d4ccd648 (jobs 124673785214, 124673797179, 124744747052): cause is the unrecorded `class_excess_loc` gain, repaired at b8353012f530. b8353012f530 (job 124797544268): cause is the uutils `sleep` refusing the renamed symlink. Check-runs API (all pages) shows the failures at e24686de4679: gate, instrument-self-tests, pr-contract, tests / fast (3.14); at 0c38d4ccd648: the same four; at b8353012f530: gate and instrument-self-tests. Every one is named in the section (gate and pr-contract as downstream of the two others).
- Cause verified in the failing job log (124797544268): `Image: ubuntu-26.04`, `Security violation: Requested utility \`unrelated-sleep\` does not match executable name`, `FAIL open_pr: the null control -- an unrelated sleeper survives`, `FAIL null control: a normal successful update_pr ...`, `pr_args self-test: 158 checks, 2 failed`.
- 1a8051350 (#3086) is on origin/main and touches tools/audit/seat/pr_args.sh (4 lines). It is not an ancestor of the live head; the head still has pr_args.sh:625 `ln -s /bin/sleep`. The body does not name #3086, only the cause and a forward-carry to R10-FLOW-BODY-ONLY, which is now superseded by #3086; that is a wording lag, not an unanswered red.
- Red at the live head: none. Live-head job 124844620343 ran on `Image: ubuntu-26.04` and ended `pr_args self-test: 158 checks, 0 failed`; `merge_train.py classify` exits GREEN (`pending: none red: none`), so no check concluded red at this head. (The fixture passes here with the symlink unchanged; I did not establish why the same image now passes, and the green does not depend on it.)
- Item 2: `review_carry.py b8353012f..46c2ac3b4271c268014c13ac0334c56c33dde2d7` prints CARRY (3 branch-only commits, all automatic merges). `git log --no-merges` over branch-only commits in the range is empty (the unqualified range lists main's own commits arriving through the merges). `git merge-tree --write-tree origin/main` exits 0 (LEDGER-MERGE resolved tests/closures.json).
- Item 3: the body's `## Head` names 46c2ac3b4271c268014c13ac0334c56c33dde2d7.
- Head re-read: 46c2ac3b4271c268014c13ac0334c56c33dde2d7 is the PR head at posting.
