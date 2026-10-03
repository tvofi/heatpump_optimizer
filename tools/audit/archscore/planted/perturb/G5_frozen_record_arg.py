"""G5 (GOOD, small scale): replace a shared in-place per-operation value with a
frozen record passed as an argument.

_async_learn_house_heat_loss overwrites self._last_house_sample /
self._last_house_sample_time near its top, and _async_learn_lower_floor_loss
reads them -- so the caller must run the lower-floor learner FIRST (the
comment at coordinator.py:5708 says "Order matters, and not obviously").
Now the caller snapshots ONE frozen ``_HouseSample`` and passes it to both
learners as an argument; the two attributes collapse into one record
attribute that only the house learner advances. The order dependence is gone.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write, replace_once

s = read(COORD)
s = replace_once(s, "\ndef _freq_fold_blocked(coord: Any) -> bool:\n", '''
@dataclass(frozen=True)
class _HouseSample:
    """The previous interval's state and when it was taken (fabric learners)."""

    state: ThermalState | None = None
    time: datetime | None = None


def _freq_fold_blocked(coord: Any) -> bool:
''')
s = replace_once(s, '''        self._last_house_sample: ThermalState | None = None
        self._last_house_sample_time: datetime | None = None
''', '''        self._last_house = _HouseSample()
''')
s = replace_once(s, '''    async def _async_learn_house_heat_loss(self) -> None:''',
                 '''    async def _async_learn_house_heat_loss(self, previous: _HouseSample) -> None:''')
s = replace_once(s, '''        observed = ctx._current_state.room_temperature
        previous_state = self._last_house_sample
        previous_time = self._last_house_sample_time
''', '''        observed = ctx._current_state.room_temperature
        previous_state, previous_time = previous.state, previous.time
''')
s = replace_once(s, '''        self._last_house_sample = replace(ctx._current_state)
        self._last_house_sample_time = now
''', '''        self._last_house = _HouseSample(replace(ctx._current_state), now)
''')
s = replace_once(s, '''    async def _async_learn_lower_floor_loss(self) -> None:''',
                 '''    async def _async_learn_lower_floor_loss(self, previous: _HouseSample) -> None:''')
s = replace_once(s, '''        params = ctx._thermal_params
        previous_state = self._last_house_sample
        previous_time = self._last_house_sample_time
''', '''        params = ctx._thermal_params
        previous_state, previous_time = previous.state, previous.time
''')
s = replace_once(s, '''        # Order matters, and not obviously. `_async_learn_house_heat_loss`
        # overwrites `_last_house_sample` with the *current* state near its top,
        # so anything reading that baseline has to run first or it silently
        # compares the current state against itself and learns nothing.
        await self._async_learn_lower_floor_loss()
        await self._async_learn_house_heat_loss()
''', '''        # Both learners replay the same frozen baseline, taken once here.
        previous = self._last_house
        await self._async_learn_lower_floor_loss(previous)
        await self._async_learn_house_heat_loss(previous)
''')
write(COORD, s)
