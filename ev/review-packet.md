# Review packet #3442
head: 9394a6528c7683f5b8b5fb19a1d939e244c515e6
base: a7628041dc02e298c5399003d4c0576391dd5c4e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=130369142820 queued
arm id=130366855914 skipped
budget-raise-gate / budget-raise-gate id=130369142716 success
cancel-superseded id=130367269319 queued
codeql id=130368635897 skipped
codeql / Analyze (actions) id=130369142893 queued
codeql / Analyze (javascript-typescript) id=130369142705 queued
codeql / Analyze (python) id=130369142746 in_progress
governance id=130368635793 skipped
governance / delivery-status id=130369142905 queued
governance / delivery-status-publish id=130369145140 skipped
governance / env-matrix id=130369142933 queued
governance / instrument-self-tests id=130369142874 queued
governance / policy-docs id=130369142787 queued
governance / record id=130369144666 skipped
governance / wave-script id=130369142895 queued
hassfest id=130368635763 skipped
hassfest / hassfest id=130369142642 queued
kernel-points id=130369144027 skipped
prelude id=130367269663 queued
refresh id=130367269515 queued
tests id=130368635479 skipped
tests / briefs id=130369142799 queued
tests / closure-scope id=130369142770 queued
tests / mutation id=130369142904 queued
tests / nightly-status id=130369142763 queued
validate id=130368636427 skipped
validate / validate-hacs id=130369142839 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item defedabb: R10-SAV-VALUATION-RESIDUE: R10-SAV-VALUATION-RESIDUE resolved on origin/handoff/audit-r10-roster
NOTE body item ea47847e: R10-SAV-VALUATION-RESIDUE: R10-SAV-VALUATION-RESIDUE resolved on origin/handoff/audit-r10-roster
NOTE body item 78bf9246: R10-SAV-VALUATION-RESIDUE: R10-SAV-VALUATION-RESIDUE resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py
             `dev/audit/harnesses/r10_partload_pricing.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_sav_valuation_residue.py
             `dev/audit/harnesses/r10_sav_valuation_residue.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat
             `dev/audit/harnesses/r10_sav_residual_attribution.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/closure.py select --diff 32aea942
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 10 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json
deleted file mode 100644
index 703fab94d0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._deferred_energy_cost RETURN_DEL b3108ffd",
-  "killed_by": "tests/plan_view.py",
-  "old": "        return float(electrical * refill_price)",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index d9250b37f3..45f71299ac 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -98,6 +98,7 @@ from .thermal_model import (
     _mean_humidity,
     _step_humidity,
     channel_heating_draw,
+    refill_power_kwh,
     channel_heating_steps,
     combi_dhw_net_series,
     combi_space_net_kw,
@@ -130,6 +131,11 @@ from .dhw_schedule import format_resolved_day_spec
 
 _LOGGER = logging.getLogger(__name__)
 
+#: The share of the horizon's cheapest steps stored heat is bought back in:
+#: the settlement's refill price is that quantile of the window's prices, and
+#: under a part-load derate its refill rate is the heat spread over that share.
+_REFILL_PRICE_QUANTILE = 0.25
+
 
 def _duty_floor(opt: HeatPumpOptimizer) -> float | None:
     """``p_min`` on a clamped install, else ``None`` (the duty-cycle reading)."""
@@ -2617,14 +2623,53 @@ def slab_settlement_cap(
     )
 
 
+def _refill_price(prices: np.ndarray) -> float:
+    """The price stored heat is bought back at: the window's
+    ``_REFILL_PRICE_QUANTILE`` price, its cheap tail, not its mean."""
+    return float(np.percentile(prices, 100.0 * _REFILL_PRICE_QUANTILE))
+
+
+def _refill_law(
+    params: ThermalParameters, n_steps: int, dt_hours: float
+) -> Callable[[float], float] | None:
+    """The part-load law both ends of the stored-heat settlement buy heat back
+    at (``_terminal_cost`` in the objective, ``_deferred_energy_cost`` in the
+    savings), or ``None`` with no derate.
+
+    The stated refill rate: the heat spread evenly over the cheapest quarter
+    of the horizon -- the hours the 25th-percentile refill price is drawn
+    from. A small refill duty-cycles at the floor and pays no derate; one
+    above it pays the band's (``refill_power_kwh``).
+    """
+    if not params.cop_partload_derate:
+        return None
+    hours = _REFILL_PRICE_QUANTILE * n_steps * dt_hours
+    return lambda heat_per_cop: refill_power_kwh(params, heat_per_cop, hours)
+
+
+def _bought_back(
+    params: ThermalParameters, heat_per_cop: float, n_steps: int, dt_hours: float
+) -> float:
+    """``heat_per_cop`` (heat over COP, kWh) as the electrical kWh
+    ``_refill_law`` buys it back at; itself with no derate."""
+    law = _refill_law(params, n_steps, dt_hours)
+    return heat_per_cop if law is None else law(heat_per_cop)
+
+
 def _terminal_row_cost(
     refill_price: float,
     cop_end: float,
     cop_buffer: float,
     stores: tuple[tuple[float, str, float, float], ...],
+    refill: Callable[[float], float] | None = None,
 ) -> tuple[Callable[[Iterable[float]], float], tuple[tuple[float, str, float], ...]]:
     """The terminal cost of ONE plan, from its end-of-horizon temperatures.
 
+    ``refill`` converts the deficit's heat over COP to the electrical kWh
+    that buys it back (``refill_power_kwh`` at the refill hours) under a
+    part-load derate; ``None`` (no derate) keeps the linear arithmetic bit
+    for bit.
+
     Returns the shared per-plan accumulation and the per-store term
     specification (``mass * survival`` folded, with the store's name and
     cap) the caller builds that plan's terms from. The terms are exact IEEE
@@ -2664,11 +2709,18 @@ def _terminal_row_cost(
                     buffer_deficit += term
                 else:
                     deficit += term
+            if refill is not None:
+                return refill_price * refill(
+                    deficit / max(cop_end, 1e-6)
+                    + buffer_deficit / max(cop_buffer, 1e-6)
+                )
             return refill_price * (
                 deficit / max(cop_end, 1e-6)
                 + buffer_deficit / max(cop_buffer, 1e-6)
             )
         deficit = sum(term_values)
+        if refill is not None:
+            return refill_price * refill(deficit / max(cop_end, 1e-6))
         return refill_price * deficit / max(cop_end, 1e-6)
 
     return row_cost, terms
@@ -2974,9 +3026,7 @@ class HeatPumpOptimizer:
         physics never charged: systematic under-charging.
         """
         caps = self._settlement_caps(outdoor_temps, humidity=humidity)
-        refill_price = (
-            float(np.percentile(prices, 25)) * self.config.price_weight
-        )
+        refill_price = _refill_price(prices) * self.config.price_weight
         # How much of what the tank holds the next window actually gets to
         # spend. Every building store settles at 1.0: their cap IS the comfort
         # target, so heat credited there is heat serving the objective
@@ -3027,7 +3077,8 @@ class HeatPumpOptimizer:
             )
 
         row_cost, term_spec = _terminal_row_cost(
-            refill_price, cop_end, cop_buffer, stores
+            refill_price, cop_end, cop_buffer, stores,
+            _refill_law(params, len(prices), self.config.dt_hours),
         )
 
         def cost(
@@ -5550,7 +5601,7 @@ class HeatPumpOptimizer:
         # percentile prices a credit, where it errs the other way and is the
         # conservative choice: heat already in store displaces whatever the next
         # window would have paid, which is the average and not the cheap tail.
-        refill_price = float(np.percentile(prices, 25))
+        refill_price = _refill_price(prices)
         electrical = stored_gap / cop
 
         # v4.0.5: the tank shares of the gap re-price at their own marginal
@@ -5586,7 +5637,7 @@ class HeatPumpOptimizer:
             if cop_store != cop:
                 gap = mass * (_capped(ref_end, store) - _capped(plan_end, store))
                 electrical += gap / cop_store - gap / cop
-        return float(electrical * refill_price)
+        return float(_bought_back(p, electrical, len(prices), self.config.dt_hours) * refill_price)
 
     def _compute_baseline_power(
         self,
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 4ec7c3ba88..a8cdad246e 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2593,6 +2593,21 @@ def power_for_heat_per_cop_kw(
     return float(power) if np.ndim(heat_per_cop) == 0 else power
 
 
+def refill_power_kwh(params: ThermalParameters, heat_per_cop_kwh: float, hours: float) -> float:
+    """The electrical kWh that buys back ``heat_per_cop_kwh`` (heat over COP)
+    as a steady draw over ``hours``: :func:`power_for_heat_per_cop_kw` at that
+    rate, so a refill above the modulation floor pays its part-load derate.
+
+    Sign-symmetric: a surplus is credited at the law a deficit is charged at.
+    The input itself while the derate is 0, bit for bit."""
+    if not params.cop_partload_derate or hours <= 0.0:
+        return heat_per_cop_kwh
+    return math.copysign(
+        power_for_heat_per_cop_kw(params, abs(heat_per_cop_kwh), hours=hours),
+        heat_per_cop_kwh,
+    )
+
+
 def added_power_for_heat_per_cop_kw(
     params: ThermalParameters, power_kw: Any, heat_per_cop: Any
 ) -> Any:
diff --git a/dev/audit/harnesses/r10_sav_residual_attribution.py b/dev/audit/harnesses/r10_sav_residual_attribution.py
new file mode 100644
index 0000000000..d87bbca253
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_residual_attribution.py
@@ -0,0 +1,77 @@
+"""R10-SAV-VALUATION-RESIDUE: the savings residual the valved arms leave, attributed.
+
+    PYTHONPATH=tests/hastub:tests:custom_components \\
+        python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat|winter_typical
+
+``r10_sav_wood_reference.closed_loop``'s valve arm (no wood, tank at 30 C,
+the arm ``valve_arm`` runs) with the plant step and the booked reference
+wrapped, never changed. Per plant step, in kWh_th: the plan's pump heat
+``cop * heat_per_cop_kw(P) * dt`` and its store change (``_stored_thermal_energy``
+next less now), so its loss; and the booked reference stepped once from its
+held state (``_thermostat_held_state`` at 21 C) at the power the harness
+booked for that step, its pump heat at ``_reference_cop`` and its store
+change, so its loss; beside the steady floor demand at 21 C and at the
+room the plan delivered (the comfort term's rule).
+
+The harness's residual is ``ref - comfort + stored - plan``. With each
+side's loss defined as its heat less its store change, the residual in
+kWh_th is ``(L_ref - L_plan - steady gap) + reference store change``: an
+identity, so its content is the two measured terms, not their sum. Both are
+the booked reference's own: the heat its booked steps draw from the held
+state's stores (a reference at equilibrium reads 0), and its loss beyond
+the steady comfort term. Precondition, asserted: the wrappers saw every
+plant step of the run (``DAYS * 24 / DT``) and a booked reference for each;
+the harness exits 1 otherwise.
+"""
+
+import sys
+sys.path.insert(0, "dev/audit/harnesses")
+import r10_sav_wood_reference as h
+from heatpump_optimizer.optimizer import (
+    _thermostat_held_state, _reference_cop, _floor_demand_at_target, WeatherSeries)
+from heatpump_optimizer.thermal_model import heat_per_cop_kw
+A = dict(q_p=0.0, ds_p=0.0, q_r=0.0, ds_r=0.0, st_r=0.0, st_p=0.0, n=0)
+orig = h._install
+def _install(wood, two_zone=True):
+    opt, model = orig(wood, two_zone)
+    real, real_base = model.simulate_step, opt._compute_baseline_power
+    last = {}
+    def base(series, state, dt, *a, **k):
+        out = real_base(series, state, dt, *a, **k)
+        if sys._getframe(1).f_code.co_name == "closed_loop":
+            last["booked"], last["series"] = float(out[0][0]), series
+        return out
+    opt._compute_baseline_power = base
+    S = opt._stored_thermal_energy
+    def step(*args, **kw):
+        if len(args) < 7 or sys._getframe(1).f_code.co_name != "closed_loop":
+            return real(*args, **kw)
+        state, power, out, wind, rain, sol, dt = args[:7]
+        nxt = real(*args, **kw)
+        cop_p = model.compute_cop(out, flow_temp=state.buffer_tank_temperature)
+        A["q_p"] += cop_p * heat_per_cop_kw(model.params, power) * dt
+        A["ds_p"] += S(nxt) - S(state)
+        series = last["series"]
+        held = _thermostat_held_state(model, state, series, 21.0)
+        b = last["booked"]
+        ref_next = real(held, b, out, wind, rain, sol, dt, **kw)
+        A["q_r"] += _reference_cop(model, held, out, None) * heat_per_cop_kw(model.params, b) * dt
+        A["ds_r"] += S(ref_next) - S(held)
+        A["st_r"] += _floor_demand_at_target(model, 21.0, out, wind, rain, sol) * dt
+        A["st_p"] += _floor_demand_at_target(model, nxt.room_temperature, out, wind, rain, sol) * dt
+        A["n"] += 1
+        return nxt
+    model.simulate_step = step
+    return opt, model
+h._install = _install
+residual_pct = h.closed_loop(False, lambda t: 0.0, None, 30.0, sys.argv[1])[1]
+print(f"harness residual {residual_pct:+.2f} %")
+L_p, L_r = A["q_p"] - A["ds_p"], A["q_r"] - A["ds_r"]
+print(f"steps {A['n']} | plan heat {A['q_p']:.2f} store change {A['ds_p']:+.2f} loss {L_p:.2f} | "
+      f"reference heat {A['q_r']:.2f} store change {A['ds_r']:+.2f} loss {L_r:.2f} | "
+      f"steady loss at 21 {A['st_r']:.2f} at delivered {A['st_p']:.2f}")
+print(f"loss gap ref-plan {L_r - L_p:+.2f} kWh_th against steady {A['st_r'] - A['st_p']:+.2f}: "
+      f"non-steady {(L_r - L_p) - (A['st_r'] - A['st_p']):+.2f}; reference stored {A['ds_r']:+.2f} kWh_th")
+want = int(h.DAYS * 24 / h.DT)
+print(f"plant steps seen {A['n']} of {want}")
+sys.exit(0 if A["n"] == want else 1)
diff --git a/dev/audit/harnesses/r10_sav_valuation_residue.py b/dev/audit/harnesses/r10_sav_valuation_residue.py
new file mode 100644
index 0000000000..e5280e98d9
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_valuation_residue.py
@@ -0,0 +1,182 @@
+"""R10-SAV-VALUATION-RESIDUE: the part-load refill pricing, against the rule it owes.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r10_sav_valuation_residue.py
+
+Synthetic throughout: ``r10_partload_pricing.solve``'s 16 installs on its
+spread and flat price days, at ``d = 0`` and at the central plant's derate
+(``r10_partload_residue.central_derate``). Three figures per solve, each the
+production figure against the tree's own part-load inverse
+(``thermal_model.power_for_heat_per_cop_kw``) applied to the same inputs:
+
+1. ``lp``: every hot-water LP the solve runs (``dhw_planner.linprog``,
+   wrapped). The LP's own valuation of the energy it bought,
+   ``c[:energy] . x[:energy]``, against what that energy costs at the draw
+   the planner publishes for it, ``sum(price * dt * P(h))`` with
+   ``h = E / (cop * dt)`` and ``P`` the inverse. The largest gap over the
+   solve's LPs, currency per day.
+2. ``terminal``: ``_terminal_cost`` on the published end state, against
+   ``refill_price * P(T_lin / refill_price, hours=H)``: ``T_lin`` the same
+   call with the derate zeroed (the linear figure), ``H`` the refill hours
+   (a quarter of the 24 h horizon, the hours the 25th-percentile refill
+   price is drawn from), sign-symmetric.
+3. ``deferred``: every ``_deferred_energy_cost`` call of the solve (wrapped),
+   re-evaluated alike: its zero-derate figure through the same rule.
+
+Null control: at ``d = 0`` all three must read 0 (``lp`` within 1e-9: the
+two valuations multiply and divide by the COP in different orders); the
+harness exits 1 otherwise. A tree that prices refill linearly reads the
+``d > 0`` terminal and deferred gaps above 0; a tree pricing it at the rule
+reads 0. ``lp`` reads the chord between segment breakpoints where the LP is
+segmented, the whole secant where it is not.
+
+Also printed per solve: ``predicted_savings``, so the flat-price day (no
+timing saving to find) shows what the derated refill moves in the savings.
+"""
+from __future__ import annotations
+
+import math
+import sys
+
+import numpy as np
+
+sys.path.insert(0, "dev/audit/harnesses")
+
+import r10_partload_pricing as pp  # noqa: E402
+import r10_partload_residue as pr  # noqa: E402
+import r10_setpoint_boost as sb  # noqa: E402
+from heatpump_optimizer import dhw_planner as planner_mod  # noqa: E402
+from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
+from heatpump_optimizer.thermal_model import power_for_heat_per_cop_kw  # noqa: E402
+
+REFILL_HOURS = 0.25 * 24.0
+NULL_TOL = 1e-9
+
+
+def rule(params, linear: float, refill_price: float) -> float:
+    """The derated refill of a linear figure: the tree's own inverse at H."""
+    # No derate: the inverse is the identity, and ``rp * (x / rp)`` need not
+    # be ``x`` to the bit, so the rule returns the figure itself.
+    if not params.cop_partload_derate or refill_price == 0.0 or linear == 0.0:
+        return linear
+    hpc = linear / refill_price
+    return refill_price * math.copysign(
+        float(power_for_heat_per_cop_kw(params, abs(hpc), hours=REFILL_HOURS)), hpc)
+
+
+def zeroed(params):
+    class _Z:
+        def __enter__(self):
+            self.d = params.cop_partload_derate
+            params.cop_partload_derate = 0.0
+
+        def __exit__(self, *exc):
+            params.cop_partload_derate = self.d
+    return _Z()
+
+
+def solve_recording(cell, prices, d):
+    lps, defers = [], []
+    real_lp = planner_mod.linprog
+    real_plan = planner_mod.DhwPlanner._plan_dhw_min_cost
+    real_cop = planner_mod.DhwPlanner._dhw_cop_profile
+    real_defer = opt_mod.HeatPumpOptimizer._deferred_energy_cost
+    seen: dict = {}
+
+    def plan(self, ctx, *a, **k):
+        seen["ctx"], seen["params"] = ctx, self.model.params
+        return real_plan(self, ctx, *a, **k)
+
+    def cop_profile(self, *a, **k):
+        seen["cop"] = out = real_cop(self, *a, **k)
+        return out
+
+    def lp(c, *a, **k):
+        res = real_lp(c, *a, **k)
+        if res.success and res.x is not None and "ctx" in seen:
+            ctx, cop = seen["ctx"], np.asarray(seen["cop"], float)
+            x, cv = np.asarray(res.x, float), np.asarray(c, float)
+            lps.append((cv, x, ctx.n_steps, ctx.dt, cop, np.asarray(ctx.prices, float), seen["params"]))
+        return res
+
+    def defer(self, *a, **k):
+        out = real_defer(self, *a, **k)
+        with zeroed(self.model.params):
+            lin = real_defer(self, *a, **k)
+        prices = a[2] if len(a) > 2 else k["prices"]
+        refill = float(np.percentile(prices, 25))
+        defers.append((out, rule(self.model.params, lin, refill)))
+        return out
+
+    planner_mod.linprog = lp
+    planner_mod.DhwPlanner._plan_dhw_min_cost = plan
+    planner_mod.DhwPlanner._dhw_cop_profile = cop_profile
+    opt_mod.HeatPumpOptimizer._deferred_energy_cost = defer
+    try:
+        opt, res = pp.solve(cell, prices, d)
+    finally:
+        planner_mod.linprog = real_lp
+        planner_mod.DhwPlanner._plan_dhw_min_cost = real_plan
+        planner_mod.DhwPlanner._dhw_cop_profile = real_cop
+        opt_mod.HeatPumpOptimizer._deferred_energy_cost = real_defer
+    return opt, res, lps, defers
+
+
+def lp_gap(entry) -> float:
+    cv, x, n, dt, cop, prices, params = entry
+    # Energy columns are the leading n-wide blocks priced below the
+    # shortfall slack, which ``_plan_dhw_min_cost`` prices at
+    # 1000 * (max |price| + 1): one block unsegmented, one per segment else.
+    slack = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)
+    blocks = 0
+    while (blocks + 1) * n <= len(cv) and np.all(cv[blocks * n:(blocks + 1) * n] < 0.5 * slack):
+        blocks += 1
+    n_e = blocks * n
+    lp_value = float(cv[:n_e] @ x[:n_e])
+    energy = x[:n_e].reshape(blocks, n).sum(axis=0)
+    draw = np.asarray(power_for_heat_per_cop_kw(params, energy / (cop * dt)), float)
+    return float((prices * draw).sum() * dt) - lp_value
+
+
+def main() -> int:
+    derate = pr.central_derate()
+    print(f"central plant derate {derate}; refill hours {REFILL_HOURS}")
+    null_bad = failures = 0
+    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
+        for d in (0.0, derate):
+            rows = []
+            for cell in sb.CELLS:
+                try:
+                    opt, res, lps, defers = solve_recording(cell, prices, d)
+                except Exception as err:  # counted, never dropped
+                    failures += 1
+                    print(f"  {tag} {cell} d={d} failed: {err!r}")
+                    continue
+                params = opt.model.params
+                lp = max((lp_gap(e) for e in lps), default=0.0)
+                term = pp.terminal_figure(opt, res)
+                with zeroed(params):
+                    term_lin = pp.terminal_figure(opt, res)
+                refill = float(np.percentile(np.asarray(res.prices, float), 25)) * opt.config.price_weight
+                term_gap = rule(params, term_lin, refill) - term
+                defer_gap = max((abs(r - o) for o, r in defers), default=0.0)
+                sav = float(res.predicted_savings)
+                rows.append((abs(lp), abs(term_gap), defer_gap))
+                print(f"  {tag} {cell} d={d} lp {lp:+.6f} ({len(lps)} LPs)"
+                      f" | terminal {term:.4f} gap {term_gap:+.6f}"
+                      f" | deferred calls {len(defers)} gap max {defer_gap:.6f}"
+                      f" | predicted_savings {sav:.4f}")
+                if d == 0.0 and (abs(lp) > NULL_TOL or term_gap != 0.0 or defer_gap != 0.0):
+                    null_bad += 1
+                    print(f"    null row off: lp {lp!r} terminal {term_gap!r} deferred {defer_gap!r}")
+            if rows:
+                a = np.array(rows, float)
+                print(f"{tag} d={d}: cells {len(rows)} lp gap max {a[:, 0].max():.6f}"
+                      f" terminal gap max {a[:, 1].max():.6f} deferred gap max {a[:, 2].max():.6f}")
+    print(f"null rows not zero {null_bad}")
+    print(f"failures {failures}")
+    return 1 if null_bad or failures else 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/dev/programme/delivery/3442.md b/dev/programme/delivery/3442.md
new file mode 100644
index 0000000000..8e8a59b844
--- /dev/null
+++ b/dev/programme/delivery/3442.md
@@ -0,0 +1 @@
+- [#3442](https://github.com/tvofi/heatpump_optimizer/pull/3442) — **open**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue (R10-SAV-VALUATION-RESIDUE)
diff --git a/tests/closures.json b/tests/closures.json
index b8209d1b40..bb1ac3dfeb 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4226,6 +4226,8 @@
    "dev/audit/harnesses/r10_sav_null_settled.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
    "dev/audit/harnesses/r10_sav_receipt_render.py",
+   "dev/audit/harnesses/r10_sav_residual_attribution.py",
+   "dev/audit/harnesses/r10_sav_valuation_residue.py",
    "dev/audit/harnesses/r10_sav_volume.py",
    "dev/audit/harnesses/r10_sav_wood_reference.py",
    "dev/audit/harnesses/r10_savings_upgrade_month.py",
diff --git a/tests/features.py b/tests/features.py
index 01608621a3..e307dc5432 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -68654,9 +68654,9 @@ for _f25_valve, _f25_kw in (
     _f25_cap = {}
     _f25_real_builder = _f21_optmod._terminal_row_cost
 
-    def _f25_cap_builder(refill, cop_end, cop_buffer, stores):
-        built = _f25_real_builder(refill, cop_end, cop_buffer, stores)
-        _f25_cap["args"] = (refill, cop_end, cop_buffer, stores)
+    def _f25_cap_builder(refill, cop_end, cop_buffer, stores, law=None):
+        built = _f25_real_builder(refill, cop_end, cop_buffer, stores, law)
+        _f25_cap["args"] = (refill, cop_end, cop_buffer, stores, law)
         _f25_cap["spec"] = built[1]
         return built
 
@@ -83203,6 +83203,82 @@ R.check(
 )
 
 
+# --- R10-SAV-VALUATION-RESIDUE: stored heat bought back at the part-load law ---
+from heatpump_optimizer import optimizer as _svr_optmod  # noqa: E402
+from heatpump_optimizer.optimizer import (  # noqa: E402
+    HeatPumpOptimizer as _SVR_OPT,
+    OptimizationConfig as _SVR_CFG,
+)
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel as _SVR_MODEL,
+    ThermalParameters as _SVR_PARAMS,
+    ThermalState as _SVR_STATE,
+    power_for_heat_per_cop_kw as _svr_inverse,
+)
+
+_SVR_HOURS = 0.25 * 96 * 0.25  # the cheapest quarter of the 24 h, 15 min horizon
+
+
+def _svr_opt(derate):
+    p = _SVR_PARAMS(min_electrical_power=0.5, max_electrical_power=6.0)
+    p.cop_partload_derate = derate
+    return _SVR_OPT(_SVR_MODEL(p), _SVR_CFG(horizon_hours=24, time_step_minutes=15)), p
+
+
+def _svr_state(t):
+    return _SVR_STATE(room_temperature=t, slab_temperature=t + 4.0, outdoor_temperature=-5.0,
+                      upper_floor_temperature=t, lower_floor_temperature=t,
+                      buffer_tank_temperature=30.0, dhw_temperature=50.0)
+
+
+def _svr_figures(derate):
+    opt, p = _svr_opt(derate)
+    prices, out = np.linspace(0.5, 2.0, 96), np.full(96, -5.0)
+    cost, batch = opt._terminal_cost(prices, out)
+    cold = np.full(96, 12.0)
+    term = cost(cold, cold, cold, cold, None)
+    row = batch({k: cold[None, :] for k in ("room", "slab", "upper", "lower", "buffer")})[0]
+    # A deficit whose refill rate sits on the band, below max power.
+    mild = np.full(96, 20.6)
+    band = cost(mild, mild, mild, mild, None)
+    warm_end, cold_end = _svr_state(21.0), _svr_state(12.0)
+    charge = opt._deferred_energy_cost(warm_end, cold_end, prices, out)
+    credit = opt._deferred_energy_cost(cold_end, warm_end, prices, out)
+    rp = float(np.percentile(prices, 25)) * opt.config.price_weight
+    return dict(term=term, band=band, row=row, charge=charge, credit=credit, rp=rp, p=p, opt=opt)
+
+
+_svr_lin, _svr_der = _svr_figures(0.0), _svr_figures(0.2)
+
+
+def _svr_law(fig, key):
+    hpc = _svr_lin[key] / fig["rp"]
+    return fig["rp"] * np.copysign(
+        float(_svr_inverse(fig["p"], abs(hpc), hours=_SVR_HOURS)), hpc)
+
+
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: under a part-load derate the terminal cost and "
+    "the deferred settlement buy stored heat back at the same law, the tree's "
+    "own inverse at the deficit spread over the cheapest quarter of the "
+    "horizon; the batch twin agrees bit for bit, a surplus is credited at the "
+    "law a deficit is charged; null control: with no derate both laws are "
+    "None and the figures are the linear ones",
+    _svr_der["term"] > _svr_lin["term"] > 0.0
+    and abs(_svr_der["term"] - _svr_law(_svr_der, "term")) <= 1e-9 * _svr_der["term"]
+    and 1.0 < _svr_der["band"] / _svr_lin["band"] < 1.0 / (1.0 - 0.2)
+    and abs(_svr_der["band"] - _svr_law(_svr_der, "band")) <= 1e-9 * _svr_der["band"]
+    and _svr_der["row"] == _svr_der["term"] and _svr_lin["row"] == _svr_lin["term"]
+    and _svr_der["charge"] > _svr_lin["charge"] > 0.0
+    and abs(_svr_der["charge"] - _svr_law(_svr_der, "charge")) <= 1e-9 * _svr_der["charge"]
+    and _svr_der["credit"] == -_svr_der["charge"]
+    and _svr_optmod._refill_law(_svr_lin["p"], 96, 0.25) is None
+    and _svr_optmod._refill_law(_svr_der["p"], 96, 0.25) is not None,
+    f"linear {({k: _svr_lin[k] for k in ('term', 'band', 'row', 'charge', 'credit')})} "
+    f"derated {({k: _svr_der[k] for k in ('term', 'band', 'row', 'charge', 'credit')})}",
+)
+
+
 # --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380, adopted by design
 # note design/R10-WATER-SETPOINT-FEEDBACK at 1442f906, approved d3623f5b):
 # a water set-point under Pump duty control was inlet + lift, re-anchored on
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json
deleted file mode 100644
index 703fab94d0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._deferred_energy_cost.RETURN_DEL.b3108ffd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._deferred_energy_cost RETURN_DEL b3108ffd",
-  "killed_by": "tests/plan_view.py",
-  "old": "        return float(electrical * refill_price)",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 3538fbe51e..a54f9365fd 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17537,
+ "class_excess_loc": 17536,
  "const_modules_over_50": 3,
  "coordinator_attrs": 139,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "0a8033305d7b03494eb63453e6181a13ffa55c05",
+ "recorded_at": "32aea942e19d36433713292ae02508e46753e932",
  "seam_cut_total": 421
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
