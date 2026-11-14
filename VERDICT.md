Fix review: merge b56f703837126d8e20d1af7f75339ed58189ce3a

bus-nonce: aeba9c83f42ab7f673cc5ba648b71533
pending-ci: gate

## Evidence

Round: first (no prior reviewed head). Measured head: b56f703837126d8e20d1af7f75339ed58189ce3a (ev/HEAD.txt), the PR's head at the time of this verdict and the head the body names. The diff against the merge base touches only tools/policy/brief_lint.mjs (+6/-2, inside assertCarryControl) and dev/programme/delivery/3570.md (ev/diffstat.txt). VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched, so env_drift has nothing to check.

Merge with main: `git merge-tree --write-tree origin/main <head>` at origin/main 7aac3e7c044a6ea7c5e6f4271e7e563f2fdee424 exits 0, with no conflict (ev/merge-tree.txt).

Hunk provenance: the body says the hunk is part 2's `git diff 154dbb4c61..78325190f8 -- tools/policy/brief_lint.mjs`, applied unchanged. I diffed the +/- lines of that range against c311127944's own diff and they are identical (ev/p2.diff, ev/p3.diff).

The body's four arms (`node tools/policy/brief_lint.mjs`, with the grader file copied into the data tree), re-taken at origin/main 7aac3e7c04, which is newer than the 3fd9fab077 the body cites (ev/arms-summary.txt, ev/arm-*.txt):
- RESULT arm A, main grader on main data: rc=0, VACUOUS 0.
- RESULT arm B, head grader on main data: rc=0, VACUOUS 0.
- RESULT arm C, head grader on part-2 data (78325190f8): rc=0, VACUOUS 0. This is the case the fix exists for.
- RESULT arm D, main grader on part-2 data: rc=1, `CONTROL VACUOUS: carry control:` printed. This is the null control, and it reproduces the red the fix cures.
- RESULT arm E, head grader on head data: rc=0, VACUOUS 0.
All four figures in the body re-derive.

Mutation proof, at the head (ev/mutants-summary.txt, ev/mut-*.txt):
- RESULT M1 (the body's mutant, member = 'not-a-member.json'): rc=1, killed by a TypeError in carryControlFindings and not by a VACUOUS line. That matches the body's own disclosure.
- RESULT M2 (a stronger mutant of my own, member = 'carry-999998.json', a name with digits that is outside the set): rc=1, `CONTROL VACUOUS: carry control: a legacy carry file (carry-999998.json) is refused (the narrowing)`. The narrowing check really reads membership, so it is not vacuous.
- RESULT M5 (legacy_control_files.json emptied): rc=1, `the legacy set is empty, so the narrowing is unexercised`. The new empty-set guard fires on its own case.
- RESULT M4 (empty-set guard deleted, real data): rc=0, survives. This is equivalent on the real data, since the guard only fires on an empty set, as the body states. M5 is its kill.
- RESULT M3 (the `if (legacy.length) problems.push` line deleted): rc=0, survives. That line is the self-test's own assertion. It changed only in wording, from the same assertion on main, and it is not a production line. Deleting an assertion cannot make the assertion fail; M2 shows the assertion is live.

Harness: the finder's harness is the linter's own no-arg self-test run, which is committed and is the only brief_lint.mjs step in tests.yml (`briefs`). No other harness is owed. Class: one seam (the one literal member name in assertCarryControl). The other uses of LEGACY_CONTROL_FILES at the head read the set, not a literal member (lines 980, 1466-1496).

Brief carries 0-2: the body says none is discharged or changed here (grader half only). carry_audit at the head reports 0 finding items, and the body's Forward-carry is none, so there is no carry for step 10 to open.

CI: classify printed `WAIT b56f703837126d8e20d1af7f75339ed58189ce3a pending: gate red: none` on every poll from 22:32 to 23:02 UTC (ev/classify.log). With the review complete, the verdict goes back pending-ci on the `gate` context, and the relay posts it only once CI is green at this head. There is no red at this head so far, which matches the body's `## Red checks: none`.
