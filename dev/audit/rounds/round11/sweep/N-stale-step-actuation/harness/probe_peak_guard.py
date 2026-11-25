#!/usr/bin/env python3
"""N-stale-step-actuation probe: the peak-guard release re-publishes the cut displace.

On D16-s2's rig (reference plant, frozen clock, device stub): a plan whose step 0
is 'partial' and step 1 'full' (different displace), one cycle cut at T0+1 min.
At the instant AT (default T0+16 min, inside step 1) the peak guard releases and
``_async_peak_guard_transition`` publishes; the probe compares the MQTT displace it
published with the plan's own displace for the step covering AT (D16-s2's oracle).

Usage: PYTHONPATH=tests/hastub python3 probe_peak_guard.py [--at MIN] [--recut]
  --at 5     null arm: the release inside the cut's own step (expected rc=0)
  --recut    perturbation: a cycle re-cut at AT before the release (expected rc=0)
rc=1 while the release publishes another step's displace.
"""
import argparse
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "dev/audit/rounds/round11/D16/s2"))
import rig  # noqa: E402
import timing  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", type=int, default=16)
    ap.add_argument("--recut", action="store_true")
    a = ap.parse_args()
    sim = rig.Sim()
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    plan = rig.plan(timing.rows_for(["partial", "full", "full", "full"], f, P))
    sim.at(rig.T0 + timedelta(minutes=1))
    sim.cycle(plan)
    at = rig.T0 + timedelta(minutes=a.at)
    sim.at(at)
    if a.recut:
        sim.cycle(plan)
    # engage, then release: the release is the transition that re-publishes the action
    pg = c._peak_guard
    for state in (True, False):
        try:
            pg.suppressing = state
        except AttributeError:
            pg._suppressing = state
        sim.run(c._async_peak_guard_transition())
    k = rig.oracle_index(plan, at)
    want = timing.oracle(None, plan, k, "mqtt_displace")
    got = sim.mqtt_payload()
    print(f"RESULT at_min={a.at} step={k} published={got} plan_step_displace={want} "
          f"cut_step_displace={timing.oracle(None, plan, 0, 'mqtt_displace')}")
    stale = got != want
    print(f"RESULT release_publishes_other_step={int(stale)}")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
