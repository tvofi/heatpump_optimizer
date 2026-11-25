Fix review: blocked 8681cc72f623c825054b81b7ffb2dca70fc4c189 tests-red: entities.py and doc_claims.py fail at the head on two counts the main-merge resolution left stale (architecture.md:306 HA-free 65 vs 66; deployment_shape.py #1218 pair note 182 vs 184 of 561)

bus-nonce: 6383f7eabb91bf5dc6f166e2b9555d9c

Round 2 (delta re-review over the reviewed head 3f8fb54ffcf92146097881fe4762866340446fe8). Scope: the repair `git diff 3f8fb54ffc 875dfbc86f`, the main-merge resolution `git diff d3d66c4040 f2f9e3f5d5 -- dev/audit/rounds/round4/D6 tests/deployment_shape.py docs/architecture.md`, and the three prior findings (M1, M8, M9).

## Block

The code repair is sound and every prior finding is resolved (see `## Evidence`). The head is blocked only on two tree-derived counts that the merge of main into this branch (`f2f9e3f5d5`) left stale. Two in-tree checks fail on them at this head and pass at origin/main `d3d66c4040`:

- `docs/architecture.md:306` reads "The other 65 modules are deliberately free of it". The resolution moved the module count from 102 to 103 (lines 8 and 297) and did not move this line. Main already reads 65 at 102 modules, and `dhw_start.py` imports no `homeassistant`, so the head's tree measures 66.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `FAIL architecture.md's HA-free count is the tree's [architecture.md says 65; 103 modules less 37 that touch homeassistant anywhere leaves 66]`.
  - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `FAIL ... [architecture.md:306 modules_free_of_homeassistant: documented=65 measured=66]`, `1 of 443 checks FAILED`, rc=1.
  - The PR body's own figure ("65 free of `homeassistant`") is the pre-merge one.
- `tests/deployment_shape.py:60`, the #1218 selection-cost note, still reads "182 of the 561 script pairs". The head's tree derives 184: `entities.py` at the head prints `FAIL and the lane's docstring records those measured numbers as the selection-cost note (#1218) [... 122 production files; 184 of 561 pairs at >= 0.80; 435 pairs comparable; ... missing markers -> ['184 of the 561']]`.
  - The resolution moved this note's file count (121 to 122) but not its pair count. Adding `dhw_start.py` to the planner's 27 closures moves pair overlaps.
  - Derived on the PR head as briefed: the head itself is wrong, so this is a head defect, not a merge-time carry. origin/main is still `d3d66c4040`, so there is no further drift against main.

`entities.py` at the head: `2 of 2763 ENTITY CHECKS FAILED`, rc=1. Control at `d3d66c4040`: `ALL 2763 ENTITY CHECKS PASSED` and `doc_claims.py` `ALL 443 checks PASSED`. The 52 nested `a3:`/`a4:` FAIL lines appear identically in both runs; they are the script's own controls, not failures.

Owed: `docs/architecture.md:306` 65 to 66, and `tests/deployment_shape.py`'s #1218 note 182 to 184, both re-derived by running the two scripts. Then refresh the body's pre-merge figures (Note below). No production line changes.

## Findings

- Note: stale-body: the PR body's summary still describes pre-repair and pre-merge states:
  - "tests/features.py: the `_repair_dhw_floor` stand-in `_lg_whole_tail_repair` takes `charge_running`". `875dfbc86f` removed that keyword.
  - "(102 modules, 65 free of `homeassistant`; the #1218 note's 121 package files)" and "The other 64 modules ... reads 65" both describe the tree before `f2f9e3f5d5`.
  - The `## Head` section is current. Refresh with the block's fix. Carry: #3863

## Evidence

- Head reviewed: `8681cc72f623c825054b81b7ffb2dca70fc4c189` (`ev/HEAD.txt`), equal to the PR head read live. The base and merge base are both `d3d66c40408e76351ffc528686353cadf815a05c`, which equals origin/main. Role files are unchanged between merge base and origin/main.
- `git merge-tree --write-tree origin/main 8681cc72f6`: rc=0, no conflict (`ev/merge-tree.txt`).
- CI: `merge_train.py classify 8681cc72f623c825054b81b7ffb2dca70fc4c189 --pr 3863` printed `WAIT ... pending: gate red: none` on every poll from 12:58Z to 13:32Z (`ev/classify.log`). The `gate` lane had not finished when this verdict was returned. The block rests on the local runs above against a clean main control, not on CI.
- Prior M1 (planner flag read to `True`) is resolved, KILLED: `tests/block_duty.py` rc=1, `1 of 161 BLOCK DUTY CHECKS FAILED` on the new end-to-end check "with no charge under way the planner drops a step-0 hot water run ..." (`ev/mutant_M1.txt`).
- Prior M9 (`place_startable`'s final `drop_unstartable` without `charge_running`) is resolved, KILLED: rc=1, the new unit check "... a repair that keeps re-placing a first-step charge ..." (`ev/mutant_M9.txt`).
- M9 inner (the loop's `drop_unstartable` without `charge_running`): KILLED by the end-to-end check (`ev/mutant_M9inner.txt`).
- NULL (a comment on `STARTABLE_ROUNDS`): SURVIVED, `ALL 161 BLOCK DUTY CHECKS PASSED` (`ev/mutant_NULL.txt`). Head unmutated: `ALL 161 BLOCK DUTY CHECKS PASSED` (`ev/block_duty.txt`), confirming the fixer's 161/161.
- Prior M8 is resolved as an equivalent mutant; the site no longer exists. This is the production delta's one non-obvious risk (`custom_components/heatpump_optimizer/dhw_planner.py` `_repair_dhw_floor` now calls `startable_steps` with the default `charge_running=True` while the plan may be judged under `False`), so I re-derived it in two ways.
  - Reading: `startable_steps`'s `ok[0]` is `temps[0] < start_below[0]`, independent of the flag. The flag only changes `under_way` after a step-0 charge with `ok[0]` false.
  - Every plan the repair receives has passed `drop_unstartable(..., charge_running)`. That removes such a charge when the flag is false, using `temps_of(plan)[0]`. Both `temps_of` and the repair's `_dhw_shortfall` take `_dhw_plan_temps` with the same `initial_temp`, so index 0 is the same number.
  - The repair adds only at `usable` steps, which include `startable_steps`, so it cannot add a step-0 charge with `ok[0]` false.
  - Measurement, with my own harness (`ev/m8_equiv.py`, the reviewer's, not the finder's): it wraps `dhw_planner.startable_steps` to evaluate both flag values on every call. It sweeps 162 solves of `block_duty._solve_winter_mild` with `under_way=False`: hysteresis {2, 4, 7} K x tank {44, 48, 50, 51.5, 52, 54} degC x window {none, 00:15-02:00, 06:00-08:00} x minimum {none, 50, 53}.
  - Result at the head: 3708 calls, 47 with a step-0 charge on, 0 where the two flag readings differ.
  - The same sweep with the PR's former binding restored (`charge_running=running` threaded into the repair) gives byte-identical plans (digest `7a4f3403b7d57749` for both; `ev/m8_sweep.txt`).
  - Perturbation control: the wrapper's comparison does differ on an undropped plan (`[1,0,0]` on a 54 degC tank with start below 51: `True` gives `[F,T,F]`, `False` gives `[F,F,F]`), so the zero result is not vacuous.
  - `block_duty.py` with the binding restored: `ALL 161 BLOCK DUTY CHECKS PASSED`.
- Counts re-derived on the head's tree (`git ls-tree`):
  - 122 files under `custom_components/heatpump_optimizer/` and 103 top-level `.py` modules (main: 121 and 102). The `docs/architecture.md` 103 and the `deployment_shape.py` 122 are correct.
  - `dev/audit/rounds/round4/D6/claims.py` at the head: `RESULT claims_false=0`, `arch_modules_on_disk=103`, `arch_map_listed=103`, `arch_map_missing=0`, rc=0, matching the resolved `claims.{json,md,py}`.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files are untouched three-dot against the merge base. `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- `tests/deployment_shape.py` itself was not run at this head. The #1218 note's text is checked by `entities.py`, quoted above.
- Not re-derived: the body's patch-id equality, the finder's-harness counts (42/43 KILLED) and the features-block mutants (M1/M2 at `859dda1c38`). They are outside this delta.
