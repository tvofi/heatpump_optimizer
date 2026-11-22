# Per-key step-4 answers for box D3-g29, from the executed probes (probes/probe_<key>.out).
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
PD = "dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes"
U = "unreachable through production"
T = {}

T["e196155b7525014c"] = dict(
    cls="candidate", baseline="'optimal' (success=True, f(x)=1 > f(x0)=0: scipy L-BFGS-B with x0 outside its bounds)",
    mutant="'suboptimal (CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL)'; 2 objective evaluations per successful solve instead of 0",
    inputs=["success, x better than x0 (control: both 'optimal')", "success, x worse than x0", "success, objective raises",
            "real scipy L-BFGS-B result with x0 outside the box bounds", "null: success=False better/worse than x0"],
    reach="golden matrix: 58 of 60 _solver_status calls are successes, 0 of them score above their start (reach_sweep.out)",
    should=("tests/features.py", "a _solver_status check that feeds success=True with result.x scoring above initial_guess and asserts 'optimal' (and that the objective is not re-evaluated on success)"),
    title="No check pins _solver_status's success branch: a converged solve scoring above its start reads 'suboptimal'",
    claim="Mutant e196155b7525014c (optimizer.py:2844 `if result.success:` -> `if False:`) survives the full gate, yet the probe's label moves on a real SciPy result: baseline 'optimal', mutant 'suboptimal (CONVERGENCE: ...)'.",
    metric="the solver_status label _solver_status returns for a SciPy L-BFGS-B success whose start lies outside its bounds (f(x)=1 > f(x0)=0)",
    value="'optimal' -> 'suboptimal (...)'", direction="label 'optimal' -> 'suboptimal (<message>)'", sev="low",
    prop="A SciPy result reporting success is labelled 'optimal' without re-evaluating the objective",
    files=["custom_components/heatpump_optimizer/optimizer.py", "tests/features.py"],
)
for k, line, what in (("9d455ff4aaf3f3e0", 3328, "cop_end (split branch, refill law set)"),
                      ("55022279c6d6bbda", 3329, "cop_buffer (split branch, refill law set)"),
                      ("6a75a1ff72dc1df8", 3338, "cop_end == cop_buffer (single-sum branch, no refill law)")):
    T[k] = dict(cls="equivalent-candidate", note=U,
        baseline="row_cost finite, floored at COP 1e-6 (e.g. 2000001.0 at COP 0)",
        mutant="ZeroDivisionError at COP 0, sign flip at COP -1, x1000 at COP 1e-9; identical at and above 1e-6",
        inputs=[f"{what} = 0.0, -1.0, 1e-9, 1e-6", "null: COP 1.0, 1.05, 2.5, 4.0, nan",
                "reach: ThermalModel.compute_cop / marginal_cop('buffer') over outdoor -60..45 C x humidity x store 20..90 C x 3 parameter sets"],
        reach="every COP _terminal_row_cost receives comes from ThermalModel._cop_law, floored by `return max(cop, 1.0)`: scan minimum 1.0000; golden matrix minimum cop_end 1.5675, cop_buffer 1.1728 (reach_sweep.out)",
        should=("tests/features.py", "none through production: the 1e-6 floor sits under _cop_law's 1.0 floor; only a direct _terminal_row_cost call with COP < 1e-6 separates the arms"))
for k, sym, line in (("133158399eac10ae", "classify_dhw_steps", 2357), ("2d4e3ff8e818b777", "classify_space_steps", 2294)):
    T[k] = dict(cls="equivalent-candidate", note=U,
        baseline="reasons identical to the mutant on all 7 default-threshold inputs; at threshold 0 with zero draw: all 'idle'/'idle_coasting'",
        mutant="identical at the default threshold; at a non-default threshold (0.0, 0.5) every idle step at draw == threshold becomes active",
        inputs=["default threshold: zeros, exactly CHANNEL_ACTIVE_KW, one ulp above/below, mixed, nan, negative",
                "threshold 0.0 with zero draws", "threshold 0.5 with 0.5 kW draws"],
        reach="no production caller passes `threshold` (optimizer.py:2467, 3905), and channel_heating_draw returns 0.0 or a draw strictly above CHANNEL_ACTIVE_KW, so no step equals the default threshold: draws_equal_threshold=0 of 56; golden matrix nondefault_threshold 0, power_eq_threshold 0",
        should=("tests/features.py", f"none through production; only a direct {sym} call with a non-default threshold separates the arms"))
