# Review packet #3910
head: 454abc83f05e3e9d290ad4e68c4e6b36eca69897
base: 1d3077736d4a7ced6ec15d9aec29f6bcf40fbae8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139875210830 success
arch-score / arch-score id=139874751857 success
arm id=139873760383 skipped
budget-raise-gate / budget-raise-gate id=139874751882 success
cancel-superseded id=139873813718 success
codeql id=139874755685 skipped
codeql / Analyze (actions) id=139874708532 success
codeql / Analyze (javascript-typescript) id=139874708437 success
codeql / Analyze (python) id=139874708480 success
gate id=139899254162 cancelled
governance id=139874753895 skipped
governance / env-matrix id=139874708774 success
governance / instrument-self-tests id=139874708826 success
governance / policy-docs id=139874708572 success
governance / record id=139874710859 skipped
governance / wave-script id=139874708978 success
hassfest id=139874753905 skipped
hassfest / hassfest id=139874708535 success
kernel-points id=139874754361 skipped
pr-contract id=139899253136 skipped
prelude id=139873813849 success
refresh id=139873813200 success
sweep-self id=139899254250 cancelled
tests id=139874753799 skipped
tests / arch-instrument id=139875301865 success
tests / briefs id=139874708616 success
tests / browser id=139875301798 success
tests / ci-ratchet id=139899194368 skipped
tests / claims-autofix id=139893496298 skipped
tests / closure-scope id=139874708497 success
tests / closures id=139875301936 success
tests / closures-autofix id=139890549930 skipped
tests / coverage id=139875301852 success
tests / coverage-ratchet id=139899192483 cancelled
tests / fast (3.14) id=139875301800 success
tests / graders-head-copy id=139899192623 cancelled
tests / lane-proofs id=139899192260 cancelled
tests / mutation id=139874708441 failure
tests / mutation-autofix id=139895786196 success
tests / mutation-pins (1) id=139875236057 success
tests / nightly-ha id=139875304012 skipped
tests / nightly-status id=139874709007 failure
tests / replay id=139875303899 skipped
tests / typing id=139875301829 success
validate id=139874754603 skipped
validate / validate-hacs id=139874709090 success

## Refusals
moved-head: the pull request's head is ea316e99f52dfccc38c08b09a7abddf49a5297a3, not the dispatched 454abc83f05e3e9d290ad4e68c4e6b36eca69897
head-note: ## Head does not name the dispatched head 454abc83f05e3e9d290ad4e68c4e6b36eca69897 -- repair: the body's ## Head must name 454abc83f05e3e9d290ad4e68c4e6b36eca69897; `tools/audit/seat/update_pr.sh fix/r11-late-p2-replay-finite - <body-file>` (PR branch fix/r11-late-p2-replay-finite)
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `tests / coverage-ratchet` is not named in ## Red checks
required-red: required context `gate` concluded failure at 454abc83f05e3e9d290ad4e68c4e6b36eca69897 (merge_train.py classify --pr reads RED pending: none red: gate)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show 872510cd3e:dev/audit/rounds/round11/sweep/P2/D14-sweep-P2/probes_p2.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff dbdc71faea358a95a7b33840ed252b0d8a646a31
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff dbdc71faea358a95a7b33840ed252b0d8a646a31 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 4 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json b/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json
deleted file mode 100644
index 2c0bd47d50..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_number BOOLOP 59b66cd2",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if isinstance(value, (int, float)) and not isinstance(value, bool):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: BOOLOP (`if isinstance(value, (int, float)) or not isinstance(value, bool):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json b/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json
deleted file mode 100644
index b7c3d8f6ba..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_number GUARD_OFF 59b66cd2",
-  "killed_by": "tests/entities.py",
-  "old": "    if isinstance(value, (int, float)) and not isinstance(value, bool):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head 454abc83f05e3e9d290ad4e68c4e6b36eca69897, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/replay_doc.py b/custom_components/heatpump_optimizer/replay_doc.py
index 374f949139..0509269a65 100644
--- a/custom_components/heatpump_optimizer/replay_doc.py
+++ b/custom_components/heatpump_optimizer/replay_doc.py
@@ -241,11 +241,12 @@ def clean_value(node: object, dropped: list[str]) -> object:
                 continue
             if _is_coordinate(key) and isinstance(value, (int, float, str)) \
                     and not isinstance(value, bool):
-                try:
+                if numeric(value):
                     out[key] = round(float(value), MAX_COORDINATE_DECIMALS)
-                except ValueError:
-                    dropped.append(str(value))
-                    out[key] = None
+                    continue
+                if isinstance(value, str):
+                    dropped.append(value)
+                out[key] = None
                 continue
             out[key] = clean_value(value, dropped)
         return out
@@ -264,9 +265,10 @@ def clean_value(node: object, dropped: list[str]) -> object:
 
 
 def _number(value: object) -> object:
+    """A real number ``numeric`` admits: NaN and an infinity are cut."""
     if value is None:
         return None
