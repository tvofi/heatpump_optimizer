R10-FLOW-DESIGN-STAGES part 3, item G only: `orchestrator_tick.py` `designs_owed` now prints the age since the newest predecessor dispatched, and a `CP` mark when the group is on `roster_lib.critical_path`. The roster keeps no per-group dispatch instant, so the age is read from the committer date of `origin/dispatch/fixer-<topic>` (topic = predecessor branch after `handoff/`); an unreadable ref prints `(age unknown)`, never a number.

## Head

eba0dcc764ef877d809e1a3f9ff70f1c305f8b81 (base ca0a6cfbc2e5538e6e2220793831443719ff6e98)

## Mutation proof

One mutant per arm, each run with `python3 tools/audit/seat/orchestrator_tick.py --self-test`, restored after:
- CP always on: FAIL `DESIGN OWED age and CP: null control: a non-critical group prints no CP mark`
- CP always off: FAIL `DESIGN OWED age and CP: a critical-path group carries the CP mark`
- age replaced by `(age unknown)`: FAIL `DESIGN OWED age and CP: a group with no design ref prints the age since its predecessor dispatched`

## Null control

Baseline self-test at the head: `223 checks, 0 failed`. Controls in the new block: a non-critical group prints no CP mark; with the design ref present nothing prints; an unreadable dispatch ref prints `age unknown` and no `h ago`. The pre-existing DESIGN OWED check matched `x.split()[2]`, which the CP mark shifts; it now matches the group id by substring and keeps its meaning.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test` -> 223 checks, 0 failed
- `bash tools/pr/prepr.sh` on the committed tree -> `PRE-PR: eba0dcc764ef877d809e1a3f9ff70f1c305f8b81 ... rc=0`

## Red checks

none

## Forward-carry

none

## Friction

none
