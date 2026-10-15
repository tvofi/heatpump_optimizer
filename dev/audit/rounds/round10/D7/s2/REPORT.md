# D7-s2 — round 10, baseline 17f1c55fad1b

Cells: D7.M2, D7.M3, D7.M4 over `**`. Run everything from the export root with
`PYTHONPATH=tests/hastub` and the venv-ci interpreter. Box B5 was heavily loaded
(load1 36-86). Every number here is a count or a deterministic float, so the load
does not affect it.

## Findings

### D7-s2-01 (M3, low, bug): the frequency map folds defrost and pump-offline intervals that every other learner refuses
`coordinator:_freq_fold_blocked` refuses only cooling, distorted draw and
`":"`-shaped (unusable-input) freeze reasons. `_observe_frequency` therefore
calls `FrequencyMap.observe` on intervals that the plant-wide gate
`_learning_frozen` refuses: `defrosting`, `pump_offline`/`pump_fault`, external
heat and ventilation. Only defrost and offline bear on an electrical kW-per-Hz
map. The COP learner reads the same meter, and on the same defrost interval its
gate returns `'defrosting'`.
- Harness: `learner_gates.py`. Result: `freq_map_defrost_folds=8` of 8
  intervals. Null arm: `clean_folds=8`.
- Perturbation: `--perturb` makes `_freq_fold_blocked` also refuse
  `defrosting`. The count falls from 8 to 0.

Learner table. INGEST means the learner's own gate admits the sample. The rows
are the contamination arms; `heat_loss` carries the gains and solar folds.

| arm | heat_loss | cop | flow_bias | buffer | curve | defrost | accuracy | freq_map |
|---|---|---|---|---|---|---|---|---|
| clean | I | I | I | I | I | I | I | I |
| external_heat | f | f | f | f | f | f | f | **I** |
| defrost | f | f | f | f | f | I (own evidence, #944) | f | **I** |
| pump_offline | f | f | f | f | f | f | f | **I** |
| open_window | f* | f | f | f | f | f | f | **I** |

\* The heat-loss learner looks past `ventilation` only to feed the CUSUM, and
it still does not fold. Away is not a freeze reason in `_learning_frozen`. The
learners replay the measured or commanded power, so away is not a contaminant
of the interval. Not measured further.

## Non-findings
- **M2:** the production sysid route (`identify_slab`) has a UA bias of
  -1.1 %, -1.6 % and -2.1 % on the three `stress.BUILDINGS` presets, with no
  noise. The adoption gate admits heavy_old and typical_slab and refuses
  light_new (interval ±15 %). Biased fits admitted (|bias| > 10 %): **0**. At
  sigma=0.02 it is again 0. The first-order `identify()` refuses all three
  presets ("drift collapsed", "gains outside bounds"), so its bias never reaches
  adoption. That route is harness-only (#1395). Perturbation `--glue-slab`
  makes the plant first-order: the first-order fit then completes on light_new
  (bias -2.6 %, admitted) and the slab fit's bias goes to 0.0000.
  **Harness gap:** the two-exponential fit takes its gain from a 2 h step. That
  step has not converged, so its -57 % to -87 % "bias" is the window, not a
  plant property. Do not cite it.
- **M4:** `last_buffer_trajectory` is not in production at this baseline (grep:
  only `RELEASE_NOTES.md` and `tests/features.py` mention it). Its successor
  state is `HeatPumpOptimizer._initial_buffer_temp`.
  - The terminal-cost closure is pure in its arguments. With another call in
    between, `second_call_delta=0`.
  - Rebuilding the closure after a different solve's `_stash_price_horizon`
    moves the cost by 13.44 (65 C start compared with 40 C, at -15 C and 3 kW
    where the charge ceiling is 35 C). `--perturb` takes that to 0.
  - That dependency is the intended per-solve floor. The two production
    builders are `_solve_objectives` and the `_settlement_caps` callers, and
    both run after `_stash_price_horizon` within one `optimize`. No reorder
    exists in production.

## Harnesses
`sysid_plant.py`, `learner_gates.py`, `terminal_state.py` (this directory).

## Unfinished
- M3: the table is gate-level for 7 of the 8 learners. End-to-end ingestion was
  measured only for `freq_map`.
- M3: `dhw_learning`'s own `_frozen` and `comfort_learner` were not tabled.

exposure: none.
