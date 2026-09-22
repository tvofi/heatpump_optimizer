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

def score_plan(m,pw,st,ot,wi,ra,so,pr,minT=16.5):
    room,slab,up,lo,_,_,_=m.simulate_trajectory(st,pw,ot,wi,ra,so,DT)
    r=room[1:]
    cost=float(np.sum(pr*pw*DT))
    viol=float(np.maximum(0,minT-r).sum())
    return cost,viol,r.min(),r.max()

def pin_result(label,res,m,st,ot,wi,ra,so,pr,dhw=False):
    """Pin the post-conditions every solve in this file owes.

    Twelve real solves run here. Before this helper, nine of them were pinned
    by exactly one check -- the comparison that justified calling them -- so a
    solve that returned its own start vector as a plan, or one whose schedule
    left the model's own power bounds, satisfied that comparison and passed.
    These are the properties a solve owes before any comparison is meaningful,
    and the two about a computed quantity read a PRODUCTION symbol rather than
    a copy of one: the model's own ``max_electrical_power`` for the bounds, and
    ``ThermalModel.simulate_trajectory`` (through ``score_plan``) for the
    comfort floor. ``dhw`` adds the same two pins on the hot-water channel.
    """
    pw=np.asarray(res.power_schedule,dtype=float)
    pmax=float(m.params.max_electrical_power)
    R.check(f"{label}: one finite schedule entry per horizon step",
            pw.shape==(N,) and bool(np.all(np.isfinite(pw))),
            f"schedule shape {pw.shape}")
    R.check(f"{label}: every step inside the model's own power bounds",
            bool(np.all(pw>=-1e-9) and np.all(pw<=pmax+1e-9)),
            f"range {pw.min():.3f}-{pw.max():.3f} kW, bound {pmax:.3f}")
    _,viol,_,_=score_plan(m,pw,st,ot,wi,ra,so,pr)
    R.check(f"{label}: the plan holds the comfort floor",viol<=1e-6,
            f"degree-steps below floor: {viol:.4f}")
    if dhw:
        dpw=np.asarray(res.dhw_power_schedule,dtype=float)
        R.check(f"{label}: one finite DHW entry per horizon step",
                dpw.shape==(N,) and bool(np.all(np.isfinite(dpw))),
                f"DHW schedule shape {dpw.shape}")
        R.check(f"{label}: every DHW step inside the model's own power bounds",
                bool(np.all(dpw>=-1e-9) and np.all(dpw<=pmax+1e-9)),
                f"DHW range {dpw.min():.3f}-{dpw.max():.3f} kW")

for tz in (False,True):
    R.section(f"two_zone={tz}")
    opt,m,pr,ot,wi,ra,so,st,start=setup(tz)
    r=opt.optimize(st,pr,ot,wi,ra,so,start)
    base=np.asarray(r.power_schedule)
    c0,v0,mn0,mx0=score_plan(m,base,st,ot,wi,ra,so,pr)
    print(f" optimizer : cost {c0:7.2f}  room {mn0:.2f}-{mx0:.2f}  viol {v0:.3f}")
    R.check("optimizer plan meets the comfort floor", v0 <= 1e-6,
            f"degree-steps below floor: {v0:.4f}")
    pin_result(f"space base (two_zone={tz})",r,m,st,ot,wi,ra,so,pr)

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
    c1,v1,mn1,mx1=score_plan(m,greedy,st,ot,wi,ra,so,pr)
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
        c,v,mn,mx=score_plan(m,cand,st,ot,wi,ra,so,pr)
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
        c3,v3,_,_ = score_plan(m,np.asarray(r3.power_schedule),st,ot,wi,ra,so,pr)
        print(f" starved  : cost {c3:7.2f}  viol {v3:.3f}")
        R.check("the production iteration budget buys a materially better plan",
                v3 <= 1e-6 and c0 <= c3 * 0.95,
                f"full-budget {c0:.2f} vs starved {c3:.2f} "
                f"({100.0*(c3-c0)/c3:.1f}% gap)")
        pin_result("space starved-budget arm (two_zone=True)",r3,m,st,ot,wi,ra,so,pr)

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
    pin_result(f"space no-batch control (two_zone={tz})",r_fd,m,st,ot,wi,ra,so,pr)

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
    pin_result(f"DHW base (two_zone={_tz})",r_batch,m,st,ot,wi,ra,so,pr,dhw=True)
    pin_result(f"DHW no-batch control (two_zone={_tz})",r_fd,m,st,ot,wi,ra,so,pr,dhw=True)

