# Design note, round 3: r10-cop-gate-vent (R10-COP-GATE item E, carries 8 and 9)

Tree measured: origin/main e77418f9b48f89421bd72b0ab511c057341c7fa4. `custom_components/` has no diff from 1afdef88 (round 2's measured SHA), so every line number carries; each one cited new here was re-read at e77418f9. Round 2: handoff-body/r10-cop-gate-vent at 6eb360d0. Review: `Design review: revise` at handoff-body/r10-cop-gate-vent-drev c8fba463.

## Deviation (unchanged)

The payload gives this seat the probe role: read-only, with no code pushed to any ref. **Nothing was pushed to `design/R10-COP-GATE-vent`, so there is no design SHA.** The harness source is in Appendix A, ready to commit as `dev/audit/harnesses/r10_cop_gate_vent.py`. Whoever commits it owes the `tests/closure.py` classification.

The payload names the return ref `handoff-body/r10-cop-gate-vent-r3`, and the brief names `handoff-body/r10-cop-gate-vent`. This body is pushed to both, as in round 2.

## The revise point: `_fold_flow_lift` (`coordinator.py:878`) keeps the default freeze

Round 2 lifted `:878` on argument alone. This round runs the arm the reviewer specified, and by the note's own rule the arm reverses the lift.

### Arm: `_fold_flow_lift under a window` (Appendix A, `arm_flow_window`)

- **Driver.** The production `coordinator._fold_flow_lift` runs once per 30-min interval for 30 days (1440 cycles, at the default `optimization_interval` of 30 min). It goes through every gate: a fresh supply set by `FlowCurveBias.observe_temps`, the power floor, `_learning_frozen` with the latch clear, `_cop_fold_blocked`, and the space-dominant split. The curve is the production `curve_supply_temp`, which gives 22.42 °C at -10 °C and a target of 21.0. Every cycle folds (1440/1440).
- **Scenario.** This is round 2's window scenario: default `ThermalParameters` (UA 0.15 kW/K, C 10 kWh/K), -10 °C outdoors, and a window of +k kW/K from 19:00 for 3 h every second day. Supply noise is ±0.3 K, over 8 seeds.
- **Law (a), the reviewer's.** The emitters deliver the commanded hold heat q0 = UA·31 K whatever the room does. Supply = room + q0/UA_em + ΔT_design/2.
  - UA_em is the model's own: nameplate × COP_nominal / `emitter_design_delta_t`, the same UA the curve is built on.
  - ΔT_design is a 5 K flow-return spread. It is a constant offset, so it enters the null and the window arms equally, and every reading below is taken against its own null.
- **Law (b), the null by construction.** The curve is held: supply = curve + ΔT_design/2, independent of the room.
- **Law (a2), a sensitivity, not the rule.** The plan replans each interval, asking q0 + C·(target − room)/6 h (capped at the nameplate heat). A room the window has cooled is reheated, and the extra heat raises supply, which pushes the other way.
- **Positive check of today's gate.** The same driver with the latch set folds 0 times (law a, k = 0.30).

### Measured (Appendix A at e77418f9; `PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py`, venv-ci, 36 s)

```
## _fold_flow_lift under a window, latch clear (bias_k K after 30 d; 8 seeds: final mean [min-max] | 30-d mean [min-max] | run min..max; folds)
law=a  k=0.00 final=+2.518 [+2.364..+2.626] mean=+2.496 [+2.483..+2.511] run=+2.181..+3.112 folds=1440
law=a  k=0.15 final=+0.710 [+0.556..+0.817] mean=+0.835 [+0.821..+0.849] run=+0.111..+3.112 folds=1440
law=a  k=0.30 final=-0.889 [-1.043..-0.782] mean=-0.651 [-0.665..-0.637] run=-1.814..+3.112 folds=1440
law=b  k=0.00 final=+2.518 [+2.364..+2.626] mean=+2.496 [+2.483..+2.511] run=+2.181..+3.112 folds=1440
law=b  k=0.15 final=+2.518 [+2.364..+2.626] mean=+2.496 [+2.483..+2.511] run=+2.181..+3.112 folds=1440
law=b  k=0.30 final=+2.518 [+2.364..+2.626] mean=+2.496 [+2.483..+2.511] run=+2.181..+3.112 folds=1440
law=a2 k=0.00 final=+2.518 [+2.364..+2.626] mean=+2.496 [+2.483..+2.511] run=+2.181..+3.112 folds=1440
law=a2 k=0.15 final=+2.503 [+2.349..+2.611] mean=+2.420 [+2.406..+2.434] run=+2.020..+3.112 folds=1440
law=a2 k=0.30 final=+2.489 [+2.335..+2.597] mean=+2.346 [+2.332..+2.361] run=+1.762..+3.112 folds=1440
(law a k=0.15: room min 18.50 C, 30-d mean 19.33 C, last 19.31 C)
(law a k=0.30: room min 16.30 C, 30-d mean 17.83 C, last 17.82 C)
(law a2 k=0.15: room min 19.91 C, 30-d mean 20.84 C, last 20.99 C)
(law a2 k=0.30: room min 18.87 C, 30-d mean 20.69 C, last 20.98 C)
(curve at -10.0 C, target 21.0: 22.42 C; latch set, law a k=0.30: folds=0)
(priced at -10.0 C; cop_flow_reference_temp=35.0 C)
(plant 25 C, bias +2.58 K, factor 1.0000: a/0.15 shift -1.662 K factor +0.00%; a/0.30 shift -3.148 K factor +0.00%; a2/0.15 shift -0.077 K factor +0.00%; a2/0.30 shift -0.151 K factor +0.00%; b/0.30 shift +0.000 K factor +0.00%)
(plant 40 C, bias +17.58 K, factor 0.9146: a/0.15 shift -1.662 K factor +2.89%; a/0.30 shift -3.148 K factor +5.65%; a2/0.15 shift -0.077 K factor +0.13%; a2/0.30 shift -0.151 K factor +0.25%; b/0.30 shift +0.000 K factor +0.00%)
(plant 50 C, bias +27.58 K, factor 0.7865: a/0.15 shift -1.662 K factor +2.32%; a/0.30 shift -3.148 K factor +4.51%; a2/0.15 shift -0.077 K factor +0.10%; a2/0.30 shift -0.151 K factor +0.20%; b/0.30 shift +0.000 K factor +0.00%)
```

### Readings

1. **Law (a) moves `bias_k` well beyond its no-window null.**

   | k (kW/K) | 30-day mean `bias_k`, 8 seeds | final value |
   |---|---|---|
   | 0.00 (null) | +2.496 [+2.483..+2.511] | — |
   | 0.15 | +0.835 [+0.821..+0.849], a shift of −1.66 K | +0.710 |
   | 0.30 | −0.651 [−0.665..−0.637], a shift of −3.15 K | −0.889 |

   The seed ranges are disjoint from the null by more than 1.6 K. The run minimum reaches −1.81 K against a null minimum of +2.18.
2. **Part of law (a)'s shift is the room's lasting drop, not only the window events.** With the heat held at q0 and nothing restoring the room, the room's 30-day mean is 19.33 °C at k = 0.15 and 17.83 °C at k = 0.30. This is the reviewer's law, stated as the strong case.
3. **Law (a2) also moves beyond its null, even with the room recovering** (room 30-day mean 20.84 and 20.69 °C).
   - 30-day mean +2.420 [+2.406..+2.434] at k = 0.15 and +2.346 [+2.332..+2.361] at k = 0.30, against +2.496 [+2.483..+2.511].
   - Its shifts are −0.08 and −0.15 K. They are small, but outside the null's seed range.
4. **Law (b) is identical to the null to the last digit at both k.** Its flatness is a property of the model, not evidence. This is the reviewer's point about round 2's window model, now measured.
5. **The price.** `bias_k` reaches the plan as `flow_curve_bias` (`coordinator.py:3931`), which is added to `curve_flow_temp` (`thermal_model.py:2641`). `flow_lift_factor` reads curve + bias only above `cop_flow_reference_temp` (35.0 °C).
   - In this house the 22–25 °C supply is below the reference, so the shift costs nothing (factor +0.00 % at every k).
   - On a plant whose supply sits at 40 °C (bias +17.58 K), the same additive shifts move the priced COP factor:
     - law (a): +2.89 % at k = 0.15 and +5.65 % at k = 0.30;
     - law (a2): +0.13 % and +0.25 %.
   - At 50 °C: law (a) +2.32 % and +4.51 %; law (a2) +0.10 % and +0.20 %.
   - Under a window the learner reads a cooler supply as a curve set lower, and the plan then prices every step at a COP that is too high.
   - These rows apply the 25 °C scenario's shift to hotter plants. That is exact under law (a), because supply = room + Q/UA_em + const moves by the room's move at any offset.

### Decision

The rule (round 2, point 3) is that a learner whose output moves under a window keeps the freeze. Law (a) moves `bias_k` beyond its no-window null, and so does law (a2). **`coordinator.py:878` keeps the default `room_air=True`.** No edit at `:878`.

- **Cost.** No flow-bias sample is taken while the latch is set. The bias is an installation property on a 0.1 EWMA with no time pressure, and the latch is the same one the house learner sits behind.
- **Inherited risk.** Round 2's argument ("supply against the curve, on the outdoor key") was wrong where the reviewer said it was. The outdoor key names the curve's input, but the supply side reads the room through the emitter.

## The reviewer's carried notes, settled

1. **`coordinator.py:1152` (`_freq_fold_blocked`) already lifts.** Re-read at e77418f9: `frozen = coord._learning_frozen(CONF_POWER_ENTITY)` then `return bool(frozen and ":" in frozen)` (`:1152-1153`), and the vent branch returns `"ventilation"` with no colon (`coordinator.py:6641-6642`).
   - **The `room_air=False` edit at `:1152` is dropped, and so is its mutant**, an equivalent mutant no test can kill.
   - The PR body records that the site already lifts through its own colon predicate. Boost and the tail reasons pass there too.
2. **The flow-heat COP lift must fail closed on a stale thermal-power reading.** This is added as failing test 2b (below): a stale thermal-power entity with the latch set must give `COP_REFUSED_FROZEN`.
   - `observe_temps` stores whatever `read_heat_output_kw` returns each cycle (`flow_lift.py:154-178`). The test, not this note, establishes that a stale entity yields `None`.
   - If it does not, the fixer gates `measured_heat` on the reading being fresh, rather than on `is not None`, and says so in the PR body.
3. Carry: dismissed: freeze reason resets each cycle (item 9). The latch arm (Appendix A) reads `ventilation` → `None` across consecutive cycles, unchanged.

## Unchanged (accepted by review in rounds 1–2; nothing here edits them)

- **Point 1: COP splits on heat evidence.** The counter span and measured flow heat are lifted, and the inferred path is kept frozen. The shape is `room_air=not measured_heat` with the hoisted `heat_kw` (`coordinator.py:5017`, `:5048`).
  - Evidence: the `cop under a window` arm. At e77418f9 it is byte-identical to round 2's measured block (diffed): inferred 0.500 against a null of 1.056 [0.989-1.120], flow and span 1.000.
- **Point 2: draw-range `power_frozen` (`coordinator.py:9760`) stays frozen.** The arm is byte-identical.
- **The buffer stays frozen, settled from the topology.** The arm is byte-identical.
- **The DHW callable (`:3405`) and `_dhw_probe_temperature` (`:9926`) lift** (review: "their lift stands on inspection").
- **The seam.** `_learning_frozen(self, *keys: str, room_air: bool = True) -> str | None`, where `room_air=False` skips only the `ventilation` branch.
  - The default fails closed. The house learner's pass-through, `learner_freeze_reason` and the ranking are unchanged.
  - The alternatives lost as in round 1.
- **sysid keeps its abort.** There is no `VENT_CUSUM_*` tuning.
- The cusum, learners and latch arms are reproduced unchanged at e77418f9.

## Site table (13 call sites plus the DHW callable; `coordinator.py` at e77418f9, line numbers equal to 1afdef8)

| line | function (def line) | keys | decision |
|---|---|---|---|
| 878 | `_fold_flow_lift` (839) | outdoor | **default** (reversed this round: arm above) |
| 1152 | `_freq_fold_blocked` (1136) | power | **no edit**: already lifts through `":" in frozen` (carried note 1) |
| 3405 | DHW callable, `frozen=` in the `DhwProfileLearner` wiring (nested def at 3391) | — | `functools.partial(self._learning_frozen, room_air=False)` |
| 5017 | `_fold_measured_cop` (4999) | power, outdoor, thermal power | `room_air=not measured_heat` (point 1) |
| 5311 | `_async_learn_buffer_cooling` (5287) | buffer | default |
| 5437 | `_async_learn_house_heat_loss` (5410) | indoor, outdoor, thermal power | default |
| 5601 | `_async_learn_lower_floor_loss` (5571) | indoor, outdoor, lower floor, thermal power | default |
| 8971 | `_track_curve_comfort` (8952) | indoor | default |
| 9388 | `_inputs_unhealthy` (9386) | indoor, outdoor, power | default |
| 9760 | `_record_accuracy` (9737), draw-range `power_frozen` | power | default (point 2) |
| 9780 | `_record_accuracy` (9737), `indoor_frozen` | indoor | default |
| 9926 | `_dhw_probe_temperature` (9886) | DHW | `room_air=False` |
| 10773 | `_record_quiet_comfort_period` (10766) | indoor | default |
| 10858 | `_run_system_identification` (10840) | indoor, outdoor | default: abort |

After this round:
- `room_air=False` is passed at one call site (`:9926`), plus the DHW callable.
- `room_air=not measured_heat` is passed at one site (`:5017`).
- `:1152` is not edited.
- The other ten call sites keep the default.

## Evidence plan, by file

**Failing test** in `tests/features.py`, beside the existing `_vent_cusum.tripped` cases, all with the latch set:

1. **Counter install** (`heat_energy.meter_of(c).counter` truthy): after `_learn_measured_cop`, `c._measured_cop.refusal == COP_REFUSED_SPAN_OPEN`. Today it reads `COP_REFUSED_FROZEN`. The test asserts the code, not only whether a fold happened.
2. **Measured flow heat** (`_flow_bias.heat_output_kw` set): `_fold_measured_cop` folds (`_cop_samples` + 1).
   - 2b: a configured thermal-power entity whose state is stale, run through the cycle's real `observe_temps` read, gives `COP_REFUSED_FROZEN` (carried note 2).
3. **Inferred** (no heat reading): `_fold_measured_cop` still returns `COP_REFUSED_FROZEN`.
4. DHW runs, and `_dhw_probe_temperature` returns the probe.
5. Buffer, draw-range (`draw_range.fold` sees `frozen=True`), sysid, house and lower floor still freeze or abort on `ventilation`. **New this round:** `_fold_flow_lift` with a fresh supply above the power floor leaves `_flow_bias.samples` unchanged. This one passes at the base and must keep passing; it pins the reversal.

**Finder's harness:** Appendix A, committed as `dev/audit/harnesses/r10_cop_gate_vent.py`.
- **At both ends:**
  - `cop under a window`: flow and span read 1.000, and inferred still moves.
  - `_fold_flow_lift under a window`: law (a) moves against its null, law (b) equals it, and the latch-set row folds 0.
  - These are properties of folds this group does not edit, so neither may change.
- **The learners arm at the head:**
  - inferred COP `refused:learners_frozen`;
  - DHW `runs`;
  - buffer `frozen:ventilation`;
  - sysid `aborted:ventilation`.
- **The fixer adds rows** for counter COP and flow-heat COP: `span_open` and `passes freeze` at the head, `refused:learners_frozen` at the base.

**Null control.** Latch clear, and `k=0.00` in each window arm. Law (b) is the flow arm's by-construction null.

**Mutation proof targets** (one mutant per gate):
- the `room_air` guard on the vent branch: fails tests 1, 2 and 4;
- `room_air=not measured_heat` → `True`: fails tests 1 and 2;
- `room_air=not measured_heat` → `False`: fails tests 3 and 2b;
- `:9926` and the `:3405` partial back to default: fail test 4's rows;
- `:878`, `:5311` and `:9760` set to `room_air=False`: fail test 5's rows.
- Dropped: `:1152` (equivalent mutant, carried note 1) and `:878` back to default (it is the default).

**Goldens:** none expected to move.

**Hot files and serial position:** `coordinator.py`. #2262's COP observability edits `_fold_measured_cop` and serializes with this item. R10-CEILING-PROBE F1 owns the sysid abort.

## Notes for the fixer

- Carry: R10-COP-GATE (item 8)
- Carry: R10-COP-GATE (item E)
- Carry: R10-CEILING-PROBE (item F1)
- Carry: dismissed: freeze reason resets each cycle (item 9)
- The inferred COP fold has no restoring force (round 2). It goes to the COP fold's own brief by `finding-propagation.md`.
- Lifting `:9760` later needs a consumer that judges draws against measured heat. None exists today.
- **New.** `_fold_flow_lift` reads room air through the emitter whenever the plant runs a commanded power. Any later proposal to lift `:878` needs a window arm with the plant law the install actually runs. Round 2's fixed-flow model reads flat by construction.

Seat tokens: subagent locator 35175; main-loop count not reported by the harness.

## Appendix A: harness source (scratchpad `r10_cop_gate_vent.py`, not committed; rounds 1–2 arms unchanged, round 3 adds `room_series`, `run_flow`, `arm_flow_window`)

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


# --- round 3: the window through _fold_flow_lift (coordinator.py:878) ---
SPREAD_K = 5.0      # flow-return design spread; supply = mean water + spread/2


def room_series(k_vent: float, law: str, days: int = 30) -> list[tuple[float, float]]:
    """Per 30-min interval, (room degC, emitter heat kW) under a plant law.

    a   commanded heat: the emitters deliver the nominal hold heat q0 whatever
        the room does (the reviewer's law); a window cools the room and the
        room recovers only on the house's own constant.
    a2  sensitivity, not the rule: the plan replans each interval, asking q0
        plus C*(target-room)/6 h, capped at the nameplate heat.
    b   the curve held (round 2's model): the flow temperature is fixed, so
        supply is room-independent by construction (the null by construction).
    Same window as round 2: +k_vent kW/K from 19:00 for 3 h every second day."""
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    t_flow = ROOM_C + q0 / u_em
    qmax = P.max_electrical_power * P.cop_nominal_floored
    room, out = ROOM_C, []
    for i in range(int(days * 24 / DT_H)):
        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
        if law == "a":
            q = q0
        elif law == "a2":
            q = min(q0 + C * max(ROOM_C - room, 0.0) / 6.0, qmax)
        for _ in range(30):
            if law == "b":
                q = u_em * (t_flow - room)
            room += (q - (UA + k) * (room - OUT_C)) * (1 / 60) / C
        out.append((room, q))
    return out


def flow_coordinator():
    c = coordinator()
    ctx = getattr(c, "_ctx", c)
    ctx._current_state.outdoor_temperature = OUT_C
    return c, ctx


def run_flow(law: str, k_vent: float, seed: int, *, latch: bool = False) -> tuple[float, float, float, float, int, float]:
    """30 d of cycles through the production _fold_flow_lift, latch clear.

    Supply under law a/a2: room + Q/UA_em + SPREAD_K/2, with UA_em the model's
    own (nameplate x COP_nominal / emitter_design_delta_t, the curve's), so the
    no-window supply sits SPREAD_K/2 above the curve. Under law b: the curve
    plus SPREAD_K/2. +-0.3 K sensor noise per sample. Returns (final bias_k,
    30-d mean, min, max, folds, curve)."""
    c, ctx = flow_coordinator()
    c._vent_cusum.tripped = latch
    p = c._thermal_model.params
    ua_em = p.max_electrical_power * p.cop_nominal_floored / p.emitter_design_delta_t_floored
    from heatpump_optimizer.flow_lift import curve_supply_temp
    from heatpump_optimizer.coordinator import _fold_flow_lift
    curve = curve_supply_temp(c._thermal_model, OUT_C, c.target_temperature)
    cop = c._thermal_model.compute_cop(OUT_C)
    rng = np.random.default_rng(seed)
    hist, folds = [], 0
    now = datetime.now(timezone.utc)
    for room, q in room_series(k_vent, law):
        supply = (curve if law == "b" else room + q / ua_em) + SPREAD_K / 2 + rng.normal(0, 0.3)
        c._current_action = {"power": q / cop, "dhw_power": 0.0}
        c._flow_bias.observe_temps(supply, None, None)
        before = c._flow_bias.samples
        _fold_flow_lift(c, now)
        folds += c._flow_bias.samples != before
        hist.append(c._flow_bias.bias_k)
    return hist[-1], float(np.mean(hist)), min(hist), max(hist), folds, curve


def arm_flow_window() -> list[str]:
    out = ["## _fold_flow_lift under a window, latch clear (bias_k K after 30 d; 8 seeds: final mean [min-max] | 30-d mean [min-max] | run min..max; folds)"]
    means = {}
    for law in ("a", "b", "a2"):
        for k in (0.0, 0.15, 0.30):
            res = [run_flow(law, k, s) for s in range(8)]
            fi, mn = [r[0] for r in res], [r[1] for r in res]
            means[law, k] = float(np.mean(mn))
            out.append(f"law={law:2s} k={k:.2f} final={np.mean(fi):+.3f} [{min(fi):+.3f}..{max(fi):+.3f}] "
                       f"mean={np.mean(mn):+.3f} [{min(mn):+.3f}..{max(mn):+.3f}] "
                       f"run={min(r[2] for r in res):+.3f}..{max(r[3] for r in res):+.3f} folds={res[0][4]}")
    for law in ("a", "a2"):
        for k in (0.15, 0.30):
            rs = room_series(k, law)
            out.append(f"(law {law} k={k:.2f}: room min {min(r for r, _ in rs):.2f} C, 30-d mean {np.mean([r for r, _ in rs]):.2f} C, last {rs[-1][0]:.2f} C)")
    c, _ = flow_coordinator()
    out.append(f"(curve at {OUT_C} C, target {c.target_temperature}: {run_flow('b', 0.0, 0)[5]:.2f} C; "
               f"latch set, law a k=0.30: folds={run_flow('a', 0.30, 0, latch=True)[4]})")
    # What a shift costs where it is priced: flow_lift_factor reads curve +
    # bias only above cop_flow_reference_temp, so price each arm's 30-d mean
    # shift (window minus its own no-window null) on plants at 25/40/50 C.
    m = c._thermal_model
    curve = m.curve_flow_temp(OUT_C)
    out.append(f"(priced at {OUT_C} C; cop_flow_reference_temp={m.params.cop_flow_reference_temp} C)")
    for plant in (25.0, 40.0, 50.0):
        b0 = plant - curve
        m.params.flow_curve_bias = b0
        f0 = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
        row = []
        for law, k in (("a", 0.15), ("a", 0.30), ("a2", 0.15), ("a2", 0.30), ("b", 0.30)):
            d = means[law, k] - means[law, 0.0]
            m.params.flow_curve_bias = b0 + d
            f = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
            row.append(f"{law}/{k:.2f} shift {d:+.3f} K factor {f / f0 - 1:+.2%}")
        out.append(f"(plant {plant:.0f} C, bias {b0:+.2f} K, factor {f0:.4f}: " + "; ".join(row) + ")")
    m.params.flow_curve_bias = 0.0
    return out


async def main() -> None:
    lines = (arm_cusum() + await arm_learners() + await arm_latch()
             + arm_cop_window() + arm_draw_window() + await arm_buffer_window()
             + arm_flow_window())
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
```
