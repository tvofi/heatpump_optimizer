"""V2 (independent) harness for D1-s2-05.

Metric (one line): wall seconds for production coordinator._shutdown_process_pool
(the body of the EVENT_HOMEASSISTANT_STOP listener) to return when called from a
second thread 0.3 s into a job of known duration D running through production
_run_in_process (the child runs time.sleep(D)), divided by D, for D in {2, 5} s;
null control: the same call with no job in flight.
Count key: time around the production call; job duration fixed by the job itself
(not a solve), so the ratio is independent of solver speed and box load.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_stop_reap.py [--unlocked]
Expected: ratio ~ (D-0.3)/D, i.e. 0.85 (D=2) and 0.94 (D=5) +-0.05; idle < 0.1 s.
  --unlocked (_PROCESS_LOCK rebound to a fresh Lock for the stop call only): ratio < 0.05.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, threading, time, logging
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from heatpump_optimizer import coordinator as cm  # noqa

UNLOCKED = "--unlocked" in sys.argv


def stop_call():
    t = time.monotonic()
    if UNLOCKED:
        real = cm._PROCESS_LOCK
        cm._PROCESS_LOCK = threading.Lock()
        try:
            cm._shutdown_process_pool()
        finally:
            cm._PROCESS_LOCK = real
    else:
        cm._shutdown_process_pool()
    return time.monotonic() - t


def trial(d):
    cm._run_in_process(time.sleep, (0.0,))  # worker warm
    out = {}

    def job():
        try:
            cm._run_in_process(time.sleep, (d,))
        except Exception as e:  # noqa: BLE001 -- killed child
            out["err"] = type(e).__name__
    th = threading.Thread(target=job)
    th.start()
    time.sleep(0.3)
    lat = stop_call()
    th.join(timeout=d + 10)
    return lat


idle = []
for _ in range(3):
    cm._run_in_process(time.sleep, (0.0,))
    idle.append(stop_call())
idle.sort()
print(f"RESULT stop_idle_s={idle[1]:.3f} s (median of 3) provisional")
for d in (2.0, 5.0):
    rs = sorted(trial(d) / d for _ in range(3))
    print(f"RESULT stop_ratio_D{d:g}={rs[1]:.3f} ratio (median of 3; min {rs[0]:.3f} max {rs[2]:.3f})")
cm._shutdown_process_pool()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print("RESULT deliberate_thread_cpu_s=~0 (job thread blocks in pickle.load)")
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
