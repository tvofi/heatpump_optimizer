#!/usr/bin/env python3
"""D3-s1 M3 (T2 survivor R10-C2 M31): the k <= 0 guard of tariff._smooth_topk_sum is unpinned.

Mutant (R10-C2 M31, key d931ab195b940b0c): tariff.py:744
    `if x.size == 0 or k <= 0:`  ->  `if x.size == 0 or k < 0:`
It SURVIVED the full GATE_SCOPE=full GOLDEN_MODE=drift gate (state/gates/d931ab195b940b0c.json).

Metric (one line): soft_k0 = tariff._smooth_topk_sum(X, 0, _PEAK_SMOOTH_TAU) on a fixed
four-way peak plateau X (kW); the documented contract (k <= 0 -> 0.0) gives 0.0.
Count key: the value the production symbol delivers for k = 0, never the input.

Second number (reach): prod_k0 = tariff.peak_cost_smooth(...) with bill.peaks_averaged = 0
minus the same with peaks_averaged = 1; 0.0 means the production caller clamps k to 1
(tariff.py:982 `k = max(1, min(int(bill.peaks_averaged), excess.size))`) before
_smooth_topk_sum is reached, so the guard at 744 is not reachable with k <= 0 from the
solver path; the gap is an unpinned contract on a helper, not a wrong bill.

Instrumented symbols: custom_components/heatpump_optimizer/tariff.py:_smooth_topk_sum and
tariff.py:peak_cost_smooth (-> _peak_charge -> _plateau_aware_topk_sum).
Perturbation: --mutant loads tariff.py with the M31 line applied (in memory, private module
name; no file is written). Direction: soft_k0 up (0.0 -> the top-1 soft sum, > 0).
Null control: soft_k1 (k = 1) is identical in both arms; prod_k0 stays 0.0 in both arms.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/t3_m31_topk_k0.py [--mutant]
Expected: baseline soft_k0=0.0; --mutant soft_k0>0. Exact values (contention-immune).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
SRC = ROOT / "custom_components/heatpump_optimizer/tariff.py"
OLD = "    if x.size == 0 or k <= 0:"
NEW = "    if x.size == 0 or k < 0:"


def load(mutant: bool):
    import custom_components.heatpump_optimizer  # noqa: F401  (package for relative imports)

    text = SRC.read_text()
    if mutant:
        lines = text.split("\n")
        assert lines[743] == OLD, f"line 744 is {lines[743]!r}, not the M31 site"
        lines[743] = NEW
        text = "\n".join(lines)
    name = "custom_components.heatpump_optimizer._d3s1_tariff_" + ("m31" if mutant else "base")
    spec = importlib.util.spec_from_loader(name, loader=None, origin=str(SRC))
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    mod.__file__ = str(SRC)
    sys.modules[name] = mod
    exec(compile(text, str(SRC), "exec"), mod.__dict__)
    return mod


def bill_with(t, peaks):
    import dataclasses
    import inspect

    params = inspect.signature(t.PeakBilling).parameters
    kw = {}
    for p in params.values():
        if p.name == "peaks_averaged":
            kw[p.name] = peaks
        elif p.name == "price_per_kw":
            kw[p.name] = 50.0
        elif p.default is inspect.Parameter.empty:
            raise SystemExit(f"REFUSE PeakBilling needs {p.name}; harness cannot build it")
    return t.PeakBilling(**kw) if not dataclasses.is_dataclass(t.PeakBilling) or True else None


def main() -> None:
    mutant = "--mutant" in sys.argv
    t = load(mutant)
    x = np.array([1.0, 3.0, 3.0, 3.0, 3.0, 2.0, 0.5, 1.5])
    tau = t._PEAK_SMOOTH_TAU
    soft_k0 = float(t._smooth_topk_sum(x, 0, tau))
    soft_km1 = float(t._smooth_topk_sum(x, -1, tau))
    soft_k1 = float(t._smooth_topk_sum(x, 1, tau))
    print(f"RESULT arm={'mutant' if mutant else 'baseline'}")
    print(f"RESULT soft_k0={soft_k0!r} kW")
    print(f"RESULT soft_km1={soft_km1!r} kW")
    print(f"RESULT soft_k1={soft_k1!r} kW (null control: equal in both arms)")
    try:
        total = np.zeros_like(x) + x
        base = np.zeros_like(x)
        c0 = float(t.peak_cost_smooth(total, base, bill_with(t, 0)))
        c1 = float(t.peak_cost_smooth(total, base, bill_with(t, 1)))
        print(f"RESULT prod_k0_minus_k1={c0 - c1!r} (0.0: production clamps k to >= 1 before line 744)")
    except SystemExit as e:
        print(str(e))
    except Exception as e:  # report, do not hide, a signature mismatch
        print(f"RESULT prod_k0_minus_k1=ERROR {type(e).__name__}: {e}")
    print("RESULT thread_factor=1.0")


if __name__ == "__main__":
    main()
