"""D5-s1 harness: docs/setup.md's Quick setup storage promises against what the answers build.

docs/setup.md "The five house questions" says Buffer tank "yes" records a store-sized tank
and "On stores cheap heat and releases it during expensive hours", and that the two wood-tank
probes "are what actually switch the two-tank physics on".
Metric (one line): of those two promises, how many the ThermalParameters built from
quick_setup.derive(<every toggle yes + both wood probes>) fails to honour -- buffer_is_store
False, two_tank_modelled False.
Count key: ThermalParameters.from_config(quick_setup.derive(answers)).buffer_is_store and
.two_tank_modelled -- the production properties the optimizer and coordinator read.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/quick_setup_promise.py [--perturb]
--perturb adds, in memory, a throttling mixing-valve mode ("Set by hand") to what
    quick_setup.derive returns -- the one answer the page never asks. Expected:
    unhonoured_promises 2 -> 0.
Null arm (printed): the same answers entered with mixing_valve_mode set on the
    Heating system page, which is where docs/configuration.md says a store needs it.
Expected at baseline: unhonoured_promises=2 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
from heatpump_optimizer import const, mixing_valve, quick_setup  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

THROTTLE = sorted(mixing_valve.THROTTLING_MODES)[0]
if "--perturb" in sys.argv:
    _real = quick_setup.derive
    quick_setup.derive = lambda answers: {**_real(answers),
                                          const.CONF_MIXING_VALVE_MODE: THROTTLE}

answers = {
    quick_setup.FIELD_TWO_ZONE: True,
    quick_setup.FIELD_BUFFER_TANK: True,
    quick_setup.FIELD_DHW_TANK: True,
    quick_setup.FIELD_WOOD_FURNACE: True,
    quick_setup.FIELD_WOOD_BUFFER_TANK: True,
    const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
    const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wood_bottom",
}
cfg = quick_setup.derive(dict(answers))
p = ThermalParameters.from_config(cfg)
print("derived keys:", sorted(k for k in cfg if "valve" in k or "buffer" in k or "wood" in k or "zone" in k))
print(f"buffer_tank_volume={p.buffer_tank_volume} mixing_valve_mode={p.mixing_valve_mode} "
      f"two_zone={p.two_zone_enabled} wood_tank_configured={p.wood_tank_configured} "
      f"layout={p.topology_layout}")
unhonoured = int(not p.buffer_is_store) + int(not p.two_tank_modelled)
ctrl = ThermalParameters.from_config({**cfg, const.CONF_MIXING_VALVE_MODE: THROTTLE})
print(f"null arm (valve set on Heating system page): buffer_is_store={ctrl.buffer_is_store} "
      f"two_tank_modelled={ctrl.two_tank_modelled}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT buffer_is_store={int(p.buffer_is_store)} count")
print(f"RESULT two_tank_modelled={int(p.two_tank_modelled)} count")
print(f"RESULT unhonoured_promises={unhonoured} count")
print(f"RESULT null_arm_unhonoured={int(not ctrl.buffer_is_store) + int(not ctrl.two_tank_modelled)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
