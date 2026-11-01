# Review packet #3078
head: ee29ed568e2701badacfb4febff27a7834ff1d04
base: 25c46e76e2d7fe504a457a145cadbce33c773662

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125000782197 neutral
arch-score / arch-score id=125000581050 success
arm id=125000474744 skipped
budget-raise-gate / budget-raise-gate id=125000581455 success
cancel-superseded id=125000479395 success
codeql / Analyze (actions) id=125000581109 success
codeql / Analyze (javascript-typescript) id=125000581058 success
codeql / Analyze (python) id=125000581047 in_progress
governance / delivery-status id=125000581374 success
governance / delivery-status-publish id=125000582670 skipped
governance / env-matrix id=125000581204 in_progress
governance / instrument-self-tests id=125000581205 in_progress
governance / policy-docs id=125000581130 success
governance / record id=125000582353 skipped
governance / wave-script id=125000581219 success
hassfest / hassfest id=125000580978 success
kernel-points id=125000582595 skipped
prelude id=125000479228 success
refresh id=125000479240 success
tests / arch-instrument id=125000687299 success
tests / briefs id=125000581408 success
tests / browser id=125000687360 in_progress
tests / closure-scope id=125000581322 success
tests / closures id=125000687341 in_progress
tests / coverage id=125000687240 in_progress
tests / fast (3.14) id=125000687293 in_progress
tests / mutation id=125000581256 in_progress
tests / nightly-ha id=125000688474 skipped
tests / nightly-status id=125000581330 success
tests / replay id=125000687320 in_progress
tests / typing id=125000687239 success
validate / validate-hacs id=125000581094 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item f2da9546: R10-REPLAY-COST-BUDGET
NOTE body item fe624911: R10-LIVE-BUNDLE-READS
NOTE body item b78ae234: R10-USER-DOCS-VERIFY
NOTE body item 2a5882d0: dismissed:disclosed design trade with its control
NOTE body item 6740c973: dismissed:no seat holds the export
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/replay.py
             `tests/replay.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json
new file mode 100644
index 000000000..48fe278bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings BOOLOP 1af5d1b5",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if text and secret:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if text or secret:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json
new file mode 100644
index 000000000..81ca93fd2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF 1af5d1b5",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if text and secret:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json
deleted file mode 100644
index 7e72b50c8..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF c831c60b",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if text and (secret or (isinstance(node, str) and not text_ok(node))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json
new file mode 100644
index 000000000..1f249bbcc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF d8e39501",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        elif text and isinstance(node, str) and not text_ok(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json b/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json
new file mode 100644
index 000000000..34a0a4d23
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_copy RETURN_DEL d004bc2e",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return re.compile(rf\"(?<![A-Za-z0-9]){re.escape(value)}(?![A-Za-z0-9])\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json
new file mode 100644
index 000000000..889fd1d7b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids BOOLOP c4fcf654",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, str) or ENTITY_ID.match(node):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json
new file mode 100644
index 000000000..4059e18fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF 50e92e5d",
+  "killed_by": "tests/entities.py",
+  "old": "    elif isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json
new file mode 100644
index 000000000..3c4e29f3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF bc1e8661",
+  "killed_by": "tests/entities.py",
+  "old": "    elif isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json
new file mode 100644
index 000000000..7482b5f00
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF c4fcf654",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json
new file mode 100644
index 000000000..f445fdb4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids RETURN_DEL b954b2d8",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return into",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json
new file mode 100644
index 000000000..dc8cf10be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entry_shape BOOLOP aa32e007",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(value, str) and re.search(r\"\\s\", value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(value, str) or re.search(r\"\\s\", value):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json
new file mode 100644
index 000000000..7dc016f98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entry_shape GUARD_OFF aa32e007",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(value, str) and re.search(r\"\\s\", value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json
new file mode 100644
index 000000000..1fc94975d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_hit GUARD_OFF 320a5d6d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if copy.search(text):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json
new file mode 100644
index 000000000..a0fba7bcb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_no_credential RETURN_DEL e8b4342c",
+  "killed_by": "tests/entities.py",
+  "old": "    return isinstance(value, bool) or value in (None, \"\", [], {})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json
new file mode 100644
index 000000000..54e2a6fd1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan BOOLOP c5354b16",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if path == \"states\" and isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if path == \"states\" or isinstance(node, dict):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json
new file mode 100644
index 000000000..8a8aa9251
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF 08da69e4",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json
new file mode 100644
index 000000000..37746fc75
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF b9435854",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json
new file mode 100644
index 000000000..a601e1033
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF c5354b16",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if path == \"states\" and isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json
new file mode 100644
index 000000000..7de01a750
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan RETURN_DEL a0419929",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return _scan_leaf(node, path, found, creds)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json
new file mode 100644
index 000000000..c06bdcebb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf BOOLOP 33a88808",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, (int, float)) and not isinstance(node, bool):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, (int, float)) or not isinstance(node, bool):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json
new file mode 100644
index 000000000..9c2780201
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf GUARD_OFF 33a88808",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, (int, float)) and not isinstance(node, bool):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json
new file mode 100644
index 000000000..3938d2499
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf GUARD_OFF d5257eac",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, str) and not ISO_TIME.match(node) and any(c.search(node) for c in creds):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json
new file mode 100644
index 000000000..bf6ed8638
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf RETURN_DEL b20e5b2d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return node",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json
new file mode 100644
index 000000000..ec3b40699
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_unmasked BOOLOP 48930130",
+  "killed_by": "tests/debug_collect.py",
+  "old": "                   if not HASHED_ID.match(i) and roles.get(i) != i), key=len, reverse=True)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not HASHED_ID.match(i) or roles.get(i) != i), key=len, reverse=True)`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json
new file mode 100644
index 000000000..348c084e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_unmasked GUARD_OFF 14f861a9",
+  "killed_by": "tests/entities.py",
+  "old": "    if not isinstance(payload, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=51."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json
deleted file mode 100644
index 841be3746..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk BOOLOP 5476d757",
-  "killed_by": "tests/debug_collect.py",
-  "old": "            if SECRET_KEY.search(str(key)) and value not in (None, \"\", [], {}):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: BOOLOP (`if SECRET_KEY.search(str(key)) or value not in (None, \"\", [], {}):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json
new file mode 100644
index 000000000..3eb622024
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk BOOLOP 7cfc611c",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if SECRET_KEY.search(str(key)) and not _no_credential(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if SECRET_KEY.search(str(key)) or not _no_credential(value):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json
deleted file mode 100644
index 5e4d2ec11..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk GUARD_OFF 5476d757",
-  "killed_by": "tests/entities.py",
-  "old": "            if SECRET_KEY.search(str(key)) and value not in (None, \"\", [], {}):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json
new file mode 100644
index 000000000..8e7f0cec6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk GUARD_OFF 7cfc611c",
+  "killed_by": "tests/structure.py",
+  "old": "            if SECRET_KEY.search(str(key)) and not _no_credential(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
new file mode 100644
index 000000000..c3450f3d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
+  "killed_by": "tests/entities.py",
+  "old": "            if isinstance(value, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json
new file mode 100644
index 000000000..9d8dd3186
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles RETURN_DEL 24126f41",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return roles",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json
new file mode 100644
index 000000000..53fa0a2f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles.claim GUARD_OFF 801db476",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(eid, str) and ENTITY_ID.match(eid) and eid not in roles:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json
new file mode 100644
index 000000000..724698461
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles.claim GUARD_OFF f1238e21",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if rid not in roles.values():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json b/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json
new file mode 100644
index 000000000..8286e5783
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:hashed_id RETURN_DEL f8942d60",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return f\"{entity_id.split('.', 1)[0]}.e_{digest[:10]}\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json
new file mode 100644
index 000000000..243733628
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids RETURN_DEL f7fb6f10",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return cast(Json, rename(doc))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json
new file mode 100644
index 000000000..a38deb5db
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename BOOLOP 497676f1",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, str) or ENTITY_ID.match(node):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json
new file mode 100644
index 000000000..799de000a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF 497676f1",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json
new file mode 100644
index 000000000..4dbe9dfb4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF b78e27c0",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json
new file mode 100644
index 000000000..0eac08b0d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF c41f3797",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json
new file mode 100644
index 000000000..306e428c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename RETURN_DEL 7139a494",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        return node",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json
new file mode 100644
index 000000000..c5c9d63bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_violations GUARD_OFF 71e0616b",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if not left:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json
new file mode 100644
index 000000000..569a04f4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:refusals RETURN_DEL a8227ccf",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json
deleted file mode 100644
index 91506594f..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal BOOLOP b11cce2f",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS and s in blob})",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS or s in blob})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json
new file mode 100644
index 000000000..02d27bb97
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal CMP_BOUND 61a9917d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "                    and len(s) >= LEAK_MIN_CHARS and s.lower() not in STATE_WORDS})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and len(s) > LEAK_MIN_CHARS and s.lower() not in STATE_WORDS})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json
deleted file mode 100644
index 5e4c39ecd..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal CMP_BOUND b11cce2f",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS and s in blob})",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`leaked = sorted({s for s in dropped if len(s) > LEAK_MIN_CHARS and s in blob})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json
new file mode 100644
index 000000000..8f5e34b1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal GUARD_OFF 3d96d616",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if found:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json
deleted file mode 100644
index ea569d0a8..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal GUARD_OFF 43b78c97",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if leaked:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json b/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json
deleted file mode 100644
index cd0f90e2d..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:text_ok BOOLOP aa6ef607",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return bool(LABEL.match(value)) and not re.search(r\"\\d{4}\", value)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: BOOLOP (`return bool(LABEL.match(value)) or not re.search(r\"\\d{4}\", value)`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json b/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json
deleted file mode 100644
index bdc1faaba..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:text_ok RETURN_DEL aa6ef607",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return bool(LABEL.match(value)) and not re.search(r\"\\d{4}\", value)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/replay_doc.py b/custom_components/heatpump_optimizer/replay_doc.py
index 9cc384d97..d177af2c3 100644
--- a/custom_components/heatpump_optimizer/replay_doc.py
+++ b/custom_components/heatpump_optimizer/replay_doc.py
@@ -13,9 +13,22 @@ library and nothing else -- no ``homeassistant``, no sibling module.
 WHAT IT KEEPS is an allowlist, because the file goes into a public
 repository; ``tools/replay/export.py``'s docstring states it, with what it
 cannot remove.
+
+EVERY ENTITY ID IS MASKED (``mask_ids``), because an id can embed the home's name
+or street address -- the Tibber price sensor's is derived from the home's
+address. ``document`` renames each id through one mapping: an id the entry
+holds under a key becomes ``<domain>.<role>``, the key less its ``_entity``
+suffix (``price_entity`` -> ``sensor.price``; the n-th of an ``_entities`` list
+``<domain>.<role>_n<n>``; the Tibber price series ``sensor.price``), and every
+other id a stable keyed hash, ``<domain>.e_<10 hex>``. ``refusals`` refuses a
+document still holding an id the mapping did not produce, and any text that
+looks like a street address (a word, then a house number); its messages name
+the class, never the id or the token.
 """
 from __future__ import annotations
 
+import hashlib
+import hmac
 import json
 import re
 from collections.abc import Callable, Iterable, Mapping
@@ -78,6 +91,13 @@ SERIES_TIME_KEYS = frozenset({"start", "end", "starts_at"})
 SERIES_VALUE_KEYS = frozenset({"value", "price", "total"})
 LABEL = re.compile(r"^[A-Za-z\u00b0][A-Za-z0-9 _+\-./()\u00b0%\u00b2\u00b3]{0,39}$")
 ISO_TIME = re.compile(r"^\d{4}-\d\d-\d\d([T ][\d:.]+([+-]\d\d:\d\d|Z)?)?$")
+#: A street address: a word of three letters or more, a space, underscore or
+#: hyphen, then a house number of up to four digits and an optional letter
+#: ("Storgatan 12", "exempelgatan_12b"). An entry string holding whitespace is
+#: free text (a name), dropped whatever it says.
+ADDRESS = re.compile(r"(?<![^\W\d_])[^\W\d_]{3,}[ _-]\d{1,4}(?:[ _]?[^\W\d_])?(?![^\W_])")
+#: An entity id ``mask_ids`` hashed: no role names it.
+HASHED_ID = re.compile(r"^[a-z_]+\.e_[0-9a-f]{10}$")
 
 # THE TIBBER PRICE SENSOR. With the Tibber source the integration fetches
 # prices itself, so the replay needs a recorded sensor whose state is the
@@ -99,6 +119,10 @@ PRICE_SOURCE_ENTITY = "entity"
 #: The shortest dropped value a leak check searches the rest of a payload for:
 #: a shorter one matches ordinary words and numbers by chance.
 LEAK_MIN_CHARS = 6
+#: Words Home Assistant writes as a state, which a device also writes under a
+#: credential-named attribute it cannot fill (``serial_number: unavailable``):
+#: no credential, and searching for one refuses every day an input went away.
+STATE_WORDS = frozenset({"unknown", "unavailable", "none", "null", "true", "false"})
 
 
 class Refused(ValueError):
@@ -193,7 +217,8 @@ def text_ok(value: str) -> bool:
         return "," not in value
     except ValueError:
         pass
-    return bool(LABEL.match(value)) and not re.search(r"\d{4}", value)
+    return (bool(LABEL.match(value)) and not re.search(r"\d{4}", value)
+            and not ADDRESS.search(value))
 
 
 def _is_coordinate(key: str) -> bool:
@@ -308,6 +333,8 @@ def _entry_shape(key: str, value: object) -> object:
         if isinstance(value, list):
             return [v for v in value if isinstance(v, str) and ENTITY_ID.match(v)]
         return _DROP
+    if isinstance(value, str) and re.search(r"\s", value):
+        return _DROP  # free text: a name, an address -- dropped, never masked
     return value
 
 
@@ -356,16 +383,24 @@ def sanitise(raw: Json, conf: frozenset[str], dropped: list[str]) -> Json:
     return cast(Json, clean_value(out, dropped))  # a dict cleans to a dict
 
 
+class Credential(str):
+    """A dropped value that sat under a credential-named key: its copy in a kept
+    string is dropped too, and a copy as a number refuses the document."""
+
+
 def _collect_strings(node: object, into: list[str], secret: bool = False) -> None:
-    """Collect what the leak check must not find again: every value under a
-    credential-named key, and every string that fails ``text_ok`` elsewhere.
+    """Collect what was dropped: every value under a credential-named key, as a
+    ``Credential`` the leak check must not find again, and every string that
+    fails ``text_ok`` elsewhere, counted only.
     A plain label dropped only for sitting under an unlisted key ("Hot water",
     a friendly name) may legitimately appear elsewhere, so it is not collected."""
     if isinstance(node, bool) or node is None:
         return
     if isinstance(node, (str, int, float)):
         text = str(node)
-        if text and (secret or (isinstance(node, str) and not text_ok(node))):
+        if text and secret:
+            into.append(Credential(text))
+        elif text and isinstance(node, str) and not text_ok(node):
             into.append(text)
     elif isinstance(node, dict):
         for key, value in node.items():
@@ -375,11 +410,17 @@ def _collect_strings(node: object, into: list[str], secret: bool = False) -> Non
             _collect_strings(value, into, secret)
 
 
+def _no_credential(value: object) -> bool:
+    """Nothing a credential-named key can leak: empty, or a bool -- a flag such as
+    ``tibber_reauth_started``, which ``_collect_strings`` skips too (D15-s1-04)."""
+    return isinstance(value, bool) or value in (None, "", [], {})
+
+
 def _walk(node: object, path: str, found: list[str]) -> None:
     if isinstance(node, dict):
         for key, value in node.items():
             here = f"{path}.{key}" if path else str(key)
-            if SECRET_KEY.search(str(key)) and value not in (None, "", [], {}):
+            if SECRET_KEY.search(str(key)) and not _no_credential(value):
                 found.append(f"{here}: a credential-named key carries a value")
             if _is_coordinate(key):
                 places = json_decimal_places(value)
@@ -390,11 +431,13 @@ def _walk(node: object, path: str, found: list[str]) -> None:
         for i, value in enumerate(node):
             _walk(value, f"{path}[{i}]", found)
     elif isinstance(node, str) and not text_ok(node):
-        found.append(f"{path}: text outside the allowlist")
+        found.append(f"{path}: " + ("an address-like token (a word, then a house number)"
+                                    if ADDRESS.search(node) else "text outside the allowlist"))
 
 
 def violations(payload: object, conf: frozenset[str] | None = None) -> list[str]:
-    """Every place ``payload`` breaks a rule. Empty means committable.
+    """Every place ``payload`` breaks a shape rule; ``refusals`` adds the mask's,
+    and empty there means committable.
 
     Without ``conf`` the entry's keys are judged by shape only; ``check_file``
     always passes the installed allowlist.
@@ -415,7 +458,9 @@ def _entry_violations(entry: Json, conf: frozenset[str] | None) -> list[str]:
             if (conf is not None and key not in conf) or not KEY.match(str(key)):
                 found.append(f"entry.{section}.{key}: not an entry key of this integration")
             elif _entry_shape(key, block[key]) != block[key]:
-                found.append(f"entry.{section}.{key}: must hold entity ids only")
+                found.append(f"entry.{section}.{key}: " + (
+                    "must hold entity ids only" if re.search(r"_entit(y|ies)$", key)
+                    else "free text"))
     return found
 
 
@@ -474,13 +519,117 @@ def state_rows(records: Iterable[tuple[Any, Any, Any, Any]]) -> list[list[Any]]:
     return rows
 
 
+# --- masking every entity id ---------------------------------------------------
+
+
+def entity_roles(entry: Json, price_series_entity: str | None) -> dict[str, str]:
+    """``{id: <domain>.<role>}`` for every id the entry holds under a key, options
+    before data, keys in order, then the price series as ``price``. An id keeps
+    its first role; a role a second id would take leaves that id to the hash."""
+    roles: dict[str, str] = {}
+
+    def claim(eid: object, role: str) -> None:
+        if isinstance(eid, str) and ENTITY_ID.match(eid) and eid not in roles:
+            rid = f"{eid.split('.', 1)[0]}.{role}"
+            if rid not in roles.values():
+                roles[eid] = rid
+
+    for section in ("options", "data"):
+        block = entry.get(section)
+        for key, value in sorted(block.items() if isinstance(block, dict) else ()):
+            role = re.sub(r"_entit(y|ies)$", "", str(key))
+            if isinstance(value, list):
+                for i, item in enumerate(value, start=1):
+                    claim(item, f"{role}_n{i}")
+            else:
+                claim(value, role)
+    for role in ("price", "price_series"):
+        claim(price_series_entity, role)
+    return roles
+
+
+def hashed_id(entity_id: str, key: str) -> str:
+    """``<domain>.e_<10 hex>``: an HMAC of the id keyed by the entry id, which the
+    document does not carry, so the same install masks an id the same way every
+    export and a guessed street cannot be hashed to match it."""
+    digest = hmac.new(key.encode(), entity_id.encode(), hashlib.sha256).hexdigest()
+    return f"{entity_id.split('.', 1)[0]}.e_{digest[:10]}"
+
+
+def mask_ids(doc: Json, key: str) -> Json:
+    """``doc`` with every entity id, at any depth and as any dict key,
+    renamed through ``entity_roles`` else ``hashed_id``: one mapping."""
+    roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"))
+
+    def rename(node: object) -> object:
+        if isinstance(node, str) and ENTITY_ID.match(node):
+            return roles.get(node) or hashed_id(node, key)
+        if isinstance(node, dict):
+            return {rename(k): rename(v) for k, v in node.items()}
+        if isinstance(node, list):
+            return [rename(v) for v in node]
+        return node
+
+    return cast(Json, rename(doc))
+
+
+def _entity_ids(node: object, into: set[str]) -> set[str]:
+    """Every string spelled like an entity id in ``node``, a dict's keys too --
+    ``states``' and any other: ``mask_ids`` renames every key it can."""
+    if isinstance(node, str) and ENTITY_ID.match(node):
+        into.add(node)
+    elif isinstance(node, dict):
+        for k, v in node.items():
+            _entity_ids(k, into)
+            _entity_ids(v, into)
+    elif isinstance(node, list):
+        for v in node:
+            _entity_ids(v, into)
+    return into
+
+
+def _unmasked(payload: object) -> list[str]:
+    """The ids in ``payload`` ``mask_ids`` did not produce: neither hashed nor the role
+    the document's own entry gives them; longest first."""
+    if not isinstance(payload, dict):
+        return []
+    roles = entity_roles(payload.get("entry") or {}, payload.get("price_series_entity"))
+    return sorted((i for i in _entity_ids(payload, set())
+                   if not HASHED_ID.match(i) and roles.get(i) != i), key=len, reverse=True)
+
+
+def mask_violations(payload: object) -> list[str]:
+    """The unmasked ids, counted and never named."""
+    left = _unmasked(payload)
+    if not left:
+        return []
+    street = sum(1 for i in left if ADDRESS.search(i.split(".", 1)[1]))
+    return [f"{len(left)} entity id(s) not masked to a role or a hashed id"
+            + (f", {street} holding an address-like token (a word, then a house number)"
+               if street else "")]
+
+
+def refusals(payload: object, conf: frozenset[str] | None = None) -> list[str]:
+    """``violations`` and ``mask_violations``, each message with every unmasked id
+    and address-like token in it replaced by its class: what ``seal`` refuses and
+    ``--check`` prints, so a refusal never repeats what it refuses."""
+    unsafe = _unmasked(payload)
+    out = []
+    for line in violations(payload, conf) + mask_violations(payload):
+        for eid in unsafe:
+            line = line.replace(eid, "<unmasked id>")
+        out.append(ADDRESS.sub("<address-like token>", line))
+    return out
+
+
 def document(
     *, time_zone: str, window: tuple[str, str], recorder_schema: int | None,
     entry: Json, inputs: Iterable[str], published: Iterable[str],
     price_series_entity: str | None, states: dict[str, list[list[Any]]],
 ) -> Json:
-    """The unsanitised ``hpo-replay/1`` document; ``seal`` makes it writable."""
-    return {
+    """The unsanitised ``hpo-replay/1`` document, every entity id masked
+    (``mask_ids``, keyed by the entry's id); ``seal`` makes it writable."""
+    return mask_ids({
         "format": FORMAT,
         "time_zone": time_zone,
         "window": {"start": window[0], "end": window[1]},
@@ -495,22 +644,74 @@ def document(
         "published": sorted(published),
         "price_series_entity": price_series_entity,
         "states": states,
-    }
+    }, str(entry.get("entry_id") or ""))
+
+
+def _copy(value: str) -> re.Pattern[str]:
+    """``value`` as a whole token: not a digit or letter run's middle, so a
+    dropped ``4829137`` is no copy inside ``14829137.5``."""
+    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(value)}(?![A-Za-z0-9])")
+
+
+_ROW_FIELDS = ("updated", "state", "attributes", "reported")
+
+
+def _scan(node: object, path: str, found: dict[str, set[int]],
+          creds: list[re.Pattern[str]]) -> object:
+    """``node`` with each kept string holding a credential's copy nulled, and
+    ``found`` the place of every copy that cannot be dropped (a number, a key)
+    -- the place only. An ISO time is never a copy: a credential that reads
+    like a date fragment ("2026-10") sits inside every timestamp by chance.
+    Text dropped for its shape alone is not searched: a string holding it
+    breaks the same shape rule, so ``sanitise`` dropped that string too."""
+    if path == "states" and isinstance(node, dict):
+        return {eid: [[_scan(cell, f"states[{eid}].{field}", found, creds)
+                       for field, cell in zip(_ROW_FIELDS, row)]
+                      if isinstance(row, list) else row for row in (rows or [])]
+                for eid, rows in node.items()}
+    if isinstance(node, dict):
+        for key in node:
+            _hit(str(key), f"{path or '<top>'}: a key", found, creds)
+        return {k: _scan(v, f"{path}.{k}" if path else str(k), found, creds)
+                for k, v in node.items()}
+    if isinstance(node, list):
+        return [_scan(v, f"{path}[]", found, creds) for v in node]
+    return _scan_leaf(node, path, found, creds)
+
+
+def _scan_leaf(node: object, path: str, found: dict[str, set[int]],
+               creds: list[re.Pattern[str]]) -> object:
+    if isinstance(node, str) and not ISO_TIME.match(node) and any(c.search(node) for c in creds):
+        return None
+    if isinstance(node, (int, float)) and not isinstance(node, bool):
+        _hit(json.dumps(node), path, found, creds)
+    return node
+
+
+def _hit(text: str, place: str, found: dict[str, set[int]],
+         copies: list[re.Pattern[str]]) -> None:
+    for i, copy in enumerate(copies):
+        if copy.search(text):
+            found.setdefault(place, set()).add(i)
 
 
 def seal(raw: Json, conf: frozenset[str]) -> Json:
-    """``raw`` sanitised, or ``Refused`` when a dropped value survives elsewhere in
-    it or the result still breaks a rule."""
+    """``raw`` sanitised, every string holding a copy of a dropped value dropped
+    too; ``Refused`` when a copy survives where it cannot be dropped (a number,
+    a key) -- naming its place, never the value -- or the result still breaks a
+    rule of ``refusals``, an unmasked id or an address-like token among them."""
     dropped: list[str] = []
     clean = sanitise(raw, conf, dropped)
-    blob = json.dumps(clean, sort_keys=True)
-    leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS and s in blob})
-    if leaked:
+    creds = sorted({str(s) for s in dropped if isinstance(s, Credential)
+                    and len(s) >= LEAK_MIN_CHARS and s.lower() not in STATE_WORDS})
+    found: dict[str, set[int]] = {}
+    clean = cast(Json, _scan(clean, "", found, [_copy(v) for v in creds]))
+    if found:
         raise Refused(
-            f"refusing to write: {len(leaked)} dropped credential value(s) "
-            "survive elsewhere in the payload"
-        )
-    left = violations(clean, conf)
+            f"refusing to write: {len(set().union(*found.values()))} dropped "
+            "credential value(s) survive elsewhere in the payload, at "
+            + ", ".join(sorted(found)[:8]))
+    left = refusals(clean, conf)
     if left:
         raise Refused("refusing to write: " + "; ".join(left[:5]))
     return clean
diff --git a/dev/audit/harnesses/r10_replay_real_day_mutants.py b/dev/audit/harnesses/r10_replay_real_day_mutants.py
new file mode 100644
index 000000000..574b8ec17
--- /dev/null
+++ b/dev/audit/harnesses/r10_replay_real_day_mutants.py
@@ -0,0 +1,274 @@
+#!/usr/bin/env python3
+"""R10-REPLAY-REAL-DAY's mutation proof for the sites no CI lane mutates.
+
+``mutation-autofix`` mutates ``custom_components/`` only, so the export's
+recorder and masking guards (``tools/replay/export.py``), the fixture cutter
+(``tools/replay/cut_day.py``) and the replay lane's own guards
+(``tests/replay.py``) carry their proof here, in the tree, where a reviewer
+re-runs it; so do the ``replay_doc.py`` sites the autofix lane left unpinned,
+whose ledger pins it records after the push. Each mutant is one exact substitution, applied to a copy of the
+tree (``tests``, ``tools``, ``custom_components``); the checks named beside it
+must turn red, and the unmutated copy (the null) must be all green.
+
+The fast tier runs, per mutant, ``tests/replay.py``'s ``controls()``,
+``sanitiser_checks()`` over the committed fixtures and
+``synthetic_reproduces()`` in a fresh interpreter -- seconds each. The slow
+tier (``--replay``) replays ``tests/replay/owner-2026-10-30-away.json``
+through ``tests/replay.py --one`` for the mutants only a recorded day can see
+(the controls never run ``run_fixture``), minutes each.
+
+Prints one ``KILLED``/``SURVIVED`` row per mutant, naming the red checks, and
+``RESULT killed=<k> mutants=<n> null_red=<r>``. Run from a worktree root:
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py [--replay]
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+import sys
+import tempfile
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
+ROOT = repo_root(__file__)
+COPIED = ("tests", "tools", "custom_components")
+OWNER = "tests/replay/owner-2026-10-30-away.json"
+MARK = "<<<replay-json>>>"  # tests/replay.py MARK
+
+EXPORT, CUT, LANE = "tools/replay/export.py", "tools/replay/cut_day.py", "tests/replay.py"
+DOC = "custom_components/heatpump_optimizer/replay_doc.py"
+
+#: (name, file, old, new, a check that must turn red). ``old`` occurs once.
+FAST = [
+    ("no db_url from configuration.yaml", EXPORT,
+     "url = db_url or (None if db else recorder_url(config_dir))", "url = db_url",
+     "recorder:db_url_whole_day_read"),
+    ("no read-only session", EXPORT,
+     'cur.execute("SET SESSION TRANSACTION READ ONLY")', 'cur.execute("SELECT 1")',
+     "recorder:db_url_read_only_session_selects_only"),
+    ("URL carried into the recorder label", EXPORT,
+     "parts, label = urlsplit(url), MYSQL_LABEL", "parts, label = urlsplit(url), url",
+     "recorder:db_url_connect_refusal_names_no_credential"),
+    ("SQLite db_url path carried into the recorder label", EXPORT,
+     "        label = SQLITE_URL_LABEL\n", "        label = f\"SQLite {db}\"\n",
+     "recorder:sqlite_db_url_refusal_names_kind_not_path"),
+    ("recorder label interpolated into the open line (alert 47)", EXPORT,
+     '    print("reading the recorder", file=sys.stderr)\n',
+     '    print(f"reading the recorder {rec.label}", file=sys.stderr)\n',
+     "recorder:open_line_constant_no_label"),
+    ("connect refusal carries the driver's text", EXPORT,
+     'f"{type(err).__name__}") from None', 'f"{err}") from None',
+     "recorder:db_url_connect_refusal_names_no_credential"),
+    ("no quiet-input refusal", EXPORT, "    if quiet:\n", "    if False:\n",
+     "recorder:stale_sqlite_near_empty_day_refused"),
+    ("no !secret resolution", EXPORT,
+     "return _secret(config_dir, _yaml_scalar(found.group(1)))",
+     "return _yaml_scalar(found.group(1))", "recorder:url_from_configuration:secret"),
+    ("no !include followed", EXPORT, "    if include:\n", "    if False:\n",
+     "recorder:url_from_configuration:include"),
+    ("retired-key filter removed", EXPORT,
+     "mapped_entities({k: v for k, v in sec.items() if k in conf})",
+     "mapped_entities(sec)", "recorder:retired_key_left_out"),
+    ("untimed dropped from check_file", EXPORT,
+     "return found + untimed(payload)", "return found",
+     "mask:check_refuses_a_document_with_its_times_nulled"),
+    ("no thinning", CUT,
+     "thinned(rows, ahead if _read_ahead(doc, eid) else instants)", "rows",
+     "cut_day:every_cycle_instant_reads_as_the_whole_export"),
+    ("no read-ahead", CUT,
+     "ahead if _read_ahead(doc, eid) else instants", "instants",
+     "cut_day:price_series_kept_to_the_export_end"),
+    ("a restart counted as a reload", CUT,
+     "and not inputs.get(minute))", ")",
+     "cut_day:null_restart_with_inputs_gone_is_no_reload"),
+    ("published entities kept", CUT,
+     'for eid, rows in doc["states"].items() if eid in doc["inputs"]}',
+     'for eid, rows in doc["states"].items()}', "cut_day:no_published_entity_kept"),
+    ("two paired switches not refused", CUT,
+     "if len(switches) > 1 or (set_at and not switches):",
+     "if set_at and not switches:", "cut_day:two_paired_switches_refused"),
+    # The seven sites mutation-autofix left unpinned at 4c994241d, as the
+    # mutation table spells them (GUARD_OFF: the test made False), less the two
+    # this round's simplification of _entity_ids removed, plus that change's own.
+    ("an _entities list not claimed (GUARD_OFF)", DOC,
+     "            if isinstance(value, list):\n                for i, item",
+     "            if False:\n                for i, item",
+     "mask:entities_list_ids_take_their_numbered_role"),
+    ("ids in a list not collected (GUARD_OFF)", DOC,
+     "    elif isinstance(node, list):\n        for v in node:\n            _entity_ids(v, into)",
+     "    elif False:\n        for v in node:\n            _entity_ids(v, into)",
+     "mask:id_only_as_a_list_item_refused"),
+    ("a payload that is no document read as one (GUARD_OFF)", DOC,
+     "    if not isinstance(payload, dict):\n        return []\n    roles",
+     "    if False:\n        return []\n    roles",
+     "mask:a_payload_that_is_no_document_has_no_violation"),
+    ("a list not scanned for credential copies (GUARD_OFF)", DOC,
+     "    if isinstance(node, list):\n        return [_scan(",
+     "    if False:\n        return [_scan(", "leak_copy:copy_inside_a_list_dropped"),
+    ("dict keys outside states not renamed", DOC,
+     "return {rename(k): rename(v) for k, v in node.items()}",
+     "return {k: rename(v) for k, v in node.items()}",
+     "mask:id_as_any_dict_key_renamed_and_refused_unrenamed"),
+    ("dict keys not collected", DOC,
+     "            _entity_ids(k, into)\n", "",
+     "mask:id_only_as_a_states_key_refused"),
+    ("a bool under a credential key read as a credential (carry 12)", DOC,
+     "return isinstance(value, bool) or value in", "return value in",
+     "leak_copy:bool_under_a_credential_key_is_no_credential"),
+    ("away floor unchecked", LANE,
+     'o["floor"] <= o["target"])', "True)", "control:away:floor"),
+    ("away override unchecked", LANE,
+     'if not (o["active"] and o["override"] and floor_ok):',
+     'if not (o["active"] and floor_ok):', "control:away:override"),
+    ("away command not compared with the recording", LANE,
+     'if bool(held) != bool(o.get("commanded_return")):', "if False:",
+     "control:away:replayed"),
+    ("away coverage not asked of a command-less fixture", LANE,
+     "    return [] if any(e[1] for e in events or ()) else [", "    return [] if True else [",
+     "control:away:coverage_needs_a_command"),
+    ("owner fixture's controls.away emptied (the fixture-side twin)", OWNER,
+     '"away": [\n   [\n    "2026-10-30T15:42:54.058467+00:00",\n    true,\n'
+     '    "2026-10-31T19:00:00+00:00"\n   ],\n   [\n    "2026-10-30T18:39:25.778625+00:00",\n'
+     '    false,\n    null\n   ]\n  ],',
+     '"away": [],', "away_coverage:owner-2026-10-30-away.json"),
+    ("no commanded cycle required", LANE,
+     "        if not any(o.get(\"commanded_return\") for o in observations):\n",
+     "        if False:\n", "control:away:coverage_needs_a_commanded_cycle"),
+    ("no_default setpoint exemption removed", LANE,
+     "for k in supplied):", "for k in ()):",
+     "control:no_default:setpoint_value_on_a_reading"),
+    ("no_default setpoint exemption on every entity", LANE,
+     'SETPOINT_KEYS.get(rec.get("key"), ())', '("max_temperature",)',
+     "control:no_default:setpoint_value_on_a_reading"),
+    ("no_default setpoint at any value", LANE,
+     "if any(config.get(k) is not None and _is(v, config[k]) for k in supplied):",
+     "if supplied:",
+     "control:no_default:setpoint_at_an_unconfigured_default"),
+    ("not_frozen counts a zero as a mirrored value", LANE,
+     "for v in matched if abs(v) > MIRROR_TOL}) < 2:", "for v in matched}) < 2:",
+     "control:not_frozen:one_value_beside_zeros"),
+    ("arms skipped everywhere allowed", LANE,
+     "    if not committed - skipped:\n", "    if False:\n",
+     "control:cycle_cost:arms_skipped_never_everywhere"),
+]
+
+#: (name, file, old, new, the fixture's result key that must hold offenders).
+REPLAY = [
+    ("the recorded away command not replayed (round 1's survivor)", LANE,
+     "commanded = returns if active else None", "commanded = None", "away"),
+    ("the recorded away events dropped (round 3's survivor)", LANE,
+     'recorded_away = list((fixture.get("controls") or {}).get("away") or [])',
+     "recorded_away = []", "away"),
+    ("no_default setpoint exemption not handed the config", LANE,
+     "inv_no_default(records, defaults, readings, config)",
+     "inv_no_default(records, defaults, readings)", "no_default"),
+]
+
+FAST_DRIVER = """
+import json, sys; sys.path.insert(0, 'tests'); import replay
+try:
+    r = (replay.controls() + replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json')))
+         + [replay.synthetic_reproduces()])
+    red = [n for n, ok, _ in r if not ok]
+    print('RED ' + json.dumps(red))
+except BaseException as err:
+    print('RED ' + json.dumps(['raised ' + type(err).__name__ + ': ' + str(err)[:120]]))
+"""
+
+
+def env() -> dict[str, str]:
+    out = {**os.environ, "PYTHONPATH": "tests/hastub"}
+    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
+        out.setdefault(var, "1")
+    return out
+
+
+def fast(tree: Path) -> list[str]:
+    proc = subprocess.run([sys.executable, "-c", FAST_DRIVER], cwd=tree, env=env(),
+                          capture_output=True, text=True)
+    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("RED ")), None)
+    if line is None:
+        return [f"no result: rc={proc.returncode} {proc.stderr.strip()[-200:]}"]
+    return json.loads(line[4:])
+
+
+def replay(tree: Path) -> dict:
+    zone = json.loads((tree / OWNER).read_text()).get("time_zone") or "UTC"
+    proc = subprocess.run([sys.executable, "tests/replay.py", "--one", OWNER], cwd=tree,
+                          env={**env(), "HASTUB_TZ": zone}, capture_output=True, text=True)
+    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
+    if line is None:
+        return {"counts": {}, "error": f"rc={proc.returncode} {proc.stderr.strip()[-200:]}"}
+    return json.loads(line[len(MARK):])
+
+
+def apply(tree: Path, rel: str, old: str, new: str) -> str:
+    path = tree / rel
+    text = path.read_text()
+    if text.count(old) != 1:
+        raise SystemExit(f"{rel}: the mutant's site occurs {text.count(old)} times: {old!r}")
+    path.write_text(text.replace(old, new))
+    return text
+
+
+def main(argv: list[str]) -> int:
+    slow = "--replay" in argv
+    killed = total = 0
+    with tempfile.TemporaryDirectory() as tmp:
+        tree = Path(tmp)
+        for name in COPIED:
+            shutil.copytree(ROOT / name, tree / name, ignore=shutil.ignore_patterns(
+                "__pycache__", ".mypy_cache"))
+        null = fast(tree)
+        print(f"null: red {null}")
+        for name, rel, old, new, want in FAST:
+            original = apply(tree, rel, old, new)
+            try:
+                red = fast(tree)
+            finally:
+                (tree / rel).write_text(original)
+            hit = want in red or any(r.startswith("raised") for r in red)
+            killed += hit
+            total += 1
+            first = [want] if want in red else []
+            shown = first + [r for r in red if r != want]
+            print(f"{'KILLED' if hit else 'SURVIVED'} {rel}: {name}: red {shown[:4]}"
+                  + (f" (+{len(shown) - 4})" if len(shown) > 4 else ""))
+        null_replay = None
+        if slow:
+            null_replay = replay(tree)["counts"]
+            print(f"null replay: counts {null_replay}")
+            for name, rel, old, new, key in REPLAY:
+                original = apply(tree, rel, old, new)
+                try:
+                    counts = replay(tree)["counts"]
+                finally:
+                    (tree / rel).write_text(original)
+                hit = counts.get(key, 0) > 0
+                killed += hit
+                total += 1
+                print(f"{'KILLED' if hit else 'SURVIVED'} {rel}: {name}: counts {counts}")
+    null_red = len(null) + (sum((null_replay or {}).get(k, 0) for k in
+                                ("away", "no_default")) if slow else 0)
+    print(f"RESULT killed={killed} mutants={total} null_red={null_red}")
+    return 0 if killed == total and not null_red else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3078.md b/dev/programme/delivery/3078.md
new file mode 100644
index 000000000..aa89d8dcc
--- /dev/null
+++ b/dev/programme/delivery/3078.md
@@ -0,0 +1 @@
+- [#3078](https://github.com/tvofi/heatpump_optimizer/pull/3078) — **open**, R10-REPLAY-REAL-DAY: a recorded owner day replays through the away path as a regression guard (R10-REPLAY-REAL-DAY)
diff --git a/tests/closures.json b/tests/closures.json
index 0875150fc..5ed92ad55 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1652,6 +1652,7 @@
    "tests/profiles.py",
    "tests/pwlane/package-lock.json",
    "tests/replay.py",
+   "tests/replay/owner-2026-10-30-away.json",
    "tests/replay/synthetic-dhw-only.json",
    "tests/requirements-build.txt",
    "tests/requirements-ci.txt",
@@ -1869,6 +1870,7 @@
    "tools/pr/codeql_scope.py",
    "tools/pr/preflight.sh",
    "tools/release/stamp.py",
+   "tools/replay/cut_day.py",
    "tools/replay/dbg_bundle_gen.py",
    "tools/replay/debug_ingest.py",
    "tools/replay/debug_replay.py",
@@ -2211,6 +2213,7 @@
    "tests/hastub/homeassistant/util/dt.py",
    "tests/profiles.py",
    "tests/replay.py",
+   "tests/replay/owner-2026-10-30-away.json",
    "tests/replay/synthetic-dhw-only.json",
    "tests/run.sh",
    "tests/stress.py",
@@ -3999,6 +4002,7 @@
    "dev/audit/harnesses/r10_registry_leak.py",
    "dev/audit/harnesses/r10_relay_owed_class_reach.py",
    "dev/audit/harnesses/r10_replay_loopnorm.py",
+   "dev/audit/harnesses/r10_replay_real_day_mutants.py",
    "dev/audit/harnesses/r10_review_gather_share.py",
    "dev/audit/harnesses/r10_review_strength_mutants.py",
    "dev/audit/harnesses/r10_roster_push_race.sh",
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index 4ab4f1a8b..d30235d2c 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -934,13 +934,14 @@ R.check(
 )
 R.check(
     "the replay half carries the entry's inputs and what it publishes, read through the "
-    "recorder's history API: the state in force at the window's start, then the window",
-    set(replay["states"]) == {"sensor.indoor", "sensor.outdoor", "sensor.nordpool",
-                              "sensor.hpo_plan"}
-    and replay["published"] == ["sensor.hpo_plan"]
+    "recorder's history API: the state in force at the window's start, then the window; "
+    "every id masked to its role, and what it publishes to the entry-keyed hash",
+    set(replay["states"]) == {"sensor.indoor_temp", "sensor.outdoor_temp", "sensor.price",
+                              replay_doc.hashed_id("sensor.hpo_plan", "rp")}
+    and replay["published"] == [replay_doc.hashed_id("sensor.hpo_plan", "rp")]
     and replay["price_series_entity"] is None
-    and [row[1] for row in replay["states"]["sensor.outdoor"]] == ["-3.5"]
-    and len(replay["states"]["sensor.indoor"]) == 24
+    and [row[1] for row in replay["states"]["sensor.outdoor_temp"]] == ["-3.5"]
+    and len(replay["states"]["sensor.indoor_temp"]) == 24
     and replay["recorder_schema"] == ha_recorder.Recorder.schema_version
     and replay["time_zone"] == "Europe/Stockholm",
     str({k: replay.get(k) for k in ("published", "price_series_entity", "window")}),
@@ -969,7 +970,7 @@ R.check(
     not a10.failures(), str(a10.results),
 )
 planted = json.loads(json.dumps(replay))
-planted["states"]["sensor.indoor"][0][2] = {"access_token": TOKEN}
+planted["states"]["sensor.indoor_temp"][0][2] = {"access_token": TOKEN}
 planted_found = export.violations(planted, CONF)
 R.check(
     "the null control: a credential planted back into the generated replay half is "
@@ -1018,11 +1019,30 @@ tibber = asyncio.run(_replay_download(
     price_source="tibber", tibber=[("sensor.electricity_price_home", "96a14971")]))
 R.check(
     "with the Tibber source the replay half takes the price series from the Tibber "
-    "price sensor, the export's own choice",
-    tibber["debug"]["replay"]["price_series_entity"] == "sensor.electricity_price_home"
-    and "sensor.electricity_price_home" in tibber["debug"]["replay"]["states"],
+    "price sensor, the export's own choice, masked as the price series (the entry's "
+    "own price_entity holds sensor.price)",
+    tibber["debug"]["replay"]["price_series_entity"] == "sensor.price_series"
+    and "sensor.price_series" in tibber["debug"]["replay"]["states"]
+    and "electricity_price_home" not in json.dumps(tibber["debug"]["replay"]),
     str(tibber["debug"]["manifest"].get("replay")),
 )
+# R10-REPLAY-REAL-DAY: the home's name or street address rides in entity ids (the
+# Tibber price sensor's id is derived from the home's address), in friendly names
+# and in text. Invented here; the sealed replay half must carry none of it.
+street = asyncio.run(_replay_download(
+    price_source="tibber", tibber=[("sensor.electricity_price_exempelgatan_12", "96a14971")],
+    plant={"friendly_name": "Exempelgatan 12 vardagsrum"}, plant_state="Exempelgatan 12B"))
+street_replay = street["debug"]["replay"]
+R.check(
+    "Download diagnostics seals a recorder holding an address-like home name masked: no "
+    "id, name or text of it survives in the replay half, the Tibber series is the price "
+    "series role, and the half passes the export's check mode",
+    street_replay is not None
+    and "exempelgatan" not in json.dumps(street_replay).lower()
+    and street_replay["price_series_entity"] == "sensor.price_series"
+    and _check_download(street_replay) == [],
+    str(street["debug"]["manifest"].get("replay")),
+)
 no_price = asyncio.run(_replay_download(price_source="tibber"))
 R.check(
     "with the Tibber source and no price sensor the replay half is refused as the export "
@@ -1040,7 +1060,7 @@ R.check(
     "newest shorter window that fits, and the bundle stays inline",
     "inline" not in short["debug"] and short["debug"]["replay"] is not None
     and short["debug"]["replay"]["window"]["start"] == (T0 + timedelta(hours=18)).isoformat()
-    and len(short["debug"]["replay"]["states"]["sensor.indoor"]) == 7
+    and len(short["debug"]["replay"]["states"]["sensor.indoor_temp"]) == 7
     and debugger.download_bytes(short["debug"]) + debugger.DOWNLOAD_HEADROOM_BYTES
     <= whole_size - 1,
     str(short["debug"].get("manifest", {}).get("replay")),
@@ -1263,21 +1283,26 @@ def _raw_doc(token="secretvalue123", **states):
         price_series_entity=None, states=states)
 
 
-_leaked = _sealed(_raw_doc(**{"sensor.a": [["t", "secretvalue123", None, None]]}))
+# A copy in a string is dropped with it; a number cannot be, so its copy refuses.
+_copied = _sealed(_raw_doc(**{"sensor.a": [["t", "secretvalue123", None, None]]}))
+_leaked = _sealed(_raw_doc(123456789, **{"sensor.a": [["t", 123456789, None, None]]}))
 # Six characters is the shortest dropped value the leak check looks for again.
-_leaked_six = _sealed(_raw_doc("abc123", **{"sensor.a": [["t", "abc123", None, None]]}))
-_short = _sealed(_raw_doc("abc12", **{"sensor.a": [["t", "abc12", None, None]]}))
+_leaked_six = _sealed(_raw_doc(123456, **{"sensor.a": [["t", 123456, None, None]]}))
+_short = _sealed(_raw_doc(12345, **{"sensor.a": [["t", 12345, None, None]]}))
 _unfit = _sealed(_raw_doc(plainkey=[["t", "1", None, None]]))
 _ok = _sealed(_raw_doc(**{"sensor.a": [["t", "1", None, None]]}))
 R.check(
-    "replay_doc.seal refuses a document where a dropped credential survives elsewhere, "
-    "and one whose sanitised form still breaks a rule, and writes a clean one",
-    isinstance(_leaked, replay_doc.Refused) and "1 dropped credential value(s)" in str(_leaked)
+    "replay_doc.seal drops a string copy of a dropped credential, refuses a document "
+    "where a copy survives as a number (naming its place, not its value), and one whose "
+    "sanitised form still breaks a rule, and writes a clean one",
+    isinstance(_copied, dict) and "secretvalue123" not in json.dumps(_copied)
+    and isinstance(_leaked, replay_doc.Refused) and "1 dropped credential value(s)" in str(_leaked)
+    and ".state" in str(_leaked) and "123456789" not in str(_leaked)
     and isinstance(_leaked_six, replay_doc.Refused) and isinstance(_short, dict)
     and isinstance(_unfit, replay_doc.Refused)
     and "states.plainkey: not an entity id" in str(_unfit)
     and isinstance(_ok, dict) and _ok["entry"]["data"] == {}
-    and _ok["states"] == {"sensor.a": [["t", "1", None, None]]},
+    and _ok["states"] == {replay_doc.hashed_id("sensor.a", ""): [["t", "1", None, None]]},
     f"{_leaked if isinstance(_leaked, replay_doc.Refused) else type(_leaked).__name__} "
     f"{_unfit!r}",
 )
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json
new file mode 100644
index 000000000..48fe278bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.BOOLOP.1af5d1b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings BOOLOP 1af5d1b5",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if text and secret:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if text or secret:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json
new file mode 100644
index 000000000..81ca93fd2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.1af5d1b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF 1af5d1b5",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if text and secret:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json
deleted file mode 100644
index 7e72b50c8..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.c831c60b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF c831c60b",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if text and (secret or (isinstance(node, str) and not text_ok(node))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json
new file mode 100644
index 000000000..1f249bbcc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_collect_strings.GUARD_OFF.d8e39501.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_collect_strings GUARD_OFF d8e39501",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        elif text and isinstance(node, str) and not text_ok(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json b/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json
new file mode 100644
index 000000000..34a0a4d23
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_copy.RETURN_DEL.d004bc2e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_copy RETURN_DEL d004bc2e",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return re.compile(rf\"(?<![A-Za-z0-9]){re.escape(value)}(?![A-Za-z0-9])\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json
new file mode 100644
index 000000000..889fd1d7b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.BOOLOP.c4fcf654.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids BOOLOP c4fcf654",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, str) or ENTITY_ID.match(node):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json
new file mode 100644
index 000000000..4059e18fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.50e92e5d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF 50e92e5d",
+  "killed_by": "tests/entities.py",
+  "old": "    elif isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json
new file mode 100644
index 000000000..3c4e29f3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.bc1e8661.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF bc1e8661",
+  "killed_by": "tests/entities.py",
+  "old": "    elif isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json
new file mode 100644
index 000000000..7482b5f00
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.GUARD_OFF.c4fcf654.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids GUARD_OFF c4fcf654",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json
new file mode 100644
index 000000000..f445fdb4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entity_ids.RETURN_DEL.b954b2d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entity_ids RETURN_DEL b954b2d8",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return into",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json
new file mode 100644
index 000000000..dc8cf10be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.BOOLOP.aa32e007.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entry_shape BOOLOP aa32e007",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(value, str) and re.search(r\"\\s\", value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(value, str) or re.search(r\"\\s\", value):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json
new file mode 100644
index 000000000..7dc016f98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_entry_shape.GUARD_OFF.aa32e007.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_entry_shape GUARD_OFF aa32e007",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(value, str) and re.search(r\"\\s\", value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json
new file mode 100644
index 000000000..1fc94975d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_hit.GUARD_OFF.320a5d6d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_hit GUARD_OFF 320a5d6d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if copy.search(text):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json
new file mode 100644
index 000000000..a0fba7bcb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_no_credential.RETURN_DEL.e8b4342c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_no_credential RETURN_DEL e8b4342c",
+  "killed_by": "tests/entities.py",
+  "old": "    return isinstance(value, bool) or value in (None, \"\", [], {})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json
new file mode 100644
index 000000000..54e2a6fd1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.BOOLOP.c5354b16.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan BOOLOP c5354b16",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if path == \"states\" and isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if path == \"states\" or isinstance(node, dict):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json
new file mode 100644
index 000000000..8a8aa9251
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.08da69e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF 08da69e4",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json
new file mode 100644
index 000000000..37746fc75
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.b9435854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF b9435854",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json
new file mode 100644
index 000000000..a601e1033
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.GUARD_OFF.c5354b16.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan GUARD_OFF c5354b16",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if path == \"states\" and isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json
new file mode 100644
index 000000000..7de01a750
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan.RETURN_DEL.a0419929.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan RETURN_DEL a0419929",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return _scan_leaf(node, path, found, creds)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json
new file mode 100644
index 000000000..c06bdcebb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.BOOLOP.33a88808.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf BOOLOP 33a88808",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(node, (int, float)) and not isinstance(node, bool):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, (int, float)) or not isinstance(node, bool):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json
new file mode 100644
index 000000000..9c2780201
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.33a88808.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf GUARD_OFF 33a88808",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, (int, float)) and not isinstance(node, bool):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json
new file mode 100644
index 000000000..3938d2499
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.GUARD_OFF.d5257eac.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf GUARD_OFF d5257eac",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(node, str) and not ISO_TIME.match(node) and any(c.search(node) for c in creds):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json
new file mode 100644
index 000000000..bf6ed8638
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_scan_leaf.RETURN_DEL.b20e5b2d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_scan_leaf RETURN_DEL b20e5b2d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return node",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json
new file mode 100644
index 000000000..ec3b40699
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.BOOLOP.48930130.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_unmasked BOOLOP 48930130",
+  "killed_by": "tests/debug_collect.py",
+  "old": "                   if not HASHED_ID.match(i) and roles.get(i) != i), key=len, reverse=True)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not HASHED_ID.match(i) or roles.get(i) != i), key=len, reverse=True)`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json
new file mode 100644
index 000000000..348c084e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_unmasked.GUARD_OFF.14f861a9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_unmasked GUARD_OFF 14f861a9",
+  "killed_by": "tests/entities.py",
+  "old": "    if not isinstance(payload, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=51."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json
deleted file mode 100644
index 841be3746..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.5476d757.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk BOOLOP 5476d757",
-  "killed_by": "tests/debug_collect.py",
-  "old": "            if SECRET_KEY.search(str(key)) and value not in (None, \"\", [], {}):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: BOOLOP (`if SECRET_KEY.search(str(key)) or value not in (None, \"\", [], {}):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json
new file mode 100644
index 000000000..3eb622024
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.BOOLOP.7cfc611c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk BOOLOP 7cfc611c",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if SECRET_KEY.search(str(key)) and not _no_credential(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if SECRET_KEY.search(str(key)) or not _no_credential(value):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json
deleted file mode 100644
index 5e4d2ec11..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.5476d757.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk GUARD_OFF 5476d757",
-  "killed_by": "tests/entities.py",
-  "old": "            if SECRET_KEY.search(str(key)) and value not in (None, \"\", [], {}):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json
new file mode 100644
index 000000000..8e7f0cec6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_walk.GUARD_OFF.7cfc611c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_walk GUARD_OFF 7cfc611c",
+  "killed_by": "tests/structure.py",
+  "old": "            if SECRET_KEY.search(str(key)) and not _no_credential(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
new file mode 100644
index 000000000..c3450f3d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
+  "killed_by": "tests/entities.py",
+  "old": "            if isinstance(value, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json
new file mode 100644
index 000000000..9d8dd3186
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.RETURN_DEL.24126f41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles RETURN_DEL 24126f41",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return roles",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json
new file mode 100644
index 000000000..53fa0a2f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.801db476.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles.claim GUARD_OFF 801db476",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(eid, str) and ENTITY_ID.match(eid) and eid not in roles:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json
new file mode 100644
index 000000000..724698461
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.claim.GUARD_OFF.f1238e21.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles.claim GUARD_OFF f1238e21",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if rid not in roles.values():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json b/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json
new file mode 100644
index 000000000..8286e5783
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/hashed_id.RETURN_DEL.f8942d60.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:hashed_id RETURN_DEL f8942d60",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return f\"{entity_id.split('.', 1)[0]}.e_{digest[:10]}\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json
new file mode 100644
index 000000000..243733628
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.RETURN_DEL.f7fb6f10.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids RETURN_DEL f7fb6f10",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return cast(Json, rename(doc))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json
new file mode 100644
index 000000000..a38deb5db
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.BOOLOP.497676f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename BOOLOP 497676f1",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(node, str) or ENTITY_ID.match(node):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json
new file mode 100644
index 000000000..799de000a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.497676f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF 497676f1",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, str) and ENTITY_ID.match(node):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json
new file mode 100644
index 000000000..4dbe9dfb4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.b78e27c0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF b78e27c0",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json
new file mode 100644
index 000000000..0eac08b0d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.GUARD_OFF.c41f3797.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename GUARD_OFF c41f3797",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        if isinstance(node, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json
new file mode 100644
index 000000000..306e428c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_ids.rename.RETURN_DEL.7139a494.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_ids.rename RETURN_DEL 7139a494",
+  "killed_by": "tests/debug_collect.py",
+  "old": "        return node",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json b/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json
new file mode 100644
index 000000000..c5c9d63bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/mask_violations.GUARD_OFF.71e0616b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:mask_violations GUARD_OFF 71e0616b",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if not left:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json
new file mode 100644
index 000000000..569a04f4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/refusals.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:refusals RETURN_DEL a8227ccf",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json
deleted file mode 100644
index 91506594f..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.BOOLOP.b11cce2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal BOOLOP b11cce2f",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS and s in blob})",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS or s in blob})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json
new file mode 100644
index 000000000..02d27bb97
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.61a9917d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal CMP_BOUND 61a9917d",
+  "killed_by": "tests/debug_collect.py",
+  "old": "                    and len(s) >= LEAK_MIN_CHARS and s.lower() not in STATE_WORDS})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and len(s) > LEAK_MIN_CHARS and s.lower() not in STATE_WORDS})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json
deleted file mode 100644
index 5e4c39ecd..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.CMP_BOUND.b11cce2f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal CMP_BOUND b11cce2f",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    leaked = sorted({s for s in dropped if len(s) >= LEAK_MIN_CHARS and s in blob})",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`leaked = sorted({s for s in dropped if len(s) > LEAK_MIN_CHARS and s in blob})`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json
new file mode 100644
index 000000000..8f5e34b1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.3d96d616.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal GUARD_OFF 3d96d616",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if found:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json b/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json
deleted file mode 100644
index ea569d0a8..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/seal.GUARD_OFF.43b78c97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:seal GUARD_OFF 43b78c97",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if leaked:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json b/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json
deleted file mode 100644
index cd0f90e2d..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.BOOLOP.aa6ef607.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:text_ok BOOLOP aa6ef607",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return bool(LABEL.match(value)) and not re.search(r\"\\d{4}\", value)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: BOOLOP (`return bool(LABEL.match(value)) or not re.search(r\"\\d{4}\", value)`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json b/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json
deleted file mode 100644
index bdc1faaba..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/text_ok.RETURN_DEL.aa6ef607.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:text_ok RETURN_DEL aa6ef607",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return bool(LABEL.match(value)) and not re.search(r\"\\d{4}\", value)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/replay.py b/tests/replay.py
index 5eb13fb03..13799dc4a 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -47,6 +47,13 @@ THE INVARIANTS, per cycle and per published entity:
                      optimizer's own on threshold), and ``hvac_action`` not
                      idle while ``heat_pump_on`` (#1499's shape);
 ``cycle``            every cycle returns data and no entity property raises;
+``away``             while the owner's recorded command holds away (the
+                     fixture's ``controls.away``, replayed through
+                     ``coordinator.async_set_away``; ``controls.reloads``
+                     replayed as an in-process reload handed the last
+                     publish), the plan's view is away and holds the
+                     override, and -- not recovering -- its published floor
+                     is at the away target (``away_offenders``);
 
 and once per fixture:
 
@@ -103,6 +110,8 @@ import io
 import json
 import math
 import os
+import re
+import shutil
 import subprocess
 import sys
 import tempfile
@@ -215,15 +224,36 @@ def _is(a: object, b: float, tol: float = 1e-9) -> bool:
     return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(float(a) - b) <= tol
 
 
-def inv_no_default(records: list[dict], defaults: list[float], readings: list[float]) -> list[str]:
-    """A temperature equal to a constructor default, which no input read."""
+#: Temperature sensors that publish a SETPOINT the configuration supplies,
+#: not a reading of the house, by translation key, with the config value each
+#: is made of. Such a sensor equal to a ``ThermalState`` default is no leaked
+#: default when its configured value says the same: the owner's install
+#: configures ``max_temperature`` 21.0, which ``mixing_valve.recommend_target``
+#: publishes as the valve target, and 21.0 is also ``room_temperature``'s
+#: default (14 offenders a cycle on owner-2026-10-30-away.json before this).
+#: Keyed on the entity AND the configured value, so the same 21.0 on a reading
+#: entity, or the setpoint at a default the config does not hold, still fires
+#: (``control:no_default:setpoint``). The climate entity's target is left out
+#: of the judgement altogether, below, for the same reason.
+SETPOINT_KEYS: dict[str, tuple[str, ...]] = {
+    "valve_target_recommendation": ("max_temperature",),
+}
+
+
+def inv_no_default(records: list[dict], defaults: list[float], readings: list[float],
+                   config: dict | None = None) -> list[str]:
+    """A temperature equal to a constructor default, which no input read --
+    nor, for a setpoint sensor (``SETPOINT_KEYS``), the config option it is."""
     out = []
+    config = config or {}
 
-    def judge(label: str, value: object) -> None:
+    def judge(label: str, value: object, supplied: tuple[str, ...] = ()) -> None:
         try:
             v = float(value)  # type: ignore[arg-type]
         except (TypeError, ValueError):
             return
+        if any(config.get(k) is not None and _is(v, config[k]) for k in supplied):
+            return
         if any(_is(v, d) for d in defaults) and not any(_is(v, r) for r in readings):
             out.append(f"{label}={v}")
 
@@ -231,7 +261,7 @@ def inv_no_default(records: list[dict], defaults: list[float], readings: list[fl
         if not rec["available"]:
             continue
         if str(rec.get("device_class")) == "temperature":
-            judge(rec["entity_id"], rec["state"])
+            judge(rec["entity_id"], rec["state"], SETPOINT_KEYS.get(rec.get("key"), ()))
         if rec["entity_id"].startswith("climate."):
             # The readings only: a target is a setpoint the config supplies.
             judge(f"{rec['entity_id']}.current_temperature",
@@ -278,6 +308,61 @@ def inv_agreement(records: list[dict], plan_draws: bool | None,
     return out
 
 
+def away_coverage_offenders(name: str, events: list | None) -> list[str]:
+    """A fixture in ``AWAY_COVERED`` whose ``controls.away`` holds no active
+    command: it declares coverage the recording does not carry."""
+    if name not in AWAY_COVERED:
+        return []
+    return [] if any(e[1] for e in events or ()) else [
+        f"{name} declares away coverage but records no active command"]
+
+
+def away_offenders(observations: list[dict], events: list | None = None,
+                   expect_commanded: bool = False) -> list[str]:
+    """A cycle the owner's recorded command holds away (``controls.away``) whose
+    plan was not made away: the coordinator's live view not active, the
+    override not held, or -- not recovering -- the solve's published floor
+    above the away target. R10-HOTFIX-AWAY-LIVE's stated behaviour: after the
+    switch, a restore and a reload, the live state equals the resolved
+    override and the solve's bands carry the away target. How much the plan
+    then heats is not judged: a floor that outranks the setback by design
+    (the mold guard's, capped at the configured target) heats an away house.
+
+    ``events`` is the fixture's own ``controls.away``, read apart from the
+    replay: every cycle at or after an active command, before the next, must
+    be one the replay observed commanded, so a replay that stopped carrying
+    the command is red while the events are non-empty (R10-REPLAY-REAL-DAY
+    round 1: ``commanded = None`` survived). Empty events judge nothing, so
+    ``expect_commanded`` -- true for a fixture in ``AWAY_COVERED`` -- also
+    requires at least one commanded cycle, and ``away_coverage_offenders``
+    refuses such a fixture whose events hold no active command (round 3:
+    ``recorded_away = []`` survived with none).
+    """
+    out = []
+    if expect_commanded:
+        if not any(o.get("commanded_return") for o in observations):
+            out.append("the fixture declares away coverage but the replay carried no "
+                       "commanded cycle")
+    for o in observations if events is not None else ():
+        held = None
+        for when, active, returns in events:
+            if _ts(when) <= _ts(o["t"]):
+                held = returns if active else None
+        if bool(held) != bool(o.get("commanded_return")):
+            out.append(f"{o['t']}: the recorded command holds away={bool(held)}, "
+                       f"the replay carried away={bool(o.get('commanded_return'))}")
+    for o in observations:
+        if not o.get("commanded_return"):
+            continue
+        floor_ok = o["recovery"] or (o["floor"] is not None and o["target"] is not None
+                                     and o["floor"] <= o["target"])
+        if not (o["active"] and o["override"] and floor_ok):
+            out.append(f"{o['t']}: commanded away, the plan's view active={o['active']} "
+                       f"override={o['override']} recovery={o['recovery']} "
+                       f"floor={o['floor']} target={o['target']}")
+    return out
+
+
 def frozen_offenders(
     published: dict[str, list[float | None]],
     inputs: dict[str, list[float | None]],
@@ -288,10 +373,14 @@ def frozen_offenders(
         for ikey, ivals in inputs.items():
             both = [(p, i) for p, i in zip(pvals, ivals) if p is not None and i is not None]
             matched = [i for p, i in both if abs(p - i) <= MIRROR_TOL]
-            # Two distinct matched values at least: a published 0.0 beside an
-            # input idling at 0.0 is a coincidence of zeros, not a mirror.
+            # Two distinct NON-ZERO matched values at least: a published 0.0
+            # beside an input idling at 0.0 is a coincidence of zeros, not a
+            # mirror, and so is one value met once beside those zeros (the
+            # owner's day: power_ratio 1.55 = mean(0/0.5, 1.55/0.5) on the cycle
+            # the pump read 1.55 kW). A mirror is seen at two values it tracked;
+            # a 0/x signal that mirrors only one non-zero value is not judged.
             if len(matched) < MIRROR_MIN_HITS or len(matched) * 2 < len(both) \
-                    or len({round(v, 3) for v in matched}) < 2:
+                    or len({round(v, 3) for v in matched if abs(v) > MIRROR_TOL}) < 2:
                 continue
             for k in range(1, len(pvals)):
                 p0, p1, i0, i1 = pvals[k - 1], pvals[k], ivals[k - 1], ivals[k]
@@ -369,10 +458,39 @@ COST_DETECTION = 2.0
 #: after it read 1.880 and 1.391; sqrt(2) x the geometric midpoint of 1.256
 #: and 1.880 is 2.173, each edge 15.6 % inside the band (floor 1.087).
 #: Re-centre at the next timed week, not on one run.
+#: ``owner-2026-10-30-away.json`` (R10-REPLAY-REAL-DAY), the same rule, sqrt(2)
+#: x the geometric midpoint of the readings' extremes, from the clean ``--one``
+#: replays of 2026-10-31/11-01: ``cpu_ratio`` over the Linux readings -- one CI
+#: ``replay`` job (249.0) and two 4-core boxes (217.8-278.7, 231.8-290.5) --
+#: 217.8-290.5, each edge 18-22 % inside; a loaded M1 (177-394, load average
+#: 30-200) spans more than a 2x band holds and is left out. ``peak_kib`` and
+#: ``loop_cpu_ratio`` over all four environments, the M1 included: 2514-2783
+#: and 0.137-0.227, the loop's edges 9-10 % inside. One CI class only: the
+#: R10-REPLAY-LANE carry asks for both, so re-centre when the other class reads.
 COST_BUDGETS: dict[str, dict[str, float]] = {
     "synthetic-dhw-only.json": {"cpu_ratio": 2.173, "peak_kib": 2686.0,
                                 "loop_cpu_ratio": 0.143},
+    "owner-2026-10-30-away.json": {"cpu_ratio": 355.7, "peak_kib": 3740.0,
+                                   "loop_cpu_ratio": 0.249},
 }
+#: Fixtures the lane replays once, clean, without the three doubled-cost
+#: arms: each arm is a whole replay, and a fixture whose replay costs a large
+#: share of the lane's job time cannot be run four times inside it (the
+#: replay job's ``timeout-minutes``, tests.yml). The clean run still holds
+#: its budget's band, (budget / 2, budget], so the budget can see a doubling;
+#: the arms' own proof -- that the instrument reads a doubled cycle as one --
+#: is fixture-independent and stays on the fixtures not named here, which the
+#: driver requires to exist.
+COST_ARMS_SKIPPED: dict[str, str] = {
+    "owner-2026-10-30-away.json": "a real install's solve: 16 cycles, about 12 "
+    "CPU-minutes a replay, so four would overrun the replay job; the arms run on "
+    "the synthetic fixture",
+}
+#: Fixtures that declare away coverage: their ``controls.away`` must hold an
+#: active command and their replay must carry it for at least one cycle
+#: (``away_offenders``'s ``expect_commanded``). A design choice: coverage is
+#: declared here, so a fixture cut without the command is refused, not passed.
+AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})
 #: A reference solve after every this many cycles, beside the ones before
 #: and after the day, so the unit tracks the runner through the replay.
 COST_REF_EVERY = 8
@@ -469,6 +587,16 @@ def cost_offenders(figures: dict[str, float], budget: dict[str, float] | None,
     return out
 
 
+def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
+    """``COST_ARMS_SKIPPED`` naming a fixture not committed, or every one: the
+    doubled-cost arms must still run on some fixture of the full lane."""
+    out = [f"{name}: skipped but not a committed fixture"
+           for name in sorted(skipped - committed)]
+    if not committed - skipped:
+        out.append("every committed fixture skips the doubled-cost arms")
+    return out
+
+
 def short_doubling(injected_ratio: float) -> list[str]:
     """A perturbation arm that burnt less than the clean span its metric
     times is no doubling (#2205: the cpu arm spun the update alone, ~0.93)."""
@@ -511,6 +639,31 @@ def controls() -> list[tuple[str, bool, str]]:
     pair("no_default",
          inv_no_default([rec(device_class="temperature", state=22.0)], defaults, [20.4]),
          inv_no_default([rec(device_class="temperature", state=21.0)], defaults, [21.0]))
+    # A setpoint sensor at the value its config option holds is no default; the
+    # same value on a reading, or the setpoint at a default the config does not
+    # hold, still is (owner-2026-10-30-away.json: max_temperature 21.0).
+    valve = dict(device_class="temperature", key="valve_target_recommendation",
+                 entity_id="sensor.valve_target_recommendation")
+    conf = {"max_temperature": 21.0}
+    pair("no_default:setpoint_value_on_a_reading",
+         inv_no_default([rec(device_class="temperature", key="room_temperature", state=21.0)],
+                        defaults, [20.4], conf),
+         inv_no_default([rec(**valve, state=21.0)], defaults, [20.4], conf))
+    pair("no_default:setpoint_at_an_unconfigured_default",
+         inv_no_default([rec(**valve, state=22.0)], defaults, [20.4], conf),
+         inv_no_default([rec(**valve, state=21.0)], defaults, [20.4], conf))
+    # The rule's preconditions: each key is a sensor the integration publishes,
+    # each option one it reads, and the sensor is that option (a renamed key or
+    # option would leave the exemption matching nothing, or the wrong thing).
+    from heatpump_optimizer import const, mixing_valve
+    sensors = json.loads((ROOT / "custom_components" / "heatpump_optimizer"
+                          / "strings.json").read_text())["entity"]["sensor"]
+    options = {v for k, v in vars(const).items() if k.startswith("CONF_")}
+    made = mixing_valve.recommend_target(comfort_min=18.0, comfort_max=21.5).target
+    res.append(("control:no_default:setpoint_keys_are_published_config",
+                made == 21.5 and all(k in sensors and set(o) <= options
+                                     for k, o in SETPOINT_KEYS.items()),
+                f"recommend_target(comfort_max=21.5)={made}; keys {sorted(SETPOINT_KEYS)}"))
     hpa = dict(entity_id="sensor.hpa", key="heat_pump_action")
     pair("agreement:attribute",
          inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": True})], None),
@@ -531,6 +684,14 @@ def controls() -> list[tuple[str, bool, str]]:
          frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 3.0]}, inp),
          frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 2.0]}, inp)
          + frozen_offenders({"sensor.zero": [0.0] * 5}, {"sensor.idle": [0.0] * 4 + [2.0]}))
+    # One non-zero value met once beside idle zeros (owner-2026-10-30-away.json,
+    # prediction_accuracy.power_ratio against heat_pump_power) is no mirror; a
+    # value that tracked the input at two non-zero values and then stuck is.
+    pair("not_frozen:one_value_beside_zeros",
+         frozen_offenders({"sensor.out": [0.0, 1.0, 1.0, 3.0, 3.0, 3.0]},
+                          {"sensor.in": [0.0, 1.0, 1.0, 3.0, 2.0, 0.0]}),
+         frozen_offenders({"sensor.ratio": [0.0, 0.0, 1.55, 1.55, 1.55, 1.55]},
+                          {"sensor.power": [0.0, 0.0, 1.55, 2.89, 3.02, 0.0]}))
     ref, clean = [10.0, 11.0, 9.0], cost_figures([20.0, 22.0], [10.0, 11.0, 9.0], [4096])
     budget = {k: math.sqrt(COST_DETECTION) * v for k, v in clean.items()}
     pair("cycle_cost:cpu", cost_offenders(cost_figures([40.0, 44.0], ref, [4096]), budget),
@@ -571,8 +732,36 @@ def controls() -> list[tuple[str, bool, str]]:
         [20.0, 22.0], [r * 3 for r in ref], [4096])["cpu_ratio"]
     res.append(("control:cycle_cost:cpu_normaliser", cpu_solve_moved,
                 f"cpu_ratio {clean['cpu_ratio']}: solve x3 moved={cpu_solve_moved}"))
+    pair("cycle_cost:arms_skipped_never_everywhere",
+         arms_skip_offenders({"a.json", "b.json"}, {"a.json", "b.json"}),
+         arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
+    pair("cycle_cost:arms_skipped_committed_only",
+         arms_skip_offenders({"gone.json"}, {"a.json"}),
+         arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
     pair("cycle_cost:short_doubling", short_doubling(0.93), short_doubling(1.0001))
     pair("cycle_cost:unmetered_doubling", short_doubling(float("nan")), short_doubling(1.0))
+    held = {"t": "t", "commanded_return": "r", "active": True, "override": True,
+            "recovery": False, "floor": 15.0, "target": 15.0}
+    good_away = away_offenders([held, {**held, "recovery": True, "floor": 18.0},
+                                {**held, "commanded_return": None, "active": False}])
+    for broken, values in (("view", {"active": False}), ("override", {"override": False}),
+                           ("floor", {"floor": 18.0})):
+        pair(f"away:{broken}", away_offenders([{**held, **values}]), good_away)
+    # The command replayed at all: an observation the recorded events hold
+    # away but the replay did not carry is red (the reviewer's surviving
+    # ``commanded = None``), and one after the command ended is not.
+    events = [["2026-01-01T10:00:00+00:00", True, "r"], ["2026-01-01T11:00:00+00:00", False, None]]
+    seen = [{**held, "t": "2026-01-01T10:15:00+00:00"},
+            {**held, "t": "2026-01-01T11:15:00+00:00", "commanded_return": None, "active": False}]
+    pair("away:replayed",
+         away_offenders([{**o, "commanded_return": None} for o in seen], events),
+         away_offenders(seen, events))
+    covered = next(iter(AWAY_COVERED))
+    pair("away:coverage_needs_a_command",
+         away_coverage_offenders(covered, []), away_coverage_offenders(covered, events))
+    pair("away:coverage_needs_a_commanded_cycle",
+         away_offenders([{**o, "commanded_return": None} for o in seen], [], True),
+         away_offenders(seen, events, True))
     pkg = "/x/custom_components/heatpump_optimizer/"
     pair("cycle_cost:coverage", uncovered_files({pkg + f for f in COST_FILES[1:]}),
          uncovered_files({pkg + f for f in COST_FILES}))
@@ -592,6 +781,10 @@ def sanitiser_checks(paths: list[Path]) -> list[tuple[str, bool, str]]:
         nightly_ha.check_a10_no_precise_location(checks, json.loads(path.read_text()))
         res.append((f"a10_location:{path.name}", not checks.failures(),
                     str(checks.results)))
+        events = (json.loads(path.read_text()).get("controls") or {}).get("away") or []
+        res.append((f"away_coverage:{path.name}",
+                    not away_coverage_offenders(path.name, events),
+                    f"{len(events)} away event(s)"))
     # The null control: an unsanitised payload is refused by the same rules.
     raw = {"format": export.FORMAT, "entry": {"data": {"tibber_token": "abc123xyz",
            "solar_location": {"latitude": 59.334591}}, "options": {}},
@@ -606,7 +799,7 @@ def sanitiser_checks(paths: list[Path]) -> list[tuple[str, bool, str]]:
     res.append(("control:sanitise_clears",
                 not export.violations(export.sanitise(raw, conf, dropped), conf),
                 f"dropped {len(dropped)} value(s)"))
-    return res + leak_probes() + tibber_price_checks()
+    return res + leak_probes() + tibber_price_checks() + recorder_checks() + mask_checks() + leak_copy_checks() + cut_day_checks()
 
 
 #: The review of #1508's leak probe (the first eleven): shapes of private data a recorder
@@ -640,6 +833,10 @@ LEAK_PROBES = {
     "n11_host_path_unit": {"unit_of_measurement": "home.local/api/x"},
     "entry_n13_text_in_entity_key": {"weather_entity": "Storgatan 12 Stockholm"},
     "n14_mac_no_colons": {"options": ["aabbccddeeff"]},
+    # The owner's street address (R10-REPLAY-REAL-DAY): a street and its house
+    # number as a text state, and free text in an entry key the allowlist keeps.
+    "state_street_number": {"state": "Exempelgatan 12B"},
+    "entry_free_text": {"ecl110_state_topic": "Anna Exempel"},
 }
 PROBE_ENTITY = "sensor.heat_pump_power"
 
@@ -744,11 +941,13 @@ def _tibber_export(rows: list[tuple], entry: dict, price_entity: str | None = No
 
     def patched(series=series):
         out = series()
-        for row in rows:
+        # Each sensor's prices sit a whole krona apart, so the masked document's
+        # ``sensor.price`` rows name the sensor they were read from.
+        for i, row in enumerate(rows):
             if row[0] not in unrecorded:
                 out[row[0]] = [(synthesize.DAY + timedelta(hours=h),
                                 "unavailable" if row[0] in unavailable
-                                else f"{0.8 + h / 100:.3f}",
+                                else f"{i + 1 + h / 100:.3f}",
                                 {"unit_of_measurement": "SEK/kWh",
                                  "state_class": "measurement"}) for h in range(-1, 24)]
         return out
@@ -770,7 +969,10 @@ def _tibber_export(rows: list[tuple], entry: dict, price_entity: str | None = No
                     Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
                     None, [], price_entity)
         chosen = payload["price_series_entity"]
-        return f"{chosen} rows={len(payload['states'].get(chosen) or [])}"
+        series_rows = payload["states"].get(chosen) or [] if chosen else []
+        prices = [float(r[1]) for r in series_rows if _num(r[1]) is not None]
+        source = rows[int(prices[-1]) - 1][0] if prices else chosen
+        return f"{source} rows={len(series_rows)}"
     except SystemExit as err:
         return f"refused: {err}"
     finally:
@@ -815,6 +1017,602 @@ def tibber_price_checks() -> list[tuple[str, bool, str]]:
     return [(f"tibber_price:{name}", ok(out), out) for name, (out, ok) in cases.items()]
 
 
+# --- the recorder a ``recorder: db_url`` names, and the masked document --------
+#
+# R10-REPLAY-REAL-DAY: the owner's recorder is MariaDB, named by
+# configuration.yaml's ``recorder: db_url``, beside a stale SQLite file; the
+# export read the SQLite file and wrote a near-empty day its own check passed.
+# These drive ``export.build_export`` over the synthetic install with the
+# MySQL driver replaced by a DB-API double over the same rows: no server.
+
+#: Invented credentials; the checks below require that neither leaves the export.
+_CANARY_USER, _CANARY_KEY = "hpo_reader", "Invented-Pa55word-91"
+_DB_URL = f"mysql://{_CANARY_USER}:{_CANARY_KEY}@core-mariadb/homeassistant?charset=utf8mb4"
+_CONFIGURATION_YAML = (
+    "homeassistant:\n  name: Exempel\n\n"
+    "recorder:\n  purge_keep_days: 10\n  db_url: !secret recorder_db_url  # MariaDB add-on\n"
+    "\nhistory:\n"
+)
+
+
+class _FakeMySQL:
+    """A DB-API module standing in for ``MySQLdb``: each connection runs its
+    ``%s`` statements on a SQLite copy of the recorder, opened read-only, and
+    records them; anything but a SELECT or the read-only session is an error."""
+
+    def __init__(self, backing: Path, fail: str | None = None) -> None:
+        self.backing, self.fail = backing, fail
+        self.statements: list[str] = []
+        self.kwargs: dict = {}
+
+    def connect(self, **kwargs):
+        self.kwargs = kwargs
+        if self.fail:
+            raise RuntimeError(self.fail)
+        return _FakeConnection(self, _sqlite_ro(self.backing))
+
+
+def _sqlite_ro(path: Path):
+    import sqlite3
+
+    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
+
+
+class _FakeConnection:
+    def __init__(self, module: _FakeMySQL, conn) -> None:
+        self.module, self.conn = module, conn
+
+    def cursor(self):
+        return _FakeCursor(self)
+
+    def close(self) -> None:
+        self.conn.close()
+
+
+class _FakeCursor:
+    READ_ONLY = ("SET SESSION TRANSACTION READ ONLY", "START TRANSACTION READ ONLY")
+
+    def __init__(self, conn: _FakeConnection) -> None:
+        self.conn, self.description, self._rows = conn, None, []
+
+    def execute(self, sql: str, params=()) -> None:
+        self.conn.module.statements.append(sql)
+        if sql in self.READ_ONLY:
+            return
+        if not sql.lstrip().upper().startswith("SELECT") or "?" in sql:
+            raise RuntimeError("the double runs SELECTs in the %s paramstyle only")
+        cur = self.conn.conn.execute(sql.replace("%s", "?"), tuple(params))
+        self.description, self._rows = cur.description, cur.fetchall()
+
+    def fetchall(self):
+        return list(self._rows)
+
+    def close(self) -> None:
+        pass
+
+
+def _mariadb_install(tmp: Path, *, url_line: str | None = "!secret recorder_db_url",
+                     empty_window: bool = False) -> Path:
+    """The owner's layout, invented: a synthetic recorder moved to where the
+    MariaDB double reads it, a stale SQLite file of two early-2025 rows left at
+    ``home-assistant_v2.db``, and configuration.yaml naming the database."""
+    import shutil
+    import sqlite3
+    import synthesize
+
+    db = synthesize.write_install(tmp)
+    backing = tmp / "mariadb-backing.db"
+    shutil.copy(db, backing)
+    stale = sqlite3.connect(db)
+    stale.execute("DELETE FROM states WHERE state_id NOT IN "
+                  "(SELECT MIN(state_id) FROM states GROUP BY metadata_id LIMIT 2)")
+    stale.execute("UPDATE states SET last_updated_ts = 1736500000.0, last_reported_ts = NULL")
+    stale.commit()
+    stale.close()
+    if empty_window:
+        conn = sqlite3.connect(backing)
+        start = synthesize.DAY.timestamp()
+        conn.execute("DELETE FROM states WHERE last_updated_ts >= ?", (start,))
+        conn.execute("UPDATE states SET last_reported_ts = NULL")
+        conn.commit()
+        conn.close()
+    if url_line is not None:
+        (tmp / "configuration.yaml").write_text(
+            _CONFIGURATION_YAML.replace("!secret recorder_db_url", url_line))
+        (tmp / "secrets.yaml").write_text(f'recorder_db_url: "{_DB_URL}"\nother: x\n')
+    return backing
+
+
+def _export_mariadb(fake: _FakeMySQL | None, tmp: Path, db: Path | None = None,
+                    db_url: str | None = None) -> tuple[dict | None, str]:
+    """``export.main`` over ``tmp`` with ``MySQLdb`` (and ``pymysql``) replaced
+    by ``fake``, None for neither installed: the document and every line it
+    printed, or None and the refusal."""
+    import export
+    import synthesize
+
+    saved = {m: sys.modules.get(m) for m in ("MySQLdb", "pymysql")}
+    sys.modules["MySQLdb"] = fake  # type: ignore[assignment]
+    sys.modules["pymysql"] = None  # type: ignore[assignment]
+    out = tmp / "out.json"
+    argv = ["--config-dir", str(tmp), "--days", "1",
+            "--end", (synthesize.DAY + timedelta(days=1)).date().isoformat(), "--out", str(out)]
+    argv += ["--db", str(db)] if db else []
+    argv += ["--db-url", db_url] if db_url else []
+    printed = io.StringIO()
+    try:
+        with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(printed):
+            export.main(argv)
+        return json.loads(out.read_text()), printed.getvalue()
+    except SystemExit as err:
+        return None, printed.getvalue() + f"refused: {err}"
+    finally:
+        for name, module in saved.items():
+            if module is None:
+                sys.modules.pop(name, None)
+            else:
+                sys.modules[name] = module
+
+
+def _in_window(doc: dict) -> dict[str, int]:
+    """Rows of each input stamped inside the window, updated or reported."""
+    start = _ts(doc["window"]["start"])
+    return {eid: sum(1 for r in doc["states"].get(eid, [])
+                     if _ts(r[0]) >= start or (r[3] and _ts(r[3]) >= start))
+            for eid in doc["inputs"]}
+
+
+def recorder_checks() -> list[tuple[str, bool, str]]:
+    import export
+
+    res = []
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        fake = _FakeMySQL(_mariadb_install(tmp))
+        doc, printed = _export_mariadb(fake, tmp)
+        counts = _in_window(doc) if doc else {}
+        res.append(("recorder:db_url_whole_day_read",
+                    bool(counts) and all(counts.values()) and sum(counts.values()) > 500,
+                    printed[-300:] if doc is None else f"in-window rows {sorted(counts.items())}"))
+        passed = [s for s in fake.statements if s not in _FakeCursor.READ_ONLY]
+        res.append(("recorder:db_url_read_only_session_selects_only",
+                    fake.statements[:1] == [_FakeCursor.READ_ONLY[0]] and bool(passed)
+                    and all(s.lstrip().upper().startswith("SELECT") for s in passed),
+                    f"{len(fake.statements)} statement(s), first {fake.statements[:1]}"))
+        res.append(("recorder:db_url_secret_resolved",
+                    fake.kwargs.get("user") == _CANARY_USER
+                    and fake.kwargs.get("password") == _CANARY_KEY
+                    and fake.kwargs.get("host") == "core-mariadb"
+                    and fake.kwargs.get("database") == "homeassistant",
+                    f"keys {sorted(fake.kwargs)}"))
+        written = (tmp / "out.json").read_text() if doc else ""
+        res.append(("recorder:db_url_credentials_never_printed",
+                    doc is not None and "reading the recorder" in printed
+                    and not any(c in printed + written for c in (_CANARY_KEY, _CANARY_USER)),
+                    "printed and written text searched for the user and the password"))
+        failed, why = _export_mariadb(_FakeMySQL(tmp / "mariadb-backing.db",
+                                                 fail=f"denied for {_CANARY_USER}:{_CANARY_KEY}"), tmp)
+        res.append(("recorder:db_url_connect_refusal_names_no_credential",
+                    failed is None and "MySQL/MariaDB database" in why
+                    and not any(c in why for c in (_CANARY_KEY, _CANARY_USER)), why[-200:]))
+        # The open line is constant: a recorder label (a SQLite path here) is
+        # never interpolated into stderr (code-scanning alert 47).
+        marked = tmp / "label-canary-recorder.db"
+        shutil.copy(tmp / "mariadb-backing.db", marked)
+        _, said = _export_mariadb(None, tmp, db=marked)
+        _, said_url = _export_mariadb(fake, tmp)
+        res.append(("recorder:open_line_constant_no_label",
+                    "reading the recorder\n" in said and marked.name not in said
+                    and "MySQL/MariaDB database" not in said_url,
+                    said[-200:]))
+        flag, _ = _export_mariadb(fake, tmp, db_url=_DB_URL.replace("homeassistant", "hadb"))
+        res.append(("recorder:db_url_flag_read", flag is not None
+                    and fake.kwargs.get("database") == "hadb", str(fake.kwargs.get("database"))))
+        # A SQLite recorder named by a db_url (which may come from secrets.yaml)
+        # is named by its kind; its path is printed only where the person typed it.
+        shutil.copy(tmp / "mariadb-backing.db", tmp / "url-named-recorder.db")
+        lite, said = _export_mariadb(None, tmp, db_url="sqlite:///url-named-recorder.db")
+        res.append(("recorder:sqlite_db_url_named_by_kind_not_path",
+                    lite is not None and "reading the recorder" in said
+                    and "url-named-recorder" not in said, said[-200:]))
+        missing, why = _export_mariadb(None, tmp)
+        res.append(("recorder:db_url_driver_missing_refused_by_name",
+                    missing is None and "MySQLdb" in why and "pymysql" in why, why[-200:]))
+        # The owner's layout read the old way: the stale SQLite file alone.
+        stale, why = _export_mariadb(fake, tmp, db=tmp / "home-assistant_v2.db")
+        res.append(("recorder:stale_sqlite_near_empty_day_refused",
+                    stale is None and "home-assistant_v2.db" in why
+                    and "sensor.outdoor_temp" in why, why[-300:]))
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        fake = _FakeMySQL(_mariadb_install(tmp, empty_window=True))
+        doc, why = _export_mariadb(fake, tmp)
+        res.append(("recorder:db_url_emptied_window_refused_naming_inputs_and_recorder",
+                    doc is None and "MySQL/MariaDB database" in why
+                    and "sensor.outdoor_temp" in why and "sensor.price" in why, why[-300:]))
+        # The label that no longer prints on opening still names the recorder in
+        # a refusal: by kind for a SQLite recorder a db_url names, never its path.
+        shutil.copy(tmp / "mariadb-backing.db", tmp / "url-named-recorder.db")
+        none, said = _export_mariadb(None, tmp, db_url="sqlite:///url-named-recorder.db")
+        res.append(("recorder:sqlite_db_url_refusal_names_kind_not_path",
+                    none is None and "SQLite database" in said
+                    and "url-named-recorder" not in said, said[-200:]))
+    # A key the integration no longer reads (``heat_pump_entity``, dropped in
+    # v3.8.0 as never read) still in an old entry, its entity long unrecorded:
+    # not an input, so neither exported nor refused -- while an unrecorded
+    # entity under a key it does read is refused (the null control).
+    import synthesize
+
+    for name, key, refused in (("retired_key_left_out", "heat_pump_entity", False),
+                               ("read_key_unrecorded_refused", "heat_pump_switch_entity", True)):
+        data = synthesize.ENTRY_DATA
+        synthesize.ENTRY_DATA = {**data, key: "climate.retired_pump"}
+        try:
+            with tempfile.TemporaryDirectory() as tmp:
+                tmp = Path(tmp)
+                _mariadb_install(tmp, url_line=None)
+                doc, why = _export_mariadb(None, tmp, db=tmp / "mariadb-backing.db")
+        finally:
+            synthesize.ENTRY_DATA = data
+        blob = json.dumps(doc) if doc else ""
+        ok = (doc is None and "1 of" in why) if refused else (
+            doc is not None and "retired_pump" not in blob and "climate." not in blob
+            .replace('"climate.e_', "") and key in why)
+        res.append((f"recorder:{name}", ok, why[-300:]))
+    # configuration.yaml's spellings of the URL, and an install without one.
+    cases = {
+        "inline_quoted": ("recorder:\n  db_url: 'mysql://u:p@h/db'\n", None, "mysql://u:p@h/db"),
+        "inline_plain": ("recorder:\n    auto_purge: true\n    db_url: mysql://u:p@h/db # x\n",
+                         None, "mysql://u:p@h/db"),
+        "secret": ("recorder:\n  db_url: !secret rec\n", "rec: mysql://u:p@h/db\n",
+                   "mysql://u:p@h/db"),
+        "include": ("recorder: !include recorder.yaml\n", None, "mysql://u:p@h/inc"),
+        "nested_key_ignored": ("other:\n  recorder:\n    db_url: mysql://u:p@h/no\n", None, None),
+        "no_db_url": ("recorder:\n  purge_keep_days: 3\nlogger:\n  db_url: x\n", None, None),
+        "no_file": (None, None, None),
+    }
+    for name, (config, secrets, want) in cases.items():
+        with tempfile.TemporaryDirectory() as tmp:
+            tmp = Path(tmp)
+            if config is not None:
+                (tmp / "configuration.yaml").write_text(config)
+            if secrets is not None:
+                (tmp / "secrets.yaml").write_text(secrets)
+            (tmp / "recorder.yaml").write_text("db_url: \"mysql://u:p@h/inc\"\n")
+            got = export.recorder_url(tmp) if hasattr(export, "recorder_url") else "absent"
+            res.append((f"recorder:url_from_configuration:{name}", got == want,
+                        "matched" if got == want else "differs"))
+    return res
+
+
+#: An invented street address, in every place the owner's real one can hide.
+_STREET = "exempelgatan_12"
+
+
+def mask_checks() -> list[tuple[str, bool, str]]:
+    import export
+    import synthesize
+
+    res = []
+    fixture = json.loads((FIXTURES / "synthetic-dhw-only.json").read_text())
+    ids = set(fixture["states"]) | set(fixture["inputs"]) | set(fixture["published"])
+    entry_ids = {k: v for k, v in fixture["entry"]["data"].items() if k.endswith("_entity")}
+    res.append(("mask:entry_entities_renamed_to_their_role",
+                entry_ids.get("price_entity") == "sensor.price"
+                and entry_ids.get("outdoor_temp_entity") == "sensor.outdoor_temp"
+                and entry_ids.get("heat_pump_mode_entity") == "select.heat_pump_mode"
+                and set(entry_ids.values()) <= ids, str(sorted(entry_ids.values()))))
+    res.append(("mask:published_ids_hashed",
+                all(re.match(r"^[a-z_]+\.e_[0-9a-f]{10}$", p) for p in fixture["published"])
+                and len(fixture["published"]) == 2, str(fixture["published"])))
+
+    # An install whose ids carry the street: the price sensor and a published entity.
+    series, data, published = synthesize._series, synthesize.ENTRY_DATA, synthesize.PUBLISHED
+    price_id, pub_id = f"sensor.nordpool_{_STREET}", f"sensor.{_STREET}_heat_pump_action"
+
+    def patched(series=series):
+        out = series()
+        out[price_id] = out.pop("sensor.nordpool_kwh_se3_sek")
+        out[pub_id] = out.pop("sensor.heat_pump_optimizer_heat_pump_action")
+        for eid, rows in out.items():
+            out[eid] = [(t, st, {**a, "friendly_name": "Exempelgatan 12 " + eid[:6]})
+                        for t, st, a in rows]
+        return out
+
+    synthesize._series = patched
+    synthesize.ENTRY_DATA = {**data, "price_entity": price_id}
+    synthesize.PUBLISHED = (pub_id, published[1])
+    try:
+        with tempfile.TemporaryDirectory() as tmp:
+            db = synthesize.write_install(Path(tmp))
+            payload = export.build_export(
+                Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
+                None, [], None)
+        blob = json.dumps(payload).lower()
+        outcome = "written"
+    except SystemExit as err:
+        payload, blob, outcome = None, "", f"refused: {err}"
+    finally:
+        synthesize._series, synthesize.ENTRY_DATA, synthesize.PUBLISHED = series, data, published
+    res.append(("mask:street_in_entity_ids_and_names_absent_from_export",
+                payload is not None and "exempelgatan" not in blob
+                and payload["entry"]["data"]["price_entity"] == "sensor.price"
+                and "sensor.price" in payload["states"], outcome))
+
+    # Put back by hand: the check refuses, naming the class and never the token.
+    planted = json.loads(json.dumps(fixture))
+    planted["states"][f"sensor.{_STREET}_power"] = planted["states"].pop("sensor.heat_pump_power")
+    planted["entry"]["data"]["heat_pump_power_entity"] = f"sensor.{_STREET}_power"
+    # A broken rule inside that state, so a message's path carries the id itself.
+    planted["states"][f"sensor.{_STREET}_power"][0][2] = {"colour": "red"}
+    found = export.check_file(_written(planted), export.entry_keys(*export.default_const_paths()))
+    joined = "; ".join(found)
+    res.append(("mask:check_refuses_unmapped_id_naming_class_not_token",
+                "not masked" in joined and "address-like" in joined
+                and "exempelgatan" not in joined.lower(), joined[:300]))
+    texted = json.loads(json.dumps(fixture))
+    texted["states"][sorted(texted["states"])[0]][0][1] = "Exempelgatan 12"
+    found = export.check_file(_written(texted), export.entry_keys(*export.default_const_paths()))
+    joined = "; ".join(found)
+    res.append(("mask:check_refuses_address_text_naming_class_not_token",
+                "address-like" in joined and "exempelgatan" not in joined.lower(), joined[:300]))
+    # seal() on a document that skipped the mask.
+    unmasked = json.loads(json.dumps(planted))
+    try:
+        export._doc.seal(unmasked, export.entry_keys(*export.default_const_paths()))
+        why = "sealed"
+    except export._doc.Refused as err:
+        why = str(err)
+    res.append(("mask:seal_refuses_unmapped_id_naming_class_not_token",
+                why != "sealed" and "not masked" in why and "exempelgatan" not in why.lower(),
+                why[:300]))
+    # A document whose times a writer nulled (the 2026-10-31 export) is refused.
+    nulled = json.loads(json.dumps(fixture))
+    nulled["window"]["start"] = None
+    for rows in nulled["states"].values():
+        for r in rows:
+            r[0] = None
+    found = export.check_file(_written(nulled))
+    res.append(("mask:check_refuses_a_document_with_its_times_nulled",
+                "window.start: not an ISO time" in found
+                and any(f.startswith("states: ") and "no ISO update time" in f for f in found),
+                "; ".join(found[-2:])))
+    res.append(("mask:null_committed_fixture_passes_the_check",
+                not export.check_file(FIXTURES / "synthetic-dhw-only.json"), "check_file"))
+    return res + mask_seam_checks()
+
+
+def mask_seam_checks() -> list[tuple[str, bool, str]]:
+    """Every place an id can sit, each alone: ``mask_ids`` renames it and
+    ``mask_violations`` refuses it unrenamed -- a dict key anywhere (an
+    attribute keyed by entity id, not only ``states``), a list item, a
+    ``states`` key; an ``_entities`` list's ids take their numbered role; a
+    payload that is not a document has no id to refuse; and a credential's copy
+    inside a list is dropped. R10-REPLAY-REAL-DAY round 2 (the seven sites
+    ``mutation-autofix`` left unpinned at 4c994241d)."""
+    from heatpump_optimizer import replay_doc as doc_mod
+
+    res = []
+    street = f"sensor.{_STREET}"
+    keyed = {"entry": {"data": {}}, "states": {},
+             "attrs": {f"{street}_a": {"state": "on"}}}
+    masked = doc_mod.mask_ids(keyed, "01JX")
+    res.append(("mask:id_as_any_dict_key_renamed_and_refused_unrenamed",
+                _STREET not in json.dumps(masked) and not doc_mod.mask_violations(masked)
+                and bool(doc_mod.mask_violations(keyed)),
+                f"masked keys {sorted(masked['attrs'])}; unrenamed refused "
+                f"{len(doc_mod.mask_violations(keyed))}"))
+    for name, alone in (("list_item", {"entry": {}, "attrs": [f"{street}_b"]}),
+                        ("states_key", {"entry": {}, "states": {f"{street}_c": []}})):
+        res.append((f"mask:id_only_as_a_{name}_refused",
+                     bool(doc_mod.mask_violations(alone)) and not doc_mod.mask_violations(
+                         doc_mod.mask_ids(alone, "01JX")), name))
+    roles = doc_mod.entity_roles({"data": {"room_sensor_entities": ["sensor.a", "sensor.b"]}},
+                                 None)
+    res.append(("mask:entities_list_ids_take_their_numbered_role",
+                roles == {"sensor.a": "sensor.room_sensor_n1", "sensor.b": "sensor.room_sensor_n2"},
+                str(roles)))
+    try:
+        stray = doc_mod.mask_violations([f"{street}_d"])
+    except Exception as err:  # noqa: BLE001 - a raise is the observation
+        stray = [f"raised {type(err).__name__}"]
+    res.append(("mask:a_payload_that_is_no_document_has_no_violation", stray == [],
+                f"a list payload: {stray}"))
+    # Carry 12 (D15-s1-04): a bool under a credential-named key carries no
+    # credential -- ``_collect_strings`` already skips it, and ``_walk`` must
+    # agree -- while a string under one still does (the null).
+    flag, token = (doc_mod.violations({"tibber_reauth_started": v}) for v in (True, False)), \
+        doc_mod.violations({"tibber_token": "abc123xyz"})
+    flags = [f for found_ in flag for f in found_]
+    res.append(("leak_copy:bool_under_a_credential_key_is_no_credential",
+                flags == [] and any("credential-named" in f for f in token),
+                f"bool {flags}; string {token}"))
+    found: dict[str, set[int]] = {}
+    scanned = doc_mod._scan({"attrs": {"options": ["off", _TOKEN]}}, "", found,
+                            [doc_mod._copy(_TOKEN)])
+    res.append(("leak_copy:copy_inside_a_list_dropped",
+                scanned == {"attrs": {"options": ["off", None]}} and not found, str(scanned)))
+    return res
+
+
+#: An invented Tibber token: letters first, no run of four digits, short enough
+#: to pass as a unit -- so a copy of it in a kept attribute is not dropped by its
+#: shape, only by the leak check.
+_TOKEN = "Tk9xQzR2bXcK"
+
+
+def _sealed(states: dict, entry_data: dict) -> tuple[dict | None, str]:
+    """``replay_doc.document`` then ``seal``, as both writers call them."""
+    import export
+
+    raw = export._doc.document(
+        time_zone="UTC", window=("2026-01-15T00:00:00+00:00", "2026-01-16T00:00:00+00:00"),
+        recorder_schema=48, entry={"entry_id": "01JX", "data": entry_data, "options": {}},
+        inputs=[k for k in states if k != "sensor.hpo_out"], published=["sensor.hpo_out"],
+        price_series_entity=None, states=states)
+    try:
+        return export._doc.seal(raw, export.entry_keys(*export.default_const_paths())), ""
+    except export._doc.Refused as err:
+        return None, str(err)
+
+
+def leak_copy_checks() -> list[tuple[str, bool, str]]:
+    """A value dropped as a credential, with a copy elsewhere: a copy in a kept
+    string is dropped too; one that cannot be dropped (a number) is refused,
+    naming where it sits and never the value; and a dropped word Home
+    Assistant uses as a state is not a credential to search for."""
+    t = "2026-01-15T01:00:00+00:00"
+    row = lambda state, attrs: [t, state, attrs, None]  # noqa: E731
+    base = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
+    res = []
+    # The token in the entry and, by an integration that copies it, in a unit.
+    doc, why = _sealed({"sensor.indoor": [row("21.5", {"unit_of_measurement": _TOKEN})],
+                        "sensor.outdoor": [row("-3.0", None)], "sensor.hpo_out": []},
+                       {**base, "tibber_token": _TOKEN})
+    res.append(("leak_copy:string_copy_in_attribute_dropped",
+                doc is not None and _TOKEN not in json.dumps(doc)
+                and doc["states"]["sensor.indoor_temp"][0][2] == {"unit_of_measurement": None},
+                why or "sealed"))
+    # A numeric PIN, its number also a recorded attribute: refused with the place.
+    doc, why = _sealed({"sensor.indoor": [row("21.5", {"temperature": 4829137})],
+                        "sensor.outdoor": [row("-3.0", None)], "sensor.hpo_out": []},
+                       {**base, "door_pin": 4829137})
+    res.append(("leak_copy:number_copy_refused_naming_its_place_not_its_value",
+                doc is None and "states[sensor.indoor_temp].attributes.temperature" in why
+                and "4829137" not in why, why))
+    # The null control: the number inside a longer one is no copy of it.
+    doc, why = _sealed({"sensor.indoor": [row("21.5", {"temperature": 14829137.5})],
+                        "sensor.outdoor": [row("-3.0", None)], "sensor.hpo_out": []},
+                       {**base, "door_pin": 4829137})
+    res.append(("leak_copy:null_number_inside_a_longer_one_sealed", doc is not None, why))
+    # A text state dropped for its shape ("2026-01", a firmware date) is no
+    # credential: its copy inside every ISO time must neither refuse nor null them.
+    doc, why = _sealed({"sensor.indoor": [row("21.5", None)],
+                        "sensor.outdoor": [row("2026-01", None), row("-3.0", None)],
+                        "sensor.hpo_out": []}, base)
+    res.append(("leak_copy:dropped_text_inside_timestamps_keeps_them",
+                doc is not None and doc["window"]["start"] is not None
+                and all(r[0] == t for rows in doc["states"].values() for r in rows)
+                and doc["states"]["sensor.outdoor_temp"][0][1] is None, why or "sealed"))
+    # The same text under a credential key: its copy in a time is chance, not a leak.
+    doc, why = _sealed({"sensor.indoor": [row("21.5", {"serial": "2026-01"})],
+                        "sensor.outdoor": [row("-3.0", None)], "sensor.hpo_out": []}, base)
+    res.append(("leak_copy:credential_text_inside_timestamps_keeps_them",
+                doc is not None and doc["window"]["start"] is not None
+                and all(r[0] == t for rows in doc["states"].values() for r in rows),
+                why or "sealed"))
+    # A device's serial attribute reading "unavailable", and states that do.
+    doc, why = _sealed({"sensor.indoor": [row("unavailable", {"serial_number": "unavailable"})],
+                        "sensor.outdoor": [row("unknown", {"serial": "unknown"})],
+                        "sensor.hpo_out": []}, base)
+    res.append(("leak_copy:state_words_under_a_credential_key_not_searched",
+                doc is not None and doc["states"]["sensor.indoor_temp"][0][1] == "unavailable",
+                why or "sealed"))
+    return res
+
+
+def _week_doc() -> dict:
+    """Two invented days of a sealed export: a thermometer every five minutes
+    with its unit on the first row only, the away switch and its return time
+    set together on day two (a restart's ``unavailable`` between), and a
+    second switch the owner toggled on its own."""
+    tz = "Europe/Stockholm"
+    t0 = datetime(2026, 10, 29, tzinfo=timezone(timedelta(hours=1)))
+
+    def at(minutes: float) -> str:
+        return (t0 + timedelta(minutes=minutes)).isoformat()
+
+    thermo = [[at(m), f"{20 + (m % 60) / 100:.2f}", {"unit_of_measurement": "°C"} if m == 0
+               else None, None] for m in range(-30, 48 * 60, 5)]
+    away_on, other_on = 24 * 60 + 16 * 60 + 42.9, 20 * 60 + 59
+    return {"format": "hpo-replay/1", "time_zone": tz, "recorder_schema": 53,
+            "window": {"start": t0.isoformat(), "end": (t0 + timedelta(days=2)).isoformat()},
+            "entry": {"data": {"indoor_temp_entity": "sensor.indoor_temp"}, "options": {}},
+            "inputs": ["sensor.indoor_temp", "sensor.price"], "price_series_entity": "sensor.price",
+            "published": ["datetime.e_00000000aa", "switch.e_00000000bb", "switch.e_00000000cc"],
+            "states": {
+                "sensor.indoor_temp": thermo,
+                "sensor.price": [[at(h * 60), f"{1 + h / 100:.2f}", None, None]
+                                 for h in range(-1, 48)],
+                "datetime.e_00000000aa": [[at(-30), "unknown", None, None],
+                                          [at(away_on), "2026-10-31T19:00:00+00:00", None, None],
+                                          [at(away_on + 60), "unavailable", None, None],
+                                          [at(away_on + 61), "2026-10-31T19:00:00+00:00", None, None],
+                                          [at(away_on + 177), "unknown", None, None]],
+                "switch.e_00000000bb": [[at(-30), "off", None, None], [at(away_on), "on", None, None],
+                                        [at(away_on + 60), "unavailable", None, None],
+                                        [at(away_on + 61), "on", None, None],
+                                        [at(away_on + 177), "off", None, None]],
+                "switch.e_00000000cc": [[at(-30), "off", None, None], [at(other_on), "on", None, None],
+                                        [at(other_on + 123), "off", None, None],
+                                        [at(away_on + 60), "unavailable", None, None],
+                                        [at(away_on + 61), "off", None, None]]}}
+
+
+def cut_day_checks() -> list[tuple[str, bool, str]]:
+    """``tools/replay/cut_day.py``: the cut answers every cycle instant as the
+    whole export does, keeps no published entity, and replays the owner's away
+    command from the one switch that turned on with the return time."""
+    import cut_day
+
+    doc, res = _week_doc(), []
+    day = cut_day.cut(doc, "2026-10-30")
+    whole, cut = Recording(doc["states"]), Recording(day["states"])
+    instants = cut_day.grid(_ts(day["window"]["start"]), _ts(day["window"]["end"]))
+    same = [whole.at("sensor.indoor_temp", t) == cut.at("sensor.indoor_temp", t)
+            for t in instants]
+    rows = len(day["states"]["sensor.indoor_temp"])
+    res.append(("cut_day:every_cycle_instant_reads_as_the_whole_export",
+                len(instants) == 96 and all(same) and rows <= 97
+                and day["states"]["sensor.indoor_temp"][0][2] == {"unit_of_measurement": "°C"},
+                f"{sum(same)}/{len(instants)} instants equal, {rows} rows kept of "
+                f"{len(doc['states']['sensor.indoor_temp'])}"))
+    first = cut_day.cut(doc, "2026-10-29")
+    ahead = [whole.at("sensor.price", t) == Recording(first["states"]).at("sensor.price", t)
+             for t in cut_day.grid(_ts(first["window"]["start"]), _ts(doc["window"]["end"]))]
+    res.append(("cut_day:price_series_kept_to_the_export_end",
+                len(ahead) == 192 and all(ahead), f"{sum(ahead)}/{len(ahead)} quarters equal"))
+    res.append(("cut_day:no_published_entity_kept",
+                day["published"] == [] and set(day["states"]) == {"sensor.indoor_temp",
+                                                                  "sensor.price"},
+                str(sorted(day["states"]))))
+    events = day["controls"]["away"]
+    res.append(("cut_day:away_command_from_the_paired_switch_restart_skipped",
+                [e[1:] for e in events] == [[True, "2026-10-31T19:00:00+00:00"], [False, None]]
+                and events[0][0].startswith("2026-10-30T16:42"), str(events)))
+    res.append(("cut_day:reload_is_every_published_entity_gone_and_no_input",
+                day["controls"]["reloads"] == [(t0_day2 := _ts(events[0][0]).replace(
+                    second=0, microsecond=0) + timedelta(minutes=60)).isoformat()],
+                str(day["controls"]["reloads"])))
+    restart = json.loads(json.dumps(doc))
+    restart["states"]["sensor.indoor_temp"].append(
+        [t0_day2.isoformat(), "unavailable", None, None])
+    restart["states"]["sensor.indoor_temp"].sort(key=lambda r: r[0])
+    res.append(("cut_day:null_restart_with_inputs_gone_is_no_reload",
+                cut_day.cut(restart, "2026-10-30")["controls"]["reloads"] == [],
+                str(cut_day.cut(restart, "2026-10-30")["controls"]["reloads"])))
+    res.append(("cut_day:null_day_without_a_command_has_none",
+                cut_day.cut(doc, "2026-10-29")["controls"] == {"away": [], "reloads": []},
+                str(cut_day.cut(doc, "2026-10-29")["controls"])))
+    twin = json.loads(json.dumps(doc))
+    twin["states"]["switch.e_00000000cc"] = doc["states"]["switch.e_00000000bb"]
+    try:
+        cut_day.cut(twin, "2026-10-30")
+        why = "cut"
+    except SystemExit as err:
+        why = str(err)
+    res.append(("cut_day:two_paired_switches_refused", "expected exactly one" in why, why))
+    return res
+
+
+def _written(doc: dict) -> Path:
+    """``doc`` in a file of its own, for ``export.check_file``."""
+    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
+    with handle:
+        json.dump(doc, handle)
+    return Path(handle.name)
+
+
 def synthetic_reproduces() -> tuple[str, bool, str]:
     """In this process, so a recorder of this interpreter sees both files read."""
     import synthesize
@@ -978,7 +1776,21 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
     cm._ensure_worker = lambda: worker
     inject_cost(cm, inject)
 
-    hass = FakeHass()
+    class RestoringHass(FakeHass):
+        """``FakeHass`` that keeps the session restore a coordinator spawns -- the
+        stored away override and boosts a reload's new entry reads back -- for
+        ``set_up`` to run once the constructor has returned, as Home Assistant's
+        loop runs the task after it; every other spawn is closed as before."""
+
+        restores: list = []
+
+        def async_create_task(self, coro, name=None, eager_start=None):
+            if getattr(coro, "__name__", "") != "restore_session":
+                return super().async_create_task(coro)
+            self.restores.append(coro)
+            return None
+
+    hass = RestoringHass()
     # Executor jobs run inline on this thread in the double, so the loop
     # thread's own work is the cycle's thread CPU less theirs.
     _EXEC_CPU[0] = 0.0
@@ -1018,36 +1830,51 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
         hass.services.async_register("weather", "get_forecasts", forecasts)
 
     entry = FakeEntry(data=entry_data, options=entry_options)
-    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
-    entry.runtime_data = coord
-
     price_series = fixture.get("price_series_entity")
-    if not cm._entity_price_source(config):
-        async def recorded_prices() -> None:
-            now = dt_util.now()
-            day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
-            span = 2 if now.hour >= 13 else 1
-            rows = []
-            # The day's quarters walked in UTC: a wall-clock walk invents the
-            # spring gap's four quarters and folds the autumn hour onto one.
-            t = dt_util.as_utc(day0)
-            while t < day0 + timedelta(days=span):
-                row = rec.at(price_series, t) if price_series else None
-                value = _num(row[1]) if row else None
-                if value is not None:
-                    rows.append({"total": value, "starts_at": dt_util.as_local(t).isoformat(),
-                                 "level": "NORMAL"})
-                t += timedelta(minutes=15)
-            if not rows:
-                raise UpdateFailed("the fixture records no price series")
-            coord._prices = rows
-
-        coord._fetch_tibber_prices = recorded_prices
-
-    entities: list = []
-    for platform in integration.PLATFORM_LIST:
-        module = importlib.import_module(f"heatpump_optimizer.{str(platform)}")
-        asyncio.run(module.async_setup_entry(hass, entry, entities.extend))
+
+    def set_up(**kwargs):
+        """The coordinator and its entities, as ``async_setup_entry`` builds them;
+        a reload passes ``skip_first_solve`` and the last publish as the handover."""
+        coord = cm.HeatPumpOptimizerCoordinator(hass, entry, **kwargs)
+        entry.runtime_data = coord
+        while hass.restores:
+            asyncio.run(hass.restores.pop(0))
+
+        async def no_solar_fetch() -> None:
+            # A fixture records no irradiance, and the lane opens no socket: an
+            # install on the Open-Meteo source replays with no solar forecast.
+            coord._open_meteo = None
+
+        coord._fetch_solar_forecast = no_solar_fetch
+        if not cm._entity_price_source(config):
+            async def recorded_prices() -> None:
+                now = dt_util.now()
+                day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
+                span = 2 if now.hour >= 13 else 1
+                rows = []
+                # The day's quarters walked in UTC: a wall-clock walk invents the
+                # spring gap's four quarters and folds the autumn hour onto one.
+                t = dt_util.as_utc(day0)
+                while t < day0 + timedelta(days=span):
+                    row = rec.at(price_series, t) if price_series else None
+                    value = _num(row[1]) if row else None
+                    if value is not None:
+                        rows.append({"total": value, "starts_at": dt_util.as_local(t).isoformat(),
+                                     "level": "NORMAL"})
+                    t += timedelta(minutes=15)
+                if not rows:
+                    raise UpdateFailed("the fixture records no price series")
+                coord._prices = rows
+
+            coord._fetch_tibber_prices = recorded_prices
+
+        entities: list = []
+        for platform in integration.PLATFORM_LIST:
+            module = importlib.import_module(f"heatpump_optimizer.{str(platform)}")
+            asyncio.run(module.async_setup_entry(hass, entry, entities.extend))
+        return coord, entities
+
+    coord, entities = set_up()
 
     table = units_table()
     defaults = thermal_defaults()
@@ -1070,8 +1897,27 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
     injected: list[tuple[float, float]] = []
     peaks: list[int] = []
     traced: set[str] = set()
+    recorded_away = list((fixture.get("controls") or {}).get("away") or [])
+    away_events = list(recorded_away)
+    reloads = list((fixture.get("controls") or {}).get("reloads") or [])
+    away_seen: list[dict] = []
+    commanded: str | None = None  # the return time while the owner's command holds away
     while t < end:
         dt_util.freeze(t)
+        while away_events and _ts(away_events[0][0]) <= t:
+            # The owner's command, as the away switch and return-time entity give it.
+            _when, active, returns = away_events.pop(0)
+            commanded = returns if active else None
+            asyncio.run(coord.async_set_away(active=active, return_time=returns, refresh=False)
+                        if active else coord.async_set_away(active=False, refresh=False))
+        while reloads and _ts(reloads[0]) <= t:
+            # The integration reloaded in process (an options save): the unload
+            # hands the last publish to the new entry, which publishes it first.
+            reloads.pop(0)
+            coord, entities = set_up(skip_first_solve=True, reload_handover=coord.data)
+            # Setup's first refresh publishes without solving; the cycle's own
+            # update below is the background solve setup schedules after it.
+            coord.data = asyncio.run(coord._async_update_data())
         readings: list[float] = []
         for entity_id in fixture["inputs"]:
             row = rec.at(entity_id, t)
@@ -1109,6 +1955,7 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
             coord.last_update_success = False
             data = coord.data or {}
 
+        away_seen.append({**away_observation(data, t), "commanded_return": commanded})
         action = data.get("current_action") or {}
         records = sweep(entities, action, results["cycle"], t)
         own_loop = (time.thread_time() - began_thread) - (_EXEC_CPU[0] - exec_before)
@@ -1134,7 +1981,7 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
             loop_ref_cpu.append(reference_loop())
         results["finite"] += inv_finite(records)
         results["unit"] += inv_unit(records, table)
-        results["no_default"] += inv_no_default(records, defaults, readings)
+        results["no_default"] += inv_no_default(records, defaults, readings, config)
         results["agreement"] += [f"{t.isoformat()} {o}" for o in
                                  inv_agreement(records, plan_draws(coord, data, t),
                                                plan_draw_kw(data, t))]
@@ -1152,6 +1999,9 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
     ref_cpu += [reference_solve()[1] for _ in range(3)]
     loop_ref_cpu += [reference_loop() for _ in range(3)]
     results["not_frozen"] = frozen_offenders(pub_series, inp_series)
+    results["away"] = away_offenders(
+        away_seen, recorded_away, path.name in AWAY_COVERED
+    ) + away_coverage_offenders(path.name, recorded_away)
     figures = cost_figures(cycle_cpu, ref_cpu, peaks, loop_cpu, loop_ref_cpu)
     clean = sum(c for _, c in injected)
     share = ({"injected_ratio": round(sum(i for i, _ in injected) / clean, 4)}
@@ -1165,7 +2015,25 @@ def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None)
             "seconds": round(time.monotonic() - started, 1),
             "results": {k: v[:12] + ([f"... {len(v) - 12} more"] if len(v) > 12 else [])
                         for k, v in results.items()},
-            "counts": {k: len(v) for k, v in results.items()}}
+            "counts": {k: len(v) for k, v in results.items()},
+            "away": away_seen}
+
+
+def away_observation(data: dict, t: datetime) -> dict:
+    """One cycle's away view and the space heating its plan buys."""
+    schedule = data.get("schedule") or []
+    step_h = 0.25
+    if len(schedule) > 1:
+        step_h = (_ts(schedule[1]["time"]) - _ts(schedule[0]["time"])).total_seconds() / 3600
+    return {"t": t.isoformat(), "active": bool(data.get("away_active")),
+            "recovery": bool(data.get("away_recovery_active")),
+            "target": data.get("away_target_temperature"),
+            "floor": data.get("min_temperature"),
+            "override": bool(data.get("away_override_active")),
+            "space_kwh": round(sum(float(r.get("power") or 0.0) for r in schedule) * step_h, 2),
+            "space_slots": sum(1 for r in schedule if float(r.get("power") or 0.0) > 0.1),
+            "room_min": min((r["room_temp"] for r in schedule), default=None),
+            "horizon_h": round(len(schedule) * step_h, 2)}
 
 
 def _plan_step(data: dict, t: datetime) -> tuple[float, float] | None:
@@ -1562,6 +2430,7 @@ def main(argv: list[str] | None = None) -> int:
     name, ok, detail = synthetic_reproduces()
     R.check("the synthetic fixture is what synthesize.py + export.py write", ok, detail)
 
+    perturbed: list[str] = []
     for path in paths:
         R.section(f"replay {path.name}")
         out = replay_one(R, path, args.step_minutes, None)
@@ -1578,6 +2447,10 @@ def main(argv: list[str] | None = None) -> int:
             R.check(f"{path.name}: {name}", not offenders,
                     f"{out['counts'][name]} offender(s): " + " | ".join(offenders[:6]))
         # The perturbation, every night: a doubled cycle must be over budget.
+        if path.name in COST_ARMS_SKIPPED:
+            print(f"  doubled arms not run: {COST_ARMS_SKIPPED[path.name]}")
+            continue
+        perturbed.append(path.name)
         for kind, key in (("cpu", "cpu_ratio"), ("memory", "peak_kib"),
                           ("loop", "loop_cpu_ratio")):
             hot = replay_one(R, path, args.step_minutes, kind)
@@ -1593,6 +2466,13 @@ def main(argv: list[str] | None = None) -> int:
                 short = short_doubling(hot["cost"].get("injected_ratio", float("nan")))
                 R.check(f"{path.name}: the {kind} arm doubles the whole span {key} times",
                         not short, " | ".join(short))
+    # The arms prove the instrument sees a doubling: the skip list names only
+    # committed fixtures and leaves at least one to them, so the full lane
+    # (nightly, and every pull request that reaches it) always runs them.
+    committed = {f.name for f in FIXTURES.glob("*.json")}
+    wrong = arms_skip_offenders(set(COST_ARMS_SKIPPED), committed)
+    R.check("the doubled-cost arms are skipped on committed fixtures only, never all",
+            not wrong, " | ".join(wrong) + f"; this run perturbed {perturbed}")
     print(f"\nreplay lane wall time {time.monotonic() - began:.1f} s")
     return R.close("replay checks")
 
diff --git a/tests/replay/owner-2026-10-30-away.json b/tests/replay/owner-2026-10-30-away.json
new file mode 100644
index 000000000..129dfc29d
--- /dev/null
+++ b/tests/replay/owner-2026-10-30-away.json
@@ -0,0 +1,1934 @@
+{
+ "controls": {
+  "away": [
+   [
+    "2026-10-30T15:42:54.058467+00:00",
+    true,
+    "2026-10-31T19:00:00+00:00"
+   ],
+   [
+    "2026-10-30T18:39:25.778625+00:00",
+    false,
+    null
+   ]
+  ],
+  "reloads": [
+   "2026-10-30T15:44:00+00:00"
+  ]
+ },
+ "entry": {
+  "data": {
+   "buffer_tank_volume": 750.0,
+   "comfort_temp_day": 21.0,
+   "comfort_temp_night": 18.5,
+   "comfort_weight": 2.0,
+   "day_end_hour": 22.0,
+   "day_start_hour": 6.0,
+   "dhw_daily_consumption": 90.0,
+   "dhw_idle_min_temperature": 10.0,
+   "dhw_legionella_enabled": true,
+   "dhw_legionella_interval_days": 7.0,
+   "dhw_legionella_temperature": 60.0,
+   "dhw_min_temperature": 40.0,
+   "dhw_schedule_enabled": true,
+   "dhw_setpoint": 51.0,
+   "dhw_tank_volume": 150.0,
+   "dhw_temp_entity": "sensor.e_2e8ffac4a3",
+   "ecl110_command_topic": "ecl110/command",
+   "ecl110_displace_max": 20.0,
+   "ecl110_displace_min": -20.0,
+   "ecl110_displace_set_topic": "ecl110/flow_temp_control/displace/set",
+   "ecl110_mqtt_qos": 1.0,
+   "ecl110_mqtt_retain": false,
+   "ecl110_pid_time_constant_hours": 1.5,
+   "ecl110_state_topic": "ecl110/flow_temp_control/displace",
+   "floor_return_temp_entity": "sensor.valve_outlet_temp",
+   "heat_pump_cop_nominal": 4.0,
+   "heat_pump_max_power": 14.0,
+   "heat_pump_min_power": 1.0,
+   "heat_pump_switch_entity": "switch.heat_pump_switch",
+   "house_heat_loss_coefficient": 0.15,
+   "house_thermal_mass": 10.0,
+   "indoor_temp_entity": "sensor.lower_floor_temp",
+   "inter_zone_heat_transfer": 0.5,
+   "lower_floor_heat_loss": 0.07,
+   "lower_floor_thermal_mass": 5.0,
+   "max_temperature": 23.0,
+   "min_temperature": 17.0,
+   "optimization_interval": 30.0,
+   "outdoor_temp_entity": "sensor.outdoor_temp",
+   "price_weight": 5.0,
+   "radiator_power_fraction": 0.4,
+   "rain_heat_loss_multiplier": 1.15,
+   "slab_heat_transfer": 0.8,
+   "slab_thermal_mass": 2.0,
+   "solar_heat_gain_coefficient": 0.7,
+   "solar_orientation_factor": 0.7,
+   "target_temperature": 21.0,
+   "upper_floor_area_ratio": 0.5,
+   "upper_floor_heat_loss": 0.08,
+   "upper_floor_thermal_mass": 3.0,
+   "weather_entity": "weather.weather",
+   "wind_sensitivity_factor": 0.15,
+   "window_area": 15.0
+  },
+  "minor_version": 1,
+  "options": {
+   "away_dhw_min_temperature": 10.0,
+   "away_presence_entity": null,
+   "away_temperature": 15.0,
+   "buffer_max_temperature": 56.0,
+   "buffer_tank_temp_entity": "sensor.buffer_tank_temp",
+   "buffer_tank_volume": 500.0,
+   "building_era": "1960_1980",
+   "building_foundation": "crawlspace",
+   "building_preset_enabled": false,
+   "building_structure": "timber_crawlspace",
+   "capacity_curve_enabled": true,
+   "comfort_learning_enabled": true,
+   "comfort_temp_day": 19.5,
+   "comfort_temp_night": 18.5,
+   "comfort_weight": 2.0,
+   "compressor_cycling_cost": 0.0,
+   "compressor_freq_entity": null,
+   "compressor_freq_sensor": null,
+   "compressor_rated_starts": 100000.0,
+   "compressor_replacement_cost": 30000.0,
+   "confidence_margins_enabled": true,
+   "contract_fixed_price": 0.0,
+   "curve_learning_enabled": true,
+   "day_end_hour": 22,
+   "day_start_hour": 6,
+   "debug_collect_enabled": true,
+   "dhw_cooling_rate": 0.3,
+   "dhw_daily_consumption": 90.0,
+   "dhw_disinfection_mode": "control",
+   "dhw_disinfection_switch_entity": "switch.dhw_disinfection_switch",
+   "dhw_elastic_legionella_enabled": true,
+   "dhw_enabled": true,
+   "dhw_free_disinfection_enabled": true,
+   "dhw_idle_min_temperature": 11.0,
+   "dhw_inlet_entity": null,
+   "dhw_inlet_seasonal_amplitude": 0.0,
+   "dhw_inlet_temp": 10.0,
+   "dhw_legionella_enabled": true,
+   "dhw_legionella_interval_days": 7.0,
+   "dhw_legionella_min_interval_days": 5.0,
+   "dhw_legionella_temperature": 55.0,
+   "dhw_min_temperature": 45.0,
+   "dhw_quantile_targets_enabled": false,
+   "dhw_schedule_enabled": true,
+   "dhw_setpoint": 57.0,
+   "dhw_setpoint_entity": "number.dhw_setpoint",
+   "dhw_tank_volume": 150.0,
+   "dhw_temp_entity": "sensor.dhw_temp",
+   "dhw_windows": null,
+   "dhw_windows_by_day": true,
+   "dhw_wood_coil_enabled": true,
+   "ecl110_command_topic": "ecl110/command",
+   "ecl110_displace_max": 20.0,
+   "ecl110_displace_min": -20.0,
+   "ecl110_displace_set_topic": "ecl110/flow_temp_control/displace/set",
+   "ecl110_mqtt_qos": 1.0,
+   "ecl110_mqtt_retain": false,
+   "ecl110_pid_time_constant_hours": 1.5,
+   "ecl110_state_topic": "ecl110/flow_temp_control/displace",
+   "external_heat_decay_minutes": 90.0,
+   "external_heat_detection_enabled": true,
+   "external_heat_entity": null,
+   "external_heat_min_rise": 1.5,
+   "floor_return_temp_entity": "sensor.floor_return_temp",
+   "freq_control_mode": "observe",
+   "fuse_guard_enabled": true,
+   "greywater_recovery_effectiveness": 0.0,
+   "grid_fee_entity": null,
+   "grid_fee_fixed": 1.0,
+   "grid_fee_mode": "none",
+   "heat_pump_backup_heater_entity": "switch.heat_pump_backup_heater",
+   "heat_pump_capacity_limited_entity": "switch.heat_pump_capacity_limited",
+   "heat_pump_cop_nominal": 4.0,
+   "heat_pump_defrost_entity": "binary_sensor.heat_pump_defrost",
+   "heat_pump_dhw_booster_entity": "switch.heat_pump_dhw_booster",
+   "heat_pump_energy_entity": null,
+   "heat_pump_fault_entity": "binary_sensor.heat_pump_fault",
+   "heat_pump_max_power": 4.0,
+   "heat_pump_min_power": 0.5,
+   "heat_pump_mode_entity": "select.heat_pump_mode",
+   "heat_pump_online_entity": "binary_sensor.heat_pump_online",
+   "heat_pump_power_entity": "sensor.heat_pump_power",
+   "heat_pump_return_temp_entity": "sensor.floor_return_temp",
+   "heat_pump_supply_temp_entity": "sensor.heat_pump_supply_temp",
+   "heat_pump_switch_entity": "switch.heat_pump_switch",
+   "heated_area_m2": 140.0,
+   "holiday_calendar_entity": null,
+   "holiday_dhw_windows": "",
+   "house_heat_loss_coefficient": 0.12,
+   "house_power_entity": null,
+   "house_thermal_mass": 2.52,
+   "immersion_feedback_enabled": false,
+   "indoor_humidity_entity": "sensor.indoor_humidity",
+   "indoor_temp_entity": "sensor.indoor_temp",
+   "inter_zone_heat_transfer": 0.5,
+   "internal_gains_learning_enabled": true,
+   "lower_floor_emitter": "floor",
+   "lower_floor_heat_loss": 0.08,
+   "lower_floor_temp_entity": "sensor.lower_floor_temp",
+   "lower_floor_thermal_mass": 1.5,
+   "main_fuse_amperes": 25.0,
+   "main_fuse_phases": 3.0,
+   "max_temperature": 21.0,
+   "min_temperature": 18.0,
+   "mixing_valve_mode": "manual",
+   "mixing_valve_target": 21.0,
+   "mixing_valve_target_entity": null,
+   "mixing_valve_write_entity": null,
+   "mixing_valve_write_target_kind": "indoor",
+   "mold_guard_enabled": true,
+   "open_window_relax_enabled": true,
+   "optimization_interval": 15.0,
+   "outage_recovery_enabled": false,
+   "outdoor_temp_entity": "sensor.outdoor_temp",
+   "peak_guard_enabled": false,
+   "peak_guard_margin_kw": 0.5,
+   "peak_tariff_enabled": true,
+   "peak_tariff_hours": "",
+   "peak_tariff_months": "",
+   "peak_tariff_offpeak_factor": 1.0,
+   "peak_tariff_peaks_averaged": 3.0,
+   "peak_tariff_price_per_kw": 45.0,
+   "peak_tariff_weekdays_only": false,
+   "peak_tariff_window_minutes": 15,
+   "precip_type_enabled": true,
+   "prefill_offer": true,
+   "price_prior_enabled": true,
+   "price_risk_lambda": 1.0,
+   "price_tiles_enabled": true,
+   "price_weight": 5.0,
+   "pump_duty_mode": "control",
+   "pv_enabled": false,
+   "pv_export_price": 0.0,
+   "pv_export_price_entity": null,
+   "pv_peak_kw": 0.0,
+   "pv_production_entity": null,
+   "pv_system_efficiency": 0.8,
+   "quiet_off_windows": "",
+   "radiator_power_fraction": 0.5,
+   "rain_heat_loss_multiplier": 1.15,
+   "shower_flow_lpm": 8.0,
+   "silent_mode_power_fraction": 0.9,
+   "slab_heat_transfer": 0.7,
+   "slab_thermal_mass": 2.0,
+   "snow_roof_factor_enabled": true,
+   "solar_aperture_learning_enabled": true,
+   "solar_forecast_source": "open_meteo",
+   "solar_heat_gain_coefficient": 0.6,
+   "solar_location": {
+    "latitude": 60.06,
+    "longitude": 17.0
+   },
+   "solar_orientation_factor": 0.7,
+   "solar_radiation_entity": null,
+   "space_circulation_pump_entity": null,
+   "space_setpoint_entity": "number.space_setpoint",
+   "space_setpoint_unit": "flow",
+   "staleness_max_age_scale": 1.0,
+   "staleness_watchdog_enabled": true,
+   "system_identification_enabled": true,
+   "target_temperature": 19.5,
+   "thermal_bridge_frsi": 0.7,
+   "topology_layout": "two_tank_4way",
+   "topology_positions": {
+    "buffer_tank": [
+     260.0,
+     157.0
+    ],
+    "dhw_tank": [
+     260.0,
+     298.0
+    ],
+    "heat_pump": [
+     16.0,
+     157.0
+    ],
+    "lower_zone": [
+     504.0,
+     111.0
+    ],
+    "mixing_valve": [
+     260.0,
+     16.0
+    ],
+    "outdoor": [
+     16.0,
+     354.0
+    ],
+    "upper_zone": [
+     504.0,
+     16.0
+    ],
+    "wood_tank": [
+     16.0,
+     16.0
+    ]
+   },
+   "two_zone_mode": "on",
+   "upper_floor_area_ratio": 0.5,
+   "upper_floor_emitter": "radiators",
+   "upper_floor_heat_loss": 0.06,
+   "upper_floor_thermal_mass": 1.26,
+   "valve_outlet_temp_entity": "sensor.valve_outlet_temp",
+   "vvc_lead_minutes": 20.0,
+   "vvc_pump_entity": null,
+   "wear_autotune_enabled": true,
+   "weather_entity": "weather.weather",
+   "wind_sensitivity_factor": 0.03,
+   "window_area": 14.5,
+   "wood_furnace_efficiency": 75.0,
+   "wood_furnace_enabled": true,
+   "wood_packing": "loose",
+   "wood_price_sek_m3": 800.0,
+   "wood_tank_bottom_entity": "sensor.wood_tank_bottom",
+   "wood_tank_top_entity": "sensor.wood_tank_top",
+   "wood_tank_volume": 500.0,
+   "wood_type": "mixed"
+  },
+  "version": 7
+ },
+ "format": "hpo-replay/1",
+ "inputs": [
+  "binary_sensor.heat_pump_defrost",
+  "binary_sensor.heat_pump_fault",
+  "binary_sensor.heat_pump_online",
+  "number.dhw_setpoint",
+  "number.space_setpoint",
+  "select.heat_pump_mode",
+  "sensor.indoor_humidity",
+  "sensor.indoor_temp",
+  "sensor.price",
+  "sensor.heat_pump_supply_temp",
+  "sensor.e_2e8ffac4a3",
+  "sensor.heat_pump_power",
+  "sensor.outdoor_temp",
+  "sensor.lower_floor_temp",
+  "sensor.floor_return_temp",
+  "sensor.wood_tank_top",
+  "sensor.wood_tank_bottom",
+  "sensor.buffer_tank_temp",
+  "sensor.dhw_temp",
+  "sensor.valve_outlet_temp",
+  "switch.dhw_disinfection_switch",
+  "switch.heat_pump_dhw_booster",
+  "switch.heat_pump_backup_heater",
+  "switch.heat_pump_capacity_limited",
+  "switch.heat_pump_switch",
+  "weather.weather"
+ ],
+ "price_series_entity": "sensor.price",
+ "published": [],
+ "recorder_schema": 53,
+ "states": {
+  "binary_sensor.heat_pump_defrost": [
+   [
+    "2026-10-29T20:50:13.217424+00:00",
+    "off",
+    {
+     "device_class": "cold"
+    },
+    "2026-10-29T20:51:05.664379+00:00"
+   ],
+   [
+    "2026-10-30T15:32:22.617973+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.418828+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.994796+00:00",
+    "off",
+    null,
+    "2026-10-30T16:20:36.227563+00:00"
+   ]
+  ],
+  "binary_sensor.heat_pump_fault": [
+   [
+    "2026-10-30T11:37:16.668797+00:00",
+    "off",
+    {
+     "device_class": "problem"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.617645+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.418693+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.994586+00:00",
+    "off",
+    null,
+    "2026-10-30T18:32:49.502010+00:00"
+   ],
+   [
+    "2026-10-30T18:36:11.099305+00:00",
+    "off",
+    null,
+    "2026-10-31T13:29:44.748890+00:00"
+   ]
+  ],
+  "binary_sensor.heat_pump_online": [
+   [
+    "2026-10-30T02:03:46.512139+00:00",
+    "on",
+    {
+     "device_class": "connectivity"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.617409+00:00",
+    "on",
+    null,
+    "2026-10-30T15:33:15.418578+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.994223+00:00",
+    "on",
+    null,
+    "2026-10-30T16:20:36.227478+00:00"
+   ]
+  ],
+  "number.dhw_setpoint": [
+   [
+    "2026-10-29T20:50:13.220021+00:00",
+    "57.0",
+    {
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-29T20:51:05.664875+00:00"
+   ],
+   [
+    "2026-10-30T15:32:22.622044+00:00",
+    "57.0",
+    null,
+    "2026-10-30T15:33:15.419573+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.997028+00:00",
+    "57.0",
+    null,
+    "2026-10-30T16:20:36.227940+00:00"
+   ]
+  ],
+  "number.space_setpoint": [
+   [
+    "2026-10-30T14:33:48.057992+00:00",
+    "25.0",
+    {
+     "unit_of_measurement": "\u00b0C"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:44:14.472034+00:00",
+    "35.0",
+    null,
+    "2026-10-30T15:44:14.472385+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.996814+00:00",
+    "35.0",
+    null,
+    "2026-10-30T17:54:36.744628+00:00"
+   ],
+   [
+    "2026-10-30T17:56:36.049425+00:00",
+    "47.0",
+    null,
+    "2026-10-30T18:08:32.132696+00:00"
+   ],
+   [
+    "2026-10-30T18:09:20.121551+00:00",
+    "55.0",
+    null,
+    "2026-10-31T10:33:29.724399+00:00"
+   ]
+  ],
+  "select.heat_pump_mode": [
+   [
+    "2026-10-30T14:02:20.593193+00:00",
+    "Heating",
+    {},
+    null
+   ],
+   [
+    "2026-10-30T15:44:13.614176+00:00",
+    "Heating + DHW",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:20:01.022087+00:00",
+    "Heating + DHW",
+    null,
+    "2026-10-30T17:54:31.193405+00:00"
+   ],
+   [
+    "2026-10-30T17:54:36.046892+00:00",
+    "Heating",
+    null,
+    "2026-10-31T10:33:19.170298+00:00"
+   ]
+  ],
+  "sensor.buffer_tank_temp": [
+   [
+    "2026-10-30T14:59:29.600245+00:00",
+    "39.5",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:00:24.639208+00:00"
+   ],
+   [
+    "2026-10-30T15:13:19.590575+00:00",
+    "38.62",
+    null,
+    "2026-10-30T15:14:44.617678+00:00"
+   ],
+   [
+    "2026-10-30T15:29:24.577172+00:00",
+    "37.62",
+    null,
+    "2026-10-30T15:30:49.602193+00:00"
+   ],
+   [
+    "2026-10-30T15:44:09.585181+00:00",
+    "37.0",
+    null,
+    "2026-10-30T15:46:14.051233+00:00"
+   ],
+   [
+    "2026-10-30T15:57:59.553182+00:00",
+    "36.38",
+    null,
+    "2026-10-30T15:59:59.055549+00:00"
+   ],
+   [
+    "2026-10-30T16:06:39.547543+00:00",
+    "36.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:27:44.509528+00:00",
+    "35.0",
+    null,
+    "2026-10-30T16:30:49.519717+00:00"
+   ],
+   [
+    "2026-10-30T16:43:34.488867+00:00",
+    "34.38",
+    null,
+    "2026-10-30T16:44:49.502636+00:00"
+   ],
+   [
+    "2026-10-30T16:59:19.490354+00:00",
+    "33.75",
+    null,
+    "2026-10-30T17:03:24.522406+00:00"
+   ],
+   [
+    "2026-10-30T17:13:39.635448+00:00",
+    "33.25",
+    null,
+    "2026-10-30T17:17:34.252867+00:00"
+   ],
+   [
+    "2026-10-30T17:28:09.468949+00:00",
+    "32.75",
+    null,
+    "2026-10-30T17:31:01.753557+00:00"
+   ],
+   [
+    "2026-10-30T17:43:54.447334+00:00",
+    "32.25",
+    null,
+    "2026-10-30T17:46:07.295551+00:00"
+   ],
+   [
+    "2026-10-30T17:59:49.450125+00:00",
+    "32.12",
+    null,
+    "2026-10-30T18:00:34.445684+00:00"
+   ],
+   [
+    "2026-10-30T18:14:49.438948+00:00",
+    "33.0",
+    null,
+    "2026-10-30T18:15:14.437224+00:00"
+   ],
+   [
+    "2026-10-30T18:29:44.415499+00:00",
+    "36.06",
+    null,
+    "2026-10-30T18:30:34.465201+00:00"
+   ],
+   [
+    "2026-10-30T18:44:14.406928+00:00",
+    "37.38",
+    null,
+    "2026-10-30T18:45:29.388443+00:00"
+   ]
+  ],
+  "sensor.dhw_temp": [
+   [
+    "2026-10-30T14:58:49.600784+00:00",
+    "50.0",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:06:59.594631+00:00"
+   ],
+   [
+    "2026-10-30T15:07:19.593974+00:00",
+    "49.88",
+    null,
+    "2026-10-30T15:15:14.578189+00:00"
+   ],
+   [
+    "2026-10-30T15:24:14.571814+00:00",
+    "49.62",
+    null,
+    "2026-10-30T15:31:24.559350+00:00"
+   ],
+   [
+    "2026-10-30T15:38:59.568803+00:00",
+    "49.38",
+    null,
+    "2026-10-30T15:45:14.561658+00:00"
+   ],
+   [
+    "2026-10-30T15:55:19.554893+00:00",
+    "49.12",
+    null,
+    "2026-10-30T16:00:49.550741+00:00"
+   ],
+   [
+    "2026-10-30T16:01:19.549901+00:00",
+    "49.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:29:14.519311+00:00",
+    "48.62",
+    null,
+    "2026-10-30T16:29:54.537723+00:00"
+   ],
+   [
+    "2026-10-30T16:42:54.496390+00:00",
+    "48.25",
+    null,
+    "2026-10-30T16:49:59.467721+00:00"
+   ],
+   [
+    "2026-10-30T16:56:39.548652+00:00",
+    "48.0",
+    null,
+    "2026-10-30T17:04:09.518618+00:00"
+   ],
+   [
+    "2026-10-30T17:10:09.491621+00:00",
+    "47.75",
+    null,
+    "2026-10-30T17:15:49.492739+00:00"
+   ],
+   [
+    "2026-10-30T17:29:39.468232+00:00",
+    "47.38",
+    null,
+    "2026-10-30T17:37:09.466885+00:00"
+   ],
+   [
+    "2026-10-30T17:43:54.491365+00:00",
+    "47.12",
+    null,
+    "2026-10-30T17:48:54.254105+00:00"
+   ],
+   [
+    "2026-10-30T17:55:39.453318+00:00",
+    "46.88",
+    null,
+    "2026-10-30T18:05:29.417848+00:00"
+   ],
+   [
+    "2026-10-30T18:11:04.435007+00:00",
+    "46.62",
+    null,
+    "2026-10-30T18:16:49.437306+00:00"
+   ],
+   [
+    "2026-10-30T18:28:59.429336+00:00",
+    "46.25",
+    null,
+    "2026-10-30T18:34:54.421820+00:00"
+   ],
+   [
+    "2026-10-30T18:44:54.451070+00:00",
+    "40.62",
+    null,
+    null
+   ]
+  ],
+  "sensor.e_2e8ffac4a3": [
+   [
+    "2026-10-30T14:38:02.942275+00:00",
+    "56.0",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:43:49.821927+00:00",
+    "55.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:29:58.155936+00:00",
+    "54.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:33:01.264446+00:00",
+    "54.0",
+    null,
+    "2026-10-30T17:22:01.121942+00:00"
+   ],
+   [
+    "2026-10-30T17:24:57.798224+00:00",
+    "53.0",
+    null,
+    "2026-10-30T18:11:01.209465+00:00"
+   ],
+   [
+    "2026-10-30T18:13:20.161735+00:00",
+    "52.0",
+    null,
+    "2026-10-30T18:40:44.903701+00:00"
+   ],
+   [
+    "2026-10-30T18:44:28.389500+00:00",
+    "44.0",
+    null,
+    "2026-10-30T18:46:36.547647+00:00"
+   ]
+  ],
+  "sensor.floor_return_temp": [
+   [
+    "2026-10-30T14:56:46.703396+00:00",
+    "35.0",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:01:24.811598+00:00"
+   ],
+   [
+    "2026-10-30T15:13:19.587478+00:00",
+    "32.0",
+    null,
+    "2026-10-30T15:19:54.837489+00:00"
+   ],
+   [
+    "2026-10-30T15:26:57.147883+00:00",
+    "30.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T15:42:12.874185+00:00",
+    "28.0",
+    null,
+    "2026-10-30T15:49:02.770053+00:00"
+   ],
+   [
+    "2026-10-30T15:57:46.598116+00:00",
+    "26.0",
+    null,
+    "2026-10-30T16:06:27.239941+00:00"
+   ],
+   [
+    "2026-10-30T16:06:29.460364+00:00",
+    "25.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:27:17.922351+00:00",
+    "23.0",
+    null,
+    "2026-10-30T16:37:01.035621+00:00"
+   ],
+   [
+    "2026-10-30T16:37:30.046047+00:00",
+    "22.0",
+    null,
+    "2026-10-30T16:48:31.057091+00:00"
+   ],
+   [
+    "2026-10-30T16:48:41.450290+00:00",
+    "21.0",
+    null,
+    "2026-10-30T17:01:01.081385+00:00"
+   ],
+   [
+    "2026-10-30T17:14:19.539560+00:00",
+    "19.0",
+    null,
+    "2026-10-30T17:27:31.129962+00:00"
+   ],
+   [
+    "2026-10-30T17:27:43.104089+00:00",
+    "18.0",
+    null,
+    "2026-10-30T17:42:01.155630+00:00"
+   ],
+   [
+    "2026-10-30T17:42:28.712095+00:00",
+    "17.0",
+    null,
+    "2026-10-30T17:54:47.672094+00:00"
+   ],
+   [
+    "2026-10-30T17:56:32.172901+00:00",
+    "31.0",
+    null,
+    "2026-10-30T18:08:31.205611+00:00"
+   ],
+   [
+    "2026-10-30T18:08:49.444428+00:00",
+    "32.0",
+    null,
+    "2026-10-30T18:17:37.313315+00:00"
+   ],
+   [
+    "2026-10-30T18:24:06.354469+00:00",
+    "34.0",
+    null,
+    "2026-10-30T18:31:05.369082+00:00"
+   ],
+   [
+    "2026-10-30T18:44:56.337954+00:00",
+    "36.0",
+    null,
+    "2026-10-30T18:45:22.456416+00:00"
+   ]
+  ],
+  "sensor.heat_pump_power": [
+   [
+    "2026-10-30T14:34:02.019310+00:00",
+    "0.0",
+    {
+     "device_class": "power",
+     "state_class": "measurement",
+     "unit_of_measurement": "kW"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.616200+00:00",
+    "0.0",
+    null,
+    "2026-10-30T15:33:15.417900+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.993124+00:00",
+    "0.0",
+    null,
+    "2026-10-30T17:54:57.851302+00:00"
+   ],
+   [
+    "2026-10-30T17:58:01.520351+00:00",
+    "1.55",
+    null,
+    "2026-10-30T18:00:01.197005+00:00"
+   ],
+   [
+    "2026-10-30T18:13:10.343536+00:00",
+    "2.89",
+    null,
+    "2026-10-30T18:18:11.364978+00:00"
+   ],
+   [
+    "2026-10-30T18:22:42.562876+00:00",
+    "3.02",
+    null,
+    "2026-10-30T18:31:24.570746+00:00"
+   ],
+   [
+    "2026-10-30T18:39:51.720564+00:00",
+    "0.0",
+    null,
+    "2026-10-31T10:34:47.367270+00:00"
+   ]
+  ],
+  "sensor.heat_pump_supply_temp": [
+   [
+    "2026-10-30T14:59:06.227574+00:00",
+    "33.0",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:02:45.767121+00:00"
+   ],
+   [
+    "2026-10-30T15:11:37.378624+00:00",
+    "30.0",
+    null,
+    "2026-10-30T15:16:24.832164+00:00"
+   ],
+   [
+    "2026-10-30T15:26:18.756304+00:00",
+    "27.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T15:44:15.302399+00:00",
+    "24.0",
+    null,
+    "2026-10-30T15:50:32.770512+00:00"
+   ],
+   [
+    "2026-10-30T15:57:28.417846+00:00",
+    "22.0",
+    null,
+    "2026-10-30T16:04:20.080292+00:00"
+   ],
+   [
+    "2026-10-30T16:04:37.176708+00:00",
+    "21.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:28:51.670233+00:00",
+    "18.0",
+    null,
+    "2026-10-30T16:38:01.037246+00:00"
+   ],
+   [
+    "2026-10-30T16:38:05.297078+00:00",
+    "17.0",
+    null,
+    "2026-10-30T16:49:01.057536+00:00"
+   ],
+   [
+    "2026-10-30T16:49:21.779761+00:00",
+    "16.0",
+    null,
+    "2026-10-30T17:00:24.155770+00:00"
+   ],
+   [
+    "2026-10-30T17:12:19.652357+00:00",
+    "14.0",
+    null,
+    "2026-10-30T17:25:45.541370+00:00"
+   ],
+   [
+    "2026-10-30T17:25:45.758436+00:00",
+    "13.0",
+    null,
+    "2026-10-30T17:40:01.153810+00:00"
+   ],
+   [
+    "2026-10-30T17:40:36.445215+00:00",
+    "12.0",
+    null,
+    "2026-10-30T17:54:42.593544+00:00"
+   ],
+   [
+    "2026-10-30T17:58:38.958373+00:00",
+    "36.0",
+    null,
+    "2026-10-30T18:00:42.103029+00:00"
+   ],
+   [
+    "2026-10-30T18:07:40.818279+00:00",
+    "39.0",
+    null,
+    "2026-10-30T18:16:37.274707+00:00"
+   ],
+   [
+    "2026-10-30T18:24:54.669355+00:00",
+    "41.0",
+    null,
+    "2026-10-30T18:31:11.149142+00:00"
+   ],
+   [
+    "2026-10-30T18:42:31.008394+00:00",
+    "36.0",
+    null,
+    "2026-10-30T18:45:53.315690+00:00"
+   ]
+  ],
+  "sensor.indoor_humidity": [
+   [
+    "2026-10-30T14:59:24.783566+00:00",
+    "52",
+    {
+     "device_class": "humidity",
+     "state_class": "measurement"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:33.675574+00:00",
+    "52",
+    null,
+    "2026-10-30T15:32:33.676178+00:00"
+   ],
+   [
+    "2026-10-30T16:20:06.203790+00:00",
+    "52",
+    null,
+    "2026-10-30T16:22:24.427523+00:00"
+   ],
+   [
+    "2026-10-30T17:08:24.778939+00:00",
+    "53",
+    null,
+    "2026-10-30T18:30:24.531315+00:00"
+   ],
+   [
+    "2026-10-30T18:39:24.703600+00:00",
+    "52",
+    null,
+    null
+   ]
+  ],
+  "sensor.indoor_temp": [
+   [
+    "2026-10-30T14:59:24.783656+00:00",
+    "22.6",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:34:24.437343+00:00",
+    "22.5",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T15:49:24.771271+00:00",
+    "22.4",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:22:24.427548+00:00",
+    "22.2",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:40:24.521489+00:00",
+    "22.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:52:24.922838+00:00",
+    "21.9",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T17:08:24.779053+00:00",
+    "21.8",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T17:25:24.827814+00:00",
+    "21.7",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T17:43:24.489583+00:00",
+    "21.5",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T17:50:24.458065+00:00",
+    "21.4",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T18:01:24.559523+00:00",
+    "21.3",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T18:16:24.886857+00:00",
+    "21.4",
+    null,
+    "2026-10-30T18:29:35.474628+00:00"
+   ],
+   [
+    "2026-10-30T18:34:24.503197+00:00",
+    "21.6",
+    null,
+    null
+   ]
+  ],
+  "sensor.lower_floor_temp": [
+   [
+    "2026-10-30T14:42:09.966027+00:00",
+    "20.4",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.656037+00:00",
+    "20.4",
+    null,
+    "2026-10-30T15:49:15.378027+00:00"
+   ],
+   [
+    "2026-10-30T15:59:28.655941+00:00",
+    "20.4",
+    null,
+    "2026-10-30T16:00:02.792859+00:00"
+   ],
+   [
+    "2026-10-30T16:07:05.405668+00:00",
+    "20.4",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:23:47.177264+00:00",
+    "19.4",
+    null,
+    "2026-10-30T16:34:31.032990+00:00"
+   ],
+   [
+    "2026-10-30T16:37:40.565006+00:00",
+    "19.4",
+    null,
+    "2026-10-30T18:20:39.792370+00:00"
+   ],
+   [
+    "2026-10-30T18:27:43.105889+00:00",
+    "19.4",
+    null,
+    "2026-10-30T19:37:31.359690+00:00"
+   ]
+  ],
+  "sensor.outdoor_temp": [
+   [
+    "2026-10-30T14:27:49.360907+00:00",
+    "8.0",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:02:24.814122+00:00"
+   ],
+   [
+    "2026-10-30T15:02:45.767894+00:00",
+    "7.0",
+    null,
+    "2026-10-30T15:28:43.331810+00:00"
+   ],
+   [
+    "2026-10-30T15:28:43.336288+00:00",
+    "6.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.612346+00:00",
+    "6.0",
+    null,
+    "2026-10-30T15:50:27.410173+00:00"
+   ],
+   [
+    "2026-10-30T15:50:29.475182+00:00",
+    "5.0",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:22:02.897025+00:00",
+    "4.0",
+    null,
+    "2026-10-30T17:02:31.085794+00:00"
+   ],
+   [
+    "2026-10-30T17:03:00.477137+00:00",
+    "3.0",
+    null,
+    "2026-10-30T17:53:01.174695+00:00"
+   ],
+   [
+    "2026-10-30T17:53:10.000569+00:00",
+    "2.0",
+    null,
+    "2026-10-30T18:18:11.363746+00:00"
+   ],
+   [
+    "2026-10-30T18:18:23.035610+00:00",
+    "1.0",
+    null,
+    "2026-10-30T18:34:50.400269+00:00"
+   ],
+   [
+    "2026-10-30T18:37:15.085874+00:00",
+    "1.0",
+    null,
+    "2026-10-30T19:24:01.333765+00:00"
+   ]
+  ],
+  "sensor.price": [
+   [
+    "2026-10-30T14:45:00.083057+00:00",
+    "2.9989",
+    {
+     "state_class": "measurement",
+     "unit_of_measurement": "SEK/kWh"
+    },
+    "2026-10-30T14:59:59.802519+00:00"
+   ],
+   [
+    "2026-10-30T15:00:00.082299+00:00",
+    "2.545",
+    null,
+    "2026-10-30T15:14:59.804588+00:00"
+   ],
+   [
+    "2026-10-30T15:15:00.082272+00:00",
+    "2.8795",
+    null,
+    "2026-10-30T15:24:21.863631+00:00"
+   ],
+   [
+    "2026-10-30T15:32:36.606108+00:00",
+    "2.8795",
+    null,
+    "2026-10-30T15:44:59.802252+00:00"
+   ],
+   [
+    "2026-10-30T15:45:00.425434+00:00",
+    "3.2824",
+    null,
+    "2026-10-30T15:59:59.802259+00:00"
+   ],
+   [
+    "2026-10-30T16:00:00.425496+00:00",
+    "3.1487",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:20:08.755702+00:00",
+    "3.1098",
+    null,
+    "2026-10-30T16:28:25.218649+00:00"
+   ],
+   [
+    "2026-10-30T16:30:00.217538+00:00",
+    "3.1627",
+    null,
+    "2026-10-30T16:44:59.987806+00:00"
+   ],
+   [
+    "2026-10-30T16:45:00.446828+00:00",
+    "3.1341",
+    null,
+    "2026-10-30T16:59:43.267414+00:00"
+   ],
+   [
+    "2026-10-30T17:12:46.177539+00:00",
+    "3.2196",
+    null,
+    "2026-10-30T17:13:55.001497+00:00"
+   ],
+   [
+    "2026-10-30T17:15:00.432601+00:00",
+    "3.2175",
+    null,
+    "2026-10-30T17:29:06.323254+00:00"
+   ],
+   [
+    "2026-10-30T17:30:00.111662+00:00",
+    "2.88",
+    null,
+    "2026-10-30T17:37:56.133515+00:00"
+   ],
+   [
+    "2026-10-30T17:45:00.308451+00:00",
+    "2.8082",
+    null,
+    "2026-10-30T17:52:17.146466+00:00"
+   ],
+   [
+    "2026-10-30T18:00:00.289475+00:00",
+    "2.1966",
+    null,
+    "2026-10-30T18:10:09.147262+00:00"
+   ],
+   [
+    "2026-10-30T18:15:00.286690+00:00",
+    "2.4784",
+    null,
+    "2026-10-30T18:29:59.987356+00:00"
+   ],
+   [
+    "2026-10-30T18:30:00.447685+00:00",
+    "2.474",
+    null,
+    "2026-10-30T18:36:37.307888+00:00"
+   ],
+   [
+    "2026-10-30T18:45:00.127918+00:00",
+    "2.2947",
+    null,
+    "2026-10-30T18:59:59.988097+00:00"
+   ],
+   [
+    "2026-10-30T19:00:00.448014+00:00",
+    "2.3886",
+    null,
+    "2026-10-30T19:14:59.987649+00:00"
+   ],
+   [
+    "2026-10-30T19:15:00.447316+00:00",
+    "2.3631",
+    null,
+    "2026-10-30T19:23:46.387432+00:00"
+   ],
+   [
+    "2026-10-30T19:30:00.049499+00:00",
+    "2.179",
+    null,
+    "2026-10-30T19:43:51.155344+00:00"
+   ],
+   [
+    "2026-10-30T19:45:00.280896+00:00",
+    "2.1396",
+    null,
+    "2026-10-30T19:59:59.987600+00:00"
+   ],
+   [
+    "2026-10-30T20:00:00.449545+00:00",
+    "2.0562",
+    null,
+    "2026-10-30T20:14:59.988485+00:00"
+   ],
+   [
+    "2026-10-30T20:15:00.447542+00:00",
+    "2.0311",
+    null,
+    "2026-10-30T20:29:59.992118+00:00"
+   ],
+   [
+    "2026-10-30T20:30:00.444566+00:00",
+    "2.0077",
+    null,
+    "2026-10-30T20:44:06.277016+00:00"
+   ],
+   [
+    "2026-10-30T20:45:00.158735+00:00",
+    "2.0117",
+    null,
+    "2026-10-30T20:59:50.225963+00:00"
+   ],
+   [
+    "2026-10-30T21:00:00.209251+00:00",
+    "2.3653",
+    null,
+    "2026-10-30T21:14:59.987608+00:00"
+   ],
+   [
+    "2026-10-30T21:15:00.447850+00:00",
+    "2.2088",
+    null,
+    "2026-10-30T21:26:38.214460+00:00"
+   ],
+   [
+    "2026-10-30T21:30:00.220984+00:00",
+    "2.4668",
+    null,
+    "2026-10-30T21:44:59.987715+00:00"
+   ],
+   [
+    "2026-10-30T21:45:00.447783+00:00",
+    "2.3696",
+    null,
+    "2026-10-30T21:55:49.221459+00:00"
+   ],
+   [
+    "2026-10-30T22:00:00.214491+00:00",
+    "2.4154",
+    null,
+    "2026-10-30T22:14:59.987780+00:00"
+   ],
+   [
+    "2026-10-30T22:15:00.446713+00:00",
+    "2.3846",
+    null,
+    "2026-10-30T22:22:23.272837+00:00"
+   ],
+   [
+    "2026-10-30T22:30:00.161238+00:00",
+    "2.3505",
+    null,
+    "2026-10-30T22:44:59.988300+00:00"
+   ]
+  ],
+  "sensor.valve_outlet_temp": [
+   [
+    "2026-10-30T14:59:04.598711+00:00",
+    "40.69",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T14:59:29.600392+00:00"
+   ],
+   [
+    "2026-10-30T15:14:09.588025+00:00",
+    "39.19",
+    null,
+    "2026-10-30T15:15:24.581579+00:00"
+   ],
+   [
+    "2026-10-30T15:28:49.576891+00:00",
+    "37.94",
+    null,
+    "2026-10-30T15:30:49.548975+00:00"
+   ],
+   [
+    "2026-10-30T15:43:39.564849+00:00",
+    "36.94",
+    null,
+    "2026-10-30T15:45:04.535237+00:00"
+   ],
+   [
+    "2026-10-30T15:57:54.584178+00:00",
+    "36.06",
+    null,
+    "2026-10-30T16:00:24.588571+00:00"
+   ],
+   [
+    "2026-10-30T16:05:04.544747+00:00",
+    "35.69",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:28:49.522543+00:00",
+    "34.56",
+    null,
+    "2026-10-30T16:31:19.543768+00:00"
+   ],
+   [
+    "2026-10-30T16:44:49.502709+00:00",
+    "33.81",
+    null,
+    "2026-10-30T16:48:19.086286+00:00"
+   ],
+   [
+    "2026-10-30T16:57:14.487469+00:00",
+    "33.31",
+    null,
+    "2026-10-30T16:59:19.490487+00:00"
+   ],
+   [
+    "2026-10-30T17:12:49.505796+00:00",
+    "32.69",
+    null,
+    "2026-10-30T17:15:39.254540+00:00"
+   ],
+   [
+    "2026-10-30T17:29:09.467629+00:00",
+    "32.06",
+    null,
+    "2026-10-30T17:33:03.254150+00:00"
+   ],
+   [
+    "2026-10-30T17:43:44.470120+00:00",
+    "31.56",
+    null,
+    "2026-10-30T17:46:59.470090+00:00"
+   ],
+   [
+    "2026-10-30T17:59:54.450946+00:00",
+    "33.31",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T18:14:09.439609+00:00",
+    "36.94",
+    null,
+    "2026-10-30T18:14:49.439049+00:00"
+   ],
+   [
+    "2026-10-30T18:28:34.427187+00:00",
+    "38.44",
+    null,
+    "2026-10-30T18:29:44.415600+00:00"
+   ],
+   [
+    "2026-10-30T18:44:44.424700+00:00",
+    "34.25",
+    null,
+    "2026-10-30T18:45:39.447591+00:00"
+   ]
+  ],
+  "sensor.wood_tank_bottom": [
+   [
+    "2026-10-30T14:57:54.628615+00:00",
+    "31.31",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:00:24.631949+00:00"
+   ],
+   [
+    "2026-10-30T15:14:44.617572+00:00",
+    "31.94",
+    null,
+    "2026-10-30T15:15:39.586812+00:00"
+   ],
+   [
+    "2026-10-30T15:29:29.627778+00:00",
+    "32.12",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T15:43:14.543276+00:00",
+    "31.75",
+    null,
+    "2026-10-30T15:47:24.559065+00:00"
+   ],
+   [
+    "2026-10-30T15:58:59.552103+00:00",
+    "31.38",
+    null,
+    "2026-10-30T16:01:19.549863+00:00"
+   ],
+   [
+    "2026-10-30T16:06:19.546253+00:00",
+    "31.25",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:29:54.537628+00:00",
+    "31.12",
+    null,
+    "2026-10-30T16:30:19.521313+00:00"
+   ],
+   [
+    "2026-10-30T16:38:14.489539+00:00",
+    "31.12",
+    null,
+    "2026-10-30T17:23:54.506745+00:00"
+   ],
+   [
+    "2026-10-30T17:24:49.473914+00:00",
+    "31.0",
+    null,
+    "2026-10-30T17:36:29.466809+00:00"
+   ],
+   [
+    "2026-10-30T17:37:09.466658+00:00",
+    "30.88",
+    null,
+    "2026-10-30T17:47:14.444671+00:00"
+   ],
+   [
+    "2026-10-30T17:53:14.433471+00:00",
+    "30.62",
+    null,
+    "2026-10-30T18:03:04.443546+00:00"
+   ],
+   [
+    "2026-10-30T18:08:49.442786+00:00",
+    "30.88",
+    null,
+    "2026-10-30T18:19:39.489573+00:00"
+   ],
+   [
+    "2026-10-30T18:20:19.447124+00:00",
+    "31.0",
+    null,
+    "2026-10-30T18:45:29.435977+00:00"
+   ]
+  ],
+  "sensor.wood_tank_top": [
+   [
+    "2026-10-30T14:58:34.574236+00:00",
+    "34.5",
+    {
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
+    },
+    "2026-10-30T15:00:19.600060+00:00"
+   ],
+   [
+    "2026-10-30T15:13:29.589054+00:00",
+    "33.75",
+    null,
+    "2026-10-30T15:16:04.564956+00:00"
+   ],
+   [
+    "2026-10-30T15:27:54.581925+00:00",
+    "33.12",
+    null,
+    "2026-10-30T15:30:29.158302+00:00"
+   ],
+   [
+    "2026-10-30T15:41:29.570987+00:00",
+    "32.62",
+    null,
+    "2026-10-30T15:44:09.585133+00:00"
+   ],
+   [
+    "2026-10-30T15:55:44.526137+00:00",
+    "32.25",
+    null,
+    "2026-10-30T16:01:59.549700+00:00"
+   ],
+   [
+    "2026-10-30T16:02:09.521940+00:00",
+    "32.12",
+    null,
+    null
+   ],
+   [
+    "2026-10-30T16:29:54.493464+00:00",
+    "31.5",
+    null,
+    "2026-10-30T16:40:09.630912+00:00"
+   ],
+   [
+    "2026-10-30T16:44:39.474585+00:00",
+    "31.5",
+    null,
+    "2026-10-30T16:49:29.555031+00:00"
+   ],
+   [
+    "2026-10-30T16:57:49.463250+00:00",
+    "31.38",
+    null,
+    "2026-10-30T17:47:49.459301+00:00"
+   ],
+   [
+    "2026-10-30T17:59:24.420841+00:00",
+    "31.38",
+    null,
+    "2026-10-30T18:03:49.445640+00:00"
+   ],
+   [
+    "2026-10-30T18:05:29.417557+00:00",
+    "31.38",
+    null,
+    "2026-10-30T18:22:44.431141+00:00"
+   ],
+   [
+    "2026-10-30T18:27:49.402215+00:00",
+    "31.62",
+    null,
+    "2026-10-30T18:30:59.427944+00:00"
+   ],
+   [
+    "2026-10-30T18:44:44.391339+00:00",
+    "32.25",
+    null,
+    "2026-10-30T18:45:19.475701+00:00"
+   ]
+  ],
+  "switch.dhw_disinfection_switch": [
+   [
+    "2026-10-30T01:53:10.300783+00:00",
+    "off",
+    {},
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.619469+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.419014+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.995515+00:00",
+    "off",
+    null,
+    "2026-10-31T11:56:33.202536+00:00"
+   ]
+  ],
+  "switch.heat_pump_backup_heater": [
+   [
+    "2026-10-30T10:03:41.955886+00:00",
+    "off",
+    {},
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.619891+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.419116+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.995714+00:00",
+    "off",
+    null,
+    "2026-10-30T18:31:01.246943+00:00"
+   ],
+   [
+    "2026-10-30T18:35:48.868446+00:00",
+    "off",
+    null,
+    "2026-10-31T20:55:00.973435+00:00"
+   ]
+  ],
+  "switch.heat_pump_capacity_limited": [
+   [
+    "2026-10-30T04:00:19.830794+00:00",
+    "off",
+    {},
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.620950+00:00",
+    "unknown",
+    null,
+    "2026-10-30T15:33:15.419367+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.996264+00:00",
+    "unknown",
+    null,
+    "2026-10-30T18:39:41.234215+00:00"
+   ],
+   [
+    "2026-10-30T18:39:41.242204+00:00",
+    "off",
+    null,
+    null
+   ]
+  ],
+  "switch.heat_pump_dhw_booster": [
+   [
+    "2026-10-30T05:49:54.610675+00:00",
+    "off",
+    {},
+    null
+   ],
+   [
+    "2026-10-30T15:32:22.620309+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.419217+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.995894+00:00",
+    "off",
+    null,
+    "2026-10-30T18:31:04.226745+00:00"
+   ],
+   [
+    "2026-10-30T18:35:50.037962+00:00",
+    "off",
+    null,
+    "2026-10-31T20:55:01.321927+00:00"
+   ]
+  ],
+  "switch.heat_pump_switch": [
+   [
+    "2026-10-30T14:33:49.116710+00:00",
+    "off",
+    {},
+    "2026-10-30T14:33:49.118075+00:00"
+   ],
+   [
+    "2026-10-30T15:32:22.619096+00:00",
+    "off",
+    null,
+    "2026-10-30T15:33:15.419951+00:00"
+   ],
+   [
+    "2026-10-30T16:20:00.995248+00:00",
+    "off",
+    null,
+    "2026-10-30T17:53:31.181278+00:00"
+   ],
+   [
+    "2026-10-30T17:53:50.898389+00:00",
+    "on",
+    null,
+    "2026-10-30T18:39:31.259810+00:00"
+   ],
+   [
+    "2026-10-30T18:39:41.233735+00:00",
+    "off",
+    null,
+    "2026-10-31T10:33:03.072030+00:00"
+   ]
+  ],
+  "weather.weather": [
+   [
+    "2026-10-30T14:53:13.413253+00:00",
+    "sunny",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 10.4,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 8.3,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T15:32:21.728742+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 8.8,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 4.3,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T16:20:00.808972+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 6.9,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 4.0,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T17:15:00.619895+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 5.3,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 4.3,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T18:10:00.608557+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 4.2,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 5.8,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T19:05:00.594152+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 2.7,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 4.7,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T20:00:00.637810+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 1.8,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 3.6,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T20:55:00.579537+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 1.7,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 3.6,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ],
+   [
+    "2026-10-30T21:50:00.622922+00:00",
+    "clear-night",
+    {
+     "precipitation_unit": "mm",
+     "temperature": 1.1,
+     "temperature_unit": "\u00b0C",
+     "wind_speed": 3.6,
+     "wind_speed_unit": "km/h"
+    },
+    null
+   ]
+  ]
+ },
+ "time_zone": "Europe/Stockholm",
+ "window": {
+  "end": "2026-10-30T20:00:00+01:00",
+  "start": "2026-10-30T16:00:00+01:00"
+ }
+}
diff --git a/tests/replay/synthetic-dhw-only.json b/tests/replay/synthetic-dhw-only.json
index ba5c58648..76f743081 100644
--- a/tests/replay/synthetic-dhw-only.json
+++ b/tests/replay/synthetic-dhw-only.json
@@ -2,18 +2,18 @@
  "entry": {
   "data": {
    "dhw_tank_volume": 180.0,
-   "dhw_temp_entity": "sensor.hot_water_tank_temperature",
-   "heat_pump_mode_entity": "select.heat_pump_operating_mode",
+   "dhw_temp_entity": "sensor.dhw_temp",
+   "heat_pump_mode_entity": "select.heat_pump_mode",
    "heat_pump_power_entity": "sensor.heat_pump_power",
-   "indoor_temp_entity": "sensor.living_room_temperature",
-   "outdoor_temp_entity": "sensor.outdoor_temperature",
-   "price_entity": "sensor.nordpool_kwh_se3_sek",
+   "indoor_temp_entity": "sensor.indoor_temp",
+   "outdoor_temp_entity": "sensor.outdoor_temp",
+   "price_entity": "sensor.price",
    "price_source": "entity",
    "solar_location": {
     "latitude": 59.33,
     "longitude": 18.06
    },
-   "weather_entity": "weather.forecast_home"
+   "weather_entity": "weather.weather"
   },
   "minor_version": 1,
   "options": {
@@ -23,22 +23,22 @@
  },
  "format": "hpo-replay/1",
  "inputs": [
-  "select.heat_pump_operating_mode",
+  "select.heat_pump_mode",
   "sensor.heat_pump_power",
-  "sensor.hot_water_tank_temperature",
-  "sensor.living_room_temperature",
-  "sensor.nordpool_kwh_se3_sek",
-  "sensor.outdoor_temperature",
-  "weather.forecast_home"
+  "sensor.dhw_temp",
+  "sensor.indoor_temp",
+  "sensor.price",
+  "sensor.outdoor_temp",
+  "weather.weather"
  ],
  "price_series_entity": null,
  "published": [
-  "climate.heat_pump_optimizer",
-  "sensor.heat_pump_optimizer_heat_pump_action"
+  "climate.e_ac61a3e761",
+  "sensor.e_2cdc621bcb"
  ],
  "recorder_schema": 48,
  "states": {
-  "climate.heat_pump_optimizer": [
+  "climate.e_ac61a3e761": [
    [
     "2026-01-14T22:30:00+00:00",
     "auto",
@@ -337,7 +337,7 @@
     "2026-01-15T22:59:00+00:00"
    ]
   ],
-  "select.heat_pump_operating_mode": [
+  "select.heat_pump_mode": [
    [
     "2026-01-14T22:00:00+00:00",
     "Hot water",
@@ -351,3789 +351,3789 @@
     "2026-01-15T23:59:00+00:00"
    ]
   ],
-  "sensor.heat_pump_optimizer_heat_pump_action": [
+  "sensor.dhw_temp": [
    [
-    "2026-01-14T22:30:00+00:00",
-    "off",
+    "2026-01-14T22:55:00+00:00",
+    "48.1",
     {
-     "heat_pump_on": false
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
     },
     "2026-01-14T22:59:00+00:00"
    ],
    [
     "2026-01-14T23:00:00+00:00",
-    "off",
+    "48.0",
     null,
-    "2026-01-14T23:29:00+00:00"
+    "2026-01-14T23:04:00+00:00"
    ],
    [
-    "2026-01-14T23:30:00+00:00",
-    "off",
+    "2026-01-14T23:05:00+00:00",
+    "48.0",
     null,
-    "2026-01-14T23:59:00+00:00"
+    "2026-01-14T23:09:00+00:00"
    ],
    [
-    "2026-01-15T00:00:00+00:00",
-    "off",
+    "2026-01-14T23:10:00+00:00",
+    "48.0",
     null,
-    "2026-01-15T00:29:00+00:00"
+    "2026-01-14T23:14:00+00:00"
    ],
    [
-    "2026-01-15T00:30:00+00:00",
-    "off",
+    "2026-01-14T23:15:00+00:00",
+    "48.0",
     null,
-    "2026-01-15T00:59:00+00:00"
+    "2026-01-14T23:19:00+00:00"
    ],
    [
-    "2026-01-15T01:00:00+00:00",
-    "off",
-    {
-     "heat_pump_on": true
-    },
-    "2026-01-15T01:29:00+00:00"
+    "2026-01-14T23:20:00+00:00",
+    "48.0",
+    null,
+    "2026-01-14T23:24:00+00:00"
    ],
    [
-    "2026-01-15T01:30:00+00:00",
-    "off",
+    "2026-01-14T23:25:00+00:00",
+    "47.9",
     null,
-    "2026-01-15T01:59:00+00:00"
+    "2026-01-14T23:29:00+00:00"
    ],
    [
-    "2026-01-15T02:00:00+00:00",
-    "off",
+    "2026-01-14T23:30:00+00:00",
+    "47.9",
     null,
-    "2026-01-15T02:29:00+00:00"
+    "2026-01-14T23:34:00+00:00"
    ],
    [
-    "2026-01-15T02:30:00+00:00",
-    "off",
+    "2026-01-14T23:35:00+00:00",
+    "47.9",
     null,
-    "2026-01-15T02:59:00+00:00"
+    "2026-01-14T23:39:00+00:00"
    ],
    [
-    "2026-01-15T03:00:00+00:00",
-    "off",
+    "2026-01-14T23:40:00+00:00",
+    "47.9",
     null,
-    "2026-01-15T03:29:00+00:00"
+    "2026-01-14T23:44:00+00:00"
    ],
    [
-    "2026-01-15T03:30:00+00:00",
-    "off",
+    "2026-01-14T23:45:00+00:00",
+    "47.9",
     null,
-    "2026-01-15T03:59:00+00:00"
+    "2026-01-14T23:49:00+00:00"
    ],
    [
-    "2026-01-15T04:00:00+00:00",
-    "off",
+    "2026-01-14T23:50:00+00:00",
+    "47.8",
     null,
-    "2026-01-15T04:29:00+00:00"
+    "2026-01-14T23:54:00+00:00"
    ],
    [
-    "2026-01-15T04:30:00+00:00",
-    "off",
+    "2026-01-14T23:55:00+00:00",
+    "47.8",
     null,
-    "2026-01-15T04:59:00+00:00"
+    "2026-01-14T23:59:00+00:00"
    ],
    [
-    "2026-01-15T05:00:00+00:00",
-    "off",
-    {
-     "heat_pump_on": false
-    },
-    "2026-01-15T05:29:00+00:00"
+    "2026-01-15T00:00:00+00:00",
+    "47.8",
+    null,
+    "2026-01-15T00:04:00+00:00"
    ],
    [
-    "2026-01-15T05:30:00+00:00",
-    "off",
+    "2026-01-15T00:05:00+00:00",
+    "47.8",
     null,
-    "2026-01-15T05:59:00+00:00"
+    "2026-01-15T00:09:00+00:00"
    ],
    [
-    "2026-01-15T06:00:00+00:00",
-    "off",
+    "2026-01-15T00:10:00+00:00",
+    "47.8",
     null,
-    "2026-01-15T06:29:00+00:00"
+    "2026-01-15T00:14:00+00:00"
    ],
    [
-    "2026-01-15T06:30:00+00:00",
-    "off",
+    "2026-01-15T00:15:00+00:00",
+    "47.7",
     null,
-    "2026-01-15T06:59:00+00:00"
+    "2026-01-15T00:19:00+00:00"
    ],
    [
-    "2026-01-15T07:00:00+00:00",
-    "off",
+    "2026-01-15T00:20:00+00:00",
+    "47.7",
     null,
-    "2026-01-15T07:29:00+00:00"
+    "2026-01-15T00:24:00+00:00"
    ],
    [
-    "2026-01-15T07:30:00+00:00",
-    "off",
+    "2026-01-15T00:25:00+00:00",
+    "47.7",
     null,
-    "2026-01-15T07:59:00+00:00"
+    "2026-01-15T00:29:00+00:00"
    ],
    [
-    "2026-01-15T08:00:00+00:00",
-    "off",
+    "2026-01-15T00:30:00+00:00",
+    "47.7",
     null,
-    "2026-01-15T08:29:00+00:00"
+    "2026-01-15T00:34:00+00:00"
    ],
    [
-    "2026-01-15T08:30:00+00:00",
-    "off",
+    "2026-01-15T00:35:00+00:00",
+    "47.7",
     null,
-    "2026-01-15T08:59:00+00:00"
+    "2026-01-15T00:39:00+00:00"
    ],
    [
-    "2026-01-15T09:00:00+00:00",
-    "off",
+    "2026-01-15T00:40:00+00:00",
+    "47.6",
     null,
-    "2026-01-15T09:29:00+00:00"
+    "2026-01-15T00:44:00+00:00"
    ],
    [
-    "2026-01-15T09:30:00+00:00",
-    "off",
+    "2026-01-15T00:45:00+00:00",
+    "47.6",
     null,
-    "2026-01-15T09:59:00+00:00"
+    "2026-01-15T00:49:00+00:00"
    ],
    [
-    "2026-01-15T10:00:00+00:00",
-    "off",
+    "2026-01-15T00:50:00+00:00",
+    "47.6",
     null,
-    "2026-01-15T10:29:00+00:00"
+    "2026-01-15T00:54:00+00:00"
    ],
    [
-    "2026-01-15T10:30:00+00:00",
-    "off",
+    "2026-01-15T00:55:00+00:00",
+    "47.6",
     null,
-    "2026-01-15T10:59:00+00:00"
+    "2026-01-15T00:59:00+00:00"
    ],
    [
-    "2026-01-15T11:00:00+00:00",
-    "off",
+    "2026-01-15T01:00:00+00:00",
+    "47.6",
     null,
-    "2026-01-15T11:29:00+00:00"
+    "2026-01-15T01:04:00+00:00"
    ],
    [
-    "2026-01-15T11:30:00+00:00",
-    "off",
+    "2026-01-15T01:05:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T11:59:00+00:00"
+    "2026-01-15T01:09:00+00:00"
    ],
    [
-    "2026-01-15T12:00:00+00:00",
-    "off",
+    "2026-01-15T01:10:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T12:29:00+00:00"
+    "2026-01-15T01:14:00+00:00"
    ],
    [
-    "2026-01-15T12:30:00+00:00",
-    "off",
+    "2026-01-15T01:15:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T12:59:00+00:00"
+    "2026-01-15T01:19:00+00:00"
    ],
    [
-    "2026-01-15T13:00:00+00:00",
-    "off",
+    "2026-01-15T01:20:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T13:29:00+00:00"
+    "2026-01-15T01:24:00+00:00"
    ],
    [
-    "2026-01-15T13:30:00+00:00",
-    "off",
+    "2026-01-15T01:25:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T13:59:00+00:00"
+    "2026-01-15T01:29:00+00:00"
    ],
    [
-    "2026-01-15T14:00:00+00:00",
-    "off",
+    "2026-01-15T01:30:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T14:29:00+00:00"
+    "2026-01-15T01:34:00+00:00"
    ],
    [
-    "2026-01-15T14:30:00+00:00",
-    "off",
+    "2026-01-15T01:35:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T14:59:00+00:00"
+    "2026-01-15T01:39:00+00:00"
    ],
    [
-    "2026-01-15T15:00:00+00:00",
-    "off",
+    "2026-01-15T01:40:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T15:29:00+00:00"
+    "2026-01-15T01:44:00+00:00"
    ],
    [
-    "2026-01-15T15:30:00+00:00",
-    "off",
+    "2026-01-15T01:45:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T15:59:00+00:00"
+    "2026-01-15T01:49:00+00:00"
    ],
    [
-    "2026-01-15T16:00:00+00:00",
-    "off",
+    "2026-01-15T01:50:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T16:29:00+00:00"
+    "2026-01-15T01:54:00+00:00"
    ],
    [
-    "2026-01-15T16:30:00+00:00",
-    "off",
+    "2026-01-15T01:55:00+00:00",
+    "47.3",
     null,
-    "2026-01-15T16:59:00+00:00"
+    "2026-01-15T01:59:00+00:00"
    ],
    [
-    "2026-01-15T17:00:00+00:00",
-    "off",
+    "2026-01-15T02:00:00+00:00",
+    "47.3",
     null,
-    "2026-01-15T17:29:00+00:00"
+    "2026-01-15T02:04:00+00:00"
    ],
    [
-    "2026-01-15T17:30:00+00:00",
-    "off",
+    "2026-01-15T02:05:00+00:00",
+    "47.3",
     null,
-    "2026-01-15T17:59:00+00:00"
+    "2026-01-15T02:09:00+00:00"
    ],
    [
-    "2026-01-15T18:00:00+00:00",
-    "off",
+    "2026-01-15T02:10:00+00:00",
+    "47.3",
     null,
-    "2026-01-15T18:29:00+00:00"
+    "2026-01-15T02:14:00+00:00"
    ],
    [
-    "2026-01-15T18:30:00+00:00",
-    "off",
+    "2026-01-15T02:15:00+00:00",
+    "47.3",
     null,
-    "2026-01-15T18:59:00+00:00"
+    "2026-01-15T02:19:00+00:00"
    ],
    [
-    "2026-01-15T19:00:00+00:00",
-    "off",
+    "2026-01-15T02:20:00+00:00",
+    "47.2",
     null,
-    "2026-01-15T19:29:00+00:00"
+    "2026-01-15T02:24:00+00:00"
    ],
    [
-    "2026-01-15T19:30:00+00:00",
-    "off",
+    "2026-01-15T02:25:00+00:00",
+    "47.2",
     null,
-    "2026-01-15T19:59:00+00:00"
+    "2026-01-15T02:29:00+00:00"
    ],
    [
-    "2026-01-15T20:00:00+00:00",
-    "off",
+    "2026-01-15T02:30:00+00:00",
+    "47.2",
     null,
-    "2026-01-15T20:29:00+00:00"
+    "2026-01-15T02:34:00+00:00"
    ],
    [
-    "2026-01-15T20:30:00+00:00",
-    "off",
+    "2026-01-15T02:35:00+00:00",
+    "47.2",
     null,
-    "2026-01-15T20:59:00+00:00"
+    "2026-01-15T02:39:00+00:00"
    ],
    [
-    "2026-01-15T21:00:00+00:00",
-    "off",
+    "2026-01-15T02:40:00+00:00",
+    "47.2",
     null,
-    "2026-01-15T21:29:00+00:00"
+    "2026-01-15T02:44:00+00:00"
    ],
    [
-    "2026-01-15T21:30:00+00:00",
-    "off",
+    "2026-01-15T02:45:00+00:00",
+    "47.1",
     null,
-    "2026-01-15T21:59:00+00:00"
+    "2026-01-15T02:49:00+00:00"
    ],
    [
-    "2026-01-15T22:00:00+00:00",
-    "off",
+    "2026-01-15T02:50:00+00:00",
+    "47.1",
     null,
-    "2026-01-15T22:29:00+00:00"
+    "2026-01-15T02:54:00+00:00"
    ],
    [
-    "2026-01-15T22:30:00+00:00",
-    "off",
+    "2026-01-15T02:55:00+00:00",
+    "47.1",
     null,
-    "2026-01-15T22:59:00+00:00"
-   ]
-  ],
-  "sensor.heat_pump_power": [
-   [
-    "2026-01-14T22:55:00+00:00",
-    "0.0",
-    {
-     "device_class": "power",
-     "state_class": "measurement",
-     "unit_of_measurement": "kW"
-    },
-    "2026-01-14T22:59:00+00:00"
+    "2026-01-15T02:59:00+00:00"
    ],
    [
-    "2026-01-14T23:00:00+00:00",
-    "0.0",
+    "2026-01-15T03:00:00+00:00",
+    "47.6",
     null,
-    "2026-01-14T23:04:00+00:00"
+    "2026-01-15T03:04:00+00:00"
    ],
    [
-    "2026-01-14T23:05:00+00:00",
-    "0.0",
+    "2026-01-15T03:05:00+00:00",
+    "48.2",
     null,
-    "2026-01-14T23:09:00+00:00"
+    "2026-01-15T03:09:00+00:00"
    ],
    [
-    "2026-01-14T23:10:00+00:00",
-    "0.0",
+    "2026-01-15T03:10:00+00:00",
+    "48.7",
     null,
-    "2026-01-14T23:14:00+00:00"
+    "2026-01-15T03:14:00+00:00"
    ],
    [
-    "2026-01-14T23:15:00+00:00",
-    "0.0",
+    "2026-01-15T03:15:00+00:00",
+    "49.3",
     null,
-    "2026-01-14T23:19:00+00:00"
+    "2026-01-15T03:19:00+00:00"
    ],
    [
-    "2026-01-14T23:20:00+00:00",
-    "0.0",
+    "2026-01-15T03:20:00+00:00",
+    "49.8",
     null,
-    "2026-01-14T23:24:00+00:00"
+    "2026-01-15T03:24:00+00:00"
    ],
    [
-    "2026-01-14T23:25:00+00:00",
-    "0.0",
+    "2026-01-15T03:25:00+00:00",
+    "50.4",
     null,
-    "2026-01-14T23:29:00+00:00"
+    "2026-01-15T03:29:00+00:00"
    ],
    [
-    "2026-01-14T23:30:00+00:00",
-    "0.0",
+    "2026-01-15T03:30:00+00:00",
+    "50.9",
     null,
-    "2026-01-14T23:34:00+00:00"
+    "2026-01-15T03:34:00+00:00"
    ],
    [
-    "2026-01-14T23:35:00+00:00",
-    "0.0",
+    "2026-01-15T03:35:00+00:00",
+    "51.5",
     null,
-    "2026-01-14T23:39:00+00:00"
+    "2026-01-15T03:39:00+00:00"
    ],
    [
-    "2026-01-14T23:40:00+00:00",
-    "0.0",
+    "2026-01-15T03:40:00+00:00",
+    "52.0",
     null,
-    "2026-01-14T23:44:00+00:00"
+    "2026-01-15T03:44:00+00:00"
    ],
    [
-    "2026-01-14T23:45:00+00:00",
-    "0.0",
+    "2026-01-15T03:45:00+00:00",
+    "52.6",
     null,
-    "2026-01-14T23:49:00+00:00"
+    "2026-01-15T03:49:00+00:00"
    ],
    [
-    "2026-01-14T23:50:00+00:00",
-    "0.0",
+    "2026-01-15T03:50:00+00:00",
+    "53.1",
     null,
-    "2026-01-14T23:54:00+00:00"
+    "2026-01-15T03:54:00+00:00"
    ],
    [
-    "2026-01-14T23:55:00+00:00",
-    "0.0",
+    "2026-01-15T03:55:00+00:00",
+    "53.7",
     null,
-    "2026-01-14T23:59:00+00:00"
+    "2026-01-15T03:59:00+00:00"
    ],
    [
-    "2026-01-15T00:00:00+00:00",
-    "0.0",
+    "2026-01-15T04:00:00+00:00",
+    "54.2",
     null,
-    "2026-01-15T00:04:00+00:00"
+    "2026-01-15T04:04:00+00:00"
    ],
    [
-    "2026-01-15T00:05:00+00:00",
-    "0.0",
+    "2026-01-15T04:05:00+00:00",
+    "54.8",
     null,
-    "2026-01-15T00:09:00+00:00"
+    "2026-01-15T04:09:00+00:00"
    ],
    [
-    "2026-01-15T00:10:00+00:00",
-    "0.0",
+    "2026-01-15T04:10:00+00:00",
+    "55.3",
     null,
-    "2026-01-15T00:14:00+00:00"
+    "2026-01-15T04:14:00+00:00"
    ],
    [
-    "2026-01-15T00:15:00+00:00",
-    "0.0",
+    "2026-01-15T04:15:00+00:00",
+    "55.9",
     null,
-    "2026-01-15T00:19:00+00:00"
+    "2026-01-15T04:19:00+00:00"
    ],
    [
-    "2026-01-15T00:20:00+00:00",
-    "0.0",
+    "2026-01-15T04:20:00+00:00",
+    "56.4",
     null,
-    "2026-01-15T00:24:00+00:00"
+    "2026-01-15T04:24:00+00:00"
    ],
    [
-    "2026-01-15T00:25:00+00:00",
-    "0.0",
+    "2026-01-15T04:25:00+00:00",
+    "57.0",
     null,
-    "2026-01-15T00:29:00+00:00"
+    "2026-01-15T04:29:00+00:00"
    ],
    [
-    "2026-01-15T00:30:00+00:00",
-    "0.0",
+    "2026-01-15T04:30:00+00:00",
+    "57.0",
     null,
-    "2026-01-15T00:34:00+00:00"
+    "2026-01-15T04:34:00+00:00"
    ],
    [
-    "2026-01-15T00:35:00+00:00",
-    "0.0",
+    "2026-01-15T04:35:00+00:00",
+    "57.0",
     null,
-    "2026-01-15T00:39:00+00:00"
+    "2026-01-15T04:39:00+00:00"
    ],
    [
-    "2026-01-15T00:40:00+00:00",
-    "0.0",
+    "2026-01-15T04:40:00+00:00",
+    "56.9",
     null,
-    "2026-01-15T00:44:00+00:00"
+    "2026-01-15T04:44:00+00:00"
    ],
    [
-    "2026-01-15T00:45:00+00:00",
-    "0.0",
+    "2026-01-15T04:45:00+00:00",
+    "56.9",
     null,
-    "2026-01-15T00:49:00+00:00"
+    "2026-01-15T04:49:00+00:00"
    ],
    [
-    "2026-01-15T00:50:00+00:00",
-    "0.0",
+    "2026-01-15T04:50:00+00:00",
+    "56.9",
     null,
-    "2026-01-15T00:54:00+00:00"
+    "2026-01-15T04:54:00+00:00"
    ],
    [
-    "2026-01-15T00:55:00+00:00",
-    "0.0",
+    "2026-01-15T04:55:00+00:00",
+    "56.9",
     null,
-    "2026-01-15T00:59:00+00:00"
+    "2026-01-15T04:59:00+00:00"
    ],
    [
-    "2026-01-15T01:00:00+00:00",
-    "0.0",
+    "2026-01-15T05:00:00+00:00",
+    "56.9",
     null,
-    "2026-01-15T01:04:00+00:00"
+    "2026-01-15T05:04:00+00:00"
    ],
    [
-    "2026-01-15T01:05:00+00:00",
-    "0.0",
+    "2026-01-15T05:05:00+00:00",
+    "56.8",
     null,
-    "2026-01-15T01:09:00+00:00"
+    "2026-01-15T05:09:00+00:00"
    ],
    [
-    "2026-01-15T01:10:00+00:00",
-    "0.0",
+    "2026-01-15T05:10:00+00:00",
+    "56.8",
     null,
-    "2026-01-15T01:14:00+00:00"
+    "2026-01-15T05:14:00+00:00"
    ],
    [
-    "2026-01-15T01:15:00+00:00",
-    "0.0",
+    "2026-01-15T05:15:00+00:00",
+    "56.8",
     null,
-    "2026-01-15T01:19:00+00:00"
+    "2026-01-15T05:19:00+00:00"
    ],
    [
-    "2026-01-15T01:20:00+00:00",
-    "0.0",
+    "2026-01-15T05:20:00+00:00",
+    "56.8",
     null,
-    "2026-01-15T01:24:00+00:00"
+    "2026-01-15T05:24:00+00:00"
    ],
    [
-    "2026-01-15T01:25:00+00:00",
-    "0.0",
+    "2026-01-15T05:25:00+00:00",
+    "56.8",
     null,
-    "2026-01-15T01:29:00+00:00"
+    "2026-01-15T05:29:00+00:00"
    ],
    [
-    "2026-01-15T01:30:00+00:00",
-    "0.0",
+    "2026-01-15T05:30:00+00:00",
+    "55.6",
     null,
-    "2026-01-15T01:34:00+00:00"
+    "2026-01-15T05:34:00+00:00"
    ],
    [
-    "2026-01-15T01:35:00+00:00",
-    "0.0",
+    "2026-01-15T05:35:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T01:39:00+00:00"
+    "2026-01-15T05:39:00+00:00"
    ],
    [
-    "2026-01-15T01:40:00+00:00",
-    "0.0",
+    "2026-01-15T05:40:00+00:00",
+    "53.4",
     null,
-    "2026-01-15T01:44:00+00:00"
+    "2026-01-15T05:44:00+00:00"
    ],
    [
-    "2026-01-15T01:45:00+00:00",
-    "0.0",
+    "2026-01-15T05:45:00+00:00",
+    "52.3",
     null,
-    "2026-01-15T01:49:00+00:00"
+    "2026-01-15T05:49:00+00:00"
    ],
    [
-    "2026-01-15T01:50:00+00:00",
-    "0.0",
+    "2026-01-15T05:50:00+00:00",
+    "51.2",
     null,
-    "2026-01-15T01:54:00+00:00"
+    "2026-01-15T05:54:00+00:00"
    ],
    [
-    "2026-01-15T01:55:00+00:00",
-    "0.0",
+    "2026-01-15T05:55:00+00:00",
+    "50.0",
     null,
-    "2026-01-15T01:59:00+00:00"
+    "2026-01-15T05:59:00+00:00"
    ],
    [
-    "2026-01-15T02:00:00+00:00",
-    "0.0",
+    "2026-01-15T06:00:00+00:00",
+    "48.9",
     null,
-    "2026-01-15T02:04:00+00:00"
+    "2026-01-15T06:04:00+00:00"
    ],
    [
-    "2026-01-15T02:05:00+00:00",
-    "0.0",
+    "2026-01-15T06:05:00+00:00",
+    "47.8",
     null,
-    "2026-01-15T02:09:00+00:00"
+    "2026-01-15T06:09:00+00:00"
    ],
    [
-    "2026-01-15T02:10:00+00:00",
-    "0.0",
+    "2026-01-15T06:10:00+00:00",
+    "46.7",
     null,
-    "2026-01-15T02:14:00+00:00"
+    "2026-01-15T06:14:00+00:00"
    ],
    [
-    "2026-01-15T02:15:00+00:00",
-    "0.0",
+    "2026-01-15T06:15:00+00:00",
+    "46.7",
     null,
-    "2026-01-15T02:19:00+00:00"
+    "2026-01-15T06:19:00+00:00"
    ],
    [
-    "2026-01-15T02:20:00+00:00",
-    "0.0",
+    "2026-01-15T06:20:00+00:00",
+    "46.6",
     null,
-    "2026-01-15T02:24:00+00:00"
+    "2026-01-15T06:24:00+00:00"
    ],
    [
-    "2026-01-15T02:25:00+00:00",
-    "0.0",
+    "2026-01-15T06:25:00+00:00",
+    "46.6",
     null,
-    "2026-01-15T02:29:00+00:00"
+    "2026-01-15T06:29:00+00:00"
    ],
    [
-    "2026-01-15T02:30:00+00:00",
-    "0.0",
+    "2026-01-15T06:30:00+00:00",
+    "46.6",
     null,
-    "2026-01-15T02:34:00+00:00"
+    "2026-01-15T06:34:00+00:00"
    ],
    [
-    "2026-01-15T02:35:00+00:00",
-    "0.0",
+    "2026-01-15T06:35:00+00:00",
+    "46.6",
     null,
-    "2026-01-15T02:39:00+00:00"
+    "2026-01-15T06:39:00+00:00"
    ],
    [
-    "2026-01-15T02:40:00+00:00",
-    "0.0",
+    "2026-01-15T06:40:00+00:00",
+    "46.6",
     null,
-    "2026-01-15T02:44:00+00:00"
+    "2026-01-15T06:44:00+00:00"
    ],
    [
-    "2026-01-15T02:45:00+00:00",
-    "0.0",
+    "2026-01-15T06:45:00+00:00",
+    "46.5",
     null,
-    "2026-01-15T02:49:00+00:00"
+    "2026-01-15T06:49:00+00:00"
    ],
    [
-    "2026-01-15T02:50:00+00:00",
-    "0.0",
+    "2026-01-15T06:50:00+00:00",
+    "46.5",
     null,
-    "2026-01-15T02:54:00+00:00"
+    "2026-01-15T06:54:00+00:00"
    ],
    [
-    "2026-01-15T02:55:00+00:00",
-    "0.0",
+    "2026-01-15T06:55:00+00:00",
+    "46.5",
     null,
-    "2026-01-15T02:59:00+00:00"
+    "2026-01-15T06:59:00+00:00"
    ],
    [
-    "2026-01-15T03:00:00+00:00",
-    "1.83",
+    "2026-01-15T07:00:00+00:00",
+    "46.5",
     null,
-    "2026-01-15T03:04:00+00:00"
+    "2026-01-15T07:04:00+00:00"
    ],
    [
-    "2026-01-15T03:05:00+00:00",
-    "1.83",
+    "2026-01-15T07:05:00+00:00",
+    "46.5",
     null,
-    "2026-01-15T03:09:00+00:00"
+    "2026-01-15T07:09:00+00:00"
    ],
    [
-    "2026-01-15T03:10:00+00:00",
-    "1.83",
+    "2026-01-15T07:10:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T03:14:00+00:00"
+    "2026-01-15T07:14:00+00:00"
    ],
    [
-    "2026-01-15T03:15:00+00:00",
-    "1.83",
+    "2026-01-15T07:15:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T03:19:00+00:00"
+    "2026-01-15T07:19:00+00:00"
    ],
    [
-    "2026-01-15T03:20:00+00:00",
-    "1.83",
+    "2026-01-15T07:20:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T03:24:00+00:00"
+    "2026-01-15T07:24:00+00:00"
    ],
    [
-    "2026-01-15T03:25:00+00:00",
-    "1.83",
+    "2026-01-15T07:25:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T03:29:00+00:00"
+    "2026-01-15T07:29:00+00:00"
    ],
    [
-    "2026-01-15T03:30:00+00:00",
-    "1.83",
+    "2026-01-15T07:30:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T03:34:00+00:00"
+    "2026-01-15T07:34:00+00:00"
    ],
    [
-    "2026-01-15T03:35:00+00:00",
-    "1.83",
+    "2026-01-15T07:35:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T03:39:00+00:00"
+    "2026-01-15T07:39:00+00:00"
    ],
    [
-    "2026-01-15T03:40:00+00:00",
-    "1.83",
+    "2026-01-15T07:40:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T03:44:00+00:00"
+    "2026-01-15T07:44:00+00:00"
    ],
    [
-    "2026-01-15T03:45:00+00:00",
-    "1.83",
+    "2026-01-15T07:45:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T03:49:00+00:00"
+    "2026-01-15T07:49:00+00:00"
    ],
    [
-    "2026-01-15T03:50:00+00:00",
-    "1.83",
+    "2026-01-15T07:50:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T03:54:00+00:00"
+    "2026-01-15T07:54:00+00:00"
    ],
    [
-    "2026-01-15T03:55:00+00:00",
-    "1.83",
+    "2026-01-15T07:55:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T03:59:00+00:00"
+    "2026-01-15T07:59:00+00:00"
    ],
    [
-    "2026-01-15T04:00:00+00:00",
-    "1.83",
+    "2026-01-15T08:00:00+00:00",
+    "46.2",
     null,
-    "2026-01-15T04:04:00+00:00"
+    "2026-01-15T08:04:00+00:00"
    ],
    [
-    "2026-01-15T04:05:00+00:00",
-    "1.83",
+    "2026-01-15T08:05:00+00:00",
+    "46.2",
     null,
-    "2026-01-15T04:09:00+00:00"
+    "2026-01-15T08:09:00+00:00"
    ],
    [
-    "2026-01-15T04:10:00+00:00",
-    "1.83",
+    "2026-01-15T08:10:00+00:00",
+    "46.2",
     null,
-    "2026-01-15T04:14:00+00:00"
+    "2026-01-15T08:14:00+00:00"
    ],
    [
-    "2026-01-15T04:15:00+00:00",
-    "1.83",
+    "2026-01-15T08:15:00+00:00",
+    "46.2",
     null,
-    "2026-01-15T04:19:00+00:00"
+    "2026-01-15T08:19:00+00:00"
    ],
    [
-    "2026-01-15T04:20:00+00:00",
-    "1.83",
+    "2026-01-15T08:20:00+00:00",
+    "46.2",
     null,
-    "2026-01-15T04:24:00+00:00"
+    "2026-01-15T08:24:00+00:00"
    ],
    [
-    "2026-01-15T04:25:00+00:00",
-    "1.83",
+    "2026-01-15T08:25:00+00:00",
+    "46.1",
     null,
-    "2026-01-15T04:29:00+00:00"
+    "2026-01-15T08:29:00+00:00"
    ],
    [
-    "2026-01-15T04:30:00+00:00",
-    "0.0",
+    "2026-01-15T08:30:00+00:00",
+    "46.1",
     null,
-    "2026-01-15T04:34:00+00:00"
+    "2026-01-15T08:34:00+00:00"
    ],
    [
-    "2026-01-15T04:35:00+00:00",
-    "0.0",
+    "2026-01-15T08:35:00+00:00",
+    "46.1",
     null,
-    "2026-01-15T04:39:00+00:00"
+    "2026-01-15T08:39:00+00:00"
    ],
    [
-    "2026-01-15T04:40:00+00:00",
-    "0.0",
+    "2026-01-15T08:40:00+00:00",
+    "46.1",
     null,
-    "2026-01-15T04:44:00+00:00"
+    "2026-01-15T08:44:00+00:00"
    ],
    [
-    "2026-01-15T04:45:00+00:00",
-    "0.0",
+    "2026-01-15T08:45:00+00:00",
+    "46.1",
     null,
-    "2026-01-15T04:49:00+00:00"
+    "2026-01-15T08:49:00+00:00"
    ],
    [
-    "2026-01-15T04:50:00+00:00",
-    "0.0",
+    "2026-01-15T08:50:00+00:00",
+    "46.0",
     null,
-    "2026-01-15T04:54:00+00:00"
+    "2026-01-15T08:54:00+00:00"
    ],
    [
-    "2026-01-15T04:55:00+00:00",
-    "0.0",
+    "2026-01-15T08:55:00+00:00",
+    "46.0",
     null,
-    "2026-01-15T04:59:00+00:00"
+    "2026-01-15T08:59:00+00:00"
    ],
    [
-    "2026-01-15T05:00:00+00:00",
-    "0.0",
+    "2026-01-15T09:00:00+00:00",
+    "46.0",
     null,
-    "2026-01-15T05:04:00+00:00"
+    "2026-01-15T09:04:00+00:00"
    ],
    [
-    "2026-01-15T05:05:00+00:00",
-    "0.0",
+    "2026-01-15T09:05:00+00:00",
+    "46.0",
     null,
-    "2026-01-15T05:09:00+00:00"
+    "2026-01-15T09:09:00+00:00"
    ],
    [
-    "2026-01-15T05:10:00+00:00",
-    "0.0",
+    "2026-01-15T09:10:00+00:00",
+    "46.0",
     null,
-    "2026-01-15T05:14:00+00:00"
+    "2026-01-15T09:14:00+00:00"
    ],
    [
-    "2026-01-15T05:15:00+00:00",
-    "0.0",
+    "2026-01-15T09:15:00+00:00",
+    "45.9",
     null,
-    "2026-01-15T05:19:00+00:00"
+    "2026-01-15T09:19:00+00:00"
    ],
    [
-    "2026-01-15T05:20:00+00:00",
-    "0.0",
+    "2026-01-15T09:20:00+00:00",
+    "45.9",
     null,
-    "2026-01-15T05:24:00+00:00"
+    "2026-01-15T09:24:00+00:00"
    ],
    [
-    "2026-01-15T05:25:00+00:00",
-    "0.0",
+    "2026-01-15T09:25:00+00:00",
+    "45.9",
     null,
-    "2026-01-15T05:29:00+00:00"
+    "2026-01-15T09:29:00+00:00"
    ],
    [
-    "2026-01-15T05:30:00+00:00",
-    "0.0",
+    "2026-01-15T09:30:00+00:00",
+    "45.9",
     null,
-    "2026-01-15T05:34:00+00:00"
+    "2026-01-15T09:34:00+00:00"
    ],
    [
-    "2026-01-15T05:35:00+00:00",
-    "0.0",
+    "2026-01-15T09:35:00+00:00",
+    "45.9",
     null,
-    "2026-01-15T05:39:00+00:00"
+    "2026-01-15T09:39:00+00:00"
    ],
    [
-    "2026-01-15T05:40:00+00:00",
-    "0.0",
+    "2026-01-15T09:40:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T05:44:00+00:00"
+    "2026-01-15T09:44:00+00:00"
    ],
    [
-    "2026-01-15T05:45:00+00:00",
-    "0.0",
+    "2026-01-15T09:45:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T05:49:00+00:00"
+    "2026-01-15T09:49:00+00:00"
    ],
    [
-    "2026-01-15T05:50:00+00:00",
-    "0.0",
+    "2026-01-15T09:50:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T05:54:00+00:00"
+    "2026-01-15T09:54:00+00:00"
    ],
    [
-    "2026-01-15T05:55:00+00:00",
-    "0.0",
+    "2026-01-15T09:55:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T05:59:00+00:00"
+    "2026-01-15T09:59:00+00:00"
    ],
    [
-    "2026-01-15T06:00:00+00:00",
-    "0.0",
+    "2026-01-15T10:00:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T06:04:00+00:00"
+    "2026-01-15T10:04:00+00:00"
    ],
    [
-    "2026-01-15T06:05:00+00:00",
-    "0.0",
+    "2026-01-15T10:05:00+00:00",
+    "45.7",
     null,
-    "2026-01-15T06:09:00+00:00"
+    "2026-01-15T10:09:00+00:00"
    ],
    [
-    "2026-01-15T06:10:00+00:00",
-    "0.0",
+    "2026-01-15T10:10:00+00:00",
+    "45.7",
     null,
-    "2026-01-15T06:14:00+00:00"
+    "2026-01-15T10:14:00+00:00"
    ],
    [
-    "2026-01-15T06:15:00+00:00",
-    "0.0",
+    "2026-01-15T10:15:00+00:00",
+    "45.7",
     null,
-    "2026-01-15T06:19:00+00:00"
+    "2026-01-15T10:19:00+00:00"
    ],
    [
-    "2026-01-15T06:20:00+00:00",
-    "0.0",
+    "2026-01-15T10:20:00+00:00",
+    "45.7",
     null,
-    "2026-01-15T06:24:00+00:00"
+    "2026-01-15T10:24:00+00:00"
    ],
    [
-    "2026-01-15T06:25:00+00:00",
-    "0.0",
+    "2026-01-15T10:25:00+00:00",
+    "45.7",
     null,
-    "2026-01-15T06:29:00+00:00"
+    "2026-01-15T10:29:00+00:00"
    ],
    [
-    "2026-01-15T06:30:00+00:00",
-    "0.0",
+    "2026-01-15T10:30:00+00:00",
+    "45.6",
     null,
-    "2026-01-15T06:34:00+00:00"
+    "2026-01-15T10:34:00+00:00"
    ],
    [
-    "2026-01-15T06:35:00+00:00",
-    "0.0",
+    "2026-01-15T10:35:00+00:00",
+    "45.6",
     null,
-    "2026-01-15T06:39:00+00:00"
+    "2026-01-15T10:39:00+00:00"
    ],
    [
-    "2026-01-15T06:40:00+00:00",
-    "0.0",
+    "2026-01-15T10:40:00+00:00",
+    "45.6",
     null,
-    "2026-01-15T06:44:00+00:00"
+    "2026-01-15T10:44:00+00:00"
    ],
    [
-    "2026-01-15T06:45:00+00:00",
-    "0.0",
+    "2026-01-15T10:45:00+00:00",
+    "45.6",
     null,
-    "2026-01-15T06:49:00+00:00"
+    "2026-01-15T10:49:00+00:00"
    ],
    [
-    "2026-01-15T06:50:00+00:00",
-    "0.0",
+    "2026-01-15T10:50:00+00:00",
+    "45.6",
     null,
-    "2026-01-15T06:54:00+00:00"
+    "2026-01-15T10:54:00+00:00"
    ],
    [
-    "2026-01-15T06:55:00+00:00",
-    "0.0",
+    "2026-01-15T10:55:00+00:00",
+    "45.5",
     null,
-    "2026-01-15T06:59:00+00:00"
+    "2026-01-15T10:59:00+00:00"
    ],
    [
-    "2026-01-15T07:00:00+00:00",
-    "0.0",
+    "2026-01-15T11:00:00+00:00",
+    "45.5",
     null,
-    "2026-01-15T07:04:00+00:00"
+    "2026-01-15T11:04:00+00:00"
    ],
    [
-    "2026-01-15T07:05:00+00:00",
-    "0.0",
+    "2026-01-15T11:05:00+00:00",
+    "45.5",
     null,
-    "2026-01-15T07:09:00+00:00"
+    "2026-01-15T11:09:00+00:00"
    ],
    [
-    "2026-01-15T07:10:00+00:00",
-    "0.0",
+    "2026-01-15T11:10:00+00:00",
+    "45.5",
     null,
-    "2026-01-15T07:14:00+00:00"
+    "2026-01-15T11:14:00+00:00"
    ],
    [
-    "2026-01-15T07:15:00+00:00",
-    "0.0",
+    "2026-01-15T11:15:00+00:00",
+    "45.5",
     null,
-    "2026-01-15T07:19:00+00:00"
+    "2026-01-15T11:19:00+00:00"
    ],
    [
-    "2026-01-15T07:20:00+00:00",
-    "0.0",
+    "2026-01-15T11:20:00+00:00",
+    "45.4",
     null,
-    "2026-01-15T07:24:00+00:00"
+    "2026-01-15T11:24:00+00:00"
    ],
    [
-    "2026-01-15T07:25:00+00:00",
-    "0.0",
+    "2026-01-15T11:25:00+00:00",
+    "45.4",
     null,
-    "2026-01-15T07:29:00+00:00"
+    "2026-01-15T11:29:00+00:00"
    ],
    [
-    "2026-01-15T07:30:00+00:00",
-    "0.0",
+    "2026-01-15T11:30:00+00:00",
+    "45.4",
     null,
-    "2026-01-15T07:34:00+00:00"
+    "2026-01-15T11:34:00+00:00"
    ],
    [
-    "2026-01-15T07:35:00+00:00",
-    "0.0",
+    "2026-01-15T11:35:00+00:00",
+    "45.4",
     null,
-    "2026-01-15T07:39:00+00:00"
+    "2026-01-15T11:39:00+00:00"
    ],
    [
-    "2026-01-15T07:40:00+00:00",
-    "0.0",
+    "2026-01-15T11:40:00+00:00",
+    "45.4",
     null,
-    "2026-01-15T07:44:00+00:00"
+    "2026-01-15T11:44:00+00:00"
    ],
    [
-    "2026-01-15T07:45:00+00:00",
-    "0.0",
+    "2026-01-15T11:45:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T07:49:00+00:00"
+    "2026-01-15T11:49:00+00:00"
    ],
    [
-    "2026-01-15T07:50:00+00:00",
-    "0.0",
+    "2026-01-15T11:50:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T07:54:00+00:00"
+    "2026-01-15T11:54:00+00:00"
    ],
    [
-    "2026-01-15T07:55:00+00:00",
-    "0.0",
+    "2026-01-15T11:55:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T07:59:00+00:00"
+    "2026-01-15T11:59:00+00:00"
    ],
    [
-    "2026-01-15T08:00:00+00:00",
-    "0.0",
+    "2026-01-15T12:00:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T08:04:00+00:00"
+    "2026-01-15T12:04:00+00:00"
    ],
    [
-    "2026-01-15T08:05:00+00:00",
-    "0.0",
+    "2026-01-15T12:05:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T08:09:00+00:00"
+    "2026-01-15T12:09:00+00:00"
    ],
    [
-    "2026-01-15T08:10:00+00:00",
-    "0.0",
+    "2026-01-15T12:10:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T08:14:00+00:00"
+    "2026-01-15T12:14:00+00:00"
    ],
    [
-    "2026-01-15T08:15:00+00:00",
-    "0.0",
+    "2026-01-15T12:15:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T08:19:00+00:00"
+    "2026-01-15T12:19:00+00:00"
    ],
    [
-    "2026-01-15T08:20:00+00:00",
-    "0.0",
+    "2026-01-15T12:20:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T08:24:00+00:00"
+    "2026-01-15T12:24:00+00:00"
    ],
    [
-    "2026-01-15T08:25:00+00:00",
-    "0.0",
+    "2026-01-15T12:25:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T08:29:00+00:00"
+    "2026-01-15T12:29:00+00:00"
    ],
    [
-    "2026-01-15T08:30:00+00:00",
-    "0.0",
+    "2026-01-15T12:30:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T08:34:00+00:00"
+    "2026-01-15T12:34:00+00:00"
    ],
    [
-    "2026-01-15T08:35:00+00:00",
-    "0.0",
+    "2026-01-15T12:35:00+00:00",
+    "45.1",
     null,
-    "2026-01-15T08:39:00+00:00"
+    "2026-01-15T12:39:00+00:00"
    ],
    [
-    "2026-01-15T08:40:00+00:00",
-    "0.0",
+    "2026-01-15T12:40:00+00:00",
+    "45.1",
     null,
-    "2026-01-15T08:44:00+00:00"
+    "2026-01-15T12:44:00+00:00"
    ],
    [
-    "2026-01-15T08:45:00+00:00",
-    "0.0",
+    "2026-01-15T12:45:00+00:00",
+    "45.1",
     null,
-    "2026-01-15T08:49:00+00:00"
+    "2026-01-15T12:49:00+00:00"
    ],
    [
-    "2026-01-15T08:50:00+00:00",
-    "0.0",
+    "2026-01-15T12:50:00+00:00",
+    "45.1",
     null,
-    "2026-01-15T08:54:00+00:00"
+    "2026-01-15T12:54:00+00:00"
    ],
    [
-    "2026-01-15T08:55:00+00:00",
-    "0.0",
+    "2026-01-15T12:55:00+00:00",
+    "45.1",
     null,
-    "2026-01-15T08:59:00+00:00"
+    "2026-01-15T12:59:00+00:00"
    ],
    [
-    "2026-01-15T09:00:00+00:00",
-    "0.0",
+    "2026-01-15T13:00:00+00:00",
+    "45.0",
     null,
-    "2026-01-15T09:04:00+00:00"
+    "2026-01-15T13:04:00+00:00"
    ],
    [
-    "2026-01-15T09:05:00+00:00",
-    "0.0",
+    "2026-01-15T13:05:00+00:00",
+    "45.0",
     null,
-    "2026-01-15T09:09:00+00:00"
+    "2026-01-15T13:09:00+00:00"
    ],
    [
-    "2026-01-15T09:10:00+00:00",
-    "0.0",
+    "2026-01-15T13:10:00+00:00",
+    "45.0",
     null,
-    "2026-01-15T09:14:00+00:00"
+    "2026-01-15T13:14:00+00:00"
    ],
    [
-    "2026-01-15T09:15:00+00:00",
-    "0.0",
+    "2026-01-15T13:15:00+00:00",
+    "45.0",
     null,
-    "2026-01-15T09:19:00+00:00"
+    "2026-01-15T13:19:00+00:00"
    ],
    [
-    "2026-01-15T09:20:00+00:00",
-    "0.0",
+    "2026-01-15T13:20:00+00:00",
+    "45.0",
     null,
-    "2026-01-15T09:24:00+00:00"
+    "2026-01-15T13:24:00+00:00"
    ],
    [
-    "2026-01-15T09:25:00+00:00",
-    "0.0",
+    "2026-01-15T13:25:00+00:00",
+    "44.9",
     null,
-    "2026-01-15T09:29:00+00:00"
+    "2026-01-15T13:29:00+00:00"
    ],
    [
-    "2026-01-15T09:30:00+00:00",
-    "0.0",
+    "2026-01-15T13:30:00+00:00",
+    "44.9",
     null,
-    "2026-01-15T09:34:00+00:00"
+    "2026-01-15T13:34:00+00:00"
    ],
    [
-    "2026-01-15T09:35:00+00:00",
-    "0.0",
+    "2026-01-15T13:35:00+00:00",
+    "44.9",
     null,
-    "2026-01-15T09:39:00+00:00"
+    "2026-01-15T13:39:00+00:00"
    ],
    [
-    "2026-01-15T09:40:00+00:00",
-    "0.0",
+    "2026-01-15T13:40:00+00:00",
+    "44.9",
     null,
-    "2026-01-15T09:44:00+00:00"
+    "2026-01-15T13:44:00+00:00"
    ],
    [
-    "2026-01-15T09:45:00+00:00",
-    "0.0",
+    "2026-01-15T13:45:00+00:00",
+    "44.9",
     null,
-    "2026-01-15T09:49:00+00:00"
+    "2026-01-15T13:49:00+00:00"
    ],
    [
-    "2026-01-15T09:50:00+00:00",
-    "0.0",
+    "2026-01-15T13:50:00+00:00",
+    "44.8",
     null,
-    "2026-01-15T09:54:00+00:00"
+    "2026-01-15T13:54:00+00:00"
    ],
    [
-    "2026-01-15T09:55:00+00:00",
-    "0.0",
+    "2026-01-15T13:55:00+00:00",
+    "44.8",
     null,
-    "2026-01-15T09:59:00+00:00"
+    "2026-01-15T13:59:00+00:00"
    ],
    [
-    "2026-01-15T10:00:00+00:00",
-    "0.0",
+    "2026-01-15T14:00:00+00:00",
+    "44.8",
     null,
-    "2026-01-15T10:04:00+00:00"
+    "2026-01-15T14:04:00+00:00"
    ],
    [
-    "2026-01-15T10:05:00+00:00",
-    "0.0",
+    "2026-01-15T14:05:00+00:00",
+    "44.8",
     null,
-    "2026-01-15T10:09:00+00:00"
+    "2026-01-15T14:09:00+00:00"
    ],
    [
-    "2026-01-15T10:10:00+00:00",
-    "0.0",
+    "2026-01-15T14:10:00+00:00",
+    "44.8",
     null,
-    "2026-01-15T10:14:00+00:00"
+    "2026-01-15T14:14:00+00:00"
    ],
    [
-    "2026-01-15T10:15:00+00:00",
-    "0.0",
+    "2026-01-15T14:15:00+00:00",
+    "44.7",
     null,
-    "2026-01-15T10:19:00+00:00"
+    "2026-01-15T14:19:00+00:00"
    ],
    [
-    "2026-01-15T10:20:00+00:00",
-    "0.0",
+    "2026-01-15T14:20:00+00:00",
+    "44.7",
     null,
-    "2026-01-15T10:24:00+00:00"
+    "2026-01-15T14:24:00+00:00"
    ],
    [
-    "2026-01-15T10:25:00+00:00",
-    "0.0",
+    "2026-01-15T14:25:00+00:00",
+    "44.7",
     null,
-    "2026-01-15T10:29:00+00:00"
+    "2026-01-15T14:29:00+00:00"
    ],
    [
-    "2026-01-15T10:30:00+00:00",
-    "0.0",
+    "2026-01-15T14:30:00+00:00",
+    "45.2",
     null,
-    "2026-01-15T10:34:00+00:00"
+    "2026-01-15T14:34:00+00:00"
    ],
    [
-    "2026-01-15T10:35:00+00:00",
-    "0.0",
+    "2026-01-15T14:35:00+00:00",
+    "45.8",
     null,
-    "2026-01-15T10:39:00+00:00"
+    "2026-01-15T14:39:00+00:00"
    ],
    [
-    "2026-01-15T10:40:00+00:00",
-    "0.0",
+    "2026-01-15T14:40:00+00:00",
+    "46.3",
     null,
-    "2026-01-15T10:44:00+00:00"
+    "2026-01-15T14:44:00+00:00"
    ],
    [
-    "2026-01-15T10:45:00+00:00",
-    "0.0",
+    "2026-01-15T14:45:00+00:00",
+    "46.9",
     null,
-    "2026-01-15T10:49:00+00:00"
+    "2026-01-15T14:49:00+00:00"
    ],
    [
-    "2026-01-15T10:50:00+00:00",
-    "0.0",
+    "2026-01-15T14:50:00+00:00",
+    "47.4",
     null,
-    "2026-01-15T10:54:00+00:00"
+    "2026-01-15T14:54:00+00:00"
    ],
    [
-    "2026-01-15T10:55:00+00:00",
-    "0.0",
+    "2026-01-15T14:55:00+00:00",
+    "48.0",
     null,
-    "2026-01-15T10:59:00+00:00"
+    "2026-01-15T14:59:00+00:00"
    ],
    [
-    "2026-01-15T11:00:00+00:00",
-    "0.0",
+    "2026-01-15T15:00:00+00:00",
+    "48.5",
     null,
-    "2026-01-15T11:04:00+00:00"
+    "2026-01-15T15:04:00+00:00"
    ],
    [
-    "2026-01-15T11:05:00+00:00",
-    "0.0",
+    "2026-01-15T15:05:00+00:00",
+    "49.1",
     null,
-    "2026-01-15T11:09:00+00:00"
+    "2026-01-15T15:09:00+00:00"
    ],
    [
-    "2026-01-15T11:10:00+00:00",
-    "0.0",
+    "2026-01-15T15:10:00+00:00",
+    "49.6",
     null,
-    "2026-01-15T11:14:00+00:00"
+    "2026-01-15T15:14:00+00:00"
    ],
    [
-    "2026-01-15T11:15:00+00:00",
-    "0.0",
+    "2026-01-15T15:15:00+00:00",
+    "50.2",
     null,
-    "2026-01-15T11:19:00+00:00"
+    "2026-01-15T15:19:00+00:00"
    ],
    [
-    "2026-01-15T11:20:00+00:00",
-    "0.0",
+    "2026-01-15T15:20:00+00:00",
+    "50.7",
     null,
-    "2026-01-15T11:24:00+00:00"
+    "2026-01-15T15:24:00+00:00"
    ],
    [
-    "2026-01-15T11:25:00+00:00",
-    "0.0",
+    "2026-01-15T15:25:00+00:00",
+    "51.3",
     null,
-    "2026-01-15T11:29:00+00:00"
+    "2026-01-15T15:29:00+00:00"
    ],
    [
-    "2026-01-15T11:30:00+00:00",
-    "0.0",
+    "2026-01-15T15:30:00+00:00",
+    "51.8",
     null,
-    "2026-01-15T11:34:00+00:00"
+    "2026-01-15T15:34:00+00:00"
    ],
    [
-    "2026-01-15T11:35:00+00:00",
-    "0.0",
+    "2026-01-15T15:35:00+00:00",
+    "52.4",
     null,
-    "2026-01-15T11:39:00+00:00"
+    "2026-01-15T15:39:00+00:00"
    ],
    [
-    "2026-01-15T11:40:00+00:00",
-    "0.0",
+    "2026-01-15T15:40:00+00:00",
+    "52.9",
     null,
-    "2026-01-15T11:44:00+00:00"
+    "2026-01-15T15:44:00+00:00"
    ],
    [
-    "2026-01-15T11:45:00+00:00",
-    "0.0",
+    "2026-01-15T15:45:00+00:00",
+    "53.5",
     null,
-    "2026-01-15T11:49:00+00:00"
+    "2026-01-15T15:49:00+00:00"
    ],
    [
-    "2026-01-15T11:50:00+00:00",
-    "0.0",
+    "2026-01-15T15:50:00+00:00",
+    "54.0",
     null,
-    "2026-01-15T11:54:00+00:00"
+    "2026-01-15T15:54:00+00:00"
    ],
    [
-    "2026-01-15T11:55:00+00:00",
-    "0.0",
+    "2026-01-15T15:55:00+00:00",
+    "54.6",
     null,
-    "2026-01-15T11:59:00+00:00"
+    "2026-01-15T15:59:00+00:00"
    ],
    [
-    "2026-01-15T12:00:00+00:00",
-    "0.0",
+    "2026-01-15T16:00:00+00:00",
+    "54.6",
     null,
-    "2026-01-15T12:04:00+00:00"
+    "2026-01-15T16:04:00+00:00"
    ],
    [
-    "2026-01-15T12:05:00+00:00",
-    "0.0",
+    "2026-01-15T16:05:00+00:00",
+    "54.6",
     null,
-    "2026-01-15T12:09:00+00:00"
+    "2026-01-15T16:09:00+00:00"
    ],
    [
-    "2026-01-15T12:10:00+00:00",
-    "0.0",
+    "2026-01-15T16:10:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T12:14:00+00:00"
+    "2026-01-15T16:14:00+00:00"
    ],
    [
-    "2026-01-15T12:15:00+00:00",
-    "0.0",
+    "2026-01-15T16:15:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T12:19:00+00:00"
+    "2026-01-15T16:19:00+00:00"
    ],
    [
-    "2026-01-15T12:20:00+00:00",
-    "0.0",
+    "2026-01-15T16:20:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T12:24:00+00:00"
+    "2026-01-15T16:24:00+00:00"
    ],
    [
-    "2026-01-15T12:25:00+00:00",
-    "0.0",
+    "2026-01-15T16:25:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T12:29:00+00:00"
+    "2026-01-15T16:29:00+00:00"
    ],
    [
-    "2026-01-15T12:30:00+00:00",
-    "0.0",
+    "2026-01-15T16:30:00+00:00",
+    "54.5",
     null,
-    "2026-01-15T12:34:00+00:00"
+    "2026-01-15T16:34:00+00:00"
    ],
    [
-    "2026-01-15T12:35:00+00:00",
-    "0.0",
+    "2026-01-15T16:35:00+00:00",
+    "54.4",
     null,
-    "2026-01-15T12:39:00+00:00"
+    "2026-01-15T16:39:00+00:00"
    ],
    [
-    "2026-01-15T12:40:00+00:00",
-    "0.0",
+    "2026-01-15T16:40:00+00:00",
+    "54.4",
     null,
-    "2026-01-15T12:44:00+00:00"
+    "2026-01-15T16:44:00+00:00"
    ],
    [
-    "2026-01-15T12:45:00+00:00",
-    "0.0",
+    "2026-01-15T16:45:00+00:00",
+    "54.4",
     null,
-    "2026-01-15T12:49:00+00:00"
+    "2026-01-15T16:49:00+00:00"
    ],
    [
-    "2026-01-15T12:50:00+00:00",
-    "0.0",
+    "2026-01-15T16:50:00+00:00",
+    "54.4",
     null,
-    "2026-01-15T12:54:00+00:00"
+    "2026-01-15T16:54:00+00:00"
    ],
    [
-    "2026-01-15T12:55:00+00:00",
-    "0.0",
+    "2026-01-15T16:55:00+00:00",
+    "54.4",
     null,
-    "2026-01-15T12:59:00+00:00"
+    "2026-01-15T16:59:00+00:00"
    ],
    [
-    "2026-01-15T13:00:00+00:00",
-    "0.0",
+    "2026-01-15T17:00:00+00:00",
+    "54.3",
     null,
-    "2026-01-15T13:04:00+00:00"
+    "2026-01-15T17:04:00+00:00"
    ],
    [
-    "2026-01-15T13:05:00+00:00",
-    "0.0",
+    "2026-01-15T17:05:00+00:00",
+    "54.3",
     null,
-    "2026-01-15T13:09:00+00:00"
+    "2026-01-15T17:09:00+00:00"
    ],
    [
-    "2026-01-15T13:10:00+00:00",
-    "0.0",
+    "2026-01-15T17:10:00+00:00",
+    "54.3",
     null,
-    "2026-01-15T13:14:00+00:00"
+    "2026-01-15T17:14:00+00:00"
    ],
    [
-    "2026-01-15T13:15:00+00:00",
-    "0.0",
+    "2026-01-15T17:15:00+00:00",
+    "54.3",
     null,
-    "2026-01-15T13:19:00+00:00"
+    "2026-01-15T17:19:00+00:00"
    ],
    [
-    "2026-01-15T13:20:00+00:00",
-    "0.0",
+    "2026-01-15T17:20:00+00:00",
+    "54.3",
     null,
-    "2026-01-15T13:24:00+00:00"
+    "2026-01-15T17:24:00+00:00"
    ],
    [
-    "2026-01-15T13:25:00+00:00",
-    "0.0",
+    "2026-01-15T17:25:00+00:00",
+    "54.2",
     null,
-    "2026-01-15T13:29:00+00:00"
+    "2026-01-15T17:29:00+00:00"
    ],
    [
-    "2026-01-15T13:30:00+00:00",
-    "0.0",
+    "2026-01-15T17:30:00+00:00",
+    "53.1",
     null,
-    "2026-01-15T13:34:00+00:00"
+    "2026-01-15T17:34:00+00:00"
    ],
    [
-    "2026-01-15T13:35:00+00:00",
-    "0.0",
+    "2026-01-15T17:35:00+00:00",
+    "52.0",
     null,
-    "2026-01-15T13:39:00+00:00"
+    "2026-01-15T17:39:00+00:00"
    ],
    [
-    "2026-01-15T13:40:00+00:00",
-    "0.0",
+    "2026-01-15T17:40:00+00:00",
+    "50.9",
     null,
-    "2026-01-15T13:44:00+00:00"
+    "2026-01-15T17:44:00+00:00"
    ],
    [
-    "2026-01-15T13:45:00+00:00",
-    "0.0",
+    "2026-01-15T17:45:00+00:00",
+    "49.8",
     null,
-    "2026-01-15T13:49:00+00:00"
+    "2026-01-15T17:49:00+00:00"
    ],
    [
-    "2026-01-15T13:50:00+00:00",
-    "0.0",
+    "2026-01-15T17:50:00+00:00",
+    "48.6",
     null,
-    "2026-01-15T13:54:00+00:00"
+    "2026-01-15T17:54:00+00:00"
    ],
    [
-    "2026-01-15T13:55:00+00:00",
-    "0.0",
+    "2026-01-15T17:55:00+00:00",
+    "47.5",
     null,
-    "2026-01-15T13:59:00+00:00"
+    "2026-01-15T17:59:00+00:00"
    ],
    [
-    "2026-01-15T14:00:00+00:00",
-    "0.0",
+    "2026-01-15T18:00:00+00:00",
+    "46.4",
     null,
-    "2026-01-15T14:04:00+00:00"
+    "2026-01-15T18:04:00+00:00"
    ],
    [
-    "2026-01-15T14:05:00+00:00",
-    "0.0",
+    "2026-01-15T18:05:00+00:00",
+    "45.3",
     null,
-    "2026-01-15T14:09:00+00:00"
+    "2026-01-15T18:09:00+00:00"
    ],
    [
-    "2026-01-15T14:10:00+00:00",
-    "0.0",
+    "2026-01-15T18:10:00+00:00",
+    "44.2",
     null,
-    "2026-01-15T14:14:00+00:00"
+    "2026-01-15T18:14:00+00:00"
    ],
    [
-    "2026-01-15T14:15:00+00:00",
-    "0.0",
+    "2026-01-15T18:15:00+00:00",
+    "43.0",
     null,
-    "2026-01-15T14:19:00+00:00"
+    "2026-01-15T18:19:00+00:00"
    ],
    [
-    "2026-01-15T14:20:00+00:00",
-    "0.0",
+    "2026-01-15T18:20:00+00:00",
+    "41.9",
     null,
-    "2026-01-15T14:24:00+00:00"
+    "2026-01-15T18:24:00+00:00"
    ],
    [
-    "2026-01-15T14:25:00+00:00",
-    "0.0",
+    "2026-01-15T18:25:00+00:00",
+    "40.8",
     null,
-    "2026-01-15T14:29:00+00:00"
+    "2026-01-15T18:29:00+00:00"
    ],
    [
-    "2026-01-15T14:30:00+00:00",
-    "1.83",
+    "2026-01-15T18:30:00+00:00",
+    "40.8",
     null,
-    "2026-01-15T14:34:00+00:00"
+    "2026-01-15T18:34:00+00:00"
    ],
    [
-    "2026-01-15T14:35:00+00:00",
-    "1.83",
+    "2026-01-15T18:35:00+00:00",
+    "40.8",
     null,
-    "2026-01-15T14:39:00+00:00"
+    "2026-01-15T18:39:00+00:00"
    ],
    [
-    "2026-01-15T14:40:00+00:00",
-    "1.83",
+    "2026-01-15T18:40:00+00:00",
+    "40.7",
     null,
-    "2026-01-15T14:44:00+00:00"
+    "2026-01-15T18:44:00+00:00"
    ],
    [
-    "2026-01-15T14:45:00+00:00",
-    "1.83",
+    "2026-01-15T18:45:00+00:00",
+    "40.7",
     null,
-    "2026-01-15T14:49:00+00:00"
+    "2026-01-15T18:49:00+00:00"
    ],
    [
-    "2026-01-15T14:50:00+00:00",
-    "1.83",
+    "2026-01-15T18:50:00+00:00",
+    "40.7",
     null,
-    "2026-01-15T14:54:00+00:00"
+    "2026-01-15T18:54:00+00:00"
    ],
    [
-    "2026-01-15T14:55:00+00:00",
-    "1.83",
+    "2026-01-15T18:55:00+00:00",
+    "40.7",
     null,
-    "2026-01-15T14:59:00+00:00"
+    "2026-01-15T18:59:00+00:00"
    ],
    [
-    "2026-01-15T15:00:00+00:00",
-    "1.83",
+    "2026-01-15T19:00:00+00:00",
+    "40.7",
     null,
-    "2026-01-15T15:04:00+00:00"
+    "2026-01-15T19:04:00+00:00"
    ],
    [
-    "2026-01-15T15:05:00+00:00",
-    "1.83",
+    "2026-01-15T19:05:00+00:00",
+    "40.6",
     null,
-    "2026-01-15T15:09:00+00:00"
+    "2026-01-15T19:09:00+00:00"
    ],
    [
-    "2026-01-15T15:10:00+00:00",
-    "1.83",
+    "2026-01-15T19:10:00+00:00",
+    "40.6",
     null,
-    "2026-01-15T15:14:00+00:00"
+    "2026-01-15T19:14:00+00:00"
    ],
    [
-    "2026-01-15T15:15:00+00:00",
-    "1.83",
+    "2026-01-15T19:15:00+00:00",
+    "40.6",
     null,
-    "2026-01-15T15:19:00+00:00"
+    "2026-01-15T19:19:00+00:00"
    ],
    [
-    "2026-01-15T15:20:00+00:00",
-    "1.83",
+    "2026-01-15T19:20:00+00:00",
+    "40.6",
     null,
-    "2026-01-15T15:24:00+00:00"
+    "2026-01-15T19:24:00+00:00"
    ],
    [
-    "2026-01-15T15:25:00+00:00",
-    "1.83",
+    "2026-01-15T19:25:00+00:00",
+    "40.6",
     null,
-    "2026-01-15T15:29:00+00:00"
+    "2026-01-15T19:29:00+00:00"
    ],
    [
-    "2026-01-15T15:30:00+00:00",
-    "1.83",
+    "2026-01-15T19:30:00+00:00",
+    "40.5",
     null,
-    "2026-01-15T15:34:00+00:00"
+    "2026-01-15T19:34:00+00:00"
    ],
    [
-    "2026-01-15T15:35:00+00:00",
-    "1.83",
+    "2026-01-15T19:35:00+00:00",
+    "40.5",
     null,
-    "2026-01-15T15:39:00+00:00"
+    "2026-01-15T19:39:00+00:00"
    ],
    [
-    "2026-01-15T15:40:00+00:00",
-    "1.83",
+    "2026-01-15T19:40:00+00:00",
+    "40.5",
     null,
-    "2026-01-15T15:44:00+00:00"
+    "2026-01-15T19:44:00+00:00"
    ],
    [
-    "2026-01-15T15:45:00+00:00",
-    "1.83",
+    "2026-01-15T19:45:00+00:00",
+    "40.5",
     null,
-    "2026-01-15T15:49:00+00:00"
+    "2026-01-15T19:49:00+00:00"
    ],
    [
-    "2026-01-15T15:50:00+00:00",
-    "1.83",
+    "2026-01-15T19:50:00+00:00",
+    "40.5",
     null,
-    "2026-01-15T15:54:00+00:00"
+    "2026-01-15T19:54:00+00:00"
    ],
    [
-    "2026-01-15T15:55:00+00:00",
-    "1.83",
+    "2026-01-15T19:55:00+00:00",
+    "40.4",
     null,
-    "2026-01-15T15:59:00+00:00"
+    "2026-01-15T19:59:00+00:00"
    ],
    [
-    "2026-01-15T16:00:00+00:00",
-    "0.0",
+    "2026-01-15T20:00:00+00:00",
+    "40.4",
     null,
-    "2026-01-15T16:04:00+00:00"
+    "2026-01-15T20:04:00+00:00"
    ],
    [
-    "2026-01-15T16:05:00+00:00",
-    "0.0",
+    "2026-01-15T20:05:00+00:00",
+    "40.4",
     null,
-    "2026-01-15T16:09:00+00:00"
+    "2026-01-15T20:09:00+00:00"
    ],
    [
-    "2026-01-15T16:10:00+00:00",
-    "0.0",
+    "2026-01-15T20:10:00+00:00",
+    "40.4",
     null,
-    "2026-01-15T16:14:00+00:00"
+    "2026-01-15T20:14:00+00:00"
    ],
    [
-    "2026-01-15T16:15:00+00:00",
-    "0.0",
+    "2026-01-15T20:15:00+00:00",
+    "40.4",
     null,
-    "2026-01-15T16:19:00+00:00"
+    "2026-01-15T20:19:00+00:00"
    ],
    [
-    "2026-01-15T16:20:00+00:00",
-    "0.0",
+    "2026-01-15T20:20:00+00:00",
+    "40.3",
     null,
-    "2026-01-15T16:24:00+00:00"
+    "2026-01-15T20:24:00+00:00"
    ],
    [
-    "2026-01-15T16:25:00+00:00",
-    "0.0",
+    "2026-01-15T20:25:00+00:00",
+    "40.3",
     null,
-    "2026-01-15T16:29:00+00:00"
+    "2026-01-15T20:29:00+00:00"
    ],
    [
-    "2026-01-15T16:30:00+00:00",
-    "0.0",
+    "2026-01-15T20:30:00+00:00",
+    "40.3",
     null,
-    "2026-01-15T16:34:00+00:00"
+    "2026-01-15T20:34:00+00:00"
    ],
    [
-    "2026-01-15T16:35:00+00:00",
-    "0.0",
+    "2026-01-15T20:35:00+00:00",
+    "40.3",
     null,
-    "2026-01-15T16:39:00+00:00"
+    "2026-01-15T20:39:00+00:00"
    ],
    [
-    "2026-01-15T16:40:00+00:00",
-    "0.0",
+    "2026-01-15T20:40:00+00:00",
+    "40.3",
     null,
-    "2026-01-15T16:44:00+00:00"
+    "2026-01-15T20:44:00+00:00"
    ],
    [
-    "2026-01-15T16:45:00+00:00",
-    "0.0",
+    "2026-01-15T20:45:00+00:00",
+    "40.2",
     null,
-    "2026-01-15T16:49:00+00:00"
+    "2026-01-15T20:49:00+00:00"
    ],
    [
-    "2026-01-15T16:50:00+00:00",
-    "0.0",
+    "2026-01-15T20:50:00+00:00",
+    "40.2",
     null,
-    "2026-01-15T16:54:00+00:00"
+    "2026-01-15T20:54:00+00:00"
    ],
    [
-    "2026-01-15T16:55:00+00:00",
-    "0.0",
+    "2026-01-15T20:55:00+00:00",
+    "40.2",
     null,
-    "2026-01-15T16:59:00+00:00"
+    "2026-01-15T20:59:00+00:00"
    ],
    [
-    "2026-01-15T17:00:00+00:00",
-    "0.0",
+    "2026-01-15T21:00:00+00:00",
+    "40.2",
     null,
-    "2026-01-15T17:04:00+00:00"
+    "2026-01-15T21:04:00+00:00"
    ],
    [
-    "2026-01-15T17:05:00+00:00",
-    "0.0",
+    "2026-01-15T21:05:00+00:00",
+    "40.2",
     null,
-    "2026-01-15T17:09:00+00:00"
+    "2026-01-15T21:09:00+00:00"
    ],
    [
-    "2026-01-15T17:10:00+00:00",
-    "0.0",
+    "2026-01-15T21:10:00+00:00",
+    "40.1",
     null,
-    "2026-01-15T17:14:00+00:00"
+    "2026-01-15T21:14:00+00:00"
    ],
    [
-    "2026-01-15T17:15:00+00:00",
-    "0.0",
+    "2026-01-15T21:15:00+00:00",
+    "40.1",
     null,
-    "2026-01-15T17:19:00+00:00"
+    "2026-01-15T21:19:00+00:00"
    ],
    [
-    "2026-01-15T17:20:00+00:00",
-    "0.0",
+    "2026-01-15T21:20:00+00:00",
+    "40.1",
     null,
-    "2026-01-15T17:24:00+00:00"
+    "2026-01-15T21:24:00+00:00"
    ],
    [
-    "2026-01-15T17:25:00+00:00",
-    "0.0",
+    "2026-01-15T21:25:00+00:00",
+    "40.1",
     null,
-    "2026-01-15T17:29:00+00:00"
+    "2026-01-15T21:29:00+00:00"
    ],
    [
-    "2026-01-15T17:30:00+00:00",
-    "0.0",
+    "2026-01-15T21:30:00+00:00",
+    "40.1",
     null,
-    "2026-01-15T17:34:00+00:00"
+    "2026-01-15T21:34:00+00:00"
    ],
    [
-    "2026-01-15T17:35:00+00:00",
-    "0.0",
+    "2026-01-15T21:35:00+00:00",
+    "40.0",
     null,
-    "2026-01-15T17:39:00+00:00"
+    "2026-01-15T21:39:00+00:00"
    ],
    [
-    "2026-01-15T17:40:00+00:00",
-    "0.0",
+    "2026-01-15T21:40:00+00:00",
+    "40.0",
     null,
-    "2026-01-15T17:44:00+00:00"
+    "2026-01-15T21:44:00+00:00"
    ],
    [
-    "2026-01-15T17:45:00+00:00",
-    "0.0",
+    "2026-01-15T21:45:00+00:00",
+    "40.0",
     null,
-    "2026-01-15T17:49:00+00:00"
+    "2026-01-15T21:49:00+00:00"
    ],
    [
-    "2026-01-15T17:50:00+00:00",
-    "0.0",
+    "2026-01-15T21:50:00+00:00",
+    "40.0",
     null,
-    "2026-01-15T17:54:00+00:00"
+    "2026-01-15T21:54:00+00:00"
    ],
    [
-    "2026-01-15T17:55:00+00:00",
-    "0.0",
+    "2026-01-15T21:55:00+00:00",
+    "40.0",
     null,
-    "2026-01-15T17:59:00+00:00"
+    "2026-01-15T21:59:00+00:00"
    ],
    [
-    "2026-01-15T18:00:00+00:00",
-    "0.0",
+    "2026-01-15T22:00:00+00:00",
+    "39.9",
     null,
-    "2026-01-15T18:04:00+00:00"
+    "2026-01-15T22:04:00+00:00"
    ],
    [
-    "2026-01-15T18:05:00+00:00",
-    "0.0",
+    "2026-01-15T22:05:00+00:00",
+    "39.9",
     null,
-    "2026-01-15T18:09:00+00:00"
+    "2026-01-15T22:09:00+00:00"
    ],
    [
-    "2026-01-15T18:10:00+00:00",
-    "0.0",
+    "2026-01-15T22:10:00+00:00",
+    "39.9",
     null,
-    "2026-01-15T18:14:00+00:00"
+    "2026-01-15T22:14:00+00:00"
    ],
    [
-    "2026-01-15T18:15:00+00:00",
-    "0.0",
+    "2026-01-15T22:15:00+00:00",
+    "39.9",
     null,
-    "2026-01-15T18:19:00+00:00"
+    "2026-01-15T22:19:00+00:00"
    ],
    [
-    "2026-01-15T18:20:00+00:00",
-    "0.0",
+    "2026-01-15T22:20:00+00:00",
+    "39.9",
     null,
-    "2026-01-15T18:24:00+00:00"
+    "2026-01-15T22:24:00+00:00"
    ],
    [
-    "2026-01-15T18:25:00+00:00",
-    "0.0",
+    "2026-01-15T22:25:00+00:00",
+    "39.8",
     null,
-    "2026-01-15T18:29:00+00:00"
+    "2026-01-15T22:29:00+00:00"
    ],
    [
-    "2026-01-15T18:30:00+00:00",
-    "0.0",
+    "2026-01-15T22:30:00+00:00",
+    "39.8",
     null,
-    "2026-01-15T18:34:00+00:00"
+    "2026-01-15T22:34:00+00:00"
    ],
    [
-    "2026-01-15T18:35:00+00:00",
-    "0.0",
+    "2026-01-15T22:35:00+00:00",
+    "39.8",
     null,
-    "2026-01-15T18:39:00+00:00"
+    "2026-01-15T22:39:00+00:00"
    ],
    [
-    "2026-01-15T18:40:00+00:00",
-    "0.0",
+    "2026-01-15T22:40:00+00:00",
+    "39.8",
     null,
-    "2026-01-15T18:44:00+00:00"
+    "2026-01-15T22:44:00+00:00"
    ],
    [
-    "2026-01-15T18:45:00+00:00",
-    "0.0",
+    "2026-01-15T22:45:00+00:00",
+    "39.8",
     null,
-    "2026-01-15T18:49:00+00:00"
+    "2026-01-15T22:49:00+00:00"
    ],
    [
-    "2026-01-15T18:50:00+00:00",
-    "0.0",
+    "2026-01-15T22:50:00+00:00",
+    "39.7",
     null,
-    "2026-01-15T18:54:00+00:00"
+    "2026-01-15T22:54:00+00:00"
    ],
    [
-    "2026-01-15T18:55:00+00:00",
-    "0.0",
+    "2026-01-15T22:55:00+00:00",
+    "39.7",
     null,
-    "2026-01-15T18:59:00+00:00"
-   ],
+    "2026-01-15T22:59:00+00:00"
+   ]
+  ],
+  "sensor.e_2cdc621bcb": [
    [
-    "2026-01-15T19:00:00+00:00",
-    "0.0",
-    null,
-    "2026-01-15T19:04:00+00:00"
+    "2026-01-14T22:30:00+00:00",
+    "off",
+    {
+     "heat_pump_on": false
+    },
+    "2026-01-14T22:59:00+00:00"
    ],
    [
-    "2026-01-15T19:05:00+00:00",
-    "0.0",
+    "2026-01-14T23:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:09:00+00:00"
+    "2026-01-14T23:29:00+00:00"
    ],
    [
-    "2026-01-15T19:10:00+00:00",
-    "0.0",
+    "2026-01-14T23:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:14:00+00:00"
+    "2026-01-14T23:59:00+00:00"
    ],
    [
-    "2026-01-15T19:15:00+00:00",
-    "0.0",
+    "2026-01-15T00:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:19:00+00:00"
+    "2026-01-15T00:29:00+00:00"
    ],
    [
-    "2026-01-15T19:20:00+00:00",
-    "0.0",
+    "2026-01-15T00:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:24:00+00:00"
+    "2026-01-15T00:59:00+00:00"
    ],
    [
-    "2026-01-15T19:25:00+00:00",
-    "0.0",
-    null,
-    "2026-01-15T19:29:00+00:00"
+    "2026-01-15T01:00:00+00:00",
+    "off",
+    {
+     "heat_pump_on": true
+    },
+    "2026-01-15T01:29:00+00:00"
    ],
    [
-    "2026-01-15T19:30:00+00:00",
-    "0.0",
+    "2026-01-15T01:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:34:00+00:00"
+    "2026-01-15T01:59:00+00:00"
    ],
    [
-    "2026-01-15T19:35:00+00:00",
-    "0.0",
+    "2026-01-15T02:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:39:00+00:00"
+    "2026-01-15T02:29:00+00:00"
    ],
    [
-    "2026-01-15T19:40:00+00:00",
-    "0.0",
+    "2026-01-15T02:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:44:00+00:00"
+    "2026-01-15T02:59:00+00:00"
    ],
    [
-    "2026-01-15T19:45:00+00:00",
-    "0.0",
+    "2026-01-15T03:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:49:00+00:00"
+    "2026-01-15T03:29:00+00:00"
    ],
    [
-    "2026-01-15T19:50:00+00:00",
-    "0.0",
+    "2026-01-15T03:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:54:00+00:00"
+    "2026-01-15T03:59:00+00:00"
    ],
    [
-    "2026-01-15T19:55:00+00:00",
-    "0.0",
+    "2026-01-15T04:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T19:59:00+00:00"
+    "2026-01-15T04:29:00+00:00"
    ],
    [
-    "2026-01-15T20:00:00+00:00",
-    "0.0",
+    "2026-01-15T04:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:04:00+00:00"
+    "2026-01-15T04:59:00+00:00"
    ],
    [
-    "2026-01-15T20:05:00+00:00",
-    "0.0",
-    null,
-    "2026-01-15T20:09:00+00:00"
+    "2026-01-15T05:00:00+00:00",
+    "off",
+    {
+     "heat_pump_on": false
+    },
+    "2026-01-15T05:29:00+00:00"
    ],
    [
-    "2026-01-15T20:10:00+00:00",
-    "0.0",
+    "2026-01-15T05:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:14:00+00:00"
+    "2026-01-15T05:59:00+00:00"
    ],
    [
-    "2026-01-15T20:15:00+00:00",
-    "0.0",
+    "2026-01-15T06:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:19:00+00:00"
+    "2026-01-15T06:29:00+00:00"
    ],
    [
-    "2026-01-15T20:20:00+00:00",
-    "0.0",
+    "2026-01-15T06:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:24:00+00:00"
+    "2026-01-15T06:59:00+00:00"
    ],
    [
-    "2026-01-15T20:25:00+00:00",
-    "0.0",
+    "2026-01-15T07:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:29:00+00:00"
+    "2026-01-15T07:29:00+00:00"
    ],
    [
-    "2026-01-15T20:30:00+00:00",
-    "0.0",
+    "2026-01-15T07:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:34:00+00:00"
+    "2026-01-15T07:59:00+00:00"
    ],
    [
-    "2026-01-15T20:35:00+00:00",
-    "0.0",
+    "2026-01-15T08:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:39:00+00:00"
+    "2026-01-15T08:29:00+00:00"
    ],
    [
-    "2026-01-15T20:40:00+00:00",
-    "0.0",
+    "2026-01-15T08:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:44:00+00:00"
+    "2026-01-15T08:59:00+00:00"
    ],
    [
-    "2026-01-15T20:45:00+00:00",
-    "0.0",
+    "2026-01-15T09:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:49:00+00:00"
+    "2026-01-15T09:29:00+00:00"
    ],
    [
-    "2026-01-15T20:50:00+00:00",
-    "0.0",
+    "2026-01-15T09:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:54:00+00:00"
+    "2026-01-15T09:59:00+00:00"
    ],
    [
-    "2026-01-15T20:55:00+00:00",
-    "0.0",
+    "2026-01-15T10:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T20:59:00+00:00"
+    "2026-01-15T10:29:00+00:00"
    ],
    [
-    "2026-01-15T21:00:00+00:00",
-    "0.0",
+    "2026-01-15T10:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:04:00+00:00"
+    "2026-01-15T10:59:00+00:00"
    ],
    [
-    "2026-01-15T21:05:00+00:00",
-    "0.0",
+    "2026-01-15T11:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:09:00+00:00"
+    "2026-01-15T11:29:00+00:00"
    ],
    [
-    "2026-01-15T21:10:00+00:00",
-    "0.0",
+    "2026-01-15T11:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:14:00+00:00"
+    "2026-01-15T11:59:00+00:00"
    ],
    [
-    "2026-01-15T21:15:00+00:00",
-    "0.0",
+    "2026-01-15T12:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:19:00+00:00"
+    "2026-01-15T12:29:00+00:00"
    ],
    [
-    "2026-01-15T21:20:00+00:00",
-    "0.0",
+    "2026-01-15T12:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:24:00+00:00"
+    "2026-01-15T12:59:00+00:00"
    ],
    [
-    "2026-01-15T21:25:00+00:00",
-    "0.0",
+    "2026-01-15T13:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:29:00+00:00"
+    "2026-01-15T13:29:00+00:00"
    ],
    [
-    "2026-01-15T21:30:00+00:00",
-    "0.0",
+    "2026-01-15T13:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:34:00+00:00"
+    "2026-01-15T13:59:00+00:00"
    ],
    [
-    "2026-01-15T21:35:00+00:00",
-    "0.0",
+    "2026-01-15T14:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:39:00+00:00"
+    "2026-01-15T14:29:00+00:00"
    ],
    [
-    "2026-01-15T21:40:00+00:00",
-    "0.0",
+    "2026-01-15T14:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:44:00+00:00"
+    "2026-01-15T14:59:00+00:00"
    ],
    [
-    "2026-01-15T21:45:00+00:00",
-    "0.0",
+    "2026-01-15T15:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:49:00+00:00"
+    "2026-01-15T15:29:00+00:00"
    ],
    [
-    "2026-01-15T21:50:00+00:00",
-    "0.0",
+    "2026-01-15T15:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:54:00+00:00"
+    "2026-01-15T15:59:00+00:00"
    ],
    [
-    "2026-01-15T21:55:00+00:00",
-    "0.0",
+    "2026-01-15T16:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T21:59:00+00:00"
+    "2026-01-15T16:29:00+00:00"
    ],
    [
-    "2026-01-15T22:00:00+00:00",
-    "0.0",
+    "2026-01-15T16:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:04:00+00:00"
+    "2026-01-15T16:59:00+00:00"
    ],
    [
-    "2026-01-15T22:05:00+00:00",
-    "0.0",
+    "2026-01-15T17:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:09:00+00:00"
+    "2026-01-15T17:29:00+00:00"
    ],
    [
-    "2026-01-15T22:10:00+00:00",
-    "0.0",
+    "2026-01-15T17:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:14:00+00:00"
+    "2026-01-15T17:59:00+00:00"
    ],
    [
-    "2026-01-15T22:15:00+00:00",
-    "0.0",
+    "2026-01-15T18:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:19:00+00:00"
+    "2026-01-15T18:29:00+00:00"
    ],
    [
-    "2026-01-15T22:20:00+00:00",
-    "0.0",
+    "2026-01-15T18:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:24:00+00:00"
+    "2026-01-15T18:59:00+00:00"
    ],
    [
-    "2026-01-15T22:25:00+00:00",
-    "0.0",
+    "2026-01-15T19:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:29:00+00:00"
+    "2026-01-15T19:29:00+00:00"
    ],
    [
-    "2026-01-15T22:30:00+00:00",
-    "0.0",
+    "2026-01-15T19:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:34:00+00:00"
+    "2026-01-15T19:59:00+00:00"
    ],
    [
-    "2026-01-15T22:35:00+00:00",
-    "0.0",
+    "2026-01-15T20:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:39:00+00:00"
+    "2026-01-15T20:29:00+00:00"
    ],
    [
-    "2026-01-15T22:40:00+00:00",
-    "0.0",
+    "2026-01-15T20:30:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:44:00+00:00"
+    "2026-01-15T20:59:00+00:00"
    ],
    [
-    "2026-01-15T22:45:00+00:00",
-    "0.0",
+    "2026-01-15T21:00:00+00:00",
+    "off",
     null,
-    "2026-01-15T22:49:00+00:00"
+    "2026-01-15T21:29:00+00:00"
    ],
    [
-    "2026-01-15T22:50:00+00:00",
-    "0.0",
-    null,
-    "2026-01-15T22:54:00+00:00"
+    "2026-01-15T21:30:00+00:00",
+    "off",
+    null,
+    "2026-01-15T21:59:00+00:00"
    ],
    [
-    "2026-01-15T22:55:00+00:00",
-    "0.0",
+    "2026-01-15T22:00:00+00:00",
+    "off",
+    null,
+    "2026-01-15T22:29:00+00:00"
+   ],
+   [
+    "2026-01-15T22:30:00+00:00",
+    "off",
     null,
     "2026-01-15T22:59:00+00:00"
    ]
   ],
-  "sensor.hot_water_tank_temperature": [
+  "sensor.heat_pump_power": [
    [
     "2026-01-14T22:55:00+00:00",
-    "48.1",
+    "0.0",
     {
-     "device_class": "temperature",
+     "device_class": "power",
      "state_class": "measurement",
-     "unit_of_measurement": "\u00b0C"
+     "unit_of_measurement": "kW"
     },
     "2026-01-14T22:59:00+00:00"
    ],
    [
     "2026-01-14T23:00:00+00:00",
-    "48.0",
+    "0.0",
     null,
     "2026-01-14T23:04:00+00:00"
    ],
    [
     "2026-01-14T23:05:00+00:00",
-    "48.0",
+    "0.0",
     null,
     "2026-01-14T23:09:00+00:00"
    ],
    [
     "2026-01-14T23:10:00+00:00",
-    "48.0",
+    "0.0",
     null,
     "2026-01-14T23:14:00+00:00"
    ],
    [
     "2026-01-14T23:15:00+00:00",
-    "48.0",
+    "0.0",
     null,
     "2026-01-14T23:19:00+00:00"
    ],
    [
     "2026-01-14T23:20:00+00:00",
-    "48.0",
+    "0.0",
     null,
     "2026-01-14T23:24:00+00:00"
    ],
    [
     "2026-01-14T23:25:00+00:00",
-    "47.9",
+    "0.0",
     null,
     "2026-01-14T23:29:00+00:00"
    ],
    [
     "2026-01-14T23:30:00+00:00",
-    "47.9",
+    "0.0",
     null,
     "2026-01-14T23:34:00+00:00"
    ],
    [
     "2026-01-14T23:35:00+00:00",
-    "47.9",
+    "0.0",
     null,
     "2026-01-14T23:39:00+00:00"
    ],
    [
     "2026-01-14T23:40:00+00:00",
-    "47.9",
+    "0.0",
     null,
     "2026-01-14T23:44:00+00:00"
    ],
    [
     "2026-01-14T23:45:00+00:00",
-    "47.9",
+    "0.0",
     null,
     "2026-01-14T23:49:00+00:00"
    ],
    [
     "2026-01-14T23:50:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-14T23:54:00+00:00"
    ],
    [
     "2026-01-14T23:55:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-14T23:59:00+00:00"
    ],
    [
     "2026-01-15T00:00:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-15T00:04:00+00:00"
    ],
    [
     "2026-01-15T00:05:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-15T00:09:00+00:00"
    ],
    [
     "2026-01-15T00:10:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-15T00:14:00+00:00"
    ],
    [
     "2026-01-15T00:15:00+00:00",
-    "47.7",
+    "0.0",
     null,
     "2026-01-15T00:19:00+00:00"
    ],
    [
     "2026-01-15T00:20:00+00:00",
-    "47.7",
+    "0.0",
     null,
     "2026-01-15T00:24:00+00:00"
    ],
    [
     "2026-01-15T00:25:00+00:00",
-    "47.7",
+    "0.0",
     null,
     "2026-01-15T00:29:00+00:00"
    ],
    [
     "2026-01-15T00:30:00+00:00",
-    "47.7",
+    "0.0",
     null,
     "2026-01-15T00:34:00+00:00"
    ],
    [
     "2026-01-15T00:35:00+00:00",
-    "47.7",
+    "0.0",
     null,
     "2026-01-15T00:39:00+00:00"
    ],
    [
     "2026-01-15T00:40:00+00:00",
-    "47.6",
+    "0.0",
     null,
     "2026-01-15T00:44:00+00:00"
    ],
    [
     "2026-01-15T00:45:00+00:00",
-    "47.6",
+    "0.0",
     null,
     "2026-01-15T00:49:00+00:00"
    ],
    [
     "2026-01-15T00:50:00+00:00",
-    "47.6",
+    "0.0",
     null,
     "2026-01-15T00:54:00+00:00"
    ],
    [
     "2026-01-15T00:55:00+00:00",
-    "47.6",
+    "0.0",
     null,
     "2026-01-15T00:59:00+00:00"
    ],
    [
     "2026-01-15T01:00:00+00:00",
-    "47.6",
+    "0.0",
     null,
     "2026-01-15T01:04:00+00:00"
    ],
    [
     "2026-01-15T01:05:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T01:09:00+00:00"
    ],
    [
     "2026-01-15T01:10:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T01:14:00+00:00"
    ],
    [
     "2026-01-15T01:15:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T01:19:00+00:00"
    ],
    [
     "2026-01-15T01:20:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T01:24:00+00:00"
    ],
    [
     "2026-01-15T01:25:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T01:29:00+00:00"
    ],
    [
     "2026-01-15T01:30:00+00:00",
-    "47.4",
+    "0.0",
     null,
     "2026-01-15T01:34:00+00:00"
    ],
    [
     "2026-01-15T01:35:00+00:00",
-    "47.4",
+    "0.0",
     null,
     "2026-01-15T01:39:00+00:00"
    ],
    [
     "2026-01-15T01:40:00+00:00",
-    "47.4",
+    "0.0",
     null,
     "2026-01-15T01:44:00+00:00"
    ],
    [
     "2026-01-15T01:45:00+00:00",
-    "47.4",
+    "0.0",
     null,
     "2026-01-15T01:49:00+00:00"
    ],
    [
     "2026-01-15T01:50:00+00:00",
-    "47.4",
+    "0.0",
     null,
     "2026-01-15T01:54:00+00:00"
    ],
    [
     "2026-01-15T01:55:00+00:00",
-    "47.3",
+    "0.0",
     null,
     "2026-01-15T01:59:00+00:00"
    ],
    [
     "2026-01-15T02:00:00+00:00",
-    "47.3",
+    "0.0",
     null,
     "2026-01-15T02:04:00+00:00"
    ],
    [
     "2026-01-15T02:05:00+00:00",
-    "47.3",
+    "0.0",
     null,
     "2026-01-15T02:09:00+00:00"
    ],
    [
     "2026-01-15T02:10:00+00:00",
-    "47.3",
+    "0.0",
     null,
     "2026-01-15T02:14:00+00:00"
    ],
    [
     "2026-01-15T02:15:00+00:00",
-    "47.3",
+    "0.0",
     null,
     "2026-01-15T02:19:00+00:00"
    ],
    [
     "2026-01-15T02:20:00+00:00",
-    "47.2",
+    "0.0",
     null,
     "2026-01-15T02:24:00+00:00"
    ],
    [
     "2026-01-15T02:25:00+00:00",
-    "47.2",
+    "0.0",
     null,
     "2026-01-15T02:29:00+00:00"
    ],
    [
     "2026-01-15T02:30:00+00:00",
-    "47.2",
+    "0.0",
     null,
     "2026-01-15T02:34:00+00:00"
    ],
    [
     "2026-01-15T02:35:00+00:00",
-    "47.2",
+    "0.0",
     null,
     "2026-01-15T02:39:00+00:00"
    ],
    [
     "2026-01-15T02:40:00+00:00",
-    "47.2",
+    "0.0",
     null,
     "2026-01-15T02:44:00+00:00"
    ],
    [
     "2026-01-15T02:45:00+00:00",
-    "47.1",
+    "0.0",
     null,
     "2026-01-15T02:49:00+00:00"
    ],
    [
     "2026-01-15T02:50:00+00:00",
-    "47.1",
+    "0.0",
     null,
     "2026-01-15T02:54:00+00:00"
    ],
    [
     "2026-01-15T02:55:00+00:00",
-    "47.1",
+    "0.0",
     null,
     "2026-01-15T02:59:00+00:00"
    ],
    [
     "2026-01-15T03:00:00+00:00",
-    "47.6",
+    "1.83",
     null,
     "2026-01-15T03:04:00+00:00"
    ],
    [
     "2026-01-15T03:05:00+00:00",
-    "48.2",
+    "1.83",
     null,
     "2026-01-15T03:09:00+00:00"
    ],
    [
     "2026-01-15T03:10:00+00:00",
-    "48.7",
+    "1.83",
     null,
     "2026-01-15T03:14:00+00:00"
    ],
    [
     "2026-01-15T03:15:00+00:00",
-    "49.3",
+    "1.83",
     null,
     "2026-01-15T03:19:00+00:00"
    ],
    [
     "2026-01-15T03:20:00+00:00",
-    "49.8",
+    "1.83",
     null,
     "2026-01-15T03:24:00+00:00"
    ],
    [
     "2026-01-15T03:25:00+00:00",
-    "50.4",
+    "1.83",
     null,
     "2026-01-15T03:29:00+00:00"
    ],
    [
     "2026-01-15T03:30:00+00:00",
-    "50.9",
+    "1.83",
     null,
     "2026-01-15T03:34:00+00:00"
    ],
    [
     "2026-01-15T03:35:00+00:00",
-    "51.5",
+    "1.83",
     null,
     "2026-01-15T03:39:00+00:00"
    ],
    [
     "2026-01-15T03:40:00+00:00",
-    "52.0",
+    "1.83",
     null,
     "2026-01-15T03:44:00+00:00"
    ],
    [
     "2026-01-15T03:45:00+00:00",
-    "52.6",
+    "1.83",
     null,
     "2026-01-15T03:49:00+00:00"
    ],
    [
     "2026-01-15T03:50:00+00:00",
-    "53.1",
+    "1.83",
     null,
     "2026-01-15T03:54:00+00:00"
    ],
    [
     "2026-01-15T03:55:00+00:00",
-    "53.7",
+    "1.83",
     null,
     "2026-01-15T03:59:00+00:00"
    ],
    [
     "2026-01-15T04:00:00+00:00",
-    "54.2",
+    "1.83",
     null,
     "2026-01-15T04:04:00+00:00"
    ],
    [
     "2026-01-15T04:05:00+00:00",
-    "54.8",
+    "1.83",
     null,
     "2026-01-15T04:09:00+00:00"
    ],
    [
     "2026-01-15T04:10:00+00:00",
-    "55.3",
+    "1.83",
     null,
     "2026-01-15T04:14:00+00:00"
    ],
    [
     "2026-01-15T04:15:00+00:00",
-    "55.9",
+    "1.83",
     null,
     "2026-01-15T04:19:00+00:00"
    ],
    [
     "2026-01-15T04:20:00+00:00",
-    "56.4",
+    "1.83",
     null,
     "2026-01-15T04:24:00+00:00"
    ],
    [
     "2026-01-15T04:25:00+00:00",
-    "57.0",
+    "1.83",
     null,
     "2026-01-15T04:29:00+00:00"
    ],
    [
     "2026-01-15T04:30:00+00:00",
-    "57.0",
+    "0.0",
     null,
     "2026-01-15T04:34:00+00:00"
    ],
    [
     "2026-01-15T04:35:00+00:00",
-    "57.0",
+    "0.0",
     null,
     "2026-01-15T04:39:00+00:00"
    ],
    [
     "2026-01-15T04:40:00+00:00",
-    "56.9",
+    "0.0",
     null,
     "2026-01-15T04:44:00+00:00"
    ],
    [
     "2026-01-15T04:45:00+00:00",
-    "56.9",
+    "0.0",
     null,
     "2026-01-15T04:49:00+00:00"
    ],
    [
     "2026-01-15T04:50:00+00:00",
-    "56.9",
+    "0.0",
     null,
     "2026-01-15T04:54:00+00:00"
    ],
    [
     "2026-01-15T04:55:00+00:00",
-    "56.9",
+    "0.0",
     null,
     "2026-01-15T04:59:00+00:00"
    ],
    [
     "2026-01-15T05:00:00+00:00",
-    "56.9",
+    "0.0",
     null,
     "2026-01-15T05:04:00+00:00"
    ],
    [
     "2026-01-15T05:05:00+00:00",
-    "56.8",
+    "0.0",
     null,
     "2026-01-15T05:09:00+00:00"
    ],
    [
     "2026-01-15T05:10:00+00:00",
-    "56.8",
+    "0.0",
     null,
     "2026-01-15T05:14:00+00:00"
    ],
    [
     "2026-01-15T05:15:00+00:00",
-    "56.8",
+    "0.0",
     null,
     "2026-01-15T05:19:00+00:00"
    ],
    [
     "2026-01-15T05:20:00+00:00",
-    "56.8",
+    "0.0",
     null,
     "2026-01-15T05:24:00+00:00"
    ],
    [
     "2026-01-15T05:25:00+00:00",
-    "56.8",
+    "0.0",
     null,
     "2026-01-15T05:29:00+00:00"
    ],
    [
     "2026-01-15T05:30:00+00:00",
-    "55.6",
+    "0.0",
     null,
     "2026-01-15T05:34:00+00:00"
    ],
    [
     "2026-01-15T05:35:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T05:39:00+00:00"
    ],
    [
     "2026-01-15T05:40:00+00:00",
-    "53.4",
+    "0.0",
     null,
     "2026-01-15T05:44:00+00:00"
    ],
    [
     "2026-01-15T05:45:00+00:00",
-    "52.3",
+    "0.0",
     null,
     "2026-01-15T05:49:00+00:00"
    ],
    [
     "2026-01-15T05:50:00+00:00",
-    "51.2",
+    "0.0",
     null,
     "2026-01-15T05:54:00+00:00"
    ],
    [
     "2026-01-15T05:55:00+00:00",
-    "50.0",
+    "0.0",
     null,
     "2026-01-15T05:59:00+00:00"
    ],
    [
     "2026-01-15T06:00:00+00:00",
-    "48.9",
+    "0.0",
     null,
     "2026-01-15T06:04:00+00:00"
    ],
    [
     "2026-01-15T06:05:00+00:00",
-    "47.8",
+    "0.0",
     null,
     "2026-01-15T06:09:00+00:00"
    ],
    [
     "2026-01-15T06:10:00+00:00",
-    "46.7",
+    "0.0",
     null,
     "2026-01-15T06:14:00+00:00"
    ],
    [
     "2026-01-15T06:15:00+00:00",
-    "46.7",
+    "0.0",
     null,
     "2026-01-15T06:19:00+00:00"
    ],
    [
     "2026-01-15T06:20:00+00:00",
-    "46.6",
+    "0.0",
     null,
     "2026-01-15T06:24:00+00:00"
    ],
    [
     "2026-01-15T06:25:00+00:00",
-    "46.6",
+    "0.0",
     null,
     "2026-01-15T06:29:00+00:00"
    ],
    [
     "2026-01-15T06:30:00+00:00",
-    "46.6",
+    "0.0",
     null,
     "2026-01-15T06:34:00+00:00"
    ],
    [
     "2026-01-15T06:35:00+00:00",
-    "46.6",
+    "0.0",
     null,
     "2026-01-15T06:39:00+00:00"
    ],
    [
     "2026-01-15T06:40:00+00:00",
-    "46.6",
+    "0.0",
     null,
     "2026-01-15T06:44:00+00:00"
    ],
    [
     "2026-01-15T06:45:00+00:00",
-    "46.5",
+    "0.0",
     null,
     "2026-01-15T06:49:00+00:00"
    ],
    [
     "2026-01-15T06:50:00+00:00",
-    "46.5",
+    "0.0",
     null,
     "2026-01-15T06:54:00+00:00"
    ],
    [
     "2026-01-15T06:55:00+00:00",
-    "46.5",
+    "0.0",
     null,
     "2026-01-15T06:59:00+00:00"
    ],
    [
     "2026-01-15T07:00:00+00:00",
-    "46.5",
+    "0.0",
     null,
     "2026-01-15T07:04:00+00:00"
    ],
    [
     "2026-01-15T07:05:00+00:00",
-    "46.5",
+    "0.0",
     null,
     "2026-01-15T07:09:00+00:00"
    ],
    [
     "2026-01-15T07:10:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T07:14:00+00:00"
    ],
    [
     "2026-01-15T07:15:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T07:19:00+00:00"
    ],
    [
     "2026-01-15T07:20:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T07:24:00+00:00"
    ],
    [
     "2026-01-15T07:25:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T07:29:00+00:00"
    ],
    [
     "2026-01-15T07:30:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T07:34:00+00:00"
    ],
    [
     "2026-01-15T07:35:00+00:00",
-    "46.3",
+    "0.0",
     null,
     "2026-01-15T07:39:00+00:00"
    ],
    [
     "2026-01-15T07:40:00+00:00",
-    "46.3",
+    "0.0",
     null,
     "2026-01-15T07:44:00+00:00"
    ],
    [
     "2026-01-15T07:45:00+00:00",
-    "46.3",
+    "0.0",
     null,
     "2026-01-15T07:49:00+00:00"
    ],
    [
     "2026-01-15T07:50:00+00:00",
-    "46.3",
+    "0.0",
     null,
     "2026-01-15T07:54:00+00:00"
    ],
    [
     "2026-01-15T07:55:00+00:00",
-    "46.3",
+    "0.0",
     null,
     "2026-01-15T07:59:00+00:00"
    ],
    [
     "2026-01-15T08:00:00+00:00",
-    "46.2",
+    "0.0",
     null,
     "2026-01-15T08:04:00+00:00"
    ],
    [
     "2026-01-15T08:05:00+00:00",
-    "46.2",
+    "0.0",
     null,
     "2026-01-15T08:09:00+00:00"
    ],
    [
     "2026-01-15T08:10:00+00:00",
-    "46.2",
+    "0.0",
     null,
     "2026-01-15T08:14:00+00:00"
    ],
    [
     "2026-01-15T08:15:00+00:00",
-    "46.2",
+    "0.0",
     null,
     "2026-01-15T08:19:00+00:00"
    ],
    [
     "2026-01-15T08:20:00+00:00",
-    "46.2",
+    "0.0",
     null,
     "2026-01-15T08:24:00+00:00"
    ],
    [
     "2026-01-15T08:25:00+00:00",
-    "46.1",
+    "0.0",
     null,
     "2026-01-15T08:29:00+00:00"
    ],
    [
     "2026-01-15T08:30:00+00:00",
-    "46.1",
+    "0.0",
     null,
     "2026-01-15T08:34:00+00:00"
    ],
    [
     "2026-01-15T08:35:00+00:00",
-    "46.1",
+    "0.0",
     null,
     "2026-01-15T08:39:00+00:00"
    ],
    [
     "2026-01-15T08:40:00+00:00",
-    "46.1",
+    "0.0",
     null,
     "2026-01-15T08:44:00+00:00"
    ],
    [
     "2026-01-15T08:45:00+00:00",
-    "46.1",
+    "0.0",
     null,
     "2026-01-15T08:49:00+00:00"
    ],
    [
     "2026-01-15T08:50:00+00:00",
-    "46.0",
+    "0.0",
     null,
     "2026-01-15T08:54:00+00:00"
    ],
    [
     "2026-01-15T08:55:00+00:00",
-    "46.0",
+    "0.0",
     null,
     "2026-01-15T08:59:00+00:00"
    ],
    [
     "2026-01-15T09:00:00+00:00",
-    "46.0",
+    "0.0",
     null,
     "2026-01-15T09:04:00+00:00"
    ],
    [
     "2026-01-15T09:05:00+00:00",
-    "46.0",
+    "0.0",
     null,
     "2026-01-15T09:09:00+00:00"
    ],
    [
     "2026-01-15T09:10:00+00:00",
-    "46.0",
+    "0.0",
     null,
     "2026-01-15T09:14:00+00:00"
    ],
    [
     "2026-01-15T09:15:00+00:00",
-    "45.9",
+    "0.0",
     null,
     "2026-01-15T09:19:00+00:00"
    ],
    [
     "2026-01-15T09:20:00+00:00",
-    "45.9",
+    "0.0",
     null,
     "2026-01-15T09:24:00+00:00"
    ],
    [
     "2026-01-15T09:25:00+00:00",
-    "45.9",
+    "0.0",
     null,
     "2026-01-15T09:29:00+00:00"
    ],
    [
     "2026-01-15T09:30:00+00:00",
-    "45.9",
+    "0.0",
     null,
     "2026-01-15T09:34:00+00:00"
    ],
    [
     "2026-01-15T09:35:00+00:00",
-    "45.9",
+    "0.0",
     null,
     "2026-01-15T09:39:00+00:00"
    ],
    [
     "2026-01-15T09:40:00+00:00",
-    "45.8",
+    "0.0",
     null,
     "2026-01-15T09:44:00+00:00"
    ],
    [
     "2026-01-15T09:45:00+00:00",
-    "45.8",
+    "0.0",
     null,
     "2026-01-15T09:49:00+00:00"
    ],
    [
     "2026-01-15T09:50:00+00:00",
-    "45.8",
+    "0.0",
     null,
     "2026-01-15T09:54:00+00:00"
    ],
    [
     "2026-01-15T09:55:00+00:00",
-    "45.8",
+    "0.0",
     null,
     "2026-01-15T09:59:00+00:00"
    ],
    [
     "2026-01-15T10:00:00+00:00",
-    "45.8",
+    "0.0",
     null,
     "2026-01-15T10:04:00+00:00"
    ],
    [
     "2026-01-15T10:05:00+00:00",
-    "45.7",
+    "0.0",
     null,
     "2026-01-15T10:09:00+00:00"
    ],
    [
     "2026-01-15T10:10:00+00:00",
-    "45.7",
+    "0.0",
     null,
     "2026-01-15T10:14:00+00:00"
    ],
    [
     "2026-01-15T10:15:00+00:00",
-    "45.7",
+    "0.0",
     null,
     "2026-01-15T10:19:00+00:00"
    ],
    [
     "2026-01-15T10:20:00+00:00",
-    "45.7",
+    "0.0",
     null,
     "2026-01-15T10:24:00+00:00"
    ],
    [
     "2026-01-15T10:25:00+00:00",
-    "45.7",
+    "0.0",
     null,
     "2026-01-15T10:29:00+00:00"
    ],
    [
     "2026-01-15T10:30:00+00:00",
-    "45.6",
+    "0.0",
     null,
     "2026-01-15T10:34:00+00:00"
    ],
    [
     "2026-01-15T10:35:00+00:00",
-    "45.6",
+    "0.0",
     null,
     "2026-01-15T10:39:00+00:00"
    ],
    [
     "2026-01-15T10:40:00+00:00",
-    "45.6",
+    "0.0",
     null,
     "2026-01-15T10:44:00+00:00"
    ],
    [
     "2026-01-15T10:45:00+00:00",
-    "45.6",
+    "0.0",
     null,
     "2026-01-15T10:49:00+00:00"
    ],
    [
     "2026-01-15T10:50:00+00:00",
-    "45.6",
+    "0.0",
     null,
     "2026-01-15T10:54:00+00:00"
    ],
    [
     "2026-01-15T10:55:00+00:00",
-    "45.5",
+    "0.0",
     null,
     "2026-01-15T10:59:00+00:00"
    ],
    [
     "2026-01-15T11:00:00+00:00",
-    "45.5",
+    "0.0",
     null,
     "2026-01-15T11:04:00+00:00"
    ],
    [
     "2026-01-15T11:05:00+00:00",
-    "45.5",
+    "0.0",
     null,
     "2026-01-15T11:09:00+00:00"
    ],
    [
     "2026-01-15T11:10:00+00:00",
-    "45.5",
+    "0.0",
     null,
     "2026-01-15T11:14:00+00:00"
    ],
    [
     "2026-01-15T11:15:00+00:00",
-    "45.5",
+    "0.0",
     null,
     "2026-01-15T11:19:00+00:00"
    ],
    [
     "2026-01-15T11:20:00+00:00",
-    "45.4",
+    "0.0",
     null,
     "2026-01-15T11:24:00+00:00"
    ],
    [
     "2026-01-15T11:25:00+00:00",
-    "45.4",
+    "0.0",
     null,
     "2026-01-15T11:29:00+00:00"
    ],
    [
     "2026-01-15T11:30:00+00:00",
-    "45.4",
+    "0.0",
     null,
     "2026-01-15T11:34:00+00:00"
    ],
    [
     "2026-01-15T11:35:00+00:00",
-    "45.4",
+    "0.0",
     null,
     "2026-01-15T11:39:00+00:00"
    ],
    [
     "2026-01-15T11:40:00+00:00",
-    "45.4",
+    "0.0",
     null,
     "2026-01-15T11:44:00+00:00"
    ],
    [
     "2026-01-15T11:45:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T11:49:00+00:00"
    ],
    [
     "2026-01-15T11:50:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T11:54:00+00:00"
    ],
    [
     "2026-01-15T11:55:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T11:59:00+00:00"
    ],
    [
     "2026-01-15T12:00:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T12:04:00+00:00"
    ],
    [
     "2026-01-15T12:05:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T12:09:00+00:00"
    ],
    [
     "2026-01-15T12:10:00+00:00",
-    "45.2",
+    "0.0",
     null,
     "2026-01-15T12:14:00+00:00"
    ],
    [
     "2026-01-15T12:15:00+00:00",
-    "45.2",
+    "0.0",
     null,
     "2026-01-15T12:19:00+00:00"
    ],
    [
     "2026-01-15T12:20:00+00:00",
-    "45.2",
+    "0.0",
     null,
     "2026-01-15T12:24:00+00:00"
    ],
    [
     "2026-01-15T12:25:00+00:00",
-    "45.2",
+    "0.0",
     null,
     "2026-01-15T12:29:00+00:00"
    ],
    [
     "2026-01-15T12:30:00+00:00",
-    "45.2",
+    "0.0",
     null,
     "2026-01-15T12:34:00+00:00"
    ],
    [
     "2026-01-15T12:35:00+00:00",
-    "45.1",
+    "0.0",
     null,
     "2026-01-15T12:39:00+00:00"
    ],
    [
     "2026-01-15T12:40:00+00:00",
-    "45.1",
+    "0.0",
     null,
     "2026-01-15T12:44:00+00:00"
    ],
    [
     "2026-01-15T12:45:00+00:00",
-    "45.1",
+    "0.0",
     null,
     "2026-01-15T12:49:00+00:00"
    ],
    [
     "2026-01-15T12:50:00+00:00",
-    "45.1",
+    "0.0",
     null,
     "2026-01-15T12:54:00+00:00"
    ],
    [
     "2026-01-15T12:55:00+00:00",
-    "45.1",
+    "0.0",
     null,
     "2026-01-15T12:59:00+00:00"
    ],
    [
     "2026-01-15T13:00:00+00:00",
-    "45.0",
+    "0.0",
     null,
     "2026-01-15T13:04:00+00:00"
    ],
    [
     "2026-01-15T13:05:00+00:00",
-    "45.0",
+    "0.0",
     null,
     "2026-01-15T13:09:00+00:00"
    ],
    [
     "2026-01-15T13:10:00+00:00",
-    "45.0",
+    "0.0",
     null,
     "2026-01-15T13:14:00+00:00"
    ],
    [
     "2026-01-15T13:15:00+00:00",
-    "45.0",
+    "0.0",
     null,
     "2026-01-15T13:19:00+00:00"
    ],
    [
     "2026-01-15T13:20:00+00:00",
-    "45.0",
+    "0.0",
     null,
     "2026-01-15T13:24:00+00:00"
    ],
    [
     "2026-01-15T13:25:00+00:00",
-    "44.9",
+    "0.0",
     null,
     "2026-01-15T13:29:00+00:00"
    ],
    [
     "2026-01-15T13:30:00+00:00",
-    "44.9",
+    "0.0",
     null,
     "2026-01-15T13:34:00+00:00"
    ],
    [
     "2026-01-15T13:35:00+00:00",
-    "44.9",
+    "0.0",
     null,
     "2026-01-15T13:39:00+00:00"
    ],
    [
     "2026-01-15T13:40:00+00:00",
-    "44.9",
+    "0.0",
     null,
     "2026-01-15T13:44:00+00:00"
    ],
    [
     "2026-01-15T13:45:00+00:00",
-    "44.9",
+    "0.0",
     null,
     "2026-01-15T13:49:00+00:00"
    ],
    [
     "2026-01-15T13:50:00+00:00",
-    "44.8",
+    "0.0",
     null,
     "2026-01-15T13:54:00+00:00"
    ],
    [
     "2026-01-15T13:55:00+00:00",
-    "44.8",
+    "0.0",
     null,
     "2026-01-15T13:59:00+00:00"
    ],
    [
     "2026-01-15T14:00:00+00:00",
-    "44.8",
+    "0.0",
     null,
     "2026-01-15T14:04:00+00:00"
    ],
    [
     "2026-01-15T14:05:00+00:00",
-    "44.8",
+    "0.0",
     null,
     "2026-01-15T14:09:00+00:00"
    ],
    [
     "2026-01-15T14:10:00+00:00",
-    "44.8",
+    "0.0",
     null,
     "2026-01-15T14:14:00+00:00"
    ],
    [
     "2026-01-15T14:15:00+00:00",
-    "44.7",
+    "0.0",
     null,
     "2026-01-15T14:19:00+00:00"
    ],
    [
     "2026-01-15T14:20:00+00:00",
-    "44.7",
+    "0.0",
     null,
     "2026-01-15T14:24:00+00:00"
    ],
    [
     "2026-01-15T14:25:00+00:00",
-    "44.7",
+    "0.0",
     null,
     "2026-01-15T14:29:00+00:00"
    ],
    [
     "2026-01-15T14:30:00+00:00",
-    "45.2",
+    "1.83",
     null,
     "2026-01-15T14:34:00+00:00"
    ],
    [
     "2026-01-15T14:35:00+00:00",
-    "45.8",
+    "1.83",
     null,
     "2026-01-15T14:39:00+00:00"
    ],
    [
     "2026-01-15T14:40:00+00:00",
-    "46.3",
+    "1.83",
     null,
     "2026-01-15T14:44:00+00:00"
    ],
    [
     "2026-01-15T14:45:00+00:00",
-    "46.9",
+    "1.83",
     null,
     "2026-01-15T14:49:00+00:00"
    ],
    [
     "2026-01-15T14:50:00+00:00",
-    "47.4",
+    "1.83",
     null,
     "2026-01-15T14:54:00+00:00"
    ],
    [
     "2026-01-15T14:55:00+00:00",
-    "48.0",
+    "1.83",
     null,
     "2026-01-15T14:59:00+00:00"
    ],
    [
     "2026-01-15T15:00:00+00:00",
-    "48.5",
+    "1.83",
     null,
     "2026-01-15T15:04:00+00:00"
    ],
    [
     "2026-01-15T15:05:00+00:00",
-    "49.1",
+    "1.83",
     null,
     "2026-01-15T15:09:00+00:00"
    ],
    [
     "2026-01-15T15:10:00+00:00",
-    "49.6",
+    "1.83",
     null,
     "2026-01-15T15:14:00+00:00"
    ],
    [
     "2026-01-15T15:15:00+00:00",
-    "50.2",
+    "1.83",
     null,
     "2026-01-15T15:19:00+00:00"
    ],
    [
     "2026-01-15T15:20:00+00:00",
-    "50.7",
+    "1.83",
     null,
     "2026-01-15T15:24:00+00:00"
    ],
    [
     "2026-01-15T15:25:00+00:00",
-    "51.3",
+    "1.83",
     null,
     "2026-01-15T15:29:00+00:00"
    ],
    [
     "2026-01-15T15:30:00+00:00",
-    "51.8",
+    "1.83",
     null,
     "2026-01-15T15:34:00+00:00"
    ],
    [
     "2026-01-15T15:35:00+00:00",
-    "52.4",
+    "1.83",
     null,
     "2026-01-15T15:39:00+00:00"
    ],
    [
     "2026-01-15T15:40:00+00:00",
-    "52.9",
+    "1.83",
     null,
     "2026-01-15T15:44:00+00:00"
    ],
    [
     "2026-01-15T15:45:00+00:00",
-    "53.5",
+    "1.83",
     null,
     "2026-01-15T15:49:00+00:00"
    ],
    [
     "2026-01-15T15:50:00+00:00",
-    "54.0",
+    "1.83",
     null,
     "2026-01-15T15:54:00+00:00"
    ],
    [
     "2026-01-15T15:55:00+00:00",
-    "54.6",
+    "1.83",
     null,
     "2026-01-15T15:59:00+00:00"
    ],
    [
     "2026-01-15T16:00:00+00:00",
-    "54.6",
+    "0.0",
     null,
     "2026-01-15T16:04:00+00:00"
    ],
    [
     "2026-01-15T16:05:00+00:00",
-    "54.6",
+    "0.0",
     null,
     "2026-01-15T16:09:00+00:00"
    ],
    [
     "2026-01-15T16:10:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T16:14:00+00:00"
    ],
    [
     "2026-01-15T16:15:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T16:19:00+00:00"
    ],
    [
     "2026-01-15T16:20:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T16:24:00+00:00"
    ],
    [
     "2026-01-15T16:25:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T16:29:00+00:00"
    ],
    [
     "2026-01-15T16:30:00+00:00",
-    "54.5",
+    "0.0",
     null,
     "2026-01-15T16:34:00+00:00"
    ],
    [
     "2026-01-15T16:35:00+00:00",
-    "54.4",
+    "0.0",
     null,
     "2026-01-15T16:39:00+00:00"
    ],
    [
     "2026-01-15T16:40:00+00:00",
-    "54.4",
+    "0.0",
     null,
     "2026-01-15T16:44:00+00:00"
    ],
    [
     "2026-01-15T16:45:00+00:00",
-    "54.4",
+    "0.0",
     null,
     "2026-01-15T16:49:00+00:00"
    ],
    [
     "2026-01-15T16:50:00+00:00",
-    "54.4",
+    "0.0",
     null,
     "2026-01-15T16:54:00+00:00"
    ],
    [
     "2026-01-15T16:55:00+00:00",
-    "54.4",
+    "0.0",
     null,
     "2026-01-15T16:59:00+00:00"
    ],
    [
     "2026-01-15T17:00:00+00:00",
-    "54.3",
+    "0.0",
     null,
     "2026-01-15T17:04:00+00:00"
    ],
    [
     "2026-01-15T17:05:00+00:00",
-    "54.3",
+    "0.0",
     null,
     "2026-01-15T17:09:00+00:00"
    ],
    [
     "2026-01-15T17:10:00+00:00",
-    "54.3",
+    "0.0",
     null,
     "2026-01-15T17:14:00+00:00"
    ],
    [
     "2026-01-15T17:15:00+00:00",
-    "54.3",
+    "0.0",
     null,
     "2026-01-15T17:19:00+00:00"
    ],
    [
     "2026-01-15T17:20:00+00:00",
-    "54.3",
+    "0.0",
     null,
     "2026-01-15T17:24:00+00:00"
    ],
    [
     "2026-01-15T17:25:00+00:00",
-    "54.2",
+    "0.0",
     null,
     "2026-01-15T17:29:00+00:00"
    ],
    [
     "2026-01-15T17:30:00+00:00",
-    "53.1",
+    "0.0",
     null,
     "2026-01-15T17:34:00+00:00"
    ],
    [
     "2026-01-15T17:35:00+00:00",
-    "52.0",
+    "0.0",
     null,
     "2026-01-15T17:39:00+00:00"
    ],
    [
     "2026-01-15T17:40:00+00:00",
-    "50.9",
+    "0.0",
     null,
     "2026-01-15T17:44:00+00:00"
    ],
    [
     "2026-01-15T17:45:00+00:00",
-    "49.8",
+    "0.0",
     null,
     "2026-01-15T17:49:00+00:00"
    ],
    [
     "2026-01-15T17:50:00+00:00",
-    "48.6",
+    "0.0",
     null,
     "2026-01-15T17:54:00+00:00"
    ],
    [
     "2026-01-15T17:55:00+00:00",
-    "47.5",
+    "0.0",
     null,
     "2026-01-15T17:59:00+00:00"
    ],
    [
     "2026-01-15T18:00:00+00:00",
-    "46.4",
+    "0.0",
     null,
     "2026-01-15T18:04:00+00:00"
    ],
    [
     "2026-01-15T18:05:00+00:00",
-    "45.3",
+    "0.0",
     null,
     "2026-01-15T18:09:00+00:00"
    ],
    [
     "2026-01-15T18:10:00+00:00",
-    "44.2",
+    "0.0",
     null,
     "2026-01-15T18:14:00+00:00"
    ],
    [
     "2026-01-15T18:15:00+00:00",
-    "43.0",
+    "0.0",
     null,
     "2026-01-15T18:19:00+00:00"
    ],
    [
     "2026-01-15T18:20:00+00:00",
-    "41.9",
+    "0.0",
     null,
     "2026-01-15T18:24:00+00:00"
    ],
    [
     "2026-01-15T18:25:00+00:00",
-    "40.8",
+    "0.0",
     null,
     "2026-01-15T18:29:00+00:00"
    ],
    [
     "2026-01-15T18:30:00+00:00",
-    "40.8",
+    "0.0",
     null,
     "2026-01-15T18:34:00+00:00"
    ],
    [
     "2026-01-15T18:35:00+00:00",
-    "40.8",
+    "0.0",
     null,
     "2026-01-15T18:39:00+00:00"
    ],
    [
     "2026-01-15T18:40:00+00:00",
-    "40.7",
+    "0.0",
     null,
     "2026-01-15T18:44:00+00:00"
    ],
    [
     "2026-01-15T18:45:00+00:00",
-    "40.7",
+    "0.0",
     null,
     "2026-01-15T18:49:00+00:00"
    ],
    [
     "2026-01-15T18:50:00+00:00",
-    "40.7",
+    "0.0",
     null,
     "2026-01-15T18:54:00+00:00"
    ],
    [
     "2026-01-15T18:55:00+00:00",
-    "40.7",
+    "0.0",
     null,
     "2026-01-15T18:59:00+00:00"
    ],
    [
     "2026-01-15T19:00:00+00:00",
-    "40.7",
+    "0.0",
     null,
     "2026-01-15T19:04:00+00:00"
    ],
    [
     "2026-01-15T19:05:00+00:00",
-    "40.6",
+    "0.0",
     null,
     "2026-01-15T19:09:00+00:00"
    ],
    [
     "2026-01-15T19:10:00+00:00",
-    "40.6",
+    "0.0",
     null,
     "2026-01-15T19:14:00+00:00"
    ],
    [
     "2026-01-15T19:15:00+00:00",
-    "40.6",
+    "0.0",
     null,
     "2026-01-15T19:19:00+00:00"
    ],
    [
     "2026-01-15T19:20:00+00:00",
-    "40.6",
+    "0.0",
     null,
     "2026-01-15T19:24:00+00:00"
    ],
    [
     "2026-01-15T19:25:00+00:00",
-    "40.6",
+    "0.0",
     null,
     "2026-01-15T19:29:00+00:00"
    ],
    [
     "2026-01-15T19:30:00+00:00",
-    "40.5",
+    "0.0",
     null,
     "2026-01-15T19:34:00+00:00"
    ],
    [
     "2026-01-15T19:35:00+00:00",
-    "40.5",
+    "0.0",
     null,
     "2026-01-15T19:39:00+00:00"
    ],
    [
     "2026-01-15T19:40:00+00:00",
-    "40.5",
+    "0.0",
     null,
     "2026-01-15T19:44:00+00:00"
    ],
    [
     "2026-01-15T19:45:00+00:00",
-    "40.5",
+    "0.0",
     null,
     "2026-01-15T19:49:00+00:00"
    ],
    [
     "2026-01-15T19:50:00+00:00",
-    "40.5",
+    "0.0",
     null,
     "2026-01-15T19:54:00+00:00"
    ],
    [
     "2026-01-15T19:55:00+00:00",
-    "40.4",
+    "0.0",
     null,
     "2026-01-15T19:59:00+00:00"
    ],
    [
     "2026-01-15T20:00:00+00:00",
-    "40.4",
+    "0.0",
     null,
     "2026-01-15T20:04:00+00:00"
    ],
    [
     "2026-01-15T20:05:00+00:00",
-    "40.4",
+    "0.0",
     null,
     "2026-01-15T20:09:00+00:00"
    ],
    [
     "2026-01-15T20:10:00+00:00",
-    "40.4",
+    "0.0",
     null,
     "2026-01-15T20:14:00+00:00"
    ],
    [
     "2026-01-15T20:15:00+00:00",
-    "40.4",
+    "0.0",
     null,
     "2026-01-15T20:19:00+00:00"
    ],
    [
     "2026-01-15T20:20:00+00:00",
-    "40.3",
+    "0.0",
     null,
     "2026-01-15T20:24:00+00:00"
    ],
    [
     "2026-01-15T20:25:00+00:00",
-    "40.3",
+    "0.0",
     null,
     "2026-01-15T20:29:00+00:00"
    ],
    [
     "2026-01-15T20:30:00+00:00",
-    "40.3",
+    "0.0",
     null,
     "2026-01-15T20:34:00+00:00"
    ],
    [
     "2026-01-15T20:35:00+00:00",
-    "40.3",
+    "0.0",
     null,
     "2026-01-15T20:39:00+00:00"
    ],
    [
     "2026-01-15T20:40:00+00:00",
-    "40.3",
+    "0.0",
     null,
     "2026-01-15T20:44:00+00:00"
    ],
    [
     "2026-01-15T20:45:00+00:00",
-    "40.2",
+    "0.0",
     null,
     "2026-01-15T20:49:00+00:00"
    ],
    [
     "2026-01-15T20:50:00+00:00",
-    "40.2",
+    "0.0",
     null,
     "2026-01-15T20:54:00+00:00"
    ],
    [
     "2026-01-15T20:55:00+00:00",
-    "40.2",
+    "0.0",
     null,
     "2026-01-15T20:59:00+00:00"
    ],
    [
     "2026-01-15T21:00:00+00:00",
-    "40.2",
+    "0.0",
     null,
     "2026-01-15T21:04:00+00:00"
    ],
    [
     "2026-01-15T21:05:00+00:00",
-    "40.2",
+    "0.0",
     null,
     "2026-01-15T21:09:00+00:00"
    ],
    [
     "2026-01-15T21:10:00+00:00",
-    "40.1",
+    "0.0",
     null,
     "2026-01-15T21:14:00+00:00"
    ],
    [
     "2026-01-15T21:15:00+00:00",
-    "40.1",
+    "0.0",
     null,
     "2026-01-15T21:19:00+00:00"
    ],
    [
     "2026-01-15T21:20:00+00:00",
-    "40.1",
+    "0.0",
     null,
     "2026-01-15T21:24:00+00:00"
    ],
    [
     "2026-01-15T21:25:00+00:00",
-    "40.1",
+    "0.0",
     null,
     "2026-01-15T21:29:00+00:00"
    ],
    [
     "2026-01-15T21:30:00+00:00",
-    "40.1",
+    "0.0",
     null,
     "2026-01-15T21:34:00+00:00"
    ],
    [
     "2026-01-15T21:35:00+00:00",
-    "40.0",
+    "0.0",
     null,
     "2026-01-15T21:39:00+00:00"
    ],
    [
     "2026-01-15T21:40:00+00:00",
-    "40.0",
+    "0.0",
     null,
     "2026-01-15T21:44:00+00:00"
    ],
    [
     "2026-01-15T21:45:00+00:00",
-    "40.0",
+    "0.0",
     null,
     "2026-01-15T21:49:00+00:00"
    ],
    [
     "2026-01-15T21:50:00+00:00",
-    "40.0",
+    "0.0",
     null,
     "2026-01-15T21:54:00+00:00"
    ],
    [
     "2026-01-15T21:55:00+00:00",
-    "40.0",
+    "0.0",
     null,
     "2026-01-15T21:59:00+00:00"
    ],
    [
     "2026-01-15T22:00:00+00:00",
-    "39.9",
+    "0.0",
     null,
     "2026-01-15T22:04:00+00:00"
    ],
    [
     "2026-01-15T22:05:00+00:00",
-    "39.9",
+    "0.0",
     null,
     "2026-01-15T22:09:00+00:00"
    ],
    [
     "2026-01-15T22:10:00+00:00",
-    "39.9",
+    "0.0",
     null,
     "2026-01-15T22:14:00+00:00"
    ],
    [
     "2026-01-15T22:15:00+00:00",
-    "39.9",
+    "0.0",
     null,
     "2026-01-15T22:19:00+00:00"
    ],
    [
     "2026-01-15T22:20:00+00:00",
-    "39.9",
+    "0.0",
     null,
     "2026-01-15T22:24:00+00:00"
    ],
    [
     "2026-01-15T22:25:00+00:00",
-    "39.8",
+    "0.0",
     null,
     "2026-01-15T22:29:00+00:00"
    ],
    [
     "2026-01-15T22:30:00+00:00",
-    "39.8",
+    "0.0",
     null,
     "2026-01-15T22:34:00+00:00"
    ],
    [
     "2026-01-15T22:35:00+00:00",
-    "39.8",
+    "0.0",
     null,
     "2026-01-15T22:39:00+00:00"
    ],
    [
     "2026-01-15T22:40:00+00:00",
-    "39.8",
+    "0.0",
     null,
     "2026-01-15T22:44:00+00:00"
    ],
    [
     "2026-01-15T22:45:00+00:00",
-    "39.8",
+    "0.0",
     null,
     "2026-01-15T22:49:00+00:00"
    ],
    [
     "2026-01-15T22:50:00+00:00",
-    "39.7",
+    "0.0",
     null,
     "2026-01-15T22:54:00+00:00"
    ],
    [
     "2026-01-15T22:55:00+00:00",
-    "39.7",
+    "0.0",
     null,
     "2026-01-15T22:59:00+00:00"
    ]
   ],
-  "sensor.living_room_temperature": [
+  "sensor.indoor_temp": [
    [
     "2026-01-14T22:50:00+00:00",
     "20.86",
@@ -5009,860 +5009,88 @@
     "2026-01-15T22:59:00+00:00"
    ]
   ],
-  "sensor.nordpool_kwh_se3_sek": [
+  "sensor.outdoor_temp": [
    [
-    "2026-01-14T22:00:00+00:00",
-    "0.4019",
+    "2026-01-14T22:50:00+00:00",
+    "-7.1",
     {
-     "currency": "SEK",
-     "raw_today": [
-      {
-       "end": "2026-01-14T01:00:00+01:00",
-       "start": "2026-01-14T00:00:00+01:00",
-       "value": 0.42
-      },
-      {
-       "end": "2026-01-14T02:00:00+01:00",
-       "start": "2026-01-14T01:00:00+01:00",
-       "value": 0.4452
-      },
-      {
-       "end": "2026-01-14T03:00:00+01:00",
-       "start": "2026-01-14T02:00:00+01:00",
-       "value": 0.4474
-      },
-      {
-       "end": "2026-01-14T04:00:00+01:00",
-       "start": "2026-01-14T03:00:00+01:00",
-       "value": 0.426
-      },
-      {
-       "end": "2026-01-14T05:00:00+01:00",
-       "start": "2026-01-14T04:00:00+01:00",
-       "value": 0.4138
-      },
-      {
-       "end": "2026-01-14T06:00:00+01:00",
-       "start": "2026-01-14T05:00:00+01:00",
-       "value": 0.4861
-      },
-      {
-       "end": "2026-01-14T07:00:00+01:00",
-       "start": "2026-01-14T06:00:00+01:00",
-       "value": 0.7427
-      },
-      {
-       "end": "2026-01-14T08:00:00+01:00",
-       "start": "2026-01-14T07:00:00+01:00",
-       "value": 1.1406
-      },
-      {
-       "end": "2026-01-14T09:00:00+01:00",
-       "start": "2026-01-14T08:00:00+01:00",
-       "value": 1.3497
-      },
-      {
-       "end": "2026-01-14T10:00:00+01:00",
-       "start": "2026-01-14T09:00:00+01:00",
-       "value": 1.1333
-      },
-      {
-       "end": "2026-01-14T11:00:00+01:00",
-       "start": "2026-01-14T10:00:00+01:00",
-       "value": 0.7348
-      },
-      {
-       "end": "2026-01-14T12:00:00+01:00",
-       "start": "2026-01-14T11:00:00+01:00",
-       "value": 0.4849
-      },
-      {
-       "end": "2026-01-14T13:00:00+01:00",
-       "start": "2026-01-14T12:00:00+01:00",
-       "value": 0.4212
-      },
-      {
-       "end": "2026-01-14T14:00:00+01:00",
-       "start": "2026-01-14T13:00:00+01:00",
-       "value": 0.4416
-      },
-      {
-       "end": "2026-01-14T15:00:00+01:00",
-       "start": "2026-01-14T14:00:00+01:00",
-       "value": 0.4939
-      },
-      {
-       "end": "2026-01-14T16:00:00+01:00",
-       "start": "2026-01-14T15:00:00+01:00",
-       "value": 0.618
-      },
-      {
-       "end": "2026-01-14T17:00:00+01:00",
-       "start": "2026-01-14T16:00:00+01:00",
-       "value": 0.8966
-      },
-      {
-       "end": "2026-01-14T18:00:00+01:00",
-       "start": "2026-01-14T17:00:00+01:00",
-       "value": 1.2754
-      },
-      {
-       "end": "2026-01-14T19:00:00+01:00",
-       "start": "2026-01-14T18:00:00+01:00",
-       "value": 1.4775
-      },
-      {
-       "end": "2026-01-14T20:00:00+01:00",
-       "start": "2026-01-14T19:00:00+01:00",
-       "value": 1.3087
-      },
-      {
-       "end": "2026-01-14T21:00:00+01:00",
-       "start": "2026-01-14T20:00:00+01:00",
-       "value": 0.9327
-      },
-      {
-       "end": "2026-01-14T22:00:00+01:00",
-       "start": "2026-01-14T21:00:00+01:00",
-       "value": 0.6236
-      },
-      {
-       "end": "2026-01-14T23:00:00+01:00",
-       "start": "2026-01-14T22:00:00+01:00",
-       "value": 0.4638
-      },
-      {
-       "end": "2026-01-15T00:00:00+01:00",
-       "start": "2026-01-14T23:00:00+01:00",
-       "value": 0.4019
-      }
-     ],
-     "raw_tomorrow": [
-      {
-       "end": "2026-01-16T01:00:00+01:00",
-       "start": "2026-01-16T00:00:00+01:00",
-       "value": 0.42
-      },
-      {
-       "end": "2026-01-16T02:00:00+01:00",
-       "start": "2026-01-16T01:00:00+01:00",
-       "value": 0.4452
-      },
-      {
-       "end": "2026-01-16T03:00:00+01:00",
-       "start": "2026-01-16T02:00:00+01:00",
-       "value": 0.4474
-      },
-      {
-       "end": "2026-01-16T04:00:00+01:00",
-       "start": "2026-01-16T03:00:00+01:00",
-       "value": 0.426
-      },
-      {
-       "end": "2026-01-16T05:00:00+01:00",
-       "start": "2026-01-16T04:00:00+01:00",
-       "value": 0.4138
-      },
-      {
-       "end": "2026-01-16T06:00:00+01:00",
-       "start": "2026-01-16T05:00:00+01:00",
-       "value": 0.4861
-      },
-      {
-       "end": "2026-01-16T07:00:00+01:00",
-       "start": "2026-01-16T06:00:00+01:00",
-       "value": 0.7427
-      },
-      {
-       "end": "2026-01-16T08:00:00+01:00",
-       "start": "2026-01-16T07:00:00+01:00",
-       "value": 1.1406
-      },
-      {
-       "end": "2026-01-16T09:00:00+01:00",
-       "start": "2026-01-16T08:00:00+01:00",
-       "value": 1.3497
-      },
-      {
-       "end": "2026-01-16T10:00:00+01:00",
-       "start": "2026-01-16T09:00:00+01:00",
-       "value": 1.1333
-      },
-      {
-       "end": "2026-01-16T11:00:00+01:00",
-       "start": "2026-01-16T10:00:00+01:00",
-       "value": 0.7348
-      },
-      {
-       "end": "2026-01-16T12:00:00+01:00",
-       "start": "2026-01-16T11:00:00+01:00",
-       "value": 0.4849
-      },
-      {
-       "end": "2026-01-16T13:00:00+01:00",
-       "start": "2026-01-16T12:00:00+01:00",
-       "value": 0.4212
-      },
-      {
-       "end": "2026-01-16T14:00:00+01:00",
-       "start": "2026-01-16T13:00:00+01:00",
-       "value": 0.4416
-      },
-      {
-       "end": "2026-01-16T15:00:00+01:00",
-       "start": "2026-01-16T14:00:00+01:00",
-       "value": 0.4939
-      },
-      {
-       "end": "2026-01-16T16:00:00+01:00",
-       "start": "2026-01-16T15:00:00+01:00",
-       "value": 0.618
-      },
-      {
-       "end": "2026-01-16T17:00:00+01:00",
-       "start": "2026-01-16T16:00:00+01:00",
-       "value": 0.8966
-      },
-      {
-       "end": "2026-01-16T18:00:00+01:00",
-       "start": "2026-01-16T17:00:00+01:00",
-       "value": 1.2754
-      },
-      {
-       "end": "2026-01-16T19:00:00+01:00",
-       "start": "2026-01-16T18:00:00+01:00",
-       "value": 1.4775
-      },
-      {
-       "end": "2026-01-16T20:00:00+01:00",
-       "start": "2026-01-16T19:00:00+01:00",
-       "value": 1.3087
-      },
-      {
-       "end": "2026-01-16T21:00:00+01:00",
-       "start": "2026-01-16T20:00:00+01:00",
-       "value": 0.9327
-      },
-      {
-       "end": "2026-01-16T22:00:00+01:00",
-       "start": "2026-01-16T21:00:00+01:00",
-       "value": 0.6236
-      },
-      {
-       "end": "2026-01-16T23:00:00+01:00",
-       "start": "2026-01-16T22:00:00+01:00",
-       "value": 0.4638
-      },
-      {
-       "end": "2026-01-17T00:00:00+01:00",
-       "start": "2026-01-16T23:00:00+01:00",
-       "value": 0.4019
-      }
-     ],
-     "unit_of_measurement": "SEK/kWh"
+     "device_class": "temperature",
+     "state_class": "measurement",
+     "unit_of_measurement": "\u00b0C"
     },
     "2026-01-14T22:59:00+00:00"
    ],
    [
     "2026-01-14T23:00:00+00:00",
-    "0.4200",
-    {
-     "currency": "SEK",
-     "raw_today": [
-      {
-       "end": "2026-01-15T01:00:00+01:00",
-       "start": "2026-01-15T00:00:00+01:00",
-       "value": 0.42
-      },
-      {
-       "end": "2026-01-15T02:00:00+01:00",
-       "start": "2026-01-15T01:00:00+01:00",
-       "value": 0.4452
-      },
-      {
-       "end": "2026-01-15T03:00:00+01:00",
-       "start": "2026-01-15T02:00:00+01:00",
-       "value": 0.4474
-      },
-      {
-       "end": "2026-01-15T04:00:00+01:00",
-       "start": "2026-01-15T03:00:00+01:00",
-       "value": 0.426
-      },
-      {
-       "end": "2026-01-15T05:00:00+01:00",
-       "start": "2026-01-15T04:00:00+01:00",
-       "value": 0.4138
-      },
-      {
-       "end": "2026-01-15T06:00:00+01:00",
-       "start": "2026-01-15T05:00:00+01:00",
-       "value": 0.4861
-      },
-      {
-       "end": "2026-01-15T07:00:00+01:00",
-       "start": "2026-01-15T06:00:00+01:00",
-       "value": 0.7427
-      },
-      {
-       "end": "2026-01-15T08:00:00+01:00",
-       "start": "2026-01-15T07:00:00+01:00",
-       "value": 1.1406
-      },
-      {
-       "end": "2026-01-15T09:00:00+01:00",
-       "start": "2026-01-15T08:00:00+01:00",
-       "value": 1.3497
-      },
-      {
-       "end": "2026-01-15T10:00:00+01:00",
-       "start": "2026-01-15T09:00:00+01:00",
-       "value": 1.1333
-      },
-      {
-       "end": "2026-01-15T11:00:00+01:00",
-       "start": "2026-01-15T10:00:00+01:00",
-       "value": 0.7348
-      },
-      {
-       "end": "2026-01-15T12:00:00+01:00",
-       "start": "2026-01-15T11:00:00+01:00",
-       "value": 0.4849
-      },
-      {
-       "end": "2026-01-15T13:00:00+01:00",
-       "start": "2026-01-15T12:00:00+01:00",
-       "value": 0.4212
-      },
-      {
-       "end": "2026-01-15T14:00:00+01:00",
-       "start": "2026-01-15T13:00:00+01:00",
-       "value": 0.4416
-      },
-      {
-       "end": "2026-01-15T15:00:00+01:00",
-       "start": "2026-01-15T14:00:00+01:00",
-       "value": 0.4939
-      },
-      {
-       "end": "2026-01-15T16:00:00+01:00",
-       "start": "2026-01-15T15:00:00+01:00",
-       "value": 0.618
-      },
-      {
-       "end": "2026-01-15T17:00:00+01:00",
-       "start": "2026-01-15T16:00:00+01:00",
-       "value": 0.8966
-      },
-      {
-       "end": "2026-01-15T18:00:00+01:00",
-       "start": "2026-01-15T17:00:00+01:00",
-       "value": 1.2754
-      },
-      {
-       "end": "2026-01-15T19:00:00+01:00",
-       "start": "2026-01-15T18:00:00+01:00",
-       "value": 1.4775
-      },
-      {
-       "end": "2026-01-15T20:00:00+01:00",
-       "start": "2026-01-15T19:00:00+01:00",
-       "value": 1.3087
-      },
-      {
-       "end": "2026-01-15T21:00:00+01:00",
-       "start": "2026-01-15T20:00:00+01:00",
-       "value": 0.9327
-      },
-      {
-       "end": "2026-01-15T22:00:00+01:00",
-       "start": "2026-01-15T21:00:00+01:00",
-       "value": 0.6236
-      },
-      {
-       "end": "2026-01-15T23:00:00+01:00",
-       "start": "2026-01-15T22:00:00+01:00",
-       "value": 0.4638
-      },
-      {
-       "end": "2026-01-16T00:00:00+01:00",
-       "start": "2026-01-15T23:00:00+01:00",
-       "value": 0.4019
-      }
-     ],
-     "raw_tomorrow": [],
-     "unit_of_measurement": "SEK/kWh"
-    },
-    "2026-01-14T23:59:00+00:00"
-   ],
-   [
-    "2026-01-15T00:00:00+00:00",
-    "0.4452",
+    "-7.2",
     null,
-    "2026-01-15T00:59:00+00:00"
+    "2026-01-14T23:09:00+00:00"
    ],
    [
-    "2026-01-15T01:00:00+00:00",
-    "0.4474",
+    "2026-01-14T23:10:00+00:00",
+    "-7.3",
     null,
-    "2026-01-15T01:59:00+00:00"
+    "2026-01-14T23:19:00+00:00"
    ],
    [
-    "2026-01-15T02:00:00+00:00",
-    "0.4260",
+    "2026-01-14T23:20:00+00:00",
+    "-7.4",
     null,
-    "2026-01-15T02:59:00+00:00"
+    "2026-01-14T23:29:00+00:00"
    ],
    [
-    "2026-01-15T03:00:00+00:00",
-    "0.4138",
+    "2026-01-14T23:30:00+00:00",
+    "-7.4",
     null,
-    "2026-01-15T03:59:00+00:00"
+    "2026-01-14T23:39:00+00:00"
    ],
    [
-    "2026-01-15T04:00:00+00:00",
-    "0.4861",
+    "2026-01-14T23:40:00+00:00",
+    "-7.5",
     null,
-    "2026-01-15T04:59:00+00:00"
+    "2026-01-14T23:49:00+00:00"
    ],
    [
-    "2026-01-15T05:00:00+00:00",
-    "0.7427",
+    "2026-01-14T23:50:00+00:00",
+    "-7.6",
     null,
-    "2026-01-15T05:59:00+00:00"
+    "2026-01-14T23:59:00+00:00"
    ],
    [
-    "2026-01-15T06:00:00+00:00",
-    "1.1406",
+    "2026-01-15T00:00:00+00:00",
+    "-7.6",
     null,
-    "2026-01-15T06:59:00+00:00"
+    "2026-01-15T00:09:00+00:00"
    ],
    [
-    "2026-01-15T07:00:00+00:00",
-    "1.3497",
+    "2026-01-15T00:10:00+00:00",
+    "-7.7",
     null,
-    "2026-01-15T07:59:00+00:00"
+    "2026-01-15T00:19:00+00:00"
    ],
    [
-    "2026-01-15T08:00:00+00:00",
-    "1.1333",
+    "2026-01-15T00:20:00+00:00",
+    "-7.7",
     null,
-    "2026-01-15T08:59:00+00:00"
+    "2026-01-15T00:29:00+00:00"
    ],
    [
-    "2026-01-15T09:00:00+00:00",
-    "0.7348",
+    "2026-01-15T00:30:00+00:00",
+    "-7.8",
     null,
-    "2026-01-15T09:59:00+00:00"
+    "2026-01-15T00:39:00+00:00"
    ],
    [
-    "2026-01-15T10:00:00+00:00",
-    "0.4849",
+    "2026-01-15T00:40:00+00:00",
+    "-7.8",
     null,
-    "2026-01-15T10:59:00+00:00"
+    "2026-01-15T00:49:00+00:00"
    ],
    [
-    "2026-01-15T11:00:00+00:00",
-    "0.4212",
+    "2026-01-15T00:50:00+00:00",
+    "-7.9",
     null,
-    "2026-01-15T11:59:00+00:00"
-   ],
-   [
-    "2026-01-15T12:00:00+00:00",
-    "0.4416",
-    {
-     "currency": "SEK",
-     "raw_today": [
-      {
-       "end": "2026-01-15T01:00:00+01:00",
-       "start": "2026-01-15T00:00:00+01:00",
-       "value": 0.42
-      },
-      {
-       "end": "2026-01-15T02:00:00+01:00",
-       "start": "2026-01-15T01:00:00+01:00",
-       "value": 0.4452
-      },
-      {
-       "end": "2026-01-15T03:00:00+01:00",
-       "start": "2026-01-15T02:00:00+01:00",
-       "value": 0.4474
-      },
-      {
-       "end": "2026-01-15T04:00:00+01:00",
-       "start": "2026-01-15T03:00:00+01:00",
-       "value": 0.426
-      },
-      {
-       "end": "2026-01-15T05:00:00+01:00",
-       "start": "2026-01-15T04:00:00+01:00",
-       "value": 0.4138
-      },
-      {
-       "end": "2026-01-15T06:00:00+01:00",
-       "start": "2026-01-15T05:00:00+01:00",
-       "value": 0.4861
-      },
-      {
-       "end": "2026-01-15T07:00:00+01:00",
-       "start": "2026-01-15T06:00:00+01:00",
-       "value": 0.7427
-      },
-      {
-       "end": "2026-01-15T08:00:00+01:00",
-       "start": "2026-01-15T07:00:00+01:00",
-       "value": 1.1406
-      },
-      {
-       "end": "2026-01-15T09:00:00+01:00",
-       "start": "2026-01-15T08:00:00+01:00",
-       "value": 1.3497
-      },
-      {
-       "end": "2026-01-15T10:00:00+01:00",
-       "start": "2026-01-15T09:00:00+01:00",
-       "value": 1.1333
-      },
-      {
-       "end": "2026-01-15T11:00:00+01:00",
-       "start": "2026-01-15T10:00:00+01:00",
-       "value": 0.7348
-      },
-      {
-       "end": "2026-01-15T12:00:00+01:00",
-       "start": "2026-01-15T11:00:00+01:00",
-       "value": 0.4849
-      },
-      {
-       "end": "2026-01-15T13:00:00+01:00",
-       "start": "2026-01-15T12:00:00+01:00",
-       "value": 0.4212
-      },
-      {
-       "end": "2026-01-15T14:00:00+01:00",
-       "start": "2026-01-15T13:00:00+01:00",
-       "value": 0.4416
-      },
-      {
-       "end": "2026-01-15T15:00:00+01:00",
-       "start": "2026-01-15T14:00:00+01:00",
-       "value": 0.4939
-      },
-      {
-       "end": "2026-01-15T16:00:00+01:00",
-       "start": "2026-01-15T15:00:00+01:00",
-       "value": 0.618
-      },
-      {
-       "end": "2026-01-15T17:00:00+01:00",
-       "start": "2026-01-15T16:00:00+01:00",
-       "value": 0.8966
-      },
-      {
-       "end": "2026-01-15T18:00:00+01:00",
-       "start": "2026-01-15T17:00:00+01:00",
-       "value": 1.2754
-      },
-      {
-       "end": "2026-01-15T19:00:00+01:00",
-       "start": "2026-01-15T18:00:00+01:00",
-       "value": 1.4775
-      },
-      {
-       "end": "2026-01-15T20:00:00+01:00",
-       "start": "2026-01-15T19:00:00+01:00",
-       "value": 1.3087
-      },
-      {
-       "end": "2026-01-15T21:00:00+01:00",
-       "start": "2026-01-15T20:00:00+01:00",
-       "value": 0.9327
-      },
-      {
-       "end": "2026-01-15T22:00:00+01:00",
-       "start": "2026-01-15T21:00:00+01:00",
-       "value": 0.6236
-      },
-      {
-       "end": "2026-01-15T23:00:00+01:00",
-       "start": "2026-01-15T22:00:00+01:00",
-       "value": 0.4638
-      },
-      {
-       "end": "2026-01-16T00:00:00+01:00",
-       "start": "2026-01-15T23:00:00+01:00",
-       "value": 0.4019
-      }
-     ],
-     "raw_tomorrow": [
-      {
-       "end": "2026-01-16T01:00:00+01:00",
-       "start": "2026-01-16T00:00:00+01:00",
-       "value": 0.42
-      },
-      {
-       "end": "2026-01-16T02:00:00+01:00",
-       "start": "2026-01-16T01:00:00+01:00",
-       "value": 0.4452
-      },
-      {
-       "end": "2026-01-16T03:00:00+01:00",
-       "start": "2026-01-16T02:00:00+01:00",
-       "value": 0.4474
-      },
-      {
-       "end": "2026-01-16T04:00:00+01:00",
-       "start": "2026-01-16T03:00:00+01:00",
-       "value": 0.426
-      },
-      {
-       "end": "2026-01-16T05:00:00+01:00",
-       "start": "2026-01-16T04:00:00+01:00",
-       "value": 0.4138
-      },
-      {
-       "end": "2026-01-16T06:00:00+01:00",
-       "start": "2026-01-16T05:00:00+01:00",
-       "value": 0.4861
-      },
-      {
-       "end": "2026-01-16T07:00:00+01:00",
-       "start": "2026-01-16T06:00:00+01:00",
-       "value": 0.7427
-      },
-      {
-       "end": "2026-01-16T08:00:00+01:00",
-       "start": "2026-01-16T07:00:00+01:00",
-       "value": 1.1406
-      },
-      {
-       "end": "2026-01-16T09:00:00+01:00",
-       "start": "2026-01-16T08:00:00+01:00",
-       "value": 1.3497
-      },
-      {
-       "end": "2026-01-16T10:00:00+01:00",
-       "start": "2026-01-16T09:00:00+01:00",
-       "value": 1.1333
-      },
-      {
-       "end": "2026-01-16T11:00:00+01:00",
-       "start": "2026-01-16T10:00:00+01:00",
-       "value": 0.7348
-      },
-      {
-       "end": "2026-01-16T12:00:00+01:00",
-       "start": "2026-01-16T11:00:00+01:00",
-       "value": 0.4849
-      },
-      {
-       "end": "2026-01-16T13:00:00+01:00",
-       "start": "2026-01-16T12:00:00+01:00",
-       "value": 0.4212
-      },
-      {
-       "end": "2026-01-16T14:00:00+01:00",
-       "start": "2026-01-16T13:00:00+01:00",
-       "value": 0.4416
-      },
-      {
-       "end": "2026-01-16T15:00:00+01:00",
-       "start": "2026-01-16T14:00:00+01:00",
-       "value": 0.4939
-      },
-      {
-       "end": "2026-01-16T16:00:00+01:00",
-       "start": "2026-01-16T15:00:00+01:00",
-       "value": 0.618
-      },
-      {
-       "end": "2026-01-16T17:00:00+01:00",
-       "start": "2026-01-16T16:00:00+01:00",
-       "value": 0.8966
-      },
-      {
-       "end": "2026-01-16T18:00:00+01:00",
-       "start": "2026-01-16T17:00:00+01:00",
-       "value": 1.2754
-      },
-      {
-       "end": "2026-01-16T19:00:00+01:00",
-       "start": "2026-01-16T18:00:00+01:00",
-       "value": 1.4775
-      },
-      {
-       "end": "2026-01-16T20:00:00+01:00",
-       "start": "2026-01-16T19:00:00+01:00",
-       "value": 1.3087
-      },
-      {
-       "end": "2026-01-16T21:00:00+01:00",
-       "start": "2026-01-16T20:00:00+01:00",
-       "value": 0.9327
-      },
-      {
-       "end": "2026-01-16T22:00:00+01:00",
-       "start": "2026-01-16T21:00:00+01:00",
-       "value": 0.6236
-      },
-      {
-       "end": "2026-01-16T23:00:00+01:00",
-       "start": "2026-01-16T22:00:00+01:00",
-       "value": 0.4638
-      },
-      {
-       "end": "2026-01-17T00:00:00+01:00",
-       "start": "2026-01-16T23:00:00+01:00",
-       "value": 0.4019
-      }
-     ],
-     "unit_of_measurement": "SEK/kWh"
-    },
-    "2026-01-15T12:59:00+00:00"
-   ],
-   [
-    "2026-01-15T13:00:00+00:00",
-    "0.4939",
-    null,
-    "2026-01-15T13:59:00+00:00"
-   ],
-   [
-    "2026-01-15T14:00:00+00:00",
-    "0.6180",
-    null,
-    "2026-01-15T14:59:00+00:00"
-   ],
-   [
-    "2026-01-15T15:00:00+00:00",
-    "0.8966",
-    null,
-    "2026-01-15T15:59:00+00:00"
-   ],
-   [
-    "2026-01-15T16:00:00+00:00",
-    "1.2754",
-    null,
-    "2026-01-15T16:59:00+00:00"
-   ],
-   [
-    "2026-01-15T17:00:00+00:00",
-    "1.4775",
-    null,
-    "2026-01-15T17:59:00+00:00"
-   ],
-   [
-    "2026-01-15T18:00:00+00:00",
-    "1.3087",
-    null,
-    "2026-01-15T18:59:00+00:00"
-   ],
-   [
-    "2026-01-15T19:00:00+00:00",
-    "0.9327",
-    null,
-    "2026-01-15T19:59:00+00:00"
-   ],
-   [
-    "2026-01-15T20:00:00+00:00",
-    "0.6236",
-    null,
-    "2026-01-15T20:59:00+00:00"
-   ],
-   [
-    "2026-01-15T21:00:00+00:00",
-    "0.4638",
-    null,
-    "2026-01-15T21:59:00+00:00"
-   ],
-   [
-    "2026-01-15T22:00:00+00:00",
-    "0.4019",
-    null,
-    "2026-01-15T22:59:00+00:00"
-   ]
-  ],
-  "sensor.outdoor_temperature": [
-   [
-    "2026-01-14T22:50:00+00:00",
-    "-7.1",
-    {
-     "device_class": "temperature",
-     "state_class": "measurement",
-     "unit_of_measurement": "\u00b0C"
-    },
-    "2026-01-14T22:59:00+00:00"
-   ],
-   [
-    "2026-01-14T23:00:00+00:00",
-    "-7.2",
-    null,
-    "2026-01-14T23:09:00+00:00"
-   ],
-   [
-    "2026-01-14T23:10:00+00:00",
-    "-7.3",
-    null,
-    "2026-01-14T23:19:00+00:00"
-   ],
-   [
-    "2026-01-14T23:20:00+00:00",
-    "-7.4",
-    null,
-    "2026-01-14T23:29:00+00:00"
-   ],
-   [
-    "2026-01-14T23:30:00+00:00",
-    "-7.4",
-    null,
-    "2026-01-14T23:39:00+00:00"
-   ],
-   [
-    "2026-01-14T23:40:00+00:00",
-    "-7.5",
-    null,
-    "2026-01-14T23:49:00+00:00"
-   ],
-   [
-    "2026-01-14T23:50:00+00:00",
-    "-7.6",
-    null,
-    "2026-01-14T23:59:00+00:00"
-   ],
-   [
-    "2026-01-15T00:00:00+00:00",
-    "-7.6",
-    null,
-    "2026-01-15T00:09:00+00:00"
-   ],
-   [
-    "2026-01-15T00:10:00+00:00",
-    "-7.7",
-    null,
-    "2026-01-15T00:19:00+00:00"
-   ],
-   [
-    "2026-01-15T00:20:00+00:00",
-    "-7.7",
-    null,
-    "2026-01-15T00:29:00+00:00"
-   ],
-   [
-    "2026-01-15T00:30:00+00:00",
-    "-7.8",
-    null,
-    "2026-01-15T00:39:00+00:00"
-   ],
-   [
-    "2026-01-15T00:40:00+00:00",
-    "-7.8",
-    null,
-    "2026-01-15T00:49:00+00:00"
-   ],
-   [
-    "2026-01-15T00:50:00+00:00",
-    "-7.9",
-    null,
-    "2026-01-15T00:59:00+00:00"
+    "2026-01-15T00:59:00+00:00"
    ],
    [
     "2026-01-15T01:00:00+00:00",
@@ -6387,277 +5615,1049 @@
     "2026-01-15T15:29:00+00:00"
    ],
    [
-    "2026-01-15T15:30:00+00:00",
-    "-2.8",
+    "2026-01-15T15:30:00+00:00",
+    "-2.8",
+    null,
+    "2026-01-15T15:39:00+00:00"
+   ],
+   [
+    "2026-01-15T15:40:00+00:00",
+    "-2.9",
+    null,
+    "2026-01-15T15:49:00+00:00"
+   ],
+   [
+    "2026-01-15T15:50:00+00:00",
+    "-2.9",
+    null,
+    "2026-01-15T15:59:00+00:00"
+   ],
+   [
+    "2026-01-15T16:00:00+00:00",
+    "-3.0",
+    null,
+    "2026-01-15T16:09:00+00:00"
+   ],
+   [
+    "2026-01-15T16:10:00+00:00",
+    "-3.0",
+    null,
+    "2026-01-15T16:19:00+00:00"
+   ],
+   [
+    "2026-01-15T16:20:00+00:00",
+    "-3.1",
+    null,
+    "2026-01-15T16:29:00+00:00"
+   ],
+   [
+    "2026-01-15T16:30:00+00:00",
+    "-3.2",
+    null,
+    "2026-01-15T16:39:00+00:00"
+   ],
+   [
+    "2026-01-15T16:40:00+00:00",
+    "-3.2",
+    null,
+    "2026-01-15T16:49:00+00:00"
+   ],
+   [
+    "2026-01-15T16:50:00+00:00",
+    "-3.3",
+    null,
+    "2026-01-15T16:59:00+00:00"
+   ],
+   [
+    "2026-01-15T17:00:00+00:00",
+    "-3.4",
+    null,
+    "2026-01-15T17:09:00+00:00"
+   ],
+   [
+    "2026-01-15T17:10:00+00:00",
+    "-3.5",
+    null,
+    "2026-01-15T17:19:00+00:00"
+   ],
+   [
+    "2026-01-15T17:20:00+00:00",
+    "-3.6",
+    null,
+    "2026-01-15T17:29:00+00:00"
+   ],
+   [
+    "2026-01-15T17:30:00+00:00",
+    "-3.7",
+    null,
+    "2026-01-15T17:39:00+00:00"
+   ],
+   [
+    "2026-01-15T17:40:00+00:00",
+    "-3.8",
+    null,
+    "2026-01-15T17:49:00+00:00"
+   ],
+   [
+    "2026-01-15T17:50:00+00:00",
+    "-3.8",
+    null,
+    "2026-01-15T17:59:00+00:00"
+   ],
+   [
+    "2026-01-15T18:00:00+00:00",
+    "-4.0",
+    null,
+    "2026-01-15T18:09:00+00:00"
+   ],
+   [
+    "2026-01-15T18:10:00+00:00",
+    "-4.1",
+    null,
+    "2026-01-15T18:19:00+00:00"
+   ],
+   [
+    "2026-01-15T18:20:00+00:00",
+    "-4.2",
+    null,
+    "2026-01-15T18:29:00+00:00"
+   ],
+   [
+    "2026-01-15T18:30:00+00:00",
+    "-4.3",
+    null,
+    "2026-01-15T18:39:00+00:00"
+   ],
+   [
+    "2026-01-15T18:40:00+00:00",
+    "-4.4",
+    null,
+    "2026-01-15T18:49:00+00:00"
+   ],
+   [
+    "2026-01-15T18:50:00+00:00",
+    "-4.5",
+    null,
+    "2026-01-15T18:59:00+00:00"
+   ],
+   [
+    "2026-01-15T19:00:00+00:00",
+    "-4.6",
+    null,
+    "2026-01-15T19:09:00+00:00"
+   ],
+   [
+    "2026-01-15T19:10:00+00:00",
+    "-4.7",
+    null,
+    "2026-01-15T19:19:00+00:00"
+   ],
+   [
+    "2026-01-15T19:20:00+00:00",
+    "-4.8",
+    null,
+    "2026-01-15T19:29:00+00:00"
+   ],
+   [
+    "2026-01-15T19:30:00+00:00",
+    "-4.9",
+    null,
+    "2026-01-15T19:39:00+00:00"
+   ],
+   [
+    "2026-01-15T19:40:00+00:00",
+    "-5.1",
+    null,
+    "2026-01-15T19:49:00+00:00"
+   ],
+   [
+    "2026-01-15T19:50:00+00:00",
+    "-5.2",
+    null,
+    "2026-01-15T19:59:00+00:00"
+   ],
+   [
+    "2026-01-15T20:00:00+00:00",
+    "-5.3",
+    null,
+    "2026-01-15T20:09:00+00:00"
+   ],
+   [
+    "2026-01-15T20:10:00+00:00",
+    "-5.4",
+    null,
+    "2026-01-15T20:19:00+00:00"
+   ],
+   [
+    "2026-01-15T20:20:00+00:00",
+    "-5.5",
+    null,
+    "2026-01-15T20:29:00+00:00"
+   ],
+   [
+    "2026-01-15T20:30:00+00:00",
+    "-5.7",
+    null,
+    "2026-01-15T20:39:00+00:00"
+   ],
+   [
+    "2026-01-15T20:40:00+00:00",
+    "-5.8",
+    null,
+    "2026-01-15T20:49:00+00:00"
+   ],
+   [
+    "2026-01-15T20:50:00+00:00",
+    "-5.9",
+    null,
+    "2026-01-15T20:59:00+00:00"
+   ],
+   [
+    "2026-01-15T21:00:00+00:00",
+    "-6.0",
+    null,
+    "2026-01-15T21:09:00+00:00"
+   ],
+   [
+    "2026-01-15T21:10:00+00:00",
+    "-6.1",
+    null,
+    "2026-01-15T21:19:00+00:00"
+   ],
+   [
+    "2026-01-15T21:20:00+00:00",
+    "-6.2",
+    null,
+    "2026-01-15T21:29:00+00:00"
+   ],
+   [
+    "2026-01-15T21:30:00+00:00",
+    "-6.3",
+    null,
+    "2026-01-15T21:39:00+00:00"
+   ],
+   [
+    "2026-01-15T21:40:00+00:00",
+    "-6.4",
+    null,
+    "2026-01-15T21:49:00+00:00"
+   ],
+   [
+    "2026-01-15T21:50:00+00:00",
+    "-6.5",
+    null,
+    "2026-01-15T21:59:00+00:00"
+   ],
+   [
+    "2026-01-15T22:00:00+00:00",
+    "-6.7",
+    null,
+    "2026-01-15T22:09:00+00:00"
+   ],
+   [
+    "2026-01-15T22:10:00+00:00",
+    "-6.8",
+    null,
+    "2026-01-15T22:19:00+00:00"
+   ],
+   [
+    "2026-01-15T22:20:00+00:00",
+    "-6.8",
+    null,
+    "2026-01-15T22:29:00+00:00"
+   ],
+   [
+    "2026-01-15T22:30:00+00:00",
+    "-6.9",
+    null,
+    "2026-01-15T22:39:00+00:00"
+   ],
+   [
+    "2026-01-15T22:40:00+00:00",
+    "-7.0",
+    null,
+    "2026-01-15T22:49:00+00:00"
+   ],
+   [
+    "2026-01-15T22:50:00+00:00",
+    "-7.1",
+    null,
+    "2026-01-15T22:59:00+00:00"
+   ]
+  ],
+  "sensor.price": [
+   [
+    "2026-01-14T22:00:00+00:00",
+    "0.4019",
+    {
+     "currency": "SEK",
+     "raw_today": [
+      {
+       "end": "2026-01-14T01:00:00+01:00",
+       "start": "2026-01-14T00:00:00+01:00",
+       "value": 0.42
+      },
+      {
+       "end": "2026-01-14T02:00:00+01:00",
+       "start": "2026-01-14T01:00:00+01:00",
+       "value": 0.4452
+      },
+      {
+       "end": "2026-01-14T03:00:00+01:00",
+       "start": "2026-01-14T02:00:00+01:00",
+       "value": 0.4474
+      },
+      {
+       "end": "2026-01-14T04:00:00+01:00",
+       "start": "2026-01-14T03:00:00+01:00",
+       "value": 0.426
+      },
+      {
+       "end": "2026-01-14T05:00:00+01:00",
+       "start": "2026-01-14T04:00:00+01:00",
+       "value": 0.4138
+      },
+      {
+       "end": "2026-01-14T06:00:00+01:00",
+       "start": "2026-01-14T05:00:00+01:00",
+       "value": 0.4861
+      },
+      {
+       "end": "2026-01-14T07:00:00+01:00",
+       "start": "2026-01-14T06:00:00+01:00",
+       "value": 0.7427
+      },
+      {
+       "end": "2026-01-14T08:00:00+01:00",
+       "start": "2026-01-14T07:00:00+01:00",
+       "value": 1.1406
+      },
+      {
+       "end": "2026-01-14T09:00:00+01:00",
+       "start": "2026-01-14T08:00:00+01:00",
+       "value": 1.3497
+      },
+      {
+       "end": "2026-01-14T10:00:00+01:00",
+       "start": "2026-01-14T09:00:00+01:00",
+       "value": 1.1333
+      },
+      {
+       "end": "2026-01-14T11:00:00+01:00",
+       "start": "2026-01-14T10:00:00+01:00",
+       "value": 0.7348
+      },
+      {
+       "end": "2026-01-14T12:00:00+01:00",
+       "start": "2026-01-14T11:00:00+01:00",
+       "value": 0.4849
+      },
+      {
+       "end": "2026-01-14T13:00:00+01:00",
+       "start": "2026-01-14T12:00:00+01:00",
+       "value": 0.4212
+      },
+      {
+       "end": "2026-01-14T14:00:00+01:00",
+       "start": "2026-01-14T13:00:00+01:00",
+       "value": 0.4416
+      },
+      {
+       "end": "2026-01-14T15:00:00+01:00",
+       "start": "2026-01-14T14:00:00+01:00",
+       "value": 0.4939
+      },
+      {
+       "end": "2026-01-14T16:00:00+01:00",
+       "start": "2026-01-14T15:00:00+01:00",
+       "value": 0.618
+      },
+      {
+       "end": "2026-01-14T17:00:00+01:00",
+       "start": "2026-01-14T16:00:00+01:00",
+       "value": 0.8966
+      },
+      {
+       "end": "2026-01-14T18:00:00+01:00",
+       "start": "2026-01-14T17:00:00+01:00",
+       "value": 1.2754
+      },
+      {
+       "end": "2026-01-14T19:00:00+01:00",
+       "start": "2026-01-14T18:00:00+01:00",
+       "value": 1.4775
+      },
+      {
+       "end": "2026-01-14T20:00:00+01:00",
+       "start": "2026-01-14T19:00:00+01:00",
+       "value": 1.3087
+      },
+      {
+       "end": "2026-01-14T21:00:00+01:00",
+       "start": "2026-01-14T20:00:00+01:00",
+       "value": 0.9327
+      },
+      {
+       "end": "2026-01-14T22:00:00+01:00",
+       "start": "2026-01-14T21:00:00+01:00",
+       "value": 0.6236
+      },
+      {
+       "end": "2026-01-14T23:00:00+01:00",
+       "start": "2026-01-14T22:00:00+01:00",
+       "value": 0.4638
+      },
+      {
+       "end": "2026-01-15T00:00:00+01:00",
+       "start": "2026-01-14T23:00:00+01:00",
+       "value": 0.4019
+      }
+     ],
+     "raw_tomorrow": [
+      {
+       "end": "2026-01-16T01:00:00+01:00",
+       "start": "2026-01-16T00:00:00+01:00",
+       "value": 0.42
+      },
+      {
+       "end": "2026-01-16T02:00:00+01:00",
+       "start": "2026-01-16T01:00:00+01:00",
+       "value": 0.4452
+      },
+      {
+       "end": "2026-01-16T03:00:00+01:00",
+       "start": "2026-01-16T02:00:00+01:00",
+       "value": 0.4474
+      },
+      {
+       "end": "2026-01-16T04:00:00+01:00",
+       "start": "2026-01-16T03:00:00+01:00",
+       "value": 0.426
+      },
+      {
+       "end": "2026-01-16T05:00:00+01:00",
+       "start": "2026-01-16T04:00:00+01:00",
+       "value": 0.4138
+      },
+      {
+       "end": "2026-01-16T06:00:00+01:00",
+       "start": "2026-01-16T05:00:00+01:00",
+       "value": 0.4861
+      },
+      {
+       "end": "2026-01-16T07:00:00+01:00",
+       "start": "2026-01-16T06:00:00+01:00",
+       "value": 0.7427
+      },
+      {
+       "end": "2026-01-16T08:00:00+01:00",
+       "start": "2026-01-16T07:00:00+01:00",
+       "value": 1.1406
+      },
+      {
+       "end": "2026-01-16T09:00:00+01:00",
+       "start": "2026-01-16T08:00:00+01:00",
+       "value": 1.3497
+      },
+      {
+       "end": "2026-01-16T10:00:00+01:00",
+       "start": "2026-01-16T09:00:00+01:00",
+       "value": 1.1333
+      },
+      {
+       "end": "2026-01-16T11:00:00+01:00",
+       "start": "2026-01-16T10:00:00+01:00",
+       "value": 0.7348
+      },
+      {
+       "end": "2026-01-16T12:00:00+01:00",
+       "start": "2026-01-16T11:00:00+01:00",
+       "value": 0.4849
+      },
+      {
+       "end": "2026-01-16T13:00:00+01:00",
+       "start": "2026-01-16T12:00:00+01:00",
+       "value": 0.4212
+      },
+      {
+       "end": "2026-01-16T14:00:00+01:00",
+       "start": "2026-01-16T13:00:00+01:00",
+       "value": 0.4416
+      },
+      {
+       "end": "2026-01-16T15:00:00+01:00",
+       "start": "2026-01-16T14:00:00+01:00",
+       "value": 0.4939
+      },
+      {
+       "end": "2026-01-16T16:00:00+01:00",
+       "start": "2026-01-16T15:00:00+01:00",
+       "value": 0.618
+      },
+      {
+       "end": "2026-01-16T17:00:00+01:00",
+       "start": "2026-01-16T16:00:00+01:00",
+       "value": 0.8966
+      },
+      {
+       "end": "2026-01-16T18:00:00+01:00",
+       "start": "2026-01-16T17:00:00+01:00",
+       "value": 1.2754
+      },
+      {
+       "end": "2026-01-16T19:00:00+01:00",
+       "start": "2026-01-16T18:00:00+01:00",
+       "value": 1.4775
+      },
+      {
+       "end": "2026-01-16T20:00:00+01:00",
+       "start": "2026-01-16T19:00:00+01:00",
+       "value": 1.3087
+      },
+      {
+       "end": "2026-01-16T21:00:00+01:00",
+       "start": "2026-01-16T20:00:00+01:00",
+       "value": 0.9327
+      },
+      {
+       "end": "2026-01-16T22:00:00+01:00",
+       "start": "2026-01-16T21:00:00+01:00",
+       "value": 0.6236
+      },
+      {
+       "end": "2026-01-16T23:00:00+01:00",
+       "start": "2026-01-16T22:00:00+01:00",
+       "value": 0.4638
+      },
+      {
+       "end": "2026-01-17T00:00:00+01:00",
+       "start": "2026-01-16T23:00:00+01:00",
+       "value": 0.4019
+      }
+     ],
+     "unit_of_measurement": "SEK/kWh"
+    },
+    "2026-01-14T22:59:00+00:00"
+   ],
+   [
+    "2026-01-14T23:00:00+00:00",
+    "0.4200",
+    {
+     "currency": "SEK",
+     "raw_today": [
+      {
+       "end": "2026-01-15T01:00:00+01:00",
+       "start": "2026-01-15T00:00:00+01:00",
+       "value": 0.42
+      },
+      {
+       "end": "2026-01-15T02:00:00+01:00",
+       "start": "2026-01-15T01:00:00+01:00",
+       "value": 0.4452
+      },
+      {
+       "end": "2026-01-15T03:00:00+01:00",
+       "start": "2026-01-15T02:00:00+01:00",
+       "value": 0.4474
+      },
+      {
+       "end": "2026-01-15T04:00:00+01:00",
+       "start": "2026-01-15T03:00:00+01:00",
+       "value": 0.426
+      },
+      {
+       "end": "2026-01-15T05:00:00+01:00",
+       "start": "2026-01-15T04:00:00+01:00",
+       "value": 0.4138
+      },
+      {
+       "end": "2026-01-15T06:00:00+01:00",
+       "start": "2026-01-15T05:00:00+01:00",
+       "value": 0.4861
+      },
+      {
+       "end": "2026-01-15T07:00:00+01:00",
+       "start": "2026-01-15T06:00:00+01:00",
+       "value": 0.7427
+      },
+      {
+       "end": "2026-01-15T08:00:00+01:00",
+       "start": "2026-01-15T07:00:00+01:00",
+       "value": 1.1406
+      },
+      {
+       "end": "2026-01-15T09:00:00+01:00",
+       "start": "2026-01-15T08:00:00+01:00",
+       "value": 1.3497
+      },
+      {
+       "end": "2026-01-15T10:00:00+01:00",
+       "start": "2026-01-15T09:00:00+01:00",
+       "value": 1.1333
+      },
+      {
+       "end": "2026-01-15T11:00:00+01:00",
+       "start": "2026-01-15T10:00:00+01:00",
+       "value": 0.7348
+      },
+      {
+       "end": "2026-01-15T12:00:00+01:00",
+       "start": "2026-01-15T11:00:00+01:00",
+       "value": 0.4849
+      },
+      {
+       "end": "2026-01-15T13:00:00+01:00",
+       "start": "2026-01-15T12:00:00+01:00",
+       "value": 0.4212
+      },
+      {
+       "end": "2026-01-15T14:00:00+01:00",
+       "start": "2026-01-15T13:00:00+01:00",
+       "value": 0.4416
+      },
+      {
+       "end": "2026-01-15T15:00:00+01:00",
+       "start": "2026-01-15T14:00:00+01:00",
+       "value": 0.4939
+      },
+      {
+       "end": "2026-01-15T16:00:00+01:00",
+       "start": "2026-01-15T15:00:00+01:00",
+       "value": 0.618
+      },
+      {
+       "end": "2026-01-15T17:00:00+01:00",
+       "start": "2026-01-15T16:00:00+01:00",
+       "value": 0.8966
+      },
+      {
+       "end": "2026-01-15T18:00:00+01:00",
+       "start": "2026-01-15T17:00:00+01:00",
+       "value": 1.2754
+      },
+      {
+       "end": "2026-01-15T19:00:00+01:00",
+       "start": "2026-01-15T18:00:00+01:00",
+       "value": 1.4775
+      },
+      {
+       "end": "2026-01-15T20:00:00+01:00",
+       "start": "2026-01-15T19:00:00+01:00",
+       "value": 1.3087
+      },
+      {
+       "end": "2026-01-15T21:00:00+01:00",
+       "start": "2026-01-15T20:00:00+01:00",
+       "value": 0.9327
+      },
+      {
+       "end": "2026-01-15T22:00:00+01:00",
+       "start": "2026-01-15T21:00:00+01:00",
+       "value": 0.6236
+      },
+      {
+       "end": "2026-01-15T23:00:00+01:00",
+       "start": "2026-01-15T22:00:00+01:00",
+       "value": 0.4638
+      },
+      {
+       "end": "2026-01-16T00:00:00+01:00",
+       "start": "2026-01-15T23:00:00+01:00",
+       "value": 0.4019
+      }
+     ],
+     "raw_tomorrow": [],
+     "unit_of_measurement": "SEK/kWh"
+    },
+    "2026-01-14T23:59:00+00:00"
+   ],
+   [
+    "2026-01-15T00:00:00+00:00",
+    "0.4452",
+    null,
+    "2026-01-15T00:59:00+00:00"
+   ],
+   [
+    "2026-01-15T01:00:00+00:00",
+    "0.4474",
+    null,
+    "2026-01-15T01:59:00+00:00"
+   ],
+   [
+    "2026-01-15T02:00:00+00:00",
+    "0.4260",
+    null,
+    "2026-01-15T02:59:00+00:00"
+   ],
+   [
+    "2026-01-15T03:00:00+00:00",
+    "0.4138",
+    null,
+    "2026-01-15T03:59:00+00:00"
+   ],
+   [
+    "2026-01-15T04:00:00+00:00",
+    "0.4861",
+    null,
+    "2026-01-15T04:59:00+00:00"
+   ],
+   [
+    "2026-01-15T05:00:00+00:00",
+    "0.7427",
+    null,
+    "2026-01-15T05:59:00+00:00"
+   ],
+   [
+    "2026-01-15T06:00:00+00:00",
+    "1.1406",
+    null,
+    "2026-01-15T06:59:00+00:00"
+   ],
+   [
+    "2026-01-15T07:00:00+00:00",
+    "1.3497",
+    null,
+    "2026-01-15T07:59:00+00:00"
+   ],
+   [
+    "2026-01-15T08:00:00+00:00",
+    "1.1333",
+    null,
+    "2026-01-15T08:59:00+00:00"
+   ],
+   [
+    "2026-01-15T09:00:00+00:00",
+    "0.7348",
+    null,
+    "2026-01-15T09:59:00+00:00"
+   ],
+   [
+    "2026-01-15T10:00:00+00:00",
+    "0.4849",
+    null,
+    "2026-01-15T10:59:00+00:00"
+   ],
+   [
+    "2026-01-15T11:00:00+00:00",
+    "0.4212",
+    null,
+    "2026-01-15T11:59:00+00:00"
+   ],
+   [
+    "2026-01-15T12:00:00+00:00",
+    "0.4416",
+    {
+     "currency": "SEK",
+     "raw_today": [
+      {
+       "end": "2026-01-15T01:00:00+01:00",
+       "start": "2026-01-15T00:00:00+01:00",
+       "value": 0.42
+      },
+      {
+       "end": "2026-01-15T02:00:00+01:00",
+       "start": "2026-01-15T01:00:00+01:00",
+       "value": 0.4452
+      },
+      {
+       "end": "2026-01-15T03:00:00+01:00",
+       "start": "2026-01-15T02:00:00+01:00",
+       "value": 0.4474
+      },
+      {
+       "end": "2026-01-15T04:00:00+01:00",
+       "start": "2026-01-15T03:00:00+01:00",
+       "value": 0.426
+      },
+      {
+       "end": "2026-01-15T05:00:00+01:00",
+       "start": "2026-01-15T04:00:00+01:00",
+       "value": 0.4138
+      },
+      {
+       "end": "2026-01-15T06:00:00+01:00",
+       "start": "2026-01-15T05:00:00+01:00",
+       "value": 0.4861
+      },
+      {
+       "end": "2026-01-15T07:00:00+01:00",
+       "start": "2026-01-15T06:00:00+01:00",
+       "value": 0.7427
+      },
+      {
+       "end": "2026-01-15T08:00:00+01:00",
+       "start": "2026-01-15T07:00:00+01:00",
+       "value": 1.1406
+      },
+      {
+       "end": "2026-01-15T09:00:00+01:00",
+       "start": "2026-01-15T08:00:00+01:00",
+       "value": 1.3497
+      },
+      {
+       "end": "2026-01-15T10:00:00+01:00",
+       "start": "2026-01-15T09:00:00+01:00",
+       "value": 1.1333
+      },
+      {
+       "end": "2026-01-15T11:00:00+01:00",
+       "start": "2026-01-15T10:00:00+01:00",
+       "value": 0.7348
+      },
+      {
+       "end": "2026-01-15T12:00:00+01:00",
+       "start": "2026-01-15T11:00:00+01:00",
+       "value": 0.4849
+      },
+      {
+       "end": "2026-01-15T13:00:00+01:00",
+       "start": "2026-01-15T12:00:00+01:00",
+       "value": 0.4212
+      },
+      {
+       "end": "2026-01-15T14:00:00+01:00",
+       "start": "2026-01-15T13:00:00+01:00",
+       "value": 0.4416
+      },
+      {
+       "end": "2026-01-15T15:00:00+01:00",
+       "start": "2026-01-15T14:00:00+01:00",
+       "value": 0.4939
+      },
+      {
+       "end": "2026-01-15T16:00:00+01:00",
+       "start": "2026-01-15T15:00:00+01:00",
+       "value": 0.618
+      },
+      {
+       "end": "2026-01-15T17:00:00+01:00",
+       "start": "2026-01-15T16:00:00+01:00",
+       "value": 0.8966
+      },
+      {
+       "end": "2026-01-15T18:00:00+01:00",
+       "start": "2026-01-15T17:00:00+01:00",
+       "value": 1.2754
+      },
+      {
+       "end": "2026-01-15T19:00:00+01:00",
+       "start": "2026-01-15T18:00:00+01:00",
+       "value": 1.4775
+      },
+      {
+       "end": "2026-01-15T20:00:00+01:00",
+       "start": "2026-01-15T19:00:00+01:00",
+       "value": 1.3087
+      },
+      {
+       "end": "2026-01-15T21:00:00+01:00",
+       "start": "2026-01-15T20:00:00+01:00",
+       "value": 0.9327
+      },
+      {
+       "end": "2026-01-15T22:00:00+01:00",
+       "start": "2026-01-15T21:00:00+01:00",
+       "value": 0.6236
+      },
+      {
+       "end": "2026-01-15T23:00:00+01:00",
+       "start": "2026-01-15T22:00:00+01:00",
+       "value": 0.4638
+      },
+      {
+       "end": "2026-01-16T00:00:00+01:00",
+       "start": "2026-01-15T23:00:00+01:00",
+       "value": 0.4019
+      }
+     ],
+     "raw_tomorrow": [
+      {
+       "end": "2026-01-16T01:00:00+01:00",
+       "start": "2026-01-16T00:00:00+01:00",
+       "value": 0.42
+      },
+      {
+       "end": "2026-01-16T02:00:00+01:00",
+       "start": "2026-01-16T01:00:00+01:00",
+       "value": 0.4452
+      },
+      {
+       "end": "2026-01-16T03:00:00+01:00",
+       "start": "2026-01-16T02:00:00+01:00",
+       "value": 0.4474
+      },
+      {
+       "end": "2026-01-16T04:00:00+01:00",
+       "start": "2026-01-16T03:00:00+01:00",
+       "value": 0.426
+      },
+      {
+       "end": "2026-01-16T05:00:00+01:00",
+       "start": "2026-01-16T04:00:00+01:00",
+       "value": 0.4138
+      },
+      {
+       "end": "2026-01-16T06:00:00+01:00",
+       "start": "2026-01-16T05:00:00+01:00",
+       "value": 0.4861
+      },
+      {
+       "end": "2026-01-16T07:00:00+01:00",
+       "start": "2026-01-16T06:00:00+01:00",
+       "value": 0.7427
+      },
+      {
+       "end": "2026-01-16T08:00:00+01:00",
+       "start": "2026-01-16T07:00:00+01:00",
+       "value": 1.1406
+      },
+      {
+       "end": "2026-01-16T09:00:00+01:00",
+       "start": "2026-01-16T08:00:00+01:00",
+       "value": 1.3497
+      },
+      {
+       "end": "2026-01-16T10:00:00+01:00",
+       "start": "2026-01-16T09:00:00+01:00",
+       "value": 1.1333
+      },
+      {
+       "end": "2026-01-16T11:00:00+01:00",
+       "start": "2026-01-16T10:00:00+01:00",
+       "value": 0.7348
+      },
+      {
+       "end": "2026-01-16T12:00:00+01:00",
+       "start": "2026-01-16T11:00:00+01:00",
+       "value": 0.4849
+      },
+      {
+       "end": "2026-01-16T13:00:00+01:00",
+       "start": "2026-01-16T12:00:00+01:00",
+       "value": 0.4212
+      },
+      {
+       "end": "2026-01-16T14:00:00+01:00",
+       "start": "2026-01-16T13:00:00+01:00",
+       "value": 0.4416
+      },
+      {
+       "end": "2026-01-16T15:00:00+01:00",
+       "start": "2026-01-16T14:00:00+01:00",
+       "value": 0.4939
+      },
+      {
+       "end": "2026-01-16T16:00:00+01:00",
+       "start": "2026-01-16T15:00:00+01:00",
+       "value": 0.618
+      },
+      {
+       "end": "2026-01-16T17:00:00+01:00",
+       "start": "2026-01-16T16:00:00+01:00",
+       "value": 0.8966
+      },
+      {
+       "end": "2026-01-16T18:00:00+01:00",
+       "start": "2026-01-16T17:00:00+01:00",
+       "value": 1.2754
+      },
+      {
+       "end": "2026-01-16T19:00:00+01:00",
+       "start": "2026-01-16T18:00:00+01:00",
+       "value": 1.4775
+      },
+      {
+       "end": "2026-01-16T20:00:00+01:00",
+       "start": "2026-01-16T19:00:00+01:00",
+       "value": 1.3087
+      },
+      {
+       "end": "2026-01-16T21:00:00+01:00",
+       "start": "2026-01-16T20:00:00+01:00",
+       "value": 0.9327
+      },
+      {
+       "end": "2026-01-16T22:00:00+01:00",
+       "start": "2026-01-16T21:00:00+01:00",
+       "value": 0.6236
+      },
+      {
+       "end": "2026-01-16T23:00:00+01:00",
+       "start": "2026-01-16T22:00:00+01:00",
+       "value": 0.4638
+      },
+      {
+       "end": "2026-01-17T00:00:00+01:00",
+       "start": "2026-01-16T23:00:00+01:00",
+       "value": 0.4019
+      }
+     ],
+     "unit_of_measurement": "SEK/kWh"
+    },
+    "2026-01-15T12:59:00+00:00"
+   ],
+   [
+    "2026-01-15T13:00:00+00:00",
+    "0.4939",
     null,
-    "2026-01-15T15:39:00+00:00"
+    "2026-01-15T13:59:00+00:00"
    ],
    [
-    "2026-01-15T15:40:00+00:00",
-    "-2.9",
+    "2026-01-15T14:00:00+00:00",
+    "0.6180",
     null,
-    "2026-01-15T15:49:00+00:00"
+    "2026-01-15T14:59:00+00:00"
    ],
    [
-    "2026-01-15T15:50:00+00:00",
-    "-2.9",
+    "2026-01-15T15:00:00+00:00",
+    "0.8966",
     null,
     "2026-01-15T15:59:00+00:00"
    ],
    [
     "2026-01-15T16:00:00+00:00",
-    "-3.0",
-    null,
-    "2026-01-15T16:09:00+00:00"
-   ],
-   [
-    "2026-01-15T16:10:00+00:00",
-    "-3.0",
-    null,
-    "2026-01-15T16:19:00+00:00"
-   ],
-   [
-    "2026-01-15T16:20:00+00:00",
-    "-3.1",
-    null,
-    "2026-01-15T16:29:00+00:00"
-   ],
-   [
-    "2026-01-15T16:30:00+00:00",
-    "-3.2",
-    null,
-    "2026-01-15T16:39:00+00:00"
-   ],
-   [
-    "2026-01-15T16:40:00+00:00",
-    "-3.2",
-    null,
-    "2026-01-15T16:49:00+00:00"
-   ],
-   [
-    "2026-01-15T16:50:00+00:00",
-    "-3.3",
+    "1.2754",
     null,
     "2026-01-15T16:59:00+00:00"
    ],
    [
     "2026-01-15T17:00:00+00:00",
-    "-3.4",
-    null,
-    "2026-01-15T17:09:00+00:00"
-   ],
-   [
-    "2026-01-15T17:10:00+00:00",
-    "-3.5",
-    null,
-    "2026-01-15T17:19:00+00:00"
-   ],
-   [
-    "2026-01-15T17:20:00+00:00",
-    "-3.6",
-    null,
-    "2026-01-15T17:29:00+00:00"
-   ],
-   [
-    "2026-01-15T17:30:00+00:00",
-    "-3.7",
-    null,
-    "2026-01-15T17:39:00+00:00"
-   ],
-   [
-    "2026-01-15T17:40:00+00:00",
-    "-3.8",
-    null,
-    "2026-01-15T17:49:00+00:00"
-   ],
-   [
-    "2026-01-15T17:50:00+00:00",
-    "-3.8",
+    "1.4775",
     null,
     "2026-01-15T17:59:00+00:00"
    ],
    [
     "2026-01-15T18:00:00+00:00",
-    "-4.0",
-    null,
-    "2026-01-15T18:09:00+00:00"
-   ],
-   [
-    "2026-01-15T18:10:00+00:00",
-    "-4.1",
-    null,
-    "2026-01-15T18:19:00+00:00"
-   ],
-   [
-    "2026-01-15T18:20:00+00:00",
-    "-4.2",
-    null,
-    "2026-01-15T18:29:00+00:00"
-   ],
-   [
-    "2026-01-15T18:30:00+00:00",
-    "-4.3",
-    null,
-    "2026-01-15T18:39:00+00:00"
-   ],
-   [
-    "2026-01-15T18:40:00+00:00",
-    "-4.4",
-    null,
-    "2026-01-15T18:49:00+00:00"
-   ],
-   [
-    "2026-01-15T18:50:00+00:00",
-    "-4.5",
+    "1.3087",
     null,
     "2026-01-15T18:59:00+00:00"
    ],
    [
     "2026-01-15T19:00:00+00:00",
-    "-4.6",
-    null,
-    "2026-01-15T19:09:00+00:00"
-   ],
-   [
-    "2026-01-15T19:10:00+00:00",
-    "-4.7",
-    null,
-    "2026-01-15T19:19:00+00:00"
-   ],
-   [
-    "2026-01-15T19:20:00+00:00",
-    "-4.8",
-    null,
-    "2026-01-15T19:29:00+00:00"
-   ],
-   [
-    "2026-01-15T19:30:00+00:00",
-    "-4.9",
-    null,
-    "2026-01-15T19:39:00+00:00"
-   ],
-   [
-    "2026-01-15T19:40:00+00:00",
-    "-5.1",
-    null,
-    "2026-01-15T19:49:00+00:00"
-   ],
-   [
-    "2026-01-15T19:50:00+00:00",
-    "-5.2",
+    "0.9327",
     null,
     "2026-01-15T19:59:00+00:00"
    ],
    [
     "2026-01-15T20:00:00+00:00",
-    "-5.3",
-    null,
-    "2026-01-15T20:09:00+00:00"
-   ],
-   [
-    "2026-01-15T20:10:00+00:00",
-    "-5.4",
-    null,
-    "2026-01-15T20:19:00+00:00"
-   ],
-   [
-    "2026-01-15T20:20:00+00:00",
-    "-5.5",
-    null,
-    "2026-01-15T20:29:00+00:00"
-   ],
-   [
-    "2026-01-15T20:30:00+00:00",
-    "-5.7",
-    null,
-    "2026-01-15T20:39:00+00:00"
-   ],
-   [
-    "2026-01-15T20:40:00+00:00",
-    "-5.8",
-    null,
-    "2026-01-15T20:49:00+00:00"
-   ],
-   [
-    "2026-01-15T20:50:00+00:00",
-    "-5.9",
+    "0.6236",
     null,
     "2026-01-15T20:59:00+00:00"
    ],
    [
     "2026-01-15T21:00:00+00:00",
-    "-6.0",
-    null,
-    "2026-01-15T21:09:00+00:00"
-   ],
-   [
-    "2026-01-15T21:10:00+00:00",
-    "-6.1",
-    null,
-    "2026-01-15T21:19:00+00:00"
-   ],
-   [
-    "2026-01-15T21:20:00+00:00",
-    "-6.2",
-    null,
-    "2026-01-15T21:29:00+00:00"
-   ],
-   [
-    "2026-01-15T21:30:00+00:00",
-    "-6.3",
-    null,
-    "2026-01-15T21:39:00+00:00"
-   ],
-   [
-    "2026-01-15T21:40:00+00:00",
-    "-6.4",
-    null,
-    "2026-01-15T21:49:00+00:00"
-   ],
-   [
-    "2026-01-15T21:50:00+00:00",
-    "-6.5",
+    "0.4638",
     null,
     "2026-01-15T21:59:00+00:00"
    ],
    [
     "2026-01-15T22:00:00+00:00",
-    "-6.7",
-    null,
-    "2026-01-15T22:09:00+00:00"
-   ],
-   [
-    "2026-01-15T22:10:00+00:00",
-    "-6.8",
-    null,
-    "2026-01-15T22:19:00+00:00"
-   ],
-   [
-    "2026-01-15T22:20:00+00:00",
-    "-6.8",
-    null,
-    "2026-01-15T22:29:00+00:00"
-   ],
-   [
-    "2026-01-15T22:30:00+00:00",
-    "-6.9",
-    null,
-    "2026-01-15T22:39:00+00:00"
-   ],
-   [
-    "2026-01-15T22:40:00+00:00",
-    "-7.0",
-    null,
-    "2026-01-15T22:49:00+00:00"
-   ],
-   [
-    "2026-01-15T22:50:00+00:00",
-    "-7.1",
+    "0.4019",
     null,
     "2026-01-15T22:59:00+00:00"
    ]
   ],
-  "weather.forecast_home": [
+  "weather.weather": [
    [
     "2026-01-14T22:00:00+00:00",
     "cloudy",
diff --git a/tools/replay/cut_day.py b/tools/replay/cut_day.py
new file mode 100644
index 000000000..77f37de15
--- /dev/null
+++ b/tools/replay/cut_day.py
@@ -0,0 +1,201 @@
+#!/usr/bin/env python3
+"""Cut one replay fixture out of a sealed multi-day ``hpo-replay/1`` export.
+
+The export (``export.py --days 7``) is the owner's recorded week, and at over
+10 MB it is never committed. The replay lane reads a fixture in only three
+ways (``tests/replay.py:run_fixture``): each mapped input's state in force at
+a cycle instant, the weather entity's rows from that instant on (its
+forecast) and the price series' state in force at each quarter. All three
+instants lie on the quarter-hour grid that starts at the window's local
+midnight, so this keeps, of every input, only the rows in force at a grid
+instant -- what the lane reads, unchanged -- and drops the rest (a
+thermometer reporting every 30 s keeps 96 rows a day, not 3000). The price
+series and the weather, read ahead of the cycle, keep their grid rows to the
+export's end. ``--span`` cuts part of a day: the lane's cost scales with its
+cycles.
+
+The entities the integration publishes are left out, because the lane never
+reads them and they are what the build that recorded the day did -- often
+the defect itself. The one exception is the away override the owner set from
+the integration's own away switch and return-time entity: the user's
+command, not the integration's output. ``controls.away`` carries it as
+events ``[time, active, return_time]``; the lane replays each through
+``coordinator.async_set_away``, the call the switch and the datetime entity
+make. ``controls.reloads`` carries the minutes the integration reloaded in
+process -- every published entity ``unavailable``, every input readable --
+which the lane replays as a new entry handed the last publish. Both entities are masked to hashes, so they are found by what they
+did: the one published ``datetime`` entity is the return time, and the away
+switch is the one published switch that turned on within a few seconds of
+that return time being set. Anything else is refused.
+
+    python3 tools/replay/cut_day.py EXPORT.json --day 2026-10-30 --out tests/replay/F.json
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import sys
+from datetime import datetime, time, timedelta
+from pathlib import Path
+from zoneinfo import ZoneInfo
+
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE))
+import export  # noqa: E402
+
+GRID = timedelta(minutes=15)
+#: How close the away switch's turn-on and the return time's setting are.
+PAIRED = timedelta(seconds=10)
+
+
+def _ts(text: str) -> datetime:
+    return datetime.fromisoformat(text)
+
+
+def grid(start: datetime, end: datetime) -> list[datetime]:
+    """The quarter-hour instants of ``[start, end)``, stepped in UTC."""
+    out, t = [], start.astimezone(ZoneInfo("UTC"))
+    while t < end:
+        out.append(t)
+        t += GRID
+    return out
+
+
+def thinned(rows: list[list], instants: list[datetime]) -> list[list]:
+    """The rows in force at some instant of ``instants``, each carrying its full
+    attributes, then compacted as ``replay_doc.state_rows`` writes them."""
+    full, attrs = [], None
+    for updated, state, maybe, reported in rows:
+        attrs = maybe if maybe is not None else attrs
+        full.append((updated, state, attrs, reported))
+    keep, i = [], -1
+    for t in instants:
+        while i + 1 < len(full) and _ts(full[i + 1][0]) <= t:
+            i += 1
+        if i >= 0 and (not keep or keep[-1] is not full[i]):
+            keep.append(full[i])
+    return export._doc.state_rows(keep)
+
+
+def _changes(series: list[tuple[datetime, object]]) -> list[tuple[datetime, object]]:
+    """The points where a value changes, a restart's ``unavailable`` skipped: a
+    restart writes every entity again, which is no command."""
+    out, last = [], object()
+    for t, v in series:
+        if v != "unavailable" and v != last:
+            out.append((t, v))
+            last = v
+    return out
+
+
+def away_events(doc: dict, start: datetime, end: datetime) -> list[list]:
+    """The owner's away commands in ``[start, end)``, and the one in force at
+    ``start``, from the published away switch and return-time entity."""
+    states, published = doc["states"], doc["published"]
+    dates = [e for e in published if e.startswith("datetime.")]
+    if len(dates) != 1:
+        raise SystemExit(f"{len(dates)} published datetime entities; the away return "
+                         "time is the only one this integration publishes")
+    returns = [(_ts(r[0]), r[1]) for r in states.get(dates[0], [])]
+    set_at = [t for t, v in _changes(returns) if v not in ("unknown", None)]
+    switches = [e for e in published if e.startswith("switch.") and any(
+        v == "on" and any(abs(t - s) <= PAIRED for s in set_at)
+        for t, v in _changes([(_ts(r[0]), r[1]) for r in states.get(e, [])]))]
+    if len(switches) > 1 or (set_at and not switches):
+        raise SystemExit(f"{len(switches)} published switches turned on as the away "
+                         "return time was set; expected exactly one")
+    if not switches:
+        return []
+    events, last = [], None
+    for updated, state, _attrs, _rep in states[switches[0]]:
+        if state not in ("on", "off"):
+            continue  # a restart's ``unavailable``, not a command
+        t = _ts(updated)
+        ret = next((v for when, v in reversed(returns) if when <= t + PAIRED
+                    and v not in ("unknown", "unavailable")), None)
+        event = [t.isoformat(), state == "on", ret if state == "on" else None]
+        if event[1:] == (last or [None, None, None])[1:]:
+            continue
+        if t < start:
+            events = [[start.isoformat(), *event[1:]]] if event[1] else []
+        elif t < end:
+            events.append(event)
+        last = event
+    return events
+
+
+def reloads(doc: dict, start: datetime, end: datetime) -> list[str]:
+    """The minutes in ``[start, end)`` at which every entity the integration
+    publishes went ``unavailable`` while every input stayed readable: the
+    integration reloaded in process (an options save), not Home Assistant."""
+    def unavailable(entities: list[str]) -> dict[str, set[str]]:
+        out: dict[str, set[str]] = {}
+        for eid in entities:
+            for row in doc["states"].get(eid, []):
+                if row[1] == "unavailable" and start <= _ts(row[0]) < end:
+                    out.setdefault(_ts(row[0]).replace(second=0, microsecond=0).isoformat(),
+                                   set()).add(eid)
+        return out
+
+    published, inputs = unavailable(doc["published"]), unavailable(doc["inputs"])
+    return sorted(minute for minute, gone in published.items()
+                  if doc["published"] and len(gone) == len(doc["published"])
+                  and not inputs.get(minute))
+
+
+def _read_ahead(doc: dict, entity_id: str) -> bool:
+    return entity_id == doc.get("price_series_entity") or entity_id.startswith("weather.")
+
+
+def cut(doc: dict, day: str, warmup_days: int = 0,
+        span: tuple[time, time] | None = None) -> dict:
+    """``day``, local midnight to midnight -- or the local ``span`` of it --
+    after ``warmup_days`` whole days before it that the lane replays too."""
+    tz = ZoneInfo(doc["time_zone"])
+    first = datetime.fromisoformat(day).date()
+    begin, until = span or (time(0), None)
+    start = datetime.combine(first - timedelta(days=warmup_days), begin, tz)
+    end = (datetime.combine(first, until, tz) if until
+           else datetime.combine(first + timedelta(days=1), time(0), tz))
+    if not _ts(doc["window"]["start"]) <= start < end <= _ts(doc["window"]["end"]):
+        raise SystemExit(f"{day} is not inside the export's window {doc['window']}")
+    instants = grid(start, end)
+    # The price series and the weather are read ahead -- the day's quarters and
+    # the forecast's hours -- so they keep their rows to the export's end.
+    ahead = grid(start, _ts(doc["window"]["end"]))
+    out = {k: v for k, v in doc.items() if k not in ("states", "published")}
+    out["window"] = {"start": start.isoformat(), "end": end.isoformat()}
+    out["published"] = []
+    out["states"] = {eid: thinned(rows, ahead if _read_ahead(doc, eid) else instants)
+                     for eid, rows in doc["states"].items() if eid in doc["inputs"]}
+    out["controls"] = {"away": away_events(doc, start, end), "reloads": reloads(doc, start, end)}
+    return out
+
+
+def main(argv: list[str] | None = None) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
+    ap.add_argument("export", type=Path)
+    ap.add_argument("--day", required=True, help="the local date to cut, YYYY-MM-DD")
+    ap.add_argument("--warmup-days", type=int, default=0,
+                    help="whole days before --day the fixture starts at")
+    ap.add_argument("--span", help="local HH:MM-HH:MM of --day only, not the whole day")
+    ap.add_argument("--out", type=Path, required=True)
+    args = ap.parse_args(argv)
+    found = export.check_file(args.export)
+    if found:
+        raise SystemExit(f"{args.export} fails the export's check: " + "; ".join(found[:3]))
+    span = tuple(time.fromisoformat(x) for x in args.span.split("-")) if args.span else None
+    fixture = cut(json.loads(args.export.read_text()), args.day, args.warmup_days, span)
+    args.out.write_text(json.dumps(fixture, sort_keys=True, indent=1) + "\n")
+    found = export.check_file(args.out)
+    if found:
+        args.out.unlink()
+        raise SystemExit("the cut fails the export's check: " + "; ".join(found[:3]))
+    rows = sum(len(v) for v in fixture["states"].values())
+    print(f"wrote {args.out}: {len(fixture['states'])} inputs, {rows} rows, "
+          f"{len(fixture['controls']['away'])} away event(s), {args.out.stat().st_size} B")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/tools/replay/debug_replay.py b/tools/replay/debug_replay.py
index b083dc79b..d423a7740 100644
--- a/tools/replay/debug_replay.py
+++ b/tools/replay/debug_replay.py
@@ -160,7 +160,8 @@ def gate_checks() -> list[tuple[str, bool, str]]:
     start = datetime.fromisoformat(replay["window"]["start"])
     trimmed = trim_replay(replay, start, start + timedelta(hours=2))
     seam = offender_window(replay)
-    np_id = "sensor.nordpool_kwh_se3_sek"
+    # The fixture's own price entity: the export masks every id to its role.
+    np_id = replay["entry"]["data"]["price_entity"]
     filled_np = sum(1 for r in seam["states"].get(np_id, [])
                     if r[2] and r[2].get("raw_today"))
     stub._DISK.clear()
diff --git a/tools/replay/export.py b/tools/replay/export.py
index b070761d5..231b4303b 100644
--- a/tools/replay/export.py
+++ b/tools/replay/export.py
@@ -3,28 +3,40 @@
 
 Run on the owner's own Home Assistant box. It reads, and only reads:
 
-* ``<config>/home-assistant_v2.db`` -- the recorder's SQLite database, opened
-  with ``mode=ro`` (the ``states``, ``states_meta``, ``state_attributes`` and
-  ``schema_changes`` tables of the current schema; ``states_meta`` arrived in
-  schema 41, so an older database is refused by name);
+* the recorder's database (the ``states``, ``states_meta``,
+  ``state_attributes`` and ``schema_changes`` tables of the current schema;
+  ``states_meta`` arrived in schema 41, so an older database is refused by
+  name), SELECTs only. Which database: ``--db-url``, else ``--db``, else the
+  ``db_url`` configuration.yaml's ``recorder:`` names (inline or by
+  ``!include``, a ``!secret`` resolved through secrets.yaml), else
+  ``<config>/home-assistant_v2.db``. SQLite is opened with ``mode=ro``;
+  MySQL/MariaDB through the driver the Home Assistant container ships
+  (``MySQLdb``, else ``pymysql``), found at run time, in a read-only session.
+  The URL's credentials are never printed, logged or written: the recorder is
+  named as ``scheme://host/database``;
 * ``<config>/.storage/core.config_entries`` -- this integration's entry;
 * ``<config>/.storage/core.entity_registry`` -- the entities it publishes;
 * ``<config>/.storage/core.config`` -- the instance's time zone.
 
-It opens no socket. The standard library is all it imports, so it runs under
-the interpreter inside the Home Assistant container as it is -- and the rules
+It opens no socket but the database's, for a ``db_url`` recorder. The
+standard library is all it imports on the SQLite path, so it runs under the
+interpreter inside the Home Assistant container as it is -- and the rules
 below, which it loads by path from the integration's own
 ``custom_components/heatpump_optimizer/replay_doc.py`` (the checkout's, else a
 copy beside this file, else the one installed under ``/config``), because
 Download diagnostics writes the same document through the same rules (#2271).
 
 WHAT IT EXPORTS, for the window ``[end - days, end)`` in the instance's zone:
-every entity id the config entry maps (any value in ``data`` or ``options``
-spelled like an entity id -- thermometers, the price and weather entities, the
+every entity id the config entry maps under a key the installed integration
+reads (any value in ``data`` or ``options`` spelled like an entity id, under a
+``CONF_*`` key; a key a release retired is named on stderr and left out --
+thermometers, the price and weather entities, the
 pump's mode, switch, power and valve entities), the entities this integration
 publishes (from the registry; carried for comparison, never fed back), and any
 ``--extra-entity``. For each, the last state before the window and every state
-inside it.
+inside it. It refuses a window in which a mapped input has no state, updated
+or reported -- naming the inputs by their masked role and the recorder it read
+-- because a near-empty day passes every other rule.
 
 WITH THE TIBBER PRICE SOURCE the integration fetches prices itself, so the
 replay builds the day's series from a recorded price sensor
@@ -61,14 +73,16 @@ not its meaning, so a person reads the file before it is committed:
 
 * any text state, and any entry value under a key not naming an entity, of
   up to 40 characters that starts with a letter and breaks none of the rules
-  above -- several words and short numbers included: a full name, a street
-  and house number ("Storgatan 12"), a bare hostname, a random-looking token;
+  above -- several words and short numbers included: a full name, a bare
+  hostname, a random-looking token;
 * the same for units (up to 16 characters) and for ``device_class``,
   ``state_class`` and ``hvac_action`` (any ``[a-z_]`` word up to 32
   characters, a snake-case name included) -- and a select's option labels
   (no digits, otherwise the same);
-* entity ids, which the user named and which may embed a name, a street or a
-  device's MAC (``sensor.anna_storgatan_power``);
+* nothing of the entity ids, which the user named and which may embed a
+  name, a street or a device's MAC: ``replay_doc.mask`` renames every one to
+  a role (``sensor.price``) or a keyed hash, and a street and house number in
+  any text is dropped (``replay_doc.ADDRESS``);
 * numbers: a state, a numeric attribute or a price or forecast value is kept
   whatever it is, so a coordinate published as a sensor's state or a long
   number survives -- only keys named as coordinates are rounded.
@@ -84,12 +98,15 @@ on any violation; ``tests/replay.py`` runs it on every committed fixture.
 from __future__ import annotations
 
 import argparse
+import importlib
 import importlib.util
 import json
+import re
 import sqlite3
 import sys
 from datetime import datetime, time, timedelta, timezone
 from pathlib import Path
+from urllib.parse import parse_qs, unquote, urlsplit
 from zoneinfo import ZoneInfo
 
 DOMAIN = "heatpump_optimizer"
@@ -154,10 +171,25 @@ def check_file(path: Path, conf: frozenset[str] | None = None) -> list[str]:
         payload = json.loads(path.read_text())
     except (OSError, ValueError) as err:
         return [f"{path}: unreadable ({err})"]
-    found = violations(payload, conf if conf is not None else entry_keys(*default_const_paths()))
+    found = _doc.refusals(
+        payload, conf if conf is not None else entry_keys(*default_const_paths()))
     if not isinstance(payload, dict) or payload.get("format") != FORMAT:
         found.insert(0, f"format is not {FORMAT!r}")
-    return found
+    return found + untimed(payload)
+
+
+def untimed(payload: object) -> list[str]:
+    """A window bound or a row's update time that is not an ISO time: a replay
+    cannot place it, and a writer that nulled it wrote no recorded day."""
+    if not isinstance(payload, dict):
+        return []
+    window = payload.get("window") or {}
+    found = [f"window.{k}: not an ISO time" for k in ("start", "end")
+             if not (isinstance(window.get(k), str) and _doc.ISO_TIME.match(window[k]))]
+    bad = sum(1 for rows in (payload.get("states") or {}).values() for row in rows or []
+              if not (isinstance(row, list) and isinstance(row[0], str)
+                      and _doc.ISO_TIME.match(row[0])))
+    return found + ([f"states: {bad} row(s) with no ISO update time"] if bad else [])
 
 
 # --- reading the install -----------------------------------------------------
@@ -167,13 +199,157 @@ def _storage(config_dir: Path, name: str) -> dict:
     return json.loads((config_dir / ".storage" / name).read_text())["data"]
 
 
-def _open_ro(db: Path) -> sqlite3.Connection:
-    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)
-
-
-def _schema_version(conn: sqlite3.Connection) -> int:
-    row = conn.execute("SELECT MAX(schema_version) FROM schema_changes").fetchone()
-    return int(row[0] or 0)
+def _yaml_scalar(text: str) -> str:
+    """A one-line YAML scalar: quoted, or plain with its trailing comment cut."""
+    text = text.strip()
+    if text[:1] in "\"'" and len(text) > 1 and text[-1] == text[0]:
+        return text[1:-1]
+    return re.split(r"\s+#", text, maxsplit=1)[0].strip()
+
+
+def _top_key(text: str, key: str) -> tuple[str, list[str]] | None:
+    """A top-level ``key:``'s inline value and its indented block's lines."""
+    lines = text.splitlines()
+    for i, line in enumerate(lines):
+        found = re.match(rf"^{re.escape(key)}:(.*)$", line)
+        if found:
+            block = []
+            for nxt in lines[i + 1:]:
+                if nxt.strip() and not nxt[:1].isspace():
+                    break
+                block.append(nxt)
+            return found.group(1), block
+    return None
+
+
+def _secret(config_dir: Path, value: str) -> str:
+    tag = re.match(r"^!secret\s+(\S+)$", value)
+    if not tag:
+        return value
+    secrets = config_dir / "secrets.yaml"
+    hit = _top_key(secrets.read_text(), tag.group(1)) if secrets.is_file() else None
+    if hit is None:
+        raise SystemExit(f"configuration.yaml's recorder db_url names !secret "
+                         f"{tag.group(1)}, which {secrets} does not hold")
+    return _yaml_scalar(hit[0])
+
+
+def recorder_url(config_dir: Path) -> str | None:
+    """The ``db_url`` of configuration.yaml's top-level ``recorder:``, written
+    inline or in the file its ``!include`` names, a ``!secret`` resolved; None
+    without one, which is the default SQLite file."""
+    path = config_dir / "configuration.yaml"
+    hit = _top_key(path.read_text(), "recorder") if path.is_file() else None
+    if hit is None:
+        return None
+    inline, block = hit
+    include = re.match(r"^\s*!include\s+(\S+)", inline)
+    if include:
+        included = config_dir / include.group(1)
+        block = included.read_text().splitlines() if included.is_file() else []
+    depth = min((len(b) - len(b.lstrip()) for b in block if b.strip()), default=0)
+    for line in block:
+        found = re.match(rf"^ {{{depth}}}db_url:(.*)$", line)
+        if found:
+            return _secret(config_dir, _yaml_scalar(found.group(1)))
+    return None
+
+
+#: What a message calls a MySQL/MariaDB recorder. No text of the URL is in it:
+#: its host and database are the owner's, and a message only names the kind.
+MYSQL_LABEL = "MySQL/MariaDB database"
+#: A SQLite recorder named by a ``db_url`` is named by its kind alone, for the
+#: same reason: the URL may come from ``secrets.yaml``, and a message names a
+#: location only when the person typed it (``--db``, or the config directory).
+SQLITE_URL_LABEL = "SQLite database"
+
+
+class Recorder:
+    """The recorder database through DB-API, its SQL written once with ``?``
+    placeholders and rewritten to the driver's ``%s`` where it uses that."""
+
+    def __init__(self, conn, label: str, qmark: bool) -> None:
+        self.conn, self.label, self.qmark = conn, label, qmark
+
+    def rows(self, sql: str, params: tuple = ()) -> list[tuple]:
+        cur = self.conn.cursor()
+        try:
+            cur.execute(sql if self.qmark else sql.replace("?", "%s"), params)
+            return [tuple(r) for r in cur.fetchall()]
+        finally:
+            cur.close()
+
+    def columns(self, table: str) -> set[str]:
+        cur = self.conn.cursor()
+        try:
+            cur.execute(f"SELECT * FROM {table} WHERE 1 = 0")
+            return {d[0] for d in cur.description}
+        finally:
+            cur.close()
+
+    def close(self) -> None:
+        self.conn.close()
+
+
+#: The MySQL/MariaDB DB-API drivers, in the order tried: what SQLAlchemy's
+#: ``mysql://`` resolves to in the Home Assistant container, then the pure one.
+MYSQL_DRIVERS = ("MySQLdb", "pymysql")
+
+
+def _mysql(url: str) -> Recorder:
+    parts, label = urlsplit(url), MYSQL_LABEL
+    wanted = ("pymysql",) if parts.scheme.endswith("+pymysql") else MYSQL_DRIVERS
+    module = None
+    for name in wanted:
+        try:
+            module = importlib.import_module(name)
+            break
+        except ImportError:
+            continue
+    if module is None:
+        raise SystemExit(
+            f"the recorder {label} is MySQL/MariaDB, and reading it needs the "
+            f"{' or '.join(wanted)} module, which the Home Assistant container ships: "
+            "run this inside it (the SSH add-on's `docker exec -it homeassistant`)")
+    query = {k: v[-1] for k, v in parse_qs(parts.query).items()}
+    kwargs = {"host": parts.hostname or "localhost", "user": unquote(parts.username or ""),
+              "password": unquote(parts.password or ""), "database": parts.path.lstrip("/"),
+              "charset": query.get("charset", "utf8mb4")}
+    if parts.port:
+        kwargs["port"] = parts.port
+    if "unix_socket" in query:
+        kwargs["unix_socket"] = query["unix_socket"]
+    try:
+        conn = module.connect(**kwargs)
+        cur = conn.cursor()
+        cur.execute("SET SESSION TRANSACTION READ ONLY")
+        cur.close()
+    except Exception as err:  # noqa: BLE001 - its text can carry the user name
+        raise SystemExit(f"cannot open the recorder {label} read-only: "
+                         f"{type(err).__name__}") from None
+    return Recorder(conn, label, qmark=False)
+
+
+def open_recorder(config_dir: Path, db: Path | None, db_url: str | None) -> Recorder:
+    """The recorder ``--db-url``, ``--db``, configuration.yaml or the default names."""
+    url = db_url or (None if db else recorder_url(config_dir))
+    if url and not url.startswith("sqlite"):
+        if not url.split(":", 1)[0].split("+", 1)[0] in ("mysql", "mariadb"):
+            raise SystemExit("the recorder URL is neither SQLite nor "
+                             "MySQL/MariaDB, the two this export reads")
+        return _mysql(url)
+    label = None
+    if url:
+        db = Path(urlsplit(url).path[1:] if url.startswith("sqlite:////") else
+                  config_dir / urlsplit(url).path.lstrip("/"))
+        label = SQLITE_URL_LABEL
+    db = db or config_dir / "home-assistant_v2.db"
+    return Recorder(sqlite3.connect(f"file:{db}?mode=ro", uri=True),
+                    label or f"SQLite {db}", qmark=True)
+
+
+def _schema_version(rec: Recorder) -> int:
+    return int(rec.rows("SELECT MAX(schema_version) FROM schema_changes")[0][0] or 0)
 
 
 def _iso(ts: float | None) -> str | None:
@@ -182,12 +358,10 @@ def _iso(ts: float | None) -> str | None:
     return datetime.fromtimestamp(ts, timezone.utc).isoformat()
 
 
-def read_states(
-    conn: sqlite3.Connection, entity_id: str, start: float, end: float
-) -> list[list]:
+def read_states(rec: Recorder, entity_id: str, start: float, end: float) -> list[list]:
     """``replay_doc.state_rows`` of the entity's rows: the last before ``start``,
     then every one in ``[start, end)``."""
-    cols = {r[1] for r in conn.execute("PRAGMA table_info(states)")}
+    cols = rec.columns("states")
     reported = "s.last_reported_ts" if "last_reported_ts" in cols else "NULL"
     base = (
         f"SELECT s.last_updated_ts, {reported}, s.state, a.shared_attrs "
@@ -195,37 +369,50 @@ def read_states(
         "LEFT JOIN state_attributes a ON s.attributes_id = a.attributes_id "
         "WHERE m.entity_id = ? "
     )
-    before = conn.execute(
+    before = rec.rows(
         base + "AND s.last_updated_ts < ? ORDER BY s.last_updated_ts DESC LIMIT 1",
-        (entity_id, start),
-    ).fetchall()
-    inside = conn.execute(
+        (entity_id, start))
+    inside = rec.rows(
         base + "AND s.last_updated_ts >= ? AND s.last_updated_ts < ? "
         "ORDER BY s.last_updated_ts",
-        (entity_id, start, end),
-    ).fetchall()
+        (entity_id, start, end))
     return _doc.state_rows(
-        (_iso(updated), state, _attributes(shared), _iso(rep) if rep and rep > updated else None)
+        (_iso(updated), _text(state), _attributes(shared),
+         _iso(rep) if rep and rep > updated else None)
         for updated, rep, state, shared in before + inside
     )
 
 
-def _attributes(shared: str | None) -> dict:
+def _text(value: object) -> object:
+    """A MySQL driver can hand a text column back as bytes."""
+    return value.decode() if isinstance(value, (bytes, bytearray)) else value
+
+
+def _attributes(shared: object) -> dict:
     try:
-        return json.loads(shared) if shared else {}
+        return json.loads(_text(shared)) if shared else {}
     except ValueError:
         return {}
 
 
+def quiet_inputs(doc: dict) -> list[str]:
+    """The (masked) inputs with no state updated or reported inside the window."""
+    start = datetime.fromisoformat(doc["window"]["start"])
+    return [eid for eid in doc["inputs"] if not any(
+        any(t and datetime.fromisoformat(t) >= start for t in (row[0], row[3]))
+        for row in doc["states"].get(eid, []))]
+
+
 def build_export(
     config_dir: Path,
-    db: Path,
+    db: Path | None,
     days: int,
     end_date: str | None,
     entry_id: str | None,
     extra: list[str],
     price_entity: str | None,
     const: Path | None = None,
+    db_url: str | None = None,
 ) -> dict:
     entries = [
         e for e in _storage(config_dir, "core.config_entries")["entries"]
@@ -247,9 +434,18 @@ def build_export(
     end = datetime.combine(end_day, time(0), tz)
     start = datetime.combine(end_day - timedelta(days=days), time(0), tz)
 
-    inputs = mapped_entities(entry.get("data", {})) | mapped_entities(
-        entry.get("options", {})
-    )
+    # An input is an id under a key the installed integration reads: an old
+    # entry can keep a key a release retired (``heat_pump_entity``, v3.8.0),
+    # whose entity nothing reads and the recorder may long have stopped writing.
+    conf = entry_keys(*([const] if const else default_const_paths(config_dir)))
+    sections = [entry.get("data", {}), entry.get("options", {})]
+    retired = sorted({k for sec in sections for k, v in sec.items()
+                      if k not in conf and mapped_entities(v)})
+    if retired:
+        print(f"left out: entity id(s) under {len(retired)} entry key(s) this integration "
+              f"does not read ({', '.join(retired)})", file=sys.stderr)
+    inputs = set().union(*(mapped_entities({k: v for k, v in sec.items() if k in conf})
+                           for sec in sections))
     inputs |= set(extra)
     registry = _storage(config_dir, "core.entity_registry")["entities"]
     published = sorted(
@@ -259,9 +455,10 @@ def build_export(
         and e.get("config_entry_id") == entry.get("entry_id")
     )
     config = {**entry.get("data", {}), **entry.get("options", {})}
-    conn = _open_ro(db)
+    rec = open_recorder(config_dir, db, db_url)
+    print("reading the recorder", file=sys.stderr)
     try:
-        version = _schema_version(conn)
+        version = _schema_version(rec)
         if version < MIN_SCHEMA:
             raise SystemExit(
                 f"recorder schema {version} predates states_meta ({MIN_SCHEMA}); "
@@ -271,32 +468,49 @@ def build_export(
             price_entity = choose_price_entity(
                 config, registry,
                 lambda eid: any(_doc.numeric(row[1]) for row in read_states(
-                    conn, eid, start.timestamp(), end.timestamp())))
-            print(f"price series from the Tibber price sensor {price_entity} "
-                  "(--price-entity overrides)", file=sys.stderr)
+                    rec, eid, start.timestamp(), end.timestamp())))
+            print("price series from the one Tibber price sensor the registry and the "
+                  "recorder agree on, masked as sensor.price (--price-entity overrides)",
+                  file=sys.stderr)
         if price_entity:
             inputs.add(price_entity)
         states = {
-            eid: read_states(conn, eid, start.timestamp(), end.timestamp())
+            eid: read_states(rec, eid, start.timestamp(), end.timestamp())
             for eid in sorted(inputs | set(published))
         }
     finally:
-        conn.close()
+        rec.close()
 
     raw = _doc.document(
         time_zone=tz_name, window=(start.isoformat(), end.isoformat()),
         recorder_schema=version, entry=entry, inputs=inputs, published=published,
         price_series_entity=price_entity, states=states,
     )
+    quiet = quiet_inputs(raw)
+    if quiet:
+        raise SystemExit(
+            f"refusing to write: the recorder {rec.label} holds no state in "
+            f"[{start.isoformat()}, {end.isoformat()}) for {len(quiet)} of "
+            f"{len(raw['inputs'])} mapped input(s): {', '.join(quiet)} (masked ids; "
+            "is this the recorder Home Assistant writes?)")
     try:
-        return _doc.seal(raw, entry_keys(*([const] if const else default_const_paths(config_dir))))
+        sealed = _doc.seal(raw, conf)
     except _doc.Refused as err:
         raise SystemExit(str(err)) from None
+    if untimed(sealed):
+        raise SystemExit("refusing to write: sealing lost the document's times: "
+                         + "; ".join(untimed(sealed)))
+    return sealed
 
 def main(argv: list[str] | None = None) -> int:
     ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
     ap.add_argument("--config-dir", type=Path, default=Path("/config"))
-    ap.add_argument("--db", type=Path, help="default <config-dir>/home-assistant_v2.db")
+    ap.add_argument("--db", type=Path, help="a SQLite recorder file; default: the db_url "
+                    "configuration.yaml's recorder names, else "
+                    "<config-dir>/home-assistant_v2.db")
+    ap.add_argument("--db-url", help="the recorder's URL, over --db and configuration.yaml; "
+                    "prefer configuration.yaml's, which keeps the password off the "
+                    "command line")
     ap.add_argument("--days", type=int, default=7)
     ap.add_argument("--end", help="local date the window ends on (exclusive), YYYY-MM-DD")
     ap.add_argument("--entry-id", help="needed only with more than one entry")
@@ -325,13 +539,14 @@ def main(argv: list[str] | None = None) -> int:
         ap.error("--out is required unless --check is given")
     payload = build_export(
         args.config_dir,
-        args.db or args.config_dir / "home-assistant_v2.db",
+        args.db,
         args.days,
         args.end,
         args.entry_id,
         args.extra_entity,
         args.price_entity,
         args.const,
+        args.db_url,
     )
     args.out.write_text(json.dumps(payload, sort_keys=True, indent=1) + "\n")
     rows = sum(len(v) for v in payload["states"].values())

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
