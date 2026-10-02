Fix review: blocked e964fb7871aa5a2c188f47ba9262d2d366db7bb8 mutation: the floor properties' CLAMP_DROP survivors are a coverage loss this diff causes; 4 base pins that killed those floors were deleted and their replacements survive

Round 1. PR #1808, head e964fb78 = code head 12269398 merged into f94025bf (main 787fe137).

BLOCKING
- At base 404a5fb0 tests/features.py killed the CLAMP_DROP of max(p.cop_nominal, 1.0) and max(p.emitter_design_delta_t, 1.0) (ledger pins sysid _held_state 36d89191, thermal_model _stability_substeps 2356eace/ccd6440c). They were kills by inconsistency: one site lost its floor, the R8-P5c held-state fixed-point check (features.py ~54430) saw _held_state and simulate_step disagree. The diff moved every site into one property, so a floor drop now moves all sites together and that consistency check cannot see it. The diff deleted those pins as stale.
- Reproduced at code head 12269398: return (self.cop_nominal) in cop_nominal_floored -> features.py ALL 3638 PASSED rc 0; same for emitter_design_delta_t_floored. Mutant diffs and tails here.
- Nothing pins any floor's value (COP 0.6 behaves as 1.0, etc). The mutation ratchet does not refuse (3545 unpinned vs 3564 at base), so mutation-autofix will never act; ci-autofix.md forbids automated survivor triage. Survivors are not equivalent mutants.
- Ask: one value check per floor property (cop_nominal_floored, emitter_design_delta_t_floored, slab_heat_transfer_floored, flow_lift_power_floor_kw) on a sub-floor input, plus a check or a written survivor_triage with measured reason for each of the other 4 (ambient clamps at optimizer _dhw_window_floors, _buffer_charge_ceiling.net, coordinator ~3164; _utc_step_starts naive-start guard). Then --pin-killed so all 19 new sites carry a disposition.

VERIFIED OK
- No resume files in code-head ancestry; transport commit above the code head.
- Finder p3_floors.py (79aa98ec, sha1 8b9fd95e): base seam 22 / raw-divisor 6 / capacity 1; head 21 / 5 / 0. Only dhw_tank_thermal_mass closed. slab_heat_transfer still listed as a finder seam group at head (barrier arm (a) reads it as one owner); note only.
- Barrier mutants (in-memory, R9-P3 block only): raw slab floor in optimizer, max() floor in _power_fraction, raw on-threshold in _observe_compressor_start: each fails its named check; restored passes 7/7.
- features.py full at 8c7be89d: 3638 passed. structure.py PASSED at code head and at f94025bf. brief_lint rc 0.
- dst_checks at f94025bf: 82/82 with HASTUB_TZ=Europe/Stockholm (6 tz checks fail without it, same at base: environment).
- Merge delta: merge-tree(787fe137, 8c7be89d) tree == f94025bf tree; e964fb78 per coordinator equals merge-tree(12269398, 787fe137). dst_checks carries F10.1c arms plus this diff's timedelta clock; bugclasses.json P3 entry only.
- F6.4 (#1806): merge-tree with #1808 clean, no conflict on coordinator.py.
- Real-HA ha_contract (Mac, f94025bf): 61/61, 22/22 probes.

NOT VERIFIED
- comment_numbers.py (finder, sha1 e058d3ba) crashes at base and head (float('any') at line 96: harness/tree mismatch), so D5-s2-02 is not re-derived with the finder harness; fixer evidence only.
- CI at e964fb78: typing, briefs, policy-docs, env-matrix, browser, hassfest green; fast, mutation, coverage, closures still running at 11:31Z.
