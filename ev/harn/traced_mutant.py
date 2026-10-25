"""Reviewer's own instrument: drive one mutant through one driver N times, each
run TRACED with the lane's own hook (tests/mutation_table.py REACH_HOOK), and
report per run: rc, failed checks, and whether the mutated line was executed.
A red run that never executed the mutated line ran the original program: it is
a flake by construction, not a kill the skip lost.
usage: traced_mutant.py <repo> <driver> <rel> <line> <runs> <jobs> [--unmutated]"""
import sys, shutil, tempfile, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
repo, drv, rel, line, runs, jobs = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
unmut = "--unmutated" in sys.argv
sys.path.insert(0, f"{repo}/tests")
import mutation_table as mt
mut = next(m for m in mt.candidates(Path(repo)/rel) if m["line"] == line and m["kind"] == "GUARD_OFF") if not unmut else None
def one(i):
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)/"t"
        shutil.copytree(repo, t, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        if mut:
            p = t/rel; ls = p.read_text().splitlines(True)
            assert ls[line-1].rstrip("\n") == mut["old"]; ls[line-1] = mut["new"] + "\n"; p.write_text("".join(ls))
        out = Path(d)/"rec"; out.mkdir()
        env = mt.hook_env(out)
        a, e = mt.drive_spec(drv, "HEAD^1") if hasattr(mt, "drive_spec") else ([], {})
        tenv = {**(e or {}), **env, "PYTHONPATH": mt.traced_pythonpath(env, (e or {}).get("PYTHONPATH", "tests/hastub"))}
        r = mt.run_script(drv, t, 900, a, tenv)
        reach = mt.collect(out)
        hit = line in reach["hits"].get(rel, [])
        fails = [l.strip()[:110] for l in (r.stdout or "").splitlines() if l.strip().startswith("FAIL")]
        return f"run {i}: rc={r.rc} line_{line}_executed={hit} problems={mt.reach_problems({**reach,'rc':r.rc})} fails={fails}"
with ThreadPoolExecutor(jobs) as ex:
    for s in ex.map(one, range(runs)): print(s, flush=True)
