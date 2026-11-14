# Review packet #3330
head: 18850191756612458a8a83d581789e04c25802fb
base: bb7dfb9bd6c68548d1a956adc411be91e02965e0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128746455645 success
arch-score / arch-score id=128746409691 success
arm id=128746277536 skipped
budget-raise-gate / budget-raise-gate id=128746409837 success
cancel-superseded id=128746279582 success
codeql id=128746406435 skipped
codeql / Analyze (actions) id=128746409750 success
codeql / Analyze (javascript-typescript) id=128746409666 success
codeql / Analyze (python) id=128746409800 success
gate id=128746734275 failure
governance id=128746406327 skipped
governance / delivery-status id=128746409720 success
governance / delivery-status-publish id=128746411273 skipped
governance / env-matrix id=128746409744 in_progress
governance / instrument-self-tests id=128746409871 in_progress
governance / policy-docs id=128746409767 success
governance / record id=128746410585 skipped
governance / wave-script id=128746409863 success
hassfest id=128746406103 skipped
hassfest / hassfest id=128746409611 success
kernel-points id=128746410377 skipped
pr-contract id=128746735236 skipped
prelude id=128746279502 success
refresh id=128746279320 success
tests id=128746406730 skipped
tests / arch-instrument id=128746631025 success
tests / briefs id=128746409736 success
tests / browser id=128746630995 success
tests / closure-scope id=128746409755 success
tests / closures id=128746630939 in_progress
tests / coverage id=128746631039 in_progress
tests / fast (3.14) id=128746631032 in_progress
tests / mutation id=128746409727 success
tests / mutation-autofix id=128746695471 skipped
tests / mutation-pins id=128746695458 skipped
tests / nightly-ha id=128746632602 skipped
tests / nightly-status id=128746409751 success
tests / replay id=128746632200 skipped
tests / typing id=128746631052 success
validate id=128746406695 skipped
validate / validate-hacs id=128746409640 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 18850191756612458a8a83d581789e04c25802fb

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
diff --git a/.claude/rules/finding-propagation.md b/.claude/rules/finding-propagation.md
index 34a387732..1806b8cb5 100644
--- a/.claude/rules/finding-propagation.md
+++ b/.claude/rules/finding-propagation.md
@@ -74,8 +74,9 @@ not at all.
   not yet started, so a running stage's seam has none (#1345's fifth seam).
 
 **While two copies disagree, the newer one is right and the other is the bug.**
-Say which is which in the carry; the out-of-tree copy needs no pull request, so
-it is usually the newer.
+Say which is which in the carry; the out-of-tree copy is usually the newer.
+
+A carry routes to another stage or seam's owner, never the fixer's own (`fixer.md`).
 
 ## Enforcement
 
@@ -96,6 +97,5 @@ done (`pr-contract`; the train's pre-flight).
 **Name a destination that exists.** A carry to a file `git grep` cannot find is
 not a carry.
 
-**Verify the write landed.** A scripted edit matching nothing reports success
-(`str.replace`, `sed`); seven of nine carries once went missing. Read the destination back: `brief_lint.mjs` does it for a roster and a
+**Verify the write landed.** A scripted edit matching nothing reports success; read the destination back: `brief_lint.mjs` does it for a roster and a
 carry file, and nothing for a role contract.
diff --git a/.cursor/rules/finding-propagation.mdc b/.cursor/rules/finding-propagation.mdc
index 5ba6a0139..5617efd41 100644
--- a/.cursor/rules/finding-propagation.mdc
+++ b/.cursor/rules/finding-propagation.mdc
@@ -71,8 +71,9 @@ not at all.
   not yet started, so a running stage's seam has none (#1345's fifth seam).
 
 **While two copies disagree, the newer one is right and the other is the bug.**
-Say which is which in the carry; the out-of-tree copy needs no pull request, so
-it is usually the newer.
+Say which is which in the carry; the out-of-tree copy is usually the newer.
+
+A carry routes to another stage or seam's owner, never the fixer's own (`fixer.md`).
 
 ## Enforcement
 
