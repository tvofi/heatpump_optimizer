Raises the CodeQL `analyze` job cap from 45 to 60 minutes. The withdrawn module-scope `try` wrapping of `tests/features.py` and `tests/entities.py` is not carried: this head's tree touches only `.github/workflows/codeql.yml` (the branch merges the earlier handoff heads `-s ours` only so the refs fast-forward). Re-scoped under the orchestrator ruling on mandate comment 6624093439.

Closes #3266

## Head

0fb6d09799b98606bb23011dfaf9d7222372562e (code tree identical to e738d3ce2652a7199749d703bc45e584a683a6e6, the head `prepr.sh` ran on; the only later commit is the `-s ours` merge). Base 53273de4d449a990bc29734565f63babada9ff7f; origin/main had not moved when measured and no conflict (`git merge-tree --write-tree origin/main HEAD` printed a tree).

## Mutation proof

n/a: a workflow timeout integer with no production code; the pinned check is `tests/entities.py`'s "codeql.yml's analyze cap clears the python leg's measured worst case" (cap >= 45). Setting the value back to 45 or 60 both satisfy it; the check has no bearing on this raise.

## Null control

Unmodified tree: cap 45 (`git show origin/main:.github/workflows/codeql.yml | grep timeout-minutes`). Legs: the cap is one job-level integer, and `tests/entities.py` requires exactly one `analyze` job (`set(_CODEQL_JOBS) == {"analyze"}`) with an integer `timeout-minutes`, so it cannot be scoped to the python leg without editing entities.py, which the ruling forbids. The actions and javascript-typescript legs therefore also read 60; the diff shows no other changed value (`git diff origin/main...HEAD` is one cap line plus comment).

## Figures

- Python-leg job durations (`completed_at - started_at`), jobs named "codeql / Analyze (python)" in the last 99 push runs of ci.yml on main (`gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs -f branch=main -f event=push -f per_page=100`, then `.../actions/runs/<id>/jobs` per run), fetched 2026-11-07: n=99; p50 41.0, p90 44.5, p99 45.1 min (linear interpolation); min 26.1, max 45.2. 8 runs cancelled: 7 at 45.0 to 45.2 (the cap), 1 at 38.2 (superseded); 91 succeeded, slowest 45.0. Quantiles by a python3 -I script over those rows.
- The sample is right-censored at 45, so its p99 is the cap and not a runtime. Margin: 15 minutes over that p99 (33 percent), clearing 2.3x the fastest run (26.1 -> 60); I cannot prove the 7 capped runs would have finished, since their true duration was never observed, only that 60 gives them 15 more minutes than the observed slow-runner spread (26.5 to 43.9 reported in the ruling) would need.
- `tests/entities.py`: 3 of 2655 checks fail at this head AND at origin/main (a8:register_once set-order extras, two hb:positive_control sampler reads); `diff` of the FAIL lines differs only in those timings/set order. codeql cap check passes.

## Red checks

`prepr.sh` rc=1 with one REFUSE: "closures: failed while being recorded: tests/entities.py (exit 1)". Cause: those 3 environment failures in this container, identical on unmodified origin/main (null control above). Every other step ok or skip. Not repaired in this seat; CI is the judge. The earlier handoff refs held a non-fast-forwardable attempt, so this head merges them `-s ours` (tree unchanged); carries 6e003ed3, 93aad749 and e017bcd8 are dispositioned by dropping the wrapping and not dispatching ci.yml. No non-required reds known.

## Forward-carry

none

## Friction

none
