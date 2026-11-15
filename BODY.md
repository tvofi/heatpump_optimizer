Round-10 closure record 3, follow-up to #3601 and #3604 (R10-CLOSEOUT-CLEANUP, closure runbook step 9 repeated after the v10.0.0 stamp): re-lands the round-10 roster on main at the roster branch's tip, retargets the four bare citations the closeout dry plan at the stamp (`13cbe48de4`) names, refreshes the four round-10 state documents, and updates `dev/programme/HANDOVER.md` in place. The dry plan printed `step in-main: BLOCKED` on `handoff/r10-cop-learner-draw-floor`, `handoff/r10-hotfix-main-selftest-scope-2`, `handoff/r10-hotfix-reference-basis` and `review/3481`, each `is cited bare by dev/programme/rosters/wave-r10-groups.json; retarget it to archive/<ref>`, and the roster branch had moved since #3604 took it at `f8d3342d50`. It closes nothing by keyword and leaves #3394 open.

## Summary

- **Roster.** The head merges `handoff/audit-r10-roster` at `89acffb1abf6276cc58d18b36907aa81f0b8b20d` into `origin/main` and takes the branch's blob for `dev/programme/rosters/wave-r10-groups.json`. Since `f8d3342d50` the branch added one carry on R11-INTAKE-R10-RESIDUE (item `ca87a555`, from the self-test scope re-record 3) and `roster_sync` stage edits from the merged pull requests. `main_only_roster_delta.py` against the final head (after the retarget re-applied #3601's and #3604's `archive/` prefixes, which the blob copy drops) printed:

