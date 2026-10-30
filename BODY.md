# Design note, round 2: r10-cop-gate-vent (R10-COP-GATE item E, carries 8 and 9)

Tree measured: origin/main 1afdef8872a5da2eedff32916c1095e114198fae. Every line number below was re-measured there. Round 1: handoff-body/r10-cop-gate-vent at ce5ca88b. Review: `Design review: revise` at handoff-body/r10-cop-gate-vent-drev.

## Deviation (unchanged from round 1)

The payload gives this seat the probe role: read-only, no code to any ref. **Nothing was pushed to `design/R10-COP-GATE-vent`, so there is no design SHA.** The harness source is in Appendix A, ready to commit as `dev/audit/harnesses/r10_cop_gate_vent.py`. Whoever commits it owes the `tests/closure.py` classification. The payload names the return ref `handoff-body/r10-cop-gate-vent-r2`, and the brief asks for a fast-forward of `handoff-body/r10-cop-gate-vent`. This body is pushed to both.

## What changed since round 1

| review point | round 1 | round 2 | evidence |
|---|---|---|---|
| 1. COP (`flow_meter.py:105` `cop_evidence`) | lift the freeze for every COP fold | **split on heat evidence.** Lift only where the heat is measured: a counter span, or a measured flow heat. **The inferred path keeps the freeze.** | arm `cop under a window`: the inferred fold moves to the `COP_SCALE_MIN` clamp (0.500), against a null of 1.056 [0.989-1.120]. The flow-heat and counter-span folds read 1.000 at the null and in both windows. |
| 2. draw-range `power_frozen` (`coordinator.py:9760`) | lift (`room_air=False`) | **stays frozen** (default) | arm `draw_range.fold under a window`: the metered range moves. No consumer judges the draw against measured heat, so a lift limited to measured heat has no site to apply to. |
| 3. harness | gate-pass only | three new arms (COP, draw-range, buffer). Each feeds a window-shaped interval through the production fold with the latch clear and reports against a no-window null. | Appendix A |
| carried: buffer row | conditional on the fixer | **settled from the topology: stays frozen** (reverses round 1) | topology read below, plus arm `buffer cooling under a window` |
| carried: site count | "15 sites" | 13 call sites plus the DHW callable, `coordinator.py:9780` named | site table below |
| carried: counter-span refusal code | not addressed | the failing test asserts `COP_REFUSED_SPAN_OPEN` | evidence plan |

## Measured (Appendix A at 1afdef8; `PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py`, venv-ci)

The cusum, learners and latch arms are byte-identical to round 1. The reviewer reproduced them, and they are not repeated here. The new arms:

```
## cop under a window, latch clear (cop_scale after 30 d; truth 1.000; 8 seeds mean [min-max]; folds; folds on an interval the window raised by >0.5 %)
inferred draw-evidence=none    k=0.00 scale=1.056 [0.989-1.120] folds=1440 window-folds=0
inferred draw-evidence=none    k=0.15 scale=0.500 [0.500-0.501] folds=1434 window-folds=1396
inferred draw-evidence=none    k=0.30 scale=0.500 [0.500-0.500] folds=1266 window-folds=1228
inferred draw-evidence=follows k=0.00 scale=1.056 [0.989-1.120] folds=1440 window-folds=0
inferred draw-evidence=follows k=0.15 scale=0.500 [0.500-0.501] folds=1440 window-folds=1402
inferred draw-evidence=follows k=0.30 scale=0.500 [0.500-0.500] folds=1440 window-folds=1402
flow     draw-evidence=none    k=0.00 scale=1.000 [1.000-1.000] folds=1440 window-folds=0
flow     draw-evidence=none    k=0.15 scale=1.000 [1.000-1.000] folds=1440 window-folds=1402
flow     draw-evidence=none    k=0.30 scale=1.000 [1.000-1.000] folds=1440 window-folds=1402
span     draw-evidence=none    k=0.00 scale=1.000 [1.000-1.000] folds=1440 window-folds=0
span     draw-evidence=none    k=0.15 scale=1.000 [1.000-1.000] folds=1440 window-folds=1402
span     draw-evidence=none    k=0.30 scale=1.000 [1.000-1.000] folds=1440 window-folds=1402
(window k=0.15: excess peak +9.5%, 30-d mean +4.02%, intervals over COP_ASK_TOLERANCE 0)
(window k=0.30: excess peak +18.5%, 30-d mean +7.83%, intervals over COP_ASK_TOLERANCE 158)
(window excess at k=0.30: peak +18.5%, mean over perturbed intervals +8.0%; k=0.15 peak +9.5%)
## draw_range.fold under a window, frozen=False (8 seeds: slope mean [min-max]; follows; engaged; planned)
k=0.00 slope=0.996 [0.991-0.999] follows=['True'] engaged=[False] planned=['None'] observed0=(1.1880120058874524, 2.453458215500379)
k=0.15 slope=1.003 [0.998-1.006] follows=['True'] engaged=[False] planned=['None'] observed0=(1.2348907444636494, 2.575870658737858)
k=0.30 slope=1.009 [1.004-1.012] follows=['True'] engaged=[False] planned=['None'] observed0=(1.2715628489730775, 2.6978193797111185)
## buffer cooling under a window, latch clear (learned C/h after 30 d; samples)
g=0.0000kW/K k=0.00 rate=1.0000 samples=1440
g=0.0000kW/K k=0.30 rate=1.0000 samples=1440
g=0.0005kW/K k=0.00 rate=1.2946 samples=1440
g=0.0005kW/K k=0.30 rate=1.3058 samples=1440
g=0.0020kW/K k=0.00 rate=2.1781 samples=1440
g=0.0020kW/K k=0.30 rate=2.2233 samples=1440
```

