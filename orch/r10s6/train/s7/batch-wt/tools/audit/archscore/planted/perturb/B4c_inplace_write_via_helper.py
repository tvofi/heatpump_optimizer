"""B4c (BAD): the same new per-operation attribute as B4b, but written through
a module-level helper that takes the coordinator -- the existing
``_note_solve_failure(coord, err)`` shape (coordinator.py:648). The attribute
lives on the coordinator exactly as in B4b.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write, replace_once

s = read(COORD)
s = replace_once(s, '''def _note_solve_failure(coord: "HeatPumpOptimizerCoordinator", err: Exception) -> None:''',
'''def _note_solve_prices(coord: "HeatPumpOptimizerCoordinator", prices: Any) -> None:
    """Remember this solve's price vector on the coordinator."""
    coord._solve_prices = list(prices)


def _note_solve_failure(coord: "HeatPumpOptimizerCoordinator", err: Exception) -> None:''')
s = replace_once(s, '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
''', '''            horizon = self._forecast_arrays(now)
            prices = horizon.prices
            _note_solve_prices(self, prices)
''')
write(COORD, s)
