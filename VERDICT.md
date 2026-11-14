Fix review: merge d6a7b00bba95068c5236805aa0a740b792d0d954

bus-nonce: fca124fe4cbaa8cb902b9d9bdcdc53af
pending-ci: gate

## Findings

- Still open from round 1: a conflict with #3561 (a02783d4, not yet on main). It is the same adjacent-line edit in strings.json, en.json, sv.json and de.json. Round 1 measured it and resolved it by keeping both lines. This delta does not change it. Carry: dismissed: a hand resolution the orchestrator makes at the second merge, both sides kept; measured in round 1
- Still open from round 1: translations are not pinned. The written-slot arm reads only strings.json. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the written-slot set (`pump_arbiter._entities`) is narrower than the set of entities that are written. `heat_pump_switch_entity` and `dhw_disinfection_switch_entity` are not covered. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: two record rows cite strings.json `menu_options` rather than the code that builds the menu. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the `pump_duty_mode` text says "toward 5 °C", but the value is a temperature difference and should be in K. It predates the branch. Carry: R11-INTAKE-R10-RESIDUE
- Main added two hysteresis data_description texts that flow-claims.json does not cover. Its record is judged at merge base 154dbb4c. These texts are main's reviewed work, not this PR's. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Scope: a delta round over the reviewed head 9a524d703f3a25325c71f1fe888a35ab53147189. The review packet's scope line reads `delta`, and I rendered the packet at this head (ev/review-packet.md). The previous verdict (verdict/3564 at 9cdcdd2c) blocked with `ci-red` for one reason only: `tests/features.py`'s weekend-clock check, which was red at main 50373173 as well.
- RESULT delta is main's content only: head d6a7b00b has one branch-only commit. It is a merge with parents 9a524d70 and c987209c, and c987209c is current origin/main (#3578, fix/r10-hotfix-features-weekend-clock). `git merge-tree --write-tree 9a524d70 c987209c` writes tree d3323dcc3020fdce49ebbc301e2bee2538e40154, which equals the head's tree. `git show --remerge-diff d6a7b00b` shows no resolution hunks. The merge is automatic, with no branch-authored change (ev/auto_merge_check.txt). `git diff --stat 9a524d70 d6a7b00b` (12 files, +144/-20) equals main's own diff from the merge base to c987209c (ev/delta_stat.txt). It includes the tests/features.py fix (+3/-1).
- RESULT review_carry: `review_carry.py 9a524d70 d6a7b00b` prints `CARRY`, rc 0: "0 of 1 branch-only commit(s) are non-merge" (ev/review_carry.txt).
- RESULT prior findings stay resolved: the sorted +/- lines of `git diff 50373173 9a524d70 -- custom_components` and `git diff origin/main d6a7b00b -- custom_components` are identical, so the production patch is the one reviewed. The net diff against main is the same 10 files as before: strings/de/en 112 lines each and sv 110, flow-claims.{json,md,py}, delivery/3564.md, closures.json and doc_claims.py. VERSION, the manifest, RELEASE_NOTES.md and both claim files do not differ from main (ev/patch_identity.txt). No production delta, so no widening (fix-review.md step 12).
- Merge with origin/main c987209c: `git merge-tree --write-tree origin/main d6a7b00b` rc 0 (ev/merge_tree_main.txt).
- Not re-derived locally: `tests/features.py` cannot run in this container because `homeassistant` is not installed (ev/features_local_unrunnable.txt). Whether the weekend-clock check is green comes from CI's gate at this head (below).
- `tests / nightly-status` shows failure in the packet's check list. It is not in the `owed-reds` set (ev/owed_reds.txt), so it is neither answered nor a block.
- CI at this head: I polled `merge_train.py classify` from 03:07 to 03:37 UTC, 75 s apart, and every run printed `WAIT d6a7b00b… pending: gate red: none`, rc 3 (ev/classify_poll.txt). Nothing was red. The review is otherwise a merge, so I return it with the `pending-ci: gate` line, for the relay to post once the gate is green at this head.
