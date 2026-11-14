Fix review: merge 82319883fccd6f842dd4b9fc905e994d13d38e64

bus-nonce: 1b2ff36233cc0a5416eaa24954e7f792

Round 2 (delta review). Head 82319883fccd6f842dd4b9fc905e994d13d38e64 is unchanged since round 1; the only delta is the PR body, relabelled from "of the over-draw" to "of the loop-off draw". Round 1's only block (`figure-mislabelled`) is resolved.

## Evidence

- Relabel verified against the body's own table rows (ev/shares.txt): (off - on) / off = 60.2 % at 0.5 K, 54.6 % at 2 K, 27.1 % at 4 K, 18.9 % at 6 K, which round to the quoted 60 / 55 / 27 / 19 %. Taken as a share of the over-draw (off - 1.59 kWh booked), the same rows give 83 / 72 / 36 / 25 %, so the new label is the right one and the old one was wrong.
- Table re-derived at this head with the body's command (`--lift`, ev/lift-head.txt): every drew / last-30 / settle row matches the body to the digit. The hysteresis 0.5 K arms and the =lift arms print identical rows, and every row prints `repeat identical True` (null control).
- Step 1 failing run re-taken at base fdb526895c31c430b31325718f8af768807ffbfb (ev/base-run.txt): `TypeError: cannot create weak reference to 'types.SimpleNamespace' object`, rc 1, as the body says.
- Mutation proof: n/a. The diff touches no production code, only `dev/audit/harnesses/r10_water_setpoint_feedback.py` and `dev/programme/delivery/3577.md` (ev/diffstat.txt). VERSION, the manifest and the notes heading are untouched.
- Step 4 refusal (no `pump_arbiter.py` change, because over-draw is shown only on the synthetic controller and no real trace is in the tree) is unchanged since round 1 and is not reopened by a body-only delta.
- Merge with origin/main: `git merge-tree --write-tree origin/main <head>` gives rc 0, tree c30725eca7187623c6cff45743e5042daeac2534.
- Red checks: `tests / nightly-status` is red but not in `merge_train.py owed-reds` (ev/owed-reds.txt), so no answer is owed.
- CI: `merge_train.py classify 82319883fccd6f842dd4b9fc905e994d13d38e64 --pr 3577` exits 0 with `GREEN 82319883fccd6f842dd4b9fc905e994d13d38e64 pending: none red: none` (ev/classify.txt, ev/poll.log).
