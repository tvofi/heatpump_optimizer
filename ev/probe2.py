"""Reviewer-built probe 2: early window (MIN_SAMPLES pairs) and the probe's own perturbation (draw = 1.75*a**0.7)."""
import numpy as np
from heatpump_optimizer import draw_range as dr
rng = np.random.default_rng(2)
for expo, label in ((1.0, "proportional"), (0.7, "PERTURBATION_a^0.7")):
    for pmin, pmax in ((0.5, 4.0), (1.0, 14.0)):
        for sigma in (0.1, 0.2, 0.3):
            c = {}
            for t in range(200):
                w = dr.DrawRange()
                for a in rng.uniform(pmin, pmax, dr.MIN_SAMPLES):
                    w.observe(1.6 * a ** expo * float(np.exp(sigma * rng.standard_normal())), float(a), pmin, pmax)
                ev = dr.ask_evidence(w); c[ev] = c.get(ev, 0) + 1
            print(f"RESULT {label} n={dr.MIN_SAMPLES} range={pmin}-{pmax} sigma={sigma} {dict(sorted(c.items()))}")
