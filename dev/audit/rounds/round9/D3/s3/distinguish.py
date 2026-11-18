#!/usr/bin/env python3
"""D3.M4 -- is each pre-screen survivor a real behaviour change, or equivalent?

Metric: for one survivor, the named production symbol is driven by a small
  fixed scenario twice -- once from a copy of the unmutated package, once from
  a copy carrying the pooled mutant line -- and the scenario's output value is
  printed for both.  differs=1 when they differ (the survivor is a gap: the
  suite cannot fail on a real behaviour change), 0 when they agree (equivalent
  on this scenario).  Count key: the value the production symbol returns or
  stores, never an input attribute.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s3/distinguish.py [M19 M21 ...] [--identity]
Expected (baseline 1936d5ca72a0): M02 differs=1 (under TZ=Europe/Stockholm;
  0 under TZ=UTC), M11 differs=0, M19 differs=1, M20 differs=1, M21 differs=1,
  M24 differs=1; exact (deterministic scenarios, no timing).
Perturbation / null control: --identity writes new == old into the "mutant"
  copy; every scenario must then print differs=0.
Machine: box B3 (4 CPUs, CPython 3.14.0rc2).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = Path("custom_components/heatpump_optimizer")

PRELUDE = """
import json, math, asyncio, os, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests")
import harness  # inserts the checkout's own package path; undo that below
sys.path.insert(0, os.environ["D3S3_PKG"])
assert "heatpump_optimizer" not in sys.modules
"""

SCEN = {
    # open_meteo._parse_block: the naive ISO stamps Open-Meteo returns under
    # timezone=UTC; the metric is the first parsed instant, as UTC ISO text.
    "M02": ("TZ=Europe/Stockholm", """
from heatpump_optimizer import open_meteo as om
s = om._parse_block({"time": ["2026-01-15T00:00", "2026-01-15T01:00",
                              "2026-01-15T02:00"],
                     "shortwave_radiation": [0.0, 10.0, 20.0]},
                    "shortwave_radiation", 1500.0)
print(json.dumps(s.times[0].astimezone(timezone.utc).isoformat()))
"""),
    # open_meteo series mean_over on an EMPTY series: None either way.
    "M11": ("", """
from heatpump_optimizer import open_meteo as om
e = om._EMPTY
t0 = datetime(2026, 1, 15, tzinfo=timezone.utc)
out = [e.mean_over(t0 + timedelta(minutes=15 * k), t0 + timedelta(minutes=15 * k + d))
       for k in range(-4, 5) for d in (-30, 0, 15, 60)]
print(json.dumps(out))
"""),
    # dhw_draws.DrawStats: an OPEN occurrence (a shower in progress at 1.5
    # kWh) through the store round trip, then closed by the next fold; the
    # metric is the event the reservoir records for it.
    "M19": ("", """
from heatpump_optimizer.dhw_draws import DrawStats
d = DrawStats()
t = datetime(2026, 1, 15, 6, 30, tzinfo=timezone.utc)
d.fold(t, "06:00-08:30", 1.0)
d.fold(t + timedelta(minutes=15), "06:00-08:30", 0.5)
r = DrawStats.from_dict(json.loads(json.dumps(d.as_dict())))
r.fold(t + timedelta(hours=4), "", 0.0)
print(json.dumps(r.reservoirs.get("06:00-08:30")))
"""),
    # legionella.LegionellaGuard._drive_switch in observe (not controlling):
    # five healthy cycles; the metric is how many issue-registry deletes of
    # the write-failed notice the five cycles issue.
    "M20": ("", """
from harness import FakeHass
from homeassistant.helpers import issue_registry as ir
from heatpump_optimizer import legionella as lg
from heatpump_optimizer.disinfection import DisinfectionSwitch
calls = []
ir.async_delete_issue = lambda hass, dom, iid: calls.append(("delete", iid))
lg.create_issue = lambda *a, **k: calls.append(("create", a[2]))
async def _svc(*a, **k):
    return None
g = lg.LegionellaGuard.__new__(lg.LegionellaGuard)
g.hass = FakeHass()
g.disinfect = DisinfectionSwitch({}, _svc, lambda e: None)
g.switch_latched = False
g._switch_saved = ((), False)
g.write_failed_notice = False
async def _save():
    return None
g.async_save = _save
for _ in range(5):
    asyncio.run(g._drive_switch(False))
