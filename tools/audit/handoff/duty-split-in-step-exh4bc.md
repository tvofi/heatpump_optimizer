<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Stacked on the boost hotfix (`handoff/hotfix-boost-heat-only-exh4bc`, code head b99fc232), which must merge first.

Before: with Pump duty control at Control, a plan step with both space heating and hot water wrote *Heating + DHW*. The pump's own two thermostats then decided how the step was split. So the optimizer lost control of which duty ran in about a third of hot-water steps.

After: the arbiter splits such a step itself. It writes *DHW (Hot Water)* for the step's hot-water share of its 15 minutes, then *Heating* for the rest, each through its own row of the duty table. The share is hot-water power divided by total power. A share under `SPLIT_MIN_MINUTES` (5) goes to the other duty for the whole step. On a pump with no single-duty mode (GCHV Modbus), each part is *Heat + DHW* with the other duty's set-point lowered to its gate, as the single-duty rows already do. A boost, a disinfection hold, and any mode other than auto or economy keep *Heating + DHW* for the whole step. The optimizer off still writes nothing.

tvofi chose this over a planner ban on overlap. In a scratch comparison (not a gate instrument, and not in this diff), zeroing space capacity on every hot-water step made 13 of 16 optimizer scenarios dearer. So the plan and every golden fixture are unchanged, and only how a both step reaches the pump changes.

How: `pump_arbiter._share` maps a planned both step to `dhw` or `space` by the minute, and `_arbitrate` passes that to `desired`. The ledger still records the step's planned duty. `docs/configuration.md`'s duty table and a new bullet describe the split.

## Head

Code head 5c391eb6edeb305c2c2c72aee0af8d9d70593448 on `handoff/duty-split-in-step-exh4bc`, on top of b99fc23298a89be1de9cc5a122a1a956c1efc6b1 (the boost hotfix), from merge base cfa2cb07b1474ed3b405787d3b41978e9be61d2f. Commits: 42e79c7a the split, 5c391eb6 its ledger rows and the guard checks.

## Mutation proof

- `python3 tests/mutation_table.py --pin-killed --base origin/main` at 42e79c7a: `PIN KILLED: 4 pinned, 0 left unpinned`. `pump_arbiter.py:177 CONST` (`SPLIT_MIN_MINUTES`), `:637 GUARD_OFF`, `:639 GUARD_OFF` and `:641 RETURN_DEL` were each killed by `tests/features.py`.
- `python3 tests/mutation_table.py --scope changed --base origin/main` at 5c391eb6: `0 survivor(s) of 3 evaluated = 0.0%, cap 20.0%`, `MUTATION TABLE PASSED`.
- By hand, in `_share`'s guard, one clause deleted at a time, with `tests/features.py`:
  - `or _disinfecting(coord)` removed: FAIL `a disinfection hold keeps a both step on Heating + DHW, and so does comfort`.
  - `or held.active(boost.CHANNEL_DHW, now)` removed: FAIL `a boost writes its own single duty where the pump offers it, Heating + DHW where it does not or the other duty is due too, and nothing while off`.
- The checks that go red on the unsplit arbiter: `a both step writes DHW only for its hot-water share of the 15 minutes, then heating only` and `a share under the minimum sub-slot goes to the other duty for the whole step`.

## Null control

- The new checks against the hotfix's `pump_arbiter.py` (tests written first): `2 of 3417 FEATURE CHECKS FAILED`. Every case wrote `Heating + DHW` at minute 1.
- At head: `ALL 3418 FEATURE CHECKS PASSED`.
- Modbus keeps *Heat + DHW* and a boost's both step is not split; both are asserted in the same run.
- The one existing check the split changed, `on the real curve a heating-plus-hot-water step's heating share writes Heating and the heating flow`, now runs at minute 10 of a both step. Its heating-flow and no-gate assertions are unchanged.

## Figures

- `python3 tests/features.py` (PYTHONPATH=tests/hastub, pinned requirements-ci env on Python 3.14): 3418 checks passed at head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/typing_ruler.py`: `ALL 11 typing-ruler source checks PASSED`. The census is left to CI's `typing` job.
- `python3 tests/doc_claims.py`: `ALL 39 checks PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none
