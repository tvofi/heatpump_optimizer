# D7 — architecture and maintainability, audit round 6

- **baseline**: `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9, the round-5
  completion stamp — `tools/audit/round6/BASELINE.md`)
- **tree**: `~/audit-r6-baseline`, an export with no `.git`
- **python**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`
  (3.11.5, numpy 2.4.6, scipy 1.17.1); every command below runs from the export
  root with `PYTHONPATH=tests/hastub`
- **machine**: 8-core Apple M1, 8 GB, darwin arm64
- **contention**: the fan-out was live throughout; `load1` was 7.9–12.6 at every
  measurement. Nothing in this report is a timing number, so nothing here is
  `provisional`: every value is a count or a percentage produced by the
  production arithmetic, which does not move with load.

`exposure`: **empty**. No `docs/audit-*.md`, no `docs/backlog.md`, no
`gh`/GitHub read, and no earlier round's report was opened. Round 3/4/5 and
`round5-fix` directories **are** physically present in this export
(`tools/audit/round3/D7/sysid_plant.py`, `round5/D7/seat-a/sysid_step_bias.py`
and the `ledger/*.tsv` files) — the export was not stripped as the task
supposed. I did not open them, and nothing below cites them. What I did read
that carries earlier-round ids is `tests/features.py`, which is part of the
tree under audit: it pins the claims D7-01 below contradicts.

## Method

The brief's item 2 is the loaded instrument, so it was built first:

`tools/audit/round6/D7/sysid_common.py` drives **one complete production
sysid experiment** on a shipped preset plant — the call sequence
`coordinator._run_system_identification` makes, argument for argument — with the
house advanced by the production `ThermalModel` and the room sensor the only
contaminated input. At zero noise the fit reproduces the plant's own UA to
1.3e-12 %, which is what says the rig is the production plant and not a
re-implementation: the fit's rollout and the rig's house are the same object
with the same `ThermalParameters`.

Two facts make this the right seam for item 2. `_finish` (sysid.py:978) routes
to `identify_slab` whenever `_slab_pair` is set, and `arm` sets it on every
declared plant — so the two-state fit is what production runs, and it confirms
**-0.00 %** on all three presets at zero noise, exactly as the tree's own test
at `tests/features.py:34500` asserts. The interesting number is therefore not
the *specification* error but the estimator's variance at the sensor noise the
tree itself prices as adoptable.

## Findings

### D7-01 — the production sysid adoption gate admits UA errors up to 28.7 % at the sensor noise the ratification prices as adoptable

**Claim.** On the three shipped building presets, with the plant's outdoor
temperature, thermal power and state exact and the room sensor the only noisy
input, one in five of the experiments that clear the production adoption gate
identify the house's heat-loss coefficient more than 10 % wrong — worst of the
grid −28.7 % at confidence 0.978 — and `_adopt_system_identification` then
blends that value into the persisted heat-loss scale at that confidence.

**Instrumented symbol:** `sysid:SystemIdentification.identify_slab`.

