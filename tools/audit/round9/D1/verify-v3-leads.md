# D1 verify, lens V3 (reach and class), unit leads, box G1-V3

Evidence tree 96b89163 (baseline 1936d5ca). Harnesses are in `tools/audit/round9/D1/verify-v3-leads/`, with the shared rig `_realha_rig.py`.

Real-HA runs used `/root/venvha/bin/python` with Home Assistant 2026.2.3, `PYTHONPATH=custom_components[:tests]`, no tests/hastub, and the `typing.ByteString = bytes` shim for mashumaro on 3.14.0rc2. Stub-side comparisons used `PYTHONPATH=tests/hastub`. Every finder harness was also re-run in the first pass and matched exactly (load1 2.4-2.85). The own-harness pass ran at load1 0.06-0.45. All numbers are counts.

## Rig note for later V3 seats

A bare `homeassistant.core.HomeAssistant()` boots enough to host the real `HeatPumpOptimizerCoordinator`: a real StateMachine, a real executor, the real DataUpdateCoordinator base, real Store loads, and eager tasks.

- `hass.config_entries` stays None without bootstrap, so a service handler needs `async_entries` and `async_get_entry` supplied by hand.
- `StateMachine.async_set` stamps from `time.time()`, not from `dt_util`. Pass `timestamp=` explicitly, or construct the `State` directly.

## D1-s1-51: hastub Store decodes with stdlib json
- **Measurement:** `D1-s1-51_realha_store_codec.py`, real Store with disk and orjson against the stub.
  - Real HA: the healthy sibling is kept in 1 of 6 cases, and the whole store is lost in 5 of 6 (nan, inf, -inf, 1e400, 10**400 load as None; 2**64 loses precision).
  - Stub: kept 6 of 6, lost 0 of 6.
  - The two diverge on 6 of 6.
- **Null control:** the control document loads identically under both.
- **ha_contract.py:** the Store disposition claims parity only for write-time errors. This load-time divergence is undeclared.
- **Class:** P11. **Seam rule:** all. **Severity:** low.
- **Vote:** verify.

## D1-s1-52: hastub dt_util.now() is naive by default
- **Measurement:** `D1-s1-52_realha_naive_clock.py`, 3 production seams, each given an aware and a naive stored stamp.
  - Real HA (now() is aware): aware stamps raise 0/3, naive stamps raise 3/3.
  - Stub: aware 3/3, naive 0/3, exactly inverted.
  - The two diverge on 6 of 6.
- **ha_contract.py:** the `now()` contract is gated on `DEFAULT_TIME_ZONE is not None`, so it passes vacuously on the stub. The divergence itself is declared (#577); the consequence on these 3 seams is new.
- **Class:** P11. **Seam rule:** partial. **Severity:** low.
- **Vote:** verify.

## D1-s2-51: unfenced learner and arbiter calls on the cycle path
- **Measurement:** real coordinator on real HA.
  - A quiet-period fault fails the solve in 3/3 cycles, and the plan is still published 3/3.
  - An arbiter fault fails 3/3 cycles and skips 15/15 sibling steps.
  - Both are identical to the stub.
- **Mechanism:** `_apply_action()` and `_record_quiet_comfort_period()` are outside any try block, while their siblings are each fenced.
- **Class:** corrected from new to **P2**. **Severity:** medium. **Seam rule:** all.
- **Vote:** verify.

## D1-s2-52: store writers do not wait for the startup read
- **Measurement:** real HA, a real Store on disk, real eager tasks, and a second `HomeAssistant()` as the restart.
  - 5 of 5 stores lost their persisted state: energy 1234.5 → 0.0, ledger 77 → None, thermal 1.3 → 1.0, price dates → [], accuracy 7.5 → 5.0.
  - The guarded `async_set_mode` arm lost 0 of 1.
- **Class:** corrected from new to **P2**. `async_set_mode` alone waits for the startup read; the other five writers do not.
- **Severity:** I would give **high**, raised from medium. This is executed data loss of persisted learned and energy state on a restart race. It stays below critical because the state re-accumulates and the window is timing-dependent.
- **Vote:** verify (with the raised severity). **Seam rule:** all.

## D1-s2-53: set_thermal_parameters lost at restart
- **Measurement:** two real coordinators over one on-disk config directory.
  - 19 fields of a 20-field subset changed; 17 of those were lost.
  - The survivors are `dhw_cooling_rate` and `buffer_cooling_rate`, the same two the finder found.
- **Severity:** medium (the workaround is to re-issue after restart). **Class:** new. **Seam rule:** all.
- **Vote:** verify.

## D1-s2-54: manual-plan expires_at past the horizon
- **Measurement:** the real `handle_apply_manual_plan`.
  - With expires_at at +48 h: 0/96 free steps at apply and 0/96 at +23 h.
  - With the default expiry: 16/96 at apply and 96/96 at +23 h.
- **Severity:** low. **Class:** new (a missing upper-bound clamp). **Seam rule:** all.
- **Vote:** verify.

## D1-s2-55: Popen OSError skips the in-process fallback
- **Measurement:** real coordinator, with `Popen` raising `OSError(EAGAIN)`.
  - 0/3 cycles planned, 0 fallback notices.
  - The traceback shows `_ensure_worker()` runs before the try block that translates the error.
- **Severity:** medium. **Class:** new. **Seam rule:** all.
- **Vote:** verify.

## D1-s5-51: silent report-on-change thermometer turns Indoor Temperature unavailable
- **Measurement:** a genuine `State` through the real InputReader into the real IndoorTempSensor.
  - Unavailable at 4 of 7 ages: 61, 90, 240 and 480 min.
  - The re-report arm is unavailable in 0 of 1.
- **Severity:** medium. A workaround exists (`staleness_max_age_scale`), and there is no field data on report intervals. **Class:** new. **Seam rule:** all.
- **Vote:** verify.

## D1-s5-52: -127 and 85 °C sentinels delivered as ok
- **Measurement:**
  - InputReader: 12 of 12 sentinel cells are delivered as ok.
  - Full real cycle with a genuine -127 `State`: IndoorTempSensor is available with native_value -127.0, and DHWTemperatureSensor is available with native_value -127.0. The 85 arm behaves the same.
  - Control: 21.3 °C is delivered in 6 of 6 cases.
- **Class:** corrected from new to **P2**. `_dhw_inlet_c` carries a -5..35 guard; the other temperature paths do not.
- **Severity:** I would give **high**, raised from medium. It is a wrong published value with no user workaround.
- **Vote:** verify (with the raised severity). **Seam rule:** all.
- **Same mechanism as:** D1-s1-03 and D1-s2-02 in unit D1-1 (an input with no plausibility bound).

## D1-s2-71: hastub DataUpdateCoordinator drops update_interval
- **Measurement:** on real HA, `update_interval` matches in 4 of 4 intervals. On the stub it is readable in 0 of 4.
- **ha_contract.py:** `absent=(...)` names only the scheduler internals, not `update_interval`.
- **Class:** P11. **Seam rule:** demonstrated-only. **Severity:** low.
- **Vote:** verify.
