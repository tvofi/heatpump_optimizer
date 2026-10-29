# Review packet #2946
head: 8b0f5c316903372f34e5194a9c5791fd9b8365ee
base: 66974d47312caa46e9817b9aeae7186e9764e560

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=123399260281 success
budget-raise-gate / budget-raise-gate id=123399189312 success
cancel-superseded id=123399188470 skipped
codeql id=123399122442 skipped
codeql / Analyze (actions) id=123399248630 success
codeql / Analyze (javascript-typescript) id=123399189642 success
codeql / Analyze (python) id=123399230408 success
gate id=123399915061 in_progress
governance id=123399121754 skipped
governance / delivery-status id=123399188544 skipped
governance / delivery-status-publish id=123399188433 skipped
governance / env-matrix id=123399234928 success
governance / instrument-self-tests id=123399253703 success
governance / policy-docs id=123399234999 success
governance / record id=123399188569 skipped
governance / wave-script id=123399249334 success
hassfest id=123399121644 skipped
hassfest / hassfest id=123399253770 success
kernel-points id=123399188357 skipped
pr-contract / pr-contract id=123399630627 success
prelude id=123399243815 success
refresh id=123399221695 success
tests id=123399122085 skipped
tests / arch-instrument id=123399190785 success
tests / briefs id=123399230099 success
tests / browser id=123399191492 success
tests / ci-ratchet id=123399192746 skipped
tests / claims-autofix id=123399191851 skipped
tests / closure-scope id=123399247977 success
tests / closures id=123399190917 success
tests / closures-autofix id=123399192248 skipped
tests / coverage id=123399192080 success
tests / coverage-ratchet id=123399191917 success
tests / fast (3.14) id=123399190843 success
tests / graders-head-copy id=123399192787 skipped
tests / lane-proofs id=123399192915 skipped
tests / mutation id=123399249477 success
tests / mutation-autofix id=123399191662 skipped
tests / mutation-pins id=123399190818 skipped
tests / nightly-ha id=123399191069 skipped
tests / nightly-status id=123399189065 skipped
tests / replay id=123399192290 skipped
tests / typing id=123399191440 success
validate id=123399121709 skipped
validate / validate-hacs id=123399230427 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 697b9811: R10-ARCH-SHAPES-CLASSIFIER
NOTE body item 605bc17a: R10-ROUND-PLAYBOOK
NOTE body item 841fa6a4: R10-ROUND-PLAYBOOK
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py
             `dev/audit/harnesses/r10_configflow_pages.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py --null
             `dev/audit/harnesses/r10_configflow_pages.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py --clear-required
             `dev/audit/harnesses/r10_configflow_pages.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py --all
             `dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py --bump heat_pump_cop_nominal
             `dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py` is in the tree at this head
  ok         tools/audit/archscore/vector.py
             `tools/audit/archscore/vector.py` is in the tree at this head
  unverified git diff 66974d473...HEAD -- tests/ci_budgets.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/ci_ratchet.py
             `tests/ci_ratchet.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 66974d473
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D8/s1/f1_active_now.py
             `dev/audit/rounds/round10/D8/s1/f1_active_now.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py
             `dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py
             `dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 66974d473
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=66974d473 ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  unverified git diff --name-only 66974d473...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --stat 66974d473...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 15 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index c1a29607e..c96ada5d8 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -13,7 +13,7 @@ from homeassistant import config_entries
 from homeassistant.const import CONF_NAME
 from homeassistant.core import HomeAssistant, callback
 from homeassistant.data_entry_flow import section
-from homeassistant.helpers import device_registry as dr, entity_registry as er, selector
+from homeassistant.helpers import entity_registry as er, selector
 from homeassistant.helpers.aiohttp_client import async_get_clientsession
 from homeassistant.helpers.translation import async_get_translations
 from homeassistant.helpers.typing import UNDEFINED, UndefinedType
