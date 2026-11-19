"""D12.M3 -- the DHW set-point Fix (repairs) on every DHW set-point surface the tree writes.

Metric (one line): over (DHW set-point domain x entity range), RESULT bad_fix_writes = the
service calls the confirmed ``dhw_setpoint_below_disinfection`` repair sends that (a) go to a
service of another domain than the entity's, or (b) put a value outside the entity's own
declared range (climate/water_heater min_temp/max_temp, number/input_number min/max).
RESULT fix_writes is the denominator; RESULT issues_raised counts the cells whose cycle raised
the notice (the Fix is only reachable there).

Count key: what production sends -- the (domain, service, data) the real
repairs.DhwSetpointRepairFlow.async_step_confirm hands ``hass.services.async_call`` after
one real coordinator cycle raised the issue with its own data (setpoint_check._dhw) -- never
the harness's own config.

Cells: 4 domains (number, input_number, climate, water_heater) x 2 ranges:
  holds  -- the entity's range [40, 65] holds the notice's floor
  capped -- the entity's range [30, 55]: a pump whose DHW set-point tops out at 55 degC
  capped_immersion -- the same, with the disinfection run by an immersion switch
             (dhw_disinfection_switch_entity, mode control): the plant the tree offers
             for a pump that cannot reach the disinfection temperature itself
The entity reads 41 degC (below the floor) in both, so the notice is raised in all 8. The
floor is setpoint_check._dhw_floor: max(dhw_min_temperature 45, the disinfection temperature
while a legionella cycle is active -- 60 degC on this plant's first cycle, printed per cell).

Hooks: heatpump_optimizer.repairs:async_create_fix_flow / DhwSetpointRepairFlow.async_step_confirm,
heatpump_optimizer.setpoint_check:_dhw (via coordinator:HeatPumpOptimizerCoordinator._async_update_data).

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/repairs_surfaces.py
  ... --perturb entity-cap   # setpoint_check.quantise_setpoint_c given hi_c = min(its hi_c, the entity's own max):
                             # the one-line production change; bad_fix_writes must go to 0
  ... --list                 # the cells, one per line
Expected at baseline 92d38ecb (box B6): see REPORT.md (exact counts).
Machine: box B6, Linux x86_64, python 3.14.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import surfaces as S  # noqa: E402
from harness import FakeState  # noqa: E402

from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer import inputs, repairs, setpoint_check  # noqa: E402

FLOOR = 45.0
RANGES = {"holds": (40, 65), "capped": (30, 55), "capped_immersion": (30, 55)}
DOMAINS = ("number", "input_number", "climate", "water_heater")


def entity(domain, lo, hi):
    if domain in ("climate", "water_heater"):
        return FakeState("heat", attributes={"temperature": 41, "current_temperature": 41,
                                             "min_temp": lo, "max_temp": hi, "target_temp_step": 1,
                                             "unit_of_measurement": "°C"})
    return FakeState("41", attributes={"unit_of_measurement": "°C", "min": lo, "max": hi, "step": 1})


def cells():
    return [(d, r) for d in DOMAINS for r in RANGES]


def run(domain, rng):
    lo, hi = RANGES[rng]
    ent = f"{domain}.dhw_sp"
    cfg = {**S.GEN_BASE, **S.CONTROL, c.CONF_DHW_SETPOINT_ENTITY: ent, c.CONF_DHW_MIN_TEMP: FLOOR}
    states = {**S.GEN_STATES, ent: entity(domain, lo, hi)}
    if rng == "capped_immersion":
        cfg.update({c.CONF_DHW_DISINFECTION_SWITCH_ENTITY: "switch.immersion", c.CONF_DHW_DISINFECTION_MODE: "control"})
        states["switch.immersion"] = FakeState("off")
    hass, coord = S.build(cfg, states, entry_id=f"rep_{domain}_{rng}")
    asyncio.run(coord._async_update_data())
    issue = next((i for i in getattr(hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW), None)
    if issue is None:
        return False, []
    print(f"  issue data {issue[2].get('data')} legionella_active={coord._ctx._thermal_params.legionella_cycle_active}")
    flow = asyncio.run(repairs.async_create_fix_flow(hass, setpoint_check.ISSUE_DHW, issue[2].get("data")))
    flow.hass, flow.issue_id, flow.data = hass, setpoint_check.ISSUE_DHW, issue[2].get("data")
    hass.services.calls.clear()
    asyncio.run(flow.async_step_confirm({}))
    out = []
    for dom, svc, data in hass.services.calls:
        if (data or {}).get("entity_id") != ent:
            print(f"  other call {dom}.{svc} {data}")
            continue
        key = inputs.SETPOINT_SERVICES.get(dom, (None, "value"))[1]
        val = (data or {}).get(key)
        bad = []
        if dom != domain:
            bad.append(f"domain {dom} != {domain}")
        if val is not None and not (lo - 1e-9 <= float(val) <= hi + 1e-9):
            bad.append(f"value {val} outside [{lo},{hi}]")
        out.append((dom, svc, val, bad))
    return True, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--perturb", choices=["entity-cap"])
    a = ap.parse_args()
    if a.list:
        for d, r in cells():
            print(f"{d}:{r}")
        return
    t0, c0, th0 = time.time(), time.process_time(), time.thread_time()
    patches = []
    if a.perturb == "entity-cap":
        real = setpoint_check.quantise_setpoint_c

        def capped(hass, entity_id, value_c, *, rounding="nearest", lo_c=None, hi_c=None):
            ent_hi = inputs.setpoint_range_c(hass, entity_id)[1]
            if ent_hi is not None:
                hi_c = ent_hi if hi_c is None else min(hi_c, ent_hi)
            return real(hass, entity_id, value_c, rounding=rounding, lo_c=lo_c, hi_c=hi_c)
        patches.append(mock.patch.object(setpoint_check, "quantise_setpoint_c", capped))
    for p in patches:
        p.start()
    raised = writes = bad = 0
    try:
        for d, r in cells():
            got, out = run(d, r)
            raised += got
            writes += len(out)
            bad += sum(bool(b) for *_x, b in out)
            print(f"CELL {d}:{r}\tissue={'raised' if got else 'none'}\twrites={[(x[0], x[1], x[2]) for x in out]}"
                  + "".join(f"\tBAD {'; '.join(x[3])}" for x in out if x[3]))
    finally:
        for p in patches:
            p.stop()
    print(f"RESULT arm={'perturb:' + a.perturb if a.perturb else 'baseline'}")
    print(f"RESULT cells={len(cells())} count")
    print(f"RESULT issues_raised={raised} count")
    print(f"RESULT fix_writes={writes} count")
    print(f"RESULT bad_fix_writes={bad} count")
    pc, tc = time.process_time() - c0, time.thread_time() - th0
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(next((int(x.split()[1]) for x in open('/proc/vmstat') if x.startswith('pswpin')), 0)))


if __name__ == "__main__":
    main()
