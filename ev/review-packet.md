# Review packet #3278
head: d5c4a06bccab2e3f7b2abffc2f49b49cf7d642cc
base: 28d46c4918285d36c409c1fb2f72eb77e04e569e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=128405400563 success
arch-score / arch-score id=128409055369 success
budget-raise-gate / budget-raise-gate id=128409055426 success
cancel-superseded id=128408946566 success
codeql id=128409055933 skipped
codeql / Analyze (actions) id=128405170846 success
codeql / Analyze (javascript-typescript) id=128405170852 success
codeql / Analyze (python) id=128405170843 in_progress
gate id=128409314146 in_progress
governance id=128409056173 skipped
governance / delivery-status id=128405172231 skipped
governance / delivery-status-publish id=128405171954 skipped
governance / env-matrix id=128405170914 success
governance / instrument-self-tests id=128405170885 in_progress
governance / policy-docs id=128405170921 success
governance / record id=128405172273 skipped
governance / wave-script id=128405170932 success
hassfest id=128409056312 skipped
hassfest / hassfest id=128405170904 success
kernel-points id=128409056272 skipped
pr-contract id=128409314543 skipped
prelude id=128408946427 success
refresh id=128408946638 success
tests id=128409056311 skipped
tests / arch-instrument id=128405832731 success
tests / briefs id=128405170809 success
tests / browser id=128405832761 success
tests / claims-autofix id=128408423384 skipped
tests / closure-scope id=128405170836 success
tests / closures id=128405832757 in_progress
tests / coverage id=128405832698 in_progress
tests / fast (3.14) id=128405832692 success
tests / mutation id=128405170863 success
tests / mutation-autofix id=128405957554 skipped
tests / mutation-pins id=128405957346 skipped
tests / nightly-ha id=128405834014 skipped
tests / nightly-status id=128405172216 skipped
tests / replay id=128405834117 skipped
tests / typing id=128405832753 success
validate id=128409056112 skipped
validate / validate-hacs id=128405170818 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 56d39a53: #201
NOTE body item e24cad51: #201
NOTE body item 5d1aea44: dismissed:identity settled per brief, as on #3246
NOTE body item e3842a39: dismissed:seat-harness configuration, outside this repository
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins
             `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <export>/tools/ci
             `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` is in the tree at this head
  unverified git archive <sha> tools/ci tools/pr
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z
             `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` is in the tree at this head
  unverified git log --first-parent --since=2026-10-31 4839ac95 -- tools/ci/gate.py tools/ci/prelude.py
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log --first-parent --since=2026-10-23 4839ac95 -- 'tools/ci/*.py' tools/pr/codeql_scope.py tests/closure.py tools/pr/cancel_superseded.py
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/fold_ledger.py check
             `tools/audit/fold_ledger.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git checkout "$PINNED" --
             `git checkout` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/pr/codeql_scope.py
             `tools/pr/codeql_scope.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         tools/pr/cancel_superseded.py
             `tools/pr/cancel_superseded.py` is in the tree at this head

FIGURES: 11 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index 0a2df5636..e12d8529a 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -4721,6 +4721,24 @@
       "doc": [
         "dev/audit/rca/r10-livehead-cancel.md"
       ]
+    },
+    "R10-RCA-GATE-BUSY-DEFER-2": {
+      "class": null,
+      "level": "instance-or-process",
+      "subject": "#3246 (355d9965) fixed gate.py's mutual deferral, yet mutual deferral reds persisted on #3261, #3265 and #3255: ci.yml restores tools/ci from the payload's base.sha, a job re-run replays that payload, so refresh and the sweep re-ran pre-merge runs on the pre-fix gate.py (46 stale-pinned gates, 21 deferral reds on 7 PRs in the 65 min after the merge; the replay of their real listings DEADLOCKs at each pinned base and DECIDES at the fix). #3263's red is C3's designed at-once deferral under the fixed program, not the race",
+      "trigger": "2 (red required check: gate)",
+      "date": "2026-11-07",
+      "status": "proposed",
+      "parts_missing": [
+        "the stale-pin compare in refresh() and sweep.py, dispatching a fresh run (tools/ci, the gate fixer's and the orchestrator's)"
+      ],
+      "process_state": "(c) fixer step 3's harnesses import one tools/ci copy per scene and the mutation proof mutates that copy; the #3246 review read the live reds' `programs restored from b36679ce` lines and dismissed them until the fix landed, and landing does not reach a run pinned at its creation",
+      "countermeasure": "built: dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay over recorded live listings (rc 1 at 28482ece, f2a01514, 80016a71; rc 0 at 294a880d and the branch; M17 red; the C3 scenes C3-AT-ONCE under every program) and its census arm; proposed: a re-run of a gate whose pinned programs differ from the base tip is replaced by a ci.yml dispatch (under 0.01 s of compare per re-run)",
+      "landed": null,
+      "in_tree_home": "dev/audit/rca/r10-gate-busy-defer-2.md",
+      "doc": [
+        "dev/audit/rca/r10-gate-busy-defer-2.md"
+      ]
     }
   },
   "N-registry-leak": {
diff --git a/dev/audit/harnesses/r10_rca_gate_busy_defer_2.json b/dev/audit/harnesses/r10_rca_gate_busy_defer_2.json
new file mode 100644
index 000000000..6a08a5fc0
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_gate_busy_defer_2.json
@@ -0,0 +1,10284 @@
+{
+ "repo": "tvofi/heatpump_optimizer",
+ "recorded_at": "2026-11-07T04:47:56Z",
+ "scenes": [
+  {
+   "name": "3261-pair",
+   "pr": "3261",
+   "head": "e17fadc1795ebbaaf0f01ed067fbb59aeba90dee",
+   "runs": [
+    {
+     "id": 42338360371,
+     "title": "CI review pr=3261 base=main sha=7871b3e3a4f688d20a04f4a7cbbafc32a80af518",
+     "created_at": "2026-11-07T04:25:00Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:25:00Z",
+       "jobs": [
+        {
+         "id": 128300301865,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:00Z",
+         "started_at": "2026-11-07T04:25:03Z",
+         "completed_at": "2026-11-07T04:25:52Z"
+        },
+        {
+         "id": 128300302043,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:00Z",
+         "started_at": "2026-11-07T04:25:03Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300302927,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:01Z",
+         "started_at": "2026-11-07T04:25:01Z",
+         "completed_at": "2026-11-07T04:25:00Z"
+        },
+        {
+         "id": 128300424050,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:31Z",
+         "started_at": "2026-11-07T04:25:34Z",
+         "completed_at": "2026-11-07T04:25:57Z"
+        },
+        {
+         "id": 128300425024,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425134,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425239,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425290,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425300,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425356,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300425547,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:32Z",
+         "started_at": "2026-11-07T04:25:32Z",
+         "completed_at": "2026-11-07T04:25:31Z"
+        },
+        {
+         "id": 128300519716,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:58Z",
+         "started_at": "2026-11-07T04:26:01Z",
+         "completed_at": "2026-11-07T04:27:40Z"
+        },
+        {
+         "id": 128300520716,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:58Z",
+         "started_at": "2026-11-07T04:25:58Z",
+         "completed_at": "2026-11-07T04:25:58Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42316391808,
+     "title": "CI review pr=3261 base=main sha=7871b3e3a4f688d20a04f4a7cbbafc32a80af518",
+     "created_at": "2026-11-07T00:08:37Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T00:08:37Z",
+       "jobs": [
+        {
+         "id": 128229913273,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:08:38Z",
+         "started_at": "2026-11-07T00:08:41Z",
+         "completed_at": "2026-11-07T00:09:09Z"
+        },
+        {
+         "id": 128229913588,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:08:38Z",
+         "started_at": "2026-11-07T00:08:41Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128229915526,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:08:39Z",
+         "started_at": "2026-11-07T00:08:39Z",
+         "completed_at": "2026-11-07T00:08:38Z"
+        },
+        {
+         "id": 128230092634,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:12Z",
+         "completed_at": "2026-11-07T00:09:40Z"
+        },
+        {
+         "id": 128230093986,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230094045,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230094288,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230094293,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230094421,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230094507,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230095025,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:10Z",
+         "started_at": "2026-11-07T00:09:10Z",
+         "completed_at": "2026-11-07T00:09:10Z"
+        },
+        {
+         "id": 128230274239,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:40Z",
+         "started_at": "2026-11-07T00:09:42Z",
+         "completed_at": "2026-11-07T00:10:20Z"
+        },
+        {
+         "id": 128230276261,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:40Z",
+         "started_at": "2026-11-07T00:09:40Z",
+         "completed_at": "2026-11-07T00:09:40Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T04:25:39Z",
+       "jobs": [
+        {
+         "id": 128300456958,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T00:08:41Z",
+         "completed_at": "2026-11-07T00:09:09Z"
+        },
+        {
+         "id": 128300457075,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:27:29Z"
+        },
+        {
+         "id": 128300457553,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300457556,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300457621,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:41Z"
+        },
+        {
+         "id": 128300457655,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T00:09:12Z",
+         "completed_at": "2026-11-07T00:09:40Z"
+        },
+        {
+         "id": 128300457669,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300457687,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300457691,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300457902,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:41Z",
+         "started_at": "2026-11-07T04:25:41Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300482108,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:47Z",
+         "started_at": "2026-11-07T04:25:47Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300486499,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-07T00:08:41Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128300489187,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-07T04:25:49Z",
+         "completed_at": "2026-11-07T00:08:38Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42307798573,
+     "title": "CI edit pr=3261 base=main sha=7871b3e3a4f688d20a04f4a7cbbafc32a80af518",
+     "created_at": "2026-11-06T22:51:29Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-06T22:51:29Z",
+       "jobs": [
+        {
+         "id": 128201459986,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:51:30Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128201460335,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:51:30Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201460351,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:51:30Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128201649324,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128201649528,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128201650794,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201651152,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201651170,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201651704,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201651728,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128201652034,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:51:59Z",
+         "started_at": "2026-11-06T22:51:59Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128202148031,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-06T22:53:14Z",
+         "started_at": "2026-11-06T22:53:17Z",
+         "completed_at": "2026-11-06T22:53:47Z"
+        },
+        {
+         "id": 128202149359,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:53:14Z",
+         "started_at": "2026-11-06T22:53:14Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-06T23:22:38Z",
+       "jobs": [
+        {
+         "id": 128213732340,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128213732877,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128213733037,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:43Z",
+         "completed_at": "2026-11-06T23:23:16Z"
+        },
+        {
+         "id": 128213733086,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:40Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213733111,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:40Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213733535,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128213733555,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:40Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213733654,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:40Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213733681,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128213733905,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:40Z",
+         "started_at": "2026-11-06T23:22:40Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213735114,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:41Z",
+         "started_at": "2026-11-06T23:22:41Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213767710,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:46Z",
+         "started_at": "2026-11-06T23:22:46Z",
+         "completed_at": "2026-11-06T23:22:40Z"
+        },
+        {
+         "id": 128213777779,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:47Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-06T23:27:09Z",
+       "jobs": [
+        {
+         "id": 128215425787,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T23:27:14Z",
+         "completed_at": "2026-11-06T23:27:50Z"
+        },
+        {
+         "id": 128215426141,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128215426306,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128215426484,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T23:27:11Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215427031,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128215427174,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128215427291,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T23:27:11Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215427552,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T23:27:11Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215427635,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:11Z",
+         "started_at": "2026-11-06T23:27:11Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215461580,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:27:17Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128215468330,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:18Z",
+         "started_at": "2026-11-06T23:27:18Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215470610,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:18Z",
+         "started_at": "2026-11-06T23:27:18Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        },
+        {
+         "id": 128215481382,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:27:20Z",
+         "started_at": "2026-11-06T23:27:20Z",
+         "completed_at": "2026-11-06T23:27:11Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T00:09:12Z",
+       "jobs": [
+        {
+         "id": 128230122945,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-07T00:09:17Z",
+         "completed_at": "2026-11-07T00:09:59Z"
+        },
+        {
+         "id": 128230123103,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128230123128,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-07T00:09:15Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230123551,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128230124026,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-07T00:09:15Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230124156,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-07T00:09:15Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230124900,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:15Z",
+         "started_at": "2026-11-07T00:09:15Z",
+         "completed_at": "2026-11-07T00:09:15Z"
+        },
+        {
+         "id": 128230157539,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-07T00:09:20Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230160280,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:21Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128230166844,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128230171023,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-07T00:09:22Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230172422,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:23Z",
+         "started_at": "2026-11-07T00:09:23Z",
+         "completed_at": "2026-11-07T00:09:14Z"
+        },
+        {
+         "id": 128230174480,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:23Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        }
+       ]
+      },
+      {
+       "n": 5,
+       "run_started_at": "2026-11-07T00:10:40Z",
+       "jobs": [
+        {
+         "id": 128230650438,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-07T00:10:44Z",
+         "completed_at": "2026-11-07T00:11:19Z"
+        },
+        {
+         "id": 128230650524,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128230650947,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128230651258,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-07T00:10:42Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230651356,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-07T00:10:42Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230651474,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-07T00:10:42Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230651495,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128230652512,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:42Z",
+         "started_at": "2026-11-07T00:10:42Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230682072,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:47Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128230684660,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:47Z",
+         "started_at": "2026-11-07T00:10:47Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230684698,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:47Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128230686181,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:48Z",
+         "started_at": "2026-11-07T00:10:48Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        },
+        {
+         "id": 128230690429,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:48Z",
+         "started_at": "2026-11-07T00:10:48Z",
+         "completed_at": "2026-11-07T00:10:41Z"
+        }
+       ]
+      },
+      {
+       "n": 6,
+       "run_started_at": "2026-11-07T00:12:35Z",
+       "jobs": [
+        {
+         "id": 128231320702,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:12:37Z",
+         "started_at": "2026-11-07T00:12:40Z",
+         "completed_at": "2026-11-07T00:13:15Z"
+        },
+        {
+         "id": 128231320928,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:37Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128231321388,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-07T00:12:38Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231321715,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128231321803,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128231321806,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128231321818,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-07T00:12:38Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231321979,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-07T00:12:38Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231322344,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:38Z",
+         "started_at": "2026-11-07T00:12:38Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231350872,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:43Z",
+         "started_at": "2026-11-07T00:12:43Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231374468,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:47Z",
+         "started_at": "2026-11-07T00:12:47Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        },
+        {
+         "id": 128231374956,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:47Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128231376693,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:47Z",
+         "started_at": "2026-11-07T00:12:47Z",
+         "completed_at": "2026-11-07T00:12:37Z"
+        }
+       ]
+      },
+      {
+       "n": 7,
+       "run_started_at": "2026-11-07T00:36:50Z",
+       "jobs": [
+        {
+         "id": 128239633653,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-07T00:36:55Z",
+         "completed_at": "2026-11-07T00:37:34Z"
+        },
+        {
+         "id": 128239633728,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128239634046,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128239634255,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128239634388,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-07T00:36:52Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239634396,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-07T00:36:52Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239634700,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128239634928,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-07T00:36:52Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239635189,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:52Z",
+         "started_at": "2026-11-07T00:36:52Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239667273,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:58Z",
+         "started_at": "2026-11-07T00:36:58Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239667519,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:58Z",
+         "started_at": "2026-11-07T00:36:58Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239668772,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:36:59Z",
+         "started_at": "2026-11-07T00:36:59Z",
+         "completed_at": "2026-11-07T00:36:52Z"
+        },
+        {
+         "id": 128239671111,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:36:59Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        }
+       ]
+      },
+      {
+       "n": 8,
+       "run_started_at": "2026-11-07T04:25:41Z",
+       "jobs": [
+        {
+         "id": 128300465569,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128300465816,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:45Z",
+         "completed_at": "2026-11-07T04:26:17Z"
+        },
+        {
+         "id": 128300466168,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128300466484,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300466519,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300466537,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300466560,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300466564,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300466595,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128300466888,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:43Z",
+         "started_at": "2026-11-07T04:25:43Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300492894,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-07T04:25:43Z"
+        },
+        {
+         "id": 128300496558,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128300502446,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:53Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        }
+       ]
+      },
+      {
+       "n": 9,
+       "run_started_at": "2026-11-07T04:27:49Z",
+       "jobs": [
+        {
+         "id": 128300939509,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128300939791,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128300939929,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300939940,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:53Z",
+         "completed_at": "2026-11-07T04:28:22Z"
+        },
+        {
+         "id": 128300940027,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300940033,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128300940041,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300940044,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300940101,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300940233,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:50Z"
+        },
+        {
+         "id": 128300940293,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-07T04:27:51Z",
+         "completed_at": "2026-11-07T04:27:51Z"
+        },
+        {
+         "id": 128300940504,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:51Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128300968518,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:59Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        }
+       ]
+      },
+      {
+       "n": 10,
+       "run_started_at": "2026-11-07T04:29:05Z",
+       "jobs": [
+        {
+         "id": 128301214046,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:07Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:59Z"
+        },
+        {
+         "id": 128301214116,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:29:07Z",
+         "started_at": "2026-11-07T04:29:10Z",
+         "completed_at": "2026-11-07T04:29:41Z"
+        },
+        {
+         "id": 128301214340,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214411,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214474,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214548,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:52:17Z"
+        },
+        {
+         "id": 128301214571,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214574,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214581,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-06T22:51:33Z",
+         "completed_at": "2026-11-06T22:51:43Z"
+        },
+        {
+         "id": 128301214654,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-06T22:52:01Z",
+         "completed_at": "2026-11-06T22:52:31Z"
+        },
+        {
+         "id": 128301214854,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        },
+        {
+         "id": 128301214875,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-06T22:52:02Z",
+         "completed_at": "2026-11-06T22:53:14Z"
+        },
+        {
+         "id": 128301215005,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:08Z",
+         "started_at": "2026-11-07T04:29:08Z",
+         "completed_at": "2026-11-07T04:29:07Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42307493079,
+     "title": "CI code pr=3261 base=main sha=7871b3e3a4f688d20a04f4a7cbbafc32a80af518",
+     "created_at": "2026-11-06T22:48:56Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-06T22:48:56Z",
+       "jobs": [
+        {
+         "id": 128200419215,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:56Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:07Z"
+        },
+        {
+         "id": 128200419610,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200419658,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128200692525,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:15Z"
+        },
+        {
+         "id": 128200692549,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:54Z"
+        },
+        {
+         "id": 128200692554,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:29Z"
+        },
+        {
+         "id": 128200692566,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:47Z"
+        },
+        {
+         "id": 128200692621,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:56:43Z"
+        },
+        {
+         "id": 128200692630,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:24Z"
+        },
+        {
+         "id": 128200692638,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T23:16:34Z"
+        },
+        {
+         "id": 128200692713,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:45Z",
+         "completed_at": "2026-11-06T22:50:08Z"
+        },
+        {
+         "id": 128200692737,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128200692782,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:02Z"
+        },
+        {
+         "id": 128200692803,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:11Z"
+        },
+        {
+         "id": 128200692830,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:51Z"
+        },
+        {
+         "id": 128200692836,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:09Z"
+        },
+        {
+         "id": 128200692858,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:59Z"
+        },
+        {
+         "id": 128200692899,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:57Z"
+        },
+        {
+         "id": 128200693055,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:06Z"
+        },
+        {
+         "id": 128200694711,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:37Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128200694728,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:37Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128200694770,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:37Z",
+         "started_at": "2026-11-06T22:49:37Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128200934360,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128200934402,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:54:30Z"
+        },
+        {
+         "id": 128200934425,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:16Z"
+        },
+        {
+         "id": 128200934470,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:10:32Z"
+        },
+        {
+         "id": 128200934498,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128200934527,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:09Z"
+        },
+        {
+         "id": 128200936536,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:13Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128200936622,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:50:13Z",
+         "started_at": "2026-11-06T22:50:13Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128201034484,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:50:28Z",
+         "started_at": "2026-11-06T22:50:28Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128201034591,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:50:28Z",
+         "started_at": "2026-11-06T22:50:28Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128205456224,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:01:35Z",
+         "started_at": "2026-11-06T23:01:35Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128208954556,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:10:32Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:45Z"
+        },
+        {
+         "id": 128208954569,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:10:32Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:59Z"
+        },
+        {
+         "id": 128208954680,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:10:32Z",
+         "started_at": "2026-11-06T23:10:36Z",
+         "completed_at": "2026-11-06T23:10:43Z"
+        },
+        {
+         "id": 128213148674,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:21:09Z",
+         "started_at": "2026-11-06T23:21:11Z",
+         "completed_at": "2026-11-06T23:21:46Z"
+        },
+        {
+         "id": 128213149962,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:21:09Z",
+         "started_at": "2026-11-06T23:21:09Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128213150052,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:21:09Z",
+         "started_at": "2026-11-06T23:21:09Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128213388457,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:21:46Z",
+         "started_at": "2026-11-06T23:21:50Z",
+         "completed_at": "2026-11-06T23:22:24Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T00:09:15Z",
+       "jobs": [
+        {
+         "id": 128230152371,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:07Z"
+        },
+        {
+         "id": 128230152855,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128230155926,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-07T00:09:20Z",
+         "completed_at": "2026-11-07T00:09:20Z"
+        },
+        {
+         "id": 128230156503,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:54Z"
+        },
+        {
+         "id": 128230156704,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:15Z"
+        },
+        {
+         "id": 128230157068,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T23:16:34Z"
+        },
+        {
+         "id": 128230157143,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:45Z",
+         "completed_at": "2026-11-06T22:50:08Z"
+        },
+        {
+         "id": 128230157146,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:09Z"
+        },
+        {
+         "id": 128230157151,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:56:43Z"
+        },
+        {
+         "id": 128230157493,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:29Z"
+        },
+        {
+         "id": 128230157614,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:51Z"
+        },
+        {
+         "id": 128230157853,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-07T00:09:20Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128230157890,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:11Z"
+        },
+        {
+         "id": 128230157926,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:02Z"
+        },
+        {
+         "id": 128230157960,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:47Z"
+        },
+        {
+         "id": 128230158001,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-07T00:09:20Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128230158120,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128230158180,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:59Z"
+        },
+        {
+         "id": 128230158274,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:24Z"
+        },
+        {
+         "id": 128230158376,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:57Z"
+        },
+        {
+         "id": 128230158422,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:20Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:06Z"
+        },
+        {
+         "id": 128230168288,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:54:30Z"
+        },
+        {
+         "id": 128230168613,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:10:32Z"
+        },
+        {
+         "id": 128230168949,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:16Z"
+        },
+        {
+         "id": 128230169046,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-07T00:09:22Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128230169070,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128230169195,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128230169429,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:09Z"
+        },
+        {
+         "id": 128230169440,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-07T00:09:22Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128230169777,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:22Z",
+         "started_at": "2026-11-07T00:09:22Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128230178959,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-07T00:09:24Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128230181672,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-06T23:10:36Z",
+         "completed_at": "2026-11-06T23:10:43Z"
+        },
+        {
+         "id": 128230182110,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:45Z"
+        },
+        {
+         "id": 128230182207,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-07T00:09:24Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128230182305,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-07T00:09:24Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128230182653,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-07T00:09:24Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128230182823,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:24Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:59Z"
+        },
+        {
+         "id": 128230185107,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:25Z",
+         "started_at": "2026-11-07T00:09:27Z",
+         "completed_at": "2026-11-07T00:12:14Z"
+        },
+        {
+         "id": 128230186105,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:25Z",
+         "started_at": "2026-11-06T23:21:11Z",
+         "completed_at": "2026-11-06T23:21:46Z"
+        },
+        {
+         "id": 128230206919,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:28Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T04:25:47Z",
+       "jobs": [
+        {
+         "id": 128300488018,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:07Z"
+        },
+        {
+         "id": 128300488450,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128300488583,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:02Z"
+        },
+        {
+         "id": 128300488628,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:15Z"
+        },
+        {
+         "id": 128300488665,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:59Z"
+        },
+        {
+         "id": 128300488718,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128300488790,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:29Z"
+        },
+        {
+         "id": 128300488901,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:24Z"
+        },
+        {
+         "id": 128300488915,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:56:43Z"
+        },
+        {
+         "id": 128300489008,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:45Z",
+         "completed_at": "2026-11-06T22:50:08Z"
+        },
+        {
+         "id": 128300489077,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-07T04:25:49Z",
+         "completed_at": "2026-11-07T04:25:49Z"
+        },
+        {
+         "id": 128300489079,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:09Z"
+        },
+        {
+         "id": 128300489097,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:51Z"
+        },
+        {
+         "id": 128300489123,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:49:57Z"
+        },
+        {
+         "id": 128300489134,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:11Z"
+        },
+        {
+         "id": 128300489168,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:06Z"
+        },
+        {
+         "id": 128300489177,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:54Z"
+        },
+        {
+         "id": 128300489217,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-07T04:25:49Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128300489236,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128300489242,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T23:16:34Z"
+        },
+        {
+         "id": 128300489246,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-07T04:25:49Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        },
+        {
+         "id": 128300489275,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:49:40Z",
+         "completed_at": "2026-11-06T22:50:47Z"
+        },
+        {
+         "id": 128300489315,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:09Z"
+        },
+        {
+         "id": 128300489409,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:49Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128300489505,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128300489682,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128300489687,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:54:30Z"
+        },
+        {
+         "id": 128300489742,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T22:51:16Z"
+        },
+        {
+         "id": 128300489799,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T22:50:13Z"
+        },
+        {
+         "id": 128300489902,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:53Z",
+         "completed_at": "2026-11-07T04:27:37Z"
+        },
+        {
+         "id": 128300489937,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T22:50:16Z",
+         "completed_at": "2026-11-06T23:10:32Z"
+        },
+        {
+         "id": 128300490013,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:59Z"
+        },
+        {
+         "id": 128300490021,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T23:10:36Z",
+         "completed_at": "2026-11-06T23:10:43Z"
+        },
+        {
+         "id": 128300490030,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T22:50:27Z"
+        },
+        {
+         "id": 128300490063,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128300490112,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T23:21:09Z"
+        },
+        {
+         "id": 128300490285,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-07T04:25:50Z",
+         "completed_at": "2026-11-06T23:01:35Z"
+        },
+        {
+         "id": 128300490392,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T23:10:35Z",
+         "completed_at": "2026-11-06T23:10:45Z"
+        },
+        {
+         "id": 128300490875,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:50Z",
+         "started_at": "2026-11-06T23:21:11Z",
+         "completed_at": "2026-11-06T23:21:46Z"
+        },
+        {
+         "id": 128300518058,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:37Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42307493684,
+     "title": "CI edit pr=3261 base=main sha=7871b3e3a4f688d20a04f4a7cbbafc32a80af518",
+     "created_at": "2026-11-06T22:48:56Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-06T22:48:56Z",
+       "jobs": [
+        {
+         "id": 128200421307,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128200421665,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200421715,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:48:57Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128200615675,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128200615858,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128200617211,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200617995,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200618116,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200618291,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200618427,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128200619037,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:49:26Z",
+         "started_at": "2026-11-06T22:49:26Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128201061248,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-06T22:50:31Z",
+         "started_at": "2026-11-06T22:50:34Z",
+         "completed_at": "2026-11-06T22:50:59Z"
+        },
+        {
+         "id": 128201062398,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T22:50:32Z",
+         "started_at": "2026-11-06T22:50:32Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-06T23:22:37Z",
+       "jobs": [
+        {
+         "id": 128213724460,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:42Z",
+         "completed_at": "2026-11-06T23:23:14Z"
+        },
+        {
+         "id": 128213724689,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128213725322,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128213725501,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:39Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213725558,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:39Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213725665,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128213725705,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:39Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213726012,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:39Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213726602,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:39Z",
+         "started_at": "2026-11-06T23:22:39Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213766599,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:46Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128213770681,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:46Z",
+         "started_at": "2026-11-06T23:22:46Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213771685,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:22:46Z",
+         "started_at": "2026-11-06T23:22:46Z",
+         "completed_at": "2026-11-06T23:22:39Z"
+        },
+        {
+         "id": 128213775663,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:22:47Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-06T23:26:16Z",
+       "jobs": [
+        {
+         "id": 128215102788,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128215102848,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T23:26:22Z",
+         "completed_at": "2026-11-06T23:26:52Z"
+        },
+        {
+         "id": 128215103397,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128215103819,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128215103844,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T23:26:19Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215104020,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T23:26:19Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215104089,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128215105242,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:19Z",
+         "started_at": "2026-11-06T23:26:19Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215135247,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:24Z",
+         "started_at": "2026-11-06T23:26:24Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215138062,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-06T23:26:25Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128215139023,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:25Z",
+         "started_at": "2026-11-06T23:26:25Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215143555,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:26Z",
+         "started_at": "2026-11-06T23:26:26Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        },
+        {
+         "id": 128215158394,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-06T23:26:28Z",
+         "started_at": "2026-11-06T23:26:28Z",
+         "completed_at": "2026-11-06T23:26:19Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T00:09:17Z",
+       "jobs": [
+        {
+         "id": 128230150812,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128230151371,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:22Z",
+         "completed_at": "2026-11-07T00:09:57Z"
+        },
+        {
+         "id": 128230151877,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:19Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230151920,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:19Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230152078,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:19Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230152277,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128230152295,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:19Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230152536,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128230152580,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:19Z",
+         "started_at": "2026-11-07T00:09:19Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230185474,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:25Z",
+         "started_at": "2026-11-07T00:09:25Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230192941,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:09:26Z",
+         "started_at": "2026-11-07T00:09:26Z",
+         "completed_at": "2026-11-07T00:09:19Z"
+        },
+        {
+         "id": 128230196722,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:27Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128230202565,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:09:28Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        }
+       ]
+      },
+      {
+       "n": 5,
+       "run_started_at": "2026-11-07T00:10:38Z",
+       "jobs": [
+        {
+         "id": 128230643732,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:40Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128230643969,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:10:40Z",
+         "started_at": "2026-11-07T00:10:43Z",
+         "completed_at": "2026-11-07T00:11:19Z"
+        },
+        {
+         "id": 128230644380,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230644483,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230644606,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230644818,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128230644838,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128230645109,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230645118,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230645125,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-07T00:10:41Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230645379,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:41Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128230690979,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:10:49Z",
+         "started_at": "2026-11-07T00:10:49Z",
+         "completed_at": "2026-11-07T00:10:40Z"
+        },
+        {
+         "id": 128230700401,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:10:50Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        }
+       ]
+      },
+      {
+       "n": 6,
+       "run_started_at": "2026-11-07T00:12:34Z",
+       "jobs": [
+        {
+         "id": 128231310878,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-07T00:12:38Z",
+         "completed_at": "2026-11-07T00:13:15Z"
+        },
+        {
+         "id": 128231311195,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128231311308,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128231311793,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128231311849,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-07T00:12:36Z",
+         "completed_at": "2026-11-07T00:12:36Z"
+        },
+        {
+         "id": 128231312055,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:36Z",
+         "started_at": "2026-11-07T00:12:36Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        },
+        {
+         "id": 128231342510,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:41Z",
+         "started_at": "2026-11-07T00:12:41Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        },
+        {
+         "id": 128231343251,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:41Z",
+         "started_at": "2026-11-07T00:12:41Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        },
+        {
+         "id": 128231350036,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:43Z",
+         "started_at": "2026-11-07T00:12:43Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        },
+        {
+         "id": 128231355210,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:43Z",
+         "started_at": "2026-11-07T00:12:43Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        },
+        {
+         "id": 128231361280,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:44Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128231363199,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:12:45Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128231368519,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:12:46Z",
+         "started_at": "2026-11-07T00:12:46Z",
+         "completed_at": "2026-11-07T00:12:35Z"
+        }
+       ]
+      },
+      {
+       "n": 7,
+       "run_started_at": "2026-11-07T00:38:12Z",
+       "jobs": [
+        {
+         "id": 128240088211,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:15Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128240088261,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:15Z",
+         "started_at": "2026-11-07T00:38:23Z",
+         "completed_at": "2026-11-07T00:39:00Z"
+        },
+        {
+         "id": 128240088546,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128240088812,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-07T00:38:16Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240089100,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-07T00:38:16Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240089150,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-07T00:38:16Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240089152,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128240089197,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-07T00:38:16Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240089246,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128240089255,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:16Z",
+         "started_at": "2026-11-07T00:38:16Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240118269,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T00:38:21Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128240121640,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:22Z",
+         "started_at": "2026-11-07T00:38:22Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        },
+        {
+         "id": 128240130924,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T00:38:23Z",
+         "started_at": "2026-11-07T00:38:23Z",
+         "completed_at": "2026-11-07T00:38:15Z"
+        }
+       ]
+      },
+      {
+       "n": 8,
+       "run_started_at": "2026-11-07T04:25:49Z",
+       "jobs": [
+        {
+         "id": 128300495200,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:24Z"
+        },
+        {
+         "id": 128300495231,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        },
+        {
+         "id": 128300495390,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128300495753,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495779,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495788,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495803,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495844,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495895,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495908,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128300495916,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128300496307,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300523393,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        }
+       ]
+      },
+      {
+       "n": 9,
+       "run_started_at": "2026-11-07T04:27:47Z",
+       "jobs": [
+        {
+         "id": 128300935532,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-07T04:27:50Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300935537,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-07T04:27:52Z",
+         "completed_at": "2026-11-07T04:28:25Z"
+        },
+        {
+         "id": 128300936047,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-07T04:27:50Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300936152,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-07T04:27:50Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300936184,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128300936392,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-07T04:27:50Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300936715,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:50Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128300954722,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:55Z",
+         "started_at": "2026-11-07T04:27:55Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300956718,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:56Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128300962747,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:57Z",
+         "started_at": "2026-11-07T04:27:57Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300964498,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:58Z",
+         "started_at": "2026-11-07T04:27:58Z",
+         "completed_at": "2026-11-07T04:27:49Z"
+        },
+        {
+         "id": 128300968826,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:59Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128300969804,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:27:59Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        }
+       ]
+      },
+      {
+       "n": 10,
+       "run_started_at": "2026-11-07T04:29:04Z",
+       "jobs": [
+        {
+         "id": 128301209450,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-07T04:29:09Z",
+         "completed_at": "2026-11-07T04:29:46Z"
+        },
+        {
+         "id": 128301209453,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:08Z"
+        },
+        {
+         "id": 128301209547,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-07T04:29:06Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301209868,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:26Z"
+        },
+        {
+         "id": 128301209983,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-07T04:29:06Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301209989,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-07T04:29:06Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301210014,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:06Z",
+         "started_at": "2026-11-07T04:29:06Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301228408,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:12Z",
+         "started_at": "2026-11-07T04:29:12Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301237809,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:14Z",
+         "started_at": "2026-11-07T04:29:14Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301240547,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:15Z",
+         "started_at": "2026-11-06T22:49:28Z",
+         "completed_at": "2026-11-06T22:50:16Z"
+        },
+        {
+         "id": 128301240896,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:29:15Z",
+         "started_at": "2026-11-07T04:29:15Z",
+         "completed_at": "2026-11-07T04:29:06Z"
+        },
+        {
+         "id": 128301243553,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:16Z",
+         "started_at": "2026-11-06T22:49:29Z",
+         "completed_at": "2026-11-06T22:50:31Z"
+        },
+        {
+         "id": 128301244182,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:29:16Z",
+         "started_at": "2026-11-06T22:48:59Z",
+         "completed_at": "2026-11-06T22:49:25Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42307493684,
+     "attempt": 8,
+     "job": 128300495200,
+     "started_at": "2026-11-07T04:25:54Z",
+     "completed_at": "2026-11-07T04:26:24Z",
+     "conclusion": "failure",
+     "pin": "28482eceeb6b9809e44b12d80fc994282cc21645",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42307798573] at this head are still being judged; their gate decides"
+    },
+    {
+     "run": 42307798573,
+     "attempt": 8,
+     "job": 128300465816,
+     "started_at": "2026-11-07T04:25:45Z",
+     "completed_at": "2026-11-07T04:26:17Z",
+     "conclusion": "failure",
+     "pin": "28482eceeb6b9809e44b12d80fc994282cc21645",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42307493684] at this head are still being judged; their gate decides"
+    }
+   ]
+  },
+  {
+   "name": "3265-pair",
+   "pr": "3265",
+   "head": "c7c5cef52a49bed59ee4c8a42e495ef2dae30db5",
+   "runs": [
+    {
+     "id": 42336664899,
+     "title": "CI edit pr=3265 base=main sha=21b2a2d65a9d9861bf3ff2b017658c0bcf154b25",
+     "created_at": "2026-11-07T04:02:39Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:02:39Z",
+       "jobs": [
+        {
+         "id": 128295015123,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:02:40Z",
+         "started_at": "2026-11-07T04:02:42Z",
+         "completed_at": "2026-11-07T04:03:07Z"
+        },
+        {
+         "id": 128295015283,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:02:40Z",
+         "started_at": "2026-11-07T04:02:43Z",
+         "completed_at": "2026-11-07T04:03:19Z"
+        },
+        {
+         "id": 128295015302,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:02:40Z",
+         "started_at": "2026-11-07T04:02:43Z",
+         "completed_at": "2026-11-07T04:02:56Z"
+        },
+        {
+         "id": 128295121320,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:10Z",
+         "completed_at": "2026-11-07T04:04:23Z"
+        },
+        {
+         "id": 128295121348,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:10Z",
+         "completed_at": "2026-11-07T04:03:42Z"
+        },
+        {
+         "id": 128295122228,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295122432,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295122501,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295122542,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295122647,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295122728,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:08Z",
+         "started_at": "2026-11-07T04:03:08Z",
+         "completed_at": "2026-11-07T04:03:08Z"
+        },
+        {
+         "id": 128295428450,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:04:24Z",
+         "started_at": "2026-11-07T04:04:26Z",
+         "completed_at": "2026-11-07T04:05:16Z"
+        },
+        {
+         "id": 128295636172,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:05:16Z",
+         "started_at": "2026-11-07T04:05:18Z",
+         "completed_at": "2026-11-07T04:05:52Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42333388705,
+     "title": "CI edit pr=3265 base=main sha=21b2a2d65a9d9861bf3ff2b017658c0bcf154b25",
+     "created_at": "2026-11-07T03:18:21Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T03:18:21Z",
+       "jobs": [
+        {
+         "id": 128284739030,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:18:22Z",
+         "started_at": "2026-11-07T03:18:24Z",
+         "completed_at": "2026-11-07T03:18:32Z"
+        },
+        {
+         "id": 128284739248,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:18:22Z",
+         "started_at": "2026-11-07T03:18:34Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284739301,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:18:22Z",
+         "started_at": "2026-11-07T03:18:28Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284910170,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:05Z",
+         "completed_at": "2026-11-07T03:19:25Z"
+        },
+        {
+         "id": 128284910183,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:06Z",
+         "completed_at": "2026-11-07T03:20:19Z"
+        },
+        {
+         "id": 128284911337,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284911415,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284911428,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284912061,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284912222,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128284912245,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:19:03Z",
+         "started_at": "2026-11-07T03:19:03Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128285223329,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T03:20:20Z",
+         "started_at": "2026-11-07T03:20:22Z",
+         "completed_at": "2026-11-07T03:20:50Z"
+        },
+        {
+         "id": 128285224482,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:20:20Z",
+         "started_at": "2026-11-07T03:20:20Z",
+         "completed_at": "2026-11-07T03:20:20Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T03:45:21Z",
+       "jobs": [
+        {
+         "id": 128291152558,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:22Z",
+         "started_at": "2026-11-07T03:18:34Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128291152776,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:25Z",
+         "completed_at": "2026-11-07T03:45:59Z"
+        },
+        {
+         "id": 128291152877,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:18:28Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128291153236,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:23Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291153243,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:23Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291153259,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:19:05Z",
+         "completed_at": "2026-11-07T03:19:25Z"
+        },
+        {
+         "id": 128291153311,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:23Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291153414,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:23Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291153525,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:19:06Z",
+         "completed_at": "2026-11-07T03:20:19Z"
+        },
+        {
+         "id": 128291154126,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:23Z",
+         "started_at": "2026-11-07T03:45:23Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291179856,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:29Z",
+         "started_at": "2026-11-07T03:45:29Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        },
+        {
+         "id": 128291180328,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:30Z",
+         "started_at": "2026-11-07T03:18:24Z",
+         "completed_at": "2026-11-07T03:18:32Z"
+        },
+        {
+         "id": 128291192210,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:45:33Z",
+         "started_at": "2026-11-07T03:45:33Z",
+         "completed_at": "2026-11-07T03:45:22Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T04:03:13Z",
+       "jobs": [
+        {
+         "id": 128295153828,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T04:03:56Z"
+        },
+        {
+         "id": 128295154034,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T03:18:28Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128295154382,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295154545,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295154619,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295154650,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295154661,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295154695,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T03:19:05Z",
+         "completed_at": "2026-11-07T03:19:25Z"
+        },
+        {
+         "id": 128295155242,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:16Z",
+         "started_at": "2026-11-07T04:03:16Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        },
+        {
+         "id": 128295177050,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:21Z",
+         "started_at": "2026-11-07T03:19:06Z",
+         "completed_at": "2026-11-07T03:20:19Z"
+        },
+        {
+         "id": 128295184522,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:23Z",
+         "started_at": "2026-11-07T03:18:24Z",
+         "completed_at": "2026-11-07T03:18:32Z"
+        },
+        {
+         "id": 128295187176,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:24Z",
+         "started_at": "2026-11-07T03:18:34Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128295190970,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:25Z",
+         "started_at": "2026-11-07T04:03:25Z",
+         "completed_at": "2026-11-07T04:03:15Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T04:06:13Z",
+       "jobs": [
+        {
+         "id": 128295878197,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:06:16Z",
+         "started_at": "2026-11-07T04:06:18Z",
+         "completed_at": "2026-11-07T04:06:47Z"
+        },
+        {
+         "id": 128295878573,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:16Z",
+         "started_at": "2026-11-07T03:18:34Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128295878649,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:16Z",
+         "started_at": "2026-11-07T04:06:16Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295878719,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:16Z",
+         "started_at": "2026-11-07T03:19:05Z",
+         "completed_at": "2026-11-07T03:19:25Z"
+        },
+        {
+         "id": 128295879106,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:16Z",
+         "started_at": "2026-11-07T04:06:16Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295902364,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:22Z",
+         "started_at": "2026-11-07T04:06:22Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295902442,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:22Z",
+         "started_at": "2026-11-07T03:18:24Z",
+         "completed_at": "2026-11-07T03:18:32Z"
+        },
+        {
+         "id": 128295903609,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:22Z",
+         "started_at": "2026-11-07T04:06:22Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295904634,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:22Z",
+         "started_at": "2026-11-07T03:18:28Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128295905483,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:22Z",
+         "started_at": "2026-11-07T04:06:22Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295915955,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:25Z",
+         "started_at": "2026-11-07T04:06:25Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        },
+        {
+         "id": 128295917159,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:25Z",
+         "started_at": "2026-11-07T03:19:06Z",
+         "completed_at": "2026-11-07T03:20:19Z"
+        },
+        {
+         "id": 128295917493,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:25Z",
+         "started_at": "2026-11-07T04:06:25Z",
+         "completed_at": "2026-11-07T04:06:15Z"
+        }
+       ]
+      },
+      {
+       "n": 5,
+       "run_started_at": "2026-11-07T04:07:36Z",
+       "jobs": [
+        {
+         "id": 128296198588,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T04:07:41Z",
+         "completed_at": "2026-11-07T04:08:22Z"
+        },
+        {
+         "id": 128296198810,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T03:18:34Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128296199316,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T04:07:38Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296199435,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T04:07:38Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296199569,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T03:19:05Z",
+         "completed_at": "2026-11-07T03:19:25Z"
+        },
+        {
+         "id": 128296199874,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:38Z",
+         "started_at": "2026-11-07T04:07:38Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296224650,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:45Z",
+         "started_at": "2026-11-07T04:07:45Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296228391,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T03:18:24Z",
+         "completed_at": "2026-11-07T03:18:32Z"
+        },
+        {
+         "id": 128296229204,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T04:07:46Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296230273,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T03:19:06Z",
+         "completed_at": "2026-11-07T03:20:19Z"
+        },
+        {
+         "id": 128296231091,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T04:07:46Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        },
+        {
+         "id": 128296231389,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T03:18:28Z",
+         "completed_at": "2026-11-07T03:19:03Z"
+        },
+        {
+         "id": 128296233964,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:47Z",
+         "started_at": "2026-11-07T04:07:47Z",
+         "completed_at": "2026-11-07T04:07:38Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42332778588,
+     "title": "CI code pr=3265 base=main sha=21b2a2d65a9d9861bf3ff2b017658c0bcf154b25",
+     "created_at": "2026-11-07T03:10:45Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T03:10:45Z",
+       "jobs": [
+        {
+         "id": 128282837003,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:46Z",
+         "started_at": "2026-11-07T03:11:49Z",
+         "completed_at": "2026-11-07T03:11:58Z"
+        },
+        {
+         "id": 128282837176,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:46Z",
+         "started_at": "2026-11-07T03:12:01Z",
+         "completed_at": "2026-11-07T03:12:37Z"
+        },
+        {
+         "id": 128282837256,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:46Z",
+         "started_at": "2026-11-07T03:12:17Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128283313078,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:12:51Z",
+         "completed_at": "2026-11-07T03:13:22Z"
+        },
+        {
+         "id": 128283313093,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:14:12Z",
+         "completed_at": "2026-11-07T03:14:33Z"
+        },
+        {
+         "id": 128283313097,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:13:26Z",
+         "completed_at": "2026-11-07T03:14:40Z"
+        },
+        {
+         "id": 128283313127,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:14:52Z",
+         "completed_at": "2026-11-07T03:15:08Z"
+        },
+        {
+         "id": 128283313147,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:13:13Z",
+         "completed_at": "2026-11-07T03:13:24Z"
+        },
+        {
+         "id": 128283313159,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:13:31Z",
+         "completed_at": "2026-11-07T03:14:09Z"
+        },
+        {
+         "id": 128283313178,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:15:52Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128283313187,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "cancelled",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:15:08Z",
+         "completed_at": "2026-11-07T03:45:10Z"
+        },
+        {
+         "id": 128283313189,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:15:31Z",
+         "completed_at": "2026-11-07T03:15:49Z"
+        },
+        {
+         "id": 128283313193,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:15:09Z",
+         "completed_at": "2026-11-07T03:16:24Z"
+        },
+        {
+         "id": 128283313203,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:14:18Z",
+         "completed_at": "2026-11-07T03:15:00Z"
+        },
+        {
+         "id": 128283313209,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:14:45Z",
+         "completed_at": "2026-11-07T03:19:24Z"
+        },
+        {
+         "id": 128283313226,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:16:27Z",
+         "completed_at": "2026-11-07T03:16:44Z"
+        },
+        {
+         "id": 128283313238,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:16:36Z",
+         "completed_at": "2026-11-07T03:17:23Z"
+        },
+        {
+         "id": 128283313296,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:16:47Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128283313867,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:15:37Z",
+         "completed_at": "2026-11-07T03:16:07Z"
+        },
+        {
+         "id": 128283314095,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:12:38Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128283314460,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:38Z",
+         "started_at": "2026-11-07T03:12:38Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128283314870,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:39Z",
+         "started_at": "2026-11-07T03:12:39Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128284302245,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:16:34Z",
+         "started_at": "2026-11-07T03:16:34Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128284302470,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:16:34Z",
+         "started_at": "2026-11-07T03:16:34Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128284483605,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:33:36Z"
+        },
+        {
+         "id": 128284483622,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:21:41Z"
+        },
+        {
+         "id": 128284483639,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128284483644,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:18:40Z"
+        },
+        {
+         "id": 128284483656,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:18:41Z"
+        },
+        {
+         "id": 128284483679,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:29:42Z"
+        },
+        {
+         "id": 128284484508,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:17:18Z",
+         "started_at": "2026-11-07T03:17:18Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128284484870,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:17:19Z",
+         "started_at": "2026-11-07T03:17:19Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128287482771,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:29:42Z",
+         "started_at": "2026-11-07T03:29:42Z",
+         "completed_at": "2026-11-07T03:29:42Z"
+        },
+        {
+         "id": 128288439397,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:33:40Z",
+         "started_at": "2026-11-07T03:34:21Z",
+         "completed_at": "2026-11-07T03:34:27Z"
+        },
+        {
+         "id": 128288439409,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:33:40Z",
+         "started_at": "2026-11-07T03:34:04Z",
+         "completed_at": "2026-11-07T03:34:39Z"
+        },
+        {
+         "id": 128288439451,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:33:40Z",
+         "started_at": "2026-11-07T03:34:28Z",
+         "completed_at": "2026-11-07T03:34:40Z"
+        },
+        {
+         "id": 128289434439,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:37:48Z",
+         "started_at": "2026-11-07T03:37:48Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128289434658,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:37:48Z",
+         "started_at": "2026-11-07T03:37:48Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128291102764,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:10Z",
+         "started_at": "2026-11-07T03:45:13Z",
+         "completed_at": "2026-11-07T03:45:50Z"
+        },
+        {
+         "id": 128291256420,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:45:50Z",
+         "started_at": "2026-11-07T03:46:32Z",
+         "completed_at": "2026-11-07T03:47:00Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T04:03:15Z",
+       "jobs": [
+        {
+         "id": 128295161009,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:17Z",
+         "started_at": "2026-11-07T03:11:49Z",
+         "completed_at": "2026-11-07T03:11:58Z"
+        },
+        {
+         "id": 128295161517,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128295161566,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:16:27Z",
+         "completed_at": "2026-11-07T03:16:44Z"
+        },
+        {
+         "id": 128295161597,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:13:26Z",
+         "completed_at": "2026-11-07T03:14:40Z"
+        },
+        {
+         "id": 128295161601,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:13:31Z",
+         "completed_at": "2026-11-07T03:14:09Z"
+        },
+        {
+         "id": 128295161606,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T04:03:17Z"
+        },
+        {
+         "id": 128295161634,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:14:18Z",
+         "completed_at": "2026-11-07T03:15:00Z"
+        },
+        {
+         "id": 128295161674,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:16:47Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128295161934,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:12:51Z",
+         "completed_at": "2026-11-07T03:13:22Z"
+        },
+        {
+         "id": 128295161961,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:14:12Z",
+         "completed_at": "2026-11-07T03:14:33Z"
+        },
+        {
+         "id": 128295161985,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128295162018,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "cancelled",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:15:08Z",
+         "completed_at": "2026-11-07T03:45:10Z"
+        },
+        {
+         "id": 128295162029,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:14:52Z",
+         "completed_at": "2026-11-07T03:15:08Z"
+        },
+        {
+         "id": 128295162045,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:15:31Z",
+         "completed_at": "2026-11-07T03:15:49Z"
+        },
+        {
+         "id": 128295162073,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:16:36Z",
+         "completed_at": "2026-11-07T03:17:23Z"
+        },
+        {
+         "id": 128295162138,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128295162141,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:13:13Z",
+         "completed_at": "2026-11-07T03:13:24Z"
+        },
+        {
+         "id": 128295162177,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:14:45Z",
+         "completed_at": "2026-11-07T03:19:24Z"
+        },
+        {
+         "id": 128295162188,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:15:37Z",
+         "completed_at": "2026-11-07T03:16:07Z"
+        },
+        {
+         "id": 128295162191,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:15:09Z",
+         "completed_at": "2026-11-07T03:16:24Z"
+        },
+        {
+         "id": 128295162193,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:15:52Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128295162244,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:33:36Z"
+        },
+        {
+         "id": 128295162288,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:21:41Z"
+        },
+        {
+         "id": 128295162292,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:29:42Z"
+        },
+        {
+         "id": 128295162409,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:18:41Z"
+        },
+        {
+         "id": 128295162558,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128295162604,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:17:18Z"
+        },
+        {
+         "id": 128295162629,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:18:40Z"
+        },
+        {
+         "id": 128295162964,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:34:21Z",
+         "completed_at": "2026-11-07T03:34:27Z"
+        },
+        {
+         "id": 128295163098,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:34:28Z",
+         "completed_at": "2026-11-07T03:34:40Z"
+        },
+        {
+         "id": 128295163244,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:17:21Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128295163327,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:34:04Z",
+         "completed_at": "2026-11-07T03:34:39Z"
+        },
+        {
+         "id": 128295163353,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128295163373,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:16:33Z"
+        },
+        {
+         "id": 128295163374,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:29:42Z"
+        },
+        {
+         "id": 128295163417,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:20Z",
+         "completed_at": "2026-11-07T04:06:09Z"
+        },
+        {
+         "id": 128295163610,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:18Z",
+         "completed_at": "2026-11-07T03:37:48Z"
+        },
+        {
+         "id": 128295164269,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:45:13Z",
+         "completed_at": "2026-11-07T03:45:50Z"
+        },
+        {
+         "id": 128295187600,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:24Z",
+         "started_at": "2026-11-07T03:12:17Z",
+         "completed_at": "2026-11-07T03:12:38Z"
+        },
+        {
+         "id": 128295191986,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:25Z",
+         "started_at": "2026-11-07T03:12:01Z",
+         "completed_at": "2026-11-07T03:12:37Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42332777827,
+     "title": "CI edit pr=3265 base=main sha=21b2a2d65a9d9861bf3ff2b017658c0bcf154b25",
+     "created_at": "2026-11-07T03:10:45Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T03:10:45Z",
+       "jobs": [
+        {
+         "id": 128282834671,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:45Z",
+         "started_at": "2026-11-07T03:10:53Z",
+         "completed_at": "2026-11-07T03:11:24Z"
+        },
+        {
+         "id": 128282834913,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:45Z",
+         "started_at": "2026-11-07T03:11:30Z",
+         "completed_at": "2026-11-07T03:11:38Z"
+        },
+        {
+         "id": 128282834969,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:10:45Z",
+         "started_at": "2026-11-07T03:11:46Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283213899,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:27Z",
+         "completed_at": "2026-11-07T03:13:28Z"
+        },
+        {
+         "id": 128283213956,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:41Z",
+         "completed_at": "2026-11-07T03:13:11Z"
+        },
+        {
+         "id": 128283214795,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283214918,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283214926,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283215083,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283215358,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283215683,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:12:15Z",
+         "started_at": "2026-11-07T03:12:15Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128283535088,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T03:13:29Z",
+         "started_at": "2026-11-07T03:13:34Z",
+         "completed_at": "2026-11-07T03:14:04Z"
+        },
+        {
+         "id": 128283535963,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:13:29Z",
+         "started_at": "2026-11-07T03:13:29Z",
+         "completed_at": "2026-11-07T03:13:29Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T03:48:55Z",
+       "jobs": [
+        {
+         "id": 128291967008,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:49:28Z",
+         "completed_at": "2026-11-07T03:49:59Z"
+        },
+        {
+         "id": 128291967151,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:10:53Z",
+         "completed_at": "2026-11-07T03:11:24Z"
+        },
+        {
+         "id": 128291967434,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:48:57Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128291967639,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:48:57Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128291967662,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:48:57Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128291967688,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:12:41Z",
+         "completed_at": "2026-11-07T03:13:11Z"
+        },
+        {
+         "id": 128291967748,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:48:57Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128291967821,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:48:57Z",
+         "started_at": "2026-11-07T03:48:57Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128291994194,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:49:04Z",
+         "started_at": "2026-11-07T03:12:27Z",
+         "completed_at": "2026-11-07T03:13:28Z"
+        },
+        {
+         "id": 128291996700,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:49:05Z",
+         "started_at": "2026-11-07T03:49:05Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128292001746,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T03:49:06Z",
+         "started_at": "2026-11-07T03:49:06Z",
+         "completed_at": "2026-11-07T03:48:57Z"
+        },
+        {
+         "id": 128292002722,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:49:06Z",
+         "started_at": "2026-11-07T03:11:30Z",
+         "completed_at": "2026-11-07T03:11:38Z"
+        },
+        {
+         "id": 128292003212,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T03:49:06Z",
+         "started_at": "2026-11-07T03:11:46Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T04:03:16Z",
+       "jobs": [
+        {
+         "id": 128295165802,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:10:53Z",
+         "completed_at": "2026-11-07T03:11:24Z"
+        },
+        {
+         "id": 128295165813,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T04:03:21Z",
+         "completed_at": "2026-11-07T04:03:50Z"
+        },
+        {
+         "id": 128295165829,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:18Z",
+         "started_at": "2026-11-07T03:11:30Z",
+         "completed_at": "2026-11-07T03:11:38Z"
+        },
+        {
+         "id": 128295166270,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T03:12:27Z",
+         "completed_at": "2026-11-07T03:13:28Z"
+        },
+        {
+         "id": 128295166378,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295166467,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295166515,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295166539,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295166633,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295166876,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T03:12:41Z",
+         "completed_at": "2026-11-07T03:13:11Z"
+        },
+        {
+         "id": 128295166970,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:19Z",
+         "started_at": "2026-11-07T04:03:19Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295188118,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:03:24Z",
+         "started_at": "2026-11-07T04:03:24Z",
+         "completed_at": "2026-11-07T04:03:18Z"
+        },
+        {
+         "id": 128295188359,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:03:24Z",
+         "started_at": "2026-11-07T03:11:46Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T04:06:08Z",
+       "jobs": [
+        {
+         "id": 128295859545,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T03:11:46Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128295859611,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T04:06:14Z",
+         "completed_at": "2026-11-07T04:06:48Z"
+        },
+        {
+         "id": 128295859887,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T03:10:53Z",
+         "completed_at": "2026-11-07T03:11:24Z"
+        },
+        {
+         "id": 128295859974,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T04:06:11Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295860143,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T03:12:41Z",
+         "completed_at": "2026-11-07T03:13:11Z"
+        },
+        {
+         "id": 128295860202,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T04:06:11Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295860280,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T03:12:27Z",
+         "completed_at": "2026-11-07T03:13:28Z"
+        },
+        {
+         "id": 128295860438,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T04:06:11Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295860635,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:11Z",
+         "started_at": "2026-11-07T04:06:11Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295885997,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:06:17Z",
+         "started_at": "2026-11-07T03:11:30Z",
+         "completed_at": "2026-11-07T03:11:38Z"
+        },
+        {
+         "id": 128295889772,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:18Z",
+         "started_at": "2026-11-07T04:06:18Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295890131,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:19Z",
+         "started_at": "2026-11-07T04:06:19Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        },
+        {
+         "id": 128295892005,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:06:19Z",
+         "started_at": "2026-11-07T04:06:19Z",
+         "completed_at": "2026-11-07T04:06:11Z"
+        }
+       ]
+      },
+      {
+       "n": 5,
+       "run_started_at": "2026-11-07T04:07:35Z",
+       "jobs": [
+        {
+         "id": 128296192993,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T03:10:53Z",
+         "completed_at": "2026-11-07T03:11:24Z"
+        },
+        {
+         "id": 128296193620,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:40Z",
+         "completed_at": "2026-11-07T04:08:17Z"
+        },
+        {
+         "id": 128296193628,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296193738,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T03:11:46Z",
+         "completed_at": "2026-11-07T03:12:15Z"
+        },
+        {
+         "id": 128296193757,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296193773,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296194097,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T03:12:41Z",
+         "completed_at": "2026-11-07T03:13:11Z"
+        },
+        {
+         "id": 128296194109,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296194242,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296194423,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T04:07:37Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        },
+        {
+         "id": 128296194567,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:37Z",
+         "started_at": "2026-11-07T03:12:27Z",
+         "completed_at": "2026-11-07T03:13:28Z"
+        },
+        {
+         "id": 128296228678,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T03:11:30Z",
+         "completed_at": "2026-11-07T03:11:38Z"
+        },
+        {
+         "id": 128296232252,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:07:46Z",
+         "started_at": "2026-11-07T04:07:46Z",
+         "completed_at": "2026-11-07T04:07:37Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42332777827,
+     "attempt": 4,
+     "job": 128295859611,
+     "started_at": "2026-11-07T04:06:14Z",
+     "completed_at": "2026-11-07T04:06:48Z",
+     "conclusion": "failure",
+     "pin": "f2a015142714383722bf49d7ab20d8398ec9674c",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42333388705] at this head are still being judged; their gate decides"
+    },
+    {
+     "run": 42333388705,
+     "attempt": 4,
+     "job": 128295878197,
+     "started_at": "2026-11-07T04:06:18Z",
+     "completed_at": "2026-11-07T04:06:47Z",
+     "conclusion": "failure",
+     "pin": "f2a015142714383722bf49d7ab20d8398ec9674c",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42332777827] at this head are still being judged; their gate decides"
+    }
+   ]
+  },
+  {
+   "name": "3255-pair",
+   "pr": "3255",
+   "head": "2ad28ecb50906877b34a378cacd8085e6afca029",
+   "runs": [
+    {
+     "id": 42339824517,
+     "title": "CI review pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T04:45:31Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:45:31Z",
+       "jobs": [
+        {
+         "id": 128304810894,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:45:32Z",
+         "started_at": "2026-11-07T04:46:41Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128304811057,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:45:32Z",
+         "started_at": "2026-11-07T04:47:22Z",
+         "completed_at": "2026-11-07T04:48:00Z"
+        },
+        {
+         "id": 128304812203,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:45:32Z",
+         "started_at": "2026-11-07T04:45:32Z",
+         "completed_at": "2026-11-07T04:45:32Z"
+        },
+        {
+         "id": 128305165510,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "queued",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": null
+        },
+        {
+         "id": 128305166164,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166291,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166554,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166680,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166776,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166885,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        },
+        {
+         "id": 128305166893,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:09Z",
+         "started_at": "2026-11-07T04:47:09Z",
+         "completed_at": "2026-11-07T04:47:09Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42339614618,
+     "title": "CI review pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T04:42:35Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:42:35Z",
+       "jobs": [
+        {
+         "id": 128304170280,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:42:35Z",
+         "started_at": "2026-11-07T04:43:42Z",
+         "completed_at": "2026-11-07T04:44:25Z"
+        },
+        {
+         "id": 128304170474,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:42:36Z",
+         "started_at": "2026-11-07T04:43:52Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304171195,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:42:36Z",
+         "started_at": "2026-11-07T04:42:36Z",
+         "completed_at": "2026-11-07T04:42:35Z"
+        },
+        {
+         "id": 128304569677,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:45:47Z",
+         "completed_at": "2026-11-07T04:46:16Z"
+        },
+        {
+         "id": 128304570292,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570362,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570373,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570452,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570654,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570729,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304570835,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T04:44:26Z"
+        },
+        {
+         "id": 128304974421,
+         "name": "gate",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:46:17Z",
+         "started_at": "2026-11-07T04:48:09Z",
+         "completed_at": null
+        },
+        {
+         "id": 128304975980,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:46:17Z",
+         "started_at": "2026-11-07T04:46:17Z",
+         "completed_at": "2026-11-07T04:46:17Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42339292099,
+     "title": "CI review pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T04:37:55Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:37:55Z",
+       "jobs": [
+        {
+         "id": 128303176523,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:37:55Z",
+         "started_at": "2026-11-07T04:37:58Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303176648,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:37:55Z",
+         "started_at": "2026-11-07T04:37:58Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303177325,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:37:56Z",
+         "started_at": "2026-11-07T04:37:56Z",
+         "completed_at": "2026-11-07T04:37:55Z"
+        },
+        {
+         "id": 128303294557,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:39:07Z"
+        },
+        {
+         "id": 128303295430,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303295503,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303295782,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303295850,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303295909,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303295943,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303296031,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:29Z",
+         "started_at": "2026-11-07T04:38:29Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128303424199,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:39:07Z",
+         "started_at": "2026-11-07T04:39:09Z",
+         "completed_at": "2026-11-07T04:39:39Z"
+        },
+        {
+         "id": 128303425048,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:39:07Z",
+         "started_at": "2026-11-07T04:39:07Z",
+         "completed_at": "2026-11-07T04:39:07Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T04:44:17Z",
+       "jobs": [
+        {
+         "id": 128304542553,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:18Z",
+         "started_at": "2026-11-07T04:44:18Z",
+         "completed_at": "2026-11-07T04:37:55Z"
+        },
+        {
+         "id": 128304542572,
+         "name": "gate",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:44:18Z",
+         "started_at": "2026-11-07T04:44:50Z",
+         "completed_at": null
+        },
+        {
+         "id": 128304542730,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:18Z",
+         "started_at": "2026-11-07T04:37:58Z",
+         "completed_at": "2026-11-07T04:38:29Z"
+        },
+        {
+         "id": 128304543091,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304543191,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:37:58Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128304543212,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304543227,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304543422,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:39:07Z"
+        },
+        {
+         "id": 128304543492,
+         "name": "arch-score",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304543613,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304543903,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:19Z",
+         "started_at": "2026-11-07T04:44:19Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304574424,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:28Z",
+         "started_at": "2026-11-07T04:44:28Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        },
+        {
+         "id": 128304576933,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:28Z",
+         "started_at": "2026-11-07T04:44:28Z",
+         "completed_at": "2026-11-07T04:44:18Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42322943199,
+     "title": "CI edit pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T01:14:11Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T01:14:11Z",
+       "jobs": [
+        {
+         "id": 128251528481,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:14:12Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:49Z"
+        },
+        {
+         "id": 128251528683,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:14:12Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251528913,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:14:12Z",
+         "started_at": "2026-11-07T01:14:34Z",
+         "completed_at": "2026-11-07T01:14:43Z"
+        },
+        {
+         "id": 128251724008,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:14:52Z",
+         "started_at": "2026-11-07T01:15:09Z",
+         "completed_at": "2026-11-07T01:15:35Z"
+        },
+        {
+         "id": 128251724040,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:14:52Z",
+         "started_at": "2026-11-07T01:15:11Z",
+         "completed_at": "2026-11-07T01:16:12Z"
+        },
+        {
+         "id": 128251724940,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251725187,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251725344,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251725445,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251725613,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128251725772,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:14:53Z",
+         "started_at": "2026-11-07T01:14:53Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128252139285,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T01:16:12Z",
+         "started_at": "2026-11-07T01:17:15Z",
+         "completed_at": "2026-11-07T01:17:47Z"
+        },
+        {
+         "id": 128252139748,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:16:12Z",
+         "started_at": "2026-11-07T01:16:12Z",
+         "completed_at": "2026-11-07T01:16:12Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T01:34:36Z",
+       "jobs": [
+        {
+         "id": 128257498742,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:40Z",
+         "completed_at": "2026-11-07T01:35:13Z"
+        },
+        {
+         "id": 128257498811,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128257499289,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:49Z"
+        },
+        {
+         "id": 128257499445,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499483,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499507,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:15:09Z",
+         "completed_at": "2026-11-07T01:15:35Z"
+        },
+        {
+         "id": 128257499577,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499674,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499687,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499727,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499920,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:38Z"
+        },
+        {
+         "id": 128257499945,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:15:11Z",
+         "completed_at": "2026-11-07T01:16:12Z"
+        },
+        {
+         "id": 128257528236,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:44Z",
+         "started_at": "2026-11-07T01:14:34Z",
+         "completed_at": "2026-11-07T01:14:43Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T04:38:30Z",
+       "jobs": [
+        {
+         "id": 128303305061,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128303305624,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:35Z",
+         "completed_at": "2026-11-07T04:39:04Z"
+        },
+        {
+         "id": 128303305626,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305630,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T01:15:11Z",
+         "completed_at": "2026-11-07T01:16:12Z"
+        },
+        {
+         "id": 128303305650,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305691,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305726,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305728,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305741,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303305785,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:49Z"
+        },
+        {
+         "id": 128303305851,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T01:15:09Z",
+         "completed_at": "2026-11-07T01:15:35Z"
+        },
+        {
+         "id": 128303306298,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:32Z",
+         "started_at": "2026-11-07T04:38:32Z",
+         "completed_at": "2026-11-07T04:38:32Z"
+        },
+        {
+         "id": 128303337364,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:14:34Z",
+         "completed_at": "2026-11-07T01:14:43Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T04:40:12Z",
+       "jobs": [
+        {
+         "id": 128303662681,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:40:14Z",
+         "started_at": "2026-11-07T04:40:22Z",
+         "completed_at": "2026-11-07T04:41:00Z"
+        },
+        {
+         "id": 128303662937,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:14Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:49Z"
+        },
+        {
+         "id": 128303663221,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:14Z",
+         "started_at": "2026-11-07T01:14:23Z",
+         "completed_at": "2026-11-07T01:14:52Z"
+        },
+        {
+         "id": 128303663431,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:14Z",
+         "started_at": "2026-11-07T04:40:14Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303663607,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:15Z",
+         "started_at": "2026-11-07T04:40:15Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303664248,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:15Z",
+         "started_at": "2026-11-07T04:40:15Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303685970,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:20Z",
+         "started_at": "2026-11-07T04:40:20Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303687199,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:21Z",
+         "started_at": "2026-11-07T01:14:34Z",
+         "completed_at": "2026-11-07T01:14:43Z"
+        },
+        {
+         "id": 128303694679,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T04:40:23Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303695123,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T01:15:11Z",
+         "completed_at": "2026-11-07T01:16:12Z"
+        },
+        {
+         "id": 128303696490,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T04:40:23Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303697197,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T04:40:23Z",
+         "completed_at": "2026-11-07T04:40:14Z"
+        },
+        {
+         "id": 128303697895,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T01:15:09Z",
+         "completed_at": "2026-11-07T01:15:35Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42321825054,
+     "title": "CI edit pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T01:02:41Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T01:02:41Z",
+       "jobs": [
+        {
+         "id": 128247923747,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:16Z"
+        },
+        {
+         "id": 128247924017,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128247924049,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:45Z",
+         "completed_at": "2026-11-07T01:02:55Z"
+        },
+        {
+         "id": 128248087589,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:03:49Z"
+        },
+        {
+         "id": 128248087695,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:04:15Z"
+        },
+        {
+         "id": 128248089051,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:13Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248089068,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:13Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248089369,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:13Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248089433,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:13Z",
+         "started_at": "2026-11-07T01:03:13Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248089467,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:14Z",
+         "started_at": "2026-11-07T01:03:14Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248089491,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:14Z",
+         "started_at": "2026-11-07T01:03:14Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128248412839,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T01:04:16Z",
+         "started_at": "2026-11-07T01:04:40Z",
+         "completed_at": "2026-11-07T01:05:15Z"
+        },
+        {
+         "id": 128248413471,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:04:16Z",
+         "started_at": "2026-11-07T01:04:16Z",
+         "completed_at": "2026-11-07T01:04:16Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T01:34:30Z",
+       "jobs": [
+        {
+         "id": 128257474644,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128257474821,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:34:35Z",
+         "completed_at": "2026-11-07T01:35:08Z"
+        },
+        {
+         "id": 128257474968,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:03:49Z"
+        },
+        {
+         "id": 128257475204,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:04:15Z"
+        },
+        {
+         "id": 128257475596,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:34:33Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257476214,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:33Z",
+         "started_at": "2026-11-07T01:34:33Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257498213,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:02:45Z",
+         "completed_at": "2026-11-07T01:02:55Z"
+        },
+        {
+         "id": 128257498431,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257500958,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:38Z",
+         "started_at": "2026-11-07T01:34:38Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257504908,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:34:39Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:16Z"
+        },
+        {
+         "id": 128257509403,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:40Z",
+         "started_at": "2026-11-07T01:34:40Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257510782,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:41Z",
+         "started_at": "2026-11-07T01:34:41Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        },
+        {
+         "id": 128257516501,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:34:42Z",
+         "started_at": "2026-11-07T01:34:42Z",
+         "completed_at": "2026-11-07T01:34:32Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T01:35:27Z",
+       "jobs": [
+        {
+         "id": 128257741570,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:02:45Z",
+         "completed_at": "2026-11-07T01:02:55Z"
+        },
+        {
+         "id": 128257742171,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257742377,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257742491,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257742496,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:32Z",
+         "completed_at": "2026-11-07T01:36:02Z"
+        },
+        {
+         "id": 128257742873,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257743075,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:03:49Z"
+        },
+        {
+         "id": 128257743231,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:04:15Z"
+        },
+        {
+         "id": 128257743345,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257743832,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:29Z",
+         "started_at": "2026-11-07T01:35:29Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257773063,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:35Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:16Z"
+        },
+        {
+         "id": 128257787309,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:35:38Z",
+         "started_at": "2026-11-07T01:35:38Z",
+         "completed_at": "2026-11-07T01:35:29Z"
+        },
+        {
+         "id": 128257790557,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:35:38Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        }
+       ]
+      },
+      {
+       "n": 4,
+       "run_started_at": "2026-11-07T04:38:36Z",
+       "jobs": [
+        {
+         "id": 128303325171,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T04:38:41Z",
+         "completed_at": "2026-11-07T04:39:15Z"
+        },
+        {
+         "id": 128303325325,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:16Z"
+        },
+        {
+         "id": 128303325706,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:03:49Z"
+        },
+        {
+         "id": 128303325852,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T04:38:38Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303325941,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T04:38:38Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303326031,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T04:38:38Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303326041,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:38Z",
+         "started_at": "2026-11-07T04:38:38Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303346806,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:44Z",
+         "started_at": "2026-11-07T04:38:44Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303348749,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:45Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128303349432,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:45Z",
+         "started_at": "2026-11-07T01:02:45Z",
+         "completed_at": "2026-11-07T01:02:55Z"
+        },
+        {
+         "id": 128303349588,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:45Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:04:15Z"
+        },
+        {
+         "id": 128303356202,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:47Z",
+         "started_at": "2026-11-07T04:38:47Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        },
+        {
+         "id": 128303357025,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:47Z",
+         "started_at": "2026-11-07T04:38:47Z",
+         "completed_at": "2026-11-07T04:38:38Z"
+        }
+       ]
+      },
+      {
+       "n": 5,
+       "run_started_at": "2026-11-07T04:40:10Z",
+       "jobs": [
+        {
+         "id": 128303658267,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:16Z",
+         "completed_at": "2026-11-07T04:40:51Z"
+        },
+        {
+         "id": 128303658369,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:13Z"
+        },
+        {
+         "id": 128303658658,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:13Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303658795,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:13Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303658816,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:13Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303658818,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:13Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303658837,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:04:15Z"
+        },
+        {
+         "id": 128303658870,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:13Z",
+         "started_at": "2026-11-07T04:40:13Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303687726,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:21Z",
+         "started_at": "2026-11-07T01:02:45Z",
+         "completed_at": "2026-11-07T01:02:55Z"
+        },
+        {
+         "id": 128303688743,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:21Z",
+         "started_at": "2026-11-07T04:40:21Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303689040,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:21Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:16Z"
+        },
+        {
+         "id": 128303690485,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:40:21Z",
+         "started_at": "2026-11-07T04:40:21Z",
+         "completed_at": "2026-11-07T04:40:13Z"
+        },
+        {
+         "id": 128303696174,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:40:23Z",
+         "started_at": "2026-11-07T01:03:16Z",
+         "completed_at": "2026-11-07T01:03:49Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42321824512,
+     "title": "CI code pr=3255 base=main sha=e27a970bff188b81bd6b1202e58396594caeaf1c",
+     "created_at": "2026-11-07T01:02:41Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T01:02:41Z",
+       "jobs": [
+        {
+         "id": 128247922362,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128247922763,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:21Z"
+        },
+        {
+         "id": 128247922823,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:02:42Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:02:52Z"
+        },
+        {
+         "id": 128248097405,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:42Z"
+        },
+        {
+         "id": 128248097419,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:52Z"
+        },
+        {
+         "id": 128248097484,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:39Z"
+        },
+        {
+         "id": 128248097531,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:36Z"
+        },
+        {
+         "id": 128248097571,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128248097601,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128248097615,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128248097664,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128248097679,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:05:54Z"
+        },
+        {
+         "id": 128248097683,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:28Z"
+        },
+        {
+         "id": 128248097694,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:02Z"
+        },
+        {
+         "id": 128248097702,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:10:11Z"
+        },
+        {
+         "id": 128248097706,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:31Z"
+        },
+        {
+         "id": 128248097717,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:33:12Z"
+        },
+        {
+         "id": 128248097796,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128248097812,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:50Z"
+        },
+        {
+         "id": 128248098793,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:15Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128248099577,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:15Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128248099635,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:15Z",
+         "started_at": "2026-11-07T01:03:15Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128248248695,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:49Z"
+        },
+        {
+         "id": 128248248699,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:38Z"
+        },
+        {
+         "id": 128248248718,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:08:20Z"
+        },
+        {
+         "id": 128248248719,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:12:26Z"
+        },
+        {
+         "id": 128248248810,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:20:11Z"
+        },
+        {
+         "id": 128248248833,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:50Z",
+         "completed_at": "2026-11-07T01:24:14Z"
+        },
+        {
+         "id": 128248250385,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:44Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128248250611,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:03:44Z",
+         "started_at": "2026-11-07T01:03:44Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128248333013,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:04:00Z",
+         "started_at": "2026-11-07T01:04:00Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128248334029,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:04:01Z",
+         "started_at": "2026-11-07T01:04:01Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128250989602,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:12:27Z",
+         "started_at": "2026-11-07T01:12:27Z",
+         "completed_at": "2026-11-07T01:12:27Z"
+        },
+        {
+         "id": 128253328361,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:20:11Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:24:57Z"
+        },
+        {
+         "id": 128253328392,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:20:11Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:24Z"
+        },
+        {
+         "id": 128253328459,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:20:11Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:21Z"
+        },
+        {
+         "id": 128254536564,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:24:15Z",
+         "started_at": "2026-11-07T01:24:15Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128254536843,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T01:24:15Z",
+         "started_at": "2026-11-07T01:24:15Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128257095312,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:33:12Z",
+         "started_at": "2026-11-07T01:33:15Z",
+         "completed_at": "2026-11-07T01:33:49Z"
+        },
+        {
+         "id": 128257274132,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T01:33:50Z",
+         "started_at": "2026-11-07T01:33:52Z",
+         "completed_at": "2026-11-07T01:34:22Z"
+        }
+       ]
+      },
+      {
+       "n": 2,
+       "run_started_at": "2026-11-07T04:38:34Z",
+       "jobs": [
+        {
+         "id": 128303318526,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:21Z"
+        },
+        {
+         "id": 128303318746,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128303318768,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:50Z"
+        },
+        {
+         "id": 128303318952,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:52Z"
+        },
+        {
+         "id": 128303318989,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:20:11Z"
+        },
+        {
+         "id": 128303319026,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128303319050,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:31Z"
+        },
+        {
+         "id": 128303319053,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:28Z"
+        },
+        {
+         "id": 128303319061,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128303319139,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:38Z"
+        },
+        {
+         "id": 128303319155,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:42Z"
+        },
+        {
+         "id": 128303319269,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:50Z",
+         "completed_at": "2026-11-07T01:24:14Z"
+        },
+        {
+         "id": 128303319276,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:49Z"
+        },
+        {
+         "id": 128303319358,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128303319400,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128303319405,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:12:26Z"
+        },
+        {
+         "id": 128303319507,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:39Z",
+         "completed_at": "2026-11-07T04:41:30Z"
+        },
+        {
+         "id": 128303319509,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:08:20Z"
+        },
+        {
+         "id": 128303319536,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:24Z"
+        },
+        {
+         "id": 128303319559,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128303319686,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128303319751,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128303319813,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:21Z"
+        },
+        {
+         "id": 128303319864,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:24:57Z"
+        },
+        {
+         "id": 128303319880,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128303319970,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:12:27Z"
+        },
+        {
+         "id": 128303320112,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T04:38:36Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128303320215,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:36Z",
+         "started_at": "2026-11-07T01:33:15Z",
+         "completed_at": "2026-11-07T01:33:49Z"
+        },
+        {
+         "id": 128303337485,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:39Z"
+        },
+        {
+         "id": 128303338092,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:36Z"
+        },
+        {
+         "id": 128303338182,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:33:12Z"
+        },
+        {
+         "id": 128303338208,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:10:11Z"
+        },
+        {
+         "id": 128303339361,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:42Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:02Z"
+        },
+        {
+         "id": 128303340579,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:43Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128303342003,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:43Z",
+         "started_at": "2026-11-07T04:38:43Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128303342398,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:43Z",
+         "started_at": "2026-11-07T04:38:43Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128303345035,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:44Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:02:52Z"
+        },
+        {
+         "id": 128303346875,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:44Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:05:54Z"
+        },
+        {
+         "id": 128303349265,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:38:45Z",
+         "started_at": "2026-11-07T04:38:45Z",
+         "completed_at": "2026-11-07T04:38:36Z"
+        },
+        {
+         "id": 128303349752,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:38:45Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        }
+       ]
+      },
+      {
+       "n": 3,
+       "run_started_at": "2026-11-07T04:44:23Z",
+       "jobs": [
+        {
+         "id": 128304566217,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:02:52Z"
+        },
+        {
+         "id": 128304566514,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128304566704,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:36Z"
+        },
+        {
+         "id": 128304566779,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T04:44:25Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128304566848,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128304566856,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:10:11Z"
+        },
+        {
+         "id": 128304566897,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128304566935,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T04:44:25Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128304567028,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:31Z"
+        },
+        {
+         "id": 128304567046,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128304567053,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:52Z"
+        },
+        {
+         "id": 128304567066,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:35Z"
+        },
+        {
+         "id": 128304567098,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:05:54Z"
+        },
+        {
+         "id": 128304567103,
+         "name": "governance / instrument-self-tests",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:33:12Z"
+        },
+        {
+         "id": 128304567120,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T04:44:25Z",
+         "completed_at": "2026-11-07T04:44:25Z"
+        },
+        {
+         "id": 128304567126,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:02Z"
+        },
+        {
+         "id": 128304567162,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:17Z",
+         "completed_at": "2026-11-07T01:03:42Z"
+        },
+        {
+         "id": 128304567171,
+         "name": "gate",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T04:46:32Z",
+         "completed_at": null
+        },
+        {
+         "id": 128304567173,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:12:26Z"
+        },
+        {
+         "id": 128304567184,
+         "name": "tests / coverage",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:20:11Z"
+        },
+        {
+         "id": 128304567187,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:08:20Z"
+        },
+        {
+         "id": 128304567225,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T04:44:25Z",
+         "completed_at": "2026-11-07T01:03:15Z"
+        },
+        {
+         "id": 128304567274,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:39Z"
+        },
+        {
+         "id": 128304567275,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:03:50Z"
+        },
+        {
+         "id": 128304567278,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128304567407,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:25Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:38Z"
+        },
+        {
+         "id": 128304567587,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128304567656,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:04:00Z"
+        },
+        {
+         "id": 128304567676,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:12:27Z"
+        },
+        {
+         "id": 128304567717,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:03:50Z",
+         "completed_at": "2026-11-07T01:24:14Z"
+        },
+        {
+         "id": 128304567751,
+         "name": "tests / graders-head-copy",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:24:57Z"
+        },
+        {
+         "id": 128304567758,
+         "name": "tests / ci-ratchet",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128304567760,
+         "name": "tests / coverage-ratchet",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:24Z"
+        },
+        {
+         "id": 128304567774,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:24:15Z"
+        },
+        {
+         "id": 128304567776,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T04:44:26Z",
+         "completed_at": "2026-11-07T01:03:44Z"
+        },
+        {
+         "id": 128304567788,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:03:46Z",
+         "completed_at": "2026-11-07T01:04:49Z"
+        },
+        {
+         "id": 128304567882,
+         "name": "tests / lane-proofs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:20:14Z",
+         "completed_at": "2026-11-07T01:20:21Z"
+        },
+        {
+         "id": 128304568032,
+         "name": "pr-contract / pr-contract",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:26Z",
+         "started_at": "2026-11-07T01:33:15Z",
+         "completed_at": "2026-11-07T01:33:49Z"
+        },
+        {
+         "id": 128304585434,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:31Z",
+         "started_at": "2026-11-07T01:03:18Z",
+         "completed_at": "2026-11-07T01:04:28Z"
+        },
+        {
+         "id": 128304586258,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:44:31Z",
+         "started_at": "2026-11-07T01:02:44Z",
+         "completed_at": "2026-11-07T01:03:21Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42321825054,
+     "attempt": 5,
+     "job": 128303658267,
+     "started_at": "2026-11-07T04:40:16Z",
+     "completed_at": "2026-11-07T04:40:51Z",
+     "conclusion": "failure",
+     "pin": "80016a71f567d936450d8708abcbb79d9e8071d7",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42322943199] at this head are still being judged; their gate decides"
+    },
+    {
+     "run": 42322943199,
+     "attempt": 4,
+     "job": 128303662681,
+     "started_at": "2026-11-07T04:40:22Z",
+     "completed_at": "2026-11-07T04:41:00Z",
+     "conclusion": "failure",
+     "pin": "80016a71f567d936450d8708abcbb79d9e8071d7",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42321825054] at this head are still being judged; their gate decides"
+    }
+   ]
+  },
+  {
+   "name": "3263-c3",
+   "pr": "3263",
+   "head": "02e92e7cbcb95c32fbb2ad3a7a46a8d465a436d8",
+   "runs": [
+    {
+     "id": 42338396871,
+     "title": "CI code pr=3263 base=main sha=e04d1f00da70b39c0cd8d1483219a6ddfaf0039f",
+     "created_at": "2026-11-07T04:25:27Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:25:27Z",
+       "jobs": [
+        {
+         "id": 128300410853,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:31Z",
+         "completed_at": "2026-11-07T04:25:40Z"
+        },
+        {
+         "id": 128300410924,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:31Z",
+         "completed_at": "2026-11-07T04:26:08Z"
+        },
+        {
+         "id": 128300410939,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:30Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300495382,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:12Z"
+        },
+        {
+         "id": 128300495385,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:53Z",
+         "completed_at": "2026-11-07T04:26:33Z"
+        },
+        {
+         "id": 128300495389,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:19Z"
+        },
+        {
+         "id": 128300495401,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:10Z",
+         "completed_at": "2026-11-07T04:26:53Z"
+        },
+        {
+         "id": 128300495404,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:00Z",
+         "completed_at": "2026-11-07T04:27:26Z"
+        },
+        {
+         "id": 128300495412,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:58Z",
+         "completed_at": "2026-11-07T04:26:27Z"
+        },
+        {
+         "id": 128300495416,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:53Z",
+         "completed_at": "2026-11-07T04:26:09Z"
+        },
+        {
+         "id": 128300495445,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:11Z",
+         "completed_at": "2026-11-07T04:26:22Z"
+        },
+        {
+         "id": 128300495469,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:33Z"
+        },
+        {
+         "id": 128300495471,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:18Z"
+        },
+        {
+         "id": 128300495473,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:12Z"
+        },
+        {
+         "id": 128300495474,
+         "name": "governance / instrument-self-tests",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:10Z",
+         "completed_at": null
+        },
+        {
+         "id": 128300495481,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:11Z",
+         "completed_at": "2026-11-07T04:27:07Z"
+        },
+        {
+         "id": 128300495497,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:26:04Z",
+         "completed_at": "2026-11-07T04:32:24Z"
+        },
+        {
+         "id": 128300495501,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:22Z"
+        },
+        {
+         "id": 128300495534,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:54Z",
+         "completed_at": "2026-11-07T04:26:54Z"
+        },
+        {
+         "id": 128300496427,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300496444,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300496787,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:51Z",
+         "started_at": "2026-11-07T04:25:51Z",
+         "completed_at": "2026-11-07T04:25:51Z"
+        },
+        {
+         "id": 128300628273,
+         "name": "tests / coverage",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:29Z",
+         "completed_at": null
+        },
+        {
+         "id": 128300628284,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:29Z",
+         "completed_at": "2026-11-07T04:27:34Z"
+        },
+        {
+         "id": 128300628318,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:35Z",
+         "completed_at": "2026-11-07T04:31:13Z"
+        },
+        {
+         "id": 128300628328,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:29Z",
+         "completed_at": "2026-11-07T04:37:56Z"
+        },
+        {
+         "id": 128300628334,
+         "name": "tests / closures",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:29Z",
+         "completed_at": null
+        },
+        {
+         "id": 128300628345,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:35Z",
+         "completed_at": "2026-11-07T04:27:34Z"
+        },
+        {
+         "id": 128300629349,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:27Z",
+         "completed_at": "2026-11-07T04:26:27Z"
+        },
+        {
+         "id": 128300629765,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:26:27Z",
+         "started_at": "2026-11-07T04:26:27Z",
+         "completed_at": "2026-11-07T04:26:27Z"
+        },
+        {
+         "id": 128300728965,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:26:54Z",
+         "started_at": "2026-11-07T04:26:54Z",
+         "completed_at": "2026-11-07T04:26:53Z"
+        },
+        {
+         "id": 128300729300,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:26:54Z",
+         "started_at": "2026-11-07T04:26:54Z",
+         "completed_at": "2026-11-07T04:26:53Z"
+        },
+        {
+         "id": 128303181124,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:37:57Z",
+         "started_at": "2026-11-07T04:37:57Z",
+         "completed_at": "2026-11-07T04:37:56Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42338396358,
+     "title": "CI edit pr=3263 base=main sha=e04d1f00da70b39c0cd8d1483219a6ddfaf0039f",
+     "created_at": "2026-11-07T04:25:27Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:25:27Z",
+       "jobs": [
+        {
+         "id": 128300408866,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:30Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300408900,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:30Z",
+         "completed_at": "2026-11-07T04:25:39Z"
+        },
+        {
+         "id": 128300409051,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:28Z",
+         "started_at": "2026-11-07T04:25:30Z",
+         "completed_at": "2026-11-07T04:25:56Z"
+        },
+        {
+         "id": 128300523790,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:26:14Z",
+         "completed_at": "2026-11-07T04:27:26Z"
+        },
+        {
+         "id": 128300523832,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:26:14Z",
+         "completed_at": "2026-11-07T04:26:41Z"
+        },
+        {
+         "id": 128300524393,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300524565,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300524684,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300524896,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300524998,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300525244,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:25:59Z",
+         "started_at": "2026-11-07T04:25:59Z",
+         "completed_at": "2026-11-07T04:25:59Z"
+        },
+        {
+         "id": 128300847842,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:27:26Z",
+         "started_at": "2026-11-07T04:27:28Z",
+         "completed_at": "2026-11-07T04:28:01Z"
+        },
+        {
+         "id": 128300849116,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:27:26Z",
+         "started_at": "2026-11-07T04:27:26Z",
+         "completed_at": "2026-11-07T04:27:26Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42338396358,
+     "attempt": 1,
+     "job": 128300847842,
+     "started_at": "2026-11-07T04:27:28Z",
+     "completed_at": "2026-11-07T04:28:01Z",
+     "conclusion": "failure",
+     "pin": "294a880dae608502b62055775e34a5db93217b98",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42338396871] at this head are still being judged; their gate decides"
+    }
+   ]
+  },
+  {
+   "name": "3261-c3",
+   "pr": "3261",
+   "head": "61187afe6cfdc4416f161e23111571bc50d25d9c",
+   "runs": [
+    {
+     "id": 42338828950,
+     "title": "CI code pr=3261 base=main sha=f984b1874c67bd865836c2a2658ee2c635677a3a",
+     "created_at": "2026-11-07T04:31:29Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:31:29Z",
+       "jobs": [
+        {
+         "id": 128301748682,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:30Z",
+         "started_at": "2026-11-07T04:31:32Z",
+         "completed_at": "2026-11-07T04:31:41Z"
+        },
+        {
+         "id": 128301748938,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:30Z",
+         "started_at": "2026-11-07T04:31:33Z",
+         "completed_at": "2026-11-07T04:31:54Z"
+        },
+        {
+         "id": 128301748939,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:30Z",
+         "started_at": "2026-11-07T04:31:32Z",
+         "completed_at": "2026-11-07T04:31:57Z"
+        },
+        {
+         "id": 128301840071,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:32:14Z"
+        },
+        {
+         "id": 128301840088,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:34Z"
+        },
+        {
+         "id": 128301840104,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:32Z"
+        },
+        {
+         "id": 128301840108,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:40Z"
+        },
+        {
+         "id": 128301840112,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:19Z"
+        },
+        {
+         "id": 128301840122,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:06Z"
+        },
+        {
+         "id": 128301840149,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:14Z"
+        },
+        {
+         "id": 128301840189,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:38:23Z"
+        },
+        {
+         "id": 128301840191,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:29Z"
+        },
+        {
+         "id": 128301840204,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": "2026-11-07T04:32:34Z"
+        },
+        {
+         "id": 128301840225,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:33:11Z"
+        },
+        {
+         "id": 128301840251,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:32:49Z"
+        },
+        {
+         "id": 128301840329,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:33:09Z"
+        },
+        {
+         "id": 128301840331,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:32:16Z"
+        },
+        {
+         "id": 128301840337,
+         "name": "governance / instrument-self-tests",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:57Z",
+         "completed_at": null
+        },
+        {
+         "id": 128301840364,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:54Z",
+         "started_at": "2026-11-07T04:31:58Z",
+         "completed_at": "2026-11-07T04:32:17Z"
+        },
+        {
+         "id": 128301840989,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:31:55Z",
+         "started_at": "2026-11-07T04:31:55Z",
+         "completed_at": "2026-11-07T04:31:54Z"
+        },
+        {
+         "id": 128301841357,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:31:55Z",
+         "started_at": "2026-11-07T04:31:55Z",
+         "completed_at": "2026-11-07T04:31:54Z"
+        },
+        {
+         "id": 128301841579,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:31:55Z",
+         "started_at": "2026-11-07T04:31:55Z",
+         "completed_at": "2026-11-07T04:31:54Z"
+        },
+        {
+         "id": 128301981804,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:34Z",
+         "completed_at": "2026-11-07T04:36:59Z"
+        },
+        {
+         "id": 128301981813,
+         "name": "tests / closures",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:34Z",
+         "completed_at": null
+        },
+        {
+         "id": 128301981826,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:34Z",
+         "completed_at": "2026-11-07T04:41:10Z"
+        },
+        {
+         "id": 128301981848,
+         "name": "tests / coverage",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:35Z",
+         "completed_at": null
+        },
+        {
+         "id": 128301981852,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:35Z",
+         "completed_at": "2026-11-07T04:33:43Z"
+        },
+        {
+         "id": 128301981859,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:36Z",
+         "completed_at": "2026-11-07T04:34:08Z"
+        },
+        {
+         "id": 128301982984,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:32Z",
+         "completed_at": "2026-11-07T04:32:32Z"
+        },
+        {
+         "id": 128301983038,
+         "name": "tests / replay",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:32Z",
+         "started_at": "2026-11-07T04:32:32Z",
+         "completed_at": "2026-11-07T04:32:32Z"
+        },
+        {
+         "id": 128302014340,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:41Z",
+         "started_at": "2026-11-07T04:32:41Z",
+         "completed_at": "2026-11-07T04:32:41Z"
+        },
+        {
+         "id": 128302015252,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:41Z",
+         "started_at": "2026-11-07T04:32:41Z",
+         "completed_at": "2026-11-07T04:32:41Z"
+        },
+        {
+         "id": 128303864924,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:41:11Z",
+         "started_at": "2026-11-07T04:41:11Z",
+         "completed_at": "2026-11-07T04:41:10Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42338828285,
+     "title": "CI edit pr=3261 base=main sha=f984b1874c67bd865836c2a2658ee2c635677a3a",
+     "created_at": "2026-11-07T04:31:28Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:31:28Z",
+       "jobs": [
+        {
+         "id": 128301746878,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:29Z",
+         "started_at": "2026-11-07T04:31:31Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301747033,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:29Z",
+         "started_at": "2026-11-07T04:31:32Z",
+         "completed_at": "2026-11-07T04:32:08Z"
+        },
+        {
+         "id": 128301747102,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:31:29Z",
+         "started_at": "2026-11-07T04:31:32Z",
+         "completed_at": "2026-11-07T04:31:40Z"
+        },
+        {
+         "id": 128301865140,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:03Z",
+         "completed_at": "2026-11-07T04:33:05Z"
+        },
+        {
+         "id": 128301865176,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:03Z",
+         "completed_at": "2026-11-07T04:32:31Z"
+        },
+        {
+         "id": 128301866044,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301866141,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301866150,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301866372,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301866622,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128301866637,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:01Z",
+         "started_at": "2026-11-07T04:32:01Z",
+         "completed_at": "2026-11-07T04:32:01Z"
+        },
+        {
+         "id": 128302106991,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:33:05Z",
+         "started_at": "2026-11-07T04:33:11Z",
+         "completed_at": "2026-11-07T04:33:33Z"
+        },
+        {
+         "id": 128302108459,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:33:05Z",
+         "started_at": "2026-11-07T04:33:05Z",
+         "completed_at": "2026-11-07T04:33:05Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42338828285,
+     "attempt": 1,
+     "job": 128302106991,
+     "started_at": "2026-11-07T04:33:11Z",
+     "completed_at": "2026-11-07T04:33:33Z",
+     "conclusion": "failure",
+     "pin": "294a880dae608502b62055775e34a5db93217b98",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42338828950] at this head are still being judged; their gate decides"
+    }
+   ]
+  },
+  {
+   "name": "3241-c3",
+   "pr": "3241",
+   "head": "3720667a319cca90628a6b4167e3774408cb60a3",
+   "runs": [
+    {
+     "id": 42338898175,
+     "title": "CI edit pr=3241 base=main sha=ff348d154d2f639b2c69b38345c0029b999efac5",
+     "created_at": "2026-11-07T04:32:25Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:32:25Z",
+       "jobs": [
+        {
+         "id": 128301958941,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:26Z",
+         "started_at": "2026-11-07T04:32:28Z",
+         "completed_at": "2026-11-07T04:32:52Z"
+        },
+        {
+         "id": 128301959162,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:26Z",
+         "started_at": "2026-11-07T04:32:28Z",
+         "completed_at": "2026-11-07T04:32:36Z"
+        },
+        {
+         "id": 128301959189,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:26Z",
+         "started_at": "2026-11-07T04:32:28Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302080535,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:58Z",
+         "started_at": "2026-11-07T04:33:19Z",
+         "completed_at": "2026-11-07T04:34:19Z"
+        },
+        {
+         "id": 128302080552,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:58Z",
+         "started_at": "2026-11-07T04:33:21Z",
+         "completed_at": "2026-11-07T04:33:49Z"
+        },
+        {
+         "id": 128302081278,
+         "name": "codeql",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:58Z",
+         "started_at": "2026-11-07T04:32:58Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302081435,
+         "name": "governance",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:58Z",
+         "started_at": "2026-11-07T04:32:58Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302081464,
+         "name": "tests",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:58Z",
+         "started_at": "2026-11-07T04:32:58Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302081579,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:59Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302081594,
+         "name": "validate",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:59Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302081893,
+         "name": "hassfest",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:59Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128302387259,
+         "name": "gate",
+         "status": "completed",
+         "conclusion": "failure",
+         "created_at": "2026-11-07T04:34:20Z",
+         "started_at": "2026-11-07T04:34:22Z",
+         "completed_at": "2026-11-07T04:34:48Z"
+        },
+        {
+         "id": 128302387848,
+         "name": "pr-contract",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:34:20Z",
+         "started_at": "2026-11-07T04:34:20Z",
+         "completed_at": "2026-11-07T04:34:19Z"
+        }
+       ]
+      }
+     ]
+    },
+    {
+     "id": 42338897730,
+     "title": "CI code pr=3241 base=main sha=ff348d154d2f639b2c69b38345c0029b999efac5",
+     "created_at": "2026-11-07T04:32:24Z",
+     "attempts": [
+      {
+       "n": 1,
+       "run_started_at": "2026-11-07T04:32:24Z",
+       "jobs": [
+        {
+         "id": 128301957469,
+         "name": "refresh",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:25Z",
+         "started_at": "2026-11-07T04:32:27Z",
+         "completed_at": "2026-11-07T04:32:58Z"
+        },
+        {
+         "id": 128301957770,
+         "name": "cancel-superseded",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:25Z",
+         "started_at": "2026-11-07T04:32:28Z",
+         "completed_at": "2026-11-07T04:32:38Z"
+        },
+        {
+         "id": 128301957837,
+         "name": "prelude",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:25Z",
+         "started_at": "2026-11-07T04:32:28Z",
+         "completed_at": "2026-11-07T04:32:56Z"
+        },
+        {
+         "id": 128302074004,
+         "name": "codeql / Analyze (actions)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:00Z",
+         "completed_at": "2026-11-07T04:33:17Z"
+        },
+        {
+         "id": 128302074020,
+         "name": "validate / validate-hacs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:07Z",
+         "completed_at": "2026-11-07T04:33:46Z"
+        },
+        {
+         "id": 128302074023,
+         "name": "codeql / Analyze (javascript-typescript)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:33:19Z"
+        },
+        {
+         "id": 128302074027,
+         "name": "governance / instrument-self-tests",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": null
+        },
+        {
+         "id": 128302074043,
+         "name": "tests / briefs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:13Z",
+         "completed_at": "2026-11-07T04:33:59Z"
+        },
+        {
+         "id": 128302074050,
+         "name": "governance / env-matrix",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:39:30Z"
+        },
+        {
+         "id": 128302074052,
+         "name": "governance / policy-docs",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:34:24Z"
+        },
+        {
+         "id": 128302074072,
+         "name": "hassfest / hassfest",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:01Z",
+         "completed_at": "2026-11-07T04:33:24Z"
+        },
+        {
+         "id": 128302074082,
+         "name": "governance / wave-script",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:59Z",
+         "completed_at": "2026-11-07T04:33:51Z"
+        },
+        {
+         "id": 128302074089,
+         "name": "codeql / Analyze (python)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:00Z",
+         "completed_at": "2026-11-07T04:33:17Z"
+        },
+        {
+         "id": 128302074097,
+         "name": "tests / mutation",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:22Z",
+         "completed_at": "2026-11-07T04:34:08Z"
+        },
+        {
+         "id": 128302074098,
+         "name": "governance / delivery-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:00Z",
+         "completed_at": "2026-11-07T04:33:32Z"
+        },
+        {
+         "id": 128302074105,
+         "name": "budget-raise-gate / budget-raise-gate",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:19Z",
+         "completed_at": "2026-11-07T04:33:47Z"
+        },
+        {
+         "id": 128302074108,
+         "name": "tests / nightly-status",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:27Z",
+         "completed_at": "2026-11-07T04:33:38Z"
+        },
+        {
+         "id": 128302074140,
+         "name": "arch-score / arch-score",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:00Z",
+         "completed_at": "2026-11-07T04:33:49Z"
+        },
+        {
+         "id": 128302074221,
+         "name": "tests / closure-scope",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:33:34Z",
+         "completed_at": "2026-11-07T04:34:11Z"
+        },
+        {
+         "id": 128302074718,
+         "name": "kernel-points",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:57Z",
+         "completed_at": "2026-11-07T04:32:57Z"
+        },
+        {
+         "id": 128302075497,
+         "name": "governance / record",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:57Z",
+         "completed_at": "2026-11-07T04:32:57Z"
+        },
+        {
+         "id": 128302075848,
+         "name": "governance / delivery-status-publish",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:32:57Z",
+         "started_at": "2026-11-07T04:32:57Z",
+         "completed_at": "2026-11-07T04:32:57Z"
+        },
+        {
+         "id": 128302345554,
+         "name": "tests / mutation-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:34:08Z",
+         "started_at": "2026-11-07T04:34:08Z",
+         "completed_at": "2026-11-07T04:34:08Z"
+        },
+        {
+         "id": 128302345574,
+         "name": "tests / mutation-pins",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:34:08Z",
+         "started_at": "2026-11-07T04:34:08Z",
+         "completed_at": "2026-11-07T04:34:08Z"
+        },
+        {
+         "id": 128302358043,
+         "name": "tests / typing",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": "2026-11-07T04:35:26Z"
+        },
+        {
+         "id": 128302358049,
+         "name": "tests / browser",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": "2026-11-07T04:38:41Z"
+        },
+        {
+         "id": 128302358052,
+         "name": "tests / fast (3.14)",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": "2026-11-07T04:47:20Z"
+        },
+        {
+         "id": 128302358081,
+         "name": "tests / replay",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": null
+        },
+        {
+         "id": 128302358095,
+         "name": "tests / arch-instrument",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:15Z",
+         "completed_at": "2026-11-07T04:35:37Z"
+        },
+        {
+         "id": 128302358096,
+         "name": "tests / coverage",
+         "status": "in_progress",
+         "conclusion": null,
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": null
+        },
+        {
+         "id": 128302358142,
+         "name": "tests / closures",
+         "status": "completed",
+         "conclusion": "success",
+         "created_at": "2026-11-07T04:34:11Z",
+         "started_at": "2026-11-07T04:34:14Z",
+         "completed_at": "2026-11-07T04:47:51Z"
+        },
+        {
+         "id": 128302358798,
+         "name": "tests / nightly-ha",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:34:12Z",
+         "started_at": "2026-11-07T04:34:12Z",
+         "completed_at": "2026-11-07T04:34:11Z"
+        },
+        {
+         "id": 128305206354,
+         "name": "tests / claims-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:21Z",
+         "started_at": "2026-11-07T04:47:21Z",
+         "completed_at": "2026-11-07T04:47:20Z"
+        },
+        {
+         "id": 128305313739,
+         "name": "tests / closures-autofix",
+         "status": "completed",
+         "conclusion": "skipped",
+         "created_at": "2026-11-07T04:47:52Z",
+         "started_at": "2026-11-07T04:47:52Z",
+         "completed_at": "2026-11-07T04:47:51Z"
+        }
+       ]
+      }
+     ]
+    }
+   ],
+   "gates": [
+    {
+     "run": 42338898175,
+     "attempt": 1,
+     "job": 128302387259,
+     "started_at": "2026-11-07T04:34:22Z",
+     "completed_at": "2026-11-07T04:34:48Z",
+     "conclusion": "failure",
+     "pin": "294a880dae608502b62055775e34a5db93217b98",
+     "workset": "arch-score budget-raise-gate",
+     "verdict": "FAIL run(s) [42338897730] at this head are still being judged; their gate decides"
+    }
+   ]
+  }
+ ]
+}
diff --git a/dev/audit/harnesses/r10_rca_gate_busy_defer_2.py b/dev/audit/harnesses/r10_rca_gate_busy_defer_2.py
new file mode 100644
index 000000000..6bc797fa1
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_gate_busy_defer_2.py
@@ -0,0 +1,316 @@
+#!/usr/bin/env python3
+"""R10-RCA-GATE-BUSY-DEFER-2: replay recorded live run/job listings through a gate program.
+
+Root-cause seat harness (dev/audit/rca/r10-gate-busy-defer-2.md). The two harnesses #3246
+was proven with (r10_gate_defer_race.py, r10_ci_gate_core.py) build their run listings by
+hand and import ONE copy of tools/ci per scene. This one feeds the gate the listings GitHub
+actually served, reconstructed from recorded job timestamps, and names the program copy each
+live gate ran (its `programs restored from <sha>` line), so it can answer the question those
+harnesses could not ask: which program judged the red.
+
+Arms:
+  record OUT.json        read the scenes below from the GitHub API (gh api), write the fixture
+  replay --ci DIR        judge every scene's gates with DIR's gate.py; print one line per scene
+                         and exit 1 if a pair scene's gate defers to its partner (DEADLOCK: both
+                         do; HALF-DEFERRED: one does), the live #3241/#3246 defect
+  census --since ISO [--until ISO]
+                         live: every `gate` job started in the window on a ci.yml run, by
+                         whether its pinned programs carry the fix (--fix SHA; no pin line:
+                         unpinned), its verdict class, and whether it was a re-run attempt
+  pins                   per scene: the pinned sha each live gate ran, and whether that sha
+                         carries the #3246 fix (355d9965); needs the repository's history
+
+The fixture is dev/audit/harnesses/r10_rca_gate_busy_defer_2.json (default --fixture).
+A scene's snapshot at time T: a run is listed if created by T, under the attempt started
+latest by T; a job is listed if created by T, `completed` if it completed by T, `in_progress`
+if it started by T, else `queued`. The judging gates themselves are simulated, concurrently as
+they ran live (the harness refuses a pair whose gates did not overlap): each first reads beside
+its partner's gate `in_progress`; a gate that waited is re-judged with every partner that decided
+at once `completed` from that verdict's time.
+"""
+from __future__ import annotations
+
+import argparse
+import importlib
+import json
+import subprocess
+import sys
+from datetime import datetime, timedelta, timezone
+from pathlib import Path
+
+REPO = "tvofi/heatpump_optimizer"
+FIX = "355d9965a7a14ec45ef8cd25fb9c75c5ced044f1"        # #3246's merge
+FIXTURE = Path(__file__).with_suffix(".json")
+READ_AFTER_S = 20       # a gate's first read lands ~20 s after its job starts (#2754's edit gate: 21 s in all)
+MODULES = ("prelude", "gate", "ghapi", "codeql_scope", "sweep")
+# (scene, pr, head sha, [(run id, attempt) of each judging gate]); every gate here published red live.
+SCENES = [
+    ("3261-pair", "3261", "e17fadc1795ebbaaf0f01ed067fbb59aeba90dee", [(42307493684, 8), (42307798573, 8)]),
+    ("3265-pair", "3265", "c7c5cef52a49bed59ee4c8a42e495ef2dae30db5", [(42332777827, 4), (42333388705, 4)]),
+    ("3255-pair", "3255", "2ad28ecb50906877b34a378cacd8085e6afca029", [(42321825054, 5), (42322943199, 4)]),
+    ("3263-c3", "3263", "02e92e7cbcb95c32fbb2ad3a7a46a8d465a436d8", [(42338396358, 1)]),
+    ("3261-c3", "3261", "61187afe6cfdc4416f161e23111571bc50d25d9c", [(42338828285, 1)]),
+    ("3241-c3", "3241", "3720667a319cca90628a6b4167e3774408cb60a3", [(42338898175, 1)]),
+]
+
+
+def ts(s):
+    return None if not s else datetime.fromisoformat(s.replace("Z", "+00:00"))
+
+
+def iso(t):
+    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+
+
+# ---------------------------------------------------------------- record (live, gh api)
+def gh(path):
+    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
+    if p.returncode != 0:
+        raise SystemExit(f"gh api {path}: {p.stderr.strip()}")
+    return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else p.stdout
+
+
+def gate_log(job_id):
+    p = subprocess.run(["gh", "api", f"repos/{REPO}/actions/jobs/{job_id}/logs"], capture_output=True, text=True)
+    pin = workset = verdict = None
+    for line in p.stdout.splitlines():
+        line = line.split(" ", 1)[1] if line[:4].isdigit() and " " in line else line
+        if line.startswith("programs restored from "):
+            pin = line.split()[3]
+        elif line.strip().startswith("WORKSET:"):
+            workset = line.split(":", 1)[1].strip()
+        elif verdict is None and (line.startswith("FAIL") or line == "PASS"):
+            verdict = line
+    return {"pin": pin, "workset": workset, "verdict": verdict}
+
+
+def record(out):
+    doc = {"repo": REPO, "recorded_at": iso(datetime.now(timezone.utc)), "scenes": []}
+    for name, pr, head, gates in SCENES:
+        runs = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={head}&per_page=100")["workflow_runs"]
+        rec = []
+        for r in runs:
+            atts = []
+            for n in range(1, r["run_attempt"] + 1):
+                a = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}")
+                jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}/jobs?per_page=100")["jobs"]
+                atts.append({"n": n, "run_started_at": a["run_started_at"], "jobs": [
+                    {k: j[k] for k in ("id", "name", "status", "conclusion", "created_at", "started_at",
+                                       "completed_at")} for j in jobs]})
+            rec.append({"id": r["id"], "title": r["display_title"], "created_at": r["created_at"],
+                        "attempts": atts})
+        live = []
+        for rid, n in gates:
+            run = next(x for x in rec if x["id"] == rid)
+            g = next(j for j in run["attempts"][n - 1]["jobs"] if j["name"] == "gate")
+            live.append({"run": rid, "attempt": n, "job": g["id"], "started_at": g["started_at"],
+                         "completed_at": g["completed_at"], "conclusion": g["conclusion"], **gate_log(g["id"])})
+        doc["scenes"].append({"name": name, "pr": pr, "head": head, "runs": rec, "gates": live})
+    Path(out).write_text(json.dumps(doc, indent=1) + "\n")
+    print(f"recorded {len(doc['scenes'])} scenes to {out}")
+    return 0
+
+
+# ---------------------------------------------------------------- snapshot
+def snapshot(scene, t, sim):
+    """[{id, title, status, jobs: {name: (status, conclusion)}}] as listed at t. `sim` maps a
+    judging gate's run id to (finished_at or None, conclusion): its gate is simulated."""
+    out = []
+    for r in scene["runs"]:
+        if ts(r["created_at"]) > t:
+            continue
+        att = [a for a in r["attempts"] if ts(a["run_started_at"]) <= t]
+        if not att:
+            continue
+        jobs = {}
+        for j in att[-1]["jobs"]:
+            if ts(j["created_at"]) and ts(j["created_at"]) > t:
+                continue
+            if j["name"] == "gate" and r["id"] in sim:
+                fin, concl = sim[r["id"]]
+                jobs["gate"] = ("completed", concl) if fin is not None and fin <= t else ("in_progress", None)
+            elif ts(j["completed_at"]) and ts(j["completed_at"]) <= t and j["status"] == "completed":
+                jobs[j["name"]] = ("completed", j["conclusion"])
+            elif ts(j["started_at"]) and ts(j["started_at"]) <= t:
+                jobs[j["name"]] = ("in_progress", None)
+            else:
+                jobs[j["name"]] = ("queued", None)
+        status = "completed" if jobs and all(s == "completed" for s, _ in jobs.values()) else "in_progress"
+        out.append({"id": r["id"], "title": r["title"], "status": status, "jobs": jobs})
+    return out
+
+
+# ---------------------------------------------------------------- replay
+def load(ci):
+    for m in MODULES:
+        sys.modules.pop(m, None)
+    sys.path[:0] = [str(ci)]
+    try:
+        return importlib.import_module("gate")
+    finally:
+        sys.path.remove(str(ci))
+
+
+def judge_one(gate, scene, g, t0, sim):
+    """Run gate.judge for live gate g, its first read at t0; (outcome, verdict time, naps)."""
+    clock = {"t": t0, "naps": 0}
+    run = next(r for r in scene["runs"] if r["id"] == g["run"])
+    sha = run["title"].split("sha=")[1]
+
+    def get(path, params=None):
+        listing = snapshot(scene, clock["t"], sim)
+        if path.endswith(f"/pulls/{scene['pr']}"):
+            return 200, {}, {"head": {"sha": scene["head"], "repo": {"full_name": REPO}},
+                             "base": {"ref": "main"}, "state": "open"}
+        if path.endswith("/actions/workflows/ci.yml/runs"):
+            return 200, {}, {"workflow_runs": [{"id": r["id"], "display_title": r["title"], "status": r["status"]}
+                                               for r in listing]}
+        if "/actions/runs/" in path and path.endswith("/jobs"):
+            rid = int(path.split("/actions/runs/")[1].split("/")[0])
+            r = next((x for x in listing if x["id"] == rid), None)
+            jobs = dict(r["jobs"]) if r else {}
+            if rid == g["run"]:
+                jobs["gate"] = ("in_progress", None)        # this gate is the one judging
+            return 200, {}, {"jobs": [{"name": k, "status": s, "conclusion": c} for k, (s, c) in jobs.items()]}
+        return 404, {}, {"message": f"fixture serves no {path}"}
+
+    def sleep(s):
+        clock["t"] += timedelta(seconds=s)
+        clock["naps"] += 1
+
+    def now():
+        return (clock["t"] - t0).total_seconds()
+
+    ctx = gate.context("pull_request", {"action": "edited" if " edit " in run["title"] else "synchronize",
+                                         "pull_request": {"number": int(scene["pr"]), "base": {"ref": "main"},
+                                                          "head": {"sha": scene["head"]}}},
+                       {"GITHUB_SHA": sha, "GITHUB_REPOSITORY": REPO, "GITHUB_RUN_ID": str(g["run"]),
+                        "GITHUB_RUN_ATTEMPT": str(g["attempt"])})
+    kind = gate.parse_title(run["title"])[0]
+    claim = {"kind": kind, "pr": scene["pr"]}
+    if g.get("workset") is not None:
+        claim["workset"] = set(g["workset"].split())
+    outcome, _, _ = gate.judge(ctx, claim, get, reaches=lambda b, h: False, sleep=sleep, now=now)
+    return outcome, clock["t"], clock["naps"]
+
+
+def classify(scene, verdicts):
+    pair = {g["run"] for g in scene["gates"]}
+    deferred_to = {}
+    for rid, (out, _, _) in verdicts.items():
+        if "are still being judged" in out:
+            ids = {int(x) for x in out.split("[")[1].split("]")[0].split(",")}
+            deferred_to[rid] = ids
+    if len(pair) > 1:
+        if all(rid in deferred_to and deferred_to[rid] & (pair - {rid}) for rid in pair):
+            return "DEADLOCK"
+        if any(deferred_to.get(rid, set()) & (pair - {rid}) for rid in pair):
+            return "HALF-DEFERRED"
+        return "DECIDED"
+    (rid,) = pair
+    if rid in deferred_to:
+        others = deferred_to[rid]
+        codes = [r for r in scene["runs"] if r["id"] in others and " code " in r["title"]]
+        return "C3-AT-ONCE" if codes and verdicts[rid][2] == 0 else "DEFERRED"
+    return "DECIDED"
+
+
+def replay(fixture, ci):
+    gate = load(Path(ci).resolve())
+    doc = json.loads(Path(fixture).read_text())
+    rc = 0
+    for scene in doc["scenes"]:
+        gates = sorted(scene["gates"], key=lambda g: g["run"])
+        for g in gates:                                     # every judging gate's precondition: listed started
+            if ts(g["started_at"]) is None:
+                raise SystemExit(f"{scene['name']}: gate of run {g['run']} never started; fixture unusable")
+        for g in gates:                                     # the pair's gates overlapped live: both started
+            for o in gates:                                 # before the other's first read
+                if o is not g and not ts(o["started_at"]) <= ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S):
+                    raise SystemExit(f"{scene['name']}: gate {o['run']} had not started by {g['run']}'s read")
+        sim = {g["run"]: (None, None) for g in gates}       # pass 1: every partner's gate in_progress throughout
+        verdicts = {g["run"]: judge_one(gate, scene, g, ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S), sim)
+                    for g in gates}
+        if any(n for _, _, n in verdicts.values()):         # pass 2: a gate that waited sees each partner that
+            sim = {rid: ((fin, "success" if out == "PASS" else "failure") if n == 0 else (None, None))
+                   for rid, (out, fin, n) in verdicts.items()}   # decided at once finish when it did
+            verdicts = {g["run"]: (verdicts[g["run"]] if verdicts[g["run"]][2] == 0 else judge_one(
+                gate, scene, g, ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S), sim)) for g in gates}
+        cls = classify(scene, verdicts)
+        rc |= cls in ("DEADLOCK", "HALF-DEFERRED")
+        detail = "; ".join(f"{rid}: {out[:60]} naps={n}" for rid, (out, _, n) in sorted(verdicts.items()))
+        print(f"{scene['name']}: {cls} | {detail}")
+    print(f"RESULT replay ci={ci} deadlocks={'yes' if rc else 'no'}")
+    return rc
+
+
+def census(since, until, fix):
+    """Every gate verdict since `since`: pinned sha, carries `fix`?, conclusion, class, seconds."""
+    rows, page = [], 1
+    while True:
+        doc = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?per_page=100&page={page}")
+        runs = [r for r in doc["workflow_runs"] if r["updated_at"] >= since]
+        if not runs:
+            break
+        for r in runs:
+            for n in range(1, r["run_attempt"] + 1):
+                jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}/jobs?per_page=100")["jobs"]
+                for j in jobs:
+                    if j["name"] != "gate" or j["status"] != "completed" or not j["started_at"] \
+                            or not since <= j["started_at"] < until or j["run_attempt"] != n:
+                        continue
+                    lg = gate_log(j["id"])
+                    ok = bool(lg["pin"]) and subprocess.run(
+                        ["git", "merge-base", "--is-ancestor", fix, lg["pin"]]).returncode == 0
+                    v = lg["verdict"] or ""
+                    cls = "pass" if v == "PASS" else "defer" if "are still being judged" in v else \
+                        "other-red" if j["conclusion"] == "failure" else j["conclusion"]
+                    secs = (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds()
+                    rows.append((r["id"], n, r["display_title"].split()[2], "fixed" if ok else "stale" if lg["pin"] else "unpinned", cls, secs))
+        page += 1
+    for row in sorted(rows):
+        print("\t".join(map(str, row)))
+    for pin in ("stale", "fixed", "unpinned"):
+        sub = [x for x in rows if x[3] == pin]
+        by = {c: sum(1 for x in sub if x[4] == c) for c in sorted({x[4] for x in sub})}
+        print(f"CENSUS {pin}: gates={len(sub)} {by} prs={sorted({x[2] for x in sub if x[4] == 'defer'})} "
+              f"reruns={sum(1 for x in sub if x[1] > 1)} "
+              f"defer_job_s={int(sum(x[5] for x in sub if x[4] == 'defer'))}")
+    return 0
+
+
+def pins(fixture):
+    doc = json.loads(Path(fixture).read_text())
+    stale = 0
+    for scene in doc["scenes"]:
+        for g in scene["gates"]:
+            pin = g["pin"]
+            ok = pin and subprocess.run(["git", "merge-base", "--is-ancestor", FIX, pin]).returncode == 0
+            stale += not ok
+            print(f"{scene['name']} run {g['run']} attempt {g['attempt']}: pinned {pin[:10] if pin else None} "
+                  f"{'CARRIES' if ok else 'LACKS'} {FIX[:10]} | live: {g['verdict'][:70] if g['verdict'] else None}")
+    print(f"RESULT pins gates={sum(len(s['gates']) for s in doc['scenes'])} stale={stale}")
+    return 0
+
+
+def main(argv):
+    ap = argparse.ArgumentParser()
+    ap.add_argument("arm", choices=("record", "replay", "pins", "census"))
+    ap.add_argument("out", nargs="?")
+    ap.add_argument("--ci", default=str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
+    ap.add_argument("--fixture", default=str(FIXTURE))
+    ap.add_argument("--since", default="2026-11-07T03:45:14Z")    # 355d9965's merge
+    ap.add_argument("--until", default="9999")
+    ap.add_argument("--fix", default=FIX)
+    a = ap.parse_args(argv)
+    if a.arm == "record":
+        return record(a.out or a.fixture)
+    if a.arm == "census":
+        return census(a.since, a.until, a.fix)
+    if a.arm == "pins":
+        return pins(a.fixture)
+    return replay(a.fixture, a.ci)
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/rca/r10-gate-busy-defer-2.md b/dev/audit/rca/r10-gate-busy-defer-2.md
new file mode 100644
index 000000000..8ce2bf7b7
--- /dev/null
+++ b/dev/audit/rca/r10-gate-busy-defer-2.md
@@ -0,0 +1,302 @@
+# R10-RCA-GATE-BUSY-DEFER-2: a gate fix does not reach a run created before it merged
+
+Root-cause seat (`dev/governance/roles/root-cause.md`), run beside the fixer of
+R10-HOTFIX-GATE-BUSY-DEFER (topic r10-gate-busy-defer-2). Measured at origin/main
+`294a880da`, which carries #3246's merge `355d9965a`, on 2026-11-07. This seat
+changed nothing in `tools/ci/`. The live figures are for the window
+2026-11-07T03:45:14Z (#3246 merged) to 2026-11-07T04:50:21Z, and the harness prints
+them again for any window.
+
+## Result
+
+- **Cause.** `ci.yml` restores `tools/ci/*.py` from the event payload's
+  `pull_request.base.sha`. A re-run replays that payload. `refresh` (`gate.py`
+  `refresh()`) and `gate-sweep.yml` (`sweep.py`) re-judge a gate through the
+  job-rerun API, so each re-run of a run created before #3246 merged ran the
+  programs #3246 fixed. Every mutual deferral since the merge ran those programs.
+  The reported cause, "#3246's fix missed these shapes", is wrong. Replayed through
+  the fixed `gate.py`, the listings GitHub served decide every pair.
+- **#3263 is not the race.** Run 42338396358's 2-second red is C3's at-once
+  deferral, which is designed (`fa921fd59`; #3246 widened it). It ran the fixed
+  program, pinned `294a880da`. The pre-fix and the fixed program give the same
+  verdict on its recorded listing.
+- **Process state: (c).** The fixer's harnesses, the mutation proof and the
+  review's step 11 all ran and passed. Their unit is one copy of the gate program
+  per scene. The review read the live reds' `programs restored from <base>` lines
+  and dismissed them until "this fix lands". Landing the fix does not reach those
+  runs.
+- **Cost test: passes** for the countermeasure below, proposed and not built,
+  because it edits `tools/ci/`. It costs one tree compare per re-run. Against it,
+  21 red gates on 7 PRs in the first 65 minutes after the
+  merge, and 3 gate-program fixes merged on main in the 7 days before.
+- **Built.** `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` replays the real
+  run and job listings of both evidence pairs, and of one more pair, through a
+  chosen program copy. It is red at the three pinned bases the live gates ran
+  and green at the fix. Its `census` arm sorts every gate since a time into
+  pinned-stale and pinned-fixed.
+
+## 1. The cause, reproduced
+
+### What each live gate ran
+
+Every `gate` job prints `programs restored from <sha>` (ci.yml's prelude and gate
+steps, `PINNED: ${{ github.event.pull_request.base.sha || ... }}`). The `pins` arm
+reads that line from each recorded gate's log and asks whether the sha carries
+`355d9965a`:
+
+    python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins
+
+| scene | gate run, attempt | started (Z) | pinned | carries 355d9965? | live verdict |
+|---|---|---|---|---|---|
+| #3261 pair | 42307493684 #8 | 04:25:54 | 28482ece | no | FAIL, defers to 42307798573 |
+| #3261 pair | 42307798573 #8 | 04:25:45 | 28482ece | no | FAIL, defers to 42307493684 |
+| #3265 pair | 42332777827 #4 | 04:06:14 | f2a01514 | no | FAIL, defers to 42333388705 |
+| #3265 pair | 42333388705 #4 | 04:06:18 | f2a01514 | no | FAIL, defers to 42332777827 |
+| #3255 pair | 42321825054 #5 | 04:40:16 | 80016a71 | no | FAIL, defers to 42322943199 |
+| #3255 pair | 42322943199 #4 | 04:40:22 | 80016a71 | no | FAIL, defers to 42321825054 |
+| #3263 C3 | 42338396358 #1 | 04:27:28 | 294a880d | yes | FAIL, defers to code run 42338396871 |
+| #3261 C3 | 42338828285 #1 | 04:33:11 | 294a880d | yes | FAIL, defers to code run 42338828950 |
+| #3241 C3 | 42338898175 #1 | 04:34:22 | 294a880d | yes | FAIL, defers to code run 42338897730 |
+
+`RESULT pins gates=9 stale=6`. Each of the six mutual-deferral gates is a re-run
+attempt (#4, #5, #8) of a run created before 03:45:14Z. The original runs were
+created at 22:48Z and 22:51Z (#3261), 03:10Z and 03:18Z (#3265), and 01:02Z and
+01:14Z (#3255). `github-actions[bot]` triggered them through `refresh` and the
+sweep, according to the attempts API's `triggering_actor`. #3261's two runs reached
+attempt 10, all at `28482ece`, and attempts 4 to 6 and 8 to 10 each deadlocked the
+same way.
+
+### The same listings through each program
+
+The `replay` arm rebuilds each scene's run and job listing from the recorded job
+timestamps, at the gate's first read (job start + 20 s). It then calls
+`gate.judge()` from the program copy `--ci` names. The two gates of a pair overlap
+in time, as they did live, and the arm refuses a fixture where they do not.
+
+    for c in 28482ece f2a01514 80016a71 294a880d; do
+      git archive $c tools/ci tools/pr | tar -x -C $D/$c
+      python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci $D/$c/tools/ci; done
+    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay      # this tree's tools/ci
+
+| program | #3261 pair | #3265 pair | #3255 pair | three C3 scenes | rc |
+|---|---|---|---|---|---|
+| 28482ece (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
+| f2a01514 (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
+| 80016a71 (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
+| 294a880d (main, the fix) | DECIDED: PASS, PASS after 1 nap | DECIDED: PASS, PASS | DECIDED: PASS, PASS | C3-AT-ONCE, naps 0 | 0 |
+| this branch's tools/ci | as 294a880d | as 294a880d | as 294a880d | as 294a880d | 0 |
+
+In every pre-fix row, the replay gives the same deferral ids the live logs print.
+The fixed program decides all three pairs. The lower gate passes at once beside
+the higher's started gate. In #3261, the higher gate waits one poll, then passes.
+None of the six live reds would have happened if the re-run had executed main's
+`gate.py`.
+
+### #3263: the designed C3 red, under the fixed program
+
+Run 42338396358 is an edit run. Its prelude left `pr-contract` to code run
+42338396871 (`WORKSET: arch-score budget-raise-gate`). That code run's `gate` had
+not started. `judge()` sets the wait bound to 0
+(`deferring(...) and not all(started(r) ...)`) and publishes
+`FAIL run(s) [42338396871] ...` at once. The `gate.py` docstring states this case:
+"It publishes the deferral at once: that code run's gate is listed only after its
+pr-contract has read the latest body, so it is the later verdict here, and the
+sweep re-judges this one". The replay gives this verdict, with 0 naps, under all
+four programs. #3246's race harness counts it too: its `prelude` scenario reads
+UNDECIDED-RED 1, a designed deferral that the sweep converges to PASS. So the
+brief's first instance is not an escape of the race. The other two fixed-pin reds
+in the window, on #3261's new head and on #3241, have the same shape.
+
+The cost of this red is real. Until its code run's gate is listed, the PR carries a
+red `gate`. At the recording, the code run had been in progress for 29 minutes
+(`governance / instrument-self-tests`, `tests / fast (3.14)` and `tests / closures`
+were still running). That cost is C3 option A's design, decided in R10-CI-SLIM, and
+#3246 did not change it. This seat records it in section 3 and does not price it as
+this defect.
+
+## 2. Why the harnesses, the mutation proof and the review passed it
+
+- **`r10_gate_defer_race.py`** builds every scene by hand: `2754`, `2754-red`,
+  `editcode`, `pair`, `cascade`, `single` and `prelude`. `Head.__init__` puts one
+  `--ci` directory on `sys.path` and imports `prelude`, `gate`, `ghapi`,
+  `codeql_scope` and `sweep` from it. Every run in a scene is judged by the same
+  copy. No scene gives a run the program of its own base, so in the harness "the fix
+  is in `tools/ci`" means "every gate runs the fix".
+- **`r10_ci_gate_core.py`** compares the port against the design model (`replay`,
+  `sim`). It also mutates the single in-tree `gate.py`/`prelude.py`, one mutant at a
+  time (`mutants`, 23 rows, 0 survivors). The mutation proof answers "does a test
+  see the predicate move". It does not ask which copy of the predicate a live run
+  executes.
+- **The review** (`origin/verdict/3246`, verdict `merge 2a0d228c`) read the live
+  reds at the PR's own head. Attempt 2 of both edit runs printed
+  `programs restored from b36679ce...`, and the verdict concluded: "main's gate
+  cannot judge this mutual pair until this fix lands". The fixer's body gives the
+  same key: "a `gate` red reading `programs restored from <base>` with a mutual
+  `FAIL run(s)` deferral is the same pinned-main defect". Both name the signature
+  correctly. Both assume that landing the fix changes what such a run executes on
+  its next attempt, and it does not. A run's pin is its payload's `base.sha`, fixed
+  when the run is created. The fixer and the reviewer each saw this shape twice
+  before the merge (attempt 2 at 8af5fa58 pinned 5421413b, and at 2a0d228c pinned
+  b36679ce), because #3246's own PR's re-runs were pinned to pre-fix bases.
+
+## 3. Process state: (c)
+
+The process is `fixer.md` step 3 (the finder's harness at both ends), step 2 (the
+mutation proof), and `fix-review.md`'s reading of every red check. It existed, it
+was followed, and it measured correctly what it measures, which is the gate
+predicate in one program copy. It did not produce the intended result, "the red
+stops once this merges", because its unit leaves out where the program is
+deployed. The predicate is fixed at `main`. The executed copy is fixed per run, at
+the run's creation. The signature of the gap was read and recorded, and it was
+attributed to the defect itself.
+
+The other states were ruled out:
+
+- **Not (d).** The pin from the payload is not new. It dates from `85d13b859`
+  (2026-10-23, the CI umbrella), before #3246 and before the R10-GATE-DEFER design.
+  Nothing changed underneath the process.
+- **Not (b).** No rule asks a fixer of a pinned program whether the fix reaches runs
+  that are already open.
+- **Not (a).** The checks that would have shown it existed and ran: the fixer's
+  body and the review both read the `programs restored from` line.
+
+**Reach of the class.** Every program ci.yml restores from the base is in the
+class: `tools/ci/*.py`, `tools/pr/codeql_scope.py` and `tests/closure.py` (the
+prelude and gate restore), `tools/pr/cancel_superseded.py` and the `refresh`
+restore. A fix to any of them takes effect only for runs created after it merges.
+A re-run of an older run replays the old behaviour, and does so until
+`ATTEMPT_CAP` (45) or a new push. The class search
+(`git log --first-parent --since=<d> origin/main -- 'tools/ci/*.py' tools/pr/codeql_scope.py tests/closure.py tools/pr/cancel_superseded.py`)
+returns 27 first-parent commits since 2026-10-23 and 11 since 2026-10-31. Over
+`tools/ci/gate.py` and `tools/ci/prelude.py` alone, it returns 3 merges since
+2026-10-31, each a hotfix for a red `gate`: #3205 (R10-HOTFIX-GATE-STALE-JOBS),
+#3230 (R10-CI-SLIM) and #3246. A fix to a grader that a PR's `pr-contract` re-run
+reads has the same reach. `pr-contract.yml` already avoids the payload base for
+the main ref ("THE MAIN REF IS FETCHED, NOT THE PAYLOAD'S `base.sha`: a re-run
+replays the payload"), so the hazard is known in one workflow and not handled in
+the other.
+
+## 4. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+**The defect, measured once.** Census rule: every `gate` job that started in the
+window on a ci.yml run. A gate is pinned stale when its `programs restored from`
+sha lacks `355d9965a`, pinned fixed when it carries it, and unpinned when it has
+no such line (push runs, cancelled jobs). Command:
+
+    python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census \
+      --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z
+
+    CENSUS stale: gates=46 {'defer': 21, 'other-red': 1, 'pass': 24} prs=['pr=3232', 'pr=3241', 'pr=3255', 'pr=3261', 'pr=3265', 'pr=3271', 'pr=3273'] reruns=36 defer_job_s=685
+    CENSUS fixed: gates=3 {'defer': 3} prs=['pr=3241', 'pr=3261', 'pr=3263'] reruns=0 defer_job_s=81
+    CENSUS unpinned: gates=5 {'cancelled': 4, 'other-red': 1} prs=[] reruns=3 defer_job_s=0
+
+36 of the 46 stale gates were re-run attempts (attempt > 1).
+
+Within 65 minutes of the merge, the stale gates published 21 deferral
+reds on 7 PRs. The fixed gates published 3, all of them C3's
+designed at-once red, and no mutual deferral. Null control: had the fix not
+reached new runs either, the fixed row would hold mutual deferrals, and it holds
+none. Had the census called everything stale, the fixed row would be empty, and it
+holds three. Each stale mutual pair stays red until a new push creates a fresh run.
+For example, #3261 at `7871b3e3` was re-run to attempt 10 and was cleared only by
+its new head `f984b187` at 04:31Z. While a pair stays red, `merge_train.py
+classify` reads the head as `RED ... red: gate`, as the #3246 review's
+`classify_log.txt` recorded at that PR's head. This seat did not measure reviewer dispatches delayed: no API records
+them, and the bus log is not in this tree.
+
+**P(recurrence).** 3 merges to `gate.py`/`prelude.py` in the 7 days to 2026-11-07,
+each a gate hotfix merged while PRs had open runs (section 3), and 27 commits to
+pinned programs in 15 days. Every one of them leaves the open PRs' re-runs on the
+old copy.
+
+**The countermeasure's standing cost.** Before `refresh` or the sweep re-runs a
+`gate` job, they compare the run's pinned base (the sha its gate log's
+`programs restored from` line printed, which is the payload's `base.sha`) with the base tip, over the
+restored paths. One `git diff --quiet <pin> origin/<base> -- <paths>` in a full-history checkout
+took 0.0035 s here (`28482ece` against `294a880d`, rc 1, the trees differ; the same
+sha on both sides gives rc 0, the null). It is paid only on
+re-runs, not on every gate. When the trees differ, the re-run is replaced by a
+`workflow_dispatch` of ci.yml with `pr=N base=<base>`. ci.yml already pins that
+event to `origin/<base>` (its `INPUT_BASE` branch), and `gate()` already refuses a
+dispatch that does not name the open PR headed by its SHA. That costs one fresh run in place of a re-run of one job, about the
+code-run length once per open PR per pinned-program merge. A re-run that replays a
+fixed defect costs that run anyway, plus the red.
+
+Unit, per gate-program merge: under 0.01 s of compare per re-run, against the window's
+21 red gates on 7 PRs, each of which needs a fresh push or a
+manual dispatch to clear. **The test passes.**
+
+The harness costs nothing standing. It runs no gate and no CI lane. Its `replay`
+arm takes 0.08 s wall (`date +%s.%N` around it).
+
+## 5. Countermeasure
+
+### 5.1 Built: the real-listing replay, shown failing and passing
+
+`dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` and its fixture
+`r10_rca_gate_busy_defer_2.json` (sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70,
+recorded 2026-11-07T04:47:56Z by `record`). It addresses state (c)'s unit: it
+judges listings GitHub actually served, and it names the program copy.
+
+- **Red on the defect:** rc 1, DEADLOCK on all three pairs, at `28482ece`,
+  `f2a01514` and `80016a71`, the three bases the live gates ran.
+- **Green on the fix:** rc 0, DECIDED on all three pairs, at `294a880d` and at this
+  branch's `tools/ci`.
+- **Null controls:**
+  - The three C3 scenes read C3-AT-ONCE, with 0 naps, under every program, so the
+    arm does not count the designed red as the race.
+  - Mutant M17 (busy()'s tie-break deleted) on this tree's `gate.py` turns the arm
+    red: rc 1, with DEADLOCK on #3265 and #3255 and HALF-DEFERRED on #3261.
+  - Mutant M24 (`all` to `any`) survives the arm, rc 0. None of the recorded scenes
+    is the mixed prelude/gate scene that M24 opens, and `gate.py --self-test`'s
+    named case pins it. The arm does not replace the self-test.
+  - The arm refuses, and does not go green, on a fixture whose pair gates did not
+    overlap, and on a gate that never started.
+
+It can run against any proposed `gate.py` (`--ci`), and a fix to the gate can be
+re-proven on real listings before it merges.
+
+### 5.2 Proposed, not built: re-judge a stale-pinned gate with a fresh run
+
+This change is in `tools/ci/` (`gate.py` `refresh()` and `sweep.py`), and this seat
+may not edit `tools/ci/gate.py`. Its owner is the gate's fixer and the orchestrator.
+
+> Before a job re-run, compare the run's pinned base with the base tip over the
+> restored paths. If they differ, dispatch ci.yml with `pr=N base=<base>` instead,
+> and print `STALE-PIN <pin>: re-judged by a fresh run`.
+
+The detector for this change is the `census` arm. After a pinned-program merge, it
+shows stale reds that the next re-run cycle still leaves. With the change, a stale
+pin is never re-run, so the stale row's `reruns` count drops to 0 after the merge.
+
+### 5.3 Until then, the operational step
+
+After merging a change to a pinned program, dispatch ci.yml
+(`workflow_dispatch`, `pr=N`, `base=main`) for each open PR whose latest gate is
+red with a `programs restored from` sha that lacks the merge. The census arm lists
+them. A re-run of the old run does not clear them.
+
+### Refused
+
+- **Re-running harder, or raising `ATTEMPT_CAP`.** Every attempt replays the same
+  copy. #3261 reached attempt 10 with nothing changed.
+- **Pinning to `origin/<base>` at job time instead of the payload's `base.sha`.**
+  That would make every grader judge with a base newer than the one the PR was
+  checked against, which is the stamp trap `pr-contract.yml` documents. It would
+  also let a merge to main change a verdict mid-run. A fresh dispatched run keeps
+  one base per run.
+- **A self-test case for "the fix reaches old runs".** That property is the
+  workflow's, not `gate.py`'s. No in-process test of `gate.py` can see it.
+
+## Carries
+
+- To the R10-HOTFIX-GATE-BUSY-DEFER fixer (topic r10-gate-busy-defer-2) and the
+  orchestrator: #3263's red is the designed C3 at-once deferral under the fixed
+  program, not the race. Another change to busy() or judge() cannot remove the six
+  stale reds, because they never ran busy() as it stands on main. Re-prove any
+  gate change with `replay --ci <export>`.
+- To the orchestrator, now: #3265 and #3255 at their recorded heads, and any other
+  PR the census lists as stale-red, need a fresh dispatched run (5.3), not a
+  re-run.
diff --git a/dev/programme/delivery/3278.md b/dev/programme/delivery/3278.md
new file mode 100644
index 000000000..115d6977b
--- /dev/null
+++ b/dev/programme/delivery/3278.md
@@ -0,0 +1 @@
+- [#3278](https://github.com/tvofi/heatpump_optimizer/pull/3278) — **open**, R10-RCA-GATE-BUSY-DEFER-2: rca gate busy defer 2 (R10-RCA-GATE-BUSY-DEFER-2)
diff --git a/tests/closures.json b/tests/closures.json
index 2139c2396..bad7daabf 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4080,6 +4080,7 @@
    "dev/audit/harnesses/r10_raise_paths.sh",
    "dev/audit/harnesses/r10_ratio_anchor.py",
    "dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py",
+   "dev/audit/harnesses/r10_rca_gate_busy_defer_2.py",
    "dev/audit/harnesses/r10_rca_name_kept_plant.py",
    "dev/audit/harnesses/r10_rca_sav_estimate.py",
    "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
