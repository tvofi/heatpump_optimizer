#!/usr/bin/env python3
# Metric: after feeding HeatPumpOptimizerCoordinator._observe_cop_health a sample sequence, the health CUSUM
#   statistic (Cusum.stat, the input the cop_degradation repair issue trips on) and the bucket's baseline COP
#   (entry[0], read by machine_score/machine_evidence at coordinator.py:10591-10596); key = those two delivered values.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_509893a173fa6a29.py
# Expected: baseline COP exactly 0.5 after N samples, then a 0.1 sample: the baseline does not judge (stat 0), the mutant does (stat > 0); null: baseline 0.6 / 0.4: moved 0. Exact to 1e-9 (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._observe_cop_health
#   (coordinator.py:9486), called from _learn_measured_cop at coordinator.py:5420.
# Perturbation: mutant 509893a173fa6a29 (CMP_BOUND) `if count >= COP_BASELINE_MIN_SAMPLES and baseline > 0.5:` -> `if count >= COP_BASELINE_MIN_SAMPLES and baseline >= 0.5:`, compiled in memory from the method's source.
# Inputs: SimpleNamespace coordinator (no _ctx) with the real Cusum(COP_HEALTH_THRESHOLD, COP_HEALTH_DRIFT, side=1),
#   flow_curve_cop off (so _watch_lift returns (1.0, False)), outdoor 0 degC (one bucket); dt_util.now and
#   ir.async_delete_issue patched; _raise_cop_issue counted. Sequences in SEQS: n warm-up samples of a COP then probes.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.const import (  # noqa: E402
    COP_BASELINE_MIN_SAMPLES as N, COP_HEALTH_DRIFT, COP_HEALTH_THRESHOLD)
from custom_components.heatpump_optimizer.drift import Cusum  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD, NEW = "if count >= COP_BASELINE_MIN_SAMPLES and baseline > 0.5:", "if count >= COP_BASELINE_MIN_SAMPLES and baseline >= 0.5:"


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._observe_cop_health)
NOW = datetime(2026, 1, 10, 12, tzinfo=timezone.utc)


def run(fn, seq):
    raised = []
    me = SimpleNamespace(
        _cop_baseline={}, _cop_health_cusum=Cusum(threshold=COP_HEALTH_THRESHOLD, drift=COP_HEALTH_DRIFT, side=1),
        _thermal_params=SimpleNamespace(flow_curve_cop=False), _config=SimpleNamespace(),
        _current_state=SimpleNamespace(outdoor_temperature=0.0), hass=None,
        _raise_cop_issue=lambda b: raised.append(b),
    )
    with mock.patch.object(co.dt_util, "now", lambda: NOW), mock.patch.object(co.ir, "async_delete_issue", lambda *a: None):
        for cop in seq:
            fn(me, float(cop))
    entry = me._cop_baseline[(0, False)]
    return round(me._cop_health_cusum.stat, 9), round(entry[0], 9), int(entry[1]), len(raised)


SEQS = {
    "baseline_0p5_then_drop": [0.5] * N + [0.1],
    "baseline_0p5_then_three_drops": [0.5] * N + [0.1] * 3,
    "baseline_0p5_then_equal": [0.5] * N + [0.5],
}
NULLS = {
    "baseline_0p6_then_drop": [0.6] * N + [0.1],
    "baseline_0p4_then_drop": [0.4] * N + [0.1],
}
moved = 0
for name, seq in SEQS.items():
    b, m = run(CLS._observe_cop_health, seq), run(MUT, seq)
    moved += int(b != m)
    print(f"RESULT {name}_baseline=stat {b[0]} baseline_cop {b[1]} count {b[2]} issues {b[3]}")
    print(f"RESULT {name}_mutant=stat {m[0]} baseline_cop {m[1]} count {m[2]} issues {m[3]}")
print(f"RESULT seqs_moved={moved} count of {len(SEQS)}")
print(f"RESULT null_moved={sum(int(run(CLS._observe_cop_health, s) != run(MUT, s)) for s in NULLS.values())} count of {len(NULLS)}")