# Challenger 7 (DHW two-zone only): the solver's own STOP RULE, raced
# against itself the way challenger 3 races the budget. R4-D0-02 (#921)
# measured the asymmetry this closes: the iteration budget challenger 3
# polices is never binding (0 of 488 observed L-BFGS-B calls reached the
# cap, worst nit 52 against 200/300), while ftol decides every plan and
# until now no check in this file saw it -- production ftol loosened
# 1000x-10000x (1e-6 -> 1e-3 / 1e-2 in optimizer.py's two options dicts)
# passed all 14 checks at the round-4 baseline while degrading the plan
# on the production objective. The arm loosens ftol to 1e-3 on the
# multi-start's own refinement solves only (the optimizer.py:529 options
# dict) and leaves the restart's (:407) at 1e-6, so it is exactly the
# single-site mutation class the round demonstrated -- a both-sites arm
# would also pass the single-site cut, because the tight restart
# repairs most of a loosened multi-start on the dhw-off scenario above.
# Measured on this scenario (winter_typical / winter_cold / two-zone /
# dhw on, at e069caf): the 1e-3 arm costs 2.6% more energy (61.23 vs
# 59.69 SEK) and 0.5% more objective; 1e-2 costs 10.2% / 1.6%; 1e-4
# moves nothing (5e-5 relative). The bound demands 1%, roughly the same
# ~2.5x headroom over the measured gap challenger 3 keeps, so
# BLAS-to-BLAS noise cannot trip it. Single-zone is insensitive to ftol
# on this scenario (identical cost and objective at 1e-4..1e-2) and the
# dhw-off two-zone cell is non-monotone under loosening (a 1e-2
# multi-start can land in a different basin the restart then repairs),
# which is why the check lives here and only here. Like challenger 3,
# the bound is not a hardcoded objective: if production's ftol is ever
# loosened toward the arm, the two solves converge and the check fails
# by construction.
R.section("stop rule (ftol) on a DHW-enabled two-zone solve (#921)")
_o7, _m7, _pr7, _ot7, _wi7, _ra7, _so7, _st7, _start7 = _dhw_setup(True)
_r7 = _o7.optimize(_st7, _pr7, _ot7, _wi7, _ra7, _so7, _start7)
_c70, _v70, _, _ = score_plan(_m7, np.asarray(_r7.power_schedule),
                              _st7, _ot7, _wi7, _ra7, _so7, _pr7)
pin_result("stop-rule production arm",_r7,_m7,_st7,_ot7,_wi7,_ra7,_so7,_pr7,dhw=True)
_full_scoped_7 = _optm_dhw._scoped_minimize
_full_ms_7 = _optm_dhw._multi_start_minimize
_full_restart_7 = _optm_dhw._lbfgsb_restart


def _loose_ftol_7(*a, **kw):
    kw = dict(kw)
    _opts = dict(kw.get("options") or {})
    _opts["ftol"] = 1e-3
    kw["options"] = _opts
    return _full_scoped_7(*a, **kw)


def _restart_tight_7(*a, **kw):
    with _mock_dhw.patch.object(_optm_dhw, "_scoped_minimize",
                                _full_scoped_7):
        return _full_restart_7(*a, **kw)


def _loose_ms_7(objective, starts, bounds, *a, **kw):
    with _mock_dhw.patch.object(_optm_dhw, "_lbfgsb_restart",
                                _restart_tight_7):
        with _mock_dhw.patch.object(_optm_dhw, "_scoped_minimize",
                                    _loose_ftol_7):
            return _full_ms_7(objective, starts, bounds, *a, **kw)


