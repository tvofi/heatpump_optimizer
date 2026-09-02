# D9 — verifier seat 1 of 3, round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree `audit-r2-D9`,
interpreter `.../tvofi-claude/.venv/bin/python`, `PYTHONPATH=tests/hastub`,
the five BLAS variables pinned to `1` before numpy in every run.
`thread_factor` was 1.000 ± 0.0005 on every harness below.

**Box conditions.** The audit box was never idle during my window: `load1`
ran 1.6 – 5.6 and another agent's Python process held one core at ~99 % for
part of it. The contract's `load1 ≤ 1.5` gate is not reachable here (the
quiet-window agent recorded the same standing 1.4 – 2.0). Every absolute
wall/CPU figure below is therefore **provisional** and carries its `load1`;
counts, path decisions, bytes and CPU ratios against
`tests/stress.py:reference_solve` are final. Where a timing number decides
anything I say so explicitly.

**Harnesses I wrote**, all under `/tmp/verify-D9-1/` (`vlib.py` is my own
scaffolding — thread pin, RESULT printing, and a `tests/stress.py` prefix
loader cut at its own sweep marker, so `reference_solve` is the gate's own
function object):

| file | for | what it measures that the finder's does not |
|---|---|---|
| `v1_zero_range.py` | D9-01 | per-gradient equivalents **scoped to `_multi_start_minimize`**; every `_bounds_supported_by_batch` decision with its zero-range count |
| `v2_production_reach.py` | D9-01 | the same, on real `_async_update_data` cycles driven only through shipped config |
| `v2b_more_paths.py` | D9-01 | fuse minus measured house load; the monthly fuse-advisor shadow solve |
| `v2c_argprobe.py` | D9-01 | binds `optimize`'s real signature, so the POSITIONAL `caps_extra`/`space_pins` are read |
| `v3_dup_fx.py` | D9-03 | duplicate `objective(x)` calls observed at the point of duplication; bit-identity of the proposed fix |
| `v4_dhw_planner.py` | D9-04 | tank steps counted as `simulate_dhw_step` loop bodies, not as `len()` sums; 5-case distribution + DHW-off null |
| `v5_stress_gate.py` | D9-02 | an executed **4×** injection; a named one-line production mutation; leave-one-out |
| `v6_gil.py` | D9-05 | real executor-thread stack sampling; a switch-interval **diagnostic** |
| `v6b/v6c_yield*.py` | D9-05 | what kind of yield actually unblocks the loop |
| `v7_fix_probe.py` | D9-01 | does the proposed fix work, and does it drift |

Logs: `/tmp/verify-D9-1/logs/`.

---

## D9-01 — one zero-range bound puts the whole solve on the scalar FD path

### My metric definition

> `equiv_per_gradient_scoped` = (scalar `ThermalModel.simulate_step` calls +
> rows of `ThermalModel.simulate_trajectory_batch`) accumulated **only
> between entry and return of `optimizer._multi_start_minimize`**, divided by
> the sum of `OptimizeResult.njev` over the L-BFGS-B runs inside those calls.

The brief fixes the numerator and says "per gradient evaluation of
`_multi_start_minimize`". The finder accumulated the numerator over the whole
`optimize()` call — DHW planning, the baseline power computation and the final
trajectory simulations included. The two definitions differ by a **fixed 5 n =
480 equivalents per `_multi_start_minimize` call** (3 candidate scorings + 2
final scorings) plus everything outside the solve. That is 1.6 % on the
two-zone case (njev 103) and 10 % on a single-zone one (njev 9–11), which is
why the finder's own table shows `single_zone_dhw` at 394.7 "per gradient" —
an artefact of its divisor, not a path difference. Both definitions agree on
every path decision and on the scalar/batched ratio.

### RESULT lines — finder's harness, re-run once

`tools/audit/round2/D9/h1_grad_equivalents.py`, load1 3.69 → thread_factor 1.000:

```
RESULT two_zone_dhw.equivalents_per_gradient=297.32 count          (report 297.32, exact)
RESULT pin_zero_range_two_zone_dhw.equivalents_per_gradient=9221.55 (report 9221.55, exact)
RESULT pin_zero_range_two_zone_dhw.simulate_step_calls=1595328      (report 1595328, exact)
RESULT dhw_cap_zero_range.equivalents_per_gradient=9221.85          (exact)
RESULT dhw_cap_one_step_zero_range.equivalents_per_gradient=294     (exact)
RESULT two_zone_dhw.solve_over_reference=37.7923 ratio              (report 38.5)
RESULT pin_zero_range_two_zone_dhw.solve_over_reference=748.849     (report 751)
RESULT dhw_cap_zero_range.solve_over_reference=722.79               (report 711–750)
RESULT reference_solve_cpu=18.338 ms_provisional
```

Every count is bit-identical to the report; every CPU ratio is inside its
tolerance. Nothing in D9-01 rests on a number that failed to reproduce.

### RESULT lines — my harness `v1_zero_range.py` (load1 2.9 → 5.6)

