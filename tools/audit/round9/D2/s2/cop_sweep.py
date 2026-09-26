"""D2-s2 / D2.M2 -- COP and derate sanity, swept.

Metrics (one line each):
  mono_outdoor_viol  = count of adjacent pairs (0.05 K apart, -30..40 C) where
                       ThermalModel.compute_cop falls as outdoor rises, per config arm, with
                       no defrost derate learned (the smooth curve must be non-decreasing)
  mono_flow_viol     = count of adjacent pairs (0.25 K apart, 20..80 C) where
                       ThermalModel.compute_cop (cop_flow_carnot on) rises as flow rises
  dhw_mono_viol      = same for compute_cop_dhw in dhw_temp (both branches)
  cross_mode_viol    = count of (outdoor, T) cells, flow_curve_cop on (direct plant), where
                       compute_cop_dhw(outdoor, T) > compute_cop(outdoor) although T >= the
                       curve flow the space COP is priced at (hotter water priced cheaper)
  derate_out_of_band = count of DefrostDerate.factor samples outside [DERATE_MIN, 1]
  derate_max_jump    = max |factor(x+1e-7) - factor(x)| over a random learned table (continuity)
  count key: the float compute_cop / compute_cop_dhw / factor return (production seam).

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/cop_sweep.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT; exact counts (deterministic, seed 9).
Perturbation (--perturb): in memory, ThermalModel.compute_cop_dhw's non-valve branch is made to
  price the tank through _cop_law(outdoor, humidity, dhw_temp) (the Carnot law the space path
  uses) -> cross_mode_viol must fall to 0.
Instrumented: thermal_model:ThermalModel.compute_cop, thermal_model:ThermalModel.compute_cop_dhw,
  defrost:DefrostDerate.factor
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import house  # noqa: E402
from heatpump_optimizer import defrost  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    def _dhw_carnot(self, outdoor_temp, dhw_temp, humidity=None):
        return self._cop_law(outdoor_temp, humidity, dhw_temp)
    ThermalModel.compute_cop_dhw = _dhw_carnot

t0 = time.process_time(); tt0 = time.thread_time()


def model(two_zone, **over):
    cfg = house(two_zone=two_zone, dhw=True)
    p = ThermalParameters.from_config(cfg)
    for k, v in over.items():
        setattr(p, k, v)
    return ThermalModel(p)


outs = np.round(np.arange(-30.0, 40.0001, 0.05), 6)
res = {}
# --- 1. monotone in outdoor, per arm ------------------------------------------
arms = {
    "plain_1z": model(False),
    "plain_2z": model(True),
    "curve_cop_2z": model(True, flow_curve_cop=True),
    "curve_cop_2z_bias5": model(True, flow_curve_cop=True, flow_curve_bias=5.0),
    "curve_cop_1z": model(False, flow_curve_cop=True),
    "cop_scale_0.8": model(True, cop_scale=0.8),
}
mono = 0
for name, m in arms.items():
    c = np.array([m.compute_cop(float(o)) for o in outs])
    v = int(np.sum(np.diff(c) < -1e-12))
    mono += v
    print(f"# outdoor-monotone arm={name:20s} viol={v} min={c.min():.3f} max={c.max():.3f}")
# valve arm: carnot at fixed flow, outdoor sweep
mv = model(True, cop_flow_carnot=True)
for flow in (35.0, 45.0, 55.0, 65.0, 75.0):
    c = np.array([mv.compute_cop(float(o), flow_temp=flow) for o in outs])
    v = int(np.sum(np.diff(c) < -1e-12))
    mono += v
    print(f"# outdoor-monotone arm=carnot_flow{flow:.0f}      viol={v}")
res["mono_outdoor_viol"] = mono
# --- 2. monotone in flow ------------------------------------------------------
flows = np.arange(20.0, 80.0001, 0.25)
fv = 0
for o in np.arange(-30.0, 40.1, 2.5):
    c = np.array([mv.compute_cop(float(o), flow_temp=float(f)) for f in flows])
    fv += int(np.sum(np.diff(c) > 1e-12))
res["mono_flow_viol"] = fv
# --- 3. DHW monotone in tank temp, both branches ------------------------------
dv = 0
temps = np.arange(20.0, 75.0001, 0.25)
for m in (model(True), mv, arms["curve_cop_2z"]):
    for o in np.arange(-30.0, 40.1, 2.5):
        c = np.array([m.compute_cop_dhw(float(o), float(t)) for t in temps])
        dv += int(np.sum(np.diff(c) > 1e-12))
res["dhw_mono_viol"] = dv
# --- 4. cross-mode: same (or hotter) water priced cheaper as hot water --------
cross = 0; cells = 0; worst = (0.0, None)
for name in ("curve_cop_2z", "curve_cop_2z_bias5", "curve_cop_1z"):
    m = arms[name]
    for o in np.arange(-30.0, 15.01, 0.5):
        f = m.curve_flow_temp(float(o))
        if f is None:
            continue
        space = m.compute_cop(float(o))
        for t in np.arange(max(35.0, np.ceil(f)), 65.01, 0.5):
            if t < f:
                continue
            cells += 1
            d = m.compute_cop_dhw(float(o), float(t))
            if d > space + 1e-9:
                cross += 1
                r = d / space
                if r > worst[0]:
                    worst = (r, (name, float(o), round(f, 2), float(t), round(space, 4), round(d, 4)))
res["cross_mode_cells"] = cells
res["cross_mode_viol"] = cross
res["cross_mode_worst_ratio"] = round(worst[0], 4)
print(f"# cross-mode worst (arm, outdoor, curve_flow, dhw_temp, space_cop, dhw_cop) = {worst[1]}")
# --- 5. derate bounds and continuity -----------------------------------------
rng = np.random.default_rng(9)
dd = defrost.DefrostDerate()
for t in range(len(defrost.TEMP_EDGES) - 1):
    for h in range(len(defrost.HUMIDITY_EDGES) - 1):
        dd.factors[t][h] = float(rng.uniform(defrost.DERATE_MIN, 1.0))
        dd.counts[t][h] = int(rng.integers(0, 30))
        dd.duty[t][h] = float(rng.uniform(0, 0.3))
        dd.duty_counts[t][h] = int(rng.integers(0, 30))
oob = 0; jump = 0.0
for o in np.arange(-35.0, 45.0, 0.037):
    for hh in (None, 0.0, 30.0, 69.99, 70.0, 85.0, 100.0, 101.0):
        a = dd.factor(float(o), hh)
        b = dd.factor(float(o) + 1e-7, hh)
        if not (defrost.DERATE_MIN - 1e-12 <= a <= 1.0 + 1e-12):
            oob += 1
        jump = max(jump, abs(a - b))
for hh in np.arange(0.0, 101.0, 0.37):
    for o in (-10.0, 0.0, 2.0, 5.0, 8.0):
        jump = max(jump, abs(dd.factor(o, float(hh)) - dd.factor(o, float(hh) + 1e-7)))
res["derate_out_of_band"] = oob
res["derate_max_jump"] = f"{jump:.3e}"
# derate_from_duty bounds
res["duty_derate_min"] = min(defrost.derate_from_duty(d) for d in np.linspace(-1, 2, 301))
res["duty_derate_max"] = max(defrost.derate_from_duty(d) for d in np.linspace(-1, 2, 301))
# flow_lift_factor in (0,1]
lf = [arms["curve_cop_2z"].flow_lift_factor(float(o), float(f)) for o in outs[::20] for f in flows[::8]]
res["flow_lift_min"] = round(min(lf), 4); res["flow_lift_max"] = round(max(lf), 4)
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
for k, v in res.items():
    print(f"RESULT {k}={v}")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
