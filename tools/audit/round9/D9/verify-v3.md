# Round 9 verify: box G3-V3, lens V3 (reach and class), dimension D9

- Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (worktree /home/claude/ev, branch handoff/audit-r9-evidence at 6f51db2c).
- Machine: x86_64, 4 vCPU Intel Xeon @ 2.10GHz, Linux container, CPython 3.14.0rc2, numpy/scipy at the CI pins, BLAS pinned to 1 thread.
- Date: 2026-09-26.
- Contention: two other sub-seats (D14, D2) shared the box. load1 is quoted beside every timing below and ranged 0.65 to 4.14. Every thread_factor was between 1.000 and 1.020. Counts are final. Timing and CPU-ratio numbers are provisional, and each is paired with a same-session null control.
- Harnesses: tools/audit/round9/D9/verify-v3/ (v3_*.py, with shared plumbing in _v3.py). Raw outputs, including the finder-harness re-runs, are in tools/audit/round9/D9/verify-v3/out/.
- Real Home Assistant: `homeassistant` is not installed in this venv. Reach is argued from the production call chain plus tests/ha_contract.py, which records `helpers.entity.Entity` as stubbed: the stub's async_write_ha_state records is_on and does NOT evaluate extra_state_attributes. `CoordinatorEntity` and the `DataUpdateCoordinator` refresh chain are recorded as faithful, and always_update defaults to True as upstream.
- Class ids come from tools/audit/bugclasses.json (P1-P11, I1-I5). None of them covers pure interpreter-cost recomputation, so I propose two new classes, each shared by several findings: "new: avoidable interpreter-bound recomputation in the solve" and "new: CPU work run inline on the event-loop thread".

---

## D9-s1-01: per-row loop in _comfort_terms_batch

- **Step 1 (finder harness, one cell):** comfort_rowloop.py --only two_zone_dhw_winter gave share 0.3218 (finder 0.3206, tolerance ±0.03). The --vectorize run gave 0.0369, with plan sha e55e6b6677dbfdc9 unchanged and 0 mismatched values over 501 calls. load1 0.65 / 2.62, thread_factor 1.001.
- **Step 2 (my method):** v3_s1_01_comfort.py.
  - Metric: removable_share = 1 - median solve thread CPU with an axis=1 twin I wrote myself / median solve thread CPU with production. The two arms are ABAB-interleaved in one process.
  - two_zone_dhw_winter: removable 0.3196 (4510.5 to 3068.8 ms).
  - single_zone_dhw_winter: 0.1475.
  - two_zone_dhw_flat: 0.3241.
  - Plan sha is equal in every arm. 0 bit mismatches over 501, 26 and 358 calls. load1 4.12, thread_factor 1.0003.
  - Null control (--twin-off, production in both arms): -0.0423 at load1 4.01. The removable share is not an artefact of the rig.
- **Attacks:**
  - Contention: the metric is a ratio with a same-session null control, and it holds at load1 4.1.
  - Gate mode: not applicable (not a golden or mutation claim).
  - Grid artefact: the finder's leave-one-out range was 0.13-0.32. Mine is 0.15 on single-zone and 0.32 on two-zone. It holds on the flat-price cell, so it is structural and not driven by price shape.
  - Bit-parity hazard in the docstring (19/51 re-planned on CI x86_64): a synthetic sweep over n = 20..200 and B in {1, 7, 96, 97}, on [:, 1:] views, gave 0 mismatches over 72,762 row values on this x86_64 box. The hazard is not reproduced here, but a CI runner with another SIMD dispatch is not excluded. The finding's fix scope already demands proof on both x86_64 and arm64 CI, and that is the correct scope.
- **Reach in real HA:** yes. optimize() runs in the process worker (coordinator._await_process); on fallback it runs in the executor. The code is pure numpy, with no stub symbol involved. The cost lands on the worker process, not on the event loop.
- **Severity:** medium, as claimed. It is a bounded CPU cost on every two-zone solve: about 1.4 s here, and the finder's assumed 4-6x factor puts it at 5-9 s per solve on a Pi. The plan is unchanged.
- **seam_rule:** `grep -n 'for b in range(n_rows)' optimizer.py` returns 1889, 1915 and 2164. It does NOT enumerate the phenomenon, which is O(B) numpy calls per batched term. It misses:
  - optimizer.py:819 (cycling_penalty batch, `for b in range(shape[0])`)
  - optimizer.py:2422 and 2442 (grid_only_cost / energy_cost list comprehensions over total_power rows)
  - tariff.py:957 (peak-cost batch)
  - A rule that enumerates all of them: `grep -nE 'for b in range\(' custom_components/heatpump_optimizer/*.py`.
