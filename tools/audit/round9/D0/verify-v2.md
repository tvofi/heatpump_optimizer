# Round 9, D0: verifier V2 (independent lens)

Box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1, BLAS pinned to 1 thread.
Tree: /home/claude/wt-g1v2 at 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus round-9 evidence); no production or test file edited, every perturbation in memory.
Every number below is an objective value or a ratio of two, so it is contention-immune. load1 during the runs was 2.0 to 3.4. The pooled harnesses (`--jobs 2`) print a parent-process thread_factor of 1.27 to 2.41. That factor comes from the pool's helper threads in the parent, not from BLAS, and it applies to no number here, because none is a timing.
Logs: `tools/audit/round9/D0/verify-v2/*.log`. The three V2 harnesses are `v2_dhw_anchor.py`, `v2_stoprule.py` and `v2_random_seeds.py`, each with its metric, command and expected value in its header.

## D0-s1-01: the 0.20x anchor missing from `_solve_space`. Vote: refute

- **Step 1 (finder's harness).** `seeds_ab.py --perturb deep_anchor_dhw --jobs 2` gave drop_rel_max=0.2507 % (two|dhw|winter_narrow|winter_cold, 135.443194 -> 135.103629), mean 0.0108 %, mean with the best cell dropped 0.0046 %, 3 of 40 cells over 0.01 %, and energy_sek_drop_sum=-1.5765 SEK. That matches the finder exactly. load1 2.93. Log: `step1_s1_deep_anchor.log`.
- **Step 2 (own metric).** V2 metric: per two-zone DHW-on cell, (f_prod - f_arm)/|f_prod| at the DHW path's cold-start `_multi_start_minimize` call, captured by wrapping `_solve_space` when `warm_start is None`. The arm is the real seam re-run with production's candidates plus one extra seed. Baseline energy is taken from the same `optimize()` call's `_compute_baseline_power`, with no pre-pass. The finder's metric is the shipped `objective_value` after `_co_optimize`. On every cell the seam value equals the shipped value (`f_seam == shipped` on 25/25 lines), so the two metrics are comparable. Re-racing production's own candidates reproduces f_prod at 0.0000 % on 25/25 cells.

  | arm, 20 winter-price cells | max | mean | mean, best cell dropped | cells > 0.01 % |
  |---|---|---|---|---|
  | b020 (the finding's anchor, 0.20x baseline energy) | 0.2507 % | 0.0215 % | 0.0095 % | 3 |
  | i020 placebo (0.20x init_base energy) | 0.2482 % | 0.0235 % | 0.0116 % | 4 |
  | b015 placebo (0.15x baseline) | 0.2165 % | 0.0351 % | 0.0256 % | 6 |
  | b025 placebo (0.25x baseline) | 0.2842 % | 0.0255 % | 0.0119 % | 3 |
  | b020 at FLAT prices (5 cells) | 0.2342 % | 0.0468 % | 0.0000 % | 1 |

- **Attacks, in the verifier.md step-3 order.**
  1. Contention: none applies, since every number is an objective value.
  2. Gate mode: not applicable.
  3. Grid artefact: one cell carries the aggregate. The mean with the best cell dropped is 0.0046 % on step 1 and 0.0095 % on V2.
  4. Null control: failed. Flat-price b020 reaches max 0.2342 % (two|dhw|flat|shoulder weather), against 0.2507 % at winter prices, and its flat mean of 0.0468 % is above the winter mean of 0.0215 %. The finder's null quoted only the two flat cells that stay at 0.
  5. Placebo: failed. Any extra seed of similar energy moves cells by the same amount, but on different cells. b025 beats b020 on max (0.2842 % vs 0.2507 %), and b015 moves 6 cells against b020's 3. The effect belongs to seed count and basin choice in a rugged landscape (the D0-s2-02 phenomenon), not to the absence of the 0.20x anchor.
  6. Money: in the finder's own arm the energy bill rises. energy_sek_drop_sum is -1.5765 SEK over 40 cells, and two|dhw|winter_narrow|winter_mild pays 45.60 -> 47.32 SEK for its 0.1360 % objective drop.
  7. Reachability: `_solve_space` is the default DHW-on path. That seed-set asymmetry is real in code (optimizer.py:3463-3482 vs 3994-4016).
- **Vote: refute.** Executed numbers: placebo b025 max 0.2842 % ≥ anchor 0.2507 %, and flat-null b020 max 0.2342 %. The code asymmetry is a consistency or hygiene fact. As a price-optimality gap specific to the missing anchor, it fails both the null and the placebo.

## D0-s2-01: ftol=1e-6 stops short of its own fixed point. Vote: refute (headline unreachable; reachable part already claimed)

- **Step 1.** `polish.py --horizon 48 --prices summer_typical --weather winter_cold --tz 1 --dhw 1` gave 55.32744 -> 54.96744 (0.6507 %), load1 2.45. The `--perturb ftol_tight` run gave shipped 54.78892 with gap 0.0000 %. The 24 h repro step gave one|nodhw|shoulder|winter_cold 0.8523 % and one|nodhw|shoulder|summer_cool 0.2701 % (0.0078 units, energy 1.683 -> 1.780 SEK, which rises). All reproduce exactly. Logs: `step1_s2_polish48*.log`, `step1_s2_polish24.log`.
- **Step 2 (own metric).** V2 metric: (f_prod - f_scipy)/|f_prod| at the first seam call's x. f_scipy comes from scipy L-BFGS-B with scipy's OWN finite-difference gradient (jac=None, not production's `_batch_fd_gradient`), ftol 1e-10 and gtol 1e-8. A second arm iterates production's own `_lbfgsb_restart` up to 30 times. Main-run stop messages are hooked at `_scoped_minimize`.
  - 48 h finder cell: 0.6507 % (54.96744, the same point). The iterated production restart gets 0.0000 % and stops after 1 attempt. All 8 first-call runs stop on `RELATIVE REDUCTION OF F`. The mechanism holds independently of the jac. The 48 h flat null is 0.0231 %. Log: `v2_stoprule48.log`.
  - **The shipped horizon is 24 h**: `OptimizationConfig.from_mapping({}).n_steps` = 96 (RESULT shipped_n_steps=96). `from_mapping` reads no horizon key, and the coordinator builds its config only through `from_mapping` (coordinator.py:1980). The 48 h cell is unreachable in real Home Assistant.
  - 24 h grid of 48 cells (shoulder, summer_typical and flat prices × 4 weathers × topology × DHW): shoulder max 0.8523 %, mean 0.0729 %, mean with the best cell dropped 0.0209 %, 2 of 16 cells over 0.1 %. summer_typical max 0.0027 %. flat max 0.0070 %. The finder's headline cell at 24 h (two|dhw|summer_typical|winter_cold) is under 0.003 %. Log: `v2_stoprule24.log`.
- **Attacks.**
  1. Contention: none applies.
  2. Grid: the finder's LOO is 0.0005 % with its one cell dropped.
  3. Null: it holds at 48 h (0.0231 %).
  4. Reachability: fails for the headline. At the reachable 24 h horizon, the cells over 0.1 % are the already-recorded claim one|shoulder|winter_cold (`_CERT_CLAIMS` in tests/optimality.py, "refused on money (#1293)") and one|nodhw|shoulder|summer_cool. That second cell is worth 0.0078 objective units, and the polished plan costs more energy (1.683 -> 1.780 SEK).
  5. Severity: at the shipped horizon there is no unclaimed consequence above 0.01 units a day.
- **Vote: refute.** The executed numbers are shipped_n_steps=96 and 24 h unclaimed max residue 0.0078 units (0.2701 %) with the bill rising. The mechanism itself is verified (0.6507 % via scipy's own finite-difference gradient at 48 h), so if the judge reads it as the #1293 class at a reachable horizon, V2's alternative is weaken to hygiene.

## D0-s2-02: the seed set misses lower basins on shoulder prices. Vote: verify, low

- **Step 1.** `race.py --cells shoulder --weather winter_cold,winter_mild,summer_cool,shoulder --first-only` gave max 1.2012 %, mean 0.3927 % (finder 0.3909 %), mean with the worst cell dropped 0.3388 %, 8 of 16 cells over 0.1 %. The flat run gave max 0.3247 %, mean 0.0918 %, LOO 0.0763 %, 6 of 16. These are within tolerance. load1 2.89 / 2.68. Logs: `step1_s2_race_{shoulder,flat}.log`.
- **Step 2 (own metric, a seed family unrelated to the finder's).** V2 metric: (f_prod - f_rand)/|f_prod| at the first seam call. The challenger is the real seam re-run with production's candidates plus 12 seeded uniform-random starts, with energy scale k/12 and the RNG seeded by the cell name, counted only when floor violation is no worse than production's + 0.01. Paired excess = shoulder gap - matched flat gap.
  - shoulder: max 2.3355 % (one|nodhw|shoulder-weather, 0.1338 units, 7.25 -> 8.57 kWh, matching the finder's 8.5 kWh basin), mean 0.3181 %, LOO 0.1836 %, 6 of 16 over 0.1 %.
  - flat: max 0.4142 %, mean 0.0901 %, LOO 0.0685 %.
  - Paired excess: max 1.9213 pp, mean 0.2280 pp, LOO 0.1152 pp, 5 of 16 cells over 0.1 pp. After also excluding the claimed stop-rule cell one|nodhw|shoulder|winter_cold, the mean over the remaining 14 is 0.065 pp. It stays positive, with 3 cells over 0.1 pp: one|dhw|summer_cool 0.54, one|dhw|shoulder 0.74 and two|nodhw|shoulder 0.105 pp. Log: `v2_random_seeds.log`.
- **Attacks.**
  1. Contention: none applies.
  2. Grid: the excess survives LOO in both families.
  3. Null: flat gaps are nonzero (mean 0.09 % in both families), but shoulder exceeds them, paired.
  4. Circular perturbation: the finder's `add_emax_ladder` hands production the challenger's own seeds, so its closure proves little. V2's independent random family reproduces the gap, which removes that objection.
  5. Money: absolute gaps are small, at most 0.134 units on a 5.7-unit day. The finder's low severity is earned, not inflated.
  6. Reachability: 24 h and the default seam, so reachable.
  7. Prior disposition: the class overlaps the #1294 refused-ladder claims in `_CERT_CLAIMS`. That is for the judge; it does not change the number.
- **Vote: verify, severity low.**
