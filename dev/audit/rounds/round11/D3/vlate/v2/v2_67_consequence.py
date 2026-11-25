"""VD3L V2 D3-s1-67 consequence: windows_for_day (dhw_schedule.py, the one resolution seam) with
holiday=True and the value the parser returns for an unset holiday-windows option: baseline None,
mutant []. Metric: number of DHW windows in force on a holiday day. Null: holiday=False (the overlay
is not consulted, so both arms must agree)."""
import sys
sys.path.insert(0, "custom_components")
from heatpump_optimizer.dhw_schedule import windows_for_day
from heatpump_optimizer.dhw_schedule import parse_windows
fb = parse_windows("06:00-08:00, 18:00-21:00")
b = windows_for_day(None, 2, fb, holiday_windows=None, holiday=True)
m = windows_for_day(None, 2, fb, holiday_windows=[], holiday=True)
nb = windows_for_day(None, 2, fb, holiday_windows=None, holiday=False)
nm = windows_for_day(None, 2, fb, holiday_windows=[], holiday=False)
print(f"RESULT 67_holiday_windows_in_force base={len(b)} mut={len(m)}")
print(f"RESULT 67_null_not_holiday base={len(nb)} mut={len(nm)} delta={len(nb)-len(nm)}")