**Metric:** `admitted_and_biased` = the number of grid cells that both clear
`result.completed and result.confidence >= 0.3`
(`coordinator.py:10450`) and carry `|100·(identified UA − plant UA)/plant UA|
> 10`, over a seeded grid of presets × room-sensor σ × seeds. The key is the
**UA value the production seam delivers** (`SysIdResult.heat_loss_kw_per_c` →
`_adopt_system_identification`'s `scale`), never an input attribute.

**Command:**

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round6/D7/sysid_adoption_bias.py
```

**Executed numbers** (96 experiments, 12 cells, `load1 = 12.0`,
`thread_factor = 1.000`):

| RESULT | value | unit |
|---|---|---|
| `experiments` | 96 | count |
| `admitted` | 75 | count |
| `admitted_and_biased` | 14 | count |
| `admitted_biased_share` | 0.186667 | ratio |
| `worst_adopted_bias_cell` | `typical_slab/sigma0.02/seed5` | label |
| `worst_adopted_bias` | −28.7018 | % |
| `worst_adopted_confidence` | 0.97751 | 0–1 |
| `bias_max_heavy_old_sigma0.01` | +22.5461 | % |
| `bias_min_heavy_old_sigma0.01` | −20.2859 | % |
| `bias_min_typical_slab_sigma0.02` | −28.7018 | % |

Per-cell bias range, so a reader can see which plants carry it (min / max / mean
of the identified UA's error, %):

| preset | σ=0.00 | σ=0.01 | σ=0.02 | σ=0.03 |
|---|---|---|---|---|
| light_new | −2.1e-14 / −2.1e-14 / −2.1e-14 | −2.65 / +5.08 / +0.43 | −2.63 / +3.19 / +0.06 | −4.02 / +4.74 / +0.05 |
| heavy_old | 0.0 / 0.0 / 0.0 | −20.29 / +22.55 / +1.60 | −6.35 / +20.61 / +3.10 | −9.82 / +15.29 / +1.06 |
| typical_slab | −1.3e-12 / −1.3e-12 / −1.3e-12 | −12.65 / +19.35 / +1.90 | −28.70 / +16.58 / −1.76 | −14.52 / +18.65 / −0.27 |

Every cell's *mean* is within ±3 %, so this is a variance failure rather than a
bias in the estimator's centre — which is exactly why it is invisible to the
confidence the fit reports. The harm is per-install: `min_days_between_runs` is
30, so a user gets **one** experiment, adopts it at weight ≈ confidence
(`coordinator.py:10470-10473`), and persists the result
(`_async_save_thermal_learning`).

**Perturbation (the judge runs it):** `--sigmas 0.0` → `--sigmas 0.02`.

| arm | `admitted_and_biased` | `experiments` | `admitted` |
|---|---|---|---|
| `--sigmas 0.0` (null control) | **0** | 24 | 24 |
| `--sigmas 0.02` (perturbation) | **6** | 24 | 17 |

Direction **up**, as required. The null-control arm's largest |bias| over all 24
experiments is 1.3e-12 % — the fit is exact when the sensor is.

**Leave-one-out** (12 cells = preset × σ; cell statistic = the worst |bias| in
that cell): cells 12, `min` 0.0 %, `max` 28.7018 %,
`drop_most_favourable` 22.5461 %. Dropping the single most favourable cell
changes nothing about the claim (11 cells still carry a worst-cell |bias|
> 4 %).

**Severity `high`; stop-rule class `bug`.** An opt-in feature
(`DEFAULT_SYSID_ENABLED = False`, `const.py:563`) whose entire product is one
adopted parameter that multiplies the house's heat loss in every solve — and a
wrong UA is wrong money and wrong comfort, published silently. Not `critical`
only because a user must switch it on.

**Mechanism.** The ported intercept ridge (`SLAB_INTERCEPT_PRIOR_SD_KW = 0.1`,
sysid.py:345) is one pseudo-observation on G weighed against the whole residual
vector; the comfort bound holds the experiment's ΔT within a few percent of its
mean (sysid.py:341-345 says so itself), so UA and G are collinear and a ridge on
G does not buy UA an error bar. The confidence
(`_slab_confidence`, sysid.py:606-624) is R² × row count × excursion × residual
SNR — none of which is the **UA standard error**, so a window whose residuals
look clean reports ≈1.0 while its slope is 29 % off.

**Proposed fix scope.** Either widen the ridge's own report into a refusal — an
adoption gate on the UA's *own* uncertainty (a profile-likelihood interval, or
the ratio of the ridge's pull on G to the fit's curvature), which turns the
confidences above into refusals — or price the fitted UA's uncertainty into the
blend weight instead of using R²-class confidence. A one-line fix is not
available: the confidence formula has no term for the parameter of interest.

**Files:** `custom_components/heatpump_optimizer/sysid.py` (341-360, 606-624,
1474-1515, 1517-1590), `custom_components/heatpump_optimizer/coordinator.py`
(10447-10485). **Expected golden drift:** none — the fix changes which
experiments adopt, not the solver's arithmetic on any golden scenario.

### D7-02 — a 379-line production method has no production caller, and the ratchet's dead-code metric cannot see it

**Claim.** `SystemIdentification.identify` — the first-order regression, its
errors-in-variables correction, its sensor-drift column and its settle
cross-check — is entered **zero** times by the only call sequence production
uses, because `arm` sets `_slab_pair` on every declared plant and `_finish`
then routes to `identify_slab`; meanwhile `tests/structure_budgets.json`'s
`dead_top_level_symbols` row reads 0 for a rule that walks module-level
definitions only, while the package holds 1 statement that can never execute.

**Instrumented symbol:** `sysid:SystemIdentification.identify`.

**Metric:** `identify_calls_production_path` = the number of times the
production method is entered while one complete experiment runs on a shipped
preset with a declared plant, counted by a runtime sentinel wrapping the
method. The key is the **call taken at runtime**, not the source: a fix that
deletes the method moves `identify_loc` to 0, and a fix that routes production
back to it moves the count.

**Command:**

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round6/D7/production_dead_paths.py
```

**Executed numbers** (`load1 = 12.6`, `thread_factor = 1.000`):

| RESULT | value | unit |
|---|---|---|
| `identify_calls_production_path` | 0 | count |
| `identify_slab_calls_production_path` | 1 | count |
| `sizer_one_state_calls` | 0 | count |
| `sizer_two_state_calls` | 1 | count |
| `identify_loc` | 379 | lines |
| `production_call_sites_identify` | 2 | count |
| `production_call_sites_identify_list` | `sysid.py:982,sysid.py:1422` | paths |
| `dead_statements_unreachable` | 1 | count |
| `dead_statement_at` | `optimizer.py:2100:Return` | site |

Both production call sites of `identify` are **inside `sysid.py` itself** —
line 982 is `_finish`'s `else` branch and line 1422 is `identify_slab`'s
own no-plant guard — so no coordinator path reaches it, and the guard's
precondition (`_slab_pair is None`) is exactly the one `arm` makes impossible
on a declared plant. The companion one-state sizer `_predict_step_excursion`
(sysid.py:63-94) is likewise entered 0 times: its only remaining caller is the
`_LOGGER.debug` at sysid.py:803.

`dead_statements_unreachable = 1` is `optimizer.py:2100`, a second
`return cost_batch` after the one at 2098 in
`optimizer._terminal_cost_batch` — a duplicate statement the ratchet's
`dead_top_level_symbols` row (0) cannot represent, because
`tests/structure.py:903` only walks `top_level_defs`.

**Perturbation (the judge runs it):** `--no-plant` — drop the `plant=`
declaration from the arm call, which is the only input `_finish` routes on.

| arm | `identify_calls_production_path` | `identify_slab_calls_production_path` | `result_completed` |
|---|---|---|---|
| default (`plant=`) | **0** | 1 | 1 |
| `--no-plant` | **1** | 0 | 0 |

Direction **up**, as required.

**Severity `low`; stop-rule class `hygiene`.** No user sees this. It is real
dead weight with a cost beyond lines: 11 of the tree's sysid checks in
`tests/features.py` (from `:18093` to `:18330`) pin the behaviour of a
regression the integration never runs, so the suite's sysid coverage is
concentrated on the wrong model class — the one #1329 moved the arm gate off
precisely because its predicate refused every plant the tree ships. The
duplicate `return` is inert.

**Proposed fix scope.** Decide which of two things is true and say so: either
the one-state regression is the intended cadence-gap fallback (then
`identify_slab`'s `sysid.py:1438-1471` refusal, which currently refuses the gap
by name, is the bug and the fallback should call it), or it is not (then
`identify`, `_predict_step_excursion` and the tests pinned on them go, and
`dead_top_level_symbols` grows a statement-level sibling so the next one is
caught). Either way the ratchet is measuring the wrong granularity today.

**Files:** `custom_components/heatpump_optimizer/sysid.py` (63-94, 978-982,
995-1373, 1417-1422), `custom_components/heatpump_optimizer/optimizer.py`
(2098-2100), `tests/structure.py` (785-903).

### D7-03 — the production two-state fit raises an uncaught `OverflowError` out of the coordinator's update cycle

**Claim.** On the heaviest shipped preset, a room sensor drifting at the rate
the tree's own drift prior is written for (0.02 °C/h default,
`sensor_drift_prior_c_per_h`; 0.05-0.10 measured in the D2-03 record) makes
`SystemIdentification.identify_slab` raise `OverflowError: cannot convert
float infinity to integer` out of `_finish`, and `_run_system_identification`
has no `try` — so it unwinds through `_async_update_data` and fails the whole
update cycle.

