# Review packet #3632
head: 1b9db1a72251463faf31ddeaa586119ed950dfb0
base: 98847b99d7bb3238686efd6869f805c89c6d1ff1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132950266063 success
arch-score / arch-score id=132950138141 success
arm id=132949878133 skipped
budget-raise-gate / budget-raise-gate id=132950138120 success
cancel-superseded id=132949879107 success
codeql id=132950084058 skipped
codeql / Analyze (actions) id=132950138080 success
codeql / Analyze (javascript-typescript) id=132950138109 success
codeql / Analyze (python) id=132950138135 success
gate id=132950553246 failure
governance id=132950084023 skipped
governance / env-matrix id=132950138128 in_progress
governance / instrument-self-tests id=132950138091 in_progress
governance / policy-docs id=132950138099 success
governance / record id=132950139301 skipped
governance / wave-script id=132950138148 success
hassfest id=132950084245 skipped
hassfest / hassfest id=132950138040 success
kernel-points id=132950138975 skipped
pr-contract id=132950554843 skipped
prelude id=132949878823 success
refresh id=132949879010 success
sweep-self id=132950787236 skipped
tests id=132950083634 skipped
tests / arch-instrument id=132950372497 success
tests / briefs id=132950138071 success
tests / browser id=132950372454 in_progress
tests / closure-scope id=132950138039 success
tests / closures id=132950372509 in_progress
tests / coverage id=132950372465 in_progress
tests / fast (3.14) id=132950372463 in_progress
tests / mutation id=132950138052 success
tests / mutation-autofix id=132950437610 skipped
tests / mutation-pins id=132950437527 skipped
tests / nightly-ha id=132950373889 skipped
tests / nightly-status id=132950138160 success
tests / replay id=132950373662 skipped
tests / typing id=132950372475 success
validate id=132950084832 skipped
validate / validate-hacs id=132950138029 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132950138091: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 1b9db1a72251463faf31ddeaa586119ed950dfb0 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3632.md b/dev/programme/delivery/3632.md
new file mode 100644
index 0000000000..2e60d1777c
--- /dev/null
+++ b/dev/programme/delivery/3632.md
@@ -0,0 +1 @@
+- [#3632](https://github.com/tvofi/heatpump_optimizer/pull/3632) — **open**, R11-PRE-OWNER-CRITERIA: r11 pre owner criteria p1 (R11-PRE-OWNER-CRITERIA)
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index c0b8bd5653..70c48332ff 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -260,6 +260,11 @@ const POLICY_GLOBS = [
   /^dev\/governance\/rules\/[a-z0-9-]+\.md$/,
   /^dev\/governance\/roles\/[A-Za-z0-9_.-]+\.md$/,
   /^dev\/governance\/dimensions\/[A-Za-z0-9_.-]+\.md$/,
+  // The owner's acceptance criteria per dimension, named by
+  // dev/audit/config/objective.json's owner_criteria: what a finder grades
+  // against, so measured like the brief beside it (R11-PRE-OWNER-CRITERIA,
+  // under mandate 6893738184).
+  /^dev\/governance\/dimensions\/criteria\/[A-Za-z0-9_.-]+\.md$/,
   /^tools\/audit\/briefs\/[A-Za-z0-9_.-]+\.md$/,
   /^tools\/audit\/README\.md$/,
   /^dev\/audit\/README\.md$/,
@@ -6149,6 +6154,23 @@ function assertAcceptance(derived) {
     console.log(`\nFIXTURE OVER-FIRES: checkCoverage reported ${covOk.length} finding(s) on a covered file, e.g. ${JSON.stringify(covOk[0].where)}`)
     return 1
   }
+  // The owner's per-dimension acceptance criteria live one directory below the
+  // dimension briefs, which `dimensions/[A-Za-z0-9_.-]+\.md` does not reach.
+  // Dropping the `dimensions/criteria/` glob reports the file as uncovered, and
+  // a file two levels down (`criteria/sub/`) stays uncovered under it.
+  const criteriaFile = 'dev/governance/dimensions/criteria/D10-criteria.md'
+  const criteriaDeep = 'dev/governance/dimensions/criteria/sub/D10-criteria.md'
+  const covCriteria = drive([criteriaFile])
+  const covCriteriaDeep = drive([criteriaDeep])
+  pins += 2
+  if (covCriteria.length) {
+    console.log(`\nFIXTURE OVER-FIRES: checkCoverage reported ${criteriaFile}: ${JSON.stringify(covCriteria[0].message)}. The criteria directory is a policy directory with its own glob.`)
+    return 1
+  }
+  if (covCriteriaDeep.length !== 1 || covCriteriaDeep[0].where !== criteriaDeep) {
+    console.log(`\nFIXTURE VACUOUS: checkCoverage did not report ${criteriaDeep}; the criteria glob must cover one directory level, not a subtree`)
+    return 1
+  }
   // R9-RO-5. A file under dev/governance/ that no glob names is the coverage
   // arm. Dropping `^dev/governance/` from POLICY_DIRS makes covStray empty,
   // which is the vacuous pass the directory constant existed to close. A

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
