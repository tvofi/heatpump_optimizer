Fix review: blocked f36611dd23542a73d141963c1eb7860f8a219edb mutation-vacuous: custom_components/heatpump_optimizer/pump_arbiter.py:936 GUARD_OFF survives all 6045 checks of tests/features.py

bus-nonce: c290fc08c82dfa769eb2e36019454c2f
pending-ci: gate

Round 1 (first review of #3866).

## Block

- `pump_arbiter._boost_ceiling_c` still holds `if (limit := _space_limit_c(inp)) is not None: caps.append(limit)` at the head (lines 936-937). The body says this cap was removed: "A second cap in `_boost_ceiling_c` was an equivalent mutant (M7 below), so it was removed", and "The cap was deleted from `_boost_ceiling_c`, so the mutant site no longer exists". Commit `ea4b6dd401` ("the level map alone caps a boost under the high limit") changes only `tests/features.py`. `git show 0d1cae21a6:custom_components/heatpump_optimizer/pump_arbiter.py` still has the cap at line 937, and the body's own `## Unpinned sites` lists `pump_arbiter.py:936 GUARD_OFF`.
- Mutant: GUARD_OFF (`if False:`) at 936 (`ev/mutant_boost_cap_guard_off.diff`). The full `tests/features.py` passes under it: `ALL 6045 FEATURE CHECKS PASSED` (`ev/features_full_mutant_boost_cap_guard_off.log`). The R11-OWNER-FLOWCAP block passes too (`ev/mutants.txt`, `F-boost-cap-off`).
- Why no check can kill it: `_boost_ceiling_c`'s one caller is `_map_inputs` (pump_arbiter.py:1009; `git grep '_boost_ceiling_c'` at the head). That caller takes `min(boost_c, _space_limit_c(inp) or math.inf)` (line 1011), so the limit inside `_boost_ceiling_c` can never change the result. `mutation-autofix` pins only killed mutants, so `tests / mutation` stays red on this site after the bot commit, despite the body's `## Red checks` answer ("mutation-autofix pins killed sites").
- Remedy: delete lines 936-937 as the body describes. The `_boost_ceiling_c` docstring's "and by the high limit (:func:`_space_limit_c` ...)" goes with them, or is re-worded to say the level map applies the limit. Re-run the FLOWCAP block afterwards. My view is that this is a two-line deletion that leaves the rest of the review standing.

## Findings

- Out of scope: the finder's harness `owner_flowcap_harness.py` (sha1 `970cb958...`) is out of tree and did not reach this seat. Its base and head columns are not re-derived here. Its boost, option, clamp and valve rows are re-driven by the committed FLOWCAP and clamp checks in `tests/features.py`, which I ran at the head (12/12, 7/7) and under mutants. Carry: dismissed: the owner item has no finder harness, and the committed checks pin each row the body quotes.
- Residual: the FLOWCAP block alone does not pin that `_space_limit_c` passes the stepped lowest heating write (`_heating_floor_c(inp)[1]`) rather than the unstepped `clear` (`[0]`). Under that mutant, a 5-degree-step entity with a high-limit sensor reading 28 writes the 25 °C gate (off) on every heating and boost step (`ev/mutants.txt` probe). The block stays green, but the full suite kills it: 2 of 6045 fail, both R10-WATER-SETPOINT-FEEDBACK part 3 I2 (`ev/features_full_mutant_lowest_to_clear.log`). It is pinned by the closure, so this is no block. Carry: dismissed: killed by tests/features.py's R10 I2 checks at this head.
- Note: stale-body: the body describes `_boost_ceiling_c` without the limit cap, which the head does not match (see Block). It also states "these keep the advertised grid: ... `_flow_command`", which the head matches (line 878 bounds `_heat_ceiling_c` without the limit). Carry: dismissed: resolved by the Block's remedy, which makes the code match the body.

## Evidence

- Head reviewed: f36611dd23542a73d141963c1eb7860f8a219edb (`ev/HEAD.txt`), the same head the body names. Merge base 8cc3fb3e35. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main f36611dd23` gives rc=0 with no conflict (`ev/merge_tree.txt`; origin/main e3cb5c019b).
- Mutation proof, my driver `ev/mutants.txt` over the FLOWCAP block (12 checks) and the clamp block (7 checks):
  - Clamp mutants, all killed, matching the body's counts: C-max-off 4/7, C-min-off 2/7, C-max-nearest 1/7, C-min-nearest 1/7, C-ownrange-numberkeys 1/7.
  - Option mutants, killed: F-max 3, F-strict 1, F-opt-floor 1, F-opt-ceil 1, F-indoor 1, F-map-top 4, F-hold 1, F-loop 1, F-option-never 9, F-sensor-raw (crossed-pair bypass) 1, F-dropped-voids 1.
  - Survived on the block: F-boost-cap-off (see Block) and F-floor-lowest-is-clear (killed by the full suite, see Findings).
- Null control, clamp: with `inputs.py` from the merge base, the clamp block fails 4 of 7 and both null-control checks pass (`ev/clamp_block_base_inputs.txt`), as the body states.
- Head runs: FLOWCAP block `ALL 12 FEATURES BLOCK PASSED`; clamp block `ALL 7 FEATURES BLOCK PASSED`. Full features.py under each mutant ran 6045 checks, consistent with the body's 6045.
- Seam enumeration, class "a temperature set-point service call": I re-ran the body's rule (`ev/enum_setpoint_calls.txt`). Every hit is dispositioned in the body: valve `write_setpoint_c` (coordinator.py:728), frequency `set_value` (coordinator.py:10835), heat_curve write and Restorer, repairs.py:51, arbiter `_write` (pump_arbiter.py:1668), night-slot `set_value` (pump_arbiter.py:1647, `_NIGHT_KEYS`), and services.py's flag. No open seam.
- Option consumers (`git grep '"space_setpoint"' pump_arbiter.py`): the heating step (`_map_inputs` heat_c), the hold (line 990), and the feedback highs (line 1115) read the limit. The gate (832), the draw-range ceiling (878) and the adopt baseline (1750) do not, as the body states.
- Step 16: the diff adds no refusal that skips an actuator write. The clamp changes the value sent, never whether it is sent. A dropped limit source falls back to no limit.
- Structure: `tests/structure.py` at the head passes, `module_excess_loc 21766 <= 21766` (`ev/structure_head.txt`). The budget moves down only, with no raise. The payment is moving `_silent_rows`/`_inside_silent` into `quiet_windows.py`, the module that owns `step_actions`, which is a sound home for them. CI `arch-score` is success.
- Claim files and versions: no claim file, `VERSION`, manifest or `RELEASE_NOTES.md` appears in the three-dot diff.
- CI: `merge_train.py classify f36611dd23 --pr 3866` printed `WAIT f36611dd23542a73d141963c1eb7860f8a219edb pending: gate red: none` on every poll from 20:10 to 20:49 UTC (`ev/classify.log`).
- Red checks: `tests / mutation` is in the owed-reds set, and the body answers it by naming its unpinned sites. That answer does not hold for 936 GUARD_OFF (see Block). The `gate` red at render was its own wait on run 45055462774, not a finding.
