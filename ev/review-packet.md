# Review packet #3830
head: 5c8ad0805b99d3be04b221e92cd40ad2c6506d66
base: e698fc8ac374a1d72c230b55d938d75b03b7de67

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=136877205518 skipped
cancel-superseded id=136878881020 queued
prelude id=136878880732 queued
refresh id=136878880951 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git grep -I
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git rev-parse --verify
             `git rev-parse` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git ls-tree -r -l <c> | awk '{s+=$4} END{print s}'
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 1 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index b7ebf071f9..cc1e47f695 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -1727,7 +1727,12 @@ jobs:
   # above: `policy-docs` proves the checks are right, this proves they ran.
   env-matrix:
     runs-on: ubuntu-latest
-    timeout-minutes: 10
+    # Twice the job's projected p95. Its policy_lint arms spend most of their
+    # time in one whole-tree `git grep` per cited symbol, so the job scales with
+    # tracked bytes. 8fa10e00ce doubled those bytes with round-11 evidence; the
+    # 10-minute cap then cancelled 11 of the next 29 main runs, where 270 before
+    # had none. Rule: ceil(2 x p95 before x policy-docs lint-step growth / 60).
+    timeout-minutes: 26
     # R10-CI-SLIM C7(a): a required name, so it stands down at the step level on
     # a pull request whose every changed file is product and reports success.
     env:
diff --git a/dev/programme/delivery/3830.md b/dev/programme/delivery/3830.md
new file mode 100644
index 0000000000..032edfeb36
--- /dev/null
+++ b/dev/programme/delivery/3830.md
@@ -0,0 +1 @@
+- [#3830](https://github.com/tvofi/heatpump_optimizer/pull/3830) — **open**, env-matrix: cap re-derived from its measured duration (26 min) (r11-hotfix-envmatrix-timeout)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