with _mock_dhw.patch.object(_optm_dhw, "_multi_start_minimize", _loose_ms_7):
    _r7l = _o7.optimize(_st7, _pr7, _ot7, _wi7, _ra7, _so7, _start7)
_c7l, _v7l, _, _ = score_plan(_m7, np.asarray(_r7l.power_schedule),
                              _st7, _ot7, _wi7, _ra7, _so7, _pr7)
pin_result("stop-rule loosened arm",_r7l,_m7,_st7,_ot7,_wi7,_ra7,_so7,_pr7,dhw=True)
print(f" stop-prod : cost {_c70:7.2f}  viol {_v70:.3f}")
print(f" stop-rule: cost {_c7l:7.2f}  viol {_v7l:.3f}")
# The bound was 1% (0.99) against a 2.6% measured gap until #1207 dropped
# the restart keep gate 2e-2 -> 2e-5 (owner directive, #1207 comment
# c1329fe / database id 5750296026, 2026-09-20): the arm's tight restart
# now ADOPTS the sub-2% repairs it used to discard, so it repairs most of
# what the loosened multi-start gives up -- the repair this check's own
# single-site comment predicted. Measured 0.30% on this box at this head
# (59.71 vs 59.88), the same number the parked a42e961 composition
# measured; the gap is environment-wide, not box noise -- the parked
# rounds measured 2.4% on the arm64 dev box and 0.2% on CI's x86_64
# py3.14 runner for the keep-gate-only sibling of this composition -- so
# the bound is set at half the SMALLER environment's number, 0.1%, the
# same derivation the parked tip used when it held both: this box's 0.30%
# clears it with the same 3x headroom the 1% bound kept over 2.6%, and
# the failure construction is unchanged: loosen production's ftol toward
# the arm and the two solves converge past it.
R.check("the production stop rule (ftol) buys a materially better plan",
        _v7l <= 1e-6 and _c70 <= _c7l * 0.999,
        f"ftol 1e-6 {_c70:.2f} vs loosened 1e-3 {_c7l:.2f} "
        f"({100.0*(_c7l-_c70)/_c7l:.2f}% gap, bound 0.1%)")

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
_zc0, _zv0, _zmn, _zmx = score_plan(_zm, _zbase, _zst, _zot, _zwi, _zra, _zso, _zpr)
pin_result("zero-range pinned plan",_zr,_zm,_zst,_zot,_zwi,_zra,_zso,_zpr)
print(f" pinned    : cost {_zc0:7.2f}  room {_zmn:.2f}-{_zmx:.2f}  viol {_zv0:.3f}")
R.check("a pinned plan still meets the comfort floor", _zv0 <= 1e-6,
        f"degree-steps below floor: {_zv0:.4f}")
R.check("the forced-off pin is honoured, or reported as safety-released",
        (90 in _zr.manual_released_space) or _zbase[90] <= 1e-6,
        f"step 90 planned {_zbase[90]:.3f} kW and was not released")
R.check("no step is reported released that was never pinned",
        set(_zr.manual_released_space) <= {90},
        f"released {sorted(_zr.manual_released_space)}, only step 90 was pinned")
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
_zc1, _zv1, _, _ = score_plan(_zm, _zgreedy, _zst, _zot, _zwi, _zra, _zso, _zpr)
print(f" greedy    : cost {_zc1:7.2f}  viol {_zv1:.3f}")
if _zv1 <= _zv0 + 1e-6:
    R.check("greedy does not rout the plan built with a fixed variable",
            _zc1 >= _zc0 * 0.95, f"greedy {_zc1:.2f} vs optimizer {_zc0:.2f}")

