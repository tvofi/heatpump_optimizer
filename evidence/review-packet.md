# Review packet #3686
head: 375037b736ccac76242b76c8d2c0dc4af9806605
base: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=133549825435 skipped
cancel-superseded id=133551340252 queued
prelude id=133551340564 queued
refresh id=133551340786 queued

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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/yardstick/round11/EVALUATION.json b/dev/audit/yardstick/round11/EVALUATION.json
index a145946887..4793b31806 100644
--- a/dev/audit/yardstick/round11/EVALUATION.json
+++ b/dev/audit/yardstick/round11/EVALUATION.json
@@ -887,6 +887,10 @@
    "verdict": "keep",
    "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ledger.py` 1359 lines (0 at the window's start), 17 merges touched it in the window, 16 roster group(s) name it, 2 of them hotfix."
   },
+  "tools/audit/seat/instruments/loop_ledger.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD); the guide also landed after the graded window, so no round has run with it. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 92d38ecb64 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/loop_ledger.py` 353 lines (0 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. The guide was added by 30d545ce63 (R11-PRE-ROUND-METRICS part 2, pull request 3657): `git merge-base --is-ancestor <sha> v10.0.0` -> rc 1, after v10.0.0, so it is an object of objective.json at origin/main 92d38ecb64 and not at the graded SHA a39627da59. The page's claims hold against the script at 92d38ecb64: its seven fields are roster_lib.CONVERGENCE_FIELDS, all in roster_edit.py's SET_FIELDS; its vocabularies are roster_lib.FOUND_BY, CAUSES, CM_KINDS and convergence_why's D<n>, none, bugclasses.json and other-group rules; its owing rules are loop_ledger.owed; scorecard.py's E line calls owned_split. `python3 -I tools/audit/seat/loop_ledger.py --self-test` -> 21 ok, 0 failed, rc 0, covering each self-test claim on the page (empty directory, one dropped field per read, vocabulary refusal, two-commit history). `python3 -I tools/audit/seat/loop_ledger.py --repo . --roster-ref HEAD` -> rc 0, rounds 9 and 10 and weeks 2026-W42 on, with escapes, injected, refix and loop `unread (k of n ...)` wherever an owing group is unrecorded (round 10: escapes 43 of 43), as the page says."
+  },
   "tools/audit/seat/instruments/machinery_ratchet.py.md": {
    "verdict": "keep",
    "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/machinery_ratchet.py` 734 lines (0 at the window's start), 2 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix. 0018 names its `--measure` for rule 4; re-run: `python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4` -> {\"churn_per_kilo_product_lines\": 13548, \"exempted\": [], \"head\": \"13cbe48de4236b7979c754640cc5b1a099ef7475\", \"machinery\": 320, \"nonproduct_lines\": 303475, \"nonproduction_merges\": 477, \"product_lines\": 22400, \"production\": 103, \"record\": 157, \"window\": 580} | rc=0"
@@ -2111,5 +2115,14 @@
   },
   "unset": "`merged` stays unset on the 14 accepted gating cards whose work is open: E11-K-D4, K-D5, K-D9, K-D10 (pull request 3641), E11-N-P744-SCOPE (3657, 3658), E11-U1, U2, U4 to U10 (NEW-DIMENSIONS part 2).",
   "review_owed": "The objects differ from those at the review sha 02a48db212, so check_scopes.py refuses the review until a reviewer approves at a commit holding these objects; a delta review of this revision is owed. A review sha on this line keeps every `merged` above after the review."
+ },
+ "revision_5": {
+  "of": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
+  "by": "r11-evaluator (Opus 5.5)",
+  "why": "`python3 -I tools/audit/check_scopes.py --repo . --ref 92d38ecb64 --round 11` printed `has no keep/change/remove verdict for tools/audit/seat/instruments/loop_ledger.py.md`: pull request 3657 added the guide after revision 4. No existing verdict, card, `decision`, `ruling`, `merged` or `gates_finders` moves.",
+  "changes": {
+   "objects.tools/audit/seat/instruments/loop_ledger.py.md": "row added, `keep` on a NO-READ yield with its cost read and the page checked against the script; objective.json's globs at 92d38ecb64 match no other unrowed object (check_scopes.py names only this one)."
+  },
+  "review_owed": "The objects differ from those at the review sha 83dc948818, so check_scopes.py refuses the review until a reviewer approves at a commit holding this row; a delta review of this revision is owed."
  }
 }
diff --git a/dev/programme/delivery/3686.md b/dev/programme/delivery/3686.md
new file mode 100644
index 0000000000..7a99daa36c
--- /dev/null
+++ b/dev/programme/delivery/3686.md
@@ -0,0 +1 @@
+- [#3686](https://github.com/tvofi/heatpump_optimizer/pull/3686) — **open**, R11-START-EVALUATION-LAND (part 2): grade the loop-ledger instrument page (R11-START-EVALUATION-LAND)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
