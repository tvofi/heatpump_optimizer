# Review packet #3232
head: 28e4375441e6011083dce278e3ffdee9cbbbf26f
base: 80016a71f567d936450d8708abcbb79d9e8071d7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128271923258 success
arch-score / arch-score id=128305317011 success
arm id=128271631899 skipped
budget-raise-gate / budget-raise-gate id=128305317165 success
cancel-superseded id=128305345288 success
codeql id=128305335909 skipped
codeql / Analyze (actions) id=128292503964 success
codeql / Analyze (javascript-typescript) id=128292503971 success
codeql / Analyze (python) id=128292504049 success
gate id=128305316658 success
governance id=128305317134 skipped
governance / delivery-status id=128292504024 success
governance / delivery-status-publish id=128292505233 skipped
governance / env-matrix id=128292504003 success
governance / instrument-self-tests id=128292504040 success
governance / policy-docs id=128292503991 success
governance / record id=128292505140 skipped
governance / wave-script id=128292504038 success
hassfest id=128305335972 skipped
hassfest / hassfest id=128292504005 success
kernel-points id=128305343901 skipped
pr-contract id=128305317224 skipped
pr-contract / pr-contract id=128303396284 success
prelude id=128305316806 success
refresh id=128305316606 success
tests id=128305316893 skipped
tests / arch-instrument id=128292633019 success
tests / briefs id=128292504006 success
tests / browser id=128292633094 success
tests / ci-ratchet id=128300689909 skipped
tests / claims-autofix id=128292745490 skipped
tests / closure-scope id=128292503951 success
tests / closures id=128292633115 success
tests / closures-autofix id=128300689908 skipped
tests / coverage id=128292633850 skipped
tests / coverage-ratchet id=128292634834 skipped
tests / fast (3.14) id=128292633069 success
tests / graders-head-copy id=128292633322 success
tests / lane-proofs id=128292744137 success
tests / mutation id=128292503945 success
tests / mutation-autofix id=128303395574 skipped
tests / mutation-pins id=128303395485 skipped
tests / nightly-ha (2025.2.0) id=128292633030 success
tests / nightly-ha (stable) id=128292633198 success
tests / nightly-status id=128292504011 success
tests / replay id=128292633083 success
tests / typing id=128292633051 success
validate id=128305317059 skipped
validate / validate-hacs id=128292503984 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item a08541b3: dismissed:instrument class outside this PR's diff; the orchestrator routes it to the mutation-tooling owner or refuses it
NOTE body item 979393b1: dismissed:orchestrator's dispatch, not a finding
NOTE body item 4e05a0b0: dismissed:orchestrator's dispatch, not a finding
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 -I tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/worker_deadlines.py
             `tests/worker_deadlines.py` is in the tree at this head
  unverified git diff --stat origin/main...HEAD -- tests/golden VERSION RELEASE_NOTES.md
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json
new file mode 100644
index 000000000..5e93dda30
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST 862cfb54",
+  "killed_by": "tests/features.py",
+  "old": "PROCESS_REPLY_TIMEOUT_S = 1800.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROCESS_REPLY_TIMEOUT_S = 3600.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json
new file mode 100644
index 000000000..b0f709249
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST c828ef01",
+  "killed_by": "tests/features.py",
+  "old": "_SHUTDOWN_LOCK_TIMEOUT_S = 5.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_SHUTDOWN_LOCK_TIMEOUT_S = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json
new file mode 100644
index 000000000..ea93f9015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST cb651c79",
+  "killed_by": "tests/features.py",
+  "old": "_REPLY_FRAME_TIMEOUT_S = 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_REPLY_FRAME_TIMEOUT_S = 120.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json
new file mode 100644
index 000000000..3d312fc34
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_await_off_loop RAISE_DEL 7456231f",
+  "killed_by": "tests/features.py",
+  "old": "        raise",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RAISE_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json
new file mode 100644
index 000000000..87baf9630
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_await_off_loop RETURN_DEL 48ca4fb4",
+  "killed_by": "tests/features.py",
+  "old": "    return result",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json
new file mode 100644
index 000000000..d6bb54238
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader RETURN_DEL 909c8492",
+  "killed_by": "tests/features.py",
+  "old": "    return SimpleNamespace(read=read, readline=readline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json
new file mode 100644
index 000000000..11612813b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND 821e5720",
+  "killed_by": "tests/features.py",
+  "old": "        if size > left_bytes:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if size >= left_bytes:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json
new file mode 100644
index 000000000..c68507a8d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND eef3603a",
+  "killed_by": "tests/features.py",
+  "old": "        while size > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`while size >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json
new file mode 100644
index 000000000..921c281f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF 821e5720",
+  "killed_by": "tests/features.py",
+  "old": "        if size > left_bytes:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json
new file mode 100644
index 000000000..3f025320d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF 9aafe706",
+  "killed_by": "tests/features.py",
+  "old": "            if not chunk:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json
new file mode 100644
index 000000000..1e340c0d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF fb715113",
+  "killed_by": "tests/features.py",
+  "old": "            if left_s <= 0 or not _reply_ready(fd, left_s):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json
new file mode 100644
index 000000000..66c73fc21
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read RETURN_DEL e9d62676",
+  "killed_by": "tests/features.py",
+  "old": "        return b\"\".join(chunks)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json
new file mode 100644
index 000000000..36f010896
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.readline BOOLOP 65afbd87",
+  "killed_by": "tests/features.py",
+  "old": "        while not line.endswith(b\"\\n\") and (byte := read(1)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`while not line.endswith(b\"\\n\") or (byte := read(1)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json
new file mode 100644
index 000000000..828f38f17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.readline RETURN_DEL e4edcdb0",
+  "killed_by": "tests/features.py",
+  "old": "        return line",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json
new file mode 100644
index 000000000..42a0347cb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_read_reply GUARD_OFF 6c857468",
+  "killed_by": "tests/features.py",
+  "old": "    if not _reply_ready(stdout, timeout):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json
new file mode 100644
index 000000000..3093eb454
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_read_reply RETURN_DEL 65f007ab",
+  "killed_by": "tests/features.py",
+  "old": "    return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json b/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json
new file mode 100644
index 000000000..cdb82c7da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_reply_ready RETURN_DEL 0023660a",
+  "killed_by": "tests/features.py",
+  "old": "        return bool(selector.select(timeout_s))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json b/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json
new file mode 100644
index 000000000..2b616679d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_run_in_process RAISE_DEL d876a130",
+  "killed_by": "tests/features.py",
+  "old": "                raise",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RAISE_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json b/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json
new file mode 100644
index 000000000..3c0cb4521
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_shutdown_process_pool GUARD_OFF 9403447b",
+  "killed_by": "tests/features.py",
+  "old": "    if not _PROCESS_LOCK.acquire(timeout=_SHUTDOWN_LOCK_TIMEOUT_S):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json b/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json
new file mode 100644
index 000000000..6e8946c28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_diagnose_interval GUARD_OFF 7beb0a59",
+  "killed_by": "tests/features.py",
+  "old": "    if failed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json b/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json
new file mode 100644
index 000000000..f944ca9a1
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND fb715113",
+  "old": "            if left_s <= 0 or not _reply_ready(fd, left_s):",
+  "reason": "CMP_BOUND (`left_s < 0`) differs from `left_s <= 0` only when the remaining time is exactly 0.0, a float difference of two monotonic readings. Even then the outcome is unchanged: `_reply_ready(fd, 0.0)` polls without blocking, so a quiet writer still raises ProcessWorkerTimeout on that pass, and a ready descriptor yields one non-blocking read before the next pass sees a negative remainder and raises. Measured: `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` drove this mutant and reported `coordinator.py:1948 CMP_BOUND -- lives`, while GUARD_OFF on the same line was killed (tests/features.py rc=1 failed=2).",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 09c3beb21..7bcdcea16 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -21,9 +21,12 @@ import logging
 import math
 import os
 import pickle
+import selectors
 import subprocess
 import sys
 import threading
+import time
+from types import SimpleNamespace
 from bisect import bisect_right
 from dataclasses import dataclass, field, replace
 from operator import attrgetter
@@ -790,6 +793,28 @@ SOLVE_FAILURE_ISSUE_COUNT = 3
 # hass.data, not a process global, so a later test's new hass is not charged
 # for an earlier one.
 WORKER_FALLBACK_CAP = 3
