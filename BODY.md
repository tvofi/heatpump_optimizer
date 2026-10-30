# Probe result: r10-cop-gate-vent (R10-COP-GATE item E, carries 8 and 9)

Tree measured: origin/main 507a9ec264eb373b132248d752259254d8a9fa4d (no predecessor handoff head; code read at the same SHA).

## Deviation from the brief (read first)

The payload gives this seat the probe role: read-only, "change no tracked file and send no code to any ref", and "never write to any branch except your return refs". The brief inside it also asks for a harness under `dev/audit/harnesses/` and a push of `design/R10-COP-GATE-vent`. The two conflict, so I followed the stricter role. **Nothing was pushed to `design/R10-COP-GATE-vent` and there is no design SHA to report.** The harness source is in Appendix A and the design note is below, both ready for a designer seat (or the orchestrator) to commit at `design/R10-COP-GATE-vent` as `dev/audit/harnesses/r10_cop_gate_vent.py` plus the architect note. The harness has not been run under `tests/run.sh` or classified for `tests/closure.py`: whoever commits it owes that.

## Measured (harness: Appendix A; `PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py`)

Model: production `drift.Cusum` with the coordinator's constants (threshold 1.2, drift 0.08, clip 0.6, side -1, 24 h reference on heat and sun). The residual is synthetic: 30-min intervals over 30 days and 8 seeds, a first-order room using the default `ThermalParameters` (UA 0.15 kW/K, C 10 kWh/K), 21 °C indoors, an outdoor mean of 2 °C with a ±5 K diurnal swing, and price-shaped heat. The owner's residual series is not in the bundle, so these numbers are synthetic and are not the owner's trip rate.

```
## cusum (trips / 30 d over 8 seeds: mean [min-max]; tripped share)
null sigma=0.05                              trips= 0.00 [0-0] tripped=  0.0%
null sigma=0.1                               trips= 0.00 [0-0] tripped=  0.0%
null sigma=0.15                              trips= 0.00 [0-0] tripped=  0.0%
null sigma=0.2                               trips= 1.12 [0-3] tripped=  0.7%
window k=0.15kW/K sigma=0.05 (15 events)     trips= 0.00 [0-0] tripped=  0.0%
window k=0.3kW/K sigma=0.05 (15 events)      trips= 2.50 [0-5] tripped=  1.7%
window k=0.15kW/K sigma=0.1 (15 events)      trips= 0.00 [0-0] tripped=  0.0%
window k=0.3kW/K sigma=0.1 (15 events)       trips= 4.25 [1-9] tripped=  3.5%
window k=0.15kW/K sigma=0.15 (15 events)     trips= 0.62 [0-3] tripped=  0.5%
window k=0.3kW/K sigma=0.15 (15 events)      trips= 5.12 [1-9] tripped=  4.7%
ua_bias f=+0.50 sigma=0.05                   trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+1.09 sigma=0.05                   trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+2.00 sigma=0.05                   trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=-0.52 sigma=0.05                   trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+1.09 swing=10 sigma=0.05          trips= 0.00 [0-0] tripped=  0.0%
front 8K, f=0 (null for front) sigma=0.05    trips= 0.00 [0-0] tripped=  0.0%
front 8K + ua_bias f=+0.50 sigma=0.05        trips= 0.00 [0-0] tripped=  0.0%
front 8K + ua_bias f=+1.09 sigma=0.05        trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+0.50 sigma=0.1                    trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+1.09 sigma=0.1                    trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+2.00 sigma=0.1                    trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=-0.52 sigma=0.1                    trips= 0.00 [0-0] tripped=  0.0%
ua_bias f=+1.09 swing=10 sigma=0.1           trips= 0.12 [0-1] tripped=  0.1%
front 8K, f=0 (null for front) sigma=0.1     trips= 0.00 [0-0] tripped=  0.0%
front 8K + ua_bias f=+0.50 sigma=0.1         trips= 0.00 [0-0] tripped=  0.0%
front 8K + ua_bias f=+1.09 sigma=0.1         trips= 0.00 [0-0] tripped=  0.0%
## learners on the vent latch (latch | null: latch clear | mutant: vent branch dropped)
cop(_fold_measured_cop)                  refused:learners_frozen            | passes freeze (None)           | passes freeze (None)
dhw(async_learn_dynamics)                frozen:ventilation                 | runs                           | runs
buffer(_async_learn_buffer_cooling)      frozen:ventilation                 | runs                           | runs
sysid(_run_system_identification)        aborted:ventilation                | passes freeze (later outcome '', active-before=True) | passes freeze (later outcome '', active-before=True)
house(_learning_frozen keys)             ventilation                        | None                           | None
## latch on-then-off (carry 9), consecutive _update_current_state cycles
latch=True: learner_freeze_reason=ventilation
latch=True: learner_freeze_reason=ventilation
latch=False: learner_freeze_reason=None
latch=False: learner_freeze_reason=None
```

