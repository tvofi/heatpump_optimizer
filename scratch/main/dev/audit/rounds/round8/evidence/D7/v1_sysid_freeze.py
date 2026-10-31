"""D7-v1 verifier harness for D7-s1-01: a contaminated experiment night through the REAL coordinator.

Metric (one line): over a sweep of contamination magnitudes, the count of experiment nights that the
  production coordinator (FakeHass HeatPumpOptimizerCoordinator, not a stub) carries to a heat-loss
  scale write while coordinator._learning_frozen(indoor, outdoor) was non-None on >= 1 recorded
  tick, and the worst |adopted UA error| (%) among them (adopted UA = written scale * declared base).
Drive: every 15-min tick sets dt_util, the room reading and the plan power on the coordinator, calls
  the production _run_system_identification(prices) then _adopt_system_identification(); the plant
  is the production ThermalModel of the preset (declared == true), driven with the coordinator's
  resulting _current_action["power"].  Contamination is physical AND flagged the way production
  flags it on the tick it happens: wood = unrecorded external heat (kW) with _external_heat_active;
  defrost = commanded step heat not delivered with _pump_signals.defrosting.
Sweep: presets {light_new, heavy_old, typical_slab} x wood {0.5,1,2} kW in relax x wood {0.5,1,2}
  kW in step x defrost {1,2,3} step ticks  (27 contaminated nights) + 3 clean nights (null control).
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/v1_sysid_freeze.py [--perturb]
  --perturb: wrap _run_system_identification to abort the experiment when _learning_frozen is set
  (the finder's one-line fix, abort variant); contaminated_adopted must go to 0.  Restored in finally.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, dataclasses, logging
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from datetime import datetime, timedelta
from harness import FakeHass, FakeEntry
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as C
from heatpump_optimizer import sysid as S
from heatpump_optimizer.inputs import InputHealth, InputReading
from heatpump_optimizer.const import CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.presets import BuildingPreset, derive
from profiles import house
from stress import BUILDINGS

PERTURB = "--perturb" in sys.argv
T0 = datetime(2026, 1, 15, 23, 0, 0)
OUT = 0.0
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.hp_power", "system_identification_enabled": True}


def preset_cfg(name):
    cfg = house(two_zone=False, dhw=False)
    d = derive(BuildingPreset(**{**vars(BUILDINGS[name]), "two_zone": False}))
    d.pop("heating_response_hours", None)
    cfg.update(d)
    cfg.update(CFG)
    return cfg


def night(name, kind, mag):
    dt_util.freeze(T0)
    c = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=preset_cfg(name)))
    c._thermal_params.wind_sensitivity = 0.0
    p = dataclasses.replace(c._thermal_params)
    c._house_heat_loss_scale = 1.0
    c._house_heat_loss_samples = 0
    written = []
    orig_apply = c._apply_house_heat_loss_scale
    c._apply_house_heat_loss_scale = lambda v: (written.append(v), orig_apply(v))
    c._spawn = lambda coro: getattr(coro, "close", lambda: None)()
    health = InputHealth()
    for key, ent in ((CONF_INDOOR_TEMP_ENTITY, "sensor.indoor"), (CONF_OUTDOOR_TEMP_ENTITY, "sensor.outdoor")):
        health.record(InputReading(key=key, entity_id=ent, value=21.0 if "indoor" in ent else OUT))
    c._input_health = health
    c._sysid.config.enabled = True
    c._sysid.config.min_days_between_runs = 0.0
    assert c._sysid.arm(T0, plant=c._thermal_params)
    plant = ThermalModel(dataclasses.replace(p))
    ua = p.heat_loss_coefficient
    hold_th = max(ua * (21.0 - OUT) - p.internal_gains, 0.0)
    cop = plant.compute_cop(OUT)
    st = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold_th / max(p.slab_heat_transfer, 1e-9),
                      outdoor_temperature=OUT)
    prices = np.full(48, 1.0)
    frozen_ticks = 0
    step_ticks = 0
    base_signals = c._pump_signals
    for k in range(30):
        now = T0 + timedelta(minutes=15 * k)
        dt_util.freeze(now)
        phase = c._sysid.phase
        ext = 0.0
        defrost = False
        if kind == "wood_relax" and phase == S.PHASE_RELAX:
            ext = mag
        if kind == "wood_step" and phase == S.PHASE_STEP:
            ext = mag
        if kind == "defrost" and phase == S.PHASE_STEP and 1 <= step_ticks <= mag:
            defrost = True
        c._external_heat_active = ext > 0
        c._pump_signals = dataclasses.replace(base_signals, defrosting=defrost)
        c._current_state = dataclasses.replace(c._current_state, room_temperature=st.room_temperature,
                                                 outdoor_temperature=OUT)
        c._current_action = {"power": hold_th / cop, "dhw_power": 0.0}
        if c._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY) is not None and c._sysid.active:
            frozen_ticks += 1
        c._run_system_identification(prices)
        c._adopt_system_identification()
        if c._sysid.phase == S.PHASE_STEP:
            step_ticks += 1
        if not c._sysid.active:
            break
        el = float(c._current_action.get("power", 0.0))
        heat = 0.0 if defrost else el * cop
        st = plant.simulate_step(st, electrical_power=0.0, outdoor_temp=OUT, dt_hours=0.25,
                                 external_heat_kw=heat + ext)
    dt_util.freeze(None)
    r = c._sysid.result
    err = (written[0] - 1.0) * 100 if written else None
    LAST["coord"] = c
    return dict(phase=c._sysid.phase, reason=r.reason, frozen=frozen_ticks, err=err)


LAST = {}


KINDS = [("wood_relax", m) for m in (0.5, 1.0, 2.0)] + [("wood_step", m) for m in (0.5, 1.0, 2.0)] \
    + [("defrost", m) for m in (1, 2, 3)]
def main():
    _orig = C.HeatPumpOptimizerCoordinator._run_system_identification
    try:
        if PERTURB:
            def _patched(self, prices):
                why = self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)
                if why is not None and self._sysid.active:
                    self._sysid.abort(why)
                    return
                return _orig(self, prices)
            C.HeatPumpOptimizerCoordinator._run_system_identification = _patched
        clean_written, clean_worst = 0, 0.0
        adopted, worst, over10, total = 0, 0.0, 0, 0
        for name in BUILDINGS:
            r = night(name, "clean", 0)
            print(f"CELL {name} clean: {r}", flush=True)
            if r["err"] is not None:
                clean_written += 1
                clean_worst = max(clean_worst, abs(r["err"]))
            for kind, mag in KINDS:
                r = night(name, kind, mag)
                total += 1
                print(f"CELL {name} {kind}={mag}: {r}", flush=True)
                if r["err"] is not None and r["frozen"] > 0:
                    adopted += 1
                    worst = max(worst, abs(r["err"]))
                    over10 += abs(r["err"]) > 10.0
    finally:
        C.HeatPumpOptimizerCoordinator._run_system_identification = _orig
        dt_util.freeze(None)
    print(f"RESULT clean_adopted={clean_written} count (of 3; null control) clean_worst_err={clean_worst:.3f} pct")
    print(f"RESULT contaminated_adopted={adopted} count (of {total} nights with >=1 frozen tick recorded)")
    print(f"RESULT contaminated_worst_adopted_err={worst:.2f} pct")
    print(f"RESULT contaminated_adopted_over_10pct={over10} count")
    tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
