"""R9-F2.5 mutation proofs: one mutant in memory at a time, against the
production symbol, with the healthy arm and the divergence count beside it.

Run:  PYTHONPATH=tests/hastub:custom_components python3 mutation_proof.py
"""
import sys
import numpy as np

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, "custom_components")

from datetime import datetime, timezone

import heatpump_optimizer.tariff as T
from heatpump_optimizer.tariff import peak_cost_batch, peak_cost_smooth, metering_windows
from heatpump_optimizer.optimizer import HeatPumpOptimizer
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from heatpump_optimizer.optimizer import OptimizationConfig

N = 96
rng = np.random.default_rng(2512)
tie = np.zeros(N)
tie[0:16] = 7.0
nanrow = rng.uniform(1.0, 4.0, size=N)
nanrow[5] = np.nan
rows = np.vstack([
    rng.uniform(0.0, 9.0, size=N),
    np.full(N, 7.0),
    tie,
    rng.uniform(0.0, 1.0, size=N),
    nanrow,
    np.zeros(N),
    rng.uniform(0.0, 6.0, size=N),
])
base = np.full(N, 1.5)


def grid_divergences():
    """The features grid, compact: returns the count of byte-divergent rows."""
    bad = 0
    for w, dt, offs in (
        (15, 0.25, (0, 1, 3)), (45, 0.25, (0, 1, 3)),
        (60, 0.25, (0, 1, 3)), (120, 0.25, (0, 1, 3)),
        (60, 1.0 / 12.0, (0, 1, 3, 11)),
    ):
        for off in offs:
            nw = metering_windows(np.zeros(N), w, dt, off).size
            facs = np.tile(np.array([1.0, 0.0, 0.5, 1.0]), 1 + nw // 4)[:nw]
            lab = T.plan_window_days(
                nw, w, datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)
            )
            for f in (None, facs):
                for dd in (True, False):
                    for order in ("C", "F"):
                        mat = np.asarray(rows, order=order)
                        got = peak_cost_batch(
                            mat, base, 3.0, 20.0, w, dt, 3, off,
                            window_factors=f, distinct_days=dd, window_days=lab,
                        )
                        for r in range(mat.shape[0]):
                            one = peak_cost_smooth(
                                np.array(mat[r]), base, 3.0, 20.0, w, dt, 3,
                                off, window_factors=f, distinct_days=dd,
                                window_days=lab,
                            )
                            if (np.float64(got[r]).tobytes()
                                    != np.float64(one).tobytes()):
                                bad += 1
    for wn in (8, 12, 48, 96, 129, 192):
        wrows = rng.uniform(0.0, 9.0, size=(7, wn))
        wrows[0] = 7.0
        wrows[1, : wn // 6] = 7.0
        nw = metering_windows(np.zeros(wn), 60, 0.25, 3).size
        lab = T.plan_window_days(
            nw, 60, datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)
        )
        got = peak_cost_batch(
            wrows, np.full(wn, 1.5), 3.0, 20.0, 60, 0.25, 3, 3,
            window_days=lab, distinct_days=True,
        )
        for r in range(7):
            one = peak_cost_smooth(
                wrows[r], np.full(wn, 1.5), 3.0, 20.0, 60, 0.25, 3, 3,
                window_days=lab, distinct_days=True,
            )
            if (np.float64(got[r]).tobytes() != np.float64(one).tobytes()):
                bad += 1
    return bad


def term_divergences(arms=(None, "manual")):
    """The terminal grid: rows whose store terms span the deficits' range."""
    bad = 0
    for kw in ({}, {"mixing_valve_mode": "manual", "buffer_tank_volume": 300.0,
                    "cop_flow_carnot": True}):
        if (kw.get("mixing_valve_mode") or None) not in arms:
            continue
        o = HeatPumpOptimizer(
            ThermalModel(ThermalParameters(two_zone_enabled=True, **kw)),
            OptimizationConfig(),
        )
        cost, cb = o._terminal_cost(np.full(96, 1.0), np.full(96, -5.0))
        traj = {k: rng.uniform(5.0, 32.0, size=(97, 5))
                for k in ("room", "slab", "upper", "lower", "buffer")}
        got = cb(traj)
        for r in range(97):
            one = cost(traj["room"][r], traj["slab"][r], traj["upper"][r],
                       traj["lower"][r], traj["buffer"][r])
            if (np.float64(got[r]).tobytes() != np.float64(one).tobytes()):
                bad += 1
    return bad


