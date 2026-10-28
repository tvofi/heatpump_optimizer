# Review packet #2918
head: c44e95fe3b826fa2d17b6c8ddb3877a62840b850
base: eab04d0ebf8c45667099b668ab0d8bf976d5f99a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=122984074060 neutral
arch-score / arch-score id=122983038706 success
arm id=122978002443 skipped
budget-raise-gate / budget-raise-gate id=122983038928 success
cancel-superseded id=122978007050 success
codeql / Analyze (actions) id=122983038410 success
codeql / Analyze (javascript-typescript) id=122983038439 success
codeql / Analyze (python) id=122983038599 in_progress
governance / delivery-status id=122983038663 success
governance / delivery-status-publish id=122983041980 skipped
governance / env-matrix id=122983038731 in_progress
governance / instrument-self-tests id=122983038770 in_progress
governance / policy-docs id=122983039066 queued
governance / record id=122983041832 skipped
governance / wave-script id=122983038632 in_progress
hassfest / hassfest id=122983038484 success
kernel-points id=122983040031 skipped
prelude id=122978007356 in_progress
refresh id=122978006545 success
tests / arch-instrument id=122984594707 queued
tests / briefs id=122983038492 success
tests / browser id=122984594571 queued
tests / closure-scope id=122983038480 success
tests / closures id=122984594506 in_progress
tests / coverage id=122984594468 in_progress
tests / fast (3.14) id=122984594839 queued
tests / mutation id=122983038637 in_progress
tests / nightly-ha id=122984597857 skipped
tests / nightly-status id=122983038577 success
tests / replay id=122984597922 skipped
tests / typing id=122984594738 queued
validate / validate-hacs id=122983038324 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git show origin/main:.github/workflows/nightly.yml
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/nightly.yml b/.github/workflows/nightly.yml
index 1daaa035d..fd46def88 100644
--- a/.github/workflows/nightly.yml
+++ b/.github/workflows/nightly.yml
@@ -946,6 +946,25 @@ jobs:
                     || echo "::warning::dismissing the approver App's review $rid on #$NUM failed"
                 done
           }
+          HEAD=$(pr_field 'd["head"]["sha"]') || {
+            echo "::warning::record pull request #$NUM is unreadable"; say skip-unread; exit 0; }
+          if ! guard; then
+            echo "::warning::the automerge guard refused #$NUM at $HEAD; it keeps the manual review"
+            dismiss_bot; say refused; exit 0
+          fi
+          if [ -n "$APPROVER" ]; then
+            # One approving review per head: a held beat sees the same head again.
+            have=$(curl -fsS -H "$AUTH" -H "$ACCEPT" "$API/repos/$REPO/pulls/$NUM/reviews?per_page=100" \
+              | python3 -I -c 'import sys,json; h=sys.argv[1]; print(any(r.get("state")=="APPROVED" and r.get("commit_id")==h and (r.get("user") or {}).get("login")=="hpo-approver[bot]" for r in json.load(sys.stdin)))' "$HEAD") \
+              || { say skip-unread; exit 0; }
+            if [ "$have" != True ]; then
+              python3 -I -c 'import json,sys; print(json.dumps({"commit_id": sys.argv[1], "event": "APPROVE", "body": "Automerge guard: row-only record pull request at " + sys.argv[1] + "; tools/audit/seat/record_row.py --automerge-check passed (tvofi, 2026-10-07)."}))' "$HEAD" \
+                > "$RUNNER_TEMP/review.json"
+              curl -fsS -o /dev/null -X POST -H "Authorization: Bearer $APPROVER" -H "$ACCEPT" \
+                -d @"$RUNNER_TEMP/review.json" "$API/repos/$REPO/pulls/$NUM/reviews" || {
+                echo "::warning::the approver App's review on #$NUM was refused"; say skip-review-refused; exit 0; }
+            fi
+          fi
           # THE TRAIN HOLD (R10-TRAIN-HOLD, issue #2302). A merge train
           # merges pull requests itself, and a record pull request landing
           # from this beat while it waits on CI moves main under it: #2291,
