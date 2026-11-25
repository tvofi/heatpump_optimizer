#!/usr/bin/env python3
# Metric: the price-shape model (shape[0][0]) a live coordinator holds after HeatPumpOptimizerCoordinator._apply_learner_payloads restores a
#   learner snapshot (the drift-rollback / snapshot-restore path) whose price-shape model (shape[0][0]) differs from the fresh state.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_cf7be12db1a662c4.py
# EXPECTED RESULT price_shape00_baseline=1.3 ; price_shape00_mutant=1.0  (the snapshot is ignored)
# EXPECTED RESULT null_{non_dict_payload,empty,fresh_state}_delta=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._apply_learner_payloads
#   line 9613 (`if isinstance(prices, dict):`), on a live coordinator; the snapshot is built from a second coordinator's own as_dict()
#   producers (_learner_snapshot_payloads' shapes) with one field changed per learner.
# Perturbation: key cf7be12db1a662c4, `if isinstance(prices, dict):` -> `if False:` (GUARD_OFF), in memory: the method is recompiled from its own
#   source in the module namespace and called in place of the original for the mutant arm.
#   Direction: snapshot value restored -> fresh value kept (the restore silently drops this learner).
# Null control: a snapshot whose entries are not dicts, an empty snapshot, and a snapshot equal to the fresh state.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
logging.disable(logging.CRITICAL)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


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


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


CLS = co.HeatPumpOptimizerCoordinator


def snapshot():
    """A learner snapshot whose three restorable learners differ from a fresh coordinator's in one field each."""
    src = coord()
    p = src._price_model.as_dict()
    p["shapes"][0][0], p["days"][0] = 1.3, 5
    cf = src._comfort_learner.as_dict()
    cf["learned_weight"], cf["evidence"] = 8.0, 2.0
    d = src._defrost.as_dict()
    d["factors"][0][0], d["counts"][0][0] = 0.8, 5
    return {"price_model": p, "comfort": cf, "defrost": d}


def restored(fn, learners):
    c = coord()
    fn(c, learners)
    return {
        "price_shape00": round(float(c._price_learner.model.as_dict()["shapes"][0][0]), 6),
        "comfort_learned_weight": float(c._comfort_learner.as_dict()["learned_weight"]),
        "defrost_factor00": float(c._defrost.as_dict()["factors"][0][0]),
        "defrost_published": c._thermal_params.defrost_derate is c._defrost,
    }


def run(old, field):
    mut = recompile(CLS, "_apply_learner_payloads", old, "if False:")
    snap = snapshot()
    b, m = restored(CLS._apply_learner_payloads, snap), restored(mut, snap)
    print(f"RESULT {field}_baseline={b[field]}")
    print(f"RESULT {field}_mutant={m[field]}")
    print(f"RESULT fields_moved={sum(int(b[k] != m[k]) for k in b)} count ({ {k: (b[k], m[k]) for k in b if b[k] != m[k]} })")
    for name, learners in (("non_dict_payload", {k: None for k in snap}), ("empty", {}), ("fresh_state", {
            "price_model": coord()._price_model.as_dict(), "comfort": coord()._comfort_learner.as_dict(),
            "defrost": coord()._defrost.as_dict()})):
        bb, mm = restored(CLS._apply_learner_payloads, learners), restored(mut, learners)
        print(f"RESULT null_{name}_delta={sum(int(bb[k] != mm[k]) for k in bb if k != 'defrost_published')} count")


run("if isinstance(prices, dict):", "price_shape00")
tail()
