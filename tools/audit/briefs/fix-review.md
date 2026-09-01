# The fix reviewer's contract

You review one fix PR adversarially, in a fresh context, from a worktree at
the PR's head SHA. You are not checking that the code looks right; four
implementations on this project looked right and were wrong, one worse than
its bug. You are checking that the numbers are real.

1. Re-run the mutation proof: delete the production line(s) the PR names,
   run the closure, confirm the named checks fail, restore. If nothing fails,
   the test is vacuous and the PR is blocked.
2. Measure with the **finder's** harness, not the fixer's: at the baseline
   SHA and at the PR head, printing your own `RESULT` lines. A fixer who
   measures with a harness they wrote is measuring themselves.
3. Re-run the null control and the both-ends check where the PR claims one.
4. Compare the claim files with the actual drift: run `env_drift.py --all`
   (and `card_drift.mjs` for card changes) against the merge base; every
   moved fixture is claimed and every claim moved.
5. Check `VERSION`, the manifest version and the notes heading are untouched.
6. Attack the fix at other configurations the finding's harness accepts:
   the other topologies, the other price profiles, the zero-evidence install.
7. Confirm the head SHA in the PR body is the head you measured.

Return a verdict (`merge` / `blocked: <what>`) with your RESULT lines.
