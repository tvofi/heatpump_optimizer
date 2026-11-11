The CI gate livelock behind #3445 (held in the train 75+ min) and #3446 (code suite run five times at one head), ruling P620 (`dev/programme/triage/s6-batch196.md`). Two seams, each with a failing self-test first and a null arm.

1. `tools/ci/gate.py`, the source loop in `gate()`: a run whose unit's jobs concluded only `cancelled` or `success`, at least one `cancelled`, is no source for that unit, and the loop falls through, as it already does for a deferred (all-skipped) unit. A cancelled newer run sorted first by `fresh()` (its jobs started latest) and the gate read its CANCELLED. A red beside a cancelled job (fail-fast) keeps that run the source.
2. `tools/ci/sweep.py`, `Sweep.fresh()`: a `workflow_dispatch` run at the head that is not completed (`NOT_COMPLETED`) or concluded `success` is the head's fresh judge whatever its `created_at`. Keying on creation at or after the stale gate's completion re-dispatched each time an old pull_request or pull_request_review gate was re-run.

Alternatives: (gate) skipping only an all-`cancelled` unit, the brief's literal wording, leaves a run cancelled mid-unit (some jobs already `success`) as the CANCELLED source, so the livelock survives a late cancel; skipping any unit with one `cancelled` job hides a fail-fast red behind an older green. (sweep) keeping the creation key and adding the re-run's attempt start loses to a stateless one: any live or green dispatch is a judge, so nothing about gate timing can re-open the loop.

Merge note for the orchestrator: a change under `tools/ci` makes every open PR whose base predates it stale-pinned (`Sweep.stale_pin`), costing one fresh dispatch per open PR once; time the merge accordingly.

Fixture fidelity: `sweep_selftest.run()` and `finish()` now set the run's own `conclusion` (the gate job's when the run completed), which GitHub always lists and the new predicate reads; no prior check changed verdict.

## Head

97e6011948c9dd967888050fcb5ad4bc4a17c94b, on base ee64358be7eeccaec5178a923cb3b83a18a924a0 (origin/main at 2026-11-11T13:06:51Z).

## Mutation proof

Each production predicate removed alone, then the self-tests:

- gate.py, the whole new `continue` deleted: `python3 -I tools/ci/gate.py --self-test` fails `a newer cancelled run over an older green one at the head is no source: green` and `null: with only the cancelled run at the head the unit has no source: red` (2 of 85 failed).
- gate.py, `"success"` dropped from the allowed set: fails `a newer run cancelled after part of its unit passed is no source either: the older green judges` (1 of 87).
- gate.py, the `any(... "cancelled" ...)` clause deleted: fails 19 of 87, among them `null: a newer green run over an older red one is the source: green` and `null: a newer failed run over an older green one is the source: red`.
- sweep.py, `later` restored to the `created_at >= completed_at` key: `cd tools/ci && python3 sweep.py --self-test` fails `stale pin, one judge per head: a dispatch listed completed|queued|in_progress, created before the stale gate's re-run completed is the fresh judge; nothing dispatched` (3 of 85).

Restored: gate 87 checks, 0 failed; sweep 85 checks, 0 failed.

## Null control

At ee64358be7 with only the new checks applied: gate self-test 2 of 85 failed (the cancelled-over-green arm reads `(False, ['tests / fast (3.14): cancelled (run 95)', ...])`); sweep self-test 3 of 85 failed (the three one-judge-per-head arms dispatch). The null arms passed at the base and pass at the head: a newer failed run over an older green one reads red; a fail-fast unit (one failure, rest cancelled) reads red; a newer green run over an older red one reads green; with only a `failure` or only a `cancelled` dispatch at the head the sweep dispatches exactly once (`dispatches=1`).

## Figures

- gate self-test: `python3 -I tools/ci/gate.py --self-test` prints `gate self-test: 87 checks, 0 failed` at the head; 81 checks, 0 failed at the base before the new checks.
- sweep self-test: `cd tools/ci && python3 sweep.py --self-test` prints `sweep self-test: 85 checks, 0 failed` at the head.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (reason: `tools/ci/gate.py changes the gate itself`); the full suite is CI's.
- structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Class enumeration (fixer step 8): the seams that pick a run as a judge of a head are the source loop in `gate.gate()` and `Sweep.fresh()` (both closed here); `sweep.settled`/`undecided` read gate jobs, not run conclusions, and are already guarded by the #3308 and settle checks. The P620 measurement (10 of 43 code dispatches) is the ruling's and not re-taken here.

## Red checks

none

## Forward-carry

none

## Friction

none