```
RESULT house.p_max_kw=6 kW                RESULT house.dhw_run_power_kw=4.8 kW
RESULT A_two_zone_dhw_default.equiv_per_gradient_scoped=292.66  path=batched  zero_range_bounds=0
RESULT B_one_pin_off.equiv_per_gradient_scoped=9218.77          path=scalar   zero_range_bounds=1   njev=173
RESULT C_cap_0p6_pmax.equiv_per_gradient_scoped=9029.11         path=scalar   zero_range_bounds=3
RESULT D_fuse_16A_1phase.equiv_per_gradient_scoped=9026.54      path=scalar   zero_range_bounds=3
RESULT E_fuse_16A_3phase_control.equiv_per_gradient_scoped=292.66 path=batched zero_range_bounds=0
RESULT F_perturb_bound_removed.equiv_per_gradient_scoped=292.66 path=batched   (perturbation, direction DOWN)
RESULT golden_fuse_guard.equiv_per_gradient_scoped=9029.93      path=scalar   zero_range_bounds=3
RESULT golden_fuse_guard.simulate_step_calls=731424  batch_rows=0  solve_over_reference=218.874
RESULT golden_capacity_curve.equiv_per_gradient_scoped=341.333  path=batched  zero_range_bounds=0
RESULT golden_winter_two_zone_dhw.equiv_per_gradient_scoped=292.66 path=batched
RESULT ratio.B_one_pin_off_over_A=31.4999
RESULT ratio.C_cap_0p6_pmax_over_A=30.8518
RESULT ratio.D_fuse_16A_1phase_over_A=30.8431
RESULT ratio.golden_fuse_guard_over_golden_winter_two_zone_dhw=30.8546
```

The counts are exact arithmetic, and worth stating as such because it makes
the finding independent of any clock:

* batched path, **per gradient** = `3n` = 288 equivalents (n batch rows + 2n
  scalar steps: scipy's `fun(x)` and the jac's own `f0`);
* scalar path, **per gradient** = `n²` = 9,216 (n scalar trajectories of n
  steps; scipy reuses f0, so it is n and not n+1);
* case B closes exactly: `173 × 9216 + 480 = 1,594,848` = the measured
  `equiv_in_msm`.

So the gradient-cost ratio is **n/3 = 32.0 exactly**, and the observed
whole-solve ratios (30.8–31.5) are that number diluted by the fixed 5n.

### Attacks

**1. Is the metric the one the brief fixed?** Yes for the numerator; the
divisor differs (above). Both give the same verdict; I report both
(`equiv_per_gradient_finder_defn` is printed alongside mine in every case).

**2. Is the trigger reachable in production, or only by injecting a kwarg?**
This was the attack I expected to land, and it did not. `v2/v2b/v2c` drive
real `HeatPumpOptimizerCoordinator._async_update_data()` cycles and touch the
optimizer only to read arguments and gate decisions. `v2c` binds
`optimize`'s real signature because `coordinator.py:4736` passes
`space_pins`, `dhw_pins` and `caps_extra` **positionally**:

```
RESULT fuse_16A_1phase.call0_main.caps_min_kw=3.68        zero_range_bounds=1   path=scalar
RESULT fuse_25A_3phase_ev14kw.call0_main.caps_min_kw=3.25 zero_range_bounds=1   path=scalar
RESULT fuse_25A_3phase_ev14kw.call1_fuse_advisor.caps_min_kw=0 zero_range_bounds=96 path=scalar
RESULT manual_plan_one_slot.call0_main.space_pins_off=23  space_pins_on=2
RESULT manual_plan_one_slot.call0_main.zero_range_bounds=23 path=scalar
```

Whole-cycle cost, same harness (`v2`):

```
RESULT base_no_guard.equivalents=26880          path=batched
RESULT fuse_16A_1phase.equivalents=415680       path=scalar   (x15.46)
RESULT manual_plan_one_slot.equivalents=491424  path=scalar   (x18.28)
RESULT perturb_guard_off_same_fuse.equivalents=26880 path=batched   (perturbation, DOWN)
RESULT fuse_25A_3phase_control.equivalents=53760 path=batched  (control: cap does not bind)
RESULT control_no_fuse.equivalents=26880        path=batched
```

Four independent shipped routes, none of them contrived:

* **Fuse guard, single-phase 16 A.** `coordinator.py:_fuse_kw` gives
  `16 × 1 × 230/1000 = 3.68 kW`; the DHW planner clamps its block to
  `p_run_cap = min(caps_extra)` (`optimizer.py:3196`), so `p_dhw_run` becomes
  *exactly* the cap and `solve_space`'s `headroom = caps_extra − dhw_plan` is
  *exactly* zero at every DHW step. The condition is simply
  `fuse_kw − baseline_house_load < 0.8 × nameplate`; with the shipped default
  nameplate of 5 kW that is any headroom under 4.0 kW. `fuse_guard_enabled`
  and `main_fuse_phases` are both user-facing config-flow fields
  (`config_flow.py:2587–2601`, `translations/en.json:580–601`).
* **Fuse guard minus a measured house load.** 25 A 3-phase (17.25 kW) with a
  14 kW `house_power_entity` reading gives a 3.25 kW cap — scalar.
* **The monthly fuse advisor**, which runs whenever `main_fuse_amperes` is set
  *even with the guard switched off*, re-solves at the next lower rung of
  `FUSE_LADDER_A`; on a 1-phase 20 A house the candidate is 3.68 kW, and on
  the 25 A/14 kW house the candidate cap clips to **0**, giving all 96 bounds
  zero range. (`advisor_20A_1phase_guard_off.scalar_path_solves.fuse_advisor=2`
  with `.main=0`.)
