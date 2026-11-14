"""Reviewer's own instrument: how often ask_evidence keeps learning on an
install whose draw IS one efficiency shift of its ask (slope 1), under
multiplicative meter/averaging noise, and on mild part-load curvature."""
import sys, numpy as np
sys.path[:0] = ["tests/hastub", "custom_components"]
from heatpump_optimizer import draw_range as d
rng = np.random.default_rng(20261114)
def win(asks, drawn, cfg):
    w = d.DrawRange()
    for a, x in zip(asks, drawn):
        w.observe(float(x), float(a), cfg[0], cfg[1])
    return w
def frac(span, sigma, n, slope=1.0, k=1/0.6, trials=200, cfg=(0.5, 4.0)):
    lo = 0.6; hi = lo * span
    f = 0
    for _ in range(trials):
        asks = np.exp(rng.uniform(np.log(lo), np.log(hi), n))
        drawn = k * asks ** slope * np.exp(rng.normal(0, sigma, n))
        f += d.ask_evidence(win(asks, drawn, cfg)) == d.ASK_FOLLOWS
    return f / trials
for slope in (1.0, 0.9, 0.85, 0.8):
    for span in (1.5, 3.0, 6.0):
        for sigma in (0.1, 0.2, 0.3):
            for n in (48, 150):
                print(f"RESULT slope={slope} span={span} sigma={sigma} n={n} follows_frac={frac(span, sigma, n, slope):.3f}")
