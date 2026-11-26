Main `tests / fast (3.14)` is red in `tests/stress.py` ("probed scenarios' memory peaks stay within their recorded budgets"). The row `summer/1z/space/valve` read 0.4 MiB attributable against a 0.2 MiB record, so its fail threshold (0.3 MiB) was crossed. Since #3890 (db56b365) the memory pass probes every recorded row on CI, and this row's record was taken on macOS. Its CI readings are 0.1 (job 139068952639), 0.0 (job 139717939394) and 0.4 (job 139744456641, dbdc71fa, red).

This changes one value in `tests/stress_budgets.json`: that row's `rss_attrib_mb` goes from 0.2 to 0.4, the red run's reading and no higher. Every other row and field is unchanged and no check logic moves. It is the remedy the docstring of `rss_attrib_fail_threshold` prescribes: the record is the maximum over contexts, so the CI draw is folded into it. Leaves #3885 open.

## Head

37ddb0181d33ba9c122c0c727555e6014b02ecd2

## Mutation proof

The mutation is the old record. the fixer verdict script evaluates `rss_attrib_fail_threshold` on the record at origin/main and at the head against the three CI readings: the old record (0.2, threshold 0.30) fails the 0.4 reading; the new record (0.4, threshold 0.60) passes 0.1, 0.0 and 0.4. The fixer's scoped prepr returned `PRE-PR: 37ddb0181d33 rc=0`.

## Null control

The unmodified tree is main at e91329c2: `tests/stress.py` fails its memory-peak check on this row at the 0.4 reading, as main's `tests / fast (3.14)` shows.

## Figures

none

## Red checks

- `tests / fast (3.14)` on main is the check this change answers. The cheaper detectors and their standing cost are in `## Root cause`.
- `budget-raise-gate` is red until an approval at the head, because a cap went up (`tests/stress_budgets.json`: `summer/1z/space/valve.rss_attrib_mb` 0.2 -> 0.4). The finding that no cheaper payment exists is in `## Raise justification`; the approval is under mandate 6893738184 (scope all).

## Raise justification

A `*_budgets.json` value goes up, approved under mandate 6893738184 (scope all).

Payments tried: no code-side payment exists, because the docstring of `rss_attrib_fail_threshold` rules out a fixed allowance on this check (it refuses an additive floor on the attributable arm); and the budget is a measurement record, so there is nothing to delete, move, share or refactor that pays it.
Architecture score: dS +0.0000 NULL

(`python3 tools/audit/archscore/score.py --diff e91329c2c2 origin/handoff/hotfix-main-fast314`; no metric moves, the change is one JSON value.)

## Root cause

- Cause: the row's 0.2 MiB record was taken on macOS (76.3 MiB watermark); the CI runner reads every probe at the import floor, which is up to 0.5 MiB for this row, above its 0.3 MiB threshold. Carry: dismissed: fixed by this change, the CI reading is in the record.
- Process state (c): `tests/run.sh` `lane_stress` has skipped `tests/stress.py` on every scoped PR gate since dafdd50e (#3885), even when the diff touches `stress.py`, so #3890 never ran the all-row probing on Linux before main. Carry: #3885
- Cheaper detector (a), proposed and not built under the tooling freeze: keep `stress.py` in the gate when the diff touches `tests/stress.py` or `tests/stress_budgets.json`. Carry: #3885
- Cheaper detector (b), proposed and not built, the reliable one: a static check over `tests/stress_budgets.json` that flags a row whose fail limit (record x 1.5) sits inside CI floor noise of up to 0.5 MiB. Carry: #3885

Both detectors are written up as proposal P-R11-STRESS-SCOPE-AND-NOISE.

## Forward-carry

- Detector (a), `tests/run.sh` keeps `lane_stress` in the scoped gate when the diff touches `tests/stress.py` or `tests/stress_budgets.json`. Carry: #3885
- Detector (b), a static noise-floor check in `tests/stress.py` over the rows of `tests/stress_budgets.json`. Carry: #3885

## Friction

none
