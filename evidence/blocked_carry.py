"""Reviewer's own reproducer (not the finder's harness): a BLOCKED verdict's head
plus one clean main merge. review_owed with git_recarry: does it print CARRY
(silencing REVIEW OWED) although only a merge verdict carries (fix-review.md 12,
orchestrator.md 11)? Run from a checkout: python3 blocked_carry.py <checkout>."""
import importlib.util, os, subprocess, sys, tempfile
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("lg", os.path.join(root, "tools/audit/seat/ledger.py"))
lg = importlib.util.module_from_spec(spec); spec.loader.exec_module(lg)
d = tempfile.mkdtemp()
env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
def g(*a):
    return subprocess.run(["git", "-C", d, *a], env=env, capture_output=True, text=True, check=True).stdout.strip()
def put(f, t):
    open(os.path.join(d, f), "w").write(t); g("add", f); g("commit", "-qm", f); return g("rev-parse", "HEAD")
g("init", "-q", "-b", "main"); put("a.txt", "base")
g("checkout", "-q", "-b", "fix"); vh = put("fix.txt", "the fix")
g("checkout", "-q", "main"); put("m.txt", "main moves")
g("checkout", "-q", "fix"); g("merge", "-q", "--no-edit", "main"); head = g("rev-parse", "HEAD")
rc = lg.git_recarry(d, "main", env)
pr = [{"number": 9, "headRefOid": head}]
for verdict in (f"Fix review: merge {vh}", f"Fix review: blocked {vh} mutation-vacuous: x",
                f"Fix review: blocked {vh} root-cause-unanswered: gate"):
    out = lg.review_owed(pr, {"9": [verdict]}, set(), None, None, rc)
    print(f"RESULT prior verdict={verdict.split()[2]:8s} {' '.join(verdict.split()[4:])[:30]:30s} -> {out}")
