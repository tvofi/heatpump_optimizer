#!/usr/bin/env python3
"""D7 verify-v3 (D7-s2-02): does the derate fold a backup-heater interval when
the contamination arrives only as Home Assistant entity states through the
coordinator's own update cycle (no internal attribute is set by the harness)?

Metric (one line): over N consecutive coordinator:_async_update_data cycles
(30-min frozen-clock steps, outdoor 2 C, flag-less, meter 6000 W), the number
of cycles on which defrost:DefrostDerate.counts rises while
coordinator:_cop_fold_blocked(coord) is True; plus the published
coord._defrost.factor(2.0, 85) and factor(2.0, None) after the run.
Count key: DefrostDerate.counts (production state), contamination only via
hass.states (binary_sensor.backup_heater = on/off, read by pump_signals.read_electric_heat).
Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/verify-v3/derate_cycle.py [--cycles N] [--gate-derate]
Perturbation: --gate-derate (the finder's in-memory gate: _settle_defrost returns
when _cop_fold_blocked) -> blocked_folds must fall to 0; clean arm unchanged.
Null control: the 'off' arm (backup heater off): blocked_folds must be 0 by construction.
Machine: cloud container linux x86_64 (4 cores, shared). Counts are contention-immune.
Stub note: FakeHass runs executor jobs inline; the path read here holds no
executor or timing dependence, and the only stub-divergent symbols it touches
(tests/ha_contract.py: util.dt.as_local / DEFAULT_TIME_ZONE) are not on it
unless HASTUB_TZ is set (it is not).
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, asyncio, sys, time  # noqa: E401,E402
from datetime import datetime, timedelta  # noqa: E402
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

START = datetime(2026, 1, 12, 1, 0)


def run_arm(backup_on: bool, cycles: int) -> dict:
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState(os.environ.get("D7V3_INDOOR", "18.0")))
    hass.states.set("sensor.outdoor", FakeState("2.0"))
    hass.states.set("sensor.humidity", FakeState("85"))
    hass.states.set("sensor.hp_power", FakeState(os.environ.get("D7V3_METER_W", "6000"), unit="W"))
    hass.states.set("binary_sensor.backup_heater", FakeState("on" if backup_on else "off"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_max_power": 6.0,
        const.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY: "binary_sensor.backup_heater",
    }
    hum = getattr(const, "CONF_OUTDOOR_HUMIDITY_ENTITY", None)
    if hum:
        cfg[hum] = "sensor.humidity"
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))

    async def _prices() -> None:
        t0 = dt_util.now().replace(minute=0, second=0, microsecond=0)
        coord._prices = [{"total": 1.0, "starts_at": (t0 + timedelta(hours=h)).isoformat()}
                         for h in range(48)]
    coord._fetch_tibber_prices = _prices
    folds_blocked = folds = blocked_cycles = errors = 0
    now = START
    for i in range(cycles):
        dt_util.freeze(now)
        for eid in ("sensor.indoor", "sensor.outdoor", "sensor.humidity", "sensor.hp_power",
                    "binary_sensor.backup_heater"):
            st = hass.states.get(eid)
            hass.states.set(eid, FakeState(st.state, last_updated=now,
                                           unit=st.attributes.get("unit_of_measurement")))
        before = sum(sum(r) for r in coord._defrost.counts)
        try:
            asyncio.run(coord._async_update_data())
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  cycle {i}: {type(e).__name__}: {str(e)[:120]}")
        after = sum(sum(r) for r in coord._defrost.counts)
        blocked = bool(C._cop_fold_blocked(coord))
        blocked_cycles += int(blocked)
        if after > before:
            folds += 1
            if blocked:
                folds_blocked += 1
        print(f"  {'on ' if backup_on else 'off'} cycle {i}: power_cmd={coord._current_action.get('power', 0):.2f} "
              f"measured={coord._measured_power} blocked={blocked} derate_counts {before}->{after}")
        now += timedelta(minutes=30)
    dt_util.freeze(None)
    return {"folds": folds, "folds_blocked": folds_blocked, "blocked_cycles": blocked_cycles,
            "errors": errors, "factor": coord._defrost.factor(2.0, 85.0),
            "factor_nohum": coord._defrost.factor(2.0, None)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--gate-derate", action="store_true")
    a = ap.parse_args()
    if a.gate_derate:
        orig = C.HeatPumpOptimizerCoordinator._settle_defrost

        def gated(self, sample, window):
            if C._cop_fold_blocked(self):
                return None
            return orig(self, sample, window)
        C.HeatPumpOptimizerCoordinator._settle_defrost = gated
    c0, t0 = time.process_time(), time.thread_time()
    for label, on in (("off", False), ("on", True)):
        r = run_arm(on, a.cycles)
        for k, v in r.items():
            isf = k.startswith("factor")
            print(f"RESULT {label}_{k}={v:.4f} ratio" if isf else f"RESULT {label}_{k}={v} count")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "n/a")
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
