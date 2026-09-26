# Round 9 verify, lens V1 (reproduce), D2 leads unit

Tree: handoff/audit-r9-evidence 96b89163 (baseline 1936d5ca plus round-9 evidence incl. leads). Box G3-V1, CPython 3.14.0rc2, numpy 2.4.6, OpenBLAS 1 thread. Finder harnesses re-run with their documented flags; no verifier harness written; perturbations in memory.

## D2-s1-51 — DHW sweep priced at 5.0degC default without outdoor thermometer
Rerun (`dhw_sweep_outdoor.py`, count metric, load1=0.14, thread_factor=1.000): `off_total_cold=14 of 14`, worst_rel_err 0.527 (F=-15) and 0.265 (F=-5) — bit-exact match to the finding. Null control (F=+5, forecast equals default) reproduced `off=0 of 7`. Perturbation (`--forecast`, sweep priced at `forecast_outdoor_now`): `off_total_cold=0 of 14` (load1=0.21) — moves fully in the stated `to_zero` direction, matching `observed_value=0`.
Attacks: count metric is contention-immune; null control passes; production path (`coordinator._update_current_state` / `_dhw_setpoint_sweep`) is reachable in real HA, no `FakeHass` executor dependency in the seam measured.
Vote: verify, severity low (unchanged — recommended setpoint is unchanged, only the published `cost_per_day` is wrong).

## D2-s2-81 — Two-zone comfort penalty halves each zone's floor price
Rerun (`l4_zone_floor.py`, degree-steps count metric, exact-on-build tolerance, load1=1.74, thread_factor=1.000): `two_zone_floor_deg_steps_sum=2.4672`, max=1.3144, drop-best=0.1048 — bit-exact match to the finding's value and leave-one-out. Null controls reproduced bit-exact: `single_zone_floor_deg_steps_sum=0.1471`, `two_zone_flat_sum=0.0000`. Perturbation (`_COMFORT_FLOOR_L1` 2.0->4.0 in memory, load1=1.86): `two_zone_priced_sum=0.8573` vs the finding's recorded `observed_value=0.8574` (delta 0.0001, within the stated tolerance).
Attacks: contention-immune per finder's own note, confirmed by bit-exact reproduction at different load; null controls pass; leave-one-out over 12 cells rules out a single-cell artefact; instrumented seam (`_comfort_terms`/`_comfort_terms_batch`) is pure production math on the shipped trajectory, reachable in real HA.
Vote: verify, severity medium (unchanged).

## D2-s4-81 — sysid refuses/aborts its own exact noise-free fit on 43 of 80 presets
Rerun (`l4_sysid_null_refusal.py`, count metric, exact tolerance, load1=1.79, thread_factor=1.000): `null_refused=19 of 80`, `null_admitted=37`, `null_aborted=24`, `unarmed=0` — bit-exact match. Refusals spread across 3 of 4 structure types (timber_crawlspace 8, timber_slab 4, concrete_slab 5, masonry 2), ruling out a single-structure artefact; leave-one-out (19-1=18) matches the finding's recorded `drop_most_favourable=18`. Perturbation (`UA_ADOPTION_HALFWIDTH_BAR` ln(1.10)->ln(1.20) in memory, load1=1.70): `null_refused=2` — bit-exact match to `observed_value=2`.
Attacks: count metric, contention-immune, confirmed at different load; null control (`null_admitted=37 of 80`) passes, showing the gate can and does admit; production seam (`SystemIdentification.arm/step/_finish`, `adoption_decision`) has no test-stub dependency.
Vote: verify, severity medium (43 of 80 presets — most structure/era/emitter combinations — cannot adopt their own exact answer; a real usability defect, not inflated).
