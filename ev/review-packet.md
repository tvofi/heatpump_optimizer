# Review packet #3045
head: 9ef51b8215dd7216950f177386fb2f5a8f010a47
base: a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124640194182 success
arch-score / arch-score id=124664943246 success
arm id=124639935665 skipped
budget-raise-gate / budget-raise-gate id=124664943224 failure
cancel-superseded id=124664850435 success
codeql id=124664944551 skipped
codeql / Analyze (actions) id=124640032413 success
codeql / Analyze (javascript-typescript) id=124640032156 success
codeql / Analyze (python) id=124640032177 success
gate id=124665332374 failure
governance id=124664944306 skipped
governance / delivery-status id=124640032485 success
governance / delivery-status-publish id=124640033769 skipped
governance / env-matrix id=124640032279 success
governance / instrument-self-tests id=124640032200 success
governance / policy-docs id=124640032286 success
governance / record id=124640033972 skipped
governance / wave-script id=124640032439 success
hassfest id=124664943999 skipped
hassfest / hassfest id=124640032176 success
kernel-points id=124664944382 skipped
pr-contract / pr-contract id=124665193958 success
prelude id=124664850610 success
refresh id=124664850641 success
tests id=124664944393 skipped
tests / arch-instrument id=124640163551 success
tests / briefs id=124640032578 success
tests / browser id=124640163559 success
tests / ci-ratchet id=124645085765 skipped
tests / claims-autofix id=124642563432 skipped
tests / closure-scope id=124640032228 success
tests / closures id=124640163623 success
tests / closures-autofix id=124644296435 skipped
tests / coverage id=124640163533 success
tests / coverage-ratchet id=124645084067 success
tests / fast (3.14) id=124640163593 success
tests / graders-head-copy id=124645084127 success
tests / lane-proofs id=124645084149 success
tests / mutation id=124640032423 success
tests / mutation-autofix id=124640185898 skipped
tests / mutation-pins id=124640185703 skipped
tests / nightly-ha id=124640165025 skipped
tests / nightly-status id=124640032218 success
tests / replay id=124640164449 skipped
tests / typing id=124640163578 success
validate id=124664944231 skipped
validate / validate-hacs id=124640032139 success

## Refusals
required-red: required context `gate` concluded failure at 9ef51b8215dd7216950f177386fb2f5a8f010a47

## Advisories
none

