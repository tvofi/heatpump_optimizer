fix(train): re-run an infra-only red main once; dispatch refuses an unreviewable head (R10-FLOW-MAIN-GATE carries)

R10-FLOW-MAIN-GATE's code landed in #2584; the group sits at `carries-open` with two carries, and this pull request builds both.

1. **V142, triage s6-batch45 P228: re-run a rate-limited red main once.** `merge_train.py`'s `main_green` now calls `Train.infra_rerun` in both arms: the `--overlap` log-only read and the blocking wait. For each red required context it reads the context's workflow run (`RUN_URL` on its `details_url`). A run qualifies only at attempt 1, and only when the pure decision `infra_due` accepts it:
   - Every failed job other than `gate` has a log containing one of `INFRA_STRINGS`.
   - The failed `gate` either printed `RATE-LIMITED reset_epoch=`, or its reasons qualify. `gate_outcome` reads the reasons, runner timestamps stripped: the text after `FAIL ` on the outcome line, then each line up to the `##[error]` line. They are read as a set, and each must be `<job>: failure (this run)` naming one of those matching jobs.

   A qualifying run is re-run once with `POST .../rerun-failed-jobs` and logged `INFRA-RERUN <ctx> run <id> attempt 1 (<matched>)`. The POST is never sent before the largest printed `reset_epoch`. With no epoch printed, the due time is `INFRA_WAIT_SECONDS` (3600) after the last matching job completed; until then the arm logs `INFRA-RED <ctx> run <id>: rate-limited, re-run due at <UTC>` and the red stands. In the blocking arm the train sleeps one `POLL_SECONDS` after a re-run and waits once more. The attempt counter is the only bound, and nothing is kept. Any unreadable read, any other failure shape, or any other attempt leaves today's behaviour. `Train` gains an injectable wall clock (`wall=time.time`), because `clock` is monotonic and a reset_epoch is wall time.
