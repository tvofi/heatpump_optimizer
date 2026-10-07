Fix review: blocked eb0a8bf97bdbcea0b2b289077b2cc9e9a22e5553 harness: class-rule-missing #1955 states (a)-(d) and the body names no enumeration command

bus-nonce: ed8ed3cc856ca5eb3fcda5475449605e

Round 3. Measured `eb0a8bf97bdbcea0b2b289077b2cc9e9a22e5553`. Live pull-request head at posting is that SHA. The body ## Head names it. Merge-base and `origin/main` are `1fa713f73740e99a5762019f574ccd6afa45dca2`. `git diff` of `tools/audit/briefs/` from the merge-base to `origin/main` is empty. `git merge-tree --write-tree origin/main eb0a8bf97bdbcea0b2b289077b2cc9e9a22e5553` exited 0 with empty stderr. Three-dot diff of `VERSION`, the manifest and `RELEASE_NOTES.md` is empty.

## The previous block

`tests/mutation_table.py` inventory at this head: `completeness_problems` length 0, `added_unpinned` length 0, unpinned 4694 of 5637 against 4695 at `1fa713f7`. `changed_lines` against `origin/main` draws 6 sites:

- `coordinator.py:6525` RETURN_DEL `return _tail_freeze(self)`
- `pump_arbiter.py:480` two CLAMP_DROP sites on `min(max(curve, FLOW_HOLD_C), ceiling)`, one anchor `fa7f3970`
- `thermal_model.py:1213` GUARD_OFF `if floor is not None:`
- `thermal_model.py:1214` CMP_BOUND `below_floor = total < floor`
- `thermal_model.py:1215` GUARD_OFF `if below_floor:`

The mutation job on this head was still pending, so the lane had not driven them. Applying each site's own replacement:

- outer clamp, `hold = ... (max(curve, FLOW_HOLD_C))`: `_flow_target` with `flow_heat_c` 48 and a curve of 60 returns 60.0
- inner clamp, `min((curve), ceiling)`: a curve of 20 returns 25.0, not the pin's 20.0; `_bounded` lifts it to the gate. 25.0 is not `FLOW_HOLD_C` 35.0
- either floor guard replaced with `if False:`: `planned_draw_runs(0.3, modulation_floor=3.0)` is `True`
- bound `<=`: `planned_draw_runs(3.0, modulation_floor=3.0)` is `False`
- `return _tail_freeze(self)` replaced with `pass`: `_learning_frozen` on switch plus setpoint is `None`

At the unmodified head those reads are 48.0, 35.0, `False`, `True`, and `unmetered_power`. `planned_draw_runs(0.3)` with no floor is `True`. The changed-line draw is not an empty pool.

`_flow_target` with `flow_heat_c` 48 and a curve of 60, duty `None`, returns 48.0, not 55.0.

`tools/policy/policy_lint_envmatrix.mjs` at this head and at `origin/main` is blob `d1f64ecac027143488b756af9fcec4ed52fa0e68`, not `40bac880`. `governance.yml` is unchanged against `origin/main`. The env-matrix job on this head succeeded. The body says the job checks the script out from the base and that this update does not edit the file that job replaces. It does not claim the job runs a head script.

## What still blocks

#1955 states (a), (b), (c) and (d). ## Figures is `none`. The body names no command that enumerates the seams. `pr-contract` on this head is success. `delivery-status` and `nightly-status` are still failure and grade main. `fast (3.14)` and `mutation` were still pending at this posting.
