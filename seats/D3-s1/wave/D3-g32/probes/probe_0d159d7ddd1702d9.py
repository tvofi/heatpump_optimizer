#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 0d159d7ddd1702d9.
# Metric: guessed price tail extend_price_series returns for known [1,2,3] SEK/kWh on a fresh (zero-confidence) PriceShapeModel.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d159d7ddd1702d9.py   (from the repository root)
# EXPECTED: guessed_tail_baseline=[3.0, 3.0, 3.0] (flat repeat of the last price); guessed_tail_mutant=[2.0, 2.0, 2.0] (known-window mean); guessed_tail_delta=1.0000; null_delta=0; flat_known_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:extend_price_series, line 544.
# Perturbation: key 0d159d7ddd1702d9 (CMP_BOUND) `model.confidence(when) <= 0.0` -> `< 0.0`. Direction: the tail moves from last_known to mean(known)/shape_mean; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: model=None (both arms flat-repeat) and a constant known window (mean == last).
# Counts are exact (no timing); thread_factor/load1/swapins are printed per the harness contract.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
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
_T0 = (time.process_time(), time.thread_time())


def mutate(owner, name, old, new):
    """Re-compile ``owner.name`` from its own source with the one-line mutant applied (in memory)."""
    fn = getattr(owner, name)
    mod = sys.modules[fn.__module__]
    src = inspect.getsource(fn)  # the anchor carries the file's own indentation
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(mod.__dict__)
    exec(compile(textwrap.dedent(src.replace(old, new, 1)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import price_model as pm

OLD = "        if model is None or model.confidence(when) <= 0.0:"
NEW = "        if model is None or model.confidence(when) < 0.0:"
mut = mutate(pm, "extend_price_series", OLD, NEW)
t0 = datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)  # a Wednesday
times = [t0 + timedelta(hours=i) for i in range(6)]
known = [1.0, 2.0, 3.0]


def tail_prices(fn, model):
    prices, mask, sigma = fn(list(known), 6, times, model)
    return [float(x) for x in prices[3:]], [float(s) for s in sigma[3:]]


fresh = pm.PriceShapeModel()  # nothing learned: confidence 0.0 on every hour
assert fresh.confidence(times[3]) == 0.0
b, bs = tail_prices(pm.extend_price_series, fresh)
m, ms = tail_prices(mut, fresh)
print(f"RESULT guessed_tail_baseline={b}")
print(f"RESULT guessed_tail_mutant={m}")
print(f"RESULT guessed_tail_delta={max(abs(x - y) for x, y in zip(b, m)):.4f} SEK/kWh")
print(f"RESULT sigma_delta={max(abs(x - y) for x, y in zip(bs, ms)):.4f} SEK/kWh")
# null control: no model at all, where both arms take the flat repeat
nb, _ = tail_prices(pm.extend_price_series, None)
nm, _ = tail_prices(mut, None)
print(f"RESULT null_delta={max(abs(x - y) for x, y in zip(nb, nm)):.4f} SEK/kWh")
# null control 2: a constant known window, where mean == last price
known = [2.0, 2.0, 2.0]
cb, _ = tail_prices(pm.extend_price_series, fresh)
cm, _ = tail_prices(mut, fresh)
print(f"RESULT flat_known_delta={max(abs(x - y) for x, y in zip(cb, cm)):.4f} SEK/kWh")
tail()
