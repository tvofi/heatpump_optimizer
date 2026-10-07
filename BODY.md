The capacity-limited slot is a fourth held slot on the arbiter's existing record when its domain is switch and at least one silent row is configured. Inside a silent window the switch is held on; outside, off; a boost releases it and the window holds it again after. An off window writes the idle row and nothing else. Optimizer active off writes nothing and undoes nothing, so a switch the arbiter turned on stays on. The reading that write causes still marks the interval capacity-limited, so the learners skip it, and `quiet_windows.compose` does not read that entity.

The merge with #2008 (R9-SW-4, GCHV night-mode hold) conflicted in `pump_arbiter.py` and kept both: the silent slot in `_SLOTS` and `CONF_QUIET_OFF_WINDOWS` from this branch, `_NIGHT_KEYS` and `_slot_entity` from main, and both write branches. The two never meet on one install: the silent slot needs the capacity-limited entity to be a `switch` (`quiet_windows.silent_control_usable`), the night-mode numbers need it to be the GCHV `binary_sensor` flag (`modbus_prefill.package_prefix`). With both branches `_write` reached cyclomatic 17 and `functions_cc_over_15` 32 against 31, so the three service calls became `_service`, which returns the service and its data; `_write` makes one call. `_write` is 14, `_service` 5, and no budget moved.

`_silent_rows` is a `TypeGuard` so a true result is the `str` `_inside_silent` takes. `dict.get` of the silent spec is `Any | None`, and the guard is what narrows it.

Closes #1911.

_Requested by **tvofi**_.

## Head

9e0f0a2f01a7f19e49cefb5108cb42cef30f5c5e

## Mutation proof

`_silent_target` returned None before the entity check. `PYTHONPATH=tests/hastub python3 tests/features.py` then failed the seven silent-slot checks (inside, outside, overlap, rewrite and warning, restart record, channel boost, global boost). The line was restored.

`python3 tests/mutation_table.py --pin-killed --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --scripts tests/features.py --jobs 3 --budget-minutes 180` drove the 17 sites this diff adds. Baseline `tests/features.py`: rc=0 failed=0 in 486s. Result: `PIN KILLED: 13 pinned, 4 left unpinned`. The four that lived are recorded as `equivalent` under `survivor_triage`, each from a measured comparison. After that, `python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py` exits 0: 4695 unpinned, equal to the count at 6001b09a.

The merge delta's sites. `python3 tests/mutation_table.py --pin-killed --scope changed --base 3910026eed3059201875f159e9bd4a2244d59281 --scripts tests/guard_pins.py --jobs 3 --budget-minutes 30` killed `_service`'s mode and silent guards and `_write`'s `if service is None` with the new `tests/guard_pins.py` checks (R9-SW-2 mode, silent, set-point), and the night-key guard with #1913's. Null control: the comment-only mutant at line 175 survived every driver. The same drive with `tests/features.py` timed every mutant out at a load average near 90, which is why the cheap checks exist. The two `_write` pins whose guards moved into `_service` were deleted, and `_service`'s trailing `return None` is triaged equivalent: removing it returns the implicit None. Then the `--max 0` count is 4694 unpinned against 4695 at 3910026e.

## Null control

Before the slot wrote anything, those seven checks failed and a space step's mode and set-point writes matched the twin with no silent rows. With the slot, that duty row still matches and the switch call is the addition. No silent rows, a binary_sensor, a select, the power switch reading off, Optimizer active off, and an off window with no silent rows add no switch call. An on echo clears the miss: the next off is one rewrite and not yet `pump_write_ignored`.

## Figures

- Strict mypy of the package, before the narrow and after it: `/Users/timmalmstrom/.venv-typing-r9f23/bin/python -m mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --python-version 3.14 custom_components/heatpump_optimizer`
- The pin drive: `python3 tests/mutation_table.py --pin-killed --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --scripts tests/features.py --jobs 3 --budget-minutes 180`
- The unpinned count after the pins: `python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py`
- Structure ratchet: `python3 tests/structure.py`. Before the extraction it printed `FAIL functions_cc_over_15 32 > 31 (+1)`; after, it exits 0.
- Cyclomatic per function, `tests/structure.py`'s `cyclomatic_complexity` over `pump_arbiter.py`: `_write` 13 at 29751f36, 15 at 3910026e, 17 after the merge, 14 at the head; `_service` 5.
- Every slot through `_service`: `PYTHONPATH=tests/hastub:. python3 -c` over `_SLOTS + _NIGHT_SLOTS`. mode gives select_option, silent turn_on, the four night numbers set_value, and the two set-points None (the `_write_setpoint` path).
- Three-dot names: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`
- Main tip merged: be0cb82134bd3a008e59127da6f2b67fb1c77e98, read with `git rev-parse origin/main` at 2026-10-07T08:10Z.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 20 script(s) run, 11 scoped out`; each script in `scope.run` was run with `PYTHONPATH=tests/hastub`, all of them at 9e410efd (before the be0cb821 merge) and again at the head for every script whose recorded closure the be0cb821 merge reaches; `boost_drift_replay.py`, `plan_view.py` and `solar_alignment.py` are reached by none of its files and stand at 9e410efd. Green at the head: golden (`NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`), card_drift, card, structure, typing_ruler, wood_advisor, guard_pins (50 checks), deployment_shape, config_flow_steps, manual_plan, doc_claims, finite_boundary, arch_score_head, env_drift, entities (2191 checks) and harness_headers (both with the venv-ci Python 3.14; the shell's 3.11 cannot parse an f-string in `tests/entities.py` that main carries). Red at the head: features.py, 1 of 3810, the R9-F2.1 P3 check below.
- Claim files: `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo identical` printed identical for both.
- Unpinned count: `python3 tests/mutation_table.py --scope changed --base 3910026eed3059201875f159e9bd4a2244d59281 --max 0 --scripts tests/features.py` prints 4694 against 4695 and `MUTATION TABLE PASSED`. Before the `_service` pins it printed `REFUSED -- 4699 ... 4 of them added by this diff`.

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
