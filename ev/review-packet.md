# Review packet #3214
head: b15157fb5b98e2011fdd9765672fda20f9952b63
base: af941ad4a296ffec76562e3161972bce3ad2dec4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126910601523 skipped
cancel-superseded id=126910607148 queued
prelude id=126910606470 queued
refresh id=126910606871 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...15e5ebacee11809acb17728f1dc36326989d1566
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3214.md b/dev/programme/delivery/3214.md
new file mode 100644
index 000000000..a90495175
--- /dev/null
+++ b/dev/programme/delivery/3214.md
@@ -0,0 +1 @@
+- [#3214](https://github.com/tvofi/heatpump_optimizer/pull/3214) — **open**, triage: batch 124, P389 REJECT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch124.md b/dev/programme/triage/s6-batch124.md
new file mode 100644
index 000000000..2decff42c
--- /dev/null
+++ b/dev/programme/triage/s6-batch124.md
@@ -0,0 +1,13 @@
+# Proposal triage, session s12, batch 124 (P389)
+
+## P389: the newest `Carry:` marker for an item supersedes earlier ones
+
+Verdict: REJECT, already delivered by `s6-batch65.md#P296`: `Carry: <dest> (item <id>, supersedes <old>)`.
+
+Source: the orchestrator's queue line of 2026-11-04T21:43:27Z, withdrawn by the orchestrator as its own mistake.
+
+Instances: #3185 item a2e21972. `carry_audit.py pr 3185` prints `#2259 superseded by R10-FLY-ARCHSCORE-STMT-PACKING` and 4 routed, 0 bad.
+
+Cost: the binding cost is losing P296's guard: newest-wins would let a later marker undo a live routing, which a supersede of a valid destination is refused for today.
+
+Binding: none.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
