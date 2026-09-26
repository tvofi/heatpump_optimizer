# D9 leads unit — verifier V2 (independent), box G3-V2

Same environment as `D2/verify-v2-leads.md` (evidence 96b89163, CPython 3.14.0rc2, BLAS pinned to 1 thread). Own harnesses: `tools/audit/round9/D9/verify-v2-leads/`; the finder re-run of `l3_valve_solve.py` is in `verify-v2-leads/out/f_valve*.txt`. No D3 re-run (tvofi rule). Votes: `tools/audit/round9/verify/votes-G3-v2.json`, key `leads`.

Tally: 2 verify, 0 weaken, 0 refute, 0 unresolved.

## D9-s1-71 — constant DHW helpers recomputed per solve — **verify, low**
- **Finder re-run** (`leads/l3_dhw_helpers.py [--null]`, load1 1.76–1.82, tf 1.000, provisional): calls per solve match exactly (summer_dhw_only 3989/11930/97; dhw_cold_tank 10316/30879/98; dhw_learned_windows 10426/31213/100). saved_share_mean 0.1005 (min −0.0008, max 0.2044) vs null mean −0.0206 (min −0.1265, max 0.0508).
- **Own** (`v2_dhw_helpers_calls.py`, load1 0.50–1.01): independent counting wrapper on `winter_two_zone_dhw`, a cell the finder did not use: 8809/26364/98 calls, inside the finder's bands. Single-cell CPU (5-repeat median, interleaved): memo saved_share −0.0158, null +0.0675.
- **Attacks:** the contention-immune part (call counts) is reproduced independently. The CPU share is noise-comparable per cell: the own single-cell ratio sits inside the null band with the opposite sign even at load1 < 1, so the stated 3–17 % is an order-of-magnitude estimate that holds only as the finder's cross-cell mean. Timing alone cannot carry a refute. Plans bitwise identical in both harnesses.
- **Vote:** verify on mechanism and counts, low; read the CPU percentage as imprecise.

## D9-s2-71 — stress.py samples 0 of 51 throttling-valve plants — **verify, medium**
- **Finder re-run** (`leads/l3_valve_solve.py`, box otherwise idle, load1 0.56 / 0.71, tf 1.000):

| arm | valve CPU / reference | control CPU / reference | valve step-equivalents |
|---|---|---|---|
| as shipped | 184.0–410.7 | 100.4–119.6 | 3,949,248–9,426,048 |
| `--perturb novalve` | 112.6–135.2 | 81.6–94.2 | 4,852,896–5,439,456 |

  stress_sweep_valve_cases=0 of 51 in both. Direction reproduces; the valve band is higher than the finder's recorded 131–285 (CPU ratios provisional).
- **Own** (`v2_valve_coverage.py`, load1 0.99, tf 1.000): built all 51 cases with `stress.build_case()` and read `mixing_valve_mode` off the returned params (no sentinel): 0 of 51 throttle. cProfile cumulative `optimize()` on golden valve_storage: 8.527 s valve vs 5.658 s no-valve (1.51×).
- **Gate mode:** `sweep_combinations()` / `build_case()` take no valve argument and `house()` leaves `mixing_valve_mode='none'`; this is the CI gate's own path.
- **Test-gap lens (step 4), argued without a mutant run (tvofi rule):** a single-line production slowdown in `custom_components/heatpump_optimizer/mixing_valve.py` `emitter_delivery` (line 117, `return max(0.0, ua * (mix_temp - zone_temp))`) is reached only from the throttled branch of `ThermalModel.simulate_step` (`thermal_model.py:2052`, calls at `:2165` and `:2175`), which 0 of 51 sweep cases enter, so no stress rule can see it. The killing change would be in production, not a test; the gap stands.
- **Severity:** a CI blind spot over a real 1.3–3× CPU path, no wrong money or comfort by itself. Medium.
