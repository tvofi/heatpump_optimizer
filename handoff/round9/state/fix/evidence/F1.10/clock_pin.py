"""#1741 agreement pin, standalone: the coordinator's horizon bridge against
_Horizon.timestamps on both 2026 Stockholm transition days, at the 15-minute
step and at a 7.5-minute step (the control: not a whole number of minutes)."""
import sys
sys.path.insert(0, "custom_components")
from datetime import datetime
from zoneinfo import ZoneInfo
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C
from heatpump_optimizer.optimizer import _Horizon
tz = ZoneInfo("Europe/Stockholm")
bad = 0
for label, day in (("spring", datetime(2026, 3, 29, tzinfo=tz)), ("autumn", datetime(2026, 10, 25, tzinfo=tz))):
    for dt in (0.25, 0.125):
        fake = type("_C", (), {"_opt_config": type("_O", (), {"dt_hours": dt})()})()
        a = C._horizon_step_starts(fake, day, 96)
        b = list(_Horizon.timestamps.fget(type("_H", (), {"start_time": day, "n_steps": 96, "dt": dt})()))
        n = sum(x != y for x, y in zip(a, b))
        bad += n
        print(f"ROW {label} dt_hours={dt} disagreeing_steps={n} of {len(a)}")
print(f"RESULT clock_disagreements={bad}")
