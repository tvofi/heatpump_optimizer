# Review packet #2912
head: 4fc6a4c51ad990b04f7911807c83b245df3a2141
base: eab04d0ebf8c45667099b668ab0d8bf976d5f99a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123019900931 neutral
arch-score / arch-score id=123016888847 success
budget-raise-gate / budget-raise-gate id=123016889113 success
cancel-superseded id=123013458884 skipped
codeql / Analyze (actions) id=123016888542 success
codeql / Analyze (javascript-typescript) id=123016889037 success
codeql / Analyze (python) id=123016888613 in_progress
governance / delivery-status id=123016891922 skipped
governance / delivery-status-publish id=123016892275 skipped
governance / env-matrix id=123016888727 success
governance / instrument-self-tests id=123016888869 in_progress
governance / policy-docs id=123016889089 success
governance / record id=123016891864 skipped
governance / wave-script id=123016889344 success
hassfest / hassfest id=123016888824 success
kernel-points id=123016891194 skipped
prelude id=123013457168 success
refresh id=123013458860 skipped
tests / arch-instrument id=123022875588 success
tests / briefs id=123016889266 success
tests / browser id=123022875621 success
tests / closure-scope id=123016888924 success
tests / closures id=123022875916 in_progress
tests / coverage id=123022875514 in_progress
tests / fast (3.14) id=123022875786 in_progress
tests / mutation id=123016889009 failure
tests / mutation-autofix id=123022396826 skipped
tests / mutation-pins id=123022396522 skipped
tests / nightly-ha id=123022878657 skipped
tests / nightly-status id=123016890961 skipped
tests / replay id=123022879379 skipped
tests / typing id=123022875723 success
validate / validate-hacs id=123016888570 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item d919cdf6: R10-CONFIGFLOW-PAGES
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_configflow_pages.py
             `dev/audit/harnesses/r10_configflow_pages.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py
             `dev/audit/harnesses/r10_configflow_pages.py` is in the tree at this head
  ok         bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 04_suggested 08_page
             `dev/audit/rounds/round10/D7/arch-s2/run_findings.sh` is in the tree at this head
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         GOLDEN_MODE=drift python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh --body-check <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git diff --stat 6d86acc909f7fc465e5736771daf8fa45c1373a4...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --numstat
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only 6d86acc90...HEAD -- <those five> | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 12 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json
new file mode 100644
index 000000000..94809b4e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._building_wood_flag RETURN_DEL f37fd05d",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..002bda4ed
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._disinfection_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json
new file mode 100644
index 000000000..d249adab3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors BOOLOP 0b8e0158",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submitted and submitted != current.get(CONF_TIBBER_TOKEN):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if submitted or submitted != current.get(CONF_TIBBER_TOKEN):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json
new file mode 100644
index 000000000..b94b2a9aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 0b8e0158",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submitted and submitted != current.get(CONF_TIBBER_TOKEN):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json
new file mode 100644
index 000000000..e92f41977
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 2a9c0142",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if verdict == \"invalid_auth\":",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF c680d852` (the guard moved into `HeatPumpOptimizerOptionsFlow._entities_errors`). Previous: Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json
new file mode 100644
index 000000000..31e23f5fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 30631ec6",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if not view.get(CONF_PRICE_ENTITY):",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF b9ebe2fa` (the guard moved into `HeatPumpOptimizerOptionsFlow._entities_errors`). Previous: Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json
new file mode 100644
index 000000000..74eb45e98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 83cb93cb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if source == PRICE_SOURCE_ENTITY:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json
new file mode 100644
index 000000000..bce266f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF b4c07480",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            elif verdict != \"ok\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json
new file mode 100644
index 000000000..37339431d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF c7990b6d",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not (submit.get(CONF_TIBBER_TOKEN) or current.get(CONF_TIBBER_TOKEN)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json
new file mode 100644
index 000000000..20e795a55
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors RETURN_DEL 421708f2",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..a2154851e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json
new file mode 100644
index 000000000..713819368
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._grid_fee_errors GUARD_OFF ea8cc91b",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if fee_problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..81cbba591
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._grid_fee_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json
new file mode 100644
index 000000000..729871f08
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors BOOLOP 47acdc72",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not errors and _dhw_min_too_close(submit, current):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not errors or _dhw_min_too_close(submit, current):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json
new file mode 100644
index 000000000..6e44953f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 03e357ee",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if window_problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json
new file mode 100644
index 000000000..74a645116
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 355fc9b4",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if holiday_spec:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 02e99d97` (the guard moved into `HeatPumpOptimizerOptionsFlow._hot_water_errors`). Previous: Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json
new file mode 100644
index 000000000..77c40dfe0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 47acdc72",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not errors and _dhw_min_too_close(submit, current):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json
new file mode 100644
index 000000000..3c21a0833
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 8cd5759a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if holiday_problem is not None:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 07c72f5d` (the guard moved into `HeatPumpOptimizerOptionsFlow._hot_water_errors`). Previous: Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..a44f5fbd6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json
new file mode 100644
index 000000000..2af5344d6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors BOOLOP bdb67645",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL or not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json
new file mode 100644
index 000000000..d28394727
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors GUARD_OFF bdb67645",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities_metering GUARD_OFF c8d82db8` (the guard moved into `HeatPumpOptimizerOptionsFlow._metering_errors`). Previous: Recorded by `mutation_table.py --drain` against c3530277373ddf87652858f9ecb0ee1cf36f4347: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..409ba2c17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json
new file mode 100644
index 000000000..8a80b5923
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._page GUARD_OFF 45af9d64",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if check is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=39."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json
new file mode 100644
index 000000000..429055959
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._page GUARD_OFF 980b44df",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if not errors:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF 980b44df` (the guard moved into `HeatPumpOptimizerOptionsFlow._page`). Previous: Recorded by `mutation_table.py --drain` against 3976515a08228598ea3863f4f36dc4c7c4846865: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json
new file mode 100644
index 000000000..1ff31b621
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors GUARD_OFF 67752ca1",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not _valid_months_spec(submit.get(CONF_PEAK_TARIFF_MONTHS, \"\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json
new file mode 100644
index 000000000..773da22f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors GUARD_OFF 821aac0b",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not is_valid_spec(submit.get(CONF_PEAK_TARIFF_HOURS, \"\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..bd699c6c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..3035848a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._plumbing_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json
new file mode 100644
index 000000000..81c95f777
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._silent_window_errors GUARD_OFF 093742d2",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..b90654ac3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._silent_window_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json
deleted file mode 100644
index d9d261a87..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_comfort GUARD_OFF b75e92ec",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if user_input is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json
new file mode 100644
index 000000000..d6b058854
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_comfort RETURN_DEL a5ae6e26",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return await self._page(\"comfort\", user_input, clear=True, check=self._comfort_errors)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json
deleted file mode 100644
index 0285b7415..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF 980b44df",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if not errors:",
-  "reason": "Recorded by `mutation_table.py --drain` against 3976515a08228598ea3863f4f36dc4c7c4846865: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=30."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json
deleted file mode 100644
index d3a67260c..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF b9ebe2fa",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                if not entity:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json
deleted file mode 100644
index 5b3cd5a3f..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF c680d852",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                        if verdict == \"invalid_auth\":",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json
deleted file mode 100644
index 0e3fbbea6..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities_metering GUARD_OFF c8d82db8",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if user_input.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not user_input.get(CONF_COMPRESSOR_FREQ_ENTITY):",
-  "reason": "Recorded by `mutation_table.py --drain` against c3530277373ddf87652858f9ecb0ee1cf36f4347: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json
deleted file mode 100644
index 31ab43fca..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 02e99d97",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if holiday_spec:",
-  "reason": "Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json
deleted file mode 100644
index 630f10fc2..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 07c72f5d",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                if holiday_problem is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json
deleted file mode 100644
index a4b037dd4..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank GUARD_OFF b75e92ec",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if user_input is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against 15f0b5924f3c2a75befe984d156cb3e602effd2e: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=10."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json
new file mode 100644
index 000000000..6a7ab27f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_apply_dso_catalog GUARD_OFF 607abe98",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if applied:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json
new file mode 100644
index 000000000..d21895ba8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_apply_dso_catalog RETURN_DEL 0ff10d02",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json b/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json
new file mode 100644
index 000000000..fb4cd34aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fee_placeholders RETURN_DEL aa4e4753",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {\"currency\": currency, \"fee_bound\": f\"{grid_fee.fee_bound(currency):g}\"}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json
new file mode 100644
index 000000000..b1fcd2416
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_peak_window_as_int GUARD_OFF ab2bb6c0",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if window is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json
new file mode 100644
index 000000000..6bb9e21ca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_peak_window_as_int RETURN_DEL 0ff10d02",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json
new file mode 100644
index 000000000..9c6f7c7e2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_warn_legionella_ceiling GUARD_OFF 04d1f31e",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if warning is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json
new file mode 100644
index 000000000..16b920934
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_warn_legionella_ceiling RETURN_DEL 455596d0",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return submit",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index bc51e5feb..1dffb3e88 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -3,7 +3,7 @@ from __future__ import annotations
 
 import hashlib
 import logging
