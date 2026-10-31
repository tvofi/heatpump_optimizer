#!/usr/bin/env python3
"""Equivalence probe for coordinator.py ``_forecast_arrays`` CMP_BOUND (#1745, PR #2025).

The mutant is ``np.any(snow_array > 0.0)`` -> ``np.any(snow_array >= 0.0)`` on
the precipitation-type guard. The ``survivor_triage`` row
``tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._forecast_arrays.CMP_BOUND.54c3c7b5.json``
marks it ``equivalent`` on this probe's result. Re-run it when that line,
``_liquid_fraction`` or ``_weather_series`` changes.

Metric: the number of cases whose precipitation array differs, float by float
(``repr``), from the head's. The probe builds three ``git archive HEAD`` trees:
- ``head``: unchanged;
- ``mutant``: the operator's mutant;
- ``control``: the perturbation. It changes only the zero-snow boundary,
  halving the rain when every step's snow is 0.
In each tree it drives the real coordinator's ``_forecast_arrays`` and the
real ``_weather_series`` over 552 cases: 23 rain values (None, text, nan,
+-inf, -3, -0.0, 0, 1e-12, 1e-9, 1.0000001e-9 ... 1e300, 1.7e308), 6
Open-Meteo snow answers (None, 0, -0.0, -2, nan, Open-Meteo absent), timed
and untimed forecast rows, and the precipitation-type flag on and off.

Expected, as measured at 95b08306 and again at 9c664109 (this copy), and cited
by the triage row:
    RESULT mutant: cases=552 differing=0 (flag on 0, flag off 0)
    RESULT control: cases=552 differing=264 (flag on 264, flag off 0)
    boundary cases (flag on, every step's snow 0)=276, of them with rain on some step=264
The control moving every wet boundary case shows the probe reaches the
boundary; the 12 dry boundary cases cannot move under any multiplier.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/eg_b11_equiv_6840.py <out-dir>

It writes ``equiv_6840_{head,mutant,control}.json`` into ``<out-dir>``.
"""

import json, os, subprocess, sys, tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)

GUARD = "        if ctx._config.precip_type_enabled and np.any(snow_array > 0.0):\n"
BODY = ("            precip_array = precip_array * _liquid_fraction(\n"
        "                precip_array, snow_array\n"
        "            )\n")
VARIANTS = {
    "head": (GUARD, None),
    "mutant": (GUARD, GUARD.replace("> 0.0", ">= 0.0")),
    "control": (GUARD + BODY,
                GUARD.replace("> 0.0", ">= 0.0")
                + "            precip_array = precip_array * _liquid_fraction(\n"
                  "                precip_array, snow_array\n"
                  "            ) * (1.0 if np.any(snow_array > 0.0) else 0.5)\n"),
}

DRIVER = r'''
import asyncio, json, math, sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass
import numpy as np
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

now = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
RAIN = [None, "garbage", float("nan"), float("inf"), float("-inf"), -3.0, -0.0,
        0.0, 1e-12, 1e-9, 1.0000001e-9, 2e-9, 1e-6, 0.1, 0.3, 1.0, 1.7, 2.0,
        7.3, 25.0, 1e3, 1e300, 1.7e308]
SNOW = [None, 0.0, -0.0, -2.0, float("nan"), "none-avail"]
rows, boundary, boundary_wet = [], 0, 0
for flag in (False, True):
    for snow in SNOW:
        for timed in (True, False):
            for k in range(len(RAIN)):
                # three entries: the rain under test, its neighbour, and a dry one
                vals = [RAIN[k], RAIN[(k + 7) % len(RAIN)], 0.0]
                fc = []
                for j, v in enumerate(vals):
                    e = {"temperature": 0.0, "wind_speed": 1.0, "precipitation": v,
                         "humidity": 80.0}
                    if timed:
                        e["datetime"] = (now + timedelta(hours=j)).isoformat()
                    fc.append(e)
                entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                                        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
                                        const.CONF_PRECIP_TYPE_ENABLED: flag})
                c = HeatPumpOptimizerCoordinator(FakeHass(), entry)
                n = c._ctx._opt_config.n_steps
                c._price_series = lambda n, m, o: (np.ones(n), np.ones(n, dtype=bool), np.zeros(n))
                c._weather_forecast = fc
                c._update_snow_memory = lambda *a: False
                if snow == "none-avail":
                    c._open_meteo = None
                else:
                    c._open_meteo = NS(available=True, humidity_for=lambda *a: None, irradiance_for=lambda *a: None,
                                       snowfall_for=(lambda s: (lambda *a: s))(snow))
                fa = c._forecast_arrays(now)
                p = [repr(float(x)) for x in np.asarray(fa.precipitation)]
                if flag:
                    boundary += 1
                    if any(float(x) > 0 for x in np.asarray(fa.precipitation)):
                        boundary_wet += 1
                rows.append({"flag": flag, "snow": repr(snow), "timed": timed,
                             "rain": repr(RAIN[k]), "precip": p})
print(json.dumps({"rows": rows, "boundary": boundary, "boundary_wet": boundary_wet}))
'''

def build(variant, root):
    head = REPO
    subprocess.run(f"git archive HEAD custom_components tests | tar -x -C {root}",
                   shell=True, check=True, cwd=head)
    old, new = VARIANTS[variant]
    if new is not None:
        f = Path(root) / "custom_components/heatpump_optimizer/coordinator.py"
        src = f.read_text()
        assert src.count(old) == 1, (variant, src.count(old))
        f.write_text(src.replace(old, new))

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
res = {}
for v in ("head", "mutant", "control"):
    with tempfile.TemporaryDirectory() as root:
        build(v, root)
        r = subprocess.run([sys.executable, "-c", DRIVER], cwd=root,
                           capture_output=True, text=True,
                           env=dict(os.environ, PYTHONPATH=f"{root}/tests/hastub"))
        if r.returncode:
            print(v, "FAILED", r.stderr[-3000:]); sys.exit(2)
        res[v] = json.loads(r.stdout.strip().splitlines()[-1])
        (out / f"equiv_6840_{v}.json").write_text(json.dumps(res[v], indent=0))
h = res["head"]["rows"]
for v in ("mutant", "control"):
    rows = res[v]["rows"]
    assert len(rows) == len(h)
    diff = sum(1 for a, b in zip(h, rows) if a["precip"] != b["precip"])
    diff_on = sum(1 for a, b in zip(h, rows) if a["precip"] != b["precip"] and a["flag"])
    diff_off = diff - diff_on
    print(f"RESULT {v}: cases={len(h)} differing={diff} (flag on {diff_on}, flag off {diff_off})")
print(f"boundary cases (flag on, every step's snow 0)={res['head']['boundary']}, "
      f"of them with rain on some step={res['head']['boundary_wet']}")
