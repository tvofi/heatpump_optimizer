"""Bootstrap for dead_code.py: run one test script under sys.monitoring, record every code
object under D7_PKG_PREFIX that STARTS at least once, dump the set to D7_MON_OUT on exit.
Not a harness on its own; dead_code.py is the one command."""
import atexit
import json
import os
import runpy
import sys

PREFIX = os.environ["D7_PKG_PREFIX"]
OUT = os.environ["D7_MON_OUT"]
seen = set()


def cb(code, offset):
    if code.co_filename.startswith(PREFIX):
        seen.add((os.path.relpath(code.co_filename, PREFIX), code.co_firstlineno, code.co_qualname))
    return sys.monitoring.DISABLE


TOOL = sys.monitoring.COVERAGE_ID
sys.monitoring.use_tool_id(TOOL, "d7")
sys.monitoring.register_callback(TOOL, sys.monitoring.events.PY_START, cb)
sys.monitoring.set_events(TOOL, sys.monitoring.events.PY_START)


def dump():
    with open(OUT, "w") as f:
        json.dump(sorted(seen), f)


atexit.register(dump)
script = sys.argv[1]
sys.argv = sys.argv[1:]
# `python tests/x.py` puts tests/ first on sys.path; runpy from here would not, and every
# script that does `from harness import ...` without inserting its own directory would fail.
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit:
    pass
