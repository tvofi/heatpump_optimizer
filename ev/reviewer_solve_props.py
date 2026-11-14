"""Reviewer's own instrument: design invariants of the candidate stage on full synthetic solves."""
import sys, time, itertools, dataclasses
from datetime import datetime, timezone
import numpy as np
import heatpump_optimizer.optimizer as om
try:
    from heatpump_optimizer import runs
except ImportError:
    runs = None
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, MIN_RUNNING_DRAW_KW as RUN
from profiles import solve_inputs
STEPS = np.arange(96); T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
seed = int(sys.argv[1]); budget = float(sys.argv[2]); rng = np.random.default_rng(seed)
INST = {"duty1.1": (False, 1.1), "duty0": (False, 0.0), "clamp1.5": (True, 1.5), "fixed5.5": (True, 5.5)}
PRICES = {"sine": lambda: 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0), "flat": lambda: np.full(96, 1.0),
          "spiky": lambda: np.where(rng.random(96) < 0.2, 4.0, 0.6) - 0.8 * (rng.random(96) < 0.1)}
EXTRA = ("none", "caps", "pins_on", "pins_off", "off_steps")
cells = list(itertools.product(INST, (0.0, 0.25, 2.0), (False, True), ((0.0, 0.0), (1.0, 0.0), (0.6, 0.9)), (False, True), PRICES, EXTRA, (-4.0, 4.0, 10.0)))
rng.shuffle(cells)
viol = {}; stats = {"solves": 0, "engaged_calls": 0, "stage_fallback": 0, "failed_status": 0, "realizable_changed": 0}
def note(k, info):
    viol.setdefault(k, []).append(info)
kept = getattr(om, '_commit_runs', None)
def spy(opt, h, scope, relaxed, dhw, maxiter, rescope=None):
    before = opt._space_avail
    out = kept(opt, h, scope, relaxed, dhw, maxiter, rescope)
    after = opt._space_avail
    plan, sc = out
    if not om._engaged(opt):
        if plan is not relaxed[0] or sc is not scope: note("unengaged not identity", CUR)
        return out
    stats["engaged_calls"] += 1
    args = () if dhw is None else (dhw,)
    _, hi, _, cycled = om._stage_box(opt, scope[0], dhw)
    first = om._projection(opt, relaxed[0], dhw, hi, cycled)
    if rescope is None: fsc, fx = scope, first
    else:
        fsc = rescope(first); fx = np.clip(first, *om._stage_box(opt, fsc[0], dhw)[:2])
    s_first = float(fsc[1](fx, *args)); s_ship = float(sc[1](plan, *args))
    opt._space_avail = after
    if s_ship > s_first + 1e-7: note("I1 shipped scores above candidate (1)", (CUR, s_ship, s_first))
    if not np.isfinite(s_ship): note("non-finite shipped score", CUR)
    lo, hi2, other, cyc = om._stage_box(opt, sc[0], dhw)
    if np.any(plan < lo - 1e-7) or np.any(plan > hi2 + 1e-7): note("shipped plan outside its scope's box", (CUR, float(np.max(lo - plan)), float(np.max(plan - hi2))))
    if runs.realizable(relaxed[0] + other, runs.floor_kw(opt.model.params.min_electrical_power)) and not np.array_equal(plan, relaxed[0]):
        stats["realizable_changed"] += 1
    return out
