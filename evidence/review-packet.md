# Review packet #3161
head: 60279abb4d3160ed64fd0a2fe73c4c6c3fbeed86
base: 3dd3697228dfac221f90915c6060bb8ad794e99f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125085058338 success
arch-score / arch-score id=125085014433 success
arm id=125084326137 skipped
budget-raise-gate / budget-raise-gate id=125085014276 success
cancel-superseded id=125084337102 success
codeql / Analyze (actions) id=125085014475 success
codeql / Analyze (javascript-typescript) id=125085014408 success
codeql / Analyze (python) id=125085014375 success
governance / delivery-status id=125085014518 success
governance / delivery-status-publish id=125085015847 skipped
governance / env-matrix id=125085014551 in_progress
governance / instrument-self-tests id=125085014529 in_progress
governance / policy-docs id=125085014523 success
governance / record id=125085016448 skipped
governance / wave-script id=125085014417 success
hassfest / hassfest id=125085014368 success
kernel-points id=125085015351 skipped
prelude id=125084337144 success
refresh id=125084336852 success
tests / arch-instrument id=125085290340 in_progress
tests / briefs id=125085014578 success
tests / browser id=125085290330 in_progress
tests / closure-scope id=125085014541 success
tests / closures id=125085290314 in_progress
tests / coverage id=125085290360 queued
tests / fast (3.14) id=125085290341 in_progress
tests / mutation id=125085014412 success
tests / mutation-autofix id=125085239881 skipped
tests / mutation-pins id=125085239229 skipped
tests / nightly-ha id=125085292030 skipped
tests / nightly-status id=125085014472 success
tests / replay id=125085291957 skipped
tests / typing id=125085290320 queued
validate / validate-hacs id=125085014607 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --name-only $(git merge-base origin/main 99835eadc) 99835eadc
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         dev/audit/rounds/round6/D11/fix/codeowners_gap.py
             `dev/audit/rounds/round6/D11/fix/codeowners_gap.py` is in the tree at this head

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3161.md b/dev/programme/delivery/3161.md
new file mode 100644
index 000000000..fbdb4ff1f
--- /dev/null
+++ b/dev/programme/delivery/3161.md
@@ -0,0 +1 @@
+- [#3161](https://github.com/tvofi/heatpump_optimizer/pull/3161) — **open**, triage: s9 batch 112 (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch112.md b/dev/programme/triage/s6-batch112.md
new file mode 100644
index 000000000..b62a62743
--- /dev/null
+++ b/dev/programme/triage/s6-batch112.md
@@ -0,0 +1,44 @@
+# Proposal triage, session s10, batch 112 (P370)
+
+The rolling batch after batch 111. Facts were read at origin/main `8247a1ed1`, at the round's
+roster branch `origin/handoff/audit-r10-roster` (`5dc16bbe1`), in the session-local opener's log,
+and in the session's seat ledger.
+
+## P370: the opener maps a split-part topic to no roster group (a re-file of P363)
+
+Verdict: DEFER. The item is already owned: R10-OPENER-REUSE carry 10, routed from P363
+(`s6-batch106.md#P363`, ACCEPT). No new carry and no group. The answer changes only if that
+group is closed without building the rule, or if the rule it builds still misses a part topic.
+
+Source: the orchestrator s10's queue line of 2026-11-02T03:29:40Z. It proposes stripping a
+trailing `-p<N>` before the roster lookup, so the group is the base group and the title names the
+part.
+
+Instances:
+- **The new instance.** Opener log `driver4.log` at 03:24Z:
+  `NEEDS-TITLE/GROUP (no roster group for topic) r10-deps-actions-bump-p1`. The seat ledger at
+  03:29:40Z records it as opened by hand with group R10-DEPS-ACTIONS-BUMP.
+  - Its handoff head `99835eadc` changes one file against its merge base,
+    `dev/audit/rounds/round6/D11/fix/codeowners_gap.py`. Nothing is under `custom_components/`.
+- **The same mechanism P363 ruled on.** P363's instances were the part topics
+  `r10-fly-train-defaults-p2`, `r10-roster-ops-2-p1` and `r10-sav-comfort-p2`.
+  - Today's line is the fourth part topic to miss.
+  - `grep -c NEEDS-TITLE driver4.log` prints 8, against 88 `RESULT` lines.
+- **The rule is routed and has landed.** On roster `5dc16bbe1`, R10-OPENER-REUSE holds 10 carries.
+  - Carry 10 opens "From triage P363", and amends rule (3) of P337's open driver, which is carry 8.
+  - P363's rule tries an exact match first, then the base group with the part suffix stripped.
+    That is this proposal's remedy, with the exact-match guard P363 found it needs: five roster
+    names already end in such a suffix, among them R10-ROSTER-OPS-2.
+  - The group's `resume` reads stage `not-started`, next step "dispatch a fixer". No pull request
+    is open on its branch.
+
+Cost:
+- A duplicate carry would cost a second copy of the same text on R10-OPENER-REUSE. Its brief would
+  then hold two specifications of one rule, which its fixer must reconcile.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why DEFER.** The ruling's destination already exists and holds this exact remedy. What this
+  instance adds is a count: 4 part topics have missed since 2026-10-31, each opened by hand.
+- **Not ruled under the LOG class.** The rule is already ACCEPTed. Its delivery waits on
+  R10-OPENER-REUSE's dispatch, which is the orchestrator's queue decision, not a triage one.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
