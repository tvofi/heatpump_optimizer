"""Reviewer's harness v2: shift BOTH wall clocks by OFFSET seconds before anything
imports them -- datetime.datetime (the class every `from datetime import datetime`
binds), time.time, and hence the hastub dt clock -- so producers and consumers agree.
usage: cd <tree> && python3 shift_run2.py <offset_seconds>"""
import os, sys, runpy, time, datetime as _m
_D = _m.datetime
OFF = float(sys.argv[1])
off = _m.timedelta(seconds=OFF)
class datetime(_D):
    @classmethod
    def now(cls, tz=None):
        r = _D.now(tz) + off
        return cls(r.year, r.month, r.day, r.hour, r.minute, r.second, r.microsecond, r.tzinfo, fold=r.fold)
    @classmethod
    def utcnow(cls):
        return cls.now()
    @classmethod
    def today(cls):
        return cls.now()
class date(_m.date):
    @classmethod
    def today(cls):
        d = datetime.now().date(); return cls(d.year, d.month, d.day)
_m.datetime = datetime
_m.date = date
_rt = time.time
time.time = lambda: _rt() + OFF
sys.path[:0] = [os.path.abspath("tests"), os.path.abspath("tests/hastub")]
from homeassistant.util import dt as hdt
print("SHIFTED-NOW", hdt.now().isoformat(), "weekday", hdt.now().weekday(), _m.datetime.now().isoformat(), flush=True)
sys.argv = ["tests/features.py"]
runpy.run_path("tests/features.py", run_name="__main__")
