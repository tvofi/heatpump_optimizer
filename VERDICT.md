Fix review: merge bcf46f6fb0544871f559837d38d10c2b4dfc194c

bus-nonce: 94a1e34e85e69f47d2649522e00bc630

## Findings

none

## Evidence

- Scope: delta review over the reviewed head cbd6e64df9e8ae00214ea162a5f587a2ba074339 (verdict merge, no findings, so no prior finding is left to resolve). The only new commit is bcf46f6fb0, a merge of origin/main e84856520d. review_carry.py printed FRESH-REVIEW. I compared the three-dot patch at the old head (base 190ffb10) with the one at the new head (base e84856520d) (`ev/delta.txt`).
- What changed in the branch's own diff:
  - `dev/audit/config/scopes.json` left the diff. The branch's cherry-pick of 7df39f349a is now on main via #3924, and the file at the head is identical to origin/main.
  - `tests/structure_budgets.json` is re-based on main's value: `module_excess_loc` 21627 -> 21619 (the same -8 as before) and `unloaded_package_imports` 5 -> 4. Nothing rises. structure.py at the head prints `ok module_excess_loc 21619 <= 21619`.
- Production code (`custom_components/`) and the tests carry the same branch diff as at the reviewed head, so nothing widens the review (step 12).
- Merge: `git merge-tree --write-tree origin/main bcf46f6fb0` (main 9ffb388f7e) exits 0, and LEDGER-MERGE resolved tests/closures.json.
- Live checks at the head: every required check is green. The only red is `tests / nightly-status`, which is not an owed red.
- VERSION, the manifest and the notes heading are untouched (they are absent from the patch).
