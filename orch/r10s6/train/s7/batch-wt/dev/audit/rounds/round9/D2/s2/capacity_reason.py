"""D2-s2 / D2.M2 -- a capacity ceiling below demand-at-derate carries no reason code.

Metric (one line): short_unlabelled = count of plan steps where the per-step electrical ceiling
  (power_caps_extra: the fuse / learned-envelope / silent-mode channel) times the step's
  ThermalModel.compute_cop is below the steady demand to hold the comfort MINIMUM at that
  step's outdoor temperature (U_eff*(min_temp - out) - internal_gains), and the published
  space_reasons entry for the step says nothing about capacity (no reason code names it:
  the codes are the optimizer.REASON_* set). Swept over golden `make` houses (1-zone, 2-zone)
  x weather {winter_cold, winter_mild, shoulder} x cap fraction {0.6 (the envelope floor),
  0.8} of nameplate. Also: floor_breach_capped = steps where the room ends below min_temp and
  the pump sits at its ceiling.
  count key: OptimizationResult.space_reasons at each step (production seam).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/capacity_reason.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT.
Perturbation (--perturb): power_caps_extra=None in every cell (the ceiling removed) ->
  short_unlabelled falls to 0 (direction: to_zero). Null control: cap fraction 1.0.
Instrumented: optimizer:HeatPumpOptimizer.optimize (space_reasons, power_caps_extra),
  optimizer:classify_space_steps, thermal_model:ThermalModel.compute_cop
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import collections
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

PERTURB = "--perturb" in sys.argv
codes = sorted(v for k, v in vars(optmod).items() if k.startswith("REASON_") and isinstance(v, str))
cap_codes = [c for c in codes if "cap" in c or "fuse" in c or "limit" in c or "envelope" in c]
t0 = time.process_time(); tt0 = time.thread_time()
cells = []
reason_hist = collections.Counter()
for two_zone in (False, True):
    for wx in ("winter_cold", "winter_mild", "shoulder"):
        for frac in (0.6, 0.8, 1.0):
            b = golden.make(two_zone=two_zone, dhw=False, weather_profile=wx)
            opt = b["optimizer"]; m = opt.model; p = m.params
            n = len(b["prices"])
            caps = np.full(n, p.max_electrical_power * frac)
            res = opt.optimize(b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"],
                               b["solar"], golden.START,
                               power_caps_extra=None if PERTURB else caps)
            tmin = opt.config.min_temp
            room = np.asarray(res.upper_temp_trajectory if two_zone else res.room_temp_trajectory)
            P = np.asarray(res.power_schedule)
            short = 0; breach = 0
            for i in range(n):
                out = float(b["outdoor"][i])
                if two_zone:
                    u = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss, b["wind"][i], b["rain"][i]) + \
                        m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned, b["wind"][i] * 0.5, b["rain"][i] * 0.5)
                else:
                    u = m.effective_heat_loss_coefficient(p.heat_loss_coefficient, b["wind"][i], b["rain"][i])
                demand = u * (tmin - out) - p.internal_gains
                cap_i = p.max_electrical_power * (1.0 if PERTURB else frac)
                if cap_i * m.compute_cop(out) < demand and res.space_reasons[i] not in cap_codes:
                    short += 1
                    reason_hist[res.space_reasons[i]] += 1
                if room[i + 1] < tmin - 0.05 and P[i] >= cap_i - 1e-3 and res.space_reasons[i] not in cap_codes:
                    breach += 1
            cells.append((two_zone, wx, frac, short, breach, n))
            print(f"# two_zone={two_zone!s:5s} wx={wx:12s} cap={frac:.1f} short_unlabelled={short:3d} floor_breach_capped={breach:3d} of {n}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
live = [c for c in cells if c[2] < 1.0]
null = [c for c in cells if c[2] == 1.0]
print(f"# reason codes in production: {codes}; capacity codes: {cap_codes}")
print(f"# reasons carried by capacity-short steps: {dict(reason_hist)}")
print(f"RESULT cells={len(live)} count")
print(f"RESULT short_unlabelled={sum(c[3] for c in live)} count")
print(f"RESULT short_unlabelled_max_cell={max(c[3] for c in live)} count")
print(f"RESULT short_unlabelled_drop_worst={sum(c[3] for c in live) - max(c[3] for c in live)} count")
print(f"RESULT floor_breach_capped={sum(c[4] for c in live)} count")
print(f"RESULT null_short_unlabelled={sum(c[3] for c in null)} count")
print(f"RESULT capacity_reason_codes={len(cap_codes)} count")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
