<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Hotfix. Before: with Pump duty control at Control, every boost sent the pump to the fallback row. Boost Space Heating and DHW Boost both wrote *Heating + DHW*, the configured hot-water set-point and the 35 °C flow hold. So a space boost handed the tank to the pump's own thermostat for two hours, and a DHW boost handed it the house. The climate Boost mode also got the 35 °C hold.

After: a boost adds its own duty to the plan step's duty (`pump_arbiter._planned_duty`). Boost Space Heating alone is the space-only row: *Heating* where the mode select offers it, and *Heating + DHW* with the hot-water gate where it does not (GCHV Modbus). DHW Boost alone is the hot-water-only row: *DHW (Hot Water)*, leased like any hot-water-only stretch. A step where the plan, or the other boost, also wants the other duty is the both row. The climate Boost mode is the both row, so it writes the 55 °C heating flow. With the optimizer off nothing is written, as before.

Heat-only support is read from the mode select's own `options` (`_option_for`), not from a model list, so any tuya_heat_pump model that offers *Heating* gets it.

How: `_planned_duty` computes the plan step's duty first, then, while a boost channel is active (`BoostState.active`, so an expired channel no longer counts), ORs the boost's duty into it. The four mutation-ledger rows whose sites the rewrite removed are dropped, and the five new sites are pinned. `docs/configuration.md`'s Rails bullet says the same.

## Head

Code head b99fc23298a89be1de9cc5a122a1a956c1efc6b1 on `handoff/hotfix-boost-heat-only-exh4bc`, cut from cfa2cb07b1474ed3b405787d3b41978e9be61d2f (origin/main, #1708), which is its merge base. Commits: f64911d9 space boost, 06bd2452 DHW boost and the global boost flow, 70f37a68 ledger rows, b99fc232 docs. The mutation table ran at 70f37a68; b99fc232 changes only `docs/configuration.md`.

## Mutation proof

- `python3 tests/mutation_table.py --pin-killed --base origin/main` at 06bd2452: `PIN KILLED: 5 pinned, 0 left unpinned`. Each of `pump_arbiter.py:404 GUARD_OFF`, `:406 GUARD_OFF`, `:415 GUARD_OFF`, `:419 BOOLOP` and `:419 RETURN_DEL` was killed by `tests/features.py`.
- `python3 tests/mutation_table.py --scope changed --base origin/main` at 70f37a68: `0 survivor(s) of 3 evaluated = 0.0%, cap 20.0%`, `MUTATION TABLE PASSED`; the NULL_COMMENT null control survived every driver.
- The checks that go red: `a boost writes its own single duty where the pump offers it, Heating + DHW where it does not or the other duty is due too, and nothing while off` and `the global boost mode writes Heating + DHW and the heating flow; comfort keeps the baseline's hold`.

## Null control

- The new space-boost check at the merge base's `pump_arbiter.py` (test written first): `1 of 3413 FEATURE CHECKS FAILED`. The Tuya space boost wrote `('select', 'select_option', 'Heating + DHW'), ('number', 'set_value', 48.0), ('number', 'set_value', 35.0)`.
- At head: `ALL 3414 FEATURE CHECKS PASSED`.
- In the same check, the optimizer off with a space boost writes nothing, and an expired space boost writes no *Heating*. In the global-boost check, comfort still writes the 35 °C hold.

## Figures

- `python3 tests/features.py` (PYTHONPATH=tests/hastub, pinned requirements-ci env on Python 3.14): 3414 checks passed at head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/typing_ruler.py`: `ALL 11 typing-ruler source checks PASSED`. The census was not run (HPO_TYPING_PYTHON unset); it is left to CI's `typing` job.
- `python3 tests/doc_claims.py`: `ALL 39 checks PASSED`.

## Red checks

none

## Forward-carry

none. The follow-up tvofi chose, splitting a planned both step into DHW only then Heating within the step, is its own pull request from `handoff/duty-split-in-step-exh4bc`.

## Friction

none
