Lands the round-11 start evaluation on main. `tools/audit/check_scopes.py --round 11` refused the round-11 finder start because `dev/audit/yardstick/round11/EVALUATION.json` was missing from the tree. The evaluation was written, reviewed and ruled by the owner (43 cards accepted, 5 deferred), but it existed only on `eval/r11` (c6ce415b7711d76cf6c08f926f30da91f7bda924). This change copies the nine files that main lacked under `dev/audit/yardstick/round11/` and `dev/audit/rounds/round11/evaluation/`, byte-identical from `eval/r11`. Nothing else changes. Every new path is under `dev/audit/{rounds,yardstick}/**`, which `dev/audit/config/scopes.json` `_coverage_excluded` already classifies.

## Head

caf50a30cf1c693cabba4020f7be6ecfcb3eb996

## Mutation proof

n/a: a record landing with no code change. Removing `EVALUATION.json` brings back the original refusal, shown under Null control.

## Null control

At origin/main 030a4d377f, `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD --round 11` gives `FAIL start evaluation round=11: 1 gap(s)` (`EVALUATION.json is not in the tree`). At this head it reads the evaluation and lists its open cards instead.

## Figures

none

## Red checks

none known

## Forward-carry

none

## Friction

none
