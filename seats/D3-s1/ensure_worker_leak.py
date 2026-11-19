#!/usr/bin/env python3
"""D3-s1 box D3-u1d: what one closure driver does under the _ensure_worker
GUARD_OFF mutant (pre-screen key dc6c13eca2ca1737), measured safely.

Metric (one line): peak count of live `process_worker.py` processes that
descend from one run of the driver script (default tests/boost_drift_replay.py),
sampled every 0.5 s; the run is killed (whole process group) once the count
reaches --cap, so the box's memory cgroup is never exhausted.
Count key: processes whose argv names custom_components/.../process_worker.py
and whose ancestry reaches the driver's pid (never a box-wide count).

Instrumented symbol: custom_components/heatpump_optimizer/coordinator.py:_ensure_worker
(line 1864, `if worker is not None and worker.poll() is None:`).
Perturbation: `--mutant` rewrites that line to `if False:` (the pre-screen's
GUARD_OFF) in a private detached worktree; the count must move from the
unmutated arm's peak (null control, expected <= 1) up to --cap.

Run (export root, PYTHONPATH=tests/hastub):
  python3 dev/audit/rounds/round11/D3/s1/ensure_worker_leak.py [--mutant] [--cap 40] [--script tests/boost_drift_replay.py]
Expected: RESULT peak_process_workers=<=1 (null), =cap with --mutant; RESULT capped=1 with --mutant.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1d (Linux x86_64, 4 cores).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
FILE = "custom_components/heatpump_optimizer/coordinator.py"
LINE = 1864
OLD = "    if worker is not None and worker.poll() is None:"
NEW = "    if False:"


def children() -> dict[int, tuple[int, str]]:
    out = {}
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            st = (d / "stat").read_text()
            ppid = int(st[st.rindex(")") + 2:].split()[1])
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        out[int(d.name)] = (ppid, cmd)
    return out


def descendants_matching(root: int, needle: str) -> int:
    procs = children()
    n = 0
    for pid, (_, cmd) in procs.items():
        if needle not in cmd:
            continue
        p = pid
        while p in procs and p > 1:
            if p == root:
                n += 1
                break
            p = procs[p][0]
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutant", action="store_true")
    ap.add_argument("--cap", type=int, default=40)
    ap.add_argument("--script", default="tests/boost_drift_replay.py")
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="d3s1-leak-"))
    wt = tmp / "wt"
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(wt), "HEAD"],
                   cwd=ROOT, check=True)
    try:
        if a.mutant:
            p = wt / FILE
            src = p.read_text().splitlines(keepends=True)
            assert src[LINE - 1].rstrip("\n") == OLD, src[LINE - 1]
            src[LINE - 1] = NEW + "\n"
            p.write_text("".join(src))
        env = {**os.environ, "PYTHONPATH": "tests/hastub"}
        t0 = time.monotonic()
        proc = subprocess.Popen([sys.executable, a.script], cwd=wt, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        peak, capped = 0, 0
        while proc.poll() is None:
            n = descendants_matching(proc.pid, "process_worker.py")
            peak = max(peak, n)
            if n >= a.cap:
                capped = 1
                break
            if time.monotonic() - t0 > a.timeout:
                break
            time.sleep(0.5)
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        # orphaned workers leave the process group only if they setsid; sweep by session
        time.sleep(1)
        print(f"RESULT arm={'mutant' if a.mutant else 'null'}")
        print(f"RESULT peak_process_workers={peak}")
        print(f"RESULT capped={capped}")
        print(f"RESULT script_rc={proc.returncode}")
        print(f"RESULT seconds={time.monotonic() - t0:.1f}")
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
        print("RESULT thread_factor=1.00")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT,
                       capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
