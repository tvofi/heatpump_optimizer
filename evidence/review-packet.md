# Review packet #3562
head: ece8328001608ff93f5138392f6e6c15420c8929
base: 513a07dfdc0daf09a054826974dbb64bfea9de27

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=132419175367 queued
arm id=132418354871 skipped
budget-raise-gate / budget-raise-gate id=132419175406 queued
cancel-superseded id=132418332066 success
codeql / Analyze (actions) id=132419175282 queued
codeql / Analyze (javascript-typescript) id=132419175299 queued
codeql / Analyze (python) id=132419175287 queued
governance / delivery-status id=132419175415 queued
governance / delivery-status-publish id=132419176751 skipped
governance / env-matrix id=132419175380 queued
governance / instrument-self-tests id=132419175354 queued
governance / policy-docs id=132419175351 queued
governance / record id=132419176507 skipped
governance / wave-script id=132419175374 queued
hassfest / hassfest id=132419175319 success
kernel-points id=132419175852 skipped
prelude id=132418332093 success
refresh id=132418331880 success
tests / briefs id=132419175339 queued
tests / closure-scope id=132419175370 queued
tests / mutation id=132419175458 queued
tests / nightly-status id=132419175428 queued
validate / validate-hacs id=132419175280 queued

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132419175354: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 4fe395ee: dismissed:owner ruling 2026-11-13, I need no further boost temperature trim
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
similarity index 60%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
index 3c3cb57df3..7674632b2b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 59013da4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 87a4cba9",
   "killed_by": "tests/features.py",
-  "old": "        if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if held.written or held.retry or held.space_before is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
new file mode 100644
index 0000000000..d52a0f3f66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space GUARD_OFF bc2b348d",
+  "killed_by": "tests/features.py",
+  "old": "    if own:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
index f29be90584..eedc551b94 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL cbe69d47",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL ee5d5b70",
   "killed_by": "tests/features.py",
-  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
new file mode 100644
index 0000000000..a7763a6b16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c BOOLOP e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limit is not None or limit > _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
new file mode 100644
index 0000000000..3aeba63c75
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if limit is not None and limit >= _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json
new file mode 100644
index 0000000000..ec2e05c85a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF 0cd5c442",
+  "killed_by": "tests/features.py",
+  "old": "    if (ceiling := _heat_ceiling_c(inp.config)) != DEFAULT_FLOW_HEAT_C:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json
new file mode 100644
index 0000000000..3070a5af12
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF c89e426b",
+  "killed_by": "tests/features.py",
+  "old": "    if high is None or not _gate_floor_c(inp.config) < high <= FLOW_HEAT_C_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
new file mode 100644
index 0000000000..7127158872
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json
new file mode 100644
index 0000000000..fc06916701
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c RETURN_DEL 2985261d",
+  "killed_by": "tests/features.py",
+  "old": "    return min(caps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
index d5ce21b72b..6150d6a294 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP 605f504a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP dd8cf122",
   "killed_by": "tests/guard_pins.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity, now)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
index 9a74fc5f22..febd8f790b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL 605f504a",
-  "killed_by": "tests/structure.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL dd8cf122",
+  "killed_by": "tests/features.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json
new file mode 100644
index 0000000000..4538077c43
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw GUARD_OFF b06f8296",
+  "killed_by": "tests/features.py",
+  "old": "    if boosted:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json
new file mode 100644
index 0000000000..3b8a2da6c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw GUARD_OFF eee8dcd8",
+  "killed_by": "tests/features.py",
+  "old": "    if (kw := _experiment_kw(inp)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json
new file mode 100644
index 0000000000..b6e67a4cb0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw RETURN_DEL 1e8ade07",
+  "killed_by": "tests/features.py",
+  "old": "    return _step_kw(inp.plan, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
new file mode 100644
index 0000000000..1ef3907eac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_own_space_write RETURN_DEL 98fa5cc9",
+  "killed_by": "tests/features.py",
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json
deleted file mode 100644
index 2aa98ee949..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_space_target RETURN_DEL 268586e3",
-  "killed_by": "tests/structure.py",
-  "old": "        return _flow_target(inp, duty, now)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against e5f7e169d64b93d4ae117eb07c68ecef6d47aea6: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json
new file mode 100644
index 0000000000..0ad0ed51fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_space_target RETURN_DEL 628d75e4",
+  "killed_by": "tests/features.py",
+  "old": "        return _flow_target(inp, duty, now, boosted=boosted)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
index b541e26d05..3a07eb6ceb 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:desired GUARD_OFF 0082e8a4",
   "killed_by": "tests/features.py",
   "old": "    if _flow_unit(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cbb8a2712fef67b4719309fa01396706e66148bc: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Re-measured on a git-archive export of 13a82a9d, 2026-10-05: 3 of 3698 feature checks fail, against the export baseline's two artefacts (#363 recorded_at, R9-F2.1 P3). Re-keyed by R9-EG-B6 (#1739): the collaborator-interface rename made the line `    if _flow_unit(coord._config):` into `    if _flow_unit(inp.config):`."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
 }
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json
new file mode 100644
index 0000000000..4aa62e7c56
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND c89e426b",
+  "old": "    if high is None or not _gate_floor_c(inp.config) < high <= FLOW_HEAT_C_MAX:",
+  "reason": "Equivalent (CMP_BOUND on the first comparator, `_gate_floor_c(...) < high` -> `<=`): the two arms differ only at an entity maximum exactly equal to the gate, where the boost either writes min(high, ...) = the gate or keeps the planned level; the entity's own range (`_bounded`) clamps every heating write on that entity to its maximum, the gate, so both arms write the same value on every input. Measured by the R10-HOTFIX-BOOST-FLOW-CEILING repair seat's `mutation_table.py --pin-killed --base origin/main` (tests/features.py, tests/config_flow_steps.py, tests/guard_pins.py): the site lived while the anchor's other comparator (`<= FLOW_HEAT_C_MAX` -> `<`) is killed by the arbiter block's `max 70, the bound` row, and the same line's GUARD_OFF is pinned (killed by tests/features.py).",
+  "verdict": "equivalent"
+}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head ced9b233580709f530d5dc402dc12344697fef87, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index 3bb0dfe9d3..2536024d45 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -127,6 +127,8 @@ Built from outside pull request #3439 by Bankaifan, with thanks. With Pump duty
 
 Turning the optimizer off, and every unload, now writes the space set-point that Pump duty control had changed back to the person's own baseline. The baseline is saved before the first write, a value the person sets between writes becomes the new baseline, and the restored value is kept within the entity's range and step. This replaces the earlier behaviour where off wrote nothing for that set-point. `docs/configuration.md` describes it under Pump duty control.
 
+Upgrade note, added 2026-11-13: after an upgrade from v7.1.11 or earlier, the space set-point is not written until it has been set once at the pump or in Home Assistant. Under Pump duty control this can leave the pump at its last idle set-point (25 °C on a flow set-point), boost included. Until the release that follows v7.1.15, set the set-point entity once by hand to release it; from that release the optimizer releases it on its own.
+
 ### #3469 Optional controller limits bound the water set-point (R10-WATER-SETPOINT-FEEDBACK, part 3)
 
 Two new optional entity options on the options page that carries the space set-point unit, shown for a water unit, name the controller's own lower and upper limit sensors for the written set-point. An upper limit that leaves no room above the off value for a heating write is ignored, so a placeholder or misplaced sensor can no longer make the loop write the off value or lower. The options have labels in every translation and in the card.
diff --git a/custom_components/heatpump_optimizer/away.py b/custom_components/heatpump_optimizer/away.py
index 9fad06b00d..375ced98bb 100644
--- a/custom_components/heatpump_optimizer/away.py
+++ b/custom_components/heatpump_optimizer/away.py
@@ -1,8 +1,8 @@
 """Away / holiday mode with deadline-driven recovery.
 
 A week away is the single largest saving a heating system can offer: a deep
-setback plus hot water suppressed entirely, except for a legionella cycle timed
-to complete before return.
+setback plus hot water held only at its away minimum; the legionella cycle
+keeps its usual interval.
 
 What makes this more than an ``input_number`` is the **return time**. Knowing
 when the house must be comfortable again lets the optimizer buy the recovery
@@ -73,11 +73,6 @@ class AwayConfig:
     #: Setback targets while away.
     away_temperature: float = 16.0
     away_dhw_min_temperature: float = 20.0
-    #: Whether to keep the anti-legionella cycle running while away. Kept on by
-    #: default: a tank sitting lukewarm for a week is exactly the condition the
-    #: cycle exists for, and it is much cheaper to run it in a chosen cheap
-    #: hour than to arrive home to an overdue one.
-    legionella_before_return: bool = True
 
 
 @dataclass
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index c7afb1923a..7f4c4e5d4e 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -213,6 +213,7 @@ from .const import (
     SPACE_SETPOINT_WATER_UNITS,
     CONF_FLOW_HEAT_C,
     DEFAULT_FLOW_HEAT_C,
+    FLOW_HEAT_C_MAX,
     CONF_FLOW_MIN_LIFT_K,
     CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY,
     CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
@@ -1698,7 +1699,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities", CONF_FLOW_MIN_LIFT_K, DEFAULT_FLOW_MIN_LIFT_K, _number(0.5, 15, 0.5, 'K'), when=_water_space_setpoint, group="indoor"),
     # The ceiling's minimum sits above pump_arbiter.FLOW_GATE_C (25 °C): a
     # ceiling at the gate would write "off" on every heating step.
-    _F("entities", CONF_FLOW_HEAT_C, DEFAULT_FLOW_HEAT_C, _number(30, 70, 0.5, '°C'), when=_water_space_setpoint, group="indoor"),
+    _F("entities", CONF_FLOW_HEAT_C, DEFAULT_FLOW_HEAT_C, _number(30, FLOW_HEAT_C_MAX, 0.5, '°C'), when=_water_space_setpoint, group="indoor"),
     # Closing that flow on the measured draw (R10-WATER-SETPOINT-FEEDBACK):
     # on by default, and it acts only where a power meter is configured too.
     _F("entities", CONF_SPACE_SETPOINT_POWER_FEEDBACK, DEFAULT_SPACE_SETPOINT_POWER_FEEDBACK, selector.BooleanSelector(), when=_water_space_setpoint, group="indoor"),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 24f7060188..b7e63ff723 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -823,6 +823,11 @@ SPACE_SETPOINT_WATER_UNITS: Final = ("flow", "return")
 #: :data:`pump_arbiter.FLOW_HEAT_C`.
 CONF_FLOW_HEAT_C: Final = "flow_heat_c"
 DEFAULT_FLOW_HEAT_C: Final = 55.0
+#: The highest heating-flow ceiling the options flow offers, °C, and the
+#: highest set-point-entity maximum a boost writes (``pump_arbiter.
+#: _boost_ceiling_c``): above it the entity is no heating-flow set-point
+#: (a generic number helper reads 100), so a boost keeps the planned level.
+FLOW_HEAT_C_MAX: Final = 70.0
 #: The flow set-point's lift over the measured inlet water at the modulation
 #: floor, K. Absent keeps :data:`thermal_model.FLOW_MIN_LIFT_K`. A controller
 #: that takes the set-point as its return-water target modulates on the gap
diff --git a/custom_components/heatpump_optimizer/off_restore.py b/custom_components/heatpump_optimizer/off_restore.py
index 6df838c235..be47b192b7 100644
--- a/custom_components/heatpump_optimizer/off_restore.py
+++ b/custom_components/heatpump_optimizer/off_restore.py
@@ -153,12 +153,16 @@ async def _save(held: _Held) -> None:
         _LOGGER.debug("Could not save the off-restore store: %s", err)
 
 
-async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str) -> bool:
+async def async_arm(
+    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str,
+    *, baseline_c: float | None = None,
+) -> bool:
     """Before a write by consumer ``key``: arm its restore; False refuses the write.
 
     The first arm captures the baseline of a consumer with no ``neutral`` and
-    persists it with its entity; a later arm, in this run or after a restart,
-    keeps it. An unreadable baseline refuses the write: what it would restore
+    persists it with its entity: ``baseline_c`` where the consumer knows the
+    reading is no baseline (its own last write), else the reading. A later
+    arm, in this run or after a restart, keeps it. An unreadable baseline refuses the write: what it would restore
     is unknown. A baseline entry for another entity, or under a neutral
     restorer, is restored first (rule R), and a failure refuses the write; a
     neutral entry under a baseline restorer is dropped unwritten, so a neutral
@@ -181,7 +185,8 @@ async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, co
             return False  # latched, still armed: nothing to save
     baseline = None
     if restorer.neutral is None:
-        baseline = restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None
+        baseline = baseline_c if baseline_c is not None else (
+            restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None)
         if log_held(entry, f"off_restore_baseline_{key}", baseline is None,
                     "No baseline readable from %s: not written, nothing to restore it to",
                     restorer.entity_id):
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index e3afe6c67d..f3cd3aa0a4 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -115,7 +115,8 @@ write the arbiter arms :mod:`off_restore` (:data:`CONSUMER`), which captures
 the entity's reading, persisted, as the person's baseline and writes it back
 on the change into Off and on every unload, a reload and a Home Assistant
 stop included (the hook's one rule). A reading equal to the arbiter's own
-last write is never captured (:func:`_arm_space`). What a person sets while
+last write is never captured: the baseline row's own target is, and the write
+is sent (:func:`_arm_space`). What a person sets while
 the optimizer is off is captured at the next arm; one set between writes is
 adopted as the baseline (:func:`_edited`), bounded to the entity's own
 range, and, while active, still written over. The mode, the hot-water set-point and the silent switch are not
@@ -176,7 +177,9 @@ from .const import (
     CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
     CONF_SPACE_SETPOINT_POWER_FEEDBACK,
     CONF_VALVE_OUTLET_TEMP_ENTITY,
+    DEFAULT_FLOW_HEAT_C,
     DOMAIN,
+    FLOW_HEAT_C_MAX,
     MODE_AUTO,
     MODE_BOOST,
     MODE_ECONOMY,
@@ -615,13 +618,16 @@ def _planned_room(
 
 
 def _space_target(
-    inp: ArbiterInputs, result: Any, now: datetime, duty: str | None
+    inp: ArbiterInputs, result: Any, now: datetime, duty: str | None, *, boosted: bool
 ) -> float | None:
-    """The plan's own space set-point for ``duty``; see :func:`_flow_target`."""
+    """The plan's own space set-point for ``duty``; see :func:`_flow_target`.
+
+    ``boosted``: a space boost or the global boost mode is live (:func:`_level_kw`).
+    """
     entity = _entities(inp.config)["space_setpoint"]
     if _flow_unit(inp.config):
         log_held(inp.hass, f"space_target_flow_declared:{entity}", False)
-        return _flow_target(inp, duty, now)
+        return _flow_target(inp, duty, now, boosted=boosted)
     room = _planned_room(result, now)
     low = setpoint_range_c(inp.hass, entity)[0]
     # An "indoor" entity that cannot hold the room target is a flow
@@ -647,6 +653,25 @@ def _step_kw(result: Any, now: datetime) -> float | None:
     return finite_float(_planned_room(result, now, "power_schedule"))
 
 
+def _level_kw(inp: ArbiterInputs, now: datetime, boosted: bool) -> float | None:
+    """The space level a heating step's flow set-point maps (:func:`_flow_target`), kW.
+
+    The experiment's commanded power where the action is the experiment's
+    (:func:`_experiment_kw`). Under a live space boost or the global boost
+    mode with a ceiling to write (``boosted``, :func:`_boost_ceiling_c`), the
+    band's top: a boost replaces the plan's power for the space channel with
+    the maximum (``boost.overlay``), so the plan's own partial level for the
+    step is not the one served, and mapped it wrote a set-point between the
+    floor and the ceiling (tvofi, 2026-11-13: 41, then 43, during a boost;
+    R10-HOTFIX-BOOST-FLOW-CEILING). Else the plan step's.
+    """
+    if (kw := _experiment_kw(inp)) is not None:
+        return kw
+    if boosted:
+        return finite_float(_band_kw(inp)[1])
+    return _step_kw(inp.plan, now)
+
+
 def _experiment_kw(inp: ArbiterInputs) -> float | None:
     """The system-identification experiment's commanded space power, or
     ``None`` when the action is not the experiment's.
@@ -861,7 +886,38 @@ def _or_hold(floor_c: float | None, config: Any) -> float:
     return _as_target(config, FLOW_HOLD_C) if floor_c is None else floor_c
 
 
-def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float | None:
+def _boost_ceiling_c(inp: ArbiterInputs) -> float | None:
+    """The space water set-point a live boost writes, °C in the entity's own terms, or ``None``.
+
+    The set-point entity's own maximum (tvofi, 2026-11-13: "set at the
+    maximum value"), capped by a heating ceiling (``flow_heat_c``) set to
+    anything but its default, and by the controller's upper-limit sensor
+    where it reads (:func:`_setpoint_limits_c`). The default caps nothing: an
+    absent key reads as it, and an untouched options page must change
+    nothing (``tests/config_flow_steps.py``), so a stored default cannot be
+    told from no setting.
+    The maximum and the cap are both in the entity's own terms, so a return
+    target is not moved. ``None``, and the boost follows the planned level as
+    before, where the maximum does not read, sits at or below the gate, or
+    sits above :data:`~.const.FLOW_HEAT_C_MAX`, the highest ceiling the options
+    offer: such an entity is no heating-flow set-point to drive to its top.
+    """
+    entity = _entities(inp.config)["space_setpoint"]
+    high = setpoint_range_c(inp.hass, entity)[1] if entity else None
+    if high is None or not _gate_floor_c(inp.config) < high <= FLOW_HEAT_C_MAX:
+        return None
+    caps = [high]
+    if (ceiling := _heat_ceiling_c(inp.config)) != DEFAULT_FLOW_HEAT_C:
+        caps.append(ceiling)
+    limit = _setpoint_limits_c(inp)[1]
+    if limit is not None and limit > _gate_floor_c(inp.config):
+        caps.append(limit)
+    return min(caps)
+
+
+def _flow_target(
+    inp: ArbiterInputs, duty: str | None, now: datetime, *, boosted: bool = False,
+) -> float | None:
     """A flow set-point per duty: heat, gate, or the fallback's hold.
 
     The model's weather curve is a pricing curve, not a set-point: it sizes
@@ -873,7 +929,10 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
     (``thermal_model.start_flow_min_lift_k``: ``flow_min_lift_k``, never
     below the pump's own heating start hysteresis where one is read) at the
     modulation floor, so the pump's own water thermostat can realize a
-    lower level.
+    lower level. Under a boost (``boosted``) with a ceiling to write
+    (:func:`_boost_ceiling_c`), the level is the band top and the ceiling
+    that one, so a boost writes it on every step: at the band top the level
+    formula gives the ceiling exactly.
     With no inlet reading the floor is the rated :data:`FLOW_HOLD_C`, in
     return terms on a return target (:func:`_as_target`), as is the
     fallback's hold below. A
@@ -885,7 +944,8 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
     """
     if duty in ("space", "both"):
         p_min, p_max = _band_kw(inp)
-        heat_c = _heat_ceiling_c(inp.config)
+        boost_c = _boost_ceiling_c(inp) if boosted else None
+        heat_c = _heat_ceiling_c(inp.config) if boost_c is None else boost_c
         floor_c = _or_hold(modulation_floor_flow_c(
             _flow_inlet_c(inp), _gate_c(inp),
             start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
@@ -893,10 +953,7 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
         return _bounded(
             inp,
             "space_setpoint",
-            flow_setpoint_for_level(
-                _step_kw(inp.plan, now) if (kw := _experiment_kw(inp)) is None else kw,
-                p_min, p_max, heat_c, floor_c,
-            ),
+            flow_setpoint_for_level(_level_kw(inp, now, boost_c is not None), p_min, p_max, heat_c, floor_c),
             _gate_floor_c(inp.config),
             lo=min(floor_c, heat_c),
             hi=heat_c,
@@ -1055,7 +1112,7 @@ def _note_sent(held: ArbiterState, rec: FeedbackRun, out: float | None, base: fl
     moves at all drops the record, and an equal one is still not sent. The
     dropped record is the run's ``prev_c``, the bracket :func:`_cut_of`
     reads, and ``held.dropped`` until a restore ends it: it is still the
-    arbiter's last write, which the off restore's own-write refusal reads
+    arbiter's last write, which the off restore's own-write check reads
     (:func:`_arm_space`) after the run that dropped it has ended.
     """
     recorded = held.written.get("space_setpoint")
@@ -1209,7 +1266,10 @@ def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) ->
     silent = _silent_target(coord, inp, now)
     duty = _disinfecting(inp, duty)
     mode = _mode_for(inp, duty)
-    space = _space_target(inp, result, now, duty)
+    # The boost fact is read for a water set-point only: an indoor one maps no
+    # level, and a caller may hand no coordinator for it.
+    space = _space_target(inp, result, now, duty, boosted=_flow_unit(inp.config) and (
+        inp.mode == MODE_BOOST or boost.held_for(coord).active(boost.CHANNEL_SPACE, now)))
     if _flow_unit(inp.config):
         space = _feedback(state_for(coord), inp, now, space, _feedback_on(inp, duty, now, boost.held_for(coord)))
     if duty == "space" and mode != pump_mode.MODE_HEAT:
@@ -1460,7 +1520,24 @@ def _not_held(coord: Any, held: ArbiterState, slot: str, detail: str, now: datet
 
 
 def _forget(held: ArbiterState) -> None:
-    held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None
+    """Let go of the pump: every record goes but the arbiter's own last space write.
+
+    That value stays on ``held.dropped`` until a restore replaces it on the
+    entity (:func:`_space_restored`): with no baseline armed, Off writes
+    nothing there, so the entity still reads the optimizer's number, and the
+    arm after On must not capture it as the person's (:func:`_arm_space`).
+    """
+    own = _own_space_write(held)
+    held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None
+    held.dropped = {} if own is None else {"space_setpoint": own}
+
+
+def _own_space_write(held: ArbiterState) -> Any:
+    """The arbiter's own last space write, or ``None``: its record, else the
+    one a loop move dropped to be sent (:func:`_note_sent`), which
+    ``held.dropped`` keeps across the run's end and an Off (:func:`_forget`)."""
+    record = held.written.get("space_setpoint")
+    return record[0] if record is not None else held.dropped.get("space_setpoint")
 
 
 def _service(slot: str, state: Any, value: Any) -> tuple[str, dict[str, Any]] | None:
@@ -1591,33 +1668,34 @@ async def _held_back(
         return True
     if slot == "mode" and entity.split(".", 1)[0] not in _MODE_DOMAINS:
         return True
-    return slot == "space_setpoint" and not await _arm_space(inp, entry, held, entity)
+    return slot == "space_setpoint" and not await _arm_space(inp, entry, held, entity, now)
 
 
-async def _arm_space(inp: ArbiterInputs, entry: Any, held: ArbiterState, entity: str) -> bool:
+async def _arm_space(inp: ArbiterInputs, entry: Any, held: ArbiterState, entity: str, now: datetime) -> bool:
     """Arm the off restore before a space write; False holds the write.
 
     The first arm captures the entity's reading as the baseline off restores
     (:mod:`off_restore`), but never one equal to the arbiter's own last write
     -- a record from before this restore existed: that number is the
-    optimizer's, not the person's, so the write is held, latched, until the
-    controller reads anything else.
+    optimizer's, not the person's. The baseline captured in its place is the
+    baseline row's own space target (:func:`_space_target` with no duty), the
+    value the arbiter holds when the plan is not in charge, and the write is
+    sent. It used to be held until the controller read anything else, which
+    on an upgrade held every space write, a boost's included, with the pump
+    left on the optimizer's last gate (R10-HOTFIX-FLOW-SETPOINT-STUCK).
     """
     armed = await off_restore.async_armed_entry(inp.hass, entry, CONSUMER)
     reading = read_setpoint(inp.hass, entity)
-    record = held.written.get("space_setpoint")
-    # A loop move dropped the record to be sent (_note_sent); held.dropped
-    # keeps it across the run's end, which the loop resets on any stop.
-    last = record[0] if record is not None else held.dropped.get("space_setpoint")
+    last = _own_space_write(held)
     own = (armed is None or armed["entity_id"] != entity) and last is not None \
         and reading is not None and not _differs("space_setpoint", reading, last)
-    if log_held(inp.hass, f"space_baseline_own:{entity}", own,
-                "Pump duty: %s reads %s, the optimizer's own last write, which is no "
-                "baseline to restore on off; not writing it until it is set at the controller",
-                entity, reading):
-        return False
+    baseline = None
+    if own:
+        baseline = _space_target(inp, inp.plan, now, None, boosted=False)
+        _LOGGER.info("Pump duty: %s reads %s, the optimizer's own last write; turning the "
+                     "optimizer off restores %s instead", entity, reading, baseline)
     held.space_before = reading
-    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)
+    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)
 
 
 async def _command(coord: Any, inp: ArbiterInputs, command: PumpCommand, now: datetime) -> None:
@@ -1759,7 +1837,7 @@ async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: s
         # person's the moment the optimizer lets go of it. The space
         # set-point's baseline is restored by off_restore (tvofi, 2026-11-07,
         # "Arbiter too"), before this pass; its record is dropped here.
-        if held.written or held.retry or held.dropped or held.space_before is not None:
+        if held.written or held.retry or held.space_before is not None:
             # A pending retry dies with control, and so does its warning.
             _forget(held)
             issues.clear_issue(coord.hass, ISSUE_IGNORED)
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 5b5bba0267..d44463572a 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "Shown in front of every sensor this integration creates.",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -592,10 +592,10 @@
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
-              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: this integration never recommends a space set-point.",
+              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
-              "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
+              "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
               "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
               "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor lets the forecast correct itself against what the roof actually delivers.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, and is timed to finish before you get back.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater already gets the tank to the anti-legionella temperature and holds it there, count that as a completed cycle instead of running another one.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "Never run anti-legionella cycles closer together than this, even on very cheap days.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the heating target by 1 °C while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index dfba34dc50..4ac3077922 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -12,7 +12,7 @@
           "weather_entity": "Wettervorhersage"
         },
         "data_description": {
-          "name": "Wird jedem Sensor vorangestellt, den diese Integration erstellt.",
+          "name": "Der Titel dieses Eintrags unter Geräte & Dienste. Entitätsnamen verwenden den festen Gerätenamen Heat Pump Optimizer.",
           "price_source": "Tibber verwendet dein API-Token. Entität liest einen Preissensor aus Home Assistant, z. B. Nord Pool.",
           "tibber_token": "Wird verwendet, um deine stündlichen Strompreise abzufragen. Erstelle eines unter developer.tibber.com. Unverändert lassen, solange es sich nicht geändert hat. Nicht erforderlich, wenn die Preisquelle eine Entität ist.",
           "price_entity": "Erforderlich, wenn die Preisquelle eine Entität ist. Typische Attribute sind raw_today und raw_tomorrow.",
@@ -592,10 +592,10 @@
             "data_description": {
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
-              "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Dient nur dazu zu bemerken, wenn die Entität nicht gelesen werden kann. Der Optimierer schreibt nie einen empfohlenen Raumheizungs-Sollwert.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Diese Integration empfiehlt nie einen Raumheizungs-Sollwert.",
+              "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Steht die Steuerung der Pumpenfunktion auf Steuern, schreibt der Optimierer sie in jedem Planschritt, wie die Steuerung der Pumpenfunktion beschreibt, und das Ausschalten von Optimierer aktiv schreibt den Wert zurück, den die Entität vor dem ersten Schreiben zeigte. Bei Aus oder Beobachten wird sie nur gelesen, um zu bemerken, wenn sie nicht gelesen werden kann.",
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor.",
               "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
-              "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel.",
+              "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel. Ein Raumheizungs-Boost oder der Boost-Modus schreibt stattdessen in jedem Schritt das eigene Maximum der Sollwert-Entität (höchstens 70 °C); ein anderer Wert als 55 °C begrenzt auch das, also stelle bei einer Niedertemperatur-Fußbodenheizung einen ein.",
               "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (Luxtronik: 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn eine Luxtronik Smart Home Interface verwirft nach 600 s ohne Zugriff alle gesetzten Werte; und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik verwirft Schreibvorgänge dann stillschweigend).",
               "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
               "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
@@ -1012,7 +1012,7 @@
               "building_preset_enabled": "Thermische Werte aus dem Gebäudetyp ableiten"
             },
             "data_description": {
-              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experte)“ bei jedem Speichern dieser Seite überschrieben."
+              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experten)“ bei jedem Speichern dieser Seite überschrieben."
             }
           },
           "climate": {
@@ -1033,7 +1033,7 @@
         }
       },
       "thermal_model": {
-        "title": "Thermisches Modell (Experte)",
+        "title": "Thermisches Modell (Experten)",
         "description": "Die Rohwerte hinter dem thermischen Modell, die sonst nur bei der Einrichtung abgefragt werden. Ein leer gelassenes Feld behält seinen aktuellen Wert und wird nie gespeichert, ein Haus mit einer Zone bleibt also ein Haus mit einer Zone – und durch Ausfüllen der Felder für zwei Zonen schaltet eine bestehende Installation das Zwei-Zonen-Modell ein.\n\n{preset_warning}",
         "data": {
           "house_thermal_mass": "Thermische Masse des Hauses (kWh/°C)",
@@ -1061,7 +1061,7 @@
         }
       },
       "grid": {
-        "title": "Netz-Spitzentarif",
+        "title": "Lastspitzentarif des Netzes",
         "description": "Kosten, die nicht einfach der Preis pro kWh sind. Viele schwedische Netzbetreiber berechnen zusätzlich eine monatliche Leistungsgebühr auf Basis deiner höchsten Stunden – Warmwasser und Heizung in dieselbe günstige Stunde zu legen kann dann mehr kosten, als es spart.",
         "data": {
           "peak_tariff_enabled": "Meine Netzrechnung enthält eine Leistungsgebühr",
@@ -1089,7 +1089,7 @@
         }
       },
       "solar_pv": {
-        "title": "Solaranlage",
+        "title": "Solarmodule",
         "description": "Wenn du Solarstrom erzeugst, ist es besser, Warmwasser oder den Pufferspeicher mit Überschuss zu beheizen, als ihn zum Vergütungssatz einzuspeisen. Teile dem Optimierer mit, wie deine Anlage aussieht, und er bewertet jede Stunde mit den tatsächlichen Kosten des Verbrauchs.",
         "data": {
           "pv_enabled": "Ich habe eine Solaranlage",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Verwende stattdessen diese, wenn deine Vergütung dem Spotpreis folgt.",
           "pv_enabled": "Lässt den Plan die Wärmepumpe mit deinem eigenen Überschuss betreiben, statt ihn für weniger zu verkaufen, als Netzstrom kostet.",
           "pv_peak_kw": "Die Nennspitzenleistung der Anlage. Dient zur Skalierung der Erzeugungsprognose.",
-          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor lässt die Prognose sich anhand dessen korrigieren, was das Dach tatsächlich liefert.",
+          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor ersetzt den aktuellen Schritt der Prognose durch das, was das Dach gerade liefert, begrenzt auf die installierte Leistung; spätere Schritte bleiben modelliert.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "Eine Person, ein Gerätetracker, ein Kalender oder ein Anwesenheitssensor. Der Schalter auf der Plan-Seite hat Vorrang, bis er ausgeschaltet wird. Eine Person, die „nicht zu Hause“ ist, bedeutet bei ausgeschaltetem Schalter weiterhin Abwesenheit.",
           "holiday_calendar_entity": "Wenn dieser Kalender eingeschaltet ist, ersetzen die Feiertags-Komfort- und Feiertags-Warmwasserfenster für diesen Tag das Paar aus Werktag und Wochenende. Die Abwesenheitsabsenkung hat weiterhin Vorrang, wenn Abwesenheit aktiv ist.",
-          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin und wird so getimt, dass er vor deiner Rückkehr abgeschlossen ist.",
+          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin in seinem üblichen Intervall; er wird nicht auf deine Rückkehr abgestimmt.",
           "away_temperature": "Die Haltetemperatur während der Abwesenheit. Niedrig genug zum Sparen, hoch genug, um das Haus und seine Leitungen zu schützen.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Beobachten liest den Schalter und schreibt ihn nie. Steuern schaltet ihn ein, wenn eine Legionellenschaltung startet, und aus, wenn sie endet, schaltet ihn aber nie ein, solange der Modus der Pumpe kein Warmwasser erzeugt. Es wird nur ein Schalter ausgeschaltet, den die Integration selbst eingeschaltet hat: Ein Schalter, der bei Beginn des Zyklus schon eingeschaltet war, bleibt unberührt. Eine Einschränkung: Wenn du den Schalter von Hand einschaltest, während ein vom Optimierer gestarteter Zyklus läuft, wird er am Ende dieses Zyklus ausgeschaltet, weil sich beides nicht unterscheiden lässt. Steuern benötigt den obigen Schalter.",
               "dhw_disinfection_switch_entity": "Ein Schalter oder Helfer, der das eigene Legionellenprogramm der Wärmepumpe startet. Im Beobachtungsmodus wird sein Zustand nur gelesen und in den Attributen des Warmwasser-Sensors angezeigt; im Steuerungsmodus schaltet die Integration ihn ein, wenn ein Desinfektionszyklus startet, und aus, wenn er endet.",
               "dhw_elastic_legionella_enabled": "Erlaubt der Legionellenschaltung, ein bis zwei Tage früher zu laufen, wenn Strom ungewöhnlich günstig ist, statt immer bis zur Frist zu warten. Die Frist wird weiterhin immer eingehalten.",
-              "dhw_free_disinfection_enabled": "Wenn ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher bereits auf die Legionellentemperatur bringt und dort hält, wird das als abgeschlossener Zyklus gezählt, statt einen weiteren auszuführen.",
+              "dhw_free_disinfection_enabled": "Bringt ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher auf die Legionellentemperatur, wird das in jedem Fall als abgeschlossener Zyklus gezählt. Aus: sofort; ein: erst nachdem der Speicher diese Temperatur 20 Minuten gehalten hat, sodass eine kurze Spitze nichts anrechnet.",
               "dhw_legionella_min_interval_days": "Legionellenschaltungen laufen nie in kürzerem Abstand als diesem, auch nicht an sehr günstigen Tagen.",
               "dhw_quantile_targets_enabled": "Lernt, wie viel Warmwasser jeder Zeitraum an einem Tag mit hohem Verbrauch tatsächlich nutzt, und bereitet den Speicher darauf vor statt auf den Durchschnittstag. Benötigt einen Speichertemperatursensor, konfigurierte Warmwasser-Zeitfenster und einige Wochen an Daten."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt, läuft die Pumpe nur in deinen Warmwasser-Zeitfenstern plus der unten genannten Vorlaufzeit.",
+          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt, läuft die Pumpe nur in deinen Warmwasser-Zeitfenstern plus der unten genannten Vorlaufzeit. Ist Warmwasser aus oder gibt es keine Zeitfenster, bleibt sie an.",
           "vvc_lead_minutes": "Wie lange vor einem Warmwasser-Zeitfenster die Zirkulationspumpe startet, damit die Leitung bei Beginn des Zeitfensters schon heiß ist.",
           "after_save": "Das Speichern wirkt sofort; hier legst du fest, wohin der Dialog als Nächstes führt."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater, der Sicherungswächter und der Sensor für die Reserve inaktiv bleiben – es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
+          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater und der Sicherungswächter inaktiv bleiben und der Sensor für die Reserve allein der Spitze des Lastspitzentarifs folgt, ohne Lastspitzentarif nicht verfügbar – es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
           "main_fuse_phases": "Fast jedes schwedische Haus hat 3 Phasen.",
           "fuse_guard_enabled": "Begrenzt die geplante Leistung der Wärmepumpe auf das, was die Sicherung nach dem restlichen Haus noch übrig lässt. Wenn eine Begrenzung die Komfortuntergrenze unerreichbar machen würde, meldet der Plan das auf seinen Sensoren, statt stillschweigend kalt zu werden.",
           "peak_guard_enabled": "Überwacht den Stromzähler live und hält, wenn für das laufende Messfenster voraussichtlich eine neue abgerechnete Spitze entsteht, elektrisches Warmwasser zurück und senkt die Heizkurve für den Rest dieses Fensters leicht ab. Benötigt einen Stromzähler; ein kalter Speicher oder eine verletzte Komfortuntergrenze haben immer Vorrang vor dem Wächter.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Nach starkem Schneefall weniger Sonne annehmen"
             },
             "data_description": {
-              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option das Heizziel um 1 °C, solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
+              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option die niedrigste Raumtemperatur, die der Plan zulässt, um 1 °C, nie unter 15 °C, solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
               "outage_recovery_enabled": "Nach einem Ausfall läuft alles gleichzeitig wieder an – kaltes Haus, kalter Speicher, die ganze Nachbarschaft – und genau dann entsteht eine neue monatliche Leistungsspitze. Ist dies aktiviert, öffnet eine lange Lücke bei den Aktualisierungen ein zweistündiges Wiederanlauffenster, in dem der Leistungspreis vom ersten kW an ernst genommen wird und Warmwasser 45 Minuten hinter der Raumheizung ansteht, außer der Speicher ist wirklich knapp.",
               "precip_type_enabled": "Regen durchfeuchtet die Gebäudehülle und erhöht den Wärmeverlust; Schnee nicht. Ohne diese Option wird eine Schneeprognose wie Regen behandelt, und der Plan kauft Wärme für eine nasse Wand, die trocken bleibt. Benötigt die Open-Meteo-Verbindung für die Schneedaten.",
               "snow_roof_factor_enabled": "Für zwei Tage nach starkem Schneefall wird der modellierte solare Wärmeeintrag halbiert – Schnee auf Dachfenstern und tiefen Winterscheiben blockiert die Sonne, mit der der Plan gerechnet hat. Bewusst grob: ein Faktor und eine Haltedauer, kein Schmelzmodell."
@@ -1518,7 +1518,7 @@
         }
       },
       "modbus_prefill": {
-        "title": "Aus einem Wärmepumpen-Gerät vorbefüllen",
+        "title": "Aus einem Wärmepumpengerät vorbefüllen",
         "description": "Für eine Rotenso Windmi oder eine andere von GCHV gebaute Wärmepumpe, die über das Modbus-Paket des Projekts tuya_heat_pump ausgelesen wird. Nenne den Entitäts-Präfix des Pakets und sende ab: Das nächste Formular schlägt Werte vor, die aus den eigenen Registern der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
         "data": {
           "prefill_device": "Wärmepumpen-Gerät (optional)",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 5b5bba0267..d44463572a 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "Shown in front of every sensor this integration creates.",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -592,10 +592,10 @@
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
-              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: this integration never recommends a space set-point.",
+              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
-              "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
+              "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
               "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
               "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor lets the forecast correct itself against what the roof actually delivers.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, and is timed to finish before you get back.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater already gets the tank to the anti-legionella temperature and holds it there, count that as a completed cycle instead of running another one.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "Never run anti-legionella cycles closer together than this, even on very cheap days.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the heating target by 1 °C while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index ae8c426623..40e3a9df09 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -12,7 +12,7 @@
           "price_entity": "Prissensor (Nord Pool eller liknande)"
         },
         "data_description": {
-          "name": "Visas framför alla sensorer som integrationen skapar.",
+          "name": "Titeln på den här posten under Enheter och tjänster. Entiteternas namn använder det fasta enhetsnamnet Heat Pump Optimizer.",
           "tibber_token": "Används för att läsa dina timpriser på el. Skapa en på developer.tibber.com. Lämna som den är om den inte har ändrats. Krävs inte när priskällan är en entitet.",
           "weather_entity": "Härifrån hämtas prognos för utomhustemperatur, vind och regn. Optimeringen planerar 24 timmar framåt och kräver därför en prognos.",
           "price_source": "Tibber använder din API-token. Entitet läser en Home Assistant-prissensor, till exempel Nord Pool.",
@@ -343,7 +343,7 @@
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
-          "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+          "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
           "compressor_freq_sensor": "Sensor för faktisk frekvens (rekommenderas för styrning)",
           "outdoor_temp_entity": "Utomhusgivare",
@@ -582,7 +582,7 @@
               "indoor_temp_entity": "Inomhusgivare",
               "outdoor_temp_entity": "Utomhusgivare",
               "space_setpoint_entity": "Börvärdesenhet för rumsuppvärmning (valfritt)",
-              "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+              "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
               "flow_min_lift_k": "Minsta höjning över inkommande vatten (K)",
               "flow_heat_c": "Högsta framledning vid värme (°C)",
               "space_setpoint_power_feedback": "Följ planerad effekt efter uppmätt förbrukning",
@@ -592,10 +592,10 @@
             "data_description": {
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
               "outdoor_temp_entity": "Valfritt. En egen utegivare är mer exakt än prognosen för den aktuella timmen.",
-              "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Används bara för att märka när enheten inte går att läsa. Optimeringen skriver aldrig ett rekommenderat rumsuppvärmningsbörvärde.",
-              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsenhet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: den här integrationen rekommenderar aldrig ett rumsuppvärmningsbörvärde.",
+              "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Med Styrning av pumpens uppgift satt till Styrning skriver optimeraren det vid varje plansteg, som Styrning av pumpens uppgift beskriver, och när Optimeraren aktiv stängs av skrivs värdet tillbaka som enheten visade före den första skrivningen. Med Av eller Observera läses det bara, för att märka när det inte går att läsa.",
+              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en.",
               "flow_min_lift_k": "Med Styrning av pumpens uppgift på Styrning skrivs vattenbörvärdet vid planens lägsta effekt som det uppmätta inkommande vattnet plus detta: värmepumpens retur, bufferttank, golvretur eller ventilens utlopp, och för en entitet med Returtemperatur bara de tre första. 5 K passar en styrenhet som håller sin framledning på börvärdet. En styrenhet som tar börvärdet som mål för returvattnet antas köra kompressorn hårdare ju högre målet ligger över returen och vill troligen ha mindre; 1–2 K är en startpunkt att kontrollera mot kompressorns uppmätta frekvens och effekt, inte ett uppmätt värde.",
-              "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål.",
+              "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål. En rumsvärmeboost eller Boost-läget skriver i stället börvärdesentitetens eget maximum (högst 70 °C) vid varje steg; ett annat värde än 55 °C här begränsar även det, så ange ett för en lågtemperatur-golvvärme.",
               "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (Luxtronik: 0,5 K), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom ett Luxtronik Smart Home Interface släpper alla satta värden efter 600 s utan åtkomst; och inget annat verktyg skriver samma register (en Luxtronik kastar då skrivningar tyst).",
               "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
               "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Använd denna i stället om din ersättning följer spotpriset.",
           "pv_enabled": "Låter planen köra värmepumpen på ditt eget överskott i stället för att sälja det för mindre än vad köpt el kostar.",
           "pv_peak_kw": "Anläggningens installerade toppeffekt. Används för att skala produktionsprognosen.",
-          "pv_production_entity": "Valfritt. En sensor med faktisk produktion låter prognosen rätta sig efter vad taket verkligen levererar.",
+          "pv_production_entity": "Valfritt. En sensor med faktisk produktion ersätter prognosens aktuella steg med vad taket levererar just nu, högst den installerade effekten; senare steg förblir modellerade.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
       },
@@ -1122,7 +1122,7 @@
         },
         "data_description": {
           "away_presence_entity": "En person, enhetsspårare, kalender eller närvarosensor. Plan-sidans brytare vinner tills den slås av. Att en person är 'inte hemma' betyder fortfarande bortavaro när brytaren är av.",
-          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande, och tidsätts så att den hinner bli klar innan du är tillbaka.",
+          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande med sitt vanliga intervall; den tidsätts inte efter din hemkomst.",
           "away_temperature": "Temperaturen som hålls under bortavaron. Låg nog att spara, hög nog att skydda hus och rör.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst.",
           "holiday_calendar_entity": "När den här kalendern är på ersätter lovets komfort och varmvattenfönster vardag/helg för den dagen. Bortasänkning vinner om bortaläget är aktivt."
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observera läser brytaren och skriver aldrig till den. Styra slår på den när en legionellacykel börjar och av den när cykeln är slut, men slår aldrig på den medan pumpens driftläge inte gör varmvatten. Den slår bara av en brytare som den själv slog på: en brytare som redan var på när cykeln började lämnas i fred. En begränsning: om du slår på brytaren för hand medan en cykel som optimeraren startade pågår, slås den av när cykeln är slut, eftersom de två inte går att skilja åt. Styra kräver brytaren ovan.",
               "dhw_disinfection_switch_entity": "En brytare eller hjälpare som startar värmepumpens eget legionellaprogram. I läget observera läses bara dess tillstånd och visas bland varmvattensensorns attribut; i läget styra slår integrationen på den när en desinfektionscykel börjar och av den när cykeln är slut.",
               "dhw_elastic_legionella_enabled": "Låt legionellacykeln köras en dag eller två tidigare när elen är ovanligt billig, i stället för att alltid vänta till sista dagen. Sista dagen hålls alltid.",
-              "dhw_free_disinfection_enabled": "Om en vedpanna, solslinga eller elpatron redan får tanken till legionellatemperatur och håller den där, räkna det som en genomförd cykel i stället för att köra en till.",
+              "dhw_free_disinfection_enabled": "En vedpanna, solslinga eller elpatron som får tanken till legionellatemperatur räknas som en genomförd cykel i båda lägena. Av: direkt; på: först när tanken har hållit den temperaturen i 20 minuter, så en kort topp räknas inte.",
               "dhw_legionella_min_interval_days": "Kör aldrig legionellacykler tätare än så här, även på mycket billiga dagar.",
               "dhw_quantile_targets_enabled": "Lär in hur mycket varmvatten varje tidsfönster faktiskt använder en tung dag, och gör tanken redo för det i stället för för genomsnittsdagen. Kräver tanktemperaturgivare, konfigurerade varmvattenfönster och ett par veckors underlag."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "vvc_pump_entity": "En brytare som styr VVC-pumpen. Om satt körs pumpen bara under dina varmvattenfönster, plus förvarmningstiden nedan.",
+          "vvc_pump_entity": "En brytare som styr VVC-pumpen. Om satt körs pumpen bara under dina varmvattenfönster, plus förvarmningstiden nedan. Med varmvattnet avslaget eller utan fönster lämnas den på.",
           "vvc_lead_minutes": "Hur långt före ett varmvattenfönster cirkulationspumpen startar, så att slingan redan är varm när fönstret öppnar.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren, säkringsvakten och utrymmessensorn vilande — det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
+          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren och säkringsvakten vilande medan utrymmessensorn bara följer effekttariffens topp, otillgänglig utan effekttariff — det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
           "main_fuse_phases": "Nästan alla svenska hus har 3 faser.",
           "fuse_guard_enabled": "Begränsar värmepumpens planerade effekt till vad säkringen lämnar efter resten av huset. Om en begränsning skulle göra komfortgolvet onåbart säger planen det på sina sensorer i stället för att tyst bli kall.",
           "peak_guard_enabled": "Bevakar effektmätaren live och håller tillbaka eldrivet varmvatten samt sänker värmekurvan resten av mätfönstret när fönstret beräknas sätta en ny fakturerad topp. Kräver en effektmätare; en kall tank eller ett brutet komfortgolv vinner alltid över vakten.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Räkna med mindre sol efter kraftigt snöfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom värmemålet med 1 °C medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
+              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom den lägsta inomhustemperatur som planen godtar med 1 °C, aldrig under 15 °C, medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
               "outage_recovery_enabled": "Efter ett avbrott startar allt samtidigt — kallt hus, kall tank, hela grannskapet — vilket är exakt när en ny månadstopp sätts. Med detta på öppnar ett långt uppehåll i uppdateringarna ett tvåtimmarsfönster där effektavgiften tas på allvar från första kW och varmvattnet köar 45 minuter bakom husvärmen, om inte tanken är riktigt låg.",
               "precip_type_enabled": "Regn blöter ner klimatskalet och ökar värmeförlusten; snö gör det inte. Utan detta behandlas en snöig prognos som regn och planen köper värme för en våt vägg som förblir torr. Kräver Open-Meteo-anslutningen för snödata.",
               "snow_roof_factor_enabled": "I två dygn efter kraftigt snöfall halveras den modellerade solvinsten — snö på takfönster och låga vinterrutor blockerar solen planen räknade med. Medvetet grovt: en faktor och en hålltid, ingen smältmodell."
@@ -1530,7 +1530,7 @@
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
-          "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+          "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
           "outdoor_temp_entity": "Utomhusgivare",
           "dhw_temp_entity": "Givare för varmvattenberedarens temperatur",
diff --git a/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py b/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
index 607977916f..6047966856 100644
--- a/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
+++ b/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
@@ -10,10 +10,20 @@ through ``tools/audit/seat/features_block.py``. Run from the repository root:
     python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
 
 It prints mutant_run's lines, ``SURVIVED NULL`` then ``KILLED <name>`` per
-mutant at the fix head, once for M01-M20 on the arbiter block and once for the
-seam mutants (M21 to M38; M33 retired) on the water-setpoint feedback block, and exits with
+mutant at the fix head, once for M01-M20 and M35 on the arbiter block and once for the
+seam mutants (M21 to M38; M33 and M36 retired) on the water-setpoint feedback block, and exits with
 mutant_run's status. A mutant whose ``old`` text no longer occurs exactly once
 is refused before anything runs.
+
+R10-HOTFIX-FLOW-SETPOINT-STUCK re-anchored M02, M03, M11, M13, M23, M35 and
+M37 on the lines it rewrote: the own-write check no longer holds the write but
+substitutes the baseline (M03 drops that check), and Off keeps the own space
+write until a restore replaces it (M35, renamed, forgets it, and moves to the
+arbiter block, whose stuck-install Off-and-On check kills it). M36 (Off's guard
+reads the dropped write) is retired: that guard no longer reads it, by design.
+The seam block now ends at the replay's `_fb_floor = _fb_sim(clamp=(26.4`: the
+bare `_fb_floor = _fb_sim(` marker matched an earlier simulation #3469 added,
+so the block stopped before every Carry 8 check and no seam mutant could die.
 """
 from __future__ import annotations
 
@@ -37,14 +47,14 @@ MUTANTS = json.loads(r"""
  {
   "name": "M02_no_arm",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
   "new": "    return False"
  },
  {
   "name": "M03_no_own_refusal",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "f\"space_baseline_own:{entity}\", own,",
-  "new": "f\"space_baseline_own:{entity}\", False,"
+  "old": "    if own:\n        baseline = _space_target(inp, inp.plan, now, None, boosted=False)\n",
+  "new": "    if False:\n        baseline = _space_target(inp, inp.plan, now, None, boosted=False)\n"
  },
  {
   "name": "M04_before_ignored",
@@ -91,8 +101,8 @@ MUTANTS = json.loads(r"""
  {
   "name": "M11_off_no_persist",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "new": "if held.written or held.retry or held.dropped:"
+  "old": "if held.written or held.retry or held.space_before is not None:",
+  "new": "if held.written or held.retry:"
  },
  {
   "name": "M12_no_grace",
@@ -103,8 +113,8 @@ MUTANTS = json.loads(r"""
  {
   "name": "M13_forget_keeps_before",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
-  "new": "held.written, held.misses, held.retry, held.dropped = {}, {}, {}, {}"
+  "old": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None",
+  "new": "held.written, held.misses, held.retry = {}, {}, {}"
  },
  {
   "name": "M14_factory_none",
@@ -147,21 +157,28 @@ MUTANTS = json.loads(r"""
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
   "old": "    if not entity:\n        return None\n    return off_restore.Restorer(",
   "new": "    return off_restore.Restorer("
+ },
+ {
+  "name": "M35_forget_drops_own_write",
+  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
+  "old": "    held.dropped = {} if own is None else {\"space_setpoint\": own}\n",
+  "new": "    held.dropped = {}\n"
  }
 ]
 """)
 #: The seam with R10-WATER-SETPOINT-FEEDBACK (the merge of #3405): the off
 #: restore's edit adoption reads the space slot before ``hold``, so a loop
 #: write's controller cut is ``_clamp_cut``'s, never a person's baseline; and
-#: the record a loop move drops (``_note_sent``) still refuses the optimizer's
-#: own write as the restore's baseline (roster Carry 8). Their checks sit in
+#: the record a loop move drops (``_note_sent``) still keeps the optimizer's
+#: own write from the restore's baseline (roster Carry 8). Their checks sit in
 #: the feedback block, which needs the arbiter block's imports.
 SEAM_BLOCK = (
     'env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py '
     '--prelude "from harness import FakeEntry as _pa_entry" '
     '--prelude "from types import SimpleNamespace as _PaNS" '
     '--prelude "from heatpump_optimizer.const import MODE_AUTO as _PA_AUTO, MODE_OFF as _PA_OFF" '
-    '"# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim("'
+    '--prelude "from heatpump_optimizer import off_restore as _pa_or" '
+    '"# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim(clamp=(26.4"'
 )
 SEAM_MUTANTS = json.loads(r"""
 [
@@ -180,8 +197,8 @@ SEAM_MUTANTS = json.loads(r"""
  {
   "name": "M23_arm_ignores_dropped_record",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
-  "new": "    last = record[0] if record is not None else None\n"
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
+  "new": "    return record[0] if record is not None else None\n"
  },
  {
   "name": "M24_prev_not_kept",
@@ -243,23 +260,11 @@ SEAM_MUTANTS = json.loads(r"""
   "old": "(held.written, held.misses, held.retry, held.dropped)",
   "new": "(held.written, held.misses, held.retry)"
  },
- {
-  "name": "M35_forget_keeps_dropped",
-  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
-  "new": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None"
- },
- {
-  "name": "M36_off_ignores_dropped",
-  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "new": "if held.written or held.retry or held.space_before is not None:"
- },
  {
   "name": "M37_arm_reads_run",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
-  "new": "    last = record[0] if record is not None else None if held.feedback is None else held.feedback.prev_c\n"
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
+  "new": "    return record[0] if record is not None else None if held.feedback is None else held.feedback.prev_c\n"
  },
  {
   "name": "M38_load_unfiltered",
diff --git a/dev/audit/harnesses/r10_rca_setpoint_latch.py b/dev/audit/harnesses/r10_rca_setpoint_latch.py
new file mode 100644
index 0000000000..a6b5ccd72a
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_setpoint_latch.py
@@ -0,0 +1,162 @@
+"""R10-RCA-SETPOINT-LATCH-DEADLOCK detector: from every persisted arbiter state,
+the demanded space write reaches the entity with no person acting.
+
+    python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <checkout> [--passes N]
+
+The pump-duty arbiter (``pump_arbiter.apply``) runs on a flow set-point
+install, with Control on and a plan that heats the house on every step. The
+stub device takes every write. A reference install with no persisted state
+gives the demanded target. Then each persisted starting state is driven for
+N one-minute passes (default 10): the space record (none, the idle gate
+``FLOW_GATE_C``, or the heating flow), the record a loop move dropped (none,
+or the gate; only where the tree has ``ArbiterState.dropped``), the entity's
+reading (the gate, 40, or the heating flow), and whether the off restore is
+already armed on the entity (only where the tree has ``pump_arbiter.CONSUMER``).
+Every state must end with the entity reading the demanded target.
+
+Exit codes: 0 every state converges; 1 a state never gets the demanded
+write (the defect); 2 the reference install was never written, so the
+harness can see no write (the skip control); 3 the modules were loaded from
+outside the named checkout (provenance refusal).
+"""
+from __future__ import annotations
+
+import argparse
+import asyncio
+import itertools
+import os
+import sys
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace as NS
+
+UTC = timezone.utc
+T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
+SPACE = "number.water_set"
+
+
+def main() -> int:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--check", required=True, help="checkout root to measure")
+    ap.add_argument("--passes", type=int, default=10)
+    args = ap.parse_args()
+    root = os.path.realpath(args.check)
+    # Older trees read package data relative to the cwd: measure from the root.
+    os.chdir(root)
+    for sub in ("custom_components", "tests", "tests/hastub"):
+        sys.path.insert(0, os.path.join(root, sub))
+
+    import harness  # noqa: PLC0415
+    from heatpump_optimizer import pump_arbiter as pa  # noqa: PLC0415
+    from heatpump_optimizer.const import MODE_AUTO  # noqa: PLC0415
+    from heatpump_optimizer.entry_config import EntryConfig  # noqa: PLC0415
+
+    for mod in (harness, pa):
+        if not os.path.realpath(mod.__file__).startswith(root + os.sep):
+            print(f"REFUSED {mod.__name__} loaded from {mod.__file__}, not {root}")
+            return 3
+
+    def plan(n):
+        return NS(
+            timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)],
+            power_schedule=[1.5] * n,
+            dhw_power_schedule=[0.0] * n,
+            optimal_setpoints=[21.0] * n,
+        )
+
+    class Coord:
+        def __init__(self, reading: str, entry_id: str) -> None:
+            self.hass = harness.FakeHass({
+                "select.pump_mode": harness.FakeState("Heating", attributes={"options": list(TUYA)}),
+                "number.dhw_set": harness.FakeState("48", attributes={"min": 40, "max": 63}),
+                SPACE: harness.FakeState(reading, attributes={"min": 25, "max": 63}),
+            })
+            self._config = EntryConfig.from_mapping({
+                "pump_duty_mode": "control",
+                "heat_pump_mode_entity": "select.pump_mode",
+                "dhw_setpoint_entity": "number.dhw_set",
+                "space_setpoint_entity": SPACE,
+                "space_setpoint_unit": "flow",
+            })
+            self._mode = MODE_AUTO
+            self.stale = False
+            self._current_action = {"mode": "eco"}
+            self._optimization_result = plan(400)
+            self._thermal_model = NS(params=NS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2)
+            self._thermal_params = NS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None)
+            self._current_state = NS(outdoor_temperature=0.0)
+            self.entry = harness.FakeEntry(entry_id=entry_id)
+
+        def _plan_is_stale(self) -> bool:
+            return self.stale
+
+        @property
+        def effective_config(self):
+            return self._config
+
+        @property
+        def thermal_params(self):
+            return self._thermal_params
+
+        def arbiter_inputs(self):
+            return pa.ArbiterInputs(
+                hass=self.hass, config=self._config, mode=self._mode,
+                plan=self._optimization_result, plan_stale=self.stale, entry_released=False,
+                state=self._current_state, thermal=self._thermal_model, params=self._thermal_params,
+                action=self._current_action, measured_power_kw=None, disinfecting=False,
+            )
+
+        async def async_set_mode(self, mode) -> None:
+            self._mode = mode
+
+    def converge(coord: Coord) -> float:
+        for i in range(args.passes):
+            asyncio.run(pa.apply(coord, T0 + timedelta(minutes=i)))
+            for _d, _s, data in coord.hass.services.calls:  # the device takes each write
+                value = data.get("option", data.get("value"))
+                coord.hass.states.get(data["entity_id"]).state = str(value)
+            coord.hass.services.calls.clear()
+        return float(coord.hass.states.get(SPACE).state)
+
+    ids = itertools.count()
+    ref_reading = "40"
+    target = converge(Coord(ref_reading, f"latch{next(ids)}"))
+    if target == float(ref_reading):
+        print(f"SKIP the reference install was never written (reads {target}): nothing to measure")
+        return 2
+
+    gate, heat = float(pa.FLOW_GATE_C), target
+    has_dropped = "dropped" in getattr(pa.ArbiterState, "__dataclass_fields__", {})
+    has_restore = hasattr(pa, "CONSUMER")
+    if has_restore:
+        from heatpump_optimizer import off_restore  # noqa: PLC0415
+    states = list(itertools.product(
+        (None, gate, heat),
+        (None, gate) if has_dropped else (None,),
+        (gate, 40.0, heat),
+        (False, True) if has_restore else (False,),
+    ))
+    failed = 0
+    for written, dropped, reading, armed in states:
+        coord = Coord(f"{reading:g}", f"latch{next(ids)}")
+        held = pa.state_for(coord)
+        held.loaded = True
+        if armed:
+            coord.entry.runtime_data = coord
+            asyncio.run(off_restore.async_arm(coord.hass, coord.entry, coord._config, pa.CONSUMER))
+        if written is not None:
+            held.written["space_setpoint"] = (written, T0 - timedelta(hours=1))
+        if dropped is not None:
+            held.dropped["space_setpoint"] = dropped
+        final = converge(coord)
+        if final != target:
+            failed += 1
+            print(f"FAIL written={written} dropped={dropped} reading={reading:g} armed={armed}: "
+                  f"reads {final:g} after {args.passes} passes, demanded {target:g}")
+    print(f"SUMMARY root={root} demanded={target:g} states={len(states)} failed={failed} "
+          f"passes={args.passes} dropped_axis={has_dropped} armed_axis={has_restore}")
+    return 1 if failed else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3562.md b/dev/programme/delivery/3562.md
new file mode 100644
index 0000000000..18baa9d028
--- /dev/null
+++ b/dev/programme/delivery/3562.md
@@ -0,0 +1 @@
+- [#3562](https://github.com/tvofi/heatpump_optimizer/pull/3562) — **open**, R10-HOTFIX-BOOST-FLOW-CEILING: r10 hotfix boost flow ceiling (R10-HOTFIX-BOOST-FLOW-CEILING)
diff --git a/dev/programme/delivery/3576.md b/dev/programme/delivery/3576.md
new file mode 100644
index 0000000000..84ac680f85
--- /dev/null
+++ b/dev/programme/delivery/3576.md
@@ -0,0 +1 @@
+- [#3576](https://github.com/tvofi/heatpump_optimizer/pull/3576) — **open**, Correct the away, disinfection, circulation and set-point-unit text to what the code does (R10-DOCS-STRINGS-RESIDUE)
diff --git a/dev/programme/delivery/3580.md b/dev/programme/delivery/3580.md
new file mode 100644
index 0000000000..afa5d6d8a8
--- /dev/null
+++ b/dev/programme/delivery/3580.md
@@ -0,0 +1 @@
+- [#3580](https://github.com/tvofi/heatpump_optimizer/pull/3580) — **open**, R10-DOCS-STRINGS-RESIDUE (part 2): r10 docs strings residue p2 (R10-DOCS-STRINGS-RESIDUE)
diff --git a/docs/configuration.md b/docs/configuration.md
index d8ded8775a..7471fcd262 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -71,7 +71,7 @@ reported as a connection problem rather than as a bad token.
 
 | Setting | Default | What it means |
 |---|---|---|
-| Name for this integration | Heat Pump Optimizer | Shown in front of every entity this integration creates. |
+| Name for this integration | Heat Pump Optimizer | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | Tibber | Where hourly electricity prices come from: Tibber (needs the token below) or a price sensor entity you already have. |
 | Tibber API token | — (**required with the Tibber source**) | Reads your hourly electricity prices. Create one at developer.tibber.com. The field still shows when the price source is a price entity — not needed then, so leave it empty. |
 | Price sensor (Nord Pool or similar) | — (**required with the price-entity source**) | A `sensor` publishing the current electricity price, read instead of Tibber. |
@@ -527,7 +527,7 @@ device page and on the card, not here.
 | Away indicator | none | `person`, `device_tracker`, `calendar`, `binary_sensor` | Polarity is handled for you: a person being *not home* still means away when the Plan-page toggle is off. |
 | Holiday-profile calendar | none | a `calendar` | When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active. |
 | Temperature while away | 16.0 °C | 5–21, 0.5 steps | Low enough to save, high enough to protect the house and its plumbing. With the mold guard on, the mold-safe temperature outranks it and can hold the room near the comfort target in a humid house, so away then saves little space-heating energy ([Away and the mold guard](how-it-works.md#away-and-holiday-mode)). |
-| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs, timed to finish before you get back. |
+| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs on its usual interval; it is not timed to your return. |
 
 ### Quick setup
 
@@ -625,7 +625,7 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Space-heating set-point entity | none | `number` / `input_number` / `climate` | Optional. Used to notice when the entity cannot be read. Written only with **Pump duty control** at Control, and then with the plan's own number (see below), never a recommended optimum. |
 | What that set-point entity expects | Indoor temperature | Indoor temperature / Flow temperature / Return temperature | A declaration, not a write. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C. *Return temperature* is a controller that takes the number as its return-water target (see [Pump duty control](#pump-duty-control)). |
 | Minimum lift above the inlet water (`flow_min_lift_k`) | 5 K | 0.5–15 K, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at the plan's lowest power is the measured inlet water plus this (see [Pump duty control](#pump-duty-control)). |
-| Heating flow ceiling (`flow_heat_c`) | 55 °C | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at full planned power, and the highest heating value written. A stored value at or below the 25 °C gate is read as 55 °C. |
+| Heating flow ceiling (`flow_heat_c`) | 55 °C | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at full planned power, and the highest heating value written while the plan is in charge. A space boost or Boost mode writes the set-point entity's own maximum instead (up to 70 °C), capped by a value here other than 55 °C. A stored value at or below the 25 °C gate is read as 55 °C. |
 | Follow the planned power on the measured draw (`space_setpoint_power_feedback`) | On | on / off | Shown when the unit above is *Flow* or *Return temperature*; acts only when a heat-pump power sensor is configured too. Closes the heating value on the measured draw (see [Pump duty control](#pump-duty-control)). Off writes the inlet plus the lift. |
 | Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
 | Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
@@ -856,8 +856,16 @@ writes, at every 15-minute plan step:
   all get the fallback row, the space set-point apart (see below). A boost switch adds its own duty to the plan's
   step: *Boost Space Heating* alone writes *Heating*, *DHW Boost* alone
   writes *DHW (Hot Water)*, and a step that also wants the other duty
-  writes *Heating + DHW*. Boost mode writes *Heating + DHW* with the
-  heating-flow ceiling (55 °C, or `flow_heat_c`) rather than the fallback's.
+  writes *Heating + DHW*. Boost mode writes *Heating + DHW*, and a
+  heating set-point rather than the fallback's.
+  On a flow or return set-point, *Boost Space Heating* and Boost mode both
+  write the set-point entity's own maximum on every step they cover,
+  whatever power the plan booked for the step, capped by a heating flow
+  ceiling set to anything but its 55 °C default and by the controller's
+  maximum set-point sensor when one is configured. An entity whose maximum it cannot read, or one above
+  70 °C (a generic number helper), keeps the planned level instead. A boost
+  lasts two hours and is not trimmed on the room temperature, so on a
+  low-temperature floor heating set the heating flow ceiling to bound it.
 - **While Optimizer active is on, the optimizer holds what it wrote.** A
   reading of those three entities that differs from what the optimizer wrote —
   a change made on the pump, in an app, by a schedule, or the pump's own reset —
@@ -876,9 +884,12 @@ writes, at every 15-minute plan step:
   over it until you turn it off (outside the entity's own minimum and
   maximum, the nearest value it takes); a value set while it is off is read again
   when it next writes. A reading equal to the optimizer's own last write is
-  never taken as yours: after an upgrade from a version without this, the
-  set-point is not written until it reads anything else, so set it on the
-  pump once. The mode and the hot-water set-point are not restored.
+  never taken as yours: after an upgrade from a version without this, the value
+  restored is the one the optimizer holds when the plan is not in charge (35 °C
+  or the weather curve for a water set-point, the planned room temperature for
+  an indoor one), and the optimizer writes the set-point from its first pass.
+  Set it on the pump once while the optimizer is on to have your own
+  value restored instead. The mode and the hot-water set-point are not restored.
 - **A write the pump does not hold is retried.** If the value written back
   still does not hold, a warning repair notice is raised and the value is sent
   again every 5 minutes; the notice clears on the first write that holds, or
@@ -1060,7 +1071,7 @@ Tank size, daily draw, inlet water and the disinfection extras. The first-menu
 | Cold water inlet sensor | none | a temperature sensor | When set, its live reading replaces the model above. |
 | Greywater heat recovery effectiveness | 0.0 | 0–0.9, 0.05 steps | The fraction of drain heat a drain-water recovery unit returns. 0 means none installed. |
 | Learn heavy-day hot water targets | off | on/off | Makes the tank ready for a heavy day rather than an average one. Needs a tank sensor, configured time frames, and a couple of weeks of evidence. |
-| Credit disinfection from any heat source | off | on/off | If a wood boiler, solar coil or immersion heater already got the tank hot enough and held it there, count that as a completed cycle. |
+| Credit disinfection from any heat source | off | on/off | A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature counts as a completed cycle either way. Off, it counts the moment the tank is within 1 °C of that temperature; on, only after the tank has spent 20 minutes within 0.5 °C of it, so a short peak credits nothing. |
 | Let the anti-legionella cycle pick a cheap day | off | on/off | Allows the cycle to run a day or two early when electricity is unusually cheap. The deadline is still always honoured. |
 | Earliest anti-legionella re-run | 5 days | 1–14 | A floor on how close together cycles may run, however cheap the day. |
 | Pump's disinfection switch | none | `switch` / `input_boolean` | A switch or helper that starts the heat pump's own anti-legionella program. Its state is read on every update and published on the hot water sensor's attributes as `dhw_disinfection_switch`; the attribute is absent while no switch is set. |
@@ -1074,7 +1085,7 @@ The DHW loop pump. The heating-circuit circulation pump lives on
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. |
+| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. With hot water off or no time frames, it is left on. |
 | Start circulation before a time frame | 20 min | 0–120, 5 steps | So the loop is already hot when the time frame opens. |
 
 ### Solar panels
@@ -1090,7 +1101,7 @@ what consuming actually costs you.
 | Overall system efficiency | 0.80 | 0.3–1.0, 0.01 steps | Everything between sunlight and the meter: inverter losses, panel temperature, dirt, orientation. |
 | Export compensation per kWh | 0.0 | 0–10, 0.01 steps | What you are paid for an exported kWh. While you have surplus, that is what an extra kWh of heating really costs. |
 | Export compensation entity | none | a sensor | Use this instead if your compensation follows the spot price. |
-| Solar production sensor | none | a `power` sensor | Lets the forecast correct itself against what the roof actually delivers. |
+| Solar production sensor | none | a `power` sensor | Replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled. |
 
 ### Self-learning and diagnostics
 
@@ -1113,7 +1124,7 @@ opt-in learners are on **Advanced learning features**.
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Staggered recovery after a power cut | off | on/off | After an outage everything restarts at once, which is exactly when a new monthly peak gets set. This opens a two-hour recovery window where hot water queues 45 minutes behind space heating unless the tank is genuinely low. A restart that finds the last saved heartbeat ahead of the clock (the clock was set back, so the gap cannot be known) counts as an outage too. |
-| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the target by 1 °C while a window appears open. Off by default because it moves real heat. |
+| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the coldest temperature the plan accepts by 1 °C, never below 15 °C, while a window appears open. Off by default because it moves real heat. |
 | Plan around immersion heater use | off | on/off | Repeated immersion use raises the hot-water planning margin so the heat pump gets there first. It also declares the immersion element: when the power meter reads more than the compressor's nameplate can draw, the excess books as its own ledger line. With this off and neither pump heater flag on, nothing books as resistive heat, because the meter alone cannot tell an element from a compressor over its configured nameplate. |
 | Tell snow from rain in the forecast | off | on/off | Rain soaks the envelope and raises heat loss; snow does not. Needs the Open-Meteo connection. |
 | Assume less sun after heavy snowfall | off | on/off | Halves modelled solar gain for two days after heavy snowfall. Deliberately crude. |
@@ -1126,7 +1137,7 @@ opt-in learners are on **Advanced learning features**.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess. |
+| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor and the fuse guard dormant; the headroom sensor then follows the capacity-tariff peak alone and is unavailable without a capacity tariff — there is no safe default to guess. |
 | Phases | 3 | 1–3 | Nearly every Swedish house is 3-phase. |
 | Keep the plan under the main fuse | off | on/off | Caps planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so instead of silently going cold. |
 | Live peak guard | off | on/off | Watches the power meter and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter. |
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 4e1bb4d63c..43544808cb 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -575,8 +575,9 @@ capacity charge at the month's billed peak, the kWh a resistive heater drew
 beyond what the compressor can (the pump's own tank booster or backup heater
 while its flag is on, or an immersion heater you have declared), and
 compressor wear in starts. The total adds those lines and nothing else; a
-note under it says which lines it covers and that the savings figure
-compares spot cost only. Wear reads "not priced" until you set a
+note under it says which lines it covers and what the savings figure
+compares: the plan and the thermostat baseline are both priced at spot
+plus the per-kWh grid fee. Wear reads "not priced" until you set a
 compressor replacement cost. Beside it, **Where the money went** splits the
 spot line by the plan's reason for each kWh, largest first; the bars add up
 to the spot line. Every receipt the integration keeps (24 months) is on the
@@ -697,8 +698,8 @@ configured, the way it did before:
 - **Each ranked row carries its spread and an *estimated* badge.** The spread
   is in degrees the model's predictions can move — one unit, comparable
   between sensors. The line under the heading names what drove the replay:
-  your install's measured delivery where there is history, configured
-  defaults otherwise.
+  the mean electrical power your heat pump has measured where there is
+  history, half its configured maximum otherwise.
 - **A sensor the estimate cannot price is listed below the ranked rows, with
   its reason** — the outdoor probe whose job the weather entity already does,
   the floor-return probe that feeds a state estimate rather than a learned
@@ -724,7 +725,7 @@ on the Health page names which. The pill appears once that sensor has a state.
 
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="img/card/health-dark.png">
-  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first settled month; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
+  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first month with a booked saving; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
 </picture>
 
 *Everything here is read from the integration's sensors; the card computes no
@@ -735,8 +736,8 @@ figure of its own.* The page shows, top to bottom:
   solve took (the Optimization Status sensor's `solve_time_ms`). Its pill reads
   **Stale** once the plan is past the limit the header's own status pill uses.
   **Still learning** lists the sensors that are enabled by default and wait
-  for evidence, each with its reason in words: savings (the first settled
-  month), heat pump COP (a power meter, then some running time), prediction
+  for evidence, each with its reason in words: savings (the first month with a
+  booked saving), heat pump COP (a power meter, then some running time), prediction
   accuracy (the first scored interval) and the optimization score (the first
   scored day). Home Assistant hides an unavailable entity's attributes, so the
   card cannot read the sensor's own `waiting_for` code and the reason is keyed
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index ccbb2bb9c7..8d334740c5 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -617,9 +617,10 @@ redundant cycle.
 
 Two opt-in refinements:
 
-- **Free disinfection**: if another heat source holds the tank at the
-  disinfection temperature *long enough*, that counts as a completed cycle. It
-  is hold-verified, so a momentary blip at 60 °C credits nothing.
+- **Hold-verified disinfection**: with *Credit disinfection from any heat
+  source* on, a heat source resets the timer only once the tank has held the
+  disinfection temperature for 20 minutes, so a momentary blip at 60 °C credits
+  nothing; with it off, any observation resets it at once, as above.
 - **A price-aware cycle**: inside its interval the cycle may run a day or two
   early (no sooner than a configurable minimum, default 5 days) when a known
   price beats what a typical remaining day is expected to bottom out at. The
@@ -646,7 +647,8 @@ Everything here is inert until configured or until evidence exists:
   Advisor** reports the cheapest setpoint that still covers your learned heavy
   days — read-only, the decision stays yours.
 - **Circulation pumps** (opt-in): a VVC loop pump runs only around your demand
-  frames, with a lead (default 20 minutes) so the loop is hot when they open.
+  frames, with a lead (default 20 minutes) so the loop is hot when they open;
+  with hot water off or no frames it is left on.
   The space circulation pump pauses only in provably idle, warm slots, and is
   forced on whenever heat is planned, the heat curve is being driven, any room
   is near its comfort floor, or it is freezing outside.
@@ -921,7 +923,7 @@ that cannot save them anything should not be able to cost them anything.
 
 A week away is the largest single saving a heating system can offer: a deep
 setback plus hot water held only at its away minimum (20 °C unless you change
-it), except for a legionella cycle timed to complete before you return.
+it), while the legionella cycle keeps its usual interval.
 
 What makes this more than a manual setpoint is the **return time**. Knowing when
 the house must be comfortable again lets the recovery heat be bought in the
diff --git a/docs/setup.md b/docs/setup.md
index ebd69f7217..03cd658ae1 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -88,7 +88,7 @@ answers of the whole flow.*
 
 | Setting | What it asks |
 |---|---|
-| Name for this integration | Shown in front of every entity the integration creates. |
+| Name for this integration | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | `Tibber` uses your API token; `Price entity (Nord Pool or similar)` reads a Home Assistant price sensor. |
 | Tibber API token | Required only when the source is Tibber. Checked against Tibber before the flow continues — a network failure is reported as a connection problem, not as a bad token. |
 | Price sensor (Nord Pool or similar) | Required only when the source is an entity. |
diff --git a/tests/closures.json b/tests/closures.json
index 23e59f4c8b..d9c773fc84 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4351,6 +4351,7 @@
    "dev/audit/harnesses/r10_rca_name_kept_plant.py",
    "dev/audit/harnesses/r10_rca_roster_drain_replay.py",
    "dev/audit/harnesses/r10_rca_sav_estimate.py",
+   "dev/audit/harnesses/r10_rca_setpoint_latch.py",
    "dev/audit/harnesses/r10_rca_sweep_settle_loop.py",
    "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",
    "dev/audit/harnesses/r10_recarry_head.py",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 8641c21162..6a677b7f93 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -4664,6 +4664,164 @@ def check_power_feedback_claims() -> None:
             all(fact in (pa._clamp_cut.__doc__ or "") for fact in (comment_id, "10104", "10103")))
 
 
+# ---------------------------------------------------------------------------
+# R10-DOCS-STRINGS-RESIDUE carries 5 to 13: reader sentences and option texts
+# that described behaviour the code does not have. Each arm takes its fact
+# from the producing code, refuses the old wording in the reader corpus and in
+# all four string files, and requires the corrected sentence to state the fact.
+# ---------------------------------------------------------------------------
+_STRING_FILES = {
+    name: json.loads((PKG / rel).read_text())
+    for name, rel in (("strings.json", "strings.json"), ("en.json", "translations/en.json"),
+                      ("de.json", "translations/de.json"), ("sv.json", "translations/sv.json"))
+}
+
+#: (carry, the old wording in any language) -- the sentences these carries corrected.
+_RESIDUE_REFUSED = (
+    ("Carry 5", r"lowers the (?:heating )?target by|Heizziel um|värmemålet med"),
+    ("Carry 6", r"headroom sensor dormant|Reserve inaktiv|utrymmessensorn vilande"),
+    ("Carry 7", r"correct itself against|Prognose sich anhand|rätta sig efter"),
+    ("Carry 8", r"in front of every (?:entity|sensor)|vorangestellt|Visas framför"),
+    ("Carry 9", r"compares spot cost only"),
+    ("Carry 10", r"measured delivery"),
+    ("Carry 11", r"first settled month"),
+)
+
+
+def _string_leaves(tree: object):
+    if isinstance(tree, dict):
+        for value in tree.values():
+            yield from _string_leaves(value)
+    elif isinstance(tree, str):
+        yield tree
+
+
+def residue_hits(corpus: dict[str, str], string_files: dict[str, dict]) -> dict[str, list[str]]:
+    """Every refused wording still present, by carry: the document or string file it is in."""
+    texts = {**{k: " ".join(v.split()) for k, v in corpus.items()},
+             **{k: "\n".join(_string_leaves(v)) for k, v in string_files.items()}}
+    return {carry: hits for carry, pattern in _RESIDUE_REFUSED
+            if (hits := [name for name, text in texts.items() if re.search(pattern, text)])}
+
+
+def menu_title_mismatches(strings: dict) -> tuple[int, list[str]]:
+    """Every options-menu entry whose target step has a title: (pairs compared, the pairs whose names differ).
+
+    Design choice: the options flow only. Its menu entries name the page they open; the config flow's are
+    actions ("Continue setup", "Describe my building (recommended)") and legitimately differ from the title."""
+    pairs, bad = 0, []
+    for flow in ("options",):
+        steps = strings.get(flow, {}).get("step", {})
+        for body in steps.values():
+            for key, label in (body.get("menu_options") or {}).items():
+                title = steps.get(key, {}).get("title")
+                if title is None:
+                    continue
+                pairs += 1
+                if title != label:
+                    bad.append(f"{flow}.step.{key}: menu {label!r}, title {title!r}")
+    return pairs, bad
+
+
+def check_docs_strings_residue() -> None:
+    R.section("reader text against the code that produces it (R10-DOCS-STRINGS-RESIDUE carries 5 to 13)")
+    import inspect
+    import types
+    from heatpump_optimizer import away, const, coordinator, entry_config, ledger, topology
+
+    flat = {k: " ".join(v.split()) for k, v in DOCS.items()}
+    cfg, en = flat.get("configuration.md", ""), _STRING_FILES["en.json"]
+    opts = en["options"]["step"]
+    hits = residue_hits(CORPUS, _STRING_FILES)
+    R.check("no reader doc or string file keeps a corrected sentence's old wording", not hits, repr(hits))
+
+    # Carry 5: the open-window relax widens the floor and leaves the target.
+    relax, floor = const.OPEN_WINDOW_RELAX_C, const.ECONOMY_ABSOLUTE_FLOOR
+    fields = dict.fromkeys(away._OPT_FIELDS, None) | {"target_temp": 21.0, "min_temp": 20.0}
+    thermal = types.SimpleNamespace(**dict.fromkeys(away._DHW_FIELDS, 45.0))
+    banded, _ = away.solve_bands(types.SimpleNamespace(**fields), thermal, None, (relax,))
+    R.check("solve_bands lowers min_temp by OPEN_WINDOW_RELAX_C and leaves target_temp",
+            banded["min_temp"] == 20.0 - relax and banded["target_temp"] == 21.0, repr(banded))
+    low, _ = away.solve_bands(types.SimpleNamespace(**(fields | {"min_temp": floor})), thermal, None, (relax,))
+    R.check("solve_bands never takes min_temp below ECONOMY_ABSOLUTE_FLOOR", low["min_temp"] == floor, repr(low))
+    phrase = f"by {relax:g} °C, never below {floor:g} °C"
+    R.check(f"configuration.md's open-window row says the coldest accepted temperature drops {phrase}",
+            f"lowers the coldest temperature the plan accepts {phrase}" in cfg)
+    R.check(f"the open-window option text says {phrase}",
+            phrase in opts["learning_features"]["sections"]["weather"]["data_description"]["open_window_relax_enabled"])
+
+    # Carry 6: fuse 0 is no fuse, so the headroom follows the capacity-tariff peak alone.
+    def fuse(amps: int) -> float | None:
+        cfg_ = types.SimpleNamespace(main_fuse_amperes=amps, main_fuse_phases=3)
+        cfg_.fuse_kw_at = lambda a: entry_config.EntryConfig.fuse_kw_at(cfg_, a)
+        return entry_config.EntryConfig.fuse_kw(cfg_)
+
+    R.check("EntryConfig.fuse_kw answers None at main fuse 0, and a capacity at 16 A (control)",
+            fuse(0) is None and fuse(16) is not None, repr((fuse(0), fuse(16))))
+    R.check("configuration.md's main-fuse row says the headroom sensor follows the capacity-tariff peak",
+            "the headroom sensor then follows the capacity-tariff peak alone" in cfg)
+    R.check("the main-fuse option text says the headroom sensor follows the capacity-tariff peak",
+            "headroom sensor following the capacity-tariff peak alone"
+            in opts["grid_connection"]["data_description"]["main_fuse_amperes"])
+
+    # Carry 7: the measured production replaces step 0 only.
+    pv = re.search(r"production\[0\] = min\(self\._pv_production, config\.peak_kw\)",
+                   inspect.getsource(coordinator))
+    R.check("the coordinator replaces production[0] alone, capped at peak_kw (anchor)", pv is not None)
+    for where, text in (("configuration.md", cfg),
+                        ("the PV sensor option text", opts["solar_pv"]["data_description"]["pv_production_entity"])):
+        R.check(f"{where} says only the current step is replaced, capped at the installed capacity",
+                "current step" in text and "capped at the installed capacity" in text)
+
+    # Carry 8: every entity is named from the device, whose name is a literal.
+    device = re.search(r'DeviceInfo\(\s*identifiers=.*?name="([^"]+)"', inspect.getsource(coordinator), re.S)
+    R.check("the coordinator's DeviceInfo names the device by a literal (anchor)", device is not None)
+    name = device.group(1) if device else "<none>"
+    for where, text in (("setup.md", flat.get("setup.md", "")), ("configuration.md", cfg),
+                        ("the name option text", en["config"]["step"]["user"]["data_description"]["name"])):
+        R.check(f"{where} says entities use the fixed device name {name!r}",
+                f"fixed device name, {name}" in text)
+
+    # Carry 9: both sides of the saving are priced at spot plus the per-kWh fee.
+    R.check("observe_spot_and_settle_savings prices the settlement at spot + fee_per_kwh (anchor)",
+            "spot=spot + fee_per_kwh" in inspect.getsource(ledger.MonthlyLedger.observe_spot_and_settle_savings))
+    card = flat.get("dashboard-card.md", "")
+    R.check("dashboard-card.md says both sides are priced at spot plus the per-kWh grid fee",
+            "both priced at spot plus the per-kWh grid fee" in card)
+
+    # Carry 10: the replay's power is the measured mean, else a fraction of the maximum.
+    half = {0.5: "half"}.get(topology._ADVISOR_DUTY_FRACTION)
+    R.check("_ADVISOR_DUTY_FRACTION is a fraction the page can name", half is not None,
+            repr(topology._ADVISOR_DUTY_FRACTION))
+    R.check("dashboard-card.md names the measured mean power, else the configured maximum's fraction",
+            f"mean electrical power your heat pump has measured where there is history, {half} its configured maximum"
+            in card)
+
+    # Carry 11: the Health picture's alt text names the booked-saving wait.
+    R.check("dashboard-card.md's Health picture waits for the first month with a booked saving",
+            "savings waiting for the first month with a booked saving" in card)
+
+    # Carry 13: one options page, one name per language.
+    for fname, strings in _STRING_FILES.items():
+        pairs, bad = menu_title_mismatches(strings)
+        R.check(f"{fname}: every options-menu entry names its page by the page's title ({pairs} pairs)",
+                pairs > 0 and not bad, "; ".join(bad))
+
+    # Null controls: each old wording, put back, fires; a renamed page title fires.
+    for carry, old in (
+        ("Carry 5", "this additionally lowers the target by 1 °C"), ("Carry 6", "the headroom sensor dormant"),
+        ("Carry 7", "Lets the forecast correct itself against what the roof"),
+        ("Carry 8", "Shown in front of every entity"), ("Carry 9", "the savings figure compares spot cost only"),
+        ("Carry 10", "your install's measured delivery"), ("Carry 11", "waiting for the first settled month"),
+    ):
+        R.check(f"{carry}: the old wording, put back, is refused (null control)",
+                carry in residue_hits({"setup.md": old}, {}))
+    renamed = json.loads(json.dumps(_STRING_FILES["de.json"]))
+    renamed["options"]["step"]["grid"]["title"] = "Netz-Spitzentarif"
+    R.check("a de grid page titled apart from its menu entry is refused (null control)",
+            bool(menu_title_mismatches(renamed)[1]))
+
+
 def check_stateless() -> None:
     R.section("the user pages describe the integration as it is, with no change history (R10-USER-DOCS-FINAL)")
     pages = _user_pages()
@@ -4756,6 +4914,7 @@ def main() -> int:
     check_readme_marketplace()
     check_surface_coverage()
     check_power_feedback_claims()
+    check_docs_strings_residue()
     check_stateless()
     return R.close("checks")
 
diff --git a/tests/features.py b/tests/features.py
index 01a0f60761..25808db221 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -63056,7 +63056,7 @@ _pa_bound = _PaCoord(_PA_TUYA, duties="ssss", flow=False)
 def _pa_bound_target(low):
     _pa_bound.hass.states.get("number.water_set").attributes = {"min": low, "max": 63}
     return _pa._space_target(
-        _pa_bound.arbiter_inputs(), _pa_bound._optimization_result, _PA_T0, "space")
+        _pa_bound.arbiter_inputs(), _pa_bound._optimization_result, _PA_T0, "space", boosted=False)
 
 
 _pa_bound_at = _pa_bound_target(21.0 + _pa.SETPOINT_TOLERANCE)
@@ -63462,17 +63462,131 @@ for _pa_gb_mode in ("boost", "comfort"):
     _pa_gb[_pa_gb_mode]._mode = _pa_gb_mode
     _pa_run(_pa_gb[_pa_gb_mode], 1)
 R.check(
-    "the global boost mode writes Heating + DHW and the heating flow; comfort keeps the baseline's hold",
+    "the global boost mode writes Heating + DHW and the set-point entity's maximum, 63 "
+    "(R10-HOTFIX-BOOST-FLOW-CEILING); comfort keeps the baseline's hold",
     ("select", "select_option", "Heating + DHW") in _pa_gb["boost"].writes()
-    and ("number", "set_value", 55.0) in _pa_gb["boost"].writes()
+    and ("number", "set_value", 63.0) in _pa_gb["boost"].writes()
     and ("number", "set_value", 35.0) in _pa_gb["comfort"].writes(),
     f"{_pa_gb['boost'].writes()} / {_pa_gb['comfort'].writes()}",
 )
+
+
+# R10-HOTFIX-BOOST-FLOW-CEILING (tvofi, 2026-11-13: a space boost wrote 41,
+# then 43, not his maximum; "set at the maximum value"): a boost replaces the
+# plan's power for the space channel (boost.overlay), so it writes the
+# set-point entity's own maximum on every step, a partial one included,
+# capped by a stored flow_heat_c and the controller's upper-limit sensor. An
+# entity whose maximum does not read, or reads above FLOW_HEAT_C_MAX, keeps
+# the planned level. The band is ready here (max_electrical_power set), which
+# the idle-plan check above never needed.
+def _pa_boost_level(duties, kw, how=None, power_meter=False, entity_max=60, option=None, limit=None, unit="flow"):
+    """The space writes of one pass on a plan booking ``kw`` on its space steps, band 0.4-2.0 kW.
+
+    ``how``: None, ``"channel"`` (Boost Space Heating) or ``"mode"`` (the global boost mode).
+    ``entity_max``: the set-point entity's ``max`` attribute, None for none.
+    """
+    coord = _PaCoord(_PA_TUYA, duties=duties)
+    attrs = {"min": 25} if entity_max is None else {"min": 25, "max": entity_max}
+    coord.hass.states.set("number.water_set", FakeState("40", attributes=attrs))
+    coord._optimization_result.power_schedule = [kw if c == "s" else 0.0 for c in duties]
+    coord._thermal_params = _PaNS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None,
+                                  min_electrical_power=0.4, max_electrical_power=2.0)
+    extra = {"space_setpoint_unit": unit}
+    if option is not None:
+        extra["flow_heat_c"] = option
+    if limit is not None:
+        extra["space_setpoint_high_limit_entity"] = "sensor.hp_high_limit"
+        coord.hass.states.set("sensor.hp_high_limit", FakeState(str(limit), unit="°C"))
+    if power_meter:
+        extra.update({"heat_pump_power_entity": "sensor.hp_power", "space_setpoint_power_feedback": True})
+    with_config(coord, extra)
+    if how == "channel":
+        boost_mod.held_for(coord).set("space", True, _PA_T0)
+    elif how == "mode":
+        coord._mode = "boost"
+    _pa_run(coord, 1)
+    return coord, [v for d, _sv, v in coord.writes() if d == "number" and v != 48.0]
+
+
+def _pa_bl(how, **kw):
+    return _pa_boost_level("ss", 1.0, how, **kw)[1]
+
+
+_pa_bl_rows = {
+    name: {how: _pa_bl(how, **kw) for how in (None, "channel", "mode")}
+    for name, kw in {
+        "max 55": {"entity_max": 55},
+        "max 60": {"entity_max": 60},
+        "max 70, the bound": {"entity_max": 70},
+        "max 60, stored 50": {"entity_max": 60, "option": 50},
+        "max 60, stored default 55": {"entity_max": 60, "option": 55},
+        "max 60, limit 52": {"entity_max": 60, "limit": 52},
+        "max 60, limit at the gate": {"entity_max": 60, "limit": 25},
+        "max 90": {"entity_max": 90},
+        "no max": {"entity_max": None},
+        "return, max 45": {"entity_max": 45, "unit": "return"},
+    }.items()
+}
+_pa_bl_idle = {how: _pa_boost_level("--", 0.0, how)[1] for how in (None, "channel", "mode")}
+_pa_bl_top = {how: _pa_boost_level("ss", 2.0, how)[1] for how in (None, "channel", "mode")}
+_pa_bl_want = {"max 55": 55, "max 60": 60, "max 70, the bound": 70, "max 60, stored 50": 50, "max 60, stored default 55": 60,
+               "max 60, limit 52": 52,
+               "max 60, limit at the gate": 60, "return, max 45": 45}
+R.check(
+    "R10-HOTFIX-BOOST-FLOW-CEILING: a space boost and the global boost mode write the set-point entity's "
+    "own maximum on a step the plan books at a partial 1.0 kW of a 0.4-2.0 kW band (55 for 55, 60 for 60, "
+    "70 for 70, FLOW_HEAT_C_MAX itself, "
+    "45 for a return target's 45, unmoved), capped by a flow_heat_c set off its default (50, never the "
+    "default 55, which an untouched page reads as) and the controller's "
+    "upper-limit sensor (52), never by a limit at the 25 degC gate, which leaves no heating value; controls: "
+    "the same step with no boost writes its partial value, below each of them, and an entity maximum of 90 "
+    "or none leaves a boost on that partial value",
+    all(_pa_bl_rows[name]["channel"] == [want] and _pa_bl_rows[name]["mode"] == [want]
+        and len(_pa_bl_rows[name][None]) == 1 and _pa_bl_rows[name][None][0] < want
+        for name, want in _pa_bl_want.items())
+    and all(_pa_bl_rows[name]["channel"] == _pa_bl_rows[name]["mode"] == _pa_bl_rows[name][None]
+            and len(_pa_bl_rows[name][None]) == 1 and _pa_bl_rows[name][None][0] < 55
+            for name in ("max 90", "no max")),
+    f"{_pa_bl_rows=}",
+)
+R.check(
+    "R10-HOTFIX-BOOST-FLOW-CEILING: on an idle plan and a band-top plan a boost writes the entity's "
+    "maximum, 60; null control: with no boost a band-top step writes the heating flow, 55, and an idle "
+    "one the gate, 25",
+    _pa_bl_idle == {None: [25], "channel": [60], "mode": [60]}
+    and _pa_bl_top == {None: [55], "channel": [60], "mode": [60]},
+    f"{_pa_bl_idle=} {_pa_bl_top=}",
+)
+from heatpump_optimizer import config_flow as _pa_cf  # noqa: E402
+from heatpump_optimizer.const import FLOW_HEAT_C_MAX as _PA_FLOW_HEAT_C_MAX  # noqa: E402
+
+_pa_bl_offer = [row.widget.config for row in _pa_cf._OPTION_FIELDS if row.key == "flow_heat_c"]
+R.check(
+    "R10-HOTFIX-BOOST-FLOW-CEILING: the heating ceiling the options offer is 30 to FLOW_HEAT_C_MAX, "
+    "70 degC, the range docs/configuration.md states and the bound above which a boost does not drive "
+    "an entity's maximum; null control: a maximum of 90 is above it",
+    [(c["min"], c["max"]) for c in _pa_bl_offer] == [(30, _PA_FLOW_HEAT_C_MAX)] and _PA_FLOW_HEAT_C_MAX == 70.0
+    and 90 > _PA_FLOW_HEAT_C_MAX,
+    f"{_pa_bl_offer=}",
+)
+_pa_bl_fb, _ = _pa_boost_level("ss", 1.0, "channel", power_meter=True)
+_pa_bl_fb_on = _pa._feedback_on(_pa_bl_fb.arbiter_inputs(), "space", _PA_T0 + timedelta(minutes=1),
+                                boost_mod.held_for(_pa_bl_fb))
+_pa_bl_nb, _ = _pa_boost_level("ss", 1.0, None, power_meter=True)
+_pa_bl_nb_on = _pa._feedback_on(_pa_bl_nb.arbiter_inputs(), "space", _PA_T0 + timedelta(minutes=1),
+                                boost_mod.held_for(_pa_bl_nb))
+R.check(
+    "R10-HOTFIX-BOOST-FLOW-CEILING: the power-feedback loop stays off during a space boost; "
+    "null control: on the same partial step with no boost it is on",
+    _pa_bl_fb_on is False and _pa_bl_nb_on is True,
+    f"{_pa_bl_fb_on=} {_pa_bl_nb_on=}",
+)
 R.check(
     "a boost writes its own single duty where the pump offers it, Heating + DHW "
-    "where it does not or the other duty is due too, and nothing while off",
+    "where it does not or the other duty is due too, and nothing while off; a space boost "
+    "writes the set-point entity's maximum, 63 (R10-HOTFIX-BOOST-FLOW-CEILING)",
     ("select", "select_option", "Heating") in _pa_sb["tuya"].writes()
-    and ("number", "set_value", 55.0) in _pa_sb["tuya"].writes()
+    and ("number", "set_value", 63.0) in _pa_sb["tuya"].writes()
     and all(w[2] != "Heating + DHW" for w in _pa_sb["tuya"].writes())
     and ("select", "select_option", "Heat + DHW") in _pa_sb["modbus"].writes()
     and ("select", "select_option", "Heating + DHW") in _pa_sb["dhwstep"].writes()
@@ -63652,17 +63766,127 @@ def _pa_upgraded(reading):
 
 _pa_up, _pa_up_first, _pa_up_sent = _pa_upgraded("30")
 _pa_up_n, _pa_up_n_first, _pa_up_n_sent = _pa_upgraded("31")
+# Re-pinned by R10-HOTFIX-FLOW-SETPOINT-STUCK: this check pinned "the write
+# waits", which on an upgrade held every space write, boosts included, until a
+# person set the controller. The own write is still never the baseline; the
+# baseline row's hold (35 degC: the curve's 34.2 under the rated hold) is.
 R.check(
     "R10-ARBITER-OFF-RESTORE: a reading equal to the arbiter's own last write is never captured as "
-    "the baseline, and the write waits; null control: a reading of the person's own is captured, "
-    "written over, and restored on off",
-    _pa_up_first == [] and _pa_up_sent == 0 and _pa_space(_pa_up) == []
+    "the baseline: the baseline row's 35 is, and the write is sent; null control: a reading of the "
+    "person's own is captured, written over, and restored on off",
+    _pa_up_first == [25.0] and _pa_up_sent == 1 and _pa_space(_pa_up) == [35.0]
     and _pa_up_n_first == [25.0] and _pa_up_n_sent == 1 and _pa_space(_pa_up_n) == [31.0],
     f"{_pa_up_first=} {_pa_up_sent=} {_pa_up.writes()=} / {_pa_up_n_first=} {_pa_up_n_sent=} "
     f"{_pa_up_n.writes()=}",
 )
 
 
+# R10-HOTFIX-FLOW-SETPOINT-STUCK (tvofi, 2026-11-13, a Rotenso on v7.1.15 held
+# at 25 degC through a boost): from any persisted arbiter state, a space step
+# or a boost under Control writes the space set-point within one pass. The
+# states: a record equal to the reading with no baseline armed, in memory and
+# loaded from the pre-#3404 store shape (an upgrade, then a restart).
+def _pa_stuck(duties, record, boost=False, stored=False):
+    """The space writes of one pass at minute 1; ``record`` the persisted last write or None."""
+    coord = _PaCoord(_PA_TUYA, duties=duties)
+    coord.device("number.water_set", "25")
+    at = _PA_T0 - timedelta(hours=1)
+    if record is not None and stored:
+        _pa_aio.run(_pa._store(coord).async_save({"written": {"space_setpoint": [record, at.isoformat()]}}))
+    elif record is not None:
+        held = _pa.state_for(coord)
+        held.loaded = True
+        held.written["space_setpoint"] = (record, at)
+    if boost:
+        boost_mod.held_for(coord).set("space", True, _PA_T0)
+    _pa_run(coord, 1)
+    return _pa_space(coord)
+
+
+_pa_stuck_rows = {
+    (duties, boost, stored): _pa_stuck(duties, 25.0, boost, stored)
+    for duties, boost in (("-", True), ("s", False)) for stored in (False, True)
+}
+_pa_stuck_null = {(duties, boost): _pa_stuck(duties, None, boost) for duties, boost in (("-", True), ("s", False))}
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK: a boost over an idle step writes the entity's 63 maximum "
+    "(R10-HOTFIX-BOOST-FLOW-CEILING), and a space step the 55 degC ceiling, in one pass from a persisted "
+    "own write of 25 equal to the reading with no baseline armed, in memory and loaded from the store; "
+    "null control: the same passes with no record write the same",
+    all(v == ([63.0] if key[1] else [55.0]) for key, v in _pa_stuck_rows.items())
+    and _pa_stuck_null == {("-", True): [63.0], ("s", False): [55.0]},
+    f"{_pa_stuck_rows=} {_pa_stuck_null=}",
+)
+
+
+def _pa_stuck_off(hand=None):
+    """Off after the released write from a persisted own 25: what the restore writes.
+
+    ``hand``: a value the person sets at the controller before the pass.
+    """
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (25.0, _PA_T0 - timedelta(hours=1))
+    coord.device("number.water_set", "25" if hand is None else hand)
+    _pa_settled(coord, 1)
+    return _pa_turn_off(coord), _pa_space(coord)
+
+
+
+
+def _pa_stuck_cycle():
+    """A stuck install (own 25 persisted, reading 25, nothing armed) turned Off and On again.
+
+    Returns what the Off restored, the space writes after On, and what a later Off restores.
+    """
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (25.0, _PA_T0 - timedelta(hours=1))
+    coord.device("number.water_set", "25")
+    first = _pa_turn_off(coord)
+    coord._mode = _PA_AUTO
+    coord.hass.services.calls.clear()
+    _pa_settled(coord, 46)
+    coord.hass.services.calls.clear()
+    _pa_run(coord, 47)
+    on = _pa.state_for(coord).written.get("space_setpoint", (None,))[0]
+    coord.hass.services.calls.clear()
+    return first, on, _pa_turn_off(coord), _pa_space(coord)
+
+
+def _pa_dropped_over(written, dropped):
+    """The space writes of three passes from a written record over a dropped own 25, reading 25."""
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (written, _PA_T0 - timedelta(hours=1))
+    held.dropped["space_setpoint"] = dropped
+    coord.device("number.water_set", "25")
+    for minute in (1, 2, 3):
+        _pa_settled(coord, minute)
+    return float(coord.hass.states.get("number.water_set").state)
+
+
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK (R10-RCA-SETPOINT-LATCH-DEADLOCK (b)): a stuck install turned Off "
+    "(nothing armed, nothing restored) and On writes 55 at once, and a later Off restores the baseline "
+    "row's 35, never the 25 the optimizer left; (c): a written 55 over a dropped own 25 with the entity "
+    "reading 25 reaches 55; null control: a dropped 40 that is not the reading reaches 55 too",
+    _pa_stuck_cycle() == (0, 55.0, 1, [35.0])
+    and _pa_dropped_over(55.0, 25.0) == 55.0 and _pa_dropped_over(55.0, 40.0) == 55.0,
+    f"{_pa_stuck_cycle()=} {_pa_dropped_over(55.0, 25.0)=} {_pa_dropped_over(55.0, 40.0)=}",
+)
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK: Optimizer off after the write a persisted own 25 no longer holds "
+    "restores the baseline row's 35, never the 25 gate; null control: a value set by hand, 40, is "
+    "restored as set",
+    _pa_stuck_off() == (1, [35.0]) and _pa_stuck_off("40") == (1, [40.0]),
+    f"{_pa_stuck_off()=} {_pa_stuck_off('40')=}",
+)
+
+
 def _pa_between(reading, switch_off=False, then=None):
     """Baseline 53; the gate 25, then a space step's target; then the entity reads ``reading``.
 
@@ -63811,13 +64035,17 @@ def _pa_restored_twice(via):
     _pa_run(again, 0)
     _pa_run(again, 30)
     again.hass.services.calls.clear()
-    return _pa_turn_off(again)
+    return _pa_turn_off(again), _pa_space(again)
 
 
+# The restored value, not only the count: since R10-HOTFIX-FLOW-SETPOINT-STUCK
+# an own write left on the record no longer refuses the arm but substitutes
+# the baseline row's 35, so only the value tells a record the restore dropped
+# (and saved) from one it kept.
 R.check(
     "R10-ARBITER-OFF-RESTORE: after an off or an unload restored a baseline equal to the plan's value, "
-    "a restart captures it again and the next off restores it",
-    _pa_restored_twice("unload") == 1 and _pa_restored_twice("off") == 1,
+    "a restart captures it again and the next off restores it, 25, not the baseline row's 35",
+    _pa_restored_twice("unload") == (1, [25.0]) and _pa_restored_twice("off") == (1, [25.0]),
     f"{_pa_restored_twice('unload')=} {_pa_restored_twice('off')=}",
 )
 _pa_subs = _PaCoord(_PA_TUYA)
@@ -88193,7 +88421,7 @@ R.check(
 import asyncio as _fb_aio  # noqa: E402
 
 
-def _fb_own(moves, wrote=True):
+def _fb_own(moves, wrote=True, arm=True):
     coord = _FbCoord()
     held = _fb_pa.state_for(coord)
     if wrote:
@@ -88201,23 +88429,35 @@ def _fb_own(moves, wrote=True):
         held.feedback = _fb_running(3600, 0)
     for target in moves:
         _fb_pa._note_sent(held, held.feedback, target, 26.4)
-    sent = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET))
+    sent = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET, _FB_NOW)) if arm else None
     return sent, coord, held
 
 
+def _fb_baseline(coord):
+    """The space baseline the off restore holds, or None when unarmed."""
+    armed = _fb_aio.run(_pa_or.async_armed_entry(coord.hass, coord.entry, _fb_pa.CONSUMER))
+    return None if armed is None else armed["value"]
+
+
+# Re-pinned by R10-HOTFIX-FLOW-SETPOINT-STUCK: the own write is no longer
+# refused, which held the write; the baseline row's 30.0 (the rated 35 in
+# return terms, under the 32 ceiling) is captured in its place.
 _fb_own_one, _fb_own_two, _fb_own_none = _fb_own([25.8]), _fb_own([25.8, 25.6]), _fb_own([], wrote=False)
 _fb_rs_coord, _fb_rs_held = _fb_own([25.8])[1:]
 _fb_rs_coord.entry.runtime_data = _fb_rs_coord
 _fb_pa._space_restored(_fb_rs_coord.entry, _FB_SET, 26.0)
 R.check(
     "R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK (Carry 8): a loop move's "
-    "dropped record still refuses the optimizer's own 26.0 as an unarmed key's baseline, "
-    "after one move and after two with no write between; a restore ends the run; an "
-    "arbiter that never wrote captures it",
-    _fb_own_one[0] is False and _fb_own_two[0] is False and _fb_own_two[2].feedback.prev_c == 26.0
-    and _fb_rs_held.feedback is None and _fb_own_none[0] is True,
-    f"one {_fb_own_one[0]}, two {_fb_own_two[0]} (prev {_fb_own_two[2].feedback.prev_c}), "
-    f"restored run {_fb_rs_held.feedback}, never wrote {_fb_own_none[0]}",
+    "dropped record still keeps the optimizer's own 26.0 from an unarmed key's baseline, "
+    "after one move and after two with no write between, and the write is sent; a restore "
+    "ends the run; an arbiter that never wrote captures it",
+    _fb_own_one[0] is True and _fb_baseline(_fb_own_one[1]) == 30.0
+    and _fb_own_two[0] is True and _fb_baseline(_fb_own_two[1]) == 30.0
+    and _fb_own_two[2].feedback.prev_c == 26.0
+    and _fb_rs_held.feedback is None and _fb_own_none[0] is True and _fb_baseline(_fb_own_none[1]) == 26.0,
+    f"one {_fb_own_one[0]} {_fb_baseline(_fb_own_one[1])}, two {_fb_own_two[0]} {_fb_baseline(_fb_own_two[1])} "
+    f"(prev {_fb_own_two[2].feedback.prev_c}), restored run {_fb_rs_held.feedback}, "
+    f"never wrote {_fb_own_none[0]} {_fb_baseline(_fb_own_none[1])}",
 )
 # Round 2 of Carry 8 (#3404's verdict at 4a5abf4a): the loop run ends on
 # paths that are neither a write nor a restore -- a pass off the loop
@@ -88230,12 +88470,12 @@ R.check(
 
 
 def _fb_own_after(end):
-    sent, coord, held = _fb_own([25.8])
+    _sent, coord, held = _fb_own([25.8], arm=False)
     end(coord, held)
     held = _fb_pa.state_for(coord)  # a restart's is a fresh state
     run = held.feedback
-    after = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET))
-    return sent, None if run is None else run.prev_c, after
+    after = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET, _FB_NOW))
+    return _fb_baseline(coord), None if run is None else run.prev_c, after
 
 
 def _fb_end_stale(coord, held):
@@ -88265,29 +88505,32 @@ _fb_own_ends = {
 print("CARRY8-RUN-ENDS", _fb_own_ends)
 R.check(
     "R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK (Carry 8, round 2): the "
-    "own-write refusal survives every end of the loop run while the dropped write is "
-    "held -- an off pass, a missing base, a compressor stop, a stale run, a restart",
-    all(sent is False and prev is None and after is False for sent, prev, after in _fb_own_ends.values()),
-    f"(before, run prev_c after, after) {_fb_own_ends}",
+    "own-write fact survives every end of the loop run while the dropped write is "
+    "held -- an off pass, a missing base, a compressor stop, a stale run, a restart: "
+    "the arm after it sends the write and captures 30.0, not the own 26.0",
+    all(after is True and prev is None and baseline == 30.0 for baseline, prev, after in _fb_own_ends.values()),
+    f"(baseline, run prev_c after, after) {_fb_own_ends}",
 )
 # Where the fact stops mattering or ends: once the person moves the
 # controller (25.0) the arm captures and the write lands, after which the
 # armed key never consults it -- the controller reading 26.0 again with the
-# record gone is not refused; a restore (_space_restored) and a release (Off
-# forgets the record, even one that is only the dropped write) end it, and
-# a stored value the arbiter could not have written is not loaded.
+# record gone is not refused; a restore (_space_restored) ends it, and a
+# stored value the arbiter could not have written is not loaded. Re-pinned by
+# R10-HOTFIX-FLOW-SETPOINT-STUCK: Off with no restore no longer ends it (the
+# entity still reads the optimizer's number, and the arm after On must not
+# take it as the person's), and a written record becomes the dropped one.
 # Control: before each, the fact is held.
-_fb_wr_sent, _fb_wr_coord, _fb_wr_held = _fb_own([25.8])
+_fb_wr_sent, _fb_wr_coord, _fb_wr_held = _fb_own([25.8], arm=False)
 _fb_wr_before = dict(_fb_wr_held.dropped)
 _fb_wr_coord.hass.states.set(_FB_SET, FakeState("25.0", attributes={"min": 15, "max": 45, "step": 0.1}))
 _fb_aio.run(_fb_pa._write(_fb_wr_coord, _fb_wr_coord.arbiter_inputs(), "space_setpoint", 25.8, _FB_NOW))
 _fb_wr_written = _fb_wr_held.written.pop("space_setpoint", (None,))[0]
 _fb_wr_coord.hass.states.set(_FB_SET, FakeState("26.0", attributes={"min": 15, "max": 45, "step": 0.1}))
-_fb_wr_after = _fb_aio.run(_fb_pa._arm_space(_fb_wr_coord.arbiter_inputs(), _fb_wr_coord.entry, _fb_wr_held, _FB_SET))
+_fb_wr_after = _fb_aio.run(_fb_pa._arm_space(_fb_wr_coord.arbiter_inputs(), _fb_wr_coord.entry, _fb_wr_held, _FB_SET, _FB_NOW))
 _fb_junk = _FbCoord()
 _fb_aio.run(_fb_pa._store(_fb_junk).async_save({"written": {}, "dropped": {"space_setpoint": "26.0 degC"}}))
 _fb_aio.run(_fb_pa._load(_fb_junk))
-_fb_off_coord, _fb_off_held = _fb_own([25.8])[1:]
+_fb_off_coord, _fb_off_held = _fb_own([25.8], arm=False)[1:]
 _fb_off_held.written.clear()
 _fb_off_before = dict(_fb_off_held.dropped)
 _fb_off_coord._mode = _PA_OFF
@@ -88295,11 +88538,11 @@ _fb_aio.run(_fb_pa._arbitrate(_fb_off_coord, _fb_off_held, _fb_off_coord.arbiter
                               _fb_pa.DUTY_CONTROL, _FB_NOW))
 R.check(
     "R10-ARBITER-OFF-RESTORE (Carry 8, round 2): the dropped own write is not consulted "
-    "once a write lands on the armed key, and ends when a restore writes the baseline or "
-    "Off releases the pump",
+    "once a write lands on the armed key, and ends when a restore writes the baseline; "
+    "Off with nothing restored keeps it",
     _fb_wr_before == {"space_setpoint": 26.0} and _fb_wr_written == 25.8 and _fb_wr_after is True
     and _fb_rs_held.dropped == {}
-    and _fb_off_before == {"space_setpoint": 26.0} and _fb_off_held.dropped == {}
+    and _fb_off_before == {"space_setpoint": 26.0} and _fb_off_held.dropped == {"space_setpoint": 26.0}
     and _fb_pa.state_for(_fb_junk).dropped == {},
     f"write {_fb_wr_before}, wrote {_fb_wr_written}, armed after {_fb_wr_after}, "
     f"restore {_fb_rs_held.dropped}, off {_fb_off_before} -> {_fb_off_held.dropped}, "
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
similarity index 60%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
index 3c3cb57df3..7674632b2b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 59013da4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 87a4cba9",
   "killed_by": "tests/features.py",
-  "old": "        if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if held.written or held.retry or held.space_before is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
new file mode 100644
index 0000000000..d52a0f3f66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space GUARD_OFF bc2b348d",
+  "killed_by": "tests/features.py",
+  "old": "    if own:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
index f29be90584..eedc551b94 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL cbe69d47",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL ee5d5b70",
   "killed_by": "tests/features.py",
-  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
new file mode 100644
index 0000000000..a7763a6b16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.BOOLOP.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c BOOLOP e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limit is not None or limit > _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
new file mode 100644
index 0000000000..3aeba63c75
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if limit is not None and limit >= _gate_floor_c(inp.config):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json
new file mode 100644
index 0000000000..ec2e05c85a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.0cd5c442.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF 0cd5c442",
+  "killed_by": "tests/features.py",
+  "old": "    if (ceiling := _heat_ceiling_c(inp.config)) != DEFAULT_FLOW_HEAT_C:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json
new file mode 100644
index 0000000000..3070a5af12
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.c89e426b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF c89e426b",
+  "killed_by": "tests/features.py",
+  "old": "    if high is None or not _gate_floor_c(inp.config) < high <= FLOW_HEAT_C_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
new file mode 100644
index 0000000000..7127158872
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.GUARD_OFF.e74f8c8c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c GUARD_OFF e74f8c8c",
+  "killed_by": "tests/features.py",
+  "old": "    if limit is not None and limit > _gate_floor_c(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json
new file mode 100644
index 0000000000..fc06916701
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_boost_ceiling_c.RETURN_DEL.2985261d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c RETURN_DEL 2985261d",
+  "killed_by": "tests/features.py",
+  "old": "    return min(caps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
index d5ce21b72b..6150d6a294 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP 605f504a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP dd8cf122",
   "killed_by": "tests/guard_pins.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity, now)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
index 9a74fc5f22..febd8f790b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL 605f504a",
-  "killed_by": "tests/structure.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL dd8cf122",
+  "killed_by": "tests/features.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json
new file mode 100644
index 0000000000..4538077c43
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.b06f8296.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw GUARD_OFF b06f8296",
+  "killed_by": "tests/features.py",
+  "old": "    if boosted:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json
new file mode 100644
index 0000000000..3b8a2da6c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.GUARD_OFF.eee8dcd8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw GUARD_OFF eee8dcd8",
+  "killed_by": "tests/features.py",
+  "old": "    if (kw := _experiment_kw(inp)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json
new file mode 100644
index 0000000000..b6e67a4cb0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_level_kw.RETURN_DEL.1e8ade07.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_level_kw RETURN_DEL 1e8ade07",
+  "killed_by": "tests/features.py",
+  "old": "    return _step_kw(inp.plan, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
new file mode 100644
index 0000000000..1ef3907eac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_own_space_write RETURN_DEL 98fa5cc9",
+  "killed_by": "tests/features.py",
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json
deleted file mode 100644
index 2aa98ee949..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.268586e3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_space_target RETURN_DEL 268586e3",
-  "killed_by": "tests/structure.py",
-  "old": "        return _flow_target(inp, duty, now)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against e5f7e169d64b93d4ae117eb07c68ecef6d47aea6: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json
new file mode 100644
index 0000000000..0ad0ed51fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_space_target.RETURN_DEL.628d75e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_space_target RETURN_DEL 628d75e4",
+  "killed_by": "tests/features.py",
+  "old": "        return _flow_target(inp, duty, now, boosted=boosted)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
index b541e26d05..3a07eb6ceb 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/desired.GUARD_OFF.0082e8a4.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:desired GUARD_OFF 0082e8a4",
   "killed_by": "tests/features.py",
   "old": "    if _flow_unit(inp.config):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cbb8a2712fef67b4719309fa01396706e66148bc: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Re-measured on a git-archive export of 13a82a9d, 2026-10-05: 3 of 3698 feature checks fail, against the export baseline's two artefacts (#363 recorded_at, R9-F2.1 P3). Re-keyed by R9-EG-B6 (#1739): the collaborator-interface rename made the line `    if _flow_unit(coord._config):` into `    if _flow_unit(inp.config):`."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
 }
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json
new file mode 100644
index 0000000000..4aa62e7c56
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_boost_ceiling_c CMP_BOUND c89e426b",
+  "old": "    if high is None or not _gate_floor_c(inp.config) < high <= FLOW_HEAT_C_MAX:",
+  "reason": "Equivalent (CMP_BOUND on the first comparator, `_gate_floor_c(...) < high` -> `<=`): the two arms differ only at an entity maximum exactly equal to the gate, where the boost either writes min(high, ...) = the gate or keeps the planned level; the entity's own range (`_bounded`) clamps every heating write on that entity to its maximum, the gate, so both arms write the same value on every input. Measured by the R10-HOTFIX-BOOST-FLOW-CEILING repair seat's `mutation_table.py --pin-killed --base origin/main` (tests/features.py, tests/config_flow_steps.py, tests/guard_pins.py): the site lived while the anchor's other comparator (`<= FLOW_HEAT_C_MAX` -> `<`) is killed by the arbiter block's `max 70, the bound` row, and the same line's GUARD_OFF is pinned (killed by tests/features.py).",
+  "verdict": "equivalent"
+}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
