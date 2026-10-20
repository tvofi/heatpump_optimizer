import importlib.util, sys
spec = importlib.util.spec_from_file_location("drv", "tools/audit/seat/r10_deeplink_mutants.py")
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)
# An unplanted member of the same kind CAP8 plants: a timer member taken at load.
# CAP8 plants setTimeout; this plants setInterval, and the callback navigates.
CAP_SI = drv.at_load(
    "const __capSI = globalThis[['set','Interval'].join('')];",
    "try { __capSI(() => { try { globalThis.history.back(); } catch (_e) {} }, 50); } catch (_e) {}")
drv.run("PROBE_CAP_SI_set_interval_captured_at_load", CAP_SI)
