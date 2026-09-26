# D9 round 9: verifier V2 (independent), box G3-V2

**Environment**
- Evidence tree `handoff/audit-r9-evidence` at 6f51db2c (baseline 1936d5ca plus evidence).
- x86_64, 4 cores, Linux container. CPython 3.14.0rc2, BLAS pinned to 1 thread before numpy.
- Seats D14 and D2 ran on the box concurrently; load1 0.88–3.0, quoted per number. `thread_factor` 0.9999–1.021 on every run.
- No production file was edited; every perturbation was in memory.
- Own harnesses: `tools/audit/round9/D9/verify-v2/` (shared plumbing `_v2.py`). Raw outputs: `verify-v2/out/` — `f_*.txt` finder re-runs, `v2_*.txt` own measurements. Every harness resolves from the repository root.
- `stress.py` sweeps ran only under `tests/gate_lock.py auto-lease --label g3v2-d9`, with 0 other stress processes each time. No mutation pool, no full gate.
- Machine-readable votes: `tools/audit/round9/verify/votes-G3-v2.json`.

**Tally:** 7 verify, 0 weaken, 0 refute, 0 unresolved.

## D9-s1-01 — per-row loop in `_comfort_terms_batch` — **verify, medium**
- **Finder re-run** (`s1/comfort_rowloop.py --only two_zone_dhw_winter`, load1 0.88, tf 1.001): share 0.3288 (finder 0.3206 ± 0.03); `--vectorize` 0.0403; 0 rows mismatched; plan sha e55e6b6677dbfdc9 both arms.
- **Own** (`v2_comfort_twin.py`, load1 2.99, tf 1.0001). Metric: 1 − median(twin solve thread CPU)/median(production solve thread CPU), interleaved A/B/A/B, no timer inside the hooked method.

