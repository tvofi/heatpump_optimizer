# Review packet #3259
head: 47810de38785ec8563d97c89d5c6dfdb822c6288
base: 57958d6a44c4f489384705ba64e8f65a8507f6b7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128102962362 success
arch-score / arch-score id=128124085307 success
arm id=128102591191 skipped
budget-raise-gate / budget-raise-gate id=128124085277 success
cancel-superseded id=128124084384 success
codeql id=128124085449 skipped
codeql / Analyze (actions) id=128102870416 success
codeql / Analyze (javascript-typescript) id=128102870266 success
codeql / Analyze (python) id=128102870469 success
gate id=128124083797 success
governance id=128124151716 skipped
governance / delivery-status id=128102870395 success
governance / delivery-status-publish id=128102872208 skipped
governance / env-matrix id=128102870167 success
governance / instrument-self-tests id=128102870348 success
governance / policy-docs id=128102870158 success
governance / record id=128102873133 skipped
governance / wave-script id=128102870032 success
hassfest id=128124085505 skipped
hassfest / hassfest id=128102870063 success
kernel-points id=128124139880 skipped
pr-contract id=128124085896 skipped
pr-contract / pr-contract id=128122829640 success
prelude id=128124085462 success
refresh id=128124083685 success
tests id=128124163482 skipped
tests / arch-instrument id=128103127559 success
tests / briefs id=128102870341 success
tests / browser id=128103127460 success
tests / ci-ratchet id=128122829576 skipped
tests / claims-autofix id=128113658653 skipped
tests / closure-scope id=128102870499 success
tests / closures id=128103127572 success
tests / closures-autofix id=128122830522 skipped
tests / coverage id=128103127414 success
tests / coverage-ratchet id=128120052219 success
tests / fast (3.14) id=128103127608 success
tests / graders-head-copy id=128120052331 success
tests / lane-proofs id=128120052364 success
tests / mutation id=128102870400 success
tests / mutation-autofix id=128103297282 skipped
tests / mutation-pins id=128103295983 skipped
tests / nightly-ha id=128103129622 skipped
tests / nightly-status id=128102870536 success
tests / replay id=128103130539 skipped
tests / typing id=128103127675 success
validate id=128124135261 skipped
validate / validate-hacs id=128102870160 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 61994172: dismissed(R10-HOTFIX-GATE-STALE-JOBS):built by 3205 and verified here
NOTE body item 0a7b243f: dismissed(R10-HOTFIX-GATE-STALE-JOBS):fixed in this diff
NOTE body item 7138d160: dismissed(R10-HOTFIX-GATE-STALE-JOBS):unmeasured, cannot fail open
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_gate_stale_jobs/harness.py
             `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` is in the tree at this head
  ok         python3 -I tools/ci/codescan_wait.py --self-test
             `tools/ci/codescan_wait.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3259.md b/dev/programme/delivery/3259.md
new file mode 100644
index 000000000..3af7ca534
--- /dev/null
+++ b/dev/programme/delivery/3259.md
@@ -0,0 +1 @@
+- [#3259](https://github.com/tvofi/heatpump_optimizer/pull/3259) — **open**, R10-HOTFIX-GATE-STALE-JOBS (part 2): gate stale jobs carries from #3205/#3206 (R10-HOTFIX-GATE-STALE-JOBS)
diff --git a/tools/ci/codescan_wait.py b/tools/ci/codescan_wait.py
index 6e3f3077d..41e9f016a 100644
--- a/tools/ci/codescan_wait.py
+++ b/tools/ci/codescan_wait.py
@@ -71,7 +71,13 @@ def source(get, repo, run_id, pr, base, stop, sleep=time.sleep, now=time.monoton
     """(S's run object, S's jobs): step 1, polled until `stop`."""
     me = _get(get, f"repos/{repo}/actions/runs/{run_id}", "this run")
     if owns_codeql(me, pr):
-        return me, _jobs(get, repo, me["id"])
+        while True:                                # a listing under load lags: poll it settled, as the other path does
+            jobs = _jobs(get, repo, me["id"])
+            if settled(jobs):
+                return me, jobs
+            if now() + POLL_S > stop:
+                raise Fail(f"this run's codeql jobs were not listed finished after {WAIT_MAX_S} s")
+            sleep(POLL_S)
     if pr:
         base = _get(get, f"repos/{repo}/pulls/{pr}", f"pull request {pr}")["base"]["ref"]
     while True:
@@ -89,6 +95,21 @@ def source(get, repo, run_id, pr, base, stop, sleep=time.sleep, now=time.monoton
         sleep(POLL_S)
 
 
+def settled(jobs):
+    """Every codeql job listed completed, and each either skipped outright or with its analysis step concluded:
+    a leg whose step row lags reads as stood down in `legs_uploaded`, and goes unread."""
+    by = {j["name"]: j for j in jobs}
+    for n in CODEQL:
+        j = by.get(n)
+        if j is None or j.get("status") != "completed":
+            return False
+        if j.get("conclusion") in ("skipped", "cancelled"):
+            continue
+        if not any(s["name"] == STEP and s.get("conclusion") for s in j.get("steps") or []):
+            return False
+    return True
+
+
 def legs_uploaded(jobs):
     """Step 2."""
     out = []
@@ -275,6 +296,31 @@ def self_test() -> int:
         got = f"FAIL {e}"
     check("17 WAIT_MAX_S bounds steps 1 and 4 together, not each", str(got).startswith("FAIL no analysis")
           and clock[0] <= WAIT_MAX_S, f" (waited {clock[0]} s: {got!r})")
+    # 18-20: the own-run path polls a listing whose step rows lag (R10-HOTFIX-GATE-STALE-JOBS part 2, e350d851)
+    lag = lambda: [{"name": n, "status": "completed", "steps": [{"name": STEP, "conclusion": None}]} for n in CODEQL]   # noqa: E731
+    reads.clear()
+
+    def stale_then_fresh(path, params=None, headers=None):    # this run's step rows lag for two reads, then settle
+        if path.endswith("/runs/100/jobs"):
+            reads.append(path)
+        return world(A.THREE, plant, live, run_jobs={100: jobs() if len(reads) > 2 else lag()})(path, params, headers)
+
+    naps = []
+    try:
+        got = run(stale_then_fresh, repo, 100, pr, "main", False, sleep=naps.append, now=iter(range(0, 10_000, 1)).__next__)
+    except Fail as e:
+        got = f"FAIL {e}"
+    check("18 own run: a lagging step row is polled at the 60 s poll, then the leg is read, not dropped",
+          got == one and naps == [POLL_S, POLL_S], f" (got {got!r}, slept {naps})")
+    try:
+        got = run(world(A.THREE, plant, live, run_jobs={100: lag()}), repo, 100, pr, "main", False, **nosleep,
+                  now=iter(range(0, 10_000, 100)).__next__)
+    except Fail as e:
+        got = f"FAIL {e}"
+    check("19 own run: a step row still lagging at the bound FAILs, never passes", str(got).startswith("FAIL this run's codeql"), f" ({got!r})")
+    reads.clear()
+    check("20 null: a settled stand-down (step skipped) is not waited for",
+          go(world(A.THREE[1:], A.EMPTY, [], run_jobs={100: jobs(skip=("python",))})) == [])
     print(f"codescan_wait self-test: {n} checks, {bad} failed")
     return 1 if bad else 0
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