# ===== round-5 solver convergence knob: the warm start (#1295) ===========
# One finding ships from the round-5 D0 seam: the previous cycle's shipped
# plan offered to the fresh per-solve optimizer as one more first-solve
# candidate (#1295). The round's other two knobs do not. The tighter
# L-BFGS-B stop rule (#1293) is refuted on money (that is why it is not in
# the diff; tests/backtest.py's shoulder check is the detector), and the
# raised refinement cut with its two appended seeds (#1294) cost a quarter of
# the sweep's solver CPU for a plan-quality gain that does not reproduce
# across BLAS builds, over the D9 sweep budget.
#
# What is checked here is the MECHANISM, not a plan margin. The warm start's
# plan-quality effect is BLAS-dependent: on a developer box it moves the
# objective, and on CI's runner the added candidate is screened out of the
# refinement set and the solve is byte-identical to a cold one. A check that
# pinned its percentage would therefore be a check on a float that does not
# travel -- the void-harness case the judge contract names. The three
# properties below hold on any BLAS, and the first moves under the knob's own
# defect, so the check is not vacuous:
#
#   * the previous plan IS offered as exactly one extra candidate, with the
#     structural candidates unchanged around it;
#   * handing a plan in never returns a plan worse than the one handed in --
#     the multi-start scores every candidate and keeps the cheapest, and the
#     handed-in plan is the best-scoring one here, so it is always refined;
#   * a plan of the wrong width is refused outright.
#
# "Objective" is the production closure value the solve returns, so nothing
# here re-derives a cost; every arm is scored through the production seam
# (``_multi_start_minimize``), never a re-implementation.
from unittest import mock as _kb_mock
import heatpump_optimizer.optimizer as _kb_mod

_kb_start = datetime(2026, 1, 15)


def _kb_inputs(tz, pp, wp, dhw):
    """Fresh optimizer + inputs, so no prior plan and no warm start."""
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(pp, _kb_start)
    ot, wi, ra, so = weather(wp, _kb_start)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st


def _kb_capture(o, pr, ot, wi, ra, so, st):
    """One production solve; every seam call it makes is recorded, with the
    seam left intact."""
    seen = []
    real = _kb_mod._multi_start_minimize

    def rec(objective, candidates, bounds, *a, **kw):
        res = real(objective, candidates, bounds, *a, **kw)
        seen.append([np.asarray(c, float).copy() for c in candidates])
        return res

    with _kb_mock.patch.object(_kb_mod, "_multi_start_minimize", rec):
        r = o.optimize(st, pr, ot, wi, ra, so, _kb_start)
    return r, seen


# --- #1295: the caller's previous plan as a candidate ---------------------
# The coordinator rebuilds the optimizer every cycle, so it is the seat that
# carries the last shipped plan across one (``coordinator._warm_seeded``), and
# the next solve offers it as one extra multi-start candidate. The cell is
# solved cold first; its own plan is then what a later cycle would hand in,
# so the warm arm is the same solve with one candidate added and nothing else
# changed. That makes the candidate lists comparable cell-for-cell, which is
# what the structural check reads.
_kb15c_o, _kb15c_m, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, \
    _kb15c_st = _kb_inputs(False, "winter_typical", "shoulder", True)
_kb15_cold, _kb15_cold_seen = _kb_capture(
    _kb15c_o, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, _kb15c_st)
_kb15_prev = np.asarray(_kb15_cold.power_schedule, dtype=float)
_j15f = float(_kb15_cold.objective_value)

_kb15w_o, _kb15w_m, _kb15w_pr, _kb15w_ot, _kb15w_wi, _kb15w_ra, _kb15w_so, \
    _kb15w_st = _kb_inputs(False, "winter_typical", "shoulder", True)
_kb15w_o._prev_shipped_plan = _kb15_prev.copy()
_kb15_warm, _kb15_warm_seen = _kb_capture(
    _kb15w_o, _kb15w_pr, _kb15w_ot, _kb15w_wi, _kb15w_ra, _kb15w_so, _kb15w_st)
_j15w = float(_kb15_warm.objective_value)

