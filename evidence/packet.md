# Review packet #2892
head: 7243c07fe53232e96750ec89ff1687753fa50b53
base: e8cb7e68302b1d350bb8219fea99e911170af030

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=122561480636 success
arch-score / arch-score id=122567139924 success
arm id=122561288823 skipped
budget-raise-gate / budget-raise-gate id=122567139902 success
cancel-superseded id=122561288903 success
codeql id=122567142140 skipped
codeql / Analyze (actions) id=122561421234 success
codeql / Analyze (javascript-typescript) id=122561421044 success
codeql / Analyze (python) id=122561421129 success
gate id=122569756098 success
governance id=122567142362 skipped
governance / delivery-status id=122561421353 success
governance / delivery-status-publish id=122561423846 skipped
governance / env-matrix id=122561421207 success
governance / instrument-self-tests id=122561421219 success
governance / policy-docs id=122561421118 success
governance / record id=122561423783 skipped
governance / wave-script id=122561421187 success
hassfest id=122567142596 skipped
hassfest / hassfest id=122561420859 success
kernel-points id=122567142360 skipped
pr-contract / pr-contract id=122567680253 success
prelude id=122561289148 success
refresh id=122561289379 success
tests id=122567141942 skipped
tests / arch-instrument id=122561595548 success
tests / briefs id=122561421092 success
tests / browser id=122561595677 success
tests / ci-ratchet id=122563238964 skipped
tests / claims-autofix id=122562503176 skipped
tests / closure-scope id=122561421284 success
tests / closures id=122561595661 success
tests / closures-autofix id=122563238597 skipped
tests / coverage id=122561595630 success
tests / coverage-ratchet id=122561849799 success
tests / fast (3.14) id=122561595802 success
tests / graders-head-copy id=122561849787 success
tests / lane-proofs id=122563133323 success
tests / mutation id=122561421071 success
tests / mutation-autofix id=122561737847 skipped
tests / mutation-pins id=122561737304 skipped
tests / nightly-ha id=122561597114 skipped
tests / nightly-status id=122561421244 success
tests / replay id=122561597135 skipped
tests / typing id=122561595753 success
validate id=122567142969 skipped
validate / validate-hacs id=122561421033 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tools/audit/seat/merge_train.py
             `tools/audit/seat/merge_train.py` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2892.md b/dev/programme/delivery/2892.md
