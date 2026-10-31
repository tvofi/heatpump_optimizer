"""R10-CEILING-PROBE: what ceiling-probe runs teach DrawRange's band top.

A set-point install's window holds sub-ceiling commands; each probe run adds
``step_hours / 30 min`` ceiling samples drawing 3.0 kW against a configured
5.0 kW. At 3b4180dcc the rolling window was the only route: one run left
``observed()`` at ``(1.5, None)`` and even 48 ceiling samples left the clamp
unengaged (48/336 under DISAGREE_SHARE). The probe store, where present, is
printed beside it.

Run from a worktree root:
  PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/ceiling_probe_draw.py
"""
from __future__ import annotations

from custom_components.heatpump_optimizer import draw_range as dr, sysid

cfg = sysid.SysIdConfig()
per_run = int(cfg.step_hours / 0.5)  # DEFAULT_OPTIMIZATION_INTERVAL, 30 min


def window(n_ceiling):
    d = dr.DrawRange()
    for _ in range(dr.WINDOW - n_ceiling):
        d.observe(1.5, 2.0, 1.0, 5.0, (35.0, 55.0))
    for _ in range(n_ceiling):
        d.observe(3.0, 5.0, 1.0, 5.0, (55.0, 55.0))
    return d.observed(), d.engaged, d.planned(1.0, 5.0)


def store(runs):
    d = dr.DrawRange()
    if not hasattr(d, "observe_probe"):
        return "no probe store"
    for r in range(runs):
        for j in range(per_run):
            d.observe_probe(r * 86400.0, r * 86400.0 + 1800.0 * (j + 1), 3.0)
    return d.probe_top(), d.planned(1.0, 5.0)


print("samples per run", per_run, "| MIN_SAMPLES", dr.MIN_SAMPLES)
print("window, one run    :", window(per_run))
print("window, 48 ceiling :", window(dr.MIN_SAMPLES))
for runs in (1, 2, 3):
    print(f"probe store, {runs} run(s):", store(runs))
