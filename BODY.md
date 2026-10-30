# Probe r10-live-plan-energy — result

Measured at cc930cdd1a3cfb005ba7ec557f4451ff5e53e364 (= origin/main), detached worktree. Read-only: no tracked file changed.

## Verdict

**Mostly (b), with an unsettled (a) on the lower-floor ratio, plus a secondary (f) labelling defect.** The ~67 kWh plan is what the model in force predicts it takes to *hold the comfort floor*. It is not price-driven preheat: the flat-price null makes no difference. It does not hold the room above the band either: the planned room falls to about 18.9. The model it plans with has an effective UA of 0.641 kW/K, which is the configured two-zone nameplates multiplied by both learned corrections. 75 % of that loss sits on the lower floor, and the learned `lower_floor_loss_ratio` of 1.943 is the largest single lever. The label `preheat_weather` is wrong: it fires under perfectly flat weather because the learned `house_heat_loss_scale` > 1.1 is read as "weather". That label is the (f) defect.

- (d) preheat for a cold spell: **refuted**. With flat 6 °C and a flat price (arm 7b) the plan is still one slot, 51.8 kWh, 88/96 steps `preheat_weather`.
- (e) comfort pull or margins hold the room above the band: **refuted**. The planned room min/median is 18.6/18.9. Margins off makes no change (arm 6), and margins at their 0.8 cap add 4.3 kWh (6a). The mold floor is capped at the configured target 18 = min_temp, so it is inert here.
- (c) a cold lower floor or slab start: **minor**. Starting the lower floor and slab at 18 adds only +1.9 kWh. What the lower floor does drive is its learned *loss* (the ratio), not its starting temperature.
- The configured `house_heat_loss_coefficient` 0.4 is **inert in two-zone mode**. The solve's UA is upper + lower×ratio (`optimizer.py:2122-2126`, `thermal_model.py:563-573`), so arm 4 gives UA 0.33 = 0.13 + 0.20. The reported 0.6409 = (0.13 + 0.20×1.943)×1.2356 exactly (`coordinator.py:2907-2911`). The "×1.24 on top of 0.4" the brief worried about does not happen. The scale multiplies 0.13 + 0.389 instead.

## Arithmetic check

The brief's estimate, 0.64 kW/K × ~14 K / COP 3.8 ≈ 57 kWh/day, is borne out. In arm 1 the zones hold upper ~19.8 and lower ~18.0 at an outdoor mean of 6 °C. The loss is 0.16 kW/K × 13.8 K (upper) plus 0.48 kW/K × 12 K (lower), about 8 kW of heat. At the modelled COP of 3.41 that is about 2.3 kW electrical, or 52 kWh/24 h. The live 66.7 kWh fits a forecast about 2-3 K colder: arm s3, at a 3 °C mean, gives 71.4 kWh. The live outdoor forecast series would settle the residual.

## Measured table

