import atexit, os, runpy, subprocess, sys, time
spawned = []
_P = subprocess.Popen
class P(_P):
    def __init__(self, args, *a, **k):
        super().__init__(args, *a, **k)
        if "process_worker" in " ".join(map(str, args if isinstance(args, (list, tuple)) else [args])):
            spawned.append(self)
subprocess.Popen = P
def report():
    live = [p for p in spawned if p.poll() is None]
    print(f"PROBE spawns={len(spawned)} live_at_exit={len(live)}", file=sys.__stderr__, flush=True)
atexit.register(report)
sys.argv = ["tests/features.py"]
sys.path.insert(0, "tests")
runpy.run_path("tests/features.py", run_name="__main__")
