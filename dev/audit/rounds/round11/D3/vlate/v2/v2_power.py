#!/usr/bin/env python3
"""VD3L V2 D3-s1-70: whole-module mutant of coordinator.py:8806 (`and` -> `or`), the mutant module's
own HeatPumpOptimizerCoordinator._on_power_event, called unbound on a namespace holding real
PeakTracker/GuardState. Own inputs: meter 6 kW, tracker peak 4 kW, three events 30 s apart.
Cells: (i) tariff disabled + fuse 8 kW; (ii) tariff enabled, factor 0 (months mask), fuse 8 kW;
(iii) tariff enabled, factor 0, NO fuse. Metric: guard.suppressing after the 3rd event and the
(proj, threshold) last handed to GuardState.update. Null: enabled + factor 1 + fuse 8."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from unittest import mock
from mutload import load
b, m = load("coordinator", 8806, "if tariff.enabled and factor > 0.0:", "if tariff.enabled or factor > 0.0:")
tar = load("tariff"); pg = load("power_guard")
T0 = datetime(2026, 8, 3, 9, 0, tzinfo=timezone.utc)

def drive(mod, tariff, fuse):
    tr = tar.PeakTracker(); tr.month, tr.peaks, tr.peak_days = "2026-08", [4.0], ["2026-08-01"]
    g = pg.GuardState(); seen = []
    real = g.update
    def spy(now, key, proj, thr, margin, *, floor_hold):
        seen.append((round(proj, 4), thr)); return real(now, key, proj, thr, margin, floor_hold=floor_hold)
    g.update = spy
    me = SimpleNamespace(_peak_guard=g, _peak_tracker=tr, _guard_last_fold=None,
                         _config=SimpleNamespace(peak_guard_margin_kw=0.3), _capacity_tariff=lambda: tariff,
                         _fuse_kw=lambda: fuse, _guard_floor_hold=lambda: False, publish=lambda *a, **k: None,
                         _spawn=lambda *a, **k: None, _async_peak_guard_transition=lambda: None)
    ev = SimpleNamespace(data={"new_state": SimpleNamespace(state="6.0", attributes={"unit_of_measurement": "kW"})})
    ts = iter([T0 + timedelta(seconds=30 * i) for i in range(3)])
    with mock.patch.object(mod.dt_util, "now", lambda: next(ts)):
        for _ in range(3):
            mod.HeatPumpOptimizerCoordinator._on_power_event(me, ev)
    return (seen[-1] if seen else None), g.suppressing

cells = {"i_disabled_fuse8": (tar.CapacityTariff(enabled=False), 8.0),
         "ii_enabled_factor0_fuse8": (tar.CapacityTariff(enabled=True, months=frozenset({1})), 8.0),
         "iii_enabled_factor0_nofuse": (tar.CapacityTariff(enabled=True, months=frozenset({1})), None)}
moved = 0
for k, (t, f) in cells.items():
    rb, rm = drive(b, t, f), drive(m, t, f)
    moved += int(rb != rm)
    print(f"RESULT 70_{k}_base={rb} mut={rm}")
print(f"RESULT 70_cells_moved={moved} of {len(cells)}")
t = tar.CapacityTariff(enabled=True)
print(f"RESULT 70_null_moved={int(drive(b, t, 8.0) != drive(m, t, 8.0))}")
