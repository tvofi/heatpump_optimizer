The capacity-limited slot is a fourth held slot on the arbiter's existing record when its domain is switch and at least one silent row is configured. Inside a silent window the switch is held on; outside, off; a boost releases it and the window holds it again after. An off window writes the idle row and nothing else. Optimizer active off writes nothing and undoes nothing, so a switch the arbiter turned on stays on. The reading that write causes still marks the interval capacity-limited, so the learners skip it, and `quiet_windows.compose` does not read that entity.

`_silent_rows` is a `TypeGuard` so a true result is the `str` `_inside_silent` takes. `dict.get` of the silent spec is `Any | None`, and the guard is what narrows it.

Closes #1911.

_Requested by **tvofi**_.

## Head

ab5226b6fa1902c7295de240c12d71615d98986e

## Mutation proof

`_silent_target` returned None before the entity check. `PYTHONPATH=tests/hastub python3 tests/features.py` then failed the seven silent-slot checks (inside, outside, overlap, rewrite and warning, restart record, channel boost, global boost). The line was restored.

`python3 tests/mutation_table.py --pin-killed --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --scripts tests/features.py --jobs 3 --budget-minutes 180` drove the 17 sites this diff adds. Baseline `tests/features.py`: rc=0 failed=0 in 486s. Result: `PIN KILLED: 13 pinned, 4 left unpinned`. The four that lived are recorded as `equivalent` under `survivor_triage`, each from a measured comparison. After that, `python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py` exits 0: 4695 unpinned, equal to the count at 6001b09a.

## Null control

Before the slot wrote anything, those seven checks failed and a space step's mode and set-point writes matched the twin with no silent rows. With the slot, that duty row still matches and the switch call is the addition. No silent rows, a binary_sensor, a select, the power switch reading off, Optimizer active off, and an off window with no silent rows add no switch call. An on echo clears the miss: the next off is one rewrite and not yet `pump_write_ignored`.

## Figures

- Strict mypy of the package, before the narrow and after it: `/Users/timmalmstrom/.venv-typing-r9f23/bin/python -m mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --python-version 3.14 custom_components/heatpump_optimizer`
- The pin drive: `python3 tests/mutation_table.py --pin-killed --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --scripts tests/features.py --jobs 3 --budget-minutes 180`
- The unpinned count after the pins: `python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py`
- Structure ratchet: `python3 tests/structure.py`
- Three-dot names: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`
- Main tip at 2026-10-07T01:00Z, not merged: `git rev-parse origin/main`

## Red checks

`typing`, job 112532951404. One `arg-type` in `pump_arbiter.py`, against a recorded 0. Same error on a1fda868: argument 1 to `_inside_silent` was `Any | None`. Cheaper detector: the ruler's mypy, one package run. Measured here before the narrow (1 error, `arg-type` 1, `pump_arbiter.py` 1, exit 1) and after (0 errors, exit 0).

`mutation`, job 112532951481. `MUTATION TABLE REFUSED`, 17 sites this diff adds, 4712 unpinned against 4695 at 6001b09a. Cheaper detector: `python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py`, which refuses the count without driving a mutant. The 17 are pinned or triaged on this head; that command then exits 0.

`mutation-autofix`, job 112535205266. Summary `AUTOFIX: skip-no-measurement` and the repair did not happen: the pin step started none of the 17 for `--budget-minutes`. No cheaper detector than that summary line. The pins were recorded here.

`env-matrix`, job 112532467495. `policy_lint` cannot find `.claude/workflows/policy_lint.mjs`. That path moved on the merge base in #1919. This diff does not touch the matrix driver. The cheaper detector is the job itself. R9-RO-4 and R9-RO-5 own the repair.

`pr-contract`. Cheaper detector: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` on this body, which reads the section.

`nightly-status` and `delivery-status` grade main.

Leaves #201 open.

`tests/features.py` check "R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it" fails on this machine. The three-dot diff does not include the optimizer. The same check failed, with the same two objectives, on the run before the silent slot wrote anything, on the run with the slot, and on the return-None mutant. No cheaper detector: the comparison is the check. This diff does not move it. The pin drive's baseline was green (rc=0 failed=0, 486s) because that local failure was held out of the drive only.

## Forward-carry

none

## Friction

none