T["4434c1fcedef6b6d"] = dict(cls="equivalent-candidate", note="equivalent for every in-contract input",
    baseline="[] for n_steps == 0", mutant="[] for all 6 in-contract inputs; TypeError only for power=None (out of the np.ndarray contract)",
    inputs=["all-empty arrays", "length-4 arrays", "empty prices", "nan prices", "surplus given", "empty room_temps", "out of contract: power=None", "null: n_steps=4"],
    reach="golden matrix: n_steps_zero 0 of 52 classify_space_steps calls",
    should=("tests/features.py", "none: with n_steps == 0 the loop and idle_codes both return [] without the guard"))
T["69e4aa41f4562af9"] = dict(cls="equivalent-candidate", note=U,
    baseline="last active step's reason 'terminal_value' when room_temps has n_steps samples", mutant="IndexError on that call",
    inputs=["room_temps of n_steps samples, active step 0, 5, n-2, n-1", "null: n_steps + 1 samples at steps 0, 5, n-1"],
    reach="production passes the simulated trajectory, n_steps + 1 states (optimizer.py:3844): golden matrix room_index_at_len 0 of 1999 active steps",
    should=("tests/features.py", "none through production; a direct classify_space_steps call with a short room_temps separates the arms"))
for k, line, tie, b, m, rule in (
    ("8171db177f51df33", 2300, "next room temperature exactly temp_min_bound + 0.15", "comfort_floor", "cheap_price", "if room <= temp_min_bounds[i] + 0.15"),
    ("2aff1f5c0b10dffa", 2303, "PV surplus exactly 1e-6 kW", "cheap_price", "solar_surplus", "surplus[i] > 1e-6"),
    ("000221f3921dd956", 2309, "weather heat-loss factor exactly 1.1", "cheap_price", "preheat_weather", "heat_loss_factors[i] > 1.1")):
    T[k] = dict(cls="candidate", baseline=f"'{b}'", mutant=f"'{m}'",
        inputs={"8171db177f51df33": ["tie at floor 19.0, 0.0, -5.0, 21.85, 35.0 (all move)", "null: room 19.16, 19.14, 21.0"],
                "2aff1f5c0b10dffa": ["tie surplus 1e-6", "null: surplus 0.0, 2e-6, 1.0", "idle_codes at the same tie (reads no sun)"],
                "000221f3921dd956": ["tie factor 1.1", "null: factor 1.0, 1.2", "reach scan: _weather_loss_factors over wind 0..40 m/s (0.01 step) x 8 precipitation levels: 0 of 32008 exactly 1.1"]}[k],
        reach={"8171db177f51df33": "golden matrix: room_eq_floor_plus_015 0 of 1999 active steps; the room trajectory is a continuous solver output, so the tie is in-domain",
               "2aff1f5c0b10dffa": "golden matrix: surplus_eq_1e-6 0 of 1999 active steps; the surplus is a forecast kW series, so the tie is in-domain; idle_codes (optimizer.py:2237) keeps `> 1e-6`, so the mutant splits the two classifiers at the tie",
               "000221f3921dd956": "golden matrix: hlf_eq_1.1 0 of 1999 active steps; scan 0 of 32008; the factor is a ratio of continuous weather inputs, so the tie is in-domain but unfound"}[k],
        should=("tests/features.py", f"a classify_space_steps check at the exact boundary `{rule}` asserting the baseline reason '{b}'"),
        title=f"No check feeds classify_space_steps an active step at its {tie.split(' exactly')[0]} boundary",
        claim=f"Mutant {k} (optimizer.py:{line}, the `{rule}` comparison flipped) survives the full gate, yet the probe's reason moves at the {tie}: baseline '{b}', mutant '{m}'.",
        metric=f"the reason classify_space_steps gives an active step whose {tie}",
        value=f"'{b}' -> '{m}'", direction=f"reason '{b}' -> '{m}' at the exact tie", sev="low",
        prop=f"classify_space_steps' reason at the {tie} is the baseline's '{b}'",
        files=["custom_components/heatpump_optimizer/optimizer.py", "tests/features.py"])
T["8ef8417029ab8385"] = dict(cls="equivalent-candidate", note=U,
    baseline="1.0 at span 0 with demand 0 or -1", mutant="0.0 there; identical at span 0 with demand > 0 and at span > 0",
    inputs=["span 0, demand 0.0 and -1.0", "null: span 0 demand 2; span 30 demand 2 and 0"],
    reach="the only caller (optimizer.py:3593) passes caps['buffer'] = min(buffer_max_temp, max(ceiling, initial)), the ceiling bisected in [max(20, cop_flow_reference_temp=35), buffer_max_temp] and the config flow bounds buffer_max_temperature to 40..90 C, so span = cap - 20 >= 15 K; golden matrix span_zero 0 of 10 calls",
    should=("tests/features.py", "none through production; a direct stored_heat_survival call with cap == ambient and demand <= 0 separates the arms"))
