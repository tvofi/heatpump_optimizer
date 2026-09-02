"""Verifier-3, D9-03 fix scope: does the proposed one-entry objective cache
actually remove the duplicate f(x), and is it really bit-identical?

The finding's fix scope says: wrap ``objective`` in ``_multi_start_minimize``
in a one-entry cache keyed on ``x.tobytes()`` so scipy's ``fun`` call and the
batched jac's ``f0`` share one evaluation -- "bit-identical, no golden drift".
This harness implements exactly that wrapper (at the ``_multi_start_minimize``
boundary, so the production body is untouched) and executes both halves of
the claim:

  metric 1  ``scalar_trajectory_calls`` = calls to
            ``ThermalModel.simulate_trajectory`` per solve, and per gradient
            (``njev`` from scipy's own counters). The duplicate f(x) shows up
            here as 2 per gradient instead of 1.
  metric 2  all 49 golden scenarios captured with and without the wrapper,
            payloads diffed field by field at the fixtures' own stored
            precision (``golden.PRECISION`` = 6, compared exactly).

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/v3_d903_memo_golden.py

Expected (baseline c398fc8): trajectories per gradient 2.07 -> 1.07 on the
default two-zone DHW solve, and zero changed fields across all 49 fixtures.

Instrumented symbols: optimizer:_multi_start_minimize (the wrapper),
optimizer:_scoped_minimize (counters),
thermal_model:ThermalModel.simulate_trajectory.
Baseline c398fc84eec25fc44b60d74aae05b9a2da205884; Apple M1 8-core 8 GB.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
import golden  # noqa: E402

C = {"traj": 0, "njev": 0, "nfev": 0}

_orig_msm = opt_mod._multi_start_minimize
_orig_scoped = opt_mod._scoped_minimize
_orig_traj = tm_mod.ThermalModel.simulate_trajectory


def hooked_traj(self, *a, **k):
    C["traj"] += 1
    return _orig_traj(self, *a, **k)


def hooked_scoped(*a, **k):
    res = _orig_scoped(*a, **k)
    C["njev"] += int(getattr(res, "njev", 0) or 0)
    C["nfev"] += int(getattr(res, "nfev", 0) or 0)
    return res


tm_mod.ThermalModel.simulate_trajectory = hooked_traj
opt_mod._scoped_minimize = hooked_scoped


def memo_msm(objective, candidates, bounds, args=(), **kw):
    """The proposed fix, at the boundary: one entry, keyed on x.

    ``args`` is fixed for the whole call, so the key is x alone. The cached
    value is the float the objective returned, so a hit is bit-identical to
    the miss it replaces -- which is the half of the claim that has to be
    proved on the fixtures, not argued.
    """
    slot: dict = {}

    def cached(x, *a):
        key = np.asarray(x, dtype=float).tobytes()
        if slot.get("k") == key:
            slot["hits"] = slot.get("hits", 0) + 1
            return slot["v"]
        value = objective(x, *a)
        slot["k"] = key
        slot["v"] = value
        return value

    try:
        return _orig_msm(cached, candidates, bounds, args=args, **kw)
    finally:
        C["hits"] = C.get("hits", 0) + slot.get("hits", 0)


stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]


def measure(label, fixed, **case):
    C.update(traj=0, njev=0, nfev=0, hits=0)
    opt_mod._multi_start_minimize = memo_msm if fixed else _orig_msm
    try:
        build_case(**case)
    finally:
        opt_mod._multi_start_minimize = _orig_msm
    njev = max(C["njev"], 1)
    d9lib.result(f"{label}.njev", C["njev"], "count")
    d9lib.result(f"{label}.scalar_trajectory_calls", C["traj"], "count")
    d9lib.result(f"{label}.trajectories_per_gradient", C["traj"] / njev, "ratio")
    d9lib.result(f"{label}.cache_hits", C.get("hits", 0), "count")


measure("current_two_zone_dhw", False, season="winter", two_zone=True, dhw=True)
measure("memo_two_zone_dhw", True, season="winter", two_zone=True, dhw=True)
measure("current_single_zone_nodhw", False, season="winter", two_zone=False, dhw=False)
measure("memo_single_zone_nodhw", True, season="winter", two_zone=False, dhw=False)


def diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            diff(a[k], b.get(k), f"{path}.{k}", out)
        return
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", out)
        return
    if isinstance(a, float) and isinstance(b, float):
        if a != b:
            out.append((abs(a - b), path))
        return
    if a != b:
        out.append((float("inf"), path))


changed_scenarios = []
worst = (0.0, "-")
total_fields = 0
for name in sorted(golden.SCENARIOS):
    cur = golden.capture(name, golden.SCENARIOS[name])
    opt_mod._multi_start_minimize = memo_msm
    try:
        fix = golden.capture(name, golden.SCENARIOS[name])
    finally:
        opt_mod._multi_start_minimize = _orig_msm
    out: list = []
    diff(cur, fix, name, out)
    if out:
        out.sort(reverse=True)
        changed_scenarios.append(name)
        total_fields += len(out)
        if out[0][0] > worst[0]:
            worst = (out[0][0], out[0][1])

d9lib.result("golden_scenarios", len(golden.SCENARIOS), "count")
d9lib.result("golden_scenarios_changed", len(changed_scenarios), "count")
d9lib.result("golden_fields_changed_at_precision6", total_fields, "count")
d9lib.result("golden_changed_names", ",".join(changed_scenarios) or "-", "labels")
d9lib.result("golden_max_abs_delta", worst[0], "unit")
d9lib.result("golden_max_delta_field", worst[1], "label")
d9lib.closing(1.0)