@@ -956,7 +975,7 @@ jobs:
           # its closing line (hold_refresh/hold_release). The ref points at a
           # commit made at publication, whose committer date is the age here:
           # younger than HOLD_MAX_AGE_S is a live train, so the pull request
-          # stays open for a later beat; at or past it the hold is stale (a
+          # is not merged here; at or past it the hold is stale (a
           # crashed train moved nothing, so no rows went overdue) and this
           # beat proceeds. The train refreshes the ref on every queue item,
           # every recarry and before every CI-wait sleep, so the longest gap
@@ -969,7 +988,13 @@ jobs:
           # "No commit found for SHA" for an absent ref (measured live
           # 2026-10-20), not 404, so both arms are the silent absence; any
           # other code is logged. record_row.py's own --automerge-check is
-          # untouched.
+          # untouched. AFTER the guard and the approver App's review, before
+          # the pitch and the merge (V118): only a merge moves main, and the
+          # train's --bot-prs sweep merges on the guard alone and leaves the
+          # review to this beat, so a hold ahead of the review left a record
+          # pull request unreviewed while trains ran back to back (#2856,
+          # about 3 h). A held beat still dismisses on a refusal and posts
+          # the one approving review per head; it never merges.
           HOLD_REF=train-hold
           HOLD_MAX_AGE_S=3600
           hold_code=$(curl -sS -o "$RUNNER_TEMP/train-hold.json" -w '%{http_code}' \
@@ -999,25 +1024,6 @@ jobs:
           elif [ "$hold_code" != 404 ] && [ "$hold_code" != 422 ]; then
             echo "::warning::the train hold is unreadable (HTTP $hold_code); treated as absent"
           fi
-          HEAD=$(pr_field 'd["head"]["sha"]') || {
-            echo "::warning::record pull request #$NUM is unreadable"; say skip-unread; exit 0; }
-          if ! guard; then
-            echo "::warning::the automerge guard refused #$NUM at $HEAD; it keeps the manual review"
-            dismiss_bot; say refused; exit 0
-          fi
-          if [ -n "$APPROVER" ]; then
-            # One approving review per head: a held beat sees the same head again.
-            have=$(curl -fsS -H "$AUTH" -H "$ACCEPT" "$API/repos/$REPO/pulls/$NUM/reviews?per_page=100" \
-              | python3 -I -c 'import sys,json; h=sys.argv[1]; print(any(r.get("state")=="APPROVED" and r.get("commit_id")==h and (r.get("user") or {}).get("login")=="hpo-approver[bot]" for r in json.load(sys.stdin)))' "$HEAD") \
-              || { say skip-unread; exit 0; }
-            if [ "$have" != True ]; then
-              python3 -I -c 'import json,sys; print(json.dumps({"commit_id": sys.argv[1], "event": "APPROVE", "body": "Automerge guard: row-only record pull request at " + sys.argv[1] + "; tools/audit/seat/record_row.py --automerge-check passed (tvofi, 2026-10-07)."}))' "$HEAD" \
-                > "$RUNNER_TEMP/review.json"
-              curl -fsS -o /dev/null -X POST -H "Authorization: Bearer $APPROVER" -H "$ACCEPT" \
-                -d @"$RUNNER_TEMP/review.json" "$API/repos/$REPO/pulls/$NUM/reviews" || {
-                echo "::warning::the approver App's review on #$NUM was refused"; say skip-review-refused; exit 0; }
-            fi
-          fi
           # THE PITCH (R10-FLOW-RECORD-PITCH, Lean study K6). A record merge
           # moves main under every open head, so a push beat leaves the pull
           # request for the train's --bot-prs sweep while the last record
diff --git a/dev/programme/delivery/2918.md b/dev/programme/delivery/2918.md
new file mode 100644
index 000000000..0b541aade
--- /dev/null
+++ b/dev/programme/delivery/2918.md
@@ -0,0 +1 @@
+- [#2918](https://github.com/tvofi/heatpump_optimizer/pull/2918) — **open**, fix(nightly): post the record review before the train hold (R10-RECORD-HOLD-APPROVE) (R10-RECORD-HOLD-APPROVE)
diff --git a/tests/entities.py b/tests/entities.py
index 5562214e6..aedec24e3 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -28315,9 +28315,12 @@ R.check(
 # younger than the step's bound: the beat auto-merged mid-train on 2026-10-15
 # (#2291, #2295, #2299), moving main under #2284 and #2290, which CI cannot
 # see because the train's pidfile is local. THE STEP IS EXECUTED, over a
-# stubbed API: the status it prints is what proves the skip happens before the
-# guard and the merge, so a check placed after them (or an inverted age
-# comparison) cannot pass. The bound is read from the step, never carried.
+# stubbed API: the status it prints and the calls it makes are what prove the
+# skip happens after the guard and the approver App's review and before the
+# merge (V118: a hold ahead of the review left #2856 unreviewed while trains
+# ran back to back, since the train's --bot-prs sweep merges on the guard
+# alone), so a check placed elsewhere (or an inverted age comparison) cannot
+# pass. The bound is read from the step, never carried.
 _HOLD_STEP = next((s for s in ((_yaml.safe_load(_NIGHTLY_YML) or {}).get("jobs") or {})
                    .get("record-autofix", {}).get("steps") or []
                    if str(s.get("id") or "") == "automerge"), {})
@@ -28330,7 +28333,8 @@ _MT_HOLD_REF = re.search(r'(?m)^HOLD_REF = "refs/heads/([\w.-]+)"',
 
 
 def _train_hold_status(code: int, body: str, pitch_rc: int = 0, guard_rc: int = 1,
-                       approver: str = "", calls: "list | None" = None) -> "tuple[str, bool]":
+                       approver: str = "", calls: "list | None" = None, green_rc: int = 1,
+                       reviews: str = "[]", run: str = "") -> "tuple[str, bool]":
     """The automerge step's `status=` and whether it warned "unreadable" over a
     stubbed API whose train-hold read answers (code, body); every other read is
     the minimum the step needs.
@@ -28345,19 +28349,21 @@ def _train_hold_status(code: int, body: str, pitch_rc: int = 0, guard_rc: int =
     `pitch_rc` is what the stub answers `--pitch-check` with: 0 no pitch (the
     default, so the hold's own arms read as before), 4 the pitch's wait.
     `guard_rc` is the first guard's exit (the refusing default; 0 passes it,
-    and the green wait after it still refuses), `approver` the approver App's
-    token, and `calls`, when given, receives every curl argv the step ran."""
+    and the green wait after it refuses unless `green_rc` is 0), `approver` the
+    approver App's token, `reviews` the pull request's reviews read, `run` a
+    step text in place of the step's own (a mutant), and `calls`, when given,
+    receives every curl argv the step ran."""
     with tempfile.TemporaryDirectory() as td:
         t = Path(td)
         (t / "tools" / "audit" / "seat").mkdir(parents=True)
         (t / "tools" / "audit" / "seat" / "record_row.py").write_text(
-            f"import sys\nsys.exit({pitch_rc} if '--pitch-check' in sys.argv else 1 "
-            f"if '--require-green' in sys.argv else {guard_rc})\n")
+            f"import sys\nsys.exit({pitch_rc} if '--pitch-check' in sys.argv else "
+            f"{green_rc} if '--require-green' in sys.argv else {guard_rc})\n")
         answers = t / "answers.json"
         answers.write_text(json.dumps({
             "hold": {"code": code, "body": body},
             "pulls": {"code": 200, "body": json.dumps({"head": {"sha": "a" * 40}})},
-            "reviews": {"code": 200, "body": "[]"},
+            "reviews": {"code": 200, "body": reviews},
             "other": {"code": 404, "body": "{}"}}))
         bin_ = t / "bin"
         bin_.mkdir()
@@ -28383,7 +28389,7 @@ def _train_hold_status(code: int, body: str, pitch_rc: int = 0, guard_rc: int =
         (bin_ / "curl").chmod(0o755)
         out = t / "out"
         out.write_text("")
-        p = subprocess.run(["bash", "-c", _HOLD_RUN], cwd=t, capture_output=True, text=True,
+        p = subprocess.run(["bash", "-c", run or _HOLD_RUN], cwd=t, capture_output=True, text=True,
                            env={**os.environ, "PATH": str(bin_) + os.pathsep + os.environ["PATH"],
                                 "RUNNER_TEMP": str(t), "GITHUB_OUTPUT": str(out),
                                 "REPO": "o/r", "TOKEN": "t0k", "APPROVER": approver, "NUM": "42",
@@ -28402,30 +28408,82 @@ def _hold_when(offset_s: int) -> str:
         "date": at.strftime("%Y-%m-%dT%H:%M:%SZ")}}})
 
 
-R.check(
-    "tests.yml's automerge skips while a live merge train holds the record "
-    "beat (executed, issue #2302)",
-    _HOLD_BOUND > 0
-    and _train_hold_status(200, _hold_when(-60)) == ("skip-train-hold", False),
-    f"bound={_HOLD_BOUND}, "
-    f"status={_train_hold_status(200, _hold_when(-60))!r}",
+def _hold_calls(code: int, body: str, **kw) -> "tuple[str, bool, bool, bool]":
+    """(status, approver review posted, a review dismissed, merge called) for one
+    run of the automerge step with the approver App's token present."""
+    calls: list = []
+    st, _ = _train_hold_status(code, body, approver="ap0", calls=calls, **kw)
+    return (st,
+            any("POST" in c and "Authorization: Bearer ap0" in c
+                and c[-1].endswith("/pulls/42/reviews") for c in calls),
+            any("PUT" in c and c[-1].endswith("/dismissals") for c in calls),
+            any(c[-1].endswith("/merge") for c in calls))
+
+
+# A bot approval at an older head, so a refusal has one to dismiss.
+_HOLD_OLD_REVIEW = json.dumps([{"id": 7, "state": "APPROVED", "commit_id": "b" * 40,
+                                "user": {"login": "hpo-approver[bot]"}}])
+_HELD = _hold_calls(200, _hold_when(-60), guard_rc=0)
+_HELD_REFUSED = _hold_calls(200, _hold_when(-60), reviews=_HOLD_OLD_REVIEW)
+R.check(
+    "nightly.yml's automerge reviews a record pull request the guard passes "
+    "under a live merge train hold, then skips the merge (executed, issue "
+    "#2302, V118)",
+    _HOLD_BOUND > 0 and _HELD == ("skip-train-hold", True, False, False),
+    f"bound={_HOLD_BOUND}, (status, reviewed, dismissed, merged)={_HELD!r}; the "
+    "train's --bot-prs sweep merges on the guard alone and leaves the review "
+    "to this beat, so a hold ahead of the review starves it (#2856)",
+)
+R.check(
+    "and under a live hold a head the guard refuses is refused, its approver "
+    "App approvals dismissed and no review posted",
+    _HELD_REFUSED == ("refused", False, True, False),
+    f"(status, reviewed, dismissed, merged)={_HELD_REFUSED!r}",
+)
+# The mutant: the hold block moved back ahead of the head read, the guard and
+# the review -- the order #2856 deadlocked under. Built from the step's own
+# text, so it tracks the block; a mutant that cannot be built is red.
+_HOLD_A = _HOLD_RUN.find("# THE TRAIN HOLD (")
+_HOLD_B = _HOLD_RUN.find("# THE PITCH (")
+_HOLD_H = _HOLD_RUN.find("HEAD=$(pr_field")
+_HOLD_MUT_OK = -1 < _HOLD_H < _HOLD_A < _HOLD_B
+_HOLD_A, _HOLD_B, _HOLD_H = (_HOLD_RUN.rfind("\n", 0, i) + 1 for i in (_HOLD_A, _HOLD_B, _HOLD_H))
+_HOLD_MUT = (_HOLD_RUN[:_HOLD_H] + _HOLD_RUN[_HOLD_A:_HOLD_B] + _HOLD_RUN[_HOLD_H:_HOLD_A]
+             + _HOLD_RUN[_HOLD_B:])
+_HELD_MUT = _hold_calls(200, _hold_when(-60), guard_rc=0, run=_HOLD_MUT) if _HOLD_MUT_OK else None
+R.check(
+    "and the hold moved back ahead of the review leaves the held head "
+    "unreviewed, so the reviewed-under-a-live-hold check sees it (mutant)",
+    _HOLD_MUT_OK and _HELD_MUT == ("skip-train-hold", False, False, False),
+    f"order ok={_HOLD_MUT_OK}, mutant (status, reviewed, dismissed, merged)={_HELD_MUT!r}",
 )
 R.check(
     "and a hold at the bound, one dated ahead of the runner's clock, an absent "
     "one (the API's own 422) and an unreadable one do not skip -- and only the "
     "unreadable ones warn (null controls)",
     _HOLD_BOUND > 0
-    and _train_hold_status(200, _hold_when(-(_HOLD_BOUND + 60))) == ("refused", False)
-    and _train_hold_status(200, _hold_when(3600)) == ("refused", False)
-    and _train_hold_status(422, "{}") == ("refused", False)
-    and _train_hold_status(404, "{}") == ("refused", False)
-    and _train_hold_status(500, "{}") == ("refused", True)
-    and _train_hold_status(200, "{}") == ("refused", True),
+    and _train_hold_status(200, _hold_when(-(_HOLD_BOUND + 60)), guard_rc=0)
+    == ("refused", False)
+    and _train_hold_status(200, _hold_when(3600), guard_rc=0) == ("refused", False)
+    and _train_hold_status(422, "{}", guard_rc=0) == ("refused", False)
+    and _train_hold_status(404, "{}", guard_rc=0) == ("refused", False)
+    and _train_hold_status(500, "{}", guard_rc=0) == ("refused", True)
+    and _train_hold_status(200, "{}", guard_rc=0) == ("refused", True),
     "a stale hold is a crashed train (no merges, so no rows go overdue); a "
     "date ahead of the reading clock is unknowable, never young (#775); the "
     "commits endpoint answers 422 for an absent ref, so that arm must be "
     "silent or every idle beat warns; an unreadable hold leaves the pre-fix "
-    "behaviour, which is the safe failure",
+    "behaviour, which is the safe failure. The guard passes, so the hold is "
+    "read; the green wait, stubbed to refuse, reports `refused`",
+)
+_HOLD_NONE = _hold_calls(422, "{}", guard_rc=0, green_rc=0)
+_HOLD_STALE = _hold_calls(200, _hold_when(-(_HOLD_BOUND + 60)), guard_rc=0, green_rc=0)
+R.check(
+    "and with no hold, or a stale one, a passing head is reviewed, passes the "
+    "pitch and merges as before (null control)",
+    _HOLD_NONE == ("merged", True, False, True)
+    and _HOLD_STALE == ("merged", True, False, True),
+    f"absent: {_HOLD_NONE!r}; stale: {_HOLD_STALE!r}",
 )
 # THE PITCH (R10-FLOW-RECORD-PITCH, Lean study K6), executed over the same
 # stub: record_row.py's `--pitch-check` answering 4 skips the merge with
@@ -28434,7 +28492,7 @@ R.check(
 # posts no review -- finds a head main's ruleset accepts (directive [7]:
 # record pull requests ride trains rather than race them). 0 proceeds to the
 # green wait; a crashed check is no pitch; a refused head never waits; a live
-# train answers first, so the hold arm is unchanged by it. The decision itself
+# train answers before the pitch, so the hold arm is unchanged by it. The decision itself
 # (a young record merge waits, a stale backlog proceeds) is record_row.py's
 # `pitch_wait`, driven both ways by its --self-test.
 _PITCH_CALLS: list = []
@@ -28445,7 +28503,7 @@ _PITCH_REVIEWED = any("POST" in c and "Authorization: Bearer ap0" in c
 _PITCH_MERGED = any(c[-1].endswith("/merge") for c in _PITCH_CALLS)
 R.check(
     "nightly.yml's automerge waits the pitch when record_row.py says so, after "
-    "the train hold, the guard and the approver App's review, before the merge "
+    "the guard, the approver App's review and the train hold, before the merge "
     "(executed)",
     _PITCH_ST == ("skip-pitch", False) and _PITCH_REVIEWED and not _PITCH_MERGED
     and _train_hold_status(200, _hold_when(-60), pitch_rc=4, guard_rc=0)

