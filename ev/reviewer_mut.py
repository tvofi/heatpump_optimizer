import sys, shutil, subprocess, tempfile, pathlib
src = pathlib.Path(sys.argv[1])
MUTS = [
 ("CONTROL-unmutated", "gate.py", "def fresh(r, names):", "def fresh(r, names):"),
 ("G-max-min", "gate.py", 'return max(((r.get("starts")', 'return min(((r.get("starts")'),
 ("G-me-no-starts", "gate.py", 'jobs = run_jobs(get, repo, ctx["run_id"], starts)', 'jobs = run_jobs(get, repo, ctx["run_id"])'),
 ("G-others-no-starts", "gate.py", 'else run_jobs(get, repo, r["id"], st)})', 'else run_jobs(get, repo, r["id"])})'),
 ("G-api-starts-dropped", "gate.py", '"jobs": api["jobs"], "starts": api.get("starts") or {}}', '"jobs": api["jobs"]}'),
 ("G-lag-any-all", "gate.py", 'if r is me and any((r["jobs"]', 'if r is me and all((r["jobs"]'),
 ("P-starts-not-filled", "prelude.py", '        starts.update((j["name"], j.get("started_at")) for j in rows)\n', '        pass\n'),
 ("S-later-ge-le", "sweep.py", 'r.get("created_at", "") >= (gate.get("completed_at") or "~")', 'r.get("created_at", "") <= (gate.get("completed_at") or "~")'),
 ("S-review-event-dropped", "sweep.py", 'PINNED_EVENTS = ("pull_request", "pull_request_review")', 'PINNED_EVENTS = ("pull_request",)'),
 ("S-py-suffix-dropped", "sweep.py", 'f["filename"].startswith(PINNED_PROGRAMS) and f["filename"].endswith(".py")', 'f["filename"].startswith(PINNED_PROGRAMS)'),
 ("S-polled-runs-dropped", "sweep.py", '"polled, completed red", list(listing.values()))', '"polled, completed red")'),
 ("S-run-runs-dropped", "sweep.py", 'self.judge(r, g, "completed red", runs)', 'self.judge(r, g, "completed red")'),
 ("S-settle-runs-dropped", "sweep.py", 'f"judged before run(s) {late} finished", runs)', 'f"judged before run(s) {late} finished")'),
 ("S-pin-cache-off", "sweep.py", '        if self.pin == ():\n', '        if True:\n'),
]
for name, f, a, b in MUTS:
    d = src.parent.parent; ci = src
    p = ci / f; t = p.read_text(); n = t.count(a)
    if n != 1: print(f"{name}: ANCHOR count {n}"); continue
    p.write_text(t.replace(a, b)); orig = t
    res = []
    for s in ("gate", "sweep", "prelude"):
        r = subprocess.run([sys.executable, "-I", "-B", str(ci / f"{s}.py"), "--self-test"], capture_output=True, text=True, cwd=d)
        last = (r.stdout.strip().splitlines() or ["<none>"])[-1]
        res.append(f"{s}:rc={r.returncode} '{last}'")
    p.write_text(orig); print(f"{name}: " + " | ".join(res))