- **Class:** class_guess "new" confirmed. No bugclasses.json class covers per-call dispatch cost. Proposed name: new: avoidable interpreter-bound recomputation in the solve.
- **Vote:** verify, medium. Value 0.3196.

## D9-s1-02: scalar f(x) beside the batched jac

- **Step 1:**
  - scalar_objective.py --no-parity --only two_zone_dhw_winter gave share 0.1504 (finder 0.1505, tolerance ±0.02). ms per scalar call over ms per batch row: 18.0. load1 2.31.
  - The --fused arm gave share 0.0053 with plan sha unchanged, 0 row-0 mismatches over 501 fused calls, and solve 4445 to 3866 ms. load1 2.37.
- **Step 2 (my method):** v3_s1_02_scalar.py.
  - Metric: CPU of real (memo-missing) scalar evaluations issued inside _scoped_minimize whose x equals the x0 of the very next _batch_fd_gradient, as a share of solve CPU. Net share subtracts one extra batch row per fused evaluation.
  - I had to route stress.SolverWork._wrapped through the hook, because SolverWork re-installs its own counter at om._scoped_minimize.
  - two_zone_dhw_winter: 495 of 507 scalar evaluations are fusable, share 0.1475, net 0.1393.
  - two_zone_dhw_shoulder: 0.1503 (net 0.1421).
  - single_zone_dhw_winter: 0.0764 (net 0.0733).
  - flat: 0.1505.
  - One scalar evaluation costs 18-25 batch rows. load1 3.44.
  - Perturbation --maxiter-scale 0.02: fusable evaluations 495 to 127 and gradients 501 to 131, share 0.133. The count follows the iterates.
- **Attacks:**
  - Contention: ratio metric, stable at load1 3.4.
  - Grid artefact: single-zone is lower at 0.07-0.09, consistent with the finder's minimum of 0.087.
  - Null control: flat prices give the same share, so the effect is structural.
  - Mechanism check: _multi_start_minimize passes `memoized` as fun and a jac that reads f0 from the same memo. scipy L-BFGS-B evaluates fun and then grad at every trial point, so each iterate pays one full scalar evaluation. 495/501 measured.
  - Parity risk: fusing requires batch row 0 to be bit-equal to the scalar objective, otherwise every gradient's f0 moves. The finder found 0 mismatches, but only on this architecture. The fix scope correctly names the CI proof.
- **Reach in real HA:** yes. Same worker-process solve path, no stub involvement. Off the loop.
- **Severity:** medium, as claimed (bounded CPU: about 0.6 s per two-zone solve here).
- **seam_rule:** `grep -n '_scoped_minimize(' optimizer.py` returns 494 (restart) and 635 (main): every scipy entry in the tree. A repo-wide grep for `minimize(` finds only these two, via _scoped_minimize. It enumerates the phenomenon's seams.
- **Class:** new, confirmed (same proposed class as s1-01).
- **Vote:** verify, medium. Value 0.1475.

## D9-s1-03: sysid fit inline on the event loop

- **Step 1:** sysid_loop.py --cadence-min 15 gave a max step() call of 76.6 ms, 2.08x reference_solve (finder 2.46x; -15%, inside ±25%). --no-fit gave 0.12 ms. load1 2.62, thread_factor 1.0.
- **Step 2 (my method):** v3_s1_03_sysid_loop.py.
  - A REAL asyncio loop with a 1 ms heartbeat task. A coroutine calls SystemIdentification.step() once per cadence with the production argument shape.
  - Metric: the maximum heartbeat gap, plus the finishing call's thread CPU over reference_solve (median of 5 seeds).

  | cadence | finishing call | heartbeat gap | samples |
  |---|---|---|---|
  | 30 min (default) | 1.33x ref (43.5 ms) | 44.7 ms | 11 |
  | 15 min | 2.41x ref | 82.8 ms | 21 |
  | 10 min (config minimum) | 3.61x ref | 120.1 ms | 31 |
  | 30 min, --no-fit null | 0.0x | 1.44 ms | 11 |

  load1 3.25-3.27. The stall is the fit and it scales with sample count.
- **Attacks:**
  - Contention: the gap is wall time and provisional, but it tracks thread CPU within 5%, and the null arm under the same load sits at the tick floor.
  - FakeHass trap: my harness uses a real loop, so it is not affected.
