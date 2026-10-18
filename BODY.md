Part of #2264 (R10-TICK-ORCH's `fixes` is empty, so no closing keyword). This lands the two arms #2281 left: (a) and (c), plus the code-owned `ROSTER_REF` comment #2281 forward-carried.

(a) `orchestrator_tick.py` reported a required context ABSENT whenever it had no check run at the sha. A job gated on `needs` (`closures` waits on `coverage` in the Tests workflow) has no run until its sibling finishes, so the tick flagged work that was only queued and invited a needless re-dispatch. `Tick.split_absent` now says WAITING (unflagged) when any run at the sha has not completed, and ABSENT (flagged) only once everything has settled. It is applied in both places that said ABSENT, the PRS arm and the MAIN arm. A job that really is missing still flags once the sha is settled. The wait is bounded by the ETA check's own threshold: a run in flight past 2x `critical_path_minutes` (`Tick.stuck`, one reader `Tick.critical_median` shared with the ETA lane check) no longer explains a missing job, and an unreadable median cannot bound it, so both read ABSENT. The first review (blocked at 1c9c0bdf3) found the MAIN arm unpinned and unbounded; both are fixed here.

(c) `git grep -oh "#[0-9]\+"` in the ledger arm was a non-raw string, so Python 3.14 compiled it with a `SyntaxWarning: "\+" is an invalid escape sequence`. It is now `r"#[0-9]\+"`; the regex value is unchanged.

`tests.yml`: only the `ROSTER_REF` comment changed. It now says the beat reads the newest `wave-r<N>-groups.json` through `roster_lib.roster_path`, not the removed `ROSTER_PATH` and the round-9 path. `record_row.py --roster-ref` does resolve through `roster_lib.roster_path`, so the comment is true.

The local branch `fix/orchestrator-tick` (268858e54) held nothing for these arms: `git diff --stat origin/main...fix/orchestrator-tick` printed nothing.

## Head

f8e44e97385bf309f4471d04649b232ac0985ce7

## Mutation proof

Each mutant was applied after the commit, the self-test run, then restored with `git checkout -- .`:
- M1 `split_absent` always returns ABSENT: red on `PRS needs-gated job`, `MAIN needs-gated job` and `split_absent: in flight -> waiting` (3 failed of 100).
- M2 the grep literal restored to non-raw `"#[0-9]\+"`: red on `compile clean` (1 failed, at the earlier head; the line is untouched since).
- M3 the PRS-arm call replaced by `waiting = []`: red on `PRS needs-gated job` (1 failed).
- M4 the MAIN-arm call replaced by `waiting = []` (the reviewer's mutant): red on `MAIN needs-gated job` (1 failed). It was 93/0 before.
- M5 the stuck bound removed: red on both arms' `stuck sibling` cases and `split_absent: stuck -> absent` (5 failed).
- M6 the unreadable-median guard removed: the self-test crashes (`TypeError` on `None`), so it cannot pass.

## Null control

`split_absent` with nothing in flight returns `([], ["closures"])`: with nothing in flight the unmodified behaviour holds and the missing job still flags (self-test case `split_absent: settled -> absent (null control)`). The PRS arm's existing `absent required flagged (14)` case, a settled head with `closures` missing, still passes.

## Figures

Instrument: `python3 tools/audit/seat/orchestrator_tick.py --self-test`: head `100 checks, 0 failed`, run with `-W error`; mutant counts are in the Mutation proof. The reviewer's probe (a mutation lane in progress 10 h, `closures` never queued) is the `MAIN stuck sibling` case: ABSENT flagged. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` printed `Architecture score: dS +0.0000 NULL`. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL` (the diff touches `.github/workflows/tests.yml`, which forces the full suite); heavy scripts are CI's. No golden fixture is in the diff.

## Red checks

none

## Forward-carry

none

## Friction

none
