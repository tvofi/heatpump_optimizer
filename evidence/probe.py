from datetime import datetime, timedelta, timezone
from heatpump_optimizer.drift import Cusum
from heatpump_optimizer.const import VENT_CUSUM_THRESHOLD_C, VENT_CUSUM_DRIFT_C, VENT_CUSUM_CLIP_C, VENT_CUSUM_REFERENCE_HOURS
T = datetime(2026, 1, 15, 7, tzinfo=timezone.utc)
def run(res, regs, step):
    d = Cusum(threshold=VENT_CUSUM_THRESHOLD_C, drift=VENT_CUSUM_DRIFT_C, side=-1, clip=VENT_CUSUM_CLIP_C, reference_hours=VENT_CUSUM_REFERENCE_HOURS)
    t = []
    for i, (r, u) in enumerate(zip(res, regs)):
        d.update(T + timedelta(minutes=step * i), r, u); t.append(d.tripped)
    return t, d.tripped
def perday(t, n): return [sum(t[i*n:(i+1)*n]) for i in range(len(t)//n)]
for b in (0.4, 0.7, 1.0):
    q = [600 if i % 48 < 20 else 0 for i in range(192)]
    res = [-b * x / 600 for x in q]
    for name, regs in (("head", [(1.0, x*0.5/1000) for x in q]), ("sun0", [(1.0, 0.0) for x in q]), ("heat0", [(0.0, x*0.5/1000) for x in q])):
        t, e = run(res, regs, 30); print(f"RESULT check-schedule b={b} {name} perday={perday(t,48)}")
for shape in ("steady", "heat", "sun"):
    for b in (0.1, 0.4, 1.0):
        x = [1.5 if (i // 16) % 2 == 0 else 0 for i in range(384)]
        q = [0.15 if i % 96 < 40 else 0 for i in range(384)]
        res = {"steady": [-b]*384, "heat": [-b*a/1.5 for a in x], "sun": [-b*s/0.15 for s in q]}[shape]
        t, e = run(res, list(zip(x, q)), 15); print(f"RESULT census {shape} b={b} tripped={sum(t)} end={e}")
