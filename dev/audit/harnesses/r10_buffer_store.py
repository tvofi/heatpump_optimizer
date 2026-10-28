"""R10-BUFFER-STORE (#2500): does a 750 L manual-valve buffer change the plan?

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_buffer_store.py [plans|accuracy|reference|bench N] [--two-zone]

Synthetic installs only; no private data.

``plans`` (default; optional outdoor temperature after it, default 0 degC):
a 750 L manual-valve buffer against no buffer, each at a spread price day
and at its flat mean (the null: a flat day has no cheap window to store
for). Printed per arm: the plan's sha1, space kWh, the cheapest quarter's
share of space kWh, the planned tank's largest rise over its 30 degC start,
the plan's energy cost, and whether the buffer plan is byte-identical to the
no-buffer plan.

``accuracy``: ``AccuracyTracker.summary``'s ``power_ratio`` and
``cost_error_percent`` on three synthetic sample sets -- calibrated
(realised == predicted, the null), realised 1.4x predicted, and realised
predicted/1.4 (a plan booking 40 % more than is drawn) -- printing each
field's value, so the definitions' signs are read off the tree.

``reference``: the savings reference (``_compute_baseline_power``) on the
finder's cell -- 0.6 loss scale, 5 degC, a 24 degC tank, no hot water -- at
the flat price day, per zoning, 750 L behind a manual valve against no
buffer (the null: nothing stores there). Printed per arm: the reference's
kWh, its own tank's peak, the heat its tank refused at ``buffer_max_temp``,
and the published ``predicted_savings`` / ``savings_percentage``. Exits 1
when a valved reference refuses more than 0.01 kWh: heat bought for a cap.

``bench N``: wall time and peak RSS of ``optimize`` over N solves per arm,
each arm in its own process, on the owner's shape (750 L buffer behind a
manual valve, slab, hourly prices over a 24 h horizon at 15-minute steps,
seeded random prices per solve) and the null (flat prices, no buffer).
"""
from __future__ import annotations

import hashlib
import json
import resource
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

T0 = datetime(2026, 1, 12, 20, 0, tzinfo=timezone.utc)
STEPS = np.arange(96)
HOUR = (21.0 + STEPS / 4.0) % 24.0
SPREAD = 1.6 * np.interp(
    HOUR, [0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 23, 24],
    [0.65, 0.58, 0.62, 1.2, 1.35, 0.95, 0.9, 1.3, 1.5, 1.25, 0.85, 0.65],
)
FLAT = np.full(96, float(SPREAD.mean()))
TANK0 = 30.0
TWO_ZONE = "--two-zone" in sys.argv


def solve(buffer_l: float, prices: np.ndarray, outdoor: float):
    p = ThermalParameters(two_zone_enabled=TWO_ZONE)
    if buffer_l:
        p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
    p.min_electrical_power, p.max_electrical_power = 1.5, 5.0
    p.dhw_enabled = False
    opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig())
    return opt.optimize(inputs=solve_inputs(
        initial_state=ThermalState(
            room_temperature=20.0, upper_floor_temperature=20.0,
            lower_floor_temperature=20.0, slab_temperature=20.5,
            outdoor_temperature=outdoor, buffer_tank_temperature=TANK0,
            dhw_temperature=48.0,
        ),
        prices=prices, outdoor_temps=np.full(96, outdoor), start_time=T0,
    ))


def plans(outdoor: float) -> None:
    cheap = np.argsort(SPREAD, kind="stable")[:24]
    shas = {}
    for tag, prices in (("spread", SPREAD), ("flat", FLAT)):
        for buffer_l in (750.0, 0.0):
            r = solve(buffer_l, prices, outdoor)
            plan = np.asarray(r.power_schedule, float)
            share = float(plan[cheap].sum() / plan.sum()) if plan.sum() else 0.0
            tank = np.asarray(r.buffer_temp_trajectory or [TANK0], float)
            sha = hashlib.sha1(plan.tobytes()).hexdigest()[:12]
            shas[(tag, buffer_l)] = sha
            print(f"{tag} buffer {buffer_l:.0f} L: plan {sha} "
                  f"space_kwh {float(plan.sum()) / 4.0:.2f} cheap_quarter {share:.3f} "
                  f"tank_rise {tank.max() - TANK0:+.2f} "
                  f"cost {float(np.dot(plan, prices)) / 4.0:.3f}")
        print(f"{tag}: buffer plan identical to no-buffer "
              f"{shas[(tag, 750.0)] == shas[(tag, 0.0)]}")


