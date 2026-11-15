Round-10 closure record, follow-up to #3601 (R10-CLOSEOUT-CLEANUP, closure runbook step 9 repeated at today's state): re-lands the round-10 roster on main at the roster branch's tip, retargets the bare citations that tip and the passing hours brought back, refreshes the four round-10 state documents, and updates `dev/programme/HANDOVER.md`. The closeout dry plan at #3601's merge (`29b3e5a74c`) printed `step in-main: BLOCKED` on one line, `handoff/r10-arch-docs-delta is cited bare by dev/programme/rosters/wave-r10-groups.json; retarget it to archive/handoff/r10-arch-docs-delta`, and the roster branch had moved since #3601 took it at `00e3c2f8c0`. It closes nothing by keyword and leaves #3394 open.

## Summary

- **Roster.** The head merges `handoff/audit-r10-roster` at `f8d3342d50d1651c197d8e157bbfa8ce3daab302` into `origin/main` and takes the branch's blob for `dev/programme/rosters/wave-r10-groups.json`. Since `00e3c2f8c0` the branch re-wired #201 to R10-CATALOG-PR (after #3553 deleted `dev/programme/carries/carry-201.json`), folded carries for #3575, #3553, #3521, the playbook round-start pull request (#3600) and draw-map part B, and `roster_sync` derived stages from the merged pull requests (R10-PLAYBOOK-ROUND-START is `done` at #3600's merge). `main_only_roster_delta.py` against the final head (after the retarget re-applied #3601's `archive/` prefixes, which the blob copy drops) printed:

~~~text
R11-INTAKE-R10-RESIDUE.carry: main changed it; result DROPPED  main='["From r10-ci-priority-pause, body item d76fe7a3: Carry 9 (item 7bd3e57f), name the process sending `@tvofi` cancels at live heads, then land P267\'s bounded pau'  result='["From r10-ci-priority-pause, body item d76fe7a3: Carry 9 (item 7bd3e57f), name the process sending `@tvofi` cancels at live heads, then land P267\'s bounded pau'
~~~

  That line is field granularity, not a loss: main's two changes to R11-INTAKE-R10-RESIDUE's `carry` since `00e3c2f8c0` (carries 66 and 72, each an inserted `archive/`) are both present verbatim at the head, at indices 66 and 72 (checked element-wise: base, main and head lists hold 175, 175 and 183 carries); the field differs because the branch dropped and appended carries there since `00e3c2f8c0`. A trial build at roster `da51ce1c30` also printed `R10-PROCESS-SLIM.resume: main changed it; result DROPPED` for #3601's `archive/handoff/r10-process-slim-p2`, which the blob copy drops and closeout no longer names while that ref's tip is young; this head re-applies main's own prefix (`main_archive_lines.py` in the closure runbook directory lists refs main cites only as `archive/<ref>` that the head cites bare, and `retarget.py` rewrites them), so that line is gone. No line names R10-CATALOG-PR.

- **Bare citations.** `retarget.py` (closure runbook directory, the handoff's prototype inventory) rewrote each citation `closeout.py` step 1 names to its `archive/` tag, applied to `wave-r10-groups.json` and `wave-r9-groups.json` until a dry pass printed no `cited bare` line. The count is mostly #3601's own retargets, which the blob copy drops and the pass re-applies; the new ones are `handoff/r10-arch-docs-delta`, kept by the six-hour age rule at #3601's last dry pass, and `handoff/r10-hotfix-carry-tip-sigpipe` and `handoff/r10-draw-map-evidence`, whose tips aged past six hours between this build's passes (hence five dry passes and four retarget commits). Before the dry passes every head was fetched, so no ref was kept for an unreadable tip age. Review the roster diff with `git diff --word-diff-regex='[^ ]+' 29b3e5a74c HEAD -- dev/programme/rosters/`: it should be the branch's own edits since `00e3c2f8c0` plus `archive/` prefixes.
- **State docs.** `python3 tools/audit/seat/state_docs.py --roster-ref origin/handoff/audit-r10-roster --mirror dev/programme/round10/state` regenerated `PLAN-TABLE.md`, `FLOW-BOARD.md`, `RESUME-CURRENT.md` and `NEXT-SESSION-PROMPT.md`.
- **Handover.** `updated-for:` names `29b3e5a74cbb30474120c84a27b4e6130f6346bc`, the merge of #3601: #3599 (R10-HOTFIX-REFERENCE-BASIS), the last gating item, was still open at head `b58c6ca368` when this seat's 45-minute wait for it ended (01:21Z), and the handover says so. The update: #3553 merged as `a72ae19952` (five carry files deleted, their entries re-homed as carries, #201 re-wired); #3575 merged as `4eea986a62` (decision 0018 and the evaluator contract; `corpus_tokens` raised 68618 to 69333 under the mandate), the first of the four pre-round-11 items; #3600 merged second, as `2a257fce08`, while this pull request was built; #3491 and #3451 still in review; #3601 merged as `29b3e5a74c` and why this follow-up exists; #3599 still unmerged, with why its first-round merge verdict (probe `94f29ddb`) was never posted and the delta review of the pin commit that returned merge (probe `996b06f9`); the honest-starts state (handoff verdict `blocked architecture-unsound`, design amendment `a63a2ca6cd` approved, PR #3602 open, ruling c1 still the owner's with the reviewer's fixture measurement); the repair fixers out on #3598 and #3593; draw-map part B handed off at `8c1508d9c1`; four friction families with their cures; and the bare-citation trap sharpened by tonight's instance. Stale sentences these facts contradicted were corrected in place (the #201 wire, `verdict/3553`'s findings, the re-routed rows for #3451, #3491, #3553, #3593, #3598, the playbook and honest starts).

## Head

`455c4733f34374ee8469d08355e93297a46ce27e`. Commits on `origin/main` `29b3e5a74c`: the roster landing at `f8d3342d50`, the state docs, 4 retarget commit(s), the handover. Read the diff three-dot.

## Mutation proof

n/a: record files only (roster, state docs, handover); no production, test or instrument code.

## Null control

Keyed on the `group` field (measured at this head), main's roster holds 544 groups and this head's 544: 0 added, 0 removed, so the landing drops no group. 11 of main's groups differ at the head (the branch's edits since `00e3c2f8c0`); a vacuous keying would print 0 changed. The retarget only rewrites citation text: `retarget.py` printed `json parses; dump round-trip identical` for both rosters on every pass.

## Figures

- `cited bare` lines at the first dry pass over the landed roster: `286`; after the last pass: `0` (`grep -c "cited bare"` over the output of `python3 tools/audit/seat/closeout.py --checkout <head worktree> --main <head> --roster-file <roster at f8d3342d50> --repo tvofi/heatpump_optimizer --report-dir <dir> --seats-root /nonexistent --orch-root /nonexistent --verdicts-drained --successor 3394`, dry, after `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`).
- The last dry pass prints `step in-main: ok` and `step issues: BLOCKED` (`1 open issue(s) beyond the successor #3394 await a disposition, first #2728`), with no `brief_lint refuses` line.
- The closeout dry plan at `29b3e5a74c` (before this pull request) printed `step in-main: BLOCKED` with the one bare citation quoted above.
<!-- figure-block: scope-line mb=2a257fce0895e9e1a77d049f879adac438517c3a head=455c4733f34374ee8469d08355e93297a46ce27e -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

- `tools/audit/seat/prune_refs.py` `tip_ages` reads 500 tips per `git log --no-walk=unsorted`, which exits 128 and prints nothing when any one sha is missing from the checkout (reproduced: `git log --no-walk=unsorted --format='%H %ct' <good> 1111111111111111111111111111111111111111 <good>` prints only `fatal: bad object`), so one unfetched tip leaves its whole batch unread and `classify` keeps every ref in it as `keep-young-tip`; a dry closeout pass of this record read `keep-young-tip=698` against 207 one pass earlier, which hides bare citations from `step in-main`. Cure used here: fetch every head before each dry pass. The fix reads ages per sha or drops the missing shas before the batch call, with a self-test arm holding one missing sha. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
