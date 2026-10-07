Fix review: merge d279db99be024981d674f6e66b29c12d7230b5f9

bus-nonce: a5eeead6bf5fed56ebba64537e4d21e5

Seat r9c-rev-2026, round 2. I reviewed from a fresh detached worktree (/Users/timmalmstrom/hpo-seats/r9c-rev-2026-r2) at d279db99. The round-1 verdict at e6e9b775 is superseded. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2026-r2-ev. Live head re-read at posting: d279db99.

## Round-1 blockers, re-measured

1. **Timing.** The nightly limit is now `driver_timeout(1200, 1634.2)` = 4903 s, where it was 1576 s.
   - Dispatched run 37654541009, `mutation-nightly` job 112906276693, at baa6c237 (test code and production code identical to the head apart from one docstring path):
     `baseline tests/boost_drift_replay.py: rc=0 failed=0 1942s`, then `MUTATION TABLE PASSED (partial: 20 evaluated, 0 timed out, 20 not started for the budget)`.
     `features.py` took 700 s there, so this was the slow runner class.
   - PR head `fast (3.14)` job 112929499909: `ok python3 tests/boost_drift_replay.py (782s)` (fast class).
   - The replay is now measured under its limit at this code.
2. **inert_reads.** `inert_reads["tests/harness_headers.py"]` now lists `dev/audit/harnesses/boost_replay_fork_parity.py` and `dev/audit/harnesses/ci_script_seconds.py`.
   - The full (dispatched) `closures` job 112906198850 at baa6c237 passed: "committed closures cover every file this run touched".
   - The PR head's `closures` job 112929646010 is green.
3. **Guard scope.** `check_fork` now also compares each surface's pre-fork trace with the surface-free arm. My own plants:
   - Fails, as it should, at the planted cycle: channel boost at cycle 100, mode `comfort` at cycle 30, channel boost at cycle 253.
   - Passes: a DHW boost at cycle 200 and a model-param edit at cycle 253. I checked separately that both are output-neutral: shared and unshared replays are EQUAL (plant_effect.log). So no gap is demonstrated.

## Re-verified at this head

- **Equivalence.** My `fork_equiv.py` compares the merge-base per-arm `run` with the head's `replay`. With the stub solver over the full 9 days and fork 254, all 5 arms are EQUAL. The control at fork 255 DIFFERS. At the base, solve inputs diverge first at cycle 255 (channel) and 256 (mode).
- `entities.py`: ALL 2198 PASSED. `structure.py`: PASSED. `closure.py no-copies`: clean. `merge-tree` exits 0. VERSION, the manifest, release notes, golden and claim files are untouched.
- **Head check-runs.** Every gate check is green.
  - `delivery-status` and `nightly-status` are red, but they grade main, as the body says.
  - `budget-raise-gate` was cancelled and its twin succeeded.

## Judged, not blocking

- **The `recorded.seconds` move, 525.3 to 1634.2 (step 14).** The value comes from CI's own Linux recording. I checked it against job 112889923161's record/done stamps: 16:09:59 to 16:37:14, 1635 s. That is a measurement on the right machine, not a figure the change earned, and the body says so: it calls it a correction and states that the fork itself saves about 10 %. `closures.json` is not a `*_budgets.json`.
- **The recorded figure undershoots the slow class.** The nightly baseline ran at 1942 s, above 1634.2. The 3x scale still leaves 2.5x headroom.
- **Cost of the nightly passing.** The replay's baseline now consumes about 32 minutes of the 270-minute nightly budget. 20 mutants were not started, against 13 on 2026-10-06. That cost comes with the corrected limit and is visible in the table.
- **The body's CI line is stale.** It still reads "pending" for run 37654541009. The figures above (1942 s, `MUTATION TABLE PASSED`) belong there before the merge.
- **Root-cause section.** It gives the cause and state (d). It names a cheaper detector that is not built, with the decision recorded and handed to a root-cause.md seat. It also states that the detector would not have fired on #1935's own PR.

## RESULT lines

RESULT ci mutation-nightly 112906276693 @baa6c237 boost_drift_replay rc=0 1942s (limit 4903) PASSED partial 20/40
RESULT ci fast(3.14) 112929499909 @d279db99 boost_drift_replay ok 782s
RESULT ci closures 112906198850 @baa6c237 full: committed closures cover every file; 112929646010 @d279db99 success
RESULT equiv stub fork=254: 5/5 EQUAL; control fork=255 DIFFERS
RESULT check_fork plants: channel100/comfort30/channel253 FAIL (caught); dhw200/param253 PASS and output-neutral
