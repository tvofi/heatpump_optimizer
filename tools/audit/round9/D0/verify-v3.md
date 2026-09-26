# D0 verify, lens V3 (reach and class), round 9

Baseline 1936d5ca; evidence tree 6f51db2c. The harnesses resolve no git ref. Stub venv: CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. Real-HA venv: HA 2026.2.3, numpy 2.5.3, scipy 1.18.1. Own harnesses: `tools/audit/round9/D0/verify-v3/` (`D0-s1-01_reach.py`, `D0-s2-01_reach.py`, `D0-s2-02_reach.py`). All numbers are objective values or SEK (contention-immune); load1 0.5–3.4, thread_factor 1.000 except the finder's `seeds_ab.py --jobs 2` fork pool (1.748, no timing meaning).

## Reach in real Home Assistant (applies to all three)
- The solve path is `optimizer.py` plus `thermal_model` and `const`. It imports no `homeassistant` symbol; the bare-package import loaded no HA module.
- In production the solve runs in `process_worker.py`, a subprocess of HA's interpreter. `tests/ha_contract.py` stub divergences do not touch it.
- The integration package cannot be imported in the real-HA venv without a shim: under 3.14.0rc2, `homeassistant.config_entries` fails because mashumaro reads `typing.ByteString`. The harnesses bind the package as a namespace (`HPO_V3_BARE_PKG=1`).
- Every cell run in both venvs gave identical objectives to 6 decimals.
- The production horizon is fixed at 24 h: `OptimizationConfig.horizon_hours` defaults to 24.0, `from_mapping` never sets it, and `n_steps = min(len(prices), 96)`.
- Quick-setup defaults: DHW True, two-zone False.

## D0-s1-01: the 0.20x deep anchor is missing on the DHW path
- **Finder re-run**: `seeds_ab.py --perturb deep_anchor_dhw --jobs 2` gave drop_rel_max 0.2507 % (exact), 3 cells over 0.01 %, energy_sek_drop_sum -1.5765 SEK. Load1 3.09.
- **Own measurement**: `D0-s1-01_reach.py`, anchor keyed on `_solve_space`'s init_base energy instead of the baseline thermostat energy. Winter grid (8 cells): max 0.2482 % (two|dhw|winter_extreme|winter_cold, 129.340129 → 129.019135), mean 0.0455 %, 2 of 8 over 0.1 %. Flat: max 0.0302 %. Single-zone control: 0.0000 %. thread_factor 1.000, load1 2.58.
- **Keying attack**: the gap moves between cells with the keying but stays the same size. Finder's keying: winter_narrow|winter_cold 0.2507 %. Own: 0 on that cell and 0.2482 % on winter_extreme|winter_cold.
- **MPC attack**: production's own warm start (#1295), re-solved on identical inputs, closes winter_narrow|winter_cold (0.2141 %) but not winter_extreme|winter_cold (0.0049 %).
- **Money**: winter_extreme|winter_cold saves 0.42 SEK/day. winter_narrow|winter_mild spends +2.82 SEK/day (finder's arm: +1.72). The gain is on the objective, not always on money.
- **Reach**: two-zone set plus DHW on; real-HA venv numbers identical.
- **Severity**: low. **Seam rule**: all; the only two cold-start call sites are `:3484` and `:4019`.
- **Class**: P4. The mechanism also fits P2 (one seed decision made at two sibling seams that disagree); P4 kept.
- **Vote**: verify.

## D0-s2-01: ftol=1e-6 stops short of its own fixed point
- **Finder re-run**: `polish.py --horizon 48` on two|dhw|summer_typical|winter_cold gave 55.32744 → 54.96744, 0.6507 % (exact). With `--perturb ftol_tight`: 0.0000 %. Load1 0.85 / 1.53, thread_factor 1.000.
- **Seam rule at 24 h** (64 cells): shoulder max 0.8523 %, 2 over 0.1 %. summer_typical max 0.0027 %; summer_negative max 0.0051 %; flat max 0.0070 %.
- **Own measurement**: `D0-s2-01_reach.py`, end to end, every `_scoped_minimize` at ftol 1e-12, 24 h, 32 cells. gap max 7.5928 % (objective 0.306), min -0.3754 %, mean 0.4866 %, 10 of 32 over 0.1 %. Flat: max 0.2430 %, mean 0.0691 %. The 48 h headline cell end to end gives 0.9733 %.
- **Reach**: 48 h is not a shipped horizon. At 24 h the largest polish residue is on one|nodhw|shoulder|winter_cold, the `_CERT_CLAIMS` entry that records the tighter stop rule as refused on money (#1293).
- **Money**: the tight rule spends 3.65 SEK/day more summed over 32 cells; 10 cells save, at most 0.34 SEK/day each. one|nodhw|shoulder|winter_cold spends +1.80 SEK/day.
- **MPC**: the warm re-solve gains at most 0.0076 %, so the stall repeats every cycle.
- **Severity**: low. **Seam rule**: partial. It covers both ftol sites through the hook, but it is a cell list, half of it at 48 h, and it has no winter prices (own: two|nodhw|winter_typical|winter_cold 0.3815 %).
- **Class**: P4.
- **Vote**: weaken. Restate the claim at 24 h (0.85 % on the #1293 claim cell) and record it as a re-find of an owner-refused knob.

## D0-s2-02: the seed set misses lower basins on shoulder prices
- **Finder re-run**: `race.py --cells shoulder,flat ... --first-only` gave shoulder max 1.2012 % (exact) and mean 0.3927 % (finder 0.3909; inside tolerance). Flat max 0.3247 % (exact). Pooled cells over 0.1 %: 14 of 32. Load1 1.60, thread_factor 1.000.
- **Own measurement**: `D0-s2-02_reach.py`, end to end, 13-seed ladder on every seam call, no polish arm. Shoulder: max 1.2012 %, mean 0.3275 %, 8 of 16 over 0.1 %, min -0.1544 %. Flat: max 0.3247 %, mean 0.0915 %, 6 of 16 over 0.1 %. thread_factor 1.000, load1 3.24 / 1.99.
- **Attacks**:
  - Excess over flat: 0.88 pp on the headline cell, 1.17 pp on one|dhw|shoulder|shoulder.
  - one|nodhw|shoulder|winter_cold is mostly D0-s2-01's residue (polish 0.8523 %, ladder 0.8915 %).
  - Money: the headline cell spends +1.00 SEK/day; only 4 of 16 cells save (max 0.10 SEK/day); the sum is -3.81 SEK/day.
  - This re-finds #1294 (ladder refused on cost). `_CERT_CLAIMS` already records the same basin miss at one|summer_negative|shoulder and one|winter_narrow|shoulder.
- **MPC**: the warm re-solve gains at most 0.0014 %.
- **Reach**: the default install (single zone, 24 h).
- **Severity**: low. **Seam rule**: demonstrated-only; shoulder and flat only, while the stated property covers every price shape.
- **Class**: P4.
- **Vote**: weaken. The claim should say the objective gap is paid for in money (negative net SEK) and that the finding re-finds #1294.
