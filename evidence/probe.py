"""Reviewer-built probe: false ASK_IGNORED rate on proportional draws (one efficiency shift) with lognormal noise."""
import sys, numpy as np
from heatpump_optimizer import draw_range as dr
rng = np.random.default_rng(1)
print(f"WINDOW={dr.WINDOW} MIN_SAMPLES={dr.MIN_SAMPLES} DISAGREE_FACTOR={dr.DISAGREE_FACTOR}")
for pmin, pmax in ((0.5, 4.0), (1.0, 14.0), (2.0, 6.0)):
    for sigma in (0.05, 0.10, 0.20, 0.30):
        for shape in ("uniform", "floorpiled"):
            ign = n = 0
            for t in range(100):
                w = dr.DrawRange()
                m = dr.WINDOW
                if shape == "uniform":
                    asks = rng.uniform(pmin, pmax, m)
                else:
                    asks = np.where(rng.random(m) < 0.5, pmin, rng.uniform(pmin, pmax, m))
                for a in asks:
                    w.observe(1.6 * a * float(np.exp(sigma * rng.standard_normal())), float(a), pmin, pmax)
                ev = dr.ask_evidence(w)
                if ev in (dr.ASK_FOLLOWS, dr.ASK_IGNORED):
                    n += 1; ign += ev == dr.ASK_IGNORED
            print(f"RESULT range={pmin}-{pmax} sigma={sigma} {shape} judged={n} ignored={ign}")
