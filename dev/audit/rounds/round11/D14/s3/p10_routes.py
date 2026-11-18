#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): P10 detector over replayed days.

Metric: CPU kernels called in the coordinator's own interpreter outside
``process_worker.run_worker`` over a replayed fixture, by route (``loop`` /
``executor``), counted once at the outermost kernel and only when a
``heatpump_optimizer`` frame is on the stack. Count key: the route the
production call actually ran on (thread-local flags set by
``process_worker:run_worker`` and ``FakeHass.async_add_executor_job``), never
an attribute of the input.

The kernel set is WIDER than ``tests/replay.py:kernel_routes`` (which counts
``ThermalModel.simulate_*`` and four sysid entry points): it adds every
numeric library call the package makes (``numpy.linalg.solve/lstsq/inv/
cholesky``, ``scipy.optimize.minimize`` as bound in ``optimizer``,
``scipy.optimize.linprog`` as bound in ``dhw_planner``) and the package's own
replay/simulation helpers outside ``ThermalModel`` (``wood_fuel.
simulate_wood_slots``, ``sysid._simulate_slab_path``,
``topology._advisor_replay``). A seam is
``<route> <file:function> <kernel>``; every seam the day reaches is printed.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/p10_routes.py
    ... --arm owner-learner            # one arm (see ARMS)
    ... --tree /path/to/old/export     # replay a pre-fix tree's own coordinator
    ... --reintroduce                  # perturbation: _await_off_loop runs fn inline
    P10_PERTURB_WHATIF=1 ... --arm owner-1h   # perturbation: whatif.schedule_days -> None

Expected at 92d38ecb6 (box B7, 4 vCPU): loop=0 executor=0 on every arm (a
non-finding: the barrier holds on both fixtures); --reintroduce: loop > 0
(up); at a pre-F1.7 tree (3dfebc1690): loop > 0 (topology._advisor_replay).
Tolerance: exact (counts).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
MARK = "<<<p10>>>"
ARMS = {
    # name: (fixture, hours or None for the whole window, open learner gates)
    "synthetic": ("synthetic-dhw-only.json", 6.0, False),
    "synthetic-learner": ("synthetic-dhw-only.json", 6.0, True),
    "owner": ("owner-2026-10-30-away.json", 2.0, False),
    "owner-1h": ("owner-2026-10-30-away.json", 1.0, False),
    "owner-learner": ("owner-2026-10-30-away.json", 2.0, True),
    # The day, then what a user does beside it: the config-entry diagnostics
    # download, every button press, every options page rendered.
    "synthetic-surfaces": ("synthetic-dhw-only.json", 2.0, False),
}


