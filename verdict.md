Fix review: merge 7b2f46be31725d0b003b36e7d4ad0e462f42f847

bus-nonce: a0d7578a7be3647c52148e14753b64b0

## Evidence

- Head reviewed: 7b2f46be31725d0b003b36e7d4ad0e462f42f847 (handoff/r10-closeout-prep-p2a tip, re-read at post time: ev/head-recheck.txt); the body's "## Head" names the same SHA, cut from origin/main e23124ff6e, which is current origin/main and the merge base.
- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. cloud-setup.sh --check: OK.
- Diff: one file, tools/policy/brief_lint.mjs, +6/-2, in assertCarryControl only. VERSION, manifest version and RELEASE_NOTES.md untouched; no claim file touched, no fixture moved, so env_drift has nothing to compare.
- Mutation proof re-run (ev/mutation-run.txt, ev/mutant.txt): `const LEGACY_CONTROL_FILES = new Set()` makes `node tools/policy/brief_lint.mjs` exit 1 with "CONTROL VACUOUS: carry control: the legacy set is empty, so the narrowing is unexercised", the body's line exactly; restored head exits 0 with "CONTROL ok" (ev/head.txt).
- Second mutant, mine: the same empty set with the new `if (!member)` arm also deleted prints "CONTROL ok" (ev/mutant2.txt; exit 1 there comes from the other checks once nothing is exempt), so the arm is what keeps an empty set from passing the narrowing vacuously. Deleting the arm alone against the real, non-empty set would survive: it guards a future state the set's shrink-only rule allows, not today's data, and the first mutant is the test that exercises it.
- Null control re-run (ev/null-control-run.txt, ev/part2-data.patch): part 2's data, `git diff 154dbb4c61 78325190f8` without tools/policy/brief_lint.mjs, applied to the head (carry-201.json leaves legacy_control_files.json). With main's linter: exit 1, "CONTROL VACUOUS ... a legacy carry file is refused (the narrowing)". With the head's linter: exit 0, "CONTROL ok". On main's own data the head's linter exits 0 (ev/head.txt). This matches the body.
- Class: one seam. In the head's tree, assertCarryControl was the only place that named a specific legacy member as a literal, and the change removes it. The other LEGACY_CONTROL_FILES readers (lintCarryFile default, the cap and staleness checks) take the set as a whole. Every other carry-N.json literal in the head linter is a self-test fixture (99000x, 999999), not a legacy member (ev/literal-members.txt).
- Merge with main: `git merge-tree --write-tree origin/main 7b2f46be31725d0b003b36e7d4ad0e462f42f847` exits 0, tree 37ae12e9d2 (ev/merge-tree.txt). No claim-driver lines.
- CI: no pull request exists yet, so there are no check runs and no review packet to read. `merge_train.py owed-reds` lists the owed set, but no head runs exist to compare against it. Red checks: none to answer. Figures: the body states none.
- Harness: the finder's instrument is the linter's own self-check (assertCarryControl run by `node tools/policy/brief_lint.mjs`, committed in-tree). No instrument was built by the fixer.
- Forward-carry: the body states none, and its note that this is not closure-gating (unmerged at the v10.0.0 stamp it goes to round 11) changes no later stage's brief.

## Findings

none
