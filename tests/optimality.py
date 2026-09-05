"""Solution-quality floor for the optimizer.

Not an optimality proof — the solver is a multi-start local method over a
non-convex objective and the challengers here only price energy cost, not
the full objective (comfort pull, cycling, capacity). What this asserts is
a floor: the plan must satisfy comfort, and no trivial challenger may beat
it by a margin that says "the solver missed the basin", with generous
headroom over the measured gap so BLAS-to-BLAS solver noise cannot trip it.

Measured on the pinned test stack (2026-08): single-zone — greedy ties the
optimizer to the öre and 0/300 perturbations beat it; two-zone — greedy is
2.4% cheaper at a colder room minimum (it is buying less comfort, which the
objective prices and this cost comparison does not) and 2/300 perturbations
find at most 1.7%. The thresholds below are roughly double those gaps.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_components"))
import numpy as np
from datetime import datetime
from harness import Results
from profiles import prices, weather, house, DT, N
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer, OptimizationConfig)
rng=np.random.default_rng(0)
R = Results("Optimality floor")

def setup(tz, price_p="winter_typical", weather_p="winter_cold", start=datetime(2026,1,15)):
    cfg=house(two_zone=tz); p=ThermalParameters.from_config(cfg); p.dhw_enabled=False
    m=ThermalModel(p)
    opt=HeatPumpOptimizer(m,OptimizationConfig(horizon_hours=24,time_step_minutes=15,
        target_temp=21.0,min_temp=17.0,max_temp=23.0))
    pr=prices(price_p,start); ot,wi,ra,so=weather(weather_p,start)
    st=ThermalState(room_temperature=21.0,slab_temperature=22.0,
        outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
    return opt,m,pr,ot,wi,ra,so,st,start

def evaluate(m,pw,st,ot,wi,ra,so,pr,minT=16.5):
    room,slab,up,lo,_,_,_=m.simulate_trajectory(st,pw,ot,wi,ra,so,DT)
    r=room[1:]
    cost=float(np.sum(pr*pw*DT))
    viol=float(np.maximum(0,minT-r).sum())
    return cost,viol,r.min(),r.max()

for tz in (False,True):
    R.section(f"two_zone={tz}")
    opt,m,pr,ot,wi,ra,so,st,start=setup(tz)
    r=opt.optimize(st,pr,ot,wi,ra,so,start)
    base=np.asarray(r.power_schedule)
    c0,v0,mn0,mx0=evaluate(m,base,st,ot,wi,ra,so,pr)
    print(f" optimizer : cost {c0:7.2f}  room {mn0:.2f}-{mx0:.2f}  viol {v0:.3f}")
    R.check("optimizer plan meets the comfort floor", v0 <= 1e-6,
            f"degree-steps below floor: {v0:.4f}")

    # Challenger 1: same total energy, greedily moved to the cheapest slots.
    # It may run the house colder than the optimizer chose to (comfort is
    # not in this cost), so the bound is a floor with headroom, not a tie.
    total=base.sum()
    pmax=m.params.max_electrical_power
    order=np.argsort(pr)
    greedy=np.zeros(N); left=total
    for i in order:
        take=min(pmax,left); greedy[i]=take; left-=take
        if left<=0: break
    c1,v1,mn1,mx1=evaluate(m,greedy,st,ot,wi,ra,so,pr)
    print(f" greedy    : cost {c1:7.2f}  room {mn1:.2f}-{mx1:.2f}  viol {v1:.3f}")
    if v1 <= v0 + 1e-6:
        R.check("greedy same-energy challenger does not rout the optimizer",
                c1 >= c0 * 0.95, f"greedy {c1:.2f} vs optimizer {c0:.2f}")

    # Challenger 2: random perturbations that keep comfort. Finding a
    # slightly cheaper neighbour is expected on the two-zone objective
    # (cost here is not the objective); finding a much cheaper one means
    # the solver stopped short of its basin's floor.
    best=c0; improved=0
    for k in range(300):
        cand=np.clip(base+rng.normal(0,0.6,N),0,pmax)
        c,v,mn,mx=evaluate(m,cand,st,ot,wi,ra,so,pr)
        if v<=v0+1e-6 and c<best-0.01:
            best=c; improved+=1
    print(f" random    : {improved}/300 comfort-safe perturbations cheaper; best {best:7.2f}")
    R.check("no perturbation finds a materially cheaper comfort-safe plan",
            best >= c0 * 0.965, f"best {best:.2f} vs optimizer {c0:.2f}")

    # Challenger 3 (two-zone only): the solver's own iteration budget,
    # raced against itself. A second solve with maxiter slashed to 3 --
    # the exact 300 -> 3 cut this gate once could not see (issue #89) --
    # must be materially cheaper when solved at the production budget:
    # measured 16.2% costlier starved on this scenario, against 0.3%
    # single-zone (which is why the check lives here and only here). The
    # bound is not a hardcoded objective: if production's budget is ever
    # cut, the two solves coincide and the check fails by construction.
    # Headroom is generous over the measured gap, like every threshold
    # in this file, so BLAS-to-BLAS noise cannot trip it.
    if tz:
        from unittest import mock
        from heatpump_optimizer import optimizer as _opt_mod
        _full_ms = _opt_mod._multi_start_minimize
        def _starved_ms(objective, starts, bounds, *a, **kw):
            kw["maxiter"] = 3
            return _full_ms(objective, starts, bounds, *a, **kw)
        with mock.patch.object(_opt_mod, "_multi_start_minimize", _starved_ms):
            r3 = opt.optimize(st,pr,ot,wi,ra,so,start)
        c3,v3,_,_ = evaluate(m,np.asarray(r3.power_schedule),st,ot,wi,ra,so,pr)
        print(f" starved  : cost {c3:7.2f}  viol {v3:.3f}")
        R.check("the production iteration budget buys a materially better plan",
                v3 <= 1e-6 and c0 <= c3 * 0.95,
                f"full-budget {c0:.2f} vs starved {c3:.2f} "
                f"({100.0*(c3-c0)/c3:.1f}% gap)")

    # Challenger 4: the batched-FD jac (issue #97) must move no plan. The
    # production path solves through objective_batch/_batch_fd_gradient; a
    # control solve with the batch stripped falls back to scipy's own FD,
    # and the two schedules must agree bit for bit -- the jac reproduces
    # scipy's 2-point estimate exactly (same eps, same bounds rule) or
    # the iterate path, and the plan with it, would diverge. This is the
    # equivalence the drift gate holds across every captured scenario;
    # here it is asserted directly on the solve this file already runs.
    # Run for both zones: the single-zone and two-zone objectives each
    # carry their own batch twin.
    from unittest import mock
    from heatpump_optimizer import optimizer as _opt_mod
    _full_ms = _opt_mod._multi_start_minimize
    def _nobatch_ms(objective, starts, bounds, *a, **kw):
        kw.pop("batch_objective", None)
        return _full_ms(objective, starts, bounds, *a, **kw)
    with mock.patch.object(_opt_mod, "_multi_start_minimize", _nobatch_ms):
        r_fd = opt.optimize(st, pr, ot, wi, ra, so, start)
    same = np.array_equal(
        np.round(np.asarray(r_fd.power_schedule), 12),
        np.round(base, 12),
    )
    R.check("the batched-FD jac reproduces scipy's own gradient path exactly",
            same,
            "schedules differ -- the jac is not bit-identical to scipy's FD")

# Challenger 5: the same batched-jac bit-identity race, but for a DHW-ENABLED
# solve -- the class the batched jac was blocked from until D9-01. Enabling DHW
# pins the space bounds unevenly (per-step headroom under the DHW block), which
# is exactly the non-uniform shape the old uniform-bounds gate refused to hand
# the batch. Now that it serves them, the batched path must still land on the
# byte-identical schedule scipy's own FD would, or the 38/39 DHW golden
# scenarios we just moved onto the batch would drift. Run single- and two-zone;
# the two-zone-DHW case additionally exercises the tariff/valve one-sided rule.
R.section("batched-FD jac on DHW-enabled solves (D9-01)")
from unittest import mock as _mock_dhw
from heatpump_optimizer import optimizer as _optm_dhw


def _dhw_setup(tz, start=datetime(2026, 1, 15)):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices("winter_typical", start)
    ot, wi, ra, so = weather("winter_cold", start)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st, start


for _tz in (False, True):
    o, m, pr, ot, wi, ra, so, st, start = _dhw_setup(_tz)
    r_batch = o.optimize(st, pr, ot, wi, ra, so, start)
    base_dhw = np.asarray(r_batch.power_schedule)

    _full_ms_d = _optm_dhw._multi_start_minimize

    def _nobatch_ms_d(objective, starts, bounds, *a, **kw):
        kw.pop("batch_objective", None)
        return _full_ms_d(objective, starts, bounds, *a, **kw)

    with _mock_dhw.patch.object(
            _optm_dhw, "_multi_start_minimize", _nobatch_ms_d):
        r_fd = o.optimize(st, pr, ot, wi, ra, so, start)
    same_dhw = np.array_equal(
        np.round(np.asarray(r_fd.power_schedule), 12),
        np.round(base_dhw, 12),
    )
    R.check(
        f"DHW-enabled batched-FD jac matches scipy's gradient path "
        f"(two_zone={_tz})",
        same_dhw,
        "DHW schedules differ -- the batched jac diverges from scipy's FD "
        "on non-uniform (DHW-pinned) bounds")

# Challenger 6: the ZERO-RANGE-BOUND path (#286/#287). Every solve above
# leaves each variable a strictly positive range. One forced-off manual pin
# is one (0, 0) bound out of 96, and until this section neither this file nor
# stress.py had ever passed a pin or a power cap -- so no check anywhere in
# the gate had seen a plan produced with a fixed variable in it.
#
# #317 has since made that path CHEAP (a fixed variable is treated as fixed
# rather than as a reason to abandon the batched jacobian; stress.py measures
# the 6-12x it removed). Cheap is not the same as checked. What #317 changed
# is precisely the gradient the solver descends on these bounds, and the way
# that fails is silent: a jac that returns NaN at a fixed variable kills
# L-BFGS-B at status 2 with nit 0 and hands back the starting vector as a
# plan, without raising anything. Cost alone would not notice -- a solve that
# gives up immediately is FASTER. The three checks below are what notices:
# comfort, the pin's own contract, and a trivial challenger that must not
# rout the plan.
R.section("solution quality on a zero-range bound (D9-01)")
_zopt, _zm, _zpr, _zot, _zwi, _zra, _zso, _zst, _zstart = setup(False)
_pins = np.full(N, float("nan"))
_pins[90] = 0.0                       # 22:30, one step forced off
_zr = _zopt.optimize(_zst, _zpr, _zot, _zwi, _zra, _zso, _zstart,
                     space_pins=_pins)
_zbase = np.asarray(_zr.power_schedule)
_zc0, _zv0, _zmn, _zmx = evaluate(_zm, _zbase, _zst, _zot, _zwi, _zra, _zso, _zpr)
print(f" pinned    : cost {_zc0:7.2f}  room {_zmn:.2f}-{_zmx:.2f}  viol {_zv0:.3f}")
R.check("a pinned plan still meets the comfort floor", _zv0 <= 1e-6,
        f"degree-steps below floor: {_zv0:.4f}")
R.check("the forced-off pin is honoured, or reported as safety-released",
        (90 in _zr.manual_released_space) or _zbase[90] <= 1e-6,
        f"step 90 planned {_zbase[90]:.3f} kW and was not released")
_ztotal = _zbase.sum()
_zpmax = _zm.params.max_electrical_power
_zgreedy = np.zeros(N); _zleft = _ztotal
for _i in np.argsort(_zpr):
    _take = min(_zpmax, _zleft)
    if 90 not in _zr.manual_released_space and _i == 90:
        _take = 0.0                   # the challenger has to respect the pin too
    _zgreedy[_i] = _take; _zleft -= _take
    if _zleft <= 0:
        break
_zc1, _zv1, _, _ = evaluate(_zm, _zgreedy, _zst, _zot, _zwi, _zra, _zso, _zpr)
print(f" greedy    : cost {_zc1:7.2f}  viol {_zv1:.3f}")
if _zv1 <= _zv0 + 1e-6:
    R.check("greedy does not rout the plan built with a fixed variable",
            _zc1 >= _zc0 * 0.95, f"greedy {_zc1:.2f} vs optimizer {_zc0:.2f}")

sys.exit(R.close("OPTIMALITY CHECKS"))
