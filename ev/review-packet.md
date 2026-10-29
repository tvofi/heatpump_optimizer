# Review packet #2948
head: d47fd1dfbc72bc5f0c2e80304a92ce5ffd7b2d71
base: d074b94b0626d2a66014e0629946c850ab283e05

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123408349030 success
arch-score / arch-score id=123426106459 success
arm id=123407865622 skipped
budget-raise-gate / budget-raise-gate id=123426141245 success
cancel-superseded id=123426067576 success
codeql id=123426101273 skipped
codeql / Analyze (actions) id=123426068601 success
codeql / Analyze (javascript-typescript) id=123426068691 success
codeql / Analyze (python) id=123426068551 success
gate id=123426071439 in_progress
governance id=123426112396 skipped
governance / delivery-status id=123426068542 success
governance / delivery-status-publish id=123426069087 skipped
governance / env-matrix id=123426068533 success
governance / instrument-self-tests id=123426068840 success
governance / policy-docs id=123426068851 success
governance / record id=123426069673 skipped
governance / wave-script id=123426068749 success
hassfest id=123426054127 skipped
hassfest / hassfest id=123426068058 success
kernel-points id=123426068073 skipped
pr-contract / pr-contract id=123426562298 in_progress
prelude id=123426068021 success
refresh id=123426093682 success
tests id=123426054562 skipped
tests / arch-instrument id=123426071911 success
tests / briefs id=123426068707 success
tests / browser id=123426071917 success
tests / ci-ratchet id=123426072476 skipped
tests / claims-autofix id=123426072525 skipped
tests / closure-scope id=123426068576 success
tests / closures id=123426071545 success
tests / closures-autofix id=123426071549 skipped
tests / coverage id=123426071808 success
tests / coverage-ratchet id=123426072214 success
tests / fast (3.14) id=123426071486 success
tests / graders-head-copy id=123426072335 success
tests / lane-proofs id=123426072209 success
tests / mutation id=123426068482 success
tests / mutation-autofix id=123426072053 skipped
tests / mutation-pins id=123426071523 skipped
tests / nightly-ha id=123426071165 skipped
tests / nightly-status id=123426068802 failure
tests / replay id=123426071654 skipped
tests / typing id=123426070928 success
validate id=123426127035 skipped
validate / validate-hacs id=123426068643 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/owed_unactioned.py --self-test
             `tools/audit/seat/owed_unactioned.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 66974d47312caa46e9817b9aeae7186e9764e560 --workdir <tmpdir>
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only 66974d47312caa46e9817b9aeae7186e9764e560
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/audit/seat/seat_venv.sh
             `tools/audit/seat/seat_venv.sh` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2948.md b/dev/programme/delivery/2948.md
new file mode 100644
index 000000000..48a4bf874
--- /dev/null
+++ b/dev/programme/delivery/2948.md
@@ -0,0 +1 @@
+- [#2948](https://github.com/tvofi/heatpump_optimizer/pull/2948) — **open**, owed_unactioned: key MERGE-READY and BLOCKED-UNFIXED as owed (P277) (R10-FLY-OWED-LEVELS)
diff --git a/tools/audit/seat/instruments/owed_unactioned.py.md b/tools/audit/seat/instruments/owed_unactioned.py.md
index 724ccedcb..db9f51db8 100644
--- a/tools/audit/seat/instruments/owed_unactioned.py.md
+++ b/tools/audit/seat/instruments/owed_unactioned.py.md
@@ -3,7 +3,9 @@
 - `owed_unactioned.py` — says which tick owed lines have outlived a sweep with
   no live acknowledgement (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). It reads
   the board's whole owed family (`-> OWED…`, `REVIEW OWED:`, `DISPATCH:`,
-  `OWNER FLAG:`, `DESIGN-BUILD:`), keys each line on its topic or `#<pr>`, and
+  `OWNER FLAG:`, `DESIGN-BUILD:`, `MERGE-READY:`, `BLOCKED-UNFIXED:`), keys
+  each line on its topic or `#<pr>` (a verdict level's head8 is its id, so a
+  new head re-raises), and
   counts in `--state` the boards each key has stood on. A key standing
   `--after` (2) sweeps is UNACTIONED unless an `--acks` file holds a live
   `OWED-ACK <UTC> <key> <id> [ttl=<h>] <reason>` whose id prefixes a sha the
