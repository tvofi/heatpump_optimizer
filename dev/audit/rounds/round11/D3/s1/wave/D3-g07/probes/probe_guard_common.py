"""Shared driver of box D3-g07's five _guard_floor_hold probes: no measurement of its own."""
import dataclasses
import _probe_lib as L


def hold(fn, *, dhw_enabled=False, dhw_temp=55.0, dhw_min=45.0, two_zone=False,
         room=21.0, upper=21.0, lower=21.0, min_temp=17.0):
    """_guard_floor_hold's verdict (1 hold / 0 no hold) for one state on a live coordinator."""
    c = L.coord()
    c._thermal_params = dataclasses.replace(c._thermal_params, dhw_enabled=dhw_enabled,
                                            dhw_min_temp=dhw_min, two_zone_enabled=two_zone)
    c._current_state = dataclasses.replace(c._current_state, dhw_temperature=dhw_temp,
                                           room_temperature=room, upper_floor_temperature=upper,
                                           lower_floor_temperature=lower)
    c._opt_config.min_temp = min_temp
    return int(bool(fn(c)))
