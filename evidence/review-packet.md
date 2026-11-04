# Review packet #3182
head: a70ca167525903076ce6b4c050bf661d96464182
base: c3a279e3252a8b57bb00b5a677318cd4fe20387f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126442414536 neutral
arch-score / arch-score id=126442097830 success
arm id=126441904371 skipped
budget-raise-gate / budget-raise-gate id=126442097897 success
cancel-superseded id=126441907897 success
codeql / Analyze (actions) id=126442097824 success
codeql / Analyze (javascript-typescript) id=126442097708 success
codeql / Analyze (python) id=126442097734 in_progress
governance / delivery-status id=126442097759 success
governance / delivery-status-publish id=126442099740 skipped
governance / env-matrix id=126442097750 success
governance / instrument-self-tests id=126442097760 in_progress
governance / policy-docs id=126442097683 success
governance / record id=126442099802 skipped
governance / wave-script id=126442097860 success
hassfest / hassfest id=126442097570 success
kernel-points id=126442099185 skipped
prelude id=126441907708 in_progress
refresh id=126441908004 success
tests / arch-instrument id=126442264893 success
tests / briefs id=126442097701 success
tests / browser id=126442265111 success
tests / closure-scope id=126442097748 success
tests / closures id=126442264877 in_progress
tests / coverage id=126442264985 success
tests / coverage-ratchet id=126449191005 success
tests / fast (3.14) id=126442265027 in_progress
tests / graders-head-copy id=126449191105 success
tests / mutation id=126442097771 success
tests / mutation-autofix id=126442391569 skipped
tests / mutation-pins id=126442390723 skipped
tests / nightly-ha id=126442267315 skipped
tests / nightly-status id=126442097671 failure
tests / replay id=126442266627 skipped
tests / typing id=126442264880 success
validate / validate-hacs id=126442097785 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 1d9a7299: dismissed:already held open on this group's roster entry at index 0
NOTE body item d8a6c4d1: dismissed:already held open on this group's roster entry at index 2, which this pull request does not close; landing a duplicate is the standing-roster seat's
NOTE body item 63c1186f: dismissed:already held open on this group's roster entry at index 0, which this pull request does not close; landing a duplicate is the standing-roster seat's
NOTE body item cc687355: dismissed:already held open on this group's roster entry at index 6, which this pull request does not close; landing a duplicate is the standing-roster seat's
NOTE body item 99d6f6f5: dismissed:a session-local plugin, not repository policy
NOTE body item 08ca5c73: dismissed:reported to the orchestrator in this body
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py
             `dev/audit/harnesses/r10_partload_pricing.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_buffer_store.py bench 3
             `dev/audit/harnesses/r10_buffer_store.py` is in the tree at this head
  ok         bash tools/audit/seat/cloud-setup.sh
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  unverified python3 -c 'import numpy,scipy;print(...)'
             python3 runs an inline script rather than a file
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified git grep -nE "c_buf *= *0\.04|0\.04 if c_buf" -- custom_components/heatpump_optimizer/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "0\.04" -- custom_components/heatpump_optimizer/optimizer.py | wc -l
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 9 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json
deleted file mode 100644
index 1ee2631f5..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._substeps_and_loss CMP_BOUND e26455a8",
-  "killed_by": "tests/features.py",
-  "old": "                if c_buf < 1e-6:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if c_buf <= 1e-6:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json
deleted file mode 100644
index 0c24dd4c5..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._substeps_and_loss GUARD_OFF e26455a8",
-  "killed_by": "tests/features.py",
-  "old": "                if c_buf < 1e-6:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 4cd323f61..759a83171 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -3777,10 +3777,7 @@ class ThermalModel:
                 ua_floor = (
                     (1.0 - p.radiator_power_fraction) * design_power / design_dt
                 )
-                c_buf = p.buffer_tank_thermal_mass
-                if c_buf < 1e-6:
-                    c_buf = 0.04  # the step's own fallback
-                buf_row = design_power / design_dt / c_buf
+                buf_row = design_power / design_dt / _buffer_capacity(p)
             worst = max(
                 (u_upper + p.inter_zone_transfer + ua_rad)
                 / p.upper_floor_thermal_mass,
diff --git a/dev/audit/harnesses/r10_partload_pricing.py b/dev/audit/harnesses/r10_partload_pricing.py
new file mode 100644
index 000000000..00348fc66
--- /dev/null
+++ b/dev/audit/harnesses/r10_partload_pricing.py
@@ -0,0 +1,202 @@
+"""R10-PARTLOAD-PRICING: how far do the linear and mean-draw cost laws sit
+from the part-load derate they ignore?
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r10_partload_pricing.py
+
+Synthetic throughout. The scenarios are ``r10_cop_partload.py``'s solves:
+R10-SETPOINT-BOOST's 16 installs on its spread and flat price days, at
+``d = 0`` and at the central plant's own derate. Two measurements, each with
+a zero-derate null control that must read exactly 0 (no change):
+
+1. ``linear`` (carry 2): heat priced linearly at a COP.
+   - ``lp``: the hot-water LP's objective ``price * E / cop`` on the plan it
+     published, against the per-step derated price. The published draw ``P``
+     delivers ``cop * heat_per_cop_kw(P)``, which the objective valued at
+     ``price * heat_per_cop_kw(P)``; the error is
+     ``sum(price * (P - heat_per_cop_kw(P)) * dt)``, currency per day.
+   - ``terminal`` and ``deferred``: ``_terminal_cost`` on the published end
+     state and the reported ``deferred_energy_cost``. Neither states a refill
+     rate; at a stated rate ``P_r`` the secant error is the figure times
+     ``P_r / heat_per_cop_kw(P_r) - 1``: 0 at the floor, ``d / (1 - d)`` at
+     max power. Both bounds are printed.
+2. ``meandraw`` (carry 3): the always-hot baseline (``_baseline_dhw_economics``)
+   and the setpoint sweep (``_dhw_setpoint_sweep``) price a day's hot water
+   as a steady mean draw. Each is re-run with its own module's
+   ``power_for_heat_per_cop_kw`` swapped, for that call only, for the run-power
+   law ``E * P_run / heat_per_cop_kw(P_run)`` (``P_run``: the published hot-
+   water plan's own peak draw). Printed: the baseline cost change and the
+   sweep's chosen setpoint at both laws. At ``d = 0`` the swapped law is
+   ``E * 1.0``, so the null is bitwise.
+"""
+from __future__ import annotations
+
+import sys
+from types import SimpleNamespace
+
+import numpy as np
+
+sys.path.insert(0, "dev/audit/harnesses")
+
+import r10_cop_partload as cp  # noqa: E402
+import r10_setpoint_boost as sb  # noqa: E402
+from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
+from heatpump_optimizer import dhw_planner as planner_mod  # noqa: E402
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel,
+    ThermalParameters,
+    heat_per_cop_kw,
+)
+
+DT_H = 0.25
+
+
+def run_power_law(p_run: float):
+    """``power_for_heat_per_cop_kw``'s signature, pricing at ``p_run``."""
+    def law(params, heat_per_cop, hours: float = 1.0):
+        return heat_per_cop * (p_run / heat_per_cop_kw(params, p_run))
+    return law
+
+
+def solve(cell, prices, derate: float):
+    """``r10_cop_partload.solve``, keeping the optimizer for its terminal."""
+    loss, buffer_l, dhw, rounded = cell
+    p = ThermalParameters()
+    if buffer_l:
+        p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
+    p.min_electrical_power, p.max_electrical_power = sb.CFG_MIN, sb.CFG_MAX
+    p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
+    p.cop_partload_derate = derate
+    opt = sb.HeatPumpOptimizer(
+        ThermalModel(p), sb.OptimizationConfig(clamp_planned_levels=rounded))
+    res = opt.optimize(inputs=sb.solve_inputs(
+        initial_state=sb.ThermalState(
+            room_temperature=20.0, upper_floor_temperature=20.0,
+            lower_floor_temperature=20.0, slab_temperature=20.5,
+            outdoor_temperature=5.0, buffer_tank_temperature=24.0,
+            dhw_temperature=48.0,
+        ),
+        prices=prices, outdoor_temps=np.full(96, 5.0), start_time=sb.T0,
+    ))
+    return opt, res
+
+
+def terminal_figure(opt, res) -> float:
+    cost, _ = opt._terminal_cost(np.asarray(res.prices, float), np.full(96, 5.0))
+    room = np.asarray(res.room_temp_trajectory, float)
+    upper = np.asarray(res.upper_temp_trajectory or room, float)
+    lower = np.asarray(res.lower_temp_trajectory or room, float)
+    buf = (np.asarray(res.buffer_temp_trajectory, float)
+           if res.buffer_temp_trajectory else None)
+    return float(cost(room, np.asarray(res.slab_temp_trajectory, float),
+                      upper, lower, buf))
+
+
+def sweep(params: ThermalParameters, prices, law=None) -> int | None:
+    """The production sweep on a stub coordinator: no learned draws."""
+    model = ThermalModel(params)
+    stub = SimpleNamespace(
+        _thermal_params=params,
+        _current_state=SimpleNamespace(outdoor_temperature=5.0),
+        _prices=list(prices),
+        _dhw_learner=SimpleNamespace(
+            draw_stats=SimpleNamespace(quantile=lambda *_: None)),
+        _thermal_model=model,
+    )
+    orig = coord_mod.power_for_heat_per_cop_kw
+    if law is not None:
+        coord_mod.power_for_heat_per_cop_kw = law
+    try:
+        out = coord_mod.HeatPumpOptimizerCoordinator._dhw_setpoint_sweep(
+            stub, float(np.mean(prices)))
+    finally:
+        coord_mod.power_for_heat_per_cop_kw = orig
+    return out.get("recommended_setpoint"), out.get("candidates")
+
+
+def baseline_at(cell, prices, derate: float, law) -> float:
+    """The solve's ``baseline_cost`` with the baseline's law swapped."""
+    orig_fn = planner_mod.DhwPlanner._baseline_dhw_economics
+    orig_law = planner_mod.power_for_heat_per_cop_kw
+
+    def wrapped(self, *a, **k):
+        planner_mod.power_for_heat_per_cop_kw = law
+        try:
+            return orig_fn(self, *a, **k)
+        finally:
+            planner_mod.power_for_heat_per_cop_kw = orig_law
+
+    planner_mod.DhwPlanner._baseline_dhw_economics = wrapped
+    try:
+        return float(solve(cell, prices, derate)[1].baseline_cost)
+    finally:
+        planner_mod.DhwPlanner._baseline_dhw_economics = orig_fn
+
+
+def main() -> int:
+    model = ThermalModel(ThermalParameters(
+        min_electrical_power=cp.P_MIN, max_electrical_power=cp.P_MAX))
+    eta = cp.calibrate(cp.CENTRAL, model.compute_cop(cp.OUTDOOR_C))
+    derate = round(1.0 - cp.plant_cop(cp.P_MAX, *cp.CENTRAL, eta)[0]
+                   / cp.plant_cop(cp.P_MIN, *cp.CENTRAL, eta)[0], 3)
+    print(f"central plant derate {derate}")
+    failures = 0
+    null_bad = 0
+    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
+        rows: dict[float, list[tuple]] = {0.0: [], derate: []}
+        for cell in sb.CELLS:
+            for d in (0.0, derate):
+                try:
+                    opt, res = solve(cell, prices, d)
+                except Exception as err:  # counted, never dropped
+                    failures += 1
+                    print(f"  {tag} {cell} d={d} failed: {err!r}")
+                    continue
+                params = opt.model.params
+                pr = np.asarray(res.prices, float)
+                dhw = np.asarray(res.dhw_power_schedule or [0.0] * len(pr), float)
+                dhw_cost = float((pr * dhw).sum() * DT_H)
+                lp_err = float((pr * (dhw - heat_per_cop_kw(params, dhw))).sum() * DT_H)
+                term = terminal_figure(opt, res)
+                defer = float(res.deferred_energy_cost)
+                top = params.max_electrical_power
+                k_max = top / heat_per_cop_kw(params, top) - 1.0
+                p_run = float(dhw.max()) if dhw.size and dhw.max() > 0 else top
+                k_run = p_run / heat_per_cop_kw(params, p_run) - 1.0
+                base = float(res.baseline_cost)
+                base_err = base_run = 0.0
+                sp_mean = sp_run = None
+                if cell[2]:
+                    base_run = baseline_at(cell, prices, d, run_power_law(p_run))
+                    base_err = base_run - base
+                    sp_mean, _ = sweep(params, prices)
+                    sp_run, _ = sweep(params, prices, run_power_law(p_run))
+                rows[d].append((lp_err, dhw_cost, term * k_max, abs(defer) * k_max,
+                                base_err, base, sp_mean, sp_run))
+                print(f"  {tag} {cell} d={d} lp_err {lp_err:.6f} of dhw {dhw_cost:.4f}"
+                      f" | terminal {term:.4f} at-max {term * k_max:.6f}"
+                      f" | deferred {defer:.4f} at-max {abs(defer) * k_max:.6f}"
+                      f" | P_run {p_run:.3f} k_run {k_run:.5f}"
+                      f" | baseline {base:.4f} run-power {base_run:.4f} change {base_err:+.6f}"
+                      f" | sweep {sp_mean} -> {sp_run}")
+                if d == 0.0 and (lp_err != 0.0 or term * k_max != 0.0
+                                 or base_err != 0.0 or sp_mean != sp_run):
+                    null_bad += 1
+        for d, st in rows.items():
+            if not st:
+                continue
+            a = np.array([r[:6] for r in st], float)
+            moved = sum(1 for r in st if r[6] != r[7])
+            print(f"{tag} d={d}: cells {len(st)} lp_err max {a[:, 0].max():.6f}"
+                  f" (dhw cost max {a[:, 1].max():.4f})"
+                  f" terminal-at-max max {a[:, 2].max():.6f}"
+                  f" deferred-at-max max {a[:, 3].max():.6f}"
+                  f" baseline change min {a[:, 4].min():+.6f} max {a[:, 4].max():+.6f}"
+                  f" sweep setpoint moved {moved}")
+    print(f"null rows not zero {null_bad}")
+    print(f"failures {failures}")
+    return 1 if failures or null_bad else 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/dev/programme/delivery/3182.md b/dev/programme/delivery/3182.md
new file mode 100644
index 000000000..59a0fad9f
--- /dev/null
+++ b/dev/programme/delivery/3182.md
@@ -0,0 +1 @@
+- [#3182](https://github.com/tvofi/heatpump_optimizer/pull/3182) — **open**, R10-PARTLOAD-PRICING: partload pricing (R10-PARTLOAD-PRICING)
diff --git a/tests/closures.json b/tests/closures.json
index 227abacdf..dbb08c723 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4003,6 +4003,7 @@
    "dev/audit/harnesses/r10_nightly_pyspy_retry.py",
    "dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py",
    "dev/audit/harnesses/r10_open_driver_mutants.py",
+   "dev/audit/harnesses/r10_partload_pricing.py",
    "dev/audit/harnesses/r10_plan_durations_mutants.py",
    "dev/audit/harnesses/r10_plan_issues_chart_mutants.py",
    "dev/audit/harnesses/r10_plan_page_mutants.py",
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json
deleted file mode 100644
index 1ee2631f5..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.CMP_BOUND.e26455a8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._substeps_and_loss CMP_BOUND e26455a8",
-  "killed_by": "tests/features.py",
-  "old": "                if c_buf < 1e-6:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if c_buf <= 1e-6:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json
deleted file mode 100644
index 0c24dd4c5..000000000
--- a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.e26455a8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._substeps_and_loss GUARD_OFF e26455a8",
-  "killed_by": "tests/features.py",
-  "old": "                if c_buf < 1e-6:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 535a68042..a6e68505b 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17640,
+ "class_excess_loc": 17637,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "1a8051350406387d5ee1ed966d8a2ba8a770cc31",
+ "recorded_at": "c3a279e3252a8b57bb00b5a677318cd4fe20387f",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
