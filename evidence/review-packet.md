# Review packet #3291
head: d5f8f410c40476f22f06099ceeabd90f1351dd71
base: 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128451845352 success
arch-score / arch-score id=128452553318 success
arm id=128450138870 skipped
budget-raise-gate / budget-raise-gate id=128452553167 success
cancel-superseded id=128450559358 success
codeql id=128452554727 skipped
codeql / Analyze (actions) id=128451039977 success
codeql / Analyze (javascript-typescript) id=128451039951 success
codeql / Analyze (python) id=128451039960 success
gate id=128454048061 failure
governance id=128452554081 skipped
governance / delivery-status id=128451039989 success
governance / delivery-status-publish id=128451041161 skipped
governance / env-matrix id=128451039987 success
governance / instrument-self-tests id=128451039876 in_progress
governance / policy-docs id=128451039994 success
governance / record id=128451041186 skipped
governance / wave-script id=128451039958 success
hassfest id=128452554681 skipped
hassfest / hassfest id=128451039904 success
kernel-points id=128452553866 skipped
pr-contract id=128454048693 skipped
prelude id=128450559386 success
refresh id=128450559131 success
tests id=128452554521 skipped
tests / arch-instrument id=128451511092 success
tests / briefs id=128451039934 success
tests / browser id=128451511011 success
tests / claims-autofix id=128456991186 skipped
tests / closure-scope id=128451039854 success
tests / closures id=128451511066 in_progress
tests / coverage id=128451511001 in_progress
tests / fast (3.14) id=128451511022 success
tests / mutation id=128451039969 success
tests / mutation-autofix id=128452956746 skipped
tests / mutation-pins id=128452955679 skipped
tests / nightly-ha id=128451512246 skipped
tests / nightly-status id=128451039899 failure
tests / replay id=128451512309 skipped
tests / typing id=128451511064 success
validate id=128452554067 skipped
validate / validate-hacs id=128451039910 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at d5f8f410c40476f22f06099ceeabd90f1351dd71

## Advisories
none

## carry_audit at the head
NOTE body item 955a8a8f: dismissed:verdict robust below a 306x factor
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff b4ec2f332 --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_partload_residue.py b/dev/audit/harnesses/r10_partload_residue.py
new file mode 100644
index 000000000..d8f07d68f
--- /dev/null
+++ b/dev/audit/harnesses/r10_partload_residue.py
@@ -0,0 +1,135 @@
+"""R10-PARTLOAD-RESIDUE: the solver CPU the residue of #3182 left measure-first.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py relaxed|buffer N
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
+from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
+
+BUDGET_S = 10 * 60.0
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
+def main(argv: list[str]) -> int:
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
index e0693316d..2fc9862a3 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4071,6 +4071,7 @@
    "dev/audit/harnesses/r10_nightly_status_mutants.py",
    "dev/audit/harnesses/r10_open_driver_mutants.py",
    "dev/audit/harnesses/r10_partload_pricing.py",
+   "dev/audit/harnesses/r10_partload_residue.py",
    "dev/audit/harnesses/r10_plan_durations_mutants.py",
    "dev/audit/harnesses/r10_plan_issues_chart_mutants.py",
    "dev/audit/harnesses/r10_plan_page_mutants.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
