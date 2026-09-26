# D9 verify-v1 (round 9, lens V1 reproduce), box G3-V1

Tree: branch `handoff/audit-r9-verify-g3-v1` = `6f51db2c` (baseline 1936d5ca + round-9 evidence). Machine: x86_64, 4 vCPU Intel Xeon @ 2.10GHz (AVX-512), Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1, BLAS pinned to 1 thread. Interpreter: `/home/claude/venv-r9/bin/python`. The D9-s2 commands name `/home/claude/venv314/bin/python`, which is absent here; the pinned interpreter above was used instead. D2 and D14 sub-seats ran on the same box, so every CPU/ms figure is provisional; ratios are same-thread. Votes: 7 verify.

## D9-s1-01: per-row loop in `_comfort_terms_batch`
- Re-run `comfort_rowloop.py`: two_zone_dhw_winter share **0.3361** (finder 0.3206, tolerance +-0.03). load1 2.06, thread_factor 1.001, swapins 0, 0 concurrent stress runs. Other cells: two_zone_dhw_shoulder 0.3368, two_zone_nodhw_winter_mild 0.3398, two_zone_dhw_summer 0.1839, single_zone_dhw_winter 0.1412, single_zone_dhw_shoulder 0.2917, single_zone_fuse_3p68 0.2918.
- Perturbation `--vectorize`: **0.0406** on the same cell; 0 mismatched values and identical plan sha on all 8 cells. Solve thread CPU 4072 to 2683 ms (provisional).
- Null control (flat prices): 0.3383.
- Leave-one-out over 7 cells: min 0.1412, max 0.3398, mean 0.2745, mean with the max dropped 0.2636.
- Wording: the claim "0.32 on every two-zone cell" fails on two_zone_dhw_summer (0.1839). The headline value is unaffected.
- Own harness `verify-v1/comfort_parity.py`. Production against an independent axis=1 twin, 120 cases (n = 47/96/97/192/288, B = 1/96/193, 4 layouts, both zone modes):
  - C-order, offset-view and 8-byte-shifted batches: **0 mismatches** under AVX-512, AVX2-only and baseline-only dispatch (`NPY_DISABLE_CPU_FEATURES`, numpy 2.4 group names).
  - Fortran-order batches: 3659 mismatches. `sum(axis=1)` over a column-major batch is not the per-row pairwise sum.
  - Constraint on the fixer: the vectorized form keeps bit parity only while the batch stays C-contiguous. Pin that layout in the fix and its test.
  - Perturbation `--perturb` (reversed-row sum): C-order n=96 cell goes 0 to 280 mismatches.
  - Per-call cost: production/twin 14.23x two-zone, 15.11x single-zone. load1 4.00, thread_factor 1.0000.
- Vote: **verify**, medium.

## D9-s1-02: scalar f(x) per L-BFGS-B iterate
- Re-run `scalar_objective.py --no-parity`: **0.1476** (finder 0.1505, tolerance +-0.02). load1 3.21, thread_factor 1.002.
- Perturbation `--fused --no-parity`: **0.0055**; plan sha identical on 7/7 cells. Solve 3668 to 3140 ms (two-zone winter), 1380 to 1000 ms (single-zone shoulder), provisional.
- Parity arm `--fused`: fused_row0_mismatches 0 and parity_mismatches 0 on the cells read.
- Null control (flat prices): 0.1524. Leave-one-out over 6 cells: min 0.0879, max 0.19, mean with the max dropped 0.1487.
- Scalar call vs one batched row: 18.0x to 25.9x.
- Vote: **verify**, medium.

## D9-s1-03: sysid fit inside one event-loop callback
- Re-run `sysid_loop.py --cadence-min 15`: **2.15x reference_solve** (74.1 ms; finder 2.46x, tolerance +-25%). load1 5.78, thread_factor 1.0.
- Cadence 30 min: 0.92x (28.2 ms). Cadence 5 min: 5.74x (202 ms). Perturbation `--no-fit`: 0.23 ms.
- Every seed completed (phase done, reason ok).
- Reach: `async_run_optimization` (coordinator.py:4773) calls `_run_system_identification` synchronously (:5079), which calls `self._sysid.step` (:10512). No executor sits in between.
- Severity: `DEFAULT_SYSID_ENABLED=False` and runs at most once per 30 days, so low is earned.
- Vote: **verify**, low.