new file mode 100644
index 000000000..5b6b05347
--- /dev/null
+++ b/dev/programme/delivery/2892.md
@@ -0,0 +1 @@
+- [#2892](https://github.com/tvofi/heatpump_optimizer/pull/2892) — **open**, triage: batch 43 -- rule V130/V131 as P217/P218 (R10-TRAIN-UPGRADE)
diff --git a/dev/programme/triage/s6-batch43.md b/dev/programme/triage/s6-batch43.md
new file mode 100644
index 000000000..42a927729
--- /dev/null
+++ b/dev/programme/triage/s6-batch43.md
@@ -0,0 +1,82 @@
+# Proposal triage, session s7, batch 43 (P217-P218)
+
+Two proposals, written by the orchestrator s7 as alternatives on the same merge-train step: V130
+(refuse a draft head at the merge step) and V131 (undraft a head the train has already proved
+mergeable). They are ruled together, and the ruling says which one stands. Facts read at
+origin/main `ea36188c3`; roster at `origin/handoff/audit-r10-roster` `9aed78e0e` (212 groups).
+
+## P217: a draft head is admitted by the train and fails only at the merge call (V130)
+
+Verdict: REJECT -- superseded by P218. The refusal is sound and costs little, but it spends the
+resource the instance actually lost. Its one useful part, the add-time `draft: true` note, is
+carried inside P218's carry, so nothing is lost with the stop.
+
+Source: `proposals.md` V130 (orchestrator s7, 2026-10-27T20:55Z).
+
+Instances: two today. #2878 was admitted as a draft and undrafted 23 s later (`updated_at`
+2026-10-27T20:30:28Z); had its batch reached the merge step first, it would have stopped there.
+#2854 -- green on every check, `gate` green on two runs, `policy_lint` and `structure.py` green
+against main, approved by the app -- read `BLOCKED`/`REVIEW_REQUIRED` for the single reason that
+`isDraft` was true, and it is the critical path for the v7.0.5 stamp. Admission reads `state`,
+which says `open`; `mergeable_state: BLOCKED` cannot distinguish a draft from a missing approval.
+
+Why the stop loses to the undraft on the same evidence: both proposals fix the same blindness, and
+the measured cost is not "a merge was attempted on a draft" -- no merge was attempted -- it is
+**time**. #2854 sat in the batch as the stamp's critical path, and a `Stop` phase converts that
+into a batch slot spent plus a human round trip to perform a metadata write that changes no tree.
+The refusal is the right behaviour for a head that is *deliberately* held; it is the wrong
+behaviour for the heads in both instances, which were stale flags on heads every other check had
+already cleared. P218 clears the stale flag only after the train has proved the head, which is the
+stronger of the two answers to the same observation.
+
+What is kept: the add-time line logging `draft: true` as a note rather than a refusal. Draft state
+moves in both directions between `add` and the merge, and an admission-time refusal would have
+thrown out #2878, which was clean 23 seconds later. P218 makes that note load-bearing rather than
+a comment -- see its narrowing.
+
+## P218: the train undrafts a head it has already proved mergeable, instead of stopping on it (V131)
+
+Verdict: ACCEPT narrowed -> a carry of **R10-TRAIN-UPGRADE** (`resume.stage` `done`, so the roster
+op reopens it; it owns `tools/audit/seat/merge_train.py` and its brief is exactly "upgrade
+`merge_train.py` so that ...", with one carry open). The narrowing: undraft only a head the train
+**recorded as a draft at admission**, which closes the one arm the settled shape leaves open.
+
+Source: `proposals.md` V131 (orchestrator s7, 2026-10-27T21:00Z, owner-directed).
+
+Instances: the two above, read once. #2854's hours as the stamp's critical path is the cost that
+decides it; #2878's 23-second window is the demonstration that the flag is often stale.
+
+The settled conditions, which this ruling does not weaken: undraft runs in the merge step where
+V130 would stop, and only on a head the train has already admitted to that step -- a posted `merge`
+verdict naming the current head or one that carries to it (`app_approve.sh --carry` decides
+carrying), a clean merge tree against main, a delivery row at the head, no failing or pending
+required context, and the approval the step posts. Undrafting writes no commit and moves no head,
+so the verdict still names the tree being merged.
+
+**The arm the settled shape leaves open, which the narrowing closes.** An author who holds a head
+by flipping it to draft *after* admission, while a `merge` verdict is already posted at that head,
+passes every one of the five conditions -- the verdict is current, the tree is clean, the row is
+there, the contexts are green, the approval is the step's own -- and the train would publish a head
+its author had just marked as held. The conditions cannot see intent; they can see history. The
+admission-time `draft: true` note that V130 asked for makes one bit of that history available at
+the merge step: undraft only when the head was **already a draft when it was admitted**, so a flag
+set later -- the only flag an author sets to say "stop" -- is respected. The cost is one recorded
+boolean at `add` and one comparison at the merge step, and the add-time note is no longer a
+comment; it is the guard's input.
+
+Cost: one `gh pr ready` call in the merge step, one recorded boolean at admission, one log line
+(`UNDRAFT #<pr> <head>`), and a re-read of `isDraft` after the call before the merge proceeds.
+Benefit measured: #2854's hours in the live batch as the v7.0.5 critical path, and #2878's near
+miss. No new dependency, no new rule. The train reads no draft flag today (`grep -ci draft
+tools/audit/seat/merge_train.py` = 0 at origin/main `e8cb7e683`); a seat reads `isDraft` by hand, so the
+recorded boolean and the re-read are the train's first draft reads.
+
+Binding: undraft only after all five settled conditions hold **and** the head was recorded a draft
+at admission; the `UNDRAFT` line is written once, with the PR and the head, and the merge continues
+in the same iteration only if the re-read shows `isDraft` false -- a re-draft between the call and
+the merge stops the run rather than merging past it; a failed `gh pr ready` is a `Stop` with its own
+phase, never a silent continue; the non-draft path is untouched and prints no line (null control);
+a draft whose verdict names an older head, a draft with a pending required context, and a head
+drafted after admission are each left exactly as they are today (the three null controls, the third
+being this ruling's addition); and the write is the app's, as the approval already is, so a run
+without the app's authority fails at `gh pr ready` and stops.