Horizon 96×15 min from 2026-10-30 18:45. Outdoor 6±2 °C (diurnal cosine, min 4, max 8). The price is an SE3 late-October shape plus 1.15 SEK of fee and tax, mean ~2.2 SEK/kWh. Zone columns are min/median/max of the planned trajectories. In every two-zone arm the initial upper floor = room and lower = room−1.
```
arm                                               kWh    cost slots  on     UA  reason  room  upper  lower  slab (min/med/max)
1 as configured, indoor 22                      51.67  105.91     1  94  0.641  None  18.6/18.9/22.0  19.3/19.8/22.0  17.5/18.0/21.0  19.8/20.9/22.0  cop~3.41 two=True
2 indoor 20                                     53.34  110.58     1  95  0.641  None  18.6/18.9/20.0  19.3/19.8/20.1  17.5/18.0/19.0  19.8/20.9/21.3  cop~3.41 two=True
3 setup heat-loss/mass values + learned         13.21   23.09     3  37  0.267  None  18.1/18.8/22.0  18.0/18.8/22.0  18.1/18.7/21.0  19.2/20.4/23.6  cop~3.41 two=True
3b setup values, learning reset                  3.38    5.97     2  26  0.150  None  18.3/19.4/22.0  18.0/19.1/22.0  18.6/19.7/21.0  19.0/20.4/22.0  cop~3.41 two=True
4 configured, no learned scale/ratio            24.00   46.60     2  92  0.330  None  17.6/18.5/22.0  17.7/18.5/22.0  17.5/18.4/21.0  19.0/19.9/22.0  cop~3.41 two=True
4b single-zone UA=0.4, no scale                 22.39   38.97     3  50  0.400  None  18.0/18.8/22.0  18.0/18.8/22.0  18.0/18.8/21.9  18.3/20.9/27.9  cop~3.41 two=False
5 single-zone UA=0.4 x1.2356                    30.33   54.04     2  60  0.494  None  17.7/18.6/22.0  17.7/18.6/22.0  17.7/18.6/21.8  18.4/21.4/29.1  cop~3.41 two=False
5b single-zone UA=0.6409 (learned effective)    43.09   78.57     2  74  0.641  None  17.6/18.5/22.0  17.6/18.5/22.0  17.6/18.5/21.8  18.4/22.0/29.6  cop~3.41 two=False
6a margins at cap 0.8 (on, worst)               56.00  115.64     1  94  0.641  None  19.4/19.7/22.0  20.2/20.7/22.0  18.3/18.8/21.0  20.7/21.9/22.3  cop~3.41 two=True
6 margins off (=1)                              51.67  105.91     1  94  0.641  None  18.6/18.9/22.0  19.3/19.8/22.0  17.5/18.0/21.0  19.8/20.9/22.0  cop~3.41 two=True
7 null: flat price                              51.99  110.15     1  95  0.641  None  18.6/18.9/22.0  19.6/19.7/22.0  17.5/18.0/21.0  20.5/20.9/22.0  cop~3.41 two=True
7b flat price, flat 6 °C                        51.83  109.81     1  95  0.641  None  18.5/19.0/22.0  19.4/20.0/22.0  17.5/18.0/21.0  20.4/21.1/22.0  cop~3.41 two=True
s1 scale only (ratio 1)                         30.72   60.65     1  95  0.408  None  17.6/18.3/22.0  17.7/18.4/22.0  17.5/18.2/21.0  19.3/20.1/22.0  cop~3.41 two=True
s2 ratio only (scale 1)                         40.78   82.87     1  93  0.519  None  18.4/18.8/22.0  19.1/19.6/22.0  17.5/18.0/21.0  19.4/20.3/22.0  cop~3.41 two=True
s3 outdoor 3 °C mean                            71.37  147.54     1  94  0.641  None  18.8/19.1/22.0  19.6/20.2/22.0  17.5/18.0/21.0  20.3/21.7/22.2  cop~3.15 two=True
s4 outdoor 9 °C mean                            34.87   70.66     1  93  0.641  None  18.3/18.7/22.0  19.0/19.3/22.0  17.5/18.0/21.0  19.3/20.2/22.0  cop~3.67 two=True
x cold lower floor 18, slab 18                  53.58  111.37     1  95  0.641  None  18.6/18.9/22.0  19.3/19.8/22.1  17.2/18.0/18.3  18.0/20.9/21.3  cop~3.41 two=True
```

Space reasons, from `result.space_reasons`, flat price and flat 6 °C, configured nameplates:

| learned | reasons |
|---|---|
| none | cheap_price 87, terminal 3, comfort_floor 4 |
| ratio 1.943 only | cheap_price 87, terminal 7 |
| scale 1.05 only | cheap_price 75, comfort_floor 13, terminal 5 |
| scale 1.2356 only | **preheat_weather 51**, comfort_floor 40, terminal 3 |
| both (arm 1, real prices) | **preheat_weather 88**, terminal 6, idle 2 (step 0 off, one slot: reproduces the live plan shape) |

Readings:
- Learning roughly doubles the plan: 24.0 kWh (arm 4) → 51.7 kWh (arm 1). The ratio alone adds +16.8 kWh (s2) and the scale alone +6.7 (s1).
- The configured nameplates, against the setup values with learning reset, take the plan from 3.4 kWh (3b) to 24.0 (4). The owner raised upper+lower from 0.15 to 0.33 kW/K and cut the masses roughly 2-5×.
- Indoor 22 against 20 changes little (arms 1 and 2). The low masses (1.0/1.26 kWh/K) dump the initial surplus within hours.
- In the planned lower-floor trajectory, the floor sits at 17.5-18.0 while the pump runs ~2.1 kW continuously. The model cannot keep the lower zone warm, which is the signature of an inflated lower loss.

## Harness (inline)

Run as `python3 -I probe.py <worktree>` from the worktree root. It takes the production path: `OptimizationConfig.from_mapping` → `ThermalParameters.from_config` → `replace(**learned)` (the `_publish_params` path, `coordinator.py:2360-2367`) → `HeatPumpOptimizer(...).optimize(inputs=SolveInputs)`. Margins are passed the way `_solve_record` passes `min_temp_margins`. The coordinator-only extras (tariff peak, baseline load, cycling cost) are left at their defaults.

