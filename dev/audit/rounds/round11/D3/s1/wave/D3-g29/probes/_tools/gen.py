import os
SP = os.path.dirname(os.path.abspath(__file__))
PRE = open(os.path.join(SP, "prelude.py")).read()
OUT = os.path.expanduser("~/probe-tree/dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes")
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
MACH = "box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14)"
P = {}

def add(key, metric, expected, symbol, perturb, null, body):
    P[key] = (metric, expected, symbol, perturb, null, body)

# ---------------------------------------------------------------- _solver_status
add("e196155b7525014c",
"the solver_status label optimizer._solver_status returns for a SciPy result with success=True, and the objective "
"evaluations it spends classifying it",
["status_success_worse_than_x0 baseline 'optimal', mutant 'suboptimal (...)'",
 "status_real_lbfgsb_x0_outside_bounds baseline 'optimal', mutant 'suboptimal (...)' (scipy's own result)",
 "moved=3 count over the 4 success inputs (success_better is the in-arm control); objective_evals per success 0 -> 2",
 "null_delta=0 count (success=False results: the guard is false either way)"],
"custom_components.heatpump_optimizer.optimizer:_solver_status line 2844 `if result.success:`; called at optimizer.py:4983 and 5574",
"key e196155b7525014c GUARD_OFF `    if result.success:` -> `    if False:`, in memory (re-compiled from its own source). Direction: 'optimal' -> 'suboptimal (<message>)' on a success whose point scores above its start",
"success=False results (ABNORMAL_TERMINATION_IN_LNSRCH, better and worse than the start): identical labels",
r'''
from scipy.optimize import minimize
mut = mutant(opt, "_solver_status", 2844, "    if result.success:", "    if False:")
evals = [0]


def f(x):
    evals[0] += 1
    return float(np.sum(np.square(np.asarray(x, dtype=float) - 2.0)))


def boom(x):
    raise RuntimeError("objective unavailable")


x0 = np.zeros(3)
# A real L-BFGS-B success whose point scores ABOVE its start: x0 = 2 lies outside the box [0, 1],
# SciPy projects it in, converges at 1 (f = 1) while f(x0) = 0.
real = minimize(lambda x: float((x[0] - 2.0) ** 2), np.array([2.0]), method="L-BFGS-B", bounds=[(0.0, 1.0)])
print(f"RESULT real_lbfgsb_success={bool(real.success)} f_x={float(real.fun):.6f} f_x0=0.000000")
cases = {
    "success_better": (SimpleNamespace(success=True, x=np.full(3, 2.0), message="CONVERGENCE"), f, x0),
    "success_worse_than_x0": (SimpleNamespace(success=True, x=np.full(3, 5.0), message="CONVERGENCE"), f, x0),
    "success_objective_raises": (SimpleNamespace(success=True, x=np.ones(3), message="CONVERGENCE"), boom, x0),
    "real_lbfgsb_x0_outside_bounds": (real, lambda x: float((np.asarray(x)[0] - 2.0) ** 2), np.array([2.0])),
}
nulls = {
    "fail_worse": (SimpleNamespace(success=False, x=np.full(3, 5.0), message="ABNORMAL_TERMINATION_IN_LNSRCH"), f, x0),
    "fail_better": (SimpleNamespace(success=False, x=np.full(3, 2.0), message="ABNORMAL_TERMINATION_IN_LNSRCH"), f, x0),
}
moved = 0
for name, (res, obj, start) in cases.items():
    evals[0] = 0; b = call(opt._solver_status, res, obj, start); eb = evals[0]
    evals[0] = 0; m = call(mut, res, obj, start); em = evals[0]
    print(f"RESULT status_{name}_baseline={b!r}")
    print(f"RESULT status_{name}_mutant={m!r}")
    if obj is f:
        print(f"RESULT objective_evals_{name}={eb}->{em} count")
    moved += not same(b, m)
print(f"RESULT moved={moved} count")
null_delta = 0
for name, (res, obj, start) in nulls.items():
    null_delta += not same(call(opt._solver_status, res, obj, start), call(mut, res, obj, start))
print(f"RESULT null_delta={null_delta} count")
reach("solver_status")
footer()
''')

