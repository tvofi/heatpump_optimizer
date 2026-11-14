Fix review: blocked 82319883fccd6f842dd4b9fc905e994d13d38e64 figure-mislabelled: the loop-trim percentages are shares of loop-off total draw, not of over-draw as the body states

bus-nonce: 1e1e25344cdf6f19235e64e47bdcc513

## Block

Round 1. Fix-review step 8: under the body's stated rule ("The loop trims 60 % of the loop-off over-draw at 0.5 K, 55 % at 2 K, 27 % at 4 K, 19 % at 6 K"), over-draw is draw less the booked 1.59 kWh. From the body's own table rows (re-derived identically at this head, `ev/head-lift.txt`), (off - on) / (off - 1.59) gives 83.2 / 72.5 / 35.9 / 25.0 %. The quoted 60 / 55 / 27 / 19 % are (off - on) / off, i.e. a share of total loop-off draw (60.2 / 54.6 / 27.1 / 18.9 %, `ev/trim-percentages.txt`). The figures as labelled cannot be re-derived. Repair: either relabel the sentence ("of the loop-off draw") or quote the over-draw shares. A body-only edit; the head need not move, and the rest of this review carries to it.

## Evidence

- Head reviewed: 82319883fccd6f842dd4b9fc905e994d13d38e64 (`ev/HEAD.txt`), equal to the PR head and the body's `## Head`; merge base fdb526895c31c430b31325718f8af768807ffbfb. Three-dot diff: `dev/audit/harnesses/r10_water_setpoint_feedback.py` (+47/-1) and `dev/programme/delivery/3577.md` (new). No `custom_components/` change; `VERSION`, manifest and `RELEASE_NOTES.md` untouched (step 5).
- `git merge-tree --write-tree origin/main 82319883fccd6f842dd4b9fc905e994d13d38e64`: rc 0, no conflict, no claim-file driver invoked (step 13).
- `git diff <merge-base>...origin/main -- dev/governance/roles/`: only `fixer.md` moved; `fix-review.md` is current.
- Table re-derived: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py --lift` at the head reproduces every row of `## Figures` to the digit (booked 1.59 kWh; on: 2.29/2.92/4.75/5.31 kWh, last30 0.526/0.544/1.159/1.361 kW, settle 103/149/None/None; off: 5.76/6.43/6.52/6.55 kWh, last30 2.222 kW, never settles; no arm within 15 min; hysteresis 0.5 K and =lift rows identical; every row `repeat identical True`) — `ev/head-lift.txt`.
- Null control (body step 1): at the merge base the harness's original mode exits 1 with `TypeError: cannot create weak reference to 'types.SimpleNamespace' object` (`ev/base-main.txt`); at the head it runs to the end, rc 0 (`ev/head-main.txt`). Confirmed.
- Mutation (step 1, on the repair): reverting `self.entry = _Entry(...)` to `NS(entry_id=...)` at the head makes `--lift` exit 1 with the same TypeError (`ev/mutant-lift.txt`); restored, tree clean. The `_Entry` stand-in is load-bearing. No production line, so no production mutant is owed (body: n/a, agreed).
- Harness provenance (step 9): the base harness (parts 1-3) is the finder's and is committed; it could not run at the base (above), so no base RESULT exists for the lift question. Part 4 (`--lift`, `lift_row`, `part4`) is the fixer's own extension, disclosed here as the builder's instrument, not the finder's. Its `repeat identical True` null control is a determinism check of a seedless simulation; it is not a perturbation that could make the finding fail.
- Other body figures checked: `FEEDBACK_RATE_K_PER_MIN = 0.2` (`pump_arbiter.py:283`), `FEEDBACK_START_HOLD = timedelta(minutes=5)` (`pump_arbiter.py:280`); 4 K / 0.2 K/min = 20 min, as stated; `draw_kw` slope 0.0269 kW/Hz, integration 0.9 Hz per K per minute, 3-minute start programme are in the harness (lines 105-158); the two cited bundles exist; `pump_arbiter.py:270` cites #3380. The `git ls-files tests dev/audit` no-recording claim was not independently enumerated beyond the two bundles named.
- Step 4 refusal (no production change, over-draw established only on the synthetic controller) is sound as recorded; no class enumeration applies (no seam changed).
- `tests/entities.py` could not run locally (no `homeassistant` module at either end); CI's `gate` is cited instead.
- CI at this head: `merge_train.py classify 82319883fccd6f842dd4b9fc905e994d13d38e64 --pr 3577` printed `GREEN 82319883fccd6f842dd4b9fc905e994d13d38e64 pending: none red: none` (`ev/classify.log`). The packet-time `tests / nightly-status` red is outside `merge_train.py owed-reds` (`ev/owed-reds.txt`): not this PR's, owes no answer.
- carry_audit at the head (packet): 1 item, routed (`dismissed: repaired in this diff`).
