Main's `closures` check is red since #2051 merged: `tests/harness_headers.py` opens `dev/audit/harnesses/git_auto_maintenance_race.sh` (added by #2051) and `tests/closures.json` did not list it under that script's `inert_reads`. This adds that one line, after `eg_b7_seam_hubs.py`, where the closures bot put it on #2053 (`6ddb8c4c`). No timing re-records.

## Head

`b416093e94dfa45e3960478f8f3aa1d54077869e` on origin/main `816547ef`, a one-line change to `tests/closures.json`.

## Mutation proof

Remove the added line and the check goes red: that is main's own run. `closures` on `470bbd60` (#2051's merge, run 37746914557, job 113210470058) failed in "Fail if tests/closures.json under-approximates" with `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/git_auto_maintenance_race.sh`. The check needs strace recordings, so it only runs on Linux CI; it was not run locally (`derive_closures.sh` is not run off Linux, gate-scoping.md).

## Null control

The unmodified tree is main at `470bbd60` and `816547ef`: red as above (the `816547ef` runs were still in progress when this was written). Only `tests/harness_headers.py` is named, so only that key changes.

## Figures

none

## Red checks

`closures` on main (`470bbd60`, run 37746914557): INERT READS UNDER-APPROXIMATED for `dev/audit/harnesses/git_auto_maintenance_race.sh` read by `tests/harness_headers.py`.

Root cause. #2051's own `closures` was green (job 113198518531, head `afbaaf73`) because it ran the SCOPED case (`SCOPE_CASE: scoped`, `check --partial`, `DOCS_ONLY_FAST: false`): the scoped gate re-derives only the closures a diff intersects, and the diff added a new inert `.sh` that no recorded closure contains, so `harness_headers.py` was never re-recorded and never saw the new read. The push to main forces the full re-record, which opened the file and failed: the design working as intended ("main goes red within one merge"), but with one red main commit. `closures-autofix` on that head was `skipped`, so no bot commit pre-empted it. Class: a new file in a directory a measured script scans, born inert, that no PR-time re-derive can attribute to that script. This recurs the class #2042/#2049 addressed (the bot repairing INERT READS), but those fix the bot's reach once the check is red, not the scoped lane's blindness to a new inert file read by a script that scans its directory. Cheaper detector: none built here; a scoped-lane rule that a new tracked file under a directory a measured script lists (harness_headers.py scans `dev/audit/harnesses/`) forces that script's re-record would catch it at PR time. Left as a recorded candidate for the orchestrator's root-cause seat, not decided here.

## Forward-carry

none

## Friction

none
