<!-- Landed from handoff/r9-diag-1 @ 3c90f86a3; paths and file:line citations are as measured at its baseline origin/main 1913f0dd7, before the R9-RO reorganisation moved tools/audit/round9/ under dev/audit/rounds/round9/. Body transcribed verbatim; this comment is the only added line. -->
# R9-DIAG-1 pre-study: boost space heating and the "model drifting faster
than the learners" warning

Field report (tvofi, 2026-10-04): after 1-2 weeks running the integration,
boost space heating used a few times over two days produced a warning that
the model drifts faster than the learner can catch up. Two deliverables:
(1) is the handling of boost usage correct, (2) is a recommend-new-house-
parameters-at-warning-time feature feasible. Study only — no fix PR.

Every claim below carries the command or harness that produced it. The
harness is `tools/audit/round9/prestudy/boost_drift_replay.py` (branch
`handoff/r9-diag-1`), run from the repository root with the seat venv:

```
PYTHONPATH=tools/audit/round9/prestudy:tests/hastub:tests:custom_components \
  ~/.local/state/hpo/venv-ci/bin/python tools/audit/round9/prestudy/boost_drift_replay.py <arm>
```

## 1. The warning and its exact mechanism

The warning is the repairs issue **"Learned model is drifting"**
(`custom_components/heatpump_optimizer/translations/en.json:1639`):

> The optimizer's predictions have been consistently off for several days,
> which usually means something about the house or the system changed faster
> than the learners can follow. [...]

The chain, in code:

| step | where | what |
|---|---|---|
| statistic | `AccuracyTracker.temperature_bias()` (`accuracy.py:284`) | signed mean of `predicted_temp − actual_temp` over the **entire** sample deque (`HISTORY_LENGTH = 672` intervals ≈ 14 days at the 30-min default) |
| counting | `SnapshotRing.observe_bias` (`snapshots.py:111`) | once per calendar day; out of band when \|bias\| > `BIAS_BAND_C` = 0.5 °C |
| trip | `snapshots.py:145` | `BIAS_TRIP_DAYS` = 5 consecutive out-of-band days → `alarmed` |
| raise | `coordinator._async_watch_learning_drift` (`coordinator.py:9292`, issue at `:9374`) | persistent WARNING-severity repair issue `accuracy_drift`; auto-rollback to the newest qualifying weekly snapshot only when `_drift_inputs_healthy` (all counted days passed `_inputs_healthy`), at most once per alarm (`_rollback_done_for_alarm`) |

`_inputs_healthy` (`coordinator.py:9280`) asks `_learning_frozen` over the
indoor, outdoor and power entities. **Boost — in neither surface — freezes
learning** (`_learning_frozen`, `coordinator.py:6125`, checks external heat,
pump signals, defrost, unusable inputs, ventilation only), so boost days
count as *healthy inputs*: a boost-caused drift is judged rollback-worthy.

What "catching up" means mechanically: there is no reset or re-seed. The
interval learners take bounded Newton steps — `learner_newton_step`
(`thermal_model.py:1563`) with `HOUSE_LOSS_ALPHA = 0.02`, per-sample step cap
`HOUSE_LOSS_MAX_STEP = 0.05`, trust region ±0.5, residual guard
`HOUSE_LOSS_MAX_RESIDUAL = 1.0 °C` — and the COP learner walks an EWMA-gated
scale at `COP_LEARNING_ALPHA`. A parameter knocked far from truth relearns at
roughly 2 % of the remaining gap per accepted sample: **weeks-scale
recovery, by design.** `AccuracyTracker.trust()` does NOT damp the learners;
it only lifts the comfort floor margins (`coordinator.py:8729`).

The learners watched by this mechanism, and what the boost actuation does to
what they observe:

