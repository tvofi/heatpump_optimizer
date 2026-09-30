"""RCA-1747: did any test that solves with dhw_blocked=True ever reach the co-optimisation replan?

Run from a checkout's root, with the suite's own PYTHONPATH:
  PYTHONPATH=tests/hastub:custom_components:tests python3 rca_suite_reach.py tests/features.py [out.json]
Patches HeatPumpOptimizer.optimize / _co_optimize / _build_dhw_requirements with pass-through
spies (nothing is changed: every call returns the original's value), runs the script as
__main__, and on exit writes counts per solve kind:
  solves            optimize() calls
  co_entered        _co_optimize entered
  replan_built      the replan's _build_dhw_requirements ran (the contention mask was non-empty)
  replan_adopted    _co_optimize returned the replanned DHW (it scored better)
  adopted_dhw_kwh   DHW energy in adopted replans (the defect's output when the solve is blocked)
split by whether the solve had dhw_blocked=True.  The defect needs blocked AND adopted AND
adopted_dhw_kwh > 0; a suite with zero blocked-and-adopted solves cannot see it.
"""
import atexit, inspect, json, runpy, sys
import numpy as np

script = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = [script]
sys.path.insert(0, "tests")
from heatpump_optimizer import optimizer as O  # noqa: E402

H = O.HeatPumpOptimizer
_opt, _co, _build = H.optimize, H._co_optimize, H._build_dhw_requirements
_sig = inspect.signature(_opt)
stack = []
C = {k: {"solves": 0, "co_entered": 0, "replan_built": 0, "replan_adopted": 0, "adopted_dhw_kwh": 0.0,
         "replan_build_blocked_args": {}} for k in ("blocked", "unblocked")}


def _k():
    return "blocked" if (stack and stack[-1]["blocked"]) else "unblocked"


def optimize(self, *a, **kw):
    try:
        b = _sig.bind(self, *a, **kw); b.apply_defaults(); blocked = bool(b.arguments.get("dhw_blocked", False))
    except TypeError:
        blocked = bool(kw.get("dhw_blocked", False))
    stack.append({"blocked": blocked, "in_co": False})
    C[_k()]["solves"] += 1
    try:
        return _opt(self, *a, **kw)
    finally:
        stack.pop()


def co(self, h, **kw):
    k = _k(); C[k]["co_entered"] += 1
    if stack: stack[-1]["in_co"] = True
    try:
        r = _co(self, h, **kw)
    finally:
        if stack: stack[-1]["in_co"] = False
    if r[1] is not kw.get("dhw_power"):
        C[k]["replan_adopted"] += 1
        C[k]["adopted_dhw_kwh"] += float(np.sum(np.asarray(r[1], dtype=float)) * float(getattr(self.config, "dt_hours", 0.25)))
    return r


def build(self, *a, **kw):
    if stack and stack[-1]["in_co"]:
        k = _k(); C[k]["replan_built"] += 1
        v = repr(kw.get("blocked", "<omitted>"))
        C[k]["replan_build_blocked_args"][v] = C[k]["replan_build_blocked_args"].get(v, 0) + 1
    return _build(self, *a, **kw)


H.optimize, H._co_optimize, H._build_dhw_requirements = optimize, co, build


@atexit.register
def _report():
    for k in C:
        C[k]["adopted_dhw_kwh"] = round(C[k]["adopted_dhw_kwh"], 3)
    line = "RESULT " + json.dumps({"script": script, **C}, sort_keys=True)
    print(line, file=sys.stderr)
    if out:
        open(out, "w").write(line + "\n")


runpy.run_path(script, run_name="__main__")
