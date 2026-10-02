merge 17da01bbe8f53b5fd991eae1f75ae5afec4185ef

# R9-F9.3 fix review, PR #1785, round 2

The head was measured at 17da01bb and was still the live head when this verdict was posted. It is code head c927ef1e, plus main 754d2319 merged in, plus the delivery row.
Environment: Linux, Python 3.14.7, hash-pinned CI requirements, OPENBLAS_CORETYPE=Haswell, 1 thread.

1. Round-1 block cleared. `git diff origin/main...17da01bb` contains no `handoff/` path, and none of the commits in `origin/main..17da01bb` touches one. The PR body sits in 513eb26d, on the handoff branch only.
2. The two new fixes:
   - Energy totals (`coordinator.py` `_async_load_energy_totals`): the `_kwh` totals keep their live floor. The cost totals now reload exactly as stored, so a negative cost is kept.
   - `score_day`: a book with no `day` key reloads as the streak-only book. A book whose `day` is empty is still refused.
   - Tests at the head: finite_boundary `ALL 68 FINITE BOUNDARY CHECKS PASSED`; features `ALL 3597 FEATURE CHECKS PASSED`, including the changed dhw_cost check, which now keys on the first `_kwh` total.
   - My own mutants: all 4 killed (own_mutants_fb.txt, own_mutants_features.txt). N1 restores the live floor on the cost totals and fails finite_boundary. N2 drops the kWh floor and fails finite_boundary. N3 treats an empty day as the streak-only book; finite_boundary lets it through and features kills it. N4 drops the streak-only book and fails finite_boundary.
   - Caveat, not a defect: the load is a spawned task, so any accrual booked before it completes is overwritten by the stored total. That was already true for positive totals under the old `max`.
3. carry-1747.json: `brief_lint.mjs` reports 0 errors. The shape matches the existing carry files (control, remeasure, brief). The R9-EG-B8 roster brief on handoff/audit-r9-fixplan carries the same text. Once the roster lands on main, brief_lint will refuse carry-1747.json, because issue 1747 will then have a live group. The seat that lands the roster must delete the file in that same PR.
4. Structure message: 21536db2's message says "9010 -> 8999", but its diff is 9034 -> 9023. Lines 114-115 of the body correct this. The ratchet only moves down (9034 -> 9023 -> 9022), and `STRUCTURE RATCHET PASSED`.
5. Typing: CI's `typing` job passed at 17da01bb (job 109948604412). A local `typing_ruler.py --mypy` on 3.14.7 also printed `ALL 9 typing-ruler checks PASSED`.
6. Mutation table: `mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` gave `0 survivor(s) of 10 evaluated`, `MUTATION TABLE PASSED`, rc 0. Unpinned sites went from 3578 to 3574. The null control survived. CI's mutation lane was still running when this was posted, and its result is authoritative.
7. Whole-tree gates at the head: codeowners_gap `uncovered_files=0`; policy_lint 0 errors; `--budgets` rc 0; structure passed. `git merge-tree` against main 754d2319 is clean, and main is already an ancestor of the head.
8. Checks at the head: no red check. `closures`, `fast`, `coverage` and `mutation` were still running at posting.
