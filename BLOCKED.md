Question: two fixer seats hold R11-OUTSIDE-HONEST-DHW-RUNS (#3709) at once. This one (local branch fix/r11-outside-honest-dhw-runs-r2) found handoff-wip moved at 03:35Z by a seat on fix/r11-outside-honest-dhw-runs-r3 (c793aca417, origin/main merged onto this seat's step 21e945ca7e). Which seat hands off? This seat has stopped and pushed nothing to handoff/ or handoff-body/.

What this seat leaves on this ref (ddc4090264), all on top of c793aca417:
- 454585e039: `_charge_runs` reads `opt.config.start_price`, not the raw `cycling_cost` (main's check "every optimizer reader of the start price reads start_price" failed at the merge of 76bbf63744; the group's ChargeRuns check now expects CLAMPED_DEFAULT_START_PRICE on a clamped install configured at zero). env_drift --all 76bbf63744: NO UNCLAIMED DRIFT, 56 scenarios.
- 9de00356af: the stale `_charge_runs` RETURN_DEL c61a98f1 pin deleted (ci_predict STALE PIN).
- 21e945ca7e: owed red tests / fast (3.14), the duty-switch check. Reproduced locally only with numpy's dispatch narrowed to SSE (NPY_DISABLE_CPU_FEATURES of AVX-512, AVX2, FMA3, F16C, AVX; OPENBLAS_CORETYPE=Nehalem): at 2 degC the operand's descent alone is 0.0065 above the shipped plan, under the check's 0.01; the merge base keeps 0.061 in that class. Mild day moved to 1 degC: gap 0.18 in native, Haswell, Sandybridge and Nehalem classes; the block passes (103 checks) in all four.
- 0d734c48e6 (merged as 3e0b02547a): `tests/mutation_table.py --pin-killed --scripts tests/features.py --jobs 4 --shard 1/4`: 11 pinned, 6 survived (dhw_planner.py:590 CMP_BOUND, :615 CMP_BOUND x3, :684 CLAMP_DROP; optimizer.py:2106 CMP_BOUND). Shards 2-4 of 4 not run (shard 2 stopped on finding the second seat).

Not done by this seat: shards 2-4, survivor triage, prepr, body.
