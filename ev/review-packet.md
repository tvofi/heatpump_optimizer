# Review packet #3291
head: 17e891bf00140d79e166d95901391294002b513c
base: 73365699a135fb813a43380096b6776d57f8ff4c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128672955101 neutral
arch-score / arch-score id=128690671034 success
arm id=128672631176 skipped
budget-raise-gate / budget-raise-gate id=128690700421 success
cancel-superseded id=128690707884 success
codeql id=128690705840 skipped
codeql / Analyze (actions) id=128690669364 success
codeql / Analyze (javascript-typescript) id=128690669418 success
codeql / Analyze (python) id=128690670166 cancelled
gate id=128690670687 in_progress
governance id=128690703393 skipped
governance / delivery-status id=128690669488 success
governance / delivery-status-publish id=128690669360 skipped
governance / env-matrix id=128690669584 success
governance / instrument-self-tests id=128690669636 success
governance / policy-docs id=128690669861 success
governance / record id=128690669670 skipped
governance / wave-script id=128690669515 success
hassfest id=128690694992 skipped
hassfest / hassfest id=128690669414 success
kernel-points id=128690671085 skipped
pr-contract id=128690667131 skipped
pr-contract / pr-contract id=128690671724 success
prelude id=128690699120 success
refresh id=128690696637 success
tests id=128690709159 skipped
tests / arch-instrument id=128690670041 success
tests / briefs id=128690669526 success
tests / browser id=128690670496 success
tests / ci-ratchet id=128690671177 skipped
tests / claims-autofix id=128690671068 skipped
tests / closure-scope id=128690669888 success
tests / closures id=128690670122 success
tests / closures-autofix id=128690670773 skipped
tests / coverage id=128690670198 success
tests / coverage-ratchet id=128690670835 success
tests / fast (3.14) id=128690670158 success
tests / graders-head-copy id=128690670535 success
tests / lane-proofs id=128690670919 success
tests / mutation id=128690669240 success
tests / mutation-autofix id=128690670849 skipped
tests / mutation-pins id=128690670353 skipped
tests / nightly-ha id=128690670834 skipped
tests / nightly-status id=128690669935 success
tests / replay id=128690670582 success
tests / typing id=128690669911 success
validate id=128690705280 skipped
validate / validate-hacs id=128690669299 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 17e891bf00140d79e166d95901391294002b513c lacks origin/main 6188936a8bdc58b510ecb8794ad86350283c49a7; roster read at origin/main
NOTE body item c144b573: dismissed:fixed in this diff
NOTE body item 90972501: dismissed:no in-tree input reproduces it; re-opens only from a diagnostics bundle (D15), which this group does not hold
NOTE body item 213e8a10: R10-SAV-COMFORT
NOTE body item faf3b654: dismissed:verdict robust below a 306x factor
NOTE body item 50b15e32: dismissed:the step ref is deleted after the body push
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py
             `dev/audit/harnesses/r10_partload_pricing.py` is in the tree at this head
  ok         OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_residue.py refill
             `dev/audit/harnesses/r10_partload_residue.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 73365699a HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json
new file mode 100644
index 000000000..896322f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_derated RETURN_DEL f58471d4",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    return [c * f for c, f in zip(cops, partload, strict=False)] + cops[len(partload):]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json
new file mode 100644
index 000000000..95cd9da48
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_plan_partload GUARD_OFF 259d8d5a",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    if result is None or partload_at is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 3d34ee24a..aee0ae2b8 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -351,6 +351,7 @@ from .thermal_model import (
     planned_draw_runs,
     probe_install,
     reanchor_heat_loss,
+    partload_factor,
     power_for_heat_per_cop_kw,
 )
 from .dhw_schedule import (
@@ -8309,6 +8310,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             current_state=ctx._current_state,
             result=result,
             local_tz=dt_util.DEFAULT_TIME_ZONE,
+            partload_at=partload_factor,
         )
         # Only surface the manual-plan key while an override is actually active,
         # so a plan-free solve (the golden fixtures included) is byte-for-byte
@@ -10513,9 +10515,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ctx = getattr(self, "_ctx", self)
         return wear_price_per_start(
             ctx._config.compressor_replacement_cost,
-            int(
-                ctx._config.compressor_rated_starts
-            ),
+            int(ctx._config.compressor_rated_starts),
         )
     def _effective_cycling_cost(self) -> float:
         """#55 (gated): the cycling penalty, floored by realised wear.
diff --git a/custom_components/heatpump_optimizer/wood_fuel.py b/custom_components/heatpump_optimizer/wood_fuel.py
index c732f9602..efa00e052 100644
--- a/custom_components/heatpump_optimizer/wood_fuel.py
+++ b/custom_components/heatpump_optimizer/wood_fuel.py
@@ -3,6 +3,7 @@ from __future__ import annotations
 
 from collections.abc import Callable, Iterable, Mapping, Sequence
 from datetime import datetime, timedelta, tzinfo
+from itertools import zip_longest
 from typing import Any
 
 from .drift import utc_elapsed_seconds
@@ -25,6 +26,9 @@ from .const import (
 from .const import finite_float
 from .payload import NightAdvice, WoodFuel, WoodSlot, WoodWindow
 
+# ``thermal_model.partload_factor``'s signature: (params, draw kW) -> multiplier.
+PartloadAt = Callable[[Any, float], Any]
+
 WOOD_KWH_M3 = {
     "birch": {"packed": 1900.0, "loose": 1140.0},
     "pine": {"packed": 1500.0, "loose": 900.0},
@@ -461,9 +465,8 @@ def build_wood_fuel_view(
     config: Mapping[str, Any],
     *,
     prices: list[float],
-    outdoor: list[float],
+    cops: Sequence[float],
     runs: list[bool],
-    cop_at: Callable[[float], object],
     timestamps: Sequence[datetime],
     forecast_kw: list[float],
     wood_tank_temperature: float | None = None,
@@ -472,6 +475,9 @@ def build_wood_fuel_view(
 ) -> WoodFuel:
     """Ready/cheaper/slots. cheaper is False when not ready.
 
+    ``cops`` is the per-step COP the pump buys heat at, already derated at
+    the plan's own draw (``wood_fuel_from_parts``); the view only prices it.
+
     ``forecast_kw`` is the detector's free-heat forecast, empty while it is
     not suppressing, so detected slots exist only while it suppresses.
     ``cheaper_windows`` and the lighting window are present only while
@@ -498,7 +504,6 @@ def build_wood_fuel_view(
     count = 0
     cheap: list[bool] = []
     if ready and sek is not None:
-        cops = _cops(outdoor, cop_at)
         count = cheaper_hour_count(sek, prices, cops, runs)
         if count:
             cheap = cheaper_steps(sek, prices, cops, runs)
@@ -522,8 +527,7 @@ def build_wood_fuel_view(
         config,
         prices,
         timestamps,
-        outdoor,
-        cop_at,
+        cops,
         sek,
         wood_tank_temperature,
         comfort_min,
@@ -531,6 +535,12 @@ def build_wood_fuel_view(
     return view
 
 
+def _derated(cops: list[float], partload: Sequence[float]) -> list[float]:
+    """``cops`` times each step's part-load factor; a step past ``partload``
+    (and every step, when it is empty) keeps its COP."""
+    return [c * f for c, f in zip(cops, partload, strict=False)] + cops[len(partload):]
+
+
 def _attach_windows(
     view: WoodFuel,
     config: Mapping[str, Any],
@@ -566,8 +576,7 @@ def _attach_night_advice(
     config: Mapping[str, Any],
     prices: list[float],
     timestamps: Sequence[datetime],
-    outdoor: list[float],
-    cop_at: Callable[[float], object],
+    cops: Sequence[float],
     sek: float | None,
     wood_tank_temperature: float | None,
     comfort_min: float | None,
@@ -578,12 +587,11 @@ def _attach_night_advice(
     soc = wood_tank_soc_from_probes(wood_tank_temperature, floor)
     if soc is None:
         return
-    cops = _cops(outdoor, cop_at) if outdoor else [3.0] * len(prices)
     advice = night_advice(
         now=timestamps[0],
         prices=prices,
         timestamps=timestamps,
-        cops=cops,
+        cops=list(cops) if cops else [3.0] * len(prices),
         wood_sek=sek,
         tank_soc=soc,
     )
@@ -601,6 +609,7 @@ def wood_fuel_from_parts(
     current_state: Any,
     result: Any,
     local_tz: tzinfo,
+    partload_at: PartloadAt | None = None,
 ) -> WoodFuel:
     """The published wood-fuel view from the coordinator's parts (#1739).
 
@@ -622,14 +631,39 @@ def wood_fuel_from_parts(
     return build_wood_fuel_view(
         config,
         prices=list(result.prices) if result is not None else [],
-        outdoor=list(result.outdoor_temps) if result is not None else [],
+        cops=_derated(
+            _cops(result.outdoor_temps if result is not None else [],
+                  thermal_model.compute_cop),
+            _plan_partload(thermal_params, result, partload_at),
+        ),
         runs=(
             list(result.heat_pump_on_schedule or []) if result is not None else []
         ),
-        cop_at=thermal_model.compute_cop,
         timestamps=list(result.timestamps) if result is not None else [],
         forecast_kw=forecast_kw,
         wood_tank_temperature=getattr(current_state, "wood_tank_temperature", None),
         comfort_min=getattr(opt_config, "min_temp", None),
         local_tz=local_tz,
     )
+
+
+def _plan_partload(
+    thermal_params: Any, result: Any, partload_at: PartloadAt | None
+) -> list[float]:
+    """Per step, the COP multiplier at the plan's own total draw (space plus
+    hot water): a step's pump heat is bought at ``cop * partload_factor(P)``,
+    so pricing it at ``cop`` alone under-prices it by up to ``d / (1 - d)``
+    (R10-PARTLOAD-RESIDUE). ``partload_at`` is ``thermal_model.partload_factor``,
+    passed in because ``thermal_model`` imports this module. Empty with no
+    plan or no ``partload_at``; at a 0 derate every factor is exactly 1.0, so
+    the default prices every step bit for bit as before."""
+    if result is None or partload_at is None:
+        return []
+    return [
+        float(partload_at(thermal_params, finite_float(p, 0.0) + finite_float(h, 0.0)))
+        for p, h in zip_longest(
+            result.power_schedule or [],
+            getattr(result, "dhw_power_schedule", None) or [],
+            fillvalue=0.0,
+        )
+    ]
diff --git a/dev/audit/harnesses/r10_partload_residue.py b/dev/audit/harnesses/r10_partload_residue.py
new file mode 100644
index 000000000..d362b2fdd
--- /dev/null
+++ b/dev/audit/harnesses/r10_partload_residue.py
@@ -0,0 +1,291 @@
+"""R10-PARTLOAD-RESIDUE: the solver CPU the residue of #3182 left measure-first.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py relaxed|buffer N|refill
+
+Synthetic throughout; every time is ``time.process_time`` of one process
+pinned to one core, so a Raspberry-Pi-class figure is this figure times the
+stated per-core ratio (the pull-request body derives it). The budget a solve
+is held against is the shortest optimisation interval the options flow
+accepts (``config_flow``'s ``CONF_OPTIMIZATION_INTERVAL`` slider minimum,
+10 min); the default interval is 30 min.
+
+``relaxed``: the relaxed duty-cycle pass (``optimizer._relaxed_starts``) on
+R10-SETPOINT-BOOST's 16 installs, spread and flat price days, at ``d = 0``
+and at the central plant's derate (``r10_partload_pricing.solve``). Two arms
+per cell: production, and the pass removed (``_relaxed_starts`` as
+identity, ``r10_setpoint_boost.solve``'s own perturbation). Printed: the
+seconds spent inside ``_relaxed_starts`` and how many relaxed L-BFGS-B runs
+it started, and the whole solve's seconds at both arms. Null control: the
+cells whose levels do not ship clamped must start 0 relaxed runs; the
+harness exits 1 otherwise.
+
+``buffer N``: the live buffer store's solve cost, one lever at a time:
+``r10_buffer_store.solve``'s owner shape (750 L behind a manual valve, slab,
+seeded hourly prices, outdoor -15..8 degC) at 750 L and at no buffer, each
+on the seeded spread days and on a flat day (the null: no cheap window to
+store for). Printed per arm: p50 and worst ``process_time`` over N solves.
+
+``refill``: #3182's carry 2 at a stated refill rate. ``_terminal_cost`` and
+``deferred_energy_cost`` value heat at a COP with no draw, so under a derate
+their secant error is the figure times ``P_r / heat_per_cop_kw(P_r) - 1``
+(``r10_partload_pricing.py``'s rule, which prints it only at the floor, 0,
+and at max power). The rate stated here is the plan's own: ``P_r``, the
+energy-weighted mean of the published total draw (space plus hot water)
+over its running steps, ``sum(P^2) / sum(P)``, the draw at which the plan
+bought its mean kWh. Same cells and solves as ``r10_partload_pricing.py``
+(``pp.solve``, ``pp.terminal_figure``). Printed per cell and as maxima: the
+terminal and deferred errors at ``P_r``, beside the plan's hot-water cost
+and its ``predicted_cost``. Null control: at ``d = 0`` both errors must read
+exactly 0. Positive control: at each ``d > 0`` price day the terminal and
+deferred maxima must be above 0, so an error term that drops the derate
+(``k_r = 0``) refuses instead of reading "immaterial". Exits 1 on either.
+
+``refill``'s fourth seam, ``wood``: the wood advisor (``wood_fuel``) prices a
+step's pump heat at ``price / cop``, ``cop`` the model's
+``compute_cop(outdoor)`` (``wood_fuel_from_parts``'s ``cop_at``), with no
+draw. On the same solve, the step's own published draw ``P`` (space plus hot
+water) delivers its heat at ``cop * partload_factor(P)``; a step the plan
+calls off buys nothing and keeps factor 1. The advisor's COP law is held
+(only the part-load term is the seam). Both COP lists are fed to the
+production ``cheaper_hour_count`` and ``_scan_wood_night``; the wood prices
+are a stated grid: ``WOOD_GRID`` points evenly spanning the cell's band
+from its lowest linear to its highest derated pump-heat price over its
+running steps, the band in which the two prices can disagree. Printed per cell: the largest pump-heat price error on a running
+step (currency per kWh, and relative), the largest per-wood-price shortfall
+in ``cheaper_hour_count`` (steps the advisor reads as pump-cheaper that
+derated are wood-cheaper) and its share of the running steps, and how many
+grid prices change the night scan's pick (``best_i``, ``expensive_next``).
+Null: at ``d = 0`` every wood figure must read exactly 0 (``partload_factor``
+is then 1.0, so the lists are bitwise equal). Positive control: the
+``d > 0`` price-error maximum must be above 0. The production advisor's own
+COP list (``production_cops``: ``_cops`` alone at a tree without
+``wood_fuel._plan_partload``, else derated as ``wood_fuel_from_parts`` does)
+is compared with the derated arm: the count residual and the night picks off
+read the defect at the merge base and 0 once the advisor reads the draw.
+"""
+from __future__ import annotations
+
+import sys
+import time
+
+import numpy as np
+
+sys.path.insert(0, "dev/audit/harnesses")
+
+import r10_buffer_store as bs  # noqa: E402
+import r10_cop_partload as cp  # noqa: E402
+import r10_partload_pricing as pp  # noqa: E402
+import r10_setpoint_boost as sb  # noqa: E402
+from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
+from heatpump_optimizer import wood_fuel  # noqa: E402
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel,
+    ThermalParameters,
+    heat_per_cop_kw,
+    partload_factor,
+)
+
+BUDGET_S = 10 * 60.0
+WOOD_GRID = 41
+
+
+def central_derate() -> float:
+    model = ThermalModel(ThermalParameters(
+        min_electrical_power=cp.P_MIN, max_electrical_power=cp.P_MAX))
+    eta = cp.calibrate(cp.CENTRAL, model.compute_cop(cp.OUTDOOR_C))
+    return round(1.0 - cp.plant_cop(cp.P_MAX, *cp.CENTRAL, eta)[0]
+                 / cp.plant_cop(cp.P_MIN, *cp.CENTRAL, eta)[0], 3)
+
+
+def timed_solve(cell, prices, derate: float, relaxed: bool) -> tuple[float, float, int]:
+    """(solve s, seconds inside the relaxed pass, relaxed runs started)."""
+    kept = opt_mod._relaxed_starts
+    seen = {"s": 0.0, "runs": 0}
+
+    def wrapped(opt, objective, objective_batch, bounds, first, args, cands, maxiter):
+        if not relaxed:
+            return cands
+        t = time.process_time()
+        out = kept(opt, objective, objective_batch, bounds, first, args, cands, maxiter)
+        seen["s"] += time.process_time() - t
+        seen["runs"] += len(out) - len(cands)
+        return out
+
+    opt_mod._relaxed_starts = wrapped
+    try:
+        t = time.process_time()
+        pp.solve(cell, prices, derate)
+        return time.process_time() - t, seen["s"], seen["runs"]
+    finally:
+        opt_mod._relaxed_starts = kept
+
+
+def relaxed() -> int:
+    derate = central_derate()
+    print(f"central plant derate {derate}; budget {BUDGET_S:.0f} s")
+    null_bad = 0
+    clamped_solves: list[float] = []
+    clamped_pass: list[float] = []
+    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
+        for cell in sb.CELLS:
+            for d in (0.0, derate):
+                on, inside, runs = timed_solve(cell, prices, d, True)
+                off, _, _ = timed_solve(cell, prices, d, False)
+                clamped = cell[3]
+                print(f"  {tag} {cell} d={d} clamped {clamped} relaxed_runs {runs}"
+                      f" relaxed_pass_s {inside:.3f} solve_s {on:.3f}"
+                      f" pass_removed_solve_s {off:.3f} delta_s {on - off:+.3f}")
+                if clamped:
+                    clamped_solves.append(on)
+                    clamped_pass.append(inside)
+                elif runs != 0:
+                    null_bad += 1
+    a, b = np.array(clamped_solves), np.array(clamped_pass)
+    print(f"clamped solves {a.size}: solve_s p50 {np.median(a):.3f} max {a.max():.3f};"
+          f" relaxed_pass_s p50 {np.median(b):.3f} max {b.max():.3f};"
+          f" worst solve share of budget {a.max() / BUDGET_S:.5f}")
+    print(f"null (unclamped) cells with a relaxed run {null_bad}")
+    return 1 if null_bad else 0
+
+
+def buffer(n: int) -> int:
+    for buffer_l in (750.0, 0.0):
+        for kind in ("spread", "flat"):
+            rng = np.random.default_rng(2500)
+            times = []
+            for _ in range(n):
+                hourly = rng.uniform(0.4, 3.0, size=24)
+                prices = np.repeat(hourly, 4) if kind == "spread" else bs.FLAT
+                outdoor = float(rng.uniform(-15.0, 8.0))
+                t = time.process_time()
+                bs.solve(buffer_l, prices, outdoor)
+                times.append(time.process_time() - t)
+            a = np.array(times)
+            print(f"buffer {buffer_l:.0f} L {kind}: n {n} p50_s {np.median(a):.3f}"
+                  f" max_s {a.max():.3f} worst share of budget {a.max() / BUDGET_S:.5f}")
+    return 0
+
+
+def production_cops(opt, res) -> list[float]:
+    """The COP list the production advisor prices pump heat at on this plan:
+    ``_cops`` alone where the tree has no ``_plan_partload`` (the merge
+    base), else derated as ``wood_fuel_from_parts`` derates it."""
+    lin = wood_fuel._cops(list(res.outdoor_temps), opt.model.compute_cop)
+    plan = getattr(wood_fuel, "_plan_partload", None)
+    if plan is None:
+        return lin
+    return wood_fuel._derated(lin, plan(opt.model.params, res, partload_factor))
+
+
+def wood_figures(opt, res, total) -> tuple[float, float, int, float, int, int, int]:
+    """(price error max, relative max, count shortfall max, its share of the
+    running steps, night picks changed, production count residual max,
+    production night picks off) for one solve; see ``wood``."""
+    params = opt.model.params
+    pr = np.asarray(res.prices, float)
+    runs = [bool(r) for r in (res.heat_pump_on_schedule or [False] * len(pr))]
+    lin = wood_fuel._cops(list(res.outdoor_temps), opt.model.compute_cop)
+    true = [c * float(partload_factor(params, p)) if on else c
+            for c, p, on in zip(lin, total, runs, strict=True)]
+    prod = production_cops(opt, res)
+    on_i = [i for i, on in enumerate(runs) if on and lin[i] > 0.0]
+    if not on_i:
+        return 0.0, 0.0, 0, 0.0, 0, 0, 0
+    pump_lin = np.array([pr[i] / lin[i] for i in on_i])
+    pump_true = np.array([pr[i] / true[i] for i in on_i])
+    err = pump_true - pump_lin
+    stamps = list(res.timestamps)
+    short = night = resid = prod_night = 0
+    for w in np.linspace(pump_lin.min(), pump_true.max(), WOOD_GRID):
+        w = float(w)
+        derated = wood_fuel.cheaper_hour_count(w, pr, true, runs)
+        short = max(short, derated - wood_fuel.cheaper_hour_count(w, pr, lin, runs))
+        resid = max(resid, abs(derated - wood_fuel.cheaper_hour_count(w, pr, prod, runs)))
+        scan = [wood_fuel._scan_wood_night(stamps[0], pr, stamps, c, w, len(pr))
+                for c in (lin, true, prod)]
+        night += scan[0] != scan[1]
+        prod_night += scan[2] != scan[1]
+    return (float(err.max()), float((err / pump_lin).max()), short,
+            short / len(on_i), night, resid, prod_night)
+
+
+def refill() -> int:
+    derate = central_derate()
+    print(f"central plant derate {derate}")
+    null_bad = failures = positive_bad = 0
+    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
+        for d in (0.0, derate):
+            rows = []
+            woods = []
+            for cell in sb.CELLS:
+                try:
+                    opt, res = pp.solve(cell, prices, d)
+                except Exception as err:  # counted, never dropped
+                    failures += 1
+                    print(f"  {tag} {cell} d={d} failed: {err!r}")
+                    continue
+                params = opt.model.params
+                pr = np.asarray(res.prices, float)
+                space = np.asarray(res.power_schedule, float)
+                dhw = np.asarray(res.dhw_power_schedule or [0.0] * len(pr), float)
+                total = space + dhw
+                run = total[total > 0.0]
+                p_r = float((run * run).sum() / run.sum()) if run.size else 0.0
+                k_r = p_r / heat_per_cop_kw(params, p_r) - 1.0 if p_r > 0.0 else 0.0
+                term = pp.terminal_figure(opt, res)
+                defer = float(res.deferred_energy_cost)
+                dhw_cost = float((pr * dhw).sum() * pp.DT_H)
+                pred = float(res.predicted_cost)
+                rows.append((term * k_r, abs(defer) * k_r, dhw_cost, pred,
+                             term * k_r / pred if pred > 0 else 0.0))
+                wf = wood_figures(opt, res, total)
+                woods.append(wf)
+                print(f"  {tag} {cell} d={d} P_r {p_r:.3f} k_r {k_r:.5f}"
+                      f" | terminal {term:.4f} at-P_r {term * k_r:.6f}"
+                      f" | deferred {defer:.4f} at-P_r {abs(defer) * k_r:.6f}"
+                      f" | dhw cost {dhw_cost:.4f} | predicted {pred:.4f}"
+                      f" | wood price err {wf[0]:.6f} rel {wf[1]:.5f}"
+                      f" count short {wf[2]} share {wf[3]:.4f} night changed {wf[4]}"
+                      f" | production residual {wf[5]} night off {wf[6]}")
+                if d == 0.0 and (term * k_r != 0.0 or defer * k_r != 0.0
+                                 or any(wf[:5])):
+                    null_bad += 1
+            if rows:
+                a = np.array(rows, float)
+                print(f"{tag} d={d}: cells {len(rows)} terminal-at-P_r max {a[:, 0].max():.6f}"
+                      f" deferred-at-P_r max {a[:, 1].max():.6f}"
+                      f" (dhw cost max {a[:, 2].max():.4f}, predicted max {a[:, 3].max():.4f})"
+                      f" terminal-at-P_r / predicted max {a[:, 4].max():.5f}")
+                w = np.array(woods, float)
+                print(f"{tag} d={d}: wood price err max {w[:, 0].max():.6f}"
+                      f" rel max {w[:, 1].max():.5f}; count short max {w[:, 2].max():.0f}"
+                      f" (share of running steps max {w[:, 3].max():.4f});"
+                      f" cells with a count short {int((w[:, 2] > 0).sum())};"
+                      f" night picks changed {w[:, 4].sum():.0f} of"
+                      f" {len(woods) * WOOD_GRID} (cells {int((w[:, 4] > 0).sum())})")
+                print(f"{tag} d={d}: production advisor against the derated arm:"
+                      f" count residual max {w[:, 5].max():.0f},"
+                      f" night picks off {w[:, 6].sum():.0f}")
+                if d > 0.0 and not (a[:, 0].max() > 0.0 and a[:, 1].max() > 0.0
+                                    and w[:, 0].max() > 0.0):
+                    positive_bad += 1
+    print(f"null rows not zero {null_bad}")
+    print(f"positive (d>0) price days with a zero maximum {positive_bad}")
+    print(f"failures {failures}")
+    return 1 if null_bad or failures or positive_bad else 0
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["refill"]:
+        return refill()
+    if argv[:1] == ["relaxed"]:
+        return relaxed()
+    if argv[:1] == ["buffer"]:
+        return buffer(int(argv[1]))
+    print(__doc__)
+    return 2
+
+
+if __name__ == "__main__":
+    raise SystemExit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3291.md b/dev/programme/delivery/3291.md
new file mode 100644
index 000000000..974eafcc3
--- /dev/null
+++ b/dev/programme/delivery/3291.md
@@ -0,0 +1 @@
+- [#3291](https://github.com/tvofi/heatpump_optimizer/pull/3291) — **open**, R10-PARTLOAD-RESIDUE: partload residue (R10-PARTLOAD-RESIDUE)
diff --git a/tests/closures.json b/tests/closures.json
index 0a6011505..ed9c971c2 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4108,6 +4108,7 @@
    "dev/audit/harnesses/r10_nightly_status_mutants.py",
    "dev/audit/harnesses/r10_open_driver_mutants.py",
    "dev/audit/harnesses/r10_partload_pricing.py",
+   "dev/audit/harnesses/r10_partload_residue.py",
    "dev/audit/harnesses/r10_plan_durations_mutants.py",
    "dev/audit/harnesses/r10_plan_issues_chart_mutants.py",
    "dev/audit/harnesses/r10_plan_page_mutants.py",
diff --git a/tests/features.py b/tests/features.py
index c08b186ca..e92a46843 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -44851,9 +44851,8 @@ R.check(
 _wf_not_ready = _wf_view(
     {"wood_tank_volume": 500.0},
     prices=[4.0],
-    outdoor=[-5.0],
+    cops=[2.0],
     runs=[True],
-    cop_at=lambda _t: 2.0,
     timestamps=[],
     forecast_kw=[],
 )
@@ -44969,6 +44968,34 @@ R.check(
     and _wf_off_pub["wood_fuel"].get("cheaper") is False,
     repr(_wf_off_pub.get("wood_fuel")),
 )
+# R10-PARTLOAD-RESIDUE: the published advisor prices pump heat at the derated
+# COP of the plan's own draw, wired by the coordinator (``partload_at``). The
+# step runs at max power, priced so the linear pump heat is 2 % below wood's
+# and the derated one (d = 0.1, factor 0.9) about 8.9 % above it. Null: the
+# same plan at derate 0 counts no cheaper step.
+_wf_tp = _wf_ready_coord._thermal_params
+_wf_sek = _wf_pub["wood_fuel"]["sek_per_kwh"]
+_wf_cop = float(_wf_ready_coord._thermal_model.compute_cop(-5.0))
+_wf_ready_coord._optimization_result = _wf_replace(
+    _wf_result, prices=[0.98 * _wf_sek * _wf_cop],
+    power_schedule=[_wf_tp.max_electrical_power])
+_wf_kept_derate = _wf_tp.cop_partload_derate
+_wf_partload = []
+try:
+    _dt_wf.now = lambda: NOW
+    for _wf_d in (0.1, 0.0):
+        _wf_tp.cop_partload_derate = _wf_d
+        _wf_partload.append(
+            _wf_ready_coord._build_data_dict()["wood_fuel"].get("cheaper_hour_count"))
+finally:
+    _dt_wf.now = _real_now_wf
+    _wf_tp.cop_partload_derate = _wf_kept_derate
+R.check(
+    "the published wood advisor prices a max-power step's pump heat at the "
+    "derated COP (cheaper at d = 0.1, not at d = 0; R10-PARTLOAD-RESIDUE)",
+    _wf_partload == [1, 0],
+    repr(_wf_partload),
+)
 _wf_idle = _WfOR(
     power_schedule=[0.0],
     room_temp_trajectory=[21.0, 21.0],
@@ -45004,9 +45031,8 @@ R.check(
 
 _wf_soc_kwargs = dict(
     prices=_wf_cheap_night,
-    outdoor=[0.0] * 48,
+    cops=[3.0] * 48,
     runs=[False] * 48,
-    cop_at=lambda _t: 3.0,
     timestamps=_wf_stamps,
     forecast_kw=[],
 )
@@ -45055,9 +45081,8 @@ R.check(
 _wf_skip_view = _wf_view(
     _wf_cfg,
     prices=_wf_skip_prices,
-    outdoor=[0.0] * 48,
+    cops=[3.0] * 48,
     runs=[False] * 48,
-    cop_at=lambda _t: 3.0,
     timestamps=_wf_stamps,
     forecast_kw=[],
     wood_tank_temperature=87.4,
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json
new file mode 100644
index 000000000..896322f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_derated.RETURN_DEL.f58471d4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_derated RETURN_DEL f58471d4",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    return [c * f for c, f in zip(cops, partload, strict=False)] + cops[len(partload):]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json
new file mode 100644
index 000000000..95cd9da48
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_plan_partload.GUARD_OFF.259d8d5a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_plan_partload GUARD_OFF 259d8d5a",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    if result is None or partload_at is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index b09de8666..d25f493d0 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17560,
+ "class_excess_loc": 17559,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7933,
+ "max_class_loc": 7932,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "28482eceeb6b9809e44b12d80fc994282cc21645",
+ "recorded_at": "4b5d771bdf8feb1f83d7d9443e5117b771a0ab76",
  "seam_cut_total": 423
 }
diff --git a/tests/wood_advisor.py b/tests/wood_advisor.py
index f496a546c..0e90ed366 100644
--- a/tests/wood_advisor.py
+++ b/tests/wood_advisor.py
@@ -184,9 +184,8 @@ def _wood_view(cheap_steps, off_steps=(), config=None):
     return build_wood_fuel_view(
         _WOOD_READY if config is None else config,
         prices=[4.0 if i in cheap_steps else 1.0 for i in range(n)],
-        outdoor=[0.0] * n,
+        cops=[3.0] * n,
         runs=[i not in off_steps for i in range(n)],
-        cop_at=lambda _t: 3.0,
         timestamps=_STAMPS,
         forecast_kw=[],
         local_tz=_tz.utc,
@@ -248,9 +247,8 @@ _CET = _tz(_td(hours=1))
 _local = build_wood_fuel_view(
     _WOOD_READY,
     prices=[4.0 if i in (22, 23) else 1.0 for i in range(30)],
-    outdoor=[0.0] * 30,
+    cops=[3.0] * 30,
     runs=[True] * 30,
-    cop_at=lambda _t: 3.0,
     timestamps=_STAMPS,
     forecast_kw=[],
     local_tz=_CET,
@@ -579,4 +577,98 @@ if _Env is not None:
         repr((_late_before, _late_after, _late_set)),
     )
 
+# The pump-heat price is derated at the plan's own draw (R10-PARTLOAD-RESIDUE,
+# #3182 carry 2's fourth seam). Driven through the coordinator's one entry,
+# ``wood_fuel_from_parts``, on production ``ThermalParameters``: band 1-3 kW,
+# derate 0.1, so a step drawing 3 kW delivers its heat at COP 3 * 0.9 = 2.7.
+# At 2.85 SEK/kWh the linear price is 0.95 (< wood's 1.0) and the derated one
+# 1.0556 (> 1.0): wood is cheaper there only once the draw is read. A step at
+# the 1 kW floor keeps factor 1, and derate 0 is the null. The space share
+# sits at the floor, so only the total (space plus hot water) is derated.
+from types import SimpleNamespace as _NS
+
+from heatpump_optimizer.thermal_model import ThermalParameters as _TP
+from heatpump_optimizer.thermal_model import partload_factor as _plf
+from heatpump_optimizer.wood_fuel import wood_fuel_from_parts as _from_parts
+
+
+def _parts_view(derate, space, dhw, tank=None, partload_at=_plf, n_out=None,
+                price=2.85):
+    tp = _TP(min_electrical_power=1.0, max_electrical_power=3.0,
+             cop_partload_derate=derate)
+    n = len(_STAMPS)
+    result = _NS(
+        timestamps=_STAMPS, prices=[price] * n,
+        outdoor_temps=[0.0] * (n if n_out is None else n_out),
+        heat_pump_on_schedule=[True] * n,
+        power_schedule=space, dhw_power_schedule=dhw,
+    )
+    return _from_parts(
+        _WOOD_READY, external_heat=_NS(suppressing=False),
+        opt_config=_NS(dt_hours=1.0, min_temp=20.0), thermal_params=tp,
+        thermal_model=_NS(compute_cop=lambda _t: 3.0),
+        current_state=_NS(wood_tank_temperature=tank), result=result,
+        local_tz=_tz.utc, partload_at=partload_at,
+    )
+
+
+def _count(derate, draw, **kw):
+    n = len(_STAMPS)
+    return _parts_view(derate, [1.0] * n, [draw - 1.0] * n, **kw).get(
+        "cheaper_hour_count")
+
+
+_N = len(_STAMPS)
+_wood_counts = [_count(0.1, 3.0), _count(0.1, 1.0), _count(0.0, 3.0)]
+R.check(
+    "the wood advisor prices pump heat at the derated COP of the plan's own "
+    "draw (space plus hot water): every step at max power reads wood-cheaper, "
+    "none at the floor draw, none at derate 0",
+    _wood_counts == [_N, 0, 0],
+    repr(_wood_counts),
+)
+# Edges of the draw read. 1.5 kW derates to 0.975 (0.95 / 0.975 < 1.0, not
+# cheaper) and 2.5 kW to 0.925 (1.027, cheaper), so each reading of a missing
+# draw is told apart from its alternative.
+_edges = [
+    # no partload_at (the default): the view prices at the COP alone
+    _count(0.1, 3.0, partload_at=None),
+    # a non-finite space draw is 0 kW, so the step draws its 1.5 kW hot water
+    _parts_view(0.1, [float("nan")] * _N, [1.5] * _N).get("cheaper_hour_count"),
+    # no hot-water schedule is 0 kW of hot water
+    _parts_view(0.1, [1.5] * _N, None).get("cheaper_hour_count"),
+    # a plan 6 steps shorter than the outdoor list: the tail keeps its COP
+    _parts_view(0.1, [1.0] * (_N - 6), [2.0] * (_N - 6), n_out=_N).get(
+        "cheaper_hour_count"),
+]
+R.check(
+    "the derate reads only what the plan publishes: no partload_at, a "
+    "non-finite space draw (0 kW), a missing hot-water schedule (0 kW) and "
+    "steps past the plan's schedules (no factor) price as stated",
+    _edges == [0, 0, 0, _N - 6],
+    repr(_edges),
+)
+# The night scan reads the same derated COP: a low tank (25 C over a 20 C
+# floor) is told to light only where the derated pump heat is dearer than wood.
+_night = [_parts_view(d, [1.0] * _N, [2.0] * _N, tank=25.0).get(
+    "night_advice", {}).get("action")
+          for d in (0.1, 0.0)]
+R.check(
+    "the night advice prices pump heat at the derated COP of the plan's own "
+    "draw: light at derate 0.1, no advice at derate 0",
+    _night == ["light", None],
+    repr(_night),
+)
+# With no outdoor forecast the night scan keeps its flat COP 3 (no draw read):
+# at 3.3 SEK/kWh the pump heat is 1.1, dearer than wood's 1.0, so it lights;
+# at 2.7 it is 0.9 and it does not.
+_no_out = [_parts_view(0.1, [1.0] * _N, [2.0] * _N, tank=25.0, n_out=0, price=p).get(
+    "night_advice", {}).get("action") for p in (3.3, 2.7)]
+R.check(
+    "with no outdoor forecast the night advice prices pump heat at a flat "
+    "COP of 3: light at 3.3 SEK/kWh, no advice at 2.7",
+    _no_out == ["light", None],
+    repr(_no_out),
+)
+
 sys.exit(R.close("wood-advisor checks"))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
