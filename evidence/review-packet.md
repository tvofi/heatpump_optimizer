# Review packet #3174
head: 8e47d727c1024728ab3ab23c4aefa01a866dcf78
base: ea59e9a09de56447326ae71d8a45fec81c3cc275

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125418541343 neutral
arch-score / arch-score id=125418086695 success
arm id=125417851333 skipped
budget-raise-gate / budget-raise-gate id=125418086965 success
cancel-superseded id=125417859644 success
codeql / Analyze (actions) id=125418086856 success
codeql / Analyze (javascript-typescript) id=125418087058 success
codeql / Analyze (python) id=125418086871 in_progress
governance / delivery-status id=125418086625 success
governance / delivery-status-publish id=125418089184 skipped
governance / env-matrix id=125418086572 in_progress
governance / instrument-self-tests id=125418086497 in_progress
governance / policy-docs id=125418086445 success
governance / record id=125418089993 skipped
governance / wave-script id=125418086362 success
hassfest / hassfest id=125418086525 success
kernel-points id=125418090355 skipped
prelude id=125417861876 in_progress
refresh id=125417861837 success
tests / arch-instrument id=125418412978 success
tests / briefs id=125418086606 success
tests / browser id=125418412128 in_progress
tests / closure-scope id=125418086551 success
tests / closures id=125418412898 in_progress
tests / coverage id=125418412471 in_progress
tests / fast (3.14) id=125418412143 in_progress
tests / mutation id=125418086677 success
tests / mutation-autofix id=125418402985 skipped
tests / mutation-pins id=125418401606 skipped
tests / nightly-ha id=125418418878 skipped
tests / nightly-status id=125418086935 success
tests / replay id=125418412297 in_progress
tests / typing id=125418412299 success
validate / validate-hacs id=125418086842 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs
             gh api: every long flag accepted
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3174.md b/dev/programme/delivery/3174.md
new file mode 100644
index 000000000..21fb30bbf
--- /dev/null
+++ b/dev/programme/delivery/3174.md
@@ -0,0 +1 @@
+- [#3174](https://github.com/tvofi/heatpump_optimizer/pull/3174) — **open**, R10-REPLAY-COST-BUDGET: replay cost budget (R10-REPLAY-COST-BUDGET)
diff --git a/tests/replay.py b/tests/replay.py
index e98f66930..d29f875f5 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -465,14 +465,61 @@ COST_DETECTION = 2.0
 #: 217.8-290.5, each edge 18-22 % inside; a loaded M1 (177-394, load average
 #: 30-200) spans more than a 2x band holds and is left out. ``peak_kib`` and
 #: ``loop_cpu_ratio`` over all four environments, the M1 included: 2514-2783
-#: and 0.137-0.227, the loop's edges 9-10 % inside. One CI class only: the
-#: R10-REPLAY-LANE carry asks for both, so re-centre when the other class reads.
+#: and 0.137-0.227, the loop's edges 9-10 % inside.
+#: Re-centred (R10-REPLAY-COST-BUDGET) on the readings the CI ``replay`` job
+#: and nightly.yml ``slow`` take, from their own ``cost`` lines, and on
+#: nothing a reviewer's or author's box read. Owner fixture ``cpu_ratio``
+#: 235.8, 240.7 (ref_ms 30: job 125240101580 of run 41434115932, #3174; job
+#: 125160076828 of run 41405222589, #3167), 241.9, 246.0 (ref_ms 46: job
+#: 125097530406 of run 41389413359, #3078; job 125316010511, #3174): sqrt(2)
+#: x the geometric midpoint of 235.8 and 241.9 is 337.8, every reading 70-73 %
+#: of it; the ref_ms 53 class has not replayed it. Synthetic ``loop_cpu_ratio``
+#: 0.0901-0.1026 over all seven jobs below, every class: 0.1278, each
+#: ``loop doubled`` arm (0.179-0.2015) over it. A box outside every class
+#: reads the loop figure higher at the same code (4 cores, ``loop_ref_ms``
+#: 87: 0.175; the reviewer's, 85-99: 0.152-0.191); the lane never runs on one.
+#: ``peak_kib`` and the owner fixture's ``loop_cpu_ratio`` stay. Synthetic
+#: ``cpu_ratio`` is keyed by runner class, ``COST_CLASS_BUDGETS``.
 COST_BUDGETS: dict[str, dict[str, float]] = {
-    "synthetic-dhw-only.json": {"cpu_ratio": 2.173, "peak_kib": 2686.0,
-                                "loop_cpu_ratio": 0.143},
-    "owner-2026-10-30-away.json": {"cpu_ratio": 355.7, "peak_kib": 3740.0,
+    "synthetic-dhw-only.json": {"peak_kib": 2686.0, "loop_cpu_ratio": 0.1278},
+    "owner-2026-10-30-away.json": {"cpu_ratio": 337.8, "peak_kib": 3740.0,
                                    "loop_cpu_ratio": 0.249},
 }
+#: Runner classes, by the run's own BLAS ruler: its median reference-solve
+#: ms, the ``ref_ms`` its ``cost`` line prints -- never a runner's name. One
+#: synthetic ``cpu_ratio`` cannot serve them: the classes read 1.45-2.81 at
+#: the same code, more than the 2x one band holds. Each band is its ``ref_ms``
+#: readings (every clean and doubled run of the jobs cited in
+#: ``COST_CLASS_READINGS``) widened 5 % each way, the within-job spread being
+#: 2.4-3.2 %; the bands are disjoint. A run in no band is refused by name
+#: (``class_budget``), never graded against a neighbour's budget.
+COST_RUNNER_CLASSES: dict[str, tuple[float, float]] = {
+    "ref30": (28.72, 32.69),
+    "ref46": (42.99, 49.51),
+    "ref53": (49.60, 56.78),
+}
+#: Per fixture and runner class, the budgets that differ by class: sqrt(2) x
+#: the geometric midpoint of that class's clean readings in
+#: ``COST_CLASS_READINGS``, every reading 69-72 % of its class's budget.
+COST_CLASS_BUDGETS: dict[str, dict[str, dict[str, float]]] = {
+    "synthetic-dhw-only.json": {"ref30": {"cpu_ratio": 3.934},
+                                "ref46": {"cpu_ratio": 3.357},
+                                "ref53": {"cpu_ratio": 2.081}},
+}
+#: The lane readings each class budget is centred on: per cited job, its
+#: ``ref_ms``, clean ``cpu_ratio`` and ``cpu doubled`` arm, from its ``cost``
+#: lines. ref30: jobs 125160076828 (#3167), 125240101580 (#3174); ref46: jobs
+#: 125097530406 (#3078), 125316010511 (#3174); ref53: nightly.yml ``slow``
+#: jobs 124414072168 (run 41159630948), 124725704090 (run 41264951784),
+#: 125036077984 (run 41369286061). A re-record appends its job here; the
+#: ``cycle_cost:class_budgets`` control holds every clean reading inside its
+#: class's band and every doubled arm over it.
+COST_CLASS_READINGS: dict[str, list[tuple[float, float, float]]] = {
+    "synthetic-dhw-only.json": [
+        (30.32, 2.81, 5.701), (30.93, 2.7543, 5.5315),
+        (45.65, 2.3246, 4.6473), (46.36, 2.4235, 4.7775),
+        (52.76, 1.4563, 2.8848), (53.27, 1.451, 2.841), (52.43, 1.4926, 2.9251)],
+}
 #: Fixtures the lane replays once, clean, without the three doubled-cost
 #: arms: each arm is a whole replay, and a fixture whose replay costs a large
 #: share of the lane's job time cannot be run four times inside it (the
@@ -587,6 +634,22 @@ def cost_offenders(figures: dict[str, float], budget: dict[str, float] | None,
     return out
 
 
+def class_budget(name: str, ref_ms: float) -> tuple[dict[str, float] | None, list[str]]:
+    """``name``'s budget on the runner class ``ref_ms`` falls in, and the
+    refusal when a fixture keyed by class ran in no class's band: no default
+    and no neighbour's budget is assumed."""
+    keyed = COST_CLASS_BUDGETS.get(name)
+    if keyed is None:
+        return COST_BUDGETS.get(name), []
+    runner = next((c for c, (lo, hi) in COST_RUNNER_CLASSES.items()
+                   if lo <= ref_ms <= hi and c in keyed), None)
+    if runner is None:
+        return None, [f"runner class unknown: ref_ms {ref_ms:.4g} lies in no band of "
+                      f"COST_RUNNER_CLASSES {sorted(COST_RUNNER_CLASSES.values())}; "
+                      "no budget is assumed"]
+    return {**COST_BUDGETS.get(name, {}), **keyed[runner]}, []
+
+
 def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
     """``COST_ARMS_SKIPPED`` naming a fixture not committed, or every one: the
     doubled-cost arms must still run on some fixture of the full lane."""
@@ -597,6 +660,15 @@ def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
     return out
 
 
+def away_covered_offenders(covered: frozenset[str] | set[str],
+                           committed: set[str]) -> list[str]:
+    """``AWAY_COVERED`` naming a fixture that is not committed: a misspelt
+    name declares coverage no fixture carries, and ``away_coverage_offenders``
+    would never see it."""
+    return [f"{name}: declares away coverage but is not a committed fixture"
+            for name in sorted(covered - committed)]
+
+
 def short_doubling(injected_ratio: float) -> list[str]:
     """A perturbation arm that burnt less than the clean span its metric
     times is no doubling (#2205: the cpu arm spun the update alone, ~0.93)."""
@@ -732,12 +804,33 @@ def controls() -> list[tuple[str, bool, str]]:
         [20.0, 22.0], [r * 3 for r in ref], [4096])["cpu_ratio"]
     res.append(("control:cycle_cost:cpu_normaliser", cpu_solve_moved,
                 f"cpu_ratio {clean['cpu_ratio']}: solve x3 moved={cpu_solve_moved}"))
+    # Runner classes (R10-REPLAY-COST-BUDGET): each class's budget holds its
+    # own lane readings in band and sees its own doubled arm; one budget for
+    # every class could not. A ruler in no band is refused, by name.
+    syn = "synthetic-dhw-only.json"
+    off = [(ref_ms, cost_offenders({"cpu_ratio": c}, class_budget(syn, ref_ms)[0]),
+            cost_offenders({"cpu_ratio": d}, class_budget(syn, ref_ms)[0]))
+           for ref_ms, c, d in COST_CLASS_READINGS[syn]]
+    res.append(("control:cycle_cost:class_budgets",
+                all(not c and any("over its budget" in o for o in d) for _, c, d in off),
+                str([(r, c[:1], d[:1]) for r, c, d in off if c or not d])))
+    lo30, hi46 = COST_RUNNER_CLASSES["ref30"][1], COST_RUNNER_CLASSES["ref46"][0]
+    unknown = [class_budget(syn, x) for x in ((lo30 + hi46) / 2, float("nan"))]
+    pair("cycle_cost:runner_class_unknown",
+         [m for b, r in unknown if b is None for m in r if m.startswith("runner class unknown")]
+         if all(r for _, r in unknown) else [],
+         class_budget(syn, COST_CLASS_READINGS[syn][0][0])[1])
     pair("cycle_cost:arms_skipped_never_everywhere",
          arms_skip_offenders({"a.json", "b.json"}, {"a.json", "b.json"}),
          arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
     pair("cycle_cost:arms_skipped_committed_only",
          arms_skip_offenders({"gone.json"}, {"a.json"}),
          arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
+    pair("away:covered_names_are_committed",
+         away_covered_offenders({"owner-2026-10-30-awya.json"},
+                                {"owner-2026-10-30-away.json"}),
+         away_covered_offenders({"owner-2026-10-30-away.json"},
+                                {"owner-2026-10-30-away.json"}))
     pair("cycle_cost:short_doubling", short_doubling(0.93), short_doubling(1.0001))
     pair("cycle_cost:unmetered_doubling", short_doubling(float("nan")), short_doubling(1.0))
     held = {"t": "t", "commanded_return": "r", "active": True, "override": True,
@@ -1212,6 +1305,14 @@ def recorder_checks() -> list[tuple[str, bool, str]]:
                     and "core-mariadb" not in said_url and marked.name not in said_url
                     and len(_CANARY_KEY) > 3 and len(_CANARY_USER) > 3,
                     "the URL branch's stderr searched for the user, password and host"))
+        # The unsupported-scheme refusal names neither the URL nor any part of
+        # it; a URL without credentials reads the same text (the null).
+        _, bad = _export_mariadb(None, tmp, db_url=f"ftp://{_CANARY_USER}:{_CANARY_KEY}@core-mariadb/x")
+        _, plain = _export_mariadb(None, tmp, db_url="ftp://core-mariadb/x")
+        res.append(("recorder:unsupported_scheme_refusal_prints_none_of_the_url",
+                    "neither SQLite nor" in bad
+                    and not any(c in bad for c in (_CANARY_KEY, _CANARY_USER, "core-mariadb", "ftp:"))
+                    and bad == plain, bad[-200:]))
         flag, _ = _export_mariadb(fake, tmp, db_url=_DB_URL.replace("homeassistant", "hadb"))
         res.append(("recorder:db_url_flag_read", flag is not None
                     and fake.kwargs.get("database") == "hadb", str(fake.kwargs.get("database"))))
@@ -2013,11 +2114,13 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
     clean = sum(c for _, c in injected)
     share = ({"injected_ratio": round(sum(i for i, _ in injected) / clean, 4)}
              if inject in ("cpu", "loop") and clean > 0 else {})
-    results["cycle_cost"] = uncovered_files(traced) + cost_offenders(
-        figures, COST_BUDGETS.get(path.name))
+    ref_ms = sorted(ref_cpu)[len(ref_cpu) // 2]
+    budget, refused = class_budget(path.name, ref_ms)
+    results["cycle_cost"] = uncovered_files(traced) + (
+        refused or cost_offenders(figures, budget))
     return {"fixture": path.name, "cycles": cycles, "entities": len(entities),
             "cost": {**figures, **share, "timed": len(cycle_cpu), "traced": len(peaks),
-                     "ref_ms": sorted(ref_cpu)[len(ref_cpu) // 2],
+                     "ref_ms": ref_ms,
                      "loop_ref_ms": sorted(loop_ref_cpu)[len(loop_ref_cpu) // 2]},
             "seconds": round(time.monotonic() - started, 1),
             "results": {k: v[:12] + ([f"... {len(v) - 12} more"] if len(v) > 12 else [])
@@ -2477,6 +2580,8 @@ def main(argv: list[str] | None = None) -> int:
     # committed fixtures and leaves at least one to them, so the full lane
     # (nightly, and every pull request that reaches it) always runs them.
     committed = {f.name for f in FIXTURES.glob("*.json")}
+    wrong = away_covered_offenders(AWAY_COVERED, committed)
+    R.check("AWAY_COVERED names committed fixtures", not wrong, " | ".join(wrong))
     wrong = arms_skip_offenders(set(COST_ARMS_SKIPPED), committed)
     R.check("the doubled-cost arms are skipped on committed fixtures only, never all",
             not wrong, " | ".join(wrong) + f"; this run perturbed {perturbed}")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
