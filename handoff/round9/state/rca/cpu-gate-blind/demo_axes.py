"""RCA demo: the plant-axis coverage check prototyped in tests/stress.py on
handoff/r9-rca-cpu-gate-blind (plant_axes / unsampled_plant_axes).
Metric: len(unsampled_plant_axes(plant_axes(sweep))) and its names.
Arms: shipped  -- the gate's own sweep_combinations() (must name the valve axes: D9-s2-71)
      fixed    -- the same plus three valve scenarios built from tests/golden.py's own valve
                  configs, one re-moded to smart_read (must be empty)
      null     -- fixed minus the no-valve plants' axis (a sweep of valve plants only):
                  must name layout:no_valve and valve_mode:none (the check is not vacuous)
Command (from the prototype worktree root): PYTHONPATH=tests/hastub python3 <this>
"""
import sys, time
sys.path[:0] = ["tests", "custom_components"]
import stress, golden

base = stress.sweep_combinations()
def valve(name, label, season="winter", **over):
    sc = golden.SCENARIOS[name]
    return dict(season=season, two_zone=sc.get("two_zone", True), dhw=sc.get("dhw", True),
                config={**sc.get("config_overrides", {}), **over}, label=label)
extra = [valve("valve_storage", "winter/2z/valve"),
         valve("valve_upper_direct_slab", "winter/2z/valve-direct-slab", mixing_valve_mode="smart_read"),
         valve("wood_two_tank_smart_write", "winter/2z/wood-two-tank")]
for arm, combos in (("shipped", base), ("fixed", base + extra)):
    t = time.perf_counter(); seen = stress.plant_axes(combos); dt = time.perf_counter() - t
    miss = stress.unsampled_plant_axes(seen)
    print(f"RESULT arm={arm} plants={len(seen)} unsampled={len(miss)} seconds={dt:.2f} names={miss}")
    if arm == "fixed":
        for l in [c["label"] for c in extra]: print(f"  {l}: {seen[l]}")
seen = stress.plant_axes(extra)
miss = stress.unsampled_plant_axes(seen)
print(f"RESULT arm=null plants={len(seen)} unsampled={len(miss)} names={miss}")
