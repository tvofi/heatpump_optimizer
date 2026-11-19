"""D12.M3 -- the pump-duty arbiter's command for every duty on every mode vocabulary and set-point domain.

Metric (one line): over (mode vocabulary x space set-point surface x space unit x duty), the
number of PumpCommands ``pump_arbiter.desired`` returns after one real cycle that (a) name a
mode the select does not offer, (b) put a set-point outside its entity's own declared range
(climate/water_heater min_temp/max_temp, number min/max), or (c) write a duty the vocabulary
cannot express as a single-duty mode (a mode written while the step is idle).
RESULT bad_commands; RESULT commands = the denominator.

Count key: the PumpCommand production's ``desired`` returns and the option label
``pump_arbiter._option_for`` resolves for it (what ``_write`` would send) -- never the
harness's own config.

Hooks: heatpump_optimizer.pump_arbiter:desired, pump_arbiter:_option_for, pump_arbiter:_bounded,
after heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data publishes a plan.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/duties.py
  ... duties.py --perturb range-keys   # inputs._RANGE_KEYS emptied: climate/water_heater read the decoy min/max -> bad_commands UP
  ... duties.py --reference            # M5 null arm: the fully-mapped coord_all_features plant
Expected at baseline 92d38ecb (export as handed over, box B6): bad_commands=0 exact both arms; perturbation > 0.
Machine: box B6, Linux x86_64, python 3.14, numpy 2.5.4 / scipy 1.18.1.
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
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer import pump_arbiter as A  # noqa: E402
from heatpump_optimizer import pump_mode  # noqa: E402

VOCABS = {"tuya": S.TUYA_OPTIONS, "modbus": S.MODBUS_OPTIONS, "none": None}
SPACE = {
    "number": ("number.sp", lambda v: S.T(v, min=18, max=22, step=0.5), lambda v: S.T(v, min=20, max=55, step=1)),
    "climate": ("climate.sp",
                lambda v: FakeState("heat", attributes={"temperature": v, "min_temp": 18, "max_temp": 22, "min": 5, "max": 35, "target_temp_step": 0.5}),
                lambda v: FakeState("heat", attributes={"temperature": v, "min_temp": 20, "max_temp": 55, "min": 5, "max": 80, "target_temp_step": 1})),
}
DHW_STATES = {
    "water_heater": ("water_heater.dhw_sp", FakeState("heat_pump", attributes={"temperature": 50, "min_temp": 42, "max_temp": 60, "min": 5, "max": 80, "target_temp_step": 1})),
    "number": ("number.dhw_sp", S.T(50, min=42, max=60, step=1)),
}
DUTIES = ("space", "dhw", "both", "idle", None)


def _rng(st):
    return S._range_of(st)


def run(reference, idx_base=0):
    commands = bad = 0
    lines = []
    i = idx_base
    for vname, options in VOCABS.items():
        for sname, (sent, indoor_state, flow_state) in SPACE.items():
            for unit in ("indoor", "flow"):
                for dname, (dent, dstate) in DHW_STATES.items():
                    i += 1
                    cfg = {**(S.REF_BASE if reference else S.GEN_BASE), **S.CONTROL,
                           c.CONF_SPACE_SETPOINT_ENTITY: sent, c.CONF_SPACE_SETPOINT_UNIT: unit,
                           c.CONF_DHW_SETPOINT_ENTITY: dent}
                    states = {**(S.REF_STATES if reference else S.GEN_STATES),
                              sent: (indoor_state(20) if unit == "indoor" else flow_state(35)),
                              dent: FakeState(dstate.state, attributes=dict(dstate.attributes))}
                    if options is not None:
                        cfg[c.CONF_HEAT_PUMP_MODE_ENTITY] = "select.hp_mode"
                        states["select.hp_mode"] = FakeState(options[-1] if vname == "modbus" else "Heating + DHW", attributes={"options": options})
                    hass, coord = S.build(cfg, states, entry_id=f"d12s3_duty_{i}_{int(reference)}")
                    try:
                        asyncio.run(coord._async_update_data())
                    except Exception as err:  # noqa: BLE001
                        lines.append(f"{vname}/{sname}/{unit}/{dname}: cycle raised {err!r}")
                        bad += 1
                        continue
                    inp = coord.arbiter_inputs()
                    now = dt_util.now()
                    for duty in DUTIES:
                        commands += 1
                        why = []
                        try:
                            cmd = A.desired(coord, inp, duty, now)
                        except Exception as err:  # noqa: BLE001
                            why.append(f"desired raised {err!r}")
                            cmd = None
                        if cmd is not None:
                            if cmd.mode is not None:
                                st = hass.states.get("select.hp_mode")
                                label = A._option_for(st, cmd.mode) if st is not None else None
                                if label is None:
                                    why.append(f"mode {cmd.mode} not offered by {options}")
                                if duty == "idle":
                                    why.append(f"idle step writes mode {cmd.mode}")
                            for slot, ent in (("space_setpoint", sent), ("dhw_setpoint", dent)):
                                v = getattr(cmd, slot)
                                if v is None:
                                    continue
                                lo, hi = _rng(hass.states.get(ent))
                                if (lo is not None and v < lo - 1e-9) or (hi is not None and v > hi + 1e-9):
                                    why.append(f"{slot}={v} outside [{lo},{hi}] of {ent}")
                        if why:
                            bad += 1
                        lines.append(f"{vname}/{sname}/{unit}/{dname}/{duty}: "
                                     f"{'BAD ' + '; '.join(why) if why else 'ok'} "
                                     f"{'' if cmd is None else (cmd.mode, cmd.space_setpoint, cmd.dhw_setpoint)}")
    return commands, bad, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["range-keys"])
    ap.add_argument("--reference", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    patches = []
    if a.perturb == "range-keys":
        from heatpump_optimizer import inputs as _inputs
        patches.append(mock.patch.object(_inputs, "_RANGE_KEYS", {}))
    t0, c0, th0 = time.time(), time.process_time(), time.thread_time()
    for p in patches:
        p.start()
    try:
        commands, bad, lines = run(a.reference)
    finally:
        for p in patches:
            p.stop()
    for ln in lines:
        if a.v or "BAD" in ln or "raised" in ln:
            print(ln)
    print(f"RESULT arm={'reference' if a.reference else 'generalization'}")
    print(f"RESULT commands={commands} count")
    print(f"RESULT bad_commands={bad} count")
    pc, tc = time.process_time() - c0, time.thread_time() - th0
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(next((int(x.split()[1]) for x in open('/proc/vmstat') if x.startswith('pswpin')), 0)))


if __name__ == "__main__":
    main()
