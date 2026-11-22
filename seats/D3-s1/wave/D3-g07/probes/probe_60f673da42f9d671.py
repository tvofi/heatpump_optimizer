#!/usr/bin/env python3
# Metric: _immersion_dhw_margin(now) in K for three immersion events, two plainly recent and one stamped exactly at
#   the 14-day cutoff (now - 14 d), now aware UTC (2026-01-15T12:00Z).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_60f673da42f9d671.py
# EXPECTED RESULT margin_baseline=2.0 K  (the cutoff instant counts: three events, margin on)
# EXPECTED RESULT margin_mutant=0.0 K  (the tie no longer counts: two events, margin off)
# EXPECTED RESULT null_baseline=2.0 K
# EXPECTED RESULT null_mutant=2.0 K  (the third event 1 s inside the cutoff: counted in both)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._immersion_dhw_margin, line 9294.
# Perturbation: key 60f673da42f9d671 (CMP_BOUND), line 9294 `if when >= cutoff:` -> `if when > cutoff:`, applied in memory.
#   Direction: margin down at the tie (2.0 -> 0.0).
# Null control: the third event one second inside the cutoff.
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
MUT = L.mutant("_immersion_dhw_margin", "if when >= cutoff:", "if when > cutoff:")
now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
cutoff = now - timedelta(days=14)
recent = [(now - timedelta(days=1)).isoformat(), (now - timedelta(days=2)).isoformat()]
ev = recent + [cutoff.isoformat()]
nv = recent + [(cutoff + timedelta(seconds=1)).isoformat()]
print(f"RESULT margin_baseline={margin(BASE, ev, now):.1f} K")
print(f"RESULT margin_mutant={margin(MUT, ev, now):.1f} K")
print(f"RESULT null_baseline={margin(BASE, nv, now):.1f} K")
print(f"RESULT null_mutant={margin(MUT, nv, now):.1f} K")
L.footer()