diff --git a/tools/audit/seat/owed_unactioned.py b/tools/audit/seat/owed_unactioned.py
index 6cac6f1f4..79dc9575e 100644
--- a/tools/audit/seat/owed_unactioned.py
+++ b/tools/audit/seat/owed_unactioned.py
@@ -15,8 +15,11 @@ asked again. On 2026-10-28 the critical-path handoff r10-orch-beatd (#2916) stoo
 two handoffs routed to the opener at 10:55Z stood 8 h.
 
 WHAT IT DOES. It reads the tick board's owed family -- every `-> ` line that
-starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:` or `DESIGN-BUILD:` --
-and keys each on its obligation: the handoff topic, or `#<pr>`. The state file
+starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:`, `DESIGN-BUILD:`,
+`MERGE-READY:` or `BLOCKED-UNFIXED:` -- and keys each on its obligation: the
+handoff topic, or `#<pr>`. A verdict level (`MERGE-READY: #N <head8>`) carries
+its head8 as the id, so an acknowledgement covers one head and a new head
+re-raises. The state file
 counts the sweeps (distinct boards, by the board's provenance time) each key has
 stood on. A key standing on `--after` sweeps or more is UNACTIONED unless an
 acknowledgement line in an `--acks` file covers it now:
@@ -47,7 +50,7 @@ import re
 import sys
 import tempfile
 
-FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:)")
+FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|MERGE-READY:|BLOCKED-UNFIXED:)")
 BOARD = re.compile(r"^BOARD measured from origin/main at \S+, (\S+)")
 SHA = re.compile(r"\b[0-9a-f]{12,40}\b")
 REF = re.compile(r"\b(?:refs/heads/)?(?:handoff-body|handoff|design)/(\S+)")
@@ -77,6 +80,9 @@ def key_of(line: str) -> "tuple[str, list[str]]":
     m = re.match(r"REVIEW OWED: (#\d+)", body)
     if m:
         return m.group(1), shas
+    m = re.match(r"(?:MERGE-READY|BLOCKED-UNFIXED): (#\d+) ([0-9a-f]{8})$", body)
+    if m:
+        return m.group(1), [m.group(2)]
     m = re.match(r"OWED handoff: (\S+) ", body)
     if m:
         return m.group(1), shas
@@ -346,6 +352,30 @@ def self_test() -> int:
                          "-> OWED: OWED 2026-10-28T00:53:40Z push-stuck fix-r10-diag-ages 98785 STUCK 1641s"),
                     [pid], state="pid.json", after=1)
         check("null control: a whole non-sha id (a pid) still covers its key", rcj == 0)
+        # P277: the verdict levels, keyed `#<N>` with `<head8>` as the id
+        mr, bu = "-> MERGE-READY: #2896 5f3a5dd6", "-> BLOCKED-UNFIXED: #2933 1a2b3c4d"
+        for name, line, key, h8 in (("MERGE-READY", mr, "#2896", "5f3a5dd6"),
+                                    ("BLOCKED-UNFIXED", bu, "#2933", "1a2b3c4d")):
+            st = f"lv-{name}.json"
+            v0 = t0 + dt.timedelta(hours=5)
+            go(tick(v0, line), state=st)
+            rcl, ol = go(tick(v0 + dt.timedelta(minutes=10), line), state=st)
+            check(f"{name}: keyed {key} on its head8, unactioned on the second sweep",
+                  rcl == 1 and f"{key}  sweeps=2" in ol and f" {key} {h8} ttl=1" in ol)
+            lack = [f"OWED-ACK {(v0 + dt.timedelta(minutes=15)).isoformat()} {key} {h8} "
+                    "merge seat lands it after the train; waits on CI"]
+            rcm, om = go(tick(v0 + dt.timedelta(minutes=20), line), lack, state=st)
+            check(f"{name}: an OWED-ACK on #<N> <head8> covers it", rcm == 0 and "1 acknowledged" in om)
+            moved = line.replace(h8, "9e8d7c6b")
+            rcn, on = go(tick(v0 + dt.timedelta(minutes=30), moved), lack, state=st)
+            check(f"{name}: a new head8 re-raises", rcn == 1 and f"{key}  sweeps=4" in on
+                  and f" {key} 9e8d7c6b ttl=1" in on)
+        _, kv = board(tick(t0, review, mr))
+        check("REVIEW OWED and MERGE-READY on one pull request are one key",
+              set(kv) == {"#2896"} and kv["#2896"]["shas"] == ["5f3a5dd615b5", "5f3a5dd6"])
+        check("null control: a board without the levels keys as before", set(board(
+            tick(t0, beatd, held, disp, review, event))[1]) == {"r10-orch-beatd", "triage-s7-batch49",
+                                                                 "#2896", "#2920"})
         with open(os.path.join(d, "entry.json"), "w", encoding="utf-8") as fh:
             json.dump({"board": None, "keys": {"r10-orch-beatd": {"sweeps": 2}}}, fh)
         check("a malformed state entry: exit 2", go(tick(t0, beatd), state="entry.json")[0] == 2)

