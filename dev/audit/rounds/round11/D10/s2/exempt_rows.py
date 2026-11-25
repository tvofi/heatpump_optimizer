"""D10-s2 gold exempt rows stay true (D10-criteria Q3): discovery,
discovery-update-info, dynamic-devices, stale-devices; and the devices row.

Counts:
  discovery_manifest_keys   manifest keys that register a discovery mechanism
                            (bluetooth, dhcp, homekit, mqtt, ssdp, usb, zeroconf)
  discovery_steps           async_step_<mechanism>/hassio/integration_discovery
                            methods on the config flow
  device_registry_writes    calls of async_get_or_create / async_remove_device /
                            async_update_device / async_clear_config_entry
  remove_device_hook        async_remove_config_entry_device defined in __init__
  distinct_devices          distinct device identifier sets over every entity
                            the platforms add (census), and the entry_type
Metric: q3_contradictions = discovery_manifest_keys + discovery_steps +
device_registry_writes + remove_device_hook + (distinct_devices != 1).
Key: the shipped manifest and source, and the device_info each entity publishes.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/exempt_rows.py [--perturb]
Expected at baseline 92d38ecb: RESULT q3_contradictions=0, exact.
--perturb adds "zeroconf" to the manifest dict in memory: rises to 1.
Instrumented symbol: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.device_info
(through every entity's device_info) and custom_components/heatpump_optimizer/manifest.json.
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census as c  # noqa: E402

manifest = c.load_json("manifest.json")
if "--perturb" in sys.argv:
    manifest["zeroconf"] = ["_x._tcp.local."]
MECH = ("bluetooth", "dhcp", "homekit", "mqtt", "ssdp", "usb", "zeroconf")
keys = [k for k in MECH if k in manifest]
steps, writes, hook = [], [], 0
for path in sorted(c.PKG.glob("*.py")):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in {f"async_step_{m}" for m in MECH + ("hassio", "integration_discovery", "discovery")}:
                steps.append(f"{path.name}:{node.name}")
            if node.name == "async_remove_config_entry_device":
                hook += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in (
                "async_get_or_create", "async_remove_device", "async_update_device", "async_clear_config_entry"):
            src = ast.unparse(node.func.value)
            if "entity_registry" not in src and "er." not in src:
                writes.append(f"{path.name}:{node.lineno} {src}.{node.func.attr}")
ents, coord, entry = c.entities()
devices = {frozenset((e.device_info or {}).get("identifiers") or ()) for _, e in ents}
types = {str((e.device_info or {}).get("entry_type")) for _, e in ents}
print("DISCOVERY_KEYS", keys, "STEPS", steps, "WRITES", writes, "ENTRY_TYPES", types)
print(f"RESULT discovery_manifest_keys={len(keys)} count")
print(f"RESULT discovery_steps={len(steps)} count")
print(f"RESULT device_registry_writes={len(writes)} count")
print(f"RESULT remove_device_hook={hook} count")
print(f"RESULT distinct_devices={len(devices)} count")
q3 = len(keys) + len(steps) + len(writes) + hook + (len(devices) != 1)
print(f"RESULT q3_contradictions={q3} count")
c.stats()
