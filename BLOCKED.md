Question: raise needs the owner -- tests/structure_budgets.json max_class_loc 7762 -> 7763 and module_excess_loc 21646 -> 21663 stay, and `score.py --diff origin/main` reads dS -0.0006 WORSENS; no payment measured removes it. Approve the raise at the head, or rule which payment to take?

Seat fixer-r11-repair-3882b, repair of #3882 from head 2dcff40eec34. Measured at b98049141bd6 (this ref's parent) against origin/main b4ebe3dcf3c9, merge base 190ffb10c230, 2026-11-27T06:40Z.

## Red 1: governance / instrument-self-tests (repaired, on this ref)

Steps 23 (owner-only canary) and 55 (self-tests outside tools/audit/seat/) failed for one cause: `check_scopes.py` refused the live D5 scopes, `over ledger.max_units 4500: s7 holds 4523 units`. s7 is `tests/f*`. `tests/features.py` alone holds 4339 D5 units at the head (4303 at main), so with `tests/finite_boundary.py` (160) and `tests/frontend.py` (24) the seat went over the cap. The canary harness's `SCOPES null` arm runs that live check. It did not fail because an owner-only path leaked: no owner-only finding.

- b98049141b narrows s7 to `tests/features.py`, as the cap's own `_rule` says to re-cut a seat that grows past it. The two siblings fall to s9 (`rest`): s7 1f/4339u, s9 71f/4100u. No self-test is changed.
- Before (2dcff40e): `python3 -I tools/audit/check_scopes.py --self-test --repo .` rc=1, and `python3 -I dev/audit/harnesses/owner_only_channel.py` `RESULT arms=48 failed=1`. Main as the control: the check_scopes self-test is rc=0 at b4ebe3dc.
- After (b98049141b): the check_scopes self-test is rc=0, and `owner_only_channel.py` prints `RESULT arms=48 failed=0` and `OWNER-ONLY CHANNEL HELD`. Every other command of step 55 was rc=0 at 2dcff40e.

## Red 2: budget-raise-gate (blocked)

The gate prints `REFUSED: no decisive review by tvofi (id 70032254)` over RAISE max_class_loc 7762 -> 7763 and module_excess_loc 21646 -> 21663. At b98049141b, `python3 tests/structure.py` passes against the raised table. The score is `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2533->2534)`.

The charged-statement diff, computed over both trees with footprint.coord_footprint's own path: the only function whose charge changes is `frost_hold.freeze_reason` (0 -> 1). Any module function taking the coordinator is charged its logic statements. The body's earlier claim that a bound method scored NULL was measured against an older main.

Payments tried this pass, both reverted:
1. Pass `coord.arbiter_inputs` bound, and give `tests/features.py`'s `_SysIdHost` the builder as `Coord.arbiter_inputs`, beside the `_learning_frozen` and `_commanded_split` it already copies. Score unchanged: dS -0.0006 WORSENS, coord_footprint 2534. It also breaks the `_FhBare` check. It pays nothing.
2. `freeze_reason(held, inputs, now)` (the former `_freeze`), with `_tail_freeze` passing `pump_arbiter.state_for(coord), coord.arbiter_inputs`. `tests/structure.py` FAILs: seam_cut_total 426 > 413 (+13), class_excess_loc +1, module_excess_loc +1 and unloaded_package_imports 4 > 3. It is worse.

The earlier payments in the body's `## Raise justification` (items 1-7) stand as measured there. The body cites mandate 6893738184, but the agent-approval arm exists only once no payment that the score does not read as worse exists. The head reads WORSENS, so this seat does not hand the raise to a mandated approval.

## Previous review note: REKEY KEPT at duty_ledger.py:49 (not resolved, body-only)

`python3 -I tools/pr/ci_predict.py --rekey-body <PR body> --from 2dcff40e` prints `REKEY KEPT duty_ledger.py:49 GUARD_OFF` and three `frost_hold.py` rows, `REKEY: 0 re-keyed, 4 kept`. The guard `if row.get("frost"):` is at `duty_ledger.py:47`. `## Unpinned sites` already lists `:47 GUARD_OFF`, and it is pinned in `tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.cd6a62d4.json`. So the `:49` row is a stale duplicate, to be deleted from the body at the handoff. No code change is owed.

The nightly-ha and nightly-status reds are not required (brief), and none is answered here.