# The candidate is prepended by the path (``h.extra_starts``), so the handed
# plan is the first entry of the first solve's candidate list, and the rest is
# the cold solve's own list, unchanged. Every other solve is untouched.
_kb15_first_cold = _kb15_cold_seen[0]
_kb15_first_warm = _kb15_warm_seen[0]
_kb15_extra = (
    len(_kb15_first_warm) == len(_kb15_first_cold) + 1
    and np.array_equal(_kb15_first_warm[0], _kb15_prev)
    and all(
        np.array_equal(a, b)
        for a, b in zip(_kb15_first_warm[1:], _kb15_first_cold)
    )
    and _kb15_warm_seen[1:] == _kb15_cold_seen[1:]
)
print(f" cold candidates per seam call: {[len(c) for c in _kb15_cold_seen]}")
print(f" warm candidates per seam call: {[len(c) for c in _kb15_warm_seen]}")
R.check(
    "the handed-in plan is one extra candidate and the rest are unchanged "
    "(#1295)",
    _kb15_extra,
    f"cold {[len(c) for c in _kb15_cold_seen]}, "
    f"warm {[len(c) for c in _kb15_warm_seen]}, extra candidate is the "
    f"handed plan: {_kb15_extra} -- equal counts mean ``_warm_start_starts`` "
    f"offered nothing (the #1295 knob switched off); a changed tail means the "
    f"handed plan was substituted for a structural candidate instead of "
    f"added beside it",
)

# No-worse: the handed plan is the best candidate on the objective, so it is
# always refined and the multi-start minimum can only equal or improve it.
# Exact (no slack) and BLAS-independent: both arms run the same code on the
# same inputs, and the min over a candidate set that contains the cold optimum
# cannot exceed it. That makes this arm an INVARIANT rather than a
# discriminator -- with the knob off both arms are the same run and the bound
# holds by equality, so the mutation proof does not redden it. The check that
# moves under the knob's own revert is the candidate-count check above; this
# one pins the code's contract that a stale or wrong-shaped plan can lose,
# never win.
print(f" warm      : obj {_j15w:8.4f}")
print(f" no-warm   : obj {_j15f:8.4f}")
R.check(
    "the handed-in plan is never beaten by the solve that hands it back "
    "(#1295)",
    _j15w <= _j15f * (1 + 1e-9),
    f"warm {_j15w:.4f} vs no-warm {_j15f:.4f} -- a warm plan above the "
    f"handed-in plan's own objective means the candidate was dropped from the "
    f"refinement set it should have led",
)

# Null control: a previous plan of the wrong width is dropped, not clipped or
# padded into a plausible-looking guess, so the solve is the cold solve
# exactly -- byte-identical on any BLAS, because both arms run the same code
# path on the same inputs.
_kb15d_o, _kb15d_m, _kb15d_pr, _kb15d_ot, _kb15d_wi, _kb15d_ra, _kb15d_so, \
    _kb15d_st = _kb_inputs(False, "summer_negative", "shoulder", False)
_kb15d_o._prev_shipped_plan = np.zeros(48)
_kb15d = _kb15d_o.optimize(
    _kb15d_st, _kb15d_pr, _kb15d_ot, _kb15d_wi, _kb15d_ra, _kb15d_so, _kb_start)
_kb15e_o, _kb15e_m, _kb15e_pr, _kb15e_ot, _kb15e_wi, _kb15e_ra, _kb15e_so, \
    _kb15e_st = _kb_inputs(False, "summer_negative", "shoulder", False)
_kb15e = _kb15e_o.optimize(
    _kb15e_st, _kb15e_pr, _kb15e_ot, _kb15e_wi, _kb15e_ra, _kb15e_so, _kb_start)
print(f" width-null: obj {_kb15d.objective_value:.6f} vs fresh "
      f"{_kb15e.objective_value:.6f}")
R.check(
    "a previous plan of the wrong width is dropped, not clipped (#1295 null)",
    np.array_equal(np.asarray(_kb15d.power_schedule),
                   np.asarray(_kb15e.power_schedule))
    and np.array_equal(np.asarray(_kb15d.dhw_power_schedule),
                       np.asarray(_kb15e.dhw_power_schedule)),
    f"wrong-width plan reproduced the fresh plan: "
    f"{np.array_equal(np.asarray(_kb15d.power_schedule), np.asarray(_kb15e.power_schedule))}"
    f" -- False means the width guard reshaped it instead of dropping it",
)

sys.exit(R.close("OPTIMALITY CHECKS"))
