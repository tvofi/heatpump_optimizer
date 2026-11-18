D15-s3 is done for M7. M8 and M9 are only partly done, and are listed under `unfinished`. I found three things, all checkpointed with harnesses whose numbers move under their perturbations. The Write tool refused REPORT.md, so its text is below, as you agreed; REPORT.json and the finding files were written.

**Findings**
- **D15-s3-01 (low, M7):** the debugger's solver self-test counts the inert 0 from each restart's not-run publish as a 0 ms solve. On the owner's bundle that is 10 rows, so the self-test reports a minimum of 0 ms over 662 rows where 652 solves ran. Dropping those rows brings it to 0 rows and a minimum of 9.8 s. The fix is one line in `debugger.py`.
- **D15-s3-02 (medium, M7):** the null-control generator (`dbg_bundle_gen.py`) builds its rows with its own copy of the debugger's row code, and the copy has drifted. All 48 generated rows in a day differ from the production row, and the feed self-test raises a TypeError on them. So the synthetic bundle that D15 says every step runs first cannot run M7's self-test checks. Building the rows with the production function brings this to 0.
- **D15-s3-03 (medium, M8):** `debug_replay` copies the bundle's stores into the replay without masking the entity ids inside them, while the replay half is masked. 4 real ids go in. Over an 18-cycle window, the replay resets 2 learned heat-loss settings to the configuration and warns once that an input is unreadable. Mapping those ids through the mask brings all three counts to 0. All five replay judges read 0 either way, so the lane's own verdict hides it, and every replay reproduction plans on configuration defaults instead of the house as the install had learned it.

**What was not finished**
- **M7, C3:** the 6.7.17 solve-time outliers are in the round-10 bundle, which was not an input this round. On this bundle no solve exceeds 3× its release median in any of the 9 releases.
- **M8:** 7 of 12 items were not reproduced through `debug_replay`:
  - the not-run publish after a restart, because `run_fixture` has no cold-restart arm;
  - the three store off-domain anomalies, which are stored documents rather than time windows (sent to D15-s1 as a lead);
  - restart gaps, off-cadence publishes and the accuracy-sample lag, which were not replayed.
- **M9:** C_same is not computed for any of the 8 install-days. The bundle only has the decision-time inputs for the replay half's one day, and the tree has no model of the measured house except the learned one, which the oracle excludes. C_real, C_model and the model gap are measured: the gap runs from 10% to 187% per day.

**Notes**
- The replay lane traces cycle 0 with a profiler and runs alternate cycles under memory tracing, which made a 1-hour window take over 20 minutes. My harness switches both off; they only feed cost figures, which it does not read.
- `jsonschema` is not installed in the CI venv, so REPORT.json was checked by hand: required keys are present and every coverage row adds up.
- No bundle value, entity id, store key or timestamp is written in any committed file; I grepped for the identifiers and none appear.

---

**REPORT.md** (text to land at `dev/audit/rounds/round11/D15/s3/REPORT.md`)

# D15-s3, round 11: steps M7, M8, M9

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Real bundle: the owner's diagnostics download (hpo-debug/1, 662 cycle rows over 7 days, 7 payload snapshots, 16 stores, self-tests recorded, replay half filled for 24 h). Null control: `tools/replay/dbg_bundle_gen.py --days 7`, run first. Machine: macOS arm64, CI venv, a shared box (load1 between 12 and 280); every number below is a count or a ratio unless marked provisional. Exposure: none.

## Method
- **Enumerator:** `dev/audit/rounds/round11/D15/s3/s3_enumerate.py --step M7|M8|M9 --bundle B`.
  - M7: 11 row checks, 7 snapshots, 5 self-tests, C1, C3 (25 lines).
  - M8: the 10 anomalies the M7 scan raises, C2, C4 (12 lines).
  - M9: 8 install-days.
