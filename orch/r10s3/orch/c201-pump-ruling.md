Ruling on R10-PUMP-MODEL D2-s2-01 (#2238; question in comment 6228455340), under mandate 6175172275, the recommended option of an independent judge seat: **accept the fix**. The two-law hot-water pricing is the defect; the documented sentence in `docs/how-it-works.md` describes what #1530 left behind, not a recorded design decision.

Judge's executed evidence (Apple M1 / Accelerate, origin/main `6e5753a4a`; harnesses under the judge's scratch, to land with the fix):
- Over a 41 outdoor x 51 tank grid, 1861 of 2091 cells differ between the two laws at main (worst ratio 1.4346 at 7 °C / 65 °C); 0 at the fix head. Perturbation (flip the flag at one cell) moves 1.8542 <-> 2.6600; null control (35 °C tank, where both laws must agree) max |diff| 0.
- Within ONE install (direct plant, no valve) the space side pays the Carnot lift and the tank the linear penalty at the same water temperature: ratio 1.3522 at 7 °C / 55 °C. This refutes the D2 verifier's "no single install prices one tank two ways".
- `tests/optimality.py` ftol arm: at the fix head production equals the ftol 1e-8 fixed point (gap -0.000%) and every loosening lands at +0.64%; at main production sat 2.76% short of its own tight point. The plan became better conditioned; the guard's 2.5% bound no longer separates. Its derivation harness `dev/audit/harnesses/k1725_blas_kernel_gap.py` raises TypeError at main.

Steps, returned to the R10-PUMP-MODEL fixer on `handoff/r10-pump-model-d2`:
1. `docs/how-it-works.md`: one law on every plant, a tank below the 35 °C reference earns no boost.
2. Repair `k1725_blas_kernel_gap.py`; re-derive the ftol bound (or re-select the cell/arm) from a fresh kernel matrix (Accelerate + CI runner kernels), half the smallest gap, still red when production ftol is loosened; the comment cites this ruling.
3. `tests/stress.py`: route `coverage_floor_override` into the production-call floor (today it reaches only the solver-work floor); add the override in `tests/stress_budgets.json` at CI's measured counts, citing this ruling, with `## Raise justification` (no payment exists: the re-plan is the fix); dropped at the next re-record, as #1207's was.
4. The body states each re-planned stress scenario's solver work against baseline from CI's stress log; any growth past the 3.0x work factor voids the acceptance.
5. A fresh fix reviewer with the finder's harness.

Leaves #2238 and #201 open.
