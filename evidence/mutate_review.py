"""Reviewer's mutant runner (#1869), in a detached worktree at the head."""
import subprocess, pathlib, functools, time
print = functools.partial(print, flush=True)
W = pathlib.Path("/Users/timmalmstrom/hpo-seats/1869-review/mut")
V = "/Users/timmalmstrom/hpo-seats/R9-F11.4-venv/bin/python3"
S = "custom_components/heatpump_optimizer/store.py"
P = "        if old_major_version != self._major:\n"
MUTANTS = [
 ("R0 null", S, None, None),
 ("M2 predicate always true", S, P, "        if True:\n"),
 ("M4 hook returns old_data", S, "        raise NotImplementedError\n\n    def _surface_version", "        return old_data\n\n    def _surface_version"),
 ("M11 every save waits", S, "        if asyncio.current_task() is not self._reader:\n", "        if True:\n"),
 ("M12 no save waits", S, "        if asyncio.current_task() is not self._reader:\n", "        if False:\n"),
 ("RAISE_DEL downgrade re-raise", S, "                self._surface_version(\"it was saved by a newer release than this one\")\n                raise\n", "                self._surface_version(\"it was saved by a newer release than this one\")\n"),
 ("V1 predicate '>' (hook surfaces newer only)", S, P, "        if old_major_version > self._major:\n"),
 ("V2 predicate '<' (hook surfaces older only)", S, P, "        if old_major_version < self._major:\n"),
 ("V3 _major pinned to 1", S, "        self._major = version\n", "        self._major = 1\n"),
 ("V4 reader never cleared", S, "            self._reader = None\n            reading.set_result(None)", "            reading.set_result(None)"),
 ("V5 reader never recorded", S, "        self._reader = asyncio.current_task()\n", ""),
]
for name, path, old, new in MUTANTS:
    p = W / path; orig = p.read_text()
    if old is not None:
        assert orig.count(old) == 1, (name, old); p.write_text(orig.replace(old, new))
    t = time.time()
    try:
        r = subprocess.run([V, "tests/finite_boundary.py"], cwd=W, capture_output=True, text=True, timeout=900, env={"PYTHONPATH": "tests/hastub", "PATH": "/usr/bin:/bin"})
        fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        tail = [l for l in r.stdout.splitlines() if "CHECKS" in l]
        print(f"== {name}: rc={r.returncode} {tail[-1] if tail else r.stderr[-300:]} ({time.time()-t:.0f}s)")
        for f in fails: print("   ", f[:200])
    except subprocess.TimeoutExpired:
        print(f"== {name}: TIMEOUT")
    finally:
        p.write_text(orig)
