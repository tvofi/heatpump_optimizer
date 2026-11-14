"""Reviewer's own instrument (not the finder's, not the fixer's): random properties of runs.py and the switch level."""
import sys, time
import numpy as np
from datetime import timedelta
from heatpump_optimizer import runs, duty_legs
from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW as RUN
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
bad = {}
def note(k, cond, info=None):
    if not cond:
        bad.setdefault(k, []).append(info)
N = 3000
for t in range(N):
    n = int(rng.integers(1, 40)); f = float(rng.choice([0.0, 0.05, 0.53, 1.0, 1.1, 5.5])); F = runs.floor_kw(f)
    pmax = max(5.5, F)
    # realizable plan: integer edges
    on = rng.random(n) < 0.5
    q = np.where(on, rng.uniform(F, pmax, n), 0.0)
    for running in (False, True):
        note("count==edges on realizable", abs(runs.start_count(q, f, running) - runs.edge_count(q, running)) < 1e-9, (q.tolist(), f, running))
    # batch == scalar bitwise
    Q = rng.uniform(0, pmax, (5, n)) * (rng.random((5, n)) < 0.7)
    for running in (False, True):
        b = runs.start_count_batch(Q, f, running)
        note("batch==scalar", all(b[i] == runs.start_count(Q[i], f, running) for i in range(5)))
        note("batch F-order", np.array_equal(b, runs.start_count_batch(np.asfortranarray(Q), f, running)))
    # composition: start share + switch weight <= 1 per boundary (p=1 both ways)
    if n >= 2:
        space = Q[0]; dhw = Q[1] * (rng.random(n) < 0.4)
        space = np.minimum(space, np.maximum(pmax - dhw, 0)); tot = space + dhw
        r = runs.running_share(tot, f); a = np.clip(tot / RUN, 0, 1)
        for rule in (duty_legs.DEFAULT_RULE,):
            for k in range(1, n):
                sp2, dh2 = space[k-1:k+1], dhw[k-1:k+1]
                first, last, two = duty_legs.leg_ends(sp2[None], dh2, None, rule=rule)
                lv = pmax * r[k-1:k+1][None]
                w = duty_legs.switch_weights_batch(sp2[None], dh2, (1.0, 1.0), pmax, None, rule, level=lv)[0]
                inside = float(np.sum(np.where(two, lv, 0.0)) / pmax)
                across = w - inside
                note("boundary share+switch<=1", a[k] * (1 - r[k-1]) + across <= 1 + 1e-9, (tot[k-1], tot[k], across))
    # commit
    dt = float(rng.choice([1/12, 0.25, 0.5, 1.0]))
    qq = rng.uniform(0, pmax, n) * (rng.random(n) < 0.8) * rng.choice([0.2, 1.0])
    caps = np.where(rng.random(n) < 0.15, rng.uniform(0, F * 1.2, n), pmax)
    qq = np.minimum(qq, caps)
    forced = np.where(rng.random(n) < 0.1, 1.0, np.where(rng.random(n) < 0.1, 0.0, np.nan))
    prices = rng.uniform(-0.2, 3, n) if t % 3 else np.full(n, 1.0)
    sc = float(rng.choice([0.0, 0.25, 5.0])); running = bool(rng.random() < 0.5)
    L = (runs.steps_at_least(runs.MIN_RUN, dt), runs.steps_at_least(runs.MIN_PAUSE, dt))
    for band in (2, 6, 24, n):
        try:
            mask, tracked = runs.commit(qq, prices, f, caps, sc, band, dt=dt, running=running, forced=forced, lengths=L)
        except Exception as e:
            note("commit raises", False, repr(e)); continue
        eff = np.where(np.isnan(forced) & (caps < F - 1e-9), 0.0, forced)
        note("forced on kept", bool(np.all(mask[eff == 1.0])), None)
        note("forced off kept", bool(not np.any(mask[eff == 0.0])), None)
        lvl = np.where(mask, np.minimum(np.maximum(qq, F), caps), 0.0)
        note("on step in [floor,cap] unless forced on under a low cap", bool(np.all((~mask) | (lvl >= F - 1e-9) | (eff == 1.0))), None)
        walk = np.cumsum(lvl - qq) * dt
        truth = bool(np.all(np.abs(walk) <= band * F * dt + 1e-9) and abs(walk[-1]) <= F * dt / 2 + 1e-9)
        note("tracked flag is the walk's", tracked == truth, None)
        # run/pause lengths on free interior runs
        if np.all(np.isnan(eff)):
            edges = np.flatnonzero(np.diff(mask.astype(int)) != 0) + 1
            segs = np.split(mask, edges)
            for i, s in enumerate(segs[1:-1], 1):
                need = L[0] if s[0] else L[1]
                note("interior run/pause length", len(s) >= need, (len(s), need, bool(s[0])))
    # identity on realizable input, no forced, no caps
    m, tr = runs.commit(q, prices, f, pmax, sc, 2, dt=dt, running=False, lengths=(1, 1))
    note("identity on realizable (lengths 1,1)", np.array_equal(m, q > 0), (q.tolist(), m.tolist(), prices.tolist(), sc, dt, f))
for k, v in bad.items():
    print(f"RESULT leaf {k}: FAIL x{len(v)} first={str(v[0])[:400]}")
print(f"RESULT leaf: {N} cases, {len(bad)} failing properties")
# cost of the whole-horizon band
for n, dt in ((96, 0.25), (192, 0.25), (576, 1/12)):
    q = rng.uniform(0, 0.4, n); t0 = time.process_time()
    ms = runs.candidates(q, rng.uniform(0.5, 2, n), 1.1, np.where(rng.random(n) < 0.3, 0.5, 5.5), 0.25, dt=dt)
    print(f"RESULT leaf candidates n={n} dt={dt:.3f}: {len(ms)} masks in {time.process_time()-t0:.2f} cpu-s")
