R10-FLY-SUITE-ENV-FLAKES: a closure recording no longer grades the harness CPU headroom. Part of #2495.

**What failed.** The `closures` job records `tests/harness_headers.py` under strace. strace bills each harness's CPU at a multiple that depends on the runner. On the R10-CI-LAYOUT-P2 probes #2656 and #2657, `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` cost 260–310 CPU-s against its 240 s headroom, which is 50% of its 480 s bound. The same head's re-run cost 166 s, and the twin #2654 cost 179 s, so this is runner variance and not the tree. The recording exited 1, and closures-autofix then refused its repair as `skip-failed-recording`, so a runner lottery could block a PR's closure repair.

**The change.** `closure.py`'s `record()` already sets `HPO_CLOSURE_RECORDING=1` to mark a run that is recorded, not graded, and `stress.py` keys its timing verdicts on it. Under that flag, `harness_headers.py` now skips only the CPU-headroom grade and prints that it did. Every harness still runs, and its exit check and every RESULT comparison still apply, so the recorded closure stays complete.

**No grade is lost.** The headroom is still graded on every pull request by the `fast` lane, which runs `harness_headers.py` without the flag. This removes only the duplicate grade taken under strace. The 480 s bound and the 50% rule are unchanged.

## Head

5576bcdbac1b

## Mutation proof

- Commit 50423394a (pins only) fails with `NameError: name 'RECORDING_ENV' is not defined`.
- Mutant: dropping the flag check in `headroom_verdict` fails the pin "a recorded run does not grade the CPU headroom".
- Plant: lower the frontier's bound to 120 s, so its 85 s cost exceeds the 60 s headroom. A driver that sets that override and then runs `main()` exits 1 without the flag (`FAIL ... cpu=84.6s against 60s`) and 0 with `HPO_CLOSURE_RECORDING=1` (`headroom not graded under HPO_CLOSURE_RECORDING=1`).

## Null control

- An unrecorded run past half its bound still fails the headroom; this is a pin in `harness_headers.py`.
- An unrecorded run within the bound passes.
- On this tree, without the flag, the full script passes and grades the frontier, as the fast lane does.
- `closure.py`'s selftest pins that `harness_headers.py` spells the variable as `record()` sets it, the same pin `stress.py` has.

## Figures

- harness_headers checks: 112 passed. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`
- closure selftest pins: 113 passed. `PYTHONPATH=tests/hastub:tests python3 tests/closure.py selftest`

## Red checks

`none`

## Forward-carry

`none`

## Friction

`none`
