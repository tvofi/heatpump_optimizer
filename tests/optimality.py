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

for tz in (False,True):
    R.section(f"two_zone={tz}")
    opt,m,pr,ot,wi,ra,so,st,start=setup(tz)
    r=opt.optimize(st,pr,ot,wi,ra,so,start)
    base=np.asarray(r.power_schedule)
    c0,v0,mn0,mx0=score_plan(m,base,st,ot,wi,ra,so,pr)
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
_zc1, _zv1, _, _ = score_plan(_zm, _zgreedy, _zst, _zot, _zwi, _zra, _zso, _zpr)
print(f" greedy    : cost {_zc1:7.2f}  viol {_zv1:.3f}")
if _zv1 <= _zv0 + 1e-6:
    R.check("greedy does not rout the plan built with a fixed variable",
            _zc1 >= _zc0 * 0.95, f"greedy {_zc1:.2f} vs optimizer {_zc0:.2f}")

# ===== round-5 solver convergence knobs (#1294 / #1295) ==================
# Two findings, one seam: every knob below decides which basin the
# multi-start L-BFGS-B settles in -- how many structured candidates the
# refinement cut keeps, and whether the previous cycle's shipped plan is
# offered as a candidate. Each check is the smallest arm that moves under its
# own knob's defect and no other, and the cells are the round-5 core grid's,
# named in each comment.
# "Objective" is the production closure value the solve returns, so nothing
# here re-derives a cost; every arm is scored through the production seam
# (``_multi_start_minimize``/``_scoped_minimize``), never a re-implementation.
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


def _kb_capture(o, pr, ot, wi, ra, so, st, extra=None):
    """One production solve; every seam call it makes is recorded, with the
    seam left intact except for ``extra`` (an optional wrapper)."""
    seen = []
    real = _kb_mod._multi_start_minimize
    inner = real if extra is None else extra

    def rec(objective, candidates, bounds, *a, **kw):
        res = inner(objective, candidates, bounds, *a, **kw)
        seen.append(dict(
            objective=objective,
            candidates=[np.asarray(c, float).copy() for c in candidates],
            bounds=[tuple(b) for b in bounds],
            args=tuple(kw.get("args") or a),
            maxiter=int(kw.get("maxiter") or 300),
            batch=kw.get("batch_objective"),
            x=np.asarray(res.x, float).copy()))
        return res

    with _kb_mock.patch.object(_kb_mod, "_multi_start_minimize", rec):
        r = o.optimize(st, pr, ot, wi, ra, so, _kb_start)
    return r, seen


# --- #1294: the structured seeds and the refinement cut ------------------
# The finding's own patch pair: seeds alone (patch_f1) left 21 of 160 cells
# WORSE than the pre-fix configuration because the four-solve cut displaced
# cheaper candidates; seeds WITH the cut raised to six (patch_f1b) left 0
# worse and 19 better. The pair is what ships and the cut is what makes it
# safe, so the cut is checked behaviourally against the arm the finding itself
# measured (patch_f1's configuration) and both appended seeds are pinned
# structurally. Nothing here checks the seeds behaviourally: see the note under
# the cut check for the measurement that says why.
_kb_real_ms = _kb_mod._multi_start_minimize
_kb_cut_keep = _kb_mod._MULTI_START_SOLVES


def _kb_cut4_arm(objective, candidates, bounds, *a, **kw):
    """The cut knob alone: every candidate kept, the cut back at 4."""
    _kb_mod._MULTI_START_SOLVES = 4
    try:
        return _kb_real_ms(objective, candidates, bounds, *a, **kw)
    finally:
        _kb_mod._MULTI_START_SOLVES = _kb_cut_keep


def _kb_obj(tz, pp, wp, dhw, arm=None):
    """One production solve on a fresh optimizer, so no warm start enters."""
    o, _m, pr, ot, wi, ra, so, st = _kb_inputs(tz, pp, wp, dhw)
    if arm is None:
        r = o.optimize(st, pr, ot, wi, ra, so, _kb_start)
    else:
        with _kb_mock.patch.object(_kb_mod, "_multi_start_minimize", arm):
            r = o.optimize(st, pr, ot, wi, ra, so, _kb_start)
    return float(r.objective_value)