-from collections.abc import Callable, Iterable, Mapping
+from collections.abc import Awaitable, Callable, Iterable, Mapping
 from typing import TYPE_CHECKING, Any, Final, NamedTuple, Protocol, cast
 
 import aiohttp
@@ -1873,6 +1873,52 @@ def _section_inner(value: Any) -> vol.Schema | None:
     return inner if isinstance(inner, vol.Schema) else None
 
 
+#: A page's refusal: the submit (flattened, cleared rows nulled) and the stored
+#: config in, the per-field errors out (empty to save).
+_PageCheck = Callable[[dict[str, Any], dict[str, Any]], Awaitable[dict[str, str]]]
+#: What a page saves, from the accepted submit and the submit merged over the
+#: stored config (before any cleared row is nulled).
+_PageFinish = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
+
+
+def _warn_legionella_ceiling(submit: dict[str, Any], merged: dict[str, Any]) -> dict[str, Any]:
+    """Warned, never blocked -- see the setup flow's DHW step."""
+    warning = _dhw_legionella_warning(submit, merged)
+    if warning is not None:
+        _LOGGER.warning(
+            "Hot water: the anti-legionella cycle at %s °C is "
+            "above the %s °C charge limit, so the tank is taken "
+            "above that limit every %s days",
+            warning["legionella_temp"],
+            warning["setpoint"],
+            warning["interval_days"],
+        )
+    return submit
+
+
+def _peak_window_as_int(submit: dict[str, Any], _merged: dict[str, Any]) -> dict[str, Any]:
+    cleaned = dict(submit)
+    window = cleaned.get(CONF_PEAK_TARIFF_WINDOW)
+    if window is not None:
+        try:
+            cleaned[CONF_PEAK_TARIFF_WINDOW] = int(window)
+        except (TypeError, ValueError):
+            cleaned[CONF_PEAK_TARIFF_WINDOW] = DEFAULT_PEAK_TARIFF_WINDOW
+    return cleaned
+
+
+def _apply_dso_catalog(cleaned: dict[str, Any], _merged: dict[str, Any]) -> dict[str, Any]:
+    applied = grid_fee.apply_catalog(cleaned.get(CONF_DSO_PRODUCT))
+    if applied:
+        cleaned.update(applied)
+    return cleaned
+
+
+def _fee_placeholders(hass: HomeAssistant) -> dict[str, str]:
+    currency = resolve_currency(hass)
+    return {"currency": currency, "fee_bound": f"{grid_fee.fee_bound(currency):g}"}
+
+
 def _flatten_section_input(user_input: dict[str, Any]) -> dict[str, Any]:
     """Lift ``section()`` payloads to option keys.
 
@@ -3205,21 +3251,46 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         return await self.async_step_init()
 
     async def _page(
-        self, step_id: str, user_input: dict[str, Any] | None, *, clear: bool = False
+        self,
+        step_id: str,
+        user_input: dict[str, Any] | None,
+        *,
+        clear: bool = False,
+        check: _PageCheck | None = None,
+        finish: _PageFinish | None = None,
+        placeholders: Mapping[str, str] | None = None,
     ) -> ConfigFlowResult:
         """One registry page (#597): save the submit, or show the form.
 
-        ``clear`` hands the submit to ``_clear_absent`` first, so a stored
-        entity row the user emptied is nulled rather than kept. A page with
-        no ``_STORED`` row passes ``clear=False``: there is nothing to null.
+        Every options page is this one sequence: lift the ``section()``
+        groups, null the stored entity rows the user emptied (``clear``),
+        refuse the submit with ``check``'s errors, shape what is saved with
+        ``finish``, and otherwise re-render the rejected form with what was
+        typed rather than with the stored values the user was changing.
+
+        ``clear`` hands the submit to ``_clear_absent``, judged over the
+        SUBMISSION merged onto the stored config, so a block the same submit
+        turns off still clears its own slots. A page with no ``_STORED`` row
+        passes ``clear=False``: there is nothing to null.
         """
+        errors: dict[str, str] = {}
         current = self._current
         if user_input is not None:
-            return await self._save_or_menu(
-                _clear_absent(user_input, step_id, current) if clear else user_input
-            )
+            flat = _flatten_section_input(user_input)
+            merged = {**current, **flat}
+            cleaned = _clear_absent(flat, step_id, merged) if clear else flat
+            if check is not None:
+                errors = await check(cleaned, current)
+            if not errors:
+                return await self._save_or_menu(
+                    finish(cleaned, merged) if finish is not None else cleaned
+                )
+            current = {**current, **cleaned}
         return self.async_show_form(
-            step_id=step_id, data_schema=_page_schema(step_id, current, self.hass)
+            step_id=step_id,
+            errors=errors,
+            description_placeholders=placeholders,
+            data_schema=_page_schema(step_id, current, self.hass),
         )
 
     async def _thermal_model_page(
@@ -3393,68 +3464,56 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Change which Home Assistant entities the optimizer reads."""
-        errors: dict[str, str] = {}
-        current = self._current
+        return await self._page(
+            "entities", user_input, clear=True, check=self._entities_errors
+        )
 
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            source = user_input.get(
-                CONF_PRICE_SOURCE, current.get(CONF_PRICE_SOURCE, DEFAULT_PRICE_SOURCE)
-            )
-            if source == PRICE_SOURCE_ENTITY:
-                entity = user_input.get(CONF_PRICE_ENTITY) or current.get(
-                    CONF_PRICE_ENTITY
-                )
-                if not entity:
-                    errors[CONF_PRICE_ENTITY] = "price_entity_required"
-            else:
-                token = user_input.get(CONF_TIBBER_TOKEN) or current.get(
-                    CONF_TIBBER_TOKEN
-                )
-                if not token:
-                    errors[CONF_TIBBER_TOKEN] = "tibber_token_required"
-                else:
-                    submitted = user_input.get(CONF_TIBBER_TOKEN)
-                    if submitted and submitted != current.get(CONF_TIBBER_TOKEN):
-                        verdict = await validate_tibber_token(self.hass, submitted)
-                        if verdict == "invalid_auth":
-                            errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
-                        elif verdict != "ok":
-                            errors[CONF_TIBBER_TOKEN] = "cannot_connect"
-            if not errors:
-                return await self._save_or_menu(
-                    _clear_absent(user_input, "entities", current)
-                )
-            current = {**current, **user_input}
+    async def _entities_errors(
+        self, submit: dict[str, Any], current: dict[str, Any]
+    ) -> dict[str, str]:
+        """The price source must name its feed; a new Tibber token must work.
 
-        return self.async_show_form(
-            step_id="entities",
-            errors=errors,
-            data_schema=_page_schema("entities", current, self.hass),
-        )
+        The source and its entity are judged over what would be stored: a
+        cleared price entity reaches here as ``None`` (``_clear_absent``), so
+        clearing it under an entity source is refused rather than saved as a
+        source with no feed -- the rule ``_disinfection_errors`` applies.
+        """
+        errors: dict[str, str] = {}
+        view = {**current, **submit}
+        source = view.get(CONF_PRICE_SOURCE, DEFAULT_PRICE_SOURCE)
+        if source == PRICE_SOURCE_ENTITY:
+            if not view.get(CONF_PRICE_ENTITY):
+                errors[CONF_PRICE_ENTITY] = "price_entity_required"
+            return errors
+        if not (submit.get(CONF_TIBBER_TOKEN) or current.get(CONF_TIBBER_TOKEN)):
+            errors[CONF_TIBBER_TOKEN] = "tibber_token_required"
+            return errors
+        submitted = submit.get(CONF_TIBBER_TOKEN)
+        if submitted and submitted != current.get(CONF_TIBBER_TOKEN):
+            verdict = await validate_tibber_token(self.hass, submitted)
+            if verdict == "invalid_auth":
+                errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
+            elif verdict != "ok":
+                errors[CONF_TIBBER_TOKEN] = "cannot_connect"
+        return errors
 
     async def async_step_entities_metering(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Solar, power and compressor frequency sensors."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            # Only a number entity can be written; a sensor alone observes.
-            if user_input.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not user_input.get(CONF_COMPRESSOR_FREQ_ENTITY):
-                errors[CONF_FREQ_CONTROL_MODE] = "freq_control_needs_number"
-            else:
-                return await self._save_or_menu(
-                    _clear_absent(user_input, "entities_metering", current)
-                )
-            current = {**current, **user_input}
-        return self.async_show_form(
-            step_id="entities_metering",
-            errors=errors,
-            data_schema=_page_schema("entities_metering", current, self.hass),
+        return await self._page(
+            "entities_metering", user_input, clear=True, check=self._metering_errors
         )
 
+    async def _metering_errors(
+        self, submit: dict[str, Any], _current: dict[str, Any]
+    ) -> dict[str, str]:
+        """Only a number entity can be written; a sensor alone observes."""
+        errors: dict[str, str] = {}
+        if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):
+            errors[CONF_FREQ_CONTROL_MODE] = "freq_control_needs_number"
+        return errors
+
     async def async_step_entities_pump(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
@@ -3465,92 +3524,66 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """How warm the house should be, and when."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            errors = _band_errors(user_input, current)
-            if not errors:
-                return await self._save_or_menu(
-                    _clear_absent(user_input, "comfort", current)
-                )
-            # Re-render the rejected form with what was typed, not with the
-            # stored values the user was in the middle of changing.
-            current = {**current, **user_input}
-        return self.async_show_form(
-            step_id="comfort",
-            errors=errors,
-            data_schema=_page_schema("comfort", current, self.hass),
-        )
+        return await self._page("comfort", user_input, clear=True, check=self._comfort_errors)
+
+    async def _comfort_errors(
+        self, submit: dict[str, Any], current: dict[str, Any]
+    ) -> dict[str, str]:
+        return _band_errors(submit, current)
 
     async def async_step_hot_water(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """When hot water is needed and how hot it has to be."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            window_problem = dhw_spec_problem(user_input.get(CONF_DHW_WINDOWS, ""))
-            if window_problem is not None:
-                errors[CONF_DHW_WINDOWS] = window_problem
-            holiday_spec = user_input.get(CONF_HOLIDAY_DHW_WINDOWS, "")
-            if holiday_spec:
-                holiday_problem = dhw_spec_problem(holiday_spec)
-                if holiday_problem is not None:
-                    errors[CONF_HOLIDAY_DHW_WINDOWS] = holiday_problem
-            # #1260: each revealed per-day field gets the ordinary verdicts
-            # plus the selector refusal, on its own key.
-            errors.update(_dhw_day_field_errors(user_input))
-            if not errors and _dhw_min_too_close(user_input, current):
-                errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
-            if not errors:
-                # Warned, never blocked — see the setup flow's DHW step.
-                warning = _dhw_legionella_warning(user_input, current)
-                if warning is not None:
-                    _LOGGER.warning(
-                        "Hot water: the anti-legionella cycle at %s °C is "
-                        "above the %s °C charge limit, so the tank is taken "
-                        "above that limit every %s days",
-                        warning["legionella_temp"],
-                        warning["setpoint"],
-                        warning["interval_days"],
-                    )
-                return await self._save_or_menu(
-                    _clear_absent(user_input, "hot_water", current)
-                )
-            current = {**current, **user_input}
-
-        return self.async_show_form(
-            step_id="hot_water",
-            errors=errors,
-            description_placeholders=_WINDOW_PLACEHOLDERS,
-            data_schema=_page_schema("hot_water", current, self.hass),
+        return await self._page(
+            "hot_water",
+            user_input,
+            clear=True,
+            check=self._hot_water_errors,
+            finish=_warn_legionella_ceiling,
+            placeholders=_WINDOW_PLACEHOLDERS,
         )
 
+    async def _hot_water_errors(
+        self, submit: dict[str, Any], current: dict[str, Any]
+    ) -> dict[str, str]:
+        errors: dict[str, str] = {}
+        window_problem = dhw_spec_problem(submit.get(CONF_DHW_WINDOWS, ""))
+        if window_problem is not None:
+            errors[CONF_DHW_WINDOWS] = window_problem
+        holiday_spec = submit.get(CONF_HOLIDAY_DHW_WINDOWS, "")
+        if holiday_spec:
+            holiday_problem = dhw_spec_problem(holiday_spec)
+            if holiday_problem is not None:
+                errors[CONF_HOLIDAY_DHW_WINDOWS] = holiday_problem
+        # #1260: each revealed per-day field gets the ordinary verdicts
+        # plus the selector refusal, on its own key.
+        errors.update(_dhw_day_field_errors(submit))
+        if not errors and _dhw_min_too_close(submit, current):
+            errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
+        return errors
+
     async def async_step_hot_water_tank(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Tank size, inlet water, advanced DHW learning and the pump's switch."""
+        return await self._page(
+            "hot_water_tank", user_input, clear=True, check=self._disinfection_errors
+        )
+
+    async def _disinfection_errors(
+        self, submit: dict[str, Any], current: dict[str, Any]
+    ) -> dict[str, str]:
+        """#1067: control writes the pump's disinfection switch, so it is refused
+        without one -- judged over what would be stored, so clearing the switch
+        under a stored control mode is refused too."""
         errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            cleaned = _clear_absent(user_input, "hot_water_tank", current)
-            merged = {**current, **cleaned}
-            # #1067: control writes the pump's disinfection switch, so it is
-            # refused without one -- judged over what would be stored, so
-            # clearing the switch under a stored control mode is refused too.
-            if merged.get(CONF_DHW_DISINFECTION_MODE) != FREQ_MODE_CONTROL or merged.get(
-                CONF_DHW_DISINFECTION_SWITCH_ENTITY
-            ):
-                return await self._save_or_menu(cleaned)
+        merged = {**current, **submit}
+        if merged.get(CONF_DHW_DISINFECTION_MODE) == FREQ_MODE_CONTROL and not merged.get(
+            CONF_DHW_DISINFECTION_SWITCH_ENTITY
+        ):
             errors[CONF_DHW_DISINFECTION_MODE] = "disinfection_control_needs_entity"
-            current = merged
-        return self.async_show_form(
-            step_id="hot_water_tank",
-            errors=errors,
-            data_schema=_page_schema("hot_water_tank", current, self.hass),
-        )
+        return errors
 
     async def async_step_hot_water_pumps(
         self, user_input: dict[str, Any] | None = None
@@ -3577,53 +3610,44 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         configured is caught as an error instead of being saved and
         silently skipped every write cycle.
         """
+        return await self._page(
+            "building",
+            user_input,
+            clear=True,
+            check=self._plumbing_errors,
+            finish=self._building_wood_flag,
+        )
+
+    async def _plumbing_errors(
+        self, submit: dict[str, Any], current: dict[str, Any]
+    ) -> dict[str, str]:
+        """The write-target kind (#398) and the flow-curve lift (#1067), validated."""
         errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            if (
-                user_input.get(CONF_MIXING_VALVE_WRITE_TARGET_KIND)
-                == mixing_valve.WRITE_TARGET_FLOW
-                and not ThermalParameters.from_config(
-                    {**current, **user_input}
-                ).two_zone_enabled
-            ):
-                errors[CONF_MIXING_VALVE_WRITE_TARGET_KIND] = (
-                    "flow_target_needs_two_zone"
-                )
-            elif user_input.get(CONF_FLOW_CURVE_COP_ENABLED) and (
-                mixing_valve.is_throttling(
-                    {**current, **user_input}.get(CONF_MIXING_VALVE_MODE)
-                )
-            ):
-                # #1067: behind a throttling valve the tank temperature is
-                # already the priced flow; the model refuses the curve lift
-                # there too, so saving it would be a switch that does nothing.
-                errors[CONF_FLOW_CURVE_COP_ENABLED] = (
-                    "flow_curve_needs_direct_plant"
-                )
-            else:
-                # The wood block's rows carry ``when=wood_furnace_on``, so one
-                # predicate decides both what the page rendered and what its
-                # save may clear. It is evaluated over the SUBMISSION merged
-                # onto the stored config, not over the stored config alone:
-                # turning the block off would otherwise still clear its slots.
-                merged = {**current, **user_input}
-                cleaned = _clear_absent(user_input, "building", merged)
-                if wood_furnace_on(merged):
-                    cleaned[CONF_WOOD_FURNACE_ENABLED] = True
-                elif CONF_WOOD_FURNACE_ENABLED in cleaned:
-                    cleaned[CONF_WOOD_FURNACE_ENABLED] = bool(
-                        cleaned[CONF_WOOD_FURNACE_ENABLED]
-                    )
-                return await self._save_or_menu(cleaned)
-            current = {**current, **user_input}
+        merged = {**current, **submit}
+        if (
+            submit.get(CONF_MIXING_VALVE_WRITE_TARGET_KIND) == mixing_valve.WRITE_TARGET_FLOW
+            and not ThermalParameters.from_config(merged).two_zone_enabled
+        ):
+            errors[CONF_MIXING_VALVE_WRITE_TARGET_KIND] = "flow_target_needs_two_zone"
+        elif submit.get(CONF_FLOW_CURVE_COP_ENABLED) and mixing_valve.is_throttling(
+            merged.get(CONF_MIXING_VALVE_MODE)
+        ):
+            # #1067: behind a throttling valve the tank temperature is already
+            # the priced flow; the model refuses the curve lift there too, so
+            # saving it would be a switch that does nothing.
+            errors[CONF_FLOW_CURVE_COP_ENABLED] = "flow_curve_needs_direct_plant"
+        return errors
 
-        return self.async_show_form(
-            step_id="building",
-            errors=errors,
-            data_schema=_page_schema("building", current, self.hass),
-        )
+    @staticmethod
+    def _building_wood_flag(cleaned: dict[str, Any], merged: dict[str, Any]) -> dict[str, Any]:
+        """The wood block's rows carry ``when=wood_furnace_on``, so one predicate
+        decides both what the page rendered and what its save may clear, over
+        the submission merged onto the stored config."""
+        if wood_furnace_on(merged):
+            cleaned[CONF_WOOD_FURNACE_ENABLED] = True
+        elif CONF_WOOD_FURNACE_ENABLED in cleaned:
+            cleaned[CONF_WOOD_FURNACE_ENABLED] = bool(cleaned[CONF_WOOD_FURNACE_ENABLED])
+        return cleaned
 
     async def async_step_thermal_model(
         self, user_input: dict[str, Any] | None = None
@@ -3695,97 +3719,73 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Peak capacity tariff hours and pricing."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            if not _valid_months_spec(
-                user_input.get(CONF_PEAK_TARIFF_MONTHS, "")
-            ):
-                errors[CONF_PEAK_TARIFF_MONTHS] = "invalid_peak_months"
-            if not is_valid_spec(user_input.get(CONF_PEAK_TARIFF_HOURS, "")):
-                errors[CONF_PEAK_TARIFF_HOURS] = "invalid_peak_hours"
-            if not errors:
-                cleaned = dict(user_input)
-                window = cleaned.get(CONF_PEAK_TARIFF_WINDOW)
-                if window is not None:
-                    try:
-                        cleaned[CONF_PEAK_TARIFF_WINDOW] = int(window)
-                    except (TypeError, ValueError):
-                        cleaned[CONF_PEAK_TARIFF_WINDOW] = (
-                            DEFAULT_PEAK_TARIFF_WINDOW
-                        )
-                return await self._save_or_menu(cleaned)
-            current = {**current, **user_input}
-
-        return self.async_show_form(
-            step_id="grid",
-            errors=errors,
-            description_placeholders={
-                "currency": resolve_currency(self.hass),
-                "fee_bound": f"{grid_fee.fee_bound(resolve_currency(self.hass)):g}",
-            },
-            data_schema=_page_schema("grid", current, self.hass),
+        return await self._page(
+            "grid",
+            user_input,
+            check=self._peak_tariff_errors,
+            finish=_peak_window_as_int,
+            placeholders=_fee_placeholders(self.hass),
         )
 
+    async def _peak_tariff_errors(
+        self, submit: dict[str, Any], _current: dict[str, Any]
+    ) -> dict[str, str]:
+        errors: dict[str, str] = {}
+        if not _valid_months_spec(submit.get(CONF_PEAK_TARIFF_MONTHS, "")):
+            errors[CONF_PEAK_TARIFF_MONTHS] = "invalid_peak_months"
+        if not is_valid_spec(submit.get(CONF_PEAK_TARIFF_HOURS, "")):
+            errors[CONF_PEAK_TARIFF_HOURS] = "invalid_peak_hours"
+        return errors
+
     async def async_step_grid_connection(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Main fuse, peak guards and the pump's silent-mode window."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
+        return await self._page(
+            "grid_connection",
             # A cleared text field is absent, and options merge over setup
             # data, so an absent window would silently keep the old one.
-            user_input = {CONF_SILENT_MODE_WINDOWS: "", **user_input}
-            problem = dhw_spec_problem(user_input[CONF_SILENT_MODE_WINDOWS])
-            if problem is None:
-                return await self._save_or_menu(user_input)
+            None if user_input is None else {CONF_SILENT_MODE_WINDOWS: "", **user_input},
+            check=self._silent_window_errors,
+            placeholders=_WINDOW_PLACEHOLDERS,
+        )
+
+    async def _silent_window_errors(
+        self, submit: dict[str, Any], _current: dict[str, Any]
+    ) -> dict[str, str]:
+        errors: dict[str, str] = {}
+        problem = dhw_spec_problem(submit[CONF_SILENT_MODE_WINDOWS])
+        if problem is not None:
             errors[CONF_SILENT_MODE_WINDOWS] = (
                 "silent_mode_window_too_short"
                 if problem == DHW_ERROR_TOO_SHORT
                 else problem
             )
-            current = {**current, **user_input}
-        return self.async_show_form(
-            step_id="grid_connection",
-            errors=errors,
-            description_placeholders=_WINDOW_PLACEHOLDERS,
-            data_schema=_page_schema("grid_connection", current, self.hass),
-        )
+        return errors
 
     async def async_step_grid_fees(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
         """Transfer fees and contract shadow price."""
-        errors: dict[str, str] = {}
-        current = self._current
-        if user_input is not None:
-            user_input = _flatten_section_input(user_input)
-            fee_problem = grid_fee.spec_problem(
-                user_input.get(CONF_GRID_FEE_RULES, ""), resolve_currency(self.hass)
-            )
-            if fee_problem is not None:
-                errors[CONF_GRID_FEE_RULES] = fee_problem
-            if not errors:
-                cleaned = _clear_absent(user_input, "grid_fees", current)
-                applied = grid_fee.apply_catalog(user_input.get(CONF_DSO_PRODUCT))
-                if applied:
-                    cleaned.update(applied)
-                return await self._save_or_menu(cleaned)
-            current = {**current, **user_input}
-            if not user_input.get(CONF_GRID_FEE_ENTITY):
-                current.pop(CONF_GRID_FEE_ENTITY, None)
+        return await self._page(
+            "grid_fees",
+            user_input,
+            clear=True,
+            check=self._grid_fee_errors,
+            finish=_apply_dso_catalog,
+            placeholders=_fee_placeholders(self.hass),
+        )
 
-        return self.async_show_form(
-            step_id="grid_fees",
-            errors=errors,
-            description_placeholders={
-                "currency": resolve_currency(self.hass),
-                "fee_bound": f"{grid_fee.fee_bound(resolve_currency(self.hass)):g}",
-            },
-            data_schema=_page_schema("grid_fees", current, self.hass),
+    async def _grid_fee_errors(
+        self, submit: dict[str, Any], _current: dict[str, Any]
+    ) -> dict[str, str]:
+        errors: dict[str, str] = {}
+        fee_problem = grid_fee.spec_problem(
+            submit.get(CONF_GRID_FEE_RULES, ""), resolve_currency(self.hass)
         )
+        if fee_problem is not None:
+            errors[CONF_GRID_FEE_RULES] = fee_problem
+        return errors
 
     async def async_step_solar_pv(
         self, user_input: dict[str, Any] | None = None
diff --git a/dev/audit/harnesses/r10_configflow_pages.py b/dev/audit/harnesses/r10_configflow_pages.py
new file mode 100644
index 000000000..e31f7a20a
--- /dev/null
+++ b/dev/audit/harnesses/r10_configflow_pages.py
@@ -0,0 +1,206 @@
+#!/usr/bin/env python3
+"""R10-CONFIGFLOW-PAGES (#2238; D7-s2-56 and Arm A3'): the options page template, driven.
+
+Ported from the design's probes ``rejected_rerender.py`` and ``clear_required.py``
+(``dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/`` on ``design/R10-CONFIGFLOW-PAGES``
+32892dc67). Every arm drives the production step handlers of
+``HeatPumpOptimizerOptionsFlow`` over ``tests/harness``'s ``FakeEntry``/``FakeHass``.
+
+Arms (one per invocation):
+
+  (default)   For each of the nine validating options pages, store an entity in each of
+              the page's ``_STORED`` rows (``when`` gates opened), submit with every one
+              cleared plus one field that makes the page reject, and count the cleared rows
+              that re-render with the STORED entity as ``suggested_value``.
+                stale_slots   cleared rows re-rendered as stored (the defect)
+                rejected      pages whose submit was refused
+  --null      The same rejection with nothing cleared: ``shown_stored`` counts rows
+              re-rendered as stored (a page that accepts this submit shows no form and
+              contributes 0; its ``rejected`` reads 0).
+  --clear-required        Stored ``price_source: entity`` and ``price_entity: sensor.price``;
+              submit the entities page with the source and no price entity (cleared).
+  --clear-required --null The same submit with ``price_entity: sensor.other``.
+  --accepted  A3: one accepted submit per page, plus the A3' case. Prints each case's
+              saved options as canonical JSON with its sha1, so the output at the base and
+              at the head are diffed. The case ``price_entity_cleared_under_entity_source``
+              is the one deliberate behaviour change (A3-exception): it is printed on its
+              own line, excluded from ``digest``, and ``exceptions`` must read 1.
+
+Re-run when ``_page``, ``_clear_absent``, any options ``async_step_*`` of the nine pages or
+their predicates change.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py [arm]
+
+Expected, measured at origin/main 6d86acc90 (base) and at the arm-A head:
+    default                 base: stale_slots=27 stored_rows=30   head: stale_slots=0 stored_rows=30
+    --null                  base and head: shown_stored=19 rejected=7
+    --clear-required        base: type=menu stored_price_entity=None
+                            head: type=form errors=price_entity_required stored_price_entity='sensor.price'
+    --clear-required --null base and head: type=menu stored_price_entity='sensor.other'
+    --accepted              base and head: the same digest, exceptions=1
+"""
+import asyncio
+import hashlib
+import json
+import sys
+from pathlib import Path
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
+ROOT = repo_root(Path(__file__))
+sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]
+
+from harness import FakeEntry, FakeHass  # noqa: E402
+from heatpump_optimizer import config_flow as cf  # noqa: E402
+from heatpump_optimizer import const as c  # noqa: E402
+from heatpump_optimizer.freq_control import FREQ_MODE_CONTROL  # noqa: E402
+
+
+async def _refuse_token(_hass, _token):
+    return "invalid_auth"
+
+
+async def _accept_token(_hass, _token):
+    return "ok"
+
+
+#: page -> (base config opening its gates, the field set that makes it reject)
+REJECT = {
+    "entities": ({c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "old"},
+                 {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "new-bad"}),
+    "entities_metering": ({}, {c.CONF_FREQ_CONTROL_MODE: FREQ_MODE_CONTROL}),
+    "comfort": ({}, {c.CONF_MIN_TEMP: 25.0, c.CONF_MAX_TEMP: 18.0}),
+    "hot_water": ({c.CONF_DHW_ENABLED: True}, {c.CONF_DHW_WINDOWS: "nonsense"}),
+    "hot_water_tank": ({}, {c.CONF_DHW_DISINFECTION_MODE: FREQ_MODE_CONTROL}),
+    "building": ({c.CONF_WOOD_FURNACE_ENABLED: True},
+                 {c.CONF_WOOD_FURNACE_ENABLED: True, c.CONF_MIXING_VALVE_WRITE_TARGET_KIND: "flow"}),
+    "grid": ({}, {c.CONF_PEAK_TARIFF_MONTHS: "13-14"}),
+    "grid_connection": ({}, {c.CONF_SILENT_MODE_WINDOWS: "nonsense"}),
+    "grid_fees": ({}, {c.CONF_GRID_FEE_RULES: "nonsense"}),
+}
+
+#: A3: (case, page, stored config, submit) -- each accepted at the base.
+EXCEPTION = "price_entity_cleared_under_entity_source"
+_PRICE = {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY, c.CONF_PRICE_ENTITY: "sensor.price"}
+ACCEPTED = [
+    ("entities_keep", "entities", _PRICE, {**_PRICE, c.CONF_WEATHER_ENTITY: "weather.home"}),
+    ("entities_replace", "entities", _PRICE, {**_PRICE, c.CONF_PRICE_ENTITY: "sensor.other"}),
+    ("entities_tibber", "entities", _PRICE,
+     {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "t"}),
+    (EXCEPTION, "entities", _PRICE, {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY}),
+    ("entities_metering", "entities_metering", {}, {c.CONF_FREQ_CONTROL_MODE: "observe"}),
+    ("comfort", "comfort", {}, {c.CONF_MIN_TEMP: 18.0, c.CONF_MAX_TEMP: 24.0}),
+    ("hot_water", "hot_water", {c.CONF_DHW_ENABLED: True}, {c.CONF_DHW_WINDOWS: "06:00-07:00"}),
+    ("hot_water_tank", "hot_water_tank", {}, {c.CONF_DHW_DISINFECTION_MODE: "observe"}),
+    ("building", "building", {c.CONF_WOOD_FURNACE_ENABLED: True},
+     {c.CONF_WOOD_FURNACE_ENABLED: False}),
+    ("grid", "grid", {}, {c.CONF_PEAK_TARIFF_MONTHS: "nov-feb", c.CONF_PEAK_TARIFF_WINDOW: "3"}),
+    ("grid_connection", "grid_connection", {c.CONF_SILENT_MODE_WINDOWS: "22:00-06:00"},
+     {c.CONF_MAIN_FUSE_A: 25}),
+    ("grid_fees", "grid_fees", {c.CONF_GRID_FEE_ENTITY: "sensor.fee"}, {}),
+]
+
+
+def suggested(result, key):
+    def walk(schema):
+        for m, v in schema.schema.items():
+            inner = cf._section_inner(v)
+            if inner is not None:
+                yield from walk(inner)
+            else:
+                yield m
+    for m in walk(result["data_schema"]):
+        if str(getattr(m, "schema", m)) == key:
+            d = getattr(m, "description", None) or {}
+            return d.get("suggested_value", getattr(m, "default", None))
+    return None
+
+
+def _flow(entry):
+    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
+    flow.hass = FakeHass()
+    return flow
+
+
+async def rerender(step, null):
+    base, bad = REJECT[step]
+    rows = [r for r in cf._page_rows(step, {**base, c.CONF_WOOD_FURNACE_ENABLED: True})
+            if r.default is cf._STORED]
+    stored = {r.key: f"sensor.stored_{i}" for i, r in enumerate(rows)}
+    res = await getattr(_flow(FakeEntry(data={**base, **stored})), f"async_step_{step}")(
+        dict(bad) if not null else {**stored, **bad})
+    rejected = res.get("type") == "form" and bool(res.get("errors"))
+    if "data_schema" not in res:
+        return len(rows), False, 0, res.get("type"), res.get("step_id")
+    hits = sum(1 for k, v in stored.items() if suggested(res, k) == v)
+    return len(rows), rejected, hits, res.get("type"), res.get("errors")
+
+
+async def clear_required(null):
+    entry = FakeEntry(data=dict(_PRICE))
+    submit = {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY}
+    if null:
+        submit[c.CONF_PRICE_ENTITY] = "sensor.other"
+    res = await _flow(entry).async_step_entities(submit)
+    saved = {**entry.data, **(entry.options or {})}
+    errs = ",".join(sorted((res.get("errors") or {}).values())) or None
+    print(f"RESULT type={res.get('type')} errors={errs} "
+          f"stored_price_entity={saved.get(c.CONF_PRICE_ENTITY)!r}")
+
+
+async def accepted():
+    cf.validate_tibber_token = _accept_token
+    lines, exceptions = [], 0
+    for case, step, stored, submit in ACCEPTED:
+        entry = FakeEntry(data={}, options=dict(stored))
+        flow = _flow(entry)
+        await getattr(flow, f"async_step_{step}")(None)
+        res = await getattr(flow, f"async_step_{step}")(dict(submit))
+        body = json.dumps({"type": res.get("type"), "errors": res.get("errors"),
+                           "options": entry.options}, sort_keys=True, default=repr)
+        sha = hashlib.sha1(body.encode()).hexdigest()[:12]
+        if case == EXCEPTION:
+            exceptions += 1
+            print(f"  A3-exception: {case} {sha} {body}")
+            continue
+        lines.append(f"{case} {sha}")
+        print(f"  {case} {sha} {body}")
+    digest = hashlib.sha1("\n".join(lines).encode()).hexdigest()[:12]
+    print(f"RESULT cases={len(lines)} exceptions={exceptions} digest={digest}")
+
+
+def main():
+    args = set(sys.argv[1:])
+    null = "--null" in args
+    if "--clear-required" in args:
+        asyncio.run(clear_required(null))
+        return
+    if "--accepted" in args:
+        asyncio.run(accepted())
+        return
+    cf.validate_tibber_token = _refuse_token
+    label = "shown_stored" if null else "stale_slots"
+    tot_rows = tot_hits = tot_rej = 0
+    for step in REJECT:
+        n, rej, hits, typ, why = asyncio.run(rerender(step, null))
+        tot_rows += n
+        tot_hits += hits
+        tot_rej += rej
+        print(f"  {step}: stored_rows={n} rejected={int(rej)} {label}={hits} [{typ} {why}]")
+    print(f"RESULT pages={len(REJECT)} rejected={tot_rej} stored_rows={tot_rows} {label}={tot_hits}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/2912.md b/dev/programme/delivery/2912.md
new file mode 100644
index 000000000..d87aaa2ee
--- /dev/null
+++ b/dev/programme/delivery/2912.md
@@ -0,0 +1 @@
+- [#2912](https://github.com/tvofi/heatpump_optimizer/pull/2912) — **open**, fix(config-flow): a refused options submit keeps a cleared stored entity cleared (R10-CONFIGFLOW-PAGES arm A, D7-s2-56)
diff --git a/tests/closures.json b/tests/closures.json
index f591c0251..f73fc650b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3691,6 +3691,7 @@
    "dev/audit/harnesses/r10_cloud_setup_mutants.py",
    "dev/audit/harnesses/r10_cloud_setup_toolchain.py",
    "dev/audit/harnesses/r10_codescan_wait_race.py",
+   "dev/audit/harnesses/r10_configflow_pages.py",
    "dev/audit/harnesses/r10_critpath_archive_parity.py",
    "dev/audit/harnesses/r10_dead_rate_limit.py",
    "dev/audit/harnesses/r10_demand_overbook.py",
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 3dba5f309..084ab1544 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -3348,23 +3348,28 @@ async def residual_statement_branches():
     )
     stored_price = options_over(stored_price_entry, FakeHass())
     await stored_price.async_step_entities(None)
+    # An untouched picker is re-submitted as its suggested value; a cleared
+    # one is absent, and that case is refused
+    # (``options_cleared_price_entity_is_refused``).
     result = await submit(
         stored_price,
         "entities",
         {
             const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
+            const.CONF_PRICE_ENTITY: "sensor.stored_price",
             const.CONF_WEATHER_ENTITY: "weather.home",
         },
     )
     check(
         "opt_entities",
         "happy",
-        "a stored price sensor satisfies the entity source without being re-submitted",
+        "an untouched stored price sensor satisfies the entity source and is kept",
         shows_menu(result, "advanced")
         and not result.get("errors")
-        and stored_price_entry.options.get(const.CONF_PRICE_ENTITY) is None,
+        and stored_price_entry.options.get(const.CONF_PRICE_ENTITY)
+        == "sensor.stored_price",
         f"errors={result.get('errors')} "
-        f"cleared={stored_price_entry.options.get(const.CONF_PRICE_ENTITY)!r}",
+        f"stored={stored_price_entry.options.get(const.CONF_PRICE_ENTITY)!r}",
     )
 
     # The hot_water page's holiday-window validation: the holiday field gets
@@ -7327,6 +7332,249 @@ async def r9_f5_text_and_menu_findings():
     )
 
 
+# ---------------------------------------------------------------------------
+# R10-CONFIGFLOW-PAGES (D7-s2-56, #2238): every validating options page runs
+# ``_page``'s one sequence. A REJECTED submit re-renders over the cleaned
+# submit, so a stored entity the user cleared shows empty -- not the stored
+# entity the user was removing, which the next submit would silently keep.
+# ---------------------------------------------------------------------------
+#: page -> (stored config opening the page's ``when`` gates, the fields that
+#: make the page refuse). No rejection here reaches the network.
+PAGE_REJECTIONS = {
+    "entities": (
+        {const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_TIBBER},
+        {const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_TIBBER},
+    ),
+    "entities_metering": ({}, {const.CONF_FREQ_CONTROL_MODE: FREQ_MODE_CONTROL}),
+    "comfort": ({}, {const.CONF_MIN_TEMP: 25.0, const.CONF_MAX_TEMP: 18.0}),
+    "hot_water": ({const.CONF_DHW_ENABLED: True}, {const.CONF_DHW_WINDOWS: "nonsense"}),
+    "hot_water_tank": ({}, {const.CONF_DHW_DISINFECTION_MODE: FREQ_MODE_CONTROL}),
+    "building": (
+        {const.CONF_WOOD_FURNACE_ENABLED: True},
+        {
+            const.CONF_WOOD_FURNACE_ENABLED: True,
+            const.CONF_MIXING_VALVE_WRITE_TARGET_KIND: "flow",
+        },
+    ),
+    "grid": ({}, {const.CONF_PEAK_TARIFF_MONTHS: "13-14"}),
+    "grid_connection": ({}, {const.CONF_SILENT_MODE_WINDOWS: "nonsense"}),
+    "grid_fees": ({}, {const.CONF_GRID_FEE_RULES: "nonsense"}),
+}
+
+
+def _page_stored_entities(step, base):
+    """The page's ``_STORED`` rows with every ``when`` gate open, each given
+    a distinct stored entity."""
+    rows = [
+        row
+        for row in config_flow._page_rows(
+            step, {**base, const.CONF_WOOD_FURNACE_ENABLED: True}
+        )
+        if row.default is config_flow._STORED
+    ]
+    return {row.key: f"sensor.stored_{i}" for i, row in enumerate(rows)}
+
+
+async def options_rejected_page_rerenders_the_clear():
+    """A rejected page shows a cleared stored entity as cleared (D7-s2-56)."""
+    R.section("options: a rejected page re-renders what was cleared, not what was stored")
+    total_rows = 0
+    for step, (base, bad) in PAGE_REJECTIONS.items():
+        stored = _page_stored_entities(step, base)
+        total_rows += len(stored)
+        flow = options_over(FakeEntry(data={**base, **stored}), FakeHass())
+        result = await submit(flow, step, bad)
+        stale = sorted(k for k in stored if suggested_value(result, k) is not None)
+        check(
+            f"opt_{step}",
+            "error",
+            f"a rejected {step} submit re-renders each cleared stored entity empty",
+            shows(result, step) and bool(result.get("errors")) and not stale,
+            f"errors={result.get('errors')} rows={len(stored)} still_stored={stale}",
+        )
+        # Null control: the same rejection with nothing cleared shows every
+        # stored entity as stored, so the empty fields above are the clear's.
+        flow = options_over(FakeEntry(data={**base, **stored}), FakeHass())
+        result = await submit(flow, step, {**stored, **bad})
+        if result.get("type") == "form" and result.get("errors"):
+            kept = sorted(k for k in stored if suggested_value(result, k) == stored[k])
+            check(
+                f"opt_{step}",
+                "error",
+                f"a rejected {step} submit that cleared nothing re-renders every stored entity",
+                kept == sorted(stored),
+                f"shown_stored={len(kept)}/{len(stored)}",
+            )
+    # The census asserts its own reach: a page whose _STORED rows vanished
+    # would pass the loop above vacuously.
+    check(
+        "opt_entities",
+        "happy",
+        "the rejected-page census reaches every stored entity row of the nine pages",
+        total_rows >= 30,
+        f"stored rows driven={total_rows}",
+    )
+
+    # A2: a rejected page keeps its description placeholders.
+    hass = FakeHass()
+    currency = config_flow.resolve_currency(hass)
+    fee = {"currency": currency, "fee_bound": f"{config_flow.grid_fee.fee_bound(currency):g}"}
+    for step, want in (
+        ("grid", fee),
+        ("grid_fees", fee),
+        ("hot_water", config_flow._WINDOW_PLACEHOLDERS),
+        ("grid_connection", config_flow._WINDOW_PLACEHOLDERS),
+    ):
+        base, bad = PAGE_REJECTIONS[step]
+        flow = options_over(FakeEntry(data=dict(base)), FakeHass())
+        result = await submit(flow, step, bad)
+        check(
+            f"opt_{step}",
+            "error",
+            f"a rejected {step} form keeps its description placeholders",
+            shows(result, step)
+            and bool(result.get("errors"))
+            and dict(result.get("description_placeholders") or {}) == dict(want),
+            f"placeholders={result.get('description_placeholders')}",
+        )
+
+    # The clear is judged over the submit merged onto the stored config:
+    # turning the wood block off hides its rows, so their absent entities are
+    # kept, not nulled -- the save stores the switch, not a wipe of the block.
+    wood = {
+        const.CONF_WOOD_FURNACE_ENABLED: True,
+        const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
+        const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wood_bottom",
+    }
+    entry = FakeEntry(data=dict(wood))
+    flow = options_over(entry, FakeHass())
+    await flow.async_step_building(None)
+    result = await submit(flow, "building", {const.CONF_WOOD_FURNACE_ENABLED: False})
+    check(
+        "opt_building",
+        "happy",
+        "turning the wood block off keeps its hidden entities instead of nulling them",
+        shows(result, "building") is False
+        and result.get("type") == "menu"
+        and entry.options.get(const.CONF_WOOD_FURNACE_ENABLED) is False
+        and const.CONF_WOOD_TANK_TOP_ENTITY not in entry.options
+        and const.CONF_WOOD_TANK_BOTTOM_ENTITY not in entry.options,
+        f"type={result.get('type')} options={entry.options}",
+    )
+
+    # grid_connection: a cleared silent-mode window is absent from the
+    # submit and saves as "" (no window), never the stored window. The page
+    # writes that default before ``_page`` lifts any section, so the check
+    # asserts the precondition it relies on: no grid_connection row is grouped.
+    grouped = [
+        row.key
+        for row in config_flow._OPTION_FIELDS
+        if row.step == "grid_connection" and row.group
+    ]
+    entry = FakeEntry(data={const.CONF_SILENT_MODE_WINDOWS: "22:00-06:00"})
+    flow = options_over(entry, FakeHass())
+    await flow.async_step_grid_connection(None)
+    result = await submit(flow, "grid_connection", {const.CONF_MAIN_FUSE_A: 25})
+    check(
+        "opt_grid_connection",
+        "happy",
+        "a cleared silent-mode window saves as no window, on an ungrouped page",
+        not grouped
+        and shows_menu(result, "advanced")
+        and entry.options.get(const.CONF_SILENT_MODE_WINDOWS) == "",
+        f"grouped={grouped} type={result.get('type')} "
+        f"stored={entry.options.get(const.CONF_SILENT_MODE_WINDOWS)!r}",
+    )
+
+
+async def options_cleared_price_entity_is_refused():
+    """A3': clearing the price entity under an entity source is refused.
+
+    The entities page judged ``price_entity_required`` over the submit OR the
+    stored entity, while ``_clear_absent`` nulled the cleared one: the check
+    passed on the entity being removed, and the page saved an entity price
+    source with no price sensor. It now judges what would be stored.
+    """
+    R.section("options: a cleared price entity under an entity source is refused")
+    stored = {
+        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
+        const.CONF_PRICE_ENTITY: "sensor.price",
+    }
+    entry = FakeEntry(data={}, options=dict(stored))
+    result = await submit(
+        options_over(entry, FakeHass()),
+        "entities",
+        {const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY},
+    )
+    check(
+        "opt_entities",
+        "error",
+        "clearing the stored price entity under an entity source is price_entity_required",
+        shows(result, "entities")
+        and result.get("errors") == {const.CONF_PRICE_ENTITY: "price_entity_required"}
+        and entry.options == stored,
+        f"type={result.get('type')} errors={result.get('errors')} "
+        f"stored={entry.options.get(const.CONF_PRICE_ENTITY)!r}",
+    )
+    # Null control: a replacement entity saves, with no error.
+    entry = FakeEntry(data={}, options=dict(stored))
+    flow = options_over(entry, FakeHass())
+    await flow.async_step_entities(None)
+    result = await submit(
+        flow,
+        "entities",
+        {
+            const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
+            const.CONF_PRICE_ENTITY: "sensor.other",
+        },
+    )
+    check(
+        "opt_entities",
+        "happy",
+        "replacing the stored price entity saves the new one",
+        shows_menu(result, "advanced")
+        and not result.get("errors")
+        and entry.options.get(const.CONF_PRICE_ENTITY) == "sensor.other",
+        f"type={result.get('type')} errors={result.get('errors')} "
+        f"stored={entry.options.get(const.CONF_PRICE_ENTITY)!r}",
+    )
+    # Second control: switching to Tibber with a token raises no error and
+    # saves the token; the absent price entity is still nulled, as before.
+    entry = FakeEntry(data={}, options=dict(stored))
+    flow = options_over(entry, FakeHass())
+    await flow.async_step_entities(None)
+    real_validate = config_flow.validate_tibber_token
+
+    async def _accept(_hass, _token):
+        return "ok"
+
+    config_flow.validate_tibber_token = _accept
+    try:
+        result = await submit(
+            flow,
+            "entities",
+            {
+                const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_TIBBER,
+                const.CONF_TIBBER_TOKEN: "t",
+            },
+        )
+    finally:
+        config_flow.validate_tibber_token = real_validate
+    check(
+        "opt_entities",
+        "happy",
+        "switching to Tibber with a token saves it and nulls the cleared price entity",
+        shows_menu(result, "advanced")
+        and not result.get("errors")
+        and entry.options.get(const.CONF_TIBBER_TOKEN) == "t"
+        and const.CONF_PRICE_ENTITY in entry.options
+        and entry.options[const.CONF_PRICE_ENTITY] is None,
+        f"type={result.get('type')} errors={result.get('errors')} "
+        f"token={entry.options.get(const.CONF_TIBBER_TOKEN)!r} "
+        f"price_entity={entry.options.get(const.CONF_PRICE_ENTITY, 'ABSENT')!r}",
+    )
+
+
 async def main() -> int:
     if "--self-check" in sys.argv:
         return await self_check()
@@ -7372,6 +7620,8 @@ async def main() -> int:
     await config_flow_device_prefill_offer()
     await device_prefill_preview_texts()
     await r9_f5_text_and_menu_findings()
+    await options_rejected_page_rerenders_the_clear()
+    await options_cleared_price_entity_is_refused()
 
     print()
     LEDGER.print_result_lines()
diff --git a/tests/entities.py b/tests/entities.py
index 5562214e6..d415376ed 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -3837,7 +3837,7 @@ def _p2_registry(sources):
              dispositions={
                  "coordinator.py::HeatPumpOptimizerCoordinator._external_heat_config":
                      "guarded: ANDed with wood_furnace_on",
-                 "config_flow.py::HeatPumpOptimizerOptionsFlow.async_step_building":
+                 "config_flow.py::HeatPumpOptimizerOptionsFlow._building_wood_flag":
                      "guarded: normalises the flag after wood_furnace_on(merged)",
                  "thermal_model.py::ThermalParameters.from_config":
                      "guarded: under _on = wood_furnace_on(config)",
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json
new file mode 100644
index 000000000..94809b4e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._building_wood_flag.RETURN_DEL.f37fd05d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._building_wood_flag RETURN_DEL f37fd05d",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..002bda4ed
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._disinfection_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._disinfection_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json
new file mode 100644
index 000000000..d249adab3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.BOOLOP.0b8e0158.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors BOOLOP 0b8e0158",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submitted and submitted != current.get(CONF_TIBBER_TOKEN):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if submitted or submitted != current.get(CONF_TIBBER_TOKEN):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json
new file mode 100644
index 000000000..b94b2a9aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.0b8e0158.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 0b8e0158",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submitted and submitted != current.get(CONF_TIBBER_TOKEN):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json
new file mode 100644
index 000000000..e92f41977
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.2a9c0142.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 2a9c0142",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if verdict == \"invalid_auth\":",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF c680d852` (the guard moved into `HeatPumpOptimizerOptionsFlow._entities_errors`). Previous: Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json
new file mode 100644
index 000000000..31e23f5fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.30631ec6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 30631ec6",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if not view.get(CONF_PRICE_ENTITY):",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF b9ebe2fa` (the guard moved into `HeatPumpOptimizerOptionsFlow._entities_errors`). Previous: Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json
new file mode 100644
index 000000000..74eb45e98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.83cb93cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF 83cb93cb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if source == PRICE_SOURCE_ENTITY:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json
new file mode 100644
index 000000000..bce266f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.b4c07480.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF b4c07480",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            elif verdict != \"ok\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json
new file mode 100644
index 000000000..37339431d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.GUARD_OFF.c7990b6d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors GUARD_OFF c7990b6d",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not (submit.get(CONF_TIBBER_TOKEN) or current.get(CONF_TIBBER_TOKEN)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json
new file mode 100644
index 000000000..20e795a55
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.421708f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors RETURN_DEL 421708f2",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..a2154851e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._entities_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json
new file mode 100644
index 000000000..713819368
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.GUARD_OFF.ea8cc91b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._grid_fee_errors GUARD_OFF ea8cc91b",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if fee_problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..81cbba591
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._grid_fee_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._grid_fee_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json
new file mode 100644
index 000000000..729871f08
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.BOOLOP.47acdc72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors BOOLOP 47acdc72",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not errors and _dhw_min_too_close(submit, current):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not errors or _dhw_min_too_close(submit, current):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json
new file mode 100644
index 000000000..6e44953f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.03e357ee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 03e357ee",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if window_problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json
new file mode 100644
index 000000000..74a645116
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.355fc9b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 355fc9b4",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if holiday_spec:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 02e99d97` (the guard moved into `HeatPumpOptimizerOptionsFlow._hot_water_errors`). Previous: Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json
new file mode 100644
index 000000000..77c40dfe0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.47acdc72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 47acdc72",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not errors and _dhw_min_too_close(submit, current):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json
new file mode 100644
index 000000000..3c21a0833
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.GUARD_OFF.8cd5759a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors GUARD_OFF 8cd5759a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if holiday_problem is not None:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 07c72f5d` (the guard moved into `HeatPumpOptimizerOptionsFlow._hot_water_errors`). Previous: Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..a44f5fbd6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._hot_water_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._hot_water_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json
new file mode 100644
index 000000000..2af5344d6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.BOOLOP.bdb67645.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors BOOLOP bdb67645",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL or not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json
new file mode 100644
index 000000000..d28394727
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.GUARD_OFF.bdb67645.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors GUARD_OFF bdb67645",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not submit.get(CONF_COMPRESSOR_FREQ_ENTITY):",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities_metering GUARD_OFF c8d82db8` (the guard moved into `HeatPumpOptimizerOptionsFlow._metering_errors`). Previous: Recorded by `mutation_table.py --drain` against c3530277373ddf87652858f9ecb0ee1cf36f4347: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..409ba2c17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._metering_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._metering_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json
new file mode 100644
index 000000000..8a80b5923
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.45af9d64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._page GUARD_OFF 45af9d64",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if check is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=39."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json
new file mode 100644
index 000000000..429055959
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._page.GUARD_OFF.980b44df.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._page GUARD_OFF 980b44df",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if not errors:",
+  "reason": "Re-keyed by R10-CONFIGFLOW-PAGES arm A from `HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF 980b44df` (the guard moved into `HeatPumpOptimizerOptionsFlow._page`). Previous: Recorded by `mutation_table.py --drain` against 3976515a08228598ea3863f4f36dc4c7c4846865: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json
new file mode 100644
index 000000000..1ff31b621
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.67752ca1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors GUARD_OFF 67752ca1",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not _valid_months_spec(submit.get(CONF_PEAK_TARIFF_MONTHS, \"\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json
new file mode 100644
index 000000000..773da22f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.GUARD_OFF.821aac0b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors GUARD_OFF 821aac0b",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not is_valid_spec(submit.get(CONF_PEAK_TARIFF_HOURS, \"\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..bd699c6c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._peak_tariff_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._peak_tariff_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..3035848a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._plumbing_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._plumbing_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json
new file mode 100644
index 000000000..81c95f777
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.GUARD_OFF.093742d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._silent_window_errors GUARD_OFF 093742d2",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json
new file mode 100644
index 000000000..b90654ac3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._silent_window_errors.RETURN_DEL.eef27ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._silent_window_errors RETURN_DEL eef27ceb",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return errors",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json
deleted file mode 100644
index d9d261a87..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.GUARD_OFF.b75e92ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_comfort GUARD_OFF b75e92ec",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if user_input is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json
new file mode 100644
index 000000000..d6b058854
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_comfort.RETURN_DEL.a5ae6e26.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_comfort RETURN_DEL a5ae6e26",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return await self._page(\"comfort\", user_input, clear=True, check=self._comfort_errors)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json
deleted file mode 100644
index 0285b7415..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.980b44df.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF 980b44df",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if not errors:",
-  "reason": "Recorded by `mutation_table.py --drain` against 3976515a08228598ea3863f4f36dc4c7c4846865: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=30."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json
deleted file mode 100644
index d3a67260c..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.b9ebe2fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF b9ebe2fa",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                if not entity:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json
deleted file mode 100644
index 5b3cd5a3f..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities.GUARD_OFF.c680d852.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities GUARD_OFF c680d852",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                        if verdict == \"invalid_auth\":",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json
deleted file mode 100644
index 0e3fbbea6..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_entities_metering.GUARD_OFF.c8d82db8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_entities_metering GUARD_OFF c8d82db8",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if user_input.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL and not user_input.get(CONF_COMPRESSOR_FREQ_ENTITY):",
-  "reason": "Recorded by `mutation_table.py --drain` against c3530277373ddf87652858f9ecb0ee1cf36f4347: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json
deleted file mode 100644
index 31ab43fca..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.02e99d97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 02e99d97",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "            if holiday_spec:",
-  "reason": "Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json
deleted file mode 100644
index 630f10fc2..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water.GUARD_OFF.07c72f5d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water GUARD_OFF 07c72f5d",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "                if holiday_problem is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json
deleted file mode 100644
index a4b037dd4..000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank.GUARD_OFF.b75e92ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_hot_water_tank GUARD_OFF b75e92ec",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if user_input is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against 15f0b5924f3c2a75befe984d156cb3e602effd2e: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=10."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json
new file mode 100644
index 000000000..6a7ab27f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.GUARD_OFF.607abe98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_apply_dso_catalog GUARD_OFF 607abe98",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if applied:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json
new file mode 100644
index 000000000..d21895ba8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_apply_dso_catalog.RETURN_DEL.0ff10d02.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_apply_dso_catalog RETURN_DEL 0ff10d02",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json b/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json
new file mode 100644
index 000000000..fb4cd34aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fee_placeholders.RETURN_DEL.aa4e4753.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fee_placeholders RETURN_DEL aa4e4753",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {\"currency\": currency, \"fee_bound\": f\"{grid_fee.fee_bound(currency):g}\"}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json
new file mode 100644
index 000000000..b1fcd2416
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.GUARD_OFF.ab2bb6c0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_peak_window_as_int GUARD_OFF ab2bb6c0",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if window is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json
new file mode 100644
index 000000000..6bb9e21ca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_peak_window_as_int.RETURN_DEL.0ff10d02.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_peak_window_as_int RETURN_DEL 0ff10d02",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return cleaned",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json
new file mode 100644
index 000000000..9c6f7c7e2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.GUARD_OFF.04d1f31e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_warn_legionella_ceiling GUARD_OFF 04d1f31e",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if warning is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json
new file mode 100644
index 000000000..16b920934
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_warn_legionella_ceiling.RETURN_DEL.455596d0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_warn_legionella_ceiling RETURN_DEL 455596d0",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return submit",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 24fe45038..0b90cfc0a 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 18038,
+ "class_excess_loc": 17992,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -16,6 +16,6 @@
  "methods_over_150": 16,
  "methods_over_200": 9,
  "name_kept_members": 38,
- "recorded_at": "6eb552157b63d1e98a9653250789d9fe0027b5bc",
+ "recorded_at": "6d86acc909f7fc465e5736771daf8fa45c1373a4",
  "seam_cut_total": 423
 }