* **The manual plan.** `manual_plan.ManualOverride.channel_pins` pins every
  step inside the override window that no slot covers to `PIN_OFF = 0.0`. One
  30-minute "run space heating" slot applied through the production entry
  point `async_apply_manual_plan` left **23 forced-off steps**, and the
  optimizer's own safety release (`optimizer.py:2223`) released none of them.

**3. Is the golden `fuse_guard` fixture really on that path?** Yes, measured
directly by calling `tests/golden.py:capture("fuse_guard", …)`: scalar path,
3 zero-range bounds, 731,424 `simulate_step` calls, 9,029.9 equivalents per
gradient, 218.9× the reference solve. `capacity_curve` — the other
`caps_extra` fixture — is **not** (its per-step cap never coincides with the
horizon minimum at a DHW step); the report did not claim it was.

**4. Does the number move under the stated perturbation?** Yes, twice:
removing the pin/cap returns the same solve to 292.66 (×31.5 down); switching
`fuse_guard_enabled` off with the same fuse configured returns the live cycle
from 415,680 to 26,880 equivalents (×15.5 down).

**5. Does the proposed fix work, and is "no golden drift" true?**
(`v7_fix_probe.py`; the two-line patch is: drop the `lo >= hi` rejection in
`_bounds_supported_by_batch`, and set the `ub <= lb` entries of
`_batch_fd_gradient`'s result to 0.0.)

```
RESULT fuse_guard_tree.solve_over_reference=243.47     equiv_per_gradient=9035.85  path=scalar
RESULT fuse_guard_patched.solve_over_reference=17.3786 equiv_per_gradient=300.152  path=batched
RESULT fix.cpu_speedup=13.9977
RESULT pin_tree.solve_over_reference=742.594    equiv_per_gradient=9221.55
RESULT pin_patched.solve_over_reference=63.231  equiv_per_gradient=293.246   (x11.7 CPU)
RESULT drift.fields_identical=8   drift.fields_total=12   drift.status_same=1
RESULT drift.power_schedule.max_abs_diff=4.5e-05      (kW)
RESULT drift.room_temp_trajectory.max_abs_diff=1e-06  RESULT drift.predicted_cost.max_abs_diff=8e-06
RESULT pin_drift.power_schedule_max_abs_diff=0.000201911 kW
RESULT pin_drift.pinned_step_power_tree=0  pin_drift.pinned_step_power_patched=0
RESULT pin_drift.predicted_cost_rel_diff=4.11699e-07
```

The fix is correct (the pinned step still plans 0 kW) and worth 11.7–14.0× of
solve CPU. One correction to the report's fix-scope note: the drift is **not**
"possibly none". `tests/golden.py:PRECISION = 6`, and the `fuse_guard`
fixture's `power_schedule` moves by up to 4.5 × 10⁻⁵ kW, so the fixture would
need re-recording. It is last-decimal, but it is real.

### Reading of the quiet-window re-take

The five `solve_cpu` values that "did not reproduce" are absolute
milliseconds, and every one of them fell (908 → 669; 25,046 → 12,840;
17,700–23,700 → 12,212). That is the expected direction on an idle box and it
is exactly the split the harness contract predicts: the ratios against
`reference_solve` all reproduced (721 and 686 quiet, 748.8 and 722.8 in my
re-run, against 751 and 711–750 reported). **Nothing about D9-01 weakens.**

What *should* change is the report's consequence paragraph, which scales from
the contended milliseconds: "18–25 s on the M1 (≈ 2–3 min on a Pi 4)" becomes
**12.2–12.8 s on the M1, ≈ 85–90 s on a Pi 4 at the stated ×7**, and "0.9 s
(≈ 6 s on a Pi)" becomes **0.67 s (≈ 4.7 s)**. The ×7 factor itself is used
honestly — it is labelled an assumption from public single-core benchmarks at
every use, and it is applied to an M1 number that is stated. The only fault is
that the M1 numbers it multiplies are the fan-out ones.

### Vote

**verify** (high, bug).

Deciding number: through the coordinator's own wiring, with nothing injected,
a shipped single-phase 16 A fuse guard and a one-slot manual plan each put
every gradient of the live solve on scipy's scalar path — **9,026.5 / 9,218.8
simulate-step-equivalents per gradient against 292.66** (×30.8 / ×31.5), and
**415,680 / 491,424 equivalents per coordinator cycle against 26,880**
(×15.5 / ×18.3). The shipped golden `fuse_guard` fixture is on the same path
(9,029.9 per gradient, 218.9× the reference solve).

---

## D9-02 — the stress gate cannot see a 2× or 4× uniform regression

### My metric definition

> `gate_blind_at_4x` = 1 when an **exact 4× uniform CPU regression**, injected
> at `HeatPumpOptimizer.optimize` (the symbol `tests/stress.py` times), leaves
> *both* of the gate's checks passing: per-scenario tripped = 0 over all 48
> combinations **and** sweep tripped = 0.

The finder injected 2× and divided budget by observation to get 4.685. A
division is a derivation; the owner's brief asks specifically whether a 4× is
visible, so I injected 4× and ran it.

### RESULT lines — finder's harness, re-run once

`h7_stress_gate.py`, load1 2.00, thread_factor 1.000:

```
RESULT plain.worst_ratio=299.373   plain.sweep_ratio=52.7513
RESULT plain.per_scenario_tripped=0   plain.sweep_tripped=0
RESULT injected_2x.worst_ratio=579.954  injected_2x.sweep_ratio=106.739
RESULT injected_2x.per_scenario_tripped=0  injected_2x.sweep_tripped=0
RESULT smallest_detectable_uniform_regression=4.67644
RESULT ci_sets_stress_ratio=0   tests_memory_instrumentation=0
```

(report 298.8 / 50.7 / 4.685; quiet 293.9 / 53.4 / 4.763. All inside ±20 %.)

### RESULT lines — my harness `v5_stress_gate.py` (load1 1.90)

```
RESULT plain.worst_scenario=shoulder/tariff+pv+cycle   plain.worst_ratio=294.042
RESULT plain.median_ratio=35.4585   plain.p90_ratio=110.79   plain.min_ratio=0.830753
RESULT plain.sweep_ratio=53.1995
RESULT plain.per_scenario_headroom=4.76122   plain.sweep_headroom=8.45872
RESULT smallest_detectable_uniform_regression=4.76122   detection_limited_by=per_scenario
RESULT injected_4x.measured_factor_worst=4.0412   injected_4x.measured_factor_sweep=4.00346
RESULT injected_4x.worst_ratio=1188.28  (budget 1400)   injected_4x.sweep_ratio=212.982 (budget 450)
RESULT injected_4x.per_scenario_tripped=0   injected_4x.sweep_tripped=0
RESULT gate_blind_at_4x=1
RESULT mutation_multistart_4.measured_factor_sweep=1.47895
RESULT mutation_multistart_4.worst_ratio=481.35   mutation_multistart_4.sweep_ratio=78.6795
RESULT mutation_multistart_4.caught=0
RESULT plain.loo_per_scenario_headroom=5.30648   plain.loo_sweep_headroom=9.35015
RESULT ci_sets_stress_ratio=0   ci_mentions_stress_ratio_any=1   tests_memory_instrumentation=0
```

### Attacks

**1. Is the injection honest?** Yes — `optimize` is run four times and only
the last result is returned, so the scenario's `solve_cpu_ms` quadruples while
the reference solve beside it does not. Measured factor 4.041 (worst) and
4.003 (sweep), i.e. the injection is exactly what it claims.

**2. Is the aggregate a grid artefact?** No. Dropping the single most
favourable of the 48 cells (`shoulder/tariff+pv+cycle`, 294.0) leaves
`shoulder/tariff+pv` at 263.8 and the per-scenario headroom at **5.31×**;
the leave-one-out sweep headroom is 9.35×. Removing a cell makes the gate
*blinder*, not sharper.

**3. The test-gap rule — name the one-line PRODUCTION mutation and its file.**
`custom_components/heatpump_optimizer/optimizer.py:121`:
`_MULTI_START_SOLVES = 2` → `_MULTI_START_SOLVES = 4`. Applied at the module
symbol the production function reads, it makes the whole 48-combination sweep
**1.479×** dearer and lifts the worst scenario to 481.4 — against a 1400
budget and a 450 sweep budget. `mutation_multistart_4.caught = 0`. The
mutation lives in a production file, not a test file, so the gap stands under
the brief's rule 4.

**4. Was the wrong gate mode used?** The claim is about budget constants, not
about scoping, so mode does not enter. I did check the surrounding facts by
executed grep rather than by reading the report: `GATE_SCOPE` defaults to
`full` (`tests/run.sh:103`), `stress.py` is run alone after every lane
(`tests/run.sh:344,372`), and the only mention of `STRESS_*_RATIO` in
`.github/workflows/tests.yml` is a comment saying they "are the knobs if it
ever needs one" — i.e. unset. `ci_sets_stress_ratio = 0` is right.
Note in passing that this **corrects** the owner's premise in the D9 brief
("CI sets it 4× looser than the default"): CI sets nothing; the default itself
is the problem.

**5. Is the severity earned?** The consequence is a suite gap, not a live
defect, and it is the gap that let D9-01's 30× path and the pre-existing
budget mis-sizing go unnoticed. Medium is right.

### Reading of the quiet-window re-take

All twelve D9-02 numbers reproduced on the quiet box, including both tripped
counts and both greps. This finding never depended on a wall clock: its
inputs are CPU *ratios*, which are what the contract calls final. Nothing to
adjust.

### Vote

**verify** (medium, bug).

Deciding number: `gate_blind_at_4x = 1` — an exact 4.04× uniform regression
injected at `HeatPumpOptimizer.optimize` trips neither check (0 of 48
scenarios; sweep 213.0 against a 450 budget), and the one-line production
mutation `optimizer.py:121 _MULTI_START_SOLVES = 2 → 4`, worth 1.48× of sweep
CPU, also passes untouched.

---

## D9-03 — the batched jac re-evaluates f(x) that scipy just computed

### My metric definition

> The objective passed into `_multi_start_minimize` is wrapped, so every
> evaluation of the scalar objective is seen with its x.
> `duplicate_objective_evals` = evaluations whose `x.tobytes()` (and args)
> equal those of the **immediately preceding** evaluation;
> `duplicate_per_gradient` = that count / Σ njev.

This measures the duplication at the point where it happens, without assuming
anything about trajectory length — the finder inferred it from
`scalar_steps_per_gradient = 2n`.

### RESULT lines — finder's harness, re-run once

```
RESULT two_zone_dhw.nfev=103  two_zone_dhw.njev=103            (exact)
RESULT two_zone_dhw.scalar_steps_per_gradient=201.32           (exact)
RESULT perturb_memo_two_zone_dhw.scalar_steps_per_gradient=100.66 (exact)
RESULT perturb_memo_two_zone_dhw.batch_rows_per_gradient=96    (exact)
```

### RESULT lines — my harness `v3_dup_fx.py` (load1 1.88)

```
RESULT plain.objective_evals=211   plain.duplicate_objective_evals=106   plain.njev=103
RESULT plain.duplicate_per_gradient=1.02913
RESULT plain.equiv_per_gradient_scoped=292.66   plain.scalar_steps_per_gradient_scoped=196.66
RESULT perturb_one_entry_cache.equiv_per_gradient_scoped=193.864
RESULT perturb_one_entry_cache.scalar_steps_per_gradient_scoped=97.8641
RESULT plain.solve_over_reference=36.2871   perturb_one_entry_cache.solve_over_reference=31.8513
RESULT cache_identical.fields_matching=8   cache_identical.fields_total=8
RESULT cache_identical.status_same=1
```

**Half of every scalar objective evaluation in the solve is a repeat**: 106 of
211 calls land on the point the previous call already evaluated, 1.03 per
gradient (the 0.03 is the per-run final `objective(res.x)` scoring landing on
the last iterate).

### Attacks

**1. Is the duplicate really at the same x?** Measured by bytes, not argued:
`x.tobytes()` plus the args tuple. 106 exact matches.

**2. Does the perturbation move the number in the stated direction?**
Yes: the one-entry cache — the finding's own proposed fix, not the finder's
`simulate_trajectory` memo stand-in — takes equivalents per gradient from
292.66 to 193.86 (−33.8 %) and scalar steps from 196.66 to 97.86 (−50.2 %),
with batch rows unchanged at 96.

**3. Is "bit-identical, no golden drift" true?** The finder asserted it. I ran
it: with the cache active, all eight published fields I compared
(`power_schedule`, `dhw_power_schedule`, `optimal_setpoints`,
`room_temp_trajectory`, `predicted_cost`, `predicted_savings`,
`dhw_temp_trajectory`, `compressor_starts`) are **bit-identical** by
`np.array_equal`, and the status string matches. The claim holds.

**4. Is the severity earned?** The gain is 12.2 % of solve CPU (36.29 → 31.85
× reference), free and drift-free. Low is right.

### Reading of the quiet-window re-take

The only D9-03 number that did not reproduce is `perturb_memo.solve_cpu`
(789 → 565 ms), an absolute millisecond figure that fell on the idle box like
every other one. Both counts — 201.32 and 100.66 — are bit-exact in the quiet
log and in my re-run. Nothing weakens.

### Vote

**verify** (low, bug).

Deciding number: **106 duplicate objective evaluations against 103 gradients**
(1.03 wasted full objective evaluations per gradient, 50.2 % of all scalar
objective calls), and the one-entry cache removes them for
292.66 → 193.86 equivalents per gradient with all eight published fields
bit-identical.

---

## D9-04 — DHW planning cost

### My metric definition

> `tank_steps` = calls of `ThermalModel.simulate_dhw_step` — the body of the
> Python loop inside `simulate_dhw_only` — counted while inside
> `_build_dhw_requirements`; `planner_over_reference` = thread CPU inside
> `_build_dhw_requirements` / the median CPU of `reference_solve`;
> `planner_share_of_solve` = the same CPU / the whole `optimize()` thread CPU.

The finder summed `len(dhw_power_schedule)` per `simulate_dhw_only` call,
which assumes every call simulates the full horizon. Counting loop bodies
makes no such assumption and gives a slightly **higher** figure (6,624 vs
6,144 per planning call at n = 96) because the planner also steps the tank
outside `simulate_dhw_only`.

### RESULT lines — finder's harness, re-run once

`h1b_dhw_loops.py`, load1 1.61:

```
RESULT two_zone_dhw.simulate_dhw_only_per_planning_call=64      (exact)
RESULT two_zone_dhw.tank_steps_per_planning_call=6144           (exact)
RESULT two_zone_dhw.compute_cop_dhw_calls=14168                 (exact)
RESULT two_zone_dhw.planner_over_reference=3.95515   (report 3.4–3.8, quiet 4.079)
RESULT single_zone_dhw.planner_share_of_solve=0.618803 (report 0.6296, quiet 0.6213)
RESULT two_zone_dhw.minrun_share_of_planner=0.477088   (report 0.43–0.59)
RESULT perturb_h48_two_zone_dhw.simulate_dhw_only_per_planning_call=118 (exact)
```

### RESULT lines — my harness `v4_dhw_planner.py` (load1 1.66)

```
RESULT two_zone_dhw.simulate_dhw_only_per_planning_call=64   tank_steps_per_planning_call=6624
RESULT two_zone_dhw.minrun_weak_slots=26,26   two_zone_dhw.minrun_trajectories=96
RESULT two_zone_dhw.planner_share_of_solve=0.117297   planner_over_reference=4.36934
RESULT single_zone_dhw.planner_share_of_solve=0.636502   planner_over_reference=4.17587
RESULT shoulder_single_zone_dhw.planner_share_of_solve=0.102072  planner_over_reference=1.98812
RESULT summer_single_zone_dhw.planner_share_of_solve=0.433194    planner_over_reference=2.24241
RESULT heavy_old_winter_dhw.planner_share_of_solve=0.116832      planner_over_reference=3.55502
RESULT control_nodhw.planning_calls=0  tank_steps=0  planner_over_reference=0
RESULT perturb_h48_two_zone_dhw.tank_steps_per_planning_call=24096  planner_over_reference=14.6083
RESULT loo.planner_over_reference_mean=3.26615   loo.drop_most_favourable_mean=2.99036
RESULT loo.planner_share_max=0.636502  loo.planner_share_median=0.117297
RESULT loo.drop_most_favourable_share_max=0.433194
RESULT two_zone_dhw.minrun_share_of_planner=0.483806  tank_sim_share_of_planner=0.64396
```

### Attacks

**1. Is `_apply_dhw_min_run` really re-simulating once per weak slot?**
Counted, not read: 26 weak slots per call and **96 full tank trajectories**
across the two calls = 2 × (1 base + 26 raised + 21 refreshes after a
rejection). `optimizer.py:4282–4295` is the loop, one `simulate_dhw_only` per
iteration plus one more per rejected slot. Confirmed.

**2. Is the null control present?** I added one the finder did not have:
`control_nodhw` — DHW disabled — gives `planning_calls=0`, `tank_steps=0`,
`planner_over_reference=0`. The measured cost is the planner's and nothing
else's.

**3. Is the "63 % of a single-zone DHW solve" headline a cherry-pick?**
Partly, and this is my one substantive objection. Across the five cells the
share is 0.117 / **0.637** / 0.102 / 0.433 / 0.117 — median 0.117, and
dropping the most favourable cell leaves a maximum of 0.433. The 63 % is the
maximum of five, and it is large mainly because the single-zone winter DHW
solve is the *cheapest* solve in the set (116 ms, 6.6× the reference). The
planner's own cost is near-constant at **1.99–4.37× a reference solve**
(mean 3.27, drop-the-best mean 2.99) per planning call, twice per solve. I
would restate the finding's title as "the DHW planner costs a near-constant
2–4.4× a reference solve per planning call, twice per solve — 10 % of the
default two-zone solve and 64 % of a single-zone winter one". That is a
framing correction, not a refutation: every number the finder reported
reproduced.

**4. Does the perturbation move it?** Yes, 24 → 48 h: 118 `simulate_dhw_only`
calls (exact match) and 24,096 tank steps per planning call, 14.61× the
reference — a 3.6× rise for a 2× horizon, so the loops are super-linear as
claimed.

### Reading of the quiet-window re-take

Every D9-04 number reproduced on the quiet box, including the absolute
`planner_cpu` (70–76 → 71.3 ms) — this is the one finding whose milliseconds
survived, because the planner is short enough that contention did not
dominate it. Nothing to adjust.

### Vote

**verify** (low, bug), with the framing correction above.

Deciding number: **64 `simulate_dhw_only` calls and 6,624 tank steps per
`_build_dhw_requirements` call, twice per solve**, of which
`_apply_dhw_min_run` alone contributes 96 full tank trajectories for 52 weak
slots — costing 1.99–4.37× a reference solve across five cases, against a
DHW-off control of exactly zero.

---

## D9-05 — the solve starves the event loop

### My metric definition

The brief fixes it (max gap between 1 ms heartbeat ticks on a real loop with
the solve in a `ThreadPoolExecutor`; starvation share = time in gaps > 5 ms /
solve wall; idle heartbeat as null control), and I used it unchanged. Two
things I did differently:

* **no production symbol is wrapped during the measurement.** The finder
  wrapped eight production functions in Python closures to attribute stages;
  those wrappers are themselves Python frames and a plausible source of the
  holds being measured. I call `optimize` unwrapped and name the culprit by
  sampling the executor thread's own frames (`sys._current_frames()[tid]`) at
  the instant a long gap ends — the bytecode boundary right after the call
  that held the GIL.
* **a diagnostic perturbation**: `sys.setswitchinterval` 5 ms → **0.5 ms**.
  If the holds are set by the interpreter's switch interval they collapse; if
  they are single uninterruptible C calls they do not move. The finder's
  5 → 50 ms arm cannot separate those.

### RESULT lines — finder's harness, re-run once

`h3_gil_hold.py`, load1 1.97, box 85 % idle:

```
RESULT idle_control.starvation_share=0.0166677   idle_control.longest_gil_hold=14.3187
RESULT two_zone_dhw.starvation_share=0.944137    (report 0.967, quiet 0.950)
RESULT two_zone_dhw.longest_gil_hold=416.591     (report 39.4, quiet 265/313/376/412)
RESULT two_zone_dhw.gap_p50=1.80002              (report 13.3, quiet 1.6–2.4)
RESULT two_zone_dhw.gap_p99=343.411              (report 35.8, quiet 232–338)
RESULT two_zone_dhw.ticks_per_second=41.2005     (report 74, quiet 44.5)
RESULT two_zone_dhw.long_gap=416.6ms@dhw_lp_build
RESULT dhw_cap_zero_range.starvation_share=0.997861  (report 0.998) longest=18.4626 p50=16.3069
RESULT single_zone_dhw.starvation_share=0.735202  (report 0.748)
```

### RESULT lines — my harness `v6_gil.py` (load1 1.82, box 87 % idle)

```
RESULT idle_control.starvation_share=0   idle_control.longest_gil_hold=2.49912  ticks_per_second=758.457
RESULT two_zone_dhw.starvation_share=0.95138   longest_gil_hold=409.207
RESULT two_zone_dhw.gap_p50=2.37313  gap_p90=24.1923  gap_p99=310.712  ticks_per_second=45.435
RESULT two_zone_dhw.share_time_in_gaps_over_100ms=0.599752
RESULT two_zone_dhw_repeat.starvation_share=0.952108  longest_gil_hold=204.339
RESULT single_zone_dhw.starvation_share=0.759426  longest_gil_hold=16.7567
RESULT fuse_cap_zero_range.starvation_share=0.995383  longest=17.6695  p50=16.3075  p99=16.3747 (6.56 s)
RESULT perturb_switch0p5ms_two_zone_dhw.starvation_share=0
RESULT perturb_switch0p5ms_two_zone_dhw.longest_gil_hold=4.59958  ticks_per_second=362.02
RESULT switch_interval_sensitivity=0.0112402
```

Executor-thread stacks at the end of the longest gaps:

```
409.2 ms @ optimizer.py:3787:_plan_dhw_min_cost | _build_dhw_requirements | _co_optimize
204.3 ms @ thermal_model.py:1770:_simulate_step_two_zone | simulate_step | simulate_trajectory | objective
 94.1 ms @ dataclasses.py:1619:_replace | replace | _simulate_step_two_zone | simulate_step
 80.9 ms @ thermal_model.py:2268:simulate_trajectory | objective | optimizer.py:325:jac
 51.6 ms @ numeric.py:166:zeros_like | simulate_trajectory_batch | objective_batch | _batch_fd_gradient
```

### Attacks

**1. Was the number taken under contention?** Mine was taken at load1 1.82
with the box 87 % idle, and reproduces the quiet agent's numbers, not the
finder's. Both of my runs (finder's harness and mine) agree.