-    if isinstance(value, (int, float)) and not isinstance(value, bool):
+    if isinstance(value, (int, float)) and numeric(value):
         return value
     return _DROP
 
diff --git a/dev/programme/delivery/3910.md b/dev/programme/delivery/3910.md
new file mode 100644
index 0000000000..1d38e09de1
--- /dev/null
+++ b/dev/programme/delivery/3910.md
@@ -0,0 +1 @@
+- [#3910](https://github.com/tvofi/heatpump_optimizer/pull/3910) — **open**, Cut non-finite numbers in replay_doc (R11-LATE-P2-REPLAY-FINITE)
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index 48c0d81719..6a71a3baa0 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -1192,6 +1192,24 @@ R.check(
     and not any(replay_doc.numeric(v) for v in (True, "nan", "inf", float("nan"))),
     f"{[(v, a, b) for v, a, b in _numeric_split if a != b]}",
 )
+# R11-LATE-P2-REPLAY-FINITE: _number is the shape of every numeric attribute
+# and price-series value. It keeps a real number exactly when numeric does.
+# Its text and bool refusals are its own shape's: the probes compare numbers.
+_number_split = [(v, replay_doc._number(v) is not _D,
+                  isinstance(v, (int, float)) and replay_doc.numeric(v))
+                 for v in _numeric_probes if v is not None]
+_nan_rows = [{"start": "2026-10-18T00:00:00+00:00", "value": v}
+             for v in (float("nan"), float("inf"), float("-inf"), 1.5)]
+R.check(
+    "replay_doc._number keeps a value exactly when it is a number replay_doc.numeric "
+    "admits, so a NaN or infinite attribute or series value is cut",
+    all(a == b for _, a, b in _number_split)
+    and replay_doc._number(None) is None
+    and [replay_doc._number(v) for v in (float("nan"), float("inf"), float("-inf"))]
+    == [_D, _D, _D]
+    and replay_doc._series(_nan_rows) == [{"start": "2026-10-18T00:00:00+00:00", "value": 1.5}],
+    f"{[(v, a, b) for v, a, b in _number_split if a != b]} {replay_doc._series(_nan_rows)}",
+)
 R.check(
     "replay_doc.json_decimal_places counts the JSON spelling's decimals, a string's as "
     "written, and answers None for a bool, a word or a non-number",
@@ -1213,6 +1231,16 @@ R.check(
     f"kept keys {sorted(_cleaned)}; "
     + _unrecorded(["s3cret-value", "north", "https://nas.example.se/cam"], _dropped),
 )
+_coord_drop: list = []
+R.check(
+    "replay_doc.clean_value nulls a coordinate replay_doc.numeric refuses, NaN and "
+    "an infinity in any spelling, and records the text it nulled",
+    replay_doc.clean_value({"latitude": "nan", "lat": float("inf"), "longitude": "1e400",
+                            "lon": float("-inf"), "lng": "north"}, _coord_drop)
+    == {"latitude": None, "lat": None, "longitude": None, "lon": None, "lng": None}
+    and _coord_drop == ["nan", "1e400", "north"],
+    f"{_coord_drop}",
+)
 _secret_drop: list = []
 replay_doc.clean_value({"api_key": None, "password": True, "auth": {"user": "bob123456"},
                         "token": ["abc123456", 42]}, _secret_drop)
diff --git a/tests/entities.py b/tests/entities.py
index f3d2a59eae..935362f5b6 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4427,6 +4427,14 @@ _P2_CENSUSES = {
     "replay_numeric_domain": (
         "tests/debug_collect.py",
         "replay_doc.numeric answers exactly as const.finite_float on every probe"),
+    # R11-LATE-P2-REPLAY-FINITE: replay_doc's number shape and its coordinate
+    # cut keep exactly what numeric admits.
+    "replay_number_finite": (
+        "tests/debug_collect.py",
+        "replay_doc._number keeps a value exactly when it is a number replay_doc.numeric"),
+    "replay_coordinate_finite": (
+        "tests/debug_collect.py",
+        "replay_doc.clean_value nulls a coordinate replay_doc.numeric refuses"),
     # D7-s3-03: every reader of the plan step covering now takes plan_step's
     # index; the census drives the four on one plan, past its end included.
     "plan_step_covering": (
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json b/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json
deleted file mode 100644
index 2c0bd47d50..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_number.BOOLOP.59b66cd2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_number BOOLOP 59b66cd2",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if isinstance(value, (int, float)) and not isinstance(value, bool):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: BOOLOP (`if isinstance(value, (int, float)) or not isinstance(value, bool):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json b/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json
deleted file mode 100644
index b7c3d8f6ba..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/_number.GUARD_OFF.59b66cd2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_number GUARD_OFF 59b66cd2",
-  "killed_by": "tests/entities.py",
-  "old": "    if isinstance(value, (int, float)) and not isinstance(value, bool):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