**Instrumented symbol:** `sysid:_lm_solve`, driven through
`SystemIdentification.identify_slab`.

**Metric:** `fit_exceptions` = the number of complete production experiments
on which `identify_slab` raises instead of returning a `SysIdResult`, over a
seeded grid of presets × sensor drift × seeds. The key is the **exception
leaving the production symbol**: a fix that bounds the solver's parameters, or
guards the rollout, moves this count to 0.

**Command:**

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round6/D7/sysid_fit_exception.py
```

**Executed numbers** (default grid, 48 experiments, 12 cells, `load1 = 12.6`,
`thread_factor = 1.000`):

| RESULT | value | unit |
|---|---|---|
| `experiments` | 48 | count |
| `fit_exceptions` | 8 | count |
| `fit_exception_share` | 0.166667 | ratio |
| `exception_kind_OverflowError` | 8 | count |
| `completed_results` | 12 | count |
| `exceptions_heavy_old_drift0.05` | 4 | count |
| `exceptions_heavy_old_drift0.08` | 4 | count |
| `exceptions_light_new_drift*` | 0 | count |
| `exceptions_typical_slab_drift*` | 0 | count |

**Perturbation (the judge runs it):** `--drifts 0.0` → `--drifts 0.05`.

| arm | `fit_exceptions` | `experiments` | `completed_results` |
|---|---|---|---|
| `--drifts 0.0` (null control) | **0** | 12 | 12 |
| `--drifts 0.05` (perturbation) | **4** | 12 | 0 |

Direction **up**; the null-control arm completes all 12.

**Leave-one-out** (12 cells = preset × drift): cells 12, `min` 0,
`max` 4, `drop_most_favourable` 8 — dropping `heavy_old`/0.08 still leaves 4.

**Severity `medium`; stop-rule class `bug`.** One update cycle fails:
`DataUpdateCoordinator` marks the update unsuccessful (every entity of the
integration unavailable until the next good cycle) and logs the traceback, and
the experiment the user armed — a whole night of heat — is discarded with
`last_run` set, so `min_days_between_runs = 30` means it is not re-tried. It is
not `high` because it self-limits to one cycle; it is not `low` because the
user sees it.

**Mechanism.** `_lm_solve` (sysid.py:508-556) documents itself as "forward-
difference Jacobian, diagonal Marquardt damping, **projection of the linear
parameter into its loose band**" — and then clips exactly one of its three
parameters: `candidate[2] = clip(candidate[2], -5.0, 10.0)` at line 545. On the
third of the three multi-starts (`mult = 3.0`, line 1500) the iterate walks
x[0] (log UA) monotonically outward: traced on `heavy_old` at drift 0.05 the
returned log UA goes −1.17 → −100.4 (seed 1.0) → −223.3 (seed 3.0) and the
third start then overflows `np.exp(x[0])` to `+inf`. `_simulate_slab_path`
(sysid.py:455) feeds that straight into `ThermalModel.simulate_step`, where
`_stability_substeps` (thermal_model.py:2401-2474) computes
`worst = max((u_eff + k_s)/C_r, k_s/C_s)` with `u_eff = inf` and
`int(np.ceil(inf))` raises. `residual()` (sysid.py:1474) has no finiteness
guard, and `identify_slab` does not catch it.

**Proposed fix scope.** Bound the two log parameters at the same place the
third is bounded (a `candidate[0:2] = np.clip(...)` in `_lm_solve`, or
`np.clip(x, np.log(1e-4), np.log(1e4))` around the returned `x`), and make
`residual` return a large finite cost for a non-finite rollout. `_lm_solve` is
the right site: three multi-starts with one clipped parameter is the contract
its own docstring states, and the other callers of the same solver inherit the
same hole.

**Files:** `custom_components/heatpump_optimizer/sysid.py` (508-556, 1455-1515),
`custom_components/heatpump_optimizer/thermal_model.py` (2401-2474),
`custom_components/heatpump_optimizer/coordinator.py` (4921, 10391-10446).

## Non-findings (checked, held, with the number that held them)

1. **The two-state fit is exactly unbiased with an exact sensor.**
   `sysid_adoption_bias.py --sigmas 0.0` → 24 experiments, 24 admitted, 0
   biased, largest |bias| **1.33549e-12 %** (`typical_slab`). This is the
   finding's null control and also the rig's fidelity check.
2. **The ratified residual-scatter gate does fire.** 20 of the 96 default-grid
   experiments are refused, and the reason is the gate where the noise is:
   `residual scatter 0.038-0.063 C exceeds the 0.03 C noise gate` (σ=0.03 cells
   on all three presets; σ=0.02 on one seed each).
3. **The comfort bound protects the light plants from a drifting sensor.** At
   0.05 °C/h, `light_new` and `typical_slab` abort with `room temperature
   drifted beyond the allowed excursion` in 3 of 3 seeds each
   (`sysid_common.PlantRig`), so the drift reaches the fit only on the heavy
   plant.
4. **`slab_mode_identifiability` admits every plant the tree ships.** `arm`
   succeeds on all three presets in every one of the experiments above
   (`run_experiment` asserts it), matching
   `tests/features.py:34492`'s 360-combination sweep.
5. **`dead_top_level_symbols = 0` is accurate for its own rule.** Every
   module-level def/class/assignment in the package is referenced somewhere;
   the blind spot D7-02 reports is at statement and method granularity, which
   `tests/structure.py:903` does not measure. The budget file's 24 rows are
   internally consistent and I re-derived none of them.
6. **The valve-hold candidate re-solve does not corrupt stashed state.**
   `_stash_price_horizon` (optimizer.py:3022) is called once per `optimize()`
   (line 2698) and the candidate `_solve()` at line 2956 shares the same
   `initial_state`, so `self._initial_buffer_temp` and `self._price_known`
   cannot be stale between the two solves. Read, not executed — see below.

## Harnesses

| path | runnable | what it measures |
|---|---|---|
| `tools/audit/round6/D7/sysid_common.py` | no (library) | the production experiment rig, shared by all three |
| `tools/audit/round6/D7/sysid_adoption_bias.py` | yes | D7-01 |
| `tools/audit/round6/D7/production_dead_paths.py` | yes | D7-02 |
| `tools/audit/round6/D7/sysid_fit_exception.py` | yes | D7-03 |

All three carry the `tests/stress.py` thread pin before the numpy import, print
`RESULT` lines with `thread_factor`, `load1` and `swapins`, write nothing but
stdout, and set no `HPO_PLANDATA` (no Node harness is invoked). `thread_factor`
was 0.99997-1.000 on every run.

## What I could not finish

- **Item 3, the learner-freeze-versus-COP-flow matrix.** I enumerated the
  learners and their gates by reading (`_track_curve_comfort` gates away
  + indoor + `_learning_frozen`; the DHW learner takes `_learning_frozen`
  itself as its `frozen` callable and calls it with `CONF_DHW_TEMP_ENTITY`;
  `_async_learn_buffer_cooling` / `_async_learn_lower_floor_loss` /
  `_async_learn_house_heat_loss` / `_learn_measured_cop` each name their own
  keys; external heat, pump freeze, defrost and ventilation are plant-wide and
  sit ahead of the key loop), but I did **not** build the contaminated-interval
  simulation, so I have no executed number and therefore no finding here.
  The "away" gate is present on the curve learner only; whether that is a gap
  needs the simulation, not a reading.
- **Item 4, `last_buffer_trajectory`.** The symbol is gone from the tree
  (`tests/features.py:9659`: removed by R3-D7-02). What replaced it is the
  stash family `_price_known` / `_pv_surplus` / `_initial_buffer_temp` /
  `_dhw_requirement` / `_dhw_legionella_step` on `Optimizer`
  (optimizer.py:1662-1671). Non-finding 6 above is a reading of that family,
  not an executed number, and I did not test a reordering.
- **Item 5, this year's train.** Not started; no spot mutations were executed,
  so I make no claim about which additions lack a failing test.
- **Item 1's budget reading.** Beyond what D7-02 reports, I did not reconcile
  the 24 ratchet rows, per the brief's instruction not to re-derive them.

None of the three findings rests on a wall, CPU or RSS number, so nothing here
needs a quiet-window re-take.
