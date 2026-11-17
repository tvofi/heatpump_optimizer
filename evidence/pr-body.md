R11-VALVE-REFERENCE: a single-zone valve curve that holds its own target, a thermostat reference that reaches its setpoint behind it, and a digest pin on the booked reference. Built to the approved architect note (design/R11-VALVE-REFERENCE at 1abf062b2d, `Design review: approve 1abf062b2d41ce2fdd7ef89791d801f14e43ebab`).

One cause behind carries 0 and 1. A single-zone valve feeds every emitter into the slab (`_single_valve_rates`). The slab reaches the room through `slab_heat_transfer` in series. `mixing_valve.flow_setpoint` spread the house's loss over the emitter UA alone, so the plant at its pump settled 2.3 to 5.4 K short of the curve's 23 C target. `_thermostat_held_state` bisected down to the same equilibrium.

What changes:

- `mixing_valve.flow_setpoint` gains `free_heat_kw` (default 0.0): the held loss is `max(0, U * max(0, target - outdoor) - free_heat_kw)`. With 0.0 every existing caller computes the same bits.
- On a single-zone house, `_valve_flow_set` passes the series conductance `ua * ks / (ua + ks)`, with `ks = slab_heat_transfer_floored`, and `internal_gains` as free heat. Two-zone callers pass through unchanged. `_single_valve_rates` (scalar and batch), `_valve_draw_circuits`' single branch, `valve_hold_temperature` and `valve_top_draw` pick this up.
- `ThermalModel.flow_target_for_indoor` returns the plant's `_valve_flow_set` curve at zero wind, gated on `not two_zone_enabled and is_throttling(mixing_valve_mode)`. Every other install runs the old expression, so every priced direct curve is unchanged.
- `ledger.REFERENCE_BASIS` 3 → 4, because the booked reference moves on every single-zone valved install. A month stamped 3 now states no saving (new check), and a month stamped 4 keeps it.
- `tests/features.py`, beside the reference-basis checks, gains invariants (a), (b), (c′), (d) and the reference digest (carry 2).
- `dev/audit/harnesses/r10_sav_held_install.py` gains a `settled` column (960 steps) and a `combi` row (R10-COMBI-TANK's install shape). Existing columns are kept.

Existing checks that read the old single-zone curve, and what each now reads. The scoped gate's first run at p2 failed these five:

- `single-zone valve: the tank's loss is the slab's delivery plus standing loss` and `… the slab receives exactly what the tank delivered`: these re-derived the emitter-only curve by hand to compute the expected delivery. They now read the production `_valve_flow_set`, and the energy balance they pin is unchanged.
- `zoned store census: the cap books what it refuses in every zoning (#2500)`: the cap arm put a 69.5 C tank over a 25 C slab. With the curve at 31.2 C the slab's draw now takes the pump's whole output, so nothing reaches the cap (refused 0.0000 kW). The arm's slab moves to 30 C, near the curve, where the cap refuses 3.9072 kW (two-zone 2.7147 kW). Probe: one `simulate_step` per slab 25 / 28 / 30 / 31 C.
- `combi flux exchange: …`: on the combi fixture (single zone, `smart_write`) the first exchange now settles on its fourth DHW build: per-round moves 4.00 / 4.00 / 2.22 / 6.4e-14 kW, against 4.00 / 2.96 / 2.6e-14 at the base. At the cap of 4, "converged" and "capped" then read the same count. The converging arm now runs under a raised cap of 8 and must end below it; the moving arm stays at the production cap and must read exactly 4, and the check asserts the production cap is still 4. Cost: builds per exchange [3, 3] at the base and [4, 3] at the head on this fixture, so one more DHW plan build in the first exchange of a single-zone combi solve. Probe: `_combi_flux_exchange` wrapped to print each round's max |Δ schedule|.
- `R10-SAV-VALUATION-RESIDUE: behind a valve whose curve cannot hold the setpoint, …`: its precondition required the single-zone held room below 20.9 C at −10 and −15 C, which is the defect carry 1 removes. The stored-heat property holds on all eight rows. The shortfall precondition stays on the two-zone rows (19.705 and 19.442 at the head, the s1 seam), and the single-zone rows must now hold 21 C within 1e-3.

Deviations from the note, each with its reason:

- **(d) fails at the base, not only at mutation.** The note said (d) passes at both ends. At e352724335 it fails on the `floors apart` configuration that note s4 asks for: `upper_floor_heat_loss` 0.12 and `lower_floor_heat_loss` 0.09 against `heat_loss_coefficient` 0.15, so the model reports 23.88 against the plant's 23.057 at +5 C. It also fails on `ThermalParameters` defaults at −15 C, by one ulp (25.62857142857143 against 25.628571428571426): two summed losses against one. At the head it passes on all nine rows. Both base failures are the curve disagreement the gated branch removes.
- **The design reviewer's note r3 is built as an assertion in (c′).** For `none` and every throttling mode, `from_config` with `flow_curve_cop_enabled` must give `flow_curve_cop is not is_throttling(mode)`. That is the coupling that keeps the gated curve off the price path. I did not re-key the gate on `cop_flow_carnot`: that would change which predicate the plant reads, which is outside the note.

**Pending owner confirmation (the note's dispatch condition, carried as written).** Carry 1's precondition reads: "Precondition before any change: reproduce on an install's own valve parameters (the fixture is synthetic; R10-COMBI-TANK's install is this layout)". The brief adds "from a diagnostics bundle". No committed bundle has a single-zone valved install. `tests/replay/` holds the owner's two-zone install and an unvalved DHW-only one. I reproduced instead on R10-COMBI-TANK's install shape (`r10_combi_tank.params()`, single zone, `smart_write` valve, combi tank), now the harness's `combi` row: held 20.734 / 19.214 / 17.694 at the base and 21.000 at the head. Whether that stands in for a bundle is the owner's call, and the orchestrator dispatched this fixer with it open. Carry: R11-VALVE-REFERENCE (item dispatch-condition, pending owner confirmation)

## Head

`c77e7e8f97f5a3904671928720a151aa5283352b` merges main `92d38ec` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`2146b9c7d853d271226cdfa52b5ef5153b8779bd` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

prepr: passed rc=0 at c60b23450f351f073834b4795425ee2d577c1735 (scoped: `PREPR_SKIP_CLOSURES=1`, the closures run in the scoped gate below; `MUTANT_CMD` set to this group's block).

`c60b23450f351f073834b4795425ee2d577c1735`, the code head `handoff/r11-valve-reference` points at. Its merge base is e352724335c136b65562cd3e71f728549ad04a82, the base the brief gave. origin/main was at 6f422812d5 at 2026-11-16T17:39Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. Every figure below is at this head unless it names another commit. The finder harnesses re-run at 2bce6190cd print byte-identical output to the p2 commit df9499a1b1 (`cmp`). c60b23450f changes only how two gate conditions are spelled and one docstring, bit for bit, and the block, M5, M6 and BOOLOP were re-run on it.

Scoped gate at this head: `HPO_GATE_LOCK_LABEL=r11-valve-reference GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e352724335c136b65562cd3e71f728549ad04a82 ./tests/run.sh` printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and exited 0.

## Mutation proof

Each mutant was applied in a separate worktree at the head, then the new block was run (`python3 tools/audit/seat/features_block.py "# R11-VALVE-REFERENCE (carry 2)" "# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0"`, `PYTHONPATH=tests/hastub:tests:custom_components`) and the file restored:

- M1, series conductance deleted (`emitter_ua = emitter_ua * k_slab / (emitter_ua + k_slab)` in `_valve_flow_set`): FAIL `the booked reference reproduces its recorded digest on every pinned install …`, FAIL `single-zone valve: the plant at its pump, settled, holds the curve's own target within 0.02 K` (20.499 / 18.952 / 17.405), FAIL `single-zone valve: a thermostat set to 21 C holds 21 C behind it`.
- M2, the subtraction `- free_heat_kw` deleted in `flow_setpoint`: FAIL `… holds the curve's own target within 0.02 K` (23.446 at all three).
- M3, `free_heat_kw = p.internal_gains` deleted in `_valve_flow_set`: FAIL `… holds the curve's own target within 0.02 K` (23.446 at all three).
- M4, `if not p.two_zone_enabled:` → `if True:` in `_valve_flow_set`: FAIL `the booked reference reproduces its recorded digest …` (the `install` digests move).
- M5, `flow_target_for_indoor`'s branch → `if False:`: FAIL `single-zone valve: the curve the model reports is the plant's own, at zero wind and rain`.
- M6, the `is_throttling` gate dropped from that branch: FAIL `no valve: the priced flow curve of a single-zone direct plant is unchanged, bit for bit` (26.625 against 30.142857142857146 at +5 C).

- M7, the outer `max(0, …)` of `flow_setpoint`'s held loss dropped (ci_predict's CLAMP_DROP site): FAIL `single-zone valve: where the house's gains cover its loss the curve sits at its target, never below` (curve 20.558 C against 21.0).

Unmutated head: `ALL 6 FEATURES BLOCK PASSED`. M5, M6 and the BOOLOP site were re-run on the final text of that gate line (`p.mixing_valve_mode in mixing_valve.THROTTLING_MODES`), and all three are still killed.

## Unpinned sites

`python3 tools/pr/ci_predict.py --base origin/main` at the head names seven sites this diff adds. Each is left to `mutation-autofix`, whose lane mutates `custom_components/`. I ran each site's own mutant locally before claiming the kill:

- `custom_components/heatpump_optimizer/ledger.py:80 CONST` (`REFERENCE_BASIS = 4`, mutant `= 5`, on the reference-basis block): killed by `a month's first savings booking stamps the reference in force, once` and `a month stamped 4, the reference in force, keeps stating its saving as it books on`.
- `custom_components/heatpump_optimizer/mixing_valve.py:114 CLAMP_DROP` (`flow_setpoint`'s outer `max(0.0, …)`): killed by M7's check.
- `custom_components/heatpump_optimizer/thermal_model.py:2280 GUARD_OFF` (`_valve_flow_set`'s `if not p.two_zone_enabled:`): killed by the digest check, (a), (b) and the clamp check.
- `custom_components/heatpump_optimizer/thermal_model.py:3504 BOOLOP` (`flow_target_for_indoor`'s gate, `and` → `or`): killed by (c′).
- `custom_components/heatpump_optimizer/thermal_model.py:3504 GUARD_OFF` (`flow_target_for_indoor`'s gate): killed by (d) (M5).
- `custom_components/heatpump_optimizer/thermal_model.py:3506 RETURN_DEL` (the gated `return _valve_flow_set(…)`): killed by (d).
- `custom_components/heatpump_optimizer/thermal_model.py:4312 GUARD_OFF` (`ThermalModel._substeps_and_loss`'s `if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:`). The line was respelled, not added: the base pinned it as GUARD_OFF 3b3b0c0a (`if False:` took features.py to 7 failures), keyed on another spelling. Its own mutant at the head (`if False:`), on the full `tests/features.py` run directly: FAIL `single-zone valve: the stability count subdivides for the tank's own row` (one step 22.000 C against 400 sub-steps 22.411 C), and FAIL `the booked reference reproduces its recorded digest …`. The third FAIL in that run, `_bootstrap drops the package directory so datetime is stdlib`, also fails on the unmutated head when the script is invoked directly rather than through `run.sh`, where it passes.

`prepr.sh`'s diff mutants (`MUTANT_CMD` = the R11-VALVE-REFERENCE block above) leave two survivors, both on `custom_components/heatpump_optimizer/ledger.py:80`, because the checks that read that constant sit in the reference-basis block before it. CONST_SWAP (`REFERENCE_BASIS = 5`) is killed there by the two stamp checks named above. STMT_DEL (`pass`) is killed by the same block, run with its emitted prelude: `ImportError: cannot import name 'REFERENCE_BASIS'`. That import is also at features.py's module level, so the whole script fails.

The two stale pins ci_predict refused (`ledger.py` CONST 481451d2 on `REFERENCE_BASIS = 3`, `mixing_valve.py` `flow_setpoint` CLAMP_DROP 5650fea2 on the old `q_hold` line) are deleted by hand, as its repair line says.

## Null control

- Finder harness, carry 0: `r10_sav_held_install.py` (the head's version, also run on the base tree) differs between base and head only in its `one-tank` and `combi` lines. Command: `diff <(grep -v -e '^one-tank' -e '^combi' base.txt) <(grep -v -e '^one-tank' -e '^combi' head.txt) && echo "NON-SINGLE-ZONE ROWS IDENTICAL"`, which printed `NON-SINGLE-ZONE ROWS IDENTICAL`. So the `install` (two-zone, manual valve) and `valve off` rows are byte-identical. That includes the install's lower floor at 20.428, the sibling seam in Forward-carry.
- Finder harness, carry 1: in `r10_advisor_steady_seams.py fields`, every line but the `valve, one tank` pair is identical between base and head (`diff … && echo "OTHER FIXTURE LINES IDENTICAL"` printed it): single-zone 21.00 / 0 rows, two-zone 21.33 / 0, two-zone valve two-tank 21.01 / 0.
- Digest (carry 2): the four `install` and `no valve` digests are the same literals at both ends. Only the two `one-tank` digests were re-recorded. p2 run 1 (the fix before re-recording) printed exactly one FAIL, the digest check, with `install` and `no valve` unchanged.
- Goldens: `tests/env_drift.py --all e352724335c136b65562cd3e71f728549ad04a82` passes in the scoped gate. No fixture moved, so nothing is claimed and both claim files are byte-identical.
- (c′) passes at both ends and fails only under M6.

## Figures

All runs use `PYTHONPATH=tests/hastub:tests:custom_components` from the tree root.

- Carry 0, the one-tank plant: `python3 dev/audit/harnesses/r10_sav_held_install.py`. At e352724335: one-tank held, plant and settled 20.662 / 19.115 / 17.568 at +5 / −5 / −15 C. At the head: held 21.000 at all three, plant (288 steps) 22.975, settled (960 steps) 23.000 against the curve's 23 C target. `combi`: 20.734 / 19.214 / 17.694 at the base, 21.000 held and 23.000 settled at the head.
- Carry 1, the thermostat behind the valve: `python3 dev/audit/harnesses/r10_advisor_steady_seams.py fields`. At e352724335, `valve, one tank` reads 19.88 with 24 of 72 rows at 0 or against the ask. At the head it reads 21.00 with 1 of 72.
- Carry 2, the digest's BLAS reproduction: the digest probe (the p1 block run standalone) gave one md5 of its six digests under `OPENBLAS_CORETYPE` unset, Haswell, Sandybridge and Nehalem at e352724335. AVX-512 was not measurable on this seat, so CI's tests job at this head reads it.
- Invariants at the head: the block above, `ALL 6 FEATURES BLOCK PASSED`. With the reference-basis block before it (`--prelude` from `--emit-prelude`), `ALL 15 FEATURES BLOCK PASSED` (at df9499a1b1, before the clamp check).
- Structure ratchet: `python3 tests/structure.py`. `class_excess_loc` read 17455 against its budget of 17446 at df9499a1b1, and it reads 17445 at the head, recorded with the reason in c60b23450f's message. Paid inside `ThermalModel` without new calls on a per-step path. The stability row's three-line throttling test becomes one membership test against `THROTTLING_MODES`. `flow_target_for_indoor`'s docstring, which called the whole method the two-zone conversion reused, now states both branches in two lines. No budget is raised.
- Production calls: `PYTHONPATH=tests/hastub python3 tests/stress.py`, run alone under the gate lease. It passed at df9499a1b1. At 2bce6190cd it read 1.052x on `summer/1z/space` and `winter/1z/space/pin-off` (thermal_model.py and mixing_valve.py +2112 / +2208 each), over the 1.05x allowance, because an interim refactor called `is_throttling` and `_valve_ua` in the stability row's per-step fallback. c60b23450f restores call-free code there. At the head: `ALL 116 STRESS CHECKS PASSED`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff e352724335c136b65562cd3e71f728549ad04a82 HEAD` printed `Architecture score: dS +0.0000 NULL`.
- Sibling sites (fixer step 8): `git grep -n -e "flow_setpoint(" -e "_valve_flow_set(" -e "_valve_ua(" -e "flow_target_for_indoor(" -- custom_components` at the head returns these, each with its disposition:
  - `thermal_model.py` `_valve_flow_set`, its single-zone callers in `_single_valve_rates` and `_valve_draw_circuits`' single branch, and `flow_target_for_indoor`'s gated branch: closed in this diff.
  - `_valve_draw_circuits`' two-zone branch (its `_valve_flow_set` call with `two_zone_enabled` true), the direct `mixing_valve.flow_setpoint` calls in `_valve_two_zone_delivery` and the batch two-zone substep, and `flow_target_for_indoor`'s ungated expression: kept bitwise as the finding's control, pinned by the `install` and `no valve` digests and (c′). The two-zone valve-fed slab is the open sibling seam in Forward-carry.
  - `flow_lift.py` `curve_supply_temp` and `sysid.py` `_valve_regulates`: follow `flow_target_for_indoor`. The priced reader is guarded by the `from_config` coupling (c′); `_valve_regulates` now reads the plant's curve, as (d) pins.
  - `coordinator.py`'s flow write: already guarded (`valve_flow_needs_two_zone` refuses single-zone before it reads the curve).
  - `_valve_ua` is the definition, and the comment at the batch path's written-out UA has no call.
- Note s2 (`night-1` at 21:00 on the one-tank valve house, the one remaining 0 row): a scratch probe of `reference_day`'s second pass, both schedules, at 19:00 and 21:00. At the head, at 21:00, the thermostat draws 0.0000 kW-steps on all 36 night-setback steps under both schedules, and the two power arrays are equal: the room coasts above 19.5 C all night, so lowering it to 18.5 C saves nothing and a figure of 0 is the right answer. At 19:00 the live schedule draws 0.1584 kW-steps on those steps and the figure reads −0.12. Control: the unvalved single-zone house reads −0.19 at 21:00.
- Note s3 (constant gains against a learned profile): a scratch probe of the one-tank plant at its pump with `hour_of_day`, the last of 1056 steps' day, at +5 and −15 C. The flat control holds 23.000. The features.py fixture profile `[0.3]*18 + [0.9]*6` rides 23.115 to 23.365 (mean 23.223). A `[0.0]*24` profile settles at 22.554, short by 0.446 K = 0.3 / (k + U), the closed form. `[0.0]*12 + [0.6]*12` swings 22.836 to 23.164 (mean 23.000).
- Note r1 (the bias learner): `curve_supply_temp` at indoor 21 C on the one-tank fixture against the same parameters with mode `none`, at the head. Gated 25.125 / 28.071 / 31.018 against 22.714 / 23.786 / 24.857 at +5 / −5 / −15 C, so the learner's residual moves by −2.411 / −4.286 / −6.161 K. `git grep -n "flow_curve_bias"` shows one spender, `curve_flow_temp`, read by the price path only under `flow_curve_cop`. `from_config` turns that off with a valve (c′), so a valved install spends none. The learner is not reset on a mode change (`coordinator.py` resets `_flow_bias` only on a snapshot without it).

<!-- figure-block: scope-line mb=ef6363d5f291e2eaa60620b5ea12d8d5fb902478 head=2146b9c7d853d271226cdfa52b5ef5153b8779bd -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / mutation` (predicted by `tools/pr/ci_predict.py --base origin/main`): seven sites this diff adds carry no pin yet, each listed under `## Unpinned sites` with its own mutant killed locally. `mutation-autofix` pins them once the pull request exists (`ci-autofix.md`: wait for its commit, do not duplicate it). Cheaper detector: `ci_predict.py`, already a step of `prepr.sh`, which named every site before the handoff. It adds no standing cost, so no countermeasure is owed.

Local runs, none a CI check on a pull request: the first scoped gate, at df9499a1b1, failed `tests/features.py` (the five checks above, repaired by 734069c019) and `tests/structure.py` (`class_excess_loc` +9, paid in 2bce6190cd and c60b23450f). The second, at 2bce6190cd, failed `tests/stress.py` (production calls, repaired by c60b23450f) and `tests/structure.py` (an improvement left unrecorded, recorded in c60b23450f).

## Forward-carry

- s1, sibling seam: the two-zone valve-fed slab (`slab_fed_direct` false, the owner's `replay_install`) has the same series omission on its floor circuit: the install's lower floor holds 20.428 at +5 C, 19.864 at −5 C and 19.300 at −15 C in `r10_sav_held_install.py`, unchanged at both ends. Fixing it moves the owner's install, `REFERENCE_BASIS` 2's two-zone hold and every valved golden, so this group keeps it bitwise as the note requires. Its destination is a new issue: the sibling-seam rule wants one filed by this pull request, and this seat cannot file it. No live group in the valid carry set owns the two-zone valve topology. Carry: R11-VALVE-REFERENCE (item s1, pending orchestrator ruling: file the issue at the PR's opening)
- s2, the `night-1` 0 row (Figures): a correct zero, measured. The harness's `at 0 or against the ask` count treats it as a miss, and the advisor's measurement owner is the stage that reads that count. Carry: R11-ADVISOR-MEASURES (item s2)
- s3, hourly gains: the approved note chose the constant `internal_gains` over threading an hour into every step. Measured residual: up to +0.365 K over the curve's target on the fixture profile, and −0.446 K under it where a learned profile's gains sit below the constant. That costs the reference its setpoint only where the configured valve target equals the setpoint. Whether to read the profile's mean is a design ruling, not a fixer's. Carry: R11-VALVE-REFERENCE (item s3, pending orchestrator ruling)
- r1, the bias learner: no reader spends a bias learned behind a valve while the valve is configured (Figures). It would be spent after the valve is removed with `flow_curve_cop` on, and it was already learned against tank-charge supply there before this change. The note's countermeasure (skip observation under `is_throttling`) is two lines in `coordinator.py`'s guard and also changes two-zone valved installs, which this group keeps bitwise, so it is not built here. Carry: R11-VALVE-REFERENCE (item r1, pending orchestrator ruling)
- s4: built, as (d)'s `floors apart` row. Carry: dismissed: built in this pull request
- r3 (design review): built, as the coupling assertion in (c′). Carry: dismissed: built in this pull request

## Friction

none

