# D3-s3 — test-suite gaps, cells: files "rest", steps M1–M5 (baseline 17f1c55fad1b)

## Method
- M1: 18 mutants, hand-weighted (no RNG; weights in `mutants.py`), ≤3 per module, over power_guard, wear,
  silent_mode, early_cutoff, curve_learning, setpoint_check, pump_arbiter, dhw_draws, notifier,
  comfort_band, away. Guards on hysteresis, clamps, floors, thresholds, presence polarity.
- M2: `prescreen.py` runs each mutant in a clean detached worktree lane, closure scripts from
  `tests/closures.json` cheapest-first (stress/edge/backtest and structural/meta scripts skipped,
  list in the harness), stop at first non-zero exit. Differential arm: `drift_check.py` commits the
  mutant on top of the baseline (env_drift refuses a ref that resolves to HEAD) and runs
  `env_drift.py --all 17f1c55…`. Controls: clean features.py rc=0 (4107 checks); drift CTRL rc=0
  (56 scenarios). A first run in the export tree itself was voided (`laneA-dirtytree-void.out`):
  entities.py's closure-workflow check fails on the export's uncommitted edits.
- Results: 16/18 killed by assertion scripts (features.py 8, entities.py 7, config_flow_steps.py 1).
  M15 and M18 passed every closure script and env_drift --all (rc 0). `equiv.py` shows both are
  equivalent mutants: M18 diff=0 on 32 probes (the fall-through "named zone" branch also returns True);
  M15 diff=0 on non-negative energies, and its only caller clamps energy ≥ 0 (dhw_learning.py:418).
- M3/M4: no non-equivalent survivor, so no candidate for the quiet-window full gate; no findings.
- M5: golden.py ran 229–548 s per mutant against a recorded 0.9 s (closures.json documents the stub,
  #934); entities.py 330–433 s (recorded 260), features.py 558–710 s (recorded 598), provisional,
  load1 3–45. Every "rest" module shares one ~21-script closure, so any edit costs ~25 min of
  pre-screen. Duplicated coverage: none observed — each mutant was killed by the first of
  entities/features reached; scripts ordered after the killer were not run, so overlap is unmeasured.

## Findings
None.

## Unfinished
- M1: 18 mutants, below the brief's 30–40 (each costs ~25 min wall on the shared box).
- M5: kill-overlap matrix (run every script for every mutant) not taken.

## Harnesses
mutants.py, prescreen.py, drift_check.py, equiv.py; outputs laneA/B/C.out, ctrl.out, drift_ctrl.out,
drift_survivors.out.

## Exposure
none.
