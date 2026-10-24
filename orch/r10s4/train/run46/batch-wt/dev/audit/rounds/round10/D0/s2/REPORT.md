# D0-s2 — round 10, price optimality (cells M4/M5/M6 x winter price profiles)

Baseline 17f1c55fad1b, macOS arm64, box B2, load1 21-94 during the fan-out (counts and objective ratios only; no timing is evidence).
Interpreter: venv-ci python, PYTHONPATH=tests/hastub. Exposure: none.

## Method
- `grid_race.py` (M4/M5/M6 one-shot): captures every `optimizer:_multi_start_minimize` call (objective, starts, bounds, args, kw) per cell and races the real function with production starts + production x + 4 bang-bang starts at maxiter 1500, then a scipy L-BFGS-B polish (ftol 1e-12), scored with the captured production objective. Grid: prices winter_typical/extreme/narrow/moderate + flat (null) x weather winter_cold/winter_mild x single/two-zone x DHW on/off, 24 h horizon (41 calls). Output `grid_race.out`.
- `ftol_race.py`: two-zone+DHW cells; gap between production x and an ftol-1e-12 polish from that same x; `--ftol` perturbs the ftol production passes to `optimizer:_scoped_minimize`. Outputs `ftol_race.out`, `ftol_race_1e-10.out`.
- `mpc_mask.py` (M6): 1-day closed loop via `tests/rolling.py:run_rolling` (exec'd up to its test body), REPLAN 2 h, plant_error 1.0; `--arm chal` (augmented challenger) or `--arm ftol`. Outputs `mpc_mask.out` (2 cells, run cut for box load), `mpc_mask_ftol.out`.

## Findings
### D0-s2-01 (low, M4): L-BFGS-B ftol=1e-6 stop leaves descent on two-zone+DHW winter solves
Production's main run and `_lbfgsb_restart` stop at `ftol 1e-6`; from the shipped x, a tighter polish lowers the production objective by up to 1.23 % (winter_moderate/winter_cold, dJ 1.29 on J 104.6), winter mean 0.20 % over 8 cells (range 0..1.23, drop-max mean 0.055 %); flat null 0.079 % mean (max 0.157 %).
Perturbation `--ftol 1e-10`: winter mean polish gap 0.20 % -> 0.009 %, shipped objective lower in 7 of 8 winter cells (mean -0.40 %, max -0.92 % winter_narrow/cold; drop-max -0.32 %), flat/cold -0.13 %; production nfev roughly doubles (408 -> 906 winter_typical/cold).
Null control: gap survives at flat (smaller) — it is a convergence-tolerance residual, amplified by winter price shape, not a seeding defect.
M6 masking: closed loop with ftol 1e-10 realises -1.26 % energy cost on winter_narrow/cold but +0.80 % / +1.50 % on winter_moderate/typical cold and +0.65 % at flat, comfort equal (min room 17.0). One-shot gap is **not consistently realised** under re-planning; severity low accordingly.
Maxiter is not binding: `grid_race.py --maxiter 50` and `--maxiter 1000` leave the two largest cells byte-identical (prod nit 25 on the top call).

## Non-findings
- Single-zone, DHW off, winter_cold: augmented challenger gap 0.0000 % on all four winter prices (grid_race.out).
- Grid aggregate (augmented challenger): winter means 0.06-0.17 %, flat 0.063 %; cells > 0.5 %: 2 of 33 winter (both two-zone+DHW cold) vs 0 of 8 flat; drop-max means 0.014-0.055 % vs flat 0.007 %.
- Step-0 action: 31 of 41 calls have step-0 |dkW| < 0.1 between production and best challenger.
- Augmented-challenger closed loop winter_typical/cold/tz1/dhw1: challenger realises +0.31 % energy cost (no saving); winter_typical/mild/tz1/dhw0: -3.8 % energy but below-17 degree-steps 0.55 -> 1.06 (buys less comfort, not cheaper).

## Unfinished
- M4: valve storage, wood, horizon 6/48 h, coordinator captures not run (box load 40-94).
- M6: augmented-challenger closed loop cut after 2 of 7 cells; realised *objective* (not just energy) not scored; multi-day loop not run.
