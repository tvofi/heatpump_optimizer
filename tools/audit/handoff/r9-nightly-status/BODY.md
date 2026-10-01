<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: PR run 36873895128 (#1808, 2026-10-01T14:07Z), job `nightly-status`, printed "NIGHTLY ABSENT: newest CONCLUDED scheduled run is 10 nights ago" and named run 35575590367 (2026-09-21), though scheduled runs 09-22 through 10-01 succeeded (newest 36839970966, 09-30/10-01 09:00Z). The code was unchanged since dc66cc87 (09-24), the base was the same dc6c97e4, and the job passed on the 40 other PR runs of that day (the 13:52Z run passed, the 14:07Z run failed). A live curl of the exact query returns the correct newest-ten page, authenticated and not.

Cause: the listing endpoint served an incomplete answer once, and `collect()` took the first listing as truth. The bad response itself could not be captured (the log shows only the verdict), so the intermittent server-side cause is inferred, not reproduced; it is established only to the extent that the same code and query give the right answer now.

After: a result that would read ABSENT (none, or older than max-age) is re-asked up to `CORROBORATIONS=2` times, with a pause, in a different shape (`created>=` the window date, `per_page=30`), and the union is judged. A truly absent nightly is absent in every shape, so it is still red. UNREADABLE paths are unchanged.

What changed: `tests/nightly_status.py` `_discover()` and `collect()`; a new check in `tests/entities.py`. No ratchet raised, no mutation site added, no claim file or version touched.

## Approval

tvofi's approving review is owed (`tests/nightly_status.py` is code-owned).

## Head

`77ca16867e83bb603fd21dd2cbb8f6343c601c82` (code head; this body's commit sits above it).

## Mutation proof

No new mutation pin was added or attempted. The new check errors against the old code (no `_sleep` or `now` seam), so it cannot pass without the fix.

Check: `entities.py` "a stale first listing is corroborated before the nightly is called ABSENT, ...", driving `collect()` with stubbed `_get` and `_sleep`. Stale first listing plus full windowed listing recovers; fresh first answer makes no extra call. The check body was exercised standalone against the new code: recovered run 36839970966.

## Null control

Both listings stale stays ABSENT (every-shape-old ABSENT), so a truly absent nightly is still red. The unmodified tree takes the first listing as truth and prints ABSENT on a stale first answer, which is the failure on run 36873895128.

## Figures

none

## Red checks

none currently known. The `nightly-status` red on #1808 is the bug itself and clears on a re-run. `pr-contract` asks for a verification: a `workflow_dispatch` on main is not needed, because the nightly itself is green (run 36839970966).

Not run here (Python 3.11 cloud seat, no homeassistant or numpy): `tests/entities.py` in full, `tests/harness_headers.py`, the `prepr.sh` closures step (REFUSE, because `entities.py` and `harness_headers.py` cannot run), `mypy --strict`, Python 3.14.2 typing. Ran green: the other `prepr.sh` steps and `tests/structure.py` (STRUCTURE RATCHET PASSED).

## Forward-carry

none

## Friction

none
