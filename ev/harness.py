import os, sys, time, subprocess, signal
sys.path.insert(0, sys.argv[1])
import mutant_run as m
S = sys.argv[2]
def leftover(tag):
    return subprocess.run(["pgrep", "-f", tag], capture_output=True, text=True).stdout.split()
def reap(tag):
    for p in leftover(tag):
        try: os.kill(int(p), signal.SIGKILL)
        except Exception: pass
cases = [
 # name, argv, cap, timeout, tag
 ("E1 setsid+clean-env chain (escape)", ["python3", f"{S}/chain.py", "cleanenv", "80"], 32, 15, "chain.py cleanenv"),
 ("E1-null same chain keeping env (control)", ["python3", f"{S}/chain.py", "keepenv", "80"], 32, 15, "chain.py keepenv"),
 ("E2 double-fork setsid daemon, env -i, outlives command (escape)", ["sh", "-c", "(setsid env -i /bin/sh -c 'exec -a escE2 sleep 60' </dev/null >/dev/null 2>&1 &) ; exit 0"], 32, 15, "escE2"),
 ("E2-null same daemon keeping env (control)", ["sh", "-c", "(setsid /bin/sh -c 'exec -a escE2n sleep 60' </dev/null >/dev/null 2>&1 &) ; exit 0"], 32, 15, "escE2n"),
 ("E3 double fork, no setsid, orphan outlives command (covered)", ["sh", "-c", "( (exec -a escE3 sleep 60) & ) ; exit 0"], 32, 15, "escE3"),
 ("E4 orphan that setsid's after reparent to 1 with clean env (escape)", ["sh", "-c", "( sh -c 'sleep 0.3; exec setsid env -i sh -c \"exec -a escE4 sleep 60\"' & ) ; exit 0"], 32, 15, "escE4"),
]
for name, argv, cap, to, tag in cases:
    reap(tag)
    m.FORKCAP[0] = cap
    t0 = time.monotonic()
    rc = m.run_cmd(argv, __import__("pathlib").Path(S), to)
    dt = time.monotonic() - t0
    time.sleep(1.0)
    left = leftover(tag)
    label = {m.FORKCAP_RC: "FORKCAP", m.TIMEOUT_RC: "TIMEOUT"}.get(rc, f"rc={rc}")
    print(f"RESULT {name}: outcome={label} wall={dt:.1f}s leftover_after_run={len(left)}", flush=True)
    reap(tag)
