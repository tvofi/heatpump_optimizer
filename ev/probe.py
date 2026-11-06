"""Reviewer's own probe (not the finder's: #3226 has no committed harness).
Run from a tree root: PYTHONPATH=tests/hastub:. python3 probe.py <mode>"""
import asyncio, os, sys, time, resource, threading, importlib, subprocess
sys.path.insert(0, "tests/hastub"); sys.path.insert(0, ".")
c = importlib.import_module("custom_components.heatpump_optimizer.coordinator")
mode = sys.argv[1]
TO = getattr(c, "ProcessWorkerTimeout", None)

def big(n):
    return b"x" * n

if mode == "fd":
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (min(4096, hard), hard))
    c._shutdown_process_pool()
    fds = [os.open(os.devnull, os.O_RDONLY) for _ in range(1100)]
    try:
        pid = c._run_in_process(os.getpid, ())
        fd = c._PROCESS_WORKER.stdout.fileno()
        c.PROCESS_REPLY_TIMEOUT_S = 0.5
        t = time.monotonic()
        try:
            c._run_in_process(time.sleep, (5,)); r = "returned"
        except Exception as e:
            r = type(e).__name__
        print(f"RESULT fd ok child={pid} stdout_fd={fd} slow={r} after {time.monotonic()-t:.1f}s")
    except Exception as e:
        print(f"RESULT fd FAIL {type(e).__name__}: {e}")
elif mode == "bigreply":
    c._run_in_process(os.getpid, ())
    c.PROCESS_REPLY_TIMEOUT_S = 5.0
    for n in (10**6, 50 * 10**6):
        t = time.monotonic(); import operator; out = c._run_in_process(operator.mul, (b"x", n))
        print(f"RESULT bigreply {n} bytes ok={len(out)==n} in {time.monotonic()-t:.2f}s (pipe buffer 65536)")
elif mode == "loopblocked":
    # real loop, real ThreadPoolExecutor; the loop is blocked by a sync sleep
    # while the off-loop job waits for its reply. The deadline must fire in the
    # executor thread regardless: the worker is killed by t~0.5 s.
    class H:
        def __init__(self): self.data = {}
        async def async_add_executor_job(self, f, *a):
            return await asyncio.get_running_loop().run_in_executor(None, f, *a)
    c._run_in_process(os.getpid, ())
    pid = c._PROCESS_WORKER.pid
    c.PROCESS_REPLY_TIMEOUT_S = 0.5
    async def main():
        t0 = time.monotonic()
        task = asyncio.ensure_future(c._await_off_loop(H(), time.sleep, 30))
        await asyncio.sleep(0.05)
        time.sleep(2.0)                     # the loop is blocked here
        try:
            os.kill(pid, 0); alive = subprocess.run(["ps","-o","stat=","-p",str(pid)],capture_output=True,text=True).stdout.strip()
        except ProcessLookupError:
            alive = "gone"
        try:
            await asyncio.wait_for(task, 40); r = "returned"
        except Exception as e:
            r = type(e).__name__
        print(f"RESULT loopblocked worker state at t=2.05s while loop blocked: {alive or 'gone'}; outcome={r} after {time.monotonic()-t0:.1f}s")
    asyncio.run(main())
elif mode == "leak":
    c._run_in_process(os.getpid, ())
    n0 = len(os.listdir("/proc/self/fd"))
    c.PROCESS_REPLY_TIMEOUT_S = 0.2
    t = time.monotonic()
    for _ in range(10):
        try: c._run_in_process(time.sleep, (5,))
        except Exception: pass
    c.PROCESS_REPLY_TIMEOUT_S = 30
    n1 = len(os.listdir("/proc/self/fd"))
    kids = subprocess.run(["ps","-o","pid=,stat=","--ppid",str(os.getpid())],capture_output=True,text=True).stdout.split("\n")
    kids = [k.strip() for k in kids if k.strip() and "ps" not in k]
    print(f"RESULT leak 10 timeouts in {time.monotonic()-t:.1f}s fds {n0}->{n1} children={kids} threads={threading.active_count()} lock_free={c._PROCESS_LOCK.acquire(blocking=False) and (c._PROCESS_LOCK.release() or True)}")
elif mode == "interrupt":
    # a BaseException (KeyboardInterrupt-like) inside the wait must release the lock
    c._run_in_process(os.getpid, ())
    orig = c._reply_ready
    def boom(*a): raise KeyboardInterrupt
    c._reply_ready = boom
    try: c._run_in_process(os.getpid, ())
    except BaseException as e: r = type(e).__name__
    c._reply_ready = orig
    free = c._PROCESS_LOCK.acquire(blocking=False)
    if free: c._PROCESS_LOCK.release()
    print(f"RESULT interrupt raised={r} lock_free={free}")