# ---------------------------------------------------------------- _terminal_row_cost x3
TRC = r'''
mut = mutant(opt, "_terminal_row_cost", LINE, OLD, NEW)
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
stores = ((10.0, "room", 21.0, 1.0), (5.0, "buffer", 50.0, 1.0))
terms = [2.0, 3.0]


def ident(e):
    return e


def row(fn, cop):
    rc, _ = fn(1.0, *ARGS(cop))
    return call(rc, terms)


moved, tried = 0, []
for cop in (0.0, -1.0, 1e-9, 1e-6):
    b, m = row(opt._terminal_row_cost, cop), row(mut, cop)
    print(f"RESULT row_cost_{WHAT}_{cop!r}_baseline={b!r}")
    print(f"RESULT row_cost_{WHAT}_{cop!r}_mutant={m!r}")
    moved += not same(b, m); tried.append(cop)
print(f"RESULT moved={moved} count of {len(tried)} sub-floor COPs")
null_delta = sum(not same(row(opt._terminal_row_cost, c), row(mut, c)) for c in (1.0, 1.05, 2.5, 4.0, float("nan")))
print(f"RESULT null_delta={null_delta} count (COP 1.0, 1.05, 2.5, 4.0, nan)")
# Reach: every COP the terminal cost receives is ThermalModel._cop_law's, floored by `return max(cop, 1.0)`.
lo = math.inf
for kw in ({}, {"cop_flow_carnot": True}, {"cop_flow_carnot": True, "flow_curve_cop": True}):
    p = ThermalParameters()
    for k, v in kw.items():
        setattr(p, k, v)
    m_ = ThermalModel(p)
    for t in np.linspace(-60.0, 45.0, 106):
        for hum in (None, 0.0, 60.0, 100.0):
            lo = min(lo, m_.compute_cop(float(t), humidity=hum))
            for st in (20.0, 35.0, 55.0, 70.0, 90.0):
                lo = min(lo, m_.marginal_cop(float(t), "buffer", store_temp=st, humidity=hum))
print(f"RESULT reach_min_cop_over_scan={lo:.4f} (outdoor -60..45 C, humidity, store 20..90 C, 3 parameter sets)")
reach("terminal_row_cost")
footer()
'''
for key, line, old, new, what, args, branch in (
    ("9d455ff4aaf3f3e0", 3328, "                    deficit / max(cop_end, 1e-6)", "                    deficit / (cop_end)",
     "cop_end", "lambda cop: (cop, 3.0, stores, ident)", "split (cop_buffer != cop_end) with a refill law"),
    ("55022279c6d6bbda", 3329, "                    + buffer_deficit / max(cop_buffer, 1e-6)", "                    + buffer_deficit / (cop_buffer)",
     "cop_buffer", "lambda cop: (3.0, cop, stores, ident)", "split (cop_buffer != cop_end) with a refill law"),
    ("6a75a1ff72dc1df8", 3338, "        return refill_price * deficit / max(cop_end, 1e-6)", "        return refill_price * deficit / (cop_end)",
     "cop_end_eq_buffer", "lambda cop: (cop, cop, stores, None)", "single-sum (cop_buffer == cop_end), no refill law"),
):
    body = (TRC.replace("LINE", str(line)).replace("OLD", repr(old)).replace("NEW", repr(new))
            .replace("ARGS", f"({args})").replace("{WHAT}", what))
    add(key,
        f"the terminal row cost _terminal_row_cost(...)'s row_cost returns on its {branch} branch for terms [2, 3] at a "
        f"{what} below the 1e-6 floor; and the smallest COP production can hand it",
        [f"row_cost at {what}=0.0: baseline a finite 2e6-scale value, mutant 'raises ZeroDivisionError'",
         "moved=4 count of 4 sub-floor COPs (0, -1, 1e-9, 1e-6 -- at 1e-6 the arms tie)" if False else
         "moved=3 count of 4 sub-floor COPs (0, -1, 1e-9 move; 1e-6 is the floor itself and ties)",
         "null_delta=0 count", "reach_min_cop_over_scan >= 1.0 (ThermalModel._cop_law: max(cop, 1.0))"],
        f"custom_components.heatpump_optimizer.optimizer:_terminal_row_cost.row_cost line {line}; built at optimizer.py:3695 from ThermalModel.compute_cop / marginal_cop",
        f"key {key} CLAMP_DROP `{old.strip()}` -> `{new.strip()}`, in memory (the enclosing _terminal_row_cost re-compiled). Direction: a finite floored cost -> ZeroDivisionError / sign flip below COP 1e-6",
        "COPs at or above the floor (1.0, 1.05, 2.5, 4.0) and nan: identical",
        body)