- **Reach in real HA:** yes, with conditions. _run_system_identification is called synchronously from async_run_optimization inside _async_update_data (coordinator.py:5079), which is the event loop in real HA. It is not an executor job and has no stub dependence. It is reached only when all of these hold:
  - CONF_SYSID_ENABLED is set (DEFAULT_SYSID_ENABLED = False);
  - the user arms the experiment (button / service);
  - a night qualifies.
  - It then fires at most once per 30 days (min_days_between_runs).
- **Correction:** the claim's 5-minute arm (228 ms) is outside the configurable range. CONF_OPTIMIZATION_INTERVAL is 10-120 min (config_flow.py:1669), and update_interval equals that interval. The reachable worst case is 10 min: 120 ms here, and the finder's assumed 4-6x factor puts it at about 0.5-0.7 s on a Pi.
- **Severity:** low, as claimed (opt-in, rare, sub-second).
- **seam_rule:** `grep -n '_sysid\.\(step\|arm\|identify\)' coordinator.py` returns 10478 (arm) and 10512 (step). That covers sysid's own entries only. The stated property ("no learner fit ... synchronously in a coordinator cycle") also covers the coordinator's other learners (_learn_measured_cop, _async_learn_house_heat_loss / _buffer_cooling / _lower_floor_loss / _price_shape), which the rule does not list. It does not enumerate.
- **Class:** class_guess P10 corrected. P10's mechanism is "a solve on a GIL-holding thread starves the event loop". Here the fit runs ON the loop thread itself, with no second thread. P10's detector idea (a real-loop heartbeat) does catch it: that is exactly my harness. Proposed class: new: CPU work run inline on the event-loop thread (shared with D9-s2-01). The judge may instead widen P10 to "event-loop starvation".
- **Vote:** verify, low. Value 1.33x reference_solve at the default cadence (3.61x at the 10-min minimum).

## D9-s1-04: DHW min-run repair simulates past the verdict

- **Step 1:** dhw_min_run.py reproduced the count exactly: min_run_dhw_step_calls 7758, 42 of 52 weak slots refused, plan f84a5fb7240e8b43. --early-exit gave 4780 with the plan unchanged. load1 2.68, thread_factor 1.02.
  - Share of solve per cell:

    | cell | share |
    |---|---|
    | single_zone winter | 0.236 |
    | single_zone winter_extreme | 0.239 |
    | single_zone summer | 0.169 |
    | single_zone shoulder | 0.0255 |
    | single_zone flat | 0.062 |
    | two_zone winter | 0.011 |

- **Step 2 (my method):** v3_s1_04_minrun.py.
  - Metric: steps simulated past each refused candidate's first ceiling breach. The breach is computed with production's own verdict rule applied to the arrays extend_dhw_temps returns. As in s1-02, I had to route stress.SolverWork._dhw_step_wrapped through the hook.
  - At 24 h:

    | cell | past-verdict steps | share of min-run steps |
    |---|---|---|
    | single_zone winter | 3272 | 0.4218 |
    | shoulder | 973 | 0.276 |
    | summer | 1890 | 0.432 |
    | two_zone winter | 2463 | 0.428 |
    | flat | 2780 | 0.35 |

    single_zone winter uses 7758 of the solve's 11064 simulate_dhw_step calls (exact match to the finder).
  - At 48 h: 8240 past-verdict steps of 25,313.
  - Consistency with the finder: 7758 - 4780 = 2978 saved by its 8-step chunked exit, and 3272 - 2978 = 294. That is about 7 overshoot steps x 42 refusals, so the two instruments agree.
- **Attacks:** counts are contention-immune. The early exit is bit-identical by construction: a refused slot's candidate array is discarded, and base is refreshed from the slot either way.
- **Correction (grid):** the claim's "0.17-0.23 of optimize() CPU on four single-zone cells" does not hold on the shoulder cell, which was 0.0255 in the finder's own re-run here. The title's "12-23% of a single-zone DHW solve" is true of winter and summer only. The count claim stands unchanged.
- **Reach in real HA:** yes. The solve runs in the worker process whenever DHW is configured. Pure computation, no stub.
- **Severity:** low, as claimed.
- **seam_rule:** `grep -n 'extend_dhw_temps(' optimizer.py` returns 5729, 5745 and 5907.
  - It over-includes 5907 (_plan_dhw_cheapest_first), which needs the full refreshed trajectory and is not an instance.
  - It misses same-property sites that go through simulate_dhw_only / _dhw_plan_temps: the legionella reach ramp (optimizer.py:4261, which simulates the whole horizon to use hot[0]) and _repair_dhw_floor's per-round full re-simulation to find breach[0].
  - It does not enumerate.
