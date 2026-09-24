"""D2-s1 harness: thermal-model identities and COP/derate bounds (method steps 1-2) -- the non-findings.

Each section hooks the production ThermalModel / DefrostDerate and prints one RESULT:
  conservation_*   max |sum C_i dT_i - dt*(sources - losses - booked refusals)| per step (kWh),
                   random sweep over topology x state x weather x power (_simulate_step_two_zone,
                   _simulate_step_single, simulate_dhw_step)
  parity_mismatch  count of (row, series) where simulate_trajectory_batch != simulate_trajectory
                   (np.array_equal, bitwise) over 8 input kinds x 75 random cases x 5 rows
  dt_order_*       ratio of end-state error at dt=0.5 h vs dt=0.25 h against a dt=1/32 h reference
                   (first-order Euler predicts ~2); 'valve' cases substep so dt<=0.25 is exact
  monotone_violations  count of later-store temperatures that FALL when one earlier step gets +1e-3 kW
  cap_rate_not_state   K a tank read 5 K above its cap moves in one idle step (must be < 5: cools, not snapped)
  cop_monotone_viol    count of grid steps where compute_cop rises with flow or falls with outdoor
  derate_*         DefrostDerate.factor range and max jump over a 0.01 K sweep
  dhw_floor_hits   configs (of 288, dt=0.25) where simulate_dhw_step books _step_dhw_floor_injected>0
Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_identities.py
Perturbation (for the conservation arm): --drop-refused omits the booked buffer/wood refusals from
the balance; conservation_two_zone must then rise far above 1e-9.
Expected: conservation_* < 1e-12, parity_mismatch=0, dt_order ~2, monotone_violations=0,
cap_rate_not_state < 5, cop_monotone_viol=0, derate in [0.55,1] with jump < 1e-3.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (shared).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, ".")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from custom_components.heatpump_optimizer.defrost import DefrostDerate, DERATE_MIN  # noqa: E402

DROP = "--drop-refused" in sys.argv


def conservation_two_zone(rng, n=3000):
    worst = 0.0
    for _ in range(n):
        mode = rng.choice(["none", "manual"]); topo = rng.choice(["", "two_tank", "direct"])
        kw = dict(two_zone_enabled=True, mixing_valve_mode=str(mode), cop_flow_carnot=bool(rng.integers(2)),
                  buffer_tank_volume=float(rng.choice([35, 100, 300, 800])),
                  max_electrical_power=float(rng.uniform(2, 12)), buffer_max_temp=float(rng.choice([50, 70])))
        if topo == "two_tank":
            kw.update(wood_tank_configured=True, wood_tank_volume=float(rng.choice([300, 1000])))
        if topo == "direct":
            kw.update(topology_layout_override="valve_upper_direct_slab")
        m = ThermalModel(ThermalParameters(**kw)); p = m.params
        st = ThermalState(room_temperature=21, slab_temperature=float(rng.uniform(18, 35)),
                          upper_floor_temperature=float(rng.uniform(15, 25)),
                          lower_floor_temperature=float(rng.uniform(15, 25)),
                          buffer_tank_temperature=float(rng.uniform(15, 80)),
                          wood_tank_temperature=(float(rng.uniform(15, 94)) if topo == "two_tank" else None))
        P = float(rng.uniform(0, kw["max_electrical_power"])); out = float(rng.uniform(-25, 15))
        wind = float(rng.uniform(0, 10)); rain = float(rng.uniform(0, 3)); sol = float(rng.uniform(0, 800))
        ext = float(rng.choice([0, 0, 5, 15])); dt = 0.25
        thr = tm.mixing_valve.is_throttling(p.mixing_valve_mode)
        two_tank = thr and p.two_tank_modelled and st.wood_tank_temperature is not None
        cop = m.compute_cop(out, flow_temp=st.buffer_tank_temperature if thr else None)
        new = m._simulate_step_two_zone(st, P, out, wind, rain, sol, dt, ext)
        cb = p.buffer_tank_thermal_mass if p.buffer_tank_thermal_mass >= 1e-6 else 0.04
        dH = (p.upper_floor_thermal_mass * (new.upper_floor_temperature - st.upper_floor_temperature)
              + p.lower_floor_thermal_mass * (new.lower_floor_temperature - st.lower_floor_temperature)
              + p.slab_thermal_mass * (new.slab_temperature - st.slab_temperature)
              + cb * (new.buffer_tank_temperature - st.buffer_tank_temperature))
        uu = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss, wind, rain)
        ul = m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned, wind * .5, rain * .5)
        src = (cop * P + max(0., ext) - uu * (st.upper_floor_temperature - out)
               - ul * (st.lower_floor_temperature - out)
               - p.buffer_tank_heat_loss_coefficient * (st.buffer_tank_temperature - 20)
               + m.compute_solar_gain(sol) + p.internal_gains
               - (0.0 if DROP else m._step_buffer_refused))
        if two_tank:
            dH += p.wood_tank_thermal_mass * (new.wood_tank_temperature - st.wood_tank_temperature)
            src += (-p.wood_tank_heat_loss_coefficient * (st.wood_tank_temperature - 20)
                    - (0.0 if DROP else m._step_wood_refused))
        worst = max(worst, abs(dH - src * dt))
    return worst


def conservation_single(rng, n=1000):
    worst = 0.0
    for _ in range(n):
        m = ThermalModel(ThermalParameters(max_electrical_power=float(rng.uniform(2, 12)))); p = m.params
        st = ThermalState(room_temperature=float(rng.uniform(15, 25)), slab_temperature=float(rng.uniform(18, 35)))
        P = float(rng.uniform(0, 10)); out = float(rng.uniform(-25, 15)); wind = float(rng.uniform(0, 10))
        rain = float(rng.uniform(0, 3)); sol = float(rng.uniform(0, 800)); ext = float(rng.choice([0, 6])); dt = 0.25
        cop = m.compute_cop(out)
        new = m._simulate_step_single(st, P, out, wind, rain, sol, dt, ext)
        dH = (p.room_thermal_mass * (new.room_temperature - st.room_temperature)
              + p.slab_thermal_mass * (new.slab_temperature - st.slab_temperature))
        u = m.effective_heat_loss_coefficient(p.heat_loss_coefficient, wind, rain)
        src = cop * P + ext - u * (st.room_temperature - out) + p.internal_gains + m.compute_solar_gain(sol)
        worst = max(worst, abs(dH - src * dt))
    return worst


def conservation_dhw(rng, n=2000):
    worst = 0.0
    for _ in range(n):
        m = ThermalModel(ThermalParameters(dhw_enabled=True, dhw_tank_volume=float(rng.choice([150, 200, 300])),
                                           dhw_setpoint=float(rng.uniform(45, 60)),
                                           dhw_legionella_enabled=bool(rng.integers(2)),
                                           dhw_inlet_temp=float(rng.uniform(5, 15))))
        p = m.params; T = float(rng.uniform(15, 75)); q = float(rng.uniform(0, 12)); draw = float(rng.uniform(0, 5))
        dt = 0.25
        new = m.simulate_dhw_step(T, q, 7.0, dt_hours=dt, draw_power=draw)
        C = p.dhw_tank_thermal_mass
        loss = p.dhw_tank_heat_loss_coefficient * (T - tm.DHW_AMBIENT_TEMP)
        resid = C * (new - T) - dt * (q - m._step_dhw_draw_kw - loss - m._step_dhw_refused
                                      + m._step_dhw_floor_injected)
        worst = max(worst, abs(resid))
    return worst


def derate(rng):
    d = DefrostDerate()
    for t in (-10, 1, 3, 6):
        for h in (50, 90):
            for _ in range(15):
                d.observe(t, h, float(rng.uniform(0.6, 1.0)))
    return d


def parity(rng, n=600):
    bad = 0
    for trial in range(n):
        kind = trial % 8; kw = {}
        if kind >= 1:
            kw["two_zone_enabled"] = True
        if kind in (2, 3, 4, 5, 6):
            kw.update(mixing_valve_mode="manual", buffer_tank_volume=float(rng.choice([35, 100, 300])))
        if kind == 3:
            kw["cop_flow_carnot"] = True
        if kind == 4:
            kw.update(wood_tank_configured=True, wood_tank_volume=800., cop_flow_carnot=bool(rng.integers(2)))
        if kind == 5:
            kw.update(topology_layout_override="valve_upper_direct_slab")
        if kind == 6:
            kw.update(cop_flow_carnot=True, buffer_max_temp=50.)
        if kind == 7:
            kw.update(flow_curve_cop=True, flow_curve_bias=float(rng.uniform(-3, 3)))
        if rng.integers(2):
            kw["defrost_derate"] = derate(rng); kw["ambient_humidity"] = 80.0
        if rng.integers(2):
            kw["internal_gains_profile"] = [float(x) for x in rng.uniform(0, 0.8, 24)]
        kw["max_electrical_power"] = float(rng.uniform(2, 10))
        m = ThermalModel(ThermalParameters(**kw)); ns = 12
        st = ThermalState(room_temperature=float(rng.uniform(18, 22)), slab_temperature=float(rng.uniform(20, 30)),
                          upper_floor_temperature=float(rng.uniform(18, 22)),
                          lower_floor_temperature=float(rng.uniform(18, 22)),
                          buffer_tank_temperature=float(rng.uniform(25, 72)),
                          wood_tank_temperature=(float(rng.uniform(20, 94)) if kind == 4 else None))
        B = 5
        Pm = rng.uniform(0, kw["max_electrical_power"], (B, ns))
        out = rng.uniform(-20, 12, ns); wind = rng.uniform(0, 12, ns); rain = rng.uniform(0, 3, ns)
        sol = rng.uniform(0, 700, ns); ext = rng.choice([0., 0., 8.], ns)
        hum = rng.uniform(40, 100, ns); hum[rng.integers(ns)] = np.nan
        vt = rng.uniform(19, 24, ns) if rng.integers(2) else None
        sh = float(rng.uniform(0, 24)); dt = float(rng.choice([0.25, 1.0]))
        b = m.simulate_trajectory_batch(st, Pm, out, wind, rain, sol, dt, ext, vt, hum, sh)
        for r in range(B):
            s = m.simulate_trajectory(st, Pm[r], out, wind, rain, sol, dt, ext, vt, hum, sh)
            for j, nm in enumerate(["room", "slab", "upper", "lower", "buffer", "refused", "wood"]):
                if s[j] is None:
                    continue
                if not np.array_equal(s[j], b[nm][r]):
                    bad += 1
    return bad


def dt_order():
    cfgs = {"single": dict(), "tz_none": dict(two_zone_enabled=True),
            "tz_valve300": dict(two_zone_enabled=True, mixing_valve_mode="manual", cop_flow_carnot=True,
                                buffer_tank_volume=300.),
            "tz_wood": dict(two_zone_enabled=True, mixing_valve_mode="manual", buffer_tank_volume=300.,
                            wood_tank_configured=True, wood_tank_volume=1000.)}
    ratios = {}
    for name, kw in cfgs.items():
        m = ThermalModel(ThermalParameters(**kw)); res = {}
        for dt in (0.5, 0.25, 0.125, 1 / 32):
            n = int(round(6.0 / dt))
            st = ThermalState(room_temperature=20.5, slab_temperature=24, upper_floor_temperature=20.5,
                              lower_floor_temperature=20.5, buffer_tank_temperature=45.,
                              wood_tank_temperature=(60. if "wood" in name else None))
            hrs = np.arange(n) * dt
            P = np.where((hrs % 4) < 2, 3.0, 0.5); out = -5 + 2 * np.floor(hrs) % 3
            ext = np.where(hrs < 2, 6.0, 0.0)
            r = m.simulate_trajectory(st, P, out, dt_hours=dt, external_heat_kw=ext)
            res[dt] = np.array([r[0][-1], r[1][-1], r[4][-1]])
        e = [np.abs(res[d] - res[1 / 32]).max() for d in (0.25, 0.125)]
        ratios[name] = e[0] / e[1] if e[1] > 0 else float("nan")
    return ratios


def monotone():
    viol = 0
    for vol in (35, 100, 300):
        for pmax in (3, 8, 12):
            m = ThermalModel(ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual",
                                               cop_flow_carnot=True, buffer_tank_volume=float(vol),
                                               max_electrical_power=float(pmax)))
            for T0 in (30.0, 60.0):
                st = ThermalState(room_temperature=21, slab_temperature=25, upper_floor_temperature=21,
                                  lower_floor_temperature=21, buffer_tank_temperature=T0)
                n = 8
                for P in np.linspace(0.5, pmax, 4):
                    sched = np.full(n, P); out = np.full(n, -5.0)
                    base = m.simulate_trajectory(st, sched, out)
                    for k in range(n - 1):
                        s2 = sched.copy(); s2[k] += 1e-3
                        pert = m.simulate_trajectory(st, s2, out)
                        for idx in range(5):
                            viol += int(((pert[idx] - base[idx])[k + 1:] < -1e-12).sum())
    return viol


def cap_rate():
    m = ThermalModel(ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual", buffer_tank_volume=300.,
                                       buffer_max_temp=60.))
    st = ThermalState(room_temperature=21, slab_temperature=25, upper_floor_temperature=21,
                      lower_floor_temperature=21, buffer_tank_temperature=65.0)
    new = m.simulate_step(st, 0.0, 0.0)
    md = ThermalModel(ThermalParameters(dhw_enabled=True))
    tdhw = md.simulate_dhw_step(md.params.dhw_hard_max_temp + 5.0, 0.0, 3.0, draw_power=0.0)
    return 65.0 - new.buffer_tank_temperature, md.params.dhw_hard_max_temp + 5.0 - tdhw


def cop_monotone():
    outs = np.linspace(-30, 25, 551); flows = np.linspace(20, 75, 56); viol = 0
    for kw in (dict(), dict(cop_flow_carnot=True), dict(flow_curve_cop=True),
               dict(cop_flow_carnot=True, cop_nominal=5.0), dict(cop_flow_carnot=True, cop_nominal=2.2)):
        m = ThermalModel(ThermalParameters(**kw))
        G = np.array([[m.compute_cop(o, flow_temp=f) for o in outs] for f in flows])
        viol += int((np.diff(G, axis=1) < -1e-12).sum()) + int((np.diff(G, axis=0) > 1e-12).sum())
        D = np.array([[m.compute_cop_dhw(o, t) for o in outs] for t in flows])
        viol += int((np.diff(D, axis=1) < -1e-12).sum()) + int((np.diff(D, axis=0) > 1e-12).sum())
    return viol


def derate_checks(rng):
    lo, hi, jump = 1.0, 0.0, 0.0
    for _ in range(5):
        d = derate(rng)
        for h in (30.0, 60.0, 69.99, 70.0, 95.0):
            ts = np.arange(-12.0, 12.0, 0.01)
            f = np.array([d.factor(t, h) for t in ts])
            lo = min(lo, f.min()); hi = max(hi, f.max()); jump = max(jump, np.abs(np.diff(f)).max())
        hs = np.arange(0.0, 100.0, 0.01)
        f = np.array([d.factor(2.0, h) for h in hs]); jump = max(jump, np.abs(np.diff(f)).max())
    return lo, hi, jump


def dhw_floor_hits():
    hits = 0; tot = 0; worst = 0.0
    for vol in (60, 80, 100, 150, 200, 300):
        for cons in (100, 200, 300, 400):
            for win in ([(7.0, 8.0)], [(7.0, 7.5)], [(18.0, 20.0)], []):
                for inlet in (5.0, 10.0, 15.0):
                    m = ThermalModel(ThermalParameters(dhw_enabled=True, dhw_tank_volume=float(vol),
                                                       dhw_daily_consumption=float(cons),
                                                       dhw_schedule_enabled=bool(win), dhw_windows=win,
                                                       dhw_inlet_temp=inlet))
                    hours = (np.arange(96) * 0.25) % 24; dr = m.dhw_draw_rates(hours); T = 45.0; inj = 0.0
                    for i in range(96):
                        T = m.simulate_dhw_step(T, 0.0, hours[i], dt_hours=0.25, draw_power=float(dr[i]))
                        inj = max(inj, m._step_dhw_floor_injected)
                    tot += 1; hits += int(inj > 0); worst = max(worst, inj) if vol >= 150 else worst
    return hits, tot, worst


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    rng = np.random.default_rng(20260923)
    print(f"RESULT conservation_two_zone={conservation_two_zone(rng):.3e} kWh")
    print(f"RESULT conservation_single={conservation_single(rng):.3e} kWh")
    print(f"RESULT conservation_dhw={conservation_dhw(rng):.3e} kWh")
    if DROP:
        return
    print(f"RESULT parity_mismatch={parity(rng)} count")
    for k, v in dt_order().items():
        print(f"RESULT dt_order_{k}={v:.3f} ratio")
    print(f"RESULT monotone_violations={monotone()} count")
    b, d = cap_rate()
    print(f"RESULT cap_rate_not_state_buffer={b:.4f} K")
    print(f"RESULT cap_rate_not_state_dhw={d:.4f} K")
    print(f"RESULT cop_monotone_viol={cop_monotone()} count")
    lo, hi, j = derate_checks(rng)
    print(f"RESULT derate_min={lo:.4f} (DERATE_MIN={DERATE_MIN})")
    print(f"RESULT derate_max={hi:.4f}")
    print(f"RESULT derate_max_jump_per_0p01={j:.2e}")
    h, t, w = dhw_floor_hits()
    print(f"RESULT dhw_floor_hits={h}/{t} configs")
    print(f"RESULT dhw_floor_injected_max_ge150L={w:.4f} kW")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = 'n/a'
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
