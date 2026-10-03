# Reviewer's own mutants (not the fixer's mut.py). One at a time, in place, restored.
import subprocess, sys, os
P = "tests/nightly_ha.py"
M = {
 "R1 delete the gap line in _beat": ("        self.max_gap = max(self.max_gap, now - self._last)\n        self._last, self._stall_dumped", "        self._last, self._stall_dumped"),
 "R3 third container without SYS_PTRACE": ("extra=[\"--heartbeat-only\"], caps=(\"SYS_PTRACE\",),", "extra=[\"--heartbeat-only\"],"),
 "R4 _stage never stages py-spy": ("    if two_zone_dhw:\n        stage_py_spy(driver, _host_py_spy())\n", ""),
 "R7 stop() never signals the watcher": ("        self._stop.set()\n", ""),
 "R8 stop() never cancels the tick": ("        if self._handle is not None:\n            self._handle.cancel()\n", ""),
}
only = sys.argv[1:] 
orig = open(P).read()
for name, (a, b) in M.items():
    if only and name.split()[0] not in only: continue
    assert orig.count(a) == 1, name
    open(P, "w").write(orig.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "tests/entities.py"], capture_output=True, text=True)
        s = [l for l in r.stdout.splitlines() if "ENTITY CHECKS" in l]
        f = [l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        print(f"RESULT {name}: rc={r.returncode} {s[-1] if s else r.stderr.strip()[-300:]}", flush=True)
        for l in f[:5]: print("    ", l[:180], flush=True)
    finally:
        open(P, "w").write(orig)
