Idle steps publish an exact sub-code when the solved plan shows why, and the Advisor hot-water row writes that recommended setpoint through `apply_schedule`, which stores it and the comfort target in the entry options. The card says Because for a published sub-code and keeps Likely because when the step is only idle. The what-if prices an active away setback. The payload's minimum temperature is the floor that solve used, and the configured floor is named beside it while they differ. The comfort-at-risk event carries the coldest step's published reason.

Part of #201. Leaves #201 open.

Closes #1795

_Requested by **tvofi**_.

## Head

495accb541325529d87be63ff94e8af37bfb12c2

## Mutation proof

In `idle_reason`, the fuse branch's return was replaced with the bare idle code and the classifier probe was re-run. The step whose cap is shut came back idle, which is the red result of the features check "UX-5 an idle step whose fuse cap leaves no room says the fuse". The return was restored and the same probe came back the fuse sub-code.

## Null control

An idle step at the floor, cheaper than an hour that ran, stays idle. Without an away setback the what-if band and the published floor stay the configured values, and `configured_min_temperature` is absent. A comfort payload with no space-plan forecast still fires, with no cause. A hot-water advisor row already at the recommendation calls no service.

## Figures

`PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main`

`node tests/card_drift.mjs origin/main`

`PYTHONPATH=tests/hastub python3 tests/entities.py`

`PYTHONPATH=tests/hastub python3 tests/features.py`

`node tests/card.mjs`

`python3 tests/structure.py`

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`

The drift comparison's unclaimed leaves, before the claims, were `space_reasons` and `dhw_reasons` only. `flat_prices` captured on this tree and on origin/main differed in those two fields and in no other. `tests/stress.py` was left to CI.

## Red checks

`R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` — red on this branch and on origin/main, same objective pair from the isolated two-zone storage solve. This diff does not turn it red. Cheaper detector: that isolated solve, about a minute, and it fails on the merge base, so no countermeasure belongs to this change.

## Forward-carry

none

## Friction

none