### Readings

1. **CUSUM trip rate.**
   - **Null (no window):** 0 trips per 30 days for noise sigma ≤ 0.15 °C per interval. At sigma 0.2 there are 1.1 trips per 30 days, so noise alone starts to trip the detector at about 0.2 °C.
   - **Open window (15 evening events, 3 h each):** extra air exchange of +0.15 kW/K is missed almost completely (0 to 0.6 trips). +0.3 kW/K, which triples the loss, trips on 2.5 to 5.1 of 15 events, a recall of 17–34 %.
   - So in this model the detector separates window from no-window, but its recall is low. The owner's 3 trips in about 30 h, two of them at night, does not fit this model's evening-window profile. Noise at or above 0.2 °C, or a bias the reference cannot follow, fits it better.
2. **The heat-loss-scale bias reading (L2, scale 2.09).** A UA-shaped bias puts a residual of -f·UA·ΔT·Δt/C into each interval. The arms below test it, both alone and with an 8 K two-day cold front, and **none of them trips the detector** (0 to 0.12 trips per 30 days):
   - |f| from 0.5 to 2.0;
   - a ±10 K diurnal swing;
   - the cold front.

   There are two reasons:
   - (a) the 24 h reference absorbs the bias level;
   - (b) at plausible ΔT the per-interval departure (≤ 0.065 °C for f = 1.09 with an 8 K front) stays under the 0.08 drift allowance.

   The sign matters too. If a learned 2.09 is *too high*, the model over-predicts loss and the residual comes out warm (positive), which a side -1 detector cannot accumulate at all. **Verdict: within this model, the 2.09 scale is not what trips the detector.** "A detector that trips on bias" is not reproduced. The open shapes are a bias that steps faster than the 24 h reference and exceeds 0.08 °C per interval (a heat-delivery or COP step, a sensor offset step), and residual noise of 0.2 °C or more. Separating those needs the owner's residual series: ask for a `debug_collect start` capture, as the carry text already allows.
3. **Which learners stop on the ventilation reason.** `_learning_frozen` (`custom_components/heatpump_optimizer/coordinator.py`, the `if self._vent_cusum.tripped: return "ventilation"` branch) is not scoped by keys, so every caller freezes. With the latch set:
   - COP: `_fold_measured_cop` returns `learners_frozen`.
   - DHW: `async_learn_dynamics` returns `ventilation`.
   - Buffer: `_async_learn_buffer_cooling` sets `ventilation`.
   - sysid: `_run_system_identification` aborts with `ventilation`.

   The null arm (latch clear) passes all four freeze gates. The perturbation, a `_learning_frozen` with the vent branch dropped, un-freezes all four, so the harness moves under its own perturbation. **All four of COP, DHW, buffer and sysid stop.** Other callers of `_learning_frozen` also stop:
   - `_fold_flow_lift`
   - `_async_learn_lower_floor_loss`
   - `_track_curve_comfort`
   - `_record_quiet_comfort_period`
   - `_dhw_probe_temperature` (the DHW lead-prediction filing and scoring)
   - `_inputs_unhealthy` (snapshot health)
   - the draw-range fold's `power_frozen`
4. **Carry 9 (sticky reason): confirmed closed.** Four consecutive `_update_current_state` cycles with the latch on, on, off, off read `ventilation, ventilation, None, None`. The reset is `self._learner_freeze_reason = None` in `_update_current_state`, before the learners run. Recorded as: `Carry: dismissed: freeze reason resets each cycle (item 9)`.

## Design note (architect note for R10-COP-GATE item E; for design review before any code)

**Question:** should the four non-house learners freeze on a suspected open window?

**Answer:** COP, DHW and buffer should not. sysid should, and keeps doing so.

| learner | what a window corrupts in its inputs | decision | what the freeze costs today |
|---|---|---|---|
| COP (`_fold_measured_cop`, `_fold_flow_lift`) | nothing. The window changes the house's heat demand, not the electric draw, the outdoor reading or the delivered heat that the fold divides. | **stop freezing** | each latched interval is a refused fold. The owner install has 15 folds in its lifetime against `COP_BASELINE_MIN_SAMPLES` 20. |
| DHW (`DhwProfileLearner.async_learn_dynamics`) | nothing. Tank decay and draws do not depend on the room's air exchange. | **stop freezing** | tank cooling and draw samples, plus `_dhw_probe_temperature` lead scoring |
| buffer (`_async_learn_buffer_cooling`) | only through house draw on a pump-off interval. That draw already contaminates the learner whatever the window does, and the mixing-valve branch already refuses it. | **stop freezing** (the fixer must confirm there is no pump-off house circulation path without a mixing valve; if one exists, keep it frozen) | standby-loss samples |
| sysid (`_run_system_identification`) | everything. It is a heat-loss step experiment, and a window is exactly the disturbance it cannot tell from UA. | **keep** (abort) | a lost experiment. That is R10-CEILING-PROBE F1's question, not this group's. |

