# Review packet #3036
head: f51d1e5d663de8c832c881c2ef663d740db830cd
base: 4822c8f9b7f7ca6201cea05a9c80f7797e5f56a6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124473892267 success
arch-score / arch-score id=124473859999 success
arm id=124473811006 skipped
budget-raise-gate / budget-raise-gate id=124473860066 success
cancel-superseded id=124473787276 success
codeql / Analyze (actions) id=124473859834 success
codeql / Analyze (javascript-typescript) id=124473859848 success
codeql / Analyze (python) id=124473859891 success
governance / delivery-status id=124473860119 success
governance / delivery-status-publish id=124473861159 skipped
governance / env-matrix id=124473860068 success
governance / instrument-self-tests id=124473859990 in_progress
governance / policy-docs id=124473859951 success
governance / record id=124473861413 skipped
governance / wave-script id=124473859976 success
hassfest / hassfest id=124473859828 success
kernel-points id=124473861408 skipped
prelude id=124473787030 success
refresh id=124473787260 success
tests / arch-instrument id=124473970003 success
tests / briefs id=124473860059 success
tests / browser id=124473969956 success
tests / claims-autofix id=124474488416 skipped
tests / closure-scope id=124473860121 success
tests / closures id=124473969997 success
tests / closures-autofix id=124474964027 skipped
tests / coverage id=124473969981 in_progress
tests / fast (3.14) id=124473970017 success
tests / mutation id=124473860039 success
tests / mutation-autofix id=124474003787 skipped
tests / mutation-pins id=124474003407 skipped
tests / nightly-ha id=124473971339 skipped
tests / nightly-status id=124473860541 success
tests / replay id=124473970711 skipped
tests / typing id=124473970013 success
validate / validate-hacs id=124473859823 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tools/merge/ledger_merge.py
             `tools/merge/ledger_merge.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3036.md b/dev/programme/delivery/3036.md
new file mode 100644
index 000000000..a62b8a3e6
--- /dev/null
+++ b/dev/programme/delivery/3036.md
@@ -0,0 +1 @@
+- [#3036](https://github.com/tvofi/heatpump_optimizer/pull/3036) — **open**, triage: s8 batch 89 (P326 REJECT ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch89.md b/dev/programme/triage/s6-batch89.md
new file mode 100644
index 000000000..39ad6451c
--- /dev/null
+++ b/dev/programme/triage/s6-batch89.md
@@ -0,0 +1,63 @@
+# Proposal triage, session s8, batch 89 (P326)
+
+The rolling batch after batch 88 (handoff `triage-s8-batch88`). Facts were read at origin/main
+`4822c8f9b` and at #3006's head `9033a5958`.
+
+## P326: after a main merge, auto-record a structure budget that measures IMPROVED and not yet recorded
+
+Verdict: REJECT. This covers both the filed auto-record and the driver fix it suggests on
+inspection. No roster op.
+- **The filed form is a policy change.** `dev/governance/rules/ci-autofix.md` lists what CI must
+  not automate: "Do not automate survivor triage, golden drift, structure budgets, `no-copies`,
+  orphan → `INERT`, or briefs lint." A job that commits `structure.py --record` on a merge is that
+  automation. CLAUDE.md rule 2 also has a seat "re-record deliberately with the reason in the
+  commit message". Accepting the job would mean an owner-approved edit to both. The trade below
+  does not reach that question.
+- **What actually happened, measured on #3006's merges.** Each row is `class_excess_loc`, read
+  with `--first-parent` from the head:
+
+  | Merge | Base | Ours | Theirs | Merged | Measured |
+  |---|---|---|---|---|---|
+  | `4665c0c91` (`ci: merge main`) | 17672 | 17671 | 17659 | 17658 | |
+  | `958b4af8e` | 17671 | 17658 | 17670 | 17657 | |
+  | `76d96ac77` (`ci: merge main`) | 17659 | 17657 | 17658 | 17656 | |
+  | `9033a5958` (the train's recarry) | 17658 | 17656 | 17656 | 17656 | 17654 |
+
+  - The first three merges follow `tools/merge/ledger_merge.py`'s count rule for
+    `structure_budgets.json`: base plus both deltas.
+  - The fourth hit the driver's earlier rule, "a key both sides changed to the same value takes
+    it" (`merge3`, `if ours == theirs: return ours`). The two sides agreed on 17656 by
+    coincidence, so both reductions were counted once.
+- **The driver fix is REJECTED as unsound.** That fix would sum the deltas in a sum ledger even
+  when the two sides agree.
+  - The equal-value rule is what makes a merge correct when both sides carry the same reduction.
+    `update_pr.sh` merges an authored handoff head into the PR branch, and a re-cut handoff
+    re-records the same budgets on a fresh base. Summing there double-counts, so structure.py
+    would read the merged tree as a raise.
+  - A text merge cannot tell an independent reduction from a shared one. Only the measurement
+    can.
+- **Benefit, measured: one instance.** It is #3006's `9033a5958`, at about 30 minutes for a fixer
+  round plus one train skip. `ledger_merge.py` resolved every other merge in #3006's chain
+  correctly.
+  - 41 first-parent merges since 2026-10-17 touched `tests/structure_budgets.json`.
+  - A coincidental equal value on two independent reductions of the same key is rare.
+  - The miss announces itself: `tests / fast` and prepr both refuse IMPROVED-not-recorded, and
+    the repair is one deliberate `structure.py --record`.
+- **Cost of the filed form.** A CI job that commits to PR heads, with a loop-guard subject and the
+  `action_required` approvals `ci-autofix.md` describes for the existing three. The policy edits
+  come on top.
+- **The trade is marginal.** That cost is clearly more than one 30-minute round.
+- **Re-open trigger.** Re-open, as the owner's policy question on `ci-autofix.md`'s list, if
+  IMPROVED-not-recorded after an automatic merge recurs on three or more PRs in one round.
+
+Source: the orchestrator s8's message of 2026-10-31 (#3006 round 3).
+
+Instances: #3006, merge `9033a5958`, where structure.py measured 17654 against a recorded 17656.
+
+Cost: as above. The filed form is a new autofix job plus edits to `ci-autofix.md` and CLAUDE.md
+rule 2. The driver variant is XS but unsound.
+
+Binding:
+- One instance, self-announcing, repaired by one deliberate command.
+- That does not pay for automating a budget write that the policy names as never automated, nor
+  for a driver rule that would double-count every re-cut.

