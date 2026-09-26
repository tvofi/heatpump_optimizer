#!/usr/bin/env python3
"""Enumerator, class "CPU work inline on the event loop".

Widens D9-s1-03's seam_rule (`_sysid.(step|arm|identify)` in coordinator.py)
and D9-s2-01's (sensor_advisor ranking re-simulated on every plan-sensor
write) to every direct (non-executor) call from a coordinator/entity
property or `_async_update_data` into a `ThermalModel.simulate_step` /
`_sysid.step` / other O(n) numeric loop.

Run: python3 tools/audit/round9/D14/sweep/cpu_work_inline_event_loop/enumerate.py
"""
import subprocess
import sys

PKG = "custom_components/heatpump_optimizer"

SEAM_RULES = [
    ["grep", "-n", r"_sysid\.\(step\|arm\|identify\)", f"{PKG}/coordinator.py"],
    ["grep", "-rn", "rank_sensor_advisor\\|simulate_step", f"{PKG}/sensor.py", f"{PKG}/topology.py"],
]


def run(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    return out.splitlines() if out else []


def main() -> int:
    all_hits = []
    for cmd in SEAM_RULES:
        all_hits.extend(run(cmd))
    print(f"RESULT candidate_sites={len(all_hits)}")
    for h in all_hits:
        print(" ", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
