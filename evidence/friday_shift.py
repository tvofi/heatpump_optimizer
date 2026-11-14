# reviewer-built control: run tests/features.py with the hastub dt_util.now shifted back one day (a Friday on 2026-11-14)
import sys, runpy, datetime
sys.path[0:0] = ["tests", "tests/hastub"]
import homeassistant.util.dt as d
_now = d.now
d.now = lambda *a, **k: _now(*a, **k) - datetime.timedelta(days=1)
sys.argv = ["tests/features.py"]
runpy.run_path("tests/features.py", run_name="__main__")
