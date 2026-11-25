# #3805 local merge: state handed to the cloud seat

Head `f4f3cd1719a8ff5bf589c69a9767f11dcb1bf244` merges origin/main `f52e700df1` into handoff `387c44fa1937e1a93767054af43df37039d4e248`. It is not pushed to the handoff, and no PR was updated.

## Conflicts resolved

- `dev/audit/rounds/round4/D6/claims.py`: arch_modules_on_disk and arch_map_listed are now 103. The history line reads "102 until R11-OUTSIDE-HONEST-DHW-RUNS's dhw_charges.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; ...".
- `tests/deployment_shape.py`: "all 122". The history reads "(121 until ...dhw_charges.py, 120 until ...solve_gate.py, ...".
- `docs/architecture.md`: 103 modules, 36 of the 103, and the other 66 HA-free.
- `claims.json` and `claims.md` regenerated, claims_false=0.

## Checks at f4f3cd17 (local, Darwin, loaded host)

Green: structure (module_excess_loc 21728 <= 21728), doc_claims 441, deployment_shape, cycle_lane 25, block_duty 155, golden (no unclaimed drift, 56 scenarios), and ci_predict (no red predicted against f52e700df1d2).

Red: `tests/features.py` reports `1 of 6178 FEATURE CHECKS FAILED`:

    FAIL combi: the exchange leaves its rounds when a round's plan repeats the one before: the unengaged solve stops short of the cap  [4 of 4; engaged 3]

The check is near tests/features.py:99080. It compares `_hdr_x_free.rounds` against `_hdr_om._COMBI_EXCHANGE_ROUNDS`.

## Null control at 387c44fa (pre-merge head)

Not concluded. The run was stopped on the coordinator's order after 232 of 248 sections. It had not yet reached the combi section, so it has no verdict on whether the red comes from the merge or from the host. The log had no FAIL line up to that point.

A CI fast log on another head (scratchpad fast.log, 2026-11-25T04:32Z) printed this same check `ok`. That favours the merge (or main f52e700df1) as the cause over host load, but it is not a controlled comparison.

## Owed next

1. Run the combi section alone at 387c44fa and at f4f3cd17. `tools/audit/seat/features_block.py --emit-prelude` gives its prelude.
2. If the merge is the cause, check what main changed under `_COMBI_EXCHANGE_ROUNDS` or the exchange loop since 387c44fa's base.
3. Update the body's Head and Red checks for the merge. Then push the handoff and run body_push.
