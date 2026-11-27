import sys
sys.path[:0] = [sys.argv[1] + "/tests/hastub", sys.argv[1] + "/custom_components"]
from datetime import datetime
from zoneinfo import ZoneInfo
from heatpump_optimizer.dhw_schedule import hours_until_next_window
z = ZoneInfo("Europe/Stockholm")
for (h, m, f, win, want) in [
    (2, 50, 0, [(2.5, 2 + 40/60)], 40/60),          # second pass of 02:30 later
    (2, 50, 1, [(2.5, 2 + 40/60)], 24 - (2+50/60) + 2.5),  # passed both: tomorrow, plain day
    (2, 20, 0, [(2.5, 3.0)], 10/60),
    (1, 30, 0, [(2.5, 3.0)], 1.0),
    (3, 30, 0, [(2.5, 3.0)], 23.0),
]:
    now = datetime(2026, 10, 25, h, m, tzinfo=z, fold=f)
    r = hours_until_next_window(now, win)
    print(now.isoformat(), win, "->", round(r, 4), "want", round(want, 4), "OK" if abs(r - want) < 1e-6 else "OFF")
