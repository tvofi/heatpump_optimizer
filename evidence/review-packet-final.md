# Review packet #3353
head: 51f5ce37e1ebdb5643566b0c9a062b7678ada6d2
base: 425b858495432c8dceb89d8d13866550352ba54f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128902825883 success
arch-score / arch-score id=128902921683 success
arm id=128902277452 skipped
budget-raise-gate / budget-raise-gate id=128902921843 success
cancel-superseded id=128902280429 success
codeql id=128902923416 skipped
codeql / Analyze (actions) id=128902593507 success
codeql / Analyze (javascript-typescript) id=128902593553 success
codeql / Analyze (python) id=128902593465 success
gate id=128915854140 failure
governance id=128902923227 skipped
governance / delivery-status id=128902593508 success
governance / delivery-status-publish id=128902594734 skipped
governance / env-matrix id=128902593485 success
governance / instrument-self-tests id=128902593488 failure
governance / policy-docs id=128902593549 success
governance / record id=128902595097 skipped
governance / wave-script id=128902593480 success
hassfest id=128902923406 skipped
hassfest / hassfest id=128902593502 success
kernel-points id=128902923495 skipped
pr-contract id=128903750001 skipped
pr-contract / pr-contract id=128914068083 failure
prelude id=128902280339 success
refresh id=128902280107 success
tests id=128902922761 skipped
tests / arch-instrument id=128903395486 success
tests / briefs id=128902593423 success
tests / browser id=128903395418 success
tests / ci-ratchet id=128914069282 skipped
tests / claims-autofix id=128907340688 skipped
tests / closure-scope id=128902593520 success
tests / closures id=128903395425 success
tests / closures-autofix id=128914069287 skipped
tests / coverage id=128903395470 success
tests / coverage-ratchet id=128909266429 success
tests / fast (3.14) id=128903395467 success
tests / graders-head-copy id=128909266431 success
tests / lane-proofs id=128909266448 success
tests / mutation id=128902593439 success
tests / mutation-autofix id=128903174348 skipped
tests / mutation-pins id=128903173729 skipped
tests / nightly-ha id=128903396231 skipped
tests / nightly-status id=128902593486 success
tests / replay id=128903396736 skipped
tests / typing id=128903395454 success
validate id=128902923253 skipped
validate / validate-hacs id=128902593511 success

## Refusals
red-unanswered: concluded red check `governance / instrument-self-tests` is not named in ## Red checks
red-unanswered: concluded red check `pr-contract / pr-contract` is not named in ## Red checks
required-red: required context `gate` concluded failure at 51f5ce37e1ebdb5643566b0c9a062b7678ada6d2

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay
             `dev/audit/harnesses/r10_rca_gate_busy_defer_4.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since 2026-11-07T19:14:31Z --until 2026-11-07T21:30:00Z
             `dev/audit/harnesses/r10_gate_busy_defer_3.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index c26280724..ef205e63d 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -4777,6 +4777,26 @@
         "dev/audit/rca/R10-RCA-COP-UNMEASURED.md",
         "dev/audit/harnesses/r10_rca_cop_unmeasured.py"
       ]