| cell | saved fraction | prod-vs-prod spread |
|---|---|---|
| 2z winter | 0.2981 | 0.037 |
| 1z winter | 0.0959 | 0.054 |
| 2z flat (null) | 0.3304 | 0.021 |

  Plan sha and solver evals equal in every cell. Parity sweep: 0 bit mismatches over 31,680 values (n = 24..288 incl. above numpy's 128-element pairwise block; B = 1..193; aligned and offset views; both topologies).
- **Attacks:** ratio metric, null spread ≤ 5.4 % far below the effect; end-to-end saving agrees with the in-method share, so the in-method timer is not the source; flat prices: effect persists (structural, CPU only); x86_64 ulp concern probed at 48 h (n = 192), no mismatch; arm64 and other BLAS builds not tested — the proposed fix scope already demands that proof. Lower edge: single-zone end-to-end saving 0.096.
- **Vote:** verify, medium: bounded CPU cost with a bit-identical fix.

## D9-s1-02 — scalar f(x) every L-BFGS-B iterate — **verify, medium**
- **Finder re-run** (`--no-parity --only two_zone_dhw_winter`, load1 0.89–1.14, tf 1.002): share 0.1395 (finder 0.1505 ± 0.02); fused 0.0053; fused row-0 mismatches 0 of 501; plan sha equal.
- **Own** (`v2_scalar_fun.py`, load1 3.0, tf 1.0001). Metric: thread CPU of raw scalar-objective calls while scipy's `minimize` is on the stack, over the solve. Own fused arm written independently (jac=True, f from row 0 of the gradient batch).

| cell | share inside `minimize` | saved end to end |
|---|---|---|
| 2z winter | 0.1465 | 0.1404 |
| 1z shoulder | 0.1777 | 0.1543 |
| 1z fuse 3.68 kW | 0.1790 | 0.1407 |
| 2z flat (null) | 0.1480 | 0.1892 |

  Scoring and restart-score calls outside `minimize`: 0.0036–0.0055 of the solve. Scalar calls inside `minimize` 495 → 0 fused. nfev, plan sha and row-0 parity (0 mismatches) equal in all four cells.
- **Attacks:** metric scope (scoring negligible), contention (spread 0–4 %), flat null (persists), fix correctness (bitwise row 0).

## D9-s1-03 — sysid fit on the event loop — **verify, low**
- **Finder re-run** (`--cadence-min 15`, load1 1.14, tf 1.0): max `step()` 65.08 ms = 2.23× reference_solve (finder 2.46 ± 25 %); `--no-fit` 0.0×.
- **Own** (`v2_sysid_heartbeat.py`, load1 2.7–2.76, tf 1): real asyncio loop with a 1 ms heartbeat while a coroutine calls `step()` synchronously as the coordinator does.

| arm | longest heartbeat gap (median of 5 seeds) | vs reference wall | identify_slab thread CPU |
|---|---|---|---|
| 30-min cadence | 54.66 ms | 2.20× | 50.2 ms, 11 samples |
| 5-min cadence | 242.64 ms | 7.56× | 241.2 ms, 61 samples |
| stubbed fit | 1.50 ms | — | — |

- **Reach:** `coordinator.py:5079` calls synchronously inside `async def async_run_optimization`; production arms with a declared plant (`:10478`), so the slab fit is the path that runs. FakeHass trap avoided.
- **Severity:** only on a user-armed experiment, at most once per `min_days_between_runs`: low. Wall numbers provisional.

## D9-s1-04 — DHW min-run full-suffix re-simulation — **verify, low**
- **Finder re-run** (load1 1.58, tf 1.021), counts exact: 7758 → 4780 calls with early exit, plan sha f84a5fb7240e8b43 unchanged in 6 of 6 cells; flat 7954; 48 h 25,313.
- **Own** (`v2_minrun_waste.py`, load1 1.91, tf 1.001). Metric: fraction of min-run extend steps after a production-refused slot's first breach, read from production's own candidate and base arrays.

| cell | post-verdict fraction |
|---|---|
| 1z winter | 0.4437 |
| 1z summer | 0.4518 |
| 1z shoulder | 0.2834 |
| 2z winter | 0.4439 |
| flat (null) | 0.3672 |

  Min-run makes 0.70 of all the solve's DHW step calls (7758/11064). At 48 h: 8048 post-verdict steps, 2.46× the 24 h figure.
- **Correction to the claim's shares:** 0.2268 / 0.2331 / 0.2149 on 1z winter / extreme / summer, but **0.023 on 1z shoulder** (count 3526). "0.17–0.23 on four single-zone cells" holds on three; the title's "12–23 %" is cell-dependent.
- **Vote:** mechanism, counts and bit-identical fix verified. Low.

## D9-s2-01 — sensor_advisor recomputed per state write — **verify, low**
- **Finder re-run** (load1 2.03, tf 1.0005): 384 steps per read (exact), 2 advisor calls per read, 3.00 writes per cycle, advisor share of loop CPU 0.3248 (finder 0.3164).
- **Own** (`v2_advisor_read.py`, load1 1.61, tf 1): direct coordinator plus real `sensor.async_setup_entry`, no replay. 192 `simulate_step` and 1 `rank_sensor_advisor` per plan-sensor attribute evaluation (384 per read); every candidate configured: 0. Memoised on (config, power series): 0 steps, identical output, saves 0.8487 of the evaluation (1.172 → 0.177 ms). Rankings stable across 80 evaluations. Advisor 0.031× reference_solve per evaluation.
- **Writes per cycle:** 3, in code (`coordinator.py:4797`, `:5150`, plus the refresh's own).
- **Severity:** about 7 ms of loop CPU per cycle here: low.

## D9-s2-02 — no budgeted check sees a 2× of loop-thread work — **verify, medium**
- **Finder re-run** (load1 1.82, tf 1.0006): offenders none 0 / cpu 1 / loop2x 0 (exact); loop2x `cycle_cpu_ratio` 2.585 vs budget 3.576; `stress_cycle_functions` 0 of 139. `loop_over_none` 1.023 vs finder 1.164: per-interpreter ruler noise, conclusion unchanged.
- **Own test-gap lens** (`v2_replay_loop_mutation.py`, load1 1.04–1.45, tf 0.9999). Single-line **production** mutation in `custom_components/heatpump_optimizer/topology.py`: `_ADVISOR_REPLAY_STEPS: Final = 48` → 48·K.

| K | loop-thread work | cpu_ratio | offenders |
|---|---|---|---|
| 4 | ×1.454 | — | 0 |
| 16 | ×3.229 | 2.41 → 3.19 | 0 |
| 32 | ×5.589 | 2.68 → 3.549 | 0 |

  `tests/stress.py` reaches no cycle code. Positive control: replay's own `inject=cpu` fires.
- **Attack:** the finder's "×5 turns it red" is borderline on this box: ×5.59 still passed (3.549 < 3.576).
- **Vote:** verify, medium: the event-loop-share gate is blind up to about 5×.

## D9-s2-03 — stress.py misses a non-kernel 2× — **verify, medium**
- **Finder re-run** (under the lease, load1 1.00, tf 1.0000): `nonkernel2x_one@2.19` tripped_total 0 at victim_cpu_x 2.532 (budget_x 2.875); `@4` tripped_total 1 (cpu_per_scenario) at 3.076×; evals_x = sim_x = 1.
- **Own 1** (`v2_stress_headroom.py`, lease, load1 1, tf 1). Metric: per scenario, the lone CPU multiplier k_s that trips any CPU rule, from one clean sweep. **50 of 51** scenarios have k_s > 2.0 (k_min 1.805 winter_mild/2z/space, LOO min 2.048, median 3.131, max 4.137); the sweep rule alone needs ≥ 2.128×. Production-located injection on winter/2z/dhw (`_comfort_terms_batch` ×4): cpu_x 1.946, 0 rules tripped, counts 1.0000×, kernel 0.988×, plan unchanged; clean-vs-clean spread 0.9 %.
- **Own 2** (`v2_stress_1z_mutation.py`, lease, full sweeps). Single-line **production** mutation in `custom_components/heatpump_optimizer/optimizer.py`: wrap `HeatPumpOptimizer._comfort_terms_batch`'s single-zone loop in `for _rep in range(5):`.

| repeat | single-zone cpu_x (median, range) | sweep ratio | rules tripped | load1 |
|---|---|---|---|---|
| ×5 | 2.065 (1.379–2.574, LOO max 2.44) over 22 scenarios | 112.6 → 124.3, budget 134.32 | **0** | 1.1 |
| ×10 | 3.30 median | — | 9 | 1.76 |

- **Attacks:** the "confined to one scenario" framing is narrower than the gap — a two-zone-branch edit reaches 91 % of sweep CPU and would trip the sweep rule (modelled from executed rows: 217 > 134), while a single-zone edit (8.7 % of sweep CPU) passes, executed. The "contradicts the file" framing is overstated: `SCENARIO_BUDGET_FACTOR`'s comment already records a lone doubling is caught only at 3.0×, and the `SCENARIO_WORK_FACTOR` sentence cited is about the count channels.
- **Vote:** the measured blind spot holds and extends: verify, medium.
