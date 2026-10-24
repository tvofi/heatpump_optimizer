# D15-s3 — round 10, steps D15.M7 (row scan) and D15.M8 (anomaly to seam)

Baseline fe01b938f71b. Bundle: the live "Download diagnostics" file named in the task, read in place.
exposure: none (no docs/, no GitHub).

## Method
Privacy gate checked first on the part this seat writes from: `export.violations(cycle_rows)` = 0, and the
planted-credential arm fires. `payload_snapshots` fail the gate on free text (169 violations), so no
snapshot value is written here. Version seam (M1 rule): row gaps > 30 min split the 554 rows into 3
segments; tags give v6.7.17 (219 + 333 rows) and v7.0.0 (2 rows, after the 200-minute restart gap on 2026-10-14).

Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D15/s3/row_scan.py BUNDLE TAGS_FILE`.

## Findings
None. Every row anomaly is in a v6.7.17 segment. Re-checking it at the baseline needs the replay half,
and the bundle's `replay` is null (no export.py document was supplied).

## Non-findings (row_scan.py)
- solve failures: 0 rows in every segment.
- solve_wall_ms above one cycle (900 s): 0 rows. Maximum 401 s (v6.7.17); v7.0.0 maximum 30 s.
- heat_pump_on contradicting action_mode: 0 rows.
- Null indoor/outdoor/DHW feeds: 0.
- Self-tests: `manifest.self_tests` is null, so there is nothing to re-derive. That check is vacuous here, not passed.

## Unfinished
- M7: solve-time outliers (payload solve up to 272 s, wall up to 401 s, p50 about 20–27 s) are attributed to v6.7.17 only.
  They cannot be re-checked at the baseline without a replay.
- M8: `debug_replay.py --start/--end` needs `replay`, which is null. No anomaly could be reproduced or mapped to a seam.

## Leads
See the JSON report.
