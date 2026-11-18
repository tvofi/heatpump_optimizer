"""Verifier D1#2 own harness (V2) for D1-s3-04. Metric: of 4 transport-failure routes of
_run_in_process (write raises BrokenPipeError, flush raises OSError, reply read raises EOFError,
reply read raises ConnectionResetError) with a worker whose kill() is a no-op and whose untimed
wait() blocks, how many leave coordinator._PROCESS_LOCK unacquirable 3 s later. Null: the
ProcessWorkerTimeout route. Run: PYTHONPATH=tests/hastub:custom_components python3 v2_peer.py"""
import subprocess, threading, time, sys
from unittest import mock
from heatpump_optimizer import coordinator as c
FOREVER=threading.Event()
class Pipe:
    def __init__(s, exc_write=None, exc_flush=None): s.ew, s.ef = exc_write, exc_flush
    def write(s, b):
        if s.ew: raise s.ew
    def flush(s):
        if s.ef: raise s.ef
class Stuck:
    def __init__(s, stdin): s.stdin=stdin; s.stdout=object(); s.killed=0
    def poll(s): return None
    def kill(s): s.killed+=1
    def terminate(s): pass
    def wait(s, timeout=None):
        if timeout is None: FOREVER.wait(); return 0
        time.sleep(min(timeout,0.2)); raise subprocess.TimeoutExpired("w", timeout)
def route(name, stdin, read_exc):
    w=Stuck(stdin)
    def rr(_):
        if read_exc: raise read_exc
        return ("ok", 1)
    with mock.patch.object(c, "_ensure_worker", lambda: w), mock.patch.object(c, "_read_reply", rr):
        t=threading.Thread(target=lambda: _call(), daemon=True)
        def _call():
            try: c._run_in_process(len, ((),))
            except BaseException: pass
        t=threading.Thread(target=_call, daemon=True); t.start(); t.join(3.0)
        got=c._PROCESS_LOCK.acquire(timeout=3.0)
        if got: c._PROCESS_LOCK.release()
        print(f"  route {name}: returned={not t.is_alive()} lock_held={not got}")
        return (not got), t
held=0; threads=[]
# each held route wedges the lock; so test each in a fresh module lock
import threading as th
for name, stdin, rexc in [("write_BrokenPipe", Pipe(BrokenPipeError()), None),
                          ("flush_OSError", Pipe(None, OSError(5,"EIO")), None),
                          ("read_EOFError", Pipe(), EOFError()),
                          ("read_ConnReset", Pipe(), ConnectionResetError())]:
    with mock.patch.object(c, "_PROCESS_LOCK", th.Lock()):
        h,_=route(name, stdin, rexc); held+=h
with mock.patch.object(c, "_PROCESS_LOCK", th.Lock()):
    h,_=route("null_ProcessWorkerTimeout", Pipe(), c.ProcessWorkerTimeout("t"))
print(f"V2 04 transport_routes_lock_held={held}/4 null_timeout_route_held={int(h)}")
