# R9-DBG-2 review evidence — head 4e5181094ec1c84b7d2552cfd3f184972be9c687

PR #2110, branch `fix/r9-dbg-2`.
Measured head: `4e5181094ec1c84b7d2552cfd3f184972be9c687`.
Worktree (detached): `/Users/timmalmstrom/hpo-seats/r9rev-2110/wt`
Baseline (merge base): `23d354970fcaababe8e67a5c04c326cc8bc79e49` in `/Users/timmalmstrom/hpo-seats/r9rev-2110/wtbase`.

## RESULT — finder's harness, both ends

`dev/audit/harnesses/r9_dbg2_selftest_price.py` (in-tree, identical at base and head:
`git diff 23d354970 HEAD -- <harness>` empty), `--bundle week.json.gz` (sha1
`cb6e9e3357648afc41adcadaff218f135908cc3d`, the sha1 the pre-study names).

```
# BASE 23d354970
RESULT selftest_stores_ms=51.1 ms  # ok
RESULT selftest_accuracy_ms=42.5 ms  # ok
RESULT selftest_solver_ms=0.1 ms  # ok
RESULT selftest_sensors_ms=0.3 ms  # ok
RESULT selftest_feeds_ms=0.3 ms  # ok
RESULT selftest_total_ms=94.3 ms  # budget 900000 ms
RESULT bundle_bytes=588245 B  # cap 8388608 B
RESULT bundle_inline=1 flag

# HEAD 4e5181094ec1c84b7d2552cfd3f184972be9c687
RESULT selftest_stores_ms=17.1 ms  # ok
RESULT selftest_accuracy_ms=72.2 ms  # ok
RESULT selftest_solver_ms=0.1 ms  # ok
RESULT selftest_sensors_ms=0.3 ms  # ok
RESULT selftest_feeds_ms=3.1 ms  # ok
RESULT selftest_total_ms=92.8 ms  # budget 900000 ms
RESULT bundle_bytes=588448 B  # cap 8388608 B
RESULT bundle_inline=1 flag
```

Five `ok` at both ends; the four self-tests this diff does not touch are flat; the bundle
grows 588245 -> 588448 B (+203 B) and stays inline. (The body quotes 588446 / +202 B at
`5ad913305`; I re-derived +203 B and could not reproduce its absolute byte figure.)

Perturbation `--repeat 40` at head: `RESULT bundle_bytes=9214643 B`, `RESULT bundle_inline=0`
— the cap crossing the body claims.

## RESULT — mutation proof (failing-first arm)

`git checkout 23d354970 -- custom_components/heatpump_optimizer/debugger.py` in the head
worktree, then:

```
PYTHONPATH=tests/hastub python3 tests/debug_collect.py
  File ".../tests/debug_collect.py", line 473, in <module>
    holey["row_gaps_h"] == {"n": 11, "min": 0.5, "median": 0.5, "max": 6.0}
KeyError: 'row_gaps_h'
RC=1
```

Restored with `git checkout HEAD -- ...`; `git status --porcelain` empty.
Unmutated head: `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0 (the 7 `FAIL a16:` lines are the
A16 judge's own printed null arms).

## RESULT — the fixer's demonstration probe, both ends

`outage_probe.py` (the body's own disclosure: a seat probe, not the finder's instrument).
Re-run by this reviewer against both trees; it drives the real collector, 48 cycles,
cycles 20..31 publishing nothing.

```
# BASE 23d354970
RESULT rows_recorded=36 of 48 cycles
RESULT outage_streak_at_finalize=0
RESULT shipped_feeds_report={'cycles': 36, 'no_prices': 0, 'weather_stale_cycles': 0, 'weather_stale_h_max': 0.0, 'solve_failures_added': 0}
RESULT fields_naming_the_silence=0 # the six hours are in no field

# HEAD 4e5181094ec1c84b7d2552cfd3f184972be9c687
RESULT rows_recorded=36 of 48 cycles
RESULT outage_streak_at_finalize=0
RESULT shipped_feeds_report={'cycles': 36, 'no_prices': 0, 'weather_stale_cycles': 0, 'weather_stale_h_max': 0.0, 'solve_failures_added': 0, 'row_gaps_h': {'n': 35, 'min': 0.5, 'median': 0.5, 'max': 6.5}, 'tibber_outage_cycles': 0}
RESULT fields_naming_the_silence=2 # reported
```

## RESULT — CI check-runs at the head (the reds)

`repos/tvofi/heatpump_optimizer/commits/4e5181094.../check-runs`:

- `arch-score` failure. Log: `Architecture score: dS -0.0017 WORSENS (inadmissible:
  coord_footprint 2586->2589)`; `FAIL: ... Add a '## Architecture score' section`.
- `typing` failure. Artifact `typing-census.json` (id 11672230519):
  `{"errors": 1, "by_code": {"no-any-return": 1}, "by_module": {"debugger.py": 1}}`
  against `tests/typing_budgets.json` census `errors: 0`.
- `pr-contract` failure. Log:
  `ERROR [pr-body] ...: check 'arch-score' is red and '## Red checks' does not name it.`
  `ERROR [pr-body] ...: check 'typing' is red and '## Red checks' does not name it.`
  `PR-BODY: 2 error(s)`.

## RESULT — conflict and head

`git merge-tree --write-tree origin/main 4e5181094...` -> exit 0, no conflicting paths.
`git ls-remote origin refs/heads/fix/r9-dbg-2` -> `4e5181094ec1c84b7d2552cfd3f184972be9c687`.
`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/fix-review.md`
-> empty (contract current).

## RESULT — claim files

`git diff --name-only <merge-base>...HEAD -- tests/golden/` -> empty.
`python3 tests/env_drift.py --claims-only <merge-base>` -> `claims hygiene: 23d354970fca ok`.
