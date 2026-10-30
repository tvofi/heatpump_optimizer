Fix review: merge 967abc3e9c7ca6d224ba5d55cee77145d109ea3b

bus-nonce: 71cf3f6a82fa74f4f832f51cbca48cb8

## Scope

Resolution-delta review of PR #2977, from the merge verdict at 9f0e4478d5413192a34603698fedaa9dfd3cd93a to head 967abc3e9c7ca6d224ba5d55cee77145d109ea3b (fix-review.md step 12). This is the second verdict on the branch, not a fourth round. The delta is one commit: 967abc3e9, which merges main 1148ee635 into 9f0e4478d. `dev/governance/roles/` on main has not changed since the merge base, so the contract I used is current.

## Evidence

- RESULT review_carry (main's copy): FRESH-REVIEW, "resolves tests/golden/claimed_drift.txt to something other than the union of its parents". This is the defect the PR fixes, P290. Main's driver takes the claim list from the side that changed it, while the old carry rule compared against the line union.
- RESULT review_carry (head's copy): CARRY. `app_approve.sh --carry 9f0e4478d 967abc3e9 origin/main` returns rc 0 with "CARRY: yes ... claim files a pure union of both sides or main's driver output on them, and the branch's own diff compares equal" (ev/app_approve_carry.txt).
- RESULT resolution: `git merge-tree --write-tree 9f0e4478d 1148ee635` (claimnotes driver installed) gives tree cbf87928094dae89528a98c2db5de18239daa8e1, which is identical to the head's tree. Without the driver the tree is the same. No `MERGE-CLAIM:` line on stderr and no conflict. The merge adds no hand resolution (ev/remerge_parents.txt).
- RESULT claim list: the branch never touched `tests/golden/claimed_drift.txt` (empty diff from merge base 043b111d0 to 9f0e4478d). At the head the file is byte-identical to main 1148ee635, and `card_claimed_drift.txt` is identical too (ev/claimfiles_main_vs_head.diff). The claim list is therefore exactly main's claims plus this branch's own, which are none. That is the shape `claim-files.md` asks of a branch that claims nothing.
- RESULT branch's own diff: `git diff 043b111d0 9f0e4478d` and `git diff 1148ee635 967abc3e9` are identical once index lines are ignored (ev/own_at_P.diff, ev/own_at_H.diff). The same 6 files change, with 86 insertions and 13 deletions. The reviewed code did not change.
- RESULT mutation (delta-relevant): I put main's `tools/pr/app_approve.sh` in place at the head. The head's `review_carry.py` then printed FRESH-REVIEW for this very range, and printed CARRY again after I restored the file (ev/mutant_main_app_approve.txt). The fix is what turns this range from refused to carried.
- RESULT self-tests at head: `bash tools/pr/app_approve.sh --self-test` gives 271 checks, 0 failed. `python3 tools/audit/seat/review_carry.py --self-test` gives 26 checks, 0 failed. Both match the body's figures.
- RESULT merge with current main: `git merge-tree --write-tree origin/main 967abc3e9` against origin/main aced25893 exits 0 with empty stderr (ev/mergetree_main.txt).
- RESULT CI on 967abc3e9 (check-runs API, 42 runs): every run is completed. Each is success or skipped, with no failure, cancellation or pending run. That includes gate, pr-contract (started 08:24:43Z, after every other run had concluded), tests / fast (3.14), closures, coverage, mutation, instrument-self-tests, policy-docs, budget-raise-gate and arch-score. The body's `## Red checks: none` matches.
- RESULT the head named in the body is 967abc3e9c7ca6d224ba5d55cee77145d109ea3b, and it is still the live branch head (ls-remote).
- RESULT VERSION, RELEASE_NOTES.md, the manifest and tests/golden/ are untouched across the three-dot range.
- The merge commit's author is tvofi, from the orchestrator's train merge. I record this as fact and judge nothing on it, since the train's merge identity is outside this delta.
- review_packet.py rendered with exit 0. FIGURES: 12 resolved, 3 not verified, 0 refused; I did not re-derive the 3 it left unverified, because the delta does not touch them. ev/review-packet.md.
- Not re-run (cited from the prior verdict at 9f0e4478d, since the code is unchanged): the body's M1–M3 mutants, the replay of the four #2917 merges, and the entities/structure figures.

## Findings

- The PR touches `dev/governance/roles/orchestrator.md`, which is policy, and the body's `## Approval` says the owner's approving review is still owed before merge. That is a merge precondition enforced by the code-owner rule in main-protect-checks, not a defect in this delta. Carry: dismissed: owner approval is gated by main-protect-checks' code-owner review, not handed to a later stage
