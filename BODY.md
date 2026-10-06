The capacity-limited slot is a fourth held slot on the arbiter's existing record when its domain is switch and at least one silent row is configured. Inside a silent window the switch is held on; outside, off; a boost releases it and the window holds it again after. An off window writes the idle row and nothing else. Optimizer active off writes nothing and undoes nothing, so a switch the arbiter turned on stays on. The reading that write causes still marks the interval capacity-limited, so the learners skip it, and `quiet_windows.compose` does not read that entity.

Closes #1911.

_Requested by **tvofi**_.

## Head

a1fda86801998d0173ba9f5863ea2023829a9c2a

## Mutation proof

`_silent_target` returned None before the entity check. `PYTHONPATH=tests/hastub python3 tests/features.py` then failed:

- inside a silent window the night-mode switch is held on, and the space step is still the plan's
- outside a silent window the switch is held off, and the space step still heats
- where an off row overlaps a silent row the switch is held off, not on
- a silent switch that does not echo is rewritten after the grace, warned on the next miss, and retried
- the silent write is in the ownership record a restart restores
- a boost releases the silent switch for its duration and the window holds it again after
- the global boost mode releases the silent switch too

The line was restored. `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --scripts tests/features.py` lists 17 sites this diff added and refuses the unpinned count. They were not driven per site; `--pin-killed` is mutation-autofix's. Two existing RETURN_DEL pins on `desired` were re-keyed onto the same returns now that they pass `silent`; the operator is still deleting the return.

## Null control

Before the slot wrote anything, those seven checks failed and a space step's mode and set-point writes matched the twin with no silent rows. With the slot, that duty row still matches and the switch call is the addition. No silent rows, a binary_sensor, a select, the power switch reading off, Optimizer active off, and an off window with no silent rows add no switch call. An on echo clears the miss: the next off is one rewrite and not yet `pump_write_ignored`.

## Figures

- Arbiter blob at this head, same bytes the feature run executed: `git rev-parse HEAD:custom_components/heatpump_optimizer/pump_arbiter.py`
- Feature checks: `PYTHONPATH=tests/hastub python3 tests/features.py`
- Structure ratchet, no re-record: `python3 tests/structure.py`
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
- Three-dot names: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`
- Main tip this body was written against, 2026-10-06T21:38Z: `git rev-parse origin/main`
- Unpinned sites this diff adds: `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --scripts tests/features.py`

## Red checks

`tests/features.py` check "R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it". The three-dot diff does not include the optimizer. The same check failed, with the same two objectives, on the run before the silent slot wrote anything, on the run with the slot, and on the return-None mutant. No cheaper detector: the comparison is the check. This diff does not move it.

## Forward-carry

none

## Friction

none
