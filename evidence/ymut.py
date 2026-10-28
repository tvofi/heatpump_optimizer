"""Reviewer's own mutant harness for #2916 (not the finder's; the PR's MUTANTS are the fixer's).
Plants each Y entry in a temp copy (beatd's own _mutant_copy) and runs the named cases'
functions from the unmutated module against the copy. Reports checks that went False,
against the unmutated baseline run of the same cases. Usage: python -I ymut.py <worktree>"""
import sys, tempfile, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
wt = Path(sys.argv[1]); sys.path.insert(0, str(wt / "tools/audit/seat"))
import beatd as B
Y = {
 "y1_kill_group_no_grace": ("beatd", "        while time.time() < at:\n", "        while False:\n", "3"),
 "y2_drop_keeps_pid": ("beatd", "            os.ftruncate(self.fd, 0)\n            fcntl.flock(self.fd, fcntl.LOCK_UN)", "            fcntl.flock(self.fd, fcntl.LOCK_UN)", "2,8,3"),
 "y3_no_state_subst": ("beatd", '[x.replace("$S", str(self.state)) for x in job["argv"]]', 'list(job["argv"])', "1,4,5"),
 "y4_no_relative_argv": ("beatd", "            a[0] = str(self.repo / a[0])\n", "            pass\n", "1,4,5,6b"),
 "y5_no_env_pass": ("beatd", '(*BASE_ENV, *job["env_pass"])', "BASE_ENV", "4,5,6b"),
 "y6_shim_no_pull": ("shim", "case $sub in fetch|pull) ;;", "case $sub in fetch) ;;", "6"),
 "y7_shim_no_export": ("shim", "export HPO_REAL_GIT=$real", ":", "6"),
 "y8_watch_under_60_ok": ("beatd", '        if j["kind"] == "watch" and j["interval_s"] < 60:', "        if False:", "1"),
 "y9_duplicate_name_ok": ("beatd", "or name in seen or name", "or name", "1"),
 "y10_status_nonok_ok": ("beatd", 'st = "ok" if outcome in ("ok", "none") else outcome', 'st = "ok"', "7"),
 "y11_no_job_name_env": ("beatd", 'HPO_BEATD_JOB=job["name"], ', "", "4,6b"),
 "y12_no_reflock_timeout": ("beatd", 'GIT_CONFIG_COUNT="1"', 'GIT_CONFIG_COUNT="0"', "6,6b"),
 "y13_idle_hides_failure": ("beatd", 'if st == "idle" and outcome not in ("ok", "none"):', "if False:", "7"),
 "y14_shim_skip_no_c": ("shim", "-C|-c|--git-dir", "-C|--git-dir", "6"),
 "y15_for_ignored": ("beatd", "tm = threading.Timer(for_s, self.stop.set)", "tm = threading.Timer(1e6, self.stop.set)", "2,4,5"),
 "y16_grace_half_second": ("beatd", "KILL_GRACE_S = 10.0", "KILL_GRACE_S = 0.5", "3"),
}
import os as _os
if _os.environ.get("ONLY"): Y = {k: v for k, v in Y.items() if k in _os.environ["ONLY"].split(",")}
def run(case, prog, shim, td):
    try: return B._run_case(case, prog, shim, td)
    except Exception as e: return {"CRASH": f"{type(e).__name__}: {str(e)[:100]}"}
def plant(name):
    f, a, r, cases = Y[name]
    with tempfile.TemporaryDirectory(prefix="ymut-") as td:
        B.MUTANTS[name] = (f, a, r, "x", "x")
        src = B.production(B.SELF.read_text()) if f == "beatd" else B.SHIM.read_text()
        cnt = src.count(a)
        prog, shim = B._mutant_copy(Path(td), name)
        out = {c: run(c, prog, shim, Path(td) / f"w{c}") for c in cases.split(",")}
        return cnt, out
allc = sorted({c for v in Y.values() for c in v[3].split(",")})
def base(c):
    with tempfile.TemporaryDirectory(prefix="ybase-") as td:
        return run(c, B.SELF, B.SHIM, Path(td))
with ThreadPoolExecutor(4) as p:
    baseline = dict(zip(allc, p.map(base, allc)))
    for c in allc:
        bad = [k for k, v in baseline[c].items() if v is not True]
        print(f"BASELINE ({c}) {len(baseline[c])} checks, not-true: {bad}")
    names = list(Y)
    res = dict(zip(names, p.map(plant, names)))
for n in names:
    cnt, out = res[n]
    red = [f"({c}) {k}" for c, d in out.items() for k, v in d.items() if v is not True and baseline[c].get(k) is True]
    crash = [f"({c}) {d['CRASH']}" for c, d in out.items() if "CRASH" in d]
    verdict = "NOT-RUN(anchor count %d)" % cnt if cnt != 1 else ("CRASH" if crash and not red else ("KILLED" if red else "SURVIVED"))
    print(f"RESULT {n}: {verdict}; red={red}; crash={crash}")
