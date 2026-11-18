# Probe: print the stack of the first non-import text read of a package source.
import sys, os, traceback
_done = []
def _hook(ev, args):
    if ev != "open" or _done:
        return
    p = args[0]
    if not isinstance(p, str) or "custom_components/heatpump_optimizer/coordinator.py" not in p:
        return
    f = sys._getframe(1)
    while f is not None:
        if f.f_code.co_filename.startswith("<frozen importlib"):
            return
        f = f.f_back
    _done.append(1)
    sys.stderr.write("PROBE-READ " + p + "\n" + "".join(traceback.format_stack()[-14:]) + "\n")
sys.addaudithook(_hook)
