"""Reviewer's own mutants for beatd.py (not the PR's MUTANTS table).
Usage: python -I xmut.py <worktree> [name ...]. Imports the worktree's beatd.py, plants
each mutant in a temp copy, runs the named case via beatd._run_case and prints the full
result dict, so a crash is reported as a crash, not counted as a kill."""
import sys, tempfile, json
from pathlib import Path
wt = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(wt / "tools/audit/seat"))
import beatd
X = {
 "x1_no_sigkill": ("beatd", "                    os.killpg(p.pid, signal.SIGKILL)\n", "                    pass\n", "3"),
 "x2_no_real_git_env": ("beatd", "HPO_REAL_GIT=self.git,", "", "6b"),
 "x3_no_ref_lock_timeout": ("beatd", 'GIT_CONFIG_VALUE_0="30000"', 'GIT_CONFIG_VALUE_0="0"', "6b"),
 "x4_no_heartbeat": ("beatd", "elif hb and now - beat >= hb:", "elif False:", "3"),
 "x5_no_down": ("beatd", '    if pid is None:\n        out.append("DOWN', '    if False:\n        out.append("DOWN', "7"),
 "x6_no_owner_dead": ("beatd", "if p is not None and not pid_alive(p):", "if False:", "7"),
 "x7_stale_off_by_one": ("beatd", "elif int(r.stdout) > 0:", "elif int(r.stdout) > 1:", "7"),
 "x8_watch_as_periodic": ("beatd", 'nxt = (time.time() if job["kind"] == "watch" else max(nxt, start))', "nxt = max(nxt, start)", "4"),
 "x9_class_no_wait": ("beatd", 'cl.take(self.table["class_wait_s"])', "cl.take(0)", "5"),
 "x10_journal_unchecked": ("beatd", "        if not LINE_RE.match(ln):", "        if False:", "7"),
 "x11_retry_any_failure": ("shim", "! grep -q 'cannot lock ref' \"$err\"", "false", "6"),
 "x12_shim_accepted": ("beatd", "    if is_shim(real):", "    if False:", "6"),
 "x13_unreadable_staleness_clean": ("beatd", "            rc = 2\n", "            rc = 0\n", "7"),
 "x14_running_ignored": ("beatd", "        if n in running:", "        if False:", "7"),
 "x15_sigterm_handler_off": ("beatd", "        signal.signal(signal.SIGTERM, term)", "        pass", "2"),
 "x16_held_never_dead_clear": ("beatd", "        running.clear()  # no beat", "        pass  # no beat", "7"),
}
names = sys.argv[2:] or list(X)
for n in names:
    f, a, r, case = X[n]
    src = (beatd.SELF if f == "beatd" else beatd.SHIM).read_text()
    if src.count(a) != 1:
        print(f"{n}: ANCHOR count={src.count(a)}"); continue
    beatd.MUTANTS[n] = (f, a, r, case, "")
    with tempfile.TemporaryDirectory(prefix="xmut-") as td:
        prog, shim = beatd._mutant_copy(Path(td), n)
        try:
            got = beatd._run_case(case, prog, shim, Path(td) / "w")
            red = [k for k, v in got.items() if not v]
            print(f"{n} case({case}): {'KILLED by ' + '; '.join(red) if red else 'SURVIVED'}", flush=True)
        except Exception as e:
            print(f"{n} case({case}): CRASH {type(e).__name__}: {str(e)[:120]}", flush=True)
