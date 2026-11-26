# BLOCKED: R11-LATE-P1-OPTIONS

Question: `tools/pr/prepr.sh` refuses this head only on a predicted red that the diff does not cause, and I may not work around a refusal. May I hand off at `e1d91dee6065f88c34d192d1688b9c4df4565353` with this refusal answered in the body, or should a seat owning `tools/pr/ci_predict.py` / `tools/audit/seat/bus.sh` fix the replay first?

## State

- Code head `e1d91dee6065f88c34d192d1688b9c4df4565353` (parent of this commit), merge base `dbdc71faea358a95a7b33840ed252b0d8a646a31`. The full PR body is on `refs/heads/handoff-wip/r11-late-p1-options-body` (`BODY.md`).
- Scoped gate at that head: `MODE: SCOPED -- 28 script(s) run, 6 scoped out.`; every `scope.run` script and `run_always` line exits 0, with `tests/stress.py` run alone. `tests/structure.py` passes; `env_drift.py --all` in drift mode shows no unclaimed drift. 18 of 18 mutants are killed.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh BODY.md`: every row ok except `REFUSE ci predict`. The pr-body, figures, carry and unpinned-sites rows pass.

## The refusal

`PREDICT governance / instrument-self-tests STEP REPLAY Show the verdict bus refusing its own fixtures: rc 1 at the head, 0 at the base`, on two consecutive `prepr.sh` runs.

Evidence it is not this diff's:
- The step runs `bash tools/audit/seat/bus.sh --self-test`. The diff does not touch `bus.sh` or anything under `tools/`: `git diff --stat dbdc71faea35...e1d91dee6065 -- tools/` prints nothing.
- Run directly at the head, `bash tools/audit/seat/bus.sh --self-test` exits 0, both bare and under `bash --noprofile --norc -eo pipefail` with `PYTHONPATH=tests/hastub`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base dbdc71faea35 --body BODY.md --record-self-tests` is exactly `prepr.sh`'s step-6d call. Run outside `prepr.sh`, it predicts no governance or instrument red.
- With `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` set to `'2005-04-07T22:13:13 +0000'` (the date `prepr.sh`'s own fixtures pin), `bus.sh --self-test` exits 1 at the head AND at the base. The failing line is the same in both: `FAIL null control: a ref inside the two-hour window is in flight, not an orphan`. That check commits its fixture ref with `commit-tree` and requires it younger than two hours, so any pinned old committer date fails it.
- I could not find where `prepr.sh` leaks such a date into step 6d's environment: both exports I found (lines 2168–2170, 2258–2259) sit inside subshells. Nor why its base replay reads 0. The replay's mechanism inside `prepr.sh` is unresolved.

Seat-comms: `seat_comms.sh` ran without error throughout; no orchestrator command arrived.
