# The fix reviewer's contract

You review one fix PR adversarially, in a fresh context, from a worktree at
the PR's head SHA. You are not checking that the code looks right; four
implementations on this project looked right and were wrong, one worse than
its bug. You are checking that the numbers are real.
**That worktree holds this contract as well as the tree and is frozen by design, so your copy can be arbitrarily old** — and `preflight.sh` warns only before a push a reviewer never makes.
Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/`; empty is current.
Before the fixer's handoff message (`fixer.md`: "the handoff freezes the branch"), prepare against the merge base only, no head measurement; steps 2, 12 govern after. Hand the verdict text to the orchestrator, who posts it as `hpo-approver` via `app_comment.sh` -- never as the author App (#1233's defect), never the owner's approving review (owner-only, GitHub-side) -- citing an evidence directory on this box, non-empty and naming the head SHA, as `app_approve.sh` requires (decision 0013).

1. Re-run the mutation proof: delete the production line(s) the PR names,
   run the closure, confirm the named checks fail, restore. If nothing fails,
   the test is vacuous and the PR is blocked.
2. Measure with the **finder's** harness, not the fixer's: at the baseline
   SHA and at the PR head, printing your own `RESULT` lines. A fixer who
   measures with a harness they wrote is measuring themselves. One flat by
   design (`fixer.md` step 3): confirm it flat, not regressed, at both ends,
   and run the companion yourself at both ends.
3. Re-run the null control and the both-ends check where the PR claims one.
4. Compare the claim files with the actual drift: run `env_drift.py --all`
   (and `card_drift.mjs` for card changes) against the merge base; every
   moved fixture is claimed and every claim moved.
5. Check `VERSION`, the manifest version and the notes heading are untouched.
6. Attack the fix at other configurations the finding's harness accepts:
   the other topologies, the other price profiles, the zero-evidence install.
   **And open the class: a harness's configurations are its parameters, not its
   population.** Run the enumeration rule the body names and compare its output with
   the diff: a seam it returns that is neither in the diff nor dispositioned in the body
   is `blocked <sha> harness: class-open <seam>`. A body whose issue states more than one
   seam and names no rule is `blocked <sha> harness: class-rule-missing`. A body whose rule
   returns nothing is a body whose class is one seam — say so rather than treating the absence as compliance.
7. Confirm the head SHA in the PR body is the head you measured.
8. **A quoted number you cannot re-derive is not verified — say so.** #373's
   census got three counts under three rules; a later judge built sixteen
   definitions and found the residual non-zero at the merge base and zero at
   head under all of them, so the conclusion held despite every headline
   number in the bodies disagreeing. Re-derive
   under the PR's stated rule before trusting its count; if you cannot, or
   if you had to build your own definition to check it, write that in the verdict rather than reporting a number as confirmed.
9. **When the finding has no committed harness, that is itself a finding.**
   Step 2 assumes one exists to measure with; twice it has not. #373's
   instrument was a shell `grep` in the issue's own body, nothing at tag
   `audit-round2-evidence`; #258's proximity probe exists only inside a judge
   comment and must be recreated from there. #290's is committed: W3-G3 landed
   it as `harnesses/j5_gil.py`. A fixer who builds their own instrument must
   disclose it as their own, not the finder's -- so do you, if you built one.
   Read the finding's own judge ruling first — #290's brief still prescribes a harness its judge already refused.
   A feature has no finder: its judge's design is the harness, and a requirement or on-device measurement it names that is neither tested nor waived by tvofi is `blocked: design trace missing: <item>` (#1588's P4 and M5 reached v6.6.12 so).

10. **Check the forward-carry before you return `merge`.** The PR body names
    where a finding that changes a later stage was written; open that
    destination and confirm it is there, carrying the control and stated as a
    precondition (`finding-propagation.md`). A finding that exists only in this
    PR's comments is `blocked <sha> carry-missing: not carried to <stage>`.
11. **A red check owes an answer** (`defect-root-cause.md`'s second
    trigger). Read the PR's own checks — `get_check_runs`, or
    the commit's own `check-runs` API — not the body's account, and never a
    listing that shows one run per check. For each gate check that went red,
    the body names it and answers: the cheaper detector with its standing cost,
    or the finding that none exists. Both pass; silence is
    `blocked <sha> root-cause-unanswered: <check> went red, unanswered`.
    `UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them
    (`ci-autofix.md`). You check that the trigger was answered, not the answer — the analysis is a separate seat, `root-cause.md`.
    **A red `nightly-status` or `delivery-status` is not this pull request's**
    unless its diff reaches what the reporter reads — its script, its job, the
    plan, `HANDOVER.md`, or a delivery row other than the pull request's own
    (`defect-root-cause.md`; the body check voids the exemption then). Both run
    the head's checkout: deleting a merged row turns `delivery-status` OVERDUE.
    The control, re-run at your own base — heads pushed after #713 carry the
    same red, heads pushed before carry none.

    **The head's runs are not the range's** (#1144: a head naming nothing while
    `record-status` sat one commit back). The body check prints `record`/`skip
    red-history` for the range; `skip` means every earlier head UNCHECKED.

    **A GREEN `mutation` does not mean the baseline was green.** Since #1120 the
    lane prints `MUTATION TABLE INCONCLUSIVE` and exits 0 on `--scope changed`
    when its baseline is red, so a green conclusion means either no mutant
    survived or none was evaluated, and only the run's own log separates them.
    A diff that writes no production code line draws no mutant at all
    (`changed_lines`). Where the answer turns on it, read the lane's log
    rather than its conclusion.