## carry_audit at the head
NOTE body item 32562953: R10-FLY-MANDATE-REVOKE-GUARD
NOTE body item cbf840e5: dismissed:a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine
NOTE body item ff066d06: dismissed:only the label is loose, and every figure re-derives exactly
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh run view 41201096004 -R tvofi/heatpump_optimizer --log-failed
             gh run view: every long flag accepted
  unverified git diff --stat 0d33c9348 05c0d6d5d
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tests/ci_ratchet.py --gather-runs FILE --window 60
             `tests/ci_ratchet.py` is in the tree at this head
  ok         gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main&created=2026-10-25..2026-10-26
             gh api: every long flag accepted
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 9ef51b8215dd7216950f177386fb2f5a8f010a47
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3045.md b/dev/programme/delivery/3045.md
new file mode 100644
index 000000000..2754717eb
--- /dev/null
+++ b/dev/programme/delivery/3045.md
@@ -0,0 +1 @@
+- [#3045](https://github.com/tvofi/heatpump_optimizer/pull/3045) — **open**, HOTFIX R10-HOTFIX-CI-CRITPATH-2: a measured tolerance band on critical_path_minutes only (R10-HOTFIX-CI-CRITPATH-2)
diff --git a/tests/ci_budgets.json b/tests/ci_budgets.json
index 4de8c8849..de4b58a6d 100644
--- a/tests/ci_budgets.json
+++ b/tests/ci_budgets.json
@@ -24,7 +24,8 @@
  "archscore.untyped_payload_keys": 0,
  "archscore.unused_boundary_imports": 0,
  "critical_path_minutes": 34.267,
- "reason": "Two rows lowered (R10-CONFIGFLOW-PAGES arm D, the group's carried tripwires), each at the value vector.measure derives at 4b9ee5377: archscore.unused_boundary_imports 1 -> 0 (config_flow.py's unread `device_registry as dr` import is dropped), archscore.literal_clone_copies 186 -> 123 (recorded 186; measured 123 at merge base 66974d473 and at this head: arms C and C2, #2915, took the setup-flow widgets from _OPTION_FIELDS; drop 63). No other row moves; every other row stands as recorded at fd7e289d0 (previous reason: critical_path_minutes 54.825 -> 34.267, R10-LIVESTATE, #2232).",
+ "critical_path_minutes_band": 1.3,
+ "reason": "critical_path_minutes_band added at 1.3 (R10-HOTFIX-CI-CRITPATH-2, owner ruling 2026-10-31 under mandate 6329234399): main went red at 05c0d6d5d on GREW critical_path_minutes 34.467 (budget 34.267), a diff of seven delivery-row .md files that cannot move CI work. The graded statistic is the median of the newest 8 push runs; its measured spread about its window's median, over every sliding 8-run window of 145 completed ci.yml push runs (86 on 2026-10-25, 59 on 2026-10-30..31), is max |dev| 1.300 (2026-10-25 set; 0.851 on 2026-10-30..31). The band is that maximum, unpadded. critical_path_minutes itself stays 34.267 (the p90 of the 86 2026-10-25 runs, reproduced exactly); every other row is unchanged and at zero tolerance (previous reason: two archscore rows lowered at 4b9ee5377, R10-CONFIGFLOW-PAGES arm D).",
  "recorded_at": "4b9ee53778fa8fd15ad8ffdf1f1309e3f06aa282",
  "script_runs_full_case_pr": 68,
  "script_runs_per_push": 54
diff --git a/tests/ci_ratchet.py b/tests/ci_ratchet.py
index bb8ac9762..814a9645e 100644
--- a/tests/ci_ratchet.py
+++ b/tests/ci_ratchet.py
@@ -43,6 +43,14 @@ THE METRICS, each an answer to a named cost:
                   p90 of a wider window (`--gather-runs FILE --window 40`),
                   so the ratchet refuses a median beyond the work's own
                   run-to-run noise, never one slow host.
+  critical_path_minutes_band   not a metric: the minutes past its budget
+                  that critical_path_minutes may read before it is GREW. An
+                  8-run median still swings with the host draw, and a window
+                  of record-only merges read 34.467 on a 34.267 budget
+                  (05c0d6d5d). Sized at the measured maximum |8-run median -
+                  window median| over 145 runs, 1.3; it never applies to a
+                  counter, a re-record carries it over, and widening it is a
+                  raise.
 
 WHAT IS DELIBERATELY NOT HERE, so nobody re-adds it wrongly:
 
@@ -95,6 +103,13 @@ from pathlib import Path
 ROOT = Path(__file__).resolve().parent.parent
 BUDGETS = ROOT / "tests" / "ci_budgets.json"
 METADATA_KEYS = {"recorded_at", "reason"}
+# The timing metric's tolerance band (R10-HOTFIX-CI-CRITPATH-2): a bound, not a
+# graded metric. critical_path_minutes is GREW only past budget + band; every
+# other row, the integer counters included, stays at zero tolerance. Sized
+# from the measured spread of the graded statistic (an 8-run median) about
+# its window's median on unchanged work -- never padded; widening it is a
+# raise (tools/policy/budget_raise_gate.py types it MAX).
+BAND_KEYS = {"critical_path_minutes_band": "critical_path_minutes"}
 
 LANES = ("closures", "coverage")
 
@@ -371,6 +386,10 @@ def budget_problems(table: dict) -> list[str]:
         if not _finite_number(value):
             problems.append(f"{key}={value!r} is not a finite number")
             continue
+        if key in BAND_KEYS:
+            if not 0 <= value <= 10:
+                problems.append(f"{key}={value!r} is outside 0..10 minutes")
+            continue
         if key.startswith("archscore."):
             if not isinstance(value, int) or value < 0:
                 problems.append(f"{key}={value!r} is not a non-negative "
@@ -618,20 +637,33 @@ def derive(metrics_dir: Path, runs_json: Path | None,
     return derived
 
 
+def record_table(budgets: dict, derived: dict, head: str, reason: str) -> dict:
+    """The table `--record` writes: every derived metric, stamped. A band is a
+    bound sized from measured noise, not a derived value: a re-record carries
+    it over unchanged."""
+    return {**{k: v for k, v in derived.items()},
+            **{k: budgets[k] for k in BAND_KEYS if k in budgets},
+            "recorded_at": head, "reason": reason}
+
+
 def compare(budgets: dict, derived: dict) -> tuple[list[str], int]:
     grew = []
     lines = []
-    for key in sorted(set(budgets) - METADATA_KEYS):
+    bands = {BAND_KEYS[k]: budgets[k] for k in BAND_KEYS if k in budgets}
+    for key in sorted(set(budgets) - METADATA_KEYS - set(BAND_KEYS)):
         budget = budgets[key]
+        band = bands.get(key, 0)
         if key not in derived:
             lines.append(f"  ?     {key}: not derived this run "
                          "(missing input); not graded")
             continue
         cur = derived[key]
-        mark = "ok" if cur <= budget else "GREW"
-        if cur > budget:
+        over = cur > budget + band
+        mark = "GREW" if over else "ok"
+        if over:
             grew.append(key)
-        lines.append(f"  {mark:<5} {key}: {cur} (budget {budget})")
+        within = f", band {band}" if band else ""
+        lines.append(f"  {mark:<5} {key}: {cur} (budget {budget}{within})")
     for key in sorted(set(derived) - set(budgets)):
         grew.append(key)
         lines.append(f"  GREW  {key}: {derived[key]} (no budget row; a new "
@@ -1030,6 +1062,37 @@ def self_test() -> int:
            and abs((dr or {}).get("critical_path_minutes", 0) - 41.2) < 0.05,
            msg or msg2 or f"grade {dg} record {dr}")
 
+    # The timing band (R10-HOTFIX-CI-CRITPATH-2): critical_path_minutes is
+    # graded against its budget plus critical_path_minutes_band, and nothing
+    # else is -- the integer counters stay at zero tolerance.
+    bt = {"recorded_at": "x", "critical_path_minutes": 34.267,
+          "critical_path_minutes_band": 1.3, "script_runs_per_push": 54}
+    _, g_noise = compare(bt, {"critical_path_minutes": 34.467, "script_runs_per_push": 54})
+    _, g_edge = compare(bt, {"critical_path_minutes": 35.567, "script_runs_per_push": 54})
+    _, g_grow = compare(bt, {"critical_path_minutes": 35.568, "script_runs_per_push": 54})
+    _, g_count = compare(bt, {"critical_path_minutes": 34.0, "script_runs_per_push": 55})
+    _, g_noband = compare({k: v for k, v in bt.items() if k != "critical_path_minutes_band"},
+                          {"critical_path_minutes": 34.467, "script_runs_per_push": 54})
+    ck("the observed noise (34.467 on a 34.267 budget) passes inside the 1.3 band",
+       g_noise == 0, f"grew {g_noise}")
+    ck("a median at budget + band exactly passes", g_edge == 0, f"grew {g_edge}")
+    ck("a median one thousandth past budget + band is growth", g_grow == 1, f"grew {g_grow}")
+    ck("the band never applies to a counter (54 -> 55 is growth with a band present)",
+       g_count == 1, f"grew {g_count}")
+    ck("no band row is zero tolerance (34.467 on 34.267 is growth)", g_noband == 1,
+       f"grew {g_noband}")
+    ck("a band row is a known, non-negative bound and not a graded metric",
+       budget_problems(bt) == []
+       and budget_problems({**bt, "critical_path_minutes_band": -0.1}) != []
+       and budget_problems({**bt, "critical_path_minutes_band": float("nan")}) != [],
+       f"{budget_problems(bt)}")
+    rt = record_table(bt, {"critical_path_minutes": 35.317, "script_runs_per_push": 53},
+                      "h" * 40, "r")
+    ck("--record carries the band over unchanged and re-records every derived metric",
+       rt == {"critical_path_minutes": 35.317, "critical_path_minutes_band": 1.3,
+              "script_runs_per_push": 53, "recorded_at": "h" * 40, "reason": "r"},
+       f"{rt}")
+
     print(f"ci-ratchet self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
@@ -1094,8 +1157,7 @@ def main(argv: list[str] | None = None) -> int:
         head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True,
                               check=True).stdout.strip()
-        table = {**{k: v for k, v in derived.items()},
-                 "recorded_at": head, "reason": record_reason}
+        table = record_table(budgets, derived, head, record_reason)
         problems = budget_problems(table)
         if problems:
             for p in problems:
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index daad84355..ca524f2af 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -204,6 +204,7 @@ SCHEMA: dict[str, list[tuple[tuple[str, ...], str]]] = {
         (("script_runs_per_push",), MAX),
         (("script_runs_full_case_pr",), MAX),
         (("critical_path_minutes",), MAX),
+        (("critical_path_minutes_band",), MAX0),
     ],
     "dev/governance/config/policy_budgets.json": [
         (("_band",), MAX),
@@ -758,6 +759,15 @@ def self_test() -> int:
           raised(I, i0, {**i0, "archscore.duplication_copies": 69}), True)
     check("ci: an archscore cap removed is a raise",
           raised(I, i0, {k: v for k, v in i0.items() if k != "archscore.family_splits"}), True)
+    # The timing band: absent is zero tolerance, so adding one is a raise.
+    check("ci: a critical-path band added is a raise (absent is a band of zero)",
+          raised(I, i0, {**i0, "critical_path_minutes_band": 1.3}), True)
+    check("ci: a critical-path band widened is a raise",
+          raised(I, {**i0, "critical_path_minutes_band": 1.3},
+                 {**i0, "critical_path_minutes_band": 1.4}), True)
+    check("ci: a critical-path band narrowed is routine",
+          raised(I, {**i0, "critical_path_minutes_band": 1.3},
+                 {**i0, "critical_path_minutes_band": 0.9}), False)
     check("ci: a key the ratchet does not know is frozen (the consumer refuses it too)",
           raised(I, i0, {**i0, "jobs_per_day": 3}), True)
 

