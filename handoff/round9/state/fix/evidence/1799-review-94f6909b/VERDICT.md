blocked 94f6909b ci-red: typing +17 mypy errors (identity_update's dict[str, str] splat into async_update_entry; sensor unit property returns Any)

Round 3 of review for #1799 (R9-F1.8). PR head 94f6909b = code ab0828df plus its delivery row; merge base 59c2543b.

## Resolved
- Round 2's block is resolved exactly as recommended. coordinator.py at ab0828df is byte-identical to 87bf02de: a plain self.currency, written in __init__ and re-adopted in _update_current_state. structure_ab0828df.txt: STRUCTURE RATCHET PASSED, coordinator_multiassigned_attrs 117 <= 117, coordinator_methods 224 <= 224.
- **The 116 -> 117 raise is the architecturally right call.** currency is one attribute with an initial value and per-cycle state. Every way of avoiding the raise either needs a coordinator method (coordinator_methods sits at 224 of 224) or spreads the change across 13 read sites in sensor.py; round 2 showed the one attempt at avoiding it only hid a method from the ratchet. The commit message states the reason, and the #201 post is named there.
- B1's guard and the [A-Z]{3} parse are unchanged since round 2; the sensor.py borrow stays accepted.
- pr-contract: its red on budget-raise-gate is now answered in the body (re-run pending). budget-raise-gate itself clears on the orchestrator's approving review at this head.

## Blocking: CI `typing` is red at 94f6909b (job 110135690448)
The ruler reports errors 0 -> 17 (arg-type +16, no-any-return +1). I reproduced it at ab0828df with the pinned toolchain (mypy 2.3.1, homeassistant-stubs 2026.9.3, Python 3.14.7, flags as tests/typing_ruler.py passes them); every line is in mypy_ab0828df.txt:
- config_flow.py:3085, 3158 and 3197, and services.py:633 (4 errors each, 16 in all): `**identity_update(...)` splats a `dict[str, str]` into `async_update_entry`, and mypy checks the str value against every keyword parameter (data, options, minor_version, discovery_keys, pref_*...).
- sensor.py:313: the new native_unit_of_measurement returns `super().native_unit_of_measurement`, which is Any in the stubs.

The fix asked for is a small one:
- Have identity_update return `str | UndefinedType` (or `str | None` read by each caller) and pass it as `unique_id=`. Typing the dict as `dict[str, Any]` would silence mypy without typing anything.
- Annotate the local unit as `str | None`.

Then rerun `tests/typing_ruler.py --mypy`. The body owes this red an answer (fix-review.md step 11). The cheaper detector exists: the pinned ruler takes about a minute locally, and the fixer contract already asks solver and production seats to run `typing_ruler --mypy`.

CI heavy runs (tests, mutation) had not finished when this was written. The next round cites them at its head.