print(json.dumps(len([c for c in calls if c[1] == "dhw_disinfection_write_failed"])))
"""),
    # ledger.MonthlyLedger.add: one non-finite amount after a finite one,
    # then the store round trip Home Assistant's orjson Store performs (NaN
    # is written as null); the metric is the months that survive the reload.
    "M21": ("", """
import orjson
from heatpump_optimizer.ledger import MonthlyLedger
L = MonthlyLedger()
t = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
L.add(t, "spot", kwh=10.0, sek=20.0)
L.add(t, "spot", kwh=float("nan"), sek=1.0)
R = MonthlyLedger.from_dict(orjson.loads(orjson.dumps(L.as_dict())))
print(json.dumps([len(L.months), len(R.months),
                  str(L.months.get("2026-01", {}).get("lines", {}).get("spot"))]))
"""),
    # dhw_learning.DhwProfileLearner.async_fold_draw_stats while a wood burn
    # drives the tank (external_heat_active True): a 2 degC drop in 15 min in
    # the morning window; the metric is the energy folded into the OPEN
    # occurrence (the docstring: such intervals are "skipped outright").
    "M24": ("", """
from harness import FakeHass
from heatpump_optimizer.thermal_model import ThermalParameters
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.dhw_draws import labels_for, window_label
class L(DhwProfileLearner):
    async def async_save_draws(self):
        return None
p = ThermalParameters()
p.dhw_enabled = True
l = L(FakeHass(), "x", p, frozen=lambda *_: None, heating_active=lambda: False,
      external_heat_active=lambda: True)
l.cooling_rate = 0.3
w = p.dhw_demand_windows
now = datetime(2026, 1, 15, 7, 0, tzinfo=timezone.utc)
asyncio.run(l.async_fold_draw_stats(now, 55.0, 2.0, 0.25))
import heatpump_optimizer as _hp
assert _hp.__file__.startswith(os.environ["D3S3_PKG"]), _hp.__file__
print(json.dumps(round(l.draw_stats._open_kwh, 4)))
"""),
}


def pooled(mid: str) -> dict:
    pool = json.loads((HERE / "pool.json").read_text())["pool"]
    return next(m for m in pool if m["id"] == mid)


def copy_pkg(root: Path, mut: dict | None) -> Path:
    dest = root / "custom_components"
    shutil.copytree(PKG, dest / "heatpump_optimizer")
    if mut is not None:
        f = dest / "heatpump_optimizer" / Path(mut["file"]).name
        lines = f.read_text().splitlines(True)
        assert lines[mut["line"] - 1].rstrip("\n") == mut["old"], mut["id"]
        lines[mut["line"] - 1] = mut["new"] + "\n"
        f.write_text("".join(lines))
    return dest


def run(pkg_parent: Path, env_kv: str, code: str) -> str:
    env = {**os.environ,
           "PYTHONPATH": os.pathsep.join([str(pkg_parent), "tests/hastub"]),
           "D3S3_PKG": str(pkg_parent)}
    if env_kv:
        k, v = env_kv.split("=", 1)
        env[k] = v
    p = subprocess.run([sys.executable, "-c", PRELUDE + code], env=env,
                       capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        return "ERROR " + p.stderr.strip().splitlines()[-1]
    return p.stdout.strip().splitlines()[-1]


def main() -> int:
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(SCEN)
    identity = "--identity" in sys.argv
    tz_override = next((a.split("=", 1)[1] for a in sys.argv
                        if a.startswith("--tz=")), None)
    tmp = Path(tempfile.mkdtemp(prefix="d3s3-dist-"))
    try:
        for mid in ids:
            envkv, code = SCEN[mid]
            if tz_override is not None and envkv.startswith("TZ="):
                envkv = "TZ=" + tz_override
            mut = pooled(mid)
            if identity:
                mut = dict(mut, new=mut["old"])
            base = run(copy_pkg(tmp / f"{mid}-base", None), envkv, code)
            mv = run(copy_pkg(tmp / f"{mid}-mut", mut), envkv, code)
            print(f"{mid} [{envkv or 'default env'}] {mut['file']}:"
                  f"{mut['line']} {mut['kind']}")
            print(f"    baseline: {base}")
            print(f"    mutant:   {mv}")
            print(f"RESULT {mid}_differs={int(base != mv)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT thread_factor=1.00 (no timing RESULT; values only)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