- **House heat-loss learner** `_async_learn_house_heat_loss`
  (`coordinator.py:4710`): replays the elapsed interval through the live
  model with the **measured** power (`_interval_space_power`, `:3970` — with
  a power meter the pump's real draw wins; a commanded-vs-measured gap over
  `COP_TRACKING_ERROR_GATE = 0.3` skips the sample) and folds the residual
  into `house_heat_loss_scale`, persisted every 10 samples.
- **COP learner** `_learn_measured_cop` (`coordinator.py:4312`): folds
  `commanded / measured` into `cop_scale`, gated by a walking EWMA of the
  ratio (a persistent shift "unlocks folding within a handful of intervals").
- **Curve learner / flow bias / comfort learner**: the curve learner's daily
  comfort evidence (`_track_curve_comfort`, `:8816`) only reads *dips below
  the floor* — boost pushes the room up, so it contributes nothing; the
  comfort learner folds manual setpoint overrides only, and the boost switch
  is not one.
- **The accuracy record** `_record_accuracy` (`coordinator.py:9667`): pairs
  the previous interval's `predicted_temp` — the **plan trajectory's** next
  step (`_predicted_next_room_temp`, `:9964`) — with the measured room. In
  the **global** `boost` mode the prediction is properly suppressed (the
  mode gate at `:9971` returns None "pairing that stale prediction against
  reality would charge the model with errors it never made"). In the
  **boost-channel surface** (`boost.py`, the space-heating switch) `_mode`
  stays `auto`: the plan keeps promising, the overlay
  (`boost.overlay`, `boost.py:131`) actuates nameplate power at the
  `max_temp` setpoint, and the sample is recorded — the two boost surfaces
  are treated differently by the same mechanism. (EG-B9/#1765's
  copy-before-overlay fixed the actuation side of this asymmetry; the
  learning side is unhandled.)

## 2. Harness

`boost_drift_replay.py` drives, per cycle, in `_async_update_data`'s
production order: frozen clock → fake-bus sensor states (indoor, outdoor with
units, power in kW, solar in W/m²) → `_update_current_state` (every interval
learner runs here, replaying the elapsed interval against the previous
cycle's overlaid action) → a real `HeatPumpOptimizer.optimize` solve on the
coordinator's own live model (the one the learners correct), adopted through
`boost.adopt_plan` → the boost channel overlay exactly as the switch leaves
it → the **true house** (a second `ThermalModel`, same class, with the true
heat loss) advancing one step under the actuated action with a thermostat
cap at the action's setpoint → `_record_accuracy` → once per calendar day
`_async_watch_learning_drift`.

The true house's weather is the same analytic weather the solve forecasts
(perfect forecast) and the sensors read, so the only plant/model differences
are the ones under test. 16 days; boost = 3 × 2 h per boost day at 07/12/18h
(tvofi: "a few times over two days" → days 8-9). Arms:

| arm | true loss vs configured | boost | surface |
|---|---|---|---|
| `null-no-boost` | equal (model correct) | none | — (null control) |
| `boost-model-correct` | equal | 2 days | boost channel |
| `boost-model-wrong15` | true 15 % lossier (learner has real work) | 2 days | boost channel |
| `global-mode-boost-null` | equal | 2 days | mode select |

Variant runs: `DIAG_BOOST_DAYS=8,9,10,11,12` (five boost days),
`DIAG_DT_MIN=60` (60-minute optimization interval).

## 3. Findings — diagnosis

### F1 (defect, measured): boost corrupts the persisted heat-loss scale to
the trust-region floor; recovery takes days

Day-by-day `house_heat_loss_scale` (JSON in the branch's run outputs; the
table below is from `out*/<arm>.json` `daily` rows):

| day | null (no boost) | boost, model correct | boost, wrong15 | global-mode boost |
|---|---|---|---|---|
| 7 | 1.0424 | 1.0424 | 1.2036 | 1.0424 |
| 8 (boost) | 1.0451 | 1.0451 | 1.2064 | 1.0451 |
| 9 (boost) | 1.0472 | **0.7246** | 0.8774 | **0.7246** |
| 10 | 1.0478 | **0.5221** | 0.6729 | **0.5221** |
| 11 | 1.0482 | 0.7984 | 0.9547 | 0.7984 |
| 12 | 1.0495 | 0.9526 | 1.1114 | 0.9526 |
| 13 | 1.0502 | 1.0122 | 1.1726 | 1.0122 |
| 15 | 1.0489 | 1.0442 | 1.2048 | 1.0442 |

Two days of boost-channel use move a converged, persisted parameter by
**−50 % — exactly the trust-region bound (`_LEARNER_TRUST_REGION = 0.5`)** —
and the learner walks it back over ~4 further days. The null arm is flat.
The corruption is identical in the global-mode arm, so it is **not** the
accuracy-record asymmetry (§1): it is the interval replay.

Named cause: `_async_learn_house_heat_loss` replays the elapsed interval
from `_last_house_sample` — the coordinator's model plant state, whose slab
is propagated **open-loop from the previous plan's own trajectory**
(`coordinator.py:6106`+, `_open_loop_plan_value`) or seeded room+1 K. A boost
overlay overrides the actuation that trajectory assumed, so the **true
house's slab absorbs heat the model's plant state never sees**. Every replay
during and after a boost therefore starts from a plant state that is too
cold: the measured room comes in warmer than the replay predicts, the
residual is warm-side, and `learner_newton_step`'s `delta_u =
−residual·C/(ΔT·dt)` ratchets the scale down 5 % per accepted sample until
the trust region stops it. The mis-modelled quantity is the plant state the
replay integrates from, at `coordinator.py:4710` (residual at `:4830`,
fold at `:4866`); the failing scenario is the harness above. `_learning_frozen`
has no boost reason although its own docstring (`:6128`) states the class
this belongs to: "a learner that trains on … heat it did not supply corrupts
a parameter that is persisted to disk."

Falsified alternatives (same runs): it is not the COP learner (`cop_scale`
stays 1.0000 in every arm); it is not the accuracy bookkeeping (global-mode
arm identical); it is not the plan (null arm flat).

### F2 (measured): the accuracy record is contaminated by boost-channel
intervals, but the contamination is small

Boost-interval one-step errors (predicted-plan vs boosted-actual): n=24,
mean −0.169 °C (boost-model-correct arm). Whole-deque `temperature_bias`
moves from −0.018 to −0.044 °C. The channel surface does charge the model
with override-caused errors the global surface suppresses (§1), but in this
scenario the deque mean stays an order of magnitude inside the 0.5 °C band.

### F3 (measured): the alarm did NOT fire in the base scenario

No arm reached `alarmed`; `bias_days` never left 0. Worst daily bias −0.082 °C
(60-min-interval variant, day 11) with `house_heat_loss_scale` at 0.80 —
still 6× inside the band. A 50 %-wrong heat-loss scale does not by itself
push the 14-day deque mean past 0.5 °C in a single-zone January scenario:
the plan re-solves from the sensor every cycle, so the one-step error stays
small even while the parameter is badly wrong.

### F4: the aggravated variants do not close the alarm gap either

| variant | interval | boost days | worst daily bias | hh floor | alarmed |
|---|---|---|---|---|---|
| base | 30 min | 2 | −0.044 °C | 0.522 | no |
| five boost days (`runs/boost-model-correct-5days.log`) | 30 min | 5 | −0.045 °C | **0.443** | no |
| 60-min interval (`runs/boost-model-correct-60min.log`) | 60 min | 2 | −0.094 °C | 0.739 | no |

Five consecutive boost days compound the corruption below the single-window
trust-region floor (0.522 → 0.443 — the region is relative to *current*), and
the 60-minute interval roughly doubles the visible bias (each sample's
prediction is two steps ahead), but the whole-deque bias stays ≥ 5× inside
the 0.5 °C band. The vent CUSUM never trips in any run (warm-side residuals
stay under the clip), and no learner freeze ever engages (`freeze_reason`
None throughout). In a single-zone house with a perfect forecast, no
boost-reachable learner corruption produces five days of > 0.5 °C mean bias
through this statistic: the plan re-solves from the sensor every cycle, so
the one-step error stays ≲ 0.1 °C even while the parameter is 56 % wrong.

### F5: verdict on the field report

Two findings, both measured, and they pull apart:

1. **The learner's handling of boost is defective.** Two days of boost
   space-heating use crash the persisted `house_heat_loss_scale` by −50 %
   (to −56 % under five days of use), and the recovery walk takes ~4 days
   at the learner's designed 2 %-per-sample pace. During those days the
   model plans against a house it believes loses half the heat it does.
   That is precisely the field report's phenomenology — the model's
   behaviour moves far under ordinary boost use and the learner cannot
   catch up for days — and it is a defect with a named cause (F1), not the
   designed signal: nothing about the house changed.

2. **The alarm tvofi saw is not reproduced by that defect** in the tested
   envelope (single-zone, perfect forecast): the temperature-bias statistic
   stays an order of magnitude inside its 0.5 °C band. For the alarm to
   have fired, tvofi's install must carry an amplifier outside this
   envelope — the leading untested candidates are a two-zone house (the
   learner's own comments describe a 1.5 K zone split injecting +0.53 K of
   systematic residual, `coordinator.py:4790`), real forecast error, or
   learners still far from convergence when the boost days hit (a 1-2-week
   install). It is also possible the alarm was partly honest — a genuine
   house or sensor change coinciding with the boost use — but the boost
   corruption above would have degraded the model over the same days
   regardless.

So: the warning *fired* through the designed #42 gate (its text is the
closest string in the tree to tvofi's description), and the handling behind
it — the learners' behaviour under boost — is **not correct**, by
measurement. The honest statement of scope: F1 is a proven defect the fix
group can take; whether F1 alone explains the alarm firing on tvofi's
install is **not established** by this study, and the two-zone arm is the
named follow-up measurement.

## 4. Feasibility: recommend house parameters at warning time

Verdict: **feasible, with a bounded claim and one data requirement.**

What the drift evidence holds at warning time (all already in the
coordinator):

- `AccuracyTracker.samples` — up to 672 intervals (14 days; last 192
  persisted): predicted/actual room temperature, predicted/actual power,
  outdoor temperature, humidity, COP residual per interval. This is the
  same evidence the alarm judged, which is the right property: the
  recommendation is accountable to what raised the warning.
- `SnapshotRing` — weekly learner payloads tagged healthy/in-band; during
  an alarm only pre-streak snapshots qualify (`best_restore`), i.e. the
  *last known good* parameter set already exists in the tree.
- Boost-window knowledge — live only. **Data requirement:** boost intervals
  are not recorded in the samples and the boost store persists only active
  windows, so a recommendation that must exclude boost rows (as below)
  needs the boost channel state tagged onto `AccuracySample` (or the
  windows persisted). Cheap, and the fix group below includes it.

Estimator (measured, `boost_drift_refit.py` over `runs/`): the same Newton
relation the learner uses, batched over the drift window's non-boost
samples — one least-squares step instead of days of 2 % steps:

| evidence window (wrong15 arm, true scale 1.15) | n | learner's value then | batch refit |
|---|---|---|---|
| day 10, just after the boost days | 84 | 0.673 | 0.576 |
| day 12, three settled days | 180 | 1.111 | **1.138** |
| day 12, boost rows included | 192 | 1.111 | 1.093 |

Null control (no-boost arm, true scale 1.00): the refit on clean data
answers 0.929-0.931 — the estimator's own bias floor is ≈ −7 % here,
dominated by the open-loop plant-state (slab) lag that also sets the
learner's residual noise floor. So the honest shape of a recommendation is
a **value with a confidence band of roughly ±10 %**, and it must wait for
~2-3 settled days of post-change data (the day-10 refit is as corrupted as
the learner — the plant state the predictions were made from had not yet
re-equilibrated). Boost inclusion moves the day-12 answer by only −0.045 in
this scenario, but the exclusion is still correct by construction and the
amplified scenarios would lean on it.

What it can bound, from what: `house_heat_loss_scale` from temperature
pairs (every install); `cop_scale` from the power pairs on the same window
(power-meter installs, same batch ratio the COP learner folds — bounded
and one-sided in the same way). What it cannot bound: anything the window
does not excite (zone splits, slab coupling — a single-zone sensor sees
none of it), which is why the recommendation pairs the refit with the
snapshot alternative.

Restart shape (recommend-only):

- Surface: a new advisor sensor (`*_model_restart_advisor`, the R9-UX-2
  #1795 pattern) rendered as an inbox row in the card's Advisor tab. The
  row states the drift, and offers up to two restart points with their
  evidence: **"restore last known-good"** (snapshot values, pre-streak) and,
  when ≥ 2 settled days of post-drift evidence exist, **"adopt refit"**
  (batch estimate + band). Accepting either applies through the existing
  `_apply_learner_payloads` restore machinery (`coordinator.py:9197`) — the
  same code path the rollback service uses, on an explicit user action.
  Nothing auto-applies; the alarm's existing auto-rollback is unchanged.
- Safety: recommend-only everywhere; the accept action is one-click but
  explicit, logged, and reversible (the pre-restart state can itself be
  snapshotted on apply).

Risks: the ±10 % band on a wrong recommendation degrades plans no worse
than the corrupted state it replaces (measured: a 50 %-wrong scale still
held ≤ 0.1 °C one-step error in this envelope — comfort-safe but
cost-suboptimal); the settled-days requirement means the recommendation
appears days after the alarm, which is acceptable for a weeks-scale
learner; the two-zone identifiability caveats above.

## 5. Proposed group (roster-ready)

**R9-DIAG-1F "boost does not corrupt the learners"** — one fix PR:

- Scope: freeze the interval learners and the accuracy pairing during
  boost-channel windows (plus a short settling tail for the plant-state
  divergence, ~2 h), symmetrically with the global-mode gate; tag boost
  intervals on `AccuracySample` (the feasibility data requirement).
- Files: `coordinator.py` (`_learning_frozen` gains a boost reason sourced
  from `boost.held_for(coord)` — noting the ventilation pass-through
  pattern so the vent detector keeps its feed; `_record_accuracy` /
  `_predicted_next_room_temp` suppress or flag the plan-based prediction
  while the overlay is live), `boost.py` (expose the live-window check),
  `accuracy.py` (the sample tag), `snapshots.py` untouched.
- Tests: the harness scenario as a failing-first arm in `tests/features.py`
  style — converged scale, two boost days, assert `house_heat_loss_scale`
  stays within a few % of pre-boost (the null arm already proves the
  machinery); mutation: remove the freeze reason and watch the crash
  return. The `boost-model-correct`/`global-mode-boost-null` arms of
  `boost_drift_replay.py` are the starting harness; they move in-tree with
  the PR.
- UI: none in this group.
- Risks: freezing learning during boost starves the learners of exactly
  the high-power intervals that carry the most information — measured cost
  here is zero (the null arm converges on plan-power intervals alone), but
  the fixer should keep the freeze scoped to the overlay windows, not the
  whole boost mode.

**R9-DIAG-2S "restart recommendation at warning time"** (the feasibility
group, separate because it is a feature, not a repair): new advisor sensor
+ card inbox row + the batch refit + accept-through-restore; per §4. Sized
as a medium PR against `accuracy.py`/`coordinator.py`/`sensor.py`/the card;
the refit is ~60 lines and already measured.

**Follow-up measurement (not a fix):** the two-zone boost arm, to establish
or refute whether the alarm firing on tvofi's install is explained by the
zone-split amplifier; harness extension of `boost_drift_replay.py`
(two-zone config, upper-floor sensor).

