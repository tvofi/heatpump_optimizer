# The fix reviewer's contract

You review one fix PR adversarially, in a fresh context, from a worktree at
the PR's head SHA. You are not checking that the code looks right; four
implementations on this project looked right and were wrong, one worse than
its bug. You are checking that the numbers are real.
**That worktree holds this contract as well as the tree and is frozen by design, so your copy of
it can be arbitrarily old** — and `preflight.sh` warns only before a push a reviewer never makes.
Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/`; empty is current.

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
   `audit-round2-evidence`; #258's proximity probe exists only inside a judge
   comment and must be recreated from there. #290's is committed: W3-G3 landed
   it as `harnesses/j5_gil.py`. A fixer who builds their own instrument must
   disclose it as their own, not the finder's, and you say the same if you had
   to build one to check the fix.
   Read the finding's own judge ruling first — #290's brief still prescribes a
   harness its judge already refused.

10. **Check the forward-carry before you return `merge`.** If the fixer's work
    produced a finding that changes how a later stage must work — a technique
    refused, an assumption invalidated, an option removed — the PR body names
    where it was written, and you open that destination and confirm it is there,
    carrying the control and stated as a precondition rather than an
    opportunity. A finding that exists only in this PR's comments has been
    recorded, not propagated, and that is
    `blocked <sha> carry-missing: not carried to <stage>`. See
    `.cursor/rules/finding-propagation.mdc`.
11. **A red check owes an answer.** `.cursor/rules/defect-root-cause.mdc`
    triggers on a defect that turned a check red where a cheaper detector could
    have run, and this step is where that trigger is checked. Read the PR's own
    checks — `get_check_runs`, or the commit's own `check-runs` API — not the
    body's account, and never a listing that shows one run per check. For each gate check that went red, the body names it
    and answers the question: the cheaper detector with its standing cost, or the
    finding that none exists. Both answers pass; silence does not, and that is
    `blocked <sha> root-cause-unanswered: <check> went red, unanswered`. The failures
    `ci-autofix.mdc` already repairs — `UNDER-SCOPED`, `INHERITED CLAIMS` — are
    answered by naming them: their countermeasure is the autofix job that exists.
    You are checking that the trigger was answered, not adjudicating the answer
    — the analysis is a separate seat, `tools/audit/briefs/root-cause.md`.

12. **Re-read the head before you post.** Name the SHA you measured in the
    verdict, and check it is still the head when you post it. A branch that
    moved under you means some of your numbers describe a tree that no longer
    exists: say which survive and which you re-took, rather than letting the
    verdict imply all of them were taken at the head it names.

    Step 7 is not this check. It compares the SHA in the body against what you
    measured, and a branch that moved after the body was written passes it. This
    one compares the **live head at posting time** against what you measured.

    `fixer.md`'s **The handoff freezes the branch** makes the head yours from the
    handoff on, so one that moved under you is a broken rule rather than an
    accident: `blocked <sha> head-moved: measured <sha>, head is <other>`. Re-measuring
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

    A non-zero exit names the conflicting paths. A conflict on any path other
    than `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`
    is yours to block on, because you cannot know the merged result is correct.
    **For those two, the path is not the answer** — read the driver's verdict, as
    below. The earlier form of this step disposed of them by path alone; that was
    measured wrong and is the reason the paragraph below exists.

    **The driver's verdict is in that command's stderr. Read it; do not infer
    it from the paths, and do not classify the conflict by line shape.**
    Unlike GitHub, `merge-tree` *does* invoke the `claimnotes` driver —
    measured, one invocation per conflicting claim file — but only if you
    installed it, because it is git config and git never clones config:

    ```
    python3 tests/env_drift.py --install-merge-driver   # once per clone
    ```

    Every path through the driver prints one line: `MERGE-CLAIM: resolved
    <path>` or `MERGE-CLAIM: refused <path>`. Key on that marker, not on the
    wording after it — several distinct checks supply that wording, so a list
    of messages goes stale. A `resolved` line settles that claim file, and a
    non-zero exit alongside it is about some **other** path. A `refused` line
    is the orchestrator's to resolve by hand, not a defect in the authored
    work — but it is also not something to wave past silently: say which file
    refused and why.

    Classifying by line shape instead is what fails. `_comment_lines` and
    `_is_may_drift` both test "everything before `#` is blank", so a
    `may-drift` line **is** a `#` comment, and `merge_claim_defect` refuses
    when one is lost. A rule of the form "a conflict confined to the `#`
    comment notes is merge-prep" therefore waves through a real refusal, on a
    file with no bare claim lines on any side. Read the marker instead. Why
    the driver refuses at all is in `CLAUDE.md` under the `claimnotes` driver;
    that is one rule and it lives there.

Return a verdict with your RESULT lines, in the exact shape your dispatch
prompt gives: `.claude/workflows/web-fix-wave.js` parses the comment's first
line and routes on it, so one that does not parse is recorded blocked.