+# How long ``_run_in_process`` waits for the worker's reply before it reaps
+# the worker as hung. Far above any real solve: on a Raspberry Pi 4 the
+# spread measured on one install over three days was a median of 18 s and a maximum
+# of 426 s, while the hang this bounds ran for about 55 minutes with one core
+# busy. A module global read at call time, so a test can shorten it.
+PROCESS_REPLY_TIMEOUT_S = 1800.0
+# How long the stop path waits for ``_PROCESS_LOCK`` after killing the worker,
+# and how long a timed-out reply's reap waits for the killed child. The swap
+# is only bookkeeping, and neither a read the kill did not break nor a child
+# slow to die may hold a solve or Home Assistant's shutdown hostage.
+_SHUTDOWN_LOCK_TIMEOUT_S = 5.0
+# How long the reply frame may take to arrive once its first byte has. The
+# worker serialises its whole reply before writing it, so the frame then flows
+# at pipe speed (a 50 MB reply round-trips in about half a second); this only
+# bounds a writer stopped mid-frame (SIGSTOP, a stalled host). Module global,
+# read at call time, so a test can shorten it.
+_REPLY_FRAME_TIMEOUT_S = 60.0
+# The most the reply frame may carry, counted on what the unpickler asks for.
+# The bytes come from the worker, so a frame's declared lengths are bounded
+# before they are allocated. Module global, read at call time, so a test can
+# shorten it.
+_REPLY_FRAME_MAX_BYTES = 256 * 1024 * 1024
 
 
 def _republish_handover_ages(coord: Any, handover: Payload) -> Payload:
@@ -1758,6 +1783,16 @@ class ProcessWorkerUnavailable(RuntimeError):
     """
 
 
+class ProcessWorkerTimeout(ProcessWorkerUnavailable):
+    """The worker took the job and gave no reply within the deadline.
+
+    Not a transport fault that an in-process solve would route around: the
+    same job would occupy an executor thread just as long. The worker has
+    been reaped; the caller keeps the last plan and the next cycle spawns a
+    fresh worker.
+    """
+
+
 def _worker_env() -> dict[str, str]:
     """Make the package importable in the child under BOTH of its names.
 
@@ -1849,13 +1884,22 @@ def _shutdown_process_pool(*, at_exit: bool = False) -> None:
                 worker.wait(timeout=2)
             except Exception:  # noqa: BLE001
                 worker.kill()
-    with _PROCESS_LOCK:
+    # Bounded: a read the kill above did not break would otherwise hold the
+    # stop for as long as it held the lock (observed: the shutdown ran into
+    # the supervisor's timeout). Skipping the swap then only leaves a handle
+    # to a dead child, which ``_ensure_worker`` replaces on its next call.
+    if not _PROCESS_LOCK.acquire(timeout=_SHUTDOWN_LOCK_TIMEOUT_S):
+        _LOGGER.debug("Solve worker lock still held at stop; skipping the handle swap")
+        return
+    try:
         # Only the swap is locked, and only when this reap's own handle is
         # still the installed one: a solve that died on the killed pipes has
         # already cleared it, and a worker spawned after that must not be
         # clobbered by a stop it outlived.
         if _PROCESS_WORKER is worker:
             _PROCESS_WORKER = None
+    finally:
+        _PROCESS_LOCK.release()
 
 
 @callback
@@ -1878,6 +1922,91 @@ def async_register_worker_shutdown(hass: HomeAssistant, entry: HeatPumpOptimizer
     )
 
 
+def _reply_ready(stream: Any, timeout_s: float) -> bool:
+    """Whether ``stream`` turns readable within ``timeout_s``.
+
+    A selector, never ``select.select``: that refuses any descriptor at or
+    above FD_SETSIZE (1024), and Home Assistant raises its own soft fd limit
+    past it, so a worker respawned into a full fd table read as a transport
+    fault and every solve fell back in process.
+    """
+    with selectors.DefaultSelector() as selector:
+        selector.register(stream, selectors.EVENT_READ)
+        return bool(selector.select(timeout_s))
+
+
+def _frame_reader(fd: int, timeout_s: float) -> SimpleNamespace:
+    """``pickle.load``'s file over the reply pipe, every read under one deadline.
+
+    Reads the raw descriptor, never the buffered stream, whose held bytes a
+    selector cannot see. It has no ``peek``, so the unpickler asks for
+    exactly the bytes it consumes and nothing past the frame is taken.
+    """
+    deadline = time.monotonic() + timeout_s
+    left_bytes = _REPLY_FRAME_MAX_BYTES
+
+    def read(size: int) -> bytes:
+        nonlocal left_bytes
+        # Refused on the size asked for, before ``os.read`` allocates it: a
+        # frame's declared lengths come from the worker and are not trusted.
+        # Not a timeout, so the transport route reaps the worker mid-frame.
+        if size > left_bytes:
+            raise ValueError(
+                f"reply frame exceeds {_REPLY_FRAME_MAX_BYTES} bytes"
+            )
+        left_bytes -= size
+        chunks: list[bytes] = []
+        while size > 0:
+            # Checked here, not left to the wait: a descriptor at end of
+            # stream always reads as ready, so the wait alone never expires.
+            left_s = deadline - time.monotonic()
+            if left_s <= 0 or not _reply_ready(fd, left_s):
+                raise ProcessWorkerTimeout(
+                    f"process worker stopped mid-reply: the frame did not "
+                    f"arrive within {timeout_s:g} s"
+                )
+            chunk = os.read(fd, size)
+            if not chunk:
+                break  # end of stream: the unpickler reports the short frame
+            chunks.append(chunk)
+            size -= len(chunk)
+        return b"".join(chunks)
+
+    def readline() -> bytes:
+        # Only text opcodes ask, and the worker's binary protocol sends none.
+        line = b""
+        while not line.endswith(b"\n") and (byte := read(1)):
+            line += byte
+        return line
+
+    return SimpleNamespace(read=read, readline=readline)
+
+
+def _read_reply(stdout: Any) -> Any:
+    """The worker's ``(status, payload)``, its wait and its frame each bounded.
+
+    The worker serialises its whole reply before writing it
+    (``process_worker._dump``), so a readable pipe means the job is done.
+    Waiting for that with a deadline instead of blocking in ``pickle.load``
+    matters because a worker alive but silent never raises, and holding
+    ``_PROCESS_LOCK`` in that read wedged every later solve, every reload and
+    the stop path until a restart. The frame then has its own deadline, so a
+    writer stopped mid-reply (SIGSTOP, a stalled host) cannot hold it either.
+    A stream with no descriptor (an in-memory one) has nothing to wait on
+    and is read directly; the worker's pipe always has one.
+    """
+    try:
+        fd = stdout.fileno()
+    except (AttributeError, OSError, ValueError):
+        return pickle.load(stdout)
+    timeout = PROCESS_REPLY_TIMEOUT_S
+    if not _reply_ready(stdout, timeout):
+        raise ProcessWorkerTimeout(
+            f"process worker gave no reply within {timeout:g} s"
+        )
+    return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))
+
+
 def _run_in_process(fn: Callable[..., Any], args: tuple[Any, ...]) -> Any:
     """Run ``fn(*args)`` in the process worker. ``fn`` must be picklable.
 
@@ -1908,7 +2037,19 @@ def _run_in_process(fn: Callable[..., Any], args: tuple[Any, ...]) -> Any:
                 raise ProcessWorkerUnavailable("process worker pipes missing")
             stdin.write(job)
             stdin.flush()
-            status, payload = pickle.load(stdout)
+            try:
+                status, payload = _read_reply(stdout)
+            except ProcessWorkerTimeout:
+                _PROCESS_WORKER = None
+                # Bounded too: a child the kill does not end at once (one
+                # stuck in the kernel) must not turn this into the same
+                # unbounded wait one line further down.
+                try:
+                    worker.kill()
+                    worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)
+                except Exception:  # noqa: BLE001 - must not mask the timeout
+                    pass
+                raise
         except ProcessWorkerUnavailable:
             # Already the class the fallback route catches; rewrapping it
             # would bury the pipes/load-err cause under a generic one.
@@ -1953,12 +2094,24 @@ async def _await_off_loop(hass: HomeAssistant, fn: Callable[..., Any], *args: An
 
     The process worker first; a worker that cannot carry the job degrades to
     the executor, the #511 trade -- a GIL-holding thread, never the loop.
+    A job that outran the reply deadline is not rerun there: the same job
+    would hold an executor thread and a core with no deadline at all. It
+    raises to the caller, which skips its job this cycle (the replay and the
+    sensor advisor) or fails the cycle through ``_note_solve_failure`` (away
+    recovery, sysid); the warning is held per job until one completes.
     """
+    name = fn.__qualname__
+    key = f"off_loop_timeout:{name}"
     try:
-        return await _await_process(hass, fn, *args)
+        result = await _await_process(hass, fn, *args)
+    except ProcessWorkerTimeout as err:
+        log_held(hass, key, True, "%s; %s skipped this cycle", err, name)
+        raise
     except ProcessWorkerUnavailable as err:
         _LOGGER.debug("Process worker unusable (%s); using the executor", err)
         return await hass.async_add_executor_job(fn, *args)
+    log_held(hass, key, False)
+    return result
 
 
 async def _sysid_step_off_loop(
@@ -2123,6 +2276,15 @@ async def _await_optimize(
     entry_id = _CURRENT_ENTRY_ID.get()
     try:
         result = await _await_process(hass, optimize_in_process, optimizer, inputs)
+    except ProcessWorkerTimeout as err:
+        # Held, not per cycle: a worker that keeps timing out warns once and
+        # says "Resolved" on the first solve it carries again (R10 N-log-flood).
+        log_held(hass, f"process_worker_timeout:{entry_id}", True,
+                 "%s; keeping the last plan, a fresh worker starts next cycle", err)
+        _raise_update_failed(
+            "process_worker_timeout", f"{err}; the last plan stays in effect", err,
+            minutes=f"{PROCESS_REPLY_TIMEOUT_S / 60:.0f}",
+        )
     except ProcessWorkerUnavailable as err:
         _note_worker_fallback(hass, err, entry_id)
         n = _bump_worker_fallback(hass, entry_id)
@@ -2135,6 +2297,7 @@ async def _await_optimize(
             optimize_in_process, optimizer, inputs
         )
     _clear_worker_fallback(hass, entry_id)
+    log_held(hass, f"process_worker_timeout:{entry_id}", False)
     return result
 
 
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index 18718ca6f..8d774f6a6 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -85,6 +85,7 @@ from .config_flow import identity_update
 from .coordinator import (
     HeatPumpOptimizerConfigEntry,
     HeatPumpOptimizerCoordinator,
+    ProcessWorkerUnavailable,
     async_adopt_heat_loss_refit,
     async_factory_reset,
 )
@@ -1254,10 +1255,26 @@ async def handle_diagnose_interval(hass: HomeAssistant, call: ServiceCall) -> di
     """Attribute the last settled interval's residual (T6 #52)."""
     target_entry = dict(call.data).get("entry_id")
     reports: dict[str, Any] = {}
+    failed: dict[str, str] = {}
     for entry_id, coord in _manual_targets(hass, target_entry):
         # The button's snapshot path; a bound method on the executor read
         # live coordinator state off the loop (#1529).
-        reports[entry_id] = await coord.async_diagnose_interval()
+        try:
+            reports[entry_id] = await coord.async_diagnose_interval()
+        except ProcessWorkerUnavailable as err:
+            # A worker that timed out or could not run the job: the service
+            # call failed, so it says so in the shape the other services use,
+            # not as the worker's own RuntimeError.
+            failed[entry_id] = str(err)
+    if failed:
+        entry_ids = ", ".join(failed)
+        error = next(iter(failed.values()))
+        raise HomeAssistantError(
+            f"The interval diagnosis could not run for {entry_ids}: {error}",
+            translation_domain=DOMAIN,
+            translation_key="diagnose_interval_failed",
+            translation_placeholders={"entry_ids": entry_ids, "error": error},
+        )
     return {"diagnosis": reports}
 
 
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 38306f481..7d48935ba 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -457,6 +457,9 @@
     "simulate_plan_invalid_windows": {
       "message": "Invalid hot water windows \"{windows}\": {error}"
     },
+    "diagnose_interval_failed": {
+      "message": "The interval diagnosis could not run for {entry_ids}: {error}"
+    },
     "simulate_plan_failed": {
       "message": "The what-if simulation could not run for {entry_ids}: {error}"
     },
@@ -469,6 +472,9 @@
     "set_thermal_params_invalid_dhw_windows": {
       "message": "Invalid hot water windows \"{windows}\": {error}"
     },
+    "process_worker_timeout": {
+      "message": "The optimization worker gave no answer within {minutes} minutes and was restarted; the last plan stays in effect"
+    },
     "process_worker_unusable": {
       "message": "The optimization worker failed for {cycles} consecutive cycles; the last plan stays in effect"
     },
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 38306f481..7d48935ba 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -457,6 +457,9 @@
     "simulate_plan_invalid_windows": {
       "message": "Invalid hot water windows \"{windows}\": {error}"
     },
+    "diagnose_interval_failed": {
+      "message": "The interval diagnosis could not run for {entry_ids}: {error}"
+    },
     "simulate_plan_failed": {
       "message": "The what-if simulation could not run for {entry_ids}: {error}"
     },
@@ -469,6 +472,9 @@
     "set_thermal_params_invalid_dhw_windows": {
       "message": "Invalid hot water windows \"{windows}\": {error}"
     },
+    "process_worker_timeout": {
+      "message": "The optimization worker gave no answer within {minutes} minutes and was restarted; the last plan stays in effect"
+    },
     "process_worker_unusable": {
       "message": "The optimization worker failed for {cycles} consecutive cycles; the last plan stays in effect"
     },
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 529cecf89..a59596d56 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -457,6 +457,9 @@
     "simulate_plan_invalid_windows": {
       "message": "Ogiltiga varmvattentider \"{windows}\": {error}"
     },
+    "diagnose_interval_failed": {
+      "message": "Intervalldiagnosen kunde inte köras för {entry_ids}: {error}"
+    },
     "simulate_plan_failed": {
       "message": "Simuleringen kunde inte köras för {entry_ids}: {error}"
     },
@@ -469,6 +472,9 @@
     "set_thermal_params_invalid_dhw_windows": {
       "message": "Ogiltiga varmvattentider \"{windows}\": {error}"
     },
+    "process_worker_timeout": {
+      "message": "Optimeringsprocessen svarade inte inom {minutes} minuter och startades om; den senaste planen gäller fortfarande"
+    },
     "process_worker_unusable": {
       "message": "Optimeringsprocessen misslyckades {cycles} cykler i rad; den senaste planen gäller fortfarande"
     },
diff --git a/dev/programme/delivery/3232.md b/dev/programme/delivery/3232.md
new file mode 100644
index 000000000..4544cba4e
--- /dev/null
+++ b/dev/programme/delivery/3232.md
@@ -0,0 +1 @@
+- [#3232](https://github.com/tvofi/heatpump_optimizer/pull/3232) — **open**, fix(coordinator): bound the process worker's reply wait and the stop path's lock (outside contribution, was #3226)
diff --git a/tests/closure.py b/tests/closure.py
index 0ec5d97dd..b3d1df5d7 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -121,6 +121,10 @@ CLOSURES_COMMENT = (
 # could not record it without both. Its own nightly job runs it.
 NOT_A_TEST = {
     "harness.py", "profiles.py", "closure.py", "gate_lock.py",
+    # features.py's worker-deadline checks (#3232), a module it imports and
+    # runs, kept out of features.py so CodeQL's extraction of that module
+    # fits its job limit. Measured through features.py's closure.
+    "worker_deadlines.py",
     # The lane-skip decision instrument (R9-CI-SKIP): it reads this table to
     # decide whether `fast`/`coverage`/`browser` may report `skipped`, so it
     # is driven by the workflow's decision steps, never by the suite. NOT
diff --git a/tests/closures.json b/tests/closures.json
index c71959796..ca2802994 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1693,6 +1693,7 @@
    "tests/typing_ruler.py",
    "tests/validate.py",
    "tests/wood_advisor.py",
+   "tests/worker_deadlines.py",
    "tools/audit/archscore/__init__.py",
    "tools/audit/archscore/calibrate.py",
    "tools/audit/archscore/counters.py",
@@ -2254,6 +2255,7 @@
    "tests/run.sh",
    "tests/stress.py",
    "tests/structure.py",
+   "tests/worker_deadlines.py",
    "tools/devices/gen_device_fixtures.py",
    "tools/devices/measure_prefill_corpus.py"
   ],
diff --git a/tests/entities.py b/tests/entities.py
index 1a257bf95..59180c087 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -41332,6 +41332,10 @@ for _uxh_f in sorted(_UXH_PKG.glob("*.py")):
         if not (isinstance(_uxh_c, ast.Call) and isinstance(_uxh_c.func, ast.Attribute)
                 and _uxh_c.func.attr in _UXH_READS and _uxh_c.args):
             continue
+        # ``os.read(fd, n)`` is the descriptor read (the worker reply frame),
+        # never an InputReader: keyed by its receiver, not just the method name.
+        if isinstance(_uxh_c.func.value, ast.Name) and _uxh_c.func.value.id == "os":
+            continue
         _uxh_arg = _uxh_c.args[0]
         # `const.CONF_X` is the name `CONF_X`; any other shape is listed.
         _uxh_a = _uxh_arg.attr if isinstance(_uxh_arg, ast.Attribute) else getattr(_uxh_arg, "id", ast.dump(_uxh_arg))
diff --git a/tests/features.py b/tests/features.py
index 22bb32fca..2c710e433 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -38905,12 +38905,15 @@ _ET_KEYS = {
     "simulate_plan_no_prices": {"entry_ids"},
     "simulate_plan_invalid_windows": {"error", "windows"},
     "simulate_plan_failed": {"error", "entry_ids"},
+    "diagnose_interval_failed": {"error", "entry_ids"},
     "restore_learned_snapshot_no_snapshot": {"entry_ids"},
     "restore_learned_snapshot_no_refit": {"entry_ids"},
     "set_thermal_params_invalid_dhw_windows": {"error", "windows"},
     "set_temperature_comfort_band_violation": {"violations"},
     # #1546: the coordinator's UpdateFailed raises, through _raise_update_failed.
     "process_worker_unusable": {"cycles"},
+    # The worker read deadline (a silent worker is reaped, not waited on).
+    "process_worker_timeout": {"minutes"},
     "update_failed": {"error"},
     "tibber_fetch_failed": {"error"},
     # D10-s1-03: the refused token, through _raise_auth_failed.
@@ -41680,6 +41683,14 @@ R.check(
     f"jobs={_g524_ok_hass.jobs!r} issues={_g524_ok_hass.issues!r}",
 )
 
+# ---------------------------------------------------------------------------
+# The worker read deadline, the reply frame bound and the stop path's lock
+# bound (#3232): their checks are in tests/worker_deadlines.py, run here, so
+# that CodeQL's extraction of this module stays inside its job limit.
+import worker_deadlines as _worker_deadlines  # noqa: E402
+
+_worker_deadlines.run(R, _g3_parent)
+
 # ---------------------------------------------------------------------------
 R.section("#525 — nothing blocking runs on Home Assistant's event loop")
 
diff --git a/tests/harness.py b/tests/harness.py
index 3a0e2c380..beed66cc7 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -650,3 +650,44 @@ class UnpicklableResultOptimizer:
 
     def optimize(self, *, inputs):
         return UnpicklableResult()
+
+
+class SleepyOptimizer:
+    """``optimize`` runs in the child and answers only after ``seconds``.
+
+    Stands in for a worker that is alive but silent: the parent's read sees
+    no reply, no EOF and no error until the sleep ends.
+    """
+
+    def __init__(self, seconds: float) -> None:
+        self.seconds = seconds
+
+    def optimize(self, *, inputs):
+        import os
+        import time
+
+        time.sleep(self.seconds)
+        return ("slept", os.getpid(), inputs)
+
+
+def split_reply(pause_s: float, finish: bool = True) -> None:
+    """Write a reply frame in two halves ``pause_s`` apart, then end the child.
+
+    Stands in for a worker stopped mid-write after serialising its reply
+    (SIGSTOP, a stalled host): the pipe turns readable, then goes quiet. The
+    child exits after the frame, so the worker's own reply never follows it.
+    """
+    import os
+    import pickle
+    import sys
+    import time
+
+    blob = pickle.dumps(("ok", "split"), protocol=pickle.HIGHEST_PROTOCOL)
+    out = sys.stdout.buffer
+    out.write(blob[: len(blob) // 2])
+    out.flush()
+    time.sleep(pause_s)
+    if finish:  # False: the child dies mid-frame, an end of stream mid-reply
+        out.write(blob[len(blob) // 2:])
+        out.flush()
+    os._exit(0)
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json
new file mode 100644
index 000000000..5e93dda30
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.862cfb54.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST 862cfb54",
+  "killed_by": "tests/features.py",
+  "old": "PROCESS_REPLY_TIMEOUT_S = 1800.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROCESS_REPLY_TIMEOUT_S = 3600.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json
new file mode 100644
index 000000000..b0f709249
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.c828ef01.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST c828ef01",
+  "killed_by": "tests/features.py",
+  "old": "_SHUTDOWN_LOCK_TIMEOUT_S = 5.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_SHUTDOWN_LOCK_TIMEOUT_S = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json
new file mode 100644
index 000000000..ea93f9015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.cb651c79.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:<module> CONST cb651c79",
+  "killed_by": "tests/features.py",
+  "old": "_REPLY_FRAME_TIMEOUT_S = 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_REPLY_FRAME_TIMEOUT_S = 120.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json
new file mode 100644
index 000000000..3d312fc34
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RAISE_DEL.7456231f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_await_off_loop RAISE_DEL 7456231f",
+  "killed_by": "tests/features.py",
+  "old": "        raise",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RAISE_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json
new file mode 100644
index 000000000..87baf9630
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_await_off_loop.RETURN_DEL.48ca4fb4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_await_off_loop RETURN_DEL 48ca4fb4",
+  "killed_by": "tests/features.py",
+  "old": "    return result",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json
new file mode 100644
index 000000000..d6bb54238
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.RETURN_DEL.909c8492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader RETURN_DEL 909c8492",
+  "killed_by": "tests/features.py",
+  "old": "    return SimpleNamespace(read=read, readline=readline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json
new file mode 100644
index 000000000..11612813b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.821e5720.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND 821e5720",
+  "killed_by": "tests/features.py",
+  "old": "        if size > left_bytes:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if size >= left_bytes:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json
new file mode 100644
index 000000000..c68507a8d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.CMP_BOUND.eef3603a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND eef3603a",
+  "killed_by": "tests/features.py",
+  "old": "        while size > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`while size >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json
new file mode 100644
index 000000000..921c281f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.821e5720.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF 821e5720",
+  "killed_by": "tests/features.py",
+  "old": "        if size > left_bytes:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json
new file mode 100644
index 000000000..3f025320d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.9aafe706.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF 9aafe706",
+  "killed_by": "tests/features.py",
+  "old": "            if not chunk:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json
new file mode 100644
index 000000000..1e340c0d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.GUARD_OFF.fb715113.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read GUARD_OFF fb715113",
+  "killed_by": "tests/features.py",
+  "old": "            if left_s <= 0 or not _reply_ready(fd, left_s):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json
new file mode 100644
index 000000000..66c73fc21
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.read.RETURN_DEL.e9d62676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read RETURN_DEL e9d62676",
+  "killed_by": "tests/features.py",
+  "old": "        return b\"\".join(chunks)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json
new file mode 100644
index 000000000..36f010896
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.BOOLOP.65afbd87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.readline BOOLOP 65afbd87",
+  "killed_by": "tests/features.py",
+  "old": "        while not line.endswith(b\"\\n\") and (byte := read(1)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`while not line.endswith(b\"\\n\") or (byte := read(1)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json
new file mode 100644
index 000000000..828f38f17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_frame_reader.readline.RETURN_DEL.e4edcdb0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.readline RETURN_DEL e4edcdb0",
+  "killed_by": "tests/features.py",
+  "old": "        return line",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json
new file mode 100644
index 000000000..42a0347cb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.GUARD_OFF.6c857468.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_read_reply GUARD_OFF 6c857468",
+  "killed_by": "tests/features.py",
+  "old": "    if not _reply_ready(stdout, timeout):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json
new file mode 100644
index 000000000..3093eb454
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_read_reply.RETURN_DEL.65f007ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_read_reply RETURN_DEL 65f007ab",
+  "killed_by": "tests/features.py",
+  "old": "    return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json b/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json
new file mode 100644
index 000000000..cdb82c7da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_reply_ready.RETURN_DEL.0023660a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_reply_ready RETURN_DEL 0023660a",
+  "killed_by": "tests/features.py",
+  "old": "        return bool(selector.select(timeout_s))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json b/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json
new file mode 100644
index 000000000..2b616679d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_run_in_process.RAISE_DEL.d876a130.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_run_in_process RAISE_DEL d876a130",
+  "killed_by": "tests/features.py",
+  "old": "                raise",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RAISE_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json b/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json
new file mode 100644
index 000000000..3c0cb4521
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_shutdown_process_pool.GUARD_OFF.9403447b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_shutdown_process_pool GUARD_OFF 9403447b",
+  "killed_by": "tests/features.py",
+  "old": "    if not _PROCESS_LOCK.acquire(timeout=_SHUTDOWN_LOCK_TIMEOUT_S):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json b/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json
new file mode 100644
index 000000000..6e8946c28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_diagnose_interval GUARD_OFF 7beb0a59",
+  "killed_by": "tests/features.py",
+  "old": "    if failed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json b/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json
new file mode 100644
index 000000000..f944ca9a1
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_frame_reader.read CMP_BOUND fb715113",
+  "old": "            if left_s <= 0 or not _reply_ready(fd, left_s):",
+  "reason": "CMP_BOUND (`left_s < 0`) differs from `left_s <= 0` only when the remaining time is exactly 0.0, a float difference of two monotonic readings. Even then the outcome is unchanged: `_reply_ready(fd, 0.0)` polls without blocking, so a quiet writer still raises ProcessWorkerTimeout on that pass, and a ready descriptor yields one non-blocking read before the next pass sees a negative remainder and raises. Measured: `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` drove this mutant and reported `coordinator.py:1948 CMP_BOUND -- lives`, while GUARD_OFF on the same line was killed (tests/features.py rc=1 failed=2).",
+  "verdict": "equivalent"
+}
diff --git a/tests/run.sh b/tests/run.sh
index 004a7b041..b4405499a 100755
--- a/tests/run.sh
+++ b/tests/run.sh
@@ -449,7 +449,7 @@ skip() {
 for f in tests/*.py tests/*.mjs; do
   base=$(basename "$f")
   case "$base" in
-    harness.py|profiles.py) continue ;;  # shared plumbing, not tests
+    harness.py|profiles.py|worker_deadlines.py) continue ;;  # shared plumbing, not tests
     # The throwaway-repository helper (R9-RCA-stamp-race): a library; its
     # --check and --self-test run in governance's instrument-self-tests.
     throwaway_git.py) continue ;;
@@ -783,7 +783,7 @@ done
 for f in tests/*.py tests/*.mjs; do
   base=$(basename "$f")
   case "$base" in
-    harness.py|profiles.py|throwaway_git.py|dst_checks.py|closure.py|gate_lock.py|lane_skip.py|issue996_count.py|ha_floor.py|dom_stub.mjs|card_rig.mjs|card_browser.mjs|node_fs_trace.mjs|nightly_ha.py|replay.py|nightly_status.py|delivery_status.py|coverage_ratchet.py|mutation_table.py|ci_ratchet.py|host_probe.py) continue ;;
+    harness.py|profiles.py|worker_deadlines.py|throwaway_git.py|dst_checks.py|closure.py|gate_lock.py|lane_skip.py|issue996_count.py|ha_floor.py|dom_stub.mjs|card_rig.mjs|card_browser.mjs|node_fs_trace.mjs|nightly_ha.py|replay.py|nightly_status.py|delivery_status.py|coverage_ratchet.py|mutation_table.py|ci_ratchet.py|host_probe.py) continue ;;
   esac
   # The arch part owes the pair and nothing else; `fast` owes the rest, the
   # pair as its two named skips.
diff --git a/tests/worker_deadlines.py b/tests/worker_deadlines.py
new file mode 100644
index 000000000..d4576b877
--- /dev/null
+++ b/tests/worker_deadlines.py
@@ -0,0 +1,565 @@
+"""The solve worker's reply deadline, frame bound and stop-path lock bound.
+
+Not a script: ``tests/features.py`` calls ``run`` at the place these checks
+used to sit, so they report, and kill their mutants, as feature checks.
+They live in their own file because CodeQL's Python extractor spends most of
+the analysis job's 45 minutes on ``features.py`` alone: these 387 lines inside
+it took its extraction from 817-1389 s on main to over 2100 s, and
+``codeql / Analyze (python)`` never finished (#3232). Here they extract in
+seconds. A file of its own, not a second script, because the CI ratchet's
+``script_runs_per_push`` budget counts every runnable test script.
+
+``_run_in_process`` used to block in ``pickle.load`` with no deadline while it
+held ``_PROCESS_LOCK``. A worker alive but silent raised nothing, so the #511
+fallback never fired, every later solve and reload queued on the lock, and
+Home Assistant's stop ran into the supervisor's timeout. Every check drives
+the real worker process under Home Assistant's module naming.
+"""
+from __future__ import annotations
+
+import asyncio as _asyncio
+import logging as _logging
+import os as _os
+import sys
+from pathlib import Path as _Path
+from types import SimpleNamespace
+
+from harness import FakeHass
+import harness as _harness
+
+_root = str(_Path(__file__).resolve().parent.parent)
+if _root not in sys.path:
+    sys.path.insert(0, _root)
+
+# Home Assistant's spelling of the package: pickle ships a function by its
+# qualified name, so the worker must be driven under the name a real install
+# uses (#511).
+import custom_components.heatpump_optimizer.coordinator as _coord  # noqa: E402
+
+
+def _submit(run, fn, args):
+    """Round-trip ``fn`` through the real worker. The error IS the measurement."""
+    try:
+        return None, run(fn, args)
+    except Exception as err:  # noqa: BLE001
+        return err, None
+
+
+class _Hass(FakeHass):
+    """Records what reached the executor, so a fallback cannot hide."""
+
+    def __init__(self) -> None:
+        super().__init__()
+        self.jobs = []
+        self.issues = []
+
+    async def async_add_executor_job(self, func, *args):
+        self.jobs.append(func)
+        return func(*args)
+
+
+class _LogSink(_logging.Handler):
+    def __init__(self) -> None:
+        super().__init__(level=_logging.WARNING)
+        self.records = []
+
+    def emit(self, record):
+        self.records.append(record)
+
+
+def _solve(optimizer):
+    """``_await_optimize``, keeping what it RAISED apart from what it RETURNED."""
+    hass, sink = _Hass(), _LogSink()
+    logger = _logging.getLogger(_coord.__name__)
+    logger.addHandler(sink)
+    try:
+        try:
+            out = _asyncio.run(_coord._await_optimize(hass, optimizer, "STATE"))
+            raised, returned = None, out
+        except Exception as err:  # noqa: BLE001
+            raised, returned = err, None
+    finally:
+        logger.removeHandler(sink)
+    return raised, returned, hass, [r for r in sink.records if r.levelno >= 30]
+
+
+def run(R, _parent: int) -> None:
+    """Record every check on ``R``; ``_parent`` is the test process's pid."""
+    R.section("worker read timeout — a silent worker is reaped, not waited on")
+
+    # ``_run_in_process`` blocked in ``pickle.load`` with no deadline while it held
+    # ``_PROCESS_LOCK``. A worker that was alive but never answered (one install:
+    # no completed solve for ~55 minutes, one core busy) raised nothing, so the
+    # #511 fallback never fired, every later solve and reload queued on the lock,
+    # and Home Assistant's stop ran into the supervisor's timeout.
+    import threading as _wt_threading
+    import time as _wt_time
+
+    _wt_timeout_cls = getattr(_coord, "ProcessWorkerTimeout", None)
+    _wt_saved = (_coord.PROCESS_REPLY_TIMEOUT_S, _coord._SHUTDOWN_LOCK_TIMEOUT_S)
+    # Design-value pins: every timing check below shortens these, so none of
+    # them reads the shipped values. The reply deadline is the band its comment
+    # derives -- at least 4x the 426 s slowest solve measured, at most half an
+    # hour so a hung worker is reaped well inside the ~55-minute hang it bounds.
+    # The stop path's lock wait is the 5 s bookkeeping bound, far inside Home
+    # Assistant's 30 s close stage; a longer one buys the swap nothing.
+    R.check(
+        "the reply deadline sits in its derived band: 4 x 426 s <= deadline <= 30 min",
+        4 * 426 <= _wt_saved[0] <= 30 * 60,
+        f"PROCESS_REPLY_TIMEOUT_S = {_wt_saved[0]!r}",
+    )
+    R.check(
+        "the stop path's lock wait and the timed-out reap stay at the 5 s design bound",
+        _wt_saved[1] == 5.0,
+        f"_SHUTDOWN_LOCK_TIMEOUT_S = {_wt_saved[1]!r}",
+    )
+    try:
+        # Spawns and first imports run under the real deadline: only the
+        # measured call gets the short one, so a slow host cannot fail a check
+        # by starting a worker.
+        _wt_pid_before = _coord._run_in_process(_os.getpid, ())
+        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+        # Null control first, on the warm worker: a reply inside the deadline is
+        # untouched by it.
+        _wt_ok_err, _wt_ok_out = _submit(_coord._run_in_process, _wt_time.sleep, (0.05,))
+        _wt_ok_pid = _coord._run_in_process(_os.getpid, ())
+        R.check(
+            "null control: a job that answers in time returns and keeps its worker",
+            _wt_ok_err is None and _wt_ok_out is None and _wt_ok_pid == _wt_pid_before,
+            f"raised {_wt_ok_err!r}; pid {_wt_pid_before} -> {_wt_ok_pid}",
+        )
+        _wt_t0 = _wt_time.monotonic()
+        _wt_err, _wt_out = _submit(_coord._run_in_process, _wt_time.sleep, (30,))
+        _wt_elapsed = _wt_time.monotonic() - _wt_t0
+        _wt_lock_free = _coord._PROCESS_LOCK.acquire(blocking=False)
+        if _wt_lock_free:
+            _coord._PROCESS_LOCK.release()
+        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+        _wt_pid_after = _coord._run_in_process(_os.getpid, ())
+        R.check(
+            "a worker that gives no reply within the deadline raises ProcessWorkerTimeout",
+            _wt_timeout_cls is not None and isinstance(_wt_err, _wt_timeout_cls)
+            and _wt_out is None and _wt_elapsed < 10,
+            f"raised {_wt_err!r} after {_wt_elapsed:.1f} s; returned {_wt_out!r}",
+        )
+        R.check(
+            "and it frees the lock and the next job gets a fresh worker",
+            _wt_lock_free and _wt_pid_after not in (_wt_pid_before, _parent),
+            f"lock_free={_wt_lock_free} before={_wt_pid_before} after={_wt_pid_after}",
+        )
+
+        # ``_await_optimize`` must not rerun the timed-out job in process: the
+        # same job would hold an executor thread just as long. Warm the child's
+        # imports of the harness under the real deadline first.
+        _solve(_harness.SleepyOptimizer(0))
+        _coord.PROCESS_REPLY_TIMEOUT_S = 5.0
+        _wt_fast_err, _wt_fast_plan, _wt_fast_hass, _ = _solve(_harness.SleepyOptimizer(0.05))
+        R.check(
+            "null control: a solve inside the deadline returns its plan through the worker",
+            _wt_fast_err is None and isinstance(_wt_fast_plan, tuple)
+            and _wt_fast_plan[0] == "slept" and _wt_fast_plan[1] != _parent
+            and _wt_fast_hass.jobs == [_coord._run_in_process],
+            f"raised {_wt_fast_err!r}; returned {_wt_fast_plan!r}",
+        )
+        _wt_raised, _wt_plan, _wt_hass, _wt_warned = _solve(_harness.SleepyOptimizer(30))
+        R.check(
+            "_await_optimize keeps the last plan on a timeout: translated UpdateFailed, no in-process solve",
+            _wt_plan is None
+            and type(_wt_raised).__name__ == "UpdateFailed"
+            and getattr(_wt_raised, "translation_key", None) == "process_worker_timeout"
+            and _wt_hass.jobs == [_coord._run_in_process]
+            and [i for i in _wt_hass.issues if i[1] == "solve_worker_fallback"] == [],
+            f"raised {_wt_raised!r}; returned {_wt_plan!r}; jobs={_wt_hass.jobs!r} "
+            f"issues={_wt_hass.issues!r}",
+        )
+
+        # A timeout repeated every cycle warns ONCE, then says "Resolved" on the
+        # first solve the worker carries again (R10 N-log-flood: log_held).
+        _wt_latch_sink = _LogSink()
+        _wt_latch_sink.setLevel(_logging.INFO)
+        _wt_latch_log = _logging.getLogger(_coord.log_held.__module__)
+        _wt_latch_log.addHandler(_wt_latch_sink)
+        _wt_latch_level = _wt_latch_log.level
+        _wt_latch_log.setLevel(_logging.INFO)
+        _wt_one_hass = _Hass()
+        try:
+            for _wt_n in range(2):
+                try:
+                    _asyncio.run(_coord._await_optimize(
+                        _wt_one_hass, _harness.SleepyOptimizer(30), "STATE"))
+                except Exception:  # noqa: BLE001 - the UpdateFailed is checked above
+                    pass
+            _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+            _asyncio.run(_coord._await_optimize(
+                _wt_one_hass, _harness.SleepyOptimizer(0), "STATE"))
+        finally:
+            _wt_latch_log.removeHandler(_wt_latch_sink)
+            _wt_latch_log.setLevel(_wt_latch_level)
+            _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+        _wt_latch_msgs = [(r.levelno, r.getMessage()) for r in _wt_latch_sink.records
+                          if "process worker" in r.getMessage() or "process_worker" in r.getMessage()
+                          or "Resolved" in r.getMessage()]
+        R.check(
+            "two timeouts in a row warn once, and the next solve logs the recovery",
+            [lv for lv, _ in _wt_latch_msgs] == [_logging.WARNING, _logging.INFO],
+            f"latch records={_wt_latch_msgs!r}",
+        )
+
+        # ``_await_off_loop`` (replay, recovery, sysid, advisor) must not rerun a
+        # timed-out job on the executor, where it would run with no deadline.
+        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+        _coord._run_in_process(_os.getpid, ())  # warm the fresh worker
+        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+        _wt_ol_ok_hass = _Hass()
+        _wt_ol_ok = _asyncio.run(_coord._await_off_loop(_wt_ol_ok_hass, _os.getpid))
+        R.check(
+            "null control: an off-loop job inside the deadline returns through the worker",
+            _wt_ol_ok not in (None, _parent) and _wt_ol_ok_hass.jobs == [_coord._run_in_process],
+            f"returned {_wt_ol_ok!r}; jobs={_wt_ol_ok_hass.jobs!r}",
+        )
+        _wt_ol_hass = _Hass()
+        _wt_t2 = _wt_time.monotonic()
+        try:
+            _asyncio.run(_coord._await_off_loop(_wt_ol_hass, _wt_time.sleep, 30))
+            _wt_ol_err = None
+        except Exception as _wt_e:  # noqa: BLE001
+            _wt_ol_err = _wt_e
+        _wt_ol_s = _wt_time.monotonic() - _wt_t2
+        R.check(
+            "_await_off_loop raises a timeout to its caller instead of rerunning it on the executor",
+            _wt_timeout_cls is not None and isinstance(_wt_ol_err, _wt_timeout_cls)
+            and _wt_ol_hass.jobs == [_coord._run_in_process] and _wt_ol_s < 10,
+            f"raised {_wt_ol_err!r} after {_wt_ol_s:.1f} s; jobs={_wt_ol_hass.jobs!r}",
+        )
+
+        # The off-loop route holds its timeout warning per job as well: without
+        # it a timeout there is invisible at the default log level, because the
+        # replay and the sensor advisor catch it and log at DEBUG. Two timeouts of
+        # one job warn once, naming the job; its next completion logs "Resolved".
+        _wt_olw_sink = _LogSink()
+        _wt_olw_sink.setLevel(_logging.INFO)
+        _wt_olw_log = _logging.getLogger(_coord.log_held.__module__)
+        _wt_olw_log.addHandler(_wt_olw_sink)
+        _wt_olw_level = _wt_olw_log.level
+        _wt_olw_log.setLevel(_logging.INFO)
+        _wt_olw_hass = _Hass()
+        try:
+            for _wt_n in range(2):
+                try:
+                    _asyncio.run(_coord._await_off_loop(_wt_olw_hass, _wt_time.sleep, 30))
+                except Exception:  # noqa: BLE001 - the raise is checked above
+                    pass
+            _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+            _asyncio.run(_coord._await_off_loop(_wt_olw_hass, _wt_time.sleep, 0))
+        finally:
+            _wt_olw_log.removeHandler(_wt_olw_sink)
+            _wt_olw_log.setLevel(_wt_olw_level)
+            _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+        _wt_olw_msgs = [(r.levelno, r.getMessage()) for r in _wt_olw_sink.records
+                        if "sleep" in r.getMessage()]
+        R.check(
+            "two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery",
+            [lv for lv, _ in _wt_olw_msgs] == [_logging.WARNING, _logging.INFO]
+            and "Resolved" in _wt_olw_msgs[1][1]
+            and all("off loop timeout:sleep" in m or "sleep skipped" in m for _, m in _wt_olw_msgs),
+            f"latch records={_wt_olw_msgs!r}",
+        )
+
+        # The reply frame is read under its own deadline: a worker stopped
+        # mid-write after serialising its reply (SIGSTOP, a stalled host) must
+        # not hold ``pickle.load`` and the lock (#3232 round 3).
+        _wt_frame_saved = _coord._REPLY_FRAME_TIMEOUT_S
+        R.check(
+            "the reply frame deadline stays at its 60 s design value",
+            _wt_frame_saved == 60.0,
+            f"_REPLY_FRAME_TIMEOUT_S = {_wt_frame_saved!r}",
+        )
+        R.check(
+            "the reply frame size cap stays at its 256 MiB design value",
+            _coord._REPLY_FRAME_MAX_BYTES == 256 * 1024 * 1024,
+            f"_REPLY_FRAME_MAX_BYTES = {_coord._REPLY_FRAME_MAX_BYTES!r}",
+        )
+        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+        _coord._run_in_process(_os.getpid, ())  # warm a worker under the real deadline
+        _wt_big_t0 = _wt_time.monotonic()
+        _wt_big_err, _wt_big = _submit(_coord._run_in_process, bytes, (50_000_000,))
+        _wt_big_s = _wt_time.monotonic() - _wt_big_t0
+        R.check(
+            "null control: a 50 MB reply arrives whole through the frame reader, inside its deadline",
+            _wt_big_err is None and isinstance(_wt_big, bytes) and len(_wt_big) == 50_000_000
+            and _wt_big_s < _wt_frame_saved,
+            f"raised {_wt_big_err!r}; {len(_wt_big or b'')} bytes in {_wt_big_s:.2f} s",
+        )
+        _wt_big = None
+        _coord._REPLY_FRAME_TIMEOUT_S = 0.5
+        try:
+            _wt_split_ok_err, _wt_split_ok = _submit(
+                _coord._run_in_process, _harness.split_reply, (0.05,))
+            R.check(
+                "null control: a reply frame written in two halves inside the frame deadline returns",
+                _wt_split_ok_err is None and _wt_split_ok == "split",
+                f"raised {_wt_split_ok_err!r}; returned {_wt_split_ok!r}",
+            )
+            _coord._shutdown_process_pool()  # that child exited after its frame
+            _coord._run_in_process(_os.getpid, ())  # warm a fresh one
+            _wt_split_t0 = _wt_time.monotonic()
+            _wt_split_err, _wt_split_out = _submit(
+                _coord._run_in_process, _harness.split_reply, (30,))
+            _wt_split_s = _wt_time.monotonic() - _wt_split_t0
+            _wt_split_free = _coord._PROCESS_LOCK.acquire(blocking=False)
+            if _wt_split_free:
+                _coord._PROCESS_LOCK.release()
+            R.check(
+                "a worker stopped mid-reply raises ProcessWorkerTimeout, is reaped and frees the lock",
+                _wt_timeout_cls is not None and isinstance(_wt_split_err, _wt_timeout_cls)
+                and "mid-reply" in str(_wt_split_err) and _wt_split_out is None
+                and _wt_split_s < 10 and _wt_split_free
+                and _coord._PROCESS_WORKER is None,
+                f"raised {_wt_split_err!r} after {_wt_split_s:.1f} s; returned {_wt_split_out!r}; "
+                f"lock_free={_wt_split_free} worker={_coord._PROCESS_WORKER!r}",
+            )
+            # A child that dies mid-frame is an end of stream, a transport fault
+            # the fallback routes around at once, never a wait out to the deadline.
+            _coord._run_in_process(_os.getpid, ())  # warm a fresh one
+            _wt_eof_t0 = _wt_time.monotonic()
+            _wt_eof_err, _ = _submit(
+                _coord._run_in_process, _harness.split_reply, (0.05, False))
+            _wt_eof_s = _wt_time.monotonic() - _wt_eof_t0
+            R.check(
+                "a worker that dies mid-reply is a transport fault, not a timeout",
+                isinstance(_wt_eof_err, _coord.ProcessWorkerUnavailable)
+                and _wt_timeout_cls is not None and not isinstance(_wt_eof_err, _wt_timeout_cls)
+                and _wt_eof_s < 0.5,
+                f"raised {_wt_eof_err!r} after {_wt_eof_s:.2f} s",
+            )
+            # The frame's size is bounded as well as its time: the worker's bytes
+            # are not trusted, so a reply past the cap is a transport fault that
+            # reaps the worker mid-frame and frees the lock (#3232 round 4).
+            _wt_cap_saved = _coord._REPLY_FRAME_MAX_BYTES
+            _coord._REPLY_FRAME_MAX_BYTES = 1_000_000
+            try:
+                _wt_cap_ok_err, _wt_cap_ok = _submit(
+                    _coord._run_in_process, bytes, (900_000,))
+                _wt_cap_t0 = _wt_time.monotonic()
+                _wt_cap_err, _wt_cap_out = _submit(
+                    _coord._run_in_process, bytes, (2_000_000,))
+                _wt_cap_s = _wt_time.monotonic() - _wt_cap_t0
+            finally:
+                _coord._REPLY_FRAME_MAX_BYTES = _wt_cap_saved
+            _wt_cap_free = _coord._PROCESS_LOCK.acquire(blocking=False)
+            if _wt_cap_free:
+                _coord._PROCESS_LOCK.release()
+            R.check(
+                "null control: a reply under the frame size cap returns whole",
+                _wt_cap_ok_err is None and _wt_cap_ok == bytes(900_000),
+                f"raised {_wt_cap_ok_err!r}; {len(_wt_cap_ok or b'')} bytes",
+            )
+            R.check(
+                "a reply frame past its size cap is a transport fault: the worker is reaped and the lock freed",
+                isinstance(_wt_cap_err, _coord.ProcessWorkerUnavailable)
+                and _wt_timeout_cls is not None and not isinstance(_wt_cap_err, _wt_timeout_cls)
+                and "exceeds 1000000 bytes" in str(_wt_cap_err) and _wt_cap_out is None
+                and _wt_cap_s < 0.5 and _wt_cap_free and _coord._PROCESS_WORKER is None,
+                f"raised {_wt_cap_err!r} after {_wt_cap_s:.2f} s; returned {len(_wt_cap_out or b'')} bytes; "
+                f"lock_free={_wt_cap_free} worker={_coord._PROCESS_WORKER!r}",
+            )
+            # The cap bounds the WHOLE frame, not each read(): a reply of two
+            # 600 kB strings reads each under a 1 MB cap and totals 1.2 MB, and
+            # only the running count in ``_frame_reader`` refuses it. The null
+            # control is a total under the cap, which returns whole.
+            _coord._REPLY_FRAME_MAX_BYTES = 1_000_000
+            try:
+                _wt_cum_ok_err, _wt_cum_ok = _submit(
+                    _coord._run_in_process, tuple,
+                    ([bytes(400_000), bytes(400_000)],))
+                _wt_cum_t0 = _wt_time.monotonic()
+                _wt_cum_err, _wt_cum_out = _submit(
+                    _coord._run_in_process, tuple,
+                    ([bytes(600_000), bytes(600_000)],))
+                _wt_cum_s = _wt_time.monotonic() - _wt_cum_t0
+            finally:
+                _coord._REPLY_FRAME_MAX_BYTES = _wt_cap_saved
+            _wt_cum_free = _coord._PROCESS_LOCK.acquire(blocking=False)
+            if _wt_cum_free:
+                _coord._PROCESS_LOCK.release()
+            R.check(
+                "null control: a reply of two reads whose total is under the frame cap returns whole",
+                _wt_cum_ok_err is None and _wt_cum_ok is not None
+                and tuple(len(b) for b in _wt_cum_ok) == (400_000, 400_000),
+                f"raised {_wt_cum_ok_err!r}",
+            )
+            R.check(
+                "a reply whose reads each fit the frame cap but whose total exceeds it is refused and the worker reaped",
+                isinstance(_wt_cum_err, _coord.ProcessWorkerUnavailable)
+                and "exceeds 1000000 bytes" in str(_wt_cum_err) and _wt_cum_out is None
+                and _wt_cum_free and _coord._PROCESS_WORKER is None,
+                f"raised {_wt_cum_err!r} after {_wt_cum_s:.2f} s; returned {_wt_cum_out!r}; "
+                f"lock_free={_wt_cum_free} worker={_coord._PROCESS_WORKER!r}",
+            )
+        finally:
+            _coord._REPLY_FRAME_TIMEOUT_S = _wt_frame_saved
+        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+
+        # The reader's ``readline`` (only text opcodes ask) returns one line and
+        # leaves the rest of the frame unread, under the same deadline.
+        _wt_rl_r, _wt_rl_w = _os.pipe()
+        try:
+            _os.write(_wt_rl_w, b"ab\ncd")
+            _wt_rl = _coord._frame_reader(_wt_rl_r, 1.0)
+            _wt_rl_line, _wt_rl_rest = _wt_rl.readline(), _wt_rl.read(2)
+            _os.close(_wt_rl_w)
+            _wt_rl_w = None
+            _wt_rl_tail = _wt_rl.readline()
+        finally:
+            _os.close(_wt_rl_r)
+            if _wt_rl_w is not None:
+                _os.close(_wt_rl_w)
+        R.check(
+            "the frame reader's readline returns one line, the rest stays unread, and it stops at end of stream",
+            (_wt_rl_line, _wt_rl_rest, _wt_rl_tail) == (b"ab\n", b"cd", b""),
+            f"line={_wt_rl_line!r} rest={_wt_rl_rest!r} tail={_wt_rl_tail!r}",
+        )
+
+        # A declared length past the cap is refused before it is read or
+        # allocated: on an empty pipe the reader raises at once, not at its
+        # deadline, and a length exactly at the cap is still waited on.
+        _wt_dl_r, _wt_dl_w = _os.pipe()
+        _wt_dl = []
+        try:
+            for _wt_dl_size in (_coord._REPLY_FRAME_MAX_BYTES + 1,
+                                _coord._REPLY_FRAME_MAX_BYTES):
+                _wt_dl_t0 = _wt_time.monotonic()
+                try:
+                    _coord._frame_reader(_wt_dl_r, 0.3).read(_wt_dl_size)
+                    _wt_dl.append(("returned", 0.0))
+                except Exception as _wt_dl_exc:  # noqa: BLE001 - the class is the result
+                    _wt_dl.append((type(_wt_dl_exc).__name__, _wt_time.monotonic() - _wt_dl_t0))
+        finally:
+            _os.close(_wt_dl_r)
+            _os.close(_wt_dl_w)
+        R.check(
+            "the frame reader refuses a declared length past its cap at once, and waits on one at it",
+            len(_wt_dl) == 2 and _wt_dl[0][0] == "ValueError" and _wt_dl[0][1] < 0.1
+            and _wt_dl[1][0] == "ProcessWorkerTimeout" and _wt_dl[1][1] >= 0.25,
+            f"results={_wt_dl!r}",
+        )
+
+        # A worker whose pipe lands at a descriptor >= FD_SETSIZE (1024) -- Home
+        # Assistant raises its soft fd limit past it -- must still be waited on
+        # with the deadline, not read as a transport fault (select.select refuses
+        # such a descriptor; the #3232 review's regression).
+        import resource as _wt_resource  # noqa: E402
+        import gc as _wt_gc  # noqa: E402
+
+        _wt_soft, _wt_hard = _wt_resource.getrlimit(_wt_resource.RLIMIT_NOFILE)
+        _wt_fds = []
+        _wt_hi_fd = -1
+        _wt_hi_ok = _wt_hi_err = _wt_hi_warm = None
+        try:
+            _wt_want = 1200
+            if _wt_soft != _wt_resource.RLIM_INFINITY and _wt_soft < _wt_want:
+                _wt_resource.setrlimit(_wt_resource.RLIMIT_NOFILE, (
+                    _wt_want if _wt_hard == _wt_resource.RLIM_INFINITY else min(_wt_want, _wt_hard),
+                    _wt_hard))
+            # Reap first, then fill: the old worker's pipes freed after the fill
+            # would hand the respawn low descriptors again.
+            _coord._shutdown_process_pool()
+            _wt_gc.collect()
+            while len(_wt_fds) < 1100:
+                _wt_fds.append(_os.open(_os.devnull, _os.O_RDONLY))
+            _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+            _wt_hi_warm, _ = _submit(_coord._run_in_process, _os.getpid, ())
+            if _coord._PROCESS_WORKER is not None:
+                _wt_hi_fd = _coord._PROCESS_WORKER.stdout.fileno()
+            _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
+            _wt_hi_ok, _ = _submit(_coord._run_in_process, _wt_time.sleep, (0.05,))
+            _wt_hi_err, _ = _submit(_coord._run_in_process, _wt_time.sleep, (30,))
+        finally:
+            for _wt_fd in _wt_fds:
+                _os.close(_wt_fd)
+            _coord._shutdown_process_pool()
+            _wt_resource.setrlimit(_wt_resource.RLIMIT_NOFILE, (_wt_soft, _wt_hard))
+        R.check(
+            "a worker pipe at fd >= 1024 answers in time and still times out as a timeout",
+            _wt_hi_warm is None and _wt_hi_fd >= 1024 and _wt_hi_ok is None
+            and _wt_timeout_cls is not None and type(_wt_hi_err) is _wt_timeout_cls,
+            f"warm raised {_wt_hi_warm!r}; stdout fd={_wt_hi_fd}; fast job raised {_wt_hi_ok!r}; slow job raised {_wt_hi_err!r}",
+        )
+        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
+
+        # The stop path: a lock held past the kill must not hold the stop.
+        _coord._SHUTDOWN_LOCK_TIMEOUT_S = 0.2
+        _coord._run_in_process(_os.getpid, ())
+        _wt_release = _wt_threading.Event()
+
+        def _wt_hold() -> None:
+            with _coord._PROCESS_LOCK:
+                _wt_release.wait(10)
+
+        _wt_holder = _wt_threading.Thread(target=_wt_hold, daemon=True)
+        _wt_holder.start()
+        _wt_time.sleep(0.05)
+        _wt_t1 = _wt_time.monotonic()
+        _coord._shutdown_process_pool()
+        _wt_stop_s = _wt_time.monotonic() - _wt_t1
+        _wt_release.set()
+        _wt_holder.join(5)
+        R.check(
+            "the stop path returns within its lock timeout while the lock is held",
+            _wt_stop_s < 3,
+            f"_shutdown_process_pool took {_wt_stop_s:.2f} s with the lock held",
+        )
+    finally:
+        _coord.PROCESS_REPLY_TIMEOUT_S, _coord._SHUTDOWN_LOCK_TIMEOUT_S = _wt_saved
+
+    # The diagnose service calls ``_await_process`` directly: a worker timeout or
+    # an unusable worker reaches its caller as the service-failed shape the other
+    # services raise, not as the worker's own RuntimeError (#3232 round 3).
+    from heatpump_optimizer import services as _wt_svc
+    from homeassistant.exceptions import HomeAssistantError as _wt_HAE
+
+    _wt_svc_coord_mod = sys.modules[_wt_svc.__name__.rsplit(".", 1)[0] + ".coordinator"]
+
+
+    class _WtDiagCoord:
+        def __init__(self, outcome):
+            self.outcome = outcome
+
+        async def async_diagnose_interval(self):
+            if isinstance(self.outcome, BaseException):
+                raise self.outcome
+            return self.outcome
+
+
+    def _wt_diagnose(outcome):
+        saved = _wt_svc._manual_targets
+        _wt_svc._manual_targets = lambda hass, target: [("e1", _WtDiagCoord(outcome))]
+        try:
+            return None, _asyncio.run(_wt_svc.handle_diagnose_interval(
+                None, SimpleNamespace(data={})))
+        except Exception as err:  # noqa: BLE001 - the error IS the measurement
+            return err, None
+        finally:
+            _wt_svc._manual_targets = saved
+
+
+    _wt_dg_ok_err, _wt_dg_ok = _wt_diagnose({"residual": 0.1})
+    R.check(
+        "null control: a diagnosis that runs is returned by the service",
+        _wt_dg_ok_err is None and _wt_dg_ok == {"diagnosis": {"e1": {"residual": 0.1}}},
+        f"raised {_wt_dg_ok_err!r}; returned {_wt_dg_ok!r}",
+    )
+    for _wt_dg_exc in (
+        _wt_svc_coord_mod.ProcessWorkerTimeout("process worker gave no reply within 1800 s"),
+        _wt_svc_coord_mod.ProcessWorkerUnavailable("process worker cannot start: boom"),
+    ):
+        _wt_dg_err, _ = _wt_diagnose(_wt_dg_exc)
+        R.check(
+            f"a diagnosis failing with {type(_wt_dg_exc).__name__} reaches the service caller translated",
+            isinstance(_wt_dg_err, _wt_HAE)
+            and not isinstance(_wt_dg_err, _wt_svc_coord_mod.ProcessWorkerUnavailable)
+            and getattr(_wt_dg_err, "translation_key", None) == "diagnose_interval_failed"
+            and getattr(_wt_dg_err, "translation_placeholders", None)
+            == {"entry_ids": "e1", "error": str(_wt_dg_exc)},
+            f"raised {_wt_dg_err!r}",
+        )

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
