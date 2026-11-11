"""Reviewer's probe 2: one weekday-night ask, asked at 09:00 on each day of a week, weekend comfort configured; null: no weekend comfort."""
import sys
from datetime import datetime, timedelta
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
sys.argv = sys.argv[:1]
exec(open(sys.argv[0].replace("probe2.py", "probe.py")).read().split("SCHED = [")[0])
for label, over in (("weekend comfort set", dict(comfort_temp_day_weekend=22.0, comfort_temp_night_weekend=20.0)), ("null: no weekend comfort", {})):
    opt, params = mk(False, False, **over)
    for name, ov in (("night-1", {"comfort_temp_night": 18.5}), ("day+1", {"comfort_temp_day": 22.0})):
        figs = []
        for d in range(7):
            i = inp(int(9 / DT), st(), start=datetime(2026, 1, 5) + timedelta(days=d))
            days = whatif.schedule_days((shadow(opt, params, {}), i), (shadow(opt, params, ov), i))
            figs.append("pair" if days is None else f"{price_tiles.schedule_figure(*days, float(np.mean(i.forecast.prices)), 0.0, 24.0)[whatif.STEADY_KEY]:+.1f}")
        print(f"RESULT probe weekday {label}: {name} asked 09:00 Mon..Sun (same prices and weather every day): {' '.join(figs)}")