# (a) the cut knob, and the reason it is not raised for free. patch_f1's own
# JSON diff (race_cells_judgef1 against race_cells_judge) names this cell the
# worst regression of the seeds-alone configuration: 1.1091 at the pre-fix
# baseline against 1.1248 seeds-alone, +1.4177%. The arm here IS that
# configuration -- every candidate kept, the cut back at 4 -- and it lands on
# the judge's own seeds-alone value exactly: 1.1090981870 against
# 1.1248217169, +1.3979%.
#
# This is also the only behavioural #1294 check there is, and the reason is
# measured, not assumed. The appended seed was re-measured at this head against
# a faithful pre-fix arm -- the seed dropped, the cut back at 4, a
# single-candidate repair call left intact. An arm that drops the last element
# of EVERY call instead empties that one-candidate call and the arm fails
# structurally; against it this cell printed 19.4353 with the seed and 19.6801
# without, a 1.2440% "gain" that was the arm's own failure -- the faithful arm
# reaches 19.4353 too, exactly the production plan. Against the faithful arm
# every seed cell moves by 0.0999% or less, inside the band this suite calls
# noise, so a check on the seed alone would be a check on a float. What ships
# is the pair; the cut carries it.
_j14c = _kb_obj(True, "summer_negative", "shoulder", True)
_j14d = _kb_obj(True, "summer_negative", "shoulder", True, arm=_kb_cut4_arm)
print(f" cut-prod  : obj {_j14c:8.4f}")
print(f" cut-4     : obj {_j14d:8.4f}")
R.check(
    "the raised refinement cut keeps the appended seeds from displacing a "
    "cheaper candidate (#1294)",
    _j14c <= _j14d * 0.999,
    f"production {_j14c:.4f} vs seeds kept/cut 4 {_j14d:.4f} "
    f"({100.0 * (_j14d - _j14c) / abs(_j14d):+.3f}% gain, bound 0.10%) -- "
    f"the shipped plan must beat the seeds-alone configuration, and matching "
    f"it means the cut went back to four and the displaced candidate is "
    f"shipping again",
)

# Null control: on a cell no configuration regresses, the cut-4 arm IS the
# production plan, so the arm is not universally worse either.
_j14e = _kb_obj(False, "winter_extreme", "winter_cold", False)
_j14f = _kb_obj(False, "winter_extreme", "winter_cold", False,
                arm=_kb_cut4_arm)
print(f" cut-null  : obj {_j14e:8.4f} vs cut 4 {_j14f:8.4f}")
R.check(
    "the seeds-kept/cut-4 arm is inert where the race measured no regression "
    "(#1294 null)",
    abs(_j14e - _j14f) <= abs(_j14e) * 5e-5,
    f"production {_j14e:.4f} vs seeds kept/cut 4 {_j14f:.4f} on "
    f"tz=0,dhw=0,winter_extreme,winter_cold -- equal means there was no "
    f"candidate to displace there",
)

# (b) both appended seeds, pinned structurally. At this head their own cells
# move by 0.0999% or less, inside the band, so presence is what is
# BLAS-independent: one candidate more than the pre-fix four on each of the two
# default paths, which is what the seam is handed. (tests/features.py pins the
# DHW path's count a second time, off ``_solve_space`` itself.)
_kb14p_o, _kb14p_m, _kb14p_pr, _kb14p_ot, _kb14p_wi, _kb14p_ra, _kb14p_so, \
    _kb14p_st = _kb_inputs(False, "winter_typical", "summer_cool", False)
_kb14p_r, _kb14p_seen = _kb_capture(
    _kb14p_o, _kb14p_pr, _kb14p_ot, _kb14p_wi, _kb14p_ra, _kb14p_so, _kb14p_st)
_kb14p_lens = [len(c["candidates"]) for c in _kb14p_seen]
_kb14q_o, _kb14q_m, _kb14q_pr, _kb14q_ot, _kb14q_wi, _kb14q_ra, _kb14q_so, \
    _kb14q_st = _kb_inputs(False, "flat", "shoulder", True)
_kb14q_r, _kb14q_seen = _kb_capture(
    _kb14q_o, _kb14q_pr, _kb14q_ot, _kb14q_wi, _kb14q_ra, _kb14q_so, _kb14q_st)
