# D1 verify, lens V3 (reach and class), unit D1-2

Environment:
- Evidence tree at baseline 1936d5ca. Stub venv `/root/venv314`.
- Real Home Assistant 2026.2.3 in `/root/venvha`, CPython 3.14.0rc2. Loading it needs `typing.ByteString = bytes` set before the HA import (mashumaro needs it; 3.14 removed it). This is an environment shim, not a product change. The whole integration imports under real HA with that shim.
- `D1-s5-03_realha_http.py` also swaps the zeroconf DNS resolver for aiohttp's ThreadedResolver, because the network integration is not set up. The resolver does not touch response decoding.

All metrics are counts, and load1 during the runs was 0.39–3.27. thread_factor was 1.000–1.003, except D1-s5-02_realha_store at 2.6: its event loop runs on a deliberate second thread, and the metric is a count.

Harnesses: `tools/audit/round9/D1/verify-v3/` — `D1-s4-01_boundary_replay.py`, `D1-s4-01_realha_store.py` (also D1-s4-03), `D1-s4-02_reach.py`, `D1-s5-01_realha_state.py`, `D1-s5-02_realha_store.py`, `D1-s5-03_realha_http.py`, `D1-s5-04_blocks.py`.

## D1-s4-01: duty grid not bounded on load
- **Re-run** (`store_fuzz.py`): duty_targeted_stuck=53, pinned=42, silent=53; the NaN bucket stays at 0.5500 after 200 folds. `--perturb` gives 0 everywhere. Exact; load1 0.39.
- **Own measurement** (`D1-s4-01_boundary_replay.py`): the same seeded stream passed through production `store._sanitize`, which is what `QuarantiningStore.async_load` applies to every store.
  - With the boundary: 30 of 250 stuck, 23 pinned at DERATE_MIN.
  - `--no-boundary` control: 53 of 250 stuck.
  - Stuck through the boundary, by scalar: '1e308' 5, 1e300 5, -1e300 3, 2^70 9, -5.0 4, 50.0 4. Every non-finite spelling drops out.
- **Real HA** (`D1-s4-01_realha_store.py`): a file on disk, read by the genuine Store and QuarantiningStore, then from_dict, then 200 zero-duty folds.
  - 6 of 13 spellings stay out of domain; 3 pin at 0.55 (1e300, "1e308", 2^70). 1.5, -0.3 and 50.0 stay out of [0,1], but the factor still returns to 1.0 within 200 folds.
  - "nan", "inf" and "NaN" become None, which voids the grid and flags it migrated (the D1-s4-03 path). A literal NaN makes the whole load return None.
- **Reach:** the headline non-finite arm cannot reach from_dict in real HA. The residual finite arm needs a hand-edited or corrupted-but-valid file, because observe_duty refuses anything outside [0,1].
- **Severity:** low. One pessimistic bucket, and only after file corruption.
- **Seam rule:** lists all 5 grids of this loader, so it covers everything its stated property scopes. The same domain gap in other stores is D1-s5-02.
- **Class:** P1, confirmed.
- **Vote:** weaken, low.

## D1-s4-02: failed solve adopted as a plan
- **Re-run** (`solve_guard.py`): per config guarded 0/0/3, null control 3/1/0. Perturb: guarded 3/1/0, nonfinite 0 failed / 11 raised. Exact.
- **Own reach measurement** (`D1-s4-02_reach.py`): 36 coordinator-level cells (price, 4 weather keys and solar at nan/inf/-inf, in coord_minimal and coord_dhw), with no injected fault.
  - 0 failed-status plans published; 36 of 36 optimal.
  - A spot check confirmed that every array reaching optimize() is finite.
  - So the claim's "one non-finite horizon input" trigger is unreachable through the coordinator. It holds only at optimizer level.
- **Remaining trigger:** a genuine exception inside `_multi_start_minimize`. That path is pure numpy/scipy and identical under real HA. The decision is made by string status versus exception, which is independent of HA.
- **Severity:** medium, as the finder gave. A heuristic fallback is adopted, an ERROR is logged every cycle, `optimization_status` reads "failed (...)", and the solve_failures repair notice and streak are lost.
- **Seam rule:** finds both `f"failed ({e})"` writers (optimizer.py:3500, 4028), so all. The other broad excepts (co-opt pass :2388, DHW LP :5263) are designed fallbacks, not failures.
- **Class:** P2, confirmed.
- **Vote:** verify, medium.

## D1-s4-03: one bad cell voids the v2 measured grid and is labelled an upgrade
- **Re-run:** v2_one_bad_cell_flagged_migrated=226, buckets discarded 2712. `--perturb-label` gives 0. Exact.
- **Own measurement:**
  - Real HA: 5 of 13 spellings flagged migrated ("nan", "inf", "NaN", "abc", null).
  - Boundary replay: 185 of 250 duty-targeted mutants flagged migrated, against 162 without the boundary.