### What the new arms model

- **Window.** A first-order room with the default `ThermalParameters` (UA 0.15 kW/K, C 10 kWh/K), at -10 °C outdoors (outside the 0–4 °C frost band) and 21 °C indoors.
  - Emitter UA is backed out of the steady load at `emitter_design_delta_t`.
  - The flow temperature is **fixed**. A window adds `k` kW/K from 19:00 for 3 h every second day.
  - The cooler room makes the emitters take `(1+d)` times the heat. The compressor draws `(1+d)` times the power at an **unchanged true COP**.
  - Peak `d` is +9.5 % at k = 0.15 and +18.5 % at k = 0.30.
  - With a fixed flow, a 12 h room constant and no room compensation, the room never fully recovers between events (30-day mean `d` of +4.0 % and +7.8 %). This is a strong scenario and is stated as one. The inferred conclusion does not depend on it: each folded interval moves the scale by about `COP_LEARNING_ALPHA · d`, and nothing pulls it back (below).
- **COP.** 1440 intervals go through the production `_fold_measured_cop`:
  - with `_flow_bias.heat_output_kw` None (inferred);
  - with it set to the true heat (flow);
  - through `_fold_cop_evidence`, the tail `_async_learn_heat_span` calls, on counter deltas (span).

  Draw evidence is either none, or a window whose evidence says the draw follows the ask. There are 8 seeds of ±3 % draw noise. The rows report `cop_scale`, whose truth is 1.000.
- **Draw-range.** The production `draw_range.fold` with `frozen=False` takes a price-shaped ask of 1.2/1.6/2.4 kW, a draw of ask × (1+d) with ±3 % noise, and 8 seeds.
- **Buffer.** The production `_async_learn_buffer_cooling` runs on pump-off 30-min intervals. A 35 L tank (rate about 1 °C/h at the 25 K reference) loses heat to its room, and with conductance `g` kW/K to emitters at the room's temperature, which the window lowers.

### Readings

1. **The inferred COP fold moves; the measured-heat folds do not.** The inferred fold (`cop_evidence`, `heat_kw is None`) assumes the delivered heat was the ask. It folds the window's extra draw as a COP drop, whatever the draw evidence says:
   - Every window interval passes the gates (folds 1434/1440 and 1440/1440). At k = 0.15 not one interval exceeds `COP_ASK_TOLERANCE`, so `judge_ratio` folds each within the tolerance. The tracking gate (0.3) never fires on a departure that grows over 6 intervals.
   - The target is the current scale times `commanded/electrical`, so the fold has no fixed point to return to (`coordinator.py:5078-5081`, the "correction alone" note). The scale walks to the `COP_SCALE_MIN` clamp (`const.py:252`, 0.5).
   - The no-window null walks only by noise: 1.056 [0.989-1.120].
   - The flow-heat and span folds divide measured heat by measured draw. They read exactly 1.000 at the null and at both window strengths, while folding every interval.
   - **The inferred rows are this harness's positive control.** One production tail, fed the same draws, moves when its heat is assumed and holds when its heat is measured.
2. **Draw-range moves.**
   - The learned metered range `observed()` goes from (1.19, 2.45) kW at the null to (1.23, 2.58) at k = 0.15 and (1.27, 2.70) at k = 0.30, seed 0: the max is +5 % and +10 %.
   - `follows_ask` does not flip: the slope goes 0.996 → 1.009, True throughout. `engaged` stays False here, so `planned()` stays None in this scenario.
   - The quantity the latch and `planned_range` read still moves.
3. **Buffer.**
   - At `g` = 0, which is the modelled no-valve topology (below), the rate holds at 1.0000 with or without the window. This is true by construction.
   - At `g` > 0 it moves against its own null: 1.2946 → 1.3058 (+0.011 °C/h) at g = 0.0005 kW/K, and 2.1781 → 2.2233 (+0.045 °C/h) at g = 0.002.
   - `BUFFER_COOLING_ALPHA_UP` (0.02) absorbs a leakier-looking tank slowly but does not refuse it.