The other fabric and room-temperature callers keep the freeze for the same reason sysid does: lower floor, flow-lift curve comfort and quiet-comfort all read the room temperature, which a window cools.

**Owning seam:** `coordinator.py`, the single owner of `_learning_frozen`. `dhw_learning.py` only calls it, through the `frozen=` callable that the coordinator wires. One owner, so this is not a two-owner design finding. The fixer must check `tests/seam_map.json` for this; I did not.

**Shape.**
- Change the signature to `_learning_frozen(self, *keys: str, room_air: bool = True) -> str | None`. With `room_air=False`, the `ventilation` branch is skipped. The external-heat, pump-signal, defrost, input-health, boost and tail branches keep their order.
- The default stays `True`, so the change fails closed: any caller nobody touches keeps today's behaviour.
- `room_air=False` is passed at exactly these sites:
  - `_fold_measured_cop`
  - `_fold_flow_lift`
  - `_freq_fold_blocked`'s `_learning_frozen(CONF_POWER_ENTITY)` (the kW-per-Hz map: power-side, not room-air)
  - the draw-range `power_frozen` read
  - `_async_learn_buffer_cooling`
  - `_dhw_probe_temperature`
  - the DHW wiring `frozen=functools.partial(self._learning_frozen, room_air=False)`
- The house, lower-floor, sysid, comfort and `_inputs_unhealthy` callers do not change.
- Invariants that hold:
  - the house learner's vent pass-through, which feeds the detector, is unchanged;
  - `learner_freeze_reason` still reads `ventilation` while the house learner is latched;
  - ventilation still ranks below an unusable input and above boost.

**Alternatives, and why each lost.**
1. Each caller filters `== "ventilation"` out of the result. This spreads the reason string over seven sites and would drift as reasons are added. It is also wrong on ranking: a caller that drops "ventilation" also loses the boost and tail reasons ranked below it, because `_learning_frozen` returns before reaching them.
2. A separate `_fabric_frozen()` that adds the vent branch to a vent-free `_learning_frozen`. This inverts the default: every existing caller silently stops freezing on a window, the house learner included, unless each one is rewired. That fails open.
3. Scope ventilation by keys, freezing only when `CONF_INDOOR_TEMP_ENTITY` is among the keys. This lost because the keys mean "which reading must be usable", not "which physics the caller models". The COP gate's keys include no indoor key, but `_inputs_unhealthy`'s do, and that change would make snapshot health depend on a meaning the parameter does not carry.

**Sibling sites:** `grep -n "_learning_frozen(" custom_components/heatpump_optimizer/*.py` finds 15 sites in `coordinator.py` and 0 call sites in `boost.py`. The DHW callable is at `frozen=self._learning_frozen`. The list above covers every one. Each site is either rewired or named as keeping the freeze.

**Evidence plan, by file.**
- Failing test, in `tests/features.py` beside the existing `_vent_cusum.tripped` cases: with the latch set, `_fold_measured_cop` does not return `learners_frozen`; DHW and buffer run; sysid still aborts `ventilation`; and the house learner still sets `ventilation`.
- Finder's harness: Appendix A, committed as `dev/audit/harnesses/r10_cop_gate_vent.py`. Its learners arm must read "passes freeze" for COP, DHW and buffer at the head, and "aborted:ventilation" for sysid at both ends.
- Null control: latch clear, where every learner passes at both ends.
- Mutation proof targets:
  - the `room_air` guard on the vent branch, which must fail the COP/DHW/buffer assertions;
  - each `room_air=False` call site, one mutant per learner gate, as the triage carry requires.
- Goldens: none expected to move. No solver output depends on the freeze.

**Hot files and serial position.** `coordinator.py` is the hot file. R10-COP-GATE's other items (#2262 COP fold observability) edit `_fold_measured_cop` and must serialize with this item. R10-CEILING-PROBE F1 (#2808) owns the sysid-abort half and is not touched here.

## Notes for the fixer

- Carry: R10-COP-GATE (item 8)
- Carry: R10-CEILING-PROBE (item F1)
- Carry: dismissed: freeze reason resets each cycle (item 9)
- The bias reading (L2) does not reproduce synthetically. Do not tune `VENT_CUSUM_*` in this group. If the owner's trip rate matters, the next step is the owner's residual series (`debug_collect start`), not a constant change.
- Detector recall measured 17–34 % for a window that triples the loss over 3 h. Any proposal to ungate the COP side on that basis has no need to fear false negatives, but recall is a separate finding and out of scope here.

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


async def main() -> None:
    lines = arm_cusum() + await arm_learners() + await arm_latch()
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
```
