"""B4a (BAD): write a per-operation value into a long-lived shared object inside
an async method, ahead of its awaits: async_run_optimization stamps this
solve's price vector and start time into self._current_action (the dict the
sensors, the arbiter and boost all read) before the executor await at
coordinator.py:5189, so any reader that runs during the await sees a
half-updated action.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write, replace_once

s = read(COORD)
s = replace_once(s, '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
''', '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
            self._current_action["solve_started_at"] = now.isoformat()
            self._current_action["solve_prices"] = list(prices)
''')
write(COORD, s)