```python
"""r10-live-plan-energy probe: rebuild the owner's two-zone solve through the production path."""
import sys, math
from dataclasses import replace
from datetime import datetime
import numpy as np
WT = sys.argv[1]
sys.path[:0] = [f"{WT}/tests/hastub", f"{WT}/custom_components", f"{WT}/tests"]
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs
from heatpump_optimizer import const as C
SZ = {"two_zone_mode": C.TWO_ZONE_MODE_OFF}

START = datetime(2026, 10, 30, 18, 45)
N = 96
hours = np.array([(START.hour + START.minute / 60 + i * 0.25) % 24 for i in range(N)])
# SE3 late-October shape, SEK/kWh incl. grid fee + tax (~2.3 avg, matching 152.84/66.71)
spot = np.interp(hours, [0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 23, 24],
                 [0.45, 0.35, 0.40, 1.30, 1.50, 0.90, 0.85, 1.40, 1.80, 1.10, 0.60, 0.45])
PRICE = spot + 1.15
OUT = 6.0 + 2.0 * np.cos((hours - 14) / 24 * 2 * np.pi)   # 4..8 °C, median 6

CFG = {
    "target_temperature": 18.0, "comfort_temp_day": 19.5, "comfort_temp_night": 18.5,
    "min_temperature": 18.0, "max_temperature": 21.0, "comfort_weight": 2.0,
    "two_zone_mode": C.TWO_ZONE_MODE_ON, "upper_floor_area_ratio": 0.5, "inter_zone_heat_transfer": 0.5,
    "house_heat_loss_coefficient": 0.4, "lower_floor_heat_loss": 0.2, "upper_floor_heat_loss": 0.13,
    "lower_floor_thermal_mass": 1.0, "upper_floor_thermal_mass": 1.26,
    "slab_thermal_mass": 1.0, "slab_heat_transfer": 1.5,
}
SETUP = {"house_heat_loss_coefficient": 0.15, "lower_floor_heat_loss": 0.07, "upper_floor_heat_loss": 0.08,
         "lower_floor_thermal_mass": 5.0, "upper_floor_thermal_mass": 3.0,
         "slab_thermal_mass": 2.0, "slab_heat_transfer": 0.8}
LEARNED = {"house_heat_loss_scale": 1.2356, "lower_floor_loss_ratio": 1.943}

def solve(cfg, learned, room=22.0, lower=None, slab=None, price=PRICE, out=OUT, margins=None):
    opt_cfg = OptimizationConfig.from_mapping(cfg)
    p = ThermalParameters.from_config(cfg)
    p = replace(p, **learned)        # coordinator _publish_params path
    m = ThermalModel(p)
    lower = room - 1.0 if lower is None else lower
    st = ThermalState(room_temperature=room, outdoor_temperature=float(out[0]),
                      upper_floor_temperature=room, lower_floor_temperature=lower,
                      slab_temperature=lower + 1.0 if slab is None else slab)
    r = HeatPumpOptimizer(m, opt_cfg).optimize(inputs=solve_inputs(
        initial_state=st, prices=price, outdoor_temps=out, start_time=START,
        min_temp_margins=margins))
    pw = np.asarray(r.power_schedule, float)
    on = pw > 1e-3
    slots = int(np.sum(on[1:] & ~on[:-1]) + on[0])
    def tr(name):
        v = getattr(r, name, None)
        return np.asarray(v, float) if v is not None and len(v) else None
    ua = (p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned) * p.house_heat_loss_scale if p.two_zone_enabled \
        else p.heat_loss_coefficient * p.house_heat_loss_scale
    return dict(kwh=float(pw.sum() * 0.25), cost=float(r.predicted_cost), slots=slots, on=int(on.sum()),
                ua=ua, two=p.two_zone_enabled, reason=(getattr(r,"predictive_info",None) or {}).get("space_reason"),
                room=tr("room_temp_trajectory"), up=tr("upper_temp_trajectory"),
                lo=tr("lower_temp_trajectory"), slab=tr("slab_temp_trajectory"), pw=pw,
                maxkw=p.max_electrical_power, cop=float(np.mean([m.compute_cop(float(t)) for t in out])), status=getattr(r, "status", None))

def fmt(x):
    return "-" if x is None else f"{x.min():.1f}/{np.median(x):.1f}/{x.max():.1f}"

ARMS = [
    ("1 as configured, indoor 22", lambda: solve(CFG, LEARNED, 22.0)),
    ("2 indoor 20", lambda: solve(CFG, LEARNED, 20.0)),
    ("3 setup heat-loss/mass values + learned", lambda: solve({**CFG, **SETUP}, LEARNED, 22.0)),
    ("3b setup values, learning reset", lambda: solve({**CFG, **SETUP}, {}, 22.0)),
    ("4 configured, no learned scale/ratio", lambda: solve(CFG, {}, 22.0)),
    ("4b single-zone UA=0.4, no scale", lambda: solve({**CFG, **SZ}, {}, 22.0)),
    ("5 single-zone UA=0.4 x1.2356", lambda: solve({**CFG, **SZ}, {"house_heat_loss_scale": 1.2356}, 22.0)),
    ("5b single-zone UA=0.6409 (learned effective)", lambda: solve({**CFG, **SZ, "house_heat_loss_coefficient": 0.6409}, {}, 22.0)),
    ("6a margins at cap 0.8 (on, worst)", lambda: solve(CFG, LEARNED, 22.0, margins=np.full(N, 0.8))),
    ("6 margins off (=1)", lambda: solve(CFG, LEARNED, 22.0)),
    ("7 null: flat price", lambda: solve(CFG, LEARNED, 22.0, price=np.full(N, float(PRICE.mean())))),
    ("7b flat price, flat 6 °C", lambda: solve(CFG, LEARNED, 22.0, price=np.full(N, float(PRICE.mean())), out=np.full(N, 6.0))),
    ("s1 scale only (ratio 1)", lambda: solve(CFG, {"house_heat_loss_scale": 1.2356}, 22.0)),
    ("s2 ratio only (scale 1)", lambda: solve(CFG, {"lower_floor_loss_ratio": 1.943}, 22.0)),
    ("s3 outdoor 3 °C mean", lambda: solve(CFG, LEARNED, 22.0, out=OUT - 3.0)),
    ("s4 outdoor 9 °C mean", lambda: solve(CFG, LEARNED, 22.0, out=OUT + 3.0)),
    ("x cold lower floor 18, slab 18", lambda: solve(CFG, LEARNED, 22.0, lower=18.0, slab=18.0)),
]
if __name__ == "__main__":
    print(f"{'arm':<46}{'kWh':>7}{'cost':>8}{'slots':>6}{'on':>4}{'UA':>7}  reason  room  upper  lower  slab (min/med/max)")
    for name, f in ARMS:
        d = f()
        print(f"{name:<46}{d['kwh']:7.2f}{d['cost']:8.2f}{d['slots']:6d}{d['on']:4d}{d['ua']:7.3f}  {d['reason']}  "
              f"{fmt(d['room'])}  {fmt(d['up'])}  {fmt(d['lo'])}  {fmt(d['slab'])}  cop~{d['cop']:.2f} two={d['two']}")
```