**2. Are the wrappers the cause?** No. My harness wraps nothing during the
solve and still sees 409.2 ms.

**3. What is the mechanism?** Not what the report says. The report attributes
the longest hold to "the vectorised batch simulation (numpy on 96×97 arrays
holds the GIL between ops)". Two of my longest holds land in **pure Python
frames** — `thermal_model.py:_simulate_step_two_zone` (204.3 ms) and
`dataclasses.py:_replace` (94.1 ms) — which pass thousands of bytecode
boundaries per millisecond and cannot be uninterruptible C calls. And the
diagnostic perturbation settles it: a 10× shorter switch interval takes the
longest hold from 409.2 ms to **4.60 ms** (×0.011) and the starvation share
from 0.951 to **0** for **+3.1 % of executor CPU**. This is CPython's GIL
hand-off convoy — the compute thread drops the GIL and re-acquires it before
the waiting loop thread is scheduled — not a long C call. It also explains the
quiet-window paradox exactly: a contended box makes involuntary context
switches more frequent, which gives the waiting loop thread more chances, so
the *maximum* hold comes out **smaller under load** while the median gap comes
out larger. The fan-out figures were the artefact.

**4. Would the mitigation the report dismisses work?** I tested it rather than
arguing (`v6c_yield_kinds.py`, 316 yields injected at every
`simulate_trajectory` / `simulate_trajectory_batch` exit, ≈ one per 2 ms):

