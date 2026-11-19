"""N-staleness consequence (D14-s2, round 11): a quiet push-mode pump flag publishes Input Problem.

Metric: number of the six pump-flag inputs (defrost, online, fault, backup
heater, DHW booster, capacity limited) the real coordinator publishes in its
payload's ``stale_inputs`` after one real input cycle
(``HeatPumpOptimizerCoordinator._update_current_state`` then
``_build_data_dict``), when each flag is a report-on-change source
(``last_reported == last_updated``, what an MQTT push integration writes) that
has legitimately held its value for Q minutes; plus whether the real
``binary_sensor.InputHealthBinarySensor`` built over that payload is on.
Key: the payload's ``stale_inputs`` list and the entity's ``is_on``, both as
production delivers them; never the const table.

Arms:
  quiet   flags held 255 min on change (indoor/outdoor polling and fresh)
  null    the same flags last changed 10 min ago -> 0 stale, Input Problem off
  polled  the same 255 min hold, re-reported 1 min ago (a polling source) -> 0
Perturbation: ``--perturb inf`` sets INPUT_ON_CHANGE_MAX_AGE_MINUTES[k] = inf
for the six keys in memory (what the class's own power/mode rows already
declare) -> quiet arm 6 -> 0, Input Problem on -> off.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/staleness_flags.py [--perturb inf]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7, linux), exact counts:
  RESULT quiet_stale_flags=6, quiet_input_problem_on=1, null_stale_flags=0,
  null_input_problem_on=0, polled_stale_flags=0, polled_input_problem_on=0;
  under --perturb inf: quiet_stale_flags=0, quiet_input_problem_on=0.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import asyncio
import sys
import time

sys.path.insert(0, "tests")
import harness  # noqa: E402
from harness import FakeCoordinator, FakeEntry, FakeHass, FakeState, minutes_ago  # noqa: E402
from heatpump_optimizer import binary_sensor, const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

FLAGS = {
    const.CONF_HEAT_PUMP_DEFROST_ENTITY: ("binary_sensor.hp_defrost", "off"),
    const.CONF_HEAT_PUMP_ONLINE_ENTITY: ("binary_sensor.hp_online", "on"),
    const.CONF_HEAT_PUMP_FAULT_ENTITY: ("binary_sensor.hp_fault", "off"),
    const.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY: ("binary_sensor.hp_backup", "off"),
    const.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY: ("binary_sensor.hp_booster", "off"),
    const.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: ("binary_sensor.hp_limited", "off"),
}


def _cycle(held_min, reported_min):
    hass = FakeHass()
    fresh = minutes_ago(1)
    hass.states.set("sensor.indoor", FakeState("21.4", last_updated=minutes_ago(20), last_reported=fresh))
    hass.states.set("sensor.outdoor", FakeState("-3.0", last_updated=minutes_ago(20), last_reported=fresh))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    for key, (eid, val) in FLAGS.items():
        config[key] = eid
        hass.states.set(
            eid,
            FakeState(
                val,
                last_updated=minutes_ago(held_min),
                last_reported=None if reported_min is None else minutes_ago(reported_min),
            ),
        )
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    data = coord._build_data_dict()
    stale = sorted(set(data.get("stale_inputs") or []) & set(FLAGS))
    on = binary_sensor.InputHealthBinarySensor(FakeCoordinator(data), FakeEntry(data=config)).is_on
    return stale, bool(on), data.get("learners_frozen")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=("none", "inf"), default="none")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    if a.perturb == "inf":
        for k in FLAGS:
            const.INPUT_ON_CHANGE_MAX_AGE_MINUTES[k] = float("inf")
    for arm, held, rep in (("quiet", 255, None), ("null", 10, None), ("polled", 255, 1)):
        stale, on, frozen = _cycle(held, rep)
        for k in stale:
            print(f"SEAM arm={arm} key={k}")
        print(f"RESULT {arm}_stale_flags={len(stale)} keys")
        print(f"RESULT {arm}_input_problem_on={int(on)}")
        print(f"RESULT {arm}_learners_frozen={int(bool(frozen))}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
