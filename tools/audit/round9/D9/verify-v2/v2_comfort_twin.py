"""V2 (independent) check of D9-s1-01: the per-row loop in
optimizer.HeatPumpOptimizer._comfort_terms_batch.

Metric A (own definition): fraction of optimize() thread CPU REMOVED when
_comfort_terms_batch is swapped for an axis=1 twin written here, measured
end to end (1 - median(solve_twin)/median(solve_prod) over interleaved
A/B/A/B arms of stress.build_case), per cell -- no timer inside the hooked
method, so it is independent of the finder's in-method share.
Metric B: bitwise mismatches (float64 bit patterns) between the production
method and the twin over a synthetic shape sweep that includes horizons
above numpy's 128-element pairwise-summation block (n = 129..288), row
counts 1..193, and both zone topologies; plus plan sha equality end to end
at 24 h AND 48 h (n = 192, the case the docstring's x86_64 ulp concern would
bite if axis=1 reductions took a different summation path).
Count key: the (penalty, comfort) arrays the production method RETURNS and
result.power_schedule bytes.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_comfort_twin.py [--pairs 2] [--skip-48]
Perturbation: the twin swap itself (solve CPU must go DOWN, plans identical);
null arm: A vs A (same method twice) must give ~0 saved.
Expected (baseline 1936d5ca, this box, provisional): saved 0.2-0.35 on
two-zone cells, 0.05-0.2 single-zone; mismatches 0; plan sha equal.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import hashlib
import statistics
from types import SimpleNamespace

import numpy as np

import stress
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PROD = HeatPumpOptimizer._comfort_terms_batch
L1 = om._COMFORT_FLOOR_L1
P2 = om._COMFORT_PULL_TWO_ZONE
P1 = om._COMFORT_PULL_SINGLE_ZONE


def twin(self, room, upper, lower, targets, tmin, tmax, band):
    w = self.config.comfort_weight
    if self.model.params.two_zone_enabled:
        u, l = upper[:, 1:], lower[:, 1:]
        uu = np.maximum(0, tmin - u); ou = np.maximum(0, u - tmax)
        ul = np.maximum(0, tmin - l); ol = np.maximum(0, l - tmax)
        s = lambda a: np.sum(a, axis=1)  # noqa: E731
        pen = 0.5 * w * (s(uu ** 2) * 10.0 + s(ou ** 2) * 5.0 + s(ul ** 2) * 10.0
                         + s(ol ** 2) * 5.0 + (s(uu) + s(ul)) * L1)
        com = P2 * w * (s(((u - targets) / band) ** 2) + s(((l - targets) / band) ** 2))
        return pen, com
    r = room[:, 1:]
    un = np.maximum(0, tmin - r); ov = np.maximum(0, r - tmax)
    pen = w * (np.sum(un ** 2, axis=1) * 10.0 + np.sum(ov ** 2, axis=1) * 5.0
               + np.sum(un, axis=1) * L1)
    com = P1 * w * np.sum(((r - targets) / band) ** 2, axis=1)
    return pen, com


def parity_sweep():
    rng = np.random.default_rng(20260926)
    mism = values = 0
    worst = None
    for two in (True, False):
        fake = SimpleNamespace(config=SimpleNamespace(comfort_weight=1.37),
                               model=SimpleNamespace(params=SimpleNamespace(two_zone_enabled=two)))
        for n in (24, 48, 96, 97, 127, 128, 129, 192, 193, 288):
            for B in (1, 2, 7, 96, 97, 193):
                for offset in (0, 1):  # offset 1: rows start mid-buffer (view, odd alignment)
                    big = 21.0 + rng.normal(0, 1.5, (3, B, n + 1 + offset))
                    room, up, lo = (big[i][:, offset:] for i in range(3))
                    tmin = 20.0 + rng.normal(0, 0.2, n)
                    tmax = 23.0 + rng.normal(0, 0.2, n)
                    tgt = 21.0 + rng.normal(0, 0.1, n)
                    band = 1.0 + np.abs(rng.normal(0, 0.3, n))
                    a = PROD(fake, room, up, lo, tgt, tmin, tmax, band)
                    b = twin(fake, room, up, lo, tgt, tmin, tmax, band)
                    for x, y in zip(a, b):
                        bad = int(np.count_nonzero(x.view(np.int64) != y.view(np.int64)))
                        mism += bad
                        values += x.size
                        if bad and worst is None:
                            worst = (two, n, B, offset)
    V.result("parity.values_compared", values, "count")
    V.result("parity.bit_mismatches", mism, "count (exact)")
    V.result("parity.first_mismatch_shape", str(worst).replace(" ", ""))


CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),  # null: flat prices
    "two_zone_dhw_winter_h48": dict(season="winter", two_zone=True, dhw=True, hours=48),
}


def solve(spec, method):
    HeatPumpOptimizer._comfort_terms_batch = method
    try:
        run = stress.build_case(**spec)
    finally:
        HeatPumpOptimizer._comfort_terms_batch = PROD
    sha = hashlib.sha1(np.asarray(run["result"].power_schedule, float).tobytes()).hexdigest()[:16]
    return run["solve_thread_ms"], sha, run["solver_evals"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--skip-48", action="store_true")
    args = ap.parse_args()
    parity_sweep()
    for cell, spec in CELLS.items():
        if args.skip_48 and "h48" in cell:
            continue
        a, b, sa, sb = [], [], set(), set()
        for _ in range(args.pairs):
            t, s, ea = solve(spec, PROD); a.append(t); sa.add(s)
            t, s, eb = solve(spec, twin); b.append(t); sb.add(s)
        saved = 1 - statistics.median(b) / statistics.median(a)
        V.result(f"{cell}.prod_solve_thread_ms_median", round(statistics.median(a), 1), "ms (provisional)")
        V.result(f"{cell}.twin_solve_thread_ms_median", round(statistics.median(b), 1), "ms (provisional)")
        V.result(f"{cell}.saved_fraction_of_solve", round(saved, 4), "ratio")
        V.result(f"{cell}.null_prod_vs_prod_spread", round(max(a) / min(a) - 1, 4), "ratio")
        V.result(f"{cell}.plan_sha_equal", int(sa == sb and len(sa) == 1), "bool (exact)")
        V.result(f"{cell}.solver_evals_equal", int(ea == eb), "bool")
    V.trailer()


if __name__ == "__main__":
    main()
