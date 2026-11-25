#!/usr/bin/env python3
# Metric: optimizer._power_fraction(1.10 kW) on a pump whose modulation band is 0.15 kW (min 1.00, max 1.15 kW), i.e.
#   a band between the baseline threshold 0.1 and the mutant's 0.2.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_23b144fb9583c5c7.py
# EXPECTED RESULT fraction_baseline=0.6667  (graded inside the band: (1.10-1.00)/0.15)
# EXPECTED RESULT fraction_mutant=0.9565  (graded as fixed-speed: 1.10/1.15)
# EXPECTED RESULT abs_delta=0.2899 (tolerance 1e-3)
# EXPECTED RESULT null_abs_delta=0.0  (band 0.5 kW and band 0.0 kW, both arms take the same branch)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_power_fraction (reads _MIN_MODULATION_BAND_KW,
#   optimizer.py:2156, at line 2170); the one normalisation the setpoint, displace and action sites share.
# Perturbation: `_MIN_MODULATION_BAND_KW = 0.1` -> `_MIN_MODULATION_BAND_KW = 0.2` (CONST 23b144fb9583c5c7), applied in memory
#   with mock.patch.object on the module constant (read at call time). Direction: fraction rises for bands in [0.1, 0.2).
# Null control: band 0.5 kW (min 1.0, max 1.5; both modulating) and band 0 (fixed speed 1.0/1.0; both fixed-speed).
# Inputs tried: bands 0.10, 0.15, 0.19 kW at mid-band power; the two null bands.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
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
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
from custom_components.heatpump_optimizer import optimizer as O  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

assert O._MIN_MODULATION_BAND_KW == 0.1


def both(pmin, pmax, power):
    p = ThermalParameters(min_electrical_power=pmin, max_electrical_power=pmax)
    b = O._power_fraction(power, p)
    with mock.patch.object(O, "_MIN_MODULATION_BAND_KW", 0.2):
        m = O._power_fraction(power, p)
    return b, m


b, m = both(1.00, 1.15, 1.10)
moved_bands = sum(int(abs(x - y) > 1e-9) for x, y in (both(1.0, 1.10, 1.05), both(1.0, 1.15, 1.10), both(1.0, 1.19, 1.10)))
n1, n2 = both(1.0, 1.5, 1.25), both(1.0, 1.0, 1.0)
print(f"RESULT fraction_baseline={b:.4f}")
print(f"RESULT fraction_mutant={m:.4f}")
print(f"RESULT abs_delta={abs(b - m):.4f}")
print(f"RESULT bands_moved={moved_bands} of 3 count")
print(f"RESULT null_abs_delta={abs(n1[0] - n1[1]) + abs(n2[0] - n2[1])}")
tail()
