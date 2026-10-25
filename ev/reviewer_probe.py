"""Reviewer's own probe of learner_progress_view (built by the review seat, not the finder's)."""
import sys, math
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from dataclasses import replace
from homeassistant.util import dt as dt_util
import heatpump_optimizer.coordinator as co
from heatpump_optimizer.learner_progress import gate_count, snapshot_rates
NOW = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
st0 = co.ThermalState()
p0 = co.ThermalParameters()
def view(house=0, lower=0, solar=0, cold=True, sunny=True, two=False, sensor=False, gains=True, ap=True, snaps=()):
    st = replace(st0, room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0,
                 outdoor_temperature=20.0 - (10.0 if cold else 4.0), solar_radiation=300.0 if sunny else 0.0)
    p = replace(p0); p.two_zone_enabled = two
    cfg = SimpleNamespace(lower_floor_temp_entity="sensor.l" if sensor else "", solar_aperture_learning_enabled=ap,
                          internal_gains_learning_enabled=gains)
    dt_util.freeze(NOW) if hasattr(dt_util, "freeze") else None
    try:
        return co.learner_progress_view(st, p, cfg, list(snaps), (house, lower, solar))
    finally:
        dt_util.freeze(None) if hasattr(dt_util, "freeze") else None
def snap(days, house=None, lower=None, solar=None):
    tl = {}
    if house is not None: tl["house_heat_loss_samples"] = house
    if lower is not None: tl["lower_floor_loss_samples"] = lower
    if solar is not None: tl["solar_aperture"] = {"n": float(solar)}
    return {"taken_at": (NOW - timedelta(days=days)).isoformat(), "learners": {"thermal_learning": tl}}
hn = gate_count(co.house_loss_converged, 0); gn = gate_count(co.internal_gains_gate_open, 0)
print(f"RESULT gate house={hn} gains={gn} solar_min={co.SOLAR_APERTURE_MIN_SAMPLES}")
viol = 0; rows = 0
# exhaustive grid: counts x weather x rate x config
for house in (0, 1, hn-1, hn, hn+1, gn-1, gn, gn+5, 500):
  for solar in (0, 29, 30, 31, 200):
    for lower in (0, 5, 300):
      for cold in (True, False):
        for sunny in (True, False):
          for two, sensor in ((True, True), (False, True), (True, False)):
            for sn in ((), (snap(2.0, house=max(0,house-20), lower=max(0,lower-5), solar=max(0,solar-6)),), (snap(2.0, house=house, lower=lower, solar=solar),), (snap(0.5, house=0),)):
              v = view(house, lower, solar, cold, sunny, two, sensor, snaps=sn)
              for name, e in v.items():
                rows += 1
                ph = e["phase"]
                bad = []
                if ph not in ("off", "counting", "settling", "waiting"): bad.append("phase")
                if ph != "counting" and e["eta_days"] is not None: bad.append("eta-outside-counting")
                if (ph == "waiting") != (e["waiting_for"] is not None): bad.append("waiting_for")
                if ph == "counting" and e["progress"] != round(e["samples"]/e["samples_needed"],3): bad.append("count-progress")
                if ph == "off" and name == "lower" and two and sensor: bad.append("lower-off-wrong")
                if name == "lower" and not (two and sensor) and ph != "off": bad.append("lower-on-wrong")
                if ph == "settling" and e["samples_needed"] is not None and e["samples"] < e["samples_needed"]: bad.append("settling-below-gate")
                if e["eta_days"] is not None and (not math.isfinite(e["eta_days"]) or e["eta_days"] <= 0): bad.append("eta-nonpos")
                if bad:
                    viol += 1
                    if viol <= 10: print("VIOL", name, house, solar, lower, cold, sunny, two, sensor, len(sn), e, bad)
print(f"RESULT grid rows={rows} violations={viol}")
# specific readings
print("RESULT fresh", view(0, gains=True)["house"])
print("RESULT lower_zero_two_zone", view(0, lower=0, two=True, sensor=True)["lower"])
print("RESULT gains_settling_warm_norate", view(gn+5, cold=False)["gains"])
print("RESULT house_counting_rate", view(30, snaps=(snap(2.0, house=10),))["house"])
print("RESULT nan_solar", view(0, solar=float('nan'), snaps=(snap(2.0, solar=5),))["solar"])
print("RESULT future_snap", view(30, snaps=(snap(-1.0, house=10),))["house"])
print("RESULT older_behind_young", view(30, snaps=(snap(5.0, house=0), snap(0.2, house=29)))["house"])
# eta accuracy null control: constant-rate plant, the ETA must equal days to gate
errs = []
for rate in (3, 7, 12, 25):
  for start in (0, 10, 30, 45):
    if start >= hn: continue
    n_now = start + 2*rate
    e = view(n_now, snaps=(snap(2.0, house=start),))["house"]
    if e["phase"] == "counting":
      true_days = (hn - n_now) / rate
      errs.append(e["eta_days"] - true_days)
print(f"RESULT const_rate_eta_err max_abs={max(abs(x) for x in errs):.3f} n={len(errs)}")
