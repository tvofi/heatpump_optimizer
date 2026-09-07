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

10. **Check the forward-carry before you return `merge`.** If the fixer's work
    produced a finding that changes how a later stage must work — a technique
    refused, an assumption invalidated, an option removed — the PR body names
    where it was written, and you open that destination and confirm it is there,
    carrying the control and stated as a precondition rather than an
    opportunity. A finding that exists only in this PR's comments has been
    recorded, not propagated, and that is
    `blocked: finding not carried to <stage>`. See
    `.cursor/rules/finding-propagation.mdc`.
11. **A red check owes an answer.** `.cursor/rules/defect-root-cause.mdc`
    triggers on a defect that turned a check red where a cheaper detector could
    have run, and this step is where that trigger is checked. Read the PR's own
    checks — `gh pr checks <n>` and the runs on the branch's commits — not the
    body's account of them. For each gate check that went red, the body names it
    and answers the question: the cheaper detector with its standing cost, or the
    finding that none exists. Both answers pass; silence does not, and that is
    `blocked: root-cause trigger unanswered for <check>`. The failures
    `ci-autofix.mdc` already repairs — `UNDER-SCOPED`, `INHERITED CLAIMS` — are
    answered by naming them: their countermeasure is the autofix job that exists.
    You are checking that the trigger was answered, not adjudicating the answer
    — the analysis is a separate seat, `tools/audit/briefs/root-cause.md`.

12. **Re-read the head before you post.** Name the SHA you measured in the
    verdict, and check it is still the head when you post it. A branch that
    moved under you means some of your numbers describe a tree that no longer
    exists: say which survive and which you re-took, rather than letting the
    verdict imply all of them were taken at the head it names. Restricting the
    three-dot diff to the production paths and comparing it across the two heads
    is usually enough to show what moved.

    Step 7 is not this check. It compares the SHA in the body against what you
    measured, and a branch that moved after the body was written passes it. This
    one compares the **live head at posting time** against what you measured.

    `fixer.md`'s **The handoff freezes the branch** makes the head yours from the
    handoff on, so one that moved under you is a broken rule rather than an
    accident: `blocked: head moved under review, measured <sha>`. Re-measuring
    instead is yours to offer and is never owed — a violation the reviewer
    absorbs silently costs the seat that committed it nothing, which is how it
    recurs.

13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
    DIRTY` on a pull request is computed by GitHub, which cannot run this
    repository's `claimnotes` merge driver — git never clones config. Every open
    pull request therefore goes `DIRTY` the moment `main` touches a claim file,
    whether or not it conflicts with anything. Confirm before you block:

    ```
    git merge-tree --write-tree origin/main <head>
    ```

    A non-zero exit names the conflicting paths. If they are confined to
    `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`,
    that is merge-prep for the orchestrator and **not a verdict against the
    work** — say so and judge the authored diff. A conflict on any other path is
    yours to block on, because you cannot know the merged result is correct.

    Blocking on the status field alone makes every review a race with `main`,
    which no branch can win.

Return a verdict (`merge` / `blocked: <what>`) with your RESULT lines.
