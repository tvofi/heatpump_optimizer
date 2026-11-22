"""Shared body of the seven _buffer_charge_ceiling probes (lines 6069-6097).

Grid: buffer_max_temp x outdoor mean x tank UA, at the production cop_flow_reference_temp (35 C,
never assigned in production) and below it, plus constructed exact ties net(T) == 0.0 at hi, lo or the
first bisection midpoint: internal_gains is walked ulp by ulp until the production pieces of net()
(model.marginal_cop -> delivered_heat_kw, _house_ua_kw_per_c, TANK_ROOM_AMBIENT_TEMP) give exactly 0.0.
"""
import math
import numpy as np
from _mutant import build, mutated, outcome, tail, opt_mod
from custom_components.heatpump_optimizer import const
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters, delivered_heat_kw, TANK_ROOM_AMBIENT_TEMP, default_buffer_cooling_rate

HIS = (30.0, 35.0, 40.0, 55.0, 70.0, 90.0)
OUTS = (15.0, 0.0, -10.0, -15.0, -20.0, -30.0)
UAS = (None, 0.0, 2.0)  # buffer_cooling_rate (the tank UA derives from it)


def net(o, out_mean, temp):
    """net() of _buffer_charge_ceiling, from the same production pieces (input construction only)."""
    p = o.model.params
    u = opt_mod._house_ua_kw_per_c(p, p.house_heat_loss_scale)
    q = max(0.0, u * (o.config.target_temp - out_mean) - p.internal_gains)
    heat = delivered_heat_kw(p, o.model.marginal_cop(out_mean, "buffer", store_temp=temp, humidity=None),
                             p.max_electrical_power)
    return heat - q - p.buffer_tank_heat_loss_coefficient * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)


def tie(where, hi=70.0):
    """(optimizer, out_mean) with net(where) exactly 0.0, or None.

    net = H - q - X: near the root H and q are the same binade, so H - q is exact and sits on that
    binade's ulp grid; X (tank UA x (T - 20 C)) has finer bits, so the residual is never 0.0 unless X
    lands on the grid. buffer_cooling_rate (which sets the UA) is walked ulp by ulp from its volume
    default until X does; then the outdoor mean is bisected to the root and internal_gains walked ulp
    by ulp around 0.3 kW until q == H - X exactly."""
    lo = max(20.0, 35.0)
    temp = {"hi": hi, "lo": lo, "mid": 0.5 * (lo + hi)}[where]
    o = build(buffer_max_temp=hi)
    p = o.model.params
    base_gains = p.internal_gains
    rate = default_buffer_cooling_rate(p.buffer_store_volume)
    for _ in range(4000):
        rate = float(np.nextafter(rate, np.inf))
        p.buffer_cooling_rate = rate
        p.internal_gains = base_gains
        X = p.buffer_tank_heat_loss_coefficient * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)
        if math.fmod(X, 2.0 ** -50) != 0.0:
            continue
        a, b = 0.0, -40.0
        if not (net(o, a, temp) > 0 > net(o, b, temp)):
            return None
        for _ in range(200):
            m = 0.5 * (a + b)
            if m in (a, b):
                break
            a, b = (m, b) if net(o, m, temp) > 0 else (a, m)
        for x in (a, b):
            g = base_gains
            for _ in range(300):
                p.internal_gains = g
                r = net(o, x, temp)
                if r == 0.0:
                    return o, x
                g = float(np.nextafter(g, -np.inf if r > 0 else np.inf))
    return None


def cases():
    out = []
    for hi in HIS:
        for t in OUTS:
            for ua in UAS:
                kw = {"buffer_max_temp": hi}
                if ua is not None:
                    kw["buffer_cooling_rate"] = ua
                out.append((f"hi={hi} out={t} ua={ua}", build(**kw), t))
    for where in ("hi", "lo", "mid"):
        for hi in (55.0, 70.0, 90.0):
            r = tie(where, hi=hi)
            if r is not None:
                out.append((f"tie net({where})==0 hi={hi} out={r[1]!r}", r[0], r[1]))
    return out


def run(old, new, focus=None):
    moved, rows, focus_row = 0, [], None
    cs = cases()
    for label, o, t in cs:
        b = outcome(lambda: o._buffer_charge_ceiling(t))
        with mutated("_buffer_charge_ceiling", old, new):
            m = outcome(lambda: o._buffer_charge_ceiling(t))
        if b != m:
            moved += 1
            rows.append((label, b, m))
        if focus and label.startswith(focus) and focus_row is None:
            focus_row = (label, b, m)
    ties = sum(1 for l, _, _ in cs if l.startswith("tie"))
    print(f"RESULT inputs_tried={len(cs)} count (ties constructed: {ties})")
    print(f"RESULT inputs_moved={moved} count")
    for label, b, m in rows[:4]:
        print(f"RESULT moved {label}: baseline={b!r} mutant={m!r}")
    if rows:
        print(f"RESULT max_abs_delta_c={max(abs(b - m) for _, b, m in rows if not isinstance(b, str) and not isinstance(m, str)) if any(not isinstance(b, str) and not isinstance(m, str) for _, b, m in rows) else 'n/a'}")
    if focus_row:
        print(f"RESULT focus {focus_row[0]}: baseline={focus_row[1]!r} mutant={focus_row[2]!r}")
    # null control: mild weather at the default rating, where net(hi) > 0 and the function returns hi first
    o = build()
    b = o._buffer_charge_ceiling(15.0)
    with mutated("_buffer_charge_ceiling", old, new):
        m = o._buffer_charge_ceiling(15.0)
    print(f"RESULT null_delta={abs(b - m):.6g} C")
    # route: from_config does not clamp buffer_max_temperature (the flow's selector is 40..90)
    print(f"RESULT from_config_buffer_max_30={ThermalParameters.from_config({const.CONF_BUFFER_MAX_TEMP: 30}).buffer_max_temp}")
    tail()
    return moved