T["b5d57e4a1fc22d96"] = dict(cls="equivalent-candidate", note=U,
    baseline="1.0 for span < 0", mutant="exp(+...) above 1 (3.4903 at span -10 K, demand 2 kW), 0.0 with no demand",
    inputs=["span -10 demand 2 and 0", "span 0 demand 0", "span -0.5 demand 50", "null: span 30 demand 2 and 0"],
    reach=T["8ef8417029ab8385"]["reach"].replace("span_zero", "span_negative"),
    should=("tests/features.py", "none through production; a direct stored_heat_survival call with cap below ambient separates the arms"))
T["f062e0cc415ee33e"] = dict(cls="equivalent-candidate", note="equivalent at every observable output",
    baseline="9.86e-305 for every exponent above 700", mutant="2.0e-313 at 720, 5e-324 at 745, 0.0 beyond; neither arm raises",
    inputs=["exponent 720, 745, 800, 1e6, 1e301, overflow (demand 5e-324)", "consumer: 30 kWh/K x survival x 40 K added to a 0.01 SEK plan cost: identical floats",
            "null: exponent 1, 100, 700"],
    reach="golden matrix: exponent_over_700 0 of 10 calls; the arms differ by at most 9.86e-305, below the ulp of any cost it is summed into",
    should=("tests/features.py", "none: math.exp underflows to 0.0 without raising, so the cap changes no observable value"))
T["0ea7620ce058c489"] = dict(cls="candidate", baseline="shape_h8 1.478675497 after 2 days (predict 1.191470199)",
    mutant="shape_h8 1.36794702 (predict 1.147178808)",
    inputs=["2, 3 and 6 alternating weekday observations (all move)", "null: 0 and 1 observations (first day copied, no EWMA)"],
    reach="production: every observed day after the first per profile (PriceShapeModel.observe_day, price_model.py:229)",
    should=("tests/features.py", "a PriceShapeModel check that folds a second day and asserts shape = (1 - 0.12) * old + 0.12 * new (renormalised)"),
    title="No check pins SHAPE_ALPHA's value; doubling the price-shape EWMA weight is unseen",
    claim="Mutant 0ea7620ce058c489 (price_model.py:66 SHAPE_ALPHA 0.12 -> 0.24) survives the full gate, yet the probe's learned 08:00 shape moves: baseline 1.478675497, mutant 1.36794702 after two observed weekdays.",
    metric="the learned weekday shape factor at 08:00 after two alternating observed days (PriceShapeModel.observe_day)",
    value="1.478675497 -> 1.36794702", direction="down (each later day weighs twice as much)", sev="low",
    prop="The price-shape EWMA weights each day after the first by exactly the documented 0.12",
    files=["custom_components/heatpump_optimizer/price_model.py", "tests/features.py"])
T["213a122afd9ff3e1"] = dict(cls="candidate", baseline="confidence 1.0, expected_daily_min 0.4478 after 5 days",
    mutant="confidence 0.5, expected_daily_min None after 5 days (None until day 10)",
    inputs=["1, 5 and 7 observed weekdays (all move)", "null: 0, 10 and 12 observed days"],
    reach="production: PriceShapeModel.confidence (shape_for, predict, sigma) and expected_daily_min (the elastic legionella gate) on every install with fewer than 10 observed days per profile",
    should=("tests/features.py", "a PriceShapeModel check asserting confidence == 1.0 and a non-None expected_daily_min after exactly 5 observed days (0.8 after 4)"),
    title="No check pins SHAPE_CONFIDENCE_DAYS; trusting the price shape half as fast is unseen",
    claim="Mutant 213a122afd9ff3e1 (price_model.py:69 SHAPE_CONFIDENCE_DAYS 5 -> 10) survives the full gate, yet the probe's confidence after 5 observed weekdays moves: baseline 1.0, mutant 0.5, and expected_daily_min goes 0.4478 -> None.",
    metric="PriceShapeModel.confidence for the weekday profile after 5 observed days",
    value="1.0 -> 0.5", direction="down", sev="low",
    prop="The price shape is fully trusted after exactly the documented 5 observed days",
    files=["custom_components/heatpump_optimizer/price_model.py", "tests/features.py"])
for k, v in T.items():
    v["probe"] = f"{PD}/probe_{k}.py"
