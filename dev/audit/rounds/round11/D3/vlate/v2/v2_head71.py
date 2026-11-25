import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from datetime import datetime, timezone
from mutload import load
OLD = "if not np.all(np.isfinite(values)) or float(np.mean(values)) <= 1e-6:"
b, m = load("price_model", 163, OLD, OLD.replace("<= 1e-6", "< 1e-6"))
day = np.zeros(96); day[:4] = 24e-6
hday = np.zeros(24); hday[0] = 24e-6
def acc(mod, meth, vals):
    pm = mod.PriceShapeModel()
    return int(bool(getattr(pm, meth)(datetime(2026, 3, 4, tzinfo=timezone.utc), list(vals))))
print(f"RESULT head71_quarters base={acc(b,'observe_day_quarters',day)} mut={acc(m,'observe_day_quarters',day)}")
print(f"RESULT head71_hourly(observe_day, sibling now sharing _usable_day) base={acc(b,'observe_day',hday)} mut={acc(m,'observe_day',hday)}")
