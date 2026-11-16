# R11-VALVE-REFERENCE: the single-zone valve curve, the thermostat reference behind it, and the booked reference's digest (architect note, round 1)

Designer seat, round 1. Base and code read: `367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c` (origin/main; After: none, so no predecessor head). Finder harnesses: `dev/audit/harnesses/r10_sav_held_install.py` (carry 0) and `dev/audit/harnesses/r10_advisor_steady_seams.py` `fields` (carry 1); carry 2 has none: its evidence is the probe below. Figures marked (spike) come from an uncommitted scratch patch of `_valve_flow_set` and `mixing_valve.flow_setpoint` implementing the shape below at this base; the fixer re-measures every one at both ends.

## The defect, measured

One cause behind carries 0 and 1. `mixing_valve.flow_setpoint` spreads the house's loss over the emitter UA only (`_valve_ua`, 1.4 kW/K on the one-tank fixture). `_single_valve_rates` delivers that UA into the slab, and the slab reaches the room through `slab_heat_transfer` (0.8 kW/K) in series, so the steady room solves (curve − T)·k = U·(T − outdoor) − gains with k = UA·ks/(UA + ks) = 0.509 kW/K, not UA. That closed form, with U 0.1635 kW/K (wind 3 m/s) and `internal_gains` 0.3 kW, gives 20.662 / 19.115 / 17.568 at +5 / −5 / −15 C, the harness's `one-tank` plant rows to the printed digit. At target 21 the curve's top draw is below the need, so `_held_unreachable` is true and `_thermostat_held_state` bisects down to that same equilibrium: the `fields` arm's one-tank thermostat ends at 19.88 and 24 of 72 rows read 0 or against the ask at this base. Two-zone curves feed the radiators directly, which is why the install's upper floor reads 21.009 and the two-zone valve two-tank control 21.01.

## Owning seam

One owner: `thermal_model.py`'s single-zone valve topology, at `_valve_flow_set`. `mixing_valve.flow_setpoint` stays the formula's owner and gains one defaulted keyword, so every existing caller computes the same bits. Callers that only pick it up: `_single_valve_rates` (scalar step and the batch path's per-substep call), `_valve_draw_circuits`' single-zone branch, and through it `valve_hold_temperature` and `valve_top_draw`; `optimizer.py`'s `_thermostat_held_state`, `_held_unreachable` and `_compute_baseline_power` are unchanged. `ledger.py` changes one constant (`REFERENCE_BASIS`). No second owner.

## Shape

- `mixing_valve.flow_setpoint` gains a keyword for free heat in kW, default 0.0: the held loss becomes max(0, U·max(0, target − outdoor) − free heat). With 0.0 and a non-negative loss, max(0, x − 0.0) is x bit for bit.
- `_valve_flow_set(p, valve_target, outdoor_temp, heat_loss_coefficient, emitter_ua)` keeps its signature. When `p.two_zone_enabled` is false it passes the series conductance `emitter_ua · ks / (emitter_ua + ks)`, ks = `slab_heat_transfer_floored`, and `p.internal_gains` as the free heat; the two-zone branch passes both as today. Every single-zone caller then shares one curve, including `tests/features.py`'s `_single_valve_charge_landing`, which calls `_valve_flow_set` with `_valve_ua` and stays valid unchanged.
- `ThermalModel.flow_target_for_indoor`: the single-zone branch returns `_valve_flow_set(p, indoor_target, outdoor_temp, U, _valve_ua(p))`, U the effective `heat_loss_coefficient` at no wind; the two-zone branch is unchanged. Its docstring says it is the same conversion as the plant's; after the curve moves, measured, the plant's single-zone curve is 27.714 / 33.607 C at +5 / −15 against this function's unchanged 24.929 / 27.071 (spike), and `sysid.py`'s at-curve test reads it.
- `ledger.REFERENCE_BASIS` 3 → 4, with its comment line: the booked reference changes on every single-zone valved install.

        _single_valve_rates / _valve_draw_circuits (single) / flow_target_for_indoor (single)
          -> _valve_flow_set [single: series k, free heat = internal_gains | two-zone: as today]
          -> mixing_valve.flow_setpoint(.., free heat)
        _thermostat_held_state -> valve_top_draw / valve_hold_temperature -> _valve_draw_circuits (unchanged)

Invariants, each a test: (a) the one-tank plant at `max_electrical_power`, settled, holds the curve's target within 0.02 K; (b) `_thermostat_held_state` at 21 on the one-tank fixture holds 21.000; (c) every two-zone and every unvalved path is bitwise unchanged; (d) single-zone `flow_target_for_indoor` equals the plant's curve; (e) the reference digest moves only on single-zone valved installs.

## Alternatives, and why each lost

- **Series conductance without the free heat**: settles at 23.415 after the harness's 288 steps and 23.446 in closed form, 0.4 K past its target, so invariant (a) fails (spike).
- **Hour-resolved gains** (`internal_gains_at`): `_single_valve_rates` and the batch path carry no hour; threading one through both adds an argument to every step for a residual the fixer measures instead (Notes).
- **Emitters on the room, not the slab**: changes the single-zone plant's topology and removes the slab storage `recommend_target` is built on; moves every valved single-zone plan, not only its curve.
- **Correct only the reference** (a lower thermostat target, or skip the valve in `_thermostat_held_state`): the plant still misses its own curve (carry 0 stays open) and the curve's concept gains a second owner in `optimizer.py`.

## Sibling sites

`git grep -n -e "flow_setpoint(" -e "_valve_flow_set(" -e "_valve_ua(" -e "flow_target_for_indoor(" -- custom_components`. Covered: `thermal_model.py` `_single_valve_rates`, `_valve_draw_circuits` single branch, `flow_target_for_indoor` single branch; `sysid.py` and `flow_lift.py` follow it. Out of scope: the two-zone curve sites in `_valve_two_zone_delivery`, the batch two-zone substep and `_valve_draw_circuits`' two-zone branch (the finding's control, kept bitwise); `coordinator.py`'s flow write, which refuses single-zone (`valve_flow_needs_two_zone`). The two-zone valve-fed slab (`slab_fed_direct` false, the owner's `replay_install`) has the same series omission on its floor circuit (lower floor 20.428 at +5 C): see Notes.

