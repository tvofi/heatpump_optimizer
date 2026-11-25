# Class sweep: N-confounded-learner (round 11, D14 steps 3-4)

Mechanism: an online estimator absorbs the error of an unmodelled or mis-modelled
covariate into the parameter it learns. Class status in `bugclasses.json`: `open`,
no detector, no barrier (R10 instances 4, `barrier_refusal` on record).

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep_N_confounded_learner.py` lists every
learner-update def (`learn_*`, `observe*`, `_fold_*`, `ingest*`) and every call into
a shared covariate split (`space_heat_kw`, `ran_hot_water`, `learner_newton_step`)
across `custom_components/heatpump_optimizer/`: 55 seams at `handoff/audit-r11-register`.

- Positive control: re-finds the seam of D12-s3-03, D2-s3-09, D2-s3-11 and D7-s2-01.
- Null control: 0 seams on a clean one-function fixture.
- Perturbation: one added `_fold_gain` line moves the count 0 -> 1.
- `--controls` prints all three and exits 0 only when all hold.
- Known gap: comfort learning (D7-s2-01's comfort arm) uses names the regex
  misses; it is carried in by the finding, not by the enumerator.

## Dispositions

**Instances (judged sites, beyond_finding false):** `heat_energy.space_heat_kw`
(D12-s3-03), `DrawRange.observe_ceiling` (D2-s3-09), `_fold_internal_gains`
(D2-s3-11, D7-s2-01), `dhw_learning.async_learn_usage` and comfort quiet evidence
(D7-s2-01).

**Instances beyond the findings (2):** `probe_N_unobserved_dhw.py` fails (exit 1):
an unobserved interval whose plan split says space-only but where the pump ran hot
water gives `space_heat_kw=6.0` and `ran_hot_water=False`.
- `coordinator._fold_measured_cop` (line 5034 gates only on `ran_hot_water`), so an
  unplanned charge enters the COP learner as a space sample.
- `coordinator._async_learn_lower_floor_loss` reads `_interval_measured_heat_kw`
  (line 1010), the same attribution D12-s3-03 found in the house learner.
The probe covers the shared root. A per-consumer value probe is owed by the fixer.

**Guarded:** the rest of the 21 persisted learners. D7-s2-01's enumerator
(`D7/s2/enum_m3.py`) found 18 of them away-frozen. Interval learners go through
`_learning_frozen` (external heat, pump signals, defrost, unusable input) and
`boost.space_learning_frozen`. House and lower-floor solar/sunlit folds carry
the R10 `#2223` value pins in `tests/features.py`.

**Not applicable:** these seams are state machines or recorders and estimate no
parameter that a covariate could bias: `_fold_away`, `debugger.observe`,
`disinfection.observe`, `heat_energy` observe/mode/cycle/counters,
`pump_arbiter._observe`, `snapshots.observe_health`, `ledger.observe_*`,
`tariff.observe`, `defrost.py:750` flag observe.
`price_model.observe_day*` learns from prices alone, with no physical covariate.

## Barrier proposal

Promote the enumerator to a `tests/` check with a registration list: every learner
seam has to name its covariate guard or carry a covariate-error probe. This is the
R10 RCA arm that was never built. Static only, so the gate cost is under 1 s.
