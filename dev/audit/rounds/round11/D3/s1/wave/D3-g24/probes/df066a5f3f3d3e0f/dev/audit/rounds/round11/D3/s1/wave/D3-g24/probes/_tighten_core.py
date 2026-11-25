# Shared driver of box D3-g24's four _tighten_buffer_caps probes (not a harness itself): calls
# HeatPumpOptimizer._tighten_buffer_caps with the model's simulate_trajectory answering a chosen
# per-step `refused` vector (the only input the mutated lines 5120-5145 read besides the caps), and
# compares the outcome per arm: the returned `changed`, the mutated power_caps, the count the
# "Buffer cap tightened %d step(s)" debug line logs, or the exception raised.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import logging  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from unittest import mock  # noqa: E402
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

N = 4
STATE = ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0)
WEATHER = SimpleNamespace(outdoor_temps=np.full(N, -5.0), humidity=None)
SCHED = np.array([2.0, 2.0, 2.0, 2.0])


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.counts = []

    def emit(self, rec):
        if rec.msg.startswith("Buffer cap tightened"):
            self.counts.append(rec.args[0])


def _call(fn, refused, caps):
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
    caps = np.array(caps, dtype=float)
    out = (None, None, None, None, None, refused, None)
    h = _Count()
    lg = optimizer._LOGGER
    old_level = lg.level
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    try:
        with mock.patch.object(opt.model, "simulate_trajectory", lambda **kw: out):
            ch = fn(opt, WEATHER, STATE, SimpleNamespace(power_schedule=SCHED), caps, 0.25,
                    valve_targets=None, start_hour=12.0)
    except Exception as e:
        return ("raise", type(e).__name__)
    finally:
        lg.removeHandler(h)
        lg.setLevel(old_level)
    return ("ok", bool(ch), caps.tolist(), h.counts)


def new_cap_of(step_refused):
    """The cap the baseline would set at a step refusing `step_refused` kW (caps start huge)."""
    r = _call(HeatPumpOptimizer._tighten_buffer_caps, np.array([step_refused, 0.0, 0.0, 0.0]), [1e9] * N)
    return r[2][0]


def tie_cap(new_cap):
    """A cap c with float(c) - 1e-9 == new_cap exactly (the <-vs-<= tie of line 5139), or None."""
    c = new_cap + 1e-9
    for _ in range(64):
        d = c - 1e-9
        if d == new_cap:
            return c
        c = np.nextafter(c, np.inf) if d < new_cap else np.nextafter(c, -np.inf)
    return None


def cases():
    nc = new_cap_of(0.5)
    tc = tie_cap(nc)
    return [
        ("refused_none", None, [3.0] * N),
        ("refused_zero", np.zeros(N), [3.0] * N),
        ("refused_tie_1e-9_alone", np.array([1e-9, 0, 0, 0]), [3.0] * N),
        ("refused_tie_1e-9_plus_real", np.array([1e-9, 0.5, 0, 0]), [3.0] * N),
        ("refused_just_above_1e-9", np.array([np.nextafter(1e-9, 1), 0, 0, 0]), [3.0] * N),
        ("refused_just_below_1e-9", np.array([np.nextafter(1e-9, 0), 0.5, 0, 0]), [3.0] * N),
        ("refused_real_cap_far_above", np.array([0.5, 0, 0, 0]), [3.0] * N),
        ("refused_real_cap_already_below", np.array([0.5, 0, 0, 0]), [0.1] * N),
        ("refused_real_cap_tie(new_cap==cap-1e-9)", np.array([0.5, 0, 0, 0]), [tc if tc is not None else 3.0] + [3.0] * 3),
        ("refused_real_cap_equal_new_cap", np.array([0.5, 0, 0, 0]), [nc] + [3.0] * 3),
        ("refused_nan", np.array([np.nan, 0.5, 0, 0]), [3.0] * N),
        ("refused_negative", np.array([-0.5, 0.5, 0, 0]), [3.0] * N),
    ], nc, tc


def run(old, new, label):
    base = HeatPumpOptimizer._tighten_buffer_caps
    mut = _mutlib.mutated(HeatPumpOptimizer, "_tighten_buffer_caps", old, new, optimizer)
    cs, nc, tc = cases()
    print(f"INFO new_cap(refused=0.5)={nc!r} tie_cap={tc!r}")
    moved = 0
    for name, refused, caps in cs:
        b, m = _call(base, refused, caps), _call(mut, refused, caps)
        d = int(repr(b) != repr(m))
        moved += d
        print(f"CASE {name}: baseline={b} mutant={m} moved={d}")
    print(f"RESULT {label}_cases_moved={moved} count")
    print(f"RESULT {label}_cases_tried={len(cs)} count")


def reach_refused_type():
    """What the real ThermalModel.simulate_trajectory returns in the `refused` slot (default params)."""
    from custom_components.heatpump_optimizer.thermal_model import WeatherSeries
    m = ThermalModel(ThermalParameters())
    w = WeatherSeries(outdoor_temps=np.full(N, -5.0))
    out = m.simulate_trajectory(initial_state=STATE, power_schedule=SCHED, weather=w, dt_hours=0.25)
    r = out[5]
    print(f"RESULT reach_refused_is_none={int(r is None)} count  (type {type(r).__name__})")
