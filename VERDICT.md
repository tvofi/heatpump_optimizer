Fix review: merge edc8fa5dbb14ee4065b4383e5e94d4e35b0952e3

bus-nonce: 8f1f82f7a6808a7b72c9f97728dd9b94

Round 2. The prior verdict blocked 3560b69668e171c91cac0fbcf1db35490795306e. This is not a fourth round.

Measured edc8fa5dbb14ee4065b4383e5e94d4e35b0952e3. The pull-request body names that SHA. origin/fix/r9-sw-5 was that SHA at posting. Merge-base with origin/main is 1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872. The briefs diff against origin/main is empty. `git merge-tree --write-tree origin/main HEAD` exited 0. The only tree change from handoff 63aebe893e572c9ae558cae7049613b23a2c8f6b is docs/delivery/2000.md, which arrived with origin/main.

RESULT window-conjunct deleted `and _window_open(snap, now)` in `_dhw_floor`: `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exited 1, `FAIL the tank at its minimum outside a demand window does not release` (1 of 46). Restored, the same command exited 0, `ALL 46 BLOCK DUTY CHECKS PASSED`, and that check printed ok. The fixture is a 45 °C tank, minimum 45 °C, windows 00:00-01:00, at 12:00 (`NOW` in tests/block_duty.py).

RESULT power identity `action["power"] = action["power"]` in place of `action["power"] = 0.0`: the same script exited 1, `FAIL a space block zeroes space power and not the supply switch` and `FAIL a space block does not invent power_normalized` (2 of 46). Restored, it exited 0.

RESULT `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872`: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. Neither claim file is in the three-dot diff. VERSION, the manifest version and the RELEASE_NOTES heading are untouched.

RESULT `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

RESULT `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py`: `RESULT claims_true=123 claims` and `RESULT claims_false=0 claims`. The D6 movement is 76 entities to 78 and 4 switches to 6, the two block switches.

RESULT selection-cost, Jaccard at 0.80 over `tests/closures.json` as tests/entities.py's `_d308_pairs`: 103 of 496, 378 comparable pairs, 88 production files. Those three strings are in tests/deployment_shape.py. The closures diff adds only tests/block_duty.py (31 scripts to 32). That closure contains boost.py, switch.py, pump_arbiter.py and store.py. tests/run.sh runs tests/block_duty.py. tests/derive_closures.sh records it.

The body's enumeration rule is `PYTHONPATH=tests/hastub python3 tests/block_duty.py`. It returned 46 checks. The release set covers the issue's floors: due and overdue legionella and the horizon edge, a disinfection hold, the tank at its minimum inside a window and not outside one, the room floor at the margin and not above, the cold rail, system identification, a stale plan, and the switch attribute `block_release`. No returned check is a seam left outside the diff. Forward-carry: none. Nothing here changes a later stage.

Red-history over origin/main..HEAD, conclusion `failure`, `pr-contract` excluded the way `failingCheckNames` excludes it: closures, fast (3.14), mutation, mutation-autofix, nightly-status, delivery-status. Each is named under `## Red checks`. nightly-status and delivery-status grade main; the three-dot diff does not touch their scripts, the workflows, the plan or HANDOVER.md. Five commits returned no check runs: 3301d6197d15cfbf58543f4af82fc7980c012996, b89154264a7eb6cca52d4605b902f4238d23240d, aedd50be78debbf9d53a1599c1dfee616e2ed255, aa1a661584d66722c4167c00b995c7609c4cf7cf, 63aebe893e572c9ae558cae7049613b23a2c8f6b. At posting, head edc8fa5 still had fast (3.14), closures, mutation, coverage and Analyze (python) in progress. Those were not re-run. The unpinned 4698/4699 figures and the 68/10 pin tally were not re-derived.
