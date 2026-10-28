# Review packet #2926
head: 3754510d82e329cbb27d2f8ca38ed031eaafa6c2
base: beb570c817c4efcae0d5f6f4bba52f3383baf8db

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123030347658 skipped
cancel-superseded id=123030262513 queued
prelude id=123030262491 queued
refresh id=123030262266 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 87942540: R10-FLY-CARRY-DOC-CONTEXT
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git log --grep
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log origin/verdict/<n> | grep -c 'Fix review: merge'
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2926.md b/dev/programme/delivery/2926.md
new file mode 100644
index 000000000..845b28db5
--- /dev/null
+++ b/dev/programme/delivery/2926.md
@@ -0,0 +1 @@
+- [#2926](https://github.com/tvofi/heatpump_optimizer/pull/2926) — **open**, triage s7 batch 53: rule P264 (V178) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch53.md b/dev/programme/triage/s6-batch53.md
new file mode 100644
index 000000000..e591fa177
--- /dev/null
+++ b/dev/programme/triage/s6-batch53.md
@@ -0,0 +1,57 @@
+# Proposal triage, session s7, batch 53 (P264)
+
+One entry: V178, a friction filing by the orchestrator at 2026-10-28T18:43:14Z, quoted from
+`proposals.md` as it stands. It is ruled in its own batch because batch 52 (#2924) was already
+merge-verdicted and queued when it arrived. Facts were read at origin/main
+`beb570c817c4efcae0d5f6f4bba52f3383baf8db` and at the live roster,
+`origin/handoff/audit-r10-roster` `2ce021c6f19c4c4069d50994a271fd1e7b872834`.
+
+## P264: a carry-eligible merge verdict can be posted after a bot pin commit
+
+Verdict: ACCEPT, narrowed to `app_comment.sh`, into **R10-FLY-CARRY-DOC-CONTEXT**. That group is
+`not-started`, owns `tools/pr/app_approve.sh`'s carry semantics, and P255 (s6-batch52.md) routes a finding onto a
+not-started group that shares the seam.
+
+Source: `proposals.md` V178 (orchestrator friction, 2026-10-28T18:43:14Z). Instance: #2912, with a
+merge verdict at `cc0510ee2a25444363251df640509b3034bca4f6` and then the CI bot's `ci: pin killed
+mutants` commit `4fc6a4c51`.
+
+Instances (read at origin/main `beb570c81`, verdict refs fetched):
+- **The refusal is in the poster, not in the train.** `tools/pr/app_comment.sh:68-69` (`check_pr`)
+  refuses unless the live head equals the merge verdict's head: "head moved: the merge verdict
+  names $3, the live head of #$2 is $head".
+- **The train already accepts a posted verdict whose head the PR has moved past, when it carries.**
+  `merge_train.py` (`admit_verdict`, line 2029; the carry call at 2045-2048) runs `app_approve.sh --carry <verdict>
+  <head>` and takes the entry on `CARRY: yes`. But `posted_verdict` returns "verdict/<n> at <tip>
+  is confirmed and not posted" (line 2076) when the approver App never posted. So the carry path
+  is unreachable exactly when the pin lands before the post.
+- **The count since 10-21.** 16 of 284 PRs merged to main since 2026-10-21 carry a `ci: pin killed
+  mutants` commit (first-parent merges, `git log --grep` over each `^1..^2`). For 6 of them a merge
+  verdict names the pre-pin head: #2745, #2819, #2824, #2817, #2775 and #2612 (`origin/verdict/<n>`
+  subjects). In 3 of those the pin's commit time is before the verdict's, so the poster would
+  meet a moved head:
+  - #2612: pin 19:18Z, verdict 19:38Z (2026-10-22).
+  - #2775: pin 07:51Z, verdict 08:03Z (10-25).
+  - #2745: pin 01:06Z, verdict 01:45Z (10-25).
+  With #2912, that is 4 instances in 7 days. Each of the six PRs needed 2 or more merge verdicts
+  (`git log origin/verdict/<n> | grep -c 'Fix review: merge'`: 14, 3, 2, 2, 5 and 2).
+
+Carry (narrowed):
+- In `check_pr`, when the live head differs from a merge verdict's head, run `app_approve.sh
+  --carry <verdict-head> <live-head>`. Post on `CARRY: yes`, with one body line naming the carry
+  (`carry: <verdict-head> -> <live-head>, app_approve.sh --carry: yes`). Refuse as today otherwise.
+- Blocked verdicts and an unreadable carry answer are unchanged.
+- No change to `bus.sh` or `train.sh`. The train's own carry check at the queue already re-runs the
+  same predicate at the head it merges.
+- Controls:
+  - A pin-only head that carries posts and prints the carry line.
+  - A head with a branch-own code commit is refused ("head moved").
+  - A mutant that posts without the carry call passes the code-commit fixture, and fails that arm.
+  - Null: an unmoved head posts with no carry line.
+
+Cost: about 10 lines in `app_comment.sh` plus three self-test arms. One more `app_approve.sh`
+call, which reads git only, on a moved head.
+
+Binding: 4 instances in 7 days, each costing a re-review round (about 1 h review latency) plus a
+head-note body patch. The predicate that decides it is already trusted by the train at merge, so
+the fix removes the gap between the poster and the train rather than adding a rule.

