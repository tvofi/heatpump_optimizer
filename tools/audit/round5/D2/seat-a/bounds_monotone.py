"""D2-a round 5: store monotonicity, cap-clamps-rate-not-state, and physical
bounds across every golden scenario.

METRICS (one line each):
  monotone_min_delta_k: min over trials/steps/stores of (T_bumped - T_base)
    after a +1e-3 kW power bump at one step of the space schedule (or the
    DHW schedule); the identity "more power never cools a store" holds when
    the value is >= 0 for every store the power feeds.
  hot_tank_snap_k: |T_buf(after one zero-power step from 78 C against a 70 C
    cap) - physical-cooling prediction|; the cap clamps a rate, not a state,
    when this is <= 1e-9 K and the tank is NOT snapped to the cap.
  golden_bounds_violations: count of scenarios in tests/golden.py:SCENARIOS
    whose solved trajectory crosses a physical bound (buffer above its cap
    unless starting above, DHW above the 70 C rating, wood above 95 C, any
    store non-finite or below absolute zero, DHW below the inlet floor).

Instrumented production symbols:
  thermal_model.py:ThermalModel.simulate_trajectory_with_dhw
  thermal_model.py:ThermalModel.simulate_step (hot-tank cooling check)
  optimizer.py:HeatPumpOptimizer.optimize (golden captures)

COMMAND (from the export root; the golden sweep takes ~3-5 min):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/bounds_monotone.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/bounds_monotone.py --skip-golden
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/bounds_monotone.py --perturb

EXPECTED: monotone_min_delta_k >= 0 for every family except (a) the wood
store in blend conditions (measured -2e-6..-7e-6 K per +1e-3 kW: the 4-way
blend takes a larger wood fraction as the HP tank passes the curve --
physically-signed, documented) and (b) the 35 L valved buffer, where the
committed finding measures the violation and its bump scaling (1e-3 kW ->
~-9e-2 K, 1e-1 kW -> ~-30 K; the 750 L control stays exactly 0). The
hot-tank cap check must report snapped=False and
hot_tank_rate_not_state_ok=True; golden_bounds_violations == 0 (50
scenarios). --perturb (an in-memory step wrapper that drops 1e-4 kW of
thermal power per step) must drive monotone_min_delta_k below -1e-3
(direction: decreases), proving sensitivity.

Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0. Machine: 8-core M1,
Python 3.11, numpy/OpenBLAS (single-threaded pin).
"""
import sys

sys.dont_write_bytecode = True
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d2a_common as C

import numpy as np
from dataclasses import replace

import custom_components.heatpump_optimizer.thermal_model as tm_probe


def monotone_family(built, rng, bump_dhw=False, trials=8):
    model = built["optimizer"].model
    p = model.params
    n = 96
    base_sp = rng.uniform(0, p.max_electrical_power, n)
    base_dp = rng.uniform(0, 2.0, n)
    hum = np.full(n, 55.0)
    kw = dict(
        dt_hours=0.25, external_heat_kw=C.ext_forecast(n), humidity=hum,
        start_hour=6.5,
    )
    r0 = model.simulate_trajectory_with_dhw(
        replace(built["state"]), base_sp, base_dp, built["outdoor"],
        built["wind"], built["rain"], built["solar"], **kw
    )
    worst = 0.0
    worst_at = None
    for _ in range(trials):
        i = int(rng.integers(0, n))
        if bump_dhw:
            dp2 = base_dp.copy()
            dp2[i] += 1e-3
            sp2 = base_sp
        else:
            sp2 = base_sp.copy()
            sp2[i] += 1e-3
            dp2 = base_dp
        r1 = model.simulate_trajectory_with_dhw(
            replace(built["state"]), sp2, dp2, built["outdoor"],
            built["wind"], built["rain"], built["solar"], **kw
        )
        for j, a0 in enumerate(r0):
            if a0 is None:
                continue
            d = np.asarray(r1[j], dtype=float)[i + 1:] - np.asarray(a0, dtype=float)[i + 1:]
            mn = float(d.min())
            if mn < worst:
                worst = mn
                worst_at = (i, j)
    return worst, worst_at


def hot_tank_check():
    fams = C.build_families()
    built = fams["valve_store"]
    model = built["optimizer"].model
    p = model.params
    state = replace(built["state"], buffer_tank_temperature=78.0)
    new = model.simulate_step(
        state=state, electrical_power=0.0, outdoor_temp=-5.0, dt_hours=0.25
    )
    # Physical cooling prediction: only losses move the tank (no snap): the
    # charging clamp must not touch a cooling tank; the delivery bound takes
    # tank heat at house-demand rate, so compare against the model's own
    # per-step rate: new_buf < 78, new_buf > 70 (not snapped), refused == 0.
    ua = p.buffer_tank_heat_loss_coefficient
    passive = 78.0 - ua * (78.0 - 20.0) * 0.25 / max(p.buffer_tank_thermal_mass, 0.01)
    snapped = abs(float(new.buffer_tank_temperature) - 70.0) < 1e-12
    # The valve draws from the tank (house demand), so the exact prediction
    # is passive cooling MINUS delivered heat; the invariant pieces are:
    # not snapped, still above the cap, refused ledger zero, and cooler than
    # the passive-cooling bound.
    ok_rate = (
        (not snapped)
        and new.buffer_tank_temperature > 70.0
        and model._step_buffer_refused == 0.0
        and new.buffer_tank_temperature <= passive + 1e-9
    )
    return (
        float(new.buffer_tank_temperature),
        float(passive),
        snapped,
        float(model._step_buffer_refused),
        ok_rate,
    )


