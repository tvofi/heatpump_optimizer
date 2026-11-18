import sys; sys.path[:0]=[sys.argv[1]+'/tests/hastub', sys.argv[1]+'/custom_components', sys.argv[1]+'/tests']
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import open_meteo as om
U=timezone.utc
b={"time":["0001-01-01T00:00","2026-08-21T00:00"],"shortwave_radiation":[1.0,100.0]}
s=om._parse_block(b,"shortwave_radiation"); print("series", s.times, s.values, s.resolution)
for a,e in [(datetime(2026,8,20,23,0,tzinfo=U),datetime(2026,8,21,0,0,tzinfo=U)),(datetime(2026,8,20,23,30,tzinfo=U),datetime(2026,8,21,0,0,tzinfo=U)),(datetime(2026,8,20,22,0,tzinfo=U),datetime(2026,8,21,1,0,tzinfo=U))]:
    try: print(a.time(), e.time(), s.mean_over(a,e))
    except Exception as x: print("raise", repr(x))
print("empty", om._EMPTY.mean_over(datetime(2026,8,20,23,0,tzinfo=U),datetime(2026,8,21,0,0,tzinfo=U)))
