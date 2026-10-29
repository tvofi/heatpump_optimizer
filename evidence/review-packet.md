# Review packet #2872
head: 9b24795b242862ac8ea4f5f9f1c798cf087fbde7
base: 279578074a17cb2c7f527f5e28da0de4e2006db0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123580539734 neutral
arch-score / arch-score id=123580168004 success
arm id=123579813674 skipped
budget-raise-gate / budget-raise-gate id=123580168414 success
cancel-superseded id=123582637197 success
codeql / Analyze (actions) id=123580168688 success
codeql / Analyze (javascript-typescript) id=123580169500 success
codeql / Analyze (python) id=123580168692 in_progress
governance / delivery-status id=123580168803 success
governance / delivery-status-publish id=123580163796 skipped
governance / env-matrix id=123580169085 success
governance / instrument-self-tests id=123580169643 in_progress
governance / policy-docs id=123580168826 success
governance / record id=123580163659 skipped
governance / wave-script id=123580168817 success
hassfest / hassfest id=123580168789 success
kernel-points id=123580145317 skipped
prelude id=123582636616 in_progress
refresh id=123582637124 success
tests / arch-instrument id=123580492583 success
tests / briefs id=123580169316 success
tests / browser id=123580492896 success
tests / closure-scope id=123580169301 success
tests / closures id=123580492659 in_progress
tests / coverage id=123580492274 in_progress
tests / fast (3.14) id=123580492360 in_progress
tests / mutation id=123580169365 in_progress
tests / nightly-ha (2025.2.0) id=123580492976 success
tests / nightly-ha (stable) id=123580492742 success
tests / nightly-status id=123580169165 failure
tests / replay id=123580492754 success
tests / typing id=123580492266 success
validate / validate-hacs id=123580168211 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item a0b71528: R10-COP-PARTLOAD
NOTE body item 1b6e92ef: R10-COP-PARTLOAD
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_partload.py
             `dev/audit/harnesses/r10_cop_partload.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json
new file mode 100644
index 000000000..bcf2986aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors CMP_BOUND d899f1dc",
+  "killed_by": "tests/features.py",
+  "old": "    if derate >= limit:  # the limit is positive, so 0 always passes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if derate > limit:  # the limit is positive, so 0 always passes`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json
new file mode 100644
index 000000000..fde216919
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors GUARD_OFF d899f1dc",
+  "killed_by": "tests/features.py",
+  "old": "    if derate >= limit:  # the limit is positive, so 0 always passes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # the limit is positive, so 0 always passes`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json
new file mode 100644
index 000000000..59e1d8b6a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors RETURN_DEL 5e4fa825",
+  "killed_by": "tests/features.py",
+  "old": "    return {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json
new file mode 100644
index 000000000..157f3211a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_prefill_errors GUARD_OFF 9fbfea67",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if {CONF_HEAT_PUMP_MIN_POWER, CONF_HEAT_PUMP_MAX_POWER} & saved.keys():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json
new file mode 100644
index 000000000..4c267f126
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net RETURN_DEL 0531d42a",
+  "killed_by": "tests/features.py",
+  "old": "            return heat - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json
deleted file mode 100644
index 7f21935fc..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net RETURN_DEL 110923c2",
-  "killed_by": "tests/features.py",
-  "old": "            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 404a5fb0fb6041a9d430cbff08be9aae6fab4a21: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json
new file mode 100644
index 000000000..5406b2738
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate CMP_BOUND 394543d6",
+  "killed_by": "tests/features.py",
+  "old": "        return derate if derate < limit else DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return derate if derate <= limit else DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json
new file mode 100644
index 000000000..abb8fc695
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate GUARD_OFF 0035a9e4",
+  "killed_by": "tests/features.py",
+  "old": "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json
new file mode 100644
index 000000000..8ea6dac74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate RETURN_DEL 208f053a",
+  "killed_by": "tests/features.py",
+  "old": "    return DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json b/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json
new file mode 100644
index 000000000..9cf62ba52
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:delivered_heat_kw RETURN_DEL 88123fd9",
+  "killed_by": "tests/features.py",
+  "old": "    return cop * heat_per_cop_kw(params, electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json
new file mode 100644
index 000000000..7f44def31
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_per_cop_kw GUARD_OFF 54581fbd",
+  "killed_by": "tests/features.py",
+  "old": "    if params.cop_partload_derate:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json
new file mode 100644
index 000000000..c00c1ce2d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_per_cop_kw RETURN_DEL 6b4aef4f",
+  "killed_by": "tests/features.py",
+  "old": "    return electrical_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json
new file mode 100644
index 000000000..70cd1c63a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit CMP_BOUND ca26395f",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0 or band + p_max <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if band < 0.0 or band + p_max <= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json
new file mode 100644
index 000000000..e3023ba08
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit GUARD_OFF ca26395f",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0 or band + p_max <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json
new file mode 100644
index 000000000..ee2923417
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit RETURN_DEL 7ed3d385",
+  "killed_by": "tests/features.py",
+  "old": "    return band / (band + p_max)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json
new file mode 100644
index 000000000..a3ef990b0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor CLAMP_DROP e648cdad",
+  "killed_by": "tests/features.py",
+  "old": "    x = min(max(x, 0.0), 1.0) if np.ndim(x) == 0 else np.clip(x, 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`x = (max(x, 0.0)) if np.ndim(x) == 0 else np.clip(x, 0.0, 1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json
new file mode 100644
index 000000000..51dc3963e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor CMP_BOUND b007a1a8",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if band < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json
new file mode 100644
index 000000000..a0392305a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor GUARD_OFF b007a1a8",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json
new file mode 100644
index 000000000..a8f38068f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor RETURN_DEL dbcd7d83",
+  "killed_by": "tests/features.py",
+  "old": "    return 1.0 - params.cop_partload_derate * x",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
similarity index 54%
rename from tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json
rename to tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
index d8b47c613..8456afa0c 100644
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net CLAMP_DROP 110923c2",
-  "old": "            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
-  "reason": "Equivalent by construction, and measured. `net` is only ever evaluated at `hi`, `lo` and bisection midpoints between them, and `lo = max(20.0, cop_flow_reference_temp)` with TANK_ROOM_AMBIENT_TEMP = 20.0, so `temp - TANK_ROOM_AMBIENT_TEMP >= 0` at every call and `max(0.0, x)` is `x`. Measured on the F1.10 round-2 head (#1808, review of e964fb78): a differential driver (buffer_probe.py, kept with the PR's evidence) calls _buffer_charge_ceiling over 20736 inputs -- flow_curve_cop on/off, buffer_max_temp 25-75, cop_flow_reference_temp 0-50 (below and above the 20 \u00b0C ambient), one and two zones, three standby-loss scales incl. 0, max power 0.5-9 kW, outdoor -30 to 15 \u00b0C, humidity None/90 -- and spies the tank temperature every `net` call hands marginal_cop: 24468 evaluations, minimum 20.0 \u00b0C. Head vs the CLAMP_DROP mutant: 0 of 20736 ceilings differ.",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net CLAMP_DROP 0531d42a",
+  "old": "            return heat - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
+  "reason": "Equivalent by construction, and measured. `net` is only ever evaluated at `hi`, `lo` and bisection midpoints between them, and `lo = max(20.0, cop_flow_reference_temp)` with TANK_ROOM_AMBIENT_TEMP = 20.0, so `temp - TANK_ROOM_AMBIENT_TEMP >= 0` at every call and `max(0.0, x)` is `x`. Measured on the F1.10 round-2 head (#1808, review of e964fb78): a differential driver (buffer_probe.py, kept with the PR's evidence) calls _buffer_charge_ceiling over 20736 inputs -- flow_curve_cop on/off, buffer_max_temp 25-75, cop_flow_reference_temp 0-50 (below and above the 20 \u00b0C ambient), one and two zones, three standby-loss scales incl. 0, max power 0.5-9 kW, outdoor -30 to 15 \u00b0C, humidity None/90 -- and spies the tank temperature every `net` call hands marginal_cop: 24468 evaluations, minimum 20.0 \u00b0C. Head vs the CLAMP_DROP mutant: 0 of 20736 ceilings differ. Re-anchored at R10-COP-PARTLOAD: the line now returns `heat` for what was `p_max * cop`, and the measurement above was taken with the part-load derate at its default 0, where `heat` is exactly `p_max * cop`, so that run still describes this tree on a default install. For a configured derate the equivalence is analytic rather than measured: the term only scales `heat` down, which lowers `net` at every `temp` and cannot make the clamp's argument `temp - TANK_ROOM_AMBIENT_TEMP` negative, so `max(0.0, x)` stays `x` on every input the bisection can reach.",
   "verdict": "equivalent"
 }
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json
new file mode 100644
index 000000000..c24c036c8
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate CMP_BOUND 0035a9e4",
+  "old": "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:",
+  "reason": "An equivalent mutant on the probed domain, and the only disposition the ledger's one-row-per-anchor key allows: this anchor carries both comparison rewrites of `if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:`, and the lower one (`0.0 < derate ...`) cannot be killed. It separates the two arms at exactly one value, `derate == 0.0` and `-0.0`, where the tree returns `derate` and the mutant returns DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE -- both answer 0.0 (the two sign-only cells answer -0.0 against 0.0, numerically equal, and every caller multiplies its heat by 1.0 either way). Measured at d4f3e8b3c by `PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/r10_cop_partload_equiv.py`: `equiv_cells=40 differs=0 config_differs=0` -- 40 inputs (both bounds and their just-outside floats, +0.0 and -0.0, the non-finite floats, numeric strings, non-float types, numpy scalars), each driven directly and through `ThermalParameters.from_config`, with no differing answer; `ties=7` (the seven cells that are 0.0), `sign_only=2` (the -0.0 pair). The tie-only control differs on all 7 tied cells and on 0 untied ones, and `--identity` reads every count 0, so the comparison sees a difference where one exists. The anchor's other rewrite (`0.0 <= derate < MAX`) is NOT equivalent -- it answers the 0 default at 0.5 and differs on the four 0.5 cells (`positive_differs=4`, the probe's positive control) -- and it is killed: `mutation_table.py --pin-killed --scripts tests/features.py` at d4f3e8b3c records `...:1724 CMP_BOUND -- killed by tests/features.py, but its anchor also covers a site no run killed` for it beside `...:1724 CMP_BOUND -- lives` for the lower twin. The configured-derate check in tests/features.py now drives both 0.0 and 0.5, so it kills the upper twin; no check can kill the lower one, which is why this mark is `equivalent` and not a gap.",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index c96ada5d8..048e4ee1c 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -124,6 +124,7 @@ from .const import (
     CONF_HEAT_PUMP_COP_NOMINAL,
     CONF_HEAT_PUMP_MAX_POWER,
     CONF_HEAT_PUMP_MIN_POWER,
+    CONF_HEAT_PUMP_COP_PARTLOAD_DERATE,
     CONF_UPPER_FLOOR_THERMAL_MASS,
     CONF_LOWER_FLOOR_THERMAL_MASS,
     CONF_UPPER_FLOOR_HEAT_LOSS,
@@ -197,6 +198,7 @@ from .const import (
     DEFAULT_HEAT_PUMP_COP_NOMINAL,
     DEFAULT_HEAT_PUMP_MAX_POWER,
     DEFAULT_HEAT_PUMP_MIN_POWER,
+    MAX_HEAT_PUMP_COP_PARTLOAD_DERATE,
     DEFAULT_UPPER_FLOOR_THERMAL_MASS,
     DEFAULT_LOWER_FLOOR_THERMAL_MASS,
     DEFAULT_UPPER_FLOOR_HEAT_LOSS,
@@ -417,7 +419,7 @@ from . import (
     topology,
 )
 from .wood_fuel import wood_furnace_on
-from .thermal_model import ThermalParameters, _dhw_enabled_from_config
+from .thermal_model import ThermalParameters, _dhw_enabled_from_config, partload_derate_limit
 from .currency import money_scale, resolve_currency
 from .dhw_schedule import (
     ERROR_TOO_SHORT as DHW_ERROR_TOO_SHORT,
@@ -890,6 +892,22 @@ def _power_errors(
     return {}
 
 
+def _partload_errors(
+    candidate: dict[str, Any], current: dict[str, Any]
+) -> dict[str, str]:
+    """A part-load derate at or above its band's limit makes delivered heat
+    fall with power at the top of the band (``partload_derate_limit``), and
+    the model would refuse it to 0 unseen; the form says so on the field."""
+    derate = _effective(candidate, current, CONF_HEAT_PUMP_COP_PARTLOAD_DERATE, 0.0)
+    limit = partload_derate_limit(
+        _effective(candidate, current, CONF_HEAT_PUMP_MIN_POWER, DEFAULT_HEAT_PUMP_MIN_POWER),
+        _effective(candidate, current, CONF_HEAT_PUMP_MAX_POWER, DEFAULT_HEAT_PUMP_MAX_POWER),
+    )
+    if derate >= limit:  # the limit is positive, so 0 always passes
+        return {CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: "partload_derate_above_limit"}
+    return {}
+
+
 def _suggested_optional(current: dict[str, Any], key: str) -> Any:
     """An optional key that suggests the stored value, never defaults it.
 
@@ -1681,6 +1699,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("thermal_model", CONF_HEAT_PUMP_COP_NOMINAL, _SUGGESTED, _number(1.5, 6.0, 0.1)),
     _F("thermal_model", CONF_HEAT_PUMP_MAX_POWER, _SUGGESTED, _number(1, 20, 0.5, 'kW')),
     _F("thermal_model", CONF_HEAT_PUMP_MIN_POWER, _SUGGESTED, _number(0, 10, 0.5, 'kW')),
+    _F("thermal_model", CONF_HEAT_PUMP_COP_PARTLOAD_DERATE, _SUGGESTED, _number(0, MAX_HEAT_PUMP_COP_PARTLOAD_DERATE, 0.01)),
     # -- thermal_model_zones
     _F("thermal_model_zones", CONF_TWO_ZONE_MODE, _Suggested(TWO_ZONE_MODE_AUTO), _select(list(TWO_ZONE_MODES), 'two_zone_mode'), group="mode"),
     _F("thermal_model_zones", CONF_UPPER_FLOOR_THERMAL_MASS, _SUGGESTED, _number(*RANGE_ZONE_THERMAL_MASS, 0.5, 'kWh/°C'), group="zones"),
@@ -2151,8 +2170,13 @@ def _prefill_errors(saved: dict[str, Any], current: dict[str, Any]) -> dict[str,
         saved, current
     ):
         errors["base"] = "dhw_min_too_close"
-    if CONF_HEAT_PUMP_MAX_POWER in saved and _power_errors(saved, current):
-        errors["base"] = "min_power_above_max"
+    # Either half of the band moves the derate's limit, and the form shows
+    # neither the floor nor the derate, so each refusal lands on ``base``.
+    if {CONF_HEAT_PUMP_MIN_POWER, CONF_HEAT_PUMP_MAX_POWER} & saved.keys():
+        for problem in (
+            _power_errors(saved, current) or _partload_errors(saved, current)
+        ).values():
+            errors["base"] = problem
     return errors
 
 
@@ -3208,7 +3232,7 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         current = self._current
         if user_input is not None:
             user_input = _flatten_section_input(user_input)
-            errors = _power_errors(user_input, self._current)
+            errors = _power_errors(user_input, current) or _partload_errors(user_input, current)
             if not errors:
                 saved = dict(user_input)
                 _disarm_preset_on_derived_edit(saved, self._current)
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 8b887d423..7302a27d4 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -727,6 +727,7 @@ CONF_SLAB_HEAT_TRANSFER: Final = "slab_heat_transfer"  # kW/°C
 CONF_HEAT_PUMP_COP_NOMINAL: Final = "heat_pump_cop_nominal"
 CONF_HEAT_PUMP_MAX_POWER: Final = "heat_pump_max_power"  # kW electrical
 CONF_HEAT_PUMP_MIN_POWER: Final = "heat_pump_min_power"  # kW electrical
+CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: Final = "heat_pump_cop_partload_derate"
 
 # Two-zone model parameters
 #
@@ -1195,6 +1196,12 @@ DEFAULT_SLAB_HEAT_TRANSFER: Final = 0.8  # kW/°C - slab to room
 DEFAULT_HEAT_PUMP_COP_NOMINAL: Final = 3.5
 DEFAULT_HEAT_PUMP_MAX_POWER: Final = 5.0  # kW
 DEFAULT_HEAT_PUMP_MIN_POWER: Final = 1.0  # kW
+#: COP share lost at max power against min power. 0 prices no part-load
+#: effect: without a heat meter the slope is not observable on an install.
+DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE: Final = 0.0
+#: Upper bound on the configured derate; the plant grid of
+#: dev/audit/harnesses/r10_cop_partload.py spans 0.03-0.19 at fixed lift.
+MAX_HEAT_PUMP_COP_PARTLOAD_DERATE: Final = 0.5
 
 # Two-zone defaults
 DEFAULT_UPPER_FLOOR_THERMAL_MASS: Final = 3.0  # kWh/°C - lighter (radiators + air)
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 335721dda..1493e7792 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -99,6 +99,7 @@ from .thermal_model import (
     levels_clamped,
     planned_draw_runs,
     planned_draws_run,
+    delivered_heat_kw,
     project_planned_levels,
     valve_charge_demand,
     weather_or_calm,
@@ -5138,13 +5139,13 @@ class HeatPumpOptimizer:
         # as the settlement caps themselves.
         q_house = max(0.0, u_house * (target - out_mean) - p.internal_gains)
         ua_tank = p.buffer_tank_heat_loss_coefficient
-        p_max = p.max_electrical_power
 
         def net(temp: float) -> float:
             cop = self.model.marginal_cop(
                 out_mean, "buffer", store_temp=temp, humidity=humidity
             )
-            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)
+            heat: float = delivered_heat_kw(p, cop, p.max_electrical_power)
+            return heat - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)
 
         if net(hi) > 0.0:
             return hi
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index cfafd808d..67ef0dc61 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -991,6 +991,7 @@
           "heat_pump_cop_nominal": "Heat pump nominal COP",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "heat_pump_min_power": "Heat pump min power (kW)",
+          "heat_pump_cop_partload_derate": "Heat pump COP loss at max power",
           "after_save": "After saving"
         },
         "data_description": {
@@ -1001,6 +1002,7 @@
           "heat_pump_cop_nominal": "Units of heat produced per unit of electricity under normal conditions. Check the data sheet; 3 to 4 is typical for air-to-water, 4 to 5 for ground source.",
           "heat_pump_max_power": "Electrical input at full output. Caps how much cheap electricity can be stored per hour.",
           "heat_pump_min_power": "Lowest electrical input the pump can run at without cycling on and off.",
+          "heat_pump_cop_partload_derate": "Share of efficiency lost running at max power rather than min power, as a fraction (0.1 = 10 %). Larger heat flows need larger temperature differences across the heat exchangers. 0 leaves power out of the COP; typical air-to-water units lose 0.05 to 0.15. A heat meter is not needed. Keep it below band / (band + max power), band being max minus min power, or heat would fall as power rises.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1519,6 +1521,7 @@
       "night_above_day": "The night temperature is above the day temperature.",
       "day_window_empty": "The day would end at or before it starts, leaving no daytime period at all.",
       "comfort_outside_band": "Day and night comfort temperatures must sit inside the comfort band",
+      "partload_derate_above_limit": "This COP loss is too steep for the power band: delivered heat would fall as power rises towards maximum. Keep it below band / (band + maximum power), where band is maximum minus minimum power: below 0.44 for a 1-5 kW pump, below 0.17 for a 4-5 kW one.",
       "min_power_above_max": "The heat pump's minimum power is above its maximum power.",
       "stored_value_out_of_range": "This value is outside the range this field normally accepts. The range was widened so the page can still be saved — check the value, and correct it if it looks wrong.",
       "flow_target_needs_two_zone": "\"Flow temperature\" derives from the two-zone building model's own flow curve, which this entry does not have configured. Configure the two-zone model first, or leave this at \"Indoor temperature\".",
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 4d2609673..60a687f5c 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -53,6 +53,8 @@ from .const import (
     DEFAULT_HEAT_PUMP_COP_NOMINAL,
     DEFAULT_HEAT_PUMP_MAX_POWER,
     DEFAULT_HEAT_PUMP_MIN_POWER,
+    DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE,
+    MAX_HEAT_PUMP_COP_PARTLOAD_DERATE,
     DEFAULT_COP_SCALE,
     DEFAULT_UPPER_FLOOR_THERMAL_MASS,
     DEFAULT_LOWER_FLOOR_THERMAL_MASS,
@@ -277,6 +279,7 @@ class ThermalParameters:
             if not np.isfinite(value) or value < POSITIVE_PARAM_FLOOR:
                 value = POSITIVE_PARAM_FLOOR
             setattr(self, name, value)
+        self.cop_partload_derate = _partload_derate(self.cop_partload_derate, self)
 
     @property
     def buffer_is_store(self) -> bool:
@@ -513,6 +516,7 @@ class ThermalParameters:
     cop_reference_temp: float = 7.0  # °C
     max_electrical_power: float = DEFAULT_HEAT_PUMP_MAX_POWER  # kW
     min_electrical_power: float = DEFAULT_HEAT_PUMP_MIN_POWER  # kW
+    cop_partload_derate: float = DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE
     # Learned multiplicative correction to the modelled COP curve. 1.0 leaves
     # the nameplate-derived curve untouched; the coordinator moves it only when
     # a measured power entity makes real efficiency observable.
@@ -909,132 +913,81 @@ class ThermalParameters:
         they need validating, deriving from another field, or defaulting on
         absence rather than on value.
         """
+        # field name -> the name its CONF_ key and DEFAULT_ value share in
+        # ``const``, resolved by name so the table stays readable and a missing
+        # constant raises rather than silently substituting a default.
         table = {
             # Single-zone / legacy
-            "room_thermal_mass": ("HOUSE_THERMAL_MASS", "HOUSE_THERMAL_MASS"),
-            "slab_thermal_mass": ("SLAB_THERMAL_MASS", "SLAB_THERMAL_MASS"),
-            "heat_loss_coefficient": (
-                "HOUSE_HEAT_LOSS_COEFFICIENT", "HOUSE_HEAT_LOSS_COEFFICIENT"
-            ),
-            "slab_heat_transfer": ("SLAB_HEAT_TRANSFER", "SLAB_HEAT_TRANSFER"),
+            "room_thermal_mass": "HOUSE_THERMAL_MASS",
+            "slab_thermal_mass": "SLAB_THERMAL_MASS",
+            "heat_loss_coefficient": "HOUSE_HEAT_LOSS_COEFFICIENT",
+            "slab_heat_transfer": "SLAB_HEAT_TRANSFER",
             # Two-zone
-            "upper_floor_thermal_mass": (
-                "UPPER_FLOOR_THERMAL_MASS", "UPPER_FLOOR_THERMAL_MASS"
-            ),
-            "lower_floor_thermal_mass": (
-                "LOWER_FLOOR_THERMAL_MASS", "LOWER_FLOOR_THERMAL_MASS"
-            ),
-            "upper_floor_heat_loss": (
-                "UPPER_FLOOR_HEAT_LOSS", "UPPER_FLOOR_HEAT_LOSS"
-            ),
-            "lower_floor_heat_loss": (
-                "LOWER_FLOOR_HEAT_LOSS", "LOWER_FLOOR_HEAT_LOSS"
-            ),
-            "inter_zone_transfer": ("INTER_ZONE_TRANSFER", "INTER_ZONE_TRANSFER"),
-            "radiator_power_fraction": (
-                "RADIATOR_POWER_FRACTION", "RADIATOR_POWER_FRACTION"
-            ),
-            "upper_floor_area_ratio": (
-                "UPPER_FLOOR_AREA_RATIO", "UPPER_FLOOR_AREA_RATIO"
-            ),
+            "upper_floor_thermal_mass": "UPPER_FLOOR_THERMAL_MASS",
+            "lower_floor_thermal_mass": "LOWER_FLOOR_THERMAL_MASS",
+            "upper_floor_heat_loss": "UPPER_FLOOR_HEAT_LOSS",
+            "lower_floor_heat_loss": "LOWER_FLOOR_HEAT_LOSS",
+            "inter_zone_transfer": "INTER_ZONE_TRANSFER",
+            "radiator_power_fraction": "RADIATOR_POWER_FRACTION",
+            "upper_floor_area_ratio": "UPPER_FLOOR_AREA_RATIO",
             # Buffer tank
-            "buffer_tank_volume": ("BUFFER_TANK_VOLUME", "BUFFER_TANK_VOLUME"),
-            "buffer_tank_heat_loss": ("BUFFER_TANK_LOSS", "BUFFER_TANK_LOSS"),
+            "buffer_tank_volume": "BUFFER_TANK_VOLUME",
+            "buffer_tank_heat_loss": "BUFFER_TANK_LOSS",
             # Solar gain
-            "window_area": ("WINDOW_AREA", "WINDOW_AREA"),
-            "solar_orientation_factor": (
-                "SOLAR_ORIENTATION_FACTOR", "SOLAR_ORIENTATION_FACTOR"
-            ),
-            "solar_heat_gain_coefficient": (
-                "SOLAR_HEAT_GAIN_COEFF", "SOLAR_HEAT_GAIN_COEFF"
-            ),
-            "solar_upper_fraction": (
-                "SOLAR_UPPER_FRACTION", "SOLAR_UPPER_FRACTION"
-            ),
+            "window_area": "WINDOW_AREA",
+            "solar_orientation_factor": "SOLAR_ORIENTATION_FACTOR",
+            "solar_heat_gain_coefficient": "SOLAR_HEAT_GAIN_COEFF",
+            "solar_upper_fraction": "SOLAR_UPPER_FRACTION",
             # Hot water
-            "dhw_tank_volume": ("DHW_TANK_VOLUME", "DHW_TANK_VOLUME"),
-            "dhw_setpoint": ("DHW_SETPOINT", "DHW_SETPOINT"),
-            "dhw_min_temp": ("DHW_MIN_TEMP", "DHW_MIN_TEMP"),
-            "dhw_daily_consumption": (
-                "DHW_DAILY_CONSUMPTION", "DHW_DAILY_CONSUMPTION"
-            ),
-            "dhw_cooling_rate": ("DHW_COOLING_RATE", "DHW_COOLING_RATE"),
-            "dhw_idle_min_temp": ("DHW_IDLE_MIN_TEMP", "DHW_IDLE_MIN_TEMP"),
-            "dhw_legionella_temp": (
-                "DHW_LEGIONELLA_TEMP", "DHW_LEGIONELLA_TEMP"
-            ),
-            "dhw_legionella_interval_days": (
-                "DHW_LEGIONELLA_INTERVAL_DAYS", "DHW_LEGIONELLA_INTERVAL_DAYS"
-            ),
+            "dhw_tank_volume": "DHW_TANK_VOLUME",
+            "dhw_setpoint": "DHW_SETPOINT",
+            "dhw_min_temp": "DHW_MIN_TEMP",
+            "dhw_daily_consumption": "DHW_DAILY_CONSUMPTION",
+            "dhw_cooling_rate": "DHW_COOLING_RATE",
+            "dhw_idle_min_temp": "DHW_IDLE_MIN_TEMP",
+            "dhw_legionella_temp": "DHW_LEGIONELLA_TEMP",
+            "dhw_legionella_interval_days": "DHW_LEGIONELLA_INTERVAL_DAYS",
             # Hot water, v4.0.0 T3. None of these joins the dhw_enabled
             # presence trio below — a configured inlet must never phantom-
             # enable hot water on an entry that has none.
-            "dhw_inlet_temp": ("DHW_INLET_TEMP", "DHW_INLET_TEMP"),
-            "dhw_inlet_seasonal_amplitude": (
-                "DHW_INLET_SEASONAL_AMPLITUDE", "DHW_INLET_SEASONAL_AMPLITUDE"
-            ),
-            "greywater_recovery": ("GREYWATER_RECOVERY", "GREYWATER_RECOVERY"),
-            "dhw_legionella_min_interval_days": (
-                "DHW_LEGIONELLA_MIN_INTERVAL_DAYS",
-                "DHW_LEGIONELLA_MIN_INTERVAL_DAYS",
-            ),
+            "dhw_inlet_temp": "DHW_INLET_TEMP",
+            "dhw_inlet_seasonal_amplitude": "DHW_INLET_SEASONAL_AMPLITUDE",
+            "greywater_recovery": "GREYWATER_RECOVERY",
+            "dhw_legionella_min_interval_days": "DHW_LEGIONELLA_MIN_INTERVAL_DAYS",
             # Learned corrections
-            "buffer_cooling_rate": ("BUFFER_COOLING_RATE", "BUFFER_COOLING_RATE"),
-            "house_heat_loss_scale": (
-                "HOUSE_HEAT_LOSS_SCALE", "HOUSE_HEAT_LOSS_SCALE"
-            ),
-            "lower_floor_loss_ratio": (
-                "LOWER_FLOOR_LOSS_RATIO", "LOWER_FLOOR_LOSS_RATIO"
-            ),
+            "buffer_cooling_rate": "BUFFER_COOLING_RATE",
+            "house_heat_loss_scale": "HOUSE_HEAT_LOSS_SCALE",
+            "lower_floor_loss_ratio": "LOWER_FLOOR_LOSS_RATIO",
             # Weather sensitivity
-            "wind_sensitivity": ("WIND_SENSITIVITY", "WIND_SENSITIVITY"),
-            "rain_heat_loss_multiplier": (
-                "RAIN_HEAT_LOSS_MULTIPLIER", "RAIN_HEAT_LOSS_MULTIPLIER"
-            ),
+            "wind_sensitivity": "WIND_SENSITIVITY",
+            "rain_heat_loss_multiplier": "RAIN_HEAT_LOSS_MULTIPLIER",
             # ECL110 heat curve control
-            "ecl110_displace_min": (
-                "ECL110_DISPLACE_MIN", "ECL110_DISPLACE_MIN"
-            ),
-            "ecl110_displace_max": (
-                "ECL110_DISPLACE_MAX", "ECL110_DISPLACE_MAX"
-            ),
-            "ecl110_pid_time_constant_hours": (
-                "ECL110_PID_TIME_CONSTANT", "ECL110_PID_TIME_CONSTANT"
-            ),
+            "ecl110_displace_min": "ECL110_DISPLACE_MIN",
+            "ecl110_displace_max": "ECL110_DISPLACE_MAX",
+            "ecl110_pid_time_constant_hours": "ECL110_PID_TIME_CONSTANT",
             # Heat pump
-            "cop_nominal": ("HEAT_PUMP_COP_NOMINAL", "HEAT_PUMP_COP_NOMINAL"),
-            "max_electrical_power": (
-                "HEAT_PUMP_MAX_POWER", "HEAT_PUMP_MAX_POWER"
-            ),
-            "min_electrical_power": (
-                "HEAT_PUMP_MIN_POWER", "HEAT_PUMP_MIN_POWER"
-            ),
+            "cop_nominal": "HEAT_PUMP_COP_NOMINAL",
+            "max_electrical_power": "HEAT_PUMP_MAX_POWER",
+            "min_electrical_power": "HEAT_PUMP_MIN_POWER",
+            "cop_partload_derate": "HEAT_PUMP_COP_PARTLOAD_DERATE",
         }
 
         values = {
             name: config.get(
-                getattr(const, f"CONF_{conf}"), getattr(const, f"DEFAULT_{default}")
+                getattr(const, f"CONF_{key}"), getattr(const, f"DEFAULT_{key}")
             )
-            for name, (conf, default) in table.items()
+            for name, key in table.items()
         }
 
         # Booleans are coerced because a config entry may carry a string.
-        for name, conf, default in (
-            ("dhw_schedule_enabled", "DHW_SCHEDULE_ENABLED", "DHW_SCHEDULE_ENABLED"),
-            (
-                "dhw_legionella_enabled",
-                "DHW_LEGIONELLA_ENABLED",
-                "DHW_LEGIONELLA_ENABLED",
-            ),
-            (
-                "dhw_elastic_legionella_enabled",
-                "DHW_ELASTIC_LEGIONELLA_ENABLED",
-                "DHW_ELASTIC_LEGIONELLA_ENABLED",
-            ),
+        for name, key in (
+            ("dhw_schedule_enabled", "DHW_SCHEDULE_ENABLED"),
+            ("dhw_legionella_enabled", "DHW_LEGIONELLA_ENABLED"),
+            ("dhw_elastic_legionella_enabled", "DHW_ELASTIC_LEGIONELLA_ENABLED"),
         ):
             values[name] = bool(
                 config.get(
-                    getattr(const, f"CONF_{conf}"), getattr(const, f"DEFAULT_{default}")
+                    getattr(const, f"CONF_{key}"), getattr(const, f"DEFAULT_{key}")
                 )
             )
         return values
@@ -1048,9 +1001,6 @@ class ThermalParameters:
         fields that need validating against a set of legal values, deriving
         from another field, or defaulting on *absence* rather than on value.
         """
-        # field name -> (config key, default). Both are resolved from ``const``
-        # by name so the table stays readable and a missing constant fails
-        # loudly at import rather than silently substituting a default.
         values = cls._tabled_values(config)
 
 
@@ -2038,6 +1988,81 @@ def _two_tank_rates(
     )
 
 
+def partload_derate_limit(min_power: Any, max_power: Any) -> float:
+    """The derate at which delivered heat stops rising with power on the band.
+
+    ``heat = cop * P * (1 - d * (P - p_min) / band)`` has slope
+    ``cop * (1 - d * (band + p_max) / band)`` at ``p_max``, its least on the
+    band, so heat rises across the whole band exactly while ``d`` is below
+    ``band / (band + p_max)``; at or above it more power buys less heat, which
+    no vapour-compression pump does. Infinite for an empty band, where the
+    factor is 1 and a derate prices nothing."""
+    p_min = const.finite_float(min_power, DEFAULT_HEAT_PUMP_MIN_POWER)
+    p_max = const.finite_float(max_power, DEFAULT_HEAT_PUMP_MAX_POWER)
+    band = p_max - p_min
+    if band <= 0.0 or band + p_max <= 0.0:
+        return float("inf")
+    return band / (band + p_max)
+
+
+def _partload_derate(value: Any, params: ThermalParameters | None = None) -> float:
+    """A configured part-load derate, or the 0 default when it is not a
+    number inside [0, ``MAX_HEAT_PUMP_COP_PARTLOAD_DERATE``] or, given the
+    parameters, not strictly below their band's ``partload_derate_limit``.
+
+    Refused to 0 rather than clamped to the limit: a clamp would price a
+    derate nobody configured, and the limit itself is a pump whose heat stops
+    rising at max power. 0 is the term off, every plan as it was before it,
+    and the options page names the refusal on the field."""
+    derate = const.finite_float(value, DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE)
+    limit = float("inf") if params is None else partload_derate_limit(
+        params.min_electrical_power, params.max_electrical_power)
+    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:
+        return derate if derate < limit else DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE
+    return DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE
+
+
+def partload_factor(params: ThermalParameters, electrical_power: Any) -> Any:
+    """COP multiplier at ``electrical_power`` kW: 1 at or below the modulation
+    floor (a lower draw duty-cycles at the floor), falling linearly to
+    ``1 - cop_partload_derate`` at max power, as heat-exchanger approach grows
+    with the heat rate. The hot-water schedule takes it too, on top of its own
+    tank lift (``compute_cop_dhw``). Elementwise, so the batch twin's rows and
+    the scalar step share it."""
+    band = params.max_electrical_power - params.min_electrical_power
+    if band <= 0.0:
+        return 1.0
+    x = (electrical_power - params.min_electrical_power) / band
+    # min/max keep a scalar a float; np.clip is the same IEEE op per row.
+    x = min(max(x, 0.0), 1.0) if np.ndim(x) == 0 else np.clip(x, 0.0, 1.0)
+    return 1.0 - params.cop_partload_derate * x
+
+
+def heat_per_cop_kw(params: ThermalParameters, electrical_power: Any) -> Any:
+    """Heat per unit of COP at ``electrical_power`` kW: the draw itself while
+    the derate is 0, else the draw times its part-load factor.
+
+    It depends on the draw alone, so a loop whose COP moves per sub-step
+    (the batch twin, the hot-water refresh) takes it once for the whole
+    schedule and multiplies by each step's COP, instead of re-deriving it in
+    every sub-step: that per-sub-step call was stress.py's production-call
+    channel firing at 1.051x-1.064x. Elementwise, like ``partload_factor``,
+    so a schedule's rows and a scalar step get the same IEEE product."""
+    if params.cop_partload_derate:
+        return electrical_power * partload_factor(params, electrical_power)
+    return electrical_power
+
+
+def delivered_heat_kw(params: ThermalParameters, cop: Any, electrical_power: Any) -> Any:
+    """Heat the pump delivers at ``cop`` and ``electrical_power``, space or hot
+    water: ``cop`` times :func:`heat_per_cop_kw`, the one association every
+    conversion uses, so the scalar step and the batch twin stay bitwise.
+
+    Exactly ``cop * electrical_power`` while the derate is 0, so a plan with
+    no part-load term is byte-identical to one priced before it."""
+    return cop * heat_per_cop_kw(params, electrical_power)
+
+
 def _copy_state_with(state: ThermalState, **changes: object) -> ThermalState:
     """Shallow-copy ``state`` with ``changes`` applied, field-for-field the
     same result as ``dataclasses.replace(state, **changes)``.
@@ -3059,19 +3084,19 @@ class ThermalModel:
         humidity: np.ndarray | None = None,
     ) -> np.ndarray:
         """Refresh ``temps[from_step + 1:]`` after the schedule changed there."""
-        schedule = np.asarray(dhw_power_schedule, dtype=float)
+        heat_per_cop = heat_per_cop_kw(self.params, np.asarray(dhw_power_schedule, dtype=float))
         outdoor = np.asarray(outdoor_temps, dtype=float)
         draws = np.asarray(draw_rates, dtype=float)
         temp = float(temps[from_step])
         compute_cop = self.compute_cop_dhw
         simulate_step = self.simulate_dhw_step
-        for i in range(from_step, schedule.size):
+        for i in range(from_step, heat_per_cop.size):
             cop = compute_cop(
                 outdoor[i], temp, humidity=None if humidity is None else humidity[i]
             )
             temp = simulate_step(
                 dhw_temp=temp,
-                dhw_power_thermal=cop * schedule[i],
+                dhw_power_thermal=cop * heat_per_cop[i],
                 hour_of_day=0.0,
                 dt_hours=dt_hours,
                 draw_power=draws[i],
@@ -3128,7 +3153,7 @@ class ThermalModel:
         # where a flow meter read it (#2016) and inferred from the draw and
         # this step's COP everywhere else.
         pump_heat_kw = (
-            cop * electrical_power
+            cop * heat_per_cop_kw(self.params, electrical_power)
             if measured_heat_kw is None
             else measured_heat_kw
         )
@@ -3253,7 +3278,7 @@ class ThermalModel:
         # flow meter read it (#2016) and inferred from the draw and this
         # step's COP everywhere else.
         pump_heat_kw = (
-            cop * electrical_power
+            cop * heat_per_cop_kw(self.params, electrical_power)
             if measured_heat_kw is None
             else measured_heat_kw
         )
@@ -3400,7 +3425,7 @@ class ThermalModel:
 
         ``measured_heat_kw`` is the pump's thermal output for this step as a
         meter read it (#2016), and it stands in for the
-        ``cop * electrical_power`` both zone steps would otherwise infer; free
+        ``delivered_heat_kw`` both zone steps would otherwise infer; free
         external heat joins it exactly as before. ``None`` -- the default, and
         what every planning call passes, a horizon holding no measurement --
         leaves Q_hp inferred, byte-for-byte the previous behaviour. Trusted
@@ -3848,24 +3873,24 @@ class ThermalModel:
         buffer, wood (None when not modelled), plus refused [B, n].
         """
         p = self.params
-        power_matrix = np.asarray(power_matrix, dtype=float)
+        heat_per_cop = heat_per_cop_kw(p, np.asarray(power_matrix, dtype=float))
         outdoor_temps = weather.outdoor_temps
         wind_speeds = weather.wind_speeds
         precipitation = weather.precipitation
         solar_radiation = weather.solar_radiation
         humidity = weather.humidity
         external_heat_kw = weather.external_heat_kw
-        n_steps = power_matrix.shape[1]
+        n_steps = heat_per_cop.shape[1]
         wind_speeds, precipitation, solar_radiation = weather_or_calm(
             n_steps, wind_speeds, precipitation, solar_radiation
         )
 
-        room = np.zeros((power_matrix.shape[0], n_steps + 1))
+        room = np.zeros((heat_per_cop.shape[0], n_steps + 1))
         slab = np.zeros_like(room)
         upper = np.zeros_like(room)
         lower = np.zeros_like(room)
         buf = np.zeros_like(room)
-        refused = np.zeros((power_matrix.shape[0], n_steps))
+        refused = np.zeros((heat_per_cop.shape[0], n_steps))
         wood = None
         if initial_state.wood_tank_temperature is not None:
             wood = np.zeros_like(room)
@@ -3931,7 +3956,7 @@ class ThermalModel:
             wind_i = float(wind_speeds[i])
             rain_i = float(precipitation[i])
             sol_i = float(solar_radiation[i])
-            power_i = power_matrix[:, i]
+            heat_per_cop_i = heat_per_cop[:, i]
             ext_i = (
                 float(external_heat_kw[i])
                 if external_heat_kw is not None
@@ -3962,12 +3987,12 @@ class ThermalModel:
                     q_buf_loss = p.buffer_tank_heat_loss_coefficient * (
                         T_buf - TANK_ROOM_AMBIENT_TEMP
                     )
-                    # COP: only the flow-temp correction varies per element;
-                    # the scalar law lives in _batch_cop so this method's
-                    # size stays paid for.
+                    # COP: only the flow-temp correction varies per element
+                    # (the scalar law is _batch_cop's); the draws' heat per
+                    # unit COP was taken once for the whole batch above.
                     cop = self._batch_cop(out_i, hum_i, T_buf, throttled)
                     thermal_power = (
-                        cop * power_i + (0.0 if two_tank else ext)
+                        cop * heat_per_cop_i + (0.0 if two_tank else ext)
                     )
                     if throttled:
                         target = (
@@ -4099,7 +4124,7 @@ class ThermalModel:
                     # T_room is seeded with the other states above the step
                     # loop and carried across sub-steps from there.
                     cop = self._batch_cop(out_i, hum_i, T_buf, throttled)
-                    thermal_power = cop * power_i + ext
+                    thermal_power = cop * heat_per_cop_i + ext
                     if throttled:
                         # The scalar step's own law, called: one copy of it
                         # beats the calls, and this family is re-planned by
@@ -4261,7 +4286,7 @@ class ThermalModel:
                     float(humidity[i]) if humidity is not None else None
                 ),
             )
-            dhw_thermal_power = cop_dhw * dhw_power_schedule[i]
+            dhw_thermal_power = cop_dhw * heat_per_cop_kw(self.params, dhw_power_schedule[i])
 
             new_dhw = self.simulate_dhw_step(
                 dhw_temp=state.dhw_temperature,
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index d40286c9a..950f65ad6 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -991,6 +991,7 @@
           "heat_pump_cop_nominal": "Heat pump nominal COP",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "heat_pump_min_power": "Heat pump min power (kW)",
+          "heat_pump_cop_partload_derate": "Heat pump COP loss at max power",
           "after_save": "After saving"
         },
         "data_description": {
@@ -1001,6 +1002,7 @@
           "heat_pump_cop_nominal": "Units of heat produced per unit of electricity under normal conditions. Check the data sheet; 3 to 4 is typical for air-to-water, 4 to 5 for ground source.",
           "heat_pump_max_power": "Electrical input at full output. Caps how much cheap electricity can be stored per hour.",
           "heat_pump_min_power": "Lowest electrical input the pump can run at without cycling on and off.",
+          "heat_pump_cop_partload_derate": "Share of efficiency lost running at max power rather than min power, as a fraction (0.1 = 10 %). Larger heat flows need larger temperature differences across the heat exchangers. 0 leaves power out of the COP; typical air-to-water units lose 0.05 to 0.15. A heat meter is not needed. Keep it below band / (band + max power), band being max minus min power, or heat would fall as power rises.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1519,6 +1521,7 @@
       "night_above_day": "The night temperature is above the day temperature.",
       "day_window_empty": "The day would end at or before it starts, leaving no daytime period at all.",
       "comfort_outside_band": "Day and night comfort temperatures must sit inside the comfort band",
+      "partload_derate_above_limit": "This COP loss is too steep for the power band: delivered heat would fall as power rises towards maximum. Keep it below band / (band + maximum power), where band is maximum minus minimum power: below 0.44 for a 1-5 kW pump, below 0.17 for a 4-5 kW one.",
       "min_power_above_max": "The heat pump's minimum power is above its maximum power.",
       "stored_value_out_of_range": "This value is outside the range this field normally accepts. The range was widened so the page can still be saved — check the value, and correct it if it looks wrong.",
       "flow_target_needs_two_zone": "\"Flow temperature\" derives from the two-zone building model's own flow curve, which this entry does not have configured. Configure the two-zone model first, or leave this at \"Indoor temperature\".",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 02e7f7ffe..4f9a20669 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -991,6 +991,7 @@
           "heat_pump_cop_nominal": "Värmepumpens nominella COP",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
           "heat_pump_min_power": "Värmepump min effekt (kW)",
+          "heat_pump_cop_partload_derate": "Värmepumpens COP-förlust vid maxeffekt",
           "after_save": "Efter sparande"
         },
         "data_description": {
@@ -1001,6 +1002,7 @@
           "heat_pump_cop_nominal": "Enheter värme per enhet el under normala förhållanden. Se databladet; 3 till 4 är vanligt för luft/vatten, 4 till 5 för bergvärme.",
           "heat_pump_max_power": "Eleffekt vid full drift. Sätter taket för hur mycket billig el som kan lagras per timme.",
           "heat_pump_min_power": "Lägsta eleffekt pumpen klarar utan att börja starta och stanna.",
+          "heat_pump_cop_partload_derate": "Andel av verkningsgraden som går förlorad vid maxeffekt jämfört med mineffekt, som bråkdel (0,1 = 10 %). Större värmeflöden kräver större temperaturskillnad över värmeväxlarna. 0 låter effekten vara utan inverkan på COP; vanliga luft/vatten-pumpar förlorar 0,05 till 0,15. Ingen värmemätare behövs. Håll den under band / (band + maxeffekt), där bandet är max- minus mineffekt, annars sjunker värmen när effekten stiger.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
       },
@@ -1517,6 +1519,7 @@
       "night_above_day": "Nattemperaturen ligger över dagtemperaturen.",
       "day_window_empty": "Dagen skulle sluta innan den börjar, så ingen dagperiod blir kvar alls.",
       "comfort_outside_band": "Dag- och nattkomforttemperaturer måste ligga inom komfortbandet",
+      "partload_derate_above_limit": "Den här COP-förlusten är för brant för effektbandet: levererad värme skulle sjunka när effekten närmar sig max. Håll den under band / (band + maxeffekt), där bandet är max- minus mineffekt: under 0,44 för en pump på 1–5 kW, under 0,17 för en på 4–5 kW.",
       "min_power_above_max": "Värmepumpens lägsta effekt ligger över dess högsta.",
       "stored_value_out_of_range": "Det här värdet ligger utanför det intervall fältet normalt godtar. Intervallet har vidgats så att sidan ändå går att spara – kontrollera värdet och ändra det om det ser fel ut.",
       "flow_target_needs_two_zone": "\"Framledningstemperatur\" beräknas från tvåzonsmodellens egen flödeskurva, som denna anläggning inte har konfigurerad. Konfigurera tvåzonsmodellen först, eller lämna detta på \"Inomhustemperatur\".",
diff --git a/dev/audit/harnesses/r10_cop_partload.py b/dev/audit/harnesses/r10_cop_partload.py
new file mode 100644
index 000000000..9b24e0494
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_partload.py
@@ -0,0 +1,232 @@
+"""R10-COP-PARTLOAD: does COP depend on compressor power enough to plan on?
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r10_cop_partload.py [--no-solves]
+
+Synthetic throughout; no private data, no heat meter. The tree's own COP law
+(``ThermalModel.compute_cop``) has no power argument, so a synthetic install
+built from it measures a part-load effect of exactly zero by construction.
+The plant here is therefore independent of that law: one vapour-compression
+cycle at a fixed fraction of Carnot, whose condensing temperature sits above
+the supply water by ``Q / UA_COND`` and whose evaporating temperature sits
+below the air by ``Q_evap / UA_EVAP``, plus a constant auxiliary draw (fan,
+controls). The cycle fraction is calibrated so the plant equals the model's
+COP at the band's midpoint; only ratios are printed. Four parts:
+
+1. ``partload``: COP against electrical power across the configured band at a
+   fixed lift (outdoor 5 degC, supply water 35 degC), as a ratio to the
+   band's best, on every plant of the sensitivity grid (UA_COND, UA_EVAP,
+   aux). ``null``: an infinite-UA, zero-aux plant must read 1.000 at every
+   power, or the instrument invents the effect.
+2. ``burst``: the supply-temperature rise of a burst at ``p_max`` over a step
+   at ``p_min`` at a fixed return (30 degC) and water flow, and the COP that
+   rise costs through the tree's own ``flow_lift_factor``. ``null``: equal
+   powers rise 0 K.
+3. ``solves`` (skipped with ``--no-solves``): R10-SETPOINT-BOOST's 16
+   synthetic installs at its spread and flat price days, solved by the tree
+   with no term (``d=0``; its plan sha1 is the byte-identity null across
+   trees) and, where the tree has the term, at the central plant's own derate.
+   Each published space plan is re-priced on the central plant: the share of
+   planned heat the plant would not deliver, the cost per delivered kWh, and
+   its gain over a counterfactual delivering the same plant heat at one
+   constant power. ``gain`` > 0 means the shaped plan beats the flat one with
+   the part-load physics charged against it; the flat-price day is the null,
+   where shaping buys no price and the term's cost is all that is left.
+   ``term vs none`` is the term's effect on cost per delivered kWh.
+"""
+from __future__ import annotations
+
+import sys
+
+import numpy as np
+
+from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
+
+K0 = 273.15
+P_MIN, P_MAX = 1.5, 5.0
+OUTDOOR_C, SUPPLY_C, RETURN_C = 5.0, 35.0, 30.0
+#: Water capacity rate, kW/K: 0.4 kg/s x 4.19 kJ/(kg K), a 5 K spread at ~8 kW.
+MCP_KW_K = 1.68
+#: Central plant: plate condenser and finned air coil sized for a ~15 kW heat
+#: output at ~3 K and ~6 K approach; 60 W of fan and controls.
+CENTRAL = (5.0, 2.0, 0.06)
+GRID = [(uc, ue, aux) for uc in (2.5, 5.0, 10.0) for ue in (1.0, 2.0, 4.0)
+        for aux in (0.03, 0.06, 0.15)]
+NULL_PLANT = (1e9, 1e9, 0.0)
+
+
+def plant_cop(p_el: float, ua_c: float, ua_e: float, aux: float, eta: float,
+              supply_c: float | None = SUPPLY_C, return_c: float = RETURN_C) -> tuple[float, float]:
+    """Delivered COP and supply temperature at electrical draw ``p_el``.
+
+    ``supply_c`` fixes the water lift; ``None`` fixes the return instead and
+    lets the supply rise with the heat rate (the burst case)."""
+    p_comp = p_el - aux
+    cop_cycle, sup = 3.0, supply_c if supply_c is not None else return_c
+    for _ in range(200):
+        q = p_comp * cop_cycle
+        sup = supply_c if supply_c is not None else return_c + q / MCP_KW_K
+        t_c = sup + K0 + q / ua_c
+        t_e = OUTDOOR_C + K0 - (q - p_comp) / ua_e
+        new = eta * t_c / max(t_c - t_e, 1.0)
+        if abs(new - cop_cycle) < 1e-12:
+            break
+        cop_cycle = 0.5 * (cop_cycle + new)
+    return p_comp * cop_cycle / p_el, sup
+
+
+def calibrate(plant: tuple[float, float, float], target: float) -> float:
+    mid = 0.5 * (P_MIN + P_MAX)
+    lo, hi = 0.05, 1.0
+    for _ in range(100):
+        eta = 0.5 * (lo + hi)
+        if plant_cop(mid, *plant, eta)[0] < target:
+            lo = eta
+        else:
+            hi = eta
+    return 0.5 * (lo + hi)
+
+
+def ratio_curve(plant, target, powers, **kw) -> np.ndarray:
+    eta = calibrate(plant, target)
+    cops = np.array([plant_cop(p, *plant, eta, **kw)[0] for p in powers])
+    return cops / cops.max()
+
+
+def partload(model: ThermalModel) -> np.ndarray:
+    target = model.compute_cop(OUTDOOR_C, flow_temp=SUPPLY_C)
+    powers = np.linspace(P_MIN, P_MAX, 8)
+    print(f"partload: outdoor {OUTDOOR_C} supply {SUPPLY_C} model COP {target:.3f} "
+          f"powers {np.round(powers, 2).tolist()}")
+    null = ratio_curve(NULL_PLANT, target, powers)
+    print(f"  null (UA inf, aux 0): min ratio {null.min():.4f}")
+    worst_max, worst_min = 1.0, 1.0
+    for plant in GRID:
+        r = ratio_curve(plant, target, powers)
+        worst_max, worst_min = min(worst_max, r[-1]), min(worst_min, r[0])
+        tag = " central" if plant == CENTRAL else ""
+        print(f"  UAc {plant[0]:>4} UAe {plant[1]:>3} aux {plant[2]:.2f}: "
+              f"ratio {np.round(r, 3).tolist()} best at {powers[r.argmax()]:.2f} kW{tag}")
+    print(f"partload: grid {len(GRID)} plants; ratio at p_max >= {worst_max:.3f}, "
+          f"at p_min >= {worst_min:.3f}")
+    return ratio_curve(CENTRAL, target, powers)
+
+
+def burst(model: ThermalModel) -> None:
+    target = model.compute_cop(OUTDOOR_C, flow_temp=SUPPLY_C)
+    eta = calibrate(CENTRAL, target)
+    _, s_min = plant_cop(P_MIN, *CENTRAL, eta, supply_c=None)
+    _, s_max = plant_cop(P_MAX, *CENTRAL, eta, supply_c=None)
+    _, s_same = plant_cop(P_MIN, *CENTRAL, eta, supply_c=None)
+    rise = s_max - s_min
+    lift_min = model.flow_lift_factor(OUTDOOR_C, s_min)
+    lift_max = model.flow_lift_factor(OUTDOOR_C, s_max)
+    # the tree's factor is one-sided above its reference: report the Carnot
+    # ratio relative to the floor step's own supply as well
+    t_out = OUTDOOR_C + K0
+    carnot = ((s_max + K0) / (s_max + K0 - t_out)) / ((s_min + K0) / (s_min + K0 - t_out))
+    print(f"burst: return {RETURN_C} supply at p_min {s_min:.2f} at p_max {s_max:.2f} "
+          f"rise {rise:.2f} K (null rise {s_same - s_min:.2f} K); tree flow_lift_factor "
+          f"{lift_min:.4f} -> {lift_max:.4f} (ratio {lift_max / lift_min:.4f}); "
+          f"Carnot ratio across the rise {carnot:.4f}")
+
+
+def solve(sb, cell, prices, derate: float):
+    """``r10_setpoint_boost.solve``'s install with the part-load derate set
+    (absent on a tree without the term, where only ``derate == 0`` runs)."""
+    loss, buffer_l, dhw, rounded = cell
+    p = ThermalParameters()
+    if buffer_l:
+        p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
+    p.min_electrical_power, p.max_electrical_power = sb.CFG_MIN, sb.CFG_MAX
+    p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
+    if derate:
+        p.cop_partload_derate = derate
+    opt = sb.HeatPumpOptimizer(ThermalModel(p), sb.OptimizationConfig(clamp_planned_levels=rounded))
+    return opt.optimize(inputs=sb.solve_inputs(
+        initial_state=sb.ThermalState(
+            room_temperature=20.0, upper_floor_temperature=20.0,
+            lower_floor_temperature=20.0, slab_temperature=20.5,
+            outdoor_temperature=5.0, buffer_tank_temperature=24.0,
+            dhw_temperature=48.0,
+        ),
+        prices=prices, outdoor_temps=np.full(96, 5.0), start_time=sb.T0,
+    ))
+
+
+def solves(model: ThermalModel) -> int:
+    import hashlib  # noqa: PLC0415
+
+    sys.path.insert(0, "dev/audit/harnesses")
+    import r10_setpoint_boost as sb  # noqa: PLC0415
+
+    target = model.compute_cop(OUTDOOR_C)
+    eta = calibrate(CENTRAL, target)
+    best = max(plant_cop(p, *CENTRAL, eta)[0] for p in np.linspace(P_MIN, P_MAX, 50))
+    # the term's value for this plant: its COP lost at max power vs the floor
+    derate = round(1.0 - plant_cop(P_MAX, *CENTRAL, eta)[0] / plant_cop(P_MIN, *CENTRAL, eta)[0], 3)
+    has_term = hasattr(ThermalParameters(), "cop_partload_derate")
+    arms = (0.0, derate) if has_term else (0.0,)
+    print(f"solves: central plant derate {derate} term in tree {has_term}")
+
+    def r(p: float) -> float:
+        return plant_cop(p, *CENTRAL, eta)[0] / best if p > 0 else 1.0
+
+    def priced(plan: np.ndarray, prices: np.ndarray) -> tuple[float, float, float]:
+        """(plant heat short of the model's, cost per plant kWh, gain over flat)."""
+        level = np.where(plan >= P_MIN, plan, P_MIN)
+        ratio = np.array([r(x) for x in level])
+        heat_model = float((plan * target).sum())
+        heat_plant = float((plan * target * ratio).sum())
+        cost = float((plan * prices).sum() / 4.0)
+        flat_level = max(heat_plant / (target * 96), P_MIN)
+        flat_cost = float(prices.mean() * heat_plant / (target * r(flat_level)) / 4.0)
+        return 1 - heat_plant / heat_model, cost / heat_plant, (flat_cost - cost) / flat_cost
+
+    failures = 0
+    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
+        stats: dict[float, list[tuple[float, float, float]]] = {a: [] for a in arms}
+        for cell in sb.CELLS:
+            line = f"  {tag} {cell}"
+            for arm in arms:
+                try:
+                    res = solve(sb, cell, prices, arm)
+                except Exception as err:  # counted, never dropped
+                    failures += 1
+                    line += f" d={arm} failed: {err!r}"
+                    continue
+                plan = np.asarray(res.power_schedule, float)
+                sha = hashlib.sha1(np.asarray(
+                    res.power_schedule + list(res.dhw_power_schedule or []), float
+                ).tobytes()).hexdigest()[:12]
+                short, unit, gain = priced(plan, prices)
+                stats[arm].append((short, unit, gain))
+                line += (f" | d={arm} plan {sha} kWh {plan.sum() / 4:.1f} short {short:.4f}"
+                         f" cost/plant-kWh {unit:.4f} gain-vs-flat {gain:+.4f}")
+            print(line)
+        for arm in arms:
+            st = np.array(stats[arm])
+            print(f"{tag} d={arm}: cells {len(st)} heat short max {st[:, 0].max():.4f} "
+                  f"gain-vs-flat min {st[:, 2].min():+.4f} max {st[:, 2].max():+.4f} "
+                  f"cells where flat wins {int((st[:, 2] < 0).sum())}")
+        if len(arms) == 2 and stats[0.0] and stats[derate]:
+            a, b = np.array(stats[0.0]), np.array(stats[derate])
+            rel = b[:, 1] / a[:, 1] - 1
+            print(f"{tag} term vs none: cost per plant kWh change min {rel.min():+.4f} "
+                  f"max {rel.max():+.4f} cells cheaper {int((rel < -1e-9).sum())} "
+                  f"dearer {int((rel > 1e-9).sum())}")
+    return failures
+
+
+def main(argv: list[str]) -> int:
+    model = ThermalModel(ThermalParameters(
+        min_electrical_power=P_MIN, max_electrical_power=P_MAX))
+    partload(model)
+    burst(model)
+    failures = 0 if "--no-solves" in argv else solves(model)
+    print(f"failures {failures}")
+    return 1 if failures else 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main(sys.argv[1:]))
diff --git a/dev/audit/harnesses/r10_cop_partload_equiv.py b/dev/audit/harnesses/r10_cop_partload_equiv.py
new file mode 100644
index 000000000..dbd940692
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_partload_equiv.py
@@ -0,0 +1,180 @@
+#!/usr/bin/env python3
+"""R10-COP-PARTLOAD: is the `0.0 <= derate` CMP_BOUND twin an equivalent mutant?
+
+    PYTHONPATH=tests/hastub:. python3 \
+        dev/audit/harnesses/r10_cop_partload_equiv.py [--identity]
+
+Metric: the number of probe inputs on which the operator's own rewrite of
+`thermal_model._partload_derate`'s lower bound -- `0.0 <= derate` written
+`0.0 < derate` -- makes the helper, and `ThermalParameters.from_config`
+through it, answer a different value than the tree's. The grid holds both
+bounds and their just-outside floats, +0.0 and -0.0, the non-finite floats,
+numeric strings, non-float types and numpy scalars; the anchor's other twin
+(`<= MAX` written `< MAX`) rides along as the differential's positive control.
+0 differing cells over that grid is an equivalent mutant on the probed domain:
+no check can kill it, so the ledger's `survivor_triage` mark for it is
+`equivalent` and never a gap.
+Expected on this tree (chain R10-COP-PARTLOAD, the part-load derate):
+    RESULT equiv_cells=40 count
+    RESULT equiv_differs=0 count             (lower-bound twin, direct)
+    RESULT equiv_config_differs=0 count      (the same grid through from_config)
+    RESULT equiv_ties=7 count                (the cells that are 0.0 -- +0.0,
+                                              -0.0, their two strings, False, 0,
+                                              np.int64(0): every input the two
+                                              arms decide differently)
+    RESULT equiv_sign_only=2 count           (-0.0 and "-0.0": the arms answer
+                                              -0.0 and 0.0, numerically equal and
+                                              equal in every caller's product)
+    RESULT equiv_control_differs=15 count    (control: a deliberate change at
+                                              an accepted 0.0, differing on
+                                              every tied cell)
+    RESULT equiv_control_untied=8 count      (the eight refused cells -- NaN,
+                                              +-inf, "x", "", None, True and
+                                              0.5+0j -- which
+                                              const.finite_float maps to 0.0
+                                              before the range check, so they
+                                              reach the rewritten line too;
+                                              read 0 before finite_float)
+    RESULT equiv_positive_differs=4 count    (the other twin: differs on the
+                                              four cells that are 0.5 -- 0.5,
+                                              "0.5", Fraction(1, 2),
+                                              np.float64(0.5) -- and nowhere else)
+    RESULT load1=...                         (reported, not asserted)
+Baseline: the operator text is
+`if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:` in
+`thermal_model._partload_derate`; mutation is applied in memory, nothing on
+disk changes.
+Perturbation: --identity applies each mutant's *old* line as the "mutant";
+every RESULT count above must read 0, so a difference the normal run reports is
+the operator's and not the comparison's -- and the normal run's tie-only
+control, which differs on all seven tied cells, is what shows
+the comparison sees a difference there when one exists.
+"""
+from __future__ import annotations
+
+import inspect
+import math
+import os
+import sys
+from fractions import Fraction
+
+import numpy as np
+
+from custom_components.heatpump_optimizer import thermal_model as tm
+from custom_components.heatpump_optimizer.const import (
+    CONF_HEAT_PUMP_COP_PARTLOAD_DERATE as KEY,
+)
+
+IDENT = "--identity" in sys.argv
+
+LOWER_OLD = "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
+LOWER_NEW = "    if 0.0 < derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
+UPPER_OLD = LOWER_OLD
+UPPER_NEW = "    if 0.0 <= derate < MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
+ACCEPT_OLD = "        return derate"
+ACCEPT_CTRL = "        return 1.0 if derate == 0.0 else derate"
+
+GRID = [
+    0.0, -0.0, 1e-12, -1e-12, 1e-9, 0.01, 0.1, 0.25, 0.49,
+    0.4999999999, 0.5, 0.5000000001, 0.51, 0.9, 1.0, 2.0, 1e9, -1e9,
+    float("nan"), float("inf"), float("-inf"),
+    "0.0", "-0.0", "0.1", "0.5", "0.51", "-0.1", "x", "", None,
+    True, False, 0, 1, -1, Fraction(1, 2), 0.5 + 0j,
+    np.float64(0.5), np.float32(0.1), np.int64(0),
+]
+
+
+def mutate(old: str, new: str):
+    """The tree's `_partload_derate` with one of its lines rewritten.
+
+    In memory: the function's own source is re-exec'd against the module's
+    globals, so `MAX_HEAT_PUMP_COP_PARTLOAD_DERATE` and the default resolve
+    exactly as they do in the tree.
+    """
+    src = inspect.getsource(tm._partload_derate)
+    assert src.count(old) == 1, (old, src.count(old))
+    ns: dict = {}
+    exec(compile(src.replace(old, old if IDENT else new), "<mut>", "exec"),
+         dict(vars(tm)), ns)
+    return ns["_partload_derate"]
+
+
+def same(a, b) -> bool:
+    """Value equality that treats two NaNs as the same answer."""
+    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
+        return True
+    return a == b
+
+
+def call(fn, value):
+    """One probe cell, a raise included as an answer rather than a crash."""
+    try:
+        return fn(value)
+    except Exception as exc:  # noqa: BLE001 - the answer is the exception
+        return ("raised", type(exc).__name__)
+
+
+def tie(value) -> bool:
+    """True where the two lower bounds decide differently: derate == 0.0."""
+    try:
+        d = float(value)
+    except (TypeError, ValueError):
+        return False
+    return (0.0 <= d) != (0.0 < d)
+
+
+def config_cells(fn) -> list:
+    """`cop_partload_derate` through the public constructor, with `fn` in place."""
+    had = tm._partload_derate
+    tm._partload_derate = fn
+    try:
+        return [tm.ThermalParameters.from_config({KEY: v}).cop_partload_derate
+                for v in GRID]
+    finally:
+        tm._partload_derate = had
+
+
+def main() -> int:
+    head = tm._partload_derate
+    lower = mutate(LOWER_OLD, LOWER_NEW)
+    upper = mutate(UPPER_OLD, UPPER_NEW)
+    ctrl = mutate(ACCEPT_OLD, ACCEPT_CTRL)
+
+    cells = [call(head, v) for v in GRID]
+    differs = [v for v, a in zip(GRID, cells)
+               if not same(a, call(lower, v))]
+    config_differs = sum(
+        1 for a, b in zip(config_cells(head), config_cells(lower))
+        if not same(a, b))
+    ties = [v for v in GRID if tie(v)]
+    sign_only = sum(
+        1 for a, v in zip(cells, GRID)
+        if isinstance(a, float) and a == 0.0
+        and isinstance(call(lower, v), float) and call(lower, v) == 0.0
+        and math.copysign(1.0, a) != math.copysign(1.0, call(lower, v)))
+    ctrl_differs = [v for v, a in zip(GRID, cells)
+                    if not same(a, call(ctrl, v))]
+    ctrl_untied = [v for v in ctrl_differs if not tie(v)]
+    positive = [v for v, a in zip(GRID, cells)
+                if not same(a, call(upper, v))]
+
+    print(f"RESULT equiv_cells={len(GRID)} count")
+    print(f"RESULT equiv_differs={len(differs)} count")
+    print(f"RESULT equiv_config_differs={config_differs} count")
+    print(f"RESULT equiv_ties={len(ties)} count")
+    print(f"RESULT equiv_sign_only={sign_only} count")
+    print(f"RESULT equiv_control_differs={len(ctrl_differs)} count")
+    print(f"RESULT equiv_control_untied={len(ctrl_untied)} count")
+    print(f"RESULT equiv_positive_differs={len(positive)} count")
+    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
+    if differs or config_differs:
+        print(f"  lower twin differs at {differs!r}")
+        return 1
+    if not IDENT and not positive:
+        print("  the positive control saw no difference: the probe is blind")
+        return 1
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/dev/audit/rca/R10-RCA-COP-PARTLOAD.md b/dev/audit/rca/R10-RCA-COP-PARTLOAD.md
new file mode 100644
index 000000000..0fa3dd20e
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-COP-PARTLOAD.md
@@ -0,0 +1,234 @@
+# R10-RCA-COP-PARTLOAD: the COP law priced no compressor power for six releases
+
+The root-cause analysis for #2501. `dev/governance/roles/root-cause.md` wants it in
+a separate seat beside the fix. The orchestrator directed this one instead: the
+group's next step is `rca`, and the fixer seat wrote it, so the independence the
+contract asks for is weaker than usual and the reviewer should weigh that when
+reading §2.
+
+**Defect.** `ThermalModel.compute_cop` / `_cop_law` priced COP from outdoor
+temperature, humidity and flow or tank temperature only. Electrical power entered
+the model as a plain multiplier, `heat = cop * power`, at every step site, so the
+pump's efficiency was flat across its whole modulation band although the compressor
+is the machine whose power sets the lift across the heat exchangers. The law
+shipped in the initial release `ec45dc4d5` (2026-04-03, v1.0.0) and through v7.0.4.
+
+**Measured size.** On a 27-plant synthetic grid
+(`dev/audit/harnesses/r10_cop_partload.py`), COP at max power is 0.808 of the
+no-term law's at worst — 19.2 % lower — and 0.985 at the floor; the central plant
+loses 11.2 %. On the 16 synthetic installs of R10-SETPOINT-BOOST, a planner that
+prices the fall plans 0.94 % to 5.98 % cheaper per delivered kWh on price-spread
+days, 16 of 16, and its plan delivers up to 8.2 % more of the heat it promises
+instead of 10.9 %.
+
+## 1. Cause
+
+The law was written from the refrigerant cycle — a Carnot fraction across the lift
+— and the house's flow curve. Both are temperature quantities, and every
+monotonicity check in the tree is a temperature sweep. Power is a *control*
+quantity: the solver chooses it. Nothing in the law noticed that delivered heat at a
+chosen power is not the same product at every power, and one accident hid it:
+`min_electrical_power` and `max_electrical_power` were already parameters, used by
+the floor guards and the capacity envelope, never by the COP law itself.
+
+The tree has added one COP determinant it lacked before — `flow_lift_factor`,
+#1067, `3b9e7b668`, 2026-09-17 — which shows the shape is not foreign here: a
+missing term arrives as a fix, found by the feature that needed it, not by the audit
+step that was supposed to look for it.
+
+**Class search.** The mechanism is *a priced conversion that every sibling formula
+makes without one of its inputs*. The siblings agree, so it is not P2 ("one fact
+decided twice by divergent predicates"); there is no floor or divisor, so it is not
+P3. No entry in `dev/audit/config/bugclasses.json` covers it. It is recorded here as
+a first instance, not as a class; if it arrives twice more the register owns it.
+
+The forward-conversion census (`$EXPORT/probe/cop_seams.py`, sha1 `c628396caf3c`)
+found 60 sites in the package where a COP meets a power or a heat. Seven are the
+priced forward conversions and route through one helper; the other 53 are
+dispositioned in §5.
+
+## 2. Process state: (c), followed and did not produce the intended result
+
+D2's item 2 reads: "COP monotone in outdoor and flow temperature, Carnot fraction
+within the stated band, every derate in [0, 1], defrost derate bounded and continuous
+at the band edges, capacity envelope never below demand-at-derate without a reason
+code." Every round from 3 to 10 has a D2 scope report, and round 10's scope 2 is the
+COP step.
+
+That step ran, and its report is honest: `dev/audit/rounds/round10/D2/s2/REPORT.md`
+sweeps `compute_cop`, `_cop_law`, `flow_lift_factor`, `compute_cop_dhw`, `_batch_cop`
+and the defrost derate over outdoor −35–40 °C, flow and tank 10–80 °C, three plant
+modes and 40 learned derates, and its findings and non-findings are all monotonicity
+in temperature and bounds on the derate *values*. Nothing in it varies compressor
+power, because the item's text lists the quantities to sweep and power is not among
+them. The item's second half — "capacity envelope never below demand-at-derate" — is
+filed under **Unfinished** in that same report, and that is the half that needs
+delivered heat at a power.
+
+Eight rounds of the step therefore passed while the law had no power term. The defect
+was found instead by D0's demand analysis, in another dimension, from a hypothesis
+about price swings.
+
+Not (a): the step exists. Not (b): it ran, and its harness is in the tree. Not (d):
+no precondition moved — both power parameters were in the dataclass at v1.0.0, and
+the item never named power. The state is (c): the step's unit, a sweep over the
+quantities the item names, cannot detect a quantity the item omits.
+
+## 3. Cost test
+
+`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per
+release cycle.
+
+- **cost(defect).** The lower bound is the round-9 per-finding fix cost, 4.35 h
+  (#1718: 21.75 h over 5 findings), which excludes the finder, verify and judge
+  seats: 15 660 s. The field cost is the mispriced plan above; it is money, not
+  wall-clock, and is not counted here.
+- **P(recurrence).** Two arrivals of "a COP determinant absent from the law" in the
+  law's life — power (this one) and the flow-curve lift (#1067) — over 152 release
+  intervals: 152 tags from `v2.3.0-beta.1` to `v7.0.4`, 151 intervals, plus the
+  untagged `v1.0.0` interval. P = 2/152 = 0.013. On the single arrival the
+  conservative figure is 0.0066.
+- **Expected defect cost.** 15 660 x 0.013 = 206 s per release (103 s on one
+  arrival).
+- **The countermeasure.** One sentence in D2's item 2: derive the priced formula's
+  inputs from the device's own control surface — outdoor temperature, humidity,
+  flow or tank temperature, electrical power — and mark each a modelled term, a
+  documented constant, or out of scope. One sentence in the brief and about a minute
+  in each D2 scope that prices a formula; one such scope per round, so 60 s per
+  release.
+- **Verdict.** 60 s < 206 s, about 3.4x. Thin, and it rests on two arrivals, so it is
+  recorded as a request to the owner, not as a settled change.
+
+Two other countermeasures were priced and refused:
+
+- **A census check in `tests/features.py`** that every COP-by-power product routes
+  through `delivered_heat_kw` or a declared exception. Standing cost under a second,
+  but the exception list is 53 entries a reviewer must re-justify on every move, and
+  it pins a list rather than the property. Refused: it buys a list that drifts.
+- **A metered slope detector**, comparing the model's COP fall with
+  `flow_meter.cop_evidence`'s observed COP against measured power. It needs a heat
+  meter, which is exactly why the term defaults to 0. Refused on that ground.
+
+## 4. Countermeasures
+
+**Built, in this pull request.**
+
+1. The term, off by default, at the seven priced forward sites:
+   `_simulate_step_single`, `_simulate_step_two_zone`, both branches of
+   `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`, `extend_dhw_temps`,
+   and the optimizer's `_buffer_charge_ceiling`. The two public step entry points
+   and `simulate_dhw_only` inherit through these.
+2. Its null controls: a zero derate is exactly `cop * power`, asserted bit-for-bit;
+   and the branch's plans at zero derate are byte-identical to the merge base's —
+   32 of 32 plan hashes, spread and flat, 16 synthetic installs each.
+3. Pins that a future removal fails: six checks in `tests/features.py` (factor,
+   heat, step, config, ceiling, flat-price peak share), two more for the hot-water
+   sites, and two gradient-parity cells; mutation-proven in §6.
+
+**Proposed to the owner (policy, not edited by this seat).** The D2 item 2 sentence
+in §3. It addresses state (c): the step's unit is a sweep, so the fix is a
+derivation step before the sweep, not a firmer instruction. `dev/governance/` is
+policy; the owner approves it before merge.
+
+**Recorded refusal.** A class-wide census — "list every priced formula's actuators"
+— refused on the numbers in §3. Whether the shape becomes a
+`dev/audit/config/bugclasses.json` entry is the owner's call, not this seat's.
+
+## 5. Seams not routed through the helper, and why
+
+Of the 60 sites: 7 are the priced forward conversions (§4.1); 2 are the helper's
+own lines; 29 are calls to the COP law itself, which get the term through the law
+and need no site change — one of those, `sysid._valve_drive`, is also an inverse
+conversion; and 22 are other conversions:
+
+- **Inverse (power from heat), 4 sites** — `dhw_planner._plan_dhw_min_cost` and
+  `_clamp_dhw_to_capacity`, `optimizer._compute_baseline_power`,
+  `coordinator._dhw_setpoint_sweep`. With a derate the forward relation is quadratic
+  in power, so the closed form `heat / cop` understates the electrical power needed
+  by up to the derate. Making them exact is a separate change — the positive root of
+  `c2 P^2 - c1 P + Q/cop = 0` on the band — and is carried forward rather than done
+  here; at the default 0 they are exact.
+- **Nameplate and design sizing, 6 sites** — `design_power = p_max *
+  cop_nominal_floored` in `thermal_model.flow_target_for_indoor`,
+  `_simulate_step_two_zone`, `_substeps_and_loss`, `simulate_trajectory_batch`,
+  `optimizer._compute_baseline_power` and `sysid._held_state`. A plant constant that
+  calibrates emitter UA, not a delivered-heat claim at a chosen power; folding a band
+  share into it would double-count the derate against the UA it calibrates.
+- **Measurements, 3 sites** — `flow_meter.cop_evidence` (two lines) and
+  `coordinator._fold_capacity_envelope`. These read measured power; the derate is a
+  model assumption.
+- **Bounds and detectors, 2 sites** — `coordinator._max_pump_rise` uses
+  `max(cop, 1.0) * p_max` deliberately as a loose upper bound for recognising an
+  external heat source, and `sysid._size_step_power` bounds a step. Both are looser
+  than the model on purpose; tightening a detector with an assumed plant term would
+  raise its false-positive rate, not its accuracy.
+- **Learning samples, 2 sites** — `sysid.SystemIdentification.step`. The fit reads
+  the plan's power and the model's COP to infer UA; folding an assumed derate into
+  the claimed heat would make the learned UA absorb the assumption.
+- **Other converters or non-conversions, 5 sites** — `battery`, `pv`,
+  `wood_fuel`, `topology`'s error estimate, and `dhw_planner`'s retained-fraction
+  division. Not the heat pump's COP.
+
+## 6. Mutation proof
+
+Run at `24bd25b9` against the real `tests/features.py` — 4 475 checks — by
+`$EXPORT/probe/pl_mutants.py` (sha1 `979ad48a4a60`), which restores every file
+with `git checkout --` afterwards.
+
+**R1, the factor itself removed.** `partload_factor` returns 1.0, so every site
+prices the flat law the defect shipped. Seven of 4 475 checks fail, and they are
+exactly the seven that need the term: the factor, the pump heat, the scalar
+step, the buffer ceiling, the flat-price plan, and the two hot-water checks. The
+configured-derate check passes, as it must — it drives `from_config`, not the
+factor — so the run fails its own checks and nothing else:
+
+```
+=== R1: 7 failing checks
+  FAIL the part-load factor is 1 at and below the modulation floor, ...
+  FAIL pump heat at max power carries the derate and at the floor does not; ...
+  FAIL a step at max power warms the slab less with the derate on, ...
+  FAIL the buffer's charge ceiling prices the pump's max-power output ...
+  FAIL at a flat price the derate moves the plan off max power ...
+  FAIL a hot-water schedule carries the derate too ...
+  FAIL the full trajectory's hot-water track prices the same conversion ...
+=== R1 summary: 7 of 4475 FEATURE CHECKS FAILED
+```
+
+R1 is the fix's line deleted. It cannot say *where* the term is missing, because
+it removes the term everywhere at once.
+
+**R2, five site-level mutants in one run**, each owning a different check, so a
+failing name is attributable to one mutant: the optimizer's ceiling computes
+`max_power * cop` again; the two-zone scalar step is left plain (the second of
+the two identical step blocks, so the single-zone twin stays wired); both
+hot-water conversions are left plain; and `_partload_derate`'s range predicate is
+forced true. Six checks fail, one group per mutant — the two-zone twin through
+the batch and its gradient, the predicate, the ceiling, and the two hot-water
+conversions — so no site is pinned by a neighbour's check:
+
+```
+=== R2: 6 failing checks
+  FAIL batched simulation is bitwise-identical: two-zone part-load derate
+  FAIL batched jac == scipy 2-point FD bit-for-bit on free variables: ...
+  FAIL a configured derate inside [0, 0.5] is taken; ...
+  FAIL the buffer's charge ceiling prices the pump's max-power output ...
+  FAIL a hot-water schedule carries the derate too ...
+  FAIL the full trajectory's hot-water track prices the same conversion ...
+=== R2 summary: 6 of 4475 FEATURE CHECKS FAILED
+```
+
+R1 says the fix's line is load-bearing; R2 says each site is load-bearing on its
+own. Neither run is a search for the defect's instance: §1's census is the seam
+rule, and §5 dispositions every seam it returns.
+
+
+## Reproduce
+
+- Harness: `PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py`
+- Base arm: the same harness with `PYTHONPATH` on a worktree at `4f3c73020`, where
+  it prints `term in tree False`, the same 32 plan hashes and the same three score
+  summaries for the d=0 arm.
+- Census: `$EXPORT/probe/cop_seams.py custom_components/heatpump_optimizer`.
+- Standing cost of the feature block: `$EXPORT/probe/pl_block_cost.py`
+  (sha1 `fc6e9af30290`), 1.94 s CPU per run, median of three.
+- Mutants: §6.
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 1cf5f3762..adc0b50cd 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -87,14 +87,16 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     docs/configuration.md in the same commit. #2261 moved them once more,
     201 -> 202 and 234 -> 235: the heat energy meter on the
     entities_metering page, with its row in docs/configuration.md in the
-    same commit. This block is an
+    same commit. R10-COP-PARTLOAD moved them once more, 202 -> 203 and
+    235 -> 236: the part-load derate number on the thermal model page, with
+    its row in docs/configuration.md in the same commit. This block is an
     ASSERTION `tests/harness_headers.py` executes the script against, and it
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=202 count
+    RESULT option_fields_rendered=203 count
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=235 count
+    RESULT option_schema_keys_rendered=236 count
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 2e4c17d16..0193e3035 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -272,9 +272,9 @@
  {
   "id": "C31",
   "source": "docs/configuration.md",
-  "claim": "every documented Range (91 rows) is the NumberSelector min/max the rendered options page actually carries",
+  "claim": "every documented Range (92 rows) is the NumberSelector min/max the rendered options page actually carries",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "91 compared, mismatches=[]",
+  "result": "92 compared, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index f709ef187..c9db0c258 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -34,7 +34,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C28 | `docs/configuration.md` | eight on the first menu and fifteen more behind Advanced settings | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(8, 15) measured=(8, 15) | **true** |  |
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 23 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (89 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 89 compared, mismatches=[] | **true** |  |
-| C31 | `docs/configuration.md` | every documented Range (91 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 91 compared, mismatches=[] | **true** |  |
+| C31 | `docs/configuration.md` | every documented Range (92 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 compared, mismatches=[] | **true** |  |
 | C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=83 measured=83 | **true** |  |
 | C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=83, listed=83, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=28 measured=28 | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index f86346bff..2eae2818e 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -71,14 +71,17 @@ against a document that is CORRECT.
                                          #1495's mold-floor breach warning
                                          margin, a NumberSelector Default row
                                          on the Comfort and temperatures table)
-    RESULT config_ranges_compared=91     (76 until #937's rows landed; 86
+    RESULT config_ranges_compared=92     (76 until #937's rows landed; 86
                                          until #1067's silent-mode half
                                          documented the derate's range; 87
                                          until its frequency half documented
                                          the two compressor Hz bounds; 90 with
                                          #1495's same mold-floor breach warning
                                          margin, whose 0-5 °C Range row is the
-                                         only one this re-record adds)
+                                         only one this re-record adds; 92 with
+                                         R10-COP-PARTLOAD's part-load derate
+                                         Range row on the expert thermal-model
+                                         table)
     RESULT arch_modules_on_disk=83       (82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
diff --git a/dev/programme/delivery/2872.md b/dev/programme/delivery/2872.md
new file mode 100644
index 000000000..c2a531a33
--- /dev/null
+++ b/dev/programme/delivery/2872.md
@@ -0,0 +1 @@
+- [#2872](https://github.com/tvofi/heatpump_optimizer/pull/2872) — **open**, roster: R10-COP-PARTLOAD.
diff --git a/docs/configuration.md b/docs/configuration.md
index 77031b559..bba7b039c 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -173,6 +173,7 @@ declaration. It asks the model's own numbers:
 | Heat pump nominal COP | 3.5 | 1.5–6.0 | As above. |
 | Heat pump max power | 5.0 kW | 1–20 | As above. |
 | Heat pump min power | 1.0 kW | 0–10 | As above. |
+| Heat pump COP loss at max power | 0 | 0–0.5, 0.01 steps | The share of efficiency lost running at max power rather than at min power, as a fraction (0.1 = 10 %). Larger heat flows need larger temperature differences across the heat exchangers, so the compressor's COP falls with its power; the model prices that as a linear fall across the modulation band, on the space-heating and the hot-water schedules alike. 0 leaves power out of the COP entirely, which is the default because no install without a heat meter can measure the slope; typical air-to-water units lose 0.05 to 0.15. The value must stay below band / (band + max power), band being max minus min power (0.44 for a 1–5 kW pump, 0.17 for a 4–5 kW one): at or above it more power would deliver less heat at the top of the band, so the options page refuses it and a stored one is read as 0. |
 | Recalculate every | 30 min | 10–120, 5 steps | How often the plan is re-solved against fresh prices and weather. |
 | How hard to chase low prices | 1.0 | 0.1–10, 0.1 steps | Higher moves more heating into cheap hours, at the cost of more temperature swing. |
 | How strictly to hold the temperature | 5.0 | 0.1–20, 0.1 steps | The counterweight. Around 5 lets the house drift freely inside your allowed range; 10 keeps it noticeably closer to target; 20 or more behaves like an ordinary thermostat. |
diff --git a/tests/closures.json b/tests/closures.json
index 6b8a5b958..15d53b644 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3697,6 +3697,8 @@
    "dev/audit/harnesses/r10_cloud_setup_toolchain.py",
    "dev/audit/harnesses/r10_codescan_wait_race.py",
    "dev/audit/harnesses/r10_configflow_pages.py",
+   "dev/audit/harnesses/r10_cop_partload.py",
+   "dev/audit/harnesses/r10_cop_partload_equiv.py",
    "dev/audit/harnesses/r10_critpath_archive_parity.py",
    "dev/audit/harnesses/r10_dead_rate_limit.py",
    "dev/audit/harnesses/r10_demand_overbook.py",
diff --git a/tests/features.py b/tests/features.py
index 377f3e1ae..720bf8a7f 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -6696,6 +6696,12 @@ _grad_parity(False, label="single-zone DHW-pinned bounds shoulder",
 _grad_parity(True, valve="manual", label="two-zone capped bounds summer-cool",
              weather_p="summer_cool", bounds_over="capped",
              state_over={"room_temperature": 21.5})
+# R10-COP-PARTLOAD: the part-load derate is elementwise on the batch's power
+# rows; the twins must stay bitwise with it on, in both zonings.
+_grad_parity(False, label="single-zone part-load derate",
+             param_over={"cop_partload_derate": 0.15})
+_grad_parity(True, valve="manual", label="two-zone part-load derate",
+             param_over={"cop_partload_derate": 0.15})
 # Mutation anchor: the batch twin once applied the Carnot lift below the
 # reference flow temperature (a boost the scalar never grants) and once
 # let np.where's both-arms division poison states with 0/0 NaN -- each
@@ -9440,23 +9446,27 @@ def reachable(name: str) -> str | None:
     Booleans are probed by flipping them away from their default rather than
     by a sentinel value: the mapping coerces with ``bool()``, so any sentinel
     would come back as True and look like a match for every boolean field.
+    A field whose legal range stops at or below 0.5 on the default config
+    (the part-load derate's band limit is 4/9 on 1-5 kW) refuses that
+    sentinel, so 0.25 is tried after it.
     """
     default_value = getattr(ThermalParameters.from_config({}), name)
     if isinstance(default_value, bool):
-        sentinel = not default_value
+        sentinels = [not default_value]
     else:
-        sentinel = 0.5 if default_value != 0.5 else 0.25
+        sentinels = [v for v in (0.5, 0.25) if v != default_value]
     for candidate in dir(hp_const):
         if not candidate.startswith("CONF_"):
             continue
-        try:
-            built = ThermalParameters.from_config(
-                {getattr(hp_const, candidate): sentinel}
-            )
-        except Exception:
-            continue
-        if getattr(built, name, None) == sentinel:
-            return candidate
+        for sentinel in sentinels:
+            try:
+                built = ThermalParameters.from_config(
+                    {getattr(hp_const, candidate): sentinel}
+                )
+            except Exception:
+                continue
+            if getattr(built, name, None) == sentinel:
+                return candidate
     return None
 
 
@@ -71953,6 +71963,250 @@ R.check(
 )
 
 
+# --- R10-COP-PARTLOAD: COP falls with compressor power ------------------------
+# Synthetic throughout. ``cop_partload_derate`` is the share of COP lost at max
+# power against min power (dev/audit/harnesses/r10_cop_partload.py measures it
+# on an independent cycle model). 0 is the default and must price exactly
+# ``cop * power``, so every plan is byte-identical to one with no term.
+from heatpump_optimizer.const import (  # noqa: E402
+    CONF_HEAT_PUMP_COP_PARTLOAD_DERATE as _PL_KEY,
+)
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    partload_factor as _pl_factor,
+    delivered_heat_kw as _pl_heat_of,
+)
+
+
+def _pl_model(derate, p_min=1.5, p_max=5.0):
+    return ThermalModel(ThermalParameters(
+        min_electrical_power=p_min, max_electrical_power=p_max,
+        cop_partload_derate=derate))
+
+
+_pl = _pl_model(0.12)
+_pl_f = [float(_pl_factor(_pl.params, x)) for x in (0.0, 1.0, 1.5, 3.25, 5.0, 6.0)]
+R.check(
+    "the part-load factor is 1 at and below the modulation floor, 1 - derate at "
+    "max power and linear between; a fixed-speed band prices no slope",
+    _pl_f == [1.0, 1.0, 1.0, 1.0 - 0.12 * 0.5, 1.0 - 0.12, 1.0 - 0.12]
+    and _pl_factor(_pl_model(0.12, 3.0, 3.0).params, 3.0) == 1.0,
+    f"{_pl_f}",
+)
+_pl_cop = _pl.compute_cop(5.0)
+_pl_heat = [float(_pl_heat_of(_pl.params, _pl_cop, x)) for x in (1.5, 5.0)]
+_pl_heat0 = [_pl_heat_of(_pl_model(0.0).params, _pl_cop, x) for x in (1.5, 5.0)]
+R.check(
+    "pump heat at max power carries the derate and at the floor does not; "
+    "null control: a zero derate is exactly cop * power",
+    abs(_pl_heat[1] - _pl_cop * 5.0 * 0.88) < 1e-12 and _pl_heat[0] == _pl_cop * 1.5
+    and _pl_heat0 == [_pl_cop * 1.5, _pl_cop * 5.0],
+    f"derated {_pl_heat} plain {_pl_heat0}",
+)
+_pl_state = ThermalState(room_temperature=20.0, slab_temperature=21.0,
+                         outdoor_temperature=0.0)
+_pl_step = {d: _pl_model(d).simulate_step(_pl_state, 5.0, 0.0, dt_hours=0.25).slab_temperature
+            for d in (0.0, 0.2)}
+_pl_floor = {d: _pl_model(d).simulate_step(_pl_state, 1.5, 0.0, dt_hours=0.25).slab_temperature
+             for d in (0.0, 0.2)}
+R.check(
+    "a step at max power warms the slab less with the derate on, and stays a "
+    "float; "
+    "null control: a step at the floor is unchanged",
+    _pl_step[0.2] < _pl_step[0.0] and type(_pl_step[0.2]) is float
+    and _pl_floor[0.2] == _pl_floor[0.0],
+    f"max {_pl_step} floor {_pl_floor}",
+)
+_pl_cfg = {
+    v: ThermalParameters.from_config({_PL_KEY: v}).cop_partload_derate
+    for v in (0.0, 0.1, 0.5, -0.1, 0.9, "x", None, float("nan"))
+}
+from heatpump_optimizer.thermal_model import _partload_derate as _pl_read  # noqa: E402
+R.check(
+    "a configured derate inside [0, 0.5] is taken; a negative, oversized, "
+    "non-numeric or NaN one refuses to the 0 default; the reader alone keeps "
+    "0.5 and refuses the float above it, and on the default 1-5 kW band 0.5 is "
+    "past band / (band + p_max) = 4/9 and refuses too",
+    _pl_cfg[0.0] == 0.0 and _pl_cfg[0.1] == 0.1 and _pl_cfg[0.5] == 0.0
+    and _pl_read(0.5) == 0.5 and _pl_read(float(np.nextafter(0.5, 1.0))) == 0.0
+    and all(_pl_cfg[v] == 0.0 for v in (-0.1, 0.9, "x", None))
+    and _pl_cfg[next(k for k in _pl_cfg if isinstance(k, float) and k != k)] == 0.0
+    and ThermalParameters.from_config({}).cop_partload_derate == 0.0,
+    f"{_pl_cfg}",
+)
+
+
+def _pl_ceiling(derate):
+    p = ThermalParameters(min_electrical_power=1.5, max_electrical_power=5.0,
+                          cop_partload_derate=derate)
+    p.mixing_valve_mode, p.buffer_tank_volume = "manual", 750.0
+    p.cop_flow_carnot = True
+    return _PvOpt(ThermalModel(p), _PvOptCfg())._buffer_charge_ceiling(-15.0)
+
+
+_pl_ceil = {d: _pl_ceiling(d) for d in (0.0, 0.3)}
+R.check(
+    "the buffer's charge ceiling prices the pump's max-power output with the "
+    "derate: a derated pump stops charging at a cooler tank in deep cold",
+    _pl_ceil[0.3] < _pl_ceil[0.0],
+    f"{_pl_ceil}",
+)
+
+_PL_FLAT = np.full(96, 1.6)
+_PL_T0 = datetime(2026, 1, 12, 20, 0, tzinfo=UTC)
+
+
+def _pl_solve(derate, prices):
+    p = ThermalParameters(min_electrical_power=1.5, max_electrical_power=5.0,
+                          cop_partload_derate=derate, dhw_enabled=False,
+                          house_heat_loss_scale=1.7)
+    return _PvOpt(ThermalModel(p), _PvOptCfg()).optimize(
+        inputs=solve_inputs(
+            initial_state=ThermalState(
+                room_temperature=20.0, upper_floor_temperature=20.0,
+                lower_floor_temperature=20.0, slab_temperature=20.5,
+                outdoor_temperature=5.0, buffer_tank_temperature=24.0,
+                dhw_temperature=48.0),
+            prices=prices, outdoor_temps=np.full(96, 5.0), start_time=_PL_T0,
+        ))
+
+
+def _pl_peak_share(result):
+    plan = np.asarray(result.power_schedule, float)
+    return float(plan[plan >= 4.0].sum() / plan.sum())
+
+
+_pl_flat0, _pl_flat1 = _pl_solve(0.0, _PL_FLAT), _pl_solve(0.15, _PL_FLAT)
+R.check(
+    "at a flat price the derate moves the plan off max power: the share of kWh "
+    "planned at 4 kW or more falls",
+    _pl_peak_share(_pl_flat1) < _pl_peak_share(_pl_flat0),
+    f"d=0 {_pl_peak_share(_pl_flat0):.3f} d=0.15 {_pl_peak_share(_pl_flat1):.3f}",
+)
+
+
+def _pl_dhw_step(derate, kw):
+    """Hot-water tank temperature after one 15-minute step at ``kw``."""
+    temps = np.array([45.0, 0.0])
+    _pl_model(derate).extend_dhw_temps(
+        temps, 0, np.array([kw]), np.array([5.0]), np.zeros(1), dt_hours=0.25)
+    return float(temps[1])
+
+
+_pl_dhw_hi = {d: _pl_dhw_step(d, 5.0) for d in (0.0, 0.2)}
+_pl_dhw_lo = {d: _pl_dhw_step(d, 1.5) for d in (0.0, 0.2)}
+R.check(
+    "a hot-water schedule carries the derate too: the same electrical power "
+    "warms the tank less with the term on; "
+    "null control: at the modulation floor the tank is unchanged",
+    _pl_dhw_hi[0.2] < _pl_dhw_hi[0.0] and _pl_dhw_lo[0.2] == _pl_dhw_lo[0.0],
+    f"max {_pl_dhw_hi} floor {_pl_dhw_lo}",
+)
+
+
+def _pl_dhw_traj(derate, kw=5.0):
+    """DHW temperature after one step of the full space + hot-water path."""
+    out = _pl_model(derate).simulate_trajectory_with_dhw(
+        ThermalState(room_temperature=20.0, upper_floor_temperature=20.0,
+                     lower_floor_temperature=20.0, slab_temperature=20.5,
+                     outdoor_temperature=5.0, buffer_tank_temperature=24.0,
+                     dhw_temperature=45.0),
+        np.zeros(1), np.full(1, kw), _WS(np.full(1, 5.0)),
+        start_hour=20.0, dt_hours=0.25)
+    return float(out[4][-1])
+
+
+_pl_traj = {d: _pl_dhw_traj(d) for d in (0.0, 0.2)}
+_pl_traj_lo = {d: _pl_dhw_traj(d, 1.5) for d in (0.0, 0.2)}
+R.check(
+    "the full trajectory's hot-water track prices the same conversion as the "
+    "step twin: the derated tank ends cooler; "
+    "null control: at the modulation floor the track is unchanged",
+    _pl_traj[0.2] < _pl_traj[0.0] and _pl_traj_lo[0.2] == _pl_traj_lo[0.0],
+    f"max {_pl_traj} floor {_pl_traj_lo}",
+)
+
+
+# R10-COP-PARTLOAD round 2: heat = cop * P * (1 - d * (P - p_min) / band) has
+# slope cop * (1 - d * (band + p_max) / band) at p_max, so a derate at or above
+# band / (band + p_max) buys less heat with more power at the top of the band.
+# Every construction path refuses it (``ThermalParameters.clamp``), and the
+# options page names it. Narrow band 4-5 kW: the limit is 1/6.
+from heatpump_optimizer import config_flow as _pl_flow  # noqa: E402
+_pl_lim = 1.0 / 6.0
+_pl_grid = np.linspace(4.0, 5.0, 2001)
+
+
+def _pl_kept(derate, p_min=4.0, p_max=5.0):
+    """The derate a direct construction and from_config each keep."""
+    direct = ThermalParameters(min_electrical_power=p_min, max_electrical_power=p_max,
+                               cop_partload_derate=derate).cop_partload_derate
+    cfg = ThermalParameters.from_config({
+        "heat_pump_min_power": p_min, "heat_pump_max_power": p_max, _PL_KEY: derate,
+    }).cop_partload_derate
+    return direct, cfg
+
+
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    partload_derate_limit as _pl_limit,
+)
+_pl_below = float(np.nextafter(_pl_lim, 0.0))
+_pl_heat_below = _pl_heat_of(_pl_model(_pl_below, 4.0, 5.0).params, 3.0, _pl_grid)
+R.check(
+    "a part-load derate at or above band / (band + p_max) is refused on every "
+    "construction path, so delivered heat never falls with power: on a 4-5 kW "
+    "band 0.19 and the limit itself read 0, the float just below it is kept and "
+    "heat rises across the band there; "
+    "null controls: 0 stays 0 and is exactly cop * power, the default 1-5 kW "
+    "band keeps 0.19, and a fixed-speed band (or one with no positive span to "
+    "divide by) has no limit, its factor being 1",
+    _pl_kept(0.19) == (0.0, 0.0) and _pl_kept(_pl_lim) == (0.0, 0.0)
+    and _pl_kept(_pl_below) == (_pl_below, _pl_below)
+    and bool(np.all(np.diff(_pl_heat_below) > 0.0))
+    and _pl_kept(0.0) == (0.0, 0.0)
+    and np.array_equal(_pl_heat_of(_pl_model(0.0, 4.0, 5.0).params, 3.0, _pl_grid),
+                       3.0 * _pl_grid)
+    and _pl_kept(0.19, 1.0, 5.0) == (0.19, 0.19)
+    and _pl_kept(0.2, 3.0, 3.0) == (0.2, 0.2)
+    and _pl_limit(-2.0, -1.0) == float("inf"),
+    f"4-5: 0.19 {_pl_kept(0.19)} limit {_pl_kept(_pl_lim)} below {_pl_kept(_pl_below)}; "
+    f"1-5: 0.19 {_pl_kept(0.19, 1.0, 5.0)}",
+)
+_pl_err = getattr(_pl_flow, "_partload_errors", lambda c, cur: {})
+_pl_narrow = {"heat_pump_min_power": 4.0, "heat_pump_max_power": 5.0}
+R.check(
+    "the thermal-model options page refuses a derate at or above the band's "
+    "limit on the derate field, judged against the stored band when the page "
+    "posts only the derate; "
+    "null controls: 0 and the default band's 0.19 pass",
+    _pl_err({_PL_KEY: 0.19}, _pl_narrow) == {_PL_KEY: "partload_derate_above_limit"}
+    and _pl_err({**_pl_narrow, _PL_KEY: 0.19}, {}) == {_PL_KEY: "partload_derate_above_limit"}
+    and _pl_err({_PL_KEY: _pl_lim}, _pl_narrow) == {_PL_KEY: "partload_derate_above_limit"}
+    and _pl_err({_PL_KEY: _pl_below}, _pl_narrow) == {}
+    and _pl_err({_PL_KEY: 0.0}, _pl_narrow) == {}
+    and _pl_err({_PL_KEY: 0.19}, {}) == {},
+    f"{_pl_err({_PL_KEY: 0.19}, _pl_narrow)}",
+)
+# Round 3: the Modbus pre-fill save is the band's other options writer, and
+# its form has no derate field, so the refusal lands on ``base``. A stored
+# 0.40 is legal on 1-5 kW (limit 4/9) and past it once max power drops to 2.
+_pl_pre = _pl_flow._prefill_errors
+_pl_stored = {"heat_pump_min_power": 1.0, "heat_pump_max_power": 5.0, _PL_KEY: 0.40}
+R.check(
+    "a pre-fill save that narrows the power band refuses a stored part-load "
+    "derate the new band puts past its limit, on base, whichever band key the "
+    "save carries; "
+    "null controls: a derate under the narrowed limit passes, a save touching "
+    "neither band key is not judged on the stored pair, and min above max is "
+    "still named as such",
+    _pl_pre({"heat_pump_max_power": 2.0}, _pl_stored) == {"base": "partload_derate_above_limit"}
+    and _pl_pre({"heat_pump_min_power": 4.0}, _pl_stored) == {"base": "partload_derate_above_limit"}
+    and _pl_pre({"heat_pump_max_power": 2.0}, {**_pl_stored, _PL_KEY: 0.30}) == {}
+    and _pl_pre({"heat_pump_cop_nominal": 3.0}, {**_pl_stored, **_pl_narrow}) == {}
+    and _pl_pre({"heat_pump_max_power": 0.5}, _pl_stored) == {"base": "min_power_above_max"},
+    f"max 5->2: {_pl_pre({'heat_pump_max_power': 2.0}, _pl_stored)}",
+)
+
+
 # --- #2261: a delivered-heat counter, the mode dwell and one attribution --------
 # R10-HEAT-METER. A ``total_increasing`` kWh counter of the heat the pump
 # delivered is read per span (``heat_energy.HeatEnergyMeter``), the span closing
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index ccd1d1a06..eb258ceef 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -791,3 +791,5 @@ valve_storage  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost D
 valve_storage_flat_prices  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 113.116 -> 102.374 here; plan leaves move with the reference-anchored starts
 valve_storage_low_target  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 195.205 -> 111.103 here; plan leaves move with the reference-anchored starts
 valve_storage_small_tank  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 151.266 -> 128.078 here, predicted_savings and deferred_energy_cost with it
+
+config_flow # R10-COP-PARTLOAD: the heat_pump_cop_partload_derate option joins the options table and its seeded copy; keys added, no value moved
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index ac64042c3..49f528857 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -3444,6 +3444,17 @@
     "required": "Optional",
     "selector": "NumberSelector"
    },
+   "heat_pump_cop_partload_derate": {
+    "config": {
+     "max": "0.5",
+     "min": "0",
+     "mode": "'box'",
+     "step": "'any'"
+    },
+    "default": null,
+    "required": "Optional",
+    "selector": "NumberSelector"
+   },
    "heat_pump_max_power": {
     "config": {
      "max": "20",
@@ -5940,6 +5951,17 @@
    "required": "Optional",
    "selector": "NumberSelector"
   },
+  "heat_pump_cop_partload_derate": {
+   "config": {
+    "max": "0.5",
+    "min": "0",
+    "mode": "'box'",
+    "step": "'any'"
+   },
+   "default": null,
+   "required": "Optional",
+   "selector": "NumberSelector"
+  },
   "heat_pump_max_power": {
    "config": {
     "max": "20",
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json
new file mode 100644
index 000000000..bcf2986aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.CMP_BOUND.d899f1dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors CMP_BOUND d899f1dc",
+  "killed_by": "tests/features.py",
+  "old": "    if derate >= limit:  # the limit is positive, so 0 always passes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if derate > limit:  # the limit is positive, so 0 always passes`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json
new file mode 100644
index 000000000..fde216919
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.GUARD_OFF.d899f1dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors GUARD_OFF d899f1dc",
+  "killed_by": "tests/features.py",
+  "old": "    if derate >= limit:  # the limit is positive, so 0 always passes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # the limit is positive, so 0 always passes`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json
new file mode 100644
index 000000000..59e1d8b6a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_partload_errors.RETURN_DEL.5e4fa825.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_partload_errors RETURN_DEL 5e4fa825",
+  "killed_by": "tests/features.py",
+  "old": "    return {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json
new file mode 100644
index 000000000..157f3211a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.9fbfea67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_prefill_errors GUARD_OFF 9fbfea67",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if {CONF_HEAT_PUMP_MIN_POWER, CONF_HEAT_PUMP_MAX_POWER} & saved.keys():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json
new file mode 100644
index 000000000..4c267f126
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.0531d42a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net RETURN_DEL 0531d42a",
+  "killed_by": "tests/features.py",
+  "old": "            return heat - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json
deleted file mode 100644
index 7f21935fc..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.RETURN_DEL.110923c2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net RETURN_DEL 110923c2",
-  "killed_by": "tests/features.py",
-  "old": "            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 404a5fb0fb6041a9d430cbff08be9aae6fab4a21: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json
new file mode 100644
index 000000000..5406b2738
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.CMP_BOUND.394543d6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate CMP_BOUND 394543d6",
+  "killed_by": "tests/features.py",
+  "old": "        return derate if derate < limit else DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return derate if derate <= limit else DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json
new file mode 100644
index 000000000..abb8fc695
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.GUARD_OFF.0035a9e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate GUARD_OFF 0035a9e4",
+  "killed_by": "tests/features.py",
+  "old": "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json
new file mode 100644
index 000000000..8ea6dac74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_partload_derate.RETURN_DEL.208f053a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate RETURN_DEL 208f053a",
+  "killed_by": "tests/features.py",
+  "old": "    return DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json b/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json
new file mode 100644
index 000000000..9cf62ba52
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/delivered_heat_kw.RETURN_DEL.88123fd9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:delivered_heat_kw RETURN_DEL 88123fd9",
+  "killed_by": "tests/features.py",
+  "old": "    return cop * heat_per_cop_kw(params, electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json
new file mode 100644
index 000000000..7f44def31
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.GUARD_OFF.54581fbd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_per_cop_kw GUARD_OFF 54581fbd",
+  "killed_by": "tests/features.py",
+  "old": "    if params.cop_partload_derate:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json
new file mode 100644
index 000000000..c00c1ce2d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/heat_per_cop_kw.RETURN_DEL.6b4aef4f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:heat_per_cop_kw RETURN_DEL 6b4aef4f",
+  "killed_by": "tests/features.py",
+  "old": "    return electrical_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json
new file mode 100644
index 000000000..70cd1c63a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.CMP_BOUND.ca26395f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit CMP_BOUND ca26395f",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0 or band + p_max <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if band < 0.0 or band + p_max <= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json
new file mode 100644
index 000000000..e3023ba08
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.GUARD_OFF.ca26395f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit GUARD_OFF ca26395f",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0 or band + p_max <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json
new file mode 100644
index 000000000..ee2923417
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_derate_limit.RETURN_DEL.7ed3d385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_derate_limit RETURN_DEL 7ed3d385",
+  "killed_by": "tests/features.py",
+  "old": "    return band / (band + p_max)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json
new file mode 100644
index 000000000..a3ef990b0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CLAMP_DROP.e648cdad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor CLAMP_DROP e648cdad",
+  "killed_by": "tests/features.py",
+  "old": "    x = min(max(x, 0.0), 1.0) if np.ndim(x) == 0 else np.clip(x, 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`x = (max(x, 0.0)) if np.ndim(x) == 0 else np.clip(x, 0.0, 1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json
new file mode 100644
index 000000000..51dc3963e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.CMP_BOUND.b007a1a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor CMP_BOUND b007a1a8",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if band < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json
new file mode 100644
index 000000000..a0392305a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.GUARD_OFF.b007a1a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor GUARD_OFF b007a1a8",
+  "killed_by": "tests/features.py",
+  "old": "    if band <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json
new file mode 100644
index 000000000..a8f38068f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/partload_factor.RETURN_DEL.dbcd7d83.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:partload_factor RETURN_DEL dbcd7d83",
+  "killed_by": "tests/features.py",
+  "old": "    return 1.0 - params.cop_partload_derate * x",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
similarity index 54%
rename from tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json
rename to tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
index d8b47c613..8456afa0c 100644
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.110923c2.json
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._buffer_charge_ceiling.net.CLAMP_DROP.0531d42a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net CLAMP_DROP 110923c2",
-  "old": "            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
-  "reason": "Equivalent by construction, and measured. `net` is only ever evaluated at `hi`, `lo` and bisection midpoints between them, and `lo = max(20.0, cop_flow_reference_temp)` with TANK_ROOM_AMBIENT_TEMP = 20.0, so `temp - TANK_ROOM_AMBIENT_TEMP >= 0` at every call and `max(0.0, x)` is `x`. Measured on the F1.10 round-2 head (#1808, review of e964fb78): a differential driver (buffer_probe.py, kept with the PR's evidence) calls _buffer_charge_ceiling over 20736 inputs -- flow_curve_cop on/off, buffer_max_temp 25-75, cop_flow_reference_temp 0-50 (below and above the 20 \u00b0C ambient), one and two zones, three standby-loss scales incl. 0, max power 0.5-9 kW, outdoor -30 to 15 \u00b0C, humidity None/90 -- and spies the tank temperature every `net` call hands marginal_cop: 24468 evaluations, minimum 20.0 \u00b0C. Head vs the CLAMP_DROP mutant: 0 of 20736 ceilings differ.",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_charge_ceiling.net CLAMP_DROP 0531d42a",
+  "old": "            return heat - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)",
+  "reason": "Equivalent by construction, and measured. `net` is only ever evaluated at `hi`, `lo` and bisection midpoints between them, and `lo = max(20.0, cop_flow_reference_temp)` with TANK_ROOM_AMBIENT_TEMP = 20.0, so `temp - TANK_ROOM_AMBIENT_TEMP >= 0` at every call and `max(0.0, x)` is `x`. Measured on the F1.10 round-2 head (#1808, review of e964fb78): a differential driver (buffer_probe.py, kept with the PR's evidence) calls _buffer_charge_ceiling over 20736 inputs -- flow_curve_cop on/off, buffer_max_temp 25-75, cop_flow_reference_temp 0-50 (below and above the 20 \u00b0C ambient), one and two zones, three standby-loss scales incl. 0, max power 0.5-9 kW, outdoor -30 to 15 \u00b0C, humidity None/90 -- and spies the tank temperature every `net` call hands marginal_cop: 24468 evaluations, minimum 20.0 \u00b0C. Head vs the CLAMP_DROP mutant: 0 of 20736 ceilings differ. Re-anchored at R10-COP-PARTLOAD: the line now returns `heat` for what was `p_max * cop`, and the measurement above was taken with the part-load derate at its default 0, where `heat` is exactly `p_max * cop`, so that run still describes this tree on a default install. For a configured derate the equivalence is analytic rather than measured: the term only scales `heat` down, which lowers `net` at every `temp` and cannot make the clamp's argument `temp - TANK_ROOM_AMBIENT_TEMP` negative, so `max(0.0, x)` stays `x` on every input the bisection can reach.",
   "verdict": "equivalent"
 }
diff --git a/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json b/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json
new file mode 100644
index 000000000..c24c036c8
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/thermal_model.py/_partload_derate.CMP_BOUND.0035a9e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_partload_derate CMP_BOUND 0035a9e4",
+  "old": "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:",
+  "reason": "An equivalent mutant on the probed domain, and the only disposition the ledger's one-row-per-anchor key allows: this anchor carries both comparison rewrites of `if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:`, and the lower one (`0.0 < derate ...`) cannot be killed. It separates the two arms at exactly one value, `derate == 0.0` and `-0.0`, where the tree returns `derate` and the mutant returns DEFAULT_HEAT_PUMP_COP_PARTLOAD_DERATE -- both answer 0.0 (the two sign-only cells answer -0.0 against 0.0, numerically equal, and every caller multiplies its heat by 1.0 either way). Measured at d4f3e8b3c by `PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/r10_cop_partload_equiv.py`: `equiv_cells=40 differs=0 config_differs=0` -- 40 inputs (both bounds and their just-outside floats, +0.0 and -0.0, the non-finite floats, numeric strings, non-float types, numpy scalars), each driven directly and through `ThermalParameters.from_config`, with no differing answer; `ties=7` (the seven cells that are 0.0), `sign_only=2` (the -0.0 pair). The tie-only control differs on all 7 tied cells and on 0 untied ones, and `--identity` reads every count 0, so the comparison sees a difference where one exists. The anchor's other rewrite (`0.0 <= derate < MAX`) is NOT equivalent -- it answers the 0 default at 0.5 and differs on the four 0.5 cells (`positive_differs=4`, the probe's positive control) -- and it is killed: `mutation_table.py --pin-killed --scripts tests/features.py` at d4f3e8b3c records `...:1724 CMP_BOUND -- killed by tests/features.py, but its anchor also covers a site no run killed` for it beside `...:1724 CMP_BOUND -- lives` for the lower twin. The configured-derate check in tests/features.py now drives both 0.0 and 0.5, so it kills the upper twin; no check can kill the lower one, which is why this mark is `equivalent` and not a gap.",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index cbc958f16..eb1777578 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17814,
+ "class_excess_loc": 17762,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,

