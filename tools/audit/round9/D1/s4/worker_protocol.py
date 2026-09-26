#!/usr/bin/env python3
"""D1-s4 M1/M5: the process worker's framing under hostile jobs, driven over its real pipes.

Metric (one line): per job kind, whether the parent-side read (pickle.load on the worker's
stdout, as coordinator._run_in_process does) returns a well-formed (status, payload) reply,
and whether the same worker then answers a follow-up ``ok`` job.  Key: the frame the
production ``process_worker.run_worker`` writes.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/worker_protocol.py
          [--perturb]  run the child with ``_dump`` replaced by a raw pickle.dump (the pre-#511/#524
                       shape): the unpicklable kind must stop answering (well_formed 1 -> 0).
Expected (baseline): ok/raises/unpicklable/garbage well_formed=1; prints well_formed=0
          (stdout is the reply channel); exits well_formed=0 (no reply, rc=3).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6
Instrumented: custom_components/heatpump_optimizer/process_worker.py:run_worker, _dump
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import pickle
import subprocess
import sys
import time
from pathlib import Path

t_proc0, t_thr0 = time.process_time(), time.thread_time()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import worker_jobs  # noqa: E402

SCRIPT = Path("custom_components/heatpump_optimizer/process_worker.py").resolve()
PERTURB = "--perturb" in sys.argv
LAUNCH = (
    "import runpy,sys,pickle; sys.argv=[{s!r}]; "
    "g=runpy.run_path({s!r}, run_name='hpo_worker'); "
    "g['_dump']=lambda out,p:(out.write(pickle.dumps(p)),out.flush()); "
    "g['run_worker'].__globals__['_dump']=g['_dump']; g['run_worker']()"
).format(s=str(SCRIPT))


def spawn():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(HERE), env.get("PYTHONPATH", "")])
    cmd = [sys.executable, "-u", str(SCRIPT)] if not PERTURB else [sys.executable, "-u", "-c", LAUNCH]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)


def ask(w, blob):
    w.stdin.write(blob)
    w.stdin.flush()
    try:
        reply = pickle.load(w.stdout)
        return isinstance(reply, tuple) and len(reply) == 2 and reply[0] in ("ok", "err", "load-err"), reply
    except Exception as err:  # noqa: BLE001
        return False, err


def job(fn, *args):
    return pickle.dumps((fn, args), protocol=pickle.HIGHEST_PROTOCOL)


kinds = {
    "ok": job(worker_jobs.ok, 2),
    "raises": job(worker_jobs.raises, 2),
    "unpicklable": job(worker_jobs.unpicklable, 2),
    "prints": job(worker_jobs.prints, 2),
    "exits": job(worker_jobs.exits, 2),
    "garbage": b"\x80\x05not a pickle at all\n" * 3,
}
print(f"MODE perturb={PERTURB}")
for name, blob in kinds.items():
    w = spawn()
    good, reply = ask(w, blob)
    follow = False
    if good and reply[0] != "load-err":
        follow, _r = ask(w, job(worker_jobs.ok, 5))
    try:
        w.stdin.close()
    except Exception:  # noqa: BLE001
        pass
    try:
        rc = w.wait(timeout=10)
    except subprocess.TimeoutExpired:
        w.kill()
        rc = "hung"
    print(f"RESULT {name}.well_formed={int(good)} count")
    print(f"RESULT {name}.answers_next={int(bool(follow))} count")
    print(f"RESULT {name}.rc={rc}")
    print(f"# {name}: {type(reply).__name__} {str(reply)[:90]!r}")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
