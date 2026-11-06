# Probe: a blocked verdict's head is in the dispatch record (every review is dispatched first).
import subprocess, sys, tempfile, importlib.util, os
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("ledger", os.path.join(root, "tools/audit/seat/ledger.py"))
lg = importlib.util.module_from_spec(spec); spec.loader.exec_module(lg)
d = tempfile.mkdtemp()
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null")
g = lambda *a: subprocess.run(["git", "-C", d, *a], env=env, capture_output=True, text=True, check=True).stdout.strip()
def put(n, m):
    open(os.path.join(d, n), "w").write(m + "\n"); g("add", "-A"); g("commit", "-qm", m); return g("rev-parse", "HEAD")
g("init", "-q", "-b", "main"); put("base.txt", "base")
g("checkout", "-qb", "fix"); X = put("fix.txt", "fix")
g("checkout", "-q", "main"); put("main.txt", "main fixes the red")
g("checkout", "-q", "fix"); g("merge", "-q", "--no-edit", "main"); Y = g("rev-parse", "HEAD")
rc = lg.git_recarry(d, "main", env)
pr = [{"number": 9, "headRefOid": Y}]
blocked = {"9": [f"Fix review: blocked {X} root-cause-unanswered: tests"]}
print("blocked verdict, head X not in dispatch record :", lg.review_owed(pr, blocked, set(), None, None, rc))
print("blocked verdict, head X in dispatch record     :", lg.review_owed(pr, blocked, {("9", X)}, None, None, rc))
