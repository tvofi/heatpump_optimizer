"""V2 (independent) for D3-s2-01 and D3-s2-02: an executed differential over D3-s2's RECORDED
mutants (no pool, no pre-screen, no gate run).

Metric A (suite census): every call in tests/features.py and tests/finite_boundary.py of
FlowCurveBias/PeakTracker/PriceShapeModel.from_dict whose first argument evaluates from literals
(float('nan') and module constants allowed), fed to the parser twice -- the production module and
the same source with the recorded one-line mutant applied in memory (tools/audit/round9/D3/s2/
mutload.pair) -- counting suite payloads on which the two restores differ (as_dict(), NaN-aware).
Metric B (reach through the store boundary): my payload grid (non-finite spellings as strings and
floats, 1e400, negative counts, a learned positive variance, in-domain controls), each fed
(a) directly and (b) as production QuarantiningStore.async_load returns it after a JSON store
round trip (the boundary every production caller of these parsers loads through:
coordinator.py _async_load_thermal_learning / _async_load_price_model / _async_load_accuracy),
counting payloads whose restores differ between production and mutant.
Mutants (recorded, storeguards.json / pool.json): S34(=M31) flow_lift.py:210, S05 tariff.py:402,
S17 price_model.py:324, S18 price_model.py:349, S19 price_model.py:368; positive controls S04
tariff.py:393 and S08 tariff.py:458 (recorded KILLED by features).
Count key: parser output (as_dict) under production vs mutant.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/verify-v2/leads_store_guard_reach.py
Expected (exact counts): census_suite_payloads=10 (2 unresolved: features.py:11443 and the helper
parameter at :11553); suite_diverging 0 for S34, S05, S17, S18, S19 and 1 of 4 (S04), 2 of 4 (S08); grid direct/through-store diverging: S34 7/9 -> 2/9
(the two negative-count payloads), S05 6/8 -> 0/8, S17 4/10 -> 0/10, S18 2/10 -> 0/10,
S19 3/10 -> 2/10, S04 and S08 0/8 on this grid.
Perturbation: the mutant itself (orig vs orig arm, --null) -> every count 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import asyncio
import json
import math
import resource
import sys
import time

T0 = (time.process_time(), time.thread_time())
sys.path.insert(0, "tools/audit/round9/D3/s2")
import mutload  # noqa: E402  (inserts tests/hastub, tests, custom_components)
import numpy as np  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from heatpump_optimizer import flow_lift, price_model, tariff  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore  # noqa: E402

NULL = "--null" in sys.argv
MUTANTS = {"S34": "FlowCurveBias", "S05": "PeakTracker", "S17": "PriceShapeModel",
           "S18": "PriceShapeModel", "S19": "PriceShapeModel", "S04": "PeakTracker", "S08": "PeakTracker"}
CLASSES = {"FlowCurveBias", "PeakTracker", "PriceShapeModel"}


def canon(obj):
    def enc(x):
        if isinstance(x, float) and not math.isfinite(x):
            return repr(x)
        if isinstance(x, dict):
            return {k: enc(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [enc(v) for v in x]
        if isinstance(x, np.ndarray):
            return enc(x.tolist())
        return x
    try:
        return json.dumps(enc(obj.as_dict()), sort_keys=True, default=repr)
    except Exception as err:  # noqa: BLE001
        return f"as_dict raised {type(err).__name__}"


def restore(mod, cls, payload):
    try:
        return canon(getattr(mod, cls).from_dict(_copy(payload)))
    except Exception as err:  # noqa: BLE001
        return f"from_dict raised {type(err).__name__}"


def _copy(p):
    import copy
    return copy.deepcopy(p)


class _AnyMod:
    def __getattr__(self, name):
        for m in (price_model, tariff, flow_lift):
            if hasattr(m, name):
                return getattr(m, name)
        raise AttributeError(name)


def census_payloads():
    out = []
    unresolved = 0
    for path in ("tests/features.py", "tests/finite_boundary.py"):
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "from_dict" and node.args):
                continue
            recv = node.func.value
            name = recv.attr if isinstance(recv, ast.Attribute) else getattr(recv, "id", "")
            if name not in CLASSES:
                continue
            arg = node.args[0]
            names = {n.id for n in ast.walk(arg) if isinstance(n, ast.Name)}
            env = {"__builtins__": {}, "float": float, "int": int, "math": math, "np": np}
            for n in names - set(env):
                env[n] = _AnyMod()
            try:
                val = eval(compile(ast.Expression(arg), path, "eval"), env)  # noqa: S307 - test literals
            except Exception:  # noqa: BLE001
                unresolved += 1
                continue
            if isinstance(val, _AnyMod):  # a bare variable (e.g. a helper's parameter), not a payload
                unresolved += 1
                continue
            out.append((name, f"{path}:{node.lineno}", val))
    return out, unresolved


def through_store(payload):
    storage._DISK["v2_reach"] = json.dumps(payload)  # the stub writes NaN/Infinity tokens as json does

    async def go():
        return await QuarantiningStore(None, 1, "v2_reach").async_load()
    return asyncio.run(go())


NAN, INF = float("nan"), float("inf")
GRID = {
    "FlowCurveBias": [
        {"bias_k": "nan", "samples": 4}, {"bias_k": "Infinity", "samples": 4}, {"bias_k": "1e400", "samples": 9},
        {"bias_k": NAN, "samples": 7}, {"bias_k": -INF, "samples": 7},
        {"bias_k": 2.5, "samples": -1}, {"bias_k": -4.0, "samples": -5},
        {"bias_k": 1.5, "samples": 6}, {"bias_k": -3.0, "samples": 20}],
    "PeakTracker": [
        dict(month="2026-02", peaks=[4.0, 3.0], peak_days=["2026-02-02", "2026-02-03"],
             window_key="2026-02-10T07:00:00|60", window_sum=8.0, window_samples=4, window_factor=wf)
        for wf in ("nan", "inf", "-Infinity", "1e400", NAN, INF, 0.5, 1.0)],
    "PriceShapeModel": (
        [{"shapes": [[1.0] * 23 + [bad], [1.0] * 24], "days": [30, 12]} for bad in ("nan", "inf", NAN, "1e400")]
        + [{"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12],
            "quarter_factors": [[1.0] * 95 + [bad], [1.0] * 96], "quarter_days": [20, 8]} for bad in ("nan", INF)]
        + [{"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12],
            "residual_var": [[v] * 24, [0.02] * 24]} for v in ("nan", -0.01, 0.03)]
        + [{"shapes": [[0.9 + 0.01 * h for h in range(24)], [1.0] * 24], "days": [30, 12]}]),
}


def main():
    suite, unresolved = census_payloads()
    print(f"RESULT census_suite_payloads={len(suite)} unresolved_non_literal={unresolved}")
    for mid, cls in MUTANTS.items():
        o, m, rec = mutload.pair(mid)
        if NULL:
            m = o
        orig_mod = {"FlowCurveBias": flow_lift, "PeakTracker": tariff, "PriceShapeModel": price_model}[cls]
        assert o is orig_mod
        mine = [p for c, _, p in suite if c == cls]
        div_suite = sum(restore(o, cls, p) != restore(m, cls, p) for p in mine)
        direct = via_store = 0
        for p in GRID[cls]:
            direct += restore(o, cls, p) != restore(m, cls, p)
            sp = through_store(p)
            if isinstance(sp, dict):
                via_store += restore(o, cls, sp) != restore(m, cls, sp)
        print(f"RESULT {mid} {rec['file'].split('/')[-1]}:{rec['line']} suite_diverging={div_suite} of_{len(mine)} "
              f"grid_direct_diverging={direct} of_{len(GRID[cls])} grid_through_store_diverging={via_store} of_{len(GRID[cls])}")
    print(f"RESULT null_arm={int(NULL)}")
    pc, tc = time.process_time() - T0[0], time.thread_time() - T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")


main()
