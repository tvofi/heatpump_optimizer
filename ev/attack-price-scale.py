"""Reviewer's attack (not the finder's): the grid cell and two fixtures under scaled price profiles,
clamped, configured 0, clamped default 0 vs 0.1 (shipped)."""
import sys, numpy as np
sys.path[:0] = ["dev/audit/harnesses"]
import r11_honest_starts_runs as h
om = h.om
base_prices = h.GRID_PRICES.copy()
def run(scale, default, p_min=1.1, loss=0.4, out=8.0):
    h.GRID_PRICES = base_prices * scale
    kept = om.CLAMPED_DEFAULT_START_PRICE; om.CLAMPED_DEFAULT_START_PRICE = default
    try:
        r = h._grid_solve(0.0, True, p_min, loss, out)
    finally:
        om.CLAMPED_DEFAULT_START_PRICE = kept
    plan = np.asarray(r.power_schedule, float)
    return h.edges(plan), float(np.sum(plan))*0.25, float(np.sum(plan*h.GRID_PRICES))*0.25, float(np.min(r.room_temp_trajectory))
for cell in [(1.1,0.4,8.0),(0.53,0.4,8.0),(1.1,1.0,2.0),(1.1,1.0,-5.0)]:
    for scale in (0.1, 0.25, 1.0, 3.0):
        a = run(scale, 0.0, *cell); b = run(scale, 0.1, *cell)
        print(f"cell p_min/loss/out {cell} price x{scale}: default0 starts {a[0]} kwh {a[1]:.2f} energy_cost {a[2]:.4f} lowest_room {a[3]:.2f} | default0.1 starts {b[0]} kwh {b[1]:.2f} energy_cost {b[2]:.4f} lowest_room {b[3]:.2f}", flush=True)
