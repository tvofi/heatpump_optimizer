import subprocess, sys, os, pathlib, concurrent.futures as cf
W = pathlib.Path(sys.argv[1]); REPO = "/home/user/heatpump_optimizer"; H = "01164518380caf4c65bd7ee098ebf0a5f23e6bf4"
F = "tools/audit/seat/merge_train.py"
M = [  # name, line, old, new  (line 0 = whole-file unique replace)
 ("null-control", 0, None, None),
 ("pages-drop-key", 1602, "read_pages(self.run, path, key)", "read_pages(self.run, path)"),
 ("pages-key-literal-empty", 1602, "read_pages(self.run, path, key)", 'read_pages(self.run, path, "")'),
 ("bot_head-workflow_run", 1648, '"workflow_runs"', '"workflow_run"'),
 ("check_runs-1846-checkruns", 1846, '"check_runs"', '"checkruns"'),
 ("gate_deferred-1861-runs", 1861, '"workflow_runs"', '"runs"'),
 ("gate_busy-1871-runs", 1871, '"workflow_runs"', '"runs"'),
 ("sha-check_runs-3337-checkruns", 3337, '"check_runs"', '"checkruns"'),
 ("infra-jobs-3598-job", 3598, '"jobs"', '"job"'),
 ("bot_head-drop-key", 1648, ', "workflow_runs")', ')'),
 ("check_runs-1846-drop-key", 1846, ', "check_runs")', ')'),
 ("gate_deferred-1861-drop-key", 1861, ', "workflow_runs")', ')'),
 ("gate_busy-1871-drop-key", 1871, ', "workflow_runs")', ')'),
 ("sha-3337-drop-key", 3337, ', "check_runs")', ')'),
 ("infra-3598-drop-key", 3598, ', "jobs")', ')'),
]
def one(m):
    name, ln, old, new = m
    d = W / "mw" / name
    subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", str(d), H], check=True)
    p = d / F; L = p.read_text().split("\n")
    if ln:
        assert old in L[ln-1], (name, L[ln-1]); L[ln-1] = L[ln-1].replace(old, new, 1)
        p.write_text("\n".join(L))
    r = subprocess.run([sys.executable, F, "--self-test"], cwd=d, capture_output=True, text=True)
    out = r.stdout + r.stderr
    tail = [l for l in out.splitlines() if "self-test:" in l or l.startswith("  FAIL") or "Stop" in l or "Traceback" in l][-4:]
    killed = r.returncode != 0
    diff = subprocess.run(["git", "-C", str(d), "diff", "-U0"], capture_output=True, text=True).stdout
    subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", str(d)])
    return f"=== {name}: {'KILLED' if killed else 'SURVIVED'} rc={r.returncode}\n{diff}" + "\n".join(tail) + "\n"
with cf.ThreadPoolExecutor(5) as ex:
    for s in ex.map(one, M): print(s, flush=True)
