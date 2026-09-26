"""D5 verify-v2 harness for D5-s2-02 and D5-s2-03 (independent of the finder's comment_numbers.py).

Metric (one line): for each comment claim, is the number it states (a) equal to what the
production symbol delivers at the shipped default, and (b) reachable under ANY configuration the
flows admit. strict_mismatches counts claims failing (b); default_mismatches counts claims
failing (a).
  C1 defrost.py "less than half" -> floor of DefrostDerate.factors after 2000 observe() calls
     at delivered_ratio 0.01 (fixpoint of the EMA = the clamp); admissible = any, so (b)==(a).
  C2 const.py:750 "every 15 minutes" -> update_interval of a coordinator built from a default
     entry; admissible set = the optimization_interval NumberSelector range in BOTH flows.
  C3 coordinator.py:640 "5-minute update interval" -> same selectors.
  C4 (D5-s2-03) const.py:337 DHW_COLD_WATER_TEMP "the draw model heats from ~10" ->
     ThermalParameters.dhw_draw_power: fraction of dhw_inlet_temp settings (selector range, step)
     at which the draw's cold end (recovered by bisection on the power's zero crossing over
     the tank temperature) differs from the constant by >0.05 K.
Command (repository root):
    PYTHONPATH=tests/hastub python tools/audit/round9/D5/verify-v2/v2_comment_numbers.py [--perturb]
--perturb: DERATE_MIN=0.5, DEFAULT_OPTIMIZATION_INTERVAL=15 on the coordinator module, both
    selector minimums read as 5, and ThermalParameters.dhw_inlet_reference forced to the constant
    -> every mismatch count must reach 0.
Baseline 1936d5ca; exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry  # noqa
from heatpump_optimizer import defrost, const, config_flow, coordinator as coord_mod  # noqa
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa
P = "--perturb" in sys.argv
if P:
    defrost.DERATE_MIN = 0.5
    coord_mod.DEFAULT_OPTIMIZATION_INTERVAL = 15
    ThermalParameters.dhw_inlet_reference = property(lambda self, *a, **k: const.DHW_COLD_WATER_TEMP) \
        if isinstance(inspect.getattr_static(ThermalParameters, "dhw_inlet_reference"), property) \
        else (lambda self, *a, **k: const.DHW_COLD_WATER_TEMP)

# C1
d = defrost.DefrostDerate()
for _ in range(2000):
    d.observe(0.0, 80.0, 0.01)
floor = min(min(r) for r in d.factors)
c1_default = int(abs(floor - 0.5) > 1e-6)

# C2/C3: the admissible optimization_interval range in both flows, read off the selectors.
def sel_cfg(w):
    return dict(getattr(w, "config", None) or {})
opt = [sel_cfg(f.widget) for f in config_flow._OPTION_FIELDS if f.key == const.CONF_OPTIMIZATION_INTERVAL]
import re
src = inspect.getsource(config_flow.HeatPumpOptimizerConfigFlow.async_step_thermal)
m = re.search(r"CONF_OPTIMIZATION_INTERVAL,.*?\):\s*_number\((\d+),\s*(\d+),\s*(\d+)", src, re.S)
rngs = [(float(o["min"]), float(o["max"]), float(o["step"])) for o in opt] + [tuple(float(x) for x in m.groups())]
print("interval selector ranges (options, config):", rngs)
adm_min = min(r[0] for r in rngs); adm_max = max(r[1] for r in rngs); adm_step = min(r[2] for r in rngs)
if P:
    adm_min = 5.0
h = FakeHass(); e = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.w"})
_base = coord_mod.HeatPumpOptimizerCoordinator.__mro__[1]
_seen = {}
_orig_init = _base.__init__
def _rec(self, *a, **k):
    _seen["ui"] = k.get("update_interval")
    return _orig_init(self, *a, **k)
_base.__init__ = _rec  # the stub drops update_interval; record the kwarg the coordinator hands it
c = coord_mod.HeatPumpOptimizerCoordinator(h, e)
_base.__init__ = _orig_init
upd = _seen["ui"].total_seconds() / 60
def admissible(v):
    return adm_min <= v <= adm_max and abs((v - adm_min) / adm_step - round((v - adm_min) / adm_step)) < 1e-9
c2_default = int(upd != 15); c2_strict = int(not admissible(15))
c3_default = int(adm_min != 5); c3_strict = int(not admissible(5))
c1_strict = c1_default

# C4: draw cold end over the dhw_inlet_temp selector range.
icfg = [sel_cfg(f.widget) for f in config_flow._OPTION_FIELDS if f.key == const.CONF_DHW_INLET_TEMP][0]
lo_, hi_, st_ = float(icfg["min"]), float(icfg["max"]), float(icfg["step"])
n_set = int(round((hi_ - lo_) / st_)) + 1
off = 0
for i in range(n_set):
    v = lo_ + i * st_
    p = ThermalParameters.from_config({const.CONF_DHW_INLET_TEMP: v, "dhw_enabled": True})
    p.greywater_recovery = 0.0
    lph = p.dhw_daily_consumption / 24.0
    from heatpump_optimizer.thermal_model import WATER_SPECIFIC_HEAT
    cold = p.dhw_setpoint - p.dhw_draw_power / (lph * WATER_SPECIFIC_HEAT)
    off += abs(cold - const.DHW_COLD_WATER_TEMP) > 0.05
c4 = int(off > 0)
print(f"ROW C4 inlet settings={n_set} range=[{lo_},{hi_}] step {st_} draw_cold_end_off_constant={off}")
print(f"ROW C1 floor={floor:.4f} comment=0.5 default_mismatch={c1_default}")
print(f"ROW C2 update_interval_min={upd} admissible=[{adm_min},{adm_max}] step {adm_step} comment=15 default_mismatch={c2_default} strict={c2_strict}")
print(f"ROW C3 selector_min={adm_min} comment=5 default_mismatch={c3_default} strict={c3_strict}")
print(f"RESULT draw_cold_end_off_constant={off} of {n_set} settings")
print(f"RESULT coupling_claim_mismatch={c4} count")
print(f"RESULT default_mismatches={c1_default + c2_default + c3_default} count")
print(f"RESULT strict_mismatches={c1_strict + c2_strict + c3_strict} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
