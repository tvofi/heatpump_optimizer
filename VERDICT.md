Fix review: merge 2e3fc21cca5a64a9dd1684f184c210951a767b37

bus-nonce: 82c8ebe5aee0c88b4662033715c3f817
pending-ci: gate

## Summary

Round 1 (first review, scope full). The diff extends `checkOrphanCaps` in `tools/policy/policy_lint.mjs` to read `files_tokens` as well as `files`, adds one acceptance pin with an over-fire arm, and drops the two orphan `files_tokens` caps (`tools/audit/briefs/nudge.md`, `tools/audit/harnesses/README.md`), both absent from the tree at the merge base and at the head. No `custom_components/`, `VERSION`, manifest or `RELEASE_NOTES.md` line is touched.

## Evidence

- Head: the PR body's head line names 2e3fc21cca5a64a9dd1684f184c210951a767b37, which is the head reviewed (ev/HEAD.txt). Merge base e352724335c136b65562cd3e71f728549ad04a82.
- Roles currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0, no conflict, no MERGE-CLAIM line (ev/merge-tree.txt).
- Mutation (step 1): `['files', 'files_tokens'].flatMap` mutated to `['files'].flatMap`; `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: checkOrphanCaps did not report docs/a-file-no-glob-matches.md's files_tokens cap exactly once (got [])`. Restored: rc 0, `FIXTURE ok: 93 error(s) hold 279 pins` (ev/mutation-and-null.txt). Not vacuous.
- Null control, head grader on the base's budget data: `TOTAL: 2 error(s)`, the two `files_tokens` orphans named in the body; head data: `TOTAL: 0 error(s)`. Re-derived.
- Null control, base grader on the head's data: `TOTAL: 0 error(s)`, `278 pins`. Re-derived; matches the body (no BOOTSTRAP split owed).
- Figure 1: the class rule `set(files_tokens) - set(files)` gives `['tools/audit/briefs/nudge.md', 'tools/audit/harnesses/README.md']` at the merge base, `[]` at the head; both paths absent at both ends (ev/figures.txt). The class is closed by the diff; the extended check is the standing instrument.
- Figure 2: `279 pins` at the head, `278` with the base grader. Re-derived.
- Figure 3 (budget-raise reading): not re-run offline; CI `budget-raise-gate / budget-raise-gate` concluded success at this head, which reads the same `raises_between`.
- Figure 4 (`tests/structure.py`): not re-run; cited from CI per the cite-heavy-runs rule.
- Figures 5 and 6: `git grep 'nudge' -- tools/ci/` prints nothing at both ends; the `nudge\.md` grep prints the budget cap plus three `dev/programme/` records at the base and the three records only at the head. Re-derived.
- Finder's harness (steps 2, 9): none named; the group is a carry build (P764), and the acceptance pin inside `policy_lint.mjs` is the committed harness, which moves under its own perturbation (the mutant above).
- Step 14: the budget-file movement is earned: each removed cap names a file absent from the tree; the body's control (dropping a cap on a present file) is what `budget-raise-gate` refuses.
- Red checks: `tests / nightly-status` is red at render; it is not in `merge_train.py owed-reds`, so no answer is owed and it is not a block.
- CI: `merge_train.py classify 2e3fc21cca --pr 3668` polled 16:01Z-16:31Z, every run exit 3: `WAIT 2e3fc21cca5a64a9dd1684f184c210951a767b37 pending: gate red: none` (ev/classify-log.txt); jobs still running at 16:31Z: tests / lane-proofs, tests / coverage-ratchet, tests / graders-head-copy, tests / closures. Returned with `pending-ci:` per the brief.

## Findings

- Residual: a neighbouring table of the same budget file names paths absent from the tree: `roles.policy.opens` lists `tools/audit/briefs/fixer.md` (moved to `dev/governance/roles/fixer.md` by bc0f17ddb6) and `roles.record.opens` lists `.claude/workflows/wave-4-groups.json`, neither present at this head. `roleTokens` matches rule globs against those strings, so the stale spelling loads fewer rules than the real file would (an approximate fnmatch read: 1 rule for the old path against 4 for the moved one), and the `policy` role cap is measured under-charged. Not this PR's class (per-file caps), and no check reports it. Carry: R11-POLICY-TOKEN-CAP

## Notes

- Note: approval: a policy-budget change; it merges on the owner's approving review at the head or under a mandate scoped `all`, which is not this seat's to judge.
