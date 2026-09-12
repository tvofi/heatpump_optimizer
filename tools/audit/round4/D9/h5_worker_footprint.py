"""D9 round 4 / H5 -- what the persistent solve worker loads, and what that
costs in resident memory on a Raspberry-Pi-class host.

The shipped solve route is a second interpreter: ``coordinator._ensure_worker``
spawns ``custom_components/heatpump_optimizer/process_worker.py`` and keeps it
for the life of the entry, and every cycle's solve is pickled across its pipe
(#199 #290). Unpickling the job resolves ``optimize_in_process`` by qualified
name, which imports the integration PACKAGE, whose ``__init__`` imports
Home Assistant.

METRIC: (a) the child's ``sys.modules`` inventory, asked of the child itself
through the production pipe; (b) the child's RSS (``ps -o rss=``) at three
points -- just spawned, after the first solve, after N solves; (c) the RSS of
a control child that imports only what a solve arithmetically needs
(``numpy``, ``scipy.optimize``), started with the same interpreter and the
same environment.

``footprint_overhead_mb`` = worker RSS after the first solve minus the
control child's RSS. That is the measured price of importing the HA
integration package into the solve worker.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h5_worker_footprint.py

EXPECTED (baseline 7dd68dd, Apple M1 8 GB, python 3.11):
  worker_modules 900 - 1600, worker_has_homeassistant = True,
  worker_rss_mb_after_first_solve 60 - 110 MiB (PROVISIONAL),
  control_rss_mb 35 - 70 MiB (PROVISIONAL),
  footprint_overhead_mb 10 - 45 MiB (PROVISIONAL, +/- 30 %).

PERTURBATION: ``H5_PERTURB=no_ha`` submits the same solve through a child
whose job is unpickled from a module that does NOT import the package
``__init__`` (``heatpump_optimizer.optimizer`` imported directly with the
package stubbed): ``worker_has_homeassistant`` must become False and
``worker_rss_mb_after_first_solve`` must fall. Run it to size the fix,
not to establish the baseline.

MODULE COUNTS ARE FINAL; RSS MiB are PROVISIONAL.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from heatpump_optimizer import coordinator as CO  # noqa: E402

PROBE = (
    "__import__('json').dumps({"
    "'modules': len(__import__('sys').modules),"
    "'has_ha': 'homeassistant' in __import__('sys').modules,"
    "'has_np': 'numpy' in __import__('sys').modules,"
    "'has_scipy': 'scipy.optimize' in __import__('sys').modules,"
    "'ha_submodules': sum(1 for m in __import__('sys').modules"
    " if m == 'homeassistant' or m.startswith('homeassistant.')),"
    "'hpo_submodules': sum(1 for m in __import__('sys').modules"
    " if 'heatpump_optimizer' in m),"
    "'blas_env': {k: __import__('os').environ.get(k) for k in ("
    "'OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
    "'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},"
    "'threadpoolctl': bool(__import__('importlib').util.find_spec('threadpoolctl')),"
    "})"
)

CONTROL_SRC = (
    "import sys, time, numpy, scipy.optimize\n"
    "print(len(sys.modules), flush=True)\n"
    "time.sleep(30)\n"
)


def rss_kb(pid):
    try:
        out = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(pid)],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        return int(out) if out else -1
    except Exception:  # noqa: BLE001
        return -1


def main():
    print("# baseline=7dd68dd")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")

    # 1. Spawn the worker exactly as production does, measure it cold.
    worker = CO._ensure_worker()
    time.sleep(0.7)
    C.result("worker_rss_mb_spawned_PROVISIONAL",
             float(rss_kb(worker.pid) / 1024.0), "MiB")

    # 2. One real solve through the production pipe.
    packed = C.make_solve(two_zone=True, dhw=True)
    opt = packed["optimizer"]
    from heatpump_optimizer.optimizer import optimize_in_process

    positional = (
        packed["prices"], packed["outdoor"], packed["wind"], packed["rain"],
        packed["solar"], C.START, None, None, None, None, None, None,
        packed["caps"],
    )
    t0 = time.perf_counter()
    CO._run_in_process(optimize_in_process, (opt, packed["state"], positional, {}))
    C.result("first_solve_via_worker_wall_s_PROVISIONAL",
             float(time.perf_counter() - t0), "s")
    C.result("worker_rss_mb_after_first_solve_PROVISIONAL",
             float(rss_kb(worker.pid) / 1024.0), "MiB")

    # 3. Ask the CHILD what it loaded, through the same pipe.
    info = json.loads(CO._run_in_process(eval, (PROBE,)))
    C.result("worker_modules", info["modules"], "modules")
    C.result("worker_has_homeassistant", info["has_ha"])
    C.result("worker_homeassistant_submodules", info["ha_submodules"], "modules")
    C.result("worker_heatpump_optimizer_submodules",
             info["hpo_submodules"], "modules")
    C.result("worker_has_numpy", info["has_np"])
    C.result("worker_has_scipy_optimize", info["has_scipy"])
    C.result("worker_threadpoolctl_available", info["threadpoolctl"])
    for k, v in sorted(info["blas_env"].items()):
        C.result(f"worker_env.{k}", v)

    # 4. Nine more solves, then RSS again.
    for _ in range(9):
        CO._run_in_process(optimize_in_process,
                           (opt, packed["state"], positional, {}))
    C.result("worker_rss_mb_after_10_solves_PROVISIONAL",
             float(rss_kb(worker.pid) / 1024.0), "MiB")
    after10 = rss_kb(worker.pid)

    # 5. Control child: only what the arithmetic needs.
    ctl = subprocess.Popen(
        [sys.executable, "-u", "-c", CONTROL_SRC],
        stdout=subprocess.PIPE, env=CO._worker_env(),
    )
    ctl_modules = int(ctl.stdout.readline().strip())
    time.sleep(0.5)
    ctl_rss = rss_kb(ctl.pid)
    C.result("control_modules", ctl_modules, "modules")
    C.result("control_rss_mb_PROVISIONAL", float(ctl_rss / 1024.0), "MiB")
    C.result("footprint_overhead_mb_PROVISIONAL",
             float((after10 - ctl_rss) / 1024.0), "MiB")
    C.result("module_overhead", info["modules"] - ctl_modules, "modules")
    ctl.kill()
    CO._shutdown_process_pool()
    C.telemetry()


if __name__ == "__main__":
    main()
