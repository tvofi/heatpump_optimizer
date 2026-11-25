#!/usr/bin/env python3
# Metric: count of stored dicts (of 14 tried) on which FlowCurveBias.from_dict(d).as_dict() differs between the
#   baseline and the mutant; the restored learner's (bias_k, samples) is the compared value.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_19ac62540d0d5ee8.py
# EXPECTED RESULT inputs_tried=14 count
# EXPECTED RESULT differing_inputs=0 count     (equivalent: samples==0 returns cls() at line 238 in the baseline)
# EXPECTED RESULT zero_sample_restores_inert_baseline=1 count
# EXPECTED RESULT zero_sample_restores_inert_mutant=1 count
# EXPECTED RESULT positive_control_differing=3 count  (dropping line 237's guard instead moves the three zero-sample stores with bias != 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.flow_lift:FlowCurveBias.from_dict, line 232
#   `if not np.isfinite(bias) or samples < 0:`; reached from coordinator.py:4692 on store load.
# Perturbation: mutant 19ac62540d0d5ee8, `samples < 0` -> `samples <= 0`, applied in memory (the classmethod is
#   recompiled from its own source and patched onto the class for the mutant arm). Expected direction: none; the
#   samples == 0 case the edit adds already returns the same fresh learner two lines later.
# Inputs: samples in {-1, 0, 1, 7} x bias in {0.0, 4.5, -20.0}, plus bias nan, samples "0", samples 0.0 (float).
# Null control: the baseline against itself (0 by construction); positive control: the mutant plus line 237's
#   `samples == 0` guard removed, under which a zero-sample store with bias != 0 restores that bias in one arm only.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
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


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import inspect  # noqa: E402
import textwrap  # noqa: E402

from heatpump_optimizer import flow_lift as fl  # noqa: E402

OLD = "if not np.isfinite(bias) or samples < 0:"
NEW = "if not np.isfinite(bias) or samples <= 0:"
SRC = textwrap.dedent(inspect.getsource(fl.FlowCurveBias.from_dict.__func__))
assert SRC.count(OLD) == 1, "anchor line moved"


def compiled(src):
    ns = dict(fl.__dict__)
    exec(compile(src.replace("@classmethod\n", "", 1), fl.__file__, "exec"), ns)
    return ns["from_dict"]


MUT = compiled(SRC.replace(OLD, NEW, 1))
# positive control: baseline line 232 kept, the samples == 0 early return (line 237) removed
POS = compiled(SRC.replace("if samples == 0:", "if False:", 1))
INPUTS = [{"bias_k": b, "samples": s} for s in (-1, 0, 1, 7) for b in (0.0, 4.5, -20.0)]
INPUTS += [{"bias_k": float("nan"), "samples": 3}, {"bias_k": 4.5, "samples": 0.0}]


def restore(fn, d):
    return fn(fl.FlowCurveBias, d).as_dict()


def base(d):
    return fl.FlowCurveBias.from_dict(d).as_dict()


diff = sum(1 for d in INPUTS if restore(MUT, d) != base(d))
pos = sum(1 for d in INPUTS if restore(POS, d) != base(d))
zero = {"bias_k": 4.5, "samples": 0}
inert = {"bias_k": 0.0, "samples": 0}
print(f"RESULT inputs_tried={len(INPUTS)} count")
print(f"RESULT differing_inputs={diff} count")
print(f"RESULT zero_sample_restores_inert_baseline={int(base(zero) == inert)} count")
print(f"RESULT zero_sample_restores_inert_mutant={int(restore(MUT, zero) == inert)} count")
print(f"RESULT positive_control_differing={pos} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
