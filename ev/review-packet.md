# Review packet #3263
head: b0ef8f54964a832950dce1ddd02423f3cfb60aa8
base: 28482eceeb6b9809e44b12d80fc994282cc21645

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128206588947 success
arch-score / arch-score id=128206554771 success
arm id=128206410086 skipped
budget-raise-gate / budget-raise-gate id=128206554934 success
cancel-superseded id=128206356194 success
codeql id=128206556065 skipped
codeql / Analyze (actions) id=128206518212 success
codeql / Analyze (javascript-typescript) id=128206518181 success
codeql / Analyze (python) id=128206518087 success
gate id=128206881487 failure
governance id=128206556173 skipped
governance / delivery-status id=128206518360 success
governance / delivery-status-publish id=128206520758 skipped
governance / env-matrix id=128206518255 in_progress
governance / instrument-self-tests id=128206518254 in_progress
governance / policy-docs id=128206518423 success
governance / record id=128206520483 skipped
governance / wave-script id=128206518482 success
hassfest id=128206556084 skipped
hassfest / hassfest id=128206518102 success
kernel-points id=128206556960 skipped
pr-contract id=128206884286 skipped
prelude id=128206355802 success
refresh id=128206355793 success
tests id=128206557037 skipped
tests / arch-instrument id=128206739697 success
tests / briefs id=128206518266 success
tests / browser id=128206739613 success
tests / closure-scope id=128206518396 success
tests / closures id=128206739718 in_progress
tests / coverage id=128206739531 in_progress
tests / fast (3.14) id=128206739676 in_progress
tests / mutation id=128206518192 success
tests / mutation-autofix id=128206843255 skipped
tests / mutation-pins id=128206841207 skipped
tests / nightly-ha id=128206742365 skipped
tests / nightly-status id=128206518269 success
tests / replay id=128206741792 skipped
tests / typing id=128206739585 success
validate id=128206557049 skipped
validate / validate-hacs id=128206518049 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at b0ef8f54964a832950dce1ddd02423f3cfb60aa8

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified git diff --stat origin/main...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff origin/main -- VERSION RELEASE_NOTES.md tests/golden .github | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 4 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3263.md b/dev/programme/delivery/3263.md
new file mode 100644
index 000000000..34f0f08f1
--- /dev/null
+++ b/dev/programme/delivery/3263.md
@@ -0,0 +1 @@
+- [#3263](https://github.com/tvofi/heatpump_optimizer/pull/3263) — **open**, R10-HOTFIX-NIGHTLY-STATUS: nightly-status no longer grades main red on a rolling nightly (R10-HOTFIX-NIGHTLY-STATUS)
diff --git a/tests/entities.py b/tests/entities.py
index 1a257bf95..94c1962b8 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -27286,6 +27286,44 @@ R.check(
     "11 and 12, i.e. a two-night-old run reported as last night's",
 )
 
+# --- a failure a newer in-flight run has already answered (2026-11-06) -------
+#
+# Dispatch 42235215315 (14:35Z) concluded `failure` on `slow`; 42242870295 and
+# 42247578523 passed `slow` while their 3.5 h mutation lanes ran on, and the
+# check kept naming the stale failure. Null controls: the same failure with
+# nothing newer, with a newer `slow` failed or still pending, or with a newer
+# run that is OLDER, must all stay red.
+_ns_bad = _ns_run(21, "2026-09-10T02:17:00Z", conclusion="failure")
+_ns_badjobs = [j if j["name"] != "slow" else _ns_job("slow", "failure")
+               for j in _NS_LIVE]
+_ns_newer = _ns_run(22, "2026-09-10T08:00:00Z", "in_progress", None)
+_ns_older = _ns_run(20, "2026-09-09T08:00:00Z", "in_progress", None)
+_ns_green = [_ns_job("slow", "success"), _ns_job("mutation-nightly", None)]
+_ns_cases = {
+    "superseded": _nstatus.verdict(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW,
+                                   in_flight_jobs=_ns_green)[0],
+    "nothing newer": _nstatus.verdict(_ns_bad, None, _ns_badjobs, _NS_NOW)[0],
+    "newer slow failed": _nstatus.verdict(
+        _ns_bad, _ns_newer, _ns_badjobs, _NS_NOW,
+        in_flight_jobs=[_ns_job("slow", "failure")])[0],
+    "newer slow pending": _nstatus.verdict(
+        _ns_bad, _ns_newer, _ns_badjobs, _NS_NOW,
+        in_flight_jobs=[_ns_job("slow", None)])[0],
+    "in-flight older": _nstatus.verdict(
+        _ns_bad, _ns_older, _ns_badjobs, _NS_NOW,
+        in_flight_jobs=_ns_green)[0],
+}
+R.check(
+    "a failed lane is superseded only by a NEWER in-flight run that "
+    "concluded the same job green; every other arm stays FAILED",
+    _ns_cases == {"superseded": _nstatus.PASSED,
+                  "nothing newer": _nstatus.FAILED,
+                  "newer slow failed": _nstatus.FAILED,
+                  "newer slow pending": _nstatus.FAILED,
+                  "in-flight older": _nstatus.FAILED},
+    f"states {_ns_cases}",
+)
+
 # --- a run with no clock is "could not look", not a crash and not a verdict --
 #
 # `parse_ts(r["created_at"])` raised KeyError straight through `main`'s
diff --git a/tests/nightly_status.py b/tests/nightly_status.py
index 260808149..42140228b 100644
--- a/tests/nightly_status.py
+++ b/tests/nightly_status.py
@@ -409,6 +409,7 @@ def verdict(
     now: dt.datetime,
     max_age_nights: int = MAX_AGE_NIGHTS,
     workflow: dict | None = None,
+    in_flight_jobs: list[dict] | None = None,
 ) -> tuple[str, int, list[str]]:
     """Classify. Returns (state, exit code, report lines).
 
@@ -475,6 +476,30 @@ def verdict(
     run_conclusion = concluded.get("conclusion")
     run_failed = run_conclusion not in OK_CONCLUSIONS
     bad = failing_jobs(jobs)
+    # SUPERSEDED FAILURES. The nightly takes ~3.5 h (mutation-nightly and the
+    # ledger push run last), so a NEWER run is routinely still in flight when
+    # this reads; "the newest CONCLUDED run" then names a run a later one has
+    # already answered. On 2026-11-06 `slow` failed in dispatch 42235215315
+    # (14:35Z) and passed in 42242870295 and 42247578523 while their
+    # mutation lanes ran on, and this check stayed red on every pull request
+    # for hours. A failed job is superseded ONLY when a strictly newer
+    # in-flight run has already concluded the SAME job green. A job still
+    # pending, failed, skipped or absent there supersedes nothing, so a lane
+    # that is really red stays red.
+    superseded: list[dict] = []
+    if bad and in_flight is not None and in_flight_jobs and parse_ts(
+            in_flight.get("created_at")) > started:
+        greens = {j.get("name") for j in in_flight_jobs
+                  if j.get("conclusion") == "success"}
+        superseded = [j for j in bad if j.get("name") in greens]
+        if len(superseded) == len(bad):
+            where.append(
+                "  failed job(s) superseded by the newer in-flight run "
+                f"{in_flight['id']}, which already concluded them green: "
+                + ", ".join(sorted(j.get("name", "?") for j in bad)))
+            bad, run_failed = [], False
+        else:
+            superseded = []
     if bad or run_failed:
         if bad:
             names = ", ".join(sorted(j.get("name", "?") for j in bad))
@@ -690,8 +715,17 @@ def main(argv: list[str] | None = None) -> int:
         concluded, in_flight, jobs, record = collect(
             args.repo, args.workflow, os.environ.get("GITHUB_TOKEN"), args.run,
             args.default_branch, now, args.max_age_nights)
+        fly_jobs = None
+        if (in_flight is not None and concluded is not None
+                and failing_jobs(jobs)):
+            try:
+                fly_jobs = _jobs(args.repo, in_flight["id"],
+                                 os.environ.get("GITHUB_TOKEN"))
+            except Unreadable:
+                fly_jobs = None  # no jobs yet: supersedes nothing
         state, code, lines = verdict(
-            concluded, in_flight, jobs, now, args.max_age_nights, record)
+            concluded, in_flight, jobs, now, args.max_age_nights, record,
+            fly_jobs)
     except Unreadable as exc:
         state, code = UNREADABLE, EXIT_UNREADABLE
         lines = [

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
