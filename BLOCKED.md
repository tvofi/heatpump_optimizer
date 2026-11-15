# R11-PRE-OWNER-CRITERIA: blocked on a BOOTSTRAP split (decision 0013, Consequences)

Question: may the orchestrator land p1 below (the one tools/policy/policy_lint.mjs hunk) as its own pull request first, so that this group's code head da868a90ffa56ba62502dde5b1268bbb093c8cd2 (p2) hands off once p1 is on main?

Why: tools/pr/prepr.sh at da868a90ffa5 (merge base 26dbf7c43ec3) refuses only on ci predict:
  PREDICT governance / policy-docs GRADER policy_lint.mjs REFUSED by the base's copy, over tools/policy/policy_lint.mjs:
  ERROR [coverage] dev/governance/dimensions/criteria/D10-criteria.md: sits in a policy directory and matches no POLICY_GLOBS pattern
  -- BOOTSTRAP: no change in this pull request reaches the base's copy
governance / policy-docs is in merge_train.py owed-reds. uncoveredPolicyFiles reads only the hard-coded POLICY_GLOBS and POLICY_DIR_EXCLUDE, so no unpinned data
(corpus_excluded.json included) can register the new directory; the remedy fixer.md step 5 names is the split. This seat may write no ref but its own topic's.

p1, alone on origin/main (verified at 26dbf7c43ec3: node tools/policy/policy_lint.mjs -> TOTAL: 0 error(s); FIXTURE ok):

```diff
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index c0b8bd5653..acf8dc52fa 100644
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
```

p2 is this ref's parent, da868a90ffa5, which already contains the p1 hunk byte-identically: once p1 merges, p2's diff against main loses it and the base's
grader carries the glob. Every other prepr.sh step is ok at da868a90ffa5, and the body (refs/heads/handoff-wip/r11-pre-owner-criteria-body, BODY.md)
passes prepr.sh --body-check. After p1 lands: no re-merge is needed unless git merge-tree reports a conflict; rerun prepr.sh, push da868a90ffa5 to
handoff/r11-pre-owner-criteria and run body_push.sh.
