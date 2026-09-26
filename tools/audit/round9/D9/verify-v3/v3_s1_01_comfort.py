"""D9 verify-v3 (round 9, lens V3) for D9-s1-01: removable solve CPU of the
per-row loop in HeatPumpOptimizer._comfort_terms_batch, and whether an axis=1
reduction is bit-equal to it -- on the solve and on a synthetic alignment sweep.

Metric (one line): removable_share = 1 - median solve thread CPU with an
independently written axis=1 twin / median solve thread CPU with production,
ABAB-interleaved in one process, per stress.build_case cell; plus exact count of
bitwise-different (penalty, comfort) values between production and the twin.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s1_01_comfort.py [--reps 2]
Instrumented symbol: optimizer.HeatPumpOptimizer._comfort_terms_batch (swapped
in memory). Perturbation: --twin-off runs production in both arms, so the
removable share must go to ~0 (the null control; same session, same load).
Expected: removable_share 0.2-0.3 on two-zone, 0.1-0.2 single-zone (+-0.05,
provisional under contention); plan sha equal between arms (exact).
The synthetic sweep compares a per-row loop on fresh arrays with np.sum(axis=1)
over [B, n+1][:, 1:] slices for n in 20..200 and B in {1, 7, 96, 97}; any
mismatch count > 0 is the docstring's cross-backend hazard showing on THIS box.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, hashlib, statistics, time
import numpy as np
import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer
from heatpump_optimizer import optimizer as om

PROD = HeatPumpOptimizer._comfort_terms_batch


def twin(self, room, upper, lower, tgt, tmin, tmax, band):
    w = self.config.comfort_weight
    def sq(a):
        return a * a if False else a ** 2
    if self.model.params.two_zone_enabled:
        pen = np.zeros(room.shape[0]); com = np.zeros(room.shape[0])
        U = upper[:, 1:]; L = lower[:, 1:]
        a = np.maximum(0, tmin - U); b = np.maximum(0, U - tmax)
        c = np.maximum(0, tmin - L); d = np.maximum(0, L - tmax)
        pen = 0.5 * w * (np.sum(a ** 2, axis=1) * 10.0 + np.sum(b ** 2, axis=1) * 5.0
                         + np.sum(c ** 2, axis=1) * 10.0 + np.sum(d ** 2, axis=1) * 5.0
                         + (np.sum(a, axis=1) + np.sum(c, axis=1)) * om._COMFORT_FLOOR_L1)
        com = om._COMFORT_PULL_TWO_ZONE * w * (np.sum(((U - tgt) / band) ** 2, axis=1)
                                               + np.sum(((L - tgt) / band) ** 2, axis=1))
        return pen, com
    Rr = room[:, 1:]
    a = np.maximum(0, tmin - Rr); b = np.maximum(0, Rr - tmax)
    pen = w * (np.sum(a ** 2, axis=1) * 10.0 + np.sum(b ** 2, axis=1) * 5.0
               + np.sum(a, axis=1) * om._COMFORT_FLOOR_L1)
    com = om._COMFORT_PULL_SINGLE_ZONE * w * np.sum(((Rr - tgt) / band) ** 2, axis=1)
    return pen, com


MIS = {"n": 0, "calls": 0}


def checking(self, *a):
    out = PROD(self, *a)
    alt = twin(self, *a)
    MIS["calls"] += 1
    for x, y in zip(out, alt):
        MIS["n"] += int(np.count_nonzero(x.view(np.int64) != y.view(np.int64)))
    return out


def run(spec, fn):
    HeatPumpOptimizer._comfort_terms_batch = fn
    try:
        r = stress.build_case(**spec)
    finally:
        HeatPumpOptimizer._comfort_terms_batch = PROD
    sha = hashlib.sha1(np.asarray(r["result"].power_schedule, float).tobytes()).hexdigest()[:16]
    return r["solve_thread_ms"], sha


def synth():
    rng = np.random.default_rng(1)
    mism = 0; total = 0
    for n in range(20, 201):
        for B in (1, 7, 96, 97):
            X = rng.normal(20, 2, size=(B, n + 1))
            tmin = rng.normal(19, 0.5, n); band = np.full(n, 1.3)
            rows = np.array([np.sum((np.maximum(0, tmin - X[b][1:]) / band) ** 2) for b in range(B)])
            vec = np.sum((np.maximum(0, tmin - X[:, 1:]) / band) ** 2, axis=1)
            rows2 = np.array([np.sum((X[b][1:] - tmin) ** 2) for b in range(B)])
            vec2 = np.sum((X[:, 1:] - tmin) ** 2, axis=1)
            mism += int(np.count_nonzero(rows.view(np.int64) != vec.view(np.int64)))
            mism += int(np.count_nonzero(rows2.view(np.int64) != vec2.view(np.int64)))
            total += 2 * B
    return mism, total


CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--twin-off", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    B_fn = PROD if a.twin_off else twin
    tag0 = "null_" if a.twin_off else ""
    for cell, spec in CELLS.items():
        if a.only and cell != a.only:
            continue
        # parity pass (untimed)
        MIS["n"] = MIS["calls"] = 0
        _, sha_chk = run(spec, checking)
        A, Bv, shaA, shaB = [], [], set(), set()
        for _ in range(a.reps):
            t, s = run(spec, PROD); A.append(t); shaA.add(s)
            t, s = run(spec, B_fn); Bv.append(t); shaB.add(s)
        mA, mB = statistics.median(A), statistics.median(Bv)
        V.R(f"{tag0}{cell}.prod_solve_thread_ms", round(mA, 1), "ms (provisional)")
        V.R(f"{tag0}{cell}.twin_solve_thread_ms", round(mB, 1), "ms (provisional)")
        V.R(f"{tag0}{cell}.removable_share", round(1 - mB / mA, 4), "ratio")
        V.R(f"{tag0}{cell}.plan_sha_equal", shaA == shaB == {sha_chk}, f"({sorted(shaA)} vs {sorted(shaB)})")
        V.R(f"{tag0}{cell}.bit_mismatches", MIS["n"], f"values over {MIS['calls']} calls (exact)")
        V.R(f"{tag0}{cell}.thread_factor", V.tf_now())
    m, tot = synth()
    V.R("synthetic_axis1_vs_rowloop_mismatches", m, f"of {tot} row values (exact)")
    V.trailer()


if __name__ == "__main__":
    main()