# ---------------------------------------------------------------- classifiers, threshold
CLS_THR = r'''
mut = mutant(opt, SYM, LINE, "        if power[i] <= threshold:", "        if power[i] < threshold:")
from heatpump_optimizer.thermal_model import CHANNEL_ACTIVE_KW
n = 8


def run(fn, power, threshold=None):
    kw = {} if threshold is None else {"threshold": threshold}
    if SYM == "classify_space_steps":
        return call(fn, np.asarray(power, float), np.linspace(1.0, 2.0, n), np.full(n + 1, 21.0),
                    np.full(n, 19.0), np.ones(n), None, n, **kw)
    return call(fn, np.asarray(power, float), np.array([0, 0, 1, 1, 0, 0, 0, 0], bool), np.zeros(n), None, n, **kw)


k = CHANNEL_ACTIVE_KW
default_inputs = {
    "zeros": [0.0] * n, "at_active_kw": [k] * n, "just_above": [np.nextafter(k, 1.0)] * n,
    "just_below": [np.nextafter(k, 0.0)] * n, "mixed": [0.0, k, 0.5, 2.0, k, 0.0, 3.0, 0.0],
    "nan": [float("nan")] * n, "negative": [-1.0] * n,
}
moved_default = 0
for name, pw in default_inputs.items():
    b, m = run(getattr(opt, SYM), pw), run(mut, pw)
    moved_default += not same(b, m)
print(f"RESULT moved_default_threshold={moved_default} count of {len(default_inputs)} inputs")
moved_nd = 0
for name, pw, thr in (("zeros_threshold_0", [0.0] * n, 0.0), ("half_kw_threshold_half", [0.5] * n, 0.5)):
    b, m = run(getattr(opt, SYM), pw, thr), run(mut, pw, thr)
    print(f"RESULT reasons_{name}_baseline={b!r}")
    print(f"RESULT reasons_{name}_mutant={m!r}")
    moved_nd += not same(b, m)
print(f"RESULT moved_nondefault_threshold={moved_nd} count of 2 inputs")
# Why the default is inert: the classifier reads channel_heating_draw, which is 0.0 or strictly above CHANNEL_ACTIVE_KW.
draws = np.concatenate([opt._heating_draws(np.asarray(pw, float), None)[0] for pw in default_inputs.values()])
print(f"RESULT draws_equal_threshold={int(np.sum(draws == k))} count of {draws.size} draws")
print("RESULT null_delta=0 count (the default-threshold arm above is the null: no production caller passes threshold)")
reach(SYM)
footer()
'''
for key, sym, line in (("133158399eac10ae", "classify_dhw_steps", 2357), ("2d4e3ff8e818b777", "classify_space_steps", 2294)):
    add(key,
        f"the reason list optimizer.{sym} returns, compared baseline vs mutant, at the default threshold "
        "(CHANNEL_ACTIVE_KW, the only one production passes) and at a non-default one",
        ["moved_default_threshold=0 count of 7 inputs", "moved_nondefault_threshold=2 count of 2 inputs",
         "draws_equal_threshold=0", "reach: nondefault_threshold absent (0) and power_eq_threshold 0 over the 50 golden scenarios"],
        f"custom_components.heatpump_optimizer.optimizer:{sym} line {line} `if power[i] <= threshold:`",
        f"key {key} CMP_BOUND `<=` -> `<` at line {line}, in memory. Direction: an idle step at power == threshold becomes active",
        "the default-threshold inputs (zeros, exactly CHANNEL_ACTIVE_KW, one ulp either side, mixed, nan, negative): identical",
        CLS_THR.replace("SYM", repr(sym)).replace("LINE", str(line)).replace("reach(" + repr(sym) + ")", f"reach({sym!r})"))