def accuracy() -> None:
    from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker

    for tag, factor in (("calibrated", 1.0), ("realised_1.4x", 1.4),
                        ("plan_overbooks_40pct", 1 / 1.4)):
        tracker = AccuracyTracker()
        for k in range(48):
            pred = 1.5 + (k % 5) * 0.5
            tracker.record(AccuracySample(
                when=T0 + timedelta(minutes=15 * k),
                predicted_temp=21.0, actual_temp=21.0,
                predicted_power_kw=pred, actual_power_kw=pred * factor,
                predicted_cost=pred * 0.25, actual_cost=pred * factor * 0.25,
            ))
        s = tracker.summary()
        print(f"accuracy {tag}: power_ratio {s['power_ratio']} "
              f"cost_error_percent {s['cost_error_percent']}")


def reference() -> int:
    bad = 0
    for two_zone in (False, True):
        for buffer_l in (750.0, 0.0):
            p = ThermalParameters(two_zone_enabled=two_zone)
            if buffer_l:
                p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
            p.min_electrical_power, p.max_electrical_power = 1.5, 5.0
            p.dhw_enabled, p.house_heat_loss_scale = False, 0.6
            model = ThermalModel(p)
            opt = HeatPumpOptimizer(model, OptimizationConfig())
            seen = {"on": False, "tank": [], "refused": 0.0}
            real_ref, real_step = opt._compute_baseline_power, model.simulate_step

            def ref(*a, **k):
                seen["on"] = True
                try:
                    return real_ref(*a, **k)
                finally:
                    seen["on"] = False

            def step(*a, **k):
                s = real_step(*a, **k)
                if seen["on"]:
                    seen["tank"].append(s.buffer_tank_temperature)
                    seen["refused"] += model._step_buffer_refused * 0.25
                return s

            opt._compute_baseline_power, model.simulate_step = ref, step
            r = opt.optimize(inputs=solve_inputs(
                initial_state=ThermalState(
                    room_temperature=20.0, upper_floor_temperature=20.0,
                    lower_floor_temperature=20.0, slab_temperature=20.5,
                    outdoor_temperature=5.0, buffer_tank_temperature=24.0,
                    dhw_temperature=48.0,
                ),
                prices=FLAT, outdoor_temps=np.full(96, 5.0), start_time=T0,
            ))
            ref_kwh = float(np.sum(r.baseline_power_schedule)) / 4.0
            bad += int(buffer_l > 0 and seen["refused"] > 0.01)
            print(f"reference {'two' if two_zone else 'single'}-zone flat "
                  f"buffer {buffer_l:.0f} L: reference_kwh {ref_kwh:.2f} "
                  f"reference_tank_peak {max(seen['tank']):.1f} "
                  f"reference_refused_kwh {seen['refused']:.2f} "
                  f"plan_kwh {sum(r.power_schedule) / 4.0:.2f} "
                  f"savings {r.predicted_savings:.2f} pct {r.savings_percentage:.1f}")
    print(f"reference: {bad} valved arm(s) refuse heat the reference paid for")
    return 1 if bad else 0


ARMS = {
    "owner_buffer_spread": (750.0, "spread"),
    "null_flat_nobuffer": (0.0, "flat"),
}


def bench_arm(arm: str, n: int) -> dict:
    buffer_l, kind = ARMS[arm]
    rng = np.random.default_rng(2500)
    times = []
    for _ in range(n):
        hourly = rng.uniform(0.4, 3.0, size=24)
        prices = np.repeat(hourly, 4) if kind == "spread" else FLAT
        outdoor = float(rng.uniform(-15.0, 8.0))
        t = time.perf_counter()
        solve(buffer_l, prices, outdoor)
        times.append(time.perf_counter() - t)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {"arm": arm, "n": n, "median_s": round(float(np.median(times)), 3),
            "max_s": round(max(times), 3), "peak_rss": rss}


def bench(n: int) -> None:
    for arm in ARMS:
        argv = [sys.executable, str(Path(__file__).resolve()), "--arm", arm, str(n)]
        if TWO_ZONE:
            argv.append("--two-zone")
        out = subprocess.run(argv, capture_output=True, text=True, check=True).stdout
        print("bench", out.strip(), "two_zone" if TWO_ZONE else "single_zone")


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--two-zone"]
    if args[:1] == ["--arm"]:
        print(json.dumps(bench_arm(args[1], int(args[2]))))
    elif args[:1] == ["accuracy"]:
        accuracy()
    elif args[:1] == ["reference"]:
        return reference()
    elif args[:1] == ["bench"]:
        bench(int(args[1]))
    else:
        rest = args[1:] if args[:1] == ["plans"] else args
        plans(float(rest[0]) if rest else 0.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