@@ -93,6 +94,5 @@ done (`pr-contract`; the train's pre-flight).
 **Name a destination that exists.** A carry to a file `git grep` cannot find is
 not a carry.
 
-**Verify the write landed.** A scripted edit matching nothing reports success
-(`str.replace`, `sed`); seven of nine carries once went missing. Read the destination back: `brief_lint.mjs` does it for a roster and a
+**Verify the write landed.** A scripted edit matching nothing reports success; read the destination back: `brief_lint.mjs` does it for a roster and a
 carry file, and nothing for a role contract.
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 9d4cc79ff..5e141ddc3 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -42,6 +42,8 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
     carry at the body's `handoff/audit-r<N>-roster` SHA) and confirm it states
     its control as a precondition (`finding-propagation.md`). One only
     in this PR's comments is `blocked <sha> carry-missing: not carried to <stage>`.
+    An own-group `Carry:` naming neither `fixer.md` exception is
+    `blocked <sha> carry-missing: own-group`.
 11. **A red check owes an answer** (`defect-root-cause.md`'s second
     trigger). Read the PR's own checks (`get_check_runs`, or
     the commit's `check-runs` API), not the body's account, and never a
@@ -121,10 +123,9 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
     mechanism the body names; a movement that survives is not earned:
     `blocked <sha> metric-gamed: <instrument>: <how>`. Then plant the diff's own
     kind of move on the same instrument with nothing improved, and on its
-    neighbouring rules, not only the counter's own re-spelled (#2373). If it reproduces
+    neighbouring rules, not only the counter's own re-spelled. If it reproduces
     the movement, block only where the diff's change is that shape; under a sound
-    change it is an instrument finding, carried by `finding-propagation.md`
-    (#1874, #1867, #1868). On a raise, judge each listed payment and
+    change it is an instrument finding, carried by `finding-propagation.md`. On a raise, judge each listed payment and
     hunt one it missed: one that truly improves the code is `metric-gamed` too.
 15. **Judge `fixer.md` step 17 on added lines**: a breach, or a departure
     from the architect or approved design note, is `blocked <sha> architecture-unsound: <how>`.
@@ -134,4 +135,3 @@ in the grammar above; one that does not parse is refused. Before you return one,
 
 **Say which round this is**: from the fourth, `fixer.md` owes a re-cut.
 
-A ruling naming a destination stage states it as a `Carry:` marker.
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 8f7fae7e1..d5f3c1f92 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -273,14 +273,11 @@ never a pull-request body — decision 0010, true under either merge method).
 the single class named by `COORDINATOR_CLASS_NAME`; the rest from every parsed
 module. A method added outside that **class** moves none of the first group, so
 the payment question does not arise there. *Class*, not file: `coordinator.py`
-holds several, and adding a method, call and attribute to `CoordinatorContext` moves no row.
-Derive the split (what `measure()` keys by that name) at your merge base; never carry it.
-`max_class_loc` is a span: a docstring line costs what a code line does.
+holds several; `CoordinatorContext` additions move no row. Derive the split at your merge base.
 
 **An empty payment pool is a halt only where a payment was owed.** Let
 `python3 tests/structure.py` name what moved at your merge base. Outside the
-coordinator class a split usually moves the maxima *down* -- which the gate still
-refuses until you re-record them.
+coordinator class a split moves the maxima *down*; re-record them.
 
 A raise is the owner's, confirmed before the push (`CLAUDE.md` rule 2); zero
 headroom is no veto on new functionality or the better fix (#398). **The ask and the PR body list every
@@ -296,6 +293,10 @@ Name the destination in your PR body — which brief, contract, carry file or
 roster received it — so the reviewer checks the destination rather than takes
 your word.
 
+**A finding in your own group's seam is built in this PR, not carried.**
+`Carry: <own group>` only names a pending owner or orchestrator ruling, or a
+split part the approved plan names.
+
 ## Before you hand off: answer any check your branch turned red
 
 `defect-root-cause.md`'s second trigger fires on your own PR: name each check
diff --git a/dev/governance/rules/finding-propagation.md b/dev/governance/rules/finding-propagation.md
index 34a387732..1806b8cb5 100644
--- a/dev/governance/rules/finding-propagation.md
+++ b/dev/governance/rules/finding-propagation.md
@@ -74,8 +74,9 @@ not at all.
   not yet started, so a running stage's seam has none (#1345's fifth seam).
 
 **While two copies disagree, the newer one is right and the other is the bug.**
-Say which is which in the carry; the out-of-tree copy needs no pull request, so
-it is usually the newer.
+Say which is which in the carry; the out-of-tree copy is usually the newer.
+
+A carry routes to another stage or seam's owner, never the fixer's own (`fixer.md`).
 
 ## Enforcement
 
@@ -96,6 +97,5 @@ done (`pr-contract`; the train's pre-flight).
 **Name a destination that exists.** A carry to a file `git grep` cannot find is
 not a carry.
 
-**Verify the write landed.** A scripted edit matching nothing reports success
-(`str.replace`, `sed`); seven of nine carries once went missing. Read the destination back: `brief_lint.mjs` does it for a roster and a
+**Verify the write landed.** A scripted edit matching nothing reports success; read the destination back: `brief_lint.mjs` does it for a roster and a
 carry file, and nothing for a role contract.
diff --git a/dev/programme/delivery/3330.md b/dev/programme/delivery/3330.md
new file mode 100644
index 000000000..ae93b728e
--- /dev/null
+++ b/dev/programme/delivery/3330.md
@@ -0,0 +1 @@
+- [#3330](https://github.com/tvofi/heatpump_optimizer/pull/3330) — **open**, R10-FLY-NO-SELF-CARRY: a fixer builds own-seam findings instead of carrying them into its own group (R10-FLY-NO-SELF-CARRY)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
