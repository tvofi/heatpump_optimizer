# Round 9, D0: verifier V1 (reproduce), box G1-V1

Environment: evidence tree at 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1). CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1 (the finders' stack). BLAS pinned to 1 thread by each harness. Machine: 4 vCPU cloud container, shared with two other sub-seats, --jobs 2 at most. Every number below is an objective value or ratio, so contention does not affect it. load1 is quoted per run. thread_factor is 1.000 on the single-process runs; it reads 1.35–1.70 on the fork-pool runs (seeds_ab.py, anchor_sham.py) because it only reflects how the pool is accounted. None of these numbers is a timing, so none is rejected for that factor.

Tally: 2 verify, 1 weaken, 0 refute, 0 unresolved.

My harness: `tools/audit/round9/D0/verify-v1/anchor_sham.py`, a sham-seed control for D0-s1-01.

## D0-s1-01: the DHW path's `_solve_space` has no two-zone 0.20x anchor

- **Number:** `seeds_ab.py --perturb deep_anchor_dhw --jobs 2` gives drop_rel_max = **0.2507 %** over 40 cells (load1 2.35), matching the finding exactly. Only 3 cells move: two|dhw|winter_narrow|winter_cold 135.443194 → 135.103629 (0.2507 %), two|dhw|winter_narrow|winter_mild 0.1360 %, two|dhw|winter_extreme|winter_cold 0.0435 %. Mean 0.0108 %. 0/40 cells get worse on feasibility. On the headline cell, energy cost falls 122.26 → 121.98 SEK at an equal comfort floor.
- **Controls:** `--dhw off`: 40/40 cells exactly 0.0000 % (load1 2.93), so the built-in no-op holds. `--flat`: the paired two-zone winter_cold and winter_mild cells are 0.0000 % (107.886615 and 47.054120 unchanged); one flat cell moves, two|dhw|shoulder weather, 0.2342 %, while its winter-price twins are 0 (load1 3.01). This matches the finding.
- **Mechanism check (seam grep):** `_optimize_space_only` builds the 0.20x anchor (optimizer.py:4008–4010, `_DEEP_LOW_ENERGY_START_FRACTION`); `_solve_space` builds only the energy and 0.35x anchors (3468–3476) before its `_multi_start_minimize` (3484). Confirmed.
- **Attacks:**
  1. *Contention:* none; these are objective values.
  2. *Grid artefact:* leave-one-out. Dropping the best cell leaves max 0.1360 % and mean 0.0046 %, so the aggregate rests on one cell. As aggregates, the finding's max (0.2507 %) barely clears the flat-grid max (0.2342 %), but that flat max sits on a different cell (shoulder weather). Paired cell for cell, the null is 0, so the price-driven reading holds on the paired control.
  3. *Attribution (own sham arm, `anchor_sham.py --jobs 2`, load1 1.67):* one extra candidate appended to the same cold-start call. A copy of production's first candidate gives max **0.0000 %**; a 0.50x baseline anchor 0.0000 %; a 0.20x anchor 0.2507 / 0.1360 / 0.0435 %; a 0.10x anchor 0.0002 / 0.0000 / 0.1034 %. The gain comes from a deep under-heat seed, not from the count of candidates.
  4. *Perturbation:* the stated on-disk production edit is exactly the harness's arm B, so under it the drop goes to 0 by construction (to_zero). Not re-executed on disk; it is tautological.
- **Vote: verify, severity low.**
- **Metric:** (shipped objective_value − shipped objective_value with the 0.20x baseline-energy anchor added to `_solve_space`'s cold-start candidates) / |shipped|, per cell.

## D0-s2-01: L-BFGS-B ftol=1e-6 stops short of its own fixed point

- **Number:** `polish.py --horizon 48`, headline cell two|dhw|summer_typical|winter_cold: 55.32744 → 54.96744, gap **0.6507 %** (0.3600), viol 0 → 0, thread_factor 1.001, load1 2.63. Matches exactly.
- **Perturbation (ftol_tight):** the same cell goes to **0.0000 %**, shipped objective 54.78892, prod_nit 96 → 158. Across the full 48 h grid the maximum becomes 0.0000 % on all non-flat prices and 0.0011 % flat. The number moves in the stated direction.
- **Full 48 h grid (32 cells, load1 3.48):** summer_typical max 0.6507 %, mean 0.0817 %, leave-one-out mean 0.0005 %; summer_negative max 0.0001 %; shoulder max 0.0417 %; flat null max **0.0231 %**, mean 0.0030 %, matching the finding's null.
- **Attacks:**
  1. *Grid artefact:* 1 of 32 cells is over 0.1 %; the next-highest is 0.0417 %, so the 48 h headline is one outlier.
  2. *Reach:* production never solves at 48 h. `OptimizationConfig.horizon_hours = 24.0` (optimizer.py:1195), and `from_mapping` (1266 ff.) never sets it, so the headline cell is off the shipped path.
  3. *The phenomenon on the shipped 24 h horizon (the finding's own seam rule, 64 cells, load1 2.4–2.5):* shoulder max **0.8523 %** on one|nodhw|shoulder|winter_cold, then 0.2701 % on one|nodhw|shoulder|summer_cool; flat max 0.0070 %; ftol_tight takes both cells to 0.0000 %. So the residue is real on the shipped horizon. But its largest cell, one|shoulder|winter_cold, is already a recorded claim in tests/optimality.py `_CERT_CLAIMS`: "production stops at ftol=1e-6 short of its own fixed point; closing needs a tighter stop rule, refused on money (#1293)."
  4. *What is new:* the 48 h cell, which is unreachable, and the 24 h summer_cool cell at 0.27 % (0.0078 objective units absolute).
- **Vote: weaken, severity low.** The number, the perturbation and the null all reproduce, but the headline is on a horizon production does not run, and the shipped-horizon form of the phenomenon is an existing claimed refusal (#1293). (The sub-seat proposed "info"; the box records "low", the lowest severity on COMMON.md's scale.)
- **Metric:** (f_prod − f_polish) / |f_prod| on the first seam call; f_polish is production's `_scoped_minimize` restarted from the shipped x at ftol 1e-12 and gtol 1e-10.

## D0-s2-02: the multi-start seed set misses lower basins at shoulder prices

- **Number:** `race.py --cells shoulder --weather winter_cold,winter_mild,summer_cool,shoulder --first-only` (the finding's reproduction step 1, its 16-cell grid) gives max **1.2012 %** on one|nodhw|shoulder|shoulder (7.2 → 8.5 kWh basin, 0.0688 objective units). Mean 0.3927 % against the finding's 0.3909 %, within tolerance. 8 of 16 cells over 0.1 %. thread_factor 1.000, load1 2.30. The full default-grid `race.py --horizon 24` (80 cells) was not run; the vote rests on the named subset.
- **Null (flat, same 16 cells):** max **0.3247 %**, mean 0.0918 %, 6 of 16 over 0.1 % (load1 2.17). Matches exactly.
- **Perturbation (add_emax_ladder):** shoulder mean falls to **0.0503 %** (8 cells 0.0005 %, 8 cells 0.1001 %); 15/16 cells at or under 0.0021 %. The one remaining cell, one|dhw|shoulder|shoulder, is 0.8007 %, all polish. The number moves down, as stated.
- **Attacks:**
  1. *Paired null (shoulder minus flat, same topology and weather):* excess max 1.1661 pp (one|dhw|shoulder|shoulder), mean 0.3009 pp, 7/16 cells over 0.1 pp. The gain survives the flat-price null cell by cell.
  2. *Leave-one-out:* dropping the top cell leaves mean 0.3388 % (finding: 0.3369 %). Dropping the top 4 (all single-zone) leaves 0.1432 %, still above the flat mean of 0.0918 %. Concentrated in single-zone summer_cool and shoulder weather, but not one cell.
  3. *Magnitude:* small in absolute terms. The largest pure-ladder cell is 0.1066 objective units per day. The largest absolute gap, one|nodhw|shoulder|winter_cold at 0.4347, is mostly the polish residue of D0-s2-01 (#1293 claim).
  4. *Prior record:* the same class of missed basin is recorded in tests/optimality.py `_CERT_CLAIMS` for one|summer_negative|shoulder and one|winter_narrow|shoulder, closing it "refused on cost (#1294)". These shoulder-price cells are new cells of that known class, and none is a certificate cell.
- **Vote: verify, severity low.** The judge should weigh it as extending the #1294 refusal's evidence, not as a new mechanism.
- **Metric:** (f_prod − min(f_ladder, f_ladder_polish)) / |f_prod| on the first seam call; the ladder is the recorded candidates plus 13 bang-bang seeds at fractions of the bounds' maximum energy.
