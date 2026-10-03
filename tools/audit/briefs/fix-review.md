# The fix reviewer's contract

You review one fix PR adversarially, in a fresh context, from a worktree at
the PR's head SHA. You are not checking that the code looks right (four fixes
here looked right and were wrong); you are checking that the numbers are real.
**That worktree holds this contract as well as the tree and is frozen by design, so your copy can be arbitrarily old** — and `preflight.sh` warns only before a push a reviewer never makes.
Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/`; empty is current.
Before the fixer's handoff message (`fixer.md`: "the handoff freezes the branch"), prepare against the merge base only, no head measurement; steps 2, 12 govern after. Publish it with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head; it carries your brief's `bus-nonce:`) and report its output in your thread to be confirmed; it posts as `hpo-approver` (decision 0013) -- never as the author App (#1233's defect), never the owner's approving review, which code-owned paths still need.
A long job runs as `fixer.md`'s preamble says, so its exit wakes you.

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
8. **A quoted number you cannot re-derive is not verified — say so.** Re-derive
   under the PR's stated rule before trusting its count; if you cannot, or
   if you had to build your own definition to check it, write that in the verdict rather than reporting a number as confirmed.
9. **When the finding has no committed harness, that is itself a finding**
   (#373's was a `grep` in the issue body, #258's a judge comment). A fixer who builds their own instrument must
   disclose it as their own, not the finder's -- so do you, if you built one.
   Read the judge ruling first: #290's brief prescribes a refused harness.
   A feature's harness is its judge's design: a requirement or on-device measurement it names and neither tests nor tvofi waived is `blocked <sha> harness: design-trace-missing <item>` (#1588).

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

    **Cite CI's heavy runs** (tvofi, 2026-09-30): never re-run the gate or the
    mutation table; cite the head's CI run. Cheap checks (seconds: a lint, one
    test, claims) and your targeted mutants stay yours.

12. **Re-read the head before you post.** Name the SHA you measured in the
    verdict, and check it is still the head when you post it; if it moved, say
    which of your numbers survive and which you re-took.

    Step 7 checks the body's SHA, which a later move passes; this, the **live
    head at posting time**.

    The handoff makes the head yours from then on, so one that moved under you
    is a broken rule rather than an accident: `blocked <sha> head-moved: measured <sha>, head is <other>`. Re-measuring
    instead is yours to offer and is never owed — a violation the reviewer
    absorbs silently costs the seat that committed it nothing, which is how it recurs.

    **A `merge` verdict carries** (#1667) to a head passing `orchestrator.md`
    section 11's carry predicate: no reviewer turn, not `head-moved`. Any other
    main merge returns as its **resolution delta**, which alone you judge;
    any other move is re-reviewed.

13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
    DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
    (`claim-files.md`). Confirm before you block:

    ```
    git merge-tree --write-tree origin/main <head>
    ```

    A non-zero exit names the conflicting paths. A conflict on any path other
    than the two claim files is yours to block on, because you cannot know the
    merged result is correct.

    **The driver's verdict is in that command's stderr; read it, never infer it
    from the paths.** `merge-tree` invokes the driver once per conflicting claim
    file if you installed it (`claim-files.md`). Key on the marker,
    `MERGE-CLAIM: resolved <path>` or `MERGE-CLAIM: refused <path>`, not on the
    wording after it, which several checks supply. A `resolved` line settles
    that file, and a non-zero exit beside it is about another path. A `refused`
    line is the orchestrator's to resolve by hand, not a defect in the authored
    work — say which file refused and why.

    Never classify by line shape: to `_comment_lines` a `may-drift` line **is**
    a `#` comment, and `merge_claim_defect` refuses when one is lost, so "only
    comment notes conflict" waves a real refusal through.

14. **A number the diff moves is earned by the change, not the instrument.**
    Where it moves a `tests/structure_budgets.json` metric, the architecture
    score or its `calibration/expected.json`, the mutation ledger (`killed_by`,
    `survivor_triage`), `tests/closures.json` or the `INERT` list, or a golden
    or claim file: remove the mechanism the body names and show the number
    moves back, and plant at least one gaming attempt of your own against that
    instrument. A movement the removal leaves standing, or one your plant
    reproduces without better code, is `blocked <sha> metric-gamed:
    <instrument>: <how>`. Caught by reviewers planting unasked: junk
    splitting a clone read as score gain for three rounds (#1874); a `killed_by`
    its own lane refuted, and a `tests/entities.py` kill that was the staleness
    check firing on the triage itself (#1867); a quiet autofix beside a read
    `inert_reads` lacked (#1868).

Return a verdict with your RESULT lines, in the exact shape your dispatch
prompt gives: `.claude/workflows/web-fix-wave.js` parses the comment's first
line and routes on it, so one that does not parse is recorded blocked.

**Say which round this is**: from the fourth, `fixer.md` owes a re-cut, not a repair.
