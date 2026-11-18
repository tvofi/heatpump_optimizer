"""D9-s1 H7: the persistent solve worker's (process_worker.run_worker) resident
memory, idle, and its slope over consecutive solves; plus the IPC bytes of one
job and one reply.

Metric: VmRSS / VmHWM (kB, /proc/<pid>/status) of the child started by
coordinator._ensure_worker, before any job, after job 1, and after job N;
slope = (RSS_N - RSS_1)/(N-1) kB per solve. IPC bytes = len(pickle.dumps) of
(optimize_in_process, args) and of the returned OptimizationResult.
Count key: the kernel's accounting of the real child process.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/worker_rss.py [--jobs 8] [--leak-kb 0]
Perturbation: --leak-kb K sends a job whose function appends K kB to a
module-level list in the child each call (a synthetic leak): the slope must
go UP by ~K kB/solve, which proves the slope can see a leak.
Bytes are final; RSS is provisional. Baseline SHA 1936d5ca72a0.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import pickle

import stress
from heatpump_optimizer import coordinator as coord
from heatpump_optimizer.optimizer import optimize_in_process


def status(pid):
    out = {}
    with open(f"/proc/{pid}/status") as fh:
        for line in fh:
            if line.startswith(("VmRSS", "VmHWM")):
                k, v = line.split(":")
                out[k] = int(v.split()[0])
    return out


def child_cpu_ms(pid):
    with open(f"/proc/{pid}/stat") as fh:
        f = fh.read().rsplit(")", 1)[1].split()
    tck = os.sysconf("SC_CLK_TCK")
    return (int(f[11]) + int(f[12])) * 1000.0 / tck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--leak-kb", type=int, default=0)
    args = ap.parse_args()
    run = stress.build_case(season="winter", two_zone=False, dhw=True)
    positional = (run["prices"], run["outdoor"], run["wind"], run["rain"], run["solar"],
                  stress.START, None, run["surplus"])
    keywords = dict(space_pins=run["space_pins"], power_caps_extra=run["power_caps_extra"])
    job_args = (run["optimizer"], run["initial"], positional, keywords)
    C.result("ipc_job_bytes", len(pickle.dumps((optimize_in_process, job_args), protocol=pickle.HIGHEST_PROTOCOL)), "bytes")
    worker = coord._ensure_worker()
    pid = worker.pid
    import time as _t
    # the child imports lazily on the first unpickle; measure bare interpreter first
    _t.sleep(0.3)
    C.result("worker_rss_kb_before_job", status(pid)["VmRSS"], "kB (provisional)")
    rss = []
    cpu = []
    try:
        for j in range(args.jobs):
            if args.leak_kb:
                # builtins.exec pickles by name, so the child can load it
                coord._run_in_process(exec, (
                    "import builtins as _b\n"
                    "_b.__dict__.setdefault('_D9_S1_LEAK', []).append("
                    f"bytearray({args.leak_kb} * 1024))",))
            res = coord._run_in_process(optimize_in_process, job_args)
            rss.append(status(pid)["VmRSS"])
            cpu.append(child_cpu_ms(pid))
        C.result("ipc_reply_bytes", len(pickle.dumps(("ok", res), protocol=pickle.HIGHEST_PROTOCOL)), "bytes")
        st = status(pid)
        C.result("worker_rss_kb_after_job1", rss[0], "kB (provisional)")
        C.result(f"worker_rss_kb_after_job{args.jobs}", rss[-1], "kB (provisional)")
        C.result("worker_hwm_kb", st["VmHWM"], "kB (provisional)")
        if len(rss) >= 8:
            h = len(rss) // 2
            C.result("worker_rss_slope_second_half_kb_per_solve", round((rss[-1] - rss[h]) / max(len(rss) - 1 - h, 1), 1), "kB/solve (provisional)")
        C.result("worker_rss_slope_kb_per_solve", round((rss[-1] - rss[0]) / max(len(rss) - 1, 1), 1), "kB/solve (provisional)")
        C.result("worker_cpu_ms_first_job_incl_imports", round(cpu[0], 0), "ms (provisional)")
        if len(cpu) > 2:
            warm = (cpu[-1] - cpu[0]) / (len(cpu) - 1)
            C.result("worker_cpu_ms_per_warm_job", round(warm, 0), "ms (provisional)")
            C.result("respawn_overhead_ms", round(cpu[0] - warm, 0), "ms (provisional; first job minus a warm job)")
        C.result("parent_rss_kb", status(os.getpid())["VmRSS"], "kB (provisional)")
    finally:
        coord._shutdown_process_pool()
    C.trailer(1.0)


if __name__ == "__main__":
    main()
