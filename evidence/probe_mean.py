import sys, numpy as np
sys.path.insert(0, ".")
import rca as h
from heatpump_optimizer.thermal_model import ThermalState
for name in ("valve-at-curve","valve-charged","wood-warm","wood-hot"):
    kw, buf, wood = h.CELLS[name]
    for wv in ([wood, 5.0] if wood is not None else [None]):
        opt,_ = h._optimizer(h.house(**kw))
        plan = opt.optimize(inputs=h.solve_inputs(initial_state=ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=0.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0, dhw_temperature=52.0, dhw_hours_since_legionella=20.0, buffer_tank_temperature=buf, wood_tank_temperature=wv), prices=h.prices("flat", h.T0), outdoor_temps=np.full(96,0.0), wind_speeds=np.full(96,2.0), precipitation=np.zeros(96), solar_radiation=np.zeros(96), start_time=h.T0))
        b = float(opt.get_current_action(plan, h.T0)["baseline_kw"]); m=float(np.mean(plan.baseline_power_schedule))
        print(f"PROBE {name} wood={wv}: booked {b:.3f} mean {m:.3f}")
