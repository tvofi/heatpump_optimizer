# S5 class sweep: CPU gate blind to a regression outside its sampled work

New class (round 9), `rca: true`, `n: 3`: D9-s2-02, D9-s2-03, D9-s2-71.

## Enumerator

Three D9-s2/D9-leads harnesses, each already a class-shaped detector rather than a single-instance
probe, copied here unchanged as `enumerate_loop.py`, `enumerate_nonkernel.py`, `enumerate_valve.py`:

- **`enumerate_loop.py`** (D9-s2-02's harness): replays the real coordinator cycle
  (`tests/replay.py:run_fixture`, `synthetic-dhw-only.json`) under `tests/replay.py:cost_offenders`,
  the only budget that covers the event-loop-thread work, at 4 injected scales (none / real-CPU
  doubling / loop-only 2x / loop-only Nx), plus a `sys.setprofile` trace of how many
  `coordinator.py`/`sensor.py`/`topology.py` functions the per-PR gate (`tests/stress.py`'s
  `build_case` sweep) actually reaches.
- **`enumerate_nonkernel.py`** (D9-s2-03's harness): runs `tests/stress.py`'s own 51-scenario
  sweep and evaluates every one of its rules (ceiling, per-scenario, sweep, evaluations/simulate/
  kernel-cost drift) with the gate's own functions, injecting an exact Nx of one scenario's
  non-kernel (interpreter-bound Python outside the three metered `simulate` seams) solve CPU.
- **`enumerate_valve.py`** (D9-s2-71's harness): counts, per `tests/stress.py` scenario, whether
  its built plant throttles (`mixing_valve_mode`), and what `tests/stress.py:sweep_combinations()`
  actually samples versus every valve topology that exists in production.

## Controls (re-run on this box, this session)

- **`enumerate_loop.py`, no args** (default arms none/cpu/loop2x):
  `none.offenders=0` (**null control**), `cpu.offenders=1` (**positive control** — the file's own
  whole-cycle-CPU-doubling arm), `loop2x.offenders=0` (**the class finding**: an exact 2x of only
  the loop-thread share of the cycle trips nothing), `stress_cycle_functions=0` (the per-PR gate's
  sweep touches zero of `coordinator.py`/`sensor.py`/`topology.py`), `none.loop_share_of_budgeted_cycle=0.1098`,
  `loop_over_none=1.126`, `cpu_over_none=1.824`. Same shape as the D9-s2 finder's own recorded
  run (this box's absolute ratios differ slightly, as expected under different contention: the
  finder's box had `cycle_cpu_ratio` 2.42/2.82 against budget 3.576, needing a loopNx re-take;
  this run's `none.cycle_cpu_ratio=3.033` already sits closer to budget, but the qualitative result
  — `loop2x.offenders=0` while `cpu.offenders=1` — reproduces).
- **`enumerate_valve.py`, no args**: `stress_sweep_valve_cases=0 of 51` (**the class finding**,
  exact match to the D9-leads finder's recorded number), valve cells cost
  `cpu_ratio_to_reference` 160.9-353.3 versus 102.3-123.0 for the two non-valve controls in the
  same run (1.3-2.9x, matches "1.3-2.7x" in the judge record within this box's contention).
- **`enumerate_nonkernel.py`**: launched with the finder's own confined arm
  (`--arms plain,nonkernel2x_one,twice_one --victim winter/2z/dhw`); this run did not finish inside
  this session's time budget (the sweep re-solves 51 scenarios per arm on top of the confined
  victim, ~7+ CPU-minutes and rising on this box). Per the project's standing rule to minimise
  heavy CPU-sweep re-runs and reuse a finder's own evidence when the shape already qualifies
  (`no-heavy-d3-reruns`, applied here by the same logic to a heavy D9 sweep), this session did
  **not** force it to completion and instead reused D9-s2-03's own committed evidence: `plain2`
  (null, a clean re-sweep) trips 0 rules; `nonkernel2x_one` (2.014x of one scenario's non-kernel
  work, all outside the metered simulate seams) trips 0 of `tests/stress.py`'s rules across 6
  victim scenarios at 1.92x-2.21x; `twice_one` (the whole solve doubled, same scenario) trips 2
  rules as a positive control; `nonkernel2x_one@4` (non-kernel x5, solve 2.83x) trips 1 rule,
  confirming the detector moves once the injected regression is large enough.

## Disposition

- **D9-s2-02, instance**: `loop2x.offenders=0` confirmed this session — no budgeted check
  (per-PR `tests/stress.py`, nightly `tests/replay.py`) sees a 2x of the coordinator's loop-thread
  work.
- **D9-s2-03, instance**: reused evidence (not re-run this session, see above) — `tests/stress.py`
  misses a confined 2x-solve regression on 6 of 6 tested victim scenarios when the extra work sits
  outside the three metered `simulate` seams.
- **D9-s2-71, instance**: `stress_sweep_valve_cases=0 of 51` confirmed this session — the gate
  samples no throttling-valve topology at all, and valve solves cost 1.3-2.9x a same-family
  control in this run.
- **1 not applicable, new**: `enumerate_loop.py`'s `stress_cycle_functions=0` line is itself a
  fourth angle on the same underlying gap (the per-PR gate's own sweep touches none of
  `coordinator.py`/`sensor.py`/`topology.py`) but is not a fourth *instance* — it is the same
  seam as D9-s2-02 (the per-PR gate cannot see loop-thread coordinator work at all, whether
  doubled or not), not an independent regression shape. Recorded as corroborating detail, not
  counted.
- **0 guarded.**

## Count and RCA

N = 3 verified findings (D9-s2-02, D9-s2-03, D9-s2-71) + 0 additional sweep-confirmed instances
= 3. **rca: true** (N >= 3), matching the brief's table.

## Barrier proposal

Three independent, additive changes to `tests/stress.py` / `tests/replay.py` (one per instance,
since each closes a different blind spot):
1. A per-scenario non-kernel CPU channel in `tests/stress.py`, judged against a same-machine
   baseline capture (`capture_baseline_work` already exists) rather than only the recorded 3.0x
   table — closes D9-s2-03.
2. A loop-thread-only cost channel in `tests/replay.py:cost_offenders`, separate from the
   whole-cycle ratio, so the event-loop's own share is judged on its own budget — closes D9-s2-02.
3. At least one throttling-valve scenario (`mixing_valve_mode` != none) added to
   `tests/stress.py:sweep_combinations()` — closes D9-s2-71.
Cost: each channel is a cheap in-process check (no new solves beyond what the existing sweep
already runs, for 1 and 3; a same-machine baseline capture for 2, already paid once per gate run).
Provisional, not separately timed this session.

## Unfinished / exposure

- `enumerate_nonkernel.py`'s confined run did not complete in this session (see above); reused the
  finder's committed evidence rather than re-deriving it, per the project's standing guidance to
  minimise heavy re-runs of expensive sweep scripts. If a later seat needs a fresh number (e.g.
  after a fix lands), re-run it under `tests/gate_lock.py auto-lease` as its own header documents.
- D9-s2-01 (sensor_advisor re-simulated on the loop thread, low severity) is in the same D9-s2
  finder report but is not part of this class per the judge's `CLASSES-DRAFT.json` membership
  (only D9-s2-02/03/71 are), so it is out of scope for this sweep.
