Evidence tree for this unit: handoff/audit-r9-evidence at 96b89163 (the finders' leads harnesses live there, not on this branch). Box G2-V2, verifier V2.

# D8-s3-61 verify-v2 (leads unit)

Finder harness re-run: `tools/audit/round9/D8/leads/l2_d8_leads.py --only D` at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, this box (4-vCPU Linux container, /home/claude/venv CPython 3.14.0rc2). Baseline: `valve_value_but_default_off=5` count (exact match to the finding), `valve_unknown_available_no_valve=5`. load1=2.20, thread_factor=1.000. `--perturb valve`: `valve_value_but_default_off=0` (exact match to expected_direction=to_zero, observed_value=0).

Own harness (V2, independent instrument): `tools/audit/round9/D8/verify-v2-leads/v2_valve_default.py`. Metric: topologies (of 5) x mixing_valve modes (none, manual, smart_read, smart_write) where `ValveTargetRecommendationSensor.native_value` is not None while `entity_registry_enabled_default` (read off the class/instance, never the payload) is False. Widens the finder's two-arm check (no_valve / manual) to all four modes. Result: `value_but_default_off=15` (manual, smart_read, smart_write x 5 topologies each), `value_and_default_on=0`, `no_value_default_off_ok=5` (the no-valve cells, where an off default while unknown is the class's documented, non-buggy behaviour). load1=1.61, thread_factor=1.000. `--perturb` (gating the default on `mixing_valve.is_throttling`): every throttling-mode cell flips to `enabled_default=True` (confirmed for coord_minimal/coord_dhw/coord_two_zone before the run was stopped once the pattern was established across all three topologies checked; the un-perturbed run above already covers all 5 x 4).

Source check: `custom_components/heatpump_optimizer/sensor.py:2122` -- `_attr_entity_registry_enabled_default = False` is a plain class attribute on `ValveTargetRecommendationSensor`, never overridden as a property, so it cannot vary with `mixing_valve_mode`; matches the finder's `mechanism`.

Attacks (verifier.md step 3):
- Contention: load1 quoted above (1.61-2.20), thread_factor 1.000 both runs -- not gated, per `tools/audit/README.md`.
- Gate mode: not applicable; no golden/env_drift path is touched.
- Grid artefact: not an aggregate mean; every cell is printed and counted individually (`# D ...` lines).
- Null control: the finding is about a static registry default, not cost/gain/time, so COMMON.md's null-control requirement does not bind; none is missing.
- Reachability: `entity_registry_enabled_default` and `native_value` are read through the ordinary HA entity path (`async_setup_entry`, no `FakeHass`-only shortcut) -- reachable in real HA.
- Severity: my widened count (15 cells across 3 modes, not just manual) does not change the user-facing consequence -- still an extra "enable in the entity list" step for a diagnostic sensor. Kept at the finder's `low`.

Vote: **verify**, severity `low`.
