"""D7.M4 -- buffer-terminal statefulness (last_buffer_trajectory's successor).

At 17f1c55 no symbol last_buffer_trajectory exists; the terminal cost's only
per-solve state is optimizer:HeatPumpOptimizer._initial_buffer_temp, written by
_stash_price_horizon and read by _settlement_caps when _terminal_cost is BUILT.
Metric: |terminal cost of one fixed trajectory| differences, in objective units:
  (a) second_call_delta: closure called, another objective/terminal call in
      between, called again -> must be 0 (closure is pure in its arguments);
  (b) rebuilt_after_restash_delta: closure rebuilt after a different solve's
      _stash_price_horizon(buffer 65 C vs 40 C) -> the state dependency.
Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/terminal_state.py [--perturb]
--perturb pins _initial_buffer_temp to None in _settlement_caps' read (attribute
swap after stash): (b) must fall to 0.  Expected (a)=0 exact, (b)>0.
Baseline 17f1c55fad1b; machine B5. Root rule: cwd.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "custom_components")
t0p, t0t = time.process_time(), time.thread_time()
import numpy as np
from heatpump_optimizer.thermal_model import ThermalParameters, ThermalModel, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
PERTURB = "--perturb" in sys.argv
p = ThermalParameters(two_zone_enabled=True, buffer_tank_volume=750.0, mixing_valve_mode="manual", buffer_max_temp=70.0, max_electrical_power=3.0)
cfg = OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0)
opt = HeatPumpOptimizer(ThermalModel(p), cfg)
n = 96; prices = np.full(n, 1.0); out = np.full(n, -15.0); flat = lambda v: np.full(n+1, v)  # cold + 3 kW: charge ceiling 35 C, below buffer_max_temp
traj = (flat(21.0), flat(25.0), flat(21.0), flat(20.5), flat(30.0))
def stash(buf):
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=20.5,
                      slab_temperature=25.0, buffer_tank_temperature=buf, outdoor_temperature=-5.0)
    opt._stash_price_horizon(st, n, np.ones(n, bool), None, prices, np.zeros(n))
    if PERTURB: opt._initial_buffer_temp = None
stash(65.0); term, _ = opt._terminal_cost(prices, out)
c1 = term(*traj)
other = term(flat(19.0), flat(22.0), flat(19.0), flat(19.0), flat(60.0))  # an interleaved call
c2 = term(*traj)
stash(40.0); term2, _ = opt._terminal_cost(prices, out)
c3 = term2(*traj)
print(f"RESULT second_call_delta={abs(c2-c1):.6g} cost_units")
print(f"RESULT rebuilt_after_restash_delta={abs(c3-c1):.6g} cost_units  (c65={c1:.4f} c40={c3:.4f})")
tf = (time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9)
print(f"RESULT thread_factor={tf:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=0")
