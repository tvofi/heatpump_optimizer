# Review packet #3338
head: 930e1786863a0bfba7cbde0aa2e6dd246f9a4f11
base: 8a4974d1522f979f5b1c837df8e3a76b535bf35e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128798216081 success
arch-score / arch-score id=128831546722 success
arm id=128798075770 skipped
budget-raise-gate / budget-raise-gate id=128831529754 success
cancel-superseded id=128831544015 success
codeql id=128831537733 skipped
codeql / Analyze (actions) id=128831530032 success
codeql / Analyze (javascript-typescript) id=128831529890 success
codeql / Analyze (python) id=128831529863 success
gate id=128831531016 success
governance id=128831554453 skipped
governance / delivery-status id=128831555241 success
governance / delivery-status-publish id=128831530104 skipped
governance / env-matrix id=128831529894 success
governance / instrument-self-tests id=128831529998 success
governance / policy-docs id=128831559538 success
governance / record id=128831529728 skipped
governance / wave-script id=128831529820 success
hassfest id=128831536209 skipped
hassfest / hassfest id=128831569767 success
kernel-points id=128831530019 skipped
pr-contract id=128831553016 skipped
pr-contract / pr-contract id=128831531876 success
prelude id=128831570992 success
refresh id=128831529005 success
tests id=128831548343 skipped
tests / arch-instrument id=128831531113 success
tests / briefs id=128831530117 success
tests / browser id=128831530950 success
tests / ci-ratchet id=128831531115 skipped
tests / claims-autofix id=128831531522 skipped
tests / closure-scope id=128831556670 success
tests / closures id=128831531050 success
tests / closures-autofix id=128831530931 skipped
tests / coverage id=128831530796 success
tests / coverage-ratchet id=128831531712 success
tests / fast (3.14) id=128831530907 success
tests / graders-head-copy id=128831531154 success
tests / lane-proofs id=128831531570 success
tests / mutation id=128831530072 success
tests / mutation-autofix id=128831530948 skipped
tests / mutation-pins id=128831531088 skipped
tests / nightly-ha id=128831530761 skipped
tests / nightly-status id=128831529679 success
tests / replay id=128831530458 skipped
tests / typing id=128831530978 success
validate id=128831539026 skipped
validate / validate-hacs id=128831529893 success

## Refusals
none

## Advisories
none

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

## Three-dot diff
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 9d4cc79ff..eb1f7c6cd 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -97,9 +97,9 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
     git merge-tree --write-tree origin/main <head>
     ```
 
-    A non-zero exit names the conflicting paths. A conflict on any path other
-    than the two claim files is yours to block on, because you cannot know the
-    merged result is correct.
+    A non-zero exit names the conflicting paths. Block on main only on one,
+    never on a head behind main that merges cleanly (tvofi 11-07). A
+    conflict off the two claim files is yours.
 
     **The driver's verdict is in that command's stderr; read it, never infer it
     from the paths.** `merge-tree` invokes the driver once per conflicting claim
diff --git a/dev/programme/delivery/3338.md b/dev/programme/delivery/3338.md
new file mode 100644
index 000000000..610c1751b
--- /dev/null
+++ b/dev/programme/delivery/3338.md
@@ -0,0 +1 @@
+- [#3338](https://github.com/tvofi/heatpump_optimizer/pull/3338) — **open**, R10-FLY-DISPATCH-RULINGS: fly dispatch rulings (R10-FLY-DISPATCH-RULINGS)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index bd83906aa..f58b96a83 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -204,7 +204,9 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             "written unless the signal is `host-path`; re-read the live checks either way. "
             "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
             "every figure in the body at this head. Check that it merges with origin/main "
-            "(`git merge-tree --write-tree`). Wait for CI on this head only by re-running "
+            "(`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a "
+            "conflict, never on a head that is behind main but merges cleanly (the train re-proves it on "
+            "the current main). Wait for CI on this head only by re-running "
             f"`python3 tools/audit/seat/merge_train.py classify {head} --pr {pr}` in the background, at least "
             "60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) "
             "or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; "
