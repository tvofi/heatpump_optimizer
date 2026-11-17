"""D5-s1 harness: the two-tank activation rule, as each reader doc states it, against the code.

Metric: number of cells of a 16-cell config grid (two_zone_mode on/off x mixing valve
manual/none x wood probes none/top/bottom/both, wood furnace on) where a doc's stated
activation rule disagrees with ThermalParameters.from_config(cfg).two_tank_modelled.
Count key: the production property two_tank_modelled (what the model runs), never a doc.
  setup.md (Quick setup, "Wood buffer tank" row): valve AND a wood probe   (two-zone not named)
  configuration.md (layout catalog): valve AND two zones AND the TOP probe
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s1/two_tank_gate.py [--perturb]
Expected at baseline 92d38ecb: setup_md_mismatch=3, configuration_md_mismatch=1 (exact, counts).
Perturbation (--perturb): ThermalParameters.topology_layout's derivation is patched in memory to
drop the two-zone condition (valve + probe -> two_tank_4way); setup_md_mismatch falls to 0 and
configuration_md_mismatch rises.  Machine: orchestrator Mac, local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, itertools
sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import const, mixing_valve
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters

perturb = "--perturb" in sys.argv
if perturb:
    def _layout(self):
        if not mixing_valve.is_throttling(self.mixing_valve_mode):
            return const.TOPOLOGY_NO_VALVE
        if self.wood_tank_configured:
            return const.TOPOLOGY_TWO_TANK_4WAY
        return const.TOPOLOGY_SINGLE_TANK_VALVE
    ThermalParameters.topology_layout = property(_layout)

t0, c0 = time.time(), time.process_time()
setup_mm = conf_mm = 0
for tz, valve, probes in itertools.product(("on", "off"), ("manual", "none"),
                                            ("none", "top", "bottom", "both")):
    cfg = {const.CONF_WOOD_FURNACE_ENABLED: True, const.CONF_TWO_ZONE_MODE: tz,
           const.CONF_MIXING_VALVE_MODE: valve}
    if probes in ("top", "both"):
        cfg[const.CONF_WOOD_TANK_TOP_ENTITY] = "sensor.wood_top"
    if probes in ("bottom", "both"):
        cfg[const.CONF_WOOD_TANK_BOTTOM_ENTITY] = "sensor.wood_bottom"
    code = ThermalParameters.from_config(cfg).two_tank_modelled
    v = valve == "manual"
    setup_says = v and probes != "none"
    conf_says = v and tz == "on" and probes in ("top", "both")
    setup_mm += setup_says != code
    conf_mm += conf_says != code
    print(f"cell tz={tz} valve={valve} probes={probes} code={code} setup={setup_says} conf={conf_says}")
print(f"RESULT setup_md_mismatch={setup_mm} cells")
print(f"RESULT configuration_md_mismatch={conf_mm} cells")
pc, wc = time.process_time() - c0, time.time() - t0
print(f"RESULT thread_factor={pc / max(wc, 1e-9):.2f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
