"""G2 (GOOD): dedupe the near-identical replay block of the two fabric learners.

_async_learn_house_heat_loss and _async_learn_lower_floor_loss each carry the
same try/simulate_step/except replay (the 15-line duplication_blocks pair at
coordinator.py:4356/4555). One helper ``_replay_interval`` now owns it; both
learners call it. Seam: learning (both callers' seam).
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, replace_once, insert_after_method, seam_set

src = read(COORD)
house_old = '''        try:
            wind_speed, precipitation = self._current_weather()
            predicted_state = self._thermal_model.simulate_step(
                previous_state,
                previous_power,
                outdoor,
                wind_speed=wind_speed,
                precipitation=precipitation,
                solar_radiation=previous_state.solar_radiation,
                dt_hours=dt_h,
                # #53: the replay must predict with the learned per-hour
                # profile, or its residuals never re-centre and the gains
                # learner becomes an open-loop integrator converging to
                # α/ridge times the true correction. None-profile (flag
                # off, nothing learned) makes this byte-inert.
                hour_of_day=previous_time.hour + previous_time.minute / 60.0,
            )
        except Exception as err:
            _LOGGER.debug("House heat loss learning simulation failed: %s", err)
            return
'''
house_new = '''        predicted_state = self._replay_interval(
            previous_state, previous_power, outdoor, previous_time, dt_h, "House heat loss")
        if predicted_state is None:
            return
'''
lower_old = '''        try:
            wind_speed, precipitation = self._current_weather()
            predicted_state = self._thermal_model.simulate_step(
                previous_state,
                previous_power,
                outdoor,
                wind_speed=wind_speed,
                precipitation=precipitation,
                solar_radiation=previous_state.solar_radiation,
                dt_hours=dt_h,
                # Same physics as the solve when #53 is on; inert when off.
                hour_of_day=previous_time.hour + previous_time.minute / 60.0,
            )
        except Exception as err:
            _LOGGER.debug("Lower floor loss learning simulation failed: %s", err)
            return
'''
lower_new = '''        predicted_state = self._replay_interval(
            previous_state, previous_power, outdoor, previous_time, dt_h, "Lower floor loss")
        if predicted_state is None:
            return
'''
src = replace_once(src, house_old, house_new)
src = replace_once(src, lower_old, lower_new)
helper = '''    def _replay_interval(
        self, previous_state: ThermalState, previous_power: float, outdoor: float,
        previous_time: datetime, dt_h: float, label: str,
    ) -> ThermalState | None:
        """Replay the elapsed interval through the solver's own model.

        #53: the replay predicts with the learned per-hour profile, or its
        residuals never re-centre and the gains learner becomes an open-loop
        integrator. None-profile (flag off, nothing learned) is byte-inert.
        None = the simulation failed; the caller skips the sample.
        """
        try:
            wind_speed, precipitation = self._current_weather()
            return self._thermal_model.simulate_step(
                previous_state,
                previous_power,
                outdoor,
                wind_speed=wind_speed,
                precipitation=precipitation,
                solar_radiation=previous_state.solar_radiation,
                dt_hours=dt_h,
                hour_of_day=previous_time.hour + previous_time.minute / 60.0,
            )
        except Exception as err:
            _LOGGER.debug("%s learning simulation failed: %s", label, err)
            return None
'''
src = insert_after_method(src, COORD_CLASS, "_async_learn_lower_floor_loss", helper)
write(COORD, src)
seam_set("_replay_interval", "learning")
