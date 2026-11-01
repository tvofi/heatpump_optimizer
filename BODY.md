This lands the measured size model for the round-10 plan: `tools/plan/size_durations.py` re-derives `replan.py`'s duration model (`tools/plan/durations.json`) from the merged pull requests of every done round-10 group (p75 of round-adjusted active hours per size and class, review rounds added back at a Theil-Sen cost, a per-carry slope, a held group priced by its open carries). `replan.py` now starts a started group at the replan instant past the slot cap, records why each group starts when it does, orders ready work by the owner's 2026-10-30 tiers, and draws at the owner's 16 slots and 16 seats unless told otherwise. The plan page (`tools/audit/seat/plan_page.py`) lists every open issue but the tracking issue; one on no open group is listed as unplanned with the groups it was wired to. A mutant harness, self-test arms, a CI step and a closures classification pin the model.

Owning roster group (wave-r10-groups.json at `handoff/audit-r10-roster`): none fits exactly. Nearest are `R10-PLAN-ARTIFACT` (M, resume `done`, `handoff/r10-plan-artifact`, fixer opus; it owns `tools/plan/replan.py` and the plan page build) and `R10-ORCH-PLANPAGE` (M, `done`, opus; `plan_page.py`, and this diff's mutant harness names it). Both are done, so adding to either reopens finished work. `R10-FLOW-TOOLKIT-MODEL` (M, `not-started`, sonnet, issues 2438/2715) extends the plan model with `--project`, `--rank` and a shadow overlay, a different scope from measuring durations, so it does not own this either. Proposal, nothing written to the roster: a new group `R10-PLAN-REAL-DURATIONS`, size M, after `R10-PLAN-ARTIFACT` and `R10-ORCH-PLANPAGE`, models fixer sonnet / reviewer opus, files `tools/plan/size_durations.py`, `tools/plan/replan.py`, `tools/plan/durations.json`, `tools/audit/seat/plan_page.py`. The owner (tvofi) decides.

## Head

Code head measured: dcc49953a3a0169012a3c26948c1aa37b3293bd6, the merge of origin/main (c3b7c964f) into the seat's earlier head 12ec432331829ede505229b6231425b02ab4daba. The merge resolved three conflicts in `tools/plan/replan.py` self-test fixtures (main added `round_n`, the handoff added the started-work and cap fixtures) and added `round_n=2` to seven `build_plan` calls in `selftest_model`. A later move of main needs a fresh merge.

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_durations_mutants.py` (twenty one-occurrence replacements in `size_durations.py`, each run against `--self-test`): M0 prints `rc=0 fails=0 verdict=null`; every named mutant (shared-branch-maps, roster-pointer, merge-commit-pointer, verdict-dedupe, dispatch-stamp-start, active-not-span, not-answered, forward-needs-done, percentile-linear, theil-sen, rounds-priced-out, min-cell, monotone-lift, part-capacity-p90, held-open-index, future-groups-only, boilerplate, pnums-subset, forward-overlap) prints `verdict=killed` with `rc=1`, and the last line is `RESULT survived=0`. `replan.py --self-test` runs its own mutation table (freshness, gate-cancellation and others), each `ok self-test fails when ... is deleted`.

## Null control

The unmodified `size_durations.py` (mutant M0) passes with `fails=0`; `replan.py --self-test`, `size_durations.py --self-test` and `plan_page.py --self-test` all end `0 failed` at this head. At the merge base `tools/plan/size_durations.py` does not exist (`git cat-file -e origin/main:tools/plan/size_durations.py` fails), so the model had no instrument to fail.

## Unpinned sites

n/a: `tools/` sites are pinned by the in-tree mutant harness `dev/audit/harnesses/r10_plan_durations_mutants.py` (above) and `replan.py`'s self-test mutation table.

## Figures

- Mutant verdicts: `python3 dev/audit/harnesses/r10_plan_durations_mutants.py`, counting `verdict=killed` lines against the named mutants; rule: one line per mutant, `survived=` is the last line.
- Self-tests: `python3 tools/plan/size_durations.py --self-test`, `python3 tools/plan/replan.py --self-test`, `python3 tools/audit/seat/plan_page.py --self-test`; each prints its failed count last.
- Ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget moved.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`), run as named.
- Claim files, `VERSION`, manifest and `RELEASE_NOTES.md`: `git diff origin/main...HEAD --name-only | grep -cE 'claimed_drift|VERSION|RELEASE_NOTES|manifest'` prints 0.

## Red checks

none: no workflow run exists for `handoff/r10-plan-real-durations` (the actions listing for that branch returned `total_count` 0 across all pages), so no check has concluded red at this head.

## Forward-carry

none

## Friction

none
