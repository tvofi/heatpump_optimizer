"""Shared helper: load thermal_model with ONE line replaced, in memory (nothing on disk changes)."""
import os, sys, importlib.util, itertools
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
def root():
    h = Path(__file__).resolve()
    for c in h.parents:
        if (c/"custom_components"/"heatpump_optimizer"/"manifest.json").is_file(): return c
    raise RuntimeError("no root")
ROOT = root(); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"tests"/"hastub"))
from custom_components.heatpump_optimizer import thermal_model as base  # noqa
F = ROOT/"custom_components"/"heatpump_optimizer"/"thermal_model.py"
def mutant(line, old, new):
    lines = F.read_text().split("\n")
    assert lines[line-1] == old, (lines[line-1], old)
    lines[line-1] = new
    name = "custom_components.heatpump_optimizer.thermal_model_mut"
    spec = importlib.util.spec_from_file_location(name, F)
    m = importlib.util.module_from_spec(spec); m.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = m
    exec(compile("\n".join(lines), str(F), "exec"), m.__dict__)
    return m
def vz_inputs():
    """Sweep of _valve_two_zone_delivery inputs incl. boundary values."""
    P = base.ThermalParameters
    for tb, tw, tu, ts in itertools.product((15.0, 21.0, 30.0, 45.0, 60.0), (None, 15.0, 30.0, 50.0, 70.0), (19.0, 21.0), (21.0, 24.0)):
        st = base.ThermalState(upper_floor_temperature=tu, slab_temperature=ts, buffer_tank_temperature=tb, wood_tank_temperature=tw)
        for tp, loss, ext, dt, tt in itertools.product((0.0, 0.5, 3.0, 8.0), (0.0, 0.1, 1.0, 5.0), (0.0, 2.0, 10.0), (0.0, 1e-9, 0.25, 1.0), (False, True)):
            if tt and tw is None: continue
            yield P(), st, tp, ext, loss, None, 0.0, 0.2, dt, tt
import numpy as np, warnings
warnings.simplefilter("ignore")
def _norm(x):
    if isinstance(x, np.ndarray): return tuple(repr(float(v)) for v in x.ravel())
    if isinstance(x, tuple): return tuple(_norm(v) for v in x)
    if isinstance(x, float): return repr(x)
    return x
def run(fn, args):
    try:
        with np.errstate(all="ignore"): return _norm(fn(*args))
    except Exception as e: return ("EXC", type(e).__name__)
def ws_inputs():
    """_wood_share_vec(wood, hp, flow_set, floor[, margin]) grid incl. ties wood==flow, hp==flow, flow==floor, margin 0."""
    v = (10.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0)
    for fs in (25.0, 35.0, 45.0):
        for w, h, fl in itertools.product(v, v, (10.0, 20.0, 25.0, 35.0, 45.0)):
            for mg in (None, 0.0, 2.0):
                a = [np.array([w]), np.array([h]), fs, np.array([fl])]
                if mg is not None: a.append(mg)
                yield tuple(a)
def dp_inputs():
    for e in (-1.0, 0.0, 1e-12, 1e-9, 1e-3, 1.0, 6.112, 12.0, 23.4, 50.0):
        yield (e,)
def dc_inputs():
    for d, w, sp, inl in itertools.product((-2.0, -1e-9, 0.0, 1e-9, 0.5, 3.0), (5.0, 10.0, 30.0, 60.0, 80.0), (45.0, 55.0, 60.0), (5.0, 10.0, 55.0)):
        yield (d, w, sp, inl)
