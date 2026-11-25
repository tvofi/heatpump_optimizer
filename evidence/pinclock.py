import sys, runpy, datetime as _d
hour = int(sys.argv[1]); script = sys.argv[2]; sys.argv = [script] + sys.argv[3:]
sys.path.insert(0, "tests/hastub"); sys.path.insert(0, __import__("os").path.dirname(script))
from homeassistant.util import dt as dt_util
_real = dt_util.now; _done = [False]
def _now(*a, **k):
    if not _done[0]:
        _done[0] = True
        return _d.datetime(2026, 11, 25, hour, 30, tzinfo=_d.timezone.utc)
    return _real(*a, **k)
dt_util.now = _now
runpy.run_path(script, run_name="__main__")
