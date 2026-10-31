
import json, os, sys
root, out_path, specs_path = sys.argv[1:4]
os.chdir(root)
for part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(root, part))
import inspect, stress
from heatpump_optimizer import optimizer as _opt
PACKAGE = os.path.dirname(os.path.abspath(_opt.__file__))
def production_calls(fn, package_dir):
    """Run ``fn()`` and count the calls production bytecode executes.

    Returns ``(fn's result, {file basename: count})``: every function entry
    (``PY_START``) in a file under ``package_dir`` -- a property getter's
    body included, which no ``CALL`` reaches -- plus every call site
    (``CALL``) such a file's bytecode executes, a numpy call in a per-row
    loop included. A location outside the package returns ``DISABLE`` on
    first sight, so the meter costs one callback per production event. Its
    source is embedded in CALLS_PROBE_DRIVER, so both trees are counted by
    the same text.
    """
    import os as _os
    import sys as _sys

    mon = _sys.monitoring
    tool = 4
    if mon.get_tool(tool) is not None:
        raise RuntimeError(f"sys.monitoring tool {tool} is taken by {mon.get_tool(tool)!r}")
    prefix = _os.path.abspath(package_dir) + _os.sep
    counts = {}
    disable = mon.DISABLE

    def count(code, *_):
        name = code.co_filename
        if not name.startswith(prefix):
            return disable
        counts[name] = counts.get(name, 0) + 1

    mon.use_tool_id(tool, "hpo-production-calls")
    try:
        mon.register_callback(tool, mon.events.PY_START, count)
        mon.register_callback(tool, mon.events.CALL, count)
        mon.set_events(tool, mon.events.PY_START | mon.events.CALL)
        result = fn()
    finally:
        mon.set_events(tool, 0)
        mon.register_callback(tool, mon.events.PY_START, None)
        mon.register_callback(tool, mon.events.CALL, None)
        mon.free_tool_id(tool)
        mon.restart_events()
    return result, {_os.path.basename(k): v for k, v in sorted(counts.items())}

rows = {}
with open(specs_path, encoding="utf-8") as fh:
    specs = json.load(fh)
for combo in specs:
    label = combo.pop("label")
    try:  # a tree whose build_case lacks an argument the spec names
        inspect.signature(stress.build_case).bind(**combo)
    except TypeError as exc:
        rows[label] = {"unbuildable": str(exc)}
        continue
    run, files = production_calls(lambda: stress.build_case(**combo), PACKAGE)
    rows[label] = {
        "calls": files,
        "evals": int(run["solver_evals"]),
        "simulate": int(run.get("solver_simulate_steps") or 0),
        "objective": float(run["result"].objective_value),
    }
with open(out_path, "w") as fh:
    json.dump(rows, fh, indent=1, sort_keys=True)
