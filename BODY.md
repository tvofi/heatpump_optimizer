This lands the measured size model for the round-10 plan: `tools/plan/size_durations.py` re-derives `replan.py`'s duration model (`tools/plan/durations.json`) from the merged pull requests of every done round-10 group (p75 of round-adjusted active hours per size and class, review rounds added back at a Theil-Sen cost, a per-carry slope, a held group priced by its open carries). `replan.py` now starts a started group at the replan instant past the slot cap, records why each group starts when it does, orders ready work by the owner's 2026-10-30 tiers, and draws at the owner's 16 slots and 16 seats unless told otherwise. The plan page (`tools/audit/seat/plan_page.py`) lists every open issue but the tracking issue; one on no open group is listed as unplanned with the groups it was wired to. A mutant harness, self-test arms, a CI step and a closures classification pin the model.

Owning roster group: `R10-PLAN-REAL-DURATIONS` (size M, wave 1, fixer sonnet / reviewer opus, after `R10-PLAN-ARTIFACT` and `R10-ORCH-PLANPAGE`, files `tools/plan/size_durations.py`, `tools/plan/replan.py`, `tools/plan/durations.json`, `tools/audit/seat/plan_page.py`) in `dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster` 5229384ba5337f577728377b76bc1f2be21c0bfd (`git ls-remote origin refs/heads/handoff/audit-r10-roster`). Its resume branch is `handoff/r10-plan-real-durations`. The owner is tvofi.

Round 2 repair of the r1 block `mutation-survivor: theil-sen-ordered-pairs`: `round_slope`'s pair rule `if k2 != k1` could be replaced by `if k2 > k1` with no check failing, because every Theil-Sen fixture listed its rows in ascending x. `size_durations.py --self-test` now holds a row-order arm (the 5.5 h fixture ascending, reversed and shuffled must all give 5.5), and the mutant `theil-sen-ordered-pairs` is in the harness. Each r1 finding is answered: the survivor is killed (Mutation proof); Red checks is re-taken from the PR head branch; the mutant count reads nineteen plus the new one; the ownership paragraph names the roster group.

## Head

Code head measured: 4d624465940b5a4916b7ff3fd3e44b644cd668d1, the PR head 3fd85299d9c2314a3316c1956a97d37a9d95de77 plus one commit (the row-order arm and the mutant). `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so `origin/main` is not merged; `tools/pr/prepr.sh` was run at this head.

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_durations_mutants.py` (twenty one-occurrence replacements in `size_durations.py` plus the M0 null, each run against `--self-test`): M0 prints `rc=0 fails=0 verdict=null`; every named mutant (shared-branch-maps, roster-pointer, merge-commit-pointer, verdict-dedupe, dispatch-stamp-start, active-not-span, not-answered, forward-needs-done, percentile-linear, theil-sen, theil-sen-ordered-pairs, rounds-priced-out, min-cell, monotone-lift, part-capacity-p90, held-open-index, future-groups-only, boilerplate, pnums-subset, forward-overlap) prints `verdict=killed` with `rc=1`, and the last line is `RESULT survived=0`. The count is the `RESULT mutant=` lines less M0: nineteen replacements at the r1 head plus `theil-sen-ordered-pairs` (`k2 != k1` to `k2 > k1`), killed by the row-order arm (reversed rows keep no pair, slope 0 instead of 5.5; shuffled rows give 10). `replan.py --self-test` runs its own mutation table, each `ok self-test fails when ... is deleted`.

## Null control

The unmodified `size_durations.py` (mutant M0) passes with `fails=0`, and the new arm passes on it; `replan.py --self-test`, `size_durations.py --self-test` and `plan_page.py --self-test` all end `0 failed` at this head. At the merge base `tools/plan/size_durations.py` does not exist (`git cat-file -e origin/main:tools/plan/size_durations.py` fails), so the model had no instrument to fail.

## Unpinned sites

n/a: `tools/` sites are pinned by the in-tree mutant harness `dev/audit/harnesses/r10_plan_durations_mutants.py` (above) and `replan.py`'s self-test mutation table.

## Figures

- Mutant verdicts: `python3 dev/audit/harnesses/r10_plan_durations_mutants.py`, counting `verdict=killed` lines against the named mutants; rule: one line per mutant, `survived=` is the last line.
- Self-tests: `python3 tools/plan/size_durations.py --self-test`, `python3 tools/plan/replan.py --self-test`, `python3 tools/audit/seat/plan_page.py --self-test`; each prints its failed count last.
- Ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget moved.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`), run as named (rule: the mode line, not the count).
- Claim files, `VERSION`, manifest and `RELEASE_NOTES.md`: `git diff origin/main...HEAD --name-only | grep -cE 'claimed_drift|VERSION|RELEASE_NOTES|manifest'` prints 0.

## Red checks

none: the PR head branch is `fix/r10-plan-real-durations-pr`; at its head 3fd85299d9c2314a3316c1956a97d37a9d95de77 the check-run listing for pull request 3097 (one page, `total_count` 55) holds 55 runs, none concluding `failure`, `cancelled` or `timed_out` (success or skipped each). This head adds one commit whose checks have not run; a red there is the bot's to repair under `ci-autofix.md`.

## Forward-carry

none

## Friction

none