## Decisions

### Point 1: COP splits on heat evidence

| COP path | where | the window | freeze |
|---|---|---|---|
| counter span | `_async_learn_heat_span` (`coordinator.py:1079`), gated per cycle through `_fold_measured_cop` reaching `COP_REFUSED_SPAN_OPEN` (`coordinator.py:5041`), which `clean["cop"]` reads (`coordinator.py:5565`) | heat and electricity are both counter deltas. Arm: 1.000 against a null of 1.000. | **lifted** |
| measured flow heat | `_fold_measured_cop` with `self._flow_bias.heat_output_kw` not None (read at `coordinator.py:5048`). `judge_ratio` is skipped and `cop_evidence` divides the measured heat. | Arm: 1.000 against a null of 1.000. | **lifted** |
| inferred | `_fold_measured_cop` with no heat reading: `cop_evidence`'s `modelled_cop · commanded / electrical` | a window's extra draw folds as a COP drop. Arm: 0.500 (clamp) against a null of 1.056. | **kept** |

**Shape.**

```python
# _fold_measured_cop, replacing coordinator.py:5017-5018 and hoisting the read at :5048
heat_kw = self._flow_bias.heat_output_kw
measured_heat = heat_energy.meter_of(self).counter or heat_kw is not None
if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY,
                         room_air=not measured_heat):
    return COP_REFUSED_FROZEN
```

- The read at `:5048` becomes the hoisted `heat_kw`, so the gate and the fold judge the same evidence on the same cycle.
- A stale or unread thermal-power entity leaves `heat_kw` None. That interval is inferred and stays frozen, so the gate fails closed.
- The counter span needs no edit of its own:
  - `heat_energy.close_span` (`heat_energy.py:489`) folds the COP on `ev.clean["cop"]` alone (`heat_energy.py:513`).
  - The house and lower-floor flags of that span still carry the vent freeze through their own gates (`coordinator.py:5437`, `:5601`), so the span's fabric replay stays frozen while its COP folds.