## Evidence plan

- **Failing tests first**, `tests/features.py`, a new section after the R10-HOTFIX-SAV-ESTIMATE reference-basis block, on the production symbols: (a) at +5 / −5 / −15 C, 960 steps from the held state; (b); (d) for the one-tank fixture and `ThermalParameters` defaults with a valve. (a) and (b) fail at this base (20.662, 19.115, 17.568); (d) passes at both ends and guards the sibling.
- **Reference digest (carry 2)**, same section: sha256 of `_compute_baseline_power`'s power array rounded to 1e-6 kW plus its end room and tank, over three installs (`replay_install` with its manual valve, the one-tank fixture, `house(dhw=False)` unvalved) at +5 and −15 C with a sinusoid on outdoor, recorded as literals beside the `_SB_NOW` check, its message naming the `REFERENCE_BASIS` bump. Measured (probe): raw-byte and rounded digests identical under `OPENBLAS_CORETYPE` native, Haswell, Sandybridge and Nehalem at this base; at the spike the one-tank digests move and the other four are identical, so the pin detects this change. AVX-512 is not measured here: the fixer reads it from CI's tests job on the p1 head before p2.
- **Commit order**: p1 lands the digest at this base's values, green; p2 changes the curve, which turns that check red, then re-records the two one-tank digests and bumps `REFERENCE_BASIS` and the `_SB_NOW == 3` literal and stamp beside it. Both p2 runs go in the body. No pinned grader registers anything.
- **Finder's harnesses, both ends.** `r10_sav_held_install.py`: `install` and `valve off` rows identical (spike: identical); `one-tank` held 21.000 at all three, plant 22.975 at 288 steps (spike), short by settling: 960 steps read 23.000 (spike). The fixer adds a settled plant column (step 18) and keeps the existing columns. `fields`: one-tank thermostat 19.88 → 21.00, rows against the ask 24 → 1; single-zone, two-zone and two-zone valve two-tank rows identical (spike).
- **Null control**: the harness outputs above at base against head differ in the one-tank lines only (`diff`).
- **Goldens**: none expected to move: every valved scenario in `tests/golden.py` is two-zone and no `coord_*` capture sets a valve. One that moves is claimed under `claim-files.md`, never re-recorded.
- **Mutation proof**: the series expression in `_valve_flow_set`'s single-zone branch (killed by a, b); the free-heat argument and its subtraction in `flow_setpoint` (killed by a); the `two_zone_enabled` gate (killed by c and the install digest); `flow_target_for_indoor`'s single branch (killed by d).

## Hot files, serial position, carries

Hot files: `custom_components/heatpump_optimizer/thermal_model.py`, `custom_components/heatpump_optimizer/mixing_valve.py`, `custom_components/heatpump_optimizer/ledger.py`, `tests/features.py`, `dev/audit/harnesses/r10_sav_held_install.py`. After: none. Owes carries 0 (items 1364d60a), 1 and 2 (items 11e9ad5a) from R11-INTAKE-R10-RESIDUE; receives none.

**Dispatch condition, decision: owner.** Carry 1 asks for a reproduction on an install's own valve parameters from a diagnostics bundle before any change. No committed bundle has a single-zone valved install (`tests/replay/` holds the owner's two-zone install and `synthetic-dhw-only.json`, unvalved). Reproduced instead on R10-COMBI-TANK's install shape (`r10_combi_tank.py` `params()`, synthetic, smart-write valve): held 20.734 / 19.214 / 17.694 at this base, 21.000 with the plant settling at 23.000 (spike). The closed form above holds on any finite `slab_heat_transfer`. Whether that substitutes for the bundle is the owner's: pending owner confirmation, quoting carry 1's precondition.

## Notes for the fixer

- The two-zone valve-fed slab misses by the same series term (install lower floor 20.428 at +5 C, `slab_fed_direct` false); it moves the owner's install, `REFERENCE_BASIS` 2's two-zone hold and every valved golden, so this group keeps it bitwise; the pull request files it as a new issue by the sibling-seam rule. Carry: R11-VALVE-REFERENCE (item s1)
- One `fields` row stays at 0 at the spike: `night-1` asked at 21:00 on the one-tank valve house; measure its cause at your head and route it. Carry: R11-VALVE-REFERENCE (item s2)
- With a learned gains profile the curve uses the constant `internal_gains`; measure the hourly miss, (gains at the hour − `internal_gains`) / (k + U), on a profile fixture. Carry: R11-VALVE-REFERENCE (item s3)
- Before this branch, `flow_target_for_indoor` sums `upper_floor_heat_loss` and `lower_floor_heat_loss_learned` on a single-zone house; they equal `heat_loss_coefficient` on the profiles fixture and on `ThermalParameters` defaults (0.08 + 0.07 = 0.15, 24.929 C both at +5 C) and differ only where an install configures them apart; the single branch above removes that read, so pin (d) on such a configuration too. Carry: R11-VALVE-REFERENCE (item s4)
