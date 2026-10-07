Fix review: merge 0f67647bb95713447db7bc400cdc01e1c064eef6

Resolution delta only (fix-review.md step 12); prior verdict `merge 21a62c10a03f5bd684d529aa70d8ff7ef6938471` stands for everything else.

- Head 0f67647b = aadd1de4 + be0cb821 (main). `git merge-tree --write-tree aadd1de4 be0cb821` tree vs head tree: 0 paths differ, so the head step is an automatic merge.
- aadd1de4 = 21a62c10 + 421c77f9. `git merge-tree --write-tree 21a62c10 421c77f9` conflicts only in tests/features.py (append/append); the auto-merge tree and aadd1de4's tree differ in that one path and no other.
- tests/features.py union, measured against merge-base bcea7488: all 219 main-added lines and all 148 branch-added lines present in aadd1de4; zero conflict markers; parses with ast. Check/def count 3638 = 3617 (branch) + 3629 (main) - 3608 (base), exactly the union. Total lines 59027 vs 59026 expected, the one extra being a separator blank line (only lines whose count exceeds both parents: blank, `)`, `}`, `R.check(`, all structural).
- Six lines of main's 421c77f9 that aadd1de4 lacks (the "space-heating step writes the heating flow, not the 25 degC floor" check) are in the merge base and absent from the branch: the branch's own deletion, carried from the 21a62c10 side, not a resolution loss.
- No production file differs from original-verdict content plus main: aadd1de4 changes only tests/features.py relative to the automatic merge, head is an automatic merge on top.
- CI at head (check-runs, evidence/check-runs.txt): pr-contract, hassfest, validate-hacs, policy-docs, briefs, closure-scope, budget-raise-gate (success run), instrument-self-tests, wave-script green. NOT DONE when read: fast (3.14), mutation, coverage, typing, closures, browser, env-matrix, CodeQL analyses (in_progress). delivery-status / nightly-status failures are non-gating status jobs, one budget-raise-gate run cancelled (superseded by the success run). I did not re-run heavy gates.
- Fixer's local `R9-F2.1 P3 ... shipped 110.4366, seeded 110.1297`: that check and thermal_model changes come from main (efb4c6c4), so it is not introduced by this delta; I could not confirm it from CI because fast (3.14) was still running. This merge verdict is conditional on fast (3.14) landing green; the merge train's CI gate is the authority, and a red there overrides this line.

bus-nonce: 7740721228ce12a577074f5847911b01
