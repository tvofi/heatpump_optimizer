Fix review: blocked 69078d59a07a929555e77c79432e4aa655941bb2 class-open: the held state's infeasibility predicate guards only the valve curve's top draw, not the heat pump's capacity

bus-nonce: b5f532ce44cc1744431181abeb8168bb

Round 1 (first review), full scope, measured at head 69078d59a07a929555e77c79432e4aa655941bb2 (still the branch tip at verdict time).

## Block

class-open (fix-review.md step 6, a predicate's unguarded domain). The body's cause is general: a held state that no thermostat keeps makes every booked reference step draw its stores, booked as unpaid reference heat. The fix's predicate `short(held) > 0.0` compares the level-zone steady need only with `valve_top_draw`. The other bound on deliverable heat is the heat pump's maximum output, and that domain is unguarded. There the held zones stay at 21 C while the reference runs at `heat_pump_max_power` and draws stored heat every step. This happens on valved and unvalved installs alike.

- Instrument: `ev/cap.py`, which drives the PR's own `_svh_case` construction: `profiles.house`, a one-step horizon, `_compute_baseline_power`, and one `simulate_step` from the held state. It runs two-zone at -25 C with `buffer_tank_volume` 750 and `buffer_max_temperature` 56.
  - `mode=none hp_max=4.0`: held room 21.000, power 4.000, first-step dS -1.0724 kWh_th.
  - `mode=manual` (valve target 40, a curve that holds the setpoint) `hp_max=4.0`: held room 21.000, power 4.000, dS -1.0762 kWh_th.
- Perturbation (the harness moves): `hp_max=9.0` in the same cases reads dS +0.0000, power 8.085 / 8.076.
- The same figures appear at the merge base e59e21fe (`ev/capacity_control.txt`), so this is the pre-existing sibling seam, not a regression.
- Breadth (`ev/capacity_probe.txt`): over 64 cases (none/manual × zoning × hp 4/6/9 × valve target 25/40 × outdoor -25/-15/-5/5), every draw above 0.02 kWh_th, 16 cases (10 unvalved, 6 valved), has the power at `heat_pump_max_power` and the held room at 21.0. No draw remains where the power is below the maximum.
- The body neither handles nor dispositions it. Its class sweep enumerates the readers of `_thermostat_held_state` (every one dispositioned, re-run: optimizer.py:605 the definition, :5724, :5831), but the class is the infeasibility predicate's domain. Its "Unvalved installs are untouched" is true of the code and is exactly the open seam.
- Remedy, the fixer's choice: extend the predicate to the smaller of the curve's top draw and the heat pump's deliverable heat at max power (with a mutation proof and the capacity null control above), or disposition the seam in the body with a destination (`finding-propagation.md`, sibling seam: a new issue filed by this PR or a carry file).

## Findings

- The capacity seam above: the held state stays at a setpoint the heat pump cannot deliver, so its booked steps draw stored heat (-1.07 kWh_th per step at -25 C on a 4 kW two-zone house, valved or not), unchanged by this PR. Carry: R10-SAV-VALUATION-RESIDUE

## Evidence

- RESULT mutation proof, `ev/mutation_proof.txt` (the group's block via `features_block.py`, each line restored afterwards). M1 (`if False:`), M2 (bisection step to `(lo, mid)`), M3 (`valve_top_draw` returns inf), M5 (final `held = _held_zones(..., lo)` dropped) and M6 (`need` evaluated at `target`) each FAIL the held-state check. M4 (`if True:`) FAILs the null-control check. NULL (comment edit) reads `ALL 5 FEATURES BLOCK PASSED`.
- RESULT the reviewer's own mutant M7 (`held_need` taken at the target's zones) survives the block. Reasoned equivalent: at the equilibrium `held_need` equals the curve's top draw to 2**-40 of the span, and above it `valve_hold_temperature`'s `np.interp` clamps to the top kink, so both arms land on the same tank temperature. Not separately measured on the full `features.py`. Carry: dismissed: evidence, not a finding
- RESULT the head's test block against the base's production code (e59e21fe with the head's `tests/features.py`): `1 of 5 FEATURES BLOCK FAILED`, the held-state check. This is the body's at-base FAIL, re-taken at the merge base rather than at 14f227c5.
- RESULT the finder's harness `dev/audit/harnesses/r10_sav_residual_attribution.py` at both ends (`ev/harness_*`). Base: residual -3.90 % flat / -8.02 % `winter_typical`, reference stored -34.85 kWh_th, non-steady +12.52 / +11.89. Head: +4.78 % / +1.20 %, stored -0.30, non-steady -0.30 / -0.93. `plant steps seen 192 of 192` at all four. Every figure matches the body. Disclosure: this harness is the group's committed instrument named in the body, and the packet records no separately named finder's harness.
- RESULT configuration probe (`ev/config_probe.txt`): 1296 cases (smart_read/smart_write/manual × zoning × default/two_tank_4way × hp 4/6/9 × valve target 21/25/30/40 × outdoor -25..18 C). No exception, every held room within [outdoor, 21]. The worst first-step dS, -1.0762, is the capacity case above.
- Null control re-run inside the block and the capacity probe: valve target 40 holds 21.0 at both zonings.
- `git merge-tree --write-tree origin/main 69078d59...` exit 0: merges cleanly.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot diff stat empty).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2709 ENTITY CHECKS PASSED`, exit 0 (`ev/entities_full.txt`). An earlier run cut by my own 220 s timeout is `ev/entities.txt`, not a failure.
- Mutation ledger: the two deleted `killed_by` rows key lines this diff rewrote. The triage rows' equivalence arguments (CONST 40, both CMP_BOUND) are consistent with the bisection's 2**-40 bracket. I did not re-measure them.
- Figures I did not re-derive: the gate scope line, `mutation_table.py`'s unpinned count of 2608, the `r10_partload_pricing.py` and `r10_sav_valuation_residue.py` readings, and the 5.612 / 4.357 kW base infeasibility probe (scratch, not in the tree). The CI heavy runs are cited, not re-run.
- CI at this head: `merge_train.py classify` last printed `WAIT 69078d59a07a929555e77c79432e4aa655941bb2 pending: gate red: none` (rc 3, `ev/classify.txt`). Red checks were not judged, since the block stands on its own.
