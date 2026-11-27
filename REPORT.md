# r11-repair-red-batch: PRs that need no repair from this seat

Required set read with `python3 tools/audit/seat/merge_train.py owed-reds` at d380053b; logs read through the GitHub job-log API (failure_logs.sh needs `gh`, unauthenticated in this container).

- #3869 at 441ed2ab: `gate` red (job 140289253636) is a deferral, log line `FAIL run(s) [45931738581] at this head are still being judged; their gate decides`; no other red in the required set was concluded at read time (`tests / nightly-status` exempt per brief); nothing repaired.
- #3913 at 95b952b9: `gate` red (job 140292933720) is a deferral naming run 45931733267. `tests / mutation` red (job 140289945495) named one added unpinned site, `quick_setup.py:145 CMP_BOUND` (`volume >= BUFFER_STORE_MIN_VOLUME`); `mutation-autofix` pushed `ci: pin killed mutants` (5806efb5, one killed_by file `stored_answers.CMP_BOUND.550e9454.json`), no survivor named; nothing repaired by this seat.
- #3897 at 98b4926e: repaired, not a report line; code at `handoff/r11-repair-3897` 133e1d92db, body at `handoff-body/r11-repair-3897` 387490630a (its `## Red checks` answers `gate`, a deferral naming run 45931138745, and `tests / mutation` with `tests / mutation-autofix`, `skip-nothing-killed`).
