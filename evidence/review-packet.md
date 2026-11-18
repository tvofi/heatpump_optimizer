# Review packet #3730
head: 4d7c80e6eb05a70f68ab5498ebedfb42efa404ee
base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=134894826805 skipped
cancel-superseded id=134894826089 queued
prelude id=134894825255 queued
refresh id=134894825911 queued

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

## Review scope: delta (later round over the reviewed head bc02ae8701128c21146bee16d1260fa44e6e4bae)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at bc02ae8701128c21146bee16d1260fa44e6e4bae
Fix review: blocked bc02ae8701128c21146bee16d1260fa44e6e4bae record-contradiction: phases.json marks round-start items done whose own detail says still running or not dispatched, and lists #3717 (merged 11:32:08Z) under fix-waves, which it dates from 12:23Z

bus-nonce: 1a09b23e307c4dd15eb17603e33530c0

## Delta diff: git diff bc02ae8701128c21146bee16d1260fa44e6e4bae 4d7c80e6eb05a70f68ab5498ebedfb42efa404ee
diff --git a/dev/programme/round11/phases.json b/dev/programme/round11/phases.json
index 2c8cb0b029..4e89af51cd 100644
--- a/dev/programme/round11/phases.json
+++ b/dev/programme/round11/phases.json
@@ -20,68 +20,57 @@
         },
         {
           "name": "Owner card rulings",
-          "status": "done",
-          "detail": "48 cards, 2 still to rule"
+          "status": "done"
         },
         {
           "name": "Round-10 objective record",
           "status": "done",
-          "detail": "pull request #3611 open, in review"
+          "detail": "pull request #3611 merged 2026-11-15T14:47:57Z"
         },
         {
           "name": "Round-11 roster cutover",
-          "status": "done",
-          "detail": "approved"
+          "status": "done"
         },
         {
           "name": "R11-PRE-FINDER-CONTRACT",
-          "status": "done",
-          "detail": "finder-critical; fixer running since 12:05Z"
+          "status": "done"
         },
         {
           "name": "R11-PRE-BRIEFS-CENSUS",
-          "status": "done",
-          "detail": "finder-critical; fixer running since 12:05Z"
+          "status": "done"
         },
         {
           "name": "R11-PRE-BRIEFS-TEXT",
-          "status": "done",
-          "detail": "finder-critical; fixer running since 12:05Z"
+          "status": "done"
         },
         {
           "name": "R11-PRE-OWNER-CRITERIA",
-          "status": "done",
-          "detail": "finder-critical; fixer running since 12:05Z"
+          "status": "done"
         },
         {
           "name": "R11-PRE-NEW-DIMENSIONS",
-          "status": "done",
-          "detail": "finder-critical; design first, not yet dispatched"
+          "status": "done"
         },
         {
           "name": "R11-PRE-ROUND-METRICS part 1",
-          "status": "done",
-          "detail": "finder-critical (recall and overlap); fixer running since 12:43Z"
+          "status": "done"
         },
         {
           "name": "Scopes proved",
-          "status": "done",
-          "detail": "finder-critical"
+          "status": "done"
         },
         {
           "name": "Baseline at a green main",
-          "status": "done",
-          "detail": "finder-critical"
+          "status": "done"
         },
         {
           "name": "Instrument groups",
-          "status": "done",
-          "detail": "in parallel, not gating finders: R11-PRE-MACHINERY-LIMITER, three S hotfixes, R11-PRE-TOOLCHAIN-PIN and R11-PRE-SHARED-FILES in design, R11-PRE-STANDING-SCRIPTS, RULINGS-FILE, RELAY-REBUILD, HANDOFF-BOOKKEEPING, ACK-COMPLETION, TOKEN-LEDGER, PLAN-RENDER"
+          "status": "done"
         },
         {
           "name": "Outside work",
           "status": "done",
-          "detail": "in parallel, not gating finders: #3598 in review, #3602 in repair, #3529 open"
+          "detail": "#3598 merged 2026-11-15T21:29:46Z, #3602 merged 2026-11-16T19:03:08Z, #3529 merged 2026-11-18T11:32:11Z"
         }
       ]
     },
@@ -110,7 +99,7 @@
     {
       "phase": "fix-waves",
       "status": "running",
-      "started": "2026-11-18T12:23:00Z",
+      "started": "2026-11-18T11:32:09Z",
       "items": [
         {
           "name": "Merged",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
