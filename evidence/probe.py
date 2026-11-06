import os, sys, time, resource, asyncio, gc
sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests", "hastub"), os.path.join(os.getcwd(), "tests")]
import custom_components.heatpump_optimizer.coordinator as c
import operator
def big(n): return operator.mul(b"x", n)
def which(): return os.getpid()
mode = sys.argv[1]
if mode == "big":
    c._run_in_process(os.getpid, ())
    if hasattr(c, "PROCESS_REPLY_TIMEOUT_S"): c.PROCESS_REPLY_TIMEOUT_S = 2.0
    for n in (10, 70_000, 10_000_000, 100_000_000):
        t = time.monotonic(); out = c._run_in_process(operator.mul, (b"x", n)); print(f"RESULT big n={n} len={len(out)} s={time.monotonic()-t:.2f}")
elif mode == "fd":
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (min(4096, hard), hard))
    held = [os.open("/dev/null", os.O_RDONLY) for _ in range(1100)]
    try:
        out = c._run_in_process(os.getpid, ())
        print(f"RESULT fd ok child={out} stdout_fd={c._PROCESS_WORKER.stdout.fileno()}")
    except Exception as e:
        print(f"RESULT fd FAIL {type(e).__name__}: {e}")
elif mode == "leak":
    c._run_in_process(os.getpid, ())
    c.PROCESS_REPLY_TIMEOUT_S = 0.3
    def nfd(): return len(os.listdir("/proc/self/fd"))
    f0 = nfd(); t = time.monotonic()
    errs = []
    for i in range(10):
        try: c._run_in_process(time.sleep, (5,))
        except Exception as e: errs.append(e)
    del errs; gc.collect()
    import subprocess
    z = subprocess.run(["sh","-c",f"ps -o stat=,pid= --ppid {os.getpid()}"],capture_output=True,text=True).stdout.split("\n")
    print(f"RESULT leak 10 timeouts in {time.monotonic()-t:.1f}s fds {f0}->{nfd()} children={[l for l in z if l.strip()]}")
elif mode == "offloop":
    class H:
        async def async_add_executor_job(self, fn, *a):
            return await asyncio.get_running_loop().run_in_executor(None, fn, *a)
    c._run_in_process(os.getpid, ())
    c.PROCESS_REPLY_TIMEOUT_S = 0.5
    t = time.monotonic()
    try:
        out = asyncio.run(c._await_off_loop(H(), time.sleep, 3)); print(f"RESULT offloop returned {out!r} after {time.monotonic()-t:.1f}s (job re-ran on executor)")
    except Exception as e:
        print(f"RESULT offloop raised {type(e).__name__} after {time.monotonic()-t:.1f}s")
