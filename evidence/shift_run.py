"""Reviewer's own whole-script harness: run tests/features.py with the hastub
wall clock (homeassistant.util.dt.now/utcnow, unfrozen path) shifted by OFFSET
seconds, time still advancing. A freeze() inside the suite still wins.
usage: cd <tree> && python3 shift_run.py <offset_seconds>"""
import os, sys, runpy
from datetime import datetime as _dt, timedelta
off = timedelta(seconds=float(sys.argv[1]))
sys.path[:0] = [os.path.abspath("tests"), os.path.abspath("tests/hastub")]
from homeassistant.util import dt as hdt
class _Shift(_dt):
    @classmethod
    def now(cls, tz=None):
        return _dt.now(tz) + off
hdt.datetime = _Shift
print("SHIFTED-NOW", hdt.now().isoformat(), "weekday", hdt.now().weekday(), flush=True)
sys.argv = ["tests/features.py"]
runpy.run_path("tests/features.py", run_name="__main__")
