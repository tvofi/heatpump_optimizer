"""R11-SEAM-two-zone-slab (#3713): the two-zone valve curve on a second install, and the direct slab beside it.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/r11_two_zone_slab.py

The finder's harness (``r10_sav_held_install.py``) reads the owner's replay
install, the one committed bundle with a two-zone valve-fed slab. This one
reads the golden fixtures' two-zone house (``profiles.house(two_zone=True)``,
valve ``manual`` at 21 C, 750 l buffer capped at 70 C: ``valve_storage``'s
configuration with its target set), at +5, -5 and -15 C outdoor, wind 3 m/s,
no rain or sun.

  fed     the slab behind the valve (``single_tank_valve``): ``held`` is
          ``_thermostat_held_state``'s room/upper/lower at 21 C, ``plant``
          where ``simulate_step`` at ``max_electrical_power`` for 960 steps
          from the held state leaves them, and the tank there.
  direct  the same house with ``topology_layout`` ``valve_upper_direct_slab``
          (the slab drinks raw tank water): the same columns, then the
          radiator circuit's curve and the upper floor it holds with the
          lower floor at 21 C, from ``_two_zone_rates``' steady upper-floor
          balance a*(F - Tu) - Uu*(Tu - o) + c*(21 - Tu) + r*G = 0 solved for
          Tu, with ``miss`` = Tu - 21 (design note item s2).

The control is the ``fed`` row at the merge base, where the curve leaves the
room short; ``direct`` reads alike at both ends (its curve is out of scope).
"""

import numpy as np

from heatpump_optimizer.optimizer import _thermostat_held_state
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries, _valve_draw_circuits)
from profiles import house


def params(layout):
    cfg = {**house(two_zone=True, dhw=False), "mixing_valve_mode": "manual",
           "buffer_tank_volume": 750.0, "buffer_max_temperature": 70.0,
           "mixing_valve_target": 21.0}
    if layout:
        cfg["topology_layout"] = layout
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    return p


def row(name, p, outdoor):
    m = ThermalModel(p)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=outdoor,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    w = WeatherSeries(outdoor_temps=np.full(96, outdoor), wind_speeds=np.full(96, 3.0),
                      precipitation=np.zeros(96), solar_radiation=np.zeros(96))
    h = _thermostat_held_state(m, st, w, 21.0)
    s = h
    for _ in range(960):
        s = m.simulate_step(s, p.max_electrical_power, outdoor, 3.0, 0.0, 0.0, 0.25)
    text = (f"{name} {outdoor:+.0f} C: held {h.room_temperature:.3f}/{h.upper_floor_temperature:.3f}/"
            f"{h.lower_floor_temperature:.3f} plant {s.room_temperature:.3f}/"
            f"{s.upper_floor_temperature:.3f}/{s.lower_floor_temperature:.3f} tank {s.buffer_tank_temperature:.1f}")
    if p.slab_fed_direct:
        (a, curve, _), _ = _valve_draw_circuits(m, st, outdoor, 3.0, 0.0)
        u_upper, _ = m._zone_loss(3.0, 0.0)
        c, r, g = p.inter_zone_transfer, p.upper_floor_area_ratio, p.internal_gains
        upper = (a * curve + u_upper * outdoor + c * 21.0 + r * g) / (a + u_upper + c)
        text += f" curve {curve:.3f} upper {upper:.3f} miss {upper - 21.0:+.3f}"
    return text


fed, direct = params(None), params("valve_upper_direct_slab")
assert fed.two_zone_enabled and not fed.slab_fed_direct and direct.slab_fed_direct
for outdoor in (5.0, -5.0, -15.0):
    print(row("fed", fed, outdoor))
    print(row("direct", direct, outdoor))
