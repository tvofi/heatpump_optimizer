#!/usr/bin/env python3
# Metric: _immersion_dhw_margin(now) in K for three immersion events, two plainly recent and one stamped -05:00 whose
#   true instant is 1 h inside the 14-day cutoff, with now aware UTC (2026-01-15T12:00Z).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_c20f346300d7efc1.py
# EXPECTED RESULT margin_baseline=2.0 K  (three events inside 14 days: >= 3, margin on)
# EXPECTED RESULT margin_mutant=0.0 K  (the -05:00 stamp is re-labelled UTC by replace(), lands 4 h before the cutoff)
# EXPECTED RESULT null_baseline=2.0 K
# EXPECTED RESULT null_mutant=2.0 K  (the third event stamped +00:00: replace() is the identity)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._immersion_dhw_margin, line 9292.
# Perturbation: key c20f346300d7efc1 (BOOLOP), line 9292 `if when.tzinfo is None and now.tzinfo is not None:` ->
#   `if when.tzinfo is None or now.tzinfo is not None:`, applied in memory. Direction: margin down (2.0 -> 0.0).
# Null control: the same three events with the boundary one stamped in UTC.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from probe_imm_common import margin  # noqa: E402

BASE = L.baseline("_immersion_dhw_margin")
MUT = L.mutant("_immersion_dhw_margin", "if when.tzinfo is None and now.tzinfo is not None:",
               "if when.tzinfo is None or now.tzinfo is not None:")
now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
edge = now - timedelta(days=14) + timedelta(hours=1)
ny = timezone(timedelta(hours=-5))
recent = [(now - timedelta(days=1)).isoformat(), (now - timedelta(days=2)).isoformat()]
ev = recent + [edge.astimezone(ny).isoformat()]
nv = recent + [edge.isoformat()]
print(f"RESULT margin_baseline={margin(BASE, ev, now):.1f} K")
print(f"RESULT margin_mutant={margin(MUT, ev, now):.1f} K")
print(f"RESULT null_baseline={margin(BASE, nv, now):.1f} K")
print(f"RESULT null_mutant={margin(MUT, nv, now):.1f} K")
L.footer()
