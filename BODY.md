Builds four of the carries the R10-TICK-RESIDUE group holds (13, 15, 10, 9); the rest are not built here and stay open (see Forward-carry).

## Head

0613c67b62b30501d45c7dd5b1275c3c1ff0f95c

## Mutation proof

- carry 13: MUTANTS row plan_cap_unread (beat_jobs_selftest.py) drops the cap pass-through; the check "plan-beat: the overlay's plan_coordinator_cap is handed to replan as --coordinator-cap" goes red. Null control: no key leaves --coordinator-cap out.
- carry 15: `python3 -I tools/audit/seat/remerge_main_selftest.py --mutant` replaces the new exit with `true`; the detached-worktree check fails. Null control: the attached worktree still pushes, exit 0.
- carry 10: with the CAP_NOTICE skip disabled, owed_unactioned --self-test fails; null control: a board with only the cap notice has no key and is not Unreadable.
- carry 9 (helper): with _classify_red returning True unconditionally, orchestrator_tick --self-test fails the carry 9 check; null control: a real RED still reads red.
- carry 9 (wiring, review mutants M3 and M4), new one_pr checks "carry 9 one_pr: WAIT clears the red" (required ["gate"], a gate failure, classify_at stubbed to wait: `_red[77] == []`, no RED-UNOWNED), "RED keeps it (null control)" and "an unread classify keeps it" (classify_at raises mt.Stop: the red stands).
  - M3 (the two one_pr lines clearing `_red[n]` deleted), applied: `308 checks, 1 failed`, `FAIL carry 9 one_pr: WAIT clears the red: _red[77] is []`. Restored: `308 checks, 0 failed`.
  - M4 (`_classify_red` except-branch `return True` flipped to `return False`), applied: `308 checks, 1 failed`, `FAIL carry 9 one_pr: an unread classify keeps it: _red[77] is ['gate']`. Restored: `308 checks, 0 failed`.

## Null control

At the merge base: plan-beat passes no --coordinator-cap; remerge_main.sh exits 0 after a refused push; a cap notice makes the whole owed check UNREADABLE; red-unowned reads the gate conclusion alone.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` (with PYTHONPATH=tests/hastub), `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `python3 -I tools/audit/seat/owed_unactioned.py --self-test`, `python3 -I tools/audit/seat/remerge_main_selftest.py`: all report 0 failed at 0613c67b62b30501d45c7dd5b1275c3c1ff0f95c (orchestrator_tick: 308 checks).

## Red checks

none

## Forward-carry

none

## Roster carries

Not built in this pull request; they stay open as carries of R10-TICK-RESIDUE in dev/programme/rosters/wave-r10-groups.json (unchanged by this diff): carries 0-8 (NOT REVIEWABLE naming, OUTSIDE-CHAIN-IDLE, probe-refused, unrecorded-merge query, repair barrier, postmerge idempotence, OWED opener results, UNDISPATCHED P438, CI-attempt alarm P445), 12, 14, 16, and the roster restorations 17-20 (a roster write this seat may not make). Carry 11 (per-op persistence) already exists on main: the beat self-test has a roster_saved_at_pass_end mutant; not re-verified here. Carry: R10-TICK-RESIDUE

Carry 0: not built in this pull request; stays open on the roster for a later part.
Carry 1: not built in this pull request; stays open on the roster for a later part.
Carry 2: not built in this pull request; stays open on the roster for a later part.
Carry 3: not built in this pull request; stays open on the roster for a later part.
Carry 4: not built in this pull request; stays open on the roster for a later part.
Carry 5: not built in this pull request; stays open on the roster for a later part.
Carry 6: not built in this pull request; stays open on the roster for a later part.
Carry 7: not built in this pull request; stays open on the roster for a later part.
Carry 8: not built in this pull request; stays open on the roster for a later part.
Carry 12: not built in this pull request; stays open on the roster for a later part.
Carry 14: not built in this pull request; stays open on the roster for a later part.
Carry 16: not built in this pull request; stays open on the roster for a later part.
Carry 17: not built in this pull request; stays open on the roster for a later part.
Carry 18: not built in this pull request; stays open on the roster for a later part.
Carry 19: not built in this pull request; stays open on the roster for a later part.
Carry 20: not built in this pull request; stays open on the roster for a later part.
Carry 21: not built in this pull request; stays open on the roster for a later part.
Carries 22, 23, 24, 25, 26, 27, 28 and 29 (Carry 22, Carry 23, Carry 24, Carry 25, Carry 26, Carry 27, Carry 28, Carry 29): part 2 items, out of this part and not built here.
Carry 11: already built on main (roster_saved_at_pass_end mutant); no change here.
Carry 9: built here.
Carry 10: built here.
Carry 13: built here.
Carry 15: built here.
Carry: R10-TICK-RESIDUE

## Friction

none
