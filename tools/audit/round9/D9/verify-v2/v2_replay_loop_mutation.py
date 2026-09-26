"""V2 (independent) check of D9-s2-02: can the nightly replay cost budget
(tests/replay.py:cost_offenders, COST_BUDGETS["synthetic-dhw-only.json"])
see a ~2x of the coordinator cycle's LOOP-THREAD work caused by a one-line
PRODUCTION edit, rather than by an injected spin?

Mutation (in memory, one production constant): topology._ADVISOR_REPLAY_STEPS
48 -> 48*K (default K=4). The #1269 advisor runs on the loop thread inside the
plan sensors' extra_state_attributes, so this multiplies loop work only; the
solve (an executor job) is untouched.
Metric (own definition): (a) offenders tests/replay.py:cost_offenders returns
for the mutated replay; (b) loop-thread CPU per cycle, mutated over plain,
where loop-thread CPU = thread CPU of coordinator._async_update_data minus
the thread CPU of the jobs it hands to hass.async_add_executor_job, plus the
thread CPU of replay.sweep (one read of every entity) -- hooked here, not the
finder's _rig; (c) replay's own cycle cpu_ratio, mutated over plain.
Each arm runs in its own interpreter.
Count key: the offender list the gate's own function returns.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_replay_loop_mutation.py [--k 4]
Perturbation: --k 16 / --k 32 (loop work many-fold): cycle cpu_ratio must go
UP (observed 2.41 -> 3.19 at k16, 2.68 -> 3.55 at k32, loop x3.23 / x5.59) --
and offenders stayed 0 at both, under the 3.576 budget. The positive control
that the check can fire is replay's own inject="cpu" arm (the finder's
m2_loop_blind.py "cpu" arm: offenders 1).
Observed k4 (baseline 1936d5ca, this box): loop x1.45, cycle x1.01, offenders 0.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import json
import subprocess
import time
from pathlib import Path

MARK = "<<<v2-arm>>>"


def arm(k: int) -> dict:
    import replay
    import harness
    from heatpump_optimizer import topology
    from heatpump_optimizer import coordinator as cm
    if k != 1:
        topology._ADVISOR_REPLAY_STEPS = 48 * k
    acc = {"upd": [], "exec": 0.0, "sweep": []}
    real_job = harness.FakeHass.async_add_executor_job

    async def job(self, func, *a):
        t0 = time.thread_time()
        try:
            return await real_job(self, func, *a)
        finally:
            acc["exec"] += time.thread_time() - t0
    harness.FakeHass.async_add_executor_job = job
    real_upd = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def upd(self):
        e0, t0 = acc["exec"], time.thread_time()
        try:
            return await real_upd(self)
        finally:
            acc["upd"].append((time.thread_time() - t0) - (acc["exec"] - e0))
    cm.HeatPumpOptimizerCoordinator._async_update_data = upd
    real_sweep = replay.sweep

    def sweep(*a, **kw):
        t0 = time.thread_time()
        try:
            return real_sweep(*a, **kw)
        finally:
            acc["sweep"].append(time.thread_time() - t0)
    replay.sweep = sweep
    out = replay.run_fixture(Path("tests/replay/synthetic-dhw-only.json"), None)
    fig = {kk: out["cost"][kk] for kk in ("cpu_ratio", "peak_kib")}
    offenders = replay.cost_offenders(fig, replay.COST_BUDGETS["synthetic-dhw-only.json"])
    n = min(len(acc["upd"]), len(acc["sweep"]))
    loop = [acc["upd"][i] + acc["sweep"][i] for i in range(2, n, 2)]  # untraced cycles, as replay times them
    loop.sort()
    return {"cpu_ratio": fig["cpu_ratio"], "offenders": offenders,
            "loop_ms_median": 1000 * loop[len(loop) // 2],
            "budget": replay.COST_BUDGETS["synthetic-dhw-only.json"]["cpu_ratio"],
            "ref_ms": out["cost"]["ref_ms"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--child", type=int, default=None)
    args = ap.parse_args()
    if args.child is not None:
        print(MARK + json.dumps(arm(args.child)))
        return
    res = {}
    for k in (1, args.k):
        p = subprocess.run([sys.executable, __file__, "--child", str(k)],
                           capture_output=True, text=True, env=os.environ.copy())
        line = [l for l in p.stdout.splitlines() if l.startswith(MARK)]
        if not line:
            print(p.stdout[-2000:], p.stderr[-3000:])
            raise SystemExit(1)
        res[k] = json.loads(line[0][len(MARK):])
    base, mut = res[1], res[args.k]
    V.result("plain.cpu_ratio", base["cpu_ratio"], "ref_solves")
    V.result("plain.offenders", len([o for o in base["offenders"] if o.startswith("cpu")]), "count")
    V.result(f"k{args.k}.cpu_ratio", mut["cpu_ratio"], "ref_solves")
    V.result(f"k{args.k}.offenders", len([o for o in mut["offenders"] if o.startswith("cpu")]), "count (exact)")
    V.result("cpu_ratio_budget", base["budget"], "ref_solves")
    V.result("plain.loop_thread_ms_per_cycle", round(base["loop_ms_median"], 3), "ms (provisional)")
    V.result(f"k{args.k}.loop_thread_ms_per_cycle", round(mut["loop_ms_median"], 3), "ms (provisional)")
    V.result(f"k{args.k}.loop_thread_x", round(mut["loop_ms_median"] / base["loop_ms_median"], 3), "ratio")
    V.result("plain.ref_ms", base["ref_ms"], "ms (provisional)")
    V.result(f"k{args.k}.ref_ms", mut["ref_ms"], "ms (provisional)")
    V.result(f"k{args.k}.cycle_cpu_ratio_x", round(mut["cpu_ratio"] / base["cpu_ratio"], 3), "ratio")
    V.trailer()


if __name__ == "__main__":
    main()