_kb14q_lens = [len(c["candidates"]) for c in _kb14q_seen]
print(f" space-only candidates per seam call: {_kb14p_lens}")
print(f" dhw-path candidates per seam call:   {_kb14q_lens}")
R.check(
    "both default paths carry their appended seed as one more candidate "
    "(#1294)",
    _kb14p_lens == [5] and _kb14q_lens == [5],
    f"space-only {_kb14p_lens}, dhw {_kb14q_lens} -- 4 means the #1294 seed "
    f"went missing on that path; a longer list means the repair re-solve ran "
    f"and this is reading the wrong call",
)

# --- #1295: the caller's previous plan as a candidate ---------------------
# The coordinator rebuilds the optimizer every cycle, so it is the seat that
# carries the last shipped plan across one (``coordinator._warm_seeded``), and
# the next solve offers it as one extra multi-start candidate. The pair below
# is the race's own walk predecessor (flat/summer_cool -> winter_typical/
# shoulder, tz=0, DHW on) for a cell whose prev-plan seed won 0.323% at the
# merge base and where the lead still moves at this head. The same cell solved
# with no plan handed in is the no-warm-start arm.
_kb15a_o, _kb15a_m, _kb15a_pr, _kb15a_ot, _kb15a_wi, _kb15a_ra, _kb15a_so, \
    _kb15a_st = _kb_inputs(False, "flat", "summer_cool", True)
_kb15b_o, _kb15b_m, _kb15b_pr, _kb15b_ot, _kb15b_wi, _kb15b_ra, _kb15b_so, \
    _kb15b_st = _kb_inputs(False, "winter_typical", "shoulder", True)
_kb15a_prev = _kb15a_o.optimize(
    _kb15a_st, _kb15a_pr, _kb15a_ot, _kb15a_wi, _kb15a_ra, _kb15a_so, _kb_start)
_kb15b_o._prev_shipped_plan = np.asarray(
    _kb15a_prev.power_schedule, dtype=float)
_kb15_warm = _kb15b_o.optimize(
    _kb15b_st, _kb15b_pr, _kb15b_ot, _kb15b_wi, _kb15b_ra, _kb15b_so, _kb_start)
_kb15c_o, _kb15c_m, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, \
    _kb15c_st = _kb_inputs(False, "winter_typical", "shoulder", True)
_kb15_fresh = _kb15c_o.optimize(
    _kb15c_st, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, _kb_start)
_j15w = float(_kb15_warm.objective_value)
_j15f = float(_kb15_fresh.objective_value)
print(f" warm      : obj {_j15w:8.4f}")
print(f" no-warm   : obj {_j15f:8.4f}")
R.check(
    "the handed-in previous plan buys a better MPC plan (#1295)",
    _j15w <= _j15f * 0.999,
    f"warm {_j15w:.4f} vs no-warm {_j15f:.4f} "
    f"({100.0 * (_j15f - _j15w) / abs(_j15f):+.3f}% gain, bound 0.10%)",
)

# Null control: a previous plan of the wrong width is dropped, not clipped or
# padded into a plausible-looking guess, so the solve is the no-warm-start
# solve exactly.
_kb15c_o, _kb15c_m, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, \
    _kb15c_st = _kb_inputs(False, "summer_negative", "shoulder", False)
_kb15c_o._prev_shipped_plan = np.zeros(48)
_kb15c = _kb15c_o.optimize(
    _kb15c_st, _kb15c_pr, _kb15c_ot, _kb15c_wi, _kb15c_ra, _kb15c_so, _kb_start)
_j15c = float(_kb15c.objective_value)
_kb15d_o, _kb15d_m, _kb15d_pr, _kb15d_ot, _kb15d_wi, _kb15d_ra, _kb15d_so, \
    _kb15d_st = _kb_inputs(False, "summer_negative", "shoulder", False)
_kb15d = _kb15d_o.optimize(
    _kb15d_st, _kb15d_pr, _kb15d_ot, _kb15d_wi, _kb15d_ra, _kb15d_so, _kb_start)
_j15d = float(_kb15d.objective_value)
print(f" width-null: obj {_j15c:8.4f} vs fresh {_j15d:8.4f}")
R.check(
    "a previous plan of the wrong width is dropped, not clipped (#1295 null)",
    abs(_j15c - _j15d) <= abs(_j15d) * 1e-9,
    f"wrong-width {_j15c:.4f} vs fresh {_j15d:.4f} -- equal means the width "
    f"guard rejected it rather than reshaping it",
)

sys.exit(R.close("OPTIMALITY CHECKS"))