| yield | longest hold | starvation share | executor CPU |
|---|---|---|---|
| none | 310.7 ms | 0.945 | 1.000 |
| `time.sleep(0)` | 415.2 ms (×1.34) | 0.947 (×1.00) | ×0.996 |
| `time.sleep(1e-6)` | 15.5 ms (**×0.050**) | 0.928 (**×0.981**) | ×0.997 |
| `time.sleep(2e-4)` | 16.3 ms (×0.053) | **0.094** (×0.100) | ×1.050 |

The report's sentence — "a `time.sleep(0)` every k objective evaluations only
shortens the holds, not the share" — is **half right and, on the sleep it
names, too generous**: `time.sleep(0)` takes CPython's zero-argument fast path
and never releases the GIL, so it changes nothing at all (×1.00 on the share,
×1.34 on the longest hold, i.e. noise). A *real* micro-sleep does exactly what
the report predicts of it: the longest hold falls 20× while the share barely
moves (0.945 → 0.928). Only a sleep long enough for the loop to actually run
(2 × 10⁻⁴ s × 316 = 63 ms of sleeping) drops the share to 0.094, at +5 % CPU
and +120 ms of wall. So the fix scope's conclusion — a process, not a yield —
survives; the sleep it names should be corrected to a non-zero one.

**5. Is the FakeHass trap avoided?** Yes: a real `asyncio` loop and a real
`ThreadPoolExecutor` in both harnesses; the idle control gives 758 Hz and a
2.5 ms maximum, so the instrument is clean.

