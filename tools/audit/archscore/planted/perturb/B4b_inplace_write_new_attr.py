"""B4b (BAD): the same per-operation value stashed as a NEW coordinator
attribute (declared in _init_runtime_state, overwritten each solve inside the
async method before its await) -- the shape the attr census is built to see.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write, replace_once

s = read(COORD)
s = replace_once(s, '''        self._solve_failures: int = 0
''', '''        self._solve_failures: int = 0
        self._solve_prices: list[float] = []
''')
s = replace_once(s, '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
''', '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
            self._solve_prices = list(prices)
''')
write(COORD, s)
