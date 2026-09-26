"""D9 verify-v1 (round 9), finding D9-s1-01: bit parity and per-call cost of
the production per-row HeatPumpOptimizer._comfort_terms_batch against an
independently written axis=1 twin, over batch shapes and memory layouts the
finder did not test (48 h horizon, odd n, Fortran order, offset views).

Metric: (a) count of float64 values where production and twin differ bitwise
(view as int64), over every shape x layout x zone mode; (b) thread CPU per
call, production over twin, B=96 rows, n=96 steps (ratio).
Count key: the (penalty, comfort) arrays the production method RETURNS.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/verify-v1/comfort_parity.py
  (SIMD attack, numpy 2.4 group names: prefix NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR" (AVX2 dispatch), or add X86_V3 (baseline only))
Perturbation: --perturb swaps the twin's axis=1 reductions for a reversed-row
sum (a different summation order); mismatches must go UP from 0.
Expected: mismatched_production_shape_n96_C=0 (exact) and 0 on every C, offset3, shift1 cell;
F-order cells mismatch (3659 total here: axis=1 over a column-major batch is
not the per-row pairwise sum); prod_over_twin ~14x (provisional, +-30 %).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import platform
import sys
import time
from types import SimpleNamespace

for _p in ("tests", "tests/hastub", "custom_components"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as O  # noqa: E402

PROD = O.HeatPumpOptimizer._comfort_terms_batch
PERTURB = False


def rsum(a):
    return np.sum(a[:, ::-1], axis=1) if PERTURB else np.sum(a, axis=1)


def twin(self, room, upper, lower, target, tmin, tmax, band):
    w = self.config.comfort_weight
    if self.model.params.two_zone_enabled:
        u, l = upper[:, 1:], lower[:, 1:]
        a, b = np.maximum(0, tmin - u), np.maximum(0, u - tmax)
        c, d = np.maximum(0, tmin - l), np.maximum(0, l - tmax)
        pen = 0.5 * w * (rsum(a ** 2) * 10.0 + rsum(b ** 2) * 5.0
                         + rsum(c ** 2) * 10.0 + rsum(d ** 2) * 5.0
                         + (rsum(a) + rsum(c)) * O._COMFORT_FLOOR_L1)
        com = O._COMFORT_PULL_TWO_ZONE * w * (
            rsum(((u - target) / band) ** 2) + rsum(((l - target) / band) ** 2))
        return pen, com
    r = room[:, 1:]
    a, b = np.maximum(0, tmin - r), np.maximum(0, r - tmax)
    pen = w * (rsum(a ** 2) * 10.0 + rsum(b ** 2) * 5.0 + rsum(a) * O._COMFORT_FLOOR_L1)
    com = O._COMFORT_PULL_SINGLE_ZONE * w * rsum(((r - target) / band) ** 2)
    return pen, com


def fake(two_zone):
    return SimpleNamespace(config=SimpleNamespace(comfort_weight=5.0),
                           model=SimpleNamespace(params=SimpleNamespace(two_zone_enabled=two_zone)))


def layouts(arr):
    yield "C", np.ascontiguousarray(arr)
    yield "F", np.asfortranarray(arr)
    big = np.empty((arr.shape[0], arr.shape[1] + 3))
    big[:, 3:] = arr
    yield "offset3", big[:, 3:]
    raw = np.empty(arr.size + 1)
    v = raw[1:].reshape(arr.shape)  # 8-byte-misaligned-for-64B base
    v[...] = arr
    yield "shift1", v


def main():
    global PERTURB
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()
    PERTURB = args.perturb
    rng = np.random.default_rng(9)
    p0, t0 = time.process_time(), time.thread_time()
    mism = values = cases = 0
    cell = {}
    for n in (96, 192, 97, 47, 288):
        for B in (96, 193, 1):
            base = 20.0 + rng.normal(0, 1.5, (3, B, n + 1))
            tgt = 21.0 + rng.normal(0, 0.3, n)
            tmin, tmax = tgt - 1.0 + rng.normal(0, .1, n), tgt + 2.0
            band = np.full(n, 1.0) + rng.random(n)
            for tz in (False, True):
                for j in range(4):
                    room, upper, lower = (list(layouts(base[k]))[j][1] for k in range(3))
                    self = fake(tz)
                    a = PROD(self, room, upper, lower, tgt, tmin, tmax, band)
                    b = twin(self, room, upper, lower, tgt, tmin, tmax, band)
                    m = 0
                    for x, y in zip(a, b):
                        m += int(np.count_nonzero(x.view(np.int64) != y.view(np.int64)))
                        values += x.size
                    mism += m
                    key = f"n{n}.{('C', 'F', 'offset3', 'shift1')[j]}"
                    cell[key] = cell.get(key, 0) + m
                    cases += 1
    print(f"RESULT cases={cases} count")
    print(f"RESULT values_compared={values} count")
    print(f"RESULT mismatched_values={mism} values (exact)")
    for k, v in sorted(cell.items()):
        print(f"RESULT mismatched.{k}={v} values (exact)")
    n96c = cell.get("n96.C", 0)
    print(f"RESULT mismatched_production_shape_n96_C={n96c} values (exact)")
    # cost per call, B=96 rows, n=96, both zone modes
    for tz in (True, False):
        base = 20.0 + rng.normal(0, 1.5, (3, 96, 97))
        tgt = np.full(96, 21.0)
        args_ = (base[0], base[1], base[2], tgt, tgt - 1, tgt + 2, np.ones(96))
        self = fake(tz)
        res = {}
        for name, fn in (("prod", PROD), ("twin", twin)):
            best = []
            for _ in range(7):
                s = time.thread_time()
                for _ in range(50):
                    fn(self, *args_)
                best.append((time.thread_time() - s) / 50 * 1000)
            res[name] = sorted(best)[3]
        tag = "two_zone" if tz else "single_zone"
        print(f"RESULT {tag}.prod_ms_per_call={res['prod']:.4f} ms (provisional)")
        print(f"RESULT {tag}.twin_ms_per_call={res['twin']:.4f} ms (provisional)")
        print(f"RESULT {tag}.prod_over_twin={res['prod'] / res['twin']:.2f} ratio")
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / tc:.4f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin ")))
    except (OSError, StopIteration):
        pass
    print(f"RESULT swapins={sw}")
    print(f"# machine: {platform.machine()} {os.cpu_count()}cpu py{platform.python_version()} numpy {np.__version__} "
          f"NPY_DISABLE_CPU_FEATURES={os.environ.get('NPY_DISABLE_CPU_FEATURES', '')!r}")


if __name__ == "__main__":
    main()
