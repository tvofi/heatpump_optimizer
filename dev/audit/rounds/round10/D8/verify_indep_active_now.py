# Own metric: over a 0.001 kW grid of space draws in [0,0.3], dhw=0, count draws where
# the plan view's active_now predicate (raw>0.05, coordinator.py:4161) is True and the
# plan's own running rule thermal_model.planned_draws_run is False.
import sys; sys.path.insert(0,'custom_components')
from heatpump_optimizer import thermal_model as T
grid=[i/1000 for i in range(301)]
bad=[x for x in grid if (x>0.05) and not T.planned_draws_run([x],[0.0])[0]]
print("disagree",len(bad),"of",len(grid),"range",min(bad),max(bad))