- **Class:** new, confirmed (the same proposed interpreter-recomputation class).
- **Vote:** verify, low. Value 3272 past-verdict steps (0.42 of the repair's 7758).

## D9-s2-01: sensor_advisor re-simulated on every plan-sensor write

- **Step 1:** loop_work.py gave loop_simulate_steps_per_read 384, advisor_calls_per_read 2, entity_writes_per_cycle 3 (all exact), and advisor_share_of_loop 0.342 (finder 0.316, inside ±25%). The null run with every candidate configured gave 0 steps and share 0.0010. load1 3.54, thread_factor 1.0005.
- **Step 2 (my method):** v3_s2_01_advisor.py.
  - Metric: direct topology.rank_sensor_advisor calls on real integration configs.

  | config | steps per call | priced lanes | CPU per call | per cycle (x2 sensors x3 writes) |
  |---|---|---|---|---|
  | golden base config, no indoor entity | 288 | 3 | 1.70 ms | 10.2 ms, 0.315x ref |
  | indoor + outdoor configured | 192 | 2 | 1.16 ms | 6.9 ms |
  | all candidates configured | 0 | 0 | 0 | 0 |

  - --steps 1 cuts steps by exactly 48x (288 to 6, 192 to 4).
  - load1 2.43.
- **Reach in real HA:** yes, and not only through the stub.
  - Both plan sensors (SpaceHeatingPlanSensor always; DHWHeatingPlanSensor when DHW is set) are enabled by default. Only MeasuredPowerSensor at sensor.py:1626 is disabled by default.
  - Upstream's async_write_ha_state evaluates extra_state_attributes on the loop at every write. The stub does NOT (ha_contract: helpers.entity.Entity is stubbed and records is_on), which is why both the finder and I call the property or the function directly.
  - Writes per cycle: coordinator.py:4797 (entry) plus 5150 (finally) in async_run_optimization, plus the refresh's own async_update_listeners. That makes 3, because always_update defaults to True and the coordinator's super().__init__ does not override it.
- **Severity:** low, as claimed. About 7-10 ms of loop CPU per 30-min cycle here, for a value that is constant within a cycle.
- **seam_rule:** loop_work.py hooks ThermalModel.simulate_step on the loop thread across a read of EVERY published entity, so it catches any entity property that simulates, not just the demonstrated one.
  - Limits: simulate_step only (not simulate_dhw_step / simulate_trajectory_batch), and one fixture config.
  - No other entity platform calls a simulate path today (grep of sensor/binary_sensor/number/select/switch/button/climate/water_heater).
  - It enumerates the current seams: true, with those limits.
- **Class:** class_guess "new" confirmed. Proposed name: CPU work run inline on the event-loop thread (shared with D9-s1-03). The per-write form (a per-cycle constant recomputed at every state write) is the distinguishing seam.
- **Vote:** verify, low. Value 192 simulate_step per call (384 per read of both sensors), 0.315x reference_solve per cycle on the base config.

## D9-s2-02: no budgeted check sees a 2x of loop-thread work

- **Step 1:** m2_loop_blind.py gave:
  - none.offenders 0 (cycle_cpu_ratio 2.5946)
  - cpu.offenders 1 (4.5913, the positive control)
  - loop2x.offenders 0 (3.0111, against a 3.576 budget)
  - loop_over_none 1.1605
  - stress_cycle_functions 0 of 139
  - Matches the finder: offender counts exact, ratios within ±10%. load1 4.14, thread_factor 1.0006.
- **Step 2 (my method):** v3_s2_02_reach.py.
  - (a) sys.setprofile over stress.build_case on three sweep shapes: 0 functions entered in coordinator.py, sensor.py and topology.py (exact), against 123 in optimizer.py and 48 in thermal_model.py.
  - (b) The smallest multiple of the loop-thread share that replay's own cost_offenders turns red on replay's own COST_BUDGETS, solved on the figures re-measured here (r0 2.5946, L 0.1605): k_min = 3.36x. A whole-cycle regression needs only 1.378x.
  - The perturbation L = 0.5 lowers k_min to 1.76.
  - replay.py runs only in the nightly `slow` job (run.sh:303-304; tests.yml:918).
- **Step 4 (test gap):** the finder's injection is a CPU spin, not a production line. The D9 brief's M2 method prescribes that injection. Any single-line edit in coordinator.py or sensor.py that doubles loop work is diluted in the same way. The file is coordinator.py/sensor.py and the check is in tests/replay.py, so the gap does not measure itself.
- **Reach in real HA:** the finding is about the instrument. The work it cannot see (update-loop CPU plus three entity writes per cycle) runs on the real loop, as established under D9-s2-01.
- **Severity:** medium, as claimed. A 2-3x loop regression could merge and blocks HA's loop on every cycle.
- **seam_rule:** it runs both budgeted checks that exist (replay COST_BUDGETS, whose only budgeted fixture is synthetic-dhw-only.json, and stress.py's reach) and prints what each covers. It enumerates.
- **Class:** class_guess "new" corrected to I1 (a guard or budget that stays green under the regression it exists to catch). Earlier D9 gate-blindness findings (R2 D9-02/04, R3 D9-02/04, R4 D9-06, R5 D9-05/07/08, R6 D9-02) are all I1.
- **Vote:** verify, medium. Value 0 offenders at loop 2x; k_min 3.36x.

## D9-s2-03: stress.py blind to a confined 2x outside the simulate seams

- **Step 1:** under the gate lease, `m2_nonkernel_2x.py --arms plain,nonkernel2x_one@2.19,nonkernel2x_one@4 --victim winter/2z/dhw` gave:
  - plain: tripped_total 0, sweep_ratio 121.19 against 134.32.
  - @2.19: tripped_total 0, victim_cpu_x 1.914 (finder 2.014; -5%, inside ±10%), evals_x = sim_x = 1, per-scenario headroom 2.53.
  - @4: tripped_total 1 (cpu_per_scenario), victim_cpu_x 2.705.
  - Non-kernel share of solve CPU: 0.44-0.80, median 0.488.
  - load1 1.00 at the end, 3 concurrent processes; thread_factor 1.0000.
- **Step 2 (my method):**
  - (a) v3_s2_03_budget.py uses the gate's own table and constants (scenario_budget, SWEEP_BUDGET_RATIO, live_solve_budget_ratio). At the recorded ratios (mean 130.02 against a 134.32 sweep budget), a confined 2x trips a CPU rule on 9 of 51 scenarios, all via the sweep rule, all tariff/pv/cycle scenarios with r_i > 219. The other 42 of 51 are blind, including the default winter/2z/dhw, which needs 3.00x (per-scenario, 3.0x of record).
    - On this box the live sweep (121.2) sits below record, so even fewer scenarios trip.
    - The --machine-scale 1.02 arm raises the count to 21 of 51, and winter/2z/dhw then trips at 1.78x. The sweep rule sits only 3.3% above the recorded mean, so the verdict depends on the machine: on a runner whose live ratios read 2% or more above record, a confined 2x of the default scenario WOULD be seen. On this box (live 121.2, about 0.93 of record), and on the finder's, it is not. The per-scenario rule (3.0x of record) is structurally blind below about 3x on any machine that matches record.
    - A --machine-scale 1.6 arm is degenerate (every scenario is red even at 1.0x) and is not used.
  - (b) Step 4, a single-line PRODUCTION mutation: v3_s2_03_lineclass.py.
    - The mutation runs the row loop at optimizer.py:1889 (`for b in range(n_rows)` in _comfort_terms_batch) 4 times over. It is emulated in memory as 4 calls of the production method.
    - Result on winter/2z/dhw: solve CPU 1.996x, plan sha equal, solver_calls/evals/simulate_steps 10/1002/4,675,248 in both arms (exact), per-scenario headroom 2.76x. The --passes 1 null gave 0.972.
    - With the reproduced plain sweep (121.19 + 119.4/51 = 123.5 against 134.32) and kernel per-call cost unchanged, none of the six rules trips.
    - This is a one-line production mutation in optimizer.py that doubles the default configuration's solve and that stress.py cannot see. I did not run a sweep with it (no heavy re-runs); the verdict is computed from the reproduced plain sweep.
- **Correction:** "contradicts the file's own claim at SCENARIO_WORK_FACTOR" overreaches. That comment (stress.py:417-419) claims a confined 2x is seen "on both channels", meaning the evaluation and simulate COUNT channels. The kernel-cost comment (stress.py:437-441) explicitly refuses solve-wide CPU at any factor (#346, same-box noise of 1.10-1.44x). The blind spot is partly a documented design trade; it is not an unstated contradiction. The gap itself stands.
- **Reach in real HA:** instrument finding. What it hides is solve CPU in the worker process on real installs; the default config is among the blind scenarios.
- **Severity:** medium, as claimed (a 2x of the default solve can merge unseen, at bounded cost).
- **seam_rule:** it runs every stress.py rule with the gate's own functions across the 51-scenario sweep and a named victim set. It enumerates the gate's rules; victims are added with --victims. true.
- **Class:** class_guess "new" corrected to I1 (same reasoning as D9-s2-02).
- **Vote:** verify, medium. Value 0 rules tripped at a 1.91x confined victim; 42 of 51 scenarios blind at record ratios.
