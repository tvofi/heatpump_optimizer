# D8 verify-v1, leads unit (round 9, lens V1 reproduce), box G2-V1

Tree: /home/claude/wt/leads at evidence 96b89163. Finder's harness re-run unmodified from the repository root with PYTHONPATH=tests/hastub; perturbations in memory; no harness written.

## D8-s3-61 -- Valve Target Recommendation disabled-default vs available-but-unknown (vote: verify, low)
- Re-run: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D8/leads/l2_d8_leads.py --only D` -> `valve_value_but_default_off=5`, `valve_unknown_available_no_valve=5`. The finder's value is 5, so exact. load1=1.77, thread_factor=1.000.
- Perturbation `--perturb valve` (entity_registry_enabled_default follows mixing_valve.is_throttling(mode)): `valve_value_but_default_off=0`; `valve_unknown_available_no_valve` stays 5 (the perturbation targets only the manual-mode default). Finder's observed 0, direction to_zero.
- Null control: none required (a count, not cost/gain, COMMON.md item 5); the no_valve arm is the contrast and does not move under the perturbation.
- Leave-one-out: all 5 golden topologies show value=23.0 / enabled_default=False under mixing_valve_mode=manual; dropping any one cell leaves 4/4.
- Method attacks: exact count, contention-immune (load1 1.77-1.95); no gate mode or grid artefact; reach checked in source: `sensor.py:2106-2146` has a static `_attr_entity_registry_enabled_default = False` and no `available` override, reading `coordinator.data["valve_target_recommendation"]`, a production path, not a stub artefact.
- Metric (finder's): topologies (of 5) with mixing_valve_mode=manual where native_value is not None and entity_registry_enabled_default is False.
- Severity low: diagnostic-entity discoverability; no wrong money or comfort.