- **Reach:** the quarantine boundary widens this path, because every non-finite leaf becomes None and voids the grid. The trigger is still a hand-edited or corrupted file. The log line is INFO.
- **Severity:** low.
- **Seam rule:** `grep migrated` enumerates only the label (defrost.py:489). The whole-grid void in `_grid_of` is not listed, so partial.
- **Class:** P1, confirmed.
- **Vote:** verify, low.

## D1-s5-01: age_of ignores last_reported and accepts future stamps
- **Re-run:** reported 7/12, future 6/6, control 0/12. Perturb gives 0/0/0. Exact.
- **Real HA** (`D1-s5-01_realha_state.py`): the genuine StateMachine, driven with `async_set(timestamp=...)`.
  - Re-writing an identical value moves only last_reported, which confirms the premise.
  - Divergent cells: reported 4/6, future 4/4, control 0/4. Perturb gives 0/0/0.
- **Reach:** real for polling or periodically re-reporting sensors. A report-on-change sensor never diverges.
- **Severity:** medium. The humidity mold floor is dropped and the DHW inlet falls back to the seasonal model; a backward clock step lets a stale value count as fresh.
- **Seam rule:** 10 lines, covering every stamp read in the tree, so all.
- **Class:** P2, confirmed. It is the #775 reader fix, never ported to the sibling.
- **Vote:** verify, medium.

## D1-s5-02: price-model and peak-tracker loaders check finiteness, not domain
- **Re-run** (n 300, seed 9): price 11 (next cycle still invalid 9), peak 8 (2), crash 0, controls 0. Perturb 0/0. Exact.
- **Real HA** (`D1-s5-02_realha_store.py`): every mutant saved by the genuine Store and read back through QuarantiningStore gives price 11 (9) and peak 8 (2), identical to the re-run.
  - The boundary changed 81 payloads and 8 loaded as None, but none of the 19 counted, because they are finite out-of-domain values.
- **Reach:** a hand-edited or corrupted file only.
- **Severity:** medium stands. The consequence (unpublished-step prices of 0, a negative published peak) is money-relevant.
- **Seam rule:** 16 def-sites in 14 files. It misses the inline coordinator loaders (thermal_learning_store at coordinator.py:2847, the energy store) and the legionella, apply_draws and apply_cooling_rate paths, so partial.
- **Class:** P1, confirmed. Same phenomenon as D1-s4-01 in other stores.
- **Vote:** verify, medium.

## D1-s5-03: one huge JSON integer drops the whole fetch
- **Re-run:** entity, tibber and open_meteo huge_int rows are 0/0/0 (controls 24/24/72). Perturb gives 24/24/72. Exact.
- **Real HA over real HTTP** (`D1-s5-03_realha_http.py`): a local aiohttp server, fetched through the genuine `async_get_clientsession`.
  - Tibber huge_int: 0 rows, raises JSONDecodeError. Open-Meteo huge_int: 0 points. Both stay at 0 with the perturbation too: HA's `HassClientResponse.json` decodes with orjson, which rejects 10**400 before the parser runs (and turns ints of 65 bits or more into float).
  - Entity source: 0 rows (OverflowError), rising to 24 with the fix. This is the only real seam, and it needs another integration to set an attribute that is a Python int over 1e308.
- **Severity:** low.
- **Seam rule:** 3 sites in 2 files, while 46 `except (TypeError, ValueError)` sites exist across 18 files, so demonstrated-only.
- **Class:** P2, confirmed.
- **Vote:** weaken, low. The claim holds on 1 of its 3 seams in real HA.

## D1-s5-04: one off-grid stamp erases the solar horizon
- **Re-run:** stray 1/5/30 min give 192/192/94; healthy 0. Perturb gives 0. Exact.
- **Own measurement** (`D1-s5-04_blocks.py`, real-HA venv):

| arm | irradiance None | humidity None |
|---|---|---|
| hourly-only stray | 192/192 | 192/192 |
| full 15-minute block present, stray in hourly | 0/192 | 192/192 |
| stray in 15-minute block | 192/192 | 0/192 |
| healthy | 0 | 0 |

  Perturb (median gap) gives 0 in every arm.
- **Reach:** timezone=UTC is requested, so there is no DST off-grid. It needs a malformed upstream stamp.
- **Severity:** low.
- **Seam rule:** the single inference site (open_meteo.py:231) feeds every series, so all.
- **Class:** `new` confirmed. A minimum-gap resolution inferred from external stamps; no existing class covers it.
- **Vote:** verify, low.
