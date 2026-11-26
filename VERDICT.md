Fix review: merge 1a9af5fc8216e4f8044d9aa16d70ec35518272a1

bus-nonce: 92638af696ade7b1fbba167e5dcf9b76
pending-ci: gate

## Scope

Later round over the merge verdict at 54a978b5, which could not post (card C8: that head's gate concluded red). The scope is the delta `git diff 54a978b5 1a9af5fc8216e4f8044d9aa16d70ec35518272a1` (fix-review.md step 12, as the dispatch says). The rendered packet reads `## Review scope: full`, because no verdict on verdict/3874 names 1a9af5fc, which is the head this dispatch reviews. The delta is two main merges and one structure re-record. It changes no line of custom_components/ in the PR's own diff, so nothing widens the scope.

## Evidence

- RESULT interdiff: the PR's own diff, `git diff $(git merge-base origin/main H) H`, has the same 41 files and 677+/94- at 54a978b5 (merge base d3d66c40) and at 1a9af5fc (merge base dbdc520e). Diffing the two diffs with hunk headers and index lines stripped shows only these changes: the tests/structure_budgets.json rows (class_excess_loc, max_class_loc, module_excess_loc, recorded_at, unloaded_package_imports), and one context line in the D6 claims output (manifest 10.1.3 -> 10.1.4 on main). The main-merge resolutions add no PR-side change and drop none of main's content. File: ev/interdiff_54a978b5_1a9af5fc.txt.
- RESULT budgets (no raise): at merge base dbdc520e, class_excess_loc 17244, max_class_loc 7821, module_excess_loc 21762, unloaded_package_imports 5. At the head: 17237, 7817, 21759, 5. Every row is equal or lower. The -7 on class_excess_loc is the same -7 as at 54a978b5 (17290 -> 17283), re-measured on a new base: the PR's own diff is unchanged, so the movement still comes from the reviewed change (the block rule moved into external_heat.py module functions). origin/main 3ee06864 has the same budget values as dbdc520e.
- RESULT `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED` (ev/structure_head.txt). The same check passes on the tree from merging the head into origin/main 3ee06864 (ev/structure_merged_with_main.txt).
- RESULT `git merge-tree --write-tree origin/main 1a9af5fc`: exit 0, tree 9557dbe7, no conflict (ev/merge_tree.txt). The head is 6 commits behind main and merges cleanly.
- RESULT spot mutant at the head (production unchanged since 54a978b5, re-run on the new base): `features_block.py` over the #3862 block, with the prelude from `--emit-prelude` at this tree. Null: `ALL 21 FEATURES BLOCK PASSED`. M1, `external_heat.py:510` `and not ignore_effective(` -> `and ignore_effective(`: exit 1, `5 of 21 FEATURES BLOCK FAILED`, the five checks the body names (ev/m1_null.txt, ev/m1_mutant.txt). Restored after the run.
- RESULT forward-carry: `dismissed: built by #3871 at 34c7a3f610` holds. 34c7a3f610 is on origin/main as the merge of #3871. On main, heatpump-optimizer-card.js:9820 tests `ext.attributes.block_ignored === true`, and tests/card.mjs:12330-12333 covers block_ignored true and false. carry_audit at the head (packet): `1 routed, 0 unrouted, 0 bad destination(s)`.
- RESULT Red checks: the body's `## Red checks` answers the head-range reds by name. Two are the PR's own, each repaired, state (b), with its cheaper detector named. The rest are ancestry or main reds, each named as inherited. Of the reds at 7d395255, `tests / fast (3.14)` (structure, recorded in the same commit) is in the owed set (ev/owed_reds.txt). `tests / nightly-status` (red at this head in the packet digest) is not in the owed set and is owed no answer.
- RESULT VERSION, manifest version and RELEASE_NOTES heading: the delta does not touch them. The only manifest-related line in the interdiff is a context line from main.
- CI at this head: `merge_train.py classify 1a9af5fc --pr 3874` read `WAIT 1a9af5fc8216e4f8044d9aa16d70ec35518272a1 pending: gate red: none` on every run from 02:34:18 to 03:08:00 UTC, about 90 s apart. The packet's render-time digest showed `gate` failure while classify read pending, and the packet's `required-wait` advisory states that classify decides. Hence the `pending-ci: gate` line.
- Not re-derived: the body's other figures (mutation proof M2-M8, R1-R2, S1-S2, run.sh counts). They are unchanged since the 54a978b5 verdict and outside the delta; I cite them, I did not re-take them. Heavy CI runs are cited, not re-run.
- Round: second review round of this PR's code at a new head (delta round).

## Notes

- Note: stale-figure: `## Mutation proof` says `ALL 20 FEATURES BLOCK PASSED` for the #3862 block. At this head the block has 21 checks (b4b8d88a added the diagnostics check), and the null prints `ALL 21 FEATURES BLOCK PASSED`. This is paperwork (C5) and does not block. Carry: dismissed: body figure predates b4b8d88a's added check; corrected here, no later stage reads it
- Note: figure-framing: `## Head` states that 7d395255 records class_excess_loc 17281 -> 17274 and that 43be23ca moved no row. Measured against this head's merge base dbdc520e, the row reads 17244 -> 17237, the same -7. 43be23ca's resolution took main's lower values and kept the PR's -7. The figures are consistent. Paperwork. Carry: dismissed: consistent re-measure on a new base, nothing owed downstream
