"""D2-s2 / D2.M3 -- the terminal cost against a re-simulated continuation.

Metric (one line): ratio = T(E) / C(E), where T(E) is the objective's own terminal-cost closure
  (captured from HeatPumpOptimizer._terminal_cost) evaluated at the solved plan's end state E,
  and C(E) = refill_price * (sum of HeatPumpOptimizer._compute_baseline_power over a 24 h
  continuation from E  -  the same from E with every store raised to its settlement cap), the
  continuation run on the horizon's own weather and comfort targets, priced at the same
  25th-percentile refill price the terminal cost uses (x price_weight = 1). Sign: T and C must
  agree in sign; magnitude: ratio near 1.
  count key: the float the captured terminal closure returns (production seam).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/terminal_continuation.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT.
Perturbation (--perturb): refill price inside _terminal_cost doubled (config.price_weight=2 while
  the closure is built, price_weight=1 elsewhere) -> ratio doubles (direction: up).
Instrumented: optimizer:HeatPumpOptimizer._terminal_cost, optimizer:HeatPumpOptimizer._compute_baseline_power
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

SCEN = ["winter_single_no_dhw", "winter_two_zone_no_dhw", "shoulder", "flat_prices",
        "extreme_prices", "mild_windy_rain", "start_below_band"]
HPO = optmod.HeatPumpOptimizer
_orig_tc = HPO._terminal_cost
_orig_opt = HPO.optimize
cap = {}


def tc(self, prices, outdoor, solar=None, humidity=None):
    saved = self.config.price_weight
    if "--perturb" in sys.argv:
        self.config.price_weight = 2.0 * saved
    try:
        out = _orig_tc(self, prices, outdoor, solar, humidity)
    finally:
        self.config.price_weight = saved
    if "tc" not in cap:
        cap["tc"] = out[0]
        cap["caps"] = self._settlement_caps(outdoor, humidity=humidity)
        cap["p25"] = float(np.percentile(prices, 25))
    return out


def opt_wrap(self, *a, **k):
    res = _orig_opt(self, *a, **k)
    cap["res"] = res; cap["opt"] = self; cap["args"] = a
    return res


HPO._terminal_cost = tc
HPO.optimize = opt_wrap
t0 = time.process_time(); tt0 = time.thread_time()
rows = []
for name in SCEN:
    cap.clear()
    try:
        golden.capture(name, golden.SCENARIOS[name])
    except AssertionError:
        pass
    opt, res = cap["opt"], cap["res"]
    a = cap["args"]
    p = opt.model.params
    E = copy.deepcopy(a[0])
    E.room_temperature = res.room_temp_trajectory[-1]
    E.slab_temperature = res.slab_temp_trajectory[-1]
    E.upper_floor_temperature = res.upper_temp_trajectory[-1]
    E.lower_floor_temperature = res.lower_temp_trajectory[-1]
    if res.buffer_temp_trajectory:
        E.buffer_tank_temperature = res.buffer_temp_trajectory[-1]
    Tval = float(cap["tc"](np.asarray(res.room_temp_trajectory), np.asarray(res.slab_temp_trajectory),
                           np.asarray(res.upper_temp_trajectory), np.asarray(res.lower_temp_trajectory),
                           np.asarray(res.buffer_temp_trajectory) if res.buffer_temp_trajectory else None))
    caps = cap["caps"]
    C = copy.deepcopy(E)
    C.room_temperature = max(C.room_temperature, caps["room"])
    C.upper_floor_temperature = max(C.upper_floor_temperature, caps["room"])
    C.lower_floor_temperature = max(C.lower_floor_temperature, caps["room"])
    C.slab_temperature = max(C.slab_temperature, caps["slab"])
    outdoor = np.asarray(a[2], dtype=float); n = len(outdoor)
    wind = np.asarray(a[3] if a[3] is not None else np.zeros(n)); rain = np.asarray(a[4] if a[4] is not None else np.zeros(n))
    solar = np.asarray(a[5] if a[5] is not None else np.zeros(n))
    targets = np.full(n, opt.config.target_temp)
    dt = opt.config.dt_hours
    pe, _ = opt._compute_baseline_power(E, outdoor, wind, rain, solar, dt, targets)
    pc, _ = opt._compute_baseline_power(C, outdoor, wind, rain, solar, dt, targets)
    Cval = cap["p25"] * float(np.sum(pe - pc) * dt)
    ratio = Tval / Cval if abs(Cval) > 1e-9 else float("nan")
    rows.append((name, Tval, Cval, ratio))
    print(f"# {name:24s} T={Tval:8.4f} C={Cval:8.4f} ratio={ratio:.3f}  end room={E.room_temperature:.2f} slab={E.slab_temperature:.2f} caps room={caps['room']:.2f} slab={caps['slab']:.2f}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
live = [r for r in rows if np.isfinite(r[3]) and abs(r[2]) > 0.05]
rs = sorted(r[3] for r in live)
print(f"RESULT cells={len(live)} count")
print(f"RESULT sign_disagree={sum(1 for r in rows if r[1] * r[2] < -1e-12)} count")
print(f"RESULT ratio_min={rs[0]:.3f}")
print(f"RESULT ratio_max={rs[-1]:.3f}")
print(f"RESULT ratio_median={float(np.median(rs)):.3f}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
