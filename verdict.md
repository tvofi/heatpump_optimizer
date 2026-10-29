Fix review: merge 2a5bd4dd2dace72699a1f09709ca35d37e2e505f

bus-nonce: 6faa050b0758cb1bcd3a0c4f3390e5b0

## Scope

This is a delta review of PR #2917, round: the delta after the merge verdict at c861c0e7 (verdict ref 443b5841b). The range is c861c0e7..2a5bd4dd2dace72699a1f09709ca35d37e2e505f. That range has one branch-only commit: the head itself, a merge of main e5ddba1fa into c861c0e7. I measured head 2a5bd4dd2dace72699a1f09709ca35d37e2e505f.

## Evidence

- RESULT delta: `git diff c861c0e7 2a5bd4dd2dace72699a1f09709ca35d37e2e505f` touches only main's #2960 files (dev/audit/harnesses/r10_store_races_census.py, dev/programme/delivery/2960.md, tests/closures.json, tests/features.py). It does not touch tests/golden/claimed_drift.txt.
- RESULT automatic: `git merge-tree --write-tree c861c0e7 e5ddba1fa` writes 22949bd00. That tree differs from the head's tree by 0 lines, so the head is git's own merge with no hand resolution. The only driver line is `LEDGER-MERGE: resolved tests/closures.json` (a set merge). No MERGE-CLAIM line, because neither claim file conflicted.
- RESULT claim union: main did not touch tests/golden/claimed_drift.txt between the merge base ce5940c0d and e5ddba1fa (0 diff lines). The three-way result is therefore the branch side. Its sha1 is b666993f1 at both c861c0e7 and the head, so the file is byte-identical to the one the previous merge verdict measured. Under claim-files.md this merge reinstates no claim and drops none. The branch's own claim delta against the merge base (the R10-COP-GATE coord_* claims, and 535015a87 restoring the six may-drift entries) is the change already reviewed at c861c0e7. claims-for is 7.0.5, and VERSION is 7.0.5 at every end.
- RESULT claims hygiene: `python3 tests/env_drift.py --claims-only` at the head prints `claims hygiene: origin/main ok`.
- RESULT own diff: the branch's diff against its merge base with origin/main, with the index and @@ lines dropped, is identical at c861c0e7 and the head (OWN-DIFF-EQUAL, 1312 lines).
- RESULT version: VERSION, the manifest and RELEASE_NOTES.md are not in the branch's diff.
- RESULT mergeability: `git merge-tree --write-tree origin/main 2a5bd4dd2dace72699a1f09709ca35d37e2e505f` (main 7274f7f6e) exits 0. It resolves tests/structure_budgets.json and tests/closures.json through LEDGER-MERGE, and the claim file has no conflict. main changed nothing under tests/golden/ from e5ddba1fa to 7274f7f6e.
- RESULT CI at the head: run 40956132607 (CI code) has one red job of 40, `tests / nightly-status`. It grades main's scheduled Nightly, and the body's `## Red checks` answers it. Every other job is success or skipped. Run 40956132011 (CI edit) is success.
- RESULT review_carry at c861c0e7 to the head prints FRESH-REVIEW: "resolves tests/golden/claimed_drift.txt to something other than the union of its parents". That is the instrument's line-set union, explained under Findings, not a resolution this merge authored. This review is the fresh review it asks for.
- Head moved after dispatch: the PR head is now a361e454f1058a44e7c545270dc66a1b8330f3f3. It is github-actions[bot]'s "ci: merge main" of 2033b876e onto 2a5bd4dd2dace72699a1f09709ca35d37e2e505f, not a branch-authored commit. I checked it as a resolution delta. It is the automatic merge-tree of its parents (0 diff lines). claimed_drift.txt is unchanged from 2a5bd4dd2dace72699a1f09709ca35d37e2e505f, and VERSION is still 7.0.5. review_carry refuses it as FRESH-REVIEW for the same instrument reason. This verdict names 2a5bd4dd2dace72699a1f09709ca35d37e2e505f as dispatched. CI on a361e454f was still queued at review time.
- Not re-derived: the fix's figures, mutants and harness rows were verified at the previous merge verdict, and this delta changes no line of the branch's own diff. I re-ran none of them here.

## Findings

- review_carry.py, through app_approve.sh's claim-file check (tools/pr/app_approve.sh, around line 285), takes the "union of its parents" as the sorted set of non-empty lines of both parents. It does not take the three-way result. So a main merge whose main side never touched the claim file is refused whenever the branch itself deleted lines that the merge base still has. On this PR that is main's R10-HOUSE-GRADE and R10-BUFFER-STORE claims, which this branch dropped in 535015a87 as inherited, and their suspended may-drift comments. The refusal hit both e5ddba1fa and a361e454f. It forces a fresh review on every automatic main merge of this PR, and on any branch that drops inherited claims. The fix is to compare the claim file with the claimnotes driver's three-way result, or with `git merge-file --union` against the merge base, instead of a two-parent line set. Carry: R10-REVIEW-CARRY
