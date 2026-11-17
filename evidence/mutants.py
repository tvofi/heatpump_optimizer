# Reviewer's targeted mutants: apply in place in the head worktree, run the file's self-test, restore with git checkout.
import subprocess, sys
WT = sys.argv[1]
M = [
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        event(ctx, f"ROSTER-REFUSED #{n} {text}")', '        pass'),
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        if key in done or key in refused:', '        if key in done:'),
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        if lease is None:\n            break', '        if False:\n            break'),
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        if mark == f"#refused {op}":', '        if False:'),
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        refused.add(key)\n', '        done.add(key)\n'),
 ("beat_jobs", "tools/audit/seat/beat_jobs.py", '        ctx.remember("roster-refused.json", sorted(refused), [])\n', ''),
 ("roster_lib", "tools/audit/seat/roster_lib.py", 'fcntl.LOCK_EX | fcntl.LOCK_NB', 'fcntl.LOCK_SH | fcntl.LOCK_NB'),
 ("roster_lib", "tools/audit/seat/roster_lib.py", '            if clock() >= end:', '            if True:'),
 ("carry_fold", "tools/audit/seat/carry_fold.py", '    fd = lease(state_dir, wait_s)\n', '    fd = os.open(os.devnull, os.O_RDONLY)\n'),
 ("carry_fold", "tools/audit/seat/carry_fold.py", 'rc, lines = leased(a.state_dir, LEASE_WAIT_S, lambda: fold(body, load, apply, a.pr, a.topic))', 'rc, lines = fold(body, load, apply, a.pr, a.topic)'),
 ("record_beat", "tools/audit/seat/record_beat.py", ', "body": d.get("body") or ""}', '}'),
 ("record_beat", "tools/audit/seat/record_beat.py", 'closingIssuesReferences,body"', 'closingIssuesReferences"'),
 ("postmerge", "tools/audit/seat/postmerge.py", '    marks, unkeyed = derive_marks(f.get("body", ""), roster_now, group, sha) if group != rb.NO_GROUP else ([], [])', '    marks, unkeyed = [], []'),
 ("postmerge", "tools/audit/seat/postmerge.py", '        if kind == "dismissed" and (not why or "]" in why):', '        if False:'),
 ("postmerge", "tools/audit/seat/postmerge.py", '        if roster_lib.carry_mark(hits[0]):', '        if False:'),
 ("postmerge", "tools/audit/seat/postmerge.py", '            if code != 0:\n                out(f"stage refused rc {code}: {last}")', '            if False:\n                out(f"stage refused rc {code}: {last}")'),
]
for i, (t, path, old, new) in enumerate(M):
    p = f"{WT}/{path}"; s = open(p).read()
    if s.count(old) != 1:
        print(f"M{i} {t}: SITE-NOT-UNIQUE ({s.count(old)})"); continue
    open(p, "w").write(s.replace(old, new))
    args = ["python3", "-I", path, "--self-test"] + (["--no-mutants"] if t in ("postmerge", "beat_jobs") else [])
    r = subprocess.run(args, cwd=WT, capture_output=True, text=True, timeout=600)
    subprocess.run(["git", "checkout", "-q", "--", path], cwd=WT)
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or ["no output"]
    fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l][:2]
    print(f"M{i} {t}: {old.strip()[:70]!r} -> {new.strip()[:40]!r}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {tail[0]} | {fails}")
