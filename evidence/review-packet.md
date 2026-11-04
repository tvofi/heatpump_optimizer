# Review packet #3174
head: 558c54a0f0f0617678caa9acc87a426a8ddb19bc
base: b8e823699981866383f1afa54ce708ded3419316

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=125529924011 success
arch-score / arch-score id=125551307152 success
arm id=125528645333 skipped
budget-raise-gate / budget-raise-gate id=125551307379 success
cancel-superseded id=125528645345 success
codeql id=125551308595 skipped
codeql / Analyze (actions) id=125528941775 success
codeql / Analyze (javascript-typescript) id=125528941758 success
codeql / Analyze (python) id=125528941781 success
gate id=125552986776 success
governance id=125551308895 skipped
governance / delivery-status id=125528941954 failure
governance / delivery-status-publish id=125528944505 skipped
governance / env-matrix id=125528941818 success
governance / instrument-self-tests id=125528941891 success
governance / policy-docs id=125528941856 success
governance / record id=125528944964 skipped
governance / wave-script id=125528941951 success
hassfest id=125551309918 skipped
hassfest / hassfest id=125528941785 success
kernel-points id=125551309459 skipped
pr-contract / pr-contract id=125552025626 success
prelude id=125528645011 success
refresh id=125528645227 success
tests id=125551309836 skipped
tests / arch-instrument id=125530194999 success
tests / briefs id=125528941584 success
tests / browser id=125530195418 success
tests / ci-ratchet id=125541004691 skipped
tests / claims-autofix id=125537655563 skipped
tests / closure-scope id=125528941907 success
tests / closures id=125530195146 success
tests / closures-autofix id=125536431134 skipped
tests / coverage id=125530195021 success
tests / coverage-ratchet id=125541002620 success
tests / fast (3.14) id=125530195519 success
tests / graders-head-copy id=125541002557 success
tests / lane-proofs id=125541002605 success
tests / mutation id=125528941681 success
tests / mutation-autofix id=125530772551 skipped
tests / mutation-pins id=125530770865 skipped
tests / nightly-ha id=125530197148 skipped
tests / nightly-status id=125528941833 success
tests / replay id=125530195186 success
tests / typing id=125530195014 success
validate id=125551309272 skipped
validate / validate-hacs id=125528941803 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api repos/tvofi/heatpump_optimizer/actions/jobs/125461180429/logs
             gh api: every long flag accepted
  unverified PYTHONPATH=tests/hastub python3 -B -c "import sys; sys.path.insert(0,'tests'); import replay as r; s='synthetic-dhw-only.json'; [print(x, r.class_budget(s, x)[1][:1] or r.cost_offenders({'cpu_ratio': c}, r.class_budget(s, x)[0])) for x, c in ((23.83, 2.5671), (28.01, 1.8924), (34.35, 1.8747), (22.16, 1.9455), (47.73, 2.2746), (54.55, 1.4448))]"
             python3 runs an inline script rather than a file
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 4 resolved, 1 not verified, 0 refused

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
index e98f66930..e675cdb77 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -465,14 +465,76 @@ COST_DETECTION = 2.0
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
+#: 0.0901-0.1026 over the seven ref30, ref46 and ref53 jobs below: 0.1278,
+#: each ``loop doubled`` arm (0.179-0.2015) over it; the ref24 class reads
+#: 0.1282 and is keyed on its own reading. A box outside every class
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
+#: the same code, more than the 2x one band holds, and the figure is not a
+#: function of the ruler (ref24, the fastest, reads 2.57, between ref46 and
+#: ref30), so a class is admitted only on its own readings, never
+#: interpolated. Each band is its ``ref_ms``
+#: readings (every clean and doubled run of the jobs cited in
+#: ``COST_CLASS_READINGS``) widened 5 % each way, the within-job spread being
+#: 2.3-3.2 %; the bands are disjoint. A run in no band is refused by name
+#: (``class_budget``), never graded against a neighbour's budget: a new
+#: runner class turns the lane red once, and its own ``cost`` lines are the
+#: readings that admit it here. Two rulers have read once each and are
+#: refused: 28.0 (job 125000687320, #3078: 1.89) and 34.4 (nightly job
+#: 123225871060: 1.87). The first lies 2.5 % under ref30 and reads 0.67-0.72x
+#: its ratios; a ref30 widened over it would not see its doubled arm (3.89).
+#: ``COST_RULERS_REFUSED`` holds them, so a band widened over either is red.
+COST_RUNNER_CLASSES: dict[str, tuple[float, float]] = {
+    "ref24": (22.64, 25.53),
+    "ref30": (28.72, 32.69),
+    "ref46": (42.99, 49.51),
+    "ref53": (49.60, 56.78),
+}
+COST_RULERS_REFUSED: tuple[float, ...] = (28.01, 34.35)
+#: Per fixture and runner class, the budgets that differ by class: sqrt(2) x
+#: the geometric midpoint of that class's clean readings in
+#: ``COST_CLASS_READINGS``, every reading 69-72 % of its class's budget.
+COST_CLASS_BUDGETS: dict[str, dict[str, dict[str, float]]] = {
+    "synthetic-dhw-only.json": {"ref24": {"cpu_ratio": 3.630, "loop_cpu_ratio": 0.1813},
+                                "ref30": {"cpu_ratio": 3.934},
+                                "ref46": {"cpu_ratio": 3.357},
+                                "ref53": {"cpu_ratio": 2.081}},
+}
+#: The lane readings each class budget is centred on: per cited job, its
+#: ``ref_ms``, the metric, its clean reading and its doubled arm's, from its
+#: ``cost`` lines. ref24: job 125461180429 (run 41498701363, #3174); ref30: jobs 125160076828 (#3167), 125240101580 (#3174); ref46: jobs
+#: 125097530406 (#3078), 125316010511 (#3174); ref53: nightly.yml ``slow``
+#: jobs 124414072168 (run 41159630948), 124725704090 (run 41264951784),
+#: 125036077984 (run 41369286061). A re-record appends its job here; the
+#: ``cycle_cost:class_budgets`` control holds every clean reading inside its
+#: class's band and every doubled arm over it.
+COST_CLASS_READINGS: dict[str, list[tuple[float, str, float, float]]] = {
+    "synthetic-dhw-only.json": [
+        (23.83, "cpu_ratio", 2.5671, 5.2086), (23.83, "loop_cpu_ratio", 0.1282, 0.2603),
+        (30.32, "cpu_ratio", 2.81, 5.701), (30.93, "cpu_ratio", 2.7543, 5.5315),
+        (45.65, "cpu_ratio", 2.3246, 4.6473), (46.36, "cpu_ratio", 2.4235, 4.7775),
+        (52.76, "cpu_ratio", 1.4563, 2.8848), (53.27, "cpu_ratio", 1.451, 2.841),
+        (52.43, "cpu_ratio", 1.4926, 2.9251)],
+}
 #: Fixtures the lane replays once, clean, without the three doubled-cost
 #: arms: each arm is a whole replay, and a fixture whose replay costs a large
 #: share of the lane's job time cannot be run four times inside it (the