**6. Is the severity earned?** On the default path the loop is unusable for
0.95 of a 0.68 s solve, with 0.60 of that wall time inside single gaps longer
than 100 ms — on a Pi 4 at the report's ×7 that is a ~2.9 s dead event loop,
twice an hour, which Home Assistant itself logs as a blocked-loop warning. On
the D9-01 path it is 6.6–11.5 s of continuous 16 ms sludge (≈ 46–80 s on a Pi),
though that consequence is already booked to D9-01. Medium is defensible.

### Reading of the quiet-window re-take

The quiet agent is right on both counts and I reproduce it independently at
load1 1.8–2.0: the **starvation share — the number the finding rests on —
reproduced** (0.967 reported, 0.950 quiet, 0.944 and 0.951 mine), and the gap
distribution came out far worse than reported. The four "did not reproduce"
entries are all the same fact: the report's `longest_gil_hold` 39.4 ms,
`gap_p99` 35.8 ms and `gap_p50` 13.3 ms describe a contended box, where the
loop was being scheduled often enough to break the long holds into many
medium ones. The true idle-box picture is the opposite shape — mostly 2 ms
ticks punctuated by 200–420 ms freezes. **D9-05 understates its own defect**
and should be re-stated: not "the loop turns at 68–74 Hz", but "the loop turns
freely except for a handful of 0.2–0.4 s freezes that account for 60 % of the
solve's wall time", with `_plan_dhw_min_cost` named alongside the batch
simulation, and with the mechanism corrected from "numpy holds the GIL" to
"GIL hand-off starvation".

