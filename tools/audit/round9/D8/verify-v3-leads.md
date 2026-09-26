# D8 leads, verifier V3 (reach and class), round 9

Box G2-V3, lens V3 (reach and class), leads unit. Read at evidence 96b89163 (leads harnesses under `tools/audit/round9/<dim>/leads/`); own harnesses under `verify-v3/leads/` here. Real HA: core 2026.2.3 on CPython 3.14.0rc2, numpy/scipy from the gate venv; shims: stand-in `typing.ByteString` ABC before importing HA, `http` marked loaded.

## D8-s3-61 — Valve Target Recommendation ships disabled where a valve is set

**Step 1.** `l2_d8_leads.py --only D`: `valve_value_but_default_off=5`, `valve_unknown_available_no_valve=5`, thread_factor 1.000, load1 2.21. Exact.

**Step 2 / reach, real HA.** `realha_valve.py` registers through real `EntityPlatform.async_add_entities`:
- Manual (throttling) mixing valve: `real_registry_disabled_valve_manual=1`, `real_state_written_valve_manual=0`. Real HA (`entity_platform.py:904`) sets `disabled_by=integration` and never writes a state. The finder's "publishes 23.0 while disabled" (a direct `native_value` read on the stub) reaches a user only after they find and enable the entity by hand.
- Comparator `BufferTankTempSensor` (`ConfiguredInputMixin`, slot configured): `real_registry_disabled_ecl110_sibling=0`, state present.
- Perturbation (finder's fix shape, in memory): disabled 0, state written 1, value 23.0. thread_factor 1.002–1.003, load1 0.55–0.71.

**Attacks.** Contention: counts. Gate mode: n/a. Grid: 5/5 golden topologies. Null control: no-valve topologies 0 (available+unknown, as intended). Reachability: real and refined — the static-vs-config-following default mismatch is exactly what real HA's registration reads; the harm is "a useful diagnostic hidden by default for a user with a valve", not "a disabled entity leaks a value". The docstring's justification ("disabled rather than eternally-unknown") covers only the no-valve case.

**Severity:** low confirmed (discoverability of an opt-in diagnostic; no wrong control action).

**Seam rule.** `grep '_attr_entity_registry_enabled_default = False'` over sensor.py and binary_sensor.py: 11 hits (10 + 1). The only dynamic overrides are `ConfiguredInputMixin`/`DHWEntityMixin` in entity.py; no other platform file carries the attribute. **All** for the literal form; it also surfaces `DHWHeavyDaySensor` as a same-shape candidate (not voted here).

**Class:** P2 confirmed.

**Vote: verify, low.**
