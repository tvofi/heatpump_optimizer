Refs #3885

This PR leaves #3885 open.

## Summary

**`tests/stress.py` does not run on a pull request.** `tests/run.sh`'s `lane_stress` skips it by name when two things hold: CI's fast job names the event `pull_request` (`HPO_CI_EVENT`, set in `.github/workflows/tests.yml`), and the gate is not `GATE_SCOPE=full`. It still runs on the push to main, which forces `full`, and in a local run, which sets no event. `nightly.yml`'s `slow` job did not run stress.py, so this PR adds it there as its own step. `tests/harness_headers.py` still runs alone at the end of the run.

Measured saving: 928.7 s per pull request, from stress.py's `recorded` seconds in `tests/closures.json`. stress.py runs alone at the end of the run, so the saving is wall-clock time.

Section sampling of features.py and entities.py was cut from this PR by the owner's ruling. That work is kept at `wip/r11-ci-case-sample` `9df0838b` and carried below.

Safety net. The push to main always runs FULL: `GATE_SCOPE=full`, with stress.py included. A merge that turns main red is reverted first.

## Head

`94d3193927a51e754f5f72d385a12fb78f7303c3`: code commit `d09793a8`, one new commit on top of `9df0838b` (review delta `9df0838b..d09793a8`), then a clean merge of `origin/main` `6a58ba5cb3` with no conflicts.

## Mutation proof

A new check in `tests/entities.py` sources run.sh's own `lane_stress`, `run` and `skip` functions. It drives them against a stub tree under four (event, scope) pairs and records two things for each: whether stress.py ran, and whether the SKIP line was printed.
- At base `34c7a3f610` run.sh, the check is red: `('pull_request', 'auto'): (True, False)`. stress.py ran and no skip was printed.
- At this head, it is green: `{('pull_request','auto'): (False, True), ('pull_request','full'): (True, False), ('push','auto'): (True, False), ('local','auto'): (True, False)}`.
- Mutant: drop the `[ "$GATE_SCOPE" != full ]` guard. The check goes red with `('pull_request', 'full'): (False, True)`.

The existing lease pin, `run.sh's lane_stress waits for the lease`, now drops `HPO_CI_EVENT` and `GATE_SCOPE` from its driver's environment. Without that, CI's fast job on a pull request would have passed the event through, and the stub's stress.py would have been skipped instead of leased.

## Null control

`lane_stress` keeps its `run` line for every case but a scoped pull request: `GATE_SCOPE=full`, `push`, and a local run with no event all run stress.py (the check's three `(True, False)` rows).

## Figures

Run locally at this head: `python3 tests/structure.py`, `bash -n tests/run.sh`, and `python3 tests/closure.py selftest`. The new check was run in isolation against base, head and the mutant, as above. This PR adds no tracked file, so the classification in `tests/entities.py` is unchanged.
Not run locally, by the owner's expedite ruling (#3394): a full `prepr.sh`, and a full `tests/entities.py`.

## Red checks

None known at the handoff. CI is not awaited on this PR (#3394).

## Forward-carry

- section sampling (wip/r11-ci-case-sample 9df0838b, ~256 s/PR, method-call mutation rule, callee side-effect residue) Carry: #3885, lands in dev/programme/carries/carry-3885.json

## Friction

None.
