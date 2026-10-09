#!/usr/bin/env python3
"""Reviewer probe 7 (review-2066 round 3): an install whose running asks span under 1.15.

Synthetic only. Same driver as probe 6 (fold, then learn). A heat-led pump
with a real COP scale of 0.75 (right scale 0.75), 400 ticks:
  narrow_config  configured 3.0-3.4 kW, asks 3.0-3.4 kW hourly (span <= 1.13)
  wide_config_steady_week  configured 1.0-6.0 kW, asks 2.8-3.1 kW (a steady cold spell)
  wide_config_varied  configured 1.0-6.0 kW, asks 1.5-5.0 kW (control: learns)
"""
import sys, random
sys.path.insert(0, ".")
sys.argv = [sys.argv[0], "400"]
exec(open(__file__.replace("reviewer_probe7.py", "reviewer_probe6.py")).read().split("R = random.Random(99)")[0])
R = random.Random(5)
run("narrow_config_true0.75", asks(30, 3.0, 3.4), lambda t, a, s, p: a * s / 0.75 * R.uniform(0.98, 1.02), pmax=3.4, pmin=3.0)
run("wide_config_steady_week_true0.75", asks(31, 2.8, 3.1), lambda t, a, s, p: a * s / 0.75 * R.uniform(0.98, 1.02))
run("wide_config_varied_true0.75", asks(32), lambda t, a, s, p: a * s / 0.75 * R.uniform(0.98, 1.02))