# ---------------------------------------------------------------- classify_space_steps n_steps == 0
add("4434c1fcedef6b6d",
"the reason list classify_space_steps returns for n_steps == 0, baseline vs mutant, over in-contract array inputs",
["moved_in_contract=0 count of 6 inputs (every arm returns [])", "power_none: baseline [] mutant 'raises ...' (out of contract)",
 "reach: n_steps_zero absent (0) over the 50 golden scenarios"],
"custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2286 `if n_steps == 0:`",
"key 4434c1fcedef6b6d GUARD_OFF `    if n_steps == 0:` -> `    if False:`, in memory. Direction: none found in contract",
"the n_steps >= 1 call (guard false either way): identical",
r'''
mut = mutant(opt, "classify_space_steps", 2286, "    if n_steps == 0:", "    if False:")
E = np.array([])
four = np.array([0.0, 1.0, 2.0, 0.0])
inputs = {
    "all_empty": (E, E, np.array([21.0]), E, E, None),
    "four_long": (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "prices_empty": (four, E, np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "prices_nan": (four, np.full(4, np.nan), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "surplus_given": (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), np.ones(4)),
    "room_empty": (four, np.ones(4), E, np.full(4, 19.0), np.ones(4), None),
}
moved = 0
for name, a in inputs.items():
    b, m = call(opt.classify_space_steps, *a, 0), call(mut, *a, 0)
    moved += not same(b, m)
    print(f"RESULT n0_{name}_baseline={b!r} mutant={m!r}")
print(f"RESULT moved_in_contract={moved} count of {len(inputs)} inputs")
b = call(opt.classify_space_steps, None, None, None, None, None, None, 0)
m = call(mut, None, None, None, None, None, None, 0)
print(f"RESULT power_none_baseline={b!r} mutant={m!r} (out of contract: the annotations say np.ndarray)")
a = (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None)
print(f"RESULT null_delta={int(not same(call(opt.classify_space_steps, *a, 4), call(mut, *a, 4)))} count")
reach("classify_space_steps")
footer()
''')

# ---------------------------------------------------------------- classify_space_steps per-branch boundaries
SPACE = r'''
mut = mutant(opt, "classify_space_steps", LINE, OLD, NEW)
n = 20


def run(fn, i, room=21.0, floor=19.0, surplus=None, hlf=1.0, room_len=None):
    power = np.zeros(n); power[i] = 3.0
    rooms = np.full(n + 1 if room_len is None else room_len, 21.0); rooms[min(i + 1, len(rooms) - 1)] = room
    floors = np.full(n, floor)
    hl = np.ones(n); hl[i] = hlf
    return call(fn, power, np.linspace(1.0, 2.0, n), rooms, floors, hl, surplus, n)


BODY
reach("classify_space_steps")
footer()
'''
add("69e4aa41f4562af9",
"the reason classify_space_steps gives the last active step when room_temps has n_steps samples instead of n_steps + 1",
["room_short baseline reason list, mutant 'raises IndexError'", "moved=1 count", "null_delta=0 count (n_steps + 1 samples)",
 "reach: room_index_at_len absent (0) over 1999 active golden steps"],
"custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2299 (room index); production passes the simulated trajectory (n_steps + 1 states, optimizer.py:3844)",
"key 69e4aa41f4562af9 CMP_BOUND `i + 1 < len(room_temps)` -> `<=`, in memory. Direction: clamp to the last sample -> IndexError",
"room_temps of n_steps + 1 samples: identical",
SPACE.replace("LINE", "2299").replace("OLD", repr("        room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1]"))
.replace("NEW", repr("        room = room_temps[i + 1] if i + 1 <= len(room_temps) else room_temps[-1]"))
.replace("BODY", r'''
b, m = run(opt.classify_space_steps, n - 1, room_len=n), run(mut, n - 1, room_len=n)
print(f"RESULT room_short_baseline={b[-1] if isinstance(b, list) else b!r}")
print(f"RESULT room_short_mutant={m[-1] if isinstance(m, list) else m!r}")
moved = int(not same(b, m))
for i in (0, 5, n - 2):
    moved_i = not same(run(opt.classify_space_steps, i, room_len=n), run(mut, i, room_len=n))
    print(f"RESULT room_short_step{i}_moved={int(moved_i)}")
print(f"RESULT moved={moved} count")
nd = sum(not same(run(opt.classify_space_steps, i), run(mut, i)) for i in (0, 5, n - 1))
print(f"RESULT null_delta={nd} count")
'''))

