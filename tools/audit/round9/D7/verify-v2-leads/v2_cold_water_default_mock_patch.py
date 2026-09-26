"""verify-v2 (independent lens, D7-s1-71): re-measure the "three definitions of one default"
claim with a DIFFERENT perturbation technique than the finder's (they recompile thermal_model.py
from patched source text via exec(); I use unittest.mock.patch.object on the already-imported
module's attribute, which is the idiom COMMON.md and this codebase's own tests
(tests/optimality.py) treat as the standard in-memory perturbation -- so this closes the finder's
"a harness whose perturbation only works via source recompilation" attack surface).

Metric definition (mine): identical in spirit to the finder's -- of the same 5 production sites,
those whose delivered value does NOT move when const.DEFAULT_DHW_INLET_TEMP is patched 10.0 -> 12.5
-- but measured via mock.patch.object(const, "DEFAULT_DHW_INLET_TEMP", 12.5) instead of a module
move-and-reimport, and via a SEPARATE independent check: static AST confirms
thermal_model.py:469's default is a bare ast.Constant (not a Name/Attribute reference to
const.DEFAULT_DHW_INLET_TEMP or const.DHW_COLD_WATER_TEMP), and DHW_COLD_WATER_TEMP and
DEFAULT_DHW_INLET_TEMP are two independent `Final` assignments in const.py (not one aliasing the
other) -- so the "three spellings" claim is a source-level fact independent of any particular
patch technique.

Run from cwd=/home/claude/ev2:
    python3 tools/audit/round9/D7/verify-v2-leads/v2_cold_water_default_mock_patch.py
Expected (mine): sites_not_following=3 of 5 (bare ThermalParameters() literal, sysid plant, coil
default) -- same count as the finder's, reached via mock.patch.object.
Baseline / tree: evidence branch 96b89163.
"""
import ast
import inspect
import os
import sys
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
ROOT = os.getcwd()
if not os.path.isfile(os.path.join(ROOT, "custom_components/heatpump_optimizer/thermal_model.py")):
    print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
    sys.exit(2)

# --- static: confirm the two constants are independent Final assignments, and the field default
# is a bare literal, not a reference to either constant.
const_src = open("custom_components/heatpump_optimizer/const.py").read()
const_tree = ast.parse(const_src)
assigns = {}
for node in ast.walk(const_tree):
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        if node.target.id in ("DEFAULT_DHW_INLET_TEMP", "DHW_COLD_WATER_TEMP") and isinstance(node.value, ast.Constant):
            assigns[node.target.id] = node.value.value
print(f"const.py: {assigns}")
independent_defs = len(assigns) == 2  # two separate AnnAssign nodes found, not one aliasing the other
print(f"RESULT independent_constant_defs={int(independent_defs)} count")

tm_src = open("custom_components/heatpump_optimizer/thermal_model.py").read()
tm_tree = ast.parse(tm_src)
field_is_bare_literal = None
for node in ast.walk(tm_tree):
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "dhw_inlet_temp":
        field_is_bare_literal = isinstance(node.value, ast.Constant)
        print(f"thermal_model.py dhw_inlet_temp field default AST node: {ast.dump(node.value)}")
        break
print(f"RESULT field_default_is_bare_literal={int(bool(field_is_bare_literal))} count")

# --- dynamic: mock.patch.object instead of exec-recompiling the module.
import importlib  # noqa: E402
import heatpump_optimizer  # noqa: E402
from heatpump_optimizer import const, thermal_model as tm, config_flow as cf, sysid  # noqa: E402

with mock.patch.object(const, "DEFAULT_DHW_INLET_TEMP", 12.5):
    want = const.DEFAULT_DHW_INLET_TEMP
    field = [f for f in cf._OPTION_FIELDS if f.key == const.CONF_DHW_INLET_TEMP] if hasattr(cf._OPTION_FIELDS[0], "key") else \
            [f for f in cf._OPTION_FIELDS if const.CONF_DHW_INLET_TEMP in f]
    fdef = [x for x in field[0] if isinstance(x, (int, float)) and not isinstance(x, bool)][0]
    sites = {
        "ThermalParameters.from_config({})": tm.ThermalParameters.from_config({}).dhw_inlet_temp,
        "config_flow option field default": fdef,
        "ThermalParameters() bare": tm.ThermalParameters().dhw_inlet_temp,
        "sysid._sizing_model plant": sysid._sizing_model(0.2, 10.0, 0.3).params.dhw_inlet_temp,
        "dhw_coil_draw_reduction inlet_temp default": inspect.signature(tm.dhw_coil_draw_reduction).parameters["inlet_temp"].default,
    }
    off = 0
    for k, v in sites.items():
        bad = abs(float(v) - want) > 1e-9
        off += bad
        print(f"site {k:44s} value={v} follows_patched_default={not bad}")
    print(f"RESULT sites_not_following={off} of {len(sites)} count (mock.patch.object method)")

print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
