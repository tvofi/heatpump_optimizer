# The fix reviewer's contract

You review one fix PR adversarially, fresh, from a worktree at
the PR's head SHA. You check that the numbers are real, not that the code looks right.
**Its copy of this contract is frozen with the tree, so can be old**; start from the dispatch's `review-packet:`, whose check digest is as rendered: re-read live checks before a verdict.
Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`; empty is current.
Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head) and report its output to be confirmed; a cloud seat, with no `push-verdict`, commits `cloud_relay.sh`'s verdict file and `ev/` in one commit, subject `verdict <pr> <head40>`, to a fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`. Evidence names differ beyond case. First line: `Fix review: merge <head40>` or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+`, then your brief's `bus-nonce: <nonce>`.
**Block only on code, tests and harness** (C5): paperwork (a stale body, a carry route, a figure, a root-cause answer) is a `Note: <class>: <text>` line under `merge`; one on `custom_components/` blocks. `bus.sh post` refuses `merge` at a red (C8). It posts as `hpo-approver` (0013), never the author App (#1233) or the owner's review.
Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between rounds through refs, never mid-review, by ~150 k tokens.

1. Re-run the mutation proof: delete the production line(s) the PR names,
   run the closure, confirm the named checks fail, restore. If nothing fails,
   it is vacuous: `blocked <sha> mutation-vacuous: <mutants>`: every
   survivor your driver run at that head reports, which `push-verdict` reads in
   your evidence (`survivor_list.py`, tvofi 2026-11-07).
2. Measure with the **finder's** harness, not the fixer's: at the baseline
   SHA and at the PR head, printing your own `RESULT` lines. One flat by
   design (`fixer.md` step 3): confirm it flat at both ends, and run
   its companion yourself at both.
3. Re-run the null control and the both-ends check where the PR claims one.
4. Compare the claim files with the actual drift: run `env_drift.py --all`
   (`card_drift.mjs` for a card) against the merge base; every
   moved fixture is claimed and every claim moved.
5. Check `VERSION`, the manifest version and the notes heading are untouched.
6. Attack the fix at other configurations the finding's harness accepts:
   the other topologies, the other price profiles, the zero-evidence install.
   **And open the class: a harness's configurations are its parameters, not its
   population.** Run the enumeration rule the body names and compare its output to
   the diff: a seam it returns that is neither in the diff nor dispositioned in the body
   is `blocked <sha> class-open: <seams>`, a site or a predicate's unguarded
   domain: every one the review found, not one per round, no hunt past it owed.
   An item whose harness does not move under its own perturbation is void
   (`judge.md`). A body whose issue states more than one seam and names no rule is `blocked <sha> harness: class-rule-missing`. A rule returning
   nothing means a one-seam class: say so, never read the absence as compliance.
7. Confirm the PR body's head SHA is the head you measured (handoff review: the handoff tip), or `--carry`s to it.
8. **A quoted number you cannot re-derive is not verified: say so.** Re-derive
   under the PR's stated rule before trusting its count; if you cannot, or
   had to build your own definition, write that in the verdict.
9. **When the finding has no committed harness, that is itself a finding**.
   An instrument you or the fixer built is disclosed as the builder's, not the
   finder's; one rebuilt from an out-of-tree copy is named and lands (`fixer.md` 18).
   A feature's harness is its judge's design: a requirement or on-device measurement it names and neither tests nor tvofi waived is `blocked <sha> harness: design-trace-missing <item>` (#1588).

10. **Check the forward-carry before you return `merge`.** The PR body names
    where a finding changing a later stage was written; open it (a roster
    carry at the body's `handoff/audit-r<N>-roster` SHA) and confirm it states
    its control as a precondition (`finding-propagation.md`). One only
    in this PR's comments is `Note: carry-missing: not carried to <stage>`.
    An own-group `Carry:` naming neither `fixer.md` exception is
    `blocked <sha> carry-missing: own-group`.
11. **A red check owes an answer** (`defect-root-cause.md`'s second
    trigger). Read the PR's own checks (`get_check_runs`, or
    the commit's `check-runs` API), not the body's account, and never a
    listing that shows one run per check. For each required check that went red,
    the body names it and answers: the cheaper detector with its standing cost,
    or the finding that none exists. Both pass; silence is a `Note:` line, never
    a block (C5): root-cause-detectable where a cheaper detector could have shown
    the red before the handoff (name it), `root-cause-unrecorded` where that check
    is the cheapest, `root-cause-unanswered` if you cannot tell. The wave routes
    an old `blocked <sha> root-cause-detectable: <check>`.
    `UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them
    (`ci-autofix.md`). You check that the trigger was answered, not the answer (`root-cause.md`'s).
    **A red outside `merge_train.py owed-reds`' set (`nightly-status`) is not this pull request's**
    and blocks nothing, except an `instrument-self-tests` step red at the head and
    not the merge base (`classify --pr`'s INTRODUCED): its finding, a block.

    **The head's runs are not the range's** (#1144). The body check prints
    `record`/`skip red-history` for the range; `skip` means every earlier head
    UNCHECKED.

    **A GREEN `mutation` may have evaluated nothing**: on `--scope changed` a red
    baseline prints `MUTATION TABLE INCONCLUSIVE` and exits 0 (#1120), and a diff
    writing no production code line draws no mutant (`changed_lines`). Where the answer turns on it, read the lane's log.

    **Cite CI's heavy runs** (tvofi, 2026-09-30): never re-run the gate or the
    mutation table. Cheap checks (seconds: a lint, one
    test, claims) and your targeted mutants stay yours.

12. **Re-read the head before you post.** Check the SHA your verdict names is
    still the head as you post it; if it moved, say which of your numbers
    survive and which you re-took.

    **A `merge` verdict attaches to the head its first line names and carries
    to any later head whose own diff is unchanged** (C4; #1667):
    `tools/audit/seat/review_carry.py <verdicted> <new>` prints `CARRY`
    (`app_approve.sh --carry`: git-resolved main merges, unioned claim files),
    and `bus.sh dispatch` refuses a second reviewer. A red never carries.
    Else a later round is **its delta** (tvofi 2026-11-09): `git diff <reviewed-head>
    <head>` (a main merge: its resolution), each prior finding resolved, the live
    required checks. Only a production (`custom_components/`) delta putting reviewed
    functionality at a non-obvious risk CI would not detect widens it, to exactly
    that code; the verdict names path and risk. Instrument, test, policy and body
    deltas never widen it.
    A head whose own diff moved under you is `blocked <sha> head-moved: measured <sha>, head is <other>`.

13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
    DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
    (`claim-files.md`). Confirm before you block:
    `git merge-tree --write-tree origin/main <head>`; a non-zero exit names the conflicting paths. Block on main only on one,
    never on a head behind main that merges cleanly (tvofi 11-07). A
    conflict off the two claim files is yours.

    **The driver's verdict is in that command's stderr; read it, never infer it
    from the paths.** `merge-tree` invokes the driver once per conflicting claim
    file if you installed it (`claim-files.md`). Key on the marker,
    `MERGE-CLAIM: resolved|refused <path>`, not on the
    wording after it. A `resolved` line settles
    that file; a non-zero exit beside it is another path's. A `refused`
    line is the orchestrator's to resolve by hand, not the author's defect: say
    which file refused and why.

    Never classify by line shape: to `_comment_lines` a `may-drift` line **is**
    a `#` comment, and `merge_claim_defect` refuses losing one, so "only
    comment notes conflict" waves a real refusal through.

14. **Every number the diff moves is earned by the change, not the instrument**:
    a structure, policy or mutation budget, the architecture score or its
    `calibration/expected.json`, the mutation ledger, `tests/closures.json` or
    `INERT`, a golden or claim file, any figure the body quotes. Remove the
    mechanism the body names; a movement that survives is not earned:
    `blocked <sha> metric-gamed: <instrument>: <how>`. Then plant the diff's own
    kind of move on the same instrument with nothing improved, and on its
    neighbouring rules, not only the counter's own re-spelled. If it reproduces
    the movement, block only where the diff's change is that shape; under a sound
    change it is an instrument finding, carried by `finding-propagation.md`. On a raise, judge each listed payment and
    hunt one it missed: one that truly improves the code is `metric-gamed` too.
15. **Judge `fixer.md` step 17 on added lines**: a breach, or a departure
    from the architect or approved design note, is `blocked <sha> architecture-unsound: <how>`.

Return a verdict with your RESULT lines, its first line and `bus-nonce:` line
in the grammar above; one that does not parse is refused. Before you return one, run the packet's closing self-audit (`carry_audit.py check`); return it only at rc 0.

**Say which round this is**: from the fourth, `fixer.md` owes a re-cut.

