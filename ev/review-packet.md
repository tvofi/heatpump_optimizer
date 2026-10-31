# Review packet #3005
head: f91733b769b297847e7c143dbdc96d437a44c4b1
base: 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124370167103 neutral
arch-score / arch-score id=124369192864 success
arm id=124368220865 skipped
budget-raise-gate / budget-raise-gate id=124369192892 success
cancel-superseded id=124368226335 success
codeql / Analyze (actions) id=124369192795 success
codeql / Analyze (javascript-typescript) id=124369192863 queued
codeql / Analyze (python) id=124369192942 queued
governance / delivery-status id=124369192846 success
governance / delivery-status-publish id=124369194694 skipped
governance / env-matrix id=124369192875 in_progress
governance / instrument-self-tests id=124369192952 queued
governance / policy-docs id=124369192858 queued
governance / record id=124369194892 skipped
governance / wave-script id=124369192886 success
hassfest / hassfest id=124369192779 success
kernel-points id=124369194749 skipped
prelude id=124368225943 in_progress
refresh id=124368226228 success
tests / briefs id=124369192774 success
tests / closure-scope id=124369192836 queued
tests / mutation id=124369192834 in_progress
tests / nightly-status id=124369192891 queued
validate / validate-hacs id=124369192867 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 7891e5d4: R10-COP-GATE
NOTE body item 137a1d3e: R10-COP-GATE
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh body.md
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json
new file mode 100644
index 000000000..fd855658f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift CMP_BOUND 2f3e2f1a",
+  "killed_by": "tests/features.py",
+  "old": "    if a.space + a.dhw <= 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if a.space + a.dhw < 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json
new file mode 100644
index 000000000..597540756
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift GUARD_OFF 2f3e2f1a",
+  "killed_by": "tests/features.py",
+  "old": "    if a.space + a.dhw <= 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index bd7a38ab2..4466f5718 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -856,10 +856,10 @@ def _fold_flow_lift(coord: Any, now: datetime) -> None:
     * the draw not distorted — ``_cop_fold_blocked``, not a restatement of
       it: a resistive element or a capped compressor is running the plant at
       a supply temperature the compressor did not choose;
-    * a space-dominant commanded split, at the same ``_COP_CURVE_SHARE``
-      threshold the efficiency reference uses. The curve is a SPACE heating
-      curve; a hot-water interval runs the supply at the tank's charge
-      temperature and says nothing about where the space curve sits.
+    * a space-dominant interval by its attribution (the mode dwell where
+      observed, else the commanded split), at the efficiency reference's
+      ``_COP_CURVE_SHARE``: the curve is a SPACE heating curve, and a hot-water
+      interval runs the supply at the tank's charge temperature.
 
     ``now`` is unused for arithmetic and taken anyway: this is called from
     ``_record_accuracy``'s per-cycle block beside ``_observe_frequency``,
@@ -880,9 +880,8 @@ def _fold_flow_lift(coord: Any, now: datetime) -> None:
         return
     if _cop_fold_blocked(coord):
         return
-    space, dhw = coord._commanded_split()
-    total = space + dhw
-    if total <= 1e-6 or dhw / total > coord._COP_CURVE_SHARE:
+    a = heat_energy.meter_of(coord).attribution(coord._commanded_split())
+    if a.space + a.dhw <= 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:
         return
     curve = curve_supply_temp(
         coord._thermal_model,
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 01a1d9d41..55e54f1ca 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -2035,6 +2035,9 @@ class ModelStatusSensor(HeatPumpOptimizerSensorBase):
                 "samples": data.get("cop_samples"),
                 "alarm": bool(cop_health.get("alarm")),
                 "watched_buckets": cop_health.get("watched_buckets"),
+                "cop_observability": data.get("cop_observability"),
+                "cop_refusal": data.get("cop_refusal"),
+                "measured_cop_at": data.get("measured_cop_at"),
             },
             "internal_gains_kw": data.get("internal_gains_profile"),
             "capacity_envelope": _mapping(data.get("capacity_envelope")).get("buckets"),
