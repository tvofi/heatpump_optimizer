import sys
from datetime import datetime, timedelta, timezone
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C
from heatpump_optimizer.optimizer import channel_heating_steps
t=[datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=15*i) for i in range(4)]
p=[0.0,0.07,0.07,0.0]
print("RESULT slots_for_0.07kW_steps=%d" % len(C._plan_slots(t,p,[1.0]*4,0.25)))
print("RESULT channel_heating_steps=%s" % channel_heating_steps(p,[0.0]*4))