diff --git a/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py b/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py
new file mode 100644
index 000000000..c621b1f3e
--- /dev/null
+++ b/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py
@@ -0,0 +1,157 @@
+"""ARCH2-s5 (round 10, D7): one setting, two selectors -- the setup wizard against the options registry.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--bump KEY]
+
+Instrumented symbols: ``config_flow:HeatPumpOptimizerConfigFlow.async_step_<page>`` (driven, the
+widget objects the flow DELIVERS in its schema are what is counted) and
+``config_flow:_OPTION_FIELDS`` (the registry each wizard key also has a row in).
+
+Metrics (count key: the widget object the wizard page's schema delivers, per field):
+  wizard_fields     fields the six wizard pages render
+  in_registry       of those, keys that also have an ``_OPTION_FIELDS`` row
+  spelled_twice     of those, fields whose widget is NOT the registry row's object (built a second time)
+  disagree          of those, fields whose selector fingerprint (type + config) differs from every row's
+  menu_fallbacks    options-menu fallback labels in code; menu_disagree: those differing from
+                    translations/en.json (the label shown when the translation lookup fails)
+  golden_equal      1 when golden.capture_config_flow() equals tests/golden/config_flow.json
+
+Perturbation: ``--bump KEY`` multiplies that key's registry max by 2 before driving the flow (a
+one-line production edit, simulated on the loaded module). On the baseline, ``--bump
+heat_pump_cop_nominal`` moves disagree 0 -> 2 (building_extras and thermal keep their own copy); on
+a tree where the wizard reads the registry it stays 0, because the second copy no longer exists.
+
+Counts only: contention-immune. Writes nothing.
+"""
+import os
+
+for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
+    os.environ.setdefault(_v, "1")
+
+import argparse  # noqa: E402
+import asyncio  # noqa: E402
+import json  # noqa: E402
+import sys  # noqa: E402
+from pathlib import Path  # noqa: E402
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+REPO = repo_root(__file__)
+sys.path[:0] = [str(REPO / "tests"), str(REPO / "custom_components")]
+
+from harness import FakeHass  # noqa: E402
+from heatpump_optimizer import config_flow as cf  # noqa: E402
+
+WIZARD = ("temperature", "building_extras", "thermal", "zones", "dhw", "weather_sensitivity")
+#: The other initial-flow form pages, measured with --all: the first two screens and the quick path.
+OTHER = ("user", "user_sensors", "quick_setup", "building_describe")
+
+
+def fingerprint(widget):
+    cfg = getattr(widget, "config", None)
+    return (type(widget).__name__, tuple(sorted((k, repr(v)) for k, v in dict(cfg or {}).items())))
+
+
+def bump(key):
+    """Double the registry max of ``key`` in place: the one-line edit, applied to the loaded module."""
+    rows = [r for r in cf._OPTION_FIELDS if r.key == key]
+    assert rows, key
+    for r in rows:
+        r.widget.config = {**r.widget.config, "max": r.widget.config["max"] * 2}
+
+
+def _leaves(schema):
+    """(marker, widget) for every field, a ``section()``'s fields included."""
+    for marker, value in schema.schema.items():
+        inner = getattr(value, "schema", None)
+        if isinstance(inner, cf.vol.Schema):
+            yield from _leaves(inner)
+        else:
+            yield marker, value
+
+
+def measure(steps=WIZARD):
+    flow = cf.HeatPumpOptimizerConfigFlow()
+    flow.hass = FakeHass()
+    out = {"wizard_fields": 0, "in_registry": 0, "spelled_twice": 0, "disagree": 0}
+    seats = []
+    for step in steps:
+        schema = asyncio.run(getattr(flow, f"async_step_{step}")()).get("data_schema")
+        for marker, widget in _leaves(schema):
+            key = str(marker)
+            out["wizard_fields"] += 1
+            rows = [r for r in cf._OPTION_FIELDS if r.key == key]
+            if not rows:
+                continue
+            out["in_registry"] += 1
+            if any(widget is r.widget for r in rows):
+                continue
+            out["spelled_twice"] += 1
+            seats.append(f"{step}:{key}")
+            if all(fingerprint(widget) != fingerprint(r.widget) for r in rows):
+                out["disagree"] += 1
+                seats.append(f"  DISAGREES {step}:{key}")
+    return out, seats
+
+
+def menus():
+    en = json.loads((REPO / "custom_components/heatpump_optimizer/translations/en.json").read_text())
+    F = cf.HeatPumpOptimizerOptionsFlow
+    n, bad = 0, []
+    for menu, steps in (("init", F._TOP_MENU), ("advanced", F._ADVANCED_MENU)):
+        for st in steps:
+            n += 1
+            if F._MENU_LABELS[st] != en["options"]["step"][menu]["menu_options"].get(st):
+                bad.append(f"{menu}.{st}: code {F._MENU_LABELS[st]!r} vs en.json "
+                           f"{en['options']['step'][menu]['menu_options'].get(st)!r}")
+    return n, bad
+
+
+def golden_equal():
+    import golden
+    committed = json.loads((REPO / "tests/golden/config_flow.json").read_text())
+    return int(json.loads(json.dumps(golden.capture_config_flow(), sort_keys=True)) == committed)
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--bump")
+    ap.add_argument("--all", action="store_true", help="also the other initial-flow form pages")
+    a = ap.parse_args()
+    if a.bump:
+        bump(a.bump)
+    out, seats = measure()
+    for s in seats:
+        print(f"  {s}")
+    for k, v in out.items():
+        print(f"RESULT {k}={v} count")
+    if a.all:
+        other, oseats = measure(OTHER)
+        for s in oseats:
+            print(f"  other {s}")
+        for k, v in other.items():
+            print(f"RESULT other_{k}={v} count")
+    n, bad = menus()
+    for b in bad:
+        print(f"  {b}")
+    print(f"RESULT menu_fallbacks={n} count")
+    print(f"RESULT menu_disagree={len(bad)} count")
+    if not a.bump:
+        print(f"RESULT golden_equal={golden_equal()} bool")
+    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/2946.md b/dev/programme/delivery/2946.md
new file mode 100644
index 000000000..fdea62933
--- /dev/null
+++ b/dev/programme/delivery/2946.md
@@ -0,0 +1 @@
+- [#2946](https://github.com/tvofi/heatpump_optimizer/pull/2946) — **open**, R10-CONFIGFLOW-PAGES: arm D, drop unused device_registry import, land the wizard-widgets harness (R10-CONFIGFLOW-PAGES)
diff --git a/tests/ci_budgets.json b/tests/ci_budgets.json
index 8dedad2da..4de8c8849 100644
--- a/tests/ci_budgets.json
+++ b/tests/ci_budgets.json
@@ -13,7 +13,7 @@
  "archscore.hub_solve_writes": 16,
  "archscore.import_cycle_modules": 0,
  "archscore.layer_violations": 22,
- "archscore.literal_clone_copies": 186,
+ "archscore.literal_clone_copies": 123,
  "archscore.params_over_10": 12,
  "archscore.private_cross_module": 17,
  "archscore.public_unused": 1,
@@ -22,10 +22,10 @@
  "archscore.shared_inplace_writes": 3,
  "archscore.unread_private_globals": 0,
  "archscore.untyped_payload_keys": 0,
- "archscore.unused_boundary_imports": 1,
+ "archscore.unused_boundary_imports": 0,
  "critical_path_minutes": 34.267,
- "reason": "Re-record critical_path_minutes 54.825 -> 34.267 (main red, CI job 121295715608): the metric is now each push run's tests critical path with runner queue removed, not its wall, graded at the 8-run median and recorded at the p90 of `--gather-runs --window 40` taken at main f3ffb1c63 (40 CI push runs, work 20.1..34.65 min, median 32.55). The old 54.825 was a 2026-10-12 median of walls; queue for runners, not work, took the median to 59.6 under an overlapping train. Every other row stands as recorded at recorded_at (R10-LIVESTATE, #2232).",
- "recorded_at": "fd7e289d0a09862b57f0509bf1071c54b9054799",
+ "reason": "Two rows lowered (R10-CONFIGFLOW-PAGES arm D, the group's carried tripwires), each at the value vector.measure derives at 4b9ee5377: archscore.unused_boundary_imports 1 -> 0 (config_flow.py's unread `device_registry as dr` import is dropped), archscore.literal_clone_copies 186 -> 123 (recorded 186; measured 123 at merge base 66974d473 and at this head: arms C and C2, #2915, took the setup-flow widgets from _OPTION_FIELDS; drop 63). No other row moves; every other row stands as recorded at fd7e289d0 (previous reason: critical_path_minutes 54.825 -> 34.267, R10-LIVESTATE, #2232).",
+ "recorded_at": "4b9ee53778fa8fd15ad8ffdf1f1309e3f06aa282",
  "script_runs_full_case_pr": 68,
  "script_runs_per_push": 54
 }
diff --git a/tests/closures.json b/tests/closures.json
index 5b8a18073..0b0bf0303 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3956,6 +3956,7 @@
    "dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py",
    "dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py",
    "dev/audit/rounds/round10/D7/arch-s3/score_delta.py",
+   "dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py",
    "dev/audit/rounds/round10/D7/s1/class_growth.py",
    "dev/audit/rounds/round10/D7/s2/learner_gates.py",
    "dev/audit/rounds/round10/D7/s2/sysid_plant.py",

