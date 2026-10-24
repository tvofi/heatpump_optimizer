Moves the roster seat's queue runner and carry read-back (runq.py, rb.py, previously only under the seat's scratch directory) into `tools/audit/seat/roster_queue.py`, per decision 0013 (tools live in the tree). The runner lints from a clone it owns at `origin/main` so it never moves the orchestrator's checkout; it retries a moved-main refusal up to four times and reads every `append-carry @file` back from the pushed commit. Adds an INSTRUMENTS.md entry and a governance.yml step that runs the self-test.

## Head

e191a706c44a636c6252946014c20d7b4a6abbe1

## Mutation proof

Planted in `roster_queue.py` at the head, each run with `python3 -I tools/audit/seat/roster_queue.py --self-test`: the retry condition disabled (`attempt < 0`) reddens 2 checks ("run: moved main retried", "run: pushed + readback"); the read-back match forced (`hit = [0]`) reddens 3, including the null control "absent text is no match".

## Null control

Unmodified tree: `roster_queue self-test: 12 checks, 0 failed`.

## Figures

- 12 checks, 0 failed: `python3 -I tools/audit/seat/roster_queue.py --self-test`
- 94 self-testing, 94 wired, 0 unwired: `python3 -I tools/audit/seat/selftest_wiring.py --check`
- structure ratchet passed: `python3 tests/structure.py`

## Red checks

none

## Forward-carry

none. Not run locally: `tests/entities.py` (no homeassistant module on this host); CI owns it. The new file is classified by `ci_predict.py --apply-inert` (one `tests/closures.json` INERT READS line for `tests/entities.py`).

## Friction

none
