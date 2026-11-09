Fix review: merge 56a214c8bd8f72dfc4839234dc749cc53ec6813c

bus-nonce: c01f0835580a5643805332b4064f54c4

Round: re-review of the main-merge recarry (prior verdict at 00d12cad0f: blocked ci-red only, CodeQL python cancelled at the old cap; patch verified there).

## Evidence

- RESULT ci: `merge_train.py classify 56a214c8bd8f72dfc4839234dc749cc53ec6813c --pr 3349` -> `GREEN 56a214c8bd8f72dfc4839234dc749cc53ec6813c pending: none red: none`, exit 0 (ev/classify.txt). codeql / Analyze (python) success at this head.
- RESULT carry: `review_carry.py 00d12cad0f 56a214c8bd8f72dfc4839234dc749cc53ec6813c` -> CARRY; the one branch-only commit is the merge of origin/main f365ce757d (ev/review_carry.txt).
- RESULT patch-identity: the PR's diff against its merge base at 00d12cad0f (base fdc8d21ada) and at this head (base f365ce757d) differ only in two `index` lines (blob hashes of optimizer.py and tests/features.py, whose base blobs moved on main); every hunk is byte-identical (ev/patch-diff.txt).
- RESULT main-delta: main's own optimizer.py change in the merged range touches only HeatPumpOptimizer methods near lines 4817 and 5520-5595, none of the threadpoolctl pin or `_scoped_minimize` (ev/main-optimizer-delta.diff).
- RESULT merge: `git merge-tree --write-tree origin/main 56a214c8bd8f72dfc4839234dc749cc53ec6813c` exit 0 against origin/main f365ce757d (ev/merge-tree.txt).
- RESULT features at head: `PYTHONPATH=tests/hastub python3 tests/features.py` -> ALL 4987 FEATURE CHECKS PASSED, rc=0; both `_blas_pin_shared_controller` checks ok (ev/features-head-tail.txt).
- RESULT mutation: GUARD_OFF on `if _blas_threads is None:` at this head -> 1 of 4987 FAILED, rc=1, the optional-dependency arm (AttributeError on None.limit) (ev/mutation-guard-off.txt). The ledger entry records failed=2 for the same mutant; this run counted 1. The kill stands; the count of 2 is not re-derived here.
- RESULT versions: VERSION, manifest.json, RELEASE_NOTES.md and both claim files are untouched by the PR (ev/untouched.txt empty).
- RESULT body head: the PR body names 56a214c8bd8f72dfc4839234dc749cc53ec6813c under `## Head`.
- Not re-run at this head: the stress-probe figures and the replay draw (unchanged patch; measured by the prior review at 00d12cad0f, verdict/3349 61a90cfce8).