add("8171db177f51df33",
"the reason classify_space_steps gives an active step whose next room temperature is exactly floor + 0.15",
["tie baseline 'comfort_floor', mutant the next rank ('cheap_price')", "moved=1 count",
 "null_delta=0 count (room one hundredth above or below the tie)", "reach: room_eq_floor_plus_015 absent (0) over 1999 active golden steps"],
"custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2300 `if room <= temp_min_bounds[i] + 0.15:`",
"key 8171db177f51df33 CMP_BOUND `<=` -> `<`, in memory. Direction: comfort_floor -> a lower-ranked reason at the exact tie",
"room = floor + 0.16 and floor + 0.14: identical",
SPACE.replace("LINE", "2300").replace("OLD", repr("        if room <= temp_min_bounds[i] + 0.15:"))
.replace("NEW", repr("        if room < temp_min_bounds[i] + 0.15:"))
.replace("BODY", r'''
tie = 19.0 + 0.15
b, m = run(opt.classify_space_steps, 2, room=tie), run(mut, 2, room=tie)
print(f"RESULT tie_reason_baseline={b[2] if isinstance(b, list) else b!r}")
print(f"RESULT tie_reason_mutant={m[2] if isinstance(m, list) else m!r}")
print(f"RESULT moved={int(not same(b, m))} count")
for fl in (0.0, -5.0, 21.85, 35.0):
    t = fl + 0.15
    print(f"RESULT tie_floor{fl}_moved={int(not same(run(opt.classify_space_steps, 2, room=t, floor=fl), run(mut, 2, room=t, floor=fl)))}")
nd = sum(not same(run(opt.classify_space_steps, 2, room=r), run(mut, 2, room=r)) for r in (19.16, 19.14, 21.0))
print(f"RESULT null_delta={nd} count")
'''))

add("2aff1f5c0b10dffa",
"the reason classify_space_steps gives an active step whose PV surplus is exactly 1e-6 kW",
["tie baseline the next rank ('cheap_price'), mutant 'solar_surplus'", "moved=1 count",
 "null_delta=0 count (surplus 0, 2e-6, 1.0)", "reach: surplus_eq_1e-6 absent (0) over 1999 active golden steps"],
"custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2303 `surplus[i] > 1e-6`",
"key 2aff1f5c0b10dffa CMP_BOUND `>` -> `>=`, in memory. Direction: a lower-ranked reason -> solar_surplus at the exact tie",
"surplus 0.0, 2e-6, 1.0 at the step: identical",
SPACE.replace("LINE", "2303").replace("OLD", repr("        if surplus is not None and i < len(surplus) and surplus[i] > 1e-6:"))
.replace("NEW", repr("        if surplus is not None and i < len(surplus) and surplus[i] >= 1e-6:"))
.replace("BODY", r'''
def sp(v):
    s = np.zeros(n); s[2] = v
    return s


b, m = run(opt.classify_space_steps, 2, surplus=sp(1e-6)), run(mut, 2, surplus=sp(1e-6))
print(f"RESULT tie_reason_baseline={b[2] if isinstance(b, list) else b!r}")
print(f"RESULT tie_reason_mutant={m[2] if isinstance(m, list) else m!r}")
print(f"RESULT moved={int(not same(b, m))} count")
nd = sum(not same(run(opt.classify_space_steps, 2, surplus=sp(v)), run(mut, 2, surplus=sp(v))) for v in (0.0, 2e-6, 1.0))
print(f"RESULT null_delta={nd} count")
# The sibling predicate idle_codes reads for the same series (optimizer.py:2237) is `> 1e-6`: under the mutant the
# two classifiers split at the tie.
codes = opt.idle_codes(4, np.zeros(4), None, None, None, np.array([0.0, 1e-6, 0.0, 0.0]), None, None, 0.05)
print(f"RESULT idle_codes_at_tie={codes!r} (idle_codes's own `> 1e-6` reads the tie as no sun)")
'''))