2. **Carry b87aa9e4 (#2577): the reviewer-refusal arm.** `bus.sh dispatch` now asks `merge_train.py classify <head> --repo $REPO` (#2584's classifier, the one owner of head state; no second one). RED (rc 1) refuses the dispatch, records nothing, and names the red contexts. GREEN (0) and WAIT (3) dispatch. An unreadable answer (2) refuses, because an unread head is never green. `HPO_BUS_CLASSIFY` replaces the command in self-tests: bus.sh's own stub, plus a GREEN stub in `cloud_dispatch.py --self-test`, whose reviewer arms run the real `bus.sh dispatch` and must not reach `gh`.

Alternatives considered:
- Re-running the `gate` job alone, as `gate.py --refresh` does. Rejected: the red units are the rate-limited ones, and `gate` re-judges them only once they are re-run. `rerun-failed-jobs` re-runs exactly those.
- Keeping a re-run ledger. Rejected: the run's own `run_attempt` is a bound GitHub keeps, and the brief asks for no state.
- Putting the reviewable check in `cloud_dispatch.py`. Rejected: `bus.sh dispatch` is the registry's one writer and every reviewer path passes through it (seam rule below), so one check there covers them all.

## Head

`14adedc434d763e2ba2378b16bcf1211ea280dfd`, cut from `origin/main` at `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`.

## Mutation proof

The harness is `dev/audit/harnesses/r10_seat_selftests_mutants.py`, extended in this pull request with `merge_train-25`..`merge_train-33` and `bus-1`..`bus-3`. Each mutant is planted in a production line and runs the governance step that names the file. The result line was `RESULT survivors=0`: every mutant KILLED, and each step's unmutated baseline was green first. The checks each mutant reddens come from running the file's own `--self-test` with the mutant applied, restoring afterwards:

- `merge_train-25` (the `--overlap` arm's `self.infra_rerun(...)` line deleted): `FAIL V142 --overlap: past the reset the stamp's run is re-run once, failed jobs only, and logged INFRA-RERUN with its run id and attempt`; `FAIL V142 --overlap: before the reset nothing is re-run and INFRA-RED names the due time`
- `merge_train-26` (blocking arm `if red and` → `if False and`): `FAIL V142 blocking: the re-run that clears main lets the wait pass (no stop), one re-run`
- `merge_train-27` (every-match → any-match: `if not hit:` → `if not hit and not matched:`): `FAIL V142 null: one failed job on any other failure is not re-run`; `FAIL V142 null: a gate whose first reason names a job that failed on a non-infra cause is not re-run`; `FAIL V142 null: an unreadable log, of a unit or of gate, leaves today's red`
- `merge_train-28` (only the `FAIL`-prefixed reason read): `FAIL V142 null: a gate whose second, unprefixed reason is` …`tests / browser: SKIPPED (this run)`, …`failure (run 40596000001)` and …`failure (this run)` `is not re-run`; `FAIL V142 blocking null: a gate that does not qualify is not re-run and main stops red as today`
- `merge_train-29` (`attempt != 1` dropped from `infra_due`): `FAIL V142 null: the same run at attempt 2 is not re-run`
- `merge_train-30` (the train's `att.strip() != "1"` read dropped): `FAIL V142 --overlap null: at attempt 2 nothing is re-run and nothing INFRA is logged`
- `merge_train-31` (`self.wall() < due` → `False`): `FAIL V142 --overlap: before the reset nothing is re-run and INFRA-RED names the due time`
- `merge_train-32` (a reason's job no longer has to be a matching failed job): `FAIL V142 null: a gate whose second, unprefixed reason is` …`tests / browser: failure (this run)` `is not re-run`
- `merge_train-33` (printed epoch ignored): `FAIL V142: a gate whose outcome is RATE-LIMITED is a matching job and its reset_epoch is the due time`
- `bus-1` (RED read as dispatchable, `0|1|3`): `FAIL a head whose required context concluded failure (classify RED) is not dispatched, and nothing is recorded`. The three later dispatch arms also fail, because their record counts shift.
- `bus-2` (WAIT refused, `0|3` → `0`): `FAIL a head still in flight (classify WAIT) is reviewable and dispatches`; `FAIL an unreadable classification refuses the dispatch, never green`
- `bus-3` (the unreadable arm's `die` → `:`): `FAIL an unreadable classification refuses the dispatch, never green`

## Null control

Unmodified tree: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 344 checks, 0 failed` and `bash tools/audit/seat/bus.sh --self-test` prints `bus self-test: 104 checks, 0 failed`, both at the head above. Each mutant's baseline is that same green step (the harness prints `NOT RUN` otherwise).

The tests carry their own null controls:
- Re-run arm: the stamp's fixture before the reset (no POST; `INFRA-RED` names `2026-10-26T23:43:00Z`); at attempt 2; with one non-infra failure; with a gate reason naming a non-infra job, a `SKIPPED`, a `(run <id>)` or an absent job; with unreadable logs.
- Dispatch arm: the same dispatch at a GREEN and at a WAIT head, both of which record.

## Figures

- `merge_train self-test: 344 checks, 0 failed`: `python3 tools/audit/seat/merge_train.py --self-test`, at the head.
- `bus self-test: 104 checks, 0 failed`: `bash tools/audit/seat/bus.sh --self-test`, at the head.
- `cloud_dispatch self-test: 87 checks, 0 failed`: `python3 tools/audit/seat/cloud_dispatch.py --self-test`, at the head.
- `RESULT survivors=0` over the twelve mutants: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-25 merge_train-26 merge_train-27 merge_train-28 merge_train-29 merge_train-30 merge_train-31 merge_train-32 merge_train-33 bus-1 bus-2 bus-3`. Null control: the per-mutant baseline step, which must be green or the harness prints `NOT RUN`.
- Scope: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running `tests/entities.py`. Command: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. Also run: `tests/entities.py`, plus the `run_always` scripts `tests/env_drift.py --claims-only <merge-base>`, `tests/closure.py selftest`, `tests/layout.py` and `tests/harness_headers.py`, all green; and `python3 tests/structure.py`, which printed `STRUCTURE RATCHET PASSED`.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`.
- Seam rule, every main-gate reader the arm must cover: `grep -nE 'self\.main_green\(' tools/audit/seat/merge_train.py` returns three call sites (before admission, right before a merge, after an unproved merge). All three go through `main_green`, whose two arms both call `infra_rerun`: closed in this diff. The other `classify` readers (`orchestrator_tick.py`'s MAIN section, `proof_watch.py`) report state and do not re-run anything; no carry asks them to.
- Seam rule, every writer of a reviewer dispatch: `grep -rnE '\$S/dispatched"' tools/audit/seat | grep '>>'` returns one writer, `bus.sh` `dispatch`, closed in this diff. `cloud_dispatch.py`'s `_bus_dispatch` reaches it by subprocess: `grep -nE 'HERE / "bus.sh"\), "dispatch"' tools/audit/seat/cloud_dispatch.py` returns the production call and its self-test's relay call, both covered.
- The finder's harness: V142 and carry b87aa9e4 were triaged from instances, not from a round `D*/*.py` harness, so no finder harness exists to re-run. The carries' own controls (the stamp's fixture, both reason orders, and each null control they name) are the `V142` checks in `_infra_self_test` and the four K15 (d) checks in `bus.sh`'s self-test.

## Red checks

none

## Forward-carry

none

## Friction

none