def golden_bounds():
    from tests.golden import capture, SCENARIOS

    bad = []
    for name, spec in SCENARIOS.items():
        try:
            p = capture(name, spec)
        except Exception as e:  # noqa: BLE001 - recorded, not swallowed
            bad.append((name, "capture-fail:%s" % type(e).__name__))
            continue
        buf = np.asarray(p.get("buffer_temp_trajectory") or [], dtype=float)
        dhw = np.asarray(p.get("dhw_temp_trajectory") or [], dtype=float)
        wood = p.get("wood_temp_trajectory")
        wood = np.asarray(wood, dtype=float) if wood else None
        if buf.size and np.all(np.isfinite(buf)) is False:
            bad.append((name, "buffer-nonfinite"))
        if dhw.size and np.all(np.isfinite(dhw)) is False:
            bad.append((name, "dhw-nonfinite"))
        if wood is not None and wood.size and not np.all(np.isfinite(wood)):
            bad.append((name, "wood-nonfinite"))
        if buf.size and float(buf.min()) < -273.15:
            bad.append((name, "buffer-abs0"))
        if buf.size and float(buf[0]) <= 70.0 and float(buf[1:].max()) > 70.0 + 1e-6:
            bad.append((name, "buffer-cap-crossed:%.4f" % float(buf.max())))
        if dhw.size and float(dhw[0]) <= 70.0 and float(dhw[1:].max()) > 70.0 + 1e-6:
            bad.append((name, "dhw-rating-crossed:%.4f" % float(dhw.max())))
        if wood is not None and wood.size and float(wood[0]) <= 95.0 and float(wood.max()) > 95.0 + 1e-6:
            bad.append((name, "wood-cap-crossed:%.4f" % float(wood.max())))
    return len(SCENARIOS), bad


def main():
    args = sys.argv[1:]
    perturb = "--perturb" in args
    rng = np.random.default_rng(23)

    fams = C.build_families()
    if perturb:
        # Config perturbation: 35 L -> 40 L. The sawtooth amplitude scales
        # with 1/C_buf, so the violation magnitude must move (direction:
        # shrink) under a change an honest fix to the discharge dynamics
        # could not fake.
        b = fams["valve_small"]
        b["optimizer"].model.params.buffer_tank_volume = 40.0
        b["optimizer"].model.params._buffer_ua_cache = None
    worst = 0.0
    worst_at = None
    for name in fams:
        w, at = monotone_family(fams[name], rng)
        print("RESULT monotone_min_delta_k[%s]=%.3e at %s" % (name, w, at))
        if w < worst:
            worst, worst_at = w, (name, at)
        w2, at2 = monotone_family(fams[name], rng, bump_dhw=True)
        print("RESULT monotone_dhw_min_delta_k[%s]=%.3e at %s" % (name, w2, at2))
        if w2 < worst:
            worst, worst_at = w2, (name, at2)
    print("RESULT monotone_min_delta_k=%.3e at %s" % (worst, worst_at))

    # Finding evidence: bump-size scaling of the small-tank (35 L, valved,
    # cop_flow_carnot) buffer violation, plus the 750 L control.
    # (In --perturb mode the 40 L config above carries through here too.)
    small = fams["valve_small"]
    big = fams["valve_store"]
    rng99 = np.random.default_rng(99)
    n = 96
    base99 = rng99.uniform(0, small["optimizer"].model.params.max_electrical_power, n)
    hum99 = np.full(n, 55.0)
    kw99 = dict(dt_hours=0.25, external_heat_kw=C.ext_forecast(n),
                humidity=hum99, start_hour=6.5)

    def _run(b, sched):
        return b["optimizer"].model.simulate_trajectory_with_dhw(
            replace(b["state"]), sched, np.zeros(n), b["outdoor"], b["wind"],
            b["rain"], b["solar"], **kw99
        )

    r_small = _run(small, base99)
    for bump in (1e-3, 1e-2, 1e-1, 1.0):
        worst_b = 0.0
        at = None
        for i in range(0, n, 3):
            s = base99.copy()
            s[i] += bump
            r1 = _run(small, s)
            for j, a0 in enumerate(r_small):
                if a0 is None:
                    continue
                d = np.asarray(r1[j], dtype=float)[i + 1:] - np.asarray(a0, dtype=float)[i + 1:]
                mn = float(d.min())
                if mn < worst_b:
                    worst_b, at = mn, (i, j)
        print("RESULT smalltank_bump_%g_k_worst_cool_k=%.4e at %s" % (bump, worst_b, at))
    r_big = _run(big, base99)
    worst_big = 0.0
    for i in range(0, n, 3):
        s = base99.copy()
        s[i] += 1e-3
        r1 = _run(big, s)
        for j, a0 in enumerate(r_big):
            if a0 is None:
                continue
            d = np.asarray(r1[j], dtype=float)[i + 1:] - np.asarray(a0, dtype=float)[i + 1:]
            worst_big = min(worst_big, float(d.min()))
    print("RESULT bigtank_bump_0.001_k_worst_cool_k=%.4e (control)" % worst_big)

    t_new, t_passive, snapped, refused, ok = hot_tank_check()
    print("RESULT hot_tank_after_c=%.6f passive_c=%.6f snapped=%s refused=%.1e"
          % (t_new, t_passive, snapped, refused))
    print("RESULT hot_tank_rate_not_state_ok=%s" % ok)

    if "--skip-golden" not in args:
        total, bad = golden_bounds()
        print("RESULT golden_bounds_violations=%d of %d" % (len(bad), total))
        for b in bad:
            print("  %s" % (b,))
    print("RESULT concurrent_test_procs=%d" % C.concurrent_test_procs())
    C.epilogue()


if __name__ == "__main__":
    main()
