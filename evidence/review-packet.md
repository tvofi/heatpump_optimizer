# Review packet #2995
head: edf1cba7cda43790435d1d4b5aa1b3b24562912a
base: e77418f9b48f89421bd72b0ab511c057341c7fa4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124095732263 success
arch-score / arch-score id=124134390375 success
arm id=124095227899 skipped
budget-raise-gate / budget-raise-gate id=124134389326 success
cancel-superseded id=124134308634 success
codeql id=124134231077 skipped
codeql / Analyze (actions) id=124134309931 success
codeql / Analyze (javascript-typescript) id=124134310170 success
codeql / Analyze (python) id=124134310426 success
gate id=124135042439 queued
governance id=124134229783 skipped
governance / delivery-status id=124134358833 success
governance / delivery-status-publish id=124134310991 skipped
governance / env-matrix id=124134310471 success
governance / instrument-self-tests id=124134310612 success
governance / policy-docs id=124134310238 success
governance / record id=124134310480 skipped
governance / wave-script id=124134359698 success
hassfest id=124134230825 skipped
hassfest / hassfest id=124134309887 success
kernel-points id=124134309594 skipped
pr-contract / pr-contract id=124134694531 success
prelude id=124134367144 success
refresh id=124134309050 success
tests id=124134229445 skipped
tests / arch-instrument id=124134311927 success
tests / briefs id=124134309831 success
tests / browser id=124134312296 success
tests / ci-ratchet id=124134313841 skipped
tests / claims-autofix id=124134314281 skipped
tests / closure-scope id=124134309316 success
tests / closures id=124134311809 success
tests / closures-autofix id=124134313166 skipped
tests / coverage id=124134312013 success
tests / coverage-ratchet id=124134312572 success
tests / fast (3.14) id=124134311965 success
tests / graders-head-copy id=124134313661 success
tests / lane-proofs id=124134313535 success
tests / mutation id=124134310831 success
tests / mutation-autofix id=124134312691 skipped
tests / mutation-pins id=124134312836 skipped
tests / nightly-ha id=124134311689 skipped
tests / nightly-status id=124134361642 success
tests / replay id=124134312388 skipped
tests / typing id=124134311688 success
validate id=124134229568 skipped
validate / validate-hacs id=124134309829 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 21ef7bb9: R10-FLY-STAMP-CHECK-NOTES
NOTE body item b5024815: dismissed:a one-shot replay harness of a finished group; #2731, the class's issue, has no live roster group (R10-FLY-GH-READ-RETRY reads done at origin/handoff/audit-r10-roster 78c0bb77b while #2731 is open), so no destination exists; routed to the orchestrator in this handoff's result
NOTE body item 932bd75b: dismissed:a session plugin, not repository policy
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/ci/ghapi.py --self-test
             `tools/ci/ghapi.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_seat_selftests_mutants.py ghapi-1 ghapi-2 ghapi-3 ghapi-4 ghapi-5 ghapi-6 ghapi-7 ghapi-8 ghapi-9 ghapi-10
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 507a9ec264eb373b132248d752259254d8a9fa4d --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/ghapi.py changes the gate itself
             `tools/ci/ghapi.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 507a9ec264eb373b132248d752259254d8a9fa4d
             `tools/audit/archscore/score.py` is in the tree at this head
  unverified git grep -n "urlopen(" -- tools dev/audit/harnesses .github
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/ci/ghapi.py
             `tools/ci/ghapi.py` is in the tree at this head
  ok         tools/audit/seat/record_row.py
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         tools/release/stamp.py
             `tools/release/stamp.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_main_gate_replay.py
             `dev/audit/harnesses/r10_main_gate_replay.py` is in the tree at this head
  ok         dev/audit/harnesses/d6_page_anchors.py
             `dev/audit/harnesses/d6_page_anchors.py` is in the tree at this head
  ok         dev/audit/harnesses/r10_codescan_wait_race.py
             `dev/audit/harnesses/r10_codescan_wait_race.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 61e122ae6..207b354f3 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -400,6 +400,19 @@ MUTANTS = [
     ("ghapi-2", "tools/ci/ghapi.py", "        if not nxt:\n            return out\n", "        return out\n"),
     # P2a glue: the extra request headers alert_list's SARIF read is bound through.
     ("ghapi-3", "tools/ci/ghapi.py", "        req.add_header(k, v)\n", "        pass\n"),
+    # R10-FLY-GH-READ-RETRY carry 7 (#2859): a GET retries a transport failure like a 5xx;
+    # one mutant per TRANSPORT member, the arm, the budget's raise and the retry itself.
+    ("ghapi-4", "tools/ci/ghapi.py", "        except TRANSPORT:\n", "        except ():\n"),
+    ("ghapi-5", "tools/ci/ghapi.py", "(urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError)",
+     "(http.client.HTTPException, ConnectionError, TimeoutError)"),
+    ("ghapi-6", "tools/ci/ghapi.py", "(urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError)",
+     "(urllib.error.URLError, ConnectionError, TimeoutError)"),
+    ("ghapi-7", "tools/ci/ghapi.py", "(urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError)",
+     "(urllib.error.URLError, http.client.HTTPException, TimeoutError)"),
+    ("ghapi-8", "tools/ci/ghapi.py", "(urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError)",
+     "(urllib.error.URLError, http.client.HTTPException, ConnectionError)"),
+    ("ghapi-9", "tools/ci/ghapi.py", "            if nap is None:\n                raise\n", "            if False:\n                raise\n"),
+    ("ghapi-10", "tools/ci/ghapi.py", "    for nap in RETRY_5XX + (None,):\n", "    for nap in (None,):\n"),
     ("prelude-1", "tools/ci/prelude.py", 'return (KP if ctx.get("label") == KP else "label")', 'return "code"'),
     ("prelude-2", "tools/ci/prelude.py", 'if r["id"] < ctx["run_id"] and r["status"] in UNFINISHED)',
      'if r["status"] in UNFINISHED)'),
diff --git a/dev/programme/delivery/2995.md b/dev/programme/delivery/2995.md
new file mode 100644
index 000000000..13323c608
--- /dev/null
+++ b/dev/programme/delivery/2995.md
@@ -0,0 +1 @@
+- [#2995](https://github.com/tvofi/heatpump_optimizer/pull/2995) — **open**, R10-FLY-GH-READ-RETRY: ghapi: a GET retries a transport failure like a 5xx (R10-FLY-GH-READ-RETRY carry 7, #2859) (R10-FLY-GH-READ-RETRY)
diff --git a/tools/ci/ghapi.py b/tools/ci/ghapi.py
index 8ab1e3d37..5afe52a98 100644
--- a/tools/ci/ghapi.py
+++ b/tools/ci/ghapi.py
@@ -14,7 +14,8 @@ there that imports urllib (contract item 2), stdlib only.
     post(path, body=None)  -> Resp
     paginate(path, params) -> list       every item of every page, Link-followed
 
-A GET retries a 5xx twice (RETRY_5XX backoffs) before answering. A non-2xx
+A GET retries a 5xx or a TRANSPORT failure twice (RETRY_5XX backoffs) before
+answering, or raising the last transport failure. A non-2xx
 answer is returned, never raised, so the caller names it -- except a
 RATE LIMIT (A1 item 4): a 403 or 429 whose body says the rate limit was
 exceeded raises `RateLimited`, carrying `reset_epoch` from `X-RateLimit-Reset`
@@ -26,6 +27,7 @@ is GITHUB_TOKEN, else GH_TOKEN.
 """
 from __future__ import annotations
 
+import http.client
 import json
 import os
 import re
@@ -36,7 +38,12 @@ import urllib.parse
 import urllib.request
 
 API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
-RETRY_5XX = (2, 6)      # GET only: the backoffs, in seconds, before each retry of a 5xx answer
+RETRY_5XX = (2, 6)      # GET only: the backoffs, in seconds, before each retry of a 5xx or TRANSPORT failure
+#: A failure with no answer that a later read can ride out: a connection that failed
+#: (URLError; HTTPError, its subclass, is an answer and _request catches it first), a
+#: response cut short in r.read() (IncompleteRead, an HTTPException), a reset, a timeout.
+#: gh_read.urllib_wait's transport set, which tools/ci may not import (contract item 2).
+TRANSPORT = (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError)
 MAX_PAGES = 50          # 5000 items at per_page=100: far past any head's runs; a Link loop ends here
 _NEXT = re.compile(r'<([^>]+)>;\s*rel="next"')
 
@@ -102,16 +109,20 @@ def _sleep(seconds: float) -> None:
 
 
 def get(path: str, params=None, headers=None):
-    """A 5xx is GitHub's transient (M-5b: a gate FAILed on one HTTP 502), so a GET retries it
-    after each backoff in RETRY_5XX and then returns what it got; any other status, a rate limit
-    included, answers at once. A POST is never retried."""
-    resp = _request("GET", path, params, headers=headers)
-    for nap in RETRY_5XX:
-        if resp[0] < 500:
-            break
+    """A 5xx is GitHub's transient (M-5b: a gate FAILed on one HTTP 502), and so is a TRANSPORT
+    failure (#2859: prelude red on one IncompleteRead), so a GET retries either after each
+    backoff in RETRY_5XX and then returns what it got, or raises the last transport failure; any
+    other status, a rate limit included, answers at once. A POST is never retried."""
+    for nap in RETRY_5XX + (None,):
+        try:
+            resp = _request("GET", path, params, headers=headers)
+        except TRANSPORT:
+            if nap is None:
+                raise
+        else:
+            if resp[0] < 500 or nap is None:
+                return resp
         _sleep(nap)
-        resp = _request("GET", path, params, headers=headers)
-    return resp
 
 
 def post(path: str, body=None):
@@ -250,6 +261,57 @@ def self_test() -> int:
             calls.clear()
             _open = lambda req: (calls.append(req), serve(502, b"")(req))[1]  # noqa: E731
             check("a POST is never retried (a re-run request is not repeated)", (post("x")[0], len(calls)), (502, 1))
+
+            # A transport failure is a 5xx's transient (#2859's prelude: IncompleteRead out of
+            # r.read(), green twice at the next head): a GET retries it alike, and after the
+            # budget raises the last failure, never a guessed answer.
+            class CutShort(Fake):
+                def read(self):
+                    raise self._body
+
+            def broken(*answers):
+                seq = iter(answers)
+
+                def fake(req):
+                    calls.append(req)
+                    a = next(seq)
+                    if isinstance(a, BaseException):
+                        raise a
+                    return a
+                return fake
+            for name, failure, raised in (
+                    ("a truncated read", CutShort(200, http.client.IncompleteRead(b"", 48262)), http.client.IncompleteRead),
+                    ("a reset mid-read", CutShort(200, ConnectionResetError(104, "reset")), ConnectionResetError),
+                    ("a timeout mid-read", CutShort(200, TimeoutError("timed out")), TimeoutError),
+                    ("a connection reset", urllib.error.URLError(ConnectionResetError(104, "reset")), urllib.error.URLError)):
+                calls.clear()
+                _open = broken(failure, Fake(200, b'{"ok": true}'))
+                try:
+                    got = get("x")
+                except Exception as e:  # noqa: BLE001 -- an unretried failure is this check's FAIL
+                    got = repr(e)
+                check(f"{name} then a 200 on a GET answers the 200", (got, len(calls)), ((200, {}, {"ok": True}), 2))
+                calls.clear()
+                _open = broken(failure, failure, failure, failure)
+                try:
+                    get("x")
+                    check(f"{name} that persists raises", "returned", "raised")
+                except raised:
+                    check(f"{name} that persists raises the last failure after two retries", len(calls), 3)
+                calls.clear()
+                _open = broken(failure, Fake(200, b"{}"))
+                try:
+                    post("x")
+                    check(f"{name} on a POST raises", "returned", "raised")
+                except raised:
+                    check(f"{name} on a POST raises at once, never retried", len(calls), 1)
+            calls.clear()
+            _open = broken(ValueError("not transport"), Fake(200, b"{}"))
+            try:
+                get("x")
+                check("a non-transport exception raises", "returned", "raised")
+            except ValueError:
+                check("a non-transport exception raises at once (null control)", len(calls), 1)
         finally:
             _sleep = saved_sleep
         _open = serve(200, b"{}")

