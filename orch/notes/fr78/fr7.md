_Requested by **tvofi**_

Part of #201.

## The measured cause

Each added unpinned mutation site costs a full `features.py` drive (~500 s) and the wall-clock `--budget-minutes` (#1880) caps the autofix lane. Diffs of 8–21 sites (EG-B10 #1779, EG-B1 #1887, both 2026-10-04) overrun deterministically; the bot reports `skip-no-measurement`; every large-diff PR pays a manual local-pinning round (+2–3 h each).

## The fix

Parallelise the per-site pin-measurement drive in `tests/mutation_table.py` — the drives are independent (mutant × driver, no shared state): split N-way with a cap (default 4), pins byte-identical, wall-clock before/after measured in the body, a self-test arm proving pin equality under the split. #1880's honesty guard untouched: a driver timeout is never a kill.

## Sources

Roster: `origin/handoff/audit-r9-fixplan` (group R9-FR-7). Incidents: #1779's and #1887's mutation-autofix `skip-no-measurement` logs, 2026-10-04.
