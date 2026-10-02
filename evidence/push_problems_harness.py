"""Reviewer's harness: drain_push_problems / drain_changed against real git repos (scratch)."""
import os, subprocess, sys, tempfile, shutil
sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/1848-review/wt/tests")
import mutation_table as m
ROW = m.DRAIN_ROWS + "a.py/g.GUARD_OFF.cccc.json"
def g(d, *a): return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True).stdout.strip()
def w(d, p, t):
    os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True); open(os.path.join(d, p), "w").write(t)
def repo():
    d = tempfile.mkdtemp(dir="/Users/timmalmstrom/hpo-seats/1848-review/scratch")
    g(d, "init", "-q"); g(d, "config", "user.email", "r@x"); g(d, "config", "user.name", "r")
    w(d, "src.py", "x=1\n"); w(d, m.DRAIN_ROWS + "old.json", "{}\n"); g(d, "add", "-A"); g(d, "commit", "-qm", "base")
    g(d, "update-ref", "refs/remotes/origin/main", "HEAD"); return d
def commit(d, msg): g(d, "add", "-A"); g(d, "commit", "-qm", msg)
cases = {}
d = repo(); w(d, ROW, "{}\n"); commit(d, m.DRAIN_SUBJECT); cases["S1 one row commit (null)"] = m.drain_push_problems(d)
d = repo(); w(d, "src.py", "x=2\n"); commit(d, "feat: branch work"); w(d, ROW, "{}\n"); commit(d, m.DRAIN_SUBJECT); cases["S2 branch commit under row commit"] = m.drain_push_problems(d)
d = repo(); w(d, m.DRAIN_ROWS + "old.json", '{"x":1}\n'); commit(d, m.DRAIN_SUBJECT); cases["S3 modifies a row"] = m.drain_push_problems(d)
d = repo(); w(d, ROW, "{}\n"); commit(d, "ci: pin killed mutants"); cases["S4 wrong subject"] = m.drain_push_problems(d)
d = repo(); w(d, ROW, "{}\n"); w(d, "src.py", "x=3\n"); commit(d, m.DRAIN_SUBJECT); cases["S5 row + src in one commit"] = m.drain_push_problems(d)
d = repo(); w(d, ROW, "{}\n"); commit(d, m.DRAIN_SUBJECT); g(d, "update-ref", "-d", "refs/remotes/origin/main"); cases["S6 no origin/main"] = m.drain_push_problems(d)
d = repo(); cases["S7 nothing committed"] = m.drain_push_problems(d)
d = repo(); g(d, "rm", "-q", m.DRAIN_ROWS + "old.json"); commit(d, m.DRAIN_SUBJECT); cases["S8 deletes a row"] = m.drain_push_problems(d)
for k, v in cases.items(): print("RESULT", k, "->", v)
d = repo(); base = g(d, "rev-parse", "HEAD"); w(d, "src.py", "x=9\n"); commit(d, "x"); head = g(d, "rev-parse", "HEAD")
print("RESULT drain_changed real", m.drain_changed(base, head, d))
print("RESULT drain_changed unknown sha", m.drain_changed("f"*40, head, d))
print("RESULT drain_changed empty at", m.drain_changed("", head, d))
print("RESULT drain_changed same", m.drain_changed(head, head, d))
shutil.rmtree("/Users/timmalmstrom/hpo-seats/1848-review/scratch", ignore_errors=True)