## Heat-loss learner: bias review

How it fits:
- `house_heat_loss_scale` comes from a Newton step on the **upper zone** residual. That is the BTHome indoor sensor, with base_u = upper loss and C = upper mass (`coordinator.py:1206-1218`, `5474-5530`). It multiplies both zones.
- `lower_floor_loss_ratio` comes from the lower-zone residual on T6, about base_u = lower×scale (`coordinator.py:5577-5650`). The product lower×ratio×scale is therefore the lower zone's own fit, so **the ratio is not double-counted on top of the scale**. That suspicion is refuted by construction.
- Step: EWMA α 0.02, trust region 0.5 (`coordinator.py:1446,1472`; `thermal_model.py:2353-2412`). Gates: ΔT ≥ 6 (`:1449`) and |residual| ≤ 1.0 K (`:1463`). Bounds 0.3-3.0 for both (`const.py:1394-1395`, `1413-1414`).

Candidate upward biases, each with what would settle it:
1. **Sensor switch, no reset (strongest candidate).** Changing `indoor_temp_entity` (T6 → BTHome) or `lower_floor_temp_entity` (now T6) neither resets nor voids either learner. The options path resets the fabric only for `house_heat_loss_coefficient`/buffer keys (`coordinator.py:~6242-6280`). Re-anchoring re-expresses only on nameplate UA edits (`coordinator.py:5209-5285`). The entity keys are read-only at `coordinator.py:5438`, `5602` and `6347`. So the evidence fitted while T6 was "indoor", and the ratio fitted with T6 as the lower floor, both survive. A heat-pump T6 that reads below the real floor air (hydronic or near-floor placement) inflates the ratio directly: the model's lower zone always looks too warm, so the residual stays negative and the ratio climbs, which matches the 17.5-18 planned lower floor. *Settles it:* the T6 time series against BTHome, and the sample counts at the time of the switch (store `house_heat_loss_samples` / `lower_floor_loss_samples` before and after).
2. **DHW apportioned by the commanded split.** With a power entity, the space power is measured − commanded DHW share (`coordinator.py:4707-4752`, split `4662-4685`). If the pump makes DHW while the plan commanded space and no mode entity is observed, DHW electricity is booked as space heat, which pushes UA up. Immersion and resistive heat are excluded (`:4718-4723`). *Settles it:* whether a pump-mode entity is configured and observed (`mode_observed`).
3. **Modelled, not measured, COP in the replay.** `simulate_step` → `compute_cop(outdoor, humidity)` (`thermal_model.py:3536`). The measured COP has only 3 samples (cop_scale 0.999), so the heat booked = draw × modelled COP. For two-zone UFH the real supply is lower and the real COP higher, which would bias UA *down*, not up. Not the cause.
4. **Defrost:** frozen, not counted (`_learning_frozen`, `coordinator.py:6574` ff.). Not the cause.
5. **Solar:** a missing radiation reading is treated as dark (`thermal_model.py:1629`, threshold 50 W/m², `const.py:1049`). Unmodelled sun makes the room warmer than predicted, which biases UA *down*. Internal gains: flat 0.3 kW (`thermal_model.py:540`) unless profile learning is on. Under-stated gains would bias UA up, but only by gains/ΔT ≈ 0.02-0.04 kW/K, which is small.
6. **Configured masses.** At steady state the fit returns heat/ΔT whatever C is. But with C at 1.0/1.26 kWh/K, a 15-minute interval's predicted swing is large, so the |residual| ≤ 1 K gate discards asymmetrically. Not measured here; it would need a replay study.

