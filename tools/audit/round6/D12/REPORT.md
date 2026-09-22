# D12 — Generalization — audit round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), export `/Users/timmalmstrom/audit-r6-baseline`. Interpreter system `python3` (3.11.5). Threads pinned before numpy; `thread_factor=1.0`, `load1` 8.5–13.4 (shared box), `cpu_seconds` provisional.

> Reconstructed by the orchestrator from the finder's inline return (the subagent report-file guard refused REPORT.md; 8 harnesses on disk).

## Finding

### D12-01 (medium, bug) — battery view publishes buffer/DHW stores at ThermalState constructor defaults on plants that do not model them

`battery.build()` guards the optional buffer/DHW stores with `state.<field> is not None` on non-Optional floats defaulting to 40.0/55.0 °C that no code path ever sets to `None` (`battery.py:333` buffer, `:320` DHW, against `thermal_model.py:1080/1085`). Both `is not None` conjuncts are provably invariant. Contrast the wood tank (`thermal_model.py:1109` made Optional) where the same sentinel works. Result: a 35 L buffer that `describe_setup()` reports as `is_store: false` is listed as a storage component, and the default-on `BATTERY`/`ENERGY_STORAGE` aggregate includes heat at a temperature nothing measured.

- instrumented symbol: `heatpump_optimizer.battery:build` (via `_build_data_dict` → `_battery_view()`).
- Evidence: `buffer_store.py` — `invented_buffer_stores=8 cells=8`; perturbation (store variant / probed) → `0`; `fabricated_store_kwh=13.32` → `0.0`; `null_control_repeat_identical=1`.
- `batt.py store_unprobed`: 750 L buffer store, no probe → `18.27 kWh stored / 44.37 kWh usable` = 34 % of the published 53.27 kWh at an unmeasured temperature.
- `sensors.py`: `thermal_battery_available=1` with `measured_components=["house"]` — the fabricated constants ride inside a default-on MEASUREMENT series; disclosure is only an attribute (`measured: false`).
- Context for the judge: `battery.py:186` `label_measured` decides to keep probe-less figures + add disclosure (#282); `sensor.py:193` sets the threshold to "at least one" store. Neither covers a buffer on an `is_store: false` plant. Same class as #1335 (per-store sensors fixed; the aggregate left).
- Fix scope: make the two fields Optional, or gate the components on `params.buffer_is_store` / `reading_ok`, and/or extend `_MeasuredStoreMixin.available`. Golden-bearing: 5 `tests/golden/coord_*.json` pin `data.battery`.

## Non-findings (11, each executed)

Full solve + `_build_data_dict` on every describable plant `cells=27 failed=0`; omit any of 21 optional slots `cells=21 failed=0`; construct + all six platform setups `cells=10 failed=0`; #1335 probe gating live (`available_probe_absent=0`); two-zone gate live; `dhw_enabled=false` omits `dhw_tank`; wood tank not fabricated (needs real probe); ECL110 not invented (topics `""`, DIAGNOSTIC, off by default); no compressor modulation for a fixed-speed pump; PV peak default 0.0 fabricates none.

## Not finished

`ecl110_last_payload` data-dict surface (entity layer mitigates); vendor prefill tables (needs a device-model corpus the export lacks). No timing/memory claim made.

## Harnesses

`buffer_store.py`, `sensors.py`, `fullcell.py`, `grid.py`, `probe.py`, `batt.py`, `dumpcell.py`, `dump.py`.
