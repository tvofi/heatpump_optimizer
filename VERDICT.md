Fix review: merge ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a

bus-nonce: f8eeaf3fe4d4c22a030ca34706a11ee6

Round: third review of PR #2588. This is a re-review at the same head, ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a, after the figure-wrong block from probe rev-2588-566ff789. I ran the instruments from a detached worktree at origin/main 3976515a0, and the roster figures from git objects at B=93e6a63d2 (the merge base) and H=ad10fd21. I read the contract from main. Main changed one item since the merge base: #2561 made wording edits to fix-review.md and orchestrator.md, and neither edit changes a step this review uses. I re-read the head before returning: `fix/audit-r10-roster-pr` is ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a, `handoff/audit-r10-roster` is 306a96d5f21f7876070d48c194fd4be99b64022c (frozen), and the live body is 7379 bytes. The live body is byte-equal to origin/handoff-body/audit-r10-roster 940c524d:BODY.md, apart from one trailing newline that the REST `--jq` read adds (ev/body.md, ev/body_ref.md).

## Findings

- At 93e6a63d2, the body's Forward-carry calls `update_pr.sh` l.42 "the unpushed-worktree refusal". This clause was carried unchanged from the previous body. Line 42 is actually the loop line that skips the train's own worktree and dirty worktrees. The unpushed refusal itself (`pr_refuse ... # mut:unpushed`) is l.43, inside the same 41-45 block (ev/figures.txt). This does not misdirect the fixer, because the bullet tells them to locate the exit by its message text "checked out elsewhere", and that exit is l.46 `exit 1`, both at 93e6a63d2 and at main 3976515a0. The roster carry's own "(l.42)" is therefore wrong, and its fixer should ignore the line number. Carry: R10-FLOW-BODY-ONLY
- The P22 counts (28 entries, 17 / 6 / 5) come from the relay's out-of-tree state. I could not re-derive them, and the body says so. The R10-FLOW-BODY-ONLY fixer owes a re-measurement at their own start. Carry: R10-FLOW-BODY-ONLY
- `brief_lint`'s METRIC_LITERAL_RE matches only the comparator form, so a prose literal lints clean. Carry: dismissed: the rule enforces #411 class 4 as defined, no stage depends on widening it, and this PR adds no such literal (re-stated from the earlier verdicts).

## Evidence

- Block cleared: the carry check figure. I ran `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <live body>`. It prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0, which is exactly what the body says. `--roster-ref ad10fd21` gives the same line (ev/carry.txt). The CI form (`python3 -I tools/audit/carry_audit.py check --body`, run from a worktree at the head, as pr-contract reads the tree's roster) prints the same line, rc 0 (ev/carry_ci_form_head.txt). Run from main's tree, that form reports R10-FLOW-BODY-ONLY as a bad destination, which is expected: this PR is what adds the group (ev/carry_ci_form.txt).
- The sweep line matches its stated command. `... sweep` prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` and then `CARRY-SWEEP: 0 pull request(s), 0 other unowned finding(s)`. The body quotes the CARRY-SWEEP line up to `0 pull request(s)`, which is a correct prefix.
- The body edit is limited to the two lines named in the brief (ev/body_delta.txt, previous body against live body): the Carry-routing figure and the P22 Forward-carry bullet. The P22 bullet now locates the exit by its message text, says it is `exit 1` at :46 and that 75 is P22's prescription, and says its counts are out-of-tree and re-measured by the fixer. All three requirements are met. The previous verdict's finding on "the 75 exit at :46" is settled by this wording.
- policy_lint with pr-contract's arguments, run from main's program: `--pr-body <live body> --head ad10fd21... --title <live title> --author hpo-author[bot] --paths-file (2 paths) --existing-file (1 path) --red nightly-status`. It prints `PR-BODY: 0 error(s)`, rc 0, and `record red-history: 129 commit(s) ... every failure conclusion across them: nightly-status` (ev/policy_lint.txt). figure_lint prints `FIGURES: 5 resolved, 2 not verified, 0 refused`, rc 0. The 2 not verified are `git show` lines, whose flags the linter does not check (ev/figure_lint.txt).
- Every figure re-derived at this head (ev/figures.txt):
  - Groups: 108 at the base, 144 at the head. The jq program prints `{"new":36,"removed":0,"changed":30}`.
  - Null control: `git diff --exit-code origin/main 93e6a63d2 -- <roster>` gives rc 0 against both the merge base and current main, because #2561 does not touch the roster.
  - The roster is byte-identical between handoff/audit-r10-roster and the head (rc 0).
  - The head's parents are 23cc013fa and 93e6a63d2, as the body says.
  - plan_table prints `8 wave(s)` at main and at the head. The critical paths match the body: main's starts R10-ADVISOR -> R10-SCORES, the head's starts R10-NIGHT-FOLDS -> R10-LOOP-CPU, and the last six nodes are identical.
  - I did not re-run the remaining roster figures: the new-group names, the by-field breakdown and the stage commits. The previous verdict re-derived them at this same head, and no roster byte has changed since.
- Merge with main: `git merge-tree --write-tree origin/main ad10fd21` against main 3976515a0 gives rc 0, tree 5c47fcb1c. Clean, with no claim-file conflict.
- Red checks (check-runs API per commit; ev/checks_*.tsv). At ad10fd21 there are 55 runs, all completed: 33 success, 20 skipped, 1 neutral (CodeQL), 1 failure.
  - The failure is `nightly-status`. It grades main, and this diff (the roster and delivery/2588.md) does not reach what it reads. The body names and answers it, so no root-cause answer is owed.
  - pr-contract ran four times: 01:22, 01:29, 01:39 and 02:39Z. All four succeeded, and the 02:39 run started after the body edit and after the only red had concluded.
  - The body's "both pr-contract runs" and its "in_progress" reading of closures, env-matrix and instrument-self-tests are a dated earlier read. All three have since concluded success.
  - The intermediate commits 23cc013fa and 306a96d5f have 0 check-runs each.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched. The diff is two paths. No claim file or golden changed, so env_drift does not apply. The mutation proof is n/a (roster state only), as the body says.
- Every Carry in this verdict names R10-FLOW-BODY-ONLY. That group is `not-started` at the head and on the handoff roster, so it is live.
- I built no instrument of my own beyond the commands printed in the body and the grep/awk reads of update_pr.sh.