12. **Re-read the head before you post.** Name the SHA you measured in the
    verdict, and check it is still the head when you post it. A branch that
    moved under you means some of your numbers describe a tree that no longer
    exists: say which survive and which you re-took, rather than letting the
    verdict imply all of them were taken at the head it names.

    Step 7 is not this check. It compares the SHA in the body against what you
    measured, and a branch that moved after the body was written passes it. This
    one compares the **live head at posting time** against what you measured.

    The handoff makes the head yours from then on, so one that moved under you
    is a broken rule rather than an accident: `blocked <sha> head-moved: measured <sha>, head is <other>`. Re-measuring
    instead is yours to offer and is never owed — a violation the reviewer
    absorbs silently costs the seat that committed it nothing, which is how it recurs.

13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
    DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
    (`claim-files.md`), so every open pull request goes `DIRTY` the moment
    `main` touches a claim file. Confirm before you block:

    ```
    git merge-tree --write-tree origin/main <head>
    ```

    A non-zero exit names the conflicting paths. A conflict on any path other
    than `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`
    is yours to block on, because you cannot know the merged result is correct.

    **The driver's verdict is in that command's stderr. Read it; do not infer it from the paths.** Unlike
    GitHub, `merge-tree` *does* invoke the `claimnotes` driver — measured, one
    invocation per conflicting claim file — but only if you installed it:

    ```
    python3 tests/env_drift.py --install-merge-driver   # once per clone
    ```

    Every path through the driver prints one line: `MERGE-CLAIM: resolved
    <path>` or `MERGE-CLAIM: refused <path>`. Key on that marker, not on the
    wording after it — several distinct checks supply that wording, so a list
    of messages goes stale. A `resolved` line settles that claim file, and a
    non-zero exit alongside it is about some **other** path. A `refused` line
    is the orchestrator's to resolve by hand, not a defect in the authored
    work — say which file refused and why.

    Classifying by line shape instead is what fails. `_comment_lines` and
    `_is_may_drift` both test "everything before `#` is blank", so a
    `may-drift` line **is** a `#` comment, and `merge_claim_defect` refuses
    when one is lost. A rule of the form "a conflict confined to the `#`
    comment notes is merge-prep" therefore waves through a real refusal, on a
    file with no bare claim lines on any side. Why the driver refuses at all is `claim-files.md`'s.

Return a verdict with your RESULT lines, in the exact shape your dispatch
prompt gives: `.claude/workflows/web-fix-wave.js` parses the comment's first
line and routes on it, so one that does not parse is recorded blocked.

**Say which round this is.** From the fourth the fixer owes a re-cut body, not a
repair (`fixer.md`), and blocking one on `claims` again indicts the fix.
