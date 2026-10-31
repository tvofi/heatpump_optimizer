#!/usr/bin/env python3
"""Owner-reported quirk: DHW-only summer plan scores 7/100 despite cheap-hour
buying; envelope scores 0 with no space heating.

Measures, by EXECUTING the production score code (not a re-implementation):
1. HeatPumpOptimizerCoordinator._fold_score_sample + _close_score_day over
   synthetic day shapes (coordinator.py:9441-9510), EMA per SCORE_ALPHA.
2. The day-skip rules (kwh < 0.2, hours < 1.0, mean_spot <= 0.01) and what
   they do to the EMA when every summer day is skipped.
3. _scores_view's envelope term on configured-parameter shapes
   (coordinator.py:9511-9560): tau_h = mass / loss, envelope = clip((tau-20)/80).

Command: PYTHONPATH=tests/hastub python3 tools/audit/round4/D0/owner_quirk_score.py
Expected: see RESULT lines; no single expected number - this is a mechanism
census over day shapes, baseline 7dd68dd, box-load-free (imports + arithmetic).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import types
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, "custom_components")
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402


class FakeParams:
    def __init__(self, mass, loss, scale):
        self.room_thermal_mass = mass
        self.heat_loss_coefficient = loss
        self.house_heat_loss_scale = scale


def run_days(days, start_score=None):
    """Drive the production fold/close pair over a list of day dicts.

    Each day: list of (kwh, spot, known) interval samples. Returns the
    operation score after the run (None if no day ever scored).
    """
    fake = types.SimpleNamespace(
        _score_day={}, _operation_score=start_score,
        _schedule_ledger_save=lambda: None,
    )
    fold = HeatPumpOptimizerCoordinator._fold_score_sample.__get__(fake)
    close = HeatPumpOptimizerCoordinator._close_score_day.__get__(fake)
    fake._close_score_day = close  # the fold rolls days through the real close
    t0 = datetime(2026, 7, 1)
    for di, samples in enumerate(days):
        for hi, (kwh, spot, known) in enumerate(samples):
            fold(t0 + timedelta(days=di, hours=hi), kwh, kwh * spot, spot, 1.0, known)
    # close the final day explicitly (a new-day sample would do it in prod)
    close()
    return fake._operation_score


def day(hours, kwh_by_hour, spot_by_hour, known=True):
    return [
        (kwh_by_hour.get(h, 0.0), spot_by_hour[h], known)
        for h in range(hours)
    ]


R = []

# --- operation score: mechanism census --------------------------------------
# Flat-price control: uniform buy at mean -> saved 0 -> sample 0.
flat = day(24, {}, {h: 0.30 for h in range(24)})
R.append(("control_flat_day_sample", run_days([flat])))

# The docstring's own bar: 20 % below flat scores 100.
cheap20 = day(24, {h: 1.0 for h in (2, 3, 4)}, {h: (0.24 if h in (2, 3, 4) else 0.30) for h in range(24)})
R.append(("control_20pct_below_sample", run_days([cheap20])))

# S3: summer DHW bought 50 % below mean, but a continuous measured base load
# (HP standby/electronics on the same meter) buys at the mean all day.
base_kwh = {h: 0.5 for h in range(24)}
base_kwh.update({2: 0.5 + 1.0, 3: 0.5 + 1.0, 4: 0.5 + 1.0})
s3 = day(24, base_kwh, {h: (0.05 if h in (2, 3, 4) else 0.10) for h in range(24)})
R.append(("summer_dhw50pct_off_with_12kwh_base", run_days([s3])))

# S4: same with a heavier 1 kW continuous base (24 kWh at the mean).
base_kwh = {h: 1.0 for h in range(24)}
base_kwh.update({2: 2.0, 3: 2.0, 4: 2.0})
s4 = day(24, base_kwh, {h: (0.05 if h in (2, 3, 4) else 0.10) for h in range(24)})
R.append(("summer_dhw50pct_off_with_24kwh_base", run_days([s4])))

# S5: DHW reheat rebound - tank actually reheats at mean-priced hours
# (lagged draw), despite the PLAN naming the cheap hours.
s5 = day(24, {h: 0.5 + (1.0 if h in (12, 13, 14) else 0.0) for h in range(24)},
         {h: (0.05 if h in (2, 3, 4) else 0.10) for h in range(24)})
R.append(("summer_dhw_rebound_at_mean_price", run_days([s5])))

# S6: the skip rule - a spring day scores low, then every summer day's
# mean spot is <= 0.01 (sunny windy weekend curve) so the EMA never moves.
spring = day(24, {h: 1.0 for h in (2, 3, 4)},
             {h: (0.342 if h in (2, 3, 4) else 0.35) for h in range(24)})
skipped = [day(24, {h: 1.0 for h in (2, 3, 4)},
               {h: 0.008 for h in range(24)}) for _ in range(30)]
R.append(("skip_rule_freeze_after_spring_day",
          run_days([spring] + skipped)))

# EMA time constant at SCORE_ALPHA: how many 0-samples to drag 100 -> ~7.
ema = run_days([cheap20])
zero_days = [flat for _ in range(60)]
ema = run_days(zero_days, start_score=ema)
R.append(("ema_after_60_flat_days_from_100", ema))

# --- envelope: the tau formula on plausible configured shapes ---------------
def envelope(mass_kwh_per_c, loss_kw_per_c, scale=1.0):
    p = FakeParams(mass_kwh_per_c, loss_kw_per_c, scale)
    fake = types.SimpleNamespace(_ctx=types.SimpleNamespace(_thermal_params=p),
                                 _thermal_params=p, _cop_baseline={},
                                 _cop_health_cusum=types.SimpleNamespace(stat=0.0),
                                 _operation_score=None)
    view = HeatPumpOptimizerCoordinator._scores_view.__get__(fake)
    return view()["envelope"]

R.append(("envelope_tau20h_leaky_default", envelope(20.0, 1.0)))
R.append(("envelope_tau50h", envelope(50.0, 1.0)))
R.append(("envelope_tau100h_insulated", envelope(100.0, 1.0)))
# A light, poorly-insulated preset (small mass, big loss) - the shape a
# summer DHW-only install shows when nothing was ever learned.
R.append(("envelope_light_leaky_preset", envelope(8.0, 0.6)))

print("RESULT alpha=%s" % C.SCORE_ALPHA)
for name, val in R:
    print("RESULT %s=%s" % (name, val))
import time
print("RESULT thread_factor=%.6f" % (time.process_time() / max(time.thread_time(), 1e-9)))
print("RESULT load1=%.2f" % float(os.getloadavg()[0]))
