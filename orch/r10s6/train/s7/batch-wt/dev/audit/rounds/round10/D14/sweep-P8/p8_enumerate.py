"""Sweep P8 (round 10): enumerate every unit/currency resolution seam in the package.

Class P8: a currency or unit resolved by divergent precedence on different surfaces.
Seams (AST): (C) every resolve_currency(...) call outside currency.py -- the
instance-label resolver, which must not label feed-denominated money at runtime;
(T) every outbound temperature write (async_call set_temperature / set_value and
_write_setpoint) -- whose value must come from temperature_from_c with a unit
that falls back to hass.config.units.temperature_unit (setpoint_check._setpoint_and_unit).
FLAG rule: C-seam inside a runtime function not named in ALLOW_C; T-seam whose
value expression is not a Name/attr computed upstream by _setpoint_and_unit and
does not call temperature_from_c with a unit from _setpoint_and_unit.
Usage: python3 p8_enumerate.py [PKG_DIR]   (default custom_components/heatpump_optimizer)
Prints one SEAM line per seam and RESULT flagged=N seams=M.
"""
import ast, pathlib, sys

PKG = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "custom_components/heatpump_optimizer")
# C-seams that are not publishing surfaces: the guard that compares feed vs
# instance, the setup fallback, and options-dialog labels (guarded by the
# price_currency_mismatch repair, #1657).
ALLOW_C = {("coordinator.py", "_audit_price_units"), ("coordinator.py", "__init__"),
           ("config_flow.py", "_money"), ("config_flow.py", "async_step_grid"),
           ("config_flow.py", "async_step_grid_fees")}
TEMP_SERVICES = {"set_temperature", "set_value"}
NON_TEMP_HINT = ("freq", "night", "hz")


def funcs(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                sub._fn = getattr(sub, "_fn", None) or node.name
    return tree


def name(call):
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def seams(path):
    tree = funcs(ast.parse(path.read_text()))
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fn = getattr(n, "_fn", "<module>")
        nm = name(n)
        if nm == "resolve_currency" and path.name != "currency.py":
            yield "C", fn, n.lineno, (path.name, fn) not in ALLOW_C
        elif nm == "_write_setpoint" and fn != "_write_setpoint":
            arg = ast.unparse(n.args[2]) if len(n.args) > 2 else ""
            ok = "temperature_from_c" not in arg  # value precomputed upstream
            if "temperature_from_c" in arg:
                ok = "_setpoint_and_unit" in arg or "temperature_unit" in arg
            yield "T", fn, n.lineno, not ok if fn != "async_step_init" else False
        elif nm == "async_call" and len(n.args) >= 3 and isinstance(n.args[1], ast.Constant) \
                and n.args[1].value in TEMP_SERVICES and fn != "_write_setpoint":
            data = ast.unparse(n.args[2])
            if any(h in fn.lower() for h in NON_TEMP_HINT):
                yield "T", fn, n.lineno, False
                continue
            yield "T", fn, n.lineno, "temperature_from_c" not in data


flagged = total = 0
for p in sorted(PKG.rglob("*.py")):
    for kind, fn, line, flag in seams(p):
        total += 1; flagged += flag
        print(f"SEAM {kind} {p.name}:{line} {fn} {'FLAG' if flag else 'ok'}")
print(f"RESULT flagged={flagged} seams={total}")
