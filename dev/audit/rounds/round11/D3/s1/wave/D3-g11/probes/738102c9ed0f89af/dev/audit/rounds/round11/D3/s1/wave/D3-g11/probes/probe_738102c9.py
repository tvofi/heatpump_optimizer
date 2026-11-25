#!/usr/bin/env python3
# Metric: the outcome of one coordinator._fold_flow_lift call with a fresh 45 degC supply reading when the weather
#   curve is unusable (curve_supply_temp returns None: a non-finite outdoor temperature): "ok" plus the bias sample
#   count, or the exception type the call raises into its caller _record_accuracy (coordinator.py:10011).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_738102c9.py
# Expected: RESULT outdoor_nan_baseline=ok samples=0, mutant=TypeError; null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_fold_flow_lift (line 984, `    if curve is None:`),
#   with the real flow_lift.curve_supply_temp and FlowCurveBias.observe.
# Perturbation: mutant 738102c9ed0f89af, `if curve is None:` -> `if False:`, in memory (recompiled from its own source in
#   the module namespace). The coordinator is a SimpleNamespace carrying the attributes the function reads; the gates
#   before the curve (draw floor, learning freeze, COP-fold block, meter attribution) are stubbed open.
#   Direction: ok -> TypeError (np.isfinite(None) in FlowCurveBias.observe), which aborts the rest of _record_accuracy's
#   per-cycle block for that cycle.
# Null control: a finite outdoor temperature (curve finite), where both arms fold one sample identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

import time
from types import SimpleNamespace
from unittest import mock
from custom_components.heatpump_optimizer.flow_lift import FlowCurveBias

MUT = mutate(co._fold_flow_lift, "if curve is None:", "if False:")


class _Model:
    def flow_target_for_indoor(self, indoor, outdoor):
        return 35.0 + 0.5 * (indoor - outdoor)


def drive(fn, outdoor):
    bias = FlowCurveBias()
    bias.observe_temps(45.0, 38.0)
    coord = SimpleNamespace(
        _flow_bias=bias, _thermal_params=None, _commanded_power=lambda: 3.0,
        _accuracy=SimpleNamespace(draw=None), _learning_frozen=lambda key: None,
        _commanded_split=lambda: None, _COP_CURVE_SHARE=0.5, _thermal_model=_Model(),
        _current_state=SimpleNamespace(outdoor_temperature=outdoor), target_temperature=21.0,
    )
    meter = SimpleNamespace(attribution=lambda split: SimpleNamespace(space=1.0, dhw=0.0))
    with mock.patch.object(co.draw_range, "power_floor_kw", lambda draw, params: 0.0), \
         mock.patch.object(co, "_cop_fold_blocked", lambda c: False), \
         mock.patch.object(co.heat_energy, "meter_of", lambda c: meter), \
         mock.patch.object(co.heat_energy, "dhw_share", lambda a: 0.0):
        g = fn.__globals__
        saved = {k: g[k] for k in ("_cop_fold_blocked",)}
        g["_cop_fold_blocked"] = lambda c: False  # the mutant's own namespace copy
        try:
            fn(coord, None)
            return f"ok samples={bias.samples}"
        except Exception as err:  # noqa: BLE001
            return type(err).__name__
        finally:
            g.update(saved)


t0, t1 = time.process_time(), time.thread_time()
for name, out in {"outdoor_nan": float("nan"), "outdoor_inf": float("inf")}.items():
    print(f"RESULT {name}_baseline={drive(co._fold_flow_lift, out)} mutant={drive(MUT, out)}")
print(f"RESULT null_moved={int(drive(co._fold_flow_lift, 2.0) != drive(MUT, 2.0))} count  "
      f"(finite outdoor: {drive(co._fold_flow_lift, 2.0)})")
tail_results(t0, t1)
