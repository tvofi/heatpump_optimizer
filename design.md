# R11-SEAM-two-zone-slab: the two-zone valve curve with the slab in series (architect note)

Designer seat, round 1. Base and code read: `8cc3fb3e35b8cf320124af236f1c713a928e5685` (After: none, so no predecessor handoff head; the code is read at this base, which contains R11-VALVE-REFERENCE's merges #3685 and #3715). Finding: issue 3713, R11-VALVE-REFERENCE carry 3 item 2c38f69d, from that group's approved note (design/R11-VALVE-REFERENCE at 1abf062b2d, Notes, first bullet). Finder harness: `dev/audit/harnesses/r10_sav_held_install.py`, `install` rows. Figures marked (spike) come from an uncommitted scratch patch of the four sites below at this base, container pinned to `OPENBLAS_CORETYPE` Haswell; the fixer re-measures each at both ends.

## The defect, measured

`_valve_two_zone_delivery`, the batch twin's throttled substep and `_valve_draw_circuits` compute the two-zone curve as target + (Uu + Ul)·(target − outdoor) / (ua_rad + ua_floor). The floor circuit heats the slab, which reaches the lower floor through `slab_heat_transfer` in series (`_two_zone_rates`), so its steady conductance is ua_floor·ks/(ua_floor + ks), not ua_floor. On `profiles.replay_install` (valve `manual` at 21, `slab_fed_direct` false, ua_rad = ua_floor = 0.533, ks 0.7, `inter_zone_transfer` 0.5) the harness reads room/upper/lower held, end, plant and settled alike at 20.719/21.009/20.428, 20.350/20.835/19.864 and 19.980/20.661/19.300 at +5/−5/−15 C (this base). The curve also omits `internal_gains`, which the single-zone branch of `_valve_flow_set` counts since R11-VALVE-REFERENCE.

## The law

One flow temperature feeds two unequal paths, so no curve holds both floors; it holds the thermostat's variable, `room_temperature` = r·Tu + (1 − r)·Tl, r = `upper_floor_area_ratio` (thermal_model.py:2456 "upper_floor_area_ratio", in `valve_top_equilibrium`). Steady `_two_zone_rates` at zero sun, with a = ua_rad, b = ua_floor·ks/(ua_floor + ks), ks = `slab_heat_transfer_floored`, c = `inter_zone_transfer`, Uu and Ul the step's `_zone_loss`, G = `internal_gains`:

    A = a + Uu + c,  B = b + Ul + c,  wu = r·B + (1 − r)·c,  wl = r·c + (1 − r)·A,  s = wu + wl
    curve = flow_setpoint(target, outdoor, heat_loss = (wu·Uu + wl·Ul)/s,
                          emitter_ua = (wu·a + wl·b)/s, free_heat = (wu·r + wl·(1 − r))·G/s)

It is the solution of the 2×2 steady system for room = target, written in `mixing_valve.flow_setpoint`'s form, so that function is unchanged (its `free_heat_kw` keyword exists). As c → ∞ it reduces to the conductance sum (a + b, Uu + Ul, G). Measured (spike), `install` rows held = settled: 21.000/21.296/20.704, 21.000/21.499/20.501, 21.000/21.701/20.299; the lower floor sits below target by the topology's split, which `radiator_power_fraction` sets, not the curve.

## Owning seam

One owner: `thermal_model.py`'s two-zone valve topology, at `_valve_flow_set`, whose two-zone branch gains the law behind `not p.slab_fed_direct`. `tests/seam_map.json` maps coordinator units only; no coordinator line changes. Callers that change only to route through it: `_valve_draw_circuits` (two-zone branch), `_valve_two_zone_delivery` (drops its inline target fallback and `flow_setpoint` call; its `u_eff` parameter becomes the pair of zone losses, keeping the ten-parameter guard), the batch twin's throttled two-zone substep (one call per step, hoisted out of the substep loop: target, outdoor and `_substeps_and_loss`'s pair are per step, and `tests/stress.py` `production_calls` prices calls), and `ThermalModel.flow_target_for_indoor` (new branch for a two-zone throttling valve with a valve-fed slab, at `_zone_loss(0, 0)`). Readers that pick it up unchanged: `valve_hold_temperature`, `valve_top_draw`, `optimizer.py`'s `_thermostat_held_state`, `sysid.py`'s `_valve_regulates`, `coordinator.py`'s flow write (two-zone only). `ledger.py` changes one constant. No second owner.

## Shape

- `_valve_flow_set` keeps its five positional parameters and gains one keyword for the lower floor's loss, default 0.0; on a two-zone house `heat_loss_coefficient` is the upper floor's. Single-zone callers, including `tests/features.py`'s `_single_valve_charge_landing`, are unchanged. Two-zone with `slab_fed_direct` keeps today's bits: heat loss is the same `upper + lower` sum, emitter UA as passed, free heat 0.0.
- `flow_target_for_indoor`: two-zone, `is_throttling`, not `slab_fed_direct` → `_valve_flow_set(p, indoor_target, outdoor, Uu0, _valve_ua(p), lower = Ul0)`; every other install runs today's expression, so `flow_lift.curve_supply_temp`, `direct_flow_carnot` and the direct-slab layout stay bitwise (its emitter UA, design_power/dt, is not bitwise ua_rad + ua_floor).
- `ledger.REFERENCE_BASIS` 4 → 5 with its comment line: the booked reference changes on every two-zone valve-fed install.

        _valve_two_zone_delivery / batch substep / _valve_draw_circuits (two-zone) / flow_target_for_indoor (two-zone valved)
          -> _valve_flow_set [single: as today | two-zone direct slab: as today | two-zone valve-fed: the law]
          -> mixing_valve.flow_setpoint (unchanged)

Invariants, each a test: (a) `replay_install` at `max_electrical_power`, 960 steps from the held state, wind 3 m/s, room within 0.02 K of 21 at +5/−5/−15 C, scalar step and batch twin both; (b) `_thermostat_held_state` at 21 on it holds room 21.000; (c) every single-zone, unvalved and `slab_fed_direct` path bitwise unchanged; (d) on a two-zone valve-fed install `flow_target_for_indoor` equals the plant's `_valve_flow_set` at wind 0 and precipitation 0, on `replay_install` and on one with `upper_floor_area_ratio` 0.3 and `radiator_power_fraction` 0.7; (e) the reference digest moves only on the two-zone valve-fed install.

## Alternatives, and why each lost

- **The series term alone** (the issue's literal reading): room 21.240/21.196/21.153 (spike), above target, and the harness's precondition fails (exit 1): the free heat the single-zone branch counts is uncounted.
- **Conductance sum with free heat** (a + b, Uu + Ul, G): room 20.936/20.893/20.849 (spike), short by up to 0.151 K and growing with the outdoor delta, so (a) fails; it is the law's c → ∞ limit and needs the same inputs less two.
- **Hold the lower floor, the slab's zone, at target**: the upper floor runs above it by the split, so the room exceeds the thermostat's target and the booked reference holds a room its own `_thermostat_held_state` refuses.
- **A curve per circuit**: the plant has one valve and one flow; it changes topology, not the curve.

## Sibling sites

`git grep -n -e "flow_setpoint(" -e "_valve_flow_set(" -e "_valve_ua(" -e "flow_target_for_indoor(" -e "slab_fed_direct" -- custom_components`. Covered: the four sites above. Unchanged by construction: the single-zone sites (R11-VALVE-REFERENCE's), `flow_lift.py` and `sysid.py` (readers). Out of scope: `slab_fed_direct`'s curve still spreads loss over both circuits while only the radiators see it; no finding names it (Notes).

## Evidence plan

- **Failing tests first**, `tests/features.py`, after the R11-VALVE-REFERENCE reference-digest block, on production symbols: (a) and (b) fail at this base (room 20.719/20.350/19.980); (c) as `==` against literals recorded at this base for `direct_flow_carnot`'s configuration and a `slab_fed_direct` copy of `replay_install`, passing at both ends; (d) passes at both ends and fails if one side moves.
- **Finder's harness, both ends**: `r10_sav_held_install.py` `install` rows as above (spike); every other row identical (spike, `diff`). `r10_advisor_steady_seams.py` `fields`: all four arms identical (spike), its two-zone valve two-tank fixture holding 21.01 at both.
- **Null control**: `valve off` rows and `valve_upper_direct_slab` identical at head; the harness at base against head differs in `install` lines only.
- **Goldens that move**, claimed in `tests/golden/claimed_drift.txt`, never re-recorded; direction (spike, mean of each trajectory, base → head): `valve_storage` room +0.198 K, cost 43.245 → 41.120; `valve_storage_low_target` room +0.373, cost 43.605 → 43.683; `valve_storage_flat_prices` room −0.035, cost 89.785 → 89.298; `valve_storage_small_tank` room +0.157, cost 55.335 → 52.005; `valve_storage_smart_write` room +0.498, cost 42.023 → 41.713; `wood_two_tank` room +0.001, cost 32.652 → 31.165; `wood_two_tank_smart_write` room +0.469, cost 28.466 → 31.863; `wood_coil` room +0.177, cost 38.938 → 39.204. Identical: `valve_upper_direct_slab`, `winter_two_zone_no_dhw`, `shoulder_two_zone`, `direct_flow_carnot`; `coord_*` and `config_flow` set no valve.
- **Reference digest**: the `install +5` and `install -15` literals move (spike: `b7300f2dfadef8eb`, `c94024cf8a5fa259`); the four others reproduce at base and head. Commit order, one branch: the first commit adds (a) to (d), (a) and (b) red, (c) and (d) green; the second changes the law, claims the eight goldens, re-records the two install digests and bumps `REFERENCE_BASIS` with the `_SB_NOW == 4` literal and its stamp beside it. No pinned grader registers anything.
- **Mutation proof**: b → ua_floor (killed by a, b); wu/wl → equal weights (conductance sum, killed by a); free heat dropped (killed by a, b); the `slab_fed_direct` gate dropped (killed by c and `valve_upper_direct_slab`); the lower-loss keyword dropped at each call site (killed by a at the scalar and batch arms); `flow_target_for_indoor`'s branch (killed by d).

## Hot files, serial position, carries

Hot files: `custom_components/heatpump_optimizer/thermal_model.py`, `custom_components/heatpump_optimizer/ledger.py`, `tests/features.py`, `tests/golden/claimed_drift.txt`. The roster names `mixing_valve.py` and `thermal_model.py`; this shape leaves `mixing_valve.py` untouched and adds `ledger.py`, which the orchestrator checks against open groups at dispatch. After: none. Receives R11-VALVE-REFERENCE carry 3 (item 2c38f69d, issue 3713); owes none.

## Notes for the fixer

- The owner's install is the only committed bundle with a two-zone valve-fed slab (`tests/replay/owner-2026-10-30-away.json`); the law is closed-form on any parameters, so (d)'s second configuration covers a split the bundle does not. Carry: R11-SEAM-two-zone-slab (item s1)
- `slab_fed_direct` installs keep a curve over both circuits while only the radiator circuit is capped by it; measure its upper-floor miss on `valve_upper_direct_slab`'s configuration and route it by the sibling-seam rule if it misses. Carry: R11-SEAM-two-zone-slab (item s2)
- The law uses `slab_heat_transfer_floored`; `_two_zone_rates` integrates `slab_heat_transfer`. They differ only below the floor; pin (a) at the default and say so. Carry: R11-SEAM-two-zone-slab (item s3)
- With a learned gains profile the curve uses the constant `internal_gains`, as the single-zone branch does; R11-VALVE-REFERENCE's item s3 measures that residual for both branches. Carry: R11-SEAM-two-zone-slab (item s4)
- The flow-kind valve write on a two-zone `smart_write` install commands the new curve; the lower floor then reads below target by the split (0.30 to 0.70 K on the install, spike), which a user sees on that floor's sensor. Carry: R11-SEAM-two-zone-slab (item s5)