add("000221f3921dd956",
"the reason classify_space_steps gives an active step whose weather heat-loss factor is exactly 1.1",
["tie baseline the next rank ('cheap_price'), mutant 'preheat_weather'", "moved=1 count",
 "null_delta=0 count (factor 1.0, 1.2)", "reach_exact_1.1 over the wind/precipitation scan of _weather_loss_factors: printed (exact count)"],
"custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2309 `heat_loss_factors[i] > 1.1`; the factors are optimizer._weather_loss_factors",
"key 000221f3921dd956 CMP_BOUND `>` -> `>=`, in memory. Direction: a lower-ranked reason -> preheat_weather at the exact tie",
"factor 1.0 and 1.2: identical",
SPACE.replace("LINE", "2309").replace("OLD", repr("        if i < len(heat_loss_factors) and heat_loss_factors[i] > 1.1:"))
.replace("NEW", repr("        if i < len(heat_loss_factors) and heat_loss_factors[i] >= 1.1:"))
.replace("BODY", r'''
b, m = run(opt.classify_space_steps, 2, hlf=1.1), run(mut, 2, hlf=1.1)
print(f"RESULT tie_reason_baseline={b[2] if isinstance(b, list) else b!r}")
print(f"RESULT tie_reason_mutant={m[2] if isinstance(m, list) else m!r}")
print(f"RESULT moved={int(not same(b, m))} count")
nd = sum(not same(run(opt.classify_space_steps, 2, hlf=v), run(mut, 2, hlf=v)) for v in (1.0, 1.2))
print(f"RESULT null_delta={nd} count")
# Honest reach search: does the production factor ever land on exactly 1.1?
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
model = ThermalModel(ThermalParameters())
wind = np.round(np.arange(0.0, 40.0001, 0.01), 2)
exact = 0; total = 0; near = 0
for rain in (0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
    f = opt._weather_loss_factors(model, wind, np.full(len(wind), rain), len(wind))
    exact += int(np.sum(f == 1.1)); near += int(np.sum(np.abs(f - 1.1) < 1e-9)); total += len(f)
print(f"RESULT reach_exact_1.1={exact} count of {total} (wind 0..40 m/s step 0.01, 8 precipitation levels)")
print(f"RESULT reach_within_1e-9_of_1.1={near} count")
'''))

