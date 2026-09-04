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
8. **A quoted number you cannot re-derive is not verified — say so.** Three
   agents counting "the same" published-attribute census (#373) got three
   different absolute counts because each used a different rule; a later
   judge built sixteen definitions and found the residual non-zero at the
   merge base and zero at head under all of them, so the conclusion held
   even though every headline number in the bodies disagreed. Re-derive
   under the PR's stated rule before trusting its count; if you cannot, or
   if you had to build your own definition to check it, write that in the
   verdict rather than reporting a number as confirmed.
9. **When the finding has no committed harness, that is itself a finding.**
   Step 2 assumes one exists to measure with; twice it has not. #373's
   instrument was a shell `grep` in the issue's own body, nothing at tag
   `audit-round2-evidence`; #258's proximity probe and #290's `j5_gil.py`
   exist only inside judge comments and must be recreated from there. A
   fixer who builds their own instrument in that case must disclose it as
   its own construction, not the finder's, and you say the same in your
   verdict if you had to build one to check the fix. Read the finding's own
   judge ruling first — #290's brief still prescribes a harness its judge
   already refused.

Return a verdict (`merge` / `blocked: <what>`) with your RESULT lines.
