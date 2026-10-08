Fix review: merge b5cab6fc6425daa7cd43cdd4fac24ef43aad4987
bus-nonce: e40e7b0519141fc02aca3c0153ea57f1

Round 2. Measured head b5cab6fc (code head 7e744707); live head re-read at posting: b5cab6fc.

## Round-1 blocker and recommendations: resolved

- Image labels: run 37768894718 at 7e744707, jobs API: 113283232227 = `nightly-ha (stable)` logs `the download 8077011B` / `12945B`; 113283232260 = `nightly-ha (2025.2.0)` logs `8077018B` / `12952B`; both `ALL 64 checks PASSED`. The body's `## Figures` quotes exactly these, with the right labels.
- data_issues: `known["data_issues"] = []`, matching what HA 2026.10.0 passes when an entry has no issues. New check `A16 passes data_issues as the list HA passes...`.
- _body_bytes: the str branch is removed (aiohttp never exposes a str `.body`, which I confirmed in round 1 against real aiohttp 3.14.3), and the bytes branch is pinned by a new `_writer_bytes` stand-in.

## RESULT lines (seat venv-ci, PYTHONPATH=tests/hastub tests/debug_collect.py, at b5cab6fc)

- RESULT M0 rc=0 ALL 64 DEBUG COLLECT CHECKS PASSED
- RESULT M6_bytes (bytes branch removed) rc=1: FAIL `A16's download writer returns a bytes body as it is` (in round 1 this mutant survived)
- RESULT M7_issues_none (`[]` back to `None`) rc=1: FAIL the data_issues check
- RESULT M1 positional call rc=1 (2 fail); RESULT M2 raw body rc=1 (3 fail); RESULT M3 status guard off rc=1 (1 fail)

## Merges: nothing resolved by hand

- c3c204d3 (5671a611 + 7e744707) and b5cab6fc (c3c204d3 + origin/main 9cac1947): for each, `git merge-tree --write-tree <p1> <p2>` gives rc 0 and a tree equal to the commit's own tree (ae28d1c1, 0ab90c6c).
- `git merge-tree --write-tree origin/main HEAD` gives rc 0. The three-dot diff is still only `dev/programme/delivery/2056.md`, `tests/debug_collect.py` and `tests/nightly_ha.py`. VERSION, the manifest, the release notes and the claim files are untouched.
- STRUCTURE RATCHET PASSED; ALL 2210 ENTITY CHECKS PASSED.
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Reds

- Head check-runs (settled, 40): 24 success, 14 skipped, 2 failure. The two failures are `nightly-status` (113291785187) and `delivery-status` (113291784494); both grade main, and the body says so.
- The oracle run 37768894718 also has `closures` (113283232584) and `mutation-nightly` (113283282696) red. Their refusals are identical to those the body names from run 37760373214: the INERT READS line for `git_auto_maintenance_race.sh`, which main fixed in #2055, and the NULL_COMMENT timeout at `__init__.py:43` under boost_drift_replay.py. This diff reaches neither. The body cites the earlier run's job ids for them; the class is the same.

Round-1 findings 1, 2, 4 and 6 carry forward unchanged: the cause, HA's signatures, the A16 size reconciliation, and the RCA soundness.