# ---------------------------------------------------------------- stored_heat_survival
SHS = r'''
mut = mutant(opt, "stored_heat_survival", LINE, OLD, NEW)
amb = opt.DHW_COOLING_REFERENCE_AMBIENT_TEMP
BODY
# Reach: the only caller (optimizer.py:3593) passes caps["buffer"], set at optimizer.py:6031 to
# min(buffer_max_temp, max(_buffer_charge_ceiling, initial)), where the ceiling bisects in
# [max(20, cop_flow_reference_temp), buffer_max_temp] and the config flow bounds buffer_max_temperature to 40..90 C.
from heatpump_optimizer.thermal_model import ThermalParameters
print(f"RESULT reach_ambient={amb} C reach_cop_flow_reference_default={ThermalParameters().cop_flow_reference_temp} C")
reach("stored_heat_survival")
footer()
'''
add("8ef8417029ab8385",
"the survival fraction stored_heat_survival(ua, cap, demand) returns when the tank cap equals the reference ambient (span 0)",
["span0_demand0 baseline 1.0, mutant 0.0", "moved=2 count (demand 0 and -1)", "null_delta=0 count (span 0 with demand > 0; span > 0)",
 "reach: span_zero absent (0) over the golden buffer-store calls"],
"custom_components.heatpump_optimizer.optimizer:stored_heat_survival line 3177 `if span <= 0.0:`",
"key 8ef8417029ab8385 CMP_BOUND `<=` -> `<`, in memory. Direction: 1.0 -> 0.0 at span == 0 with no demand",
"span 0 with demand 2 kW, and span 30 K: identical",
SHS.replace("LINE", "3177").replace("OLD", repr("    if span <= 0.0:")).replace("NEW", repr("    if span < 0.0:")).replace("BODY", r'''
moved = 0
for d in (0.0, -1.0):
    b, m = call(opt.stored_heat_survival, 0.5, amb, d), call(mut, 0.5, amb, d)
    print(f"RESULT span0_demand{d}_baseline={b!r} mutant={m!r}")
    moved += not same(b, m)
print(f"RESULT moved={moved} count")
nd = sum(not same(call(opt.stored_heat_survival, 0.5, c, d), call(mut, 0.5, c, d)) for c, d in ((amb, 2.0), (amb + 30.0, 2.0), (amb + 30.0, 0.0)))
print(f"RESULT null_delta={nd} count")
'''))
add("b5d57e4a1fc22d96",
"the survival fraction stored_heat_survival(ua, cap, demand) returns when the tank cap sits below the reference ambient (span < 0)",
["span_neg baseline 1.0, mutant exp(+...) > 1 (3.4903 at ua 0.5, span -10 K, demand 2 kW)", "moved>=2 count", "null_delta=0 count (span > 0)",
 "reach: span_negative absent (0) over the golden buffer-store calls"],
"custom_components.heatpump_optimizer.optimizer:stored_heat_survival line 3177 `if span <= 0.0:`",
"key b5d57e4a1fc22d96 GUARD_OFF `    if span <= 0.0:` -> `    if False:`, in memory. Direction: 1.0 -> above 1 (or 0.0 with no demand)",
"span 30 K at demand 2 kW and 0 kW: identical",
SHS.replace("LINE", "3177").replace("OLD", repr("    if span <= 0.0:")).replace("NEW", repr("    if False:")).replace("BODY", r'''
moved = 0
for c, d in ((amb - 10.0, 2.0), (amb - 10.0, 0.0), (amb, 0.0), (amb - 0.5, 50.0)):
    b, m = call(opt.stored_heat_survival, 0.5, c, d), call(mut, 0.5, c, d)
    print(f"RESULT span{c - amb:+.1f}_demand{d}_baseline={b!r} mutant={m!r}")
    moved += not same(b, m)
print(f"RESULT moved={moved} count of 4")
nd = sum(not same(call(opt.stored_heat_survival, 0.5, amb + 30.0, d), call(mut, 0.5, amb + 30.0, d)) for d in (2.0, 0.0))
print(f"RESULT null_delta={nd} count")
'''))
add("f062e0cc415ee33e",
"the survival fraction stored_heat_survival returns when its exponent 0.5*ua*span/demand exceeds 700, and that value's "
"effect on a terminal cost it is added into",
["no arm raises (raises=0 both arms)", "exponent 720: baseline exp(-700)=9.86e-305, mutant ~2.0e-313: the float moves",
 "cost_delta_after_adding=0.0 (the buffer credit term mass*survival*deficit added to a 0.01 SEK plan cost: identical floats)",
 "null_delta=0 count (exponent <= 700)"],
"custom_components.heatpump_optimizer.optimizer:stored_heat_survival line 3186 `math.exp(-min(0.5 * ua * span / demand, 700.0))`",
"key f062e0cc415ee33e CLAMP_DROP `min(..., 700.0)` dropped, in memory. Direction: exp(-700) -> exp(-x) < 1e-304 (or 0.0)",
"exponent 1, 100, 700 exactly: identical",
SHS.replace("LINE", "3186").replace("OLD", repr("    return float(math.exp(-min(0.5 * ua * span / demand, 700.0)))"))
.replace("NEW", repr("    return float(math.exp(-(0.5 * ua * span / demand)))")).replace("BODY", r'''
ua, cap = 1.0, amb + 30.0           # span 30 K: exponent = 15 / demand
raises = [0, 0]; moved = 0; worst = 0.0; diffs = []
for x in (720.0, 745.0, 800.0, 1e6, 1e301):
    d = 15.0 / x
    b, m = call(opt.stored_heat_survival, ua, cap, d), call(mut, ua, cap, d)
    raises[0] += isinstance(b, str); raises[1] += isinstance(m, str)
    print(f"RESULT exponent{x:g}_baseline={b!r} mutant={m!r}")
    moved += not same(b, m)
    if not isinstance(b, str) and not isinstance(m, str):
        worst = max(worst, abs(b - m))
        # The consumer: the buffer's credit coefficient mass * survival times a deficit, summed into a plan cost.
        term_b, term_m = 30.0 * b * 40.0, 30.0 * m * 40.0
        diffs.append((0.01 + term_b) - (0.01 + term_m))
d = 5e-324                          # the smallest positive demand: 15 / 5e-324 overflows
b, m = call(opt.stored_heat_survival, ua, cap, d), call(mut, ua, cap, d)
print(f"RESULT exponent_overflow_baseline={b!r} mutant={m!r}")
raises[0] += isinstance(b, str); raises[1] += isinstance(m, str)
print(f"RESULT raises_baseline={raises[0]} raises_mutant={raises[1]} count")
print(f"RESULT moved={moved} count of 5 (the float, all below 1e-304)")
print(f"RESULT max_abs_survival_delta={worst:.3e}")
print(f"RESULT cost_delta_after_adding={max(abs(v) for v in diffs):.1f} (0.01 SEK plan cost + 30 kWh/K * survival * 40 K)")
nd = sum(not same(call(opt.stored_heat_survival, ua, cap, 15.0 / x), call(mut, ua, cap, 15.0 / x)) for x in (1.0, 100.0, 700.0))
print(f"RESULT null_delta={nd} count")
'''))

