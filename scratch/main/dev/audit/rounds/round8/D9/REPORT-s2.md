# D9 seat s2: loop-thread work, retained bytes, payload bytes and the stress gate's 2x detection

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. The machine is a 4-vCPU shared cloud container (load1 7-25 during the runs). Threads were pinned to 1. Every ms and RSS figure is provisional. Counts, bytes and ratios are final.

## Method

- `s2_cycle.py` drives the real `HeatPumpOptimizerCoordinator._async_update_data` on a real asyncio loop.
  - The executor is a real `ThreadPoolExecutor`, and the solve goes over the production process-worker route.
  - The clock is frozen and advanced 15 min per cycle. Only the three network fetches are stubbed; the inputs are pre-seeded for 10 days.
  - It measures loop-thread `thread_time` per cycle as a ratio to `stress.reference_solve`.
  - It measures the tracemalloc slope, and deep `getsizeof` of every coordinator attribute, at warm-up, at the midpoint and at the end.
  - It measures `ru_maxrss` in fresh children after 16 and after N cycles.
  - It measures entity attribute JSON bytes over all PLATFORMS, split by `_unrecorded_attributes`, and the pickle bytes of the worker job and reply.
- `s2_stress_2x.py` runs `tests/stress.py` under the gate lease. A private `sitecustomize` makes `HeatPumpOptimizer.optimize` run twice, but only in processes that load this tree's `optimizer.py`. The HEAD^1 baseline capture resets `PYTHONPATH` and so stays uninjected, which makes it the in-run null arm. No production file is edited.
- `s2_gate_blind.py` counts the budgeted gate scripts (those with an elapsed-CPU or memory instrument) whose measured closure contains each cycle-path file.

Raw outputs are in `s2_evidence/`.

## Findings

**D9-s2-01 (medium, bug, instrument): no budgeted gate reaches the coordinator cycle.**
- `stress.py` is the only script that budgets CPU or memory. Its measured closure contains none of these files: `coordinator.py`, `sensor.py`, `process_worker.py`, `price_model.py`, `narrative.py`. The count for each is 0. The positive control, `optimizer.py`, gives 1.
- For a change to `coordinator.py`, `closure.py select` prints `SKIP tests/stress.py`.
- Injecting a second `_build_data_dict` per cycle moved loop CPU per cycle from 0.257 to 0.363 reference solves (+41 %). Nothing in the gate can see that increase. The same blindness covers retained memory across cycles and payload bytes.
- Perturbation: adding `coordinator.py` to stress's closure (the fix shape) moves the count from 0 to 1.
- The proposed fix is a cycle arm with ratio budgets. `s2_cycle.py` is a starting point.

## Non-findings, with numbers

- **Stress gate against a 2x regression:** it detects the regression. rc=1 and 4 of 83 checks fail:
  - evaluation count at 2.00x
  - simulate count at 2.00x
  - sweep ratio at 210.62x against a budget of 134.32x
  - per-scenario ceiling at 1678x against 1630x

  All 51 scenarios had unchanged plans against the in-run HEAD^1 baseline.
- **Loop-thread work:** 0.26-0.31 of a reference solve per cycle under contention, and about 9-12 ms per cycle uncontended. Components timed alone: `_build_data_dict` 2.3 ms, `_forecast_arrays` 1.3 ms, all 74 entities' state and attributes 4.4 ms.
  - Pi extrapolation assumes a Pi 4 core is 3-4x slower than this vCPU. That is an assumption, not a measurement. On it, the cycle costs about 30-50 ms of loop work per 15 min.
- **Retained bytes are bounded:**
  - traced slope 1654 B/cycle in the first half and 1161 B/cycle in the second half, over 112 cycles
  - `_accuracy` is the only attribute that grows, capped at 672 samples plus 512 pending entries
  - `ru_maxrss` is 102984 kB after both 16 and 112 cycles
  - Perturbation: `HISTORY_LENGTH=20` lowers the second-half slope to 729 B/cycle.
- **Payload:**
  - recorded attributes are 8174 B/cycle across 74 entities; the largest set is 773 B, well under the recorder's 16384 B cap
  - 79030 B/cycle are excluded by `_unrecorded_attributes`
  - the data dict is 75.8 kB and is not recorded
- **Worker transport:** 13.0 kB job and 16.7 kB reply per solve, at 1.3 ms or less of parent CPU.
- **Memory pass:** it probes 6 of 51 scenarios, a trade `stress.py` states itself. On this box all 6 probes read at the 100.4 MiB import floor, so the attributable-RSS arm says nothing here. This is a lead, not a finding: I injected no RSS-only regression.

## Unfinished

- I did not run the full uninjected stress null. The in-run baseline served as the null arm for the work channels.
- The finding id uses the task's `D9-s2-NN` form, which does not match the schema's `^D9-NN$` pattern.

## Exposure

None.
