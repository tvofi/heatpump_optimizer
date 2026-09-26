# Round 9 · D1 · verifier V1 (reproduce): leads unit (10 findings)

Box G1-V1, lens V1. Evidence tree: detached worktree of `origin/handoff/audit-r9-evidence` at `96b8916318513c3617254c3ce43b10570eb16307` (baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`). CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1, orjson 3.11.9, node v22.22.2. Machine: 4 vCPU cloud container, shared with two other sub-seats; load1 0.28–0.71, thread_factor 1.000 on every RESULT. Every number is an exact count, so contention does not bear on it. All perturbations were the harnesses' own in-memory arms; no on-disk edits, no new harnesses.

Tally: 10 verify, 0 weaken, 0 refute, 0 unresolved.

## D1-s1-51 — hastub Store decodes with stdlib json vs Home Assistant's orjson · VERIFY (low)
- **Re-run** (`stub_store_codec.py`): `divergent=6 of_6`, `healthy_sibling_lost_stub=0 healthy_sibling_lost_ha=5`, `control_divergent=0 of_1`. Exact match (load1 0.30, thread_factor 1.000).
- **Perturbation** (`--orjson`, the stub's decode swapped for HA's orjson-or-None): `divergent=0 of_6` (healthy_sibling_lost_stub becomes 5, matching HA). Moves to zero as claimed.
- **Attacks:** count metric, contention negligible; not a gate check; 6 named discrete cells, no aggregate; null control (healthy doc) 0 and passes. Scoped correctly as an instrument (test-double) defect, not a production path. Low is earned: it inflates stub-only findings elsewhere but harms no user by itself.
- **Metric:** of 6 stored documents (a healthy leaf plus one hostile number token each), the count whose `QuarantiningStore.async_load` payload differs between the stub's stdlib-json codec and HA's orjson decode-or-None codec.

## D1-s1-52 — hastub dt_util.now() is naive by default, inverting the naive/aware verdict · VERIFY (low)
- **Re-run** (`stub_naive_clock.py`): `stub_now_naive=1`; the stub raises on the aware-stored input (0/3 on naive), real-HA-now raises on the naive-stored input (0/3 on aware); `divergent=6 of_6` (load1 0.34).
- **Perturbation** (`HASTUB_TZ=UTC`): `stub_now_naive=0`, `divergent=0 of_6`, and the raise pattern flips to match HA's aware clock (raises on naive-stored 3/3, not on aware-stored 3/3). This arm is also the null control.
- **Attacks:** count metric; 3 seams × 2 storage tags, all shown individually, no aggregate. The seams (SnapshotRing.due, CurveLearner._step_down, ComfortLearner._decay) are named production symbols reached from real coordinator paths (see D1-s1-01, D1-s3-01). Low fits: an instrument defect that inverts a suite verdict, not a direct product bug.
- **Metric:** of 3 production seams × {aware, naive} stored stamps, the cells whose TypeError-raise verdict under the stub's default now() differs from the verdict under an aware now.

## D1-s2-51 — a best-effort subsystem raise on the cycle path fails the whole cycle · VERIFY (medium)
- **Re-run** (`cycle_fence.py`): quiet arm `quiet_calls=3`, `quiet_solve_failed=3 cycles_of_3`, `quiet_plan_published=3 cycles_of_3`, `quiet_solve_failures_counter=1`; arbiter arm `arbiter_cycles_failed=3 cycles_of_3`, `arbiter_skipped_steps=15 of_15`, all five sibling counters 0/3 reached. Exact match (load1 0.63).
- **Perturbation** (`--fence`, the seam wrapped in try/except like its siblings): both arms drop to 0; every sibling reached 3/3.
- **Null control** (`--no-inject`): identically 0/0 across both arms, the same as `--fence`, so the injected raise, not rig plumbing, drives the failure.
- **Attacks:** the tracebacks show the raise crossing real production frames (`coordinator.py:5096`, `:10454`, `:4653`, `:6676`) under `asyncio.run`, with no executor boundary involved, so this is not a FakeHass artefact. Medium is earned: a real producer exists (D1-s3-03), and the consequence (a false solve_failed, skipped actuation and saves) recovers next cycle.
- **Metric:** per arm over 3 cycles, cycles reported failed and sibling cycle steps not reached, with a raise injected in a best-effort subsystem on the cycle path.

## D1-s2-52 — five store writers do not wait for the startup read · VERIFY (medium)
- **Re-run** (`startup_clobber.py`): `lost=5 stores_of_5` (energy, ledger, thermal, price, accuracy), `mode_arm_lost=0 of_1`; detail 1234.5→0.0, 77.0→None, 1.3→1.0, ['2026-01-10','2026-01-11']→[], 7.5→5.0 (load1 0.65). Exact match.
- **Null control** (`--after-read`, writers run after the loads land): `lost=0 stores_of_5`. **Perturbation** (`--wait`, `async_save` awaits `async_wait_for_read` first): `lost=0 stores_of_5`.
- **Attacks:** the outcome is deterministic given eager-start task semantics, which the rig matches to real HA's `hass.async_create_task`; 5 named stores, each shown, the same missing wait in each. The one writer that already waits (`async_set_mode`) loses nothing, an internal control that isolates the mechanism. Medium fits: learned state lost on an unlucky restart timing.
- **Metric:** of 5 stores, the count whose persisted learned marker differs from the value held after every startup load has landed, when each store's writer runs during its load.

## D1-s2-53 — set_thermal_parameters changes are silently lost at restart (24 of 26 fields) · VERIFY (medium)
- **Re-run** (`runtime_params_restart.py`): `changed_fields=26 of_28` (radiator_power_fraction and dhw_windows leave no simple-typed footprint on this rig, as the finding says), `lost=24 of_changed`, `survived=dhw_cooling_rate,buffer_cooling_rate` (load1 0.53). Exact match.
- **Perturbation and null control** (`--persist`, the changed field written into entry.options before restart): `lost=0 of_changed`.
- **Attacks:** leave-one-out over the 24 lost fields leaves the same mechanism (nothing writes the non-cooling-rate fields to entry.options or a store; the two survivors go through the thermal-learning store). `async_update_thermal_params` is the real service-call path, run on a real asyncio loop with eager task starts. Medium is defensible (a silent revert; the workaround is re-issuing the call after each restart). There is a case for high, since the user gets no signal, but no evidence to override the recorded severity.
- **Metric:** of the set_thermal_parameters fields whose call changed coordinator state, the count whose changed footprint is absent after a restart with every store load landed.

## D1-s2-54 — apply_manual_plan accepts expires_at past the horizon · VERIFY (low)
- **Re-run** (`manual_plan_expiry.py`): `free_at_apply_48h=0, free_at_23h_48h=0`. Exact match. **Null control** (no expires_at, 20 h default): `free_at_apply=16, free_at_23h=96`. **Perturbation** (`--clamp`, expires_at capped at now+MANUAL_PLAN_WINDOW_HOURS in memory): `free_at_apply=16, free_at_23h=96`, up to the default arm exactly.
- **Code check:** `services.py:864-892` parses `raw_expires` with `dt_util.parse_datetime` and passes it to `build_override`, which refuses only a past expiry, an unparseable slot, an end at or before its start, or overlapping slots. There is no upper bound. `expires_at` is a free-text field (`services.yaml:455-457`), reachable from Developer Tools or any automation.
- **Attacks:** exact count; single scenario; null control matches; reachable in real HA. The finder's low severity stands, though a stricter reading is plausible: any date more than 20 h out silently turns the optimizer off for the whole span.

## D1-s2-55 — Popen OSError on worker spawn skips the in-process fallback · VERIFY (medium)
- **Re-run** (`worker_spawn.py`): default `planned=0 cycles_of_3, fallback_notice=0`; `--wrap` (OSError re-raised as ProcessWorkerUnavailable) `planned=3, fallback_notice=1`; `--no-inject` null control `planned=3, fallback_notice=0`. All exact.
- **Code check:** `coordinator.py:1091-1103`: `_run_in_process` calls `_ensure_worker()` at :1095, inside `_PROCESS_LOCK` but before the `try:` at :1099 that maps transport failures to `ProcessWorkerUnavailable`. `_await_optimize` (:1214-1230) catches only `ProcessWorkerUnavailable`, so the #511 degrade path is skipped; the default run's traceback shows the `BlockingIOError` propagating unmodified.
- **Attacks:** exact count; real production code through a monkeypatched `Popen`, not FakeHass-only; EAGAIN is a real errno on a loaded Pi-class host. Medium is reasonable.

## D1-s5-51 — a report-on-change indoor thermometer silent over 60 min goes unavailable · VERIFY (medium)
- **Re-run** (`indoor_silence.py`): `unavailable=4 of_7` (61/90/240/480 min unavailable; 5/30/59 available), `rereport_unavailable=0 of_1`. Exact. `--scale 8`: 0 of 7. `--no-watchdog`: 0 of 7.
- **Code check:** `inputs.py:594-629` (`_age_gate`) takes `last_reported or last_updated or last_changed` and marks stale only when age > limit; the re-report arm is fresh because `last_reported` is honoured (distinct from D1-s5-01's `age_of` seam).
- **Attacks:** leave-one-out: dropping the 480 min cell leaves 3 of 6 unavailable. Null control clean. Report-on-change Zigbee and BLE thermometers are an ordinary real pattern. Medium kept; arguably high, but the base rate of long silences is unmeasured here, as the finder says.

## D1-s5-52 — DS18B20 sentinel temperatures (-127, 85 °C) delivered as ok · VERIFY (medium)
- **Re-run** (`sentinel_temps.py`): `delivered_minus127=6 of_6, delivered_85=6 of_6, delivered_sentinels=12 of_12, control_21_3=6 of_6`. Exact. **Perturbation** (`--range`): `delivered_minus127=0, delivered_85=2, delivered_sentinels=2 of 12`, down as stated (85 °C survives on the two 0..100 windows, DHW and buffer tank, as the harness's own table implies).
- **Code check:** `inputs.py` has no per-key range check beyond `_finite`, `normalize_temperature_c` and `_age_gate`; the only physical-range check is `_dhw_inlet_c`'s single-consumer -5..35 clamp (`coordinator.py:1358`).
- **Attacks:** leave-one-out over the 12 cells leaves 10 of 11 delivered by default; null control clean; DS18B20 fault sentinels are documented real hardware behaviour. Medium is reasonable.

## D1-s2-71 — hastub DataUpdateCoordinator drops update_interval · VERIFY (low)
- **Re-run** (`l3_update_interval.py`): `unreadable_cells=4 of 4, matching_cells=0 of 4, null_control_kept_attrs_readable=4 of 4, undeclared_in_ha_contract=1` over intervals {5,15,30,60} min. Exact. `--perturb store`: `unreadable_cells=0, matching_cells=4 of 4`.
- **Code check:** `tests/hastub/homeassistant/helpers/update_coordinator.py:130-150` accepts `update_interval` and never assigns it. `tests/ha_contract.py:618-641`'s `absent=(...)` tuple for `DataUpdateCoordinator` does not list it, so the divergence is undeclared.
- **Test-gap mutation (step 4):** the one production call site is `coordinator.py:1830`; nothing in `tests/` or `custom_components/` outside the stub reads `.update_interval` back, so a wrong constant there goes uncaught. An instrument defect under COMMON.md. Low as recorded.
