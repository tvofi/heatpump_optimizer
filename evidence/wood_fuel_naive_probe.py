"""Reviewer's probe: wood_fuel.cheaper_windows on naive plan stamps under two host zones.
Run from the repo root: TZ=<zone> PYTHONPATH=tests/hastub:. python3 <this>."""
import sys
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from heatpump_optimizer.wood_fuel import cheaper_windows
ts = [datetime(2026, 1, 15, 20, 0) + timedelta(hours=i) for i in range(8)]
print(cheaper_windows(ts, [True] * 8, ZoneInfo("Europe/Stockholm"))[-1][1])
