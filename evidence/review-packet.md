# Review packet #3904
head: de0b44670aa52b08abed9bfa6419d71049384174
base: 658fcae30b8db6e984de1a7bdd7066951a804686

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139621304902 success
arch-score / arch-score id=139623020021 success
arm id=139619851494 skipped
budget-raise-gate / budget-raise-gate id=139623019887 success
cancel-superseded id=139619902359 success
codeql id=139623021441 skipped
codeql / Analyze (actions) id=139620327714 success
codeql / Analyze (javascript-typescript) id=139620327692 success
codeql / Analyze (python) id=139620327756 success
gate id=139625975835 failure
governance id=139623021335 skipped
governance / env-matrix id=139620327782 success
governance / instrument-self-tests id=139620327931 success
governance / policy-docs id=139620327935 success
governance / record id=139620329768 skipped
governance / wave-script id=139620327839 success
hassfest id=139623022650 skipped
hassfest / hassfest id=139620327665 success
kernel-points id=139623022321 skipped
pr-contract id=139625977642 skipped
prelude id=139619902501 success
refresh id=139619902269 success
sweep-self id=139626423859 skipped
tests id=139623021125 skipped
tests / arch-instrument id=139624716434 in_progress
tests / briefs id=139620327812 success
tests / browser id=139624716388 success
tests / closure-scope id=139620327818 success
tests / closures id=139624716439 in_progress
tests / coverage id=139624716449 in_progress
tests / fast (3.14) id=139624716513 in_progress
tests / mutation id=139620327766 success
tests / mutation-autofix id=139622215973 skipped
tests / mutation-pins id=139622214858 skipped
tests / nightly-ha id=139624718691 skipped
tests / nightly-status id=139620327836 failure
tests / replay id=139624718145 skipped
tests / typing id=139624716418 success
validate id=139623021422 skipped
validate / validate-hacs id=139620327718 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at de0b44670aa52b08abed9bfa6419d71049384174 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head de0b44670aa52b08abed9bfa6419d71049384174, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 452c2f17c4..0c108be76d 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -66,14 +66,14 @@ permissions: {}
 
 # A group per run (rev2, N1): `refresh` and gate-sweep.yml re-run `gate` jobs,
 # and a re-run re-enters its run's group, so a group shared between runs would
-# let a re-run cancel a pending run. Supersession is cancel-superseded's alone.
-# Except a push to main's first attempt (CI-5, owner 2026-11-21): one `CI-main`
-# group, cancelling nothing in progress, so one push run executes at a time and
-# GitHub replaces a pending one with the newest before it starts; a burst of
-# merges is graded once, at its last tip, and no started run is cancelled. A
-# re-run (attempt 2+) keeps its run-id group, so it never displaces that tip.
+# let a re-run cancel a pending run. A push to main's run is no exception
+# (owner 2026-11-25, retiring CI-5's `CI-main` group): every main push run
+# starts at once, and supersession is the cancellers' alone -- this file's
+# cancel-superseded job for a pull request, and for main main-cancel.yml, which
+# cancels the older active main push runs when the new push is graded in full,
+# never past three main runs with no concluded verdict.
 concurrency:
-  group: ${{ github.event_name == 'push' && github.run_attempt == '1' && 'CI-main' || format('CI-{0}', github.run_id) }}
+  group: ${{ format('CI-{0}', github.run_id) }}
   cancel-in-progress: false
 
 jobs:
diff --git a/.github/workflows/main-cancel.yml b/.github/workflows/main-cancel.yml
index b5e8b17ead..5b453022c2 100644
--- a/.github/workflows/main-cancel.yml
+++ b/.github/workflows/main-cancel.yml
@@ -7,9 +7,10 @@
 # sat queued past `pause_queued_min` (ci_pause's signal: GitHub is not
 # granting runners), and cancels nothing for a light push.
 #
