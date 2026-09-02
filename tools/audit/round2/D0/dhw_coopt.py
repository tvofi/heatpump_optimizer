"""D0 decomposition: does a second DHW <-> space pass, or the terminal credit, move the plan?

Metric A (co-optimization): per DHW-enabled cell, the objective after
production's single _co_optimize pass (score1) and after one MORE pass run by
this harness on its output (score2) with the same solve_space closure and the
same adoption rule; pass2_gain = score1 - score2 (SEK on the objective).
Also counted: cells where pass 1 triggered (pinned steps > 0), re-solved the
space stage (a second _multi_start_minimize call) and was adopted. Hook: heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize.

Metric B (terminal credit): the same cells solved with
HeatPumpOptimizer._terminal_cost replaced by a zero closure; reports the
end-of-horizon room temperature and the last-2h energy with and without the
credit (the docstring's claim: without it the tail is dumped).

Command:
    PYTHONPATH=tests/hastub python tools/audit/round2/D0/dhw_coopt.py
Perturbation: D0_REFILL_HOURS=0.5 sets optimizer._DHW_REFILL_WINDOW_HOURS
(expected: pass-1 replans UP or DOWN; pass2_gain must move); for metric B the
perturbation is the harness's own zero closure (tail energy DOWN, end room DOWN).

Expected on baseline c398fc8: pass2_gain_max small (<= 0.05 SEK) if the single
pass is sufficient; terminal_end_room_drop > 0. Counts exact; CPU provisional.
Writes nothing outside stdout.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import sys
from unittest import mock

sys.path.insert(0, "tools/audit/round2/D0")

import numpy as np  # noqa: E402

import d0lib as L  # noqa: E402

CELLS = [
    (p, w, tz) for p in ("winter_typical", "winter_extreme", "winter_moderate",
                         "winter_narrow", "shoulder", "summer_typical",
                         "summer_negative", "flat")
    for w in ("winter_cold",) for tz in (False, True)
] + [("winter_typical", "winter_mild", True), ("shoulder", "shoulder", True),
     ("winter_typical", "winter_mild", False), ("shoulder", "shoulder", False)]


def main() -> int:
    refill = os.environ.get("D0_REFILL_HOURS")
    patches = []
    if refill:
        patches.append(mock.patch.object(L.opt_mod, "_DHW_REFILL_WINDOW_HOURS", float(refill)))
        patches[-1].start()

    rows = []
    clock = L.CpuClock()
    real_co = L.HeatPumpOptimizer._co_optimize
    for price, wx, tz in CELLS:
        cell = L.build_cell(price, wx, two_zone=tz, dhw=True)
        log = {}

        def co_wrapper(opt_self, h, *, dhw_plan, space_power, dhw_power, status,
                       best_score, solve_space, p_max):
            headroom = np.maximum(0.0, p_max - dhw_power)
            pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)
            log["pinned"] = int(np.sum(pinned))
            log["score0"] = float(best_score)
            n0 = len(rec.calls)
            s1, d1, st1 = real_co(opt_self, h, dhw_plan=dhw_plan, space_power=space_power,
                                  dhw_power=dhw_power, status=status, best_score=best_score,
                                  solve_space=solve_space, p_max=p_max)
            obj = rec.calls[-1].objective
            score1 = float(obj(s1, d1))
            log["solved1"] = len(rec.calls) - n0
            log["replanned1"] = bool(not np.allclose(d1, dhw_power, atol=1e-4))
            log["score1"] = score1
            n1 = len(rec.calls)
            s2, d2, st2 = real_co(opt_self, h, dhw_plan=dict(dhw_plan), space_power=s1,
                                  dhw_power=d1, status=st1, best_score=score1,
                                  solve_space=solve_space, p_max=p_max)
            log["solved2"] = len(rec.calls) - n1
            log["replanned2"] = bool(not np.allclose(d2, d1, atol=1e-4))
            log["score2"] = float(obj(s2, d2))
            return s1, d1, st1

        with clock:
            with L.Recorder() as rec, mock.patch.object(L.HeatPumpOptimizer, "_co_optimize", co_wrapper):
                res = cell.solve()
            # Metric B: zero terminal credit.
            def zero_terminal(opt_self, prices, outdoor, solar_gains=None):
                return lambda *a, **k: 0.0
            with mock.patch.object(L.HeatPumpOptimizer, "_terminal_cost", zero_terminal):
                res0 = cell.solve()
        traj = np.asarray(res.upper_temp_trajectory if tz else res.room_temp_trajectory)
        traj0 = np.asarray(res0.upper_temp_trajectory if tz else res0.room_temp_trajectory)
        pw = np.asarray(res.power_schedule); pw0 = np.asarray(res0.power_schedule)
        row = {
            "cell": cell.name, "n_calls": len(rec.calls),
            "pinned": log.get("pinned", 0), "score0": log.get("score0", float("nan")),
            "score1": log.get("score1", float("nan")), "score2": log.get("score2", float("nan")),
            "replanned1": log.get("replanned1", False), "replanned2": log.get("replanned2", False),
            "solved1": log.get("solved1", 0), "solved2": log.get("solved2", 0),
            "adopted1": len(rec.calls) >= 2 and log.get("score1", 0) < log.get("score0", 0) - 1e-9,
            "end_room": float(traj[-1]), "end_room_noterm": float(traj0[-1]),
            "tail_kwh": float(np.sum(pw[-8:]) * 0.25), "tail_kwh_noterm": float(np.sum(pw0[-8:]) * 0.25),
            "energy_cost": float(res.predicted_cost), "energy_cost_noterm": float(res0.predicted_cost),
        }
        row["pass1_gain"] = row["score0"] - row["score1"]
        row["pass2_gain"] = row["score1"] - row["score2"]
        rows.append(row)
        print(f"  {cell.name}: calls {row['n_calls']} pinned {row['pinned']:3d} score0 {row['score0']:.4f} "
              f"pass1 {row['pass1_gain']:+.4f} (solved {row['solved1']} adopted {row['replanned1']}) pass2 {row['pass2_gain']:+.4f} "
              f"(solved {row['solved2']} adopted {row['replanned2']}) | terminal: end_room {row['end_room']:.3f} -> {row['end_room_noterm']:.3f} "
              f"tail_kwh {row['tail_kwh']:.2f} -> {row['tail_kwh_noterm']:.2f} cost {row['energy_cost']:.2f} -> {row['energy_cost_noterm']:.2f}")
    for p in patches:
        p.stop()
    p1 = np.array([r["pass1_gain"] for r in rows]); p2 = np.array([r["pass2_gain"] for r in rows])
    print()
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT coopt_triggered={sum(1 for r in rows if r['pinned'] > 0)} count")
    print(f"RESULT coopt_resolved_pass1={sum(1 for r in rows if r['solved1'] > 0)} count")
    print(f"RESULT coopt_adopted_pass1={sum(1 for r in rows if r['pass1_gain'] > 1e-9)} count")
    print(f"RESULT coopt_resolved_pass2={sum(1 for r in rows if r['solved2'] > 0)} count")
    print(f"RESULT coopt_adopted_pass2={sum(1 for r in rows if r['pass2_gain'] > 1e-9)} count")
    print(f"RESULT pass1_gain_sum={p1.sum():.4f} SEK")
    print(f"RESULT pass2_gain_sum={p2.sum():.4f} SEK")
    print(f"RESULT pass2_gain_max={p2.max():.4f} SEK")
    drop = np.array([r["end_room"] - r["end_room_noterm"] for r in rows])
    tail = np.array([r["tail_kwh"] - r["tail_kwh_noterm"] for r in rows])
    print(f"RESULT terminal_end_room_drop_mean={drop.mean():.3f} K")
    print(f"RESULT terminal_end_room_drop_min={drop.min():.3f} K")
    print(f"RESULT terminal_tail_kwh_delta_mean={tail.mean():.3f} kWh")
    print(f"RESULT terminal_cells_tail_dumped={int(np.sum(drop > 0.05))} count")
    print("RESULT provisional=true flag")
    L.footer(clock)
    return 0


if __name__ == "__main__":
    sys.exit(main())
