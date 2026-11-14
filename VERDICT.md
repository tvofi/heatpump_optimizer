Fix review: merge af01d592585120f546221394cb694bf6e51a94b1

bus-nonce: 7fd72449efbb3ea44276e238d650b98b
pending-ci: gate

## Scope

First round (no reviewed head). Part 4 of R10-SAV-VALUATION-RESIDUE, Carry 9 only: `thermal_model.valve_top_equilibrium`, `optimizer._held_at_valve_top`, `_pump_unreachable`, `_held_bisected`. Measured at head af01d592585120f546221394cb694bf6e51a94b1 (still `refs/pull/3587/head` when this verdict was written), merge base a2ef25b4b25b7d34bfe17e04697bef70ae454277. The base end is the head's tree with `custom_components/` checked out from the merge base. `dev/governance/roles/` is unchanged between the merge base and origin/main.

## Evidence

- Finder's harness `dev/audit/harnesses/r10_sav_held_install.py`, both ends (`ev/harness_both_ends.txt`). The output matches `## Figures` row for row. RESULT base install +5/-5/-15 C: held level 20.527/20.029/19.532, gap 0.482/0.806/1.130. RESULT head: held 20.719/21.009/20.428, 20.350/20.835/19.864, 19.980/20.661/19.300, each gap 0.000. The controls are flat at both ends: one-tank 20.662/19.115/17.568 with gap 0.000, and valve off held at 21.000/21.000/21.000. Precondition rc 0 at both ends.
- The 3481 `fields` arm (measurement (1)) was not re-run: 3481's head is not this PR's tree. Not re-derived.
- Bitwise probe figures, re-derived with my own probe (`ev/kwh_probe.txt`, `ev/probe_kwh.py`; kWh_e = sum of `_compute_baseline_power` power x 0.25 h). All eight match the body: +5 C 12.7979 to 12.9413, 0 C 19.9060 to 20.1266, -5 C 29.5526 to 29.8781, -15 C 64.9236 to 65.6335. The held rooms 20.527/20.278/20.029/19.532 to 20.719/20.534/20.350/19.980 also match. The body's "20 of 24 rows identical" count uses six houses the body does not name, so I did not re-derive the count itself. Its valve-off and one-tank controls are flat in the harness at both ends.
- Mutation proof (`ev/mutant_run_diff.txt`). I re-ran the body's `mutant_run.py --diff` against the merge base over the group's block. It reports only three SURVIVED lines, all CMP_BOUND: optimizer.py:894, optimizer.py:914 and thermal_model.py:2404. These are the three triaged equivalent under `tests/mutation_ledger/survivor_triage/`.
- Targeted mutants (`ev/mutants.txt`, block `ALL 13 FEATURES BLOCK PASSED` on NULL before and after). KILLED: drop the `_held_at_valve_top` call (the Carry 9 install check fails), ignore the pump bound (the 1 kW fallback check fails), drop `need_kw > valve_top_draw` (part 1's pump check fails), drop `two_zone_enabled` (ValueError), GUARD_OFF on the equilibrium's guard, CLAMP_DROP on `t_rad` and on `t_floor`, room as the upper floor only, and drop `if top is None`.
- Targeted mutants that SURVIVED:
  - `dt` from `math.inf` to 0.25 and a zero solve origin. Both are equivalent by construction: the tank is at its goal, and the rates are affine. The body says it changed these lines for exactly that reason.
  - Dropping `is_throttling`. The only non-throttling mode is `none`. Over 32 valve-`none` rows (4 outdoor temperatures x 2 sun levels x 1/2/4/9 kW pumps) the held state is bit-identical under this mutant (`ev/throttle_probe.txt`): equivalent on that probe.
  - Dropping either half of the `upper >= t_rad or slab >= t_floor` guard. See `## Findings`.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against origin/main 82fa3884c2, with closures.json resolved by LEDGER-MERGE (`ev/merge_tree.txt`).
- VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff). `tests/golden/` and both claim files are untouched. I cite CI's tests lanes for golden drift and did not re-run it.
- Forward-carry: the body's plant-curve finding carries to R11-INTAKE-R10-RESIDUE. That group is in `dev/programme/rosters/wave-r10-groups.json` at this head and on main. The packet's carry_audit reads it routed, with 0 bad destinations. It states its precondition and control: the one-tank row within 0.02 K, the two-zone direct circuits bitwise unchanged, and each moved fixture claimed.
- Red checks: the body answers `tests / mutation`, the predicted red from 8 ADDED UNPINNED sites, and names ci_predict.py as the cheaper detector that already fired.
- CI: `merge_train.py classify af01d592585120f546221394cb694bf6e51a94b1 --pr 3587` polled from 13:21 to 13:51 UTC and printed `WAIT af01d592585120f546221394cb694bf6e51a94b1 pending: gate red: none` (rc 3) every time (`ev/classify.txt`). No red at the head when this verdict was written, so `## Red checks` is owed nothing beyond the body's `tests / mutation` answer.

## Findings

- Residual: the fallback domain still books the warming Carry 9 removes on the default curve. Where `valve_top_equilibrium` returns None (a circuit's top at or below its zone, so a low curve or sun), `_thermostat_held_state` keeps level floors below the plant's own ceiling. `ev/gap_probe.txt` runs the install at 21 C target with the finder's plant column (288 steps at `max_electrical_power`, constant weather). Head held vs plant room:
  - +5 C, no sun, curve 3 C: 6.794 vs 6.992 (gap 0.216)
  - +5 C, 150 W/m2, curve 3 or 10 C: 12.881 vs 13.113 (0.247)
  - +5 C, 300 W/m2: 18.468 vs 19.179 (0.757)
  - -5 C, 300 W/m2, curve 3 C: 8.468 vs 9.179 (0.757)
  The same rows are identical at the merge base, so nothing regressed. On the default curve every unreachable row reads gap 0.000 at the head. The PR dispositions this domain: its body says "anywhere else, the level bisection holds as before", and its third Carry 9 check pins level floors there. So it is not class-open. The gap there is unmeasured in the body. A later stage owes the measurement on that domain with this probe's plant column as its control, re-measured at its own merge base, and must decide whether the reference should follow the plant there (a non-affine equilibrium, the drawing circuit only). Carry: R11-INTAKE-R10-RESIDUE
- Test gap: each half of `valve_top_equilibrium`'s guard is unpinned. `if upper >= t_rad:` alone and `if slab >= t_floor:` alone both pass the group's block; only GUARD_OFF on both halves is killed (`ev/mutants.txt`). The slab-only arm is reachable: 3 calls over a 1,440-configuration grid (`ev/guard_probe.txt`), at -15 C, 600 W/m2, curve 10 C, 9 kW pump, cap none/25/30. There, dropping the slab half moves the held room from 11.501 (level) to 11.580, with the plant at 11.643 (`ev/probe_half.py`). So the mutant lands nearer the plant than the head does, and the arm's correctness belongs with the residual above. The upper-only arm never fired in the grid. Whoever takes up the residual pins the slab-only arm with that configuration, or records it unreachable on a physical weather bound. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