if hasattr(om, '_commit_runs'): om._commit_runs = spy
t_end = time.time() + 1e9; done = 0
for cell in cells:
    if done >= budget: break
    inst, cost, dhw_on, pair, running, pname, extra, out_mean = cell
    if not dhw_on and pair != (0.0, 0.0): continue
    CUR = cell; done += 1
    clamp, p_min = INST[inst]
    params = ThermalParameters(); params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5; params.dhw_enabled = dhw_on
    cfg = om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost)
    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, (501.0, 300.0)
    opt = om.HeatPumpOptimizer(ThermalModel(params), cfg)
    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    kw = {}
    win = np.zeros(96, bool); a = int(rng.integers(0, 80)); win[a:a + int(rng.integers(1, 12))] = True
    if extra == "caps": kw["power_caps_extra"] = np.where(win, float(rng.choice([0.0, 0.6, 1.2, 2.0])), 99.0)
    if extra == "pins_on": kw["space_pins"] = np.where(win, 1.0, np.nan)
    if extra == "pins_off": kw["space_pins"] = np.where(win, 0.0, np.nan)
    if extra == "off_steps": kw["off_steps"] = win
    inp = solve_inputs(initial_state=ThermalState(room_temperature=20.5, upper_floor_temperature=20.5, lower_floor_temperature=20.5,
        slab_temperature=21.0, outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0, dhw_temperature=45.0, dhw_hours_since_legionella=20.0),
        prices=PRICES[pname](), outdoor_temps=outdoor, start_time=T0, **kw)
    HAS = any(f.name == 'compressor_running' for f in dataclasses.fields(inp))
    if HAS: inp = dataclasses.replace(inp, compressor_running=running)
    try:
        res = opt.optimize(inputs=inp)
    except Exception as e:
        note("optimize raised", (CUR, repr(e))); continue
    stats["solves"] += 1
    if "failed" in str(getattr(res, "status", "")): stats["failed_status"] += 1; note("failed status", (CUR, str(res.status)[:120]))
    space = np.asarray(res.power_schedule, float)
    dhw = np.asarray(res.dhw_power_schedule, float) if getattr(res, "dhw_power_schedule", None) is not None else np.zeros(96)
    if dhw.size != 96: dhw = np.zeros(96)
    tot = space + dhw; F = max(p_min, RUN)
    print('CELL', cell, 'over_cap=%.3f' % float(np.max(tot - kw.get('power_caps_extra', np.full(96, 99.0)))), 'obj=%.4f' % float(res.objective_value), 'kwh=%.2f' % (tot.sum() / 4), 'under=%d' % int(np.sum((space > RUN) & (space < F - 1e-6))))
    capv = kw.get("power_caps_extra", np.full(96, 99.0))
    pinned = ~np.isnan(kw.get("space_pins", np.full(96, np.nan)))
    eng = cost > 0 or clamp
    if eng:
        bad = (dhw <= 0) & (space > RUN) & (space < F - 1e-6) & (capv >= F) & ~pinned
        if bad.any(): note("I2 space step between running rule and floor, no cap, no charge", (CUR, int(bad.sum()), space[bad][:4].tolist()))
        besid = (dhw > 0) & (tot > RUN) & (tot < F - 1e-6)
        if besid.any(): note("(info) combined draw under the floor on a hot-water step", (CUR, int(besid.sum())))
    if clamp:
        bad = (tot > 1e-9) & ((tot < p_min - 1e-6) | (tot > 5.5 + 1e-6)) & (capv >= p_min)
        if bad.any(): note("I4 clamped total outside {0} or [p_min,p_max]", (CUR, tot[bad][:4].tolist()))
    if np.any(tot > capv + 1e-6): note("total above the external cap", (CUR, float(np.max(tot - capv))))
    if extra == "off_steps" and np.any(space[win] > 1e-9): note("space on an off step", (CUR,))
    pub = getattr(res, "compressor_starts", None)
    if runs is not None and pub is not None and int(pub) != runs.edge_count(tot, running): note("published starts != edge count with the running reading", (CUR, pub, runs.edge_count(tot, running)))
    if not eng and HAS:
        inp2 = dataclasses.replace(inp, compressor_running=not running)
        r2 = om.HeatPumpOptimizer(ThermalModel(params), cfg).optimize(inputs=inp2)
        if not np.array_equal(np.asarray(r2.power_schedule), space): note("null: running flag moved an unengaged plan", (CUR,))
for k, v in viol.items():
    print(f"RESULT solve[{seed}] {k}: x{len(v)} first={str(v[0])[:600]}")
print(f"RESULT solve[{seed}] stats {stats}; violated properties {len([k for k in viol if not k.startswith('(info)')])}")