@@ -243,10 +245,11 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"in a worktree of your own cut from origin/main. Fetch {head} for the base you were given.\n"
             f"Output: push each verified step, fast-forward only, to refs/heads/{WIP_NS}/{topic} before "
             f"any wait on a background run, so an idle container loses nothing; never step-push to "
-            f"handoff/{topic}, whose move updates the pull request. Before the handoff, when origin/main "
-            "has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun "
-            "`tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a "
-            "clean run (an unmoved main needs no second run: say so in the body). Then push the code to "
+            f"handoff/{topic}, whose move updates the pull request. Hand off at your first clean "
+            "`tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved "
+            "since that run needs no re-merge and no second run, because the train re-proves the head on the "
+            "current main. Merge origin/main and rerun prepr.sh only when "
+            "`git merge-tree --write-tree origin/main HEAD` reports a conflict. Then push the code to "
             f"refs/heads/handoff/{topic}, then write the PR body and run "
             f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
             f"refs/heads/handoff-body/{topic}; that second push is the return signal. Once it succeeds, "
@@ -1049,9 +1052,17 @@ def self_test() -> int:
           and f"except your return refs and {wip} and {wip}-body." in fx)
     check("the fixer deletes the step ref only after body_push.sh succeeds",
           0 <= fx.find("body_push.sh t-1") < fx.find(f"`git push origin :{wip}`"))
-    check("the fixer merges a moved origin/main and reruns prepr.sh before it pushes the handoff",
-          0 <= fx.find("`git merge origin/main`, rerun `tools/pr/prepr.sh`")
-          < fx.find("push the code to refs/heads/handoff/t-1"))
+    check("the fixer hands off at its first clean prepr.sh head and re-merges main only on a merge-tree conflict",
+          "Hand off at your first clean `tools/pr/prepr.sh` head" in fx
+          and "needs no re-merge and no second run" in fx
+          and 0 <= fx.find("Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict")
+          < fx.find("push the code to refs/heads/handoff/t-1")
+          and "`git merge origin/main`, rerun" not in fx)
+    check("the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main",
+          "`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict" in rv
+          and "never on a head that is behind main but merges cleanly" in rv)
+    check("no other role is told the merge-tree block rule (null control)",
+          all("behind main but merges cleanly" not in t for r, t in prompts.items() if r != "reviewer"))
     check("no other role is licensed a step ref (null control)",
           all(WIP_NS not in t for r, t in prompts.items() if r != "fixer"))
     ident = f"`git config user.name {SEAT_NAME} && git config user.email {SEAT_EMAIL}`"
diff --git a/tools/audit/seat/instruments/cloud_dispatch.py.md b/tools/audit/seat/instruments/cloud_dispatch.py.md
index b2b79948f..9140c769b 100644
--- a/tools/audit/seat/instruments/cloud_dispatch.py.md
+++ b/tools/audit/seat/instruments/cloud_dispatch.py.md
@@ -49,8 +49,10 @@
   else, and a seat may not write a record it did not mint), `handoff/<topic>`
   plus `handoff-body/<topic>` for a fixer (which pushes each verified step,
   fast-forward only, to `handoff-wip/<topic>`, a prefix neither
-  `cloud_relay.sh`'s handoff arm nor `bus.sh orphans` lists, merges a moved
-  `origin/main` and reruns `prepr.sh` before the handoff, and deletes the step
+  `cloud_relay.sh`'s handoff arm nor `bus.sh orphans` lists, hands off at its
+  first clean `prepr.sh` head, merges `origin/main` and reruns only when
+  `git merge-tree --write-tree origin/main HEAD` conflicts (tvofi, 2026-11-07),
+  and deletes the step
   ref once `body_push.sh` succeeds; a seat that dies leaves that one ref),
   `handoff-body/<topic>` for a probe; a fixer or probe pins the noreply seat
   identity before its first commit,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
