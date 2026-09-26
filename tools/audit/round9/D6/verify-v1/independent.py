#!/usr/bin/env python3
"""D6 round 9, verifier V1: independent measurements beside the finders' harnesses.

RUN (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D6/verify-v1/independent.py
Each block prints RESULT lines keyed on what the production symbol delivers:
  s1_04  manual_plan.build_override(...).channel_pins over a 96-step grid, expires_at in
         {none->20h default, +24h, +48h}; hours pinned beyond 20 h. Perturbation arm:
         expiry clamped to 20 h (must give 0).
  s2_03  curve_learning.CurveLearner fed margins {0.5, 1.0, 3.0} and 3 start dates,
         largest drop over any trailing 7 calendar days; plus the long-run average rate.
  s2_04  optimizer._multi_start_minimize candidate counts over 4 build_case cells
         (winter/shoulder x single/two-zone, dhw off). Leave-one-out over cells.
  s2_05  simulate_plan registered schema keys (services.SERVICE_SCHEMA_SIMULATE_PLAN.schema)
         minus the backticked names in the paragraph after 'Fields,\nall optional:'.
         Perturbation arm: drop wood_* keys from the key set (must give 0).
  s2_01  number stated in configuration.md's 'All N entities' vs README's stated total.
BASELINE: handoff/audit-r9-evidence worktree (1936d5ca + evidence).
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))

import stress  # noqa: E402  (same import order as the finder: sets the package path)
from heatpump_optimizer import manual_plan, curve_learning, const  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402
from heatpump_optimizer import services  # noqa: E402

# ---- s1_04
now = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
steps = [now + timedelta(minutes=15 * i) for i in range(96)]
for label, exp in (("default20", now + timedelta(hours=const.MANUAL_PLAN_WINDOW_HOURS)),
                   ("plus24", now + timedelta(hours=24)),
                   ("plus48", now + timedelta(hours=48)),
                   ("clamped48", min(now + timedelta(hours=48), now + timedelta(hours=20)))):
    ov = manual_plan.build_override(dhw_slots=None, space_slots=[], expires_at=exp, now=now)
    pins = ov.channel_pins(manual_plan.CHANNEL_SPACE if hasattr(manual_plan, "CHANNEL_SPACE") else "space", steps)
    import math
    n = sum(1 for p in (pins or []) if p is not None and not math.isnan(p))
    print(f"RESULT s1_04_{label}_hours_pinned={n*0.25:.2f} beyond20={max(0.0, n*0.25-20):.2f}")

# ---- s2_03
worst = 0.0
for margin in (0.5, 1.0, 3.0):
    for start in (datetime(2026, 1, 1, 23, tzinfo=timezone.utc),
                  datetime(2026, 3, 7, 6, tzinfo=timezone.utc),
                  datetime(2026, 10, 20, 12, tzinfo=timezone.utc)):
        cl = curve_learning.CurveLearner()
        hist = []
        for d in range(70):
            cl.record_day(start + timedelta(days=d), margin)
            hist.append(cl.bias)
        drop = max(hist[d - 7] - hist[d] for d in range(7, 70))
        avg = (hist[6] - hist[69]) / (63 / 7)
        worst = max(worst, drop)
        print(f"# s2_03 margin={margin} start={start.date()} max7day={drop:.3f} avg_per_week={avg:.3f}")
print(f"RESULT s2_03_max_7day_drop_k={worst:.3f}")

# ---- s2_04
import stress  # noqa: E402
cells = {}
orig = optmod._multi_start_minimize
for season in ("winter", "shoulder" if "shoulder" in stress.__dict__.get("SEASONS", {"shoulder": 1}) else "spring"):
    for tz in (False, True):
        seen = []
        def spy(objective, candidates, *a, **k):
            seen.append(len(candidates))
            return orig(objective, candidates, *a, **k)
        try:
            with mock.patch.object(optmod, "_multi_start_minimize", spy):
                stress.build_case(season=season, two_zone=tz, dhw=False)
        except Exception as e:  # season name may not exist
            print(f"# s2_04 {season} two_zone={tz} error {e!r}")
            continue
        cells[(season, tz)] = seen
        print(f"# s2_04 {season} two_zone={tz} candidates per call {seen}")
firsts = [v[0] for v in cells.values() if v]
print(f"RESULT s2_04_first_call_candidates_min={min(firsts)} max={max(firsts)} cells={len(firsts)}")
for k in cells:
    rest = [v[0] for kk, v in cells.items() if kk != k and v]
    print(f"# s2_04 leave-out {k}: min={min(rest)} max={max(rest)}")

# ---- s2_05
keys = {str(getattr(k, "schema", k)) for k in services.SERVICE_SCHEMA_SIMULATE_PLAN.schema}
text = (ROOT / "docs/configuration.md").read_text()
m = re.search(r"\*\*`simulate_plan`\*\*.*?Fields,\s*all optional:(.*?)\.\s", text, re.S)
listed = set(re.findall(r"`([a-z_0-9]+)`", m.group(1)))
missing = sorted(keys - listed - {"entry_id"})
print(f"# s2_05 schema={sorted(keys)} listed={sorted(listed)}")
print(f"RESULT s2_05_missing={len(missing)} {missing}")
pert = {k for k in keys if not k.startswith("wood_")}
print(f"RESULT s2_05_perturb_drop_wood_missing={len(sorted(pert - listed - {'entry_id'}))}")

# ---- s2_01
c = re.search(r"All (\d+) entities", text)
r = re.findall(r"(\d+) entities", (ROOT / "README.md").read_text())
print(f"RESULT s2_01_configuration_md_stated={c.group(1) if c else None} readme_stated={r[:5]}")
