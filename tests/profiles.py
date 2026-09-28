"""Realistic Swedish weather and Nord Pool SE3 price profiles for the test suite."""
import numpy as np
from datetime import datetime, timedelta

DT = 0.25
N = 96

def _h(start):
    return np.array([(start + timedelta(hours=i*DT)).hour +
                     (start + timedelta(hours=i*DT)).minute/60.0 for i in range(N)])

def prices(profile, start):
    """Nord Pool SE3 style day-ahead curves, SEK/kWh incl. grid+tax."""
    h = _h(start)
    if profile == "winter_typical":
        # Jan 2025 SE3: cheap night, sharp 07-09 and 17-20 peaks
        p = np.full(N, 1.05)
        p[(h >= 0) & (h < 5)] = 0.62
        p[(h >= 5) & (h < 7)] = 0.95
        p[(h >= 7) & (h < 10)] = 2.35
        p[(h >= 10) & (h < 16)] = 1.15
        p[(h >= 16) & (h < 20)] = 2.85
        p[(h >= 20) & (h < 23)] = 1.30
        p[h >= 23] = 0.78
    elif profile == "winter_extreme":
        # Cold snap with low wind: severe evening scarcity pricing
        p = np.full(N, 1.80)
        p[(h >= 0) & (h < 5)] = 0.90
        p[(h >= 7) & (h < 10)] = 4.80
        p[(h >= 16) & (h < 20)] = 7.40
        p[h >= 22] = 1.20
    elif profile == "summer_typical":
        # Jul SE3: low and flat, midday dip from solar+hydro
        p = np.full(N, 0.45)
        p[(h >= 0) & (h < 6)] = 0.28
        p[(h >= 6) & (h < 9)] = 0.62
        p[(h >= 10) & (h < 15)] = 0.18
        p[(h >= 17) & (h < 21)] = 0.72
    elif profile == "summer_negative":
        # Windy/sunny summer day: negative midday prices happen in SE3
        p = np.full(N, 0.30)
        p[(h >= 11) & (h < 15)] = -0.12
        p[(h >= 18) & (h < 21)] = 0.55
    elif profile == "shoulder":
        p = np.full(N, 0.80)
        p[(h >= 1) & (h < 5)] = 0.40
        p[(h >= 7) & (h < 9)] = 1.60
        p[(h >= 17) & (h < 20)] = 1.90
    elif profile == "winter_narrow":
        # The case the existing profiles miss entirely.
        #
        # Every other curve here has a cheap:dear ratio of 0.12-0.25, which is
        # far inside the break-even a thermal store needs (a 20 K lift at 2 %/K
        # needs the cheap hour at or below 0.60 of the dear one). Measuring
        # storage only against those profiles concludes "storage always pays"
        # without ever touching the marginal case that actually decides it.
        # Ratio here is 0.70.
        p = np.full(N, 1.55)
        p[(h >= 0) & (h < 5)] = 1.40
        p[(h >= 7) & (h < 10)] = 1.95
        p[(h >= 16) & (h < 20)] = 2.00
        p[h >= 22] = 1.45
    elif profile == "winter_moderate":
        # Between narrow and typical: ratio 0.52, i.e. either side of break-even
        # depending on how hard the tank is charged. This is where a storage
        # feature has to make a genuinely correct call rather than a lucky one.
        p = np.full(N, 1.30)
        p[(h >= 0) & (h < 5)] = 0.95
        p[(h >= 7) & (h < 10)] = 1.75
        p[(h >= 16) & (h < 20)] = 1.85
        p[h >= 22] = 1.05
    elif profile == "flat":
        p = np.full(N, 1.20)
    else:
        raise ValueError(profile)
    return p

def weather(profile, start):
    """Returns (outdoor_temp, wind, precipitation, solar W/m2)."""
    h = _h(start)
    if profile == "winter_cold":       # Stockholm mid-Jan cold spell
        t = -12.0 + 4.0*np.sin((h-14)/24*2*np.pi)
        wind = np.full(N, 2.0); rain = np.zeros(N)
        solar = np.clip(45*np.sin((h-8.5)/7.0*np.pi), 0, None)
    elif profile == "winter_mild":     # Jan thaw, wet and windy
        t = 1.5 + 2.0*np.sin((h-14)/24*2*np.pi)
        wind = np.full(N, 9.0); rain = np.full(N, 1.0)
        solar = np.clip(30*np.sin((h-9)/6.0*np.pi), 0, None)
    elif profile == "summer_warm":     # Jul, no space heating needed
        t = 19.0 + 6.0*np.sin((h-15)/24*2*np.pi)
        wind = np.full(N, 3.0); rain = np.zeros(N)
        solar = np.clip(780*np.sin((h-4.0)/16.0*np.pi), 0, None)
    elif profile == "summer_cool":     # Rainy Swedish July
        t = 13.0 + 3.0*np.sin((h-15)/24*2*np.pi)
        wind = np.full(N, 6.0); rain = np.full(N, 2.0)
        solar = np.clip(220*np.sin((h-5)/15.0*np.pi), 0, None)
    elif profile == "shoulder":        # April
        t = 6.0 + 5.0*np.sin((h-15)/24*2*np.pi)
        wind = np.full(N, 4.0); rain = np.zeros(N)
        solar = np.clip(420*np.sin((h-6)/13.0*np.pi), 0, None)
    else:
        raise ValueError(profile)
    return t, wind, rain, solar

def house(two_zone=False, dhw=True, **over):
    cfg = {
        "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
        "heat_pump_max_power": 6.0, "heat_pump_min_power": 1.0,
        "dhw_tank_volume": 300.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
        "dhw_daily_consumption": 200.0,
        "dhw_windows": "06:00-08:30, 17:00-22:00",
        "buffer_tank_volume": 200.0, "window_area": 18.0,
    }
    if two_zone:
        cfg.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 4.5,
                    "upper_floor_heat_loss": 0.10, "lower_floor_heat_loss": 0.09,
                    "inter_zone_heat_transfer": 0.6, "radiator_power_fraction": 0.4})
    cfg.update(over)
    return cfg
