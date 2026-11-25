# #3805 merge-main repair: result (topic merge-3805)

- New head: `6f48176bb62c0728f8a9c62120e5e0f5e6cc2b43` on `refs/heads/handoff/r11-outside-honest-dhw-runs` (force-with-lease from `387c44fa1937e1a93767054af43df37039d4e248`).
- Base: origin/main `6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699` (measured 2026-11-25T11:20:51Z, Linux, python 3.14.7, numpy 2.5.5, scipy 1.18.1).
- Reviewer delta: `7ad21f377478009eebfa80e64baba65cd9bf0c69..6f48176bb62c0728f8a9c62120e5e0f5e6cc2b43`.
- Commits added on top of f4f3cd17 (NOTES commit cc22626f dropped):
  - `2defd1e2d8` Merge origin/main 6a58ba5cb3 (148 commits past f52e700df1).
  - `6f48176bb6` deployment_shape: the #1218 selection-cost note reads 184 of the 561 pairs.

## Resolution per file (merge 2defd1e2d8)

`git merge origin/main` reported no conflict. The claim driver was installed (`MERGE-CLAIM: already-installed`).
- `tests/structure_budgets.json`: the LEDGER-MERGE driver set module_excess_loc to 21727 and class_excess_loc to 17297, which is a lowering. `python3 tests/structure.py` re-measured them: `STRUCTURE RATCHET PASSED`. No budget was raised.
- `tests/closures.json`: the LEDGER-MERGE driver merged it as a set union (closures.tests/entities.py, inert_reads.tests/harness_headers.py). No script's closure needed `--single` re-recording: the gate's `closure.py` lanes passed.
- `docs/architecture.md`, `custom_components/heatpump_optimizer/optimizer.py`, `tests/entities.py`, `tests/features.py`, `tools/ci/selftest_closures.json`: auto-merged. Main added no production module since f52e700df1 (`git diff --name-status f52e700df1 origin/main -- custom_components` shows no A, D or R).
  The counts in `docs/architecture.md` (103 modules), `claims.py` (103) and `deployment_shape.py` ("all 122") still hold.
- `dev/audit/rounds/round4/D6/claims.*`: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` printed claims_true=123 and claims_false=0, with no diff to the committed files.
- `tests/mutation_ledger`: both sides' pins are kept.
  - Of main's pins, 33 are missing at the head. All 33 are this branch's own renames and deletes: `comm` against `git diff -M --diff-filter=DR $(merge-base main 387c44fa) 387c44fa` leaves 0.
  - Of the branch's pins, 7 are missing at the head. They are the duty_legs.py and duty_switch.py pins that main itself deleted in fab96b2fd9.

## Inherited red fixed (6f48176bb6)

The gate's `tests/entities.py` failed one check: `and the lane's docstring records those measured numbers as the selection-cost note (#1218)`, missing marker `184 of the 561`.
Standalone pair census over `tests/closures.json` (the same predicate as entities.py `_d308_pairs`, at Jaccard >= 0.80):

| tree | production files | pairs >= 0.80 |
|---|---|---|
| 2defd1e2d8 | 122 | 184 |
| f4f3cd17 | 122 | 184 |
| 387c44fa | 121 | 182 |
| main 6a58ba5cb3 | 121 | 182 |

The red therefore comes from the first merge at f4f3cd17. That merge combined main's solve_gate.py with this branch's dhw_charges.py, and together they lift tests/golden.py/manual_plan.py and tests/env_drift.py/manual_plan.py to 0.80. The first merge updated "all 122" but not the pair count.
The fix changes the docstring to 184, with a history clause. After it, `PYTHONPATH=tests/hastub python3 tests/entities.py` at 6f48176bb6 printed `ALL 2762 ENTITY CHECKS PASSED` (rc 0). Null control: the marker check on f4f3cd17's deployment_shape.py reads False.

## Combi null control

Check: `combi: the exchange leaves its rounds when a round's plan repeats the one before: the unengaged solve stops short of the cap`.
- It is **absent at origin/main 6a58ba5cb3**. The check is this branch's own, so main has no inherited verdict to give.
- Block run with `tools/audit/seat/features_block.py --emit-prelude P "# A tank that starts over its ceiling coasts: the ceiling binds a charging" "# The kernel hands an action whether the cells it leaves"`, then `--prelude "exec(open(P).read())"` on the same markers (PYTHONPATH=tests/hastub, Linux). The result was `ok` (rc 0, `ALL 2 FEATURES BLOCK PASSED`) at 387c44fa, at f4f3cd17 and at 2defd1e2d8.
- In the full run, `python3 tests/features.py` inside the gate at 2defd1e2d8 printed `ALL 6188 FEATURE CHECKS PASSED`.
- Verdict: the red does not reproduce on Linux at the pre-merge head, at the first merge or at the new head. The local red `[4 of 4; engaged 3]` was seen only in the predecessor's Darwin run on a loaded host at f4f3cd17, where this run shows it passing. It is not caused by the merge, and nothing was changed for it.
  A host-dependent round count (Darwin BLAS) stays possible, and that run was not reproduced here.

## Gate (at 2defd1e2d8, before 6f48176bb6)

Command: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699 ./tests/run.sh`, under gate lease `merge-3805`.
```
  MODE: FULL -- every test script runs, nothing is scoped out.
  reason: tools/ci/selftest_closures.json changes the gate itself, so every closure is suspect
>>> FAILED: python3 tests/entities.py
1 TEST SCRIPT(S) FAILED     (2894s TOTAL, 3 lanes)
```
- The FULL mode is pre-existing: the branch's own diff touches `tools/ci/selftest_closures.json`.
- The one failure is the #1218 note fixed in 6f48176bb6. entities.py, re-run alone at 6f48176bb6, passes 2762 of 2762. 6f48176bb6 changes only the docstring of tests/deployment_shape.py, and `python3 tests/deployment_shape.py` passes.
- Also at 6f48176bb6: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `node tools/policy/brief_lint.mjs` exited 0.
- GOLDEN_MODE=drift: `env_drift.py --all` and `--claims-only` against 6a58ba5cb3 both ok.

## Owed by the orchestrator

- update_pr: the body's Head (now 6f48176bb6) and its main-tip stamp (6a58ba5cb3, 2026-11-25T11:20:51Z).
- Read the combi verdict above in place of NOTES-3805's red.