## D9-s1-04: DHW min-run full-suffix re-simulation
- Re-run `dhw_min_run.py`: **7758 calls, 52 weak slots, 42 refused**, exact. Share 0.2418 (load1 6.83, thread_factor 1.02).
- Perturbation `--early-exit`: **4780 calls**; plan sha f84a5fb7240e8b43 unchanged; 6/6 cells unchanged.
- `--hours 48`: 25313 calls (3.26x). The single-zone winter share falls to 0.037 at 48 h.
- Null control (flat prices): 7954 calls, 44/52 refused, plan unchanged under early exit.
- Leave-one-out on the share over 5 cells: min 0.0128, max 0.2418, mean with the max dropped 0.1056.
- Wording: "0.17-0.23 on four single-zone cells" holds on three; single_zone_dhw_shoulder is 0.0198.
- Vote: **verify**, low.

## D9-s2-01: sensor_advisor re-simulated at every plan-sensor write
- Re-run `loop_work.py`: **384 steps per read, 2 advisor calls per read, 3 writes per cycle**, exact. advisor_share_of_loop **0.3209**. load1 6.77, thread_factor 1.0005.
- Perturbation `--advisor-steps 1`: 8 steps per read, share 0.0908. Null control (all candidates configured): 0 steps, share 0.0012.
- Reach: `rank_sensor_advisor` is called unmemoised from `extra_state_attributes` (sensor.py:111), which Home Assistant evaluates on every `async_write_ha_state`.
- Vote: **verify**, low.

## D9-s2-02: replay budget blind to a 2x of loop-thread work
- Re-run `m2_loop_blind.py` at load1 5.36: loop2x.offenders = **1** (loop_over_none 1.478), not the finder's 0.
  - The same run's cpu arm, an exact 2x of the update, read 1.969x of none; the `--scale 4` run read 2.687x.
  - Each arm runs in its own interpreter at a different moment, so cross-arm ratios move by up to ~35% under this load.
  - This is a timing mismatch alone and is not a refute.
- Own paired harness `verify-v1/loop_blind_paired.py` (both ratios from one replay):
  - scale 1: 2.3230 to 2.6685, **1.1488x, 0 offenders**; budget headroom 1.5394x; loop share 0.1486. load1 4.17, thread_factor 1.0005.
  - Perturbation, scale 4: 1.6081x, **1 offender** (4.295 over 3.576).
  - Null control, scale 0: 1.0001x, 0 offenders.
  - Positive control, `--whole`: 1.988x, 1 offender.
- Finder harness `--scale 4`: loop5x offenders 1. stress_cycle_functions = 0 of 139, exact.
- Instrument note: the finder's per-arm-interpreter design is contention-fragile. A fix review should take this number paired or on the quiet box.
- Vote: **verify**, medium.

## D9-s2-03: stress.py blind to a one-scenario non-kernel 2x
- Re-run under `gate_lock auto-lease`, arms `plain,nonkernel2x_one@2.19,nonkernel2x_one@4`, victim winter/2z/dhw: **tripped_total 0** at victim_cpu_x **1.986**, evals_x = sim_x = 1, kernel_x 0.988. The per-scenario budget sits at 2.777x of this run's ratio. load1 1.03, thread_factor 1.0000.
- Non-kernel share of solve CPU per scenario: 0.455 to 0.812 (median 0.512).
- Perturbation @4: victim 3.570x, 1 rule tripped (the per-scenario rule).
- Null control plain2: 0 tripped (sweep 0.983 of plain).
- Positive control twice_one: 2 tripped (evals and simulate at 2.000x), victim 2.613x.
- Leave-one-out, `solvecpu2x_set`, 6 victims: 0 tripped. cpu_x: winter/2z/dhw 2.600, winter/1z/dhw 2.290, shoulder/1z/space 2.202, summer/2z/dhw 2.119, heavy_old/winter 1.483, typical_slab/winter 1.381. Min with the lowest dropped: 1.483.
  - The last two fell short of 2x because the solve itself ran faster in the injected sweep (kernel_x 0.86 and 0.74): sweep-to-sweep noise.
  - Four victims at 2.12x to 2.60x stayed untripped, which carries the claim.
- Wording: the SCENARIO_WORK_FACTOR comment claims detection of a count-channel 2x ("seen on both channels"). The finding's "contradicts" overreads it. The missing non-kernel CPU channel is real.
- Vote: **verify**, medium.
