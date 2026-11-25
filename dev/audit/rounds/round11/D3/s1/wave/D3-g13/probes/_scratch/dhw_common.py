import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
    horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
planner = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
BASE_FN = DhwPlanner._apply_dhw_min_run
MIN_RUN, P_MAX = 0.6, 3.0


def run(plan, fn=None, initial=50.0, ceiling=50.0, draws=None, p_max=P_MAX, min_run=MIN_RUN, dt=0.25):
    n = len(plan)
    draws = np.zeros(n) if draws is None else draws
    return (fn or BASE_FN)(
        planner, plan=np.array(plan, dtype=float), initial_temp=initial, outdoor_temps=np.zeros(n),
        draw_rates=draws, dt=dt, p_dhw_max=p_max, min_run_power=min_run, max_temp=np.full(n, ceiling))


def fixture(n, n_weak, seed, initial, ceiling, draw_level):
    """features.py's _mr_fixture shape: weak slots spread over the horizon, a draw block in the middle."""
    rng = np.random.default_rng(seed)
    draws = np.zeros(n)
    draws[n // 2:n // 2 + n // 6] = draw_level
    plan = np.zeros(n)
    pos = np.linspace(1, n - 2, n_weak).astype(int)
    plan[pos] = 0.05 + 0.5 * rng.random(n_weak)
    strong = rng.choice(n, size=max(1, n // 10), replace=False)
    plan[strong] = np.where(plan[strong] > 0, plan[strong], 1.0 + 2.0 * rng.random(strong.size))
    return plan, dict(initial=initial, ceiling=ceiling, draws=draws)


def sweep(fn, seeds=range(12)):
    """Production-shaped fixtures (0 <= plan <= p_max, min_run <= p_max as dhw_planner.py:1141 guarantees)."""
    moved, total = [], 0
    for seed in seeds:
        for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
            for n, nw in ((24, 3), (96, 24), (48, 10)):
                plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                total += 1
                b, m = run(plan, **kw), run(plan, fn, **kw)
                if b.shape != m.shape or not np.array_equal(b, m):
                    moved.append((seed, initial, ceiling, draw, n, float(np.max(np.abs(b - m)))))
    return moved, total


def joint_cases(seeds=range(12)):
    """How many sweep fixtures take the joint shortcut (no per-slot _dhw_raise_fits call) on the baseline."""
    calls = {"n": 0}
    orig = DhwPlanner._dhw_raise_fits

    def counted(self, *a, **k):
        calls["n"] += 1
        return orig(self, *a, **k)

    joint = per_slot = 0
    with mock.patch.object(DhwPlanner, "_dhw_raise_fits", counted):
        for seed in seeds:
            for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
                for n, nw in ((24, 3), (96, 24), (48, 10)):
                    plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                    calls["n"] = 0
                    run(plan, **kw)
                    joint += calls["n"] == 0
                    per_slot += calls["n"] > 0
    return joint, per_slot


SRC = Path(dhw_planner.__file__).read_text()