@@ -587,6 +649,22 @@ def cost_offenders(figures: dict[str, float], budget: dict[str, float] | None,
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
@@ -597,6 +675,15 @@ def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
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
@@ -732,12 +819,37 @@ def controls() -> list[tuple[str, bool, str]]:
         [20.0, 22.0], [r * 3 for r in ref], [4096])["cpu_ratio"]
     res.append(("control:cycle_cost:cpu_normaliser", cpu_solve_moved,
                 f"cpu_ratio {clean['cpu_ratio']}: solve x3 moved={cpu_solve_moved}"))
+    # Runner classes (R10-REPLAY-COST-BUDGET): each class's budget holds its
+    # own lane readings in band and sees its own doubled arm; one budget for
+    # every class could not. A ruler in no band is refused, by name.
+    syn = "synthetic-dhw-only.json"
+    off = [(ref_ms, cost_offenders({key: c}, class_budget(syn, ref_ms)[0]),
+            cost_offenders({key: d}, class_budget(syn, ref_ms)[0]))
+           for ref_ms, key, c, d in COST_CLASS_READINGS[syn]]
+    res.append(("control:cycle_cost:class_budgets",
+                all(not c and any("over its budget" in o for o in d) for _, c, d in off),
+                str([(r, c[:1], d[:1]) for r, c, d in off if c or not d])))
+    # One probe in every gap between bands, one under the lowest, the rulers
+    # CI read and no band admits, and NaN.
+    bands = sorted(COST_RUNNER_CLASSES.values())
+    gaps = [(hi + lo) / 2 for (_, hi), (lo, _) in zip(bands, bands[1:])]
+    unknown = [class_budget(syn, x) for x in (*gaps, bands[0][0] / 2,
+                                              *COST_RULERS_REFUSED, float("nan"))]
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
@@ -1212,6 +1324,14 @@ def recorder_checks() -> list[tuple[str, bool, str]]:
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
@@ -2013,11 +2133,13 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
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
@@ -2477,6 +2599,8 @@ def main(argv: list[str] | None = None) -> int:
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
