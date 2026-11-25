import os,sys
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"): os.environ.setdefault(_v,"1")
sys.path.insert(0,'tests'); import harness
from harness import FakeHass, FakeEntry
import asyncio, inspect, textwrap, math
from datetime import datetime, timedelta, timezone
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as co
from heatpump_optimizer.const import buffer_cooling_rate_bounds
print(co.DHW_COOLING_REFERENCE_DELTA, co.HeatPumpOptimizerCoordinator._async_learn_buffer_cooling)
src=inspect.getsource(co.HeatPumpOptimizerCoordinator._async_learn_buffer_cooling)
print(src.splitlines()[0:2], 'super(' in src)
c=co.HeatPumpOptimizerCoordinator(FakeHass(),FakeEntry(data={"tibber_token":"x","weather_entity":"weather.home"}))
print('rate0',c._buffer_cooling_rate,'bounds',c._buffer_cooling_bounds(), c._thermal_params.buffer_tank_volume)
for v in (None,0,1,5,35,100,750,5000,1e6):
    try: print(v, buffer_cooling_rate_bounds(v))
    except Exception as e: print(v,'ERR',e)