diff --git a/dev/programme/delivery/3005.md b/dev/programme/delivery/3005.md
new file mode 100644
index 000000000..0b87be05f
--- /dev/null
+++ b/dev/programme/delivery/3005.md
@@ -0,0 +1 @@
+- [#3005](https://github.com/tvofi/heatpump_optimizer/pull/3005) — **open**, R10-COP-GATE part 5: residual carries (R10-COP-GATE)
diff --git a/tests/entities.py b/tests/entities.py
index 22d5d35bf..21442a4d0 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -6172,6 +6172,31 @@ R.check(
     f"{_cg_view!r}",
 )
 
+# R10-COP-GATE part 5 (A): the observed-COP sensor is unavailable exactly when
+# the install is not measurable, so Home Assistant hides its attributes from
+# the card; the model status sensor's ``cop`` row carries the same three keys
+# under their own names, copied from the learning view, never re-derived.
+_cg_keys = ("cop_observability", "cop_refusal", "measured_cop_at")
+_cg_status_view = {
+    obs: {
+        k: sensor.ModelStatusSensor(FakeCoordinator(ent.coordinator.data), ENTRY)
+        .extra_state_attributes["cop"].get(k, "<absent>")
+        for k in _cg_keys
+    }
+    for obs, ent in _cg_cop.items()
+}
+R.check(
+    "the model status sensor's cop row carries cop_observability, "
+    "cop_refusal and measured_cop_at as the learning view publishes them, "
+    "while the not-measurable observed-COP sensor is unavailable",
+    not _cg_cop["not_measurable"].available
+    and all(
+        _cg_status_view[obs] == {k: ent.coordinator.data[k] for k in _cg_keys}
+        for obs, ent in _cg_cop.items()
+    ),
+    f"{_cg_status_view!r}",
+)
+
 # --- a failed refresh reaches every entity ----------------------------------
 R.section("A failed refresh reaches every entity")
 
diff --git a/tests/features.py b/tests/features.py
index 1a6ca7cc5..48e3cc3da 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -67067,6 +67067,54 @@ R.check(
     _cf_fl._flow_bias.samples == 1,
     f"flow-bias samples {_cf_fl._flow_bias.samples}",
 )
+# R10-COP-GATE part 5 (C): the duty gate reads the interval's attribution,
+# not the commanded split. A switch-back window -- 0.45 h hot water, then
+# 0.05 h space, under a space-only plan -- ran the supply at the tank's charge
+# temperature; the all-space window and the no-dwell plan (above) still fold.
+from heatpump_optimizer import heat_energy as _cf_he  # noqa: E402
+
+
+def _cf_fl_window(dhw_h, space_h):
+    coord = _cf_coord()
+    _cf_learn(coord, 2.2)
+    coord._flow_bias.observe_temps(35.0, 30.0)
+    meter = _cf_he.meter_of(coord)
+    start = _T6 - timedelta(hours=dhw_h + space_h)
+    meter.cycle = (start, _T6)
+    meter.dwell.segments = [
+        *([_cf_he.Segment(start, _cf_he.DHW)] if dhw_h else []),
+        _cf_he.Segment(_T6 - timedelta(hours=space_h), _cf_he.SPACE),
+    ]
+    _fold_flow_lift(coord, _T6)
+    return coord._commanded_split(), meter.attribution(coord._commanded_split()), coord._flow_bias.samples
+
+
+_cf_sw, _cf_all = _cf_fl_window(0.45, 0.05), _cf_fl_window(0.0, 0.5)
+R.check(
+    "a hot-water-dominant window under a space plan folds no flow-bias "
+    "sample; an all-space window folds one (null)",
+    _cf_sw[0][1] == 0.0 and _cf_sw[1].observed and _cf_sw[2] == 0 and _cf_all[2] == 1,
+    f"switch-back {_cf_sw} / all-space {_cf_all}",
+)
+# Both of the gate's bounds at equality, through the real dwell. A window of
+# exactly 1e-6 h (3.6 ms) is the "no weight" bound and folds nothing; 2e-6 h
+# folds (null). A hot-water share of exactly _COP_CURVE_SHARE (0.15 h of 1 h)
+# is still the space curve's duty and folds; 0.16 h does not (null).
+_cf_w0, _cf_w1 = _cf_fl_window(0.0, 1e-6), _cf_fl_window(0.0, 2e-6)
+R.check(
+    "the flow-lift gate's no-weight bound is inclusive: a 1e-6 h window "
+    "folds nothing, a 2e-6 h window folds one (null)",
+    _cf_w0[1].space + _cf_w0[1].dhw == 1e-6 and _cf_w0[2] == 0 and _cf_w1[2] == 1,
+    f"1e-6 h {_cf_w0} / 2e-6 h {_cf_w1}",
+)
+_cf_s15, _cf_s16 = _cf_fl_window(0.15, 0.85), _cf_fl_window(0.16, 0.84)
+R.check(
+    "a hot-water share exactly at the curve share still folds; just above "
+    "it does not (null)",
+    _cf_he.dhw_share(_cf_s15[1]) == Coord._COP_CURVE_SHARE
+    and _cf_s15[2] == 1 and _cf_s16[2] == 0,
+    f"0.15 {_cf_s15} / 0.16 {_cf_s16}",
+)
 
 # The refusal is published where Home Assistant does not hide it: the
 # observed-COP sensor is unavailable exactly while this is the explanation,
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index b7341d300..2df9bbe66 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -733,3 +733,8 @@
 # valve_storage_low_target, whose plan leaves move too: the reference's energy
 # anchors three of the space solve's starts, so a valved plan can land in
 # another basin. Unvalved fixtures do not move.
+coord_all_features  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
+coord_dhw  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
+coord_grid_fee  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
+coord_minimal  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
+coord_two_zone  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 931c703fe..67a6c297e 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -2070,6 +2070,9 @@
     "capacity_envelope": {},
     "cop": {
      "alarm": false,
+     "cop_observability": "no_electric_meter",
+     "cop_refusal": null,
+     "measured_cop_at": null,
      "samples": 0,
      "scale": 1.0,
      "watched_buckets": 0
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index 9f29db493..f108e11ac 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -1991,6 +1991,9 @@
     "capacity_envelope": {},
     "cop": {
      "alarm": false,
+     "cop_observability": "no_electric_meter",
+     "cop_refusal": null,
+     "measured_cop_at": null,
      "samples": 0,
      "scale": 1.0,
      "watched_buckets": 0
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 3087f9e10..da1e9b46d 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -1834,6 +1834,9 @@
     "capacity_envelope": {},
     "cop": {
      "alarm": false,
+     "cop_observability": "no_electric_meter",
+     "cop_refusal": null,
+     "measured_cop_at": null,
      "samples": 0,
      "scale": 1.0,
      "watched_buckets": 0
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index bccc3b3a7..3ad9d21bb 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -1834,6 +1834,9 @@
     "capacity_envelope": {},
     "cop": {
      "alarm": false,
+     "cop_observability": "no_electric_meter",
+     "cop_refusal": null,
+     "measured_cop_at": null,
      "samples": 0,
      "scale": 1.0,
      "watched_buckets": 0
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index 20caa9416..d0bbc0ebd 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -1880,6 +1880,9 @@
     "capacity_envelope": {},
     "cop": {
      "alarm": false,
+     "cop_observability": "no_electric_meter",
+     "cop_refusal": null,
+     "measured_cop_at": null,
      "samples": 0,
      "scale": 1.0,
      "watched_buckets": 0
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json
new file mode 100644
index 000000000..fd855658f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.CMP_BOUND.2f3e2f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift CMP_BOUND 2f3e2f1a",
+  "killed_by": "tests/features.py",
+  "old": "    if a.space + a.dhw <= 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if a.space + a.dhw < 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json
new file mode 100644
index 000000000..597540756
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.2f3e2f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift GUARD_OFF 2f3e2f1a",
+  "killed_by": "tests/features.py",
+  "old": "    if a.space + a.dhw <= 1e-6 or heat_energy.dhw_share(a) > coord._COP_CURVE_SHARE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 061d4aef7..5defe9b2c 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17659,
+ "class_excess_loc": 17658,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "88c6ad5bbec69bfe157e04597a74d0c9c3e4775c",
+ "recorded_at": "507a9ec264eb373b132248d752259254d8a9fa4d",
  "seam_cut_total": 422
 }

