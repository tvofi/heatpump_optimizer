import sys

sys.path.insert(
    0, "/tmp/claude-0/-home-user/67fb38f0-9f88-5c6b-9d2e-78b6cb07f57d/scratchpad"
)
import numpy as np
from _common import (
    S,
    FOLD_LAST,
    FOLD_NOW,
    F60_LAST,
    F60_NOW,
    SP_LAST,
    SP_NOW,
    true_s,
    show,
    datetime,
)
from heatpump_optimizer.drift import Cusum
from heatpump_optimizer.comfort_learning import ComfortLearner
from heatpump_optimizer.external_heat import ExternalHeatDetector, ExternalHeatConfig
from heatpump_optimizer import sysid

# --- drift.py:129  release_if_starved(now, max_gap_hours)
for lbl, (a, b, gap_h) in {
    "fold true 1h/wall 0 (window 1h: should release)": (FOLD_LAST, FOLD_NOW, 1.0),
    "spring true 2min/wall 62min (window 1h: should NOT release)": (
        SP_LAST,
        SP_NOW,
        1.0,
    ),
}.items():
    c = Cusum(threshold=3.0, drift=0.5)
    c.tripped = True
    c.stat = 5.0
    c.last_fed = a
    show(
        f"drift.py:129 release_if_starved [{lbl}]",
        c.release_if_starved(b, gap_h),
        true_s(b, a) >= gap_h * 3600,
    )

# --- comfort_learning.py:102 _decay
cases = {
    "fold true 1h/wall 0": (FOLD_LAST, FOLD_NOW),
    "fold true 60s/wall -3540s": (F60_LAST, F60_NOW),
    "spring true 2min/wall 62min": (SP_LAST, SP_NOW),
}
for lbl, (a, b) in cases.items():
    cl = ComfortLearner()
    cl.evidence = 4.0
    cl.last_update = a
    cl._decay(b)
    exp = 4.0 * 0.5 ** ((true_s(b, a) / 86400.0) / 21.0)
    show(
        f"comfort_learning.py:102 _decay [{lbl}]", round(cl.evidence, 6), round(exp, 6)
    )

# --- external_heat.py:462 _decay (confidence)
for lbl, (a, b) in cases.items():
    det = ExternalHeatDetector(ExternalHeatConfig(enabled=True, decay_minutes=90.0))
    det.state.last_active = a
    det._decay(b)
    exp = max(0.0, 1.0 - (true_s(b, a) / 60.0) / 90.0)
    show(
        f"external_heat.py:462 _decay confidence [{lbl}]",
        round(det.state.confidence, 4),
        round(exp, 4),
    )

# --- sysid.py:1299 arm(): 30-day minimum between runs. last_run 03:00Z Sep 25; now 03:30Z Oct 25 (CET):
# true 30 d + 30 min (arm allowed), wall 29 d 23.5 h (arm refused).
last_run = datetime(2026, 9, 25, 5, 0, tzinfo=S)
now = datetime(2026, 10, 25, 4, 30, tzinfo=S)
si = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
si.last_run = last_run
print(
    "   arm gap: true days",
    true_s(now, last_run) / 86400.0,
    "wall days",
    (now - last_run).total_seconds() / 86400.0,
)
show("sysid.py:1299 arm() 30-day gate [true 30d+30min]", si.arm(now), True)


def step(si, now, phase, started):
    si.phase = phase
    si.phase_started = started
    si._baseline_temp = 20.0
    si.step(
        now=now,
        room_temp=20.0,
        outdoor_temp=0.0,
        price=1.0,
        price_horizon=np.ones(8),
        learner_samples=0,
        max_power_kw=5.0,
        cop=3.0,
    )
    return si.phase


# --- sysid.py:1585 phase timer: STEP lasts step_hours=2.0
# fold: STEP started 01:30 CEST (23:30Z); at 02:30 CET fold1 (01:30Z) true 2.0 h, wall 1.0 h -> must be RELAX
si = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
a = datetime(2026, 10, 25, 1, 30, tzinfo=S)
b = datetime(2026, 10, 25, 2, 30, tzinfo=S, fold=1)
print(
    "   fold phase: true h",
    true_s(b, a) / 3600.0,
    "wall h",
    (b - a).total_seconds() / 3600.0,
)
show(
    "sysid.py:1585 STEP->RELAX at true 2h across the fold",
    step(si, b, sysid.PHASE_STEP, a),
    sysid.PHASE_RELAX,
)
# spring: STEP started 00:30 CET (23:30Z prev day); at 03:00 CEST (01:00Z) true 1.5 h, wall 2.5 h -> must still be STEP
si = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
a = datetime(2026, 3, 29, 0, 30, tzinfo=S)
b = datetime(2026, 3, 29, 3, 0, tzinfo=S)
print(
    "   spring phase: true h",
    true_s(b, a) / 3600.0,
    "wall h",
    (b - a).total_seconds() / 3600.0,
)
show(
    "sysid.py:1585 STEP stays at true 1.5h across the spring gap",
    step(si, b, sysid.PHASE_STEP, a),
    sysid.PHASE_STEP,
)