~~~text
R10-REVIEW-DISPATCH-RESIDUE.carry: main changed it; result DROPPED  main="['Moved from R10-FLY-STANDING-CONTRACTS carry 18 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dis"  result="['Moved from R10-FLY-STANDING-CONTRACTS carry 18 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dis"
R11-INTAKE-R10-RESIDUE.carry: main changed it; result DROPPED  main='["From r10-ci-priority-pause, body item d76fe7a3: Carry 9 (item 7bd3e57f), name the process sending `@tvofi` cancels at live heads, then land P267\'s bounded pau'  result='["From r10-ci-priority-pause, body item d76fe7a3: Carry 9 (item 7bd3e57f), name the process sending `@tvofi` cancels at live heads, then land P267\'s bounded pau'
~~~

  Both lines are field granularity, not a loss, checked element-wise by group and carry index (base `f8d3342d50`, main and head): R10-REVIEW-DISPATCH-RESIDUE holds 33, 33 and 33 carries; main's six changes since the base (carries 5, 14, 17, 20, 30 and 31, each an inserted `archive/`) are present verbatim at the head at the same indices, except carry 30, whose head text is main's plus one more `archive/`, on `review/3481`, which is this pass's own retarget. R11-INTAKE-R10-RESIDUE holds 183, 183 and 185 carries; main's two changes (carries 66 and 72) are present verbatim at the head at indices 66 and 72, and the field differs because the roster branch appended two carries since the base (indices 183 and 184: the digest check beside `REFERENCE_BASIS` from #3599's body, and item `ca87a555`). The other 334 of the 336 main-side changes print `result KEEPS` (R10-CATALOG-PR's carry among them), and neither DROPPED line names R10-CATALOG-PR.

- **Bare citations.** `retarget.py` (closure runbook directory, the handoff's prototype inventory) rewrote each citation `closeout.py` step 1 names to its `archive/` tag, applied to `wave-r10-groups.json` and `wave-r9-groups.json` until a dry pass printed no `cited bare` line (4 dry passes). The dry command is the closeout dry plan's (`--seats-root ~/hpo-seats --seats-root ~/.local/state/hpo/pr`, `--orch-root <orchestrator state root>/NO-SCRATCH-CLEAR-r10`, a path that does not exist, so a scratch clear cannot run), pointed at this worktree's roster with `--roster-file`. Every head was fetched before each pass (`git fetch origin '+refs/heads/*:refs/remotes/origin/*'`), so no ref was kept for an unreadable tip age. The roster cites `archive/handoff/r10-process-slim-p2`, a ref that is still a live handoff (a merge-repair of #3451 awaiting a delta review at `c314960799`): main already cited it as the tag after #3604, and `main_archive_lines.py` keeps that retarget when the blob copy drops it. The tag exists only after the closeout's pass A, so until then the roster and the handover name the `archive/` form of a ref a resumer finds at `handoff/`; it resolves at pass A, as every retarget in closure runbook step 9 does. Review the roster diff with `git diff --word-diff-regex='[^ ]+' 946eb6d255 HEAD -- dev/programme/rosters/`: it should be the branch's own edits since `f8d3342d50` plus `archive/` prefixes.
- **State docs.** `python3 tools/audit/seat/state_docs.py --roster-ref origin/handoff/audit-r10-roster --mirror dev/programme/round10/state` regenerated `PLAN-TABLE.md`, `FLOW-BOARD.md`, `RESUME-CURRENT.md` and `NEXT-SESSION-PROMPT.md`.
- **Handover.** `updated-for:` names the stamp commit `13cbe48de4236b7979c754640cc5b1a099ef7475`, reachable from this head. The sentences that were true before the stamp are corrected to what `git` and `gh pr view` read now: v10.0.0 stamped at `13cbe48de4`; #3599 merged as `57fa260451`; #3491 as `099d4fa3f2`; #3604 as `946eb6d255`; #3605 (delivery rows) as `2d0b1c7594`; #3451 open and CONFLICTING at its merge-verdict head `7f4a9be89c`, with the merge-repair handoff `c314960799` awaiting a delta review; #3606 open in review; the open non-gating pull requests routed to round 11 if unmerged at the handover (#3602, #3598, #3593, #3521, #3551, #3566); the delta re-read section for #3491 and #3451; the rows for #3451, #3491, #3593, #3598 and #3602 stripped of "when this file was written" seat state; and the bare-citation trap's third instance. No volatile seat state was added (`writing-for-agents.md`).

## Head

`baa98dc85f042238f104bb19402b25fce50baedc`. Commits on `origin/main` `13cbe48de4`: the roster landing at `89acffb1ab`, the state docs, 2 retarget commit(s), the handover. Read the diff three-dot.

## Mutation proof

n/a: record files only (roster, state docs, handover); no production, test or instrument code.

## Null control

Keyed on the `group` field (measured at this head), main's roster holds 544 groups and this head's 544: 0 added, 0 removed, so the landing drops no group. 6 of main's groups differ at the head (the branch's edits since `f8d3342d50`); a vacuous keying would print 0 changed. The retarget only rewrites citation text: `retarget.py` printed `json parses; dump round-trip identical` for both rosters on every pass.

## Figures

- `cited bare` lines at the first dry pass over the landed roster: `292`; after the last pass: `0` (`grep -c "cited bare"` over the output of `python3 tools/audit/seat/closeout.py --repo tvofi/heatpump_optimizer --checkout <head worktree> --main <head> --roster-file <head worktree>/dev/programme/rosters/wave-r10-groups.json --report-dir <dir> --seats-root ~/hpo-seats --seats-root ~/.local/state/hpo/pr --orch-root <orchestrator state root>/NO-SCRATCH-CLEAR-r10 --verdicts-drained --successor 3394`, dry, after `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`).
- The last dry pass prints `step in-main: ok` and `step issues: BLOCKED` (`1 open issue(s) beyond the successor #3394 await a disposition, first #2728``, with no `brief_lint refuses` line.
- The closeout dry plan at the stamp (before this pull request) printed `step in-main: BLOCKED` with the four bare citations quoted above.
<!-- figure-block: scope-line mb=13cbe48de4236b7979c754640cc5b1a099ef7475 head=baa98dc85f042238f104bb19402b25fce50baedc -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

- `closeout.py` step 1 refuses a roster that cites a ref the plan is about to delete, and the rewrite is a file rewrite the roster gate refuses on the roster branch, so every ref the plan newly names after a record merges costs another record pull request (#3601, #3604 and this one: one, then four bare citations at the stamp's dry plan). The `retarget` arm in `closeout.py` that removes the pull request is already owed in the handover's local prototype inventory (the owner's 2026-11-13 rule: prototype locally in-round, file the permanent fix for round-end consolidation), so it is not a new carry. Carry: dismissed: the same proposal is already recorded in `dev/programme/HANDOVER.md`'s "Local prototype inventory" and goes to round-end consolidation

## Friction

none
