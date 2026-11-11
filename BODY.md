Main is red on `tests / fast`: the `combi_type_branch` census in `tests/features.py` fails at origin/main because six package Python lines name a controller vendor, over the census's recorded base, since the census (#3398) and two of those lines landed in separate merges. This change rewrites each of the six lines to state the behaviour (comments and docstrings only, no translated string) and drops the census base to 0, so a single vendor name refuses.

The fix commit is the first fixer's, unchanged; this head carries no further code. `tools/pr/prepr.sh` was run with `PREPR_SKIP_CLOSURES=1` under the orchestrator's ruling: the seat's `/opt/hpo/venv-ci` has no `homeassistant`, so the `closures` step fails at `tests/harness.py` with `ModuleNotFoundError` identically on unmodified origin/main ee64358b. CI's `tests / closures` proves that step.

## Head

39f34916ab9929ee14c5c63fbdd64ab5298c04e7, measured against origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in.

## Mutation proof

`tools/audit/seat/mutant_run.py --in-place`, six mutants each putting the vendor name back on one renamed line (const.py x2, heat_curve.py, pump_arbiter.py x2, thermal_model.py): all six KILLED by the census block.

## Null control

The same `mutant_run.py` run with the unmutated tree: SURVIVED NULL. At origin/main the census block run alone through `tools/audit/seat/features_block.py` FAILS, naming the six lines; at this head it passes (`ALL 1 FEATURES BLOCK PASSED`).

## Figures

none

## Red checks

`tests / fast`: the `combi_type_branch` census in `tests/features.py` fails on main since #3398 merged. The cheaper detector is that census block run locally through `tools/audit/seat/features_block.py` (seconds, no standing cost) before the #3398 handoff against the then-current main. Process state: the check existed and the block was not run against the head that merged; the census and the two late lines arrived in separate merges, so each branch alone was green. This head turns the block green.

## Forward-carry

none

## Friction

none