### Vote

**verify** (medium, bug) — the finding stands and its headline metric
reproduces; the numbers around it must be re-stated from idle-box samples.

Deciding number: **starvation share 0.951 against an idle null control of
0.000**, with a longest contiguous hold of **409.2 ms** (mine, unwrapped) and
**416.6 ms** (the finder's own harness, my re-run) against the 39.4 ms in the
report, and **0.600 of the solve's wall time inside gaps longer than 100 ms**.

---

## Summary

| finding | vote | deciding number |
|---|---|---|
| D9-01 | **verify** (high) | 9,027 vs 292.66 equivalents per gradient (×30.8) on the live solve of a shipped single-phase 16 A fuse-guard install; 415,680 vs 26,880 per coordinator cycle; the golden `fuse_guard` fixture on the same path at 218.9× the reference solve |
| D9-02 | **verify** (medium) | `gate_blind_at_4x = 1`: an exact 4.04× uniform regression trips 0 of 48 per-scenario checks and the sweep check; `optimizer.py:121 _MULTI_START_SOLVES = 2 → 4` (1.48× sweep CPU) also survives |
| D9-03 | **verify** (low) | 106 duplicate objective evaluations against 103 gradients; the one-entry cache gives 292.66 → 193.86 equivalents per gradient with all 8 published fields bit-identical |
| D9-04 | **verify** (low), title should be re-framed | 64 `simulate_dhw_only` calls / 6,624 tank steps per planning call, twice per solve; planner 1.99–4.37× a reference solve across 5 cells (the 63 % share is the maximum of five, median 0.117) |
| D9-05 | **verify** (medium), numbers to be re-stated upward | starvation share 0.951 vs an idle null of 0.000; longest hold 409–417 ms against the report's 39.4 ms; 60 % of the solve's wall inside >100 ms gaps |

Three corrections the judge should carry forward, none of which changes a
verdict:

1. **D9-01's consequence paragraph** scales from contended milliseconds.
   From the quiet re-take it is 12.2–12.8 s of M1 CPU (≈ 85–90 s on a Pi 4 at
   the stated ×7), not 18–25 s (≈ 2–3 min); and 0.67 s (≈ 4.7 s), not 0.9 s
   (≈ 6 s). The ×7 factor itself is used honestly throughout.
2. **D9-01's fix-scope note** says the golden drift may be none. Measured, the
   two-line fix moves `fuse_guard`'s `power_schedule` by up to 4.5 × 10⁻⁵ kW
   at `PRECISION = 6`, so the fixture needs re-recording. The fix is worth
   11.7–14.0× of solve CPU and keeps the pin (pinned step 0 kW on both arms).
3. **D9-05's mechanism and mitigation sentences** are wrong in detail: the
   longest holds land in pure-Python frames and in `_plan_dhw_min_cost`, not
   in the batch simulation, and they are GIL hand-off starvation (a 10×
   shorter switch interval removes them entirely for +3 % CPU);
   `time.sleep(0)` releases nothing, so it does not even shorten the holds —
   a non-zero micro-sleep does, exactly as the report predicts of `sleep(0)`.

Exposure: I read only `tools/audit/briefs/verifier.md`, `tools/audit/README.md`,
`tools/audit/briefs/D9.md`, the D9 finder's `REPORT.md` and harnesses, the
quiet-window `QUIET.md` and its D9 logs, and the tree itself. No other
verifier's output, no register verdict column, no GitHub.