# ---------------------------------------------------------------- price_model constants
PM = r'''
from datetime import datetime, timedelta
day_a = [0.5] * 6 + [2.0] * 4 + [1.0] * 6 + [2.5] * 4 + [0.8] * 4      # 24 hourly prices
day_b = [1.0] * 6 + [1.0] * 4 + [3.0] * 6 + [1.0] * 4 + [1.0] * 4
mon = datetime(2026, 1, 5, 0, 0)                                        # a Monday: the weekday profile


def learn(days):
    m = pm.PriceShapeModel()
    for k in range(days):
        m.observe_day(mon + timedelta(days=7 * k), day_a if k % 2 == 0 else day_b)
    return m


def metrics(days):
    m = learn(days)
    at = mon + timedelta(days=7 * days, hours=8)
    return {"shape_h8": round(float(m.shapes[0][8]), 9), "confidence": m.confidence(at),
            "predict_h8": round(m.predict(at, 1.0), 9), "expected_daily_min": m.expected_daily_min([0], 1.0)}


BODY
footer()
'''
add("0ea7620ce058c489",
"the learned weekday shape factor at 08:00 after N alternating observed days (PriceShapeModel.observe_day), and predict() there",
["two_days shape_h8 baseline != mutant (EWMA weight 0.12 vs 0.24)", "moved=N count over N in (2, 3, 6)", "null_delta=0 count (0 and 1 observed days: the first day is copied, no EWMA)"],
"custom_components.heatpump_optimizer.price_model:SHAPE_ALPHA (line 66), read in PriceShapeModel.observe_day (line 229)",
"key 0ea7620ce058c489 CONST `SHAPE_ALPHA = 0.12` -> `0.24`, by mock.patch.object on the module attribute. Direction: each later day weighs twice as much",
"0 and 1 observed days: identical",
PM.replace("BODY", r'''
moved = 0
for days in (2, 3, 6):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_ALPHA", 0.24):
        m = metrics(days)
    print(f"RESULT days{days}_shape_h8_baseline={b['shape_h8']} mutant={m['shape_h8']}")
    print(f"RESULT days{days}_predict_h8_baseline={b['predict_h8']} mutant={m['predict_h8']}")
    moved += b != m
print(f"RESULT moved={moved} count of 3")
nd = 0
for days in (0, 1):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_ALPHA", 0.24):
        nd += b != metrics(days)
print(f"RESULT null_delta={nd} count")
'''))
add("213a122afd9ff3e1",
"the weekday shape confidence, predict() at 08:00 and expected_daily_min after N observed days (PriceShapeModel)",
["days5 confidence baseline 1.0, mutant 0.5; expected_daily_min baseline a value, mutant None", "moved=N count over N in (1, 5, 7)",
 "null_delta=0 count (0 days: confidence 0 both; 10 and 12 days: 1.0 both)"],
"custom_components.heatpump_optimizer.price_model:SHAPE_CONFIDENCE_DAYS (line 69), read in PriceShapeModel.confidence (285) and expected_daily_min (342)",
"key 213a122afd9ff3e1 CONST `SHAPE_CONFIDENCE_DAYS = 5` -> `10`, by mock.patch.object. Direction: the shape is trusted half as fast; the legionella shopping gate answers None until day 10",
"0, 10 and 12 observed days: identical",
PM.replace("BODY", r'''
moved = 0
for days in (1, 5, 7):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_CONFIDENCE_DAYS", 10):
        m = metrics(days)
    print(f"RESULT days{days}_confidence_baseline={b['confidence']} mutant={m['confidence']}")
    print(f"RESULT days{days}_predict_h8_baseline={b['predict_h8']} mutant={m['predict_h8']}")
    print(f"RESULT days{days}_expected_daily_min_baseline={b['expected_daily_min']} mutant={m['expected_daily_min']}")
    moved += b != m
print(f"RESULT moved={moved} count of 3")
nd = 0
for days in (0, 10, 12):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_CONFIDENCE_DAYS", 10):
        nd += b != metrics(days)
print(f"RESULT null_delta={nd} count")
'''))

os.makedirs(OUT, exist_ok=True)
for key, (metric, expected, symbol, perturb, null, body) in P.items():
    rel = f"dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_{key}.py"
    hdr = ["#!/usr/bin/env python3", f"# Metric: {metric}.",
           f"# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {rel} [--reach]",
           "#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)"]
    hdr += [f"# EXPECTED {e}" for e in expected]
    hdr += [f"# Baseline: {BASE}. Machine: {MACH}.", f"# Instrumented symbol: {symbol}.",
            f"# Perturbation: {perturb}.", f"# Null control: {null}.",
            "# Values are exact (deterministic); no timing is measured."]
    open(os.path.join(OUT, f"probe_{key}.py"), "w").write("\n".join(hdr) + "\n" + PRE + body)
print(len(P), "probes written")
