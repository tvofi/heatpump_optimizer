"""Enumerator for D0-s1's cells: D0.M1, D0.M2 and D0.M3, one item per line.

Run:  python3 dev/audit/rounds/round11/D0/s1/cells.py
Prints <file>/<price profile>/<arm>: every file of D0-s1's scope (check_scopes.py
--seat D0-s1: coordinator.py, optimizer.py, thermal_model.py) crossed with every
price profile of the scope's axis, crossed with the solve arms whose multi-start
calls that file owns. optimizer.py: the space-only and DHW solve paths at the 6,
24 and 48 h horizons, the two-zone DHW path and a manual-pin arm (C2, C3).
thermal_model.py: the store topologies the model owns (two-zone, mixing valve
over a buffer, the two-tank wood plumbing, the wood DHW coil) (C2). coordinator.py:
golden.coordinator_scenarios()'s five configs, solved through
HeatPumpOptimizerCoordinator.async_run_optimization. Baseline 92d38ecb.
"""
PROFILES = ["winter_typical", "winter_extreme", "winter_narrow", "winter_moderate",
            "summer_typical", "summer_negative", "shoulder", "flat"]
ARMS = {
    "optimizer.py": ["space-6h", "space-24h", "space-48h", "dhw-6h", "dhw-24h", "dhw-48h",
                     "twozone-dhw-24h", "pinned-dhw-24h"],
    "thermal_model.py": ["twozone-24h", "valve-storage", "valve-smart-write", "wood-two-tank", "wood-coil"],
    "coordinator.py": ["coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features"],
}


def cells():
    return [f"{f}/{p}/{a}" for f in sorted(ARMS) for p in PROFILES for a in ARMS[f]]


if __name__ == "__main__":
    print("\n".join(cells()))
