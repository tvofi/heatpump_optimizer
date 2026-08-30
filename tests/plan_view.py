import os, sys, json
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from profiles import prices, weather, house, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

START = datetime(2026,1,15,0,0)
cfg = house(two_zone=False, dhw=True)
p = ThermalParameters.from_config(cfg); p.dhw_enabled = True
oc = OptimizationConfig(horizon_hours=24, time_step_minutes=15,
    target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
    max_temp=cfg["max_temperature"])
opt = HeatPumpOptimizer(ThermalModel(p), oc)
pr = prices("winter_typical", START)
ot, wind, rain, sol = weather("winter_cold", START)
st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
    outdoor_temperature=float(ot[0]), dhw_temperature=50.0,
    dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
r = opt.optimize(st, pr, ot, wind, rain, sol, START)

# v5.2.0: the DHW expected-error band comes off the tank's own accuracy
# record. Seeded here with a widening-with-lead sigma so the payload
# card.mjs renders actually carries a band; a fresh record publishes
# nulls, which the card test covers separately by nulling these out.
from heatpump_optimizer.accuracy import AccuracyTracker
dhw_acc = AccuracyTracker()
for lead, err in ((1.0, 0.4), (3.0, 0.9), (6.0, 1.5), (12.0, 2.2), (24.0, 3.0)):
    dhw_acc.lead_sigma[lead] = err
    dhw_acc.lead_counts[lead] = 20

class Fake:
    _opt_config = oc
    _dhw_accuracy = dhw_acc
    _build_plan_views = Coord._build_plan_views
    _dhw_confidence_band = Coord._dhw_confidence_band
    _plan_slots = staticmethod(Coord._plan_slots)
views = Fake()._build_plan_views(r)

for key in ("space_plan","dhw_plan"):
    v = views[key]
    print("==", key, "points", len(v["forecast"]), "slots", len(v["slots"]),
          "kWh", v["total_energy_kwh"], "cost", v["total_cost"], "active", v["active_now"])
    print("  first fc:", json.dumps(v["forecast"][0]))
    if v["slots"]:
        print("  first slot:", json.dumps(v["slots"][0]))
        print("  last slot :", json.dumps(v["slots"][-1]))

# ---- reason codes and price provenance (items 16, 7) ---------------------
#
# The plan sensors used to publish which slots were chosen but never why, which
# made an unexpected slot indistinguishable from a bug. Check the codes survive
# the whole path from the optimizer to the sensor payload the card reads.
issues = []
for key, power_key in (("space_plan", "space_power"), ("dhw_plan", "dhw_power")):
    forecast = views[key]["forecast"]
    heating = [p for p in forecast if (p.get(power_key) or 0.0) > 0.05]
    if heating and any(p.get("reason") in (None, "idle") for p in heating):
        issues.append(f"{key}: heating steps with no reason code")
    if any("price_known" not in p for p in forecast):
        issues.append(f"{key}: forecast points missing price provenance")
    slots = views[key]["slots"]
    if slots and any("reason" not in s for s in slots):
        issues.append(f"{key}: slots missing a dominant reason")

# v5.2.0: the hot-water band. Every step must carry both keys (the card
# reads them by name), and where both are present they must bracket the
# curve they belong to — a band that does not contain its own centre is
# worse than no band.
_dhw_fc = views["dhw_plan"]["forecast"]
if any("dhw_temp_lo" not in p or "dhw_temp_hi" not in p for p in _dhw_fc):
    issues.append("dhw_plan: forecast points missing the expected-error band")
_banded = [
    p for p in _dhw_fc
    if p.get("dhw_temp_lo") is not None and p.get("dhw_temp") is not None
]
if not _banded:
    issues.append("dhw_plan: the seeded accuracy record produced no band")
if any(
    not (p["dhw_temp_lo"] <= p["dhw_temp"] <= p["dhw_temp_hi"]) for p in _banded
):
    issues.append("dhw_plan: band does not bracket dhw_temp")
if _banded:
    _widths = [p["dhw_temp_hi"] - p["dhw_temp_lo"] for p in _banded]
    print(
        "dhw band width: first %.2f last %.2f °C over %d steps"
        % (_widths[0], _widths[-1], len(_widths))
    )
    if not _widths[-1] > _widths[0]:
        issues.append("dhw_plan: band does not widen with lead time")

reasons = sorted({p.get("reason") for p in views["space_plan"]["forecast"]} - {None})
print("space reasons:", reasons)
print("dhw reasons  :", sorted({p.get("reason") for p in views["dhw_plan"]["forecast"]} - {None}))
# `scheduled` joined the list in v5.1.7: it is the neutral fall-through, so a
# plan made entirely of ordinary slots carries nothing else — leaving it out
# would have this check call a perfectly labelled plan unrecognisable.
if not any(
    r in reasons
    for r in ("cheap_price", "comfort_floor", "preheat_weather", "scheduled")
):
    issues.append("space plan produced no recognisable reason codes")

# cross-check totals against the raw schedule: the slot summaries the card
# shows must account for the same energy the optimizer scheduled.
sp = np.asarray(r.power_schedule).sum()*DT
dw = np.asarray(r.dhw_power_schedule).sum()*DT
print("raw space kWh", round(sp,2), "raw dhw kWh", round(dw,2))
slot_e = sum(s["energy_kwh"] for s in views["space_plan"]["slots"])
print("slot-sum space kWh", round(slot_e,2))
slot_d = sum(s["energy_kwh"] for s in views["dhw_plan"]["slots"])
print("slot-sum dhw kWh", round(slot_d,2))
if abs(slot_e - sp) > 0.01:
    issues.append(f"space slot energy {slot_e:.3f} kWh != schedule {sp:.3f} kWh")
if abs(slot_d - dw) > 0.01:
    issues.append(f"dhw slot energy {slot_d:.3f} kWh != schedule {dw:.3f} kWh")

# The rendered-plan payload for card.mjs. The path is shared via HPO_PLANDATA,
# defaulting to a name derived from this checkout's tests/ directory so a run
# here can never satisfy (or be satisfied by) a stale file another checkout
# wrote. card.mjs derives the identical default.
import hashlib
import pathlib
import tempfile
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_default = os.path.join(
    "/tmp", "plandata-%s.json" % hashlib.sha256(_tests_dir.encode()).hexdigest()[:12]
)
plandata_path = os.environ.get("HPO_PLANDATA", _default)
# The payload is scratch shared with card.mjs, and every documented path
# lives in the temp area (the default hardcodes /tmp, which is not always
# tempfile.gettempdir() on every platform, so both roots are allowed).
# Normalize, then confine: an override that escapes both roots -- via ..
# or an absolute path elsewhere -- is a mistake worth refusing, not writing.
_resolved = pathlib.Path(plandata_path).resolve()
_roots = [pathlib.Path(r).resolve() for r in ("/tmp", tempfile.gettempdir())]
if not any(_resolved.is_relative_to(r) for r in _roots):
    raise SystemExit(
        f"HPO_PLANDATA must live under a temp root ({', '.join(str(r) for r in _roots)}): {plandata_path}"
    )
_resolved.write_text(json.dumps(views))
print("wrote", _resolved)

if issues:
    print("PLAN VIEW ISSUES:")
    for i in issues:
        print("  -", i)
else:
    print("plan reason codes, price provenance and slot energy OK")

sys.exit(1 if issues else 0)