**The refusal code changes for counter installs (reviewer's carried note).** Today, with the latch set, a counter install's per-cycle COP refusal is `learners_frozen`, because the freeze check at `:5017` comes before the counter check at `:5040-5041`. After the change it is `span_open`, and the span folds at its close. The failing test asserts the code (below).

### Point 2: draw-range `power_frozen` stays frozen

`coordinator.py:9760` keeps the default `room_air=True`. This is decided together with point 1, for three reasons:

1. The fold's learned quantity moves under a window (reading 2).
2. Nothing downstream judges the draw against measured heat, so "lift only where the draw is judged against measured heat" names no site. The consumers are:
   - `follows_ask`, read by `judge_ratio` (the inferred path only, which point 1 keeps frozen) and by `cop_observability` (`coordinator.py:7699`, diagnostics);
   - `planned` / `planned_range`, the range the plan may book;
   - `space_draw_kw` (`coordinator.py:1010`), the slab estimate.

   None reads a heat measurement. Lifting `power_frozen` on measured-heat installs would only feed window-shaped draws into the plan's booking range.
3. The same `power_frozen` gates the defrost settlement at `coordinator.py:9850` (`power_frozen in (None, "defrosting")`). Keeping the default leaves that unchanged.

Point 1's measured-heat lift does not need draw-range evidence, because `judge_ratio` is not consulted when `heat_kw` is present, and a counter install's span does not consult it either.

### Buffer row: stays frozen (reverses round 1), settled from the topology

- **Topology.** `mixing_valve.py:57-59`: `THROTTLING_MODES` = manual, smart_read, smart_write. The only non-throttling mode is `none`, and with it the only valid layout is `no_valve`: `const.py:436-446` (`topology_layout_valid`) and `topology.py:407-417` (edges heat_pump→buffer_tank→upper_zone, plus lower_zone on two-zone installs).
  - The throttling modes are already refused by the learner (`coordinator.py:5323-5324`).
  - In `no_valve` the model makes the tank a pass-through: emitter draw is the pump's heat (`thermal_model.py:3349-3352`, `:3390-3392`). So the **modelled** pump-off draw is zero.
- **The hardware.** The space circulation pump is not a model term. Per `pump_schedule.py:1-27` and `translations/en.json:839-844`, it runs in every slot except those that are "provably idle and warm". On a `no_valve` install, a pump-off interval with circulation running therefore drains the buffer into the emitters at room temperature, and the learner's own docstring names this contamination (`coordinator.py:5292-5294`).
- **The rule.** The arm at `g` > 0 moves against its null, so by point 3's rule (a learner whose output moves keeps the freeze) the buffer keeps it.
- **Cost.** Standby-loss samples on a buffer whose rate has a volume-derived prior. This is small.

## Site table (13 call sites plus the DHW callable; `coordinator.py` at 1afdef8)

`grep -n "_learning_frozen" coordinator.py` also hits the `def` at `:6574`, the substring `boost.space_learning_frozen` at `:6651`, and comments at `:1044`, `:6481`, `:6525` and `:9906`. None of them is a call.

| line | function (def line) | keys | decision |
|---|---|---|---|
| 878 | `_fold_flow_lift` (839) | outdoor | `room_air=False` (accepted round 1) |
| 1152 | `_freq_fold_blocked` (1136) | power | `room_air=False` (accepted round 1) |
| 3405 | DHW callable, `frozen=` in the `DhwProfileLearner` wiring (nested def at 3391) | — | `functools.partial(self._learning_frozen, room_air=False)` (accepted round 1) |
| 5017 | `_fold_measured_cop` (4999) | power, outdoor, thermal power | `room_air=not measured_heat` (point 1) |
| 5311 | `_async_learn_buffer_cooling` (5287) | buffer | **default** (reversed, above) |
| 5437 | `_async_learn_house_heat_loss` (5410) | indoor, outdoor, thermal power | default: it is the room-air learner and feeds the detector |
| 5601 | `_async_learn_lower_floor_loss` (5571) | indoor, outdoor, lower floor, thermal power | default: room temperature |
| 8971 | `_track_curve_comfort` (8952) | indoor | default: room temperature |
| 9388 | `_inputs_unhealthy` (9386) | indoor, outdoor, power | default: snapshot health keeps its meaning |
| 9760 | `_record_accuracy` (9737), draw-range `power_frozen` | power | **default** (point 2) |
| 9780 | `_record_accuracy` (9737), `indoor_frozen` for lead-prediction scoring | indoor | default: scores the room against a prediction, so a window is exactly what it must not score |
| 9926 | `_dhw_probe_temperature` (9886) | DHW | `room_air=False` (accepted round 1) |
| 10773 | `_record_quiet_comfort_period` (10766) | indoor | default: room temperature |
| 10858 | `_run_system_identification` (10840) | indoor, outdoor | default: abort (R10-CEILING-PROBE F1's question) |

So `room_air=False` is now passed at four call sites (878, 1152, 9926, and 5017 conditionally) plus the DHW callable. Nine call sites keep the default.

## Unchanged from round 1 (accepted by review)

- **The seam.** One owner, `_learning_frozen` (`coordinator.py:6574`). The signature becomes `_learning_frozen(self, *keys: str, room_air: bool = True) -> str | None`, and `room_air=False` skips only the `ventilation` branch. The default fails closed, and every other branch keeps its order.
- **Invariants.**
  - The house learner's vent pass-through is unchanged.
  - `learner_freeze_reason` still reads `ventilation` while the house learner is latched.
  - Ventilation still ranks below an unusable input and above boost.
- **The alternatives and why each lost.** Caller-side filtering loses boost and the tail reasons below it and spreads the reason string. A `_fabric_frozen()` fails open. Key-scoping changes what keys mean for `_inputs_unhealthy`.

  The new `room_air=not measured_heat` argument is the same keyword carrying a per-interval value. It is not a fourth shape.
- **sysid keeps its abort.** DHW, `_freq_fold_blocked`, `_fold_flow_lift` and `_dhw_probe_temperature` lift as designed (review: "their lift stands").

  This round adds no window arm for these four. The review ruled them unaffected by points 1–3, and none of their inputs is room air: a tank probe, a kW-per-Hz map, and supply against the curve on the outdoor key. If the reviewer reads point 3 as covering them too, that is the open item for round 3.
- **No `VENT_CUSUM_*` tuning.** The L2 bias does not reproduce synthetically, and the next step is the owner's residual series (`debug_collect start`).

## Evidence plan, by file

**Failing test** in `tests/features.py`, beside the existing `_vent_cusum.tripped` cases, all with the latch set:

1. **Counter install** (`heat_energy.meter_of(c).counter` truthy): after `_learn_measured_cop`, `c._measured_cop.refusal == COP_REFUSED_SPAN_OPEN`. Today it reads `COP_REFUSED_FROZEN` (`learners_frozen`). It must assert the code, not only fold or no fold.
2. **Measured flow heat** (`_flow_bias.heat_output_kw` set): `_fold_measured_cop` folds, so `_cop_samples` rises by 1. It does not return `COP_REFUSED_FROZEN`.
3. **Inferred** (no heat reading): `_fold_measured_cop` still returns `COP_REFUSED_FROZEN`.
4. DHW runs, and `_dhw_probe_temperature` returns the probe.
5. Buffer, draw-range (`draw_range.fold` sees `frozen=True`), sysid, house and lower-floor still freeze or abort on `ventilation`.

**Finder's harness:** Appendix A, committed as `dev/audit/harnesses/r10_cop_gate_vent.py`.
- At both ends, the `cop under a window` arm must read 1.000 for flow and span against a null of 1.000, and the inferred rows must still move (the positive control). This is a property of the fold tail, which this group does not edit, so it must not change.
- The learners arm must read, at the head:
  - COP on an inferred install: `refused:learners_frozen`. The harness's COP probe is inferred, so this row is unchanged.
  - DHW: `runs`.
  - buffer: `frozen:ventilation`.
  - sysid: `aborted:ventilation`.
- The fixer extends the learners arm with a counter and a flow-heat COP row, which must read `span_open` and `passes freeze` at the head and `refused:learners_frozen` at the base.

**Null control.**
- Latch clear: every learner passes at both ends.
- `k=0.00` in each window arm.

**Mutation proof targets** (one mutant per gate):
- the `room_air` guard on the vent branch: fails tests 1, 2 and 4;
- `room_air=not measured_heat` → `True`: fails tests 1 and 2;
- `room_air=not measured_heat` → `False`: fails test 3;
- each of `:878`, `:1152`, `:9926` and the `:3405` partial back to default: fails its row;
- `:5311` and `:9760` set to `room_air=False`: fail test 5's rows.

**Goldens:** none expected to move. No solver output depends on the freeze.

**Hot files and serial position:** `coordinator.py`. #2262's COP observability edits `_fold_measured_cop` and must serialize with this item. R10-CEILING-PROBE F1 owns the sysid abort.

## Notes for the fixer

- Carry: R10-COP-GATE (item 8)
- Carry: R10-COP-GATE (item E)
- Carry: R10-CEILING-PROBE (item F1)
- Carry: dismissed: freeze reason resets each cycle (item 9)
- The inferred COP fold has no restoring force. Its target is the current scale times the observed correction, so any persistent draw-over-ask bias walks the scale to a clamp: 0.5 here, within 30 days. That is why the inferred path keeps the freeze. It is also a property of the fold beyond windows, outside this group, and it goes to the COP fold's own brief by `finding-propagation.md`, not to an issue.
- The draw-range `observed()` max moved by up to +10 % under a window without `follows_ask` flipping. Lifting `:9760` later needs a consumer that judges draws against measured heat, which none does today.

Seat tokens: subagent locators 50301 + 20961; main-loop count not reported by the harness.

## Appendix A: harness source (scratchpad `r10_cop_gate_vent.py`, not committed)

```python
#!/usr/bin/env python3
"""R10-COP-GATE item E (carries L1/L2, 8 and 9): the ventilation freeze.

Four arms, all through production symbols at the tree under test:

  cusum    drift.Cusum with the coordinator's constants (VENT_CUSUM_*),
           fed a synthetic 30-min residual series for 30 days x seeds:
             null     zero-mean noise only (the null control: must trip ~0)
             window   noise + an open window every 2nd evening (19:00, 3 h,
                      +k_vent kW/K air exchange at the interval's dT)
             ua_bias  noise + a heat-loss scale error f (true UA = model UA
                      x (1+f)) under a diurnal outdoor swing: the shape a
                      wrong learned scale (L2, 2.09) puts in the residual
           reports trips per 30 days and the share of tripped time.
  learners which learners stop when the vent latch is set: _learning_frozen
           per learner's own keys, plus the learner entry points
           (_fold_measured_cop, DhwProfileLearner.async_learn_dynamics,
           _async_learn_buffer_cooling, _run_system_identification).
           Null control: latch clear. Perturbation (mutant): a
           _learning_frozen that drops the vent branch must un-freeze each.
  latch    carry 9: latch on, a cycle of _update_current_state, then latch
           off and another cycle; the reason must read "ventilation" then None.

    PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py
"""
from __future__ import annotations

import asyncio
import math
import sys
from datetime import datetime, timedelta, timezone

sys.path[:0] = ["tests", "custom_components"]

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

P = ThermalParameters()
UA, C = P.heat_loss_coefficient, P.room_thermal_mass  # kW/K, kWh/K
DT_H = 0.5


def detector() -> Cusum:
    return Cusum(threshold=const.VENT_CUSUM_THRESHOLD_C, drift=const.VENT_CUSUM_DRIFT_C, side=-1,
                 clip=const.VENT_CUSUM_CLIP_C, reference_hours=const.VENT_CUSUM_REFERENCE_HOURS)


def run_cusum(sigma: float, *, window_k: float = 0.0, f: float = 0.0, seed: int = 0,
              days: int = 30, t_mean: float = 2.0, t_swing: float = 5.0, room: float = 21.0,
              front_k: float = 0.0):
    rng = np.random.default_rng(seed)
    d = detector()
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    trips = tripped_n = 0
    n = int(days * 24 / DT_H)
    for i in range(n):
        when = t0 + timedelta(hours=i * DT_H)
        hour = when.hour + when.minute / 60
        outdoor = t_mean - t_swing * math.cos(2 * math.pi * (hour - 15) / 24)  # coldest ~03:00
        # A cold front: front_k K colder for two days in every ten, stepped in.
        if front_k and when.day % 10 in (3, 4):
            outdoor -= front_k
        dT = room - outdoor
        # Price-shaped heat, not dT-shaped: the planner shifts heat to cheap hours.
        heat_kwh = (3.0 if hour < 6 or 13 <= hour < 16 else 0.6) * DT_H
        r = rng.normal(0.0, sigma) - f * UA * dT * DT_H / C
        if window_k and (when.day % 2 == 0) and 19 <= hour < 22:
            r -= window_k * dT * DT_H / C
        if d.update(when, float(r), (heat_kwh, 0.0)) and d.tripped:
            trips += 1
        tripped_n += d.tripped
    return trips, tripped_n / n


def arm_cusum() -> list[str]:
    out = ["## cusum (trips / 30 d over 8 seeds: mean [min-max]; tripped share)"]
    def row(label, **kw):
        res = [run_cusum(seed=s, **kw) for s in range(8)]
        t = [r[0] for r in res]
        share = sum(r[1] for r in res) / len(res)
        out.append(f"{label:44s} trips={np.mean(t):5.2f} [{min(t)}-{max(t)}] tripped={share:6.1%}")
    for sigma in (0.05, 0.10, 0.15, 0.20):
        row(f"null sigma={sigma}", sigma=sigma)
    for sigma in (0.05, 0.10, 0.15):
        for k in (0.15, 0.30):
            row(f"window k={k}kW/K sigma={sigma} (15 events)", sigma=sigma, window_k=k)
    for sigma in (0.05, 0.10):
        for f in (0.5, 1.09, 2.0, -0.52):
            row(f"ua_bias f={f:+.2f} sigma={sigma}", sigma=sigma, f=f)
        row(f"ua_bias f=+1.09 swing=10 sigma={sigma}", sigma=sigma, f=1.09, t_swing=10.0)
        row(f"front 8K, f=0 (null for front) sigma={sigma}", sigma=sigma, front_k=8.0)
        for f in (0.5, 1.09):
            row(f"front 8K + ua_bias f=+{f:.2f} sigma={sigma}", sigma=sigma, f=f, front_k=8.0)
    return out


CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
    "dhw_temp_entity": "sensor.dhw", "buffer_tank_temp_entity": "sensor.buffer",
    "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
}
STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("2.0", unit="°C"),
    "sensor.pump_power": FakeState("2200", unit="W"), "sensor.dhw": FakeState("50.0", unit="°C"),
    "sensor.buffer": FakeState("40.0", unit="°C"),
}


def coordinator():
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    return HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=dict(CFG)))


async def learner_outcomes(tripped: bool, mutant: bool) -> dict[str, str]:
    c = coordinator()
    c._vent_cusum.tripped = tripped
    if mutant:
        real = c._learning_frozen
        c._learning_frozen = lambda *k: (None if (r := real(*k)) == "ventilation" else r)
        c._dhw_learner._frozen = c._learning_frozen
    out = {}
    # COP: the guard's refusal code; anything past the freeze gate is "passes freeze".
    c._measured_power, c._current_action = 2.2, {"power": 2.1, "dhw_power": 0.0}
    code = c._fold_measured_cop(None)
    out["cop(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
    # DHW: returns the freeze reason, or None when it ran.
    t0 = datetime.now(timezone.utc)
    await c._dhw_learner.async_learn_dynamics(50.0)
    c._dhw_learner.last_sample_time = t0 - timedelta(minutes=30)
    r = await c._dhw_learner.async_learn_dynamics(49.8)
    out["dhw(async_learn_dynamics)"] = f"frozen:{r}" if r else "runs"
    # Buffer: sets _learner_freeze_reason on a freeze.
    c._learner_freeze_reason = None
    await c._async_learn_buffer_cooling(40.0)
    out["buffer(_async_learn_buffer_cooling)"] = f"frozen:{c._learner_freeze_reason}" if c._learner_freeze_reason else "runs"
    # sysid: aborts an active experiment with the freeze reason.
    from heatpump_optimizer import sysid as _s
    c._sysid.phase = next(v for k, v in vars(_s).items() if k.startswith("PHASE_") and v not in (_s.PHASE_ABORTED,) and k not in ("PHASE_IDLE", "PHASE_DONE", "PHASE_COMPLETE"))
    try:
        active = c._sysid.active
    except Exception:  # noqa: BLE001
        active = None
    try:
        await c._run_system_identification(np.full(48, 1.0))
    except Exception as e:  # noqa: BLE001 - past the gate the experiment needs more state
        out["sysid(_run_system_identification)"] = f"passes freeze (raised {type(e).__name__})"
    else:
        res = c._sysid.result
        out["sysid(_run_system_identification)"] = (
            f"aborted:{res.reason}" if res is not None and res.reason == "ventilation"
            else f"passes freeze (later outcome {getattr(res, 'reason', None)!r}, active-before={active})")
    # The house learner's own keys, for the record.
    out["house(_learning_frozen keys)"] = str(c._learning_frozen("indoor_temp_entity", "outdoor_temp_entity"))
    return out


def const_cop_frozen():
    from heatpump_optimizer import coordinator as co
    return co.COP_REFUSED_FROZEN


async def arm_learners() -> list[str]:
    out = ["## learners on the vent latch (latch | null: latch clear | mutant: vent branch dropped)"]
    a, b, m = (await learner_outcomes(True, False), await learner_outcomes(False, False),
               await learner_outcomes(True, True))
    for k in a:
        out.append(f"{k:40s} {a[k]:34s} | {b[k]:30s} | {m[k]}")
    return out


async def arm_latch() -> list[str]:
    c = coordinator()
    seq = []
    for tripped in (True, True, False, False):
        c._vent_cusum.tripped = tripped
        await c._update_current_state()
        seq.append(f"latch={tripped}: learner_freeze_reason={c._learner_freeze_reason}")
    return ["## latch on-then-off (carry 9), consecutive _update_current_state cycles"] + seq


# --- round 2: the window through each lifted learner's production fold ---
from heatpump_optimizer import draw_range as _dr  # noqa: E402

OUT_C, ROOM_C = -10.0, 21.0          # outside the frost band (0..4 C), so no defrost gate
DESIGN_DT = 31.0                     # steady room-outdoor dT at OUT_C


def window_excess(k_vent: float, days: int = 30) -> list[float]:
    """Per 30-min interval, the fractional rise of the emitters' heat at a FIXED
    flow temperature: a first-order room (default UA, C) whose emitter UA is
    backed out of the steady load at ``emitter_design_delta_t``; an open window
    adds ``k_vent`` kW/K from 19:00 for 3 h every second day and the room then
    recovers on the same emitters. 0.0 everywhere for k_vent=0 (the null)."""
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    t_flow = ROOM_C + q0 / u_em
    room, out = ROOM_C, []
    n = int(days * 24 / DT_H)
    for i in range(n):
        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
        for _ in range(30):                      # 1-min Euler steps
            q_em = u_em * (t_flow - room)
            room += (q_em - (UA + k) * (room - OUT_C)) * (1 / 60) / C
        out.append(u_em * (ROOM_C - room) / q0)  # delta = extra heat / nominal heat
    return out


def cop_coordinator():
    c = coordinator()
    st = getattr(c, "_ctx", c)._current_state
    st.outdoor_temperature = OUT_C
    cop = c._thermal_model.compute_cop(OUT_C)
    ask = UA * DESIGN_DT / cop
    c._current_action = {"power": ask, "dhw_power": 0.0}
    return c, ask, cop


def follows_draw(ask: float) -> "_dr.DrawRange":
    """A draw window whose evidence says the draw follows the ask."""
    d = _dr.DrawRange()
    rng = np.random.default_rng(7)
    for _ in range(_dr.MIN_SAMPLES + 12):
        a = ask * rng.choice((0.6, 1.0, 1.4))
        d.observe(a * (1 + rng.normal(0, 0.02)), a, P.min_electrical_power, P.max_electrical_power)
    return d


def run_cop(path: str, k_vent: float, seed: int, evidence: str) -> tuple[float, int, int]:
    """Feed 30 d of intervals through the production COP fold, latch clear.

    path: inferred   _fold_measured_cop, no heat reading (cop_evidence's inference)
          flow       _fold_measured_cop with a measured flow heat (_flow_bias.heat_output_kw)
          span       _fold_cop_evidence on counter deltas, as _async_learn_heat_span calls it
    The pump's true COP never changes: at a fixed flow the emitters take (1+d)
    times the heat and the compressor draws (1+d) times the power. Returns
    (final cop_scale, folds, folds inside a window-perturbed interval)."""
    c, ask, cop = cop_coordinator()
    rng = np.random.default_rng(seed)
    draw = follows_draw(ask) if evidence == "follows" else None
    folds = wfolds = 0
    for d in window_excess(k_vent):
        noise = rng.normal(0, 0.03)
        elec = ask * (1 + d) * (1 + noise)
        heat = cop * elec   # the true COP is the model's curve at scale 1, window or not
        c._measured_power = elec
        before = c._cop_samples
        if path == "span":
            c._flow_bias.heat_output_kw = None
            c._fold_cop_evidence(ask, elec, heat, c._cop_reference_curve((heat, None)))
        else:
            c._flow_bias.heat_output_kw = heat if path == "flow" else None
            c._fold_measured_cop(draw)
        if c._cop_samples != before:
            folds += 1
            wfolds += d > 0.005
    return c._cop_scale, folds, wfolds


def arm_cop_window() -> list[str]:
    out = ["## cop under a window, latch clear (cop_scale after 30 d; truth 1.000; 8 seeds mean [min-max]; folds; folds on an interval the window raised by >0.5 %)"]
    for path, ev in (("inferred", "none"), ("inferred", "follows"), ("flow", "none"), ("span", "none")):
        for k in (0.0, 0.15, 0.30):
            res = [run_cop(path, k, s, ev) for s in range(8)]
            sc = [r[0] for r in res]
            out.append(f"{path:8s} draw-evidence={ev:7s} k={k:.2f} scale={np.mean(sc):.3f} [{min(sc):.3f}-{max(sc):.3f}] "
                       f"folds={res[0][1]} window-folds={res[0][2]}")
    ex = window_excess(0.30)
    for k in (0.15, 0.30):
        ex = window_excess(k)
        out.append(f"(window k={k:.2f}: excess peak {max(ex):+.1%}, 30-d mean {np.mean(ex):+.2%}, intervals over COP_ASK_TOLERANCE {sum(e > 0.15 for e in ex)})")
    out.append(f"(window excess at k=0.30: peak {max(ex):+.1%}, mean over perturbed intervals {np.mean([e for e in ex if e > 0.005]):+.1%};"
               f" k=0.15 peak {max(window_excess(0.15)):+.1%})")
    return out


def run_draw(k_vent: float, seed: int):
    """draw_range.fold, frozen=False, on a price-shaped ask; the drawn kW is the
    ask times the window excess. Returns follows_ask, the log-log slope, engaged
    and planned() after 30 d."""
    d = _dr.DrawRange()
    rng = np.random.default_rng(seed)
    for i, e in enumerate(window_excess(k_vent)):
        hour = (i * DT_H) % 24
        ask = 2.4 if hour < 6 or 13 <= hour < 16 else (1.6 if 16 <= hour < 23 else 1.2)
        drawn = ask * (1 + e) * (1 + rng.normal(0, 0.03))
        _dr.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False, command=None)
    pairs = np.array([(dd, a) for dd, a, _ in d._evidence()], dtype=float)
    la, ld = np.log(pairs[:, 1]), np.log(pairs[:, 0])
    la = la - la.mean()
    slope = float(np.dot(la, ld - ld.mean()) / np.dot(la, la))
    return _dr.follows_ask(d), slope, d.engaged, d.planned(P.min_electrical_power, P.max_electrical_power), d.observed()


def arm_draw_window() -> list[str]:
    out = ["## draw_range.fold under a window, frozen=False (8 seeds: slope mean [min-max]; follows; engaged; planned)"]
    for k in (0.0, 0.15, 0.30):
        res = [run_draw(k, s) for s in range(8)]
        sl = [r[1] for r in res]
        out.append(f"k={k:.2f} slope={np.mean(sl):.3f} [{min(sl):.3f}-{max(sl):.3f}] follows={sorted({str(r[0]) for r in res})} "
                   f"engaged={sorted({r[2] for r in res})} planned={sorted({str(r[3]) for r in res})} observed0={res[0][4]}")
    return out


async def run_buffer(g: float, k_vent: float) -> tuple[float, int]:
    """_async_learn_buffer_cooling on pump-off 30-min intervals, latch clear.
    The tank loses to its room (standby UA_s) and, with the circulation pump
    running, ``g`` kW/K into the emitters at the ROOM's temperature, which the
    window lowers. g=0 is the modelled no-valve topology (draw == pump heat)."""
    c = coordinator()
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    cbuf = P.buffer_tank_volume * 1.163 / 1000.0          # kWh/K
    ua_s = 0.04 * cbuf                                     # ~1 C/h at the 25 K reference
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    ex = window_excess(k_vent)
    for i, e in enumerate(ex):
        room = ROOM_C - e * q0 / u_em
        tb0 = 45.0
        k = (ua_s + g) / cbuf                               # per hour
        t_inf = (ua_s * 20.0 + g * room) / (ua_s + g)
        tb1 = t_inf + (tb0 - t_inf) * math.exp(-k * DT_H)
        c._last_buffer_temp_sample = tb0
        c._last_buffer_sample_time = datetime.now(timezone.utc) - timedelta(hours=DT_H)
        c._buffer_heating_since_sample = False
        await c._async_learn_buffer_cooling(tb1)
    return c._buffer_cooling_rate, c._buffer_cooling_samples


async def arm_buffer_window() -> list[str]:
    out = ["## buffer cooling under a window, latch clear (learned C/h after 30 d; samples)"]
    for g in (0.0, 0.0005, 0.002):
        for k in (0.0, 0.30):
            r, n = await run_buffer(g, k)
            out.append(f"g={g:.4f}kW/K k={k:.2f} rate={r:.4f} samples={n}")
    return out


async def main() -> None:
    lines = (arm_cusum() + await arm_learners() + await arm_latch()
             + arm_cop_window() + arm_draw_window() + await arm_buffer_window())
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
```
