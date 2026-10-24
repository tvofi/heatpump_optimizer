"""l3_update_interval: can any test read the cadence the coordinator was built with?

Metric (one line): configured optimization_interval cells whose cadence is NOT readable as
coordinator.update_interval through the hastub DataUpdateCoordinator (upstream stores it);
key = getattr(coordinator, "update_interval") after the real HeatPumpOptimizerCoordinator.__init__.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/l3_update_interval.py [--perturb store]
Expected: unreadable_cells=4 of 4 (exact); undeclared_in_ha_contract=1 (update_interval is not in
          ha_contract.py's `absent` tuple for DataUpdateCoordinator, so the divergence is undeclared);
          --perturb store (stub __init__ keeps update_interval, in memory) -> unreadable_cells=0 and
          matching_cells=4. Null control: the attributes the stub does keep (name, config_entry)
          are readable in 4 of 4.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbol: tests/hastub/homeassistant/helpers/update_coordinator.py:DataUpdateCoordinator.__init__
driven by custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.__init__.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, sys, time
from datetime import timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
t0p, t0t = time.process_time(), time.thread_time()
from homeassistant.helpers import update_coordinator as uc
from harness import FakeHass, FakeEntry
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.const import CONF_OPTIMIZATION_INTERVAL

PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "store"
if PERTURB:
    _orig = uc.DataUpdateCoordinator.__init__

    def _keeping(self, *a, update_interval=None, **k):
        _orig(self, *a, update_interval=update_interval, **k)
        self.update_interval = update_interval
    uc.DataUpdateCoordinator.__init__ = _keeping

MISSING = object()
unreadable = matching = ctl = 0
CELLS = (5, 15, 30, 60)
for minutes in CELLS:
    coord = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data={CONF_OPTIMIZATION_INTERVAL: minutes}))
    got = getattr(coord, "update_interval", MISSING)
    unreadable += got is MISSING
    matching += got == timedelta(minutes=minutes)
    ctl += getattr(coord, "name", MISSING) is not MISSING and getattr(coord, "config_entry", MISSING) is not MISSING
    print(f"cell interval={minutes:3d} min update_interval={'<absent>' if got is MISSING else got}")

# does the stub's own authority (ha_contract.py inventory) declare it absent?
tree = ast.parse(open("tests/ha_contract.py").read())
declared = False
for node in ast.walk(tree):
    if isinstance(node, ast.keyword) and node.arg == "absent" and isinstance(node.value, ast.Tuple):
        if any(isinstance(e, ast.Constant) and e.value == "update_interval" for e in node.value.elts):
            declared = True
print(f"RESULT unreadable_cells={unreadable} of {len(CELLS)} count")
print(f"RESULT matching_cells={matching} of {len(CELLS)} count")
print(f"RESULT null_control_kept_attrs_readable={ctl} of {len(CELLS)} count")
print(f"RESULT undeclared_in_ha_contract={int(not declared)} count")
print(f"RESULT perturbed={int(PERTURB)}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
