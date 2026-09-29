"""D6-s2 harness: a sample of docs/how-it-works.md claims, each executed against production.

Metric: count of the sampled how-it-works.md claims (CHECKS below) whose executed check
disagrees with the doc sentence. Key: the value the named production symbol delivers.

  :47   24 h horizon on a 15-minute grid          optimizer.HeatPumpOptimizer.optimize (result.timestamps) via tests/stress.py:build_case
  :120  space solve runs from two starting points  optimizer._multi_start_minimize (len(candidates) per call, wrapped)
  :289  two-zone / single-zone parameter defaults  thermal_model.ThermalParameters.from_config({})
  :293  hot water activates on any one of tank volume / tank sensor / windows
                                                   thermal_model.ThermalParameters.from_config
  :1143 COP scale bound [0.5, 1.6]; :1148 capacity keeps >= 60 %; :1150 aperture [0.3, 2.0]
                                                   const.COP_SCALE_MIN/MAX, CAPACITY_FLOOR_FRACTION, SOLAR_APERTURE_MIN/MAX
                                                   (constant reads: spot depth, named as such in REPORT.md)

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/howitworks_claims.py
Perturbation (finding D6-s2 starts): --perturb-starts truncates each multi-start call to its
  first two candidates, the behaviour the doc describes; space_solve_start_candidates 4 -> 2.
Perturbation (generic): --perturb wraps optimizer._multi_start_minimize to pass only the first
  candidate, and sets thermal_model defaults house_thermal_mass via
  ThermalParameters.from_config({'house_thermal_mass': 12}); howitworks_claims_false up by >= 2.
Expected: see REPORT.md (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import re
import sys
import time
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import stress  # noqa: E402  (thread pin precedes its numpy import)
from heatpump_optimizer import const, optimizer as optmod  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

DOCL = (ROOT / "docs/how-it-works.md").read_text().splitlines()
RESULTS = []


def line_of(pat):
    for i, l in enumerate(DOCL, 1):
        if re.search(pat, l):
            return i
    return 0


def claim(pat, what, ok, detail=""):
    RESULTS.append((f"docs/how-it-works.md:{line_of(pat)}", what, bool(ok), detail))


def run(perturb):
    starts = []
    lbfgsb = []
    orig = optmod._multi_start_minimize
    orig_min = optmod._scoped_minimize

    def count_min(*a, **k):
        lbfgsb[-1] += 1
        return orig_min(*a, **k)

    def spy(objective, candidates, *a, **k):
        if perturb:
            candidates = candidates[:1]
        if "--perturb-starts" in sys.argv:
            candidates = candidates[:2]
        starts.append(len(candidates))
        lbfgsb.append(0)
        return orig(objective, candidates, *a, **k)

    with mock.patch.object(optmod, "_multi_start_minimize", spy):
        one = stress.build_case(season="winter", two_zone=False, dhw=False)
        two = stress.build_case(season="winter", two_zone=True, dhw=True)
    res = one["result"]
    ts = res.timestamps
    step_min = (ts[1] - ts[0]).total_seconds() / 60
    span_h = len(ts) * step_min / 60
    claim(r"builds a 24-hour horizon on a 15-minute grid", "24-hour horizon on a 15-minute grid",
          step_min == 15 and span_h == 24, f"{len(ts)} steps x {step_min} min = {span_h} h")
    claim(r"Every optimization interval \(30 minutes by default\)", "interval defaults to 30 minutes",
          const.DEFAULT_OPTIMIZATION_INTERVAL == 30 if hasattr(const, "DEFAULT_OPTIMIZATION_INTERVAL") else False,
          str(getattr(const, "DEFAULT_OPTIMIZATION_INTERVAL", "?")))
    # the solver work of the perturbed arm differs: count what the spy saw
    print(f"RESULT space_solve_start_candidates={starts[0]} count")
    print(f"RESULT space_solve_minimize_calls={one['solver_calls']} count  (tests/stress.py:SolverWork.calls, single-zone no-DHW solve)")
    claim(r"runs from two candidate", "the space solve runs from two starting points",
          starts and starts[0] == 2, f"candidates refined per multi-start call {starts}; minimize calls in the single-zone solve {one['solver_calls']}")
    p = ThermalParameters.from_config({"house_thermal_mass": 12.0} if perturb else {})
    got = (p.upper_floor_thermal_mass, p.lower_floor_thermal_mass, p.upper_floor_heat_loss,
           p.lower_floor_heat_loss, p.inter_zone_transfer, p.radiator_power_fraction,
           p.buffer_tank_volume, p.room_thermal_mass, p.heat_loss_coefficient)
    want = (3.0, 8.0, 0.08, 0.07, 0.5, 0.4, 35.0, 10.0, 0.15)
    claim(r"Defaults, for orientation", "two-zone and single-zone defaults", got == want, f"{got}")
    for cfg, label in (({const.CONF_DHW_TANK_VOLUME: 180.0}, "tank volume"),
                       ({const.CONF_DHW_TEMP_ENTITY: "sensor.tank"}, "tank sensor"),
                       ({const.CONF_DHW_WINDOWS: "06:00-08:00"}, "windows")):
        claim(r"hot water optimization activates", f"hot water activates on {label} alone",
              ThermalParameters.from_config(cfg).dhw_enabled is True, "")
    claim(r"hot water optimization activates", "hot water stays off with none of them",
          ThermalParameters.from_config({}).dhw_enabled is False, "")
    claim(r"^\| COP scale", "COP scale bound [0.5, 1.6]", (const.COP_SCALE_MIN, const.COP_SCALE_MAX) == (0.5, 1.6), "constant read")
    claim(r"^\| Capacity envelope", "capacity keeps >= 60 % of nameplate", const.CAPACITY_FLOOR_FRACTION == 0.6, "constant read")
    claim(r"^\| Solar aperture", "aperture clamped [0.3, 2.0]",
          (const.SOLAR_APERTURE_MIN, const.SOLAR_APERTURE_MAX) == (0.3, 2.0), "constant read")


def main():
    perturb = "--perturb" in sys.argv
    run(perturb)
    for src, what, ok, det in RESULTS:
        print(f"{'true ' if ok else 'FALSE'} {src:28s} {what} -- {det}")
    print(f"RESULT howitworks_claims={len(RESULTS)} count")
    print(f"RESULT howitworks_claims_false={sum(not r[2] for r in RESULTS)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