-# Not a job of ci.yml: its workflow-level `CI-main` group holds this push's
-# run pending until the older one finishes, so no job of it could cancel
-# that run. No `concurrency:` here: two pushes' runs overlap, and the older
+# Not a job of ci.yml: a canceller there runs only once its run starts, and
+# every main push run of ci.yml starts at once (a group per run; CI-5's
+# `CI-main` group is retired), so this workflow is the one place main
+# supersession is decided, independent of ci.yml's runners. No `concurrency:` here: two pushes' runs overlap, and the older
 # push's finds a newer run listed and cancels nothing. Fail-soft: the cancel
 # is an optimisation, never a gate -- the step always exits 0.
 
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index 72728a7a1d..ae96fc9e2f 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -866,7 +866,7 @@ jobs:
             BASE=$(git rev-parse HEAD)
             # The range base (#3885) where the prelude read one: the head of the
             # last push run whose units ran, so the entry it saved. HEAD^1's run
-            # may have been replaced while pending (CI-5) and saved none.
+            # may have been cancelled as superseded (main-cancel.yml) and saved none.
             RESTORE_BASE=$(git rev-parse "${RANGE_BASE:-HEAD^1}")
           else
             BASE=$(git merge-base origin/main HEAD)
diff --git a/dev/programme/delivery/3904.md b/dev/programme/delivery/3904.md
new file mode 100644
index 0000000000..33f165eb97
--- /dev/null
+++ b/dev/programme/delivery/3904.md
@@ -0,0 +1 @@
+- [#3904](https://github.com/tvofi/heatpump_optimizer/pull/3904) — **open**, ci(#3885): each main push run gets its own CI group; main-cancel.yml cancels older ones (ci-3885)
diff --git a/tests/entities.py b/tests/entities.py
index 3ffc926f86..338533a937 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -21404,15 +21404,15 @@ def _ci_umbrella_defects(doc: dict, text: str) -> "list[str]":
                 out.append(f"`on:` lists {ev}/{a}, which no model here renders")
     if doc.get("permissions") != {}:
         out.append(f"workflow permissions {doc.get('permissions')!r}")
-    # CI-5 (owner 2026-11-21): a push's first attempt joins the one CI-main group, so a pending
-    # push run is replaced by the newest and none in progress is cancelled; every other run and
-    # every re-run keeps its run-id group (N1). Rendered per event and attempt, not matched as text.
+    # Every run and every re-run keeps its run-id group (N1), a push to main's included: no
+    # group serialises main push runs (owner 2026-11-25, retiring CI-5's `CI-main` group);
+    # main-cancel.yml cancels the superseded ones. Rendered per event and attempt, not as text.
     cc = doc.get("concurrency") or {}
     if cc.get("cancel-in-progress") is not False:
         out.append(f"concurrency {cc} cancels in progress")
     for (ev, a), payload in _CI_EVENTS.items():
         for attempt in ("1", "2"):
-            want = "CI-main" if ev == "push" and attempt == "1" else "CI-99"
+            want = "CI-99"
             got = _ghx(cc.get("group", ""), {**_ci_ctx(ev, payload)[0], "github.run_attempt": attempt})
             if got != want:
                 out.append(f"concurrency group under {ev}/{a} attempt {attempt} renders {got!r}, want {want!r}")
@@ -21524,11 +21524,13 @@ _CI_PLANTS = {
     "labeled dropped": _CI_TEXT.replace("edited, labeled]", "edited]", 1),
     "a group per PR": _CI_TEXT.replace("format('CI-{0}', github.run_id)",
                                        "format('CI-{0}', github.event.pull_request.number)", 1),
-    "push re-runs in the main group": _CI_TEXT.replace(" && github.run_attempt == '1' && 'CI-main'", " && 'CI-main'", 1),
-    "every push in its own group": _CI_TEXT.replace(" && 'CI-main' ||", " && format('CI-{0}', github.run_id) ||", 1),
-    "the main group cancelling in progress": _CI_TEXT.replace(
-        "'CI-main' || format('CI-{0}', github.run_id) }}\n  cancel-in-progress: false",
-        "'CI-main' || format('CI-{0}', github.run_id) }}\n  cancel-in-progress: true", 1),
+    "push runs serialised in one main group (CI-5)": _CI_TEXT.replace(
+        "group: ${{ format('CI-{0}', github.run_id) }}",
+        "group: ${{ github.event_name == 'push' && github.run_attempt == '1' && 'CI-main'"
+        " || format('CI-{0}', github.run_id) }}", 1),
+    "a run-id group cancelling in progress": _CI_TEXT.replace(
+        "format('CI-{0}', github.run_id) }}\n  cancel-in-progress: false",
+        "format('CI-{0}', github.run_id) }}\n  cancel-in-progress: true", 1),
     "gate skippable on merge_group": _CI_TEXT.replace(
         "    if: ${{ !cancelled() }}\n", "    if: ${{ !cancelled() && github.event_name != 'merge_group' }}\n", 1),
     "gate skipped when the prelude fails": _CI_TEXT.replace(
@@ -21574,7 +21576,7 @@ _CI_PLANT_MISSED = sorted(k for k, t in _CI_PLANTS.items()
                           if t == _CI_TEXT or not _ci_umbrella_defects(_yaml.safe_load(t) or {}, t))
 R.check(
     "the CI umbrella: DESIGN-P2's triggers with labeled and merge_group, a "
-    "run-name equal to prelude.title, one run per group but a push's first attempt (CI-main, CI-5), "
+    "run-name equal to prelude.title, one run per group, a push to main's included (no CI-main), "
     "every unit called "
     "by its stem exactly when the prelude's workset names it, and a `gate` "
     "no event can skip, judging on the prelude's outputs (U0c)",
@@ -32707,11 +32709,10 @@ def _cc_pr_event(doc, run_id, sha, *, who="hpo-author[bot]", ev="pull_request"):
 _CC_TWIN_ROUTE = {
                   # The umbrella (U0c): every run in a run-id group (rev2, N1).
                   "ci.yml": "per-run"}
-# The (file, event) pairs whose first attempts share one group that cancels
-# nothing in progress, so GitHub replaces a pending run with the newest: CI-5's
-# push-to-main coalescing (owner 2026-11-21). A re-run keeps its run-id group
-# (the umbrella check above renders that per attempt).
-_CC_COALESCED = {("ci.yml", "push")}
+# No (file, event) pair shares a group across runs: CI-5's push-to-main
+# `CI-main` group is retired (owner 2026-11-25), so every main push run starts
+# at once and main-cancel.yml cancels the superseded ones.
+_CC_COALESCED: "set[tuple[str, str]]" = set()
 
 
 def _cc_lists_edited(doc: dict) -> bool:
@@ -32817,8 +32818,8 @@ R.check(
     "a same-SHA twin must survive",
 )
 # #3885: a superseded MAIN push run is cancelled from main-cancel.yml, never from
-# ci.yml, whose workflow-level `CI-main` group holds the newer push's run pending
-# until the older one ends. The job reads the push's prelude `scope` and hands it
+# ci.yml: a job of the newer run would need that run to start, and no main push
+# run waits on another (no `CI-main` group since 2026-11-25). The job reads the push's prelude `scope` and hands it
 # to `cancel_superseded.py main --scope`, which cancels only for `full`, within
 # the three-run bound and while GitHub grants runners (its self-test).
 def _mc_shape(doc: dict) -> bool:
diff --git a/tools/ci/prelude.py b/tools/ci/prelude.py
index be18e1424c..e4e85db410 100644
--- a/tools/ci/prelude.py
+++ b/tools/ci/prelude.py
@@ -622,8 +622,8 @@ def push_range(ctx: dict, get, diff=None, ancestor=None,
                cwd: Path = HERE.parents[1]) -> "tuple[str, list[str]] | None":
     """(base, the files changed base..head) for a push to main, or None (graded in full).
     The base is the head of the newest EARLIER push run on main that completed, was not
-    cancelled and whose prelude succeeded, so its units ran: CI-5's `CI-main` group
-    replaces a pending run, so HEAD^1 would leave the replaced run's commits graded by no
+    cancelled and whose prelude succeeded, so its units ran: main-cancel.yml cancels a
+    superseded run, so HEAD^1 would leave the cancelled run's commits graded by no
     run, and a production commit among them must never fall into a light range. A run
     whose prelude failed graded nothing, and its range stays in ours. None when the
     listing is unreadable, no such run is on its first page, or its head is not an

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