def calls_97_vs_2():
    """The growth pin: total profiled calls at 97 rows against 2."""
    def count(fn, *a, **k):
        c = [0]
        def prof(_f, event, _arg):
            if event in ("call", "c_call"):
                c[0] += 1
        sys.setprofile(prof)
        try:
            fn(*a, **k)
        finally:
            sys.setprofile(None)
        return c[0]
    labels = T.plan_window_days(
        metering_windows(np.zeros(N), 60, 0.25, 3).size, 60,
        datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc),
    )
    mat2 = rows[[0, 6]]
    mat97 = np.tile(mat2, (49, 1))[:97]
    return (
        count(peak_cost_batch, mat97, base, 3.0, 20.0, 60, 0.25, 3, 3,
              window_days=labels, distinct_days=True),
        count(peak_cost_batch, mat2, base, 3.0, 20.0, 60, 0.25, 3, 3,
              window_days=labels, distinct_days=True),
    )


print("healthy: grid_divergences=%d term_divergences=%d calls(97,2)=%s"
      % (grid_divergences(), term_divergences(), calls_97_vs_2()))

# M1: every replicated reduction replaced by numpy's own axis reduction --
# the #948 shape (arm64 seat wrote it, x86_64 CI re-planned 19 of 51).
_real_row_sums = T.row_sums
T.row_sums = lambda m: np.sum(m, axis=1)
print("M1 row_sums->np.sum(axis=1): grid_divergences=%d" % grid_divergences())
T.row_sums = _real_row_sums

# M2: the window means as np.mean over the batched blocks.
_real_means = T._block_means_batch
T._block_means_batch = lambda b: np.mean(b, axis=1)
print("M2 block means->np.mean(axis=1): grid_divergences=%d" % grid_divergences())
T._block_means_batch = _real_means

# M3: the bisection without the freeze -- every row keeps bisecting after
# its root is found, so a converged row's mid moves off its root.
_real_smooth = T._smooth_topk_sum_batch


def _smooth_nofreeze(values, k, tau):
    n_rows, m = values.shape
    out = np.zeros(n_rows)
    if m == 0 or k <= 0:
        return out
    k = max(1, min(int(k), m))
    positive = np.flatnonzero(np.any(values > 0, axis=1))
    if positive.size == 0:
        return out
    x = values[positive]
    peak = np.max(x, axis=1)
    scale = np.maximum(tau * peak, 1e-9)
    pad = 40.0 * scale
    lo = np.min(x, axis=1) - 1.0 - pad
    hi = peak + 1.0 + pad
    mid = 0.5 * (lo + hi)
    for _ in range(64):
        z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0)
        w = 1.0 / (1.0 + np.exp(-z))
        count = np.sum(w, axis=1)
        if np.all(np.abs(count - k) < 1e-6):
            break
        over = count > k
        lo = np.where(over, mid, lo)
        hi = np.where(over, hi, mid)
        mid = 0.5 * (lo + hi)
    z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0)
    w = 1.0 / (1.0 + np.exp(-z))
    out[positive] = np.sum(w * x, axis=1)
    return out


T._smooth_topk_sum_batch = _smooth_nofreeze
print("M3 bisection without the freeze: grid_divergences=%d" % grid_divergences())
T._smooth_topk_sum_batch = _real_smooth

# M4: the TWIN's accumulation vectorised -- plain np.add.reduce over the
# term columns instead of the per-row builtin sum through row_cost, the
# exact #948 round-7 shape. The pricing rides through row_cost([p]) on the
# single-sum arm, whose 1-term call applies the same multiply and divide.
# On CPython 3.11 sum() is plain accumulation, so this box is expected to
# agree (blind); CI's 3.14 lane is the detector, and this proof runs there
# in the container too.
_real_tcb = HeatPumpOptimizer.__dict__["_terminal_cost_batch"].__func__


def _tcb_plain(row_cost, term_spec):
    def cost_batch(traj):
        terms = np.stack([
            coef * np.where(
                (d := cap - traj[name][:, -1]) > 0.0, d, 0.0
            )
            for coef, name, cap in term_spec
        ], axis=1)
        plain = np.add.reduce(terms, axis=1)
        return np.fromiter(
            (row_cost([p]) for p in plain.tolist()),
            dtype=float, count=plain.size,
        )
    return cost_batch


HeatPumpOptimizer._terminal_cost_batch = staticmethod(_tcb_plain)
print("M4 twin accumulation -> plain reduce (single-sum arm, where the"
      " mutant is faithful): term_divergences=%d"
      % term_divergences(arms=(None,)))
HeatPumpOptimizer._terminal_cost_batch = staticmethod(_real_tcb)

# M5: the window means re-entered per row -- the recomputation this fix
# removes, reintroduced on one stage only.
_real_wmb = T._window_means_batch


def _wmb_per_row(houses, window_minutes, dt_hours, offset_steps):
    return np.stack([
        metering_windows(houses[b], window_minutes, dt_hours, offset_steps)
        for b in range(houses.shape[0])
    ])


T._window_means_batch = _wmb_per_row
print("M5 window means per row: calls(97,2)=%s (pin: equal)"
      % (calls_97_vs_2(),))
T._window_means_batch = _real_wmb

print("restored: grid_divergences=%d term_divergences=%d calls(97,2)=%s"
      % (grid_divergences(), term_divergences(), calls_97_vs_2()))