+    },
+    "R10-RCA-GATE-BUSY-DEFER-4": {
+      "class": null,
+      "level": "instance-or-process",
+      "subject": "the merge train skipped #3293 (fefaa492), #3267 (cc6ee11f) and #3268 (64fe84b2) on `ci: red at the head: gate` while each head's code run was still in progress: gate.py publishes an edit run's deferral as a failed `gate` at once (fa921fd59, 2026-11-05; the wait cc100c275 restored for 8 h; published at once again by #3287, 52f9fc5b3), and merge_train.py classify, which reads a check run's conclusion alone and has done so since 9262e6f43 (2026-10-22), cannot tell a deferral from a verdict. 14 deferral gates on 14 heads in the 2 h 16 min after #3287 merged; the producer moved three times, the reader never",
+      "trigger": "2 (red required check: gate), third instance of the deferral-red class (#3246, #3278, this)",
+      "date": "2026-11-07",
+      "status": "proposed",
+      "parts_missing": [
+        "the classifier wait (tools/audit/seat/merge_train.py, PR #3290, unmerged, not this seat's)",
+        "the settle gap between the code run's green and gate-sweep's re-run of the edit gate",
+        "the readers outside classify: merge_pr.sh, merge_train.py policy_refusal, review_packet.py gate_digest, ci-watch.sh, orchestrator_tick.py one_pr"
+      ],
+      "process_state": "(c) #3287's replay and race harnesses and its review ran and passed; their unit is gate.py judge() and sweep over recorded listings, the producer. The review ran merge_train.py classify, read RED on a deferral at 16:55Z and waited, and the verdict records that as evidence; the same signature was attributed to the defect being fixed, as in #3278's RCA. No harness had a consumer of the published conclusion in its unit",
+      "countermeasure": "built: dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay of the three evidence heads' recorded listings through a chosen merge_train.py (defects=3 at origin/main dee8b413, 0 at #3290 a38bd141, 3 again with #3290's busy wait mutated out); proposed, not built: the readers outside classify read one shared deferral predicate, and the settle gap needs a wait keyed on the sweep, not a poll count",
+      "landed": null,
+      "in_tree_home": "dev/audit/rca/r10-gate-busy-defer-4.md",
+      "doc": [
+        "dev/audit/rca/r10-gate-busy-defer-4.md"
+      ]
     }
   },
   "N-registry-leak": {
diff --git a/dev/audit/harnesses/r10_rca_gate_busy_defer_4.json b/dev/audit/harnesses/r10_rca_gate_busy_defer_4.json
new file mode 100644
index 000000000..9c9a6a418
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_gate_busy_defer_4.json
@@ -0,0 +1,1650 @@
+{
+ "3267": {
+  "check_runs": [
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:14:28Z",
+    "conclusion": "skipped",
+    "id": 128530763762,
+    "name": "tests / claims-autofix",
+    "started_at": "2026-11-07T21:14:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:33Z",
+    "conclusion": "skipped",
+    "id": 128527011029,
+    "name": "tests / mutation-pins",
+    "started_at": "2026-11-07T20:59:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:33Z",
+    "conclusion": "skipped",
+    "id": 128527010998,
+    "name": "tests / mutation-autofix",
+    "started_at": "2026-11-07T20:59:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:59:21Z",
+    "conclusion": "skipped",
+    "id": 128526965563,
+    "name": "pr-contract",
+    "started_at": "2026-11-07T20:59:22Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T21:00:29Z",
+    "conclusion": "failure",
+    "id": 128526964506,
+    "name": "gate",
+    "started_at": "2026-11-07T21:00:01Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114905492022
+    },
+    "completed_at": "2026-11-07T20:59:09Z",
+    "conclusion": "neutral",
+    "id": 128526899084,
+    "name": "CodeQL",
+    "started_at": "2026-11-07T20:59:06Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:02Z",
+    "conclusion": "skipped",
+    "id": 128526884861,
+    "name": "tests / replay",
+    "started_at": "2026-11-07T20:59:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:02Z",
+    "conclusion": "skipped",
+    "id": 128526884714,
+    "name": "tests / nightly-ha",
+    "started_at": "2026-11-07T20:59:02Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:14:28Z",
+    "conclusion": "success",
+    "id": 128526884000,
+    "name": "tests / fast (3.14)",
+    "started_at": "2026-11-07T21:00:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526883982,
+    "name": "tests / coverage",
+    "started_at": "2026-11-07T21:00:37Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:02:18Z",
+    "conclusion": "success",
+    "id": 128526883951,
+    "name": "tests / typing",
+    "started_at": "2026-11-07T21:01:06Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:04:31Z",
+    "conclusion": "success",
+    "id": 128526883910,
+    "name": "tests / browser",
+    "started_at": "2026-11-07T21:00:02Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:01:18Z",
+    "conclusion": "success",
+    "id": 128526883831,
+    "name": "tests / arch-instrument",
+    "started_at": "2026-11-07T20:59:53Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526883825,
+    "name": "tests / closures",
+    "started_at": "2026-11-07T20:59:37Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:04Z",
+    "conclusion": "skipped",
+    "id": 128526414614,
+    "name": "governance / record",
+    "started_at": "2026-11-07T20:57:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:04Z",
+    "conclusion": "skipped",
+    "id": 128526414098,
+    "name": "governance / delivery-status-publish",
+    "started_at": "2026-11-07T20:57:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:04Z",
+    "conclusion": "skipped",
+    "id": 128526413701,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T20:57:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:00:14Z",
+    "conclusion": "success",
+    "id": 128526412863,
+    "name": "tests / briefs",
+    "started_at": "2026-11-07T20:59:17Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:50Z",
+    "conclusion": "success",
+    "id": 128526412840,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T20:59:24Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526412819,
+    "name": "governance / instrument-self-tests",
+    "started_at": "2026-11-07T20:59:14Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526412817,
+    "name": "codeql / Analyze (python)",
+    "started_at": "2026-11-07T20:58:59Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:00:06Z",
+    "conclusion": "success",
+    "id": 128526412806,
+    "name": "governance / wave-script",
+    "started_at": "2026-11-07T20:59:06Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:35Z",
+    "conclusion": "success",
+    "id": 128526412793,
+    "name": "governance / delivery-status",
+    "started_at": "2026-11-07T20:59:04Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:02Z",
+    "conclusion": "success",
+    "id": 128526412789,
+    "name": "tests / closure-scope",
+    "started_at": "2026-11-07T20:58:36Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:00:35Z",
+    "conclusion": "success",
+    "id": 128526412780,
+    "name": "governance / policy-docs",
+    "started_at": "2026-11-07T20:57:14Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:15Z",
+    "conclusion": "success",
+    "id": 128526412766,
+    "name": "codeql / Analyze (javascript-typescript)",
+    "started_at": "2026-11-07T20:58:00Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:42Z",
+    "conclusion": "success",
+    "id": 128526412765,
+    "name": "codeql / Analyze (actions)",
+    "started_at": "2026-11-07T20:58:46Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:58:55Z",
+    "conclusion": "success",
+    "id": 128526412754,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T20:58:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:32Z",
+    "conclusion": "success",
+    "id": 128526412752,
+    "name": "tests / mutation",
+    "started_at": "2026-11-07T20:58:49Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T21:02:59Z",
+    "conclusion": "success",
+    "id": 128526412726,
+    "name": "governance / env-matrix",
+    "started_at": "2026-11-07T20:57:09Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:58:34Z",
+    "conclusion": "success",
+    "id": 128526412706,
+    "name": "tests / nightly-status",
+    "started_at": "2026-11-07T20:58:24Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:59:37Z",
+    "conclusion": "success",
+    "id": 128526412660,
+    "name": "validate / validate-hacs",
+    "started_at": "2026-11-07T20:58:58Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:45Z",
+    "conclusion": "success",
+    "id": 128526412652,
+    "name": "hassfest / hassfest",
+    "started_at": "2026-11-07T20:57:25Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526289214,
+    "name": "codeql",
+    "started_at": "2026-11-07T20:56:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526289001,
+    "name": "validate",
+    "started_at": "2026-11-07T20:56:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526288882,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T20:56:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526288381,
+    "name": "governance",
+    "started_at": "2026-11-07T20:56:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526288325,
+    "name": "hassfest",
+    "started_at": "2026-11-07T20:56:32Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "skipped",
+    "id": 128526288320,
+    "name": "tests",
+    "started_at": "2026-11-07T20:56:32Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:59:21Z",
+    "conclusion": "success",
+    "id": 128526287699,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T20:58:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:59:11Z",
+    "conclusion": "success",
+    "id": 128526287687,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T20:58:44Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:56:52Z",
+    "conclusion": "success",
+    "id": 128525990244,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T20:56:42Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:23Z",
+    "conclusion": "success",
+    "id": 128525990211,
+    "name": "refresh",
+    "started_at": "2026-11-07T20:56:47Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904749769
+    },
+    "completed_at": "2026-11-07T20:57:04Z",
+    "conclusion": "success",
+    "id": 128525990063,
+    "name": "prelude",
+    "started_at": "2026-11-07T20:56:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:32Z",
+    "conclusion": "success",
+    "id": 128525989536,
+    "name": "prelude",
+    "started_at": "2026-11-07T20:56:00Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:24Z",
+    "conclusion": "success",
+    "id": 128525989502,
+    "name": "refresh",
+    "started_at": "2026-11-07T20:55:47Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904748991
+    },
+    "completed_at": "2026-11-07T20:56:26Z",
+    "conclusion": "success",
+    "id": 128525989415,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T20:56:17Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904744406
+    },
+    "completed_at": "2026-11-07T20:55:15Z",
+    "conclusion": "skipped",
+    "id": 128525985094,
+    "name": "arm",
+    "started_at": "2026-11-07T20:55:15Z",
+    "status": "completed"
+   }
+  ],
+  "head": "cc6ee11ff27b8b57cd7e017121544dca9dbe6e30",
+  "runs": [
+   {
+    "check_suite_id": 114904748991,
+    "conclusion": "failure",
+    "created_at": "2026-11-07T20:55:15Z",
+    "display_title": "CI edit pr=3267 base=main sha=7907726524a6e1c91b31699e03de6d5751f3f170",
+    "id": 42413349169,
+    "status": "completed",
+    "updated_at": "2026-11-07T21:00:29Z"
+   },
+   {
+    "check_suite_id": 114904749769,
+    "conclusion": null,
+    "created_at": "2026-11-07T20:55:15Z",
+    "display_title": "CI code pr=3267 base=main sha=7907726524a6e1c91b31699e03de6d5751f3f170",
+    "id": 42413349469,
+    "status": "in_progress",
+    "updated_at": "2026-11-07T21:01:07Z"
+   }
+  ]
+ },
+ "3268": {
+  "check_runs": [
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:21:29Z",
+    "conclusion": "skipped",
+    "id": 128532483245,
+    "name": "tests / claims-autofix",
+    "started_at": "2026-11-07T21:21:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:59:03Z",
+    "conclusion": "skipped",
+    "id": 128526889844,
+    "name": "pr-contract",
+    "started_at": "2026-11-07T20:59:04Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T21:00:17Z",
+    "conclusion": "failure",
+    "id": 128526888792,
+    "name": "gate",
+    "started_at": "2026-11-07T20:59:40Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114905146876
+    },
+    "completed_at": "2026-11-07T20:57:20Z",
+    "conclusion": "neutral",
+    "id": 128526466013,
+    "name": "CodeQL",
+    "started_at": "2026-11-07T20:57:18Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:12Z",
+    "conclusion": "skipped",
+    "id": 128526445758,
+    "name": "tests / nightly-ha",
+    "started_at": "2026-11-07T20:57:13Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:04:59Z",
+    "conclusion": "success",
+    "id": 128526444565,
+    "name": "tests / browser",
+    "started_at": "2026-11-07T21:00:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:01:39Z",
+    "conclusion": "success",
+    "id": 128526444564,
+    "name": "tests / typing",
+    "started_at": "2026-11-07T21:00:16Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526444563,
+    "name": "tests / coverage",
+    "started_at": "2026-11-07T21:00:22Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526444562,
+    "name": "tests / closures",
+    "started_at": "2026-11-07T21:00:29Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:11:19Z",
+    "conclusion": "success",
+    "id": 128526444542,
+    "name": "tests / replay",
+    "started_at": "2026-11-07T21:00:10Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:02:01Z",
+    "conclusion": "success",
+    "id": 128526444465,
+    "name": "tests / arch-instrument",
+    "started_at": "2026-11-07T21:00:09Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:21:28Z",
+    "conclusion": "success",
+    "id": 128526444441,
+    "name": "tests / fast (3.14)",
+    "started_at": "2026-11-07T20:59:45Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526406281,
+    "name": "governance",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526405768,
+    "name": "validate",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526405676,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526405518,
+    "name": "hassfest",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526405484,
+    "name": "codeql",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "skipped",
+    "id": 128526405386,
+    "name": "tests",
+    "started_at": "2026-11-07T20:57:03Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:59:03Z",
+    "conclusion": "success",
+    "id": 128526404565,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T20:57:49Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:58:29Z",
+    "conclusion": "success",
+    "id": 128526404482,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T20:57:59Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:28Z",
+    "conclusion": "skipped",
+    "id": 128526274515,
+    "name": "governance / record",
+    "started_at": "2026-11-07T20:56:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:28Z",
+    "conclusion": "skipped",
+    "id": 128526274497,
+    "name": "governance / delivery-status-publish",
+    "started_at": "2026-11-07T20:56:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:28Z",
+    "conclusion": "skipped",
+    "id": 128526274412,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T20:56:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:01:16Z",
+    "conclusion": "success",
+    "id": 128526273493,
+    "name": "governance / policy-docs",
+    "started_at": "2026-11-07T20:58:00Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:27Z",
+    "conclusion": "success",
+    "id": 128526273477,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T20:56:55Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:00:08Z",
+    "conclusion": "success",
+    "id": 128526273453,
+    "name": "tests / briefs",
+    "started_at": "2026-11-07T20:58:56Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:02:54Z",
+    "conclusion": "success",
+    "id": 128526273430,
+    "name": "governance / env-matrix",
+    "started_at": "2026-11-07T20:57:30Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:27Z",
+    "conclusion": "success",
+    "id": 128526273357,
+    "name": "codeql / Analyze (actions)",
+    "started_at": "2026-11-07T20:56:38Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:58:02Z",
+    "conclusion": "success",
+    "id": 128526273346,
+    "name": "governance / delivery-status",
+    "started_at": "2026-11-07T20:57:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:58:11Z",
+    "conclusion": "success",
+    "id": 128526273341,
+    "name": "codeql / Analyze (javascript-typescript)",
+    "started_at": "2026-11-07T20:56:49Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T21:22:57Z",
+    "conclusion": "success",
+    "id": 128526273339,
+    "name": "governance / instrument-self-tests",
+    "started_at": "2026-11-07T20:57:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:57Z",
+    "conclusion": "success",
+    "id": 128526273336,
+    "name": "governance / wave-script",
+    "started_at": "2026-11-07T20:57:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:58:44Z",
+    "conclusion": "success",
+    "id": 128526273298,
+    "name": "tests / nightly-status",
+    "started_at": "2026-11-07T20:58:32Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526273289,
+    "name": "codeql / Analyze (python)",
+    "started_at": "2026-11-07T20:56:34Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:58:47Z",
+    "conclusion": "success",
+    "id": 128526273277,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T20:57:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:12Z",
+    "conclusion": "success",
+    "id": 128526273270,
+    "name": "tests / closure-scope",
+    "started_at": "2026-11-07T20:56:43Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128526273264,
+    "name": "tests / mutation",
+    "started_at": "2026-11-07T20:58:16Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:57:08Z",
+    "conclusion": "success",
+    "id": 128526273255,
+    "name": "hassfest / hassfest",
+    "started_at": "2026-11-07T20:56:46Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:58:03Z",
+    "conclusion": "success",
+    "id": 128526273180,
+    "name": "validate / validate-hacs",
+    "started_at": "2026-11-07T20:57:25Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904850887
+    },
+    "completed_at": "2026-11-07T20:55:48Z",
+    "conclusion": "skipped",
+    "id": 128526145308,
+    "name": "arm",
+    "started_at": "2026-11-07T20:55:56Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:37Z",
+    "conclusion": "success",
+    "id": 128526115577,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T20:56:29Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:57:02Z",
+    "conclusion": "success",
+    "id": 128526115563,
+    "name": "prelude",
+    "started_at": "2026-11-07T20:56:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:56:35Z",
+    "conclusion": "success",
+    "id": 128526115548,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T20:56:27Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:40Z",
+    "conclusion": "success",
+    "id": 128526115517,
+    "name": "refresh",
+    "started_at": "2026-11-07T20:56:14Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852864
+    },
+    "completed_at": "2026-11-07T20:56:47Z",
+    "conclusion": "success",
+    "id": 128526115378,
+    "name": "refresh",
+    "started_at": "2026-11-07T20:56:14Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114904852828
+    },
+    "completed_at": "2026-11-07T20:56:28Z",
+    "conclusion": "success",
+    "id": 128526115347,
+    "name": "prelude",
+    "started_at": "2026-11-07T20:56:07Z",
+    "status": "completed"
+   }
+  ],
+  "head": "64fe84b24efb6e4f720e011b75b559b6a3bac7e9",
+  "runs": [
+   {
+    "check_suite_id": 114904852864,
+    "conclusion": "failure",
+    "created_at": "2026-11-07T20:55:48Z",
+    "display_title": "CI edit pr=3268 base=main sha=d1bc47acf1bef87803e0e1cb0def198c2ec851f1",
+    "id": 42413389204,
+    "status": "completed",
+    "updated_at": "2026-11-07T21:00:17Z"
+   },
+   {
+    "check_suite_id": 114904852828,
+    "conclusion": null,
+    "created_at": "2026-11-07T20:55:48Z",
+    "display_title": "CI code pr=3268 base=main sha=d1bc47acf1bef87803e0e1cb0def198c2ec851f1",
+    "id": 42413389218,
+    "status": "in_progress",
+    "updated_at": "2026-11-07T21:00:29Z"
+   }
+  ]
+ },
+ "3293": {
+  "check_runs": [
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:23:35Z",
+    "conclusion": "skipped",
+    "id": 128533000077,
+    "name": "tests / closures-autofix",
+    "started_at": "2026-11-07T21:23:35Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:11:12Z",
+    "conclusion": "skipped",
+    "id": 128529965671,
+    "name": "tests / claims-autofix",
+    "started_at": "2026-11-07T21:11:12Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:07:15Z",
+    "conclusion": "skipped",
+    "id": 128528992344,
+    "name": "pr-contract",
+    "started_at": "2026-11-07T21:07:15Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:07:57Z",
+    "conclusion": "failure",
+    "id": 128528991330,
+    "name": "gate",
+    "started_at": "2026-11-07T21:07:26Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:24Z",
+    "conclusion": "skipped",
+    "id": 128528777764,
+    "name": "tests / mutation-autofix",
+    "started_at": "2026-11-07T21:06:24Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:23Z",
+    "conclusion": "skipped",
+    "id": 128528777247,
+    "name": "tests / mutation-pins",
+    "started_at": "2026-11-07T21:06:24Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:08Z",
+    "conclusion": "skipped",
+    "id": 128528716379,
+    "name": "tests / replay",
+    "started_at": "2026-11-07T21:06:09Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:08Z",
+    "conclusion": "skipped",
+    "id": 128528716290,
+    "name": "tests / nightly-ha",
+    "started_at": "2026-11-07T21:06:08Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:23:35Z",
+    "conclusion": "success",
+    "id": 128528714784,
+    "name": "tests / closures",
+    "started_at": "2026-11-07T21:07:17Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128528714759,
+    "name": "tests / coverage",
+    "started_at": "2026-11-07T21:07:09Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:11:44Z",
+    "conclusion": "success",
+    "id": 128528714739,
+    "name": "tests / browser",
+    "started_at": "2026-11-07T21:07:05Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:07:51Z",
+    "conclusion": "success",
+    "id": 128528714685,
+    "name": "tests / arch-instrument",
+    "started_at": "2026-11-07T21:06:57Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:07:53Z",
+    "conclusion": "success",
+    "id": 128528714680,
+    "name": "tests / typing",
+    "started_at": "2026-11-07T21:06:49Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:11:12Z",
+    "conclusion": "success",
+    "id": 128528714673,
+    "name": "tests / fast (3.14)",
+    "started_at": "2026-11-07T21:06:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906908359
+    },
+    "completed_at": "2026-11-07T21:05:52Z",
+    "conclusion": "success",
+    "id": 128528634650,
+    "name": "CodeQL",
+    "started_at": "2026-11-07T21:05:49Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528559600,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528559330,
+    "name": "hassfest",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528559288,
+    "name": "validate",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528559176,
+    "name": "tests",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528559169,
+    "name": "codeql",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528558912,
+    "name": "governance",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:07:02Z",
+    "conclusion": "success",
+    "id": 128528558041,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T21:06:09Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:07:15Z",
+    "conclusion": "success",
+    "id": 128528558025,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T21:06:46Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528557829,
+    "name": "governance / record",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528557688,
+    "name": "governance / delivery-status-publish",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "skipped",
+    "id": 128528557674,
+    "name": "kernel-points",
+    "started_at": "2026-11-07T21:05:31Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:44Z",
+    "conclusion": "success",
+    "id": 128528556655,
+    "name": "tests / nightly-status",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:07:07Z",
+    "conclusion": "success",
+    "id": 128528556582,
+    "name": "governance / wave-script",
+    "started_at": "2026-11-07T21:06:25Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:13Z",
+    "conclusion": "success",
+    "id": 128528556575,
+    "name": "validate / validate-hacs",
+    "started_at": "2026-11-07T21:05:37Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:23Z",
+    "conclusion": "success",
+    "id": 128528556571,
+    "name": "arch-score / arch-score",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:13:25Z",
+    "conclusion": "success",
+    "id": 128528556560,
+    "name": "governance / env-matrix",
+    "started_at": "2026-11-07T21:06:25Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:46Z",
+    "conclusion": "success",
+    "id": 128528556559,
+    "name": "codeql / Analyze (actions)",
+    "started_at": "2026-11-07T21:06:30Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:55Z",
+    "conclusion": "success",
+    "id": 128528556544,
+    "name": "governance / delivery-status",
+    "started_at": "2026-11-07T21:06:23Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:08Z",
+    "conclusion": "success",
+    "id": 128528556526,
+    "name": "tests / closure-scope",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:23Z",
+    "conclusion": "success",
+    "id": 128528556523,
+    "name": "tests / mutation",
+    "started_at": "2026-11-07T21:05:34Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:28Z",
+    "conclusion": "success",
+    "id": 128528556518,
+    "name": "codeql / Analyze (javascript-typescript)",
+    "started_at": "2026-11-07T21:06:10Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:07:24Z",
+    "conclusion": "success",
+    "id": 128528556517,
+    "name": "governance / policy-docs",
+    "started_at": "2026-11-07T21:06:15Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": null,
+    "conclusion": null,
+    "id": 128528556504,
+    "name": "governance / instrument-self-tests",
+    "started_at": "2026-11-07T21:05:46Z",
+    "status": "in_progress"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:58Z",
+    "conclusion": "success",
+    "id": 128528556502,
+    "name": "codeql / Analyze (python)",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:20Z",
+    "conclusion": "success",
+    "id": 128528556465,
+    "name": "hassfest / hassfest",
+    "started_at": "2026-11-07T21:06:00Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:41Z",
+    "conclusion": "success",
+    "id": 128528556462,
+    "name": "tests / briefs",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:06:03Z",
+    "conclusion": "success",
+    "id": 128528556345,
+    "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-07T21:05:33Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:26Z",
+    "conclusion": "success",
+    "id": 128528404073,
+    "name": "refresh",
+    "started_at": "2026-11-07T21:04:59Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:08Z",
+    "conclusion": "success",
+    "id": 128528404037,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T21:04:59Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:06Z",
+    "conclusion": "success",
+    "id": 128528403969,
+    "name": "cancel-superseded",
+    "started_at": "2026-11-07T21:04:58Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:31Z",
+    "conclusion": "success",
+    "id": 128528403961,
+    "name": "prelude",
+    "started_at": "2026-11-07T21:04:59Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715780
+    },
+    "completed_at": "2026-11-07T21:05:30Z",
+    "conclusion": "success",
+    "id": 128528403952,
+    "name": "prelude",
+    "started_at": "2026-11-07T21:04:58Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906715876
+    },
+    "completed_at": "2026-11-07T21:05:34Z",
+    "conclusion": "success",
+    "id": 128528403749,
+    "name": "refresh",
+    "started_at": "2026-11-07T21:04:58Z",
+    "status": "completed"
+   },
+   {
+    "check_suite": {
+     "id": 114906713615
+    },
+    "completed_at": "2026-11-07T21:04:55Z",
+    "conclusion": "skipped",
+    "id": 128528402282,
+    "name": "arm",
+    "started_at": "2026-11-07T21:04:56Z",
+    "status": "completed"
+   }
+  ],
+  "head": "fefaa4926e36e9c571cc685e0b6aa2b391d14793",
+  "runs": [
+   {
+    "check_suite_id": 114906715780,
+    "conclusion": null,
+    "created_at": "2026-11-07T21:04:55Z",
+    "display_title": "CI code pr=3293 base=main sha=facbb8f2eec3b628af76157fa6cc0af29d8a39e0",
+    "id": 42414123291,
+    "status": "in_progress",
+    "updated_at": "2026-11-07T21:07:17Z"
+   },
+   {
+    "check_suite_id": 114906715876,
+    "conclusion": "failure",
+    "created_at": "2026-11-07T21:04:55Z",
+    "display_title": "CI edit pr=3293 base=main sha=facbb8f2eec3b628af76157fa6cc0af29d8a39e0",
+    "id": 42414123334,
+    "status": "completed",
+    "updated_at": "2026-11-07T21:07:58Z"
+   }
+  ]
+ }
+}
diff --git a/dev/audit/harnesses/r10_rca_gate_busy_defer_4.py b/dev/audit/harnesses/r10_rca_gate_busy_defer_4.py
new file mode 100644
index 000000000..ebc2a1d65
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_gate_busy_defer_4.py
@@ -0,0 +1,186 @@
+#!/usr/bin/env python3
+"""R10-RCA-GATE-BUSY-DEFER-4: the merge train's classifier reads gate.py's deferral red as RED.
+
+    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py record     # prints fixture JSON (gh api)
+    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay [--tree DIR]
+
+An edit run's `gate` concludes `failure` with the deferral text at once (gate.py `deferral`)
+while the code run it defers to is unfinished; gate-sweep.yml re-runs it after the code run
+completes. A reader that keys on the check run's conclusion alone reads that as a verdict.
+
+record  reads the check runs and the ci.yml runs listing of the three evidence heads (#3293
+        fefaa492, #3267 cc6ee11f, #3268 64fe84b2) from the GitHub API, trimmed to the fields the
+        train reads, for dev/audit/harnesses/r10_rca_gate_busy_defer_4.json.
+replay  puts each scene through DIR's merge_train (default: this tree; a baseline is
+        `git archive <sha> tools custom_components/heatpump_optimizer/manifest.json | tar -x -C $D`
+        and `--tree $D`). The reader is `Train.classify_at` when the program has it, else
+        `classify(latest_runs(runs), required)` -- the one-read `classify` subcommand's read.
+        Scenes: the three evidence heads at the moment their edit gate concluded (the code run
+        unfinished: the recorded listings, cut at that instant), a SETTLE-GAP scene (the same
+        head with the code run's gate green and the edit gate not yet re-run: built from the
+        #3293 fixture, synthetic, flagged so), and three null controls (a real code-run red, an
+        all-green head, a red non-gate required context beside a running code run).
+        Prints one `SCENE name state` line each, then `RESULT replay defects=<n> scenes=<m>`;
+        rc 1 when a deferral scene reads RED (DEFERRAL-READ-RED) or a null control reads wrong.
+        SETTLE-GAP reads are printed and counted apart (`settle_gap=`); they are not in `defects`.
+"""
+from __future__ import annotations
+
+import copy
+import importlib
+import json
+import subprocess
+import sys
+from datetime import datetime
+from pathlib import Path
+
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+FIXTURE = Path(__file__).with_suffix(".json")
+REPO = "tvofi/heatpump_optimizer"
+HEADS = {"3293": "fefaa4926e36e9c571cc685e0b6aa2b391d14793", "3267": "cc6ee11ff27b8b57cd7e017121544dca9dbe6e30",
+         "3268": "64fe84b24efb6e4f720e011b75b559b6a3bac7e9"}
+CR_KEYS = ("id", "name", "status", "conclusion", "started_at", "completed_at")
+
+
+def gh(path):
+    out = subprocess.run(["gh", "api", "--paginate", "--jq", ".check_runs[]?, .workflow_runs[]?", path],
+                         capture_output=True, text=True, check=True).stdout
+    return [json.loads(x) for x in out.splitlines() if x.strip()]
+
+
+def record():
+    fx = {}
+    for pr, sha in HEADS.items():
+        crs = [dict({k: c.get(k) for k in CR_KEYS}, check_suite={"id": (c.get("check_suite") or {}).get("id")})
+               for c in gh(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100")]
+        runs = [{k: r.get(k) for k in ("id", "check_suite_id", "display_title", "status", "conclusion",
+                                       "created_at", "updated_at")}
+                for r in gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={sha}&per_page=100")]
+        fx[pr] = {"head": sha, "check_runs": crs, "runs": runs}
+    print(json.dumps(fx, indent=1, sort_keys=True))
+
+
+def ts(s):
+    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
+
+
+def as_of(scene, t):
+    """The listings as they read at instant <t>: a job or run not yet started is absent; one
+    that concluded after <t> is in progress."""
+    crs = []
+    for c in copy.deepcopy(scene["check_runs"]):
+        if c["started_at"] and ts(c["started_at"]) > t:
+            continue
+        if c["completed_at"] and ts(c["completed_at"]) > t:
+            c["status"], c["conclusion"] = "in_progress", None
+        crs.append(c)
+    runs = []
+    for r in copy.deepcopy(scene["runs"]):
+        if r["status"] == "completed" and ts(r["updated_at"]) > t:
+            r["status"], r["conclusion"] = "in_progress", None
+        runs.append(r)
+    return crs, runs
+
+
+def load_train(tree):
+    for m in [k for k in sys.modules if k in ("merge_train", "gh_read")]:
+        del sys.modules[m]
+    sys.path.insert(0, str(Path(tree) / "tools/audit/seat"))
+    try:
+        return importlib.import_module("merge_train")
+    finally:
+        sys.path.pop(0)
+
+
+def read(mt, crs, runs, head):
+    """(state, pending, red) as the train's one-read classifier gives it at <head>."""
+    req = [mt.GATE]
+    if not hasattr(mt.Train, "classify_at"):
+        return mt.classify(mt.latest_runs(crs), req)
+    t = object.__new__(mt.Train)
+    t.repo, t.log = REPO, lambda *a, **k: None
+    t.run = lambda argv: (0, "\n".join(json.dumps(r) for r in runs))
+    # the wall clock `sweep_settling` reads: five seconds after the newest completion in the scene
+    now = max([ts(c["completed_at"]) for c in crs if c.get("completed_at")] or [0]) + 5
+    t.wall = lambda: now
+    return t.classify_at(head, crs, req)
+
+
+def unit(name, suite, status="completed", conclusion="success", at="2026-11-07T21:05:00Z", cid=1):
+    return {"id": cid, "name": name, "status": status, "conclusion": conclusion if status == "completed" else None,
+            "started_at": at, "completed_at": at if status == "completed" else None, "check_suite": {"id": suite}}
+
+
+def scenes():
+    fx = json.loads(FIXTURE.read_text())
+    out = []
+    for pr, sc in fx.items():
+        gate = next(c for c in sc["check_runs"] if c["name"] == "gate")
+        out.append((f"#{pr}-edit-gate-just-failed", "WAIT", "defect", sc["head"], *as_of(sc, ts(gate["completed_at"]) + 5)))
+    sc = fx["3293"]
+    gate = next(c for c in sc["check_runs"] if c["name"] == "gate")
+    crs, runs = as_of(sc, ts(gate["completed_at"]) + 5)
+    code = next(r for r in runs if "code" in r["display_title"])
+    code["status"], code["conclusion"] = "completed", "success"
+    crs = crs + [unit("gate", code["check_suite_id"], at="2026-11-07T21:20:00Z", cid=9)]
+    out.append(("#3293-settle-gap(synthetic)", "WAIT", "settle-gap", sc["head"], crs, runs))
+    code_red = [dict(c) for c in crs]
+    code_red[-1] = dict(code_red[-1], conclusion="failure")
+    out.append(("null-code-run-red(synthetic)", "RED", "null", sc["head"], code_red, runs))
+    all_green = [dict(c, conclusion="success") if c["name"] == "gate" else c for c in crs]
+    out.append(("null-all-green(synthetic)", "GREEN", "null", sc["head"], [c for c in all_green if c["name"] != "gate"
+                or c["check_suite"]["id"] == code["check_suite_id"]], [dict(r, status="completed") for r in runs]))
+    return out
+
+
+def replay(tree):
+    mt = load_train(tree)
+    defects = gap = bad = 0
+    fx = json.loads(FIXTURE.read_text())
+    rows = scenes()
+    for name, want, kind, head, crs, runs in rows:
+        state, pending, red = read(mt, crs, runs, head)
+        got = state.upper()
+        print(f"SCENE {name} want={want} got={got} pending={pending} red={red}")
+        if got != want:
+            if kind == "defect" and got == "RED":
+                defects += 1
+            elif kind == "settle-gap":
+                gap += 1
+            else:
+                bad += 1
+    # the non-gate null: a red non-gate required context beside a running code run is RED for any program
+    crs, runs = as_of(fx["3293"], ts("2026-11-07T21:07:00Z"))
+    crs = crs + [unit("fast", 99, conclusion="failure")]
+    req = ["fast"]
+    st = (mt.classify(mt.latest_runs(crs), req))[0].upper()
+    print(f"SCENE null-red-non-gate want=RED got={st}")
+    bad += st != "RED"
+    print(f"RESULT replay defects={defects} settle_gap={gap} null_bad={bad} scenes={len(rows) + 1}")
+    return 1 if defects or bad else 0
+
+
+if __name__ == "__main__":
+    a = sys.argv[1:]
+    if a[:1] == ["record"]:
+        record()
+    elif a[:1] == ["replay"]:
+        sys.exit(replay(a[a.index("--tree") + 1] if "--tree" in a else ROOT))
+    else:
+        print(__doc__)
+        sys.exit(2)
diff --git a/dev/audit/rca/r10-gate-busy-defer-4.md b/dev/audit/rca/r10-gate-busy-defer-4.md
new file mode 100644
index 000000000..6569a4054
--- /dev/null
+++ b/dev/audit/rca/r10-gate-busy-defer-4.md
@@ -0,0 +1,226 @@
+# R10-RCA-GATE-BUSY-DEFER-4: the producer of a deferral was fixed three times, its reader never
+
+Root-cause seat (`dev/governance/roles/root-cause.md`), run beside the repair fixer of
+#3290 (R10-HOTFIX-TRAIN-DEFER-WAIT, head `a38bd141`, unmerged), which owns the classifier
+wait. This seat changed nothing in `tools/audit/seat/merge_train.py`, `proof_watch.py` or
+`tools/ci/`. Measured at origin/main `dee8b413f` (which carries #3287's merge `5c1fa41fb`)
+on 2026-11-07 between 21:00Z and 21:45Z. Third instance of one class: a required `gate`
+that concludes `failure` as a deferral, not a verdict (#3246, #3278's RCA, this).
+
+## Result
+
+- **Cause.** `gate.py` publishes an edit run's deferral as a failed `gate` check run at
+  once ("run(s) [ids] at this head are still being judged; their gate decides"). The code
+  run it defers to publishes no `gate` until every unit finishes, and `gate-sweep.yml`
+  re-runs the deferred gate only after that run completes. For that whole time the head
+  carries a completed, failed `gate`. `merge_train.py` `classify` reads a check run's
+  conclusion alone, and `run_state` counts only `success` as a green `gate`, so it reads
+  the deferral as RED and the train SKIPs (`ci: red at the head: gate`).
+- **Why #3287 did not cure it.** #3287 fixed the producer: the deferring gate no longer
+  holds a runner and `sweep.settle` re-judges it. It also made the red visible at once and
+  longer to a reader: before it, a deferring gate waited, up to 720 s, a gate in progress
+  the train read as pending. The reader #3278's RCA and #3287's harnesses never modelled
+  is the train's classifier, shared by `bus.sh` dispatch (`merge_train.py classify`).
+- **Which side moved** (`git log`, not the error text). The reader's rule,
+  "only `success` is a green gate; the worst suite stands", dates from `9262e6f43`
+  (2026-10-22, ci-layout P2b U9a). The producer moved three times: `fa921fd59`
+  (2026-11-05 20:29Z, C3: an edit run beside an unfinished code run fails at once),
+  `cc100c275` (#3276, 2026-11-07 04:47Z, the wait restored, bounded), `52f9fc5b3` (#3287,
+  12:47Z, at once again, no bound). `git log --since=2026-11-04 -S'def classify(' -- tools/audit/seat/merge_train.py`
+  returns 0 commits. The producer's meaning of a failed `gate` changed; the
+  reader was not told.
+- **Process state: (c).** Section 2.
+- **Cost test: the harness passes** (standing cost 0). Section 4. A structural change to
+  the readers outside `classify` is proposed, not built.
+- **Built.** `dev/audit/harnesses/r10_rca_gate_busy_defer_4.py` and its fixture
+  `r10_rca_gate_busy_defer_4.json`: the recorded listings of the three evidence heads,
+  cut at the instant their edit gate concluded, through a chosen `merge_train.py`.
+
+## 1. The cause, reproduced
+
+### The evidence, read through the API
+
+#3293 head `fefaa492`. Both runs were created 21:04:55Z. Edit run 42414123334: `gate` job
+21:07:26Z to 21:07:57Z, `failure`; its log (read through `merge_train.py job-log`) says
+`programs restored from dee8b413...` and ends
+`FAIL run(s) [42414123291] at this head are still being judged; their gate decides`, so the
+gate ran the tree that carries #3287. Code run 42414123291 was `in_progress` with its
+`governance / instrument-self-tests` job unfinished at 21:07:17Z and still at 21:20Z.
+#3267 `cc6ee11f` (edit gate failed 21:00:29Z, code run 42413349469 in progress) and #3268
+`64fe84b2` (edit gate failed 21:00:17Z, code run 42413389218 in progress) have the same
+shape. The listings are `r10_rca_gate_busy_defer_4.json`, recorded by its `record` arm.
+I could not read the train's own log (it is not in the tree); the SKIP lines are the
+orchestrator's, and the harness reconstructs the read from the listings.
+
+### The listings through the train's reader
+
+    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay            # this tree
+    D=$(mktemp -d); git archive <ref> tools custom_components/heatpump_optimizer/manifest.json | tar -x -C $D
+    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay --tree $D
+
+| program | three evidence heads | settle gap (synthetic) | null controls | rc |
+|---|---|---|---|---|
+| origin/main `dee8b413` | RED, RED, RED (`red=['gate']`) | RED | as wanted | 1, `defects=3` |
+| #3290 head `a38bd141` | WAIT, WAIT, WAIT (`pending=['gate']`) | RED | as wanted | 0, `defects=0` |
+| `a38bd141` with `deferred = {GATE} if busy else set()` mutated to `set()` | RED x3 | RED | as wanted | 1, `defects=3` |
+
+All three skips would have been prevented by #3290: at each, the code run was unfinished,
+which is what its `busy` read names. **The one it would not prevent is the settle gap**:
+the code run has concluded green and `gate-sweep.yml` has not yet re-run the edit gate.
+`classify_at` is one read and takes no settle (its own docstring); `wait_ci` waits
+`SWEEP_SETTLE_POLLS = 1` poll. The harness scene is built from the #3293 fixture by adding
+a green code-run `gate` and marking the code run completed. It is synthetic, named so,
+and counted apart (`settle_gap=1`); the evidence pairs hold no real instance, because
+all three code runs were still in progress. Its reads are RED at main and at #3290 alike.
+Whether the sweep leaves the edit gate red for longer than one poll is #3290's open
+question; this record measured the gap from the census below only (median 0.9 min from
+the decider's green to the re-run's green, three samples).
+
+Null controls, all in the same run: a code run that ended `failure` reads RED at every
+program (a deferral wait must not hide a real red); a head with every gate green reads
+GREEN; a red non-gate required context beside a running code run reads RED. The
+mutated row above is the scoring control: a copy of #3290 with its wait removed goes
+back to `defects=3`, so the arm moves.
+
+## 2. Process state: (c)
+
+The process that existed: #3287's finder harnesses (`r10_gate_busy_defer_3.py replay`,
+`r10_gate_defer_race.py`, both at both ends), its mutation proof (G1, S1-S7) and its
+adversarial review. They ran, and they passed (`origin/verdict/3287`). Their unit is
+`gate.judge()` and `sweep.Sweep` over recorded listings: the producer of a conclusion. No
+check had a consumer of the conclusion in its unit.
+
+The signature was in the evidence and was attributed to the defect being fixed. The
+review ran `merge_train.py classify` at the PR head, which "first read RED at 16:55Z on
+edit gate 128458265063" with the deferral text, and "per the brief I waited rather than
+blocked". The verdict lists it as evidence, and the PR's merge made the red appear on
+every head with a running code run. #3278's RCA recorded the same shape for the stale pin
+("the signature of the gap was read and recorded, and it was attributed to the defect
+itself").
+
+**Why the class's barrier did not reach the instance** (`root-cause.md` section 2). The
+two earlier instances are `_rca` entries with `class: null`, so no audit-class barrier is
+on record for this class; what stands in as one is #3278's replay harness
+(`r10_rca_gate_busy_defer_2.py`), and its unit is `gate.judge()` over recorded listings
+through a chosen program copy. It asks "which program copy decides this listing, and
+how". It does not ask "who reads what the decision publishes". The countermeasure
+changes the unit: the replay here judges the same recorded listings through a consumer.
+
+Ruled out: **not (d)**, as a changed precondition nobody noticed? Partly true of
+`fa921fd59`, which changed what a failed `gate` means on 2026-11-05, and `A5`'s comment in
+`merge_train.py` already names "R-9's defer red" as a hazard to readers; but the train's
+SKIPs on this class predate #3287 (#3290's header counts 32 of 56 `ci red=['gate']` SKIPs
+over 2026-11-05 to 2026-11-07, which I quote and did not re-measure), so the process
+was not changed under a working check; it never had one. **Not (b)**: `fixer.md` step 8
+already says a fix that changes one reader of a governance concept registers the concept
+with every reader the enumeration returns, and `fix-review.md` reads every red check.
+**Not (a)**: the cheaper detector, the reviewer's own `classify`, ran and printed RED.
+
+## 3. Reach of the class
+
+Question: which readers of a required context's conclusion can read a deferral red as
+final RED. A static read of origin/main (a subagent's; I re-read `merge_pr.sh`'s `RED:` exit,
+`policy_refusal`'s `POLICY_RED` and `gate_digest`'s red list myself): the deferral text appears in no
+reader; `gate.py`'s `busy` is consumed by `gate.py` and its self-test alone, until #3290.
+
+| reader | reads | reads a deferral as RED | behind #3290? |
+|---|---|---|---|
+| `merge_train.py classify`, `classify_at`, `Train.wait_ci` | check runs, worst `gate` suite | yes (the proof wait, the main wait, the `--overlap` log) | yes, `classify`; `wait_ci` partly |
+| `merge_train.py platform_gate` (`classify --pr` cross-check) | `statusCheckRollup` | yes | no |
+| `merge_train.py policy_refusal` | `statusCheckRollup`, `POLICY_RED` includes FAILURE | yes: parks the entry, `wait=False` | no |
+| `bus.sh` dispatch, `cloud_dispatch.py` reviewer prompt | the `classify` exit code | yes: refuses a reviewer, tells it RC 1 is RED | through `classify` |
+| `review_packet.py` `gate_digest` | check runs | yes: writes the red into the packet | no |
+| `merge_pr.sh` | check runs, then `mergeStateStatus` | yes: exits 1 `RED: gate` | no |
+| `ci-watch.sh` | check runs | yes: alerts `RED: gate` | no |
+| `orchestrator_tick.py` `one_pr` | check runs | partly: a heuristic (`GATE_WAIT_MAX_S`, now stale, #3287's review) | no |
+| `tools/ci/ruleset_cutover.py` `preconditions_gate` | newest `gate` per suite | yes: a precondition refusal, manual | no |
+| `postmerge.py`, `orchestrator_tick.py` main tip | `classify --main` | no: main push runs are not edit runs | n/a |
+| `body_patch.sh`, `pr-contract.yml`, `prepr.sh` | check runs less `gate` | no: `gate` is filtered out | n/a |
+| `autofix_statuses.sh`, `approve_held_runs.sh`, `ci_critpath.py`, `failure_logs.sh`, `codeql-triage-poll.sh` | analytics or other names | no | n/a |
+
+Eight rows read the deferral as final (`orchestrator_tick.py` partly), six of them outside the
+`classify` family: `platform_gate`, `policy_refusal`, `gate_digest`, `merge_pr.sh`, `ci-watch.sh`
+and `ruleset_cutover.py`. The harness drives `classify` only; the others are named, not
+driven (Forward-carry).
+
+## 4. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+**The defect, measured.** Census rule: every `gate` job of a `ci.yml` run created in the
+window whose log's verdict is the deferral text (`r10_gate_busy_defer_3.py census`, the
+#3287 harness, run unchanged):
+
+    python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census \
+      --since 2026-11-07T19:14:31Z --until 2026-11-07T21:30:00Z
+    RESULT census deferral_fails=14 heads=14 per_head_max=1 held_runner_s=1844 held_ge_600=2
+      resolved=3 by_bot=3 by_human=0 median_min=0.9
+
+(19:14:31Z is #3287's merge, `5c1fa41fb`, 20:14:31+01:00; the run took 88 s.) 14 heads
+carried a deferral red in 2 h 16 min; 3 resolved by the sweep (no human re-run: the
+producer's repair works), after 32.3, 35.0 and 12.6 minutes counted from the edit gate's
+start to the re-run's green. The other 11 had no green re-run at 21:30Z; the three evidence
+heads are among them, and their code runs were still unfinished. Every one of those heads
+is a head the train reads RED for the whole interval. I did not count the train's SKIPs
+since the merge (its log is not in the tree): the three named by the orchestrator are
+the SKIPs I read the runs of. #3290 quotes 32 of 56 `ci red=['gate']` SKIPs over 2026-11-05
+to 2026-11-07. Null control: a census that read every gate would also count the
+non-deferral reds; it printed `deferral_fails=14` against the log text, and the replay's
+real-red scene is the control that the text and the verdict differ.
+
+**P(recurrence).** Every edit run beside a code run that outlives it (`C3`): 14 of 14 heads
+here. Three producer changes in 3 days; every future change to `gate.py` re-opens it.
+
+**The harness's standing cost.** 0: it runs no gate and no CI lane; `replay` takes 0.055 s
+wall (`time` around it). Against 11 heads reading RED for tens of minutes. The test
+passes.
+
+**What was refused.** Changing the readers outside `classify` in this pull request: they
+are not this seat's files and #3290's design (the classifier waits on `busy`) fixes the
+`classify` family; the rest is a design choice for that fixer and the orchestrator, not a
+mechanical edit. A new CI lane that drives every reader on every `gate.py` change was
+refused for cost: a reader census runs only when `gate.py` merges (4 merges to
+`gate.py`, `prelude.py` and `sweep.py` since 2026-11-05).
+
+## 5. Countermeasure
+
+### 5.1 Built
+
+`r10_rca_gate_busy_defer_4.py replay` (red on the defect, green on the fix, with the null
+controls of section 1). It is classified in `tests/closures.json`. Standing cost: none.
+
+### 5.2 Proposed, not built
+
+1. **One deferral predicate for every reader**, `gate_deferred(check_run)` exported
+   next to `gate.py`'s `deferral()`, so the text has one author and readers take the
+   predicate (the check run's output title carries the text; #3290's self-test builds
+   its fixtures that way). Readers: the table in section 3. Addresses (c): the unit
+   becomes "every reader of the published conclusion".
+2. **Register "a failed required gate is a verdict" in `agreement.mjs`**, with the
+   readers section 3 lists, so `fixer.md` step 8 has an enumeration to run when a
+   producer changes the conclusion's meaning. Owner's decision (policy-adjacent).
+3. **The settle gap**: a wait keyed on the sweep's own re-run (the edit run listed
+   `in_progress` again) and not a poll count. #3290's.
+
+### 5.3 Side finding: `train.sh add --front`
+
+`merge_train.py add <pr> <verdict> --front` exists; `train.sh add` forwards it to the
+child's flag list after `--`, where it is refused as an unknown argument. The pass-through
+next to `--priority` (and a pin of it in `train.sh --self-test`'s `add` argv case) belongs
+to R10-HOTFIX-TRAIN-DEFER-WAIT (#3290), which owns `train.sh`; this record does not change
+the file. `add <pr> --front` (re-fronting an entry already spooled, no verdict) is a
+further gap: `train.sh add` needs `<verdict>`, and a verdictless form is a restructure.
+
+## Forward-carry
+
+- To the #3290 fixer and the orchestrator: the settle gap (section 1) and the six
+  readers outside `classify`'s family in section 3. `merge_pr.sh` and `policy_refusal` act on the
+  red (exit, park); `review_packet.py` and `ci-watch.sh` report it.
+- To the #3290 fixer: replay this record's harness at the new head; the three evidence
+  scenes must read WAIT, and the mutated-wait control must read `defects=3`.
+- To the orchestrator: `orchestrator_tick.py` still describes the superseded 720 s wait
+  (#3287's review carried it).
+- Carry: R10-HOTFIX-TRAIN-DEFER-WAIT: `train.sh add <pr> <verdict> --front` is refused by
+  `merge_train.py` as an unknown argument after `--`; add the pass-through next to
+  `--priority` with an argv pin in `train.sh --self-test`, and consider a verdictless
+  `add <pr> --front`.
diff --git a/dev/programme/delivery/3353.md b/dev/programme/delivery/3353.md
new file mode 100644
index 000000000..18d612fea
--- /dev/null
+++ b/dev/programme/delivery/3353.md
@@ -0,0 +1 @@
+- [#3353](https://github.com/tvofi/heatpump_optimizer/pull/3353) — **open**, R10-RCA-GATE-BUSY-DEFER-2 (part 4): RCA (R10-RCA-GATE-BUSY-DEFER-2)
diff --git a/tests/closures.json b/tests/closures.json
index 49fc44084..3c986ee02 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4125,6 +4125,7 @@
    "dev/audit/harnesses/r10_rca_cop_unmeasured.py",
    "dev/audit/harnesses/r10_rca_flush_dispatch.py",
    "dev/audit/harnesses/r10_rca_gate_busy_defer_2.py",
+   "dev/audit/harnesses/r10_rca_gate_busy_defer_4.py",
    "dev/audit/harnesses/r10_rca_name_kept_plant.py",
    "dev/audit/harnesses/r10_rca_sav_estimate.py",
    "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
