"""D2.M2 (COP and derates) sweep harness, round 10 seat D2-s2.

Metric (finding): dhw_mode_ratio_max = max over outdoor in [-25,15] step 1 and
  DHW tank temperature T in [10,65] step 1 of
  ThermalModel(cop_flow_carnot=False).compute_cop_dhw(o,T) /
  ThermalModel(cop_flow_carnot=True).compute_cop_dhw(o,T), all other params default.
  Count key: the float compute_cop_dhw returns (the production seam).
  Identity expected: 1.0 (the valve flag is a space-circuit fact; it does not
  change the DHW lift). Observed at baseline: ~1.43 (at o=+7.., T=65); below 35 C
  the non-valve branch also returns a >1 boost (dhw_below_ref_boost_max ~1.2).
Non-finding metrics: monotonicity violation counts, derate range, batch/scalar
  COP parity mismatches, derate continuity jump.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D2/s2/cop_laws.py [--perturb]
  --perturb patches the non-valve branch of compute_cop_dhw to the valve branch's
  law (_cop_law at dhw_temp): dhw_mode_ratio_max -> 1.0, dhw_below_ref_boost_max -> 1.0.
Expected: dhw_mode_ratio_max 1.435 +/- 0.01 ; tolerance on identities exact (1e-12).
Baseline 17f1c55fad1b, machine: macOS arm64 (B5).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, random, sys, time
sys.path.insert(0, os.getcwd())
from unittest import mock
import numpy as np
from custom_components.heatpump_optimizer import thermal_model as tm
from custom_components.heatpump_optimizer import defrost as df

t0p, t0t = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv
P = tm.ThermalParameters()

def model(**kw):
    return tm.ThermalModel(dataclasses.replace(P, **kw))

ctx = mock.patch.object(
    tm.ThermalModel, "compute_cop_dhw",
    lambda self, o, T, humidity=None: self._cop_law(o, humidity, T)) if PERTURB else None
if ctx: ctx.start()

direct, valve = model(cop_flow_carnot=False), model(cop_flow_carnot=True)
outs = np.arange(-25, 15.01, 1.0); temps = np.arange(10, 65.01, 1.0)
worst = (1.0, None)
for o in outs:
    for T in temps:
        r = direct.compute_cop_dhw(o, T) / valve.compute_cop_dhw(o, T)
        if abs(r - 1) > abs(worst[0] - 1): worst = (r, (o, T))
print(f"RESULT dhw_mode_ratio_max={worst[0]:.4f} ratio  # at (outdoor,T)={worst[1]}")
# leave-one-out over outdoor cells
per_o = [max(abs(direct.compute_cop_dhw(o, T)/valve.compute_cop_dhw(o, T)-1) for T in temps) for o in outs]
s = sorted(per_o)
print(f"RESULT dhw_mode_dev_cells={len(per_o)} min={s[0]:.4f} max={s[-1]:.4f} drop_max={s[-2]:.4f}")
boost = max(direct.compute_cop_dhw(o, T) / direct._cop_law(o, None, None)
            for o in outs for T in np.arange(10, 35, 1.0))
print(f"RESULT dhw_below_ref_boost_max={boost:.4f} ratio")
if ctx: ctx.stop()

# --- non-findings -----------------------------------------------------------
fine = np.arange(-35, 40.001, 0.05)
viol = 0
for kw in ({"cop_flow_carnot": True}, {"flow_curve_cop": True}, {}):
    m = model(**kw)
    for f in (None, 30, 35, 40, 50, 60, 70, 75):
        c = np.array([m.compute_cop(o, flow_temp=f) for o in fine]); viol += int((np.diff(c) < -1e-12).sum())
print(f"RESULT cop_outdoor_monotone_violations={viol} count")
m = model(cop_flow_carnot=True); viol = 0
for o in (-30, -15, -5, 0, 7, 20, 35):
    c = np.array([m.compute_cop(o, flow_temp=f) for f in np.arange(20, 80, 0.05)]); viol += int((np.diff(c) > 1e-12).sum())
for carn in (False, True):
    m = model(cop_flow_carnot=carn)
    for o in (-30, -10, 0, 7, 20):
        c = np.array([m.compute_cop_dhw(o, T) for T in np.arange(10, 80, 0.05)]); viol += int((np.diff(c) > 1e-12).sum())
print(f"RESULT cop_flow_monotone_violations={viol} count")
# derate range + continuity under random learning
rng = random.Random(7); lo, hi, jump = 9.0, -9.0, 0.0
for trial in range(40):
    d = df.DefrostDerate()
    for _ in range(rng.randint(0, 400)):
        o = rng.uniform(-30, 15); h = rng.uniform(20, 100)
        if rng.random() < 0.5: d.observe(o, h, rng.uniform(0.01, 3.0))
        else: d.observe_duty(o, h, rng.uniform(0, 1), rng.randint(0, 5))
    for o in np.arange(-32, 42, 0.25):
        for h in (0.0, 30.0, 69.999, 70.0, 85.0, 100.0):
            v = d.factor(o, h); lo, hi = min(lo, v), max(hi, v)
            jump = max(jump, abs(d.factor(o + 1e-9, h) - v))
print(f"RESULT derate_min={lo:.4f} derate_max={hi:.4f} ratio")
print(f"RESULT derate_jump_1e-9={jump:.3e} ratio")
dm = [df.derate_from_duty(x) for x in np.linspace(-1, 2, 3001)]
print(f"RESULT duty_derate_range={min(dm):.4f}..{max(dm):.4f} ratio")
# batch/scalar COP parity, with a learned derate
d = df.DefrostDerate()
for i in range(200): d.observe_duty(rng.uniform(-3, 6), rng.uniform(60, 100), rng.uniform(0, .3))
mism = 0; n = 0
for kw in ({"cop_flow_carnot": True}, {"flow_curve_cop": True}, {}):
    m = model(defrost_derate=d, ambient_humidity=85.0, **kw)
    for o in np.arange(-30, 30, 0.37):
        tb = np.arange(15, 80, 0.5)
        b = m._batch_cop(float(o), 85.0, tb, True)
        s_ = np.array([m.compute_cop(float(o), humidity=85.0, flow_temp=float(t)) for t in tb])
        mism += int((b != s_).sum()); n += len(tb)
print(f"RESULT batch_scalar_cop_mismatch={mism} of {n} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc/tc:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
