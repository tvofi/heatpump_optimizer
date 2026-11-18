Fix review: merge 6a21c2886a246f440be4870e093616ceea80265a

bus-nonce: c1385bf3cdaa63ffe6b607c2b407fcee

## Scope

Round 1, full review (no prior reviewed head). Merge base 83b9012d61eb9dba11c265cf987dd1d5960c8c96. The three-dot diff touches two files: `dev/audit/harnesses/r11_honest_starts_runs_mutants.json` (re-anchored spec, carry 5) and `dev/programme/delivery/3720.md` (delivery row). No production, test or budget file moves. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 6a21c288` exits 0 (tree 9fb124e5c3), no conflict (ev/merge_tree.txt).
- RESULT CI: `merge_train.py classify 6a21c288 --pr 3720` prints `GREEN 6a21c2886a246f440be4870e093616ceea80265a pending: none red: none`, rc 0 (ev/classify.txt). `tests / nightly-status` is red in the packet digest but is not in the `owed-reds` set (ev/owed_reds.txt), so it is owed no answer.
- RESULT step 1, mutation proof at the head: `mutant_run.py --spec ev/four.json` (the four re-anchored entries, extracted unchanged from the head spec) with the body's `features_block.py` command prints `SURVIVED NULL`, then `KILLED` for ENGAGED_COST_ARM, ENGAGED_CLAMP_ARM, UNPRICED_DESCENT and UNPRICED_DESCENT_COST_ARM, rc 0 (ev/mutant_run.txt). This matches the body.
- RESULT carry 5 enumerator (re-derived under the body's rule: an entry whose `old` occurs other than once in its `file`): the head spec over head code gives 53 entries, 0 refused. The merge-base spec over head code gives 54 entries, 5 refused: ENGAGED_COST_ARM, ENGAGED_CLAMP_ARM, IDENTITY_GUARD, UNPRICED_DESCENT and UNPRICED_DESCENT_COST_ARM. Comparing the specs entry by entry: IDENTITY_GUARD is dropped, nothing is added, 49 entries are byte-identical, and each of the 4 changed entries equals its base entry with `cycling_cost` replaced by `start_price` in both `old` and `new`.
- RESULT IDENTITY_GUARD drop: its `old` line occurs once in `optimizer.py` at 29fbdf5d4a (first parent before #3697) and 0 times at the #3697 merge 332da69b74. So it has no target, and dropping it is right (ev/checks.txt).
- RESULT carry 6 figure: `dev/audit/harnesses/r11_honest_starts_runs.py descents` at the head (ev/descents_head.txt). `custom_components/` is byte-identical between 7c2f4c30ca and the head, so the head stands in for the body's measurement base. 1 of 12 cells is above min(operand, unpriced): modulating clamped, phase 30, -4 degC, with both 38.1123, operand 38.0075 and unpriced 38.1123, exactly the body's row. The null rows print `one plan across the arms True` for all three installs, and `null cells that moved or descended twice 0`. I did not re-run the two gate-variant rows; they modify production in a scratch tree, and no code here depends on them.
- RESULT step 4/5: the diff touches no file under `tests/golden/`, and not `VERSION`, `manifest.json` or `RELEASE_NOTES.md` (0 diff lines, ev/checks.txt).
- RESULT step 6: the class is one seam, the spec's stale anchors. The enumeration rule run over the whole spec returns 0 at the head, so no anchor is left open.
- RESULT step 7: the body names head 6a21c2886a246f440be4870e093616ceea80265a, the head measured here.
- RESULT step 10: the carry 6 forward-carry is in the tree. `handoff/audit-r10-roster` at 003fab8564 (`wave-r11-groups.json`) holds item 00652efb under R11-INTAKE-R10-RESIDUE.
- RESULT step 14: the only figures the diff moves are the spec's anchors. Removing the mechanism (restoring the `cycling_cost` anchors) brings back the 5 refusals above, so the movement is earned.
- Not re-derived: carries 2/4 null control (`lost_share` -> 0.0 gives 19 of 163 features failing). It concerns code already on main, and this diff does not touch it.

## Findings

- Note: carry-control: the carry 6 text on the roster (item 00652efb) cites "the two gate variants under `## Figures`" of this PR's body instead of stating its control in place. Its stage will not read this PR, so the harness command (`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py descents`), the null-row expectation (`null cells that moved or descended twice 0`) and the "above" rule (both > min(operand, unpriced)) should be restated in the carry when its stage is cut. Carry: R11-INTAKE-R10-RESIDUE
