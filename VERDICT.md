Fix review: merge dba968f8d579890b70db289f0b5bd0400d0b921b

bus-nonce: 8123b36a9460a8901b1b2257311d7a69

Round 2, delta re-check after round 1b (merge 5bb7710c1c347a7969b2319d97575eb4f15f8151, verdict/3147). Measured at dba968f8d579890b70db289f0b5bd0400d0b921b; base origin/main 0166aefd7047b98e275bc0ab4e604fac3a7c75c6.

## Head

dba968f8d579890b70db289f0b5bd0400d0b921b, the head the body names. `git merge-tree --write-tree origin/main dba968f8d579890b70db289f0b5bd0400d0b921b` exits 0, no conflict (ev/merge-tree.txt).

## Why review_carry prints FRESH-REVIEW

The branch's own diff (merge-base..head) is the same 11 files with the same added and removed lines at 5bb7710c1 and at dba968f8d. A diff of the two diffs (ev/diff-of-diffs.txt) differs in three lines only: the `index` blob hashes and the hunk offset of snapshots.py (`@@ -194` becomes `@@ -200`) and one context line there. Main's #3050 changed snapshots.py near the annotation (`if not snap.get("healthy") or "before_reset" in snap:`), shifting six lines. Requirements pins, typing_budgets.json (ruler.mypy 2.3.1 to 2.4.1), the seat scripts, carry-201.json and the delivery row are identical. The merge resolution touched nothing of the PR's.

## Re-run checks

- Ruler raise: one line, `ruler.mypy` 2.3.1 to 2.4.1; the body's Raise justification lists the payment tried and `Architecture score: dS +0.0000 NULL`. `budget-raise-gate / budget-raise-gate` is success at this head (the owner's approval is in).
- structure.py: STRUCTURE RATCHET PASSED (ev/structure.txt).
- Typing venv built from the head's lock (mypy 2.4.1): `tests/typing_ruler.py --mypy` reads ALL 9 typing-ruler checks PASSED. Mutant: deleting `snap: dict[str, Any]` in snapshots.py, merged with #3050's change, reads snapshots.py 1 error, FAIL errors did not grow [recorded 0, measured 1] and by_code[no-any-return] (ev/mut-snap.txt); restored clean.
- Pin set: the four requirements files are byte-identical in the branch diff across the merge; main moved none of them.
- Claim files, tests/golden, VERSION, manifest, RELEASE_NOTES: empty three-dot diff (ev/claims-3dot.txt).
- Delivery row: three-dot diff adds only dev/programme/delivery/3147.md, one line.
- No governance role file changed on main since the merge base.

## Red checks

None at the head. All workflow runs concluded success or skipped; merge_train classify exits 0, GREEN (ev/classify-final.txt). `pr-contract / pr-contract` success; `tests / typing`, `tests / fast (3.14)`, coverage, closures, arch-instrument, mutation success.

## Findings

None new. The round 1b reindent note on carry-201.json is unchanged and already dismissed there.

## Evidence

- tests/entities.py and tests/features.py cannot import homeassistant in this seat's venv-ci; they were not re-run, and CI's `tests / fast (3.14)` (success) is cited instead. Round 1b ran them at the prior head; the code delta is offsets only.
- Heavy runs (gate, mutation) cited from CI, not re-run.
