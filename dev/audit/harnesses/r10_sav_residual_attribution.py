"""R10-SAV-VALUATION-RESIDUE: the savings residual the valved arms leave, attributed.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat|winter_typical

``r10_sav_wood_reference.closed_loop``'s valve arm (no wood, tank at 30 C,
the arm ``valve_arm`` runs) with the plant step and the booked reference
wrapped, never changed. Per plant step, in kWh_th: the plan's pump heat
``cop * heat_per_cop_kw(P) * dt`` and its store change (``_stored_thermal_energy``
next less now), so its loss; and the booked reference stepped once from its
held state (``_thermostat_held_state`` at 21 C) at the power the harness
booked for that step, its pump heat at ``_reference_cop`` and its store
change, so its loss; beside the steady floor demand at 21 C and at the
room the plan delivered (the comfort term's rule).

The harness's residual is ``ref - comfort + stored - plan``. With each
side's loss defined as its heat less its store change, the residual in
kWh_th is ``(L_ref - L_plan - steady gap) + reference store change``: an
identity, so its content is the two measured terms, not their sum. Both are
the booked reference's own: the heat its booked steps draw from the held
state's stores (a reference at equilibrium reads 0), and its loss beyond
the steady comfort term. Precondition, asserted: the wrappers saw every
plant step of the run (``DAYS * 24 / DT``) and a booked reference for each;
the harness exits 1 otherwise.
"""

import sys
sys.path.insert(0, "dev/audit/harnesses")
import r10_sav_wood_reference as h
from heatpump_optimizer.optimizer import (
    _thermostat_held_state, _reference_cop, _floor_demand_at_target, WeatherSeries)
from heatpump_optimizer.thermal_model import heat_per_cop_kw
A = dict(q_p=0.0, ds_p=0.0, q_r=0.0, ds_r=0.0, st_r=0.0, st_p=0.0, n=0)
orig = h._install
def _install(wood, two_zone=True):
    opt, model = orig(wood, two_zone)
    real, real_base = model.simulate_step, opt._compute_baseline_power
    last = {}
    def base(series, state, dt, *a, **k):
        out = real_base(series, state, dt, *a, **k)
        if sys._getframe(1).f_code.co_name == "closed_loop":
            last["booked"], last["series"] = float(out[0][0]), series
        return out
    opt._compute_baseline_power = base
    S = opt._stored_thermal_energy
    def step(*args, **kw):
        if len(args) < 7 or sys._getframe(1).f_code.co_name != "closed_loop":
            return real(*args, **kw)
        state, power, out, wind, rain, sol, dt = args[:7]
        nxt = real(*args, **kw)
        cop_p = model.compute_cop(out, flow_temp=state.buffer_tank_temperature)
        A["q_p"] += cop_p * heat_per_cop_kw(model.params, power) * dt
        A["ds_p"] += S(nxt) - S(state)
        series = last["series"]
        held = _thermostat_held_state(model, state, series, 21.0)
        b = last["booked"]
        ref_next = real(held, b, out, wind, rain, sol, dt, **kw)
        A["q_r"] += _reference_cop(model, held, out, None) * heat_per_cop_kw(model.params, b) * dt
        A["ds_r"] += S(ref_next) - S(held)
        A["st_r"] += _floor_demand_at_target(model, 21.0, out, wind, rain, sol) * dt
        A["st_p"] += _floor_demand_at_target(model, nxt.room_temperature, out, wind, rain, sol) * dt
        A["n"] += 1
        return nxt
    model.simulate_step = step
    return opt, model
h._install = _install
residual_pct = h.closed_loop(False, lambda t: 0.0, None, 30.0, sys.argv[1])[1]
print(f"harness residual {residual_pct:+.2f} %")
L_p, L_r = A["q_p"] - A["ds_p"], A["q_r"] - A["ds_r"]
print(f"steps {A['n']} | plan heat {A['q_p']:.2f} store change {A['ds_p']:+.2f} loss {L_p:.2f} | "
      f"reference heat {A['q_r']:.2f} store change {A['ds_r']:+.2f} loss {L_r:.2f} | "
      f"steady loss at 21 {A['st_r']:.2f} at delivered {A['st_p']:.2f}")
print(f"loss gap ref-plan {L_r - L_p:+.2f} kWh_th against steady {A['st_r'] - A['st_p']:+.2f}: "
      f"non-steady {(L_r - L_p) - (A['st_r'] - A['st_p']):+.2f}; reference stored {A['ds_r']:+.2f} kWh_th")
want = int(h.DAYS * 24 / h.DT)
print(f"plant steps seen {A['n']} of {want}")
sys.exit(0 if A["n"] == want else 1)