def _arm(tree: Path, arm: str, reintroduce: bool) -> dict:
    for p in (tree / "tests" / "hastub", tree / "tests", tree / "custom_components",
              tree / "tools" / "replay"):
        sys.path.insert(0, str(p))
    import replay  # the tree under test's own lane
    import harness
    import numpy as np
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import process_worker as pw
    from heatpump_optimizer import thermal_model as tm
    import importlib

    tl = threading.local()
    counts: Counter = Counter()
    sites: Counter = Counter()
    worker_sites: Counter = Counter()
    stacks: Counter = Counter()
    off_cpu: Counter = Counter()  # thread CPU of the outermost off-worker kernel calls, ms

    def pkg_frames(start):
        out, f = [], start
        while f is not None:
            fn = f.f_code.co_filename.replace("\\", "/")
            if "/heatpump_optimizer/" in fn:
                out.append(f"{Path(fn).name}:{f.f_code.co_name}")
            f = f.f_back
        return out

    def counted(real, label):
        def wrap(*a, **k):
            if not getattr(tl, "inside", 0):
                frames = pkg_frames(sys._getframe(1))
                if frames:
                    route = ("worker" if getattr(tl, "worker", 0)
                             else "executor" if getattr(tl, "executor", 0) else "loop")
                    counts[route] += 1
                    counts[f"{route}:{label}"] += 1
                    if route == "worker":
                        worker_sites.update(set(frames))
                    else:
                        caller = next((fr for fr in frames
                                       if not fr.startswith(("thermal_model.py", "sysid.py"))),
                                      frames[0])
                        sites[f"{route} {caller} {label}"] += 1
                        stacks[f"{route} " + " <- ".join(frames[:7])] += 1
                        began = time.thread_time()
                        tl.inside = getattr(tl, "inside", 0) + 1
                        try:
                            return real(*a, **k)
                        finally:
                            tl.inside -= 1
                            off_cpu[route] += (time.thread_time() - began) * 1000.0
            tl.inside = getattr(tl, "inside", 0) + 1
            try:
                return real(*a, **k)
            finally:
                tl.inside -= 1
        wrap.__wrapped__ = real
        return wrap

    def flagged(name, real):
        def wrap(*a, **k):
            setattr(tl, name, getattr(tl, name, 0) + 1)
            try:
                return real(*a, **k)
            finally:
                setattr(tl, name, getattr(tl, name) - 1)
        return wrap

    # The model kernels tests/replay.py counts ...
    for n in dir(tm.ThermalModel):
        if n.startswith("simulate_"):
            setattr(tm.ThermalModel, n, counted(getattr(tm.ThermalModel, n), f"ThermalModel.{n}"))
    try:
        from heatpump_optimizer import sysid
        for n in ("identify", "identify_slab", "_size_step_power", "_unadoptable"):
            if hasattr(sysid.SystemIdentification, n):
                setattr(sysid.SystemIdentification, n,
                        counted(getattr(sysid.SystemIdentification, n), f"sysid.{n}"))
        if hasattr(sysid, "_simulate_slab_path"):
            sysid._simulate_slab_path = counted(sysid._simulate_slab_path, "sysid._simulate_slab_path")
    except ImportError:
        pass
    # ... and the package's other replay/simulation helpers, where they exist.
    for mod, attr in (("wood_fuel", "simulate_wood_slots"), ("topology", "_advisor_replay")):
        try:
            m = importlib.import_module(f"heatpump_optimizer.{mod}")
        except ImportError:
            continue
        if hasattr(m, attr):
            setattr(m, attr, counted(getattr(m, attr), f"{mod}.{attr}"))
    # (``accuracy.AccuracyTracker.replay`` was in the first cut of this list and
    # is NOT a kernel: a dict lookup of yesterday's promise, 12 loop calls per
    # 6 h on the synthetic day; dropped as a false positive of name matching.)
    # The numeric library kernels, at every binding the package uses.
    for n in ("solve", "lstsq", "inv", "cholesky"):
        setattr(np.linalg, n, counted(getattr(np.linalg, n), f"np.linalg.{n}"))
    for mod, attr in (("optimizer", "minimize"), ("dhw_planner", "linprog")):
        try:
            m = importlib.import_module(f"heatpump_optimizer.{mod}")
        except ImportError:
            continue
        if hasattr(m, attr):
            setattr(m, attr, counted(getattr(m, attr), f"scipy.optimize.{attr}"))

    pw.run_worker = flagged("worker", pw.run_worker)
    real_ex = harness.FakeHass.async_add_executor_job

    async def executor(self, func, *args):
        tl.executor = getattr(tl, "executor", 0) + 1
        try:
            return await real_ex(self, func, *args)
        finally:
            tl.executor -= 1

    harness.FakeHass.async_add_executor_job = executor

    fixture, hours, learner = ARMS[arm]
    if learner:
        cm.HeatPumpOptimizerCoordinator._learning_frozen = lambda self, *a, **k: None
        if hasattr(cm.HeatPumpOptimizerCoordinator, "_interval_space_power"):
            cm.HeatPumpOptimizerCoordinator._interval_space_power = lambda self: 3.0
    if os.environ.get("P10_PERTURB_WHATIF"):
        # The seam's own perturbation: the what-if's schedule pricing returns
        # "no schedule change" without pricing a reference day.
        from heatpump_optimizer import whatif
        whatif.schedule_days = lambda live, sim: None
    if reintroduce:
        # The one-line re-introduction: the P10 helper runs its job inline.
        async def inline(hass, fn, *args):
            return fn(*args)
        cm._await_off_loop = inline

    src = json.loads((tree / "tests" / "replay" / fixture).read_text()) \
        if (tree / "tests" / "replay" / fixture).exists() \
        else json.loads((ROOT / "tests" / "replay" / fixture).read_text())
    if hours is not None:
        start = datetime.fromisoformat(src["window"]["start"])
        src["window"]["end"] = (start + timedelta(hours=hours)).isoformat()
    held = {}
    real_init = cm.HeatPumpOptimizerCoordinator.__init__

    def init(self, hass, entry, *a, **kw):
        real_init(self, hass, entry, *a, **kw)
        held.update(hass=hass, entry=entry, coord=self)
    cm.HeatPumpOptimizerCoordinator.__init__ = init
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "day.json"
        path.write_text(json.dumps(src))
        with contextlib.redirect_stdout(io.StringIO()):
            run = replay.run_fixture(path, 30)
    surface_errors = []
    if arm.endswith("-surfaces"):
        import asyncio
        hass, entry = held["hass"], held["entry"]
        entry.runtime_data = held["coord"]
        mark = dict(counts)

        def delta(label):
            for route in ("loop", "executor", "worker"):
                n = counts.get(route, 0) - mark.get(route, 0)
                if n:
                    counts[f"surface:{label}:{route}"] = n
            mark.clear()
            mark.update(counts)
        try:
            from heatpump_optimizer import diagnostics
            asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
        except Exception as err:  # noqa: BLE001
            surface_errors.append(f"diagnostics: {type(err).__name__}: {err}")
        delta("diagnostics")
        from heatpump_optimizer import button
        buttons = []
        asyncio.run(button.async_setup_entry(hass, entry, buttons.extend))
        for b in buttons:
            name = type(b).__name__
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    asyncio.run(b.async_press())
            except Exception as err:  # noqa: BLE001
                surface_errors.append(f"{name}: {type(err).__name__}: {err}")
            delta(f"button:{name}")
        from heatpump_optimizer.config_flow import HeatPumpOptimizerOptionsFlow as Flow
        f = Flow(entry)
        f.hass = hass
        for step in Flow._MENU_LABELS:
            try:
                asyncio.run(getattr(f, f"async_step_{step}")())
            except Exception as err:  # noqa: BLE001
                surface_errors.append(f"options {step}: {type(err).__name__}: {err}")
            delta(f"options:{step}")
    return {"arm": arm, "cycles": run["cycles"], "cycle_offenders": run["counts"].get("cycle"),
            "surface_errors": surface_errors[:20],
            "counts": dict(counts), "sites": dict(sites.most_common()),
            "stacks": dict(stacks.most_common(6)),
            "off_cpu_ms": {k: round(v, 1) for k, v in off_cpu.items()},
            "worker_sites": {k: v for k, v in worker_sites.items()
                             if k.startswith("coordinator.py:_async_learn")
                             or k.endswith(("_replay_interval", "_replay_fabric",
                                            "estimate_recovery_hours", "_with_sensor_advisor"))}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--tree", type=Path, default=ROOT)
    ap.add_argument("--reintroduce", action="store_true")
    ap.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.child:
        print(MARK + json.dumps(_arm(a.tree.resolve(), a.arm, a.reintroduce)))
        return 0
    arms = [a.arm] if a.arm else list(ARMS)
    tz = "Europe/Stockholm"
    t0, c0, tc0 = time.monotonic(), time.process_time(), time.thread_time()
    procs = {}
    for arm in arms:
        env = {**os.environ, "HASTUB_TZ": tz,
               "PYTHONPATH": str(a.tree.resolve() / "tests" / "hastub")}
        cmd = [sys.executable, __file__, "--child", "--arm", arm, "--tree", str(a.tree.resolve())]
        if a.reintroduce:
            cmd.append("--reintroduce")
        procs[arm] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True, env=env, cwd=a.tree.resolve())
    total_loop = total_exec = 0
    for arm, p in procs.items():
        out, err = p.communicate()
        line = next((ln for ln in out.splitlines() if ln.startswith(MARK)), None)
        if line is None:
            print(f"arm {arm}: did not run rc={p.returncode}\n{err[-1500:]}")
            print(f"RESULT {arm}_ran=0 count")
            continue
        d = json.loads(line[len(MARK):])
        c = d["counts"]
        print(f"arm {arm}: cycles={d['cycles']} cycle_offenders={d['cycle_offenders']} "
              f"worker={c.get('worker', 0)} loop={c.get('loop', 0)} executor={c.get('executor', 0)}")
        for s, n in d["sites"].items():
            print(f"  seam {s} x{n}")
        for k, n in sorted(c.items()):
            if k.startswith("surface:"):
                print(f"  {k} x{n}")
        for e in d.get("surface_errors") or []:
            print(f"  surface error {e}")
        print(f"  reached in worker: {sorted(d['worker_sites'])}")
        for st, n in d.get("stacks", {}).items():
            print(f"  stack x{n}: {st}")
        for route, ms in d.get("off_cpu_ms", {}).items():
            print(f"RESULT {arm}_{route}_kernel_cpu_ms={ms} ms (provisional)")
            print(f"RESULT {arm}_{route}_kernel_cpu_ms_per_cycle={ms / max(1, d['cycles']):.1f} ms (provisional)")
        print(f"RESULT {arm}_loop={c.get('loop', 0)} count")
        print(f"RESULT {arm}_executor={c.get('executor', 0)} count")
        print(f"RESULT {arm}_worker={c.get('worker', 0)} count")
        total_loop += c.get("loop", 0)
        total_exec += c.get("executor", 0)
    print(f"RESULT loop_kernels_total={total_loop} count")
    print(f"RESULT executor_kernels_total={total_exec} count")
    pc = time.process_time() - c0
    tc = time.thread_time() - tc0
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={(pc / tc) if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