- **M7:** `m7_rowscan.py`. Every check runs over all rows, and every self-test is re-derived through the production function that wrote it.
- **M8:** `m8_replay.py`. It uses `debug_replay`'s trimming and store seeding with `run_fixture`, over a window of 18.5 to 23 h after the replay half's start (18 cycles). It counts what-if solves per solve, in-window tank cycles, foreign store ids, unreadable-input warnings and learner resets. Arms: base, `tiles-off`, `remap-ids`. The lane's profiler and memory tracing are switched off; they only feed cost figures.
- **M9:** `m9_costs.py`. Per install-day it computes C_real and C_model from the distinct accuracy samples. Null arm and plant-scale perturbation included.

## Findings
- **D15-s3-01 (low, M7):** the solver self-test counts every restart's not-run publish as a 0 ms solve. 10 rows, minimum 0 ms; with `--perturb solver-filter` 0 rows, minimum 9.8 s. The null week reads 0. See `findings/D15-s3-01.json`.
- **D15-s3-02 (medium, M7):** the null-control rows are a diverged copy of `cycle_row`. 48 of 48 rows differ and `feed_health` raises; with `--perturb production-row` 0 rows differ and it completes. See `findings/D15-s3-02.json`.
- **D15-s3-03 (medium, M8):** `debug_replay` seeds store-held real entity ids into the masked replay. 4 foreign ids, 2 heat-loss learners reset to the configuration, 1 unreadable-input warning, all five judges at 0. With `--perturb remap-ids`: 0, 0, 0. See `findings/D15-s3-03.json`.

## Non-findings (commands in REPORT.json)
- No solve failures.
- No solve-time outliers: 0 over 3× the release median in 9 releases; maximum 49.9 s, and 31.7 s on 10.0.0.
- Solve wall time is about twice the payload solve time because of the price tiles:
  - The 10.0.0 rows follow the 2-2-1 rotation with one 4× cap refresh.
  - Older releases ran an extra solve every cycle.
  - At baseline: 0.667 what-if solves per solve, 0 with tiles off.
- Price feed healthy: no row without prices, no short horizon after 14:00 local.
- Weather forecast never stale.
- No contradictions between action mode, pump state and power.
- Snapshot action matches the plan's current step in 5 of 7; the other 2 are user boost overlays.
- Self-tests sensors, feeds, solver and stores re-derive exactly. Accuracy re-derives within 0.006 °C on 192 samples.
- The 10 no-action rows are restarts: 8 release changes and 2 others.
- Hot-water tank below the demand-window minimum: at baseline over the replay window, 5 of 12 in-window cycles are below the floor and all 5 are heating. Over the whole week, 68 of 159 in-window rows are below the floor, 4 of them on 10.0.0.

## Not finished
- M7: C3, because the round-10 bundle was not an input.
- M8: 7 items not reproduced through the replay (see above).
- M9: C_same on all 8 days. Measured: model gap 0.10 to 1.87, mean 0.80, 0.90 with the most favourable day dropped; the null arm reads 0.

## Leads
- **D15-s1:**
  - The 3-interval restart-gap rule finds 2 of the 10 restarts.
  - The store domains disagree with what is written in 3 stores (82 paths).
- **D15-s2:** stores are seeded from 1–2 days after the replay window.
- **D2-s1:** planned power exceeds measured power: hot water 1.66 vs 0.72 kW, boost 4.94 vs 2.39 kW.
- **D0-s3:** the same-information oracle has no measured-house plant for a live bundle.
- **D9-s1:** the price-tile what-if solve doubles the cycle's wall time on the owner's host.

## Harnesses
`s3_enumerate.py`, `m7_rowscan.py`, `m7_nullcontrol_rows.py`, `m8_replay.py`, `m9_costs.py`, all under `dev/audit/rounds/round11/D15/s3/`.

---

**JSON report**: written to `/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D15-s3/dev/audit/rounds/round11/D15/s3/REPORT.json`. It has the dimension and baseline, three coverage rows that add up (M7 24 of 25, M8 5 of 12, M9 0 of 8), three unfinished entries, three findings, ten non-findings, five harnesses and six leads.

Files are in `/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D15-s3/dev/audit/rounds/round11/D15/s3/`:
- REPORT.json
- findings/D15-s3-01.json
- findings/D15-s3-02.json
- findings/D15-s3-03.json
- s3_enumerate.py
- m7_rowscan.py
- m7_nullcontrol_rows.py
- m8_replay.py
- m9_costs.py