Is 0.64 kW/K plausible? It implies ~26 kW of heat at −20 °C, about 3-4× a typical Swedish villa and 4.3× the setup's 0.15. It is plausible only if the meter really shows ~2.3 kW average space draw at an outdoor 6 °C. The probe cannot see that.

## Diagnostics fields that would settle (a) against (b)

- The measured heat-pump electrical energy per day (power/energy entity) over the last week, plus outdoor mean. This is the direct test of 0.64 kW/K.
- `pump mode` entity configured / `mode_observed`, and the DHW kWh share.
- The lower-floor (T6) history against the BTHome room, and what T6 physically is on this pump.
- The thermal learning store: `house_heat_loss_anchor`, `lower_floor_loss_anchor`, `house_heat_loss_basis`, and sample counts. Plus the log lines "Re-anchored learned house heat loss scale" and "cannot be expressed", with dates against the sensor switch and the owner's nameplate edits.
- The live solve's outdoor forecast series. That explains 52 against 67 kWh.

## Fix brief (minimal)

1. **(f) The `preheat_weather` label is mis-attributed. This is a confirmed defect.** The classifier labels any non-floor, non-terminal heating step `preheat_weather` when `heat_loss_factors[i] > 1.1`, before the price test (`optimizer.py:1436-1448`, constant `payload.py:60`). The factor carries the learned `house_heat_loss_scale`, so a house with scale > 1.1 gets "preheat for weather" under flat weather (measured: scale 1.05 → 0 steps, 1.2356 → 51 steps). The fix is to test the forecast's weather component only, the factor relative to its own scale-free baseline, so a learned level never reads as weather. Pin: flat-weather, scale 1.24 → zero `preheat_weather`. Owner: **R10-SAV-REASONS** (roster `dev/programme/rosters/wave-r10-groups.json:992`, brief line 1043). **R10-ARCH-SHAPES-CLASSIFIER** (`:10145`, names `classify_space_steps` at `:10181-10184`) claims the shape. This is a separate seam from R10-HOTFIX-AWAY-LIVE.
2. **(a, candidate) No learner reset on a temperature-entity swap.** When `indoor_temp_entity` or `lower_floor_temp_entity` changes id, void that learner's evidence: samples → 0, confidence 0, the same path as the basis voiding in `_reanchor_house_heat_loss_scale`. Learned evidence then never carries across a sensor that measures a different place. Pin: swap the lower entity, and the ratio confidence is 0 with the next folds starting fresh. Owner: **R10-RATIO-ANCHOR** (roster `:328`, brief `:325` names both learners). This is the closest match; the roster has no explicit owner for `_async_learn_*_loss`. Whether it *caused* the 1.943 needs the T6 history above. File it as measure-first, not as a proven defect.
3. **(b) No code change.** In two-zone mode the plan is consistent with what was configured and learned. The UX gap is that `house_heat_loss_coefficient` (0.4) is inert in two-zone mode while the options flow lets the owner edit it. A D4/D10 note, not this probe's.

## Process notes
- The session-start `toolchain:` line read EXPORTED. venv-ci python3 was on PATH.
- The frugal routing hook capped inline search operations. Its locates went to read-only scout workers, and every cited line was read by a worker or by this seat.
