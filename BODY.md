Part of #2264 (R10-TICK-ORCH's `fixes` is empty, so no closing keyword). This lands the two arms #2281 left: (a) and (c), plus the code-owned `ROSTER_REF` comment #2281 forward-carried.

(a) `orchestrator_tick.py` reported a required context ABSENT whenever it had no check run at the sha. A job gated on `needs` (`closures` waits on `coverage` in the Tests workflow) has no run until its sibling finishes, so the tick flagged work that was only queued and invited a needless re-dispatch. `Tick.split_absent` now says WAITING (unflagged) when any run at the sha has not completed, and ABSENT (flagged) only once everything has settled. It is applied in both places that said ABSENT, the PRS arm and the MAIN arm. A job that really is missing still flags once the sha is settled.

(c) `git grep -oh "#[0-9]\+"` in the ledger arm was a non-raw string, so Python 3.14 compiled it with a `SyntaxWarning: "\+" is an invalid escape sequence`. It is now `r"#[0-9]\+"`; the regex value is unchanged.

`tests.yml`: only the `ROSTER_REF` comment changed. It now says the beat reads the newest `wave-r<N>-groups.json` through `roster_lib.roster_path`, not the removed `ROSTER_PATH` and the round-9 path. `record_row.py --roster-ref` does resolve through `roster_lib.roster_path`, so the comment is true.

The local branch `fix/orchestrator-tick` (268858e54) held nothing for these arms: `git diff --stat origin/main...fix/orchestrator-tick` printed nothing.

## Head

a53ec398537e4f9d68671e91402e95801ef7268c

## Mutation proof

Each mutant was applied after the commit, the self-test run, then restored with `git checkout -- .`:
- M1 `split_absent` always returns ABSENT: `python3 tools/audit/seat/orchestrator_tick.py --self-test` red on `PRS needs-gated job: waiting named, unflagged`, `PRS needs-gated job: not reported ABSENT while a run is in flight` and `split_absent: in flight -> waiting` (3 failed of 93).
- M2 the grep literal restored to non-raw `"#[0-9]\+"`: red on `compile clean: no SyntaxWarning on compile` (1 failed of 93).

## Null control

`split_absent(["closures"], {"c": {"status": "completed"}})` returns `([], ["closures"])`: with nothing in flight the unmodified behaviour holds and the missing job still flags (self-test case `split_absent: settled -> absent (null control)`). The PRS arm's existing `absent required flagged (14)` case, a settled head with `closures` missing, still passes.

## Figures

Instrument: `python3 tools/audit/seat/orchestrator_tick.py --self-test`: head `93 checks, 0 failed`; M1 `93 checks, 3 failed`; M2 `93 checks, 1 failed`. The five new checks are the two PRS cases, the two split_absent cases and the compile case. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` printed `Architecture score: dS +0.0000 NULL`. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL` (the diff touches `.github/workflows/tests.yml`, which forces the full suite); heavy scripts are CI's. No golden fixture is in the diff.

## Red checks

none

## Forward-carry

none

## Friction

none
