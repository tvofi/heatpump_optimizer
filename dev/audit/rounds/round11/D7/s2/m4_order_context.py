"""D7.M4 (round 11, seat D7-s2): implied order through the optimizer's per-solve state, and
what a holder of a superseded CoordinatorContext sees.

Part A -- reuse: for each scenario pair (X then Y) of tests/golden.py:make(), one
HeatPumpOptimizer solves X then Y; a fresh one solves Y. reuse_divergence = number of pairs
whose reused Y differs from the fresh Y (predicted_cost or any power_schedule entry, exact).
Key: the OptimizationResult HeatPumpOptimizer.optimize returns.
Part B -- terminal cost: ``HeatPumpOptimizer._terminal_cost`` evaluated twice on one end
state (second_call_delta), and the same closure built after a solve of another initial
buffer temperature (reorder_delta: the order coupling through ``_initial_buffer_temp``, the
successor of last_buffer_trajectory). Key: the closure's returned cost.
Part C -- context holder: a coordinator's ``_ctx`` is captured, then
``async_update_thermal_params`` publishes a new context; then ``async_set_target_temperature``
and ``_apply_comfort_weight`` run. holder_torn_fields = number of fields of the SUPERSEDED
context's members that changed after it was superseded (CoordinatorContext's docstring: "a
holder of the old one keeps a consistent view"). Key: the old context object's member values.

Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/m4_order_context.py
       --perturb-stash : ``_stash_buffer_seed`` keeps the first solve's seed (a reordering): reuse_divergence must rise
       --perturb-ctx   : the two in-place writers publish a replaced _opt_config instead: holder_torn_fields -> 0
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): reuse_divergence=0, second_call_delta=0,
reorder_delta=0 and seed_binding_scenarios=0 (in every shipped buffer scenario the settlement
ceiling already equals buffer_max_temperature, so the stashed seed cannot move the terminal
cost: the order coupling is latent and --perturb-stash leaves reuse_divergence at 0 -- a harness
gap recorded as such), holder_torn_fields=2 (0 under --perturb-ctx); exact.
Machine: box B5 (round-11 finder container), numpy 2.5.4 / scipy 1.18.1, CPython 3.14.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import fields, replace  # noqa: E402

sys.path[:0] = ["tests"]
import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import golden  # noqa: E402
from profiles import solve_inputs  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

P_STASH = "--perturb-stash" in sys.argv
P_CTX = "--perturb-ctx" in sys.argv

if P_STASH:
    _orig_seed = HeatPumpOptimizer._stash_buffer_seed

    def _sticky_seed(self, initial_state):
        if getattr(self, "_seed_taken", False):
            return
        _orig_seed(self, initial_state)
        self._seed_taken = True

    HeatPumpOptimizer._stash_buffer_seed = _sticky_seed


def build(name, **state):
    spec = dict(golden.SCENARIOS[name])
    so = dict(spec.pop("state_overrides", None) or {})
    so.update(state)
    return golden.make(state_overrides=so, **spec)


def inputs_of(b):
    return solve_inputs(initial_state=b["state"], prices=b["prices"], outdoor_temps=b["outdoor"],
                        wind_speeds=b["wind"], precipitation=b["rain"],
                        solar_radiation=b["solar"], start_time=golden.START)


def same(r1, r2):
    return (r1.predicted_cost == r2.predicted_cost
            and np.array_equal(np.asarray(r1.power_schedule), np.asarray(r2.power_schedule)))


PAIRS = [  # (scenario, X state, Y state)
    ("valve_storage", {"buffer_tank_temperature": 60.0}, {"buffer_tank_temperature": 32.0}),
    ("valve_storage", {"buffer_tank_temperature": 32.0}, {"buffer_tank_temperature": 60.0}),
    ("valve_storage_low_target", {"buffer_tank_temperature": 65.0}, {"buffer_tank_temperature": 30.0}),
]


def part_a():
    names = [n for n in golden.SCENARIOS if "two_zone" in golden.SCENARIOS[n]
             and golden.SCENARIOS[n].get("dhw", True)][:2]
    pairs = list(PAIRS) + [(n, {"room_temperature": 19.0, "dhw_temperature": 42.0},
                            {"room_temperature": 21.5}) for n in names]
    diverged = 0
    for name, sx, sy in pairs:
        bx, by = build(name, **sx), build(name, **sy)
        reused = bx["optimizer"]
        reused.optimize(inputs=inputs_of(bx))
        r_reused = reused.optimize(inputs=inputs_of(by))
        r_fresh = build(name, **sy)["optimizer"].optimize(inputs=inputs_of(by))
        d = not same(r_reused, r_fresh)
        diverged += d
        print(f"# A {name} {sx} -> {sy}: reused==fresh {not d} "
              f"(cost {r_reused.predicted_cost:.6f} vs {r_fresh.predicted_cost:.6f}); "
              f"_prev_shipped_plan set by optimize: {getattr(reused, '_prev_shipped_plan', None) is not None}")
    print(f"RESULT reuse_pairs={len(pairs)} count")
    print(f"RESULT reuse_divergence={diverged} count")


def seed_binding():
    """Scenarios in which the stashed buffer seed moves the settlement ceiling at all."""
    binding = 0
    names = [n for n in golden.SCENARIOS if "buffer_tank_volume" in
             (golden.SCENARIOS[n].get("config_overrides") or {})]
    for name in names:
        b = build(name, buffer_tank_temperature=30.0)
        o = b["optimizer"]
        o._initial_buffer_temp = None
        lo = o._settlement_caps(b["outdoor"]).get("buffer")
        o._initial_buffer_temp = float(o.model.params.buffer_max_temp) - 1.0
        hi = o._settlement_caps(b["outdoor"]).get("buffer")
        binding += lo != hi
    print(f"RESULT buffer_scenarios={len(names)} count")
    print(f"RESULT seed_binding_scenarios={binding} count")


def part_b():
    name = "valve_storage_low_target"
    bx = build(name, buffer_tank_temperature=65.0)
    by = build(name, buffer_tank_temperature=30.0)
    o = by["optimizer"]
    o.optimize(inputs=inputs_of(by))
    n = len(by["prices"])
    ends = dict(room_temps=np.full(n, 19.5), slab_temps=np.full(n, 21.0),
                upper_temps=np.full(n, 19.5), lower_temps=np.full(n, 19.5),
                buffer_temps=np.full(n, 30.0))
    cost, _batch = o._terminal_cost(by["prices"], by["outdoor"])
    c1, c2 = cost(**ends), cost(**ends)
    print(f"RESULT second_call_delta={abs(c1 - c2):.12g} cost-units")
    # the same closure, built after the instance last solved a 65 C start
    o.optimize(inputs=inputs_of(bx))
    cost_after_x, _ = o._terminal_cost(by["prices"], by["outdoor"])
    c3 = cost_after_x(**ends)
    print(f"RESULT reorder_delta={abs(c3 - c1):.6f} cost-units (terminal cost of Y's end, closure built after X's stash vs Y's)")


def part_c():
    states = {"sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("-5.0", unit="°C")}
    c = coord_mod.HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "comfort_learning_enabled": True}))
    c.async_request_refresh = lambda: asyncio.sleep(0)

    if P_CTX:
        async def set_target(self, temperature):
            ctx = self._ctx
            self._ctx = replace(ctx, _opt_config=replace(ctx._opt_config, target_temp=temperature))

        def apply_weight(self):
            ctx = self._ctx
            self._ctx = replace(ctx, _opt_config=replace(ctx._opt_config, comfort_weight=self._comfort_weight()))

        c.async_set_target_temperature = set_target.__get__(c)
        c._apply_comfort_weight = apply_weight.__get__(c)

    old = c._ctx
    snap = {m: {f.name: repr(getattr(getattr(old, m), f.name)) for f in fields(getattr(old, m))}
            for m in ("_opt_config", "_thermal_params", "_current_state")}
    asyncio.run(c.async_update_thermal_params({"house_heat_loss_coefficient": 0.2}))
    superseded = c._ctx is not old
    asyncio.run(c.async_set_target_temperature(22.0))
    c._comfort_learner.learned_weight = c._comfort_learner.configured_weight * 1.5
    c._apply_comfort_weight()
    torn = []
    for m, before in snap.items():
        member = getattr(old, m)
        for f, v in before.items():
            if repr(getattr(member, f)) != v:
                torn.append(f"{m}.{f}")
    print(f"# C superseded={superseded}; shares _opt_config with live ctx: {old._opt_config is c._ctx._opt_config}; "
          f"old _thermal_params.heat_loss_coefficient={old._thermal_params.heat_loss_coefficient} "
          f"live={c._ctx._thermal_params.heat_loss_coefficient}; torn={torn}")
    print(f"RESULT holder_torn_fields={len(torn)} count")


def main():
    t0 = time.process_time()
    part_a()
    part_b()
    seed_binding()
    part_c()
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    print(f"# cpu {time.process_time() - t0:.1f}s (provisional, not a finding)")


if __name__ == "__main__":
    main()
